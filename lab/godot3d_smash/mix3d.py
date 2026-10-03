"""LAB plan B v5 — sound, commentary, replay and end card for the 3D smash render (international Shorts standard).
events.json (smash3d.gd: t, type, power, sx, sy, who) ->
  * picture: zoomed INSTANT REPLAY of the final KO (smash25d overlay) + the YouTube end card drawn by the SAME cairo
    function as the aired videos (race25d.draw_cta: LIKE / SUBSCRIBE tapped by a hand, bell)
  * sound: sonic logo sting at 0 s, voice-C commentators m1 + f1 (cached Chatterbox lines only, no new spend),
    arena crowd bed + cheers + gasps (smash25d), Sonniss SFX bank (stereo, panned by screen x), shrink horn, CTA taps,
    music bed ducked under the voices, -14 LUFS.
Production modules are imported read-only; nothing in production imports this file.
  venv/bin/python lab/godot3d_smash/mix3d.py --video v.mp4 --events ev.json --out out.mp4"""
import argparse
import json
import os
import random
import subprocess
import sys
import wave

import cairo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for sub in ("generators/physics_2d", "generators/lanes25d", "generators/voice"):
    sys.path.insert(0, os.path.join(ROOT, sub))
import sim_engine as se  # noqa: E402
import race25d as R  # noqa: E402  (draw_cta)
import smash25d as S  # noqa: E402  (crowd, cheer, gasp, horn, schedule_narration)
import announcer as A  # noqa: E402

SR = se.SR
BANK = "/root/lab/sfx/bank"
REPLAY_LEN = 3.6
ZOOM = 1.4
GO_T = 4.3                                                  # smash3d.gd GO_T
rnd = random.Random(7)
_cache = {}


# ------------------------------------------------------------------ audio helpers
def load(path):
    if path not in _cache:
        with wave.open(path) as w:
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
            x = x.reshape(-1, w.getnchannels())
            if x.shape[1] == 1:
                x = np.repeat(x, 2, axis=1)
            if w.getframerate() != SR:
                idx = np.arange(0, len(x) - 1, w.getframerate() / SR)
                x = np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(2)], axis=1)
        _cache[path] = x
    return _cache[path]


def bank(key, pitch=0.08):
    files = json.load(open(os.path.join(BANK, "bank.json")))[key]
    x = load(rnd.choice(files)["file"])
    f = 1.0 + rnd.uniform(-pitch, pitch)
    if abs(f - 1.0) > 1e-3:
        idx = np.arange(0, len(x) - 1, f)
        x = np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(2)], axis=1)
    return x


def st(m):
    return np.stack([m, m], axis=1)


def place(buf, sig, t, g=1.0, pan=0.0):
    if sig.ndim == 1:
        sig = st(sig)
    i0 = int(t * SR)
    if i0 < 0 or i0 >= len(buf):
        return
    m = min(len(sig), len(buf) - i0)
    a = (pan + 1.0) * np.pi / 4.0
    buf[i0:i0 + m, 0] += sig[:m, 0] * g * np.cos(a) * 1.41
    buf[i0:i0 + m, 1] += sig[:m, 1] * g * np.sin(a) * 1.41


def peak(x, target=0.45):
    m = np.max(np.abs(x))
    return x * (target / m) if m > 1e-9 else x


