# RESEARCH_W3 — data Shorts minggu 1 + arah 2.5D terbaik (2026-10-03)

> User 2026-10-03: "riset terus untuk hasil 2.5D yang terbaik. 3D boleh, tapi tidak wajib — apalagi kalau bikin modal
> keluar, video lambat, dan kurang memacu adrenalin / rasa ingin tahu. 2 video tadi malam belum ada respons (< 10 views)."

## 1. Data (YouTube Data API, 2026-10-03 01:15 UTC)
| Video | Tayang (UTC) | Slot ET | Durasi | Views | Likes |
|---|---|---|---|---|---|
| Ep.2 Speed Bumps | 30/9 19:00 | 15:00 | 50 s | 133 | 2 |
| **Ep.3 Potholes** | 30/9 23:00 | 19:00 | 47 s | **872** | 14 |
| Ep.4 Speed Bumps | 1/10 15:00 | 11:00 | 50 s | 239 | 8 |
| **Ep.5 Potholes** | 1/10 19:00 | 15:00 | 48 s | **1.280** | 13 |
| Ep.6 Speed Bumps | 1/10 23:00 | 19:00 | 48 s | 796 | 18 |
| Ep.1 Potholes | 2/10 15:00 | 11:00 | 45 s | 8 (umur 10 jam) | 2 |
| Ep.9 RACE (slippery) | 2/10 19:00 | 15:00 | 30 s | 0 (umur 6 jam) | 0 |
| Ep.22 SMASH | 2/10 23:00 | 19:00 | 50 s | 3 (umur 2 jam) | 1 |

YouTube Analytics (rinci per video, sumber trafik, retensi) baru tersedia sampai 30/9 (terlambat 1–3 hari).
Catatan dari data awal: rata-rata ditonton > 100% (ditonton ulang/loop) pada video yang sudah ada datanya.

## 2. Bacaan
1. **Tiga video terakhir masih terlalu muda untuk dinilai.** Shorts diuji ke audiens kecil dulu; panduan umum menilai
   setelah 24–48 jam. Cek lagi di laporan Telegram 4–5/10.
2. **Topik pemenang jelas: Potholes** (872 dan 1.280) > Speed Bumps (133–796). Ep.1 (potholes, slot 11:00 ET) masih 8 views:
   slot 11:00 ET juga yang paling lemah di Ep.4 (239). Slot 15:00/19:00 ET lebih baik.
3. **Sinyal utama algoritma = "ditonton vs digeser" di 2 detik pertama.** Target ≥ 75–80% tetap menonton, retensi
   ≥ 80% di 3 detik pertama, rata-rata ditonton ≥ 70% (loop > 100% ideal).
   → **Intro panjang (ident, "Ladies and gentlemen", perkenalan 4 tokoh ±9 dtk) di depan Shorts berisiko tinggi digeser.**
   SMASH lama (cairo) juga begitu, dan Ep.22 SMASH baru 3 views. Perkenalan tokoh tetap bagus untuk cerita, tapi harus
   **didahului cold open 1–2 dtk aksi paling seru** (KO/ledakan terbesar) + teks pertanyaan.
4. Judul yang sama berulang ("Cars VS Giant Potholes! Who Survives?") untuk banyak episode → kurang rasa ingin tahu baru.
   Pakai pola RESEARCH_W2: **tokoh + tantangan + pertanyaan** ("Can Tiny Zippy Survive Giant Potholes?").
5. Format terbukti di niche ini (BeamNG "car crash overstimulation", puluhan juta views): mobil vs rintangan raksasa,
   besar vs kecil, kecepatan naik bertahap, kehancuran jelas terlihat. Itu persis kekuatan 2.5D kita (potholes).

## 3. 3D vs 2.5D (keputusan)
| | 2.5D cairo (produksi) | 3D Godot (lab) |
|---|---|---|
| Render | menit, CPU VM, Rp 0 | 25–30 mnt/video CPU, atau Modal GPU (biaya + setup) |
| Gaya | identitas channel, sudah tayang | lebih "wah", tapi belum terbukti menaikkan retensi |
| Status | **jalur utama** | **opsional / riset** — tidak dipakai produksi sebelum terbukti |

Ide terbaik dari lab 3D yang murah dipindah ke 2.5D: **POW burst + hit-stop 3 frame**, **serpihan bodi mobil copot**
(potongan gambar mobil sendiri), **asap/api bertahap sesuai HP**, **arena air + hiu** (ring-out yang lucu & memuaskan),
**hujan meteor 3 batu**, ledakan bola api halus, end card & replay sudah sama.

## 4. Rencana (urut dampak)
1. **Cold open 1,5 dtk di semua Shorts** (CHALLENGE / RACE / SMASH): potongan momen terbesar video itu sendiri +
   teks pertanyaan besar, baru masuk intro/hitung mundur. Ending nyambung ke awal (loop).
2. **Perbanyak Potholes** dan variannya (lubang air, lubang berjalan, lubang lava) di slot 15:00 / 19:00 ET.
3. **Judul per episode unik**: nama tokoh + tantangan + pertanyaan; teks atas = judul.
4. **SMASH 2.5D v5**: intro tokoh dipersingkat (1,2 dtk/tokoh) setelah cold open; sisipkan POW/hit-stop, serpihan,
   arena air + hiu.
5. Ukur di YouTube Studio: **"Viewed vs swiped away"** per video (tidak tersedia di API) → bandingkan Ep.5 vs Ep.1/9/22.

Sumber: subscribr.ai (Shorts stop getting views), vidiq.com (Shorts algorithm 2026), bytecap.io & shortimize.com
(retention benchmarks), knowyourmeme.com (car crash overstimulation videos), thedrive.com (BeamNG viral crash tests).
