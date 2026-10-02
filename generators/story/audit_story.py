"""Story audit: checks the shot lists BEFORE rendering, from the user's review rules (DRAF_v6, 2026-10-02).

  venv/bin/python generators/story/audit_story.py --episode S01E01_sprinkles_first_race [--aspect h]

Checks (per shot, positions simulated like the renderer):
  FRAME   close/medium/two shot: the subject's body must be >= 85 % inside the frame
  FACE    a character's face must not be hidden behind another vehicle's body (mimic must be visible)
  STOP    race scenes ("race": true): visible cars must move or "roll" (no frozen cars mid-race)
  SHAKE   camera shake / crash sound needs a "note" explaining what happened
  KEYWORD a line mentions mud / song / hill / number -> the scene must show it (mud prop, jingle, hill, note)
  LOOK    a "look" shot must point at something (prop / hill / actor near x)
  CUT     transitions (edit.json) must be >= 0.8 s, shot glide >= 0.8 s
Exit code 1 when any ERROR is found; WARN lines are for review.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import story25d as st  # noqa: E402

se = st.se
KEYWORDS = {"mud": ("mud", "prop"), "song": ("jingle", "sfx"), "hill": ("hill", "scene"),
            "thirteen": ("#13", "text"), "#13": ("#13", "text")}


def body_box(a, camx, zoom, piv):
    """Screen box (x0, y0, x1, y1) of an actor's body + its face point."""
    veh = se.VEHICLES[a["key"]]
    bw, bh = veh["body"]
    k = st.k_of(a["z"])
    hh, _ = st.hill_h(a["x"])
    ride = veh["wheel_r"] + 0.6 * veh["travel"] + bh / 2
    gy = st.ground_y(a["z"])

    def scr(x, y):
        return st.W / 2 + (x - camx) * k * zoom, st.H / 2 + (y - piv) * zoom

    x0, y0 = scr(a["x"] - bw / 2 * a["small"], gy - (a["h"] + hh + (ride + bh / 2 + 0.6) * a["small"]) * k)
    x1, y1 = scr(a["x"] + bw / 2 * a["small"], gy - (a["h"] + hh) * k)
    fx, fy = se.FACES[a["key"]]["eyes"][0]
    face = scr(a["x"] + fx * a["face"] * a["small"], gy - (a["h"] + hh + (ride + fy) * a["small"]) * k)
    return (min(x0, x1), y0, max(x0, x1), y1), face


def inside(box):
    x0, y0, x1, y1 = box
    area = max(1e-6, (x1 - x0) * (y1 - y0))
    ix = max(0.0, min(x1, st.W) - max(x0, 0.0))
    iy = max(0.0, min(y1, st.H) - max(y0, 0.0))
    return ix * iy / area


def simulate(scene):
    """Actor positions at the end of every shot (moves completed), like the renderer."""
    actors = {aid: st.make_actor(aid, a) for aid, a in scene["actors"].items()}
    for a in actors.values():
        a["sq"], a["v"] = 1.0, 0.0
    states = []
    for sh in scene["shots"]:
        dur = max(sh.get("hold", 0.0), 2.5)
        for aid, mv in sh.get("moves", {}).items():
            a = actors[aid]
            if "show" in mv:
                a["hidden"] = not mv["show"]
            if "x" in mv:
                a["x"] = mv["x"]
            if "face" in mv:
                a["face"] = mv["face"]
            if "h" in mv:
                a["h"] = mv["h"]
        before = {aid: dict(a) for aid, a in actors.items()}
        for aid, mv in sh.get("moves", {}).items():
            a = actors[aid]
            if "to_x" in mv:
                d = mv["to_x"] - a["x"]
                if not mv.get("reverse"):
                    a["face"] = 1 if d >= 0 else -1
                a["x"] = mv["to_x"]
        if sh.get("roll"):
            for a in actors.values():
                if not a["hidden"]:
                    a["x"] += sh["roll"] * dur
        states.append((before, {aid: dict(a) for aid, a in actors.items()}))
    return states


