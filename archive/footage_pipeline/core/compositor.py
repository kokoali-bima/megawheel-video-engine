import subprocess
import os
from typing import List, Dict, Any, Optional

class VideoCompositor:
    """Robust FFmpeg-backed video assembler enforcing 9:16 safe-zone rules."""

    @staticmethod
    def render_shorts_segment(
        input_video: str,
        start_sec: float,
        duration_sec: float,
        output_file: str,
        target_w: int = 1080,
        target_h: int = 1920,
        hold_sec: float = 0.0
    ) -> str:
        """
        Extract clip with exact 9:16 vertical pad framing (preserving full 16:9 content without zoom distortion).
        hold_sec > 0 freezes the last frame to stretch a segment shorter than the narration that plays over it.
        Output is video-only (-an): the source's own audio (engine noise, ambient sound) is intentionally
        dropped here so merge_and_finalize can never accidentally pick it up instead of the narration track.
        """
        inner_h = int(target_w * 9 / 16)
        if inner_h % 2 != 0:
            inner_h += 1

        vf = f"scale={target_w}:{inner_h}:force_original_aspect_ratio=decrease,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1"
        if hold_sec > 0:
            vf += f",tpad=stop_mode=clone:stop_duration={hold_sec}"

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_sec),
            "-t", str(duration_sec),
            "-i", input_video,
            "-vf", vf,
            "-an",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-movflags", "+faststart",
            output_file
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Compositor error: {res.stderr}")

        return output_file

    @staticmethod
    def merge_and_finalize(
        video_segments: List[str],
        audio_track: str,
        subtitle_ass: Optional[str],
        output_file: str
    ) -> str:
        """
        Concatenate segments, burn subtitles, attach audio track, and output verified MP4.
        Explicit -map is required here: without it ffmpeg's default stream-selection can pick
        an unrelated audio stream over the intended narration/BGM mix (this bit us once already).
        """
        concat_txt = "/tmp/concat_segments.txt"
        with open(concat_txt, "w") as f:
            for seg in video_segments:
                f.write(f"file '{os.path.abspath(seg)}'\n")

        vf_filters = []
        if subtitle_ass and os.path.exists(subtitle_ass):
            escaped_ass = subtitle_ass.replace(":", r"\:").replace("'", r"\'")
            vf_filters.append(f"ass={escaped_ass}")

        vf_str = ",".join(vf_filters) if vf_filters else "null"

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_txt,
            "-i", audio_track,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-vf", vf_str,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            output_file
        ]

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Finalize error: {res.stderr}")

        return output_file
