# EPISODES_INDEX — identitas pasti setiap episode MegaWheel Arena

> Dibuat otomatis oleh `generators/publishing/episodes.py` (2026-11-05 05:01) setiap approve/reject/upload. **Jangan diedit manual.** Sumber data: `PRODUCTION_REGISTRY.json`.

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
| 21 | `SIM_POTHOLES_V2_S008` | potholes | UPLOADED_SCHEDULED 2026-10-10T15:00:00Z | Sat 2026-10-10 11:00 | https://www.youtube.com/shorts/ggvN5p10cfQ |
| 22 | `SIM_SMASH25D_V4_S001` | smash25d | UPLOADED_SCHEDULED 2026-10-02T23:00:00Z | Fri 2026-10-02 19:00 | https://www.youtube.com/shorts/Q-7067tL0A8 |
| 23 | `SIM_SMASH25D_V4_S003` | smash25d | UPLOADED_SCHEDULED 2026-10-03T23:00:00Z | Sat 2026-10-03 19:00 | https://www.youtube.com/shorts/ZjUnuZvelKY |
| 24 | `SIM_SMASH25D_V4_S007` | smash25d | UPLOADED_SCHEDULED 2026-10-04T23:00:00Z | Sun 2026-10-04 19:00 | https://www.youtube.com/shorts/RCBE3lgA2uo |
| 25 | `SIM_SMASH25D_V4_S008` | smash25d | UPLOADED_SCHEDULED 2026-10-05T23:00:00Z | Mon 2026-10-05 19:00 | https://www.youtube.com/shorts/5ljCNw1Hnlg |
| 26 | `SIM_SMASH25D_V4_S011` | smash25d | UPLOADED_SCHEDULED 2026-10-06T23:00:00Z | Tue 2026-10-06 19:00 | https://www.youtube.com/shorts/eQQzWYXAda8 |
| 27 | `SIM_SMASH25D_V4_S012` | smash25d | UPLOADED_SCHEDULED 2026-10-07T23:00:00Z | Wed 2026-10-07 19:00 | https://www.youtube.com/shorts/pjx_weAS40w |
| 28 | `SIM_SMASH25D_V4_S014` | smash25d | UPLOADED_SCHEDULED 2026-10-08T23:00:00Z | Thu 2026-10-08 19:00 | https://www.youtube.com/shorts/ZXEi9fG7RZA |
| 29 | `SIM_SMASH25D_V4_S015` | smash25d | UPLOADED_SCHEDULED 2026-10-09T23:00:00Z | Fri 2026-10-09 19:00 | https://www.youtube.com/shorts/AbvICeQ1lPE |
| 30 | `SIM_POTHOLES_V2_S021` | potholes | UPLOADED_SCHEDULED 2026-10-11T15:00:00Z | Sun 2026-10-11 11:00 | https://www.youtube.com/shorts/S1t8T9lwAMs |
| 31 | `SIM_RACE25D_V4_S036` | race25d | UPLOADED_SCHEDULED 2026-10-09T19:00:00Z | Fri 2026-10-09 15:00 | https://www.youtube.com/shorts/vZFKVw21xA8 |
| 32 | `SIM_SMASH25D_V5_S002` | smash25d | UPLOADED_SCHEDULED 2026-10-10T23:00:00Z | Sat 2026-10-10 19:00 | https://www.youtube.com/shorts/k9fMTUKrdeA |
| 33 | `SIM_POTHOLES_V2_S022` | potholes | UPLOADED_SCHEDULED 2026-10-12T15:00:00Z | Mon 2026-10-12 11:00 | https://www.youtube.com/shorts/hBNWKl7lX6I |
| 34 | `SIM_RACE25D_V4_S045` | race25d | UPLOADED_SCHEDULED 2026-10-10T19:00:00Z | Sat 2026-10-10 15:00 | https://www.youtube.com/shorts/nYMwvHZvwmY |
| 35 | `SIM_SMASH25D_V5_S003` | smash25d | UPLOADED_SCHEDULED 2026-10-11T23:00:00Z | Sun 2026-10-11 19:00 | https://www.youtube.com/shorts/etUL6wxoccA |
| 36 | `SIM_LAVA_POTHOLES_V2_S025` | lava_potholes | UPLOADED_SCHEDULED 2026-10-13T15:00:00Z | Tue 2026-10-13 11:00 | https://www.youtube.com/shorts/8XC7Jkb0aZA |
| 37 | `SIM_RACE25D_V4_S040` | race25d | UPLOADED_SCHEDULED 2026-10-11T19:00:00Z | Sun 2026-10-11 15:00 | https://www.youtube.com/shorts/1aa8NVWoMhQ |
| 38 | `SIM_SMASH25D_V5_S004` | smash25d | UPLOADED_SCHEDULED 2026-10-12T23:00:00Z | Mon 2026-10-12 19:00 | https://www.youtube.com/shorts/1g38LQv-7k8 |
| 39 | `SIM_POTHOLES_V2_S027` | potholes | UPLOADED_SCHEDULED 2026-10-14T15:00:00Z | Wed 2026-10-14 11:00 | https://www.youtube.com/shorts/_ep2xhmCcMg |
| 40 | `SIM_RACE25D_V4_S037` | race25d | UPLOADED_SCHEDULED 2026-10-12T19:00:00Z | Mon 2026-10-12 15:00 | https://www.youtube.com/shorts/Gp7yvNydnKs |
| 41 | `SIM_SMASH25D_V5_S005` | smash25d | UPLOADED_SCHEDULED 2026-10-13T23:00:00Z | Tue 2026-10-13 19:00 | https://www.youtube.com/shorts/2ekvyKZl7v8 |
| 42 | `SIM_LAVA_POTHOLES_V2_S026` | lava_potholes | UPLOADED_SCHEDULED 2026-10-15T15:00:00Z | Thu 2026-10-15 11:00 | https://www.youtube.com/shorts/ivasm__dTxM |
| 43 | `SIM_RACE25D_V4_S044` | race25d | UPLOADED_SCHEDULED 2026-10-13T19:00:00Z | Tue 2026-10-13 15:00 | https://www.youtube.com/shorts/MsJCeAgnOrY |
| 44 | `SIM_SMASH25D_V5_S008` | smash25d | UPLOADED_SCHEDULED 2026-10-14T23:00:00Z | Wed 2026-10-14 19:00 | https://www.youtube.com/shorts/qNLPmagWH3M |
| 45 | `SIM_BUMPS_V2_S021` | bumps | UPLOADED_SCHEDULED 2026-10-16T15:00:00Z | Fri 2026-10-16 11:00 | https://www.youtube.com/shorts/Sh2WfMcLj-M |
| 46 | `SIM_RACE25D_V4_S046` | race25d | UPLOADED_SCHEDULED 2026-10-14T19:00:00Z | Wed 2026-10-14 15:00 | https://www.youtube.com/shorts/BJhlWYkiHF8 |
| 47 | `SIM_SMASH25D_V5_S009` | smash25d | UPLOADED_SCHEDULED 2026-10-15T23:00:00Z | Thu 2026-10-15 19:00 | https://www.youtube.com/shorts/eWqvYeCTWqk |
| 48 | `SIM_POTHOLES_V2_S031` | potholes | UPLOADED_SCHEDULED 2026-10-17T15:00:00Z | Sat 2026-10-17 11:00 | https://www.youtube.com/shorts/c8Y6AecAUCI |
| 49 | `SIM_RACE25D_V4_S043` | race25d | UPLOADED_SCHEDULED 2026-10-15T19:00:00Z | Thu 2026-10-15 15:00 | https://www.youtube.com/shorts/6HkCyVZqXrc |
| 50 | `SIM_POTHOLES_V2_S028` | potholes | UPLOADED_SCHEDULED 2026-10-18T15:00:00Z | Sun 2026-10-18 11:00 | https://www.youtube.com/shorts/8_uVESE2cr4 |
| 51 | `SIM_POTHOLES_V2_S029` | potholes | UPLOADED_SCHEDULED 2026-10-19T15:00:00Z | Mon 2026-10-19 11:00 | https://www.youtube.com/shorts/JYouVAHqUeA |
| 52 | `SIM_DUNGEON_V2_S015` | dungeon | UPLOADED_SCHEDULED 2026-10-20T15:00:00Z | Tue 2026-10-20 11:00 | https://www.youtube.com/shorts/DERf3rVbKd0 |
| 53 | `SIM_RACE25D_V4_S048` | race25d | UPLOADED_SCHEDULED 2026-10-16T19:00:00Z | Fri 2026-10-16 15:00 | https://www.youtube.com/shorts/jbr_oreCvfY |
| 54 | `SIM_RACE25D_V4_S051` | race25d | UPLOADED_SCHEDULED 2026-10-17T19:00:00Z | Sat 2026-10-17 15:00 | https://www.youtube.com/shorts/puxQcUZoOdc |
| 55 | `SIM_RACE25D_V4_S055` | race25d | UPLOADED_SCHEDULED 2026-10-18T19:00:00Z | Sun 2026-10-18 15:00 | https://www.youtube.com/shorts/NaQ5MVI0etc |
| 56 | `SIM_RACE25D_V4_S056` | race25d | UPLOADED_SCHEDULED 2026-10-19T19:00:00Z | Mon 2026-10-19 15:00 | https://www.youtube.com/shorts/Wls3wOxIct0 |
| 57 | `SIM_SMASH25D_V5_S016` | smash25d | UPLOADED_SCHEDULED 2026-10-16T23:00:00Z | Fri 2026-10-16 19:00 | https://www.youtube.com/shorts/6eLjmpy02NM |
| 58 | `SIM_SMASH25D_V5_S017` | smash25d | UPLOADED_SCHEDULED 2026-10-17T23:00:00Z | Sat 2026-10-17 19:00 | https://www.youtube.com/shorts/0UhR4k8z9mk |
| 59 | `SIM_SMASH25D_V5_S018` | smash25d | UPLOADED_SCHEDULED 2026-10-18T23:00:00Z | Sun 2026-10-18 19:00 | https://www.youtube.com/shorts/2mJ7FCqvYTg |
| 60 | `SIM_RACE25D_V4_S047` | race25d | UPLOADED_SCHEDULED 2026-10-20T19:00:00Z | Tue 2026-10-20 15:00 | https://www.youtube.com/shorts/YsTdVDb4fWc |
| 61 | `SIM_RACE25D_V4_S057` | race25d | UPLOADED_SCHEDULED 2026-10-21T19:00:00Z | Wed 2026-10-21 15:00 | https://www.youtube.com/shorts/qs4m4wnQx2s |
| 62 | `SIM_SMASH25D_V5_S020` | smash25d | UPLOADED_SCHEDULED 2026-10-19T23:00:00Z | Mon 2026-10-19 19:00 | https://www.youtube.com/shorts/lym-XWogLPk |
| 63 | `SIM_SMASH25D_V5_S021` | smash25d | UPLOADED_SCHEDULED 2026-10-20T23:00:00Z | Tue 2026-10-20 19:00 | https://www.youtube.com/shorts/vZAkrIzQ7zQ |
| 64 | `SIM_PENDULUM_V2_S002` | pendulum | UPLOADED_SCHEDULED 2026-10-21T15:00:00Z | Wed 2026-10-21 11:00 | https://www.youtube.com/shorts/YTTl_1sokjE |
| 65 | `SIM_DOMINO_V2_S001` | domino | UPLOADED_SCHEDULED 2026-10-22T15:00:00Z | Thu 2026-10-22 11:00 | https://www.youtube.com/shorts/mVQhUTvk9ZI |
| 66 | `SIM_PINBALL_V2_S004` | pinball | UPLOADED_SCHEDULED 2026-10-23T15:00:00Z | Fri 2026-10-23 11:00 | https://www.youtube.com/shorts/qoeUhMg2-7Q |
| 67 | `SIM_RACE25D_V4_S058` | race25d | UPLOADED_SCHEDULED 2026-10-22T19:00:00Z | Thu 2026-10-22 15:00 | https://www.youtube.com/shorts/Guo_ikHKcMk |
| 68 | `SIM_RACE25D_V4_S059` | race25d | UPLOADED_SCHEDULED 2026-10-23T19:00:00Z | Fri 2026-10-23 15:00 | https://www.youtube.com/shorts/_BkZRCpEhPg |
| 69 | `SIM_RACE25D_V4_S060` | race25d | UPLOADED_SCHEDULED 2026-10-24T19:00:00Z | Sat 2026-10-24 15:00 | https://www.youtube.com/shorts/KIZF_hjOXJY |
| 70 | `SIM_SMASH25D_V5_S022` | smash25d | UPLOADED_SCHEDULED 2026-10-21T23:00:00Z | Wed 2026-10-21 19:00 | https://www.youtube.com/shorts/YOg4cwmPHdw |
| 71 | `SIM_SMASH25D_V5_S023` | smash25d | UPLOADED_SCHEDULED 2026-10-22T23:00:00Z | Thu 2026-10-22 19:00 | https://www.youtube.com/shorts/diUdJsm2_SM |
| 72 | `SIM_SMASH25D_V5_S024` | smash25d | UPLOADED_SCHEDULED 2026-10-23T23:00:00Z | Fri 2026-10-23 19:00 | https://www.youtube.com/shorts/ygW5VWZpx1c |
| 73 | `SIM_GAUNTLET_V2_S004` | gauntlet | UPLOADED_SCHEDULED 2026-10-24T15:00:00Z | Sat 2026-10-24 11:00 | https://www.youtube.com/shorts/VFZjvEaUpsc |
| 74 | `SIM_GAUNTLET_V2_S005` | gauntlet | UPLOADED_SCHEDULED 2026-10-25T15:00:00Z | Sun 2026-10-25 11:00 | https://www.youtube.com/shorts/xm-xShnbV_g |
| 75 | `SIM_LAVA_POTHOLES_V2_S028` | lava_potholes | UPLOADED_SCHEDULED 2026-10-26T15:00:00Z | Mon 2026-10-26 11:00 | https://www.youtube.com/shorts/lHByBBaLVXo |
| 76 | `SIM_RACE25D_V4_S061` | race25d | UPLOADED_SCHEDULED 2026-10-25T19:00:00Z | Sun 2026-10-25 15:00 | https://www.youtube.com/shorts/dpIG3zz0nQs |
| 77 | `SIM_RACE25D_V4_S063` | race25d | UPLOADED_SCHEDULED 2026-10-26T19:00:00Z | Mon 2026-10-26 15:00 | https://www.youtube.com/shorts/wJRlHjwcgWg |
| 78 | `SIM_SMASH25D_V5_S025` | smash25d | UPLOADED_SCHEDULED 2026-10-24T23:00:00Z | Sat 2026-10-24 19:00 | https://www.youtube.com/shorts/2FRVVI2q_vM |
| 79 | `SIM_SMASH25D_V5_S028` | smash25d | UPLOADED_SCHEDULED 2026-10-25T23:00:00Z | Sun 2026-10-25 19:00 | https://www.youtube.com/shorts/n7E87OZBYe8 |
| 80 | `SIM_SMASH25D_V5_S029` | smash25d | UPLOADED_SCHEDULED 2026-10-26T23:00:00Z | Mon 2026-10-26 19:00 | https://www.youtube.com/shorts/trI9Q77SAxU |
| 81 | `SIM_GAUNTLET_V2_S007` | gauntlet | UPLOADED_SCHEDULED 2026-10-27T15:00:00Z | Tue 2026-10-27 11:00 | https://www.youtube.com/shorts/Mb76nmh0YyM |
| 82 | `SIM_LAVA_POTHOLES_V2_S029` | lava_potholes | UPLOADED_SCHEDULED 2026-10-28T15:00:00Z | Wed 2026-10-28 11:00 | https://www.youtube.com/shorts/KZNCFqh33go |
| 83 | `SIM_PENDULUM_V2_S004` | pendulum | UPLOADED_SCHEDULED 2026-10-29T15:00:00Z | Thu 2026-10-29 11:00 | https://www.youtube.com/shorts/XTuIEMNarGE |
| 84 | `SIM_RACE25D_V4_S066` | race25d | UPLOADED_SCHEDULED 2026-10-27T19:00:00Z | Tue 2026-10-27 15:00 | https://www.youtube.com/shorts/4xdJO93mknM |
| 85 | `SIM_RACE25D_V4_S067` | race25d | UPLOADED_SCHEDULED 2026-10-28T19:00:00Z | Wed 2026-10-28 15:00 | https://www.youtube.com/shorts/cwG86oKxxwQ |
| 86 | `SIM_RACE25D_V4_S068` | race25d | UPLOADED_SCHEDULED 2026-10-29T19:00:00Z | Thu 2026-10-29 15:00 | https://www.youtube.com/shorts/PsnDA9kn7ig |
| 87 | `SIM_SMASH25D_V5_S030` | smash25d | UPLOADED_SCHEDULED 2026-10-27T23:00:00Z | Tue 2026-10-27 19:00 | https://www.youtube.com/shorts/i6zipDevoTA |
| 88 | `SIM_SMASH25D_V5_S032` | smash25d | UPLOADED_SCHEDULED 2026-10-28T23:00:00Z | Wed 2026-10-28 19:00 | https://www.youtube.com/shorts/8q9Bbk-An5U |
| 89 | `SIM_SMASH25D_V5_S034` | smash25d | UPLOADED_SCHEDULED 2026-10-29T23:00:00Z | Thu 2026-10-29 19:00 | https://www.youtube.com/shorts/jiixposH0eo |
| 90 | `SIM_POTHOLES_V2_S033` | potholes | UPLOADED_SCHEDULED 2026-10-30T15:00:00Z | Fri 2026-10-30 11:00 | https://www.youtube.com/shorts/LA5GZDAqS1U |
| 91 | `SIM_BUMPS_V2_S022` | bumps | UPLOADED_SCHEDULED 2026-10-31T15:00:00Z | Sat 2026-10-31 11:00 | https://www.youtube.com/shorts/yFWEjAOlIB4 |
| 92 | `SIM_RACE25D_V4_S069` | race25d | UPLOADED_SCHEDULED 2026-10-30T19:00:00Z | Fri 2026-10-30 15:00 | https://www.youtube.com/shorts/dfyq1sts3ZI |
| 93 | `SIM_RACE25D_V4_S070` | race25d | UPLOADED_SCHEDULED 2026-10-31T19:00:00Z | Sat 2026-10-31 15:00 | https://www.youtube.com/shorts/nuWeVdaiJe8 |
| 94 | `SIM_SMASH25D_V5_S036` | smash25d | UPLOADED_SCHEDULED 2026-10-30T23:00:00Z | Fri 2026-10-30 19:00 | https://www.youtube.com/shorts/ec1zc5iboQE |
| 95 | `SIM_SMASH25D_V5_S037` | smash25d | UPLOADED_SCHEDULED 2026-10-31T23:00:00Z | Sat 2026-10-31 19:00 | https://www.youtube.com/shorts/S6FoCd1kejM |
| 96 | `SIM_DOMINO_V2_S003` | domino | UPLOADED_SCHEDULED 2026-11-01T16:00:00Z | Sun 2026-11-01 11:00 | https://www.youtube.com/shorts/uHkmWJYEZvA |
| 97 | `SIM_PINBALL_V2_S006` | pinball | UPLOADED_SCHEDULED 2026-11-02T16:00:00Z | Mon 2026-11-02 11:00 | https://www.youtube.com/shorts/SaMAPLv7ErM |
| 98 | `SIM_DUNGEON_V2_S026` | dungeon | UPLOADED_SCHEDULED 2026-11-03T16:00:00Z | Tue 2026-11-03 11:00 | https://www.youtube.com/shorts/MsN81LV_nP4 |
| 99 | `SIM_DUNGEON_V2_S029` | dungeon | UPLOADED_SCHEDULED 2026-11-10T16:00:00Z | Tue 2026-11-10 11:00 | https://www.youtube.com/shorts/-AXUqUCBwBk |
| 100 | `SIM_DUNGEON_V2_S031` | dungeon | UPLOADED_SCHEDULED 2026-11-17T16:00:00Z | Tue 2026-11-17 11:00 | https://www.youtube.com/shorts/30CLnhlfxQI |
| 101 | `SIM_DUNGEON_V2_S032` | dungeon | UPLOADED_SCHEDULED 2026-11-24T16:00:00Z | Tue 2026-11-24 11:00 | https://www.youtube.com/shorts/zxPurjmlF6w |
| 102 | `SIM_DUNGEON_V2_S038` | dungeon | UPLOADED_SCHEDULED 2026-12-01T16:00:00Z | Tue 2026-12-01 11:00 | https://www.youtube.com/shorts/U3oGHMwFI0I |
| 103 | `SIM_SPLASH_V2_S013` | splash | UPLOADED_SCHEDULED 2026-11-04T16:00:00Z | Wed 2026-11-04 11:00 | https://www.youtube.com/shorts/qLmoNh8nyEU |
| 104 | `MW_SPLASH_3D_S021` | splash | UPLOADED_SCHEDULED 2026-11-05T16:00:00Z | Thu 2026-11-05 11:00 | https://www.youtube.com/shorts/0qVPxSCaBUI |
| 105 | `MW_RACE_3D_S071` | race25d | UPLOADED_SCHEDULED 2026-11-03T20:00:00Z | Tue 2026-11-03 15:00 | https://www.youtube.com/shorts/CmFaZq12F6c |
| 106 | `MW_RACE_3D_S072` | race25d | UPLOADED_SCHEDULED 2026-11-04T20:00:00Z | Wed 2026-11-04 15:00 | https://www.youtube.com/shorts/yEIw_K4Fswo |
| 107 | `MW_RACE_3D_S217` | race25d | UPLOADED_SCHEDULED 2026-11-05T20:00:00Z | Thu 2026-11-05 15:00 | https://www.youtube.com/shorts/GWJc_r7ZF-Q |
| 108 | `MW_RACE_3D_S088` | race25d | UPLOADED_SCHEDULED 2026-11-06T20:00:00Z | Fri 2026-11-06 15:00 | https://www.youtube.com/shorts/MTlsgscsj3Q |
| 109 | `MW_RACE_3D_S108` | race25d | APPROVED | Sat 2026-11-07 15:00 |  |
| 110 | `MW_SMASH_3D_S062_R2` | smash25d | UPLOADED_SCHEDULED 2026-11-05T00:00:00Z | Wed 2026-11-04 19:00 | https://www.youtube.com/shorts/UTVc7gPmdkI |
| 111 | `MW_SMASH_3D_S043_R2` | smash25d | UPLOADED_SCHEDULED 2026-11-06T00:00:00Z | Thu 2026-11-05 19:00 | https://www.youtube.com/shorts/_VvjsGfjf0s |
| 112 | `MW_SMASH_3D_S039_R2` | smash25d | UPLOADED_SCHEDULED 2026-11-07T00:00:00Z | Fri 2026-11-06 19:00 | https://www.youtube.com/shorts/TK2avDRy0aM |
| 113 | `MW_BUMPS_3D_S040` | bumps | UPLOADED_SCHEDULED 2026-11-06T16:00:00Z | Fri 2026-11-06 11:00 | https://www.youtube.com/shorts/M-eAqay4M4Q |
| 114 | `MW_POTHOLES_3D_S041` | potholes | APPROVED | Sat 2026-11-07 11:00 |  |
| 115 | `MW_LAVA_3D_S043` | lava | APPROVED | Sun 2026-11-08 11:00 |  |
| 116 | `MW_POTHOLES_3D_S124` | potholes | APPROVED | Mon 2026-11-09 11:00 |  |
| 1001 | `2026-10-02_story15_e01` | story15 | UPLOADED_SCHEDULED 2026-10-04T17:00:00Z | Sun 2026-10-04 13:00 | https://www.youtube.com/shorts/gAVCxOicZyM |
| 1002 | `2026-10-07_story15_e02` | story15 | UPLOADED_SCHEDULED 2026-10-11T17:00:00Z | Sun 2026-10-11 13:00 | https://www.youtube.com/shorts/SdByNtxACP4 |
| 1003 | `2026-10-23_story15_e03` | story15 | UPLOADED_SCHEDULED 2026-10-25T17:00:00Z | Sun 2026-10-25 13:00 | https://www.youtube.com/shorts/3wtRIEEN4WY |
| 1501 | `2026-10-02_story15_trailer_e01` | story15_trailer | UPLOADED_SCHEDULED 2026-10-03T21:00:00Z | Sat 2026-10-03 17:00 | https://www.youtube.com/shorts/BB8Lr9LwL9g |
| 1502 | `2026-10-07_story15_trailer_e02` | story15_trailer | UPLOADED_SCHEDULED 2026-10-07T12:00:00Z | Wed 2026-10-07 08:00 | https://www.youtube.com/shorts/v4oErNoDW64 |

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
- **Status:** UPLOADED_SCHEDULED 2026-10-10T15:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-10T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/ggvN5p10cfQ

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
- **Status:** UPLOADED_SCHEDULED 2026-10-09T23:00:00Z (approve 2026-10-01)
- **Antrian:** SCHEDULED 2026-10-09T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/AbvICeQ1lPE

