import os, subprocess, requests

OUTPUT_DIR = "/tmp/v6_sync"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Correctly identified scenes and synced audio cues
scenes = [
    {
        "video_start": 176.65, "video_dur": 15.0, "sfx_delay": 14.35,
        "voice_intro": "Look at this blue rally car!",
        "voice_crash": "Boom! That is a total fail!"
    },
    {
        "video_start": 203.45, "video_dur": 14.0, "sfx_delay": 8.83,
        "voice_intro": "Here comes the blue sedan!",
        "voice_crash": "Oh no, crashed and stopped!"
    },
    {
        "video_start": 221.38, "video_dur": 18.0, "sfx_delay": 1.62,
        "voice_intro": "The monster truck is here!",
        "voice_crash": "Champion! We made it!"
    }
]

def tts(text, filename):
    if os.path.exists(filename): return
    payload = {"model": "kokoro", "input": text, "voice": "af_bella", "response_format": "mp3", "speed": 1.0}
    r = requests.post("http://localhost:8880/v1/audio/speech", json=payload)
    if r.status_code == 200:
        with open(filename, 'wb') as f: f.write(r.content)

audio_clips = []
for i, sc in enumerate(scenes):
    f_intro = f"{OUTPUT_DIR}/v_{i}_intro.mp3"
    f_crash = f"{OUTPUT_DIR}/v_{i}_crash.mp3"
    tts(sc["voice_intro"], f_intro)
    tts(sc["voice_crash"], f_crash)
    audio_clips.append((f_intro, f_crash))

video_durations = [sc["video_dur"] for sc in scenes]
total_len = sum(video_durations)

scene_starts = [0, video_durations[0], video_durations[0] + video_durations[1]]

t_fail1 = scene_starts[0] + scenes[0]["sfx_delay"]
t_fail2 = scene_starts[1] + scenes[1]["sfx_delay"]
t_win3  = scene_starts[2] + scenes[2]["sfx_delay"]

audio_mixed = f"{OUTPUT_DIR}/audio_mixed.mp3"
# Mix background music, game sfx, voice intros, voice crashes, and sfx
complex_audio = (
    f"[0:a]volume=0.20,atrim=duration={total_len:.2f},afade=t=out:st={total_len-1.5:.2f}:d=1.5[bgm];"
    f"[1:a]volume=0.35,atrim=duration={total_len:.2f}[game_sfx];"
    f"[2:a]volume=1.8,adelay={int(scene_starts[0]*1000)}|{int(scene_starts[0]*1000)}[v1_i];"
    f"[3:a]volume=1.8,adelay={int(t_fail1*1000)}|{int(t_fail1*1000)}[v1_c];"
    f"[4:a]volume=1.8,adelay={int(scene_starts[1]*1000)}|{int(scene_starts[1]*1000)}[v2_i];"
    f"[5:a]volume=1.8,adelay={int(t_fail2*1000)}|{int(t_fail2*1000)}[v2_c];"
    f"[6:a]volume=1.8,adelay={int(scene_starts[2]*1000)}|{int(scene_starts[2]*1000)}[v3_i];"
    f"[7:a]volume=1.8,adelay={int(t_win3*1000)}|{int(t_win3*1000)}[v3_c];"
    f"[8:a]volume=1.8,adelay={int(t_fail1*1000)}|{int(t_fail1*1000)}[sfx1];"
    f"[9:a]volume=1.8,adelay={int(t_fail2*1000)}|{int(t_fail2*1000)}[sfx2];"
    f"[10:a]volume=2.2,adelay={int(t_win3*1000)}|{int(t_win3*1000)}[sfx3_win];"
    f"[11:a]volume=1.6,adelay={int(t_win3*1000)}|{int(t_win3*1000)}[sfx3_cheer];"
    "[bgm][game_sfx][v1_i][v1_c][v2_i][v2_c][v3_i][v3_c][sfx1][sfx2][sfx3_win][sfx3_cheer]amix=inputs=12:duration=first:dropout_transition=2,volume=5.0[aout]"
)

subprocess.run([
    "ffmpeg", "-y", 
    "-i", "/tmp/kids_cheerful_bgm.mp3", 
    "-i", "/root/.gemini/antigravity-cli/scratch/raw_materials/Physics_Gaming/2026-09-25/beamng_test.mp4", 
    "-i", audio_clips[0][0], "-i", audio_clips[0][1],
    "-i", audio_clips[1][0], "-i", audio_clips[1][1],
    "-i", audio_clips[2][0], "-i", audio_clips[2][1],
    "-i", "/tmp/sfx_fail.wav", "-i", "/tmp/sfx_fail.wav", 
    "-i", "/tmp/sfx_win.wav", "-i", "/tmp/sfx_cheer.wav", 
    "-filter_complex", complex_audio, "-map", "[aout]", "-c:a", "libmp3lame", "-b:a", "192k", audio_mixed
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Video assembly 
t_end1 = min(t_fail1 + 5.0, scene_starts[1])
t_end2 = min(t_fail2 + 4.0, scene_starts[2])

filter_parts = []
concat_inputs = ""
for idx, (sc, dur) in enumerate(zip(scenes, video_durations)):
    filter_parts.append(f"[0:v]trim=start={sc['video_start']:.2f}:duration={dur:.2f},setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[sc{idx}];")
    concat_inputs += f"[sc{idx}]"

filter_parts.append(f"{concat_inputs}concat=n=3:v=1:a=0[raw_seq];"
    "[raw_seq]split=2[in_bg][in_fg];"
    "[in_bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.22[bg];"
    "[in_fg]scale=1080:608,drawbox=x=0:y=0:w=iw:h=ih:color=yellow@0.7:t=5[fg];"
    "[bg][fg]overlay=x=0:y=656[base_video];"
    f"[base_video][2:v]overlay=x=0:y=1320:enable='between(t,{t_fail1:.2f},{t_end1:.2f}) + between(t,{t_fail2:.2f},{t_end2:.2f})'[with_fail];"
    f"[with_fail][3:v]overlay=x=0:y=1320:enable='between(t,{t_win3:.2f},{total_len:.2f})',fade=t=out:st={total_len-1.0:.2f}:d=1.0[vfinal]")

out_mp4 = "/root/V6_SYNCED_RENDER.mp4"
subprocess.run([
    "ffmpeg", "-y", 
    "-i", "/root/.gemini/antigravity-cli/scratch/raw_materials/Physics_Gaming/2026-09-25/beamng_test.mp4", 
    "-i", audio_mixed, 
    "-i", "/tmp/kids_graphic_assets_fhd/fail_en_fhd.png", 
    "-i", "/tmp/kids_graphic_assets_fhd/win_en_fhd.png", 
    "-filter_complex", "".join(filter_parts), 
    "-map", "[vfinal]", "-map", "1:a", 
    "-t", f"{total_len:.2f}", 
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", 
    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_mp4
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"SUCCESS: {out_mp4}")
