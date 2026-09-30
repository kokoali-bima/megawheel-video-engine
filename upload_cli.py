#!/usr/bin/env python3
"""
Manual / Approved YouTube Video Upload CLI with Anti-Duplication Tracker
Usage:
  python3 upload_cli.py <video_id_or_path> --title "Title #Shorts" --privacy unlisted
"""

import os
import sys
import argparse
from core.youtube_uploader import YouTubeUploader
from core.tracker import VideoPublishingTracker

def main():
    parser = argparse.ArgumentParser(description="Upload a video to YouTube Shorts with manual approval.")
    parser.add_argument("video_input", help="Video ID (e.g. VIDEO_01_SPEED_BUMPS) or path to MP4 file")
    parser.add_argument("--title", help="Video title (must include #Shorts)")
    parser.add_argument("--description", help="Video description")
    parser.add_argument("--tags", default="Shorts,BeamNG,Gaming,Animation,Kids", help="Comma separated tags")
    parser.add_argument("--privacy", default="unlisted", choices=["unlisted", "private", "public"], help="Privacy status (default: unlisted)")
    parser.add_argument("--category", default="20", help="Category ID (20: Gaming, 24: Entertainment)")

    args = parser.parse_args()

    uploader = YouTubeUploader()
    if not uploader.is_authenticated():
        print("\n[ERROR] YouTube account belum terotentikasi!")
        print("Silakan jalankan: python3 auth_youtube.py terlebih dahulu.\n")
        sys.exit(1)

    # Determine video file & metadata from tracker or args
    db = VideoPublishingTracker.load_database()
    video_path = args.video_input
    video_id = os.path.splitext(os.path.basename(video_path))[0]
    matched_entry = next((v for v in db.get("videos", []) if v.get("video_id") == args.video_input or v.get("file_path") == args.video_input), None)

    if matched_entry:
        video_id = matched_entry["video_id"]
        video_path = matched_entry["file_path"]
        title = args.title or matched_entry["title"]
        description = args.description or matched_entry.get("description", "Fun car physics challenge! #Shorts #BeamNG #Kids")
        tag_list = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else matched_entry.get("tags", [])
    else:
        title = args.title or f"{video_id} #Shorts"
        description = args.description or "Fun car physics challenge! #Shorts #BeamNG #Kids"
        tag_list = [t.strip() for t in args.tags.split(",") if t.strip()]

    # Check Anti-Duplication
    if VideoPublishingTracker.is_already_uploaded(video_id, title):
        print(f"\n[WARNING] Video '{video_id}' / '{title}' SUDAH PERNAH DI-UPLOAD SEBELUMNYA!")
        print("Sistem anti-duplikasi mencegah upload ganda untuk video yang sama.")
        proceed = input("Apakah tetap ingin memaksa upload ulang? (y/N): ").strip().lower()
        if proceed != 'y':
            print("Upload dibatalkan.")
            sys.exit(0)

    print("\n" + "=" * 60)
    print("  KONFIRMASI UPLOAD YOUTUBE SHORTS (MANUAL APPROVAL)")
    print("=" * 60)
    print(f"Video ID   : {video_id}")
    print(f"File Path  : {video_path}")
    print(f"Judul      : {title}")
    print(f"Status     : {args.privacy.upper()}")
    print(f"Tags       : {', '.join(tag_list)}")
    print("=" * 60)

    res = uploader.upload_shorts(
        video_path=video_path,
        title=title,
        description=description,
        tags=tag_list,
        category_id=args.category,
        privacy_status=args.privacy
    )

    # Register in Tracker
    VideoPublishingTracker.register_upload(
        video_id=video_id,
        youtube_video_id=res["video_id"],
        youtube_url=res["url"],
        privacy=args.privacy
    )

    print("\n" + "=" * 60)
    print("  [BERHASIL] VIDEO BERHASIL DI-UPLOAD KE YOUTUBE!")
    print("=" * 60)
    print(f"Video ID   : {res['video_id']}")
    print(f"URL Link   : {res['url']}")
    print(f"Status     : {res['privacy']}")
    print(f"Tracker    : VIDEO_PUBLISHING_TRACKER.md diperbarui!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