## Ep. 30 — `SIM_POTHOLES_V2_S021`

- **Judul YouTube:** Can Siren the Police Car Survive Giant Potholes? 🚗💥 | Ep. 30 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/E030_2026-10-03_potholes/SIM_POTHOLES_V2_S021.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/E030_2026-10-03_potholes/SIM_POTHOLES_V2_S021.json` · audit: `renders/megawheel_arena/S01/E030_2026-10-03_potholes/SIM_POTHOLES_V2_S021_audit.md`
- **Season / seri / seed:** S01 / potholes / 21
- **Tema / narator:** night-rain-city / chatterbox:m1
- **Durasi:** 51.07 s
- **Tokoh dan hasil:** Level 1: Siren (police) → rollback@obs2+broken; Level 2: Titan (bigrig) → stuck@obs1; Level 3 (juara): Zippy (sports) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-11T15:00:00Z (approve 2026-10-03)
- **Antrian:** SCHEDULED 2026-10-11T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/S1t8T9lwAMs

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
- **Status:** UPLOADED_SCHEDULED 2026-10-10T23:00:00Z (approve 2026-10-03)
- **Antrian:** SCHEDULED 2026-10-10T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/k9fMTUKrdeA

## Ep. 33 — `SIM_POTHOLES_V2_S022`

- **Judul YouTube:** Taxi vs Giant Potholes! Can Tilly Make It? 🚗💥 | Ep. 33 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E033_2026-10-03_potholes/SIM_POTHOLES_V2_S022.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E033_2026-10-03_potholes/SIM_POTHOLES_V2_S022.json` · audit: `renders/megawheel_arena/S02/E033_2026-10-03_potholes/SIM_POTHOLES_V2_S022_audit.md`
- **Season / seri / seed:** S02 / potholes / 22
- **Tema / narator:** night-clear-mountains / en-US-EmmaMultilingualNeural
- **Durasi:** 47.97 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → rollback@obs2+broken; Level 2: Sprinkles (icecream) → stuck@obs0; Level 3 (juara): Hydro (firetruck) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-12T15:00:00Z (approve 2026-10-03)
- **Antrian:** SCHEDULED 2026-10-12T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/hBNWKl7lX6I

## Ep. 34 — `SIM_RACE25D_V4_S045`

