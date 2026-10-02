#!/usr/bin/env python3
"""Upload an APPROVED episode to YouTube. Run ONLY on the user's explicit instruction.

Usage (cd /root/video-engine):
  ./venv/bin/python generators/publishing/publish.py <EP> [--privacy private|unlisted|public]   (default: private)

Refuses anything that is not APPROVED (episodes.py approve) or that already has a YouTube URL.
Title, description and tags come from the episode manifest. Category 1 (Film & Animation),
selfDeclaredMadeForKids = False (channel is a general-audience channel, BLUEPRINT rule 7).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))            # /root/video-engine (core/)
sys.path.insert(0, os.path.join(HERE, "..", "physics_2d"))
sys.path.insert(0, HERE)
import episodes  # noqa: E402
from core.youtube_uploader import YouTubeUploader  # noqa: E402

CATEGORY_FILM_ANIMATION = "1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode", type=int)
    ap.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    args = ap.parse_args()

    e = episodes.by_episode(args.episode)
    if not e:
        sys.exit(f"[publish] STOP: episode {args.episode} tidak ada (belum di-approve?)")
    if e.get("status") != "APPROVED":
        sys.exit(f"[publish] STOP: episode {args.episode} berstatus {e.get('status')}. Hanya APPROVED yang boleh diupload.")
    if e.get("youtube_url"):
        sys.exit(f"[publish] STOP: episode {args.episode} sudah diupload: {e['youtube_url']}")
    folder = f"{episodes.BASE}/{e['folder']}"
    with open(f"{folder}/{e['video_id']}.json") as fh:
        m = json.load(fh)
    video = f"{folder}/{e['video_id']}.mp4"
    if not os.path.exists(video):
        sys.exit(f"[publish] STOP: file video tidak ada: {video}")
    uploader = YouTubeUploader()
    if not uploader.is_authenticated():
        sys.exit("[publish] STOP: YouTube belum terotentikasi (jalankan auth_youtube.py).")

    print(f"[publish] Ep. {args.episode} | {m['title']} | privacy={args.privacy}")
    res = uploader.upload_shorts(video_path=video, title=m["title"], description=episodes.with_credit(m["description"]), tags=m["tags"],
                                 category_id=CATEGORY_FILM_ANIMATION, privacy_status=args.privacy,
                                 made_for_kids=False)
    episodes.mark_uploaded(args.episode, res["url"], args.privacy)
    episodes.write_log()
    print(f"[publish] OK -> {res['url']}")


if __name__ == "__main__":
    main()
