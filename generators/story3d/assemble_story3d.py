"""Join story3d scenes into one smooth episode (owner 2026-10-06: "karena ini sepotong, nanti harus smooth waktu
menyambungkan scene sebelumnya ke scene yang ini"). Same result for every agent: the transition of every join is
chosen by a fixed rule from the two scenes' JSON, the audio is cross-faded, and every join is measured.
  rule   time of day or location changes  -> fade through black (1.0 s; audio dips with it)
         same place, same time            -> dissolve (0.6 s; audio cross-fade)
         override per join in stories/<ep>/edit.json: {"story3d": {"order": [1, 2, 3], "joins": {"1-2": ["fadeblack", 1.2]}}}
  sensor per join: FAIL = sound cut abruptly (a > 14 dB drop within 100 ms in the join window), a silence hole
         >= 1.2 s, or a loudness step > 8 dB inside one place (dissolve); WARN = step > 14 dB across a time jump
Runs on Modal (CPU 16) from the final scene files kept in the volume (/vol/final/<ep>/scene_NN.mp4):
  venv-modal/bin/modal run generators/story3d/assemble_story3d.py --episode S01E02_who_is_kraggor --order 1,2 \
      --out work/story3d/S01E02_who_is_kraggor
Writes <out>/<ep>_episode[_<order>].mp4, _chapters.txt, _joins.json; exit 5 if a join fails its sensor."""
import json
import os

CONTRACT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "STYLE_CONTRACT.json"),
                          encoding="utf-8"))["joins"]
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FPS = 30
JOIN = dict(step_db=8.0, step_fade_db=14.0, drop_db=14.0, hole_s=1.2)   # (mirrored in modal_story3d)


def plan_joins(ep, order, overrides):
    joins = []
    for a, b in zip(order[:-1], order[1:]):
        sa = json.load(open(os.path.join(ROOT, "stories", ep, f"scene_{a:02d}.json"), encoding="utf-8"))
        sb = json.load(open(os.path.join(ROOT, "stories", ep, f"scene_{b:02d}.json"), encoding="utf-8"))
        change = (sa.get("time") != sb.get("time")) or (sa.get("location") != sb.get("location"))
        tj, sp = CONTRACT["time_jump"], CONTRACT["same_place"]     # J01: never rushed across a time jump
        j = (dict(kind=tj["kind"], dur=tj["out"], hold=tj["hold"], din=tj["in"]) if change else
             dict(kind=sp["kind"], dur=sp["dur"], hold=0.0, din=0.0))
        ov = overrides.get(f"{a}-{b}")
        if ov:
            j.update(kind=ov[0], dur=float(ov[1]), hold=float(ov[2]) if len(ov) > 2 else 0.0,
                     din=float(ov[3]) if len(ov) > 3 else 0.0)
        if change and tj.get("card"):                              # J03: episode card (dracin style)
            j.update(card=True, label=tj.get("label", "PART"), chime=tj.get("chime", True), num=b,
                     title=sb.get("chapter") or sb.get("title", ""))
        joins.append(dict(a=a, b=b, why="waktu/lokasi berubah" if change else "tempat sama", **j))
    return joins
