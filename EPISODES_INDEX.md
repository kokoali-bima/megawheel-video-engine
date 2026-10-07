# EPISODES_INDEX — identitas pasti setiap episode MegaWheel Arena

> Dibuat otomatis oleh `generators/publishing/episodes.py` (2026-10-07 05:00) setiap approve/reject/upload. **Jangan diedit manual.** Sumber data: `PRODUCTION_REGISTRY.json`.

## Cara mengenali episode (wajib untuk semua agent)

1. **Nomor episode = kunci utama.** "Ep. 1" selalu berarti VIDEO_ID di kartu Ep. 1 di bawah, bukan urutan render, tanggal di nama folder, atau nomor seed.
2. Nomor seed ≠ nomor episode. Contoh: `SIM_LAVA_V2_S003` adalah **Ep. 8**, bukan Ep. 3.
3. Hanya folder `renders/megawheel_arena/S01/E0NN_*` yang berisi episode. Folder `pending/` = belum di-approve, `rejected/` = ditolak. Keduanya **bukan** episode dan tidak boleh diupload.
4. Sebelum upload atau menjawab pertanyaan tentang "Ep. N", cocokkan tiga hal: VIDEO_ID, path MP4, judul.
5. Ragu? Jalankan `./venv/bin/python generators/publishing/episodes.py list` di `/root/video-engine`.

## Ringkasan

| Ep | VIDEO_ID | Seri | Status | Jadwal tayang (ET) | URL |
|---|---|---|---|---|---|
| 1 | `SIM_POTHOLES_V2_S001` | potholes | UPLOADED_SCHEDULED 2026-10-02T15:00:00Z | Fri 2026-10-02 11:00 | https://www.youtube.com/shorts/PwlO0ptmi-c |
| 2 | `SIM_BUMPS_V2_S002` | bumps | UPLOADED_SCHEDULED 2026-09-30T19:00:00Z | Wed 2026-09-30 15:00 | https://www.youtube.com/shorts/dVBtbf8Bi_Q |
| 3 | `SIM_POTHOLES_V2_S003` | potholes | UPLOADED_SCHEDULED 2026-09-30T23:00:00Z | Wed 2026-09-30 19:00 | https://www.youtube.com/shorts/yf0y4R83hto |
| 4 | `SIM_BUMPS_V2_S004` | bumps | UPLOADED_SCHEDULED 2026-10-01T15:00:00Z | Thu 2026-10-01 11:00 | https://www.youtube.com/shorts/3CfgGpkOx3Q |
| 5 | `SIM_POTHOLES_V2_S005` | potholes | UPLOADED_SCHEDULED 2026-10-01T19:00:00Z | Thu 2026-10-01 15:00 | https://www.youtube.com/shorts/xEWas3W61QU |
| 6 | `SIM_BUMPS_V2_S006` | bumps | UPLOADED_SCHEDULED 2026-10-01T23:00:00Z | Thu 2026-10-01 19:00 | https://www.youtube.com/shorts/nXlV3f6Wux8 |
| 7 | `SIM_SPLASH_V2_S007` | splash | UPLOADED_SCHEDULED 2026-10-03T15:00:00Z | Sat 2026-10-03 11:00 | https://www.youtube.com/shorts/0FEC9QmNYw0 |
| 8 | `SIM_LAVA_V2_S003` | lava | UPLOADED_SCHEDULED 2026-10-04T15:00:00Z | Sun 2026-10-04 11:00 | https://www.youtube.com/shorts/LIP2P98Be6M |
| 9 | `SIM_RACE25D_V1_S001` | race25d | UPLOADED_SCHEDULED 2026-10-02T19:00:00Z | Fri 2026-10-02 15:00 | https://www.youtube.com/shorts/lA92He_9FeQ |
| 10 | `SIM_RACE25D_V2_S002` | race25d | UPLOADED_SCHEDULED 2026-10-03T19:00:00Z | Sat 2026-10-03 15:00 | https://www.youtube.com/shorts/0o6TY6tXF_c |
| 11 | `SIM_RACE25D_V2_S003` | race25d | UPLOADED_SCHEDULED 2026-10-04T19:00:00Z | Sun 2026-10-04 15:00 | https://www.youtube.com/shorts/WinoMp1Dmzw |
| 12 | `SIM_RACE25D_V2_S004` | race25d | UPLOADED_SCHEDULED 2026-10-05T19:00:00Z | Mon 2026-10-05 15:00 | https://www.youtube.com/shorts/ABojeEOuK4M |
| 13 | `SIM_RACE25D_V2_S005` | race25d | UPLOADED_SCHEDULED 2026-10-06T19:00:00Z | Tue 2026-10-06 15:00 | https://www.youtube.com/shorts/qePl8AzQ9Rw |
| 14 | `SIM_RACE25D_V2_S006` | race25d | UPLOADED_SCHEDULED 2026-10-07T19:00:00Z | Wed 2026-10-07 15:00 | https://www.youtube.com/shorts/_CL0pzpWPTg |
| 15 | `SIM_RACE25D_V2_S007` | race25d | UPLOADED_SCHEDULED 2026-10-08T19:00:00Z | Thu 2026-10-08 15:00 | https://www.youtube.com/shorts/grvQnQ1E94k |
| 16 | `SIM_SPLASH_V2_S011` | splash | UPLOADED_SCHEDULED 2026-10-05T15:00:00Z | Mon 2026-10-05 11:00 | https://www.youtube.com/shorts/_lZj6d402lU |
| 17 | `SIM_POTHOLES_V2_S007` | potholes | UPLOADED_SCHEDULED 2026-10-06T15:00:00Z | Tue 2026-10-06 11:00 | https://www.youtube.com/shorts/15-W4OJNtt4 |
| 18 | `SIM_BUMPS_V2_S010` | bumps | UPLOADED_SCHEDULED 2026-10-07T15:00:00Z | Wed 2026-10-07 11:00 | https://www.youtube.com/shorts/dO6mPkPhO70 |
| 19 | `SIM_LAVA_V2_S021` | lava | UPLOADED_SCHEDULED 2026-10-08T15:00:00Z | Thu 2026-10-08 11:00 | https://www.youtube.com/shorts/6YB8aBiEn_o |
| 20 | `SIM_SPLASH_V2_S012` | splash | UPLOADED_SCHEDULED 2026-10-09T15:00:00Z | Fri 2026-10-09 11:00 | https://www.youtube.com/shorts/16KM8XY8BCA |
| 21 | `SIM_POTHOLES_V2_S008` | potholes | APPROVED | Sat 2026-10-10 11:00 |  |
| 22 | `SIM_SMASH25D_V4_S001` | smash25d | UPLOADED_SCHEDULED 2026-10-02T23:00:00Z | Fri 2026-10-02 19:00 | https://www.youtube.com/shorts/Q-7067tL0A8 |
| 23 | `SIM_SMASH25D_V4_S003` | smash25d | UPLOADED_SCHEDULED 2026-10-03T23:00:00Z | Sat 2026-10-03 19:00 | https://www.youtube.com/shorts/ZjUnuZvelKY |
| 24 | `SIM_SMASH25D_V4_S007` | smash25d | UPLOADED_SCHEDULED 2026-10-04T23:00:00Z | Sun 2026-10-04 19:00 | https://www.youtube.com/shorts/RCBE3lgA2uo |
| 25 | `SIM_SMASH25D_V4_S008` | smash25d | UPLOADED_SCHEDULED 2026-10-05T23:00:00Z | Mon 2026-10-05 19:00 | https://www.youtube.com/shorts/5ljCNw1Hnlg |
| 26 | `SIM_SMASH25D_V4_S011` | smash25d | UPLOADED_SCHEDULED 2026-10-06T23:00:00Z | Tue 2026-10-06 19:00 | https://www.youtube.com/shorts/eQQzWYXAda8 |
| 27 | `SIM_SMASH25D_V4_S012` | smash25d | UPLOADED_SCHEDULED 2026-10-07T23:00:00Z | Wed 2026-10-07 19:00 | https://www.youtube.com/shorts/pjx_weAS40w |
| 28 | `SIM_SMASH25D_V4_S014` | smash25d | UPLOADED_SCHEDULED 2026-10-08T23:00:00Z | Thu 2026-10-08 19:00 | https://www.youtube.com/shorts/ZXEi9fG7RZA |
| 29 | `SIM_SMASH25D_V4_S015` | smash25d | APPROVED | Fri 2026-10-09 19:00 |  |
| 30 | `SIM_POTHOLES_V2_S021` | potholes | APPROVED | Sun 2026-10-11 11:00 |  |
| 31 | `SIM_RACE25D_V4_S036` | race25d | UPLOADED_SCHEDULED 2026-10-09T19:00:00Z | Fri 2026-10-09 15:00 | https://www.youtube.com/shorts/vZFKVw21xA8 |
| 32 | `SIM_SMASH25D_V5_S002` | smash25d | APPROVED | Sat 2026-10-10 19:00 |  |
| 33 | `SIM_POTHOLES_V2_S022` | potholes | APPROVED | Mon 2026-10-12 11:00 |  |
| 34 | `SIM_RACE25D_V4_S045` | race25d | APPROVED | Sat 2026-10-10 15:00 |  |
| 35 | `SIM_SMASH25D_V5_S003` | smash25d | APPROVED | Sun 2026-10-11 19:00 |  |
| 36 | `SIM_LAVA_POTHOLES_V2_S025` | lava_potholes | APPROVED | Tue 2026-10-13 11:00 |  |
| 37 | `SIM_RACE25D_V4_S040` | race25d | APPROVED | Sun 2026-10-11 15:00 |  |
| 38 | `SIM_SMASH25D_V5_S004` | smash25d | APPROVED | Mon 2026-10-12 19:00 |  |
| 39 | `SIM_POTHOLES_V2_S027` | potholes | APPROVED | Wed 2026-10-14 11:00 |  |
| 40 | `SIM_RACE25D_V4_S037` | race25d | APPROVED | Mon 2026-10-12 15:00 |  |
| 41 | `SIM_SMASH25D_V5_S005` | smash25d | APPROVED | Tue 2026-10-13 19:00 |  |
| 42 | `SIM_LAVA_POTHOLES_V2_S026` | lava_potholes | APPROVED | Thu 2026-10-15 11:00 |  |
| 43 | `SIM_RACE25D_V4_S044` | race25d | APPROVED | Tue 2026-10-13 15:00 |  |
| 44 | `SIM_SMASH25D_V5_S008` | smash25d | APPROVED | Wed 2026-10-14 19:00 |  |
| 45 | `SIM_BUMPS_V2_S021` | bumps | APPROVED | Fri 2026-10-16 11:00 |  |
| 46 | `SIM_RACE25D_V4_S046` | race25d | APPROVED | Wed 2026-10-14 15:00 |  |
| 47 | `SIM_SMASH25D_V5_S009` | smash25d | APPROVED | Thu 2026-10-15 19:00 |  |
| 48 | `SIM_POTHOLES_V2_S031` | potholes | APPROVED | Sat 2026-10-17 11:00 |  |
| 49 | `SIM_RACE25D_V4_S043` | race25d | APPROVED | Thu 2026-10-15 15:00 |  |
| 50 | `SIM_POTHOLES_V2_S028` | potholes | APPROVED | Sun 2026-10-18 11:00 |  |
| 51 | `SIM_POTHOLES_V2_S029` | potholes | APPROVED | Mon 2026-10-19 11:00 |  |
| 1001 | `2026-10-02_story15_e01` | story15 | UPLOADED_SCHEDULED 2026-10-04T17:00:00Z | Sun 2026-10-04 13:00 | https://www.youtube.com/shorts/gAVCxOicZyM |
| 1002 | `2026-10-07_story15_e02` | story15 | APPROVED | Sun 2026-10-11 13:00 |  |
| 1501 | `2026-10-02_story15_trailer_e01` | story15_trailer | UPLOADED_SCHEDULED 2026-10-03T21:00:00Z | Sat 2026-10-03 17:00 | https://www.youtube.com/shorts/BB8Lr9LwL9g |
| 1502 | `2026-10-07_story15_trailer_e02` | story15_trailer | APPROVED | Wed 2026-10-07 08:00 |  |

