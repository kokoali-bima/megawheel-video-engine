import subprocess
import json
import os
from typing import Dict, Any

class PreflightValidator:
    """Automated Quality Assurance checker before delivering videos."""

    @staticmethod
    def audit_video(video_path: str, max_duration_sec: float = 60.0) -> Dict[str, Any]:
        """
        Check dimensions, aspect ratio, duration, and audio stream health.
        """
        if not os.path.exists(video_path):
            return {"valid": False, "reason": "File not found"}
            
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "stream=codec_type,width,height,duration,codec_name",
            "-show_entries", "format=duration,size",
            "-of", "json",
            video_path
        ]
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return {"valid": False, "reason": f"ffprobe error: {res.stderr}"}
            
        data = json.loads(res.stdout)
        streams = data.get("streams", [])
        
        has_video = any(s.get("codec_type") == "video" for s in streams)
        has_audio = any(s.get("codec_type") == "audio" for s in streams)
        
        if not has_video:
            return {"valid": False, "reason": "No video stream found"}
        if not has_audio:
            return {"valid": False, "reason": "No audio stream found (silent video)"}
            
        # Check video stream properties
        video_stream = next(s for s in streams if s.get("codec_type") == "video")
        width = int(video_stream.get("width", 0))
        height = int(video_stream.get("height", 0))
        
        format_info = data.get("format", {})
        duration = float(format_info.get("duration", 0))
        
        # Check aspect ratio 9:16
        if height == 0 or (width / height) > 0.60:
            return {
                "valid": False,
                "reason": f"Non-vertical aspect ratio: {width}x{height} (expected 9:16 vertical)"
            }
            
        if duration > max_duration_sec:
            return {
                "valid": False,
                "reason": f"Duration {duration:.1f}s exceeds limit {max_duration_sec}s"
            }
            
        return {
            "valid": True,
            "width": width,
            "height": height,
            "duration_sec": duration,
            "size_bytes": int(format_info.get("size", 0)),
            "codec_video": video_stream.get("codec_name"),
            "status": "PASSED"
        }
