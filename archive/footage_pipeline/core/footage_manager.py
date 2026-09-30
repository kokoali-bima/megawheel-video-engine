#!/usr/bin/env python3
"""
Footage Manager & 7-Day Retention Cleanup for MegaWheel Kids
- Tracks download history and source URLs in JSON & Markdown
- Auto-prunes raw footage older than 7 days if unused
- Provides quick re-download capabilities
"""

import os
import json
import time
from typing import Dict, Any, List, Optional

REGISTRY_JSON = "/root/video-engine/FOOTAGE_SOURCE_REGISTRY.json"
REGISTRY_MD = "/root/video-engine/FOOTAGE_SOURCE_REGISTRY.md"

class FootageManager:
    @classmethod
    def load_registry(cls) -> Dict[str, Any]:
        if os.path.exists(REGISTRY_JSON):
            try:
                with open(REGISTRY_JSON, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_updated": "", "retention_days": 7, "sources": []}

    @classmethod
    def save_registry(cls, data: Dict[str, Any]):
        data["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        os.makedirs(os.path.dirname(REGISTRY_JSON), exist_ok=True)
        with open(REGISTRY_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        cls.export_markdown(data)

    @classmethod
    def register_source(
        cls,
        source_id: str,
        title: str,
        source_url: str,
        theme: str,
        local_path: str,
        origin_platform: str = "YouTube / Web",
        used_in: Optional[List[str]] = None
    ):
        db = cls.load_registry()
        size_mb = 0.0
        if os.path.exists(local_path):
            size_mb = round(os.path.getsize(local_path) / (1024 * 1024), 2)

        entry = {
            "source_id": source_id,
            "title": title,
            "source_url": source_url,
            "origin_platform": origin_platform,
            "theme": theme,
            "local_path": local_path,
            "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "timestamp": time.time(),
            "file_size_mb": size_mb,
            "used_in_videos": used_in or [],
            "status": "ACTIVE"
        }

        # Check if exists
        existing = [s for s in db.get("sources", []) if s.get("source_id") == source_id]
        if existing:
            db["sources"] = [s if s.get("source_id") != source_id else entry for s in db["sources"]]
        else:
            db["sources"].append(entry)

        cls.save_registry(db)

    @classmethod
    def cleanup_expired_footage(cls) -> List[str]:
        """Prune unused files older than 7 days (7 * 86400s)."""
        db = cls.load_registry()
        now = time.time()
        retention_sec = db.get("retention_days", 7) * 86400
        pruned = []

        for s in db.get("sources", []):
            ts = s.get("timestamp", 0)
            is_old = (now - ts) > retention_sec
            is_unused = len(s.get("used_in_videos", [])) == 0
            path = s.get("local_path", "")

            if is_old and is_unused and os.path.exists(path):
                try:
                    os.remove(path)
                    s["status"] = "PRUNED_AVAILABLE_FOR_REDOWNLOAD"
                    pruned.append(path)
                except Exception as e:
                    print(f"Error removing {path}: {e}")

        if pruned:
            cls.save_registry(db)
        return pruned

    @classmethod
    def export_markdown(cls, data: Dict[str, Any]):
        sources = data.get("sources", [])
        rows = []
        for idx, s in enumerate(sources, 1):
            used = ", ".join(s.get("used_in_videos", [])) if s.get("used_in_videos") else "None"
            rows.append(
                f"| {idx} | `{s.get('source_id')}` | {s.get('title')[:30]} | {s.get('theme')} | [{s.get('origin_platform')}]({s.get('source_url')}) | {s.get('downloaded_at')[:10]} | `{s.get('status')}` | {used} |"
            )

        table = "\n".join(rows) if rows else "| - | - | Belum ada sumber | - | - | - | - | - |"
        md = f"""# 🗂️ MEGAWHEEL KIDS - FOOTAGE SOURCE & RETENTION REGISTRY

Dokumen ini mencatat seluruh riwayat bahan footage, URL sumber, dan status retensi 7 hari.

* **Terakhir Diperbarui**: {data.get('last_updated', 'N/A')}
* **Kebijakan Retensi**: Otomatis dibersihkan jika tidak terpakai dalam 7 hari
* **Total Sumber Terdata**: {len(sources)}

---

## 📹 Daftar Sumber Footage & Status

| No | Source ID | Judul Bahan Asal | Tema Rintangan | URL Sumber (Download Ulang) | Tanggal Unduh | Status | Digunakan Pada |
| :- | :--- | :--- | :--- | :--- | :--- | :- | :--- |
{table}

---
"""
        with open(REGISTRY_MD, "w", encoding="utf-8") as f:
            f.write(md)

if __name__ == "__main__":
    FootageManager.cleanup_expired_footage()
    print("FootageManager check completed.")
