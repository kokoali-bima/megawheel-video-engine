#!/usr/bin/env python3
"""
Production Video Pipeline Execution Script
Demonstrating the unified Video Engine:
- Frame-accurate segment cuts (SceneAnalyzer)
- Neural Voiceover + Auto-Ducking (AudioEngine)
- Kinetic ASS Subtitles (SubtitleEngine + Whisper)
- 9:16 Shorts Framing (VideoCompositor)
- Automated Pre-Flight QA (PreflightValidator)
"""

import os
import sys
import json
import subprocess
from core.audio_engine import AudioEngine
from core.subtitle_engine import SubtitleEngine
from core.compositor import VideoCompositor
from core.validator import PreflightValidator

def main():
    print("=== STARTING UNIFIED VIDEO ENGINE PIPELINE ===")
    source_video = "/tmp/speed_bumps.mp4"
    work_dir = "/tmp/engine_run_v1"
    os.makedirs(work_dir, exist_ok=True)
    
    # 1. Definisi 3 Ronde Cerita (Gagal -> Gagal -> Juara)
    segments_config = [
        {"start": 6.80, "dur": 7.5, "label": "seg1", "text": "Mobil pertama meluncur kencang... Dan langsung remuk berantakan!"},
        {"start": 18.83, "dur": 7.5, "label": "seg2", "text": "Ronde dua, sedan kuning mencoba... Bannya copot dan gagal total!"},
        {"start": 42.43, "dur": 6.5, "label": "seg3", "text": "Ronde terakhir sang penantang... Luar biasa, mendarat mulus dan jadi juara!"}
    ]
    
    rendered_segments = []
    voice_track_items = []
    all_words = []
    
    current_time_offset_ms = 500 # Start 0.5s in
    
    print("\n[Step 1/5] Generating Neural Voiceovers & Measuring Exact Audio Durations...")
    for i, seg in enumerate(segments_config):
        tts_file = f"{work_dir}/voice_{seg['label']}.mp3"
        AudioEngine.generate_speech(
            text=seg["text"],
            output_file=tts_file,
            voice_key="id_male",
            rate="+5%"
        )
        
        # Transcribe words for ASS subtitles
        words = SubtitleEngine.transcribe(tts_file, language="id")
        for w in words:
            all_words.append({
                "start": (current_time_offset_ms / 1000.0) + w["start"],
                "end": (current_time_offset_ms / 1000.0) + w["end"],
                "word": w["word"]
            })
            
        voice_track_items.append({
            "file": tts_file,
            "start_ms": current_time_offset_ms,
            "volume_db": 3.0
        })
        
        # Step video rendering
        seg_out = f"{work_dir}/rendered_{seg['label']}.mp4"
        print(f"  -> Rendering Video Clip {i+1}: {seg['start']}s for {seg['dur']}s...")
        VideoCompositor.render_shorts_segment(
            input_video=source_video,
            start_sec=seg["start"],
            duration_sec=seg["dur"],
            output_file=seg_out,
            target_w=1080,
            target_h=1920
        )
        rendered_segments.append(seg_out)
        
        current_time_offset_ms += int(seg["dur"] * 1000)

    total_duration_ms = current_time_offset_ms + 500
    print(f"\n[Step 2/5] Mixing Audio Tracks with Auto-Ducking (Total Duration: {total_duration_ms/1000:.2f}s)...")
    final_audio = f"{work_dir}/final_mixed_audio.aac"
    AudioEngine.mix_tracks_with_ducking(
        voice_clips=voice_track_items,
        output_path=final_audio,
        total_duration_ms=total_duration_ms
    )
    
    print("\n[Step 3/5] Generating Kinetic Animated Subtitles (.ASS)...")
    sub_file = f"{work_dir}/subtitles.ass"
    SubtitleEngine.generate_ass_subtitles(
        word_list=all_words,
        output_ass_path=sub_file,
        font_size=26,
        primary_color="&H00FFFFFF",
        highlight_color="&H0000FFFF",
        words_per_group=3
    )

    print("\n[Step 4/5] Merging Segments, Burning Subtitles & Finalizing MP4...")
    final_output = "/tmp/video_engine_masterpiece_v1.mp4"
    VideoCompositor.merge_and_finalize(
        video_segments=rendered_segments,
        audio_track=final_audio,
        subtitle_ass=sub_file,
        output_file=final_output
    )
    
    print("\n[Step 5/5] Running Pre-Flight QA Validator...")
    qa_report = PreflightValidator.audit_video(final_output)
    print("QA REPORT:")
    print(json.dumps(qa_report, indent=2))
    
    if qa_report.get("status") == "PASSED":
        print(f"\n[SUCCESS] Final Video Ready: {final_output}")
    else:
        print(f"\n[FAILED] QA check failed: {qa_report.get('reason')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
