"""LAB — 3D CHALLENGE sample (user 2026-10-03): the aired CHALLENGE engine (sim_engine.py) decides EVERYTHING —
physics, story, timeline, camera, sizes, moods, HUD, narration — and Godot only re-draws the world in 3D with
bigger crash damage. This exporter runs the real engine in --preview-only mode and writes:
  <out>/scene.json      track (polyline, pits, ramp, signs), theme, cast sizes, per-level events
  <out>/frames.json     per output frame: level, mode, sim time, camera (x, y, zoom incl. punch), shake px,
                        car (x, y, angle, yaw squeeze, sink, wheels, detached), mood, broken / melt / burned
  <out>/sprites/        <vk>_<mood>.png body+face (+ _broken), <vk>_wheel.png  (60 px per metre, cast art)
  <out>/overlay.mov     the engine's own HUD / bubbles / READY-GO / replay overlay / speed lines (alpha)
  <out>/mix.wav         the engine's own audio mix (narrator, engine, SFX; no music bed)
  venv/bin/python lab/godot3d_challenge/export_challenge.py --seed 21 --series potholes --out /root/lab/ch3d/s21
Production modules are imported read-only; nothing in production imports lab/."""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "generators", "physics_2d"))
import sim_engine as se  # noqa: E402

PPM = 60
MOODS = ["normal", "scared", "whoa", "dizzy", "happy"]


def body_png(path, vk, mood, broken=False):
    v = se.VEHICLES[vk]
    bw, bh = v["body"]
    w, h = int((bw + 1.6) * PPM), int((bh + 3.0) * PPM)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)
    ctx.translate(w / 2, h / 2)
    ctx.scale(PPM, -PPM)
    se.draw_body(ctx, vk, v, broken, 0.0)
    se.draw_face(ctx, vk, mood, 0.0)
    surf.write_to_png(path)
    return w, h