- **Judul YouTube:** Nitro vs the Giant Hammer! Who Wins the Race? 🏁 | Ep. 34 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E034_2026-10-04_race25d/SIM_RACE25D_V4_S045.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E034_2026-10-04_race25d/SIM_RACE25D_V4_S045.json` · audit: `renders/megawheel_arena/S02/E034_2026-10-04_race25d/SIM_RACE25D_V4_S045_audit.md`
- **Season / seri / seed:** S02 / race25d / 45
- **Tema / narator:** noon-clear-beach / chatterbox:f1
- **Durasi:** 37.11 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p2+dodge_oil; Level 2: Grizzly (monster2) → win; Level 3 (juara): Nitro (f1) → p3+hammer; Level 4: Zippy (sports) → p4+dragon_ice
- **Status:** UPLOADED_SCHEDULED 2026-10-10T19:00:00Z (approve 2026-10-05)
- **Antrian:** SCHEDULED 2026-10-10T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/nYMwvHZvwmY

## Ep. 35 — `SIM_SMASH25D_V5_S003`

- **Judul YouTube:** Can Tiny Nitro Beat a Big Rig? 💥 | Ep. 35 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E035_2026-10-03_smash25d/SIM_SMASH25D_V5_S003.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E035_2026-10-03_smash25d/SIM_SMASH25D_V5_S003.json` · audit: `renders/megawheel_arena/S02/E035_2026-10-03_smash25d/SIM_SMASH25D_V5_S003_audit.md`
- **Season / seri / seed:** S02 / smash25d / 3
- **Tema / narator:** sunset-clear-city / chatterbox:mw-announcers-m1f1
- **Durasi:** 53.23 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → win; Level 2: Grizzly (monster2) → p2+wreck; Level 3 (juara): Nitro (f1) → p4+ring; Level 4: Siren (police) → p3+wreck
- **Status:** UPLOADED_SCHEDULED 2026-10-11T23:00:00Z (approve 2026-10-03)
- **Antrian:** SCHEDULED 2026-10-11T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/etUL6wxoccA

## Ep. 36 — `SIM_LAVA_POTHOLES_V2_S025`

- **Judul YouTube:** Race Car vs Giant Lava Potholes! Can Nitro Make It? 🌋🔥 | Ep. 36 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E036_2026-10-03_lava_potholes/SIM_LAVA_POTHOLES_V2_S025.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E036_2026-10-03_lava_potholes/SIM_LAVA_POTHOLES_V2_S025.json` · audit: `renders/megawheel_arena/S02/E036_2026-10-03_lava_potholes/SIM_LAVA_POTHOLES_V2_S025_audit.md`
- **Season / seri / seed:** S02 / lava_potholes / 25
- **Tema / narator:** noon-clear-volcano / chatterbox:f1
- **Durasi:** 50.77 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → pit@obs2+broken; Level 2: Sprinkles (icecream) → stuck@obs0; Level 3 (juara): Tilly (taxi) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-13T15:00:00Z (approve 2026-10-03)
- **Antrian:** SCHEDULED 2026-10-13T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/8XC7Jkb0aZA

## Ep. 37 — `SIM_RACE25D_V4_S040`

- **Judul YouTube:** Can Tilly Survive the Meteors? 🏁 | Ep. 37 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E037_2026-10-04_race25d/SIM_RACE25D_V4_S040.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E037_2026-10-04_race25d/SIM_RACE25D_V4_S040.json` · audit: `renders/megawheel_arena/S02/E037_2026-10-04_race25d/SIM_RACE25D_V4_S040_audit.md`
- **Season / seri / seed:** S02 / race25d / 40
- **Tema / narator:** noon-clear-countryside / chatterbox:f1
- **Durasi:** 35.25 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p4+laser; Level 2: Rocky (monster) → p2+dodge_oil; Level 3 (juara): Tilly (taxi) → p3+meteor; Level 4: Zippy (sports) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-11T19:00:00Z (approve 2026-10-04)
- **Antrian:** SCHEDULED 2026-10-11T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/1aa8NVWoMhQ

## Ep. 38 — `SIM_SMASH25D_V5_S004`

- **Judul YouTube:** Fire Truck vs Monster Truck vs Taxi vs Race Car! Who Survives? 💥 | Ep. 38 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E038_2026-10-03_smash25d/SIM_SMASH25D_V5_S004.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E038_2026-10-03_smash25d/SIM_SMASH25D_V5_S004.json` · audit: `renders/megawheel_arena/S02/E038_2026-10-03_smash25d/SIM_SMASH25D_V5_S004_audit.md`
- **Season / seri / seed:** S02 / smash25d / 4
- **Tema / narator:** night-snow-mountains / chatterbox:mw-announcers-m1f1
- **Durasi:** 51.61 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → win; Level 2: Grizzly (monster2) → p4+ring; Level 3 (juara): Tilly (taxi) → p3+wreck; Level 4: Nitro (f1) → p2+wreck
- **Status:** UPLOADED_SCHEDULED 2026-10-12T23:00:00Z (approve 2026-10-03)
- **Antrian:** SCHEDULED 2026-10-12T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/1g38LQv-7k8

## Ep. 39 — `SIM_POTHOLES_V2_S027`

- **Judul YouTube:** Can Nitro the Race Car Survive Giant Potholes? 🚗💥 | Ep. 39 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E039_2026-10-03_potholes/SIM_POTHOLES_V2_S027.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E039_2026-10-03_potholes/SIM_POTHOLES_V2_S027.json` · audit: `renders/megawheel_arena/S02/E039_2026-10-03_potholes/SIM_POTHOLES_V2_S027_audit.md`
- **Season / seri / seed:** S02 / potholes / 27
- **Tema / narator:** sunset-clear-beach / chatterbox:f1
- **Durasi:** 48.7 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → pit@obs2+broken; Level 2: Hydro (firetruck) → stuck@obs0; Level 3 (juara): Buster (bus) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-14T15:00:00Z (approve 2026-10-03)
- **Antrian:** SCHEDULED 2026-10-14T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/_ep2xhmCcMg

## Ep. 40 — `SIM_RACE25D_V4_S037`

- **Judul YouTube:** Can Siren Survive the Oil Slick? 🏁 | Ep. 40 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E040_2026-10-04_race25d/SIM_RACE25D_V4_S037.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E040_2026-10-04_race25d/SIM_RACE25D_V4_S037.json` · audit: `renders/megawheel_arena/S02/E040_2026-10-04_race25d/SIM_RACE25D_V4_S037_audit.md`
- **Season / seri / seed:** S02 / race25d / 37
- **Tema / narator:** morning-snow-city / chatterbox:f1
- **Durasi:** 35.79 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p4+dragon_fire; Level 2: Grizzly (monster2) → p2+dodge_lava; Level 3 (juara): Tilly (taxi) → win; Level 4: Siren (police) → p3+oil
- **Status:** UPLOADED_SCHEDULED 2026-10-12T19:00:00Z (approve 2026-10-04)
- **Antrian:** SCHEDULED 2026-10-12T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/Gp7yvNydnKs

## Ep. 41 — `SIM_SMASH25D_V5_S005`

- **Judul YouTube:** Sprinkles, Rocky, Zippy or Siren? Last Car Standing! 💥 | Ep. 41 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E041_2026-10-03_smash25d/SIM_SMASH25D_V5_S005.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E041_2026-10-03_smash25d/SIM_SMASH25D_V5_S005.json` · audit: `renders/megawheel_arena/S02/E041_2026-10-03_smash25d/SIM_SMASH25D_V5_S005_audit.md`
- **Season / seri / seed:** S02 / smash25d / 5
- **Tema / narator:** noon-clear-city / chatterbox:mw-announcers-m1f1
- **Durasi:** 50.47 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p2+ring; Level 2: Rocky (monster) → win; Level 3 (juara): Zippy (sports) → p3+wreck; Level 4: Siren (police) → p4+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-13T23:00:00Z (approve 2026-10-03)
- **Antrian:** SCHEDULED 2026-10-13T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/2ekvyKZl7v8

## Ep. 42 — `SIM_LAVA_POTHOLES_V2_S026`

- **Judul YouTube:** Will Siren the Police Car Survive Giant Lava Potholes? 🌋🔥 | Ep. 42 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E042_2026-10-03_lava_potholes/SIM_LAVA_POTHOLES_V2_S026.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E042_2026-10-03_lava_potholes/SIM_LAVA_POTHOLES_V2_S026.json` · audit: `renders/megawheel_arena/S02/E042_2026-10-03_lava_potholes/SIM_LAVA_POTHOLES_V2_S026_audit.md`
- **Season / seri / seed:** S02 / lava_potholes / 26
- **Tema / narator:** morning-clear-volcano / chatterbox:m1
- **Durasi:** 46.77 s
- **Tokoh dan hasil:** Level 1: Siren (police) → rollback@obs2+broken; Level 2: Titan (bigrig) → stuck@obs0; Level 3 (juara): Nitro (f1) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-15T15:00:00Z (approve 2026-10-03)
- **Antrian:** SCHEDULED 2026-10-15T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/ivasm__dTxM

## Ep. 43 — `SIM_RACE25D_V4_S044`

- **Judul YouTube:** Can Nitro Survive the Giant Hammer? 🏁 | Ep. 43 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E043_2026-10-04_race25d/SIM_RACE25D_V4_S044.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E043_2026-10-04_race25d/SIM_RACE25D_V4_S044.json` · audit: `renders/megawheel_arena/S02/E043_2026-10-04_race25d/SIM_RACE25D_V4_S044_audit.md`
- **Season / seri / seed:** S02 / race25d / 44
- **Tema / narator:** sunset-clear-mountains / chatterbox:m1
- **Durasi:** 34.56 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p4+oil; Level 2: Grizzly (monster2) → p2; Level 3 (juara): Nitro (f1) → p3+hammer; Level 4: Zippy (sports) → win+dodge_lava
- **Status:** UPLOADED_SCHEDULED 2026-10-13T19:00:00Z (approve 2026-10-05)
- **Antrian:** SCHEDULED 2026-10-13T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/MsJCeAgnOrY

## Ep. 44 — `SIM_SMASH25D_V5_S008`

- **Judul YouTube:** Titan, Rocky, Tilly or Zippy? Last Car Standing! 💥 | Ep. 44 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E044_2026-10-03_smash25d/SIM_SMASH25D_V5_S008.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E044_2026-10-03_smash25d/SIM_SMASH25D_V5_S008.json` · audit: `renders/megawheel_arena/S02/E044_2026-10-03_smash25d/SIM_SMASH25D_V5_S008_audit.md`
- **Season / seri / seed:** S02 / smash25d / 8
- **Tema / narator:** morning-snow-countryside / chatterbox:mw-announcers-m1f1
- **Durasi:** 50.17 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p3+ring; Level 2: Rocky (monster) → p2+ring; Level 3 (juara): Tilly (taxi) → win; Level 4: Zippy (sports) → p4+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-14T23:00:00Z (approve 2026-10-03)
- **Antrian:** SCHEDULED 2026-10-14T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/qNLPmagWH3M

## Ep. 45 — `SIM_BUMPS_V2_S021`

- **Judul YouTube:** Can Zippy the Sports Car Survive Giant Speed Bumps? 🚗💥 | Ep. 45 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E045_2026-10-03_bumps/SIM_BUMPS_V2_S021.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E045_2026-10-03_bumps/SIM_BUMPS_V2_S021.json` · audit: `renders/megawheel_arena/S02/E045_2026-10-03_bumps/SIM_BUMPS_V2_S021_audit.md`
- **Season / seri / seed:** S02 / bumps / 21
- **Tema / narator:** sunset-rain-beach / chatterbox:m1
- **Durasi:** 49.33 s
- **Tokoh dan hasil:** Level 1: Zippy (sports) → flip@obs2; Level 2: Buster (bus) → flip@obs1+broken; Level 3 (juara): Rocky (monster) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-16T15:00:00Z (approve 2026-10-03)
- **Antrian:** SCHEDULED 2026-10-16T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/Sh2WfMcLj-M

## Ep. 46 — `SIM_RACE25D_V4_S046`

- **Judul YouTube:** Can Nitro Survive the Meteors? 🏁 | Ep. 46 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E046_2026-10-04_race25d/SIM_RACE25D_V4_S046.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E046_2026-10-04_race25d/SIM_RACE25D_V4_S046.json` · audit: `renders/megawheel_arena/S02/E046_2026-10-04_race25d/SIM_RACE25D_V4_S046_audit.md`
- **Season / seri / seed:** S02 / race25d / 46
- **Tema / narator:** morning-clear-desert / chatterbox:m1
- **Durasi:** 35.67 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p3; Level 2: Grizzly (monster2) → p2+dodge_oil; Level 3 (juara): Nitro (f1) → win+meteor; Level 4: Siren (police) → p4+wall
- **Status:** UPLOADED_SCHEDULED 2026-10-14T19:00:00Z (approve 2026-10-05)
- **Antrian:** SCHEDULED 2026-10-14T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/BJhlWYkiHF8

## Ep. 47 — `SIM_SMASH25D_V5_S009`

- **Judul YouTube:** Can Tiny Tilly Beat a School Bus? 💥 | Ep. 47 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E047_2026-10-03_smash25d/SIM_SMASH25D_V5_S009.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E047_2026-10-03_smash25d/SIM_SMASH25D_V5_S009.json` · audit: `renders/megawheel_arena/S02/E047_2026-10-03_smash25d/SIM_SMASH25D_V5_S009_audit.md`
- **Season / seri / seed:** S02 / smash25d / 9
- **Tema / narator:** night-clear-desert / chatterbox:mw-announcers-m1f1
- **Durasi:** 48.4 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p3+ring; Level 2: Grizzly (monster2) → win; Level 3 (juara): Tilly (taxi) → p4+ring; Level 4: Siren (police) → p2+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-15T23:00:00Z (approve 2026-10-03)
- **Antrian:** SCHEDULED 2026-10-15T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/eWqvYeCTWqk

## Ep. 48 — `SIM_POTHOLES_V2_S031`

