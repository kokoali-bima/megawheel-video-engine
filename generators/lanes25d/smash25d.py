#!/usr/bin/env python3
"""MegaWheel Arena — series "smash25d": SMASH ARENA, the 19:00 ET daily slot (user 2026-10-01).

Four cars ram each other in a 2.5D arena until only one is left. Same "paper cutout" style as race25d: the
characters are drawn by the SAME functions as the 2D episodes (race25d.draw_car -> sim_engine draw_body /
draw_face / draw_wheel), so they look exactly like the 2D cast; a car turning around flips like a paper card.

Rules: every car has 100 HP. Rams do damage by closing speed and (effective) mass, side hits hurt more, the
attacker's front is reinforced. A car is OUT when its HP hits 0 (wrecked, smoking) or when it is pushed off
the floor (lava ring / mud pit / icy water). CHAOS (v2): missile strike, the kaiju KRAGGOR (own design) stomping,
UFO abduction, floor cracking with lava geysers, all with a warning so agile drivers can escape. Last car wins.
Arenas (rotation): lava ring (steel floor) · mud pit (dirt floor) · ice rink (slippery, low grip).
Cartoon slapstick only (BLUEPRINT rule 7): no fire deaths, no people; wrecks smoke and get dizzy.

Timeline: READY-GO -> smash -> winner + confetti -> INSTANT REPLAY of the biggest moment -> YouTube end card.
Hard rules: hard cuts between scenes, check "no frame without a car".

Usage (cd /root/video-engine):
  ./venv/bin/python generators/lanes25d/smash25d.py --seed 1                 # -> renders/megawheel_arena/pending/
  ./venv/bin/python generators/lanes25d/smash25d.py --seed 1 --preview-only  # -> work/lanes25d/previews/
  [--arena lava|mud|ice]   force the arena (tests)
  [--dry-run]              simulate + battle checks only (fast seed search, nothing written)
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
sys.path.insert(0, os.path.join(HERE, "..", "voice"))
import announcer  # noqa: E402  (Chatterbox announcer on Modal, cached; Edge TTS fallback)

USE_CB = False                                   # set per video: True = Chatterbox announcer lines from the cache
# two commentators (user 2026-10-01): m1 = ring announcer / play-by-play, f1 = colour commentator (reactions)
EDGE_VOICES = {"m1": "en-US-GuyNeural", "f1": "en-US-AriaNeural"}     # Edge fallback per speaker
HIT_CALLS_F = ["Oh my goodness! What a hit!", "Ouch! That's gotta hurt!", "Did you see that?"]
CHAOS_WHO = {"missile": "f1", "ufo": "f1", "kraggor": "m1", "crack": "m1"}

SERIES, ENGINE_VERSION = "smash25d", "v4"             # v4: voice C duo commentators + spoken READY-GO (v3: intros)
W, H, FPS = se.W, se.H, 30
# perspective: x, z in metres (z = depth). Higher camera than race25d so the floor reads as an arena.
F_PERSP, D0, DZ = 6000.0, 100.0, 8.0             # k(z) = F / (D0 + DZ*z): front 60 px/m, back (z=8.5) ≈ 36
Y_H, CAM_H = 276.0, 20.4
WORLD_DY, PIV_Y = 20.0, 1190.0                  # zoom pivot (world space)
ZC = 5.0                                         # arena centre depth
HX0, HZ0, HX_MIN, HZ_MIN = 13.0, 5.0, 8.5, 3.6   # floor half-size at start / after the last shrink (v2: wider)
SHRINK_AT, SHRINK_EVERY, SHRINK_STEP = 18.0, 7.0, 0.12
BARRIER_DOWN = 9.0                               # tyre barriers bounce cars back until then
# CHAOS library (v2, user 2026-10-01): sudden events that hit the arena. Own designs only (KRAGGOR is our
# dino-robot kaiju, not Godzilla). warn = seconds of warning (target ring / shadow / cracks) before impact.
CHAOS = {
    "missile": dict(warn=1.5, banner="MISSILE STRIKE!", line="Incoming missile!", bubble="KABOOM!"),
    "kraggor": dict(warn=2.4, banner="KRAGGOR ATTACK!", line="Oh no... it's Kraggor!", bubble="SPLAT!"),
    "ufo":     dict(warn=1.3, banner="UFO INVASION!", line="A UFO! It's got {n}!", bubble="HELP!"),
    "crack":   dict(warn=1.4, banner="THE FLOOR IS CRACKING!", line="The floor is breaking!", bubble="HOT HOT!"),
}
CHAOS_AT = [(4.5, 5.8), (9.5, 10.8), (14.5, 15.8), (19.5, 20.8)]
ANNOUNCERS = ["en-US-GuyNeural", "en-US-ChristopherNeural", "en-US-EricNeural"]   # arena announcer (male, en-US)
# announcer delivery per line type (edge-tts rate, pitch): slow + deep intro, fast + high action calls
VOICE_STYLE = {"intro": ("-8%", "-6Hz"), "hype": ("+20%", "+6Hz"), "call": ("+4%", "+2Hz"), "norm": ("+12%", "+0Hz"),
               "clear": ("+8%", "+0Hz")}
T_MAX = 40.0
POOL = ["sports", "police", "taxi", "f1", "bus", "firetruck", "icecream", "bigrig", "monster", "monster2"]
BIG = {"bus", "firetruck", "icecream", "bigrig"}
ARENAS = {
    "lava": dict(name="the lava", out_line="{n} is out!", bubble="HOT HOT!", grip=0.03),
    "mud":  dict(name="the mud", out_line="{n} is out!", bubble="YUCK!", grip=0.028),
    "ice":  dict(name="the icy water", out_line="{n} is out!", bubble="BRRR!", grip=0.01),
}
VMAX = {"f1": 8.4, "sports": 8.2, "police": 7.6, "taxi": 7.4, "monster": 7.2, "monster2": 7.2,
        "icecream": 6.0, "bus": 5.8, "firetruck": 5.8, "bigrig": 5.4}
TURN = {"f1": 3.2, "sports": 3.0, "police": 2.7, "taxi": 2.6, "monster": 2.4, "monster2": 2.4,
        "icecream": 1.8, "bus": 1.6, "firetruck": 1.6, "bigrig": 1.4}
HIT_BUBBLES = ["BAM!", "WHAM!", "CRUNCH!", "BONK!", "OOF!"]
TITLES = ["4 Cars Enter, 1 Survives! 💥 Smash Arena", "Last Car Standing Wins! 💥", "Who Survives the Smash Arena? 💥",
          "Crash Battle! Only One Can Win! 💥"]
TAGS = ["cars", "car crash", "demolition derby", "cartoon cars", "funny cars", "smash", "car battle", "shorts",
        "MegaWheel Arena"]

CAST, ARENA, CHAOS_PLAN = [], "lava", []
STANDS_TEXT = "SMASH ARENA"                      # banner on the stands (story scenes reuse the stands)
STANDS_ROWS = 6                                  # story scenes use fewer rows (sky visible for Kraggor)
FREEZE_T = 1e9                                   # the floor stops shrinking once there is a winner


def k_of(z):
    return F_PERSP / (D0 + DZ * z)


def ground_y(z):
    return Y_H + CAM_H * k_of(z)


def pxy(x, z, camx):
    return (x - camx) * k_of(z) + 540, ground_y(z)


def nick(vk):
    return se.VEHICLES[vk]["nick"]


def m_eff(vk):
    return (se.VEHICLES[vk]["mass"] / 1000.0) ** 0.4


def radius(vk):
    return 0.3 * se.VEHICLES[vk]["body"][0] + 0.25


def bounds(t):
    """Floor half-size (hx, hz) at time t: shrinks in eased steps."""
    hx, hz = HX0, HZ0
    s = min(t, FREEZE_T) - SHRINK_AT
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
    global CHAOS_PLAN
    kinds = [str(k) for k in r.permutation(list(CHAOS))]
    CHAOS_PLAN = [dict(type=k, T=float(r.uniform(*CHAOS_AT[i])), warn=CHAOS[k]["warn"]) for i, k in enumerate(kinds)]
    return dict(cast=cast, arena=ARENA, chaos=[[c["type"], round(c["T"], 2)] for c in CHAOS_PLAN])


# ------------------------------------------------------------------ scripted battle (120 Hz)
def simulate(seed):
    global FREEZE_T
    FREEZE_T = 1e9
    rng = np.random.default_rng(13000 + seed)
    dt = 1 / 120
    grip = ARENAS[ARENA]["grip"]
    corners = [(-9.0, ZC - 3.0), (9.0, ZC + 3.0), (9.0, ZC - 3.0), (-9.0, ZC + 3.0)]
    for ch in CHAOS_PLAN:
        for kk in ("armed", "done", "skip", "victim", "carry_end"):
            ch.pop(kk, None)
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
        ahx, ahz = bounds(t + 1.5)                               # drivers see the floor shrinking coming
        go = t >= 1.4                                            # READY... GO!
        esc = 1.0 + t / 22.0 + (0.12 * max(0.0, t - 16) if len(alive) <= 2 else 0.0)   # always ends
        if not sudden and t > 34.0 and len(alive) > 1:
            sudden = True
            events.append(("sudden", t, 0.0, ZC))
        danger = []                                              # warned impact zones: drivers try to escape
        for ch in CHAOS_PLAN:
            if ch.get("armed") and not ch.get("done") and not ch.get("skip") and ch["type"] in ("missile", "kraggor"):
                danger.append((ch["tx"], ch["tz"], 4.5 if ch["type"] == "missile" else 4.0))
        for c in cars:
            vk = c["key"]
            if c.get("carry") is not None:                       # held in the UFO beam
                cy = c["carry"]
                a_ = t - cy["T"]
                e_ = min(1.0, a_ / 1.8)
                e_ = e_ * e_ * (3 - 2 * e_)
                c["x"] = cy["x0"] + (cy["dx"] - cy["x0"]) * e_
                c["z"] = cy["z0"] + (cy["dz"] - cy["z0"]) * e_
                c["h"] = 3.8 * min(1.0, a_ / 0.6)
                c["vx"] = c["vz"] = c["vh"] = 0.0
                c["yaw"] += 2.5 * dt
                if a_ >= 1.8:                                    # dropped!
                    c["carry"] = None
                    c["vh"] = -2.0
                    c["stun"], c["last_push"] = 1.2, t
                    c["hp"] = max(0.0, c["hp"] - 18)
                    c["hits_taken"].append(t)
                    c["last_hit"] = t
                continue
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
                ex = abs(c["x"]) - (ahx - 2.6)                   # stay away from the edge
                ez = abs(c["z"] - ZC) - (ahz - 1.8)
                gain = 10.0 if t >= BARRIER_DOWN - 1.5 else 3.0
                if ex > 0:
                    ax -= math.copysign(ex * gain, c["x"])
                if ez > 0:
                    az -= math.copysign(ez * gain, c["z"] - ZC)
                for dx_, dz_, rr in danger:                      # escape the target ring / the kaiju's shadow
                    dd = math.hypot(c["x"] - dx_, c["z"] - dz_)
                    if dd < rr + 1.5:
                        ax += (c["x"] - dx_) / max(dd, 0.3) * 14.0
                        az += (c["z"] - dz_) / max(dd, 0.3) * 14.0
                want = math.atan2(az, ax)
                d = (want - c["th"] + math.pi) % (2 * math.pi) - math.pi
                c["th"] += float(np.clip(d, -TURN[vk] * dt, TURN[vk] * dt))
                vmax = VMAX[vk] * c["aggro"] * (0.8 if c["recoil"] > 0 else 1.0) * (0.6 + 0.4 * c["hp"] / 100)
                dvx, dvz = math.cos(c["th"]) * vmax - c["vx"], math.sin(c["th"]) * vmax - c["vz"]
                g = grip * 1.6 * (0.3 if c["stun"] > 0 else 1.0)   # dazed right after a hit: pushed around
                c["vx"] += dvx * g
                c["vz"] += dvz * g
            else:                                                # wrecked / waiting / celebrating: roll to a stop
                damp = 0.985 if ARENA == "ice" else 0.94
                if c is winner and t_end is not None:            # victory donut + hops
                    if c["h"] <= 0 and t - winner["finish"] > 0.6 and t - c.get("hop_t", -9) > 1.0:
                        c["vh"], c["hop_t"] = 5.0, t
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
                    if c["vh"] < -7 and winner is None:
                        events.append(("land", t, c["x"], c["z"]))
                    c["h"], c["vh"] = 0.0, 0.0
                    c["land"] = t
            c["spin"] = max(0.0, c["spin"] - dt)
            c["stun"] = max(0.0, c["stun"] - dt)
            if c["out_kind"] == "ring" and c["h"] <= 0 and t - c["out"] > 0.3:
                c["vx"] *= 0.9
                c["vz"] *= 0.9
            cs = math.cos(c["th"])                               # paper-card flip toward the driving direction,
            if c.get("face") is None or (c["face"] == 0.0 and cs < -0.35) or (c["face"] != 0.0 and cs > 0.35):
                c["face"] = 0.0 if cs >= 0 else math.pi          # (hysteresis: no flicker when driving in depth)
            face = c["face"]
            if c["spin"] > 0:
                c["yaw"] += 14.0 * dt
            else:
                tgt = face + round((c["yaw"] - face) / (2 * math.pi)) * 2 * math.pi
                c["yaw"] += float(np.clip(tgt - c["yaw"], -7 * dt, 7 * dt))
        # CHAOS: warn -> impact
        for ch in CHAOS_PLAN:
            if winner is not None or ch.get("skip") or ch.get("done"):
                continue
            if not ch.get("armed") and t >= ch["T"] - ch["warn"]:
                cand = [c for c in cars if c["alive"] and c.get("carry") is None]
                if not cand:
                    ch["skip"] = True
                    continue
                v = cand[int(rng.integers(len(cand)))]
                ch["armed"], ch["victim"] = True, v
                ch["tx"], ch["tz"] = v["x"], v["z"]
                if ch["type"] == "missile":                      # aimed where the victim is heading
                    ch["tx"] = float(np.clip(v["x"] + v["vx"] * ch["warn"] * 0.7, -hx + 1, hx - 1))
                    ch["tz"] = float(np.clip(v["z"] + v["vz"] * ch["warn"] * 0.7, ZC - hz + 1, ZC + hz - 1))
                if ch["type"] == "crack":
                    ch["tx"] = float(np.clip(v["x"], -hx + 2, hx - 2))
                    ch["tz"] = float(np.clip(v["z"], ZC - hz + 1.5, ZC + hz - 1.5))
                    ang = float(rng.uniform(0.25, 1.3)) * (1 if rng.random() < 0.5 else -1)
                    ch["ux"], ch["uz"], ch["L"] = math.cos(ang), math.sin(ang) * 0.55, 5.5
                    ch["seedc"] = int(rng.integers(1000))
                    ch["hit"] = set()
                events.append(("warn", t, ch["tx"], ch["tz"], ch["type"]))
            if not ch.get("armed"):
                continue
            v = ch["victim"]
            if ch["type"] == "kraggor" and t < ch["T"] - 0.9 and v["alive"]:   # the shadow follows, then locks
                ch["tx"] = float(np.clip(v["x"], -hx + 1, hx - 1))
                ch["tz"] = float(np.clip(v["z"], ZC - hz + 0.8, ZC + hz - 0.8))
            if ch["type"] == "ufo" and v["alive"]:
                ch["tx"], ch["tz"] = v["x"], v["z"]
            if t < ch["T"]:
                continue
            ch["done"] = True
            typ, tx_, tz_ = ch["type"], ch["tx"], ch["tz"]
            if typ == "ufo":
                if not v["alive"] or v.get("carry") is not None:
                    cand = [c for c in cars if c["alive"] and c.get("carry") is None]
                    if not cand:
                        ch["skip"] = True
                        continue
                    v = ch["victim"] = cand[int(rng.integers(len(cand)))]
                if t >= BARRIER_DOWN and v["hp"] < 60:           # weak car: dropped off the edge!
                    side = 1 if v["x"] >= 0 else -1
                    dxp, dzp = side * (hx + 2.2), float(np.clip(v["z"], ZC - hz + 1, ZC))
                else:
                    dxp = float(rng.uniform(-hx + 2, hx - 2))
                    dzp = float(rng.uniform(ZC - hz + 1, ZC))                  # drop it near the camera
                v["carry"] = dict(T=t, x0=v["x"], z0=v["z"], dx=dxp, dz=dzp)
                v.setdefault("chaos_hits", []).append((t, typ))
                ch.update(x0=v["x"], z0=v["z"], dx=dxp, dz=dzp)
                tx_, tz_ = v["x"], v["z"]
            for c in cars:
                if not c["alive"] or c.get("carry") is not None:
                    continue
                d = math.hypot(c["x"] - tx_, c["z"] - tz_)
                ux, uz = (c["x"] - tx_) / max(d, 0.3), (c["z"] - tz_) / max(d, 0.3)
                if typ == "missile" and d < 4.5:
                    c.setdefault("chaos_hits", []).append((t, typ))
                    f = 1 - d / 4.5
                    c["hp"] = max(0.0, c["hp"] - (12 + 30 * f))
                    c["vx"] += ux * (3 + 12 * f)
                    c["vz"] += uz * (3 + 12 * f)
                    c["vh"], c["spin"], c["stun"], c["last_push"] = 2 + 6 * f, 0.7, 0.9, t
                    c["soot"] = True
                    c["hits_taken"].append(t)
                    c["last_hit"] = t
                elif typ == "kraggor" and d < 7.0:
                    if d < 2.8:
                        c.setdefault("chaos_hits", []).append((t, typ))
                        c["hp"] = max(0.0, c["hp"] - 40)
                        c["squash_t"] = t
                        c["x"], c["z"] = tx_ + ux * 2.9, tz_ + uz * 2.9
                        c["stun"] = 1.4
                    else:
                        f = 1 - d / 7.0
                        c["hp"] = max(0.0, c["hp"] - 8 * f)
                        c["vx"] += ux * (2 + 7 * f)
                        c["vz"] += uz * (2 + 7 * f)
                        c["vh"], c["stun"] = 1.5 + 3 * f, 0.6
                    c["last_push"] = t
                    c["hits_taken"].append(t)
                    c["last_hit"] = t
            events.append(("chaos", t, tx_, tz_, typ))
        for ch in CHAOS_PLAN:                                    # lava erupting from the crack (2.4 s)
            if ch["type"] != "crack" or not ch.get("done") or ch.get("skip") or not 0 <= t - ch["T"] < 2.4:
                continue
            if winner is not None:
                continue
            for c in cars:
                if not c["alive"] or id(c) in ch["hit"] or c.get("carry") is not None:
                    continue
                rx, rz = c["x"] - ch["tx"], c["z"] - ch["tz"]
                along = max(-ch["L"], min(ch["L"], rx * ch["ux"] + rz * ch["uz"]))
                px_, pz_ = rx - along * ch["ux"], rz - along * ch["uz"]
                dd = math.hypot(px_, pz_)
                if dd < 1.1 + 0.25 * c["r"]:
                    ch["hit"].add(id(c))
                    nxp, nzp = (px_ / dd, pz_ / dd) if dd > 0.05 else (-ch["uz"], ch["ux"])
                    c["hp"] = max(0.0, c["hp"] - 28)
                    c["vx"] += nxp * 8
                    c["vz"] += nzp * 8
                    c["vh"], c["stun"], c["last_push"], c["soot"] = 7.0, 0.9, t, True
                    c["hits_taken"].append(t)
                    c["last_hit"] = t
                    c.setdefault("chaos_hits", []).append((t, "crack"))
                    events.append(("erupt", t, c["x"], c["z"]))
        # collisions (alive cars and wrecks; cars that fell off are gone)
        solid = [c for c in cars if (c["out_kind"] != "ring" or c["out"] is None) and c.get("carry") is None]
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
                if winner is None and go:                        # pushing and grinding wears both down
                    for me, oth in ((a, b), (b, a)):
                        if me["alive"]:
                            me["hp"] = max(0.0, me["hp"] - 2.8 * esc * dt * oth["m"] / (oth["m"] + me["m"]))
                if rel <= 0:
                    continue
                e = 0.35
                J = (1 + e) * rel / (1 / ma + 1 / mb)
                a["vx"] -= J / ma * nx
                a["vz"] -= J / ma * nz
                b["vx"] += J / mb * nx
                b["vz"] += J / mb * nz
                key = (id(a), id(b))
                if rel < 2.5 or t - cool.get(key, -9) < 0.45 or winner is not None:
                    continue
                cool[key] = t
                a["last_push"] = b["last_push"] = t
                hx_, hz_ = (a["x"] + b["x"]) / 2, (a["z"] + b["z"]) / 2
                for me, oth, sgn in ((a, b, 1), (b, a, -1)):
                    if not me["alive"]:
                        continue
                    front = math.cos(me["th"]) * nx * sgn + math.sin(me["th"]) * nz * sgn   # 1 = I hit with my nose
                    side = 1.35 if abs(front) < 0.45 else 1.0
                    armour = 0.55 if front > 0.6 else 1.0
                    dmg = 1.1 * rel * (oth["m"] / (oth["m"] + me["m"])) * 2 * side * armour * esc
                    me["hp"] = max(0.0, me["hp"] - dmg)
                    me["recoil"] = 0.85 if front > 0.3 else 0.35
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
        # eliminations (none after the winner is decided)
        for c in cars:
            if not c["alive"] or winner is not None or c.get("carry") is not None:
                continue
            if not any(o["alive"] for o in cars if o is not c):  # last car standing: it survives, whatever happens
                c["hp"] = max(c["hp"], 1.0)
                if abs(c["x"]) > hx + 0.2:
                    c["x"] = math.copysign(hx + 0.2, c["x"])
                if abs(c["z"] - ZC) > hz + 0.2:
                    c["z"] = ZC + math.copysign(hz + 0.2, c["z"] - ZC)
                continue
            if c["hp"] <= 0:
                c["alive"], c["out"], c["out_kind"] = False, t, "wreck"
                events.append(("wreck", t, c["x"], c["z"]))
            elif t < BARRIER_DOWN:                               # tyre barrier: bounce back in
                lim_x, lim_z = hx - 0.5 * c["r"], hz - 0.3 * c["r"]
                if abs(c["x"]) > lim_x:
                    c["x"] = math.copysign(lim_x, c["x"])
                    if c["vx"] * c["x"] > 0:
                        if abs(c["vx"]) > 3 and t - c.get("thud", -9) > 0.5:
                            events.append(("thud", t, c["x"], c["z"]))
                            c["thud"] = t
                        c["vx"] = -0.5 * c["vx"]
                if abs(c["z"] - ZC) > lim_z:
                    c["z"] = ZC + math.copysign(lim_z, c["z"] - ZC)
                    if c["vz"] * (c["z"] - ZC) > 0:
                        c["vz"] = -0.5 * c["vz"]
            elif (abs(c["x"]) > hx + 0.2 or abs(c["z"] - ZC) > hz + 0.2) and                     t - c.get("last_push", -9) > 0.8 and c["stun"] <= 0:  # nobody pushed it: teeter, drive back in
                if abs(c["x"]) > hx + 0.2:
                    c["x"] = math.copysign(hx + 0.2, c["x"])
                    c["vx"] = min(c["vx"], 0) if c["x"] > 0 else max(c["vx"], 0)
                if abs(c["z"] - ZC) > hz + 0.2:
                    c["z"] = ZC + math.copysign(hz + 0.2, c["z"] - ZC)
                    c["vz"] = min(c["vz"], 0) if c["z"] > ZC else max(c["vz"], 0)
            elif (abs(c["x"]) > hx + 0.2 or abs(c["z"] - ZC) > hz + 0.2) and c["h"] < 0.4:
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
            t_end = t + 4.6                                      # winner showcase
            FREEZE_T = t
        # record (race25d.state layout: x, z, h, yaw, pitch, v, sq, split, burn, patched, ice, tires)
        if int(round(t * 120)) % 4 == 0:
            for c in cars:
                sink = 0.0
                if c["out_kind"] == "ring" and c["out"] is not None and c["h"] <= 0 and t - c["out"] > 0.3:
                    sink = min(1.0, (t - c["out"] - 0.3) / 1.2)
                c["sink_rec"] = c.get("sink_rec", []) + [sink]
                tilt = 0.22 if c["out_kind"] == "wreck" else (-0.12 * min(1.0, c["vh"] / 4) if c["h"] > 0 else 0.0)
                sq = 0.88 if c["out_kind"] == "wreck" else 1.0
                if c.get("squash_t") is not None and 0 <= t - c["squash_t"] < 1.4:   # flattened by Kraggor, BOING
                    a_ = t - c["squash_t"]
                    sq = 0.42 if a_ < 0.9 else 0.42 + 0.58 * se.ease_out_back(min(1.0, (a_ - 0.9) / 0.4))
                burn = 1.0 if (c["hp"] < 45 or c.get("soot") or
                               (c["out_kind"] == "ring" and ARENA == "lava" and sink > 0)) else 0.0
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
    for ch in CHAOS_PLAN:
        if ch.get("done") and not ch.get("skip"):
            mom.append((ch["T"], 11.5 if ch["type"] in ("kraggor", "missile") else 10.5, ch["victim"]))
    return sorted(mom, key=lambda m: -m[1])


def build_timeline(cars, hits, winner):
    mom = big_moments(cars, hits)
    slows = sorted([(m[0] - 0.15, m[0] + 0.5) for m in mom[:2]])
    frames, t = [], 0.0
    end = winner["finish"] + 4.2                                 # the winner shows off before the replay
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
    for row in range(STANDS_ROWS):
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
        se.draw_text(ctx, STANDS_TEXT, (x0 - camx) * k + 540, y - 0.45 * k, 0.62 * k, fill=(1, 0.86, 0.12),
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


def chaos_live(t=None):
    """Chaos events to draw: armed ones; an event cut short by the final whistle is only shown until its impact."""
    return [ch for ch in CHAOS_PLAN if ch.get("armed") and not ch.get("skip")
            and (t is None or ch.get("done") or t < ch["T"])]


def crack_points(ch):
    rng = np.random.default_rng(ch["seedc"])
    pts = []
    for i in range(15):
        u = -ch["L"] + 2 * ch["L"] * i / 14
        j = float(rng.uniform(-0.35, 0.35)) if 0 < i < 14 else 0.0
        pts.append((ch["tx"] + u * ch["ux"] - j * ch["uz"], ch["tz"] + u * ch["uz"] + j * ch["ux"], u))
    return pts


def draw_kraggor_head(ctx, ch, t, stands_top):
    """KRAGGOR, our own dino-robot kaiju: rises behind the stands (screen space), roars, sinks back."""
    a = t - (ch["T"] - ch["warn"])
    if not 0 <= a < ch["warn"] + 2.3:
        return
    end = ch["warn"] + 1.5
    rise = se.ease_out_back(min(1.0, a / 0.8)) if a < end else max(0.0, 1 - (a - end) / 0.8)
    roar = max(0.0, math.sin(min(math.pi, max(0.0, a - 0.8) * 1.6)))
    S = 40.0
    body, metal = (0.24, 0.55, 0.36), (0.66, 0.68, 0.76)
    dark = se.shade(body, 0.62)
    ctx.save()
    ctx.translate(905, stands_top + 1.2 * S + (1 - rise) * 13 * S + math.sin(t * 20) * 3 * roar)
    ctx.scale(S, S)
    se.rrect(ctx, -3.0, -3, 6.0, 12, 1.4)                        # neck
    ctx.set_source_rgb(*se.lit(dark))
    ctx.fill()
    for i in range(5):                                           # silver back spikes
        bx = -3.0 + i * 1.5
        se.poly(ctx, [(bx - 0.65, -9.4), (bx, -12.0 - (0.8 if i == 2 else 0.0)), (bx + 0.65, -9.4)])
        ctx.set_source_rgb(*se.lit(metal))
        ctx.fill()
    se.rrect(ctx, -4.6, -10.2, 9.2, 7.6, 2.3)                    # head
    ctx.set_source_rgb(*se.lit(body))
    ctx.fill_preserve()
    ctx.set_source_rgb(*dark)
    ctx.set_line_width(0.28)
    ctx.stroke()
    se.rrect(ctx, -4.0, -9.6, 8.0, 1.4, 0.6)                     # metal brow plate + bolts
    ctx.set_source_rgb(*se.lit(metal))
    ctx.fill()
    for bx in (-3.3, -1.1, 1.1, 3.3):
        ctx.arc(bx, -8.9, 0.25, 0, 2 * math.pi)
        ctx.set_source_rgb(0.35, 0.35, 0.42)
        ctx.fill()
    for sgn in (-1, 1):                                          # glowing eyes, angry brows
        ex = sgn * 1.9
        ctx.arc(ex, -7.0, 1.0, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 0.88, 0.15)
        ctx.fill()
        ctx.arc(ex, -7.0, 1.6, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 0.9, 0.2, 0.25 + 0.2 * roar)
        ctx.fill()
        ctx.arc(ex + sgn * 0.15, -6.9, 0.42, 0, 2 * math.pi)
        ctx.set_source_rgb(0.85, 0.15, 0.05)
        ctx.fill()
        se.poly(ctx, [(ex - 1.3 * sgn, -8.5), (ex + 1.2 * sgn, -7.9), (ex + 1.2 * sgn, -8.4), (ex - 1.3 * sgn, -8.9)])
        ctx.set_source_rgb(*dark)
        ctx.fill()
    mh = 0.4 + 2.6 * roar                                        # mouth (cartoon, teeth only)
    se.rrect(ctx, -3.1, -4.2, 6.2, mh + 0.4, 0.5)
    ctx.set_source_rgb(0.5, 0.1, 0.14)
    ctx.fill()
    for i in range(7):
        tx_ = -2.7 + i * 0.9
        se.poly(ctx, [(tx_ - 0.32, -4.2), (tx_ + 0.32, -4.2), (tx_, -3.5)])
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        se.poly(ctx, [(tx_ - 0.3, -3.8 + mh), (tx_ + 0.3, -3.8 + mh), (tx_, -4.4 + mh)])
        ctx.fill()
    se.rrect(ctx, -3.7, -6.0, 7.4, 1.9, 0.8)                     # snout
    ctx.set_source_rgb(*se.lit(body))
    ctx.fill()
    for sgn in (-1, 1):
        ctx.arc(sgn * 0.9, -5.3, 0.28, 0, 2 * math.pi)
        ctx.set_source_rgb(*dark)
        ctx.fill()
    se.rrect(ctx, -3.6, -4.0 + mh, 7.2, 1.7, 0.7)                # lower jaw
    ctx.set_source_rgb(*se.lit(body))
    ctx.fill()
    ctx.restore()
    if roar > 0.35:                                              # roar waves
        for q in range(3):
            r = (1.5 + q * 1.4 + (t * 6) % 1.4) * S
            ctx.arc(905, stands_top - 2 * S, r, math.pi * 1.1, math.pi * 1.9)
            ctx.set_source_rgba(1, 1, 1, 0.5 * roar * (1 - q / 3))
            ctx.set_line_width(6)
            ctx.stroke()


def draw_chaos_ground(ctx, ch, t, camx):
    typ, a = ch["type"], t - ch["T"]
    tx, tz = ch["tx"], ch["tz"]
    sx, sy = pxy(tx, tz, camx)
    k = k_of(tz)

    def ellipse(rx, alpha, rgb, fill=True, lw=6):
        ctx.save()
        ctx.translate(sx, sy)
        ctx.scale(1.0, 0.42)
        ctx.arc(0, 0, rx * k, 0, 2 * math.pi)
        ctx.restore()
        if fill:
            ctx.set_source_rgba(*rgb, alpha)
            ctx.fill()
        else:
            ctx.set_source_rgba(*rgb, alpha)
            ctx.set_line_width(lw)
            ctx.stroke()

    if typ == "missile":
        if -ch["warn"] <= a < 0:                                 # pulsing target ring + crosshair
            pulse = 0.5 + 0.5 * math.sin(t * 18)
            ellipse(4.5, 0.18 + 0.12 * pulse, (1, 0.1, 0.1))
            ellipse(4.5, 0.9, (1, 0.15, 0.1), fill=False, lw=8)
            ellipse(2.2, 0.9, (1, 0.15, 0.1), fill=False, lw=6)
            for ang in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
                ctx.move_to(sx + math.cos(ang) * 1.0 * k, sy + math.sin(ang) * 0.42 * k)
                ctx.line_to(sx + math.cos(ang) * 5.0 * k, sy + math.sin(ang) * 0.42 * 5.0 * k)
            ctx.set_source_rgba(1, 0.15, 0.1, 0.9)
            ctx.set_line_width(6)
            ctx.stroke()
        elif a >= 0:                                             # crater
            ellipse(2.0, 0.85, (0.12, 0.1, 0.1))
            ellipse(2.0, 0.6, (0.35, 0.3, 0.28), fill=False, lw=0.18 * k)
            if a < 0.5:
                ellipse(4.5 * a / 0.5 + 0.5, 0.8 * (1 - a / 0.5), (1, 0.85, 0.5), fill=False, lw=10)
    elif typ == "kraggor":
        if -1.7 <= a < 0:                                        # the giant shadow grows
            g = 1 + a / 1.7
            ellipse(0.6 + 2.4 * g, 0.25 + 0.35 * g, (0, 0, 0))
        elif a >= 0:                                             # footprint cracks
            for q in range(9):
                ang = q * 2 * math.pi / 9 + 0.2
                ctx.move_to(sx + math.cos(ang) * 2.4 * k, sy + math.sin(ang) * 1.0 * k)
                ctx.line_to(sx + math.cos(ang + 0.15) * 4.2 * k, sy + math.sin(ang + 0.15) * 1.8 * k)
            ctx.set_source_rgba(0.1, 0.08, 0.08, 0.7)
            ctx.set_line_width(max(2, 0.1 * k))
            ctx.stroke()
            if a < 0.9:
                ellipse(3 + a * 6, 0.7 * (1 - a / 0.9), (0.85, 0.78, 0.65))
    elif typ == "ufo":
        if -ch["warn"] <= a < 1.8:
            ux, uz = ufo_pos(ch, t)[:2]
            px, py = pxy(ux, uz, camx)
            ctx.save()
            ctx.translate(px, py)
            ctx.scale(1.0, 0.42)
            ctx.arc(0, 0, 2.0 * k_of(uz), 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgba(0.3, 1, 0.4, 0.3 if a >= 0 else 0.12)
            ctx.fill()
    elif typ == "crack":
        if a < -ch["warn"]:
            return
        pts = crack_points(ch)
        frac = min(1.0, (a + ch["warn"]) / ch["warn"])
        vis = [(x, z) for x, z, u in pts if abs(u) <= frac * ch["L"] + 1e-6]
        if len(vis) < 2:
            return
        sp = [pxy(x, z, camx) for x, z in vis]
        if a >= 0:                                               # glowing fissure
            hot = 1.0 if a < 2.4 else max(0.35, 1 - (a - 2.4) / 2)
            for wdt, col in ((0.55, (1, 0.35, 0.05)), (0.25, (1, 0.85, 0.2))):
                ctx.move_to(*sp[0])
                for q in sp[1:]:
                    ctx.line_to(*q)
                ctx.set_source_rgba(*col, hot)
                ctx.set_line_width(wdt * k)
                ctx.stroke()
        else:
            ctx.move_to(*sp[0])
            for q in sp[1:]:
                ctx.line_to(*q)
            ctx.set_source_rgba(0.08, 0.06, 0.06, 0.9)
            ctx.set_line_width(max(3, 0.14 * k))
            ctx.stroke()


def ufo_pos(ch, t):
    """UFO position (x, z, altitude): flies in, follows its catch, leaves with a whoosh."""
    a = t - ch["T"]
    if a < 0:
        return ch["tx"] + (-a) * 9.0, ch["tz"], 5.5
    if a < 1.8:
        e = min(1.0, a / 1.8)
        e = e * e * (3 - 2 * e)
        return ch["x0"] + (ch["dx"] - ch["x0"]) * e, ch["z0"] + (ch["dz"] - ch["z0"]) * e, 5.5
    b = a - 1.8
    return ch["dx"] - b * 13.0, ch["dz"], 5.5 + b * 5.0


def draw_chaos_air(ctx, ch, t, camx):
    typ, a = ch["type"], t - ch["T"]
    tx, tz = ch["tx"], ch["tz"]
    sx, sy = pxy(tx, tz, camx)
    k = k_of(tz)
    if typ == "missile":
        if -0.6 <= a < 0:                                        # the missile drops in
            hh = 30.0 * (-a / 0.6)
            ctx.save()
            ctx.translate(sx, sy - hh * k)
            ctx.rotate(0.15)
            for j in range(3):                                   # flame tail (above: it falls down)
                fl = 1.6 + 0.6 * math.sin(t * 50 + j)
                se.poly(ctx, [(-0.3 * k, -2.0 * k), (0.3 * k, -2.0 * k), (0, (-2.0 - fl) * k)])
                ctx.set_source_rgba(1, 0.6 + 0.15 * j, 0.1, 0.8)
                ctx.fill()
            se.rrect(ctx, -0.32 * k, -2.0 * k, 0.64 * k, 1.8 * k, 0.15 * k)
            ctx.set_source_rgb(0.95, 0.95, 0.97)
            ctx.fill()
            se.poly(ctx, [(-0.32 * k, -0.2 * k), (0.32 * k, -0.2 * k), (0, 0.6 * k)])
            ctx.set_source_rgb(0.9, 0.12, 0.1)
            ctx.fill()
            for sgn in (-1, 1):
                se.poly(ctx, [(sgn * 0.32 * k, -2.0 * k), (sgn * 0.85 * k, -2.3 * k), (sgn * 0.32 * k, -1.4 * k)])
                ctx.set_source_rgb(0.5, 0.52, 0.6)
                ctx.fill()
            ctx.restore()
        elif 0 <= a < 1.2:                                       # explosion
            f = a / 1.2
            for j, (col, rr) in enumerate((((0.35, 0.33, 0.33), 1.0), ((1, 0.45, 0.1), 0.8), ((1, 0.9, 0.35), 0.5))):
                if j > 0 and a > 0.55:
                    continue
                for q in range(7):
                    ang = q * 2 * math.pi / 7 + j
                    r = (1.0 + 4.0 * min(1.0, a / 0.35)) * rr * k
                    ctx.arc(sx + math.cos(ang) * r * 0.55, sy - 1.6 * k - (a * 3) * k + math.sin(ang) * r * 0.45,
                            r * 0.55, 0, 2 * math.pi)
                    ctx.set_source_rgba(*col, (1 - f) * (0.9 if j else 0.7))
                    ctx.fill()
    elif typ == "kraggor":
        if -0.45 <= a < 1.4:                                     # the giant foot from the sky
            if a < 0:
                hf = 22.0 * (-a / 0.45) ** 2
            elif a < 0.8:
                hf = 0.0
            else:
                hf = 22.0 * ((a - 0.8) / 0.6) ** 2
            fy = sy - hf * k
            body = (0.24, 0.55, 0.36)
            dark = se.shade(body, 0.62)
            ctx.rectangle(sx - 1.7 * k, -3000, 3.4 * k, fy - 1.0 * k + 3000)   # leg
            ctx.set_source_rgb(*se.lit(body))
            ctx.fill()
            for q in range(30):                                  # scale stripes
                yy = fy - 1.6 * k - q * 1.2 * k
                if yy < -200:
                    break
                ctx.move_to(sx - 1.7 * k, yy)
                ctx.line_to(sx + 1.7 * k, yy - 0.3 * k)
            ctx.set_source_rgba(*dark, 0.7)
            ctx.set_line_width(max(2, 0.12 * k))
            ctx.stroke()
            se.rrect(ctx, sx - 2.7 * k, fy - 1.7 * k, 5.4 * k, 1.8 * k, 0.6 * k)   # foot
            ctx.set_source_rgb(*se.lit(body))
            ctx.fill_preserve()
            ctx.set_source_rgb(*dark)
            ctx.set_line_width(max(2, 0.1 * k))
            ctx.stroke()
            for q in (-1, 0, 1):                                 # toes + white claws
                cx = sx + q * 1.75 * k
                ctx.arc(cx, fy - 0.5 * k, 0.8 * k, 0, 2 * math.pi)
                ctx.set_source_rgb(*se.lit(body))
                ctx.fill()
                se.poly(ctx, [(cx - 0.35 * k, fy - 0.1 * k), (cx + 0.35 * k, fy - 0.1 * k), (cx + 0.15 * k, fy + 0.45 * k)])
                ctx.set_source_rgb(1, 1, 1)
                ctx.fill()
    elif typ == "ufo":
        if -ch["warn"] <= a < 3.2:
            ux, uz, alt = ufo_pos(ch, t)
            kk = k_of(uz)
            px, gy = pxy(ux, uz, camx)
            py = gy - alt * kk
            if 0 <= a < 1.8:                                     # tractor beam
                se.poly(ctx, [(px - 0.8 * kk, py + 0.3 * kk), (px + 0.8 * kk, py + 0.3 * kk),
                              (px + 2.0 * kk, gy), (px - 2.0 * kk, gy)])
                ctx.set_source_rgba(0.4, 1, 0.5, 0.3 + 0.08 * math.sin(t * 25))
                ctx.fill()
            ctx.save()
            ctx.translate(px, py)
            ctx.scale(1.0, 0.32)
            ctx.arc(0, 0, 3.9 * kk, 0, 2 * math.pi)
            ctx.restore()
            g = cairo.LinearGradient(0, py - kk, 0, py + kk)
            g.add_color_stop_rgb(0, 0.85, 0.87, 0.92)
            g.add_color_stop_rgb(1, 0.45, 0.47, 0.55)
            ctx.set_source(g)
            ctx.fill()
            ctx.arc(px, py - 0.3 * kk, 1.7 * kk, math.pi, 2 * math.pi)
            ctx.set_source_rgba(0.5, 0.9, 1.0, 0.9)
            ctx.fill()
            for q in range(7):                                   # blinking rim lights
                lx = px + (q - 3) * 1.05 * kk
                on = (int(t * 8) + q) % 2 == 0
                ctx.arc(lx, py + 0.15 * kk, 0.17 * kk, 0, 2 * math.pi)
                ctx.set_source_rgb(*((1, 0.9, 0.2) if on else (0.9, 0.3, 0.9)))
                ctx.fill()
    elif typ == "crack":
        if 0 <= a < 2.4:                                         # lava geysers along the crack
            pts = crack_points(ch)
            for j in range(1, 14, 2):
                x, z, u = pts[j]
                gx, gy = pxy(x, z, camx)
                kk = k_of(z)
                if a < 0.5:                                      # first burst: tall glowing columns
                    hcol = 5.5 * math.sin(math.pi * a / 0.5)
                    se.rrect(ctx, gx - 0.35 * kk, gy - hcol * kk, 0.7 * kk, hcol * kk, 0.3 * kk)
                    ctx.set_source_rgba(1, 0.55, 0.1, 0.9)
                    ctx.fill()
                for q in range(3):
                    ph = (a * 1.5 + q / 3 + j * 0.13) % 1.0
                    hh = 16 * ph * (1 - ph) * (1 - 0.4 * a / 2.4)
                    ctx.arc(gx + (ph - 0.5) * 0.8 * kk, gy - hh * kk, 0.3 * kk, 0, 2 * math.pi)
                    ctx.set_source_rgba(1, 0.75 if q else 0.45, 0.15, 0.95)
                    ctx.fill()


def spotlight(ctx, x, y, r0=130, r1=460, a=0.62):
    g = cairo.RadialGradient(x, y, r0, x, y, r1)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0.05, a)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.fill()
    g2 = cairo.RadialGradient(x, y, 0, x, y, r0 * 1.3)          # warm light cone
    g2.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.22)
    g2.add_color_stop_rgba(1, 1, 0.95, 0.75, 0)
    ctx.arc(x, y, r0 * 1.3, 0, 2 * math.pi)
    ctx.set_source(g2)
    ctx.fill()


def intro_card(ctx, vk, age, last):
    """Fighter card (lower third): name, what it is, weight, speed stars."""
    veh = se.VEHICLES[vk]
    slide = 1 - se.ease_out_back(min(1.0, age / 0.35))
    ctx.save()
    ctx.translate(-1100 * slide, 0)
    se.rrect(ctx, 40, 1390, 1000, 270, 34)
    ctx.set_source_rgba(0.05, 0.05, 0.14, 0.88)
    ctx.fill()
    se.rrect(ctx, 40, 1390, 36, 270, 18)
    ctx.set_source_rgb(*veh["color"])
    ctx.fill()
    se.draw_text(ctx, ("AND... " if last else "") + nick(vk).upper(), 560, 1470, 120, fill=(1, 0.86, 0.12), max_w=880)
    se.draw_text(ctx, "THE " + veh["display"].split(" THE ")[1], 560, 1560, 52, max_w=880)
    stars = int(round(1 + 4 * (VMAX[vk] - 5.4) / 3.0))
    se.draw_text(ctx, f"WEIGHT {veh['mass'] / 1000:.1f} T", 330, 1625, 40, fill=(0.8, 0.85, 1.0))
    se.draw_text(ctx, "SPEED", 640, 1625, 40, fill=(0.8, 0.85, 1.0))
    for q in range(5):                                           # drawn stars (the font has no star glyph)
        se.star(ctx, 745 + q * 48, 1625, 21, 0.0)
        ctx.set_source_rgb(*((1, 0.82, 0.1) if q < stars else (0.35, 0.37, 0.45)))
        ctx.fill()
    ctx.restore()


def crown(ctx, x, y, s):
    se.poly(ctx, [(x - s, y), (x - s, y - 0.9 * s), (x - 0.5 * s, y - 0.45 * s), (x, y - 1.1 * s),
                  (x + 0.5 * s, y - 0.45 * s), (x + s, y - 0.9 * s), (x + s, y)])
    ctx.set_source_rgb(1, 0.82, 0.1)
    ctx.fill_preserve()
    ctx.set_source_rgb(0.6, 0.4, 0.0)
    ctx.set_line_width(max(2, s * 0.08))
    ctx.stroke()
    for q, cx in enumerate((x - 0.5 * s, x, x + 0.5 * s)):
        ctx.arc(cx, y - 0.25 * s, s * 0.12, 0, 2 * math.pi)
        ctx.set_source_rgb(*((0.9, 0.1, 0.2) if q != 1 else (0.1, 0.5, 0.95)))
        ctx.fill()


def draw_hpbar(ctx, sx, sy, hp, k):
    w, h = 2.4 * k, 0.4 * k
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
def _band_noise(n, rng, lo, hi):
    x = rng.normal(0, 1, n)
    return box_avg(x, max(1, int(se.SR / hi))) - box_avg(x, max(2, int(se.SR / lo)))


def crowd_bed(dur, seed=5):
    """Arena crowd under everything: many voices (band noise with slow swells + chatter) and scattered claps."""
    rng = np.random.default_rng(seed)
    n = int(dur * se.SR)
    tt = np.arange(n) / se.SR
    x = _band_noise(n, rng, 250, 3500)
    swell = 0.65 + 0.35 * np.sin(2 * math.pi * 0.13 * tt + 1) * np.sin(2 * math.pi * 0.07 * tt)
    chatter = 0.7 + 0.3 * box_avg(np.abs(rng.normal(0, 1, n)), int(0.06 * se.SR)) / 0.8
    x = x / max(1e-9, np.max(np.abs(x))) * swell * chatter
    m = int(0.012 * se.SR)
    clap = rng.normal(0, 1, m) * np.exp(-np.linspace(0, 6, m))
    for i in rng.integers(0, max(1, n - m), int(dur * 16)):
        x[i:i + m] += clap * float(rng.uniform(0.15, 0.4))
    return x


def cheer(dur, strength=1.0, seed=7):
    """A cheer swell: crowd noise + a few 'wooo' voices."""
    rng = np.random.default_rng(seed)
    n = int(dur * se.SR)
    tt = np.arange(n) / se.SR
    x = _band_noise(n, rng, 300, 4500)
    x = x / max(1e-9, np.max(np.abs(x)))
    for _ in range(6):                                           # 'wooo' yells
        f0 = float(rng.uniform(450, 900))
        f = f0 * (1 + 0.25 * np.minimum(1.0, tt / 0.5)) + 12 * np.sin(2 * math.pi * float(rng.uniform(4, 7)) * tt)
        x += 0.08 * np.sin(2 * math.pi * np.cumsum(f) / se.SR) * np.exp(-tt * float(rng.uniform(0.8, 1.6)))
    env = np.minimum(1.0, tt / 0.15) * np.exp(-np.maximum(0.0, tt - 0.4) * 1.2)
    return x * env * strength


def gasp(seed=9):
    """Crowd 'ooooh!'."""
    rng = np.random.default_rng(seed)
    n = int(1.0 * se.SR)
    tt = np.arange(n) / se.SR
    x = 0.4 * _band_noise(n, rng, 200, 1500) / 3
    for f in (310, 620, 700, 1150):
        x += 0.18 * np.sin(2 * math.pi * f * (1 - 0.08 * tt) * tt)
    return x * np.minimum(1.0, tt / 0.12) * np.exp(-tt * 2.2)


def kaiju_roar(dur=2.1, seed=7):
    """KRAGGOR's roar (own sound design): low saw growl + distorted screech gliding down + rasp, with echoes."""
    rng = np.random.default_rng(seed)
    n = int(dur * se.SR)
    tt = np.arange(n) / se.SR
    env = np.minimum(1.0, tt / 0.25) * np.minimum(1.0, (dur - tt) / 0.7)
    f = 660 - 160 * tt / dur + 22 * np.sin(2 * math.pi * 6.5 * tt)
    ph = 2 * math.pi * np.cumsum(f) / se.SR
    scr = np.tanh(2.6 * sum(np.sin(ph * h) / h for h in range(1, 7)))
    fl = 68 + 10 * np.sin(2 * math.pi * 3 * tt)
    growl = (2 * ((np.cumsum(fl) / se.SR) % 1.0) - 1) * (0.75 + 0.25 * np.sin(2 * math.pi * 11 * tt))
    rasp = _band_noise(n, rng, 600, 3000)
    rasp = rasp / max(1e-9, np.max(np.abs(rasp)))
    sig = (0.55 * scr + 0.8 * growl + 0.3 * rasp) * env
    out = np.zeros(n + int(0.5 * se.SR))
    for d, g in ((0.0, 1.0), (0.11, 0.35), (0.24, 0.2)):
        i = int(d * se.SR)
        out[i:i + n] += sig * g
    return out


