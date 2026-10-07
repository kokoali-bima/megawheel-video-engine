"""Custom thumbnail ARTWORK (1280x720 JPEG), drawn with the real character drawings (story25d): a huge Kraggor with glowing
eyes against a moon and mountains, little Sprinkles looking up at him, the title lettering and an episode badge.
  venv/bin/python generators/story3d/tools/make_thumbnail_art.py --out /tmp/th/art.jpg [--top "WHO IS" --big "KRAGGOR?" --badge "EP. 2"]
Runs on the VM (pycairo + story25d + ffmpeg). Never uploads anything."""
import argparse
import math
import os
import subprocess
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "generators", "story"))
import story25d as ST  # noqa: E402

se = ST.se


def lettering(ctx, text, x, y, size, fill, stroke=(0.04, 0.02, 0.1), sw=14):
    """Outlined channel lettering (Luckiest Guy), left aligned at x, baseline y."""
    ctx.save()
    ctx.select_font_face(se.FONT_FACE, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    ctx.move_to(x, y)
    ctx.text_path(text)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgb(*stroke)
    ctx.set_line_width(sw)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*fill)
    ctx.fill()
    ctx.restore()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--top", default="WHO IS")
    ap.add_argument("--big", default="KRAGGOR?")
    ap.add_argument("--badge", default="EP. 2")
    a = ap.parse_args()
    ST.setup_projection("h")
    se.load_cast()
    se.detect_font()
    se.make_theme(1, force=dict(time="night", weather="clear", location="city"))
    W, H = ST.W, ST.H
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    # ---- night sky: deep violet to a warm glow at the horizon
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.05, 0.04, 0.16)
    g.add_color_stop_rgb(0.55, 0.28, 0.12, 0.40)
    g.add_color_stop_rgb(0.8, 0.85, 0.38, 0.28)
    g.add_color_stop_rgb(1, 0.25, 0.1, 0.18)
    ctx.set_source(g)
    ctx.paint()
    for i in range(110):                                                  # stars
        x, y = (i * 977 % W), (i * 541 % int(H * 0.55))
        ctx.arc(x, y, 1.4 + (i % 3) * 0.8, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 0.9, 0.35 + 0.5 * ((i * 7) % 10) / 10)
        ctx.fill()
    mg = cairo.RadialGradient(W * 0.69, H * 0.30, 40, W * 0.69, H * 0.30, 460)      # the moon and its glow
    mg.add_color_stop_rgba(0, 1, 0.97, 0.8, 0.95)
    mg.add_color_stop_rgba(0.22, 1, 0.9, 0.7, 0.55)
    mg.add_color_stop_rgba(1, 1, 0.8, 0.6, 0.0)
    ctx.set_source(mg)
    ctx.paint()
    ctx.arc(W * 0.69, H * 0.30, 150, 0, 2 * math.pi)
    ctx.set_source_rgb(1, 0.97, 0.82)
    ctx.fill()
    for col, base, amp in (((0.18, 0.09, 0.30), 0.74, 150), ((0.10, 0.05, 0.20), 0.82, 110)):    # mountain ridges
        ctx.move_to(0, H)
        for x in range(0, W + 40, 40):
            ctx.line_to(x, H * base - amp * abs(math.sin(x * 0.0047 + base * 9)) - 0.35 * amp * math.sin(x * 0.019))
        ctx.line_to(W, H)
        ctx.close_path()
        ctx.set_source_rgb(*col)
        ctx.fill()
    # ---- Kraggor: the real drawing, huge, his head in front of the moon
    ST.kraggor_head(ctx, 3.0, dict(mode="calm", sx=0.66, scale=1.55), stands_top=H * 0.30)
    eg = cairo.RadialGradient(W * 0.66, H * 0.40, 10, W * 0.66, H * 0.40, 380)
    eg.add_color_stop_rgba(0, 1, 0.85, 0.2, 0.0)
    eg.add_color_stop_rgba(0.35, 1, 0.8, 0.1, 0.10)
    eg.add_color_stop_rgba(1, 1, 0.8, 0.1, 0.0)
    ctx.set_source(eg)
    ctx.paint()
    # ---- ground + Sprinkles looking up at him
    ctx.rectangle(0, H * 0.86, W, H * 0.14)
    ctx.set_source_rgb(0.08, 0.04, 0.12)
    ctx.fill()
    act = ST.make_actor("sprinkles", {"vk": "icecream", "x": 0.0, "z": 0.2, "face": 1, "scale": 0.9})
    ST.EMO["sprinkles"] = "surprised"
    ST.EMO_MOOD["sprinkles"] = ST.MOOD_BASE.get("surprised", "normal")
    ST.actor_state(act, 0.0)
    ctx.save()
    ctx.translate(W * 0.22 - ST.CX, H * 0.90 - ST.ground_y(0.2))        # the truck's ground point -> (22 %, 90 %)
    ST.draw_contact(ctx, act, 0.0)
    ST.draw_actor(ctx, act, 0.0, 0.0)
    ctx.restore()
    # ---- vignette + lettering + badge
    vg = cairo.RadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.0)
    vg.add_color_stop_rgba(0, 0, 0, 0, 0)
    vg.add_color_stop_rgba(1, 0, 0, 0, 0.55)
    ctx.set_source(vg)
    ctx.paint()
    lettering(ctx, a.top, 70, 760, 190, (1.0, 0.82, 0.12), sw=18)
    lettering(ctx, a.big, 60, 960, 330, (1, 1, 1), sw=26)
    ctx.rectangle(W - 430, 40, 380, 150)
    ctx.set_source_rgb(1.0, 0.42, 0.0)
    ctx.fill()
    lettering(ctx, a.badge, W - 405, 165, 120, (1, 1, 1), sw=10)
    png = a.out + ".png"
    surf.write_to_png(png)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", png, "-vf", "scale=1280:720", "-q:v", "2", a.out], check=True)
    os.remove(png)
    print(f"[thumbnail-art] {a.out} ({os.path.getsize(a.out) // 1024} KB)")


if __name__ == "__main__":
    main()
