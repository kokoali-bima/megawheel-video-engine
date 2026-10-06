#!/bin/bash
# stop every story3d render on the VM (produce / modal run / helper scripts) without matching the caller's shell
me=$$; parent=$PPID
for pat in "produce_story3""d" "modal_story3""d" "/root/lab/s3d_"; do
  for p in $(pgrep -f "$pat"); do
    [ "$p" = "$me" ] || [ "$p" = "$parent" ] || kill "$p" 2>/dev/null
  done
done
sleep 1
echo "left: $(pgrep -fc "produce_story3""d|modal_story3""d")"