def kaiju_step(strength=1.0, seed=3):
    """Giant footstep: deep boom + rumble."""
    rng = np.random.default_rng(seed)
    n = int(1.2 * se.SR)
    tt = np.arange(n) / se.SR
    boom = np.sin(2 * math.pi * (48 - 12 * tt) * tt) * np.exp(-tt * 4.5)
    rum = box_avg(rng.normal(0, 1, n), int(se.SR / 180)) * 6 * np.exp(-tt * 3.0)
    return (boom + 0.5 * rum) * strength


def say(text, style, who="m1"):
    if text == se.READY_SENTINEL:                                # "Ready... set... GO!" (one phrase: clearer)
        x = say(se.READY_SET_GO, "clear", who)
        se.READY_GO_T = max(0.42, se.last_word_onset(x))         # GO pop on the spoken "GO"
        return x
    if USE_CB:
        return announcer.get(text, style, who)
    se.VOICE = EDGE_VOICES[who]
    se.TTS_RATE, se.TTS_PITCH = VOICE_STYLE[style]
    return se.tts(text)


def star_call_for(star_t, outs):
    """What the announcer says when the replay reaches the big moment."""
    call = "What a slam!"
    for ch in CHAOS_PLAN:
        if ch.get("done") and not ch.get("skip") and abs(ch["T"] - star_t) < 0.05:
            vn = nick(ch["victim"]["key"])
            call = {"kraggor": f"Look at that! Kraggor flattens {vn}!", "missile": f"Kaboom! Right on {vn}!",
                    "ufo": f"The UFO takes {vn} for a ride!", "crack": f"Lava blasts {vn} into the air!"}[ch["type"]]
    for c in outs:
        if abs(c["out"] - star_t) < 0.05:
            call = f"Look at {nick(c['key'])} go flying!" if c["out_kind"] == "ring" else f"{nick(c['key'])} is crushed!"
    return call


