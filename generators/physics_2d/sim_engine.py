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
import shutil
import subprocess
import sys
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
CHANNEL_DIR = f"{BASE}/renders/megawheel_arena"   # pending/ -> S01/E001_<date>_<series>/ (episodes.py approve)
OUT_DIR = f"{CHANNEL_DIR}/pending"                # set per job in main()
CAST_FILE = f"{BASE}/cast/characters.json"
CHANNEL = "MegaWheel Arena"          # rebrand 2026-09-30 (was "MegaWheel Kids"): general audience, not made for kids
# Narrator rotates per episode (fewest uses first). en-US adult female voices ONLY (user rule, 2026-09-30).
VOICES = ["en-US-AriaNeural", "en-US-AvaMultilingualNeural", "en-US-EmmaMultilingualNeural",
          "en-US-JennyNeural", "en-US-MichelleNeural"]
VOICE = VOICES[0]                    # set per video in main()
TTS_RATE, TTS_PITCH = "+12%", "+2Hz"  # energetic delivery
TTS_CLARITY = "highpass=f=90,equalizer=f=3000:t=q:w=1.2:g=4,acompressor=threshold=-20dB:ratio=3:attack=5:release=90"
DUCK_DB = 8.0                        # engine + music dip while the narrator talks
CTA = ("Tap LIKE if you enjoyed this video, DISLIKE if you didn't, "
       f"and smash SUBSCRIBE to {CHANNEL}!")
REPLAY_LINE = "Let's see that again, in slow motion!"

# Audio balance (from PROJECT_HISTORY_AND_HANDOVER.md, stems normalised to 0.45 peak first)
VOL_NARR, VOL_ENGINE, VOL_BGM, VOL_SFX = 1.60, 0.85, 0.10, 0.85
# user 2026-10-03: no background music in Shorts (the narrator is enough); our theme song only, faint, after the
# win cheer. SHORTS_BGM = True brings the old synth bed back.
SHORTS_BGM = False
WIN_SONG = f"{BASE}/branding/music/intro_lets_go_v1mix3.wav"   # approved theme (Ep. 1 remix3)
WIN_SONG_FROM = 13.5                                            # chorus ("Mega, Mega, MegaWheel")

