#!/usr/bin/env python3
"""
Clean Visual & High-Energy English Audio Video Pipeline
- Minimal Visuals: Screen is clean, showing ONLY impact badges (CRASH! ❌, FAILED! ❌, WINNER! 🏆)
- Crystal-Clear English Narration: Fully normalized voice (loud, clear, professional US accent)
- Balanced Audio Master: Voice at maximum clarity, gentle BGM, punchy SFX
- Verified Video Clips: Red Sedan -> Black SUV -> Classic White Champion
"""

import os
import sys
import json
import asyncio
import subprocess
from pydub import AudioSegment
import edge_tts
from core.compositor import VideoCompositor
from core.validator import PreflightValidator

async def gen_boosted_voice(text: str, out_file: str, voice: str = "en-US-ChristopherNeural", rate: str = "+8%", pitch: str = "+2Hz"):
    c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await c.save(out_file)

def main():
    print("=== BUILDING CLEAN ENGLISH AUDIO-FIRST KIDS PHYSICS VIDEO ===")
    work_dir = "/tmp/kids_english_clean_v5"
    os.makedirs(work_dir, exist_ok=True)
    source_video = "/tmp/speed_bumps.mp4"
    bgm_file = "/tmp/kids_cheerful_bgm.mp3"
    sfx_fail = "/tmp/sfx_fail.wav"
    sfx_cheer = "/tmp/sfx_cheer.wav"
    
    # 3 Segmen Terverifikasi (Durasi 7.0 detik per ronde)
    segments = [
        {
            "id": 1,
            "video_start": 6.80,
            "video_dur": 7.0,
            "intro_text": "Here comes the red sedan!",
            "intro_offset_s": 0.2,
            "event_text": "OH NO! Total crash!",
            "event_offset_s": 3.4, # Detik tepat tabrakan
            "sfx": sfx_fail,
            "sfx_offset_s": 3.3,
            "badge_text": "CRASH! ❌",
            "badge_color": "&H000000FF", # Red outline in ASS
            "badge_start": 3.4,
            "badge_dur": 2.0
        },
        {
            "id": 2,
            "video_start": 48.30, # Mobil SUV Hitam
            "video_dur": 7.0,
            "intro_text": "Next up, the black SUV!",
            "intro_offset_s": 0.2,
            "event_text": "WHOOPS! Flying into the canyon!",
            "event_offset_s": 3.3, # Detik tepat terjun jurang
            "sfx": sfx_fail,
            "sfx_offset_s": 3.2,
            "badge_text": "FAILED! ❌",
            "badge_color": "&H000000FF",
            "badge_start": 3.3,
            "badge_dur": 2.0
        },
        {
            "id": 3,
            "video_start": 177.50, # Mobil Klasik Putih Juara
            "video_dur": 7.0,
            "intro_text": "Can the classic car make it?",
            "intro_offset_s": 0.2,
            "event_text": "YES! Smooth landing, what a champion!",
            "event_offset_s": 3.3, # Detik tepat mendarat
            "sfx": sfx_cheer,
            "sfx_offset_s": 3.2,
            "badge_text": "WINNER! 🏆",
            "badge_color": "&H0000FFFF", # Gold/Yellow in ASS
            "badge_start": 3.3,
            "badge_dur": 2.5
        }
    ]
    
    total_timeline_ms = int(len(segments) * 7.0 * 1000)
    voice_track = AudioSegment.silent(duration=total_timeline_ms)
    sfx_track = AudioSegment.silent(duration=total_timeline_ms)
    rendered_video_clips = []
    ass_events = []
    
    def format_ass_time(sec: float) -> str:
        hrs = int(sec // 3600)
        mins = int((sec % 3600) // 60)
        secs = int(sec % 60)
        cs = int(round((sec - int(sec)) * 100))
        if cs >= 100: cs = 99
        return f"{hrs:d}:{mins:02d}:{secs:02d}.{cs:02d}"
        
    print("\n[Step 1] Rendering 9:16 video clips and generating loud normalized English voice...")
    for i, seg in enumerate(segments):
        base_seg_ms = int(i * 7.0 * 1000)
        
        # 1. Render Video 9:16 Shorts
        clip_out = f"{work_dir}/clip_{seg['id']}.mp4"
        VideoCompositor.render_shorts_segment(
            input_video=source_video,
            start_sec=seg["video_start"],
            duration_sec=seg["video_dur"],
            output_file=clip_out,
            target_w=1080,
            target_h=1920
        )
        rendered_video_clips.append(clip_out)
        
        # 2. Intro Voice (Normalized & Boosted)
        intro_file = f"{work_dir}/intro_{seg['id']}.mp3"
        asyncio.run(gen_boosted_voice(seg["intro_text"], intro_file))
        intro_aud = AudioSegment.from_file(intro_file).normalize() - 1.0 # Loud peak at -1 dBFS
        intro_pos = base_seg_ms + int(seg["intro_offset_s"] * 1000)
        voice_track = voice_track.overlay(intro_aud, position=intro_pos)
        
        # 3. Event Voice (Reaction)
        event_file = f"{work_dir}/event_{seg['id']}.mp3"
        asyncio.run(gen_boosted_voice(seg["event_text"], event_file, pitch="+3Hz", rate="+10%"))
        event_aud = AudioSegment.from_file(event_file).normalize() - 0.5 # Super punchy peak at -0.5 dBFS
        event_pos = base_seg_ms + int(seg["event_offset_s"] * 1000)
        voice_track = voice_track.overlay(event_aud, position=event_pos)
        
        # 4. SFX
        if seg.get("sfx") and os.path.exists(seg["sfx"]):
            sfx_aud = AudioSegment.from_file(seg["sfx"]).normalize() - 4.0
            sfx_pos = base_seg_ms + int(seg["sfx_offset_s"] * 1000)
            sfx_track = sfx_track.overlay(sfx_aud, position=sfx_pos)
            
        # 5. Minimal Punchy Badge ONLY at moment of impact/win
        b_start = (base_seg_ms / 1000.0) + seg["badge_start"]
        b_end = b_start + seg["badge_dur"]
        style_name = "WinBadge" if seg["id"] == 3 else "FailBadge"
        ass_events.append(
            f"Dialogue: 0,{format_ass_time(b_start)},{format_ass_time(b_end)},{style_name},,0,0,0,,{{\\t(0,100,\\fscx125\\fscy125)\\t(100,200,\\fscx100\\fscy100)}}{seg['badge_text']}"
        )

    print("\n[Step 2] Mixing Master Soundscape (Voice 100% Dominant, Gentle BGM, Punchy SFX)...")
    bgm = AudioSegment.from_file(bgm_file)
    while len(bgm) < total_timeline_ms:
        bgm = bgm + bgm
    bgm = bgm[:total_timeline_ms] - 22.0 # Gentle BGM presence (-22 dBFS) so voice is 100% crystal clear
    
    # Master mix
    master_audio = bgm.overlay(sfx_track).overlay(voice_track)
    master_wav = f"{work_dir}/master_audio_loud.wav"
    master_audio.export(master_wav, format="wav")
    
    print("\n[Step 3] Creating minimal badge overlay .ASS...")
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: FailBadge,Arial,84,&H00FFFFFF,&H000000FF,&H000000FF,&H80000000,-1,0,0,0,100,100,0,0,1,8,4,2,40,40,560,1
Style: WinBadge,Arial,92,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,4,2,40,40,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_file = f"{work_dir}/minimal_badges.ass"
    with open(ass_file, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(ass_events))
        
    print("\n[Step 4] Finalizing MP4 with Loud AAC Audio & FastStart...")
    concat_txt = f"{work_dir}/concat.txt"
    with open(concat_txt, "w") as f:
        for c in rendered_video_clips:
            f.write(f"file '{os.path.abspath(c)}'\n")
            
    final_output = "/tmp/kids_physics_english_clean_master.mp4"
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
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg Error:", res.stderr)
        sys.exit(1)
        
    print("\n[Step 5] Auditing Final Output Volume & Stream Parameters...")
    v_res = subprocess.run(["ffmpeg", "-i", final_output, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    for line in v_res.stderr.split("\n"):
        if "max_volume" in line or "mean_volume" in line:
            print("Audio Level:", line.strip())
            
    qa = PreflightValidator.audit_video(final_output)
    print("QA Status:", qa.get("status"))
    print(f"\n[COMPLETE] Video ready at: {final_output}")

if __name__ == "__main__":
    main()
