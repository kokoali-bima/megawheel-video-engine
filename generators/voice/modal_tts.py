"""Expressive announcer voice on Modal GPUs (Chatterbox TTS, open source), with the same monthly budget guard as
generators/blender3d/modal_render.py. Test / sample generator (user 2026-10-01: "tidak adakah suara yang bisa kita
build pakai mesin modal.com kita?").

Run on VM 99.3 (cd /root/video-engine):
  venv-modal/bin/modal run generators/voice/modal_tts.py --lines work/voice/lines.json --out work/voice/chatterbox
  lines.json = [{"text": "...", "exaggeration": 0.9, "cfg": 0.4, "ref": "m1"}, ...]   (ref: key of --refs, or true =
  the single --ref voice, or false = Chatterbox default voice)
  --refs m1=branding/voice/announcer_ref.wav,f1=branding/voice/announcer_f1_ref.wav   synthetic reference voices
  (never a real person's voice)
Every run is logged in modal_usage.json. The run is REFUSED if this month's logged spend + the worst-case estimate
would pass BUDGET_USD.
"""
import datetime as dt
import io
import json
import os
import time

import modal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEDGER = os.path.join(ROOT, "modal_usage.json")
BUDGET_USD = 29.0                       # monthly cap (user, 2026-09-30); Modal workspace limit = $30
GPU_PRICE = {"T4": 0.000164, "L4": 0.000222, "A10": 0.000306}   # $/s (modal.com/pricing)
OVERHEAD = 1.15
MAX_LINES = 60

app = modal.App("megawheel-tts")


def _download():
    from chatterbox.tts import ChatterboxTTS
    from faster_whisper import WhisperModel
    ChatterboxTTS.from_pretrained(device="cpu")                # bake the weights into the image (no GPU time)
    WhisperModel("base.en", device="cpu", compute_type="int8")


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git")
    .pip_install("chatterbox-tts", "faster-whisper")
    .run_function(_download)
)


_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "         "seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def _num(n):
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else " " + _ONES[n % 10])
    if n < 1000:
        return _ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + _num(n % 100))
    return str(n)


def _words(s):
    """Normalised words; digits become words ('30 days' == 'thirty days')."""
    import re
    s = re.sub(r"\d+", lambda m: " " + _num(int(m.group())) + " ", s.lower().replace("...", " "))
    return re.sub(r"[^a-z ]", " ", s).split()


def _score(want, got):
    """Letter-level match 0..1 between the script line and what speech recognition heard (made-up names like
    'Kraggor' heard as 'Cragger' still pass; a wrong word like 'Siren' -> 'Lyroid' does not)."""
    import difflib
    return difflib.SequenceMatcher(None, " ".join(_words(want)), " ".join(_words(got))).ratio()


@app.function(image=image, gpu="L4", timeout=900)
def speak(items: list, ref: bytes = b"", refs: dict = None) -> dict:
    import importlib.metadata as md

    import torchaudio
    from chatterbox.tts import ChatterboxTTS
    from faster_whisper import WhisperModel
    t0 = time.time()
    model = ChatterboxTTS.from_pretrained(device="cuda")
    asr = WhisperModel("base.en", device="cpu", compute_type="int8")   # QA: does the take say the line?
    paths = {}
    for name, data in ({"__single__": ref} if ref else {}).items() | (refs or {}).items():
        paths[name] = f"/tmp/ref_{name}.wav"
        with open(paths[name], "wb") as fh:
            fh.write(data)
    wavs, qa = [], []
    for it in items:
        r = it.get("ref")
        rp = paths.get("__single__") if r is True else paths.get(r) if isinstance(r, str) else None
        ex, cfg = float(it.get("exaggeration", 0.5)), float(it.get("cfg", 0.5))
        best = None
        for attempt in range(4):                                 # re-take until speech recognition hears the line
            wav = model.generate(it["text"], audio_prompt_path=rp, exaggeration=ex, cfg_weight=cfg)
            buf = io.BytesIO()
            torchaudio.save(buf, wav.cpu(), model.sr, format="wav")
            data = buf.getvalue()
            with open("/tmp/take.wav", "wb") as fh:
                fh.write(data)
            heard = " ".join(sg.text for sg in asr.transcribe("/tmp/take.wav", language="en", beam_size=3)[0])
            sc = _score(it["text"], heard)
            if best is None or sc > best[0]:
                best = (sc, data, heard, attempt)
            if sc >= 0.85:
                break
            ex, cfg = max(0.5, ex * 0.8), min(0.6, cfg + 0.1)    # calmer + closer to the text for the next take
        wavs.append(best[1])
        qa.append(dict(text=it["text"], heard=best[2].strip(), score=round(best[0], 2), takes=best[3] + 1))
    meta = md.metadata("chatterbox-tts")
    return dict(wavs=wavs, qa=qa, secs=time.time() - t0,
                license=meta.get("License") or meta.get("License-Expression") or "?", version=meta.get("Version"))


