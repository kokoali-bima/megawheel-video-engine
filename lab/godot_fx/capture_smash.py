"""LAB (not production): render a normal smash25d preview and capture FX cues with exact screen positions.

Production code is untouched: we import smash25d and wrap its draw functions at runtime, reading the cairo
transform (world -> screen) the engine uses on every frame.

  venv/bin/python lab/godot_fx/capture_smash.py --seed 777 --name LAB_SMASH_777 [--arena lava]
Outputs: work/lanes25d/previews/<name>/<name>.mp4 (the normal video) + /root/lab/fx/<name>/cues.json
cues.json: {"fps":30, "frames": N, "fx": [{"f": frame, "type": "hit|wreck|ringout|missile|kraggor|crack|ufo",
            "x": px, "y": px, "s": px_per_metre, "key": vehicle, "flip": bool, "power": 0..1}, ...]}
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in ("generators/physics_2d", "generators/lanes25d", "generators/voice", "generators/publishing"):
    sys.path.insert(0, os.path.join(ROOT, p))
import smash25d as SM  # noqa: E402

name = sys.argv[sys.argv.index("--name") + 1]
OUT = f"/root/lab/fx/{name}"
os.makedirs(OUT, exist_ok=True)
STATE = {"f": -1, "t": None, "prev_t": None, "m": None, "camx": 0.0, "fx": [], "seen": set()}


def to_screen(x, z, h=0.0):
    """world (x, z, height) -> final screen pixel using the frame's cairo matrix."""
    sx, gy = SM.pxy(x, z, STATE["camx"])
    gy -= h * SM.k_of(z)
    return STATE["m"].transform_point(sx, gy)


def scale_px(z):
    return SM.k_of(z) * STATE["m"].xx                              # metres -> screen pixels (zoom included)


def crossed(et):
    """event time et happens during this frame (also again during the slow replay)."""
    p, t = STATE["prev_t"], STATE["t"]
    return p is not None and p < et <= t


def add(typ, x, z, h=0.0, **kw):
    X, Y = to_screen(x, z, h)
    STATE["fx"].append(dict(f=STATE["f"], type=typ, x=round(X, 1), y=round(Y, 1), s=round(scale_px(z), 2), **kw))


_arena = SM.draw_arena


def draw_arena(ctx, camx, t, flash):
    STATE["f"] += 1
    STATE["prev_t"] = STATE["t"] if STATE["t"] is not None and STATE["t"] <= t else t - 1e-6
    STATE["t"], STATE["m"], STATE["camx"] = t, ctx.get_matrix(), camx
    for ch in SM.chaos_live(t):                                   # chaos impacts
        if crossed(ch["T"]):
            add(ch["type"], ch["tx"], ch["tz"], power=1.0)
    return _arena(ctx, camx, t, flash)


_impact = SM.draw_impact


def draw_impact(ctx, ev, t, camx):
    _, et, x, z, strength, *_ = ev
    if STATE["m"] is not None and crossed(et):
        add("hit", x, z, h=1.0, power=round(float(strength), 2))
    return _impact(ctx, ev, t, camx)


_out = SM.draw_out_fx


def draw_out_fx(ctx, c, t, camx):
    if c["out"] is not None and STATE["m"] is not None and crossed(c["out"]):
        st = SM.R.state(c, t)
        add("wreck" if c["out_kind"] == "wreck" else "ringout", st[0], st[1], h=0.0, key=c["key"],
            flip=bool(abs(st[3]) > 1.57), power=1.0)
    return _out(ctx, c, t, camx)


SM.draw_arena, SM.draw_impact, SM.draw_out_fx = draw_arena, draw_impact, draw_out_fx
_main_ff = None


def save():
    with open(f"{OUT}/cues.json", "w") as fh:
        json.dump(dict(fps=SM.FPS, frames=STATE["f"] + 1, fx=STATE["fx"]), fh, indent=0)
    print(f"[lab-capture] {len(STATE['fx'])} FX cues over {STATE['f'] + 1} frames -> {OUT}/cues.json", flush=True)


import atexit  # noqa: E402
atexit.register(save)
sys.argv = [sys.argv[0]] + [a for a in sys.argv[1:]] + ["--preview-only"]
SM.main()
