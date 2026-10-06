"""story3d on Modal (user 2026-10-06: "pakai modal.com agar lebih cepat dan lebih halus dengan GPU-nya; kalau tokohnya bisa
di render di modal, render juga"). One app, three steps, every scene / part in parallel:
  1. overlay  (CPU)  story25d characters + subtitles -> alpha overlay, audio, camera per frame   [export_overlay.py]
  2. world    (T4)   Godot world from the per-frame camera, in parts of 450 frames              [project/story3d.gd]
  3. compose  (CPU)  world + overlay + audio -> scene mp4 (-16 LUFS) + the QA sensors           [audit_story3d.py]
Intermediate files stay in the Modal volume "megawheel-story3d" (an overlay is ~100 MB per scene); only the final
mp4s and QA reports come back. Voices + lip-sync must be prepared on the VM first (prepare.py): the containers are
x86 and never fall back to a weaker voice / mouth (they stop instead).
The repo is mounted at /root/video-engine, exactly like the VM, so the engine code runs unchanged.
Run on VM 99.3 (cd /root/video-engine) through produce_story3d.py, or directly:
  venv-modal/bin/modal run generators/story3d/modal_story3d.py --episode S01E02_who_is_kraggor --scenes 2 --out work/story3d
"""
import datetime as dt
import json
import os
import subprocess
import time

import modal

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
REMOTE = "/root/video-engine"
LEDGER = os.path.join(ROOT, "modal_usage.json")
BUDGET_USD = 29.0
CPU_PRICE, MEM_PRICE, T4_PRICE = 0.0000131, 0.00000222, 0.000164     # $/vCPU-s, $/GiB-s, $/GPU-s
OVERHEAD = 1.15
GODOT_URL = "https://github.com/godotengine/godot/releases/download/4.4.1-stable/Godot_v4.4.1-stable_linux.x86_64.zip"
PART = 450
FONT = "/root/.fonts/LuckiestGuy-Regular.ttf"

app = modal.App("megawheel-story3d")
vol = modal.Volume.from_name("megawheel-story3d", create_if_missing=True)


def _mounts(img):
    """Only what a render reads, mounted (not baked) so every run sees the current code / caches."""
    for sub in ("generators", "cast", "branding/music", "branding/voice/characters", "branding/infrasoft",
                "work/voice/cache", "work/voice/visemes", "stories"):
        if os.path.isdir(os.path.join(ROOT, sub)):
            img = img.add_local_dir(os.path.join(ROOT, sub), f"{REMOTE}/{sub}",
                                    ignore=["**/__pycache__/**", "**/*.mp4", "**/*.mov"])
    return img


cpu_img = _mounts(
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("ffmpeg", "libcairo2-dev", "pkg-config", "gcc", "fontconfig", "wget")
    .pip_install("pycairo>=1.27", "numpy>=2.2,<3", "pymunk>=7", "pillow", "edge-tts")
    .add_local_file(FONT, "/root/.fonts/LuckiestGuy-Regular.ttf", copy=True)   # the aired caption / subtitle font
    .run_commands("fc-cache -f")
)
gpu_img = _mounts(
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("xvfb", "xauth", "wget", "unzip", "ffmpeg", "libgl1", "libgl1-mesa-dri", "libegl1", "libgles2",
                 "libvulkan1", "mesa-vulkan-drivers", "libxcursor1", "libxinerama1", "libxrandr2", "libxi6",
                 "libfontconfig1", "libxkbcommon0", "libasound2", "libpulse0", "libudev1", "libdbus-1-3")
    .run_commands(f"wget -q {GODOT_URL} -O /tmp/g.zip && unzip -q /tmp/g.zip -d /opt/godot && "
                  "mv /opt/godot/Godot_v4.4.1-stable_linux.x86_64 /opt/godot/godot && chmod +x /opt/godot/godot")
)


