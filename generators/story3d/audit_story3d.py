"""story3d QA sensors (user 2026-10-06: "lakukan analisa ... apakah semuanya smooth? efek tidak monoton? backsound tidak
mengganggu / membosankan / monoton? pencahayaan & bayangan tidak mengganggu? jalan masih miring ketika zoom-in? objek
fokus ketutup objek lain? suara noise? ... siap otomasi sehingga agen mana pun hasilnya mirip").
Every check is a measurement with a fixed threshold (THRESH) so any agent gets the same verdict:
  camera     smooth motion inside shots (screen speed / jerk of fixed world anchors), frame-difference spikes
  roll       Godot pinhole camera == cairo camera (reprojection error of road points) -> the road never tilts
             against the cars (bug of pilot v6); grounding: cars on the road band, not floating
  framing    focus / speaking actor visible, inside the frame, not hidden by another car, subtitle or letterbox
  variety    shot sizes, camera moves, static holds, repeated shot types
  light      exposure per shot, character contrast vs background, dark shadow patches on the road (day)
  audio      noise / hiss in quiet parts, dead air, music masking the voices, effects audible on phone speakers,
             music monotony (one cue everywhere), loudness of the final mix
  reveal     far Kraggor's eyes present in his shot and absent before it
Inputs: the job dir (scene.json, frames.json, stems.npz, audio_events.json) + the final scene mp4.
  python generators/story3d/audit_story3d.py <job_dir> <scene.mp4>    (prints the report, writes qa.json/qa.md)"""
import json
import math
import os
import subprocess
import sys

import numpy as np

THRESH = dict(
    reproj_px=2.0,            # Godot vs cairo projection of road points (px @1080p): above = road tilts / floats
    speed_px=70.0,            # camera anchor speed per frame inside a shot (px @1080p) - whips must be marked
    jerk_px=22.0,             # change of that speed between frames: a visible jolt
    diff_spike=5.0,           # frame difference vs the shot median (x): a jump inside a shot
    focus_visible=0.80,       # share of the focus actor box inside the picture
    occlude=0.30,             # share of the focus box covered by a nearer car
    sub_overlap=0.35,         # share of the focus box under subtitle band / letterbox while a line plays
    static_s=7.0,             # a shot longer than this with no camera move and no car moving
    same_cam_run=3,           # this many identical shot sizes in a row
    luma_min=28.0, luma_max=215.0,
    contrast_min=1.35,        # character vs the background behind it (luma ratio)
    shadow_patch=0.22,        # share of the road band much darker than the road median (day only)
    hiss_ratio=0.30,          # energy above 3 kHz in quiet parts (no voice, no effect)
    hiss_level_db=-46.0,      # ...only when the quiet part is louder than this
    dead_air_s=1.6,           # silence (< -58 dBFS) this long
    mask_db=6.0,              # voice must be this much louder than music + effects while talking
    phone_band=0.25,          # share of an effect's energy in 200-4000 Hz (phone speakers)
    cue_share=0.85,           # one music cue covering more than this of a scene > 40 s = monotonous
    lufs=(-17.5, -14.5),
)
SAMPLE_W, SAMPLE_H = 480, 270


# ------------------------------------------------------------------ camera models
def cairo_px(S, f, X, Yh, z):
    """story25d: world (X m, height Yh m, lane depth z) -> screen px through the frame's cairo matrix."""
    k = S["F"] / (S["D0"] + S["DZ"] * z)
    px, py = S["CX"] + (X - f["camx"]) * k, S["Y_H"] + (S["CAM_H"] - Yh) * k
    xx, yx, xy, yy, x0, y0 = f["m"]
    return xx * px + xy * py + x0, yx * px + yy * py + y0


def godot_px(S, f, X, Yh, z):
    """Python port of project/story3d.gd _process() camera (keep in sync!): pinhole at (camx, CAM_H, 0), roll = +atan2,
    lens shift in screen axes, focal = F/DZ * matrix scale."""
    xx, yx, xy, yy, x0, y0 = f["m"]
    W, H = S["W"], S["H"]
    sc = math.sqrt(abs(xx * yy - xy * yx))
    roll = math.atan2(yx, xx)
    px = xx * S["CX"] + xy * S["Y_H"] + x0
    py = yx * S["CX"] + yy * S["Y_H"] + y0
    vx, vy = px - W / 2, py - H / 2
    focal = S["F"] / S["DZ"] * sc
    d = (S["D0"] + S["DZ"] * z) / S["DZ"]
    dx, dy = X - f["camx"], Yh - S["CAM_H"]
    c, s = math.cos(roll), math.sin(roll)
    xc, yc = c * dx + s * dy, -s * dx + c * dy
    return W / 2 + vx + focal * xc / d, H / 2 + vy - focal * yc / d


