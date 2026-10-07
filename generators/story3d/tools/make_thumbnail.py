"""YouTube thumbnail (1280x720 JPEG, < 2 MB) for a story3d episode, from stories/<ep>/publish.json["thumbnail"]:
a real frame of the episode (scene + time) with big channel-style lettering (Luckiest Guy) and an episode badge.
  venv/bin/python generators/story3d/tools/make_thumbnail.py --episode S01E02_who_is_kraggor --out /tmp/thumb.jpg
Runs on the VM (ffmpeg + the Luckiest Guy font + the final scene mp4 in work/story3d/<ep>/)."""
import argparse
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FONT = "/root/.fonts/LuckiestGuy-Regular.ttf"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pub = json.load(open(os.path.join(ROOT, "stories", a.episode, "publish.json"), encoding="utf-8"))
    th = pub["thumbnail"]
    src = os.path.join(ROOT, "work", "story3d", a.episode, f"{a.episode}_scene_{th['scene']:02d}.mp4")
    big = os.path.join(os.path.dirname(a.out) or ".", "thumb_big.txt")
    open(big, "w", encoding="utf-8").write(th["big"])
    top = os.path.join(os.path.dirname(a.out) or ".", "thumb_top.txt")
    open(top, "w", encoding="utf-8").write(th["top"])
    badge = os.path.join(os.path.dirname(a.out) or ".", "thumb_badge.txt")
    open(badge, "w", encoding="utf-8").write(th["badge"])
    vf = ("crop=1920:896:0:92,scale=-2:720,crop=1280:720:(iw-1280)/2:0,eq=saturation=1.25:contrast=1.08,"      # no letterbox bars
          "drawbox=x=0:y=ih*0.52:w=iw:h=ih*0.48:color=black@0.38:t=fill,"          # a dark band so the lettering reads
          f"drawtext=fontfile={FONT}:textfile={top}:fontcolor=0xFFD21F:fontsize=92:borderw=8:bordercolor=black:x=48:y=h*0.55,"
          f"drawtext=fontfile={FONT}:textfile={big}:fontcolor=white:fontsize=170:borderw=10:bordercolor=black:x=40:y=h*0.64,"
          f"drawbox=x=iw-250:y=28:w=222:h=92:color=0xFF6A00@0.95:t=fill,"
          f"drawtext=fontfile={FONT}:textfile={badge}:fontcolor=white:fontsize=64:borderw=4:bordercolor=black:x=w-232:y=44")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(th["at"]), "-i", src, "-frames:v", "1", "-vf", vf,
                    "-q:v", "2", a.out], check=True)
    print(f"[thumbnail] {a.out} ({os.path.getsize(a.out) // 1024} KB)")


if __name__ == "__main__":
    main()
