"""Scene JSON linter for story3d - runs BEFORE any render money is spent (user 2026-10-06: "standar agar Gemini, OpenAI,
DeepSeek, bahkan Kimi bisa membuat video yang sama kualitasnya"). Any agent / model writes the scene; this file decides
whether it is allowed to render. It rejects what weaker models typically get wrong:
  invented keys or values (a typo silently does nothing), unknown camera / move / effect / music / emotion names,
  speakers without a voice, cars parked in front of the one who talks, monotonous shot lists, one music cue for the
  whole scene, crickets in town, lines too long for a subtitle, timing strings that do not parse.
  venv/bin/python generators/story3d/validate_scene.py --episode S01E02_who_is_kraggor --scenes 2,3
Exit 0 = OK (warnings allowed), 1 = errors (fix the JSON; produce_story3d refuses to render)."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CONTRACT = json.load(open(os.path.join(HERE, "STYLE_CONTRACT.json"), encoding="utf-8"))
LN = CONTRACT["lint"]                                          # every number below comes from the style contract

SCENE_KEYS = {"title", "chapter", "location", "theme_location", "time", "weather", "ambience", "fog", "letterbox",
              "shops", "shops_z", "gap", "tail", "edge_fade", "actors", "props", "score", "shots", "headlights",
              "contact_shadow", "glide", "hill", "finish", "music", "song", "song_stereo", "stands_text", "tears",
              "tint", "note", "jcut"}
SHOT_KEYS = {"cam", "on", "with", "zoom", "dx", "lift", "hold", "lead", "gap", "tail", "cut", "glide", "move", "moves",
             "lines", "emote", "sfx", "fx", "caption", "note", "title", "flicker", "kraggor", "kraggor_far", "eyes",
             "look", "punch", "freeze", "roll", "speedlines", "confetti", "crown", "card", "endcard", "nametag",
             "photo_glow", "toss", "foot", "triple", "calendar", "music", "fog", "tint", "group", "follow", "lean",
             "jcut"}
ACTOR_KEYS = {"vk", "x", "z", "face", "h", "emo", "hidden", "color", "accent", "mustache", "patched", "small", "jumbo"}
MOVE_KEYS = {"push", "pull", "pan", "crane", "dutch", "handheld", "whip"}
ACTOR_MOVE_KEYS = {"to_x", "speed", "x", "face", "h", "show", "hop", "reverse", "stuck", "dizzy", "squash", "delay",
                   "at", "hold", "patched"}
CAMS = {"wide", "two", "group", "medium", "close", "ecu", "low", "track"}
SINGLE = {"close", "ecu", "medium", "low"}                     # one-character framings
# film coverage rules (owner 2026-10-06: "tiap ngobrol di-zoom ke yang bicara ... seperti film per pemeran"):
# establish the group, let exchanges play in two / group shots, single close-ups only for emotional beats.
COVER = dict(pingpong=LN["pingpong"], single_share=LN["single_share"], group_lines=LN["group_lines"])
SIZE_RANK = {"wide": 0, "track": 1, "group": 1, "two": 2, "medium": 3, "low": 3, "close": 4, "ecu": 5}
LOCATIONS = {"town", "arena", "country", "trackside", "podium", "garage"}
TIMES = {"morning", "noon", "sunset", "night"}                 # exactly the themes sim_engine knows
AMBIENCE = {"birds", "night", "city_night", "crowd", "room", "rain", "none"}
EMOTES = {"normal", "talk", "happy", "laugh", "proud", "excited", "scared", "surprised", "sad", "cry", "angry",
          "worried", "determined", "shy", "dizzy", "whisper"}
LINE_EMOS = EMOTES | {"calm"}
PROPS = {"streetlamps", "footprints", "barricade", "poster", "photo", "desk", "podium", "mud", "stage", "spotlight"}
NARRATORS = {"narrator", "announcer", "announcer2"}
MAX_LINE = LN["max_line"]


def sfx_names():
    sys.path.insert(0, os.path.join(ROOT, "generators", "story"))
    try:
        import story25d as ST
        return set(ST.SFX) | {"drone"}
    except Exception:                                              # noqa: BLE001 (lint still runs without cairo)
        return {"sting", "jingle", "heartbeat", "whoosh", "memory", "ding", "laugh", "cheer", "gasp", "roar", "stomp",
                "thunder", "engine", "splat", "lamp_off", "honk", "steps_far", "stomp_near", "drone", "thud_far",
                "honk_cheer"}


def vehicles():
    try:
        sys.path.insert(0, os.path.join(ROOT, "generators", "physics_2d"))
        import sim_engine as se
        return set(se.VEHICLES)
    except Exception:                                              # noqa: BLE001
        return {"icecream", "bus", "sports", "monster", "police", "f1", "taxi", "firetruck", "monster2", "bigrig"}


def voices():
    d = os.path.join(ROOT, "branding", "voice", "characters")
    return {f[:-4] for f in os.listdir(d) if f.endswith(".wav")} if os.path.isdir(d) else set()


def body_len(vk):
    try:
        import sim_engine as se
        return se.VEHICLES[vk]["body"][0]
    except Exception:                                              # noqa: BLE001
        return {"bus": 8.0, "bigrig": 9.0, "icecream": 5.2, "firetruck": 7.0}.get(vk, 4.4)


def lint(ep, n):
    path = os.path.join(ROOT, "stories", ep, f"scene_{n:02d}.json")
    err, warn = [], []
    try:
        sc = json.load(open(path, encoding="utf-8"))
    except Exception as e:                                         # noqa: BLE001
        return [f"tidak bisa dibaca: {e}"], []
    for k in set(sc) - SCENE_KEYS:
        err.append(f"kunci scene tidak dikenal: '{k}'")
    if sc.get("location", "town") not in LOCATIONS:
        err.append(f"location '{sc.get('location')}' tidak dikenal {sorted(LOCATIONS)}")
    tm = sc.get("time", "morning")
    if tm not in TIMES:
        err.append(f"time '{tm}' tidak dikenal {sorted(TIMES)}")
    amb = sc.get("ambience")
    if amb is not None and amb not in AMBIENCE:
        err.append(f"ambience '{amb}' tidak dikenal {sorted(AMBIENCE)}")
    if amb == "night" and sc.get("location", "town") in ("town", "arena", "podium"):
        err.append("ambience 'night' (jangkrik) di kota - pakai 'city_night' (keputusan user 2026-10-05)")
    actors = sc.get("actors", {})
    vks, vcs = vehicles(), voices()
    for aid, a in actors.items():
        for k in set(a) - ACTOR_KEYS:
            err.append(f"aktor {aid}: kunci tidak dikenal '{k}'")
        if a.get("vk") not in vks:
            err.append(f"aktor {aid}: kendaraan '{a.get('vk')}' tidak ada")
        if not -0.6 <= float(a.get("z", 1.0)) <= 3.2:
            err.append(f"aktor {aid}: z={a.get('z')} di luar jalan (-0.6..3.2)")
        if a.get("emo", "normal") not in EMOTES:
            err.append(f"aktor {aid}: emo '{a.get('emo')}' tidak dikenal")
    for p in sc.get("props", []):
        if p.get("type") not in PROPS:
            err.append(f"prop '{p.get('type')}' tidak dikenal {sorted(PROPS)}")
    sfxs = sfx_names()
    shots = sc.get("shots", [])
    if not shots:
        err.append("tidak ada shot")
    pos = {aid: (float(a.get("x", 0)), float(a.get("z", 1.0)), bool(a.get("hidden", False))) for aid, a in actors.items()}
    for i, sh in enumerate(shots):
        tag = f"shot {i}"
        for k in set(sh) - SHOT_KEYS:
            err.append(f"{tag}: kunci tidak dikenal '{k}'")
        cam = sh.get("cam", "wide")
        if "look" not in sh and cam not in CAMS:
            err.append(f"{tag}: cam '{cam}' tidak dikenal {sorted(CAMS)}")
        if sh.get("on") and sh["on"] not in actors:
            err.append(f"{tag}: on='{sh['on']}' bukan aktor scene")
        if cam == "two" and sh.get("with") not in actors:
            err.append(f"{tag}: cam 'two' butuh with=<aktor>")
        for k in set(sh.get("move", {})) - MOVE_KEYS:
            err.append(f"{tag}: gerak kamera tidak dikenal '{k}' {sorted(MOVE_KEYS)}")
        for aid, mv in sh.get("moves", {}).items():
            if aid not in actors:
                err.append(f"{tag}: moves untuk '{aid}' yang bukan aktor")
                continue
            for k in set(mv) - ACTOR_MOVE_KEYS:
                err.append(f"{tag}: gerak aktor {aid} tidak dikenal '{k}'")
            x, z, hid = pos[aid]
            if "show" in mv:
                hid = not mv["show"]
            x = float(mv.get("to_x", mv.get("x", x)))
            pos[aid] = (x, z, hid)
        for aid, e in sh.get("emote", {}).items():
            if aid not in actors:
                err.append(f"{tag}: emote untuk '{aid}' yang bukan aktor")
            elif e not in EMOTES:
                err.append(f"{tag}: emote '{e}' tidak dikenal")
        for s in sh.get("sfx", []):
            name, dt = (s, 0.0) if isinstance(s, str) else (s[0], s[1] if len(s) > 1 else 0.0)
            if name in LN.get("banned_sfx", []):
                err.append(f"{tag}: efek '{name}' dilarang (noise di headphone) - pakai 'honk_cheer' untuk sorakan [A07]")
            if name not in sfxs:
                err.append(f"{tag}: efek '{name}' tidak ada {sorted(sfxs)}")
            if isinstance(dt, str):
                try:
                    assert dt.startswith("end")
                    float(dt[3:] or 0.0)
                except Exception:                                  # noqa: BLE001
                    err.append(f"{tag}: waktu efek '{dt}' (pakai angka detik atau 'end+0.1')")
        for ln in sh.get("lines", []):
            if len(ln) < 3:
                err.append(f"{tag}: baris dialog harus [spk, teks, emosi]")
                continue
            spk, text, emo = ln[:3]
            if spk not in actors and spk not in NARRATORS:
                err.append(f"{tag}: pembicara '{spk}' bukan aktor scene")
            if spk not in NARRATORS and spk not in vcs:
                err.append(f"{tag}: tidak ada suara branding/voice/characters/{spk}.wav")
            if emo not in LINE_EMOS:
                err.append(f"{tag}: emosi kalimat '{emo}' tidak dikenal")
            if len(ln) > 3 and not os.path.exists(os.path.join(ROOT, ln[3])):
                err.append(f"{tag}: file nyanyian tidak ada: {ln[3]}")
            if len(ln) <= 3 and len(text) > MAX_LINE:
                err.append(f"{tag}: kalimat {len(text)} huruf (maks {MAX_LINE}) - pecah jadi dua shot")
            if spk in actors and pos[spk][2] and cam != "wide":
                warn.append(f"{tag}: {spk} bicara tapi masih tersembunyi (hidden)")
            if spk in actors and sh.get("on") and sh["on"] != spk and cam in ("close", "ecu", "medium", "low"):
                warn.append(f"{tag}: close-up pada {sh['on']} padahal {spk} yang bicara (reaksi? sengaja?)")
        # bumper to bumper: cars in nearly the same lane need air between them (a line of cars reads as a traffic
        # jam, not a conversation - owner review scene 2, 2026-10-06)
        vis = [(k, v) for k, v in pos.items() if not v[2]]
        for q in range(len(vis)):
            for r in range(q + 1, len(vis)):
                (ka, (xa, za, _)), (kb, (xb, zb, _)) = vis[q], vis[r]
                if abs(za - zb) < 0.9 and (sh.get("lines") or sh.get("cam") in ("group", "two")):
                    gap = abs(xa - xb) - (body_len(actors[ka]["vk"]) + body_len(actors[kb]["vk"])) / 2
                    if gap < LN["bumper_gap"]:
                        err.append(f"{tag}: {ka} dan {kb} menempel (jarak {gap:.1f} m < {LN['bumper_gap']}) [C02]")
        # cars must not stand inside a solid prop (barricade spans the whole road)
        for pr in sc.get("props", []):
            if pr.get("type") != "barricade" or not (pr.get("from_shot", 0) <= i <= pr.get("to_shot", 9999)):
                continue
            bx0 = pr.get("x", 12) - pr.get("skew", 2.6) / 2 - LN["prop_margin"]
            bx1 = pr.get("x", 12) + pr.get("skew", 2.6) / 2 + LN["prop_margin"]
            for k, (xk, zk, hk) in pos.items():
                half = body_len(actors[k]["vk"]) / 2
                if not hk and xk + half > bx0 and xk - half < bx1:
                    err.append(f"{tag}: {k} (x={xk:g}) menembus palang di x {bx0:.1f}..{bx1:.1f}")
        # parked in front of the focus / speaker (nearer car covers a farther one)
        want = {sh.get("on")} | {ln[0] for ln in sh.get("lines", []) if ln and ln[0] in actors}
        for aid in [w for w in want if w and w in actors]:
            x, z, hid = pos[aid]
            if hid:
                continue
            half = body_len(actors[aid]["vk"]) / 2
            for oid, (ox, oz, oh) in pos.items():
                if oid == aid or oh or oz >= z - 0.05:
                    continue
                oh_ = body_len(actors[oid]["vk"]) / 2
                cov = max(0.0, min(x + half, ox + oh_) - max(x - half, ox - oh_)) / (2 * half)
                if cov > 0.3:
                    err.append(f"{tag}: {aid} (x={x:g}) tertutup {oid} (x={ox:g}, lebih dekat kamera) {cov:.0%} - geser x")
    # variety (same rules as the QA sensors, before rendering)
    cams = [s.get("cam", "wide") for s in shots if "look" not in s]
    run = 1
    for i in range(1, len(cams)):
        run = run + 1 if cams[i] == cams[i - 1] else 1
        if run >= LN["same_cam_run"]:
            err.append(f"variasi: {run} shot '{cams[i]}' berturut-turut [V01]")
    if len(shots) >= 5 and len(set(cams)) < LN["min_sizes"]:
        err.append(f"variasi: hanya {len(set(cams))} ukuran shot (min {LN['min_sizes']}) [V01]")
    moves = {k for s in shots for k in s.get("move", {})}
    for i in range(1, len(shots)):                                 # C06 jump cut: same subject, same size, cut
        a_, b_ = shots[i - 1], shots[i]
        if a_.get("on") and a_.get("on") == b_.get("on") and \
                abs(SIZE_RANK.get(a_.get("cam", "wide"), 0) - SIZE_RANK.get(b_.get("cam", "wide"), 0)) < 1:
            err.append(f"shot {i}: jump cut (subjek '{b_['on']}' & ukuran sama dengan shot sebelumnya) [C06]")
    speakers = {ln[0] for s in shots for ln in s.get("lines", []) if ln and ln[0] in actors}
    if len(speakers) >= 2 and float(sc.get("jcut", CONTRACT["engine"]["jcut_s"])) < LN["jcut_min"]:
        err.append(f"jcut {sc.get('jcut')} < {LN['jcut_min']}: dialog banyak pembicara wajib J-cut [C04]")
    if len(shots) >= 5 and len(moves) < LN["min_moves"]:
        err.append(f"variasi: gerak kamera {sorted(moves)} (min 2 jenis)")
    if shots and not ({"push", "punch", "low"} & ({k for k in shots[-1].get("move", {})} |
                                                   ({"punch"} if shots[-1].get("punch") else set()) |
                                                   {shots[-1].get("cam", "")})):
        warn.append("kait akhir: shot terakhir tanpa push / low / punch")
    # coverage: no talking-heads ping-pong
    talkers = [a for a in actors if a not in NARRATORS]
    dlg = [(i, s.get("cam", "wide"), [ln[0] for ln in s.get("lines", []) if ln and ln[0] in actors and len(ln) <= 3])
           for i, s in enumerate(shots)]
    dlg = [d for d in dlg if d[2]]
    run, last = 0, None
    for i, cam, spk in dlg:
        if cam in SINGLE and len(spk) == 1 and spk[0] != last:
            run += 1
            if run >= COVER["pingpong"]:
                err.append(f"coverage: {run} close-up berturut-turut pindah pembicara (s/d shot {i}) - pola 'film per "
                           f"pemeran'; tahan two/group shot dan potong hanya pada emosi/reaksi")
        else:
            run = 0 if not (cam in SINGLE and len(spk) == 1) else run
        last = spk[-1] if spk else last
    n_lines = sum(len(d[2]) for d in dlg)
    single_lines = sum(len(d[2]) for d in dlg if d[1] in SINGLE)
    if len(set(talkers)) >= 2 and n_lines >= 4 and single_lines / n_lines > COVER["single_share"]:
        err.append(f"coverage: {single_lines}/{n_lines} kalimat diucapkan di close-up tunggal (maks "
                   f"{COVER['single_share']:.0%}) - pakai cam 'group'/'two'/'wide' untuk percakapan")
    if len(actors) >= 3 and n_lines >= 4 and not any(d[1] in ("group", "two", "wide") and len(d[2]) >= COVER["group_lines"]
                                                      for d in dlg):
        err.append("coverage: tidak ada shot grup/two yang membawa >= 2 kalimat - percakapan harus terlihat bersama")
    # music spotting
    score = sc.get("score", [])
    if not score and len(shots) >= 6:
        warn.append("tidak ada spotting musik (score)")
    cue_dir = os.path.join(ROOT, "branding", "music", "cues")
    covered = {}
    for c in score:
        name = c.get("cue") or c.get("sting")
        if not name or not os.path.exists(os.path.join(cue_dir, name + ".wav")):
            err.append(f"score: cue '{name}' tidak ada di branding/music/cues")
        if "cue" in c:
            a, b = int(c.get("from", 0)), int(c.get("to", c.get("from", 0)))
            if not (0 <= a <= b < len(shots)):
                err.append(f"score: rentang shot {a}..{b} di luar 0..{len(shots) - 1}")
            covered[name] = covered.get(name, 0) + (b - a + 1)
        elif not 0 <= int(c.get("shot", 0)) < len(shots):
            err.append(f"score: sting di shot {c.get('shot')} di luar rentang")
    if len(shots) >= 8 and covered and len(covered) == 1 and max(covered.values()) >= 0.85 * len(shots):
        err.append("score: satu cue menutupi hampir seluruh scene (monoton) - spotting per momen")
    return err, warn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", required=True)
    ap.add_argument("--scenes", required=True)
    a = ap.parse_args()
    bad = 0
    for n in [int(x) for x in a.scenes.split(",") if x]:
        err, warn = lint(a.episode, n)
        print(f"[lint] scene {n:02d}: {'OK' if not err else 'GAGAL'} ({len(err)} error, {len(warn)} peringatan)")
        for e in err:
            print(f"  ERROR {e}")
        for w in warn:
            print(f"  WARN  {w}")
        bad += len(err)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
