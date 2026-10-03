# CONFIG_BEST — setelan terbaik yang berlaku (satu sumber kebenaran)

> Permintaan user 2026-10-03: log perubahan & setelan supaya tidak mengulang kesalahan dan konfigurasi terbaik
> mudah dilacak. **Aturan:** setiap kali setelan yang disetujui user berubah, perbarui baris di sini (nilai, lokasi,
> tanggal, alasan). Riwayat perubahan kode otomatis: `CHANGELOG.md` (tools/make_changelog.py, cron harian).
> Kesalahan rinci: `ERROR_LOG.md`. Kredensial: **hanya lokasi** dicatat di sini, isinya tidak pernah.

## 1. Publikasi (produksi)
| Setelan | Nilai terbaik | Lokasi | Sejak / alasan |
|---|---|---|---|
| Slot Shorts (ET) | 11:00 CHALLENGE · 15:00 RACE · 19:00 SMASH (ketat, tanpa substitusi) | `publish_queue.py` SLOTS | 2026-10-01 user |
| Episode panjang | Minggu 13:00 ET (Senin 00:00 WIB), nomor story 1000+N | `publish_queue.py` WEEKLY_LONG_SLOT, `episodes.py` STORY_SERIES | 2026-10-01/02 user |
| Trailer episode | Short tambahan jam tetap (Ep.1: Sab 17:00 ET), nomor 1500+N, `publish_at_et` | PROMO_SERIES | 2026-10-02 user (jarak 2 jam dari slot lain) |
| Video panjang | diupload **tanpa** #Shorts | `youtube_uploader.upload_shorts(shorts=False)` | 2026-10-02 bug fix |
| Audiens | Jalur A: general audience, made_for_kids=False, tanpa kata kids/children | BLUEPRINT §12 | 2026-10-02 user |
| Kredit deskripsi | `🎬 Produced by Infrasoft Media & Tech` (otomatis saat upload) | `episodes.with_credit()` | 2026-10-02 user |
| Watermark | **tidak** dibakar di video; YouTube Studio Branding, waktu tampil "Akhir video" | BLUEPRINT §11 | 2026-10-02 user |
| Cron upload | 05:00 UTC (12:00 WIB) `daily_publish.sh`, flock, max 5 upload/run | crontab VM 99.3 | 2026-10-01 |
| Cron analytics | 06:30 UTC (13:30 WIB) `analytics_daily.sh` → ANALYTICS_TELEGRAM.txt / LATEST.json | crontab VM 99.3 | 2026-10-03 user (bot 14:00 WIB) |
| Stok | 7 hari per tipe | STOCK_DAYS | 2026-10-01 |

## 2. Suara
| Setelan | Nilai | Lokasi | Catatan |
|---|---|---|---|
| Narator | "voice C": Chatterbox (MIT) di Modal L4, ref sintetis m1 (pria) / f1 (wanita), en-US | `generators/voice/` | 2026-10-01 user "paling oke" |
| QA suara | Whisper base.en, skor huruf ≥ 0,85 (retake ≤ 4), cache ditolak < 0,75 | `modal_tts.py`, `announcer.py` | "GO" → "Geo" dulu |
| Start | "Ready... set... let's go!" (bukan "GO!") | sim_engine READY_SET_GO | 2026-10-01 |
| Mix Shorts | VOL narasi 1.60 · mesin 0.85 · SFX 0.85, duck 8 dB · **tanpa musik latar** (`SHORTS_BGM = False`); lagu tema remix3 (chorus 13,5 dtk) sayup **setelah sorak menang** (`music_bed`) | sim_engine.py | 2026-10-03 user: narator cukup, backsound bikin ramai |
| Loudness | -16 LUFS, TP -1.5 (story per scene); stereo untuk lagu tema | story25d | |
| Lip-sync story | Rhubarb Lip Sync (MIT, build ARM di `/root/tools/rhubarb-lip-sync`), 8 bentuk mulut | story25d `visemes()` | 2026-10-03; fallback mulut volume |
| Budget Modal | $29/bulan, ledger `modal_usage.json` (catat manual bila run crash) | modal_*.py | |

## 3. Musik
| Setelan | Nilai | Catatan |
|---|---|---|
| Generator | ACE-Step v1 3.5B (Apache-2.0), infer_step 60, guidance 15, keep top-N take untuk dipilih telinga | YuE2 = CC BY-NC (❌), YuE v1 lambat tanpa flash-attn (ditunda) |
| Intro Ep.1 | v1 take asli + remix Demucs **musik ×1.7 / vokal ×0.55**, stereo `width 1.6` | `intro_v1_remix3.json`; ×1.5/0.8 pada take v2 terdengar kurang smooth |
| Outro | v2 (60 dtk) | disetujui user |
| Sonic logo | `branding/music/sonic_logo*.wav` 3,8 dtk ("Mega, Mega, MegaWheel"), dipakai saat menang (RACE v3) | 2026-10-03 |
| Lagu Grandpa | jingle music-box orisinal (`story25d.jingle()`), "ding" = frasa pertamanya | user: jangan "ting-tong" |

## 4. Mesin Shorts
| Mesin | Versi terbaik | Kunci |
|---|---|---|
| CHALLENGE (`sim_engine.py`) | v3.9: durasi 44–57 dtk (cek 40–58), voice C, READY-GO | posisi rintangan acak masih backlog (C13) |
| RACE (`race25d.py`) | **v3** (2026-10-03, render uji lolos, belum dinilai visual): sirkuit melengkung amp 0,9–1,4, palu/kontainer/oli, judul pertanyaan + teks frame 1, sonic logo | v2 = versi tayang minggu 1 |
| SMASH (`smash25d.py`) | v4: duo komentator m1+f1, intro, chaos (misil/Kraggor/UFO/retak) | mobil terakhir tidak pernah tereliminasi di tick yang sama |

