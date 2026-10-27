# usage: fullb.sh EPISODE_DIR OUT_MP4   (builder cars, same world/HUD/audio)
cd /root/lab/car3d; GD=/root/tools/godot/Godot_v4.4.1-stable_linux.x86_64; export GODOT_SILENCE_ROOT_WARNING=1
D=$1; OUT=$2; B=$(basename $OUT .mp4)
N=$(python3 -c "import json;print(len(json.load(open('$D/frames.json'))['frames']))")
xvfb-run -a -s "-screen 0 1080x1920x24" $GD --path project --rendering-driver opengl3 --write-movie /root/lab/car3d/$B.avi --fixed-fps 30 --quit-after $N -- $D 0 builder > godot_$B.log 2>&1
ffmpeg -loglevel error -y -i $B.avi -c:v libx264 -pix_fmt yuv420p -crf 18 ${B}_g.mp4 && rm -f $B.avi
cd /root/video-engine && venv/bin/python lab/godot3d_challenge/compose.py --dir $D --video /root/lab/car3d/${B}_g.mp4 --out $OUT > /root/lab/car3d/compose_$B.log 2>&1
echo "DONE $B $N $(date -u +%T)" >> /root/lab/car3d/fullb_done.log
