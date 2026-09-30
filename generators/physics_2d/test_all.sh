#!/usr/bin/env bash
# Smoke test / pass-rate check: preview-only runs (never renders, never touches the registry).
# Usage: bash generators/physics_2d/test_all.sh [series...] [--seeds FROM TO]
#   default: all series, seeds 901-903 (a range no real video uses)
# Run after every engine change, before commit. Exit 1 if any series has 0 passes or a Python error.
cd /root/video-engine || exit 1
series=(); from=901; to=903
while [ $# -gt 0 ]; do
  case $1 in
    --seeds) from=$2; to=$3; shift 3 ;;
    *) series+=("$1"); shift ;;
  esac
done
[ ${#series[@]} -eq 0 ] && series=(potholes bumps splash lava)
mkdir -p work/test_all
bad=0
for s in "${series[@]}"; do
  pass=0; n=0; reasons=""
  for seed in $(seq "$from" "$to"); do
    log="work/test_all/${s}_${seed}.log"
    name="TEST_${s}_${seed}"
    ./venv/bin/python generators/physics_2d/sim_engine.py --series "$s" --seed "$seed" --name "$name" \
        --preview-only > "$log" 2>&1 < /dev/null
    rc=$?
    n=$((n + 1))
    rm -rf "work/physics_2d/previews/$name"
    if [ $rc -eq 0 ]; then
      pass=$((pass + 1))
    elif grep -q Traceback "$log"; then
      echo "  !! $s seed $seed: PYTHON ERROR -> $log"; tail -n 3 "$log"; bad=1
    else
      r=$(grep -oE 'STOP: [^(.]*' "$log" | head -n 1 | cut -c7-70)
      reasons="$reasons\n    seed $seed: $r"
    fi
  done
  echo "$s: $pass/$n lolos"
  [ -n "$reasons" ] && echo -e "  STOP:$reasons"
  [ $pass -eq 0 ] && bad=1
done
echo "TEST_ALL_DONE bad=$bad"
exit $bad
