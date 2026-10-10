#!/usr/bin/env python3
"""Pre-flight for the daily publish run (owner 2026-10-11: auto upload kept dying mid-run).

Checks BEFORE the queue is touched, so a dead token can never leave a half-done run:
  1. upload token, LIVE   - refreshes the token and asks YouTube who we are (1 quota unit). Dead -> ALERT, exit 3.
  2. token age            - Google refresh tokens of an OAuth app in status "Testing" die ~7 days after authorisation
                            (the real cause of the 2026-10-07 upload failure). Warn at 5 days, alert at 6.
                            A token that is still alive after 9 days proves the app is "In production" -> warnings stop.
  3. Drive token, LIVE    - dead is NOT fatal (Drive is only the archive): one WARN, Drive sync is skipped quietly.
  4. disk space           - < 3 GB free on the VM = WARN.
Exit codes: 0 ok (warnings allowed) | 3 upload token dead / unusable.
  python generators/publishing/preflight.py [--token PATH] [--no-drive]
  python generators/publishing/preflight.py seed youtube_token.json 2026-10-09T21:53:00Z   # record a known auth time
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("MW_BASE", os.path.abspath(os.path.join(HERE, "..", "..")))
sys.path.insert(0, os.path.join(BASE))
sys.path.insert(0, HERE)
import alert  # noqa: E402

CRED = os.path.join(BASE, "credentials")
META = os.environ.get("MW_TOKEN_META", os.path.join(CRED, "token_meta.json"))
WARN_DAYS, ALERT_DAYS, PROVEN_DAYS = 5.0, 6.0, 9.0
TOKENS = {"youtube_token.json": "upload", "youtube_analytics_token.json": "analytics", "drive_token.json": "drive"}


def _now():
    return dt.datetime.now(dt.timezone.utc)


def _load_meta():
    try:
        return json.load(open(META, encoding="utf-8"))
    except Exception:
        return {}


def _save_meta(m):
    os.makedirs(os.path.dirname(META), exist_ok=True)
    with open(META, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=1)


def refresh_hash(path):
    try:
        rt = json.load(open(path, encoding="utf-8")).get("refresh_token") or ""
        return hashlib.sha256(rt.encode()).hexdigest()[:12] if rt else ""
    except Exception:
        return ""


def track_age(name, path, now=None):
    """Age in days of the current authorisation. A changed refresh token = new authorisation = clock restarts."""
    now = now or _now()
    meta = _load_meta()
    h = refresh_hash(path)
    rec = meta.get(name)
    if not rec or rec.get("rt") != h:
        rec = {"rt": h, "authorized_at": now.isoformat(), "long_lived": False}
        meta[name] = rec
        _save_meta(meta)
    age = (now - dt.datetime.fromisoformat(rec["authorized_at"])).total_seconds() / 86400
    return age, rec, meta


def check_age(name, path, alive, now=None):
    """-> (state, message). state: 'ok' | 'warn' | 'alert' | 'proven'."""
    age, rec, meta = track_age(name, path, now)
    if rec.get("long_lived"):
        return "proven", f"{name}: umur {age:.1f} hari, app OAuth terbukti 'In production' (peringatan umur nonaktif)"
    if alive and age >= PROVEN_DAYS:
        rec["long_lived"] = True
        _save_meta(meta)
        return "proven", f"{name}: masih hidup di umur {age:.1f} hari -> app OAuth 'In production'; peringatan umur dimatikan"
    if age >= ALERT_DAYS:
        return "alert", f"{name}: umur {age:.1f} hari - bila app OAuth masih 'Testing' token ini mati dalam < 1 hari"
    if age >= WARN_DAYS:
        return "warn", f"{name}: umur {age:.1f} hari - bila app OAuth masih 'Testing' token mati sekitar hari ke-7"
    return "ok", f"{name}: umur {age:.1f} hari"


def seed(name, when):
    path = os.path.join(CRED, name)
    meta = _load_meta()
    meta[name] = {"rt": refresh_hash(path), "authorized_at": dt.datetime.fromisoformat(when.replace("Z", "+00:00")).isoformat(),
                  "long_lived": False}
    _save_meta(meta)
    print("[preflight] seed", name, "authorized_at", meta[name]["authorized_at"])


def run(token_path, with_drive=True):
    sys.path.insert(0, os.path.join(BASE, "generators", "physics_2d"))
    from core.youtube_uploader import AuthExpired, YouTubeUploader
    name = os.path.basename(token_path)
    try:
        who = YouTubeUploader(token_file=token_path).check_auth()
        print(f"[preflight] token upload HIDUP -> channel '{who}'")
        alive = True
    except AuthExpired as ex:
        alert.send("ALERT", "upload_token_dead", "Token upload YouTube MATI - upload otomatis berhenti",
                   f"{ex}\n\nCara memperbaiki: otorisasi ulang token upload (auth_youtube.py / langkah SSH tunnel), lalu "
                   f"jalankan ulang daily_publish.sh.\nPenyebab tetap: app OAuth masih 'Testing' (token mati tiap 7 hari). "
                   f"Google Cloud Console > OAuth consent screen > Publish app.")
        print(f"[preflight] STOP: token upload MATI ({ex})")
        return 3
    except Exception as ex:                                      # network etc.: do not claim the token is dead
        print(f"[preflight] PERINGATAN: cek token tidak bisa dilakukan ({type(ex).__name__}: {ex}); lanjut hati-hati")
        alive = True
    state, msg = check_age(name, token_path, alive)
    print("[preflight]", msg)
    if state == "alert":
        alert.send("ALERT", "upload_token_age", "Token upload hampir mati (umur token)", msg + "\nOtorisasi ulang sekarang, "
                   "atau Publish app OAuth ke 'In production' agar tidak mati lagi.")
    elif state == "warn":
        alert.send("WARN", "upload_token_age", "Token upload mendekati 7 hari", msg + "\nPublish app OAuth ke "
                   "'In production' (Google Cloud Console > OAuth consent screen) agar permanen.")
    free_gb = shutil.disk_usage(BASE).free / 2 ** 30
    if free_gb < 3:
        alert.send("WARN", "disk_low", "Disk VM hampir penuh", f"Sisa {free_gb:.1f} GB di {BASE}")
    print(f"[preflight] disk bebas {free_gb:.0f} GB")
    if with_drive:
        try:
            import drive_sync
            drive_sync.service()
            print("[preflight] token Drive HIDUP")
        except Exception as ex:
            kind = "MATI" if type(ex).__name__ == "DriveDead" else f"tidak bisa dicek ({type(ex).__name__})"
            print(f"[preflight] token Drive {kind}: sinkron Drive dilewati (upload YouTube tidak terpengaruh)")
            if type(ex).__name__ == "DriveDead":
                alert.send("WARN", "drive_token_dead", "Token Drive mati - arsip ke Drive berhenti",
                           "Upload YouTube tetap jalan. Perbaiki: jalankan 'drive_sync.py auth' (tunnel SSH).\n"
                           "Video tetap aman di VM sampai Drive pulih (file lokal tidak dihapus).")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "seed":
        seed(sys.argv[2], sys.argv[3])
        sys.exit(0)
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", default=os.path.join(CRED, "youtube_token.json"))
    ap.add_argument("--no-drive", action="store_true")
    a = ap.parse_args()
    sys.exit(run(a.token, with_drive=not a.no_drive))
