"""LAB — render the 3D CHALLENGE (Godot) on Modal instead of the VM CPU (user 2026-10-03: "setup modal dulu").
The export dir (scene.json, frames.json, sprites/) + the Godot project go up; every LEVEL renders in its own
16-vCPU container at the same time (levels are independent: effects reset per level), the mp4 parts come back and
are joined in order. Same monthly budget guard + modal_usage.json ledger as the other Modal apps.

Run on VM 99.3 (cd /root/video-engine):
  venv-modal/bin/modal run lab/godot3d_challenge/modal_godot.py --dir /root/lab/ch3d/s1 --out /root/lab/ch3d/s1/g.mp4
"""
import datetime as dt
import io
import json
import os
import subprocess
import tarfile
import time

import modal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(ROOT, "modal_usage.json")
BUDGET_USD = 29.0
CPUS, MEM_GB = 16, 8
CPU_PRICE = 0.0000131                                   # $/vCPU-second (Modal CPU), memory below
MEM_PRICE = 0.00000222                                  # $/GiB-second
OVERHEAD = 1.15
GODOT_URL = "https://github.com/godotengine/godot/releases/download/4.4.1-stable/Godot_v4.4.1-stable_linux.x86_64.zip"

app = modal.App("megawheel-godot3d")
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("xvfb", "xauth", "wget", "unzip", "ffmpeg", "libgl1", "libgl1-mesa-dri", "libegl1", "libgles2",
                 "libvulkan1", "mesa-vulkan-drivers",
                 "libxcursor1", "libxinerama1", "libxrandr2", "libxi6", "libfontconfig1", "libxkbcommon0",
                 "libasound2", "libpulse0", "libudev1", "libdbus-1-3")
    .run_commands(f"wget -q {GODOT_URL} -O /tmp/g.zip && unzip -q /tmp/g.zip -d /opt/godot && "
                  "mv /opt/godot/Godot_v4.4.1-stable_linux.x86_64 /opt/godot/godot && chmod +x /opt/godot/godot")
)


def _tar(paths):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for src, arc in paths:
            tf.add(src, arcname=arc)
    return buf.getvalue()


GPU_PRICE = {"T4": 0.000164, "L4": 0.000222}                # $/s, plus the container's CPU / memory


def _render(project_tgz, data_tgz, start, n, gpu):
    t0 = time.time()
    for blob, dst in ((project_tgz, "/tmp/w"), (data_tgz, "/tmp/w")):
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
            tf.extractall(dst)
    env = dict(os.environ, GODOT_SILENCE_ROOT_WARNING="1", LP_NUM_THREADS=str(CPUS))
    drv = ["--rendering-driver", "vulkan", "--rendering-method", "mobile"] if gpu else ["--rendering-driver", "opengl3"]
    cmd = ["xvfb-run", "-a", "-s", "-screen 0 1080x1920x24", "/opt/godot/godot", "--path", "/tmp/w/project"] + drv + [
           "--write-movie", "/tmp/w/part.avi", "--fixed-fps", "30", "--quit-after", str(n), "--", "/tmp/w/data", str(start)]
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    log = r.stdout + r.stderr
    errs = [ln for ln in log.splitlines() if "SCRIPT ERROR" in ln][:5]
    dev = next((ln.strip() for ln in log.splitlines() if "Vulkan" in ln and ("NVIDIA" in ln or "llvmpipe" in ln)), "")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "/tmp/w/part.avi", "-frames:v", str(n), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "18", "/tmp/w/part.mp4"], check=True)
    with open("/tmp/w/part.mp4", "rb") as fh:
        mp4 = fh.read()
    return dict(mp4=mp4, secs=time.time() - t0, errors=errs, start=start, n=n, device=dev)


@app.function(image=image, cpu=CPUS, memory=MEM_GB * 1024, timeout=1800)
def render_part(project_tgz: bytes, data_tgz: bytes, start: int, n: int) -> dict:
    return _render(project_tgz, data_tgz, start, n, None)


