"""Quick physics-only tuning for the dungeon series (no TTS, no render).
Usage: cd /root/video-engine/generators/physics_2d && ../../venv/bin/python tune_dungeon.py <seed> [<seed> ...]
Prints, per vehicle, the outcome at each tested speed: <type letter><obstacle index> (c=chop s=smash p=pit f=flip w=win)."""
import sys

import numpy as np

import sim_engine as sv

for seed in map(int, sys.argv[1:]):
    sv.THEME = dict(time="noon", weather="clear", location="volcano")
    sv.make_track("dungeon", seed)
    print(f"seed {seed}: axes={[(a['x'], a['period'], a['phase']) for a in sv.AXES]} ogres={[(o['x'], o['period'], o['phase']) for o in sv.OGRES]} pits={[(p[0], p[1]) for p in sv.PITS]} ramps={sv.RAMPS} finish={sv.FINISH_X}")
    for vk in sv.VEHICLES:
        v = sv.VEHICLES[vk]
        res = []
        for sp in np.linspace(*v["speeds"], 14):
            run = sv.simulate(v, sp)
            ev = run["event"]
            res.append(f"{ev['type'][0]}{ev.get('obstacle', '-') if ev['type'] != 'win' else ''}")
        print(f"  {vk:<10} {v['speeds'][0]:.1f}-{v['speeds'][1]:.1f}: " + " ".join(res))
