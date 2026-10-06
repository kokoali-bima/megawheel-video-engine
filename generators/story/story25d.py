#!/usr/bin/env python3
"""MegaWheel Arena — series "story15": cinematic story scenes (STORY15_PLAN.md, user 2026-10-01).

One scene (±1 minute) is described by a shot list (stories/<episode>/scene_XX.json) and rendered on the VM CPU with the
SAME character drawing as every Short (race25d.draw_car -> sim_engine body / wheels), plus story-only features:
  close-up / extreme close-up / medium / wide / low-angle / two-shot cameras, faces with drama emotions
  (sad, cry, determined, shy, laugh, angry, proud, ...), mouth moving with the voice (lip flap from the audio envelope),
  blinking, tears, subtitles, letterbox, sepia flashback, captions & title cards, poster / calendar props, music bed.
Voices: character references in branding/voice/characters (Chatterbox, QA'd, cached by generators/voice/announcer.py).
Two framings per scene (STORY15_PLAN decision): --aspect h (1920x1080, the long episode) or v (1080x1920, "Part N").

Usage (cd /root/video-engine):
  venv/bin/python generators/story/story25d.py --episode S01E01_sprinkles_first_race --scene 2 --aspect h
  venv/bin/python generators/story/story25d.py --episode S01E01_sprinkles_first_race --assemble --aspect h
Output: work/story/<episode>/scene_02_h.mp4 (+ preview PNGs); --assemble -> work/story/<episode>/<episode>_h.mp4
"""
import argparse
import json
import shutil
import math
import os
import subprocess
import sys

import cairo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(BASE, "generators", "physics_2d"))
sys.path.insert(0, os.path.join(BASE, "generators", "lanes25d"))
sys.path.insert(0, os.path.join(BASE, "generators", "voice"))
import sim_engine as se  # noqa: E402
import race25d as R  # noqa: E402
import smash25d as SM  # noqa: E402  (stands, crowd / cheer / kaiju sounds, Kraggor head)
import announcer  # noqa: E402

FPS = 30
ASPECTS = {"h": (1920, 1080), "v": (1080, 1920)}
VOICE_OF = {"narrator": "m1", "announcer": "m1", "announcer2": "f1"}      # others: actor id == voice key
STYLE_OF = {"normal": "calm", "talk": "calm", "laugh": "happy", "cry": "sad", "determined": "proud", "shy": "calm",
            "surprised": "excited", "tease": "excited", "whisper": "calm", "scared": "scared", "angry": "angry"}
MOOD_BASE = {"happy": "happy", "laugh": "happy", "proud": "happy", "scared": "scared", "surprised": "whoa",
             "excited": "happy", "dizzy": "dizzy"}                                                  # emotion -> se.draw_face mood
SPEAKER_COLOR = {"sprinkles": (1, 0.6, 0.8), "little_sprinkles": (1, 0.7, 0.85), "grandpa_cone": (0.95, 0.85, 0.6),
                 "buster": (1, 0.85, 0.2), "zippy": (1, 0.4, 0.35), "rocky": (0.45, 0.7, 1), "siren": (0.85, 0.9, 1),
                 "narrator": (0.9, 0.9, 0.9), "announcer": (1, 0.86, 0.12), "announcer2": (1, 0.86, 0.12)}

W, H = ASPECTS["h"]
EMO, TALK = {}, {}                                   # per ACTOR id (several actors can share a vehicle key)
CUR = {"aid": None, "mustache": False}               # actor being drawn right now (read by story_face)
GAZE = {}                 # actor id -> +1 look forward / -1 look back (listeners look at the speaker, 2026-10-06)
SPEAKING = {"aid": None}  # who is talking this frame (the group camera leans toward them)
SCENE = {}


# ------------------------------------------------------------------ projection (both framings)
def setup_projection(aspect):
    global W, H, F_PERSP, D0, DZ, Y_H, CAM_H
    W, H = ASPECTS[aspect]
    se.W, se.H, R.W, R.H = W, H, W, H                # sky / weather / text helpers use the module globals
    D0, DZ = 100.0, 9.0
    if aspect == "h":
        F_PERSP, Y_H, CAM_H = 10500.0, H * 0.40, 4.6   # k(0) = 105 px/m: a 4.4 m car = 460 px wide
    else:
        F_PERSP, Y_H, CAM_H = 7000.0, H * 0.43, 6.8    # vertical: k(0) = 70 px/m
    R.k_of, R.ground_y = k_of, ground_y
    SM.k_of, SM.ground_y, SM.W = k_of, ground_y, W     # stands drawn with the story projection
    R.mood_of = lambda c, t, x: EMO_MOOD.get(c.get("id"), "normal")


def k_of(z):
    return F_PERSP / (D0 + DZ * z)


def ground_y(z):
    return Y_H + CAM_H * k_of(z)


CX = 540.0     # world x of the camera centre: the shared Shorts drawing (race25d.draw_car, props, stands) assumes 540


def pxy(x, z, camx):
    return (x - camx) * k_of(z) + CX, ground_y(z)


EMO_MOOD = {}


# ------------------------------------------------------------------ faces: drama emotions, talking mouth, blink, tears
_orig_face = se.draw_face


def story_face(ctx, vk, mood, t):
    _face_core(ctx, vk, mood, t)
    if CUR.get("mustache"):                                        # elder: glasses, beard, soft mustache
        _elder(ctx, se.FACES[vk])


def _elder(ctx, f):
    r, (mx, my), mw = f["r"], f["mouth"], f["mw"]
    ink = (0.15, 0.12, 0.1)
    for ex, ey in f["eyes"]:                                       # round glasses
        ctx.arc(ex, ey, r * 1.55, 0, 2 * math.pi)
        ctx.set_source_rgba(0.85, 0.95, 1.0, 0.25)
        ctx.fill_preserve()
        ctx.set_source_rgb(*ink)
        ctx.set_line_width(r * 0.28)
        ctx.stroke()
    (x0, y0), (x1, y1) = f["eyes"][0], f["eyes"][-1]
    ctx.move_to(x0 + r * 1.55, y0)
    ctx.line_to(x1 - r * 1.55, y1)
    ctx.set_line_width(r * 0.25)
    ctx.stroke()
    ctx.save()                                                     # white beard under the mouth
    ctx.translate(mx - mw * 0.05, my - mw * 0.55)
    ctx.scale(mw * 0.75, mw * 0.55)
    ctx.arc(0, 0, 1, math.pi * 1.0, math.pi * 2.0)
    ctx.restore()
    ctx.close_path()
    ctx.set_source_rgb(0.97, 0.97, 0.95)
    ctx.fill_preserve()
    ctx.set_source_rgb(0.7, 0.7, 0.7)
    ctx.set_line_width(mw * 0.04)
    ctx.stroke()
    for s_ in (-1, 1):                                             # soft curled mustache
        ctx.save()
        ctx.translate(mx + s_ * mw * 0.28, my + mw * 0.22)
        ctx.rotate(-s_ * 0.25)
        ctx.scale(mw * 0.34, mw * 0.11)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.95, 0.95, 0.93)
        ctx.fill()


def _face_core(ctx, vk, mood, t):
    aid = CUR["aid"] or vk
    emo = EMO.get(aid, "normal")
    talk = TALK.get(aid, 0.0)
    f = se.FACES[vk]
    r, ink = f["r"], (0.05, 0.05, 0.1)
    blink = (t * 1.0 + sum(map(ord, aid)) % 7 * 0.37) % 3.7 < 0.12 and emo not in ("happy", "laugh", "dizzy")
    if emo == "dizzy":                                             # squashed / bonked: spiral-cross eyes (Shorts style)
        _orig_face(ctx, vk, "dizzy", t)
        return
    if emo in ("happy", "laugh", "proud", "excited", "scared", "surprised") and talk < 0.08 and not blink:
        _orig_face(ctx, vk, MOOD_BASE.get(emo, "normal"), t)
        _brows(ctx, f, emo)
        return
    # eyes
    for n, (ex, ey) in enumerate(f["eyes"]):
        if blink:
            ctx.move_to(ex - r, ey)
            ctx.line_to(ex + r, ey)
            ctx.set_source_rgb(*ink)
            ctx.set_line_width(r * 0.35)
            ctx.stroke()
            continue
        if emo in ("happy", "laugh", "proud"):
            ctx.new_path()
            ctx.arc(ex, ey - r * 0.2, r * 0.75, 0.15 * math.pi, 0.85 * math.pi)
            ctx.set_source_rgb(*ink)
            ctx.set_line_width(r * 0.4)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
            continue
        big = {"surprised": 1.35, "scared": 1.2}.get(emo, 1.0)
        rr = r * big
        ctx.save()
        ctx.translate(ex, ey)
        ctx.scale(1, 1.25 if emo not in ("sad", "cry", "determined", "angry") else 1.05)
        ctx.arc(0, 0, rr, 0, 2 * math.pi)
        ctx.restore()
        se.fill_stroke(ctx, (1, 1, 1), lw=r * 0.25)
        look = {"shy": (-0.35, -0.25), "sad": (0.1, -0.35), "cry": (0.1, -0.35)}.get(emo, (0.35, 0.1))
        if aid in GAZE and emo not in ("shy",):                    # listening: eyes on whoever is talking
            look = (0.38 * GAZE[aid], look[1])
        pr = 0.5 if emo not in ("surprised", "scared") else 0.32
        ctx.arc(ex + rr * look[0], ey + rr * look[1], rr * pr, 0, 2 * math.pi)
        ctx.set_source_rgb(*ink)
        ctx.fill()
        ctx.arc(ex + rr * look[0] + rr * pr * 0.35, ey + rr * look[1] + rr * pr * 0.35, rr * pr * 0.32, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        if emo in ("sad", "cry"):                                  # glossy, wet eyes
            ctx.arc(ex - rr * 0.2, ey - rr * 0.35, rr * 0.18, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.8)
            ctx.fill()
    _brows(ctx, f, emo)
    if emo in ("cry",) or (emo == "sad" and SCENE.get("tears")):
        ex, ey = f["eyes"][-1]
        for j in range(2):                                         # tears running down
            ph = (t * 0.9 + j * 0.5) % 1.0
            ctx.save()
            ctx.translate(ex + r * 0.2, ey - r * (1.0 + ph * 2.5))
            ctx.scale(1, -1)
            ctx.move_to(0, -r * 0.35)
            ctx.curve_to(r * 0.28, 0, r * 0.22, r * 0.25, 0, r * 0.25)
            ctx.curve_to(-r * 0.22, r * 0.25, -r * 0.28, 0, 0, -r * 0.35)
            ctx.restore()
            ctx.set_source_rgba(0.45, 0.8, 1.0, 0.9 * (1 - ph))
            ctx.fill()
    if emo == "shy":                                               # blush
        for ex, ey in f["eyes"]:
            ctx.arc(ex + r * 0.9, ey - r * 1.3, r * 0.45, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 0.45, 0.55, 0.55)
            ctx.fill()
    _mouth(ctx, f, emo, talk, t)


def _mustache(ctx, f):
    mx, my = f["mouth"]
    mw = f["mw"]
    for s_ in (-1, 1):
        ctx.save()
        ctx.translate(mx + s_ * mw * 0.32, my + mw * 0.32)
        ctx.scale(mw * 0.42, mw * 0.2)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.97, 0.97, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.5, 0.5, 0.5)
        ctx.set_line_width(mw * 0.04)
        ctx.stroke()


def _brows(ctx, f, emo):
    r = f["r"]
    tilt = {"sad": -0.35, "cry": -0.4, "angry": 0.45, "determined": 0.3, "worried": -0.3, "shy": -0.15}.get(emo)
    if tilt is None:
        return
    ctx.set_source_rgb(0.05, 0.05, 0.1)
    ctx.set_line_width(r * 0.3)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for n, (ex, ey) in enumerate(f["eyes"]):
        s = -1 if n == 0 else 1                                    # eyes are side by side along x
        y0 = ey + r * 1.55
        ctx.move_to(ex - r * 0.8, y0 + s * tilt * r * 0.6 * (-1 if n == 0 else 1))
        ctx.line_to(ex + r * 0.8, y0 - s * tilt * r * 0.6 * (-1 if n == 0 else 1))
        ctx.stroke()


def _mouth(ctx, f, emo, talk, t):
    mx, my = f["mouth"]
    mw = f["mw"]
    ink = (0.05, 0.05, 0.1)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    vis = VIS.get(CUR["aid"]) if CUR.get("aid") else None
    if vis and vis != "X" and talk > 0.02:                         # phoneme mouth (Rhubarb, Preston Blair set)
        _viseme_mouth(ctx, mx, my, mw, vis, emo, talk)
        return
    if talk > 0.08:                                                # talking: open mouth, size from the voice
        o = 0.12 + 0.38 * min(1.0, talk)
        smile = {"happy": 0.12, "laugh": 0.15, "proud": 0.1, "sad": -0.08, "cry": -0.1, "angry": -0.05}.get(emo, 0.0)
        ctx.save()
        ctx.translate(mx, my + smile * mw)
        ctx.scale(0.55, 1.0)
        ctx.arc(0, 0, mw * o, 0, 2 * math.pi)
        ctx.restore()
        se.fill_stroke(ctx, (0.45, 0.05, 0.1), lw=mw * 0.1)
        return
    ctx.set_source_rgb(*ink)
    ctx.set_line_width(mw * 0.16)
    ctx.new_path()
    if emo in ("sad", "cry", "worried"):                           # frown
        ctx.arc(mx, my - mw * 0.45, mw * 0.45, 0.2 * math.pi, 0.8 * math.pi)
        ctx.stroke()
    elif emo == "angry":
        ctx.move_to(mx - mw / 2, my - mw * 0.05)
        ctx.line_to(mx + mw / 2, my + mw * 0.05)
        ctx.stroke()
    elif emo == "determined":
        ctx.move_to(mx - mw * 0.45, my)
        ctx.line_to(mx + mw * 0.45, my + mw * 0.08)
        ctx.stroke()
    elif emo == "shy":
        ctx.arc(mx, my + mw * 0.25, mw * 0.3, 1.25 * math.pi, 1.75 * math.pi)
        ctx.stroke()
    else:
        ctx.arc(mx, my + mw * 0.3, mw * 0.5, 1.2 * math.pi, 1.8 * math.pi)
        ctx.stroke()


def _viseme_mouth(ctx, mx, my, mw, v, emo, talk):
    """A closed M/B/P - B slightly open + teeth (K S T EE) - C open (EH AE) - D wide (AA) - E round (AO ER)
    - F pucker (OO W) - G F/V (teeth on lip) - H L (tongue). Size breathes a little with the voice."""
    dark, teeth, tongue = (0.45, 0.05, 0.1), (1, 1, 1), (0.95, 0.45, 0.5)
    smile = {"happy": 0.1, "laugh": 0.14, "proud": 0.08, "sad": -0.08, "cry": -0.1, "angry": -0.05}.get(emo, 0.0)
    g = 0.9 + 0.2 * min(1.0, talk)
    ctx.save()
    ctx.translate(mx, my + smile * mw)
    ctx.scale(g, g)
    ink = (0.05, 0.05, 0.1)

    def oval(w, h):
        ctx.save()
        ctx.scale(w, h)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()

    if v == "A":
        ctx.move_to(-mw * 0.32, 0)
        ctx.curve_to(-mw * 0.1, mw * 0.04, mw * 0.1, mw * 0.04, mw * 0.32, 0)
        ctx.set_source_rgb(*ink)
        ctx.set_line_width(mw * 0.16)
        ctx.stroke()
    elif v in ("B", "G"):
        oval(mw * 0.3, mw * (0.13 if v == "B" else 0.11))
        se.fill_stroke(ctx, dark, lw=mw * 0.08)
        ctx.rectangle(-mw * 0.24, -mw * 0.11 if v == "G" else -mw * 0.02, mw * 0.48, mw * 0.06)
        ctx.set_source_rgb(*teeth)
        ctx.fill()
    elif v == "C":
        oval(mw * 0.3, mw * 0.2)
        se.fill_stroke(ctx, dark, lw=mw * 0.08)
    elif v == "D":
        oval(mw * 0.34, mw * 0.3)
        se.fill_stroke(ctx, dark, lw=mw * 0.08)
        ctx.rectangle(-mw * 0.22, -mw * 0.27, mw * 0.44, mw * 0.07)
        ctx.set_source_rgb(*teeth)
        ctx.fill()
        ctx.save()
        ctx.translate(0, mw * 0.17)
        oval(mw * 0.16, mw * 0.08)
        ctx.restore()
        ctx.set_source_rgb(*tongue)
        ctx.fill()
    elif v == "E":
        oval(mw * 0.2, mw * 0.22)
        se.fill_stroke(ctx, dark, lw=mw * 0.08)
    elif v == "F":
        oval(mw * 0.12, mw * 0.13)
        se.fill_stroke(ctx, dark, lw=mw * 0.09)
    elif v == "H":
        oval(mw * 0.28, mw * 0.22)
        se.fill_stroke(ctx, dark, lw=mw * 0.08)
        ctx.save()
        ctx.translate(0, -mw * 0.06)
        oval(mw * 0.13, mw * 0.08)
        ctx.restore()
        ctx.set_source_rgb(*tongue)
        ctx.fill()
    ctx.restore()


se.draw_face = story_face


# ------------------------------------------------------------------ actors
def make_actor(aid, a):
    vk = a["vk"]
    return dict(id=aid, key=vk, lane=0, x=float(a.get("x", 0)), z=float(a.get("z", 1.0)),
                face=1 if a.get("face", 1) >= 0 else -1, h=0.0, land=None, trig=None, finish=None, bump_t=None,
                rec=[], small=float(a.get("scale", 1.0)), hidden=bool(a.get("hidden", False)),
                color=tuple(a["color"]) if a.get("color") else None, mustache=bool(a.get("mustache", False)),
                accent=tuple(a["accent"]) if a.get("accent") else None, sq=1.0, patched=float(a.get("patched", 0)),
                h0=float(a.get("h", 0.0)), dizzy=False)


def draw_actor(ctx, a, t, camx):
    """race25d.draw_car with per-actor colour / mustache / size (Grandpa Cone, Little Sprinkles share a vehicle)."""
    veh = se.VEHICLES[a["key"]]
    old, old_acc = veh["color"], veh.get("accent")
    if a["color"]:
        veh["color"] = a["color"]
    if a["accent"]:
        veh["accent"] = a["accent"]
    CUR["aid"], CUR["mustache"] = a["id"], a["mustache"]
    try:
        if a["small"] != 1.0:
            sx, gy = pxy(a["x"], a["z"], camx)
            ctx.save()
            ctx.translate(sx, gy)
            ctx.scale(a["small"], a["small"])
            ctx.translate(-sx, -gy)
            R.draw_car(ctx, a, t, camx)
            ctx.restore()
        else:
            R.draw_car(ctx, a, t, camx)
    finally:
        veh["color"] = old
        if old_acc is None:
            veh.pop("accent", None)
        else:
            veh["accent"] = old_acc
        CUR["aid"], CUR["mustache"] = None, False


