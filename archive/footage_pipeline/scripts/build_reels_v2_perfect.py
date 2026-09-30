import os, subprocess, asyncio, edge_tts

OUTPUT_DIR = "/tmp/reels_deploy_v2_id"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def format_ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

scenes_id = [
    {
        "badge": "[ LEVEL 1 : MOBIL SPORT HITAM ]",
        "video_start": 0.8,
        "video_dur": 13.7,
        "sfx_delay": 3.6,
        "intro": "Mobil sport hitam melesat kencang! Awas polisi tidur raksasa!",
        "reaction": "Boom! Rodanya langsung copot! Gagal!",
        "is_win": False
    },
    {
        "badge": "[ LEVEL 2 : MOBIL KLASIK ANTIK ]",
        "video_start": 46.0,
        "video_dur": 12.0,
        "sfx_delay": 6.0,
        "intro": "Giliran mobil antik meluncur perlahan!",
        "reaction": "Waduh! Bodinya lepas dari rangka! Hancur berantakan! Gagal lagi!",
        "is_win": False
    },
    {
        "badge": "[ LEVEL 3 : TRUK MERAH 6 RODA ]",
        "video_start": 221.8,
        "video_dur": 20.0,
        "sfx_delay": 1.8,
        "intro": "Truk monster merah enam roda siap beraksi! Gas polll!",
        "reaction": "HOREEE! YAY! Berhasil sampai garis finish! Kamu juaranya!",
        "is_win": True
    }
]

