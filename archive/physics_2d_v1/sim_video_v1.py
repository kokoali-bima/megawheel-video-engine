#!/usr/bin/env python3
"""Procedural physics Shorts prototype: cartoon cars vs giant potholes.

Everything (footage, engine sounds, SFX, music) is generated here, so the
output is 100% original. Only the narration uses Edge-TTS.

Flow: simulate candidate runs -> pick runs matching the story (fail, fail, win)
-> build timeline + audio -> render frames in parallel -> mux MP4.
"""
import argparse
import asyncio
import hashlib
import json
import math
import multiprocessing as mp
import os
import subprocess
import time
import wave

import cairo
import numpy as np
import pymunk

W, H, FPS = 1080, 1920, 30
SR = 44100
S = 72.0            # pixels per metre
GROUND_Y = 1290     # screen y of the camera anchor
SUBSTEPS = 8
BASE = "/root/sim-prototype"
WORK = f"{BASE}/work"
OUT_DIR = f"{BASE}/output"
VOICE = "en-US-AnaNeural"
CTA = ("Tap LIKE if you enjoyed this video, DISLIKE if you didn't, "
       "and smash SUBSCRIBE to MegaWheel Kids!")
TITLE = "CARS VS GIANT POTHOLES!"

# Audio balance (from PROJECT_HISTORY_AND_HANDOVER.md, stems normalised to 0.45 peak first)
VOL_NARR, VOL_ENGINE, VOL_BGM, VOL_SFX = 1.60, 0.85, 0.10, 0.85

# ---------------------------------------------------------------- track
START_X = 3.0
FINISH_X = 100.0
PITS = [(30.0, 33.2, 3.2), (54.0, 62.0, 5.0), (78.0, 83.0, 3.5)]   # x0, x1, depth
RAMP = (48.0, 54.0, 1.4)                                           # x0, x1, height


def track_points():
    return [(-40, 0), (30, 0), (30, -3.2), (33.2, -3.2), (33.2, 0), (48, 0), (54, 1.4),
            (54, -5), (62, -5), (62, 0), (78, 0), (78, -3.5), (83, -3.5), (83, 0), (170, 0)]


# ---------------------------------------------------------------- vehicles
VEHICLES = {
    "sports": dict(name="Red Sports Car", color=(0.93, 0.16, 0.18), body=(4.2, 0.62), mass=900,
                   wheel_r=0.42, wheel_m=25, wheel_x=(-1.35, 1.4), travel=0.45, speeds=(7, 17),
                   cabin=[(-1.3, 0.31), (0.5, 0.31), (-0.1, 0.85), (-1.0, 0.85)],
                   engine=(55, 2.2),
                   intro="Level one! The speedy red sports car. Can it jump the giant potholes?"),
    "bus": dict(name="Yellow School Bus", color=(1.0, 0.78, 0.05), body=(7.4, 2.1), mass=5200,
                wheel_r=0.55, wheel_m=90, wheel_x=(-2.5, 2.3), travel=0.35, speeds=(6, 14),
                cabin=None, engine=(38, 1.3),
                intro="Level two! The big yellow school bus. It's heavy, but can it make it?"),
    "monster": dict(name="Monster Truck", color=(0.12, 0.45, 0.95), body=(4.3, 0.9), mass=2400,
                    wheel_r=1.0, wheel_m=130, wheel_x=(-1.75, 1.75), travel=1.0, speeds=(9, 20),
                    cabin=[(-1.5, 0.45), (0.4, 0.45), (0.0, 1.35), (-1.3, 1.35)],
                    engine=(36, 1.7),
                    intro="Level three! The mighty monster truck. Big wheels, big jump!"),
}
STORY = [("sports", "fail"), ("bus", "fail"), ("monster", "win")]
FAIL_LINES = {"pit": "Oh no! Right into the giant pothole!",
              "flip": "Whoa! It flipped right over!",
              "stuck": "Uh oh... it's totally stuck!"}
WIN_LINE = "Yes! The monster truck made it! We have a winner!"
LEVEL_COLORS = [(0.18, 0.72, 0.3), (1.0, 0.52, 0.08), (0.6, 0.3, 0.92)]


# ================================================================ physics
def build_space():
    space = pymunk.Space()
    space.gravity = (0, -9.81)
    space.iterations = 25
    pts = track_points()
    for a, b in zip(pts, pts[1:]):
        seg = pymunk.Segment(space.static_body, a, b, 0.08)
        seg.friction = 1.0
        seg.elasticity = 0.05
        space.add(seg)
    return space


def spawn(space, v, x0):
    bw, bh = v["body"]
    r, travel, m = v["wheel_r"], v["travel"], v["mass"]
    nw = len(v["wheel_x"])
    ride_y = r + 0.6 * travel + bh / 2
    polys = [[(-bw / 2, -bh / 2), (bw / 2, -bh / 2), (bw / 2, bh / 2), (-bw / 2, bh / 2)]]
    if v["cabin"]:
        polys.append(v["cabin"])
    moment = sum(pymunk.moment_for_poly(m / len(polys), p) for p in polys)
    chassis = pymunk.Body(m, moment)
    chassis.position = (x0, ride_y + 0.05)
    flt = pymunk.ShapeFilter(group=1)
    space.add(chassis)
    for p in polys:
        s = pymunk.Poly(chassis, p, radius=0.03)
        s.friction = 0.6
        s.elasticity = 0.1
        s.filter = flt
        space.add(s)

    stiff = (m * 9.81 / nw) / (0.4 * travel + 0.1)
    damp = 2 * 0.6 * math.sqrt(stiff * m / nw)
    torque = m * 7.0 * r / nw
    wheels, motors = [], []
    for wx in v["wheel_x"]:
        wb = pymunk.Body(v["wheel_m"], pymunk.moment_for_circle(v["wheel_m"], 0, r))
        wb.position = chassis.local_to_world((wx, -bh / 2 - 0.6 * travel))
        ws = pymunk.Circle(wb, r)
        ws.friction = 1.6
        ws.elasticity = 0.1
        ws.filter = flt
        groove = pymunk.GrooveJoint(chassis, wb, (wx, -bh / 2 - 0.05), (wx, -bh / 2 - travel), (0, 0))
        spring = pymunk.DampedSpring(chassis, wb, (wx, -bh / 2), (0, 0), travel + 0.1, stiff, damp)
        motor = pymunk.SimpleMotor(chassis, wb, 0)
        motor.max_force = torque
        space.add(wb, ws, groove, spring, motor)
        wheels.append(wb)
        motors.append(motor)
    return dict(chassis=chassis, wheels=wheels, motors=motors, torque=torque, ride_y=ride_y)


