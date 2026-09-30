# REKAM JEJAK & SPESIFIKASI PROYEK OTOMASI VIDEO (iPANDU VIDEO ENGINE)

Dokumen ini adalah **ringkasan komprehensif** seluruh riset, arsitektur sistem, riwayat percakapan, kesalahan masa lalu (*lessons learned*), dan Standar Operasional Prosedur (SOP) produksi video pendek (*Shorts / Reels / TikTok*). Dokumen ini dirancang agar setiap sesi **Gemini Pro** dapat langsung memahami konteks proyek secara utuh tanpa mengulang kesalahan lama.

---

## 1. Tujuan & Visi Proyek
* **Fokus Utama:** Membangun "Pabrik Konten Video Otomatis" (*Autonomous Video Generation Pipeline*) berbasis alat-alat **100% Open Source** di server Linux lokal (tanpa biaya API per detik video).
* **Target Niche Konten:**
  1. *Physics Gaming Simulation* (BeamNG.drive: Potholes, Speed Bumps, Crash Barriers).
  2. *Heavy Machinery / Industrial Machines* (Mesin Alat Berat).
  3. *Space Exploration & Science* (NASA, Roket, Sains Populer).
* **Target Penonton & Monetisasi:**
  * **Audiens Global (US / English-First):** Memaksimalkan nilai RPM/CPM monetisasi iklan.
  * **Ramah Anak (*Kids-Friendly*):** Visual ceria, narasi suara lembut bersahabat, tanpa kekerasan grafis, dan menggunakan bahasa Inggris sederhana (*Simple English*).
  * **Kompatibilitas YouTube:** Memanfaatkan fitur *YouTube Auto-Dubbing* & *Auto-Caption* untuk pasar Indonesia dan global.

---

## 2. Arsitektur Backend yang Telah Dibangun (`/root/video-engine/`)

Seluruh sistem telah distandarisasi ke dalam modul-modul Python terstruktur:

