"""Trailer Short (1080x1920, ~38 s) for a story3d episode, cut from the finished scenes (owner 2026-10-07).
Every clip is a centre crop of the finished 16:9 scene (clear of the letterbox and the aired subtitle band) shown over a
blurred, darkened copy of itself (the usual Shorts layout), with a big caption per clip, the narrator's voice (Chatterbox,
cached), a quiet score (A10) and a few effects, then an end card with the premiere time. Never uploads anything.
  venv/bin/python generators/story3d/tools/make_trailer.py --episode S01E02_who_is_kraggor
Output: work/story3d/<ep>/trailer/trailer_v.mp4"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "generators", "story"))
FONT = "/root/.fonts/LuckiestGuy-Regular.ttf"
XD = 0.0                                                          # hard cuts (a trailer), the beat comes from the music

# (scene, start s, duration s, caption)  - times are in the finished scene mp4
CLIPS = [(1, 20.5, 3.0, "MIDNIGHT IN MEGAWHEEL TOWN..."),
         (1, 35.4, 2.6, "SOMETHING HUGE IS COMING"),
         (9, 17.2, 2.6, "THE WHOLE TOWN IS AFRAID"),
         (4, 11.3, 2.2, "BUT SPRINKLES REMEMBERS A SMILE..."),
         (4, 14.6, 3.0, "AND A SECRET IN GRANDPA'S BOX"),
         (8, 14.6, 2.8, "A CAVE FULL OF TREASURES"),
         (12, 0.5, 3.0, "THEN THE TOWN SETS A TRAP"),
         (12, 12.0, 3.0, "IS HE REALLY A MONSTER...?"),
         (10, 5.0, 3.0, "...OR JUST LONELY?"),
         (14, 12.0, 3.0, "A NEW FRIEND"),
         (15, 17.0, 3.0, "AND A DOOR TO A NEW ADVENTURE")]
END_HOLD = 7.0
VO = [("Midnight in MegaWheel Town... and something huge is walking the streets.", 0.3),
      ("The whole town is afraid.", 5.7),
      ("But Sprinkles remembers a smile... and a secret in Grandpa's old box.", 8.2),
      ("Now the town is setting a trap.", 16.2),
      ("Is Kraggor really a monster...", 19.3),
      ("...or just lonely?", 22.4),
      ("Who is Kraggor? Find out this Sunday, at one P M Eastern.", 26.0)]


def sh(cmd):
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    a = ap.parse_args()
    import numpy as np
    import story25d as ST
    se = ST.se
    out = os.path.join(ROOT, "work", "story3d", a.episode, "trailer")
    os.makedirs(out, exist_ok=True)
    scenes = os.path.join(ROOT, "work", "story3d", a.episode)
    total = sum(c[2] for c in CLIPS) + END_HOLD
    sr = se.SR

    # ---------------- audio: narrator + quiet score + effects
    items = [(t, ST.line_style("calm"), ST.speaker_voice("narrator"), "studio") for t, _ in VO]
    ST.announcer.prefetch(items, note="trailer")
    vo = np.zeros(int((total + 1) * sr))
    for it, (_, at) in zip(items, VO):
        a_ = ST.announcer.get(*it)
        i = int(at * sr)
        vo[i:i + len(a_)] += a_[:len(vo) - i]
    vo = vo / max(1e-9, float(np.abs(vo).max())) * 0.9
    fx = np.zeros_like(vo)
    for name, at, g in (("steps_far", 0.6, 0.6), ("thud_far", 3.4, 0.5), ("net_drop", 16.4, 0.6), ("kraggor_moan", 20.0, 0.35)):
        s_ = ST.SFX[name]()
        i = int(at * sr)
        fx[i:i + len(s_)] += s_[:len(fx) - i] * g
    wvo, wfx = os.path.join(out, "vo.wav"), os.path.join(out, "fx.wav")
    se.write_wav(wvo, vo[:int(total * sr)])
    se.write_wav(wfx, fx[:int(total * sr)] / max(1e-9, float(np.abs(fx).max())) * 0.8)
    cues = os.path.join(ROOT, "branding", "music", "cues")

    # ---------------- picture
    inputs, fc = [], []
    for i, (n, ss, d, cap) in enumerate(CLIPS):
        inputs += ["-ss", f"{ss}", "-t", f"{d}", "-i", os.path.join(scenes, f"{a.episode}_scene_{n:02d}.mp4")]
        fc.append(f"[{i}:v]crop=1280:720:320:150,fps=30,split[f{i}][b{i}];"
                  f"[b{i}]scale=-2:1920,crop=1080:1920,boxblur=28:6,eq=brightness=-0.22:saturation=1.1[bg{i}];"
                  f"[f{i}]scale=1080:608,setsar=1[fg{i}];"
                  f"[bg{i}][fg{i}]overlay=0:(H-h)/2-80,setsar=1[c{i}]")
    n = len(CLIPS)
    fc.append("".join(f"[c{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v0]")
    # end card: dark gradient + text, appended with a fade
    card = (f"color=c=0x120a2a:s=1080x1920:r=30:d={END_HOLD},format=yuv420p,setsar=1,"
            f"drawtext=fontfile={FONT}:text='WHO IS':fontcolor=0xFFD21F:fontsize=150:borderw=8:bordercolor=black:x=(w-text_w)/2:y=520,"
            f"drawtext=fontfile={FONT}:text='KRAGGOR?':fontcolor=white:fontsize=185:borderw=10:bordercolor=black:x=(w-text_w)/2:y=690,"
            f"drawtext=fontfile={FONT}:text='STORY EP. 2':fontcolor=0xFF8A1F:fontsize=96:borderw=6:bordercolor=black:x=(w-text_w)/2:y=1000,"
            f"drawtext=fontfile={FONT}:text='FULL EPISODE THIS SUNDAY':fontcolor=white:fontsize=72:borderw=5:bordercolor=black:x=(w-text_w)/2:y=1220,"
            f"drawtext=fontfile={FONT}:text='1 PM ET · 10 AM PT':fontcolor=0xFFD21F:fontsize=78:borderw=5:bordercolor=black:x=(w-text_w)/2:y=1330,"
            f"drawtext=fontfile={FONT}:text='MEGAWHEEL ARENA':fontcolor=white:fontsize=64:borderw=4:bordercolor=black:x=(w-text_w)/2:y=1620,"
            f"fade=t=in:d=0.4[endc]")
    fc.append(card)
    fc.append("[v0][endc]concat=n=2:v=1:a=0[v1]")
    # captions (one per clip), top header and channel tag
    t, dt = 0.0, []
    for _, _, d, cap in CLIPS:
        tf = os.path.join(out, f"cap_{len(dt)}.txt")
        open(tf, "w", encoding="utf-8").write(cap.replace("'", "’"))
        fs = min(78, int(960 / (0.58 * len(cap))))                  # Luckiest Guy ~0.58 em per letter: fit 960 px
        dt.append(f"drawtext=fontfile={FONT}:textfile={tf}:fontcolor=white:fontsize={fs}:borderw=7:bordercolor=black:"
                  f"x=(w-text_w)/2:y=1330:enable='between(t,{t + 0.15:.2f},{t + d - 0.1:.2f})'")
        t += d
    head = (f"drawtext=fontfile={FONT}:text='NEW STORY EPISODE':fontcolor=0xFFD21F:fontsize=64:borderw=5:bordercolor=black:"
            f"x=(w-text_w)/2:y=170:enable='lt(t,{t:.2f})',"
            f"drawtext=fontfile={FONT}:text='SUNDAY · 1 PM ET':fontcolor=white:fontsize=84:borderw=6:bordercolor=black:"
            f"x=(w-text_w)/2:y=250:enable='lt(t,{t:.2f})',"
            f"drawtext=fontfile={FONT}:text='MEGAWHEEL ARENA':fontcolor=white:fontsize=52:borderw=4:bordercolor=black:"
            f"x=(w-text_w)/2:y=1700:enable='lt(t,{t:.2f})'")
    fc.append("[v1]" + ",".join(dt) + "," + head + f",fade=t=out:st={total - 0.5:.2f}:d=0.5[v]")
    k = n
    # score: dark cue first, tender cue for the second half; both quiet (A10), the voice is the anchor
    fc.append(f"[{k}:a]atrim=start=6.0:end={6.0 + 19.0},asetpts=PTS-STARTPTS,volume=3.0,afade=t=in:d=0.5,afade=t=out:st=17.5:d=1.5[m1]")
    fc.append(f"[{k + 1}:a]atrim=start=8.0:end={8.0 + total - 18.0},asetpts=PTS-STARTPTS,volume=4.0,adelay=18000|18000,"
              f"afade=t=in:d=1.0,afade=t=out:st={total - 18.0 - 2.0:.2f}:d=2.0[m2]")
    endt = int(sum(c[2] for c in CLIPS) * 1000)                   # the end card starts here: second sting
    fc.append(f"[{k + 2}:a]asplit=2[sa][sb];[sa]adelay=5500|5500,volume=0.5[st1];[sb]adelay={endt}|{endt},volume=0.6[st2]")
    fc.append(f"[{k + 3}:a]aformat=channel_layouts=stereo[vo]")
    fc.append(f"[{k + 4}:a]aformat=channel_layouts=stereo[fx]")
    fc.append("[m1]aformat=channel_layouts=stereo[m1s];[m2]aformat=channel_layouts=stereo[m2s];"
              "[st1]aformat=channel_layouts=stereo[s1s];[st2]aformat=channel_layouts=stereo[s2s];"
              "[m1s][m2s][s1s][s2s][vo][fx]amix=inputs=6:normalize=0:duration=longest,"
              f"loudnorm=I=-15:TP=-1.5:LRA=11,atrim=0:{total:.2f}[a]")
    inputs += ["-i", os.path.join(cues, "cue_kraggor_dark.wav"), "-i", os.path.join(cues, "cue_kraggor_tender.wav"),
               "-i", os.path.join(cues, "cue_kraggor_motif.wav"), "-i", wvo, "-i", wfx]
    dst = os.path.join(out, "trailer_v.mp4")
    sh(["ffmpeg", "-y", "-loglevel", "error"] + inputs + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
                                                           "-t", f"{total:.2f}", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                                                           "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k",
                                                           "-ar", "48000", "-ac", "2", dst])
    print(f"[trailer] {dst} ({total:.1f}s)")


if __name__ == "__main__":
    main()
