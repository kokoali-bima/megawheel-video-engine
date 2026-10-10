#!/usr/bin/env python3
"""LAB ONLY: run the experimental engine (sim_exp.py) with a private registry and output folder, so nothing touches
production (PRODUCTION_REGISTRY.json, renders/megawheel_arena, queue, Drive).

  cd /root/video-engine && venv/bin/python lab/new_obstacles/build_exp.py
  venv/bin/python lab/new_obstacles/run_exp.py --series pendulum --seed 1 [--preview-only]
Output: /root/lab/new_obstacles/out/pending/<date>_<series>_s<seed>/   (previews: /root/lab/new_obstacles/work/previews/)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "..", "..", "generators")
LAB = os.environ.get("MW_LAB_OUT", "/root/lab/new_obstacles")
for sub in ("physics_2d", "variety", "publishing"):
    sys.path.insert(0, os.path.join(GEN, sub))
sys.path.insert(0, HERE)
os.makedirs(f"{LAB}/out", exist_ok=True)

import registry  # noqa: E402

registry.PATH = f"{LAB}/out/REGISTRY_LAB.json"          # private registry: production is never read or written
registry.LOCK = registry.PATH + ".lock"

import sim_exp  # noqa: E402

sim_exp.WORK = f"{LAB}/work"
sim_exp.CHANNEL_DIR = f"{LAB}/out"
sim_exp.OUT_DIR = f"{LAB}/out/pending"
if __name__ == "__main__":
    sim_exp.main()
