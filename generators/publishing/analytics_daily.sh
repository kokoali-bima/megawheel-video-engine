#!/usr/bin/env bash
# MegaWheel Arena: daily analytics report (read-only) for agents / Telegram (user 2026-10-03).
# Writes renders/megawheel_arena/ANALYTICS_TELEGRAM.txt + ANALYTICS_LATEST.json + ANALYTICS_REPORT.md, pushes to GitHub.
# Waits for the daily publish run (same lock) so the two never sync git at the same time.
# Cron (VM 99.3, 06:30 UTC = 13:30 WIB, before the user's 14:00 WIB bot):
#   30 6 * * * /root/video-engine/generators/publishing/analytics_daily.sh >> /root/video-engine/work/analytics_daily.log 2>&1
set -uo pipefail
cd /root/video-engine
exec 9>/tmp/megawheel_daily_publish.lock
flock -w 3600 9 || { echo "[analytics] $(date -u +%FT%TZ) lock timeout -> keluar"; exit 0; }
echo "===== [analytics] $(date -u +%FT%TZ) mulai"
bash git_sync.sh push "records before analytics" 2>&1 | tail -1
bash git_sync.sh pull 2>&1 | tail -1
venv/bin/python generators/publishing/yt_analytics.py report --days 28 || { echo "[analytics] report GAGAL"; exit 1; }
python3 tools/make_changelog.py || echo "[analytics] changelog gagal (lanjut)"
bash git_sync.sh push "analytics: daily report $(date -u +%F)" 2>&1 | tail -1
echo "===== [analytics] $(date -u +%FT%TZ) selesai"
