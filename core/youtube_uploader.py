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
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger("youtube-uploader")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

CREDENTIALS_DIR = os.path.expanduser("/root/video-engine/credentials")
DEFAULT_CLIENT_SECRETS = os.path.join(CREDENTIALS_DIR, "client_secrets.json")
DEFAULT_TOKEN_FILE = os.path.join(CREDENTIALS_DIR, "youtube_token.json")


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

    def get_service(self):
        """Build and return an authenticated YouTube service object."""
        creds = None
        if os.path.exists(self.token_file):
            try:
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            except Exception as e:
                logger.error(f"Failed to load token file: {e}")

        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired YouTube access token...")
            creds.refresh(Request())
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
        made_for_kids: bool = False  # general-audience channel (BLUEPRINT rule 7)
    ) -> Dict[str, Any]:
        """
        Upload a Shorts video to YouTube with resumable chunking.
        NOTE: This must ONLY be invoked after human approval.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Ensure #Shorts is present in title or description
        if "#Shorts" not in title and "#shorts" not in title:
            title = f"{title} #Shorts"
        if "#Shorts" not in description:
            description = f"{description}\n\n#Shorts #YouTubeShorts"

        tags = tags or ["Shorts", "Car Crash", "Physics Simulation", "MegaWheel Arena"]

        youtube = self.get_service()

        body = {
            "snippet": {
                "title": title[:100],  # YouTube title cap is 100 chars
                "description": description[:5000],
                "tags": tags,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": made_for_kids,
                "embeddable": True,
                "license": "youtube"
            }
        }

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
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Uploaded {int(status.progress() * 100)}%")

        video_id = response.get("id")
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
