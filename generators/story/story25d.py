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
             "excited": "happy"}                                                  # emotion -> se.draw_face mood
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


def pxy(x, z, camx):
    return (x - camx) * k_of(z) + W / 2, ground_y(z)


EMO_MOOD = {}


# ------------------------------------------------------------------ faces: drama emotions, talking mouth, blink, tears
_orig_face = se.draw_face


def story_face(ctx, vk, mood, t):
    aid = CUR["aid"] or vk
    emo = EMO.get(aid, "normal")
    talk = TALK.get(aid, 0.0)
    f = se.FACES[vk]
    r, ink = f["r"], (0.05, 0.05, 0.1)
    blink = (t * 1.0 + sum(map(ord, aid)) % 7 * 0.37) % 3.7 < 0.12 and emo not in ("happy", "laugh")
    if CUR.get("mustache"):
        _mustache(ctx, f)
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
                color=tuple(a["color"]) if a.get("color") else None, mustache=bool(a.get("mustache", False)))


def draw_actor(ctx, a, t, camx):
    """race25d.draw_car with per-actor colour / mustache / size (Grandpa Cone, Little Sprinkles share a vehicle)."""
    veh = se.VEHICLES[a["key"]]
    old = veh["color"]
    if a["color"]:
        veh["color"] = a["color"]
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
        CUR["aid"], CUR["mustache"] = None, False


def actor_state(a, t):
    yaw = 0.0 if a["face"] > 0 else math.pi
    st = (a["x"], a["z"], a["h"], yaw, 0.0, a.get("v", 0.0), 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    a["rec"] = [st, st]
    return st


# ------------------------------------------------------------------ sets / locations
def draw_set(ctx, loc, camx, t):
    se.draw_sky(ctx, camx * 0.35, 0.0, 1.0)
    if loc == "garage":
        ctx.rectangle(-W, -H, 3 * W, 3 * H)
        ctx.set_source_rgb(*se.lit((0.22, 0.2, 0.24)))
        ctx.fill()
        for i in range(-20, 21):                                   # wooden wall planks
            x = (i * 1.6 - camx) * k_of(4) + W / 2
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
            while (x - camx) * k + W / 2 < 2 * W:
                ctx.rectangle((x - camx) * k + W / 2, y - k * 0.06, 1.6 * k, k * 0.12)
                ctx.set_source_rgba(1, 1, 1, 0.85)
                ctx.fill()
                x += 4
    if loc in ("arena", "trackside", "podium"):
        SM.draw_stands(ctx, camx, t, 0.6)


def draw_props_layer(ctx, loc, camx, seed, back=True):
    if loc in ("town", "country", "trackside"):
        R.draw_props(ctx, camx, 5.4 if back else -1.0, seed, back=back)


def draw_poster(ctx, p, camx):
    x, z = p.get("x", 3.0), p.get("z", 4.5)
    k = k_of(z)
    sx, gy = pxy(x, z, camx)
    w, hh = p.get("w", 6.0) * k, p.get("h", 3.4) * k
    ctx.rectangle(sx - 0.15 * k, gy - 6.2 * k, 0.3 * k, 6.2 * k)
    ctx.set_source_rgb(*se.lit((0.35, 0.3, 0.28)))
    ctx.fill()
    se.rrect(ctx, sx - w / 2, gy - 6.2 * k - hh, w, hh, 0.2 * k)
    ctx.set_source_rgb(*se.lit((0.98, 0.94, 0.85)))
    ctx.fill_preserve()
    ctx.set_source_rgb(0.85, 0.15, 0.15)
    ctx.set_line_width(0.15 * k)
    ctx.stroke()
    lines = p["text"].split("\n")
    for i, ln in enumerate(lines):
        se.draw_text(ctx, ln, sx, gy - 6.2 * k - hh + hh * (i + 0.8) / (len(lines) + 0.4), 0.8 * k if i == 0 else 0.55 * k,
                     fill=(0.85, 0.12, 0.12) if i == 0 else (0.1, 0.1, 0.2), stroke=(1, 1, 1), sw=2, max_w=w * 0.9)


def draw_frame_photo(ctx, p, camx, t):
    """Old photo on the garage wall: Grandpa Cone (a small ice cream truck) in a wooden frame."""
    x, z = p.get("x", -2.0), 3.6
    k = k_of(z)
    sx, gy = pxy(x, z, camx)
    w, hh = 3.0 * k, 2.2 * k
    y0 = gy - 5.0 * k
    se.rrect(ctx, sx - w / 2 - 0.2 * k, y0 - 0.2 * k, w + 0.4 * k, hh + 0.4 * k, 0.1 * k)
    ctx.set_source_rgb(0.45, 0.28, 0.12)
    ctx.fill()
    ctx.rectangle(sx - w / 2, y0, w, hh)
    ctx.set_source_rgb(0.92, 0.84, 0.66)
    ctx.fill()
    ctx.save()
    ctx.translate(sx, y0 + hh * 0.85)
    ctx.scale(k * 0.35, -k * 0.35)
    veh = se.VEHICLES["icecream"]
    se.draw_body(ctx, "icecream", veh, False, t)
    CUR["aid"], CUR["mustache"] = "photo", True
    EMO["photo"], TALK["photo"] = "happy", 0.0
    story_face(ctx, "icecream", "happy", t)
    CUR["aid"], CUR["mustache"] = None, False
    ctx.restore()
    if p.get("glow"):
        ctx.rectangle(sx - w / 2, y0, w, hh)
        ctx.set_source_rgba(1, 0.9, 0.6, 0.25)
        ctx.fill()


def draw_lamp(ctx, camx):
    sx, gy = pxy(1.0, 3.0, camx)
    g = cairo.RadialGradient(sx, gy - 6 * k_of(3), 10, sx, gy - 2 * k_of(3), 9 * k_of(3))
    g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.45)
    g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0.0)
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    ctx.set_source(g)
    ctx.fill()


