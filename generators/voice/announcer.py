"""MegaWheel Arena announcer voice: Chatterbox TTS on Modal (user choice "C", 2026-10-01) with a local cache.

- The voice comes from ONE synthetic reference (branding/voice/announcer_ref.wav, made with Edge TTS, never a real
  person), so every episode has the same announcer.
- prefetch(items) generates only the lines that are not cached yet, in ONE Modal call (generators/voice/modal_tts.py,
  budget guard + modal_usage.json ledger). Lines are stored post-processed (clarity + arena PA echo).
- get(text, style) returns the cached line at se.SR. If prefetch fails the caller falls back to Edge TTS for the
  whole video (never a mix of two voices in one video).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "generators", "physics_2d"))
import sim_engine as se  # noqa: E402

# speakers: m1 = male ring announcer / play-by-play, f1 = female colour commentator (same energy)
REFS = {"m1": os.path.join(ROOT, "branding", "voice", "announcer_ref.wav"),
        "f1": os.path.join(ROOT, "branding", "voice", "announcer_f1_ref.wav")}
CACHE = os.path.join(ROOT, "work", "voice", "cache")
BATCH = os.path.join(ROOT, "work", "voice", "batch")
MODAL = os.path.join(ROOT, "venv-modal", "bin", "modal")
VOICE_ID = "chatterbox:mw-announcers-m1f1"
# style -> (exaggeration, cfg_weight): sample "C" used exaggeration +0.35 over the base and cfg 0.3
STYLE = {"intro": (1.15, 0.3), "hype": (1.35, 0.3), "call": (1.3, 0.3), "norm": (0.9, 0.35),
         "clear": (0.65, 0.5)}                               # short calls (READY... SET... GO!) need a calm, clear take
QA_MIN = 0.75                                            # speech-recognition match a cached take must reach
_CLEAN = "highpass=f=90,equalizer=f=3000:t=q:w=1.2:g=3,acompressor=threshold=-18dB:ratio=3:attack=5:release=90"
FXS = {"arena": _CLEAN + ",aecho=0.8:0.5:45|90:0.22|0.12",   # SMASH ARENA: PA echo
       "studio": _CLEAN}                                       # RACE / CHALLENGE narrator: dry


def _ref_md5(who):
    with open(REFS[who], "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()[:10]


def path(text, style, who="m1", fx="arena"):
    key = hashlib.md5(f"chatterbox-qa1|{who}|{_ref_md5(who)}|{STYLE[style]}|{FXS[fx]}|{text}".encode()).hexdigest()[:14]
    return os.path.join(CACHE, f"{key}.wav")


def prefetch(items, note="announcer"):
    """items: [(text, style, who[, fx])]. Returns True when every line is cached (missing ones made on Modal)."""
    items = [tuple(it) if len(it) == 4 else (*it, "arena") for it in items]
    if not all(os.path.exists(r) for r in REFS.values()) or not os.path.exists(MODAL):
        print(f"[voice] announcer tidak tersedia (ref/modal tidak ada) -> Edge TTS", flush=True)
        return False
    os.makedirs(CACHE, exist_ok=True)
    for rnd in range(2):                                         # 2nd round: re-take the lines that failed QA
        todo = list(dict.fromkeys(it for it in items if not os.path.exists(path(*it))))
        if not todo:
            break
        _generate(todo, items, f"{note} r{rnd + 1}")
    return all(os.path.exists(path(*it)) for it in items)


def cached(text, style, who="m1", fx="arena"):
    return os.path.exists(path(text, style, who, fx))


def _generate(todo, items, note):
    if todo:
        shutil.rmtree(BATCH, ignore_errors=True)
        os.makedirs(BATCH)
        lines = [dict(text=t, exaggeration=STYLE[s][0], cfg=STYLE[s][1], ref=w) for t, s, w, _ in todo]
        with open(os.path.join(BATCH, "lines.json"), "w") as fh:
            json.dump(lines, fh, indent=1)
        try:
            r = subprocess.run([MODAL, "run", "generators/voice/modal_tts.py", "--lines", os.path.join(BATCH, "lines.json"),
                                "--out", BATCH, "--refs", ",".join(f"{k}={v}" for k, v in REFS.items()), "--note", note],
                               cwd=ROOT, capture_output=True, text=True,
                               timeout=1500)
            for ln in (r.stdout + r.stderr).splitlines():
                if ln.startswith("[tts] DONE") or ln.startswith("[tts] QA:") or ln.startswith("[tts] STOP"):
                    print(ln.split(" license=")[0], flush=True)
        except Exception as ex:                                  # network / Modal down: caller uses Edge TTS
            print(f"[voice] Modal gagal: {ex}", flush=True)
        qa = []
        if os.path.exists(os.path.join(BATCH, "qa.json")):
            with open(os.path.join(BATCH, "qa.json")) as fh:
                qa = json.load(fh)
        for i, (t, s, w, fx) in enumerate(todo):
            src = os.path.join(BATCH, f"line_{i:02d}.wav")
            if i < len(qa) and qa[i]["score"] < QA_MIN:              # garbled take: never cached (Edge fallback)
                print(f"[voice] QA gagal ({qa[i]['score']}): '{t}' terdengar '{qa[i]['heard']}'", flush=True)
                continue
            if os.path.exists(src):
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-af", FXS[fx], "-ac", "1", "-ar",
                                str(se.SR), path(t, s, w, fx)], check=True)
        print(f"[voice] {len(todo)} kalimat baru diminta, {len(items) - len(todo)} dari cache", flush=True)


def get(text, style, who="m1", fx="arena"):
    x = se.read_wav(path(text, style, who, fx))
    nz = np.nonzero(np.abs(x) > 0.01)[0]                         # trim silence (same as se.tts)
    if len(nz):
        x = x[max(0, nz[0] - 200): nz[-1] + 2000]
    return x
