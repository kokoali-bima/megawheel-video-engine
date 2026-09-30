#!/usr/bin/env python3
"""Episode management for MegaWheel Arena: pending -> approved episode -> uploaded.

Usage (cd /root/video-engine):
  ./venv/bin/python generators/publishing/episodes.py list
  ./venv/bin/python generators/publishing/episodes.py approve <VIDEO_ID> [<VIDEO_ID> ...]   # ONLY on the user's explicit approval
  ./venv/bin/python generators/publishing/episodes.py reject <VIDEO_ID> "<reason>"
  ./venv/bin/python generators/publishing/episodes.py set <EP> views=1234 likes=56 retention=71% note="..."
  ./venv/bin/python generators/publishing/episodes.py log                                    # rebuild EPISODE_LOG.md

Layout: renders/megawheel_arena/pending/<date>_<series>_s<seed>/   (rendered, waiting for review)
        renders/megawheel_arena/S01/E001_<render date>_<series>/   (approved; episode numbers never have gaps)
        renders/megawheel_arena/rejected/...                       (rejected by the user)
        renders/megawheel_arena/EPISODE_LOG.md                      (generated, for evaluation)
"""
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "physics_2d"))
import registry  # noqa: E402

BASE = "/root/video-engine"
CHANNEL_DIR = f"{BASE}/renders/megawheel_arena"
LOG = f"{CHANNEL_DIR}/EPISODE_LOG.md"
SEASON_SIZE = 30                     # Season 1 = episodes 1-30 (about one month at one Short per day)
UPLOADED = ("UPLOADED_PRIVATE", "UPLOADED_UNLISTED", "UPLOADED_PUBLIC")
METRIC_KEYS = ("views", "likes", "comments", "retention", "subs_gained", "note")


def _today():
    return time.strftime("%Y-%m-%d")


def cast_names():
    try:
        with open(f"{BASE}/cast/characters.json") as fh:
            return {c["vehicle_id"]: c["name"] for c in json.load(fh)["characters"]}
    except FileNotFoundError:
        return {}


def all_videos():
    return registry.load()["videos"]


def episodes():
    return sorted((e for e in all_videos() if e.get("episode")), key=lambda e: e["episode"])


def pending():
    return [e for e in all_videos() if e.get("status") == "RENDERED_PENDING_APPROVAL"]


def by_episode(ep):
    return next((e for e in episodes() if e["episode"] == int(ep)), None)


def _rewrite_paths(folder_abs, video_id, old_abs, new_abs):
    for fn in (f"{video_id}.json", f"{video_id}_audit.md", f"{video_id}_audit.json"):
        p = f"{folder_abs}/{fn}"
        if os.path.exists(p):
            with open(p) as fh:
                s = fh.read()
            with open(p, "w") as fh:
                fh.write(s.replace(old_abs, new_abs))


def _update_manifest(folder_abs, video_id, **fields):
    p = f"{folder_abs}/{video_id}.json"
    with open(p) as fh:
        m = json.load(fh)
    m.update(fields)
    with open(p, "w") as fh:
        json.dump(m, fh, indent=2, ensure_ascii=False)
    return m


def _move(e, new_rel):
    old_abs, new_abs = f"{BASE}/{e['folder']}", f"{BASE}/{new_rel}"
    if os.path.exists(new_abs):
        raise SystemExit(f"[episodes] STOP: {new_rel} sudah ada")
    os.makedirs(os.path.dirname(new_abs), exist_ok=True)
    shutil.move(old_abs, new_abs)
    _rewrite_paths(new_abs, e["video_id"], old_abs, new_abs)
    return new_abs


def approve(video_id):
    e = registry.get(video_id)
    if not e:
        raise SystemExit(f"[episodes] STOP: {video_id} tidak ada di registry")
    if e.get("status") != "RENDERED_PENDING_APPROVAL":
        raise SystemExit(f"[episodes] STOP: {video_id} berstatus {e.get('status')}, bukan RENDERED_PENDING_APPROVAL")
    eps = episodes()
    ep = (eps[-1]["episode"] + 1) if eps else 1
    season = (ep - 1) // SEASON_SIZE + 1
    new_rel = f"renders/megawheel_arena/S{season:02d}/E{ep:03d}_{e.get('render_date', _today())}_{e['series']}"
    new_abs = _move(e, new_rel)
    m = _update_manifest(new_abs, video_id, episode=ep, season=season, status="APPROVED", approved_date=_today())
    title = f"{m.get('title_base', m['title'].replace(' #Shorts', ''))} | Ep. {ep} #Shorts"
    _update_manifest(new_abs, video_id, title=title)
    registry.update(video_id, status="APPROVED", episode=ep, season=season, folder=new_rel,
                    audit=f"{new_rel}/{video_id}_audit.md", approved_date=_today(), title=title)
    print(f"[episodes] APPROVED {video_id} -> S{season:02d} Ep. {ep}: {title}")
    return ep