def sounds_for(ev):
    k, p = ev["type"], float(ev.get("power", 1.0))
    if k == "crash":
        return [(0.0, bank("crash_heavy" if p > 0.55 else "crash_light"), 0.45 + 0.55 * p)]
    if k == "chunk":
        return [(0.0, bank("debris", 0.15), 0.45)]
    if k == "fracture":
        return [(0.0, bank("car_destroy", 0.04), 1.0), (0.05, bank("debris"), 0.6), (0.2, st(R.boing()), 0.5)]
    if k == "explode":
        out = [(0.0, bank("explode"), 0.9 * min(1.3, p))]
        if p >= 1.3:
            out.append((0.0, bank("boom_big", 0.03), 0.7))
        return out
    if k in ("missile", "meteor"):
        return [(0.0, bank("whoosh", 0.12), 0.75 if k == "missile" else 0.55)]
    if k == "kraggor":
        return [(0.0, bank("roar", 0.04), 0.9)]
    if k == "stomp":
        return [(0.0, bank("stomp"), 1.0)]
    if k == "shrink":
        return [(0.0, st(S.horn()), 0.45), (0.1, bank("debris", 0.1), 0.6), (0.4, bank("splash"), 0.5)]
    if k == "fall":
        return [(0.0, bank("splash"), 0.9)]
    if k == "shark":
        return [(0.0, bank("splash"), 0.7), (0.05, bank("underwater", 0.05), 0.35)]
    if k == "chomp":
        return [(0.0, bank("crash_heavy"), 0.9), (0.15, bank("splash"), 0.8)]
    return []


def crowd_for(ev):
    k = ev["type"]
    if k == "ko":
        return [(0.2, S.cheer(2.6, 1.1, seed=int(ev["t"] * 10) % 50), 1.0)]
    if k == "chunk":
        return [(0.05, S.gasp(seed=int(ev["t"] * 10) % 50), 0.9)]
    if k in ("kraggor", "meteor", "missile"):
        return [(0.3, S.gasp(seed=31), 0.6)]
    if k == "win":
        return [(0.05, S.cheer(4.5, 1.5, seed=21), 1.0), (1.6, S.cheer(3.0, 1.3, seed=23), 1.0)]
    return []


# ------------------------------------------------------------------ commentary (voice C, cached lines only)
def ok_line(text, style, who):
    return A.cached(text, style, who)


def commentary(events, out, t_win, cta_start, replay_at):
    S.USE_CB = True                                         # S.say -> announcer.get (cache)
    anchors, extras = [], []
    rsg = (se.READY_SET_GO, "clear", "m1")
    if ok_line(*rsg):
        a = A.get(*rsg)
        onset = max(0.42, se.last_word_onset(a))
        anchors.append((max(0.0, GO_T - onset), *rsg))
    win = next((e for e in events if e["type"] == "win"), None)
    if win is not None:
        nick = win.get("who", "").title()
        wl = (f"The winner is... {nick}! Yeah!", "call", "m1")
        if ok_line(*wl):
            anchors.append((out(t_win) + 0.3, *wl))
        extras.append((out(t_win) + 2.2, 2, "What a champion!", "hype", 1.6, "f1"))
    cta = (se.CTA, "norm", "m1")
    if cta_start is not None and ok_line(*cta):
        anchors.append((cta_start + 0.2, *cta))
    if replay_at is not None and ok_line("Let's see that again!", "call", "f1"):
        anchors.append((replay_at + 0.1, "Let's see that again!", "call", "f1"))
    for e in events:
        if e["type"] == "ko" and "|" in e.get("who", ""):
            nick, how = e["who"].split("|")
            line = f"{nick.title()} is out!" if how == "fall" else f"{nick.title()} is down!"
            extras.append((out(e["t"]) + 0.15, 2, line, "hype", 1.3, "f1"))
    hits = ["Oh my goodness! What a hit!", "Ouch! That's gotta hurt!", "Did you see that?"]
    for i, e in enumerate([e for e in events if e["type"] == "chunk"][:3]):
        extras.append((out(e["t"]) + 0.05, 0, hits[i % 3], "hype", 0.6, "f1"))
    extras.append((out(9.0), 1, "Barriers down!", "hype", 0.6, "m1"))
    chaos = {"missile": ("Incoming missile!", "f1"), "kraggor": ("Oh no... it's Kraggor!", "m1"),
             "meteor": ("Meteor shower!", "m1")}
    seen = set()
    for e in events:
        if e["type"] in chaos and e["type"] not in seen:
            seen.add(e["type"])
            extras.append((out(e["t"]) + 0.05, 3, chaos[e["type"]][0], "hype", 1.0, chaos[e["type"]][1]))
    return S.schedule_narration(anchors, extras)