## Ep. 1 — `SIM_POTHOLES_V2_S001`

- **Judul YouTube:** Cars VS Giant Potholes! Who Survives? 🚗💥 | Ep. 1 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E001_2026-09-30_potholes/SIM_POTHOLES_V2_S001.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E001_2026-09-30_potholes/SIM_POTHOLES_V2_S001.json` · audit: `renders/megawheel_arena/S01/E001_2026-09-30_potholes/SIM_POTHOLES_V2_S001_audit.md`
- **Season / seri / seed:** S01 / potholes / 1
- **Tema / narator:** sunset-clear-beach / en-US-EmmaMultilingualNeural
- **Durasi:** 44.63 s
- **Tokoh dan hasil:** Level 1: Zippy (sports) → pit@obs2+broken; Level 2: Buster (bus) → stuck@obs0; Level 3 (juara): Rocky (monster) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-02T15:00:00Z (approve 2026-09-30)
- **Antrian:** SCHEDULED 2026-10-02T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/PwlO0ptmi-c

## Ep. 2 — `SIM_BUMPS_V2_S002`

- **Judul YouTube:** Cars VS Giant Speed Bumps! Who Survives? 🚗💥 | Ep. 2 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E002_2026-09-30_bumps/SIM_BUMPS_V2_S002.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E002_2026-09-30_bumps/SIM_BUMPS_V2_S002.json` · audit: `renders/megawheel_arena/S01/E002_2026-09-30_bumps/SIM_BUMPS_V2_S002_audit.md`
- **Season / seri / seed:** S01 / bumps / 2
- **Tema / narator:** night-clear-countryside / en-US-JennyNeural
- **Durasi:** 49.23 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → flip@obs3; Level 2: Titan (bigrig) → stuck@obs1; Level 3 (juara): Grizzly (monster2) → win
- **Status:** UPLOADED_SCHEDULED 2026-09-30T19:00:00Z (approve 2026-09-30)
- **Antrian:** SCHEDULED 2026-09-30T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/dVBtbf8Bi_Q

## Ep. 3 — `SIM_POTHOLES_V2_S003`

- **Judul YouTube:** Cars VS Giant Potholes! Who Survives? 🚗💥 | Ep. 3 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E003_2026-09-30_potholes/SIM_POTHOLES_V2_S003.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E003_2026-09-30_potholes/SIM_POTHOLES_V2_S003.json` · audit: `renders/megawheel_arena/S01/E003_2026-09-30_potholes/SIM_POTHOLES_V2_S003_audit.md`
- **Season / seri / seed:** S01 / potholes / 3
- **Tema / narator:** morning-clear-countryside / en-US-AvaMultilingualNeural
- **Durasi:** 46.93 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → pit@obs2+broken; Level 2: Sprinkles (icecream) → stuck@obs0; Level 3 (juara): Rocky (monster) → win
- **Status:** UPLOADED_SCHEDULED 2026-09-30T23:00:00Z (approve 2026-09-30)
- **Antrian:** SCHEDULED 2026-09-30T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/yf0y4R83hto

## Ep. 4 — `SIM_BUMPS_V2_S004`

- **Judul YouTube:** Cars VS Giant Speed Bumps! Who Survives? 🚗💥 | Ep. 4 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E004_2026-09-30_bumps/SIM_BUMPS_V2_S004.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E004_2026-09-30_bumps/SIM_BUMPS_V2_S004.json` · audit: `renders/megawheel_arena/S01/E004_2026-09-30_bumps/SIM_BUMPS_V2_S004_audit.md`
- **Season / seri / seed:** S01 / bumps / 4
- **Tema / narator:** sunset-rain-mountains / en-US-MichelleNeural
- **Durasi:** 49.33 s
- **Tokoh dan hasil:** Level 1: Siren (police) → stuck@obs2; Level 2: Hydro (firetruck) → stuck@obs2; Level 3 (juara): Grizzly (monster2) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-01T15:00:00Z (approve 2026-09-30)
- **Antrian:** SCHEDULED 2026-10-01T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/3CfgGpkOx3Q

## Ep. 5 — `SIM_POTHOLES_V2_S005`

