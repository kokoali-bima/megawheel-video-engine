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
RHUBARB_URL = ("https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.13.0/"
               "Rhubarb-Lip-Sync-1.13.0-Linux.zip")               # same version as the VM build (1.13.0)
RHUBARB = "/opt/rhubarb/Rhubarb-Lip-Sync-1.13.0-Linux/rhubarb"
VIS_VOL = "/vol/visemes"                                       # lip-sync cache shared by all runs (Modal volume)

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
    .apt_install("ffmpeg", "libcairo2-dev", "pkg-config", "gcc", "fontconfig", "wget", "unzip")
    .run_commands(f"wget -q {RHUBARB_URL} -O /tmp/rh.zip && unzip -q /tmp/rh.zip -d /opt/rhubarb && "
                  f"{RHUBARB} --version")                        # lip-sync in the cloud (user 2026-10-06)
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
    env = dict(os.environ, S3D_REMOTE="1", PYTHONUNBUFFERED="1", RHUBARB=RHUBARB, S3D_VIS_CACHE=VIS_VOL)
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
    benign = ('err != VK_SUCCESS',)                             # headless swapchain probe; picture verified OK
    errs = [ln for ln in log.splitlines() if ("SCRIPT ERROR" in ln or "ERROR:" in ln)
            and not any(b in ln for b in benign)][:8]
    dev = next((ln.strip() for ln in log.splitlines() if "Using Device" in ln), "")
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
    # two-pass loudness (one pass landed at -18.3 LUFS on a scene with long quiet parts, calibration 2026-10-06)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{d}/audio.wav", "-af",
                        "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{d}/world.mp4", "-i", f"{d}/overlay.mov",
                    "-i", f"{d}/audio.wav", "-filter_complex",
                    "[1:v]setpts=PTS-STARTPTS[o];[0:v]setpts=PTS-STARTPTS[g];[g][o]overlay=eof_action=pass[v]",
                    "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                    "-af", ln, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", final], check=True)
    sys.path.insert(0, f"{REMOTE}/generators/story3d")
    import audit_story3d as A
    report = A.audit_scene(d, final)
    ep = job.rsplit("_", 1)[0]                                     # latest render of each scene, for the assembler
    os.makedirs(f"/vol/final/{ep}", exist_ok=True)
    subprocess.run(["cp", final, f"/vol/final/{ep}/scene_{num:02d}.mp4"], check=True)
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


# ------------------------------------------------------------------ episode assembly (smooth joins)
@app.function(image=cpu_img, cpu=16, memory=16384, timeout=3600, volumes={"/vol": vol})
def assemble_remote(ep: str, order: list, joins: list) -> dict:
    import numpy as np
    FPS = 30
    JOIN = dict(step_db=8.0, step_fade_db=14.0, drop_db=14.0, hole_s=1.2)
    t0 = time.time()
    vol.reload()
    fd = f"/vol/final/{ep}"
    parts = [f"{fd}/scene_{n:02d}.mp4" for n in order]
    miss = [p for p in parts if not os.path.exists(p)]
    if miss:
        return dict(ok=False, error=f"scene belum dirender: {miss}")

    def dur(p):
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                           capture_output=True, text=True)
        return float(r.stdout.strip())

    durs = [dur(p) for p in parts]
    xd = [j["dur"] for j in joins]
    tmp = "/tmp/asm"
    os.makedirs(tmp, exist_ok=True)
    enc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
    pieces = []

    def ff(args, out):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + args + enc + [out], check=True)
        pieces.append(out)

    for i, p in enumerate(parts):                                  # body of each scene + one short piece per join
        head = xd[i - 1] if i > 0 else 0.0
        tail = xd[i] if i < len(joins) else 0.0
        ff(["-ss", f"{head:.3f}", "-t", f"{durs[i] - head - tail:.3f}", "-i", p], f"{tmp}/b{i:02d}.mp4")
        if i < len(joins):
            d_ = xd[i]
            ff(["-ss", f"{durs[i] - d_:.3f}", "-t", f"{d_:.3f}", "-i", p, "-t", f"{d_:.3f}", "-i", parts[i + 1],
                "-filter_complex", f"[0:v][1:v]xfade=transition={joins[i]['kind']}:duration={d_}:offset=0[v];"
                                   f"[0:a][1:a]acrossfade=d={d_}:c1=tri:c2=tri[a]", "-map", "[v]", "-map", "[a]"],
               f"{tmp}/x{i:02d}.mp4")
    with open(f"{tmp}/list.txt", "w") as fh:
        fh.writelines(f"file '{q}'\n" for q in pieces)
    out = f"{tmp}/episode.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt",
                    "-c", "copy", out], check=True)
    # --- join sensors on the final audio
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", out, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
    sr = 16000

    def db(seg):
        return float(20 * np.log10(max(1e-9, float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 1e-9)))   # plain float

    rep, tcur = [], 0.0
    for i, j in enumerate(joins):
        tcur += durs[i] - xd[i]                                    # join starts here in the episode timeline
        a0, a1 = tcur - 1.0, tcur
        b0, b1 = tcur + xd[i], tcur + xd[i] + 1.0
        la, lb = db(x[int(a0 * sr):int(a1 * sr)]), db(x[int(b0 * sr):int(b1 * sr)])
        win = x[int((tcur - 0.6) * sr):int((tcur + xd[i] + 0.6) * sr)]
        hole, run_, longest = 0, 0.0, 0.0
        for q in range(0, len(win) - 800, 800):                    # 50 ms windows
            if db(win[q:q + 800]) < -55:
                run_ += 0.05
                longest = max(longest, run_)
            else:
                run_ = 0.0
        step = abs(la - lb)
        fails, warns = [], []
        lv = [db(win[q:q + 1600]) for q in range(0, max(0, len(win) - 1600), 1600)]   # 100 ms levels
        drop = max([lv[q] - lv[q + 1] for q in range(len(lv) - 1) if lv[q] > -40] + [0.0])
        if drop > JOIN["drop_db"]:
            fails.append(f"suara terpotong mendadak (turun {drop:.0f} dB dalam 0,1 dtk)")
        if j["kind"] == "dissolve" and step > JOIN["step_db"]:
            fails.append(f"lompatan volume {step:.1f} dB di tempat yang sama")
        elif step > JOIN["step_fade_db"]:
            warns.append(f"beda level {step:.1f} dB antar scene (cek: kontras disengaja?)")
        if longest >= JOIN["hole_s"]:
            fails.append(f"sunyi bolong {longest:.1f}s")
        rep.append(dict(join=f"{j['a']}->{j['b']}", kind=j["kind"], dur=j["dur"], at=round(tcur, 2),
                        level_before=round(float(la), 1), level_after=round(float(lb), 1), silence=round(float(longest), 2), fail=fails,
                        warn=warns, drop=round(float(drop), 1)))
    vol.commit()
    data = open(out, "rb").read()
    return dict(ok=True, mp4=data, joins=rep, durs=durs, secs=time.time() - t0)


