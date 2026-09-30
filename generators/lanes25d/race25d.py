#!/usr/bin/env python3
"""MegaWheel Arena — series "race25d": 2.5D "paper cutout" lane race Shorts (approved style, user 2026-09-30).

The characters are drawn by the SAME functions as the 2D episodes (sim_engine.draw_body / draw_face /
draw_wheel, moods, themes, speed lines, splash, READY-GO, confetti, replay overlay), so they look exactly
like the 2D cast. Depth comes from lanes; far lanes are smaller and higher, dashes/props move with parallax.

Every seed varies: cast (rotation: fewest appearances first), lanes, puddle + ramp placement, speeds (so the
winner varies), theme (rotation) and narrator (en-US rotation). Timeline: READY-GO -> race (hydroplane spin
across lanes + bump, ramp jump in slow-mo) -> winner + confetti -> INSTANT REPLAY of the spin -> CTA.
Audio: narration without overlaps, engine, beeps, splash/spin/impact/landing, win fanfare, rewind, themed
music with ducking (all synth functions from sim_engine).

Usage (cd /root/video-engine):
  ./venv/bin/python generators/lanes25d/race25d.py --seed 1               # -> renders/megawheel_arena/pending/
  ./venv/bin/python generators/lanes25d/race25d.py --seed 1 --preview-only # -> work/lanes25d/previews/ (no registry)
Exit codes: 0 ok · 1 duplicate / STOP · 5 checks failed.
"""
import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time

import cairo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "physics_2d"))
import registry  # noqa: E402
import sim_engine as se  # noqa: E402

SERIES, ENGINE_VERSION = "race25d", "v1"
W, H, FPS = se.W, se.H, 30
F_PERSP, D0, LANE_D = 9000.0, 100.0, 25.0        # k(z) = F / (D0 + z*LANE_D): front lane 90 px/m, lane 3 ≈ 51
Y_H, CAM_H = 640.0, 13.0                         # ground_y = Y_H + CAM_H*k
WORLD_DY = -260.0                                # lift the road scene so the action sits mid-frame
POOL = ["sports", "police", "taxi", "f1", "bus", "firetruck", "icecream", "bigrig", "monster", "monster2"]
BIG = {"bus", "firetruck", "icecream", "bigrig"}
TITLES = ["4 Cars, 1 Finish Line! Who Wins? 🏁", "Slippery Race Showdown! Who Wins? 🏁💦",
          "Crazy Lane Race! Who Crosses First? 🏁", "Big Jump, Big Spin! Who Wins the Race? 🏁"]
TAGS = ["cars", "car race", "racing", "cartoon cars", "race cars", "funny cars", "shorts", "MegaWheel Arena"]

# per-video parameters (set in setup())
RACERS, PUD_X, PUD_LANE, RAMP_X, RAMP_LANE, FIN_X, SECONDS = [], 0.0, 1, 0.0, 3, 0.0, 0.0


def k_of(z):
    return F_PERSP / (D0 + z * LANE_D)


def ground_y(z):
    return Y_H + CAM_H * k_of(z)


def ease_out(p):
    return 1 - (1 - p) ** 2.2


def nick(vk):
    return se.VEHICLES[vk]["nick"]


# ------------------------------------------------------------------ per-seed setup
def setup(seed, appearances):
    global RACERS, PUD_X, PUD_LANE, RAMP_X, RAMP_LANE, FIN_X, SECONDS
    r = np.random.default_rng(8000 + seed)
    tie = {vk: float(r.random()) for vk in POOL}
    order = sorted(POOL, key=lambda vk: (appearances.get(vk, 0), tie[vk]))
    cast, bigs = [], 0
    for vk in order:                                             # max 1 big vehicle, max 1 monster truck
        if vk in BIG and bigs >= 1:
            continue
        if vk.startswith("monster") and any(c.startswith("monster") for c in cast):
            continue
        cast.append(vk)
        bigs += vk in BIG
        if len(cast) == 4:
            break
    lanes = [int(v) for v in r.permutation(4)]
    base = r.uniform(22.6, 23.6, 4)
    RACERS = [(vk, lanes[i], float(base[i])) for i, vk in enumerate(cast)]
    PUD_LANE = int(r.integers(0, 4))
    RAMP_LANE = int(r.choice([z for z in range(4) if z != PUD_LANE]))
    PUD_X = float(r.uniform(115, 140))
    RAMP_X = float(PUD_X + r.uniform(85, 110))
    FIN_X = float(RAMP_X + r.uniform(95, 125))
    SECONDS = FIN_X / 21.0 + 4.0
    return dict(cast=cast, lanes=lanes, puddle=[PUD_LANE, round(PUD_X, 1)], ramp=[RAMP_LANE, round(RAMP_X, 1)],
                finish=round(FIN_X, 1))