def draw_beam(ctx, a, t, camx, flicker=False):
    """Night: real headlight beams - a cone of light along the road ahead of the car + a pool where it lands.
    User 2026-10-05: not only lit lamps, the beam itself. Story use: the beam REVEALS things (footprints) and
    flickers when Kraggor is near (shot "flicker": [actor ids]) - a danger sign the audience learns."""
    veh = se.VEHICLES[a["key"]]
    bw, bh = veh["body"]
    k = k_of(a["z"]) * a["small"]
    sx, gy = pxy(a["x"], a["z"], camx)
    on = 1.0
    if flicker:                                                    # stutter: mostly on, sudden drops
        ph = (t * 7.3) % 1.0
        on = 0.12 if ph < 0.22 or 0.5 < ph < 0.58 else 1.0
    d = a["face"]
    fx = sx + d * bw * 0.48 * k                                    # front of the body
    hy = gy - (veh["wheel_r"] + bh * 0.35 + a["h"]) * k            # headlight height
    reach = 13.0 * k
    tip = fx + d * reach
    g = cairo.LinearGradient(fx, 0, tip, 0)
    g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.42 * on)
    g.add_color_stop_rgba(0.6, 1, 0.95, 0.75, 0.16 * on)
    g.add_color_stop_rgba(1, 1, 0.95, 0.75, 0.0)
    se.poly(ctx, [(fx, hy - 0.12 * k), (fx, hy + 0.12 * k), (tip, gy + 0.55 * k), (tip, gy - 1.6 * k)])   # air cone
    ctx.set_source(g)
    ctx.fill()
    pool = cairo.RadialGradient(fx + d * reach * 0.55, gy + 0.1 * k, 0.3 * k, fx + d * reach * 0.55, gy + 0.1 * k, reach * 0.55)
    pool.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.32 * on)
    pool.add_color_stop_rgba(1, 1, 0.95, 0.8, 0.0)
    ctx.save()
    ctx.translate(0, gy + 0.1 * k)
    ctx.scale(1.0, 0.22)                                           # the pool lies flat on the road
    ctx.translate(0, -(gy + 0.1 * k))
    ctx.arc(fx + d * reach * 0.55, gy + 0.1 * k, reach * 0.55, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source(pool)
    ctx.fill()


def platform_h(x, z):
    """Height of whatever is under (x, z): a 'stage' prop with a ramp at each end (contract G04, owner 2026-10-06:
    Siren drove off the stage and stayed in the air). 0 = the road."""
    best = 0.0
    for p in SCENE.get("props", []):
        if p.get("type") != "stage" or abs(z - p.get("z", 2.6)) > 1.0:
            continue
        half, ramp, hgt = p.get("w", 7.0) / 2, p.get("ramp", 1.8), p.get("h", 0.75)
        dx = abs(x - p.get("x", 0.0))
        if dx <= half:
            best = max(best, hgt)
        elif dx <= half + ramp:
            best = max(best, hgt * (1 - (dx - half) / ramp))
    return best


def actor_state(a, t):
    yaw = 0.0 if a["face"] > 0 else math.pi
    hh, slope = hill_h(a["x"])
    pitch = math.atan(slope) * a["face"]
    st = (a["x"], a["z"], a["h"] + hh, yaw, pitch, a.get("v", 0.0), a["sq"], 0.0, 0.0, a["patched"], 0.0, 0.0)
    a["rec"] = [st, st]
    return st


# ------------------------------------------------------------------ sets / locations
def draw_set(ctx, loc, camx, t, after_sky=None):
    se.draw_sky(ctx, camx * 0.35, 0.0, 1.0)
    if after_sky:                                                  # things behind the stands (Kraggor rising)
        after_sky()
    if loc == "garage":
        ctx.rectangle(-W, -H, 3 * W, 3 * H)
        ctx.set_source_rgb(*se.lit((0.22, 0.2, 0.24)))
        ctx.fill()
        for i in range(-20, 21):                                   # wooden wall planks
            x = (i * 1.6 - camx) * k_of(4) + CX
            ctx.rectangle(x, 0, 3, ground_y(4))
            ctx.set_source_rgba(0, 0, 0, 0.25)
            ctx.fill()
        y = ground_y(3.5)
        ctx.rectangle(-W, y, 3 * W, H)
        ctx.set_source_rgb(*se.lit((0.32, 0.3, 0.3)))
        ctx.fill()
        return
    # outdoor: ground + road
    gc = se.lit(se.th_loc()["ground"])
    ctx.rectangle(-W, ground_y(6.0), 3 * W, H * 2)
    ctx.set_source_rgb(*se.shade(gc, 0.9))
    ctx.fill()
    if loc in ("town", "arena", "country", "trackside", "podium"):
        top, bot = ground_y(3.2), ground_y(-0.6)
        ctx.rectangle(-W, top, 3 * W, bot - top)
        ctx.set_source_rgb(*se.lit((0.3, 0.3, 0.34) if loc != "country" else (0.55, 0.45, 0.3)))
        ctx.fill()
        if loc != "country":
            k, y = k_of(1.3), ground_y(1.3)
            x = math.floor((camx - W / k) / 4) * 4
            while (x - camx) * k + CX < 2 * W:
                ctx.rectangle((x - camx) * k + CX, y - k * 0.06, 1.6 * k, k * 0.12)
                ctx.set_source_rgba(1, 1, 1, 0.85)
                ctx.fill()
                x += 4
    if loc in ("arena", "trackside", "podium"):
        SM.STANDS_TEXT = SCENE.get("stands_text", "MEGAWHEEL RACEWAY")
        SM.STANDS_ROWS = 3
        SM.draw_stands(ctx, camx, t, 0.6)


def draw_props_layer(ctx, loc, camx, seed, back=True):
    if loc in ("town", "country", "trackside"):
        R.draw_props(ctx, camx, 5.4 if back else -1.0, seed, back=back)


def draw_poster(ctx, p, camx):
    x, z = p.get("x", 3.0), p.get("z", 4.5)
    k = k_of(z)
    sx, gy = pxy(x, z, camx)
    w, hh = p.get("w", 6.0) * k, p.get("h", 3.4) * k
    pole = p.get("pole", 6.2)
    ctx.rectangle(sx - 0.15 * k, gy - pole * k, 0.3 * k, pole * k)
    ctx.set_source_rgb(*se.lit((0.35, 0.3, 0.28)))
    ctx.fill()
    se.rrect(ctx, sx - w / 2, gy - pole * k - hh, w, hh, 0.2 * k)
    ctx.set_source_rgb(*se.lit((0.98, 0.94, 0.85)))
    ctx.fill_preserve()
    ctx.set_source_rgb(0.85, 0.15, 0.15)
    ctx.set_line_width(0.15 * k)
    ctx.stroke()
    lines = p["text"].split("\n")
    for i, ln in enumerate(lines):
        se.draw_text(ctx, ln, sx, gy - pole * k - hh + hh * (i + 0.8) / (len(lines) + 0.4), 0.8 * k if i == 0 else 0.55 * k,
                     fill=(0.85, 0.12, 0.12) if i == 0 else (0.1, 0.1, 0.2), stroke=(1, 1, 1), sw=2, max_w=w * 0.9)


def draw_sketch(ctx, p, camx, t):
    """A child-like pencil sketch of a little green creature with a tail, signed 'K.' (Grandpa's box, S01E02 sc.4).
    The creature is Kraggor's own drawing, small, in pencil lines - never a new character design."""
    x, z = p.get("x", 0.0), p.get("z", 3.0)
    k = k_of(z)
    sx, gy = pxy(x, z, camx)
    w, hh = 2.2 * k * p.get("scale", 1.0), 1.7 * k * p.get("scale", 1.0)
    y0 = gy - p.get("y", 1.6) * k
    ctx.save()
    ctx.translate(sx, y0 + hh / 2)
    ctx.rotate(p.get("tilt", -0.05))
    ctx.rectangle(-w / 2, -hh / 2, w, hh)                          # yellowed paper
    ctx.set_source_rgb(0.96, 0.92, 0.8)
    ctx.fill_preserve()
    ctx.set_source_rgba(0.55, 0.45, 0.3, 0.8)
    ctx.set_line_width(max(1.0, 0.03 * k))
    ctx.stroke()
    ctx.save()
    ctx.rectangle(-w / 2, -hh / 2, w, hh)
    ctx.clip()
    ctx.push_group()
    x0_, y0_, ew, eh = kraggor_ext()
    s_ = 0.82 * hh / eh
    kraggor_head(ctx, 3.0, dict(mode="smile", sx=(-s_ * (x0_ + ew / 2) - w * 0.08) / W, scale=s_ * 1080.0 / H),
                 stands_top=-hh / 2 + 0.08 * hh - s_ * y0_)
    ctx.set_operator(cairo.OPERATOR_ATOP)                          # green pencil: keep the shape, soften the colour
    ctx.rectangle(-w, -hh, 2 * w, 2 * hh)
    ctx.set_source_rgba(0.35, 0.6, 0.35, 0.55)
    ctx.fill()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(0.85)
    ctx.restore()
    se.draw_text(ctx, "K.", w * 0.32, hh * 0.32, 0.32 * k, fill=(0.25, 0.2, 0.15), stroke=(0.96, 0.92, 0.8), sw=1)
    ctx.restore()


def _photo_truck(ctx, cx, ground, length, vk, colors, mustache, t, face=1):
    """A character's vehicle inside an old photo (the real vehicle drawing, small)."""
    sc = length / 5.6
    ctx.save()
    ctx.translate(cx, ground - 1.81 * sc)
    ctx.scale(sc * face, -sc)
    for lx in (-1.9, 1.9):
        se.draw_wheel(ctx, lx, 0.5 - 1.81, 0.0, 0.5, False)
    veh = se.VEHICLES[vk]
    old, old_acc = veh["color"], veh.get("accent")
    veh["color"], veh["accent"] = colors
    se.draw_body(ctx, vk, veh, False, t)
    veh["color"] = old
    if old_acc is None:
        veh.pop("accent", None)
    else:
        veh["accent"] = old_acc
    CUR["aid"], CUR["mustache"] = "photo", mustache
    EMO["photo"], TALK["photo"] = "happy", 0.0
    story_face(ctx, vk, "happy", t)
    CUR["aid"], CUR["mustache"] = None, False
    ctx.restore()


def tear_edge(x0, y0, w, h, seed):
    """The jagged tear line of a torn print - deterministic from its seed, so the piece found later (scene 13)
    fits exactly (owner 2026-10-06: 'sobekannya harus nyambung')."""
    rng = np.random.default_rng(seed)
    n = 11
    xs = x0 + w * (0.6 + rng.uniform(-0.035, 0.035, n + 1))
    return [(float(xs[q]), y0 + h * q / n) for q in range(n + 1)]


def draw_print(ctx, kind, x0, y0, w, h, t, tear=None, side="left"):
    """An old photo print (white border). kind: town | little | mountain. tear=seed: only one side of the tear."""
    b = min(w, h) * 0.05
    ctx.save()
    if tear is not None:                                           # keep one side of the tear (border included)
        e = tear_edge(x0, y0, w, h, tear)
        if side == "left":
            ctx.move_to(x0, y0)
            for pt in e:
                ctx.line_to(*pt)
            ctx.line_to(x0, y0 + h)
        else:
            ctx.move_to(x0 + w, y0)
            for pt in e:
                ctx.line_to(*pt)
            ctx.line_to(x0 + w, y0 + h)
        ctx.close_path()
        ctx.clip()
    ctx.rectangle(x0, y0, w, h)
    ctx.set_source_rgb(0.97, 0.95, 0.9)
    ctx.fill()
    ix, iy, iw, ih = x0 + b, y0 + b, w - 2 * b, h - 2 * b
    ctx.save()
    ctx.rectangle(ix, iy, iw, ih)
    ctx.clip()
    ground = iy + ih * 0.86
    if kind == "mountain":                                         # young Grandpa on a mountain road at dusk, and
        g = cairo.LinearGradient(0, iy, 0, iy + ih)                # (right of the tear) little Kraggor, smiling
        g.add_color_stop_rgb(0, 0.55, 0.42, 0.62)
        g.add_color_stop_rgb(0.6, 0.98, 0.7, 0.45)
        ctx.rectangle(ix, iy, iw, ih)
        ctx.set_source(g)
        ctx.fill()
        for mx, mh, col in ((0.15, 0.55, (0.42, 0.35, 0.5)), (0.55, 0.7, (0.36, 0.3, 0.45)), (0.9, 0.5, (0.42, 0.35, 0.5))):
            ctx.move_to(ix + iw * (mx - 0.3), ground)
            ctx.line_to(ix + iw * mx, ground - ih * mh)
            ctx.line_to(ix + iw * (mx + 0.3), ground)
            ctx.close_path()
            ctx.set_source_rgb(*col)
            ctx.fill()
        for q in range(9):                                         # pines
            px = ix + iw * (0.04 + q * 0.12)
            ph = ih * (0.16 + 0.05 * (q % 3))
            ctx.move_to(px - ph * 0.3, ground)
            ctx.line_to(px, ground - ph)
            ctx.line_to(px + ph * 0.3, ground)
            ctx.close_path()
            ctx.set_source_rgb(0.2, 0.32, 0.25)
            ctx.fill()
        ctx.rectangle(ix, ground, iw, ih * 0.14)
        ctx.set_source_rgb(0.4, 0.36, 0.34)
        ctx.fill()
        _photo_truck(ctx, ix + iw * 0.3, ground + ih * 0.04, iw * 0.42, "icecream",
                     ((0.95, 0.9, 0.78), (0.62, 0.42, 0.25)), False, t)
        x0e, y0e, ew, eh = kraggor_ext()                           # little Kraggor: the real drawing, mirrored so
        s_ = ih * 0.62 / eh                                        # his tail reaches left across the tear
        kx = ix + iw * 0.74                                       # close to the tear: the tail tip crosses it
        ctx.save()
        ctx.translate(kx, 0)
        ctx.scale(-1, 1)
        ctx.translate(-kx, 0)
        kraggor_head(ctx, 3.0, dict(mode="smile", sx=(kx - s_ * (x0e + ew / 2)) / W, scale=s_ * 1080.0 / H),
                     stands_top=ground + ih * 0.04 - s_ * (y0e + eh))
        ctx.restore()
        tx = ix + iw * 0.5                                          # his tail sweeps left past the tear: its tip is
        ty = ground - ih * 0.08                                     # the green hint on the album side (sc.4), the rest
        ctx.move_to(kx - iw * 0.06, ty - ih * 0.06)                # joins him on the missing piece (sc.13)
        ctx.curve_to(kx - iw * 0.14, ty - ih * 0.02, tx + iw * 0.06, ty + ih * 0.02, tx, ty - ih * 0.05)
        ctx.curve_to(tx + iw * 0.05, ty + ih * 0.05, kx - iw * 0.12, ty + ih * 0.06, kx - iw * 0.05, ty + ih * 0.02)
        ctx.close_path()
        ctx.set_source_rgb(*KR_BODY)
        ctx.fill_preserve()
        ctx.set_source_rgb(*KR_DARK)
        ctx.set_line_width(max(1.0, iw * 0.006))
        ctx.stroke()
        for fx in (0.08, 0.15):                                     # back spikes along the tail
            px_ = tx + iw * fx
            ctx.move_to(px_ - iw * 0.012, ty - ih * 0.03)
            ctx.line_to(px_, ty - ih * 0.07)
            ctx.line_to(px_ + iw * 0.012, ty - ih * 0.03)
            ctx.close_path()
            ctx.set_source_rgb(*KR_DARK)
            ctx.fill()
    elif kind == "little":                                         # Grandpa and Little Sprinkles in the park
        ctx.rectangle(ix, iy, iw, ih)
        ctx.set_source_rgb(0.7, 0.86, 0.95)
        ctx.fill()
        ctx.rectangle(ix, iy + ih * 0.62, iw, ih * 0.38)
        ctx.set_source_rgb(0.55, 0.78, 0.45)
        ctx.fill()
        ctx.arc(ix + iw * 0.82, iy + ih * 0.2, ih * 0.1, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 0.9, 0.5)
        ctx.fill()
        _photo_truck(ctx, ix + iw * 0.33, ground, iw * 0.5, "icecream", ((0.93, 0.86, 0.7), (0.62, 0.42, 0.25)), True, t)
        _photo_truck(ctx, ix + iw * 0.76, ground, iw * 0.3, "icecream", ((1.0, 0.6, 0.76), (0.6, 0.9, 0.8)), False, t, -1)
    else:                                                          # town: Grandpa's truck on Main Street
        ctx.rectangle(ix, iy, iw, ih)
        ctx.set_source_rgb(0.75, 0.86, 0.95)
        ctx.fill()
        for q, col in enumerate(((0.95, 0.75, 0.6), (0.7, 0.8, 0.92), (0.95, 0.88, 0.65), (0.82, 0.72, 0.9))):
            ctx.rectangle(ix + iw * q * 0.26, iy + ih * (0.25 + 0.05 * (q % 2)), iw * 0.24, ih * 0.5)
            ctx.set_source_rgb(*col)
            ctx.fill()
        ctx.rectangle(ix, ground, iw, ih * 0.14)
        ctx.set_source_rgb(0.45, 0.45, 0.48)
        ctx.fill()
        _photo_truck(ctx, ix + iw * 0.5, ground + ih * 0.03, iw * 0.55, "icecream",
                     ((0.93, 0.86, 0.7), (0.62, 0.42, 0.25)), True, t)
    ctx.restore()
    ctx.rectangle(ix, iy, iw, ih)                                   # old, faded print
    ctx.set_source_rgba(0.95, 0.82, 0.6, 0.28)
    ctx.fill()
    ctx.restore()
    if tear is not None:                                           # the torn paper fibres along the edge
        e = tear_edge(x0, y0, w, h, tear)
        ctx.move_to(*e[0])
        for pt in e[1:]:
            ctx.line_to(*pt)
        ctx.set_source_rgba(1, 1, 1, 0.9)
        ctx.set_line_width(max(1.0, w * 0.012))
        ctx.stroke()


def draw_album(ctx, p, camx, t):
    """Grandpa's photo album, open (S01E02 sc.4): two cream pages with photo corners; the right page holds the torn
    mountain photo (a NEW photo - the Ep.1 wall photo never had Kraggor in it, continuity K01)."""
    x, z = p.get("x", 0.0), p.get("z", 2.9)
    k = k_of(z)
    sx, gy = pxy(x, z, camx)
    W_, H_ = 4.8 * k, 2.6 * k
    top = gy - p.get("y", 2.8) * k
    x0 = sx - W_ / 2
    se.rrect(ctx, x0 - 0.12 * k, top - 0.12 * k, W_ + 0.24 * k, H_ + 0.24 * k, 0.12 * k)   # cover
    ctx.set_source_rgb(0.42, 0.18, 0.14)
    ctx.fill()
    for q in range(2):                                             # pages
        ctx.rectangle(x0 + q * W_ / 2 + (0.03 * k if q else 0), top, W_ / 2 - 0.03 * k, H_)
        ctx.set_source_rgb(0.96, 0.92, 0.82)
        ctx.fill()
    g = cairo.LinearGradient(sx - 0.25 * k, 0, sx + 0.25 * k, 0)   # spine shadow
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(0.5, 0, 0, 0, 0.35)
    g.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.rectangle(sx - 0.25 * k, top, 0.5 * k, H_)
    ctx.set_source(g)
    ctx.fill()
    pw, ph = 1.5 * k, 1.05 * k                                     # left page: two small photos
    draw_print(ctx, "town", x0 + 0.35 * k, top + 0.2 * k, pw, ph, t)
    draw_print(ctx, "little", x0 + 0.7 * k, top + 1.38 * k, pw, ph, t)
    bw, bh = 2.0 * k, 1.5 * k                                      # right page: the torn one, bigger
    draw_print(ctx, "mountain", sx + 0.2 * k, top + 0.45 * k, bw, bh, t, tear=p.get("tear", 7), side="left")
    se.draw_text(ctx, "Mountain Road", sx + 0.2 * k + bw * 0.32, top + 0.45 * k + bh + 0.22 * k, 0.17 * k,
                 fill=(0.35, 0.25, 0.18), stroke=(0.96, 0.92, 0.82), sw=1)
    for (cx_, cy_) in ((sx + 0.2 * k, top + 0.45 * k), (sx + 0.2 * k, top + 0.45 * k + bh)):   # photo corners
        ctx.move_to(cx_ - 0.12 * k, cy_)
        ctx.line_to(cx_ + 0.18 * k, cy_)
        ctx.line_to(cx_, cy_ + (0.18 * k if cy_ < top + H_ / 2 else -0.18 * k))
        ctx.close_path()
        ctx.set_source_rgb(0.2, 0.15, 0.12)
        ctx.fill()


def draw_photo_piece(ctx, p, camx, t):
    """The missing right part of the mountain photo (scene 13 payoff): same tear seed -> the edges fit."""
    x, z = p.get("x", 0.0), p.get("z", 2.9)
    k = k_of(z)
    sx, gy = pxy(x, z, camx)
    bw, bh = 2.0 * k * p.get("scale", 1.0), 1.5 * k * p.get("scale", 1.0)
    draw_print(ctx, "mountain", sx - bw / 2, gy - p.get("y", 2.0) * k, bw, bh, t, tear=p.get("tear", 7),
               side=p.get("side", "right"))


def draw_frame_photo(ctx, p, camx, t):
    """Old photo on the garage wall: Grandpa Cone (cream truck, glasses, beard) centred in a wooden frame."""
    x, z = p.get("x", -2.0), p.get("z", 3.6)
    k = k_of(z)
    sx, gy = pxy(x, z, camx)
    w, hh = 3.2 * k * p.get("scale", 1.0), 2.4 * k * p.get("scale", 1.0)
    y0 = gy - p.get("y", 5.0) * k
    se.rrect(ctx, sx - w / 2 - 0.22 * k, y0 - 0.22 * k, w + 0.44 * k, hh + 0.44 * k, 0.1 * k)
    ctx.set_source_rgb(0.45, 0.28, 0.12)
    ctx.fill()
    ctx.save()
    ctx.rectangle(sx - w / 2, y0, w, hh)
    ctx.clip()
    g = cairo.LinearGradient(0, y0, 0, y0 + hh)                     # old holiday photo: sky, sea, sand, sun
    g.add_color_stop_rgb(0, 0.62, 0.78, 0.86)
    g.add_color_stop_rgb(0.55, 0.86, 0.88, 0.84)
    ctx.rectangle(sx - w / 2, y0, w, hh)
    ctx.set_source(g)
    ctx.fill()
    ctx.arc(sx + w * 0.3, y0 + hh * 0.2, hh * 0.1, 0, 2 * math.pi)
    ctx.set_source_rgb(1, 0.88, 0.55)
    ctx.fill()
    ctx.rectangle(sx - w / 2, y0 + hh * 0.5, w, hh * 0.16)
    ctx.set_source_rgb(0.32, 0.58, 0.72)
    ctx.fill()
    ctx.rectangle(sx - w / 2, y0 + hh * 0.66, w, hh * 0.34)
    ctx.set_source_rgb(0.9, 0.8, 0.58)
    ctx.fill()
    sc = w * 0.56 / 5.6                                   # truck 5.6 m long, wheels on the sand
    ground = y0 + hh * 0.86
    ctx.translate(sx, ground - 1.81 * sc)
    ctx.scale(sc, -sc)
    for lx in (-1.9, 1.9):
        se.draw_wheel(ctx, lx, 0.5 - 1.81, 0.0, 0.5, False)
    veh = se.VEHICLES["icecream"]
    old, old_acc = veh["color"], veh.get("accent")
    veh["color"], veh["accent"] = (0.93, 0.86, 0.70), (0.62, 0.42, 0.25)
    se.draw_body(ctx, "icecream", veh, False, t)
    veh["color"] = old
    if old_acc is None:
        veh.pop("accent", None)
    else:
        veh["accent"] = old_acc
    CUR["aid"], CUR["mustache"] = "photo", True
    EMO["photo"], TALK["photo"] = "happy", 0.0
    story_face(ctx, "icecream", "happy", t)
    CUR["aid"], CUR["mustache"] = None, False
    ctx.restore()
    ctx.rectangle(sx - w / 2, y0, w, hh)                            # faded print
    ctx.set_source_rgba(0.95, 0.85, 0.65, 0.25)
    ctx.fill()
    if p.get("glow"):
        ctx.rectangle(sx - w / 2, y0, w, hh)
        ctx.set_source_rgba(1, 0.9, 0.6, 0.25)
        ctx.fill()


def draw_mud(ctx, p, camx, t):
    """A mud puddle on the road (wobbly brown patch across the lanes)."""
    x, w = p.get("x", 0.0), p.get("w", 6.0)
    pts = []
    for i in range(25):
        xx = x - w / 2 + w * i / 24
        pts.append(pxy(xx, -0.4 + 0.25 * math.sin(i * 1.7), camx))
    for i in range(25):
        xx = x + w / 2 - w * i / 24
        pts.append(pxy(xx, 2.6 + 0.3 * math.sin(i * 2.3), camx))
    se.poly(ctx, pts)
    ctx.set_source_rgb(*se.lit((0.36, 0.24, 0.13)))
    ctx.fill()
    for i in range(7):                                              # wet shine
        bx, by = pxy(x - w * 0.35 + i * w * 0.11, 0.6 + (i % 3) * 0.6, camx)
        ctx.save()
        ctx.translate(bx, by)
        ctx.scale(0.5 * k_of(1.0), 0.12 * k_of(1.0))
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(0.6, 0.45, 0.3, 0.6)
        ctx.fill()


def mud_spray(ctx, a, t, camx):
    """Wheels spinning in the mud: brown drops flung backwards."""
    veh = se.VEHICLES[a["key"]]
    k = k_of(a["z"])
    rng = np.random.default_rng(int(t * 30))
    for lx in veh["wheel_x"]:
        wx, gy = pxy(a["x"] + lx * a["small"], a["z"], camx)
        for _ in range(6):
            ph = rng.uniform(0, 1)
            dx = -a["face"] * (0.3 + 1.6 * ph) * k
            dy = -(1.2 * ph - 1.4 * ph * ph) * 2.2 * k
            ctx.arc(wx + dx, gy + dy, rng.uniform(0.08, 0.18) * k, 0, 2 * math.pi)
            ctx.set_source_rgba(0.33, 0.22, 0.12, 0.9)
            ctx.fill()


def nametag(ctx, tag, age, dur):
    """Character introduction (lower third): NAME + who they are, slides in from the left."""
    a = min(1.0, age / 0.5, max(0.0, (dur - age) / 0.6))
    if a <= 0:
        return
    slide = (1 - se.ease_out_back(min(1.0, age / 0.7))) * -W * 0.4
    x0, y0 = W * 0.06 + slide, H * 0.66
    bw, bh = W * 0.42, H * 0.16
    col = tuple(tag.get("color", (1, 0.86, 0.12)))
    se.rrect(ctx, x0, y0, bw, bh, bh * 0.18)
    ctx.set_source_rgba(0.06, 0.05, 0.14, 0.78 * a)
    ctx.fill()
    ctx.rectangle(x0, y0, bh * 0.12, bh)
    ctx.set_source_rgba(*col, a)
    ctx.fill()
    se.draw_text(ctx, tag["name"], x0 + bw / 2, y0 + bh * 0.38, 72 if W > H else 64, fill=col, stroke=(0, 0, 0),
                 sw=5, alpha=a, max_w=bw * 0.86)
    se.draw_text(ctx, tag.get("role", ""), x0 + bw / 2, y0 + bh * 0.76, 34, fill=(1, 1, 1), stroke=(0, 0, 0), sw=2,
                 alpha=a, max_w=bw * 0.9)


def note(ctx, text, age, dur, low=False):
    """Short description box at the top (explains what happens: bumps, crashes, numbers...)."""
    a = min(1.0, age / 0.5, max(0.0, (dur - age) / 0.5))
    if a <= 0:
        return
    bw, bh = W * 0.86, H * 0.085
    y0 = H * (0.22 if low else 0.105)                              # below the letterbox bar (and a caption)
    se.rrect(ctx, (W - bw) / 2, y0, bw, bh, bh * 0.3)
    ctx.set_source_rgba(0.05, 0.05, 0.12, 0.62 * a)
    ctx.fill()
    se.draw_text(ctx, text, W / 2, y0 + bh * 0.52, 38 if W > H else 34, fill=(1, 0.95, 0.75),
                 stroke=(0, 0, 0), sw=3, alpha=a, max_w=bw * 0.94)


def draw_lamp(ctx, camx):
    sx, gy = pxy(1.0, 3.0, camx)
    g = cairo.RadialGradient(sx, gy - 6 * k_of(3), 10, sx, gy - 2 * k_of(3), 9 * k_of(3))
    g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.45)
    g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0.0)
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.set_source(g)
    ctx.fill()


