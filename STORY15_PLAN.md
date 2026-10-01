# STORY15 — Rencana video cerita mingguan MegaWheel Arena

> Dokumen induk untuk seri cerita panjang (series id `story15`). Disimpan di git sebagai bagian dari sejarah channel.
> Disusun oleh Claude Code (Opus) bersama user, 2026-10-01. Setiap keputusan baru dicatat di bagian "Riwayat keputusan".
> Dokumen terkait: BLUEPRINT.md (aturan channel), **CHARACTERS.md (character bible)**, PROJECT_PROGRESS.md (C9, C12, C15), EPISODES_INDEX.md.

## 1. Tujuan

- Cerita yang **menyentuh emosi anak-anak dan orang dewasa sekaligus**, seperti film Cars (Pixar): anak menikmati aksi
  dan slapstick, orang dewasa terikat pada hati ceritanya (persahabatan, gagal lalu bangkit, rival jadi sahabat).
- Membangun **jalur fans**: tokoh punya sejarah, rivalitas, dan rekor. Setiap kemenangan punya bobot karena ada ceritanya.
- Mendukung monetisasi: video panjang menambah jam tayang (jalur YPP 4.000 jam tayang).
- Jadwal tayang: **Minggu 13:00 ET** (slot sendiri, terpisah dari Shorts 11:00 / 15:00 / 19:00).

## 2. Format: "drama China" (dracin), usulan user 2026-10-01

Satu episode mingguan berdurasi **±15 menit = 15 scene × ±1 menit**.

| Prinsip | Penjelasan |
|---|---|
| **Scene = unit produksi** | Setiap scene dirender sendiri (±1 menit, ±2–4 menit render di VM). Kalau ada yang perlu diperbaiki, cukup render ulang scene itu, bukan 15 menit penuh. |
| **Setiap scene berakhir dengan "kait"** | Pertanyaan, kejutan, atau emosi yang menggantung, sehingga penonton ingin lanjut ke scene berikutnya. |
| **Dirakit jadi satu video 15 menit** | Scene disambung dengan transisi halus (musik tidak putus), plus **chapter YouTube** (timestamp per scene). |
| **Kontinuitas antar scene** | Setiap scene mencatat keadaan awal dan akhir (lokasi, waktu, cuaca, posisi tokoh, emosi), dan scene berikutnya mulai dari keadaan itu. |
| **Bisa dipecah jadi Shorts** (opsional, keputusan user) | Setiap scene bisa ditayangkan sebagai Shorts "Part N" berisi ringkasan 2 detik di awal dan kait di akhir, seperti format drama pendek yang viral. |

**Catatan supaya 15 menit tidak terasa terpotong-potong:** kait setiap 1 menit dibuat **halus** (cukup satu pertanyaan
atau momen kecil). Kait besar hanya di akhir babak (scene 4, 10, 15).

## 3. Struktur cerita per episode (15 scene)

| Scene | Babak | Isi |
|---|---|---|
| 1 | Pembuka | Momen paling seru atau mengharukan dulu sebagai kait, lalu judul |
| 2–4 | Babak 1 | Dunia tokoh, mimpi atau masalahnya. Scene 4: kait besar (masalah muncul) |
| 5–10 | Babak 2 | Latihan, gagal, konflik, bantuan teman, Kraggor mengacau. Scene 10: titik terendah (kait besar) |
| 11–14 | Babak 3 | Bangkit. Final balapan / SMASH memakai engine kita, lalu momen haru |
| 15 | Penutup | Pesan hangat, klasemen liga, cuplikan minggu depan (kait besar) |

## 4. Benang merah antar minggu (musim)

- **Liga musiman** (PROJECT_PROGRESS C12): hasil Shorts harian memberi poin, dan klasemen muncul di cerita mingguan.
- **Rivalitas tetap**: misalnya Zippy (cepat, sombong) vs Rocky (kuat, rendah hati).
- **KRAGGOR**: kaiju desain sendiri, penjahat tetap yang makin kuat; misterinya terungkap pelan-pelan.
- **Kisah latar tokoh**: bergiliran, misalnya masa kecil Sprinkles.
- **Rekor dan sejarah**: "Grizzly sudah 3× juara SMASH", disebut di cerita dan di Shorts.

Usulan episode pertama: **"Sprinkles' First Race"**. Truk es krim yang diremehkan tapi pantang menyerah.

## 5. Bahasa sinematik (engine 2.5D sendiri, gratis di CPU VM)

| Shot | Efek emosional | Cara di engine |
|---|---|---|
| Close-up / extreme close-up wajah & mata | Penonton merasakan emosi tokoh | Wajah vektor tetap tajam walau zoom 4× |
| POV / first-person (pandangan pengemudi) | Ikut merasakan ngebut | Jalan pseudo-3D ala game balap klasik |
| Low-angle hero shot | Tokoh tampak gagah saat bangkit | Kamera rendah + zoom |
| Over-the-shoulder | Percakapan dua tokoh | Tokoh depan buram, lawan bicara tajam |
| Slow motion + latar buram | Momen penting terasa besar | Lapisan latar di-blur |
| Cahaya bersuasana (senja, hujan, malam) | Sedih, tegang, haru | Sistem tema yang sudah ada |
| Letterbox (bar hitam) | Rasa "film" | Overlay |