def draw_desk(ctx, d, camx):
    x, z = d.get("x", 1.5), 0.6
    k = k_of(z)
    sx, gy = pxy(x, z, camx)
    se.rrect(ctx, sx - 2.2 * k, gy - 1.4 * k, 4.4 * k, 1.4 * k, 0.1 * k)
    ctx.set_source_rgb(*se.lit((0.55, 0.35, 0.2)))
    ctx.fill()
    se.rrect(ctx, sx - 2.6 * k, gy - 4.6 * k, 5.2 * k, 1.1 * k, 0.15 * k)
    ctx.set_source_rgb(0.15, 0.3, 0.75)
    ctx.fill()
    se.draw_text(ctx, d.get("text", "REGISTRATION"), sx, gy - 4.05 * k, 0.6 * k, fill=(1, 1, 1), stroke=(0.1, 0.1, 0.3),
                 sw=2, max_w=4.8 * k)


def draw_podium(ctx, camx):
    for i, (x, hh) in enumerate(((-3.2, 1.2), (0.0, 1.9), (3.2, 0.8))):
        k = k_of(1.0)
        sx, gy = pxy(x, 1.0, camx)
        ctx.rectangle(sx - 1.5 * k, gy - hh * k, 3.0 * k, hh * k)
        ctx.set_source_rgb(*se.lit([(0.75, 0.75, 0.8), (1, 0.82, 0.2), (0.8, 0.5, 0.25)][i]))
        ctx.fill()


# ------------------------------------------------------------------ cameras
def cam_for(shot, actors, t, u):
    """(camx, zoom, focus screen y) for a shot at shot-local time u."""
    kind = shot.get("cam", "wide")
    if "look" in shot:                                             # camera on a prop / point (poster, sky, ...)
        lk = shot["look"]
        return lk["x"], lk.get("zoom", 2.0) * (1 + 0.03 * u), ground_y(lk.get("z", 1.0)) - lk.get("y", 0.0) * k_of(lk.get("z", 1.0))
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
    face_y = ground_y(on["z"]) - (on["h"] + (ride + fy) * on["small"]) * k
    if kind == "two":
        other = actors.get(shot.get("with"))
        mid = (on["x"] + other["x"]) / 2 if other else on["x"]
        return mid, shot.get("zoom", 1.25), None
    if kind == "medium":
        return on["x"] + bw * 0.15 * on["face"], shot.get("zoom", 1.6), ground_y(on["z"]) - 1.4 * k
    if kind == "close":
        return face_x + 0.6 * on["face"], shot.get("zoom", 2.8), face_y
    if kind == "ecu":
        return face_x, shot.get("zoom", 5.0) * (1 + 0.04 * u), face_y
    if kind == "low":
        return on["x"], shot.get("zoom", 1.7), ground_y(on["z"]) - 0.4 * k
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
    a = min(1.0, age / 0.4, max(0.0, (dur - age) / 0.4))
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
            u += len(a) / se.SR + sh.get("gap", 0.3)
        sh["t1"] = t + max(u + sh.get("tail", 0.4), sh.get("hold", 0.0))
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


