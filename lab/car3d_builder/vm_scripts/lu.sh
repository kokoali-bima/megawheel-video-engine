cd /root/lab/car3d; GD=/root/tools/godot/Godot_v4.4.1-stable_linux.x86_64; export GODOT_SILENCE_ROOT_WARNING=1
timeout 300 $GD --headless --path project --import > import.log 2>&1
grep -i "SCRIPT ERROR\|Parse Error" -A1 import.log | head -12
rm -f lineup_$1.png
xvfb-run -a -s "-screen 0 1080x1920x24" $GD --path project --rendering-driver opengl3 --write-movie /root/lab/car3d/lu.avi --fixed-fps 30 --quit-after 6 res://lineup.tscn -- $1 /root/lab/car3d/lineup_$1.png ${2:-normal} > lu.log 2>&1
grep -i "SCRIPT ERROR\|Parse Error\|ERROR" -A1 lu.log | head -12
ls -la lineup_$1.png
