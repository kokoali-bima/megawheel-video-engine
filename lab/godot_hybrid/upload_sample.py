"""LAB — put hybrid sample files in Drive ipandu-video/lab/hybrid/ (not review/: samples are not production).
  venv/bin/python lab/godot_hybrid/upload_sample.py <file> [...]"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "generators", "publishing"))
import drive_sync  # noqa: E402

parent = drive_sync.folder("lab", "hybrid")
for p in sys.argv[1:]:
    fid = drive_sync.upload(p, parent, os.path.basename(p))
    print(f"[drive] lab/hybrid/{os.path.basename(p)} ({fid})")
