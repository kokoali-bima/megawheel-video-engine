"""LAB — pilot C (user 2026-10-05): a story scene with a Godot 3D world behind the ORIGINAL story25d characters.
story25d runs its normal render; only the world layer is taken out (sky, ground, road, buildings, trees, street lamps,
footprints, fog, headlight beams, Kraggor's eyes). Everything the characters are made of stays exactly as aired:
cars, faces, mouths, tears, subtitles, captions, letterbox (lesson 3-4 Oct: never re-draw the characters in 3D).

Writes to <out>/:
  overlay.mov   characters + text layer with alpha (night tint applied to the character pixels only)
  frames.json   per frame: shot, t, camx, the cairo camera matrix (zoom / pan / dutch / handheld / push), actors
                (x, z, facing, size, headlight flicker), Kraggor eyes in screen space
  scene.json    props (street lamps + off times, footprints), fog, projection constants, theme
  audio.wav     the scene's own audio (voices, cue-library score, effects)
  venv/bin/python lab/godot_story/export_story.py --episode S01E02_who_is_kraggor --scene 1 --out /root/lab/gs/s1
Production code is imported read-only; nothing in production imports lab/."""
import argparse
import json
import os
import shutil
import subprocess
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "generators", "story"))
import story25d as ST  # noqa: E402

se = ST.se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--scene", type=int, required=True)
    ap.add_argument("--aspect", default="h")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "sprites"), exist_ok=True)   # modal_godot packs this folder (unused here)
    frames, cur = [], {}

    def no_world(ctx, loc, camx, t, after_sky=None):               # draw_set: record the camera, draw nothing
        m = ctx.get_matrix()
        cur.clear()
        cur.update(t=round(t, 4), camx=round(camx, 4), m=[round(v, 6) for v in m], actors=[], eyes=None, kfar=None)
        frames.append(cur.copy())
        cur["i"] = len(frames) - 1
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.identity_matrix()
        ctx.paint()
        ctx.restore()
        if after_sky:                                              # v6 bug: never called -> far Kraggor not recorded
            after_sky()
    ST.draw_set = no_world

    def beam(ctx, act, t, camx, flicker=False):                    # headlights -> real 3D spot lights in Godot
        veh = se.VEHICLES[act["key"]]
        frames[cur["i"]]["actors"].append([act["id"], round(act["x"], 4), round(act["z"], 4), act["face"],
                                           round(act["h"], 4), act["small"], veh["body"][0], veh["body"][1],
                                           veh["wheel_r"], bool(flicker)])
    ST.draw_beam = beam

    real_eyes = ST.glow_eyes

    def eyes(ctx, t, spec):                                        # Kraggor (real head silhouette + eyes) stays the
        frames[cur["i"]]["eyes"] = dict(spec)                      # cairo drawing (same design everywhere); Godot only
        real_eyes(ctx, t, spec)                                    # adds the eyes' glow in the fog
    ST.glow_eyes = eyes
    def kfar(ctx, t, u, spec, camx):                               # far Kraggor -> a sprite of his real drawing
        frames[cur["i"]]["kfar"] = dict(spec, u=round(u, 3))       # standing in the Godot city (between the rows)
    ST.kraggor_far = kfar
    for name in ("draw_props_layer", "draw_streetlamps", "draw_footprints", "draw_fog", "draw_lamp", "draw_hill"):
        setattr(ST, name, lambda *x, **k: None)

    def night_tint(ctx, t):                                        # the aired night tint, on character pixels only
        if se.THEME.get("time") != "night":
            return
        ctx.save()
        ctx.identity_matrix()
        ctx.set_operator(cairo.OPERATOR_ATOP)
        ctx.rectangle(0, 0, ST.W, ST.H)
        ctx.set_source_rgba(0.03, 0.05, 0.16, 0.38)
        ctx.fill()
        ctx.restore()
    se.draw_weather = night_tint

    ov = os.path.join(a.out, "overlay.mov")
    real_popen, real_run = subprocess.Popen, subprocess.run

    class SP:                                                      # the scene's video writer -> alpha overlay
        PIPE = subprocess.PIPE

        @staticmethod
        def Popen(cmd, **kw):
            if "rawvideo" in cmd:
                silent = cmd[-1]
                open(silent, "wb").close()                        # story25d removes it afterwards
                w, h = cmd[cmd.index("-s") + 1].split("x")
                cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{w}x{h}",
                       "-r", str(ST.FPS), "-i", "-", "-c:v", "qtrle", ov]
            return real_popen(cmd, **kw)

        @staticmethod
        def run(cmd, **kw):
            if "-c:v" in cmd and "copy" in cmd and any(str(x).endswith(".wav") for x in cmd):
                wav = next(str(x) for x in cmd if str(x).endswith(".wav"))
                shutil.copy(wav, os.path.join(a.out, "audio.wav"))  # the final mux: we compose later
                return subprocess.CompletedProcess(cmd, 0)
            return real_run(cmd, **kw)
    ST.subprocess = SP
    ST.render_scene(a.episode, a.scene, a.aspect)

    with open(os.path.join(ROOT, "stories", a.episode, f"scene_{a.scene:02d}.json")) as fh:
        scene = json.load(fh)
    kmeta = None
    spec = next((f["kfar"] for f in frames if f.get("kfar")), None)
    if spec:                                                       # one PNG of the whole Kraggor, almost black
        x0, y0, w, h = ST.kraggor_ext()
        pad, spx = 24, 1400.0 / h
        iw, ih = int(w * spx + 2 * pad), int(h * spx + 2 * pad)
        img = cairo.ImageSurface(cairo.FORMAT_ARGB32, iw, ih)
        c = cairo.Context(img)
        ST.kraggor_head(c, 3.0, dict(mode="calm", sx=(pad - x0 * spx) / ST.W, scale=spx * 1080.0 / ST.H),
                        stands_top=pad - y0 * spx)
        c.set_operator(cairo.OPERATOR_ATOP)
        c.rectangle(0, 0, iw, ih)
        c.set_source_rgb(*spec.get("tint", (0.025, 0.03, 0.055)))
        c.fill()
        img.write_to_png(os.path.join(a.out, "sprites", "kraggor_far.png"))
        kmeta = dict(ext=[x0, y0, w, h], pad=pad, spx=spx, eyes=ST.KR_EYE_UNIT)
    rows = [[i // 450, f] for i, f in enumerate(frames)]           # [part, frame]: modal_godot renders parts in parallel
    json.dump(dict(fps=ST.FPS, frames=rows), open(os.path.join(a.out, "frames.json"), "w"))
    json.dump(dict(scene=scene, theme=se.THEME, W=ST.W, H=ST.H, F=ST.F_PERSP, D0=ST.D0, DZ=ST.DZ, Y_H=ST.Y_H,
                   CAM_H=ST.CAM_H, CX=ST.CX, kfar=kmeta), open(os.path.join(a.out, "scene.json"), "w"))
    print(f"[story3d] {len(frames)} frames exported -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
