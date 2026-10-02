#!/usr/bin/env python3
"""CHANGELOG.md from git history, grouped per day and per area (user 2026-10-03: track every code/setting change).
  python3 tools/make_changelog.py            # rewrites CHANGELOG.md at the repo root
Commit subjects start with an area prefix ("story:", "race25d v3:", "voice:", ...); automatic VM records are listed
separately so the human/agent changes stay readable."""
import collections
import os
import re
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
AREAS = [  # (label, regex on the subject)
    ("🎬 Story / episode panjang", r"^(story|story25d|stories)\b"),
    ("🏁 RACE (race25d)", r"^(race25d|race|lanes25d)\b"),
    ("💥 SMASH (smash25d)", r"^(smash25d|smash)\b"),
    ("🕳️ CHALLENGE (sim_engine)", r"^(sim_engine|challenge|produce|physics)\b"),
    ("🎙️ Suara / narasi", r"^(voice|tts|announcer|lipsync)\b"),
    ("🎵 Musik / lagu tema", r"^(music|songs|modal_song|modal_yue)\b"),
    ("📤 Upload / antrean / Drive", r"^(publish|publish_queue|queue|publishing|drive|episodes|daily)\b"),
    ("📊 Analytics", r"^(analytics)\b"),
    ("🎨 Branding", r"^(branding)\b"),
    ("🧪 Lab (eksperimen)", r"^(lab|godot|godot_race|blender3d)\b"),
    ("📚 Dokumen", r"^(docs|error log|gitignore)\b"),
]
AUTO = r"^(records|Merge branch|queue: .*approved|analytics: daily report|music: .*\+ ledger|story: .*\+ voice ledger)"


def area_of(subject):
    s = subject.lower()
    for label, rx in AREAS:
        if re.match(rx, s):
            return label
    return "🔧 Lain-lain"


def main():
    log = subprocess.run(["git", "-C", ROOT, "log", "--date=short", "--format=%ad\t%h\t%s"],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    days = collections.OrderedDict()
    for line in log:
        date, h, subj = line.split("\t", 2)
        days.setdefault(date, []).append((h, subj))
    out = ["# CHANGELOG — MegaWheel Arena video engine", "",
           "Dibuat otomatis oleh `tools/make_changelog.py` dari riwayat git (terbaru di atas). Setelan terbaik yang",
           "berlaku: **CONFIG_BEST.md**. Kesalahan & pelajaran: **ERROR_LOG.md**.", ""]
    for date, items in days.items():
        out.append(f"## {date}")
        groups, auto = collections.OrderedDict(), []
        for h, subj in items:
            if re.match(AUTO, subj):
                auto.append((h, subj))
            else:
                groups.setdefault(area_of(subj), []).append((h, subj))
        for label, rows in groups.items():
            out.append(f"**{label}**")
            out += [f"- `{h}` {subj}" for h, subj in rows]
        if auto:
            out.append(f"<details><summary>otomatis VM ({len(auto)})</summary>\n")
            out += [f"- `{h}` {subj}" for h, subj in auto]
            out.append("\n</details>")
        out.append("")
    with open(os.path.join(ROOT, "CHANGELOG.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))
    print(f"[changelog] {sum(len(v) for v in days.values())} commits, {len(days)} days -> CHANGELOG.md")


if __name__ == "__main__":
    main()
