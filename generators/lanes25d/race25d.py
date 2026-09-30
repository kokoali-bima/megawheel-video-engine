#!/usr/bin/env python3
"""MegaWheel Arena — 2.5D "paper cutout" race (PROTOTYPE, style test).

The characters are drawn by the SAME functions as the 2D episodes (sim_engine.draw_body / draw_face /
draw_wheel, moods, themes, speed lines, splash, READY-GO, confetti), so they look exactly like the 2D cast.
Depth comes from lanes: a side-on road seen slightly from above; far lanes are smaller and higher on screen,
lane dashes / props move with parallax. A car can hydroplane ACROSS lanes while spinning (yaw squash).

Usage (cd /root/video-engine):
  ./venv/bin/python generators/lanes25d/race25d.py --out work/lanes25d/proto.mp4
Render: VM CPU (cairo), free. No audio yet (style test).
"""
import argparse
import math
import os
import subprocess
import sys

import cairo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "physics_2d"))
import sim_engine as se  # noqa: E402

W, H, FPS = se.W, se.H, 30
F_PERSP, D0, LANE_D = 9000.0, 100.0, 25.0        # k(z) = F / (D0 + z*LANE_D): front lane 90 px/m, lane 3 ≈ 51
Y_H, CAM_H = 640.0, 13.0                         # vanishing line and camera height: ground_y = Y_H + CAM_H*k
PUD_X, RAMP_X, FIN_X = 100.0, 172.0, 252.0       # puddle (lane 1), ramp (lane 3), finish line
SECONDS = 13.0

# cast: key, lane, cruise speed (m/s)
RACERS = [("sports", 0, 23.4), ("police", 1, 23.0), ("taxi", 2, 23.1), ("monster", 3, 21.6)]


def k_of(z):
    return F_PERSP / (D0 + z * LANE_D)


def ground_y(z):
    return Y_H + CAM_H * k_of(z)


def ease_out(p):
    return 1 - (1 - p) ** 2.2


# ------------------------------------------------------------------ scripted race (120 Hz kinematics)
def simulate():
    dt, n = 1 / 120, int(SECONDS * 120)
    cars = []
    for key, lane, v in RACERS:
        cars.append(dict(key=key, lane=lane, v0=v, x=4.0 - lane * 1.2, z=float(lane), h=0.0, vh=0.0, yaw=0.0,
                         pitch=0.0, v=0.0, spin_t=None, jump_t=None, land_t=None, bump_t=None, finish=None,
                         rec=[]))
    events = []
    for i in range(n):
        t = i * dt
        for c in cars:
            go = min(1.0, t / 1.6)                               # launch after GO
            target = c["v0"] * (1 + 0.02 * math.sin(t * 0.9 + c["lane"]))
            if c["spin_t"] is not None:
                target *= 0.55 + 0.45 * min(1.0, max(0.0, (t - c["spin_t"] - 1.2) / 2.0))
            if c["land_t"] is not None and t - c["land_t"] < 2.5:
                target *= 1.12                                   # landed with a boost
            if c["finish"] is not None:
                target = max(4.0, c["v"] * 0.985)
            c["v"] += (target * go - c["v"]) * 0.03
            c["x"] += c["v"] * dt
            # hydroplane in the puddle: spin 2 turns, slide one lane towards the camera
            if c["lane"] == 1 and c["spin_t"] is None and PUD_X - 2 < c["x"] < PUD_X + 5:
                c["spin_t"] = t
                events.append(("splash", t, c["x"], 1.0))
            if c["spin_t"] is not None:
                p = min(1.0, (t - c["spin_t"]) / 1.4)
                c["yaw"] = 4 * math.pi * ease_out(p)
                c["z"] = 1.0 - 0.55 * ease_out(min(1.0, (t - c["spin_t"]) / 1.0))
            # ramp in lane 3: big jump
            if c["lane"] == 3 and c["jump_t"] is None and c["x"] >= RAMP_X:
                c["jump_t"], c["vh"] = t, 9.2
            if c["jump_t"] is not None and c["land_t"] is None:
                c["vh"] -= 9.81 * dt
                c["h"] = max(0.0, c["h"] + c["vh"] * dt)
                c["pitch"] = float(np.clip(c["vh"] * 0.035, -0.28, 0.28))
                if c["h"] == 0.0 and c["vh"] < 0:
                    c["land_t"], c["pitch"] = t, 0.0
                    events.append(("land", t, c["x"], 3.0))
            if c["finish"] is None and c["x"] >= FIN_X:
                c["finish"] = t
            if i % 4 == 0:
                c["rec"].append((c["x"], c["z"], c["h"], c["yaw"], c["pitch"], c["v"]))
        # the spinning car slides into the front lane and bumps whoever is beside it
        sp = next((c for c in cars if c["spin_t"] is not None and t - c["spin_t"] < 1.2), None)
        if sp:
            for c in cars:
                if c is not sp and c["lane"] == 0 and c["bump_t"] is None and abs(c["x"] - sp["x"]) < 5 and sp["z"] < 0.75:
                    c["bump_t"] = t
                    events.append(("bump", t, c["x"], 0.3))
        for c in cars:
            if c["bump_t"] is not None:
                a = t - c["bump_t"]
                c["z"] = c["lane"] - 0.28 * math.sin(min(math.pi, a * 2.6)) if a < 1.3 else float(c["lane"])
    return cars, events


