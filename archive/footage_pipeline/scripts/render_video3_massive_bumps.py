#!/usr/bin/env python3
"""
Render Video 3: Cars VS Massive Metal Speed Bumps & Cliff
Features:
- 57s Fast-Paced Exciting Action (Start to finish per car)
- Powerful Roaring Engine SFX (Vroom + Acceleration + Impact Bangs)
- 100% Clean Audio Mix (No source audio, 0% Content ID Notice risk)
- Brand New Obstacle: Massive Metal Speed Bumps on Cliffside
- Line-up:
  1. Red GT Race Car (Flies off bumps down the cliff)
  2. White Luxury Sports Car (Shatters wheels and tumbles)
  3. Blue 4x4 Off-Road Jeep (Conquers the massive bumps & Wins!)
- Strict Preview-Only Mode (RENDERED_PENDING_APPROVAL)
"""

import os
import subprocess
import asyncio
import edge_tts
from core.tracker import VideoPublishingTracker

OUTPUT_DIR = "/tmp/render_v3_massive_bumps"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUT_MP4 = "/root/renders/youtube_shorts_batch/VIDEO_03_MASSIVE_BUMPS_CHAMPION.mp4"
os.makedirs(os.path.dirname(OUT_MP4), exist_ok=True)

SOURCE_VIDEO = "/root/local_videos/physics/beamng_massive_speedbumps.mp4"
BGM_FILE = "/tmp/kids_cheerful_bgm.mp3"
SFX_FAIL = "/tmp/sfx_fail.wav"
SFX_WIN = "/tmp/sfx_win.wav"
SFX_CHEER = "/tmp/sfx_cheer.wav"
SFX_ENGINE = "/tmp/sfx_engine_vroom.wav"
SFX_CRASH = "/tmp/sfx_crash_impact.wav"
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
        "badge": "[ LEVEL 1 : RED GT RACE CAR ]",
        "text": "Level one: Red GT race car accelerating at top speed! Vroom! Watch out for the massive metal bumps... Boom! Launched into the air and tumbling down the cliff! Failed!",
        "video_start": 0.0,
        "video_dur": 18.0,
        "fail_trigger": 14.5
    },
    {
        "badge": "[ LEVEL 2 : WHITE LUXURY SPORTS CAR ]",
        "text": "Level two: White luxury sports car charging down the road! Roaring engine! Whoops! The massive bumps shattered the wheels! Total crash down the mountain! Failed again!",
        "video_start": 72.0,
        "video_dur": 17.0,
        "fail_trigger": 13.5
    },
    {
        "badge": "[ LEVEL 3 : BLUE 4X4 OFF-ROAD JEEP ]",
        "text": "Level three: Blue 4x4 Off-Road Jeep rolls in! Look at those heavy-duty wheels! Full throttle over the massive bumps! Smooth landing! HOREEE! Yay! We made it safely across to the finish line! Tap like if you enjoyed it, dislike if you didn't, and smash SUBSCRIBE to MegaWheel Kids!",
        "video_start": 142.0,
        "video_dur": 22.0,
        "win_trigger": 12.5
    }
]

async def main():
    print("=" * 60)
    print("  RENDERING VIDEO 3: MASSIVE BUMPS & ROARING ENGINES (57s)")
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

    # 2. Audio Mixing with Roaring Engine & Crash Impact SFX
    t_fail1 = scenes[0]["fail_trigger"]
    t_fail2 = durations[0] + scenes[1]["fail_trigger"]
    t_win3  = durations[0] + durations[1] + scenes[2]["win_trigger"]

    audio_mixed = f"{OUTPUT_DIR}/audio_mixed.mp3"

    complex_audio = (
        f"[0:a]volume=1.60[voice];"
        f"[1:a]volume=0.10,atrim=duration={total_len:.2f},afade=t=out:st={total_len-1.5:.2f}:d=1.5[bgm];"
        f"[2:a]volume=0.65,aloop=loop=-1:size=2e+09,atrim=duration={total_len:.2f}[engine_loop];"
        f"[3:a]adelay={int(t_fail1*1000)}|{int(t_fail1*1000)},volume=0.90[sfx1_fail];"
        f"[4:a]adelay={int(t_fail2*1000)}|{int(t_fail2*1000)},volume=0.90[sfx2_fail];"
        f"[5:a]adelay={int(t_win3*1000)}|{int(t_win3*1000)},volume=0.75[sfx3_win];"
        f"[6:a]adelay={int(t_win3*1000)}|{int(t_win3*1000)},volume=0.55[sfx3_cheer];"
        f"[7:a]adelay={int((t_fail1-1.0)*1000)}|{int((t_fail1-1.0)*1000)},volume=1.2[crash1];"
        f"[7:a]adelay={int((t_fail2-1.0)*1000)}|{int((t_fail2-1.0)*1000)},volume=1.2[crash2];"
        f"[voice][bgm][engine_loop][sfx1_fail][sfx2_fail][sfx3_win][sfx3_cheer][crash1][crash2]amix=inputs=9:duration=first:dropout_transition=2,volume=1.7[aout]"
    )

    subprocess.run([
        "ffmpeg", "-y",
        "-i", full_voice,
        "-i", BGM_FILE,
        "-i", SFX_ENGINE,
        "-i", SFX_FAIL,
        "-i", SFX_FAIL,
        "-i", SFX_WIN,
        "-i", SFX_CHEER,
        "-i", SFX_CRASH,
        "-filter_complex", complex_audio,
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "192k",
        audio_mixed
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. ASS Subtitles (Top Badges in Safe Zone)
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
    title = "Cars VS Massive Speed Bumps & Cliff! 🚗💥 Blue 4x4 Jeep Wins! #Shorts"
    tags = ["Shorts", "BeamNG", "SpeedBumps", "CliffCrash", "Jeep", "Porsche", "RaceCar", "Kids", "Gaming"]
    VideoPublishingTracker.register_render(
        video_id="VIDEO_03_MASSIVE_BUMPS_CHAMPION",
        title=title,
        theme="Massive Metal Speed Bumps & Cliff",
        vehicles=["Red GT Race Car", "White Luxury Sports Car", "Blue 4x4 Off-Road Jeep"],
        file_path=OUT_MP4,
        duration_sec=total_len,
        language="English (US)",
        tags=tags
    )
    print("\n" + "=" * 60)
    print(f"  [REGISTERED] Status: RENDERED_PENDING_APPROVAL")
    print(f"  [READY FOR REVIEW] File: {OUT_MP4}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