# ---------------------------------------------------------------- series + track
ENGINE_VERSION = "v2"
START_X = 3.0
FINISH_X = 100.0
SERIES_DEFS = {
    # win_pool: "any" = every character that can physically win on the track may be champion
    # (fewest wins first); "monsters" = only the monster trucks (the physics demands it)
    "potholes": dict(title="CARS VS GIANT POTHOLES!", obst="giant potholes", max_fail=20.0, max_win=24.0,
                     win_pool="any",
                     yt_title="Cars VS Giant Potholes! Who Survives? 🚗💥",
                     tags=["cars", "potholes", "monster truck", "crash test", "physics simulation", "shorts",
                           "MegaWheel Arena"]),
    "bumps": dict(title="CARS VS GIANT SPEED BUMPS!", obst="giant speed bumps", speed_scale=1.25,
                  max_fail=18.0, max_win=27.0, win_pool="monsters",
                  yt_title="Cars VS Giant Speed Bumps! Who Survives? 🚗💥",
                  tags=["cars", "speed bumps", "monster truck", "crash test", "physics simulation", "shorts",
                        "MegaWheel Arena"]),
    "splash": dict(title="CARS VS SPLASH ZONE!", obst="slippery splash zone", max_fail=20.0, max_win=26.0,
                   win_pool="any", signature="spin",
                   fail_lines={"crash": "Crash! {n} slid right into the wall!",
                               "crash_spun": "Crash! {n} spun out on the water and slammed the wall!",
                               "pit": "Sploosh! {n} plunged into the water pit!",
                               "pit_spun": "Sploosh! {n} spun out and splashed into the pool!",
                               "rollback": "Oh no! {n} lost grip and slid back down!",
                               "rollback_spun": "Whoa! {n} spun out and slid back down the hill!"},
                   yt_title="Cars VS Slippery Splash Zone! Who Survives? 💦🚗",
                   tags=["cars", "car crash", "slippery road", "water puddle", "crash test", "physics simulation",
                         "shorts", "MegaWheel Arena"]),
    "lava": dict(title="CARS VS LAVA ROAD!", obst="erupting lava road", max_fail=20.0, max_win=26.0,
                 win_pool="any", signature="melt", force_theme=dict(location="volcano", weather="clear"),
                 fail_lines={"pit": "Oh no! {n} fell into the lava and is melting!",
                             "lava": "Yikes! {n} got blasted by the lava!"},
                 yt_title="Cars VS Lava Road! Who Survives? 🌋🔥",
                 tags=["cars", "lava", "volcano", "car crash", "crash test", "physics simulation", "shorts",
                       "MegaWheel Arena"]),
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
PUDDLES = []        # (x0, x1) low-grip water on the road
BARRIERS = []       # (x, width, height) concrete walls
VENTS = []          # dict(x, period, phase, dur, height) erupting lava vents
RAMPS = []          # (x0, x1, height) wooden kickers (RAMP = first one, kept for potholes)
PIT_KIND = "mud"    # "mud" | "lava"
OBST_SPANS = []     # (x0, x1) of every hazard in track order (outcome tags "obs<i>")
TRACK = []
TRACK_PARAMS = {}
TRACK_ID = ""


def _reset_hazards():
    global PUDDLES, BARRIERS, VENTS, RAMPS, PIT_KIND, PITS, BUMPS, RAMP
    PUDDLES, BARRIERS, VENTS, RAMPS, PITS, BUMPS = [], [], [], [], [], []
    PIT_KIND, RAMP = "mud", None


def make_track(series, seed):
    global SERIES, TITLE, OBST_SPANS
    SERIES = series
    TITLE = SERIES_DEFS[series]["title"]
    _reset_hazards()
    {"bumps": make_bumps_track, "splash": make_splash_track, "lava": make_lava_track}.get(
        series, make_potholes_track)(seed)
    if not OBST_SPANS:
        OBST_SPANS = [(a, b) for a, b, _ in (PITS or BUMPS)]


class _TB:
    """Tiny track builder: appends polyline points left to right."""

    def __init__(self, x0=0.0):
        self.pts = [(-40, 0), (x0, 0)]

    @property
    def x(self):
        return self.pts[-1][0]

    @property
    def y(self):
        return self.pts[-1][1]

    def flat(self, length):
        self.pts.append((round(self.x + length, 2), self.y))

    def to(self, dx, y):
        self.pts.append((round(self.x + dx, 2), round(y, 2)))

    def drop(self, y):
        self.pts.append((self.x, round(y, 2)))


def make_splash_track(seed):
    """Wet road: puddles steal traction right before a wall jump, a steep hill and a pit jump."""
    global PUDDLES, BARRIERS, RAMPS, RAMP, PITS, OBSTACLES, DANGER_X, SIGNS, TRACK, TRACK_PARAMS, TRACK_ID, \
        FINISH_X, OBST_SPANS, PIT_KIND
    r = np.random.default_rng(6000 + seed)
    PIT_KIND = "water"                                       # the pit is a deep water pool
    order = [str(k) for k in r.permutation(["wall", "hill", "pit"])]
    tb = _TB(0.0)
    tb.flat(float(r.uniform(15, 18)))
    params, spans, obst, danger = [], [], [], []
    for kind in order:
        pl = round(float(r.uniform(4.5, 6.5)), 1)             # shorter track (B1: durations were too long)
        p0 = tb.x
        tb.flat(pl)
        PUDDLES.append((p0, tb.x))
        if kind == "wall":
            tb.flat(3.0)
            rl, rh = round(float(r.uniform(4.5, 5.5)), 1), round(float(r.uniform(0.9, 1.2)), 2)
            x0 = tb.x
            tb.to(rl, rh)
            tb.drop(0.0)
            RAMPS.append((x0, tb.x, rh))
            tb.flat(1.2)
            bh = round(float(r.uniform(1.4, 2.0)), 2)
            BARRIERS.append((tb.x, 1.0, bh))
            spans.append((p0, tb.x + 1.0))
            obst.append((tb.x + 0.5, "wall"))
            tb.flat(float(r.uniform(6, 8)))
            params.append(dict(kind=kind, puddle=pl, ramp=(rl, rh), wall=bh))
        elif kind == "hill":
            hh, run = round(float(r.uniform(3.2, 4.2)), 2), round(float(r.uniform(6.5, 8.0)), 1)
            x0 = tb.x
            PUDDLES[-1] = (p0, x0 + run * 0.45)              # the lower half of the slope is wet too
            tb.to(run, hh)
            tb.flat(3.0)
            tb.to(run * 1.2, 0.0)
            spans.append((p0, tb.x))
            obst.append((x0 + run, "hill"))
            tb.flat(float(r.uniform(5.5, 7)))
            params.append(dict(kind=kind, puddle=pl, hill=(hh, run)))
        else:
            tb.flat(3.0)
            rl, rh = round(float(r.uniform(5, 6.5)), 1), round(float(r.uniform(1.2, 1.5)), 2)
            x0 = tb.x
            tb.to(rl, rh)
            pw, pd = round(float(r.uniform(6.5, 8.5)), 1), round(float(r.uniform(3.8, 4.6)), 1)
            tb.drop(-pd)
            px0 = tb.x
            tb.flat(pw)
            tb.drop(0.0)
            RAMPS.append((x0, px0, rh))
            PITS.append((px0, tb.x, pd))
            spans.append((p0, tb.x))
            obst.append(((px0 + tb.x) / 2, "pit"))
            tb.flat(float(r.uniform(6, 8)))
            params.append(dict(kind=kind, puddle=pl, ramp=(rl, rh), pit=(pw, pd)))
        danger.append(p0)
    FINISH_X = round(tb.x - 2.0, 1)
    tb.pts.append((FINISH_X + 80, 0))
    TRACK = tb.pts
    RAMP = RAMPS[0] if RAMPS else None
    OBST_SPANS, OBSTACLES, DANGER_X = spans, obst, danger
    SIGNS = [d - 3 for d in danger]
    TRACK_PARAMS = dict(order=order, parts=params)
    TRACK_ID = "splash_" + hashlib.md5(json.dumps(TRACK_PARAMS).encode()).hexdigest()[:8]


def make_lava_track(seed):
    """Volcano road: erupting vents (timing!) and lava pits, the big one after a ramp."""
    global VENTS, RAMPS, RAMP, PITS, PIT_KIND, OBSTACLES, DANGER_X, SIGNS, TRACK, TRACK_PARAMS, TRACK_ID, \
        FINISH_X, OBST_SPANS
    r = np.random.default_rng(7000 + seed)
    PIT_KIND = "lava"
    tb = _TB(0.0)
    tb.flat(float(r.uniform(32, 36)))                        # first hazard after the intro narration
    spans, obst, danger = [], [], []

    def vent():
        v = dict(x=round(tb.x + 1.0, 2), period=round(float(r.uniform(2.2, 3.2)), 2),
                 phase=round(float(r.uniform(0, 3)), 2), dur=round(float(r.uniform(0.7, 0.95)), 2),
                 height=round(float(r.uniform(5, 7)), 1))
        VENTS.append(v)
        spans.append((v["x"] - 1.5, v["x"] + 1.5))
        obst.append((v["x"], "vent"))
        danger.append(v["x"] - 1.5)
        tb.flat(2.0)

    def pit(w, d, ramp=None):
        if ramp:
            x0 = tb.x
            tb.to(ramp[0], ramp[1])
            RAMPS.append((x0, tb.x, ramp[1]))
        tb.drop(-d)
        px0 = tb.x
        tb.flat(w)
        tb.drop(0.0)
        PITS.append((px0, tb.x, d))
        spans.append((px0, tb.x))
        obst.append(((px0 + tb.x) / 2, "lava"))
        danger.append(px0 - (ramp[0] if ramp else 0))

    pit(round(float(r.uniform(4.5, 5.5)), 1), 3.0)          # a pit first: vents never fire before cars get going
    tb.flat(float(r.uniform(7, 9)))
    vent()
    tb.flat(float(r.uniform(6, 8)))
    vent()
    tb.flat(float(r.uniform(6, 8)))
    pit(round(float(r.uniform(6.5, 8.5)), 1), 4.5, ramp=(round(float(r.uniform(5, 6.5)), 1),
                                                       round(float(r.uniform(1.2, 1.6)), 2)))
    tb.flat(float(r.uniform(7, 9)))
    vent()
    tb.flat(12.0)
    FINISH_X = round(tb.x - 2.0, 1)
    tb.pts.append((FINISH_X + 80, 0))
    TRACK = tb.pts
    RAMP = RAMPS[0] if RAMPS else None
    OBST_SPANS, OBSTACLES, DANGER_X = spans, obst, danger
    SIGNS = [d - 3 for d in danger]
    TRACK_PARAMS = dict(vents=VENTS, pits=PITS, ramps=RAMPS)
    TRACK_ID = "lava_" + hashlib.md5(json.dumps(TRACK_PARAMS).encode()).hexdigest()[:8]


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
    RAMPS[:] = [RAMP]
    BUMPS = []
    OBSTACLES = [((a + b) / 2, "pit") for a, b, _ in PITS]
    DANGER_X = [p["p1x"], p["rampx"], p["p3x"]]
    SIGNS = [p["p1x"] - 3, p["rampx"] - 2.5, p["p3x"] - 3]
    TRACK_PARAMS = p
    TRACK_ID = f"{SERIES}_std" if seed == 1 else \
        f"{SERIES}_" + hashlib.md5(json.dumps(p, sort_keys=True).encode()).hexdigest()[:8]


# ---------------------------------------------------------------- themes (time of day x weather x location)
TIMES = {
    "morning": dict(sky=[(0, (0.45, 0.68, 1.0)), (0.6, (0.98, 0.8, 0.75)), (1, (1.0, 0.9, 0.8))],
                    sun=(190, 600, 65, (1, 0.85, 0.5)), light=1.0, cloud=(1, 0.95, 0.95), tint=None,
                    music=dict(bpm=118, chords=[(60, 64, 67), (65, 69, 72), (67, 71, 74), (60, 64, 67)], lead="tri")),
    "noon": dict(sky=[(0, (0.36, 0.7, 1.0)), (0.6, (0.72, 0.9, 1.0)), (1, (0.85, 0.95, 1.0))],
                 sun=(900, 520, 70, (1, 0.9, 0.35)), light=1.0, cloud=(1, 1, 1), tint=None,
                 music=dict(bpm=128, chords=[(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)], lead="tri")),
    "sunset": dict(sky=[(0, (0.22, 0.22, 0.55)), (0.5, (0.95, 0.45, 0.35)), (1, (1.0, 0.72, 0.35))],
                   sun=(800, 760, 100, (1, 0.55, 0.2)), light=0.82, cloud=(1, 0.75, 0.65), tint=(0.35, 0.1, 0.25, 0.12),
                   music=dict(bpm=104, chords=[(57, 60, 64), (53, 57, 60), (60, 64, 67), (55, 59, 62)], lead="sine")),
    "night": dict(sky=[(0, (0.02, 0.03, 0.12)), (0.6, (0.07, 0.1, 0.28)), (1, (0.15, 0.17, 0.35))],
                  moon=(860, 560, 55), light=0.6, cloud=(0.5, 0.55, 0.7), tint=(0.02, 0.04, 0.18, 0.38),
                  music=dict(bpm=122, chords=[(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)], lead="saw")),
}
WEATHERS = {"clear": dict(friction=1.0), "rain": dict(friction=0.72), "snow": dict(friction=0.55)}
LOCATIONS = {
    "countryside": dict(hills=[(0.56, 0.8, 0.52), (0.42, 0.72, 0.38)], ground=(0.58, 0.38, 0.22)),
    "city": dict(hills=[(0.5, 0.56, 0.66), (0.42, 0.66, 0.4)], ground=(0.5, 0.42, 0.36), skyline=True),
    "desert": dict(hills=[(0.95, 0.82, 0.58), (0.9, 0.72, 0.46)], ground=(0.86, 0.68, 0.42), cactus=True),
    "mountains": dict(hills=[(0.56, 0.6, 0.72), (0.4, 0.6, 0.42)], ground=(0.55, 0.42, 0.3), peaks=True),
    "beach": dict(hills=[(0.25, 0.58, 0.86), (0.96, 0.88, 0.64)], ground=(0.9, 0.8, 0.55), ocean=True, palms=True),
    "volcano": dict(hills=[(0.36, 0.28, 0.28), (0.26, 0.2, 0.2)], ground=(0.32, 0.27, 0.26), volcano=True),
}
NO_SNOW = {"desert", "beach", "volcano"}
RANDOM_LOCATIONS = ["countryside", "city", "desert", "mountains", "beach"]   # volcano only for the lava series
THEME = dict(time="noon", weather="clear", location="countryside")
THEME_ID = "noon-clear-countryside"


def make_theme(seed, force=None, used=None):
    """Time + location rotate (fewest uses in the registry first, seed breaks ties); weather is random
    with plausible combos only. `used` = list of previous theme ids."""
    global THEME, THEME_ID
    r = np.random.default_rng(4000 + seed)
    used = used or []

    def least(options, idx):
        cnt = {o: sum(1 for u in used if u.split("-")[idx] == o) for o in options}
        tie = {o: float(r.random()) for o in options}
        return min(options, key=lambda o: (cnt[o], tie[o]))

    loc = least(RANDOM_LOCATIONS, 2)
    time_ = least(list(TIMES), 0)
    w = str(r.choice(["clear", "rain", "snow"], p=[0.5, 0.25, 0.25]))
    if w == "snow" and loc in NO_SNOW:
        w = "clear"
    if w == "rain" and loc == "desert":
        w = "clear"
    THEME = dict(time=time_, weather=w, location=loc)
    if force:
        THEME.update(force)
    THEME_ID = f"{THEME['time']}-{THEME['weather']}-{THEME['location']}"


def th_time():
    return TIMES[THEME["time"]]


def th_loc():
    return LOCATIONS[THEME["location"]]


def lit(c, extra=1.0):
    """Apply the time-of-day light level to a colour."""
    k = th_time()["light"] * extra
    return tuple(min(1.0, v * k) for v in c)


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
# --- cast expansion (2026-09-30): F1 car, taxi, big rig, ice cream truck
VEHICLES.update({
    "f1": dict(nick="Nitro", display="NITRO THE RACE CAR", color=(0.1, 0.55, 0.95),
               body=(4.6, 0.45), mass=750, wheel_r=0.36, wheel_m=22, wheel_x=(-1.6, 1.7),
               travel=0.3, speeds=(8, 20), break_dv=4.5, zoom=1.1,
               cabin=[(-0.9, 0.22), (0.2, 0.22), (-0.1, 0.55), (-0.7, 0.55)], engine=(70, 3.0),
               intro="Level {lvl}! Nitro the race car! Super fast... but can Nitro handle the {obst}?"),
    "taxi": dict(nick="Tilly", display="TILLY THE TAXI", color=(1.0, 0.8, 0.0),
                 body=(4.3, 0.7), mass=1100, wheel_r=0.42, wheel_m=28, wheel_x=(-1.4, 1.4),
                 travel=0.45, speeds=(7, 17), break_dv=4.5, zoom=1.05,
                 cabin=[(-1.35, 0.35), (0.65, 0.35), (0.15, 0.95), (-1.15, 0.95)], engine=(48, 2.0),
                 intro="Level {lvl}! Tilly the taxi! Hop in... can Tilly get past the {obst}?"),
    "bigrig": dict(nick="Titan", display="TITAN THE BIG RIG", color=(0.95, 0.42, 0.1),
                   body=(9.6, 2.3), mass=9000, wheel_r=0.6, wheel_x=(-4.0, -2.9, 2.2, 3.8), wheel_m=110,
                   travel=0.35, speeds=(6, 13), break_dv=4.0, zoom=0.78, cabin=None, engine=(32, 1.1),
                   intro="Level {lvl}! Titan the big rig! The biggest truck on the road... can Titan make it?"),
    "icecream": dict(nick="Sprinkles", display="SPRINKLES THE ICE CREAM TRUCK", color=(1.0, 0.6, 0.76),
                     body=(5.6, 2.2), mass=4200, wheel_r=0.5, wheel_m=80, wheel_x=(-1.9, 1.9),
                     travel=0.35, speeds=(6, 14), break_dv=4.0, zoom=0.88, cabin=None, engine=(42, 1.4),
                     intro="Level {lvl}! Sprinkles the ice cream truck! Yummy! Can Sprinkles make it?"),
})
FACES.update({
    "f1": dict(eyes=[(0.55, 0.13), (0.9, 0.13)], r=0.1, mouth=(1.95, -0.1), mw=0.22),
    "taxi": dict(eyes=[(-0.68, 0.62), (-0.26, 0.62)], r=0.13, mouth=(1.65, -0.18), mw=0.3),
    "bigrig": dict(eyes=[(3.85, 0.5), (4.25, 0.5)], r=0.17, mouth=(4.4, -0.7), mw=0.4),
    "icecream": dict(eyes=[(2.05, 0.38), (2.45, 0.38)], r=0.15, mouth=(2.5, -0.62), mw=0.35),
})
# Level roles: seed picks one vehicle per role (potholes seed 1 keeps the reference line-up)
BASE_ROSTER = [(("sports", "police", "f1", "taxi"), "fail"), (("bus", "firetruck", "bigrig", "icecream"), "fail"),
               (("monster", "monster2"), "win")]
ROSTER = list(BASE_ROSTER)          # per video: champion options widened by make_story() (series win_pool)
ROLE_ORDER = []     # per level: characters in preferred order (fewest appearances first); fallback if one can't fit
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


def make_story(series, seed, appearances=None, wins=None):
    """Order the characters of each role (fair rotation, seed breaks ties).

    Fail roles: fewest appearances first. Champion role: fewest WINS first, and with win_pool "any"
    every character may be champion (the physics decides; candidate_runs() falls back to the next
    character when one cannot produce the wanted outcome). Nobody plays two levels.
    """
    global STORY, ROLE_ORDER, ROSTER
    pool = SERIES_DEFS[series].get("win_pool", "monsters")
    champs = tuple(VEHICLES) if pool == "any" else BASE_ROSTER[2][0]
    ROSTER = [BASE_ROSTER[0], BASE_ROSTER[1], (champs, "win")]
    if series == "potholes" and seed == 1:
        ROLE_ORDER = [["sports"], ["bus"], ["monster"]]
    else:
        r = np.random.default_rng(3000 + seed)
        appearances, wins = appearances or {}, wins or {}
        ROLE_ORDER = []
        for li, (opts, want) in enumerate(ROSTER):
            tie = {o: float(r.random()) for o in opts}
            if want == "win":
                ROLE_ORDER.append(sorted(opts, key=lambda o: (wins.get(o, 0), appearances.get(o, 0), tie[o])))
            else:
                ROLE_ORDER.append(sorted(opts, key=lambda o: (appearances.get(o, 0), tie[o])))
    STORY = [(order[0], want) for order, (_, want) in zip(ROLE_ORDER, ROSTER)]


def intro_text(li, vk):
    return VEHICLES[vk]["intro"].format(lvl=NUM_WORDS[li], obst=SERIES_DEFS[SERIES]["obst"])
FAIL_LINES = {"pit": "Oh no! {n} fell into the giant pothole!",
              "flip": "Whoa! {n} flipped right over!",
              "stuck": "Uh oh... {n} is totally stuck!",
              "crash": "Crash! {n} slammed into the wall!",
              "rollback": "Uh oh! {n} slid all the way back down!",
              "lava": "Yikes! {n} got blasted by the lava!"}
WIN_LINE = "Yes! {n} made it! We have a winner!"
LEVEL_COLORS = [(0.18, 0.72, 0.3), (1.0, 0.52, 0.08), (0.6, 0.3, 0.92)]


# ================================================================ physics
PUDDLE_FRICTION = 0.06
SPIN_V = 6.5        # m/s: hitting water faster than this may hydroplane into a spin (chance grows with speed)
PIT_FILL = {"lava": 1.3, "water": None}   # liquid depth in a pit (None = filled up to 0.8 m below the road)


def in_puddle(x):
    return any(x0 <= x <= x1 for x0, x1 in PUDDLES)


def pit_surface(d):
    """y of the liquid surface in a pit of depth d."""
    fill = PIT_FILL.get(PIT_KIND)
    return -d + fill if fill is not None else -0.8


def start_slide(t, vx, v, rng, kind=None):
    """Hydroplaning on water: a full spin (most drive lost) or a fishtail wobble (part drive).
    Big tyres cut through water better (grip). At most one spin per run (caller passes kind="wobble")."""
    grip = 1.35 if v["wheel_r"] >= 0.8 else 1.0
    ve = vx / grip
    if kind is None:
        kind = "spin" if rng.uniform() < np.clip((ve - SPIN_V) / 5.0, 0.0, 0.8) else "wobble"
    sign = 1.0 if rng.uniform() < 0.5 else -1.0
    if kind == "spin":
        turns = 2 if ve > 12.0 else 1
        return dict(kind="spin", t0=t, dur=0.75 + 0.5 * turns, turns=turns, dir=sign, drive=0.5)
    return dict(kind="wobble", t0=t, dur=1.5, amp=float(np.clip(0.2 + 0.045 * vx, 0.3, 0.7)), dir=sign, drive=1.0)


def slide_yaw(sl, t):
    """Yaw angle (rotation around the vertical axis, rendered 2.5D) of a slide at time t."""
    if sl is None:
        return 0.0
    tau = t - sl["t0"]
    if tau < 0 or tau > sl["dur"]:
        return 0.0
    if sl["kind"] == "spin":
        return sl["dir"] * 2 * math.pi * sl["turns"] * (1 - (1 - tau / sl["dur"]) ** 2.2)
    return sl["dir"] * sl["amp"] * math.sin(2 * math.pi * 1.7 * tau) * math.exp(-tau / 0.55)


def vent_active(vent, t):
    return ((t + vent["phase"]) % vent["period"]) < vent["dur"]


def build_space():
    space = pymunk.Space()
    space.gravity = (0, -9.81)
    space.iterations = 25
    wf = WEATHERS[THEME["weather"]]["friction"]
    for a, b in zip(TRACK, TRACK[1:]):
        seg = pymunk.Segment(space.static_body, a, b, 0.08)
        seg.friction = PUDDLE_FRICTION if in_puddle((a[0] + b[0]) / 2) else 1.0 * wf
        seg.elasticity = 0.05
        space.add(seg)
    for bx, bwid, bh in BARRIERS:                         # solid concrete walls
        wall = pymunk.Poly(space.static_body, [(bx, 0), (bx + bwid, 0), (bx + bwid, bh), (bx, bh)], radius=0.03)
        wall.friction = 0.8
        wall.elasticity = 0.15
        space.add(wall)
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
        ws.friction = 1.6 * WEATHERS[THEME["weather"]]["friction"]
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
    for i, (x0, x1) in enumerate(OBST_SPANS):
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
    rec = dict(cx=[], cy=[], ca=[], wheels=[], wrel=[], speed=[], air=[], yaw=[])
    deb_rec, debris = [], []
    impacts, event, broken, burned = [], None, None, None
    flip_t = stuck_t = back_t = None
    vent_hit = set()
    slide, slid, spun, sunk, air_since = None, set(), None, None, None
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
            if slide is not None and t <= slide["t0"] + slide["dur"]:
                force *= slide["drive"]                     # tyres floating on water: drive lost
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
        rec["yaw"].append(slide_yaw(slide, t))
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
        front = ch.position.x + bw / 2 * math.cos(ch.angle)
        if event is None and dv > 4.0 and any(bx - 1.0 <= front <= bx + bwid + 0.5 and ch.position.y < bh + bh_car(v)
                                              for bx, bwid, bh in BARRIERS):
            event = dict(type="crash", t=t)                 # slammed into a wall
        for vi, vent in enumerate(VENTS):                   # lava eruption blasts the car
            if vi in vent_hit or not vent_active(vent, t):
                continue
            # narrow fountain column: only the car body right above the vent is blasted (length-independent)
            if abs(ch.position.x - vent["x"]) < 1.1 and ch.position.y < car["ride_y"] + 2.5:
                vent_hit.add(vi)
                m_tot = v["mass"]
                ch.apply_impulse_at_local_point((m_tot * 1.0, m_tot * 7.0), (-bw * 0.3, 0))
                burned = burned or t
                if event is None:
                    event = dict(type="lava", t=t)
        # hydroplaning: each puddle once; snow: fishtail after a hard landing
        airborne = bool(rec["air"][-1])
        if event is None and (slide is None or t > slide["t0"] + slide["dur"]):
            fw = max((w.position.x for w in attached), default=ch.position.x)
            pk = next((k for k, (x0, x1) in enumerate(PUDDLES) if x0 <= fw <= x1), None)
            if pk is not None and pk not in slid and ch.velocity.x > 3.0 and not airborne:
                slid.add(pk)
                slide = start_slide(t, ch.velocity.x, v, rng, kind="wobble" if spun else None)
                if slide["kind"] == "spin":
                    spun = spun or t
            elif (THEME["weather"] == "snow" and not airborne and air_since is not None and t - air_since > 0.25
                  and ch.velocity.x > 4.0):
                slide = start_slide(t, ch.velocity.x, v, rng, kind="wobble")
        air_since = (air_since if air_since is not None else t) if airborne else None
        for x0, x1, d in PITS:                              # touched the liquid in a pit (lava / water)
            if sunk is None and PIT_KIND in PIT_FILL and x0 <= ch.position.x <= x1 \
                    and ch.position.y - bh / 2 < pit_surface(d):
                sunk = t
                if PIT_KIND == "lava":
                    burned = burned or t
                if event is None:                           # touching the liquid is the fail (never "stuck")
                    event = dict(type="pit", t=max(0.0, t - 0.2))
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
            if event is None and t > 1.5 and ch.velocity.x < -0.8:  # slid back down a hill
                back_t = back_t if back_t is not None else t
                if t - back_t > 0.8:
                    event = dict(type="rollback", t=back_t)
            elif ch.velocity.x >= -0.8:
                back_t = None
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
        elif t >= event["t"] + (after_win if event["type"] == "win" else after_fail):
            break
        if event is not None and "obstacle" not in event:   # also for crash/lava events set above
            event["x"] = ch.position.x
            event["obstacle"] = nearest_obstacle(ch.position.x)

    for k in rec:
        rec[k] = np.asarray(rec[k], dtype=np.float64)
    n = len(rec["cx"])
    deb = np.full((n, len(debris), 3), np.nan)
    for si, row in enumerate(deb_rec):
        for di, stt in enumerate(row):
            deb[si, di] = stt
    if np.max(rec["cx"]) < rec["cx"][0] + 1 and event["type"] != "stuck":
        raise RuntimeError("car did not move forward, motor sign is wrong")
    meta = [{k: d[k] for k in ("kind", "size", "verts", "color", "spawn")} for d in debris]
    return dict(rec=rec, impacts=impacts, event=event, speed=float(speed), broken=broken, burned=burned,
                spun=spun, sunk=sunk, debris=deb, debris_meta=meta, detached=car["detached"])


def bh_car(v):
    return v["body"][1] + v["wheel_r"] * 2 + v["travel"]


TARGET_TOTAL = (44.0, 57.0)   # seconds, pacing window (v3.9: +READY-GO hold, voice C; Shorts limit 60 s)
PICK_STATS = {}


def event_min_t(intro_d):
    """Earliest allowed outcome: may overlap the intro's tail; the outcome line waits for the intro."""
    return max(2.5, intro_d - 1.0)


def level_cap(L):
    d = SERIES_DEFS[SERIES]
    return (d["max_win"] + 1.5 if L["event"]["type"] == "win" else d["max_fail"]) + HOLD_S   # + READY-GO hold, voice-C CTA


def is_spectacular(L):
    """Crash-worthy fail level: broken car, flip, a big bullet-time jump, or the series' signature moment."""
    return bool(L["broken"] or L["event"]["type"] == "flip" or L.get("bullet") or has_signature(L))


def has_signature(L):
    """The moment a series is about: a hydroplane spin (splash), melting in a lava pit (lava)."""
    sig = SERIES_DEFS[SERIES].get("signature")
    if sig == "spin":
        return L.get("spun") is not None and L["spun"] < L["event"]["t"] + 0.5
    if sig == "melt":
        return L.get("sunk") is not None and PIT_KIND == "lava"
    return False


def outcome_vo_t(ev_out, intro_d):
    """Output time (level-local) of the outcome narration: after the event AND after the intro."""
    return max(ev_out + 0.25, HOLD_S + 0.15 + intro_d + 0.2)


def runs_for(vk, want, intro_d):
    """All simulated runs of one character that match the wanted outcome and timing."""
    v = VEHICLES[vk]
    scale = SERIES_DEFS[SERIES].get("speed_scale", 1.0)
    lo = event_min_t(intro_d)
    hi = 15.0 if want == "win" else 11.5
    cands, summary = [], []
    for sp in np.linspace(v["speeds"][0] * scale, v["speeds"][1] * scale, 21):
        run = simulate(v, sp)
        ev = run["event"]
        summary.append(f"{sp:.1f}:{ev['type']}@{ev['t']:.1f}s/obs{ev['obstacle']}{'/BRK' if run['broken'] else ''}"
                       f"{'/SPIN' if run['spun'] else ''}")
        is_win = ev["type"] == "win"
        if (want == "win") == is_win and ev["type"] != "timeout" and lo <= ev["t"] <= hi:
            cands.append(run)
    print(f"[sim] {vk}: " + ", ".join(summary), flush=True)
    return cands


def candidate_runs():
    """Per level: first character of ROLE_ORDER that can produce the wanted outcome (fallback to next)."""
    global STORY
    out, story, intros = [], [], []
    for li, (order, (_, want)) in enumerate(zip(ROLE_ORDER, ROSTER)):
        for vk in order:
            if any(vk == used for used, _ in story):         # nobody plays two levels
                continue
            text = intro_text(li, vk)
            audio = tts(text)
            cands = runs_for(vk, want, len(audio) / SR)
            if cands:
                break
            print(f"[cast] {vk} cannot '{want}' on this track -> trying next character", flush=True)
        else:
            raise SystemExit(f"[analysis] STOP: tidak ada tokoh peran level {li + 1} yang bisa '{want}' "
                             f"di lintasan ini. Coba seed lain.")
        story.append((vk, want))
        intros.append((text, audio))
        out.append(cands)
    STORY = story
    return out, intros


def level_timing(vk, run, intro_d, outcome_d, cta_d, allow_replay=True):
    """Level dict with replay/outro/bullet windows and output frames (no camera yet).
    allow_replay=False gives the same run without its slow-mo replay (pick_combo may use it to fit the pacing)."""
    ev = run["event"]
    L = dict(vk=vk, v=VEHICLES[vk], **run)
    tmax = (len(run["rec"]["cx"]) - 1) / REC_HZ
    L["could_replay"] = ev["type"] != "win" and bool(run["broken"] or ev["type"] == "flip")
    if ev["type"] == "win":
        L["outro_t"] = ev["t"] + outcome_d + 0.3
        L["live_end"] = L["outro_t"] + cta_d + 0.8
        L["replay"] = None
    else:
        L["live_end"] = ev["t"] + max(1.7, outcome_d + 0.45)
        if L["could_replay"] and allow_replay:
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
        replays = sum(1 for L in fails if L["replay"])
        if replays == 0 and any(L["could_replay"] for L in fails):
            continue                                              # keep at least one slow-mo replay per video
        distinct = len({L["event"]["obstacle"] for L in fails}) == len(fails)
        sig = sum(1 for L in Ls if has_signature(L))              # series signature moment on screen
        if SERIES_DEFS[SERIES].get("signature") and sig == 0:
            continue                                              # mandatory: no spin / melt -> next seed
        score = 2.0 * distinct + 1.0 * (spect - 1) + 1.5 * min(crash, 1) - 0.3 * abs(total - 46.0) \
            + 4.0 * min(sig, 1) + 0.5 * max(0, sig - 1) + 0.8 * replays
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
                air=float(interp(rec["air"], st)), yaw=float(interp(rec["yaw"], st)) if "yaw" in rec else 0.0,
                sink=sink_offset(L, st))


