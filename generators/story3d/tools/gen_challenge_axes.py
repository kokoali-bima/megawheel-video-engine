"""CHALLENGE Short 'Cars VS Dungeon Axes' on the story3d engine (owner 2026-10-07: a CHALLENGE Short made with the new
engine, rotating the 10 characters, an obstacle never used before, a dungeon).
Giant axes chop down on a fixed rhythm; each level one car tries to run the gauntlet. The outcome of every run is
SIMULATED here (the car's eased motion x the axes' cycle), so a fail is a real hit and a win is a real clean pass, and
the sound effects land on the real slams. Writes stories/<episode>/scene_01.json (vertical 9:16, 'aspect v').
  python generators/story3d/tools/gen_challenge_axes.py --episode CH01_dungeon_axes --cast siren,rocky,monster2"""
import argparse
import json
import math
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

CHOP = dict(P=2.6, up=1.0, fall=0.18, down=0.40, h_up=5.2, h_dn=0.15)        # = story25d.CHOP
AXES = [(16.0, 0.0), (28.0, 0.9), (40.0, 1.7)]                                # x, phase (s)
START_X, FINISH_X, RUN_TO = 2.0, 56.0, 60.0
BODY = {"police": (4.4, 2.3), "monster": (4.3, 3.1), "monster2": (4.3, 3.1), "sports": (4.2, 1.5), "bus": (7.4, 3.0),
        "firetruck": (6.4, 3.2), "f1": (4.6, 1.2), "taxi": (4.3, 1.9), "bigrig": (9.6, 3.6), "icecream": (5.6, 2.9)}
DISPLAY = {"sports": "ZIPPY THE SPORTS CAR", "police": "SIREN THE POLICE CAR", "bus": "BUSTER THE SCHOOL BUS",
           "firetruck": "HYDRO THE FIRE TRUCK", "monster": "ROCKY THE MONSTER TRUCK",
           "monster2": "GRIZZLY THE MONSTER TRUCK", "f1": "NITRO THE RACE CAR", "taxi": "TILLY THE TAXI",
           "bigrig": "TITAN THE BIG RIG", "icecream": "SPRINKLES THE ICE CREAM TRUCK"}
NICK = {"sports": "Zippy", "police": "Siren", "bus": "Buster", "firetruck": "Hydro", "monster": "Rocky",
        "monster2": "Grizzly", "f1": "Nitro", "taxi": "Tilly", "bigrig": "Titan", "icecream": "Sprinkles"}
LEVEL_COLORS = [(0.18, 0.72, 0.3), (1.0, 0.52, 0.08), (0.6, 0.3, 0.92)]


def bottom(tau):
    c = CHOP
    rise = c["P"] - c["up"] - c["fall"] - c["down"]
    tau %= c["P"]
    if tau < c["up"]:
        return c["h_up"]
    tau -= c["up"]
    if tau < c["fall"]:
        return c["h_up"] + (c["h_dn"] - c["h_up"]) * (tau / c["fall"]) ** 2
    tau -= c["fall"]
    if tau < c["down"]:
        return c["h_dn"]
    tau -= c["down"]
    return c["h_dn"] + (c["h_up"] - c["h_dn"]) * min(1.0, tau / rise)


def x_at(u, speed, delay):
    """story25d's eased move: T = |d|/speed * 1.25 + 0.4, smoothstep."""
    d = RUN_TO - START_X
    T = d / speed * 1.25 + 0.4
    pr = min(1.0, max(0.0, (u - delay) / T))
    return START_X + d * pr * pr * (3 - 2 * pr), T


def first_hit(vk, speed, delay, dt=0.004):
    half, h = BODY[vk][0] / 2, BODY[vk][1]
    _, T = x_at(0, speed, delay)
    u = 0.0
    while u < delay + T + 0.2:
        x, _ = x_at(u, speed, delay)
        for i, (xp, ph) in enumerate(AXES):
            if abs(xp - x) < half + 0.9 and bottom(u + ph) < h:
                return i, round(u, 3), round(x, 2)
        u += dt
    return None


