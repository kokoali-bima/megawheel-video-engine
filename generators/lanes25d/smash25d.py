#!/usr/bin/env python3
"""MegaWheel Arena — series "smash25d": SMASH ARENA, the 19:00 ET daily slot (user 2026-10-01).

Four cars ram each other in a 2.5D arena until only one is left. Same "paper cutout" style as race25d: the
characters are drawn by the SAME functions as the 2D episodes (race25d.draw_car -> sim_engine draw_body /
draw_face / draw_wheel), so they look exactly like the 2D cast; a car turning around flips like a paper card.

Rules: every car has 100 HP. Rams do damage by closing speed and (effective) mass, side hits hurt more, the
attacker's front is reinforced. A car is OUT when its HP hits 0 (wrecked, smoking) or when it is pushed off
the floor (lava ring / mud pit / icy water). The floor shrinks every few seconds. Last car standing wins.
Arenas (rotation): lava ring (steel floor) · mud pit (dirt floor) · ice rink (slippery, low grip).
Cartoon slapstick only (BLUEPRINT rule 7): no fire deaths, no people; wrecks smoke and get dizzy.

Timeline: READY-GO -> smash -> winner + confetti -> INSTANT REPLAY of the biggest moment -> YouTube end card.
Hard rules: hard cuts between scenes, check "no frame without a car".

Usage (cd /root/video-engine):
  ./venv/bin/python generators/lanes25d/smash25d.py --seed 1                 # -> renders/megawheel_arena/pending/
  ./venv/bin/python generators/lanes25d/smash25d.py --seed 1 --preview-only  # -> work/lanes25d/previews/
  [--arena lava|mud|ice]   force the arena (tests)
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
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "physics_2d"))
import registry  # noqa: E402
import sim_engine as se  # noqa: E402
import race25d as R  # noqa: E402  (shared drawing: car, bubble, YouTube end card, sounds)

SERIES, ENGINE_VERSION = "smash25d", "v1"
W, H, FPS = se.W, se.H, 30
# perspective: x, z in metres (z = depth). Higher camera than race25d so the floor reads as an arena.
F_PERSP, D0, DZ = 6000.0, 100.0, 8.0             # k(z) = F / (D0 + DZ*z): front 60 px/m, back (z=8.5) ≈ 36
Y_H, CAM_H = 276.0, 20.4
WORLD_DY, PIV_Y = -40.0, 1190.0                  # zoom pivot (world space)
ZC = 4.25                                        # arena centre depth
HX0, HZ0, HX_MIN, HZ_MIN = 9.5, 4.25, 4.6, 2.3   # floor half-size at start / after the last shrink
SHRINK_AT, SHRINK_EVERY, SHRINK_STEP = 7.0, 6.5, 0.22
T_MAX = 40.0
POOL = ["sports", "police", "taxi", "f1", "bus", "firetruck", "icecream", "bigrig", "monster", "monster2"]
BIG = {"bus", "firetruck", "icecream", "bigrig"}
ARENAS = {
    "lava": dict(name="the lava", out_line="{n} is pushed into the lava!", bubble="HOT HOT!", grip=0.022),
    "mud":  dict(name="the mud", out_line="Splat! {n} slides into the mud pit!", bubble="YUCK!", grip=0.02),
    "ice":  dict(name="the icy water", out_line="Splash! {n} slides into the icy water!", bubble="BRRR!", grip=0.007),
}
VMAX = {"f1": 12.5, "sports": 12.0, "police": 11.0, "taxi": 10.5, "monster": 10.0, "monster2": 10.0,
        "icecream": 8.0, "bus": 7.8, "firetruck": 7.8, "bigrig": 7.2}
TURN = {"f1": 3.2, "sports": 3.0, "police": 2.7, "taxi": 2.6, "monster": 2.4, "monster2": 2.4,
        "icecream": 1.8, "bus": 1.6, "firetruck": 1.6, "bigrig": 1.4}
HIT_BUBBLES = ["BAM!", "WHAM!", "CRUNCH!", "BONK!", "OOF!"]
TITLES = ["4 Cars Enter, 1 Survives! 💥 Smash Arena", "Last Car Standing Wins! 💥", "Who Survives the Smash Arena? 💥",
          "Crash Battle! Only One Can Win! 💥"]
TAGS = ["cars", "car crash", "demolition derby", "cartoon cars", "funny cars", "smash", "car battle", "shorts",
        "MegaWheel Arena"]

CAST, ARENA = [], "lava"


def k_of(z):
    return F_PERSP / (D0 + DZ * z)


def ground_y(z):
    return Y_H + CAM_H * k_of(z)


def pxy(x, z, camx):
    return (x - camx) * k_of(z) + 540, ground_y(z)


def nick(vk):
    return se.VEHICLES[vk]["nick"]


def m_eff(vk):
    return (se.VEHICLES[vk]["mass"] / 1000.0) ** 0.55


def radius(vk):
    return 0.3 * se.VEHICLES[vk]["body"][0] + 0.25


def bounds(t):
    """Floor half-size (hx, hz) at time t: shrinks in eased steps."""
    hx, hz = HX0, HZ0
    s = t - SHRINK_AT
    while s > 0:
        p = min(1.0, s / 1.2)
        e = p * p * (3 - 2 * p)
        nhx, nhz = max(HX_MIN, hx * (1 - SHRINK_STEP)), max(HZ_MIN, hz * (1 - SHRINK_STEP * 0.75))
        hx, hz = hx + (nhx - hx) * e, hz + (nhz - hz) * e
        s -= SHRINK_EVERY
    return hx, hz


def shrink_times():
    out, t = [], SHRINK_AT
    while t < T_MAX:
        if bounds(t + 2)[0] < bounds(t - 0.01)[0] - 0.05:
            out.append(t)
        t += SHRINK_EVERY
    return out


# ------------------------------------------------------------------ per-seed setup
def setup(seed, appearances, used_arenas, forced_arena=None):
    global CAST, ARENA
    r = np.random.default_rng(12000 + seed)
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
    CAST = cast
    if forced_arena:
        ARENA = forced_arena
    else:
        cnt = {a: used_arenas.count(a) for a in ARENAS}
        at = {a: float(r.random()) for a in ARENAS}
        ARENA = min(ARENAS, key=lambda a: (cnt[a], at[a]))
    return dict(cast=cast, arena=ARENA)


# ------------------------------------------------------------------ scripted battle (120 Hz)
def simulate(seed):
    rng = np.random.default_rng(13000 + seed)
    dt = 1 / 120
    grip = ARENAS[ARENA]["grip"]
    corners = [(-6.5, ZC - 2.6), (6.5, ZC + 2.6), (6.5, ZC - 2.6), (-6.5, ZC + 2.6)]
    cars = []
    for i, vk in enumerate(CAST):
        x, z = corners[i]
        th = math.atan2(ZC - z, -x)                              # face the centre
        cars.append(dict(key=vk, lane=i, x=x, z=z, th=th, vx=0.0, vz=0.0, h=0.0, vh=0.0, hp=100.0, alive=True,
                         out=None, out_kind=None, yaw=0.0 if math.cos(th) >= 0 else math.pi, spin=0.0,
                         target=None, retarget=0.0, recoil=0.0, stun=0.0, last_hit=None, hits_taken=[], land=None,
                         trig=None, finish=None, bump_t=None, place=None, rec=[], m=m_eff(vk), r=radius(vk),
                         aggro=float(rng.uniform(0.85, 1.15))))
    events, hits = [], []                                        # hits: dict(t, a, b, rel, x, z)
    cool = {}
    winner, t_end, t = None, None, 0.0
    sudden = False
    while True:
        alive = [c for c in cars if c["alive"]]
        hx, hz = bounds(t)
        go = t >= 1.4                                            # READY... GO!
        esc = 1.0 + t / 22.0                                     # damage escalates so the battle always ends
        if not sudden and t > 34.0 and len(alive) > 1:
            sudden = True
            events.append(("sudden", t, 0.0, ZC))
        for c in cars:
            vk = c["key"]
            if c["alive"] and go and winner is None:
                c["retarget"] -= dt
                if c["target"] is None or not c["target"]["alive"] or c["retarget"] <= 0:
                    others = [o for o in alive if o is not c]
                    if others:
                        w = np.array([1.0 / (1.0 + math.hypot(o["x"] - c["x"], o["z"] - c["z"])) *
                                      (1.6 if o["hp"] < 40 else 1.0) for o in others])
                        c["target"] = others[int(rng.choice(len(others), p=w / w.sum()))]
                    c["retarget"] = float(rng.uniform(1.4, 2.8))
                tg = c["target"]
                if tg is not None:
                    ax, az = tg["x"] + tg["vx"] * 0.35 - c["x"], tg["z"] + tg["vz"] * 0.35 - c["z"]
                else:
                    ax, az = -c["x"], ZC - c["z"]
                if c["recoil"] > 0:                              # back off after a hit, then charge again
                    ax, az = -ax, -az
                    c["recoil"] -= dt
                ex = abs(c["x"]) - (hx - 2.2)                    # stay away from the edge
                ez = abs(c["z"] - ZC) - (hz - 1.6)
                if ex > 0:
                    ax -= math.copysign(ex * 6.0, c["x"])
                if ez > 0:
                    az -= math.copysign(ez * 6.0, c["z"] - ZC)
                want = math.atan2(az, ax)
                d = (want - c["th"] + math.pi) % (2 * math.pi) - math.pi
                c["th"] += float(np.clip(d, -TURN[vk] * dt, TURN[vk] * dt))
                vmax = VMAX[vk] * c["aggro"] * (0.55 if c["recoil"] > 0 else 1.0) * (0.6 + 0.4 * c["hp"] / 100)
                dvx, dvz = math.cos(c["th"]) * vmax - c["vx"], math.sin(c["th"]) * vmax - c["vz"]
                g = grip * 1.6 * (0.3 if c["stun"] > 0 else 1.0)   # dazed right after a hit: pushed around
                c["vx"] += dvx * g
                c["vz"] += dvz * g
            else:                                                # wrecked / waiting / celebrating: roll to a stop
                damp = 0.985 if ARENA == "ice" else 0.94
                if c is winner and t_end is not None:            # victory donut
                    c["th"] += 2.6 * dt
                    c["vx"] += (math.cos(c["th"]) * 5 - c["vx"]) * 0.08
                    c["vz"] += (math.sin(c["th"]) * 5 - c["vz"]) * 0.08
                elif c["out"] is None or c["out_kind"] == "wreck":
                    c["vx"] *= damp
                    c["vz"] *= damp
            c["x"] += c["vx"] * dt
            c["z"] += c["vz"] * dt
            if c["h"] > 0 or c["vh"] > 0:
                c["vh"] -= 22.0 * dt
                c["h"] += c["vh"] * dt
                if c["h"] <= 0:
                    c["h"], c["vh"] = 0.0, 0.0
                    c["land"] = t
            c["spin"] = max(0.0, c["spin"] - dt)
            c["stun"] = max(0.0, c["stun"] - dt)
            if c["out_kind"] == "ring" and c["h"] <= 0 and t - c["out"] > 0.3:
                c["vx"] *= 0.9
                c["vz"] *= 0.9
            face = 0.0 if math.cos(c["th"]) >= 0 else math.pi    # paper-card flip toward the driving direction
            if c["spin"] > 0:
                c["yaw"] += 14.0 * dt
            else:
                tgt = face + round((c["yaw"] - face) / (2 * math.pi)) * 2 * math.pi
                c["yaw"] += float(np.clip(tgt - c["yaw"], -7 * dt, 7 * dt))
        # collisions (alive cars and wrecks; cars that fell off are gone)
        solid = [c for c in cars if c["out_kind"] != "ring" or c["out"] is None]
        for i in range(len(solid)):
            for j in range(i + 1, len(solid)):
                a, b = solid[i], solid[j]
                dx, dz = b["x"] - a["x"], b["z"] - a["z"]
                dist = math.hypot(dx, dz)
                if dist >= a["r"] + b["r"] or dist < 1e-6:
                    continue
                nx, nz = dx / dist, dz / dist
                ma = a["m"] * (3 if not a["alive"] else 1)
                mb = b["m"] * (3 if not b["alive"] else 1)
                over = a["r"] + b["r"] - dist
                a["x"] -= nx * over * mb / (ma + mb)
                a["z"] -= nz * over * mb / (ma + mb)
                b["x"] += nx * over * ma / (ma + mb)
                b["z"] += nz * over * ma / (ma + mb)
                rel = (a["vx"] - b["vx"]) * nx + (a["vz"] - b["vz"]) * nz
                if rel <= 0:
                    continue
                e = 0.75
                J = (1 + e) * rel / (1 / ma + 1 / mb)
                a["vx"] -= J / ma * nx
                a["vz"] -= J / ma * nz
                b["vx"] += J / mb * nx
                b["vz"] += J / mb * nz
                key = (id(a), id(b))
                if rel < 2.5 or t - cool.get(key, -9) < 0.45 or winner is not None:
                    continue
                cool[key] = t
                hx_, hz_ = (a["x"] + b["x"]) / 2, (a["z"] + b["z"]) / 2
                for me, oth, sgn in ((a, b, 1), (b, a, -1)):
                    if not me["alive"]:
                        continue
                    front = math.cos(me["th"]) * nx * sgn + math.sin(me["th"]) * nz * sgn   # 1 = I hit with my nose
                    side = 1.35 if abs(front) < 0.45 else 1.0
                    armour = 0.55 if front > 0.6 else 1.0
                    dmg = 2.3 * rel * (oth["m"] / (oth["m"] + me["m"])) * 2 * side * armour * esc
                    me["hp"] = max(0.0, me["hp"] - dmg)
                    me["recoil"] = 0.55 if front > 0.3 else 0.25
                    me["stun"] = 0.2 + 0.3 * min(1.0, rel / 10) * (oth["m"] / me["m"]) ** 0.5
                    if dmg > 9:
                        me["hits_taken"].append(t)
                        me["last_hit"] = t
                    if rel > 7.5 and oth["m"] >= me["m"] * 0.8 and me["h"] <= 0:
                        me["vh"] = 3.0 + (rel - 7.5) * 0.45
                    if rel > 8.5 and front < 0.3:
                        me["spin"] = 0.6
                hits.append(dict(t=t, a=a, b=b, rel=rel, x=hx_, z=hz_))
                events.append(("hit", t, hx_, hz_, min(1.0, rel / 13.0), int(t * 1000) % 997,
                               se.VEHICLES[a["key"]]["color"], se.VEHICLES[b["key"]]["color"]))
        # eliminations
        for c in cars:
            if not c["alive"]:
                continue
            if c["hp"] <= 0:
                c["alive"], c["out"], c["out_kind"] = False, t, "wreck"
                events.append(("wreck", t, c["x"], c["z"]))
            elif abs(c["x"]) > hx + 0.2 or abs(c["z"] - ZC) > hz + 0.2:
                c["alive"], c["out"], c["out_kind"] = False, t, "ring"
                c["vh"] = 3.5
                events.append(("ringout", t, c["x"], c["z"]))
        alive = [c for c in cars if c["alive"]]
        if winner is None and (len(alive) <= 1 or t >= T_MAX):
            pool = alive or sorted(cars, key=lambda c: -(c["out"] or 0))[:1]
            winner = max(pool, key=lambda c: c["hp"])
            for c in alive:
                if c is not winner:
                    c["alive"], c["out"], c["out_kind"] = False, t, "wreck"
                    events.append(("wreck", t, c["x"], c["z"]))
            winner["finish"] = t
            t_end = t + 2.6
        # record (race25d.state layout: x, z, h, yaw, pitch, v, sq, split, burn, patched, ice, tires)
        if int(round(t * 120)) % 4 == 0:
            for c in cars:
                sink = 0.0
                if c["out_kind"] == "ring" and c["out"] is not None and c["h"] <= 0 and t - c["out"] > 0.3:
                    sink = min(1.0, (t - c["out"] - 0.3) / 1.2)
                c["sink_rec"] = c.get("sink_rec", []) + [sink]
                tilt = 0.22 if c["out_kind"] == "wreck" else (-0.12 * min(1.0, c["vh"] / 4) if c["h"] > 0 else 0.0)
                sq = 0.88 if c["out_kind"] == "wreck" else 1.0
                burn = 1.0 if (c["hp"] < 45 or (c["out_kind"] == "ring" and ARENA == "lava" and sink > 0)) else 0.0
                c["rec"].append((c["x"], c["z"], c["h"], c["yaw"], tilt, math.hypot(c["vx"], c["vz"]), sq, 0.0, burn,
                                 0.0, 0.0, 0.0))
                c.setdefault("hp_rec", []).append(c["hp"])
        t += dt
        if t_end is not None and t >= t_end:
            break
    order = [winner] + sorted([c for c in cars if c is not winner], key=lambda c: -(c["out"] or 0))
    for p, c in enumerate(order, start=1):
        c["place"] = p
    return cars, events, hits, winner


def rec_at(c, name, t):
    arr = c[name]
    f = min(t * 30, len(arr) - 1.001)
    i = int(f)
    a = f - i
    return arr[i] * (1 - a) + arr[i + 1] * a


# ------------------------------------------------------------------ timeline
def big_moments(cars, hits):
    """Candidates for slow-mo + replay: eliminations and the hardest hits."""
    mom = [(c["out"], 9 + (1 if c["out_kind"] == "ring" else 0), c) for c in cars if c["out"] is not None
           and c["finish"] is None]
    mom += [(h["t"], h["rel"] / 2, h["b"]) for h in hits if h["rel"] > 6]
    return sorted(mom, key=lambda m: -m[1])


def build_timeline(cars, hits, winner):
    mom = big_moments(cars, hits)
    slows = sorted([(m[0] - 0.15, m[0] + 0.5) for m in mom[:2]])
    frames, t = [], 0.0
    end = winner["finish"] + 2.2
    while t < end:
        frames.append(("race", t))
        t += (0.4 if any(a < t < b for a, b in slows) else 1.0) / FPS
    replay, star_t, star = None, None, None
    if mom:
        star_t, _, star = mom[0]
        a, b = max(0.0, star_t - 0.9), star_t + 1.6
        replay = (len(frames) / FPS, a, b)
        t = a
        while t < b:
            frames.append(("replay", t))
            t += 0.4 / FPS
    cta_start = len(frames) / FPS
    for _ in range(int(4.8 * FPS)):
        frames.append(("cta", end - 0.1))
    return frames, replay, star_t, star, cta_start


# ------------------------------------------------------------------ drawing
def mood(c, t, x):
    if c["finish"] is not None and t >= c["finish"]:
        return "happy"
    if c["out"] is not None and t >= c["out"]:
        return "dizzy"
    if c["last_hit"] is not None:
        recent = [h for h in c["hits_taken"] if 0 <= t - h < 1.1]
        if recent:
            return "whoa"
    hp = rec_at(c, "hp_rec", t)
    if hp < 35:
        return "scared"
    return "normal"


def floor_poly(hx, hz, camx, pad=0.0):
    return [pxy(-hx - pad, ZC - hz - pad, camx), pxy(hx + pad, ZC - hz - pad, camx),
            pxy(hx + pad, ZC + hz + pad, camx), pxy(-hx - pad, ZC + hz + pad, camx)]


def draw_stands(ctx, camx, t, cheer):
    """Crowd stands behind the arena (simple shapes; cars are the only characters)."""
    zb = ZC + HZ0 + 3.0
    for row in range(6):
        z = zb + row * 1.6
        k, y = k_of(z), ground_y(z) - row * 1.25 * k_of(z)
        ctx.rectangle(-W, y - 1.25 * k, 3 * W, 1.3 * k)
        ctx.set_source_rgb(*se.lit(se.shade((0.45, 0.47, 0.55), 1 - row * 0.06)))
        ctx.fill()
        rng = np.random.default_rng(100 + row)
        x = camx - 1500 / k
        while (x - camx) * k + 540 < 2 * W:
            sx = (x - camx) * k + 540
            jump = max(0.0, math.sin(t * 9 + x * 1.7)) * 0.35 * k * cheer
            col = [(0.95, 0.3, 0.3), (0.3, 0.6, 0.95), (0.98, 0.8, 0.2), (0.4, 0.8, 0.4), (0.9, 0.5, 0.9)][
                int(rng.integers(5))]
            ctx.arc(sx, y - 0.75 * k - jump, 0.32 * k, 0, 2 * math.pi)
            ctx.set_source_rgb(*se.lit(col))
            ctx.fill()
            x += 0.9 + float(rng.uniform(0, 0.4))
    k, y = k_of(zb - 0.6), ground_y(zb - 0.6)
    ctx.rectangle(-W, y - 0.9 * k, 3 * W, 0.9 * k)                 # front wall with banner
    ctx.set_source_rgb(*se.lit((0.12, 0.12, 0.2)))
    ctx.fill()
    x0 = math.floor((camx - 1500 / k) / 12) * 12
    while (x0 - camx) * k + 540 < 2 * W:
        se.draw_text(ctx, "SMASH ARENA", (x0 - camx) * k + 540, y - 0.45 * k, 0.62 * k, fill=(1, 0.86, 0.12),
                     stroke=(0.12, 0.12, 0.2), sw=3)
        x0 += 12


def draw_arena(ctx, camx, t, flash):
    hx, hz = bounds(t)
    big = floor_poly(40, 9.0, camx)                              # the danger zone everywhere outside the floor
    se.poly(ctx, big)
    if ARENA == "lava":
        g = cairo.LinearGradient(0, ground_y(ZC + 9), 0, ground_y(ZC - 9))
        g.add_color_stop_rgb(0, 0.85, 0.25, 0.05)
        g.add_color_stop_rgb(1, 1.0, 0.55, 0.1)
        ctx.set_source(g)
        ctx.fill()
        rng = np.random.default_rng(5)
        for _ in range(40):                                      # bubbling lava
            bx, bz, ph = float(rng.uniform(-16, 16)), float(rng.uniform(ZC - 7, ZC + 7)), float(rng.uniform(0, 6))
            if abs(bx) < hx + 0.3 and abs(bz - ZC) < hz + 0.3:
                continue
            p = (t * 0.8 + ph) % 1.0
            sx, sy = pxy(bx, bz, camx)
            ctx.arc(sx, sy, (0.15 + 0.35 * p) * k_of(bz), 0, 2 * math.pi)
            ctx.set_source_rgba(1, 0.9, 0.3, 0.8 * (1 - p))
            ctx.fill()
    elif ARENA == "mud":
        ctx.set_source_rgb(*se.lit((0.36, 0.24, 0.13)))
        ctx.fill()
        rng = np.random.default_rng(6)
        for _ in range(35):
            bx, bz = float(rng.uniform(-16, 16)), float(rng.uniform(ZC - 7, ZC + 7))
            sx, sy = pxy(bx, bz, camx)
            k = k_of(bz)
            ctx.save()
            ctx.translate(sx, sy)
            ctx.scale(1.0, 0.35)
            ctx.arc(0, 0, (0.5 + 0.3 * math.sin(t * 2 + bx)) * k, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgba(0.25, 0.15, 0.07, 0.7)
            ctx.fill()
    else:
        g = cairo.LinearGradient(0, ground_y(ZC + 9), 0, ground_y(ZC - 9))
        g.add_color_stop_rgb(0, 0.05, 0.2, 0.4)
        g.add_color_stop_rgb(1, 0.1, 0.35, 0.6)
        ctx.set_source(g)
        ctx.fill()
        rng = np.random.default_rng(7)
        for _ in range(26):                                      # floating ice chunks
            bx, bz = float(rng.uniform(-16, 16)), float(rng.uniform(ZC - 7, ZC + 7))
            if abs(bx) < hx + 0.6 and abs(bz - ZC) < hz + 0.6:
                continue
            sx, sy = pxy(bx + 0.2 * math.sin(t + bz), bz, camx)
            k = k_of(bz)
            se.poly(ctx, [(sx - 0.6 * k, sy), (sx - 0.2 * k, sy - 0.25 * k), (sx + 0.5 * k, sy - 0.15 * k),
                          (sx + 0.4 * k, sy + 0.15 * k)])
            ctx.set_source_rgba(0.9, 0.97, 1.0, 0.9)
            ctx.fill()
    # floor (side walls give it thickness)
    fp = floor_poly(hx, hz, camx)
    d = 0.5
    front = [fp[0], fp[1], (fp[1][0], fp[1][1] + d * k_of(ZC - hz)), (fp[0][0], fp[0][1] + d * k_of(ZC - hz))]
    se.poly(ctx, front)
    ctx.set_source_rgb(*se.lit({"lava": (0.25, 0.25, 0.3), "mud": (0.45, 0.32, 0.18), "ice": (0.55, 0.75, 0.9)}[ARENA]))
    ctx.fill()
    se.poly(ctx, fp)
    top = {"lava": (0.52, 0.53, 0.58), "mud": (0.72, 0.56, 0.36), "ice": (0.85, 0.94, 1.0)}[ARENA]
    g = cairo.LinearGradient(0, fp[2][1], 0, fp[0][1])
    g.add_color_stop_rgb(0, *se.lit(se.shade(top, 0.85)))
    g.add_color_stop_rgb(1, *se.lit(top))
    ctx.set_source(g)
    ctx.fill()
    ctx.save()
    se.poly(ctx, fp)
    ctx.clip()
    ctx.set_line_width(2)
    if ARENA == "lava":                                          # steel plates + rivets
        ctx.set_source_rgba(0.2, 0.2, 0.25, 0.6)
        for gx in np.arange(-HX0, HX0 + 0.1, 2.5):
            a, b = pxy(gx, ZC - HZ0, camx), pxy(gx, ZC + HZ0, camx)
            ctx.move_to(*a)
            ctx.line_to(*b)
            ctx.stroke()
        for gz in np.arange(ZC - HZ0, ZC + HZ0 + 0.1, 2.0):
            a, b = pxy(-HX0, gz, camx), pxy(HX0, gz, camx)
            ctx.move_to(*a)
            ctx.line_to(*b)
            ctx.stroke()
    elif ARENA == "mud":                                         # tyre tracks
        ctx.set_source_rgba(0.45, 0.32, 0.18, 0.5)
        for q in range(6):
            pts = [pxy(-HX0 + i * 1.0, ZC - 3 + q * 1.2 + 0.6 * math.sin(i * 0.5 + q), camx) for i in range(20)]
            ctx.move_to(*pts[0])
            for p in pts[1:]:
                ctx.line_to(*p)
            ctx.stroke()
    else:                                                        # ice shine streaks
        ctx.set_source_rgba(1, 1, 1, 0.6)
        ctx.set_line_width(5)
        for q in range(7):
            gx = -8 + q * 2.6
            a, b = pxy(gx, ZC - 1.5, camx), pxy(gx + 1.6, ZC + 1.2, camx)
            ctx.move_to(*a)
            ctx.line_to(*b)
            ctx.stroke()
    ctx.restore()
    # hazard-striped edge (flashes red while the floor shrinks)
    ctx.set_line_width(9)
    se.poly(ctx, fp)
    ctx.set_source_rgba(*((1, 0.15, 0.1, 0.95) if flash else (1, 0.85, 0.1, 0.95)))
    ctx.stroke()


def draw_hpbar(ctx, sx, sy, hp, k):
    w, h = 1.9 * k, 0.24 * k
    se.rrect(ctx, sx - w / 2 - 3, sy - 3, w + 6, h + 6, 6)
    ctx.set_source_rgba(0.05, 0.05, 0.15, 0.8)
    ctx.fill()
    col = (0.2, 0.85, 0.3) if hp > 60 else (0.98, 0.78, 0.1) if hp > 30 else (0.95, 0.2, 0.15)
    ctx.rectangle(sx - w / 2, sy, w * max(0.0, hp) / 100, h)
    ctx.set_source_rgb(*col)
    ctx.fill()


def draw_hud(ctx, cars, t):
    se.draw_text(ctx, "SMASH ARENA!", W / 2, 150, 92, fill=(1, 0.86, 0.12))
    for i, c in enumerate(cars):
        y = 260 + i * 74
        out = c["out"] is not None and t >= c["out"]
        se.rrect(ctx, 30, y - 30, 470, 62, 16)
        ctx.set_source_rgba(0.05, 0.05, 0.15, 0.7)
        ctx.fill()
        ctx.arc(70, y, 14, 0, 2 * math.pi)
        ctx.set_source_rgb(*se.VEHICLES[c["key"]]["color"])
        ctx.fill()
        se.draw_text(ctx, nick(c["key"]).upper(), 175, y + 1, 36, max_w=170,
                     fill=(0.55, 0.55, 0.6) if out else (1, 1, 1))
        if out:
            se.draw_text(ctx, "OUT", 390, y + 1, 38, fill=(0.95, 0.25, 0.2))
        else:
            hp = rec_at(c, "hp_rec", t)
            ctx.rectangle(285, y - 12, 200, 24)
            ctx.set_source_rgba(1, 1, 1, 0.15)
            ctx.fill()
            col = (0.2, 0.85, 0.3) if hp > 60 else (0.98, 0.78, 0.1) if hp > 30 else (0.95, 0.2, 0.15)
            ctx.rectangle(285, y - 12, 200 * hp / 100, 24)
            ctx.set_source_rgb(*col)
            ctx.fill()


def draw_debris(ctx, ev, t, camx, airborne):
    _, et, x, z, strength, sd, ca, cb = ev
    age = t - et
    if not 0 <= age < 3.5:
        return
    rng = np.random.default_rng(sd)
    n = 3 + int(strength * 5)
    for j in range(n):
        vx, vz, vh = float(rng.uniform(-4, 4)), float(rng.uniform(-2, 2)), float(rng.uniform(3, 7)) * strength
        tl = 2 * vh / 22.0
        a = min(age, tl)
        hh = max(0.0, vh * a - 11.0 * a * a)
        if (hh > 0.05) != airborne:
            continue
        px, pz = x + vx * a * 0.8, z + vz * a * 0.8
        sx, sy = pxy(px, pz, camx)
        k = k_of(pz)
        ctx.save()
        ctx.translate(sx, sy - hh * k)
        ctx.rotate(age * 9 * (1 if j % 2 else -1) if age < tl else j)
        col = ca if j % 3 == 0 else cb if j % 3 == 1 else (0.75, 0.75, 0.8)
        ctx.rectangle(-0.25 * k, -0.1 * k, 0.5 * k, 0.2 * k)
        ctx.set_source_rgba(*se.lit(col), max(0.0, min(1.0, (3.5 - age) / 0.6)))
        ctx.fill()
        ctx.restore()


def draw_impact(ctx, ev, t, camx):
    _, et, x, z, strength, *_ = ev
    age = t - et
    if not 0 <= age < 0.35:
        return
    sx, sy = pxy(x, z, camx)
    k = k_of(z)
    for j in range(8):
        ang = j * math.pi / 4 + 0.3
        r0, r1 = (0.6 + age * 4) * k, (1.2 + age * 7) * k * (0.6 + strength)
        ctx.move_to(sx + math.cos(ang) * r0, sy - 1.0 * k + math.sin(ang) * r0)
        ctx.line_to(sx + math.cos(ang) * r1, sy - 1.0 * k + math.sin(ang) * r1)
    ctx.set_source_rgba(1, 0.95, 0.4, 1 - age / 0.35)
    ctx.set_line_width(max(3, 0.12 * k))
    ctx.stroke()
    se.star(ctx, sx, sy - 1.0 * k, (0.7 + strength) * k * (1 - age / 0.35 * 0.5), age * 6)
    ctx.set_source_rgba(1, 1, 1, 1 - age / 0.35)
    ctx.fill()


def draw_out_fx(ctx, c, t, camx):
    """Ring-out splash / lava burst, wreck smoke."""
    if c["out"] is None:
        return
    age = t - c["out"]
    if age < 0:
        return
    x, z = R.state(c, t)[0], R.state(c, t)[1]
    sx, sy = pxy(x, z, camx)
    k = k_of(z)
    if c["out_kind"] == "ring" and 0.3 < age < 2.2:
        a = age - 0.3
        col = {"lava": (1, 0.6, 0.1), "mud": (0.4, 0.27, 0.14), "ice": (0.85, 0.95, 1.0)}[ARENA]
        for j in range(12):
            ang = math.pi * (0.1 + 0.8 * j / 11)
            r = (1 + a * 5) * k
            ctx.arc(sx + math.cos(ang) * r, sy - math.sin(ang) * r * 0.9 + a * a * 6 * k, (0.35 - a * 0.12) * k + 2,
                    0, 2 * math.pi)
            ctx.set_source_rgba(*col, max(0.0, 1 - a / 1.9))
            ctx.fill()
    if c["out_kind"] == "wreck" or rec_at(c, "hp_rec", t) < 30:
        dark = 0.15 if c["out_kind"] == "wreck" and age >= 0 else 0.35
        for j in range(6):
            p = ((t * 0.9) + j / 6) % 1.0
            ctx.arc(sx + (p * 0.8 - 0.3) * k, sy - (2.0 + p * 3.0) * k, (0.35 + p * 0.7) * k, 0, 2 * math.pi)
            ctx.set_source_rgba(dark, dark, dark + 0.02, 0.55 * (1 - p))
            ctx.fill()


# ------------------------------------------------------------------ audio
def crowd(dur, seed=3):
    rng = np.random.default_rng(seed)
    n = int(dur * se.SR)
    noise = rng.normal(0, 1, n)
    k = int(0.004 * se.SR)
    smooth = np.convolve(noise, np.ones(k) / k, "same")
    env = np.minimum(1.0, np.linspace(0, 1, n) * 5) * np.exp(-np.linspace(0, dur, n) * 1.3)
    return smooth * env * 3


def horn():
    return np.concatenate([se.tone(440, 0.22, "tri"), se.tone(330, 0.22, "tri"), se.tone(440, 0.22, "tri")])


def build_audio(frames, events, winner, star_t, replay, lines, voice, out_of, cta_start):
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
    for t_want, text in lines:
        a = se.tts(text)
        t0 = max(t_want, busy + 0.15)
        place(narr, a, t0)
        busy = t0 + len(a) / se.SR
    wrel, amp, pitch = [], [], []
    for mode, t in frames:
        v = R.state(winner, t)[5] if mode != "cta" else 0.0
        wrel.append(v / se.VEHICLES[winner["key"]]["wheel_r"] * 1.6)
        amp.append(0.0 if mode == "cta" else 0.55 + 0.45 * min(1.0, v / 10))
        pitch.append(1.0 if mode == "race" else 0.6)
    base, kk = se.VEHICLES[winner["key"]]["engine"]
    place(eng, se.synth_engine(np.array(wrel), np.array(amp), np.array(pitch), base, kk, seed=3), 0.0)
    place(sfx, se.tone(660, 0.12, "sine", decay=0.08), 0.02, 0.5)
    place(sfx, se.tone(990, 0.22, "sine", decay=0.12), 0.5, 0.6)

    def ev_sfx(ev, o, slow=1.0):
        kind = ev[0]
        if kind == "hit":
            s = ev[4]
            sig = se.synth_impact(0.4 + 0.6 * s, seed=ev[5] % 50)
            place(sfx, se.stretch(sig, slow) if slow != 1 else sig, o, 0.7 + 0.4 * s)
            if s > 0.5:
                place(sfx, se.synth_shatter(seed=ev[5] % 20), o + 0.03, 0.35)
                place(sfx, crowd(1.4, seed=ev[5]), o + 0.1, 0.25)
        elif kind == "ringout":
            if ARENA == "lava":
                place(sfx, se.synth_lava_plunge(), o + 0.3, 0.9)
            elif ARENA == "mud":
                place(sfx, se.synth_splash(1.0, seed=43, big=True), o + 0.3, 0.9)
            else:
                place(sfx, se.synth_splash(1.0, seed=47, big=True), o + 0.3, 0.9)
                place(sfx, se.synth_shatter(seed=5), o + 0.3, 0.4)
            place(sfx, crowd(2.0, seed=9), o + 0.4, 0.4)
        elif kind == "wreck":
            place(sfx, se.synth_impact(1.0, seed=31), o, 0.8)
            place(sfx, R.boing(), o + 0.2, 0.6)
            place(sfx, crowd(2.0, seed=11), o + 0.3, 0.4)
        elif kind == "shrink":
            place(sfx, horn(), o, 0.45)
        elif kind == "sudden":
            place(sfx, horn(), o, 0.6)

    for ev in events:
        ev_sfx(ev, out_of(ev[1]))
    place(sfx, se.synth_win(), out_of(winner["finish"]), 0.9)
    place(sfx, crowd(2.5, seed=21), out_of(winner["finish"]) + 0.1, 0.5)
    if replay:
        r0, a, b = replay
        place(sfx, se.synth_rewind(), r0, 0.6)
        for ev in events:
            if a <= ev[1] < b and ev[0] in ("hit", "ringout", "wreck"):
                ev_sfx(ev, r0 + (ev[1] - a) / 0.4, slow=0.5)
    for tap in (R.CTA_LIKE_T, R.CTA_SUB_T):
        place(sfx, se.tone(1300, 0.06, "sine", decay=0.02), cta_start + tap, 0.8)
    place(sfx, se.tone(1760, 0.8, "sine", decay=0.35) + se.tone(2637, 0.8, "sine", decay=0.25) * 0.5,
          cta_start + R.CTA_SUB_T + 0.05, 0.6)
    bgm = se.synth_bgm(total + 1, style=se.th_time()["music"])
    bgm = bgm[:n] if len(bgm) >= n else np.pad(bgm, (0, n - len(bgm)))
    talk = np.convolve((np.abs(narr) > 0.01).astype(float), np.ones(int(0.25 * se.SR)) / (0.25 * se.SR), "same")
    duck = 1.0 - (1.0 - 10 ** (-se.DUCK_DB / 20)) * np.clip(talk * 3, 0, 1)
    mix = (se.peak(narr) * se.VOL_NARR + se.peak(eng) * se.VOL_ENGINE * 0.8 * duck + se.peak(bgm) * se.VOL_BGM * duck
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
    ap.add_argument("--arena", default="", choices=["", *ARENAS])
    opt = ap.parse_args()
    se.load_cast()
    se.detect_font()
    # race25d's car drawing uses race25d's projection + mood: point them at the arena versions
    R.k_of, R.ground_y, R.mood_of = k_of, ground_y, mood
    active = registry._active(None)
    name = opt.name or f"SIM_SMASH25D_{ENGINE_VERSION.upper()}_S{opt.seed:03d}"
    if not opt.preview_only and registry.find_seed(SERIES, ENGINE_VERSION, opt.seed):
        print(f"[smash] STOP: seed {opt.seed} sudah dipakai untuk {SERIES}. Pakai seed lain.", flush=True)
        raise SystemExit(1)
    appearances = {}
    for e in active:
        for vk in e.get("vehicles", []):
            appearances[vk] = appearances.get(vk, 0) + 1
    used_arenas = [e.get("arena") for e in active if e.get("series") == SERIES]
    params = setup(opt.seed, appearances, used_arenas, opt.arena or None)
    se.make_theme(opt.seed, used=[e.get("theme", "") for e in active if e.get("theme")])
    uses = {v: 0 for v in se.VOICES}
    for e in active:
        if e.get("voice") in uses:
            uses[e["voice"]] += 1
    vr = np.random.default_rng(5100 + opt.seed)
    tie = {v: float(vr.random()) for v in se.VOICES}
    voice = min(se.VOICES, key=lambda v: (uses[v], tie[v]))
    cars, events, hits, winner = simulate(opt.seed)
    for st in shrink_times():
        if st < winner["finish"]:
            events.append(("shrink", st, 0.0, ZC))
    events.sort(key=lambda e: e[1])
    frames, replay, star_t, star, cta_start = build_timeline(cars, hits, winner)
    outs = sorted([c for c in cars if c["out"] is not None and c is not winner], key=lambda c: c["out"])
    print(f"[smash] {name} arena={ARENA} theme={se.THEME_ID} voice={voice} cast={[nick(c['key']) for c in cars]} "
          f"hits={len(hits)} big={sum(h['rel'] > 6 for h in hits)} "
          f"outs={[(nick(c['key']), c['out_kind'], round(c['out'], 1)) for c in outs]} winner={nick(winner['key'])} "
          f"hp={round(winner['hp'])} battle={winner['finish']:.1f}s frames={len(frames)} ({len(frames) / FPS:.1f}s)",
          flush=True)
    race_idx = [(j, ft) for j, (mode, ft) in enumerate(frames) if mode == "race"]

    def out_of(t):
        for j, ft in race_idx:
            if ft >= t:
                return j / FPS
        return len(frames) / FPS

    names = [nick(c["key"]) for c in cars]
    arena_word = {"lava": "the lava ring", "mud": "the mud pit", "ice": "the ice rink"}[ARENA]
    lines = [(0.15, f"Welcome to the Smash Arena! {names[0]}, {names[1]}, {names[2]} and {names[3]} "
                    f"battle on {arena_word}. Only one car survives!")]
    story = []
    shr = [e for e in events if e[0] == "shrink"]
    if shr:
        story.append((shr[0][1], "Watch out! The arena is shrinking!"))
    for c in outs:
        story.append((c["out"], ARENAS[ARENA]["out_line"].format(n=nick(c["key"])) if c["out_kind"] == "ring"
                      else f"{nick(c['key'])} is wrecked! {nick(c['key'])} is out!"))
    bigh = sorted([h for h in hits if h["rel"] > 7], key=lambda h: -h["rel"])[:2]
    for h in bigh:
        if all(abs(h["t"] - s[0]) > 2.5 for s in story):
            story.append((h["t"], f"Wham! {nick(h['a']['key'])} smashes into {nick(h['b']['key'])}!"))
    for tt, txt in sorted(story):
        lines.append((out_of(tt) + 0.15, txt))
    lines.append((out_of(winner["finish"]) + 0.2,
                  f"{nick(winner['key'])} is the last car standing! {nick(winner['key'])} wins!"))
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
    se.write_wav(wav, build_audio(frames, events, winner, star_t, replay, lines, voice, out_of, cta_start))
    silent = f"{se.WORK}/v_{name}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", silent],
                          stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    marks = {int(out_of(2.5) * FPS): "start"}
    for c in outs:
        marks[int(out_of(c["out"] + 0.35) * FPS)] = f"out_{nick(c['key']).lower()}"
    if bigh:
        marks.setdefault(int(out_of(bigh[0]["t"] + 0.05) * FPS), "bighit")
    marks[int(out_of(winner["finish"] + 0.8) * FPS)] = "winner"
    marks[int((cta_start + 1.5) * FPS)] = "outro"
    hit_ev = [e for e in events if e[0] == "hit"]
    camx, zoom, prev_mode, empty_frames = None, 1.0, None, 0
    for fi, (mode, t) in enumerate(frames):
        st = {id(c): R.state(c, t) for c in cars}
        show = [c for c in cars if c["out"] is None or t < c["out"] + 1.6]
        focus = None
        for h in hits:                                           # zoom in a little on big hits
            if h["rel"] > 7 and -0.2 < t - h["t"] < 0.8:
                focus = (h["x"], h["z"])
        if mode == "replay" and star is not None:
            focus = (st[id(star)][0], st[id(star)][1])
        if (winner["finish"] is not None and t >= winner["finish"]) or mode == "cta":
            focus = (st[id(winner)][0], st[id(winner)][1])
        xs = [st[id(c)][0] for c in show]
        lo, hi = min(xs) - 4.0, max(xs) + 4.0
        mid = (lo + hi) / 2
        fit = float(np.clip(W * 0.95 / ((hi - lo) * k_of(ZC - 1)), 0.78, 1.15))
        target, want = (mid, fit)
        if focus is not None:
            target = 0.6 * focus[0] + 0.4 * mid
            want = min(1.3, max(fit, 1.05) * (1.15 if mode == "replay" else 1.05))
        cut = camx is None or mode != prev_mode
        punch = 1.0
        for e in hit_ev:
            if e[4] > 0.5 and 0 <= t - e[1] < 0.3:
                punch = max(punch, 1 + 0.07 * math.sin(math.pi * (t - e[1]) / 0.3))
        camx = target if cut else camx + (target - camx) * (0.25 if mode == "replay" else 0.1)
        zoom = want * punch if cut else zoom + (want * punch - zoom) * 0.1
        prev_mode = mode
        if not any(0 < 540 + (st[id(c)][0] - camx) * k_of(st[id(c)][1]) * zoom < W for c in show):
            empty_frames += 1
        shx = shy = 0.0
        for e in hit_ev:
            if e[4] > 0.45 and 0 <= t - e[1] < 0.35:
                amp = 18 * e[4] * (1 - (t - e[1]) / 0.35)
                shx, shy = amp * math.sin(t * 90), amp * math.cos(t * 70)
        flash = any(0 <= t - s < 1.3 and int((t - s) * 6) % 2 == 0 for s in shrink_times())
        cheer = 1.0 if any(0 <= t - e[1] < 1.5 for e in events if e[0] in ("ringout", "wreck")) or \
            (t >= winner["finish"]) else 0.3
        se.draw_sky(ctx, camx * 0.35, WORLD_DY / se.S, 1.0)
        ctx.save()
        ctx.translate(0, WORLD_DY)
        ctx.translate(540 + shx, PIV_Y + shy)
        ctx.scale(zoom, zoom)
        ctx.translate(-540, -PIV_Y)
        draw_stands(ctx, camx, t, cheer)
        draw_arena(ctx, camx, t, flash)
        for e in hit_ev:
            draw_debris(ctx, e, t, camx, airborne=False)
        heads = {}
        for c in sorted(cars, key=lambda c: -st[id(c)][1]):
            sink = rec_at(c, "sink_rec", t)
            if sink >= 1.0:
                continue
            if sink > 0:
                ctx.push_group()
            hd = R.draw_car(ctx, c, t, camx)
            if sink > 0:
                ctx.pop_group_to_source()
                ctx.paint_with_alpha(1 - sink)
            draw_out_fx(ctx, c, t, camx)
            if hd is not None:
                heads[id(c)] = (540 + (hd[0] - 540) * zoom + shx, PIV_Y + (hd[1] - PIV_Y) * zoom + shy + WORLD_DY,
                                hd[2], c)
                if c["out"] is None or t < c["out"]:
                    draw_hpbar(ctx, hd[0], hd[1] - 0.75 * hd[2], rec_at(c, "hp_rec", t), hd[2])
        for e in hit_ev:
            draw_debris(ctx, e, t, camx, airborne=True)
            draw_impact(ctx, e, t, camx)
        ctx.restore()
        se.draw_weather(ctx, fi / FPS)
        if mode != "cta":
            for sx, sy, k, c in heads.values():
                for h in hits:
                    if h["rel"] > 6 and h["b"] is c:
                        R.bubble(ctx, HIT_BUBBLES[int(h["t"] * 7) % len(HIT_BUBBLES)], sx, sy, t - h["t"] - 0.05,
                                 k * zoom)
                if c["out"] is not None and c is not winner:
                    R.bubble(ctx, ARENAS[ARENA]["bubble"] if c["out_kind"] == "ring" else "I'M OUT!", sx, sy,
                             t - c["out"] - 0.1, k * zoom)
                if c is winner:
                    R.bubble(ctx, "CHAMPION!", sx, sy, t - winner["finish"] - 0.3, k * zoom)
            draw_hud(ctx, cars, t)
        if mode == "race":
            se.draw_ready_go(ctx, t)
            for s in shrink_times():
                if 0 <= t - s < 1.6 and s < winner["finish"]:
                    a = t - s
                    sc = se.ease_out_back(min(1.0, a / 0.3)) * min(1.0, (1.6 - a) / 0.3)
                    ctx.save()
                    ctx.translate(540, 640)
                    ctx.scale(sc, sc)
                    se.draw_text(ctx, "ARENA SHRINKING!", 0, 0, 84, fill=(1, 0.3, 0.2))
                    ctx.restore()
        if mode == "replay":
            se.draw_replay_overlay(ctx, fi / FPS)
        if t >= winner["finish"] and mode != "replay":
            age = t - winner["finish"] if mode == "race" else 2.0
            se.draw_confetti(ctx, age)
            s = se.ease_out_back(min(1.0, age / 0.4))
            ctx.save()
            ctx.translate(540, 620 if mode == "cta" else 700)
            ctx.scale(s, s)
            se.draw_text(ctx, f"{nick(winner['key']).upper()} WINS!", 0, 0, 120, fill=(1, 0.86, 0.12))
            ctx.restore()
        if mode == "cta":
            R.draw_cta(ctx, fi / FPS - cta_start)
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
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type:format=duration", "-of",
                            "json", out], capture_output=True, text=True)
    pj = json.loads(probe.stdout or "{}")
    dur = float(pj.get("format", {}).get("duration", 0))
    kinds = [s["codec_type"] for s in pj.get("streams", [])]
    checks = {"video+audio streams": "video" in kinds and "audio" in kinds,
              "duration 20-60 s": 20 <= dur <= 60,
              "one winner, 3 cars out": len(outs) == 3,
              "battle 12-38 s": 12 <= winner["finish"] <= 38,
              "at least 4 big hits": sum(h["rel"] > 6 for h in hits) >= 4,
              "has replay": replay is not None,
              "previews": all(os.path.exists(os.path.join(prev, f"{m}.png")) for m in ("winner", "outro")),
              "no frame without a car": empty_frames == 0}
    passed = all(checks.values())
    outcomes = [("win" if c is winner else f"p{c['place']}+{c['out_kind']}") for c in cars]
    track_id = "smash25d_" + hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()[:8] + "@" + se.THEME_ID
    title = TITLES[opt.seed % len(TITLES)]
    folder_rel = os.path.relpath(out_dir, se.BASE)
    manifest = dict(
        video_id=name, status="RENDERED_PENDING_APPROVAL" if passed else "CHECKS_FAILED",
        engine=f"smash25d {ENGINE_VERSION}", series=SERIES, seed=opt.seed, fps=FPS, duration=round(dur, 2),
        params=params, arena=ARENA, theme=se.THEME, theme_id=se.THEME_ID, voice=voice, outcomes=outcomes,
        checks=checks, cta=se.CTA, title_base=title, title=f"{title} #Shorts",
        description=(f"{', '.join(names[:3])} and {names[3]} enter the Smash Arena on {arena_word}! 💥 "
                     "Last car standing wins!\n\n"
                     "Watch till the end for the slow-motion replay! 🎬\n\n🏆 Comment your champion below!\n"
                     f"🔔 Subscribe to {se.CHANNEL} for new car battles every day.\n\n"
                     "#Shorts #SmashArena #CartoonCars #CarCrash #MegaWheelArena"),
        tags=TAGS + [se.VEHICLES[c["key"]]["display"].split(" THE ")[1].lower() for c in cars] + [ARENA],
        narration=[txt for _, txt in lines],
        assets="100% procedurally generated (cairo 2.5D render + synthesized audio), narration Edge-TTS " + voice,
        video_path=out, preview_dir=prev)
    with open(os.path.join(out_dir, f"{name}.json"), "w") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, f"{name}_audit.md"), "w") as fh:
        fh.write(f"# Checks {name}\n\n" + "\n".join(f"- {'✅' if ok else '❌'} {k}" for k, ok in checks.items())
                 + f"\n\nDuration {dur:.1f} s · arena {ARENA} · theme {se.THEME_ID} · voice {voice}\n")
    print(f"[smash] checks {'PASS' if passed else 'FAIL'} {checks} empty_frames={empty_frames}", flush=True)
    if not opt.preview_only:
        registry.upsert(dict(video_id=name, series=SERIES, engine_version=ENGINE_VERSION, seed=opt.seed, created=date,
                             render_date=date, vehicles=[c["key"] for c in cars], track_id=track_id, arena=ARENA,
                             theme=se.THEME_ID, voice=voice, outcomes=outcomes, duration=round(dur, 2),
                             status="RENDERED_PENDING_APPROVAL" if passed else "AUDIT_FAILED", folder=folder_rel,
                             audit=f"{folder_rel}/{name}_audit.md", episode=None, season=None, upload_date=None,
                             youtube_url=None))
    print("[result] " + json.dumps(dict(video_id=name, video=out, duration=round(dur, 1), passed=passed)), flush=True)
    if not passed:
        raise SystemExit(5)


if __name__ == "__main__":
    main()