- **Judul YouTube:** Police Car vs Giant Potholes! Can Siren Make It? 🚗💥 | Ep. 48 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E048_2026-10-04_potholes/SIM_POTHOLES_V2_S031.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E048_2026-10-04_potholes/SIM_POTHOLES_V2_S031.json` · audit: `renders/megawheel_arena/S02/E048_2026-10-04_potholes/SIM_POTHOLES_V2_S031_audit.md`
- **Season / seri / seed:** S02 / potholes / 31
- **Tema / narator:** morning-clear-desert / chatterbox:m1
- **Durasi:** 50.03 s
- **Tokoh dan hasil:** Level 1: Siren (police) → stuck@obs1+broken; Level 2: Hydro (firetruck) → pit@obs0+broken; Level 3 (juara): Zippy (sports) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-17T15:00:00Z (approve 2026-10-04)
- **Antrian:** SCHEDULED 2026-10-17T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/c8Y6AecAUCI

## Ep. 49 — `SIM_RACE25D_V4_S043`

- **Judul YouTube:** Can Siren Survive the Giant Hammer? 🏁 | Ep. 49 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E049_2026-10-04_race25d/SIM_RACE25D_V4_S043.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E049_2026-10-04_race25d/SIM_RACE25D_V4_S043.json` · audit: `renders/megawheel_arena/S02/E049_2026-10-04_race25d/SIM_RACE25D_V4_S043_audit.md`
- **Season / seri / seed:** S02 / race25d / 43
- **Tema / narator:** night-rain-city / chatterbox:f1
- **Durasi:** 39.04 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p3+dodge_crusher; Level 2: Rocky (monster) → p2; Level 3 (juara): Tilly (taxi) → win+ramp; Level 4: Siren (police) → p4+hammer
- **Status:** UPLOADED_SCHEDULED 2026-10-15T19:00:00Z (approve 2026-10-04)
- **Antrian:** SCHEDULED 2026-10-15T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/6HkCyVZqXrc

## Ep. 50 — `SIM_POTHOLES_V2_S028`

- **Judul YouTube:** Race Car vs Giant Potholes! Can Nitro Make It? 🚗💥 | Ep. 50 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E050_2026-10-04_potholes/SIM_POTHOLES_V2_S028.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E050_2026-10-04_potholes/SIM_POTHOLES_V2_S028.json` · audit: `renders/megawheel_arena/S02/E050_2026-10-04_potholes/SIM_POTHOLES_V2_S028_audit.md`
- **Season / seri / seed:** S02 / potholes / 28
- **Tema / narator:** morning-clear-countryside / chatterbox:m1
- **Durasi:** 47.17 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → pit@obs0+broken; Level 2: Hydro (firetruck) → stuck@obs0; Level 3 (juara): Sprinkles (icecream) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-18T15:00:00Z (approve 2026-10-04)
- **Antrian:** SCHEDULED 2026-10-18T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/8_uVESE2cr4

## Ep. 51 — `SIM_POTHOLES_V2_S029`

- **Judul YouTube:** Will Siren the Police Car Survive Giant Potholes? 🚗💥 | Ep. 51 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E051_2026-10-04_potholes/SIM_POTHOLES_V2_S029.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E051_2026-10-04_potholes/SIM_POTHOLES_V2_S029.json` · audit: `renders/megawheel_arena/S02/E051_2026-10-04_potholes/SIM_POTHOLES_V2_S029_audit.md`
- **Season / seri / seed:** S02 / potholes / 29
- **Tema / narator:** sunset-clear-beach / chatterbox:f1
- **Durasi:** 50.0 s
- **Tokoh dan hasil:** Level 1: Siren (police) → flip@obs0; Level 2: Titan (bigrig) → stuck@obs0; Level 3 (juara): Nitro (f1) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-19T15:00:00Z (approve 2026-10-04)
- **Antrian:** SCHEDULED 2026-10-19T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/JYouVAHqUeA

## Ep. 52 — `SIM_DUNGEON_V2_S015`

- **Judul YouTube:** Can Tilly the Taxi Survive Deadly Dungeon Traps? 🪓🌋 NEW 3D Graphics | Ep. 52 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E052_2026-10-07_dungeon/SIM_DUNGEON_V2_S015.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E052_2026-10-07_dungeon/SIM_DUNGEON_V2_S015.json` · audit: `renders/megawheel_arena/S02/E052_2026-10-07_dungeon/SIM_DUNGEON_V2_S015_audit.md`
- **Season / seri / seed:** S02 / dungeon / 15
- **Tema / narator:** noon-clear-volcano / chatterbox:m1
- **Durasi:** 49.3 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → smash@obs1+broken; Level 2: Titan (bigrig) → chop@obs0+broken; Level 3 (juara): Siren (police) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-20T15:00:00Z (approve 2026-10-07)
- **Antrian:** SCHEDULED 2026-10-20T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/DERf3rVbKd0

## Ep. 53 — `SIM_RACE25D_V4_S048`

- **Judul YouTube:** Can Hydro Survive the Giant Hammer? 🏁 | Ep. 53 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E053_2026-10-10_race25d/SIM_RACE25D_V4_S048.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E053_2026-10-10_race25d/SIM_RACE25D_V4_S048.json` · audit: `renders/megawheel_arena/S02/E053_2026-10-10_race25d/SIM_RACE25D_V4_S048_audit.md`
- **Season / seri / seed:** S02 / race25d / 48
- **Tema / narator:** sunset-clear-desert / chatterbox:m1
- **Durasi:** 36.65 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p3+hammer; Level 2: Grizzly (monster2) → p2; Level 3 (juara): Siren (police) → win+dodge_oil; Level 4: Zippy (sports) → p4+ufo
- **Status:** UPLOADED_SCHEDULED 2026-10-16T19:00:00Z (approve 2026-10-10)
- **Antrian:** SCHEDULED 2026-10-16T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/jbr_oreCvfY

## Ep. 54 — `SIM_RACE25D_V4_S051`

- **Judul YouTube:** Can Siren Survive Falling Containers? 🏁 | Ep. 54 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E054_2026-10-10_race25d/SIM_RACE25D_V4_S051.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E054_2026-10-10_race25d/SIM_RACE25D_V4_S051.json` · audit: `renders/megawheel_arena/S02/E054_2026-10-10_race25d/SIM_RACE25D_V4_S051_audit.md`
- **Season / seri / seed:** S02 / race25d / 51
- **Tema / narator:** morning-clear-mountains / chatterbox:f1
- **Durasi:** 38.48 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p3; Level 2: Rocky (monster) → p2+dodge_crusher; Level 3 (juara): Siren (police) → p4+container; Level 4: Tilly (taxi) → win+ramp
- **Status:** UPLOADED_SCHEDULED 2026-10-17T19:00:00Z (approve 2026-10-10)
- **Antrian:** SCHEDULED 2026-10-17T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/puxQcUZoOdc

## Ep. 55 — `SIM_RACE25D_V4_S055`

- **Judul YouTube:** Siren vs Falling Containers! Who Wins the Race? 🏁 | Ep. 55 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E055_2026-10-10_race25d/SIM_RACE25D_V4_S055.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E055_2026-10-10_race25d/SIM_RACE25D_V4_S055.json` · audit: `renders/megawheel_arena/S02/E055_2026-10-10_race25d/SIM_RACE25D_V4_S055_audit.md`
- **Season / seri / seed:** S02 / race25d / 55
- **Tema / narator:** noon-rain-beach / chatterbox:m1
- **Durasi:** 35.28 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p3+pothole; Level 2: Grizzly (monster2) → p2+ramp; Level 3 (juara): Zippy (sports) → win; Level 4: Siren (police) → p4+container
- **Status:** UPLOADED_SCHEDULED 2026-10-18T19:00:00Z (approve 2026-10-10)
- **Antrian:** SCHEDULED 2026-10-18T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/NaQ5MVI0etc

## Ep. 56 — `SIM_RACE25D_V4_S056`

- **Judul YouTube:** Zippy vs the Oil Slick! Who Wins the Race? 🏁 | Ep. 56 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E056_2026-10-10_race25d/SIM_RACE25D_V4_S056.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E056_2026-10-10_race25d/SIM_RACE25D_V4_S056.json` · audit: `renders/megawheel_arena/S02/E056_2026-10-10_race25d/SIM_RACE25D_V4_S056_audit.md`
- **Season / seri / seed:** S02 / race25d / 56
- **Tema / narator:** morning-snow-city / chatterbox:f1
- **Durasi:** 36.25 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p2; Level 2: Grizzly (monster2) → win+dodge_lava; Level 3 (juara): Tilly (taxi) → p4+ufo; Level 4: Zippy (sports) → p3+oil
- **Status:** UPLOADED_SCHEDULED 2026-10-19T19:00:00Z (approve 2026-10-10)
- **Antrian:** SCHEDULED 2026-10-19T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/Wls3wOxIct0

## Ep. 57 — `SIM_SMASH25D_V5_S016`

- **Judul YouTube:** Big Rig vs Monster Truck vs Race Car vs Taxi! Who Survives? 💥 | Ep. 57 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E057_2026-10-10_smash25d/SIM_SMASH25D_V5_S016.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E057_2026-10-10_smash25d/SIM_SMASH25D_V5_S016.json` · audit: `renders/megawheel_arena/S02/E057_2026-10-10_smash25d/SIM_SMASH25D_V5_S016_audit.md`
- **Season / seri / seed:** S02 / smash25d / 16
- **Tema / narator:** night-clear-mountains / chatterbox:mw-announcers-m1f1
- **Durasi:** 49.3 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p3+wreck; Level 2: Grizzly (monster2) → win; Level 3 (juara): Nitro (f1) → p4+ring; Level 4: Tilly (taxi) → p2+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-16T23:00:00Z (approve 2026-10-10)
- **Antrian:** SCHEDULED 2026-10-16T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/6eLjmpy02NM

## Ep. 58 — `SIM_SMASH25D_V5_S017`

- **Judul YouTube:** Sprinkles, Rocky, Nitro or Zippy? Last Car Standing! 💥 | Ep. 58 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E058_2026-10-10_smash25d/SIM_SMASH25D_V5_S017.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E058_2026-10-10_smash25d/SIM_SMASH25D_V5_S017.json` · audit: `renders/megawheel_arena/S02/E058_2026-10-10_smash25d/SIM_SMASH25D_V5_S017_audit.md`
- **Season / seri / seed:** S02 / smash25d / 17
- **Tema / narator:** night-snow-countryside / chatterbox:mw-announcers-m1f1
- **Durasi:** 51.62 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p4+ring; Level 2: Rocky (monster) → win; Level 3 (juara): Nitro (f1) → p2+wreck; Level 4: Zippy (sports) → p3+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-17T23:00:00Z (approve 2026-10-10)
- **Antrian:** SCHEDULED 2026-10-17T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/0UhR4k8z9mk

## Ep. 59 — `SIM_SMASH25D_V5_S018`

- **Judul YouTube:** Can Tiny Nitro Beat a Big Rig? 💥 | Ep. 59 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E059_2026-10-10_smash25d/SIM_SMASH25D_V5_S018.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E059_2026-10-10_smash25d/SIM_SMASH25D_V5_S018.json` · audit: `renders/megawheel_arena/S02/E059_2026-10-10_smash25d/SIM_SMASH25D_V5_S018_audit.md`
- **Season / seri / seed:** S02 / smash25d / 18
- **Tema / narator:** sunset-clear-desert / chatterbox:mw-announcers-m1f1
- **Durasi:** 52.2 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p4+ring; Level 2: Rocky (monster) → win; Level 3 (juara): Tilly (taxi) → p2+ring; Level 4: Nitro (f1) → p3+wreck
- **Status:** UPLOADED_SCHEDULED 2026-10-18T23:00:00Z (approve 2026-10-10)
- **Antrian:** SCHEDULED 2026-10-18T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/2mJ7FCqvYTg

## Ep. 60 — `SIM_RACE25D_V4_S047`

- **Judul YouTube:** Can Zippy Survive Falling Containers? 🏁 | Ep. 60 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S02/E060_2026-10-08_race25d/SIM_RACE25D_V4_S047.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S02/E060_2026-10-08_race25d/SIM_RACE25D_V4_S047.json` · audit: `renders/megawheel_arena/S02/E060_2026-10-08_race25d/SIM_RACE25D_V4_S047_audit.md`
- **Season / seri / seed:** S02 / race25d / 47
- **Tema / narator:** noon-clear-mountains / chatterbox:f1
- **Durasi:** 38.55 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p3+meteor; Level 2: Grizzly (monster2) → p2+dodge_puddle; Level 3 (juara): Zippy (sports) → p4+container; Level 4: Tilly (taxi) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-20T19:00:00Z (approve 2026-10-10)
- **Antrian:** SCHEDULED 2026-10-20T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/YsTdVDb4fWc

## Ep. 61 — `SIM_RACE25D_V4_S057`

- **Judul YouTube:** Siren vs the Giant Hammer! Who Wins the Race? 🏁 | Ep. 61 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E061_2026-10-10_race25d/SIM_RACE25D_V4_S057.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E061_2026-10-10_race25d/SIM_RACE25D_V4_S057.json` · audit: `renders/megawheel_arena/S03/E061_2026-10-10_race25d/SIM_RACE25D_V4_S057_audit.md`
- **Season / seri / seed:** S03 / race25d / 57
- **Tema / narator:** sunset-rain-beach / chatterbox:m1
- **Durasi:** 35.79 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p3+pothole; Level 2: Rocky (monster) → p2+dodge_wall; Level 3 (juara): Nitro (f1) → win; Level 4: Siren (police) → p4+hammer
- **Status:** UPLOADED_SCHEDULED 2026-10-21T19:00:00Z (approve 2026-10-10)
- **Antrian:** SCHEDULED 2026-10-21T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/qs4m4wnQx2s

## Ep. 62 — `SIM_SMASH25D_V5_S020`

