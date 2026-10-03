"""LAB 3D CHALLENGE: Godot render + the engine's HUD overlay + the engine's audio + the production cold open.
  venv/bin/python lab/godot3d_challenge/compose.py --dir /root/lab/ch3d/s1 --video godot.mp4 --out final.mp4"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "generators", "physics_2d"))
import sim_engine as se  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--dir", required=True)
ap.add_argument("--video", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.video, "-i", f"{a.dir}/overlay.mov", "-i", f"{a.dir}/mix.wav",
                "-filter_complex", "[1:v]setpts=PTS-STARTPTS[o];[0:v]setpts=PTS-STARTPTS[g];[g][o]overlay=eof_action=pass[v]",
                "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac",
                "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", "-movflags", "+faststart", a.out], check=True)
meta = json.load(open(f"{a.dir}/meta.json"))
se.detect_font()
se.add_cold_open(a.out, meta["cold_t"], meta["cold_text"])                  # same rule as every aired Short
print(f"[compose] {a.out} | title: {meta['title']}")
