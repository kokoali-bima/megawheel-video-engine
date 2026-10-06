"""story3d (option C, user-approved 2026-10-06): one story scene = Godot 3D world + the ORIGINAL story25d characters.
This step renders the character layer: story25d runs its normal render with the world layer taken out (sky, ground,
road, buildings, trees, lamps, footprints, fog, headlight beams, far Kraggor). Everything the characters are made of
stays exactly as aired: cars, faces, mouths, tears, subtitles, captions, letterbox (never re-draw characters in 3D).

Writes to <out>/:
  overlay.mov   characters + text with alpha (night tint on character pixels only)
  frames.json   per frame: shot index, t, camx, cairo camera matrix, actors (x, z, facing, h, size, body, flicker),
                Kraggor eyes / far Kraggor spec
  scene.json    the scene, the shot table (t0, t1, cam, focus actor, moves), projection constants, theme
  audio.wav     the scene audio (voices, cue-library score, effects, ambience)
  sprites/      kraggor_far.png when a shot has kraggor_far
Runs on the VM or in a Modal container (S3D_REMOTE=1: voices MUST already be cached; lip-sync is made here with
rhubarb x86 and cached in the Modal volume; nothing degrades silently - a missing voice / mouth / font stops it).
  python generators/story3d/export_overlay.py --episode S01E02_who_is_kraggor --scene 2 --out /tmp/s3d/s02"""
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
PART = 450                                         # frames per Godot render part (parallel GPU containers)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--scene", type=int, required=True)
    ap.add_argument("--aspect", default="h")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    run(a.episode, a.scene, a.aspect, a.out)


