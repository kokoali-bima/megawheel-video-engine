#!/bin/bash
# LAB 3D CHALLENGE sample.  bash lab/godot3d_challenge/run.sh <seed> [series] [tag]
cd /root/video-engine
SEED=${1:-1}; SERIES=${2:-potholes}; TAG=${3:-v1}
D=/root/lab/ch3d/s${SEED}_${SERIES}
GD=/root/tools/godot/Godot_v4.4.1-stable_linux.arm64
P=lab/godot3d_challenge/project
export GODOT_SILENCE_ROOT_WARNING=1
[ -f $D/frames.json ] || venv/bin/python lab/godot3d_challenge/export_challenge.py --seed $SEED --series $SERIES --out $D > $D.export.log 2>&1 || { tail -5 $D.export.log; exit 1; }
N=$(python3 -c "import json;print(len(json.load(open('$D/frames.json'))['frames']))")
timeout 120 $GD --headless --path $P --quit-after 5 -- $D 2>&1 | grep -E "SCRIPT ERROR|Parse Error|at: " | head -8
S=$(date +%s)
xvfb-run -a -s "-screen 0 1080x1920x24" $GD --path $P --rendering-driver opengl3 --write-movie $D/g.avi --fixed-fps 30 --quit-after $N -- $D > $D/godot.log 2>&1
echo "render $N frames: $(( $(date +%s) - S )) s"
grep -E "SCRIPT ERROR|ERROR:" $D/godot.log | grep -v MSAA | sort | uniq -c | head -6
ffmpeg -loglevel error -y -i $D/g.avi -c:v libx264 -pix_fmt yuv420p -crf 18 $D/g.mp4 && rm -f $D/g.avi
venv/bin/python lab/godot3d_challenge/compose.py --dir $D --video $D/g.mp4 --out $D/CHALLENGE3D_${TAG}.mp4
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $D/CHALLENGE3D_${TAG}.mp4)
ffmpeg -loglevel error -y -i $D/CHALLENGE3D_${TAG}.mp4 -vf "fps=12/$(python3 -c "print(round($DUR,1))"),scale=270:-1,tile=6x2" -frames:v 1 $D/sheet_${TAG}.jpg
echo "CH3D_DONE $D/CHALLENGE3D_${TAG}.mp4 dur=$DUR"