# ------------------------------------------------------------------ scripted race (120 Hz kinematics)
def simulate(seed):
    rng = np.random.default_rng(9100 + seed)
    dt, n = 1 / 120, int(SECONDS * 120)
    cars = []
    for key, lane, v in RACERS:
        cars.append(dict(key=key, lane=lane, v0=v, x=4.0 - lane * 1.2, z=float(lane), h=0.0, vh=0.0, yaw=0.0,
                         pitch=0.0, v=0.0, spin_t=None, jump_t=None, land_t=None, bump_t=None, finish=None,
                         surge=float(rng.uniform(0, 6.28)), rec=[]))
    events = []
    to_lane = PUD_LANE - 1 if PUD_LANE > 0 else 1                # the spinner slides one lane (towards camera)
    for i in range(n):
        t = i * dt
        for c in cars:
            go = min(1.0, t / 1.6)
            target = c["v0"] * (1 + 0.025 * math.sin(t * 0.7 + c["surge"]))
            if c["spin_t"] is not None:
                target *= 0.55 + 0.45 * min(1.0, max(0.0, (t - c["spin_t"] - 1.2) / 2.5))
            if c["land_t"] is not None and t - c["land_t"] < 2.5:
                target *= 1.1
            if c["bump_t"] is not None and 0 < t - c["bump_t"] < 1.0:
                target *= 0.9
            if c["finish"] is not None:
                target = max(4.0, c["v"] * 0.985)
            c["v"] += (target * go - c["v"]) * 0.03
            c["x"] += c["v"] * dt
            if c["lane"] == PUD_LANE and c["spin_t"] is None and PUD_X - 2 < c["x"] < PUD_X + 5:
                c["spin_t"] = t
                events.append(("splash", t, c["x"], float(PUD_LANE)))
            if c["spin_t"] is not None:
                p = min(1.0, (t - c["spin_t"]) / 1.4)
                c["yaw"] = 4 * math.pi * ease_out(p)
                c["z"] = PUD_LANE + (to_lane - PUD_LANE) * 0.55 * ease_out(min(1.0, (t - c["spin_t"]) / 1.0))
            if c["lane"] == RAMP_LANE and c["jump_t"] is None and c["x"] >= RAMP_X:
                c["jump_t"], c["vh"] = t, 9.2
                events.append(("takeoff", t, c["x"], float(RAMP_LANE)))
            if c["jump_t"] is not None and c["land_t"] is None:
                c["vh"] -= 9.81 * dt
                c["h"] = max(0.0, c["h"] + c["vh"] * dt)
                c["pitch"] = float(np.clip(c["vh"] * 0.035, -0.28, 0.28))
                if c["h"] == 0.0 and c["vh"] < 0:
                    c["land_t"], c["pitch"] = t, 0.0
                    events.append(("land", t, c["x"], float(RAMP_LANE)))
            if c["finish"] is None and c["x"] >= FIN_X:
                c["finish"] = t
            if i % 4 == 0:
                c["rec"].append((c["x"], c["z"], c["h"], c["yaw"], c["pitch"], c["v"]))
        sp = next((c for c in cars if c["spin_t"] is not None and t - c["spin_t"] < 1.2), None)
        if sp:
            for c in cars:
                if c is not sp and c["lane"] == to_lane and c["bump_t"] is None and abs(c["x"] - sp["x"]) < 5 \
                        and abs(sp["z"] - to_lane) < 0.75:
                    c["bump_t"] = t
                    events.append(("bump", t, c["x"], float(to_lane)))
        for c in cars:
            if c["bump_t"] is not None:
                a = t - c["bump_t"]
                side = -1 if to_lane == 0 else 1
                c["z"] = c["lane"] + side * 0.28 * math.sin(min(math.pi, a * 2.6)) if a < 1.3 else float(c["lane"])
    for place, c in enumerate(sorted(cars, key=lambda c: c["finish"] if c["finish"] else 1e9), start=1):
        c["place"] = place
    return cars, events


# ------------------------------------------------------------------ timeline: race -> celebrate -> replay -> CTA
def build_timeline(cars):
    winner = min(cars, key=lambda c: c["finish"] or 1e9)
    jumper = next((c for c in cars if c["jump_t"] is not None), None)
    spinner = next((c for c in cars if c["spin_t"] is not None), None)
    frames, t = [], 0.0
    race_end = min(SECONDS - 0.2, (winner["finish"] or SECONDS) + 1.8)
    while t < race_end:
        slow = jumper is not None and jumper["jump_t"] + 0.25 < t < jumper["jump_t"] + 1.35
        frames.append(("race", t))
        t += (0.35 if slow else 1.0) / FPS
    replay = None
    if spinner is not None:
        a, b = spinner["spin_t"] - 0.5, spinner["spin_t"] + 1.7
        replay = (len(frames) / FPS, a, b)
        t = a
        while t < b:
            frames.append(("replay", t))
            t += 0.4 / FPS
    cta_start = len(frames) / FPS
    for _ in range(int(4.8 * FPS)):
        frames.append(("cta", race_end - 0.1))
    return frames, winner, spinner, jumper, replay, cta_start


def state(c, t):
    f = min(t * 30, len(c["rec"]) - 1.001)
    i = int(f)
    a = f - i
    r0, r1 = c["rec"][i], c["rec"][i + 1]
    return tuple(r0[j] * (1 - a) + r1[j] * a for j in range(6))


