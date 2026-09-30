#!/usr/bin/env python3
"""
Potholes Physics Challenge - Perfected Kids English Master Edition
- Full-Bleed 1080x1920 Blurred Background
- Golden Framed Center Video
- Top Pill Tag: [ LEVEL 1 : BLACK SPORT CAR ] -> [ LEVEL 2 : VINTAGE CLASSIC CAR ] -> [ LEVEL 3 : GIANT RED TRUCK ]
- Bottom Dynamic Pill Button: Perfectly synced to appear EXACTLY at the moment of impact/finish
- Simple, Friendly Kids English Voice (en-US-AnaNeural)
- Big Joyful "HOREEE! YAY! WE HAVE A CHAMPION!" Celebration with Applause & Cheering SFX
"""

import os
import sys
import json
import asyncio
import subprocess
from pydub import AudioSegment
import edge_tts

async def gen_voice(text: str, out_file: str, voice: str = "en-US-AnaNeural", rate: str = "+3%", pitch: str = "+1Hz"):
    c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await c.save(out_file)

def main():
    print("=== BUILDING PERFECTED POTHOLES KIDS ENGLISH MASTER ===")
    work_dir = "/tmp/potholes_kids_master"
    os.makedirs(work_dir, exist_ok=True)
    
    source_video = "/tmp/beamng_test.mp4"
    bgm_file = "/tmp/kids_cheerful_bgm.mp3"
    sfx_fail = "/tmp/sfx_fail.wav"
    sfx_cheer = "/tmp/sfx_cheer.wav"
    
    # 3 Level Segment Breakdown (Exact Settle-to-Stop Timestamps)
    # Level 1: 0:02:12 -> 13.7s
    # Level 2: 0:03:52 -> 11.0s
    # Level 3: 0:06:00 -> 21.2s
    # Total Duration: 45.90s
    
    tts_chunks = [
        # Level 1
        {"file": f"{work_dir}/l1_intro.mp3", "text": "Level one! Look at the black sport car speeding up!", "pos_ms": 500, "vol": 5.0},
        {"file": f"{work_dir}/l1_event.mp3", "text": "Oh no! The wheel snapped off! Failed!", "pos_ms": 6800, "vol": 6.0}, # Detik tepat roda patah
        # Level 2
        {"file": f"{work_dir}/l2_intro.mp3", "text": "Level two! Here comes the classic vintage car!", "pos_ms": 14200, "vol": 5.0},
        {"file": f"{work_dir}/l2_event.mp3", "text": "Whoa! The whole car body fell off! Failed again!", "pos_ms": 18200, "vol": 6.0}, # Detik bodi copot
        # Level 3
        {"file": f"{work_dir}/l3_intro.mp3", "text": "Final level! Look at the giant red truck! Go go go!", "pos_ms": 25200, "vol": 5.0},
        {"file": f"{work_dir}/l3_win.mp3", "text": "HOREEE! Yay! It made it smoothly! We have a champion!", "pos_ms": 34500, "vol": 7.0} # Detik sukses lolos
    ]
    
    print("\n[Step 1] Generating Soft & Energetic Kids Voiceover Chunks...")
    for t in tts_chunks:
        asyncio.run(gen_voice(t["text"], t["file"], voice="en-US-AnaNeural"))
        
    total_timeline_ms = 45900 # 45.9 seconds
    voice_track = AudioSegment.silent(duration=total_timeline_ms)
    sfx_track = AudioSegment.silent(duration=total_timeline_ms)
    
    for t in tts_chunks:
        aud = AudioSegment.from_file(t["file"]).normalize() + t.get("vol", 4.0)
        voice_track = voice_track.overlay(aud, position=t["pos_ms"])
        
    # Add SFX at exact impact / celebration moments
    # SFX Fail 1 (6.8s)
    sfx1 = AudioSegment.from_file(sfx_fail).normalize() + 1.0
    sfx_track = sfx_track.overlay(sfx1, position=6700)
    
    # SFX Fail 2 (18.2s)
    sfx2 = AudioSegment.from_file(sfx_fail).normalize() + 1.0
    sfx_track = sfx_track.overlay(sfx2, position=18100)
    
    # SFX Cheer & Fanfare (34.5s)
    sfx3 = AudioSegment.from_file(sfx_cheer).normalize() + 5.0
    sfx_track = sfx_track.overlay(sfx3, position=34400)
    
    print("\n[Step 2] Mixing Master Soundscape (Gentle Kids BGM + Dominant Voice + SFX)...")
    bgm = AudioSegment.from_file(bgm_file)
    while len(bgm) < total_timeline_ms:
        bgm = bgm + bgm
    bgm = bgm[:total_timeline_ms] - 20.0 # Soft background music
    
    master_audio = bgm.overlay(sfx_track).overlay(voice_track)
    master_wav = f"{work_dir}/master_sound.wav"
    master_audio.export(master_wav, format="wav")
    
    # Step 3: Build Full-Bleed Filter Complex with Exact Pill Button Timings
    # Level 1 FAIL Pill: enable='between(t,6.8,13.7)'  (Bukan di 4s!)
    # Level 2 FAIL Pill: enable='between(t,18.2,24.7)'
    # Level 3 WINNER Pill: enable='between(t,34.5,45.9)'
    
    print("\n[Step 3] Rendering Full-Bleed 1080x1920 Video with Synced Pill Buttons...")
    
    # We cut 3 segments from beamng_test.mp4:
    # Seg 1: -ss 00:02:12 -t 13.7
    # Seg 2: -ss 00:03:52 -t 11.0
    # Seg 3: -ss 00:06:00 -t 21.2
    
    filter_script = f"""
    [0:v]trim=start=132.0:duration=13.7,setpts=PTS-STARTPTS[v1_raw];
    [0:v]trim=start=232.0:duration=11.0,setpts=PTS-STARTPTS[v2_raw];
    [0:v]trim=start=360.0:duration=21.2,setpts=PTS-STARTPTS[v3_raw];
    [v1_raw][v2_raw][v3_raw]concat=n=3:v=1:a=0[v_base];
    
    [v_base]split=2[fg_in][bg_in];
    
    [bg_in]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[bg_blur];
    
    [fg_in]scale=1080:608,drawbox=x=0:y=0:w=1080:h=608:color=yellow@1.0:t=6[fg_sharp];
    
    [bg_blur][fg_sharp]overlay=x=0:y=656[v_comp];
    
    [v_comp]
    drawbox=x=(w-680)/2:y=240:w=680:h=64:color=black@0.9:t=fill:enable='between(t,0,13.7)',
    drawtext=text='[ LEVEL 1 : BLACK SPORT CAR ]':font='Arial':fontsize=36:fontcolor=yellow:x=(w-text_w)/2:y=255:enable='between(t,0,13.7)',
    
    drawbox=x=(w-740)/2:y=240:w=740:h=64:color=black@0.9:t=fill:enable='between(t,13.7,24.7)',
    drawtext=text='[ LEVEL 2 : VINTAGE CLASSIC CAR ]':font='Arial':fontsize=36:fontcolor=yellow:x=(w-text_w)/2:y=255:enable='between(t,13.7,24.7)',
    
    drawbox=x=(w-680)/2:y=240:w=680:h=64:color=black@0.9:t=fill:enable='between(t,24.7,45.9)',
    drawtext=text='[ LEVEL 3 : GIANT RED TRUCK ]':font='Arial':fontsize=36:fontcolor=yellow:x=(w-text_w)/2:y=255:enable='between(t,24.7,45.9)',
    
    drawbox=x=(w-560)/2:y=1340:w=560:h=110:color=0xCC0033@1.0:t=fill:enable='between(t,6.8,13.7)',
    drawbox=x=(w-560)/2:y=1340:w=560:h=110:color=white@1.0:t=6:enable='between(t,6.8,13.7)',
    drawtext=text='FAIL / GAGAL!':font='Arial Black':fontsize=52:fontcolor=white:x=(w-text_w)/2:y=1370:enable='between(t,6.8,13.7)',
    
    drawbox=x=(w-560)/2:y=1340:w=560:h=110:color=0xCC0033@1.0:t=fill:enable='between(t,18.2,24.7)',
    drawbox=x=(w-560)/2:y=1340:w=560:h=110:color=white@1.0:t=6:enable='between(t,18.2,24.7)',
    drawtext=text='FAIL / GAGAL!':font='Arial Black':fontsize=52:fontcolor=white:x=(w-text_w)/2:y=1370:enable='between(t,18.2,24.7)',
    
    drawbox=x=(w-620)/2:y=1340:w=620:h=110:color=0x009944@1.0:t=fill:enable='between(t,34.5,45.9)',
    drawbox=x=(w-620)/2:y=1340:w=620:h=110:color=white@1.0:t=6:enable='between(t,34.5,45.9)',
    drawtext=text='BERHASIL / WINNER!':font='Arial Black':fontsize=50:fontcolor=white:x=(w-text_w)/2:y=1370:enable='between(t,34.5,45.9)'
    [v_out]
    """
    
    final_output = "/tmp/POTHOLES_PERFECTED_KIDS_ENGLISH_MASTER.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-i", source_video,
        "-i", master_wav,
        "-filter_complex", filter_script,
        "-map", "[v_out]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-ac", "2",
        "-t", "45.9",
        "-movflags", "+faststart",
        final_output
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg Error:\n", res.stderr)
        sys.exit(1)
        
    print(f"\n[SUCCESS] Master Video Created: {final_output}")

if __name__ == "__main__":
    main()
