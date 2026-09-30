#!/usr/bin/env bash
# git_sync.sh — the ONE way to sync /root/video-engine (VM 192.168.99.3) with GitHub.
#   bash git_sync.sh status              compare VM with GitHub, list uncommitted files
#   bash git_sync.sh pull                start of every session: take the latest from GitHub (fast-forward only)
#   bash git_sync.sh push "<message>"    end of every task: smoke test (if engine code changed) -> commit -> push
# Rules: never edit on the VM without finishing with `push`; never force-push; never commit credentials/.
set -u
cd /root/video-engine || exit 1
export GIT_SSH_COMMAND="ssh -o BatchMode=yes"
git config user.name >/dev/null || git config user.name "kokoali-bima"
git config user.email "mu.aliwardana@gmail.com"                 # author email (user, 2026-09-30)

status() {
  git fetch -q origin || { echo "[git_sync] STOP: fetch gagal (cek deploy key / jaringan)"; exit 1; }
  echo "[git_sync] VM $(git rev-parse --short HEAD) | GitHub $(git rev-parse --short origin/main) | ahead/behind: $(git rev-list --left-right --count HEAD...origin/main | tr '\t' '/')"
  n=$(git status --porcelain | wc -l)
  echo "[git_sync] file belum di-commit: $n"
  [ "$n" -gt 0 ] && git status --porcelain | head -n 20
}

case "${1:-status}" in
  status)
    status ;;
  pull)
    if [ -n "$(git status --porcelain)" ]; then
      echo "[git_sync] STOP: ada perubahan belum di-commit di VM. Selesaikan dulu dengan: bash git_sync.sh push \"<pesan>\""
      git status --porcelain | head -n 20; exit 1
    fi
    git pull -q --ff-only origin main || { echo "[git_sync] STOP: tidak bisa fast-forward (riwayat bercabang). Laporkan ke user, jangan force."; exit 1; }
    echo "[git_sync] OK: VM = GitHub $(git rev-parse --short HEAD) — $(git log -1 --format=%s)" ;;
  push)
    msg="${2:-}"
    [ -z "$msg" ] && { echo "[git_sync] STOP: pesan commit wajib: bash git_sync.sh push \"<pesan>\""; exit 1; }
    if git status --porcelain | grep -qE '\.py$|\.sh$'; then
      echo "[git_sync] kode berubah -> smoke test dulu (generators/physics_2d/test_all.sh)"
      bash generators/physics_2d/test_all.sh > work/git_sync_test.log 2>&1 < /dev/null
      tail -n 12 work/git_sync_test.log
      if ! grep -q "TEST_ALL_DONE bad=0" work/git_sync_test.log; then
        echo "[git_sync] STOP: smoke test gagal. Tidak di-commit. Log: work/git_sync_test.log"; exit 1
      fi
    fi
    git add -A
    if git diff --cached --name-only | grep -q '^credentials/'; then
      echo "[git_sync] STOP: credentials/ ikut ter-stage. Dibatalkan."; git reset -q; exit 1
    fi
    if git diff --cached --quiet; then
      echo "[git_sync] tidak ada perubahan untuk di-commit"
    else
      git commit -q -m "$msg" && echo "[git_sync] commit $(git rev-parse --short HEAD): $msg"
    fi
    git pull -q --rebase origin main || { echo "[git_sync] STOP: konflik saat rebase. Laporkan ke user."; exit 1; }
    git push -q origin main && echo "[git_sync] OK: pushed. VM = GitHub $(git rev-parse --short HEAD)" ;;
  *)
    echo "usage: bash git_sync.sh status | pull | push \"<message>\""; exit 1 ;;
esac
