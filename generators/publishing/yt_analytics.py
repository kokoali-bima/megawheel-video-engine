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