def nearest_obstacle(x):
    best, bi = 1e9, -1
    for i, (x0, x1, _) in enumerate(PITS):
        d = 0 if x0 - 1 <= x <= x1 + 1 else min(abs(x - x0), abs(x - x1))
        if d < best:
            best, bi = d, i
    return bi


def simulate(v, speed, after_fail=6.0, after_win=15.0, t_max=24.0):
    space = build_space()
    car = spawn(space, v, START_X)
    ch, wheels, motors = car["chassis"], car["wheels"], car["motors"]
    dt = 1.0 / (FPS * SUBSTEPS)
    for m in motors:
        m.rate = 0
    for _ in range(int(0.7 / dt)):          # settle suspension, not recorded
        space.step(dt)

    target = speed / v["wheel_r"]           # SimpleMotor: wheel.w - chassis.w = -rate -> +x motion
    rec = dict(cx=[], cy=[], ca=[], wheels=[], wrel=[], speed=[])
    impacts, event = [], None
    flip_t = stuck_t = None
    prev_v = ch.velocity
    last_imp = -1.0
    f = 0
    while True:
        t = f / FPS
        if event is None:
            rate, force = target, car["torque"]
        elif event["type"] == "win":
            rate, force = target * max(0.0, 1 - (t - event["t"]) / 2.5), car["torque"] * 0.6
        else:
            rate, force = 0.0, 0.0
        for m in motors:
            m.rate, m.max_force = rate, force

        rec["cx"].append(ch.position.x)
        rec["cy"].append(ch.position.y)
        rec["ca"].append(ch.angle)
        rec["wheels"].append([(w.position.x, w.position.y, w.angle) for w in wheels])
        rec["wrel"].append(float(np.mean([abs(w.angular_velocity - ch.angular_velocity) for w in wheels])))
        rec["speed"].append(ch.velocity.length)

        for _ in range(SUBSTEPS):
            space.step(dt)
        f += 1
        t = f / FPS

        dv = (ch.velocity - prev_v).length
        prev_v = ch.velocity
        if dv > 2.5 and t - last_imp > 0.25:
            impacts.append((t, min(1.0, dv / 10.0), ch.position.x, ch.position.y))
            last_imp = t

        if event is None:
            a = (ch.angle + math.pi) % (2 * math.pi) - math.pi
            if abs(a) > 1.9:
                flip_t = flip_t if flip_t is not None else t
                if t - flip_t > 0.5:
                    event = dict(type="flip", t=flip_t)
            else:
                flip_t = None
            if event is None and ch.position.y - car["ride_y"] < -2.2:
                event = dict(type="pit", t=max(0.0, t - 0.3))
            if event is None and t > 2.0 and ch.velocity.length < 0.6:
                stuck_t = stuck_t if stuck_t is not None else t
                if t - stuck_t > 1.5:
                    event = dict(type="stuck", t=stuck_t)
            elif ch.velocity.length >= 0.6:
                stuck_t = None
            if event is None and ch.position.x > FINISH_X:
                event = dict(type="win", t=t)
            if event is None and t > t_max:
                event = dict(type="timeout", t=t)
            if event is not None:
                event["x"] = ch.position.x
                event["obstacle"] = nearest_obstacle(ch.position.x)
        else:
            if t >= event["t"] + (after_win if event["type"] == "win" else after_fail):
                break

    for k in rec:
        rec[k] = np.asarray(rec[k], dtype=np.float64)
    if rec["cx"][-1] < rec["cx"][0] + 1 and event["type"] != "stuck":
        raise RuntimeError("car did not move forward, motor sign is wrong")
    return dict(rec=rec, impacts=impacts, event=event, speed=float(speed))


def choose_runs(rng, intro_durs):
    chosen = []
    for li, (vk, want) in enumerate(STORY):
        v = VEHICLES[vk]
        lo = intro_durs[li] + 0.4
        hi = 15.0 if want == "win" else 11.5
        cands, summary = [], []
        for sp in np.linspace(*v["speeds"], 21):
            run = simulate(v, sp)
            ev = run["event"]
            summary.append(f"{sp:.1f}:{ev['type']}@{ev['t']:.1f}s/obs{ev['obstacle']}")
            is_win = ev["type"] == "win"
            if (want == "win") == is_win and ev["type"] != "timeout" and lo <= ev["t"] <= hi:
                cands.append(run)
        print(f"[sim] {vk}: " + ", ".join(summary), flush=True)
        if not cands:
            raise RuntimeError(f"no run of {vk} matches outcome {want}")
        used = {c["event"]["obstacle"] for c in chosen}
        fresh = [c for c in cands if c["event"]["obstacle"] not in used]
        pool = fresh or cands
        chosen.append(pool[rng.integers(len(pool))])
    return chosen


def camera_track(rec):
    n = len(rec["cx"])
    cam = np.zeros((n, 2))
    cx, cy = rec["cx"][0] + 3.0, 0.0
    for i in range(n):
        tx = rec["cx"][i] + 3.0
        ty = float(np.clip(rec["cy"][i] - 1.5, -4.5, 4.0)) * 0.8
        cx += (tx - cx) * (1.0 if i == 0 else 0.18)
        cy += (ty - cy) * 0.12
        cam[i] = (cx, cy)
    return cam


# ================================================================ audio
def read_wav(path):
    with wave.open(path) as w:
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return data.astype(np.float64) / 32768.0


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def tts(text):
    key = hashlib.md5(f"{VOICE}|{text}".encode()).hexdigest()[:12]
    mp3, wav = f"{WORK}/tts_{key}.mp3", f"{WORK}/tts_{key}.wav"
    if not os.path.exists(wav):
        import edge_tts

        async def go():
            await edge_tts.Communicate(text, VOICE, rate="+6%").save(mp3)
        asyncio.run(go())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", str(SR), wav],
                       check=True)
    x = read_wav(wav)
    nz = np.nonzero(np.abs(x) > 0.01)[0]          # trim silence
    if len(nz):
        x = x[max(0, nz[0] - 200): nz[-1] + 2000]
    return x


def peak(x, target=0.45):
    m = np.max(np.abs(x)) if len(x) else 0
    return x * (target / m) if m > 0 else x


