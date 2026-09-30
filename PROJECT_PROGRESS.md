# PROJECT_PROGRESS — status pekerjaan MegaWheel Arena (dibaca semua agent)

> Lokasi resmi: `/root/video-engine/PROJECT_PROGRESS.md` di VM 192.168.99.3.
> **Setiap agent wajib membaca file ini di awal sesi** (bersama `BLUEPRINT.md` dan `ERROR_LOG.md`).
> Aturan update:
> - Saat mulai sebuah tugas, ubah statusnya ke 🔄 dan isi kolom "Pemegang".
> - Saat selesai, ubah ke ✅, isi tanggal, dan tambah 1 baris di bagian Riwayat.
> - Jangan menghapus baris. Tugas yang dibatalkan diberi ❌ beserta alasannya.
> - Hanya user yang boleh menambah prioritas baru atau mengubah urutan prioritas.
>
> Status: ⬜ belum · 🔄 dikerjakan · ⏸️ menunggu (user/izin) · ✅ selesai · ❌ batal

## Ringkasan saat ini (2026-09-30)

- Engine **v2.8**: 4 seri Shorts (potholes, bumps, splash, lava), 10 tokoh, tema dan narator bergilir, audit otomatis.
- **8 episode APPROVED** (S01 Ep. 1–8) di `renders/megawheel_arena/S01/`, masuk `PUBLISH_QUEUE`, **belum ada yang diupload**.
- Dokumen agent: `AGENT_VIDEO_PRODUCER.md` (buat video, tanpa upload), `AGENT_UPLOAD_SCHEDULER.md` (jadwalkan yang APPROVED).
- Repo: `github.com/kokoali-bima/megawheel-video-engine` (branch main). VM 99.3 = GitHub, disinkronkan **hanya** dengan `bash git_sync.sh pull|push`.

## A. Wajib sebelum otomasi dilepas

| # | Tugas | Status | Pemegang | Catatan / langkah berikut |
|---|---|---|---|---|
| A1 | Akses SSH 99.2 → 99.3 untuk agent (key terbatas, bukan root penuh) | ⏸️ | user | Disarankan `command=`-restricted key di `authorized_keys` 99.3 |
| A2 | Uji upload terjadwal 1 episode (Ep. 1) + cek di YouTube Studio | ✅ 2026-09-30 | user / agent | Upload antrian dijalankan di VM: **Ep. 2–6 SCHEDULED** di YouTube (URL di PUBLISH_QUEUE.md). Ep. 1 terlewat slotnya → dijadwal ulang. Catatan lama: | Upload dari Claude Code ditolak pengaman otomatisnya (2026-09-30). Jalankan sendiri: `publish_queue.py plan` lalu `publish_queue.py upload --confirm --max 1`, atau beri izin ke Claude Code. Cek: status "Terjadwal", jam sesuai, "Tidak dibuat untuk anak-anak", kategori Film & Animasi |
| A3 | Uji coba agent produksi + agent penjadwal di 99.2 (dry run) | ⬜ | user + agent | Setelah A1. Cek: agent tidak approve, mengisi PRODUCTION_LOG, commit |
| A4 | Upload terjadwal Ep. 2–8 | 🔄 | agent penjadwal | Ep. 2–6 ✅ SCHEDULED. Sisa: Ep. 1, 7, 8 (QUEUED, urut nomor episode). Cek di YouTube Studio: status Terjadwal, "Tidak dibuat untuk anak-anak", kategori Film & Animasi |

## B. Kualitas engine

| # | Tugas | Status | Pemegang | Catatan |
|---|---|---|---|---|
| B1 | Tingkat lolos seri splash ≥ 7/10 seed | 🔄 | Claude Code Opus | v2.9: 3/10 → **5/10** (varian tanpa replay + lintasan lebih pendek). Sisa hambatan: level juara 22–25 s. Langkah berikut: persingkat outro juara di splash atau naikkan `max_win` |
| B2 | Kendaraan berat jangan selalu "stuck" | ⬜ | — | Roadmap BLUEPRINT 9 no. 3 |
| B3 | Smoke test semua seri sebelum commit | ✅ 2026-09-30 | Claude Code Opus | `bash generators/physics_2d/test_all.sh` (default seed 901–903 semua seri). Exit 1 = ada error / seri 0 lolos |
| B4 | Sinkronisasi VM = GitHub lewat git | ✅ 2026-09-30 | Claude Code Opus | `bash git_sync.sh pull` di awal sesi, `bash git_sync.sh push "<pesan>"` di akhir tugas (smoke test otomatis kalau kode berubah, menolak credentials/). PC user (2026-09-30): git terpasang + deploy key `id_ed25519_megawheel` (alias `github-megawheel`), clone di `ipandu-video/megawheel-video-engine`. Alur: edit di clone PC → commit → push GitHub → VM `bash git_sync.sh pull`. Folder lama `sim-prototype` = arsip, jangan dipakai lagi. Sumber kebenaran = GitHub |
| B5 | Bersihkan MP4 di `renders/megawheel_arena/rejected/` (±95 MB) | ⏸️ | user | Butuh izin hapus dari user |

