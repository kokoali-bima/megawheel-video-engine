"""MegaWheel Arena theme songs on Modal GPUs: ACE-Step (open source, Apache-2.0) text+lyrics -> song with vocals.
Several takes per song; the take whose sung lyrics speech recognition hears best is kept (faster-whisper QA).
Then optional remix (Demucs, MIT): split vocals / music and rebalance ("mix"), plus fade in / out.
Same monthly budget guard + modal_usage.json ledger as modal_tts.py.

Run on VM 99.3 (cd /root/video-engine):
  venv-modal/bin/modal run generators/voice/modal_song.py --songs branding/music/songs.json --out branding/music
  songs.json = [{"name": "intro_lets_go", "duration": 28, "tags": "...", "lyrics": "[verse]...", "takes": 4}, ...]
"""
import datetime as dt
import json
import os
import time

import modal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEDGER = os.path.join(ROOT, "modal_usage.json")
BUDGET_USD = 29.0
GPU_PRICE = {"L4": 0.000222}
OVERHEAD = 1.15
CKPT = "/root/ace_ckpt"

app = modal.App("megawheel-song")


def _download():
    from faster_whisper import WhisperModel
    from huggingface_hub import snapshot_download
    snapshot_download("ACE-Step/ACE-Step-v1-3.5B", local_dir=CKPT)
    WhisperModel("base.en", device="cpu", compute_type="int8")
    from demucs.pretrained import get_model
    get_model("htdemucs")


image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "git", "libsndfile1")
    # torchaudio >= 2.9 saves through torchcodec (not installed) -> pin the pair ACE-Step was built on
    .pip_install("torch==2.5.1", "torchaudio==2.5.1")
    .pip_install("git+https://github.com/ace-step/ACE-Step.git", "faster-whisper", "huggingface_hub",
                 "demucs==4.0.1", "soundfile", "torch==2.5.1", "torchaudio==2.5.1")
    .run_function(_download)
)


def _finish(path, sg):
    """Rebalance vocals vs music (Demucs two-stem split), fade in / out, peak-normalise, 16-bit WAV bytes."""
    import io
    import subprocess
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(path, always_2d=True)
    mix = sg.get("mix")
    if mix:
        subprocess.run(["python", "-m", "demucs", "--two-stems", "vocals", "-n", "htdemucs", "-o", "/tmp/sep", path],
                       check=True, capture_output=True)
        stem = os.path.join("/tmp/sep", "htdemucs", os.path.splitext(os.path.basename(path))[0])
        v, sr = sf.read(os.path.join(stem, "vocals.wav"), always_2d=True)
        m, _ = sf.read(os.path.join(stem, "no_vocals.wav"), always_2d=True)
        n = min(len(v), len(m))
        x = v[:n] * mix.get("vocals", 1.0) + m[:n] * mix.get("music", 1.0)
    if sg.get("pitch"):                                            # whole song (voice + band stay in key)
        r = 2 ** (sg["pitch"] / 12)
        sf.write("/tmp/pin.wav", x, sr, subtype="PCM_16")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "/tmp/pin.wav", "-af",
                        f"asetrate={int(sr * r)},aresample={sr},atempo={1 / r:.6f}", "/tmp/pout.wav"], check=True)
        x, sr = sf.read("/tmp/pout.wav", always_2d=True)
    fi, fo = int(sg.get("fade_in", 0) * sr), int(sg.get("fade_out", 0) * sr)
    if fi:
        x[:fi] *= np.linspace(0, 1, fi)[:, None]
    if fo:
        x[-fo:] *= (np.linspace(1, 0, fo) ** 1.5)[:, None]
    x = x / max(1e-9, np.max(np.abs(x))) * 0.95
    buf = io.BytesIO()
    sf.write(buf, x, sr, format="WAV", subtype="PCM_16")
    return buf.getvalue()


def _ending(path):
    """1.0 = the song ends by itself (quiet last second), 0.0 = cut off at full volume."""
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(path, always_2d=True)
    m = np.abs(x).mean(axis=1)
    body = np.median(m[: max(1, len(m) - 3 * sr)]) + 1e-9
    return float(np.clip(1.0 - (m[-sr:].mean() / body - 0.15) / 0.6, 0.0, 1.0))


def _score(want, got):
    import difflib
    import re
    norm = lambda s: " ".join(re.sub(r"[^a-z ]", " ", s.lower()).split())
    lyr = norm(re.sub(r"\[[^\]]*\]", " ", want))
    return difflib.SequenceMatcher(None, lyr, norm(got)).ratio()


