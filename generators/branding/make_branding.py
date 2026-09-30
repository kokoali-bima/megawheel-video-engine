#!/usr/bin/env python3
"""YouTube channel branding for MegaWheel Kids, drawn with the engine's own cast art.

Usage: cd /root/video-engine && ./venv/bin/python generators/branding/make_branding.py
Writes branding/profile_*.png (800x800), branding/banner.png (2560x1440) and *_check.png
previews (circle crop / banner safe areas) to verify the layout.
"""
import math
import os
import sys

import cairo

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "physics_2d"))
import sim_engine as se  # noqa: E402

OUT = "/root/video-engine/branding"
NAVY = (0.07, 0.07, 0.2)
YELLOW = (1, 0.86, 0.12)


def vehicle(ctx, vk, x, ground_y, s, mood="happy", wheel_angle=0.3):
    """Draw a cast vehicle standing on screen-space ground line ground_y, centred at x, s px/m."""
    v = se.VEHICLES[vk]
    bw, bh = v["body"]
    r, tr = v["wheel_r"], v["travel"]
    ctx.save()
    ctx.translate(x, ground_y)
    ctx.scale(s, -s)
    ctx.save()
    ctx.scale(bw * 0.55, 0.16)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(0, 0, 0, 0.22)
    ctx.fill()
    ctx.translate(0, r + 0.6 * tr + bh / 2)
    wy = -bh / 2 - 0.6 * tr
    ctx.set_source_rgb(0.3, 0.3, 0.34)
    ctx.set_line_width(0.14)
    for wx in v["wheel_x"]:
        ctx.move_to(wx, -bh / 2)
        ctx.line_to(wx, wy)
        ctx.stroke()
    for wx in v["wheel_x"]:
        se.draw_wheel(ctx, wx, wy, wheel_angle, r, vk.startswith("monster"))
    se.draw_body(ctx, vk, v, False, 0.0)
    se.draw_face(ctx, vk, mood, 0.0)
    ctx.restore()


def vehicle_width(vk, s):
    v = se.VEHICLES[vk]
    return (max(v["body"][0], abs(v["wheel_x"][0]) * 2 + v["wheel_r"] * 2) + 0.4) * s


def cloud(ctx, x, y, k=1.0):
    ctx.set_source_rgba(1, 1, 1, 0.95)
    for dx, dy, rr in [(0, 0, 55), (60, -25, 65), (125, 0, 50), (60, 15, 55)]:
        ctx.arc(x + dx * k, y + dy * k, rr * k, 0, 2 * math.pi)
        ctx.fill()


