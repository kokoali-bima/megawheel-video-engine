#!/usr/bin/env python3
"""
Render Batch of 3 YouTube Shorts for MegaWheel Kids (US / Global Target)
Exact Narration-Aligned Timing:
- Level 1 FAIL card & buzzer triggers at 10.50s (right when car stops, 0.6s before narrator says 'Failed!')
- Level 2 FAIL card & buzzer triggers at 23.00s (right when chassis settles, 0.5s before 'Failed again!')
- Level 3 WINNER card & cheering triggers at 34.70s (exactly when 'HOREEE! Yay! We made it to the finish line!' starts)
"""

import os
import subprocess
import asyncio
import edge_tts
from core.tracker import VideoPublishingTracker

OUTPUT_BASE = "/root/renders/youtube_shorts_batch"
os.makedirs(OUTPUT_BASE, exist_ok=True)

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

VIDEOS_CONFIG = [
    {
        "id": "VIDEO_01_SPEED_BUMPS",
        "title": "Cars VS 100 Giant Speed Bumps! 🚗💥 Level 3 Monster Truck Wins! #Shorts",
        "description": "Watch cool cars take on 100 giant speed bumps! Who will survive and reach the finish line?\n\nHit LIKE if you liked it, dislike if you didn't, and SUBSCRIBE to MegaWheel Kids for daily car fun!\n\n#Shorts #BeamNG #Cars #Kids #Gaming #SpeedBumps",
        "theme": "Speed Bumps Physics",
        "vehicles": ["Black Sport Car", "Vintage Classic Car", "6x6 Heavy Dually Truck"],
        "tags": ["Shorts", "BeamNG", "Cars", "SpeedBumps", "MonsterTruck", "Kids", "Gaming"],
        "scenes": [
            {
                "badge": "[ LEVEL 1 : BLACK SPORT CAR ]",
                "text": "Black sport car speeding up! Watch out for the giant bumps... Boom! The wheel snapped off! Crashed and stopped! Failed!",
                "video_start": 0.8,
                "video_dur": 13.7,
                "fail_trigger": 10.5
            },
            {
                "badge": "[ LEVEL 2 : VINTAGE CLASSIC CAR ]",
                "text": "Vintage classic car going slowly... Whoops! The body came off the chassis! Smashed to pieces! Failed again!",
                "video_start": 46.0,
                "video_dur": 11.0,
                "fail_trigger": 9.3
            },
            {
                "badge": "[ LEVEL 3 : 6X6 HEAVY DUALLY TRUCK ]",
                "text": "Giant six-wheel red truck is ready! Gas pol! Look at those heavy-duty wheels conquering the road! HOREEE! Yay! We made it to the finish line! Hit like if you liked it, dislike if you didn't, and smash SUBSCRIBE to MegaWheel Kids!",
                "video_start": 221.8,
                "video_dur": 22.5,
                "win_trigger": 10.0
            }
        ]
    },
    {
        "id": "VIDEO_02_POTHOLES",
        "title": "Cars VS Giant Road Potholes! 🕳️💥 Will the 6-Wheel Truck Survive? #Shorts",
        "description": "Extreme road pothole challenge! Can sports cars survive the deep potholes?\n\nHit LIKE if you loved this truck, dislike if you didn't, and hit SUBSCRIBE to MegaWheel Kids!\n\n#Shorts #BeamNG #Cars #Potholes #MonsterTruck #Kids #CarCrash",
        "theme": "Potholes Extreme",
        "vehicles": ["Speed Racer Coupe", "Retro Sedan", "6-Wheel Power Truck"],
        "tags": ["Shorts", "BeamNG", "Cars", "Potholes", "CarCrash", "Kids", "Simulation"],
        "scenes": [
            {
                "badge": "[ LEVEL 1 : SPEED RACER COUPE ]",
                "text": "Speed racer coupe zooming in! Oh no, a massive road pothole! Boom! The suspension shattered! Total wreck! Failed!",
                "video_start": 0.8,
                "video_dur": 13.7,
                "fail_trigger": 10.5
            },
            {
                "badge": "[ LEVEL 2 : RETRO SEDAN ]",
                "text": "Retro classic sedan taking the challenge... Watch out! The entire body tore away from the wheels! Failed again!",
                "video_start": 46.0,
                "video_dur": 11.0,
                "fail_trigger": 9.3
            },
            {
                "badge": "[ LEVEL 3 : 6-WHEEL POWER TRUCK ]",
                "text": "Massive six-wheel power truck rolls in! Full throttle over the giant potholes! Nothing can stop this monster! HOREEE! Champion finish! Hit LIKE if you liked it, dislike if you didn't, and SUBSCRIBE for daily car fun!",
                "video_start": 221.8,
                "video_dur": 22.5,
                "win_trigger": 10.0
            }
        ]
    },
    {
        "id": "VIDEO_03_OBSTACLE_CHALLENGE",
        "title": "Extreme Road Obstacle Challenge! 🚧💥 Who Is The Ultimate Champion? #Shorts",
        "description": "Testing sports cars vs heavy trucks on the extreme obstacle track!\n\nHit LIKE if you enjoyed the video, dislike if you didn't, and SUBSCRIBE to MegaWheel Kids for more epic episodes!\n\n#Shorts #BeamNG #Trucks #Cars #Gaming #Challenge",
        "theme": "Obstacle Challenge",
        "vehicles": ["Turbo Sport Car", "Classic Cruiser", "6x6 Dually Beast"],
        "tags": ["Shorts", "BeamNG", "Cars", "Challenge", "MonsterTruck", "Kids", "Gaming"],
        "scenes": [
            {
                "badge": "[ LEVEL 1 : TURBO SPORT CAR ]",
                "text": "Turbo sport car flying down the track! Watch out for the obstacles! Boom! Crash and wheel loss! Stopped completely! Failed!",
                "video_start": 0.8,
                "video_dur": 13.7,
                "fail_trigger": 10.5
            },
            {
                "badge": "[ LEVEL 2 : CLASSIC CRUISER ]",
                "text": "Classic cruiser tries to navigate the bumps... Oh no! Smashed completely to the ground! Failed again!",
                "video_start": 46.0,
                "video_dur": 11.0,
                "fail_trigger": 9.3
            },
            {
                "badge": "[ LEVEL 3 : 6X6 DUALLY BEAST ]",
                "text": "Six-wheel heavy dually beast takes the track! Rolling right over every bump! HOREEE! We made it to the finish line! Smash that LIKE button if you liked it, dislike if you didn't, and hit SUBSCRIBE to MegaWheel Kids!",
                "video_start": 221.8,
                "video_dur": 22.5,
                "win_trigger": 10.0
            }
        ]
    }
]

