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
| 2026-09-30 | Upload terjadwal Ep. 1 dari Claude Code **ditolak** pengaman otomatis (kategori transaksi dunia nyata), walau user sudah bilang "gas" | Upload ke YouTube = aksi publik yang diblok mode otomatis Claude Code | Jangan mencari jalan lain. Upload dijalankan user sendiri (`publish_queue.py upload --confirm`), agent penjadwal 99.2, atau user menambah izin di setting Claude Code. |
| 2026-09-30 | Clone di PC (folder Google Drive): `.git/index.lock` tertinggal tanpa proses git. Setelah lock dihapus, **index kosong**, sehingga commit berikutnya berisi "hapus 143 file" | Sinkronisasi Google Drive mengganggu rename atomik di `.git` saat clone, jadi file index tidak pernah selesai ditulis | Commit salah itu belum sempat di-push; dibatalkan dengan `git reset --mixed <commit-benar>`. **Selalu cek `git status` / `git show --stat` sebelum push.** Kalau muncul banyak `D` (hapus) yang tidak disengaja: STOP, jangan push. |
| 2026-09-30 | Commit `95de2ce` berpesan ".gitignore", padahal ikut memuat hasil upload Ep. 2–6 (registry, antrian, manifest) | Upload dijalankan di VM tanpa `git_sync.sh push` sesudahnya, lalu commit berikutnya (oleh Claude Code) menyapu semua perubahan | Setelah upload/approve WAJIB langsung `bash git_sync.sh push "publish: …"`. `git_sync.sh push` kini menampilkan daftar file sebelum commit: baca daftar itu. |
| 2026-09-30 | Ep. 1 dijadwal SETELAH Ep. 7 dan 8 | `plan` lama menaruh item yang slotnya terlewat di slot paling akhir | `plan` baru mengurutkan ulang semua item QUEUED per nomor episode ke slot bebas paling awal (item yang sudah di YouTube tidak disentuh) |
| 2026-09-30 | Blender tarball resmi: `cannot execute binary file: Exec format error` (1.2 GB terbuang, sudah dihapus) | VM 99.3 memakai CPU **ARM64 (aarch64, Neoverse-N1)**, sedangkan build Linux resmi Blender hanya x64 | Cek `uname -m` sebelum memasang binary apa pun. Di VM ini pakai paket Ubuntu (`apt install blender`, arm64, Blender 5.0.1). Image Modal (GPU) = x64: di sana tarball resmi boleh dipakai. |
| 2026-10-01 | `ValueError: operands could not be broadcast` di audio race25d | Dua sinyal sintetis dengan durasi berbeda dijumlah langsung | Gabungkan sinyal beda panjang dengan overlay (`a[:len(b)] += b`) atau `place()`. Uji tiap rintangan baru dengan `--hazards`. |
| 2026-10-01 | Patch Python via heredoc di Git Bash gagal: `unexpected EOF while looking for matching '` | Teks patch berisi banyak kutip tiga (`'''`) dan backslash | Patch besar ditulis sebagai file `.py` (Write) lalu dijalankan; heredoc hanya untuk skrip pendek. |
| 2026-10-01 | Render batch race25d v2 di VM ternyata masih memakai kode lama (hasil identik) | `episodes.py reject` membuat tree VM kotor, lalu `git_sync.sh pull` di awal batch berhenti tanpa terlihat karena outputnya dipotong `tail -1` | Setelah reject/approve/render di VM, jalankan `git_sync.sh push` DULU, baru pull. Setelah pull, cek hash commit (`git log -1`) sebelum render. |
| 2026-10-02 | `git_sync pull` di VM berhenti: ada file untracked `monitor_harian.py` (script verifikasi bot user) di root repo | Bot user menaruh script-nya di dalam folder repo | Ditambahkan ke `.git/info/exclude` di VM (file tidak diubah). Agent lain: taruh script pribadi di luar `/root/video-engine` atau minta dicatat di exclude. |
| 2026-10-01 | Saat memasang cron: `git_sync pull` di VM berhenti karena EPISODES_INDEX.md belum di-commit (sisa `plan` uji) — cron upload besok akan STOP | `publish_queue.py plan` menulis ulang index/antrian; run manual tanpa `git_sync push` meninggalkan tree kotor | `daily_publish.sh` meng-commit catatan sisa (`git_sync push`) sebelum pull. Setiap run manual `plan`/`approve` harus diakhiri `git_sync push`. |
| 2026-10-01 | "Ready… GO!" versi suara C tidak jelas ("GO" terdengar "Geo"), ditemukan user | Chatterbox lemah untuk kalimat sangat pendek / satu kata | QA otomatis faster-whisper di Modal (ulang take, tolak skor <0.75). Hindari kalimat satu kata; pakai frasa ("Ready… set… let's go!"). |
| 2026-10-01 | Uji suara di VM memakai kode lama | `git_sync pull` berhenti karena folder pending sisa analisa CHALLENGE yang gagal (untracked); output `tail -1` menyembunyikannya | Batch menghapus folder seed gagal tanpa MP4. Selalu cek `git log -1` di VM setelah pull. |
| 2026-10-01 | `git pull --rebase` di PC berhenti di tengah ("local changes would be overwritten") padahal tidak ada perubahan isi | Google Drive mengubah metadata file sehingga git menganggap file berubah | Cek `git diff` (0 baris = aman), `git rebase --abort`, lalu `git pull --no-rebase`. Jangan reset paksa. |
| 2026-10-01 | `episodes.py reject` diam-diam gagal untuk 4 video (STOP: folder sudah ada) | Nama folder `rejected/<tanggal>_<seri>_s<seed>` sudah dipakai versi lama dengan seed sama; output reject tersaring `grep` | Reject memberi akhiran ID video saat bentrok. Folder render memuat versi mesin. Setelah reject massal, selalu cek status di registry. |
| 2026-10-01 | Render SMASH crash `min() iterable argument is empty` | Dua mobil terakhir gugur di tick yang sama, lalu "pemenang" yang dipilih sudah berstatus out, sehingga tidak ada mobil di layar | Mobil terakhir tidak pernah tereliminasi (HP minimal 1, ditahan di tepi). |
| 2026-10-01 | Narasi SMASH tertinggal dari video sampai 9,5 s dan masih terdengar setelah video habis (ditemukan user) | Penjadwal antrian sederhana (`max(want, busy)`) tanpa membuang kalimat; kalimat panjang; CTA berdurasi tetap 4,8 s | `schedule_narration`: kalimat wajib + kalimat aksi yang boleh dibuang dengan batas telat. Durasi CTA menyesuaikan. Jadwal narasi dicetak di log dan harus dicek di setiap seri baru. |
| 2026-10-01 | Render SMASH terlihat "mati" tanpa error, ternyata masih berjalan 50+ menit; 6 render saling berebut CPU | (1) Log baru ditulis di akhir, sehingga proses terlihat mati padahal hidup. (2) `np.convolve` ducking narasi O(N·K) sangat lambat | Selalu cek `ps` sebelum menjalankan render ulang. Matikan render usang. Ducking pakai `box_avg` O(N). Profil dengan `venv/bin/py-spy dump --pid`. |
| 2026-10-01 | `ssh ... 'pkill -f "smash25d..."'` memutus sesi ssh sendiri (exit 255) | Pola `pkill -f` cocok dengan baris perintah bash milik sesi ssh itu sendiri | Logika kill ditaruh di file script (`/tmp/restart_v2.sh`) dengan `pgrep -f` per PID. |
| 2026-10-01 | Pemenang SMASH ikut tereliminasi saat berputar merayakan | Pemeriksaan keluar arena dan penyempitan lantai tetap berjalan setelah ada pemenang | Eliminasi dan penyempitan dibekukan saat pemenang ditentukan (`FREEZE_T`). |
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
| 2026-09-30 | `KeyError: 'obstacle'` saat event `crash`/`lava` | Event baru terdeteksi di luar jalur yang mengisi `obstacle`/`x` | Setiap tipe event baru wajib mengisi `obstacle` & `x` (diisi setelah deteksi kalau belum ada). |
| 2026-09-30 | Aliran lahar latar gunung berapi memanjang sampai ke jalan; semburan melempar mobil terlalu tinggi | Titik akhir kurva di `horizon+40`; impuls `(m*2.5, m*10)` terlalu besar | Elemen latar harus tetap di dalam siluetnya. Setiap gaya/impuls baru dicek di PNG `L*_event.png` (kamera tidak boleh zoom-out berlebihan). |
| 2026-09-30 | Lava seed lolos di preview, tapi STOP saat render sungguhan (level 2) | Zona kena semburan diskalakan dengan panjang mobil → kendaraan panjang selalu kena. Preview tidak mengubah registry, jadi rotasi tokoh saat render berbeda dari preview | Zona bahaya jangan diskalakan dengan ukuran mobil. Setiap seri baru: `tune_cast.py <seri> <SEMUA tokoh> 1 2 3`, karena rotasi bisa memilih tokoh mana pun. |
| 2026-09-30 | `AttributeError: 'tuple' object has no attribute 'seed'` di semua seri | Variabel lokal `args` di `main()` menimpa hasil argparse `args` | Jangan pakai nama `args`/`a` untuk variabel sementara di `main()`. Setiap perubahan engine WAJIB lolos `test_all.sh` (smoke test ini yang menangkap bug ini sebelum commit). |
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
| 2026-09-30 | Siluet kota tidak tergambar | `-(a) % n` di Python bernilai positif, jadi tiling mulai di luar layar kanan | Tiling paralaks: `x = -(a % period)`. Selalu cek PNG untuk setiap tema baru (`--theme` + `--preview-only`). |
| 2026-09-30 | Kotak pink di latar gunung | Celah antar segitiga gunung memperlihatkan langit | Beri alas solid di bawah layer latar. |
| 2026-09-30 | Perintah PowerShell diblokir total | `Remove-Item` dengan path variabel dianggap berbahaya oleh sandbox | Tulis ke folder baru, jangan menghapus folder scratchpad lewat variabel. |

