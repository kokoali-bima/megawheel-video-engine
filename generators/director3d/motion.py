#!/usr/bin/env python3
"""director3d step 1 — race simulation -> smooth 30 fps motion data for the Blender renderer.

Physics comes from generators/topdown/race3d.py (flat tyre-grip model: drifts, hydroplane spins on puddles).
This adds what makes motion feel alive but costs nothing at render time:
  wheel spin from distance travelled, body roll in corners, nose dip/squat under braking/throttle,
  a small speed-dependent bounce, all through a damped spring (weight, no jitter),
  and spring-smoothed follow cameras for a horizontal (16:9) and a vertical (9:16) cut of the same action.

Usage (cd /root/video-engine):
  ./venv/bin/python generators/director3d/motion.py --seed 1 --seconds 15 --out work/director3d/demo/motion.json
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "topdown"))
import race3d as rd  # noqa: E402

FPS = rd.FPS
CAST_OF = {"sports": "zippy", "f1": "nitro", "taxi": "tilly", "police": "siren"}   # race3d key -> cast id
WHEEL_R = {"zippy": 0.36, "nitro": 0.36, "tilly": 0.38, "siren": 0.38}


def spring(x, stiffness=0.18, damping=0.72):
    """Damped spring follower: smooth, slightly lagging (feels like mass) — never overshoots much."""
    y, v, out = float(x[0]), 0.0, np.empty(len(x))
    for i, target in enumerate(x):
        v = v * damping + (target - y) * stiffness
        y += v
        out[i] = y
    return out


def ema(x, k):
    y, out = x[0], np.empty_like(np.asarray(x, dtype=float))
    for i, v in enumerate(x):
        y = y + (v - y) * k
        out[i] = y
    return out


def car_motion(c):
    rec = np.array([r[:5] for r in c["rec"]], dtype=float)          # x, y, angle, s, speed
    x, y, s, speed = rec[:, 0], rec[:, 1], rec[:, 3], rec[:, 4]
    yaw = np.unwrap(rec[:, 2])
    cid = CAST_OF[c["key"]]
    yaw_rate = np.gradient(yaw) * FPS
    a_lat = speed * yaw_rate                                        # centripetal acceleration (m/s^2)
    a_long = np.gradient(ema(speed, 0.3)) * FPS
    roll = spring(np.clip(0.011 * a_lat, -0.11, 0.11))               # +X roll lifts the inner (left) side: lean out
    pitch = spring(np.clip(0.006 * a_long, -0.05, 0.05))             # squat on throttle, dip on brakes
    t = np.arange(len(x)) / FPS
    bounce = spring(0.012 * np.clip(speed / 25, 0, 1) * np.sin(t * 17 + len(cid)), 0.3, 0.6)
    dist = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    wheel = dist / WHEEL_R[cid]
    frames = np.stack([x, y, yaw, roll, pitch, bounce, wheel, speed], axis=1).round(4).tolist()
    return dict(id=cid, frames=frames, spin_t=c["spin"], finish_t=c["finish"])


def cameras(track, cars, n):
    """Follow cams aimed at the real centre of the pack (cars more than 30 m behind the leader are ignored,
    so a spun-out straggler does not drag the shot); spring-smoothed position, aim and heading."""
    cx, cy, hd = np.empty(n), np.empty(n), np.empty(n)
    for i in range(n):
        rec = [c["rec"][i] for c in cars]
        lead = max(r[3] for r in rec)
        pack = [r for r in rec if lead - r[3] < 30.0]
        cx[i] = float(np.mean([r[0] for r in pack]))
        cy[i] = float(np.mean([r[1] for r in pack]))
        s_mid = float(np.mean([r[3] for r in pack]))
        hd[i] = track.t[int(np.clip((s_mid + 6) / rd.STEP, 0, track.n - 1)), 2]
    cx, cy = spring(cx, 0.16, 0.72), spring(cy, 0.16, 0.72)
    hd = spring(np.unwrap(hd), 0.07, 0.78)
    out = {}
    #                 name          back  height ahead
    for name, back, height, ahead in (("horizontal", 15.0, 8.0, 3.0), ("vertical", 11.0, 14.0, 2.0)):
        f0, f1 = np.cos(hd), np.sin(hd)
        arr = np.stack([cx - f0 * back, cy - f1 * back, np.full(n, height),
                        cx + f0 * ahead, cy + f1 * ahead, np.full(n, 0.6)], axis=1)
        out[name] = arr.round(3).tolist()
    return out


def scenery(track, seed):
    rng = np.random.default_rng(seed + 77)
    trees = []
    for i in range(0, track.n, 16):
        for side in (1, -1):
            if rng.random() < 0.8:
                d = side * (rd.TRACK_W / 2 + float(rng.uniform(5, 18)))
                x, y = track.point(i * rd.STEP, d)
                trees.append([round(x, 2), round(y, 2), round(float(rng.uniform(1.4, 2.4)), 2)])
    puddles = []
    for p in track.puddles:
        ring = []
        for k in range(24):
            th = 2 * math.pi * k / 24
            s_ = (p["s0"] + p["s1"]) / 2 + (p["s1"] - p["s0"]) / 2 * math.cos(th) * (1 + 0.08 * math.sin(3 * th))
            d_ = (p["d0"] + p["d1"]) / 2 + (p["d1"] - p["d0"]) / 2 * math.sin(th) * (1 + 0.1 * math.cos(2 * th))
            ring.append([round(v, 3) for v in track.point(s_, d_)])
        puddles.append(ring)
    return trees, puddles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--seconds", type=float, default=15.0)
    ap.add_argument("--out", default="/root/video-engine/work/director3d/demo/motion.json")
    a = ap.parse_args()
    track = rd.Track(a.seed)
    cars, skids, splash = rd.simulate(track, a.seconds, a.seed)
    n = len(cars[0]["rec"])
    trees, puddles = scenery(track, a.seed)
    step = 4                                                        # centreline every 2 m is enough for the mesh
    data = dict(
        fps=FPS, frames=n, seed=a.seed,
        track=dict(points=track.t[::step].round(4).tolist(), width=rd.TRACK_W, step=rd.STEP * step,
                   finish=[round(v, 3) for v in (*track.point(track.finish_s, 0), track.t[int(track.finish_s / rd.STEP), 2])]),
        trees=trees, puddles=puddles,
        cars=[car_motion(c) for c in cars],
        cams=cameras(track, cars, n),
    )
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(data, fh, separators=(",", ":"))
    spins = [(c["id"], round(c["spin_t"], 1)) for c in data["cars"] if c["spin_t"] is not None]
    print(f"[motion] {n} frames ({a.seconds:.0f} s), track {track.length:.0f} m, {len(trees)} trees, "
          f"{len(puddles)} puddles, spins {spins} -> {a.out} ({os.path.getsize(a.out) // 1024} KB)")


if __name__ == "__main__":
    main()