def mood_of(c, t, x):
    if c["finish"] is not None and t > c["finish"] and c.get("place") == 1:
        return "happy"
    if c["spin_t"] is not None and 0 <= t - c["spin_t"] < 1.4:
        return "whoa"
    if c["spin_t"] is not None and 1.4 <= t - c["spin_t"] < 3.5:
        return "dizzy"
    if c["jump_t"] is not None and c["land_t"] is not None and c["jump_t"] <= t < c["land_t"]:
        return "whoa"
    if c["bump_t"] is not None and 0 <= t - c["bump_t"] < 1.2:
        return "scared"
    if (c["lane"] == PUD_LANE and 0 < PUD_X - x < 22) or (c["lane"] == RAMP_LANE and 0 < RAMP_X - x < 22):
        return "scared"
    return "normal"


BUBBLES = {"spin": "WHOA!", "bump": "HEY!", "jump": "YEEHAW!", "win": "YEAH!"}


# ------------------------------------------------------------------ drawing
def draw_ground(ctx, camx):
    gc = se.lit(se.th_loc()["ground"])
    g = cairo.LinearGradient(0, ground_y(4.6), 0, H)
    g.add_color_stop_rgb(0, *se.shade(gc, 0.85))
    g.add_color_stop_rgb(1, *gc)
    ctx.rectangle(-W, ground_y(4.6), 3 * W, H * 2)
    ctx.set_source(g)
    ctx.fill()
    top, bot = ground_y(3.55), ground_y(-0.55)
    rg = cairo.LinearGradient(0, top, 0, bot)
    rg.add_color_stop_rgb(0, *se.lit((0.3, 0.3, 0.34)))
    rg.add_color_stop_rgb(1, *se.lit((0.23, 0.23, 0.27)))
    ctx.rectangle(-W, top, 3 * W, bot - top)
    ctx.set_source(rg)
    ctx.fill()
    if se.THEME["weather"] == "rain":                            # wet sheen
        ctx.rectangle(-W, top, 3 * W, bot - top)
        ctx.set_source_rgba(0.6, 0.7, 0.85, 0.12)
        ctx.fill()
    for z0, z1 in ((-0.55, -0.72), (3.55, 3.7)):
        k0, k1 = k_of(z0), k_of(z1)
        y0, y1 = ground_y(z0), ground_y(z1)
        x = math.floor((camx - 1600 / k1) / 2) * 2
        while (x - camx) * k1 + 540 < 2 * W:
            se.poly(ctx, [((x - camx) * k0 + 540, y0), ((x + 2 - camx) * k0 + 540, y0),
                          ((x + 2 - camx) * k1 + 540, y1), ((x - camx) * k1 + 540, y1)])
            ctx.set_source_rgb(*((0.85, 0.1, 0.1) if int(x / 2) % 2 else (0.96, 0.96, 0.96)))
            ctx.fill()
            x += 2
    for zl in (0.5, 1.5, 2.5):
        k, y = k_of(zl), ground_y(zl)
        x = math.floor((camx - 1600 / k) / 4) * 4
        while (x - camx) * k + 540 < 2 * W:
            ctx.rectangle((x - camx) * k + 540, y - k * 0.06, 1.6 * k, k * 0.12)
            ctx.set_source_rgba(1, 1, 1, 0.9)
            ctx.fill()
            x += 4
    for row in range(8):                                         # checkered finish line
        za, zb = -0.55 + row * 0.5, -0.05 + row * 0.5
        for col in range(2):
            xa = FIN_X + col * 0.9
            se.poly(ctx, [((xa - camx) * k_of(za) + 540, ground_y(za)), ((xa + 0.9 - camx) * k_of(za) + 540, ground_y(za)),
                          ((xa + 0.9 - camx) * k_of(zb) + 540, ground_y(zb)), ((xa - camx) * k_of(zb) + 540, ground_y(zb))])
            ctx.set_source_rgb(*((0.05, 0.05, 0.05) if (row + col) % 2 else (1, 1, 1)))
            ctx.fill()


