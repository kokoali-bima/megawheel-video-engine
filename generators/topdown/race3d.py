#!/usr/bin/env python3
"""MegaWheel Arena — Top-Down 2.5D / pseudo-3D race engine (PROTOTYPE, style test).

Physics: flat 2D world (pymunk, no gravity) with a tyre-grip model -> real skids, drifts and
hydroplane spins on puddles. Rendering: a tiny 3D projection on cairo (camera above/behind the pack,
real perspective), cars as shaded low-poly boxes, ground decals (kerbs, puddles, skid marks).

Usage (cd /root/video-engine):
  ./venv/bin/python generators/topdown/race3d.py --seed 1 --seconds 14 --out work/topdown/proto.mp4
Output: MP4 (no audio yet) + PNG frames in the same folder (prototype, NOT a publishable episode).
"""
import argparse
import math
import os
import subprocess
import sys

import cairo
import numpy as np
import pymunk

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "physics_2d"))
import sim_engine as se  # noqa: E402  (cast identity + fonts only)

W, H, FPS = 1080, 1920, 30
PHYS_HZ = 120
TRACK_W = 15.0                     # road width (m)
STEP = 0.5                         # centerline sample spacing (m)
MU_ROAD, MU_WATER = 1.15, 0.10     # tyre grip on asphalt / standing water
F_LEN = (H / 2) / math.tan(math.radians(36))   # focal length for a ~72 deg vertical field of view

# racers: cast key -> top-down size (length, width) and box heights (clearance, body top, roof top)
CAR_SHAPES = {
    "sports": dict(size=(4.4, 2.0), z=(0.25, 0.75, 1.2), cabin=(0.45, -0.25)),
    "f1": dict(size=(5.0, 1.9), z=(0.1, 0.5, 0.95), cabin=(0.18, -0.1)),
    "taxi": dict(size=(4.7, 2.0), z=(0.3, 0.95, 1.55), cabin=(0.55, -0.15)),
    "police": dict(size=(4.8, 2.0), z=(0.3, 0.95, 1.55), cabin=(0.55, -0.15)),
}
RACERS = [("sports", 30.0, 1.05), ("f1", 32.0, 1.00), ("taxi", 28.5, 1.10), ("police", 29.5, 1.08)]
#          key,      vmax m/s, corner courage (>1 = brakes later, may overshoot)


# ------------------------------------------------------------------ track
def build_track(seed):
    rng = np.random.default_rng(9000 + seed)
    spec = [("S", 45)]
    turn = 1 if rng.random() < 0.5 else -1
    for _ in range(5):
        spec.append(("C", float(rng.uniform(28, 45)), turn * float(rng.uniform(45, 95))))
        spec.append(("S", float(rng.uniform(25, 45))))
        turn = -turn if rng.random() < 0.75 else turn
    x, y, a = 0.0, 0.0, math.pi / 2
    pts = [(x, y, a)]
    for seg in spec:
        if seg[0] == "S":
            for _ in range(int(seg[1] / STEP)):
                x, y = x + math.cos(a) * STEP, y + math.sin(a) * STEP
                pts.append((x, y, a))
        else:
            r, ang = seg[1], math.radians(seg[2])
            n = max(1, int(r * abs(ang) / STEP))
            for _ in range(n):
                a += ang / n
                x, y = x + math.cos(a) * STEP, y + math.sin(a) * STEP
                pts.append((x, y, a))
    t = np.array(pts)
    # puddles: at the entry of three corners (where a spin hurts most), across part of the road
    starts = [i for i in range(1, len(spec)) if spec[i][0] == "C"]
    puddles, s_acc = [], 0.0
    seg_s = []
    for seg in spec:
        seg_s.append(s_acc)
        s_acc += seg[1] if seg[0] == "S" else seg[1] * abs(math.radians(seg[2]))
    for ci in starts[:4:1][:3]:
        s0 = seg_s[ci] - float(rng.uniform(14, 22))
        d0 = float(rng.uniform(-TRACK_W / 2 + 1, 0.5))
        puddles.append(dict(s0=s0, s1=s0 + float(rng.uniform(9, 14)), d0=d0, d1=d0 + float(rng.uniform(6, 9))))
    return t, puddles, spec