| Modul | File Path | Fungsi Utama |
| :--- | :--- | :--- |
| **Downloader** | [`/root/video-engine/core/downloader.py`](file:///root/video-engine/core/downloader.py) | `yt-dlp` wrapper dengan pembatasan resolusi otomatis (mencegah file AV1 bengkak). |
| **Scene Detector** | [`/root/video-engine/core/scene_detector.py`](file:///root/video-engine/core/scene_detector.py) | `PySceneDetect` + `OpenCV` untuk membedah video dan menemukan pergantian adegan per frame (*frame-accurate*). |
| **Audio Engine** | [`/root/video-engine/core/audio_engine.py`](file:///root/video-engine/core/audio_engine.py) | `Edge-TTS` (`en-US-AnaNeural`) + `Pydub` *Auto-Ducking* (mengecilkan BGM saat suara narator bicara). |
| **Subtitle Engine** | [`/root/video-engine/core/subtitle_engine.py`](file:///root/video-engine/core/subtitle_engine.py) | `Faster-Whisper` + *Dynamic Animated ASS Subtitle Generator*. |
| **Compositor** | [`/root/video-engine/core/compositor.py`](file:///root/video-engine/core/compositor.py) | FFmpeg Assembler untuk layout 9:16 vertikal (*Full-Bleed Blur Background* + *Golden Framed Center Window*). |
| **Validator (QA)** | [`/root/video-engine/core/validator.py`](file:///root/video-engine/core/validator.py) | Pre-Flight Linter: Memvalidasi resolusi (1080x1920), durasi (<50s), dan kesehatan audio stream. |

---

## 3. Formula Standar Produksi (*The Production Standard Recipe*)

Berdasarkan video referensi terbaik ([`POTHOLES_PERFECTED_KIDS_ENGLISH_MASTERPIECE_LOUD.mp4`](file:///tmp/POTHOLES_PERFECTED_KIDS_ENGLISH_MASTERPIECE_LOUD.mp4)), berikut adalah formula wajib:

```text
+-------------------------------------------------------------------------+
|                  1080 x 1920 FULL-BLEED BLURRED CANVAS                  |
|                                                                         |
|        [ TOP BADGE: LEVEL 1 : BLACK SPORT CAR ] (DejaVu Sans 36pt)      |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  |                                                                   |  |
|  |        CENTER 16:9 MAIN VIDEO BOX (1080 x 608)                    |  |
|  |        - Bingkai Emas Tebal (drawbox yellow@0.7:t=5)             |  |
|  |        - Ketajaman 100% tanpa crop/zoom                           |  |
|  |                                                                   |  |
|  +-------------------------------------------------------------------+  |
|                                                                         |
|        [ BOTTOM PILL: FAIL / GAGAL! atau WINNER / JUARA! ]              |
|        - Menggunakan Aset Grafis PNG Asli (1080x220) di y=1320          |
|                                                                         |
+-------------------------------------------------------------------------+
```

### Detail Spesifikasi Layout & Audio:
1. **Full-Bleed Blurred Background:** Video 16:9 diduplikasi ke latar belakang, di-scale ke 1080x1920, dan diberi efek blur halus (`boxblur=25:5,eq=brightness=-0.22`). Tidak boleh ada layar hitam kosong (*dead letterbox*).
2. **Top Pill Tag (.ASS Subtitle):** Font `DejaVu Sans 36pt` berwarna kuning berlatar hitam transparan:
   * Level 1: `[ LEVEL 1 : BLACK SPORT CAR ]`
   * Level 2: `[ LEVEL 2 : VINTAGE CLASSIC CAR ]`
   * Level 3: `[ LEVEL 3 : 6X6 HEAVY DUALLY TRUCK ]`
3. **Bottom Pill Cards (Wajib Menggunakan PNG):**
   * Gagal: [`/tmp/kids_graphic_assets_fhd/fail_id_fhd.png`](file:///tmp/kids_graphic_assets_fhd/fail_id_fhd.png) (Merah berbingkai putih).
   * Menang: [`/tmp/kids_graphic_assets_fhd/win_id_fhd.png`](file:///tmp/kids_graphic_assets_fhd/win_id_fhd.png) (Hijau zamrud berbingkai putih).
   * **Dilarang memakai kalkulasi `drawbox` dinamis** yang rentan tergeser (*misaligned/cut-off*).
4. **Struktur Durasi 3 Level (Total 45.9 Detik):**
   * Level 1 (0.0s – 13.7s): Mobil Sport Hitam -> Tabrak lubang di 3.6s -> Terseret sampai BERHENTI DIAM TOTAL -> FAIL ❌.
   * Level 2 (13.7s – 24.7s): Sedan Klasik Vintage -> Tabrak lubang & bodi lepas di 6.0s -> Sasis berhenti diam -> FAIL ❌.
   * Level 3 (24.7s – 45.9s): Truk Pikap Merah 6-Roda -> Libas jalanan rusak di 12.2s -> Tembus finis di 17.5s -> Melaju gagah merayakan kemenangan -> WINNER 🏆.
5. **Karakter Suara & Narasi (English Kids Voice):**
   * Voice ID: **`en-US-AnaNeural`** (Suara narator anak/kartun yang halus, ceria, dan tidak robotik).
   * Pacing: Narasi deskripsi mobil saat melaju, narasi seruan benturan tepat saat mobil menghantam rintangan, dan narasi klimaks di akhir: *"HOREEE! Yay! We made it to the finish line! You are the champion!"* diiringi *Cheering & Fanfare SFX*.
   * Audio Master: Di-boost +10dB agar lantang dan jernih di speaker handphone (`mean_volume: ~-18 dB`, `max_volume: 0 dB`).

---

## 4. Riwayat Kesalahan Masa Lalu & Solusinya (*Lessons Learned*)

| Masalah yang Pernah Terjadi | Penyebab Masalah | Solusi Baku (SOP Wajib) |
| :--- | :--- | :--- |
| **Teks Bergeser & Terpotong di Layar HP** | Menggunakan filter `drawbox/drawtext` dengan koordinat manual yang bergeser. | Gunakan aset gambar **PNG resmi (`1080x220`)** yang di-overlay di koordinat `y=1320`. |
| **Kotak Bolong (*Tofu Emoji `[]`*)** | Menyisipkan emoji unicode langsung ke filter teks tanpa font emoji sistem. | Gunakan tulisan teks bersih beranimasi atau grafis PNG, dilarang menyisipkan emoji mentah di ASS. |
| **Narasi / Teks Mendahului Tabrakan** | Timestamp reaksi di-set di awal klip saat mobil masih melaju. | Reaksi vokal dan tombol FAIL wajib di-trigger **persis di detik benturan fisik pertama**. |
| **Salah Identifikasi Mobil (Mismatch)** | Asumsi teks tidak mencocokkan rekaman visual asli. | Wajib melakukan **audit visual frame-by-frame** (menggunakan OpenCV / inspect frames) sebelum merilis video. |
| **Suara Narator Hilang / Tertelan BGM** | Volume musik latar terlalu keras atau audio diekspor format `.adts` yang rusak. | BGM di-set pada level `-20 dBFS`, suara narator dinormalisasi ke `-1.0 dBFS peak`, dan diekspor ke master WAV uncompressed sebelum di-encode ke AAC stereo. |

---

## 5. File Penting & Script Produksi Siap Pakai

1. **Script Builder Produksi Master:**
   [`/root/video-engine/build_english_masterpiece_perfect.py`](file:///root/video-engine/build_english_masterpiece_perfect.py)
2. **File Video Master Siap Tayang:**
   [`/tmp/POTHOLES_PERFECTED_KIDS_ENGLISH_MASTERPIECE_LOUD.mp4`](file:///tmp/POTHOLES_PERFECTED_KIDS_ENGLISH_MASTERPIECE_LOUD.mp4)
   [`/root/.gemini/antigravity-cli/scratch/ready_to_upload/VIDEO_02_POTHOLES_US.mp4`](file:///root/.gemini/antigravity-cli/scratch/ready_to_upload/VIDEO_02_POTHOLES_US.mp4)
3. **Aset Grafis Presisi:**
   [`/tmp/kids_graphic_assets_fhd/fail_id_fhd.png`](file:///tmp/kids_graphic_assets_fhd/fail_id_fhd.png)
   [`/tmp/kids_graphic_assets_fhd/win_id_fhd.png`](file:///tmp/kids_graphic_assets_fhd/win_id_fhd.png)
4. **Preset Konfigurasi Niche:**
   [`/root/video-engine/presets/gaming_physics.json`](file:///root/video-engine/presets/gaming_physics.json)
