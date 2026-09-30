#!/usr/bin/env python3
"""MegaWheel Kids procedural physics Shorts engine (sim-prototype v2).

Everything (footage, engine sounds, SFX, music) is generated here, so the
output is 100% original. Only the narration uses Edge-TTS.

Flow: simulate candidate runs -> pick runs matching the story (fail, fail, win)
-> build timeline (live + bullet-time + slow-mo replay) + audio
-> render frames in parallel -> mux MP4.

v2 features: dynamic camera (zoom, shake, speed lines), bullet-time on big
jumps, slow-mo instant replay, breakable cars (wheels fly off, debris, sparks,
smoke), character faces with moods + speech bubbles, named mascots.
"""
import argparse
import asyncio
import hashlib
import itertools
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

W, H = 1080, 1920
FPS = 30            # output fps (overridable with --fps)
SR = 44100
S = 72.0            # pixels per metre at zoom 1.0
GROUND_Y = 1290     # screen y of the camera anchor
PHYS_HZ = 240
REC_HZ = 120        # recorded state rate (sub-frame data for slow motion)
SUB_PER_REC = PHYS_HZ // REC_HZ
CTRL_EVERY = REC_HZ // 30   # control + event detection at 30 Hz
REPLAY_SPEED = 0.4
BULLET_RATE = 0.38
BASE = "/root/video-engine"
WORK = f"{BASE}/work/physics_2d"
OUT_DIR = f"{BASE}/renders"
CAST_FILE = f"{BASE}/cast/characters.json"
VOICE = "en-US-AnaNeural"
CTA = ("Tap LIKE if you enjoyed this video, DISLIKE if you didn't, "
       "and smash SUBSCRIBE to MegaWheel Kids!")
REPLAY_LINE = "Let's see that again, in slow motion!"

# Audio balance (from PROJECT_HISTORY_AND_HANDOVER.md, stems normalised to 0.45 peak first)
VOL_NARR, VOL_ENGINE, VOL_BGM, VOL_SFX = 1.60, 0.85, 0.10, 0.85

# ---------------------------------------------------------------- series + track
ENGINE_VERSION = "v2"
START_X = 3.0
FINISH_X = 100.0
SERIES_DEFS = {
    "potholes": dict(title="CARS VS GIANT POTHOLES!", obst="giant potholes", max_fail=20.0, max_win=24.0,
                     yt_title="Cars VS Giant Potholes! 🚗💥 Who Makes It? #Shorts",
                     tags=["cars", "potholes", "monster truck", "kids", "shorts", "physics", "MegaWheel Kids"]),
    "bumps": dict(title="CARS VS GIANT SPEED BUMPS!", obst="giant speed bumps", speed_scale=1.25,
                  max_fail=18.0, max_win=27.0,
                  yt_title="Cars VS Giant Speed Bumps! 🚗💥 Who Makes It? #Shorts",
                  tags=["cars", "speed bumps", "monster truck", "kids", "shorts", "physics", "MegaWheel Kids"]),
}
# Filled by make_track(series, seed). Potholes seed 1 is the reference track.
SERIES = ""
TITLE = ""
PITS = []           # (x0, x1, depth)
BUMPS = []          # (x0, x1, height)
RAMP = None         # (x0, x1, height) or None
OBSTACLES = []      # [(x_center, kind)] in track order, used for HUD markers + outcome tags
DANGER_X = []       # where faces get scared
SIGNS = []          # x of warning signs
TRACK = []
TRACK_PARAMS = {}
TRACK_ID = ""


def make_track(series, seed):
    global SERIES, TITLE
    SERIES = series
    TITLE = SERIES_DEFS[series]["title"]
    if series == "bumps":
        make_bumps_track(seed)
    else:
        make_potholes_track(seed)


# Speed-bump generator knobs (tuned with tune_bumps.py; see DEV_HISTORY)
BUMP_CFG = dict(n=(4, 5), x_first=(40.0, 44.0), gap=(6.5, 8.5), h0=0.6, dh=(0.6, 0.75), w0=2.0, wk=(0.85, 1.1),
                h_max=2.7)


def make_bumps_track(seed):
    """Half-sine speed bumps that grow in height (and steepness) towards the finish."""
    global PITS, BUMPS, RAMP, OBSTACLES, DANGER_X, SIGNS, TRACK, TRACK_PARAMS, TRACK_ID, FINISH_X
    FINISH_X = 100.0
    c = BUMP_CFG
    r = np.random.default_rng(2000 + seed)
    n = int(r.integers(c["n"][0], c["n"][1]))
    bumps, x = [], float(r.uniform(*c["x_first"]))
    for i in range(n):
        h = round(float(min(c.get("h_max", 9.0), c["h0"] + i * r.uniform(*c["dh"]))), 2)
        w = round(float(c["w0"] + h * r.uniform(*c["wk"])), 1)
        x = round(x, 1)
        bumps.append((x, round(x + w, 1), h))
        x += w + float(r.uniform(*c["gap"]))
        if x > FINISH_X - 10:
            break
    TRACK = [(-40, 0)]
    for x0, x1, h in bumps:
        for k in range(13):
            t = k / 12
            TRACK.append((round(x0 + (x1 - x0) * t, 3), round(h * math.sin(math.pi * t), 3)))
    TRACK.append((170, 0))
    PITS, RAMP, BUMPS = [], None, bumps
    FINISH_X = round(bumps[-1][1] + 10.0, 1)     # finish right after the last bump keeps level 3 short
    OBSTACLES = [((x0 + x1) / 2, "bump") for x0, x1, _ in bumps]
    DANGER_X = [b[0] for b in bumps]
    SIGNS = [b[0] - 3 for b in bumps[1::2]]
    TRACK_PARAMS = dict(bumps=bumps)
    TRACK_ID = "bumps_" + hashlib.md5(json.dumps(bumps).encode()).hexdigest()[:8]


def make_potholes_track(seed):
    global PITS, BUMPS, RAMP, OBSTACLES, DANGER_X, SIGNS, TRACK, TRACK_PARAMS, TRACK_ID, FINISH_X
    FINISH_X = 100.0
    if seed == 1:
        p = dict(p1x=30.0, p1w=3.2, p1d=3.2, rampx=48.0, rampl=6.0, ramph=1.4, p2w=8.0, p2d=5.0,
                 p3x=78.0, p3w=5.0, p3d=3.5)
    else:
        r = np.random.default_rng(1000 + seed)
        p = dict(p1x=r.uniform(26, 32), p1w=r.uniform(2.6, 3.8), p1d=r.uniform(2.8, 3.8))
        p["rampx"] = p["p1x"] + p["p1w"] + r.uniform(11, 16)
        p.update(rampl=r.uniform(5, 7), ramph=r.uniform(1.1, 1.7), p2w=r.uniform(6.5, 9.0), p2d=r.uniform(4.2, 5.5))
        p["p3x"] = p["rampx"] + p["rampl"] + p["p2w"] + r.uniform(13, 18)
        p.update(p3w=r.uniform(3.8, 5.6), p3d=r.uniform(3.0, 4.2))
        p = {k: round(float(val), 1) for k, val in p.items()}
    x1 = round(p["p1x"] + p["p1w"], 1)
    rx1 = round(p["rampx"] + p["rampl"], 1)
    p2x1 = round(rx1 + p["p2w"], 1)
    p3x1 = round(p["p3x"] + p["p3w"], 1)
    TRACK = [(-40, 0), (p["p1x"], 0), (p["p1x"], -p["p1d"]), (x1, -p["p1d"]), (x1, 0), (p["rampx"], 0),
             (rx1, p["ramph"]), (rx1, -p["p2d"]), (p2x1, -p["p2d"]), (p2x1, 0), (p["p3x"], 0),
             (p["p3x"], -p["p3d"]), (p3x1, -p["p3d"]), (p3x1, 0), (170, 0)]
    PITS = [(p["p1x"], x1, p["p1d"]), (rx1, p2x1, p["p2d"]), (p["p3x"], p3x1, p["p3d"])]
    RAMP = (p["rampx"], rx1, p["ramph"])
    BUMPS = []
    OBSTACLES = [((a + b) / 2, "pit") for a, b, _ in PITS]
    DANGER_X = [p["p1x"], p["rampx"], p["p3x"]]
    SIGNS = [p["p1x"] - 3, p["rampx"] - 2.5, p["p3x"] - 3]
    TRACK_PARAMS = p
    TRACK_ID = f"{SERIES}_std" if seed == 1 else \
        f"{SERIES}_" + hashlib.md5(json.dumps(p, sort_keys=True).encode()).hexdigest()[:8]


def ground_h(x):
    for a, b in zip(TRACK, TRACK[1:]):
        if a[0] <= x <= b[0] and b[0] - a[0] > 1e-6:
            return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])
    return 0.0