def sink_offset(L, st):
    """Visual sinking into lava (viscous, slow); the physics body rests on the pit floor."""
    if PIT_KIND != "lava" or L.get("sunk") is None or st < L["sunk"]:
        return 0.0
    return min(0.7, 0.4 * (st - L["sunk"]))


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
    frames, t = [(0.0, "live")] * int(round(HOLD_S * FPS)), 0.0    # READY... GO! hold on the start line
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
    if abs(s.get("yaw", 0.0)) > 0.25:                            # spinning / fishtailing on water
        return "whoa" if abs(s["yaw"]) > 1.5 else "scared"
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


# Narrator voice "C" (Chatterbox on Modal, user 2026-10-01): m1 (male) / f1 (female) alternate per video. Lines come
# from the announcer cache; missing lines are collected (Edge stands in), generated in ONE Modal call by cb_finish(),
# and the generator restarts itself with the full cache (max 3 rounds, then the whole video uses Edge TTS).
CB = {"on": False, "who": "m1", "edge": "en-US-GuyNeural", "missing": []}
CB_VOICES = ["chatterbox:m1", "chatterbox:f1"]
CB_EDGE = {"m1": "en-US-GuyNeural", "f1": "en-US-AriaNeural"}


def _announcer():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "voice"))
    import announcer
    return announcer


def cb_pick(active, seed, exclude_id=None):
    """Narrator for this video (fewest uses of m1/f1); None = Edge rotation (MW_CB_OFF / MW_VOICE=edge)."""
    if os.environ.get("MW_CB_OFF") or os.environ.get("MW_VOICE") == "edge":
        return None
    uses = {v: 0 for v in CB_VOICES}
    for e in active:
        if e.get("voice") in uses and e.get("video_id") != exclude_id:
            uses[e["voice"]] += 1
    vr = np.random.default_rng(5000 + seed)
    tie = {v: float(vr.random()) for v in CB_VOICES}
    v = min(CB_VOICES, key=lambda x: (uses[x], tie[x]))
    who = v.split(":")[1]
    CB.update(on=True, who=who, edge=CB_EDGE[who], missing=[])
    return v


def cb_finish(note):
    """Call after every narration line was synthesized, before rendering frames."""
    if not CB["on"] or not CB["missing"]:
        return
    rnd = int(os.environ.get("MW_CB_ROUND", "0"))
    ok = _announcer().prefetch(list(dict.fromkeys(CB["missing"])), note=note)
    os.environ["MW_CB_ROUND"] = str(rnd + 1)
    if not ok or rnd >= 2:
        os.environ["MW_CB_OFF"] = "1"
        print("[voice] suara C tidak lengkap -> seluruh video memakai Edge TTS", flush=True)
    print(f"[voice] restart dengan cache suara (putaran {rnd + 1})", flush=True)
    sys.stdout.flush()
    os.execv(sys.executable, [sys.executable] + sys.argv)


READY_LINE, GO_LINE = "Ready...", "Go!"
READY_SET_GO = "Ready... set... let's go!"     # one phrase ("GO!" alone came out as "Geo" in voice C)
READY_SENTINEL = "__READY_GO__"                  # narration placeholder for the spoken READY... GO!
READY_GO_T = 0.5                                 # when "GO!" pops (s after READY); set by ready_go_audio()
HOLD_S = 0.0                                     # CHALLENGE: car waits on the line this long (READY... GO!)


def last_word_onset(x):
    """Start (s) of the last voiced segment after a pause: where 'GO!' begins in 'Ready... set... GO!'."""
    k = int(0.02 * SR)
    env = np.convolve(np.abs(x), np.ones(k) / k, "same")
    on = env > 0.06 * max(1e-9, env.max())
    edges = [i for i in range(1, len(on)) if on[i] and not on[i - 1]]
    gaps = [i for i in edges if not on[max(0, i - int(0.08 * SR)):i].any()]
    return (gaps[-1] if gaps else int(0.6 * len(x))) / SR


def ready_go_audio():
    """Spoken 'Ready... set... GO!'; the GO pop (draw_ready_go) is timed to the spoken 'GO'."""
    global READY_GO_T
    x = tts(READY_SET_GO)
    READY_GO_T = max(0.42, last_word_onset(x))
    return x


def tts(text):
    if CB["on"]:
        an = _announcer()
        style = "norm" if text == CTA else "clear" if text in (READY_SET_GO, GO_LINE, READY_LINE) else "call"
        if os.path.exists(an.path(text, style, CB["who"], "studio")):
            return an.get(text, style, CB["who"], "studio")
        CB["missing"].append((text, style, CB["who"], "studio"))
    voice = CB["edge"] if CB["on"] else VOICE
    key = hashlib.md5(f"{voice}|{TTS_RATE}|{TTS_PITCH}|{TTS_CLARITY}|{text}".encode()).hexdigest()[:12]
    mp3, wav = f"{WORK}/tts_{key}.mp3", f"{WORK}/tts_{key}.wav"
    if not os.path.exists(wav):
        import edge_tts

        async def go():
            await edge_tts.Communicate(text, voice, rate=TTS_RATE, pitch=TTS_PITCH).save(mp3)
        asyncio.run(go())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", TTS_CLARITY, "-ac", "1",
                        "-ar", str(SR), wav], check=True)
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


def _band(x, lo, hi):
    """Crude band-pass: difference of two moving averages (lo/hi in samples)."""
    return smooth(x, lo) - smooth(x, hi)


def _fband(x, lo=None, hi=None):
    """Band-pass through an FFT mask with soft (2nd-order) edges; lo/hi in Hz, None = open."""
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if lo:
        g /= 1 + (lo / np.maximum(f, 1e-3)) ** 4
    if hi:
        g /= 1 + (f / hi) ** 4
    return np.fft.irfft(np.fft.rfft(x) * g, len(x))


def _norm(x, peak=1.0):
    return x / max(1e-9, float(np.max(np.abs(x)))) * peak


def _add(buf, sig, t0):
    i0 = int(t0 * SR)
    if 0 <= i0 < len(buf):
        m = min(len(sig), len(buf) - i0)
        buf[i0:i0 + m] += sig[:m]


def _chirp(f0, f1, dur, decay):
    """Exponential pitch glide with a fast attack; rising = water bubble, falling = heavy gloop."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay) * np.minimum(1, t / 0.002)


def _crackle(n, rate, rng, lo=1200, hi=6000):
    """Fire crackle: random short clicks with a heavy-tailed loudness."""
    out = np.zeros(n)
    for _ in range(int(rate * n / SR)):
        m = int(rng.uniform(0.002, 0.007) * SR)
        i0 = int(rng.uniform(0, n - m - 1))
        out[i0:i0 + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / (0.0015 * SR)) * rng.pareto(2.5)
    return _fband(out, lo, hi)


# ---- water: bright, fast, splashy; bubbles glide UP in pitch ----
def synth_splash(strength=1.0, seed=41, big=False):
    """Car hitting water: slap, sploosh, spray hiss, rising bubble plinks, then falling drops."""
    dur = 1.8 if big else 1.1
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    slap = _fband(rng.standard_normal(n), 350, 4500) * np.exp(-t / 0.018)
    sploosh = _fband(rng.standard_normal(n), 140 if big else 260, 2400) * np.minimum(1, t / 0.012) \
        * np.exp(-t / (0.3 if big else 0.14))
    spray = _fband(rng.standard_normal(n), 2500, 10000) * np.minimum(1, t / 0.03) * np.exp(-t / (0.6 if big else 0.35))
    bubbles = np.zeros(n)
    for _ in range(50 if big else 30):
        t0 = 0.02 + rng.exponential(0.32 if big else 0.18)
        if t0 < dur - 0.1:
            f0 = rng.uniform(450, 1900) * (0.75 if big else 1.0)
            _add(bubbles, _chirp(f0, f0 * rng.uniform(1.5, 2.4), rng.uniform(0.025, 0.06), rng.uniform(0.01, 0.025))
                 * rng.uniform(0.3, 1.0), t0)
    drops = np.zeros(n)
    for _ in range(26):
        t0 = rng.uniform(0.3, dur - 0.05)
        _add(drops, _chirp(rng.uniform(1800, 3800), rng.uniform(3000, 5000), 0.02, 0.006) * rng.uniform(0.2, 0.6), t0)
    mix = slap * 0.8 + sploosh + spray * 0.35 + bubbles * 0.5 + drops * 0.3
    if big:                                                          # big air pocket escaping: low bloop
        _add(mix, _chirp(110, 230, 0.25, 0.12) * 0.8, 0.12)
    return _norm(mix) * (0.55 + 0.45 * strength)


def synth_water_rush(dur, strength=1.0, seed=61):
    """Tyres ploughing through water: continuous shhhh with a restless surge."""
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    hiss = _fband(rng.standard_normal(n), 700, 7000)
    surge = 0.7 + 0.3 * _norm(_fband(rng.standard_normal(n), None, 8))
    env = np.minimum(1, t / 0.05) * np.clip((dur - t) / 0.2, 0, 1)
    return _norm(hiss * surge * env) * strength


def synth_spin(dur, turns, seed=67):
    """Hydroplane spin: swish-swish of spray as the car turns (one swell per half turn)."""
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    ph = 2 * turns * (1 - (1 - t / dur) ** 2.2)                      # follows the yaw curve (half turns)
    swell = np.sin(np.pi * ph) ** 2
    swish = _fband(rng.standard_normal(n), 900, 6000) * (0.25 + swell)
    scrub = _fband(rng.standard_normal(n), 120, 600) * swell * 0.5  # tyre rubber sliding sideways
    return _norm((swish + scrub) * np.clip((dur - t) / 0.2, 0, 1))


def synth_gurgle(seed=83):
    """Sunk car under water: big bubbles glugging up (low, rising)."""
    n = int(2.5 * SR)
    out = np.zeros(n)
    rng = np.random.default_rng(seed)
    for k in range(14):
        t0 = k * 0.16 + rng.uniform(0, 0.08)
        f0 = rng.uniform(150, 320)
        _add(out, _chirp(f0, f0 * rng.uniform(1.6, 2.2), 0.09, 0.05) * (1 - k / 16), t0)
    return _norm(_fband(out, None, 1500))


# ---- lava: low, thick, slow; fire roar + crackle; no bright hiss ----
def _blorp(f0, dur):
    """Viscous lava bubble: slow low swell that rises, then a dull pop."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.7 * (t / dur) ** 2)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / dur) ** 1.5
    pop = np.zeros(n)
    m = int(0.02 * SR)
    pop[-m:] = np.random.default_rng(int(f0)).standard_normal(m) * np.exp(-np.arange(m) / (0.004 * SR))
    return body + _fband(pop, 80, 900) * 0.8


def synth_fire(dur, seed=71):
    """Burning car: low roar that flickers + crackling."""
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    roar = _fband(rng.standard_normal(n), 60, 650)
    flick = 0.55 + 0.45 * _norm(_fband(rng.standard_normal(n), None, 5))
    env = np.minimum(1, t / 0.15) * np.clip((dur - t) / 0.6, 0, 1)
    return _norm(_norm(roar * flick) + _norm(_crackle(n, 30, rng)) * 0.55) * env


def synth_ignite(seed=73):
    """Car catching fire: FWOOMP (low swell of flame) + first crackles."""
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    env = np.minimum(1, t / 0.08) * np.exp(-np.maximum(0, t - 0.08) / 0.4)
    whoomp = _fband(rng.standard_normal(n), 70, 1100) * env
    thump = _chirp(80, 45, 0.4, 0.15)
    mix = _norm(whoomp)
    _add(mix, thump * 0.8, 0.0)
    return _norm(mix + _norm(_crackle(n, 25, rng)) * 0.35 * np.minimum(1, t / 0.2))


