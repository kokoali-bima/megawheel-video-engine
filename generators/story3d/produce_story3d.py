"""THE standard command for a story3d scene / episode (option C). Any agent runs exactly this; the result is the
same because every step is fixed: pinned Godot 4.4.1 + fonts, seeded worlds, cached voices, fixed QA thresholds.
  cd /root/video-engine && venv/bin/python generators/story3d/produce_story3d.py --episode S01E02_who_is_kraggor \
       --scenes 2[,3,...] [--upload]
Steps (stop at the first hard failure):
  1. preflight   VM code == GitHub (git_sync), Modal CLI present, scene files exist and parse
  2. prepare     every voice line (Chatterbox on Modal, cached + speech-recognition QA); a line that is not
                 cached afterwards stops the render (lip-sync is made in the Modal container, rhubarb x86)
  3. render      Modal: characters (CPU) + Godot world (T4 GPU) + compose, all scenes / parts in parallel
  4. QA          sensor report per scene (audit_story3d): PASS / WARN / FAIL -> work/story3d/<ep>/QA_<job>.md
                 FAIL -> exit 5: the agent fixes the scene JSON / engine and runs again (never upload a FAIL)
  5. upload      (--upload, only PASS / WARN) Drive ipandu-video/story3d/<episode>/ for the user's review
Exit codes: 0 ok · 2 preflight · 3 prepare · 4 render · 5 QA FAIL."""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "generators", "story"))
sys.path.insert(0, HERE)


def log(msg):
    print(f"[produce3d] {msg}", flush=True)


def preflight(ep, nums):
    r = subprocess.run(["bash", "git_sync.sh", "status"], cwd=ROOT, capture_output=True, text=True)
    st = r.stdout + r.stderr
    log(st.strip().splitlines()[0] if st.strip() else "git_sync status: kosong")
    ab = st.split("ahead/behind:")[-1].split()[0] if "ahead/behind:" in st else "?/?"
    if "STOP" in st or ab.split("/")[-1] not in ("0",):
        log("STOP: kode VM tidak sama dengan GitHub (jalankan bash git_sync.sh pull dulu)")
        return False
    if not os.path.exists(os.path.join(ROOT, "venv-modal", "bin", "modal")):
        log("STOP: venv-modal/bin/modal tidak ada")
        return False
    for n in nums:
        p = os.path.join(ROOT, "stories", ep, f"scene_{n:02d}.json")
        try:
            json.load(open(p))
        except Exception as e:                                     # noqa: BLE001
            log(f"STOP: {p}: {e}")
            return False
    return True


def prepare(ep, nums, aspect):
    """Voices only (Chatterbox on Modal, cached, speech-recognition QA). Lip-sync is made in the Modal render
    container (rhubarb x86, user 2026-10-06), so nothing here depends on the VM's CPU architecture."""
    import story25d as ST
    ST.PREPARE_ONLY = True
    ST.visemes = lambda audio, text: [(0.0, "X")]                 # mouths are made in the cloud
    ok = True
    for n in nums:
        ST.render_scene(ep, n, aspect)
        P = ST.PREPARED
        log(f"prepare scene {n:02d}: {len(P['lines'])} kalimat, {P['shots']} shot, {P['total']:.1f}s")
    ST.PREPARE_ONLY = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--aspect", default="h")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    nums = [int(x) for x in a.scenes.split(",") if x]
    out = os.path.join(ROOT, "work", "story3d", a.episode)
    os.makedirs(out, exist_ok=True)
    if not preflight(a.episode, nums):
        sys.exit(2)
    if not prepare(a.episode, nums, a.aspect):
        log("STOP: persiapan suara / lip-sync belum lengkap")
        sys.exit(3)
    cmd = [os.path.join(ROOT, "venv-modal", "bin", "modal"), "run", "generators/story3d/modal_story3d.py",
           "--episode", a.episode, "--scenes", a.scenes, "--out", out, "--aspect", a.aspect,
           "--note", a.note or f"story3d {a.episode} {a.scenes}"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    tail = "\n".join(ln for ln in (r.stdout + r.stderr).splitlines() if "[story3d]" in ln)
    print(tail, flush=True)
    job = next((ln.split("job=")[1].strip() for ln in tail.splitlines() if "job=" in ln), None)
    if r.returncode != 0 or not job:
        log("STOP: render Modal gagal\n" + (r.stdout + r.stderr)[-2500:])
        sys.exit(4)
    import audit_story3d as A
    res = json.load(open(os.path.join(out, f"{job}.json")))["reports"]
    md = [f"# QA story3d — {a.episode} — {dt.datetime.now():%Y-%m-%d %H:%M} — job {job}", ""]
    worst = "PASS"
    for n in nums:
        rep = res.get(str(n))
        if rep is None:
            md.append(f"### scene {n:02d} — TIDAK ADA HASIL")
            worst = "FAIL"
            continue
        md.append(A.to_md(f"scene {n:02d}", rep))
        md.append("")
        worst = "FAIL" if rep["verdict"] == "FAIL" or worst == "FAIL" else ("WARN" if rep["verdict"] == "WARN" else worst)
    qa = os.path.join(out, f"QA_{job}.md")
    open(qa, "w").write("\n".join(md))
    print("\n".join(md), flush=True)
    log(f"QA {worst} -> {qa}")
    if worst == "FAIL":
        sys.exit(5)
    if a.upload:
        sys.path.insert(0, os.path.join(ROOT, "generators", "publishing"))
        import drive_sync
        parent = drive_sync.folder("story3d", a.episode)
        for n in nums:
            p = os.path.join(out, f"{a.episode}_scene_{n:02d}.mp4")
            fid = drive_sync.upload(p, parent, os.path.basename(p))
            log(f"drive story3d/{a.episode}/{os.path.basename(p)} ({fid})")
        drive_sync.upload(qa, parent, os.path.basename(qa))
    log("DONE")


if __name__ == "__main__":
    main()