@app.function(image=cpu_img, cpu=8, memory=8192, timeout=2400, volumes={"/vol": vol})
def overlay(job: str, episode: str, num: int, aspect: str) -> dict:
    t0 = time.time()
    out = f"/vol/{job}/s{num:02d}"
    os.makedirs(out, exist_ok=True)
    env = dict(os.environ, S3D_REMOTE="1", PYTHONUNBUFFERED="1")
    r = subprocess.run(["python", f"{REMOTE}/generators/story3d/export_overlay.py", "--episode", episode,
                        "--scene", str(num), "--aspect", aspect, "--out", out], capture_output=True, text=True, env=env)
    vol.commit()
    ok = r.returncode == 0 and os.path.exists(f"{out}/frames.json")
    n = len(json.load(open(f"{out}/frames.json"))["frames"]) if ok else 0
    return dict(num=num, ok=ok, frames=n, secs=time.time() - t0, log=(r.stdout + r.stderr)[-3000:])


@app.function(image=gpu_img, gpu="T4", cpu=4, memory=8192, timeout=1800, volumes={"/vol": vol})
def world(job: str, num: int, start: int, n: int) -> dict:
    t0 = time.time()
    vol.reload()
    d = f"/vol/{job}/s{num:02d}"
    env = dict(os.environ, GODOT_SILENCE_ROOT_WARNING="1")
    avi = f"/tmp/p{start}.avi"
    subprocess.run(["cp", "-r", f"{REMOTE}/generators/story3d/project", "/tmp/proj"], check=True)   # Godot writes
    cmd = ["xvfb-run", "-a", "-s", "-screen 0 1920x1080x24", "/opt/godot/godot", "--path",          # .godot/ here
           "/tmp/proj", "--rendering-driver", "vulkan", "--rendering-method", "forward_plus",
           "--write-movie", avi, "--fixed-fps", "30", "--quit-after", str(n), "--", d, str(start)]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    log = r.stdout + r.stderr
    errs = [ln for ln in log.splitlines() if "SCRIPT ERROR" in ln or "ERROR:" in ln][:8]
    dev = next((ln.strip() for ln in log.splitlines() if "Vulkan" in ln and "NVIDIA" in ln), "")
    mp4 = f"{d}/world_{start:06d}.mp4"
    if os.path.exists(avi):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", avi, "-frames:v", str(n), "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-crf", "16", mp4], check=True)
    vol.commit()
    return dict(num=num, start=start, n=n, ok=os.path.exists(mp4), errors=errs, device=dev, secs=time.time() - t0)


@app.function(image=cpu_img, cpu=4, memory=8192, timeout=1800, volumes={"/vol": vol})
def compose(job: str, num: int) -> dict:
    import sys
    t0 = time.time()
    vol.reload()
    d = f"/vol/{job}/s{num:02d}"
    parts = sorted(f for f in os.listdir(d) if f.startswith("world_") and f.endswith(".mp4"))
    with open(f"{d}/parts.txt", "w") as fh:
        fh.writelines(f"file '{d}/{p}'\n" for p in parts)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{d}/parts.txt",
                    "-c", "copy", f"{d}/world.mp4"], check=True)
    final = f"{d}/scene.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{d}/world.mp4", "-i", f"{d}/overlay.mov",
                    "-i", f"{d}/audio.wav", "-filter_complex",
                    "[1:v]setpts=PTS-STARTPTS[o];[0:v]setpts=PTS-STARTPTS[g];[g][o]overlay=eof_action=pass[v]",
                    "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-shortest", final], check=True)
    sys.path.insert(0, f"{REMOTE}/generators/story3d")
    import audit_story3d as A
    report = A.audit_scene(d, final)
    vol.commit()
    with open(final, "rb") as fh:
        mp4 = fh.read()
    return dict(num=num, mp4=mp4, report=report, secs=time.time() - t0)


def _ledger():
    if os.path.exists(LEDGER):
        with open(LEDGER) as fh:
            return json.load(fh)
    return {"budget_usd": BUDGET_USD, "runs": []}


