"""director3d step 3 — render motion.json on Modal GPUs (Cycles + OptiX), horizontal and/or vertical, in parallel.

Run on VM 99.3 (cd /root/video-engine):
  venv-modal/bin/modal run generators/director3d/modal_director.py --motion work/director3d/demo/motion.json \
      --aspect both --chunks 4 [--samples 16] [--note "demo race"]
Output: work/director3d/<name>/<aspect>.mp4 (+ one still per chunk). Budget guard: shared ledger modal_usage.json,
refuses a run if this month's spend + worst-case estimate would pass BUDGET_USD.
"""
import datetime as dt
import json
import os
import subprocess
import time

import modal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEDGER = os.path.join(ROOT, "modal_usage.json")
BUDGET_USD = 29.0                          # same cap as blender3d/modal_render.py (user, 2026-09-30)
GPU, GPU_PRICE, OVERHEAD = "L4", 0.000222, 1.15
MAX_CONTAINERS = 8
BLENDER_V = "5.2.2"

app = modal.App("megawheel-director3d")
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("curl", "xz-utils", "ffmpeg", "libx11-6", "libxi6", "libxxf86vm1", "libxfixes3", "libxrender1",
                 "libgl1", "libxkbcommon0", "libsm6", "libice6", "libegl1")
    .run_commands(
        f"curl -sSfL https://download.blender.org/release/Blender5.2/blender-{BLENDER_V}-linux-x64.tar.xz"
        " | tar -xJ -C /opt",
        f"ln -s /opt/blender-{BLENDER_V}-linux-x64/blender /usr/local/bin/blender")
    .add_local_file(os.path.join(ROOT, "cast", "characters.json"), "/root/mw/cast/characters.json")
    .add_local_file(os.path.join(ROOT, "generators", "blender3d", "cast3d.py"), "/root/mw/generators/blender3d/cast3d.py")
    .add_local_file(os.path.join(ROOT, "generators", "director3d", "blender_scene.py"),
                    "/root/mw/generators/director3d/blender_scene.py")
)


@app.function(image=image, gpu=GPU, timeout=2400, max_containers=MAX_CONTAINERS)
def render_chunk(motion_json: str, aspect: str, start: int, end: int, samples: int, fps: int) -> dict:
    t0 = time.time()
    with open("/tmp/motion.json", "w") as fh:
        fh.write(motion_json)
    out = "/tmp/out"
    os.makedirs(out, exist_ok=True)
    cmd = ["blender", "-b", "-P", "/root/mw/generators/director3d/blender_scene.py", "--", "--motion",
           "/tmp/motion.json", "--aspect", aspect, "--frame-start", str(start), "--frame-end", str(end),
           "--outdir", out, "--samples", str(samples), "--gpu"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    pngs = sorted(f for f in os.listdir(out) if f.endswith(".png"))
    if r.returncode != 0 or len(pngs) < end - start + 1:
        raise RuntimeError(f"blender failed ({r.returncode}, {len(pngs)} png):\n{r.stdout[-2500:]}\n{r.stderr[-1500:]}")
    mp4 = "/tmp/chunk.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(fps), "-start_number", str(start),
                    "-i", f"{out}/frame_%04d.png", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", mp4],
                   check=True)
    with open(mp4, "rb") as fh:
        video = fh.read()
    with open(os.path.join(out, pngs[len(pngs) // 2]), "rb") as fh:
        still = fh.read()
    log = [ln for ln in r.stdout.splitlines() if "[scene]" in ln]
    return dict(aspect=aspect, start=start, end=end, mp4=video, png=still, secs=time.time() - t0, log=log)


@app.local_entrypoint()
def main(motion: str, aspect: str = "both", chunks: int = 4, samples: int = 16, note: str = "director3d"):
    with open(motion) as fh:
        mj = fh.read()
    m = json.loads(mj)
    frames, fps = m["frames"], m["fps"]
    aspects = ["horizontal", "vertical"] if aspect == "both" else [aspect]
    chunks = max(1, min(chunks, MAX_CONTAINERS // len(aspects)))
    total = frames * len(aspects)
    led = json.load(open(LEDGER)) if os.path.exists(LEDGER) else {"budget_usd": BUDGET_USD, "runs": []}
    month = dt.date.today().strftime("%Y-%m")
    spent = sum(r["cost_usd"] for r in led["runs"] if r["date"].startswith(month))
    worst = total * 2.5 * GPU_PRICE * OVERHEAD + chunks * len(aspects) * 120 * GPU_PRICE
    print(f"[modal] bulan {month}: tercatat ${spent:.2f} / ${BUDGET_USD:.2f}; estimasi terburuk run ini ${worst:.2f}")
    if spent + worst > BUDGET_USD:
        raise SystemExit("[modal] STOP: budget bulanan akan terlewati. Tidak dijalankan.")
    per = -(-frames // chunks)
    jobs = [(mj, asp, s, min(frames, s + per - 1), samples, fps) for asp in aspects for s in range(1, frames + 1, per)]
    t0 = time.time()
    results = list(render_chunk.starmap(jobs))
    wall = time.time() - t0
    out = os.path.join(os.path.dirname(os.path.abspath(motion)))
    for asp in aspects:
        rs = sorted((r for r in results if r["aspect"] == asp), key=lambda r: r["start"])
        lst = os.path.join(out, f"{asp}_chunks.txt")
        with open(lst, "w") as fl:
            for r in rs:
                p = os.path.join(out, f"{asp}_{r['start']:04d}.mp4")
                open(p, "wb").write(r["mp4"])
                open(os.path.join(out, f"{asp}_still_{r['start']:04d}.png"), "wb").write(r["png"])
                fl.write(f"file '{os.path.basename(p)}'\n")
                print(f"[modal] {asp} {r['start']}-{r['end']}: {r['secs']:.0f}s {' '.join(r['log'])}")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                        os.path.join(out, f"{asp}.mp4")], check=True)
    gpu_secs = sum(r["secs"] for r in results)
    cost = gpu_secs * GPU_PRICE * OVERHEAD
    led["runs"].append(dict(date=dt.date.today().isoformat(), note=note, gpu=GPU, engine="CYCLES", samples=samples,
                            frames=total, chunks=len(jobs), gpu_seconds=round(gpu_secs, 1), wall_seconds=round(wall, 1),
                            cost_usd=round(cost, 4)))
    with open(LEDGER, "w") as fh:
        json.dump(led, fh, indent=1)
    print(f"[modal] DONE {total} frame ({'+'.join(aspects)}) di {len(jobs)} GPU {GPU}: wall {wall:.0f}s, "
          f"GPU {gpu_secs:.0f}s, ≈${cost:.3f} ({gpu_secs / total:.2f} GPU-s/frame) -> {out}")