def draw_props(ctx, camx, z, seed, back=True):
    k, y = k_of(z), ground_y(z)
    rng = np.random.default_rng(seed)
    xs = np.cumsum(rng.uniform(9, 20, 90)) - 30
    loc = se.THEME["location"]
    for i, x in enumerate(xs):
        sx = (x - camx) * k + 540
        if not -300 < sx < W + 300:
            continue
        s = 1.0 + 0.3 * math.sin(i * 1.7)
        if not back:
            for j in range(3):
                ctx.arc(sx + (j - 1) * 0.9 * k, y - 0.4 * k, (0.8 + 0.2 * j) * k * 0.6, math.pi, 2 * math.pi)
                ctx.set_source_rgb(*se.lit((0.2, 0.55, 0.22) if loc != "desert" else (0.6, 0.5, 0.3)))
                ctx.fill()
        elif loc == "desert":                                    # cactus
            ctx.set_source_rgb(*se.lit((0.25, 0.6, 0.3)))
            se.rrect(ctx, sx - 0.3 * k * s, y - 3.2 * k * s, 0.6 * k * s, 3.2 * k * s, 0.3 * k * s)
            ctx.fill()
            se.rrect(ctx, sx - 1.0 * k * s, y - 2.4 * k * s, 0.45 * k * s, 1.2 * k * s, 0.22 * k * s)
            ctx.fill()
        elif loc == "beach":                                     # palm
            ctx.set_source_rgb(*se.lit((0.55, 0.38, 0.2)))
            ctx.set_line_width(0.35 * k)
            ctx.move_to(sx, y)
            ctx.curve_to(sx + 0.3 * k, y - 2 * k * s, sx + 0.8 * k, y - 3.5 * k * s, sx + 0.6 * k, y - 5 * k * s)
            ctx.stroke()
            for q in range(5):
                ang = math.pi * (0.1 + q * 0.2)
                ctx.move_to(sx + 0.6 * k, y - 5 * k * s)
                ctx.line_to(sx + 0.6 * k + math.cos(ang) * 2.2 * k, y - 5 * k * s - math.sin(ang) * 0.8 * k + 1.0 * k)
                ctx.set_source_rgb(*se.lit((0.2, 0.55, 0.25)))
                ctx.set_line_width(0.3 * k)
                ctx.stroke()
        else:                                                    # round tree (snow cap in snow)
            ctx.rectangle(sx - 0.25 * k, y - 2.6 * k * s, 0.5 * k, 2.6 * k * s)
            ctx.set_source_rgb(*se.lit((0.4, 0.26, 0.14)))
            ctx.fill()
            ctx.arc(sx, y - 3.4 * k * s, 1.7 * k * s, 0, 2 * math.pi)
            ctx.set_source_rgb(*se.lit((0.18, 0.5, 0.22)))
            ctx.fill()
            ctx.arc(sx - 0.5 * k * s, y - 3.8 * k * s, 1.0 * k * s, 0, 2 * math.pi)
            ctx.set_source_rgb(*se.lit((0.95, 0.96, 1.0) if se.THEME["weather"] == "snow" else (0.26, 0.62, 0.3)))
            ctx.fill()


def draw_puddle(ctx, camx, t):
    k, y = k_of(PUD_LANE), ground_y(PUD_LANE)
    sx = (PUD_X + 2.5 - camx) * k + 540
    if -600 < sx < W + 600:
        ctx.save()
        ctx.translate(sx, y)
        ctx.scale(4.8 * k, 0.55 * k)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(*se.lit((0.3, 0.6, 1.0)), 0.9)
        ctx.fill()
        for j in range(4):
            ox = (j - 1.5) * 1.8 * k + 8 * math.sin(t * 3 + j)
            ctx.move_to(sx + ox - 0.5 * k, y - 0.1 * k)
            ctx.line_to(sx + ox + 0.5 * k, y - 0.1 * k)
            ctx.set_source_rgba(1, 1, 1, 0.7)
            ctx.set_line_width(max(2, k * 0.06))
            ctx.stroke()


def draw_ramp(ctx, camx):
    k, y = k_of(RAMP_LANE), ground_y(RAMP_LANE)
    x0, x1 = (RAMP_X - 5.5 - camx) * k + 540, (RAMP_X - camx) * k + 540
    if -400 < x1 < W + 400:
        se.poly(ctx, [(x0, y), (x1, y), (x1, y - 1.3 * k)])
        ctx.set_source_rgb(*se.lit((0.85, 0.55, 0.25)))
        ctx.fill_preserve()
        ctx.set_source_rgb(0.3, 0.18, 0.08)
        ctx.set_line_width(3)
        ctx.stroke()


def draw_car(ctx, c, t, camx):
    x, z, h, yaw, pitch, v = state(c, t)
    vk = c["key"]
    veh = se.VEHICLES[vk]
    k, gy = k_of(z), ground_y(z)
    sx = (x - camx) * k + 540
    if not -900 < sx < W + 900:
        return None
    bw, bh = veh["body"]
    r, travel = veh["wheel_r"], veh["travel"]
    ride = r + 0.6 * travel + bh / 2
    ctx.save()
    ctx.translate(sx, gy)
    ctx.scale(bw * 0.58 * k * (1 + h * 0.06), 0.16 * k)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(0, 0, 0, 0.3 * max(0.0, 1 - h / 5))
    ctx.fill()
    ys = se.yaw_scale(yaw)
    land = c["land_t"] is not None and 0 <= t - c["land_t"] < 0.3
    squash = 1 - 0.12 * math.sin(math.pi * (t - c["land_t"]) / 0.3) if land else 1.0
    ctx.save()
    ctx.translate(sx, gy - h * k)
    ctx.scale(k, -k)
    ctx.rotate(pitch)
    ctx.scale(ys, squash)
    ctx.set_source_rgb(0.3, 0.3, 0.34)
    ctx.set_line_width(0.14)
    for lx in veh["wheel_x"]:
        ctx.move_to(lx, ride - bh / 2)
        ctx.line_to(lx, r)
        ctx.stroke()
    for lx in veh["wheel_x"]:
        se.draw_wheel(ctx, lx, r, -x / r, r, vk.startswith("monster"), sx=max(0.3, abs(ys)))
    ctx.translate(0, ride + 0.03 * math.sin(t * 18 + c["lane"]) * min(1.0, v / 20))
    se.draw_body(ctx, vk, veh, False, t)
    se.draw_face(ctx, vk, mood_of(c, t, x), t)
    ctx.restore()
    return sx, gy - (h + ride + bh) * k, k