@app.local_entrypoint()
def main(episode: str, scenes: str, out: str = "work/story3d", aspect: str = "h", note: str = ""):
    nums = [int(x) for x in scenes.split(",") if x]
    led = _ledger()
    month = dt.date.today().strftime("%Y-%m")
    spent = sum(r["cost_usd"] for r in led["runs"] if r["date"].startswith(month))
    worst = len(nums) * (300 * 8 * CPU_PRICE + 4 * 400 * (T4_PRICE + 4 * CPU_PRICE) + 200 * 4 * CPU_PRICE) * OVERHEAD
    print(f"[story3d] bulan {month}: ${spent:.2f} / ${BUDGET_USD:.2f}; estimasi terburuk ${worst:.2f} ({len(nums)} scene)")
    if spent + worst > BUDGET_USD:
        raise SystemExit("[story3d] STOP: budget bulanan akan terlewati.")
    job = f"{episode}_{int(time.time())}"
    t0 = time.time()
    cpu_s = gpu_s = 0.0
    ov = list(overlay.starmap([(job, episode, n, aspect) for n in nums]))
    for r in ov:
        cpu_s += r["secs"] * 8
        print(f"[story3d] overlay s{r['num']:02d}: {'OK' if r['ok'] else 'GAGAL'} {r['frames']} frames {r['secs']:.0f}s")
        if not r["ok"]:
            print(r["log"])
    good = [r for r in ov if r["ok"]]
    jobs = [(job, r["num"], s, min(PART, r["frames"] - s)) for r in good for s in range(0, r["frames"], PART)]
    wr = list(world.starmap(jobs))
    bad = set()
    for r in wr:
        gpu_s += r["secs"]
        if not r["ok"]:
            bad.add(r["num"])
        if not r["ok"] or r["errors"]:
            print(f"[story3d] world s{r['num']:02d}@{r['start']}: ok={r['ok']} errors={r['errors']}")
    print(f"[story3d] world: {len(wr)} part(s) on {sorted({r['device'][:40] for r in wr})}")
    cr = list(compose.starmap([(job, r["num"]) for r in good if r["num"] not in bad]))
    os.makedirs(out, exist_ok=True)
    reports = {}
    for r in cr:
        cpu_s += r["secs"] * 4
        path = os.path.join(out, f"{episode}_scene_{r['num']:02d}.mp4")
        with open(path, "wb") as fh:
            fh.write(r["mp4"])
        reports[r["num"]] = r["report"]
        with open(path.replace(".mp4", "_qa.json"), "w") as fh:
            json.dump(r["report"], fh, indent=1)
        print(f"[story3d] scene {r['num']:02d} -> {path}  QA {r['report']['verdict']} "
              f"({len(r['report']['fail'])} gagal, {len(r['report']['warn'])} peringatan)")
    cost = (cpu_s * (CPU_PRICE + 1 * MEM_PRICE) + gpu_s * (T4_PRICE + 4 * CPU_PRICE + 8 * MEM_PRICE)) * OVERHEAD
    led["runs"].append(dict(date=dt.date.today().isoformat(), note=note or f"story3d {episode} {scenes}",
                            engine="story3d (cairo overlay + godot-4.4.1 T4)", scenes=len(nums),
                            cpu_seconds=round(cpu_s, 1), gpu_seconds=round(gpu_s, 1),
                            wall_seconds=round(time.time() - t0, 1), cost_usd=round(cost, 4)))
    with open(LEDGER, "w") as fh:
        json.dump(led, fh, indent=1)
    with open(os.path.join(out, f"{job}.json"), "w") as fh:
        json.dump(dict(job=job, reports=reports), fh, indent=1)
    print(f"[story3d] DONE {len(cr)}/{len(nums)} scene(s) in {time.time() - t0:.0f}s wall ≈${cost:.3f} job={job}")