def smooth(x, n):
    return np.convolve(x, np.ones(n) / n, "same")


def per_sample(vals, n):
    return np.interp(np.arange(n) / SR * FPS, np.arange(len(vals)), vals)


def synth_engine(wrel, amp, base, k, seed):
    n = int(len(wrel) * SR / FPS)
    f = per_sample(base + k * np.minimum(wrel, 60), n)
    a = per_sample(amp, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = sum(np.sin(h * ph) / h ** 1.2 for h in range(1, 9))
    sig = sig * (0.75 + 0.25 * np.sin(ph * 0.5))
    sig = sig + smooth(np.random.default_rng(seed).standard_normal(n), 12) * 0.35
    return smooth(sig, 4) * a


def synth_impact(strength, seed):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    crunch = smooth(rng.standard_normal(n), 6) * np.exp(-t / 0.09)
    thud = np.sin(2 * np.pi * (75 - 35 * t) * t) * np.exp(-t / 0.2) * 1.4
    clank = np.sin(2 * np.pi * 430 * t) * np.exp(-t / 0.05) * 0.35
    return (crunch + thud + clank) * (0.35 + 0.65 * strength)


def tone(freq, dur, kind="tri", decay=None, vib=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1 + vib * np.sin(2 * np.pi * 6 * t))
    ph = np.cumsum(f) / SR
    if kind == "tri":
        w = 2 * np.abs(2 * (ph % 1) - 1) - 1
    elif kind == "saw":
        w = smooth(2 * (ph % 1) - 1, 6)
    else:
        w = np.sin(2 * np.pi * ph)
    env = np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.03)
    if decay:
        env = env * np.exp(-t / decay)
    return w * env


def synth_fail():
    parts = [tone(f, d, "saw", vib=v) for f, d, v in
             [(392, 0.3, 0), (370, 0.3, 0), (349, 0.3, 0), (330, 0.85, 0.02)]]
    return np.concatenate(parts)


def synth_win():
    notes = [523.25, 659.25, 783.99, 1046.5]
    arp = np.concatenate([tone(f, 0.13, "tri", decay=0.2) for f in notes])
    chord = sum(tone(f, 1.0, "tri", decay=0.5) for f in notes) / 2
    rng = np.random.default_rng(7)
    sparkle = np.zeros(int(1.0 * SR))
    for i in range(10):
        p = tone(rng.uniform(1800, 3200), 0.12, "sine", decay=0.04) * 0.3
        i0 = int(rng.uniform(0, 0.85) * SR)
        sparkle[i0:i0 + len(p)] += p
    return np.concatenate([arp, chord + sparkle])


def synth_whoosh():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    x = np.random.default_rng(3).standard_normal(n)
    band = smooth(x, 3) - smooth(x, 30)
    return band * np.sin(np.pi * t / 0.45) ** 2


def synth_bgm(dur, seed=11):
    rng = np.random.default_rng(seed)
    beat = 60 / 128
    chords = [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)]
    pats = [[0, 1, 2, 1, 0, 1, 2, 1], [2, 1, 0, 1, 2, 2, 1, 0]]
    n = int(dur * SR) + SR
    out = np.zeros(n)

    def add(sig, t0, vol):
        i0 = int(t0 * SR)
        if i0 >= n:
            return
        m = min(len(sig), n - i0)
        out[i0:i0 + m] += sig[:m] * vol

    t, bi = 0.0, 0
    while t < dur:
        ch = chords[bi % 4]
        f = lambda midi: 440 * 2 ** ((midi - 69) / 12)
        for b in range(4):
            add(tone(f(ch[0] - 24), beat * 0.9, "sine", decay=beat * 0.5), t + b * beat, 0.6)
        for e, ci in enumerate(pats[bi % 2]):
            add(tone(f(ch[ci] + 12), beat * 0.45, "tri", decay=0.12), t + e * beat / 2, 0.22)
            m = int(0.03 * SR)
            add(rng.standard_normal(m) * np.exp(-np.arange(m) / SR / 0.008), t + e * beat / 2, 0.08)
        t += 4 * beat
        bi += 1
    return out[:int(dur * SR)]


# ================================================================ drawing helpers
FONT_FACE = "Luckiest Guy"


def detect_font():
    global FONT_FACE
    try:
        out = subprocess.run(["fc-list"], capture_output=True, text=True).stdout
    except FileNotFoundError:
        out = ""
    if "Luckiest Guy" not in out:
        FONT_FACE = "DejaVu Sans"


def set_font(ctx, size):
    bold = cairo.FONT_WEIGHT_BOLD if FONT_FACE == "DejaVu Sans" else cairo.FONT_WEIGHT_NORMAL
    ctx.select_font_face(FONT_FACE, cairo.FONT_SLANT_NORMAL, bold)
    ctx.set_font_size(size)


def draw_text(ctx, s, cx, cy, size, fill=(1, 1, 1), stroke=(0.07, 0.07, 0.2), sw=None,
              max_w=None, alpha=1.0):
    set_font(ctx, size)
    ext = ctx.text_extents(s)
    if max_w and ext.width > max_w:
        size *= max_w / ext.width
        set_font(ctx, size)
        ext = ctx.text_extents(s)
    ctx.new_path()
    ctx.move_to(cx - ext.width / 2 - ext.x_bearing, cy - ext.height / 2 - ext.y_bearing)
    ctx.text_path(s)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(size * 0.16 if sw is None else sw)
    ctx.set_source_rgba(*stroke, alpha)
    ctx.stroke_preserve()
    ctx.set_source_rgba(*fill, alpha)
    ctx.fill()
    return ext.width


def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def poly(ctx, pts):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()


def fill_stroke(ctx, fill, stroke=(0.1, 0.08, 0.12), lw=0.06):
    ctx.set_source_rgb(*fill)
    ctx.fill_preserve()
    ctx.set_source_rgb(*stroke)
    ctx.set_line_width(lw)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()


def ease_out_back(x):
    x = min(1.0, max(0.0, x))
    c1 = 1.70158
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def shade(c, k):
    return tuple(min(1.0, max(0.0, v * k)) for v in c)


# ================================================================ scene
ROCKS = []


def init_scenery():
    rng = np.random.default_rng(5)
    for _ in range(260):
        x = rng.uniform(-30, 160)
        y = rng.uniform(-9, -0.8)
        if any(x0 - 0.4 < x < x1 + 0.4 and y > -d - 0.3 for x0, x1, d in PITS):
            continue
        ROCKS.append((x, y, rng.uniform(0.08, 0.28), rng.uniform(0.75, 0.95)))


