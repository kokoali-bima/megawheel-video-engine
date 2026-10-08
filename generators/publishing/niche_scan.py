"""Niche scan for a new channel (owner 2026-10-08: 3 channels, US market, trending + few creators, sharia-safe).
Read-only YouTube Data API through the analytics token (youtube.readonly, never the upload token). For every keyword:
the top videos published in the window (US region, by views) -> demand (views), competition (distinct channels,
their age and size) and outliers (small/young channels with big views = a gap others have not filled yet).
Quota: 100 units per keyword (search) + a few units for stats. Writes work/niche_scan_<date>.json/.md (stats only).
  venv/bin/python generators/publishing/niche_scan.py --days 180 --kw "earthquake simulation" "tsunami simulation" ...
"""
import argparse
import datetime as dt
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yt_analytics  # noqa: E402

BASE = "/root/video-engine"


def iso_dur(s):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    return (int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + int(m.group(3) or 0)) if m else 0


def scan(yt, kw, after, n):
    res = yt.search().list(part="snippet", q=kw, type="video", order="viewCount", regionCode="US",
                           relevanceLanguage="en", publishedAfter=after, maxResults=n).execute()
    vids = [it["id"]["videoId"] for it in res.get("items", [])]
    if not vids:
        return None
    vs = yt.videos().list(part="statistics,contentDetails,snippet", id=",".join(vids)).execute()["items"]
    chans = sorted({v["snippet"]["channelId"] for v in vs})
    cs = {}
    for i in range(0, len(chans), 50):
        for c in yt.channels().list(part="statistics,snippet", id=",".join(chans[i:i + 50])).execute()["items"]:
            cs[c["id"]] = c
    now = dt.datetime.now(dt.timezone.utc)
    rows = []
    for v in vs:
        c = cs.get(v["snippet"]["channelId"], {})
        cst = c.get("statistics", {})
        born = c.get("snippet", {}).get("publishedAt", "2000-01-01T00:00:00Z")
        age_m = (now - dt.datetime.fromisoformat(born.replace("Z", "+00:00"))).days / 30.4
        rows.append(dict(title=v["snippet"]["title"][:90], channel=v["snippet"]["channelTitle"],
                         views=int(v["statistics"].get("viewCount", 0)), secs=iso_dur(v["contentDetails"]["duration"]),
                         published=v["snippet"]["publishedAt"][:10], subs=int(cst.get("subscriberCount", 0) or 0),
                         ch_videos=int(cst.get("videoCount", 0) or 0), ch_age_months=round(age_m, 1)))
    views = [r["views"] for r in rows]
    young = {r["channel"] for r in rows if r["ch_age_months"] <= 12}
    small_hits = [r for r in rows if r["subs"] < 50_000 and r["views"] >= 500_000]
    return dict(keyword=kw, n=len(rows), median_views=int(statistics.median(views)), top_views=max(views),
                channels=len({r["channel"] for r in rows}), young_channels=len(young),
                shorts_share=round(sum(1 for r in rows if r["secs"] <= 60) / len(rows), 2),
                small_channel_hits=len(small_hits), rows=sorted(rows, key=lambda r: -r["views"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=180)
    ap.add_argument("--n", type=int, default=25)
    ap.add_argument("--kw", nargs="+", required=True)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    _, yt = yt_analytics.services()
    after = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.days)).strftime("%Y-%m-%dT00:00:00Z")
    out = []
    for kw in a.kw:
        r = scan(yt, kw, after, a.n)
        if r:
            out.append(r)
            print(f"[niche] {kw:<34} median {r['median_views']:>10,}  top {r['top_views']:>11,}  channels {r['channels']:>2}"
                  f"  young<=12m {r['young_channels']:>2}  small-channel hits {r['small_channel_hits']:>2}  shorts {r['shorts_share']:.0%}",
                  flush=True)
    day = dt.date.today().isoformat()
    path = f"{BASE}/work/niche_scan_{day}{('_' + a.tag) if a.tag else ''}"
    json.dump(dict(window_days=a.days, after=after, results=out), open(path + ".json", "w"), indent=1, ensure_ascii=False)
    md = [f"# Niche scan {day} (US, terbit {a.days} hari terakhir, top {a.n} per kata kunci menurut views)", "",
          "| Kata kunci | Median views | Top views | Channel berbeda | Channel umur <=12 bln | Hit channel kecil (<50rb subs, >=500rb views) | % Shorts |",
          "|---|---|---|---|---|---|---|"]
    for r in out:
        md.append(f"| {r['keyword']} | {r['median_views']:,} | {r['top_views']:,} | {r['channels']} | {r['young_channels']} | "
                  f"{r['small_channel_hits']} | {r['shorts_share']:.0%} |")
    for r in out:
        md += ["", f"## {r['keyword']}", "", "| Views | Detik | Terbit | Channel | Subs | Umur ch (bln) | Judul |", "|---|---|---|---|---|---|---|"]
        for x in r["rows"][:10]:
            md.append(f"| {x['views']:,} | {x['secs']} | {x['published']} | {x['channel']} | {x['subs']:,} | {x['ch_age_months']} | "
                      f"{x['title'].replace('|', '/')} |")
    open(path + ".md", "w").write("\n".join(md) + "\n")
    print(f"[niche] -> {path}.md")


if __name__ == "__main__":
    main()