def schedule_narration(anchors, extras):
    """Commentary timing. anchors = [(want, text, style, who)] are always spoken, in order. extras = [(want, prio, text,
    style, max_late, who)] are spoken only if they fit in a free gap without moving an anchor and start at most
    max_late seconds after the action (higher priority first). The two commentators never talk over each other.
    Returns [(start, end, audio, text)] by start."""
    placed, busy = [], 0.0
    for w, txt, sty, who in sorted(anchors, key=lambda a: a[0]):
        a = say(txt, sty, who)
        t0 = max(w, busy + 0.15)
        busy = t0 + len(a) / se.SR
        placed.append((t0, busy, a, txt))
    for w, pr, txt, sty, ml, who in sorted(extras, key=lambda x: (-x[1], x[0])):
        if USE_CB and not announcer.cached(txt, sty, who):       # failed voice QA: skip this reaction line
            continue
        a = say(txt, sty, who)
        d = len(a) / se.SR
        t0, moved = w, True
        while moved:
            moved = False
            for s0, e0, _, _ in placed:
                if t0 < e0 + 0.15 and t0 + d > s0 - 0.15:
                    t0, moved = e0 + 0.15, True
        if t0 <= w + ml:
            placed.append((t0, t0 + d, a, txt))
    return sorted(placed, key=lambda q: q[0])


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