def run(episode, scene_no, aspect, out):
    os.makedirs(os.path.join(out, "sprites"), exist_ok=True)
    frames, cur, box = [], {}, {}
    remote = os.environ.get("S3D_REMOTE") == "1"

    if remote:                                                     # quality gates: no silent fallback in the cloud
        real_prefetch = ST.announcer.prefetch

        def prefetch(items, note=""):
            items = [tuple(it) if len(it) == 4 else (*it, "arena") for it in items]
            miss = [it for it in items if not os.path.exists(ST.announcer.path(*it))]
            if miss:
                raise SystemExit(f"[story3d] STOP: {len(miss)} voice line(s) not prepared: {[m[0][:40] for m in miss]}")
            return True
        ST.announcer.prefetch = prefetch
        vc = os.environ.get("S3D_VIS_CACHE")                    # lip-sync runs here (rhubarb x86, user 2026-10-06);
        if vc:                                                     # cache in the Modal volume, seeded from the repo
            os.makedirs(vc, exist_ok=True)
            seed = os.path.join(ROOT, "work", "voice", "visemes")
            for fn in (os.listdir(seed) if os.path.isdir(seed) else []):
                if fn.endswith(".json") and not os.path.exists(os.path.join(vc, fn)):
                    shutil.copy(os.path.join(seed, fn), os.path.join(vc, fn))
            ST.VIS_CACHE = vc
        real_vis = ST.visemes

        def vis(audio, text):
            r = real_vis(audio, text)
            if not r:
                raise SystemExit(f"[story3d] STOP: lip-sync failed for: {text[:50]} (rhubarb {ST.RHUBARB})")
            return r
        ST.visemes = vis
        del real_prefetch
        real_font = se.detect_font

        def font():
            real_font()
            if se.FONT_FACE != "Luckiest Guy":
                raise SystemExit("[story3d] STOP: caption font Luckiest Guy missing in the container")
        se.detect_font = font

    real_build = ST.build

    def build(scene):                                              # keep the shot table (t0/t1) for frame records
        shots, placed, total = real_build(scene)
        box["shots"] = shots
        return shots, placed, total
    ST.build = build

    def shot_of(t):
        sh = box.get("shots") or []
        return max([i for i, s in enumerate(sh) if s["t0"] <= t] + [0])

    def no_world(ctx, loc, camx, t, after_sky=None):               # draw_set: record the camera, draw nothing
        m = ctx.get_matrix()
        cur.clear()
        cur.update(t=round(t, 4), shot=shot_of(t), camx=round(camx, 4), m=[round(v, 6) for v in m], actors=[],
                   eyes=None, kfar=None)
        frames.append(cur.copy())
        cur["i"] = len(frames) - 1
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.identity_matrix()
        ctx.paint()
        ctx.restore()
        if after_sky:                                              # far Kraggor etc. (lesson: forgetting this lost
            after_sky()                                            # the sprite silently, pilot v6)
    ST.draw_set = no_world

    flick = {}

    def beam(ctx, act, t, camx, flicker=False):                    # headlights -> real 3D spot lights in Godot
        flick[act["id"]] = bool(flicker)
    ST.draw_beam = beam

    real_actor = ST.draw_actor

    def actor(ctx, act, t, camx):                                  # every visible car, day or night
        veh = se.VEHICLES[act["key"]]
        frames[cur["i"]]["actors"].append([act["id"], round(act["x"], 4), round(act["z"], 4), act["face"],
                                           round(act["h"], 4), act["small"], veh["body"][0], veh["body"][1],
                                           veh["wheel_r"], flick.pop(act["id"], False)])
        real_actor(ctx, act, t, camx)
    ST.draw_actor = actor

    real_eyes = ST.glow_eyes

    def eyes(ctx, t, spec):                                        # Kraggor eyes in screen space: still cairo
        frames[cur["i"]]["eyes"] = dict(spec)
        real_eyes(ctx, t, spec)
    ST.glow_eyes = eyes

    def kfar(ctx, t, u, spec, camx):                               # far Kraggor -> Godot sprite of his real drawing
        frames[cur["i"]]["kfar"] = dict(spec, u=round(u, 3))
    ST.kraggor_far = kfar
    for name in ("draw_props_layer", "draw_streetlamps", "draw_footprints", "draw_fog", "draw_lamp", "draw_hill",
                 "draw_poster"):
        setattr(ST, name, lambda *x, **k: None)

    def night_tint(ctx, t):                                        # the aired night tint, on character pixels only
        if se.THEME.get("time") != "night":
            return
        loc = ST.SCENE.get("location")
        indoor = loc == "garage"                                   # lit by a warm bulb indoors, not by the moon
        tint = (0.35, 0.2, 0.05, 0.14) if indoor else (0.04, 0.09, 0.2, 0.22) if loc == "cave" else (0.03, 0.05, 0.16, 0.38)
        ctx.save()
        ctx.identity_matrix()
        ctx.set_operator(cairo.OPERATOR_ATOP)
        ctx.rectangle(0, 0, ST.W, ST.H)
        ctx.set_source_rgba(*tint)
        ctx.fill()
        ctx.restore()
    se.draw_weather = night_tint

    ov = os.path.join(out, "overlay.mov")
    real_popen, real_run = subprocess.Popen, subprocess.run

    class SP:                                                      # the scene's video writer -> alpha overlay
        PIPE = subprocess.PIPE
        CompletedProcess = subprocess.CompletedProcess

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
                shutil.copy(wav, os.path.join(out, "audio.wav"))  # the final mux happens in compose
                return subprocess.CompletedProcess(cmd, 0)
            return real_run(cmd, **kw)
    ST.subprocess = SP
    eng = json.load(open(os.path.join(HERE, "STYLE_CONTRACT.json"), encoding="utf-8"))["engine"]   # one source
    ST.CUT_RULE, ST.ISO_CAMERA = eng["cut_rule"], eng["iso_camera"]  # real 3D camera: clean cuts, no fake stretch
    mix = eng.get("mix", {})                                       # A10: dialogue is the anchor, music sits under it
    ST.MUSIC_GAIN = mix.get("music_gain", ST.MUSIC_GAIN)
    ST.DUCK_DEPTH = mix.get("duck_depth", ST.DUCK_DEPTH)
    ST.DUCK_SMOOTH = mix.get("duck_smooth_s", ST.DUCK_SMOOTH)
    ST.JCUT = eng["jcut_s"]                                        # C04: voice leads the picture across cuts
    se.TEXT_UNMIRROR = eng["text_unmirror"]                        # "SCHOOL BUS" not mirrored on a left-facing bus
    ST.STEMS = {}
    ST.sepia = lambda surf: None                                   # flashback grade is applied ONCE, on the finished
    ST.render_scene(episode, scene_no, aspect)                     # picture in compose (world + characters together)
    import numpy as np                                             # stems for the audio sensors (16 kHz, float16)
    stm = ST.STEMS
    k = max(1, int(stm["sr"] // 16000))
    np.savez_compressed(os.path.join(out, "stems.npz"), sr=stm["sr"] / k,
                        **{n: stm[n][::k].astype(np.float16) for n in ("voice", "music", "sfx", "amb")})
    json.dump(dict(lines=stm["lines"], sfx=stm["sfx_events"]), open(os.path.join(out, "audio_events.json"), "w"))

    with open(os.path.join(ROOT, "stories", episode, f"scene_{scene_no:02d}.json")) as fh:
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
        img.write_to_png(os.path.join(out, "sprites", "kraggor_far.png"))
        kmeta = dict(ext=[x0, y0, w, h], pad=pad, spx=spx, eyes=ST.KR_EYE_UNIT)
    shots = [dict(i=i, t0=round(s["t0"], 3), t1=round(s["t1"], 3),
                  cam="insert" if "look" in s else s.get("cam", "wide"), on=s.get("on"),
                  move=s.get("move") or {}, cut=s.get("cut", "soft"), lines=len(s.get("lines", [])),
                  sfx=[x if isinstance(x, str) else x[0] for x in s.get("sfx", [])], fx=s.get("fx", []),
                  caption=bool(s.get("caption")))
             for i, s in enumerate(box.get("shots") or [])]
    rows = [[i // PART, f] for i, f in enumerate(frames)]
    json.dump(dict(fps=ST.FPS, frames=rows), open(os.path.join(out, "frames.json"), "w"))
    json.dump(dict(scene=scene, shots=shots, theme=se.THEME, W=ST.W, H=ST.H, F=ST.F_PERSP, D0=ST.D0, DZ=ST.DZ,
                   Y_H=ST.Y_H, CAM_H=ST.CAM_H, CX=ST.CX, kfar=kmeta, fps=ST.FPS),
              open(os.path.join(out, "scene.json"), "w"))
    print(f"[story3d] scene {scene_no}: {len(frames)} frames, {len(shots)} shots -> {out}", flush=True)
    return len(frames)


if __name__ == "__main__":
    main()