def draw_sky(ctx, camx, camy):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.36, 0.7, 1.0)
    g.add_color_stop_rgb(0.6, 0.72, 0.9, 1.0)
    g.add_color_stop_rgb(1, 0.85, 0.95, 1.0)
    ctx.set_source(g)
    ctx.paint()
    # sun
    rg = cairo.RadialGradient(900, 520, 40, 900, 520, 190)
    rg.add_color_stop_rgba(0, 1, 0.95, 0.55, 0.9)
    rg.add_color_stop_rgba(1, 1, 0.95, 0.55, 0)
    ctx.set_source(rg)
    ctx.arc(900, 520, 190, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(1, 0.9, 0.35)
    ctx.arc(900, 520, 70, 0, 2 * math.pi)
    ctx.fill()
    # clouds
    for i in range(7):
        x = (i * 430 - camx * S * 0.12) % (W + 700) - 350
        y = 600 + (i % 3) * 110 + camy * S * 0.1
        ctx.set_source_rgba(1, 1, 1, 0.92)
        for dx, dy, r in [(0, 0, 55), (60, -25, 65), (125, 0, 50), (60, 15, 55)]:
            ctx.arc(x + dx, y + dy, r, 0, 2 * math.pi)
            ctx.fill()
    # hills (two parallax layers)
    ground_sy = GROUND_Y + camy * S
    for par, base, col, a1, a2 in [(0.2, -260, (0.56, 0.8, 0.52), 90, 45),
                                   (0.45, -150, (0.42, 0.72, 0.38), 70, 35)]:
        ctx.new_path()
        ctx.move_to(0, H)
        for sx in range(0, W + 21, 20):
            wx = sx + camx * S * par
            y = ground_sy + base - camy * S * (1 - par) * 0.5 - a1 * math.sin(wx / 260) - a2 * math.sin(wx / 113 + 1)
            ctx.line_to(sx, y)
        ctx.line_to(W, H)
        ctx.close_path()
        ctx.set_source_rgb(*col)
        ctx.fill()


def draw_track(ctx, camx):
    view0, view1 = camx - 12, camx + 12
    # pit backdrops
    for x0, x1, d in PITS:
        ctx.rectangle(x0, -d, x1 - x0, d)
        ctx.set_source_rgb(0.28, 0.17, 0.1)
        ctx.fill()
    # ground body
    pts = track_points()
    poly(ctx, pts + [(170, -40), (-40, -40)])
    ctx.set_source_rgb(0.58, 0.38, 0.22)
    ctx.fill()
    # soil strata below the pits
    for depth, col in [(-6.0, (0.5, 0.32, 0.18)), (-8.0, (0.44, 0.27, 0.15)), (-10.5, (0.52, 0.5, 0.5))]:
        ctx.new_path()
        ctx.move_to(view0 - 2, -40)
        x = view0 - 2
        while x <= view1 + 2:
            ctx.line_to(x, depth + 0.35 * math.sin(x * 0.7) + 0.2 * math.sin(x * 1.9 + depth))
            x += 0.5
        ctx.line_to(view1 + 2, -40)
        ctx.close_path()
        ctx.set_source_rgb(*col)
        ctx.fill()
    for x, y, r, k in ROCKS:
        if view0 - 1 < x < view1 + 1:
            ctx.arc(x, y, r, 0, 2 * math.pi)
            ctx.set_source_rgb(0.58 * k, 0.38 * k, 0.22 * k)
            ctx.fill()
    # mud in pits
    for x0, x1, d in PITS:
        ctx.rectangle(x0, -d, x1 - x0, 0.55)
        ctx.set_source_rgb(0.4, 0.26, 0.13)
        ctx.fill()
        for j in range(int((x1 - x0) / 0.8)):
            ctx.arc(x0 + 0.4 + j * 0.8, -d + 0.55, 0.22, 0, math.pi)
            ctx.fill()
    # asphalt road on flat top segments
    for a, b in zip(pts, pts[1:]):
        if a[1] < -0.01 or b[1] < -0.01 or abs(a[0] - b[0]) < 1e-6 or b[1] > 0.01 or a[1] > 0.01:
            continue
        poly(ctx, [a, b, (b[0], b[1] - 0.55), (a[0], a[1] - 0.55)])
        ctx.set_source_rgb(0.26, 0.26, 0.3)
        ctx.fill()
        ctx.set_source_rgb(0.4, 0.4, 0.45)
        ctx.rectangle(a[0], -0.08, b[0] - a[0], 0.08)
        ctx.fill()
        ctx.set_source_rgb(1, 1, 1)
        x = math.ceil(a[0] / 3.0) * 3.0
        while x + 1.5 <= b[0]:
            ctx.rectangle(x, -0.33, 1.5, 0.09)
            ctx.fill()
            x += 3.0
    # broken asphalt edges at pit lips
    for x0, x1, d in PITS:
        for xe, sgn in [(x0, -1), (x1, 1)]:
            if abs(xe - RAMP[1]) < 1e-6:
                continue
            poly(ctx, [(xe, 0), (xe, -0.55), (xe + sgn * 0.25, -0.35), (xe + sgn * 0.12, -0.2),
                       (xe + sgn * 0.3, 0)])
            ctx.set_source_rgb(0.28, 0.17, 0.1)
            ctx.fill()
    # wooden ramp
    rx0, rx1, rh = RAMP
    poly(ctx, [(rx0, 0), (rx1, rh), (rx1, 0)])
    fill_stroke(ctx, (0.85, 0.58, 0.28), lw=0.07)
    ctx.set_source_rgb(0.6, 0.38, 0.16)
    ctx.set_line_width(0.05)
    for i in range(1, 6):
        x = rx0 + (rx1 - rx0) * i / 6
        ctx.move_to(x, 0)
        ctx.line_to(x, rh * i / 6)
        ctx.stroke()
    # warning signs
    for x in [PITS[0][0] - 3, RAMP[0] - 2.5, PITS[2][0] - 3]:
        ctx.rectangle(x - 0.07, 0, 0.14, 2.0)
        ctx.set_source_rgb(0.45, 0.45, 0.5)
        ctx.fill()
        poly(ctx, [(x, 1.7), (x + 0.6, 2.3), (x, 2.9), (x - 0.6, 2.3)])
        fill_stroke(ctx, (1, 0.82, 0.1), lw=0.08)
        ctx.set_source_rgb(0.1, 0.1, 0.1)
        ctx.rectangle(x - 0.06, 2.2, 0.12, 0.45)
        ctx.fill()
        ctx.arc(x, 2.05, 0.07, 0, 2 * math.pi)
        ctx.fill()
    # finish arch
    fx = FINISH_X
    for px in (fx - 1.3, fx + 1.3):
        ctx.rectangle(px - 0.1, 0, 0.2, 4.6)
        ctx.set_source_rgb(0.9, 0.9, 0.92)
        ctx.fill()
    for i in range(12):
        for j in range(2):
            ctx.rectangle(fx - 1.5 + i * 0.25, 3.9 + j * 0.35, 0.25, 0.35)
            ctx.set_source_rgb(*(((0.08,) * 3) if (i + j) % 2 else (1, 1, 1)))
            ctx.fill()
    for i in range(3):
        for j in range(2):
            ctx.rectangle(fx - 0.3 + j * 0.3, -0.55 + i * 0.18, 0.3, 0.18)
            ctx.set_source_rgb(*(((0.08,) * 3) if (i + j) % 2 else (1, 1, 1)))
            ctx.fill()


def draw_eyes(ctx, pts, r, dead):
    for ex, ey in pts:
        ctx.save()
        ctx.translate(ex, ey)
        ctx.scale(1, 1.25)
        ctx.arc(0, 0, r, 0, 2 * math.pi)
        ctx.restore()
        fill_stroke(ctx, (1, 1, 1), lw=r * 0.25)
        ctx.set_source_rgb(0.05, 0.05, 0.1)
        if dead:
            ctx.set_line_width(r * 0.35)
            for s in (1, -1):
                ctx.move_to(ex - r * 0.6, ey - s * r * 0.6)
                ctx.line_to(ex + r * 0.6, ey + s * r * 0.6)
                ctx.stroke()
        else:
            ctx.arc(ex + r * 0.35, ey + r * 0.1, r * 0.5, 0, 2 * math.pi)
            ctx.fill()
            ctx.set_source_rgb(1, 1, 1)
            ctx.arc(ex + r * 0.5, ey + r * 0.3, r * 0.16, 0, 2 * math.pi)
            ctx.fill()


def local_text(ctx, s, x, y, size, color):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, -1)
    set_font(ctx, size)
    ext = ctx.text_extents(s)
    ctx.move_to(-ext.width / 2 - ext.x_bearing, -ext.height / 2 - ext.y_bearing)
    ctx.set_source_rgb(*color)
    ctx.show_text(s)
    ctx.restore()