class Track:
    def __init__(self, seed):
        self.t, self.puddles, self.spec = build_track(seed)
        self.n = len(self.t)
        self.length = (self.n - 1) * STEP
        self.finish_s = self.length - 25.0

    def nearest(self, x, y, hint):
        lo, hi = max(0, hint - 60), min(self.n, hint + 60)
        seg = self.t[lo:hi]
        i = lo + int(np.argmin((seg[:, 0] - x) ** 2 + (seg[:, 1] - y) ** 2))
        return i

    def frame(self, i):
        i = int(np.clip(i, 0, self.n - 1))
        x, y, a = self.t[i]
        return x, y, a, (-math.sin(a), math.cos(a))           # point, heading, left normal

    def coords(self, x, y, hint):
        i = self.nearest(x, y, hint)
        cx, cy, a, nl = self.frame(i)
        return i, i * STEP, (x - cx) * nl[0] + (y - cy) * nl[1]  # index, s, lateral (+ = left)

    def point(self, s, d):
        cx, cy, a, nl = self.frame(s / STEP)
        return cx + nl[0] * d, cy + nl[1] * d

    def in_puddle(self, s, d):
        return any(p["s0"] <= s <= p["s1"] and p["d0"] <= d <= p["d1"] for p in self.puddles)

    def curvature_ahead(self, s, dist):
        i0, i1 = int(s / STEP), int(min(self.n - 1, (s + dist) / STEP))
        if i1 <= i0 + 2:
            return 0.0
        da = np.abs(np.diff(np.unwrap(self.t[i0:i1 + 1, 2])))
        k = np.convolve(da / STEP, np.ones(9) / 9, mode="same")
        return float(np.max(k))


