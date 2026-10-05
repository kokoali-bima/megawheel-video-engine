"""LAB pilot C: Godot world video + the story25d character overlay (alpha) + the scene audio -> final scene mp4
(same loudness rule as story25d: -16 LUFS).
  venv/bin/python lab/godot_story/compose_story.py --dir /root/lab/gs/s1 --video g.mp4 --out PILOT_C.mp4"""
import argparse
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("--dir", required=True)
ap.add_argument("--video", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.video, "-i", f"{a.dir}/overlay.mov", "-i", f"{a.dir}/audio.wav",
                "-filter_complex", "[1:v]setpts=PTS-STARTPTS[o];[0:v]setpts=PTS-STARTPTS[g];[g][o]overlay=eof_action=pass[v]",
                "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                a.out], check=True)
print(f"[story3d] -> {a.out}")