# ------------------------------------------------------------------ overlays (cairo, same drawing code as the aired videos)
def overlay_mov(path, dur, draw):
    n = int(round(dur * 30))
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", "1080x1920",
                           "-r", "30", "-i", "-", "-c:v", "qtrle", path], stdin=subprocess.PIPE)
    for i in range(n):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1080, 1920)
        ctx = cairo.Context(surf)
        draw(ctx, i / 30.0)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close()
    ff.wait()


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
    t_win = next((e["t"] for e in events if e["type"] == "win"), None)
    kos = [e for e in events if e["type"] == "ko"]
    t_ins = (t_win + 3.0) if t_win is not None else None
    replay = bool(kos) and t_ins is not None and t_ins < dur - 1.0
    rl, r0, r1, ko = 0.0, 0.0, 0.0, None
    if replay:
        ko = kos[-1]
        r0 = max(0.0, ko["t"] - 1.4)
        r1 = min(r0 + REPLAY_LEN, dur)
        rl = r1 - r0

    def out(t):                                             # source time -> final time (replay inserted at t_ins)
        return t + rl if (replay and t >= t_ins) else t

    out_dur = dur + rl
    cta_start = out(t_ins) if t_ins is not None and t_ins < dur else None
    work = os.path.dirname(os.path.abspath(a.out))

    # ---- buses (stereo)
    n = int((out_dur + 2) * SR)
    sfx, crowd, narr, logo = (np.zeros((n, 2)) for _ in range(4))
    src_sfx = np.zeros((int((dur + 2) * SR), 2))
    for ev in events:
        pan = float(np.clip((ev.get("sx", 540) / 1080.0 - 0.5) * 1.4, -0.8, 0.8))
        for d, sig, g in sounds_for(ev):
            place(src_sfx, sig, ev["t"] + d, g, pan)
    eng = load(json.load(open(os.path.join(BANK, "bank.json")))["engine_loop"][0]["file"])
    e1 = (t_win or dur) + 0.5
    m = min(len(eng), int((e1 - 1.0) * SR))
    env = np.minimum(1.0, np.minimum(np.arange(m), m - np.arange(m)) / (0.6 * SR))[:, None]
    place(src_sfx, eng[:m] * env, 1.0, 0.16)                 # revving from the jingle, driving after GO
    if replay:
        i_ins, i0, i1 = int(t_ins * SR), int(r0 * SR), int(r1 * SR)
        rep = src_sfx[i0:i1] * 0.8
        place(rep, se.synth_rewind(), 0.0, 0.6)
        src_sfx = np.concatenate([src_sfx[:i_ins], rep, src_sfx[i_ins:]])
    k = min(n, len(src_sfx))
    sfx[:k] += src_sfx[:k]
    for ev in events:
        for d, sig, g in crowd_for(ev):
            place(crowd, sig, out(ev["t"]) + d, g)
    place(crowd, S.cheer(1.8, 0.9, seed=70), GO_T, 0.9)
    bed = np.stack([S.crowd_bed(out_dur + 1, seed=5), S.crowd_bed(out_dur + 1, seed=6)], axis=1)
    if cta_start is not None:
        bed[int(cta_start * SR):] *= 0.45
    place(crowd, bed, 0.0, 0.35)
    if cta_start is not None:                                # end card taps + bell (smash25d)
        for tap in (R.CTA_LIKE_T, R.CTA_SUB_T):
            place(sfx, se.tone(1300, 0.06, "sine", decay=0.02), cta_start + tap, 0.8)
        place(sfx, se.tone(1760, 0.8, "sine", decay=0.35) + se.tone(2637, 0.8, "sine", decay=0.25) * 0.5,
              cta_start + R.CTA_SUB_T + 0.05, 0.6)
    lp = os.path.join(ROOT, "branding", "music", "sonic_logo.wav")    # our sonic logo opens every video
    if os.path.exists(lp):
        place(logo, load(lp), 0.0, 1.0)
    if t_win is not None:
        place(sfx, se.synth_win(), out(t_win), 0.8)
    placed = commentary(events, out, t_win, cta_start, out(t_ins) if replay else None)
    for t0, _, au, _ in placed:
        place(narr, au, t0, 1.0)
    se.make_theme(3)
    bgm = se.synth_bgm(out_dur + 1, style=se.th_time()["music"])
    bgm = st(np.pad(bgm, (0, max(0, n - len(bgm))))[:n])
    bgm *= np.clip((np.arange(n) / SR - 3.4) / 0.8, 0, 1)[:, None]    # music enters after the jingle
    talk = S.box_avg((np.abs(narr[:, 0]) > 0.01).astype(float), int(0.25 * SR))
    duck = (1.0 - (1.0 - 10 ** (-se.DUCK_DB / 20)) * np.clip(talk * 3, 0, 1))[:, None]
    mix = (peak(narr) * se.VOL_NARR + peak(bgm) * 0.55 * duck + peak(logo) * 1.1
           + peak(sfx) * se.VOL_SFX * (0.7 + 0.3 * duck) + peak(crowd) * se.VOL_SFX * 0.75 * (0.6 + 0.4 * duck))
    mix = np.nan_to_num(np.tanh(1.3 * mix) / np.tanh(1.3))[:int(out_dur * SR)]
    wav = a.out.replace(".mp4", ".wav")
    write_wav(wav, mix / max(1e-9, np.max(np.abs(mix))) * 0.95)

    # ---- picture: replay + end card overlays
    cta_mov = os.path.join(work, "_cta.mov")
    rep_mov = os.path.join(work, "_replay.mov")
    tail = dur - t_ins if t_ins is not None else 0.0
    if t_ins is not None and tail > 0.5:
        overlay_mov(cta_mov, tail, lambda ctx, tt: R.draw_cta(ctx, tt))
    if replay and tail > 0.5:
        overlay_mov(rep_mov, rl, lambda ctx, tt: se.draw_replay_overlay(ctx, tt))
        sx, sy = float(ko.get("sx", 540)), float(ko.get("sy", 960))
        cw, ch = 1080 / ZOOM, 1920 / ZOOM
        x = int(np.clip(sx - cw / 2, 0, 1080 - cw))
        y = int(np.clip(sy - ch / 2, 0, 1920 - ch))
        vf = (f"[0:v]trim=0:{t_ins:.3f},setpts=PTS-STARTPTS,setsar=1[a];"
              f"[0:v]trim={r0:.3f}:{r1:.3f},setpts=PTS-STARTPTS,crop={int(cw)}:{int(ch)}:{x}:{y},scale=1080:1920,setsar=1[bz];"
              f"[1:v]setpts=PTS-STARTPTS[ro];[bz][ro]overlay=eof_action=pass,fade=t=in:st=0:d=0.18:color=white[b];"
              f"[0:v]trim={t_ins:.3f},setpts=PTS-STARTPTS,setsar=1[c0];[2:v]setpts=PTS-STARTPTS[co];"
              f"[c0][co]overlay=eof_action=pass[c];[a][b][c]concat=n=3:v=1:a=0[v]")
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", a.video, "-i", rep_mov, "-i", cta_mov, "-i", wav,
               "-filter_complex", vf, "-map", "[v]", "-map", "3:a"]
    elif t_ins is not None and tail > 0.5:
        vf = f"[1:v]setpts=PTS-STARTPTS+{t_ins:.3f}/TB[co];[0:v][co]overlay=eof_action=pass[v]"
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", a.video, "-i", cta_mov, "-i", wav,
               "-filter_complex", vf, "-map", "[v]", "-map", "2:a"]
    else:
        cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", a.video, "-i", wav, "-map", "0:v", "-map", "1:a"]
    subprocess.run(cmd + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                          "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", a.out], check=True)
    for f in (wav, cta_mov, rep_mov):
        if os.path.exists(f):
            os.remove(f)
    lines = [txt for _, _, _, txt in placed]
    print(f"[mix3d] {len(events)} events, replay={'%.1f-%.1f s' % (r0, r1) if replay else 'no'}, "
          f"voice lines={len(lines)} {lines} -> {a.out}")


if __name__ == "__main__":
    main()
