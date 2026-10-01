#!/usr/bin/env python3
"""MegaWheel Arena — series "race25d": 2.5D "paper cutout" lane race Shorts (approved style, user 2026-09-30).

The characters are drawn by the SAME functions as the 2D episodes (sim_engine.draw_body / draw_face /
draw_wheel, moods, themes, speed lines, splash, READY-GO, confetti, replay overlay), so they look exactly
like the 2D cast. Depth comes from lanes; far lanes are smaller and higher, dashes/props move with parallax.

HAZARD LIBRARY (v3.3): every video picks 3 different hazards, one per lane, from HAZARDS:
  puddle (spin across lanes + bump) · ramp (jump) · pothole · lava vent · concrete wall · crusher press
  (car squashed flat, BOING back) · laser gate (car split in two, patched) · meteor (blast + flip + crater)
  · UFO (beam lifts the car and drops it behind) · dragon fire (burnt, stops for a tire change, slower)
  · dragon ice (frozen in an ice block, shatters free). Cartoon slapstick, never gore (BLUEPRINT rule 7).
Lane-change AI: agile racers may swerve to a free lane to dodge a ground hazard they see coming (max 1 dodge
per video, 'NICE!'), so winning is skill as well as luck. End card: YouTube-style LIKE/SUBSCRIBE with a tapping
hand, highlight ring, +1, SUBSCRIBED + ringing bell.

Every seed varies: cast (rotation), lanes, hazards + positions, speeds (winner varies), theme (rotation),
narrator (en-US rotation). Timeline: READY-GO -> race -> winner + confetti -> INSTANT REPLAY of the most
spectacular hazard -> CTA. Hard rules: hard cuts between scenes, key car always in frame, check
"no frame without a car".

Usage (cd /root/video-engine):
  ./venv/bin/python generators/lanes25d/race25d.py --seed 1               # -> renders/megawheel_arena/pending/
  ./venv/bin/python generators/lanes25d/race25d.py --seed 1 --preview-only # -> work/lanes25d/previews/ (no registry)
  [--hazards crusher,laser,meteor]   force the hazard set (tests)
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

SERIES, ENGINE_VERSION = "race25d", "v2"             # v2: hazard library + dodge AI + YouTube end card
W, H, FPS = se.W, se.H, 30
F_PERSP, D0, LANE_D = 9000.0, 100.0, 25.0        # k(z) = F / (D0 + z*LANE_D): front lane 90 px/m, lane 3 ≈ 51
Y_H, CAM_H = 640.0, 13.0                         # ground_y = Y_H + CAM_H*k
WORLD_DY = -260.0                                # lift the road scene so the action sits mid-frame
POOL = ["sports", "police", "taxi", "f1", "bus", "firetruck", "icecream", "bigrig", "monster", "monster2"]
BIG = {"bus", "firetruck", "icecream", "bigrig"}
TITLES = ["4 Cars, 1 Finish Line! Who Wins? 🏁", "Crazy Obstacle Race! Who Survives? 🏁💥",
          "Meteors, Lasers & Lava! Who Wins the Race? 🏁", "Wildest Race Ever! Who Crosses First? 🏁"]
TAGS = ["cars", "car race", "racing", "cartoon cars", "race cars", "funny cars", "obstacle race", "shorts",
        "MegaWheel Arena"]

# ------------------------------------------------------------------ hazard library
# name: weight (pick chance), trigger lead (m before hazard x), bubble, narration, replay priority, slow-mo window
HAZARDS = {
    "puddle":  dict(weight=1.0, bubble="WHOA!", line="Whoa! {n} hits the water and spins out!", prio=5),
    "ramp":    dict(weight=1.0, bubble="YEEHAW!", line="{n} takes the ramp... big air!", prio=4, slow=(0.25, 1.35)),
    "pothole": dict(weight=0.8, bubble="OUCH!", line="Bump! {n} drops into a pothole!", prio=2),
    "lava":    dict(weight=1.0, bubble="HOT HOT!", line="Lava! {n} gets blasted!", prio=6),
    "wall":    dict(weight=0.9, bubble="OOF!", line="Crash! {n} slams into the wall!", prio=6),
    "crusher": dict(weight=1.1, bubble="SPLAT!", line="Splat! {n} gets squashed flat!", prio=8, slow=(-0.25, 0.45)),
    "laser":   dict(weight=1.1, bubble="YIKES!", line="Zap! The laser slices {n} in two!", prio=8),
    "meteor":  dict(weight=1.1, bubble="KABOOM!", line="Kaboom! A meteor hits {n}!", prio=9, slow=(-0.35, 0.8)),
    "ufo":     dict(weight=1.1, bubble="HELP!", line="Uh oh! A UFO grabs {n}!", prio=7),
    "dragon_fire": dict(weight=1.2, bubble="TOO HOT!", line="The dragon breathes fire! {n} needs new tires!",
                        prio=9, slow=(-0.1, 0.7)),
    "dragon_ice":  dict(weight=1.2, bubble="BRRR!", line="Brrr! The ice dragon freezes {n}!", prio=9,
                        slow=(-0.1, 0.7)),
}

# lane-change AI: racers see ground hazards coming and may swerve to a free lane (skill, not luck)
AGILITY = {"f1": 0.9, "sports": 0.85, "police": 0.75, "taxi": 0.7, "monster": 0.6, "monster2": 0.6,
           "icecream": 0.45, "firetruck": 0.4, "bus": 0.35, "bigrig": 0.3}
DODGEABLE = {"puddle": "puddle", "pothole": "pothole", "lava": "lava vent", "wall": "wall", "crusher": "crusher",
             "laser": "laser"}
MAX_DODGES = 1                                   # keeps at least 2 hazard hits per video

# per-video parameters (set in setup())
RACERS, HZ, FIN_X, SECONDS = [], [], 0.0, 0.0     # HZ: list of dict(type, lane, x)


def k_of(z):
    return F_PERSP / (D0 + z * LANE_D)


def ground_y(z):
    return Y_H + CAM_H * k_of(z)


def lane_xy(x, z, camx):
    return (x - camx) * k_of(z) + 540, ground_y(z)


def ease_out(p):
    p = min(1.0, max(0.0, p))
    return 1 - (1 - p) ** 2.2


def nick(vk):
    return se.VEHICLES[vk]["nick"]


# ------------------------------------------------------------------ per-seed setup
def setup(seed, appearances, forced=None):
    global RACERS, HZ, FIN_X, SECONDS
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
    names = list(HAZARDS)
    if forced:
        types = forced[:3]
    else:
        w = np.array([HAZARDS[h]["weight"] for h in names])
        types = [str(t) for t in r.choice(names, size=3, replace=False, p=w / w.sum())]
        if not any(t in DODGEABLE for t in types):               # always one ground hazard a racer can dodge
            g = [n for n in names if n in DODGEABLE]
            gw = np.array([HAZARDS[n]["weight"] for n in g])
            types[int(r.integers(3))] = str(r.choice(g, p=gw / gw.sum()))
    hz_lanes = [int(v) for v in r.permutation(4)[:3]]
    xs = [110.0 + i * 95.0 + float(r.uniform(-8, 8)) for i in range(3)]
    HZ = [dict(type=t, lane=hz_lanes[i], x=xs[i]) for i, t in enumerate(types)]
    FIN_X = xs[-1] + float(r.uniform(95, 115))
    SECONDS = FIN_X / 21.0 + 7.0
    return dict(cast=cast, lanes=lanes, hazards=[[h["type"], h["lane"], round(h["x"], 1)] for h in HZ],
                finish=round(FIN_X, 1))


# ------------------------------------------------------------------ scripted race (120 Hz kinematics)
def simulate(seed):
    rng = np.random.default_rng(9100 + seed)
    dt, n = 1 / 120, int(SECONDS * 120)
    cars = []
    for key, lane, v in RACERS:
        hz = None                                                # assigned when a hazard actually hits the car
        cars.append(dict(key=key, lane=lane, v0=v, x=4.0 - lane * 1.2, z=float(lane), h=0.0, vh=0.0, yaw=0.0,
                         pitch=0.0, sq=1.0, split=0.0, burn=0.0, patched=0.0, ice=0.0, tires=0.0, thawed=False, v=0.0, hz=hz, trig=None, land=None,
                         bump_t=None, finish=None, surge=float(rng.uniform(0, 6.28)), rec=[]))
    events = []
    decided, dodges = {}, [0]                            # (car, hazard) -> agility roll (made once)
    for h in HZ:
        h.pop("used", None)
    for i in range(n):
        t = i * dt
        for c in cars:
            go = min(1.0, t / 1.6)
            target = c["v0"] * (1 + 0.025 * math.sin(t * 0.7 + c["surge"]))
            if c.get("seek_t") is not None and t - c["seek_t"] < 0.05:
                target *= c["seek_k"]                            # blocked: sprint past / brake behind the neighbour
            a = (t - c["trig"]) if c["trig"] is not None else None
            freeze = False                                       # hazard holds the car still (x not integrated)
            if c["trig"] is None and c["finish"] is None:
                zl = int(round(c["z"]))
                if not c.get("dodge_t") and dodges[0] < MAX_DODGES:      # see a ground hazard coming -> swerve?
                    ahead = next((h for h in HZ if not h.get("used") and h["lane"] == zl and h["type"] in DODGEABLE
                                  and 9 < h["x"] - c["x"] < 40), None)
                    if ahead is not None:
                        key2 = (id(c), id(ahead))
                        if key2 not in decided:
                            ag = AGILITY.get(c["key"], 0.55)             # agile cars always try, big ones only sometimes
                            decided[key2] = ag >= 0.55 or rng.random() < ag
                        if decided[key2]:                        # keeps looking for a gap while there is room
                            free = [ln for ln in (zl - 1, zl + 1) if 0 <= ln <= 3
                                    and not any(o is not c and abs(o["z"] - ln) < 0.6 and abs(o["x"] - c["x"]) < 5.0
                                                for o in cars)
                                    and not any(not h2.get("used") and h2["lane"] == ln and -2 < h2["x"] - c["x"] < 30
                                                for h2 in HZ)]
                            if not free:
                                near = [o["x"] - c["x"] for o in cars if o is not c and abs(o["x"] - c["x"]) < 5.0
                                        and any(abs(o["z"] - ln) < 0.6 for ln in (zl - 1, zl + 1))]
                                c["seek_t"], c["seek_k"] = t, (0.8 if near and min(near) > 1.0 else 1.18)
                            else:
                                c["lane"], c["dodge_t"], c["dodged"] = free[0], t, ahead["type"]
                                dodges[0] += 1
                                events.append(("dodge", t, c["x"], float(free[0])))
                bw = se.VEHICLES[c["key"]]["body"][0]
                for h in HZ:                                     # a hazard hits whoever is in its lane when it arrives
                    if h.get("used") or abs(c["z"] - h["lane"]) > 0.35:
                        continue
                    lead = {"meteor": 0.0, "ufo": 0.0, "ramp": 0.0, "puddle": 2.0, "dragon_fire": 0.0,
                            "dragon_ice": 0.0}.get(h["type"], 0.5 * bw)
                    if h["x"] - lead <= c["x"] < h["x"] + 3.0:
                        h["used"] = True
                        c["hz"], c["trig"], a = h, t, 0.0
                        c["lane"] = h["lane"]
                        c["x0"] = c["x"]
                        events.append((h["type"], t, c["x"], float(c["lane"])))
                        break
            hz = c["hz"]
            if hz is not None and a == 0.0:
                    if hz["type"] in ("ramp",):
                        c["vh"] = 9.2
                    elif hz["type"] == "lava":
                        c["vh"], c["burn"] = 6.0, 1.0
                    elif hz["type"] == "meteor":
                        c["vh"], c["burn"] = 8.0, 1.0
            ty = hz["type"] if hz is not None else None
            if not (a is not None and ty in ("puddle", "wall")) and c["bump_t"] is None:
                c["z"] += float(np.clip(c["lane"] - c["z"], -1.9 * dt, 1.9 * dt))   # smooth lane change
            if a is not None:
                if ty == "puddle":
                    to_lane = c["lane"] - 1 if c["lane"] > 0 else 1
                    c["yaw"] = 4 * math.pi * ease_out(a / 1.4)
                    c["z"] = c["lane"] + (to_lane - c["lane"]) * 0.55 * ease_out(a / 1.0)
                    target *= 0.55 + 0.45 * min(1.0, max(0.0, (a - 1.2) / 2.5))
                elif ty in ("ramp", "lava", "meteor") and c["land"] is None:
                    c["vh"] -= 9.81 * dt
                    c["h"] = max(0.0, c["h"] + c["vh"] * dt)
                    if ty == "meteor":                           # full somersault while airborne
                        c["pitch"] = 2 * math.pi * min(1.0, a / 1.55)
                    else:
                        c["pitch"] = float(np.clip(c["vh"] * 0.035, -0.28, 0.28))
                    if c["h"] == 0.0 and c["vh"] < 0:
                        c["land"], c["pitch"] = t, 0.0
                        events.append(("land", t, c["x"], float(c["lane"])))
                    if ty == "meteor":
                        target *= 0.6
                elif ty == "pothole":
                    if a < 0.45:
                        c["h"] = -0.55 * math.sin(math.pi * a / 0.45 * 0.5)
                        c["pitch"] = -0.18 * math.sin(math.pi * a / 0.45)
                    elif a < 0.85:
                        c["h"] = -0.55 + 0.8 * math.sin(math.pi * (a - 0.45) / 0.8)
                        c["pitch"] = 0.12 * math.sin(math.pi * (a - 0.45) / 0.4)
                    else:
                        c["h"], c["pitch"] = max(0.0, c["h"] - 3 * dt), 0.0
                    target *= 0.5 + 0.5 * min(1.0, max(0.0, (a - 0.6) / 2.0))
                elif ty == "wall":
                    if a < 1.3:
                        freeze = True
                        c["v"] = 0.0
                        if a < 0.25:
                            c["x"] -= 3.2 * dt                   # bounce back off the wall
                        c["pitch"] = 0.08 * math.sin(a * 30) * max(0.0, 1 - a / 0.6)
                    side = 1 if c["lane"] < 3 else -1
                    c["z"] = c["lane"] + side * 0.45 * (ease_out((a - 1.0) / 0.5) if a < 2.4 else
                                                         1 - ease_out((a - 2.4) / 0.6))
                    target *= min(1.0, max(0.0, (a - 1.2) / 1.5))
                elif ty == "crusher":
                    if a < 1.35:
                        freeze = True
                        c["v"] = 0.0
                        c["sq"] = 0.26 if 0.05 < a < 1.1 else 1.0
                    else:
                        c["sq"] = 1 + 0.28 * math.sin((a - 1.35) * 24) * math.exp(-(a - 1.35) * 5)
                    target *= min(1.0, max(0.0, (a - 1.3) / 1.5))
                elif ty == "laser":
                    c["split"] = 0.75 * math.sin(math.pi * min(a, 1.3) / 1.3) if a < 1.3 else 0.0
                    c["patched"] = 1.0 if a >= 1.3 else 0.0
                    target *= 0.6 + 0.4 * min(1.0, max(0.0, (a - 1.0) / 2.0))
                elif ty == "dragon_fire":                       # scorched: stop for a tire change, then slower
                    c["burn"] = 1.0 if a >= 0.1 else c["burn"]
                    if a < 0.45:
                        target *= 0.25
                    elif a < 2.1:
                        freeze = True
                        c["v"] = 0.0
                        c["tires"] = 1.0 if a > 0.6 else 0.0
                    else:
                        c["tires"] = 0.0
                        target *= 0.75 + 0.25 * min(1.0, (a - 2.1) / 3.0)
                elif ty == "dragon_ice":                        # frozen in an ice block, then shatters free
                    if 0.25 < a < 1.95:
                        freeze = True
                        c["v"] = 0.0
                        c["ice"] = 1.0
                    else:
                        c["ice"] = 0.0
                        if a >= 1.95 and not c["thawed"]:
                            c["thawed"] = True
                            events.append(("thaw", t, c["x"], float(c["lane"])))
                        if a < 0.25:
                            target *= 0.4
                        else:
                            target *= min(1.0, (a - 1.95) / 1.5)
                elif ty == "ufo":
                    if a < 2.2:
                        freeze = True
                        c["v"] = 0.0
                        c["h"] = 4.2 * ease_out(a / 1.0)
                        c["x"] = c["x0"] - 14.0 * ease_out((a - 0.6) / 1.3)
                        c["pitch"] = 0.12 * math.sin(a * 5)
                        c["vh"] = 0.0
                    elif c["h"] > 0:
                        c["vh"] -= 9.81 * dt
                        c["h"] = max(0.0, c["h"] + c["vh"] * dt)
                        c["pitch"] = 0.0
                        if c["h"] == 0.0:
                            events.append(("land", t, c["x"], float(c["lane"])))
                    target *= min(1.0, max(0.0, (a - 2.4) / 1.5))
            if c["land"] is not None and ty == "ramp" and t - c["land"] < 2.5:
                target *= 1.1
            if c["bump_t"] is not None and 0 < t - c["bump_t"] < 1.0:
                target *= 0.9
            if c["finish"] is not None:
                target = max(4.0, c["v"] * 0.985)
            if not freeze:
                c["v"] += (target * go - c["v"]) * 0.03
                c["x"] += c["v"] * dt
            if c["finish"] is None and c["x"] >= FIN_X:
                c["finish"] = t
            if i % 4 == 0:
                c["rec"].append((c["x"], c["z"], c["h"], c["yaw"], c["pitch"], c["v"], c["sq"], c["split"],
                                 c["burn"], c["patched"], c["ice"], c["tires"]))
        sp = next((c for c in cars if c["hz"] and c["hz"]["type"] == "puddle" and c["trig"] is not None
                   and t - c["trig"] < 1.2), None)
        if sp:
            to_lane = sp["lane"] - 1 if sp["lane"] > 0 else 1
            for c in cars:
                if c is not sp and c["lane"] == to_lane and c["bump_t"] is None and abs(c["x"] - sp["x"]) < 5 \
                        and abs(sp["z"] - to_lane) < 0.75:
                    c["bump_t"] = t
                    events.append(("bump", t, c["x"], float(to_lane)))
        for c in cars:
            if c["bump_t"] is not None and not (c["hz"] and c["hz"]["type"] == "wall" and c["trig"] is not None):
                aa = t - c["bump_t"]
                side = -1 if c["lane"] == 0 else 1
                c["z"] = c["lane"] + side * 0.28 * math.sin(min(math.pi, aa * 2.6)) if aa < 1.3 else float(c["lane"])
    for place, c in enumerate(sorted(cars, key=lambda c: c["finish"] if c["finish"] else 1e9), start=1):
        c["place"] = place
    return cars, events


def hit_cars(cars):
    return [c for c in cars if c["hz"] is not None and c["trig"] is not None]


# ------------------------------------------------------------------ timeline: race -> celebrate -> replay -> CTA
def build_timeline(cars):
    winner = min(cars, key=lambda c: c["finish"] or 1e9)
    hits = hit_cars(cars)
    slows = sorted(((c["trig"] + HAZARDS[c["hz"]["type"]]["slow"][0], c["trig"] + HAZARDS[c["hz"]["type"]]["slow"][1])
                    for c in hits if "slow" in HAZARDS[c["hz"]["type"]]), key=lambda w: w[0])[:2]
    frames, t = [], 0.0
    race_end = min(SECONDS - 0.2, (winner["finish"] or SECONDS) + 1.8)
    while t < race_end:
        frames.append(("race", t))
        t += (0.35 if any(a < t < b for a, b in slows) else 1.0) / FPS
    star = max(hits, key=lambda c: HAZARDS[c["hz"]["type"]]["prio"], default=None)
    replay = None
    if star is not None:
        a, b = star["trig"] - 0.6, star["trig"] + 1.9
        replay = (len(frames) / FPS, a, b)
        t = a
        while t < b:
            frames.append(("replay", t))
            t += 0.4 / FPS
    cta_start = len(frames) / FPS
    for _ in range(int(4.8 * FPS)):
        frames.append(("cta", race_end - 0.1))
    return frames, winner, star, replay, cta_start


REC_N = 12


def state(c, t):
    f = min(t * 30, len(c["rec"]) - 1.001)
    i = int(f)
    a = f - i
    r0, r1 = c["rec"][i], c["rec"][i + 1]
    return tuple(r0[j] * (1 - a) + r1[j] * a for j in range(REC_N))


def mood_of(c, t, x):
    if c["finish"] is not None and t > c["finish"] and c.get("place") == 1:
        return "happy"
    if c["trig"] is not None:
        a = t - c["trig"]
        if 0 <= a < 1.4:
            return "whoa"
        if 1.4 <= a < 3.5:
            return "dizzy"
    if c["bump_t"] is not None and 0 <= t - c["bump_t"] < 1.2:
        return "scared"
    if c.get("dodge_t") is not None and 0 <= t - c["dodge_t"] < 1.3:
        return "happy"
    zz = state(c, t)[1]
    if (c["trig"] is None or t < c["trig"]) and any(abs(h["lane"] - zz) < 0.5 and 0 < h["x"] - x < 22 for h in HZ):
        return "scared"
    return "normal"


# ------------------------------------------------------------------ drawing: world
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
    if se.THEME["weather"] == "rain":
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
    for row in range(8):
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
        elif loc == "desert":
            ctx.set_source_rgb(*se.lit((0.25, 0.6, 0.3)))
            se.rrect(ctx, sx - 0.3 * k * s, y - 3.2 * k * s, 0.6 * k * s, 3.2 * k * s, 0.3 * k * s)
            ctx.fill()
            se.rrect(ctx, sx - 1.0 * k * s, y - 2.4 * k * s, 0.45 * k * s, 1.2 * k * s, 0.22 * k * s)
            ctx.fill()
        elif loc == "beach":
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
        else:
            ctx.rectangle(sx - 0.25 * k, y - 2.6 * k * s, 0.5 * k, 2.6 * k * s)
            ctx.set_source_rgb(*se.lit((0.4, 0.26, 0.14)))
            ctx.fill()
            ctx.arc(sx, y - 3.4 * k * s, 1.7 * k * s, 0, 2 * math.pi)
            ctx.set_source_rgb(*se.lit((0.18, 0.5, 0.22)))
            ctx.fill()
            ctx.arc(sx - 0.5 * k * s, y - 3.8 * k * s, 1.0 * k * s, 0, 2 * math.pi)
            ctx.set_source_rgb(*se.lit((0.95, 0.96, 1.0) if se.THEME["weather"] == "snow" else (0.26, 0.62, 0.3)))
            ctx.fill()


def hz_trig(hz, cars):
    return next((c["trig"] for c in cars if c["hz"] is hz), None)


def draw_hazard_ground(ctx, hz, camx, t, cars):
    """Hazards that lie on / in the road (drawn before the cars)."""
    k = k_of(hz["lane"])
    sx, y = lane_xy(hz["x"], hz["lane"], camx)
    if not -900 < sx < W + 900:
        return
    ty, tr = hz["type"], hz_trig(hz, cars)
    if ty == "puddle":
        cx = sx + 2.5 * k
        ctx.save()
        ctx.translate(cx, y)
        ctx.scale(4.8 * k, 0.55 * k)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(*se.lit((0.3, 0.6, 1.0)), 0.9)
        ctx.fill()
        for j in range(4):
            ox = (j - 1.5) * 1.8 * k + 8 * math.sin(t * 3 + j)
            ctx.move_to(cx + ox - 0.5 * k, y - 0.1 * k)
            ctx.line_to(cx + ox + 0.5 * k, y - 0.1 * k)
            ctx.set_source_rgba(1, 1, 1, 0.7)
            ctx.set_line_width(max(2, k * 0.06))
            ctx.stroke()
    elif ty == "ramp":
        se.poly(ctx, [(sx - 5.5 * k, y), (sx, y), (sx, y - 1.3 * k)])
        ctx.set_source_rgb(*se.lit((0.85, 0.55, 0.25)))
        ctx.fill_preserve()
        ctx.set_source_rgb(0.3, 0.18, 0.08)
        ctx.set_line_width(3)
        ctx.stroke()
    elif ty in ("pothole", "meteor"):
        if ty == "meteor" and (tr is None or t < tr):
            return                                               # the crater appears on impact
        rx = (1.6 if ty == "pothole" else 2.4) * k
        ctx.save()
        ctx.translate(sx + (0.8 if ty == "pothole" else 0.0) * k, y)
        ctx.scale(rx, 0.32 * k)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.08, 0.07, 0.07)
        ctx.fill()
        ctx.set_source_rgba(0.45, 0.4, 0.38, 0.9)
        ctx.set_line_width(max(2, 0.07 * k))
        for j in range(5):                                       # cracks
            ang = j * 1.3
            ctx.move_to(sx + math.cos(ang) * rx, y + math.sin(ang) * 0.3 * k)
            ctx.line_to(sx + math.cos(ang) * rx * 1.35, y + math.sin(ang) * 0.42 * k)
            ctx.stroke()
        if ty == "meteor" and t - tr < 3.0:                      # glowing embers in the crater
            ctx.save()
            ctx.translate(sx, y)
            ctx.scale(rx * 0.6, 0.18 * k)
            ctx.arc(0, 0, 1, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgba(1, 0.45, 0.05, 0.8 * max(0.0, 1 - (t - tr) / 3.0))
            ctx.fill()
    elif ty == "lava":
        se.poly(ctx, [(sx - 1.2 * k, y), (sx - 0.4 * k, y - 0.15 * k), (sx + 0.5 * k, y + 0.05 * k),
                      (sx + 1.2 * k, y - 0.1 * k), (sx + 0.3 * k, y + 0.2 * k)])
        ctx.set_source_rgb(0.25, 0.08, 0.04)
        ctx.fill()
        glow = 0.5 + 0.5 * math.sin(t * 8)
        ctx.save()
        ctx.translate(sx, y)
        ctx.scale(0.9 * k, 0.12 * k)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(1, 0.45 + 0.2 * glow, 0.05, 0.9)
        ctx.fill()
    elif ty == "laser":
        for dz, post in ((-0.45, True), (0.45, True)):           # two posts, beam across the lane
            px, py = lane_xy(hz["x"], hz["lane"] + dz, camx)
            kk = k_of(hz["lane"] + dz)
            se.rrect(ctx, px - 0.18 * kk, py - 2.2 * kk, 0.36 * kk, 2.2 * kk, 0.08 * kk)
            ctx.set_source_rgb(*se.lit((0.35, 0.36, 0.42)))
            ctx.fill()
            ctx.arc(px, py - 2.2 * kk, 0.22 * kk, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.15, 0.15)
            ctx.fill()


def draw_hazard_front(ctx, hz, camx, t, cars):
    """Hazards that tower over / fall on the cars (drawn after the cars)."""
    k = k_of(hz["lane"])
    sx, y = lane_xy(hz["x"], hz["lane"], camx)
    ty, tr = hz["type"], hz_trig(hz, cars)
    if not -1200 < sx < W + 1200:
        return
    a = (t - tr) if tr is not None else None
    if ty == "wall":
        se.poly(ctx, [(sx - 0.1 * k, y), (sx + 0.9 * k, y), (sx + 0.9 * k, y - 1.7 * k), (sx - 0.1 * k, y - 1.7 * k)])
        ctx.set_source_rgb(*se.lit((0.72, 0.72, 0.75)))
        ctx.fill_preserve()
        ctx.set_source_rgb(0.2, 0.2, 0.25)
        ctx.set_line_width(3)
        ctx.stroke()
        for j in range(4):
            se.poly(ctx, [(sx - 0.1 * k, y - (0.3 + j * 0.35) * k), (sx + 0.9 * k, y - (0.5 + j * 0.35) * k),
                          (sx + 0.9 * k, y - (0.65 + j * 0.35) * k), (sx - 0.1 * k, y - (0.45 + j * 0.35) * k)])
            ctx.set_source_rgb(0.85, 0.1, 0.1)
            ctx.fill()
        if a is not None and 0 <= a < 1.2:                       # debris burst
            rng = np.random.default_rng(int(hz["x"]))
            for j in range(12):
                vx, vy = rng.uniform(-6, 3), rng.uniform(3, 8)
                px = sx + vx * a * k
                py = y - 1.0 * k - (vy * a - 4.9 * a * a) * k
                ctx.rectangle(px, py, 0.25 * k, 0.18 * k)
                ctx.set_source_rgb(*se.lit((0.6, 0.6, 0.62)))
                ctx.fill()
    elif ty == "crusher":
        top = y - 7.5 * k
        for dx in (-1.6, 1.6):                                   # frame posts
            se.rrect(ctx, sx + dx * k - 0.2 * k, top, 0.4 * k, 7.5 * k, 0.1 * k)
            ctx.set_source_rgb(*se.lit((0.3, 0.32, 0.38)))
            ctx.fill()
        se.rrect(ctx, sx - 2.0 * k, top - 0.5 * k, 4.0 * k, 0.6 * k, 0.1 * k)
        ctx.fill()
        if a is None:
            drop = 0.0
        elif a < 0:
            drop = 0.0
        elif a < 0.08:
            drop = a / 0.08
        elif a < 1.2:
            drop = 1.0
        else:
            drop = max(0.0, 1 - (a - 1.2) / 0.8)
        if tr is not None and -0.25 < t - tr < 0:                # slam starts just before contact
            drop = (t - tr + 0.25) / 0.25 * 0.9
        block_bottom = top + 1.2 * k + drop * (7.5 * k - 1.2 * k - 0.5 * k)
        ctx.set_source_rgb(*se.lit((0.35, 0.35, 0.4)))
        ctx.rectangle(sx - 0.25 * k, top, 0.5 * k, block_bottom - top - 1.0 * k)
        ctx.fill()
        se.rrect(ctx, sx - 1.5 * k, block_bottom - 1.0 * k, 3.0 * k, 1.0 * k, 0.12 * k)
        ctx.set_source_rgb(*se.lit((0.95, 0.75, 0.1)))
        ctx.fill_preserve()
        ctx.set_source_rgb(0.15, 0.12, 0.05)
        ctx.set_line_width(3)
        ctx.stroke()
        for j in range(5):                                       # hazard stripes on the press
            se.poly(ctx, [(sx - 1.4 * k + j * 0.6 * k, block_bottom - 0.9 * k), (sx - 1.1 * k + j * 0.6 * k, block_bottom - 0.9 * k),
                          (sx - 1.3 * k + j * 0.6 * k, block_bottom - 0.1 * k), (sx - 1.6 * k + j * 0.6 * k, block_bottom - 0.1 * k)])
            ctx.set_source_rgb(0.1, 0.1, 0.1)
            ctx.fill()
    elif ty == "laser":
        pa, pb = lane_xy(hz["x"], hz["lane"] - 0.45, camx), lane_xy(hz["x"], hz["lane"] + 0.45, camx)
        ka, kb = k_of(hz["lane"] - 0.45), k_of(hz["lane"] + 0.45)
        on = 0.7 + 0.3 * math.sin(t * 40)
        for hh in (0.6, 1.2, 1.8):
            ctx.move_to(pa[0], pa[1] - hh * ka)
            ctx.line_to(pb[0], pb[1] - hh * kb)
            ctx.set_source_rgba(1, 0.1, 0.15, on)
            ctx.set_line_width(max(3, 0.1 * k))
            ctx.stroke()
        if a is not None and 0 <= a < 1.3:                       # sparks at the cut
            rng = np.random.default_rng(int(t * 60))
            for j in range(14):
                ang = rng.uniform(0, 2 * math.pi)
                ln = rng.uniform(0.3, 1.2) * k
                cy = y - rng.uniform(0.5, 1.8) * k
                ctx.move_to(sx, cy)
                ctx.line_to(sx + math.cos(ang) * ln, cy + math.sin(ang) * ln)
                ctx.set_source_rgba(1, 0.85, 0.3, 0.9)
                ctx.set_line_width(3)
                ctx.stroke()
    elif ty == "lava" and a is not None and -0.15 < a < 1.3:
        hgt = 7.0 * math.sin(math.pi * min(1.0, (a + 0.15) / 1.45))
        for j in range(24):
            f = j / 24
            wob = 0.25 * math.sin(t * 20 + j)
            ctx.arc(sx + wob * k, y - f * hgt * k, (0.5 - 0.25 * f) * k, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.35 + 0.5 * f, 0.05)
            ctx.fill()
    elif ty == "meteor" and tr is not None:
        if -0.9 < a < 0:                                         # falling fireball with a trail
            p = (a + 0.9) / 0.9
            mx = sx + (1 - p) * 9 * k
            my = y - (1 - p) * 16 * k
            for j in range(10):
                tq = j / 10
                ctx.arc(mx + tq * 1.6 * k, my - tq * 2.8 * k, (0.9 - 0.07 * j) * k, 0, 2 * math.pi)
                ctx.set_source_rgba(1, 0.4 + 0.05 * j, 0.1, 0.8 - 0.07 * j)
                ctx.fill()
            ctx.arc(mx, my, 0.8 * k, 0, 2 * math.pi)
            ctx.set_source_rgb(0.35, 0.22, 0.15)
            ctx.fill()
        elif 0 <= a < 0.7:                                       # explosion flash + shockwave
            rg = cairo.RadialGradient(sx, y - 1.0 * k, 0.2 * k, sx, y - 1.0 * k, (2 + 8 * a) * k)
            rg.add_color_stop_rgba(0, 1, 0.95, 0.6, 0.95 * (1 - a / 0.7))
            rg.add_color_stop_rgba(0.5, 1, 0.5, 0.1, 0.7 * (1 - a / 0.7))
            rg.add_color_stop_rgba(1, 1, 0.3, 0.0, 0.0)
            ctx.arc(sx, y - 1.0 * k, (2 + 8 * a) * k, 0, 2 * math.pi)
            ctx.set_source(rg)
            ctx.fill()
            ctx.save()
            ctx.translate(sx, y)
            ctx.scale((1 + 7 * a) * k, (0.3 + 1.6 * a) * k)
            ctx.arc(0, 0, 1, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgba(1, 1, 1, 0.8 * (1 - a / 0.7))
            ctx.set_line_width(4)
            ctx.stroke()
    elif ty in ("dragon_fire", "dragon_ice") and tr is not None and -1.6 < a < 3.2:
        draw_dragon(ctx, hz, a, t, camx, cars)
    elif ty == "ufo" and tr is not None and -1.2 < a < 3.4:
        car = next(c for c in cars if c["hz"] is hz)
        cx = state(car, t)[0] if a > 0 else hz["x"]
        ux, _ = lane_xy(cx, hz["lane"], camx)
        if a < 0:
            ux += (-a) * 6 * k                                   # flies in from the right
        elif a > 2.3:
            ux -= (a - 2.3) * 10 * k                             # leaves to the left
        uy = y - 8.5 * k - 0.3 * k * math.sin(t * 4)
        if 0 <= a < 2.2:                                         # tractor beam
            se.poly(ctx, [(ux - 0.8 * k, uy + 0.4 * k), (ux + 0.8 * k, uy + 0.4 * k), (ux + 2.6 * k, y), (ux - 2.6 * k, y)])
            ctx.set_source_rgba(0.5, 1, 0.5, 0.28 + 0.08 * math.sin(t * 20))
            ctx.fill()
        ctx.save()
        ctx.translate(ux, uy)
        ctx.scale(3.0 * k, 0.8 * k)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(*se.lit((0.6, 0.64, 0.72)))
        ctx.fill()
        ctx.save()
        ctx.translate(ux, uy - 0.45 * k)
        ctx.scale(1.4 * k, 0.9 * k)
        ctx.arc(0, 0, 1, math.pi, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(0.55, 0.9, 1.0, 0.85)
        ctx.fill()
        for j in range(6):
            lx = ux + (j - 2.5) * 0.9 * k
            ctx.arc(lx, uy + 0.25 * k, 0.16 * k, 0, 2 * math.pi)
            ctx.set_source_rgb(*((1, 0.9, 0.2) if (j + int(t * 8)) % 2 else (1, 0.3, 0.3)))
            ctx.fill()


def draw_dragon(ctx, hz, a, t, camx, cars):
    """Our own cartoon dragon: flies in, hovers ahead of the car, breathes fire or ice, flies off."""
    fire = hz["type"] == "dragon_fire"
    car = next(c for c in cars if c["hz"] is hz)
    cx = state(car, t)[0]
    k = k_of(hz["lane"])
    gx, gy = lane_xy(cx, hz["lane"], camx)
    hx, hy = gx + 3.2 * k, gy - 5.2 * k                          # close to its target: always in frame with it
    if a < -0.5:
        hx += (-0.5 - a) * 14 * k
        hy -= (-0.5 - a) * 3 * k
    elif a > 1.7:
        hx += (a - 1.7) * 12 * k
        hy -= (a - 1.7) * 9 * k
    hy += 0.4 * k * math.sin(t * 5)
    body, belly = ((0.85, 0.15, 0.1), (1.0, 0.75, 0.25)) if fire else ((0.35, 0.6, 0.95), (0.85, 0.95, 1.0))
    flap = math.sin(t * 12)
    for side in (1, -1):
        se.poly(ctx, [(hx + 0.2 * k, hy - 0.4 * k), (hx + (1.8 + side * 0.4) * k, hy - (2.6 + 1.2 * flap) * k),
                      (hx + (3.2 + side * 0.3) * k, hy - (1.4 + 0.8 * flap) * k), (hx + 2.2 * k, hy - 0.2 * k)])
        ctx.set_source_rgb(*se.shade(body, 0.75 if side > 0 else 0.6))
        ctx.fill()
    ctx.move_to(hx + 1.8 * k, hy)
    ctx.curve_to(hx + 3.5 * k, hy + 0.4 * k, hx + 4.2 * k, hy - 0.8 * k, hx + 5.0 * k, hy - 0.4 * k)
    ctx.set_source_rgb(*body)
    ctx.set_line_width(0.45 * k)
    ctx.stroke()
    se.poly(ctx, [(hx + 5.0 * k, hy - 0.8 * k), (hx + 5.6 * k, hy - 0.3 * k), (hx + 5.0 * k, hy)])
    ctx.fill()
    ctx.save()
    ctx.translate(hx + 1.0 * k, hy)
    ctx.scale(1.6 * k, 0.8 * k)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgb(*body)
    ctx.fill()
    ctx.save()
    ctx.translate(hx + 0.9 * k, hy + 0.35 * k)
    ctx.scale(1.1 * k, 0.4 * k)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgb(*belly)
    ctx.fill()
    ctx.move_to(hx + 0.2 * k, hy - 0.2 * k)
    ctx.line_to(hx - 0.8 * k, hy - 0.9 * k)
    ctx.set_source_rgb(*body)
    ctx.set_line_width(0.6 * k)
    ctx.stroke()
    ctx.arc(hx - 1.0 * k, hy - 1.0 * k, 0.55 * k, 0, 2 * math.pi)
    ctx.fill()
    se.rrect(ctx, hx - 1.9 * k, hy - 1.2 * k, 1.0 * k, 0.5 * k, 0.2 * k)
    ctx.fill()
    for dx in (-0.7, -1.2):
        se.poly(ctx, [(hx + dx * k, hy - 1.45 * k), (hx + (dx + 0.25) * k, hy - 1.45 * k),
                      (hx + (dx + 0.35) * k, hy - 2.0 * k)])
        ctx.set_source_rgb(*belly)
        ctx.fill()
    ctx.arc(hx - 1.15 * k, hy - 1.15 * k, 0.16 * k, 0, 2 * math.pi)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    ctx.arc(hx - 1.2 * k, hy - 1.13 * k, 0.08 * k, 0, 2 * math.pi)
    ctx.set_source_rgb(0.05, 0.05, 0.1)
    ctx.fill()
    if 0 <= a < 1.3:
        mx, my = hx - 1.9 * k, hy - 0.95 * k
        tx, ty_ = gx, gy - 1.0 * k
        rng = np.random.default_rng(int(t * 90))
        for _ in range(60):
            f = rng.uniform(0, 1)
            spread = f * 1.4 * k
            px = mx + (tx - mx) * f + rng.uniform(-1, 1) * spread
            py = my + (ty_ - my) * f + rng.uniform(-1, 1) * spread * 0.6
            rr = (0.25 + 0.6 * f) * k * rng.uniform(0.6, 1.0)
            col = (1, 0.9 - 0.6 * f, 0.2 - 0.15 * f) if fire else (0.75 + 0.25 * (1 - f), 0.92, 1.0)
            ctx.arc(px, py, rr, 0, 2 * math.pi)
            ctx.set_source_rgba(*col, 0.85 - 0.4 * f)
            ctx.fill()
        if not fire:
            for _ in range(10):
                px = tx + rng.uniform(-2, 2) * k
                py = ty_ + rng.uniform(-1.5, 1) * k
                for q in range(3):
                    ang = q * math.pi / 3
                    ctx.move_to(px - math.cos(ang) * 0.2 * k, py - math.sin(ang) * 0.2 * k)
                    ctx.line_to(px + math.cos(ang) * 0.2 * k, py + math.sin(ang) * 0.2 * k)
                ctx.set_source_rgba(1, 1, 1, 0.9)
                ctx.set_line_width(2)
                ctx.stroke()
    if not fire and 1.95 <= a < 2.6:
        for j in range(14):
            ang = j * 2 * math.pi / 14
            d = (a - 1.95) * 7 * k
            bx, by = gx + math.cos(ang) * d, gy - 1.0 * k + math.sin(ang) * d * 0.6
            se.poly(ctx, [(bx, by), (bx + 0.3 * k, by + 0.1 * k), (bx + 0.1 * k, by + 0.35 * k)])
            ctx.set_source_rgba(0.8, 0.95, 1.0, 0.9)
            ctx.fill()


# ------------------------------------------------------------------ drawing: cars
def draw_car(ctx, c, t, camx):
    x, z, h, yaw, pitch, v, sq, split, burn, patched, ice, tires = state(c, t)
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
    ctx.scale(bw * 0.58 * k * (1 + max(0.0, h) * 0.06), 0.16 * k)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(0, 0, 0, 0.3 * max(0.0, 1 - max(0.0, h) / 5))
    ctx.fill()
    ys = se.yaw_scale(yaw)
    land = c["land"] is not None and 0 <= t - c["land"] < 0.3
    squash = (1 - 0.12 * math.sin(math.pi * (t - c["land"]) / 0.3)) if land else 1.0
    squash *= sq
    widen = 1 + 0.35 * max(0.0, 1 - sq)                          # flattened cars spread out

    def paint():
        ctx.set_source_rgb(0.3, 0.3, 0.34)
        ctx.set_line_width(0.14)
        for lx in veh["wheel_x"]:
            ctx.move_to(lx, ride - bh / 2)
            ctx.line_to(lx, r)
            ctx.stroke()
        for lx in veh["wheel_x"]:
            se.draw_wheel(ctx, lx, r, -x / r, r, vk.startswith("monster"), sx=max(0.3, abs(ys)))
        ctx.save()
        ctx.translate(0, ride + 0.03 * math.sin(t * 18 + c["lane"]) * min(1.0, v / 20))
        se.draw_body(ctx, vk, veh, False, t)
        if burn > 0.5:                                           # cartoon soot
            rng = np.random.default_rng(17)
            for _ in range(10):
                ctx.arc(rng.uniform(-bw / 2, bw / 2), rng.uniform(-bh / 2, bh / 2 + 0.4), rng.uniform(0.15, 0.4),
                        0, 2 * math.pi)
                ctx.set_source_rgba(0.08, 0.06, 0.06, 0.55)
                ctx.fill()
        if patched > 0.5:                                        # plaster across the seam
            ctx.save()
            ctx.rotate(0.5)
            se.rrect(ctx, -0.18, -0.35, 0.36, 0.9, 0.08)
            ctx.set_source_rgb(0.98, 0.85, 0.65)
            ctx.fill()
            ctx.restore()
        se.draw_face(ctx, vk, mood_of(c, t, x), t)
        ctx.restore()

    ctx.save()
    ctx.translate(sx, gy - h * k)
    ctx.scale(k, -k)
    ctx.rotate(pitch)
    ctx.scale(ys * widen, squash)
    if split > 0.01:                                             # laser cut: two halves drift apart
        for side in (-1, 1):
            ctx.save()
            ctx.rectangle(0 if side > 0 else -40, -20, 40, 60)
            ctx.clip()
            ctx.translate(side * split / 2, side * split * 0.15)
            paint()
            ctx.restore()
    else:
        paint()
    ctx.restore()
    top_y = gy - (h + ride + bh * sq) * k
    if ice > 0.5:                                                # translucent ice block around the car
        se.rrect(ctx, sx - (bw / 2 + 0.35) * k, top_y - 0.5 * k, (bw + 0.7) * k, gy - top_y + 0.55 * k, 0.25 * k)
        ctx.set_source_rgba(0.7, 0.92, 1.0, 0.55)
        ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, 0.9)
        ctx.set_line_width(max(3, 0.08 * k))
        ctx.stroke()
        for j in range(3):
            ctx.move_to(sx - (bw / 2 - 0.2 - j * 0.5) * k, top_y - 0.3 * k)
            ctx.line_to(sx - (bw / 2 - 0.9 - j * 0.5) * k, top_y + 0.6 * k)
            ctx.set_source_rgba(1, 1, 1, 0.8)
            ctx.set_line_width(max(2, 0.06 * k))
            ctx.stroke()
    if tires > 0.5:                                              # pit-stop tire change: tires + wrench spin
        for j, lx in enumerate(veh["wheel_x"]):
            wx = sx + lx * k * ys
            ctx.save()
            ctx.translate(wx, gy - (r * 2.6 + 0.4 * abs(math.sin(t * 6 + j))) * k)
            ctx.rotate(t * 14 + j)
            ctx.arc(0, 0, r * 0.8 * k, 0, 2 * math.pi)
            ctx.set_source_rgb(0.1, 0.1, 0.12)
            ctx.fill()
            ctx.arc(0, 0, r * 0.4 * k, 0, 2 * math.pi)
            ctx.set_source_rgb(0.8, 0.8, 0.85)
            ctx.fill()
            ctx.restore()
        ctx.save()
        ctx.translate(sx, top_y - 1.2 * k)
        ctx.rotate(math.sin(t * 10) * 0.6)
        se.rrect(ctx, -0.12 * k, -0.9 * k, 0.24 * k, 1.8 * k, 0.1 * k)
        ctx.set_source_rgb(0.7, 0.72, 0.78)
        ctx.fill()
        ctx.restore()
    if burn > 0.5 and c["trig"] is not None and t - c["trig"] < 4.0:   # smoke puffs
        for j in range(5):
            age = ((t - c["trig"]) * 1.2 + j * 0.2) % 1.0
            ctx.arc(sx - age * 0.8 * k, gy - (h + ride + bh + age * 2.2) * k, (0.3 + age * 0.6) * k, 0, 2 * math.pi)
            ctx.set_source_rgba(0.25, 0.25, 0.27, 0.5 * (1 - age))
            ctx.fill()
    return sx, gy - (h + ride + bh * sq) * k, k


def bubble(ctx, text, sx, sy, age, k):
    if not 0 <= age < 1.1:
        return
    sc = se.ease_out_back(min(1.0, age / 0.25)) * min(1.0, (1.1 - age) / 0.2)
    ctx.save()
    ctx.translate(sx, sy - 110 * k / 70)
    ctx.scale(sc * k / 70, sc * k / 70)
    se.rrect(ctx, -160, -60, 320, 110, 40)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill_preserve()
    ctx.set_source_rgb(0.07, 0.07, 0.2)
    ctx.set_line_width(8)
    ctx.stroke()
    se.poly(ctx, [(-30, 48), (10, 48), (-40, 100)])
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    se.draw_text(ctx, text, 0, -5, 62, fill=(0.9, 0.12, 0.12), stroke=(1, 1, 1), sw=4, max_w=290)
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


def _thumb(ctx, x, y, sz, filled):
    """Thumbs-up icon (outline or filled blue)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sz / 100, sz / 100)
    se.rrect(ctx, -46, -8, 22, 52, 5)                            # cuff
    se.rrect(ctx, -20, -10, 62, 54, 14)                          # fist
    ctx.move_to(-16, -8)
    ctx.curve_to(-8, -30, 0, -48, 6, -52)
    ctx.curve_to(18, -56, 22, -40, 14, -10)
    ctx.close_path()
    col = (0.1, 0.45, 1.0) if filled else (1, 1, 1)
    ctx.set_source_rgb(*col)
    ctx.fill_preserve()
    ctx.set_source_rgb(0.1, 0.1, 0.12)
    ctx.set_line_width(7)
    ctx.stroke()
    ctx.restore()


