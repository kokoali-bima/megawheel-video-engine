#!/usr/bin/env python3
"""Automatic pre-preview audit for MegaWheel Arena 2D videos (BLUEPRINT.md sections 5 and 6).

Usage:  cd /root/video-engine && ./venv/bin/python generators/physics_2d/audit.py <VIDEO_ID>

Writes renders/<VIDEO_ID>_audit.md + renders/<VIDEO_ID>_audit.json and sets the manifest
status to RENDERED_PENDING_APPROVAL (pass) or AUDIT_FAILED (fail). Exit code 0 = pass.
"""
import json
import os
import re
import subprocess
import sys
import time

import numpy as np

import registry

BASE = "/root/video-engine"
OUT = f"{BASE}/renders"
W, H = 1080, 1920
CTA = ("Tap LIKE if you enjoyed this video, DISLIKE if you didn't, "
       "and smash SUBSCRIBE to MegaWheel Arena!")
FAIL_RED = (230, 26, 38)
WIN_GOLD = (255, 194, 20)
BADGE_BOX = (300, 690, 780, 850)       # x0, y0, x1, y1 around the FAIL/WINNER badge
PILL_BOX = (395, 295, 685, 375)        # LEVEL n pill
OUTRO_BOX = (120, 630, 960, 1010)      # LIKE / SUBSCRIBE panel


def item(section, cid, desc, ok, value="", hard=True):
    return dict(section=section, id=cid, desc=desc, ok=bool(ok), value=str(value), hard=hard)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def volume(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    mx = re.search(r"max_volume: (-?[\d.]+) dB", err)
    mean = re.search(r"mean_volume: (-?[\d.]+) dB", err)
    return (float(mx.group(1)) if mx else None), (float(mean.group(1)) if mean else None)


def frame(path, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t):.3f}", "-i", path, "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw[:W * H * 3], dtype=np.uint8).reshape(H, W, 3)


def color_ratio(img, box, rgb, tol=45):
    x0, y0, x1, y1 = box
    region = img[y0:y1, x0:x1].astype(int)
    return float(np.all(np.abs(region - np.array(rgb)) < tol, axis=2).mean())


