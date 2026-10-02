"""Export the cast's cairo vehicle art (body + face, wheel) as PNG sprites for the Godot race prototype.
Same drawing code as every other engine -> characters stay identical. 60 px per metre.
  venv/bin/python generators/godot_race/export_sprites.py"""
import json
import math
import os
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "generators", "physics_2d"))
import sim_engine as se  # noqa: E402

PPM = 60
OUT = os.path.join(HERE, "project", "sprites")
CAST = ["icecream", "sports", "monster", "police", "taxi", "bus", "f1"]


def body_png(vk, mood="happy"):
    v = se.VEHICLES[vk]
    bw, bh = v["body"]
    w, h = int((bw + 1.6) * PPM), int((bh + 3.0) * PPM)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)
    ctx.translate(w / 2, h / 2)
    ctx.scale(PPM, -PPM)
    se.draw_body(ctx, vk, v, False, 0.0)
    se.draw_face(ctx, vk, mood, 0.0)
    surf.write_to_png(os.path.join(OUT, f"{vk}_body.png"))
    return dict(w=w, h=h, body=[bw, bh], wheel_r=v["wheel_r"], wheel_x=list(v["wheel_x"]),
                ride=v["wheel_r"] + 0.6 * v["travel"] + bh / 2, monster=vk.startswith("monster"),
                color=list(v["color"]), nick=v["nick"])


def wheel_png(vk):
    v = se.VEHICLES[vk]
    r = v["wheel_r"]
    s = int(2 * r * PPM * 1.15) + 4
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, s, s)
    ctx = cairo.Context(surf)
    ctx.translate(s / 2, s / 2)
    ctx.scale(PPM, -PPM)
    se.draw_wheel(ctx, 0.0, 0.0, 0.0, r, vk.startswith("monster"))
    surf.write_to_png(os.path.join(OUT, f"{vk}_wheel.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    se.load_cast()
    se.detect_font()
    meta = {}
    for vk in CAST:
        meta[vk] = body_png(vk)
        wheel_png(vk)
    with open(os.path.join(OUT, "cast.json"), "w") as fh:
        json.dump(dict(ppm=PPM, cars=meta), fh, indent=1)
    print("sprites:", ", ".join(CAST))