def _ledger():
    if os.path.exists(LEDGER):
        with open(LEDGER) as fh:
            return json.load(fh)
    return {"budget_usd": BUDGET_USD, "runs": []}


@app.local_entrypoint()
def main(lines: str = "work/voice/lines.json", out: str = "work/voice/chatterbox", ref: str = "", refs: str = "",
         note: str = "tts sample"):
    with open(lines) as fh:
        items = json.load(fh)[:MAX_LINES]
    led = _ledger()
    month = dt.date.today().strftime("%Y-%m")
    spent = sum(r["cost_usd"] for r in led["runs"] if r["date"].startswith(month))
    worst = (150 + 40 * len(items)) * GPU_PRICE["L4"] * OVERHEAD   # up to 4 takes per line
    print(f"[tts] bulan {month}: tercatat ${spent:.2f} / ${BUDGET_USD:.2f}; estimasi terburuk run ini ${worst:.2f}")
    if spent + worst > BUDGET_USD:
        raise SystemExit("[tts] STOP: budget bulanan akan terlewati. Tidak dijalankan. (ubah hanya atas izin user)")
    ref_bytes = b""
    if ref:
        with open(ref, "rb") as fh:
            ref_bytes = fh.read()
    ref_map = {}
    for kv in filter(None, refs.split(",")):
        k, v = kv.split("=", 1)
        with open(v, "rb") as fh:
            ref_map[k] = fh.read()
    t0 = time.time()
    res = speak.remote(items, ref_bytes, ref_map)
    wall = time.time() - t0
    os.makedirs(out, exist_ok=True)
    for i, w in enumerate(res["wavs"]):
        with open(os.path.join(out, f"line_{i:02d}.wav"), "wb") as fh:
            fh.write(w)
    with open(os.path.join(out, "qa.json"), "w") as fh:
        json.dump(res["qa"], fh, indent=1)
    bad = [q for q in res["qa"] if q["score"] < 0.85]
    for q in res["qa"]:
        print(f"[tts] QA {q['score']:.2f} x{q['takes']} '{q['text'][:40]}' -> '{q['heard'][:40]}'")
    print(f"[tts] QA: {len(res['qa']) - len(bad)}/{len(res['qa'])} kalimat lolos (>=0.85)")
    cost = res["secs"] * GPU_PRICE["L4"] * OVERHEAD
    led["runs"].append(dict(date=dt.date.today().isoformat(), note=note, gpu="L4", engine="chatterbox-tts",
                            lines=len(items), gpu_seconds=round(res["secs"], 1), wall_seconds=round(wall, 1),
                            cost_usd=round(cost, 4)))
    with open(LEDGER, "w") as fh:
        json.dump(led, fh, indent=1)
    print(f"[tts] DONE {len(items)} kalimat: GPU {res['secs']:.0f}s, wall {wall:.0f}s, ≈${cost:.3f}; "
          f"chatterbox-tts {res['version']} license={res['license']} -> {out}")
