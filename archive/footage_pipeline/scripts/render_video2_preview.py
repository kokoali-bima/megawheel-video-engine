#!/usr/bin/env python3
"""
Render Video 2 Preview for MegaWheel Kids (Preview Only - Pending Approval)
Theme: Cars & Buses VS Extreme Road Obstacles
Vehicles:
1. White 4x4 Off-Road Jeep (Flips and crashes)
2. Giant Double Decker Bus (Loses wheels and crashes)
3. 6x6 Monster Dually Truck (Crushes obstacles & wins!)

Visuals: Clean 9:16, Safe Zone compliant, No fake UI buttons.
Audio: Calibrated volume balances, dynamic SFX, clear narration.
SOP: RENDER ONLY, NO AUTO-UPLOAD.
"""

import os
import subprocess
import asyncio
import edge_tts
from core.tracker import VideoPublishingTracker

OUTPUT_DIR = "/tmp/render_video2_preview"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUT_MP4 = "/root/renders/youtube_shorts_batch/VIDEO_02_JEEP_BUS_MONSTER_TRUCK.mp4"
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
        "badge": "[ LEVEL 1 : WHITE 4X4 OFF-ROAD JEEP ]",
        "text": "White 4x4 Jeep speeding up the road! Look at those big tires... Oh no! It lost control, flipped upside down and crashed! Failed!",
        "video_start": 72.0,
        "video_dur": 13.5,
        "fail_trigger": 11.5
    },
    {
        "badge": "[ LEVEL 2 : GIANT DOUBLE DECKER BUS ]",
        "text": "Giant double decker city bus taking on the challenge! Can this giant make it? Whoops! The wheels ripped off and it crashed into the ditch! Failed again!",
        "video_start": 114.0,
        "video_dur": 15.0,
        "fail_trigger": 12.5
    },
    {
        "badge": "[ LEVEL 3 : 6X6 MONSTER DUALLY TRUCK ]",
        "text": "Massive six-wheel dually truck is ready! Full throttle! Look at those heavy-duty wheels conquering every obstacle! HOREEE! Yay! We made it across the finish line! Tap like if you enjoyed this, dislike if you didn't, and smash SUBSCRIBE to MegaWheel Kids!",
        "video_start": 222.0,
        "video_dur": 20.0,
        "win_trigger": 8.5
    }
]

async def main():
    print("=" * 60)
    print("  RENDERING VIDEO 2 PREVIEW (JEEP, BUS & MONSTER TRUCK)")
    print("=" * 60)

    durations = [sc["video_dur"] for sc in scenes]
    total_len = sum(durations)

    # 1. TTS Generation
    audio_files = []
    for i, sc in enumerate(scenes):
        f_mp3 = f"{OUTPUT_DIR}/v_{i}.mp3"
        comm = edge_tts.Communicate(sc["text"], "en-US-AnaNeural", rate="+2%", pitch="+2Hz")
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

    # 2. Audio Mixing
    t_fail1 = scenes[0]["fail_trigger"]
    t_fail2 = durations[0] + scenes[1]["fail_trigger"]
    t_win3  = durations[0] + durations[1] + scenes[2]["win_trigger"]

    audio_mixed = f"{OUTPUT_DIR}/audio_mixed.mp3"
    a_game_filters = ""
    a_concat = ""
    for i, sc in enumerate(scenes):
        st = sc["video_start"]
        dur = sc["video_dur"]
        a_game_filters += f"[2:a]atrim=start={st:.2f}:duration={dur:.2f},asetpts=PTS-STARTPTS[g_sc{i}];"
        a_concat += f"[g_sc{i}]"
    a_game_filters += f"{a_concat}concat=n=3:v=0:a=1,volume=0.85[game_sfx];"

    complex_audio = (
        a_game_filters +
        f"[0:a]volume=1.55[voice];"
        f"[1:a]volume=0.12,atrim=duration={total_len:.2f},afade=t=out:st={total_len-1.5:.2f}:d=1.5[bgm];"
        f"[3:a]adelay={int(t_fail1*1000)}|{int(t_fail1*1000)},volume=0.85[sfx1];"
        f"[4:a]adelay={int(t_fail2*1000)}|{int(t_fail2*1000)},volume=0.85[sfx2];"
        f"[5:a]adelay={int(t_win3*1000)}|{int(t_win3*1000)},volume=0.75[sfx3_win];"
        f"[6:a]adelay={int(t_win3*1000)}|{int(t_win3*1000)},volume=0.55[sfx3_cheer];"
        f"[voice][bgm][game_sfx][sfx1][sfx2][sfx3_win][sfx3_cheer]amix=inputs=7:duration=first:dropout_transition=2,volume=1.8[aout]"
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

    # 3. ASS Subtitle (Top Badges)
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
    for idx, (sc, dur) in enumerate(zip(scenes, durations)):
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
    title = "Jeep & Giant Bus VS Extreme Road Obstacles! 🚌💥 Monster Truck Wins! #Shorts"
    tags = ["Shorts", "BeamNG", "Jeep", "Bus", "MonsterTruck", "CarCrash", "Obstacles", "Kids", "Gaming"]
    VideoPublishingTracker.register_render(
        video_id="VIDEO_02_JEEP_BUS_MONSTER_TRUCK",
        title=title,
        theme="Extreme Road Obstacles",
        vehicles=["White 4x4 Off-Road Jeep", "Giant Double Decker Bus", "6x6 Monster Dually Truck"],
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
