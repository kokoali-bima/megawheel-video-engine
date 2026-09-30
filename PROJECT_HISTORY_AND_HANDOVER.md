# MegaWheel Kids (YouTube Automation) — Project History, Architecture & Handover Guide

> **Document Version**: 1.0  
> **Last Updated**: 2026-09-30  
> **Channel Name**: **MegaWheel Kids**  
> **Channel ID**: `UC97AUm5Od7P7leF5IqX-9bQ`  
> **Target Audience**: United States & Global — Kids & Family Gaming / Physics Simulation  

---

## 1. Executive Summary & Vision

**MegaWheel Kids** is an automated, high-retention YouTube Shorts & Longform channel focusing on high-energy BeamNG physics simulations, extreme obstacle courses, and vehicle challenges.

The production pipeline is designed to be 100% automated, utilizing local open-source tools (FFmpeg, Python, PySceneDetect, OpenCV, Edge-TTS `en-US-AnaNeural`) with authentic in-game audio extraction and kinetic visual badges.

---

## 2. Infrastructure & Network Topology

| Host / Node | Role | IP / Access | Working Directory | Environment |
|---|---|---|---|---|
| **Management Host** (`hetzner-cloud01`) | Central Agent & Deployment Orchestrator | `88.198.150.205` / `localhost` | `/root/ipandu-deploy` | Linux / Python 3 / Antigravity CLI |
| **Worker Node** (`moneyprinter-node-3`) | Video Rendering, Footage Storage & Upload Worker | `192.168.99.3` (Port `22022`, User `root`) | `/root/video-engine` | Ubuntu ARM64, Python venv at `/root/video-engine/venv` |

### Key Directories on Worker Node (`192.168.99.3`):
- `/root/video-engine`: Main Python automation codebase and core modules.
- `/root/local_videos/physics/`: Raw footage downloads (BeamNG, extreme obstacles).
- `/root/renders/youtube_shorts_batch/`: Rendered production-ready Shorts MP4 files.
- `/tmp/kids_graphic_assets_fhd/`: Rendered badges (`fail_en_fhd.png`, `win_en_fhd.png`).
- `/root/video-engine/core/`: Python modules (`tracker.py`, `footage_manager.py`, `youtube_uploader.py`).

---

## 3. SOP & Standar Emas Produksi (5 Golden Rules)

Setiap video yang diproduksi WAJIB mematuhi **5 Standar Emas Produksi**:

1. **Analisa Menyeluruh Video Sumber**: Audit scene-by-scene dari raw footage sebelum proses pemotongan.
2. **Deteksi Presisi Titik Start s/d Finish**: Deteksi eksak frame start kendaraan hingga titik finish atau crash.
3. **Scene Setiap Kendaraan Wajib Utuh**: Dilarang memotong/melompat di tengah run. Satu scene mobil harus utuh dari start hingga tuntas.
4. **Sinkronisasi Teks, Narasi, Badge & SFX**:
   - Badge `FAIL` / `WINNER` muncul tepat pada frame kejadian atau 0.5s sebelumnya.
   - Narasi audio wajib selaras dengan aksi visual.
   - Audio raungan mesin asli BeamNG wajib diekstrak dan dimixing tanpa musik berhak cipta.
5. **Wajib Outro Lengkap**:
   - Sertakan CTA penutup: *"Tap LIKE if you enjoyed this video, DISLIKE if you didn't, and smash SUBSCRIBE to MegaWheel Kids!"*
6. **SOP 100 Video Pertama**:
   - **Render Lokal Preview Saja** (`RENDERED_PENDING_APPROVAL`).
   - **DILARANG KERAS UPLOAD OTOMATIS TANPA PERINTAH EKSPLISIT / APPROVAL DARI USER**.

---

## 4. Status Katalog & Tracker Video