# ---------------------------------------------------------------- vehicles
VEHICLES = {
    "sports": dict(nick="Zippy", display="ZIPPY THE SPORTS CAR", color=(0.93, 0.16, 0.18),
                   body=(4.2, 0.62), mass=900, wheel_r=0.42, wheel_m=25, wheel_x=(-1.35, 1.4),
                   travel=0.45, speeds=(7, 17), break_dv=4.5, zoom=1.08,
                   cabin=[(-1.3, 0.31), (0.5, 0.31), (-0.1, 0.85), (-1.0, 0.85)], engine=(55, 2.2),
                   intro="Level {lvl}! Zippy the sports car! Can Zippy survive the {obst}?"),
    "police": dict(nick="Siren", display="SIREN THE POLICE CAR", color=(0.96, 0.96, 0.98),
                   body=(4.4, 0.7), mass=1150, wheel_r=0.43, wheel_m=28, wheel_x=(-1.45, 1.45),
                   travel=0.45, speeds=(7, 17), break_dv=4.5, zoom=1.05,
                   cabin=[(-1.4, 0.35), (0.7, 0.35), (0.2, 0.95), (-1.2, 0.95)], engine=(50, 2.0),
                   intro="Level {lvl}! Siren the police car is on patrol! Can Siren make it past the {obst}?"),
    "bus": dict(nick="Buster", display="BUSTER THE SCHOOL BUS", color=(1.0, 0.78, 0.05),
                body=(7.4, 2.1), mass=5200, wheel_r=0.55, wheel_m=90, wheel_x=(-2.5, 2.3),
                travel=0.35, speeds=(6, 14), break_dv=4.0, zoom=0.86, cabin=None, engine=(38, 1.3),
                intro="Level {lvl}! Buster the school bus. Big and heavy... can Buster make it?"),
    "firetruck": dict(nick="Hydro", display="HYDRO THE FIRE TRUCK", color=(0.88, 0.1, 0.1),
                      body=(6.4, 1.9), mass=6000, wheel_r=0.6, wheel_m=100, wheel_x=(-2.0, 2.1),
                      travel=0.35, speeds=(6, 14), break_dv=4.0, zoom=0.88, cabin=None, engine=(40, 1.3),
                      intro="Level {lvl}! Hydro the fire truck! Long and heavy... can Hydro make it?"),
    "monster": dict(nick="Rocky", display="ROCKY THE MONSTER TRUCK", color=(0.12, 0.45, 0.95),
                    body=(4.3, 0.9), mass=2400, wheel_r=1.0, wheel_m=130, wheel_x=(-1.75, 1.75),
                    travel=1.0, speeds=(9, 20), break_dv=8.0, zoom=0.95,
                    cabin=[(-1.5, 0.45), (0.4, 0.45), (0.0, 1.35), (-1.3, 1.35)], engine=(36, 1.7),
                    intro="Level {lvl}! Rocky the monster truck. Big wheels, big jump!"),
}
VEHICLES["monster2"] = dict(VEHICLES["monster"], nick="Grizzly", display="GRIZZLY THE MONSTER TRUCK",
                            color=(0.2, 0.72, 0.25),
                            intro="Level {lvl}! Grizzly the monster truck! Can Grizzly smash through the {obst}?")
FACES = {
    "sports": dict(eyes=[(-0.75, 0.56), (-0.35, 0.56)], r=0.13, mouth=(1.62, -0.17), mw=0.3),
    "police": dict(eyes=[(-0.7, 0.62), (-0.28, 0.62)], r=0.13, mouth=(1.72, -0.18), mw=0.3),
    "bus": dict(eyes=[(2.8, 0.42), (3.22, 0.42)], r=0.16, mouth=(3.3, -0.72), mw=0.38),
    "firetruck": dict(eyes=[(2.35, 0.3), (2.75, 0.3)], r=0.15, mouth=(2.85, -0.62), mw=0.36),
    "monster": dict(eyes=[(-0.8, 0.9), (-0.35, 0.9)], r=0.16, mouth=(1.7, -0.22), mw=0.34),
}
FACES["monster2"] = FACES["monster"]
# Level roles: seed picks one vehicle per role (potholes seed 1 keeps the reference line-up)
ROSTER = [(("sports", "police"), "fail"), (("bus", "firetruck"), "fail"), (("monster", "monster2"), "win")]
STORY = [("sports", "fail"), ("bus", "fail"), ("monster", "win")]
NUM_WORDS = ["one", "two", "three", "four", "five"]


def load_cast():
    """Fixed cast identity (name, colour, intro line) from cast/characters.json; physics stays in VEHICLES."""
    if not os.path.exists(CAST_FILE):
        return
    with open(CAST_FILE) as fh:
        cast = json.load(fh)["characters"]
    for c in cast:
        v = VEHICLES.get(c["vehicle_id"])
        if v is None:
            continue
        v.update(nick=c["name"], display=c["display"], color=tuple(x / 255 for x in c["color_rgb"]),
                 intro=c["intro"])


def make_story(series, seed, appearances=None):
    """Pick one character per role: fewest appearances first (fair rotation), seed breaks ties."""
    global STORY
    if series == "potholes" and seed == 1:
        STORY = [("sports", "fail"), ("bus", "fail"), ("monster", "win")]
        return
    r = np.random.default_rng(3000 + seed)
    appearances = appearances or {}
    story = []
    for opts, want in ROSTER:
        least = min(appearances.get(o, 0) for o in opts)
        pool = [o for o in opts if appearances.get(o, 0) == least]
        story.append((pool[int(r.integers(len(pool)))], want))
    STORY = story


def intro_text(li, vk):
    return VEHICLES[vk]["intro"].format(lvl=NUM_WORDS[li], obst=SERIES_DEFS[SERIES]["obst"])
FAIL_LINES = {"pit": "Oh no! {n} fell into the giant pothole!",
              "flip": "Whoa! {n} flipped right over!",
              "stuck": "Uh oh... {n} is totally stuck!"}
WIN_LINE = "Yes! {n} made it! We have a winner!"
LEVEL_COLORS = [(0.18, 0.72, 0.3), (1.0, 0.52, 0.08), (0.6, 0.3, 0.92)]


# ================================================================ physics
def build_space():
    space = pymunk.Space()
    space.gravity = (0, -9.81)
    space.iterations = 25
    for a, b in zip(TRACK, TRACK[1:]):
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
    wheels, motors, joints = [], [], []
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
        joints.append([groove, spring, motor])
    return dict(chassis=chassis, wheels=wheels, motors=motors, joints=joints, torque=torque, ride_y=ride_y)


def nearest_obstacle(x):
    best, bi = 1e9, -1
    for i, (x0, x1, _) in enumerate(PITS or BUMPS):
        d = 0 if x0 - 1 <= x <= x1 + 1 else min(abs(x - x0), abs(x - x1))
        if d < best:
            best, bi = d, i
    return bi


def break_car(space, car, v, rng, dv, i):
    """Detach wheel(s) and spawn debris. Returns list of debris dicts."""
    ch, wheels = car["chassis"], car["wheels"]
    idxs = [len(wheels) - 1] + ([0] if dv > 1.6 * v["break_dv"] else [])
    for wi in idxs:
        for c in car["joints"][wi]:
            space.remove(c)
        w = wheels[wi]
        w.velocity = w.velocity + (rng.uniform(1, 4), rng.uniform(3, 6))
        w.angular_velocity += rng.uniform(-15, 15)
        car["detached"][wi] = i
    flt = pymunk.ShapeFilter(group=1)
    c = v["color"]
    specs = ([("panel", (0.9, 0.45), c), ("panel", (0.7, 0.35), c), ("bumper", (1.1, 0.16), (0.2, 0.2, 0.22)),
              ("hubcap", 0.2, (0.8, 0.8, 0.85))] + [("glass", 0.2, (0.7, 0.9, 1.0))] * 6)
    debris = []
    for kind, size, col in specs:
        mass = 6.0
        if kind == "hubcap":
            body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, size))
            shape = pymunk.Circle(body, size)
            verts = None
        else:
            if kind == "glass":
                verts = [(-size / 2, -size / 3), (size / 2, -size / 3), (0, size / 1.5)]
            else:
                verts = [(-size[0] / 2, -size[1] / 2), (size[0] / 2, -size[1] / 2),
                         (size[0] / 2, size[1] / 2), (-size[0] / 2, size[1] / 2)]
            body = pymunk.Body(mass, pymunk.moment_for_poly(mass, verts))
            shape = pymunk.Poly(body, verts)
        body.position = ch.position + (rng.uniform(-1.2, 1.2), rng.uniform(0.6, 1.2))
        body.velocity = ch.velocity * 0.4 + (rng.uniform(-4, 4), rng.uniform(3, 9))
        body.angular_velocity = rng.uniform(-12, 12)
        shape.friction = 0.8
        shape.elasticity = 0.3
        shape.filter = flt
        space.add(body, shape)
        debris.append(dict(body=body, kind=kind, size=size, verts=verts, color=col, spawn=i))
    return debris