- **Judul YouTube:** Sprinkles, Grizzly, Nitro or Zippy? Last Car Standing! 💥 | Ep. 62 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E062_2026-10-10_smash25d/SIM_SMASH25D_V5_S020.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E062_2026-10-10_smash25d/SIM_SMASH25D_V5_S020.json` · audit: `renders/megawheel_arena/S03/E062_2026-10-10_smash25d/SIM_SMASH25D_V5_S020_audit.md`
- **Season / seri / seed:** S03 / smash25d / 20
- **Tema / narator:** night-clear-mountains / chatterbox:mw-announcers-m1f1
- **Durasi:** 52.13 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p2+ring; Level 2: Grizzly (monster2) → win; Level 3 (juara): Nitro (f1) → p3+ring; Level 4: Zippy (sports) → p4+wreck
- **Status:** UPLOADED_SCHEDULED 2026-10-19T23:00:00Z (approve 2026-10-10)
- **Antrian:** SCHEDULED 2026-10-19T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/lym-XWogLPk

## Ep. 63 — `SIM_SMASH25D_V5_S021`

- **Judul YouTube:** Can Tiny Nitro Beat a School Bus? 💥 | Ep. 63 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E063_2026-10-10_smash25d/SIM_SMASH25D_V5_S021.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E063_2026-10-10_smash25d/SIM_SMASH25D_V5_S021.json` · audit: `renders/megawheel_arena/S03/E063_2026-10-10_smash25d/SIM_SMASH25D_V5_S021_audit.md`
- **Season / seri / seed:** S03 / smash25d / 21
- **Tema / narator:** sunset-rain-city / chatterbox:mw-announcers-m1f1
- **Durasi:** 50.67 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p4+ring; Level 2: Rocky (monster) → win; Level 3 (juara): Nitro (f1) → p3+ring; Level 4: Siren (police) → p2+wreck
- **Status:** UPLOADED_SCHEDULED 2026-10-20T23:00:00Z (approve 2026-10-10)
- **Antrian:** SCHEDULED 2026-10-20T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/vZAkrIzQ7zQ

## Ep. 64 — `SIM_PENDULUM_V2_S002`

- **Judul YouTube:** Will Tilly the Taxi Survive A Giant Swinging Wrecking Ball? 💥 | Ep. 64 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E064_2026-10-11_pendulum/SIM_PENDULUM_V2_S002.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E064_2026-10-11_pendulum/SIM_PENDULUM_V2_S002.json` · audit: `renders/megawheel_arena/S03/E064_2026-10-11_pendulum/SIM_PENDULUM_V2_S002_audit.md`
- **Season / seri / seed:** S03 / pendulum / 2
- **Tema / narator:** noon-clear-volcano / chatterbox:m1
- **Durasi:** 57.57 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → smash@obs2+broken; Level 2: Buster (bus) → smash@obs2+broken; Level 3 (juara): Titan (bigrig) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-21T15:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-21T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/YTTl_1sokjE

## Ep. 65 — `SIM_DOMINO_V2_S001`

- **Judul YouTube:** Taxi vs A Wave Of Giant Falling Dominoes! Can Tilly Make It? 🁢 | Ep. 65 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E065_2026-10-11_domino/SIM_DOMINO_V2_S001.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E065_2026-10-11_domino/SIM_DOMINO_V2_S001.json` · audit: `renders/megawheel_arena/S03/E065_2026-10-11_domino/SIM_DOMINO_V2_S001_audit.md`
- **Season / seri / seed:** S03 / domino / 1
- **Tema / narator:** sunset-clear-beach / chatterbox:m1
- **Durasi:** 52.93 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → chop@obs1+broken; Level 2: Buster (bus) → chop@obs0+broken; Level 3 (juara): Siren (police) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-22T15:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-22T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/mVQhUTvk9ZI

## Ep. 66 — `SIM_PINBALL_V2_S004`

- **Judul YouTube:** Race Car vs Giant Pinball Bumpers Over A Lava Pit! Can Nitro Make It? 🔴 | Ep. 66 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E066_2026-10-11_pinball/SIM_PINBALL_V2_S004.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E066_2026-10-11_pinball/SIM_PINBALL_V2_S004.json` · audit: `renders/megawheel_arena/S03/E066_2026-10-11_pinball/SIM_PINBALL_V2_S004_audit.md`
- **Season / seri / seed:** S03 / pinball / 4
- **Tema / narator:** noon-clear-volcano / chatterbox:f1
- **Durasi:** 59.87 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → pit@obs1+broken; Level 2: Hydro (firetruck) → rollback@obs0+broken; Level 3 (juara): Sprinkles (icecream) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-23T15:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-23T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/qoeUhMg2-7Q

## Ep. 67 — `SIM_RACE25D_V4_S058`

- **Judul YouTube:** Can Tilly Survive Falling Containers? 🏁 | Ep. 67 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E067_2026-10-11_race25d/SIM_RACE25D_V4_S058.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E067_2026-10-11_race25d/SIM_RACE25D_V4_S058.json` · audit: `renders/megawheel_arena/S03/E067_2026-10-11_race25d/SIM_RACE25D_V4_S058_audit.md`
- **Season / seri / seed:** S03 / race25d / 58
- **Tema / narator:** noon-rain-countryside / chatterbox:f1
- **Durasi:** 35.44 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p3; Level 2: Grizzly (monster2) → p2; Level 3 (juara): Tilly (taxi) → p4+container; Level 4: Nitro (f1) → win+laser+dodge_puddle
- **Status:** UPLOADED_SCHEDULED 2026-10-22T19:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-22T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/Guo_ikHKcMk

## Ep. 68 — `SIM_RACE25D_V4_S059`

- **Judul YouTube:** Can Grizzly Survive the Giant Hammer? 🏁 | Ep. 68 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E068_2026-10-11_race25d/SIM_RACE25D_V4_S059.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E068_2026-10-11_race25d/SIM_RACE25D_V4_S059.json` · audit: `renders/megawheel_arena/S03/E068_2026-10-11_race25d/SIM_RACE25D_V4_S059_audit.md`
- **Season / seri / seed:** S03 / race25d / 59
- **Tema / narator:** night-clear-desert / chatterbox:f1
- **Durasi:** 37.55 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p2+puddle; Level 2: Grizzly (monster2) → p4+hammer; Level 3 (juara): Nitro (f1) → p3+crusher; Level 4: Zippy (sports) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-23T19:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-23T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/_BkZRCpEhPg

## Ep. 69 — `SIM_RACE25D_V4_S060`

- **Judul YouTube:** Can Grizzly Survive Falling Containers? 🏁 | Ep. 69 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E069_2026-10-11_race25d/SIM_RACE25D_V4_S060.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E069_2026-10-11_race25d/SIM_RACE25D_V4_S060.json` · audit: `renders/megawheel_arena/S03/E069_2026-10-11_race25d/SIM_RACE25D_V4_S060_audit.md`
- **Season / seri / seed:** S03 / race25d / 60
- **Tema / narator:** night-rain-countryside / chatterbox:m1
- **Durasi:** 35.65 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p4+wall; Level 2: Grizzly (monster2) → p3+container; Level 3 (juara): Nitro (f1) → win+meteor; Level 4: Tilly (taxi) → p2
- **Status:** UPLOADED_SCHEDULED 2026-10-24T19:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-24T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/KIZF_hjOXJY

## Ep. 70 — `SIM_SMASH25D_V5_S022`

- **Judul YouTube:** Ice Cream Truck vs Monster Truck vs Police Car vs Sports Car! Who Survives? 💥 | Ep. 70 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E070_2026-10-11_smash25d/SIM_SMASH25D_V5_S022.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E070_2026-10-11_smash25d/SIM_SMASH25D_V5_S022.json` · audit: `renders/megawheel_arena/S03/E070_2026-10-11_smash25d/SIM_SMASH25D_V5_S022_audit.md`
- **Season / seri / seed:** S03 / smash25d / 22
- **Tema / narator:** morning-clear-desert / chatterbox:mw-announcers-m1f1
- **Durasi:** 56.17 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p4+ring; Level 2: Rocky (monster) → win; Level 3 (juara): Siren (police) → p2+wreck; Level 4: Zippy (sports) → p3+wreck
- **Status:** UPLOADED_SCHEDULED 2026-10-21T23:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-21T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/YOg4cwmPHdw

## Ep. 71 — `SIM_SMASH25D_V5_S023`

- **Judul YouTube:** Titan, Rocky, Tilly or Siren? Last Car Standing! 💥 | Ep. 71 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E071_2026-10-11_smash25d/SIM_SMASH25D_V5_S023.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E071_2026-10-11_smash25d/SIM_SMASH25D_V5_S023.json` · audit: `renders/megawheel_arena/S03/E071_2026-10-11_smash25d/SIM_SMASH25D_V5_S023_audit.md`
- **Season / seri / seed:** S03 / smash25d / 23
- **Tema / narator:** sunset-clear-mountains / chatterbox:mw-announcers-m1f1
- **Durasi:** 55.38 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p4+ring; Level 2: Rocky (monster) → p3+wreck; Level 3 (juara): Tilly (taxi) → win; Level 4: Siren (police) → p2+wreck
- **Status:** UPLOADED_SCHEDULED 2026-10-22T23:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-22T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/diUdJsm2_SM

## Ep. 72 — `SIM_SMASH25D_V5_S024`

- **Judul YouTube:** Can Tiny Zippy Beat a Fire Truck? 💥 | Ep. 72 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E072_2026-10-11_smash25d/SIM_SMASH25D_V5_S024.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E072_2026-10-11_smash25d/SIM_SMASH25D_V5_S024.json` · audit: `renders/megawheel_arena/S03/E072_2026-10-11_smash25d/SIM_SMASH25D_V5_S024_audit.md`
- **Season / seri / seed:** S03 / smash25d / 24
- **Tema / narator:** morning-rain-city / chatterbox:mw-announcers-m1f1
- **Durasi:** 52.32 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p2+ring; Level 2: Grizzly (monster2) → win; Level 3 (juara): Zippy (sports) → p3+wreck; Level 4: Siren (police) → p4+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-23T23:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-23T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/ygW5VWZpx1c

## Ep. 73 — `SIM_GAUNTLET_V2_S004`

- **Judul YouTube:** Police Car vs A Gauntlet Of Giant Swinging Balls, Falling Dominoes And More! Can Siren Make It? 💥 | Ep. 73 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E073_2026-10-11_gauntlet/SIM_GAUNTLET_V2_S004.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E073_2026-10-11_gauntlet/SIM_GAUNTLET_V2_S004.json` · audit: `renders/megawheel_arena/S03/E073_2026-10-11_gauntlet/SIM_GAUNTLET_V2_S004_audit.md`
- **Season / seri / seed:** S03 / gauntlet / 4
- **Tema / narator:** morning-clear-beach / chatterbox:m1
- **Durasi:** 49.3 s
- **Tokoh dan hasil:** Level 1: Siren (police) → chop@obs2+broken; Level 2: Titan (bigrig) → rollback@obs0; Level 3 (juara): Nitro (f1) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-24T15:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-24T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/VFZjvEaUpsc

## Ep. 74 — `SIM_GAUNTLET_V2_S005`

- **Judul YouTube:** Will Siren the Police Car Survive A Gauntlet Of Giant Swinging Balls, Falling Dominoes And More? 💥 | Ep. 74 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E074_2026-10-11_gauntlet/SIM_GAUNTLET_V2_S005.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E074_2026-10-11_gauntlet/SIM_GAUNTLET_V2_S005.json` · audit: `renders/megawheel_arena/S03/E074_2026-10-11_gauntlet/SIM_GAUNTLET_V2_S005_audit.md`
- **Season / seri / seed:** S03 / gauntlet / 5
- **Tema / narator:** noon-clear-city / chatterbox:m1
- **Durasi:** 51.47 s
- **Tokoh dan hasil:** Level 1: Siren (police) → flip@obs1+broken; Level 2: Titan (bigrig) → chop@obs0+broken; Level 3 (juara): Tilly (taxi) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-25T15:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-25T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/xm-xShnbV_g

## Ep. 75 — `SIM_LAVA_POTHOLES_V2_S028`

- **Judul YouTube:** Taxi vs Giant Lava Potholes! Can Tilly Make It? 🌋🔥 | Ep. 75 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E075_2026-10-11_lava_potholes/SIM_LAVA_POTHOLES_V2_S028.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E075_2026-10-11_lava_potholes/SIM_LAVA_POTHOLES_V2_S028.json` · audit: `renders/megawheel_arena/S03/E075_2026-10-11_lava_potholes/SIM_LAVA_POTHOLES_V2_S028_audit.md`
- **Season / seri / seed:** S03 / lava_potholes / 28
- **Tema / narator:** night-clear-volcano / chatterbox:m1
- **Durasi:** 47.57 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → pit@obs0; Level 2: Hydro (firetruck) → pit@obs2; Level 3 (juara): Grizzly (monster2) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-26T15:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-26T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/lHByBBaLVXo

## Ep. 76 — `SIM_RACE25D_V4_S061`

- **Judul YouTube:** Can Siren Survive the Wall? 🏁 | Ep. 76 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E076_2026-10-11_race25d/SIM_RACE25D_V4_S061.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E076_2026-10-11_race25d/SIM_RACE25D_V4_S061.json` · audit: `renders/megawheel_arena/S03/E076_2026-10-11_race25d/SIM_RACE25D_V4_S061_audit.md`
- **Season / seri / seed:** S03 / race25d / 61
- **Tema / narator:** night-clear-city / chatterbox:f1
- **Durasi:** 35.58 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p3; Level 2: Rocky (monster) → p2; Level 3 (juara): Tilly (taxi) → win+ramp; Level 4: Siren (police) → p4+wall+dodge_oil
- **Status:** UPLOADED_SCHEDULED 2026-10-25T19:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-25T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/dpIG3zz0nQs

## Ep. 77 — `SIM_RACE25D_V4_S063`

- **Judul YouTube:** Can Tilly Survive the Giant Hammer? 🏁 | Ep. 77 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E077_2026-10-11_race25d/SIM_RACE25D_V4_S063.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E077_2026-10-11_race25d/SIM_RACE25D_V4_S063.json` · audit: `renders/megawheel_arena/S03/E077_2026-10-11_race25d/SIM_RACE25D_V4_S063_audit.md`
- **Season / seri / seed:** S03 / race25d / 63
- **Tema / narator:** morning-clear-mountains / chatterbox:f1
- **Durasi:** 38.92 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p3+dodge_crusher; Level 2: Rocky (monster) → p2; Level 3 (juara): Tilly (taxi) → p4+hammer; Level 4: Nitro (f1) → win+ramp
- **Status:** UPLOADED_SCHEDULED 2026-10-26T19:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-26T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/wJRlHjwcgWg

