"""CHALLENGE Short 'Cars VS The Dungeon' on the story3d engine (owner 2026-10-07: more exciting - a Mario-style gauntlet with
an axe, a lava pit and a monster; fast cars; BeamNG-style crashes). One course for every car:
  axe (x=14)  ->  lava pit (x=26..36, the cars JUMP it)  ->  ogre with a club (x=48)  ->  treasure.
Level 1 is squashed by the axe, level 2 falls into the lava, level 3 jumps the pit but is launched by the ogre, level 4
beats everything. Outcomes are SIMULATED (the eased run x the axe cycle / the pit / the ogre's slam time), crashes crumple
the struck end, throw debris and tumble the car. Writes stories/<episode>/scene_01.json (vertical 9:16, 'aspect v').
  python generators/story3d/tools/gen_challenge_dungeon.py --episode CH01_dungeon_axes --cast bus,sports,firetruck,f1"""
import argparse
import json
import math
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

CHOP = dict(P=2.6, up=1.0, fall=0.18, down=0.40, h_up=5.2, h_dn=0.15)        # = story25d.CHOP
AXES = [(30.0, 0.0), (102.0, 0.9), (110.0, 1.7)]                               # the first one stops level 1; two more near the end
RAMP = (52.0, 58.0, 1.4)                                                     # launch ramp: x0, lip x1, height at the lip
PIT = (58.0, 66.0)                                                           # the lava pit starts at the lip of the ramp
LAND_X = 70.0                                                                # winners land here (car centre)
SHORT_X = 62.0                                                               # a car that is too slow lands in the pit here
OGRE_X = 86.0
CLUB_X = OGRE_X - 3.6                                                        # where the club lands
START_X, FINISH_X, RUN_TO = 3.0, 120.0, 123.0
BODY = {"police": (4.4, 2.3), "monster": (4.3, 3.1), "monster2": (4.3, 3.1), "sports": (4.2, 1.5), "bus": (7.4, 3.0),
        "firetruck": (6.4, 3.2), "f1": (4.6, 1.2), "taxi": (4.3, 1.9), "bigrig": (9.6, 3.6), "icecream": (5.6, 2.9)}
DISPLAY = {"sports": "ZIPPY THE SPORTS CAR", "police": "SIREN THE POLICE CAR", "bus": "BUSTER THE SCHOOL BUS",
           "firetruck": "HYDRO THE FIRE TRUCK", "monster": "ROCKY THE MONSTER TRUCK",
           "monster2": "GRIZZLY THE MONSTER TRUCK", "f1": "NITRO THE RACE CAR", "taxi": "TILLY THE TAXI",
           "bigrig": "TITAN THE BIG RIG", "icecream": "SPRINKLES THE ICE CREAM TRUCK"}
NICK = {"sports": "Zippy", "police": "Siren", "bus": "Buster", "firetruck": "Hydro", "monster": "Rocky",
        "monster2": "Grizzly", "f1": "Nitro", "taxi": "Tilly", "bigrig": "Titan", "icecream": "Sprinkles"}
KIND = {"sports": "sports car", "police": "police car", "bus": "school bus", "firetruck": "fire truck",
        "monster": "monster truck", "monster2": "monster truck", "f1": "race car", "taxi": "taxi", "bigrig": "big rig",
        "icecream": "ice cream truck"}
LEVEL_COLORS = [(0.18, 0.72, 0.3), (1.0, 0.52, 0.08), (0.6, 0.3, 0.92), (0.9, 0.15, 0.25)]
LV = ["one", "two", "three", "four"]


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


def t_at(X, speed, delay):
    lo, hi = delay, delay + x_at(0, speed, delay)[1]
    for _ in range(60):
        mid = (lo + hi) / 2
        if x_at(mid, speed, delay)[0] < X:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def first_hit(vk, speed, delay, dt=0.004, xmax=1e9):
    half, h = BODY[vk][0] / 2, BODY[vk][1]
    _, T = x_at(0, speed, delay)
    u = 0.0
    while u < delay + T + 0.2:
        x, _ = x_at(u, speed, delay)
        if x > xmax:
            return None
        for i, (xp, ph) in enumerate(AXES):
            if abs(xp - x) < half + 0.9 and bottom(u + ph) < h:
                return i, round(u, 3), round(x, 2)
        u += dt
    return None


