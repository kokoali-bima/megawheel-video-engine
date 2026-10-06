"""The bookends of a story3d episode (owner 2026-10-07: "merakit ident, previously dan outro"): builds
  scene_00  INFRASOFT ident + the theme song  (the AIRED Ep.1 clips, unchanged: same intro every episode)
  scene_21  "Previously on MegaWheel Arena" recap (~22 s): aired Ep.1 clips (cropped clear of their old subtitles), a soft
            score from the cue library (contract A10: quiet under the narrator) and the narrator's lines (Chatterbox, cached)
  scene_20  the outro song + character intros + next-episode teaser + end screen (story25d scene_20.json, rendered on the VM)
and puts them into the Modal volume (/final/<ep>/scene_NN.mp4) where the assembler finds every scene:
  venv/bin/python generators/story3d/tools/make_bookends.py --episode S01E02_who_is_kraggor [--only intro|recap|outro]
  venv-modal/bin/modal run generators/story3d/modal_story3d.py::assemble --episode S01E02_who_is_kraggor \\
      --order 1,0,21,2,3,...,15,20 --out work/story3d/S01E02_who_is_kraggor
Runs on the VM (needs ffmpeg, the Ep.1 renders in work/story/S01E01_sprinkles_first_race/, the Luckiest Guy font)."""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "generators", "story"))
EP1 = os.path.join(ROOT, "work", "story", "S01E01_sprinkles_first_race")
FONT = "/root/.fonts/LuckiestGuy-Regular.ttf"
ENC = ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
LUFS = "loudnorm=I=-16:TP=-1.5:LRA=11"


def sh(cmd):
    subprocess.run(cmd, check=True)


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def put(local, ep, num):
    """Into the Modal volume where assemble() reads the final scene files."""
    modal = os.path.join(ROOT, "venv-modal", "bin", "modal")
    sh([modal, "volume", "put", "--force", "megawheel-story3d", local, f"/final/{ep}/scene_{num:02d}.mp4"])
    print(f"[bookends] scene_{num:02d} -> Modal volume /final/{ep}/")


def intro(ep, out):
    """ident + theme song: the aired Ep.1 files, joined with a soft cross-fade."""
    a, b = os.path.join(EP1, "ident_h.mp4"), os.path.join(EP1, "scene_00_h.mp4")
    xd = 0.8
    da = dur(a)
    p = os.path.join(out, "scene_00.mp4")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", a, "-i", b, "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration={xd}:offset={da - xd:.3f}[v];"
        f"[0:a][1:a]acrossfade=d={xd}:c1=tri:c2=tri,{LUFS}[a]", "-map", "[v]", "-map", "[a]"] + ENC + [p])
    return p


CLIPS = [("scene_09_h.mp4", 0.0, 4.4), ("scene_11_h.mp4", 6.0, 4.4), ("scene_13_h.mp4", 0.2, 4.0),
         ("scene_13_h.mp4", 10.6, 3.6), ("scene_16_h.mp4", 0.0, 7.4)]
VO = [("Previously, on MegaWheel Arena...", 0.5),
      ("A little ice cream truck. A giant monster. And a song that changed everything.", 5.0),
      ("Everyone thought the monster was gone for good. Everyone... was wrong.", 15.2)]
XD = 0.4