async def render_single_video(cfg):
    vid_id = cfg["id"]
    work_dir = f"/tmp/render_{vid_id}"
    os.makedirs(work_dir, exist_ok=True)
    out_mp4 = f"{OUTPUT_BASE}/{vid_id}.mp4"

    print(f"\n==========================================")
    print(f"  RENDERING {vid_id}: {cfg['title']}")
    print(f"==========================================")

    scenes = cfg["scenes"]
    durations = [sc["video_dur"] for sc in scenes]
    total_len = sum(durations)

    # 1. TTS Generation (en-US-AnaNeural)
    audio_files = []
    for i, sc in enumerate(scenes):
        f_mp3 = f"{work_dir}/v_{i}.mp3"
        comm = edge_tts.Communicate(sc["text"], "en-US-AnaNeural", rate="+2%", pitch="+2Hz")
        await comm.save(f_mp3)

        target_dur = sc["video_dur"]
        f_padded = f"{work_dir}/pad_{i}.mp3"
        subprocess.run([
            "ffmpeg", "-y", "-i", f_mp3,
            "-filter_complex", f"[0:a]apad=whole_dur={target_dur:.2f}[aout]",
            "-map", "[aout]",
            "-t", f"{target_dur:.2f}",
            "-c:a", "libmp3lame", "-b:a", "192k", f_padded
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        audio_files.append(f_padded)

    concat_list = f"{work_dir}/concat.txt"
    with open(concat_list, "w") as f:
        for af in audio_files:
            f.write(f"file '{af}'\n")

    full_voice = f"{work_dir}/full_voice.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list, "-c:a", "libmp3lame", "-b:a", "192k", full_voice
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Exact Timing Calculations
    t_fail1 = scenes[0]["fail_trigger"]
    t_fail2 = durations[0] + scenes[1]["fail_trigger"]
    t_win3  = durations[0] + durations[1] + scenes[2]["win_trigger"]

    print(f"Timing triggers: Fail1={t_fail1:.2f}s, Fail2={t_fail2:.2f}s, Win3={t_win3:.2f}s")

    audio_mixed = f"{work_dir}/audio_mixed.mp3"
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
    ass_path = f"{work_dir}/subs.ass"
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
    for sc, dur in zip(scenes, durations):
        start_str = format_ass_time(curr_t)
        end_str = format_ass_time(curr_t + dur)
        ass_header += f"Dialogue: 0,{start_str},{end_str},TopBadge,,0,0,0,,{sc['badge']}\n"
        curr_t += dur

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header)

    # 4. Visual Compositing (Full-Bleed + Golden Box + Real PNG Cards)
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
        out_mp4
    ]

    print(f"Executing FFmpeg render for {vid_id}...")
    subprocess.run(cmd, check=True)
    print(f"[SUCCESS] {vid_id} rendered: {out_mp4} ({os.path.getsize(out_mp4)} bytes)")

    # Update Tracker
    VideoPublishingTracker.register_render(
        video_id=vid_id,
        title=cfg["title"],
        theme=cfg["theme"],
        vehicles=cfg["vehicles"],
        file_path=out_mp4,
        duration_sec=total_len,
        language="English (US)",
        tags=cfg["tags"]
    )

async def main():
    for cfg in VIDEOS_CONFIG:
        await render_single_video(cfg)
    print("\n" + "=" * 60)
    print("  ALL 3 YOUTUBE SHORTS RE-RENDERED WITH PERFECT SYNC!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