@app.function(image=image, gpu="L4", timeout=1800)
def sing(songs: list) -> dict:
    from acestep.pipeline_ace_step import ACEStepPipeline
    from faster_whisper import WhisperModel
    t0 = time.time()
    pipe = ACEStepPipeline(checkpoint_dir=CKPT, dtype="bfloat16", torch_compile=False, cpu_offload=False,
                           overlapped_decode=False)
    asr = WhisperModel("base.en", device="cpu", compute_type="int8")
    out = {}
    for sg in songs:
        takes = []
        for take in range(int(sg.get("takes", 3))):
            path = f"/tmp/{sg['name']}_{take}.wav"
            seed = int(sg.get("seed", 100)) + take * 17
            pipe(audio_duration=float(sg["duration"]), prompt=sg["tags"], lyrics=sg["lyrics"], infer_step=60,
                 guidance_scale=15.0, scheduler_type="euler", cfg_type="apg", omega_scale=10.0,
                 manual_seeds=str(seed), guidance_interval=0.5, guidance_interval_decay=0.0, min_guidance_scale=3.0,
                 use_erg_tag=True, use_erg_lyric=True, use_erg_diffusion=True, oss_steps="",
                 guidance_scale_text=0.0, guidance_scale_lyric=0.0, save_path=path)
            if not os.path.exists(path):                          # some versions append their own suffix
                cands = sorted(f for f in os.listdir("/tmp") if f.startswith(f"{sg['name']}_{take}"))
                path = os.path.join("/tmp", cands[-1]) if cands else path
            heard = " ".join(s.text for s in asr.transcribe(path, language="en", beam_size=3)[0])
            sc = _score(sg["lyrics"], heard)
            end = _ending(path)
            takes.append((sc + 0.25 * end, path, heard + f" [ending {end:.2f}]", take, seed))
        takes.sort(key=lambda x: -x[0])
        for rank, (sc, path, heard, take, seed) in enumerate(takes[:int(sg.get("keep", 1))]):
            name = sg["name"] if rank == 0 else f"{sg['name']}_alt{rank}"   # "keep": top-N takes for a human pick
            out[name] = dict(wav=_finish(path, sg), score=round(sc, 2), heard=heard[:300], take=take, seed=seed)
    return dict(songs=out, secs=time.time() - t0)


def _ledger():
    if os.path.exists(LEDGER):
        with open(LEDGER) as fh:
            return json.load(fh)
    return {"budget_usd": BUDGET_USD, "runs": []}


@app.local_entrypoint()
def main(songs: str = "branding/music/songs.json", out: str = "branding/music", note: str = "theme songs"):
    with open(songs) as fh:
        items = json.load(fh)
    led = _ledger()
    month = dt.date.today().strftime("%Y-%m")
    spent = sum(r["cost_usd"] for r in led["runs"] if r["date"].startswith(month))
    worst = (300 + 90 * sum(int(s.get("takes", 3)) for s in items)) * GPU_PRICE["L4"] * OVERHEAD
    print(f"[song] bulan {month}: tercatat ${spent:.2f} / ${BUDGET_USD:.2f}; estimasi terburuk run ini ${worst:.2f}")
    if spent + worst > BUDGET_USD:
        raise SystemExit("[song] STOP: budget bulanan akan terlewati. Tidak dijalankan.")
    t0 = time.time()
    res = sing.remote(items)
    os.makedirs(out, exist_ok=True)
    for name, r in res["songs"].items():
        with open(os.path.join(out, f"{name}.wav"), "wb") as fh:
            fh.write(r["wav"])
        print(f"[song] {name}: lirik terdengar {r['score']:.2f} (take {r['take']}, seed {r['seed']}) -> {out}/{name}.wav")
        print(f"[song]   heard: {r['heard'][:160]}")
    cost = res["secs"] * GPU_PRICE["L4"] * OVERHEAD
    led["runs"].append(dict(date=dt.date.today().isoformat(), note=note, gpu="L4", engine="ace-step-v1-3.5B",
                            songs=len(items), gpu_seconds=round(res["secs"], 1), wall_seconds=round(time.time() - t0, 1),
                            cost_usd=round(cost, 4)))
    with open(LEDGER, "w") as fh:
        json.dump(led, fh, indent=1)
    print(f"[song] DONE {len(items)} lagu: GPU {res['secs']:.0f}s ≈${cost:.3f}")
