cd /root/lab/car3d; GD=/root/tools/godot/Godot_v4.4.1-stable_linux.x86_64; export GODOT_SILENCE_ROOT_WARNING=1
D=${D:-/root/lab/ch3d/conv_SIM_LAVA_POTHOLES_V2_S026}
rm -f project/t1.avi
xvfb-run -a -s "-screen 0 1080x1920x24" $GD --path project --rendering-driver opengl3 --write-movie /root/lab/car3d/t1.avi --fixed-fps 30 --quit-after $1 -- $D $2 builder > godot_t1.log 2>&1
grep -i "error\|script\|invalid\|null" godot_t1.log | head -12
ffmpeg -y -loglevel error -i t1.avi -vf "select=not(mod(n\,5)),crop=1080:700:0:760,scale=360:-1,tile=4x2" -frames:v 1 t1_sheet.png; ls -la t1.avi t1_sheet.png
