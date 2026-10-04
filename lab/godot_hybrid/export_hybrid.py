"""LAB — HYBRID sample (user 2026-10-04): the aired 2.5D CHALLENGE video stays exactly as it is — cars, road, pits,
debris, effects, HUD, narration — and Godot only replaces the background world (sim_engine.draw_sky: sky, sun,
clouds, sea, hills, trees, city) with a real 3D environment. Nothing of the cars is re-drawn.
This exporter replays the review render (--like) in the real engine and writes:
  <out>/frames.json   per output frame: level, mode, sim time, camera x/y/zoom (incl. punch), cairo horizon y
  <out>/scene.json    theme (time/weather/location), sky stops, light, sun/moon screen position, hill colours
  <out>/overlay.mov   the engine's OWN frames with draw_sky made transparent (alpha) -> laid over the 3D world
  <out>/mix.wav       the engine's own audio; <out>/meta.json  cold open (production rule)
  venv/bin/python lab/godot_hybrid/export_hybrid.py --seed 27 --series potholes --out /root/lab/hy/s27 \
      --like SIM_POTHOLES_V2_S027
Production modules are imported read-only; nothing in production imports lab/."""
import argparse
import json
import os
import shutil
import subprocess
import sys

import cairo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "generators", "physics_2d"))
import sim_engine as se  # noqa: E402
import registry  # noqa: E402


def force_like(vid):
    """Same cast / theme / narrator as the review render (registry snapshot taken just before it)."""
    full = registry.load()
    idx = next(i for i, e in enumerate(full["videos"]) if e["video_id"] == vid)
    snap = dict(full, videos=full["videos"][:idx])
    registry.load = lambda: snap
    ent = full["videos"][idx]
    man = json.load(open(f"{ROOT}/{ent['folder']}/{vid}.json"))
    th = man["theme"]
    orig_theme, orig_story = se.make_theme, se.make_story
    se.make_theme = lambda seed, force=None, used=None: orig_theme(seed, dict(th), used=[])
    voice = man["voice"]

    def forced_cb(*x, **k):
        if not voice.startswith("chatterbox"):
            return None
        who = voice.split(":")[1]
        se.CB.update(on=True, who=who, edge=se.CB_EDGE[who], missing=[])
        return voice
    se.cb_pick = forced_cb
    if not voice.startswith("chatterbox"):
        se.VOICES = [voice]

    def story(series, seed, appearances=None, wins=None):
        orig_story(series, seed, appearances, wins)
        for li, vk in enumerate(ent["vehicles"]):
            order = se.ROLE_ORDER[li]
            se.ROLE_ORDER[li] = [vk] + [o for o in order if o != vk]
        se.STORY = [(order[0], want) for order, (_, want) in zip(se.ROLE_ORDER, se.ROSTER)]
    se.make_story = story
    return man


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--series", default="potholes")
    ap.add_argument("--out", required=True)
    ap.add_argument("--like", required=True, help="the review/approved VIDEO_ID to enhance")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    man = force_like(a.like)
    name = f"LAB_HY_{a.series.upper()}_S{a.seed:03d}"
    sys.argv = ["sim_engine.py", "--seed", str(a.seed), "--series", a.series, "--preview-only", "--name", name]
    se.main()                                                    # the real engine: sim + timeline + audio + checks
    L0 = se.LEVELS
    got = [L["vk"] for L in L0]
    print(f"[hybrid] {len(se.INDEX)} frames, cast {got}, theme {se.THEME_ID}", flush=True)

    # ---- frames: the camera the cairo background used (draw_sky gets the punched zoom, no shake)
    rows = []
    for g, (li, j) in enumerate(se.INDEX):
        L = L0[li]
        st, mode = L["frames"][j]
        camx, camy, z = L["cam"][j]
        z *= se.zoom_punch(L, st)
        ground_sy = se.GROUND_Y + camy * se.S * z
        horizon = ground_sy - 300 * z - camy * se.S * 0.4               # the cairo horizon (draw_sky)
        rows.append([li, mode[0], round(st, 4), round(camx, 4), round(camy, 4), round(z, 4), round(horizon, 2)])
    json.dump(dict(fps=se.FPS, keys=["li", "mode", "st", "camx", "camy", "z", "horizon"], frames=rows),
              open(os.path.join(a.out, "frames.json"), "w"))

    # ---- scene: theme as the cairo sky draws it
    tm, loc = se.th_time(), se.th_loc()
    scene = dict(series=se.SERIES, seed=a.seed, like=a.like, theme=se.THEME, theme_id=se.THEME_ID,
                 sky=[[s_, list(c)] for s_, c in tm["sky"]], light=tm.get("light", 1.0), night="moon" in tm,
                 sun=list(tm["sun"][:3]) + [list(tm["sun"][3])] if "sun" in tm else None,
                 moon=list(tm["moon"]) if "moon" in tm else None, cloud=list(tm.get("cloud", (1, 1, 1))),
                 hills=[list(c) for c in loc["hills"]], loc_flags={k: bool(v) for k, v in loc.items() if k != "hills"},
                 S=se.S, ground_y=se.GROUND_Y, track=[list(p) for p in se.TRACK], finish_x=se.FINISH_X,
                 levels=[dict(vk=L["vk"], start=L["start"]) for L in L0])
    json.dump(scene, open(os.path.join(a.out, "scene.json"), "w"))

    # ---- overlay: the engine's own frame, background left transparent
    def no_sky(ctx, camx, camy, z):
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        ctx.restore()
    se.draw_sky = no_sky
    ov = os.path.join(a.out, "overlay.mov")
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", "1080x1920",
                           "-r", str(se.FPS), "-i", "-", "-c:v", "qtrle", ov], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1080, 1920)
    for g in range(len(se.INDEX)):
        ctx = cairo.Context(surf)
        se.draw_frame(ctx, g)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close()
    ff.wait()
    shutil.copy(f"{se.WORK}/mix_{name}.wav", os.path.join(a.out, "mix.wav"))
    subj = next((L["vk"] for L in L0 if L["event"]["type"] != "win"), L0[-1]["vk"])
    fails = [L["start"] + se.out_time(L, L["event"]["t"]) for L in L0 if L["event"]["type"] != "win"]
    json.dump(dict(cold_t=(fails or [3.0])[0], cold_text=f"CAN {se.VEHICLES[subj]['nick']} SURVIVE?",
                   title=man.get("title", "")), open(os.path.join(a.out, "meta.json"), "w"))
    print(f"[hybrid] export done -> {a.out}", flush=True)


if __name__ == "__main__":
    main()
