"""Render a Blender scene on Modal GPUs (Cycles + OptiX), chunked in parallel, with a hard monthly budget guard.

Run on VM 99.3 (cd /root/video-engine):
  venv-modal/bin/modal run generators/blender3d/modal_render.py --frames 90 --chunks 3
  options: --engine CYCLES --samples 16 --gpu L4 --out work/blender3d/modal
Every run is logged in modal_usage.json (tracked in git). The run is REFUSED if this month's logged spend
+ the worst-case estimate of the new run would pass BUDGET_USD (kept below the $30/month free credit).
"""
import datetime as dt
import json
import os
import subprocess
import time

import modal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GLB_LOCAL = os.path.join(ROOT, "assets", "kenney_car_kit", "Models", "GLB format")
SCENE_LOCAL = os.path.join(ROOT, "generators", "blender3d", "bench_scene.py")
LEDGER = os.path.join(ROOT, "modal_usage.json")
BUDGET_USD = 25.0                       # monthly cap for our own runs (free credit is $30)
MAX_FRAMES, MAX_CHUNKS = 1800, 8
GPU_PRICE = {"T4": 0.000164, "L4": 0.000222, "A10": 0.000306, "L40S": 0.000542}   # $/s (modal.com/pricing)
OVERHEAD = 1.15                         # CPU + memory of the container on top of the GPU price
BLENDER_V = "5.2.2"

app = modal.App("megawheel-blender")
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("curl", "xz-utils", "ffmpeg", "libx11-6", "libxi6", "libxxf86vm1", "libxfixes3", "libxrender1",
                 "libgl1", "libxkbcommon0", "libsm6", "libice6", "libegl1")
    .run_commands(
        f"curl -sSfL https://download.blender.org/release/Blender5.2/blender-{BLENDER_V}-linux-x64.tar.xz"
        " | tar -xJ -C /opt",
        f"ln -s /opt/blender-{BLENDER_V}-linux-x64/blender /usr/local/bin/blender")
    .env({"MW_GLB_DIR": "/root/glb"})
    .add_local_dir(GLB_LOCAL, "/root/glb")
    .add_local_file(SCENE_LOCAL, "/root/scene/bench_scene.py")
)


def _gpu():
    return os.environ.get("MW_GPU", "L4")


@app.function(image=image, gpu=_gpu(), timeout=1800, max_containers=MAX_CHUNKS)
def render_chunk(start: int, end: int, engine: str, samples: int, fps: int) -> dict:
    t0 = time.time()
    out = "/tmp/out"
    os.makedirs(out, exist_ok=True)
    cmd = ["blender", "-b", "-P", "/root/scene/bench_scene.py", "--", "--engine", engine, "--samples", str(samples),
           "--gpu", "--frame-start", str(start), "--frame-end", str(end), "--outdir", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    pngs = sorted(f for f in os.listdir(out) if f.endswith(".png"))
    if r.returncode != 0 or not pngs:
        raise RuntimeError(f"blender failed ({r.returncode}):\n{r.stdout[-2500:]}\n{r.stderr[-1500:]}")
    mp4 = "/tmp/chunk.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(fps), "-start_number", str(start),
                    "-i", f"{out}/frame_%04d.png", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", mp4],
                   check=True)
    with open(mp4, "rb") as fh:
        video = fh.read()
    with open(os.path.join(out, pngs[0]), "rb") as fh:
        still = fh.read()
    log = [ln for ln in r.stdout.splitlines() if "[bench]" in ln]
    return dict(start=start, end=end, mp4=video, png=still, secs=time.time() - t0, log=log)


def _ledger():
    if os.path.exists(LEDGER):
        with open(LEDGER) as fh:
            return json.load(fh)
    return {"budget_usd": BUDGET_USD, "runs": []}


@app.local_entrypoint()
def main(frames: int = 90, chunks: int = 3, engine: str = "CYCLES", samples: int = 16, fps: int = 30,
         gpu: str = "L4", out: str = "work/blender3d/modal", note: str = "benchmark"):
    frames, chunks = min(frames, MAX_FRAMES), max(1, min(chunks, MAX_CHUNKS))
    led = _ledger()
    month = dt.date.today().strftime("%Y-%m")
    spent = sum(r["cost_usd"] for r in led["runs"] if r["date"].startswith(month))
    worst = frames * 4.0 * GPU_PRICE.get(gpu, 0.0006) * OVERHEAD + chunks * 90 * GPU_PRICE.get(gpu, 0.0006)
    print(f"[modal] bulan {month}: tercatat ${spent:.2f} / ${BUDGET_USD:.2f}; estimasi terburuk run ini ${worst:.2f}")
    if spent + worst > BUDGET_USD:
        raise SystemExit("[modal] STOP: budget bulanan akan terlewati. Tidak dijalankan. (ubah hanya atas izin user)")
    per = -(-frames // chunks)
    ranges = [(s, min(frames, s + per - 1), engine, samples, fps) for s in range(1, frames + 1, per)]
    t0 = time.time()
    results = list(render_chunk.starmap(ranges))
    wall = time.time() - t0
    os.makedirs(out, exist_ok=True)
    lst = os.path.join(out, "chunks.txt")
    with open(lst, "w") as fl:
        for r in sorted(results, key=lambda r: r["start"]):
            p = os.path.join(out, f"chunk_{r['start']:04d}.mp4")
            with open(p, "wb") as fh:
                fh.write(r["mp4"])
            with open(os.path.join(out, f"still_{r['start']:04d}.png"), "wb") as fh:
                fh.write(r["png"])
            fl.write(f"file '{os.path.basename(p)}'\n")
            print(f"[modal] chunk {r['start']}-{r['end']}: {r['secs']:.0f}s  {' '.join(r['log'])}")
    final = os.path.join(out, "render.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    final], check=True)
    gpu_secs = sum(r["secs"] for r in results)
    cost = gpu_secs * GPU_PRICE.get(gpu, 0.0006) * OVERHEAD
    led["runs"].append(dict(date=dt.date.today().isoformat(), note=note, gpu=gpu, engine=engine, samples=samples,
                            frames=frames, chunks=chunks, gpu_seconds=round(gpu_secs, 1), wall_seconds=round(wall, 1),
                            cost_usd=round(cost, 4)))
    with open(LEDGER, "w") as fh:
        json.dump(led, fh, indent=1)
    print(f"[modal] DONE {frames} frame di {chunks} GPU {gpu}: wall {wall:.0f}s, GPU {gpu_secs:.0f}s, "
          f"≈${cost:.3f} ({gpu_secs / frames:.2f} GPU-s/frame termasuk startup) -> {final}")
