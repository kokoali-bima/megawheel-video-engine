"""Physics-only check of cast members on a series (no TTS, no render).

Usage: cd /root/video-engine && ./venv/bin/python generators/physics_2d/tune_cast.py <series> <vk,vk,...> <seed> [<seed> ...]
Per character and seed: outcome at 11 test speeds (f=flip, p=pit, s=stuck, w=win, t=timeout + event second)
and a verdict whether the character can play its role (fail with event 2.5-11.5 s / win <= 15 s).
Use it before adding a new character to ROSTER.
"""
import sys

import numpy as np

import sim_engine as sv

series, vks, seeds = sys.argv[1], sys.argv[2].split(","), [int(s) for s in sys.argv[3:]]
role = {vk: want for opts, want in sv.ROSTER for vk in opts}
scale = sv.SERIES_DEFS[series].get("speed_scale", 1.0)
for vk in vks:
    v, want = sv.VEHICLES[vk], role.get(vk, "fail")
    ok_seeds = 0
    for seed in seeds:
        sv.make_track(series, seed)
        res, fit = [], 0
        for sp in np.linspace(v["speeds"][0] * scale, v["speeds"][1] * scale, 11):
            ev = sv.simulate(v, sp)["event"]
            res.append(f"{ev['type'][0]}{ev['t']:.0f}")
            good = (ev["type"] == "win") if want == "win" else (ev["type"] not in ("win", "timeout"))
            fit += good and 2.5 <= ev["t"] <= (15 if want == "win" else 11.5)
        ok_seeds += fit > 0
        print(f"{vk:<9} {series} seed {seed:<3} {' '.join(res)}   fits '{want}': {fit}/11")
    print(f"==> {vk}: can play '{want}' on {ok_seeds}/{len(seeds)} seeds\n")