def simulate(v, speed, after_fail=6.0, after_win=16.0, t_max=24.0):
    rng = np.random.default_rng(int(speed * 1000) + int(v["mass"]))
    space = build_space()
    car = spawn(space, v, START_X)
    car["detached"] = [None] * len(car["wheels"])
    ch, wheels, motors = car["chassis"], car["wheels"], car["motors"]
    bw, bh = v["body"]
    r = v["wheel_r"]
    dt = 1.0 / PHYS_HZ
    for m in motors:
        m.rate = 0
    for _ in range(int(0.7 / dt)):          # settle suspension, not recorded
        space.step(dt)

    target = speed / r                      # SimpleMotor: wheel.w - chassis.w = -rate -> +x motion
    rec = dict(cx=[], cy=[], ca=[], wheels=[], wrel=[], speed=[], air=[])
    deb_rec, debris = [], []
    impacts, event, broken = [], None, None
    flip_t = stuck_t = None
    prev_v = ch.velocity
    last_imp = -1.0
    i = 0
    while True:
        t = i / REC_HZ
        if i % CTRL_EVERY == 0:
            if event is None:
                rate, force = target, car["torque"]
            elif event["type"] == "win":
                rate, force = target * max(0.0, 1 - (t - event["t"]) / 2.5), car["torque"] * 0.6
            else:
                rate, force = 0.0, 0.0
            for m in motors:
                m.rate, m.max_force = rate, force

        attached = [w for wi, w in enumerate(wheels) if car["detached"][wi] is None]
        rec["cx"].append(ch.position.x)
        rec["cy"].append(ch.position.y)
        rec["ca"].append(ch.angle)
        rec["wheels"].append([(w.position.x, w.position.y, w.angle) for w in wheels])
        rec["wrel"].append(float(np.mean([abs(w.angular_velocity - ch.angular_velocity) for w in attached]))
                           if attached else 0.0)
        rec["speed"].append(ch.velocity.length)
        rec["air"].append(float(bool(attached) and all(w.position.y - r > ground_h(w.position.x) + 0.12
                                                      for w in attached)))
        deb_rec.append([(d["body"].position.x, d["body"].position.y, d["body"].angle) for d in debris])

        for _ in range(SUB_PER_REC):
            space.step(dt)
        i += 1
        if i % CTRL_EVERY:
            continue
        t = i / REC_HZ

        dv = (ch.velocity - prev_v).length
        prev_v = ch.velocity
        if dv > 2.5 and t - last_imp > 0.25:
            impacts.append((t, min(1.0, dv / 10.0), ch.position.x, ch.position.y))
            last_imp = t
        if event is not None and event["type"] != "win" and broken is None and dv > v["break_dv"]:
            debris = break_car(space, car, v, rng, dv, i)
            broken = dict(t=t, x=ch.position.x, y=ch.position.y)

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
        elif t >= event["t"] + (after_win if event["type"] == "win" else after_fail):
            break

    for k in rec:
        rec[k] = np.asarray(rec[k], dtype=np.float64)
    n = len(rec["cx"])
    deb = np.full((n, len(debris), 3), np.nan)
    for si, row in enumerate(deb_rec):
        for di, stt in enumerate(row):
            deb[si, di] = stt
    if rec["cx"][-1] < rec["cx"][0] + 1 and event["type"] != "stuck":
        raise RuntimeError("car did not move forward, motor sign is wrong")
    meta = [{k: d[k] for k in ("kind", "size", "verts", "color", "spawn")} for d in debris]
    return dict(rec=rec, impacts=impacts, event=event, speed=float(speed), broken=broken,
                debris=deb, debris_meta=meta, detached=car["detached"])


TARGET_TOTAL = (42.0, 49.5)   # seconds, pacing window used when picking runs
PICK_STATS = {}


def event_min_t(intro_d):
    """Earliest allowed outcome: may overlap the intro's tail; the outcome line waits for the intro."""
    return max(2.5, intro_d - 1.0)


def level_cap(L):
    d = SERIES_DEFS[SERIES]
    return d["max_win"] if L["event"]["type"] == "win" else d["max_fail"]


def is_spectacular(L):
    """Crash-worthy fail level: broken car, flip, or a big bullet-time jump."""
    return bool(L["broken"] or L["event"]["type"] == "flip" or L.get("bullet"))


def outcome_vo_t(ev_out, intro_d):
    """Output time (level-local) of the outcome narration: after the event AND after the intro."""
    return max(ev_out + 0.25, 0.15 + intro_d + 0.2)


def candidate_runs(intro_durs):
    """All simulated runs per level that match the wanted outcome and timing."""
    out = []
    scale = SERIES_DEFS[SERIES].get("speed_scale", 1.0)
    for li, (vk, want) in enumerate(STORY):
        v = VEHICLES[vk]
        lo = event_min_t(intro_durs[li])
        hi = 15.0 if want == "win" else 11.5
        cands, summary = [], []
        for sp in np.linspace(v["speeds"][0] * scale, v["speeds"][1] * scale, 21):
            run = simulate(v, sp)
            ev = run["event"]
            summary.append(f"{sp:.1f}:{ev['type']}@{ev['t']:.1f}s/obs{ev['obstacle']}{'/BRK' if run['broken'] else ''}")
            is_win = ev["type"] == "win"
            if (want == "win") == is_win and ev["type"] != "timeout" and lo <= ev["t"] <= hi:
                cands.append(run)
        print(f"[sim] {vk}: " + ", ".join(summary), flush=True)
        if not cands:
            raise SystemExit(f"[analysis] STOP: tidak ada run {vk} dengan hasil '{want}' di lintasan ini. Coba seed lain.")
        out.append(cands)
    return out


def level_timing(vk, run, intro_d, outcome_d, cta_d):
    """Level dict with replay/outro/bullet windows and output frames (no camera yet)."""
    ev = run["event"]
    L = dict(vk=vk, v=VEHICLES[vk], **run)
    tmax = (len(run["rec"]["cx"]) - 1) / REC_HZ
    if ev["type"] == "win":
        L["outro_t"] = ev["t"] + outcome_d + 0.3
        L["live_end"] = L["outro_t"] + cta_d + 0.8
        L["replay"] = None
    else:
        L["live_end"] = ev["t"] + max(1.7, outcome_d + 0.45)
        if run["broken"] or ev["type"] == "flip":
            c = run["broken"]["t"] if run["broken"] else ev["t"]
            L["replay"] = (max(0.0, c - 0.75), min(tmax, c + 0.6))
        else:
            L["replay"] = None
    L["live_end"] = max(L["live_end"], intro_d + 0.5)
    L["bullet"] = bullet_window(L)
    L["frames"] = build_frames(L)
    # the outcome line may be delayed by the intro: make sure it ends before the replay / outro
    ev_out = out_time(L, ev["t"])
    need = outcome_vo_t(ev_out, intro_d) + outcome_d + (0.3 if ev["type"] == "win" else 0.45)
    have = out_time(L, L["outro_t"]) if ev["type"] == "win" else sum(1 for f in L["frames"] if f[1] == "live") / FPS
    if need > have:                                  # after the event playback is 1:1, so shift in sim time
        if ev["type"] == "win":
            L["outro_t"] += need - have
        L["live_end"] = min(tmax, L["live_end"] + need - have)
        L["frames"] = build_frames(L)
    L["dur"] = len(L["frames"]) / FPS
    return L


def pick_combo(rng, timed):
    """Choose one run per level so the whole video hits the pacing window (BLUEPRINT 4.5)."""
    scored = []
    PICK_STATS.update(combos=0, total_ok=0, len_ok=0, spect_ok=0)
    for combo in itertools.product(*[range(len(c)) for c in timed]):
        PICK_STATS["combos"] += 1
        Ls = [timed[li][ci] for li, ci in enumerate(combo)]
        total = sum(L["dur"] for L in Ls)
        if not TARGET_TOTAL[0] <= total <= TARGET_TOTAL[1]:
            continue
        PICK_STATS["total_ok"] += 1
        if any(L["dur"] > level_cap(L) for L in Ls):
            continue
        PICK_STATS["len_ok"] += 1
        fails = [L for L in Ls if L["event"]["type"] != "win"]
        spect = sum(1 for L in fails if is_spectacular(L))
        crash = sum(1 for L in fails if L["broken"] or L["event"]["type"] == "flip")
        if spect == 0:
            continue
        PICK_STATS["spect_ok"] += 1
        distinct = len({L["event"]["obstacle"] for L in fails}) == len(fails)
        score = 2.0 * distinct + 1.0 * (spect - 1) + 1.5 * min(crash, 1) - 0.3 * abs(total - 46.0)
        scored.append((score, combo))
    if not scored:
        return None
    top = max(s for s, _ in scored)
    pool = [c for s, c in scored if s >= top - 0.5]
    return pool[rng.integers(len(pool))]


# ================================================================ timeline helpers
def interp(arr, st):
    f = st * REC_HZ
    i = int(f)
    if i >= len(arr) - 1:
        return arr[-1]
    a = f - i
    return arr[i] * (1 - a) + arr[i + 1] * a


def car_state(L, st):
    rec = L["rec"]
    return dict(cx=float(interp(rec["cx"], st)), cy=float(interp(rec["cy"], st)), ca=float(interp(rec["ca"], st)),
                wheels=interp(rec["wheels"], st), speed=float(interp(rec["speed"], st)),
                air=float(interp(rec["air"], st)))


def bullet_window(L):
    """Longest high airborne span before the outcome (for bullet-time)."""
    rec, ev, v = L["rec"], L["event"], L["v"]
    lift = v["body"][1] / 2 + v["wheel_r"] + 0.8
    n = min(int(ev["t"] * REC_HZ), len(rec["cx"]))
    spans, start = [], None
    for i in range(n):
        high = rec["air"][i] > 0.5 and rec["cy"][i] - ground_h(rec["cx"][i]) > lift
        if high and start is None:
            start = i
        elif not high and start is not None:
            spans.append((start, i - 1))
            start = None
    if start is not None:
        spans.append((start, n - 1))
    if not spans:
        return None
    a, b = max(spans, key=lambda s: s[1] - s[0])
    if b - a < 0.3 * REC_HZ:
        return None
    return a / REC_HZ, b / REC_HZ


def build_frames(L):
    ev, tmax = L["event"], (len(L["rec"]["cx"]) - 1) / REC_HZ
    bw = L["bullet"]
    frames, t = [], 0.0
    live_end = min(L["live_end"], tmax)
    while t < live_end:
        frames.append((t, "live"))
        rate = 1.0
        if bw:
            w = min(t - (bw[0] - 0.15), (bw[1] + 0.1) - t) / 0.2
            rate = 1.0 - (1.0 - BULLET_RATE) * min(1.0, max(0.0, w))
        t += rate / FPS
    if L["replay"]:
        ta, tb = L["replay"]
        L["replay_out"] = len(frames) / FPS
        t = ta
        while t < tb:
            frames.append((t, "replay"))
            t += REPLAY_SPEED / FPS
    return frames


def out_time(L, st):
    for j, (t, mode) in enumerate(L["frames"]):
        if mode == "live" and t >= st:
            return j / FPS
    return len(L["frames"]) / FPS


