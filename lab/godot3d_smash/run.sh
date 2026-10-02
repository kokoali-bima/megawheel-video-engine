#!/bin/bash
# LAB plan B: render SMASH 3D sample.  bash lab/godot3d_smash/run.sh [frames]
cd /root/video-engine
N=${1:-1140}
GD=/root/tools/godot/Godot_v4.4.1-stable_linux.arm64
P=lab/godot3d_smash/project
D=/root/lab/smash3d; mkdir -p $D
export GODOT_SILENCE_ROOT_WARNING=1
timeout 90 $GD --headless --path $P --quit-after 10 -- /root/lab/fx/sprites 2>&1 | grep -E "SCRIPT ERROR|Parse|ERROR" | grep -v MSAA | head -8
rm -f /tmp/godot_events.json
S=$(date +%s)
xvfb-run -a -s "-screen 0 1080x1920x24" $GD --path $P --rendering-driver opengl3 --write-movie $D/s3d.avi --fixed-fps 30 --quit-after $N -- /root/lab/fx/sprites > $D/godot.log 2>&1
echo "render $N frames: $(( $(date +%s) - S )) s"
grep -E "SCRIPT ERROR|ERROR:" $D/godot.log | grep -v MSAA | sort | uniq -c | head -6
ffmpeg -loglevel error -y -i $D/s3d.avi -c:v libx264 -pix_fmt yuv420p -crf 19 $D/SMASH3D_v.mp4 && rm -f $D/s3d.avi
cp /tmp/godot_events.json $D/events.json 2>/dev/null || echo '{"events":[]}' > $D/events.json
venv/bin/python lab/godot_prototype/godot_mix.py --video $D/SMASH3D_v.mp4 --events $D/events.json --out $D/SMASH3D_B_v1.mp4
python3 -c "import json;e=json.load(open('$D/events.json'))['events'];import collections;print(collections.Counter(x['type'] for x in e))"
rm -rf $D/sheet && mkdir $D/sheet; i=0; for t in 1 4 7 8.5 12 13 17.5 19 23 26 30 36; do i=$((i+1)); ffmpeg -loglevel error -y -ss $t -i $D/SMASH3D_B_v1.mp4 -frames:v 1 -vf scale=270:-1 $D/sheet/f$(printf %02d $i).jpg 2>/dev/null; done
ffmpeg -loglevel error -y -i $D/sheet/f%02d.jpg -vf "tile=6x2:padding=3" -frames:v 1 $D/sheet.jpg
echo S3D_DONE