## Ep. 78 — `SIM_SMASH25D_V5_S025`

- **Judul YouTube:** Fire Truck vs Monster Truck vs Sports Car vs Police Car! Who Survives? 💥 | Ep. 78 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E078_2026-10-11_smash25d/SIM_SMASH25D_V5_S025.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E078_2026-10-11_smash25d/SIM_SMASH25D_V5_S025.json` · audit: `renders/megawheel_arena/S03/E078_2026-10-11_smash25d/SIM_SMASH25D_V5_S025_audit.md`
- **Season / seri / seed:** S03 / smash25d / 25
- **Tema / narator:** noon-clear-countryside / chatterbox:mw-announcers-m1f1
- **Durasi:** 50.58 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p4+ring; Level 2: Grizzly (monster2) → p3+ring; Level 3 (juara): Zippy (sports) → p2+ring; Level 4: Siren (police) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-24T23:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-24T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/2FRVVI2q_vM

## Ep. 79 — `SIM_SMASH25D_V5_S028`

- **Judul YouTube:** Big Rig vs Monster Truck vs Police Car vs Sports Car! Who Survives? 💥 | Ep. 79 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E079_2026-10-11_smash25d/SIM_SMASH25D_V5_S028.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E079_2026-10-11_smash25d/SIM_SMASH25D_V5_S028.json` · audit: `renders/megawheel_arena/S03/E079_2026-10-11_smash25d/SIM_SMASH25D_V5_S028_audit.md`
- **Season / seri / seed:** S03 / smash25d / 28
- **Tema / narator:** sunset-clear-countryside / chatterbox:mw-announcers-m1f1
- **Durasi:** 51.55 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p4+ring; Level 2: Rocky (monster) → p3+ring; Level 3 (juara): Siren (police) → p2+wreck; Level 4: Zippy (sports) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-25T23:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-25T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/n7E87OZBYe8

## Ep. 80 — `SIM_SMASH25D_V5_S029`

- **Judul YouTube:** Buster, Grizzly, Tilly or Nitro? Last Car Standing! 💥 | Ep. 80 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E080_2026-10-11_smash25d/SIM_SMASH25D_V5_S029.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E080_2026-10-11_smash25d/SIM_SMASH25D_V5_S029.json` · audit: `renders/megawheel_arena/S03/E080_2026-10-11_smash25d/SIM_SMASH25D_V5_S029_audit.md`
- **Season / seri / seed:** S03 / smash25d / 29
- **Tema / narator:** sunset-clear-beach / chatterbox:mw-announcers-m1f1
- **Durasi:** 56.24 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → win; Level 2: Grizzly (monster2) → p3+ring; Level 3 (juara): Tilly (taxi) → p2+wreck; Level 4: Nitro (f1) → p4+wreck
- **Status:** UPLOADED_SCHEDULED 2026-10-26T23:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-26T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/trI9Q77SAxU

## Ep. 81 — `SIM_GAUNTLET_V2_S007`

- **Judul YouTube:** Taxi vs A Gauntlet Of Giant Swinging Balls, Falling Dominoes And More! Can Tilly Make It? 💥 | Ep. 81 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E081_2026-10-11_gauntlet/SIM_GAUNTLET_V2_S007.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E081_2026-10-11_gauntlet/SIM_GAUNTLET_V2_S007.json` · audit: `renders/megawheel_arena/S03/E081_2026-10-11_gauntlet/SIM_GAUNTLET_V2_S007_audit.md`
- **Season / seri / seed:** S03 / gauntlet / 7
- **Tema / narator:** morning-clear-mountains / chatterbox:f1
- **Durasi:** 54.1 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → flip@obs1; Level 2: Titan (bigrig) → smash@obs2+broken; Level 3 (juara): Nitro (f1) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-27T15:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-27T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/Mb76nmh0YyM

## Ep. 82 — `SIM_LAVA_POTHOLES_V2_S029`

- **Judul YouTube:** Will Tilly the Taxi Survive Giant Lava Potholes? 🌋🔥 | Ep. 82 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E082_2026-10-11_lava_potholes/SIM_LAVA_POTHOLES_V2_S029.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E082_2026-10-11_lava_potholes/SIM_LAVA_POTHOLES_V2_S029.json` · audit: `renders/megawheel_arena/S03/E082_2026-10-11_lava_potholes/SIM_LAVA_POTHOLES_V2_S029_audit.md`
- **Season / seri / seed:** S03 / lava_potholes / 29
- **Tema / narator:** sunset-clear-volcano / chatterbox:m1
- **Durasi:** 58.33 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → pit@obs1; Level 2: Buster (bus) → rollback@obs1+broken; Level 3 (juara): Sprinkles (icecream) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-28T15:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-28T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/KZNCFqh33go

## Ep. 83 — `SIM_PENDULUM_V2_S004`

- **Judul YouTube:** Race Car vs A Giant Swinging Wrecking Ball! Can Nitro Make It? 💥 | Ep. 83 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E083_2026-10-11_pendulum/SIM_PENDULUM_V2_S004.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E083_2026-10-11_pendulum/SIM_PENDULUM_V2_S004.json` · audit: `renders/megawheel_arena/S03/E083_2026-10-11_pendulum/SIM_PENDULUM_V2_S004_audit.md`
- **Season / seri / seed:** S03 / pendulum / 4
- **Tema / narator:** morning-clear-volcano / chatterbox:m1
- **Durasi:** 57.0 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → smash@obs2+broken; Level 2: Hydro (firetruck) → smash@obs2+broken; Level 3 (juara): Buster (bus) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-29T15:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-29T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/XTuIEMNarGE

## Ep. 84 — `SIM_RACE25D_V4_S066`

- **Judul YouTube:** Can Sprinkles Survive Falling Containers? 🏁 | Ep. 84 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E084_2026-10-11_race25d/SIM_RACE25D_V4_S066.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E084_2026-10-11_race25d/SIM_RACE25D_V4_S066.json` · audit: `renders/megawheel_arena/S03/E084_2026-10-11_race25d/SIM_RACE25D_V4_S066_audit.md`
- **Season / seri / seed:** S03 / race25d / 66
- **Tema / narator:** sunset-clear-desert / chatterbox:f1
- **Durasi:** 38.69 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p4+container; Level 2: Rocky (monster) → p2+dodge_laser; Level 3 (juara): Zippy (sports) → p3+dragon_ice; Level 4: Nitro (f1) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-27T19:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-27T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/4xdJO93mknM

## Ep. 85 — `SIM_RACE25D_V4_S067`

- **Judul YouTube:** Will Nitro Make It Past the Giant Hammer? 🏁 | Ep. 85 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E085_2026-10-11_race25d/SIM_RACE25D_V4_S067.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E085_2026-10-11_race25d/SIM_RACE25D_V4_S067.json` · audit: `renders/megawheel_arena/S03/E085_2026-10-11_race25d/SIM_RACE25D_V4_S067_audit.md`
- **Season / seri / seed:** S03 / race25d / 67
- **Tema / narator:** night-clear-desert / chatterbox:f1
- **Durasi:** 36.2 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p3; Level 2: Grizzly (monster2) → p2+ramp; Level 3 (juara): Zippy (sports) → win+lava; Level 4: Nitro (f1) → p4+hammer
- **Status:** UPLOADED_SCHEDULED 2026-10-28T19:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-28T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/cwG86oKxxwQ

## Ep. 86 — `SIM_RACE25D_V4_S068`

- **Judul YouTube:** Can Nitro Survive the Oil Slick? 🏁 | Ep. 86 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E086_2026-10-11_race25d/SIM_RACE25D_V4_S068.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E086_2026-10-11_race25d/SIM_RACE25D_V4_S068.json` · audit: `renders/megawheel_arena/S03/E086_2026-10-11_race25d/SIM_RACE25D_V4_S068_audit.md`
- **Season / seri / seed:** S03 / race25d / 68
- **Tema / narator:** noon-clear-mountains / chatterbox:m1
- **Durasi:** 35.65 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p4; Level 2: Rocky (monster) → p2; Level 3 (juara): Zippy (sports) → win+lava+dodge_pothole; Level 4: Nitro (f1) → p3+oil
- **Status:** UPLOADED_SCHEDULED 2026-10-29T19:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-29T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/PsnDA9kn7ig

## Ep. 87 — `SIM_SMASH25D_V5_S030`

- **Judul YouTube:** Can Tiny Zippy Beat a School Bus? 💥 | Ep. 87 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E087_2026-10-11_smash25d/SIM_SMASH25D_V5_S030.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E087_2026-10-11_smash25d/SIM_SMASH25D_V5_S030.json` · audit: `renders/megawheel_arena/S03/E087_2026-10-11_smash25d/SIM_SMASH25D_V5_S030_audit.md`
- **Season / seri / seed:** S03 / smash25d / 30
- **Tema / narator:** morning-rain-countryside / chatterbox:mw-announcers-m1f1
- **Durasi:** 48.81 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p4+ring; Level 2: Grizzly (monster2) → p2+ring; Level 3 (juara): Zippy (sports) → p3+wreck; Level 4: Siren (police) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-27T23:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-27T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/i6zipDevoTA

## Ep. 88 — `SIM_SMASH25D_V5_S032`

- **Judul YouTube:** Hydro, Rocky, Zippy or Siren? Last Car Standing! 💥 | Ep. 88 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E088_2026-10-11_smash25d/SIM_SMASH25D_V5_S032.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E088_2026-10-11_smash25d/SIM_SMASH25D_V5_S032.json` · audit: `renders/megawheel_arena/S03/E088_2026-10-11_smash25d/SIM_SMASH25D_V5_S032_audit.md`
- **Season / seri / seed:** S03 / smash25d / 32
- **Tema / narator:** night-clear-desert / chatterbox:mw-announcers-m1f1
- **Durasi:** 49.05 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → p2+ring; Level 2: Rocky (monster) → p3+wreck; Level 3 (juara): Zippy (sports) → win; Level 4: Siren (police) → p4+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-28T23:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-28T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/8q9Bbk-An5U

## Ep. 89 — `SIM_SMASH25D_V5_S034`

- **Judul YouTube:** Big Rig vs Monster Truck vs Sports Car vs Taxi! Who Survives? 💥 | Ep. 89 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E089_2026-10-11_smash25d/SIM_SMASH25D_V5_S034.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E089_2026-10-11_smash25d/SIM_SMASH25D_V5_S034.json` · audit: `renders/megawheel_arena/S03/E089_2026-10-11_smash25d/SIM_SMASH25D_V5_S034_audit.md`
- **Season / seri / seed:** S03 / smash25d / 34
- **Tema / narator:** noon-rain-city / chatterbox:mw-announcers-m1f1
- **Durasi:** 53.78 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → win; Level 2: Grizzly (monster2) → p2+wreck; Level 3 (juara): Zippy (sports) → p4+ring; Level 4: Tilly (taxi) → p3+wreck
- **Status:** UPLOADED_SCHEDULED 2026-10-29T23:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-29T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/jiixposH0eo

## Ep. 90 — `SIM_POTHOLES_V2_S033`

- **Judul YouTube:** Can Siren the Police Car Survive Giant Potholes? 🚗💥 | Ep. 90 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S03/E090_2026-10-11_potholes/SIM_POTHOLES_V2_S033.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S03/E090_2026-10-11_potholes/SIM_POTHOLES_V2_S033.json` · audit: `renders/megawheel_arena/S03/E090_2026-10-11_potholes/SIM_POTHOLES_V2_S033_audit.md`
- **Season / seri / seed:** S03 / potholes / 33
- **Tema / narator:** noon-clear-mountains / chatterbox:f1
- **Durasi:** 55.3 s
- **Tokoh dan hasil:** Level 1: Siren (police) → stuck@obs1; Level 2: Sprinkles (icecream) → pit@obs0+broken; Level 3 (juara): Hydro (firetruck) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-30T15:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-30T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/LA5GZDAqS1U

## Ep. 91 — `SIM_BUMPS_V2_S022`

- **Judul YouTube:** Taxi vs Giant Speed Bumps! Can Tilly Make It? 🚗💥 | Ep. 91 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E091_2026-10-11_bumps/SIM_BUMPS_V2_S022.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E091_2026-10-11_bumps/SIM_BUMPS_V2_S022.json` · audit: `renders/megawheel_arena/S04/E091_2026-10-11_bumps/SIM_BUMPS_V2_S022_audit.md`
- **Season / seri / seed:** S04 / bumps / 22
- **Tema / narator:** morning-clear-beach / chatterbox:f1
- **Durasi:** 50.13 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → flip@obs2+broken; Level 2: Titan (bigrig) → stuck@obs1; Level 3 (juara): Rocky (monster) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-31T15:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-31T15:00:00Z
- **YouTube:** https://www.youtube.com/shorts/yFWEjAOlIB4

## Ep. 92 — `SIM_RACE25D_V4_S069`