## C. Fitur dan pertumbuhan channel

| # | Tugas | Status | Pemegang | Catatan |
|---|---|---|---|---|
| C1 | **Mode 2.5D "paper cutout"** (arah baru, keputusan user 2026-09-30) | 🔄 | Claude Code Opus | Blender 3D (v3.0) dinilai user terlalu berat/lambat dan tokohnya tidak dikenali → 3D ditunda (kode tetap disimpan). Arah baru: tokoh = gambar 2D PERSIS (fungsi sim_engine), dunia berlajur dengan kedalaman + parallax, spin menyeberang lajur, lompatan, bubble, zoom/shake, dirender cairo di CPU VM (gratis, 449 frame dalam 14.5 s). ✅ Disetujui user. ✅ v3.1: seri Shorts lengkap `race25d` (narasi, audio, replay, CTA, variasi seed, registry). Episode pertama SIM_RACE25D_V1_S001 di pending (menunggu review). Berikutnya: rintangan seri 2D di lajur (lubang, lahar, dinding), variasi arena (C1c) |
| C1b | Tokoh 3D **lebih kartun** (review user 2026-09-30: "oke untuk sekarang, tapi harusnya lebih kartun") | 🔄 | Claude Code Opus | v2 (commit aba051e, review/cast3d_v2): ✅ mata lebih besar di tengah kaca, ✅ senyum + lidah terlihat, ✅ cone Sprinkles di dudukan atap. Sisa: lebih kartun (ringan, tanpa tambah waktu render): proporsi dilebih-lebihkan (bodi pendek-gemuk, roda & mata lebih besar), sudut lebih bulat, warna lebih jenuh, garis tepi hitam tebal (inverted-hull outline, bukan Freestyle yang berat), toon shading 2–3 tingkat |
| C1c | **Variasi arena & kamera 2.5D** (user 2026-09-30: "sudah sesuai banget") | ⬜ | — | Gaya 2.5D DISETUJUI. Tambah: jalan melengkung/menikung ke arah kamera, arena oval/melingkar dilihat dari atas-miring (tokoh tetap gambar 2D, dibalik saat arah berubah, gaya Paper Mario), variasi kamera (samping, atas-miring, close-up reaksi), tema/lokasi bergilir |
| C1e | **Perpustakaan rintangan** (dipakai 3 format) | 🔄 | Claude Code Opus | ✅ v3.3 di race25d: lubang, lahar, dinding, pres (penyet), laser (terbelah), meteor, UFO, naga api (ganti ban), naga es (beku) + genangan & ramp. Semua diuji PASS, 0 frame kosong. ✅ v3.4 (engine v2): rintangan kena siapa pun yang ada di lajurnya; AI pindah jalur untuk menghindar (maks. 1 per video, kelincahan per kendaraan), end card LIKE/SUBSCRIBE gaya YouTube. S002–S007 dirender ulang sebagai v2. Berikutnya: pasang juga di CHALLENGE 2D dan SMASH ARENA; tambah tornado, gempa, batu menggelinding |
| C10 | **SMASH ARENA** (slot 19:00 ET) | ⬜ | — | Saling tabrak sampai hancur, mobil terakhir menang. Arena: kolam lumpur, ring lahar menyempit, arena es, atap gedung, pantai. Bar nyawa, bagian mobil copot, keluar ring = gugur, arena menyempit tiap 10 s |
| C11 | **Kaiju KRAGGOR** (dino-robot, desain sendiri) + kartu kejutan | ⬜ | — | ±1 dari 3 video: kaiju menangkap peserta, UFO, meteor, tornado, gempa. Kraggor bisa jadi "penjahat" tetap di cerita mingguan |
| C12 | **LIGA mingguan** | ⬜ | — | Poin per video (juara 10, dst.), klasemen di akhir Shorts, final 3 besar di video Sabtu 19:00 |
| C1d | **Variasi lokasi & mode balapan 2.5D** (ide user 2026-10-01) | ⬜ | — | Hutan (rally, jalan tanah), padang pasir (Dakar, gundukan pasir), jalan perkampungan, dll. + mode **arena saling tabrak** (demolition derby → tugas C10). Arena: jalan berkelok, oval atas-miring, **sky track melayang ala roller coaster**. Wajib: kamera tidak pernah kosong (cek `no frame without a car`) |
| C9 | **Format cerita mingguan 15 menit** | ⬜ | — | Contoh user: minggu ini kisah Sprinkles sejak kecil. Sumber ide: struktur cerita kartun populer diadaptasi untuk tokoh kita. **Aturan:** pakai pola cerita umum & dongeng domain publik (Aesop, Grimm, dll.), JANGAN menyalin plot/tokoh/dialog spesifik dari kartun berhak cipta (hak cipta + kebijakan YouTube reused content). Shorts harian dipotong dari film mingguan. **Jadwal: Sabtu 19:00 ET** (keputusan user 2026-10-01), seri `story15` |
| C2 | Seri Roller Coaster | ⬜ | — | |
| C3 | Format balapan 3–4 mobil (hitung mundur, HUD peringkat) | ⬜ | — | Cocok digabung dengan C1 |
| C4 | Riset format video panjang 15 menit/minggu (cerita tokoh vs balapan vs campuran) | ⬜ | — | Keputusan berdasarkan data (monetisasi + penonton stabil). **Rencana user 2026-09-30:** 7–14 Shorts 3D/minggu (min. 1 Shorts 3D/hari). Video 15 menit mingguan dibuat dengan salah satu cara: (a) Shorts seminggu digabung + adegan penyambung jadi satu cerita utuh, atau (b) film 15 menit dibuat utuh lalu dipotong jadi Shorts harian. Kalau lancar: channel TikTok. Hitungan biaya Modal (L4, ±0.93 GPU-s/frame, 1080p): Shorts 45 s ≈ $0.33. 14 Shorts ≈ $4.6/minggu. Film 15 menit 30 fps ≈ $6.5 (24 fps + 12 sample ≈ $3.5). Budget $29/bulan cukup untuk (b) + Shorts potongannya. (a)+(b) sekaligus tiap minggu melewati budget |
| C5 | Pipeline video panjang (16:9, rangkaian adegan, cerita) — **"sutradara" 3D** | 🔄 | Claude Code Opus | Opsi (b) dipilih user: film 15 menit lalu dipotong/dirender ulang vertikal jadi Shorts. Tahap 1 ✅ (v3.0): `director3d/` motion → Blender → Modal, horizontal + vertikal dari animasi yang sama (demo 15 s: $0.235, review/director3d_demo). Berikutnya: event sutradara (spin besar, tabrakan, salip, finish/podium), HUD + narasi + audio, skrip adegan/cerita, gaya lebih kartun (C1b) |
| C6 | Tarik metrik YouTube Analytics otomatis → `episodes.py set` | ⬜ | — | Perlu scope `yt-analytics.readonly` (login ulang YouTube) |
| C7 | Evaluasi slot jam tayang setelah 2 minggu tayang | ⬜ | — | BLUEPRINT bagian 10 |

