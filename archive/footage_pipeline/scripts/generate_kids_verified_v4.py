#!/usr/bin/env python3
"""
Kids Physics Challenge Video Generator - Vision-Verified & Loud Audio Edition
- Car 1: Sedan Merah Corak (Crash on bumps)
- Car 2: SUV Hitam Gagah (Fling into canyon)
- Car 3: Mobil Klasik Putih (Smooth jump & Champion)
- Audio: High-fidelity uncompressed WAV master, Boosted Voice + Cheerful BGM + Cartoon SFX + Original Engine Sound
- Subtitles: Word-by-word Kinetic ASS popup with exact visual sync
"""

import os
import sys
import json
import asyncio
import subprocess
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

async def gen_voice(text: str, out_file: str, voice: str = "id-ID-ArdiNeural", rate: str = "+5%", pitch: str = "+1Hz"):
    c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await c.save(out_file)

def main():
    print("=== BUILDING VISION-VERIFIED KIDS PHYSICS VIDEO ===")
    work_dir = "/tmp/kids_verified_v4"
    os.makedirs(work_dir, exist_ok=True)
    source_video = "/tmp/speed_bumps.mp4"
    bgm_file = "/tmp/kids_cheerful_bgm.mp3"
    sfx_fail = "/tmp/sfx_fail.wav"
    sfx_cheer = "/tmp/sfx_cheer.wav"
    
    # 3 Segmen Terverifikasi Visual (Durasi 7.0 detik per ronde)
    segments = [
        {
            "id": 1,
            "video_start": 6.80,
            "video_dur": 7.0,
            "intro_text": "Ayo lihat sedan merah ini!",
            "intro_offset_s": 0.2,
            "event_text": "WADUH! Hancur berantakan!",
            "event_offset_s": 3.4, # Detik tepat benturan gundukan
            "sfx": sfx_fail,
            "sfx_offset_s": 3.3
        },
        {
            "id": 2,
            "video_start": 48.30, # Mobil SUV Hitam
            "video_dur": 7.0,
            "intro_text": "Sekarang giliran SUV hitam!",
            "intro_offset_s": 0.2,
            "event_text": "ADUH! Terlempar ke jurang!",
            "event_offset_s": 3.3, # Detik tepat terjun ke jurang
            "sfx": sfx_fail,
            "sfx_offset_s": 3.2
        },
        {
            "id": 3,
            "video_start": 177.50, # Mobil Klasik Putih Juara
            "video_dur": 7.0,
            "intro_text": "Bisakah mobil klasik ini lolos?",
            "intro_offset_s": 0.2,
            "event_text": "HOREEE! Mendarat mulus, sang juara!",
            "event_offset_s": 3.3, # Detik tepat mendarat & melaju mulus
            "sfx": sfx_cheer,
            "sfx_offset_s": 3.2
        }
    ]
    
    whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
    
    total_timeline_ms = int(len(segments) * 7.0 * 1000)
    voice_track = AudioSegment.silent(duration=total_timeline_ms)
    
    all_ass_events = []
    rendered_video_clips = []
    
    # Extract original video audio tracks for natural engine sounds
    engine_track = AudioSegment.silent(duration=total_timeline_ms)
    
    print("\n[1/5] Processing video clips & generating synchronized voiceover...")
    for i, seg in enumerate(segments):
        base_seg_ms = int(i * 7.0 * 1000)
        
        # 1. Render Video 9:16 Shorts
        clip_out = f"{work_dir}/clip_{seg['id']}.mp4"
        print(f"  -> Rendering Round {seg['id']} (start: {seg['video_start']}s, dur: {seg['video_dur']}s)...")
        VideoCompositor.render_shorts_segment(
            input_video=source_video,
            start_sec=seg["video_start"],
            duration_sec=seg["video_dur"],
            output_file=clip_out,
            target_w=1080,
            target_h=1920
        )
        rendered_video_clips.append(clip_out)
        
        # Extract audio from clip for real engine sound
        clip_wav = f"{work_dir}/engine_{seg['id']}.wav"
        subprocess.run(["ffmpeg", "-y", "-i", clip_out, "-vn", "-c:a", "pcm_s16le", clip_wav], capture_output=True)
        if os.path.exists(clip_wav):
            clip_aud = AudioSegment.from_file(clip_wav)
            engine_track = engine_track.overlay(clip_aud[:int(seg['video_dur']*1000)] - 4.0, position=base_seg_ms)
            
        # 2. Voiceover Intro
        intro_file = f"{work_dir}/intro_{seg['id']}.mp3"
        asyncio.run(gen_voice(seg["intro_text"], intro_file, rate="+6%"))
        intro_aud = AudioSegment.from_file(intro_file) + 6.0 # Loud & clear voice
        intro_pos_ms = base_seg_ms + int(seg["intro_offset_s"] * 1000)
        voice_track = voice_track.overlay(intro_aud, position=intro_pos_ms)
        
        # Whisper transcription
        seg_res, _ = whisper_model.transcribe(intro_file, language="id", word_timestamps=True)
        for s in seg_res:
            for w in s.words:
                w_start = (intro_pos_ms / 1000.0) + w.start
                w_end = (intro_pos_ms / 1000.0) + w.end
                w_text = w.word.strip().upper()
                line = f"Dialogue: 0,{format_ass_time(w_start)},{format_ass_time(w_end)},Default,,0,0,0,,{{\\t(0,60,\\fscx115\\fscy115)\\t(60,120,\\fscx100\\fscy100)}}{w_text}"
                all_ass_events.append((w_start, line))
                
        # 3. Voiceover Event
        event_file = f"{work_dir}/event_{seg['id']}.mp3"
        asyncio.run(gen_voice(seg["event_text"], event_file, rate="+8%", pitch="+2Hz"))
        event_aud = AudioSegment.from_file(event_file) + 6.5 # Boosted reaction
        event_pos_ms = base_seg_ms + int(seg["event_offset_s"] * 1000)
        voice_track = voice_track.overlay(event_aud, position=event_pos_ms)
        
        seg_res2, _ = whisper_model.transcribe(event_file, language="id", word_timestamps=True)
        for s in seg_res2:
            for w in s.words:
                w_start = (event_pos_ms / 1000.0) + w.start
                w_end = (event_pos_ms / 1000.0) + w.end
                w_text = w.word.strip().upper()
                line = f"Dialogue: 0,{format_ass_time(w_start)},{format_ass_time(w_end)},Highlight,,0,0,0,,{{\\t(0,60,\\fscx120\\fscy120)\\t(60,120,\\fscx100\\fscy100)}}{w_text}"
                all_ass_events.append((w_start, line))
                
        # 4. SFX
        if seg.get("sfx") and os.path.exists(seg["sfx"]):
            sfx_aud = AudioSegment.from_file(seg["sfx"]) + 4.0
            sfx_pos_ms = base_seg_ms + int(seg["sfx_offset_s"] * 1000)
            voice_track = voice_track.overlay(sfx_aud, position=sfx_pos_ms)

    # 5. Mix BGM + Engine + Voice Track into full-amplitude Master WAV
    print("\n[2/5] Mixing full soundscape (BGM + Engine + Boosted Voice + SFX)...")
    bgm = AudioSegment.from_file(bgm_file)
    while len(bgm) < total_timeline_ms:
        bgm = bgm + bgm
    bgm = bgm[:total_timeline_ms] - 8.0 # Clear BGM presence
    
    master_audio = bgm.overlay(engine_track).overlay(voice_track)
    master_audio_wav = f"{work_dir}/master_audio.wav"
    master_audio.export(master_audio_wav, format="wav")
    
    # 6. Generate Master ASS Subtitles
    print("\n[3/5] Generating kinetic ASS subtitles...")
    ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,58,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,3,2,40,40,480,1
