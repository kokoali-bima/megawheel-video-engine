#!/bin/bash
# usage: wide.sh EPISODE_DIR OUT_MP4 [N_FRAMES] [START]  -> 1920x1080 full-video render (BeamNG cameras, Cars day, no HUD), episode audio
cd /root/lab/car3d; GD=/root/tools/godot/Godot_v4.4.1-stable_linux.x86_64; export GODOT_SILENCE_ROOT_WARNING=1
export CAR3D_CAM=beamng CAR3D_FACE=windshield CAR3D_DAY=1 CAR3D_WIDE=1
D=$1; OUT=$2; B=$(basename $OUT .mp4)
N=${3:-$(python3 -c "import json;print(len(json.load(open('$D/frames.json'))['frames']))")}; S0=${4:-0}
rm -rf project_wide; mkdir -p project_wide/.godot; cp project/*.gd project/*.tscn project/project.godot project_wide/; cp project/.godot/global_script_class_cache.cfg project_wide/.godot/
sed -i 's/window\/size\/viewport_width=1080/window\/size\/viewport_width=1920/; s/window\/size\/viewport_height=1920/window\/size\/viewport_height=1080/' project_wide/project.godot
xvfb-run -a -s "-screen 0 1920x1080x24" $GD --path project_wide --rendering-driver opengl3 --write-movie /root/lab/car3d/$B.avi --fixed-fps 30 --quit-after $N -- $D $S0 builder > godot_$B.log 2>&1
if [ "$S0" = "0" ] && [ -z "$3" ]; then
  ffmpeg -loglevel error -y -i $B.avi -i $D/mix.wav -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a aac -b:a 192k -shortest $OUT
else
  ffmpeg -loglevel error -y -i $B.avi -c:v libx264 -pix_fmt yuv420p -crf 18 $OUT
fi
rm -f $B.avi; echo "DONE $B $N $(date -u +%T)" >> /root/lab/car3d/wide_done.log