def camera_track(L):
    v = L["v"]
    cams, prev_mode = [], None
    cx = cy = z = 0.0
    for j, (st, mode) in enumerate(L["frames"]):
        s = car_state(L, st)
        if mode == "live":
            tz = v["zoom"] * (0.84 if s["air"] > 0.5 else 1.0)
            tx = s["cx"] + 3.0 / tz
            ty = float(np.clip(s["cy"] - 1.5, -4.5, 4.0)) * 0.8
            k = 0.18
        else:
            tz = v["zoom"] * 1.45
            tx = s["cx"] + 0.6
            ty = float(np.clip(s["cy"] - 0.8, -4.5, 4.0)) * 0.9
            k = 0.25
        if mode != prev_mode:
            cx, cy, z = tx, ty, tz
        else:
            cx += (tx - cx) * k
            cy += (ty - cy) * 0.12
            z += (tz - z) * 0.08
        cams.append((cx, cy, z))
        prev_mode = mode
    return cams


def mood_at(L, st, s):
    ev = L["event"]
    if st >= ev["t"]:
        return "happy" if ev["type"] == "win" else "dizzy"
    lift = L["v"]["body"][1] / 2 + L["v"]["wheel_r"]
    # "whoa" only for real jumps: airborne AND still above road level (not nose-diving into a pit)
    if s["air"] > 0.5 and s["cy"] > lift and s["cy"] - ground_h(s["cx"]) > lift + 0.5:
        return "whoa"
    front = s["cx"] + L["v"]["body"][0] / 2 * math.cos(s["ca"])
    if any(0 < dx - front < 6.5 for dx in DANGER_X):
        return "scared"
    return "normal"


def find_bubbles(L):
    ev = L["event"]
    out, seen = [], set()
    t = 0.0
    while t < ev["t"]:
        m = mood_at(L, t, car_state(L, t))
        if m == "scared" and "scared" not in seen:
            out.append((t, "UH OH!"))
            seen.add("scared")
        if m == "whoa" and "whoa" not in seen:
            out.append((t + 0.1, "WHOA!"))
            seen.add("whoa")
        t += 1 / 30
    if ev["type"] == "win":
        out.append((ev["t"] + 0.2, "YEAH!"))
    else:
        out.append(((L["broken"]["t"] if L["broken"] else ev["t"]) + 0.05, "OUCH!"))
    return out


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


def stretch(sig, factor):
    n = int(len(sig) / factor)
    return np.interp(np.arange(n) * factor, np.arange(len(sig)), sig)


def synth_engine(wrel, amp, pitch, base, k, seed):
    n = int(len(wrel) * SR / FPS)
    f = per_sample((base + k * np.minimum(wrel, 60)) * pitch, n)
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


def synth_shatter(seed=9):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n)
    sig = (x - smooth(x, 4)) * np.exp(-t / 0.15) * 0.8
    for _ in range(14):
        p = tone(rng.uniform(2500, 6000), 0.1, "sine", decay=0.05) * 0.4
        i0 = int(rng.uniform(0, 0.5) * SR)
        sig[i0:i0 + len(p)] += p
    return sig


