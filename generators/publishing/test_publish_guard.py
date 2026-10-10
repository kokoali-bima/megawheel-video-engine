#!/usr/bin/env python3
"""Tests for the publish guard (2026-10-11): alerts, token age, upload failure paths, Drive quietness.
No network, no YouTube, no real queue: everything is faked or in a temp dir.
  cd /root/video-engine && venv/bin/python generators/publishing/test_publish_guard.py
"""
import datetime as dt
import json
import os
import sys
import tempfile
import types

TMP = tempfile.mkdtemp(prefix="mwguard_")
os.environ.update(MW_STATUS_JSON=f"{TMP}/PUBLISH_STATUS.json", MW_ALERT_FILE=f"{TMP}/PUBLISH_ALERT.txt", MW_ALERT_LOG=f"{TMP}/alerts.log",
                  MW_ALERT_STATE=f"{TMP}/state.json", MW_TG_ENV=f"{TMP}/none.env", MW_TOKEN_META=f"{TMP}/meta.json")
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, BASE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(BASE, "generators", "physics_2d"))

import alert  # noqa: E402
import preflight  # noqa: E402

FAILS = []


def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{extra}]" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


def status_text():
    return open(os.environ["MW_ALERT_FILE"], encoding="utf-8").read()


# ---------------------------------------------------------------- alerts
sent1 = alert.send("ALERT", "k1", "Judul A", "baris satu\nbaris dua")
sent2 = alert.send("ALERT", "k1", "Judul A", "baris satu")             # same key, same day
sent3 = alert.send("WARN", "k2", "Judul B", "x")
check("alert: first send true, same key same day suppressed", sent1 and not sent2 and sent3)
check("alert: status file holds the latest alert", "STATUS: WARN" in status_text() and "Judul B" in status_text())
alert.ok()
check("alert: ok() marks OK", status_text().startswith("STATUS: OK"))
check("alert: history log has all 3 events", len(open(os.environ["MW_ALERT_LOG"]).read().splitlines()) == 3)

alert.send("WARN", "sticky1", "Drive mati", "detail", sticky=True)
alert.ok()
check("alert: sticky problem stays visible after a clean run (status WARN, listed)",
      status_text().startswith("STATUS: WARN") and "Drive mati" in status_text())
alert.send("ALERT", "sticky2", "Video ditolak", "d2", sticky=True)
alert.ok()
check("alert: highest open level wins", status_text().startswith("STATUS: ALERT"))
alert.resolve("sticky1")
alert.resolve("sticky2")
alert.ok()
check("alert: once resolved, ok() reports OK again", status_text().startswith("STATUS: OK"))

alert.update_status(stock=dict(all_ok=False, roles={"race": dict(ok=False, missing_days=["2026-10-16"])}))
alert.done(0)
alert.send("WARN", "sticky3", "Drive mati", "d", sticky=True)
alert.done(3)
sj = json.load(open(os.environ["MW_STATUS_JSON"]))
check("status json: merges stock + last_run, keeps open issues, rc 3 -> token_dead",
      sj["stock"]["all_ok"] is False and sj["last_run"]["result"] == "token_dead" and sj["last_run"]["upload_rc"] == 3
      and any(i["key"] == "sticky3" for i in sj["open_issues"]))
alert.resolve("sticky3")

# ---------------------------------------------------------------- token age
tok = f"{TMP}/tok.json"
json.dump({"refresh_token": "abc", "client_id": "c"}, open(tok, "w"))
t0 = dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc)
check("age: new token starts at 0 -> ok", preflight.check_age("tok.json", tok, True, now=t0)[0] == "ok")
check("age: day 5.2 -> warn", preflight.check_age("tok.json", tok, True, now=t0 + dt.timedelta(days=5.2))[0] == "warn")
check("age: day 6.5 -> alert", preflight.check_age("tok.json", tok, True, now=t0 + dt.timedelta(days=6.5))[0] == "alert")
check("age: alive at day 9.5 -> proven (app is In production)",
      preflight.check_age("tok.json", tok, True, now=t0 + dt.timedelta(days=9.5))[0] == "proven")
check("age: proven stays proven", preflight.check_age("tok.json", tok, True, now=t0 + dt.timedelta(days=12))[0] == "proven")
json.dump({"refresh_token": "NEW", "client_id": "c"}, open(tok, "w"))
check("age: a new refresh token restarts the clock",
      preflight.check_age("tok.json", tok, True, now=t0 + dt.timedelta(days=13))[0] == "ok")

# ---------------------------------------------------------------- uploader helpers
from core.youtube_uploader import AuthExpired, QuotaExceeded, http_reason  # noqa: E402
from googleapiclient.errors import HttpError  # noqa: E402
import httplib2  # noqa: E402


def http_error(status, reason):
    body = json.dumps({"error": {"errors": [{"reason": reason}], "code": status}}).encode()
    return HttpError(httplib2.Response({"status": status}), body)


check("http_reason parses quotaExceeded", http_reason(http_error(403, "quotaExceeded")) == "quotaExceeded")
check("http_reason survives garbage", http_reason(HttpError(httplib2.Response({"status": 500}), b"not json")) == "")

# ---------------------------------------------------------------- upload() failure paths (fake queue + fake uploader)
import publish_queue as pq  # noqa: E402
import episodes  # noqa: E402

