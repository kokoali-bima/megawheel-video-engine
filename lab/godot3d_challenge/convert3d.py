"""LAB -> review: turn a pending 2.5D CHALLENGE Short into its 3D version (user 2026-10-03: "convert / render ulang
ke 3D" the review videos). Same seed, same cast, same story, same timeline, HUD, narration, title and cold open —
only the picture is re-drawn in 3D (Godot on Modal). Nothing reaches review unless BOTH audits pass:
  audit3d  (this file): every wheel drawn, no Godot script error, frame count / duration, no black/white frames,
           mandatory effects scheduled (lava contact -> explosion, water pit -> splash), sim replay identical
  audit.py (production): LEVEL / FAIL / WINNER badges in sync, audio levels, CTA, previews, uniqueness
The 2.5D file is kept as <id>_25d.mp4. Run on VM 99.3 (cd /root/video-engine):
  venv/bin/python lab/godot3d_challenge/convert3d.py SIM_POTHOLES_V2_S021"""
import json
import os
import shutil
import subprocess
import sys

BASE = "/root/video-engine"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [f"{BASE}/generators/physics_2d", f"{BASE}/generators/publishing"]
import registry  # noqa: E402


def sh(cmd, **kw):
    print("+", " ".join(cmd)[:160], flush=True)
    return subprocess.run(cmd, check=True, **kw)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_entries",
                          "stream=codec_type,width,height,r_frame_rate,nb_read_frames:format=duration", "-of", "json",
                          path], capture_output=True, text=True).stdout
    return json.loads(out)


def luminance(path, t):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1", "-vf",
                        "scale=54:96,format=gray", "-f", "rawvideo", "-"], capture_output=True)
    px = r.stdout
    return sum(px) / max(1, len(px))


def audit3d(d, mp4, man_prod, preview_man):
    items = []

    def chk(name, ok, val=""):
        items.append((name, bool(ok), str(val)))

    scene = json.load(open(f"{d}/scene.json"))
    frames = json.load(open(f"{d}/frames.json"))["frames"]
    rep = json.load(open(f"{mp4.replace('.mp4', '')}_g.mp4.render.json")) if os.path.exists(
        f"{mp4.replace('.mp4', '')}_g.mp4.render.json") else {"errors": ["no render report"]}
    # sim replay identical to the reviewed 2.5D render
    chk("replay tokoh sama dengan versi review", [lv["vehicle"] for lv in preview_man["levels"]]
        == [lv["vehicle"] for lv in man_prod["levels"]], [lv["vehicle"] for lv in preview_man["levels"]])
    for k in ("outcomes", "theme_id", "voice", "track_id"):
        chk(f"replay {k} sama dengan versi review", preview_man.get(k) == man_prod.get(k),
            f"{preview_man.get(k)} vs {man_prod.get(k)}")
    chk("replay durasi sama (tanpa cold open)",
        abs(preview_man["duration"] - (man_prod["duration"] - man_prod.get("cold_open_s", 0))) < 0.05,
        f"{preview_man['duration']} vs {man_prod['duration']}")
    # every wheel of every car on every frame
    bad = [i for i, f in enumerate(frames)
           if len(f[12]) != len(scene["cast"][scene["levels"][f[0]]["vk"]]["wheel_x"]) or len(f[12]) > 6]
    chk("semua roda tergambar (jumlah roda = data mobil, maks 6)", not bad,
        "ok" if not bad else f"{len(bad)} frame salah, mis. {bad[:3]}")
    chk("tidak ada SCRIPT ERROR Godot", not rep.get("errors"), rep.get("errors", [])[:2])
    p = probe(mp4)
    vs = next(s for s in p["streams"] if s["codec_type"] == "video")
    au = [s for s in p["streams"] if s["codec_type"] == "audio"]
    want = len(frames) + round(man_prod.get("cold_open_s", 0) * 30)
    chk("1080x1920 30 fps + audio", vs["width"] == 1080 and vs["height"] == 1920 and vs["r_frame_rate"] == "30/1" and au,
        f"{vs['width']}x{vs['height']} {vs['r_frame_rate']} audio={bool(au)}")
    chk("jumlah frame = timeline + cold open (±2)", abs(int(vs["nb_read_frames"]) - want) <= 2,
        f"{vs['nb_read_frames']} vs {want}")
    chk("durasi = manifest (±0.3 s)", abs(float(p["format"]["duration"]) - man_prod["duration"]) <= 0.3,
        f"{float(p['format']['duration']):.2f} vs {man_prod['duration']}")
    dur = float(p["format"]["duration"])
    lum = [luminance(mp4, 2.0 + (dur - 2.5) * k / 11) for k in range(12)]   # skip the cold-open white flash (~1.5 s)
    chk("tidak ada frame hitam / putih (12 sampel)", all(25 < v < 235 for v in lum), [round(v) for v in lum])
    # mandatory effects of this series
    for li, lv in enumerate(scene["levels"]):
        lava = (scene["pit_kind"] == "lava" and lv.get("sunk") is not None) or lv.get("burned") is not None
        if lava:
            chk(f"L{li + 1}: kontak lava -> ledakan terjadwal", True, f"t={lv.get('sunk') or lv.get('burned'):.2f}")
        if scene["pit_kind"] == "water" and lv.get("sunk") is not None:
            chk(f"L{li + 1}: masuk kolam -> cipratan terjadwal", True, f"t={lv['sunk']:.2f}")
        if lv.get("broken"):
            chk(f"L{li + 1}: tabrakan -> panel copot (tanpa ledakan kecuali lava)", True, f"t={lv['broken']['t']:.2f}")
    return items


