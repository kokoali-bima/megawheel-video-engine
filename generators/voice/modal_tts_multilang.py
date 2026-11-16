#!/usr/bin/env python3
"""Multilingual expressive announcer voice on Modal GPUs (ChatterboxMultilingualTTS).

Uses the exact same MegaWheel budget guard and modal_usage.json ledger as modal_tts.py,
cloning m1 (announcer_ref.wav) and f1 (announcer_f1_ref.wav) with high exaggeration.
"""
import datetime as dt
import io
import json
import os
import sys
import time

import modal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEDGER = os.path.join(ROOT, "modal_usage.json")
BUDGET_USD = 31.0
GPU_PRICE = {"T4": 0.000164, "L4": 0.000222, "A10": 0.000306}
OVERHEAD = 1.15
MAX_LINES = 100

app = modal.App("megawheel-tts-multilang")


def _download():
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    from faster_whisper import WhisperModel
    ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    WhisperModel("base", device="cpu", compute_type="int8")


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git")
    .pip_install("chatterbox-tts", "faster-whisper")
    .run_function(_download)
)


def _score(want: str, got: str) -> float:
    import difflib
    import re
    w1 = re.sub(r"[^\w\s]", "", want.lower()).split()
    w2 = re.sub(r"[^\w\s]", "", got.lower()).split()
    return difflib.SequenceMatcher(None, " ".join(w1), " ".join(w2)).ratio()


@app.function(image=image, gpu="T4", timeout=900)
def speak_multilang(items: list, refs: dict) -> dict:
    import importlib.metadata as md
    import torchaudio
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS, SUPPORTED_LANGUAGES
    from faster_whisper import WhisperModel

    t0 = time.time()
    model = ChatterboxMultilingualTTS.from_pretrained(device="cuda")
    asr = WhisperModel("base", device="cpu", compute_type="int8")

    paths = {}
    for name, data in (refs or {}).items():
        paths[name] = f"/tmp/ref_{name}.wav"
        with open(paths[name], "wb") as fh:
            fh.write(data)

    supported = set(SUPPORTED_LANGUAGES.keys()) if isinstance(SUPPORTED_LANGUAGES, dict) else set(SUPPORTED_LANGUAGES)
    wavs, qa = [], []
    for it in items:
        lang = it["lang"]
        mtl_lang = lang if lang in supported else ("ms" if lang == "id" and "ms" in supported else "en")
        rp = paths.get(it.get("ref", "m1"))
        ex = float(it.get("exaggeration", 1.15))
        cfg = float(it.get("cfg", 0.35))
        best = None
        for attempt in range(3):
            wav = model.generate(
                it["text"],
                language_id=mtl_lang,
                audio_prompt_path=rp,
                exaggeration=ex,
                cfg_weight=cfg,
            )
            buf = io.BytesIO()
            torchaudio.save(buf, wav.cpu(), model.sr, format="wav")
            data = buf.getvalue()
            with open("/tmp/take.wav", "wb") as fh:
                fh.write(data)
            heard = " ".join(sg.text for sg in asr.transcribe("/tmp/take.wav", language=lang, beam_size=3)[0])
            sc = _score(it["text"], heard)
            if best is None or sc > best[0]:
                best = (sc, data, heard, attempt)
            if sc >= 0.78:
                break
            ex, cfg = max(0.6, ex * 0.8), min(0.55, cfg + 0.08)
        wavs.append(best[1])
        qa.append(dict(lang=lang, mtl_lang=mtl_lang, text=it["text"], heard=best[2].strip(), score=round(best[0], 2), takes=best[3] + 1))

    meta = md.metadata("chatterbox-tts")
    return dict(
        wavs=wavs,
        qa=qa,
        supported=sorted(supported),
        secs=time.time() - t0,
        version=meta.get("Version"),
    )


def _ledger():
    if os.path.exists(LEDGER):
        with open(LEDGER) as fh:
            return json.load(fh)
    return {"budget_usd": BUDGET_USD, "runs": []}


@app.local_entrypoint()
def main(lines: str = "work/voice/lines_mtl.json", out: str = "work/voice/chatterbox_mtl",
         refs: str = "", note: str = "tts multilang"):
    with open(lines) as fh:
        items = json.load(fh)[:MAX_LINES]
    led = _ledger()
    month = dt.date.today().strftime("%Y-%m")
    spent = sum(r["cost_usd"] for r in led["runs"] if r["date"].startswith(month))
    worst = (150 + 35 * len(items)) * GPU_PRICE["L4"] * OVERHEAD
    print(f"[tts-mtl] bulan {month}: tercatat ${spent:.2f} / ${BUDGET_USD:.2f}; estimasi terburuk ${worst:.2f}")
    if spent + worst > BUDGET_USD:
        raise SystemExit("[tts-mtl] STOP: budget bulanan akan terlewati.")

    ref_map = {}
    for kv in filter(None, refs.split(",")):
        k, v = kv.split("=", 1)
        with open(v, "rb") as fh:
            ref_map[k] = fh.read()

    t0 = time.time()
    res = _budget_remote(
        "megawheel",
        {"label": "/root/video-engine/generators/voice/modal_tts_multilang.py::speak_multilang", "timeout": 900, "gpu": "L4"},
        speak_multilang, items, ref_map,
    )
    wall = time.time() - t0
    os.makedirs(out, exist_ok=True)
    for i, w in enumerate(res["wavs"]):
        with open(os.path.join(out, f"line_{i:03d}.wav"), "wb") as fh:
            fh.write(w)
    with open(os.path.join(out, "qa.json"), "w") as fh:
        json.dump(res["qa"], fh, indent=1, ensure_ascii=False)
    print(f"[tts-mtl] supported={res['supported']}")
    for q in res["qa"]:
        print(f"[tts-mtl] [{q['lang']}->{q['mtl_lang']}] QA {q['score']:.2f} x{q['takes']} '{q['text'][:35]}' -> '{q['heard'][:35]}'")
    cost = res["secs"] * GPU_PRICE["L4"] * OVERHEAD
    led["runs"].append(dict(
        date=dt.date.today().isoformat(), note=note, gpu="L4", engine="chatterbox-mtl",
        lines=len(items), gpu_seconds=round(res["secs"], 1), wall_seconds=round(wall, 1),
        cost_usd=round(cost, 4),
    ))
    with open(LEDGER, "w") as fh:
        json.dump(led, fh, indent=1)
    print(f"[tts-mtl] DONE {len(items)} lines: GPU {res['secs']:.0f}s, wall {wall:.0f}s, ~${cost:.3f} -> {out}")


import sys as _budget_sys
if "/root/channel-budget-guard" not in _budget_sys.path:
    _budget_sys.path.insert(0, "/root/channel-budget-guard")
try:
    from budget_guard import remote_call as _budget_remote
except ModuleNotFoundError:
    def _budget_remote(*a, **k):
        raise RuntimeError("Central budget guard unavailable; cloud call blocked")
