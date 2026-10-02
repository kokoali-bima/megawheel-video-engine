"""LAB plan B v2 — sound + instant replay for the 3D smash render.
events.json (from smash3d.gd: t, type, power, sx, sy) -> Sonniss SFX bank (stereo, panned by screen x, pitch variation)
+ engine bed + music bed + sonic logo; inserts a zoomed REPLAY of the final KO between the winner banner and end card.
  venv/bin/python lab/godot3d_smash/mix3d.py --video v.mp4 --events ev.json --out out.mp4"""
import argparse
import json
import os
import random
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "generators", "physics_2d"))
import sim_engine as se  # noqa: E402  (music bed + win sting only; read-only use)

SR = 44100
BANK = "/root/lab/sfx/bank"
FONT = "/root/.fonts/LuckiestGuy-Regular.ttf"
REPLAY_LEN = 3.6
ZOOM = 1.4
rnd = random.Random(7)
_cache = {}


def load(path):
    if path not in _cache:
        with wave.open(path) as w:
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
            x = x.reshape(-1, w.getnchannels())
            if x.shape[1] == 1:
                x = np.repeat(x, 2, axis=1)
        _cache[path] = x
    return _cache[path]


def bank(key, pitch=0.08):
    files = json.load(open(os.path.join(BANK, "bank.json")))[key]
    x = load(rnd.choice(files)["file"])
    f = 1.0 + rnd.uniform(-pitch, pitch)                # resample = pitch + speed variation
    if abs(f - 1.0) > 1e-3:
        idx = np.arange(0, len(x) - 1, f)
        x = np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(2)], axis=1)
    return x


def mono2st(m):
    return np.stack([m, m], axis=1)


def sounds_for(ev):
    """-> [(delay, stereo signal, gain)]"""
    k, p = ev["type"], float(ev.get("power", 1.0))
    if k == "crash":
        key = "crash_heavy" if p > 0.55 else "crash_light"
        return [(0.0, bank(key), 0.45 + 0.55 * p)]
    if k == "chunk":
        return [(0.0, bank("debris", 0.15), 0.45)]
    if k == "fracture":
        return [(0.0, bank("car_destroy", 0.04), 1.0), (0.05, bank("debris"), 0.6)]
    if k == "explode":
        out = [(0.0, bank("explode"), 0.9 * min(1.3, p))]
        if p >= 1.3:
            out.append((0.0, bank("boom_big", 0.03), 0.7))
        return out
    if k in ("missile", "meteor"):
        return [(0.0, bank("whoosh", 0.12), 0.75 if k == "missile" else 0.55)]
    if k == "kraggor":
        return [(0.0, bank("roar", 0.04), 0.9)]
    if k == "shrink":
        return [(0.0, bank("debris", 0.1), 0.7), (0.1, bank("stomp", 0.05), 0.45), (0.4, bank("splash"), 0.5)]
    if k == "stomp":
        return [(0.0, bank("stomp"), 1.0)]
    if k == "fall":
        return [(0.0, bank("splash"), 0.9)]
    if k == "shark":
        return [(0.0, bank("splash"), 0.7), (0.05, bank("underwater", 0.05), 0.35)]
    if k == "chomp":
        return [(0.0, bank("crash_heavy"), 0.9), (0.15, bank("splash"), 0.8)]
    if k == "win":
        out = [(0.0, mono2st(se.synth_win()), 0.8)]
        logo = os.path.join(se.BASE, "branding", "music", "sonic_logo_mono.wav")
        if os.path.exists(logo):
            out.append((0.5, mono2st(se.read_wav(logo)), 0.8))
        return out
    return []