def scenery(ctx, w, h, road_y, hill_amp=1.0, sun=None):
    g = cairo.LinearGradient(0, 0, 0, road_y)
    g.add_color_stop_rgb(0, 0.3, 0.64, 1.0)
    g.add_color_stop_rgb(1, 0.78, 0.93, 1.0)
    ctx.set_source(g)
    ctx.rectangle(0, 0, w, road_y + 5)
    ctx.fill()
    if sun:
        sx, sy, sr = sun
        rg = cairo.RadialGradient(sx, sy, sr * 0.5, sx, sy, sr * 2.6)
        rg.add_color_stop_rgba(0, 1, 0.95, 0.55, 0.9)
        rg.add_color_stop_rgba(1, 1, 0.95, 0.55, 0)
        ctx.set_source(rg)
        ctx.arc(sx, sy, sr * 2.6, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgb(1, 0.9, 0.35)
        ctx.arc(sx, sy, sr, 0, 2 * math.pi)
        ctx.fill()
    for base, col, a1, a2, ph in [(-190, (0.56, 0.8, 0.52), 70, 35, 0.0), (-95, (0.42, 0.72, 0.38), 55, 28, 2.0)]:
        ctx.new_path()
        ctx.move_to(0, road_y)
        for x in range(0, w + 21, 20):
            ctx.line_to(x, road_y + base * hill_amp - a1 * hill_amp * math.sin(x / 260 + ph)
                        - a2 * hill_amp * math.sin(x / 113 + 1 + ph))
        ctx.line_to(w, road_y)
        ctx.close_path()
        ctx.set_source_rgb(*col)
        ctx.fill()
    ctx.rectangle(0, road_y, w, h - road_y)
    ctx.set_source_rgb(0.58, 0.38, 0.22)
    ctx.fill()
    band = max(26, int(h * 0.035))
    ctx.rectangle(0, road_y, w, band)
    ctx.set_source_rgb(0.26, 0.26, 0.3)
    ctx.fill()
    ctx.rectangle(0, road_y, w, band * 0.15)
    ctx.set_source_rgb(0.4, 0.4, 0.45)
    ctx.fill()
    ctx.set_source_rgb(1, 1, 1)
    dash = band * 3.2
    x = 0.0
    while x < w:
        ctx.rectangle(x, road_y + band * 0.45, dash, band * 0.16)
        ctx.fill()
        x += dash * 2
    for depth, col in [(0.45, (0.5, 0.32, 0.18)), (0.7, (0.44, 0.27, 0.15))]:
        y0 = road_y + (h - road_y) * depth
        ctx.new_path()
        ctx.move_to(0, h)
        for x in range(0, w + 21, 20):
            ctx.line_to(x, y0 + 12 * math.sin(x / 90) + 7 * math.sin(x / 37 + depth))
        ctx.line_to(w, h)
        ctx.close_path()
        ctx.set_source_rgb(*col)
        ctx.fill()


def sparkles(ctx, pts, size):
    for x, y, k in pts:
        se.star(ctx, x, y, size * k, 0.3)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgb(1, 0.8, 0.2)
        ctx.set_line_width(3)
        ctx.stroke()


def logo(ctx, cx, y_top, size, max_w):
    """Two-line wordmark: MEGAWHEEL / KIDS."""
    se.draw_text(ctx, "MEGAWHEEL", cx, y_top + size * 0.55, size, fill=YELLOW, stroke=NAVY, sw=size * 0.2,
                 max_w=max_w)
    ctx.save()
    ctx.translate(cx, y_top + size * 1.55)
    ctx.rotate(-0.04)
    se.draw_text(ctx, "KIDS", 0, 0, size * 0.85, fill=(1, 1, 1), stroke=(0.85, 0.12, 0.2), sw=size * 0.2)
    ctx.restore()


# ---------------------------------------------------------------- profile picture
def sunburst(ctx, cx, cy, radius, rays=18, c1=(1, 0.8, 0.15), c2=(1, 0.62, 0.1)):
    ctx.set_source_rgb(*c2)
    ctx.paint()
    for i in range(rays):
        a0 = i * 2 * math.pi / rays
        a1 = a0 + math.pi / rays
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.cos(a0) * radius, cy + math.sin(a0) * radius)
        ctx.line_to(cx + math.cos(a1) * radius, cy + math.sin(a1) * radius)
        ctx.close_path()
        ctx.set_source_rgb(*c1)
        ctx.fill()


def profile(path, with_text):
    s = 800
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, s, s)
    ctx = cairo.Context(surf)
    sunburst(ctx, 400, 470, 800)
    road_y = 600 if with_text else 610
    ctx.rectangle(0, road_y, s, s - road_y)
    ctx.set_source_rgb(0.26, 0.26, 0.3)
    ctx.fill()
    ctx.set_source_rgb(1, 1, 1)
    for x in range(0, s, 90):
        ctx.rectangle(x, road_y + 45, 45, 10)
        ctx.fill()
    if with_text:
        vehicle(ctx, "monster", 400, road_y, 96)
        se.draw_text(ctx, "MEGAWHEEL", 400, 122, 86, fill=YELLOW, stroke=NAVY, sw=17, max_w=560)
        se.draw_text(ctx, "KIDS", 400, 705, 92, fill=(1, 1, 1), stroke=(0.85, 0.12, 0.2), sw=18)
    else:
        vehicle(ctx, "monster", 400, road_y, 122)
        sparkles(ctx, [(135, 170, 1.0), (665, 150, 0.8), (690, 330, 0.6)], 34)
    surf.write_to_png(path)
    check = cairo.ImageSurface(cairo.FORMAT_ARGB32, s, s)
    c = cairo.Context(check)
    c.set_source_rgb(0.12, 0.12, 0.12)
    c.paint()
    c.arc(400, 400, 400, 0, 2 * math.pi)
    c.clip()
    c.set_source_surface(surf, 0, 0)
    c.paint()
    check.write_to_png(path.replace(".png", "_check.png"))