def draw_body(ctx, vk, v, dead):
    c = v["color"]
    dark = shade(c, 0.65)
    glass = (0.62, 0.86, 1.0)
    if vk == "sports":
        poly(ctx, [(-1.3, 0.31), (0.5, 0.31), (-0.1, 0.85), (-1.0, 0.85)])
        fill_stroke(ctx, c)
        poly(ctx, [(-1.15, 0.36), (0.32, 0.36), (-0.15, 0.76), (-0.95, 0.76)])
        fill_stroke(ctx, glass, lw=0.03)
        poly(ctx, [(-2.1, -0.31), (2.1, -0.31), (2.1, -0.05), (1.6, 0.2), (0.6, 0.31), (-2.0, 0.31), (-2.1, 0.1)])
        fill_stroke(ctx, c)
        ctx.rectangle(-1.9, -0.06, 3.7, 0.1)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        poly(ctx, [(-2.05, 0.31), (-1.85, 0.31), (-1.9, 0.52), (-2.05, 0.52)])
        fill_stroke(ctx, dark, lw=0.04)
        poly(ctx, [(-2.35, 0.5), (-1.65, 0.5), (-1.65, 0.6), (-2.35, 0.6)])
        fill_stroke(ctx, dark, lw=0.04)
        ctx.arc(1.95, -0.02, 0.1, 0, 2 * math.pi)
        fill_stroke(ctx, (1, 0.95, 0.4), lw=0.03)
        draw_eyes(ctx, [(-0.75, 0.56), (-0.35, 0.56)], 0.13, dead)
    elif vk == "bus":
        rrect(ctx, -3.7, -1.05, 7.4, 2.1, 0.3)
        fill_stroke(ctx, c, lw=0.08)
        ctx.rectangle(-3.7, -0.35, 7.4, 0.14)
        ctx.set_source_rgb(0.1, 0.1, 0.1)
        ctx.fill()
        for i in range(6):
            rrect(ctx, -3.3 + i * 0.95, 0.12, 0.78, 0.7, 0.1)
            fill_stroke(ctx, glass, lw=0.05)
        rrect(ctx, 2.55, -0.05, 0.95, 0.9, 0.12)
        fill_stroke(ctx, glass, lw=0.05)
        local_text(ctx, "SCHOOL BUS", -0.5, -0.7, 0.42, (0.1, 0.1, 0.1))
        ctx.rectangle(3.62, -1.0, 0.18, 0.35)
        ctx.rectangle(-3.8, -1.0, 0.18, 0.35)
        ctx.set_source_rgb(0.15, 0.15, 0.15)
        ctx.fill()
        ctx.arc(3.55, -0.55, 0.12, 0, 2 * math.pi)
        fill_stroke(ctx, (1, 0.95, 0.4), lw=0.03)
        draw_eyes(ctx, [(2.8, 0.42), (3.22, 0.42)], 0.16, dead)
    else:
        poly(ctx, [(-1.5, 0.45), (0.4, 0.45), (0.0, 1.35), (-1.3, 1.35)])
        fill_stroke(ctx, c, lw=0.07)
        poly(ctx, [(-1.35, 0.52), (0.22, 0.52), (-0.08, 1.25), (-1.2, 1.25)])
        fill_stroke(ctx, glass, lw=0.04)
        poly(ctx, [(-2.15, -0.45), (2.15, -0.45), (2.15, 0.2), (1.9, 0.45), (-2.15, 0.45)])
        fill_stroke(ctx, c, lw=0.07)
        poly(ctx, [(0.3, -0.25), (1.2, -0.3), (0.9, -0.1), (1.9, -0.05), (1.1, 0.1), (1.6, 0.3), (0.3, 0.2)])
        fill_stroke(ctx, (1, 0.6, 0.1), stroke=(0.9, 0.2, 0.1), lw=0.04)
        for i in range(3):
            ctx.rectangle(-1.2 + i * 0.35, 1.35, 0.25, 0.14)
            ctx.set_source_rgb(1, 0.85, 0.2)
            ctx.fill()
        ctx.arc(2.02, 0.05, 0.12, 0, 2 * math.pi)
        fill_stroke(ctx, (1, 0.95, 0.4), lw=0.03)
        draw_eyes(ctx, [(-0.8, 0.9), (-0.35, 0.9)], 0.16, dead)