def bubble(ctx, text, sx, sy, age, k):
    if not 0 <= age < 1.1:
        return
    sc = se.ease_out_back(min(1.0, age / 0.25)) * min(1.0, (1.1 - age) / 0.2)
    ctx.save()
    ctx.translate(sx, sy - 110 * k / 70)
    ctx.scale(sc * k / 70, sc * k / 70)
    se.rrect(ctx, -150, -60, 300, 110, 40)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill_preserve()
    ctx.set_source_rgb(0.07, 0.07, 0.2)
    ctx.set_line_width(8)
    ctx.stroke()
    se.poly(ctx, [(-30, 48), (10, 48), (-40, 100)])
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    se.draw_text(ctx, text, 0, -5, 62, fill=(0.9, 0.12, 0.12), stroke=(1, 1, 1), sw=4)
    ctx.restore()


def draw_hud(ctx, cars, t):
    se.draw_text(ctx, "MEGAWHEEL RACE!", W / 2, 150, 92, fill=(1, 0.86, 0.12))
    order = sorted(cars, key=lambda c: (c["finish"] if c["finish"] is not None and c["finish"] <= t else 1e9,
                                        -state(c, t)[0]))
    for i, c in enumerate(order):
        y = 260 + i * 74
        se.rrect(ctx, 30, y - 30, 330, 62, 16)
        ctx.set_source_rgba(0.05, 0.05, 0.15, 0.7)
        ctx.fill()
        se.draw_text(ctx, str(i + 1), 70, y + 1, 44, fill=(1, 0.86, 0.12))
        ctx.arc(120, y, 14, 0, 2 * math.pi)
        ctx.set_source_rgb(*se.VEHICLES[c["key"]]["color"])
        ctx.fill()
        se.draw_text(ctx, nick(c["key"]).upper(), 235, y + 1, 38, max_w=190)


def draw_cta(ctx, age):
    a = min(1.0, age / 0.3)
    ctx.set_source_rgba(0.03, 0.03, 0.1, 0.55 * a)
    ctx.paint()
    s = se.ease_out_back(min(1.0, age / 0.45))
    for i, (txt, col, y) in enumerate((("LIKE", (0.2, 0.75, 1.0), 820), ("SUBSCRIBE", (1, 0.25, 0.25), 1000),
                                       ("MEGAWHEEL ARENA", (1, 0.86, 0.12), 1180))):
        ctx.save()
        ctx.translate(540, y)
        ctx.scale(s, s)
        se.draw_text(ctx, txt, 0, 0, 110 if i < 2 else 80, fill=col)
        ctx.restore()


