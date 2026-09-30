#!/usr/bin/env python3
"""
Video Publishing & History Tracker for iPandu Video Automation Engine
- Records all rendered and uploaded videos
- Prevents duplicate video generation & duplicate YouTube uploads
- Dual persistence: Structured JSON database + Human-readable Markdown summary table
"""

import os
import json
import time
from typing import List, Dict, Any, Optional

TRACKER_DIR = "/root/video-engine"
TRACKER_JSON = os.path.join(TRACKER_DIR, "VIDEO_PUBLISHING_TRACKER.json")
TRACKER_MD = os.path.join(TRACKER_DIR, "VIDEO_PUBLISHING_TRACKER.md")


class VideoPublishingTracker:
    """Manages publishing history, deduplication, and upload tracking."""

    @classmethod
    def load_database(cls) -> Dict[str, Any]:
        """Load the JSON tracking database or return empty structure."""
        if os.path.exists(TRACKER_JSON):
            try:
                with open(TRACKER_JSON, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"channel": "MegaWheel Kids", "last_updated": "", "videos": []}

    @classmethod
    def save_database(cls, data: Dict[str, Any]):
        """Save to JSON and generate updated Markdown tracker."""
        data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        os.makedirs(os.path.dirname(TRACKER_JSON), exist_ok=True)
        with open(TRACKER_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        cls.export_markdown(data)

    @classmethod
    def is_already_uploaded(cls, video_id: str, title: str) -> bool:
        """Check if video ID or identical title is already uploaded."""
        db = cls.load_database()
        for v in db.get("videos", []):
            if v.get("video_id") == video_id and v.get("youtube_video_id"):
                return True
            if v.get("title", "").strip().lower() == title.strip().lower() and v.get("youtube_video_id"):
                return True
        return False

    @classmethod
    def register_render(
        cls,
        video_id: str,
        title: str,
        theme: str,
        vehicles: List[str],
        file_path: str,
        duration_sec: float,
        language: str = "US",
        tags: Optional[List[str]] = None
    ):
        """Record a freshly rendered video pending approval."""
        db = cls.load_database()
        existing = next((v for v in db["videos"] if v.get("video_id") == video_id), None)

        record = {
            "video_id": video_id,
            "title": title,
            "theme": theme,
            "vehicles": vehicles,
            "language": language,
            "duration_sec": duration_sec,
            "file_path": file_path,
            "tags": tags or [],
            "status": "RENDERED_PENDING_APPROVAL",
            "render_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "youtube_video_id": None,
            "youtube_url": None,
            "youtube_privacy": None,
            "upload_date": None
        }

        if existing:
            # Preserve existing upload info if already present
            record["youtube_video_id"] = existing.get("youtube_video_id")
            record["youtube_url"] = existing.get("youtube_url")
            record["youtube_privacy"] = existing.get("youtube_privacy")
            record["upload_date"] = existing.get("upload_date")
            if existing.get("youtube_video_id"):
                record["status"] = existing.get("status", "UPLOADED")
            db["videos"][db["videos"].index(existing)] = record
        else:
            db["videos"].append(record)

        cls.save_database(db)

    @classmethod
    def register_upload(
        cls,
        video_id: str,
        youtube_video_id: str,
        youtube_url: str,
        privacy: str = "unlisted"
    ):
        """Record successful YouTube upload."""
        db = cls.load_database()
        for v in db.get("videos", []):
            if v.get("video_id") == video_id:
                v["status"] = f"UPLOADED_{privacy.upper()}"
                v["youtube_video_id"] = youtube_video_id
                v["youtube_url"] = youtube_url
                v["youtube_privacy"] = privacy
                v["upload_date"] = time.strftime("%Y-%m-%d %H:%M:%S")
                break
        cls.save_database(db)

    @classmethod
    def export_markdown(cls, db: Dict[str, Any]):
        """Generate a clean Markdown summary table."""
        md = f"""# 📊 MEGAWHEEL KIDS - VIDEO PRODUCTION & UPLOAD TRACKER

Dokumen ini melacak seluruh riwayat produksi dan upload video ke YouTube Shorts untuk memastikan **tidak ada duplikasi pembuatan konten maupun duplikasi upload**.

* **Channel Target**: {db.get('channel', 'MegaWheel Kids')}
* **Terakhir Diperbarui**: {db.get('last_updated', 'N/A')}
* **Total Video Terdata**: {len(db.get('videos', []))}

---

## 🏁 Daftar Riwayat Video & Status Publikasi

| No | Video ID | Judul Shorts | Niche / Tema | Kendaraan (Level 1 - 3) | Durasi | Status | YouTube Link | Tanggal Render |
| :- | :--- | :--- | :--- | :--- | :- | :--- | :--- | :--- |
"""
        for i, v in enumerate(db.get("videos", []), 1):
            vid_id = v.get("video_id", "-")
            title = v.get("title", "-")[:40] + "..." if len(v.get("title", "")) > 40 else v.get("title", "-")
            theme = v.get("theme", "-")
            vehicles = " ➔ ".join(v.get("vehicles", [])) if isinstance(v.get("vehicles"), list) else str(v.get("vehicles"))
            dur = f"{v.get('duration_sec', 0.0):.1f}s"
            status = v.get("status", "UNKNOWN")
            yt_link = f"[{v.get('youtube_video_id')}]({v.get('youtube_url')})" if v.get("youtube_url") else "Belum Upload"
            render_dt = v.get("render_date", "-")

            md += f"| {i} | `{vid_id}` | {title} | {theme} | {vehicles} | {dur} | `{status}` | {yt_link} | {render_dt} |\n"

        md += """
---

## 🔒 Kebijakan Anti-Duplikasi (Anti-Duplicate Policy):
1. **Cek Pra-Render**: Sebelum merender naskah/scene baru, periksa kombinasi *Kendaraan + Rintangan* di tabel ini untuk memastikan variasi baru.
2. **Cek Pra-Upload**: Sistem uploader otomatis menolak file/judul yang sudah memiliki `youtube_video_id` aktif di tracker.
3. **Penyimpanan Permanen**: File database tersimpan di [`VIDEO_PUBLISHING_TRACKER.json`](file:///root/video-engine/VIDEO_PUBLISHING_TRACKER.json) dan tidak terhapus saat server restart.
"""
        with open(TRACKER_MD, "w", encoding="utf-8") as f:
            f.write(md)


if __name__ == "__main__":
    tracker = VideoPublishingTracker()
    db = tracker.load_database()
    print(f"Tracker initialized. Total tracked videos: {len(db.get('videos', []))}")
