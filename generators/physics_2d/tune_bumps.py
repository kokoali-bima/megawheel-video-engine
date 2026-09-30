"""Quick physics-only tuning for the speed-bumps series (no TTS, no render).

Usage: cd /root/video-engine && ./venv/bin/python generators/physics_2d/tune_bumps.py <cfg.json> <seed> [<seed> ...]
<cfg.json> holds BUMP_CFG overrides. Prints, per vehicle, the outcome at each tested speed
(f=flip/pit, s=stuck, w=win + event second).
"""
import json
import sys

import numpy as np

import sim_engine as sv

with open(sys.argv[1]) as fh:
    sv.BUMP_CFG.update(json.load(fh))
for seed in map(int, sys.argv[2:]):
    sv.make_track("bumps", seed)
    print(f"seed {seed}: {[(b[0], b[2]) for b in sv.BUMPS]}")
    for vk in ("sports", "police", "bus", "firetruck", "monster"):
        v = sv.VEHICLES[vk]
        res = []
        for sp in np.linspace(*v["speeds"], 11):
            run = sv.simulate(v, sp)
            ev = run["event"]
            res.append(f"{ev['type'][0]}{ev['t']:.0f}")
        print(f"  {vk:<10} " + " ".join(res))