os.makedirs(f"{TMP}/vid", exist_ok=True)
for n in ("A", "B", "C"):
    open(f"{TMP}/vid/{n}.mp4", "wb").write(b"0" * 1000)
    json.dump(dict(title=f"T {n}", description="d", tags=["x"]), open(f"{TMP}/vid/{n}.json", "w"))
future = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")


def fresh_queue():
    return {"items": [dict(episode=i, video_id=v, status="QUEUED", publish_at_utc=future, role="short")
                      for i, v in ((1, "A"), (2, "B"), (3, "C"))]}


class FakeUploader:
    mode = "ok"
    calls = []

    def check_auth(self):
        if FakeUploader.mode == "dead_preflight":
            raise AuthExpired("invalid_grant test")
        return "TestChannel"

    def upload_shorts(self, video_path, **kw):
        n = os.path.basename(video_path)[0]
        FakeUploader.calls.append(n)
        m = FakeUploader.mode
        if m == "auth_mid":
            raise AuthExpired("dead mid-run")
        if m == "quota":
            raise QuotaExceeded("quotaExceeded")
        if m == "reject_B" and n == "B":
            raise http_error(400, "invalidMetadata")
        if m == "network":
            raise ConnectionResetError("reset")
        return dict(url=f"https://youtu.be/{n}")


import core.youtube_uploader as yu  # noqa: E402
yu.YouTubeUploader = FakeUploader
pq.episodes = types.SimpleNamespace(
    BASE=TMP, by_episode=lambda ep: dict(status="APPROVED", folder="vid", video_id="ABC"[ep - 1], series="x"),
    mark_uploaded=lambda *a, **k: None, write_log=lambda: None, with_credit=lambda d: d)
pq.show = lambda: None
pq.reconcile_uploading = lambda q, u: None
pq.role_of = lambda s: "short"
state = {}
pq.load = lambda: state["q"]
pq.save = lambda q: state.__setitem__("saved", json.loads(json.dumps(q)))


def run(mode, **kw):
    FakeUploader.mode, FakeUploader.calls = mode, []
    state["q"] = fresh_queue()
    for f in (os.environ["MW_ALERT_STATE"],):
        if os.path.exists(f):
            os.remove(f)
    try:
        pq.upload(5, **kw)
        return 0
    except SystemExit as ex:
        return ex.code if isinstance(ex.code, int) else 99


st = lambda: {it["episode"]: it["status"] for it in state["q"]["items"]}  # noqa: E731

rc = run("ok")
check("upload ok: 3 uploaded, all SCHEDULED, rc 0", rc == 0 and set(st().values()) == {"SCHEDULED"} and FakeUploader.calls == list("ABC"))
rc = run("dead_preflight")
check("dead token at pre-flight: rc!=0, NOTHING touched, 0 upload calls",
      rc not in (0, None) and FakeUploader.calls == [] and set(st().values()) == {"QUEUED"} and "upload_token_dead" in open(os.environ["MW_ALERT_LOG"]).read())
rc = run("auth_mid")
check("token dies mid-run: rc 3, first item back to QUEUED (nothing sent)", rc == 3 and st()[1] == "QUEUED")
rc = run("quota")
check("quota exhausted: rc 4, item stays UPLOADING for reconcile, alert is WARN",
      rc == 4 and st()[1] == "UPLOADING" and "WARN quota" in open(os.environ["MW_ALERT_LOG"]).read())
rc = run("reject_B")
check("one bad video (HTTP 400): parked UPLOAD_FAILED, the others still upload, rc 0",
      rc == 0 and st() == {1: "SCHEDULED", 2: "UPLOAD_FAILED", 3: "SCHEDULED"} and FakeUploader.calls == list("ABC"))
rc = run("network")
check("network error: rc 2, item UPLOADING (never re-uploaded blindly), run stops", rc == 2 and st()[1] == "UPLOADING" and FakeUploader.calls == ["A"])
os.rename(f"{TMP}/vid/B.mp4", f"{TMP}/vid/B.gone")
rc = run("ok")
check("missing MP4: that item is parked, the others upload, rc 0",
      rc == 0 and st() == {1: "SCHEDULED", 2: "UPLOAD_FAILED", 3: "SCHEDULED"} and FakeUploader.calls == list("AC"))
os.rename(f"{TMP}/vid/B.gone", f"{TMP}/vid/B.mp4")
rc = run("ok", dry=True)
check("dry-run: nothing uploaded, nothing changed", rc == 0 and FakeUploader.calls == [] and set(st().values()) == {"QUEUED"})

# ---------------------------------------------------------------- Drive: dead token is reported once, never fatal
import drive_sync  # noqa: E402

drive_sync._dead = True
calls = []
drive_sync.sync_one = lambda *a, **k: calls.append(1) or (_ for _ in ()).throw(drive_sync.DriveDead("x"))
drive_sync.TOKEN = f"{TMP}/drive_token.json"                         # never the real credential
open(drive_sync.TOKEN, "w").close()
try:
    drive_sync.try_sync_one("V")
    check("drive: try_sync_one on dead token is silent and does not raise", True)
except Exception as ex:
    check("drive: try_sync_one on dead token is silent and does not raise", False, str(ex))
try:
    drive_sync.service()
    check("drive: service() raises DriveDead when flagged dead", False)
except drive_sync.DriveDead:
    check("drive: service() raises DriveDead when flagged dead", True)

print("\n%d failed" % len(FAILS) if FAILS else "\nALL PASS")
sys.exit(1 if FAILS else 0)