def draw_streetlamps(ctx, prop, camx, t):
    """Street lamps along the far pavement; each can flicker and die at its own scene time ("off": [t, ...]) -
    S01E02 cold open: the lights go out one by one towards the camera before Kraggor's eyes open."""
    z = prop.get("z", 3.4)
    k = k_of(z)
    offs = prop.get("off", [])
    for i, x in enumerate(prop.get("xs", [])):
        sx, gy = pxy(x, z, camx)
        if not -400 < sx < CX * 2 + 400:
            continue
        ctx.rectangle(sx - 0.09 * k, gy - 5.2 * k, 0.18 * k, 5.2 * k)          # pole + arm
        ctx.set_source_rgb(*se.lit((0.25, 0.26, 0.3)))
        ctx.fill()
        ctx.rectangle(sx, gy - 5.2 * k, 0.9 * k, 0.12 * k)
        ctx.fill()
        off_t = offs[i] if i < len(offs) else None
        on = 1.0
        if off_t is not None and t > off_t - 0.5:                  # flicker for half a second, then dark
            on = 0.0 if t >= off_t else (1.0 if int((t - off_t) * 23) % 3 else 0.15)
        hx, hy = sx + 0.9 * k, gy - 5.0 * k
        se.rrect(ctx, hx - 0.28 * k, hy - 0.12 * k, 0.56 * k, 0.22 * k, 0.06 * k)
        ctx.set_source_rgb(*((1.0, 0.92, 0.6) if on > 0.5 else (0.3, 0.3, 0.32)))
        ctx.fill()
        if on > 0.0:                                               # warm pool of light on the road
            g = cairo.RadialGradient(hx, gy, 0.2 * k, hx, gy - 1.5 * k, 4.2 * k)
            g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.42 * on)
            g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0.0)
            se.poly(ctx, [(hx - 0.3 * k, hy), (hx + 0.3 * k, hy), (hx + 2.6 * k, gy + 0.6 * k), (hx - 2.6 * k, gy + 0.6 * k)])
            ctx.set_source(g)
            ctx.fill()


FOOT_PADS = [(-1.25, 0.0, 1.2, 0.95), (1.55, -0.95, 0.62, 0.42), (1.95, 0.0, 0.62, 0.42), (1.55, 0.95, 0.62, 0.42)]
# heel + 3 toes on the GROUND plane (along-road m, across-road m, radius along, radius across) for size 1.0:
# a 5.5 m x 3 m print. User 2026-10-05 (Godot pilot): a print standing on end looked bigger than the road and
# came out in front of the car, so the car seemed to float -> prints lie flat along the road, as Kraggor walked.


def foot_pads(prop):
    """World-space pads of every print: [(n, cx, cz, rx, rz)], left/right feet staggered across the road."""
    sc, d = prop.get("size", 1.0), prop.get("dir", 1)
    z0, stag = prop.get("z", 1.3), prop.get("stagger", 0.45)
    out = []
    for n, x in enumerate(prop.get("xs", [])):
        zc = z0 + (stag if n % 2 else -stag)
        for px, pz, rx, rz in FOOT_PADS:
            out.append((n, x + d * px * sc, zc + pz * sc, rx * sc, rz * sc))
    return out


def ground_ellipse(ctx, x, z, rx, rz, camx, grow=0.0):
    """Path of an ellipse lying on the road (correct depth squash for its distance)."""
    sx, gy = pxy(x, z, camx)
    ry = abs(ground_y(z - rz - grow) - ground_y(z + rz + grow)) / 2
    ctx.save()
    ctx.translate(sx, gy)
    ctx.scale(max(0.01, (rx + grow) * k_of(z)), max(0.01, ry))
    ctx.arc(0, 0, 1.0, 0, 2 * math.pi)
    ctx.restore()


def draw_footprints(ctx, prop, camx, t):
    """Giant three-toed footprints pressed into the road along Kraggor's path, still steaming."""
    pads = foot_pads(prop)
    for grow, col in ((0.28, (0.62, 0.64, 0.7, 0.85)), (0.0, (0.03, 0.03, 0.04, 0.95))):   # crushed rim, deep print
        for n, x, z, rx, rz in pads:
            ctx.new_sub_path()
            ground_ellipse(ctx, x, z, rx, rz, camx, grow)
        ctx.set_source_rgba(*col)
        ctx.fill()
    sc, d = prop.get("size", 1.0), prop.get("dir", 1)
    for n, x in enumerate(prop.get("xs", [])):
        zc = prop.get("z", 1.3) + (prop.get("stagger", 0.45) if n % 2 else -prop.get("stagger", 0.45))
        hx = x - d * 1.25 * sc
        for q in range(7):                                         # cracks radiating out from the heel
            ang = q * 0.9 + n
            ctx.move_to(*pxy(hx + math.cos(ang) * 1.5 * sc, zc + math.sin(ang) * 1.15 * sc, camx))
            ctx.line_to(*pxy(hx + math.cos(ang) * 2.5 * sc, zc + math.sin(ang) * 1.75 * sc, camx))
        ctx.set_source_rgba(0.55, 0.57, 0.62, 0.7)
        ctx.set_line_width(max(1.5, 0.06 * k_of(zc)))
        ctx.stroke()
        if prop.get("steam", True):                                # thin wisps rising and fading
            k = k_of(zc)
            sx, gy = pxy(x, zc, camx)
            for j in range(4):
                ph = (t * 0.45 + j * 0.25 + n * 0.17) % 1.0
                wx = sx + (j - 1.5) * 0.8 * k + math.sin(t * 1.3 + j) * 0.2 * k
                wy = gy - ph * 2.6 * k
                ctx.arc(wx, wy, (0.25 + 0.5 * ph) * k, 0, 2 * math.pi)
                ctx.set_source_rgba(0.88, 0.9, 0.95, 0.38 * (1 - ph))
                ctx.fill()


def draw_contact(ctx, a, camx):
    """Soft contact shadow where the tyres meet the road: without it a flat car over a 3D road reads as floating
    (Godot pilot, user 2026-10-05). Fades as the car leaves the ground."""
    veh = se.VEHICLES[a["key"]]
    k = k_of(a["z"]) * a["small"]
    sx, gy = pxy(a["x"], a["z"], camx)
    al = 0.42 * max(0.0, 1.0 - a["h"] / 2.5)
    if al <= 0.01:
        return
    rx, ry = veh["body"][0] * 0.56 * k, 0.32 * k
    g = cairo.RadialGradient(0, 0, 0.0, 0, 0, 1.0)
    g.add_color_stop_rgba(0, 0, 0, 0, al)
    g.add_color_stop_rgba(0.7, 0, 0, 0, al * 0.6)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.0)
    ctx.save()
    ctx.translate(sx, gy + 0.08 * k)
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1.0, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.restore()


def draw_fog(ctx, t, density):
    """Night fog drifting across the frame in soft layers (screen space, after the world)."""
    d = 0.6 if density is True else float(density)
    for j in range(5):
        y = H * (0.45 + 0.1 * j)
        x0 = ((t * (12 + 6 * j)) % (W * 0.8)) - W * 0.4
        for rep_ in range(3):
            cx_ = x0 + rep_ * W * 0.8
            g = cairo.RadialGradient(cx_, y, 0, cx_, y, W * 0.45)
            g.add_color_stop_rgba(0, 0.75, 0.78, 0.85, 0.16 * d)
            g.add_color_stop_rgba(1, 0.75, 0.78, 0.85, 0.0)
            ctx.rectangle(0, 0, W, H)
            ctx.set_source(g)
            ctx.fill()


def draw_desk(ctx, d, camx):
    """Registration booth (behind the actors): stage, two poles with the sign board, striped canopy, flags."""
    x, z = d.get("x", 3.6), d.get("z", 2.6)
    k = k_of(z)
    sx, gy = pxy(x, z, camx)
    w = 9.0 * k
    se.rrect(ctx, sx - w / 2, gy - 0.7 * k, w, 0.75 * k, 0.1 * k)            # stage
    ctx.set_source_rgb(*se.lit((0.45, 0.3, 0.2)))
    ctx.fill()
    ctx.rectangle(sx - w / 2, gy - 0.78 * k, w, 0.12 * k)
    ctx.set_source_rgb(*se.lit((0.65, 0.45, 0.3)))
    ctx.fill()
    for px in (-3.9, 3.9):                                                      # poles
        ctx.rectangle(sx + px * k - 0.12 * k, gy - 6.4 * k, 0.24 * k, 5.7 * k)
        ctx.set_source_rgb(*se.lit((0.55, 0.55, 0.6)))
        ctx.fill()
    top, bot = gy - 4.6 * k, gy - 3.7 * k                                       # striped canopy
    for i in range(10):
        x0 = sx - 4.2 * k + i * 0.84 * k
        se.poly(ctx, [(x0, top), (x0 + 0.84 * k, top), (x0 + 0.9 * k, bot), (x0 - 0.06 * k, bot)])
        ctx.set_source_rgb(*se.lit((0.9, 0.15, 0.2) if i % 2 else (1, 1, 1)))
        ctx.fill()
        ctx.arc(x0 + 0.42 * k, bot, 0.42 * k, 0, math.pi)
        ctx.fill()
    se.rrect(ctx, sx - 3.6 * k, gy - 6.6 * k, 7.2 * k, 1.5 * k, 0.15 * k)      # sign board on the poles
    ctx.set_source_rgb(0.15, 0.3, 0.75)
    ctx.fill_preserve()
    ctx.set_source_rgb(1, 0.86, 0.12)
    ctx.set_line_width(0.12 * k)
    ctx.stroke()
    se.draw_text(ctx, d.get("text", "RACE REGISTRATION"), sx, gy - 5.85 * k, 0.75 * k, fill=(1, 1, 1),
                 stroke=(0.1, 0.1, 0.3), sw=2, max_w=6.8 * k)
    for i in range(12):                                                         # little flags on a string
        fx = sx - 3.9 * k + i * 0.71 * k
        fy = gy - 6.75 * k - 0.35 * k * math.sin(math.pi * i / 11)
        se.poly(ctx, [(fx, fy), (fx + 0.5 * k, fy), (fx + 0.25 * k, fy + 0.5 * k)])
        ctx.set_source_rgb(*[(1, 0.3, 0.3), (0.3, 0.6, 1), (1, 0.85, 0.2), (0.4, 0.85, 0.4)][i % 4])
        ctx.fill()


def draw_desk_front(ctx, d, camx):
    """The registration table: drawn after the actors, in front of the official standing behind it."""
    x, z = d.get("table_x", d.get("x", 3.6)), d.get("table_z", 1.25)
    k = k_of(z)
    sx, gy = pxy(x, z, camx)
    se.rrect(ctx, sx - 2.0 * k, gy - 1.25 * k, 4.0 * k, 1.25 * k, 0.08 * k)
    ctx.set_source_rgb(*se.lit((0.55, 0.35, 0.2)))
    ctx.fill()
    se.rrect(ctx, sx - 2.15 * k, gy - 1.35 * k, 4.3 * k, 0.55 * k, 0.08 * k)  # table cloth
    ctx.set_source_rgb(*se.lit((0.97, 0.97, 0.97)))
    ctx.fill()
    se.draw_text(ctx, "SIGN UP", sx, gy - 1.07 * k, 0.32 * k, fill=(0.85, 0.15, 0.2), stroke=(1, 1, 1), sw=1)


def draw_podium(ctx, camx):
    for i, (x, hh) in enumerate(((-3.2, 1.2), (0.0, 1.9), (3.2, 0.8))):
        k = k_of(1.0)
        sx, gy = pxy(x, 1.0, camx)
        ctx.rectangle(sx - 1.5 * k, gy - hh * k, 3.0 * k, hh * k)
        ctx.set_source_rgb(*se.lit([(0.75, 0.75, 0.8), (1, 0.82, 0.2), (0.8, 0.5, 0.25)][i]))
        ctx.fill()


def hill_h(x):
    """Height (m) of the scene's hill at x: ramp up x0->x1, plateau to x2, down to x3."""
    hl = SCENE.get("hill")
    if not hl:
        return 0.0, 0.0
    x0, x1, x2, x3, hh = hl["x0"], hl["x1"], hl["x2"], hl["x3"], hl["h"]
    if x <= x0 or x >= x3:
        return 0.0, 0.0
    if x < x1:
        f = (x - x0) / (x1 - x0)
        return hh * f * f * (3 - 2 * f), hh * 6 * f * (1 - f) / (x1 - x0)
    if x <= x2:
        return hh, 0.0
    f = (x - x2) / (x3 - x2)
    return hh * (1 - f * f * (3 - 2 * f)), -hh * 6 * f * (1 - f) / (x3 - x2)


def draw_hill(ctx, camx):
    hl = SCENE.get("hill")
    if not hl:
        return
    pts_back, pts_front = [], []
    for i in range(61):
        x = hl["x0"] + (hl["x3"] - hl["x0"]) * i / 60
        hh, _ = hill_h(x)
        pts_back.append((x, hh))
    k_b, k_f = k_of(3.2), k_of(-0.6)
    poly = [((x - camx) * k_b + CX, ground_y(3.2) - hh * k_b) for x, hh in pts_back]
    poly += [((x - camx) * k_f + CX, ground_y(-0.6) - hh * k_f) for x, hh in reversed(pts_back)]
    se.poly(ctx, poly)
    ctx.set_source_rgb(*se.lit((0.45, 0.32, 0.2)))                 # earth ramp (the road climbs it)
    ctx.fill()
    side = [((x - camx) * k_f + CX, ground_y(-0.6) - hh * k_f) for x, hh in pts_back]
    side += [((hl["x3"] - camx) * k_f + CX, ground_y(-0.6)), ((hl["x0"] - camx) * k_f + CX, ground_y(-0.6))]
    se.poly(ctx, side)
    ctx.set_source_rgb(*se.lit((0.35, 0.25, 0.15)))
    ctx.fill()
    edge = [((x - camx) * k_b + CX, ground_y(3.2) - hh * k_b) for x, hh in pts_back]
    ctx.move_to(*edge[0])
    for q in edge[1:]:
        ctx.line_to(*q)
    ctx.set_source_rgb(*se.lit((0.3, 0.55, 0.25)))
    ctx.set_line_width(0.5 * k_b)
    ctx.stroke()


