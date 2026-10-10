#!/usr/bin/env bash
# MegaWheel Arena: daily publish run (the ONE script cron / agents use for scheduled uploads, user 2026-10-01).
#   git pull -> PRE-FLIGHT (live token check) -> plan (strict slots 11 CHALLENGE / 15 RACE / 19 SMASH, Sun 13:00 long)
#   -> upload --confirm (max 5, YouTube quota) -> Drive sync (archive aired videos) -> git push (ALWAYS).
# Only APPROVED episodes are ever uploaded. A lock prevents overlapping runs.
# Hardened 2026-10-11 (upload kept dying): a dead token is detected BEFORE any queue item is touched; a failing
# upload no longer aborts the run before the state is pushed; failures raise an alert (PUBLISH_ALERT.txt, optional
# Telegram); Drive problems are never fatal. Exit code: 0 ok | 1 git | 2 upload error | 3 token dead | 4 quota.
# Cron (VM 99.3, once a day, 05:00 UTC = 12:00 WIB; one line):
#   0 5 * * * /root/video-engine/generators/publishing/daily_publish.sh >> /root/video-engine/work/daily_publish.log 2>&1
set -euo pipefail
cd /root/video-engine
exec 9>/tmp/megawheel_daily_publish.lock
flock -n 9 || { echo "[daily] $(date -u +%FT%TZ) sudah ada run lain yang berjalan -> keluar"; exit 0; }
echo "===== [daily] $(date -u +%FT%TZ) mulai"
PY=./venv/bin/python
PUB=generators/publishing
# records left uncommitted by an earlier manual/agent run (plan, approve, ...) would block the pull: commit them first
bash git_sync.sh push "auto: records left uncommitted before daily run" | tail -2
bash git_sync.sh pull | tee /tmp/daily_pull.log
if ! grep -q "OK: VM = GitHub" /tmp/daily_pull.log; then
  $PY $PUB/alert.py send ALERT git_pull "git_sync pull gagal - upload harian tidak jalan" "$(tail -3 /tmp/daily_pull.log)" || true
  echo "[daily] STOP: git_sync pull gagal, tidak upload"
  exit 1
fi
# pre-flight: live token check + token age + Drive + disk. A dead upload token stops here, before anything is touched.
PF_RC=0
$PY $PUB/preflight.py || PF_RC=$?
if [ "$PF_RC" -eq 3 ]; then                                  # only "token dead" stops the run
  echo "[daily] STOP: pre-flight gagal (token upload mati). Tidak ada upload. Alert ditulis ke PUBLISH_ALERT.txt"
  bash git_sync.sh push "publish: pre-flight FAILED $(date -u +%F) [cron daily_publish.sh]" | tail -1 || true
  exit 3
elif [ "$PF_RC" -ne 0 ]; then                                # a bug in the pre-flight must never block uploads
  echo "[daily] PERINGATAN: pre-flight error rc=$PF_RC (diabaikan; upload tetap mengecek token sendiri)"
fi
$PY $PUB/publish_queue.py plan | grep -E "queue\]" || true
UP_RC=0
$PY $PUB/publish_queue.py upload --confirm --max 5 || UP_RC=$?          # do not abort: state must still be pushed
$PY $PUB/drive_sync.py sync || echo "[daily] drive_sync berakhir dengan error (diabaikan: arsip, bukan upload)"
$PY $PUB/publish_queue.py plan | grep -E "PERINGATAN|stok" || true
if [ "$UP_RC" -eq 0 ]; then
  $PY $PUB/alert.py ok
fi
bash git_sync.sh push "publish: daily run $(date -u +%F) [cron daily_publish.sh]"
echo "===== [daily] $(date -u +%FT%TZ) selesai (upload rc=$UP_RC)"
exit "$UP_RC"
