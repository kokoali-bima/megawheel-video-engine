"""LAB helper: physics-only outcome table for any CHALLENGE series of the PRODUCTION engine. venv/bin/python lab/new_obstacles/tune_prod.py gauntlet 1 2 3"""
import os
import sys
from collections import Counter

sys.path[:0] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "generators", p) for p in ("physics_2d", "variety", "publishing", "voice")]
import sim_engine as se

series, seeds = sys.argv[1], [int(x) for x in sys.argv[2:]] or [1]
se.detect_font()
se.load_cast()
for seed in seeds:
    se.make_theme(seed, dict(se.SERIES_DEFS[series].get("force_theme", {})) or None)
    se.make_track(series, seed)
    tot = Counter()
    for vk in ("f1", "sports", "taxi", "monster", "bus", "bigrig"):
        v = se.VEHICLES[vk]
        sc = se.SERIES_DEFS[series].get("speed_scale", 1.0)
        for sp in se.np.linspace(v["speeds"][0] * sc, v["speeds"][1] * sc, 11):
            tot[se.simulate(v, sp)["event"]["type"]] += 1
    print(f"{series} s{seed} {se.TRACK_ID} order={se.TRACK_PARAMS.get('order')} puddles={se.PUDDLES} muds={se.MUDS}: {dict(tot)}", flush=True)
