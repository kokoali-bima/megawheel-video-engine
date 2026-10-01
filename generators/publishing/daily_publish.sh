#!/usr/bin/env bash
# MegaWheel Arena: daily publish run (the ONE script cron / agents use for scheduled uploads, user 2026-10-01).
#   git pull -> plan (strict slots 11 CHALLENGE / 15 RACE / 19 SMASH, Sat 13:00 long) -> upload --confirm (max 5,
#   YouTube quota) -> Drive sync (archive aired videos) -> git push. Only APPROVED episodes are ever uploaded.
# Safe to run by cron once a day; a lock prevents overlapping runs; any failing step stops the run.
# Cron (VM 99.3, once a day, 12:00 WIB = 01:00 ET; one line):
#   0 12 * * * /root/video-engine/generators/publishing/daily_publish.sh >> /root/video-engine/work/daily_publish.log 2>&1
set -euo pipefail
cd /root/video-engine
exec 9>/tmp/megawheel_daily_publish.lock
flock -n 9 || { echo "[daily] $(date -u +%FT%TZ) sudah ada run lain yang berjalan -> keluar"; exit 0; }
echo "===== [daily] $(date -u +%FT%TZ) mulai"
# records left uncommitted by an earlier manual/agent run (plan, approve, ...) would block the pull: commit them first
bash git_sync.sh push "auto: records left uncommitted before daily run" | tail -2
bash git_sync.sh pull | tee /tmp/daily_pull.log
grep -q "OK: VM = GitHub" /tmp/daily_pull.log || { echo "[daily] STOP: git_sync pull gagal, tidak upload"; exit 1; }
./venv/bin/python generators/publishing/publish_queue.py plan | grep -E "queue\]" || true
./venv/bin/python generators/publishing/publish_queue.py upload --confirm --max 5
./venv/bin/python generators/publishing/drive_sync.py sync
./venv/bin/python generators/publishing/publish_queue.py plan | grep -E "PERINGATAN|stok" || true
bash git_sync.sh push "publish: daily run $(date -u +%F) [cron daily_publish.sh]"
echo "===== [daily] $(date -u +%FT%TZ) selesai"