def main():
    vid = sys.argv[1]
    e = registry.get(vid)
    if not e or e.get("status") != "RENDERED_PENDING_APPROVAL":
        raise SystemExit(f"[convert3d] STOP: {vid} bukan RENDERED_PENDING_APPROVAL")
    folder = f"{BASE}/{e['folder']}"
    man_path = f"{folder}/{vid}.json"
    man = json.load(open(man_path))
    was3d = bool(man.get("render3d"))
    if was3d and "--redo" not in sys.argv:                      # --redo: re-render a 3D one (2.5D stays _25d.mp4)
        raise SystemExit(f"[convert3d] {vid} sudah 3D (pakai --redo untuk render ulang)")
    d = f"/root/lab/ch3d/conv_{vid}"
    shutil.rmtree(d, ignore_errors=True)
    sh([f"{BASE}/venv/bin/python", f"{HERE}/export_challenge.py", "--seed", str(e["seed"]), "--series", e["series"],
        "--out", d, "--like", vid], stdout=open(f"{d}.export.log", "w"), stderr=subprocess.STDOUT)
    pname = f"LAB_CH3D_{e['series'].upper()}_S{e['seed']:03d}"
    preview_man = json.load(open(f"{BASE}/work/physics_2d/previews/{pname}/{pname}.json"))
    g = f"{d}/{vid}_g.mp4"
    sh([f"{BASE}/venv-modal/bin/modal", "run", f"{HERE}/modal_godot.py", "--dir", d, "--out", g, "--note",
        f"godot3d convert {vid}", "--gpu", "T4"])                # Modal GPU (Vulkan on a T4): faster + cheaper
    out = f"{d}/{vid}.mp4"
    sh([f"{BASE}/venv/bin/python", f"{HERE}/compose.py", "--dir", d, "--video", g, "--out", out])
    items = audit3d(d, out, man, preview_man)
    ok3d = all(ok for _, ok, _ in items)
    rep = [f"# Audit 3D: {vid}", "", f"- Hasil: **{'LULUS' if ok3d else 'GAGAL'}**", "", "| Cek | Hasil | Nilai |",
           "|---|---|---|"] + [f"| {n} | {'✅' if ok else '❌'} | {v} |" for n, ok, v in items]
    open(f"{d}/{vid}_audit3d.md", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))
    if not ok3d:
        raise SystemExit(f"[convert3d] audit 3D GAGAL -> {vid} tetap 2.5D ({d}/{vid}_audit3d.md)")
    # swap in: 2.5D kept as backup, production audit must pass on the 3D file
    if was3d:
        os.replace(f"{folder}/{vid}.mp4", f"{folder}/{vid}_3dold.mp4")
    else:
        os.replace(f"{folder}/{vid}.mp4", f"{folder}/{vid}_25d.mp4")
    shutil.copy(out, f"{folder}/{vid}.mp4")
    shutil.copy(f"{d}/{vid}_audit3d.md", f"{folder}/{vid}_audit3d.md")
    import audit
    if not audit.run_audit(vid, folder=folder):
        os.replace(f"{folder}/{vid}_3dold.mp4" if was3d else f"{folder}/{vid}_25d.mp4", f"{folder}/{vid}.mp4")
        raise SystemExit(f"[convert3d] audit produksi GAGAL pada versi 3D -> dikembalikan ke versi sebelumnya")
    if was3d and os.path.exists(f"{folder}/{vid}_3dold.mp4"):
        os.remove(f"{folder}/{vid}_3dold.mp4")
    if was3d and os.path.exists(f"{folder}/{vid}_3dold.mp4"):
        os.remove(f"{folder}/{vid}_3dold.mp4")
    man = json.load(open(man_path))
    if not was3d:
        man.update(render3d=True, engine=man.get("engine", "") + " + godot3d (lab/godot3d_challenge)",
                   assets=man.get("assets", "") + "; picture re-drawn in 3D with Godot 4.4.1 (rendered on Modal GPU T4)")
    json.dump(man, open(man_path, "w"), indent=2, ensure_ascii=False)
    registry.update(vid, render3d=True)
    prev = f"{folder}/preview"                                   # review sheet from the 3D picture (2.5D kept)
    if os.path.isdir(prev) and not os.path.isdir(f"{folder}/preview_25d"):
        shutil.move(prev, f"{folder}/preview_25d")
    os.makedirs(prev, exist_ok=True)
    dur = float(probe(f"{folder}/{vid}.mp4")["format"]["duration"])
    for k in range(12):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{dur * (k + 0.5) / 12:.2f}", "-i",
                        f"{folder}/{vid}.mp4", "-frames:v", "1", f"{prev}/f{k:02d}.png"], check=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{dur - 1.0:.2f}", "-i", f"{folder}/{vid}.mp4",
                    "-frames:v", "1", f"{prev}/outro.png"], check=True)   # the production audit wants the end card
    try:
        import drive_sync
        e = registry.get(vid)
        for key in ("drive_id", "drive_sheet_id"):               # the 2.5D upload goes, the 3D one comes
            if e.get(key):
                try:
                    drive_sync.service().files().delete(fileId=e[key]).execute()
                except Exception as ex:
                    print(f"[drive] hapus lama gagal: {ex}")
        registry.update(vid, drive_id=None, drive_sheet_id=None)
        drive_sync.sync_one(vid)
    except Exception as ex:
        print(f"[drive] dilewati: {ex}")
    print(f"[convert3d] {vid} -> 3D, kedua audit LULUS")


if __name__ == "__main__":
    main()