def draw_wheel(ctx, x, y, ang, r, monster):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.set_source_rgb(0.12, 0.12, 0.14)
    ctx.fill()
    if monster:
        ctx.set_source_rgb(0.2, 0.2, 0.22)
        for i in range(18):
            ctx.save()
            ctx.rotate(i * 2 * math.pi / 18)
            ctx.rectangle(r * 0.86, -r * 0.07, r * 0.2, r * 0.14)
            ctx.fill()
            ctx.restore()
    ctx.arc(0, 0, r * 0.55, 0, 2 * math.pi)
    fill_stroke(ctx, (0.78, 0.78, 0.84), lw=r * 0.06)
    ctx.set_source_rgb(0.35, 0.35, 0.4)
    ctx.set_line_width(r * 0.1)
    for i in range(5):
        a = i * 2 * math.pi / 5
        ctx.move_to(math.cos(a) * r * 0.15, math.sin(a) * r * 0.15)
        ctx.line_to(math.cos(a) * r * 0.5, math.sin(a) * r * 0.5)
        ctx.stroke()
    ctx.arc(0, 0, r * 0.16, 0, 2 * math.pi)
    ctx.set_source_rgb(0.25, 0.25, 0.3)
    ctx.fill()
    ctx.restore()


def draw_car(ctx, vk, v, st, dead):
    cx, cy, ca, wheels = st
    bh = v["body"][1]
    ctx.set_source_rgb(0.3, 0.3, 0.34)
    ctx.set_line_width(0.14)
    for (wx, wy, _), lx in zip(wheels, v["wheel_x"]):
        ax = cx + math.cos(ca) * lx - math.sin(ca) * (-bh / 2)
        ay = cy + math.sin(ca) * lx + math.cos(ca) * (-bh / 2)
        ctx.move_to(ax, ay)
        ctx.line_to(wx, wy)
        ctx.stroke()
    for wx, wy, wa in wheels:
        draw_wheel(ctx, wx, wy, wa, v["wheel_r"], vk == "monster")
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(ca)
    draw_body(ctx, vk, v, dead)
    ctx.restore()


def draw_dust(ctx, impacts, t):
    for ti, s, x, y in impacts:
        p = (t - ti) / 0.7
        if 0 <= p < 1:
            for j in range(6):
                a = j * math.pi / 5
                rad = (0.3 + 1.3 * p) * (0.6 + 0.4 * s)
                ctx.arc(x + math.cos(a) * rad * 1.4, y - 0.6 + abs(math.sin(a)) * rad * 0.7, rad * 0.6,
                        0, 2 * math.pi)
                ctx.set_source_rgba(0.85, 0.75, 0.6, 0.55 * (1 - p))
                ctx.fill()


# ================================================================ HUD
def draw_badge(ctx, kind, age):
    s = ease_out_back(age / 0.3) * (1 + 0.03 * math.sin(age * 8))
    ctx.save()
    ctx.translate(540, 770)
    ctx.scale(s, s)
    if kind == "win":
        ctx.save()
        ctx.rotate(age * 0.8)
        for i in range(16):
            ctx.rotate(2 * math.pi / 16)
            poly(ctx, [(0, 0), (380, -40), (380, 40)])
            ctx.set_source_rgba(1, 0.9, 0.3, 0.35 if i % 2 else 0.18)
            ctx.fill()
        ctx.restore()
        rrect(ctx, -330, -105, 660, 210, 40)
        ctx.set_source_rgb(1, 0.76, 0.08)
        ctx.fill_preserve()
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(12)
        ctx.stroke()
        draw_text(ctx, "WINNER!", 0, 0, 140, fill=(1, 1, 1), stroke=(0.55, 0.25, 0.0), max_w=600)
    else:
        ctx.rotate(-0.08)
        rrect(ctx, -270, -100, 540, 200, 40)
        ctx.set_source_rgb(0.9, 0.1, 0.15)
        ctx.fill_preserve()
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(12)
        ctx.stroke()
        draw_text(ctx, "FAIL!", 0, 0, 150, fill=(1, 1, 1), stroke=(0.4, 0.0, 0.05))
    ctx.restore()


def draw_confetti(ctx, age, seed=21):
    rng = np.random.default_rng(seed)
    cols = [(1, 0.3, 0.3), (1, 0.85, 0.2), (0.3, 0.8, 1), (0.5, 1, 0.4), (1, 0.5, 1)]
    for i in range(170):
        x0, vy, sway, delay = rng.uniform(0, W), rng.uniform(250, 520), rng.uniform(20, 70), rng.uniform(0, 1.2)
        a = age - delay
        if a < 0:
            continue
        y = -40 + vy * a
        if y > 1400:
            continue
        x = x0 + sway * math.sin(a * 3 + i)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(a * 5 + i)
        ctx.rectangle(-9, -5, 18, 10)
        ctx.set_source_rgb(*cols[i % len(cols)])
        ctx.fill()
        ctx.restore()


