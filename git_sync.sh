#!/usr/bin/env bash
# git_sync.sh — the ONE way to sync /root/video-engine (VM 192.168.99.3) with GitHub.
#   bash git_sync.sh status              compare VM with GitHub, list uncommitted files
#   bash git_sync.sh pull                start of every session: take the latest from GitHub (fast-forward only)
#   bash git_sync.sh push "<message>"    end of every task: smoke test (if engine code changed) -> commit -> push
# Rules: never edit on the VM without finishing with `push`; never force-push; never commit credentials/.
# LEDGER (owner 2026-10-07): modal_usage.json is written by every Modal run, so it is dirty after almost every task and
#   used to block `pull` (a render then started on OLD code). Now: `status` prints "ledger: BERSIH|KOTOR"; `pull` commits a
#   dirty ledger itself ("records: modal usage (auto)", merges both sides' runs, pushes) and prints it loudly. Anything else
#   dirty still blocks `pull`.
set -u
cd /root/video-engine || exit 1
export GIT_SSH_COMMAND="ssh -o BatchMode=yes"
git config user.name >/dev/null || git config user.name "kokoali-bima"
git config user.email "mu.aliwardana@gmail.com"                 # author email (user, 2026-09-30)

ledger_state() {
  if git status --porcelain -- modal_usage.json | grep -q .; then echo "KOTOR"; else echo "BERSIH"; fi
}

merge_ledger() {   # both machines appended runs: keep every run of both sides (called inside a conflicted rebase)
  python3 - <<'PYEOF'
import json, subprocess
def get(stage):
    r = subprocess.run(["git", "show", f":{stage}:modal_usage.json"], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {"runs": []}
up, mine = get(2), get(3)
runs, seen = [], set()
for r in up.get("runs", []) + mine.get("runs", []):
    k = json.dumps(r, sort_keys=True)
    if k not in seen:
        seen.add(k)
        runs.append(r)
up["runs"] = runs
json.dump(up, open("modal_usage.json", "w"), indent=1)
PYEOF
}

heal_ledger() {    # commit a dirty ledger (only when it is the ONLY dirty file), then bring it to GitHub
  [ "$(ledger_state)" = "KOTOR" ] || return 0
  others=$(git status --porcelain | grep -v ' modal_usage.json$' | wc -l)
  if [ "$others" -gt 0 ]; then return 0; fi
  echo "[git_sync] !! LEDGER modal_usage.json KOTOR -> di-commit otomatis (records: modal usage)"
  git add modal_usage.json && git commit -q -m "records: modal usage (auto)"
  if ! git pull -q --rebase origin main; then
    if git status --porcelain | grep -q '^UU modal_usage.json'; then
      merge_ledger && git add modal_usage.json && GIT_EDITOR=true git rebase --continue >/dev/null 2>&1
    fi
  fi
  if git status | grep -q "rebase in progress"; then echo "[git_sync] STOP: rebase ledger gagal. Laporkan ke user."; exit 1; fi
  git push -q origin main && echo "[git_sync] ledger tersimpan di GitHub"
}

status() {
  git fetch -q origin || { echo "[git_sync] STOP: fetch gagal (cek deploy key / jaringan)"; exit 1; }
  echo "[git_sync] VM $(git rev-parse --short HEAD) | GitHub $(git rev-parse --short origin/main) | ahead/behind: $(git rev-list --left-right --count HEAD...origin/main | tr '\t' '/')"
  n=$(git status --porcelain | wc -l)
  echo "[git_sync] file belum di-commit: $n | ledger (modal_usage.json): $(ledger_state)"
  [ "$n" -gt 0 ] && git status --porcelain | head -n 20
  return 0                                                   # status is informational: always exit 0
}

case "${1:-status}" in
  status)
    status ;;
  pull)
    heal_ledger
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
    echo "[git_sync] file yang akan di-commit:"; git diff --cached --stat | tail -n 25
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
