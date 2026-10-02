"""Sound for a Godot render: events (/tmp/godot_events.json from main.gd) -> our synth SFX + music bed + sonic logo.
  venv/bin/python generators/godot_race/godot_mix.py --video in.mp4 --events ev.json --out out.mp4"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "generators", "physics_2d"))
import sim_engine as se  # noqa: E402


def sfx_for(ev):
    k, p = ev["type"], float(ev.get("power", 1.0))
    if k == "explode":
        return [(0.0, se.synth_eruption(seed=47), 1.0), (0.0, se.synth_impact(1.0, seed=9), 0.9)]
    if k == "fracture":
        return [(0.0, se.synth_wall_crash(1.0), 0.8), (0.02, se.synth_shatter(seed=3), 0.6)]
    if k == "crash":
        return [(0.0, se.synth_impact(max(0.4, p), seed=11), 0.5 + 0.5 * p)]
    if k == "meteor":
        return [(0.0, se.sweep(1400, 250, 0.8, 0.5), 0.55)]
    if k == "container":
        return [(0.0, se.sweep(1200, 300, 0.4, 0.5), 0.6)]
    if k == "win":
        logo = os.path.join(se.BASE, "branding", "music", "sonic_logo_mono.wav")
        out = [(0.0, se.synth_win(), 0.9)]
        if os.path.exists(logo):
            out.append((0.5, se.read_wav(logo), 0.8))
        return out
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--events", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    se.make_theme(3)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.video],
                               capture_output=True, text=True).stdout)
    n = int((dur + 1) * se.SR)
    sfx = np.zeros(n)

    def place(sig, t, g):
        i0 = int(t * se.SR)
        if 0 <= i0 < n:
            m = min(len(sig), n - i0)
            sfx[i0:i0 + m] += sig[:m] * g

    events = json.load(open(a.events))["events"] if os.path.exists(a.events) else []
    for ev in events:
        for dt_, sig, g in sfx_for(ev):
            place(sig, ev["t"] + dt_, g)
    place(se.tone(660, 0.12, "sine", decay=0.08), 0.6, 0.5)            # start beeps
    place(se.tone(990, 0.22, "sine", decay=0.12), 1.2, 0.6)
    bgm = se.synth_bgm(dur + 1, style=se.th_time()["music"])
    bgm = np.pad(bgm, (0, max(0, n - len(bgm))))[:n]
    mix = se.peak(bgm) * 0.35 + (se.peak(sfx) * 0.9 if np.max(np.abs(sfx)) > 1e-6 else 0)
    mix = np.nan_to_num(mix)
    mix = np.tanh(1.2 * mix) / np.tanh(1.2)
    mix = mix[:int(dur * se.SR)]
    wav = a.out.replace(".mp4", ".wav")
    se.write_wav(wav, mix / max(1e-9, np.max(np.abs(mix))) * 0.95)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", a.video, "-i", wav, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", a.out], check=True)
    os.remove(wav)
    print(f"[godot-mix] {len(events)} events -> {a.out}")


if __name__ == "__main__":
    main()
