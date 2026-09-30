import os
import subprocess
import asyncio
import edge_tts

OUTPUT_DIR = "/tmp/v2_out"
os.makedirs(OUTPUT_DIR, exist_ok=True)
def format_ass_time(seconds):
    h = int(seconds // 3600); m = int((seconds % 3600) // 60); s = int(seconds % 60); cs = int(round((seconds - int(seconds)) * 100))
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

scenes_en = [
    {"badge": "[ LEVEL 1 : RED CAR ]", "text": "Red car is ready! Watch out for the deep hole... Oh no, crashed and stopped! Failed!", "video_start": 71.58, "video_dur": 15.0, "sfx_delay": 9.5},
    {"badge": "[ LEVEL 2 : WHITE BUGGY ]", "text": "White buggy is speeding up... Whoops! Destroyed! Failed again!", "video_start": 113.30, "video_dur": 14.0, "sfx_delay": 8.5},
    {"badge": "[ LEVEL 3 : BLUE BUS ]", "text": "Heavy duty blue bus! Look at those tires! Oh no... Flipped over and destroyed! Failed!", "video_start": 135.22, "video_dur": 16.0, "sfx_delay": 10.0}
]

async def build():
    durations = [sc["video_dur"] for sc in scenes_en]
    audio_files = []
    for i, sc in enumerate(scenes_en):
        f_mp3 = f"{OUTPUT_DIR}/v_{i}.mp3"
        comm = edge_tts.Communicate(sc["text"], "en-US-EmmaNeural", rate="+2%", pitch="+2Hz")
        await comm.save(f_mp3)
        target_dur = sc["video_dur"]
        f_padded = f"{OUTPUT_DIR}/pad_{i}.mp3"
        subprocess.run(["ffmpeg", "-y", "-i", f_mp3, "-filter_complex", f"[0:a]apad=whole_dur={target_dur:.2f}[aout]", "-map", "[aout]", "-t", f"{target_dur:.2f}", "-c:a", "libmp3lame", "-b:a", "192k", f_padded], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        audio_files.append(f_padded)
    
    concat_list = f"{OUTPUT_DIR}/concat.txt"
    with open(concat_list, "w") as f:
        for af in audio_files: f.write(f"file '{af}'\n")
    
    full_voice = f"{OUTPUT_DIR}/full_voice.mp3"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c:a", "libmp3lame", "-b:a", "192k", full_voice], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    total_len = sum(durations)
    
    game_audio = f"{OUTPUT_DIR}/game_sfx.mp3"
    game_filter = []
    game_concat = ""
    for idx, sc in enumerate(scenes_en):
        st = sc["video_start"]
        dur = sc["video_dur"]
        game_filter.append(f"[0:a]atrim=start={st:.2f}:duration={dur:.2f},asetpts=PTS-STARTPTS[a{idx}];")
        game_concat += f"[a{idx}]"
    game_filter.append(f"{game_concat}concat=n=3:v=0:a=1[game_out]")
    
    subprocess.run([
        "ffmpeg", "-y", "-i", "/root/.gemini/antigravity-cli/scratch/raw_materials/Physics_Gaming/2026-09-25/beamng_test.mp4",
        "-filter_complex", "".join(game_filter),
        "-map", "[game_out]", "-c:a", "libmp3lame", "-b:a", "192k", game_audio
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    t_fail1 = scenes_en[0]["sfx_delay"]
    t_fail2 = durations[0] + scenes_en[1]["sfx_delay"]
    t_fail3 = durations[0] + durations[1] + scenes_en[2]["sfx_delay"]
    audio_mixed = f"{OUTPUT_DIR}/audio_mixed.mp3"
    complex_audio = (
        f"[0:a]volume=1.5[voice];"
        f"[1:a]volume=0.20,atrim=duration={total_len:.2f},afade=t=out:st={total_len-1.5:.2f}:d=1.5[bgm];"
        f"[2:a]volume=0.35[game_sfx];"
        f"[3:a]adelay={int(t_fail1*1000)}|{int(t_fail1*1000)},volume=1.8[sfx1];"
        f"[4:a]adelay={int(t_fail2*1000)}|{int(t_fail2*1000)},volume=1.8[sfx2];"
        f"[5:a]adelay={int(t_fail3*1000)}|{int(t_fail3*1000)},volume=1.8[sfx3];"
        f"[voice][bgm][game_sfx][sfx1][sfx2][sfx3]amix=inputs=6:duration=first:dropout_transition=2,volume=6.30957[aout]"
    )
    
    subprocess.run([
        "ffmpeg", "-y", 
        "-i", full_voice, 
        "-i", "/tmp/kids_cheerful_bgm.mp3", 
        "-i", game_audio, 
        "-i", "/tmp/sfx_fail.wav", 
        "-i", "/tmp/sfx_fail.wav", 
        "-i", "/tmp/sfx_fail.wav", 
        "-filter_complex", complex_audio, 
        "-map", "[aout]", "-c:a", "libmp3lame", "-b:a", "192k", audio_mixed
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    ass_path = f"{OUTPUT_DIR}/subs.ass"
    ass_header = "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: TopBadge,DejaVu Sans,36,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,3,3.5,1,8,25,25,240,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    curr_t = 0.0
    for sc, dur in zip(scenes_en, durations):
        ass_header += f"Dialogue: 0,{format_ass_time(curr_t)},{format_ass_time(curr_t + dur)},TopBadge,,0,0,0,,{sc['badge']}\n"
        curr_t += dur
    with open(ass_path, "w", encoding="utf-8") as f: f.write(ass_header)
    
    t_end1 = min(t_fail1 + 5.0, durations[0])
    t_end2 = min(t_fail2 + 4.0, durations[0] + durations[1])
    t_end3 = min(t_fail3 + 5.0, total_len)
    
    filter_parts = []
    concat_inputs = ""
    for idx, (sc, dur) in enumerate(zip(scenes_en, durations)):
        st = sc['video_start']
        filter_parts.append(f"[0:v]trim=start={st:.2f}:duration={dur:.2f},setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[sc{idx}];")
        concat_inputs += f"[sc{idx}]"
    
    filter_parts.append(
        f"{concat_inputs}concat=n=3:v=1:a=0[raw_seq];"
        f"[raw_seq]split=2[in_bg][in_fg];"
        f"[in_bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.22[bg];"
        f"[in_fg]scale=1080:608,drawbox=x=0:y=0:w=iw:h=ih:color=yellow@0.7:t=5[fg];"
        f"[bg][fg]overlay=x=0:y=656[base_video];"
        f"[base_video][2:v]overlay=x=0:y=1320:enable='between(t,{t_fail1:.2f},{t_end1:.2f}) + between(t,{t_fail2:.2f},{t_end2:.2f}) + between(t,{t_fail3:.2f},{t_end3:.2f})'[with_fail];"
        f"[with_fail]ass={ass_path},fade=t=out:st={total_len-1.0:.2f}:d=1.0[vfinal]"
    )
    
    out_mp4 = "/root/VIDEO_02_POLICE.mp4"
    subprocess.run([
        "ffmpeg", "-y", 
        "-i", "/root/.gemini/antigravity-cli/scratch/raw_materials/Physics_Gaming/2026-09-25/beamng_test.mp4", 
        "-i", audio_mixed, 
        "-i", "/tmp/kids_graphic_assets_fhd/fail_en_fhd.png", 
        "-filter_complex", "".join(filter_parts), 
        "-map", "[vfinal]", 
        "-map", "1:a", 
        "-t", f"{total_len:.2f}", 
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", 
        "-c:a", "aac", "-b:a", "192k", 
        "-movflags", "+faststart", out_mp4
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"SUCCESS: {out_mp4}")

asyncio.run(build())
