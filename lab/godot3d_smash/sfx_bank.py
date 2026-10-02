"""LAB — build the SFX bank for the 3D smash from Sonniss GDC 2024 (royalty-free, commercial use OK, no AI training).
Each source -> 44.1 kHz stereo wav, leading silence trimmed, capped length, fade-out, peak -1 dBFS.
  python3 lab/godot3d_smash/sfx_bank.py   ->  /root/lab/sfx/bank/<key>_<n>.wav + bank.json"""
import json
import os
import subprocess

SRC = "/root/lab/sfx/sonniss/GDC2024"
OUT = "/root/lab/sfx/bank"
# key -> [(pack, file, max_seconds)]
BANK = {
    "crash_light": [("BluezoneCorp - Stone Impact", "Bluezone_BC0297_stone_impact_hammer_015.wav", 0.7),
                    ("BluezoneCorp - Steampunk Machines", "Bluezone_BC0305_steampunk_machine_mechanical_texture_heavy_impact_011.wav", 0.7),
                    ("Doex Studio - Qantum UI", "UI_Noisy_Impact_09.wav", 0.8)],
    "crash_heavy": [("BluezoneCorp - Stone Impact", "Bluezone_BC0297_stone_impact_steel_bar_01_010.wav", 0.8),
                    ("BluezoneCorp - Stone Impact", "Bluezone_BC0297_stone_impact_015.wav", 1.6),
                    ("Doex Studio - 90s Anime SFX Pack", "Noise_Punch_006.wav", 1.4),
                    ("Bolt - ARP 2600- Droids, Blips, Drones & more", "MECHMisc_TRS Cable Plug In Solid Metal Thump_BOLT_ARP2600.wav", 1.2)],
    "debris": [("DavidDumais - Explosion SFX Pack", "WOODCrsh_Designed Wood Crash And Debris 13_DDUMAIS_NONE.wav", 1.7),
               ("BluezoneCorp - Alien Tripod", "Bluezone_BC0292_alien_tripod_debris_glass_falling_003.wav", 1.5)],
    "car_destroy": [("DavidDumais - Explosion SFX Pack",
                     "DESTRCrsh_Designed Car Explosion With Metal Breaking And Glass Shattering  06_DDUMAIS_NONE.wav", 4.5)],
    "explode": [("DavidDumais - Explosion SFX Pack", "EXPLReal_Medium Realistic Explosion 15_DDUMAIS_NONE.wav", 2.4),
                ("BluezoneCorp - Steampunk Weapon And Textures", "Bluezone_BC0296_steampunk_weapon_flare_shot_explosion_003.wav", 2.3)],
    "boom_big": [("BluezoneCorp - Modern Cinematic Impact", "Bluezone_BC0294_modern_cinematic_impact_boom_003.wav", 4.0)],
    "whoosh": [("Chupapsound - Essential Scifi", "WHOOSH PASS SF LOW.wav", 2.5)],
    "roar": [("Chupapsound - Essential Scifi", "GRWL ROAR ANGRY.wav", 3.0)],
    "stomp": [("BluezoneCorp - Stone Impact", "Bluezone_BC0297_stone_impact_041.wav", 2.0),
              ("BluezoneCorp - Alien Tripod", "Bluezone_BC0292_alien_tripod_debris_rock_collapse_earthquake_rumble_large_005.wav", 3.0)],
    "splash": [("BluezoneCorp - Designed Water", "Bluezone_BC0298_designed_water_impact_006.wav", 2.5),
               ("BluezoneCorp - Designed Water", "Bluezone_BC0298_designed_water_transition_impact_017.wav", 2.5)],
    "underwater": [("BluezoneCorp - Designed Water", "Bluezone_BC0298_designed_water_underwater_005.wav", 2.5)],
    "engine_loop": [("DavidDumais - ATV Arctic Cat 650 H1", "VEHAtv-Mono_Medium Steady Rpm Loop 01_DDUMAIS_ATV ARCTIC CAT 650 H1.wav", 22.0)],
}


def main():
    os.makedirs(OUT, exist_ok=True)
    index = {}
    for key, items in BANK.items():
        index[key] = []
        for n, (pack, name, mx) in enumerate(items):
            src = os.path.join(SRC, pack, name)
            dst = os.path.join(OUT, f"{key}_{n}.wav")
            fade = min(0.4, mx * 0.25)
            af = (f"silenceremove=start_periods=1:start_threshold=-45dB,atrim=0:{mx},"
                  f"afade=t=out:st={mx - fade:.2f}:d={fade:.2f}")
            if key == "engine_loop":
                af = f"atrim=0:{mx}"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-af", af, "-ac", "2", "-ar", "44100",
                            "-c:a", "pcm_s16le", dst + ".tmp.wav"], check=True)
            peak = subprocess.run(["ffmpeg", "-i", dst + ".tmp.wav", "-af", "volumedetect", "-f", "null", "-"],
                                  capture_output=True, text=True).stderr
            mx_db = float(peak.split("max_volume:")[1].split("dB")[0])
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", dst + ".tmp.wav", "-af", f"volume={-1.0 - mx_db:.2f}dB",
                            "-c:a", "pcm_s16le", dst], check=True)
            os.remove(dst + ".tmp.wav")
            index[key].append({"file": dst, "source": f"Sonniss GDC2024 / {pack} / {name}"})
    json.dump(index, open(os.path.join(OUT, "bank.json"), "w"), indent=1)
    print("[sfx-bank]", {k: len(v) for k, v in index.items()})


if __name__ == "__main__":
    main()
