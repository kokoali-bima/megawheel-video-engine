# HANDOVER - CHALLENGE Shorts di mesin story3d (dibuat 2026-10-07)

Pemilik: "kita belum punya video short challenge yang menggunakan engine baru"; "tokohnya di rotasi, kita ada 10 tokoh, jangan
itu2 aja"; "rintangannya tidak boleh pernah sama (boleh ide baru: dungeon)"; "kita memakai engine baru, gaya backsound baru";
"kalau perlu kasi notice di judul (grafisnya baru)".

## Aturan (wajib)
1. Rotasi 10 tokoh (zippy sports, siren police, buster bus, hydro firetruck, rocky monster, grizzly monster2, nitro f1,
   tilly taxi, titan bigrig, sprinkles icecream): pilih yang PALING JARANG dipakai di Short sebelumnya (cek PRODUCTION_REGISTRY.json).
   CH01 = Siren (kena kapak 1), Rocky (kena kapak 2), Grizzly (menang).
2. Rintangan TIDAK PERNAH sama dengan yang lama. Terpakai: lihat daftar di bawah. CH01 = kapak dungeon vertikal.
3. Judul memuat "NEW 3D Graphics" (<=100 karakter, tanpa kata kids/children), en-US; deskripsi menyebut grafis 3D baru.
4. Musik gaya A10 (jarang, pelan, tonal): CH01 hanya pada run gagal + hasil menang; lint ERROR >60% shot.
5. Hasil tiap level DISIMULASI (gen_challenge_axes.py) - fail = tabrakan nyata, menang = lolos nyata; sfx jatuh pada slam nyata.
6. Vertikal 9:16 (`--aspect v`, 1080x1920): HUD (judul, pil level, bar progres + tanda kapak, badge FAIL/WINNER, confetti,
   kartu LIKE/SUBSCRIBE) digambar story25d `draw_challenge_hud`; kapak digambar cairo (`draw_chop`) di DEPAN mobil.
7. Jangan upload/antri sebelum pemilik review. Upload hanya oleh cron `daily_publish.sh`.

## Rintangan terpakai (Short lama, jangan ulang)
lihat PRODUCTION_REGISTRY.json / EPISODES_INDEX.md; story3d: dungeon axes (CH01).

## Perintah
```
python generators/story3d/tools/gen_challenge_axes.py --episode CH01_dungeon_axes --cast police,monster,monster2
python generators/story3d/validate_scene.py --episode CH01_dungeon_axes --scenes 1
# VM: bash git_sync.sh pull ; venv/bin/python generators/story3d/produce_story3d.py --episode CH01_dungeon_axes --scenes 1 --aspect v
```
Biaya render ~USD 0.06. Kode: story25d.py (draw_chop, chop_bottom, draw_challenge_hud, SFX chop_slam/chop_whoosh/car_boing/chain_rattle),
story3d.gd `_dungeon()`, validate_scene (location dungeon, prop chop, shot key hud/interrupt), STYLE_CONTRACT.

## Status CH01 (akhir sesi)
- v3 (gauntlet kapak+lahar+ogre, tabrakan BeamNG-style) QA PASS, di Drive; generator = gen_challenge_dungeon.py (gen_challenge_axes.py = versi lama).
- BELUM: kirim ke Drive untuk review, daftarkan sebagai video PENDING (register_story.py, seri baru -> peran "short" 11:00 ET),
  judul contoh `Cars VS Dungeon Axes! Who Survives? NEW 3D Graphics | Ep. N #Shorts`.
- Publikasi Ep.2 (1002, Min 2026-10-11 13:00 ET) dan trailer (1502, Rab 2026-10-07 08:00 ET) sudah antri; cek
  work/daily_publish.log + `publish_queue.py show` setelah cron 05:00 UTC (en-US; thumbnail custom - kalau "Thumbnail NOT set",
  pasang REVIEW_THUMBNAIL_CUSTOM_EP2.jpg manual di YouTube Studio).

## ARAH BARU (owner 2026-10-07, setelah review CH01 v4) - BACA INI DULU
Pemilik: "ikutin format yang ada; kalau masuk kumpulan lava -> group lava, sambung penomoran episode; evaluasi dengan challenge lama;
tetap format backsound, banyaknya level, banyaknya rintangan, tingkat kesulitan, efek mobil di tanjakan (cara melompat) HARUS LEBIH REAL;
lihat file-file belum-upload untuk masuk lava; jangan banyak berubah selain grafis, kecuali baru + lebih menarik (target: menyaingi BeamNG);
SLOW MOTION = kekuatan kita, JANGAN diubah."
Artinya CH01 v4 (skrip tangan gen_challenge_dungeon.py) HANYA prototipe visual. Produksi harus lewat FORMAT CHALLENGE yang sudah tayang:

