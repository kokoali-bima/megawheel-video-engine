"""Infrasoft Media & Tech logo (vector, own design): a blue gear whose orange play button breaks out of the ring.
Outputs (branding/infrasoft/): logo_light.png, logo_dark.png, icon.png (transparent, watermark), icon.svg.
Run: venv/bin/python branding/infrasoft/make_logo.py"""
import math
import os
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))

BLUE, BLUE2, ORANGE, NAVY = (0.10, 0.42, 0.93), (0.07, 0.62, 0.96), (1.0, 0.45, 0.10), (0.06, 0.15, 0.30)
N_TEETH, R_OUT, R_ROOT, R_HOLE = 9, 1.0, 0.84, 0.56


def gear_path(ctx):
    """Gear outline (outer contour, then the hole, even-odd)."""
    step = 2 * math.pi / N_TEETH
    pts = []
    for i in range(N_TEETH):
        a = i * step - math.pi / 2
        for da, r in ((-0.27, R_ROOT), (-0.16, R_OUT), (0.16, R_OUT), (0.27, R_ROOT)):
            pts.append((a + da * step, r))
    ctx.move_to(pts[0][1] * math.cos(pts[0][0]), pts[0][1] * math.sin(pts[0][0]))
    for a, r in pts[1:]:
        ctx.line_to(r * math.cos(a), r * math.sin(a))
    ctx.close_path()
    ctx.new_sub_path()
    ctx.arc_negative(0, 0, R_HOLE, 2 * math.pi, 0)
    ctx.close_path()


def play_path(ctx):
    """Play triangle: rounded, centred slightly right, tip out through the gear's right side."""
    p = [(-0.30, -0.50), (1.12, 0.0), (-0.30, 0.50)]
    rad = 0.08
    ctx.new_path()
    for i in range(3):
        a, b, c = p[i - 1], p[i], p[(i + 1) % 3]
        v1 = ((a[0] - b[0]), (a[1] - b[1]))
        v2 = ((c[0] - b[0]), (c[1] - b[1]))
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        s1 = (b[0] + v1[0] / l1 * rad * 1.6, b[1] + v1[1] / l1 * rad * 1.6)
        s2 = (b[0] + v2[0] / l2 * rad * 1.6, b[1] + v2[1] / l2 * rad * 1.6)
        if i == 0:
            ctx.move_to(*s1)
        else:
            ctx.line_to(*s1)
        ctx.curve_to(b[0], b[1], b[0], b[1], *s2)
    ctx.close_path()


def icon(ctx, cx, cy, size, dark=False):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(size / 2.3, size / 2.3)
    g = cairo.LinearGradient(-1, -1, 1, 1)
    g.add_color_stop_rgb(0, *BLUE2)
    g.add_color_stop_rgb(1, *BLUE)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    gear_path(ctx)
    ctx.set_source(g)
    ctx.fill()
    play_path(ctx)                                  # a gap around the triangle where it crosses the ring
    ctx.set_source_rgb(*((0.04, 0.05, 0.10) if dark else (1, 1, 1)))
    ctx.set_line_width(0.16)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*ORANGE)
    ctx.fill()
    ctx.restore()


def text(ctx, s, cx, cy, size, rgb, weight=cairo.FONT_WEIGHT_BOLD, track=0.0):
    """Montserrat (OFL) centred text with letter spacing."""
    ctx.select_font_face("Montserrat", cairo.FONT_SLANT_NORMAL, weight)
    ctx.set_font_size(size)
    widths = [ctx.text_extents(ch).x_advance for ch in s]
    total = sum(widths) + track * size * (len(s) - 1)
    x = cx - total / 2
    ext = ctx.text_extents(s)
    ctx.set_source_rgb(*rgb)
    for ch, w in zip(s, widths):
        ctx.move_to(x, cy - ext.height / 2 - ext.y_bearing)
        ctx.show_text(ch)
        x += w + track * size


def logo(path, dark):
    W, H = 2000, 1600
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgb(*((0.04, 0.05, 0.10) if dark else (1, 1, 1)))
    ctx.fill()
    icon(ctx, W / 2 - 40, 560, 820, dark)
    text(ctx, "INFRASOFT", W / 2, 1185, 250, (1, 1, 1) if dark else NAVY, track=0.04)
    text(ctx, "MEDIA & TECH", W / 2, 1390, 96, BLUE2 if dark else BLUE, weight=cairo.FONT_WEIGHT_NORMAL, track=0.32)
    surf.write_to_png(path)


def icon_png(path, size=1024):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    ctx = cairo.Context(surf)
    icon(ctx, size / 2 - size * 0.02, size / 2, size * 0.92, dark=True)
    surf.write_to_png(path)


def icon_svg(path):
    surf = cairo.SVGSurface(path, 512, 512)
    ctx = cairo.Context(surf)
    icon(ctx, 250, 256, 470)
    surf.finish()


if __name__ == "__main__":
    logo(os.path.join(HERE, "logo_light.png"), False)
    logo(os.path.join(HERE, "logo_dark.png"), True)
    icon_png(os.path.join(HERE, "icon.png"))
    icon_svg(os.path.join(HERE, "icon.svg"))
    print("ok")
