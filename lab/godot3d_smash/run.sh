#!/bin/bash
# LAB plan B: render SMASH 3D sample.  bash lab/godot3d_smash/run.sh [frames] [tag] [extra godot user args...]
cd /root/video-engine
N=${1:-1050}
TAG=${2:-v2}
shift 2 2>/dev/null
GD=/root/tools/godot/Godot_v4.4.1-stable_linux.arm64
P=lab/godot3d_smash/project
SP=/root/lab/fx/sprites
D=/root/lab/smash3d; mkdir -p $D
export GODOT_SILENCE_ROOT_WARNING=1
venv/bin/python lab/godot3d_smash/make_props.py $SP
[ -f /root/lab/sfx/bank/bank.json ] || python3 lab/godot3d_smash/sfx_bank.py
timeout 90 $GD --headless --path $P --quit-after 10 -- $SP 2>&1 | grep -E "SCRIPT ERROR|Parse|ERROR" | grep -v MSAA | head -8
rm -f /tmp/godot_events.json
S=$(date +%s)
xvfb-run -a -s "-screen 0 1080x1920x24" $GD --path $P --rendering-driver opengl3 --write-movie $D/s3d.avi --fixed-fps 30 --quit-after $N -- $SP "$@" > $D/godot.log 2>&1
echo "render $N frames: $(( $(date +%s) - S )) s"
grep -E "SCRIPT ERROR|ERROR:" $D/godot.log | grep -v MSAA | sort | uniq -c | head -6
ffmpeg -loglevel error -y -i $D/s3d.avi -c:v libx264 -pix_fmt yuv420p -crf 19 $D/SMASH3D_${TAG}_video.mp4 && rm -f $D/s3d.avi
cp /tmp/godot_scale.json $D/scale_${TAG}.json 2>/dev/null; grep "^SCALE" $D/godot.log | head -1
cp /tmp/godot_events.json $D/events_${TAG}.json 2>/dev/null || echo '{"events":[]}' > $D/events_${TAG}.json
venv/bin/python lab/godot3d_smash/mix3d.py --video $D/SMASH3D_${TAG}_video.mp4 --events $D/events_${TAG}.json --out $D/SMASH3D_B_${TAG}.mp4
python3 -c "import json;e=json.load(open('$D/events_${TAG}.json'))['events'];import collections;print(collections.Counter(x['type'] for x in e));print([(round(x['t'],1),x['type']) for x in e if x['type'] in ('ko','win','fall','chomp')])"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $D/SMASH3D_B_${TAG}.mp4)
rm -rf $D/sheet && mkdir $D/sheet
for i in $(seq 1 12); do t=$(python3 -c "print(round($DUR*($i-0.5)/12,2))"); ffmpeg -loglevel error -y -ss $t -i $D/SMASH3D_B_${TAG}.mp4 -frames:v 1 -vf scale=270:-1 $D/sheet/f$(printf %02d $i).jpg; done
ffmpeg -loglevel error -y -i $D/sheet/f%02d.jpg -vf "tile=6x2:padding=3" -frames:v 1 $D/sheet_${TAG}.jpg
echo "S3D_DONE $D/SMASH3D_B_${TAG}.mp4 dur=$DUR"