def synth_lava_plunge(seed=79):
    """Car sinking into lava: heavy GLOOP, fire whoomp, groaning hot metal, slow blorps."""
    n = int(3.0 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    gloop = np.zeros(n)
    _add(gloop, _chirp(130, 42, 0.55, 0.25), 0.0)
    thud = _fband(rng.standard_normal(n), 35, 320) * np.exp(-t / 0.12)
    env = np.minimum(1, t / 0.15) * (0.35 + 0.65 * np.exp(-t / 0.5)) * np.clip((3.0 - t) / 0.6, 0, 1)
    roar = _norm(_fband(rng.standard_normal(n), 60, 800)) * env
    f = 150 * (1 - 0.35 * t / 3.0) * (1 + 0.02 * np.sin(2 * np.pi * 5 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    groan = sum(np.sin(ph * k) / k for k in (1, 2.76, 5.4)) * np.clip((t - 0.4) / 0.5, 0, 1) \
        * np.clip((2.8 - t) / 0.8, 0, 1)
    blorps = np.zeros(n)
    for _ in range(9):
        _add(blorps, _blorp(rng.uniform(65, 150), rng.uniform(0.14, 0.28)), rng.uniform(0.3, 2.6))
    mix = _norm(gloop) * 1.0 + _norm(thud) * 0.8 + roar * 0.7 + _norm(groan) * 0.22 + _norm(blorps) * 0.55 \
        + _norm(_crackle(n, 20, rng)) * 0.3 * np.minimum(1, t / 0.4)
    return _norm(mix)


def synth_eruption(seed=43):
    """Lava vent: sub rumble build-up, deep boom, roaring fire column, falling rock thuds, blorps."""
    n = int(1.9 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    rumble = _norm(_fband(rng.standard_normal(n), 18, 90)) * np.clip(t / 0.35, 0, 1) * np.clip((1.9 - t) / 0.5, 0, 1)
    blast_env = np.where(t > 0.35, np.exp(-(t - 0.35) / 0.6), 0.0) * np.minimum(1, np.maximum(0, t - 0.35) / 0.05)
    roar = _norm(_fband(rng.standard_normal(n), 60, 900)) * blast_env
    boom = np.zeros(n)
    _add(boom, _chirp(75, 32, 0.8, 0.3), 0.35)
    rocks = np.zeros(n)
    for _ in range(12):
        m = int(0.03 * SR)
        _add(rocks, _fband(rng.standard_normal(m), 90, 600) * np.exp(-np.arange(m) / (0.008 * SR))
             * rng.uniform(0.4, 1.0), rng.uniform(0.6, 1.8))
    blorps = np.zeros(n)
    for _ in range(3):
        _add(blorps, _blorp(rng.uniform(60, 110), 0.22), rng.uniform(0.0, 0.3))
    return _norm(rumble * 0.9 + roar * 0.9 + _norm(boom) * 1.0 + _norm(rocks) * 0.4 + _norm(blorps) * 0.4
                 + _norm(_crackle(n, 18, rng, 900, 4000)) * 0.2 * blast_env)


def synth_lava_bed(dur, seed=89):
    """Lava pool ambience: slow blorps over a faint low roar (gain follows the distance)."""
    n = max(1, int(dur * SR))
    rng = np.random.default_rng(seed)
    out = _norm(_fband(rng.standard_normal(n), 40, 300)) * 0.25
    b = np.zeros(n)
    for _ in range(int(dur * 2.5)):
        _add(b, _blorp(rng.uniform(55, 140), rng.uniform(0.15, 0.3)), rng.uniform(0, dur))
    return _norm(out + _norm(b) * 0.8)


def synth_wall_crash(strength=1.0, seed=53):
    """Car into concrete: heavy thud + crunch + metal clang + falling rubble (~1 s)."""
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    thud = np.sin(2 * np.pi * (60 - 25 * t) * t) * np.exp(-t / 0.3) * 1.8
    crunch = smooth(rng.standard_normal(n), 4) * np.exp(-t / 0.12) * 1.2
    clang = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, d in ((320, 0.25), (515, 0.18), (790, 0.12))) * 0.35
    rubble = np.zeros(n)
    for _ in range(22):
        i0 = int(rng.uniform(0.12, 0.9) * SR)
        m = int(0.02 * SR)
        rubble[i0:i0 + m] += smooth(rng.standard_normal(min(m, n - i0)), 3) * np.exp(-np.arange(min(m, n - i0)) / SR / 0.006) * 0.7
    return (thud + crunch + clang + rubble) * (0.6 + 0.4 * strength)


def synth_whoosh():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    x = np.random.default_rng(3).standard_normal(n)
    band = smooth(x, 3) - smooth(x, 30)
    return band * np.sin(np.pi * t / 0.45) ** 2


# auto series mix (user 2026-10-03, RESEARCH_W3: Potholes 872 / 1,280 views vs Bumps 133-796): half of CHALLENGE = potholes
SERIES_WEIGHT = {"potholes": 3}
COLD_OPEN_S = 1.5   # user 2026-10-03 (RESEARCH_W3): every Short opens on its own biggest moment + a question


def kind_of(vk):
    """'ZIPPY THE SPORTS CAR' -> 'Sports Car'."""
    return VEHICLES[vk]["display"].split(" THE ")[1].title()


def challenge_title(vk, obst, emoji, seed):
    """Unique CHALLENGE title (RESEARCH_W3): character + challenge + question. vk = the car the video is about."""
    n, k, o = VEHICLES[vk]["nick"], kind_of(vk), obst.title()
    pats = [f"Can {n} the {k} Survive {o}? {emoji}",
            f"{k} vs {o}! Can {n} Make It? {emoji}",
            f"Will {n} the {k} Survive {o}? {emoji}"]
    return pats[seed % len(pats)]


def add_cold_open(mp4, t_star, text, dur=COLD_OPEN_S):
    """Prepend `dur` s of the video's own biggest moment (picture + sound, around t_star) with a big question on top,
    then a white flash into the normal start. Shorts are judged on the first 2 seconds (viewed vs swiped away)."""
    words = text.upper().split()
    lines = [" ".join(words)]
    if len(lines[0]) > 16 and len(words) > 1:                # two lines, split near the middle
        cut = min(range(1, len(words)), key=lambda k: abs(len(" ".join(words[:k])) - len(" ".join(words[k:]))))
        lines = [" ".join(words[:cut]), " ".join(words[cut:])]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    for i, ln in enumerate(lines):
        draw_text(ctx, ln, W / 2, 760 + i * 125, 112, fill=(1, 0.86, 0.12), max_w=1000)   # mid-screen, clear of the HUD
    png, tmp = mp4 + ".cold.png", mp4 + ".cold.mp4"
    surf.write_to_png(png)
    t0 = max(0.0, t_star - dur * 0.55)
    # the clip is a separate (seeked) input: reading one input twice would buffer the whole video in RAM
    fc = (f"[0:v]setpts=PTS-STARTPTS[c0];[c0][1:v]overlay=0:0:shortest=1,"
          f"fade=t=out:st={dur - 0.12:.3f}:d=0.12:color=white[cv];"
          f"[0:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st={dur - 0.15:.3f}:d=0.15[ca];"
          f"[2:v]setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.15:color=white[mv];[2:a]asetpts=PTS-STARTPTS[ma];"
          f"[cv][ca][mv][ma]concat=n=2:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", mp4,
                    "-loop", "1", "-i", png, "-i", mp4, "-filter_complex", fc,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, mp4)
    os.remove(png)
    return dur


def music_bed(total, wins=(), hold=None, style=None):
    """Shorts music bus. SHORTS_BGM off: silence, plus the theme song from its chorus at every time in `wins`
    (0.6 s fade-in; plays to the end, or `hold` seconds then a 1 s fade-out). On: the old synth bed."""
    n = int(total * SR)
    if SHORTS_BGM:
        b = synth_bgm(total, style=style)
        return b[:n] if len(b) >= n else np.pad(b, (0, n - len(b)))
    out = np.zeros(n)
    if not wins or not os.path.exists(WIN_SONG):
        return out
    with wave.open(WIN_SONG) as w:                              # stereo theme -> mono (read_wav is mono-only)
        ch, sr0 = w.getnchannels(), w.getframerate()
        song = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    song = song.reshape(-1, ch).mean(axis=1)
    if sr0 != SR:
        song = np.interp(np.arange(0, len(song) - 1, sr0 / SR), np.arange(len(song)), song)
    song = song[int(WIN_SONG_FROM * SR):]
    for t0 in wins:
        i0 = int(t0 * SR)
        if not 0 <= i0 < n:
            continue
        m = min(len(song), n - i0, int(hold * SR) if hold else n)
        env = np.minimum(1.0, np.arange(m) / (0.6 * SR))
        if hold:
            env = env * np.minimum(1.0, (m - np.arange(m)) / (1.0 * SR))
        out[i0:i0 + m] += song[:m] * env
    return out


def synth_bgm(dur, seed=11, style=None):
    """Chiptune loop; style (from the theme) sets tempo, chord progression and lead timbre."""
    style = style or TIMES["noon"]["music"]
    rng = np.random.default_rng(seed)
    beat = 60 / style["bpm"]
    chords = style["chords"]
    lead = style["lead"]
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
            add(tone(f(ch[ci] + 12), beat * 0.45, lead, decay=0.12), t + e * beat / 2, 0.22 if lead != "saw" else 0.14)
        if THEME["weather"] == "snow":                       # sleigh-bell sparkle
            add(tone(f(ch[2] + 36), 0.25, "sine", decay=0.08), t, 0.12)
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


def _hill_y(sx, camx, camy, z, ground_sy, par, base, a1, a2):
    wx = sx + camx * S * par
    return ground_sy + base * z - camy * S * (1 - par) * 0.5 - a1 * math.sin(wx / 260) - a2 * math.sin(wx / 113 + 1)


def draw_sky(ctx, camx, camy, z):
    tm, loc, weather = th_time(), th_loc(), THEME["weather"]
    g = cairo.LinearGradient(0, 0, 0, H)
    for stop, col in tm["sky"]:
        if weather == "rain":
            col = tuple(v * 0.55 + 0.25 for v in col)            # overcast
        elif weather == "snow":
            col = tuple(v * 0.7 + 0.28 for v in col)
        g.add_color_stop_rgb(stop, *col)
    ctx.set_source(g)
    ctx.paint()
    if "moon" in tm:                                            # stars + moon
        rng = np.random.default_rng(99)
        for i in range(90):
            sx, sy = rng.uniform(0, W), rng.uniform(80, 1000)
            a = 0.5 + 0.5 * math.sin(i * 1.7 + camx * 0.05)
            ctx.set_source_rgba(1, 1, 0.9, 0.35 + 0.5 * a)
            ctx.arc(sx, sy, rng.uniform(1.5, 3.5), 0, 2 * math.pi)
            ctx.fill()
        mx, my, mr = tm["moon"]
        rg = cairo.RadialGradient(mx, my, mr * 0.6, mx, my, mr * 3)
        rg.add_color_stop_rgba(0, 0.9, 0.95, 1, 0.35)
        rg.add_color_stop_rgba(1, 0.9, 0.95, 1, 0)
        ctx.set_source(rg)
        ctx.arc(mx, my, mr * 3, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgb(0.96, 0.96, 0.88)
        ctx.arc(mx, my, mr, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgba(0.8, 0.8, 0.72, 0.8)
        for dx, dy, r in [(-15, -10, 10), (18, 12, 7), (5, 22, 5)]:
            ctx.arc(mx + dx, my + dy, r, 0, 2 * math.pi)
            ctx.fill()
    elif weather == "clear":
        sx, sy, sr, col = tm["sun"]
        rg = cairo.RadialGradient(sx, sy, sr * 0.6, sx, sy, sr * 2.8)
        rg.add_color_stop_rgba(0, *col, 0.9)
        rg.add_color_stop_rgba(1, *col, 0)
        ctx.set_source(rg)
        ctx.arc(sx, sy, sr * 2.8, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgb(*col)
        ctx.arc(sx, sy, sr, 0, 2 * math.pi)
        ctx.fill()
    ccol = tm["cloud"] if weather == "clear" else (0.62, 0.64, 0.7) if weather == "rain" else (0.92, 0.93, 0.96)
    n_clouds = 7 if weather == "clear" else 11
    for i in range(n_clouds):
        x = (i * 430 - camx * S * 0.12) % (W + 700) - 350
        y = 560 + (i % 3) * 110 + camy * S * 0.1 - (80 if weather != "clear" else 0)
        ctx.set_source_rgba(*ccol, 0.92)
        k = 1.0 if weather == "clear" else 1.35
        for dx, dy, r in [(0, 0, 55), (60, -25, 65), (125, 0, 50), (60, 15, 55)]:
            ctx.arc(x + dx * k, y + dy * k, r * k, 0, 2 * math.pi)
            ctx.fill()
    ground_sy = GROUND_Y + camy * S * z
    horizon = ground_sy - 300 * z - camy * S * 0.4
    if loc.get("ocean"):                                        # sea band + waves
        ctx.rectangle(0, horizon, W, H - horizon)
        ctx.set_source_rgb(*lit(loc["hills"][0]))
        ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.5)
        ctx.set_line_width(4)
        for row in range(4):
            y = horizon + 30 + row * 45
            off = (camx * S * (0.08 + 0.03 * row)) % 160
            x = -off
            while x < W:
                ctx.move_to(x, y)
                ctx.curve_to(x + 20, y - 10, x + 40, y - 10, x + 60, y)
                x += 160
            ctx.stroke()
    if loc.get("peaks"):                                        # snowy mountain range (far)
        ctx.rectangle(0, horizon + 40, W, H - horizon)          # solid base so no sky shows between peaks
        ctx.set_source_rgb(*lit((0.5, 0.55, 0.68)))
        ctx.fill()
        for i in range(-1, 6):
            px = (i * 320 - camx * S * 0.08) % (W + 640) - 320
            ph = 330 + (i % 3) * 90
            poly(ctx, [(px - 260, horizon + 60), (px, horizon - ph), (px + 260, horizon + 60)])
            ctx.set_source_rgb(*lit((0.5, 0.55, 0.68)))
            ctx.fill()
            poly(ctx, [(px - 70, horizon - ph + 90), (px, horizon - ph), (px + 70, horizon - ph + 90),
                       (px + 25, horizon - ph + 70), (px - 20, horizon - ph + 95)])
            ctx.set_source_rgb(*lit((0.97, 0.98, 1.0)))
            ctx.fill()
    if loc.get("volcano"):                                      # erupting volcano on the horizon
        hg = cairo.LinearGradient(0, horizon - 500, 0, horizon + 60)
        hg.add_color_stop_rgba(0, 1, 0.3, 0.05, 0.0)
        hg.add_color_stop_rgba(1, 1, 0.35, 0.05, 0.45)
        ctx.rectangle(0, horizon - 500, W, 560)
        ctx.set_source(hg)
        ctx.fill()
        vx0 = 620 - (camx * S * 0.05) % 2200
        ctx.rectangle(0, horizon + 60, W, H)                     # solid plain: no sky gaps under the hills
        ctx.set_source_rgb(*lit((0.24, 0.18, 0.18)))
        ctx.fill()
        for vx in (vx0, vx0 + 2200):
            if -700 < vx < W + 700:
                poly(ctx, [(vx - 560, horizon + 80), (vx - 110, horizon - 470), (vx + 110, horizon - 470),
                           (vx + 560, horizon + 80)])
                ctx.set_source_rgb(*lit((0.24, 0.18, 0.18)))
                ctx.fill()
                for k, off in enumerate((-60, 10, 70)):           # glowing lava streams (upper slope only)
                    ctx.move_to(vx + off * 0.4, horizon - 470)
                    ctx.curve_to(vx + off * 0.9, horizon - 400, vx + off * 1.4 - 15, horizon - 330,
                                 vx + off * 1.8, horizon - 250)
                    ctx.set_source_rgba(1, 0.4 + 0.1 * k, 0.05, 0.9)
                    ctx.set_line_width(14 - 3 * k)
                    ctx.stroke()
                rg = cairo.RadialGradient(vx, horizon - 470, 20, vx, horizon - 470, 190)
                rg.add_color_stop_rgba(0, 1, 0.6, 0.1, 0.9)
                rg.add_color_stop_rgba(1, 1, 0.3, 0.0, 0.0)
                ctx.arc(vx, horizon - 470, 190, 0, 2 * math.pi)
                ctx.set_source(rg)
                ctx.fill()
                for j in range(6):                                # smoke plume
                    ctx.arc(vx + 40 * j + 20 * math.sin(j), horizon - 540 - 70 * j, 55 + 18 * j, 0, 2 * math.pi)
                    ctx.set_source_rgba(0.3, 0.27, 0.27, 0.55 - 0.07 * j)
                    ctx.fill()
    if loc.get("skyline"):                                      # city buildings (far)
        rng = np.random.default_rng(7)
        blds = [(rng.uniform(60, 140), rng.uniform(180, 520)) for _ in range(24)]
        period = sum(b[0] + 18 for b in blds)
        x = -((camx * S * 0.15) % period)                       # start left of the screen, tile to the right
        night = "moon" in tm
        while x < W + 200:
            for bw_, bh_ in blds:
                if x > W + 200:
                    break
                if x + bw_ < -10:
                    x += bw_ + 18
                    continue
                ctx.rectangle(x, horizon + 80 - bh_, bw_, bh_ + 400)
                ctx.set_source_rgb(*lit((0.42, 0.46, 0.58)))
                ctx.fill()
                for wy in range(int(horizon + 100 - bh_), int(horizon + 60), 36):
                    for wx_ in range(int(x + 12), int(x + bw_ - 14), 26):
                        on = night and (wx_ * 7 + wy * 3) % 5 < 2
                        ctx.rectangle(wx_, wy, 12, 16)
                        ctx.set_source_rgba(*((1, 0.9, 0.5) if on else (0.62, 0.68, 0.8)), 0.9 if on else 0.55)
                        ctx.fill()
                x += bw_ + 18
    hills = loc["hills"]
    layers = [(0.2, -260, hills[0], 90, 45), (0.45, -150, hills[1], 70, 35)]
    if loc.get("ocean"):
        layers = [(0.45, -110, hills[1], 40, 20)]              # beach: only a sand dune in front of the sea
    for par, base, col, a1, a2 in layers:
        ctx.new_path()
        ctx.move_to(0, H)
        for sx in range(0, W + 21, 20):
            ctx.line_to(sx, _hill_y(sx, camx, camy, z, ground_sy, par, base, a1, a2))
        ctx.line_to(W, H)
        ctx.close_path()
        ctx.set_source_rgb(*lit(col))
        ctx.fill()
        if weather == "snow":                                   # snow on the crests
            ctx.new_path()
            for sx in range(0, W + 21, 20):
                ctx.line_to(sx, _hill_y(sx, camx, camy, z, ground_sy, par, base, a1, a2) + 6)
            ctx.set_source_rgba(0.97, 0.98, 1, 0.95)
            ctx.set_line_width(22)
            ctx.stroke()
    par, base, _, a1, a2 = layers[-1]
    if loc.get("cactus") or loc.get("palms"):                   # props on the front dune
        step = 380
        off = (camx * S * par) % step
        for i in range(-1, W // step + 2):
            sx = i * step - off + 120
            sy = _hill_y(sx, camx, camy, z, ground_sy, par, base, a1, a2) + 8
            if loc.get("cactus"):
                ctx.set_source_rgb(*lit((0.25, 0.6, 0.3)))
                rrect(ctx, sx - 14, sy - 150, 28, 150, 14)
                rrect(ctx, sx - 50, sy - 110, 22, 60, 11)
                rrect(ctx, sx + 28, sy - 125, 22, 70, 11)
                ctx.fill()
                ctx.rectangle(sx - 40, sy - 62, 30, 16)
                ctx.rectangle(sx + 10, sy - 70, 30, 16)
                ctx.fill()
            else:
                ctx.set_source_rgb(*lit((0.55, 0.38, 0.2)))
                ctx.set_line_width(16)
                ctx.move_to(sx, sy)
                ctx.curve_to(sx + 10, sy - 90, sx + 30, sy - 160, sx + 40, sy - 210)
                ctx.stroke()
                ctx.set_source_rgb(*lit((0.2, 0.6, 0.3)))
                for ang in (-2.6, -2.0, -1.2, -0.5, 0.1):
                    ctx.save()
                    ctx.translate(sx + 40, sy - 210)
                    ctx.rotate(ang)
                    ctx.scale(1, 0.3)
                    ctx.arc(55, 0, 55, 0, 2 * math.pi)
                    ctx.restore()
                    ctx.fill()


def draw_weather(ctx, t):
    """Screen-space rain / snow on top of the world."""
    w = THEME["weather"]
    if w == "rain":
        rng = np.random.default_rng(3)
        ctx.set_source_rgba(0.85, 0.9, 1.0, 0.45)
        ctx.set_line_width(3)
        for i in range(140):
            x0, y0, sp = rng.uniform(0, W + 300), rng.uniform(0, H), rng.uniform(1600, 2300)
            y = (y0 + t * sp) % (H + 100) - 50
            x = (x0 - t * sp * 0.25) % (W + 300) - 150
            ctx.move_to(x, y)
            ctx.line_to(x - 12, y + 48)
        ctx.stroke()
    elif w == "snow":
        rng = np.random.default_rng(4)
        ctx.set_source_rgba(1, 1, 1, 0.9)
        for i in range(160):
            x0, y0, sp, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(80, 180), rng.uniform(3, 8)
            y = (y0 + t * sp) % (H + 40) - 20
            x = (x0 + 30 * math.sin(t * 1.3 + i)) % W
            ctx.arc(x, y, r, 0, 2 * math.pi)
            ctx.fill()
    tint = th_time().get("tint")
    if tint:
        ctx.set_source_rgba(*tint)
        ctx.paint()


def draw_track(ctx, view0, view1, t=0.0):
    gc = lit(th_loc()["ground"])
    for x0, x1, d in PITS:
        ctx.rectangle(x0, -d, x1 - x0, d)
        ctx.set_source_rgb(*shade(gc, 0.48))
        ctx.fill()
    poly(ctx, TRACK + [(170, -40), (-40, -40)])
    ctx.set_source_rgb(*gc)
    ctx.fill()
    for depth, col in [(-6.0, shade(gc, 0.86)), (-8.0, shade(gc, 0.76)), (-10.5, lit((0.52, 0.5, 0.5)))]:
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
            ctx.set_source_rgb(*shade(gc, k))
            ctx.fill()
    for x0, x1, d in PITS:
        if PIT_KIND == "lava":                                  # glowing lava pool with bubbles
            glow = cairo.LinearGradient(0, -d, 0, 0)
            glow.add_color_stop_rgba(0, 1, 0.45, 0.05, 0.8)
            glow.add_color_stop_rgba(1, 1, 0.3, 0.0, 0.0)
            ctx.rectangle(x0, -d, x1 - x0, d)
            ctx.set_source(glow)
            ctx.fill()
            lg = cairo.LinearGradient(0, -d, 0, -d + 1.3)
            lg.add_color_stop_rgb(0, 0.95, 0.25, 0.02)
            lg.add_color_stop_rgb(1, 1.0, 0.75, 0.1)
            ctx.rectangle(x0, -d, x1 - x0, 1.3)
            ctx.set_source(lg)
            ctx.fill()
            for j in range(int((x1 - x0) / 0.7)):
                ph = (t * 1.3 + j * 0.37) % 1.0
                ctx.arc(x0 + 0.35 + j * 0.7, -d + 1.3 + ph * 0.25, 0.12 + 0.12 * ph, 0, 2 * math.pi)
                ctx.set_source_rgba(1, 0.9, 0.3, 1 - ph)
                ctx.fill()
            continue
        if PIT_KIND == "water":                                 # deep pool behind the car
            sy = pit_surface(d)
            wg = cairo.LinearGradient(0, -d, 0, sy)
            wg.add_color_stop_rgb(0, *lit((0.05, 0.2, 0.42)))
            wg.add_color_stop_rgb(1, *lit((0.2, 0.5, 0.85)))
            ctx.rectangle(x0, -d, x1 - x0, sy + d)
            ctx.set_source(wg)
            ctx.fill()
            continue
        ctx.rectangle(x0, -d, x1 - x0, 0.55)
        ctx.set_source_rgb(*shade(gc, 0.68))
        ctx.fill()
        for j in range(int((x1 - x0) / 0.8)):
            ctx.arc(x0 + 0.4 + j * 0.8, -d + 0.55, 0.22, 0, math.pi)
            ctx.fill()
    ramp_x = [(a0, a1) for a0, a1, _ in RAMPS]
    for a, b in zip(TRACK, TRACK[1:]):
        if min(a[1], b[1]) < -0.01 or abs(a[0] - b[0]) < 1e-6:
            continue
        mid = (a[0] + b[0]) / 2
        if any(x0 <= mid <= x1 for x0, x1, _ in BUMPS) or any(x0 <= mid <= x1 for x0, x1 in ramp_x):
            continue
        if abs(a[1]) > 0.01 or abs(b[1]) > 0.01:                 # hill slopes: road band follows the slope
            poly(ctx, [a, b, (b[0], b[1] - 0.55), (a[0], a[1] - 0.55)])
            ctx.set_source_rgb(*lit((0.26, 0.26, 0.3)))
            ctx.fill()
            ctx.move_to(*a)
            ctx.line_to(*b)
            ctx.set_source_rgb(*lit((0.4, 0.4, 0.45)))
            ctx.set_line_width(0.1)
            ctx.stroke()
            continue
        poly(ctx, [a, b, (b[0], b[1] - 0.55), (a[0], a[1] - 0.55)])
        ctx.set_source_rgb(*lit((0.26, 0.26, 0.3)))
        ctx.fill()
        wet = THEME["weather"] == "rain"
        ctx.set_source_rgb(*lit((0.62, 0.66, 0.75) if wet else (0.4, 0.4, 0.45)))
        ctx.rectangle(a[0], -0.08, b[0] - a[0], 0.08)
        ctx.fill()
        if THEME["weather"] == "snow":                          # snow banks on the road edge
            ctx.set_source_rgb(0.96, 0.97, 1.0)
            ctx.rectangle(a[0], -0.55, b[0] - a[0], 0.12)
            ctx.fill()
        ctx.set_source_rgb(1, 1, 1)
        x = math.ceil(a[0] / 3.0) * 3.0
        while x + 1.5 <= b[0]:
            ctx.rectangle(x, -0.33, 1.5, 0.09)
            ctx.fill()
            x += 3.0
    for x0, x1, d in PITS:
        for xe, sgn in [(x0, -1), (x1, 1)]:
            if any(abs(xe - r1) < 1e-6 for _, r1, _ in RAMPS):
                continue
            poly(ctx, [(xe, 0), (xe, -0.55), (xe + sgn * 0.25, -0.35), (xe + sgn * 0.12, -0.2),
                       (xe + sgn * 0.3, 0)])
            ctx.set_source_rgb(0.28, 0.17, 0.1)
            ctx.fill()
    for x0, x1 in PUDDLES:                                       # water on the road (follows slopes)
        if x1 < view0 - 1 or x0 > view1 + 1:
            continue
        pts, x = [], x0
        while x <= x1 + 1e-6:
            pts.append((x, ground_h(x)))
            x += 0.25
        ctx.new_path()
        ctx.move_to(pts[0][0], pts[0][1] + 0.02)
        for px, py in pts:
            ctx.line_to(px, py + 0.1)
        for px, py in reversed(pts):
            ctx.line_to(px, py - 0.2)
        ctx.close_path()
        ctx.set_source_rgba(*lit((0.35, 0.65, 1.0)), 0.85)
        ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.7)                        # shimmer
        ctx.set_line_width(0.05)
        for k in range(int((x1 - x0) / 1.2)):
            sx = x0 + 0.4 + k * 1.2 + 0.3 * math.sin(t * 3 + k)
            ctx.move_to(sx, ground_h(sx) + 0.05)
            ctx.line_to(sx + 0.4, ground_h(sx + 0.4) + 0.05)
            ctx.stroke()
    for bx, bwid, bh in BARRIERS:                                # concrete wall, red/white warning stripes
        rrect(ctx, bx, 0, bwid, bh, 0.08)
        fill_stroke(ctx, lit((0.75, 0.75, 0.78)), lw=0.06)
        ctx.save()
        rrect(ctx, bx, bh - 0.45, bwid, 0.35, 0.05)
        ctx.clip()
        k = 0
        sx = bx - 0.5
        while sx < bx + bwid + 0.5:
            poly(ctx, [(sx, bh - 0.45), (sx + 0.25, bh - 0.45), (sx + 0.6, bh - 0.1), (sx + 0.35, bh - 0.1)])
            ctx.set_source_rgb(*((0.9, 0.15, 0.15) if k % 2 else (1, 1, 1)))
            ctx.fill()
            sx += 0.25
            k += 1
        ctx.restore()
    for vent in VENTS:                                           # glowing crack in the road
        vx = vent["x"]
        heat = 0.6 + 0.4 * math.sin(t * 6)
        poly(ctx, [(vx - 0.9, 0.02), (vx - 0.4, -0.3), (vx, 0.0), (vx + 0.35, -0.35), (vx + 0.9, 0.02)])
        ctx.set_source_rgb(1, 0.45 + 0.3 * heat, 0.05)
        ctx.fill()
    for rx0, rx1, rh in RAMPS:
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
    elif vk == "f1":
        rrect(ctx, -2.5, 0.55, 0.75, 0.14, 0.04)                 # rear wing
        fill_stroke(ctx, dark, lw=0.035)
        ctx.rectangle(-2.2, 0.2, 0.12, 0.36)
        ctx.set_source_rgb(0.15, 0.15, 0.18)
        ctx.fill()
        poly(ctx, [(-2.3, -0.22), (2.3, -0.22), (2.35, -0.08), (1.2, 0.04), (0.55, 0.22), (-1.7, 0.22), (-2.1, 0.08)])
        fill_stroke(ctx, c)
        ctx.rectangle(-1.6, -0.06, 2.6, 0.07)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        ctx.arc(-0.35, 0.42, 0.21, 0, 2 * math.pi)             # driver helmet
        fill_stroke(ctx, (1, 0.85, 0.1), lw=0.035)
        rrect(ctx, -0.3, 0.36, 0.2, 0.1, 0.03)
        ctx.set_source_rgb(0.1, 0.1, 0.15)
        ctx.fill()
        rrect(ctx, 1.85, -0.3, 0.7, 0.1, 0.03)                   # front wing
        fill_stroke(ctx, dark, lw=0.03)
        local_text(ctx, "1", -1.05, 0.03, 0.3, (1, 1, 1))
    elif vk == "taxi":
        poly(ctx, [(-1.35, 0.35), (0.65, 0.35), (0.15, 0.95), (-1.15, 0.95)])
        fill_stroke(ctx, c)
        poly(ctx, [(-1.2, 0.4), (0.48, 0.4), (0.08, 0.86), (-1.03, 0.86)])
        fill_stroke(ctx, glass, lw=0.03)
        ctx.set_source_rgb(0.1, 0.08, 0.12)
        ctx.set_line_width(0.05)
        ctx.move_to(-0.33, 0.4)
        ctx.line_to(-0.33, 0.86)
        ctx.stroke()
        rrect(ctx, -0.75, 0.95, 0.62, 0.22, 0.05)                # roof sign
        fill_stroke(ctx, (1, 1, 0.85), lw=0.03)
        local_text(ctx, "TAXI", -0.44, 1.06, 0.15, (0.1, 0.1, 0.1))
        poly(ctx, [(-2.15, -0.35), (2.15, -0.35), (2.15, 0.0), (1.75, 0.3), (0.75, 0.35), (-2.05, 0.35), (-2.15, 0.15)])
        fill_stroke(ctx, c)
        for i in range(16):                                     # checker stripe
            for j in range(2):
                ctx.rectangle(-1.9 + i * 0.23, -0.1 + j * 0.1, 0.23, 0.1)
                ctx.set_source_rgb(*(((0.1,) * 3) if (i + j) % 2 else (1, 1, 1)))
                ctx.fill()
        ctx.arc(2.0, 0.08, 0.09, 0, 2 * math.pi)
        fill_stroke(ctx, (1, 0.95, 0.4), lw=0.03)
    elif vk == "bigrig":
        rrect(ctx, -4.8, -0.9, 7.3, 2.05, 0.12)                  # trailer
        fill_stroke(ctx, (0.9, 0.9, 0.94), lw=0.07)
        for i in range(1, 7):
            ctx.move_to(-4.8 + i * 1.04, -0.9)
            ctx.line_to(-4.8 + i * 1.04, 1.15)
        ctx.set_source_rgb(0.75, 0.75, 0.8)
        ctx.set_line_width(0.04)
        ctx.stroke()
        local_text(ctx, "MEGA HAUL", -1.15, 0.15, 0.55, (0.12, 0.3, 0.7))
        ctx.rectangle(-4.8, -1.15, 9.6, 0.25)
        ctx.set_source_rgb(0.2, 0.2, 0.24)
        ctx.fill()
        ctx.rectangle(2.8, 0.85, 0.14, 0.75)                     # exhaust stack
        fill_stroke(ctx, (0.7, 0.7, 0.75), lw=0.03)
        poly(ctx, [(2.7, -1.1), (4.8, -1.1), (4.8, 0.2), (4.55, 1.0), (2.7, 1.0)])
        fill_stroke(ctx, c, lw=0.07)
        rrect(ctx, 3.55, 0.08, 1.0, 0.8, 0.1)
        fill_stroke(ctx, glass, lw=0.04)
        ctx.rectangle(4.62, -0.95, 0.16, 0.7)
        ctx.set_source_rgb(0.25, 0.25, 0.28)
        ctx.fill()
        ctx.arc(4.68, -0.12, 0.1, 0, 2 * math.pi)
        fill_stroke(ctx, (1, 0.95, 0.4), lw=0.03)
    elif vk == "icecream":
        ctx.move_to(-0.35, 1.95)                                 # giant cone on the roof
        ctx.line_to(0.35, 1.95)
        ctx.line_to(0.0, 1.05)
        ctx.close_path()
        fill_stroke(ctx, (0.85, 0.62, 0.3), lw=0.04)
        ctx.arc(0, 2.1, 0.42, 0, 2 * math.pi)
        fill_stroke(ctx, (1, 0.85, 0.9), lw=0.04)
        ctx.arc(0, 2.55, 0.12, 0, 2 * math.pi)
        fill_stroke(ctx, (0.9, 0.1, 0.2), lw=0.03)
        rrect(ctx, -2.8, -1.05, 5.6, 2.1, 0.3)
        ctx.set_source_rgb(*c)
        ctx.fill()
        ctx.save()                                              # lower stripe follows the rounded body corners
        rrect(ctx, -2.8, -1.05, 5.6, 2.1, 0.3)
        ctx.clip()
        ctx.rectangle(-2.8, -1.05, 5.6, 0.5)
        ctx.set_source_rgb(*v.get("accent", (0.6, 0.95, 0.8)))
        ctx.fill()
        ctx.restore()
        rrect(ctx, -2.8, -1.05, 5.6, 2.1, 0.3)
        ctx.set_source_rgb(0.07, 0.07, 0.12)
        ctx.set_line_width(0.08)
        ctx.stroke()
        rrect(ctx, -2.0, -0.15, 2.3, 0.8, 0.1)                   # serving window
        fill_stroke(ctx, glass, lw=0.05)
        for i in range(8):                                      # awning
            ctx.rectangle(-2.1 + i * 0.31, 0.68, 0.31, 0.22)
            ctx.set_source_rgb(*((1, 0.35, 0.55) if i % 2 else (1, 1, 1)))
            ctx.fill()
        rrect(ctx, 1.85, -0.05, 0.85, 0.8, 0.12)
        fill_stroke(ctx, glass, lw=0.05)
        local_text(ctx, "ICE CREAM", -0.85, -0.8, 0.34, (0.55, 0.1, 0.35))
        ctx.arc(2.65, -0.35, 0.1, 0, 2 * math.pi)
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


def draw_wheel(ctx, x, y, ang, r, monster, sx=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sx, 1.0)                                           # sx < 1: wheel seen at an angle (car spinning)
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


def yaw_scale(yaw):
    """Apparent length of a car turned by `yaw` around the vertical axis (negative = facing backwards)."""
    c = math.cos(yaw)
    return 1.0 if abs(yaw) < 1e-4 else math.copysign(max(abs(c), 0.16), c)


def melt_amount(L, st):
    """0..1 how far the body has melted in a lava pit."""
    if PIT_KIND != "lava" or L.get("sunk") is None or st < L["sunk"]:
        return 0.0
    return min(1.0, (st - L["sunk"]) / 2.2)


def draw_car(ctx, L, s, mood, st):
    vk, v = L["vk"], L["v"]
    cx, cy, ca, wheels = s["cx"], s["cy"] - s.get("sink", 0.0), s["ca"], s["wheels"]
    bw, bh = v["body"]
    sink = s.get("sink", 0.0)
    ys = yaw_scale(s.get("yaw", 0.0))
    co, sn = math.cos(ca), math.sin(ca)

    def squeeze(wx, wy):                                         # wheel position after the yaw squeeze
        dx, dy = wx - s["cx"], wy - s["cy"]
        along, perp = dx * co + dy * sn, -dx * sn + dy * co
        along *= ys
        return cx + along * co - perp * sn, cy + along * sn + perp * co

    si = st * REC_HZ
    clipped = sink > 0
    if clipped:                                                  # sinking car never pokes out below the pit floor
        pit = next(((a, b, dd) for a, b, dd in PITS if a <= s["cx"] <= b), None)
        if pit:
            ctx.save()
            ctx.rectangle(pit[0] - 50, -pit[2], pit[1] - pit[0] + 100, 200)
            ctx.clip()
        else:
            clipped = False
    ctx.set_source_rgb(0.3, 0.3, 0.34)
    ctx.set_line_width(0.14)
    for wi, ((wx, wy, _), lx) in enumerate(zip(wheels, v["wheel_x"])):
        det = L["detached"][wi]
        if det is not None and si >= det:
            continue
        lx *= ys
        ax = cx + co * lx - sn * (-bh / 2)
        ay = cy + sn * lx + co * (-bh / 2)
        ctx.move_to(ax, ay)
        ctx.line_to(*squeeze(wx, wy - sink))
        ctx.stroke()
    for wi, (wx, wy, wa) in enumerate(wheels):
        det = L["detached"][wi]
        px, py = squeeze(wx, wy - sink) if det is None or si < det else (wx, wy)
        draw_wheel(ctx, px, py, wa, v["wheel_r"], vk.startswith("monster"),
                   sx=max(0.3, abs(ys)) if det is None or si < det else 1.0)
    broken = L["broken"] is not None and st >= L["broken"]["t"]
    melt = melt_amount(L, st)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(ca)
    ctx.scale(ys, 1.0)
    if melt > 0:                                                 # sagging, softening body
        ctx.translate(0, -bh / 2)
        ctx.scale(1 + 0.08 * melt, 1 - 0.32 * melt)
        ctx.translate(0, bh / 2)
    ctx.push_group()
    draw_body(ctx, vk, v, broken, st)
    draw_face(ctx, vk, mood, st)
    burned = L.get("burned") is not None and st >= L["burned"]
    if burned or melt > 0:
        ctx.set_operator(cairo.OPERATOR_ATOP)                     # paint only on the car's own pixels
        top = bh / 2 + 1.4
        g = cairo.LinearGradient(0, -bh / 2, 0, top)
        if melt > 0:                                             # red-hot bottom, charred top
            g.add_color_stop_rgba(0, 1.0, 0.5, 0.05, 0.95 * melt)
            g.add_color_stop_rgba(0.45, 0.85, 0.2, 0.02, 0.75 * melt)
            g.add_color_stop_rgba(1, 0.12, 0.07, 0.05, 0.25 + 0.55 * melt)
        else:
            g.add_color_stop_rgba(0, 0.1, 0.07, 0.06, 0.55)
            g.add_color_stop_rgba(1, 0.1, 0.07, 0.06, 0.25)
        ctx.set_source(g)
        ctx.paint()
        rng = np.random.default_rng(17)
        for _ in range(14):                                      # soot blotches
            ctx.arc(rng.uniform(-bw / 2, bw / 2), rng.uniform(-bh / 2, bh / 2 + 0.6), rng.uniform(0.15, 0.45),
                    0, 2 * math.pi)
            ctx.set_source_rgba(0.08, 0.06, 0.06, 0.5)
            ctx.fill()
        if melt > 0:                                             # molten metal running down the body
            for k in range(7):
                x = -bw / 2 + (k + 0.5) * bw / 7 + 0.15 * math.sin(k * 2.3)
                y0 = bh / 2 + 1.2
                ln = (0.6 + 0.5 * ((k * 37) % 5) / 5) * (bh + 1.3) * melt
                w = 0.09 + 0.05 * (k % 3)
                ctx.move_to(x - w, y0)
                ctx.line_to(x - w, y0 - ln)
                ctx.arc_negative(x, y0 - ln, w, math.pi, 0)
                ctx.line_to(x + w, y0)
                ctx.close_path()
                ctx.set_source_rgba(1.0, 0.62 + 0.2 * math.sin(st * 6 + k), 0.12, 0.9)
                ctx.fill()
        ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.pop_group_to_source()
    ctx.paint()
    if melt > 0:                                                 # glowing drips hanging off the chassis
        for k in range(5):
            x = -bw / 2 + (k + 0.7) * bw / 5.5
            ln = (0.15 + 0.35 * ((k * 53) % 7) / 7) * melt * (1 + 0.25 * math.sin(st * 3 + k))
            ctx.move_to(x - 0.08, -bh / 2 + 0.05)
            ctx.curve_to(x - 0.08, -bh / 2 - ln * 0.6, x - 0.13, -bh / 2 - ln, x, -bh / 2 - ln - 0.1)
            ctx.curve_to(x + 0.13, -bh / 2 - ln, x + 0.08, -bh / 2 - ln * 0.6, x + 0.08, -bh / 2 + 0.05)
            ctx.close_path()
            ctx.set_source_rgba(1, 0.55, 0.08, 0.95)
            ctx.fill()
    ctx.restore()
    if clipped:
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
    smoke_t = min([x for x in ((b or {}).get("t"), L.get("burned")) if x is not None], default=None)
    if smoke_t is not None and st >= smoke_t:
        dark = 0.3 if L.get("burned") else 0.55                 # lava = thick black smoke
        k = 0                              # smoke puffs from the wreck
        while True:
            ts = smoke_t + k * 0.18
            if ts > st:
                break
            pa = st - ts
            if pa < 1.8:
                p = car_state(L, ts)
                x = p["cx"] + 0.3 * pa + 0.2 * math.sin(k * 1.7)
                y = p["cy"] + 0.4 + 1.3 * pa
                ctx.arc(x, y, 0.25 + 0.45 * pa, 0, 2 * math.pi)
                ctx.set_source_rgba(dark, dark, dark + 0.03, 0.55 * (1 - pa / 1.8))
                ctx.fill()
            k += 1
    if PUDDLES:
        draw_water_spray(ctx, L, st)
    for sp in splash_events(L):
        if 0 <= st - sp["t"] < 1.6:
            (draw_lava_splash if sp["kind"] == "lava" else draw_water_splash)(ctx, sp, st - sp["t"])
    ev = L["event"]
    if ev["type"] != "win" and st >= ev["t"] + 0.4:   # dizzy stars
        top = s["cy"] + L["v"]["body"][1] / 2 + 1.0
        for k in range(3):
            a = st * 4 + k * 2 * math.pi / 3
            star(ctx, s["cx"] + math.cos(a) * 0.9, top + math.sin(a) * 0.22, 0.2, a)
            fill_stroke(ctx, (1, 0.88, 0.2), lw=0.03)


def draw_pit_front(ctx, L, s, st):
    """Liquid in front of the car: opaque lava hides the sunk part, water is see-through."""
    if PIT_KIND not in PIT_FILL:
        return
    for x0, x1, d in PITS:
        sy = pit_surface(d)
        ctx.new_path()
        ctx.move_to(x0, -d - 0.1)
        x = x0
        while x <= x1 + 1e-6:
            wave = 0.06 * math.sin(x * 2.1 + st * (1.6 if PIT_KIND == "lava" else 4.0))
            ctx.line_to(x, sy + wave)
            x += 0.2
        ctx.line_to(x1, -d - 0.1)
        ctx.close_path()
        if PIT_KIND == "lava":
            g = cairo.LinearGradient(0, -d, 0, sy)
            g.add_color_stop_rgb(0, 0.8, 0.15, 0.02)
            g.add_color_stop_rgb(0.7, 1.0, 0.45, 0.05)
            g.add_color_stop_rgb(1, 1.0, 0.8, 0.2)
            ctx.set_source(g)
            ctx.fill()
            for j in range(int((x1 - x0) / 0.9)):               # crust plates drifting on the lava
                px = x0 + 0.4 + ((j * 0.9 + st * 0.25) % (x1 - x0 - 0.6))
                ctx.save()
                ctx.translate(px, sy - 0.12)
                ctx.scale(0.32, 0.07)
                ctx.arc(0, 0, 1, 0, 2 * math.pi)
                ctx.restore()
                ctx.set_source_rgba(0.35, 0.08, 0.03, 0.55)
                ctx.fill()
        else:
            ctx.set_source_rgba(*lit((0.25, 0.6, 1.0)), 0.45)
            ctx.fill()
            ctx.set_source_rgba(1, 1, 1, 0.6)
            ctx.set_line_width(0.06)
            ctx.move_to(x0, sy)
            ctx.line_to(x1, sy)
            ctx.stroke()
    if L.get("sunk") is None or st < L["sunk"]:
        return
    age = st - L["sunk"]
    x0, x1, d = next(((a, b, dd) for a, b, dd in PITS if a <= s["cx"] <= b), (None, None, None))
    if x0 is None:
        return
    sy = pit_surface(d)
    if PIT_KIND == "lava":                                       # glowing ring where the car meets the lava
        rg = cairo.RadialGradient(s["cx"], sy, 0.2, s["cx"], sy, L["v"]["body"][0] * 0.8)
        rg.add_color_stop_rgba(0, 1, 0.95, 0.4, 0.8)
        rg.add_color_stop_rgba(1, 1, 0.5, 0.05, 0.0)
        ctx.save()
        ctx.translate(0, 0)
        ctx.rectangle(x0, sy - 0.6, x1 - x0, 1.2)
        ctx.clip()
        ctx.arc(s["cx"], sy, L["v"]["body"][0] * 0.8, 0, 2 * math.pi)
        ctx.set_source(rg)
        ctx.fill()
        ctx.restore()
    else:                                                        # air bubbles escaping from the sunk car
        rng = np.random.default_rng(29)
        for j in range(18):
            t0 = j * 0.22
            a = age - t0
            if a < 0 or a > 1.6 or age > 5.0:
                continue
            bx = s["cx"] + rng.uniform(-1.2, 1.2) + 0.1 * math.sin(a * 9 + j)
            by = s["cy"] + a * 2.2
            if by > sy:
                continue
            ctx.arc(bx, by, 0.07 + 0.06 * (j % 3), 0, 2 * math.pi)
            ctx.set_source_rgba(0.85, 0.95, 1.0, 0.8)
            ctx.set_line_width(0.03)
            ctx.stroke()


SPRAY_DT = 0.025     # emission step of the tyre spray (fixed grid -> particles stay stable between frames)


def splash_events(L):
    """Cached: every moment something hits liquid -> dict(t, x, y, speed, kind, big)."""
    if "_splashes" in L:
        return L["_splashes"]
    out, rec = [], L["rec"]
    n = len(rec["cx"])
    for x0, x1 in PUDDLES:                                       # front wheel enters each puddle
        for i in range(n):
            wx, wy, _ = rec["wheels"][i][-1]
            if x0 <= wx <= x1 and rec["speed"][i] > 1.5:
                out.append(dict(t=i / REC_HZ, x=wx, y=ground_h(wx), speed=float(rec["speed"][i]),
                                kind="water", big=False))
                break
    if L.get("sunk") is not None:                                 # plunge into a pit
        i = min(n - 1, int(L["sunk"] * REC_HZ))
        d = next((dd for a, b, dd in PITS if a <= rec["cx"][i] <= b), 3.0)
        prev = max(0, i - 3)
        vy = abs(rec["cy"][i] - rec["cy"][prev]) * REC_HZ / 3
        out.append(dict(t=L["sunk"], x=float(rec["cx"][i]), y=pit_surface(d), speed=max(6.0, vy),
                        kind="lava" if PIT_KIND == "lava" else "water", big=True))
    L["_splashes"] = out
    return out


def draw_water_spray(ctx, L, st):
    """Rooster-tail spray + mist thrown by every tyre that is in the water (direction follows the yaw)."""
    r = L["v"]["wheel_r"]
    k0 = int(st / SPRAY_DT)
    for k in range(k0, max(-1, k0 - int(0.75 / SPRAY_DT)), -1):
        te = k * SPRAY_DT
        age = st - te
        p = car_state(L, te)
        if p["speed"] < 1.5:
            continue
        back = -yaw_scale(p["yaw"]) if abs(p["yaw"]) > 1e-3 else -1.0
        spin = abs(p["yaw"]) > 0.4
        for wi, (wx, wy, _) in enumerate(p["wheels"]):
            if not in_puddle(wx) or wy - r > ground_h(wx) + 0.25:
                continue
            gy = ground_h(wx)
            rng = np.random.default_rng(k * 13 + wi)
            sp = p["speed"]
            for j in range(4):                                   # droplets / streaks
                dirx = back if not spin else rng.uniform(-1, 1)
                vx = sp * 0.35 + dirx * (1.5 + 0.3 * sp) + rng.uniform(-1.0, 1.0)
                vy = 1.6 + 0.22 * sp + rng.uniform(-0.6, 1.4)
                x = wx + dirx * r * 0.8 + vx * age
                y = gy + vy * age - 4.9 * age * age
                if y < ground_h(x) - 0.05:
                    continue
                a = 0.9 * (1 - age / 0.75)
                if j == 0:
                    ctx.move_to(x, y)
                    ctx.line_to(x - vx * 0.05, y - (vy - 9.8 * age) * 0.05)
                    ctx.set_source_rgba(0.85, 0.95, 1.0, a)
                    ctx.set_line_width(0.06)
                    ctx.stroke()
                else:
                    ctx.arc(x, y, 0.05 + 0.04 * j * rng.uniform(0.5, 1.0), 0, 2 * math.pi)
                    ctx.set_source_rgba(0.62, 0.84, 1.0, a)
                    ctx.fill()
            if k % 3 == 0:                                       # soft mist behind the tyre
                mx = wx + back * (0.5 + 1.2 * age) + sp * 0.2 * age
                ctx.arc(mx, gy + 0.3 + 0.8 * age, 0.3 + 0.9 * age, 0, 2 * math.pi)
                ctx.set_source_rgba(0.92, 0.97, 1.0, 0.22 * (1 - age / 0.75))
                ctx.fill()
    for sp in splash_events(L):                                  # ripples on the puddle surface
        a = st - sp["t"]
        if sp["kind"] == "water" and not sp["big"] and 0 <= a < 1.5:
            for q in range(3):
                aa = a - q * 0.18
                if aa <= 0:
                    continue
                ctx.save()
                ctx.translate(sp["x"], sp["y"] + 0.03)
                ctx.scale(0.4 + 2.2 * aa, 0.1 + 0.25 * aa)
                ctx.arc(0, 0, 1, 0, 2 * math.pi)
                ctx.restore()
                ctx.set_source_rgba(1, 1, 1, 0.6 * (1 - aa / 1.5))
                ctx.set_line_width(0.04)
                ctx.stroke()


def draw_water_splash(ctx, sp, age):
    """Crown splash: two curved water sheets + a fan of droplets + mist."""
    big = 1.8 if sp["big"] else 1.0
    s = big * (0.6 + 0.06 * sp["speed"])
    x, y = sp["x"], sp["y"]
    up = math.sin(math.pi * min(1.0, age / 0.8))
    if age < 0.8:
        for side in (-1, 1):
            h = 1.6 * s * up
            w0, w1 = 0.3 * s, (0.9 + 1.4 * age) * s
            ctx.move_to(x + side * w0, y)
            ctx.curve_to(x + side * w0 * 1.2, y + h * 0.6, x + side * w1 * 0.8, y + h, x + side * w1, y + h * 0.9)
            ctx.curve_to(x + side * w1 * 0.9, y + h * 0.6, x + side * w0 * 2.2, y + h * 0.3, x + side * w0 * 2.4, y)
            ctx.close_path()
            g = cairo.LinearGradient(0, y, 0, y + h + 0.01)
            g.add_color_stop_rgba(0, 0.55, 0.8, 1.0, 0.85 * (1 - age / 0.8))
            g.add_color_stop_rgba(1, 1, 1, 1, 0.95 * (1 - age / 0.8))
            ctx.set_source(g)
            ctx.fill()
    rng = np.random.default_rng(int(x * 100))
    for j in range(int(28 * big)):
        vx, vy = rng.uniform(-5, 5) * s, rng.uniform(3, 8) * math.sqrt(s)
        px, py = x + vx * age, y + vy * age - 4.9 * age * age
        if py < y - 0.05:
            continue
        ctx.arc(px, py, rng.uniform(0.05, 0.14) * (1 + 0.3 * big), 0, 2 * math.pi)
        ctx.set_source_rgba(0.65, 0.87, 1.0, max(0.0, 0.95 - age / 1.6))
        ctx.fill()
    for j in range(5):
        ctx.arc(x + (j - 2) * 0.5 * s, y + 0.4 * s + age * 1.2, (0.4 + 1.1 * age) * s, 0, 2 * math.pi)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.18 * max(0.0, 1 - age / 1.4))
        ctx.fill()


def draw_lava_splash(ctx, sp, age):
    """Heavy, slow lava blobs thrown up by a car plunging in, plus a hot flash."""
    x, y = sp["x"], sp["y"]
    if age < 0.35:
        rg = cairo.RadialGradient(x, y, 0.1, x, y, 3.5)
        rg.add_color_stop_rgba(0, 1, 0.95, 0.5, 0.8 * (1 - age / 0.35))
        rg.add_color_stop_rgba(1, 1, 0.5, 0.05, 0.0)
        ctx.arc(x, y, 3.5, 0, 2 * math.pi)
        ctx.set_source(rg)
        ctx.fill()
    rng = np.random.default_rng(int(x * 100) + 5)
    for j in range(22):
        vx, vy = rng.uniform(-3.2, 3.2), rng.uniform(2.5, 6.0)
        px, py = x + vx * age, y + vy * age - 3.5 * age * age        # thick blobs: short, slow arcs
        if py < y - 0.1:
            continue
        rad = rng.uniform(0.12, 0.3)
        ctx.save()
        ctx.translate(px, py)
        ctx.rotate(math.atan2(vy - 7 * age, vx))
        ctx.scale(1.35, 0.85)
        ctx.arc(0, 0, rad, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.95, 0.35, 0.03)
        ctx.fill_preserve()
        ctx.set_source_rgba(1, 0.85, 0.3, 0.8)
        ctx.set_line_width(0.04)
        ctx.stroke()


def _flame(ctx, x, y, w, h, sway, cols):
    for (r, g, b, a), k in zip(cols, (1.0, 0.62, 0.32)):
        ww, hh = w * k, h * (0.35 + 0.65 * k)
        ctx.move_to(x - ww, y)
        ctx.curve_to(x - ww, y + hh * 0.45, x - ww * 0.25 + sway * 0.5, y + hh * 0.7, x + sway, y + hh)
        ctx.curve_to(x + ww * 0.25 + sway * 0.5, y + hh * 0.7, x + ww, y + hh * 0.45, x + ww, y)
        ctx.arc_negative(x, y, ww, 0, math.pi)
        ctx.close_path()
        ctx.set_source_rgba(r, g, b, a)
        ctx.fill()


def draw_fire(ctx, L, s, st):
    """Cartoon flames + rising embers on a car hit by lava (bigger when it sank into a lava pit)."""
    if L.get("burned") is None or st < L["burned"]:
        return
    age = st - L["burned"]
    sunk = L.get("sunk") is not None and PIT_KIND == "lava"
    size = (1.0 if sunk else 0.7) * min(1.0, age / 0.25)
    v = L["v"]
    bw, bh = v["body"]
    ys = abs(yaw_scale(s.get("yaw", 0.0)))
    cx, cy, ca = s["cx"], s["cy"] - s.get("sink", 0.0), s["ca"]
    top = bh / 2 + (0.5 if v["cabin"] else 0.1)
    n = max(3, int(bw / 0.55))
    glow = cairo.RadialGradient(cx, cy + top, 0.3, cx, cy + top + 0.8, bw * 0.9)
    glow.add_color_stop_rgba(0, 1, 0.6, 0.15, 0.35 * size)
    glow.add_color_stop_rgba(1, 1, 0.4, 0.05, 0.0)
    ctx.arc(cx, cy + top + 0.8, bw * 0.9, 0, 2 * math.pi)
    ctx.set_source(glow)
    ctx.fill()
    cols = [(0.95, 0.25, 0.03, 0.9), (1.0, 0.6, 0.08, 0.95), (1.0, 0.93, 0.5, 1.0)]
    for k in range(n):
        lx = (k / (n - 1) - 0.5) * bw * 0.85 * ys
        ly = top * (0.7 if k in (0, n - 1) else 1.0)
        bx, by = cx + math.cos(ca) * lx - math.sin(ca) * ly, cy + math.sin(ca) * lx + math.cos(ca) * ly
        h = size * (1.0 + 0.35 * math.sin(st * 11 + k * 1.7) + 0.2 * math.sin(st * 23 + k * 0.9)) \
            * (1.25 if 0 < k < n - 1 else 0.8)
        _flame(ctx, bx, by, 0.28 * size + 0.05, h, 0.18 * math.sin(st * 7 + k), cols)
    for j in range(16):                                          # embers drifting up
        ph = (st * 0.8 + j * 0.137) % 1.0
        ex = cx + (((j * 0.61) % 1.0) - 0.5) * bw + 0.4 * math.sin(st * 3 + j)
        ey = cy + top + ph * 3.5
        ctx.arc(ex, ey, 0.05, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 0.7, 0.2, (1 - ph) * size)
        ctx.fill()


def draw_eruptions(ctx, st):
    """Lava fountains from the vents (drawn in world space, in front of the car)."""
    FALL = 0.9                                                   # visual tail after the dangerous window
    for vent in VENTS:
        ph = (st + vent["phase"]) % vent["period"]
        vx = vent["x"]
        if ph < vent["dur"] + FALL:
            a = ph / vent["dur"]
            rise = min(1.0, ph / (vent["dur"] * 0.35))
            fall = 1.0 if ph < vent["dur"] else max(0.0, 1 - (ph - vent["dur"]) / FALL)
            top = vent["height"] * rise * fall
            rg = cairo.RadialGradient(vx, top * 0.4, 0.2, vx, top * 0.4, max(1.0, top * 0.8))
            rg.add_color_stop_rgba(0, 1, 0.6, 0.1, 0.55)
            rg.add_color_stop_rgba(1, 1, 0.3, 0.0, 0.0)
            ctx.arc(vx, top * 0.4, max(1.0, top * 0.8), 0, 2 * math.pi)
            ctx.set_source(rg)
            ctx.fill()
            rng = np.random.default_rng(int(vx * 10))
            for j in range(26):
                h = top * (j / 26)
                wob = 0.25 * math.sin(st * 20 + j) + rng.uniform(-0.2, 0.2)
                ctx.arc(vx + wob, h, 0.45 - 0.25 * (j / 26), 0, 2 * math.pi)
                ctx.set_source_rgb(1, 0.35 + 0.5 * (j / 26), 0.05)
                ctx.fill()
            for j in range(10):                                  # flying blobs
                bt = (a + j * 0.1) % 1.0
                bx = vx + (j - 5) * 0.5 * bt * 2
                by = top * 0.8 * (1 - (2 * bt - 1) ** 2) + 0.5
                ctx.arc(bx, by, 0.18, 0, 2 * math.pi)
                ctx.set_source_rgb(1, 0.55, 0.1)
                ctx.fill()
        elif vent["period"] - ph < 0.5:                          # rumble warning: bubbling
            w = 1 - (vent["period"] - ph) / 0.5
            for j in range(4):
                ctx.arc(vx - 0.5 + j * 0.33, 0.1 + 0.3 * w * ((j + int(st * 10)) % 2), 0.12 + 0.1 * w,
                        0, 2 * math.pi)
                ctx.set_source_rgba(1, 0.5, 0.1, 0.8)
                ctx.fill()


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
        draw_text(ctx, CHANNEL.upper(), 0, 140, 58, fill=(1, 1, 1), stroke=(0.1, 0.1, 0.3))
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
    spans = OBST_SPANS
    ok_obs = len(spans) >= 2 and all(START_X < x0 < x1 < FINISH_X for x0, x1 in spans)
    kinds = ", ".join(k for _, k in OBSTACLES) if OBSTACLES else "?"
    res.append(check("obstacles", "Minimal 2 rintangan di antara start dan finish", ok_obs,
                     f"{len(spans)} rintangan [{kinds}] ({spans[0][0]:.0f}-{spans[-1][1]:.0f} m), finish {FINISH_X:.0f} m"
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
    res.append(check("duration", "Durasi total 40-58 s", 40 <= total <= 58, f"{total:.1f} s"))
    lens_ok = all(L["dur"] <= level_cap(L) for L in LEVELS)
    d = SERIES_DEFS[SERIES]
    res.append(check("level_len", f"Level gagal <= {d['max_fail']:.0f} s, level menang (+outro) <= {d['max_win']:.0f} s",
                     lens_ok,
                     ", ".join(f"{L['dur']:.1f}s" for L in LEVELS)))
    return res


def video_description():
    """YouTube description template (general audience, no 'kids' wording). BLUEPRINT rule 7."""
    nicks = [f"{VEHICLES[vk]['nick']} the {VEHICLES[vk]['display'].split(' THE ', 1)[1].lower()}" for vk, _ in STORY]
    obst = SERIES_DEFS[SERIES]["obst"].upper()
    return (f"{nicks[0]}, {nicks[1]} and {nicks[2]} take on the {obst}! 💥 "
            f"Only one makes it to the finish line. Who's your pick? 🏁\n\n"
            "Watch till the end for the slow-motion replay! 🎬\n\n"
            "🏆 Comment your champion below!\n"
            f"🔔 Subscribe to {CHANNEL} for new car challenges every week.\n\n"
            "#Shorts #CarCrash #CrashTest #PhysicsSimulation #MonsterTruck #MegaWheelArena")


def outcome_tags():
    return [("win" if L["event"]["type"] == "win" else
             f"{L['event']['type']}@obs{L['event']['obstacle']}" + ("+broken" if L["broken"] else ""))
            for L in LEVELS]


# ================================================================ frames
LEVELS = []
INDEX = []          # global frame -> (level, local output frame)


def zoom_punch(L, st):
    """Quick camera push-in on hard impacts."""
    k = 1.0
    for ti, s, _, _ in L["impacts"]:
        a = st - ti
        if 0 <= a < 0.8 and s > 0.45:
            k += 0.12 * s * math.exp(-a / 0.22)
    return k


def draw_headlights(ctx, L, s):
    v = L["v"]
    bw = v["body"][0]
    ctx.save()
    ctx.translate(s["cx"], s["cy"] - s.get("sink", 0.0))
    ctx.rotate(s["ca"])
    ctx.scale(yaw_scale(s.get("yaw", 0.0)), 1.0)
    lg = cairo.LinearGradient(bw / 2, 0, bw / 2 + 7, 0)
    lg.add_color_stop_rgba(0, 1, 0.95, 0.6, 0.55)
    lg.add_color_stop_rgba(1, 1, 0.95, 0.6, 0)
    poly(ctx, [(bw / 2 - 0.1, -0.05), (bw / 2 + 7, -1.3), (bw / 2 + 7, 1.1), (bw / 2 - 0.1, 0.15)])
    ctx.set_source(lg)
    ctx.fill()
    ctx.restore()


def draw_ready_go(ctx, tl):
    """READY... GO! pop at the start of every level."""
    g = READY_GO_T
    for t0, t1, text, col in ((0.0, g, "READY...", (1, 0.86, 0.12)), (g, g + 0.55, "GO!", (0.3, 1, 0.4))):
        if t0 <= tl < t1:
            a = (tl - t0) / (t1 - t0)
            sc = ease_out_back(min(1.0, a / 0.35))
            ctx.save()
            ctx.translate(540, 780)
            ctx.scale(sc, sc)
            draw_text(ctx, text, 0, 0, 150 if text == "GO!" else 110, fill=col, stroke=(0.07, 0.07, 0.2),
                      alpha=max(0.0, min(1.0, (1 - a) / 0.25)))
            ctx.restore()


def draw_frame(ctx, g):
    li, j = INDEX[g]
    L = LEVELS[li]
    st, mode = L["frames"][j]
    tl = j / FPS
    camx, camy, z = L["cam"][j]
    z *= zoom_punch(L, st)
    shx, shy = shake_offset(L, st)
    s = car_state(L, st)
    draw_sky(ctx, camx, camy, z)
    ctx.save()
    ctx.translate(540 + shx, GROUND_Y + shy)
    ctx.scale(S * z, -S * z)
    ctx.translate(-camx, -camy)
    half = 540 / (S * z) + 2
    draw_track(ctx, camx - half, camx + half, st)
    draw_shadow(ctx, L, s)
    draw_dust(ctx, L["impacts"], st)
    draw_debris(ctx, L, st)
    draw_car(ctx, L, s, mood_at(L, st, s), st)
    draw_pit_front(ctx, L, s, st)
    draw_fire(ctx, L, s, st)
    draw_eruptions(ctx, st)
    draw_effects(ctx, L, s, st)
    ctx.restore()
    draw_weather(ctx, g / FPS)                                  # rain/snow + time-of-day tint
    if "moon" in th_time():                                    # headlights glow above the night tint
        ctx.save()
        ctx.translate(540 + shx, GROUND_Y + shy)
        ctx.scale(S * z, -S * z)
        ctx.translate(-camx, -camy)
        draw_headlights(ctx, L, s)
        ctx.restore()
    if mode == "live" and s["air"] < 0.5:
        draw_speed_lines(ctx, s["speed"], tl)
    if mode == "live":
        draw_ready_go(ctx, tl)
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
    global FPS, OUT_DIR
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
    ap.add_argument("--replace-episode", type=int, default=None,
                    help="re-render an APPROVED (not uploaded) episode in place: same series, seed and cast, "
                         "new theme/voice/mix; episode number and title stay")
    ap.add_argument("--theme", default=None, help="force a theme: <time>,<weather>,<location> (testing)")
    args = ap.parse_args()
    global VOICE
    FPS = args.fps
    os.makedirs(WORK, exist_ok=True)
    import registry
    detect_font()
    load_cast()
    active = [e for e in registry.load()["videos"] if e.get("status") not in registry.IGNORED_STATUS]
    replace = None
    if args.replace_episode:
        replace = next((e for e in active if e.get("episode") == args.replace_episode), None)
        if not replace or replace.get("status") != "APPROVED":
            raise SystemExit(f"[replace] STOP: episode {args.replace_episode} tidak ada atau bukan APPROVED "
                             f"(yang sudah diupload tidak boleh diganti)")
        args.series, args.seed, args.name, args.force = replace["series"], replace["seed"], replace["video_id"], True
    series = args.series
    if series == "auto":
        counts = {s: 0 for s in SERIES_DEFS}
        for e in active:
            if e.get("engine_version") == ENGINE_VERSION and e["series"] in counts:
                counts[e["series"]] += 1
        series = min(SERIES_DEFS, key=lambda s: counts[s] / SERIES_WEIGHT.get(s, 1))
    appearances = {}
    for e in active:
        for vk in e.get("vehicles", []):
            appearances[vk] = appearances.get(vk, 0) + 1
    wins = {}
    for e in active:
        if e.get("outcomes") and e["outcomes"][-1] == "win" and e.get("vehicles"):
            wins[e["vehicles"][-1]] = wins.get(e["vehicles"][-1], 0) + 1
    force = dict(SERIES_DEFS[series].get("force_theme", {}))
    if args.theme:
        force.update(zip(("time", "weather", "location"), args.theme.split(",")))
    make_theme(args.seed, force or None, used=[e.get("theme", "") for e in active if e.get("theme")])
    make_track(series, args.seed)
    make_story(series, args.seed, appearances, wins)
    if replace:                                              # keep the approved cast
        global ROLE_ORDER
        ROLE_ORDER = [[vk] for vk in replace["vehicles"]]
    init_scenery()
    VOICE = cb_pick(active, args.seed, exclude_id=args.name)   # narrator "C": m1/f1 alternating
    if VOICE is None:
        uses = {v: 0 for v in VOICES}                         # Edge narrator rotation: fewest uses first
        for e in active:
            if e.get("voice") in uses and e.get("video_id") != args.name:
                uses[e["voice"]] += 1
        vr = np.random.default_rng(5000 + args.seed)
        tie = {v: float(vr.random()) for v in VOICES}
        VOICE = min(VOICES, key=lambda v: (uses[v], tie[v]))
    print(f"[theme] {THEME_ID}  [voice] {VOICE}", flush=True)
    name = args.name or f"SIM_{SERIES.upper()}_{ENGINE_VERSION.upper()}_S{args.seed:03d}"
    render_date = time.strftime("%Y-%m-%d")
    if args.preview_only:
        OUT_DIR = f"{WORK}/previews/{name}"             # previews never land in renders/
    elif replace:
        OUT_DIR = f"{WORK}/staging/{name}"               # swapped into the episode folder after the audit passes
        shutil.rmtree(OUT_DIR, ignore_errors=True)
    else:
        OUT_DIR = f"{CHANNEL_DIR}/pending/{render_date}_{SERIES}_s{args.seed:03d}"
    if not args.preview_only and not args.force:
        other = registry.find_seed(SERIES, ENGINE_VERSION, args.seed, exclude_id=name)
        if other:
            raise SystemExit(f"[registry] STOP: seed {args.seed} sudah dipakai oleh {other}. Pakai seed lain.")
        prev = registry.get(name)
        if prev and prev.get("status") not in registry.IGNORED_STATUS:
            raise SystemExit(f"[registry] STOP: {name} sudah ada ({prev.get('status')}, {prev.get('folder')}). "
                             f"Pakai seed lain atau --force.")
    # OUT_DIR is created when the preview folder is made (after the analysis passed): no empty folders on STOP
    print(f"[track] {TRACK_ID} {json.dumps(TRACK_PARAMS)}", flush=True)
    print(f"[story] {SERIES}: " + " | ".join(f"{want}: {'>'.join(order)}" for order, (_, want)
                                             in zip(ROLE_ORDER, ROSTER)), flush=True)
    rng = np.random.default_rng(args.seed)
    t0 = time.time()
    print(f"[font] {FONT_FACE}", flush=True)

    global HOLD_S
    ready_vo = ready_go_audio()                               # also sets READY_GO_T
    HOLD_S = READY_GO_T + 0.12                                # the car launches right on "GO!"
    cands, intro_pairs = candidate_runs()
    intro_texts = [t for t, _ in intro_pairs]
    intros = [a for _, a in intro_pairs]
    intro_durs = [len(x) / SR for x in intros]
    print(f"[cast] final: " + " -> ".join(VEHICLES[vk]["nick"] for vk, _ in STORY), flush=True)
    cta = tts(CTA)
    replay_vo = tts(REPLAY_LINE)

    def outcome_line(vk, run):
        lines = dict(FAIL_LINES, **SERIES_DEFS[SERIES].get("fail_lines", {}))
        et = run["event"]["type"]
        if run.get("spun") and f"{et}_spun" in lines:            # hydroplaned before the fail
            et = f"{et}_spun"
        tmpl = WIN_LINE if et == "win" else lines[et]
        return tmpl.format(n=VEHICLES[vk]["nick"])

    line_audio = {}
    timed = []
    for li, ((vk, _), runs_li) in enumerate(zip(STORY, cands)):
        row = []
        for run in runs_li:
            text = outcome_line(vk, run)
            if text not in line_audio:
                line_audio[text] = tts(text)
            lt_args = (vk, run, intro_durs[li], len(line_audio[text]) / SR, len(cta) / SR)
            row.append(level_timing(*lt_args))
            if row[-1]["replay"]:                                 # same run without replay: shorter option
                row.append(level_timing(*lt_args, allow_replay=False))
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
    folder_rel = os.path.relpath(OUT_DIR, BASE)
    entry = dict(video_id=name, series=SERIES, engine_version=ENGINE_VERSION, seed=args.seed,
                 created=render_date, render_date=render_date, vehicles=[vk for vk, _ in STORY],
                 track_id=f"{TRACK_ID}@{THEME_ID}", theme=THEME_ID, voice=VOICE,
                 outcomes=outcome_tags(), duration=round(total, 2), status="ANALYZED",
                 folder=folder_rel, audit=f"{folder_rel}/{name}_audit.md",
                 episode=None, season=None, upload_date=None, youtube_url=None)
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
        place(sfx, tone(660, 0.12, "sine", decay=0.08), st0 + 0.02, 0.5)       # READY beep
        place(sfx, tone(990, 0.22, "sine", decay=0.12), st0 + 0.5, 0.6)        # GO beep
        for j, (ti, s, _, _) in enumerate(L["impacts"]):
            if ti < L["live_end"]:
                place(sfx, synth_impact(s, seed=100 + j), st0 + out_time(L, ti), 0.9)
        if L["broken"]:
            place(sfx, synth_shatter(), st0 + out_time(L, L["broken"]["t"]), 0.7)
        # hazard sounds (series-specific)
        rec = L["rec"]
        live_n = min(len(rec["cx"]), int(L["live_end"] * REC_HZ))
        for pi_, (px0, px1) in enumerate(PUDDLES):              # splash + tyre rush while in the water
            inside = [i for i in range(live_n) if px0 <= rec["wheels"][i][-1][0] <= px1]
            if inside:
                hit, out_i = inside[0], inside[-1]
                sp_ = min(1.0, rec["speed"][hit] / 12)
                place(sfx, synth_splash(sp_, seed=41 + pi_), st0 + out_time(L, hit / REC_HZ), 1.0)
                o0, o1 = out_time(L, hit / REC_HZ), out_time(L, out_i / REC_HZ)
                if o1 - o0 > 0.15 and rec["speed"][hit] > 2:
                    place(sfx, synth_water_rush(o1 - o0, 0.35 + 0.5 * sp_, seed=61 + pi_), st0 + o0, 0.7)
        if L.get("spun") is not None:                            # hydroplane spin swish
            sl_n = int(L["spun"] * REC_HZ)
            yaws = rec["yaw"][sl_n:]
            end = next((k for k, y in enumerate(yaws) if abs(y) < 1e-6 and k > 3), len(yaws))
            turns = max(1, int(round(abs(yaws[max(0, end - 1)]) / (2 * math.pi)))) if end else 1
            o0, o1 = out_time(L, L["spun"]), out_time(L, L["spun"] + end / REC_HZ)
            place(sfx, synth_spin(max(0.3, o1 - o0), turns), st0 + o0, 0.8)
        if PIT_KIND == "lava" and (PITS or VENTS):              # lava pools bubbling, louder when near
            dur_live = out_time(L, L["live_end"])
            bed = synth_lava_bed(dur_live, seed=89 + li)
            ts = np.arange(0, L["live_end"], 0.1)
            hz_x = [(a + b) / 2 for a, b, _ in PITS] + [vv["x"] for vv in VENTS]
            gains = [float(np.clip(1.1 - min(abs(interp(rec["cx"], tt) - hx) for hx in hz_x) / 14, 0.08, 1.0))
                     for tt in ts]
            og = np.interp(np.arange(len(bed)) / SR, [out_time(L, tt) for tt in ts], gains)
            place(sfx, bed * og, st0, 0.45)
        for vi, vent in enumerate(VENTS):                        # every eruption; louder when the car is near
            k = 0
            while True:
                t_er = k * vent["period"] - vent["phase"] - 0.35    # rumble starts just before the blast
                k += 1
                if t_er < 0:
                    continue
                if t_er > L["live_end"]:
                    break
                cx_then = float(interp(rec["cx"], t_er + 0.35))
                gain = float(np.clip(1.1 - abs(cx_then - vent["x"]) / 22, 0.15, 1.0))
                place(sfx, synth_eruption(seed=43 + vi * 7 + k), st0 + out_time(L, t_er), 0.9 * gain)
        sunk_lava = L.get("sunk") is not None and PIT_KIND == "lava"
        if L.get("sunk") is not None and PIT_KIND == "water":   # plunge into the water pool + glugging
            place(sfx, synth_splash(1.0, seed=45, big=True), st0 + out_time(L, L["sunk"]), 1.0)
            place(sfx, synth_gurgle(), st0 + out_time(L, L["sunk"]) + 0.6, 0.6)
        if sunk_lava:
            place(sfx, synth_lava_plunge(), st0 + out_time(L, L["sunk"]), 1.0)
        elif L.get("burned") is not None:
            place(sfx, synth_ignite(), st0 + out_time(L, L["burned"]), 0.9)
        if L.get("burned") is not None:                           # keeps burning until the level ends
            f0 = out_time(L, L["burned"]) + (1.0 if sunk_lava else 0.5)
            f1 = out_time(L, L["live_end"])
            if f1 - f0 > 0.5:
                place(sfx, synth_fire(f1 - f0, seed=71 + li), st0 + f0, 0.55)
        if L["event"]["type"] == "crash":
            place(sfx, synth_wall_crash(1.0), st0 + out_time(L, L["event"]["t"]), 1.0)
        for bt, text in L["bubbles"]:
            place(sfx, pop, st0 + out_time(L, bt), 0.6)
            if text == "UH OH!":
                place(sfx, gulp, st0 + out_time(L, bt) + 0.1, 0.6)
        place(narr, ready_vo, st0 + 0.0)
        place(narr, intros[li], st0 + HOLD_S + 0.15)
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
            if L["event"]["type"] == "crash" and ta <= L["event"]["t"] < tb:
                place(sfx, stretch(synth_wall_crash(1.0), 0.5), r0 + (L["event"]["t"] - ta) / REPLAY_SPEED, 1.0)
            if L.get("sunk") is not None and ta <= L["sunk"] < tb:
                sig = synth_lava_plunge() if PIT_KIND == "lava" else synth_splash(1.0, seed=45, big=True)
                place(sfx, stretch(sig, 0.6), r0 + (L["sunk"] - ta) / REPLAY_SPEED, 1.0)
            elif L.get("burned") is not None and ta <= L["burned"] < tb:
                place(sfx, stretch(synth_ignite(), 0.6), r0 + (L["burned"] - ta) / REPLAY_SPEED, 0.9)
            if L.get("spun") is not None and ta <= L["spun"] < tb:
                place(sfx, stretch(synth_spin(1.4, 1), 0.6), r0 + (L["spun"] - ta) / REPLAY_SPEED, 0.7)
    wins = [L["start"] + out_time(L, L["event"]["t"]) + 1.3 for L in LEVELS if L["event"]["type"] == "win"]
    bgm = music_bed(total, wins, hold=4.5, style=th_time()["music"])
    bgm = bgm[:n] if len(bgm) >= n else np.pad(bgm, (0, n - len(bgm)))
    # ducking: engine + music dip while the narrator talks, so every word is easy to catch
    xs = (np.abs(narr) > 0.01).astype(float)                 # O(N) moving average (np.convolve took minutes)
    kk = int(0.25 * SR)
    cs = np.concatenate([[0.0], np.cumsum(xs)])
    mv = (cs[kk:] - cs[:-kk]) / kk
    talk = np.pad(mv, ((len(xs) - len(mv)) // 2, len(xs) - len(mv) - (len(xs) - len(mv)) // 2), mode="edge")
    duck = 1.0 - (1.0 - 10 ** (-DUCK_DB / 20)) * np.clip(talk * 3, 0, 1)
    mix = (peak(narr) * VOL_NARR + peak(eng) * VOL_ENGINE * duck + peak(bgm) * VOL_BGM * duck
           + peak(sfx) * VOL_SFX * (0.5 + 0.5 * duck))
    mix = np.tanh(1.3 * mix) / np.tanh(1.3)
    mix = mix / max(1e-9, np.max(np.abs(mix))) * 0.95
    cb_finish(f"narrator {name}")                             # missing voice-C lines -> Modal -> restart
    wav_path = f"{WORK}/mix_{name}.wav"
    write_wav(wav_path, mix)

    prev_dir = f"{OUT_DIR}/preview"
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
    subj = next((L["vk"] for L in LEVELS if L["event"]["type"] != "win"), LEVELS[-1]["vk"])
    emoji = SERIES_DEFS[SERIES]["yt_title"].split("?")[-1].strip()
    yt_title = challenge_title(subj, SERIES_DEFS[SERIES]["obst"], emoji, args.seed)
    manifest = dict(
        video_id=name, status="ANALYZED" if analysis_ok else "ANALYSIS_FAILED", engine=f"sim-prototype {ENGINE_VERSION}",
        series=SERIES, seed=args.seed, fps=FPS, duration=round(total, 2),
        track_id=TRACK_ID, track_params=TRACK_PARAMS, theme=THEME, theme_id=THEME_ID, voice=VOICE,
        fingerprint=fingerprint, outcomes=entry["outcomes"],
        analysis=analysis, cta=CTA,
        title_base=yt_title,
        title=f"{yt_title} #Shorts",                              # episodes.py approve adds "| Ep. N"
        description=video_description(),
        tags=SERIES_DEFS[SERIES]["tags"] + [VEHICLES[vk]["display"].split(" THE ")[1].lower() for vk, _ in STORY],
        levels=[dict(vehicle=L["v"]["display"], speed=round(L["speed"], 2), outcome=L["event"]["type"],
                     event_t=round(L["event"]["t"], 2), obstacle=L["event"]["obstacle"],
                     broken=bool(L["broken"]), bullet_time=bool(L["bullet"]), replay=bool(L["replay"]),
                     bubbles=[b[1] for b in L["bubbles"]], start=round(L["start"], 2), duration=round(L["dur"], 2),
                     event_out=round(L["start"] + out_time(L, L["event"]["t"]), 2),
                     x_start=round(float(L["rec"]["cx"][0]), 1), x_end=round(float(L["rec"]["cx"][-1]), 1),
                     level_color=[int(c * 255) for c in LEVEL_COLORS[li]])
                for li, L in enumerate(LEVELS)],
        narration=[f"Ready... Go! {t}" for t in intro_texts] + outcome_lines + ([REPLAY_LINE] if any_replay else [])
                  + [CTA],
        assets="100% procedurally generated (pymunk physics + cairo render + synthesized audio), narration "
               + (f"Chatterbox TTS (open source, Modal GPU) synthetic voice {VOICE}" if VOICE.startswith("chatterbox") else f"Edge-TTS {VOICE}"),
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
    fails = [L["start"] + out_time(L, L["event"]["t"]) for L in LEVELS if L["event"]["type"] != "win"]
    wins_t = [L["start"] + out_time(L, L["event"]["t"]) for L in LEVELS if L["event"]["type"] == "win"]
    subj0 = next((L["vk"] for L in LEVELS if L["event"]["type"] != "win"), LEVELS[-1]["vk"])
    add_cold_open(out, (fails or wins_t or [3.0])[0], f"CAN {VEHICLES[subj0]['nick']} SURVIVE?")
    print(f"[render] {len(INDEX)} frames in {time.time() - t1:.1f}s -> {out} (+{COLD_OPEN_S}s cold open)", flush=True)
    print(json.dumps(manifest["levels"], indent=1))

    # automatic audit (BLUEPRINT.md section 6) + registry (section 7)
    import audit
    passed = audit.run_audit(name, folder=OUT_DIR)
    if replace:
        if not passed:
            print(f"[replace] audit FAILED - episode {replace['episode']} left untouched; see {OUT_DIR}", flush=True)
            raise SystemExit(5)
        ep_dir = f"{BASE}/{replace['folder']}"
        for fn in os.listdir(ep_dir):                      # old render out, new render in
            p = f"{ep_dir}/{fn}"
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        for fn in os.listdir(OUT_DIR):
            shutil.move(f"{OUT_DIR}/{fn}", f"{ep_dir}/{fn}")
        for fn in (f"{name}.json", f"{name}_audit.md", f"{name}_audit.json"):
            p = f"{ep_dir}/{fn}"
            with open(p) as fh:
                txt = fh.read()
            with open(p, "w") as fh:
                fh.write(txt.replace(OUT_DIR, ep_dir))
        with open(f"{ep_dir}/{name}.json") as fh:
            man = json.load(fh)
        man.update(episode=replace["episode"], season=replace["season"], title=replace["title"], status="APPROVED",
                   approved_date=replace.get("approved_date"), rerendered=render_date)
        with open(f"{ep_dir}/{name}.json", "w") as fh:
            json.dump(man, fh, indent=2, ensure_ascii=False)
        registry.update(name, duration=entry["duration"], outcomes=entry["outcomes"], track_id=entry["track_id"],
                        theme=THEME_ID, voice=VOICE, vehicles=entry["vehicles"], rerendered=render_date)
        shutil.rmtree(OUT_DIR, ignore_errors=True)
        print(f"[replace] Ep. {replace['episode']} re-rendered in place -> {replace['folder']}", flush=True)
        return
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
