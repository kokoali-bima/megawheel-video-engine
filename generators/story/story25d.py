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
            "surprised": "excited", "tease": "excited", "whisper": "calm"}   # face emotion -> voice style
MOOD_BASE = {"happy": "happy", "laugh": "happy", "proud": "happy", "scared": "scared", "surprised": "whoa",
             "excited": "happy", "dizzy": "dizzy"}                                                  # emotion -> se.draw_face mood
SPEAKER_COLOR = {"sprinkles": (1, 0.6, 0.8), "little_sprinkles": (1, 0.7, 0.85), "grandpa_cone": (0.95, 0.85, 0.6),
                 "buster": (1, 0.85, 0.2), "zippy": (1, 0.4, 0.35), "rocky": (0.45, 0.7, 1), "siren": (0.85, 0.9, 1),
                 "narrator": (0.9, 0.9, 0.9), "announcer": (1, 0.86, 0.12), "announcer2": (1, 0.86, 0.12)}

W, H = ASPECTS["h"]
EMO, TALK = {}, {}                                   # per ACTOR id (several actors can share a vehicle key)
CUR = {"aid": None, "mustache": False}               # actor being drawn right now (read by story_face)
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


def draw_frame_photo(ctx, p, camx, t):
    """Old photo on the garage wall: Grandpa Cone (cream truck, glasses, beard) centred in a wooden frame."""
    x, z = p.get("x", -2.0), 3.6
    k = k_of(z)
    sx, gy = pxy(x, z, camx)
    w, hh = 3.2 * k, 2.4 * k
    y0 = gy - 5.0 * k
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


def note(ctx, text, age, dur):
    """Short description box at the top (explains what happens: bumps, crashes, numbers...)."""
    a = min(1.0, age / 0.5, max(0.0, (dur - age) / 0.5))
    if a <= 0:
        return
    bw, bh = W * 0.86, H * 0.085
    se.rrect(ctx, (W - bw) / 2, H * 0.035, bw, bh, bh * 0.3)
    ctx.set_source_rgba(0.05, 0.05, 0.12, 0.62 * a)
    ctx.fill()
    se.draw_text(ctx, text, W / 2, H * 0.035 + bh * 0.52, 38 if W > H else 34, fill=(1, 0.95, 0.75),
                 stroke=(0, 0, 0), sw=3, alpha=a, max_w=bw * 0.94)


def draw_lamp(ctx, camx):
    sx, gy = pxy(1.0, 3.0, camx)
    g = cairo.RadialGradient(sx, gy - 6 * k_of(3), 10, sx, gy - 2 * k_of(3), 9 * k_of(3))
    g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.45)
    g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0.0)
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
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


KR_EYES = [(-1.9, -8.6), (1.9, -8.6)]                    # eye centres in kraggor_smile units (head-local)


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
    SM.draw_kraggor_head(ctx, {"T": 2.4, "warn": 2.4}, a, 0)
    if mode == "smile":
        kraggor_smile(ctx, a)
        w0 = spec.get("wink")
        if w0 is not None and w0 <= u < w0 + 0.6:                  # a friendly wink (one eye closes)
            kraggor_wink(ctx, spec.get("wink_eye", KR_EYES[0]))
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
    on = actors.get(shot.get("on"))
    if on is None:
        vis = [a for a in actors.values() if not a["hidden"]]
        xs = [a["x"] for a in vis] or [0.0]
        mid = (min(xs) + max(xs)) / 2
        return mid + shot.get("dx", 0.0), shot.get("zoom", 1.0), None
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
    if kind == "two":
        other = actors.get(shot.get("with"))
        mid = (on["x"] + other["x"]) / 2 if other else on["x"]
        return mid, shot.get("zoom", 1.25), None
    if kind == "medium":                                           # whole vehicle, roomy
        return on["x"] + bw * 0.1 * on["face"] * on["small"], min(shot.get("zoom", 1.6), 0.55 * fit), body_y
    if kind == "close":                                            # whole vehicle, face side favoured (cinematic)
        tall = (ride + bh / 2 + 0.6) * on["small"] * k             # tall vehicles (monster truck) fit by height
        z_c = min(shot.get("zoom", 2.8), 0.78 * fit, 0.62 * H / tall)
        return on["x"] + bw * 0.12 * on["face"] * on["small"], z_c, 0.6 * body_y + 0.4 * face_y
    if kind == "ecu":
        return face_x, shot.get("zoom", 5.0) * (1 + 0.04 * u), face_y
    if kind == "low":
        return on["x"], shot.get("zoom", 1.7), ground_y(on["z"]) - (0.4 + hh) * k
    if kind == "track":                                            # follow a moving car (race)
        return on["x"] + shot.get("dx", 2.0), shot.get("zoom", 1.1), None
    return on["x"] + shot.get("dx", 0.0), shot.get("zoom", 1.0), None


