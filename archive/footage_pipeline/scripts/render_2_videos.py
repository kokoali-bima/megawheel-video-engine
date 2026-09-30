import os, subprocess, requests

os.makedirs("/tmp/batch_renders", exist_ok=True)

def tts(text, filename, voice="af_heart"):
    payload = {"model": "kokoro", "input": text, "voice": voice, "response_format": "mp3", "speed": 1.0}
    r = requests.post("http://localhost:8880/v1/audio/speech", json=payload)
    if r.status_code == 200:
        with open(filename, 'wb') as f: f.write(r.content)
        print(f"TTS generated: {filename}")
    else:
        print(f"TTS error: {r.status_code} {r.text}")

def render_challenge_video(video_title, scenes, out_mp4):
    work_dir = f"/tmp/{video_title}"
    os.makedirs(work_dir, exist_ok=True)
    
    audio_clips = []
    for i, sc in enumerate(scenes):
        f_intro = f"{work_dir}/v_{i}_intro.mp3"
        f_crash = f"{work_dir}/v_{i}_crash.mp3"
        tts(sc["intro"], f_intro, voice="af_heart")
        tts(sc["reaction"], f_crash, voice="af_heart")
        audio_clips.append((f_intro, f_crash))
        
    video_durations = [sc["dur"] for sc in scenes]
    total_len = sum(video_durations)
    scene_starts = [0]
    for d in video_durations[:-1]:
        scene_starts.append(scene_starts[-1] + d)
        
    t_ev1 = scene_starts[0] + scenes[0]["event_delay"]
    t_ev2 = scene_starts[1] + scenes[1]["event_delay"]
    t_ev3 = scene_starts[2] + scenes[2]["event_delay"]
    
    v_filter = ""
    a_filter = ""
    concat_v = ""
    concat_a = ""
    
    for i, (sc, dur) in enumerate(zip(scenes, video_durations)):
        v_filter += f"[1:v]trim=start={sc['start']}:duration={dur},setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[sc_v{i}];"
        a_filter += f"[1:a]atrim=start={sc['start']}:duration={dur},asetpts=PTS-STARTPTS[sc_a{i}];"
        concat_v += f"[sc_v{i}]"
        concat_a += f"[sc_a{i}]"
        
    v_filter += f"{concat_v}concat=n=3:v=1:a=0[raw_seq];"
    a_filter += f"{concat_a}concat=n=3:v=0:a=1[game_sfx_raw];[game_sfx_raw]volume=0.40[game_sfx];"
    
    is_win3 = scenes[2].get("is_win", False)
    sfx3_label = "sfx3_win" if is_win3 else "sfx3_fail"
    sfx3_input = "[10:a]" if is_win3 else "[8:a]"
    
    mix_filter = (
        f"[0:a]volume=0.20,atrim=duration={total_len:.2f},afade=t=out:st={total_len-1.5:.2f}:d=1.5[bgm];"
        f"[2:a]volume=2.0,adelay={int(scene_starts[0]*1000)}|{int(scene_starts[0]*1000)}[v1_i];"
        f"[3:a]volume=2.0,adelay={int(t_ev1*1000)}|{int(t_ev1*1000)}[v1_c];"
        f"[4:a]volume=2.0,adelay={int(scene_starts[1]*1000)}|{int(scene_starts[1]*1000)}[v2_i];"
        f"[5:a]volume=2.0,adelay={int(t_ev2*1000)}|{int(t_ev2*1000)}[v2_c];"
        f"[6:a]volume=2.0,adelay={int(scene_starts[2]*1000)}|{int(scene_starts[2]*1000)}[v3_i];"
        f"[7:a]volume=2.0,adelay={int(t_ev3*1000)}|{int(t_ev3*1000)}[v3_c];"
        f"[8:a]volume=1.8,adelay={int(t_ev1*1000)}|{int(t_ev1*1000)}[sfx1];"
        f"[9:a]volume=1.8,adelay={int(t_ev2*1000)}|{int(t_ev2*1000)}[sfx2];"
        f"{sfx3_input}volume=2.2,adelay={int(t_ev3*1000)}|{int(t_ev3*1000)}[{sfx3_label}];"
        f"[11:a]volume=1.6,adelay={int(t_ev3*1000)}|{int(t_ev3*1000)}[cheer];"
        f"[bgm][game_sfx][v1_i][v1_c][v2_i][v2_c][v3_i][v3_c][sfx1][sfx2][{sfx3_label}][cheer]amix=inputs=12:duration=first:dropout_transition=2,volume=5.0[aout];"
    )
    
    t_end1 = min(t_ev1 + 4.5, scene_starts[1])
    t_end2 = min(t_ev2 + 4.0, scene_starts[2])
    
    overlay_png3 = "[13:v]" if is_win3 else "[12:v]"
    
    overlay_filter = (
        "[raw_seq]split=2[in_bg][in_fg];"
        "[in_bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.22[bg];"
        "[in_fg]scale=1080:608,drawbox=x=0:y=0:w=iw:h=ih:color=yellow@0.7:t=5[fg];"
        "[bg][fg]overlay=x=0:y=656[base_video];"
        f"[base_video][12:v]overlay=x=0:y=1320:enable='between(t,{t_ev1:.2f},{t_end1:.2f}) + between(t,{t_ev2:.2f},{t_end2:.2f})'[with_fail];"
        f"[with_fail]{overlay_png3}overlay=x=0:y=1320:enable='between(t,{t_ev3:.2f},{total_len:.2f})',fade=t=out:st={total_len-1.0:.2f}:d=1.0[vfinal]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-i", "/tmp/kids_cheerful_bgm.mp3",
        "-i", "/root/local_videos/physics/beamng_test.mp4",
        "-i", audio_clips[0][0], "-i", audio_clips[0][1],
        "-i", audio_clips[1][0], "-i", audio_clips[1][1],
        "-i", audio_clips[2][0], "-i", audio_clips[2][1],
        "-i", "/tmp/sfx_fail.wav", "-i", "/tmp/sfx_fail.wav",
        "-i", "/tmp/sfx_win.wav", "-i", "/tmp/sfx_cheer.wav",
        "-i", "/tmp/kids_graphic_assets_fhd/fail_en_fhd.png",
        "-i", "/tmp/kids_graphic_assets_fhd/win_en_fhd.png",
        "-filter_complex", v_filter + a_filter + mix_filter + overlay_filter,
        "-map", "[vfinal]", "-map", "[aout]",
        "-t", f"{total_len:.2f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_mp4
    ]
    subprocess.run(cmd, check=True)
    print(f"SUCCESS: {out_mp4}")