| Aspek | Format challenge lama (sim_engine.py, lihat renders/.../S02/E036_*lava_potholes/*.json + audit.md) | CH01 v4 (salah) |
|---|---|---|
| Level | 3 level: fail, fail, win (STORY); gagal <=20 s, menang(+outro) <=24 s; total 40-58 s; cold open 1.5 s | 4 level, 60 s |
| Rintangan | >=2 rintangan, biasanya 3-5 (pit/vent/ramp+pit), tiap level gagal di rintangan BERBEDA; hazard pertama ~30-35 m, finish ~100 m; kesulitan naik (pit kecil -> vent bertimer -> ramp + pit lebar 6.5-9 m, dalam 4.5-5.5) | 3 jenis, jarak bebas |
| Fisika | pymunk di sim_engine (simulate/build_space/spawn): hasil dari fisika asli (runs_for/pick_combo cari kecepatan untuk hasil yang diinginkan); mobil rusak (break_car: roda copot, serpihan) | skrip tangan (simulasi sederhana) |
| Lompat | kicker kayu panjang 5-7 m tinggi 1.1-1.7; terbang balistik asli, bullet-time pada lompatan besar | parabola buatan |
| Lava | masuk pit lava = tenggelam kental + MELT (badan melorot, lelehan logam), blast api, SFX gloop/api/blorp (synth_lava_plunge) | mobil dipantulkan keluar |
| Slow motion | bullet-time (jendela udara tertinggi) + INSTANT REPLAY 0.4x (REPLAY_SPEED) minimal 1 level gagal; narasi "Let's see that again, in slow motion!" | TIDAK ADA |
| Backsound | SHORTS_BGM=False: tanpa musik latar; narator + mesin + SFX; lagu tema (intro_lets_go_v1mix3.wav, chorus mulai 13.5 s) pelan SETELAH sorak menang | cue A10 tension (SALAH untuk Short) |
| Narasi | "Ready... Go! Level one! <Nama>! <teaser>?" x3, hasil per level ("Oh no! X fell into the lava and is melting!"), replay line, CTA baku "Tap LIKE if you enjoyed..." | 9 baris lain |
| Judul/deskripsi | "<Judul seri> ... | Ep. N #Shorts"; deskripsi template ("Watch till the end for the slow-motion replay! ...") di sim_engine (~baris 3724) | - |
| Penomoran | episode Short global 1..51 tanpa celah -> CH baru = **Ep. 52**; seri baru "dungeon" (peran short 11:00 ET) atau group lava | - |

RENCANA (rekomendasi, belum dikerjakan):
1. Tambah seri `dungeon` di sim_engine (SERIES_DEFS + make_dungeon_track): rintangan fisika baru = KAPAK bertimer (benda kinematik pymunk, mirip VENTS), OGRE bergada (kinematik, ayun), ramp + pit lahar (sudah ada). 3 level fail/fail/win, 4-5 rintangan, kesulitan naik. Jangan ubah seri lain (jalankan test_all.sh).
2. Narasi/judul/deskripsi/backsound/slow-mo/audit semua diwarisi sim_engine (tidak ditulis ulang).
3. Grafis baru: pakai jalur lab/godot3d_challenge (export_challenge.py: sim_engine memutuskan SEMUA, Godot hanya menggambar ulang dunia 3D + overlay.mov HUD + mix.wav) -> tambah tema dungeon (porting _dungeon/obor/lahar dari generators/story3d/project/story3d.gd) + kapak/ogre 3D; kerusakan mobil gaya BeamNG dari data physics (roda copot, remuk di ujung kena), selaras aturan "mobil logam kaku, garis lurus".
4. Daftar pending (episode 52), review pemilik, baru antri. Jangan upload sebelum review.
Efek yang SUDAH dibuat di story25d/story3d (draw_impact, crumple, ballistic, draw_ogre, draw_lava, ramp prism Godot) boleh dipakai ulang di langkah 3.

## STATUS 2026-10-07 (malam) - SELESAI mengikuti format lama
- Seri baru `dungeon` ditambahkan ke `generators/physics_2d/sim_engine.py` (jangan tulis engine baru - BLUEPRINT Aturan Nol): kapak bertimer (AXES, `axe_bottom`),
  ogre bergada (OGRES, `ogre_arm`), ramp + pit lahar (pakai yang lama), 5 rintangan [axe, ogre, ramp+lava, axe, axe], 3 level fail/fail/win, slow-mo
  + bullet-time + replay warisan engine, narasi/judul/deskripsi/audit warisan ("NEW 3D Graphics" lewat `title_notice`). Penyetel: `tune_dungeon.py`,
  `find_seeds.sh dungeon 1 40` (lolos ~55%; seed lolos: 2 6 8 10 11 12 14 15 16 17 18 19 21 26 28 29 30 32 33 36).
- Grafis 3D: `lab/godot3d_challenge/` (export_challenge.py + project/challenge3d.gd): aula dungeon bata + obor, kapak 3D, ogre 3D, mobil gepeng
  (frame key `crush`), penampang batu. Konversi resmi: `venv/bin/python lab/godot3d_challenge/convert3d.py <VIDEO_ID>` (audit 3D + audit produksi + Drive).
- Video: **SIM_DUNGEON_V2_S015** (Tilly: smash@ogre -> jatuh ke lahar, Titan: chop@kapak, Siren: menang lompat ramp) status RENDERED_PENDING_APPROVAL,
  3D + kedua audit LULUS, di Drive `ipandu-video/review/SIM_DUNGEON_V2_S015.mp4` (+ `_sheet.png`), 2.5D disimpan `_25d.mp4` di folder pending VM.
- Berikutnya: pemilik review -> `episodes.py approve SIM_DUNGEON_V2_S015` (HANYA setelah "approved" eksplisit; jadi **Ep. 52**) -> `publish_queue.py plan`.
- CH01 v4 (skrip tangan story3d, folder story3d/CH01_dungeon_axes) = prototipe, JANGAN dipakai/diunggah.