# ------------------------------------------------------------------ overlays
def letterbox(ctx, aspect):
    if aspect == "h":
        b = int(H * 0.085)
        ctx.rectangle(0, 0, W, b)
        ctx.rectangle(0, H - b, W, b)
        ctx.set_source_rgb(0, 0, 0)
        ctx.fill()


def subtitle(ctx, speaker, text, aspect, age):
    if not text:
        return
    a = min(1.0, age / 0.15)
    size = 46 if aspect == "h" else 52
    y = H * (0.86 if aspect == "h" else 0.80)
    name = {"narrator": "", "announcer": "ANNOUNCER", "announcer2": "ANNOUNCER"}.get(
        speaker, speaker.replace("_", " ").upper())
    words, line, lines = text.split(), "", []
    maxc = 52 if aspect == "h" else 30
    for w_ in words:
        if len(line) + len(w_) + 1 > maxc:
            lines.append(line)
            line = w_
        else:
            line = (line + " " + w_).strip()
    lines.append(line)
    for i, ln in enumerate(lines[-2:]):
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
        for spk, text, emo in sh.get("lines", []):
            items.append((text, line_style(emo), speaker_voice(spk), "studio"))
    ok = announcer.prefetch(items, note=f"story {scene.get('id', '')}")
    if not ok:
        missing = [it for it in items if not announcer.cached(*it)]
        print(f"[story] PERINGATAN: {len(missing)} kalimat gagal QA/tidak tersedia: {[m[0][:30] for m in missing]}")
    t, placed = 0.0, []
    for sh in scene["shots"]:
        sh["t0"] = t
        u = sh.get("lead", 0.35)
        for spk, text, emo in sh.get("lines", []):
            it = (text, line_style(emo), speaker_voice(spk), "studio")
            if not announcer.cached(*it):
                continue
            a = announcer.get(*it)
            placed.append(dict(t0=t + u, audio=a, spk=spk, text=text, emo=emo))
            u += len(a) / se.SR + sh.get("gap", scene.get("gap", 0.3))
        sh["t1"] = t + max(u + sh.get("tail", scene.get("tail", 0.4)), sh.get("hold", 0.0), 1.6 if sh.get("triple") else 0.0)
        sh["t1"] += sh.get("freeze", 0.0)
        t = sh["t1"]
    return scene["shots"], placed, t


def envelope(a):
    k = max(1, int(se.SR / FPS))
    n = len(a) // k
    e = np.abs(a[:n * k]).reshape(n, k).mean(axis=1)
    return np.clip(e / max(1e-6, np.percentile(e, 95)), 0, 1)


# ------------------------------------------------------------------ audio
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


def heartbeat(beats=4, bpm=72):
    gap = 60.0 / bpm
    out = np.zeros(int((beats * gap + 0.4) * se.SR))
    for b in range(beats):
        for off, g in ((0.0, 1.0), (0.22, 0.7)):
            i0 = int((b * gap + off) * se.SR)
            L = int(0.18 * se.SR)
            tt = np.arange(L) / se.SR
            out[i0:i0 + L] += g * np.sin(2 * math.pi * (55 - 20 * tt) * tt) * np.exp(-tt * 22)
    return out


SFX = {
    "sting": soft_hit,
    "jingle": jingle,
    "heartbeat": heartbeat,
    "whoosh": lambda: se.synth_whoosh(),
    "ding": lambda: np.concatenate([se.tone(1320, 0.18, "sine", decay=0.12), se.tone(1046, 0.3, "sine", decay=0.18)]),
    "laugh": lambda: SM.cheer(1.6, 0.6, seed=4),
    "cheer": lambda: SM.cheer(3.0, 1.2, seed=5),
    "gasp": lambda: SM.gasp(seed=6),
    "roar": lambda: SM.kaiju_roar(2.2),
    "stomp": lambda: SM.kaiju_step(1.4),
    "thunder": lambda: se.synth_impact(1.0, seed=3) * 0.8,
    "engine": lambda: se.synth_whoosh(),
    "splat": lambda: se.synth_splash(0.8, seed=12),
}