# Video 1: Speed Bump Challenge (Black Sport Car -> Vintage Classic -> 6x6 Heavy Dually Truck)
scenes_video1 = [
    {
        "start": 0.8, "dur": 13.7, "event_delay": 3.6,
        "intro": "Look at this fast black sport car!",
        "reaction": "Boom! Wheel snapped off! Failed!",
        "is_win": False
    },
    {
        "start": 46.0, "dur": 12.0, "event_delay": 6.0,
        "intro": "Here comes the vintage classic car!",
        "reaction": "Whoops! Smashed and broken! Failed again!",
        "is_win": False
    },
    {
        "start": 221.8, "dur": 19.5, "event_delay": 1.6,
        "intro": "Giant six-wheel heavy truck is rolling in!",
        "reaction": "Yay! Champion! We made it to the end!",
        "is_win": True
    }
]

# Video 2: Deep Pothole & Bridge Pit Challenge (Red Speedster -> White Buggy -> Heavy Blue Bus)
scenes_video2 = [
    {
        "start": 71.58, "dur": 15.0, "event_delay": 9.5,
        "intro": "Watch out for the red sports car!",
        "reaction": "Ouch! Crashed into the pit! Total fail!",
        "is_win": False
    },
    {
        "start": 113.30, "dur": 14.0, "event_delay": 8.5,
        "intro": "White off-road buggy speeding up!",
        "reaction": "Oh no! Flipped over and wrecked!",
        "is_win": False
    },
    {
        "start": 135.22, "dur": 16.0, "event_delay": 10.0,
        "intro": "Look at this massive heavy blue bus!",
        "reaction": "Boom! Rolled over into the deep gap!",
        "is_win": False
    }
]

print("=== Rendering Video 1: Speed Bump Challenge ===")
render_challenge_video("speed_bump_challenge", scenes_video1, "/root/VIDEO_01_SPEED_BUMPS.mp4")

print("=== Rendering Video 2: Deep Pothole Challenge ===")
render_challenge_video("pothole_pit_challenge", scenes_video2, "/root/VIDEO_02_POTHOLES.mp4")