@app.function(image=image, gpu="T4", cpu=4, memory=MEM_GB * 1024, timeout=1800)
def render_part_gpu(project_tgz: bytes, data_tgz: bytes, start: int, n: int) -> dict:
    return _render(project_tgz, data_tgz, start, n, "T4")


def _ledger():
    if os.path.exists(LEDGER):
        with open(LEDGER) as fh:
            return json.load(fh)
    return {"budget_usd": BUDGET_USD, "runs": []}


@app.local_entrypoint()
def main(dir: str, out: str, note: str = "", gpu: str = "", start: int = -1, count: int = 0, project: str = ""):
    frames = json.load(open(os.path.join(dir, "frames.json")))["frames"]
    parts, s0 = [], 0                                  # one part per level (CHALLENGE) / per mode (RACE)
    for i in range(1, len(frames) + 1):
        if i == len(frames) or frames[i][0] != frames[s0][0]:
            parts.append((s0, i - s0))
            s0 = i
    if count > 0:                                                # test: a few frames only
        parts = [(max(0, start), count)]
    led = _ledger()
    month = dt.date.today().strftime("%Y-%m")
    spent = sum(r["cost_usd"] for r in led["runs"] if r["date"].startswith(month))
    per_sec = (GPU_PRICE[gpu] + 4 * CPU_PRICE if gpu else CPUS * CPU_PRICE) + MEM_GB * MEM_PRICE
    worst = len(parts) * 900 * per_sec * OVERHEAD
    print(f"[godot3d] bulan {month}: ${spent:.2f} / ${BUDGET_USD:.2f}; estimasi terburuk ${worst:.2f}; parts {parts}")
    if spent + worst > BUDGET_USD:
        raise SystemExit("[godot3d] STOP: budget bulanan akan terlewati. Tidak dijalankan.")
    pdir = project or os.path.join(HERE, "project")             # CHALLENGE (default) or e.g. lab/godot3d_race/project
    proj = _tar([(os.path.join(pdir, f), f"project/{f}") for f in sorted(os.listdir(pdir))
                 if f.endswith((".godot", ".tscn", ".gd"))])
    data = _tar([(os.path.join(dir, f), f"data/{f}") for f in ("scene.json", "frames.json")]
                + [(os.path.join(dir, "sprites"), "data/sprites")])
    t0 = time.time()
    fn = render_part_gpu if gpu else render_part
    res = list(fn.starmap([(proj, data, a, n) for a, n in parts]))
    print("[godot3d] devices:", sorted({r.get("device", "") for r in res}))
    lst = os.path.join(dir, "_parts.txt")
    with open(lst, "w") as fh:
        for k, r in enumerate(res):
            p = os.path.join(dir, f"_part{k}.mp4")
            with open(p, "wb") as f2:
                f2.write(r["mp4"])
            fh.write(f"file '{p}'\n")
            if r["errors"]:
                print(f"[godot3d] part {k} SCRIPT ERRORS: {r['errors']}")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)
    with open(out + ".render.json", "w") as fh:                  # for audit3d: script errors + frames per part
        json.dump(dict(errors=[e for r in res for e in r["errors"]], parts=[[r["start"], r["n"]] for r in res]), fh)
    for k in range(len(res)):
        os.remove(os.path.join(dir, f"_part{k}.mp4"))
    secs = sum(r["secs"] for r in res)
    cost = secs * per_sec * OVERHEAD
    led["runs"].append(dict(date=dt.date.today().isoformat(), note=note or f"godot3d {os.path.basename(dir)}",
                            cpu=CPUS, gpu=gpu or None, engine="godot-4.4.1-" + ("vulkan-" + gpu if gpu else "llvmpipe"), parts=len(parts), cpu_container_seconds=round(secs, 1),
                            wall_seconds=round(time.time() - t0, 1), cost_usd=round(cost, 4)))
    with open(LEDGER, "w") as fh:
        json.dump(led, fh, indent=1)
    print(f"[godot3d] DONE {len(frames)} frames in {time.time() - t0:.0f}s wall ({len(parts)} parts, "
          f"{secs:.0f} container-s) ≈${cost:.3f} -> {out}")
