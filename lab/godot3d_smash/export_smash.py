"""LAB — 3D SMASH from the aired engine (smash25d.py v5). The engine runs its normal frame loop; only the world
layer (sky, stands, arena, cars) is skipped, so everything else it draws becomes a transparent overlay that lines
up exactly: HUD, fighter intros, bubbles, chaos (Kraggor, UFO, missile, cracks), the shark, damage smoke, POW,
banners, replay, winner, end card. The camera of every frame is read from the engine's own transform matrix.
Writes scene.json, frames.json, sprites/, overlay.mov (alpha), mix.wav, meta.json (cold open).
  venv/bin/python lab/godot3d_smash/export_smash.py --seed 2 --out /root/lab/s3d/s2 [--like SIM_SMASH25D_V5_S002]"""
import argparse
import json
import os
import subprocess
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for sub in ("generators/physics_2d", "generators/lanes25d", "generators/voice", "generators/publishing"):
    sys.path.insert(0, os.path.join(ROOT, sub))
import sim_engine as se  # noqa: E402
import smash25d as S  # noqa: E402
import race25d as R  # noqa: E402
import registry  # noqa: E402

PPM = 60
MOODS = ["normal", "scared", "whoa", "dizzy", "happy"]


class Caught(Exception):
    pass


def body_png(path, vk, mood):
    v = se.VEHICLES[vk]
    bw, bh = v["body"]
    w, h = int((bw + 1.6) * PPM), int((bh + 3.0) * PPM)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)
    ctx.translate(w / 2, h / 2)
    ctx.scale(PPM, -PPM)
    se.draw_body(ctx, vk, v, False, 0.0)
    se.draw_face(ctx, vk, mood, 0.0)
    surf.write_to_png(path)
    return w, h


def wheel_png(path, vk):
    v = se.VEHICLES[vk]
    r = v["wheel_r"]
    s = int(2 * r * PPM * 1.15) + 4
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, s, s)
    ctx = cairo.Context(surf)
    ctx.translate(s / 2, s / 2)
    ctx.scale(PPM, -PPM)
    se.draw_wheel(ctx, 0.0, 0.0, 0.0, r, vk.startswith("monster"))
    surf.write_to_png(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--like", default="")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    name = f"LAB_S3D_S{a.seed:03d}"
    argv = ["smash25d.py", "--seed", str(a.seed), "--preview-only", "--name", name]
    if a.like:                                                   # exactly what the review render used
        ent = registry.get(a.like)
        man = json.load(open(f"{ROOT}/{ent['folder']}/{a.like}.json"))
        cast = man["params"]["cast"]
        orig_setup, orig_theme = S.setup, se.make_theme
        # arena: not forced (that skips random draws and shifts the chaos plan) - make it the least used instead
        S.setup = lambda seed, app, used, forced=None: orig_setup(
            seed, {vk: (-10 + cast.index(vk) if vk in cast else 99) for vk in S.POOL},
            [ar for ar in S.ARENAS if ar != man["arena"] for _ in range(9)], None)
        se.make_theme = lambda seed, force=None, used=None: orig_theme(seed, dict(man["theme"]), used=[])
        voice = man["voice"]
        if not voice.startswith("chatterbox"):
            argv += ["--voice", "edge"]
            S.ANNOUNCERS = [voice.replace("edge:", "").split("+")[0]]
    got = {"cams": []}
    orig_sim, orig_audio = S.simulate, S.build_audio

    def sim(seed):                                               # keep the engine's own run (chaos state is one-shot)
        r = orig_sim(seed)
        got["sim"] = r
        return r
    S.simulate = sim

    def audio(frames, events, winner, star_t, replay, placed, voice, out_of, cta_start, intro_times=()):
        x = orig_audio(frames, events, winner, star_t, replay, placed, voice, out_of, cta_start, intro_times)
        got["narration"] = [txt for _, _, _, txt in placed]
        got.update(frames=list(frames), events=list(events), winner=winner, star_t=star_t, replay=replay,
                   out_of=out_of, cta_start=cta_start, intro=list(intro_times), audio=x)
        return x
    S.build_audio = audio

    def stands(ctx, camx, t, cheer):                              # world layer -> 3D; read the camera here
        m = ctx.get_matrix()
        zoom = m.xx
        shx = m.x0 - 540 + 540 * zoom
        shy = m.y0 - S.WORLD_DY - S.PIV_Y + S.PIV_Y * zoom
        got["cams"].append((camx, zoom, shx, shy, t))
    S.draw_stands = stands
    S.draw_arena = lambda *x, **k: None

    def sky(ctx, *x, **k):                                       # transparent background every frame
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        ctx.restore()
    se.draw_sky = sky
    orig_car = R.draw_car
    dummy = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 8, 8))

    def car(ctx, c, t, camx):                                    # cars -> 3D; keep the head position for bubbles
        dummy.set_matrix(ctx.get_matrix())
        return orig_car(dummy, c, t, camx)
    R.draw_car = car
    ov = os.path.join(a.out, "overlay.mov")
    real_popen, real_run = subprocess.Popen, subprocess.run

    class SP:                                                    # the engine's ffmpeg writer -> alpha qtrle overlay
        PIPE = subprocess.PIPE

        @staticmethod
        def Popen(cmd, **kw):
            if "rawvideo" in cmd:
                cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", "1080x1920",
                       "-r", "30", "-i", "-", "-c:v", "qtrle", ov]
            return real_popen(cmd, **kw)

        @staticmethod
        def run(cmd, **kw):
            if any(str(x).endswith(".mp4") and "/v_" in str(x) for x in cmd):
                raise Caught()                                   # the 2.5D mux: we are done
            return real_run(cmd, **kw)
    S.subprocess = SP
    sys.argv = argv
    try:
        S.main()
    except Caught:
        pass
    frames, cams = got["frames"], got["cams"]
    assert len(cams) == len(frames), (len(cams), len(frames))
    se.write_wav(os.path.join(a.out, "mix.wav"), got["audio"])
    print(f"[s3d] {len(frames)} frames, arena {S.ARENA}", flush=True)
    json.dump(dict(t_star=got["out_of"](got["star_t"] if got["star_t"] is not None else got["winner"]["finish"])),
              open(os.path.join(a.out, "_tmp.json"), "w"))
    got["cams_ok"] = True
    export_rest(a, got, name)