def reject(video_id, reason):
    e = registry.get(video_id)
    if not e or e.get("status") != "RENDERED_PENDING_APPROVAL":
        raise SystemExit(f"[episodes] STOP: {video_id} tidak sedang menunggu approval")
    new_rel = f"renders/megawheel_arena/rejected/{os.path.basename(e['folder'])}"
    new_abs = _move(e, new_rel)
    _update_manifest(new_abs, video_id, status="REJECTED", reject_reason=reason)
    registry.update(video_id, status="REJECTED", folder=new_rel, audit=f"{new_rel}/{video_id}_audit.md",
                    reject_reason=reason, rejected_date=_today())
    print(f"[episodes] REJECTED {video_id}: {reason}")


def mark_uploaded(ep, url, privacy):
    e = by_episode(ep)
    status = f"UPLOADED_{privacy.upper()}"
    registry.update(e["video_id"], status=status, youtube_url=url, upload_date=_today())
    _update_manifest(f"{BASE}/{e['folder']}", e["video_id"], status=status, youtube_url=url, upload_date=_today())


def set_fields(ep, pairs):
    e = by_episode(ep)
    if not e:
        raise SystemExit(f"[episodes] STOP: episode {ep} tidak ada")
    fields = {}
    for kv in pairs:
        k, v = kv.split("=", 1)
        if k not in METRIC_KEYS + ("privacy_note",):
            raise SystemExit(f"[episodes] STOP: field '{k}' tidak dikenal. Pilihan: {', '.join(METRIC_KEYS)}")
        fields[k] = v
    fields["metrics_updated"] = _today()
    registry.update(e["video_id"], **fields)
    print(f"[episodes] Ep. {ep} updated: {fields}")


def write_log():
    names = cast_names()
    cast = lambda e: ", ".join(names.get(v, v) for v in e.get("vehicles", []))
    lines = ["# EPISODE LOG — MegaWheel Arena", "",
             f"> Dibuat otomatis oleh `generators/publishing/episodes.py` ({time.strftime('%Y-%m-%d %H:%M')}). "
             "Jangan diedit manual; isi metrik dengan `episodes.py set`.",
             "> Status: APPROVED = siap upload · UPLOADED_* = sudah di YouTube.", "",
             "## Episode", "",
             "| Ep | Season | Seri | Tokoh (L1, L2, Juara) | Render | Approve | Upload | Status | URL | Views | Likes | Retensi | Catatan |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in episodes():
        lines.append(f"| {e['episode']} | S{e['season']:02d} | {e['series']} | {cast(e)} | {e.get('render_date', '')} | "
                     f"{e.get('approved_date', '')} | {e.get('upload_date') or ''} | {e['status']} | "
                     f"{e.get('youtube_url') or ''} | {e.get('views', '')} | {e.get('likes', '')} | "
                     f"{e.get('retention', '')} | {e.get('note', '')} |")
    if not episodes():
        lines.append("| – | | | | | | | | | | | | belum ada episode |")
    lines += ["", "## Menunggu approval (`pending/`)", "",
              "| Video ID | Seri | Tokoh | Render | Durasi | Folder |", "|---|---|---|---|---|---|"]
    for e in pending():
        lines.append(f"| {e['video_id']} | {e['series']} | {cast(e)} | {e.get('render_date', '')} | "
                     f"{e.get('duration', '')} s | `{e['folder']}` |")
    if not pending():
        lines.append("| – | | | | | tidak ada |")
    rej = [e for e in all_videos() if e.get("status") == "REJECTED"]
    if rej:
        lines += ["", "## Ditolak", "", "| Video ID | Alasan | Tanggal |", "|---|---|---|"]
        lines += [f"| {e['video_id']} | {e.get('reject_reason', '')} | {e.get('rejected_date', '')} |" for e in rej]
    os.makedirs(CHANNEL_DIR, exist_ok=True)
    with open(LOG, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return LOG


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "approve":
        for vid in args:
            approve(vid)
    elif cmd == "reject":
        reject(args[0], " ".join(args[1:]) or "no reason given")
    elif cmd == "set":
        set_fields(args[0], args[1:])
    elif cmd == "list":
        names = cast_names()
        for e in episodes():
            print(f"Ep. {e['episode']:<3} S{e['season']:02d} {e['series']:<9} {e['status']:<18} "
                  f"{', '.join(names.get(v, v) for v in e['vehicles'])}  {e.get('youtube_url') or ''}")
        for e in pending():
            print(f"PENDING  {e['video_id']:<24} {e['series']:<9} {', '.join(names.get(v, v) for v in e['vehicles'])}")
    elif cmd != "log":
        sys.exit(__doc__)
    print(f"[episodes] log -> {write_log()}")


if __name__ == "__main__":
    main()
