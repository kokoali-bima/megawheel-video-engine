# Prompt untuk sesi baru (tempel apa adanya)

```
Kamu melanjutkan produksi video cerita MegaWheel Arena S01E02 "Who Is Kraggor?" (mesin story3d: dunia Godot 3D + tokoh
asli story25d, render di Modal). Bicara kepada saya dalam Bahasa Indonesia; isi video en-US.

BACA DULU, urut (jangan mulai bekerja sebelum selesai):
1. stories/S01E02_who_is_kraggor/HANDOVER.md        (status, keputusan, pekerjaan berjalan, perintah, jebakan)
2. AGENTS.md  dan  generators/story3d/SOP_STORY3D.md
3. generators/story3d/STYLE_CONTRACT.json            (semua aturan dari review saya; angka ambang)
4. QA_DEFECT_TRACKER.md                              (kesalahan lama + sensor penjaganya - JANGAN diulang)
5. stories/S01E02_who_is_kraggor/script.md           (naskah 15 scene) dan CHARACTERS.md
6. Riwayat chat terakhir: ipandu-video/claude/agent_claude.md (tambahkan entri setiap selesai satu pertukaran)

Repo di PC: F:\drive-aliwardana\My Drive\me\ai-develop\ipandu-video\megawheel-video-engine
VM produksi: 192.168.99.3  (SSH -p 22022 root@2.28.128.77, key dari saya; repo /root/video-engine)

TUGAS SEKARANG: selesaikan scene 5-8 (kilas balik sepia badai, rencana ke gunung, jalan gunung + longsor, gua Kraggor),
dalam SATU putaran: tulis semua scene + lokasi, lint, render bersama, cek lembar kontak + audio + sambungan sendiri,
perbaiki sekali, baru kirim ke Drive. Kode Godot lokasi baru ada di cabang GitHub wip-scenes-5-8 dan BELUM teruji: uji render
singkat dulu, baru gabung ke main. Lalu rakit episode 1-8 dan lanjut scene 9-15.

ATURAN KERJA (dari kesalahan sebelumnya):
- Setiap catatan review saya = aturan baru di STYLE_CONTRACT.json + baris di QA_DEFECT_TRACKER.md, bukan tambalan sekali pakai.
- Hemat token: kerjakan sekaligus (riset, tulis, render, perbaiki), laporan singkat; jangan kirim yang belum kamu cek sendiri.
- Hanya perintah baku (validate_scene -> produce_story3d --upload -> assemble). Jangan unggah hasil QA FAIL.
- JANGAN upload ke YouTube, approve/reject, atau menyentuh credentials/modal.txt. Ep.1 jangan diubah. Jangan render paralel di VM.
- Commit pakai author kokoali-bima <mu.aliwardana@gmail.com>; push = fetch + merge origin/main (jangan rebase), lalu di VM
  git_sync.sh pull. Hentikan proses di VM hanya lewat generators/story3d/tools/stop_story3d.sh.
- Prinsip film: jangan zoom-in terus (maks 2 close-up bertanda), pakai shot grup/two + push-in, J-cut, tanpa sunyi kosong,
  tanpa noise, efek harus terdengar di HP, transisi antar scene = kartu "PART N".
- Laporkan ke saya: verdict QA per scene, peringatan + penjelasannya, biaya Modal, link Drive. Tanya saya bila ragu.
```