def draw_hud(ctx, L, li, t, gt):
    # title (whole video), pops at the very start
    ts = 1.0 + 0.25 * (1 - ease_out_back(gt / 0.5)) if gt < 0.5 else 1.0
    ctx.save()
    ctx.translate(540, 215)
    ctx.scale(ts, ts)
    draw_text(ctx, TITLE, 0, 0, 84, fill=(1, 0.86, 0.12), max_w=980)
    ctx.restore()
    # level banner
    s = ease_out_back(t / 0.35)
    col = LEVEL_COLORS[li]
    ctx.save()
    ctx.translate(540, 335)
    ctx.scale(s, s)
    rrect(ctx, -170, -48, 340, 96, 48)
    ctx.set_source_rgb(*col)
    ctx.fill_preserve()
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(7)
    ctx.stroke()
    draw_text(ctx, f"LEVEL {li + 1}", 0, 0, 62)
    ctx.restore()
    draw_text(ctx, L["v"]["name"].upper(), 540, 440, 58, max_w=900, alpha=min(1.0, t / 0.3))
    if li == 0 and gt < 2.6:
        pulse = 1 + 0.06 * math.sin(gt * 9)
        ctx.save()
        ctx.translate(540, 640)
        ctx.scale(pulse, pulse)
        draw_text(ctx, "WHO WILL MAKE IT?", 0, 0, 70, fill=(1, 1, 1), stroke=(0.85, 0.1, 0.2),
                  alpha=min(1.0, (2.6 - gt) / 0.3))
        ctx.restore()
    # progress bar
    k = min(int(t * FPS), len(L["rec"]["cx"]) - 1)
    frac = (L["rec"]["cx"][k] - START_X) / (FINISH_X - START_X)
    frac = min(1.0, max(0.0, frac))
    x0, x1, y = 110, 960, 540
    rrect(ctx, x0 - 10, y - 18, x1 - x0 + 20, 36, 18)
    ctx.set_source_rgba(0.05, 0.05, 0.15, 0.55)
    ctx.fill()
    rrect(ctx, x0, y - 9, max(18, (x1 - x0) * frac), 18, 9)
    ctx.set_source_rgb(*col)
    ctx.fill()
    for px0, px1, _ in PITS:
        px = x0 + (x1 - x0) * ((px0 + px1) / 2 - START_X) / (FINISH_X - START_X)
        poly(ctx, [(px, y - 30), (px - 14, y - 52), (px + 14, y - 52)])
        ctx.set_source_rgb(0.95, 0.2, 0.2)
        ctx.fill()
    for i in range(4):
        for j in range(4):
            ctx.rectangle(x1 + 8 + i * 9, y - 48 + j * 9, 9, 9)
            ctx.set_source_rgb(*(((0.05,) * 3) if (i + j) % 2 else (1, 1, 1)))
            ctx.fill()
    ctx.arc(x0 + (x1 - x0) * frac, y, 20, 0, 2 * math.pi)
    ctx.set_source_rgb(*L["v"]["color"])
    ctx.fill_preserve()
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(5)
    ctx.stroke()
    # outcome badge / confetti / outro
    ev = L["event"]
    badge_t = ev["t"] - 0.2
    outro_t = L.get("outro_t")
    if ev["type"] == "win" and t >= ev["t"]:
        draw_confetti(ctx, t - ev["t"])
    if t >= badge_t and (outro_t is None or t < outro_t + 0.3):
        ctx.push_group()
        draw_badge(ctx, "win" if ev["type"] == "win" else "fail", t - badge_t)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1.0 if outro_t is None else max(0.0, min(1.0, (outro_t + 0.3 - t) / 0.3)))
    if outro_t is not None and t >= outro_t:
        a = t - outro_t
        s = ease_out_back(a / 0.4)
        ctx.save()
        ctx.translate(540, 820)
        ctx.scale(s, s)
        rrect(ctx, -440, -210, 880, 420, 50)
        ctx.set_source_rgba(1, 1, 1, 0.94)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.1, 0.1, 0.25)
        ctx.set_line_width(8)
        ctx.stroke()
        draw_text(ctx, "DID YOU ENJOY IT?", 0, -135, 62, fill=(1, 0.86, 0.12), max_w=800)
        p = 1 + 0.06 * math.sin(a * 7)
        for bx, label, colr, ph in [(-215, "LIKE", (0.15, 0.5, 1.0), 0), (190, "SUBSCRIBE", (0.9, 0.1, 0.15), 1.5)]:
            ctx.save()
            ctx.translate(bx, 10)
            q = 1 + 0.07 * math.sin(a * 7 + ph)
            ctx.scale(q, q)
            w = 330 if label == "LIKE" else 420
            rrect(ctx, -w / 2, -58, w, 116, 58)
            ctx.set_source_rgb(*colr)
            ctx.fill()
            draw_text(ctx, label, 0, 0, 64, max_w=w - 50)
            ctx.restore()
        ctx.save()
        ctx.scale(p, p)
        draw_text(ctx, "MEGAWHEEL KIDS", 0, 140, 58, fill=(1, 1, 1), stroke=(0.1, 0.1, 0.3))
        ctx.restore()
        ctx.restore()


# ================================================================ frames
LEVELS = []
INDEX = []          # global frame -> (level, local frame)
STARTS = []


def draw_frame(ctx, g):
    li, k = INDEX[g]
    L = LEVELS[li]
    rec = L["rec"]
    k = min(k, len(rec["cx"]) - 1)
    t = k / FPS
    camx, camy = L["cam"][k]
    draw_sky(ctx, camx, camy)
    ctx.save()
    ctx.translate(540, GROUND_Y)
    ctx.scale(S, -S)
    ctx.translate(-camx, -camy)
    draw_track(ctx, camx)
    draw_dust(ctx, L["impacts"], t)
    dead = L["event"]["type"] != "win" and t >= L["event"]["t"]
    draw_car(ctx, L["vk"], L["v"], (rec["cx"][k], rec["cy"][k], rec["ca"][k], rec["wheels"][k]), dead)
    ctx.restore()
    draw_hud(ctx, L, li, t, g / FPS)


def render_chunk(args):
    a, b, path = args
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "19", "-pix_fmt", "yuv420p", "-threads", "2", path], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    for g in range(a, b):
        ctx = cairo.Context(surf)
        draw_frame(ctx, g)
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
    p.stdin.close()
    return p.wait()


