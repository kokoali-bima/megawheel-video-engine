#!/usr/bin/env python3
"""
Full-Length 45s Kids Physics Challenge - Master Edition
Features:
- Full Uncut Runs (Car launches, hits bumps, crashes/flies completely until stopping)
- Soft, Friendly Kids Narrator (en-US-AnaNeural / en-US-EmmaNeural)
- Aesthetic Styled Frame Box (No plain black bars, elegant styled container)
- Clean, No-Tofu Emojis Typography (CRASH! in bold red, WINNER! in bold gold)
- Master Soundscape: Soft Playful BGM, Crystal Clear Voice, Cartoon Impact & Cheering SFX
"""

import os
import sys
import json
import asyncio
import subprocess
from pydub import AudioSegment
import edge_tts
from core.validator import PreflightValidator

def format_ass_time(sec: float) -> str:
    hrs = int(sec // 3600)
    mins = int((sec % 3600) // 60)
    secs = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100: cs = 99
    return f"{hrs:d}:{mins:02d}:{secs:02d}.{cs:02d}"

async def gen_voice(text: str, out_file: str, voice: str = "en-US-AnaNeural", rate: str = "+0%", pitch: str = "+0Hz"):
    c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await c.save(out_file)

def main():
    print("=== BUILDING FULL-LENGTH 45s KIDS MASTER VIDEO ===")
    work_dir = "/tmp/kids_full_v6"
    os.makedirs(work_dir, exist_ok=True)
    source_video = "/tmp/speed_bumps.mp4"
    bgm_file = "/tmp/kids_cheerful_bgm.mp3"
    sfx_fail = "/tmp/sfx_fail.wav"
    sfx_cheer = "/tmp/sfx_cheer.wav"
    
    # 3 Segmen UTUH (Durasi total ~44 detik)
    segments = [
        {
            "id": 1,
            "title": "ROUND 1",
            "car_name": "Red Sedan",
            "video_start": 6.80,
            "video_dur": 12.0, # Full run sampai mobil remuk total
            "intro_text": "Round one! Look at the red car speeding up!",
            "intro_offset_s": 0.5,
            "event_text": "Oh no! It crashed into pieces!",
            "event_offset_s": 3.6, # Detik benturan keras
            "sfx": sfx_fail,
            "sfx_offset_s": 3.5,
            "badge_text": "CRASH!",
            "badge_color": "&H003333FF", # Bright Red
            "badge_start": 3.6,
            "badge_dur": 3.0
        },
        {
            "id": 2,
            "title": "ROUND 2",
            "car_name": "Black SUV",
            "video_start": 48.30,
            "video_dur": 15.0, # Full run sampai mobil jatuh ke dasar jurang
            "intro_text": "Round two! Here comes the big black SUV!",
            "intro_offset_s": 0.5,
            "event_text": "Whoa! It flew right off the cliff! Failed!",
            "event_offset_s": 3.3, # Detik meluncur ke jurang
            "sfx": sfx_fail,
            "sfx_offset_s": 3.2,
            "badge_text": "FAILED!",
            "badge_color": "&H003333FF", # Bright Red
            "badge_start": 3.3,
            "badge_dur": 3.0
        },
        {
            "id": 3,
            "title": "ROUND 3",
            "car_name": "Classic Car",
            "video_start": 177.50,
            "video_dur": 15.0, # Full run melompat mulus & jalan terus
            "intro_text": "Final round! Can this classic car cross the speed bumps?",
            "intro_offset_s": 0.5,
            "event_text": "Yay! A super smooth jump! We found our champion!",
            "event_offset_s": 3.5, # Detik mendarat mulus
            "sfx": sfx_cheer,
            "sfx_offset_s": 3.4,
            "badge_text": "WINNER!",
            "badge_color": "&H0000D7FF", # Bright Gold
            "badge_start": 3.5,
            "badge_dur": 4.0
        }
    ]
    
    total_dur_s = sum(s["video_dur"] for s in segments)
    total_timeline_ms = int(total_dur_s * 1000)
    print(f"Total Video Target Duration: {total_dur_s:.1f} seconds")
    
    rendered_clips = []
    voice_track = AudioSegment.silent(duration=total_timeline_ms)
    sfx_track = AudioSegment.silent(duration=total_timeline_ms)
    ass_events = []
    
    current_offset_ms = 0
    
    # 1. Render Each Segment with Visual Frame Box Layout
    print("\n[Step 1] Rendering 9:16 Video with Aesthetic Card Frame Box...")
    for i, seg in enumerate(segments):
        base_s = current_offset_ms / 1000.0
        clip_out = f"{work_dir}/clip_{seg['id']}.mp4"
        
        # Frame Box Filter: scale 1080:608, rounded frame box background effect
        # Top banner with round title + central video box + bottom badge zone
        vf_box = (
            f"scale=1040:585:force_original_aspect_ratio=decrease,"
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x141722,"
            f"drawbox=x=16:y=663:w=1048:h=593:color=0x38bdf8@0.8:t=4," # Cyan/Blue Card Border
            f"drawtext=text='PHYSICS SPEED BUMP CHALLENGE':font='Arial':fontsize=42:fontcolor=white:x=(w-text_w)/2:y=380:shadowcolor=black:shadowx=2:shadowy=2,"
            f"drawtext=text='{seg['title']}':font='Arial':fontsize=56:fontcolor=0xffd700:x=(w-text_w)/2:y=460:shadowcolor=black:shadowx=2:shadowy=2"
        )
        
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(seg["video_start"]),
            "-i", source_video,
            "-t", str(seg["video_dur"]),
            "-vf", vf_box,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-an",
            clip_out
        ]
        subprocess.run(cmd, check=True)
        rendered_clips.append(clip_out)
        
        # 2. Soft & Friendly Kids Voiceover
        intro_file = f"{work_dir}/intro_{seg['id']}.mp3"
        asyncio.run(gen_voice(seg["intro_text"], intro_file, voice="en-US-AnaNeural", rate="+2%"))
        intro_aud = AudioSegment.from_file(intro_file).normalize() - 1.0
        intro_pos = current_offset_ms + int(seg["intro_offset_s"] * 1000)
        voice_track = voice_track.overlay(intro_aud, position=intro_pos)
        
        event_file = f"{work_dir}/event_{seg['id']}.mp3"
        asyncio.run(gen_voice(seg["event_text"], event_file, voice="en-US-AnaNeural", rate="+4%", pitch="+1Hz"))
        event_aud = AudioSegment.from_file(event_file).normalize() - 0.5
        event_pos = current_offset_ms + int(seg["event_offset_s"] * 1000)
        voice_track = voice_track.overlay(event_aud, position=event_pos)
        
        # 3. SFX
        if seg.get("sfx") and os.path.exists(seg["sfx"]):
            sfx_aud = AudioSegment.from_file(seg["sfx"]).normalize() - 2.0
            sfx_pos = current_offset_ms + int(seg["sfx_offset_s"] * 1000)
            sfx_track = sfx_track.overlay(sfx_aud, position=sfx_pos)
            
        # 4. Clean Badge (.ASS) without broken emojis
        b_start = base_s + seg["badge_start"]
        b_end = b_start + seg["badge_dur"]
        style_name = "WinStyle" if seg["id"] == 3 else "FailStyle"
        ass_events.append(
            f"Dialogue: 0,{format_ass_time(b_start)},{format_ass_time(b_end)},{style_name},,0,0,0,,{{\\t(0,120,\\fscx120\\fscy120)\\t(120,240,\\fscx100\\fscy100)}}{seg['badge_text']}"
        )
        
        current_offset_ms += int(seg["video_dur"] * 1000)

    # 5. Master Audio Mix with Gentle BGM
    print("\n[Step 2] Mixing Master Audio (Gentle Kids BGM + Soft Natural Voice + SFX)...")
    bgm = AudioSegment.from_file(bgm_file)
    while len(bgm) < total_timeline_ms:
        bgm = bgm + bgm
    bgm = bgm[:total_timeline_ms] - 20.0 # Soft background rhythm
    
    master_audio = bgm.overlay(sfx_track).overlay(voice_track)
    master_wav = f"{work_dir}/master_audio.wav"
    master_audio.export(master_wav, format="wav")
    
    # 6. Generate Clean Stylish Subtitle File
    print("\n[Step 3] Generating Clean ASS Badge Styles...")
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: FailStyle,Arial Black,90,&H000000FF,&H000000FF,&H00FFFFFF,&H80000000,-1,0,0,0,100,100,0,0,1,8,4,2,40,40,460,1
Style: WinStyle,Arial Black,100,&H0000D7FF,&H0000D7FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,4,2,40,40,460,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_file = f"{work_dir}/clean_badges.ass"
    with open(ass_file, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(ass_events))
        
    # 7. Merge Clips & Finalize MP4
    print("\n[Step 4] Finalizing 45s Full-Length Masterpiece...")
    concat_txt = f"{work_dir}/concat.txt"
    with open(concat_txt, "w") as f:
        for c in rendered_clips:
            f.write(f"file '{os.path.abspath(c)}'\n")
            
    final_output = "/tmp/kids_physics_45s_masterpiece.mp4"
    escaped_ass = ass_file.replace(":", "\\:").replace("'", "\\'")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-i", master_wav,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-vf", f"ass={escaped_ass}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-ac", "2",
        "-shortest",
        "-movflags", "+faststart",
        final_output
    ]
    
    subprocess.run(cmd, check=True)
    
    # 8. QA Check
    print("\n[Step 5] Pre-Flight QA Verification...")
    qa = PreflightValidator.audit_video(final_output)
    print(json.dumps(qa, indent=2))
    
    if qa.get("status") == "PASSED":
        print(f"\n[SUCCESS] Final Video Created: {final_output}")
    else:
        print(f"\n[ERROR] QA Failed: {qa.get('reason')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
