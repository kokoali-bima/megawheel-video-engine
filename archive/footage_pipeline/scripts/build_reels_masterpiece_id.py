#!/usr/bin/env python3
"""
Full HD 1080x1920 Indonesian Masterpiece Reels - Ready for Deploy
"""

import os
import subprocess
import asyncio
import edge_tts

OUTPUT_DIR = "/tmp/reels_deploy_id"
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
        "text": "Mobil sport hitam melesat kencang! Awas polisi tidur raksasa... Boom! Rodanya langsung copot! Gagal!",
        "video_start": 0.8,
        "video_dur": 13.7,
        "sfx_delay": 3.6
    },
    {
        "badge": "[ LEVEL 2 : MOBIL KLASIK ANTIK ]",
        "text": "Sekarang giliran mobil antik meluncur... Waduh! Bodinya copot dari rangka! Hancur berantakan! Gagal lagi!",
        "video_start": 46.0,
        "video_dur": 11.0,
        "sfx_delay": 6.0
    },
    {
        "badge": "[ LEVEL 3 : TRUK MERAH 6 RODA ]",
        "text": "Truk monster merah enam roda siap beraksi! Gas polll! Roda raksasanya kuat banget! HOREEE! Berhasil sampai garis finish! Kamu juaranya!",
        "video_start": 221.8,
        "video_dur": 21.2,
        "sfx_delay": 17.5
    }
]