def save_png(g, path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    draw_frame(cairo.Context(surf), g)
    surf.write_to_png(path)


# ================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--preview-only", action="store_true", help="render PNG previews, no MP4")
    args = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    detect_font()
    init_scenery()
    rng = np.random.default_rng(args.seed)
    t0 = time.time()
    print(f"[font] {FONT_FACE}", flush=True)

    intros = [tts(VEHICLES[vk]["intro"]) for vk, _ in STORY]
    runs = choose_runs(rng, [len(x) / SR for x in intros])
    outcome_lines = [WIN_LINE if r["event"]["type"] == "win" else FAIL_LINES[r["event"]["type"]] for r in runs]
    outcomes = [tts(s) for s in outcome_lines]
    cta = tts(CTA)
    print(f"[sim] done in {time.time() - t0:.1f}s", flush=True)

    # timeline
    gstart = 0.0
    for li, ((vk, _), run) in enumerate(zip(STORY, runs)):
        ev = run["event"]
        od = len(outcomes[li]) / SR
        L = dict(vk=vk, v=VEHICLES[vk], rec=run["rec"], impacts=run["impacts"], event=ev,
                 cam=camera_track(run["rec"]), start=gstart, speed=run["speed"])
        if ev["type"] == "win":
            L["outro_t"] = ev["t"] + od + 0.5
            dur = L["outro_t"] + len(cta) / SR + 1.0
        else:
            dur = ev["t"] + max(2.0, od + 0.7)
        dur = max(dur, len(intros[li]) / SR + 0.5)
        dur = min(dur, (len(run["rec"]["cx"]) - 1) / FPS)
        L["dur"] = dur
        nf = int(round(dur * FPS))
        INDEX.extend((li, k) for k in range(nf))
        LEVELS.append(L)
        gstart += nf / FPS
    total = len(INDEX) / FPS
    print(f"[timeline] {total:.1f}s, {len(INDEX)} frames", flush=True)

    # audio
    n = int(total * SR) + 1
    narr, eng, sfx = np.zeros(n), np.zeros(n), np.zeros(n)

    def place(buf, sig, t, gain=1.0):
        i0 = int(t * SR)
        if i0 >= n:
            return
        m = min(len(sig), n - i0)
        buf[i0:i0 + m] += sig[:m] * gain

    for li, L in enumerate(LEVELS):
        st, ev = L["start"], L["event"]
        nf = int(round(L["dur"] * FPS))
        wrel = L["rec"]["wrel"][:nf]
        tt = np.arange(nf) / FPS
        amp = 0.55 + 0.45 * np.minimum(1, wrel / (L["speed"] / L["v"]["wheel_r"]))
        if ev["type"] == "win":
            amp = np.where(tt > ev["t"], np.maximum(0.35, amp * np.clip(1 - (tt - ev["t"]) / 3, 0, 1)), amp)
        else:
            amp = amp * np.clip(1 - (tt - ev["t"]) / 0.8, 0, 1)
        base, kk = L["v"]["engine"]
        place(eng, synth_engine(wrel, amp, base, kk, seed=li), st)
        place(sfx, synth_whoosh(), st, 0.5)
        for j, (ti, s, _, _) in enumerate(L["impacts"]):
            if ti < L["dur"]:
                place(sfx, synth_impact(s, seed=100 + j), st + ti, 0.9)
        place(narr, intros[li], st + 0.15)
        place(narr, outcomes[li], st + ev["t"] + 0.25)
        if ev["type"] == "win":
            place(sfx, synth_win(), st + ev["t"], 0.9)
            place(narr, cta, st + L["outro_t"])
        else:
            place(sfx, synth_fail(), st + ev["t"] + 0.1, 0.75)
    bgm = synth_bgm(total)
    mix = (peak(narr) * VOL_NARR + peak(eng) * VOL_ENGINE + peak(bgm[:n] if len(bgm) >= n else np.pad(bgm, (0, n - len(bgm)))) * VOL_BGM
           + peak(sfx) * VOL_SFX)
    mix = np.tanh(1.3 * mix) / np.tanh(1.3)
    mix = mix / max(1e-9, np.max(np.abs(mix))) * 0.95
    wav_path = f"{WORK}/mix_{args.seed}.wav"
    write_wav(wav_path, mix)

    name = f"SIM_POTHOLES_S{args.seed:03d}"
    prev_dir = f"{OUT_DIR}/{name}_preview"
    os.makedirs(prev_dir, exist_ok=True)
    marks = []
    for li, L in enumerate(LEVELS):
        g0 = int(round(L["start"] * FPS))
        marks += [(f"L{li + 1}_start", g0 + 20), (f"L{li + 1}_event", g0 + int((L["event"]["t"] + 0.4) * FPS))]
        if L.get("outro_t"):
            marks.append(("outro", g0 + int((L["outro_t"] + 1.0) * FPS)))
    for label, g in marks:
        save_png(min(g, len(INDEX) - 1), f"{prev_dir}/{label}.png")
    print(f"[preview] {prev_dir}", flush=True)

    manifest = dict(
        video_id=name, status="RENDERED_PENDING_APPROVAL", seed=args.seed, duration=round(total, 2),
        title="Cars VS Giant Potholes! 🚗💥 Who Makes It? #Shorts",
        description=("Which car can survive the GIANT potholes? 🚗💥 Red sports car, yellow school bus, or "
                     "monster truck? Watch till the end! 🏁\n\n#Shorts #Cars #MonsterTruck #KidsVideos #MegaWheelKids"),
        tags=["cars", "monster truck", "school bus", "potholes", "kids", "shorts", "physics", "MegaWheel Kids"],
        levels=[dict(vehicle=L["v"]["name"], speed=round(L["speed"], 2), outcome=L["event"]["type"],
                     event_t=round(L["event"]["t"], 2), obstacle=L["event"]["obstacle"], start=round(L["start"], 2),
                     duration=round(L["dur"], 2)) for L in LEVELS],
        narration=[VEHICLES[vk]["intro"] for vk, _ in STORY] + outcome_lines + [CTA],
        assets="100% procedurally generated (pymunk physics + cairo render + synthesized audio), narration Edge-TTS "
               + VOICE,
    )
    with open(f"{OUT_DIR}/{name}.json", "w") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    if args.preview_only:
        print(json.dumps(manifest["levels"], indent=1))
        return

    t1 = time.time()
    nw = max(1, args.workers)
    bounds = np.linspace(0, len(INDEX), nw + 1).astype(int)
    parts = [(int(bounds[i]), int(bounds[i + 1]), f"{WORK}/{name}_part{i}.mp4") for i in range(nw)]
    with mp.get_context("fork").Pool(nw) as pool:
        codes = pool.map(render_chunk, parts)
    if any(codes):
        raise RuntimeError(f"ffmpeg chunk failed: {codes}")
    lst = f"{WORK}/{name}_parts.txt"
    with open(lst, "w") as fh:
        fh.writelines(f"file '{p}'\n" for _, _, p in parts)
    out = f"{OUT_DIR}/{name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav_path,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out],
                   check=True)
    for _, _, p in parts:
        os.remove(p)
    print(f"[render] {len(INDEX)} frames in {time.time() - t1:.1f}s -> {out}", flush=True)
    print(json.dumps(manifest["levels"], indent=1))


if __name__ == "__main__":
    main()