def run_audit(video_id, write=True):
    mpath = f"{OUT}/{video_id}.json"
    vpath = f"{OUT}/{video_id}.mp4"
    m = json.load(open(mpath))
    items = []

    # 5.1 analysis results recorded by the engine
    for c in m.get("analysis", []):
        items.append(item("5.1 Analisa fisika", c["id"], c["desc"], c["ok"], c["detail"], c["hard"]))
    if not m.get("analysis"):
        items.append(item("5.1 Analisa fisika", "analysis", "Hasil analisa engine ada di manifest", False,
                          "manifest tanpa 'analysis' (engine lama?)"))

    # 6.1 technical
    exists = os.path.exists(vpath)
    items.append(item("6.1 Teknis", "file", "File video ada", exists, vpath))
    if exists:
        p = probe(vpath)
        vs = next((s for s in p["streams"] if s["codec_type"] == "video"), {})
        aus = next((s for s in p["streams"] if s["codec_type"] == "audio"), {})
        dur = float(p["format"]["duration"])
        size_mb = int(p["format"]["size"]) / 1e6
        fps = m.get("fps", 30)
        items.append(item("6.1 Teknis", "video", "H.264 1080x1920",
                          vs.get("codec_name") == "h264" and vs.get("width") == W and vs.get("height") == H,
                          f"{vs.get('codec_name')} {vs.get('width')}x{vs.get('height')}"))
        items.append(item("6.1 Teknis", "fps", f"Frame rate {fps}", vs.get("r_frame_rate") == f"{fps}/1",
                          vs.get("r_frame_rate")))
        items.append(item("6.1 Teknis", "audio", "Audio AAC ada", aus.get("codec_name") == "aac", aus.get("codec_name")))
        items.append(item("6.1 Teknis", "duration", "Durasi 40-50 s dan sama dengan manifest (±0.3 s)",
                          40 <= dur <= 50 and abs(dur - m["duration"]) <= 0.3, f"{dur:.2f} s (manifest {m['duration']})"))
        lo, hi = (8, 20) if fps == 30 else (12, 32)
        items.append(item("6.1 Teknis", "size", f"Ukuran wajar ({lo}-{hi} MB)", lo <= size_mb <= hi,
                          f"{size_mb:.1f} MB", hard=False))

        # 6.2 audio
        mx, mean = volume(vpath)
        items.append(item("6.2 Audio", "max_volume", "max_volume -3..-0.1 dB (tidak clipping)",
                          mx is not None and -3 <= mx <= -0.1, f"{mx} dB"))
        items.append(item("6.2 Audio", "mean_volume", "mean_volume -20..-12 dB",
                          mean is not None and -20 <= mean <= -12, f"{mean} dB"))
        nar = m.get("narration", [])
        items.append(item("6.2 Audio", "cta", "Narasi terakhir = CTA baku", bool(nar) and nar[-1] == CTA,
                          (nar[-1][:60] + "...") if nar else "-"))
        n_levels = len(m["levels"])
        items.append(item("6.2 Audio", "narration_count", "Narasi lengkap (intro + hasil tiap level + CTA)",
                          len(nar) >= 2 * n_levels + 1, f"{len(nar)} baris"))

        # 6.3 sync, measured on real frames of the MP4
        for li, lv in enumerate(m["levels"]):
            img = frame(vpath, lv["start"] + 0.6)
            r = color_ratio(img, PILL_BOX, lv.get("level_color", (0, 0, 0)))
            items.append(item("6.3 Sinkron", f"L{li + 1}_pill", f"L{li + 1}: badge LEVEL {li + 1} tampil di awal level",
                              r > 0.2, f"{r:.0%} piksel warna level @ {lv['start'] + 0.6:.1f}s"))
            if "event_out" in lv:
                t = lv["event_out"] + 0.4
                img = frame(vpath, t)
                win = lv["outcome"] == "win"
                r = color_ratio(img, BADGE_BOX, WIN_GOLD if win else FAIL_RED)
                items.append(item("6.3 Sinkron", f"L{li + 1}_badge",
                                  f"L{li + 1}: badge {'WINNER' if win else 'FAIL'} tampil tepat di event",
                                  r > 0.2, f"{r:.0%} piksel badge @ {t:.1f}s"))
            else:
                items.append(item("6.3 Sinkron", f"L{li + 1}_badge", "Waktu event tersedia di manifest", False,
                                  "manifest tanpa event_out"))
        img = frame(vpath, dur - 0.8)
        r = color_ratio(img, OUTRO_BOX, (245, 245, 245), tol=20)
        items.append(item("6.3 Sinkron", "outro", "Panel outro LIKE/SUBSCRIBE tampil di akhir", r > 0.3,
                          f"{r:.0%} piksel panel @ {dur - 0.8:.1f}s"))

    # 5.2 previews
    prev = m.get("preview_dir", f"{OUT}/{video_id}_preview")
    pngs = sorted(os.listdir(prev)) if os.path.isdir(prev) else []
    items.append(item("5.2 Preview", "previews", "PNG preview tersedia (>= 6, termasuk outro)",
                      len(pngs) >= 6 and "outro.png" in pngs, f"{len(pngs)} file"))

    # 7 uniqueness
    if "fingerprint" in m:
        dup = registry.find_fingerprint(m["fingerprint"], exclude_id=video_id)
        items.append(item("7 Keunikan", "fingerprint", "Sidik jari unik di registry", dup is None,
                          m["fingerprint"] + (f" = {dup}" if dup else "")))
        other = registry.find_seed(m.get("series", ""), m["engine"].split()[-1], m["seed"], exclude_id=video_id)
        items.append(item("7 Keunikan", "seed", "Seed belum dipakai video lain", other is None, other or f"seed {m['seed']}"))
        streak = registry.series_streak(m.get("series", ""), exclude_id=video_id)
        items.append(item("7 Keunikan", "streak", "Maks 3 video berturut-turut dari seri yang sama", streak < 3,
                          f"{streak} video {m.get('series')} berturut-turut sebelum ini", hard=False))

    passed = all(i["ok"] for i in items if i["hard"])
    warns = [i for i in items if not i["hard"] and not i["ok"]]
    if write:
        write_report(video_id, m, items, passed, warns)
        m["status"] = "RENDERED_PENDING_APPROVAL" if passed else "AUDIT_FAILED"
        m["audit_path"] = f"{OUT}/{video_id}_audit.md"
        with open(mpath, "w") as fh:
            json.dump(m, fh, indent=2, ensure_ascii=False)
    return passed


def write_report(video_id, m, items, passed, warns):
    verdict = ("LOLOS" + (" dengan catatan" if warns else "")) if passed else "GAGAL"
    lines = [f"# Audit otomatis: {video_id}", "",
             f"- Tanggal: {time.strftime('%Y-%m-%d %H:%M')} · Auditor: audit.py (otomatis) · "
             f"Engine: {m.get('engine')} · Seed: {m.get('seed')} · Track: {m.get('track_id')}",
             "- Mengacu: `/root/sim-prototype/BLUEPRINT.md` bagian 5, 6, 7",
             f"- **Hasil: {verdict}**" + (" → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)" if passed
                                          else " → JANGAN dikirim ke user. Perbaiki / render seed lain."),
             ""]
    section = None
    for i in items:
        if i["section"] != section:
            section = i["section"]
            lines += ["", f"## {section}", "| Cek | Hasil | Nilai |", "|---|---|---|"]
        mark = "✅" if i["ok"] else ("❌" if i["hard"] else "⚠️")
        lines.append(f"| {i['desc']} | {mark} | {i['value']} |")
    lines += ["", "Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut)."]
    with open(f"{OUT}/{video_id}_audit.md", "w") as fh:
        fh.write("\n".join(lines) + "\n")
    with open(f"{OUT}/{video_id}_audit.json", "w") as fh:
        json.dump(dict(video_id=video_id, passed=passed, items=items), fh, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ok = run_audit(sys.argv[1])
    print(f"[audit] {'PASS' if ok else 'FAIL'} -> {OUT}/{sys.argv[1]}_audit.md")
    sys.exit(0 if ok else 1)
