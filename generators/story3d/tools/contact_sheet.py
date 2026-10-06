"""Contact sheet of a story3d scene (self-review BEFORE delivery, owner 2026-10-06: "cek sendiri lembar kontak").
One thumbnail every STEP seconds with its time stamp, tiled; plus the shot start frames if the scene json is given.
  venv/bin/python generators/story3d/tools/contact_sheet.py work/story3d/<ep>/<ep>_scene_05.mp4 /tmp/s05.jpg [--step 3] [--cols 4]
Runs where ffmpeg runs (VM). Look at the sheet: tilted road / floating cars, things standing in front of faces, empty
frames, wrong colours, characters cut by the letterbox, a subtitle covering the speaker."""
import argparse
import subprocess

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mp4")
    ap.add_argument("out")
    ap.add_argument("--step", type=float, default=3.0)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--width", type=int, default=480)
    a = ap.parse_args()
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.mp4],
                       capture_output=True, text=True)
    dur = float(r.stdout.strip())
    n = int(dur / a.step) + 1
    rows = (n + a.cols - 1) // a.cols
    vf = (f"fps=1/{a.step},scale={a.width}:-1,drawtext=fontfile={FONT}:text='%{{pts\\:hms}}':x=6:y=6:fontsize=22:"
          f"fontcolor=white:box=1:boxcolor=black@0.6,tile={a.cols}x{rows}:padding=4:color=black")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.mp4, "-vf", vf, "-frames:v", "1", "-q:v", "3", a.out],
                   check=True)
    print(f"[contact] {n} frames every {a.step}s -> {a.out}")


if __name__ == "__main__":
    main()