def glow_eyes(ctx, t, spec):
    """A pair of giant yellow eyes glowing in the dark (Kraggor, far away)."""
    sx, sy, r = spec.get("sx", 0.8) * W, spec.get("sy", 0.3) * H, spec.get("r", 14) * H / 1080
    if spec.get("silhouette"):                                     # Kraggor's REAL head (horns, spikes), almost black
        ksc = spec.get("kscale", 0.5)                              # in the fog; the eyes glow in its own eye spots
        base = sy - ksc * (H / 1080) * (1.2 * 40 + 40 * KR_EYES[0][1])
        ctx.push_group()
        kraggor_head(ctx, 3.0, dict(mode="calm", sx=sx / W, sy=base / H, scale=ksc))
        ctx.set_operator(cairo.OPERATOR_ATOP)
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgb(0.03, 0.035, 0.06)
        ctx.fill()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(spec.get("silhouette", 0.6))
        r = (KR_EYES[1][0] - KR_EYES[0][0]) * 40 / 4.8 * ksc * (H / 1080)   # glow pair spacing = Kraggor's eyes
    if spec.get("open") is not None:                               # eyes opening slowly (0..1 given by the shot)
        r *= max(0.05, min(1.0, spec["open"]))
    if (t * 0.6) % 3.0 < 0.12:                                     # slow blink
        return
    for d in (-1, 1):
        g = cairo.RadialGradient(sx + d * r * 2.4, sy, 0, sx + d * r * 2.4, sy, r * 3)
        g.add_color_stop_rgba(0, 1, 0.9, 0.2, 0.95)
        g.add_color_stop_rgba(0.35, 1, 0.8, 0.1, 0.6)
        g.add_color_stop_rgba(1, 1, 0.8, 0.1, 0.0)
        ctx.arc(sx + d * r * 2.4, sy, r * 3, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
        ctx.arc(sx + d * r * 2.4, sy, r * 0.35, 0, 2 * math.pi)
        ctx.set_source_rgb(0.85, 0.15, 0.05)
        ctx.fill()


_KR_EXT = {}


def kraggor_ext():
    """Ink box of the whole Kraggor (calm, head + body) at unit drawing scale, origin = kraggor_head anchor."""
    if not _KR_EXT:
        rs = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
        c = cairo.Context(rs)
        kraggor_head(c, 3.0, dict(mode="calm", sx=0.0, scale=1080.0 / H), stands_top=0.0)
        _KR_EXT["box"] = rs.ink_extents()
    return _KR_EXT["box"]


KR_EYE_UNIT = [(-76.0, -240.0), (76.0, -240.0)]                 # eye centres at unit scale (same spots glow_eyes uses)


def kraggor_far_geom(spec, camx, ground_hide=True):
    """Where the distant Kraggor stands, in pre-camera px: (sx_px, base_y, unit->px scale).
    spec: x (world m), dist (m from camera), height (m). True perspective size; in 2.5D the feet are pushed down
    behind the far ground edge so he stands BEHIND the town (the cairo world has no real ground out there)."""
    x0, y0, w, h = kraggor_ext()
    kd = F_PERSP / (DZ * spec.get("dist", 78.0))
    s = spec.get("height", 34.0) * kd / h
    gx = CX + (spec.get("x", 30.0) - camx) * kd
    feet = Y_H + CAM_H * kd
    if ground_hide:                                                # + sink: the 2.5D skyline is low and sparse, so his
        feet = max(feet, ground_y(6.5)) + spec.get("sink", 0.3) * spec.get("height", 34.0) * kd   # legs go below it
    return gx - s * (x0 + w / 2), feet - s * (y0 + h), s


def kraggor_far(ctx, t, u, spec, camx):
    """Kraggor far away and tall, behind the town: an almost-black silhouette with glowing eyes (user 2026-10-05:
    'jauh dan tinggi, badan + kepala di balik gedung', size matching the footprints). Drawn right after the sky,
    so the town, trees and ground cover his legs."""
    sxp, base, s = kraggor_far_geom(spec, camx)
    ctx.push_group()
    kraggor_head(ctx, 3.0, dict(mode="calm", sx=sxp / W, scale=s * 1080.0 / H), stands_top=base)
    ctx.set_operator(cairo.OPERATOR_ATOP)
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.set_source_rgb(*spec.get("tint", (0.025, 0.03, 0.055)))
    ctx.fill()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(spec.get("silhouette", 0.92))
    op = 1.0
    if spec.get("eyes_at") is not None:                            # eyes open a beat after the cut
        op = max(0.0, min(1.0, (u - spec["eyes_at"]) / 0.5))
    if op <= 0.0 or (t * 0.6) % 3.0 < 0.12:
        return
    r = max(3.0, 32.0 * s) * (0.3 + 0.7 * op)
    for ex, ey in KR_EYE_UNIT:
        px, py = sxp + ex * s, base + ey * s
        g = cairo.RadialGradient(px, py, 0, px, py, r * 3)
        g.add_color_stop_rgba(0, 1, 0.9, 0.2, 0.95 * op)
        g.add_color_stop_rgba(0.35, 1, 0.8, 0.1, 0.6 * op)
        g.add_color_stop_rgba(1, 1, 0.8, 0.1, 0.0)
        ctx.arc(px, py, r * 3, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
        ctx.arc(px, py, r * 0.35, 0, 2 * math.pi)
        ctx.set_source_rgb(0.85, 0.15, 0.05)
        ctx.fill()


def draw_finish(ctx, x, camx):
    for row in range(8):
        za, zb = -0.6 + row * 0.5, -0.1 + row * 0.5
        for col in range(2):
            xa = x + col * 0.9
            se.poly(ctx, [pxy(xa, za, camx), pxy(xa + 0.9, za, camx), pxy(xa + 0.9, zb, camx), pxy(xa, zb, camx)])
            ctx.set_source_rgb(*((0.05, 0.05, 0.05) if (row + col) % 2 else (1, 1, 1)))
            ctx.fill()


def draw_foot(ctx, x, z, camx, drop):
    """Kraggor's giant foot (own design) blocking the track; drop 0 = on the ground, 1 = high in the sky."""
    k = k_of(z)
    sx, gy = pxy(x, z, camx)
    fy = gy - drop * 22 * k
    body = se.lit((0.24, 0.55, 0.36))
    dark = se.shade((0.24, 0.55, 0.36), 0.62)
    ctx.rectangle(sx - 1.7 * k, -4000, 3.4 * k, fy - 1.0 * k + 4000)
    ctx.set_source_rgb(*body)
    ctx.fill()
    se.rrect(ctx, sx - 2.7 * k, fy - 1.7 * k, 5.4 * k, 1.8 * k, 0.6 * k)
    ctx.set_source_rgb(*body)
    ctx.fill_preserve()
    ctx.set_source_rgb(*dark)
    ctx.set_line_width(max(2, 0.1 * k))
    ctx.stroke()
    for q in (-1, 0, 1):
        cx = sx + q * 1.75 * k
        ctx.arc(cx, fy - 0.5 * k, 0.8 * k, 0, 2 * math.pi)
        ctx.set_source_rgb(*body)
        ctx.fill()
        se.poly(ctx, [(cx - 0.35 * k, fy - 0.1 * k), (cx + 0.35 * k, fy - 0.1 * k), (cx + 0.15 * k, fy + 0.45 * k)])
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()


def stands_top_world():
    rows = 3
    zb = SM.ZC + SM.HZ0 + 3.0 + (rows - 1) * 1.6
    return ground_y(zb) - rows * 1.25 * k_of(zb)


KR_BODY, KR_DARK = (0.24, 0.55, 0.36), (0.15, 0.34, 0.22)


def kraggor_body(ctx, roar):
    """Kraggor's body in head units (own design): shoulders, metal belly, clawed arms, legs, tail.
    Origin = neck base used by smash25d.draw_kraggor_head; y grows downwards."""
    def fill(path_fn, col):
        path_fn()
        ctx.set_source_rgb(*se.lit(col))
        ctx.fill_preserve()
        ctx.set_source_rgb(*KR_DARK)
        ctx.set_line_width(0.3)
        ctx.stroke()
    fill(lambda: (ctx.move_to(5.5, 9), ctx.curve_to(12, 11, 15, 8, 16, 3), ctx.curve_to(15, 9, 11, 14, 5, 13),
                  ctx.close_path()), KR_BODY)                                           # tail
    for lx in (-3.6, 1.2):                                                               # legs + feet
        fill(lambda lx=lx: se.rrect(ctx, lx, 11, 2.6, 7.5, 0.8), KR_BODY)
        fill(lambda lx=lx: se.rrect(ctx, lx - 0.8, 17.6, 4.2, 1.6, 0.6), KR_BODY)
    fill(lambda: se.rrect(ctx, -6.2, -3.6, 12.4, 16.0, 3.5), KR_BODY)                   # torso / shoulders
    fill(lambda: se.rrect(ctx, -3.6, 0.0, 7.2, 10.5, 1.6), (0.66, 0.68, 0.76))          # metal belly plate
    for yy in (2.6, 5.2, 7.8):
        ctx.move_to(-3.3, yy)
        ctx.line_to(3.3, yy)
        ctx.set_source_rgb(0.45, 0.46, 0.52)
        ctx.set_line_width(0.25)
        ctx.stroke()
    lift = -6.5 * roar
    for sgn in (-1, 1):                                                                  # arms with white claws
        hx, hy = sgn * 9.6, 7.0 + lift
        fill(lambda sgn=sgn, hx=hx, hy=hy: (ctx.move_to(sgn * 5.2, -1.6), ctx.line_to(hx + sgn * 0.6, hy - 1.2),
                                           ctx.line_to(hx - sgn * 1.4, hy + 1.0), ctx.line_to(sgn * 4.8, 2.2),
                                           ctx.close_path()), KR_BODY)
        for c in range(3):
            cx = hx - sgn * 0.6 + c * 0.75 * sgn
            se.poly(ctx, [(cx - 0.3, hy + 0.6), (cx + 0.3, hy + 0.6), (cx, hy + 1.6)])
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()


def kraggor_smile(ctx, a):
    """Happy Kraggor after the ice cream: closed-mouth smile + rosy cheeks, over the head drawing."""
    ctx.save()
    ctx.translate(905, 1.2 * 40)
    ctx.scale(40, 40)
    se.rrect(ctx, -3.8, -4.6, 7.6, 3.4, 0.9)                                           # cover the angry mouth
    ctx.set_source_rgb(*se.lit(KR_BODY))
    ctx.fill()
    ctx.arc(0, -5.2, 2.6, 0.2 * math.pi, 0.8 * math.pi)                                 # big smile
    ctx.set_source_rgb(0.1, 0.05, 0.05)
    ctx.set_line_width(0.45)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    for sgn in (-1, 1):
        ctx.arc(sgn * 3.0, -4.9, 0.8, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 0.5, 0.55, 0.6)
        ctx.fill()
    ctx.restore()


KR_EYES = [(-1.9, -7.2), (1.9, -7.2)]                    # eye centres in kraggor_smile units (head-local)


def kraggor_wink(ctx, eye):
    """Close one eye: a lid in body colour and a happy closed-eye arc."""
    ctx.save()
    ctx.translate(905, 1.2 * 40)
    ctx.scale(40, 40)
    ex, ey = eye
    ctx.arc(ex, ey, 1.25, 0, 2 * math.pi)
    ctx.set_source_rgb(*se.lit(KR_BODY))
    ctx.fill()
    ctx.arc(ex, ey + 0.6, 0.9, 1.15 * math.pi, 1.85 * math.pi)
    ctx.set_source_rgb(0.1, 0.05, 0.05)
    ctx.set_line_width(0.4)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.restore()


def kraggor_mouth(spec, base_y):
    """Screen point of Kraggor's mouth (target of the ice cream)."""
    sc = spec.get("scale", 1.0) * (H / 1080)
    return spec.get("sx", 0.62) * W, base_y + (1.2 - 3.8) * 40 * sc


def kraggor_baby_head(ctx, mood, t, cone_r=0.0):
    """LITTLE Kraggor (S01E02 scene 5 flashback, scene 13 photo): the same design as the grown-up - green dino-robot,
    silver spikes, glowing eyes - but young: a big head, soft brows, a muzzle, no angry teeth. Local frame = the one
    kraggor_smile uses (origin at the neck base, 1 unit = 40 px). mood: calm | scared | munch | smile | sleep.
    cone_r > 0: he holds a strawberry cone (scoop radius in units) up to his mouth."""
    body, metal = KR_BODY, (0.66, 0.68, 0.76)
    dark = se.shade(body, 0.62)
    ctx.save()
    ctx.translate(905, 1.2 * 40)
    ctx.scale(40, 40)
    if cone_r > 0:                                             # the arm + paw + cone (before the head: partly behind it)
        ctx.move_to(5.4, 1.0)
        ctx.line_to(5.0, -2.6)
        ctx.set_source_rgb(*se.lit(body))
        ctx.set_line_width(2.1)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
        se.poly(ctx, [(4.0, -4.4), (6.0, -4.4), (5.0, -1.6)])
        ctx.set_source_rgb(0.9, 0.7, 0.35)
        ctx.fill()
        ctx.arc(5.0, -4.7, cone_r, 0, 2 * math.pi)
        ctx.set_source_rgb(1.0, 0.55, 0.7)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.5, 0.2, 0.3)
        ctx.set_line_width(0.16)
        ctx.stroke()
        ctx.arc(5.0, -2.6, 1.0, 0, 2 * math.pi)                # the paw closes round the cone
        ctx.set_source_rgb(*se.lit(body))
        ctx.fill_preserve()
        ctx.set_source_rgb(*dark)
        ctx.set_line_width(0.2)
        ctx.stroke()
    ctx.translate(0, -2.6)                                     # a baby's head is big: grow it around the neck
    ctx.scale(1.28, 1.28)
    ctx.translate(0, 2.6)
    se.rrect(ctx, -3.0, -3, 6.0, 12, 1.4)                      # neck
    ctx.set_source_rgb(*se.lit(dark))
    ctx.fill()
    for bx in (-2.2, 0.0, 2.2):                                # three small silver back spikes
        se.poly(ctx, [(bx - 0.6, -9.6), (bx, -11.4), (bx + 0.6, -9.6)])
        ctx.set_source_rgb(*se.lit(metal))
        ctx.fill()
    se.rrect(ctx, -4.6, -10.2, 9.2, 7.6, 2.6)                  # head
    ctx.set_source_rgb(*se.lit(body))
    ctx.fill_preserve()
    ctx.set_source_rgb(*dark)
    ctx.set_line_width(0.28)
    ctx.stroke()
    for sgn in (-1, 1):                                        # two little horn nubs
        se.poly(ctx, [(sgn * 3.6 - 0.5, -9.9), (sgn * 3.2, -11.5), (sgn * 2.5 + 0.2, -9.9)])
        ctx.set_source_rgb(*se.lit(metal))
        ctx.fill()
    se.rrect(ctx, -3.3, -5.7, 6.6, 3.3, 1.5)                   # muzzle, a little lighter
    ctx.set_source_rgb(*se.lit((0.34, 0.66, 0.46)))
    ctx.fill_preserve()
    ctx.set_source_rgb(*dark)
    ctx.set_line_width(0.2)
    ctx.stroke()
    for sgn in (-1, 1):
        ctx.arc(sgn * 0.9, -5.0, 0.22, 0, 2 * math.pi)
        ctx.set_source_rgb(*dark)
        ctx.fill()
    for sgn in (-1, 1):                                        # eyes
        ex = sgn * 1.9
        if mood == "sleep":                                    # closed, curved like a sleeping face
            ctx.arc(ex, -7.3, 0.95, 0.12 * math.pi, 0.88 * math.pi)
            ctx.set_source_rgb(0.1, 0.05, 0.05)
            ctx.set_line_width(0.36)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
            continue
        ctx.arc(ex, -7.0, 1.55, 0, 2 * math.pi)                # soft glow
        ctx.set_source_rgba(1, 0.9, 0.2, 0.28)
        ctx.fill()
        ctx.arc(ex, -7.0, 1.2, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 0.9, 0.3)
        ctx.fill()
        pr = {"scared": 0.38, "smile": 0.62, "munch": 0.6}.get(mood, 0.5)
        ctx.arc(ex + sgn * 0.1, -6.9, pr, 0, 2 * math.pi)
        ctx.set_source_rgb(0.75, 0.12, 0.05)
        ctx.fill()
        ctx.arc(ex - sgn * 0.3, -7.45, 0.26, 0, 2 * math.pi)   # a sparkle: the eyes shine
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        if mood == "scared":                                   # worried brows (inner ends up)
            ctx.move_to(ex + sgn * 1.2, -8.2)
            ctx.line_to(ex - sgn * 1.2, -8.85)
        elif mood in ("smile", "munch"):
            ctx.arc(ex, -7.4, 1.5, 1.2 * math.pi, 1.8 * math.pi)
        else:
            ctx.move_to(ex - sgn * 1.2, -8.5)
            ctx.line_to(ex + sgn * 1.2, -8.3)
        ctx.set_source_rgb(*dark)
        ctx.set_line_width(0.34)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    ctx.set_source_rgb(0.1, 0.05, 0.05)
    ctx.set_line_width(0.34)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if mood == "scared":                                       # a wobbling frown + trembling tears
        ctx.arc(0, -2.9 + 0.06 * math.sin(t * 30), 1.4, 1.12 * math.pi, 1.88 * math.pi)
        ctx.stroke()
        for k in range(2):
            ph = (t * 1.5 + k * 0.5) % 1.0
            ctx.save()
            ctx.translate((1.9 + 1.0) * (-1 if k == 0 else 1), -6.0 + ph * 2.4)
            ctx.scale(0.28, 0.42)
            ctx.arc(0, 0, 1.0, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgba(0.55, 0.8, 1.0, 1.0 - ph)
            ctx.fill()
    elif mood == "munch":                                      # chewing: the mouth opens and shuts, cheeks puffed
        for sgn in (-1, 1):
            ctx.arc(sgn * 2.9, -4.2, 0.9, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 0.5, 0.55, 0.55)
            ctx.fill()
        hh = 0.25 + 0.7 * abs(math.sin(t * 9))
        ctx.save()
        ctx.translate(0, -3.7)
        ctx.scale(1.5, hh)
        ctx.arc(0, 0, 1.0, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.5, 0.1, 0.14)
        ctx.fill()
    elif mood == "smile":                                      # a big happy smile and rosy cheeks
        ctx.arc(0, -4.7, 2.0, 0.14 * math.pi, 0.86 * math.pi)
        ctx.stroke()
        for sgn in (-1, 1):
            ctx.arc(sgn * 3.0, -4.7, 0.8, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 0.5, 0.55, 0.6)
            ctx.fill()
    elif mood == "sleep":                                      # a tiny smile, floating Z's
        ctx.arc(0, -4.4, 1.0, 0.2 * math.pi, 0.8 * math.pi)
        ctx.stroke()
        for k in range(3):
            ph = (t * 0.5 + k / 3.0) % 1.0
            zs, zx, zy = 0.45 + 0.45 * ph, 4.0 + ph * 1.8, -9.4 - ph * 3.2
            ctx.move_to(zx, zy)
            ctx.line_to(zx + zs, zy)
            ctx.line_to(zx, zy + zs)
            ctx.line_to(zx + zs, zy + zs)
            ctx.set_source_rgba(0.85, 0.9, 1.0, math.sin(math.pi * ph))
            ctx.set_line_width(0.2)
            ctx.stroke()
    else:
        ctx.arc(0, -4.3, 1.0, 0.2 * math.pi, 0.8 * math.pi)
        ctx.stroke()
    ctx.restore()


def kraggor_head(ctx, u, spec, stands_top=None):
    """Kraggor (smash25d head design + our body) in screen space, standing at base_y (stands top / horizon).
    mode: rise | roar | calm | munch | smile."""
    mode = spec.get("mode", "rise")
    if mode == "roar":
        a = min(u, 2.7)
    elif mode == "rise":
        a = min(u, 0.8)
    elif mode == "munch":
        a = 0.8 + 0.18 * (1 + math.sin(u * 9))
    else:
        a = 3.0
    rise = se.ease_out_back(min(1.0, a / 0.8))
    roar = max(0.0, math.sin(min(math.pi, max(0.0, a - 0.8) * 1.6))) if mode == "roar" else 0.0
    base_y = stands_top if stands_top is not None else spec.get("sy", 0.42) * H
    sc = spec.get("scale", 1.0) * (H / 1080)
    if spec.get("push"):                                           # slow push-in on Kraggor
        e = min(1.0, u / 1.8)
        sc *= 1 + spec["push"] * e * e * (3 - 2 * e)
    ctx.save()
    ctx.translate(spec.get("sx", 0.62) * W, base_y)
    ctx.scale(sc, sc)
    ctx.translate(-905, 0)
    ctx.save()
    ctx.translate(905, 1.2 * 40 + (1 - rise) * 13 * 40)
    ctx.scale(40, 40)
    kraggor_body(ctx, roar)
    ctx.restore()
    if spec.get("baby"):                                           # little Kraggor: young head, soft face (S01E02 sc.5)
        kraggor_baby_head(ctx, mode, u, spec.get("cone_r", 0.0))
    else:
        SM.draw_kraggor_head(ctx, {"T": 2.4, "warn": 2.4}, a, 0)
    if mode == "smile" and not spec.get("baby"):
        kraggor_smile(ctx, a)
        w0 = spec.get("wink")
        if w0 is not None and w0 <= u < w0 + 0.6:                  # a friendly wink (one eye closes)
            kraggor_wink(ctx, spec.get("wink_eye", KR_EYES[0]))
    ctx.restore()


def draw_kraggor_small(ctx, p, camx, t, shots):
    """Little Kraggor as a prop standing IN the world at (x, z) (his real drawing, small - never a new character):
    a contact shadow, then kraggor_head(baby) anchored with its feet on the ground. modes: calm | scared | munch |
    smile | sleep. "cone": {"from": shot, "secs": s} = a strawberry cone he holds up and eats over s seconds."""
    x0, y0, w, h = kraggor_ext()
    z = p.get("z", 3.4)
    k = k_of(z)
    s = p.get("height", 3.0) * k / h
    gx, gy = pxy(p["x"], z, camx)
    mode = p.get("mode", "calm")
    face = -1 if p.get("face", 1) < 0 else 1
    ctx.save()
    ctx.translate(gx, gy + 0.08 * k)
    ctx.scale(0.75 * p.get("height", 3.0) * k, 0.4 * k)
    g = cairo.RadialGradient(0, 0, 0.0, 0, 0, 1.0)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.42)
    g.add_color_stop_rgba(0.7, 0, 0, 0, 0.25)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.0)
    ctx.arc(0, 0, 1.0, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.restore()
    cone_r = 0.0
    cn = p.get("cone")
    if cn:
        f = min(1.0, max(0.0, (t - shots[min(cn.get("from", 0), len(shots) - 1)]["t0"]) / max(0.1, cn.get("secs", 6.0))))
        cone_r = 1.1 - 0.7 * f if f < 1.0 else 0.0
    breath = 1.0 + (0.014 * math.sin(t * 1.8) if mode == "sleep" else 0.0)
    shiver = 0.05 * k * math.sin(t * 41) if mode == "scared" else 0.0
    ctx.save()
    ctx.translate(gx + shiver, gy)
    ctx.scale(face * breath, breath)
    if p.get("sway"):                                              # swaying to the music (smile mode)
        ctx.rotate(0.06 * math.sin(t * 3.4))
    kraggor_head(ctx, t, dict(mode=mode, baby=True, cone_r=cone_r, sx=-s * (x0 + w / 2) / W, scale=s * 1080.0 / H),
                 stands_top=-s * (y0 + h))
    ctx.restore()


def ice_cream_toss(ctx, u, spec, camx, actors):
    """An ice cream cone flying from the truck window to a screen point (Kraggor's mouth)."""
    a = actors[spec["from"]]
    if not 0 <= u - spec.get("at", 0.0) < spec.get("dur", 1.2):
        return
    f = (u - spec.get("at", 0.0)) / spec.get("dur", 1.2)
    k = k_of(a["z"])
    x0, y0 = pxy(a["x"] + 1.0 * a["face"], a["z"], camx)
    y0 -= 2.6 * k
    x1, y1 = spec.get("target") or (spec.get("tx", 0.6) * W, spec.get("ty", 0.3) * H)
    x = x0 + (x1 - x0) * f
    y = y0 + (y1 - y0) * f - math.sin(math.pi * f) * 0.25 * H
    s_ = (1.15 if spec.get("jumbo") else 0.5) * k
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(f * 6.0)
    se.poly(ctx, [(-s_ * 0.5, 0), (s_ * 0.5, 0), (0, s_ * 1.5)])
    ctx.set_source_rgb(0.9, 0.7, 0.35)
    ctx.fill()
    for i, col in enumerate([(1, 0.6, 0.75), (0.98, 0.95, 0.85), (0.55, 0.32, 0.2)][:3 if spec.get("jumbo") else 1]):
        ctx.arc(0, -s_ * (0.25 + 0.75 * i), s_ * 0.6, 0, 2 * math.pi)                # 3-scoop jumbo cone
        ctx.set_source_rgb(*col)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.3, 0.15, 0.1)
        ctx.set_line_width(2)
        ctx.stroke()
    ctx.restore()


def card(ctx, lines, age, dur):
    """Full-screen text card (next-episode tease)."""
    a = min(1.0, age / 0.5, max(0.0, (dur - age) / 0.5))
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgba(0.02, 0.02, 0.08, 0.85 * a)
    ctx.fill()
    for i, ln in enumerate(lines):
        se.draw_text(ctx, ln, W / 2, H * (0.38 + i * 0.14), 84 if i == 0 else 60,
                     fill=(1, 0.86, 0.12) if i == 0 else (1, 1, 1), stroke=(0.1, 0.05, 0.2), sw=6, alpha=a, max_w=W * 0.9)


def vertical_overlay(ctx, fn, *args):
    """Run a 1080x1920 overlay (race25d end card) fitted into the current frame."""
    s_ = min(W / 1080, H / 1920)
    ctx.save()
    ctx.translate((W - 1080 * s_) / 2, (H - 1920 * s_) / 2)
    ctx.scale(s_, s_)
    w0, h0 = se.W, se.H
    se.W, se.H, R.W, R.H = 1080, 1920, 1080, 1920
    try:
        fn(ctx, *args)
    finally:
        se.W, se.H, R.W, R.H = w0, h0, w0, h0
        ctx.restore()


# ------------------------------------------------------------------ cameras
def hill_focus(x):
    """Default framing height, raised by the hill under x (None = default)."""
    hh, _ = hill_h(x)
    return ground_y(1.0) - (2.3 + hh) * k_of(1.0) if hh > 0 else None