# ------------------------------------------------------------------ physics
def simulate(track, seconds, seed):
    rng = np.random.default_rng(seed)
    space = pymunk.Space()
    space.gravity = (0, 0)
    for side in (1, -1):                                         # soft barriers (tyre walls) both sides
        prev = None
        for i in range(0, track.n, 4):
            x, y, a, nl = track.frame(i)
            p = (x + nl[0] * side * (TRACK_W / 2 + 1.6), y + nl[1] * side * (TRACK_W / 2 + 1.6))
            if prev:
                seg = pymunk.Segment(space.static_body, prev, p, 0.4)
                seg.elasticity, seg.friction = 0.35, 0.6
                space.add(seg)
            prev = p
    cars = []
    lanes = [-4.5, -1.5, 1.5, 4.5]
    for k, (key, vmax, courage) in enumerate(RACERS):
        L, Wd = CAR_SHAPES[key]["size"]
        m = 1200.0
        b = pymunk.Body(m, pymunk.moment_for_box(m, (L, Wd)))
        s0 = 14.0 - (k // 2) * 7.0
        b.position = track.point(s0, lanes[k])
        b.angle = track.frame(s0 / STEP)[2]
        shp = pymunk.Poly.create_box(b, (L, Wd), radius=0.05)
        shp.elasticity, shp.friction = 0.3, 0.7
        space.add(b, shp)
        cars.append(dict(key=key, body=b, L=L, Wd=Wd, vmax=vmax * float(rng.uniform(0.97, 1.03)),
                         courage=courage, lane=lanes[k], hint=int(s0 / STEP), wet=False, spin=None,
                         finish=None, rec=[]))
    dt = 1.0 / PHYS_HZ
    skids = []                                                    # (t, x, y, car index) rear-tyre marks
    splash = []                                                   # (t, x, y, speed) puddle entries
    n_steps = int(seconds * PHYS_HZ)
    for step in range(n_steps):
        t = step * dt
        order = sorted(range(len(cars)), key=lambda j: -track.coords(*cars[j]["body"].position, cars[j]["hint"])[1])
        for ci, c in enumerate(cars):
            b = c["body"]
            a = b.angle
            f = (math.cos(a), math.sin(a))
            n = (-math.sin(a), math.cos(a))
            v = b.velocity
            vf, vl = v.x * f[0] + v.y * f[1], v.x * n[0] + v.y * n[1]
            i, s, d = track.coords(b.position.x, b.position.y, c["hint"])
            c["hint"] = i
            wet = track.in_puddle(s, d)
            mu = MU_WATER if wet else MU_ROAD
            if wet and not c["wet"]:
                splash.append((t, b.position.x, b.position.y, abs(vf)))
                if abs(vf) > 17 and rng.random() < min(0.9, (abs(vf) - 15) / 10):   # hydroplane: yaw kick
                    b.angular_velocity += float(rng.choice([-1, 1]) * rng.uniform(2.5, 4.5))
                    c["spin"] = t
            c["wet"] = wet
            # --- driver AI: pure pursuit on a lane line, brake for corners, dodge the car ahead
            lane = c["lane"]
            for oj in order:
                o = cars[oj]
                if o is c:
                    continue
                oi, os_, od = track.coords(*o["body"].position, o["hint"])
                if 0 < os_ - s < 14 and abs(od - lane) < 2.4:
                    lane = od + (3.2 if od < 2 else -3.2)
            lane = float(np.clip(lane, -TRACK_W / 2 + 1.8, TRACK_W / 2 - 1.8))
            look = 9.0 + 0.45 * abs(vf)
            tx, ty = track.point(min(track.length, s + look), lane)
            ang = math.atan2(ty - b.position.y, tx - b.position.x) - a
            ang = (ang + math.pi) % (2 * math.pi) - math.pi
            steer = float(np.clip(math.atan2(2 * 2.6 * math.sin(ang), look), -0.6, 0.6))
            k_curv = track.curvature_ahead(s, 10 + 1.2 * abs(vf))
            v_corner = math.sqrt(c["courage"] * MU_ROAD * 9.81 / max(k_curv, 1e-3))
            v_target = min(c["vmax"], v_corner) if c["finish"] is None else 6.0
            if abs(ang) > 1.6:                                    # facing the wrong way after a spin
                v_target = 5.0
            throttle = float(np.clip((v_target - vf) / 4.0, -1.0, 1.0))
            # --- tyre forces (grip-limited)
            fmax = mu * b.mass * 9.81
            drive = throttle * (0.55 if throttle > 0 else 1.0) * fmax
            lat = float(np.clip(-vl * b.mass * 6.0, -fmax, fmax))
            if (drive ** 2 + lat ** 2) ** 0.5 > fmax * 1.05:       # friction circle
                sc = fmax * 1.05 / (drive ** 2 + lat ** 2) ** 0.5
                drive, lat = drive * sc, lat * sc
            b.apply_force_at_world_point((f[0] * drive + n[0] * lat, f[1] * drive + n[1] * lat), b.position)
            yaw_target = vf * math.tan(steer) / 2.6
            g = min(1.0, mu * 7.0 * dt)
            b.angular_velocity += (yaw_target - b.angular_velocity) * g
            b.velocity = b.velocity * (1 - 0.02 * dt)                # rolling resistance
            if abs(vl) > 2.8:                                     # sliding -> skid marks from rear tyres
                if step % 3 == 0:
                    for side in (1, -1):
                        rx = b.position.x - f[0] * c["L"] * 0.35 + n[0] * side * c["Wd"] * 0.4
                        ry = b.position.y - f[1] * c["L"] * 0.35 + n[1] * side * c["Wd"] * 0.4
                        skids.append((t, rx, ry, ci, side))
            if c["finish"] is None and s >= track.finish_s:
                c["finish"] = t
        space.step(dt)
        if step % (PHYS_HZ // FPS) == 0:
            for c in cars:
                b = c["body"]
                i, s, d = track.coords(b.position.x, b.position.y, c["hint"])
                vl = -b.velocity.x * math.sin(b.angle) + b.velocity.y * math.cos(b.angle)
                c["rec"].append((b.position.x, b.position.y, b.angle, s, b.velocity.length, vl, c["wet"]))
    return cars, skids, splash


# ------------------------------------------------------------------ 3D camera
class Cam:
    def __init__(self, x, y, yaw, back=24.0, height=21.0, pitch=math.radians(46)):
        f = (math.cos(yaw), math.sin(yaw))
        self.c = np.array([x - f[0] * back, y - f[1] * back, height])
        d = np.array([f[0] * math.cos(pitch), f[1] * math.cos(pitch), -math.sin(pitch)])
        r = np.array([f[1], -f[0], 0.0])
        self.d, self.r, self.u = d, r, np.cross(r, d)

    def proj(self, p):
        v = np.asarray(p, dtype=float) - self.c
        z = float(v @ self.d)
        if z < 0.8:
            return None
        return W / 2 + F_LEN * float(v @ self.r) / z, H / 2 - F_LEN * float(v @ self.u) / z, z

    def depth(self, p):
        return float((np.asarray(p, dtype=float) - self.c) @ self.d)


def poly_ground(ctx, cam, pts, rgba, seal=False):
    pp = [cam.proj((x, y, z)) for x, y, z in pts]
    if any(p is None for p in pp):
        return False
    ctx.move_to(pp[0][0], pp[0][1])
    for p in pp[1:]:
        ctx.line_to(p[0], p[1])
    ctx.close_path()
    ctx.set_source_rgba(*rgba)
    if seal:                                                     # hide anti-aliasing seams between strips
        ctx.fill_preserve()
        ctx.set_line_width(1.6)
        ctx.stroke()
    else:
        ctx.fill()
    return True


# ------------------------------------------------------------------ drawing
def shade(col, k):
    return tuple(min(1.0, max(0.0, c * k)) for c in col)


LIGHT = np.array([-0.4, -0.3, 0.87])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def box_faces(x, y, a, lx0, lx1, ly0, ly1, z0, z1, col, sx=1.0):
    """World faces (verts, normal, colour) of a box in car-local coords (x forward, y left)."""
    ca, sa = math.cos(a), math.sin(a)

    def w(px, py, pz):
        return (x + (px * ca - py * sa), y + (px * sa + py * ca), pz)

    lx0, lx1 = lx0 * sx, lx1 * sx
    c = {k: w(*k) for k in [(px, py, pz) for px in (lx0, lx1) for py in (ly0, ly1) for pz in (z0, z1)]}
    faces = [
        ([c[(lx0, ly0, z1)], c[(lx1, ly0, z1)], c[(lx1, ly1, z1)], c[(lx0, ly1, z1)]], (0, 0, 1)),
        ([c[(lx1, ly0, z0)], c[(lx1, ly1, z0)], c[(lx1, ly1, z1)], c[(lx1, ly0, z1)]], (ca, sa, 0)),
        ([c[(lx0, ly1, z0)], c[(lx0, ly0, z0)], c[(lx0, ly0, z1)], c[(lx0, ly1, z1)]], (-ca, -sa, 0)),
        ([c[(lx0, ly1, z0)], c[(lx1, ly1, z0)], c[(lx1, ly1, z1)], c[(lx0, ly1, z1)]], (-sa, ca, 0)),
        ([c[(lx1, ly0, z0)], c[(lx0, ly0, z0)], c[(lx0, ly0, z1)], c[(lx1, ly0, z1)]], (sa, -ca, 0)),
    ]
    return [(vs, np.array(nrm, dtype=float), col) for vs, nrm in faces]


def car_faces(c, x, y, a):
    shp = CAR_SHAPES[c["key"]]
    L, Wd = shp["size"]
    z0, z1, z2 = shp["z"]
    col = c["color"]
    f = []
    for wx in (L * 0.32, -L * 0.32):                             # wheels
        for side in (1, -1):
            f += box_faces(x, y, a, wx - 0.38, wx + 0.38, side * Wd * 0.38, side * (Wd * 0.5 + 0.08),
                           0.0, 0.68, (0.1, 0.1, 0.12))
    f += box_faces(x, y, a, -L / 2, L / 2, -Wd / 2, Wd / 2, z0, z1, col)          # body
    cl, co = shp["cabin"]
    cab = L * cl
    glass = (0.35, 0.55, 0.75)
    f += box_faces(x, y, a, co * L - cab / 2, co * L + cab / 2, -Wd * 0.42, Wd * 0.42, z1, z2, glass)
    f += box_faces(x, y, a, co * L - cab / 2 + 0.1, co * L + cab / 2 - 0.1, -Wd * 0.4, Wd * 0.4, z2 - 0.06,
                   z2, col)                                                       # roof
    if c["key"] == "police":
        f += box_faces(x, y, a, co * L - 0.2, co * L + 0.2, -0.6, 0.6, z2, z2 + 0.18, (0.9, 0.1, 0.1))
    if c["key"] == "taxi":
        f += box_faces(x, y, a, co * L - 0.25, co * L + 0.25, -0.35, 0.35, z2, z2 + 0.22, (1, 0.95, 0.4))
    if c["key"] == "f1":
        f += box_faces(x, y, a, -L / 2, -L / 2 + 0.5, -Wd / 2 - 0.1, Wd / 2 + 0.1, 0.7, 0.85, col)  # rear wing
        f += box_faces(x, y, a, L / 2 - 0.4, L / 2, -Wd / 2 - 0.15, Wd / 2 + 0.15, 0.1, 0.25, col)  # front wing
    return f


def draw_faces(ctx, cam, faces):
    items = []
    for vs, nrm, col in faces:
        ctr = np.mean(np.array(vs), axis=0)
        if nrm @ (cam.c - ctr) <= 0:                             # back-face cull
            continue
        pp = [cam.proj(v) for v in vs]
        if any(p is None for p in pp):
            continue
        k = 0.55 + 0.45 * max(0.0, float(nrm @ LIGHT))
        items.append((cam.depth(ctr), pp, shade(col, k)))
    for _, pp, col in sorted(items, key=lambda it: -it[0]):
        ctx.move_to(pp[0][0], pp[0][1])
        for p in pp[1:]:
            ctx.line_to(p[0], p[1])
        ctx.close_path()
        ctx.set_source_rgb(*col)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.05, 0.05, 0.1, 0.55)
        ctx.set_line_width(1.5)
        ctx.stroke()


def draw_scene(ctx, track, cars, skids, splash, trees, fi, t, cam):
    ctx.set_source_rgb(0.36, 0.62, 0.3)
    ctx.paint()
    # grass tiles (world-aligned checker) -> strong depth cue
    cx, cy = cam.c[0], cam.c[1]
    for gx in range(int(cx // 10) * 10 - 90, int(cx // 10) * 10 + 100, 10):
        for gy in range(int(cy // 10) * 10 - 90, int(cy // 10) * 10 + 100, 10):
            if (gx // 10 + gy // 10) % 2 == 0:
                poly_ground(ctx, cam, [(gx, gy, 0), (gx + 10, gy, 0), (gx + 10, gy + 10, 0), (gx, gy + 10, 0)],
                            (0.4, 0.68, 0.33, 1))
    # road strips, kerbs, lane dashes
    for i in range(0, track.n - 2, 2):
        x0, y0, a0, n0 = track.frame(i)
        x1, y1, a1, n1 = track.frame(i + 2)
        if cam.depth((x0, y0, 0)) < 0 or cam.depth((x0, y0, 0)) > 170:
            continue
        hw = TRACK_W / 2
        poly_ground(ctx, cam, [(x0 + n0[0] * hw, y0 + n0[1] * hw, 0), (x1 + n1[0] * hw, y1 + n1[1] * hw, 0),
                               (x1 - n1[0] * hw, y1 - n1[1] * hw, 0), (x0 - n0[0] * hw, y0 - n0[1] * hw, 0)],
                    (0.3, 0.3, 0.34, 1), seal=True)
        kc = (0.9, 0.12, 0.12, 1) if (i // 4) % 2 else (0.97, 0.97, 0.97, 1)
        for side in (1, -1):
            e0, e1 = hw * side, (hw + 0.9) * side
            poly_ground(ctx, cam, [(x0 + n0[0] * e0, y0 + n0[1] * e0, 0), (x1 + n1[0] * e0, y1 + n1[1] * e0, 0),
                                   (x1 + n1[0] * e1, y1 + n1[1] * e1, 0), (x0 + n0[0] * e1, y0 + n0[1] * e1, 0)],
                        kc)
        if (i // 6) % 2 == 0:
            for dl in (-2.5, 2.5):
                poly_ground(ctx, cam, [(x0 + n0[0] * (dl - 0.12), y0 + n0[1] * (dl - 0.12), 0),
                                       (x1 + n1[0] * (dl - 0.12), y1 + n1[1] * (dl - 0.12), 0),
                                       (x1 + n1[0] * (dl + 0.12), y1 + n1[1] * (dl + 0.12), 0),
                                       (x0 + n0[0] * (dl + 0.12), y0 + n0[1] * (dl + 0.12), 0)],
                            (1, 1, 1, 0.8))
    # finish line (checkered)
    fs = track.finish_s
    for row in range(2):
        for k in range(int(TRACK_W / 1.0)):
            d0 = -TRACK_W / 2 + k * 1.0
            s0 = fs + row * 1.0
            col = (0.05, 0.05, 0.05, 1) if (k + row) % 2 else (1, 1, 1, 1)
            poly_ground(ctx, cam, [(*track.point(s0, d0), 0), (*track.point(s0, d0 + 1), 0),
                                   (*track.point(s0 + 1, d0 + 1), 0), (*track.point(s0 + 1, d0), 0)], col)
    # puddles: blue water with shimmer
    for p in track.puddles:
        ring = []
        for k in range(20):
            th = 2 * math.pi * k / 20
            s_ = (p["s0"] + p["s1"]) / 2 + (p["s1"] - p["s0"]) / 2 * math.cos(th) * (1 + 0.08 * math.sin(3 * th))
            d_ = (p["d0"] + p["d1"]) / 2 + (p["d1"] - p["d0"]) / 2 * math.sin(th) * (1 + 0.1 * math.cos(2 * th))
            ring.append((*track.point(s_, d_), 0))
        poly_ground(ctx, cam, ring, (0.25, 0.55, 0.95, 0.85))
        for k in range(4):
            s_ = p["s0"] + (p["s1"] - p["s0"]) * (0.2 + 0.2 * k) + 0.6 * math.sin(t * 2 + k)
            d_ = (p["d0"] + p["d1"]) / 2 + (k - 1.5) * 1.1
            poly_ground(ctx, cam, [(*track.point(s_, d_ - 0.6), 0), (*track.point(s_ + 0.25, d_ - 0.6), 0),
                                   (*track.point(s_ + 0.25, d_ + 0.6), 0), (*track.point(s_, d_ + 0.6), 0)],
                        (1, 1, 1, 0.6))
    # skid marks (persistent rubber lines per tyre)
    last = {}
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for st, x, y, ci, side in skids:
        if st > t:
            break
        key = (ci, side)
        pp = cam.proj((x, y, 0))
        prev = last.get(key)
        if pp and prev and st - prev[0] < 0.06:
            ctx.move_to(prev[1][0], prev[1][1])
            ctx.line_to(pp[0], pp[1])
            ctx.set_line_width(max(2.0, F_LEN * 0.28 / pp[2]))
            ctx.set_source_rgba(0.07, 0.07, 0.07, 0.55)
            ctx.stroke()
        last[key] = (st, pp) if pp else None
    # objects: shadows first, then trees + cars sorted by depth
    objs = []
    for ci, c in enumerate(cars):
        x, y, a = c["rec"][fi][:3]
        L, Wd = CAR_SHAPES[c["key"]]["size"]
        ca, sa = math.cos(a), math.sin(a)
        sh = [(x + (px * ca - py * sa) + 0.5, y + (px * sa + py * ca) + 0.4, 0)
              for px, py in ((-L / 2, -Wd / 2), (L / 2, -Wd / 2), (L / 2, Wd / 2), (-L / 2, Wd / 2))]
        poly_ground(ctx, cam, sh, (0, 0, 0, 0.3))
        objs.append((cam.depth((x, y, 0)), "car", ci))
    for ti, (x, y, r) in enumerate(trees):
        dd = cam.depth((x, y, 0))
        if 1 < dd < 170:
            pp = cam.proj((x + 1.2, y + 1.0, 0))
            if pp:
                rr = F_LEN * r / pp[2]
                ctx.save()
                ctx.translate(pp[0], pp[1])
                ctx.scale(1, 0.45)
                ctx.arc(0, 0, rr, 0, 2 * math.pi)
                ctx.restore()
                ctx.set_source_rgba(0, 0, 0, 0.25)
                ctx.fill()
            objs.append((dd, "tree", ti))
    for dd, kind, idx in sorted(objs, key=lambda o: -o[0]):
        if kind == "car":
            c = cars[idx]
            x, y, a = c["rec"][fi][:3]
            draw_faces(ctx, cam, car_faces(c, x, y, a))
        else:
            x, y, r = trees[idx]
            base, top = cam.proj((x, y, 0)), cam.proj((x, y, 3.2 + r))
            if base and top:
                ctx.set_source_rgb(0.4, 0.25, 0.12)
                ctx.set_line_width(max(2, F_LEN * 0.35 / base[2]))
                ctx.move_to(base[0], base[1])
                ctx.line_to(top[0], top[1])
                ctx.stroke()
                rr = F_LEN * r / top[2]
                for k, (dx, dy, sc, col) in enumerate(((0, 0, 1.0, (0.13, 0.42, 0.18)),
                                                       (-0.25, -0.25, 0.7, (0.2, 0.55, 0.25)))):
                    ctx.arc(top[0] + dx * rr, top[1] + dy * rr, rr * sc, 0, 2 * math.pi)
                    ctx.set_source_rgb(*col)
                    ctx.fill()
    # water spray from cars in puddles (projected particles)
    for c in cars:
        for back in range(0, 12):
            j = fi - back
            if j < 0:
                break
            x, y, a, s, sp, vl, wet = c["rec"][j]
            if not wet or sp < 3:
                continue
            age = back / FPS
            rng = np.random.default_rng(j * 7 + len(c["key"]))
            for q in range(10):
                vx = -math.cos(a) * sp * 0.25 + rng.uniform(-3, 3) + math.cos(a) * sp * 0.6
                vy = -math.sin(a) * sp * 0.25 + rng.uniform(-3, 3) + math.sin(a) * sp * 0.6
                vz = rng.uniform(2, 5)
                px, py = x + vx * age, y + vy * age
                pz = max(0.0, 0.3 + vz * age - 4.9 * age * age)
                pp = cam.proj((px, py, pz))
                if pp:
                    ctx.arc(pp[0], pp[1], max(2, F_LEN * 0.1 / pp[2]), 0, 2 * math.pi)
                    ctx.set_source_rgba(0.85, 0.95, 1, 0.8 * (1 - back / 12))
                    ctx.fill()
    # name tags above the cars
    for c in cars:
        x, y, a = c["rec"][fi][:3]
        pp = cam.proj((x, y, 3.0))
        if pp and pp[2] < 90:
            se.draw_text(ctx, c["nick"].upper(), pp[0], pp[1] - 18, 34, fill=c["color"], stroke=(1, 1, 1), sw=7)
            ctx.move_to(pp[0] - 12, pp[1] + 4)
            ctx.line_to(pp[0] + 12, pp[1] + 4)
            ctx.line_to(pp[0], pp[1] + 20)
            ctx.close_path()
            ctx.set_source_rgb(*c["color"])
            ctx.fill()


def draw_hud(ctx, cars, fi, track):
    order = sorted(cars, key=lambda c: (c["finish_fi"] if c["finish_fi"] is not None and c["finish_fi"] <= fi
                                        else 1e9, -c["rec"][fi][3]))
    se.draw_text(ctx, "MEGAWHEEL RACE!", W / 2, 150, 92, fill=(1, 0.86, 0.12))
    for k, c in enumerate(order):
        y = 260 + k * 74
        se.rrect(ctx, 30, y - 30, 330, 62, 16)
        ctx.set_source_rgba(0.05, 0.05, 0.15, 0.7)
        ctx.fill()
        se.draw_text(ctx, f"{k + 1}", 70, y + 1, 44, fill=(1, 0.86, 0.12))
        ctx.arc(120, y, 14, 0, 2 * math.pi)
        ctx.set_source_rgb(*c["color"])
        ctx.fill()
        se.draw_text(ctx, c["nick"].upper(), 235, y + 1, 38, fill=(1, 1, 1), max_w=190)
    lead = max(c["rec"][fi][3] for c in cars)
    frac = min(1.0, lead / track.finish_s)
    se.rrect(ctx, 400, 240, 640, 22, 11)
    ctx.set_source_rgba(0.05, 0.05, 0.15, 0.6)
    ctx.fill()
    for c in cars:
        fx = 400 + 640 * min(1.0, c["rec"][fi][3] / track.finish_s)
        ctx.arc(fx, 251, 13, 0, 2 * math.pi)
        ctx.set_source_rgb(*c["color"])
        ctx.fill_preserve()
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(3)
        ctx.stroke()
    se.draw_text(ctx, f"{int(frac * 100)}%", 1000, 300, 40, fill=(1, 1, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--seconds", type=float, default=14.0)
    ap.add_argument("--out", default="/root/video-engine/work/topdown/proto.mp4")
    a = ap.parse_args()
    se.load_cast()
    se.detect_font()
    track = Track(a.seed)
    cars, skids, splash = simulate(track, a.seconds, a.seed)
    for c in cars:
        v = se.VEHICLES[c["key"]]
        c["nick"], c["color"] = v["nick"], v["color"]
        c["finish_fi"] = int(c["finish"] * FPS) if c["finish"] is not None else None
    spins = sum(1 for c in cars if c["spin"] is not None)
    print(f"[race3d] track {track.length:.0f} m, puddles {len(track.puddles)}, spins {spins}, "
          f"finish {[round(c['finish'], 1) if c['finish'] else None for c in cars]}", flush=True)
    rng = np.random.default_rng(a.seed + 77)
    trees = []
    for i in range(0, track.n, 18):
        for side in (1, -1):
            if rng.random() < 0.8:
                d = side * (TRACK_W / 2 + float(rng.uniform(5, 16)))
                trees.append((*track.point(i * STEP, d), float(rng.uniform(1.6, 2.6))))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    nfr = len(cars[0]["rec"])
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                           "-crf", "20", a.out], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    cam_s, cam_yaw = None, None
    for fi in range(nfr):
        t = fi / FPS
        lead = sorted(cars, key=lambda c: -c["rec"][fi][3])
        target_s = 0.6 * lead[0]["rec"][fi][3] + 0.4 * np.mean([c["rec"][fi][3] for c in cars])
        cam_s = target_s if cam_s is None else cam_s + (target_s - cam_s) * 0.15
        yaw_goal = float(np.mean(np.unwrap(track.t[int(cam_s / STEP):int(cam_s / STEP) + 30, 2]))) \
            if int(cam_s / STEP) + 30 < track.n else track.t[-1, 2]
        cam_yaw = yaw_goal if cam_yaw is None else cam_yaw + ((yaw_goal - cam_yaw + math.pi) % (2 * math.pi)
                                                              - math.pi) * 0.08
        px, py = track.point(cam_s, 0)
        cam = Cam(px, py, cam_yaw)
        draw_scene(ctx, track, cars, skids, splash, trees, fi, t, cam)
        draw_hud(ctx, cars, fi, track)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
        if fi % int(FPS * 2) == 0:
            surf.write_to_png(os.path.join(os.path.dirname(a.out), f"frame_{fi:04d}.png"))
    ff.stdin.close()
    ff.wait()
    print(f"[race3d] wrote {a.out} ({nfr} frames)", flush=True)


if __name__ == "__main__":
    main()