def sweep(f0, f1, dur, vol=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = np.linspace(f0, f1, n)
    env = np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env * vol


def synth_tweets():
    out = np.zeros(int(0.6 * SR))
    for i in range(3):
        p = sweep(2600, 3400, 0.09, 0.5)
        i0 = int(i * 0.16 * SR)
        out[i0:i0 + len(p)] += p
    return out


def synth_rewind():
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    x = np.random.default_rng(4).standard_normal(n)
    band = (smooth(x, 3) - smooth(x, 20)) * (t / 0.55) ** 1.5
    return band + sweep(1200, 200, 0.55, 0.4)


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


def star(ctx, x, y, r, rot=0.0):
    pts = []
    for i in range(10):
        a = rot + math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    poly(ctx, pts)


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


def draw_sky(ctx, camx, camy, z):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.36, 0.7, 1.0)
    g.add_color_stop_rgb(0.6, 0.72, 0.9, 1.0)
    g.add_color_stop_rgb(1, 0.85, 0.95, 1.0)
    ctx.set_source(g)
    ctx.paint()
    rg = cairo.RadialGradient(900, 520, 40, 900, 520, 190)
    rg.add_color_stop_rgba(0, 1, 0.95, 0.55, 0.9)
    rg.add_color_stop_rgba(1, 1, 0.95, 0.55, 0)
    ctx.set_source(rg)
    ctx.arc(900, 520, 190, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(1, 0.9, 0.35)
    ctx.arc(900, 520, 70, 0, 2 * math.pi)
    ctx.fill()
    for i in range(7):
        x = (i * 430 - camx * S * 0.12) % (W + 700) - 350
        y = 600 + (i % 3) * 110 + camy * S * 0.1
        ctx.set_source_rgba(1, 1, 1, 0.92)
        for dx, dy, r in [(0, 0, 55), (60, -25, 65), (125, 0, 50), (60, 15, 55)]:
            ctx.arc(x + dx, y + dy, r, 0, 2 * math.pi)
            ctx.fill()
    ground_sy = GROUND_Y + camy * S * z
    for par, base, col, a1, a2 in [(0.2, -260, (0.56, 0.8, 0.52), 90, 45),
                                   (0.45, -150, (0.42, 0.72, 0.38), 70, 35)]:
        ctx.new_path()
        ctx.move_to(0, H)
        for sx in range(0, W + 21, 20):
            wx = sx + camx * S * par
            y = ground_sy + base * z - camy * S * (1 - par) * 0.5 - a1 * math.sin(wx / 260) - a2 * math.sin(wx / 113 + 1)
            ctx.line_to(sx, y)
        ctx.line_to(W, H)
        ctx.close_path()
        ctx.set_source_rgb(*col)
        ctx.fill()


def draw_track(ctx, view0, view1):
    for x0, x1, d in PITS:
        ctx.rectangle(x0, -d, x1 - x0, d)
        ctx.set_source_rgb(0.28, 0.17, 0.1)
        ctx.fill()
    poly(ctx, TRACK + [(170, -40), (-40, -40)])
    ctx.set_source_rgb(0.58, 0.38, 0.22)
    ctx.fill()
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
    for x0, x1, d in PITS:
        ctx.rectangle(x0, -d, x1 - x0, 0.55)
        ctx.set_source_rgb(0.4, 0.26, 0.13)
        ctx.fill()
        for j in range(int((x1 - x0) / 0.8)):
            ctx.arc(x0 + 0.4 + j * 0.8, -d + 0.55, 0.22, 0, math.pi)
            ctx.fill()
    for a, b in zip(TRACK, TRACK[1:]):
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
    for x0, x1, d in PITS:
        for xe, sgn in [(x0, -1), (x1, 1)]:
            if RAMP and abs(xe - RAMP[1]) < 1e-6:
                continue
            poly(ctx, [(xe, 0), (xe, -0.55), (xe + sgn * 0.25, -0.35), (xe + sgn * 0.12, -0.2),
                       (xe + sgn * 0.3, 0)])
            ctx.set_source_rgb(0.28, 0.17, 0.1)
            ctx.fill()
    if RAMP:
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
    for x0, x1, h in BUMPS:                      # yellow/black striped speed bumps
        if x1 < view0 - 1 or x0 > view1 + 1:
            continue
        pts = [(x0 + (x1 - x0) * k / 24, h * math.sin(math.pi * k / 24)) for k in range(25)]
        poly(ctx, pts + [(x1, -0.55), (x0, -0.55)])
        ctx.save()
        ctx.clip_preserve()
        ctx.set_source_rgb(1, 0.8, 0.1)
        ctx.fill_preserve()
        ctx.new_path()
        ctx.set_source_rgb(0.12, 0.12, 0.14)
        sx = x0 - h - 1
        while sx < x1 + 1:
            poly(ctx, [(sx, -0.6), (sx + 0.35, -0.6), (sx + 0.35 + h + 0.6, h + 0.1), (sx + h + 0.6, h + 0.1)])
            ctx.fill()
            sx += 0.8
        ctx.restore()
        poly(ctx, pts + [(x1, -0.55), (x0, -0.55)])
        ctx.set_source_rgb(0.1, 0.08, 0.12)
        ctx.set_line_width(0.07)
        ctx.stroke()
    for x in SIGNS:
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


# ---------------------------------------------------------------- faces
def draw_face(ctx, vk, mood, t):
    f = FACES[vk]
    r = f["r"]
    ink = (0.05, 0.05, 0.1)
    big = {"scared": 1.25, "whoa": 1.45}.get(mood, 1.0)
    for n, (ex, ey) in enumerate(f["eyes"]):
        if mood == "happy":
            ctx.new_path()
            ctx.arc(ex, ey - r * 0.2, r * 0.75, 0.15 * math.pi, 0.85 * math.pi)
            ctx.set_source_rgb(*ink)
            ctx.set_line_width(r * 0.4)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
            continue
        rr = r * big
        ctx.save()
        ctx.translate(ex, ey)
        ctx.scale(1, 1.25)
        ctx.arc(0, 0, rr, 0, 2 * math.pi)
        ctx.restore()
        fill_stroke(ctx, (1, 1, 1), lw=r * 0.25)
        ctx.set_source_rgb(*ink)
        if mood == "dizzy":
            ctx.set_line_width(r * 0.35)
            for s in (1, -1):
                ctx.move_to(ex - r * 0.6, ey - s * r * 0.6)
                ctx.line_to(ex + r * 0.6, ey + s * r * 0.6)
                ctx.stroke()
        else:
            pr = {"scared": 0.25, "whoa": 0.38}.get(mood, 0.5)
            px = {"scared": 0.2, "whoa": 0.0}.get(mood, 0.35)
            ctx.arc(ex + rr * px, ey + rr * 0.1, rr * pr, 0, 2 * math.pi)
            ctx.fill()
            ctx.set_source_rgb(1, 1, 1)
            ctx.arc(ex + rr * px + rr * pr * 0.35, ey + rr * 0.1 + rr * pr * 0.35, rr * pr * 0.32, 0, 2 * math.pi)
            ctx.fill()
        if mood in ("scared", "whoa"):
            lift = 1.75 if mood == "whoa" else 1.55
            tilt = (0.25 if n == 0 else -0.25) if mood == "scared" else 0.0
            ctx.set_source_rgb(*ink)
            ctx.set_line_width(r * 0.3)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(ex - r * 0.8, ey + r * lift - tilt * r)
            ctx.line_to(ex + r * 0.8, ey + r * lift + tilt * r)
            ctx.stroke()
    if mood == "scared":
        ex, ey = f["eyes"][0]
        bob = 0.05 * math.sin(t * 12)
        dx, dy = ex - r * 2.4, ey + r * 0.9 + bob
        ctx.new_path()
        ctx.move_to(dx, dy + r * 0.9)
        ctx.curve_to(dx + r * 0.6, dy, dx + r * 0.5, dy - r * 0.6, dx, dy - r * 0.6)
        ctx.curve_to(dx - r * 0.5, dy - r * 0.6, dx - r * 0.6, dy, dx, dy + r * 0.9)
        fill_stroke(ctx, (0.45, 0.8, 1.0), stroke=(0.1, 0.35, 0.7), lw=r * 0.15)
    mx, my = f["mouth"]
    mw = f["mw"]
    ctx.set_source_rgb(*ink)
    ctx.set_line_width(mw * 0.16)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if mood == "normal":
        ctx.new_path()
        ctx.arc(mx, my + mw * 0.3, mw * 0.5, 1.2 * math.pi, 1.8 * math.pi)
        ctx.stroke()
    elif mood == "scared":
        rrect(ctx, mx - mw / 2, my - mw * 0.22, mw, mw * 0.44, mw * 0.15)
        fill_stroke(ctx, (1, 1, 1), lw=mw * 0.1)
        ctx.set_source_rgb(*ink)
        ctx.set_line_width(mw * 0.05)
        for k in range(1, 4):
            x = mx - mw / 2 + mw * k / 4
            ctx.move_to(x, my - mw * 0.22)
            ctx.line_to(x, my + mw * 0.22)
            ctx.stroke()
        ctx.move_to(mx - mw / 2, my)
        ctx.line_to(mx + mw / 2, my)
        ctx.stroke()
    elif mood == "whoa":
        ctx.save()
        ctx.translate(mx, my)
        ctx.scale(0.8, 1.0)
        ctx.arc(0, 0, mw * 0.32, 0, 2 * math.pi)
        ctx.restore()
        fill_stroke(ctx, (0.45, 0.05, 0.1), lw=mw * 0.1)
    elif mood == "happy":
        ctx.new_path()
        ctx.move_to(mx - mw / 2, my + mw * 0.1)
        ctx.line_to(mx + mw / 2, my + mw * 0.1)
        ctx.arc_negative(mx, my + mw * 0.1, mw / 2, 0, math.pi)
        ctx.close_path()
        fill_stroke(ctx, (0.45, 0.05, 0.1), lw=mw * 0.1)
        ctx.arc(mx, my - mw * 0.22, mw * 0.18, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 0.45, 0.5)
        ctx.fill()
    else:
        ctx.new_path()
        ctx.move_to(mx - mw / 2, my)
        for k in range(1, 7):
            ctx.line_to(mx - mw / 2 + mw * k / 6, my + (mw * 0.12 if k % 2 else -mw * 0.12))
        ctx.stroke()


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


def draw_body(ctx, vk, v, broken, t=0.0):
    c = v["color"]
    dark = shade(c, 0.65)
    glass = (0.62, 0.86, 1.0)
    flash = int(t * 6) % 2 == 0
    if vk == "police":
        poly(ctx, [(-1.4, 0.35), (0.7, 0.35), (0.2, 0.95), (-1.2, 0.95)])
        fill_stroke(ctx, c)
        poly(ctx, [(-1.25, 0.4), (0.52, 0.4), (0.12, 0.86), (-1.08, 0.86)])
        fill_stroke(ctx, glass, lw=0.03)
        ctx.set_source_rgb(0.1, 0.08, 0.12)
        ctx.set_line_width(0.05)
        ctx.move_to(-0.35, 0.4)
        ctx.line_to(-0.35, 0.86)
        ctx.stroke()
        poly(ctx, [(-2.2, -0.35), (2.2, -0.35), (2.2, 0.0), (1.8, 0.3), (0.8, 0.35), (-2.1, 0.35), (-2.2, 0.15)])
        fill_stroke(ctx, c)
        poly(ctx, [(-1.0, -0.35), (0.9, -0.35), (0.9, 0.3), (-1.0, 0.33)])
        fill_stroke(ctx, (0.1, 0.12, 0.2), lw=0.04)
        local_text(ctx, "POLICE", -0.05, -0.02, 0.26, (1, 1, 1))
        for k, (x0, col_on) in enumerate([(-0.75, (1, 0.15, 0.15)), (-0.35, (0.15, 0.4, 1))]):
            lit = flash if k == 0 else not flash
            rrect(ctx, x0, 0.95, 0.38, 0.16, 0.05)
            fill_stroke(ctx, col_on if lit else shade(col_on, 0.45), lw=0.03)
        ctx.arc(2.05, 0.05, 0.09, 0, 2 * math.pi)
        fill_stroke(ctx, (1, 0.95, 0.4), lw=0.03)
    elif vk == "firetruck":
        rrect(ctx, -3.2, -0.95, 6.4, 1.9, 0.2)
        fill_stroke(ctx, c, lw=0.08)
        rrect(ctx, 1.95, -0.1, 1.05, 0.8, 0.12)
        fill_stroke(ctx, glass, lw=0.05)
        ctx.rectangle(-3.2, -0.45, 6.4, 0.16)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        for i in range(4):
            rrect(ctx, -2.9 + i * 1.15, -0.25, 0.95, 0.75, 0.08)
            fill_stroke(ctx, shade(c, 0.8), lw=0.04)
        ctx.set_source_rgb(0.75, 0.75, 0.8)
        ctx.set_line_width(0.07)
        for y in (1.02, 1.28):
            ctx.move_to(-3.0, y)
            ctx.line_to(1.4, y)
            ctx.stroke()
        for i in range(12):
            x = -2.9 + i * 0.37
            ctx.move_to(x, 1.02)
            ctx.line_to(x, 1.28)
            ctx.stroke()
        rrect(ctx, 2.1, 0.95, 0.6, 0.18, 0.05)
        fill_stroke(ctx, (1, 0.15, 0.15) if flash else (0.5, 0.08, 0.08), lw=0.03)
        local_text(ctx, "FIRE", -0.9, -0.72, 0.32, (1, 1, 1))
        ctx.arc(3.05, -0.4, 0.11, 0, 2 * math.pi)
        fill_stroke(ctx, (1, 0.95, 0.4), lw=0.03)
    elif vk == "sports":
        poly(ctx, [(-1.3, 0.31), (0.5, 0.31), (-0.1, 0.85), (-1.0, 0.85)])
        fill_stroke(ctx, c)
        poly(ctx, [(-1.15, 0.36), (0.32, 0.36), (-0.15, 0.76), (-0.95, 0.76)])
        fill_stroke(ctx, glass, lw=0.03)
        poly(ctx, [(-2.1, -0.31), (2.1, -0.31), (2.1, -0.05), (1.6, 0.2), (0.6, 0.31), (-2.0, 0.31), (-2.1, 0.1)])
        fill_stroke(ctx, c)
        ctx.rectangle(-1.9, -0.06, 3.1, 0.1)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        poly(ctx, [(-2.05, 0.31), (-1.85, 0.31), (-1.9, 0.52), (-2.05, 0.52)])
        fill_stroke(ctx, dark, lw=0.04)
        poly(ctx, [(-2.35, 0.5), (-1.65, 0.5), (-1.65, 0.6), (-2.35, 0.6)])
        fill_stroke(ctx, dark, lw=0.04)
        ctx.arc(1.95, 0.02, 0.09, 0, 2 * math.pi)
        fill_stroke(ctx, (1, 0.95, 0.4), lw=0.03)
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
        local_text(ctx, "SCHOOL BUS", -0.7, -0.7, 0.42, (0.1, 0.1, 0.1))
        ctx.rectangle(3.62, -1.0, 0.18, 0.35)
        ctx.rectangle(-3.8, -1.0, 0.18, 0.35)
        ctx.set_source_rgb(0.15, 0.15, 0.15)
        ctx.fill()
        ctx.arc(3.55, -0.35, 0.11, 0, 2 * math.pi)
        fill_stroke(ctx, (1, 0.95, 0.4), lw=0.03)
    else:
        poly(ctx, [(-1.5, 0.45), (0.4, 0.45), (0.0, 1.35), (-1.3, 1.35)])
        fill_stroke(ctx, c, lw=0.07)
        poly(ctx, [(-1.35, 0.52), (0.22, 0.52), (-0.08, 1.25), (-1.2, 1.25)])
        fill_stroke(ctx, glass, lw=0.04)
        poly(ctx, [(-2.15, -0.45), (2.15, -0.45), (2.15, 0.2), (1.9, 0.45), (-2.15, 0.45)])
        fill_stroke(ctx, c, lw=0.07)
        poly(ctx, [(-0.3, -0.25), (0.6, -0.3), (0.3, -0.1), (1.3, -0.05), (0.5, 0.1), (1.0, 0.3), (-0.3, 0.2)])
        fill_stroke(ctx, (1, 0.6, 0.1), stroke=(0.9, 0.2, 0.1), lw=0.04)
        for i in range(3):
            ctx.rectangle(-1.2 + i * 0.35, 1.35, 0.25, 0.14)
            ctx.set_source_rgb(1, 0.85, 0.2)
            ctx.fill()
        ctx.arc(2.02, 0.08, 0.1, 0, 2 * math.pi)
        fill_stroke(ctx, (1, 0.95, 0.4), lw=0.03)
    if broken:
        bw, bh = v["body"]
        ctx.set_source_rgb(0.1, 0.08, 0.12)
        ctx.set_line_width(0.04)
        for sx, sy, pts in [(-bw * 0.2, 0.0, [(0.2, 0.15), (0.35, -0.05), (0.55, 0.12)]),
                            (bw * 0.18, -bh * 0.15, [(0.15, -0.12), (0.3, 0.05), (0.5, -0.1)])]:
            ctx.move_to(sx, sy)
            for px, py in pts:
                ctx.line_to(sx + px, sy + py)
            ctx.stroke()


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


def draw_shadow(ctx, L, s):
    v = L["v"]
    gh = ground_h(s["cx"])
    h = max(0.0, s["cy"] - v["body"][1] / 2 - v["wheel_r"] - gh)
    a = 0.3 * max(0.0, 1 - h / 5)
    if a <= 0.01:
        return
    ctx.save()
    ctx.translate(s["cx"], gh + 0.02)
    ctx.scale(v["body"][0] * 0.55 * (1 + h * 0.08), 0.18)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(0, 0, 0, a)
    ctx.fill()


def draw_car(ctx, L, s, mood, st):
    vk, v = L["vk"], L["v"]
    cx, cy, ca, wheels = s["cx"], s["cy"], s["ca"], s["wheels"]
    bh = v["body"][1]
    si = st * REC_HZ
    ctx.set_source_rgb(0.3, 0.3, 0.34)
    ctx.set_line_width(0.14)
    for wi, ((wx, wy, _), lx) in enumerate(zip(wheels, v["wheel_x"])):
        det = L["detached"][wi]
        if det is not None and si >= det:
            continue
        ax = cx + math.cos(ca) * lx - math.sin(ca) * (-bh / 2)
        ay = cy + math.sin(ca) * lx + math.cos(ca) * (-bh / 2)
        ctx.move_to(ax, ay)
        ctx.line_to(wx, wy)
        ctx.stroke()
    for wx, wy, wa in wheels:
        draw_wheel(ctx, wx, wy, wa, v["wheel_r"], vk.startswith("monster"))
    broken = L["broken"] is not None and st >= L["broken"]["t"]
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(ca)
    draw_body(ctx, vk, v, broken, st)
    draw_face(ctx, vk, mood, st)
    ctx.restore()


def draw_debris(ctx, L, st):
    if not L["debris_meta"]:
        return
    stt = interp(L["debris"], st)
    for d, (x, y, a) in zip(L["debris_meta"], stt):
        if math.isnan(x):
            continue
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(a)
        if d["kind"] == "hubcap":
            ctx.arc(0, 0, d["size"], 0, 2 * math.pi)
            fill_stroke(ctx, d["color"], lw=0.03)
        else:
            poly(ctx, d["verts"])
            fill_stroke(ctx, d["color"], lw=0.03)
        ctx.restore()


def draw_effects(ctx, L, s, st):
    b = L["broken"]
    if b is not None and st >= b["t"]:
        age = st - b["t"]
        if age < 0.6:                      # sparks
            rng = np.random.default_rng(31)
            for _ in range(22):
                vx, vy = rng.uniform(-7, 7), rng.uniform(2, 9)
                x = b["x"] + vx * age
                y = b["y"] + vy * age - 4.9 * age * age
                ctx.move_to(x, y)
                ctx.line_to(x - vx * 0.035, y - (vy - 9.8 * age) * 0.035)
                ctx.set_source_rgba(1, 0.75 + rng.uniform(0, 0.25), 0.2, 1 - age / 0.6)
                ctx.set_line_width(0.07)
                ctx.stroke()
        k = 0                              # smoke puffs from the wreck
        while True:
            ts = b["t"] + k * 0.18
            if ts > st:
                break
            pa = st - ts
            if pa < 1.8:
                p = car_state(L, ts)
                x = p["cx"] + 0.3 * pa + 0.2 * math.sin(k * 1.7)
                y = p["cy"] + 0.4 + 1.3 * pa
                ctx.arc(x, y, 0.25 + 0.45 * pa, 0, 2 * math.pi)
                ctx.set_source_rgba(0.55, 0.55, 0.58, 0.5 * (1 - pa / 1.8))
                ctx.fill()
            k += 1
    ev = L["event"]
    if ev["type"] != "win" and st >= ev["t"] + 0.4:   # dizzy stars
        top = s["cy"] + L["v"]["body"][1] / 2 + 1.0
        for k in range(3):
            a = st * 4 + k * 2 * math.pi / 3
            star(ctx, s["cx"] + math.cos(a) * 0.9, top + math.sin(a) * 0.22, 0.2, a)
            fill_stroke(ctx, (1, 0.88, 0.2), lw=0.03)


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


def shake_offset(L, st):
    dx = dy = 0.0
    for ti, s, _, _ in L["impacts"]:
        a = st - ti
        if 0 <= a < 0.6:
            amp = 26 * s * math.exp(-a / 0.18)
            dx += amp * math.sin(a * 83 + ti)
            dy += amp * math.cos(a * 71 + ti * 2)
    return dx, dy


# ================================================================ HUD / screen-space effects
def draw_speed_lines(ctx, speed, tl):
    if speed < 12:
        return
    a = min(0.55, (speed - 12) / 12)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(16):
        y = 700 + (i * 97) % 650
        ln = 120 + (i * 53) % 110
        x = W + 200 - ((tl * 2600 + i * 383) % (W + 500))
        ctx.move_to(x, y)
        ctx.line_to(x + ln, y)
        ctx.set_source_rgba(1, 1, 1, a)
        ctx.set_line_width(5)
        ctx.stroke()


def draw_bubbles(ctx, L, st, sx, sy, z):
    for bt, text in L["bubbles"]:
        age = st - bt
        if not 0 <= age < 1.1:
            continue
        s = ease_out_back(age / 0.2)
        bx = min(880, max(200, sx + 130))
        by = min(1250, max(930, sy - 190 * z - 40))
        ctx.save()
        ctx.translate(bx, by)
        ctx.scale(s, s)
        set_font(ctx, 62)
        w = ctx.text_extents(text).width + 70
        poly(ctx, [(-w * 0.25, 40), (-w * 0.25 - 40, 105), (-w * 0.05, 40)])
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.1, 0.1, 0.25)
        ctx.set_line_width(6)
        ctx.stroke()
        rrect(ctx, -w / 2, -55, w, 110, 40)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.1, 0.1, 0.25)
        ctx.set_line_width(6)
        ctx.stroke()
        draw_text(ctx, text, 0, 0, 62, fill=(0.9, 0.15, 0.2), stroke=(1, 1, 1), sw=2)
        ctx.restore()


