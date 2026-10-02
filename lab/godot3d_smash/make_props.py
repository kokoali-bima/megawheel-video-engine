"""LAB plan B v2 — paper-cutout props for the 3D smash arena, drawn with cairo in the cast's flat cartoon style.
  shark_open.png / shark_closed.png (side view, facing right), fin.png (dorsal fin for the circling sharks),
  pow.png (comic impact burst).   venv/bin/python lab/godot3d_smash/make_props.py /root/lab/fx/sprites"""
import math
import os
import random
import sys

import cairo

INK = (0.1, 0.11, 0.17)
SKIN = (0.42, 0.56, 0.7)
SKIN_D = (0.33, 0.45, 0.58)
BELLY = (0.95, 0.96, 0.98)


def surf(w, h):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    return s, cairo.Context(s)


def fill_ink(c, col, lw=7):
    c.set_source_rgb(*col)
    c.fill_preserve()
    c.set_source_rgb(*INK)
    c.set_line_width(lw)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.stroke()


def teeth(c, a, b, n, h, side):
    """n white triangles along a->b, pointing to `side` (+1 left normal, -1 right normal)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dy)
    nx, ny = -dy / ln * side, dx / ln * side
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        p0 = (a[0] + dx * t0, a[1] + dy * t0)
        p1 = (a[0] + dx * t1, a[1] + dy * t1)
        m = ((p0[0] + p1[0]) / 2 + nx * h, (p0[1] + p1[1]) / 2 + ny * h)
        c.move_to(*p0)
        c.line_to(*p1)
        c.line_to(*m)
        c.close_path()
        fill_ink(c, (1, 1, 1), 3)


def shark(open_mouth):
    s, c = surf(960, 480)
    if open_mouth:                                  # mouth interior + lower jaw first, body on top
        c.move_to(905, 262)
        c.line_to(700, 292)
        c.line_to(905, 380)
        c.close_path()
        fill_ink(c, (0.55, 0.08, 0.12))
        c.save()
        c.translate(800, 335)
        c.scale(1.6, 0.6)
        c.arc(0, 0, 38, 0, 2 * math.pi)
        c.restore()
        c.set_source_rgb(0.93, 0.42, 0.5)
        c.fill()
        teeth(c, (900, 264), (705, 292), 6, 24, -1)
        teeth(c, (705, 296), (898, 376), 6, 22, -1)
        c.move_to(700, 292)
        c.line_to(675, 332)
        c.curve_to(760, 400, 860, 425, 918, 398)
        c.line_to(905, 380)
        c.curve_to(830, 372, 760, 335, 700, 292)
        c.close_path()
        fill_ink(c, BELLY)
    # body
    c.move_to(905, 262)
    c.curve_to(820, 170, 700, 140, 590, 148)
    c.curve_to(420, 160, 260, 190, 150, 228)
    c.line_to(58, 104)
    c.curve_to(90, 190, 110, 230, 122, 254)
    c.curve_to(95, 292, 76, 332, 58, 384)
    c.line_to(150, 284)
    c.curve_to(300, 332, 520, 350, 680, 330)
    if open_mouth:
        c.line_to(700, 292)
        c.line_to(905, 262)
    else:
        c.curve_to(790, 318, 870, 300, 905, 262)
    c.close_path()
    path = c.copy_path()
    c.set_source_rgb(*SKIN)
    c.fill()
    c.save()                                        # white belly inside the body
    c.append_path(path)
    c.clip()
    c.move_to(140, 272)
    c.curve_to(400, 292, 650, 300, 910, 270)
    c.line_to(910, 420)
    c.line_to(140, 420)
    c.close_path()
    c.set_source_rgb(*BELLY)
    c.fill()
    c.restore()
    c.append_path(path)
    c.set_source_rgb(*INK)
    c.set_line_width(7)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.stroke()
    # dorsal + pectoral fins
    c.move_to(552, 152)
    c.curve_to(540, 92, 505, 44, 468, 18)
    c.curve_to(560, 40, 640, 100, 684, 150)
    fill_ink(c, SKIN)
    c.move_to(598, 318)
    c.curve_to(580, 368, 556, 400, 515, 424)
    c.curve_to(600, 414, 660, 372, 684, 326)
    fill_ink(c, SKIN_D)
    c.set_source_rgb(*INK)                          # gills
    c.set_line_width(5)
    for gx in (628, 652, 676):
        c.move_to(gx, 222)
        c.curve_to(gx - 10, 245, gx - 10, 262, gx, 284)
        c.stroke()
    # eye with a cheeky brow (same big-eye look as the cars)
    c.arc(790, 214, 32, 0, 2 * math.pi)
    fill_ink(c, (1, 1, 1), 5)
    c.arc(802, 216, 16, 0, 2 * math.pi)
    c.set_source_rgb(*INK)
    c.fill()
    c.arc(807, 210, 5, 0, 2 * math.pi)
    c.set_source_rgb(1, 1, 1)
    c.fill()
    c.set_source_rgb(*INK)
    c.set_line_width(9)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(752, 176)
    c.line_to(828, 192)
    c.stroke()
    if not open_mouth:                              # toothy grin
        c.set_line_width(6)
        c.move_to(712, 290)
        c.curve_to(780, 302, 850, 292, 898, 268)
        c.stroke()
        teeth(c, (722, 292), (890, 272), 7, 14, -1)
    return s


def fin():
    s, c = surf(240, 200)
    c.move_to(30, 188)
    c.curve_to(70, 120, 120, 50, 150, 12)
    c.curve_to(170, 80, 190, 140, 214, 188)
    c.close_path()
    fill_ink(c, SKIN, 6)
    c.move_to(150, 30)
    c.curve_to(160, 90, 175, 140, 190, 180)
    c.set_source_rgba(1, 1, 1, 0.35)
    c.set_line_width(8)
    c.stroke()
    return s


def pow_burst(seed=3):
    rnd = random.Random(seed)
    s, c = surf(512, 512)
    for k, (r_out, r_in, col, lw) in enumerate([(250, 150, (1, 0.86, 0.12), 12), (165, 100, (1, 1, 1), 0)]):
        n = 14
        for i in range(n * 2):
            a = i / (n * 2) * 2 * math.pi
            r = (r_out if i % 2 == 0 else r_in) * rnd.uniform(0.85, 1.0)
            x, y = 256 + math.cos(a) * r, 256 + math.sin(a) * r
            c.line_to(x, y) if i else c.move_to(x, y)
        c.close_path()
        c.set_source_rgb(*col)
        if lw:
            c.fill_preserve()
            c.set_source_rgb(0.9, 0.2, 0.1)
            c.set_line_width(lw)
            c.set_line_join(cairo.LINE_JOIN_ROUND)
            c.stroke()
        else:
            c.fill()
    return s


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/root/lab/fx/sprites"
    os.makedirs(out, exist_ok=True)
    shark(True).write_to_png(os.path.join(out, "shark_open.png"))
    shark(False).write_to_png(os.path.join(out, "shark_closed.png"))
    fin().write_to_png(os.path.join(out, "fin.png"))
    pow_burst().write_to_png(os.path.join(out, "pow.png"))
    print("[props] shark_open/closed, fin, pow ->", out)


if __name__ == "__main__":
    main()