async def build_reels_v2():
    print("=== Generating Sync Chunks (Intro + Reaction) ===")
    audio_clips = []
    for i, sc in enumerate(scenes_id):
        f_intro = f"{OUTPUT_DIR}/v_{i}_intro.mp3"
        f_react = f"{OUTPUT_DIR}/v_{i}_react.mp3"
        
        c1 = edge_tts.Communicate(sc["intro"], "id-ID-GadisNeural", rate="+10%", pitch="+4Hz")
        await c1.save(f_intro)
        
        c2 = edge_tts.Communicate(sc["reaction"], "id-ID-GadisNeural", rate="+12%", pitch="+5Hz")
        await c2.save(f_react)
        
        # Convert to standard 44.1kHz WAV for perfect sample-accurate sync
        f_intro_wav = f"{OUTPUT_DIR}/v_{i}_intro.wav"
        f_react_wav = f"{OUTPUT_DIR}/v_{i}_react.wav"
        subprocess.run(["ffmpeg", "-y", "-i", f_intro, "-ar", "44100", "-ac", "2", f_intro_wav], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["ffmpeg", "-y", "-i", f_react, "-ar", "44100", "-ac", "2", f_react_wav], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        audio_clips.append((f_intro_wav, f_react_wav))

    video_durations = [sc["video_dur"] for sc in scenes_id]
    total_len = sum(video_durations)
    scene_starts = [0, video_durations[0], video_durations[0] + video_durations[1]]
    
    t_ev1 = scene_starts[0] + scenes_id[0]["sfx_delay"]
    t_ev2 = scene_starts[1] + scenes_id[1]["sfx_delay"]
    t_ev3 = scene_starts[2] + scenes_id[2]["sfx_delay"]
    
    print(f"Total: {total_len}s | Ev1: {t_ev1}s | Ev2: {t_ev2}s | Ev3: {t_ev3}s")
    
    v_filter = ""
    a_filter = ""
    concat_v = ""
    concat_a = ""
    
    for i, (sc, dur) in enumerate(zip(scenes_id, video_durations)):
        v_filter += f"[1:v]trim=start={sc['video_start']}:duration={dur},setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[sc_v{i}];"
        a_filter += f"[1:a]atrim=start={sc['video_start']}:duration={dur},asetpts=PTS-STARTPTS,aresample=44100[sc_a{i}];"
        concat_v += f"[sc_v{i}]"
        concat_a += f"[sc_a{i}]"
        
    v_filter += f"{concat_v}concat=n=3:v=1:a=0[raw_seq];"
    a_filter += f"{concat_a}concat=n=3:v=0:a=1[game_sfx_raw];[game_sfx_raw]volume=0.45[game_sfx];"
    
    mix_filter = (
        f"[0:a]volume=0.22,atrim=duration={total_len:.2f},afade=t=out:st={total_len-1.5:.2f}:d=1.5,aresample=44100[bgm];"
        f"[2:a]volume=2.2,adelay={int(scene_starts[0]*1000)}|{int(scene_starts[0]*1000)}[v1_i];"
        f"[3:a]volume=2.2,adelay={int(t_ev1*1000)}|{int(t_ev1*1000)}[v1_c];"
        f"[4:a]volume=2.2,adelay={int(scene_starts[1]*1000)}|{int(scene_starts[1]*1000)}[v2_i];"
        f"[5:a]volume=2.2,adelay={int(t_ev2*1000)}|{int(t_ev2*1000)}[v2_c];"
        f"[6:a]volume=2.2,adelay={int(scene_starts[2]*1000)}|{int(scene_starts[2]*1000)}[v3_i];"
        f"[7:a]volume=2.2,adelay={int(t_ev3*1000)}|{int(t_ev3*1000)}[v3_c];"
        f"[8:a]volume=1.8,adelay={int(t_ev1*1000)}|{int(t_ev1*1000)}[sfx1];"
        f"[9:a]volume=1.8,adelay={int(t_ev2*1000)}|{int(t_ev2*1000)}[sfx2];"
        f"[10:a]volume=2.4,adelay={int(t_ev3*1000)}|{int(t_ev3*1000)}[sfx3_win];"
        f"[11:a]volume=1.8,adelay={int(t_ev3*1000)}|{int(t_ev3*1000)}[sfx3_cheer];"
        "[bgm][game_sfx][v1_i][v1_c][v2_i][v2_c][v3_i][v3_c][sfx1][sfx2][sfx3_win][sfx3_cheer]amix=inputs=12:duration=first:dropout_transition=2,volume=5.2,loudnorm=I=-16:LRA=11:TP=-1.5[aout];"
    )
    
    # Subtitle ASS
    ass_path = f"{OUTPUT_DIR}/subs.ass"
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopBadge,DejaVu Sans,38,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,3,3.5,1,8,25,25,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    curr_t = 0.0
    for sc, dur in zip(scenes_id, video_durations):
        start_str = format_ass_time(curr_t)
        end_str = format_ass_time(curr_t + dur)
        ass_header += f"Dialogue: 0,{start_str},{end_str},TopBadge,,0,0,0,,{sc['badge']}\n"
        curr_t += dur
        
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)

    t_end1 = min(t_ev1 + 4.5, scene_starts[1])
    t_end2 = min(t_ev2 + 4.0, scene_starts[2])
    
    overlay_filter = (
        "[raw_seq]split=2[in_bg][in_fg];"
        "[in_bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.22[bg];"
        "[in_fg]scale=1080:608,drawbox=x=0:y=0:w=iw:h=ih:color=yellow@0.7:t=5[fg];"
        "[bg][fg]overlay=x=0:y=656[base_video];"
        f"[base_video][12:v]overlay=x=0:y=1320:enable='between(t,{t_ev1:.2f},{t_end1:.2f}) + between(t,{t_ev2:.2f},{t_end2:.2f})'[with_fail];"
        f"[with_fail][13:v]overlay=x=0:y=1320:enable='between(t,{t_ev3:.2f},{total_len:.2f})'[with_win];"
        f"[with_win]ass={ass_path},fade=t=out:st={total_len-1.0:.2f}:d=1.0[vfinal]"
    )
    
    out_mp4 = "/root/REELS_MASTERPIECE_V2_PERFECT.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-i", "/tmp/kids_cheerful_bgm.mp3",
        "-i", "/root/local_videos/physics/beamng_test.mp4",
        "-i", audio_clips[0][0], "-i", audio_clips[0][1],
        "-i", audio_clips[1][0], "-i", audio_clips[1][1],
        "-i", audio_clips[2][0], "-i", audio_clips[2][1],
        "-i", "/tmp/sfx_fail.wav", "-i", "/tmp/sfx_fail.wav",
        "-i", "/tmp/sfx_win.wav", "-i", "/tmp/sfx_cheer.wav",
        "-i", "/tmp/kids_graphic_assets_fhd/fail_id_fhd.png",
        "-i", "/tmp/kids_graphic_assets_fhd/win_id_fhd.png",
        "-filter_complex", v_filter + a_filter + mix_filter + overlay_filter,
        "-map", "[vfinal]", "-map", "[aout]",
        "-t", f"{total_len:.2f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "256k", "-ar", "44100",
        "-map_metadata", "-1",
        "-movflags", "+faststart",
        out_mp4
    ]
    
    print(f"Rendering Perfected Masterpiece {out_mp4}...")
    subprocess.run(cmd, check=True)
    print(f"SUCCESS: {out_mp4} ({os.path.getsize(out_mp4)} bytes)")

asyncio.run(build_reels_v2())
