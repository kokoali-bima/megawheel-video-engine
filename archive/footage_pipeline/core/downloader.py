import subprocess
import os
import json
from typing import Optional, Dict, Any

class VideoDownloader:
    """Automated yt-dlp wrapper with sanity checks and optimal format selection."""
    
    @staticmethod
    def search_and_download(
        query_or_url: str,
        output_path: str,
        max_height: int = 720,
        max_duration_sec: int = 600
    ) -> Dict[str, Any]:
        """
        Download video from URL or search query with max quality cap to avoid AV1/oversized files.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        target = query_or_url
        if not (query_or_url.startswith("http://") or query_or_url.startswith("https://")):
            target = f"ytsearch1:{query_or_url}"
            
        fmt = f"bv*[height<={max_height}]+ba/b[height<={max_height}]"
        
        cmd = [
            "yt-dlp",
            "-f", fmt,
            "--merge-output-format", "mp4",
            "--no-playlist",
            "-o", output_path,
            target
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Download failed: {result.stderr}")
            
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Expected output file not found: {output_path}")
            
        return {
            "path": output_path,
            "status": "success"
        }