# ------------------------------------------------------------------ timeline (slow-mo on the jump)
def timeline(cars):
    rocky = next(c for c in cars if c["lane"] == 3)
    jt = rocky["jump_t"]
    frames, t = [], 0.0
    while t < SECONDS - 0.05:
        frames.append(t)
        rate = 0.35 if jt is not None and jt + 0.25 < t < jt + 1.35 else 1.0
        t += rate / FPS
    return frames


def state(c, t):
    f = t * 30
    i = min(int(f), len(c["rec"]) - 2)
    a = f - i
    r0, r1 = c["rec"][i], c["rec"][i + 1]
    return tuple(r0[j] * (1 - a) + r1[j] * a for j in range(6))


def mood_of(c, t, x):
    if c["finish"] is not None and t > c["finish"] and c.get("place") == 1:
        return "happy"
    if c["spin_t"] is not None and 0 <= t - c["spin_t"] < 1.4:
        return "whoa"
    if c["spin_t"] is not None and 1.4 <= t - c["spin_t"] < 3.5:
        return "dizzy"
    if c["jump_t"] is not None and c["land_t"] is not None and c["jump_t"] <= t < c["land_t"]:
        return "whoa"
    if c["bump_t"] is not None and 0 <= t - c["bump_t"] < 1.2:
        return "scared"
    if (c["lane"] == 1 and 0 < PUD_X - x < 22) or (c["lane"] == 3 and 0 < RAMP_X - x < 22):
        return "scared"
    return "normal"


BUBBLES = {"spin": "WHOA!", "bump": "HEY!", "jump": "YEEHAW!", "win": "YEAH!"}


# ------------------------------------------------------------------ drawing
def draw_ground(ctx, camx):
    gc = se.lit(se.th_loc()["ground"])
    g = cairo.LinearGradient(0, ground_y(4.6), 0, H)
    g.add_color_stop_rgb(0, *se.shade(gc, 0.85))
    g.add_color_stop_rgb(1, *gc)
    ctx.rectangle(0, ground_y(4.6), W, H)
    ctx.set_source(g)
    ctx.fill()
    top, bot = ground_y(3.55), ground_y(-0.55)                 # road band (lanes -0.5 .. 3.5)
    rg = cairo.LinearGradient(0, top, 0, bot)
    rg.add_color_stop_rgb(0, *se.lit((0.3, 0.3, 0.34)))
    rg.add_color_stop_rgb(1, *se.lit((0.23, 0.23, 0.27)))
    ctx.rectangle(0, top, W, bot - top)
    ctx.set_source(rg)
    ctx.fill()
    for z0, z1 in ((-0.55, -0.72), (3.55, 3.7)):               # kerbs, red/white every 2 m (parallax per edge)
        k0, k1 = k_of(z0), k_of(z1)
        y0, y1 = ground_y(z0), ground_y(z1)
        x = math.floor((camx - 540 / k1) / 2) * 2
        while (x - camx) * k1 + 540 < W + 200:
            poly = [((x - camx) * k0 + 540, y0), ((x + 2 - camx) * k0 + 540, y0),
                    ((x + 2 - camx) * k1 + 540, y1), ((x - camx) * k1 + 540, y1)]
            se.poly(ctx, poly)
            ctx.set_source_rgb(*((0.85, 0.1, 0.1) if int(x / 2) % 2 else (0.96, 0.96, 0.96)))
            ctx.fill()
            x += 2
    for zl in (0.5, 1.5, 2.5):                                  # lane dashes: 1.6 m every 4 m
        k, y = k_of(zl), ground_y(zl)
        x = math.floor((camx - 540 / k) / 4) * 4
        while (x - camx) * k + 540 < W + 100:
            ctx.rectangle((x - camx) * k + 540, y - k * 0.06, 1.6 * k, k * 0.12)
            ctx.set_source_rgba(1, 1, 1, 0.9)
            ctx.fill()
            x += 4
    for zl, k in ((3.5, k_of(3.5)), (-0.5, k_of(-0.5))):        # finish line across the road
        pass
    kf0, kf1 = k_of(-0.55), k_of(3.55)
    for row in range(8):
        za, zb = -0.55 + row * 0.5, -0.05 + row * 0.5
        for col in range(2):
            xa = FIN_X + col * 0.9
            q = [((xa - camx) * k_of(za) + 540, ground_y(za)), ((xa + 0.9 - camx) * k_of(za) + 540, ground_y(za)),
                 ((xa + 0.9 - camx) * k_of(zb) + 540, ground_y(zb)), ((xa - camx) * k_of(zb) + 540, ground_y(zb))]
            se.poly(ctx, q)
            ctx.set_source_rgb(*((0.05, 0.05, 0.05) if (row + col) % 2 else (1, 1, 1)))
            ctx.fill()