def box_avg(x, k):
    """Centred moving average (same result as np.convolve(x, ones(k)/k, "same"), but O(N))."""
    c = np.concatenate([[0.0], np.cumsum(x)])
    y = (c[k:] - c[:-k]) / k
    pad = len(x) - len(y)
    return np.pad(y, (pad // 2, pad - pad // 2), mode="edge")


def build_audio(frames, events, winner, star_t, replay, placed, voice, out_of, cta_start, intro_times=()):
    total = len(frames) / FPS
    n = int(total * se.SR) + se.SR
    narr, eng, sfx, crowd_buf = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)

    def place(buf, sig, t, gain=1.0):
        i0 = int(t * se.SR)
        if 0 <= i0 < n:
            m = min(len(sig), n - i0)
            buf[i0:i0 + m] += sig[:m] * gain

    for t0, _, a, _ in placed:
        place(narr, a, t0)
    wrel, amp, pitch = [], [], []
    for mode, t in frames:
        v = R.state(winner, t)[5] if mode not in ("cta", "intro") else 0.0
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
                place(crowd_buf, gasp(seed=ev[5]) if s > 0.75 else cheer(1.2, 0.6, seed=ev[5]), o + 0.05, 0.9)
        elif kind == "ringout":
            if ARENA == "lava":
                place(sfx, se.synth_lava_plunge(), o + 0.3, 0.9)
            elif ARENA == "mud":
                place(sfx, se.synth_splash(1.0, seed=43, big=True), o + 0.3, 0.9)
            else:
                place(sfx, se.synth_splash(1.0, seed=47, big=True), o + 0.3, 0.9)
                place(sfx, se.synth_shatter(seed=5), o + 0.3, 0.4)
            place(crowd_buf, cheer(2.6, 1.1, seed=9), o + 0.3, 1.0)
        elif kind == "wreck":
            place(sfx, se.synth_impact(1.0, seed=31), o, 0.8)
            place(sfx, R.boing(), o + 0.2, 0.6)
            place(crowd_buf, cheer(2.6, 1.1, seed=11), o + 0.2, 1.0)
        elif kind == "shrink":
            place(sfx, horn(), o, 0.45)
        elif kind == "sudden":
            place(sfx, horn(), o, 0.6)
        elif kind == "warn":
            typ, w = ev[4], CHAOS[ev[4]]["warn"]
            if typ == "missile":
                for q in range(3):
                    place(sfx, se.tone(880, 0.14, "sine", decay=0.1), o + q * 0.35, 0.5)
                place(sfx, se.sweep(1500, 260, 0.9, 0.5), o + w - 0.9, 0.7)
            elif typ == "kraggor":                               # footsteps while rising, roar with the open jaw
                for q in range(3):
                    place(sfx, kaiju_step(0.6 + 0.15 * q, seed=60 + q), o + q * 0.45, 1.0)
                place(sfx, kaiju_roar(2.1), o + 0.85, 1.25)
                place(sfx, gasp(seed=31), o + 0.3, 0.8)
            elif typ == "ufo":
                place(sfx, R.ufo_hum(w + 3.0), o, 0.6)
            elif typ == "crack":
                place(sfx, se.synth_lava_bed(w + 2.6, seed=89), o, 0.6)
                place(sfx, se.synth_shatter(seed=7), o + 0.2, 0.5)
        elif kind == "chaos":
            typ = ev[4]
            if typ == "missile":
                place(sfx, se.synth_eruption(seed=47), o, 1.0)
                place(sfx, se.synth_impact(1.0, seed=21), o, 0.9)
            elif typ == "kraggor":
                place(sfx, kaiju_step(1.6, seed=5), o, 1.2)
                place(sfx, se.synth_wall_crash(1.0), o, 0.8)
                place(sfx, R.boing(), o + 1.0, 0.6)
                place(sfx, kaiju_roar(1.4, seed=8), o + 0.5, 0.8)
            elif typ == "ufo":
                place(sfx, se.sweep(300, 1300, 0.8, 0.4), o, 0.6)
            elif typ == "crack":
                place(sfx, se.synth_eruption(seed=43), o, 1.0)
                place(sfx, se.synth_ignite(), o + 0.1, 0.7)
            place(crowd_buf, cheer(2.2, 1.0, seed=41), o + 0.2, 1.0)
        elif kind == "erupt":
            place(sfx, se.synth_impact(0.6, seed=17), o, 0.7)
            place(sfx, se.synth_fire(0.8, seed=21), o, 0.6)
        elif kind == "land":
            place(sfx, se.synth_impact(0.8, seed=11), o, 0.8)

    for ev in events:
        ev_sfx(ev, out_of(ev[1]))
    for q, it in enumerate(intro_times):                          # each fighter: whoosh + the crowd goes wild
        place(sfx, se.synth_whoosh(), it, 0.6)
        place(sfx, kaiju_step(0.5, seed=80 + q), it + 0.05, 0.5)
        place(crowd_buf, cheer(1.8, 0.9, seed=70 + q), it + 0.1, 1.0)
    place(sfx, se.synth_win(), out_of(winner["finish"]), 0.9)
    place(crowd_buf, cheer(3.0, 1.3, seed=23), out_of(winner["finish"]) + 1.6, 1.0)
    place(crowd_buf, cheer(4.5, 1.5, seed=21), out_of(winner["finish"]) + 0.05, 1.0)
    bed = crowd_bed(total + 1)                                   # the arena is never quiet (louder until the CTA)
    bed_env = np.ones(len(bed))
    bed_env[int(cta_start * se.SR):] = 0.45
    place(crowd_buf, bed * bed_env, 0.0, 0.35)
    if replay:
        r0, a, b = replay
        place(sfx, se.synth_rewind(), r0, 0.6)
        for ev in events:
            if a <= ev[1] < b and ev[0] in ("hit", "ringout", "wreck", "chaos", "erupt", "land"):
                ev_sfx(ev, r0 + (ev[1] - a) / 0.4, slow=0.5)
    for tap in (R.CTA_LIKE_T, R.CTA_SUB_T):
        place(sfx, se.tone(1300, 0.06, "sine", decay=0.02), cta_start + tap, 0.8)
    place(sfx, se.tone(1760, 0.8, "sine", decay=0.35) + se.tone(2637, 0.8, "sine", decay=0.25) * 0.5,
          cta_start + R.CTA_SUB_T + 0.05, 0.6)
    bgm = se.music_bed(total + 1, [out_of(winner["finish"]) + 1.6], style=se.th_time()["music"])   # after the cheer
    bgm = bgm[:n] if len(bgm) >= n else np.pad(bgm, (0, n - len(bgm)))
    talk = box_avg((np.abs(narr) > 0.01).astype(float), int(0.25 * se.SR))   # O(N), was a 40 s np.convolve
    duck = 1.0 - (1.0 - 10 ** (-se.DUCK_DB / 20)) * np.clip(talk * 3, 0, 1)
    # arena mix: announcer on top, crowd + effects big, engines low (it is a battle, not a race), music under
    mix = (se.peak(narr) * se.VOL_NARR + se.peak(eng) * se.VOL_ENGINE * 0.22 * duck + se.peak(bgm) * se.VOL_BGM * 0.6 * duck
           + se.peak(sfx) * se.VOL_SFX * (0.7 + 0.3 * duck) + se.peak(crowd_buf) * se.VOL_SFX * 0.75 * (0.6 + 0.4 * duck))
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
    ap.add_argument("--voice", default="chatterbox", choices=["chatterbox", "edge"],
                    help="announcer: chatterbox (Modal, cached; default) or edge (Edge TTS)")
    ap.add_argument("--dry-run", action="store_true", help="simulate + battle checks only, no render (seed search)")
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
    uses = {v: 0 for v in ANNOUNCERS}
    for e in active:
        if e.get("voice") in uses:
            uses[e["voice"]] += 1
    vr = np.random.default_rng(5100 + opt.seed)
    tie = {v: float(vr.random()) for v in ANNOUNCERS}
    voice = min(ANNOUNCERS, key=lambda v: (uses[v], tie[v]))
    cars, events, hits, winner = simulate(opt.seed)
    for st in shrink_times():
        if st < winner["finish"]:
            events.append(("shrink", st, 0.0, ZC))
    events.sort(key=lambda e: e[1])
    frames, replay, star_t, star, cta_start = build_timeline(cars, hits, winner)
    outs = sorted([c for c in cars if c["out"] is not None and c is not winner], key=lambda c: c["out"])
    print(f"[smash] {name} arena={ARENA} theme={se.THEME_ID} voice={voice} cast={[nick(c['key']) for c in cars]} "
          f"hits={len(hits)} big={sum(h['rel'] > 6 for h in hits)} "
          f"chaos={[(ch['type'], round(ch['T'], 1)) for ch in CHAOS_PLAN if ch.get('done') and not ch.get('skip')]} "
          f"outs={[(nick(c['key']), c['out_kind'], round(c['out'], 1)) for c in outs]} winner={nick(winner['key'])} "
          f"hp={round(winner['hp'])} battle={winner['finish']:.1f}s frames={len(frames)} ({len(frames) / FPS:.1f}s)",
          flush=True)
    if opt.dry_run:
        ok = (len(outs) == 3 and 15 <= winner["finish"] <= 38 and sum(h["rel"] > 6 for h in hits) >= 3
              and sum(1 for ch in CHAOS_PLAN if ch.get("done") and not ch.get("skip")) >= 3)
        print(f"[smash] dry-run {'PASS' if ok else 'FAIL'}", flush=True)
        raise SystemExit(0 if ok else 5)
    # every line the announcer may say, generated in ONE Modal call (cached); Edge TTS for the whole video if it fails
    global USE_CB
    se.VOICE = voice
    se.TTS_CLARITY = se.TTS_CLARITY + ",aecho=0.8:0.5:45|90:0.22|0.12"   # arena PA echo (Edge fallback)
    ladies = "Ladies and gentlemen... it's time to smash!"
    calls = [("And... " if i == 3 else "") + f"{nick(c['key'])}, the "
             f"{se.VEHICLES[c['key']]['display'].split(' THE ')[1].lower()}!" for i, c in enumerate(cars)]
    bigh = sorted([h for h in hits if h["rel"] > 7], key=lambda h: -h["rel"])[:3]
    star_call = star_call_for(star_t, outs) if replay else None
    win_line = f"The winner is... {nick(winner['key'])}! Yeah!"
    chaos_lines = [CHAOS[ch["type"]]["line"].format(n=nick(ch["victim"]["key"])) for ch in CHAOS_PLAN
                   if ch.get("done") and not ch.get("skip")]
    out_lines = [ARENAS[ARENA]["out_line"].format(n=nick(c["key"])) if c["out_kind"] == "ring"
                 else f"{nick(c['key'])} is down!" for c in outs]
    chaos_who = [CHAOS_WHO[ch["type"]] for ch in CHAOS_PLAN if ch.get("done") and not ch.get("skip")]
    react = "What a champion!"
    needed = ([(ladies, "intro", "m1"), (se.READY_SET_GO, "clear", "m1")]
              + [(cl, "hype", "m1") for cl in calls]
              + [(x, "hype", w) for x, w in zip(chaos_lines, chaos_who)] + [(x, "hype", "f1") for x in out_lines]
              + [("Barriers down!", "hype", "m1")] + [(HIT_CALLS_F[i % 3], "hype", "f1") for i in range(len(bigh))]
              + [(win_line, "call", "m1"), (react, "hype", "f1"),
                 ("Let's see that again... in slow motion!", "call", "f1"), (se.CTA, "norm", "m1")]
              + ([(star_call, "hype", "m1")] if star_call else []))
    essential = ([(ladies, "intro", "m1"), (se.READY_SET_GO, "clear", "m1"), (win_line, "call", "m1"),
                  ("Let's see that again... in slow motion!", "call", "f1"), (se.CTA, "norm", "m1")]
                 + [(cl, "hype", "m1") for cl in calls] + ([(star_call, "hype", "m1")] if star_call else []))
    if opt.voice == "chatterbox":
        announcer.prefetch(needed, note=f"announcer {name}")
    # voice C if every MUST-say line passed QA; a reaction line that failed QA is simply skipped
    USE_CB = opt.voice == "chatterbox" and all(announcer.cached(*e) for e in essential)
    if USE_CB:
        voice = announcer.VOICE_ID
    else:
        EDGE_VOICES["m1"] = voice
        voice = f"edge:{voice}+{EDGE_VOICES['f1']}"
    print(f"[smash] announcer: {voice}", flush=True)
    # INTRO: wide shot "Ladies and gentlemen", then every fighter is introduced (slot = length of the call)
    wide_len = len(say(ladies, "intro", "m1")) / se.SR + 0.45
    slots = [max(1.7, len(say(cl, "hype", "m1")) / se.SR + 0.5) for cl in calls]
    intro_starts = [wide_len + sum(slots[:i]) for i in range(4)]
    intro_frames = [("intro", j / FPS) for j in range(int((wide_len + sum(slots)) * FPS))]
    lf = len(intro_frames) / FPS
    frames = intro_frames + frames
    cta_start += lf
    if replay:
        replay = (replay[0] + lf, replay[1], replay[2])
    race_idx = [(j, ft) for j, (mode, ft) in enumerate(frames) if mode == "race"]

    def out_of(t):
        for j, ft in race_idx:
            if ft >= t:
                return j / FPS
        return len(frames) / FPS

    names = [nick(c["key"]) for c in cars]
    arena_word = {"lava": "the lava ring", "mud": "the mud pit", "ice": "the ice rink"}[ARENA]
    anchors = [(0.05, ladies, "intro", "m1"),
               (out_of(winner["finish"]) + 0.3, win_line, "call", "m1"),
               (cta_start + 0.2, se.CTA, "norm", "m1")]
    anchors += [(intro_starts[i] + 0.2, calls[i], "hype", "m1") for i in range(4)]
    anchors.append((out_of(0.0), se.READY_SENTINEL, "call", "m1"))
    extras = [(out_of(winner["finish"]) + 2.0, 2, react, "hype", 1.6, "f1")]   # (want, prio, text, style, late, who)
    for ch, line, who in zip([ch for ch in CHAOS_PLAN if ch.get("done") and not ch.get("skip")], chaos_lines, chaos_who):
        extras.append((out_of(ch["T"] - ch["warn"]) + 0.05, 3, line, "hype", 1.0, who))
    for c, line in zip(outs, out_lines):
        extras.append((out_of(c["out"]) + 0.15, 2, line, "hype", 1.3, "f1"))
    if BARRIER_DOWN < winner["finish"]:
        extras.append((out_of(BARRIER_DOWN), 1, "Barriers down!", "hype", 0.6, "m1"))
    if replay:                                                   # replay: announce it, then call the moment again
        anchors.append((replay[0] + 0.1, "Let's see that again... in slow motion!", "call", "f1"))
        r0, ra, rb = replay
        anchors.append((r0 + (star_t - ra) / 0.4 - 0.4, star_call, "hype", "m1"))
    for i, h in enumerate(bigh):
        extras.append((out_of(h["t"]) + 0.05, 0, HIT_CALLS_F[i % 3], "hype", 0.6, "f1"))
    placed = schedule_narration(anchors, extras)
    need = max(e for _, e, _, _ in placed) + 0.8                 # the end card lasts until the CTA is said
    while len(frames) / FPS < need:
        frames.append(("cta", frames[-1][1]))
    lines = [(t0, txt) for t0, _, _, txt in placed]
    print(f"[smash] narration (video {len(frames) / FPS:.1f}s, winner {out_of(winner['finish']):.1f}s, "
          f"replay {replay[0] if replay else -1:.1f}s, CTA {cta_start:.1f}s): "
          + " | ".join(f"{t0:.1f}-{e0:.1f} {txt[:34]}" for t0, e0, _, txt in placed), flush=True)

    date = time.strftime("%Y-%m-%d")
    out_dir = (f"{se.BASE}/work/lanes25d/previews/{name}" if opt.preview_only
               else f"{se.CHANNEL_DIR}/pending/{date}_{SERIES}_{ENGINE_VERSION}_s{opt.seed:03d}")   # version: never mixed
    prev = os.path.join(out_dir, "preview")
    os.makedirs(prev, exist_ok=True)
    os.makedirs(se.WORK, exist_ok=True)
    wav = f"{se.WORK}/mix_{name}.wav"
    se.write_wav(wav, build_audio(frames, events, winner, star_t, replay, placed, voice, out_of, cta_start,
                                  intro_times=intro_starts))
    silent = f"{se.WORK}/v_{name}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", silent],
                          stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    marks = {int(out_of(2.5) * FPS): "start", int(wide_len * 0.6 * FPS): "intro_wide"}
    for i, c in enumerate(cars):
        marks[int((intro_starts[i] + 1.0) * FPS)] = f"intro_{nick(c['key']).lower()}"
    marks[int(out_of(winner["finish"] + 2.6) * FPS)] = "showcase"
    for c in outs:
        marks[int(out_of(c["out"] + 0.35) * FPS)] = f"out_{nick(c['key']).lower()}"
    if bigh:
        marks.setdefault(int(out_of(bigh[0]["t"] + 0.05) * FPS), "bighit")
    for ch in chaos_live():
        if ch.get("done"):
            marks[int(out_of(ch["T"] + (0.5 if ch["type"] == "ufo" else 0.12)) * FPS)] = f"chaos_{ch['type']}"
            marks.setdefault(int(out_of(ch["T"] - ch["warn"] * 0.5) * FPS), f"warn_{ch['type']}")
    marks[int(out_of(winner["finish"] + 0.8) * FPS)] = "winner"
    marks[int((cta_start + 1.5) * FPS)] = "outro"
    hit_ev = [e for e in events if e[0] == "hit"]
    camx, zoom, prev_mode, empty_frames = None, 1.0, None, 0
    for fi, (mode, t) in enumerate(frames):
        u, intro_i = None, None
        if mode == "intro":                                      # cars wait on their spots during the intro
            u, t = t, 0.0
            if u >= wide_len:
                intro_i = max(i for i in range(4) if u >= intro_starts[i])
        st = {id(c): R.state(c, t) for c in cars}
        show = [c for c in cars if c["out"] is None or t < c["out"] + 1.6]
        focus = None
        for h in hits:                                           # zoom in a little on big hits
            if h["rel"] > 7 and -0.2 < t - h["t"] < 0.8:
                focus = (h["x"], h["z"])
        wide = False
        for ch in chaos_live(t):                                 # chaos is the show: frame it
            if ch["T"] - ch["warn"] * 0.85 < t < ch["T"] + (2.0 if ch["type"] == "ufo" else 1.3):
                focus = (ch["tx"], ch["tz"])
                if ch["type"] == "ufo" and t >= ch["T"]:
                    focus = ufo_pos(ch, t)[:2]
                wide = ch["type"] in ("kraggor", "ufo")
        if mode == "replay" and star is not None:
            focus = (st[id(star)][0], st[id(star)][1])
        if (winner["finish"] is not None and t >= winner["finish"]) or mode == "cta":
            focus = (st[id(winner)][0], st[id(winner)][1])
        if mode == "intro":
            focus = None if intro_i is None else (st[id(cars[intro_i])][0], st[id(cars[intro_i])][1])
        xs = [st[id(c)][0] for c in show]
        lo, hi = min(xs) - 3.0, max(xs) + 3.0
        mid = (lo + hi) / 2
        fit = float(np.clip(W * 0.95 / ((hi - lo) * k_of(ZC - 1)), 1.0, 1.45))
        target, want = (mid, fit)
        if focus is not None:
            target = 0.6 * focus[0] + 0.4 * mid
            want = min(1.6, max(fit, 1.15) * (1.2 if mode == "replay" else 1.08))
            if wide:
                want = min(want, 1.1)
            if mode == "intro":
                target, want = focus[0], 1.55
        cut = camx is None or (mode != prev_mode and not (prev_mode == "intro" and mode == "race"))
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
        for e in events:
            if e[0] == "chaos" and e[4] in ("missile", "kraggor", "crack") and 0 <= t - e[1] < 0.6:
                amp = 32 * (1 - (t - e[1]) / 0.6)
                shx, shy = amp * math.sin(t * 90), amp * math.cos(t * 70)
        flash = any(0 <= t - s < 1.3 and int((t - s) * 6) % 2 == 0 for s in shrink_times())
        cheer = 1.0 if any(0 <= t - e[1] < 1.5 for e in events if e[0] in ("ringout", "wreck", "chaos")) or \
            (t >= winner["finish"]) or mode == "intro" else 0.3
        se.draw_sky(ctx, camx * 0.35, WORLD_DY / se.S, 1.0)
        zb_top = ZC + HZ0 + 3.0 + 5 * 1.6                       # top row of the stands, in screen space
        top_w = ground_y(zb_top) - 6 * 1.25 * k_of(zb_top)
        stands_top = PIV_Y + (top_w - PIV_Y) * zoom + WORLD_DY + shy
        for ch in chaos_live(t):
            if ch["type"] == "kraggor":
                draw_kraggor_head(ctx, ch, t, stands_top)
        ctx.save()
        ctx.translate(0, WORLD_DY)
        ctx.translate(540 + shx, PIV_Y + shy)
        ctx.scale(zoom, zoom)
        ctx.translate(-540, -PIV_Y)
        draw_stands(ctx, camx, t, cheer)
        draw_arena(ctx, camx, t, flash)
        for ch in chaos_live(t):
            draw_chaos_ground(ctx, ch, t, camx)
        for e in hit_ev:
            draw_debris(ctx, e, t, camx, airborne=False)
        heads = {}
        for c in sorted(cars, key=lambda c: -st[id(c)][1]):
            sink = rec_at(c, "sink_rec", t)
            if sink >= 1.0:
                continue
            if sink > 0:
                ctx.push_group()
            hop = 0.0
            if intro_i is not None and c is cars[intro_i]:      # the introduced fighter bounces for the crowd
                hop = abs(math.sin((u - intro_starts[intro_i]) * 6.0)) * 0.7 * k_of(st[id(c)][1])
            ctx.save()
            ctx.translate(0, -hop)
            hd = R.draw_car(ctx, c, t, camx)
            ctx.restore()
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
        for ch in chaos_live(t):
            draw_chaos_air(ctx, ch, t, camx)
        ctx.restore()
        se.draw_weather(ctx, fi / FPS)
        if mode == "intro":
            if intro_i is None:
                se.draw_text(ctx, "SMASH ARENA!", W / 2, 170, 120, fill=(1, 0.86, 0.12))
                a_ = min(1.0, u / 0.5)
                se.draw_text(ctx, "4 FIGHTERS... 1 SURVIVOR!", W / 2, 1520, 76, fill=(1, 1, 1), alpha=a_)
            else:
                c = cars[intro_i]
                x_, z_ = st[id(c)][0], st[id(c)][1]
                sx_ = 540 + (x_ - camx) * k_of(z_) * zoom
                sy_ = PIV_Y + (ground_y(z_) - 1.3 * k_of(z_) - PIV_Y) * zoom + WORLD_DY
                spotlight(ctx, sx_, sy_)
                se.draw_text(ctx, "SMASH ARENA!", W / 2, 170, 100, fill=(1, 0.86, 0.12))
                intro_card(ctx, c["key"], u - intro_starts[intro_i], intro_i == 3)
        if mode == "race" and t >= winner["finish"] + 0.4 and id(winner) in heads:   # winner showcase
            sx_, sy_, k_, _ = heads[id(winner)]
            spotlight(ctx, sx_, sy_ + 60, 160, 520, 0.5)
            crown(ctx, sx_, sy_ - 70 - 6 * math.sin(t * 5), 0.9 * k_ * zoom)
        if mode not in ("cta", "intro"):
            for sx, sy, k, c in heads.values():
                for h in hits:
                    if h["rel"] > 6 and h["b"] is c:
                        R.bubble(ctx, HIT_BUBBLES[int(h["t"] * 7) % len(HIT_BUBBLES)], sx, sy, t - h["t"] - 0.05,
                                 k * zoom)
                if c["out"] is not None and c is not winner:
                    R.bubble(ctx, ARENAS[ARENA]["bubble"] if c["out_kind"] == "ring" else "I'M OUT!", sx, sy,
                             t - c["out"] - 0.1, k * zoom)
                for ht, typ in c.get("chaos_hits", []):
                    R.bubble(ctx, CHAOS[typ]["bubble"], sx, sy, t - ht - 0.05, k * zoom)
                if c is winner:
                    R.bubble(ctx, "CHAMPION!", sx, sy, t - winner["finish"] - 0.3, k * zoom)
            draw_hud(ctx, cars, t)
        if mode == "race":
            se.draw_ready_go(ctx, t)
            banners = [(s_, "ARENA SHRINKING!", 0) for s_ in shrink_times()]
            banners += [(BARRIER_DOWN, "BARRIERS DOWN!", 0)]
            banners += [(ch["T"] - ch["warn"], CHAOS[ch["type"]]["banner"], 1) for ch in chaos_live(t)]
            live = [(pr, s_, txt) for s_, txt, pr in banners if 0 <= t - s_ < 1.6 and t < winner["finish"]]
            for pr, s_, txt in sorted(live)[-1:]:                # one banner at a time: chaos first, then newest
                if True:
                    a = t - s_
                    sc = se.ease_out_back(min(1.0, a / 0.3)) * min(1.0, (1.6 - a) / 0.3)
                    ctx.save()
                    ctx.translate(540, 640)
                    ctx.scale(sc, sc)
                    se.draw_text(ctx, txt, 0, 0, 84, fill=(1, 0.3, 0.2), max_w=1000)
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
              "battle 15-38 s": 15 <= winner["finish"] <= 38,
              "at least 3 chaos events": sum(1 for ch in CHAOS_PLAN if ch.get("done") and not ch.get("skip")) >= 3,
              "at least 3 big hits": sum(h["rel"] > 6 for h in hits) >= 3,
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
                     "Missiles, a UFO, lava cracks and the monster Kraggor... last car standing wins!\n\n"
                     "Watch till the end for the slow-motion replay! 🎬\n\n🏆 Comment your champion below!\n"
                     f"🔔 Subscribe to {se.CHANNEL} for new car battles every day.\n\n"
                     "#Shorts #SmashArena #CartoonCars #CarCrash #MegaWheelArena"),
        tags=TAGS + [se.VEHICLES[c["key"]]["display"].split(" THE ")[1].lower() for c in cars] + [ARENA, "ufo",
                                                                                                 "kaiju", "missile"],
        narration=["Ready... Go!" if txt == se.READY_SENTINEL else txt for _, txt in lines],
        assets="100% procedurally generated (cairo 2.5D render + synthesized audio), narration " + (f"Chatterbox TTS (open source, Modal GPU) synthetic voice {voice}" if voice.startswith("chatterbox") else f"Edge-TTS {voice}"),
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