SFX = {
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
    mus = np.zeros(n)
    for sh in shots:                                               # music per shot mood (crossfaded by the pads)
        m = sh.get("music", scene.get("music", "warm"))
        seg = score(m, sh["t1"] - sh["t0"] + 1.0, seed=3)
        place(mus, seg, sh["t0"], 1.0)
    talk = SM.box_avg((np.abs(narr) > 0.01).astype(float), int(0.25 * se.SR))
    duck = 1.0 - 0.55 * np.clip(talk * 3, 0, 1)
    mix = se.peak(narr) * 1.0 + se.peak(mus) * 0.32 * duck + se.peak(sfx) * 0.7 * (0.6 + 0.4 * duck)
    if scene.get("ambience") == "rain":
        rng = np.random.default_rng(2)
        rain = SM.box_avg(rng.normal(0, 1, n), 6) * 0.15
        mix += rain
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
    camx = zoom = None
    prev_si = -1
    for fi in range(nfr):
        t = fi / FPS
        si = max(i for i, sh in enumerate(shots) if sh["t0"] <= t) if any(sh["t0"] <= t for sh in shots) else 0
        sh = shots[si]
        u = t - sh["t0"]
        # actor states for this shot (positions persist from earlier shots, then moves are applied)
        for aid, a in actors.items():
            a["x"], a["z"], a["face"] = start[aid]
            a["h"], a["v"] = 0.0, 0.0
            a["hidden"] = scene["actors"][aid].get("hidden", False)
        for j in range(si + 1):
            s_ = shots[j]
            uu = min(t, s_["t1"]) - s_["t0"]
            for aid, mv in s_.get("moves", {}).items():
                a = actors[aid]
                if "show" in mv:
                    a["hidden"] = not mv["show"]
                if "x" in mv:
                    a["x"] = mv["x"]
                if "face" in mv:
                    a["face"] = mv["face"]
                if "to_x" in mv:
                    sp = mv.get("speed", 3.0)
                    d = mv["to_x"] - a["x"]
                    dist = min(abs(d), sp * max(0.0, uu - mv.get("delay", 0.0)))
                    a["x"] += math.copysign(dist, d)
                    if dist < abs(d) and uu < s_["t1"] - s_["t0"]:
                        a["v"] = sp
                    a["face"] = 1 if d >= 0 else -1
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
        cut = camx is None or si != prev_si                   # hard cut between shots, smooth moves within a shot
        prev_si = si
        if cut:
            camx, zoom = cx, z_
        else:
            camx += (cx - camx) * 0.12
            zoom += (z_ - zoom) * 0.12
        piv_y = focus_y if focus_y is not None else ground_y(1.0) - 1.2 * k_of(1.0)
        # draw
        ctx.save()
        shake = 0.0
        if "shake" in sh.get("fx", []):
            shake = 14 * math.sin(t * 60)
        ctx.translate(W / 2 + shake, H * 0.5)
        ctx.scale(zoom, zoom * (1.12 if sh.get("cam") == "low" else 1.0))
        ctx.translate(-W / 2, -piv_y)
        draw_set(ctx, loc, camx, t)
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
        for a in sorted((a for a in actors.values() if not a["hidden"]), key=lambda a: -a["z"]):
            actor_state(a, t)
            draw_actor(ctx, a, t, camx)
        draw_props_layer(ctx, loc, camx, 13, back=False)
        ctx.restore()
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
        if sh.get("calendar") is not None:
            calendar(ctx, sh["calendar"], aspect)
        if sh.get("caption"):
            caption(ctx, sh["caption"], u, sh["t1"] - sh["t0"])
        if sh.get("title"):
            caption(ctx, sh["title"], u, sh["t1"] - sh["t0"], big=True)
        if scene.get("letterbox", True):
            letterbox(ctx, aspect)
        if cur is not None:
            subtitle(ctx, cur["spk"], cur["text"], aspect, t - cur["t0"])
        fade = min(1.0, t / 0.4, max(0.0, (total - t) / 0.4))
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
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", out], check=True)
    os.remove(silent)
    print(f"[story] scene {num} ({aspect}): {total:.1f}s, {len(shots)} shots, {len(placed)} lines -> {out}", flush=True)
    return out


def assemble(ep, aspect):
    d = os.path.join(BASE, "work", "story", ep)
    parts = sorted(f for f in os.listdir(d) if f.startswith("scene_") and f.endswith(f"_{aspect}.mp4"))
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
