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
- Repo: `github.com/kokoali-bima/megawheel-video-engine` (branch main).

## A. Wajib sebelum otomasi dilepas

| # | Tugas | Status | Pemegang | Catatan / langkah berikut |
|---|---|---|---|---|
| A1 | Akses SSH 99.2 → 99.3 untuk agent (key terbatas, bukan root penuh) | ⏸️ | user | Disarankan `command=`-restricted key di `authorized_keys` 99.3 |
| A2 | Uji upload terjadwal 1 episode (Ep. 1) + cek di YouTube Studio | ⏸️ | user | Upload dari Claude Code ditolak pengaman otomatisnya (2026-09-30). Jalankan sendiri: `publish_queue.py plan` lalu `publish_queue.py upload --confirm --max 1`, atau beri izin ke Claude Code. Cek: status "Terjadwal", jam sesuai, "Tidak dibuat untuk anak-anak", kategori Film & Animasi |
| A3 | Uji coba agent produksi + agent penjadwal di 99.2 (dry run) | ⬜ | user + agent | Setelah A1. Cek: agent tidak approve, mengisi PRODUCTION_LOG, commit |
| A4 | Upload terjadwal Ep. 2–8 | ⬜ | agent penjadwal | Setelah A2 lolos |

## B. Kualitas engine

| # | Tugas | Status | Pemegang | Catatan |
|---|---|---|---|---|
| B1 | Tingkat lolos seri splash ≥ 7/10 seed (sekarang ±2–3/10) | ⬜ | — | Penyebab: durasi level terlalu panjang + momen spin wajib. Kandidat: lintasan lebih pendek, `max_win` 27 |
| B2 | Kendaraan berat jangan selalu "stuck" | ⬜ | — | Roadmap BLUEPRINT 9 no. 3 |
| B3 | Smoke test semua seri sebelum commit (`test_all.sh`: preview 2 seed per seri) | ⬜ | — | |
| B4 | Folder kerja lokal user (`sim-prototype`) diganti clone git | ⬜ | — | Hindari beda versi lokal vs VM |
| B5 | Bersihkan MP4 di `renders/megawheel_arena/rejected/` (±95 MB) | ⏸️ | user | Butuh izin hapus dari user |

## C. Fitur dan pertumbuhan channel

| # | Tugas | Status | Pemegang | Catatan |
|---|---|---|---|---|
| C1 | Mode kamera **Top-Down 2.5D** (balapan, efek licin, kamera campuran) | ⬜ | — | Keputusan user 2026-09-30: kamera campuran. Samping untuk crash/lompat/lahar, atas untuk licin/balapan |
| C2 | Seri Roller Coaster | ⬜ | — | |
| C3 | Format balapan 3–4 mobil (hitung mundur, HUD peringkat) | ⬜ | — | Cocok digabung dengan C1 |
| C4 | Riset format video panjang 15 menit/minggu (cerita tokoh vs balapan vs campuran) | ⬜ | — | Keputusan berdasarkan data (monetisasi + penonton stabil) |
| C5 | Pipeline video panjang (16:9, rangkaian adegan, cerita) | ⬜ | — | Setelah C4 |
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

## Riwayat update file ini

| Tanggal | Oleh | Perubahan |
|---|---|---|
| 2026-09-30 | Claude Code | File dibuat. A2 ⏸️: upload dari Claude Code ditolak pengaman otomatis, menunggu user |
