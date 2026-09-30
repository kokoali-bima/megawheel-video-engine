#!/usr/bin/env python3
"""
Render Video 3 Perfected & Audited with Complete Outro:
- Zero intruder clips: Level 3 starts exactly at 689.85s (Soliad start line).
- Extended transition time and aftermath buffer between scenes.
- Complete outro CTA: "Tap LIKE if you enjoyed this video, DISLIKE if you didn't, and smash SUBSCRIBE to MegaWheel Kids!"
- 1-to-1 Frame & Voice & Badge synchronization.
- Authentic BeamNG engine audio extraction.
- Total duration: 47.0s (Shorts format).
- Strict Preview-Only mode (RENDERED_PENDING_APPROVAL).
"""

import os
import subprocess
import asyncio
import edge_tts
from core.tracker import VideoPublishingTracker

OUTPUT_DIR = "/tmp/render_v3_clean_synced"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUT_MP4 = "/root/renders/youtube_shorts_batch/VIDEO_03_SYNCED_PERFECT_CHAMPION.mp4"
os.makedirs(os.path.dirname(OUT_MP4), exist_ok=True)

SOURCE_VIDEO = "/root/local_videos/physics/beamng_test.mp4"
BGM_FILE = "/tmp/kids_cheerful_bgm.mp3"
SFX_FAIL = "/tmp/sfx_fail.wav"
SFX_WIN = "/tmp/sfx_win.wav"
SFX_CHEER = "/tmp/sfx_cheer.wav"
FAIL_PNG = "/tmp/kids_graphic_assets_fhd/fail_en_fhd.png"
WIN_PNG = "/tmp/kids_graphic_assets_fhd/win_en_fhd.png"

def format_ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

scenes = [
    {
        "badge": "[ LEVEL 1 : SILVER FASTBACK MUSCLE CAR ]",
        "text": "Level one! Silver Muscle Car speeding up! Whoa! Flying airborne flip and crashing down! Failed!",
        "video_start": 160.0,
        "video_dur": 12.0,
        "clip_dur": 12.0,
        "fail_trigger": 6.5,
        "rate": "+10%"
    },
    {
        "badge": "[ LEVEL 2 : POLICE SHERIFF CRUISER ]",
        "text": "Level two! Police Sheriff Cruiser in hot pursuit! Siren blaring! Whoops! Launched into the air and rolling upside down! Failed again!",
        "video_start": 608.0,
        "video_dur": 16.0,
        "clip_dur": 16.0,
        "fail_trigger": 11.0,
        "rate": "+10%"
    },
    {
        "badge": "[ LEVEL 3 : BLUE & WHITE SOLIAD RACE CAR ]",
        "text": "Level three! Blue and White Soliad Race Car charges the track! Look at that balance, gliding across on all four wheels! HOREEE! We have a champion winner! Tap LIKE if you enjoyed this video, DISLIKE if you didn't, and smash SUBSCRIBE to MegaWheel Kids!",
        "video_start": 689.85,
        "video_dur": 19.0,
        "clip_dur": 15.15,
        "win_trigger": 9.2,
        "rate": "+12%"
    }
]