def draw_props(ctx, camx, z, seed, back=True):
    """Trees / bushes on a depth row (parallax)."""
    k, y = k_of(z), ground_y(z)
    rng = np.random.default_rng(seed)
    xs = np.cumsum(rng.uniform(9, 20, 60)) - 30
    for i, x in enumerate(xs):
        sx = (x - camx) * k + 540
        if -300 < sx < W + 300:
            s = 1.0 + 0.3 * math.sin(i * 1.7)
            if back:
                ctx.rectangle(sx - 0.25 * k, y - 2.6 * k * s, 0.5 * k, 2.6 * k * s)
                ctx.set_source_rgb(*se.lit((0.4, 0.26, 0.14)))
                ctx.fill()
                ctx.arc(sx, y - 3.4 * k * s, 1.7 * k * s, 0, 2 * math.pi)
                ctx.set_source_rgb(*se.lit((0.18, 0.5, 0.22)))
                ctx.fill()
                ctx.arc(sx - 0.5 * k * s, y - 3.8 * k * s, 1.0 * k * s, 0, 2 * math.pi)
                ctx.set_source_rgb(*se.lit((0.26, 0.62, 0.3)))
                ctx.fill()
            else:
                for j in range(3):
                    ctx.arc(sx + (j - 1) * 0.9 * k, y - 0.4 * k, (0.8 + 0.2 * j) * k * 0.6, math.pi, 2 * math.pi)
                    ctx.set_source_rgb(*se.lit((0.2, 0.55, 0.22)))
                    ctx.fill()


def draw_puddle(ctx, camx, t):
    k, y = k_of(1.0), ground_y(1.0)
    sx = (PUD_X + 2.5 - camx) * k + 540
    if -600 < sx < W + 600:
        ctx.save()
        ctx.translate(sx, y)
        ctx.scale(4.8 * k, 0.55 * k)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(*se.lit((0.3, 0.6, 1.0)), 0.9)
        ctx.fill()
        for j in range(4):
            ox = (j - 1.5) * 1.8 * k + 8 * math.sin(t * 3 + j)
            ctx.move_to(sx + ox - 0.5 * k, y - 0.1 * k)
            ctx.line_to(sx + ox + 0.5 * k, y - 0.1 * k)
            ctx.set_source_rgba(1, 1, 1, 0.7)
            ctx.set_line_width(max(2, k * 0.06))
            ctx.stroke()


def draw_ramp(ctx, camx):
    k, y = k_of(3.0), ground_y(3.0)
    x0 = (RAMP_X - 5.5 - camx) * k + 540
    x1 = (RAMP_X - camx) * k + 540
    if -400 < x1 < W + 400:
        se.poly(ctx, [(x0, y), (x1, y), (x1, y - 1.3 * k)])
        ctx.set_source_rgb(*se.lit((0.85, 0.55, 0.25)))
        ctx.fill_preserve()
        ctx.set_source_rgb(0.3, 0.18, 0.08)
        ctx.set_line_width(3)
        ctx.stroke()