def cam_for(shot, actors, t, u):
    """(camx, zoom, focus screen y) for a shot at shot-local time u."""
    kind = shot.get("cam", "wide")
    if "look" in shot:                                             # camera on a prop / point (poster, sky, ...)
        lk = shot["look"]
        z0 = lk.get("z", 1.0)
        zm = lk.get("zoom", 2.0)
        if lk.get("fit"):                                          # frame a prop of this width (m) with a margin
            zm = 0.8 * W / (lk["fit"] * k_of(z0))
        hh, _ = hill_h(lk["x"]) if lk.get("on_hill") else (0.0, 0.0)
        return lk["x"], zm * (1 + 0.02 * u), ground_y(z0) - (lk.get("y", 0.0) + hh) * k_of(z0)
    if kind == "group":                                            # film coverage (2026-10-06): one frame for the
        ids = shot.get("group") or [k for k, a in actors.items() if not a["hidden"]]   # whole exchange, no cut per line
        grp = [actors[k] for k in ids if k in actors and not actors[k]["hidden"]] or list(actors.values())
        lo = min(a["x"] - se.VEHICLES[a["key"]]["body"][0] * 0.6 * a["small"] for a in grp)
        hi = max(a["x"] + se.VEHICLES[a["key"]]["body"][0] * 0.6 * a["small"] for a in grp)
        zm = sum(a["z"] for a in grp) / len(grp)
        mid = (lo + hi) / 2 + shot.get("dx", 0.0)
        spk = actors.get(SPEAKING["aid"])
        if spk is not None and spk in grp:
            mid += shot.get("lean", 0.22) * (spk["x"] - mid)
        fit = 0.86 * W / max(4.0, (hi - lo) * k_of(zm))
        return mid, min(shot.get("zoom", 2.2), fit), hill_focus(mid)
    on = actors.get(shot.get("on"))
    if on is None:
        vis = [a for a in actors.values() if not a["hidden"]]
        xs = [a["x"] for a in vis] or [0.0]
        mid = (min(xs) + max(xs)) / 2 + shot.get("dx", 0.0)
        return mid, shot.get("zoom", 1.0), hill_focus(mid)
    veh = se.VEHICLES[on["key"]]
    bw, bh = veh["body"]
    k = k_of(on["z"])
    fx, fy = se.FACES[on["key"]]["eyes"][0]
    face_x = on["x"] + fx * on["face"] * on["small"]
    ride = veh["wheel_r"] + 0.6 * veh["travel"] + bh / 2
    hh, _ = hill_h(on["x"])
    lift_h = on["h"] + hh
    face_y = ground_y(on["z"]) - (lift_h + (ride + fy) * on["small"] * on["sq"]) * k
    body_y = ground_y(on["z"]) - (lift_h + (ride + 0.25 * bh) * on["small"]) * k   # a bit above the body centre
    fit = W / (bw * on["small"] * k)                               # zoom at which the body fills the frame width
    tall = (ride + bh / 2 + 0.6) * on["small"] * k
    if kind == "two":
        other = actors.get(shot.get("with"))
        mid = (on["x"] + other["x"]) / 2 if other else on["x"]
        return mid, shot.get("zoom", 1.25), None
    if kind == "medium":                                           # whole vehicle, roomy
        return on["x"] + bw * 0.1 * on["face"] * on["small"], min(shot.get("zoom", 1.6), 0.55 * fit), body_y
    if kind == "close":                                            # whole vehicle, face side favoured (cinematic)
        z_c = min(shot.get("zoom", 2.8), 0.78 * fit, 0.62 * H / tall)
        return on["x"] + bw * 0.12 * on["face"] * on["small"], z_c, 0.6 * body_y + 0.4 * face_y
    if kind == "ecu":
        return face_x, shot.get("zoom", 5.0) * (1 + 0.04 * u), face_y
    if kind == "low":                                              # looking up a little, whole vehicle in frame
        z_l = min(shot.get("zoom", 1.7), 0.6 * fit, 0.5 * H / tall)
        return on["x"] + bw * 0.1 * on["face"] * on["small"], z_l, ground_y(on["z"]) - (hh + 0.5 * tall / k) * k
    if kind == "track":                                            # follow a moving car (race)
        return on["x"] + shot.get("dx", 2.0), shot.get("zoom", 1.1), hill_focus(on["x"])
    return on["x"] + shot.get("dx", 0.0), shot.get("zoom", 1.0), hill_focus(on["x"])


# ------------------------------------------------------------------ overlays
def letterbox(ctx, aspect):
    if aspect == "h":
        b = int(H * 0.085)
        ctx.rectangle(0, 0, W, b)
        ctx.rectangle(0, H - b, W, b)
        ctx.set_source_rgb(0, 0, 0)
        ctx.fill()


def sub_pages(text, maxc):
    """Text -> pages of at most 2 wrapped lines. '|' forces a page break (e.g. song phrases)."""
    pages = []
    for part in text.split("|"):
        words, line, lines = part.split(), "", []
        for w_ in words:
            if len(line) + len(w_) + 1 > maxc:
                lines.append(line)
                line = w_
            else:
                line = (line + " " + w_).strip()
        lines.append(line)
        pages += [lines[i:i + 2] for i in range(0, len(lines), 2)]
    return [pg for pg in pages if any(pg)]


def subtitle(ctx, speaker, text, aspect, age, dur=None, pages_at=None):
    """Bottom subtitle. Long lines are paged (bug until 2026-10-06: only the LAST two lines were shown, so the
    start of a long line - e.g. the first words of Tilly's song - never appeared). Page timing: pages_at (seconds
    into the line) when given, else proportional to the characters of each page."""
    if not text:
        return
    a = min(1.0, age / 0.15)
    size = 46 if aspect == "h" else 52
    y = H * (0.86 if aspect == "h" else 0.80)
    name = {"narrator": "", "announcer": "ANNOUNCER", "announcer2": "ANNOUNCER"}.get(
        speaker, speaker.replace("_", " ").upper())
    pages = sub_pages(text, 52 if aspect == "h" else 30)
    k = 0
    if len(pages) > 1:
        if pages_at:
            k = max([i for i, t0 in enumerate(pages_at[:len(pages)]) if age >= t0] + [0])
            if k > 0:
                a = min(1.0, (age - pages_at[k]) / 0.12)
        elif dur:
            cs = np.cumsum([sum(len(x) for x in pg) for pg in pages], dtype=float)
            k = int(min(len(pages) - 1, np.searchsorted(cs / cs[-1], min(0.999, age / dur), side="right")))
    lines = pages[k]
    for i, ln in enumerate(lines):
        se.draw_text(ctx, ln, W / 2, y + i * size * 1.25, size, fill=(1, 1, 1), stroke=(0, 0, 0), sw=5, alpha=a,
                     max_w=W * 0.92)
    if name:
        se.draw_text(ctx, name, W / 2, y - size * 1.05, size * 0.6, fill=SPEAKER_COLOR.get(speaker, (1, 1, 1)),
                     stroke=(0, 0, 0), sw=4, alpha=a)


def caption(ctx, text, age, dur, big=False):
    a = min(1.0, age / 0.6, max(0.0, (dur - age) / 0.9))
    if a <= 0:
        return
    if big:
        s = se.ease_out_back(min(1.0, age / 0.6))
        ctx.save()
        ctx.translate(W / 2, H * 0.45)
        ctx.scale(s, s)
        se.draw_text(ctx, text, 0, 0, 130 if W > H else 110, fill=(1, 0.86, 0.12), stroke=(0.1, 0.05, 0.2), sw=10,
                     alpha=a, max_w=W * 0.9)
        ctx.restore()
    else:
        se.draw_text(ctx, text, W / 2, H * 0.16, 62, fill=(1, 1, 1), stroke=(0, 0, 0), sw=5, alpha=a, max_w=W * 0.9)


def calendar(ctx, day, aspect):
    w, hh = (300, 340) if aspect == "h" else (360, 400)
    x, y = W - w - 60, H * 0.14
    se.rrect(ctx, x, y, w, hh, 24)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    se.rrect(ctx, x, y, w, hh * 0.28, 24)
    ctx.set_source_rgb(0.85, 0.15, 0.2)
    ctx.fill()
    se.draw_text(ctx, "DAYS TO RACE" if str(day).isdigit() else "", x + w / 2, y + hh * 0.14, 34, fill=(1, 1, 1),
                 stroke=(0.5, 0, 0), sw=2)
    se.draw_text(ctx, str(day), x + w / 2, y + hh * 0.64, 150 if str(day).isdigit() else 70, fill=(0.1, 0.1, 0.2),
                 stroke=(1, 1, 1), sw=2, max_w=w * 0.9)


def sepia(surf):
    buf = np.ndarray(shape=(H, W, 4), dtype=np.uint8, buffer=surf.get_data())
    b, g, r = buf[..., 0].astype(np.float32), buf[..., 1].astype(np.float32), buf[..., 2].astype(np.float32)
    nr = np.clip(0.393 * r + 0.769 * g + 0.189 * b, 0, 255)
    ng = np.clip(0.349 * r + 0.686 * g + 0.168 * b, 0, 255)
    nb = np.clip(0.272 * r + 0.534 * g + 0.131 * b, 0, 255)
    buf[..., 2], buf[..., 1], buf[..., 0] = nr.astype(np.uint8), ng.astype(np.uint8), nb.astype(np.uint8)


# ------------------------------------------------------------------ timeline: shots -> lines -> frames
def speaker_voice(spk):
    return VOICE_OF.get(spk, spk)


def line_style(emo):
    s = STYLE_OF.get(emo, emo)
    return s if s in announcer.STYLE else "calm"


def build(scene):
    """Shot timing from the real voice lengths. Returns (shots with t0/t1, placed lines)."""
    items = []
    for sh in scene["shots"]:
        for ln in sh.get("lines", []):
            spk, text, emo = ln[:3]
            if len(ln) > 3:                                        # sung line: its own audio file, no TTS
                continue
            items.append((text, line_style(emo), speaker_voice(spk), "studio"))
    ok = announcer.prefetch(items, note=f"story {scene.get('id', '')}")
    if not ok:
        missing = [it for it in items if not announcer.cached(*it)]
        print(f"[story] PERINGATAN: {len(missing)} kalimat gagal QA/tidak tersedia: {[m[0][:30] for m in missing]}")
    t, placed = 0.0, []
    last_end = 0.0
    for si_, sh in enumerate(scene["shots"]):
        sh["t0"] = t
        u = sh.get("lead", 0.35)
        jc = float(sh.get("jcut", scene.get("jcut", JCUT))) if si_ > 0 else 0.0
        first = True
        for ln in sh.get("lines", []):
            spk, text, emo = ln[:3]
            if len(ln) > 3:                                        # sung (e.g. Tilly singing to chase her fear away),
                a = load_cue(os.path.join(BASE, ln[3]))             # optionally cut off at a beat (the lamp dies)
                if len(ln) > 4:
                    a = a[:int(float(ln[4]) * se.SR)]
                    f = int(0.05 * se.SR)
                    a[-f:] *= np.linspace(1, 0, f)
                pre = float(ln[5]) if len(ln) > 5 else 0.0          # lead-in heard over the previous shot
                placed.append(dict(t0=t + u - pre, audio=a, spk=spk, text=text, emo=emo,      # (humming from off-screen)
                                   pages=ln[6] if len(ln) > 6 else None))          # subtitle page times in the song
                last_end = t + u - pre + len(a) / se.SR
                u += len(a) / se.SR - pre + sh.get("gap", scene.get("gap", 0.3))
                first = False
                continue
            it = (text, line_style(emo), speaker_voice(spk), "studio")
            if not announcer.cached(*it):
                continue
            a = announcer.get(*it)
            pull = 0.0
            if first and jc > 0:                                   # J-cut: voice leads the picture, never over a line
                pull = max(0.0, min(jc + u, t + u - last_end - 0.15))
            placed.append(dict(t0=t + u - pull, audio=a, spk=spk, text=text, emo=emo))
            last_end = t + u - pull + len(a) / se.SR
            u += len(a) / se.SR - pull + sh.get("gap", scene.get("gap", 0.3))
            first = False
        sh["t1"] = t + max(u + sh.get("tail", scene.get("tail", 0.4)), sh.get("hold", 0.0), 1.6 if sh.get("triple") else 0.0)
        sh["t1"] += sh.get("freeze", 0.0)
        t = sh["t1"]
    return scene["shots"], placed, t


STEMS = None              # story3d QA: dict to receive the audio stems of the next render
CUT_RULE = "soft"         # "soft" (2.5D, aired): glide to every new shot. "auto" (story3d, 2026-10-06 QA): a big
                          # change of framing = clean cut, a small reframe = slow glide (no 20 m swoops in 1 s)
JCUT = 0.0                # story3d (contract C04): the next shot's first line starts this many seconds BEFORE the
                          # picture cut (J-cut) - straight cuts on every exchange feel like tennis
ISO_CAMERA = False        # story3d: no anisotropic "low" stretch (a real 3D camera cannot match it: 283 px QA error)
SMOKE = False             # story3d preflight: draw ~3 frames/s + every shot in memory, no encode (catches crashes
                          # in new drawing code on the VM in seconds, before any cloud render - 2026-10-06)
PREPARE_ONLY = False      # story3d: stop after voices + visemes are cached (frames are rendered on Modal)
PREPARED = {}             # what the last prepare produced (lines, viseme counts, duration)

RHUBARB = os.environ.get("RHUBARB", "/root/tools/rhubarb-lip-sync/build/rhubarb/rhubarb")
VIS_CACHE = os.path.join(BASE, "work", "voice", "visemes")
VIS = {}                                                         # actor id -> current mouth shape (A..H, X)


def visemes(audio, text):
    """Rhubarb Lip Sync on one line -> [(t_start, shape)], cached by audio + text. [] when unavailable."""
    import hashlib
    import wave as _wave
    if not os.path.exists(RHUBARB):
        return []
    key = hashlib.md5(np.asarray(audio, dtype=np.float32).tobytes() + text.encode()).hexdigest()
    cache = os.path.join(VIS_CACHE, key + ".json")
    if os.path.exists(cache):
        with open(cache) as fh:
            return [tuple(x) for x in json.load(fh)]
    os.makedirs(VIS_CACHE, exist_ok=True)
    wav, txt = os.path.join(VIS_CACHE, key + ".wav"), os.path.join(VIS_CACHE, key + ".txt")
    with _wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(se.SR)
        w.writeframes((np.clip(audio, -1, 1) * 32767).astype(np.int16).tobytes())
    with open(txt, "w") as fh:
        fh.write(text)
    r = subprocess.run([RHUBARB, "-q", "-f", "json", "--extendedShapes", "GHX", "-d", txt, wav],
                       capture_output=True, text=True)
    os.remove(wav)
    os.remove(txt)
    if r.returncode:
        print(f"[lipsync] rhubarb gagal ({r.stderr.strip()[-120:]}) -> mulut volume")
        return []
    cues = [(c["start"], c["value"]) for c in json.loads(r.stdout)["mouthCues"]]
    with open(cache, "w") as fh:
        json.dump(cues, fh)
    return cues


def shape_at(cues, t):
    sh = "X"
    for st_, v in cues:
        if st_ > t:
            break
        sh = v
    return sh


def envelope(a):
    k = max(1, int(se.SR / FPS))
    n = len(a) // k
    e = np.abs(a[:n * k]).reshape(n, k).mean(axis=1)
    return np.clip(e / max(1e-6, np.percentile(e, 95)), 0, 1)


# ------------------------------------------------------------------ audio
CUE_DIR = os.path.join(BASE, "branding", "music", "cues")


def load_cue(path):
    """Any wav (ACE-Step writes stereo, 44.1/48 kHz) -> mono float at se.SR."""
    import wave as _wave
    with _wave.open(path) as w:
        ch, rate, width = w.getnchannels(), w.getframerate(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    dt_ = {2: np.int16, 4: np.int32}[width]
    x = np.frombuffer(raw, dtype=dt_).astype(np.float64) / float(np.iinfo(dt_).max)
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    if rate != se.SR:
        n = int(len(x) * se.SR / rate)
        x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)
    return x


def place_score(mus, spec, shots, place):
    """Spotting sheet (user 2026-10-05: backsound was monotonous - the same everywhere). Music only where it helps:
      {"cue": "cue_mystery_night", "from": 0, "to": 3, "vol": 0.9, "start": 0.0, "fade": 1.2}  shots from..to (incl.)
      {"sting": "cue_kraggor_motif", "shot": 4, "at": 0.3, "vol": 1.0}                       a hit on a beat
    Anything not covered stays silent (ambience + effects carry it)."""
    sr = se.SR
    for c in spec:
        name = c.get("cue") or c.get("sting")
        path = os.path.join(CUE_DIR, name + ".wav")
        if not os.path.exists(path):
            print(f"[story] WARN cue missing: {path}", flush=True)
            continue
        sig = load_cue(path)
        if "sting" in c:
            t0 = shots[c["shot"]]["t0"] + c.get("at", 0.0)
            place(mus, sig * c.get("vol", 1.0), t0, 1.0)
            continue
        t0, t1 = shots[c["from"]]["t0"], shots[min(c.get("to", c["from"]), len(shots) - 1)]["t1"]
        seg = sig[int(c.get("start", 0.0) * sr):]
        n = int((t1 - t0 + c.get("tail", 1.0)) * sr)
        if len(seg) < n:                                           # loop gently if the cue is shorter than the span
            seg = np.concatenate([seg] * (n // max(1, len(seg)) + 1))
        seg = seg[:n].copy()
        f = int(c.get("fade", 1.2) * sr)
        if f > 0 and len(seg) > 2 * f:
            seg[:f] *= np.linspace(0, 1, f)
            seg[-f:] *= np.linspace(1, 0, f)
        place(mus, seg * c.get("vol", 0.9), t0, 1.0)


def score(mood, dur, seed=1):
    """Simple emotional music bed (pads + soft arpeggio), own synthesis."""
    sr = se.SR
    n = int(dur * sr)
    tt = np.arange(n) / sr
    prog = {"sad": [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)],
            "warm": [(48, 52, 55), (55, 59, 62), (57, 60, 64), (53, 57, 60)],
            "hopeful": [(53, 57, 60), (55, 59, 62), (57, 60, 64), (60, 64, 67)],
            "tense": [(45, 48, 52), (44, 48, 51), (45, 48, 52), (46, 50, 53)],
            "epic": [(50, 53, 57), (46, 50, 53), (48, 52, 55), (45, 49, 52)],
            "playful": [(60, 64, 67), (62, 65, 69), (64, 67, 71), (65, 69, 72)]}.get(mood, [(48, 52, 55)])
    bar = {"sad": 4.0, "tense": 3.0, "epic": 2.0, "playful": 1.6}.get(mood, 3.2)
    out = np.zeros(n)
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    for b in range(int(dur / bar) + 1):
        ch = prog[b % len(prog)]
        i0, i1 = int(b * bar * sr), min(n, int((b + 1) * bar * sr))
        if i0 >= n:
            break
        seg = tt[i0:i1] - b * bar
        env = np.minimum(1, seg / 0.8) * np.minimum(1, (bar - seg) / 0.8)
        for m in ch:                                               # pad
            out[i0:i1] += 0.10 * np.sin(2 * math.pi * hz(m) * seg) * env
            out[i0:i1] += 0.04 * np.sin(2 * math.pi * hz(m) * 2.003 * seg) * env
        steps = 8 if mood in ("playful", "epic") else 4
        for s in range(steps):                                     # soft arpeggio (bell-like)
            j0 = i0 + int(s * bar / steps * sr)
            if j0 >= i1:
                break
            m = ch[s % 3] + 12
            L = min(i1 - j0, int(1.2 * sr))
            st = np.arange(L) / sr
            out[j0:j0 + L] += 0.07 * np.sin(2 * math.pi * hz(m) * st) * np.exp(-st * 3.5)
        if mood == "epic":                                          # drums
            for s in range(4):
                j0 = i0 + int(s * bar / 4 * sr)
                L = min(n - j0, int(0.3 * sr))
                if L > 0:
                    st = np.arange(L) / sr
                    out[j0:j0 + L] += 0.25 * np.sin(2 * math.pi * (70 - 30 * st) * st) * np.exp(-st * 12)
    return out


def sting():
    """Drama hit: low boom + dissonant string stab (the drama-China 'DUN!')."""
    n = int(1.6 * se.SR)
    t = np.arange(n) / se.SR
    boom = np.sin(2 * math.pi * (60 - 25 * t) * t) * np.exp(-t * 3.0)
    stab = sum(np.sign(np.sin(2 * math.pi * f * t)) * 0.5 + np.sin(2 * math.pi * f * 2 * t) * 0.3
               for f in (220.0, 233.1, 311.1, 466.2)) / 4
    stab = np.convolve(stab, np.ones(9) / 9, mode="same") * np.exp(-t * 1.6) * np.minimum(1, t / 0.01)
    return 0.9 * boom + 0.45 * stab


JINGLE = [("E5", 1), ("G5", 1), ("C6", 1), ("G5", 1), ("A5", 1), ("G5", 1), ("E5", 2),
          ("F5", 1), ("A5", 1), ("D6", 1), ("A5", 1), ("G5", 1), ("F5", 1), ("E5", 2),
          ("E5", 1), ("G5", 1), ("C6", 1), ("E6", 1), ("D6", 1), ("C6", 1), ("A5", 1), ("G5", 1),
          ("F5", 1), ("E5", 1), ("D5", 1), ("G5", 1), ("C6", 4)]          # original melody (MegaWheel), not a cover


def jingle(step=0.26):
    """Grandpa Cone's ice-cream song: a music-box melody (bell tones with a soft echo)."""
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    total = sum(d for _, d in JINGLE) * step + 1.5
    out = np.zeros(int(total * se.SR))
    t0 = 0.0
    for nm, d in JINGLE:
        f = 440.0 * 2 ** ((names[nm[0]] + 12 * (int(nm[1]) + 1) - 69) / 12)
        L = int(min(1.4, d * step + 0.8) * se.SR)
        tt = np.arange(L) / se.SR
        tone = (np.sin(2 * math.pi * f * tt) + 0.35 * np.sin(2 * math.pi * 2 * f * tt) +
                0.12 * np.sin(2 * math.pi * 3.01 * f * tt)) * np.exp(-tt * 3.2)
        i0 = int(t0 * se.SR)
        out[i0:i0 + L] += tone[:len(out) - i0]
        t0 += d * step
    echo = np.zeros_like(out)
    dly = int(0.21 * se.SR)
    echo[dly:] = out[:-dly] * 0.35
    out = out + echo
    return 0.5 * out / max(1e-9, np.max(np.abs(out)))


def soft_hit():
    """Cinematic low hit + short string swell (replaces the harsh stab)."""
    n = int(2.2 * se.SR)
    t = np.arange(n) / se.SR
    boom = np.sin(2 * math.pi * (52 - 18 * t) * t) * np.exp(-t * 2.4)
    sw = sum(np.sin(2 * math.pi * f * t) for f in (146.8, 174.6, 220.0)) / 3
    sw *= np.minimum(1, t / 0.35) * np.exp(-np.maximum(0, t - 0.35) * 2.0)
    return 0.8 * boom + 0.25 * sw


def _reverb(x, secs=1.2, mix=0.35, seed=5):
    """Cheap plate: convolve with decaying noise (FFT)."""
    n = int(secs * se.SR)
    ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-np.arange(n) / se.SR * 4.5)
    ir /= np.sqrt(np.sum(ir ** 2))
    m = len(x) + n
    wet = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:m]
    out = np.zeros(m)
    out[:len(x)] += x * (1 - mix)
    return out + wet * mix


