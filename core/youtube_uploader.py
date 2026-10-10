#!/usr/bin/env python3
"""
YouTube Shorts Uploader Module for iPandu Video Automation Engine
- Official Google API Client (YouTube Data API v3)
- Token management & auto-refresh
- Resumable Chunk Uploading for reliability
- Strict approval requirement before triggering upload
"""

import os
import json
import logging
from typing import List, Optional, Dict, Any

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger("youtube-uploader")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

CREDENTIALS_DIR = os.path.expanduser("/root/video-engine/credentials")
DEFAULT_CLIENT_SECRETS = os.path.join(CREDENTIALS_DIR, "client_secrets.json")
DEFAULT_TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "youtube_token.json")

QUOTA_REASONS = {"quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded", "uploadLimitExceeded"}


class AuthExpired(PermissionError):
    """The refresh token is dead (revoked / expired, e.g. OAuth app in 'Testing' = 7 days). Needs a new authorisation."""


class QuotaExceeded(RuntimeError):
    """YouTube API daily quota (or upload limit) is used up. Not a bug: wait for the reset, then run again."""


def http_reason(ex) -> str:
    """First error reason of a googleapiclient HttpError ('' when unknown)."""
    try:
        return json.loads(ex.content.decode("utf-8"))["error"]["errors"][0]["reason"]
    except Exception:
        return ""


class YouTubeUploader:
    """Manages YouTube Data API v3 client, authentication, and video publishing."""

    def __init__(
        self,
        client_secrets_file: str = DEFAULT_CLIENT_SECRETS,
        token_file: str = DEFAULT_TOKEN_FILE
    ):
        self.client_secrets_file = client_secrets_file
        self.token_file = token_file
        os.makedirs(os.path.dirname(self.token_file), exist_ok=True)

    def is_authenticated(self) -> bool:
        """Check if a valid or refreshable token is present."""
        if not os.path.exists(self.token_file):
            return False
        try:
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            return bool(creds and (creds.valid or creds.refresh_token))
        except Exception as e:
            logger.warning(f"Error checking credentials: {e}")
            return False

    def get_service(self, force_refresh: bool = False):
        """Build and return an authenticated YouTube service object.
        Raises AuthExpired when the refresh token is dead (is_authenticated() cannot see that)."""
        creds = None
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            except Exception as e:
                logger.error(f"Failed to load token file: {e}")

        if creds and creds.refresh_token and (creds.expired or force_refresh):
            logger.info("Refreshing YouTube access token...")
            try:
                creds.refresh(Request())
            except RefreshError as ex:
                raise AuthExpired(f"refresh token YouTube ditolak Google: {ex}") from ex
            with open(self.token_file, "w", encoding="utf-8") as f:
                f.write(creds.to_json())

        if not creds or not creds.valid:
            if not os.path.exists(self.client_secrets_file):
                raise FileNotFoundError(
                    f"client_secrets.json not found at {self.client_secrets_file}. "
                    "Please download OAuth Client ID JSON from Google Cloud Console."
                )
            raise PermissionError(
                "YouTube authorization required. Run interactive auth setup or auth_flow()."
            )

        return build("youtube", "v3", credentials=creds)

    def check_auth(self) -> str:
        """LIVE check: force a token refresh and ask YouTube who we are (1 quota unit). Returns the channel title.
        Raises AuthExpired when the refresh token is dead. Call this BEFORE touching the upload queue."""
        yt = self.get_service(force_refresh=True)
        return yt.channels().list(part="snippet", mine=True).execute()["items"][0]["snippet"]["title"]

    def generate_auth_url(self) -> Tuple_Auth:
        """Generate an OAuth authorization URL for manual browser approval."""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, SCOPES, redirect_uri="urn:ietf:wg:oauth:2.0:oob"
        )
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
        return flow, auth_url

    def complete_auth(self, flow: InstalledAppFlow, auth_code: str) -> bool:
        """Exchange auth code for credentials and save to token file."""
        flow.fetch_token(code=auth_code.strip())
        creds = flow.credentials
        with open(self.token_file, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        logger.info(f"YouTube credentials saved to {self.token_file}")
        return True

    def upload_shorts(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        category_id: str = "1",  # 1: Film & Animation (MegaWheel Arena default)
        privacy_status: str = "unlisted",  # 'unlisted', 'private', 'public'
        made_for_kids: bool = False,  # general-audience channel (BLUEPRINT rule 7)
        publish_at: Optional[str] = None,  # ISO-8601 UTC ("2026-10-01T15:00:00Z"): YouTube publishes it then
        shorts: bool = True,  # False for long-form episodes (story15): no #Shorts added
        thumbnail_path: Optional[str] = None  # custom thumbnail (jpg/png < 2 MB); never fails the upload
    ) -> Dict[str, Any]:
        """
        Upload a Shorts video to YouTube with resumable chunking.
        NOTE: This must ONLY be invoked after human approval.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Ensure #Shorts is present in title or description
        if shorts and "#Shorts" not in title and "#shorts" not in title:
            title = f"{title} #Shorts"
        if shorts and "#Shorts" not in description:
            description = f"{description}\n\n#Shorts #YouTubeShorts"

        tags = tags or ["Shorts", "Car Crash", "Physics Simulation", "MegaWheel Arena"]

        youtube = self.get_service()

        body = {
            "snippet": {
                "title": title[:100],  # YouTube title cap is 100 chars
                "description": description[:5000],
                "tags": tags,
                "categoryId": category_id,
                "defaultLanguage": "en-US",
                "defaultAudioLanguage": "en-US"
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": made_for_kids,
                "embeddable": True,
                "license": "youtube"
            }
        }
        if publish_at:                        # scheduled release: must be uploaded as private
            body["status"]["privacyStatus"] = "private"
            body["status"]["publishAt"] = publish_at
            privacy_status = "scheduled"

        # 2MB chunks for robust uploading
        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            chunksize=2 * 1024 * 1024,
            resumable=True
        )

        logger.info(f"Initiating YouTube Shorts upload for {video_path} ('{title}')...")
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        try:
            while response is None:
                # num_retries: exponential backoff on 5xx / 429 / connection resets (one network blip must not kill a batch)
                status, response = request.next_chunk(num_retries=5)
                if status:
                    logger.info(f"Uploaded {int(status.progress() * 100)}%")
        except HttpError as ex:
            if http_reason(ex) in QUOTA_REASONS:
                raise QuotaExceeded(f"{http_reason(ex)}: {ex}") from ex
            raise

        video_id = response.get("id")
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                ext = os.path.splitext(thumbnail_path)[1].lower()
                youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(
                    thumbnail_path, mimetype="image/png" if ext == ".png" else "image/jpeg")).execute()
                logger.info("Custom thumbnail set")
            except Exception as ex:           # needs a verified channel: report, never fail the upload
                logger.warning(f"Thumbnail NOT set ({ex}); set it by hand in YouTube Studio")
        video_url = f"https://www.youtube.com/shorts/{video_id}"
        logger.info(f"Upload successful! Video ID: {video_id} -> {video_url}")

        return {
            "status": "success",
            "video_id": video_id,
            "url": video_url,
            "title": title,
            "privacy": privacy_status,
            "response": response
        }


if __name__ == "__main__":
    uploader = YouTubeUploader()
    print("YouTube Uploader initialized.")
    print(f"Auth Status: {'AUTHENTICATED' if uploader.is_authenticated() else 'NOT AUTHENTICATED'}")
    print(f"Credentials Path: {uploader.client_secrets_file}")
    print(f"Token Path: {uploader.token_file}")