### Video 1 (Live Public):
- **Judul**: *Cars VS Giant Road Potholes! 🚗💥 Can They Survive? #Shorts*
- **Status**: `UPLOADED_PUBLIC`
- **YouTube Link**: [https://www.youtube.com/shorts/Ej0ID15SfOk](https://www.youtube.com/shorts/Ej0ID15SfOk)

### Video 2 (Live Public):
- **Judul**: *Jeep & Double Decker Bus VS Big Rig Semi Truck! 🚒💥 Who Wins? #Shorts*
- **Status**: `UPLOADED_PUBLIC`
- **YouTube Link**: [https://www.youtube.com/shorts/V_ZOODktNmY](https://www.youtube.com/shorts/V_ZOODktNmY)

### Video 3 (Live Public):
- **Judul**: *Muscle Car & Police Cruiser VS Soliad Race Car! 🏎️💥 Level 3 Wins! #Shorts*
- **Status**: `UPLOADED_PUBLIC`
- **YouTube Link**: [https://www.youtube.com/shorts/TR3suH0vA18](https://www.youtube.com/shorts/TR3suH0vA18)
- **File Output**: `/root/renders/youtube_shorts_batch/VIDEO_03_SYNCED_PERFECT_CHAMPION.mp4`
- **Struktur Scene (Total: 47.0s)**:
  - **Level 1 (0.0s - 12.0s)**: *Silver Fastback Muscle Car* (Start: 160.0s, Crash flip: 6.5s, FAIL badge).
  - **Level 2 (12.0s - 28.0s)**: *Police Sheriff Cruiser* (Start: 608.0s, Airborne roll: 23.0s / 11.0s scene, FAIL badge + siren).
  - **Level 3 (28.0s - 47.0s)**: *Blue & White Soliad Race Car* (Start: 689.85s murni tanpa penyusup, Finish cross: 37.2s / 9.2s scene, WINNER badge + cheer + Full Outro CTA).

---

## 5. Kebijakan Retensi Bahan Footage (7-Day Auto Retention)

- **Modul**: [`core/footage_manager.py`](file:///root/video-engine/core/footage_manager.py)
- **Registry**: [`FOOTAGE_SOURCE_REGISTRY.md`](file:///root/video-engine/FOOTAGE_SOURCE_REGISTRY.md) & `.json`
- **Aturan**:
  - Setiap footage yang diunduh wajib dicatat URL sumber, platform, tanggal download, durasi, dan file path.
  - Footage mentah yang tidak digunakan dalam kurun waktu **7 hari** dihapus otomatis oleh sistem untuk menghemat disk storage.
  - Jika footage dibutuhkan kembali di masa depan, sistem dapat mengunduh ulang secara otomatis berdasarkan URL pada registry.

---

## 6. Command & Script Cheat Sheet

### Menghubungkan ke Node Worker:
```bash
ssh -p 22022 root@192.168.99.3
```

### Menjalankan Render Video 3:
```bash
ssh -p 22022 root@192.168.99.3 "cd /root/video-engine && PYTHONPATH=. /root/video-engine/venv/bin/python3 render_video3_synced_perfect.py"
```

### Mengambil Preview Video ke Host Lokal:
```bash
scp -P 22022 root@192.168.99.3:/root/renders/youtube_shorts_batch/VIDEO_03_SYNCED_PERFECT_CHAMPION.mp4 /tmp/VIDEO_03_SYNCED_PERFECT_CHAMPION.mp4
```

### Menjalankan Upload ke YouTube (Hanya setelah persetujuan user):
```bash
ssh -p 22022 root@192.168.99.3 "cd /root/video-engine && PYTHONPATH=. /root/video-engine/venv/bin/python3 upload_cli.py --file /root/renders/youtube_shorts_batch/VIDEO_03_SYNCED_PERFECT_CHAMPION.mp4 --video-id VIDEO_03_SYNCED_PERFECT_CHAMPION"
```

---

## 7. Catatan Penting untuk Sesi / Model Selanjutnya

1. **Selalu Gunakan Port SSH `22022`** saat berkomunikasi dengan node `192.168.99.3`.
2. **Jangan Lupa Format Telegram**: Jangan gunakan notasi LaTeX/KaTeX (`$..$`). Gunakan teks biasa.
3. **Format Shorts 9:16**:
   - Resolusi target: `1080x1920`.
   - Video utama di-crop/letterbox 16:9 di bagian tengah (`y=656`, ukuran `1080x608`) dengan background blurred.
   - Badge status di atas (`y=1320` atau safe zone tengah).
   - Jangan letakkan elemen interaktif di 500px terbawah layar (`y > 1400`) agar tidak tertutup UI YouTube Shorts (tombol like/comment bawaan YouTube).
4. **Audio Balance Standar**:
   - Narasi (`en-US-AnaNeural`): Volume `1.60x`
   - Suara Mesin Game BeamNG Asli: Volume `0.85x`
   - BGM Ceria Anak: Volume `0.10x` (ducked)
   - SFX Fail Buzzer / Win Fanfare: Volume `0.75x - 0.90x`
