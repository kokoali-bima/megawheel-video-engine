#!/usr/bin/env python3
"""LAB ONLY: physics-only tuning of the experimental series (no narration, no render).
  venv/bin/python lab/new_obstacles/tune_exp.py pendulum 1 2 3          -> per character: win / fail share over speeds
A series is usable when most characters have BOTH wins and fails (the story needs fail, fail, win)."""
import os
import sys
from collections import Counter

import run_exp  # noqa: F401  (sets sys.path, private registry)
import sim_exp as se

series = sys.argv[1]
seeds = [int(x) for x in sys.argv[2:]] or [1]
se.detect_font()
se.load_cast()
for seed in seeds:
    se.make_theme(seed, dict(se.SERIES_DEFS[series].get("force_theme", {})) or None)
    se.make_track(series, seed)
    print(f"--- {series} seed {seed}: {se.TRACK_ID}")
    tot = Counter()
    for vk, v in se.VEHICLES.items():
        scale = se.SERIES_DEFS[series].get("speed_scale", 1.0)
        c = Counter()
        for sp in se.np.linspace(v["speeds"][0] * scale, v["speeds"][1] * scale, 21):
            ev = se.simulate(v, sp)["event"]
            c["win" if ev["type"] == "win" else ev["type"]] += 1
        tot.update(c)
        print(f"{vk:11s} " + " ".join(f"{k}:{n}" for k, n in sorted(c.items())))
    print("TOTAL", dict(tot))