def cine_whoosh(dur=1.3, peak=0.62, lo=180.0, hi=2600.0, reverse=False, seed=9):
    """Cinematic transition whoosh: band-pass air sweep (low -> high -> low), a soft tonal body, reverb tail."""
    n = int(dur * se.SR)
    t = np.arange(n) / se.SR
    noise = np.random.default_rng(seed).standard_normal(n)
    hop, win = 512, 2048
    out = np.zeros(n + win)
    w = np.hanning(win)
    freqs = np.fft.rfftfreq(win, 1 / se.SR)
    for i0 in range(0, n - win, hop):
        ph = (i0 + win / 2) / n
        bell = math.exp(-((ph - peak) / 0.28) ** 2)
        fc = lo * (hi / lo) ** bell                                # centre frequency rises to the peak and back
        spec = np.fft.rfft(noise[i0:i0 + win] * w)
        spec *= np.exp(-0.5 * (np.log2(np.maximum(freqs, 20) / fc) / 0.9) ** 2)
        out[i0:i0 + win] += np.fft.irfft(spec, win) * w
    air = out[:n]
    env = np.where(t / dur < peak, (t / dur / peak) ** 2, np.exp(-(t / dur - peak) / (1 - peak) * 3.2))
    body = np.sin(2 * math.pi * np.cumsum(70 + 60 * env) / se.SR) * env * 0.35
    x = air / max(1e-9, np.max(np.abs(air))) * env + body
    if reverse:
        x = x[::-1]
    x = _reverb(x, 1.3, 0.4)
    return 0.6 * x / max(1e-9, np.max(np.abs(x)))


def memory_swell(dur=2.6):
    """Into a memory: reversed whoosh + airy pad swell + one soft bell note with echo."""
    n = int(dur * se.SR)
    t = np.arange(n) / se.SR
    pad = sum(np.sin(2 * math.pi * f * t) for f in (261.6, 329.6, 392.0, 523.3)) / 4
    pad *= np.sin(np.pi * t / dur) ** 2
    bell = np.zeros(n)
    i0 = int(dur * 0.55 * se.SR)
    tt = np.arange(n - i0) / se.SR
    bell[i0:] = (np.sin(2 * math.pi * 784 * tt) + 0.3 * np.sin(2 * math.pi * 1568 * tt)) * np.exp(-tt * 2.5)
    w = cine_whoosh(dur * 0.6, reverse=True, seed=13)
    x = np.zeros(n + len(w))
    x[:n] += 0.35 * pad + 0.4 * bell
    x[:len(w)] += 0.5 * w
    x = _reverb(x, 1.8, 0.5)
    return 0.55 * x / max(1e-9, np.max(np.abs(x)))


def truck_tune():
    """The ice-cream truck's music (first phrase of Grandpa's song), replaces the old 'ting-tong' ding."""
    keep = 8
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    step = 0.22
    out = np.zeros(int((keep * step + 1.2) * se.SR))
    t0 = 0.0
    for nm, d in JINGLE[:keep]:
        f = 440.0 * 2 ** ((names[nm[0]] + 12 * (int(nm[1]) + 1) - 69) / 12)
        L = int(1.0 * se.SR)
        tt = np.arange(L) / se.SR
        tone = (np.sin(2 * math.pi * f * tt) + 0.35 * np.sin(2 * math.pi * 2 * f * tt)) * np.exp(-tt * 3.5)
        i0 = int(t0 * se.SR)
        out[i0:i0 + L] += tone[:len(out) - i0]
        t0 += d * step
    return 0.45 * out / max(1e-9, np.max(np.abs(out)))


def heartbeat(beats=4, bpm=72):
    """lub-dub. 2026-10-06 QA: the 55 Hz thump had 0 % energy in the phone band (inaudible on a phone) -> plus a
    soft 150-700 Hz knock with harmonics on every beat."""
    gap = 60.0 / bpm
    out = np.zeros(int((beats * gap + 0.4) * se.SR))
    rng = np.random.default_rng(31)
    for b in range(beats):
        for off, g in ((0.0, 1.0), (0.22, 0.7)):
            i0 = int((b * gap + off) * se.SR)
            L = int(0.18 * se.SR)
            tt = np.arange(L) / se.SR
            sub = np.sin(2 * math.pi * (55 - 20 * tt) * tt) * np.exp(-tt * 22)
            knock = fft_band(rng.normal(0, 1, L), 150, 700) * np.exp(-tt * 40)
            knock = np.tanh(knock / max(1e-9, np.abs(knock).max()) * 2.0)
            out[i0:i0 + L] += g * (sub * 0.75 + knock * 0.6)
    return out


SFX = {
    "sting": soft_hit,
    "jingle": jingle,
    "heartbeat": heartbeat,
    "whoosh": cine_whoosh,
    "memory": memory_swell,
    "ding": truck_tune,
    "laugh": lambda: SM.cheer(1.6, 0.6, seed=4),
    "cheer": lambda: SM.cheer(3.0, 1.2, seed=5),
    "gasp": lambda: SM.gasp(seed=6),
    "roar": lambda: SM.kaiju_roar(2.2),
    "stomp": lambda: SM.kaiju_step(1.4),
    "thunder": lambda: se.synth_impact(1.0, seed=3) * 0.8,
    "engine": lambda: cine_whoosh(0.9, peak=0.5, lo=120.0, hi=1400.0, seed=21),
    "splat": lambda: se.synth_splash(0.8, seed=12),
    "lamp_off": lambda: lamp_off(),
    "honk": lambda: honk(2),
    "thud_far": lambda: phone_step(0.45, seed=52) * 0.7,
    "honk_cheer": lambda: honk_cheer(),
    "box_drop": lambda: box_drop(),
    "steps_far": lambda: steps_far(),
    "stomp_near": lambda: stomp_near(),
    "thunder_roll": lambda: thunder_roll(),
    "rockslide": lambda: rockslide(),
    "munch": lambda: munch(),
    "whimper": lambda: whimper(),
    "snore": lambda: snore(),
    "drip": lambda: drip(),
    "key_glint": lambda: key_glint(),
    "breath_big": lambda: breath_big(),
}


def steps_far():
    """Four giant footsteps coming closer: each a deep thud + ground rumble, louder and brighter as it nears."""
    sr = se.SR
    out = np.zeros(int(4.0 * sr))
    for k in range(4):
        st = phone_step(0.15 + 0.25 * k, seed=40 + k)
        g = 0.35 + 0.22 * k
        i = int(k * 0.85 * sr)
        L = min(len(st), len(out) - i)
        out[i:i + L] += st[:L] * g
    return out


def stomp_near():
    """One huge step right here: thud + crack + rattling debris."""
    sr = se.SR
    st, ks = phone_step(1.0, seed=47), SM.kaiju_step(1.4) * 0.25
    st = np.pad(st, (0, max(0, len(ks) - len(st))))
    st[:len(ks)] += ks
    rng = np.random.default_rng(17)
    t = np.arange(int(0.9 * sr)) / sr
    rattle = fft_band(rng.normal(0, 1, len(t)), 700, 2600) * np.exp(-t * 7) * (np.sin(2 * math.pi * 31 * t) > 0)
    rattle = rattle / max(1e-9, np.abs(rattle).max()) * 0.1             # debris: short, band-limited (A07 headphones)
    out = np.zeros(max(len(st), len(t)))
    out[:len(st)] += st
    out[:len(t)] += rattle
    return out