- **Judul YouTube:** Cars VS Giant Potholes! Who Survives? 🚗💥 | Ep. 5 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E005_2026-09-30_potholes/SIM_POTHOLES_V2_S005.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E005_2026-09-30_potholes/SIM_POTHOLES_V2_S005.json` · audit: `renders/megawheel_arena/S01/E005_2026-09-30_potholes/SIM_POTHOLES_V2_S005_audit.md`
- **Season / seri / seed:** S01 / potholes / 5
- **Tema / narator:** noon-rain-beach / en-US-AriaNeural
- **Durasi:** 47.8 s
- **Tokoh dan hasil:** Level 1: Zippy (sports) → flip@obs2+broken; Level 2: Sprinkles (icecream) → stuck@obs0; Level 3 (juara): Grizzly (monster2) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-01T19:00:00Z (approve 2026-09-30)
- **Antrian:** SCHEDULED 2026-10-01T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/xEWas3W61QU

## Ep. 6 — `SIM_BUMPS_V2_S006`

- **Judul YouTube:** Cars VS Giant Speed Bumps! Who Survives? 🚗💥 | Ep. 6 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E006_2026-09-30_bumps/SIM_BUMPS_V2_S006.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E006_2026-09-30_bumps/SIM_BUMPS_V2_S006.json` · audit: `renders/megawheel_arena/S01/E006_2026-09-30_bumps/SIM_BUMPS_V2_S006_audit.md`
- **Season / seri / seed:** S01 / bumps / 6
- **Tema / narator:** sunset-clear-countryside / en-US-JennyNeural
- **Durasi:** 47.27 s
- **Tokoh dan hasil:** Level 1: Siren (police) → flip@obs2+broken; Level 2: Buster (bus) → flip@obs1+broken; Level 3 (juara): Rocky (monster) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-01T23:00:00Z (approve 2026-09-30)
- **Antrian:** SCHEDULED 2026-10-01T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/nXlV3f6Wux8

## Ep. 7 — `SIM_SPLASH_V2_S007`

- **Judul YouTube:** Cars VS Slippery Splash Zone! Who Survives? 💦🚗 | Ep. 7 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E007_2026-09-30_splash/SIM_SPLASH_V2_S007.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E007_2026-09-30_splash/SIM_SPLASH_V2_S007.json` · audit: `renders/megawheel_arena/S01/E007_2026-09-30_splash/SIM_SPLASH_V2_S007_audit.md`
- **Season / seri / seed:** S01 / splash / 7
- **Tema / narator:** night-clear-desert / en-US-AvaMultilingualNeural
- **Durasi:** 48.4 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → pit@obs0; Level 2: Sprinkles (icecream) → stuck@obs1; Level 3 (juara): Titan (bigrig) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-03T15:00:00Z (approve 2026-09-30)
- **Antrian:** SCHEDULED 2026-10-03T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/0FEC9QmNYw0

## Ep. 8 — `SIM_LAVA_V2_S003`

- **Judul YouTube:** Cars VS Lava Road! Who Survives? 🌋🔥 | Ep. 8 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E008_2026-09-30_lava/SIM_LAVA_V2_S003.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E008_2026-09-30_lava/SIM_LAVA_V2_S003.json` · audit: `renders/megawheel_arena/S01/E008_2026-09-30_lava/SIM_LAVA_V2_S003_audit.md`
- **Season / seri / seed:** S01 / lava / 3
- **Tema / narator:** morning-clear-volcano / en-US-AriaNeural
- **Durasi:** 46.2 s
- **Tokoh dan hasil:** Level 1: Zippy (sports) → pit@obs0; Level 2: Hydro (firetruck) → lava@obs2+broken; Level 3 (juara): Titan (bigrig) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-04T15:00:00Z (approve 2026-09-30)
- **Antrian:** SCHEDULED 2026-10-04T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/LIP2P98Be6M

## Ep. 9 — `SIM_RACE25D_V1_S001`

- **Judul YouTube:** Slippery Race Showdown! Who Wins? 🏁💦 | Ep. 9 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E009_2026-09-30_race25d/SIM_RACE25D_V1_S001.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E009_2026-09-30_race25d/SIM_RACE25D_V1_S001.json` · audit: `renders/megawheel_arena/S01/E009_2026-09-30_race25d/SIM_RACE25D_V1_S001_audit.md`
- **Season / seri / seed:** S01 / race25d / 1
- **Tema / narator:** noon-clear-city / en-US-EmmaMultilingualNeural
- **Durasi:** 29.23 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → win+jump+bump; Level 2: Hydro (firetruck) → p3; Level 3 (juara): Siren (police) → p2; Level 4: Tilly (taxi) → p4+spin
- **Status:** UPLOADED_SCHEDULED 2026-10-02T19:00:00Z (approve 2026-09-30)
- **Antrian:** SCHEDULED 2026-10-02T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/lA92He_9FeQ

## Ep. 10 — `SIM_RACE25D_V2_S002`

- **Judul YouTube:** Meteors, Lasers & Lava! Who Wins the Race? 🏁 | Ep. 10 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E010_2026-09-30_race25d/SIM_RACE25D_V2_S002.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E010_2026-09-30_race25d/SIM_RACE25D_V2_S002.json` · audit: `renders/megawheel_arena/S01/E010_2026-09-30_race25d/SIM_RACE25D_V2_S002_audit.md`
- **Season / seri / seed:** S01 / race25d / 2
- **Tema / narator:** morning-clear-desert / en-US-MichelleNeural
- **Durasi:** 32.8 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → p3+dragon_ice; Level 2: Buster (bus) → win+lava; Level 3 (juara): Zippy (sports) → p2; Level 4: Tilly (taxi) → p4+ufo
- **Status:** UPLOADED_SCHEDULED 2026-10-03T19:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-03T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/0o6TY6tXF_c

## Ep. 11 — `SIM_RACE25D_V2_S003`

- **Judul YouTube:** Wildest Race Ever! Who Crosses First? 🏁 | Ep. 11 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E011_2026-09-30_race25d/SIM_RACE25D_V2_S003.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E011_2026-09-30_race25d/SIM_RACE25D_V2_S003.json` · audit: `renders/megawheel_arena/S01/E011_2026-09-30_race25d/SIM_RACE25D_V2_S003_audit.md`
- **Season / seri / seed:** S01 / race25d / 3
- **Tema / narator:** night-clear-city / en-US-AvaMultilingualNeural
- **Durasi:** 34.97 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p2; Level 2: Siren (police) → p4+dragon_fire; Level 3 (juara): Nitro (f1) → p3+meteor; Level 4: Rocky (monster) → win+dodge_lava
- **Status:** UPLOADED_SCHEDULED 2026-10-04T19:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-04T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/WinoMp1Dmzw

## Ep. 12 — `SIM_RACE25D_V2_S004`

- **Judul YouTube:** 4 Cars, 1 Finish Line! Who Wins? 🏁 | Ep. 12 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E012_2026-09-30_race25d/SIM_RACE25D_V2_S004.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E012_2026-09-30_race25d/SIM_RACE25D_V2_S004.json` · audit: `renders/megawheel_arena/S01/E012_2026-09-30_race25d/SIM_RACE25D_V2_S004_audit.md`
- **Season / seri / seed:** S01 / race25d / 4
- **Tema / narator:** noon-snow-mountains / en-US-MichelleNeural
- **Durasi:** 35.1 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p4+dragon_fire; Level 2: Grizzly (monster2) → p3+meteor; Level 3 (juara): Zippy (sports) → win+dodge_pothole; Level 4: Siren (police) → p2
- **Status:** UPLOADED_SCHEDULED 2026-10-05T19:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-05T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/ABojeEOuK4M

## Ep. 13 — `SIM_RACE25D_V2_S005`