def draw_replay_overlay(ctx, tl):
    rg = cairo.RadialGradient(540, 1000, 350, 540, 1000, 1150)
    rg.add_color_stop_rgba(0, 0, 0, 0, 0)
    rg.add_color_stop_rgba(1, 0, 0, 0.1, 0.5)
    ctx.set_source(rg)
    ctx.paint()
    rrect(ctx, 250, 600, 580, 90, 45)
    ctx.set_source_rgba(0.05, 0.05, 0.15, 0.8)
    ctx.fill()
    if int(tl * 2.5) % 2 == 0:
        ctx.arc(300, 645, 16, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 0.15, 0.2)
        ctx.fill()
    draw_text(ctx, "INSTANT REPLAY", 560, 645, 50, fill=(1, 1, 1), stroke=(0.05, 0.05, 0.15), sw=4)


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


def draw_hud(ctx, L, li, st, tl, gt, mode, car_x):
    ts = 1.0 + 0.25 * (1 - ease_out_back(gt / 0.5)) if gt < 0.5 else 1.0
    ctx.save()
    ctx.translate(540, 215)
    ctx.scale(ts, ts)
    draw_text(ctx, TITLE, 0, 0, 84, fill=(1, 0.86, 0.12), max_w=980)
    ctx.restore()
    s = ease_out_back(tl / 0.35)
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
    draw_text(ctx, L["v"]["display"], 540, 440, 56, max_w=950, alpha=min(1.0, tl / 0.3))
    if li == 0 and gt < 2.6:
        pulse = 1 + 0.06 * math.sin(gt * 9)
        ctx.save()
        ctx.translate(540, 640)
        ctx.scale(pulse, pulse)
        draw_text(ctx, "WHO WILL MAKE IT?", 0, 0, 70, fill=(1, 1, 1), stroke=(0.85, 0.1, 0.2),
                  alpha=min(1.0, (2.6 - gt) / 0.3))
        ctx.restore()
    frac = min(1.0, max(0.0, (car_x - START_X) / (FINISH_X - START_X)))
    x0, x1, y = 110, 960, 540
    rrect(ctx, x0 - 10, y - 18, x1 - x0 + 20, 36, 18)
    ctx.set_source_rgba(0.05, 0.05, 0.15, 0.55)
    ctx.fill()
    rrect(ctx, x0, y - 9, max(18, (x1 - x0) * frac), 18, 9)
    ctx.set_source_rgb(*col)
    ctx.fill()
    for oc, _ in OBSTACLES:
        px = x0 + (x1 - x0) * (oc - START_X) / (FINISH_X - START_X)
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
    if mode != "live":
        return
    ev = L["event"]
    badge_t = ev["t"] - 0.2
    outro_t = L.get("outro_t")
    if ev["type"] == "win" and st >= ev["t"]:
        draw_confetti(ctx, st - ev["t"])
    if st >= badge_t and (outro_t is None or st < outro_t + 0.3):
        ctx.push_group()
        draw_badge(ctx, "win" if ev["type"] == "win" else "fail", st - badge_t)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1.0 if outro_t is None else max(0.0, min(1.0, (outro_t + 0.3 - st) / 0.3)))
    if outro_t is not None and st >= outro_t:
        a = st - outro_t
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