Style: Highlight,Arial,62,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,2,40,40,480,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    all_ass_events.sort(key=lambda x: x[0])
    ass_lines = [item[1] for item in all_ass_events]
    ass_file = f"{work_dir}/subtitles.ass"
    with open(ass_file, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(ass_lines))
        
    # 7. Merge Video, Burn Subtitles, and Encode High-Quality Audio
    print("\n[4/5] Merging and encoding MP4 with loud AAC stereo audio...")
    concat_txt = f"{work_dir}/concat.txt"
    with open(concat_txt, "w") as f:
        for c in rendered_video_clips:
            f.write(f"file '{os.path.abspath(c)}'\n")
            
    final_output = "/tmp/kids_physics_v4_perfect_verified.mp4"
    escaped_ass = ass_file.replace(":", "\\:").replace("'", "\\'")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-i", master_audio_wav,
        "-vf", f"ass={escaped_ass}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-ac", "2",
        "-shortest",
        "-movflags", "+faststart",
        final_output
    ]
    
    subprocess.run(cmd, check=True)
    
    # 8. QA Audit
    print("\n[5/5] Auditing final output...")
    qa = PreflightValidator.audit_video(final_output)
    print(json.dumps(qa, indent=2))
    
    # Verify volume levels
    res = subprocess.run(["ffmpeg", "-i", final_output, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    for line in res.stderr.split("\n"):
        if "max_volume" in line or "mean_volume" in line:
            print("Audio Volume:", line.strip())

    if qa.get("status") == "PASSED":
        print(f"\n[SUCCESS] Final Video Ready: {final_output}")
    else:
        print(f"\n[ERROR] QA Failed: {qa.get('reason')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