- **Judul YouTube:** Crazy Obstacle Race! Who Survives? 🏁💥 | Ep. 13 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E013_2026-09-30_race25d/SIM_RACE25D_V2_S005.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E013_2026-09-30_race25d/SIM_RACE25D_V2_S005.json` · audit: `renders/megawheel_arena/S01/E013_2026-09-30_race25d/SIM_RACE25D_V2_S005_audit.md`
- **Season / seri / seed:** S01 / race25d / 5
- **Tema / narator:** noon-clear-city / en-US-AriaNeural
- **Durasi:** 33.43 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → win; Level 2: Rocky (monster) → p2; Level 3 (juara): Tilly (taxi) → p3+meteor+dodge_wall; Level 4: Nitro (f1) → p4+ufo
- **Status:** UPLOADED_SCHEDULED 2026-10-06T19:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-06T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/qePl8AzQ9Rw

## Ep. 14 — `SIM_RACE25D_V2_S006`

- **Judul YouTube:** Meteors, Lasers & Lava! Who Wins the Race? 🏁 | Ep. 14 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E014_2026-09-30_race25d/SIM_RACE25D_V2_S006.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E014_2026-09-30_race25d/SIM_RACE25D_V2_S006.json` · audit: `renders/megawheel_arena/S01/E014_2026-09-30_race25d/SIM_RACE25D_V2_S006_audit.md`
- **Season / seri / seed:** S01 / race25d / 6
- **Tema / narator:** sunset-clear-mountains / en-US-JennyNeural
- **Durasi:** 35.23 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p3+crusher; Level 2: Grizzly (monster2) → p4+ufo; Level 3 (juara): Zippy (sports) → p2+meteor; Level 4: Siren (police) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-07T19:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-07T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/_CL0pzpWPTg

## Ep. 15 — `SIM_RACE25D_V2_S007`

- **Judul YouTube:** Wildest Race Ever! Who Crosses First? 🏁 | Ep. 15 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E015_2026-09-30_race25d/SIM_RACE25D_V2_S007.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E015_2026-09-30_race25d/SIM_RACE25D_V2_S007.json` · audit: `renders/megawheel_arena/S01/E015_2026-09-30_race25d/SIM_RACE25D_V2_S007_audit.md`
- **Season / seri / seed:** S01 / race25d / 7
- **Tema / narator:** morning-clear-beach / en-US-EmmaMultilingualNeural
- **Durasi:** 34.17 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p4+dragon_ice; Level 2: Nitro (f1) → win+dodge_puddle; Level 3 (juara): Rocky (monster) → p3+dragon_fire; Level 4: Tilly (taxi) → p2
- **Status:** UPLOADED_SCHEDULED 2026-10-08T19:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-08T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/grvQnQ1E94k

## Ep. 16 — `SIM_SPLASH_V2_S011`

- **Judul YouTube:** Cars VS Slippery Splash Zone! Who Survives? 💦🚗 | Ep. 16 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E016_2026-10-01_splash/SIM_SPLASH_V2_S011.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E016_2026-10-01_splash/SIM_SPLASH_V2_S011.json` · audit: `renders/megawheel_arena/S01/E016_2026-10-01_splash/SIM_SPLASH_V2_S011_audit.md`
- **Season / seri / seed:** S01 / splash / 11
- **Tema / narator:** morning-clear-countryside / chatterbox:f1
- **Durasi:** 56.5 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → flip@obs2+broken; Level 2: Buster (bus) → pit@obs0+broken; Level 3 (juara): Hydro (firetruck) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-05T15:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-05T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/_lZj6d402lU

## Ep. 17 — `SIM_POTHOLES_V2_S007`

- **Judul YouTube:** Cars VS Giant Potholes! Who Survives? 🚗💥 | Ep. 17 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E017_2026-10-01_potholes/SIM_POTHOLES_V2_S007.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E017_2026-10-01_potholes/SIM_POTHOLES_V2_S007.json` · audit: `renders/megawheel_arena/S01/E017_2026-10-01_potholes/SIM_POTHOLES_V2_S007_audit.md`
- **Season / seri / seed:** S01 / potholes / 7
- **Tema / narator:** sunset-clear-mountains / chatterbox:m1
- **Durasi:** 49.33 s
- **Tokoh dan hasil:** Level 1: Zippy (sports) → pit@obs2+broken; Level 2: Sprinkles (icecream) → stuck@obs0; Level 3 (juara): Buster (bus) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-06T15:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-06T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/15-W4OJNtt4

## Ep. 18 — `SIM_BUMPS_V2_S010`

- **Judul YouTube:** Cars VS Giant Speed Bumps! Who Survives? 🚗💥 | Ep. 18 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E018_2026-10-01_bumps/SIM_BUMPS_V2_S010.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E018_2026-10-01_bumps/SIM_BUMPS_V2_S010.json` · audit: `renders/megawheel_arena/S01/E018_2026-10-01_bumps/SIM_BUMPS_V2_S010_audit.md`
- **Season / seri / seed:** S01 / bumps / 10
- **Tema / narator:** noon-clear-beach / chatterbox:f1
- **Durasi:** 48.57 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → flip@obs2+broken; Level 2: Titan (bigrig) → stuck@obs1; Level 3 (juara): Grizzly (monster2) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-07T15:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-07T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/dO6mPkPhO70

## Ep. 19 — `SIM_LAVA_V2_S021`

- **Judul YouTube:** Cars VS Lava Road! Who Survives? 🌋🔥 | Ep. 19 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E019_2026-10-01_lava/SIM_LAVA_V2_S021.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E019_2026-10-01_lava/SIM_LAVA_V2_S021.json` · audit: `renders/megawheel_arena/S01/E019_2026-10-01_lava/SIM_LAVA_V2_S021_audit.md`
- **Season / seri / seed:** S01 / lava / 21
- **Tema / narator:** night-clear-volcano / chatterbox:m1
- **Durasi:** 46.07 s
- **Tokoh dan hasil:** Level 1: Siren (police) → pit@obs0; Level 2: Buster (bus) → lava@obs1+broken; Level 3 (juara): Hydro (firetruck) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-08T15:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-08T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/6YB8aBiEn_o

## Ep. 20 — `SIM_SPLASH_V2_S012`

- **Judul YouTube:** Cars VS Slippery Splash Zone! Who Survives? 💦🚗 | Ep. 20 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E020_2026-10-01_splash/SIM_SPLASH_V2_S012.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E020_2026-10-01_splash/SIM_SPLASH_V2_S012.json` · audit: `renders/megawheel_arena/S01/E020_2026-10-01_splash/SIM_SPLASH_V2_S012_audit.md`
- **Season / seri / seed:** S01 / splash / 12
- **Tema / narator:** noon-clear-city / chatterbox:m1
- **Durasi:** 48.9 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → flip@obs2; Level 2: Sprinkles (icecream) → pit@obs0+broken; Level 3 (juara): Tilly (taxi) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-09T15:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-09T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/16KM8XY8BCA

## Ep. 21 — `SIM_POTHOLES_V2_S008`

- **Judul YouTube:** Cars VS Giant Potholes! Who Survives? 🚗💥 | Ep. 21 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E021_2026-10-01_potholes/SIM_POTHOLES_V2_S008.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E021_2026-10-01_potholes/SIM_POTHOLES_V2_S008.json` · audit: `renders/megawheel_arena/S01/E021_2026-10-01_potholes/SIM_POTHOLES_V2_S008_audit.md`
- **Season / seri / seed:** S01 / potholes / 8
- **Tema / narator:** morning-clear-desert / chatterbox:f1
- **Durasi:** 46.7 s
- **Tokoh dan hasil:** Level 1: Zippy (sports) → flip@obs2+broken; Level 2: Titan (bigrig) → stuck@obs0; Level 3 (juara): Sprinkles (icecream) → win
- **Status:** APPROVED (approve 2026-10-01)
- **Antrian:** QUEUED 2026-10-10T15:00:00Z
- **YouTube:** belum diupload

## Ep. 22 — `SIM_SMASH25D_V4_S001`

- **Judul YouTube:** Last Car Standing Wins! 💥 | Ep. 22 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E022_2026-10-01_smash25d/SIM_SMASH25D_V4_S001.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E022_2026-10-01_smash25d/SIM_SMASH25D_V4_S001.json` · audit: `renders/megawheel_arena/S01/E022_2026-10-01_smash25d/SIM_SMASH25D_V4_S001_audit.md`
- **Season / seri / seed:** S01 / smash25d / 1
- **Tema / narator:** night-clear-desert / chatterbox:mw-announcers-m1f1
- **Durasi:** 49.93 s
- **Tokoh dan hasil:** Level 1: Grizzly (monster2) → p4+wreck; Level 2: Titan (bigrig) → p3+ring; Level 3 (juara): Siren (police) → win; Level 4: Nitro (f1) → p2+wreck
- **Status:** UPLOADED_SCHEDULED 2026-10-02T23:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-02T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/Q-7067tL0A8

## Ep. 23 — `SIM_SMASH25D_V4_S003`

