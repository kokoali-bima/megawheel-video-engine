#!/usr/bin/env python3
"""Builds stories/S01E03_forgotten_speedway/scene_01..10.json + _script_index.json from one source of truth.
v1.8: TASK M revision after Codex gate v1.5.
- S9: Zippy is righted gradually while the cable is taut and the claws still hold; the cable is released only after
  he is stable, the hook reels back, then he drives away.
- Shot-start table is strictly signature-checked for all ten scenes; --write-sigs refreshes the _sig block.
- validate_table() now checks existence, shot counts, [t0,t1] shape, positive durations, zero start, contiguity,
  and _sig coverage for all scenes 1..10 BEFORE any output file is written.
HONEST LIMITS of the signature: scene_sig() covers only each shot's hold and its speaker+text lines. It does NOT
cover the voice model / reference audio / TTS audio hash, the lead / gap / tail / J-cut / freeze settings, or the
engine version. --write-sigs refreshes the checksum without re-measuring any times, so a refreshed table can still
be stale with respect to the rendered audio unless real_shot_times.json is re-exported from frames.json after voice
 generation (see _meta.engine_diff and _meta.voice_cache_files).
Usage (worktree root):  python3 build_s01e03.py [--write-sigs] [--selftest-table]
"""
import copy
import hashlib
import json
import math
import os
import sys

EP = "stories/S01E03_forgotten_speedway"

_HERE = os.path.dirname(os.path.abspath(__file__))
WRITE_SIGS_MODE = "--write-sigs" in sys.argv
SELFTEST_TABLE_MODE = "--selftest-table" in sys.argv
ALLOW_ESTIMATE = os.environ.get("S01E03_ALLOW_ESTIMATE") == "1"
SIG_SCENES = {str(n) for n in range(1, 11)}                    # every scene in the table must be signed
try:
    with open(os.path.join(_HERE, "real_shot_times.json"), encoding="utf-8") as _fh:
        REAL_SHOT_TIMES = json.load(_fh)
except Exception:                                              # noqa: BLE001
    REAL_SHOT_TIMES = {}


# ---------------------------------------------------------------- helpers
def A(vk, x, z, face=1, emo="normal", **kw):
    d = {"vk": vk, "x": x, "z": z, "face": face, "emo": emo}
    d.update(kw)
    return d


def L(who, text, emo="normal"):
    return [who, text, emo]


def base(title, chapter, location, time, ambience, **kw):
    d = {"title": title, "chapter": chapter, "location": location, "theme_location": kw.pop("theme", "countryside"),
         "time": time, "weather": "clear", "ambience": ambience, "letterbox": True, "gap": 0.45, "tail": 0.9, "edge_fade": False}
    d.update(kw)
    return d


KR_CALM = {"mode": "calm", "sx": 0.88, "sy": 0.6, "scale": 0.45, "stand": True, "gz": 6.5}
SCRIPT = []          # (scene no, chapter, [(speaker, text)], estimated seconds)
SCENES = {}          # scene no -> scene dict (for signatures)


def _speech(shots):
    return sum(len(l[1].split()) / 2.9 + 0.35 for s in shots for l in s.get("lines", []))


def _shot_len(d, s):
    sp = sum(len(l[1].split()) / 2.9 + 0.35 for l in s.get("lines", []))
    return max(float(s.get("hold", 0) or 0), sp + 0.3)


def est(d):
    """rough duration: shot = max(hold, speech) ; speech = words/2.9 + 0.35 per line; + gap*0.5"""
    return round(sum(_shot_len(d, s) + d.get("gap", 0.45) * 0.5 for s in d["shots"]), 1)


def _estimate_scene_time(d, i):
    return round(sum(_shot_len(d, s) + d.get("gap", 0.45) * 0.5 for s in d["shots"][:i]), 2)


def scene_sig(d):
    """Structural signature: what determines the shot table (holds + spoken text), not props/emotions.
    HONEST LIMITS: it does NOT cover the voice model / reference audio / TTS audio hash, the lead / gap / tail /
    J-cut / freeze settings, or the engine version. --write-sigs refreshes this checksum without re-measuring any
    times."""
    struct = []
    for s in d["shots"]:
        struct.append([s.get("hold", 0), [[l[0], l[1]] for l in s.get("lines", [])]])
    return hashlib.md5(json.dumps(struct, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()[:12]


def _sig_problem(n, d):
    """Why the signed table cannot be trusted for scene n (None = fine)."""
    sigs = REAL_SHOT_TIMES.get("_sig")
    if not isinstance(sigs, dict):
        return "real_shot_times.json is unsigned (no _sig block)"
    missing = sorted((s for s in SIG_SCENES if s not in sigs), key=int)
    if missing:
        return "real_shot_times.json _sig is missing scene(s) " + ", ".join(missing)
    if sigs.get(str(n)) != scene_sig(d):
        return "real_shot_times.json scene " + str(n) + " is stale (signature mismatch)"
    return None


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))


def validate_table(scenes):
    """Strictly validate real_shot_times.json against every built scene 1..10.

    Raises RuntimeError on: missing scene key, wrong shot count, non-[t0,t1] entry, t1 <= t0, first t0 not 0.0
    (tolerance 0.002), non-contiguous consecutive entries (tolerance 0.002), missing _sig scene key, or stale
    signature. --write-sigs tolerates only stale signatures. S01E03_ALLOW_ESTIMATE=1 skips with a warning.
    """
    if ALLOW_ESTIMATE:
        print("WARNING: S01E03_ALLOW_ESTIMATE=1 -> skipping real_shot_times.json validation")
        return

    if not isinstance(REAL_SHOT_TIMES, dict):
        raise RuntimeError("real_shot_times.json is not a JSON object")

    sigs = REAL_SHOT_TIMES.get("_sig")
    if not isinstance(sigs, dict):
        raise RuntimeError("real_shot_times.json is unsigned (no _sig block); regenerate it or set S01E03_ALLOW_ESTIMATE=1")

    for n in range(1, 11):
        key = str(n)
        d = scenes.get(n)
        if d is None:
            raise RuntimeError("built scene " + key + " is missing; cannot validate real_shot_times.json")

        if key not in REAL_SHOT_TIMES:
            raise RuntimeError("real_shot_times.json is missing scene " + key +
                               "; regenerate it or set S01E03_ALLOW_ESTIMATE=1")

        table = REAL_SHOT_TIMES[key]
        if not isinstance(table, list):
            raise RuntimeError("real_shot_times.json scene " + key + " is not a list of [t0, t1] pairs")

        n_shots = len(d.get("shots", []))
        if len(table) != n_shots:
            raise RuntimeError("real_shot_times.json scene " + key + " has " + str(len(table)) +
                               " shot(s), but the built scene has " + str(n_shots) +
                               "; regenerate it or set S01E03_ALLOW_ESTIMATE=1")

        for i, entry in enumerate(table):
            if (not isinstance(entry, (list, tuple)) or len(entry) != 2 or
                    not _is_number(entry[0]) or not _is_number(entry[1])):
                raise RuntimeError("real_shot_times.json scene " + key + " shot " + str(i) +
                                   " is not a two-number [t0, t1] pair: " + repr(entry))
            t0 = float(entry[0])
            t1 = float(entry[1])
            if t1 <= t0:
                raise RuntimeError("real_shot_times.json scene " + key + " shot " + str(i) +
                                   " has t1 <= t0 (t0=" + str(t0) + ", t1=" + str(t1) + ")")

        if not table:
            raise RuntimeError("real_shot_times.json scene " + key + " has an empty shot table")

        first_t0 = float(table[0][0])
        if abs(first_t0 - 0.0) > 0.002:
            raise RuntimeError("real_shot_times.json scene " + key + " first shot starts at t0=" + str(first_t0) +
                               " instead of 0.0 (tolerance 0.002)")

        for i in range(len(table) - 1):
            gap = abs(float(table[i][1]) - float(table[i + 1][0]))
            if gap > 0.002:
                raise RuntimeError("real_shot_times.json scene " + key + " shots " + str(i) + " and " + str(i + 1) +
                                   " are not contiguous (t1=" + str(float(table[i][1])) +
                                   ", next t0=" + str(float(table[i + 1][0])) +
                                   ", gap=" + str(round(gap, 6)) + " > 0.002)")

        if key not in sigs:
            raise RuntimeError("real_shot_times.json _sig is missing scene " + key +
                               "; regenerate it or set S01E03_ALLOW_ESTIMATE=1")

        expected = scene_sig(d)
        if sigs.get(key) != expected and not WRITE_SIGS_MODE:
            raise RuntimeError("real_shot_times.json scene " + key + " is stale (signature mismatch: table " +
                               str(sigs.get(key)) + ", built " + expected +
                               "); regenerate it, run --write-sigs, or set S01E03_ALLOW_ESTIMATE=1")


def shot_start(d, i, n=None):
    """Real scene-time start of shot i from real_shot_times.json for scene n.
    Raises if the table is missing/mismatched/unsigned/stale; S01E03_ALLOW_ESTIMATE=1 falls back to the estimator.
    --write-sigs uses the table even if the old signature is stale (the director is refreshing it)."""
    if n is None:
        return _estimate_scene_time(d, i)
    key = str(n)

    def _warn_est(msg):
        print("WARNING: " + msg + " -> estimator")
        return _estimate_scene_time(d, i)

    if not REAL_SHOT_TIMES:
        if ALLOW_ESTIMATE:
            return _warn_est("real_shot_times.json missing")
        raise RuntimeError("real_shot_times.json is missing; regenerate it or set S01E03_ALLOW_ESTIMATE=1")
    if key not in REAL_SHOT_TIMES:
        if ALLOW_ESTIMATE:
            return _warn_est("real_shot_times.json has no scene " + key)
        raise RuntimeError("real_shot_times.json has no scene " + key + "; regenerate it or set S01E03_ALLOW_ESTIMATE=1")
    table = REAL_SHOT_TIMES[key]
    if not isinstance(table, list) or len(table) != len(d["shots"]):
        if ALLOW_ESTIMATE:
            return _warn_est("real_shot_times.json scene " + key + " has " + str(len(table) if isinstance(table, list) else "?") +
                             " shots, scene has " + str(len(d["shots"])))
        raise RuntimeError("real_shot_times.json scene " + key + " shot count does not match the built scene; "
                           "regenerate it or set S01E03_ALLOW_ESTIMATE=1")
    problem = _sig_problem(n, d)
    if problem:
        if ALLOW_ESTIMATE:
            return _warn_est(problem)
        if not WRITE_SIGS_MODE:
            raise RuntimeError(problem + "; regenerate it, run --write-sigs, or set S01E03_ALLOW_ESTIMATE=1")
    try:
        return round(float(table[i][0]), 2)
    except (IndexError, TypeError, ValueError) as exc:
        if ALLOW_ESTIMATE:
            return _warn_est("real_shot_times.json scene " + key + " has no usable shot " + str(i))
        raise RuntimeError("real_shot_times.json scene " + key + " has no usable shot " + str(i)) from exc