def audit_scene(path, out):
    sc = json.load(open(path, encoding="utf-8"))
    st.SCENE.clear()
    st.SCENE.update(sc)
    name = os.path.basename(path)
    texts = " ".join(ln[1].lower() for sh in sc["shots"] for ln in sh.get("lines", []))
    sfx_all = {x if isinstance(x, str) else x[0] for sh in sc["shots"] for x in sh.get("sfx", [])}
    sfx_all |= set(sc.get("context", []))                         # established in the previous scene
    notes = " ".join(str(sh.get(k, "")) for sh in sc["shots"] for k in ("note", "caption")).lower()
    props = {p["type"] for p in sc.get("props", [])}
    for kw, (need, kind) in KEYWORDS.items():
        if kw in texts:
            ok = (kind == "prop" and need in props) or (kind == "sfx" and need in sfx_all) or \
                 (kind == "scene" and sc.get(need)) or (kind == "text" and need in notes)
            if not ok:
                out.append(("ERROR", name, "-", f"KEYWORD: dialog menyebut '{kw}' tapi tidak ada {need} ({kind})"))
    for i, (sh, (before, after)) in enumerate(zip(sc["shots"], simulate(sc)), start=1):
        tag = f"shot {i:02d} {sh.get('cam', 'look' if 'look' in sh else 'wide')}"
        if ("shake" in sh.get("fx", []) or "splat" in [x if isinstance(x, str) else x[0] for x in sh.get("sfx", [])]) \
                and not sh.get("note") and not sh.get("kraggor") and not sh.get("foot"):
            out.append(("ERROR", name, tag, "SHAKE: kamera bergetar / tabrakan tanpa 'note' penjelasan"))
        if sc.get("race") and not sh.get("roll") and not sh.get("moves") and not sh.get("freeze"):
            if any(not a["hidden"] for a in after.values()):
                out.append(("WARN", name, tag, "STOP: adegan balap tanpa gerak/roll (mobil terlihat diam)"))
        if "look" in sh:
            lx = sh["look"]["x"]
            near = [p for p in sc.get("props", []) if abs(p.get("x", 0) - lx) < 6] + \
                   [a for a in after.values() if not a["hidden"] and abs(a["x"] - lx) < 6]
            hl = sc.get("hill")
            if not near and not (hl and hl["x0"] <= lx <= hl["x3"]):
                out.append(("ERROR", name, tag, f"LOOK: kamera diarahkan ke x={lx} tapi tidak ada objek di sana"))
            continue
        for phase, acts in (("awal", before), ("akhir", after)):
            cx, zm, fy = st.cam_for(sh, acts, 0.0, 0.0)
            piv = (fy if fy is not None else st.ground_y(1.0) - 2.3 * st.k_of(1.0)) - sh.get("lift", 0.0) * st.k_of(1.0)
            vis = [a for a in acts.values() if not a["hidden"]]
            boxes = {a["id"]: body_box(a, cx, zm, piv) for a in vis}
            subj = sh.get("on")
            if subj in boxes and sh.get("cam") in ("close", "medium", "two"):
                f = inside(boxes[subj][0])
                if f < 0.85:
                    out.append(("ERROR", name, tag, f"FRAME ({phase}): {subj} hanya {f:.0%} masuk frame"))
            for a in vis:                                         # face hidden behind a vehicle in front?
                (_, fpt) = boxes[a["id"]]
                if not (0 <= fpt[0] <= st.W and 0 <= fpt[1] <= st.H):
                    continue
                for b in vis:
                    if b is a or b["z"] >= a["z"]:
                        continue
                    x0, y0, x1, y1 = boxes[b["id"]][0]
                    if x0 <= fpt[0] <= x1 and y0 <= fpt[1] <= y1:
                        out.append(("ERROR", name, tag, f"FACE ({phase}): wajah {a['id']} tertutup bodi {b['id']}"))
        if sh.get("glide", sc.get("glide", 1.2)) < 0.8 and sh.get("cut") != "hard":
            out.append(("WARN", name, tag, "CUT: glide < 0.8 s (terasa terburu-buru)"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--aspect", default="h")
    a = ap.parse_args()
    st.setup_projection(a.aspect)
    se.load_cast()
    d = os.path.join(st.BASE, "stories", a.episode)
    out = []
    for path in sorted(glob.glob(os.path.join(d, "scene_*.json"))):
        audit_scene(path, out)
    ed = os.path.join(d, "edit.json")
    if os.path.exists(ed):
        for i, x in enumerate(json.load(open(ed))["transitions"]):
            dur = st.XF_DUR.get(x, 1.0) if isinstance(x, str) else float(x[1])
            if dur < 0.8:
                out.append(("WARN", "edit.json", f"transisi {i}", f"CUT: transisi {dur:.1f} s < 0.8 s"))
    for lvl, f, tag, msg in out:
        print(f"[audit] {lvl:5s} {f} {tag}: {msg}")
    err = sum(1 for o in out if o[0] == "ERROR")
    print(f"[audit] {err} ERROR, {len(out) - err} WARN")
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