def place(buf, sig, t, g, pan=0.0):
    i0 = int(t * SR)
    if i0 < 0 or i0 >= len(buf):
        return
    m = min(len(sig), len(buf) - i0)
    a = (pan + 1.0) * np.pi / 4.0                        # equal-power pan
    buf[i0:i0 + m, 0] += sig[:m, 0] * g * np.cos(a) * 1.41
    buf[i0:i0 + m, 1] += sig[:m, 1] * g * np.sin(a) * 1.41


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--events", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.video],
                               capture_output=True, text=True).stdout)
    events = json.load(open(a.events))["events"] if os.path.exists(a.events) else []
    sfx = np.zeros((int((dur + 2) * SR), 2))
    for ev in events:
        pan = float(np.clip((ev.get("sx", 540) / 1080.0 - 0.5) * 1.4, -0.8, 0.8))
        for d, sig, g in sounds_for(ev):
            place(sfx, sig, ev["t"] + d, g, pan)
    place(sfx, mono2st(se.tone(660, 0.12, "sine", decay=0.08)), 0.6, 0.4)
    place(sfx, mono2st(se.tone(990, 0.22, "sine", decay=0.12)), 1.2, 0.5)
    t_win = next((e["t"] for e in events if e["type"] == "win"), None)
    eng = load(json.load(open(os.path.join(BANK, "bank.json")))["engine_loop"][0]["file"])
    e0, e1 = 2.5, (t_win or dur) + 0.5                   # engine bed while fighting
    n = min(len(eng), int((e1 - e0) * SR))
    env = np.minimum(1.0, np.minimum(np.arange(n), n - np.arange(n)) / (0.6 * SR))[:, None]
    place(sfx, eng[:n] * env, e0, 0.16)

    # ---- instant replay of the final KO
    kos = [e for e in events if e["type"] == "ko"]
    t_ins = (t_win + 3.0) if t_win is not None else None
    replay = bool(kos) and t_ins is not None and t_ins < dur - 1.0
    if replay:
        ko = kos[-1]
        r0 = max(0.0, ko["t"] - 1.4)
        r1 = min(r0 + REPLAY_LEN, dur)
        i_ins, i0, i1 = int(t_ins * SR), int(r0 * SR), int(r1 * SR)
        rep = sfx[i0:i1] * 0.85
        wh = bank("whoosh", 0.0)
        rep[:min(len(rep), len(wh))] += wh[:len(rep)] * 0.6
        sfx = np.concatenate([sfx[:i_ins], rep, sfx[i_ins:]])
        out_dur = dur + (r1 - r0)
    else:
        out_dur = dur
    sfx = sfx[:int(out_dur * SR)]
    se.make_theme(3)
    bgm = se.synth_bgm(out_dur + 1, style=se.th_time()["music"])
    bgm = np.pad(bgm, (0, max(0, len(sfx) - len(bgm))))[:len(sfx)]
    bgm = se.peak(bgm) * 0.32
    mix = mono2st(bgm) + sfx * 0.8
    mix = np.nan_to_num(np.tanh(1.3 * mix) / np.tanh(1.3))
    wav = a.out.replace(".mp4", ".wav")
    write_wav(wav, mix / max(1e-9, np.max(np.abs(mix))) * 0.95)

    if replay:
        sx, sy = float(ko.get("sx", 540)), float(ko.get("sy", 960))
        cw, ch = 1080 / ZOOM, 1920 / ZOOM
        x = int(np.clip(sx - cw / 2, 0, 1080 - cw))
        y = int(np.clip(sy - ch / 2, 0, 1920 - ch))
        vf = (f"[0:v]trim=0:{t_ins:.3f},setpts=PTS-STARTPTS,setsar=1[a];"
              f"[0:v]trim={r0:.3f}:{r1:.3f},setpts=PTS-STARTPTS,crop={int(cw)}:{int(ch)}:{x}:{y},scale=1080:1920,setsar=1,"
              f"fade=t=in:st=0:d=0.18:color=white,"
              f"drawtext=fontfile={FONT}:text='REPLAY':fontsize=120:fontcolor=white:borderw=12:bordercolor=0xd02020:"
              f"x=(w-text_w)/2:y=230,"
              f"drawbox=x=170:y=262:w=56:h=56:color=0xff2020:t=fill:enable='lt(mod(t\\,0.8)\\,0.45)'[b];"
              f"[0:v]trim={t_ins:.3f},setpts=PTS-STARTPTS,setsar=1[c];[a][b][c]concat=n=3:v=1:a=0[v]")
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", a.video, "-i", wav, "-filter_complex", vf, "-map", "[v]",
               "-map", "1:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19"]
    else:
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", a.video, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy"]
    subprocess.run(cmd + ["-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", a.out], check=True)
    os.remove(wav)
    print(f"[mix3d] {len(events)} events, replay={'%.1f-%.1f s' % (r0, r1) if replay else 'no'} -> {a.out}")


if __name__ == "__main__":
    main()