def _bell(ctx, x, y, sz, swing):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(swing)
    ctx.scale(sz / 100, sz / 100)
    ctx.move_to(-36, 26)
    ctx.curve_to(-30, 18, -32, -30, 0, -36)
    ctx.curve_to(32, -30, 30, 18, 36, 26)
    ctx.close_path()
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill_preserve()
    ctx.set_source_rgb(0.1, 0.1, 0.12)
    ctx.set_line_width(7)
    ctx.stroke()
    ctx.arc(0, 34, 9, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def _hand(ctx, x, y, press):
    """Cartoon pointer hand (fingertip at x, y)."""
    ctx.save()
    ctx.translate(x, y)
    s = 1.0 - 0.15 * press
    ctx.scale(s, s)
    se.rrect(ctx, -14, 0, 28, 70, 14)                            # index finger
    se.rrect(ctx, -34, 44, 78, 70, 22)                           # palm
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill_preserve()
    ctx.set_source_rgb(0.1, 0.1, 0.12)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.restore()


def _ring(ctx, x, y, w, h, age):
    """Pulsing highlight ring around a button (the 'look here' cue of the early episodes)."""
    for q in range(2):
        f = ((age * 1.6) + q * 0.5) % 1.0
        se.rrect(ctx, x - w / 2 - 14 - 40 * f, y - h / 2 - 14 - 40 * f, w + 28 + 80 * f, h + 28 + 80 * f, h / 2 + 30)
        ctx.set_source_rgba(1, 0.86, 0.12, 0.9 * (1 - f))
        ctx.set_line_width(10)
        ctx.stroke()


CTA_LIKE_T, CTA_SUB_T = 1.3, 2.4                  # tap times inside the end card (audio uses them too)


def draw_cta(ctx, age):
    """YouTube-style end card: channel row, LIKE + SUBSCRIBE buttons, a hand taps LIKE (turns blue, +1) then
    SUBSCRIBE (turns grey 'SUBSCRIBED', bell rings); pulsing highlight ring on the next button."""
    ctx.set_source_rgba(0.03, 0.03, 0.1, 0.6 * min(1.0, age / 0.3))
    ctx.paint()
    s = se.ease_out_back(min(1.0, age / 0.45))
    ctx.save()
    ctx.translate(540, 1030 + (1 - min(1.0, age / 0.45)) * 200)
    ctx.scale(s, s)
    se.rrect(ctx, -460, -300, 920, 600, 48)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    ctx.arc(-330, -160, 72, 0, 2 * math.pi)                      # channel avatar
    g = cairo.LinearGradient(-400, -230, -260, -90)
    g.add_color_stop_rgb(0, 1, 0.3, 0.2)
    g.add_color_stop_rgb(1, 0.95, 0.75, 0.1)
    ctx.set_source(g)
    ctx.fill()
    se.draw_text(ctx, "MW", -330, -160, 62, fill=(1, 1, 1), stroke=(0.2, 0.05, 0.05), sw=6)
    se.draw_text(ctx, "MegaWheel Arena", 70, -185, 64, fill=(0.1, 0.1, 0.14), stroke=(1, 1, 1), sw=2, max_w=560)
    se.draw_text(ctx, "New races every day!", 70, -115, 40, fill=(0.4, 0.4, 0.45), stroke=(1, 1, 1), sw=2, max_w=560)
    liked, subbed = age >= CTA_LIKE_T, age >= CTA_SUB_T
    bx_like, bx_sub, by = -235, 175, 90
    if not liked:
        _ring(ctx, bx_like, by, 330, 120, age)
    elif not subbed:
        _ring(ctx, bx_sub, by, 440, 120, age)
    pop = 1 + 0.18 * math.sin(math.pi * min(1.0, max(0.0, (age - CTA_LIKE_T) / 0.3))) if liked else 1.0
    ctx.save()
    ctx.translate(bx_like, by)
    ctx.scale(pop, pop)
    se.rrect(ctx, -165, -60, 330, 120, 60)
    ctx.set_source_rgb(0.93, 0.93, 0.95)
    ctx.fill()
    _thumb(ctx, -85, 4, 72, liked)
    se.draw_text(ctx, "LIKE", 45, 2, 54, fill=(0.1, 0.45, 1.0) if liked else (0.12, 0.12, 0.15),
                 stroke=(0.93, 0.93, 0.95), sw=2)
    ctx.restore()
    if liked and age - CTA_LIKE_T < 1.0:                         # +1 floats up
        f = (age - CTA_LIKE_T) / 1.0
        se.draw_text(ctx, "+1", bx_like + 90, by - 90 - 80 * f, 56, fill=(0.1, 0.45, 1.0), alpha=1 - f)
    pop = 1 + 0.18 * math.sin(math.pi * min(1.0, max(0.0, (age - CTA_SUB_T) / 0.3))) if subbed else 1.0
    ctx.save()
    ctx.translate(bx_sub, by)
    ctx.scale(pop, pop)
    se.rrect(ctx, -220, -60, 440, 120, 60)
    ctx.set_source_rgb(*((0.9, 0.9, 0.92) if subbed else (0.9, 0.0, 0.0)))
    ctx.fill()
    if subbed:
        swing = 0.5 * math.sin((age - CTA_SUB_T) * 22) * math.exp(-(age - CTA_SUB_T) * 2.5)
        _bell(ctx, -150, 0, 64, swing)
        se.draw_text(ctx, "SUBSCRIBED", 40, 2, 50, fill=(0.3, 0.3, 0.33), stroke=(0.9, 0.9, 0.92), sw=2, max_w=300)
    else:
        se.draw_text(ctx, "SUBSCRIBE", 0, 2, 58, fill=(1, 1, 1), stroke=(0.6, 0, 0), sw=4, max_w=380)
    ctx.restore()
    if subbed and age - CTA_SUB_T < 0.9:                         # sparkles
        f = (age - CTA_SUB_T) / 0.9
        for j in range(10):
            ang = j * 2 * math.pi / 10
            se.star(ctx, bx_sub + math.cos(ang) * (150 + 140 * f), by + math.sin(ang) * (70 + 90 * f), 16, ang)
            ctx.set_source_rgba(1, 0.86, 0.12, 1 - f)
            ctx.fill()
    se.draw_text(ctx, "for more crazy races!", 0, 240, 46, fill=(0.95, 0.35, 0.1), stroke=(1, 1, 1), sw=3)
    if age > 0.5:                                                # the hand: to LIKE, tap, to SUBSCRIBE, tap
        path = [(0.5, (380, 420)), (CTA_LIKE_T - 0.05, (bx_like + 30, by + 40)), (CTA_LIKE_T + 0.35, (bx_like + 30, by + 40)),
                (CTA_SUB_T - 0.05, (bx_sub + 60, by + 40)), (99.0, (bx_sub + 60, by + 40))]
        for (t0, p0), (t1, p1) in zip(path, path[1:]):
            if t0 <= age < t1:
                f = se.ease_out_back(min(1.0, (age - t0) / max(0.01, min(0.6, t1 - t0)))) if t1 < 99 else 1.0
                hx, hy = p0[0] + (p1[0] - p0[0]) * min(1.0, f), p0[1] + (p1[1] - p0[1]) * min(1.0, f)
                press = max(0.0, 1 - abs(age - CTA_LIKE_T) / 0.12) + max(0.0, 1 - abs(age - CTA_SUB_T) / 0.12)
                _hand(ctx, hx, hy, press)
                break
    ctx.restore()


# ------------------------------------------------------------------ audio
def boing():
    n = int(0.45 * se.SR)
    t = np.arange(n) / se.SR
    f = 180 + 700 * (1 - np.exp(-t * 9)) + 60 * np.sin(t * 60)
    return np.sin(2 * np.pi * np.cumsum(f) / se.SR) * np.exp(-t / 0.25)


def zap():
    a, b = se.sweep(2400, 300, 0.35, 0.9), se.sweep(1800, 200, 0.3, 0.5)
    a[:len(b)] += b                                              # different lengths: overlay, not add
    return a


def ufo_hum(dur):
    n = int(dur * se.SR)
    t = np.arange(n) / se.SR
    f = 420 + 120 * np.sin(2 * np.pi * 6 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / se.SR) * np.minimum(1, t / 0.2) * np.clip((dur - t) / 0.3, 0, 1) * 0.7


def dragon_roar():
    n = int(1.0 * se.SR)
    t = np.arange(n) / se.SR
    f = 150 - 70 * t + 25 * np.sin(2 * np.pi * 9 * t)
    ph = 2 * np.pi * np.cumsum(f) / se.SR
    rough = np.random.default_rng(5).standard_normal(n) * 0.35
    return (np.sin(ph) + 0.5 * np.sin(2 * ph) + rough) * np.minimum(1, t / 0.08) * np.exp(-t / 0.55)


def ice_blast():
    n = int(1.3 * se.SR)
    t = np.arange(n) / se.SR
    x = np.random.default_rng(8).standard_normal(n)
    hiss = (x - se.smooth(x, 3)) * np.minimum(1, t / 0.05) * np.exp(-t / 0.7)
    return hiss + se.sweep(2600, 900, 1.3, 0.25)


HAZ_SFX = {
    "puddle": lambda: [(0.0, se.synth_splash(1.0, seed=41), 1.0), (0.05, se.synth_spin(1.4, 2), 0.8)],
    "ramp": lambda: [(0.0, se.synth_whoosh(), 0.6)],
    "pothole": lambda: [(0.05, se.synth_impact(0.7, seed=5), 0.9)],
    "lava": lambda: [(-0.2, se.synth_eruption(seed=43), 0.9), (0.05, se.synth_ignite(), 0.8)],
    "wall": lambda: [(0.0, se.synth_wall_crash(1.0), 1.0), (0.05, se.synth_shatter(), 0.5)],
    "crusher": lambda: [(-0.05, se.synth_impact(1.0, seed=9), 1.0), (1.3, boing(), 0.8)],
    "laser": lambda: [(0.0, zap(), 0.8), (0.1, se.synth_shatter(), 0.35)],
    "meteor": lambda: [(-0.9, se.sweep(1400, 250, 0.9, 0.5), 0.6), (0.0, se.synth_eruption(seed=47), 1.0)],
    "ufo": lambda: [(-1.0, ufo_hum(3.6), 0.6)],
    "dragon_fire": lambda: [(-0.6, dragon_roar(), 0.8), (0.0, se.synth_fire(1.4, seed=21), 0.9),
                            (0.7, se.synth_impact(0.4, seed=13), 0.5)],
    "dragon_ice": lambda: [(-0.6, dragon_roar(), 0.8), (0.0, ice_blast(), 0.9)],
    "thaw": lambda: [(0.0, se.synth_shatter(seed=3), 0.9)],
}


def box_avg(x, k):
    """Centred moving average (same result as np.convolve(x, ones(k)/k, "same"), but O(N))."""
    c = np.concatenate([[0.0], np.cumsum(x)])
    y = (c[k:] - c[:-k]) / k
    pad = len(x) - len(y)
    return np.pad(y, (pad // 2, pad - pad // 2), mode="edge")


def build_audio(frames, events, winner, star, replay, lines, voice, out_of, cta_start):
    se.VOICE = voice
    total = len(frames) / FPS
    sched = []
    n = int(total * se.SR) + se.SR
    narr, eng, sfx = np.zeros(n), np.zeros(n), np.zeros(n)

    def place(buf, sig, t, gain=1.0):
        i0 = int(t * se.SR)
        if 0 <= i0 < n:
            m = min(len(sig), n - i0)
            buf[i0:i0 + m] += sig[:m] * gain

    busy = 0.0
    for t_want, text in lines:                                   # narration: never overlapping
        a = se.ready_go_audio() if text == se.READY_SENTINEL else se.tts(text)
        t0 = max(t_want, busy + 0.15)
        place(narr, a, t0)
        busy = t0 + len(a) / se.SR
        sched.append(f"{t_want:.1f}>{t0:.1f}-{busy:.1f} {text[:28]}")
    print(f"[25d] narration (video {total:.1f}s): " + " | ".join(sched), flush=True)
    lead = winner
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
        if kind in HAZ_SFX:
            for dt_, sig, g in HAZ_SFX[kind]():
                place(sfx, sig, max(0.0, o + dt_), g)
        elif kind == "bump":
            place(sfx, se.synth_impact(0.6, seed=7), o, 0.8)
        elif kind == "dodge":
            place(sfx, se.synth_whoosh(), o, 0.7)
        elif kind == "land":
            place(sfx, se.synth_impact(1.0, seed=11), o, 1.0)
    if winner["finish"] is not None:
        place(sfx, se.synth_win(), out_of(winner["finish"]), 0.9)
    if replay:
        r0, a, b = replay
        o = r0 + (star["trig"] - a) / 0.4
        place(sfx, se.synth_rewind(), r0, 0.6)
        for dt_, sig, g in HAZ_SFX[star["hz"]["type"]]():
            place(sfx, se.stretch(sig, 0.5), max(r0, o + dt_ / 0.4), g)
    for tap in (CTA_LIKE_T, CTA_SUB_T):                         # end card: click pops + subscribe bell
        place(sfx, se.tone(1300, 0.06, "sine", decay=0.02), cta_start + tap, 0.8)
    place(sfx, se.tone(1760, 0.8, "sine", decay=0.35) + se.tone(2637, 0.8, "sine", decay=0.25) * 0.5,
          cta_start + CTA_SUB_T + 0.05, 0.6)
    bgm = se.synth_bgm(total + 1, style=se.th_time()["music"])
    bgm = bgm[:n] if len(bgm) >= n else np.pad(bgm, (0, n - len(bgm)))
    talk = box_avg((np.abs(narr) > 0.01).astype(float), int(0.25 * se.SR))   # O(N), was a 40 s np.convolve
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
    ap.add_argument("--hazards", default="", help="force 3 hazard types, comma separated (tests)")
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
    forced = [h for h in opt.hazards.split(",") if h] or None
    params = setup(opt.seed, appearances, forced)
    se.make_theme(opt.seed, used=[e.get("theme", "") for e in active if e.get("theme")])
    uses = {v: 0 for v in se.VOICES}
    for e in active:
        if e.get("voice") in uses:
            uses[e["voice"]] += 1
    vr = np.random.default_rng(5000 + opt.seed)
    tie = {v: float(vr.random()) for v in se.VOICES}
    voice = min(se.VOICES, key=lambda v: (uses[v], tie[v]))
    voice = se.cb_pick(active, opt.seed) or voice                # narrator "C" (m1/f1 alternating) when available
    cars, events = simulate(opt.seed)
    frames, winner, star, replay, cta_start = build_timeline(cars)
    order = sorted(cars, key=lambda c: c["place"])
    hits = hit_cars(cars)
    print(f"[25d] {name} theme={se.THEME_ID} voice={voice} cast={[nick(c['key']) for c in cars]} "
          f"hazards={[(h['type'], h['lane']) for h in HZ]} hit={[(nick(c['key']), c['hz']['type']) for c in hits]} "
          f"dodge={[(nick(c['key']), c['dodged']) for c in cars if c.get('dodge_t') is not None]} "
          f"finish={[nick(c['key']) for c in order]} frames={len(frames)} ({len(frames) / FPS:.1f}s)", flush=True)
    race_idx = [(j, ft) for j, (mode, ft) in enumerate(frames) if mode == "race"]

    def out_of(t):
        for j, ft in race_idx:
            if ft >= t:
                return j / FPS
        return len(frames) / FPS

    names = [nick(c["key"]) for c in cars]
    lines = [(0.0, se.READY_SENTINEL), (1.2, f"Four racers, one finish line! {names[0]}, {names[1]}, {names[2]} and {names[3]}. Who will win?")]
    story = [(c["trig"], HAZARDS[c["hz"]["type"]]["line"].format(n=nick(c["key"]))) for c in hits]
    story += [(c["dodge_t"], f"Nice move! {nick(c['key'])} dodges the {DODGEABLE[c['dodged']]}!")
              for c in cars if c.get("dodge_t") is not None]
    for tt, txt in sorted(story):
        lines.append((out_of(tt) + 0.15, txt))
    lines.append((out_of(winner["finish"]) + 0.2, f"{nick(winner['key'])} wins the race!"))
    if replay:
        lines.append((replay[0] + 0.1, se.REPLAY_LINE))
    lines.append((cta_start + 0.2, se.CTA))

    date = time.strftime("%Y-%m-%d")
    out_dir = (f"{se.BASE}/work/lanes25d/previews/{name}" if opt.preview_only
               else f"{se.CHANNEL_DIR}/pending/{date}_{SERIES}_{ENGINE_VERSION}_s{opt.seed:03d}")   # version: never mixed
    prev = os.path.join(out_dir, "preview")
    os.makedirs(prev, exist_ok=True)
    os.makedirs(se.WORK, exist_ok=True)
    wav = f"{se.WORK}/mix_{name}.wav"
    se.ready_go_audio()                                          # sets se.READY_GO_T (GO pop on the spoken "Go!")
    busy = 0.0                                                   # end card lasts until the CTA has been said
    for t_want, text in lines:
        d = len(se.ready_go_audio() if text == se.READY_SENTINEL else se.tts(text)) / se.SR
        busy = max(t_want, busy + 0.15) + d
    while len(frames) / FPS < busy + 0.7:
        frames.append(("cta", frames[-1][1]))
    audio = build_audio(frames, events, winner, star, replay, lines, voice, out_of, cta_start)
    se.cb_finish(f"narrator {name}")                             # missing voice-C lines -> Modal -> restart
    se.write_wav(wav, audio)
    silent = f"{se.WORK}/v_{name}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", silent],
                          stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    marks = {}
    for c in hits:
        marks[int(out_of(c["trig"] + 0.3) * FPS)] = f"hz_{c['hz']['type']}"
    for c in cars:
        if c.get("dodge_t") is not None:
            marks[int(out_of(c["dodge_t"] + 0.5) * FPS)] = "dodge"
    marks[int(out_of(winner["finish"] + 0.5) * FPS)] = "winner"
    marks[int((cta_start + 1.5) * FPS)] = "outro"
    camx, zoom, prev_mode, empty_frames = None, 1.0, None, 0
    for fi, (mode, t) in enumerate(frames):
        st = {id(c): state(c, t) for c in cars}
        focus = None
        for c in cars:                                           # a dodge is a highlight too
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
        if focus is not None and focus["hz"] is not None and focus["hz"]["type"].startswith("dragon")                 and focus is not winner:
            target = st[id(focus)][0] + 2.2                     # frame the car AND the dragon hovering ahead of it
        spread = max(xs) - min(xs) + 9.0
        fit = float(np.clip(W * 0.92 / (spread * k_of(0.0)), 0.82, 1.12))
        cut = camx is None or mode != prev_mode
        camx = target if cut else camx + (target - camx) * (0.3 if mode == "replay" else 0.12)
        punch = 1.0
        for kind, et, ex, ez in events:
            if kind in ("land", "bump", "puddle", "crusher", "meteor", "wall") and 0 <= t - et < 0.35:
                punch = max(punch, 1 + 0.09 * math.sin(math.pi * (t - et) / 0.35))
        want = 1.15 if mode == "replay" else min(fit, 1.05 if focus else 1.0)
        zoom = want * punch if cut else zoom + (want * punch - zoom) * 0.12
        key = focus if focus is not None else max(cars, key=lambda c: st[id(c)][0])
        kx, kz = st[id(key)][0], st[id(key)][1]
        reach = 380.0 / (k_of(kz) * zoom)
        camx = float(np.clip(camx, kx - reach, kx + reach))
        prev_mode = mode
        if not any(0 < 540 + (st[id(c)][0] - camx) * k_of(st[id(c)][1]) * zoom < W for c in cars):
            empty_frames += 1
        shx = shy = 0.0
        for kind, et, ex, ez in events:
            if kind in ("land", "bump", "wall", "crusher", "meteor") and 0 <= t - et < 0.45:
                amp = (24 if kind == "meteor" else 16) * (1 - (t - et) / 0.45)
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
        for hz in sorted(HZ, key=lambda h: -h["lane"]):
            draw_hazard_ground(ctx, hz, camx, t, cars)
        heads = {}
        for c in sorted(cars, key=lambda c: -st[id(c)][1]):
            for hz in HZ:                                        # towering hazards of farther lanes go behind nearer cars
                if hz["lane"] > st[id(c)][1] + 0.5 and not hz.get("_drawn"):
                    draw_hazard_front(ctx, hz, camx, t, cars)
                    hz["_drawn"] = True
            hd = draw_car(ctx, c, t, camx)
            heads[id(c)] = None if hd is None else (540 + (hd[0] - 540) * zoom + shx,
                                                   1520 + (hd[1] - 1520) * zoom + shy + WORLD_DY, hd[2])
        for hz in HZ:
            if not hz.pop("_drawn", False):
                draw_hazard_front(ctx, hz, camx, t, cars)
        for kind, et, ex, ez in events:
            age = t - et
            if kind == "puddle" and 0 <= age < 1.6:
                k, y = k_of(ez), ground_y(ez)
                ctx.save()
                ctx.translate((ex - camx) * k + 540, y)
                ctx.scale(k, -k)
                se.draw_water_splash(ctx, dict(x=0.0, y=0.0, speed=22.0, big=False), age)
                ctx.restore()
            if kind in ("land", "pothole") and 0 <= age < 0.8:
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
            if c["trig"] is not None:
                bubble(ctx, HAZARDS[c["hz"]["type"]]["bubble"], hd[0], hd[1], t - c["trig"] - 0.1, hd[2] * zoom)
            if c["bump_t"] is not None:
                bubble(ctx, "HEY!", hd[0], hd[1], t - c["bump_t"] - 0.1, hd[2] * zoom)
            if c.get("dodge_t") is not None:
                bubble(ctx, "NICE!", hd[0], hd[1], t - c["dodge_t"] - 0.1, hd[2] * zoom)
            if c is winner and c["finish"] is not None:
                bubble(ctx, "YEAH!", hd[0], hd[1], t - c["finish"] - 0.3, hd[2] * zoom)
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
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type:format=duration", "-of",
                            "json", out], capture_output=True, text=True)
    pj = json.loads(probe.stdout or "{}")
    dur = float(pj.get("format", {}).get("duration", 0))
    kinds = [s["codec_type"] for s in pj.get("streams", [])]
    checks = {"video+audio streams": "video" in kinds and "audio" in kinds,
              "duration 20-60 s": 20 <= dur <= 60,
              "has winner": winner["finish"] is not None,
              "at least 2 hazards hit": len(hits) >= 2,
              "has replay": replay is not None,
              "previews": all(os.path.exists(os.path.join(prev, f"{m}.png")) for m in ("winner", "outro")),
              "no frame without a car": empty_frames == 0}
    passed = all(checks.values())
    outcomes = [("win" if c is winner else f"p{c['place']}") + (f"+{c['hz']['type']}" if c["trig"] is not None else "")
                + ("+bump" if c["bump_t"] else "") + (f"+dodge_{c['dodged']}" if c.get("dodge_t") else "")
                for c in cars]
    track_id = "race25d_" + hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()[:8] + "@" + se.THEME_ID
    title = TITLES[opt.seed % len(TITLES)]
    folder_rel = os.path.relpath(out_dir, se.BASE)
    hz_words = ", ".join(sorted({h["type"] for h in HZ}))
    manifest = dict(
        video_id=name, status="RENDERED_PENDING_APPROVAL" if passed else "CHECKS_FAILED",
        engine=f"race25d {ENGINE_VERSION}", series=SERIES, seed=opt.seed, fps=FPS, duration=round(dur, 2),
        params=params, theme=se.THEME, theme_id=se.THEME_ID, voice=voice, outcomes=outcomes, checks=checks,
        cta=se.CTA, title_base=title, title=f"{title} #Shorts",
        description=(f"{', '.join(names[:3])} and {names[3]} race to the finish line! 🏁 "
                     f"Obstacles today: {hz_words}! 💥\n\n"
                     "Watch till the end for the slow-motion replay! 🎬\n\n🏆 Comment your champion below!\n"
                     f"🔔 Subscribe to {se.CHANNEL} for new car challenges every week.\n\n"
                     "#Shorts #CarRace #CartoonCars #Racing #MegaWheelArena"),
        tags=TAGS + [se.VEHICLES[c["key"]]["display"].split(" THE ")[1].lower() for c in cars] + sorted({h["type"] for h in HZ}),
        narration=["Ready... Go!" if txt == se.READY_SENTINEL else txt for _, txt in lines],
        assets="100% procedurally generated (cairo 2.5D render + synthesized audio), narration " + (f"Chatterbox TTS (open source, Modal GPU) synthetic voice {voice}" if voice.startswith("chatterbox") else f"Edge-TTS {voice}"),
        video_path=out, preview_dir=prev)
    with open(os.path.join(out_dir, f"{name}.json"), "w") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, f"{name}_audit.md"), "w") as fh:
        fh.write(f"# Checks {name}\n\n" + "\n".join(f"- {'✅' if ok else '❌'} {k}" for k, ok in checks.items())
                 + f"\n\nDuration {dur:.1f} s · theme {se.THEME_ID} · voice {voice} · hazards {hz_words}\n")
    print(f"[25d] checks {'PASS' if passed else 'FAIL'} {checks} empty_frames={empty_frames}", flush=True)
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
