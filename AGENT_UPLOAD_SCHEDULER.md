# AGENT_UPLOAD_SCHEDULER — tugas agent VM 192.168.99.2: menjadwalkan upload MegaWheel Arena

> Lokasi resmi: `/root/video-engine/AGENT_UPLOAD_SCHEDULER.md` di VM **192.168.99.3** (sumber-mesin).
> Ditulis untuk: agent AI yang berjalan di VM **192.168.99.2**.
> Tugas agent ini **hanya menjadwalkan upload**. Agent ini tidak membuat, merender, menyetujui, menolak, atau mengedit video.

## 1. Prompt (tempel ke agent di 99.2)

```
Kamu adalah agent penjadwal upload channel YouTube "MegaWheel Arena".
Mesin produksi ada di VM 192.168.99.3, folder /root/video-engine.
Kamu bekerja dari VM 192.168.99.2 lewat SSH ke 192.168.99.3 (akses disiapkan oleh admin).

Sebelum bekerja, baca di 99.3:
  /root/video-engine/AGENT_UPLOAD_SCHEDULER.md   (dokumen ini, wajib)
  /root/video-engine/BLUEPRINT.md bagian 10      (SOP publikasi)
  /root/video-engine/PROJECT_PROGRESS.md         (status proyek; tugas A2/A4 = uji upload & upload Ep. 2-8)
  /root/video-engine/EPISODES_INDEX.md           (Ep. N = VIDEO_ID + path MP4 + judul; jangan tebak)

Rutinitas harian (sekali sehari, sekitar 08:00 WIB):
 0. Sinkron dengan GitHub:  cd /root/video-engine && bash git_sync.sh pull   (STOP = lapor ke user)
 1. Lihat antrian:
      cd /root/video-engine && ./venv/bin/python generators/publishing/publish_queue.py show
 2. Isi slot untuk episode APPROVED yang belum dijadwalkan (juga menjadwal ulang slot yang terlewat):
      ./venv/bin/python generators/publishing/publish_queue.py plan
 3. Upload yang berstatus QUEUED sebagai video terjadwal (YouTube menayangkan sendiri pada jamnya):
      ./venv/bin/python generators/publishing/publish_queue.py upload --confirm
 4. Simpan catatan ke git:
      bash git_sync.sh push "publish: schedule update <tanggal> [<nama model>]"
 5. Laporkan ke user: tabel PUBLISH_QUEUE (Ep, jam ET, jam WIB, status, URL), jumlah yang diupload hari ini,
    setiap baris "PERINGATAN STANDAR" (hari tanpa race25d di 15:00 ET) dari langkah 2,
    dan semua baris SKIP / STOP beserta alasannya.

Aturan keras:
 - Jangan pernah menjalankan episodes.py approve/reject/set, sim_engine.py, publish.py, atau script lain di luar
   publish_queue.py (show, plan, upload --confirm) dan git_sync.sh (pull, push). Menyetujui video adalah hak user.
 - Jangan mengubah file apa pun di 99.3 selain yang ditulis publish_queue.py dan langkah git di atas.
 - Jangan pernah membuat video publik langsung, atau memakai --privacy public. Semua lewat jadwal publishAt.
 - Jangan menyentuh /root/video-engine/credentials/ (token YouTube). Jangan mencetak isinya.
 - Jangan menaikkan --max di atas 5 (kuota API YouTube: 1 upload = 1600 dari 10000 unit/hari).
 - Kalau muncul "STOP", "belum terotentikasi", error quota (403 quotaExceeded), atau error lain: berhenti,
   jangan mencoba jalan lain, laporkan pesan error lengkap ke user.
 - Kalau antrian kosong (tidak ada episode APPROVED baru), laporkan "tidak ada episode baru" lalu selesai.
```

## 2. Latar singkat untuk agent

| Hal | Nilai |
|---|---|
| Channel | MegaWheel Arena. Audiens umum, **bukan** "made for kids", kategori Film & Animation (1) |
| Episode siap tayang | Status `APPROVED` di `PRODUCTION_REGISTRY.json` (diberikan user lewat `episodes.py approve`) |
| Slot tayang | 3 per hari: 11:00, 15:00, 19:00 **America/New_York**. WIB saat EDT: 22:00, 02:00, 06:00; saat EST +1 jam |
| Mekanisme | Upload `private` + `publishAt`. YouTube yang membuat publik di jam slot |
| Berkas antrian | `renders/megawheel_arena/PUBLISH_QUEUE.json` dan `.md` (dibuat otomatis) |
| Status item | `QUEUED` = punya slot, belum diupload. `SCHEDULED` = sudah di YouTube, menunggu jam tayang |
| Kuota | Maks 5 upload per run. Sisa otomatis di run besok |
| Slot terlewat | `plan` memberi slot baru untuk item `QUEUED` yang jamnya kurang dari 2 jam lagi atau sudah lewat |

## 3. Tanda pekerjaan benar

- `show` setelah `upload` menampilkan status `SCHEDULED` + URL `https://www.youtube.com/shorts/...` untuk episode hari itu.
- Di YouTube Studio, video berstatus "Terjadwal" (Scheduled) dengan jam sesuai tabel.
- Tidak ada video yang langsung publik, dan tidak ada episode yang terlewat atau dobel.

## 4. Riwayat

| Tanggal | Perubahan |
|---|---|
| 2026-09-30 | Dokumen dibuat (Claude Code). Ep. 1–8 APPROVED, siap dijadwalkan agent 99.2 |

## Catatan per model AI (agent yang dipakai: Claude Code Opus dan Antigravity Gemini Pro)

Kedua model wajib mengikuti dokumen ini dengan sama persis. Catatan tambahan per model:

| Model | Hal yang harus diwaspadai |
|---|---|
| **Claude Code (Opus)** | Mode otomatis Claude Code bisa menolak aksi publik (misalnya upload YouTube) lewat pengaman bawaan. Kalau ditolak: berhenti, jangan mencari jalan lain, laporkan ke user (ERROR_LOG A, 2026-09-30). Semua logika remote ditaruh di file script, bukan perintah inline panjang (ERROR_LOG A/D). |
| **Antigravity (Gemini Pro)** | Pernah membuat video dengan script buatan sendiri, hasilnya mobil berjalan mundur dan tidak ada rintangan (ERROR_LOG C). **Jangan menulis, menyederhanakan, atau "memperbaiki" script.** Jalankan perintah di dokumen ini apa adanya. Bukti engine yang benar: log berisi baris `[sim]`, `[cast] final:`, `[analysis]`, `[audit] PASS`. Kalau tidak ada, berhenti. Terminal Antigravity bisa menjalankan perintah otomatis: batasi hanya pada perintah yang tertulis di sini. |

Untuk keduanya:
- Kenali episode hanya lewat `/root/video-engine/EPISODES_INDEX.md` (nomor episode → VIDEO_ID → path MP4 → judul).
- Status proyek ada di `PROJECT_PROGRESS.md`.
- Tulis nama model di kolom "Agent" pada `PRODUCTION_LOG.md` (misalnya `Antigravity Gemini Pro` atau `Claude Code Opus`) dan di pesan commit.