def robust(vk, speed, delay, want, xmax=1e9):
    for dd in (-0.12, 0.0, 0.12):
        r = first_hit(vk, speed, max(0.0, delay + dd), xmax=xmax)
        if (None if r is None else r[0]) != want:
            return False
    return True


def find_run(vk, want, xmax=1e9, speeds=(18.0, 19.0, 17.0, 20.0, 16.0)):
    for sp in speeds:
        for d10 in range(0, 40):
            delay = d10 * 0.1
            if robust(vk, sp, delay, want, xmax):
                return sp, delay, first_hit(vk, sp, delay, xmax=xmax)
    raise SystemExit(f"no run found for {vk} want={want}")


def slams(t_end):
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


def ballistic(tau, vx, vy, g, h0=0.0):                                        # = story25d.ballistic (position only)
    tl = (vy + math.sqrt(vy * vy + 2 * g * h0)) / g
    vimp = abs(vy - g * tl)
    vy2 = vimp * 0.4
    tl2 = 2 * vy2 / g
    return tl, vx * tl + vx * 0.4 * tl2


def L(spk, text, emo="excited"):
    return [spk, text, emo]


def build(cast):
    wants = [0, None, None, None]
    xmaxes = [1e9, SHORT_X + 3, OGRE_X, 1e9]                          # only the axes a car really reaches count
    runs = [find_run(vk, w, xm) for vk, w, xm in zip(cast, wants, xmaxes)]
    for vk, w, r in zip(cast, wants, runs):
        print(f"[dungeon] {NICK[vk]:8s} want={w} speed={r[0]} delay={r[1]} hit={r[2]}")
    actors = {vk: {"vk": vk, "x": START_X, "z": 1.4, "face": 1, "emo": "normal", "hidden": True} for vk in cast}
    HUD0 = {"title": "CARS VS THE DUNGEON!", "x0": START_X, "x1": FINISH_X, "marks": [AXES[0][0], (PIT[0] + PIT[1]) / 2, OGRE_X, AXES[1][0], AXES[2][0]]}
    shots, props, score = [], [], []
    shots.append({"cam": "wide", "zoom": 0.5, "dx": 28, "hold": 4.6, "cut": "hard", "move": {"push": 0.05},
                  "hud": {"title": "CARS VS THE DUNGEON!", "tag": "NEW 3D GRAPHICS!"}, "sfx": [["chain_rattle", 0.2, 0.7]],
                  "lines": [L("announcer", "Axes, lava and an angry ogre! Who will survive?")]})
    props.append({"type": "lava", "pits": [list(PIT)], "z": 1.4, "from_shot": 0, "to_shot": 99})
    props.append({"type": "ogre", "x": OGRE_X, "z": 0.7, "face": -1, "scale": 1.35, "slams": [], "from_shot": 0, "to_shot": 0,
                  "ref_shot": 0})
    props.append({"type": "chop", "axes": [[x, ph] for x, ph in AXES], "z": 0.3, "from_shot": 0, "to_shot": 0, "ref_shot": 0})
    for lv, (vk, (sp, delay, hit)) in enumerate(zip(cast, runs)):
        b = len(shots)
        col = LEVEL_COLORS[lv]
        hud = dict(HUD0, level=lv + 1, name=DISPLAY[vk], color=col, actor=vk)
        prev = cast[lv - 1] if lv else None
        intro_moves = {vk: {"show": True, "x": START_X}}
        if prev:
            intro_moves[prev] = {"show": False}
        trap = ["Watch out for the axe!", "Jump the lava pit!", "The ogre is awake!", "Axes, lava and the ogre!"][lv]
        shots.append({"cam": "wide", "zoom": 0.8, "dx": 9, "hold": 2.6, "cut": "hard", "moves": intro_moves, "move": {"pan": 2},
                      "hud": dict(hud, who="WHO WILL MAKE IT?") if lv == 0 else hud, "sfx": [["engine", 0.3, 0.5]],
                      "lines": [L("announcer2", (f"Level {LV[lv]}! " if lv < 3 else "Final level! ") +
                                  f"{NICK[vk]} the {KIND[vk]}! {trap}")]})
        T = x_at(0, sp, delay)[1]
        t_ramp0 = t_at(RAMP[0], sp, delay)
        t_lip = t_at(RAMP[1] - 0.5, sp, delay)
        t_land = t_at(LAND_X, sp, delay)
        moves = {"to_x": RUN_TO, "speed": sp, "delay": delay}
        sfx = [["engine", 0.0, 0.6]]
        slam_ogre = None
        half = BODY[vk][0] / 2
        if lv >= 1:
            moves["ramp"] = {"x0": RAMP[0], "x1": RAMP[1], "h": RAMP[2]}
        if lv == 1:                                                  # too slow: a short hop, drops into the lava
            t_short = t_at(SHORT_X, sp, delay)
            moves["jump"] = {"at": t_lip, "dur": t_short - t_lip, "peak": 1.0, "h0": RAMP[2]}
            fall_x = SHORT_X
            t_end = t_short
        elif lv >= 2:
            moves["jump"] = {"at": t_lip, "dur": t_land - t_lip, "peak": 2.8, "h0": RAMP[2]}
        if lv == 0:
            t_end = hit[1] + 0.1
        elif lv == 2:                                                # the club lands on the hood
            slam_ogre = t_at(CLUB_X - 1.7 - half, sp, delay)
            t_end = slam_ogre
        elif lv == 3:
            slam_ogre = t_at(OGRE_X + 2.0, sp, delay)               # the club lands well behind the winner
            t_end = delay + T + 0.2
        if lv >= 2:
            sfx.append(["car_boing", t_land, 0.5])
        if slam_ogre is not None:
            sfx.append(["ogre_swing", max(0.0, slam_ogre - 0.55), 0.9])
            sfx.append(["chop_slam", slam_ogre + 0.02, 0.7 if lv == 3 else 0.9])
        for i, t in slams(t_end):
            main = hit is not None and i == hit[0] and abs(t - hit[1]) < 0.45
            sfx.append(["chop_slam", max(0.0, t), 0.9 if main else 0.3])
            sfx.append(["chop_whoosh", max(0.0, t - 0.2), 0.3])
        shots.append({"cam": "track", "on": vk, "dx": 4.5, "zoom": 1.35, "hold": round(t_end, 2), "interrupt": True,
                      "speedlines": True, "move": {"push": 0.05}, "moves": {vk: moves}, "hud": hud, "sfx": sfx})
        res = {"cam": "medium", "on": vk, "zoom": 0.95, "hold": 4.6, "lead": 1.5, "jcut": 0.0, "move": {"push": 0.06}}
        if lv == 0:                                                  # the axe squashes the bus
            res["moves"] = {vk: {"squash": 0.4, "at": 0.0, "hold": 1.0, "dizzy": True, "to_x": hit[2] - 5.0, "speed": 4.0,
                                 "reverse": True, "crumple": {"at": 0.0, "end": 1, "amt": 0.5}}}
            res["impacts"] = [{"at": 0.0, "x": hit[2] + 0.5, "h": 2.0, "kind": "hit", "word": "CLANG!", "size": 1.1,
                               "shake": 26, "debris": ["wheel", "bumper", "light", "shard", "shard"]}]
            res["hud"] = dict(hud, badge="fail", badge_at=1.1, bubbles=[[0.15, "OUCH!", vk]])
            res["sfx"] = [["chop_slam", 0.0, 1.0], ["crash_big", 0.03, 0.9], ["car_boing", 1.0, 0.8]]
            res["lines"] = [L("announcer", f"Chop! {NICK[vk]} got squashed by the axe!")]
        elif lv == 1:                                                # into the lava, then spat out
            vx, vy, g, h0 = 10.0, 14.5, 24.0, -3.8
            tl, dxl = ballistic(0, vx, vy, g, h0)
            pop = 1.0
            res["moves"] = {vk: {"sink": {"at": 0.0, "dur": 0.7, "depth": 3.8, "tilt": 0.8},
                                 "fling": {"at": pop, "vx": vx, "vy": vy, "g": g, "turns": 1, "h0": h0}}}
            land_x = fall_x + vx * tl
            res["impacts"] = [{"at": 0.45, "x": fall_x, "h": 0.0, "kind": "splash", "word": "SPLASH!", "size": 1.1, "shake": 16},
                              {"at": pop + tl, "x": land_x, "h": 0.3, "kind": "land", "shake": 12}]
            res["hud"] = dict(hud, badge="fail", badge_at=1.3, bubbles=[[pop + tl, "HOT HOT HOT!", vk]])
            res["sfx"] = [["fall_whistle", 0.0, 0.5], ["lava_splash", 0.4, 0.6], ["car_boing", pop + tl, 0.8]]
            res["lines"] = [L("announcer", f"Splash! {NICK[vk]} fell into the lava!")]
        elif lv == 2:                                                # smashed up into the air
            vx, vy, g = -2.2, 13.0, 24.0
            tl, dxl = ballistic(0, vx, vy, g)
            res["moves"] = {vk: {"crumple": {"at": 0.0, "end": 1, "amt": 0.95},
                                 "fling": {"at": 0.06, "vx": vx, "vy": vy, "g": g, "turns": 1}}}
            cx = CLUB_X
            res["impacts"] = [{"at": 0.0, "x": cx, "h": 1.6, "kind": "hit", "word": "BAM!", "size": 1.3, "shake": 30,
                               "debris": ["wheel", "bumper", "light", "shard", "shard", "shard"]},
                              {"at": 0.06 + tl, "x": cx - 1.7 - BODY[vk][0] / 2 + vx * tl, "h": 0.3, "kind": "land", "word": "CRASH!",
                               "size": 1.0, "shake": 20}]
            res["hud"] = dict(hud, badge="fail", badge_at=1.1, bubbles=[[0.5, "WAAAH!", vk]])
            res["sfx"] = [["crash_big", 0.0, 1.0], ["car_boing", 0.06 + tl, 0.8], ["chop_slam", 0.06 + tl, 0.6]]
            res["lines"] = [L("announcer", f"Smash! The ogre sent {NICK[vk]} flying!")]
        else:
            res["moves"] = {vk: {"hop": True}}
            res["hud"] = dict(hud, badge="win", badge_at=0.4, outro_at=3.2, bubbles=[[0.2, "YES!", vk]])
            res["hold"] = 6.2
            res["sfx"] = [["jingle", 0.4, 0.8]]
            res["lines"] = [L("announcer", f"Incredible! {NICK[vk]} beat the whole dungeon!")]
        shots.append(res)
        props.append({"type": "chop", "axes": [[x, ph] for x, ph in AXES], "z": 0.3, "from_shot": b, "to_shot": b + 2,
                      "ref_shot": b + 1})
        props.append({"type": "ogre", "x": OGRE_X, "z": 0.7, "face": -1, "scale": 1.35,
                      "slams": [round(slam_ogre, 3)] if slam_ogre is not None else [], "from_shot": b, "to_shot": b + 2,
                      "ref_shot": b + 1})
        if lv in (1, 2):                                             # A10: music only on tense fail runs and the win
            score.append({"cue": "cue_tension_cave", "from": b + 1, "to": b + 1, "vol": 0.38, "start": 6.0 + 5.0 * lv,
                          "fade": 0.4, "tail": 0.5})
        if lv == 3:
            score.append({"cue": "cue_heroic_stand", "from": b + 1, "to": b + 2, "vol": 0.45, "start": 0.0, "fade": 0.4,
                          "tail": 0.8})
    return {
        "title": "CHALLENGE - Cars VS The Dungeon", "chapter": "Cars VS The Dungeon", "location": "dungeon",
        "theme_location": "city", "time": "night", "weather": "clear", "ambience": "cave", "fog": 0.15, "letterbox": False,
        "edge_fade": False, "gap": 0.35, "tail": 0.6, "wall_z": 5.2, "exit_x": FINISH_X + 6.0, "finish": FINISH_X,
        "lava": [list(PIT)], "lava_z": [-0.2, 3.6], "ramps": [list(RAMP)], "actors": actors, "props": props, "score": score, "shots": shots}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--cast", default="bus,sports,firetruck,f1",
                    help="vehicle keys: level 1 (axe), 2 (lava), 3 (ogre), 4 (wins) - rotate the 10 characters")
    a = ap.parse_args()
    scene = build(a.cast.split(","))
    d = os.path.join(ROOT, "stories", a.episode)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "scene_01.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(scene, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"[dungeon] wrote {d}/scene_01.json ({len(scene['shots'])} shots)")


if __name__ == "__main__":
    main()