- **Judul YouTube:** Crash Battle! Only One Can Win! 💥 | Ep. 23 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E023_2026-10-01_smash25d/SIM_SMASH25D_V4_S003.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E023_2026-10-01_smash25d/SIM_SMASH25D_V4_S003.json` · audit: `renders/megawheel_arena/S01/E023_2026-10-01_smash25d/SIM_SMASH25D_V4_S003_audit.md`
- **Season / seri / seed:** S01 / smash25d / 3
- **Tema / narator:** sunset-clear-city / chatterbox:mw-announcers-m1f1
- **Durasi:** 47.2 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → win; Level 2: Grizzly (monster2) → p2+wreck; Level 3 (juara): Nitro (f1) → p4+ring; Level 4: Siren (police) → p3+wreck
- **Status:** UPLOADED_SCHEDULED 2026-10-03T23:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-03T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/ZjUnuZvelKY

## Ep. 24 — `SIM_SMASH25D_V4_S007`

- **Judul YouTube:** Crash Battle! Only One Can Win! 💥 | Ep. 24 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E024_2026-10-01_smash25d/SIM_SMASH25D_V4_S007.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E024_2026-10-01_smash25d/SIM_SMASH25D_V4_S007.json` · audit: `renders/megawheel_arena/S01/E024_2026-10-01_smash25d/SIM_SMASH25D_V4_S007_audit.md`
- **Season / seri / seed:** S01 / smash25d / 7
- **Tema / narator:** morning-clear-mountains / chatterbox:mw-announcers-m1f1
- **Durasi:** 48.1 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p4+ring; Level 2: Rocky (monster) → p2+wreck; Level 3 (juara): Tilly (taxi) → win; Level 4: Siren (police) → p3+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-04T23:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-04T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/RCBE3lgA2uo

## Ep. 25 — `SIM_SMASH25D_V4_S008`

- **Judul YouTube:** 4 Cars Enter, 1 Survives! 💥 Smash Arena | Ep. 25 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E025_2026-10-01_smash25d/SIM_SMASH25D_V4_S008.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E025_2026-10-01_smash25d/SIM_SMASH25D_V4_S008.json` · audit: `renders/megawheel_arena/S01/E025_2026-10-01_smash25d/SIM_SMASH25D_V4_S008_audit.md`
- **Season / seri / seed:** S01 / smash25d / 8
- **Tema / narator:** night-snow-countryside / chatterbox:mw-announcers-m1f1
- **Durasi:** 45.93 s
- **Tokoh dan hasil:** Level 1: Rocky (monster) → p2+ring; Level 2: Hydro (firetruck) → p4+ring; Level 3 (juara): Zippy (sports) → win; Level 4: Tilly (taxi) → p3+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-05T23:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-05T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/5ljCNw1Hnlg

## Ep. 26 — `SIM_SMASH25D_V4_S011`

- **Judul YouTube:** Crash Battle! Only One Can Win! 💥 | Ep. 26 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E026_2026-10-01_smash25d/SIM_SMASH25D_V4_S011.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E026_2026-10-01_smash25d/SIM_SMASH25D_V4_S011.json` · audit: `renders/megawheel_arena/S01/E026_2026-10-01_smash25d/SIM_SMASH25D_V4_S011_audit.md`
- **Season / seri / seed:** S01 / smash25d / 11
- **Tema / narator:** sunset-clear-desert / chatterbox:mw-announcers-m1f1
- **Durasi:** 52.87 s
- **Tokoh dan hasil:** Level 1: Rocky (monster) → win; Level 2: Sprinkles (icecream) → p2+ring; Level 3 (juara): Siren (police) → p3+ring; Level 4: Zippy (sports) → p4+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-06T23:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-06T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/eQQzWYXAda8

## Ep. 27 — `SIM_SMASH25D_V4_S012`

- **Judul YouTube:** 4 Cars Enter, 1 Survives! 💥 Smash Arena | Ep. 27 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E027_2026-10-01_smash25d/SIM_SMASH25D_V4_S012.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E027_2026-10-01_smash25d/SIM_SMASH25D_V4_S012.json` · audit: `renders/megawheel_arena/S01/E027_2026-10-01_smash25d/SIM_SMASH25D_V4_S012_audit.md`
- **Season / seri / seed:** S01 / smash25d / 12
- **Tema / narator:** night-clear-beach / chatterbox:mw-announcers-m1f1
- **Durasi:** 47.0 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → win; Level 2: Grizzly (monster2) → p3+ring; Level 3 (juara): Tilly (taxi) → p4+ring; Level 4: Zippy (sports) → p2+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-07T23:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-07T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/pjx_weAS40w

## Ep. 28 — `SIM_SMASH25D_V4_S014`

- **Judul YouTube:** Who Survives the Smash Arena? 💥 | Ep. 28 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E028_2026-10-01_smash25d/SIM_SMASH25D_V4_S014.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E028_2026-10-01_smash25d/SIM_SMASH25D_V4_S014.json` · audit: `renders/megawheel_arena/S01/E028_2026-10-01_smash25d/SIM_SMASH25D_V4_S014_audit.md`
- **Season / seri / seed:** S01 / smash25d / 14
- **Tema / narator:** noon-rain-countryside / chatterbox:mw-announcers-m1f1
- **Durasi:** 50.03 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p3+ring; Level 2: Rocky (monster) → p4+wreck; Level 3 (juara): Nitro (f1) → win; Level 4: Tilly (taxi) → p2+wreck
- **Status:** UPLOADED_SCHEDULED 2026-10-08T23:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-08T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/ZXEi9fG7RZA

## Ep. 29 — `SIM_SMASH25D_V4_S015`

- **Judul YouTube:** Crash Battle! Only One Can Win! 💥 | Ep. 29 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E029_2026-10-01_smash25d/SIM_SMASH25D_V4_S015.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E029_2026-10-01_smash25d/SIM_SMASH25D_V4_S015.json` · audit: `renders/megawheel_arena/S01/E029_2026-10-01_smash25d/SIM_SMASH25D_V4_S015_audit.md`
- **Season / seri / seed:** S01 / smash25d / 15
- **Tema / narator:** noon-clear-beach / chatterbox:mw-announcers-m1f1
- **Durasi:** 49.77 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p4+ring; Level 2: Grizzly (monster2) → win; Level 3 (juara): Nitro (f1) → p3+ring; Level 4: Zippy (sports) → p2+wreck
- **Status:** APPROVED (approve 2026-10-01)
- **Antrian:** QUEUED 2026-10-09T23:00:00Z
- **YouTube:** belum diupload

## Ep. 30 — `SIM_POTHOLES_V2_S021`

- **Judul YouTube:** Can Siren the Police Car Survive Giant Potholes? 🚗💥 | Ep. 30 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E030_2026-10-03_potholes/SIM_POTHOLES_V2_S021.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E030_2026-10-03_potholes/SIM_POTHOLES_V2_S021.json` · audit: `renders/megawheel_arena/S01/E030_2026-10-03_potholes/SIM_POTHOLES_V2_S021_audit.md`
- **Season / seri / seed:** S01 / potholes / 21
- **Tema / narator:** night-rain-city / chatterbox:m1
- **Durasi:** 51.07 s
- **Tokoh dan hasil:** Level 1: Siren (police) → rollback@obs2+broken; Level 2: Titan (bigrig) → stuck@obs1; Level 3 (juara): Zippy (sports) → win
- **Status:** APPROVED (approve 2026-10-03)
- **Antrian:** QUEUED 2026-10-11T15:00:00Z
- **YouTube:** belum diupload

## Ep. 31 — `SIM_RACE25D_V4_S036`

