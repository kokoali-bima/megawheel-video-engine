#!/bin/bash
# LAB method A for SMASH: normal smash25d preview (format identical) + Godot FX layer + extra explosion SFX.
#   bash lab/godot_fx/run_smash_fx.sh <seed> [arena]
set -u
cd /root/video-engine
SEED=${1:-777}; ARENA=${2:-lava}; NAME=LAB_SMASH_${SEED}
D=/root/lab/fx/$NAME; mkdir -p $D
venv/bin/python -u lab/godot_fx/capture_smash.py --seed $SEED --name $NAME --arena $ARENA 2>&1 | grep -E "lab-capture|checks|result|STOP|Error|Traceback" | tail -6
SRC=work/lanes25d/previews/$NAME/$NAME.mp4
[ -f $SRC ] || { echo "no source video"; exit 1; }
rm -rf $D/frames && mkdir -p $D/frames && ffmpeg -loglevel error -i $SRC $D/frames/%05d.png
N=$(ls $D/frames | wc -l); echo "frames: $N"
mkdir -p /root/lab/fx/sprites && venv/bin/python - <<'PY'
import sys, os
sys.path.insert(0, "lab/godot_prototype"); import export_sprites as E
E.OUT = "/root/lab/fx/sprites"; os.makedirs(E.OUT, exist_ok=True)
E.se.load_cast(); E.se.detect_font()
import json
meta = {vk: E.body_png(vk) for vk in ["sports","police","taxi","f1","bus","firetruck","icecream","bigrig","monster","monster2"]}
json.dump(dict(ppm=E.PPM, cars=meta), open(E.OUT + "/cast.json", "w"))
print("sprites ok")
PY
GD=/root/tools/godot/Godot_v4.4.1-stable_linux.arm64
export GODOT_SILENCE_ROOT_WARNING=1
timeout 60 $GD --headless --path lab/godot_fx/project --quit-after 5 -- $D /root/lab/fx/sprites 2>&1 | grep -E "SCRIPT ERROR|Parse" && { echo PARSE_ERROR; exit 1; }
S=$(date +%s)
xvfb-run -a -s "-screen 0 1080x1920x24" $GD --path lab/godot_fx/project --rendering-driver opengl3 --write-movie $D/fx.avi --fixed-fps 30 --quit-after $N -- $D /root/lab/fx/sprites > $D/godot.log 2>&1
echo "godot render: $(( $(date +%s) - S )) s"; grep -E "SCRIPT ERROR|ERROR:" $D/godot.log | grep -v MSAA | sort | uniq -c | head -5
venv/bin/python - "$D" "$SRC" <<'PY'
import sys, json, subprocess
sys.path.insert(0, "generators/physics_2d"); import sim_engine as se, numpy as np
D, SRC = sys.argv[1], sys.argv[2]
cues = json.load(open(D + "/cues.json"))["fx"]
dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",SRC],capture_output=True,text=True).stdout)
n = int((dur + 1) * se.SR); x = np.zeros(n)
def place(sig, t, g):
    i = int(t * se.SR)
    if 0 <= i < n: m = min(len(sig), n - i); x[i:i+m] += sig[:m] * g
for c in cues:
    t = c["f"] / 30.0
    if c["type"] in ("wreck", "missile", "ringout"):
        place(se.synth_eruption(seed=47), t, 1.0); place(se.synth_shatter(seed=3), t + 0.03, 0.6)
    elif c["type"] == "hit" and c.get("power", 0) > 0.6:
        place(se.synth_impact(1.0, seed=9), t, 0.5)
se.write_wav(D + "/extra.wav", x[:int(dur * se.SR)] / max(1e-9, np.max(np.abs(x)) or 1) * 0.9)
print("extra sfx:", sum(1 for c in cues if c["type"] in ("wreck","missile")), "explosions")
PY
ffmpeg -loglevel error -y -i $D/fx.avi -i $SRC -i $D/extra.wav -filter_complex "[1:a][2:a]amix=inputs=2:weights=1 0.7:normalize=0,alimiter=limit=0.95[a]" -map 0:v -map "[a]" -c:v libx264 -pix_fmt yuv420p -crf 19 -c:a aac -b:a 192k -shortest $D/${NAME}_GODOT_FX.mp4
cp $SRC $D/${NAME}_ORIGINAL.mp4
ffmpeg -loglevel error -y -i $D/${NAME}_ORIGINAL.mp4 -i $D/${NAME}_GODOT_FX.mp4 -filter_complex "[0:v]scale=540:960[a];[1:v]scale=540:960[b];[a][b]hstack[v]" -map "[v]" -map 1:a -c:v libx264 -crf 21 -c:a aac -shortest $D/${NAME}_BANDINGKAN.mp4
rm -f $D/fx.avi
ls -la $D/*.mp4
echo FX_DONE