def export_rest(a, got, name):
    """scene / frames / sprites / meta from the captured run (cars come from the simulate() rerun)."""
    cars, events, hits, winner = got["sim"]
    sp = os.path.join(a.out, "sprites")
    os.makedirs(sp, exist_ok=True)
    cast = {}
    for c in cars:
        vk, v = c["key"], se.VEHICLES[c["key"]]
        for m in MOODS:
            w, h = body_png(os.path.join(sp, f"{vk}_{m}.png"), vk, m)
        wheel_png(os.path.join(sp, f"{vk}_wheel.png"), vk)
        cast[vk] = dict(body=list(v["body"]), wheel_r=v["wheel_r"], wheel_x=list(v["wheel_x"]), w=w, h=h,
                        travel=v["travel"], nick=v["nick"])
    th = se.th_time()
    bnd = [list(S.bounds(t)) for t in [i / 10 for i in range(0, 700)]]
    scene = dict(seed=a.seed, arena=S.ARENA, theme=se.THEME, theme_id=se.THEME_ID,
                 sky=[[s_, list(c_)] for s_, c_ in th["sky"]], light=th.get("light", 1.0), night="moon" in th,
                 cloud=list(th.get("cloud", (1, 1, 1))), cast=cast, bounds10=bnd,
                 events=[[e[0], e[1], e[2], e[3]] + ([e[4]] if len(e) > 4 and isinstance(e[4], (int, float)) else [])
                         for e in got["events"]],
                 hits=[dict(t=h["t"], x=h["x"], z=h["z"], rel=h["rel"], car=h["b"]["key"]) for h in hits],
                 proj=dict(F=S.F_PERSP, D0=S.D0, DZ=S.DZ, Y_H=S.Y_H, CAM_H=S.CAM_H, WORLD_DY=S.WORLD_DY,
                           PIV_Y=S.PIV_Y, ZC=S.ZC, HX0=S.HX0, HZ0=S.HZ0, STANDS_ROWS=S.STANDS_ROWS),
                 intro=got["intro"], winner=winner["key"], finish=winner["finish"],
                 narration=["Ready... Go!" if x == se.READY_SENTINEL else x for x in got.get("narration", [])])
    json.dump(scene, open(os.path.join(a.out, "scene.json"), "w"))
    rows = []
    for (mode, t), (camx, zoom, shx, shy, tt) in zip(got["frames"], got["cams"]):
        ts = 0.0 if mode == "intro" else t
        cs = []
        for c in cars:
            s = R.state(c, ts)
            sink = S.rec_at(c, "sink_rec", ts)
            hp = S.rec_at(c, "hp_rec", ts)
            out = c["out"] is not None and ts >= c["out"]
            cs.append([round(v, 4) for v in s] + [S.mood(c, ts, s[0]), round(sink, 3), round(hp, 1), out,
                                                  c["out_kind"] if out else ""])
        rows.append([mode[0], round(t, 4), round(camx, 4), round(zoom, 4), round(shx, 2), round(shy, 2), cs])
    json.dump(dict(fps=30, keys=["mode", "t", "camx", "zoom", "shx", "shy", "cars"],
                   car_keys=["x", "z", "h", "yaw", "pitch", "v", "sq", "split", "burn", "patched", "ice", "tires",
                             "mood", "sink", "hp", "out", "out_kind"], frames=rows),
              open(os.path.join(a.out, "frames.json"), "w"))
    t_star = json.load(open(os.path.join(a.out, "_tmp.json")))["t_star"]
    json.dump(dict(cold_t=t_star, cold_text="WHO SURVIVES?", title=f"{S.ARENA} smash"), open(os.path.join(a.out, "meta.json"), "w"))
    print(f"[s3d] export done -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