# ------------------------------------------------------------------ audio
def build_audio(frames, events, winner, spinner, replay, lines, voice, out_of):
    se.VOICE = voice
    total = len(frames) / FPS
    n = int(total * se.SR) + se.SR
    narr, eng, sfx = np.zeros(n), np.zeros(n), np.zeros(n)

    def place(buf, sig, t, gain=1.0):
        i0 = int(t * se.SR)
        if 0 <= i0 < n:
            m = min(len(sig), n - i0)
            buf[i0:i0 + m] += sig[:m] * gain

    busy = 0.0
    for t_want, text in lines:                                   # narration: never overlapping
        a = se.tts(text)
        t0 = max(t_want, busy + 0.15)
        place(narr, a, t0)
        busy = t0 + len(a) / se.SR
    lead = winner                                                # engine follows the winner's speed
    wrel, amp, pitch = [], [], []
    for mode, t in frames:
        v = state(lead, t)[5] if mode != "cta" else 0.0
        wrel.append(v / se.VEHICLES[lead["key"]]["wheel_r"])
        amp.append(0.0 if mode == "cta" else 0.5 + 0.5 * min(1.0, v / 23))
        pitch.append(1.0 if mode == "race" else 0.6)
    base, kk = se.VEHICLES[lead["key"]]["engine"]
    place(eng, se.synth_engine(np.array(wrel), np.array(amp), np.array(pitch), base, kk, seed=3), 0.0)
    place(sfx, se.tone(660, 0.12, "sine", decay=0.08), 0.02, 0.5)
    place(sfx, se.tone(990, 0.22, "sine", decay=0.12), 0.5, 0.6)
    place(sfx, se.synth_whoosh(), 0.55, 0.4)
    for kind, t, x, z in events:
        o = out_of(t)
        if kind == "splash":
            place(sfx, se.synth_splash(1.0, seed=41), o, 1.0)
            place(sfx, se.synth_spin(1.4, 2), o + 0.05, 0.8)
        elif kind == "bump":
            place(sfx, se.synth_impact(0.6, seed=7), o, 0.8)
        elif kind == "takeoff":
            place(sfx, se.synth_whoosh(), o, 0.6)
        elif kind == "land":
            place(sfx, se.synth_impact(1.0, seed=11), o, 1.0)
    if winner["finish"] is not None:
        place(sfx, se.synth_win(), out_of(winner["finish"]), 0.9)
    if replay:
        r0, a, b = replay
        o = r0 + (spinner["spin_t"] - a) / 0.4
        place(sfx, se.synth_rewind(), r0, 0.6)
        place(sfx, se.stretch(se.synth_splash(1.0, seed=42), 0.5), o, 1.0)
        place(sfx, se.stretch(se.synth_spin(1.4, 2), 0.5), o, 0.7)
    bgm = se.synth_bgm(total + 1, style=se.th_time()["music"])
    bgm = bgm[:n] if len(bgm) >= n else np.pad(bgm, (0, n - len(bgm)))
    talk = np.convolve((np.abs(narr) > 0.01).astype(float), np.ones(int(0.25 * se.SR)) / (0.25 * se.SR), "same")
    duck = 1.0 - (1.0 - 10 ** (-se.DUCK_DB / 20)) * np.clip(talk * 3, 0, 1)
    mix = (se.peak(narr) * se.VOL_NARR + se.peak(eng) * se.VOL_ENGINE * duck + se.peak(bgm) * se.VOL_BGM * duck
           + se.peak(sfx) * se.VOL_SFX * (0.5 + 0.5 * duck))
    mix = np.tanh(1.3 * mix) / np.tanh(1.3)
    mix = mix[:int(total * se.SR)]
    return mix / max(1e-9, np.max(np.abs(mix))) * 0.95


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--name", default="")
    opt = ap.parse_args()
    se.load_cast()
    se.detect_font()
    active = registry._active(None)
    name = opt.name or f"SIM_RACE25D_{ENGINE_VERSION.upper()}_S{opt.seed:03d}"
    if not opt.preview_only and registry.find_seed(SERIES, ENGINE_VERSION, opt.seed):
        print(f"[25d] STOP: seed {opt.seed} sudah dipakai untuk {SERIES}. Pakai seed lain.", flush=True)
        raise SystemExit(1)
    appearances = {}
    for e in active:
        for vk in e.get("vehicles", []):
            appearances[vk] = appearances.get(vk, 0) + 1
    params = setup(opt.seed, appearances)
    se.make_theme(opt.seed, used=[e.get("theme", "") for e in active if e.get("theme")])
    uses = {v: 0 for v in se.VOICES}
    for e in active:
        if e.get("voice") in uses:
            uses[e["voice"]] += 1
    vr = np.random.default_rng(5000 + opt.seed)
    tie = {v: float(vr.random()) for v in se.VOICES}
    voice = min(se.VOICES, key=lambda v: (uses[v], tie[v]))
    cars, events = simulate(opt.seed)
    frames, winner, spinner, jumper, replay, cta_start = build_timeline(cars)
    order = sorted(cars, key=lambda c: c["place"])
    print(f"[25d] {name} theme={se.THEME_ID} voice={voice} cast={[nick(c['key']) for c in cars]} "
          f"lanes={params['lanes']} finish={[nick(c['key']) for c in order]} frames={len(frames)} "
          f"({len(frames) / FPS:.1f}s)", flush=True)
    race_idx = [(j, ft) for j, (mode, ft) in enumerate(frames) if mode == "race"]

    def out_of(t):
        for j, ft in race_idx:
            if ft >= t:
                return j / FPS
        return len(frames) / FPS

    names = [nick(c["key"]) for c in cars]
    lines = [(0.15, f"Four racers, one finish line! {names[0]}, {names[1]}, {names[2]} and {names[3]}. Who will win?")]
    if spinner:
        lines.append((out_of(spinner["spin_t"]) + 0.2, f"Whoa! {nick(spinner['key'])} hits the water and spins out!"))
    if jumper:
        lines.append((out_of(jumper["jump_t"]) + 0.1, f"{nick(jumper['key'])} takes the ramp... big air!"))
    lines.append((out_of(winner["finish"]) + 0.2, f"{nick(winner['key'])} wins the race!"))
    if replay:
        lines.append((replay[0] + 0.1, se.REPLAY_LINE))
    lines.append((cta_start + 0.2, se.CTA))

    date = time.strftime("%Y-%m-%d")
    out_dir = (f"{se.BASE}/work/lanes25d/previews/{name}" if opt.preview_only
               else f"{se.CHANNEL_DIR}/pending/{date}_{SERIES}_s{opt.seed:03d}")
    prev = os.path.join(out_dir, "preview")
    os.makedirs(prev, exist_ok=True)
    os.makedirs(se.WORK, exist_ok=True)
    wav = f"{se.WORK}/mix_{name}.wav"
    se.write_wav(wav, build_audio(frames, events, winner, spinner, replay, lines, voice, out_of))
    silent = f"{se.WORK}/v_{name}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", silent],
                          stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    marks = {}
    if spinner:
        marks[int(out_of(spinner["spin_t"] + 0.5) * FPS)] = "spin"
    if jumper:
        marks[int(out_of(jumper["jump_t"] + 0.6) * FPS)] = "jump"
    marks[int(out_of(winner["finish"] + 0.5) * FPS)] = "winner"
    marks[int((cta_start + 1.5) * FPS)] = "outro"
    camx, zoom = None, 1.0
    for fi, (mode, t) in enumerate(frames):
        st = {id(c): state(c, t) for c in cars}
        focus = None
        for c in cars:
            if c["spin_t"] is not None and -0.6 < t - c["spin_t"] < 2.0:
                focus = c
            if c["jump_t"] is not None and -0.5 < t - c["jump_t"] < 2.2:
                focus = c
        near_finish = st[id(winner)][0] > FIN_X - 30 or (winner["finish"] is not None and t >= winner["finish"])
        if near_finish or mode == "cta":
            focus = winner                                       # finish + celebration: the winner is the star
        if mode == "replay":
            focus = spinner
        xs = [st[id(c)][0] for c in cars]
        mid = (max(xs) + min(xs)) / 2
        wgt = 0.85 if focus is not None and (focus is jumper or focus is winner) else 0.55
        target = wgt * (st[id(focus)][0] + 2) + (1 - wgt) * mid if focus else mid + 1.5
        if mode == "replay":
            target = st[id(spinner)][0] + 1
        spread = max(xs) - min(xs) + 9.0
        fit = float(np.clip(W * 0.92 / (spread * k_of(0.0)), 0.82, 1.12))
        camx = target if camx is None else camx + (target - camx) * (0.3 if mode == "replay" else 0.12)
        punch = 1.0
        for kind, et, ex, ez in events:
            if kind in ("land", "bump", "splash") and 0 <= t - et < 0.35:
                punch = max(punch, 1 + 0.08 * math.sin(math.pi * (t - et) / 0.35))
        want = 1.18 if mode == "replay" else min(fit, 1.08 if focus else 1.0)
        zoom += (want * punch - zoom) * 0.12
        shx = shy = 0.0
        for kind, et, ex, ez in events:
            if kind in ("land", "bump") and 0 <= t - et < 0.4:
                amp = 16 * (1 - (t - et) / 0.4)
                shx, shy = amp * math.sin(t * 90), amp * math.cos(t * 70)
        se.draw_sky(ctx, camx * 0.35, WORLD_DY / se.S, 1.0)
        ctx.save()
        ctx.translate(0, WORLD_DY)
        ctx.translate(540 + shx, 1520 + shy)
        ctx.scale(zoom, zoom)
        ctx.translate(-540, -1520)
        draw_props(ctx, camx, 5.2, 11 + opt.seed, back=True)
        draw_props(ctx, camx, 4.3, 12 + opt.seed, back=True)
        draw_ground(ctx, camx)
        draw_puddle(ctx, camx, t)
        draw_ramp(ctx, camx)
        heads = {}
        for c in sorted(cars, key=lambda c: -st[id(c)][1]):
            hd = draw_car(ctx, c, t, camx)
            heads[id(c)] = None if hd is None else (540 + (hd[0] - 540) * zoom + shx,
                                                   1520 + (hd[1] - 1520) * zoom + shy + WORLD_DY, hd[2])
        for kind, et, ex, ez in events:
            age = t - et
            if kind == "splash" and 0 <= age < 1.6:
                k, y = k_of(ez), ground_y(ez)
                ctx.save()
                ctx.translate((ex - camx) * k + 540, y)
                ctx.scale(k, -k)
                se.draw_water_splash(ctx, dict(x=0.0, y=0.0, speed=22.0, big=False), age)
                ctx.restore()
            if kind == "land" and 0 <= age < 0.8:
                k, y = k_of(ez), ground_y(ez)
                for j in range(8):
                    px = (ex - camx) * k + 540 + (j - 3.5) * 0.7 * k * (1 + age * 2)
                    ctx.arc(px, y - age * 0.8 * k, (0.4 + age) * k * 0.6, 0, 2 * math.pi)
                    ctx.set_source_rgba(0.75, 0.68, 0.55, 0.6 * (1 - age / 0.8))
                    ctx.fill()
        draw_props(ctx, camx, -0.95, 13 + opt.seed, back=False)
        ctx.restore()
        se.draw_weather(ctx, fi / FPS)
        if mode == "race":
            se.draw_speed_lines(ctx, max(st[id(c)][5] for c in cars), fi / FPS)
        for c in cars:
            hd = heads.get(id(c))
            if not hd or mode == "cta":
                continue
            for key, t0 in (("spin", c["spin_t"]), ("bump", c["bump_t"]), ("jump", c["jump_t"])):
                if t0 is not None:
                    bubble(ctx, BUBBLES[key], hd[0], hd[1], t - t0 - 0.1, hd[2] * zoom)
            if c is winner and c["finish"] is not None:
                bubble(ctx, BUBBLES["win"], hd[0], hd[1], t - c["finish"] - 0.3, hd[2] * zoom)
        if mode != "cta":
            draw_hud(ctx, cars, t)
        if mode == "race":
            se.draw_ready_go(ctx, t)
        if mode == "replay":
            se.draw_replay_overlay(ctx, fi / FPS)
        if winner["finish"] is not None and t >= winner["finish"] and mode != "replay":
            age = t - winner["finish"] if mode == "race" else 2.0
            se.draw_confetti(ctx, age)
            s = se.ease_out_back(min(1.0, age / 0.4))
            ctx.save()
            ctx.translate(540, 620 if mode == "cta" else 760)
            ctx.scale(s, s)
            se.draw_text(ctx, f"{nick(winner['key']).upper()} WINS!", 0, 0, 120, fill=(1, 0.86, 0.12))
            ctx.restore()
        if mode == "cta":
            draw_cta(ctx, fi / FPS - cta_start)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
        if fi in marks:
            surf.write_to_png(os.path.join(prev, f"{marks[fi]}.png"))
    ff.stdin.close()
    ff.wait()
    out = os.path.join(out_dir, f"{name}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-movflags", "+faststart", "-shortest", out], check=True)
    os.remove(silent)
    # light checks (the 2D pixel audit does not apply to this format)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type:format=duration", "-of",
                            "json", out], capture_output=True, text=True)
    pj = json.loads(probe.stdout or "{}")
    dur = float(pj.get("format", {}).get("duration", 0))
    kinds = [s["codec_type"] for s in pj.get("streams", [])]
    checks = {"video+audio streams": "video" in kinds and "audio" in kinds,
              "duration 20-60 s": 20 <= dur <= 60,
              "has winner": winner["finish"] is not None,
              "has spin + replay": spinner is not None and replay is not None,
              "has jump": jumper is not None,
              "previews": all(os.path.exists(os.path.join(prev, f"{m}.png")) for m in ("winner", "outro"))}
    passed = all(checks.values())
    outcomes = [("win" if c is winner else f"p{c['place']}") + ("+spin" if c["spin_t"] else "")
                + ("+jump" if c["jump_t"] else "") + ("+bump" if c["bump_t"] else "") for c in cars]
    track_id = "race25d_" + hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()[:8] + "@" + se.THEME_ID
    title = TITLES[opt.seed % len(TITLES)]
    folder_rel = os.path.relpath(out_dir, se.BASE)
    manifest = dict(
        video_id=name, status="RENDERED_PENDING_APPROVAL" if passed else "CHECKS_FAILED",
        engine=f"race25d {ENGINE_VERSION}", series=SERIES, seed=opt.seed, fps=FPS, duration=round(dur, 2),
        params=params, theme=se.THEME, theme_id=se.THEME_ID, voice=voice, outcomes=outcomes, checks=checks,
        cta=se.CTA, title_base=title, title=f"{title} #Shorts",
        description=(f"{', '.join(names[:3])} and {names[3]} race to the finish line! 🏁 "
                     "Watch out for the slippery puddle and the big ramp jump! 💦\n\n"
                     "Watch till the end for the slow-motion replay! 🎬\n\n🏆 Comment your champion below!\n"
                     f"🔔 Subscribe to {se.CHANNEL} for new car challenges every week.\n\n"
                     "#Shorts #CarRace #CartoonCars #Racing #MegaWheelArena"),
        tags=TAGS + [se.VEHICLES[c["key"]]["display"].split(" THE ")[1].lower() for c in cars],
        narration=[txt for _, txt in lines],
        assets="100% procedurally generated (cairo 2.5D render + synthesized audio), narration Edge-TTS " + voice,
        video_path=out, preview_dir=prev)
    with open(os.path.join(out_dir, f"{name}.json"), "w") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, f"{name}_audit.md"), "w") as fh:
        fh.write(f"# Checks {name}\n\n" + "\n".join(f"- {'✅' if ok else '❌'} {k}" for k, ok in checks.items())
                 + f"\n\nDuration {dur:.1f} s · theme {se.THEME_ID} · voice {voice}\n")
    print(f"[25d] checks {'PASS' if passed else 'FAIL'} {checks}", flush=True)
    if not opt.preview_only:
        registry.upsert(dict(video_id=name, series=SERIES, engine_version=ENGINE_VERSION, seed=opt.seed, created=date,
                             render_date=date, vehicles=[c["key"] for c in cars], track_id=track_id,
                             theme=se.THEME_ID, voice=voice, outcomes=outcomes, duration=round(dur, 2),
                             status="RENDERED_PENDING_APPROVAL" if passed else "AUDIT_FAILED", folder=folder_rel,
                             audit=f"{folder_rel}/{name}_audit.md", episode=None, season=None, upload_date=None,
                             youtube_url=None))
    print("[result] " + json.dumps(dict(video_id=name, video=out, duration=round(dur, 1), passed=passed)), flush=True)
    if not passed:
        raise SystemExit(5)


if __name__ == "__main__":
    main()
