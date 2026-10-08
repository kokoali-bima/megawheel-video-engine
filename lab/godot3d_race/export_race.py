"""LAB — 3D RACE (user 2026-10-03: all formats in 3D). The aired RACE engine (race25d.py v3) decides everything:
cast, lanes, hazards, physics, timeline, camera, narration, audio. This exporter runs it, catches its data right
before it would draw the 2.5D frames, and writes:
  scene.json   cast sizes, lanes, hazards (type, lane, x, trigger time), curve, theme, finish line, events
  frames.json  per output frame: mode, sim t, camera (camx, zoom incl. punch), shake px, every car's state
  sprites/     cast art per mood (60 px/m) + wheels
  overlay.mov  the engine's own screen layer: HUD, bubbles, READY-GO, replay, winner, end card, weather,
               speed lines + the FLYING hazards (dragons, meteor, UFO) drawn by the engine
  mix.wav      the engine's own audio; meta.json  cold open moment + question (the production rule)
  venv/bin/python lab/godot3d_race/export_race.py --seed 11 --out /root/lab/r3d/s11 [--like SIM_RACE25D_V3_S011]"""
import argparse
import json
import math
import os
import subprocess
import sys

import cairo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for sub in ("generators/physics_2d", "generators/lanes25d", "generators/voice"):
    sys.path.insert(0, os.path.join(ROOT, sub))
import sim_engine as se  # noqa: E402
import race25d as R  # noqa: E402
import registry  # noqa: E402

PPM = 60
MOODS = ["normal", "scared", "whoa", "dizzy", "happy"]
FLYING = ("dragon_fire", "dragon_ice", "meteor", "ufo")


class Caught(Exception):
    pass