async def main():
    print("=" * 60)
    print("  RENDERING VIDEO 3 (WITH COMPLETE OUTRO & PERFECT SYNC, 47.0s)")
    print("=" * 60)

    durations = [sc["video_dur"] for sc in scenes]
    total_len = sum(durations)

    # 1. TTS Generation
    audio_files = []
    for i, sc in enumerate(scenes):
        f_mp3 = f"{OUTPUT_DIR}/v_{i}.mp3"
        comm = edge_tts.Communicate(sc["text"], "en-US-AnaNeural", rate=sc["rate"], pitch="+2Hz")
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

    # 2. Extract Authentic BeamNG Engine Audio
    t_fail1 = scenes[0]["fail_trigger"]
    t_fail2 = durations[0] + scenes[1]["fail_trigger"]
    t_win3  = durations[0] + durations[1] + scenes[2]["win_trigger"]

    audio_mixed = f"{OUTPUT_DIR}/audio_mixed.mp3"

    a_game_filters = ""
    a_concat = ""
    for i, sc in enumerate(scenes):
        st = sc["video_start"]
        clip_dur = sc["clip_dur"]
        target_dur = sc["video_dur"]
        # if target_dur > clip_dur, apad it
        a_game_filters += f"[2:a]atrim=start={st:.2f}:duration={clip_dur:.2f},asetpts=PTS-STARTPTS,apad=whole_dur={target_dur:.2f}[g_sc{i}];"
        a_concat += f"[g_sc{i}]"
    a_game_filters += f"{a_concat}concat=n=3:v=0:a=1,volume=0.85[real_engine_audio];"

    complex_audio = (
        a_game_filters +
        f"[0:a]volume=1.60[voice];"
        f"[1:a]volume=0.10,atrim=duration={total_len:.2f},afade=t=out:st={total_len-1.5:.2f}:d=1.5[bgm];"
        f"[3:a]adelay={int(t_fail1*1000)}|{int(t_fail1*1000)},volume=0.90[sfx1];"
        f"[4:a]adelay={int(t_fail2*1000)}|{int(t_fail2*1000)},volume=0.90[sfx2];"
        f"[5:a]adelay={int(t_win3*1000)}|{int(t_win3*1000)},volume=0.75[sfx3_win];"
        f"[6:a]adelay={int(t_win3*1000)}|{int(t_win3*1000)},volume=0.55[sfx3_cheer];"
        f"[voice][bgm][real_engine_audio][sfx1][sfx2][sfx3_win][sfx3_cheer]amix=inputs=7:duration=first:dropout_transition=2,volume=1.8[aout]"
    )

    subprocess.run([
        "ffmpeg", "-y",
        "-i", full_voice,
        "-i", BGM_FILE,
        "-i", SOURCE_VIDEO,
        "-i", SFX_FAIL,
        "-i", SFX_FAIL,
        "-i", SFX_WIN,
        "-i", SFX_CHEER,
        "-filter_complex", complex_audio,
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        audio_mixed
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. ASS Subtitle
    ass_path = f"{OUTPUT_DIR}/subs.ass"
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopBadge,DejaVu Sans,34,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,3,3.5,1,8,25,25,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    curr_t = 0.0
    for sc, dur in zip(scenes, durations):
        start_str = format_ass_time(curr_t)
        end_str = format_ass_time(curr_t + dur)
        ass_header += f"Dialogue: 0,{start_str},{end_str},TopBadge,,0,0,0,,{sc['badge']}\n"
        curr_t += dur

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)

    # 4. Clean 9:16 Visual Compositing
    filter_parts = []
    concat_inputs = ""
    for idx, sc in enumerate(scenes):
        st = sc["video_start"]
        clip_dur = sc["clip_dur"]
        target_dur = sc["video_dur"]
        if target_dur > clip_dur:
            tpad_dur = target_dur - clip_dur
            filter_parts.append(
                f"[0:v]trim=start={st:.2f}:duration={clip_dur:.2f},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={tpad_dur:.2f},scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[sc{idx}];"
            )
        else:
            filter_parts.append(
                f"[0:v]trim=start={st:.2f}:duration={clip_dur:.2f},setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[sc{idx}];"
            )
        concat_inputs += f"[sc{idx}]"

    filter_parts.append(f"{concat_inputs}concat=n=3:v=1:a=0[raw_seq];")
    filter_parts.append(f"[raw_seq]split=2[in_bg][in_fg];")
    filter_parts.append(f"[in_bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.22[bg];")
    filter_parts.append(f"[in_fg]scale=1080:608,drawbox=x=0:y=0:w=iw:h=ih:color=yellow@0.7:t=5[fg];")
    filter_parts.append(f"[bg][fg]overlay=x=0:y=656[base_video];")
    filter_parts.append(f"[base_video][2:v]overlay=x=0:y=1320:enable='between(t,{t_fail1:.2f},{durations[0]:.2f}) + between(t,{t_fail2:.2f},{durations[0]+durations[1]:.2f})'[with_fail];")
    filter_parts.append(f"[with_fail][3:v]overlay=x=0:y=1320:enable='between(t,{t_win3:.2f},{total_len:.2f})'[with_badges];")
    filter_parts.append(f"[with_badges]ass={ass_path},fade=t=out:st={total_len-1.0:.2f}:d=1.0[vfinal]")

    full_filter = "".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        "-i", SOURCE_VIDEO,
        "-i", audio_mixed,
        "-i", FAIL_PNG,
        "-i", WIN_PNG,
        "-filter_complex", full_filter,
        "-map", "[vfinal]",
        "-map", "1:a",
        "-t", f"{total_len:.2f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-c:a", "aac", "-b:a", "256k",
        "-map_metadata", "-1",
        "-movflags", "+faststart",
        OUT_MP4
    ]

    print("Rendering video via FFmpeg...")
    subprocess.run(cmd, check=True)
    print(f"[RENDER SUCCESS] {OUT_MP4} ({os.path.getsize(OUT_MP4)} bytes)")

    # 5. Register in Tracker as RENDERED_PENDING_APPROVAL
    title = "Muscle Car & Police Cruiser VS Soliad Race Car! 🏎️💥 Level 3 Wins! #Shorts"
    tags = ["Shorts", "BeamNG", "Police", "MuscleCar", "Soliad", "RaceCar", "CarCrash", "Kids", "Gaming"]
    VideoPublishingTracker.register_render(
        video_id="VIDEO_03_SYNCED_PERFECT_CHAMPION",
        title=title,
        theme="Police & Soliad Race Challenge",
        vehicles=["Silver Fastback Muscle Car", "Police Sheriff Cruiser", "Blue & White Soliad Race Car"],
        file_path=OUT_MP4,
        duration_sec=total_len,
        language="English (US)",
        tags=tags
    )
    print("\n" + "=" * 60)
    print(f"  [REGISTERED] Status: RENDERED_PENDING_APPROVAL")
    print(f"  [READY FOR HUMAN REVIEW] File: {OUT_MP4}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
