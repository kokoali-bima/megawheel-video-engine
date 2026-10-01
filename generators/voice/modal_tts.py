"""Expressive announcer voice on Modal GPUs (Chatterbox TTS, open source), with the same monthly budget guard as
generators/blender3d/modal_render.py. Test / sample generator (user 2026-10-01: "tidak adakah suara yang bisa kita
build pakai mesin modal.com kita?").

Run on VM 99.3 (cd /root/video-engine):
  venv-modal/bin/modal run generators/voice/modal_tts.py --lines work/voice/lines.json --out work/voice/chatterbox
  lines.json = [{"text": "...", "exaggeration": 0.9, "cfg": 0.4, "ref": true}, ...]   (ref = use --ref voice prompt)
  --ref work/voice/ref.wav   synthetic reference voice for the speaker (never a real person's voice)
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
    ChatterboxTTS.from_pretrained(device="cpu")                # bake the weights into the image (no GPU time)


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git")
    .pip_install("chatterbox-tts")
    .run_function(_download)
)


@app.function(image=image, gpu="L4", timeout=900)
def speak(items: list, ref: bytes = b"") -> dict:
    import importlib.metadata as md

    import torchaudio
    from chatterbox.tts import ChatterboxTTS
    t0 = time.time()
    model = ChatterboxTTS.from_pretrained(device="cuda")
    ref_path = None
    if ref:
        ref_path = "/tmp/ref.wav"
        with open(ref_path, "wb") as fh:
            fh.write(ref)
    wavs = []
    for it in items:
        wav = model.generate(it["text"], audio_prompt_path=ref_path if it.get("ref") else None,
                             exaggeration=float(it.get("exaggeration", 0.5)), cfg_weight=float(it.get("cfg", 0.5)))
        buf = io.BytesIO()
        torchaudio.save(buf, wav.cpu(), model.sr, format="wav")
        wavs.append(buf.getvalue())
    meta = md.metadata("chatterbox-tts")
    return dict(wavs=wavs, secs=time.time() - t0, license=meta.get("License") or meta.get("License-Expression") or "?",
                version=meta.get("Version"))


def _ledger():
    if os.path.exists(LEDGER):
        with open(LEDGER) as fh:
            return json.load(fh)
    return {"budget_usd": BUDGET_USD, "runs": []}


@app.local_entrypoint()
def main(lines: str = "work/voice/lines.json", out: str = "work/voice/chatterbox", ref: str = "",
         note: str = "tts sample"):
    with open(lines) as fh:
        items = json.load(fh)[:MAX_LINES]
    led = _ledger()
    month = dt.date.today().strftime("%Y-%m")
    spent = sum(r["cost_usd"] for r in led["runs"] if r["date"].startswith(month))
    worst = (120 + 12 * len(items)) * GPU_PRICE["L4"] * OVERHEAD
    print(f"[tts] bulan {month}: tercatat ${spent:.2f} / ${BUDGET_USD:.2f}; estimasi terburuk run ini ${worst:.2f}")
    if spent + worst > BUDGET_USD:
        raise SystemExit("[tts] STOP: budget bulanan akan terlewati. Tidak dijalankan. (ubah hanya atas izin user)")
    ref_bytes = b""
    if ref:
        with open(ref, "rb") as fh:
            ref_bytes = fh.read()
    t0 = time.time()
    res = speak.remote(items, ref_bytes)
    wall = time.time() - t0
    os.makedirs(out, exist_ok=True)
    for i, w in enumerate(res["wavs"]):
        with open(os.path.join(out, f"line_{i:02d}.wav"), "wb") as fh:
            fh.write(w)
    cost = res["secs"] * GPU_PRICE["L4"] * OVERHEAD
    led["runs"].append(dict(date=dt.date.today().isoformat(), note=note, gpu="L4", engine="chatterbox-tts",
                            lines=len(items), gpu_seconds=round(res["secs"], 1), wall_seconds=round(wall, 1),
                            cost_usd=round(cost, 4)))
    with open(LEDGER, "w") as fh:
        json.dump(led, fh, indent=1)
    print(f"[tts] DONE {len(items)} kalimat: GPU {res['secs']:.0f}s, wall {wall:.0f}s, ≈${cost:.3f}; "
          f"chatterbox-tts {res['version']} license={res['license']} -> {out}")