def fft_band(x, lo, hi):
    """Band-limit a signal in the frequency domain (no scipy on the VM): smooth edges, no leaking hiss."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / se.SR)
    g = np.ones_like(f)
    if lo > 0:
        g *= 1.0 / (1.0 + (lo / np.maximum(f, 1e-3)) ** 4)
    if hi:
        g *= 1.0 / (1.0 + (f / hi) ** 4)
    return np.fft.irfft(X * g, len(x))


def phone_step(near, seed):
    """A giant footstep that also reads on PHONE speakers (user 2026-10-06: the steps were all < 200 Hz, so on a
    phone they vanished and only the hiss was left). Layers: sub thud + 220-900 Hz boom body (the part a phone
    plays) + asphalt crunch and debris that grow as he comes nearer. near: 0 (far) .. 1 (right here)."""
    sr = se.SR
    rng = np.random.default_rng(seed)
    n = int(1.5 * sr)
    t = np.arange(n) / sr
    sub = np.sin(2 * math.pi * (62 - 22 * t) * t) * np.exp(-t * 5.5)
    body = fft_band(rng.normal(0, 1, n), 220, 900 if near > 0.4 else 750) * np.exp(-t * (9 - 3 * near))
    body = np.tanh(body / max(1e-9, np.abs(body).max()) * 2.2)          # a little drive: harmonics phones hear
    crunch = fft_band(rng.normal(0, 1, n), 1600, 5200) * np.exp(-np.maximum(0, t - 0.01) * 26) * (t > 0.01)
    deb = fft_band(rng.normal(0, 1, n), 900, 4000) * np.exp(-t * 4) * (np.sin(2 * math.pi * 17 * t) > 0.2)
    out = (sub * 0.8 + body * 0.8 + crunch / max(1e-9, np.abs(crunch).max()) * 0.35 * near ** 1.5
           + deb / max(1e-9, np.abs(deb).max()) * 0.12 * near ** 2)
    return out / max(1e-9, np.abs(out).max())


def honk(n=2):
    """A taxi horn (nervous double honk): two detuned tones with harmonics, 400-2000 Hz, phone-audible."""
    sr = se.SR
    out = np.zeros(int((0.32 * n + 0.1) * sr))
    for k in range(n):
        L = int(0.22 * sr)
        tt = np.arange(L) / sr
        tone = sum(np.sign(np.sin(2 * math.pi * f * tt)) * 0.5 for f in (415.0, 523.0))
        env = np.clip(tt / 0.01, 0, 1) * np.clip((tt[-1] - tt) / 0.03, 0, 1)
        i = int(k * 0.32 * sr)
        out[i:i + L] += fft_band(tone * env, 300, 2200) * 0.5
    return out


def drone(dur=4.0, rise=True):
    """Tension bed (contract A01, research: horror quiet = low drone + off-screen steps, never empty). A low cluster
    with harmonics up to ~900 Hz (phone-audible), slowly swelling, a faint beating between detuned tones."""
    sr = se.SR
    n = int(max(1.0, dur) * sr)
    tt = np.arange(n) / sr
    base = 55.0                                                    # QA 2026-10-06: 8 % in the phone band -> the cluster
    tone = sum(np.sin(2 * math.pi * f * tt + p) * w                # now carries its weight at 220-1300 Hz
               for f, p, w in ((base, 0, 0.5), (base * 1.005, 1.3, 0.4), (base * 4, 0.4, 0.8), (base * 6.02, 2.1, 0.8),
                               (base * 8, 0.9, 0.9), (base * 12.03, 1.7, 0.7), (base * 16, 0.2, 0.55),
                               (base * 24.05, 2.6, 0.35)))
    air = fft_band(np.random.default_rng(23).normal(0, 1, n), 250, 1300)
    sig = tone / 3.0 + air / max(1e-9, np.abs(air).max()) * 0.3
    env = (tt / tt[-1]) ** 1.4 * 0.75 + 0.25 if rise else np.ones(n) * 0.6
    env *= np.clip(tt / 0.6, 0, 1) * np.clip((tt[-1] - tt) / 0.4, 0, 1)
    return np.tanh(sig * env * 1.4) * 0.55


def honk_cheer():
    """The town cheers - cars cheer by honking (contract A07: the noise-based crowd 'cheer' sounded like hiss on
    headphones). Seven cars with only TWO horn types honk 'beep-beep!' together (A08: many pitches = a melody)."""
    sr = se.SR
    out = np.zeros(int(2.3 * sr))
    rng = np.random.default_rng(61)
    horns = [(415, 523), (349, 440)]                               # owner 2026-10-06: only two horn types, many
    pairs = [horns[k % 2] for k in range(7)]                       # cars - not a melody ("om telolet om")
    for k, (f1, f2) in enumerate(pairs):
        f1, f2 = f1 * rng.uniform(0.985, 1.015), f2 * rng.uniform(0.985, 1.015)   # same horn, tiny car-to-car detune
        for b in range(2):
            L = int(rng.uniform(0.12, 0.2) * sr)
            tt = np.arange(L) / sr
            tone = (np.sign(np.sin(2 * math.pi * f1 * tt)) + np.sign(np.sin(2 * math.pi * f2 * tt))) * 0.5
            env = np.clip(tt / 0.008, 0, 1) * np.clip((tt[-1] - tt) / 0.02, 0, 1)
            i = int((k * 0.12 + b * 0.26 + rng.uniform(0, 0.06)) * sr)
            out[i:i + L] += fft_band(tone * env, 280, 2400) * rng.uniform(0.28, 0.42)
    return out / max(1e-9, np.abs(out).max()) * 0.8


def box_drop():
    """A wooden box falls off a shelf: a hollow wooden knock (180-900 Hz, phone-audible) + small objects rattling
    inside (short tonal clicks, not noise - A07)."""
    sr = se.SR
    n = int(1.3 * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(71)
    knock = sum(np.sin(2 * math.pi * f * t) * w for f, w in ((190, 1.0), (310, 0.7), (520, 0.45), (860, 0.25)))
    out = knock * np.exp(-t * 14) * 0.6
    for q in range(9):                                             # spoons, a bell, a book corner
        i = int((0.04 + q * 0.07 + rng.uniform(0, 0.05)) * sr)
        L = int(0.06 * sr)
        tt = np.arange(L) / sr
        f = rng.uniform(1400, 3200)
        out[i:i + L] += np.sin(2 * math.pi * f * tt) * np.exp(-tt * 70) * rng.uniform(0.08, 0.18)
    return out / max(1e-9, np.abs(out).max()) * 0.8


def lamp_off():
    """A street lamp dying: a soft electric hum that stutters, then a dull relay tunk (v6 was a raspy square buzz
    + white-noise click: unpleasant, user 2026-10-06)."""
    sr = se.SR
    t = np.arange(int(0.7 * sr)) / sr
    hum = sum(np.sin(2 * math.pi * 100 * h * t) * w for h, w in ((1, 0.5), (3, 0.7), (5, 0.6), (7, 0.45), (11, 0.3))) * 0.22
    flick = SM.box_avg((np.sin(2 * math.pi * 11 * t + 3 * np.sin(2 * math.pi * 3 * t)) > -0.1).astype(float),
                       int(0.006 * sr))
    hum = fft_band(hum * flick * np.clip(1.6 - t / 0.35, 0, 1), 200, 1600)
    k = int(0.5 * sr)
    tt = np.arange(len(t) - k) / sr
    tunk = np.zeros_like(t)
    tunk[k:] = (np.sin(2 * math.pi * 170 * tt) + 0.4 * np.sin(2 * math.pi * 620 * tt)) * np.exp(-tt * 38)
    return (hum + tunk * 0.5) * 0.6


def thunder_roll(dur=3.4):
    """Thunder made of TONES, not noise (A02 / A07, S01E02 scenes 5-7): a bright cracking cluster (230-1200 Hz, what a
    phone plays), a deep boom, and a rolling rumble of detuned partials whose slow beating makes it 'roll'."""
    sr = se.SR
    n = int(dur * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(81)
    crack = sum(np.sin(2 * math.pi * f * t + p) * w for f, p, w in
                ((230, 0.0, 1.0), (340, 1.1, 0.9), (510, 2.0, 0.8), (770, 0.4, 0.6), (1180, 1.7, 0.4), (1650, 0.9, 0.25)))
    crack = crack * np.exp(-t * 6.0) * np.clip(t / 0.004, 0, 1)
    boom = np.sin(2 * math.pi * (95 - 28 * np.minimum(t / 2.0, 1.0)) * t) * np.exp(-t * 1.6)
    boom += 0.6 * np.sin(2 * math.pi * 2 * (95 - 28 * np.minimum(t / 2.0, 1.0)) * t) * np.exp(-t * 1.8)      # 2nd harmonic
    roll = np.zeros(n)
    for f in (66, 83, 104, 131, 166, 210, 265, 330, 415):
        lfo = 0.5 + 0.5 * np.sin(2 * math.pi * rng.uniform(0.6, 1.7) * t + rng.uniform(0, 6.28))
        roll += np.sin(2 * math.pi * f * t + rng.uniform(0, 6.28)) * lfo
    roll *= np.exp(-t * 0.8) * np.clip(t / 0.2, 0, 1)
    out = crack / 3.2 + boom * 0.45 + roll / 5.0
    out *= np.clip((dur - t) / 0.6, 0, 1)
    return out / max(1e-9, np.abs(out).max()) * 0.85


def rockslide(dur=3.6):
    """Boulders crashing down a slope: many pitched knocks (a falling-pitch thud + a stony clack each), thickest in the
    first two seconds, over a low rolling rumble. Tonal impacts, never white noise (A02 / A07)."""
    sr = se.SR
    n = int(dur * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(91)
    out = np.zeros(n)
    for q in range(46):
        at = (dur * 0.62) * rng.random() ** 1.5                        # more at the start, fewer later
        i = int(at * sr)
        L = int(rng.uniform(0.18, 0.5) * sr)
        tt = np.arange(L) / sr
        f0 = rng.uniform(140, 380)
        thud = np.sin(2 * math.pi * (f0 - 70 * np.minimum(tt / 0.15, 1.0)) * tt) * np.exp(-tt * rng.uniform(9, 16))
        fc = rng.uniform(520, 1900)
        clack = (np.sin(2 * math.pi * fc * tt) + 0.5 * np.sin(2 * math.pi * fc * 1.52 * tt)) * np.exp(-tt * rng.uniform(35, 70))
        out[i:i + L] += (thud + 0.35 * clack)[:max(0, min(L, n - i))] * rng.uniform(0.25, 1.0)
    rum = sum(np.sin(2 * math.pi * f * t + rng.uniform(0, 6.28)) *
              (0.5 + 0.5 * np.sin(2 * math.pi * rng.uniform(0.8, 2.2) * t + rng.uniform(0, 6.28)))
              for f in (58, 73, 96, 125, 168, 220, 290))
    env = np.clip(t / 0.25, 0, 1) * np.exp(-np.maximum(0.0, t - 1.4) * 1.1)
    out = out / max(1e-9, np.abs(out).max()) * 0.8 + rum / 7.0 * env * 0.9
    out *= np.clip((dur - t) / 0.5, 0, 1)
    return out / max(1e-9, np.abs(out).max()) * 0.85


def munch(n=5):
    """Little Kraggor munching an ice cream: soft chomps (a hollow 200-400 Hz 'nom' + a tiny crunch tone)."""
    sr = se.SR
    out = np.zeros(int((0.3 * n + 0.4) * sr))
    for k in range(n):
        L = int(0.22 * sr)
        tt = np.arange(L) / sr
        nom = np.sin(2 * math.pi * (330 - 150 * np.minimum(tt / 0.12, 1.0)) * tt) * np.exp(-tt * 15)
        nom += 0.5 * np.sin(2 * math.pi * (660 - 300 * np.minimum(tt / 0.12, 1.0)) * tt) * np.exp(-tt * 20)
        crunch = np.sin(2 * math.pi * 1250 * tt) * np.exp(-tt * 60) * 0.25
        i = int(k * 0.3 * sr)
        out[i:i + L] += (nom + crunch) * (0.8 + 0.2 * (k % 2))
    return out / max(1e-9, np.abs(out).max()) * 0.6


def whimper(dur=1.3):
    """A small creature crying: two falling sighs of a wobbly tone with soft overtones (350-1100 Hz)."""
    sr = se.SR
    n = int(dur * sr)
    t = np.arange(n) / sr
    out = np.zeros(n)
    for start, f0, ln in ((0.0, 690.0, 0.62), (0.68, 610.0, 0.6)):
        m = (t >= start) & (t < start + ln)
        tt = t[m] - start
        f = f0 - 190 * (tt / ln) + 18 * np.sin(2 * math.pi * 7.5 * tt)
        ph = 2 * math.pi * np.cumsum(f) / sr
        env = np.sin(np.pi * tt / ln) ** 1.3
        out[m] += (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.18 * np.sin(3 * ph)) * env
    return out / max(1e-9, np.abs(out).max()) * 0.5


def snore(dur=3.0):
    """A sleeping little monster: slow breaths, a soft low tone with overtones (so phones can play it)."""
    sr = se.SR
    n = int(dur * sr)
    t = np.arange(n) / sr
    f = 118 + 6 * np.sin(2 * math.pi * 0.45 * t)
    ph = 2 * math.pi * np.cumsum(f) / sr
    tone = sum(np.sin(h * ph) * w for h, w in ((1, 1.0), (2, 0.8), (3, 0.6), (4, 0.4), (6, 0.2)))
    env = np.sin(math.pi * (t / 1.5 % 1.0)) ** 2 * np.clip(t / 0.3, 0, 1) * np.clip((dur - t) / 0.4, 0, 1)
    return tone * env / 3.0 * 0.5


def drip(n=3):
    """Water drops in a cave: a round 'plink' and its echoes, tonal."""
    sr = se.SR
    out = np.zeros(int((0.55 * n + 1.2) * sr))
    for k, f in enumerate((1180, 1480, 980)[:n]):
        i = int(k * 0.55 * sr)
        L = int(0.5 * sr)
        tt = np.arange(L) / sr
        pl = np.sin(2 * math.pi * (f + 260 * np.exp(-tt * 40)) * tt) * np.exp(-tt * 14)
        for e, g in ((0, 1.0), (0.23, 0.4), (0.46, 0.16)):
            j = i + int(e * sr)
            out[j:j + L] += pl[:max(0, min(L, len(out) - j))] * g * 0.5
    return out


def key_glint():
    """The old key catches the light: a soft two-tone chime."""
    sr = se.SR
    tt = np.arange(int(1.4 * sr)) / sr
    out = (np.sin(2 * math.pi * 1760 * tt) + 0.6 * np.sin(2 * math.pi * 2637 * tt) + 0.3 * np.sin(2 * math.pi * 3520 * tt)) * np.exp(-tt * 3.2)
    return out * np.clip(tt / 0.004, 0, 1) * 0.3


def breath_big(dur=3.4):
    """Something huge breathing right behind you: two slow bellows-like breaths (a low tone with a stack of overtones
    up to ~700 Hz, a slow growl in it). Kraggor is never noise (A07)."""
    sr = se.SR
    n = int(dur * sr)
    t = np.arange(n) / sr
    f = 58 + 5 * np.sin(2 * math.pi * 0.6 * t)
    ph = 2 * math.pi * np.cumsum(f) / sr
    tone = sum(np.sin(h * ph + h) * w for h, w in ((1, 0.9), (2, 0.8), (3, 0.9), (4, 0.8), (6, 0.7), (8, 0.55), (12, 0.35)))
    growl = 0.65 + 0.35 * np.sin(2 * math.pi * 23 * t)
    env = np.sin(math.pi * (t / (dur / 2) % 1.0)) ** 1.5 * np.clip(t / 0.4, 0, 1) * np.clip((dur - t) / 0.5, 0, 1)
    out = tone * growl * env
    return out / max(1e-9, np.abs(out).max()) * 0.8


def amb_storm(n, rng):
    """A night storm: wind in swells and a steady rain wash, ALL below ~1.2 kHz (the old noise rain was hiss on
    headphones, contract A02). Thunder is an effect on the lightning beats, not part of the bed."""
    tt = np.arange(n) / se.SR
    wind = fft_band(rng.normal(0, 1, n), 50, 380)
    wind = wind / max(1e-9, np.abs(wind).max()) * (0.55 + 0.45 * np.sin(2 * math.pi * tt / 7.3) ** 2)
    rain = fft_band(rng.normal(0, 1, n), 260, 1150)
    rain = rain / max(1e-9, np.abs(rain).max()) * (0.5 + 0.18 * np.sin(2 * math.pi * tt / 3.1))
    return wind * 0.7 + rain * 0.5


def amb_cave(n, rng):
    """Inside a cave: a deep hum (two beating tones), soft airflow and an occasional drip."""
    tt = np.arange(n) / se.SR
    hum = np.sin(2 * math.pi * 62 * tt) * 0.5 + np.sin(2 * math.pi * 63.4 * tt) * 0.45 + np.sin(2 * math.pi * 124.5 * tt) * 0.25
    air = fft_band(rng.normal(0, 1, n), 60, 420)
    out = hum * 0.7 + air / max(1e-9, np.abs(air).max()) * 0.4
    for i in rng.integers(0, max(1, n - se.SR), max(1, int(n / se.SR / 4.0))):
        pl = drip(1)
        j = min(len(pl), n - i)
        out[i:i + j] += pl[:j] * 0.5
    return out


def amb_birds(n, rng):
    """Daytime outdoors: soft birdsong (short frequency-swept chirps) over a faint breeze."""
    br = fft_band(rng.normal(0, 1, n), 40, 420)                    # breeze, no hiss (2026-10-06 QA)
    out = br / max(1e-9, np.abs(br).max()) * 0.25
    for i in rng.integers(0, max(1, n - se.SR), max(1, int(n / se.SR * 1.6))):
        f0 = rng.uniform(2800, 4800)
        for k in range(int(rng.integers(2, 5))):
            L = int(rng.uniform(0.05, 0.11) * se.SR)
            tt = np.arange(L) / se.SR
            ch = np.sin(2 * math.pi * (f0 + rng.uniform(-900, 900) * tt / tt[-1]) * tt) * np.sin(np.pi * tt / tt[-1])
            j = i + int(k * 0.13 * se.SR)
            out[j:j + L] += ch[:max(0, min(L, n - j))] * 0.5
    return out


def amb_night(n, rng):
    """Night outdoors: crickets (pulsed 4.5 kHz trills) and a low hush."""
    tt = np.arange(n) / se.SR
    trill = np.sin(2 * math.pi * 4500 * tt) * (np.sin(2 * math.pi * 28 * tt) > 0.3)
    gate = (np.sin(2 * math.pi * 0.9 * tt + rng.uniform(0, 6)) > -0.2).astype(float)
    return trill * SM.box_avg(gate, int(0.05 * se.SR)) * 0.25 + SM.box_avg(rng.normal(0, 1, n), 200) * 0.3


def amb_city_night(n, rng):
    """City at night (no crickets - user 2026-10-05): distant traffic hum, soft wind, a far car passing now and then."""
    # v6 was mostly 1-2 kHz hiss (box filters leak): exposed once the song stopped it sounded like noise
    # (user 2026-10-06). Now band-limited: rumble + a soft traffic wash, nothing above ~1 kHz.
    tt = np.arange(n) / se.SR
    hum = fft_band(rng.normal(0, 1, n), 30, 140)
    hum /= max(1e-9, np.abs(hum).max())
    wash = fft_band(rng.normal(0, 1, n), 160, 700) * (0.55 + 0.45 * np.sin(2 * math.pi * tt / 11.0) ** 2)
    wash /= max(1e-9, np.abs(wash).max())
    out = hum * 0.8 + wash * 0.25
    for i in rng.integers(0, max(1, n - 3 * se.SR), max(1, int(n / se.SR / 9))):   # a car passing far away
        L = int(3.0 * se.SR)
        env = np.sin(np.linspace(0, math.pi, L)) ** 2
        car = fft_band(rng.normal(0, 1, L), 180, 900)
        out[i:i + L] += car / max(1e-9, np.abs(car).max()) * env * 0.3
    return out


def amb_room(n, rng):
    """Garage room tone: low hum + air."""
    tt = np.arange(n) / se.SR                                      # A02: band-limited, no hiss; a fridge-like hum
    air = fft_band(rng.normal(0, 1, n), 40, 300)                   # with harmonics a phone can play
    hum = sum(np.sin(2 * math.pi * f * tt) * w for f, w in ((120, 0.5), (240, 0.3), (360, 0.15)))
    return air / max(1e-9, np.abs(air).max()) * 0.6 + hum * 0.12


def ambience_bed(scene, n):
    """Pick the bed from scene "ambience" or location / time. Level is low: felt, not heard."""
    kind = scene.get("ambience")
    loc, time_ = scene.get("location", "town"), scene.get("time", "morning")
    if kind is None:
        kind = "room" if loc == "garage" else "cave" if loc == "cave" else "crowd" if loc in ("arena", "podium") else             "night" if time_ == "night" else "birds" if loc in ("town", "country", "trackside") else None
    if kind == "night" and loc in ("town", "arena", "podium", "city"):   # crickets only where nature is (not in town)
        kind = "city_night"
    rng = np.random.default_rng(9)
    if kind == "crowd":
        x, g = SM.crowd_bed(n / se.SR + 0.1, seed=7)[:n], 0.05
    elif kind == "birds":
        x, g = amb_birds(n, rng), 0.035
    elif kind == "night":
        x, g = amb_night(n, rng), 0.018                            # countryside crickets, felt not heard
    elif kind == "city_night":
        x, g = amb_city_night(n, rng), 0.03
    elif kind == "room":
        x, g = amb_room(n, rng), 0.03
    elif kind == "storm":
        x, g = amb_storm(n, rng), 0.07                             # wind + rain wash, nothing above ~1.2 kHz
    elif kind == "cave":
        x, g = amb_cave(n, rng), 0.045
    else:
        return np.zeros(n)
    x = np.pad(x, (0, max(0, n - len(x))))[:n]
    return x / max(1e-9, np.max(np.abs(x))) * g


SFX_AT = []


def build_audio(shots, placed, total, scene):
    SFX_AT.clear()
    n = int(total * se.SR) + se.SR
    narr, sfx = np.zeros(n), np.zeros(n)

    def place(buf, sig, t, g=1.0):
        i0 = int(t * se.SR)
        if 0 <= i0 < n:
            m = min(len(sig), n - i0)
            buf[i0:i0 + m] += sig[:m] * g

    for p in placed:
        place(narr, p["audio"], p["t0"])
    for sh in shots:
        ends = [p["t0"] + len(p["audio"]) / se.SR for p in placed if sh["t0"] <= p["t0"] < sh["t1"]]
        for s in sh.get("sfx", []):
            name, dt_ = (s, 0.0) if isinstance(s, str) else (s[0], s[1])
            if isinstance(dt_, str) and dt_.startswith("end"):    # after the line, not over it (QA masking)
                dt_ = (max(ends) - sh["t0"] if ends else 0.0) + float(dt_[3:] or 0.0)
            if name == "drone":                                    # lasts to the end of its shot
                place(sfx, drone(sh["t1"] - sh["t0"] - dt_ + 0.6), sh["t0"] + dt_, 0.8)
                SFX_AT.append((name, round(sh["t0"] + dt_, 3)))
            elif name in SFX:
                place(sfx, SFX[name](), sh["t0"] + dt_, 0.8)
                SFX_AT.append((name, round(sh["t0"] + dt_, 3)))
    for sh in shots:
        pass                                                       # shock moments: picture only (user, v7)
    mus = np.zeros(n)
    if scene.get("song_stereo"):                                   # stereo song is mixed later by ffmpeg
        mix = se.peak(narr) * 0.9 + se.peak(sfx) * 0.4 if np.any(narr) or np.any(sfx) else np.zeros(n)
        return mix[:int(total * se.SR)]
    if scene.get("song"):
        song = se.read_wav(os.path.join(BASE, scene["song"]))     # theme song (ACE-Step), already mastered
        place(mus, song[:n], 0.0, 1.0)
        mix = se.peak(narr) * 0.9 + se.peak(mus) * 0.9 + se.peak(sfx) * 0.4
        mix = np.tanh(1.1 * mix) / np.tanh(1.1)
        mix = mix[:int(total * se.SR)]
        return mix / max(1e-9, np.max(np.abs(mix))) * 0.95
    if scene.get("score"):                                         # film score from the cue library (S01E02+)
        place_score(mus, scene["score"], shots, place)
    else:
        for sh in shots:                                           # Ep. 1: music per shot mood (synth pads)
            m = sh.get("music", scene.get("music", "warm"))
            seg = score(m, sh["t1"] - sh["t0"] + 1.0, seed=3)
            place(mus, seg, sh["t0"], 1.0)
    talk = SM.box_avg((np.abs(narr) > 0.01).astype(float), int(0.25 * se.SR))
    duck = 1.0 - 0.55 * np.clip(talk * 3, 0, 1)
    st_v, st_m, st_s = se.peak(narr) * 1.0, se.peak(mus) * 0.32 * duck, se.peak(sfx) * 0.7 * (0.6 + 0.4 * duck)
    st_a = np.zeros_like(st_v)
    if scene.get("ambience") != "rain" and scene.get("ambience") != "none":
        st_a = ambience_bed(scene, len(st_v)) * (0.7 + 0.3 * duck)
    mix = st_v + st_m + st_s + st_a
    if STEMS is not None:                                          # story3d QA: voice / music / effects / ambience
        STEMS.update(voice=st_v, music=st_m, sfx=st_s, amb=st_a, sr=se.SR,
                     lines=[(p["spk"], round(p["t0"], 3), round(len(p["audio"]) / se.SR, 3)) for p in placed],
                     sfx_events=SFX_AT[:])
    if scene.get("ambience") == "rain":                            # soft, calming rain (user review: was too loud)
        rng = np.random.default_rng(2)
        hiss = SM.box_avg(rng.normal(0, 1, n), 40)
        hiss = hiss / max(1e-9, np.max(np.abs(hiss))) * 0.035
        drops = np.zeros(n)
        tick = np.sin(2 * math.pi * 2600 * np.arange(int(0.012 * se.SR)) / se.SR) * np.exp(-np.linspace(0, 6, int(0.012 * se.SR)))
        for i in rng.integers(0, max(1, n - len(tick)), int(len(mix) / se.SR * 18)):
            drops[i:i + len(tick)] += tick * float(rng.uniform(0.004, 0.012))
        mix += hiss + drops[:len(mix)] if len(mix) <= n else hiss
    mix = np.tanh(1.2 * mix) / np.tanh(1.2)
    mix = mix[:int(total * se.SR)]
    return mix / max(1e-9, np.max(np.abs(mix))) * 0.95


# ------------------------------------------------------------------ render one scene
def render_scene(ep, num, aspect):
    path = os.path.join(BASE, "stories", ep, f"scene_{num:02d}.json")
    with open(path) as fh:
        scene = json.load(fh)
    scene["id"] = f"{ep}#{num}"
    SCENE.clear()
    SCENE.update(scene)
    setup_projection(aspect)
    se.load_cast()
    se.detect_font()
    se.make_theme(1, force=dict(time=scene.get("time", "morning"), weather=scene.get("weather", "clear"),
                                location=scene.get("theme_location", "city")))
    actors = {aid: make_actor(aid, a) for aid, a in scene["actors"].items()}
    shots, placed, total = build(scene)
    if scene.get("song"):                                          # intro/outro: the scene lasts as long as the song
        slen = len(se.read_wav(os.path.join(BASE, scene["song"]))) / se.SR
        if slen > total:
            shots[-1]["t1"] += slen - total
            total = slen
    envs = [(p, envelope(p["audio"])) for p in placed]
    for p in placed:
        p["vis"] = visemes(p["audio"], p["text"])
    if PREPARE_ONLY:
        PREPARED.clear()
        PREPARED.update(total=total, shots=len(shots),
                        lines=[dict(spk=p["spk"], text=p["text"], t0=round(p["t0"], 3), dur=round(len(p["audio"]) / se.SR, 3),
                                    visemes=len(p["vis"])) for p in placed])
        return None
    out_dir = os.path.join(BASE, "work", "story", ep)
    prev = os.path.join(out_dir, f"preview_{num:02d}_{aspect}")
    os.makedirs(prev, exist_ok=True)
    wav = os.path.join(out_dir, f"scene_{num:02d}_{aspect}.wav")
    se.write_wav(wav, build_audio(shots, placed, total, scene))
    if scene.get("song_stereo"):                                   # stereo theme song + centred voices / SFX
        mono = wav.replace(".wav", "_mono.wav")
        os.replace(wav, mono)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", mono, "-i", os.path.join(BASE, scene["song_stereo"]),
                        "-filter_complex",
                        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,extrastereo=m={scene.get('width', 1.4)},"
                        f"atrim=0:{total:.3f},apad=whole_dur={total:.3f}[m];"
                        "[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0[v];"
                        "[m][v]amix=inputs=2:weights=1 0.9:normalize=0,alimiter=limit=0.95[o]",
                        "-map", "[o]", "-c:a", "pcm_s16le", wav], check=True)
        os.remove(mono)
    silent = os.path.join(out_dir, f"scene_{num:02d}_{aspect}_v.mp4")
    if SMOKE:
        class _Null:
            def write(self, b):
                return len(b)

            def close(self):
                pass

        class _FF:
            stdin = _Null()

            def wait(self):
                return 0
        ff = _FF()
    else:
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", silent],
                              stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    nfr = int(total * FPS)
    loc = scene.get("location", "town")
    start = {aid: (a["x"], a["z"], a["face"]) for aid, a in actors.items()}
    marks = {int((sh["t0"] + (sh["t1"] - sh["t0"]) * 0.6) * FPS): f"shot{i + 1:02d}_{sh.get('cam', 'wide')}"
             for i, sh in enumerate(shots)}
    camx = zoom = piv = glide = None
    prev_si = -1
    for fi in range(nfr):
        if SMOKE and fi % 10 and fi not in marks:
            continue
        t = fi / FPS
        si = max(i for i, sh in enumerate(shots) if sh["t0"] <= t) if any(sh["t0"] <= t for sh in shots) else 0
        sh = shots[si]
        treal, frz = t, 0.0
        if sh.get("freeze") and t > sh["t1"] - sh["freeze"]:
            frz = (t - (sh["t1"] - sh["freeze"])) / sh["freeze"]
            t = sh["t1"] - sh["freeze"] - 1e-3
        u = t - sh["t0"]
        # actor states for this shot (positions persist from earlier shots, then moves are applied)
        for aid, a in actors.items():
            a["x"], a["z"], a["face"] = start[aid]
            a["h"], a["v"], a["sq"], a["dizzy"] = a["h0"], 0.0, 1.0, False
            a["patched"] = float(scene["actors"][aid].get("patched", 0))
            a["hidden"] = scene["actors"][aid].get("hidden", False)
        for a in actors.values():
            a["stuck"] = False
        for j in range(si + 1):
            s_ = shots[j]
            uu = min(t, s_["t1"]) - s_["t0"]
            if s_.get("roll") and j == si:                         # still driving while talking (see `off`)
                for a in actors.values():
                    if not a["hidden"]:
                        a["v"] = s_["roll"]
            for aid, mv in s_.get("moves", {}).items():
                a = actors[aid]
                if "show" in mv:
                    a["hidden"] = not mv["show"]
                if "x" in mv:
                    a["x"] = mv["x"]
                if "face" in mv:
                    a["face"] = mv["face"]
                if "h" in mv:
                    a["h"] = mv["h"]
                if "patched" in mv:
                    a["patched"] = 1.0 if mv["patched"] else 0.0
                if mv.get("squash") and j == si:                   # flattened, then BOING back (Shorts style)
                    a0 = uu - mv.get("at", 0.0)
                    if a0 >= 0:
                        a["sq"] = mv["squash"] if a0 < mv.get("hold", 99) else \
                            mv["squash"] + (1 - mv["squash"]) * se.ease_out_back(min(1.0, (a0 - mv.get("hold", 99)) / 0.4))
                if mv.get("dizzy") and j == si:
                    a["dizzy"] = True
                if "to_x" in mv:                                   # eased: slow -> fast -> slow -> stop
                    sp = mv.get("speed", 3.0)
                    d = mv["to_x"] - a["x"]
                    T = abs(d) / max(0.1, sp) * 1.25 + 0.4
                    pr = min(1.0, max(0.0, (uu - mv.get("delay", 0.0)) / T))
                    a["x"] += d * pr * pr * (3 - 2 * pr)
                    if 0 < pr < 1:
                        a["v"] = abs(d) / T * 6 * pr * (1 - pr)
                    if not mv.get("reverse"):                      # reverse: rolls back, still facing forward
                        a["face"] = 1 if d >= 0 else -1
                if mv.get("stuck") and j == si:                    # wheels spinning in the mud
                    a["h"] = a["h0"] + 0.06 * abs(math.sin(uu * 37))
                    a["v"] = 9.0
                    a["stuck"] = True
                if mv.get("hop") and j == si:
                    a["h"] = abs(math.sin(uu * 7)) * 0.5
        for a in actors.values():                                  # G04: stand on what is below (stage / ramp / road)
            if not a["hidden"]:
                a["h"] += platform_h(a["x"], a["z"])
        # emotions + talking
        EMO.clear()
        TALK.clear()
        VIS.clear()
        GAZE.clear()
        SPEAKING["aid"] = None
        for aid in actors:
            EMO[aid] = scene["actors"][aid].get("emo", "normal")
        for j in range(si + 1):
            for aid, e in shots[j].get("emote", {}).items():
                EMO[aid] = e
        cur = None
        for p, env in envs:
            if p["t0"] <= t < p["t0"] + len(env) / FPS:
                cur = p
                if p["spk"] in actors:
                    if p["emo"] not in ("talk", "whisper"):
                        EMO[p["spk"]] = p["emo"]
                    TALK[p["spk"]] = float(env[min(len(env) - 1, int((t - p["t0"]) * FPS))])
                    SPEAKING["aid"] = p["spk"]
                    VIS[p["spk"]] = shape_at(p["vis"], t - p["t0"]) if p.get("vis") else None
                    if p["spk"] in actors and TALK[p["spk"]] > 0.55:      # stressed syllable: tiny body bounce
                        actors[p["spk"]]["h"] += 0.05 * (TALK[p["spk"]] - 0.55)
        EMO_MOOD.clear()
        for aid, e in EMO.items():
            EMO_MOOD[aid] = MOOD_BASE.get(e, "normal")
        # camera
        off = sum(s_.get("roll", 0.0) * (s_["t1"] - s_["t0"]) for s_ in shots[:si]) + sh.get("roll", 0.0) * u
        for a in actors.values():                                  # camera sees the rolled positions (hill!)
            a["x"] += off
        spk_a = actors.get(SPEAKING["aid"])
        if spk_a is not None and not spk_a["hidden"]:
            vis_ = [a for a in actors.values() if not a["hidden"] and a is not spk_a]
            for a in vis_:
                GAZE[a["id"]] = 1 if (spk_a["x"] - a["x"]) * a["face"] > 0 else -1
            if vis_:
                near = min(vis_, key=lambda a: abs(a["x"] - spk_a["x"]))
                GAZE[spk_a["id"]] = 1 if (near["x"] - spk_a["x"]) * spk_a["face"] > 0 else -1
        cx, z_, focus_y = cam_for(sh, actors, t, u)
        for a in actors.values():
            a["x"] -= off
        cx -= off
        pv = (focus_y if focus_y is not None else ground_y(1.0) - 2.3 * k_of(1.0)) - sh.get("lift", 0.0) * k_of(1.0)
        if si != prev_si:                                          # new shot: glide the camera there (no rushed
            hard = camx is None or sh.get("punch") or sh.get("triple") or sh.get("cut") == "hard"   # cuts)
            if not hard and CUT_RULE == "auto" and sh.get("cut") != "glide":
                ratio = max(z_ / zoom, zoom / z_)
                pan = abs(cx - camx) * k_of(1.0) * max(zoom, z_) / W
                hard = ratio > 1.3 or pan > 0.3 or abs(pv - piv) * max(zoom, z_) > 0.3 * H
            glide = None if hard else (camx, zoom, piv, sh["t0"],      # slow, but settled before mid-shot
                                       min(sh.get("glide", scene.get("glide", 1.8)), 0.45 * (sh["t1"] - sh["t0"])))
            if hard:
                camx, zoom, piv = cx, z_, pv
            prev_si = si
        if glide:
            e = min(1.0, max(0.0, (t - glide[3]) / glide[4]))
            e = e * e * (3 - 2 * e)
            camx = glide[0] + (cx - glide[0]) * e
            zoom = glide[1] * (z_ / glide[1]) ** e                 # zoom eases geometrically (feels even)
            piv = glide[2] + (pv - glide[2]) * e
            if e >= 1.0:
                glide = None
        else:
            rate = sh.get("follow", 0.035 if sh.get("cam") == "group" else 0.12)
            camx += (cx - camx) * rate
            zoom += (z_ - zoom) * rate
            piv += (pv - piv) * rate
        zmul = 1.0
        if sh.get("punch"):                                        # crash zoom onto the face
            zmul = 1.0 + 0.45 * (1 - (1 - min(1.0, u / 0.25)) ** 3)
        if sh.get("triple"):                                       # triple-take: 3 hard cuts, closer each time
            zmul = (1.0, 1.4, 1.9)[min(2, int(u / 0.45))]
        if frz:
            zmul *= 1.0 + 0.12 * (1 - (1 - frz) ** 2)
        piv_y = piv
        # camera moves inside a shot (S01E02, user 2026-10-05: "cara pengambilan view kamera belum optimal"):
        #   "move": {"push": 0.3, "pull": 0.6, "pan": 6, "crane": 3, "dutch": 6, "handheld": 8}
        #   push = slow push-in (+30 % over the shot) · pull = starts close and opens up (reveal) · pan = metres across ·
        #   crane = metres up over the shot · dutch = degrees of tilt (unease) · handheld = px of organic shake (panic)
        mv = sh.get("move") or {}
        pan_off, tilt, hh_x, hh_y = 0.0, 0.0, 0.0, 0.0
        if mv:
            pp = min(1.0, u / max(0.01, sh["t1"] - sh["t0"]))
            pp = pp * pp * (3 - 2 * pp)                            # eased: starts and ends softly
            zmul *= (1.0 + mv.get("push", 0.0) * pp) * (1.0 + mv.get("pull", 0.0) * (1 - pp))
            pan_off = mv.get("pan", 0.0) * (pp - 0.5)
            piv_y = piv - mv.get("crane", 0.0) * k_of(1.0) * (pp - 0.5)
            tilt = math.radians(mv.get("dutch", 0.0))
            zmul *= 1.0 + 0.9 * abs(tilt)                          # a little closer: no empty corners when tilted
            a_ = mv.get("handheld", 0.0)                           # sum of slow sines = organic, not a vibration
            hh_x = a_ * (math.sin(t * 2.3) * 0.6 + math.sin(t * 5.1 + 1.0) * 0.4)
            hh_y = a_ * (math.sin(t * 1.9 + 2.0) * 0.6 + math.sin(t * 4.3) * 0.4)
        # draw. "roll": the world scrolls past (per shot) while the cars keep their place on screen and their
        # wheels turn (drawn at x + off with the camera at camx + off -> same screen spot, spinning wheels)
        camx_real = camx
        camx = camx + off + pan_off
        for a in actors.values():
            a["x"] += off
        ctx.save()
        shake = 0.0
        if "shake" in sh.get("fx", []):
            shake = 14 * math.sin(t * 60)
        ctx.translate(W / 2 + shake + hh_x, H * 0.5 + hh_y)
        if tilt:
            ctx.rotate(tilt)
        ctx.scale(zoom * zmul, zoom * zmul * (1.12 if sh.get("cam") == "low" and not ISO_CAMERA else 1.0))
        ctx.translate(-CX, -piv_y)
        def behind():
            if sh.get("kraggor_far"):
                kraggor_far(ctx, t, u, sh["kraggor_far"], camx)
            kr = sh.get("kraggor")
            if kr and not kr.get("front"):
                st_screen = H / 2 + (stands_top_world() - piv_y) * zoom
                if kr.get("stand"):                                # feet on the far ground, not floating
                    sc_ = kr.get("scale", 1.0) * (H / 1080)
                    st_screen = H / 2 + (ground_y(kr.get("gz", 7.0)) - piv_y) * zoom - (1.2 + 19.2) * 40 * sc_
                ctx.save()
                ctx.identity_matrix()
                kraggor_head(ctx, u, kr, stands_top=st_screen)
                ctx.restore()
        draw_set(ctx, loc, camx, t, after_sky=behind)
        if loc == "garage":
            draw_lamp(ctx, camx)
        draw_props_layer(ctx, loc, camx, 11, back=True)            # trees first, signs in front of them
        for prop in scene.get("props", []):
            if prop.get("from_shot", 0) > si:                      # props that appear later (e.g. what falls out of a box)
                continue
            if prop["type"] == "poster":
                draw_poster(ctx, prop, camx)
            elif prop["type"] == "sketch":
                draw_sketch(ctx, prop, camx, t)
            elif prop["type"] == "album":
                draw_album(ctx, prop, camx, t)
            elif prop["type"] == "photo_piece":
                draw_photo_piece(ctx, prop, camx, t)
            elif prop["type"] == "kraggor_small" and si <= prop.get("to_shot", 9999):
                draw_kraggor_small(ctx, prop, camx, t, shots)
            elif prop["type"] == "photo":
                draw_frame_photo(ctx, dict(prop, glow=sh.get("photo_glow")), camx, t)
            elif prop["type"] == "desk":
                draw_desk(ctx, prop, camx)
            elif prop["type"] == "podium":
                draw_podium(ctx, camx)
            elif prop["type"] == "streetlamps":
                draw_streetlamps(ctx, prop, camx, t)
        draw_hill(ctx, camx)
        for prop in scene.get("props", []):
            if prop["type"] == "mud":
                draw_mud(ctx, prop, camx, t)
            elif prop["type"] == "footprints":
                draw_footprints(ctx, prop, camx, t)
        if "finish" in scene:
            draw_finish(ctx, scene["finish"], camx)
        if scene.get("time") == "night" and scene.get("headlights", True):   # beams first: cars drawn over them
            for a in actors.values():
                if not a["hidden"]:
                    draw_beam(ctx, a, t, camx, flicker=a["id"] in sh.get("flicker", []))
        for a in sorted((a for a in actors.values() if not a["hidden"]), key=lambda a: -a["z"]):
            actor_state(a, t)
            if scene.get("contact_shadow", True):
                draw_contact(ctx, a, camx)
            draw_actor(ctx, a, t, camx)
            if a.get("stuck"):
                mud_spray(ctx, a, t, camx)
            if a["dizzy"]:
                sx_, gy_ = pxy(a["x"], a["z"], camx)
                k_ = k_of(a["z"])
                for q in range(3):
                    ang = t * 5 + q * 2.09
                    se.star(ctx, sx_ + math.cos(ang) * 1.6 * k_, gy_ - (1.6 * a["sq"] + 0.9) * k_ + math.sin(ang) * 0.35 * k_,
                            0.32 * k_, ang)
                    ctx.set_source_rgb(1, 0.85, 0.15)
                    ctx.fill_preserve()
                    ctx.set_source_rgb(0.4, 0.3, 0)
                    ctx.set_line_width(2)
                    ctx.stroke()
        for prop in scene.get("props", []):
            if prop["type"] == "desk":
                draw_desk_front(ctx, prop, camx)
        ft = sh.get("foot")
        if ft:
            uu = u - ft.get("at", 0.0)
            drop = max(0.0, 1 - uu / 0.4) ** 2 if uu < 0.4 else (0.0 if uu < ft.get("stay", 99) else
                                                                 min(1.0, (uu - ft.get("stay", 99)) / 0.6) ** 2)
            if uu >= 0:
                draw_foot(ctx, ft["x"], ft.get("z", 1.0), camx, drop)
        draw_props_layer(ctx, loc, camx, 13, back=False)
        ctx.restore()
        for a in actors.values():
            a["x"] -= off
        camx = camx_real
        if sh.get("kraggor") and sh["kraggor"].get("front"):      # close-up of Kraggor: in front of everything
            kraggor_head(ctx, u, sh["kraggor"])
        if sh.get("toss"):
            tspec = dict(sh["toss"])
            if sh.get("kraggor") and not sh["kraggor"].get("front"):
                tspec["target"] = kraggor_mouth(sh["kraggor"], H / 2 + (stands_top_world() - piv_y) * zoom)
            ice_cream_toss(ctx, u, tspec, camx, actors)
        vmax = max([a.get("v", 0.0) for a in actors.values() if not a["hidden"]] + [0.0])
        if sh.get("eyes"):
            glow_eyes(ctx, t, sh["eyes"])
        if sh.get("roll", 0) > 3 and not sh.get("speedlines"):       # wind lines while cruising
            se.draw_speed_lines(ctx, min(12.0, sh["roll"] * 1.4), t)
        if sh.get("speedlines") and vmax > 6:
            se.draw_speed_lines(ctx, min(26.0, vmax * 1.6), t)
        if sh.get("confetti"):
            se.draw_confetti(ctx, u)
        if sh.get("crown"):
            cr = actors[sh["crown"]]
            sx_, gy_ = pxy(cr["x"], cr["z"], camx)
            k_ = k_of(cr["z"])
            px_ = W / 2 + (sx_ - CX) * zoom
            py_ = H / 2 + (gy_ - 3.6 * k_ - piv_y) * zoom
            SM.crown(ctx, px_, py_ - 8 * math.sin(t * 4), 0.9 * k_ * zoom)
        if scene.get("fog") or sh.get("fog"):
            draw_fog(ctx, t, sh.get("fog", scene.get("fog")))
        se.draw_weather(ctx, t)
        if "lightning" in sh.get("fx", []) and int(u * 10) in (3, 4, 9):
            ctx.rectangle(0, 0, W, H)
            ctx.set_source_rgba(1, 1, 1, 0.55)
            ctx.fill()
        if scene.get("tint") == "sepia" or sh.get("tint") == "sepia":
            surf.flush()
            sepia(surf)
            surf.mark_dirty()
            ctx.rectangle(0, 0, W, H)                              # vignette
            g = cairo.RadialGradient(W / 2, H / 2, min(W, H) * 0.35, W / 2, H / 2, max(W, H) * 0.75)
            g.add_color_stop_rgba(0, 0, 0, 0, 0)
            g.add_color_stop_rgba(1, 0.15, 0.08, 0.02, 0.6)
            ctx.set_source(g)
            ctx.fill()
        if sh.get("card"):
            card(ctx, sh["card"], u, sh["t1"] - sh["t0"])
        if sh.get("endcard"):
            vertical_overlay(ctx, R.draw_cta, u)
        if sh.get("calendar") is not None:
            calendar(ctx, sh["calendar"], aspect)
        if sh.get("caption"):
            caption(ctx, sh["caption"], u, sh["t1"] - sh["t0"])
        if sh.get("note"):
            note(ctx, sh["note"], u, sh["t1"] - sh["t0"], low=bool(sh.get("caption")))
        if sh.get("nametag"):
            nametag(ctx, sh["nametag"], u, sh["t1"] - sh["t0"])
        if sh.get("title"):
            caption(ctx, sh["title"], u, sh["t1"] - sh["t0"], big=True)
        if frz:                                                    # freeze-frame: drain the colour, white flash
            surf.flush()
            buf = np.ndarray(shape=(H, W, 4), dtype=np.uint8, buffer=surf.get_data())
            f32 = buf[..., :3].astype(np.float32)
            grey = f32 @ np.array([0.114, 0.587, 0.299], np.float32)
            a_ = min(0.85, frz * 2.5)
            buf[..., :3] = np.clip(f32 * (1 - a_) + grey[..., None] * a_, 0, 255).astype(np.uint8)
            surf.mark_dirty()
            if frz < 0.06:
                ctx.rectangle(0, 0, W, H)
                ctx.set_source_rgba(1, 1, 1, 0.7 * (1 - frz / 0.06))
                ctx.fill()
        if scene.get("letterbox", True):
            letterbox(ctx, aspect)
        t = treal
        if cur is not None:
            subtitle(ctx, cur["spk"], cur["text"], aspect, t - cur["t0"], len(cur["audio"]) / se.SR, cur.get("pages"))
        fade = min(1.0, t / 0.4, max(0.0, (total - t) / 0.4)) if scene.get("edge_fade", True) else 1.0
        if fade < 1.0:
            ctx.rectangle(0, 0, W, H)
            ctx.set_source_rgba(0, 0, 0, 1 - fade)
            ctx.fill()
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
        if fi in marks:
            surf.write_to_png(os.path.join(prev, f"{marks[fi]}.png"))
    ff.stdin.close()
    ff.wait()
    if SMOKE:
        print(f"[story] smoke scene {num}: {nfr // 10 + len(marks)} frames drawn OK", flush=True)
        return None
    out = os.path.join(out_dir, f"scene_{num:02d}_{aspect}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                    out], check=True)                                # same loudness in every scene (headphones!)
    os.remove(silent)
    print(f"[story] scene {num} ({aspect}): {total:.1f}s, {len(shots)} shots, {len(placed)} lines -> {out}", flush=True)
    return out


XF_DUR = {"dissolve": 2.0, "fadeblack": 1.8, "fadewhite": 1.4}       # others: 1.6 s


def make_black(d, aspect, dur):
    """Silent black clip: a breath between parts (theme song -> story) so nothing overlaps."""
    setup_projection(aspect)
    out = os.path.join(d, f"black_{dur:.1f}_{aspect}.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={dur}",
                    "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-t", f"{dur}", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", out], check=True)
    return out


def make_ident(d, aspect, text, dur=3.6, logo=None):
    """'INFRASOFT presents' card: soft fade, gentle chime."""
    setup_projection(aspect)
    se.detect_font()
    out = os.path.join(d, f"ident_{aspect}.mp4")
    wav = os.path.join(d, f"ident_{aspect}.wav")
    n = int(dur * se.SR)
    t = np.arange(n) / se.SR
    chime = sum(np.sin(2 * math.pi * f * t) * np.exp(-np.maximum(0, t - dl) * 1.6) * (t >= dl)
                for f, dl in ((659.3, 0.5), (987.8, 0.75), (1318.5, 1.0))) * 0.25
    se.write_wav(wav, chime)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19",
                           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest", out],
                          stdin=subprocess.PIPE)
    big, small = (text.split("\n") + [""])[:2]
    img = cairo.ImageSurface.create_from_png(os.path.join(BASE, logo)) if logo else None
    for fi in range(int(dur * FPS)):
        tt = fi / FPS
        a = min(1.0, max(0.0, (tt - 0.3) / 0.8), max(0.0, (dur - 0.3 - tt) / 0.8))
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgb(0.03, 0.03, 0.06)
        ctx.fill()
        if img is not None:                                        # logo, gentle push-in
            sc = min(W * 0.5 / img.get_width(), H * 0.62 / img.get_height()) * (0.96 + 0.04 * min(1.0, tt / dur))
            ctx.save()
            ctx.translate(W / 2, H * 0.43)
            ctx.scale(sc, sc)
            ctx.set_source_surface(img, -img.get_width() / 2, -img.get_height() / 2)
            ctx.paint_with_alpha(a)
            ctx.restore()
        else:
            se.draw_text(ctx, big, W / 2, H * 0.47, 120 if W > H else 96, fill=(1, 1, 1), stroke=(0.2, 0.4, 0.9),
                         sw=4, alpha=a, max_w=W * 0.8)
        se.draw_text(ctx, small, W / 2, H * (0.82 if img is not None else 0.6), 54, fill=(0.75, 0.82, 1), stroke=(0, 0, 0), sw=2,
                     alpha=max(0.0, a - 0.2) / 0.8, max_w=W * 0.6)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close()
    ff.wait()
    os.remove(wav)
    return out


def dur_of(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def assemble(ep, aspect):
    d = os.path.join(BASE, "work", "story", ep)
    parts = sorted(f for f in os.listdir(d) if f.startswith("scene_") and f.endswith(f"_{aspect}.mp4"))
    edit = os.path.join(BASE, "stories", ep, "edit.json")
    if os.path.exists(edit):                                       # drama transitions (re-encode)
        with open(edit) as fh:
            ed = json.load(fh)
        tr = [x if isinstance(x, str) else x[0] for x in ed["transitions"]]
        xds = [XF_DUR.get(x, 1.6) if isinstance(x, str) else float(x[1]) for x in ed["transitions"]]
        if ed.get("order"):                                        # e.g. [1, "ident", 0, 2, ...]: cold open first
            ident = os.path.basename(make_ident(d, aspect, ed["ident"], logo=ed.get("ident_logo")))                 if "ident" in ed["order"] else None
            parts = [ident if x == "ident" else
                     os.path.basename(make_black(d, aspect, float(x.split(":")[1]) if ":" in x else 1.2))
                     if isinstance(x, str) and x.startswith("black") else
                     f"scene_{int(x):02d}_{aspect}.mp4" for x in ed["order"]]
        elif ed.get("ident"):                                      # studio ident before the theme song
            parts = [os.path.basename(make_ident(d, aspect, ed["ident"], logo=ed.get("ident_logo")))] + parts
            tr, xds = ["fade"] + tr, [0.8] + xds
        assert len(tr) == len(parts) - 1, f"edit.json: {len(tr)} transisi untuk {len(parts)} scene"
        # low-RAM build: every clip is split into body + head/tail; each transition is rendered from just two short
        # pieces (xfade), then all pieces are joined with the concat demuxer (same codec settings everywhere)
        durs = [dur_of(os.path.join(d, p)) for p in parts]
        for i, p in enumerate(parts):                              # each part must outlast its two transitions
            need = (xds[i - 1] if i else 0.0) + (xds[i] if i < len(xds) else 0.0)
            assert durs[i] > need + 0.1, f"{p}: {durs[i]:.2f}s < transisi {need:.2f}s (perpanjang klip / perpendek transisi)"
        tmp = os.path.join(d, "xf")
        os.makedirs(tmp, exist_ok=True)
        enc = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS),
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
        pieces = []

        def ff(args, out):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + args + enc + [out], check=True)
            pieces.append(out)

        for i, p in enumerate(parts):
            src = os.path.join(d, p)
            head = xds[i - 1] if i > 0 else 0.0
            tail = xds[i] if i < len(tr) else 0.0
            ff(["-ss", f"{head:.3f}", "-t", f"{durs[i] - head - tail:.3f}", "-i", src], os.path.join(tmp, f"b{i:02d}.mp4"))
            if i < len(tr):
                nxt = os.path.join(d, parts[i + 1])
                xd = xds[i]
                ff(["-ss", f"{durs[i] - xd:.3f}", "-t", f"{xd:.3f}", "-i", src, "-t", f"{xd:.3f}", "-i", nxt,
                    "-filter_complex", f"[0:v][1:v]xfade=transition={tr[i]}:duration={xd}:offset=0[v];"
                                       f"[0:a][1:a]acrossfade=d={xd}:c1=tri:c2=tri[a]", "-map", "[v]", "-map", "[a]"],
                   os.path.join(tmp, f"x{i:02d}.mp4"))
        lst = os.path.join(tmp, "list.txt")
        with open(lst, "w") as fh:
            for q in pieces:
                fh.write(f"file '{q}'\n")
        joined = os.path.join(tmp, "joined.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                        joined], check=True)
        total = dur_of(joined)
        out = os.path.join(d, f"{ep}_{aspect}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined, "-vf",
                        f"fade=t=in:d=0.6,fade=t=out:st={total - 1.2:.3f}:d=1.2", "-af",
                        f"afade=t=in:d=0.4,afade=t=out:st={total - 1.2:.3f}:d=1.2"] + enc + [out], check=True)
        shutil.rmtree(tmp)
        chap, t0 = [], 0.0                                         # YouTube chapters (scene "chapter" titles)
        for i, part in enumerate(parts):
            start = t0 - (xds[i - 1] / 2 if i else 0.0)
            t0 += durs[i] - (xds[i] if i < len(xds) else 0.0)
            if part.startswith("scene_"):
                title = json.load(open(os.path.join(BASE, "stories", ep, part[:8] + ".json"))).get("chapter")
                if title:
                    chap.append((0.0 if not chap else max(0.0, start), title))
            elif not chap:
                chap.append((0.0, None))                           # ident: merged into the next chapter
        if chap and chap[0][1] is None:
            chap = [(0.0, chap[1][1])] + chap[2:] if len(chap) > 1 else []
        with open(os.path.join(d, f"{ep}_{aspect}_chapters.txt"), "w") as fh:
            for st_, title in chap:
                fh.write(f"{int(st_ // 60)}:{int(st_ % 60):02d} {title}\n")
        print(f"[story] episode {ep} ({aspect}): {len(parts)} scenes, transisi drama -> {out} ({total / 60:.2f} menit)")
        return
    lst = os.path.join(d, f"concat_{aspect}.txt")
    with open(lst, "w") as fh:
        for p in parts:
            fh.write(f"file '{p}'\n")
    out = os.path.join(d, f"{ep}_{aspect}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out],
                   check=True)
    print(f"[story] episode {ep} ({aspect}): {len(parts)} scenes -> {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--scene", type=int, default=0)
    ap.add_argument("--aspect", default="h", choices=list(ASPECTS))
    ap.add_argument("--assemble", action="store_true")
    a = ap.parse_args()
    if a.assemble:
        assemble(a.episode, a.aspect)
    else:
        render_scene(a.episode, a.scene, a.aspect)


if __name__ == "__main__":
    main()
