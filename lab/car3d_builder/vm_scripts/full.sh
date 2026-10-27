cd /root/lab/car3d; GD=/root/tools/godot/Godot_v4.4.1-stable_linux.x86_64; export GODOT_SILENCE_ROOT_WARNING=1
D=/root/lab/ch3d/conv_SIM_LAVA_POTHOLES_V2_S026
N=$(python3 -c "import json;print(len(json.load(open('$D/frames.json'))['frames']))")
rm -f full.avi full_g.mp4
xvfb-run -a -s "-screen 0 1080x1920x24" $GD --path project --rendering-driver opengl3 --write-movie /root/lab/car3d/full.avi --fixed-fps 30 --quit-after $N -- $D 0 builder > godot_full.log 2>&1
ffmpeg -loglevel error -y -i full.avi -c:v libx264 -pix_fmt yuv420p -crf 18 full_g.mp4 && rm -f full.avi
cd /root/video-engine && venv/bin/python lab/godot3d_challenge/compose.py --dir $D --video /root/lab/car3d/full_g.mp4 --out /root/lab/car3d/S026_car3d_v4.mp4 > /root/lab/car3d/compose_full.log 2>&1
echo "FULL_DONE $N $(date -u +%T)" >> /root/lab/car3d/full_done4.log
