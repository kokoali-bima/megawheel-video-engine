"""LAB (Ep.2 pilot, user 2026-10-05: "suara nyanyinya sesuaikan dengan suara aslinya"): make a sung take sound
like the character's REAL voice.
  ACE-Step song (any singer) -> Demucs (MIT) two-stem split -> Seed-VC singing mode (f0-conditioned, keeps the
  melody; GPL-3.0 tool run as a separate program, the audio output is ours) with the character's Chatterbox ref
  -> remix the converted vocal over the original backing. faster-whisper word times for the cut point.
Run on VM 99.3 (cd /root/video-engine):
  venv-modal/bin/modal run lab/voice_sing/modal_singvc.py --src a.wav,b.wav --ref branding/voice/characters/tilly.wav \
      --out branding/music --shifts 0,2
Writes <name>_vc<shift>.wav (mix), <name>_vc<shift>_vox.wav (vocal only), <name>_vc<shift>.json (words)."""
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
SVC = "/opt/seed-vc"

app = modal.App("megawheel-singvc")
image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("ffmpeg", "git", "libsndfile1")
    .pip_install("torch==2.4.0", "torchaudio==2.4.0")
    .run_commands(f"git clone --depth 1 https://github.com/Plachtaa/seed-vc {SVC}")
    .pip_install("scipy==1.13.1", "librosa==0.10.2", "huggingface-hub>=0.28.1", "munch==4.0.0", "einops==0.8.0",
                 "descript-audio-codec==1.0.0", "pydub==0.25.1", "resemblyzer", "jiwer==3.0.3", "transformers==4.46.3",
                 "soundfile==0.12.1", "modelscope==1.18.1", "funasr==1.1.5", "numpy==1.26.4", "hydra-core==1.3.2",
                 "pyyaml", "python-dotenv", "accelerate", "demucs==4.0.1", "faster-whisper",
                 "torch==2.4.0", "torchaudio==2.4.0")
    # modelscope/funasr pull an old protobuf; the Modal runtime itself needs >= 4.25 (container crash-loop otherwise)
    .pip_install("protobuf>=4.25,<6")
)


def _wav16(x, sr):
    import io
    import numpy as np
    import soundfile as sf
    x = x / max(1e-6, float(np.abs(x).max())) * 0.89
    buf = io.BytesIO()
    sf.write(buf, x, sr, subtype="PCM_16", format="WAV")
    return buf.getvalue()


@app.function(image=image, gpu="L4", timeout=1800)
def convert(songs: dict, ref: bytes, shifts: list, steps: int = 40, vox_gain: float = 1.0, bed_gain: float = 0.75) -> dict:
    import glob
    import subprocess
    import librosa
    import numpy as np
    import soundfile as sf
    from faster_whisper import WhisperModel
    t0 = time.time()
    with open("/tmp/ref.wav", "wb") as fh:
        fh.write(ref)
    asr = WhisperModel("base.en", device="cpu", compute_type="int8")
    out = {}
    for name, data in songs.items():
        src = f"/tmp/{name}.wav"
        with open(src, "wb") as fh:
            fh.write(data)
        subprocess.run(["python", "-m", "demucs", "--two-stems", "vocals", "-n", "htdemucs", "-o", "/tmp/sep", src],
                       check=True, capture_output=True)
        stem = f"/tmp/sep/htdemucs/{name}"
        bed, sr = sf.read(f"{stem}/no_vocals.wav", always_2d=True)
        for sh in shifts:
            od = f"/tmp/vc_{name}_{sh}"
            r = subprocess.run(["python", "inference.py", "--source", f"{stem}/vocals.wav", "--target", "/tmp/ref.wav",
                                "--output", od, "--diffusion-steps", str(steps), "--f0-condition", "True",
                                "--auto-f0-adjust", "False", "--semi-tone-shift", str(sh), "--fp16", "True"],
                               cwd=SVC, capture_output=True, text=True)
            got = sorted(glob.glob(f"{od}/*.wav"))
            if not got:
                out[f"{name}_vc{sh}"] = dict(error=(r.stdout[-1500:] + r.stderr[-2500:]))
                continue
            v, vsr = sf.read(got[-1], always_2d=True)
            v = librosa.resample(v.mean(axis=1), orig_sr=vsr, target_sr=sr)
            n = min(len(v), len(bed))
            mix = bed[:n] * bed_gain + (v[:n] * vox_gain)[:, None]
            path = f"/tmp/mix_{name}_{sh}.wav"
            sf.write(path, mix, sr)
            segs = asr.transcribe(path, language="en", beam_size=3, word_timestamps=True)[0]
            words = [[w.word.strip(), round(w.start, 2), round(w.end, 2)] for s in segs for w in (s.words or [])]
            out[f"{name}_vc{sh}"] = dict(wav=_wav16(mix, sr), vox=_wav16(v[:n], sr), words=words)
    return dict(out=out, secs=time.time() - t0)


def _ledger():
    if os.path.exists(LEDGER):
        with open(LEDGER) as fh:
            return json.load(fh)
    return {"budget_usd": BUDGET_USD, "runs": []}


@app.local_entrypoint()
def main(src: str, ref: str, out: str = "branding/music", shifts: str = "0", steps: int = 40, note: str = "sing vc"):
    led = _ledger()
    month = dt.date.today().strftime("%Y-%m")
    spent = sum(r["cost_usd"] for r in led["runs"] if r["date"].startswith(month))
    files = [s for s in src.split(",") if s]
    sh = [int(x) for x in shifts.split(",")]
    worst = (300 + 120 * len(files) * len(sh)) * GPU_PRICE["L4"] * OVERHEAD
    print(f"[singvc] bulan {month}: tercatat ${spent:.2f} / ${BUDGET_USD:.2f}; estimasi terburuk ${worst:.2f}")
    if spent + worst > BUDGET_USD:
        raise SystemExit("[singvc] STOP: budget bulanan akan terlewati.")
    songs = {}
    for f in files:
        with open(f, "rb") as fh:
            songs[os.path.splitext(os.path.basename(f))[0]] = fh.read()
    with open(ref, "rb") as fh:
        refb = fh.read()
    t0 = time.time()
    res = convert.remote(songs, refb, sh, steps)
    os.makedirs(out, exist_ok=True)
    for name, r in res["out"].items():
        if "error" in r:
            print(f"[singvc] {name}: GAGAL\n{r['error']}")
            continue
        for suf, key in (("", "wav"), ("_vox", "vox")):
            with open(os.path.join(out, f"{name}{suf}.wav"), "wb") as fh:
                fh.write(r[key])
        with open(os.path.join(out, f"{name}.json"), "w") as fh:
            json.dump(r["words"], fh)
        print(f"[singvc] {name} -> {out}/{name}.wav | " + " ".join(f"{w}@{a}" for w, a, b in r["words"]))
    cost = res["secs"] * GPU_PRICE["L4"] * OVERHEAD
    led["runs"].append(dict(date=dt.date.today().isoformat(), note=note, gpu="L4", engine="demucs+seed-vc",
                            gpu_seconds=round(res["secs"], 1), wall_seconds=round(time.time() - t0, 1),
                            cost_usd=round(cost, 4)))
    with open(LEDGER, "w") as fh:
        json.dump(led, fh, indent=1)
    print(f"[singvc] DONE GPU {res['secs']:.0f}s ≈${cost:.3f}")