def actor_box(S, f, a):
    """Screen box of a car (x0, y0, x1, y1) from its row [id, x, z, face, h, small, bw, bh, wheel_r, flicker]."""
    _, x, z, face, h, small, bw, bh, wr, _ = a
    hw, top = bw * 0.5 * small, (wr * 2 + bh * 1.75) * small
    pts = [cairo_px(S, f, x + sx * hw, h + hy, z) for sx in (-1, 1) for hy in (0.0, top)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def inter(a, b):
    w = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    h = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    return w * h


def area(a):
    return max(1e-6, (a[2] - a[0]) * (a[3] - a[1]))


# ------------------------------------------------------------------ video helpers
def read_gray(mp4, w=320, h=180):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp4, "-vf", f"scale={w}:{h}", "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)


def grab(mp4, t, w=SAMPLE_W, h=SAMPLE_H, fmt="rgb24"):
    ch = 4 if fmt == "rgba" else 3
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", mp4, "-frames:v", "1", "-vf",
                          f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", fmt, "-"], capture_output=True).stdout
    if len(raw) < w * h * ch:
        return None
    return np.frombuffer(raw[:w * h * ch], np.uint8).reshape(h, w, ch).astype(np.float32)


def luma(img):
    return img[..., 0] * 0.299 + img[..., 1] * 0.587 + img[..., 2] * 0.114


def db(x):
    return 20 * math.log10(max(1e-9, float(np.sqrt(np.mean(np.square(x)))) if len(x) else 1e-9))


# ------------------------------------------------------------------ the audit
def audit_scene(d, mp4):
    S = json.load(open(os.path.join(d, "scene.json")))
    fr = [f for _, f in json.load(open(os.path.join(d, "frames.json")))["frames"]]
    shots = S["shots"]
    sc = S["scene"]
    W, H, fps = S["W"], S["H"], S.get("fps", 30)
    k1080 = 1080.0 / H
    fail, warn, metrics = [], [], {}

    def shot_frames(i):
        return [j for j, f in enumerate(fr) if f["shot"] == i]

    # --- roll / reprojection: the Godot world must sit exactly where cairo puts the cars
    err = 0.0
    for f in fr[::5]:
        for X in (f["camx"] - 8, f["camx"], f["camx"] + 8):
            for z in (-0.5, 1.0, 3.0):
                for Yh in (0.0, 2.0):
                    a, b = cairo_px(S, f, X, Yh, z), godot_px(S, f, X, Yh, z)
                    err = max(err, math.hypot(a[0] - b[0], a[1] - b[1]) * k1080)
    metrics["reproj_px"] = round(err, 3)
    if err > THRESH["reproj_px"]:
        fail.append(f"roll/proyeksi: dunia Godot meleset {err:.1f}px dari tokoh (jalan miring / mobil melayang)")
    road = sc.get("location", "town") in ("town", "arena", "trackside", "podium", "country")
    for f in fr[::15]:
        for a in f["actors"]:
            if road and not (-0.7 <= a[2] <= 3.3):
                warn.append(f"grounding: {a[0]} di z={a[2]} di luar pita jalan (t={f['t']:.1f})")
                break
    if not sc.get("contact_shadow", True):
        warn.append("grounding: contact_shadow dimatikan (mobil bisa terlihat melayang di atas jalan 3D)")

    # --- camera smoothness (fixed world anchors) + frame-difference spikes
    worst_v = worst_j = 0.0
    bad_v = []
    for sh in shots:
        js = shot_frames(sh["i"])[2:]
        if len(js) < 4:
            continue
        f0 = fr[js[0]]
        anchors = [(f0["camx"] + dx, 0.0, 1.0) for dx in (-6, 0, 6)]
        pos = np.array([[cairo_px(S, fr[j], *an) for an in anchors] for j in js]) * k1080
        v = np.linalg.norm(np.diff(pos, axis=0), axis=2).max(axis=1)
        jk = np.abs(np.diff(v))
        whip = bool(sh["move"].get("whip"))
        if len(v):
            worst_v = max(worst_v, float(v.max()))
        if len(jk):
            worst_j = max(worst_j, float(jk.max()))
        if not whip and len(v) and v.max() > THRESH["speed_px"]:
            bad_v.append(f"shot {sh['i']}: kamera {v.max():.0f}px/frame")
        if not whip and len(jk) and jk.max() > THRESH["jerk_px"]:
            bad_v.append(f"shot {sh['i']}: sentakan {jk.max():.0f}px/frame²")
    metrics.update(cam_speed_px=round(worst_v, 1), cam_jerk_px=round(worst_j, 1))
    fail.extend(b for b in bad_v if "kamera" in b)
    warn.extend(b for b in bad_v if "kamera" not in b)
    g = read_gray(mp4)
    if len(g) > 2:
        dif = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))
        spikes = []
        for sh in shots:
            js = [j for j in shot_frames(sh["i"])[3:-2] if j < len(dif)]
            if len(js) < 6:
                continue
            seg = dif[js]
            med = max(0.6, float(np.median(seg)))
            hit = [js[q] for q in np.nonzero(seg > THRESH["diff_spike"] * med)[0]]
            fx = set(sh["fx"]) | set(sh["sfx"])
            if hit and not ({"shake", "punch", "lamp_off", "flash"} & fx) and not sh["move"].get("whip"):
                spikes.append(f"shot {sh['i']}: lompatan gambar di t={fr[hit[0]]['t']:.2f}s")
        metrics["diff_spikes"] = len(spikes)
        warn.extend(spikes)

    # --- framing: focus / speaker visible, not covered
    ev = json.load(open(os.path.join(d, "audio_events.json"))) if os.path.exists(os.path.join(d, "audio_events.json")) else {}
    lines = ev.get("lines", [])
    sub_band = (0, H * 0.78, W, H)
    for sh in shots:
        js = shot_frames(sh["i"])
        if not js:
            continue
        f = fr[js[len(js) // 2]]
        talk = [ln for ln in lines if ln[1] <= f["t"] <= ln[1] + ln[2]]
        want = [sh["on"]] if sh.get("on") else []
        want += [ln[0] for ln in talk if ln[0] not in want]
        acts = {a[0]: a for a in f["actors"]}
        for aid in want:
            if aid not in acts:
                if aid not in ("narrator", "announcer", "announcer2") and sh.get("on") == aid:
                    fail.append(f"framing shot {sh['i']}: tokoh fokus '{aid}' tidak tampil")
                continue
            bx = actor_box(S, f, acts[aid])
            vis = inter(bx, (0, 0, W, H)) / area(bx)
            if vis < THRESH["focus_visible"] and sh["cam"] not in ("ecu",):
                warn.append(f"framing shot {sh['i']}: {aid} hanya {vis:.0%} di dalam layar")
            for o in f["actors"]:
                if o[0] != aid and o[2] < acts[aid][2] - 0.05:   # nearer car drawn on top
                    cov = inter(bx, actor_box(S, f, o)) / area(bx)
                    if cov > THRESH["occlude"]:
                        fail.append(f"framing shot {sh['i']}: {aid} tertutup {o[0]} {cov:.0%}")
            if talk and sh["cam"] not in ("close", "ecu"):
                ov = inter(bx, sub_band) / area(bx)
                if ov > THRESH["sub_overlap"]:
                    warn.append(f"framing shot {sh['i']}: subtitle menutupi {aid} {ov:.0%}")

    # --- variety / monotony of picture
    cams = [s["cam"] for s in shots]
    moves = set(k for s in shots for k in s["move"])
    metrics.update(shot_sizes=sorted(set(cams)), moves=sorted(moves))
    run = 1
    for i in range(1, len(cams)):
        run = run + 1 if cams[i] == cams[i - 1] else 1
        if run >= THRESH["same_cam_run"]:
            warn.append(f"variasi: {run} shot '{cams[i]}' berturut-turut (shot {i - run + 1}-{i})")
    if len(shots) >= 5 and len(set(cams)) < 3:
        warn.append(f"variasi: hanya {len(set(cams))} ukuran shot")
    if len(shots) >= 5 and len(moves) < 2:
        warn.append(f"variasi: gerak kamera hanya {sorted(moves) or 'tidak ada'}")
    for sh in shots:
        js = shot_frames(sh["i"])
        dur = sh["t1"] - sh["t0"]
        if dur > THRESH["static_s"] and not sh["move"] and js:
            xs = [sum(a[1] for a in fr[j]["actors"]) for j in (js[0], js[-1])]
            if abs(xs[1] - xs[0]) < 0.5:
                warn.append(f"variasi shot {sh['i']}: diam {dur:.1f}s tanpa gerak kamera/mobil")

    # --- light: exposure, character contrast, shadow patches
    night = S["theme"].get("time") == "night"
    ovl = os.path.join(d, "overlay.mov")
    wld = os.path.join(d, "world.mp4")
    lum_list = []
    for sh in shots:
        tm = (sh["t0"] + sh["t1"]) / 2
        img = grab(mp4, tm)
        if img is None:
            continue
        L = luma(img)
        lum_list.append(round(float(L.mean()), 1))
        if L.mean() < THRESH["luma_min"]:
            warn.append(f"cahaya shot {sh['i']}: terlalu gelap (luma {L.mean():.0f})")
        if L.mean() > THRESH["luma_max"]:
            warn.append(f"cahaya shot {sh['i']}: terlalu terang (luma {L.mean():.0f})")
        o = grab(ovl, tm, fmt="rgba") if os.path.exists(ovl) else None
        w = grab(wld, tm) if os.path.exists(wld) else None
        if o is not None and w is not None:
            m = o[..., 3] > 200
            if m.sum() > 400:
                ring = np.zeros_like(m)
                ys, xs = np.nonzero(m)
                ring[max(0, ys.min() - 20):ys.max() + 20, max(0, xs.min() - 20):xs.max() + 20] = True
                ring &= ~m
                lc, lb_ = float(luma(o[..., :3])[m].mean()), float(luma(w)[ring].mean()) if ring.any() else 1.0
                ratio = (max(lc, lb_) + 12) / (min(lc, lb_) + 12)
                if ratio < THRESH["contrast_min"]:
                    warn.append(f"cahaya shot {sh['i']}: tokoh kurang kontras dengan latar ({ratio:.2f})")
        if w is not None and not night:
            f = fr[min(len(fr) - 1, int(tm * fps))]
            y0 = int(np.clip(cairo_px(S, f, f["camx"], 0, 3.2)[1] / H * SAMPLE_H, 0, SAMPLE_H - 1))
            y1 = int(np.clip(cairo_px(S, f, f["camx"], 0, -0.6)[1] / H * SAMPLE_H, 0, SAMPLE_H))
            if y1 - y0 > 6:
                band = luma(w)[y0:y1]
                share = float((band < 0.5 * np.median(band)).mean())
                if share > THRESH["shadow_patch"]:
                    warn.append(f"bayangan shot {sh['i']}: {share:.0%} jalan tertutup bayangan gelap")
    metrics["luma_per_shot"] = lum_list

    # --- audio
    stp = os.path.join(d, "stems.npz")
    if os.path.exists(stp):
        st = np.load(stp)
        sr = float(st["sr"])
        V, M, X, A = (st[n].astype(np.float32) for n in ("voice", "music", "sfx", "amb"))
        mix = V + M + X + A
        win = int(0.5 * sr)
        n = len(mix) // win
        quiet_hiss, dead = [], 0.0
        longest = 0.0
        for q in range(n):
            seg = slice(q * win, (q + 1) * win)
            lv = db(mix[seg])
            if lv < -58:
                dead += 0.5
                longest = max(longest, dead)
                continue
            dead = 0.0
            if db(V[seg]) < -45 and db(X[seg]) < -45 and lv > THRESH["hiss_level_db"]:
                spec = np.abs(np.fft.rfft(mix[seg])) ** 2
                fq = np.fft.rfftfreq(win, 1 / sr)
                hi = spec[fq > 3000].sum() / max(1e-12, spec.sum())
                if hi > THRESH["hiss_ratio"]:
                    quiet_hiss.append(round(q * 0.5, 1))
        metrics.update(hiss_windows=len(quiet_hiss), longest_silence_s=longest)
        if quiet_hiss:
            fail.append(f"audio: desis/noise di bagian sepi (t={quiet_hiss[:5]})")
        if longest >= THRESH["dead_air_s"]:
            warn.append(f"audio: sunyi total {longest:.1f}s")
        masked = []
        for spk, t0, du in lines:
            seg = slice(int(t0 * sr), int((t0 + du) * sr))
            if db(V[seg]) - db(M[seg] + X[seg]) < THRESH["mask_db"] and db(M[seg] + X[seg]) > -40:
                masked.append(f"{spk}@{t0:.1f}")
        if masked:
            warn.append(f"audio: musik/efek menutupi suara tokoh ({masked[:4]})")
        weak = []
        for name, t0 in ev.get("sfx", []):
            seg = X[int(t0 * sr):int((t0 + 1.2) * sr)]
            if len(seg) < 100 or db(seg) < -50:
                continue
            spec = np.abs(np.fft.rfft(seg)) ** 2
            fq = np.fft.rfftfreq(len(seg), 1 / sr)
            band = spec[(fq >= 200) & (fq <= 4000)].sum() / max(1e-12, spec.sum())
            if band < THRESH["phone_band"]:
                weak.append(f"{name}@{t0:.1f}({band:.0%})")
        if weak:
            warn.append(f"audio: efek tidak terdengar di speaker HP {weak[:4]}")
        total = len(mix) / sr
        cues = [c for c in sc.get("score", []) if "cue" in c]
        if total > 40 and cues:
            span = {}
            for c in cues:
                a_, b_ = shots[c["from"]]["t0"], shots[min(c.get("to", c["from"]), len(shots) - 1)]["t1"]
                span[c["cue"]] = span.get(c["cue"], 0.0) + (b_ - a_)
            top = max(span.values()) / total
            metrics["music_top_cue_share"] = round(top, 2)
            if top > THRESH["cue_share"] and len(span) == 1:
                warn.append(f"audio: musik monoton (satu cue {top:.0%} scene)")
        elif total > 40 and not cues and sc.get("music") is None:
            warn.append("audio: scene panjang tanpa spotting musik")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", mp4, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    lu = [ln for ln in r.stderr.splitlines() if ln.strip().startswith("I:")]
    if lu:
        val = float(lu[-1].split()[1])
        metrics["lufs"] = val
        if not THRESH["lufs"][0] <= val <= THRESH["lufs"][1]:
            warn.append(f"audio: loudness {val} LUFS di luar target")

    # --- reveal: far Kraggor's eyes only in his shot
    first_k = next((f["t"] for f in fr if f.get("kfar")), None)
    if first_k is not None:
        pre = [sh for sh in shots if sh["t1"] <= first_k]
        if pre:
            img = grab(mp4, (pre[-1]["t0"] + pre[-1]["t1"]) / 2)
            if img is not None:
                yel = (img[..., 0] > 200) & (img[..., 1] > 160) & (img[..., 2] < 90)
                if yel[:SAMPLE_H // 2].sum() > 25:
                    warn.append("reveal: titik kuning (mata?) terlihat sebelum shot Kraggor")
    verdict = "FAIL" if fail else ("WARN" if warn else "PASS")
    rep = dict(verdict=verdict, fail=fail, warn=warn, metrics=metrics, thresholds=THRESH)
    with open(os.path.join(d, "qa.json"), "w") as fh:
        json.dump(rep, fh, indent=1)
    return rep


def to_md(name, rep):
    out = [f"### {name} — QA {rep['verdict']}", ""]
    for k in ("fail", "warn"):
        for x in rep[k]:
            out.append(f"- {'❌' if k == 'fail' else '⚠️'} {x}")
    if not rep["fail"] and not rep["warn"]:
        out.append("- ✅ semua sensor lolos")
    m = rep["metrics"]
    out.append(f"- metrik: reproj {m.get('reproj_px')}px · kamera {m.get('cam_speed_px')}px/f · sentakan "
               f"{m.get('cam_jerk_px')} · shot {m.get('shot_sizes')} · gerak {m.get('moves')} · LUFS {m.get('lufs')} · "
               f"desis {m.get('hiss_windows')} · sunyi {m.get('longest_silence_s')}s")
    return "\n".join(out)


if __name__ == "__main__":
    rep = audit_scene(sys.argv[1], sys.argv[2])
    print(to_md(os.path.basename(sys.argv[2]), rep))
