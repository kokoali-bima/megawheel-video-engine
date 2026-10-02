#!/usr/bin/env python3
"""YouTube Analytics for MegaWheel Arena: weekly performance report (read-only).

Own token (does NOT touch the upload token used by the cron):
  venv/bin/python generators/publishing/yt_analytics.py auth --port 8086   # once; user opens the URL (SSH tunnel)
  venv/bin/python generators/publishing/yt_analytics.py report [--days 28] [--drive]

Report: per-video views, watch time, average view duration / percentage, likes, subscribers gained, grouped by
series (CHALLENGE / RACE / SMASH / STORY), channel daily totals, best and worst. Markdown ->
renders/megawheel_arena/ANALYTICS_REPORT.md (+ Drive review/analytics/ with --drive).
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BASE = "/root/video-engine"
CRED = f"{BASE}/credentials"
SECRET = f"{CRED}/client_secrets.json"                # same Google Cloud project as the YouTube upload client
TOKEN = f"{CRED}/youtube_analytics_token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/yt-analytics.readonly"]
OUT = f"{BASE}/renders/megawheel_arena/ANALYTICS_REPORT.md"
TG = f"{BASE}/renders/megawheel_arena/ANALYTICS_TELEGRAM.txt"     # short plain text for a Telegram bot
JS = f"{BASE}/renders/megawheel_arena/ANALYTICS_LATEST.json"      # machine-readable (agents on other VMs)
# NOTE: these files hold statistics only (no tokens / keys); credentials/ is git-ignored.
QUEUE = f"{BASE}/renders/megawheel_arena/PUBLISH_QUEUE.json"


def auth(port):
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(SECRET, SCOPES)
    creds = flow.run_local_server(host="localhost", port=port, open_browser=False, access_type="offline",
                                  prompt="consent",
                                  authorization_prompt_message="[analytics] buka URL ini di browser PC:\n{url}\n")
    with open(TOKEN, "w") as fh:
        fh.write(creds.to_json())
    os.chmod(TOKEN, 0o600)
    print("[analytics] token tersimpan:", TOKEN)


def services():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds.valid:
        creds.refresh(Request())
        with open(TOKEN, "w") as fh:
            fh.write(creds.to_json())
    return build("youtubeAnalytics", "v2", credentials=creds), build("youtube", "v3", credentials=creds)


def series_of(title):
    t = title.lower()
    if "story ep" in t or "full episode" in t:
        return "STORY"
    if "smash" in t:
        return "SMASH"
    if "race" in t or "finish line" in t or "survive the" in t:
        return "RACE"
    return "CHALLENGE"


def upcoming(hours=36):
    """Next scheduled / queued uploads (from PUBLISH_QUEUE.json), in WIB."""
    try:
        with open(QUEUE) as fh:
            items = json.load(fh)["items"]
    except Exception:
        return []
    now = dt.datetime.now(dt.timezone.utc)
    out = []
    for it in items:
        t = dt.datetime.fromisoformat(it["publish_at_utc"].replace("Z", "+00:00"))
        if now <= t <= now + dt.timedelta(hours=hours):
            wib = t + dt.timedelta(hours=7)
            out.append(f"{wib:%a %d/%m %H:%M} WIB - Ep {it['episode']} - {it['status']}")
    return out


def telegram(start, end, days, tot, groups, rows, titles):
    """ANALYTICS_TELEGRAM.txt (< 4000 chars, plain text) + ANALYTICS_LATEST.json."""
    t = [f"📊 MegaWheel Arena - {days} hari ({start:%d/%m}-{end:%d/%m})",
         f"👀 {tot[0]:,} views | ⏱️ {tot[1]:,} menit | 👥 +{tot[2]} subs",
         "(data YouTube Analytics terlambat 1-3 hari)", ""]
    if groups:
        t.append("Per seri:")
        for s_, rs in sorted(groups.items(), key=lambda kv: -sum(r[1] for r in kv[1])):
            v = sum(r[1] for r in rs)
            t.append(f"- {s_}: {v:,} views / {len(rs)} video, {sum(r[4] for r in rs) / len(rs):.0f}% ditonton")
        t.append("")
    if rows:
        t.append("🏆 Top 3:")
        for r in rows[:3]:
            t.append(f"- {titles.get(r[0], r[0])[:60]}: {r[1]:,} views ({r[4]:.0f}%)")
        w = rows[-1]
        t += [f"🐢 Terlemah: {titles.get(w[0], w[0])[:60]}: {w[1]:,} views", ""]
    nxt = upcoming()
    if nxt:
        t.append("🗓️ Upload 36 jam ke depan:")
        t += [f"- {x}" for x in nxt]
    text = "\n".join(t)[:3900]
    with open(TG, "w") as fh:
        fh.write(text + "\n")
    data = dict(generated=dt.datetime.now(dt.timezone.utc).isoformat(), start=str(start), end=str(end), days=days,
                channel=dict(views=tot[0], minutes=tot[1], subs=tot[2]),
                series={s_: dict(videos=len(rs), views=sum(r[1] for r in rs),
                                 avg_view_pct=round(sum(r[4] for r in rs) / len(rs), 1)) for s_, rs in groups.items()},
                videos=[dict(id=r[0], title=titles.get(r[0], ""), series=series_of(titles.get(r[0], "")), views=r[1],
                             minutes=r[2], avg_view_s=r[3], avg_view_pct=r[4], likes=r[5], subs=r[6]) for r in rows],
                upcoming=nxt)
    with open(JS, "w") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    print(f"[analytics] -> {TG}, {JS}")


def report(days, to_drive):
    ya, yt = services()
    end = dt.date.today() - dt.timedelta(days=1)          # analytics lag ~1-2 days
    start = end - dt.timedelta(days=days - 1)
    metrics = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,subscribersGained"
    per = ya.reports().query(ids="channel==MINE", startDate=str(start), endDate=str(end), metrics=metrics,
                             dimensions="video", sort="-views", maxResults=200).execute()
    daily = ya.reports().query(ids="channel==MINE", startDate=str(start), endDate=str(end),
                               metrics="views,estimatedMinutesWatched,subscribersGained", dimensions="day").execute()
    rows = per.get("rows", [])
    ids = [r[0] for r in rows]
    titles = {}
    for i in range(0, len(ids), 50):
        for it in yt.videos().list(part="snippet,contentDetails", id=",".join(ids[i:i + 50])).execute()["items"]:
            titles[it["id"]] = it["snippet"]["title"]
    lines = [f"# ANALYTICS_REPORT — MegaWheel Arena", "",
             f"Periode {start} s/d {end} ({days} hari). Dibuat {dt.datetime.now():%Y-%m-%d %H:%M} oleh yt_analytics.py.", ""]
    tot = [sum(r[i] for r in daily.get("rows", [])) for i in (1, 2, 3)]
    lines += [f"**Channel:** {tot[0]:,} views · {tot[1]:,} menit tontonan · +{tot[2]} subscriber", ""]
    groups = {}
    for r in rows:
        groups.setdefault(series_of(titles.get(r[0], "")), []).append(r)
    lines += ["## Per seri", "", "| Seri | Video | Views | Rata-rata views | Rata-rata % ditonton | Subs |", "|---|---|---|---|---|---|"]
    for s, rs in sorted(groups.items(), key=lambda kv: -sum(r[1] for r in kv[1])):
        v = sum(r[1] for r in rs)
        lines.append(f"| {s} | {len(rs)} | {v:,} | {v // max(1, len(rs)):,} | "
                     f"{sum(r[4] for r in rs) / len(rs):.0f}% | {sum(r[6] for r in rs)} |")
    lines += ["", "## Per video (urut views)", "",
              "| Video | Seri | Views | Menit | Durasi rata2 (dtk) | % ditonton | Likes | Subs |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        title = re.sub(r"\|", "/", titles.get(r[0], r[0]))[:70]
        lines.append(f"| [{title}](https://youtu.be/{r[0]}) | {series_of(title)} | {r[1]:,} | {r[2]:,} | {r[3]} | "
                     f"{r[4]:.0f}% | {r[5]} | {r[6]} |")
    if rows:
        best, worst = rows[0], rows[-1]
        lines += ["", f"**Terbaik:** {titles.get(best[0], best[0])} ({best[1]:,} views, {best[4]:.0f}% ditonton)",
                  f"**Terlemah:** {titles.get(worst[0], worst[0])} ({worst[1]:,} views, {worst[4]:.0f}% ditonton)"]
    with open(OUT, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    telegram(start, end, days, tot, groups, rows, titles)
    print("\n".join(lines[:12]))
    print(f"[analytics] -> {OUT}")
    if to_drive:
        import drive_sync as d
        md = f"/tmp/ANALYTICS_{end}.md"
        with open(md, "w") as fh:
            fh.write("\n".join(lines) + "\n")
        d.upload(md, d.folder("review", "analytics"), os.path.basename(md))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["auth", "report"])
    ap.add_argument("--port", type=int, default=8086)
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--drive", action="store_true")
    a = ap.parse_args()
    auth(a.port) if a.cmd == "auth" else report(a.days, a.drive)