- **Judul YouTube:** Zippy vs Falling Containers! Who Wins the Race? 🏁 | Ep. 92 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E092_2026-10-11_race25d/SIM_RACE25D_V4_S069.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E092_2026-10-11_race25d/SIM_RACE25D_V4_S069.json` · audit: `renders/megawheel_arena/S04/E092_2026-10-11_race25d/SIM_RACE25D_V4_S069_audit.md`
- **Season / seri / seed:** S04 / race25d / 69
- **Tema / narator:** noon-clear-desert / chatterbox:f1
- **Durasi:** 37.48 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p3; Level 2: Rocky (monster) → p2; Level 3 (juara): Zippy (sports) → p4+container; Level 4: Nitro (f1) → win+ramp+dodge_wall
- **Status:** UPLOADED_SCHEDULED 2026-10-30T19:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-30T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/dfyq1sts3ZI

## Ep. 93 — `SIM_RACE25D_V4_S070`

- **Judul YouTube:** Can Sprinkles Survive the Oil Slick? 🏁 | Ep. 93 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E093_2026-10-11_race25d/SIM_RACE25D_V4_S070.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E093_2026-10-11_race25d/SIM_RACE25D_V4_S070.json` · audit: `renders/megawheel_arena/S04/E093_2026-10-11_race25d/SIM_RACE25D_V4_S070_audit.md`
- **Season / seri / seed:** S04 / race25d / 70
- **Tema / narator:** night-snow-city / chatterbox:m1
- **Durasi:** 34.79 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p3+oil; Level 2: Grizzly (monster2) → p2+dodge_laser; Level 3 (juara): Siren (police) → p4+ufo; Level 4: Nitro (f1) → win
- **Status:** UPLOADED_SCHEDULED 2026-10-31T19:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-31T19:00:00Z
- **YouTube:** https://www.youtube.com/shorts/nuWeVdaiJe8

## Ep. 94 — `SIM_SMASH25D_V5_S036`

- **Judul YouTube:** Can Tiny Zippy Beat a School Bus? 💥 | Ep. 94 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E094_2026-10-11_smash25d/SIM_SMASH25D_V5_S036.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E094_2026-10-11_smash25d/SIM_SMASH25D_V5_S036.json` · audit: `renders/megawheel_arena/S04/E094_2026-10-11_smash25d/SIM_SMASH25D_V5_S036_audit.md`
- **Season / seri / seed:** S04 / smash25d / 36
- **Tema / narator:** night-clear-countryside / chatterbox:mw-announcers-m1f1
- **Durasi:** 51.18 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p2+ring; Level 2: Rocky (monster) → p4+ring; Level 3 (juara): Zippy (sports) → win; Level 4: Siren (police) → p3+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-30T23:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-30T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/ec1zc5iboQE

## Ep. 95 — `SIM_SMASH25D_V5_S037`

- **Judul YouTube:** School Bus vs Monster Truck vs Taxi vs Race Car! Who Survives? 💥 | Ep. 95 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E095_2026-10-11_smash25d/SIM_SMASH25D_V5_S037.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E095_2026-10-11_smash25d/SIM_SMASH25D_V5_S037.json` · audit: `renders/megawheel_arena/S04/E095_2026-10-11_smash25d/SIM_SMASH25D_V5_S037_audit.md`
- **Season / seri / seed:** S04 / smash25d / 37
- **Tema / narator:** morning-clear-beach / chatterbox:mw-announcers-m1f1
- **Durasi:** 54.25 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → p2+wreck; Level 2: Grizzly (monster2) → p3+wreck; Level 3 (juara): Tilly (taxi) → win; Level 4: Nitro (f1) → p4+ring
- **Status:** UPLOADED_SCHEDULED 2026-10-31T23:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-10-31T23:00:00Z
- **YouTube:** https://www.youtube.com/shorts/S6FoCd1kejM

## Ep. 96 — `SIM_DOMINO_V2_S003`

- **Judul YouTube:** Can Siren the Police Car Survive A Wave Of Giant Falling Dominoes? 🁢 | Ep. 96 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E096_2026-10-11_domino/SIM_DOMINO_V2_S003.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E096_2026-10-11_domino/SIM_DOMINO_V2_S003.json` · audit: `renders/megawheel_arena/S04/E096_2026-10-11_domino/SIM_DOMINO_V2_S003_audit.md`
- **Season / seri / seed:** S04 / domino / 3
- **Tema / narator:** sunset-clear-beach / chatterbox:f1
- **Durasi:** 50.07 s
- **Tokoh dan hasil:** Level 1: Siren (police) → chop@obs1+broken; Level 2: Titan (bigrig) → chop@obs0+broken; Level 3 (juara): Tilly (taxi) → win
- **Status:** UPLOADED_SCHEDULED 2026-11-01T16:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-11-01T16:00:00Z
- **YouTube:** https://www.youtube.com/shorts/uHkmWJYEZvA

## Ep. 97 — `SIM_PINBALL_V2_S006`

- **Judul YouTube:** Can Zippy the Sports Car Survive Giant Pinball Bumpers Over A Lava Pit? 🔴 | Ep. 97 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E097_2026-10-11_pinball/SIM_PINBALL_V2_S006.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E097_2026-10-11_pinball/SIM_PINBALL_V2_S006.json` · audit: `renders/megawheel_arena/S04/E097_2026-10-11_pinball/SIM_PINBALL_V2_S006_audit.md`
- **Season / seri / seed:** S04 / pinball / 6
- **Tema / narator:** sunset-clear-volcano / chatterbox:m1
- **Durasi:** 57.5 s
- **Tokoh dan hasil:** Level 1: Zippy (sports) → pit@obs1+broken; Level 2: Hydro (firetruck) → pit@obs0+broken; Level 3 (juara): Titan (bigrig) → win
- **Status:** UPLOADED_SCHEDULED 2026-11-02T16:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-11-02T16:00:00Z
- **YouTube:** https://www.youtube.com/shorts/SaMAPLv7ErM

## Ep. 98 — `SIM_DUNGEON_V2_S026`

- **Judul YouTube:** Will Zippy the Sports Car Survive Deadly Dungeon Traps? 🪓🌋 NEW 3D Graphics | Ep. 98 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E098_2026-10-11_dungeon/SIM_DUNGEON_V2_S026.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E098_2026-10-11_dungeon/SIM_DUNGEON_V2_S026.json` · audit: `renders/megawheel_arena/S04/E098_2026-10-11_dungeon/SIM_DUNGEON_V2_S026_audit.md`
- **Season / seri / seed:** S04 / dungeon / 26
- **Tema / narator:** night-clear-volcano / chatterbox:m1
- **Durasi:** 50.1 s
- **Tokoh dan hasil:** Level 1: Zippy (sports) → chop@obs0+broken; Level 2: Sprinkles (icecream) → smash@obs1+broken; Level 3 (juara): Buster (bus) → win
- **Status:** UPLOADED_SCHEDULED 2026-11-03T16:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-11-03T16:00:00Z
- **YouTube:** https://www.youtube.com/shorts/MsN81LV_nP4

## Ep. 99 — `SIM_DUNGEON_V2_S029`

- **Judul YouTube:** Will Siren the Police Car Survive Deadly Dungeon Traps? 🪓🌋 NEW 3D Graphics | Ep. 99 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E099_2026-10-11_dungeon/SIM_DUNGEON_V2_S029.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E099_2026-10-11_dungeon/SIM_DUNGEON_V2_S029.json` · audit: `renders/megawheel_arena/S04/E099_2026-10-11_dungeon/SIM_DUNGEON_V2_S029_audit.md`
- **Season / seri / seed:** S04 / dungeon / 29
- **Tema / narator:** sunset-clear-volcano / chatterbox:m1
- **Durasi:** 51.27 s
- **Tokoh dan hasil:** Level 1: Siren (police) → pit@obs2; Level 2: Titan (bigrig) → chop@obs0+broken; Level 3 (juara): Nitro (f1) → win
- **Status:** UPLOADED_SCHEDULED 2026-11-10T16:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-11-10T16:00:00Z
- **YouTube:** https://www.youtube.com/shorts/-AXUqUCBwBk

## Ep. 100 — `SIM_DUNGEON_V2_S031`

- **Judul YouTube:** Sports Car vs Deadly Dungeon Traps! Can Zippy Make It? 🪓🌋 NEW 3D Graphics | Ep. 100 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E100_2026-10-11_dungeon/SIM_DUNGEON_V2_S031.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E100_2026-10-11_dungeon/SIM_DUNGEON_V2_S031.json` · audit: `renders/megawheel_arena/S04/E100_2026-10-11_dungeon/SIM_DUNGEON_V2_S031_audit.md`
- **Season / seri / seed:** S04 / dungeon / 31
- **Tema / narator:** noon-clear-volcano / chatterbox:f1
- **Durasi:** 57.9 s
- **Tokoh dan hasil:** Level 1: Zippy (sports) → smash@obs1+broken; Level 2: Hydro (firetruck) → pit@obs2+broken; Level 3 (juara): Nitro (f1) → win
- **Status:** UPLOADED_SCHEDULED 2026-11-17T16:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-11-17T16:00:00Z
- **YouTube:** https://www.youtube.com/shorts/30CLnhlfxQI

## Ep. 101 — `SIM_DUNGEON_V2_S032`

- **Judul YouTube:** Will Tilly the Taxi Survive Deadly Dungeon Traps? 🪓🌋 NEW 3D Graphics | Ep. 101 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E101_2026-10-11_dungeon/SIM_DUNGEON_V2_S032.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E101_2026-10-11_dungeon/SIM_DUNGEON_V2_S032.json` · audit: `renders/megawheel_arena/S04/E101_2026-10-11_dungeon/SIM_DUNGEON_V2_S032_audit.md`
- **Season / seri / seed:** S04 / dungeon / 32
- **Tema / narator:** morning-clear-volcano / chatterbox:f1
- **Durasi:** 57.9 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → rollback@obs2+broken; Level 2: Buster (bus) → chop@obs0+broken; Level 3 (juara): Sprinkles (icecream) → win
- **Status:** UPLOADED_SCHEDULED 2026-11-24T16:00:00Z (approve 2026-10-11)
- **Antrian:** SCHEDULED 2026-11-24T16:00:00Z
- **YouTube:** https://www.youtube.com/shorts/zxPurjmlF6w

## Ep. 102 — `SIM_DUNGEON_V2_S038`

- **Judul YouTube:** Can Zippy the Sports Car Survive 5 Deadly Dungeon Traps? 🌋🪓 NEW 3D Graphics | Ep. 102 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E102_2026-10-19_dungeon/SIM_DUNGEON_V2_S038.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E102_2026-10-19_dungeon/SIM_DUNGEON_V2_S038.json` · audit: `renders/megawheel_arena/S04/E102_2026-10-19_dungeon/SIM_DUNGEON_V2_S038_audit.md`
- **Season / seri / seed:** S04 / dungeon / 38
- **Tema / narator:** sunset-clear-volcano / chatterbox:m1
- **Durasi:** 53.33 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → pit@obs2+broken; Level 2: Titan (bigrig) → chop@obs0+broken; Level 3 (juara): Zippy (sports) → win
- **Status:** UPLOADED_SCHEDULED 2026-12-01T16:00:00Z (approve 2026-10-20)
- **Antrian:** SCHEDULED 2026-12-01T16:00:00Z
- **YouTube:** https://www.youtube.com/shorts/U3oGHMwFI0I

## Ep. 103 — `SIM_SPLASH_V2_S013`

- **Judul YouTube:** Cars VS Giant Water Pit: Can Rocky Survive Rainy City? 💦🌧️ NEW 3D Graphics | Ep. 103 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E103_2026-10-19_splash/SIM_SPLASH_V2_S013.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E103_2026-10-19_splash/SIM_SPLASH_V2_S013.json` · audit: `renders/megawheel_arena/S04/E103_2026-10-19_splash/SIM_SPLASH_V2_S013_audit.md`
- **Season / seri / seed:** S04 / splash / 13
- **Tema / narator:** noon-rain-city / chatterbox:f1
- **Durasi:** 59.7 s
- **Tokoh dan hasil:** Level 1: Siren (police) → crash@obs2+broken; Level 2: Hydro (firetruck) → pit@obs0+broken; Level 3 (juara): Rocky (monster) → win
- **Status:** UPLOADED_SCHEDULED 2026-11-04T16:00:00Z (approve 2026-10-20)
- **Antrian:** SCHEDULED 2026-11-04T16:00:00Z
- **YouTube:** https://www.youtube.com/shorts/qLmoNh8nyEU

## Ep. 104 — `MW_SPLASH_3D_S021`

- **Judul YouTube:** Can Siren the Police Car Survive Slippery Splash Zone? 💦🚗 | Ep. 104 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E104_2026-10-22_splash/MW_SPLASH_3D_S021.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E104_2026-10-22_splash/MW_SPLASH_3D_S021.json` · audit: `renders/megawheel_arena/S04/E104_2026-10-22_splash/MW_SPLASH_3D_S021_audit.md`
- **Season / seri / seed:** S04 / splash / 21
- **Tema / narator:** night-clear-city / chatterbox:m1
- **Durasi:** 57.0 s
- **Tokoh dan hasil:** Level 1: Siren (police) → crash@obs1+broken; Level 2: Sprinkles (icecream) → crash@obs1+broken; Level 3 (juara): Buster (bus) → win
- **Status:** UPLOADED_SCHEDULED 2026-11-05T16:00:00Z (approve 2026-10-22)
- **Antrian:** SCHEDULED 2026-11-05T16:00:00Z
- **YouTube:** https://www.youtube.com/shorts/0qVPxSCaBUI

## Ep. 105 — `MW_RACE_3D_S071`

- **Judul YouTube:** We Went 3D! 🔥 Can Titan Survive Falling Containers? | Ep. 105 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E105_2026-11-03_race25d/MW_RACE_3D_S071.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E105_2026-11-03_race25d/MW_RACE_3D_S071.json` · audit: `renders/megawheel_arena/S04/E105_2026-11-03_race25d/MW_RACE_3D_S071_audit.md`
- **Season / seri / seed:** S04 / race25d / 71
- **Tema / narator:** sunset-clear-desert / chatterbox:f1
- **Durasi:** 32.87 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p4+container; Level 2: Grizzly (monster2) → p2; Level 3 (juara): Tilly (taxi) → win+dodge_pothole; Level 4: Nitro (f1) → p3+ufo
- **Status:** UPLOADED_SCHEDULED 2026-11-03T20:00:00Z (approve 2026-11-03)
- **Antrian:** SCHEDULED 2026-11-03T20:00:00Z
- **YouTube:** https://www.youtube.com/shorts/CmFaZq12F6c

