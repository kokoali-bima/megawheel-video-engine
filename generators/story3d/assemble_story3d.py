"""Join story3d scenes into one smooth episode (owner 2026-10-06: "karena ini sepotong, nanti harus smooth waktu
menyambungkan scene sebelumnya ke scene yang ini"). Same result for every agent: the transition of every join is
chosen by a fixed rule from the two scenes' JSON, the audio is cross-faded, and every join is measured.
  rule   time of day or location changes  -> fade through black (1.0 s; audio dips with it)
         same place, same time            -> dissolve (0.6 s; audio cross-fade)
         override per join in stories/<ep>/edit.json: {"story3d": {"order": [1, 2, 3], "joins": {"1-2": ["fadeblack", 1.2]}}}
  sensor per join: loudness step (1 s before vs after, outside the transition) <= 8 dB, no silence hole >= 1.2 s,
         a scene's music must not be cut hard (its last 0.3 s must be quieter than its last 1.5 s or silent)
Runs on Modal (CPU 16) from the final scene files kept in the volume (/vol/final/<ep>/scene_NN.mp4):
  venv-modal/bin/modal run generators/story3d/assemble_story3d.py --episode S01E02_who_is_kraggor --order 1,2 \
      --out work/story3d/S01E02_who_is_kraggor
Writes <out>/<ep>_episode[_<order>].mp4, _chapters.txt, _joins.json; exit 5 if a join fails its sensor."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FPS = 30
JOIN = dict(step_db=8.0, hole_s=1.2)


def plan_joins(ep, order, overrides):
    joins = []
    for a, b in zip(order[:-1], order[1:]):
        sa = json.load(open(os.path.join(ROOT, "stories", ep, f"scene_{a:02d}.json"), encoding="utf-8"))
        sb = json.load(open(os.path.join(ROOT, "stories", ep, f"scene_{b:02d}.json"), encoding="utf-8"))
        change = (sa.get("time") != sb.get("time")) or (sa.get("location") != sb.get("location"))
        kind, dur = ("fadeblack", 1.0) if change else ("dissolve", 0.6)
        ov = overrides.get(f"{a}-{b}")
        if ov:
            kind, dur = ov[0], float(ov[1])
        joins.append(dict(a=a, b=b, kind=kind, dur=dur, why="waktu/lokasi berubah" if change else "tempat sama"))
    return joins