## 5. Mesin story (episode panjang)
| Setelan | Nilai | Alasan |
|---|---|---|
| Urutan | cold open → **black 2.0** → ident logo → lagu tema → **black 2.6** → cerita | retensi (riset) + user: jangan tumpang tindih |
| Transisi | XF_DUR: dissolve 2.0, fadeblack 1.8, fadewhite 1.4, fade 1.8, lainnya 1.4–1.6 | user: jangan terburu-buru |
| Kamera | glide antar-shot ±1.8 dtk (maks 45% shot), close = seluruh mobil, low = seluruh kendaraan | review v6–v8 |
| Jeda akhir scene | end_hold 1.4 dtk (masuk ke freeze bila ada) | user v7 |
| Tempo dialog | gap 0.55, tail 0.8 | dracin pacing |
| Efek kaget | **tanpa suara** (punch/triple/freeze diam) | user v7 |
| Ambience | crowd 0.05 · burung 0.035 · jangkrik 0.03 · room 0.03 | standar 5 lapis suara |
| Audit | `audit_story.py` harus 0 ERROR sebelum render | wajah tertutup, framing, keyword |
| Guard render | VM HEAD == origin/main, else STOP | render v7 pernah pakai kode lama |
| Output | chapters otomatis, end screen 14 dtk, trailer 9:16 (kartu jam tayang ditahan 6 dtk) | |

## 6. Lab (eksperimen — bukan produksi)
| Setelan | Nilai |
|---|---|
| Godot | 4.4.1 ARM64 `/root/tools/godot`, `xvfb-run` + `gl_compatibility`, Movie Maker `--fixed-fps 30`, cek parse `--headless` dulu |
| Aturan Godot | slow-mo ≤ 1×/video · zoom ≥ 1.0 · kamera per momen · CCD · `call_deferred` di callback · hindari `:=` dari Variant |
| Metode A | frame cairo asli + lapisan FX Godot (`lab/godot_fx`), cue posisi dari hook tanpa ubah produksi |
| SFX | Sonniss GDC di `/root/lab/sfx/` (unduh pakai UA browser + referer); bank `sfx_bank.py` → `/root/lab/sfx/bank/` |
| Metode A | ❌ ditolak user ("tidak kerasa bedanya") |
| Metode B (3D) v4 | `lab/godot3d_smash`, default `cam=classic`: geometri kamera & arena 26×10 m **identik smash25d** (60 px/m depan, zoom 1,0–1,45, pan), platform baja di atas air + hiu, kerusakan bertahap + POW + hit-stop 3 frame, replay di mix3d; v3 `cam=topdown` 20×24 m sebagai alternatif |
| Durasi/logika SMASH 3D | video 30–40 dtk (user 2026-10-03); logika menang smash25d (barrier 9 dtk, jatuh hanya bila didorong, lantai menyusut 18/+7 dtk, mobil terakhir selamat, batas waktu 27 dtk → HP terbanyak) + jarak KO ≥ 4,5 dtk — lihat SCALE_STANDARD §6 |
| Chaos | **satu tema per video** (meteor / kraggor / missile, bergiliran antar episode); hujan meteor = 3 batu, maks 1 KO |

## 7. Kredensial (lokasi saja — jangan pernah di-commit)
`credentials/` di VM 99.3 (git-ignored, dicek bersih 2026-10-03): YouTube upload token, YouTube Analytics token
(terpisah), client secrets, Drive token. `modal.txt` jangan dibuka. Token Telegram hanya di VM 99.2.

## 8. Pelajaran — jangan diulang (rinci di ERROR_LOG.md)
1. `git_sync pull` terhalang file untracked/dirty → selalu `git_sync push` dulu, lalu pull, lalu cek HEAD == origin.
2. `pgrep -f` di dalam `ssh '...'` bisa membunuh sesi sendiri → tulis skrip stop ke file, jalankan file.
3. Heredoc + `"\n"` di patch Python bisa jadi baris baru sungguhan → tulis patch sebagai file (Write), bukan heredoc.
4. Proses Modal bisa menggantung → selalu `timeout`; catat ledger bila run crash.
5. Uji koneksi ke server OAuth lokal (curl) memakai server-nya → jangan diuji, langsung beri link.
6. Dua sesi agent di file yang sama → cek `git log` sebelum patch; jangan timpa.
7. Klip lebih pendek dari total transisinya → assemble memeriksa durasi part vs transisi.
8. Sampel/eksperimen wajib mengikuti format tayang (kamera, rasio mobil, HUD) — jangan membuat format baru.
9. Ukuran jangan ditebak: semua dimensi (mobil, arena, px/m, zona layar) ada di `SCALE_STANDARD.md`; render Godot
   wajib mencetak `SCALE` dan lolos toleransinya.
10. Cahaya 3D: matahari siang dari sisi kamera (Godot `sun.rotation_degrees = (-55, 140, 0)`), supaya bayangan jatuh
    menjauhi kamera. Jangan mematikan bayangan untuk menutupi arah cahaya yang salah (kecuali memang adegan sore).
    Mobil berbentuk kartu tetap diberi bayangan elips di bawahnya, seperti di cairo.