# ---------------------------------------------------------------- banner
def banner(path):
    w, h = 2560, 1440
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)
    road_y = 905
    scenery(ctx, w, h, road_y, hill_amp=1.0, sun=(2350, 250, 110))
    for x, y, k in [(180, 180, 1.2), (700, 300, 0.9), (1150, 150, 1.0), (1700, 260, 0.8), (1950, 120, 1.1),
                    (300, 520, 0.7), (2200, 560, 0.7)]:
        cloud(ctx, x, y, k)
    # whole cast in one row; the two champions sit in the middle so phones (centre 1546 px) always show them
    cast = ["sports", "police", "bus", "firetruck", "monster", "monster2", "bigrig", "icecream", "f1", "taxi"]
    s, gap = 33, 22
    total = sum(vehicle_width(vk, s) for vk in cast) + gap * (len(cast) - 1)
    x = (w - total) / 2
    for vk in cast:
        wv = vehicle_width(vk, s)
        vehicle(ctx, vk, x + wv / 2, road_y, s)
        x += wv + gap
    se.draw_text(ctx, "FUN CAR CHALLENGES FOR KIDS!", 1280, 548, 42, fill=(1, 1, 1), stroke=NAVY, sw=8, max_w=820)
    se.set_font(ctx, 118)
    w1 = ctx.text_extents("MEGAWHEEL").width
    w2 = ctx.text_extents("KIDS").width
    gap_w = 40
    x0 = 1280 - (w1 + gap_w + w2) / 2
    se.draw_text(ctx, "MEGAWHEEL", x0 + w1 / 2, 650, 118, fill=YELLOW, stroke=NAVY, sw=22)
    se.draw_text(ctx, "KIDS", x0 + w1 + gap_w + w2 / 2, 650, 118, fill=(1, 1, 1), stroke=(0.85, 0.12, 0.2), sw=22)
    sparkles(ctx, [(x0 - 60, 610, 0.9), (x0 + w1 + gap_w + w2 + 60, 600, 0.8)], 28)
    se.draw_text(ctx, "NEW VIDEOS EVERY WEEK", 1280, 1180, 64, fill=YELLOW, stroke=NAVY, sw=12)
    surf.write_to_png(path)
    check = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    c = cairo.Context(check)
    c.set_source_surface(surf, 0, 0)
    c.paint()
    c.set_source_rgba(0, 0, 0, 0.45)                 # dim what only TVs show
    c.rectangle(0, 0, w, 508)
    c.rectangle(0, 931, w, h - 931)
    c.fill()
    c.set_line_width(6)
    c.set_source_rgb(1, 0.2, 0.2)
    c.rectangle(507, 508, 1546, 423)                 # visible on every device
    c.stroke()
    c.set_source_rgb(0.2, 1, 0.3)
    c.rectangle(3, 508, w - 6, 423)                  # desktop strip
    c.stroke()
    check.write_to_png(path.replace(".png", "_check.png"))


def main():
    os.makedirs(OUT, exist_ok=True)
    se.detect_font()
    se.load_cast()
    profile(f"{OUT}/profile_mascot.png", with_text=False)
    profile(f"{OUT}/profile_logo.png", with_text=True)
    banner(f"{OUT}/banner.png")
    for f in sorted(os.listdir(OUT)):
        print(f, os.path.getsize(f"{OUT}/{f}"))


if __name__ == "__main__":
    main()