## D. Kebiasaan agent (Claude Code)

| Tanggal | Gejala | Penyebab | Pencegahan |
|---|---|---|---|
| 2026-09-30 | `python -c "..."` inline lewat ssh gagal parse (terjadi lagi setelah dicatat di bagian A) | Kebiasaan lama | Cek ulang perintah ssh sebelum dikirim: kalau ada kutip, kurung, pipe, atau `\|` di dalam argumen remote → pindahkan ke file script. |
| 2026-09-30 | `grep -n "a\|b\|c"` inline lewat ssh lagi (ke-4 kali): pola rusak jadi nama file | Terburu-buru membaca file server | Untuk MEMBACA file server: `scp` ke scratchpad lalu pakai Read/Grep lokal. Jangan pernah grep inline di argumen ssh. |
| 2026-09-30 | `git log --format="VM HEAD %h <%ae>"` inline lewat ssh: `syntax error near unexpected token newline` (ke-5 kali pelanggaran aturan ini) | Kutip dibuang PowerShell, lalu `<` `>` dibaca bash sebagai redirect | Semua perintah remote yang memuat kutip/`<>`/`\|` WAJIB lewat file script, termasuk perintah "kecil". |
| 2026-09-30 | Commit dari PC gagal diam-diam: `pathspec 'Claude' did not match`, lalu push tidak mengirim apa-apa dan preview VM jalan tanpa file baru | Pesan commit dalam kutip ganda PowerShell berisi `\$29`: `$` diekspansi dan `\"` merusak kutip argumen git | Pesan commit dari PowerShell SELALU dalam kutip tunggal `'...'`, tanpa `$`. Cek hash di `git show --stat` sebelum lanjut ke VM. |
| 2026-09-30 | `bash script.sh \| grep -E "a\|b"` lewat ssh: grep error, pipe putus, **script uji ikut mati** setelah percobaan pertama | Sama: kutip dibuang PowerShell; SIGPIPE mematikan script | Script panjang dijalankan dengan `nohup ... > file.out &`, lalu hasilnya dibaca lewat script ringkasan terpisah. Jangan pernah mem-pipe output script lewat argumen ssh. |
