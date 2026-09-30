# ERROR_LOG — kesalahan yang pernah terjadi (JANGAN DIULANG)

> Lokasi: `/root/video-engine/ERROR_LOG.md`. Wajib dibaca bersama `BLUEPRINT.md` sebelum bekerja.
> Aturan: setiap error baru → tambah 1 baris di tabel yang sesuai (tanggal, gejala, penyebab, pencegahan). Jangan hapus baris lama.

## A. Operasional (SSH, shell, quoting, server)

| Tanggal | Gejala | Penyebab | Pencegahan |
|---|---|---|---|
| 2026-09-30 | Huruf `r` hilang di akhir baris kode setelah upload | `sed s/\r$//` dikirim lewat ssh dari PowerShell: backslash hilang, jadi sed menghapus huruf `r` | Konversi CRLF→LF di lokal sebelum `scp` (helper push). Jangan pakai sed untuk CR lewat ssh. |
| 2026-09-30 | Perintah ssh menggantung 10+ menit (terjadi **3 kali**) | `grep -E "a\|b"` inline: PowerShell 5.1 membuang tanda kutip, `\|` jadi pipe, lalu `grep` menunggu stdin selamanya | **Semua logika remote ditaruh di file script** (`.sh`/`.py`) lalu dijalankan dengan `< /dev/null`. Tidak ada `grep`/JSON/pipe di argumen ssh. |
| 2026-09-30 | JSON rusak saat dikirim sebagai argumen | Kutip ganda dibuang PowerShell | Tulis config ke file, kirim dengan scp, script membaca file. |
| 2026-09-30 | `scp ... "folder\"` → `Invalid argument` | Backslash di akhir string dalam kutip meng-escape tanda kutip penutup | Tujuan scp tanpa backslash penutup (`...\branding` bukan `...\branding\`). |
| 2026-09-30 | Seluruh perintah ssh gagal parse | `python -c "..."` dengan kurung/kutip di dalam argumen ssh | Pakai heredoc di dalam file script. |
| 2026-09-30 | `last: command not found` | Tool tidak terpasang di Ubuntu minimal | Cek ketersediaan tool, jangan diasumsikan ada. |
| 2026-09-30 | Pembuatan panduan trigger lintas-VM (99.2→99.3 via SSH root) **ditolak** oleh safety classifier Claude Code | Aksi otomasi lintas-server dengan akses root perlu izin eksplisit | Jangan mencoba jalur lain. Minta user memberi izin eksplisit, atau pekerjaan dilakukan agent/manusia lain. |
| 2026-09-30 | Build `pycairo` gagal (`Unknown compiler`) | Tidak ada compiler / header cairo | `apt-get install libcairo2-dev pkg-config build-essential python3-dev` sebelum `pip install pycairo`. |

## B. Engine / kode

| Tanggal | Gejala | Penyebab | Pencegahan |
|---|---|---|---|
| 2026-09-30 | `AssertionError: body must be added before shape` | pymunk 7: body harus di-`space.add` sebelum shape | Tambah body dulu, baru shape. |
| 2026-09-30 | (risiko) mobil berjalan mundur | Arah `SimpleMotor`: `wheel.w - chassis.w = -rate` | Rate positif = maju. Engine punya pengecekan `motor sign is wrong` + analisa `forward`. |
| 2026-09-30 | Worker render tidak melihat data global | Python 3.14 default start method `forkserver` | `mp.get_context("fork")`. |
| 2026-09-30 | Manifest/preview video yang sudah jadi tertimpa | `--preview-only` dijalankan untuk seed yang sudah dirender | `find_seeds.sh` melewati seed yang MP4-nya sudah ada. Jangan preview seed yang sudah jadi. |
| 2026-09-30 | Hanya 1/8 seed lolos (durasi > 50 s) | Run dipilih tanpa memperhitungkan total durasi | `pick_combo`: hitung durasi semua kombinasi dulu. |
| 2026-09-30 | Bubble "WHOA!" saat bus terperosok | Mood "whoa" hanya mengecek "melayang" | Syarat: melayang **dan** di atas permukaan jalan. |
| 2026-09-30 | Seri speed bumps 0/10 seed lolos | Parameter gundukan & batas durasi belum cocok | Tuning 5 percobaan (tabel di DEV_HISTORY v2.2), `tune_bumps.py` / `tune_cast.py` sebelum render. |
| 2026-09-30 | Tokoh baru bisa membuat engine STOP terus (rotasi selalu memilihnya) | Rotasi adil mendahulukan tokoh jarang tampil walau tidak cocok dengan lintasan | `ROLE_ORDER` + fallback ke tokoh berikutnya dalam peran yang sama. Uji tokoh baru dengan `tune_cast.py`. |

## C. Konten / standar

| Tanggal | Gejala | Penyebab | Pencegahan |
|---|---|---|---|
| 2026-09-30 | Agent lain membuat video dengan mobil mundur dan tanpa rintangan | Salah mengenali mesin (menulis script sendiri) | BLUEPRINT Aturan Nol + sidik jari log + gerbang analisa otomatis. |
| 2026-09-30 | Audit awal gagal di `mean_volume` −13.7 dB | Batas −24..−14 dB terlalu ketat | Batas −20..−12 dB (YouTube normalisasi ±−14 LUFS). |
| 2026-09-30 | Nama tokoh "Blaze" & "Crusher" | Sama dengan serial *Blaze and the Monster Machines* | Cek nama tokoh baru terhadap kartun/brand terkenal (CAST.md aturan 4). |
| 2026-09-30 | Laporan menyebut "7 karakter" padahal 6 | Salah hitung | Hitung dari `characters.json`, bukan dari ingatan. |
| 2026-09-30 | Draft video ikut tercatat sebagai "video" di tracker lama | Tracker publikasi mencampur draft & tayang | Status jelas per video (registry baru: `RENDERED_PENDING_APPROVAL` vs `UPLOADED_*`). |
| 2026-09-30 | **Uploader lama akan melabeli setiap video "Made for Kids"** + kategori Gaming + tag BeamNG/Kids | `core/youtube_uploader.upload_shorts` default `made_for_kids=True`, `category_id="20"`; `upload_cli.py` tidak pernah mengubahnya | Default diubah (`False`, kategori `1`, tag Arena). Upload hanya lewat `publish.py` (eksplisit `made_for_kids=False`, kategori 1, metadata dari manifest). `upload_cli.py` diarsipkan. |
| 2026-09-30 | Audit ulang episode APPROVED mengembalikan status ke PENDING | `audit.py` selalu menulis status | Status hanya diubah kalau masih ANALYZED/PENDING/AUDIT_FAILED atau audit gagal. |

## D. Kebiasaan agent (Claude Code)

| Tanggal | Gejala | Penyebab | Pencegahan |
|---|---|---|---|
| 2026-09-30 | `python -c "..."` inline lewat ssh gagal parse (terjadi lagi setelah dicatat di bagian A) | Kebiasaan lama | Cek ulang perintah ssh sebelum dikirim: kalau ada kutip, kurung, pipe, atau `\|` di dalam argumen remote → pindahkan ke file script. |