def check_all_sigs():
    """Strict gate: the signed table must describe every scene that was built (unless refreshing / estimating)."""
    if WRITE_SIGS_MODE or ALLOW_ESTIMATE:
        return
    sigs = REAL_SHOT_TIMES.get("_sig")
    if not isinstance(sigs, dict) or any(s not in sigs for s in SIG_SCENES):
        raise RuntimeError("real_shot_times.json is unsigned or does not cover scenes 1..10; "
                           "regenerate it, run --write-sigs, or set S01E03_ALLOW_ESTIMATE=1")
    stale = [str(n) for n, d in sorted(SCENES.items()) if sigs.get(str(n)) != scene_sig(d)]
    if stale:
        raise RuntimeError("real_shot_times.json is stale for scene(s) " + ", ".join(stale) +
                           "; regenerate it, run --write-sigs, or set S01E03_ALLOW_ESTIMATE=1")


def write_sigs():
    """Refresh the _sig block (and the honest-limits _meta) from the scenes just built, keeping every timing key
    untouched."""
    path = os.path.join(_HERE, "real_shot_times.json")
    if not os.path.exists(path):
        raise RuntimeError("cannot write signatures: real_shot_times.json is missing")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    data["_sig"] = {str(n): scene_sig(d) for n, d in sorted(SCENES.items())}
    cache_dir = os.path.join(_HERE, "work", "voice", "cache")
    n_wav = None
    if os.path.isdir(cache_dir):
        n_wav = sum(1 for _root, _dirs, files in os.walk(cache_dir) for f in files if f.endswith(".wav"))
    data["_meta"] = {"note": "exported from frames.json after voice generation",
                     "engine_diff": os.environ.get("S01E03_ENGINE_DIFF_SHA", "unrecorded"),
                     "voice_cache_files": n_wav}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    print("wrote _sig for scenes", sorted(data["_sig"]))


def save(n, d):
    lines = [(l[0], l[1]) for s in d["shots"] for l in s.get("lines", [])]
    SCRIPT.append((n, d["chapter"], lines, est(d)))
    SCENES[n] = d
    # Files are written only after validate_table() has checked every scene (all-or-nothing gate).


