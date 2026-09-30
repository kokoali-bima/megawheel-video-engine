#!/usr/bin/env bash
# Try seeds with --preview-only and report which pass the analysis gate (previews go to work/, never renders/).
# Usage: bash generators/physics_2d/find_seeds.sh <series> <from> <to>      e.g. ... bumps 1 10
cd /root/video-engine || exit 1
series=$1
for s in $(seq "$2" "$3"); do
  name=$(printf "SIM_%s_V2_S%03d" "${series^^}" "$s")
  log="work/physics_2d/seed_${series}_$s.log"
  if grep -q "\"video_id\": \"$name\"" PRODUCTION_REGISTRY.json 2>/dev/null; then
    echo "seed $s SKIP  ($name already in registry)"
    continue
  fi
  if ./venv/bin/python generators/physics_2d/sim_engine.py --series "$series" --seed "$s" --preview-only > "$log" 2>&1 < /dev/null; then
    echo "seed $s PASS  $(grep -o 'cast\] final: .*' "$log")  $(grep -o 'timeline] [0-9.]*s' "$log")"
  else
    echo "seed $s FAIL  $(grep -oE 'STOP: .*' "$log" | cut -c1-110)"
  fi
  rm -rf "work/physics_2d/previews/$name"
done