- **Judul YouTube:** Can Zippy Survive the Oil Slick? 🏁 | Ep. 31 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E031_2026-10-04_race25d/SIM_RACE25D_V4_S036.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E031_2026-10-04_race25d/SIM_RACE25D_V4_S036.json` · audit: `renders/megawheel_arena/S02/E031_2026-10-04_race25d/SIM_RACE25D_V4_S036_audit.md`
- **Season / seri / seed:** S02 / race25d / 36
- **Tema / narator:** night-clear-countryside / chatterbox:f1
- **Durasi:** 37.04 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p2+dodge_crusher; Level 2: Rocky (monster) → p4+dragon_fire+bump; Level 3 (juara): Tilly (taxi) → win; Level 4: Zippy (sports) → p3+oil
- **Status:** UPLOADED_SCHEDULED 2026-10-09T19:00:00Z (approve 2026-10-04)
- **Antrian:** SCHEDULED 2026-10-09T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/vZFKVw21xA8

## Ep. 32 — `SIM_SMASH25D_V5_S002`

- **Judul YouTube:** Hydro, Grizzly, Siren or Zippy? Last Car Standing! 💥 | Ep. 32 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E032_2026-10-03_smash25d/SIM_SMASH25D_V5_S002.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E032_2026-10-03_smash25d/SIM_SMASH25D_V5_S002.json` · audit: `renders/megawheel_arena/S02/E032_2026-10-03_smash25d/SIM_SMASH25D_V5_S002_audit.md`
- **Season / seri / seed:** S02 / smash25d / 2
- **Tema / narator:** morning-clear-desert / chatterbox:mw-announcers-m1f1
- **Durasi:** 50.08 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p4+ring; Level 2: Grizzly (monster2) → p2+ring; Level 3 (juara): Siren (police) → win; Level 4: Zippy (sports) → p3+wreck
- **Status:** APPROVED (approve 2026-10-03)
- **Antrian:** QUEUED 2026-10-10T23:00:00Z
- **YouTube:** belum diupload

## Ep. 33 — `SIM_POTHOLES_V2_S022`

- **Judul YouTube:** Taxi vs Giant Potholes! Can Tilly Make It? 🚗💥 | Ep. 33 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E033_2026-10-03_potholes/SIM_POTHOLES_V2_S022.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E033_2026-10-03_potholes/SIM_POTHOLES_V2_S022.json` · audit: `renders/megawheel_arena/S02/E033_2026-10-03_potholes/SIM_POTHOLES_V2_S022_audit.md`
- **Season / seri / seed:** S02 / potholes / 22
- **Tema / narator:** night-clear-mountains / en-US-EmmaMultilingualNeural
- **Durasi:** 47.97 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → rollback@obs2+broken; Level 2: Sprinkles (icecream) → stuck@obs0; Level 3 (juara): Hydro (firetruck) → win
- **Status:** APPROVED (approve 2026-10-03)
- **Antrian:** QUEUED 2026-10-12T15:00:00Z
- **YouTube:** belum diupload

## Ep. 34 — `SIM_RACE25D_V4_S045`

- **Judul YouTube:** Nitro vs the Giant Hammer! Who Wins the Race? 🏁 | Ep. 34 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E034_2026-10-04_race25d/SIM_RACE25D_V4_S045.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E034_2026-10-04_race25d/SIM_RACE25D_V4_S045.json` · audit: `renders/megawheel_arena/S02/E034_2026-10-04_race25d/SIM_RACE25D_V4_S045_audit.md`
- **Season / seri / seed:** S02 / race25d / 45
- **Tema / narator:** noon-clear-beach / chatterbox:f1
- **Durasi:** 37.11 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p2+dodge_oil; Level 2: Grizzly (monster2) → win; Level 3 (juara): Nitro (f1) → p3+hammer; Level 4: Zippy (sports) → p4+dragon_ice
- **Status:** APPROVED (approve 2026-10-05)
- **Antrian:** QUEUED 2026-10-10T19:00:00Z
- **YouTube:** belum diupload

## Ep. 35 — `SIM_SMASH25D_V5_S003`

- **Judul YouTube:** Can Tiny Nitro Beat a Big Rig? 💥 | Ep. 35 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E035_2026-10-03_smash25d/SIM_SMASH25D_V5_S003.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E035_2026-10-03_smash25d/SIM_SMASH25D_V5_S003.json` · audit: `renders/megawheel_arena/S02/E035_2026-10-03_smash25d/SIM_SMASH25D_V5_S003_audit.md`
- **Season / seri / seed:** S02 / smash25d / 3
- **Tema / narator:** sunset-clear-city / chatterbox:mw-announcers-m1f1
- **Durasi:** 53.23 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → win; Level 2: Grizzly (monster2) → p2+wreck; Level 3 (juara): Nitro (f1) → p4+ring; Level 4: Siren (police) → p3+wreck
- **Status:** APPROVED (approve 2026-10-03)
- **Antrian:** QUEUED 2026-10-11T23:00:00Z
- **YouTube:** belum diupload

## Ep. 36 — `SIM_LAVA_POTHOLES_V2_S025`

- **Judul YouTube:** Race Car vs Giant Lava Potholes! Can Nitro Make It? 🌋🔥 | Ep. 36 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E036_2026-10-03_lava_potholes/SIM_LAVA_POTHOLES_V2_S025.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E036_2026-10-03_lava_potholes/SIM_LAVA_POTHOLES_V2_S025.json` · audit: `renders/megawheel_arena/S02/E036_2026-10-03_lava_potholes/SIM_LAVA_POTHOLES_V2_S025_audit.md`
- **Season / seri / seed:** S02 / lava_potholes / 25
- **Tema / narator:** noon-clear-volcano / chatterbox:f1
- **Durasi:** 50.77 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → pit@obs2+broken; Level 2: Sprinkles (icecream) → stuck@obs0; Level 3 (juara): Tilly (taxi) → win
- **Status:** APPROVED (approve 2026-10-03)
- **Antrian:** QUEUED 2026-10-13T15:00:00Z
- **YouTube:** belum diupload

## Ep. 37 — `SIM_RACE25D_V4_S040`

- **Judul YouTube:** Can Tilly Survive the Meteors? 🏁 | Ep. 37 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E037_2026-10-04_race25d/SIM_RACE25D_V4_S040.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E037_2026-10-04_race25d/SIM_RACE25D_V4_S040.json` · audit: `renders/megawheel_arena/S02/E037_2026-10-04_race25d/SIM_RACE25D_V4_S040_audit.md`
- **Season / seri / seed:** S02 / race25d / 40
- **Tema / narator:** noon-clear-countryside / chatterbox:f1
- **Durasi:** 35.25 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p4+laser; Level 2: Rocky (monster) → p2+dodge_oil; Level 3 (juara): Tilly (taxi) → p3+meteor; Level 4: Zippy (sports) → win
- **Status:** APPROVED (approve 2026-10-04)
- **Antrian:** QUEUED 2026-10-11T19:00:00Z
- **YouTube:** belum diupload

## Ep. 38 — `SIM_SMASH25D_V5_S004`

- **Judul YouTube:** Fire Truck vs Monster Truck vs Taxi vs Race Car! Who Survives? 💥 | Ep. 38 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E038_2026-10-03_smash25d/SIM_SMASH25D_V5_S004.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E038_2026-10-03_smash25d/SIM_SMASH25D_V5_S004.json` · audit: `renders/megawheel_arena/S02/E038_2026-10-03_smash25d/SIM_SMASH25D_V5_S004_audit.md`
- **Season / seri / seed:** S02 / smash25d / 4
- **Tema / narator:** night-snow-mountains / chatterbox:mw-announcers-m1f1
- **Durasi:** 51.61 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → win; Level 2: Grizzly (monster2) → p4+ring; Level 3 (juara): Tilly (taxi) → p3+wreck; Level 4: Nitro (f1) → p2+wreck
- **Status:** APPROVED (approve 2026-10-03)
- **Antrian:** QUEUED 2026-10-12T23:00:00Z
- **YouTube:** belum diupload

## Ep. 39 — `SIM_POTHOLES_V2_S027`

