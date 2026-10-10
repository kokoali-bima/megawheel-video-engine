#!/usr/bin/env python3
"""Publish alerts: a failing upload must never go unnoticed (owner 2026-10-11).

Every alert goes to three places:
  1. work/publish_alerts.log                       (history on the VM)
  2. renders/megawheel_arena/PUBLISH_ALERT.txt     (latest status; committed by the daily run so GitHub-side bots/agents
                                                    can forward it, same pattern as ANALYTICS_TELEGRAM.txt)
  3. Telegram, ONLY if credentials/telegram.env exists with BOT_TOKEN= and CHAT_ID= (optional, never committed)
The same alert key is sent once per UTC day (a dead token would otherwise repeat every run).
STICKY alerts (sticky=True: dead Drive token, token age, parked UPLOAD_FAILED video) stay "open" in the status file at
the end of every clean run until resolve(key) is called - a clean run must never hide a problem that still exists.

  python generators/publishing/alert.py ok            # mark the latest status OK (end of a clean run)
  python generators/publishing/alert.py test          # send a harmless test alert
  python generators/publishing/alert.py send LEVEL KEY TITLE BODY
"""
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = os.environ.get("MW_BASE", os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
STATUS_FILE = os.environ.get("MW_ALERT_FILE", os.path.join(BASE, "renders", "megawheel_arena", "PUBLISH_ALERT.txt"))
LOG_FILE = os.environ.get("MW_ALERT_LOG", os.path.join(BASE, "work", "publish_alerts.log"))
STATE_FILE = os.environ.get("MW_ALERT_STATE", os.path.join(BASE, "work", "publish_alert_state.json"))
TG_ENV = os.environ.get("MW_TG_ENV", os.path.join(BASE, "credentials", "telegram.env"))


def _now():
    return dt.datetime.now(dt.timezone.utc)


def _write(path, text, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, encoding="utf-8") as fh:
        fh.write(text)


def _telegram(text):
    """Optional direct Telegram message. Returns True/False; never raises, never prints the token."""
    if not os.path.exists(TG_ENV):
        return False
    try:
        cfg = dict(line.strip().split("=", 1) for line in open(TG_ENV, encoding="utf-8") if "=" in line)
        data = urllib.parse.urlencode({"chat_id": cfg["CHAT_ID"], "text": text[:3900]}).encode()
        urllib.request.urlopen(urllib.request.Request(
            f"https://api.telegram.org/bot{cfg['BOT_TOKEN']}/sendMessage", data=data), timeout=15).read()
        return True
    except Exception:
        return False


def _state():
    try:
        return json.load(open(STATE_FILE, encoding="utf-8"))
    except Exception:
        return {}


def _save_state(state):
    _write(STATE_FILE, json.dumps(state, indent=1))


def resolve(key):
    """The problem behind a sticky alert is gone (token alive again, video re-queued, ...)."""
    state = _state()
    if state.get("open", {}).pop(key, None) is not None:
        _save_state(state)


def send(level, key, title, body, sticky=False):
    """level: 'ALERT' (upload blocked / needs the owner) or 'WARN' (works now, will break soon). Returns True if sent."""
    now = _now()
    stamp = now.strftime("%Y-%m-%d %H:%M UTC")
    text = f"[MegaWheel {level}] {title}\n{stamp}\n\n{body}"
    _write(STATUS_FILE, f"STATUS: {level}\nTIME: {stamp}\nTITLE: {title}\n\n{body}\n")
    _write(LOG_FILE, f"{stamp} {level} {key} | {title} | {body.splitlines()[0] if body else ''}\n", "a")
    state = _state()
    if sticky:
        since = state.get("open", {}).get(key, {}).get("since", stamp)
        state.setdefault("open", {})[key] = dict(level=level, title=title, since=since,
                                                 detail=body.splitlines()[0] if body else "")
    today = now.strftime("%Y-%m-%d")
    if state.get(key) == today:
        _save_state(state)
        return False                                            # already told the owner today
    state[key] = today
    _save_state(state)
    sent = _telegram(text)
    print(f"[alert] {level} {key}: {title}" + (" (Telegram terkirim)" if sent else ""), flush=True)
    return True


def ok():
    """End of a clean run: STATUS OK, unless sticky problems are still open (then WARN/ALERT with the list)."""
    stamp = _now().strftime("%Y-%m-%d %H:%M UTC")
    open_ = _state().get("open", {})
    if not open_:
        _write(STATUS_FILE, f"STATUS: OK\nTIME: {stamp}\nTITLE: daily publish run finished without errors\n")
        return
    level = "ALERT" if any(v["level"] == "ALERT" for v in open_.values()) else "WARN"
    lines = "\n".join(f"- [{v['level']}] {v['title']} (sejak {v['since']}): {v['detail']}" for v in open_.values())
    _write(STATUS_FILE, f"STATUS: {level}\nTIME: {stamp}\nTITLE: upload harian selesai, tetapi ada masalah terbuka\n\n{lines}\n")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "ok":
        ok()
    elif cmd == "send" and len(sys.argv) >= 6:               # alert.py send LEVEL KEY TITLE BODY
        send(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "test":
        send("WARN", "test", "tes peringatan (abaikan)", "Ini hanya uji alert.py; tidak ada masalah.")
    else:
        sys.exit(__doc__)
