import os, subprocess

OUTPUT_DIR = "/tmp/v7_perfect"
os.makedirs(OUTPUT_DIR, exist_ok=True)

video_durations = [19.0, 15.0, 18.0]
total_len = sum(video_durations)
scene_starts = [0, video_durations[0], video_durations[0] + video_durations[1]]

t_fail1 = scene_starts[0] + 14.35
t_fail2 = scene_starts[1] + 8.83
t_win3  = scene_starts[2] + 1.62

v_filter = ""
a_filter = ""
concat_v = ""
concat_a = ""

for i, (v_start, v_dur) in enumerate(zip([176.65, 203.45, 221.38], video_durations)):
    v_filter += f"[1:v]trim=start={v_start}:duration={v_dur},setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[sc_v{i}];"
    a_filter += f"[1:a]atrim=start={v_start}:duration={v_dur},asetpts=PTS-STARTPTS[sc_a{i}];"
    concat_v += f"[sc_v{i}]"
    concat_a += f"[sc_a{i}]"

v_filter += f"{concat_v}concat=n=3:v=1:a=0[raw_seq];"
a_filter += f"{concat_a}concat=n=3:v=0:a=1[game_sfx_raw];[game_sfx_raw]volume=0.35[game_sfx];"

mix_filter = (
    f"[0:a]volume=0.20,atrim=duration={total_len:.2f},afade=t=out:st={total_len-1.5:.2f}:d=1.5[bgm];"
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
    "[bgm][game_sfx][v1_i][v1_c][v2_i][v2_c][v3_i][v3_c][sfx1][sfx2][sfx3_win][sfx3_cheer]amix=inputs=12:duration=first:dropout_transition=2,volume=5.0[aout];"
)

t_end1 = min(t_fail1 + 5.0, scene_starts[1])
t_end2 = min(t_fail2 + 4.0, scene_starts[2])

overlay_filter = (
    "[raw_seq]split=2[in_bg][in_fg];"
    "[in_bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.22[bg];"
    "[in_fg]scale=1080:608,drawbox=x=0:y=0:w=iw:h=ih:color=yellow@0.7:t=5[fg];"
    "[bg][fg]overlay=x=0:y=656[base_video];"
    f"[base_video][12:v]overlay=x=0:y=1320:enable='between(t,{t_fail1:.2f},{t_end1:.2f}) + between(t,{t_fail2:.2f},{t_end2:.2f})'[with_fail];"
    f"[with_fail][13:v]overlay=x=0:y=1320:enable='between(t,{t_win3:.2f},{total_len:.2f})',fade=t=out:st={total_len-1.0:.2f}:d=1.0[vfinal]"
)

out_mp4 = "/root/V7_ULTIMATE_RENDER.mp4"
subprocess.run([
    "ffmpeg", "-y", 
    "-i", "/tmp/kids_cheerful_bgm.mp3", 
    "-i", "/root/.gemini/antigravity-cli/scratch/raw_materials/Physics_Gaming/2026-09-25/beamng_test.mp4", 
    "-i", "/tmp/v6_sync/v_0_intro.mp3", "-i", "/tmp/v6_sync/v_0_crash.mp3",
    "-i", "/tmp/v6_sync/v_1_intro.mp3", "-i", "/tmp/v6_sync/v_1_crash.mp3",
    "-i", "/tmp/v6_sync/v_2_intro.mp3", "-i", "/tmp/v6_sync/v_2_crash.mp3",
    "-i", "/tmp/sfx_fail.wav", "-i", "/tmp/sfx_fail.wav", 
    "-i", "/tmp/sfx_win.wav", "-i", "/tmp/sfx_cheer.wav", 
    "-i", "/tmp/kids_graphic_assets_fhd/fail_en_fhd.png", 
    "-i", "/tmp/kids_graphic_assets_fhd/win_en_fhd.png", 
    "-filter_complex", v_filter + a_filter + mix_filter + overlay_filter, 
    "-map", "[vfinal]", "-map", "[aout]", 
    "-t", f"{total_len:.2f}", 
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", 
    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out_mp4
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"SUCCESS: {out_mp4}")