def draw_car(ctx, c, t, camx):
    x, z, h, yaw, pitch, v = state(c, t)
    vk = c["key"]
    veh = se.VEHICLES[vk]
    k, gy = k_of(z), ground_y(z)
    sx = (x - camx) * k + 540
    if not -500 < sx < W + 500:
        return None
    bw, bh = veh["body"]
    r, travel = veh["wheel_r"], veh["travel"]
    ride = r + 0.6 * travel + bh / 2
    a = 0.3 * max(0.0, 1 - h / 5)                                 # shadow shrinks while airborne
    ctx.save()
    ctx.translate(sx, gy)
    ctx.scale(bw * 0.58 * k * (1 + h * 0.06), 0.16 * k)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(0, 0, 0, a)
    ctx.fill()
    ys = se.yaw_scale(yaw)
    land = c["land_t"] is not None and 0 <= t - c["land_t"] < 0.3
    squash = 1 - 0.12 * math.sin(math.pi * (t - c["land_t"]) / 0.3) if land else 1.0
    ctx.save()
    ctx.translate(sx, gy - h * k)
    ctx.scale(k, -k)
    ctx.rotate(pitch)
    ctx.scale(ys, squash)
    wheel_ang = -x / r
    ctx.set_source_rgb(0.3, 0.3, 0.34)
    ctx.set_line_width(0.14)
    for lx in veh["wheel_x"]:
        ctx.move_to(lx, ride - bh / 2)
        ctx.line_to(lx, r)
        ctx.stroke()
    for lx in veh["wheel_x"]:
        se.draw_wheel(ctx, lx, r, wheel_ang, r, vk.startswith("monster"), sx=max(0.3, abs(ys)))
    ctx.translate(0, ride + 0.03 * math.sin(t * 18 + c["lane"]) * min(1.0, v / 20))
    se.draw_body(ctx, vk, veh, False, t)
    se.draw_face(ctx, vk, mood_of(c, t, x), t)
    ctx.restore()
    return sx, gy - (h + ride + bh) * k, k


def bubble(ctx, text, sx, sy, age, k):
    if not 0 <= age < 1.1:
        return
    sc = se.ease_out_back(min(1.0, age / 0.25)) * min(1.0, (1.1 - age) / 0.2)
    ctx.save()
    ctx.translate(sx, sy - 110 * k / 70)
    ctx.scale(sc * k / 70, sc * k / 70)
    se.rrect(ctx, -150, -60, 300, 110, 40)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill_preserve()
    ctx.set_source_rgb(0.07, 0.07, 0.2)
    ctx.set_line_width(8)
    ctx.stroke()
    se.poly(ctx, [(-30, 48), (10, 48), (-40, 100)])
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    se.draw_text(ctx, text, 0, -5, 62, fill=(0.9, 0.12, 0.12), stroke=(1, 1, 1), sw=4)
    ctx.restore()