def robust(vk, speed, delay, want):
    """the wanted outcome must also hold for delays +-0.12 s (a clean pass / the same axe)."""
    for dd in (-0.12, 0.0, 0.12):
        r = first_hit(vk, speed, max(0.0, delay + dd))
        if (None if r is None else r[0]) != want:
            return False
    return True


def find_run(vk, want, speeds=(7.0, 7.5, 8.0, 6.5, 6.0, 8.5)):
    for sp in speeds:
        for d10 in range(0, 40):
            delay = d10 * 0.1
            if robust(vk, sp, delay, want):
                return sp, delay, first_hit(vk, sp, delay)
    raise SystemExit(f"no run found for {vk} want={want}")


def slams(t_end):
    """(axe index, time) of every slam before t_end (the moment the edge lands)."""
    out = []
    for i, (xp, ph) in enumerate(AXES):
        n = -2
        while True:
            t = n * CHOP["P"] - ph + CHOP["up"] + CHOP["fall"]
            if t > t_end:
                break
            if t >= 0.05:
                out.append((i, round(t, 2)))
            n += 1
    return sorted(out, key=lambda e: e[1])


def L(spk, text, emo="excited"):
    return [spk, text, emo]


def build(cast):
    wants = [0, 1, None]                                           # level 1 hit by axe 1, level 2 by axe 2, level 3 clean
    runs = [find_run(vk, w) for vk, w in zip(cast, wants)]
    for vk, w, r in zip(cast, wants, runs):
        print(f"[axes] {NICK[vk]:8s} want={w} speed={r[0]} delay={r[1]} hit={r[2]}")
    actors = {}
    for k, vk in enumerate(cast):
        actors[vk] = {"vk": vk, "x": START_X, "z": 1.4, "face": 1, "emo": "normal", "hidden": True}
    marks = [x for x, _ in AXES]
    HUD0 = {"title": "CARS VS DUNGEON AXES!", "x0": START_X, "x1": FINISH_X, "marks": marks}
    shots, props = [], []
    shots.append({"cam": "wide", "zoom": 0.5, "dx": 20, "hold": 3.0, "cut": "hard", "move": {"push": 0.05},
                  "hud": {"title": "CARS VS DUNGEON AXES!", "tag": "NEW 3D GRAPHICS!"}, "sfx": [["chain_rattle", 0.2, 0.7]],
                  "lines": [L("announcer", "Three drivers. Three giant dungeon axes. Who will survive?")]})
    # a decorative axe rhythm in the cold open (own prop, its rhythm measured from shot 0)
    props.append({"type": "chop", "axes": [[x, ph] for x, ph in AXES], "z": 0.3, "from_shot": 0, "to_shot": 0, "ref_shot": 0})
    # A10 (new sound style): music only on the tense runs and the win - a low pulsing dungeon cue, never a carpet
    score = [{"cue": "cue_tension_cave", "from": 0, "to": 0, "vol": 0.38, "start": 6.0, "fade": 0.5, "tail": 0.6}]
    for lv, (vk, (sp, delay, hit)) in enumerate(zip(cast, runs)):
        b = len(shots)
        col = LEVEL_COLORS[lv]
        nm = DISPLAY[vk]
        hud = dict(HUD0, level=lv + 1, name=nm, color=col, actor=vk)
        prev = cast[lv - 1] if lv else None
        intro_moves = {vk: {"show": True, "x": START_X}}
        if prev:
            intro_moves[prev] = {"show": False}
        shots.append({"cam": "wide", "zoom": 0.55, "dx": 12, "hold": 2.2, "cut": "hard", "moves": intro_moves, "move": {"pan": 2},
                      "hud": dict(hud, who="WHO WILL MAKE IT?") if lv == 0 else hud, "sfx": [["engine", 0.3, 0.5]],
                      "lines": [L("announcer2", f"Level {['one', 'two', 'three'][lv]}! {NICK[vk]} the "
                                  f"{DISPLAY[vk].split(' THE ')[1].lower()}!")]})
        T = x_at(0, sp, delay)[1]
        t_end = (hit[1] + 0.1) if hit else (delay + T + 0.3)
        sl = slams(t_end)
        sfx = [["engine", 0.0, 0.6]]
        for i, t in sl:
            main = hit is not None and i == hit[0] and abs(t - hit[1]) < 0.45
            sfx.append(["chop_slam", max(0.0, t), 1.0 if main else 0.4])
            sfx.append(["chop_whoosh", max(0.0, t - 0.2), 0.3])
        shots.append({"cam": "track", "on": vk, "dx": 3.5, "zoom": 1.25, "hold": round(t_end, 2), "interrupt": True,
                      "move": {"push": 0.05}, "moves": {vk: {"to_x": RUN_TO, "speed": sp, "delay": delay}},
                      "hud": hud, "sfx": sfx})
        res = {"cam": "medium", "on": vk, "zoom": 1.1, "hold": 3.6, "move": {"push": 0.08}}
        if hit:
            res["moves"] = {vk: {"squash": 0.42, "at": 0.0, "hold": 1.0, "dizzy": True, "to_x": hit[2] - 4.0, "speed": 5.0,
                                 "reverse": True}}
            res["hud"] = dict(hud, badge="fail", badge_at=0.2, bubbles=[[0.1, "OUCH!", vk]])
            res["sfx"] = [["car_boing", 1.0, 0.8]]
            res["lines"] = [L("announcer", f"Chop! {NICK[vk]} got hit by axe number {['one', 'two', 'three'][hit[0]]}!")]
        else:
            res["moves"] = {vk: {"to_x": FINISH_X + 2.0, "speed": 3.0}}
            res["hud"] = dict(hud, badge="win", badge_at=0.4, outro_at=3.0, bubbles=[[0.2, "YES!", vk]])
            res["hold"] = 6.0
            res["sfx"] = [["jingle", 0.4, 0.8]]
            res["lines"] = [L("announcer", f"Perfect timing! {NICK[vk]} survives all three axes!")]
        shots.append(res)
        props.append({"type": "chop", "axes": [[x, ph] for x, ph in AXES], "z": 0.3, "from_shot": b, "to_shot": b + 2,
                      "ref_shot": b + 1})
        score.append({"cue": "cue_tension_cave", "from": b + 1, "to": b + 1, "vol": 0.38, "start": 6.0 + 5.0 * lv,
                      "fade": 0.4, "tail": 0.5})                    # the run: a pulsing low cue builds the tension
        if not hit:                                                 # the win: the heroic cue under the badge and the CTA
            score.append({"cue": "cue_heroic_stand", "from": b + 2, "to": b + 2, "vol": 0.45, "start": 0.0, "fade": 0.4,
                          "tail": 0.8})
    scene = {
        "title": "CHALLENGE - Cars VS Dungeon Axes", "chapter": "Cars VS Dungeon Axes", "location": "dungeon",
        "theme_location": "city", "time": "night", "weather": "clear", "ambience": "cave", "fog": 0.15, "letterbox": False,
        "edge_fade": False, "gap": 0.35, "tail": 0.6, "wall_z": 5.2, "exit_x": FINISH_X + 6.0, "finish": FINISH_X,
        "actors": actors, "props": props, "score": score, "shots": shots}
    return scene


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--cast", default="police,monster,monster2", help="vehicle keys: level 1 (hit by axe 1), 2 (axe 2), 3 (wins)")
    a = ap.parse_args()
    cast = a.cast.split(",")
    scene = build(cast)
    d = os.path.join(ROOT, "stories", a.episode)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "scene_01.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(scene, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"[axes] wrote {d}/scene_01.json ({len(scene['shots'])} shots)")


if __name__ == "__main__":
    main()