- **Judul YouTube:** Can Nitro the Race Car Survive Giant Potholes? 🚗💥 | Ep. 39 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E039_2026-10-03_potholes/SIM_POTHOLES_V2_S027.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E039_2026-10-03_potholes/SIM_POTHOLES_V2_S027.json` · audit: `renders/megawheel_arena/S02/E039_2026-10-03_potholes/SIM_POTHOLES_V2_S027_audit.md`
- **Season / seri / seed:** S02 / potholes / 27
- **Tema / narator:** sunset-clear-beach / chatterbox:f1
- **Durasi:** 48.7 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → pit@obs2+broken; Level 2: Hydro (firetruck) → stuck@obs0; Level 3 (juara): Buster (bus) → win
- **Status:** APPROVED (approve 2026-10-03)
- **Antrian:** QUEUED 2026-10-14T15:00:00Z
- **YouTube:** belum diupload

## Ep. 40 — `SIM_RACE25D_V4_S037`

- **Judul YouTube:** Can Siren Survive the Oil Slick? 🏁 | Ep. 40 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E040_2026-10-04_race25d/SIM_RACE25D_V4_S037.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E040_2026-10-04_race25d/SIM_RACE25D_V4_S037.json` · audit: `renders/megawheel_arena/S02/E040_2026-10-04_race25d/SIM_RACE25D_V4_S037_audit.md`
- **Season / seri / seed:** S02 / race25d / 37
- **Tema / narator:** morning-snow-city / chatterbox:f1
- **Durasi:** 35.79 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p4+dragon_fire; Level 2: Grizzly (monster2) → p2+dodge_lava; Level 3 (juara): Tilly (taxi) → win; Level 4: Siren (police) → p3+oil
- **Status:** APPROVED (approve 2026-10-04)
- **Antrian:** QUEUED 2026-10-12T19:00:00Z
- **YouTube:** belum diupload

## Ep. 41 — `SIM_SMASH25D_V5_S005`

- **Judul YouTube:** Sprinkles, Rocky, Zippy or Siren? Last Car Standing! 💥 | Ep. 41 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E041_2026-10-03_smash25d/SIM_SMASH25D_V5_S005.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E041_2026-10-03_smash25d/SIM_SMASH25D_V5_S005.json` · audit: `renders/megawheel_arena/S02/E041_2026-10-03_smash25d/SIM_SMASH25D_V5_S005_audit.md`
- **Season / seri / seed:** S02 / smash25d / 5
- **Tema / narator:** noon-clear-city / chatterbox:mw-announcers-m1f1
- **Durasi:** 50.47 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p2+ring; Level 2: Rocky (monster) → win; Level 3 (juara): Zippy (sports) → p3+wreck; Level 4: Siren (police) → p4+ring
- **Status:** APPROVED (approve 2026-10-03)
- **Antrian:** QUEUED 2026-10-13T23:00:00Z
- **YouTube:** belum diupload

## Ep. 42 — `SIM_LAVA_POTHOLES_V2_S026`

- **Judul YouTube:** Will Siren the Police Car Survive Giant Lava Potholes? 🌋🔥 | Ep. 42 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E042_2026-10-03_lava_potholes/SIM_LAVA_POTHOLES_V2_S026.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E042_2026-10-03_lava_potholes/SIM_LAVA_POTHOLES_V2_S026.json` · audit: `renders/megawheel_arena/S02/E042_2026-10-03_lava_potholes/SIM_LAVA_POTHOLES_V2_S026_audit.md`
- **Season / seri / seed:** S02 / lava_potholes / 26
- **Tema / narator:** morning-clear-volcano / chatterbox:m1
- **Durasi:** 46.77 s
- **Tokoh dan hasil:** Level 1: Siren (police) → rollback@obs2+broken; Level 2: Titan (bigrig) → stuck@obs0; Level 3 (juara): Nitro (f1) → win
- **Status:** APPROVED (approve 2026-10-03)
- **Antrian:** QUEUED 2026-10-15T15:00:00Z
- **YouTube:** belum diupload

## Ep. 43 — `SIM_RACE25D_V4_S044`

- **Judul YouTube:** Can Nitro Survive the Giant Hammer? 🏁 | Ep. 43 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E043_2026-10-04_race25d/SIM_RACE25D_V4_S044.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E043_2026-10-04_race25d/SIM_RACE25D_V4_S044.json` · audit: `renders/megawheel_arena/S02/E043_2026-10-04_race25d/SIM_RACE25D_V4_S044_audit.md`
- **Season / seri / seed:** S02 / race25d / 44
- **Tema / narator:** sunset-clear-mountains / chatterbox:m1
- **Durasi:** 34.56 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p4+oil; Level 2: Grizzly (monster2) → p2; Level 3 (juara): Nitro (f1) → p3+hammer; Level 4: Zippy (sports) → win+dodge_lava
- **Status:** APPROVED (approve 2026-10-05)
- **Antrian:** QUEUED 2026-10-13T19:00:00Z
- **YouTube:** belum diupload

## Ep. 44 — `SIM_SMASH25D_V5_S008`

- **Judul YouTube:** Titan, Rocky, Tilly or Zippy? Last Car Standing! 💥 | Ep. 44 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E044_2026-10-03_smash25d/SIM_SMASH25D_V5_S008.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E044_2026-10-03_smash25d/SIM_SMASH25D_V5_S008.json` · audit: `renders/megawheel_arena/S02/E044_2026-10-03_smash25d/SIM_SMASH25D_V5_S008_audit.md`
- **Season / seri / seed:** S02 / smash25d / 8
- **Tema / narator:** morning-snow-countryside / chatterbox:mw-announcers-m1f1
- **Durasi:** 50.17 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p3+ring; Level 2: Rocky (monster) → p2+ring; Level 3 (juara): Tilly (taxi) → win; Level 4: Zippy (sports) → p4+ring
- **Status:** APPROVED (approve 2026-10-03)
- **Antrian:** QUEUED 2026-10-14T23:00:00Z
- **YouTube:** belum diupload

## Ep. 45 — `SIM_BUMPS_V2_S021`

- **Judul YouTube:** Can Zippy the Sports Car Survive Giant Speed Bumps? 🚗💥 | Ep. 45 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E045_2026-10-03_bumps/SIM_BUMPS_V2_S021.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E045_2026-10-03_bumps/SIM_BUMPS_V2_S021.json` · audit: `renders/megawheel_arena/S02/E045_2026-10-03_bumps/SIM_BUMPS_V2_S021_audit.md`
- **Season / seri / seed:** S02 / bumps / 21
- **Tema / narator:** sunset-rain-beach / chatterbox:m1
- **Durasi:** 49.33 s
- **Tokoh dan hasil:** Level 1: Zippy (sports) → flip@obs2; Level 2: Buster (bus) → flip@obs1+broken; Level 3 (juara): Rocky (monster) → win
- **Status:** APPROVED (approve 2026-10-03)
- **Antrian:** QUEUED 2026-10-16T15:00:00Z
- **YouTube:** belum diupload

## Ep. 46 — `SIM_RACE25D_V4_S046`

- **Judul YouTube:** Can Nitro Survive the Meteors? 🏁 | Ep. 46 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E046_2026-10-04_race25d/SIM_RACE25D_V4_S046.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E046_2026-10-04_race25d/SIM_RACE25D_V4_S046.json` · audit: `renders/megawheel_arena/S02/E046_2026-10-04_race25d/SIM_RACE25D_V4_S046_audit.md`
- **Season / seri / seed:** S02 / race25d / 46
- **Tema / narator:** morning-clear-desert / chatterbox:m1
- **Durasi:** 35.67 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p3; Level 2: Grizzly (monster2) → p2+dodge_oil; Level 3 (juara): Nitro (f1) → win+meteor; Level 4: Siren (police) → p4+wall
- **Status:** APPROVED (approve 2026-10-05)
- **Antrian:** QUEUED 2026-10-14T19:00:00Z
- **YouTube:** belum diupload

## Ep. 47 — `SIM_SMASH25D_V5_S009`

- **Judul YouTube:** Can Tiny Tilly Beat a School Bus? 💥 | Ep. 47 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E047_2026-10-03_smash25d/SIM_SMASH25D_V5_S009.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E047_2026-10-03_smash25d/SIM_SMASH25D_V5_S009.json` · audit: `renders/megawheel_arena/S02/E047_2026-10-03_smash25d/SIM_SMASH25D_V5_S009_audit.md`
- **Season / seri / seed:** S02 / smash25d / 9
- **Tema / narator:** night-clear-desert / chatterbox:mw-announcers-m1f1
- **Durasi:** 48.4 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p3+ring; Level 2: Grizzly (monster2) → win; Level 3 (juara): Tilly (taxi) → p4+ring; Level 4: Siren (police) → p2+ring
- **Status:** APPROVED (approve 2026-10-03)
- **Antrian:** QUEUED 2026-10-15T23:00:00Z
- **YouTube:** belum diupload

## Ep. 48 — `SIM_POTHOLES_V2_S031`

- **Judul YouTube:** Police Car vs Giant Potholes! Can Siren Make It? 🚗💥 | Ep. 48 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E048_2026-10-04_potholes/SIM_POTHOLES_V2_S031.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E048_2026-10-04_potholes/SIM_POTHOLES_V2_S031.json` · audit: `renders/megawheel_arena/S02/E048_2026-10-04_potholes/SIM_POTHOLES_V2_S031_audit.md`
- **Season / seri / seed:** S02 / potholes / 31
- **Tema / narator:** morning-clear-desert / chatterbox:m1
- **Durasi:** 50.03 s
- **Tokoh dan hasil:** Level 1: Siren (police) → stuck@obs1+broken; Level 2: Hydro (firetruck) → pit@obs0+broken; Level 3 (juara): Zippy (sports) → win
- **Status:** APPROVED (approve 2026-10-04)
- **Antrian:** QUEUED 2026-10-17T15:00:00Z
- **YouTube:** belum diupload

