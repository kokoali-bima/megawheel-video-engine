"""MegaWheel Arena theme songs with YuE v1 (HKUST / M-A-P, Apache-2.0 weights; NOT YuE2 = CC BY-NC) on a Modal L40S: lyrics -> full song, rich backing.
Credit required in the video description: "Music generated with YuE by HKUST/M-A-P".
Every take is returned (a human picks); faster-whisper lyric score is printed as a hint.
Same monthly budget guard + modal_usage.json ledger as modal_tts.py / modal_song.py.

Run on VM 99.3 (cd /root/video-engine):
  venv-modal/bin/modal run generators/voice/modal_yue.py --song branding/music/yue_intro.json --out branding/music
  yue_intro.json = {"name": "...", "genre": "tags", "lyrics": "[verse]\\n...\\n\\n[chorus]\\n...", "takes": 3, "seed": 42}
"""
import datetime as dt
import json
import os
import time

import modal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEDGER = os.path.join(ROOT, "modal_usage.json")
BUDGET_USD = 29.0
GPU_PRICE = {"L40S": 0.000542}
OVERHEAD = 1.15
S1, S2 = "m-a-p/YuE-s1-7B-anneal-en-cot", "m-a-p/YuE-s2-1B-general"

app = modal.App("megawheel-yue")


def _download():
    from faster_whisper import WhisperModel
    from huggingface_hub import snapshot_download
    snapshot_download("m-a-p/xcodec_mini_infer", local_dir="/YuE/inference/xcodec_mini_infer")
    snapshot_download(S1)
    snapshot_download(S2)
    WhisperModel("base.en", device="cpu", compute_type="int8")


image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "git-lfs", "ffmpeg", "libsndfile1")
    # YuE v1 (Apache-2.0 weights). The repo's main branch is now YuE2 (CC BY-NC weights): check out the last v1 commit.
    .run_commands("git clone https://github.com/multimodal-art-projection/YuE.git /YuE",
                  "cd /YuE && git checkout $(git rev-list -n 1 HEAD -- inference/infer.py)~1",
                  # no flash-attn wheel in this image: fall back to PyTorch SDPA attention
                  "sed -i 's/flash_attention_2/sdpa/g' /YuE/inference/infer.py")
    .pip_install("torch==2.5.1", "torchaudio==2.5.1")
    .run_commands("pip install -r /YuE/requirements.txt")
    .pip_install("faster-whisper", "huggingface_hub", "soundfile")
    .run_function(_download)
)


def _score(want, got):
    import difflib
    import re
    norm = lambda s: " ".join(re.sub(r"[^a-z ]", " ", s.lower()).split())
    return difflib.SequenceMatcher(None, norm(re.sub(r"\[[^\]]*\]", " ", want)), norm(got)).ratio()


def _finish(path, sg):
    """Fade in / out, peak-normalise -> 16-bit WAV bytes."""
    import io
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(path, always_2d=True)
    fi, fo = int(sg.get("fade_in", 0) * sr), int(sg.get("fade_out", 0) * sr)
    if fi:
        x[:fi] *= np.linspace(0, 1, fi)[:, None]
    if fo:
        x[-fo:] *= (np.linspace(1, 0, fo) ** 1.5)[:, None]
    x = x / max(1e-9, np.max(np.abs(x))) * 0.95
    buf = io.BytesIO()
    sf.write(buf, x, sr, format="WAV", subtype="PCM_16")
    return buf.getvalue()


@app.function(image=image, gpu="L40S", timeout=3600)
def sing(sg: dict) -> dict:
    import glob
    import subprocess
    from faster_whisper import WhisperModel
    t0 = time.time()
    with open("/tmp/genre.txt", "w") as fh:
        fh.write(sg["genre"])
    with open("/tmp/lyrics.txt", "w") as fh:
        fh.write(sg["lyrics"])
    nseg = sg["lyrics"].count("[")
    asr = WhisperModel("base.en", device="cpu", compute_type="int8")
    out, log = {}, []
    for take in range(int(sg.get("takes", 3))):
        od = f"/tmp/out{take}"
        cmd = ["python", "infer.py", "--cuda_idx", "0", "--stage1_model", S1, "--stage2_model", S2,
               "--genre_txt", "/tmp/genre.txt", "--lyrics_txt", "/tmp/lyrics.txt", "--run_n_segments", str(nseg),
               "--stage2_batch_size", "4", "--output_dir", od, "--max_new_tokens", "3000",
               "--repetition_penalty", "1.1", "--seed", str(int(sg.get("seed", 42)) + take * 11)]
        r = subprocess.run(cmd, cwd="/YuE/inference", capture_output=True, text=True)
        files = [f for f in glob.glob(f"{od}/**/*", recursive=True) if f.endswith((".mp3", ".wav"))]
        mixed = [f for f in files if "mix" in os.path.basename(f).lower()] or files
        if r.returncode or not mixed:
            log.append(f"take {take}: rc={r.returncode} {r.stderr[-800:]}")
            continue
        path = max(mixed, key=os.path.getsize)
        heard = " ".join(s.text for s in asr.transcribe(path, language="en", beam_size=3)[0])
        name = sg["name"] if take == 0 else f"{sg['name']}_alt{take}"
        out[name] = dict(wav=_finish(path, sg), score=round(_score(sg["lyrics"], heard), 2), heard=heard[:300])
        log.append(f"take {take}: ok {os.path.basename(path)} ({time.time() - t0:.0f}s)")
    return dict(songs=out, log=log, secs=time.time() - t0)


def _ledger():
    if os.path.exists(LEDGER):
        with open(LEDGER) as fh:
            return json.load(fh)
    return {"budget_usd": BUDGET_USD, "runs": []}


@app.local_entrypoint()
def main(song: str = "branding/music/yue_intro.json", out: str = "branding/music", note: str = "YuE theme song"):
    with open(song) as fh:
        sg = json.load(fh)
    led = _ledger()
    month = dt.date.today().strftime("%Y-%m")
    spent = sum(r["cost_usd"] for r in led["runs"] if r["date"].startswith(month))
    worst = 3600 * GPU_PRICE["L40S"] * OVERHEAD
    print(f"[yue] bulan {month}: tercatat ${spent:.2f} / ${BUDGET_USD:.2f}; estimasi terburuk run ini ${worst:.2f}")
    if spent + worst > BUDGET_USD:
        raise SystemExit("[yue] STOP: budget bulanan akan terlewati. Tidak dijalankan.")
    t0 = time.time()
    res = sing.remote(sg)
    for line in res["log"]:
        print("[yue]", line)
    os.makedirs(out, exist_ok=True)
    for name, r in res["songs"].items():
        with open(os.path.join(out, f"{name}.wav"), "wb") as fh:
            fh.write(r["wav"])
        print(f"[yue] {name}: lirik terdengar {r['score']:.2f} -> {out}/{name}.wav")
        print(f"[yue]   heard: {r['heard'][:160]}")
    cost = res["secs"] * GPU_PRICE["L40S"] * OVERHEAD
    led["runs"].append(dict(date=dt.date.today().isoformat(), note=note, gpu="L40S", engine="YuE-s1-7B+s2-1B",
                            songs=len(res["songs"]), gpu_seconds=round(res["secs"], 1),
                            wall_seconds=round(time.time() - t0, 1), cost_usd=round(cost, 4)))
    with open(LEDGER, "w") as fh:
        json.dump(led, fh, indent=1)
    print(f"[yue] DONE {len(res['songs'])} take: GPU {res['secs']:.0f}s ≈${cost:.3f}")