## Selesai (ringkas)

| Tanggal | Versi | Hasil |
|---|---|---|
| 2026-09-30 | v1–v2.3 | Engine fisika 2D, gerbang analisa + audit, registry keunikan, satu engine di `/root/video-engine` |
| 2026-09-30 | v2.4–v2.5 | 10 tokoh, rebrand MegaWheel Arena (bukan konten anak), sistem episode/season |
| 2026-09-30 | v2.6 | Tema lingkungan, narator en-US bergilir, ducking audio |
| 2026-09-30 | v2.7 | Seri Splash Zone + Lava Road, juara fleksibel, SFX bahaya |
| 2026-09-30 | v2.8 | Suara air ≠ lava, mobil meleleh, hydroplaning, momen khas wajib, antrian upload 3/hari (ET) |
| 2026-09-30 | — | Dokumen agent produksi + penjadwal, PRODUCTION_LOG, PROJECT_PROGRESS |
| 2026-09-30 | v2.9 | Varian tanpa replay (pacing), smoke test `test_all.sh`, EPISODES_INDEX, prototipe Top-Down pseudo-3D |

## Riwayat update file ini

| Tanggal | Oleh | Perubahan |
|---|---|---|
| 2026-10-01 | Claude Code Opus | C1e: race25d engine v2 (dodge AI + end card YouTube); v1 S002–S007 REJECTED (superseded) → v2 S002–S007 pending |
| 2026-09-30 | Claude Code | File dibuat. A2 ⏸️: upload dari Claude Code ditolak pengaman otomatis, menunggu user |
| 2026-09-30 | Claude Code Opus | v2.9: B1 🔄 (5/10), B3 ✅, C1 🔄 (prototipe pseudo-3D), EPISODES_INDEX.md dibuat |
| 2026-09-30 | Claude Code Opus | B4 ✅: `git_sync.sh` (pull/push/status) jadi satu-satunya cara sinkron VM ↔ GitHub |
| 2026-09-30 | Claude Code Opus | PC user punya clone git sendiri; commit pertama dari PC (uji alur PC → GitHub → VM) |
| 2026-09-30 | Claude Code Opus | A2 ✅ / A4 🔄: Ep. 2–6 terjadwal di YouTube. Commit `95de2ce` (pesan ".gitignore") ternyata juga memuat catatan upload itu (registry, antrian, manifest Ep. 2–6) yang belum di-commit di VM. Isinya benar, hanya pesannya tidak lengkap. Antrian: sisa item diurutkan ulang per nomor episode |
