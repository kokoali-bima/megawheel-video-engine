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