## Ep. 106 — `MW_RACE_3D_S072`

- **Judul YouTube:** Nitro vs Falling Containers! Who Wins the Race? 🏁 NEW 3D Graphics | Ep. 106 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E106_2026-11-04_race25d/MW_RACE_3D_S072.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E106_2026-11-04_race25d/MW_RACE_3D_S072.json` · audit: `renders/megawheel_arena/S04/E106_2026-11-04_race25d/MW_RACE_3D_S072_audit.md`
- **Season / seri / seed:** S04 / race25d / 72
- **Tema / narator:** morning-clear-beach / 
- **Durasi:** 34.47 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p4+ufo; Level 2: Rocky (monster) → p3+dragon_ice; Level 3 (juara): Nitro (f1) → p2+container; Level 4: Siren (police) → win
- **Status:** UPLOADED_SCHEDULED 2026-11-04T20:00:00Z (approve 2026-11-04)
- **Antrian:** SCHEDULED 2026-11-04T20:00:00Z
- **YouTube:** https://www.youtube.com/shorts/yEIw_K4Fswo

## Ep. 107 — `MW_RACE_3D_S217`

- **Judul YouTube:** Tilly vs Falling Containers! Who Wins the Race? 🏁 NEW 3D Graphics | Ep. 107 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E107_2026-11-04_race25d/MW_RACE_3D_S217.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E107_2026-11-04_race25d/MW_RACE_3D_S217.json` · audit: `renders/megawheel_arena/S04/E107_2026-11-04_race25d/MW_RACE_3D_S217_audit.md`
- **Season / seri / seed:** S04 / race25d / 217
- **Tema / narator:** night-clear-beach / 
- **Durasi:** 33.83 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → win; Level 2: Rocky (monster) → p2+laser; Level 3 (juara): Tilly (taxi) → p4+container; Level 4: Nitro (f1) → p3+dragon_fire
- **Status:** UPLOADED_SCHEDULED 2026-11-05T20:00:00Z (approve 2026-11-04)
- **Antrian:** SCHEDULED 2026-11-05T20:00:00Z
- **YouTube:** https://www.youtube.com/shorts/GWJc_r7ZF-Q

## Ep. 108 — `MW_RACE_3D_S088`

- **Judul YouTube:** Can Rocky Survive Falling Containers? 🏁 NEW 3D Graphics | Ep. 108 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E108_2026-11-04_race25d/MW_RACE_3D_S088.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E108_2026-11-04_race25d/MW_RACE_3D_S088.json` · audit: `renders/megawheel_arena/S04/E108_2026-11-04_race25d/MW_RACE_3D_S088_audit.md`
- **Season / seri / seed:** S04 / race25d / 88
- **Tema / narator:** morning-rain-countryside / 
- **Durasi:** 33.9 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → win; Level 2: Rocky (monster) → p4+container; Level 3 (juara): Siren (police) → p2+meteor; Level 4: Zippy (sports) → p3+dragon_ice
- **Status:** UPLOADED_SCHEDULED 2026-11-06T20:00:00Z (approve 2026-11-04)
- **Antrian:** SCHEDULED 2026-11-06T20:00:00Z
- **YouTube:** https://www.youtube.com/shorts/MTlsgscsj3Q

## Ep. 109 — `MW_RACE_3D_S108`

- **Judul YouTube:** Will Nitro Make It Past Falling Containers? 🏁 NEW 3D Graphics | Ep. 109 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E109_2026-11-04_race25d/MW_RACE_3D_S108.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E109_2026-11-04_race25d/MW_RACE_3D_S108.json` · audit: `renders/megawheel_arena/S04/E109_2026-11-04_race25d/MW_RACE_3D_S108_audit.md`
- **Season / seri / seed:** S04 / race25d / 108
- **Tema / narator:** sunset-rain-city / 
- **Durasi:** 34.9 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → p2+pothole; Level 2: Grizzly (monster2) → win; Level 3 (juara): Nitro (f1) → p3+container; Level 4: Tilly (taxi) → p4+dragon_ice
- **Status:** APPROVED (approve 2026-11-04)
- **Antrian:** QUEUED 2026-11-07T20:00:00Z
- **YouTube:** belum diupload

## Ep. 110 — `MW_SMASH_3D_S062_R2`

- **Judul YouTube:** 4 Cars Enter the Ice Arena! Who Survives? 💥 NEW 3D Graphics | Ep. 110 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E110_2026-11-04_smash25d/MW_SMASH_3D_S062_R2.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E110_2026-11-04_smash25d/MW_SMASH_3D_S062_R2.json` · audit: `renders/megawheel_arena/S04/E110_2026-11-04_smash25d/MW_SMASH_3D_S062_R2_audit.md`
- **Season / seri / seed:** S04 / smash25d / 62
- **Tema / narator:** noon-clear-mountains / 
- **Durasi:** 58.23 s
- **Tokoh dan hasil:** Level 1: Hydro (firetruck) → win; Level 2: Grizzly (monster2) → p4+wreck; Level 3 (juara): Tilly (taxi) → p3+wreck; Level 4: Zippy (sports) → p2+wreck
- **Status:** UPLOADED_SCHEDULED 2026-11-05T00:00:00Z (approve 2026-11-04)
- **Antrian:** SCHEDULED 2026-11-05T00:00:00Z
- **YouTube:** https://www.youtube.com/shorts/UTVc7gPmdkI

## Ep. 111 — `MW_SMASH_3D_S043_R2`

- **Judul YouTube:** 4 Cars Enter the Lava Arena! Who Survives? 💥 NEW 3D Graphics | Ep. 111 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E111_2026-11-04_smash25d/MW_SMASH_3D_S043_R2.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E111_2026-11-04_smash25d/MW_SMASH_3D_S043_R2.json` · audit: `renders/megawheel_arena/S04/E111_2026-11-04_smash25d/MW_SMASH_3D_S043_R2_audit.md`
- **Season / seri / seed:** S04 / smash25d / 43
- **Tema / narator:** night-rain-countryside / 
- **Durasi:** 56.93 s
- **Tokoh dan hasil:** Level 1: Titan (bigrig) → p4+wreck; Level 2: Rocky (monster) → win; Level 3 (juara): Zippy (sports) → p3+wreck; Level 4: Tilly (taxi) → p2+wreck
- **Status:** UPLOADED_SCHEDULED 2026-11-06T00:00:00Z (approve 2026-11-04)
- **Antrian:** SCHEDULED 2026-11-06T00:00:00Z
- **YouTube:** https://www.youtube.com/shorts/_VvjsGfjf0s

## Ep. 112 — `MW_SMASH_3D_S039_R2`

- **Judul YouTube:** 4 Cars Enter the Mud Arena! Who Survives? 💥 NEW 3D Graphics | Ep. 112 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E112_2026-11-04_smash25d/MW_SMASH_3D_S039_R2.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E112_2026-11-04_smash25d/MW_SMASH_3D_S039_R2.json` · audit: `renders/megawheel_arena/S04/E112_2026-11-04_smash25d/MW_SMASH_3D_S039_R2_audit.md`
- **Season / seri / seed:** S04 / smash25d / 39
- **Tema / narator:** morning-clear-desert / 
- **Durasi:** 58.7 s
- **Tokoh dan hasil:** Level 1: Buster (bus) → win; Level 2: Grizzly (monster2) → p4+wreck; Level 3 (juara): Siren (police) → p3+wreck; Level 4: Nitro (f1) → p2+wreck
- **Status:** UPLOADED_SCHEDULED 2026-11-07T00:00:00Z (approve 2026-11-04)
- **Antrian:** SCHEDULED 2026-11-07T00:00:00Z
- **YouTube:** https://www.youtube.com/shorts/TK2avDRy0aM

## Ep. 113 — `MW_BUMPS_3D_S040`

- **Judul YouTube:** Can Tilly Survive Giant Speed Bumps? 🚗💥 NEW 3D Graphics | Ep. 113 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E113_2026-11-05_bumps/MW_BUMPS_3D_S040.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E113_2026-11-05_bumps/MW_BUMPS_3D_S040.json` · audit: `renders/megawheel_arena/S04/E113_2026-11-05_bumps/MW_BUMPS_3D_S040_audit.md`
- **Season / seri / seed:** S04 / bumps / 40
- **Tema / narator:** noon-clear-countryside / 
- **Durasi:** 51.7 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → flip@obs0; Level 2: Titan (bigrig) → stuck@obs1; Level 3 (juara): Grizzly (monster2) → win
- **Status:** UPLOADED_SCHEDULED 2026-11-06T16:00:00Z (approve 2026-11-05)
- **Antrian:** SCHEDULED 2026-11-06T16:00:00Z
- **YouTube:** https://www.youtube.com/shorts/M-eAqay4M4Q

## Ep. 114 — `MW_POTHOLES_3D_S041`

- **Judul YouTube:** Will Zippy the Sports Car Survive Giant Potholes? 🚗💥 NEW 3D Graphics | Ep. 114 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E114_2026-11-05_potholes/MW_POTHOLES_3D_S041.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E114_2026-11-05_potholes/MW_POTHOLES_3D_S041.json` · audit: `renders/megawheel_arena/S04/E114_2026-11-05_potholes/MW_POTHOLES_3D_S041_audit.md`
- **Season / seri / seed:** S04 / potholes / 41
- **Tema / narator:** night-clear-mountains / 
- **Durasi:** 47.57 s
- **Tokoh dan hasil:** Level 1: Zippy (sports) → pit@obs0; Level 2: Hydro (firetruck) → stuck@obs1; Level 3 (juara): Titan (bigrig) → win
- **Status:** APPROVED (approve 2026-11-05)
- **Antrian:** QUEUED 2026-11-07T16:00:00Z
- **YouTube:** belum diupload

## Ep. 115 — `MW_LAVA_3D_S043`

- **Judul YouTube:** Race Car vs Erupting Lava Road! Can Nitro Make It? 🌋🔥 NEW 3D Graphics | Ep. 115 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E115_2026-11-05_lava/MW_LAVA_3D_S043.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E115_2026-11-05_lava/MW_LAVA_3D_S043.json` · audit: `renders/megawheel_arena/S04/E115_2026-11-05_lava/MW_LAVA_3D_S043_audit.md`
- **Season / seri / seed:** S04 / lava / 43
- **Tema / narator:** morning-clear-volcano / 
- **Durasi:** 49.9 s
- **Tokoh dan hasil:** Level 1: Nitro (f1) → pit@obs0; Level 2: Buster (bus) → rollback@obs1; Level 3 (juara): Hydro (firetruck) → win
- **Status:** APPROVED (approve 2026-11-05)
- **Antrian:** QUEUED 2026-11-08T16:00:00Z
- **YouTube:** belum diupload

## Ep. 116 — `MW_POTHOLES_3D_S124`

- **Judul YouTube:** Can Tilly Survive Giant Potholes? 🚗💥 NEW 3D Graphics | Ep. 116 #Shorts
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S04/E116_2026-11-05_potholes/MW_POTHOLES_3D_S124.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S04/E116_2026-11-05_potholes/MW_POTHOLES_3D_S124.json` · audit: `renders/megawheel_arena/S04/E116_2026-11-05_potholes/MW_POTHOLES_3D_S124_audit.md`
- **Season / seri / seed:** S04 / potholes / 124
- **Tema / narator:** night-snow-mountains / 
- **Durasi:** 52.4 s
- **Tokoh dan hasil:** Level 1: Tilly (taxi) → rollback@obs0; Level 2: Titan (bigrig) → stuck@obs1; Level 3 (juara): Buster (bus) → win
- **Status:** APPROVED (approve 2026-11-05)
- **Antrian:** QUEUED 2026-11-09T16:00:00Z
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
- **Status:** UPLOADED_SCHEDULED 2026-10-11T17:00:00Z (approve 2026-10-07)
- **Antrian:** SCHEDULED 2026-10-11T17:00:00Z
- **YouTube:** https://www.youtube.com/shorts/SdByNtxACP4

## Ep. 1003 — `2026-10-23_story15_e03`

- **Judul YouTube:** The Forgotten Speedway: Can They Escape the Broken Bridge? | MegaWheel Arena Ep. 3
- **File MP4:** `/root/video-engine/renders/megawheel_arena/S01/STORY_1003_2026-10-23_story15/2026-10-23_story15_e03.mp4`
- **Manifest:** `/root/video-engine/renders/megawheel_arena/S01/STORY_1003_2026-10-23_story15/2026-10-23_story15_e03.json` · audit: `renders/megawheel_arena/S01/STORY_1003_2026-10-23_story15/2026-10-23_story15_e03_audit.md`
- **Season / seri / seed:** S01 / story15 / 3
- **Tema / narator:**  / 
- **Durasi:** 589.164 s
- **Tokoh dan hasil:** Level 1: Sprinkles (icecream) → story15; Level 2: Zippy (sports) → ; Level 3 (juara): Rocky (monster) → ; Level 4: Buster (bus) → ; Level 5: Siren (police) → ; Level 6: Nitro (f1) → ; Level 7: Hydro (firetruck) → 
- **Status:** UPLOADED_SCHEDULED 2026-10-25T17:00:00Z (approve 2026-10-23)
- **Antrian:** SCHEDULED 2026-10-25T17:00:00Z
- **YouTube:** https://www.youtube.com/shorts/3wtRIEEN4WY

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
- **Status:** UPLOADED_SCHEDULED 2026-10-07T12:00:00Z (approve 2026-10-07)
- **Antrian:** SCHEDULED 2026-10-07T12:00:00Z
- **YouTube:** https://www.youtube.com/shorts/v4oErNoDW64