## Ep. 49 — `SIM_RACE25D_V4_S043`

- **Judul YouTube:** Can Siren Survive the Giant Hammer? 🏁 | Ep. 49 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E049_2026-10-04_race25d/SIM_RACE25D_V4_S043.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E049_2026-10-04_race25d/SIM_RACE25D_V4_S043.json` · audit: `renders/megawheel_arena/S02/E049_2026-10-04_race25d/SIM_RACE25D_V4_S043_audit.md`
- **Season / seri / seed:** S02 / race25d / 43
- **Tema / narator:** night-rain-city / chatterbox:f1
- **Durasi:** 39.04 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p3+dodge_crusher; Level 2: Rocky (monster) → p2; Level 3 (juara): Tilly (taxi) → win+ramp; Level 4: Siren (police) → p4+hammer
- **Status:** APPROVED (approve 2026-10-04)
- **Antrian:** QUEUED 2026-10-15T19:00:00Z
- **YouTube:** belum diupload

## Ep. 50 — `SIM_POTHOLES_V2_S028`

- **Judul YouTube:** Race Car vs Giant Potholes! Can Nitro Make It? 🚗💥 | Ep. 50 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E050_2026-10-04_potholes/SIM_POTHOLES_V2_S028.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E050_2026-10-04_potholes/SIM_POTHOLES_V2_S028.json` · audit: `renders/megawheel_arena/S02/E050_2026-10-04_potholes/SIM_POTHOLES_V2_S028_audit.md`
- **Season / seri / seed:** S02 / potholes / 28
- **Tema / narator:** morning-clear-countryside / chatterbox:m1
- **Durasi:** 47.17 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → pit@obs0+broken; Level 2: Hydro (firetruck) → stuck@obs0; Level 3 (juara): Sprinkles (icecream) → win
- **Status:** APPROVED (approve 2026-10-04)
- **Antrian:** QUEUED 2026-10-18T15:00:00Z
- **YouTube:** belum diupload

## Ep. 51 — `SIM_POTHOLES_V2_S029`

- **Judul YouTube:** Will Siren the Police Car Survive Giant Potholes? 🚗💥 | Ep. 51 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E051_2026-10-04_potholes/SIM_POTHOLES_V2_S029.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E051_2026-10-04_potholes/SIM_POTHOLES_V2_S029.json` · audit: `renders/megawheel_arena/S02/E051_2026-10-04_potholes/SIM_POTHOLES_V2_S029_audit.md`
- **Season / seri / seed:** S02 / potholes / 29
- **Tema / narator:** sunset-clear-beach / chatterbox:f1
- **Durasi:** 50.0 s
- **Tokoh dan hasil:** Level 1: Siren (police) → flip@obs0; Level 2: Titan (bigrig) → stuck@obs0; Level 3 (juara): Nitro (f1) → win
- **Status:** APPROVED (approve 2026-10-04)
- **Antrian:** QUEUED 2026-10-19T15:00:00Z
- **YouTube:** belum diupload

## Ep. 1001 — `2026-10-02_story15_e01`

- **Judul YouTube:** Sprinkles' First Race 🍦🏁 | MegaWheel Arena Story Ep. 1
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/STORY_1001_2026-10-02_story15/2026-10-02_story15_e01.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/STORY_1001_2026-10-02_story15/2026-10-02_story15_e01.json` · audit: `renders/megawheel_arena/S01/STORY_1001_2026-10-02_story15/2026-10-02_story15_e01_audit.md`
- **Season / seri / seed:** S01 / story15 / 1
- **Tema / narator:**  / 
- **Durasi:** None s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → story15; Level 2: Zippy (sports) → ; Level 3 (juara): Buster (bus) → ; Level 4: Rocky (monster) → ; Level 5: Siren (police) → ; Level 6: Tilly (taxi) → ; Level 7: Nitro (f1) → 
- **Status:** UPLOADED_SCHEDULED 2026-10-04T17:00:00Z (approve 2026-10-02)
- **Antrian:** SCHEDULED 2026-10-04T17:00:00Z
- **YouTube:** https://www.youtube.com/shorts/gAVCxOicZyM

## Ep. 1002 — `2026-10-07_story15_e02`

- **Judul YouTube:** Who Is Kraggor? 🦖🍦 | MegaWheel Arena Story Ep. 2
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/STORY_1002_2026-10-07_story15/2026-10-07_story15_e02.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/STORY_1002_2026-10-07_story15/2026-10-07_story15_e02.json` · audit: `renders/megawheel_arena/S01/STORY_1002_2026-10-07_story15/2026-10-07_story15_e02_audit.md`
- **Season / seri / seed:** S01 / story15 / 2
- **Tema / narator:**  / 
- **Durasi:** None s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → story15; Level 2: Zippy (sports) → ; Level 3 (juara): Buster (bus) → ; Level 4: Rocky (monster) → ; Level 5: Siren (police) → ; Level 6: Tilly (taxi) → ; Level 7: Nitro (f1) → 
- **Status:** APPROVED (approve 2026-10-07)
- **Antrian:** QUEUED 2026-10-11T17:00:00Z
- **YouTube:** belum diupload

## Ep. 1501 — `2026-10-02_story15_trailer_e01`

- **Judul YouTube:** Sprinkles' First Race 🍦 Full Episode This Sunday!
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/STORY_1501_2026-10-02_story15_trailer/2026-10-02_story15_trailer_e01.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/STORY_1501_2026-10-02_story15_trailer/2026-10-02_story15_trailer_e01.json` · audit: `renders/megawheel_arena/S01/STORY_1501_2026-10-02_story15_trailer/2026-10-02_story15_trailer_e01_audit.md`
- **Season / seri / seed:** S01 / story15_trailer / 1
- **Tema / narator:**  / 
- **Durasi:** None s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → story15_trailer; Level 2: Zippy (sports) → ; Level 3 (juara): Buster (bus) → ; Level 4: Rocky (monster) → ; Level 5: Siren (police) → ; Level 6: Tilly (taxi) → ; Level 7: Nitro (f1) → 
- **Status:** UPLOADED_SCHEDULED 2026-10-03T21:00:00Z (approve 2026-10-02)
- **Antrian:** SCHEDULED 2026-10-03T21:00:00Z
- **YouTube:** https://www.youtube.com/shorts/BB8Lr9LwL9g

## Ep. 1502 — `2026-10-07_story15_trailer_e02`

- **Judul YouTube:** Who Is Kraggor? 🦖 Full Episode This Sunday!
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/STORY_1502_2026-10-07_story15_trailer/2026-10-07_story15_trailer_e02.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/STORY_1502_2026-10-07_story15_trailer/2026-10-07_story15_trailer_e02.json` · audit: `renders/megawheel_arena/S01/STORY_1502_2026-10-07_story15_trailer/2026-10-07_story15_trailer_e02_audit.md`
- **Season / seri / seed:** S01 / story15_trailer / 2
- **Tema / narator:**  / 
- **Durasi:** None s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → story15_trailer; Level 2: Zippy (sports) → ; Level 3 (juara): Buster (bus) → ; Level 4: Rocky (monster) → ; Level 5: Siren (police) → ; Level 6: Tilly (taxi) → ; Level 7: Nitro (f1) → 
- **Status:** APPROVED (approve 2026-10-07)
- **Antrian:** UPLOADING 2026-10-07T12:00:00Z
- **YouTube:** belum diupload