def build_audio(shots, placed, total, scene):
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
        for s in sh.get("sfx", []):
            name, dt_ = (s, 0.0) if isinstance(s, str) else (s[0], s[1])
            if name in SFX:
                place(sfx, SFX[name](), sh["t0"] + dt_, 0.8)
    for sh in shots:
        if sh.get("punch"):
            place(sfx, se.synth_whoosh(), sh["t0"], 0.55)
        if sh.get("triple"):                                       # whoosh per cut, one soft hit
            for k in range(3):
                place(sfx, se.synth_whoosh(), sh["t0"] + 0.45 * k, 0.35 + 0.1 * k)
            place(sfx, soft_hit(), sh["t0"] + 0.9, 0.6)
        if sh.get("freeze"):
            place(sfx, soft_hit(), sh["t1"] - sh["freeze"], 0.7)
    mus = np.zeros(n)
    if scene.get("song"):
        song = se.read_wav(os.path.join(BASE, scene["song"]))     # theme song (ACE-Step), already mastered
        place(mus, song[:n], 0.0, 1.0)
        mix = se.peak(narr) * 0.9 + se.peak(mus) * 0.9 + se.peak(sfx) * 0.4
        mix = np.tanh(1.1 * mix) / np.tanh(1.1)
        mix = mix[:int(total * se.SR)]
        return mix / max(1e-9, np.max(np.abs(mix))) * 0.95
    for sh in shots:                                               # music per shot mood (crossfaded by the pads)
        m = sh.get("music", scene.get("music", "warm"))
        seg = score(m, sh["t1"] - sh["t0"] + 1.0, seed=3)
        place(mus, seg, sh["t0"], 1.0)
    talk = SM.box_avg((np.abs(narr) > 0.01).astype(float), int(0.25 * se.SR))
    duck = 1.0 - 0.55 * np.clip(talk * 3, 0, 1)
    mix = se.peak(narr) * 1.0 + se.peak(mus) * 0.32 * duck + se.peak(sfx) * 0.7 * (0.6 + 0.4 * duck)
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
    out_dir = os.path.join(BASE, "work", "story", ep)
    prev = os.path.join(out_dir, f"preview_{num:02d}_{aspect}")
    os.makedirs(prev, exist_ok=True)
    wav = os.path.join(out_dir, f"scene_{num:02d}_{aspect}.wav")
    se.write_wav(wav, build_audio(shots, placed, total, scene))
    silent = os.path.join(out_dir, f"scene_{num:02d}_{aspect}_v.mp4")
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
            if s_.get("roll"):                                     # still driving while talking: wheels turn,
                for a in actors.values():                          # the world scrolls past, the camera follows
                    if not a["hidden"] and a["id"] not in s_.get("parked", []):
                        a["x"] += s_["roll"] * uu
                        if j == si:
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
        # emotions + talking
        EMO.clear()
        TALK.clear()
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
        EMO_MOOD.clear()
        for aid, e in EMO.items():
            EMO_MOOD[aid] = MOOD_BASE.get(e, "normal")
        # camera
        cx, z_, focus_y = cam_for(sh, actors, t, u)
        pv = (focus_y if focus_y is not None else ground_y(1.0) - 2.3 * k_of(1.0)) - sh.get("lift", 0.0) * k_of(1.0)
        if si != prev_si:                                          # new shot: glide the camera there (no rushed
            hard = camx is None or sh.get("punch") or sh.get("triple") or sh.get("cut") == "hard"   # cuts)
            glide = None if hard else (camx, zoom, piv, sh["t0"], sh.get("glide", scene.get("glide", 1.2)))
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
            camx += (cx - camx) * 0.12
            zoom += (z_ - zoom) * 0.12
            piv += (pv - piv) * 0.12
        zmul = 1.0
        if sh.get("punch"):                                        # crash zoom onto the face
            zmul = 1.0 + 0.45 * (1 - (1 - min(1.0, u / 0.25)) ** 3)
        if sh.get("triple"):                                       # triple-take: 3 hard cuts, closer each time
            zmul = (1.0, 1.4, 1.9)[min(2, int(u / 0.45))]
        if frz:
            zmul *= 1.0 + 0.12 * (1 - (1 - frz) ** 2)
        piv_y = piv
        # draw
        ctx.save()
        shake = 0.0
        if "shake" in sh.get("fx", []):
            shake = 14 * math.sin(t * 60)
        ctx.translate(W / 2 + shake, H * 0.5)
        ctx.scale(zoom * zmul, zoom * zmul * (1.12 if sh.get("cam") == "low" else 1.0))
        ctx.translate(-CX, -piv_y)
        def behind():
            kr = sh.get("kraggor")
            if kr and not kr.get("front"):
                st_screen = H / 2 + (stands_top_world() - piv_y) * zoom
                if kr.get("stand"):                                # feet on the far ground, not floating
                    sc_ = kr.get("scale", 1.0) * (H / 1080)
                    st_screen = H / 2 + (ground_y(kr.get("gz", 30.0)) - piv_y) * zoom - (1.2 + 19.2) * 40 * sc_
                ctx.save()
                ctx.identity_matrix()
                kraggor_head(ctx, u, kr, stands_top=st_screen)
                ctx.restore()
        draw_set(ctx, loc, camx, t, after_sky=behind)
        if loc == "garage":
            draw_lamp(ctx, camx)
        for prop in scene.get("props", []):
            if prop["type"] == "poster":
                draw_poster(ctx, prop, camx)
            elif prop["type"] == "photo":
                draw_frame_photo(ctx, dict(prop, glow=sh.get("photo_glow")), camx, t)
            elif prop["type"] == "desk":
                draw_desk(ctx, prop, camx)
            elif prop["type"] == "podium":
                draw_podium(ctx, camx)
        draw_props_layer(ctx, loc, camx, 11, back=True)
        draw_hill(ctx, camx)
        for prop in scene.get("props", []):
            if prop["type"] == "mud":
                draw_mud(ctx, prop, camx, t)
        if "finish" in scene:
            draw_finish(ctx, scene["finish"], camx)
        for a in sorted((a for a in actors.values() if not a["hidden"]), key=lambda a: -a["z"]):
            actor_state(a, t)
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
            note(ctx, sh["note"], u, sh["t1"] - sh["t0"])
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
            subtitle(ctx, cur["spk"], cur["text"], aspect, t - cur["t0"])
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
    out = os.path.join(out_dir, f"scene_{num:02d}_{aspect}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                    out], check=True)                                # same loudness in every scene (headphones!)
    os.remove(silent)
    print(f"[story] scene {num} ({aspect}): {total:.1f}s, {len(shots)} shots, {len(placed)} lines -> {out}", flush=True)
    return out


XF_DUR = {"dissolve": 1.4, "fadeblack": 1.2, "fadewhite": 0.9}


def make_ident(d, aspect, text, dur=3.6):
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
    for fi in range(int(dur * FPS)):
        tt = fi / FPS
        a = min(1.0, max(0.0, (tt - 0.3) / 0.8), max(0.0, (dur - 0.3 - tt) / 0.8))
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgb(0.03, 0.03, 0.06)
        ctx.fill()
        se.draw_text(ctx, big, W / 2, H * 0.47, 120 if W > H else 96, fill=(1, 1, 1), stroke=(0.2, 0.4, 0.9), sw=4,
                     alpha=a, max_w=W * 0.8)
        se.draw_text(ctx, small, W / 2, H * 0.6, 54, fill=(0.75, 0.82, 1), stroke=(0, 0, 0), sw=2,
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
        xds = [XF_DUR.get(x, 1.0) if isinstance(x, str) else float(x[1]) for x in ed["transitions"]]
        if ed.get("ident"):                                        # studio ident before the theme song
            parts = [os.path.basename(make_ident(d, aspect, ed["ident"]))] + parts
            tr, xds = ["fade"] + tr, [0.8] + xds
        assert len(tr) == len(parts) - 1, f"edit.json: {len(tr)} transisi untuk {len(parts)} scene"
        # low-RAM build: every clip is split into body + head/tail; each transition is rendered from just two short
        # pieces (xfade), then all pieces are joined with the concat demuxer (same codec settings everywhere)
        durs = [dur_of(os.path.join(d, p)) for p in parts]
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