# ================================================================ analysis gate (BLUEPRINT.md section 5.1)
def check(cid, desc, ok, detail="", hard=True):
    return dict(id=cid, desc=desc, ok=bool(ok), detail=str(detail), hard=hard)


def analyze(intro_durs):
    res = []
    xs = [(L["rec"]["cx"][0], L["rec"]["cx"][-1]) for L in LEVELS]
    res.append(check("forward", "Semua mobil bergerak maju ke kanan (+x)", all(b > a + 5 for a, b in xs),
                     ", ".join(f"{a:.1f}->{b:.1f} m" for a, b in xs)))
    spans = PITS or BUMPS
    ok_obs = len(spans) >= 2 and all(START_X < x0 < x1 < FINISH_X for x0, x1, _ in spans)
    kind = "lubang" if PITS else "polisi tidur"
    res.append(check("obstacles", "Minimal 2 rintangan di antara start dan finish", ok_obs,
                     f"{len(spans)} {kind} ({spans[0][0]:.0f}-{spans[-1][1]:.0f} m), finish {FINISH_X:.0f} m"
                     if spans else "tidak ada rintangan"))
    got = ["win" if L["event"]["type"] == "win" else "fail" for L in LEVELS]
    want = [w for _, w in STORY]
    res.append(check("story", "Pola cerita sesuai STORY", got == want, f"{got} (target {want})"))
    res.append(check("no_timeout", "Tidak ada timeout", all(L["event"]["type"] != "timeout" for L in LEVELS)))
    tm = [event_min_t(idur) <= L["event"]["t"] <= (15.0 if L["event"]["type"] == "win" else 11.5)
          for L, idur in zip(LEVELS, intro_durs)]
    res.append(check("timing", "Waktu event masuk akal", all(tm), ", ".join(f"{L['event']['t']:.1f}s" for L in LEVELS)))
    fails = [L["event"]["obstacle"] for L in LEVELS if L["event"]["type"] != "win"]
    res.append(check("distinct_fail", "Level gagal di rintangan berbeda", len(set(fails)) == len(fails),
                     f"rintangan {fails}", hard=False))
    res.append(check("spectacular", "Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time)",
                     any(is_spectacular(L) for L in LEVELS if L["event"]["type"] != "win")))
    total = sum(L["dur"] for L in LEVELS)
    res.append(check("duration", "Durasi total 40-50 s", 40 <= total <= 50, f"{total:.1f} s"))
    lens_ok = all(L["dur"] <= level_cap(L) for L in LEVELS)
    d = SERIES_DEFS[SERIES]
    res.append(check("level_len", f"Level gagal <= {d['max_fail']:.0f} s, level menang (+outro) <= {d['max_win']:.0f} s",
                     lens_ok,
                     ", ".join(f"{L['dur']:.1f}s" for L in LEVELS)))
    return res


def outcome_tags():
    return [("win" if L["event"]["type"] == "win" else
             f"{L['event']['type']}@obs{L['event']['obstacle']}" + ("+broken" if L["broken"] else ""))
            for L in LEVELS]


# ================================================================ frames
LEVELS = []
INDEX = []          # global frame -> (level, local output frame)