def body_png(path, vk, mood):
    v = se.VEHICLES[vk]
    bw, bh = v["body"]
    w, h = int((bw + 1.6) * PPM), int((bh + 3.0) * PPM)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)
    ctx.translate(w / 2, h / 2)
    ctx.scale(PPM, -PPM)
    se.draw_body(ctx, vk, v, False, 0.0)
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
    ap.add_argument("--out", required=True)
    ap.add_argument("--like", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    name = f"LAB_R3D_S{a.seed:03d}"
    if a.like:                                                   # exactly what the review render used
        full = registry.load()
        ent = next(e for e in full["videos"] if e["video_id"] == a.like)
        man = json.load(open(f"{ROOT}/{ent['folder']}/{a.like}.json"))
        cast = man["params"]["cast"]
        orig_setup, orig_theme = R.setup, se.make_theme
        R.setup = lambda seed, app, forced=None: orig_setup(
            seed, {vk: (-10 + cast.index(vk) if vk in cast else 99) for vk in R.POOL}, forced)
        se.make_theme = lambda seed, force=None, used=None: orig_theme(seed, dict(man["theme"]), used=[])
        voice = man["voice"]
        def forced_cb(*x, **k):                              # same narrator, and switch voice C on like cb_pick
            if not voice.startswith("chatterbox"):
                return None
            who = voice.split(":")[1]
            se.CB.update(on=True, who=who, edge=se.CB_EDGE[who], missing=[])
            return voice
        se.cb_pick = forced_cb
        if not voice.startswith("chatterbox"):
            se.VOICES = [voice]
    got = {}
    orig_sim, orig_audio = R.simulate, R.build_audio

    def sim(seed):
        cars, events = orig_sim(seed)
        got.update(cars=cars, events=events)
        return cars, events

    def audio(frames, events, winner, star, replay, lines, voice, out_of, cta_start):
        x = orig_audio(frames, events, winner, star, replay, lines, voice, out_of, cta_start)
        got.update(frames=frames, winner=winner, star=star, replay=replay, cta_start=cta_start, audio=x,
                   voice=voice, out_of=out_of)
        se.cb_finish(f"narrator {name}")                         # missing voice-C lines -> Modal (cached after)
        raise Caught()
    R.simulate, R.build_audio = sim, audio
    # cb_finish may re-exec after it fills the voice cache. Restart this exporter
    # with its real arguments, not the borrowed race25d filename.
    sys.argv = [os.path.abspath(__file__), "--seed", str(a.seed), "--out", a.out, "--like", a.like]
    try:
        R.main()
    except Caught:
        pass
    cars, events, frames = got["cars"], got["events"], got["frames"]
    winner, star, replay, cta_start = got["winner"], got["star"], got["replay"], got["cta_start"]
    se.write_wav(os.path.join(a.out, "mix.wav"), got["audio"])
    print(f"[r3d] {len(frames)} frames, cast {[c['key'] for c in cars]}, hz {[(h['type'], h['lane']) for h in R.HZ]}",
          flush=True)

    sp = os.path.join(a.out, "sprites")
    os.makedirs(sp, exist_ok=True)
    cast_meta = {}
    for c in cars:
        vk, v = c["key"], se.VEHICLES[c["key"]]
        for m in MOODS:
            w, h = body_png(os.path.join(sp, f"{vk}_{m}.png"), vk, m)
        wheel_png(os.path.join(sp, f"{vk}_wheel.png"), vk)
        cast_meta[vk] = dict(body=list(v["body"]), wheel_r=v["wheel_r"], wheel_x=list(v["wheel_x"]), w=w, h=h,
                             travel=v["travel"], nick=v["nick"], color=list(v["color"]))
    hits = R.hit_cars(cars)
    th = se.th_time()
    scene = dict(seed=a.seed, theme=se.THEME, theme_id=se.THEME_ID, sky=[[s_, list(c_)] for s_, c_ in th["sky"]],
                 light=th.get("light", 1.0), night="moon" in th, cloud=list(th.get("cloud", (1, 1, 1))),
                 curve=R.CURVE, fin_x=R.FIN_X, cast=cast_meta, lanes={c["key"]: c["lane"] for c in cars},
                 hazards=[dict(type=h["type"], lane=h["lane"], x=h["x"], trig=R.hz_trig(h, cars)) for h in R.HZ],
                 events=[[k, t, x, z] for k, t, x, z in events],
                 hits=[dict(car=c["key"], type=c["hz"]["type"], trig=c["trig"]) for c in hits],
                 proj=dict(F=R.F_PERSP, D0=R.D0, LANE_D=R.LANE_D, Y_H=R.Y_H, CAM_H=R.CAM_H, WORLD_DY=R.WORLD_DY))
    json.dump(scene, open(os.path.join(a.out, "scene.json"), "w"))

    # ---- camera: the engine's own per-frame camera (same code as race25d.main)
    k_of, FIN_X, W = R.k_of, R.FIN_X, R.W
    rows, cams = [], []
    camx, zoom, prev_mode = None, 1.0, None
    for fi, (mode, t) in enumerate(frames):
        st = {id(c): R.state(c, t) for c in cars}
        focus = None
        for c in cars:
            if c.get("dodge_t") is not None and -0.8 < t - c["dodge_t"] < 1.4:
                focus = c
        for c in hits:
            if -0.9 < t - c["trig"] < 2.4:
                focus = c
        near_finish = st[id(winner)][0] > FIN_X - 30 or (winner["finish"] is not None and t >= winner["finish"])
        if near_finish or mode == "cta":
            focus = winner
        if mode == "replay":
            focus = star
        xs = [st[id(c)][0] for c in cars]
        mid = (max(xs) + min(xs)) / 2
        wgt = 0.85 if focus is not None else 0.55
        target = wgt * (st[id(focus)][0] + 2) + (1 - wgt) * mid if focus else mid + 1.5
        if mode == "replay":
            target = st[id(star)][0] + 1
        if focus is not None and focus["hz"] is not None and focus["hz"]["type"].startswith("dragon") \
                and focus is not winner:
            target = st[id(focus)][0] + 2.2
        spread = max(xs) - min(xs) + 9.0
        fit = float(np.clip(W * 0.92 / (spread * k_of(0.0)), 0.82, 1.12))
        cut = camx is None or mode != prev_mode
        camx = target if cut else camx + (target - camx) * (0.3 if mode == "replay" else 0.12)
        punch = 1.0
        for kind, et, ex, ez in events:
            if kind in ("land", "bump", "puddle", "crusher", "meteor", "wall", "hammer", "container", "oil") \
                    and 0 <= t - et < 0.35:
                punch = max(punch, 1 + 0.09 * math.sin(math.pi * (t - et) / 0.35))
        want = 1.15 if mode == "replay" else min(fit, 1.05 if focus else 1.0)
        zoom = want * punch if cut else zoom + (want * punch - zoom) * 0.12
        key = focus if focus is not None else max(cars, key=lambda c: st[id(c)][0])
        kx, kz = st[id(key)][0], st[id(key)][1]
        reach = 380.0 / (k_of(kz) * zoom)
        camx = float(np.clip(camx, kx - reach, kx + reach))
        prev_mode = mode
        shx = shy = 0.0
        for kind, et, ex, ez in events:
            if kind in ("land", "bump", "wall", "crusher", "meteor", "hammer", "container") and 0 <= t - et < 0.45:
                amp = (24 if kind == "meteor" else 16) * (1 - (t - et) / 0.45)
                shx, shy = amp * math.sin(t * 90), amp * math.cos(t * 70)
        cams.append((camx, zoom, shx, shy, focus))
        cs = []
        for c in cars:
            s = st[id(c)]
            cs.append([round(v, 4) for v in s] + [R.mood_of(c, t, s[0])])
        rows.append([mode[0], round(t, 4), round(camx, 4), round(zoom, 4), round(shx, 2), round(shy, 2), cs])
    json.dump(dict(fps=30, keys=["mode", "t", "camx", "zoom", "shx", "shy", "cars"],
                   car_keys=["x", "z", "h", "yaw", "pitch", "v", "sq", "split", "burn", "patched", "ice", "tires",
                             "mood"], frames=rows), open(os.path.join(a.out, "frames.json"), "w"))

    # ---- overlay: the engine's screen layer + flying hazards, same transforms as race25d.main
    ov = os.path.join(a.out, "overlay.mov")
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", "1080x1920",
                           "-r", "30", "-i", "-", "-c:v", "qtrle", ov], stdin=subprocess.PIPE)
    dummy = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8))
    for fi, (mode, t) in enumerate(frames):
        camx, zoom, shx, shy, focus = cams[fi]
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1080, 1920)
        ctx = cairo.Context(surf)
        ctx.save()
        ctx.translate(0, R.WORLD_DY)
        ctx.translate(540 + shx, 1520 + shy)
        ctx.scale(zoom, zoom)
        ctx.translate(-540, -1520)
        for hz in R.HZ:
            if hz["type"] in FLYING:
                R.draw_hazard_front(ctx, hz, camx, t, cars)
        ctx.restore()
        heads = {}
        for c in cars:                                           # head positions for bubbles (drawn off-screen)
            dummy.save()
            hd = R.draw_car(dummy, c, t, camx)
            dummy.restore()
            heads[id(c)] = None if hd is None else (540 + (hd[0] - 540) * zoom + shx,
                                                   1520 + (hd[1] - 1520) * zoom + shy + R.WORLD_DY, hd[2])
        se.draw_weather(ctx, fi / 30)
        if mode == "race":
            se.draw_speed_lines(ctx, max(R.state(c, t)[5] for c in cars), fi / 30)
        for c in cars:
            hd = heads.get(id(c))
            if not hd or mode == "cta":
                continue
            if c["trig"] is not None:
                R.bubble(ctx, R.HAZARDS[c["hz"]["type"]]["bubble"], hd[0], hd[1], t - c["trig"] - 0.1, hd[2] * zoom)
            if c["bump_t"] is not None:
                R.bubble(ctx, "HEY!", hd[0], hd[1], t - c["bump_t"] - 0.1, hd[2] * zoom)
            if c.get("dodge_t") is not None:
                R.bubble(ctx, "NICE!", hd[0], hd[1], t - c["dodge_t"] - 0.1, hd[2] * zoom)
            if c is winner and c["finish"] is not None:
                R.bubble(ctx, "YEAH!", hd[0], hd[1], t - c["finish"] - 0.3, hd[2] * zoom)
        if mode != "cta":
            R.draw_hud(ctx, cars, t)
        if mode == "race":
            se.draw_ready_go(ctx, t)
        if mode == "replay":
            se.draw_replay_overlay(ctx, fi / 30)
        if winner["finish"] is not None and t >= winner["finish"] and mode != "replay":
            age = t - winner["finish"] if mode == "race" else 2.0
            se.draw_confetti(ctx, age)
            s = se.ease_out_back(min(1.0, age / 0.4))
            ctx.save()
            ctx.translate(540, 620 if mode == "cta" else 760)
            ctx.scale(s, s)
            se.draw_text(ctx, f"{R.nick(winner['key']).upper()} WINS!", 0, 0, 120, fill=(1, 0.86, 0.12))
            ctx.restore()
        if mode == "cta":
            R.draw_cta(ctx, fi / 30 - cta_start)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close()
    ff.wait()
    out_of = got["out_of"]
    t_star = out_of(star["trig"]) if star is not None else out_of(winner["finish"] or 5.0)
    json.dump(dict(cold_t=t_star, cold_text=R.QUESTION_TEXT[0] or "WHO WINS?",
                   title=f"{R.QUESTION_TEXT[0]} 🏁"), open(os.path.join(a.out, "meta.json"), "w"))
    print(f"[r3d] export done -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