async def build_reels():
    print("=== Generating Indonesian Voiceover for Reels ===")
    durations = [sc["video_dur"] for sc in scenes_id]
    audio_files = []
    
    for i, sc in enumerate(scenes_id):
        f_mp3 = f"{OUTPUT_DIR}/v_{i}.mp3"
        comm = edge_tts.Communicate(sc["text"], "id-ID-GadisNeural", rate="+8%", pitch="+3Hz")
        await comm.save(f_mp3)
        
        target_dur = sc["video_dur"]
        f_padded = f"{OUTPUT_DIR}/pad_{i}.mp3"
        subprocess.run([
            "ffmpeg", "-y", "-i", f_mp3,
            "-filter_complex", f"[0:a]apad=whole_dur={target_dur:.2f}[aout]",
            "-map", "[aout]",
            "-t", f"{target_dur:.2f}",
            "-c:a", "libmp3lame", "-b:a", "192k", f_padded
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        audio_files.append(f_padded)
    
    concat_list = f"{OUTPUT_DIR}/concat.txt"
    with open(concat_list, "w") as f:
        for af in audio_files:
            f.write(f"file '{af}'\n")
    
    full_voice = f"{OUTPUT_DIR}/full_voice.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list, "-c:a", "libmp3lame", "-b:a", "192k", full_voice
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    total_len = sum(durations)
    print(f"Total Video Length: {total_len:.2f}s")
    
    t_fail1 = scenes_id[0]["sfx_delay"]
    t_fail2 = durations[0] + scenes_id[1]["sfx_delay"]
    t_win3  = durations[0] + durations[1] + scenes_id[2]["sfx_delay"]
    
    # Extract game sfx
    game_sfx_filter = []
    game_concat = ""
    for idx, (sc, dur) in enumerate(zip(scenes_id, durations)):
        st = sc["video_start"]
        game_sfx_filter.append(f"[1:a]atrim=start={st:.2f}:duration={dur:.2f},asetpts=PTS-STARTPTS[ga{idx}];")
        game_concat += f"[ga{idx}]"
    game_sfx_filter.append(f"{game_concat}concat=n=3:v=0:a=1[game_sfx_raw];[game_sfx_raw]volume=0.35[game_sfx];")
    
    audio_mixed = f"{OUTPUT_DIR}/audio_mixed.mp3"
    complex_audio = (
        "".join(game_sfx_filter) +
        f"[0:a]volume=1.8[voice];"
        f"[2:a]volume=0.20,atrim=duration={total_len:.2f},afade=t=out:st={total_len-1.5:.2f}:d=1.5[bgm];"
        f"[3:a]adelay={int(t_fail1*1000)}|{int(t_fail1*1000)},volume=1.8[sfx1];"
        f"[4:a]adelay={int(t_fail2*1000)}|{int(t_fail2*1000)},volume=1.8[sfx2];"
        f"[5:a]adelay={int(t_win3*1000)}|{int(t_win3*1000)},volume=2.2[sfx3_win];"
        f"[6:a]adelay={int(t_win3*1000)}|{int(t_win3*1000)},volume=1.6[sfx3_cheer];"
        f"[voice][bgm][game_sfx][sfx1][sfx2][sfx3_win][sfx3_cheer]amix=inputs=7:duration=first:dropout_transition=2,volume=5.5[aout]"
    )
    
    subprocess.run([
        "ffmpeg", "-y",
        "-i", full_voice,
        "-i", "/root/local_videos/physics/beamng_test.mp4",
        "-i", "/tmp/kids_cheerful_bgm.mp3",
        "-i", "/tmp/sfx_fail.wav",
        "-i", "/tmp/sfx_fail.wav",
        "-i", "/tmp/sfx_win.wav",
        "-i", "/tmp/sfx_cheer.wav",
        "-filter_complex", complex_audio,
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        audio_mixed
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    ass_path = f"{OUTPUT_DIR}/subs.ass"
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopBadge,DejaVu Sans,36,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,3,3.5,1,8,25,25,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    curr_t = 0.0
    for sc, dur in zip(scenes_id, durations):
        start_str = format_ass_time(curr_t)
        end_str = format_ass_time(curr_t + dur)
        ass_header += f"Dialogue: 0,{start_str},{end_str},TopBadge,,0,0,0,,{sc['badge']}\n"
        curr_t += dur
    
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)
    
    fail_png = "/tmp/kids_graphic_assets_fhd/fail_id_fhd.png"
    win_png = "/tmp/kids_graphic_assets_fhd/win_id_fhd.png"
    
    t_end1 = min(t_fail1 + 5.0, durations[0])
    t_end2 = min(t_fail2 + 4.0, durations[0] + durations[1])
    
    filter_parts = []
    concat_inputs = ""
    for idx, (sc, dur) in enumerate(zip(scenes_id, durations)):
        st = sc["video_start"]
        filter_parts.append(
            f"[0:v]trim=start={st:.2f}:duration={dur:.2f},setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[sc{idx}];"
        )
        concat_inputs += f"[sc{idx}]"
    
    filter_parts.append(f"{concat_inputs}concat=n=3:v=1:a=0[raw_seq];")
    filter_parts.append(f"[raw_seq]split=2[in_bg][in_fg];")
    filter_parts.append(f"[in_bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.22[bg];")
    filter_parts.append(f"[in_fg]scale=1080:608,drawbox=x=0:y=0:w=iw:h=ih:color=yellow@0.7:t=5[fg];")
    filter_parts.append(f"[bg][fg]overlay=x=0:y=656[base_video];")
    filter_parts.append(f"[base_video][2:v]overlay=x=0:y=1320:enable='between(t,{t_fail1:.2f},{t_end1:.2f}) + between(t,{t_fail2:.2f},{t_end2:.2f})'[with_fail];")
    filter_parts.append(f"[with_fail][3:v]overlay=x=0:y=1320:enable='between(t,{t_win3:.2f},{total_len:.2f})'[with_badges];")
    filter_parts.append(f"[with_badges]ass={ass_path},fade=t=out:st={total_len-1.0:.2f}:d=1.0[vfinal]")
    
    full_filter = "".join(filter_parts)
    out_mp4 = "/root/REELS_MASTERPIECE_DEPLOY.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-i", "/root/local_videos/physics/beamng_test.mp4",
        "-i", audio_mixed,
        "-i", fail_png,
        "-i", win_png,
        "-filter_complex", full_filter,
        "-map", "[vfinal]",
        "-map", "1:a",
        "-t", f"{total_len:.2f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-map_metadata", "-1",
        "-movflags", "+faststart",
        out_mp4
    ]
    
    print(f"Rendering Masterpiece {out_mp4}...")
    subprocess.run(cmd, check=True)
    print(f"SUCCESS: {out_mp4} ({os.path.getsize(out_mp4)} bytes)")

asyncio.run(build_reels())