def recap(ep, out):
    import story25d as ST
    se = ST.se
    se.detect_font()
    items = [(t, ST.line_style("calm"), ST.speaker_voice("narrator"), "studio") for t, _ in VO]
    ST.announcer.prefetch(items, note="bookends recap")
    import numpy as np
    total = sum(d for _, _, d in CLIPS) - XD * (len(CLIPS) - 1)
    sr = se.SR
    vo = np.zeros(int((total + 2) * sr))
    subs = []
    for it, (txt, at) in zip(items, VO):
        a = ST.announcer.get(*it)
        vo[int(at * sr):int(at * sr) + len(a)] += a[:len(vo) - int(at * sr)]
        subs.append((txt, at, at + len(a) / sr + 0.2))
    peak = float(np.abs(vo).max()) or 1.0
    vo = vo / peak * 0.9
    vo_wav = os.path.join(out, "recap_vo.wav")
    se.write_wav(vo_wav, vo[:int(total * sr)])
    cue = os.path.join(ROOT, "branding", "music", "cues", "cue_grandpa_memory.wav")
    sting = os.path.join(ROOT, "branding", "music", "cues", "cue_kraggor_motif.wav")
    inputs, fc, last, off = [], [], None, 0.0
    for i, (f, ss, d) in enumerate(CLIPS):
        inputs += ["-ss", f"{ss}", "-t", f"{d}", "-i", os.path.join(EP1, f)]
        # crop clear of the aired subtitle band (it sits ~86-93 % down) and note box (top), keep 16:9, back to full size
        fc.append(f"[{i}:v]crop=1369:770:275:80,scale=1920:1080,setsar=1,fps=30[c{i}]")
    cur = "c0"
    t = CLIPS[0][2]
    for i in range(1, len(CLIPS)):
        off = t - XD
        fc.append(f"[{cur}][c{i}]xfade=transition=fade:duration={XD}:offset={off:.3f}[x{i}]")
        cur, t = f"x{i}", off + CLIPS[i][2]
    dt = (f"drawtext=fontfile={FONT}:text='PREVIOUSLY ON':fontcolor=0xFFD21F:fontsize=70:borderw=5:bordercolor=black:"
          f"x=(w-text_w)/2:y=h*0.07:alpha='if(lt(t,3.2),min(1,t/0.4),max(0,(3.6-t)/0.4))',"
          f"drawtext=fontfile={FONT}:text='MEGAWHEEL ARENA':fontcolor=white:fontsize=110:borderw=6:bordercolor=black:"
          f"x=(w-text_w)/2:y=h*0.15:alpha='if(lt(t,3.2),min(1,t/0.4),max(0,(3.6-t)/0.4))'")
    for k, (txt, a0, a1) in enumerate(subs):
        words = txt.split()
        half = len(words) // 2 if len(txt) > 42 else len(words)
        lines = [" ".join(words[:half]), " ".join(words[half:])] if half < len(words) else [txt]
        for j, ln in enumerate(lines):
            tf = os.path.join(out, f"recap_sub{k}_{j}.txt")
            open(tf, "w", encoding="utf-8").write(ln)
            dt += (f",drawtext=fontfile={FONT}:textfile={tf}:fontcolor=white:fontsize=54:borderw=5:bordercolor=black:"
                   f"x=(w-text_w)/2:y=h*{0.78 + 0.075 * j:.3f}:enable='between(t,{a0:.2f},{a1:.2f})'")
    fc.append(f"[{cur}]{dt},fade=t=in:d=0.5,fade=t=out:st={total - 0.8:.3f}:d=0.8[v]")
    n = len(CLIPS)
    st_at = int(VO[2][1] * 1000)
    fc.append(f"[{n}:a]atrim=0:{total:.2f},volume=0.5,afade=t=in:d=1.0,afade=t=out:st={total - 1.5:.2f}:d=1.5[m]")      # score, A10: quiet
    fc.append(f"[{n + 1}:a]adelay={st_at}|{st_at},volume=0.35[s]")
    fc.append(f"[{n + 2}:a]aformat=channel_layouts=stereo[vo]")
    fc.append("[m]aformat=channel_layouts=stereo[m2];[s]aformat=channel_layouts=stereo[s2];"
              f"[m2][s2][vo]amix=inputs=3:normalize=0,{LUFS}[a]")
    p = os.path.join(out, "scene_21.mp4")
    sh(["ffmpeg", "-y", "-loglevel", "error"] + inputs + ["-i", cue, "-i", sting, "-i", vo_wav, "-filter_complex",
                                                          ";".join(fc), "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}"] + ENC + [p])
    return p


def outro(ep, out):
    """The 2.5D outro scene (story25d scene_20.json: song, nametags, teaser card, end screen), rendered here."""
    sh([os.path.join(ROOT, "venv", "bin", "python"), os.path.join(ROOT, "generators", "story", "story25d.py"),
        "--episode", ep, "--scene", "20"])
    src = os.path.join(ROOT, "work", "story", ep, "scene_20_h.mp4")
    p = os.path.join(out, "scene_20.mp4")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", LUFS, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-ar", "48000", "-ac", "2", p])
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--only", choices=["intro", "recap", "outro"])
    a = ap.parse_args()
    out = os.path.join(ROOT, "work", "story3d", a.episode, "bookends")
    os.makedirs(out, exist_ok=True)
    jobs = {"intro": (intro, 0), "recap": (recap, 21), "outro": (outro, 20)}
    for name, (fn, num) in jobs.items():
        if a.only and a.only != name:
            continue
        p = fn(a.episode, out)
        print(f"[bookends] {name}: {p} ({dur(p):.1f}s)")
        put(p, a.episode, num)


if __name__ == "__main__":
    main()