Perlu dikembangkan: **emosi wajah baru** (sedih/menangis dengan air mata, bertekad, tertawa, malu, mengantuk), kedipan
mata, dan **gerak mulut** saat bicara.

## 6. Suara

- **Tokoh bersuara** (lebih mengikat secara emosional, keputusan user). Setiap tokoh punya referensi suara sintetis sendiri
  di Chatterbox (`branding/voice/`), misalnya Buster berat & pelan, Zippy cepat & sombong, Sprinkles ceria. Semuanya rancangan sendiri,
  bukan tiruan orang sungguhan, en-US.
- **Aturan usia suara (user 2026-10-01):** tokoh yang masih kecil sekali = suara anak; remaja = suara remaja;
  dewasa = suara dewasa. Narator selalu dewasa (suara C).
- **Emosi per kalimat:** parameter ekspresi Chatterbox (sedih lebih lembut, marah/senang lebih kuat).
- **QA otomatis:** setiap take ditranskrip Whisper dan dibuat ulang kalau tidak cocok (sudah berjalan untuk Shorts).
- **Gerak mulut (lip-sync)** mengikuti volume suara, cukup meyakinkan untuk gaya kartun.
- **Subtitle di layar:** untuk anak, penonton yang menonton tanpa suara, dan penonton non-native.
- **Musik:** skor emosional (piano / string sintetis) per suasana, efek suara dari engine.

## 7. Alur produksi

```
naskah (Claude menulis)  ->  USER MENYETUJUI naskah  ->  shotlist per scene (JSON)  ->  render per scene
  ->  suara + musik + efek  ->  QA otomatis per scene  ->  rakit 15 menit + chapter  ->  Drive review/
  ->  USER APPROVE  ->  tayang Minggu 13:00 ET  ->  arsip Drive archive/
```

Rencana lokasi file:

```
stories/S01E01_sprinkles_first_race/
  script.md            naskah lengkap (dialog, narasi, emosi) - disetujui user sebelum render
  scene_01.json ...    shotlist: kamera, tokoh, lokasi, dialog, emosi, musik, keadaan awal/akhir
  continuity.json      keadaan tokoh/dunia antar scene
```

## 8. Perkiraan biaya & waktu

| Item | Perkiraan |
|---|---|
| Suara (±200 kalimat dialog, Modal) | $0,40 – 0,80 per episode |
| Render 15 scene (CPU VM) | ±30–60 menit per episode, gratis |
| Kerja naskah | Claude menulis draf, user menyetujui atau merevisi |

## 9. Tahapan

1. **Pilot 2–3 menit** (scene 1–3 "Sprinkles' First Race"): menguji close-up, POV, suara tokoh, lip-sync, musik, subtitle.
2. Pilot disetujui, lalu **episode penuh pertama** (target minggu ke-3).
3. Episode mingguan + liga + benang merah musim.

## 10. Keputusan terbuka

- [x] **Rasio layar: dua versi** (user 2026-10-01). Setiap scene dirender dua kali dengan bingkai kamera berbeda:
  16:9 untuk video panjang, 9:16 untuk Shorts "Part N".
- [x] **Shorts "Part N": tetap 3 Shorts per hari** (user 2026-10-01). Satu slot per hari diganti "Part N" sebagai
  selingan; RACE 15:00 tetap setiap hari. Slot yang diganti bergiliran antara CHALLENGE (11:00) dan SMASH (19:00).
  Setelah ada data YouTube Analytics (±2 minggu), yang peminatnya lebih sepi lebih sering diganti.
  Seminggu = 7 Part (scene paling menarik dari episode minggu itu, dengan kait "full episode on our channel").
- [x] Episode pertama: **"Sprinkles' First Race"** (user 2026-10-01). Daftar tokoh menyusul di naskah.

## Riwayat keputusan

| Tanggal | Keputusan |
|---|---|
| 2026-10-01 | Video panjang mingguan ±15 menit, slot sendiri Minggu 13:00 ET (Shorts tetap 3× sehari) |
| 2026-10-01 | Tokoh bersuara (lebih emosional) + narator + subtitle |
| 2026-10-01 | Aturan usia suara: kecil sekali = suara anak, remaja = suara remaja, narator dewasa |
| 2026-10-01 | Format "drama China": 15 scene × ±1 menit, setiap scene berakhir dengan kait, dirender per scene |
| 2026-10-01 | Dua versi rasio (16:9 video panjang, 9:16 Shorts "Part N") |
| 2026-10-01 | Tetap 3 Shorts/hari: 1 slot/hari jadi "Part N" bergiliran CHALLENGE/SMASH (RACE tetap); nanti pakai data Analytics |
| 2026-10-01 | Episode pertama: "Sprinkles' First Race" |
| 2026-10-01 | S01E01: 15 scene penuh; garis waktu = pembuka kilas-maju hari balapan, cerita mulai 30 hari sebelumnya, latihan 4 minggu, kilas balik masa kecil hanya kenangan singkat ("MANY YEARS AGO") |
| 2026-10-01 | Jadwal video panjang pindah ke **Minggu 13:00 ET** (= Senin 00:00 WIB): waktu keluarga + tambahan 1 hari produksi |