def draw_hud(ctx, cars, t):
    se.draw_text(ctx, "MEGAWHEEL RACE!", W / 2, 150, 92, fill=(1, 0.86, 0.12))
    order = sorted(cars, key=lambda c: (c["finish"] if c["finish"] is not None and c["finish"] <= t else 1e9,
                                        -state(c, t)[0]))
    for i, c in enumerate(order):
        y = 260 + i * 74
        se.rrect(ctx, 30, y - 30, 330, 62, 16)
        ctx.set_source_rgba(0.05, 0.05, 0.15, 0.7)
        ctx.fill()
        se.draw_text(ctx, str(i + 1), 70, y + 1, 44, fill=(1, 0.86, 0.12))
        ctx.arc(120, y, 14, 0, 2 * math.pi)
        ctx.set_source_rgb(*se.VEHICLES[c["key"]]["color"])
        ctx.fill()
        se.draw_text(ctx, se.VEHICLES[c["key"]]["nick"].upper(), 235, y + 1, 38, max_w=190)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/root/video-engine/work/lanes25d/proto.mp4")
    a = ap.parse_args()
    se.load_cast()
    se.detect_font()
    se.make_theme(1, force=dict(time="noon", weather="clear", location="countryside"))
    cars, events = simulate()
    for place, c in enumerate(sorted(cars, key=lambda c: c["finish"] if c["finish"] else 1e9), start=1):
        c["place"] = place
    frames = timeline(cars)
    winner = min(cars, key=lambda c: c["finish"] or 1e9)
    print(f"[25d] {len(frames)} frames, finish order: "
          f"{[se.VEHICLES[c['key']]['nick'] for c in sorted(cars, key=lambda c: c['place'])]}", flush=True)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", a.out],
                          stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    camx, zoom = None, 1.0
    for fi, t in enumerate(frames):
        st = {id(c): state(c, t) for c in cars}
        focus = None                                              # camera: follow the drama, else the leaders
        for c in cars:
            if c["spin_t"] is not None and -0.6 < t - c["spin_t"] < 2.0:
                focus = c
            if c["jump_t"] is not None and -0.5 < t - c["jump_t"] < 2.2:
                focus = c
        xs = [st[id(c)][0] for c in cars]
        mid = (max(xs) + min(xs)) / 2
        target = 0.55 * (st[id(focus)][0] + 2) + 0.45 * mid if focus else mid + 1.5
        spread = max(xs) - min(xs) + 9.0
        fit = float(np.clip(W * 0.92 / (spread * k_of(0.0)), 0.62, 1.12))
        camx = target if camx is None else camx + (target - camx) * 0.12
        punch = 1.0
        for kind, et, ex, ez in events:                           # zoom punch + shake on impacts
            if kind in ("land", "bump", "splash") and 0 <= t - et < 0.35:
                punch = max(punch, 1 + 0.08 * math.sin(math.pi * (t - et) / 0.35))
        zoom += (min(fit, 1.08 if focus else 1.0) * punch - zoom) * 0.12
        shx = shy = 0.0
        for kind, et, ex, ez in events:
            if kind in ("land", "bump") and 0 <= t - et < 0.4:
                amp = 16 * (1 - (t - et) / 0.4)
                shx, shy = amp * math.sin(t * 90), amp * math.cos(t * 70)
        se.draw_sky(ctx, camx * 0.35, 0.0, 1.0)
        ctx.save()
        ctx.translate(540 + shx, 1520 + shy)                      # world layer: zoom around the action
        ctx.scale(zoom, zoom)
        ctx.translate(-540, -1520)
        draw_props(ctx, camx, 5.2, 11, back=True)
        draw_props(ctx, camx, 4.3, 12, back=True)
        draw_ground(ctx, camx)
        draw_puddle(ctx, camx, t)
        draw_ramp(ctx, camx)
        heads = {}
        for c in sorted(cars, key=lambda c: -st[id(c)][1]):       # far lanes first
            heads[id(c)] = draw_car(ctx, c, t, camx)
        for kind, et, ex, ez in events:                           # splash on the puddle / dust on landing
            age = t - et
            if kind == "splash" and 0 <= age < 1.6:
                k, y = k_of(1.0), ground_y(1.0)
                ctx.save()
                ctx.translate((ex - camx) * k + 540, y)
                ctx.scale(k, -k)
                se.draw_water_splash(ctx, dict(x=0.0, y=0.0, speed=22.0, big=False), age)
                ctx.restore()
            if kind == "land" and 0 <= age < 0.8:
                k, y = k_of(ez), ground_y(ez)
                for j in range(8):
                    px = (ex - camx) * k + 540 + (j - 3.5) * 0.7 * k * (1 + age * 2)
                    ctx.arc(px, y - age * 0.8 * k, (0.4 + age) * k * 0.6, 0, 2 * math.pi)
                    ctx.set_source_rgba(0.75, 0.68, 0.55, 0.6 * (1 - age / 0.8))
                    ctx.fill()
        ctx.restore()
        lead_v = max(st[id(c)][5] for c in cars)
        se.draw_speed_lines(ctx, lead_v, fi / FPS)
        for c in cars:                                            # speech bubbles
            hd = heads.get(id(c))
            if not hd:
                continue
            for key, t0 in (("spin", c["spin_t"]), ("bump", c["bump_t"]), ("jump", c["jump_t"])):
                if t0 is not None:
                    bubble(ctx, BUBBLES[key], hd[0], hd[1], t - t0 - 0.1, hd[2] * zoom)
            if c is winner and c["finish"] is not None:
                bubble(ctx, BUBBLES["win"], hd[0], hd[1], t - c["finish"] - 0.3, hd[2] * zoom)
        draw_hud(ctx, cars, t)
        se.draw_ready_go(ctx, t)
        if winner["finish"] is not None and t >= winner["finish"]:
            age = t - winner["finish"]
            se.draw_confetti(ctx, age)
            s = se.ease_out_back(min(1.0, age / 0.4))
            ctx.save()
            ctx.translate(540, 760)
            ctx.scale(s, s)
            se.draw_text(ctx, f"{se.VEHICLES[winner['key']]['nick'].upper()} WINS!", 0, 0, 120, fill=(1, 0.86, 0.12))
            ctx.restore()
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
        if fi % 45 == 0:
            surf.write_to_png(os.path.join(os.path.dirname(a.out), f"frame_{fi:04d}.png"))
    ff.stdin.close()
    ff.wait()
    print(f"[25d] wrote {a.out}", flush=True)


if __name__ == "__main__":
    main()