def draw_frame(ctx, g):
    li, j = INDEX[g]
    L = LEVELS[li]
    st, mode = L["frames"][j]
    tl = j / FPS
    camx, camy, z = L["cam"][j]
    shx, shy = shake_offset(L, st)
    s = car_state(L, st)
    draw_sky(ctx, camx, camy, z)
    ctx.save()
    ctx.translate(540 + shx, GROUND_Y + shy)
    ctx.scale(S * z, -S * z)
    ctx.translate(-camx, -camy)
    half = 540 / (S * z) + 2
    draw_track(ctx, camx - half, camx + half)
    draw_shadow(ctx, L, s)
    draw_dust(ctx, L["impacts"], st)
    draw_debris(ctx, L, st)
    draw_car(ctx, L, s, mood_at(L, st, s), st)
    draw_effects(ctx, L, s, st)
    ctx.restore()
    if mode == "live" and s["air"] < 0.5:
        draw_speed_lines(ctx, s["speed"], tl)
    car_sx = 540 + shx + (s["cx"] - camx) * S * z
    car_sy = GROUND_Y + shy - (s["cy"] - camy) * S * z
    draw_bubbles(ctx, L, st, car_sx, car_sy, z)
    if mode == "replay":
        draw_replay_overlay(ctx, tl)
    draw_hud(ctx, L, li, st, tl, g / FPS, mode, s["cx"])


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
    global FPS
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--series", default="auto", choices=["auto"] + list(SERIES_DEFS),
                    help="auto = the series with the fewest videos in the registry")
    ap.add_argument("--fps", type=int, default=30, choices=[30, 60])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--name", default=None, help="output video id (default SIM_POTHOLES_S<seed>)")
    ap.add_argument("--preview-only", action="store_true", help="analysis + PNG previews, no MP4, no registry")
    ap.add_argument("--force", action="store_true", help="allow re-using a seed / overwriting a video")
    ap.add_argument("--allow-duplicate", action="store_true", help="allow a fingerprint already in the registry")
    args = ap.parse_args()
    FPS = args.fps
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    import registry
    detect_font()
    load_cast()
    active = [e for e in registry.load()["videos"] if e.get("status") not in registry.IGNORED_STATUS]
    series = args.series
    if series == "auto":
        counts = {s: 0 for s in SERIES_DEFS}
        for e in active:
            if e.get("engine_version") == ENGINE_VERSION and e["series"] in counts:
                counts[e["series"]] += 1
        series = min(SERIES_DEFS, key=lambda s: counts[s])
    appearances = {}
    for e in active:
        for vk in e.get("vehicles", []):
            appearances[vk] = appearances.get(vk, 0) + 1
    make_track(series, args.seed)
    make_story(series, args.seed, appearances)
    init_scenery()
    name = args.name or f"SIM_{SERIES.upper()}_{ENGINE_VERSION.upper()}_S{args.seed:03d}"
    if not args.preview_only and not args.force:
        other = registry.find_seed(SERIES, ENGINE_VERSION, args.seed, exclude_id=name)
        if other:
            raise SystemExit(f"[registry] STOP: seed {args.seed} sudah dipakai oleh {other}. Pakai seed lain.")
        if os.path.exists(f"{OUT_DIR}/{name}.mp4"):
            raise SystemExit(f"[registry] STOP: {OUT_DIR}/{name}.mp4 sudah ada. Pakai seed lain atau --force.")
    print(f"[track] {TRACK_ID} {json.dumps(TRACK_PARAMS)}", flush=True)
    print(f"[story] {SERIES}: " + " -> ".join(f"{vk}({want})" for vk, want in STORY), flush=True)
    rng = np.random.default_rng(args.seed)
    t0 = time.time()
    print(f"[font] {FONT_FACE}", flush=True)

    intro_texts = [intro_text(li, vk) for li, (vk, _) in enumerate(STORY)]
    intros = [tts(s) for s in intro_texts]
    intro_durs = [len(x) / SR for x in intros]
    cands = candidate_runs(intro_durs)
    cta = tts(CTA)
    replay_vo = tts(REPLAY_LINE)

    def outcome_line(vk, run):
        tmpl = WIN_LINE if run["event"]["type"] == "win" else FAIL_LINES[run["event"]["type"]]
        return tmpl.format(n=VEHICLES[vk]["nick"])

    line_audio = {}
    timed = []
    for li, ((vk, _), runs_li) in enumerate(zip(STORY, cands)):
        row = []
        for run in runs_li:
            text = outcome_line(vk, run)
            if text not in line_audio:
                line_audio[text] = tts(text)
            row.append(level_timing(vk, run, intro_durs[li], len(line_audio[text]) / SR, len(cta) / SR))
        timed.append(row)
    combo = pick_combo(rng, timed)
    if combo is None:
        raise SystemExit(f"[analysis] STOP: tidak ada kombinasi run yang masuk durasi {TARGET_TOTAL[0]}-"
                         f"{TARGET_TOTAL[1]} s dengan momen spektakuler. Coba seed lain. "
                         f"(kombinasi={PICK_STATS['combos']}, durasi_total_ok={PICK_STATS['total_ok']}, "
                         f"durasi_level_ok={PICK_STATS['len_ok']}, spektakuler_ok={PICK_STATS['spect_ok']}; "
                         f"kandidat per level={[len(r) for r in timed]}, "
                         f"durasi level={[sorted(round(L['dur']) for L in r) for r in timed]})")
    chosen = [timed[li][ci] for li, ci in enumerate(combo)]
    outcome_lines = [outcome_line(L["vk"], L) for L in chosen]
    outcomes = [line_audio[s] for s in outcome_lines]
    print(f"[sim] done in {time.time() - t0:.1f}s", flush=True)

    # timeline
    gstart = 0.0
    for li, L in enumerate(chosen):
        L["start"] = gstart
        L["cam"] = camera_track(L)
        L["bubbles"] = find_bubbles(L)
        L["dur"] = len(L["frames"]) / FPS
        INDEX.extend((li, j) for j in range(len(L["frames"])))
        LEVELS.append(L)
        gstart += L["dur"]
    total = len(INDEX) / FPS
    print(f"[timeline] {total:.1f}s, {len(INDEX)} frames @ {FPS}fps", flush=True)

    # analysis gate + uniqueness (BLUEPRINT.md sections 5 and 7)
    analysis = analyze([len(x) / SR for x in intros])
    entry = dict(video_id=name, series=SERIES, engine_version=ENGINE_VERSION, seed=args.seed,
                 created=time.strftime("%Y-%m-%d"), vehicles=[vk for vk, _ in STORY], track_id=TRACK_ID,
                 outcomes=outcome_tags(), duration=round(total, 2), status="ANALYZED",
                 audit=f"renders/{name}_audit.md", youtube_url=None)
    fingerprint = registry.fingerprint(entry)
    dup = registry.find_fingerprint(fingerprint, exclude_id=name)
    analysis.append(check("unique", "Sidik jari belum ada di registry", dup is None or args.allow_duplicate,
                          f"{fingerprint}" + (f" (sama dengan {dup})" if dup else "")))
    for c in analysis:
        print(f"[analysis] {'OK  ' if c['ok'] else ('FAIL' if c['hard'] else 'WARN')} {c['id']}: {c['detail']}",
              flush=True)
    analysis_ok = all(c["ok"] for c in analysis if c["hard"])

    # audio
    n = int(total * SR) + 1
    narr, eng, sfx = np.zeros(n), np.zeros(n), np.zeros(n)

    def place(buf, sig, t, gain=1.0):
        i0 = int(t * SR)
        if i0 >= n or i0 < 0:
            return
        m = min(len(sig), n - i0)
        buf[i0:i0 + m] += sig[:m] * gain

    pop = sweep(700, 1500, 0.09, 0.6)
    gulp = sweep(480, 200, 0.18, 0.7)
    for li, L in enumerate(LEVELS):
        st0, ev = L["start"], L["event"]
        fr = L["frames"]
        sts = np.array([f[0] for f in fr])
        modes = [f[1] for f in fr]
        rates = np.diff(np.append(sts, sts[-1] + 1 / FPS)) * FPS
        wrel = np.array([interp(L["rec"]["wrel"], t) for t in sts])
        top = L["speed"] / L["v"]["wheel_r"]
        amp = 0.55 + 0.45 * np.minimum(1, wrel / top)
        if ev["type"] == "win":
            amp = np.where(sts > ev["t"], np.maximum(0.35, amp * np.clip(1 - (sts - ev["t"]) / 3, 0, 1)), amp)
        else:
            amp = amp * np.clip(1 - (sts - ev["t"]) / 0.8, 0, 1)
        live = np.array([m == "live" for m in modes])
        amp = np.where(live, amp, 0.0)
        pitch = np.where(live, np.sqrt(np.clip(rates, 0.3, 1.0)), 1.0)
        base, kk = L["v"]["engine"]
        place(eng, synth_engine(wrel, amp, pitch, base, kk, seed=li), st0)
        place(sfx, synth_whoosh(), st0, 0.5)
        for j, (ti, s, _, _) in enumerate(L["impacts"]):
            if ti < L["live_end"]:
                place(sfx, synth_impact(s, seed=100 + j), st0 + out_time(L, ti), 0.9)
        if L["broken"]:
            place(sfx, synth_shatter(), st0 + out_time(L, L["broken"]["t"]), 0.7)
        for bt, text in L["bubbles"]:
            place(sfx, pop, st0 + out_time(L, bt), 0.6)
            if text == "UH OH!":
                place(sfx, gulp, st0 + out_time(L, bt) + 0.1, 0.6)
        place(narr, intros[li], st0 + 0.15)
        place(narr, outcomes[li], st0 + outcome_vo_t(out_time(L, ev["t"]), len(intros[li]) / SR))
        if ev["type"] == "win":
            place(sfx, synth_win(), st0 + out_time(L, ev["t"]), 0.9)
            place(narr, cta, st0 + out_time(L, L["outro_t"]))
        else:
            place(sfx, synth_fail(), st0 + out_time(L, ev["t"]) + 0.1, 0.75)
            place(sfx, synth_tweets(), st0 + out_time(L, ev["t"]) + 1.3, 0.5)
        if L["replay"]:
            ta, tb = L["replay"]
            r0 = st0 + L["replay_out"]
            place(sfx, synth_rewind(), r0, 0.6)
            place(narr, replay_vo, r0 + 0.1)
            for j, (ti, s, _, _) in enumerate(L["impacts"]):
                if ta <= ti < tb:
                    place(sfx, stretch(synth_impact(s, seed=200 + j), 0.45), r0 + (ti - ta) / REPLAY_SPEED, 1.0)
            if L["broken"] and ta <= L["broken"]["t"] < tb:
                place(sfx, stretch(synth_shatter(), 0.5), r0 + (L["broken"]["t"] - ta) / REPLAY_SPEED, 0.7)
    bgm = synth_bgm(total)
    bgm = bgm[:n] if len(bgm) >= n else np.pad(bgm, (0, n - len(bgm)))
    mix = peak(narr) * VOL_NARR + peak(eng) * VOL_ENGINE + peak(bgm) * VOL_BGM + peak(sfx) * VOL_SFX
    mix = np.tanh(1.3 * mix) / np.tanh(1.3)
    mix = mix / max(1e-9, np.max(np.abs(mix))) * 0.95
    wav_path = f"{WORK}/mix_{name}.wav"
    write_wav(wav_path, mix)

    prev_dir = f"{OUT_DIR}/{name}_preview"
    os.makedirs(prev_dir, exist_ok=True)
    marks = []
    for li, L in enumerate(LEVELS):
        g0 = int(round(L["start"] * FPS))
        marks.append((f"L{li + 1}_start", g0 + 20))
        for bt, text in L["bubbles"][:1]:
            marks.append((f"L{li + 1}_bubble", g0 + int(out_time(L, bt + 0.3) * FPS)))
        marks.append((f"L{li + 1}_event", g0 + int(out_time(L, L["event"]["t"] + 0.5) * FPS)))
        if L["bullet"]:
            marks.append((f"L{li + 1}_bullet", g0 + int(out_time(L, sum(L["bullet"]) / 2) * FPS)))
        if L["replay"]:
            marks.append((f"L{li + 1}_replay", g0 + int((L["replay_out"] + 2.0) * FPS)))
        if L.get("outro_t"):
            marks.append(("outro", g0 + int((out_time(L, L["outro_t"]) + 1.0) * FPS)))
    for label, g in marks:
        save_png(min(g, len(INDEX) - 1), f"{prev_dir}/{label}.png")
    print(f"[preview] {prev_dir}", flush=True)

    any_replay = any(L["replay"] for L in LEVELS)
    manifest = dict(
        video_id=name, status="ANALYZED" if analysis_ok else "ANALYSIS_FAILED", engine=f"sim-prototype {ENGINE_VERSION}",
        series=SERIES, seed=args.seed, fps=FPS, duration=round(total, 2),
        track_id=TRACK_ID, track_params=TRACK_PARAMS, fingerprint=fingerprint, outcomes=entry["outcomes"],
        analysis=analysis, cta=CTA,
        title=SERIES_DEFS[SERIES]["yt_title"],
        description=(f"Can {', '.join(VEHICLES[vk]['nick'] for vk, _ in STORY[:-1])} or {VEHICLES[STORY[-1][0]]['nick']} "
                     f"survive the {SERIES_DEFS[SERIES]['obst'].upper()}? 🚗💥 Watch till the end! 🏁\n\n"
                     "#Shorts #Cars #MonsterTruck #KidsVideos #MegaWheelKids"),
        tags=SERIES_DEFS[SERIES]["tags"] + [VEHICLES[vk]["display"].split(" THE ")[1].lower() for vk, _ in STORY],
        levels=[dict(vehicle=L["v"]["display"], speed=round(L["speed"], 2), outcome=L["event"]["type"],
                     event_t=round(L["event"]["t"], 2), obstacle=L["event"]["obstacle"],
                     broken=bool(L["broken"]), bullet_time=bool(L["bullet"]), replay=bool(L["replay"]),
                     bubbles=[b[1] for b in L["bubbles"]], start=round(L["start"], 2), duration=round(L["dur"], 2),
                     event_out=round(L["start"] + out_time(L, L["event"]["t"]), 2),
                     x_start=round(float(L["rec"]["cx"][0]), 1), x_end=round(float(L["rec"]["cx"][-1]), 1),
                     level_color=[int(c * 255) for c in LEVEL_COLORS[li]])
                for li, L in enumerate(LEVELS)],
        narration=intro_texts + outcome_lines + ([REPLAY_LINE] if any_replay else [])
                  + [CTA],
        assets="100% procedurally generated (pymunk physics + cairo render + synthesized audio), narration Edge-TTS "
               + VOICE,
        video_path=f"{OUT_DIR}/{name}.mp4", preview_dir=prev_dir,
    )
    with open(f"{OUT_DIR}/{name}.json", "w") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
    if not analysis_ok:
        failed = [c["id"] for c in analysis if c["hard"] and not c["ok"]]
        raise SystemExit(f"[analysis] STOP: gagal {failed}. Video TIDAK dirender. Coba seed lain "
                         f"(lihat {OUT_DIR}/{name}.json -> analysis).")
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

    # automatic audit (BLUEPRINT.md section 6) + registry (section 7)
    import audit
    passed = audit.run_audit(name)
    entry["status"] = "RENDERED_PENDING_APPROVAL" if passed else "AUDIT_FAILED"
    registry.upsert(entry)
    print(f"[audit] {'PASS' if passed else 'FAIL'} -> {OUT_DIR}/{name}_audit.md", flush=True)
    print("[result] " + json.dumps(dict(video_id=name, video=out, manifest=f"{OUT_DIR}/{name}.json",
                                        preview_dir=prev_dir, duration=round(total, 2), status=entry["status"],
                                        audit=f"{OUT_DIR}/{name}_audit.md")), flush=True)
    if not passed:
        raise SystemExit(5)


if __name__ == "__main__":
    main()