@app.local_entrypoint()
def assemble(episode: str, order: str = "", out: str = "work/story3d"):
    import sys
    sys.path.insert(0, HERE)
    from assemble_story3d import plan_joins
    ed_p = os.path.join(ROOT, "stories", episode, "edit.json")
    ed = json.load(open(ed_p, encoding="utf-8")).get("story3d", {}) if os.path.exists(ed_p) else {}
    nums = [int(v) for v in order.split(",") if v] if order else ed.get("order", [])
    joins = plan_joins(episode, nums, ed.get("joins", {}))
    for j in joins:
        print(f"[assemble] {j['a']:02d}->{j['b']:02d}: {j['kind']} {j['dur']}s ({j['why']})")
    r = assemble_remote.remote(episode, nums, joins)
    if not r["ok"]:
        raise SystemExit(f"[assemble] STOP: {r['error']}")
    os.makedirs(out, exist_ok=True)
    tag = "" if not order else "_" + "-".join(f"{n:02d}" for n in nums)
    path = os.path.join(out, f"{episode}_episode{tag}.mp4")
    open(path, "wb").write(r["mp4"])
    chap, t = [], 0.0                                              # YouTube chapters at the middle of each join
    for i, n in enumerate(nums):
        sc = json.load(open(os.path.join(ROOT, "stories", episode, f"scene_{n:02d}.json"), encoding="utf-8"))
        start = 0.0 if i == 0 else t + joins[i - 1]["dur"] / 2
        if sc.get("chapter"):
            chap.append(f"{int(start // 60)}:{int(start % 60):02d} {sc['chapter']}")
        t += r["durs"][i] - (joins[i]["dur"] if i < len(joins) else 0.0)
    open(path.replace(".mp4", "_chapters.txt"), "w").write("\n".join(chap) + "\n")
    json.dump(r["joins"], open(path.replace(".mp4", "_joins.json"), "w"), indent=1)
    bad = [j for j in r["joins"] if j["fail"]]
    for j in r["joins"]:
        print(f"[assemble] sambungan {j['join']} @ {j['at']}s {j['kind']}: {j['level_before']} -> {j['level_after']} dB, "
              f"sunyi {j['silence']}s turun-mendadak {j['drop']}dB {'GAGAL ' + str(j['fail']) if j['fail'] else 'OK'}"
              + (f" | {j['warn']}" if j['warn'] else ""))
    print(f"[assemble] -> {path} ({sum(r['durs']) / 60:.2f} menit bahan, {r['secs']:.0f}s)")
    if bad:
        raise SystemExit(5)
