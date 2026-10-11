"""LAB: scan wrecking-ball geometry for a ~35-50 % win rate. venv/bin/python lab/new_obstacles/scan_pend.py"""
import itertools
from collections import Counter

import run_exp  # noqa: F401
import sim_exp as se

se.detect_font()
se.load_cast()
VK = ["sports", "bus", "monster", "taxi"]
for piv, amp, pscale in itertools.product((8.8,), (1.2, 1.45), (0.8, 1.0, 1.3)):
    se.PEND_PIV, se.PEND_AMP = piv, amp
    c = Counter()
    for seed in (1, 2):
        se.make_theme(seed, dict(se.SERIES_DEFS["pendulum"]["force_theme"]))
        se.make_track("pendulum", seed)
        for p in se.PENDS:
            p["period"] *= pscale
        for vk in VK:
            v = se.VEHICLES[vk]
            for sp in se.np.linspace(v["speeds"][0], v["speeds"][1], 11):
                ev = se.simulate(v, sp)["event"]["type"]
                c["win" if ev == "win" else ("smash" if ev == "smash" else "other")] += 1
    n = sum(c.values())
    print(f"piv={piv} amp={amp} pscale={pscale}: win {c['win']/n:.0%} smash {c['smash']/n:.0%} other {c['other']/n:.0%}", flush=True)
