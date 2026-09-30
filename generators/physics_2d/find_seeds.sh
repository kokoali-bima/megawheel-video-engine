#!/usr/bin/env bash
# Try seeds with --preview-only and report which pass the analysis gate.
# Usage: bash generators/physics_2d/find_seeds.sh <series> <from> <to>      e.g. ... bumps 1 10
# Never run it on seeds that are already rendered (it would overwrite their manifest/preview).
cd /root/video-engine || exit 1
series=$1
for s in $(seq "$2" "$3"); do
  name=$(printf "SIM_%s_V2_S%03d" "${series^^}" "$s")
  log="work/physics_2d/seed_${series}_$s.log"
  if [ -f "renders/${name}.mp4" ]; then
    echo "seed $s SKIP  (${name}.mp4 already rendered)"
    continue
  fi
  if ./venv/bin/python generators/physics_2d/sim_engine.py --series "$series" --seed "$s" --preview-only > "$log" 2>&1 < /dev/null; then
    echo "seed $s PASS  $(grep -o 'story] .*' "$log")  $(grep -o 'timeline] [0-9.]*s' "$log")  $(grep -o 'unique: .*' "$log" | cut -d'|' -f4)"
  else
    echo "seed $s FAIL  $(grep -oE 'STOP: .*' "$log" | cut -c1-110)"
  fi
  rm -rf "renders/${name}.json" "renders/${name}_preview"
done