def write_outputs():
    os.makedirs(EP, exist_ok=True)
    for n, _chapter, _lines, _est in SCRIPT:
        with open(f"{EP}/scene_{n:02d}.json", "w", encoding="utf-8") as fh:
            json.dump(SCENES[n], fh, indent=1, ensure_ascii=False)
    index = [{"scene": n, "chapter": c, "est_s": e, "lines": [{"who": w, "text": t} for w, t in ls]}
             for n, c, ls, e in SCRIPT]
    with open(f"{EP}/_script_index.json", "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=1, ensure_ascii=False)


def run_table_selftest():
    """In-memory validation self-test. Never writes scene files or _script_index.json."""
    global REAL_SHOT_TIMES, ALLOW_ESTIMATE

    original = REAL_SHOT_TIMES
    original_allow = ALLOW_ESTIMATE
    ALLOW_ESTIMATE = False

    def _run_case(n, desc, mutate, expect_raise):
        global REAL_SHOT_TIMES
        data = copy.deepcopy(original)
        if mutate is not None:
            mutate(data)
        REAL_SHOT_TIMES = data
        try:
            if expect_raise:
                try:
                    validate_table(SCENES)
                except RuntimeError:
                    print("PASS case " + str(n) + ": " + desc)
                    return True
                else:
                    print("FAIL case " + str(n) + ": " + desc + " (no RuntimeError)")
                    return False
            else:
                try:
                    validate_table(SCENES)
                except RuntimeError as exc:
                    print("FAIL case " + str(n) + ": " + desc + " (" + str(exc) + ")")
                    return False
                else:
                    print("PASS case " + str(n) + ": " + desc)
                    return True
        finally:
            REAL_SHOT_TIMES = original

    ok = True
    try:
        ok = _run_case(0, "real table passes", None, False) and ok
        ok = _run_case(1, "deleting scene 4 key raises", lambda data: data.pop("4", None), True) and ok
        ok = _run_case(2, "removing the last shot of scene 7 raises", lambda data: data["7"].pop(), True) and ok
        ok = _run_case(3, "removing a middle shot of scene 9 raises", lambda data: data["9"].pop(7), True) and ok

        def _gap(data):
            data["2"][3][1] = float(data["2"][3][1]) + 1.0

        ok = _run_case(4, "making scene 2 entries non-contiguous raises", _gap, True) and ok
        ok = _run_case(5, "deleting a _sig scene key raises", lambda data: data["_sig"].pop("6", None), True) and ok
    finally:
        REAL_SHOT_TIMES = original
        ALLOW_ESTIMATE = original_allow
    return ok


# ================================================================ SCENE 1  cold open (10 s)  = prototype 2d
T0 = 1.6                                                       # approach shot length; bridge starts breaking at scene time T0
s1 = base("Scene 1 - Cold open: The Collapsing Turn", "The Collapsing Turn", "mountain", "sunset", "mountain_wind",
          theme="countryside", fog=0.25, mountains=True, gap=0.3, tail=0.6, gorge=[14.0, 38.0])
s1["actors"] = {"nitro": A("f1", 33, 2.7, 1, "determined"), "rocky": A("monster", 17, 2.1, 1, "worried"),
                "sprinkles": A("icecream", 29.0, 0.2, 1, "determined"), "zippy": A("sports", 24, 1.3, 1, "scared")}
s1["props"] = [{"type": "bridge", "x0": 14.0, "x1": 38.0, "planks": 36, "posts": 7, "z0": -0.4, "z1": 3.4,
                "keys": [[T0 + 0, 0, 0], [T0 + 2.6, 0.3, 0.4]],
                "outer_keys": [[T0 + 0, 0, 0], [T0 + 0.4, 0, 0], [T0 + 1.2, 0.4, 0.35], [T0 + 2.6, 0.7, 0.8]],
                "holes": [[T0 + 1.2, 0.36, 0.5]], "diag": [25.0, T0 + 0.6]},
               {"type": "rockslide", "x": 33.0, "n": 10, "from_shot": 1}]
s1["score"] = [{"cue": "cue_heroic_stand", "from": 2, "to": 2, "vol": 0.42, "start": 0.0, "fade": 0.6, "tail": 0.5}]
s1["shots"] = [
    {"cam": "track", "on": "sprinkles", "dx": 2.0, "zoom": 0.7, "hold": T0, "cut": "hard", "move": {"push": 0.08},
     "moves": {"rocky": {"to_x": 17.0, "speed": 3.0}}, "caption": "CAN THEY SURVIVE THE CANYON BRIDGE?",
     "sfx": [["engine", 0.1, 0.5]]},
    {"cam": "wide", "on": "sprinkles", "dx": 0.0, "zoom": 0.55, "hold": 3.2, "cut": "hard", "move": {"handheld": 3},
     "claw": [{"x": 22.0, "z": 0.4, "y": -0.3, "from_dx": -1.0, "from_dy": -11.0, "at": 0.2, "dur": 0.9, "pose": "palm", "bend": 0.05},
              {"x": 26.5, "z": 0.4, "y": -0.3, "from_dx": 1.0, "from_dy": -11.0, "at": 0.3, "dur": 0.9, "pose": "palm", "bend": 0.05}],
     "moves": {"zippy": {"to_x": 24.2, "speed": 1.0, "sink": {"at": 1.5, "dur": 1.0, "depth": 0.5, "tilt": -0.55, "noclip": True}}},
     "emote": {"zippy": "scared", "sprinkles": "worried", "rocky": "worried"}, "sfx": [["rockslide", 0.0, 0.6]]},
    {"cam": "two", "on": "zippy", "with": "sprinkles", "dx": 1.5, "hold": 4.4, "cut": "hard", "move": {"push": 0.1}, "freeze": 0.4,
     "claw": [{"x": 22.0, "z": 0.4, "y": -0.3, "from_dx": -1.0, "from_dy": -11.0, "at": 0.0, "dur": 0.1, "pose": "palm", "bend": 0.05},
              {"x": 26.5, "z": 0.4, "y": -0.3, "from_dx": 1.0, "from_dy": -11.0, "at": 0.0, "dur": 0.1, "pose": "palm", "bend": 0.05}],
     "moves": {"zippy": {"to_x": 24.2, "speed": 1.0, "sink": {"at": 0.0, "dur": 0.1, "depth": 0.5, "tilt": -0.55, "noclip": True}}},
     "emote": {"zippy": "scared", "sprinkles": "determined"},
     "lines": [L("zippy", "Outer lane's giving way! Keep going!", "scared"), L("sprinkles", "Never! Hold on to me, Zippy!", "determined")]},
]
s1["note"] = "T0=1.6 is the approach duration; bridge sink/hole/tilt times are fixed relative to T0. Speech timing estimates only."
save(1, s1)

# ================================================================ SCENE 2  Beyond the Rusty Gate (50 s)
s2 = base("Scene 2 - Beyond the Rusty Gate", "Beyond the Rusty Gate", "speedway", "morning", "mountain_wind", fog=0.35,
          mountains=True, start_x=-2.0)
s2["actors"] = {"sprinkles": A("icecream", -34, 1.2, 1, "normal"), "buster": A("bus", -44, 2.6, 1, "worried"),
                "zippy": A("sports", -52, 0.3, 1, "normal"), "rocky": A("monster", -62, 2.0, 1, "normal")}
s2["props"] = [{"type": "speedgate", "x": -14.0, "z": 1.3, "half": 6.4, "open_shot": 0, "open_dt": 0.0, "open_dur": 0.2},
               {"type": "scoreboard", "x": 22.0, "z": 4.4, "w": 7.0, "texts": [[0.0, "LAP 5 OF 5\nFINAL LAP"]]},
               {"type": "trophy_case", "x": 36.0, "z": 3.4}]
s2["score"] = [{"cue": "cue_wonder", "from": 0, "to": 1, "vol": 0.4, "start": 0.0, "fade": 1.2, "tail": 1.0},
               {"cue": "cue_grandpa_memory", "from": 7, "to": 8, "vol": 0.35, "start": 0.0, "fade": 1.0, "tail": 1.2}]
s2["shots"] = [
    {"cam": "wide", "zoom": 0.5, "dx": -6, "hold": 7.2, "cut": "hard", "move": {"pan": 2}, "kraggor": KR_CALM,
     "moves": {"sprinkles": {"to_x": 2, "speed": 9.5}, "buster": {"to_x": -8, "speed": 9.5}, "zippy": {"to_x": -16, "speed": 9.5}, "rocky": {"to_x": -26, "speed": 9.5}},
     "sfx": [["engine", 0.3, 0.4], ["gate_creak", 0.0, 0.4]]},
    {"cam": "group", "group": ["sprinkles", "buster", "zippy", "rocky"], "dx": -4, "move": {"push": 0.05}, "emote": {"zippy": "surprised"},
     "lines": [L("zippy", "Whoa... sixty years of dust and not one tire track!", "surprised")]},
    {"cam": "wide", "zoom": 0.5, "dx": 12, "hold": 4.2, "move": {"pan": 2.5},
     "moves": {"sprinkles": {"to_x": 14, "speed": 8}, "buster": {"to_x": 6, "speed": 8}, "zippy": {"to_x": -2, "speed": 8}, "rocky": {"to_x": -10, "speed": 8}}},
    {"look": {"x": 22.0, "z": 4.4, "y": 4.6, "fit": 9.0}, "hold": 3.4, "move": {"push": 0.08}, "sfx": [["drone", 0.0, 0.3]]},
    {"cam": "two", "on": "rocky", "with": "zippy", "dx": 2, "move": {"push": 0.06}, "emote": {"rocky": "worried"},
     "lines": [L("rocky", "The scoreboard's stuck on the final lap... like it's waiting for us.", "worried")]},
    {"cam": "medium", "on": "sprinkles", "move": {"pull": 0.06}, "emote": {"sprinkles": "excited"},
     "lines": [L("sprinkles", "And the trophy case has a keyhole... our key might open it!", "excited")]},
    {"look": {"x": 36.0, "z": 3.4, "y": 1.8, "fit": 6.0}, "hold": 3.2, "move": {"push": 0.08}, "sfx": [["key_glint", 0.6, 0.5]]},
    {"cam": "wide", "zoom": 0.5, "dx": 18, "hold": 3.6, "move": {"pull": 0.1}, "moves": {"sprinkles": {"to_x": 20, "speed": 5}, "buster": {"to_x": 12, "speed": 4}},
     "emote": {"buster": "sad"}},
    {"cam": "medium", "on": "buster", "beat": "emotion", "move": {"push": 0.05}, "emote": {"buster": "sad"},
     "lines": [L("buster", "Don't open that case yet, Sprinkles. That scoreboard stopped for me... over sixty years ago.", "sad")]},
    {"cam": "two", "on": "sprinkles", "with": "buster", "dx": 2, "move": {"push": 0.1}, "emote": {"sprinkles": "worried", "buster": "sad"},
     "lines": [L("sprinkles", "You were here, Buster? What happened?", "worried"), L("buster", "Come back to town with me. Your grandpa left a box in your garage.", "sad")]},
]
save(2, s2)

# ================================================================ SCENE 3  The Torn Poster & Rescue Team (50 s)
s3 = base("Scene 3 - The Torn Poster", "The Torn Poster", "garage", "noon", "room", theme="city")
s3["actors"] = {"sprinkles": A("icecream", -4, 1.2, 1, "normal"), "buster": A("bus", 6.5, 2.6, -1, "worried"),
                "zippy": A("sports", 14.5, 0.4, -1, "normal"), "siren": A("police", 22, 1.6, -1, "determined"),
                "hydro": A("firetruck", 31, 2.6, -1, "determined"), "nitro": A("f1", 40, 0.5, -1, "normal"), "tilly": A("taxi", 48, 2.8, -1, "happy")}
s3["props"] = [{"type": "poster", "x": 3.0, "z": 3.9, "y": 3.0, "text": "CHAMPIONSHIP FINAL\n5 LAPS"}]
s3["score"] = [{"cue": "cue_grandpa_memory", "from": 0, "to": 2, "vol": 0.35, "start": 0.0, "fade": 1.0, "tail": 1.0}]
s3["shots"] = [
    {"cam": "wide", "zoom": 0.5, "dx": 10, "hold": 6.5, "cut": "hard", "move": {"pan": 2}},
    {"cam": "two", "on": "sprinkles", "with": "buster", "dx": 3, "move": {"push": 0.06}, "emote": {"sprinkles": "excited"},
     "lines": [L("sprinkles", "Grandpa's dusty old box has a poster... Championship Final, five laps!", "excited")]},
    {"cam": "group", "group": ["siren", "hydro", "zippy"], "dx": 4, "move": {"pull": 0.05}, "emote": {"siren": "worried"},
     "lines": [L("siren", "That speedway's been shut for decades. The track needs a safety check first.", "worried"),
               L("hydro", "I'm Hydro, Rescue Team. We check each sector before it opens for racing.", "calm")]},
    {"cam": "wide", "zoom": 0.5, "dx": 12, "hold": 4.6, "move": {"pan": 2}, "emote": {"nitro": "angry"}},
    {"cam": "two", "on": "nitro", "with": "tilly", "dx": 2, "move": {"push": 0.05},
     "lines": [L("nitro", "Fine, inspect it. I'm still the fastest car in town.", "angry")]},
    {"cam": "close", "on": "buster", "beat": "emotion", "move": {"push": 0.08}, "emote": {"buster": "sad"},
     "lines": [L("buster", "Your grandpa and I raced there long ago. I was number seven.", "sad")]},
    {"cam": "group", "group": ["sprinkles", "zippy", "siren", "hydro"], "dx": 1, "move": {"pull": 0.05}, "emote": {"zippy": "surprised"},
     "lines": [L("zippy", "You raced Grandpa Cone?!", "surprised")]},
    {"cam": "wide", "zoom": 0.5, "dx": 14, "hold": 4.4, "move": {"pan": 2}, "emote": {"siren": "worried", "hydro": "determined", "nitro": "normal", "tilly": "worried"}},
    {"look": {"x": 3.0, "z": 3.9, "y": 3.0, "fit": 5.0}, "hold": 6.0, "move": {"push": 0.1},
     "lines": [L("buster", "Fifth and final lap. Your grandpa was right in front of me. That close.", "sad")], "sfx": [["thunder_roll", 4.6, 0.4]]},
]
save(3, s3)

# ================================================================ SCENE 4  Flashback: Grandpa's Final Lap (55 s)
s4 = base("Scene 4 - Flashback: Grandpa's Final Lap", "Grandpa's Final Lap", "mountain", "night", "storm", theme="countryside",
          fog=0.25, mountains=True, tint="sepia", rain=True, lightning=[[2, 0.3], [3, 0.4]], gap=0.5, tail=1.0)
GP = {"vk": "icecream", "color": [0.93, 0.86, 0.7], "accent": [0.62, 0.42, 0.25], "mustache": False}
s4["actors"] = {"grandpa_cone": A(GP["vk"], -30, 0.8, 1, "determined", color=GP["color"], accent=GP["accent"], mustache=False),
                "buster": A("bus", -44, 2.2, 1, "determined")}
s4["props"] = [{"type": "rockslide", "x": -8.0, "n": 10, "from_shot": 2},
               {"type": "kraggor_small", "x": 6.0, "z": 3.6, "face": -1, "height": 3.0, "mode": "scared", "from_shot": 8, "to_shot": 9},
               {"type": "key", "x": 4.5, "z": 3.2, "from_shot": 8, "to_shot": 9}]
s4["score"] = [{"cue": "cue_grandpa_memory", "from": 7, "to": 10, "vol": 0.4, "start": 0.0, "fade": 0.8, "tail": 0.6}]
s4["shots"] = [
    {"cam": "wide", "zoom": 0.6, "hold": 7.0, "cut": "hard", "move": {"pan": 2}, "caption": "OVER SIXTY YEARS AGO. LAP 5 OF 5.",
     "moves": {"grandpa_cone": {"to_x": 6, "speed": 9}, "buster": {"to_x": -6, "speed": 9}},
     "sfx": [["engine", 0.2, 0.5], ["thunder_roll", 1.5, 0.5]]},
    {"cam": "two", "on": "grandpa_cone", "with": "buster", "dx": -6, "zoom": 0.9, "move": {"push": 0.05},
     "emote": {"grandpa_cone": "excited", "buster": "laugh"},
     "lines": [L("grandpa_cone", "Last lap, Buster! Stay close!", "excited"), L("buster", "Not for long, Cone!", "laugh")]},
    {"cam": "wide", "zoom": 0.7, "dx": -4, "hold": 4.6, "move": {"pan": 1.5}, "emote": {"buster": "scared"},
     "moves": {"buster": {"to_x": -9, "speed": 3.0, "stuck": True}, "grandpa_cone": {"to_x": 14, "speed": 8}},
     "sfx": [["thunder_roll", 0.1, 0.8], ["rockslide", 0.3, 0.6]]},
    {"cam": "track", "on": "buster", "dx": 2.5, "zoom": 1.05, "move": {"handheld": 5}, "emote": {"buster": "scared"},
     "lines": [L("buster", "Cone! The road fell out from under me... I'm stuck!", "scared")]},
    {"cam": "low", "on": "grandpa_cone", "beat": "emotion", "hold": 3.8, "move": {"push": 0.1}, "emote": {"grandpa_cone": "determined"},
     "moves": {"grandpa_cone": {"to_x": 15, "face": -1, "squash": 0.4, "at": 0.0}}},
    {"cam": "two", "on": "grandpa_cone", "with": "buster", "dx": -6, "beat": "emotion", "move": {"push": 0.08}, "emote": {"grandpa_cone": "determined"},
     "lines": [L("grandpa_cone", "I'm not leaving you, Buster!", "determined")]},
    {"cam": "wide", "zoom": 0.7, "dx": 2, "hold": 4.2, "move": {"pan": 2},
     "contact": [["grandpa_cone", "buster"]],
     "moves": {"grandpa_cone": {"to_x": -2.5, "to_z": 2.2, "speed": 8, "face": -1}},
     "emote": {"grandpa_cone": "determined", "buster": "worried"}, "sfx": [["chain_rattle", 0.0, 0.5]]},
    {"cam": "wide", "zoom": 0.7, "dx": 1, "hold": 3.2, "move": {"pan": 1.5},
     "moves": {"grandpa_cone": {"to_x": 6.5, "to_z": 2.2, "speed": 6, "reverse": True, "face": -1},
               "buster": {"to_x": 0, "to_z": 2.2, "speed": 6, "delay": 0.0}},
     "sfx": [["chain_rattle", 0.0, 0.5]]},
    {"look": {"x": 5.5, "z": 3.4, "y": 1.5, "fit": 6.0}, "hold": 5.0, "move": {"push": 0.08}, "sfx": [["key_glint", 0.8, 0.5], ["whimper", 0.3, 0.4]]},
    {"cam": "two", "on": "grandpa_cone", "with": "buster", "dx": 1, "zoom": 0.9, "move": {"push": 0.08},
     "contact": [["grandpa_cone", "buster"]],
     "emote": {"grandpa_cone": "happy", "buster": "sad"},
     "lines": [L("grandpa_cone", "A trophy gets dusty, Buster. A friend never does.", "calm"), L("buster", "Thank you... Cone.", "sad")]},
    {"cam": "wide", "zoom": 0.6, "dx": 3, "hold": 6.0, "move": {"crane": 1.2, "pull": 0.1},
     "contact": [["grandpa_cone", "buster"]],
     "moves": {"grandpa_cone": {"to_x": 9.5, "speed": 6}, "buster": {"to_x": 3, "speed": 6}}, "punch": True, "emote": {"grandpa_cone": "happy"}},
]
s4["note"] = ("Same lane, true bumper contact (centre distance 6.5 m = bus half 3.7 + ice-cream half 2.8), towed. Cue covers only last four shots. Motion and cue lengths are timing "
              "ESTIMATES until real speech exists.")
save(4, s4)

# ================================================================ SCENE 5  Safety Sprint (60 s)
s5 = base("Scene 5 - The Sector 1-2 Safety Sprint", "The Safety Sprint", "speedway", "noon", "mountain_wind", mountains=True,
          finish=108.0, start_x=-4.0, ramps=[[72.0, 78.0, 1.4]])
s5["actors"] = {"sprinkles": A("icecream", 0, -0.2, 1, "determined"), "rocky": A("monster", -9, 0.9, 1, "normal"),
                "zippy": A("sports", -17, 2.0, 1, "excited"), "nitro": A("f1", -27, 3.1, 1, "normal"),
                "siren": A("police", 94, 1.0, -1, "determined"), "hydro": A("firetruck", 108, 2.6, -1, "determined")}
s5["props"] = [{"type": "mud", "x": 44.0, "w": 8.0}, {"type": "barricade", "x": 120.0, "from_shot": 0, "to_shot": 99}]
s5["score"] = [{"cue": "cue_sprinkles_theme", "from": 5, "to": 8, "vol": 0.38, "start": 0.0, "fade": 0.8, "tail": 1.0}]
s5["shots"] = [
    {"cam": "medium", "on": "sprinkles", "beat": "emotion", "cut": "hard", "move": {"push": 0.06}, "emote": {"sprinkles": "determined"},
     "lines": [L("sprinkles", "He traded his last lap for you, Buster. Now we finish that lap for him... together!", "determined")]},
    {"cam": "two", "on": "hydro", "with": "siren", "dx": -5, "move": {"push": 0.05}, "emote": {"hydro": "determined", "siren": "normal"},
     "lines": [L("hydro", "Sector Three stays closed until it's inspected. Short loop only: Sectors One and Two.", "calm"),
               L("siren", "Nice and safe. Four cars, one short loop. Racers... start your engines!", "determined")]},
    {"cam": "wide", "zoom": 0.45, "dx": -12, "hold": 3.8, "move": {"pan": 2},
     "lines": [L("announcer", "Sprinkles, Nitro, Zippy and Rocky... one short loop, and the mud is already hungry!", "excited")]},
    # shot 3: on sprinkles dx -6 zoom .46 -> camx=x_spr-6; at 3.4 s spr 26 -> screen 1255, zippy 30 -> 1369,
    # nitro 34 -> 1489: both visibly ahead; all three inside. Arrival: nitro 61m/40=2.31s, zippy 47m/30=2.36s <= 3.4s.
    {"cam": "track", "on": "sprinkles", "dx": -6, "zoom": 0.46, "hold": 3.4, "speedlines": True, "move": {"push": 0.05},
     "moves": {"nitro": {"to_x": 34, "speed": 40}, "zippy": {"to_x": 30, "speed": 30}, "rocky": {"to_x": 30, "speed": 12}, "sprinkles": {"to_x": 26, "speed": 11}},
     "lines": [L("announcer2", "And it's Nitro and Zippy out front!", "excited")], "sfx": [["engine", 0.0, 0.6]]},
    # shot 4: explicit on nitro dx -3.5 zoom .6 -> stuck camx=56-3.5=52.5 (frame 33..72m at z3.1); mud 40..48,
    # zippy 49 -> 773px, nitro 56 -> 960px. Arrival: nitro 22m/10=3.15s, zippy 19m/10=2.78s <= 4.6s.
    {"cam": "wide", "on": "nitro", "zoom": 0.6, "dx": -3.5, "hold": 4.6, "move": {"pan": 1.5}, "emote": {"nitro": "scared", "zippy": "scared"},
     "moves": {"nitro": {"to_x": 56, "speed": 10, "stuck": True, "dizzy": True}, "zippy": {"to_x": 49, "speed": 10, "stuck": True, "dizzy": True}},
     "lines": [L("announcer", "Mud! The track swallowed their speed!", "surprised")], "sfx": [["splat", 0.4, 0.6]]},
    {"cam": "track", "on": "sprinkles", "dx": 3, "zoom": 1.0, "hold": 3.6, "move": {"push": 0.05},
     "moves": {"sprinkles": {"to_x": 58, "speed": 14}, "rocky": {"to_x": 56, "speed": 12}}, "emote": {"sprinkles": "determined"},
     "lines": [L("sprinkles", "Slow is smooth... and smooth is fast.", "calm")]},
    # shot 6: on sprinkles dx 2 zoom .5 -> camx=spr+2 (frame about spr-16..spr+20 at z=-.2). At the line (spr 105..108)
    # rocky ~92 is behind, finish 108 and barricade 120 in view. Spr 54m/20=3.78s, line ~2.94s; rocky 44m/14=4.33s <=6.2s.
    {"cam": "wide", "on": "sprinkles", "zoom": 0.5, "dx": 2, "hold": 6.2, "move": {"pan": 2.5},
     "moves": {"sprinkles": {"to_x": 112, "speed": 20}, "rocky": {"to_x": 100, "speed": 14}},
     "sfx": [["engine", 0.0, 0.6], ["car_boing", 1.4, 0.5]]},
    {"cam": "two", "on": "nitro", "with": "zippy", "dx": 3, "move": {"push": 0.05}, "emote": {"nitro": "angry", "zippy": "surprised"},
     "lines": [L("nitro", "That ice cream truck just dusted me in the mud?!", "angry"), L("zippy", "An ice cream truck outdrove me... my paint will never live this down!", "surprised")]},
    # shot 8: on sprinkles dx 1 zoom .6 -> camx=spr+1=113; frame 98..128m at z=-.2; finish 108 -> 639px, spr 112 -> 896px.
    {"cam": "wide", "on": "sprinkles", "zoom": 0.6, "dx": 1.0, "hold": 5.0, "move": {"pan": 1.5}, "emote": {"hydro": "proud", "siren": "proud"},
     "lines": [L("announcer2", "Sprinkles rolls first in the Safety Sprint!", "excited")], "sfx": [["honk_cheer", 0.5, 0.6]]},
    {"cam": "group", "group": ["sprinkles", "siren", "hydro"], "dx": 0, "move": {"pull": 0.06}, "kraggor": {"mode": "calm", "sx": 0.88, "sy": 0.6, "scale": 0.45, "stand": True, "gz": 6.5},
     "emote": {"sprinkles": "worried"}, "punch": True,
     "lines": [L("sprinkles", "The short loop works... Now how do we clear Sector Three for Grandpa's real final lap?", "worried")]},
]
save(5, s5)

# ================================================================ SCENE 6  Clearing & Testing the Canyon Bridge (50 s)
s6 = base("Scene 6 - Clearing & Testing the Canyon Bridge", "Testing the Bridge", "mountain", "sunset", "mountain_wind", mountains=True,
          fog=0.25, gorge=[14.0, 38.0], gap=0.45)
s6["actors"] = {"hydro": A("firetruck", 22, 2.6, 1, "determined"), "rocky": A("monster", 31, 2.0, 1, "determined"),
                "siren": A("police", 6, 1.0, 1, "determined"), "sprinkles": A("icecream", -6, 0.3, 1, "normal"),
                "zippy": A("sports", -20, 1.8, 1, "angry"), "nitro": A("f1", -34, 2.8, 1, "normal"), "buster": A("bus", -48, 0.6, 1, "normal")}
BR6 = {"type": "bridge", "x0": 14.0, "x1": 38.0, "planks": 36, "posts": 7, "z0": -0.4, "z1": 3.4,
       "keys": [[0, 0, 0], [6.0, 0.12, 0.1]], "outer_keys": [[0, 0, 0], [6.0, 0.12, 0.1]],
       "holes": [], "diag": [25.0, 999.0]}
PICK6 = 1.0                                                     # scene seconds: shot 0 starts at scene time 0
BOULDER6 = {"type": "boulder", "x": -12.0, "z": 1.4, "r": 1.4,
            "hide_t": PICK6}                                    # world boulder is handed to the overlay rock at pick_at
RESCUE6 = {"type": "rescue", "z": 2.6, "spray": {"t0": 5.0, "t1": 9.0, "from": [24.0, 1.6], "dir": [0.0, -0.9]},
           "beacon": {"x": 22.0, "y": 2.9, "t0": 20.0, "t1": 60.0}}
s6["props"] = [BR6, BOULDER6, RESCUE6]
s6["score"] = [{"cue": "cue_heroic_stand", "from": 7, "to": 7, "vol": 0.4, "start": 0.0, "fade": 1.0, "tail": 0.8}]
# ---- SHOT 0 FRAMING (1920x1080 "h": k(z)=10500/(100+9z), CX=540, screen_x = 960 + (x-camx)*k(z)*zoom) -------------
# The Kraggor overlay is drawn in SCREEN space (identity matrix, sx*W) while the boulder is a world prop: only a
# STATIC camera keeps them locked together, so this shot has no pan/push (the other shots carry the movement).
# camera: wide, on "zippy" + dx 10; zippy is placed at x=-26 for THIS shot, so camx = -26+10 = -16, exactly the
# original camera. Shot 1 resets zippy to -20 / Sprinkles to -6 so the rest of the scene is unchanged.
#   zippy screen x = 960 - 10*k(1.8)*.55 = 960 - 10*90.36*.55 = 463 px; body ~359..567, clear of the giant's
#   left hand (957 overhead / 929 relaxed) and torso (967..1106).
#   Sprinkles is moved to x=10, z=.3 -> screen x = 960 + 26*102.24*.55 = 2422 px (body ~2265..2580), out of frame
#   on the right, so the pink truck cannot cover Kraggor at all.
#   Nitro x=-34, z=2.8 -> screen x ~130 px; body ~24..236, also left of the giant. All other cars are off-frame.
# Kraggor "hold": arms=0.8 is only the RELAXED pose (arms out, hands at the tips). story25d.kraggor_hold_pose raises
# BOTH forearms up and inward for the rock: the hands end above the head at +-1.05 rock radii (957..1116 px), the
# rock's underside just clears the head (no chest overlap).
# A7 (owner: "he reads as standing in FRONT of the road; a car nose passes through his body"): with stand=True the
# FEET must sit on the far ground line and the letterbox fit must not move him. Before the fix
# story25d.kraggor_base_y ADDED "bar - rock_top" = +239 px on top of the stand base, so the feet landed at 830 px =
# 0.77 H (near pavement). Now the fit is skipped for stand=True (hold WITHOUT stand keeps it; other modes never
# reach it) and the SCALE keeps the rock under the bar - the rock radius is screen-space (r*H), so a smaller giant
# needs a smaller scale.
#   camera pivot = ground_y(1) - 2.3*k(1) = 432 + 4.6*96.3303 - 2.3*96.3303 = 653.56 px (no hill, no push/punch
#   on this shot: _Z = zoom = 0.55). screen_y(world y) = 540 + (y - 653.56)*0.55.
#   gz=6.0 -> k(6) = 10500/154 = 68.1818 -> ground_y(6) = 432 + 4.6*68.1818 = 745.64 px
#          -> FEET = 540 + (745.64-653.56)*0.55 = 590.64 px = 0.547 H  (road band 0.57-0.63 H, so the feet are
#             at/above the far kerb; 590.64 px is also where the far ground fill starts, and it is drawn after him)
#   scale 0.28 -> sc = 0.28; neck base = 590.64 - (1.2+19.2)*40*0.28 = 590.64 - 228.48 = 362.16 px
#             -> feet = 362.16 + 0.28*816 = 590.64 px (never translated by the fit)
#             -> head top = 362.16 + 0.28*40*(1.2-9.5) = 269.2 px; torso top = 335.3 px; hands (hold) = 238.8 px
#   rock: r = .07*1080 = 75.6 px; r_u = 75.6/(40*0.28) = 6.75 head units; cy_u = -9.5-.15-6.75 = -16.4
#             -> centre = 362.16 + 0.28*40*(1.2-16.4) = 191.9 px; top = 116.3 px (letterbox bar 91.8);
#                bottom = 267.5 px, just over the head (269.2) - the whole rock is inside the frame.
#   fit limit: feet - 40*sc*(19.2+9.5+0.15) - 2*75.6 >= 101.8  ->  sc <= (590.64-151.2-101.8)/1154 = 0.2925.
#             (0.40 would put the rock top at 590.64-1154*0.40-151.2 = -22 px, cut off; 0.28 leaves ~14 px of margin.)
#   relaxed hands x = 1036.8 +- 9.6*40*0.28 = 929..1144 px at y = 362.16 + 11.2*(1.2+1.8) = 395.8 px.
# A7 check of the OTHER Kraggor specs - all non-hold, so kraggor_base_y already returns the stand base untouched:
#   sc.5 shot 9  calm  gz 6.5, group zoom ~0.72 -> feet 540+(736.7-653.56)*0.72 = 600 px = 0.556 H
#   sc.7 shot 0  calm  gz 6.5, wide zoom .45    -> feet 540+(736.7-653.56)*0.45 = 577 px = 0.535 H
#   sc.7 shot 1  calm  gz 5.5, wide zoom .60    -> feet 540+(756.2-653.56)*0.60 = 602 px = 0.557 H
#   sc.10 sh 2   smile gz 6.0, wide zoom .50    -> feet 540+(745.64-653.56)*.50 = 586 px = 0.543 H
#   sc.10 sh 5/6 munch gz 6.0, group zoom .47   -> feet 583 px = 0.540 H
#   all at the far ground line -> no geometry change needed there.
#
# BOULDER HANDOVER (no visible pop): world boulder x=-12, z=1.4, r=1.4.
#   k(1.4)=10500/(100+12.6)=10500/112.6=93.2504 px/m; zoom=.55.
#   screen x = 960 + (-12-(-16))*93.2504*.55 = 960 + 4*51.2877 = 1165.15 px.
#   ground_y(1.4)=432+4.6*93.2504=860.95 px; camera pivot = 653.56 px.
#   screen ground y = 540+(860.95-653.56)*.55 = 654.07 px; 3D boulder centre sits 0.8r=1.12 m above ground:
#   centre y = 654.07 - 1.12*93.2504*.55 = 596.63 px; screen radius = 1.4*51.2877 = 71.8 px.
#   overlay rock r=.07*1080 = 75.6 px starts at from=[1165.15/1920, 596.63/1080]=[0.60685, 0.55243].
#   pick_at=1.0, pick_dur=1.2, hold_dur=.8, throw_dur=1.2 (+0.55 s arm return) -> last action 4.75 s <= hold 7.0 s.
#   The rock leaves the hands at 1.0+1.2+0.8+0.30*1.2 = 3.36 s on ONE continuous arc (peak kept under the
#   letterbox) and exits the right edge; sfx: stomp_near at the pick, rockslide at the throw.
s6["shots"] = [
    {"cam": "wide", "on": "zippy", "dx": 10, "zoom": 0.55, "hold": 7.0, "cut": "hard",
     "kraggor": {"mode": "hold", "sx": 0.54, "sy": 0.55, "scale": 0.28, "arms": 0.8, "stand": True, "gz": 6.0,
                 "rock": {"from": [0.60685, 0.55243], "pick_at": PICK6, "pick_dur": 1.2, "hold_dur": 0.8,
                          "throw_dur": 1.2, "throw_to": [1.25, 0.55], "arc": 0.18, "r": 0.07}},
     "moves": {"zippy": {"x": -26}, "sprinkles": {"x": 10}},
     "sfx": [["stomp_near", 1.0, 0.5], ["rockslide", 3.36, 0.4]]},
    {"cam": "two", "on": "zippy", "with": "nitro", "dx": 2, "move": {"push": 0.05}, "emote": {"zippy": "angry"},
     "moves": {"zippy": {"x": -20}, "sprinkles": {"x": -6}},
     "lines": [L("zippy", "I'm a racecar, not a broom!", "angry"), L("nitro", "Less complaining, more sweeping!", "normal")]},
    {"cam": "wide", "zoom": 0.6, "dx": 8, "hold": 4.4, "move": {"push": 0.05}, "emote": {"hydro": "determined"}, "sfx": [["engine", 0.0, 0.4]]},
    {"look": {"x": 24.0, "z": 1.4, "y": 0.3, "fit": 8.0}, "hold": 4.0, "move": {"push": 0.06}, "sfx": [["engine", 0.0, 0.3]]},
    {"cam": "wide", "zoom": 0.55, "dx": 6, "hold": 6.2, "move": {"pan": 2},
     "moves": {"hydro": {"to_x": 25, "speed": 3.0}, "rocky": {"to_x": 33, "speed": 3.0, "delay": 0.8}},
     "sfx": [["engine", 0.0, 0.4]]},
    {"cam": "two", "on": "rocky", "with": "hydro", "dx": 2, "move": {"push": 0.05}, "emote": {"rocky": "proud"},
     "lines": [L("rocky", "Eight tons of monster truck, and she didn't even creak.", "proud")]},
    {"cam": "medium", "on": "hydro", "move": {"pull": 0.05}, "emote": {"hydro": "determined"},
     "lines": [L("hydro", "Beams hold two heavy trucks at a time. Cross slowly, no passing on the span. I can't test for falling rock.", "calm")]},
    {"cam": "medium", "on": "siren", "beat": "emotion", "move": {"push": 0.08}, "emote": {"siren": "determined"},
     "lines": [L("siren", "Structure checked and cleared. Prepare for one official tribute lap... the Grandpa Cone Memorial Lap!", "determined")]},
]
BOULDER6["hide_t"] = round(shot_start(s6, 0, 6) + PICK6, 2)
BR6["keys"] = [[0.0, 0.0, 0.0], [round(shot_start(s6, 4, 6) + 1.5, 2), 0.12, 0.1]]
RESCUE6["spray"]["t0"] = round(shot_start(s6, 2, 6) + 0.4, 2)
RESCUE6["spray"]["t1"] = round(RESCUE6["spray"]["t0"] + 3.6, 2)
RESCUE6["beacon"]["t0"] = round(shot_start(s6, 7, 6), 2)
RESCUE6["beacon"]["t1"] = round(RESCUE6["beacon"]["t0"] + 40.0, 2)
s6["note"] = "Boulder handover at pick_at=1.0 s; arms lift it overhead between both hands (story25d.kraggor_hold_pose). Spray start, bridge sag and beacon start use REAL shot starts from real_shot_times.json."
save(6, s6)

# ================================================================ SCENE 7  Starting Grid: The Memorial Lap (45 s)
s7 = base("Scene 7 - Starting Grid: The Memorial Lap", "The Memorial Lap", "speedway", "sunset", "mountain_wind", mountains=True, start_x=-12.0)
s7["actors"] = {"sprinkles": A("icecream", -22, 0.3, 1, "determined"), "zippy": A("sports", -31, 1.2, 1, "excited"),
                "nitro": A("f1", -40, 2.0, 1, "normal"), "rocky": A("monster", -49, 2.8, 1, "normal"),
                "buster": A("bus", -4, 3.1, -1, "worried"), "tilly": A("taxi", 6, 3.1, -1, "happy"), "siren": A("police", 16, 1.0, -1, "proud"),
                "hydro": A("firetruck", 53, 3.2, -1, "determined")}
SB7 = {"type": "scoreboard", "x": 0.0, "z": 4.6, "w": 7.0, "texts": [[0.0, "LAP 5 OF 5\nFINAL LAP"], [8.0, "LAP 5 OF 5\nMEMORIAL LAP"]]}
RESCUE7 = {"type": "rescue", "z": 3.2, "beacon": {"x": 52.0, "y": 2.9, "t0": 0.0, "t1": 99.0},
           "winch": {"t0": 1.0, "dur": 0.8, "taut_t": 1.9, "release_t": 999.0, "sag": 0.8,
                     "from": [49.2, 1.4], "to": [57.0, 0.2]}}
s7["props"] = [SB7, RESCUE7]
s7["score"] = [{"cue": "cue_sprinkles_theme", "from": 4, "to": 6, "vol": 0.4, "start": 0.0, "fade": 1.0, "tail": 1.0}]
s7["shots"] = [
    {"cam": "wide", "zoom": 0.45, "dx": -22, "hold": 6.0, "cut": "hard", "move": {"pan": 2},
     "kraggor": {"mode": "calm", "sx": 0.6, "sy": 0.55, "scale": 0.55, "stand": True, "gz": 6.5},
     "sfx": [["engine", 0.2, 0.4]]},
    {"cam": "wide", "zoom": 0.6, "dx": 12, "hold": 3.8, "lift": -0.4, "move": {"pan": 1.2},
     "kraggor": {"mode": "calm", "sx": 0.6, "sy": 0.55, "scale": 0.55, "stand": True, "gz": 6.5,
                 "walk": {"to_sx": 1.3, "dur": 3.0}}},
    {"cam": "medium", "on": "buster", "beat": "emotion", "hold": 6.0, "move": {"push": 0.05}, "emote": {"buster": "proud"},
     "sfx": [["key_click", 1.2, 0.5], ["chain_rattle", 0.4, 0.5]]},
    {"cam": "medium", "on": "hydro", "move": {"push": 0.05}, "emote": {"hydro": "determined"},
     "lines": [L("hydro", "Rescue team in position at the bridge access. Winch anchored. If a car slips, I'm on the span in seconds.", "calm")]},
    {"cam": "wide", "zoom": 0.45, "dx": 4, "hold": 5.0, "move": {"pull": 0.08}, "emote": {"tilly": "happy"}, "sfx": [["honk_cheer", 0.4, 0.5]]},
    {"cam": "group", "group": ["sprinkles", "zippy", "nitro", "rocky"], "dx": -4, "move": {"push": 0.05}, "emote": {"nitro": "angry", "sprinkles": "determined"},
     "lines": [L("nitro", "Beat you to the bridge, ice cream. Then we crawl across, no passing.", "angry"), L("sprinkles", "I'm ready. This lap belongs to Grandpa.", "determined")]},
    {"cam": "low", "on": "siren", "beat": "emotion", "move": {"push": 0.1}, "emote": {"siren": "proud"},
     "lines": [L("siren", "For Grandpa Cone, and every racer who puts friends first. Ready... set... GO!", "determined")]},
    {"cam": "track", "on": "sprinkles", "dx": 3, "zoom": 1.0, "hold": 6.0, "speedlines": True, "move": {"push": 0.05},
     "moves": {"sprinkles": {"to_x": 6, "speed": 12}, "zippy": {"to_x": -4, "speed": 14}, "nitro": {"to_x": -12, "speed": 14}, "rocky": {"to_x": -22, "speed": 14}},
     "sfx": [["engine", 0.0, 0.7]]},
]
SB7["texts"] = [[0.0, "LAP 5 OF 5\nFINAL LAP"],
                [round(shot_start(s7, 2, 7) + 1.0, 2), "LAP 5 OF 5\nMEMORIAL LAP"]]
RESCUE7["winch"]["t0"] = round(shot_start(s7, 3, 7) + 1.0, 2)
RESCUE7["winch"]["taut_t"] = round(shot_start(s7, 3, 7) + 1.9, 2)
s7["note"] = ("Scoreboard swap and winch t0/taut_t use REAL shot starts from real_shot_times.json. "
              "anchor: ground bollard at winch from.x, drum on the truck; Kraggor walks along the access road toward the gorge rim and out of frame (walk to_sx 1.3); the next shots show the empty road, the arms appear only in the bridge shots.")
save(7, s7)

# ================================================================ SCENE 8  The Forgotten Speedway Final (60 s)
s8 = base("Scene 8 - The Forgotten Speedway Final", "The Final Lap", "mountain", "sunset", "mountain_wind", mountains=True, fog=0.25,
          gorge=[14.0, 38.0], ramps=[[-40.0, -30.0, 1.6]])
s8["actors"] = {"nitro": A("f1", -90, 2.8, 1, "determined"), "zippy": A("sports", -96, 1.3, 1, "determined"),
                "sprinkles": A("icecream", -112, 0.2, 1, "determined"), "rocky": A("monster", -120, 2.1, 1, "normal")}
BR8 = {"type": "bridge", "x0": 14.0, "x1": 38.0, "planks": 36, "posts": 7, "z0": -0.4, "z1": 3.4,
       "keys": [[0, 0, 0]], "outer_keys": [[0, 0, 0]], "holes": [], "diag": [25.0, 0.0]}
s8["props"] = [BR8, {"type": "rockslide", "x": 33.0, "n": 10, "from_shot": 11}]
s8["score"] = [{"cue": "cue_heroic_stand", "from": 1, "to": 5, "vol": 0.4, "start": 0.0, "fade": 0.8, "tail": 0.8}]
s8["shots"] = [
    {"cam": "wide", "zoom": 0.45, "dx": -92, "hold": 5.0, "cut": "hard", "move": {"pan": 2},
     "lines": [L("announcer", "Green flag on the Memorial Lap! Nitro out front, Zippy right there!", "excited")],
     "moves": {"nitro": {"to_x": -64, "speed": 12}, "zippy": {"to_x": -70, "speed": 12}, "sprinkles": {"to_x": -88, "speed": 12}, "rocky": {"to_x": -96, "speed": 12}}},
    {"cam": "track", "on": "nitro", "dx": 4, "zoom": 1.0, "hold": 5.0, "speedlines": True, "move": {"push": 0.05},
     "moves": {"nitro": {"to_x": -44, "speed": 16}, "zippy": {"to_x": -49, "speed": 19}, "sprinkles": {"to_x": -66, "speed": 18}, "rocky": {"to_x": -76, "speed": 17}}},
    {"cam": "wide", "zoom": 0.6, "dx": -44, "hold": 5.0, "lift": 0.4, "move": {"pan": 2},
     "lines": [L("announcer2", "The hill looms! Sprinkles is dropping back!", "surprised")],
     "moves": {"nitro": {"to_x": -34, "speed": 6}, "zippy": {"to_x": -39, "speed": 6}, "sprinkles": {"to_x": -50, "speed": 10}, "rocky": {"to_x": -60, "speed": 10}}},
    {"cam": "low", "on": "sprinkles", "beat": "emotion", "hold": 2.8, "move": {"push": 0.1}, "emote": {"sprinkles": "determined"},
     "lines": [L("sprinkles", "Build your speed before the hill... and keep rolling!", "determined")]},
    {"cam": "track", "on": "rocky", "dx": 3, "zoom": 1.0, "hold": 4.0, "speedlines": True, "move": {"push": 0.05}, "emote": {"rocky": "excited"},
     "lines": [L("rocky", "Keep rolling, Sprinkles!", "excited")],
     "moves": {"rocky": {"to_x": -52, "speed": 12}, "sprinkles": {"to_x": -44, "speed": 12}}},
    {"cam": "track", "on": "sprinkles", "dx": 3, "zoom": 1.1, "hold": 3.0, "speedlines": True, "move": {"push": 0.08},
     "moves": {"sprinkles": {"to_x": -22, "speed": 22}, "nitro": {"to_x": -26, "speed": 7}, "zippy": {"to_x": -31, "speed": 7}, "rocky": {"to_x": -40, "speed": 14}}},
    {"cam": "wide", "on": "sprinkles", "zoom": 0.6, "dx": -20, "hold": 5.0, "move": {"pan": 2}, "emote": {"nitro": "angry"},
     "lines": [L("announcer", "Sprinkles roars past Nitro at the summit!", "excited")],
     "moves": {"sprinkles": {"to_x": 8, "speed": 22}, "nitro": {"to_x": 2, "speed": 22}, "zippy": {"to_x": -4, "speed": 22}, "rocky": {"to_x": -14, "speed": 22}}},
    {"cam": "wide", "zoom": 0.6, "dx": -2, "hold": 4.6, "move": {"pan": 2}, "emote": {"sprinkles": "determined", "nitro": "angry"},
     "moves": {"nitro": {"to_x": 24, "speed": 8}, "sprinkles": {"to_x": 18, "speed": 8}, "zippy": {"to_x": 8, "speed": 10}, "rocky": {"to_x": 0, "speed": 10}},
     "sfx": [["engine", 0.0, 0.5]]},
    {"cam": "track", "on": "nitro", "dx": 3, "zoom": 1.0, "hold": 4.4, "speedlines": True, "move": {"push": 0.05}, "emote": {"nitro": "angry"},
     "lines": [L("nitro", "Nice try, ice cream! Nobody passes me twice!", "angry")]},
    {"cam": "two", "on": "nitro", "with": "zippy", "dx": 3, "hold": 4.4, "move": {"push": 0.05}, "emote": {"nitro": "angry", "zippy": "worried"},
     "lines": [L("zippy", "Nitro, she's right behind you again!", "worried"), L("nitro", "Not for long. Into the canyon!", "angry")]},
    {"cam": "wide", "on": "rocky", "zoom": 0.6, "dx": 6, "hold": 7.2, "move": {"pan": 1.5},
     "moves": {"nitro": {"to_x": 33, "to_z": 2.7, "speed": 4.0},
               "sprinkles": {"to_x": 29, "to_z": 0.2, "speed": 4.0},
               "zippy": {"to_x": 24.2, "to_z": 1.3, "speed": 4.0},
               "rocky": {"to_x": 17, "to_z": 2.1, "speed": 4.0}},
     "sfx": [["engine", 0.0, 0.4]]},
    {"cam": "wide", "on": "sprinkles", "dx": 0.0, "zoom": 0.55, "hold": 3.2, "cut": "hard", "move": {"handheld": 3},
     "claw": [{"x": 22.0, "z": 0.4, "y": -0.3, "from_dx": -1.0, "from_dy": -11.0, "at": 0.2, "dur": 0.9, "pose": "palm", "bend": 0.05},
              {"x": 26.5, "z": 0.4, "y": -0.3, "from_dx": 1.0, "from_dy": -11.0, "at": 0.3, "dur": 0.9, "pose": "palm", "bend": 0.05}],
     "moves": {"zippy": {"to_x": 24.2, "speed": 1.0, "sink": {"at": 1.5, "dur": 1.0, "depth": 0.5, "tilt": -0.55, "noclip": True}}},
     "emote": {"zippy": "scared", "sprinkles": "worried", "rocky": "worried"}, "sfx": [["rockslide", 0.0, 0.6]]},
]
T8 = shot_start(s8, len(s8["shots"]) - 1, 8)
BR8.update({"keys": [[T8, 0.0, 0.0], [T8 + 2.6, 0.3, 0.4]],
            "outer_keys": [[T8, 0.0, 0.0], [T8 + 0.4, 0.0, 0.0], [T8 + 1.2, 0.4, 0.35], [T8 + 2.6, 0.7, 0.8]],
            "holes": [[T8 + 1.2, 0.36, 0.5]], "diag": [25.0, T8 + 0.6]})
s8["props"][1]["from_shot"] = len(s8["shots"]) - 1
s8["note"] = f"Bridge collapse timeline starts at T8={T8} s (REAL start of the last shot); events end at T8+2.6 s, inside the 3.2 s real shot."
save(8, s8)

# ================================================================ SCENE 9  The Champion's Choice (rescue, no new dialogue)
s9 = base("Scene 9 - The Champion's Choice", "The Champion's Choice", "mountain", "sunset", "mountain_wind", mountains=True, fog=0.25,
          gorge=[14.0, 38.0])
s9["actors"] = {"nitro": A("f1", 33, 2.7, 1, "worried"), "zippy": A("sports", 24.2, 1.3, 1, "scared"),
                "sprinkles": A("icecream", 29.0, 0.2, 1, "determined"), "rocky": A("monster", 17, 2.1, 1, "worried"),
                "hydro": A("firetruck", 53, 3.2, -1, "determined")}
RESCUE9 = {"type": "rescue", "z": 3.2,
           "winch": {"t0": 0.5, "dur": 0.8, "taut_t": 18.6, "release_t": 35.7, "sag": 1.2,
                     "from": [49.2, 1.4], "to": [24.8, 0.9], "from_z": 3.2, "to_z": 1.3},
           "beacon": {"x": 52.0, "y": 2.9, "t0": 0.0, "t1": 99.0}}
s9["props"] = [{"type": "bridge", "x0": 14.0, "x1": 38.0, "planks": 36, "posts": 7, "z0": -0.4, "z1": 3.4,
                "keys": [[0, 0.3, 0.4], [60.0, 0.3, 0.4]],
                "outer_keys": [[0, 0.7, 0.8], [60.0, 0.7, 0.8]],
                "holes": [[-3.0, 0.36, 0.5]], "diag": [25.0, -3.0]},
               RESCUE9]
CL9_BASE = [{"x": 22.0, "z": 0.4, "y": -0.3, "from_dx": -1.0, "from_dy": -11.0, "at": -1.0, "dur": 0.1},
       {"x": 26.5, "z": 0.4, "y": -0.3, "from_dx": 1.0, "from_dy": -11.0, "at": -1.0, "dur": 0.1}]


def claws9(b0, b1=None, at=0.0, dur=0.8):
    """Palm pose (open hand under the girder); the forearm bends more while it takes the load."""
    return [dict(c, pose="palm", bend=b0, bend_to=(b0 if b1 is None else b1), bend_at=at, bend_dur=dur) for c in CL9_BASE]


CL9 = claws9(0.05)                      # shots 0-3
CL9_LOAD = claws9(0.05, 0.28, 0.2)      # shot 4: the cable tensions (19.23 s) and the arms take the load
CL9_HELD = claws9(0.28)                 # shots 5-6
CL9_REL = claws9(0.28, 0.10, 0.8)       # shot 7: cable released at +0.8 s, the load eases
CL9_AFTER = claws9(0.10)                # shots 8-11
ZIP_TIP = {"at": 0.0, "dur": 0.0, "depth": 0.5, "tilt": -0.55, "noclip": True}
s9["score"] = [{"cue": "cue_heroic_stand", "from": 0, "to": 3, "vol": 0.42, "start": 0.0, "fade": 0.8, "tail": 0.8}]
# ---- FRAMING UP TO THE CABLE RELEASE (h projection: screen_x = 960 + (x-camx)*k(z)*zoom, k=10500/(100+9z)) -----
# Elements that must share the frame: Zippy tipped at x=24.2 (z=1.3), both claws at x=22.0 / 26.5 (z=0.4,
# paw radius 0.8 m -> left extent x=21.2) and the bridge hole x=22.6..26, plus Nitro's exit run x=33 -> 43.5
# (+2.3 m body -> 45.8) and, when the shot size allows, Hydro at x=53.
# k(0.2)=103.14  k(0.4)=101.35  k(1.3)=94.00  k(2.1)=88.31  k(2.7)=84.47  k(3.2)=81.52
#  shot 0  wide on zippy  dx  9, zoom .55 -> cam 33.2: left edge at z=0.4 = 33.2-17.2 = 16.0 (claw 21.2 in),
#          right edge at z=2.7 = 33.2+20.7 = 53.9 (Nitro's run-out 45.8 in). Was: mean of all actors + 8 = 39.2,
#          which put the left claw exactly on the left edge (screen x = 0).
#  shot 1  wide on nitro (x=43.5 after shot 0) dx -7, zoom .55 -> cam 36.5: left edge 19.3, right edge 57.2.
#  shot 2  medium on sprinkles, zoom 1.0 (medium ignores dx): half width 9.5 m at z=0.4 -> claws 22/26.5, Zippy,
#          hole stay in frame (was 1.6 -> half width 5.9 m, the left claw was cut).
#  shot 3  was a "two" of rocky (17) and hydro (53): mid 35, zoom 1.25 -> half width 9.4 m, BOTH speakers outside.
#          Now wide on rocky + dx 16, zoom .5 -> cam 33: x 16.2..49.8 at z=2.1, claws/Zippy/Nitro in, Hydro in at
#          z=3.2 (right edge 56.6).
#  shot 4  wide on sprinkles dx 2, zoom .6 -> cam 31: left edge 17.2 (claw 21.2 in), right edge at z=2.7 = 49.9.
#  shot 5  low on zippy (was sprinkles): the low angle looks at the tipped car BETWEEN the two claws.
#  shot 6  was a "two" of hydro (53) and sprinkles (29): mid 41, zoom 1.25 -> empty frame. Now wide on sprinkles
#          + dx 8, zoom .55 -> cam 37: x 19.8..54.2 at z=0.4, 58.4 at z=3.2 -> rescue tableau + Hydro speaking.
s9["shots"] = [
    {"cam": "wide", "on": "zippy", "dx": 9, "zoom": 0.55, "hold": 3.0, "cut": "hard", "move": {"pan": 2}, "claw": CL9,
     "moves": {"nitro": {"to_x": 43.5, "to_z": 3.2, "speed": 6.0},   # far edge of the inner lane: evacuees use z 2.0
               "zippy": {"to_x": 24.2, "speed": 1.0, "sink": ZIP_TIP}}},
    {"cam": "wide", "on": "nitro", "dx": -7, "zoom": 0.55, "hold": 4.6, "move": {"pan": 2}, "claw": CL9,
     "moves": {"zippy": {"to_x": 24.2, "speed": 1.0, "sink": ZIP_TIP}},
     "lines": [L("nitro", "I'm clear on this side. I'll keep the exit open!", "determined")]},
    {"cam": "medium", "on": "sprinkles", "zoom": 1.0, "beat": "emotion", "move": {"push": 0.08}, "claw": CL9,
     "contact": [["sprinkles", "zippy"]],
     "moves": {"sprinkles": {"to_x": 29.1, "to_z": 1.3, "speed": 3.0},
               "zippy": {"to_x": 24.2, "speed": 1.0, "sink": ZIP_TIP}},
     "lines": [L("sprinkles", "Hold the exit, Nitro. We finish together, or not at all.", "determined")]},
    {"cam": "wide", "on": "rocky", "dx": 16, "zoom": 0.5, "move": {"push": 0.05}, "emote": {"hydro": "determined"}, "claw": CL9,
     "contact": [["sprinkles", "zippy"]],
     "moves": {"zippy": {"to_x": 24.2, "speed": 1.0, "sink": ZIP_TIP}},
     "lines": [L("hydro", "Cable is on Zippy's tow ring. Stay still. I'm taking the load.", "determined"),
               L("rocky", "Not budging, Hydro!", "determined")]},
    {"cam": "wide", "on": "sprinkles", "dx": 2, "zoom": 0.6, "hold": 3.0, "move": {"pan": 2}, "claw": CL9_LOAD,
     "contact": [["sprinkles", "zippy"]],
     "moves": {"zippy": {"to_x": 24.2, "speed": 1.0, "sink": ZIP_TIP}},
     "sfx": [["chain_rattle", 0.4, 0.5], ["thud_far", 1.5, 0.6], ["chain_rattle", 2.2, 0.5]]},   # A01 fill: short, sourced sounds
    {"cam": "low", "on": "zippy", "beat": "emotion", "hold": 4.0, "move": {"push": 0.12}, "claw": CL9_HELD,
     "contact": [["sprinkles", "zippy"]],
     "moves": {"zippy": {"to_x": 24.2, "speed": 1.0, "sink": ZIP_TIP}},
     "sfx": [["roar", 0.4, 0.7]]},
    {"cam": "wide", "on": "sprinkles", "dx": 8, "zoom": 0.55, "move": {"pull": 0.05}, "emote": {"hydro": "determined"}, "claw": CL9_HELD,
     "moves": {"sprinkles": {"to_x": 30.2, "to_z": 0.2, "speed": 3.0, "delay": 3.0},   # back off 1.1 m: less box overlap with Zippy
               "zippy": {"to_x": 24.2, "speed": 1.0, "sink": ZIP_TIP}},
     "lines": [L("hydro", "Zippy first, then Sprinkles, then Rocky. One car at a time on the inner lane. Steady pace.", "determined")]},
    # Evacuation lane z 2.0 (inner lane, 1.2 m off Nitro at z 3.2). Zippy leaves in the SECOND half of this long shot,
    # so the QA mid-frame sees him still at the ring (he passes behind Sprinkles at z 0.2 only afterwards).
    # Parking: the first car goes farthest, each later car parks nearer in x and z, so nobody passes behind a parked car.
    {"cam": "wide", "on": "zippy", "zoom": 0.55, "dx": 10, "hold": 7.0, "move": {"pan": 2}, "claw": CL9_REL,
     "moves": {"zippy": {"to_x": 41.0, "to_z": 2.0, "speed": 8.0, "delay": 3.2,
                         "sink": {"at": 0.0, "dur": 0.6, "depth": 0.0, "tilt": 0.0,
                                  "from_depth": 0.5, "from_tilt": -0.55, "noclip": True}}},
     "sfx": [["car_boing", 0.0, 0.5], ["chain_rattle", 0.8, 0.5], ["thud_far", 2.1, 0.6], ["engine", 3.2, 0.5],
             ["engine", 4.3, 0.5], ["engine", 5.2, 0.5], ["engine", 6.1, 0.5]]},
    {"cam": "track", "on": "zippy", "dx": 3, "zoom": 1.0, "hold": 3.0, "move": {"push": 0.05}, "claw": CL9_AFTER,
     "moves": {"zippy": {"to_x": 59.0, "to_z": 1.6, "speed": 10.0}},
     "sfx": [["engine", 0.1, 0.5], ["engine", 1.1, 0.5], ["engine", 2.1, 0.5]]},
    {"cam": "wide", "on": "sprinkles", "zoom": 0.55, "dx": 10, "hold": 2.7, "move": {"pan": 2}, "claw": CL9_AFTER,
     "moves": {"sprinkles": {"to_x": 42.0, "to_z": 2.0, "speed": 8.0}},
     "sfx": [["engine", 0.1, 0.5], ["engine", 1.2, 0.5]]},
    {"cam": "track", "on": "sprinkles", "dx": 3, "zoom": 1.0, "hold": 2.5, "move": {"push": 0.05}, "claw": CL9_AFTER,
     "moves": {"sprinkles": {"to_x": 52.5, "to_z": 0.8, "speed": 8.0}},
     "sfx": [["engine", 0.1, 0.5], ["engine", 1.2, 0.5]]},
    {"cam": "wide", "on": "rocky", "zoom": 0.55, "dx": 10, "hold": 5.2, "move": {"pan": 2}, "claw": CL9_AFTER,
     "moves": {"rocky": {"to_x": 42.0, "to_z": 2.0, "speed": 8.0}},
     "sfx": [["thud_far", 0.1, 0.6], ["engine", 0.6, 0.5], ["engine", 1.7, 0.5], ["thud_far", 2.8, 0.6],
             ["engine", 3.2, 0.5], ["engine", 4.2, 0.5]]},
    {"cam": "track", "on": "rocky", "dx": 3, "zoom": 1.0, "hold": 3.0, "move": {"push": 0.05},
     "moves": {"rocky": {"to_x": 46.0, "to_z": 0.0, "speed": 6.0}},
     "sfx": [["steps_far", 0.2, 0.5], ["engine", 0.2, 0.5], ["engine", 1.4, 0.5]]},
    {"cam": "two", "on": "rocky", "with": "sprinkles", "dx": 3, "move": {"push": 0.06}, "emote": {"rocky": "happy"},
     "lines": [L("rocky", "We're all safe on the straightaway. Time to cross that line as a team!", "happy")]},
    {"cam": "wide", "zoom": 0.6, "dx": 10, "hold": 3.0, "move": {"push": 0.08}, "emote": {"sprinkles": "happy"}, "punch": True, "sfx": [["honk_cheer", 0.6, 0.5]]},
]
w_t0 = round(shot_start(s9, 0, 9) + 0.5, 2)
w_taut = round(shot_start(s9, 4, 9) + 0.2, 2)
w_release = round(shot_start(s9, 7, 9) + 0.8, 2)
RESCUE9["winch"]["t0"] = w_t0
RESCUE9["winch"]["taut_t"] = w_taut
RESCUE9["winch"]["release_t"] = w_release
s9["note"] = ("Bridge damage is already finished at t=0 (negative hole/diag times). Winch phases use REAL shot starts from "
              "real_shot_times.json; Zippy is righted in the first 0.6 s, release_t = recovery-shot start + 0.8, the hook "
              "reels back by +1.6, and Zippy drives away at +1.8.")
save(9, s9)

# ================================================================ SCENE 10  The Memorial Trophy (45 s)
# start_x/finish are both 60: the speedway location draws the full-width chequered start/finish line across the lanes.
s10 = base("Scene 10 - The Memorial Trophy", "The Memorial Trophy", "speedway", "night", "mountain_wind", mountains=True,
           start_x=60.0, finish=60.0)
s10["actors"] = {"sprinkles": A("icecream", -34, -0.2, 1, "determined"), "zippy": A("sports", -34, 0.9, 1, "happy"),
                 "rocky": A("monster", -34, 2.0, 1, "happy"), "nitro": A("f1", -34, 3.1, 1, "happy"),
                 "siren": A("police", 80, 1.0, -1, "proud"), "buster": A("bus", 94, 2.6, -1, "proud"),
                 "hydro": A("firetruck", 108, 0.2, -1, "happy"), "tilly": A("taxi", 120, 3.0, -1, "happy")}
SB10 = {"type": "scoreboard", "x": 72.0, "z": 4.6, "w": 7.0,
        "texts": [[0.0, "LAP 5 OF 5\nMEMORIAL LAP"], [4.0, "MEMORIAL LAP\nCOMPLETE"]]}
CASE10 = {"type": "trophy_case", "x": 98.0, "z": 3.6, "drawer_t": 17.0}
BP10 = {"type": "blueprint", "x": 99.4, "z": 4.9, "h": 0.05, "w": 2.0, "from_shot": 7, "to_shot": 7}
s10["props"] = [SB10, CASE10, BP10]
s10["score"] = [{"cue": "cue_kraggor_tender", "from": 2, "to": 4, "vol": 0.38, "start": 0.0, "fade": 1.0, "tail": 1.2}]
# ---- SHOT 0/1 FRAMING: PHOTO-FINISH DIAGONAL (0.5 s spread; owner decision A5) ------------------------------
# Bodies: icecream 5.6 (half 2.8), sports 4.2 (2.1), monster 4.3 (2.15), f1 4.6 (2.3).
# Shot 1 start centres (set by shot 0) are 35.7 / 39.4 / 42.35 / 45.2 (lanes 0..3), i.e. noses
# 38.5 / 41.5 / 44.5 / 47.5: the far lane is already 3 m further ahead per lane.
# All four use the same eased move d=25 m, speed_param=20.0, delay=0:
#   T = 25/20*1.25 + 0.4 = 1.9625 s, x(u)=x0 + 25*S((u)/T), S(p)=p^2(3-2p)   [story25d to_x easing]
# Crossing a finish nose at x=60 means centre = 60-half:
#   lane 0: centre 57.2, f=(57.2-35.7)/25=0.8600 -> S^-1 -> p=0.7648 -> t=1.5009 s
#   lane 1: centre 57.9, f=0.7400 -> p=0.6661 -> t=1.3072 s
#   lane 2: centre 57.85, f=0.6200 -> p=0.5808 -> t=1.1398 s
#   lane 3: centre 57.70, f=0.5000 -> p=0.5000 -> t=0.9813 s
# First nose (lane 3) at 0.981 s, last (lane 0) at 1.501 s -> spread 0.520 s (target 0.5 +/-0.15).
# At that first crossing (p=0.5) positions are exactly noses 51 / 54 / 57 / 60 -> 3 m per lane offset.
# Camera check: at that moment centres are 48.2 / 51.9 / 54.85 / 57.7; group extents (body*0.6) span 44.84..60.46,
# mid=52.65; mean z=1.45 -> k=10500/113.05=92.88; zoom 0.55 gives half-width 960/(92.88*0.55)=18.80 m
# (frame 33.85..71.45). Near lane z=-0.2 half-width 16.32 m (frame 36.33..68.97) and far lane z=3.1
# 21.27 m (31.38..73.92): all four are inside, and the x=60 chequered line is inside the frame.
# COMPLETE is set at shot 1 + 1.75 s (last nose 1.50 s); Siren's line is in shot 2, after that.
s10["shots"] = [
    {"cam": "group", "group": ["sprinkles", "zippy", "rocky", "nitro"], "zoom": 0.5, "dx": 0.0, "hold": 6.0, "cut": "hard", "move": {"pan": 1.5},
     "moves": {"sprinkles": {"to_x": 35.7, "speed": 22.0}, "zippy": {"to_x": 39.4, "speed": 22.0},
               "rocky": {"to_x": 42.35, "speed": 22.0}, "nitro": {"to_x": 45.2, "speed": 22.0}},
     "sfx": [["engine", 0.0, 0.5]]},
    {"cam": "group", "group": ["sprinkles", "zippy", "rocky", "nitro"], "zoom": 0.55, "dx": 0.0, "hold": 4.2, "move": {"push": 0.05}, "emote": {"sprinkles": "happy"},
     "moves": {"sprinkles": {"to_x": 60.7, "speed": 20.0}, "zippy": {"to_x": 64.4, "speed": 20.0},
               "rocky": {"to_x": 67.35, "speed": 20.0}, "nitro": {"to_x": 70.2, "speed": 20.0}},
     "lines": [L("announcer", "Four cars hit the old finish line as one!", "excited")]},
    {"cam": "wide", "on": "sprinkles", "zoom": 0.5, "dx": 0.0, "hold": 5.5, "move": {"pan": 1.5}, "emote": {"siren": "proud"},
     "kraggor": {"mode": "smile", "sx": 0.86, "sy": 0.6, "scale": 0.5, "stand": True, "gz": 6.0},
     "lines": [L("siren", "Memorial Lap complete. No one crossed alone today.", "proud")]},
    {"cam": "two", "on": "sprinkles", "with": "buster", "zoom": 0.5, "dx": 12, "move": {"push": 0.05}, "emote": {"buster": "proud", "sprinkles": "happy"},
     "moves": {"sprinkles": {"to_x": 84, "speed": 6}},
     "lines": [L("sprinkles", "This one's for you, Grandpa. And for you, Buster.", "happy"),
               L("buster", "I'm so proud of you, Sprinkles. And I think Grandpa would be too.", "proud")]},
    {"look": {"x": 98.0, "z": 3.6, "y": 1.8, "fit": 6.5}, "hold": 6.0, "move": {"push": 0.1}, "sfx": [["key_click", 0.8, 0.6], ["key_glint", 0.4, 0.5]]},
    {"cam": "group", "group": ["sprinkles", "siren", "hydro"], "dx": 0.0, "zoom": 0.5, "move": {"pull": 0.05},
     "kraggor": {"mode": "munch", "sx": 0.86, "sy": 0.6, "scale": 0.5, "stand": True, "gz": 6.0},
     "emote": {"hydro": "happy", "siren": "happy"},
     "lines": [L("sprinkles", "Free ice cream for everyone who kept that bridge standing!", "happy")]},
    {"cam": "group", "group": ["sprinkles", "siren", "hydro"], "dx": 0.0, "zoom": 0.5, "hold": 4.0, "move": {"pull": 0.08},
     "kraggor": {"mode": "munch", "sx": 0.86, "sy": 0.6, "scale": 0.5, "stand": True, "gz": 6.0},
     "emote": {"hydro": "happy", "sprinkles": "happy"}},
    {"look": {"x": 98.0, "z": 3.0, "y": 0.4, "fit": 5.0}, "hold": 4.6, "move": {"push": 0.1},
     "lines": [L("narrator", "Grandpa's unfinished lap was finally complete... and his blueprint showed another mountain road waiting to be explored.", "calm")]},
]
SB10["texts"] = [[0.0, "LAP 5 OF 5\nMEMORIAL LAP"],
                 [round(shot_start(s10, 1, 10) + 1.75, 2), "MEMORIAL LAP\nCOMPLETE"]]
CASE10["drawer_t"] = round(shot_start(s10, 4, 10) + 1.0, 2)
BP10["from_shot"] = 7
BP10["to_shot"] = 7
s10["note"] = "Photo-finish spread 0.52 s (first nose 0.98 s, last 1.50 s into shot 1); COMPLETE at +1.75 s, after the last nose and within the 0.5 s finish window."
save(10, s10)

if SELFTEST_TABLE_MODE:
    sys.exit(0 if run_table_selftest() else 1)

# All scenes are now built in memory. Validate the global table BEFORE writing any output.
validate_table(SCENES)
write_outputs()
print("built scenes", [n for n, *_ in SCRIPT], [e for *_, e in SCRIPT])

if WRITE_SIGS_MODE:
    write_sigs()