def wheel_png(path, vk):
    v = se.VEHICLES[vk]
    r = v["wheel_r"]
    s = int(2 * r * PPM * 1.15) + 4
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, s, s)
    ctx = cairo.Context(surf)
    ctx.translate(s / 2, s / 2)
    ctx.scale(PPM, -PPM)
    se.draw_wheel(ctx, 0.0, 0.0, 0.0, r, vk.startswith("monster"))
    surf.write_to_png(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--series", default="potholes")
    ap.add_argument("--out", required=True)
    ap.add_argument("--like", default="", help="pending VIDEO_ID: replay the sim with the registry as it was then")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    name = f"LAB_CH3D_{a.series.upper()}_S{a.seed:03d}"
    if a.like:                                                   # same cast / theme / voice as that render
        import registry
        full = registry.load()
        idx = next(i for i, e in enumerate(full["videos"]) if e["video_id"] == a.like)
        snap = dict(full, videos=full["videos"][:idx])
        registry.load = lambda: snap
    sys.argv = ["sim_engine.py", "--seed", str(a.seed), "--series", a.series, "--preview-only", "--name", name]
    se.main()                                                    # the real engine: sim + timeline + audio + checks
    L0 = se.LEVELS
    print(f"[export] {len(se.INDEX)} frames, levels {[L['vk'] for L in L0]}", flush=True)

    # ---- sprites (cast art, every mood + broken)
    sp = os.path.join(a.out, "sprites")
    os.makedirs(sp, exist_ok=True)
    cast = {}
    for L in L0:
        vk, v = L["vk"], L["v"]
        for m in MOODS:
            w, h = body_png(os.path.join(sp, f"{vk}_{m}.png"), vk, m)
        body_png(os.path.join(sp, f"{vk}_broken.png"), vk, "dizzy", broken=True)
        wheel_png(os.path.join(sp, f"{vk}_wheel.png"), vk)
        cast[vk] = dict(body=list(v["body"]), wheel_r=v["wheel_r"], wheel_x=list(v["wheel_x"]), w=w, h=h,
                        color=list(v["color"]), nick=v["nick"], mass=v["mass"])

    # ---- scene
    th = se.th_time()
    scene = dict(series=se.SERIES, seed=a.seed, track=[list(p) for p in se.TRACK], pits=[list(p) for p in se.PITS],
                 pit_kind=se.PIT_KIND, ramps=[list(r) for r in se.RAMPS], bumps=[list(b) for b in se.BUMPS],
                 signs=list(se.SIGNS), finish_x=se.FINISH_X,
                 puddles=[list(p) for p in se.PUDDLES], barriers=[list(b) for b in se.BARRIERS],
                 vents=[dict(v) for v in se.VENTS], theme=se.THEME, theme_id=se.THEME_ID,
                 sky=[[s_, list(c)] for s_, c in th["sky"]], light=th.get("light", 1.0), night="moon" in th,
                 cloud=list(th.get("cloud", (1, 1, 1))),
                 S=se.S, ground_y=se.GROUND_Y, cast=cast, title=se.TITLE,
                 levels=[dict(vk=L["vk"], start=L["start"], event=dict(type=L["event"]["type"], t=L["event"]["t"]),
                              broken=(dict(t=L["broken"]["t"], x=L["broken"]["x"], y=L["broken"]["y"])
                                      if L["broken"] else None),
                              impacts=[[ti, s_, x, y] for ti, s_, x, y in L["impacts"]],
                              sunk=L.get("sunk"), burned=L.get("burned")) for L in L0])
    json.dump(scene, open(os.path.join(a.out, "scene.json"), "w"))

    # ---- frames
    frames = []
    for g, (li, j) in enumerate(se.INDEX):
        L = L0[li]
        st, mode = L["frames"][j]
        camx, camy, z = L["cam"][j]
        z *= se.zoom_punch(L, st)
        shx, shy = se.shake_offset(L, st)
        s = se.car_state(L, st)
        si = st * se.REC_HZ
        det = [d is not None and si >= d for d in L["detached"]]
        frames.append([li, mode[0], round(st, 4), round(camx, 4), round(camy, 4), round(z, 4), round(shx, 2),
                       round(shy, 2), round(s["cx"], 4), round(s["cy"] - s.get("sink", 0.0), 4), round(s["ca"], 4),
                       round(se.yaw_scale(s.get("yaw", 0.0)), 3), [[round(x, 4), round(y, 4), round(an, 3)]
                                                                    for x, y, an in s["wheels"]], det,
                       se.mood_at(L, st, s), bool(L["broken"] is not None and st >= L["broken"]["t"]),
                       round(se.melt_amount(L, st), 3), bool(L.get("burned") is not None and st >= L["burned"]),
                       round(s["speed"], 2), round(s["air"], 2)])
    json.dump(dict(fps=se.FPS, keys=["li", "mode", "st", "camx", "camy", "z", "shx", "shy", "cx", "cy", "ca", "ys",
                                     "wheels", "det", "mood", "broken", "melt", "burned", "speed", "air"],
                   frames=frames), open(os.path.join(a.out, "frames.json"), "w"))

    # ---- overlay: the engine's own screen-space layer (HUD, bubbles, READY-GO, replay, speed lines)
    ov = os.path.join(a.out, "overlay.mov")
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", "1080x1920",
                           "-r", str(se.FPS), "-i", "-", "-c:v", "qtrle", ov], stdin=subprocess.PIPE)
    for g, (li, j) in enumerate(se.INDEX):
        L = L0[li]
        st, mode = L["frames"][j]
        tl = j / se.FPS
        camx, camy, z = L["cam"][j]
        z *= se.zoom_punch(L, st)
        shx, shy = se.shake_offset(L, st)
        s = se.car_state(L, st)
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1080, 1920)
        ctx = cairo.Context(surf)
        if mode == "live" and s["air"] < 0.5:
            se.draw_speed_lines(ctx, s["speed"], tl)
        if mode == "live":
            se.draw_ready_go(ctx, tl)
        car_sx = 540 + shx + (s["cx"] - camx) * se.S * z
        car_sy = se.GROUND_Y + shy - (s["cy"] - camy) * se.S * z
        se.draw_bubbles(ctx, L, st, car_sx, car_sy, z)
        if mode == "replay":
            se.draw_replay_overlay(ctx, tl)
        se.draw_hud(ctx, L, li, st, tl, g / se.FPS, mode, s["cx"])
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close()
    ff.wait()
    shutil.copy(f"{se.WORK}/mix_{name}.wav", os.path.join(a.out, "mix.wav"))
    # what the aired video would be titled / opened with (cold open = first failed level)
    subj = next((L["vk"] for L in L0 if L["event"]["type"] != "win"), L0[-1]["vk"])
    fails = [L["start"] + se.out_time(L, L["event"]["t"]) for L in L0 if L["event"]["type"] != "win"]
    json.dump(dict(cold_t=(fails or [3.0])[0], cold_text=f"CAN {se.VEHICLES[subj]['nick']} SURVIVE?",
                   title=se.challenge_title(subj, se.SERIES_DEFS[se.SERIES]["obst"],
                                            se.SERIES_DEFS[se.SERIES]["yt_title"].split("?")[-1].strip(), a.seed)),
              open(os.path.join(a.out, "meta.json"), "w"))
    print(f"[export] done -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
