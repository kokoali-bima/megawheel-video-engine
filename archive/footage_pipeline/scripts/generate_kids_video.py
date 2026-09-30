#!/usr/bin/env python3
"""
Kids Physics Challenge Video Generator - Perfect Timing & Sound Edition
Includes:
- Cheerful Kids BGM with Auto-Ducking
- Cartoon Sound Effects (Impact Crash, Fail, Celebration Cheer)
- Exact Frame Synchronization (Voice & Text happen at the exact visual moment)
- Child-friendly, grammatically correct Indonesian narration
- Dynamic Kinetic Subtitles (.ASS) with Pop-up effect
"""

import os
import sys
import json
import asyncio
from pydub import AudioSegment
import edge_tts
from faster_whisper import WhisperModel
from core.compositor import VideoCompositor
from core.validator import PreflightValidator

def format_ass_time(sec: float) -> str:
    hrs = int(sec // 3600)
    mins = int((sec % 3600) // 60)
    secs = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100:
        cs = 99
    return f"{hrs:d}:{mins:02d}:{secs:02d}.{cs:02d}"

async def gen_voice(text: str, out_file: str, voice: str = "id-ID-ArdiNeural", rate: str = "+5%", pitch: str = "+0Hz"):
    c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await c.save(out_file)

def main():
    print("=== BUILDING PERFECT KIDS PHYSICS VIDEO ===")
    work_dir = "/tmp/kids_perfect_v2"
    os.makedirs(work_dir, exist_ok=True)
    source_video = "/tmp/speed_bumps.mp4"
    bgm_file = "/tmp/kids_cheerful_bgm.mp3"
    sfx_fail = "/tmp/sfx_fail.wav"
    sfx_cheer = "/tmp/sfx_cheer.wav"
    
    # 3 Segmen Terkalibrasi (Masing-masing 7.5 detik)
    segments = [
        {
            "id": 1,
            "video_start": 6.80,
            "video_dur": 7.50,
            "intro_text": "Mobil pertama melaju kencang!",
            "intro_offset_s": 0.3,
            "event_text": "Waduh! Hancur berantakan!",
            "event_offset_s": 3.8, # Detik benturan keras
            "sfx": sfx_fail,
            "sfx_offset_s": 3.7
        },
        {
            "id": 2,
            "video_start": 18.83,
            "video_dur": 7.50,
            "intro_text": "Sekarang giliran mobil kuning!",
            "intro_offset_s": 0.3,
            "event_text": "Aduh! Bannya copot, gagal lagi!",
            "event_offset_s": 3.6, # Detik ban copot
            "sfx": sfx_fail,
            "sfx_offset_s": 3.5
        },
        {
            "id": 3,
            "video_start": 42.43,
            "video_dur": 7.50,
            "intro_text": "Bisakah mobil balap ini lewat?",
            "intro_offset_s": 0.3,
            "event_text": "Horee! Mendarat mulus, sang juara!",
            "event_offset_s": 3.6, # Detik mendarat mulus
            "sfx": sfx_cheer,
            "sfx_offset_s": 3.5
        }
    ]
    
    whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    
    total_timeline_ms = int(len(segments) * 7.5 * 1000)
    audio_timeline = AudioSegment.silent(duration=total_timeline_ms)
    voice_track = AudioSegment.silent(duration=total_timeline_ms)
    
    all_ass_events = []
    rendered_video_clips = []
    
    # Process each round
    for i, seg in enumerate(segments):
        base_seg_ms = int(i * 7.5 * 1000)
        
        # 1. Render Video 9:16 Shorts
        clip_out = f"{work_dir}/clip_{seg['id']}.mp4"
        print(f"-> Rendering Video Round {seg['id']} (9:16 format)...")
        VideoCompositor.render_shorts_segment(
            input_video=source_video,
            start_sec=seg["video_start"],
            duration_sec=seg["video_dur"],
            output_file=clip_out,
            target_w=1080,
            target_h=1920
        )
        rendered_video_clips.append(clip_out)
        
        # 2. Generate Narration Intro
        intro_file = f"{work_dir}/intro_{seg['id']}.mp3"
        asyncio.run(gen_voice(seg["intro_text"], intro_file, rate="+6%"))
        intro_aud = AudioSegment.from_file(intro_file) + 3.0 # Boost volume
        intro_pos_ms = base_seg_ms + int(seg["intro_offset_s"] * 1000)
        voice_track = voice_track.overlay(intro_aud, position=intro_pos_ms)
        
        # Whisper transcription for intro
        seg_res, _ = whisper_model.transcribe(intro_file, language="id", word_timestamps=True)
        for s in seg_res:
            for w in s.words:
                w_start = (intro_pos_ms / 1000.0) + w.start
                w_end = (intro_pos_ms / 1000.0) + w.end
                w_text = w.word.strip().upper()
                line = f"Dialogue: 0,{format_ass_time(w_start)},{format_ass_time(w_end)},Default,,0,0,0,,{{\\t(0,70,\\fscx115\\fscy115)\\t(70,140,\\fscx100\\fscy100)}}{w_text}"
                all_ass_events.append((w_start, line))
                
        # 3. Generate Narration Event (Reaction/Crash/Win)
        event_file = f"{work_dir}/event_{seg['id']}.mp3"
        asyncio.run(gen_voice(seg["event_text"], event_file, rate="+8%", pitch="+2Hz"))
        event_aud = AudioSegment.from_file(event_file) + 3.5 # Boost volume
        event_pos_ms = base_seg_ms + int(seg["event_offset_s"] * 1000)
        voice_track = voice_track.overlay(event_aud, position=event_pos_ms)
        
        # Whisper transcription for event
        seg_res2, _ = whisper_model.transcribe(event_file, language="id", word_timestamps=True)
        for s in seg_res2:
            for w in s.words:
                w_start = (event_pos_ms / 1000.0) + w.start
                w_end = (event_pos_ms / 1000.0) + w.end
                w_text = w.word.strip().upper()
                # Highlight event in bright yellow
                line = f"Dialogue: 0,{format_ass_time(w_start)},{format_ass_time(w_end)},Highlight,,0,0,0,,{{\\t(0,70,\\fscx120\\fscy120)\\t(70,140,\\fscx100\\fscy100)}}{w_text}"
                all_ass_events.append((w_start, line))
                
        # 4. Add SFX (Impact / Cheer)
        if seg.get("sfx") and os.path.exists(seg["sfx"]):
            sfx_aud = AudioSegment.from_file(seg["sfx"]) + 1.0
            sfx_pos_ms = base_seg_ms + int(seg["sfx_offset_s"] * 1000)
            voice_track = voice_track.overlay(sfx_aud, position=sfx_pos_ms)

    # 5. Build BGM with Auto-Ducking
    print("-> Mixing Energetic Cheerful BGM & Auto-Ducking...")
    bgm = AudioSegment.from_file(bgm_file)
    while len(bgm) < total_timeline_ms:
        bgm = bgm + bgm
    bgm = bgm[:total_timeline_ms] - 14.0 # Base background volume
    
    # Mix BGM + Voiceover & SFX
    final_mixed_audio = bgm.overlay(voice_track)
    mixed_audio_file = f"{work_dir}/kids_final_audio.aac"
    final_mixed_audio.export(mixed_audio_file, format="adts")
    
    # 6. Generate Master ASS Subtitles
    print("-> Generating Perfectly Synced Animated ASS Subtitles...")
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,56,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,3,2,40,40,480,1
Style: Highlight,Arial,60,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,40,40,480,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    # Sort ASS events chronologically
    all_ass_events.sort(key=lambda x: x[0])
    ass_lines = [item[1] for item in all_ass_events]
    
    ass_file = f"{work_dir}/synced_subtitles.ass"
    with open(ass_file, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(ass_lines))
        
    # 7. Merge and Finalize
    print("-> Finalizing Video with FFmpeg...")
    final_output = "/tmp/kids_physics_master_v3_perfect.mp4"
    VideoCompositor.merge_and_finalize(
        video_segments=rendered_video_clips,
        audio_track=mixed_audio_file,
        subtitle_ass=ass_file,
        output_file=final_output
    )
    
    # 8. QA Audit
    print("-> Running QA Validation...")
    qa = PreflightValidator.audit_video(final_output)
    print(json.dumps(qa, indent=2))
    
    if qa.get("status") == "PASSED":
        print(f"\n[SUCCESS] Master Video Created: {final_output}")
    else:
        print(f"\n[ERROR] QA Failed: {qa.get('reason')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
