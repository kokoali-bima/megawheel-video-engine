# DEV_HISTORY — MegaWheel Kids 2D Physics Engine

> **Sejak 2026-09-30 (v2.3):** engine ada di `/root/video-engine/generators/physics_2d/sim_engine.py` (VM sumber-mesin, 192.168.99.3).
> Entri v1–v2.2 di bawah masih menyebut path lama `/root/sim-prototype/...` (`sim_video.py`, `output/`). Itu catatan sejarah; path yang berlaku ada di `BLUEPRINT.md`.
> Standar produksi: lihat `BLUEPRINT.md` di folder yang sama.
> Aturan: setiap perubahan engine WAJIB menambah entri baru di BAWAH file ini (tanggal, siapa/agent apa, apa yang diubah, hasil, masalah).

---

## 2026-09-30 — v1: prototipe pertama (Claude Code, Opus)

**Tujuan:** mengganti footage hasil download (berisiko copyright) dengan video yang 100% dibuat sendiri.

**Yang dibuat**
- Venv terpisah `/root/sim-prototype/venv`: numpy 2.5, pymunk 7.3, pycairo 1.29, edge-tts.
- Paket apt: `libcairo2-dev pkg-config build-essential python3-dev` (dibutuhkan untuk build pycairo).
- Font Luckiest Guy (Apache) di `/root/.fonts`.
- Lintasan: 3 lubang (30–33.2 m, 54–62 m setelah ramp, 78–83 m), finish di 100 m.
- Kendaraan: sports car, school bus, monster truck. Engine mencoba 21 kecepatan per kendaraan dan memilih yang menghasilkan FAIL-FAIL-WIN.
- Audio sintetis: mesin, benturan, buzzer gagal, fanfare, BGM. Narasi Edge-TTS en-US-AnaNeural.
- Hasil: `output/SIM_POTHOLES_S001.mp4` (41.6 s, render 31 s). Kode disimpan di `archive/sim_video_v1.py`.

**Pelajaran (JANGAN DIULANG)**
- pymunk 7: body harus di-`space.add()` **sebelum** shape-nya, kalau tidak muncul AssertionError.
- `SimpleMotor(chassis, wheel, rate)` membuat `wheel.w - chassis.w = -rate`. Rate POSITIF = mobil maju ke kanan. Engine punya pengecekan otomatis (`motor sign is wrong`) kalau mobil mundur.
- Python 3.14 memakai start method `forkserver` secara default. Render paralel wajib `mp.get_context("fork")` supaya data global ikut ke worker.
- Upload dari Windows lewat PowerShell: JANGAN memakai `sed s/\r$//` lewat ssh, karena quoting menghapus huruf `r` di akhir baris dan merusak kode. Konversi CRLF→LF di lokal sebelum `scp`.
- PowerShell 5.1 membuang tanda kutip ganda di argumen ssh. Pipeline/regex yang rumit sebaiknya ditaruh di script, bukan di command line.

## 2026-09-30 — v2: fitur "epic" (Claude Code, Opus)

**Yang ditambahkan**
- Perekaman state 120 Hz (fisika 240 Hz) → memungkinkan slow motion halus.
- **Bullet-time** 0.38x saat mobil melayang di atas lubang besar (setelah ramp).
- **INSTANT REPLAY** 0.4x (±1.7 s di sekitar crash) untuk level gagal yang hancur/terbalik, plus narasi "Let's see that again, in slow motion!".
- **Kamera dinamis**: zoom per kendaraan, zoom out saat melayang, zoom in 1.45x saat replay, guncangan saat benturan, speed lines saat > 12 m/s.
- **Mobil bisa hancur** (`break_dv`): roda depan (dan belakang kalau benturan sangat keras) lepas, 10 pecahan (panel, bemper, dop, kaca) jadi benda fisika, percikan api, retakan, asap.
- **Wajah & mood**: normal, scared, whoa, happy, dizzy + bintang berputar. Speech bubble UH OH! / WHOA! / OUCH! / YEAH! dengan suara pop dan gulp.
- **Nama maskot**: Zippy, Buster, Rocky (narasi ikut berubah).
- Bayangan di bawah mobil, lapisan tanah berwarna.
- SFX baru: kaca pecah, burung "tweet" (pusing), suara rewind, benturan diperlambat saat replay.
- Pemilihan run mengutamakan yang spektakuler (hancur/terbalik).
- Argumen CLI: `--fps 30|60`, `--name`, output baris `[result] {...}`.

**Hasil seed 1:** `output/SIM_POTHOLES_V2_S001.mp4`, 48.1 s, 11.2 MB, simulasi 13 s + render 39 s.
- L1 Zippy: pit di lubang 3, hancur, bullet-time, replay (17.3 s)
- L2 Buster: tersangkut di lubang 1, tidak hancur, tanpa replay (10.1 s)
- L3 Rocky: menang, bullet-time, outro (20.7 s)

**Masalah yang diketahui / belum selesai**
- Buster (bus) tidak pernah hancur di lintasan ini (benturannya pelan), jadi level 2 terasa datar.
- Bubble "WHOA!" bisa muncul saat bus terperosok, bukan hanya saat melompat.
- Level 1 lebih dari 12 s (target cetak biru) karena ada replay.
- Belum ada audit otomatis dan registry keunikan (lihat roadmap di BLUEPRINT.md). → selesai di v2.1

## 2026-09-30 — v2.1: standar baku ditegakkan oleh engine (Claude Code, Opus)

**Tujuan:** kualitas konsisten, tidak bergantung pada ketelitian agent (kasus: agent lain membuat video dengan mobil mundur dan tanpa rintangan).

**Yang ditambahkan**
- `analyze()` di engine = gerbang analisa BLUEPRINT 5.1 (maju +x, rintangan ada, pola cerita, tanpa timeout, waktu event, momen spektakuler, durasi, keunikan). Kalau ada FAIL → `[analysis] STOP`, tidak dirender, exit 1.
- `audit.py` = audit BLUEPRINT 6 (dijalankan otomatis setelah render; bisa manual): ffprobe, volumedetect, CTA, jumlah narasi, **warna piksel** badge LEVEL/FAIL/WINNER dan panel outro di detik kejadian, preview, keunikan. Output `_audit.md` + `_audit.json`. Gagal → status `AUDIT_FAILED`, exit 5.
- `registry.py` + `PRODUCTION_REGISTRY.json` = BLUEPRINT 7. Menolak seed yang sudah dipakai dan sidik jari duplikat (`[registry] STOP`). Entri ditulis otomatis setelah audit.
- **Lintasan acak per seed** (`make_track`): posisi, lebar, dan kedalaman 3 lubang serta ramp diacak dari seed. Seed 1 = lintasan referensi `potholes_std` (tidak berubah).
- **Pemilihan run berdasarkan pacing** (`pick_combo`): semua kombinasi run dihitung durasinya, lalu dipilih yang total 42–49.5 s, level gagal ≤ 20 s, level menang ≤ 24 s, minimal 1 momen spektakuler. Skor mengutamakan rintangan gagal yang berbeda.
- Perbaikan dari audit v2: bubble/ekspresi "WHOA" hanya saat benar-benar melompat di atas permukaan jalan (tidak lagi saat bus terperosok). Replay dipersingkat (±1.35 s sumber) dan jeda setelah gagal dipersingkat.
- VIDEO_ID default otomatis `SIM_POTHOLES_V2_S<seed>`; argumen baru `--force`, `--allow-duplicate`.

**Hasil uji**
- Seed 1 (render ulang, `--force`): LOLOS audit, 46.9 s (L1 16.3 s, L2 9.9 s, L3 20.7 s).
- Seed 2 (lintasan acak `potholes_dc6ea3dd`): LOLOS audit, 48.9 s, Zippy terbalik + hancur.
- Uji negatif audit: di frame tanpa badge, rasio piksel badge = 0% (audit memang bisa gagal).
- Sebelum `pick_combo`: hanya 1 dari 8 seed lolos analisa (durasi > 50 s). Sesudahnya: 8 dari 9 seed lolos (seed 2–10, hanya seed 5 gagal).
- Registry menolak `--seed 2` ulang dan `--seed 2 --name LAIN`.

**Masalah yang diketahui**
- Di lintasan acak, bus hampir selalu `stuck`, dan kedua level gagal sering di rintangan yang sama (WARN `distinct_fail`). Variasi hasil masih sempit → perlu jenis rintangan baru (roadmap 1).
- Level 1 masih 15–17 s (target 12 s).

**Pelajaran (JANGAN DIULANG)**
- Perintah ssh dari PowerShell yang memuat `|` atau tanda kutip di dalam argumen remote: quoting rusak, dan `grep` tanpa file bisa menggantung selamanya menunggu stdin. Taruh logika di script (`find_seeds.sh`), dan pakai `< /dev/null`.
- Menjalankan `--preview-only` untuk seed yang sudah dirender akan menimpa manifest/preview video itu. Jangan dilakukan untuk seed yang sudah jadi.

**File bantu:** `find_seeds.sh <dari> <sampai>` mencoba banyak seed dengan `--preview-only` dan melaporkan PASS/FAIL (output yang gagal otomatis dihapus).

## 2026-09-30 — v2.2: seri kedua + roster karakter (Claude Code, Opus)

**Tujuan:** video tidak terasa sama terus (temuan v2.1: bus selalu `stuck`, level gagal di rintangan yang sama).

**Yang ditambahkan**
- **Sistem seri** (`SERIES_DEFS`, `--series auto|potholes|bumps`). `auto` memilih seri yang videonya paling sedikit di registry. VIDEO_ID: `SIM_<SERI>_V2_S<seed>`. Judul layar/YouTube, tag, dan kata rintangan di narasi mengikuti seri.
- **Seri 2 "Cars VS Giant Speed Bumps"** (`make_bumps_track`, `BUMP_CFG`): 4–5 gundukan setengah-sinus bergaris kuning-hitam, makin tinggi (0.6 → maks 2.7 m), gundukan pertama di 40–44 m, finish 10 m setelah gundukan terakhir, kecepatan uji ×1.25.
- **Roster**: 3 karakter baru, yaitu Siren (mobil polisi, lampu berkedip), Blaze (pemadam kebakaran, tangga + lampu), dan Crusher (monster truck hijau). Seed memilih 1 kendaraan per peran (ringan / berat / juara). Potholes seed 1 tetap sports-bus-monster.
- Narasi intro memakai template (`{lvl}`, `{obst}`).
- **Timing narasi**: event boleh terjadi saat intro masih berjalan (min = maks(2.5 s, intro − 1 s)). Narasi hasil otomatis menunggu intro selesai, dan level diperpanjang kalau perlu supaya narasi tidak terpotong replay/outro.
- **Batas durasi per seri** (`max_fail`, `max_win`), jeda outro dirapatkan (+0.3 s / +0.8 s).
- **Definisi "spektakuler"** diperluas: hancur / terbalik / lompatan bullet-time di level gagal. Skor tetap mengutamakan hancur/terbalik.
- Bullet-time memilih lompatan tertinggi terlama sebelum hasil (tidak lagi khusus ramp potholes).
- Pesan STOP kombinasi sekarang berisi diagnosis (jumlah kombinasi yang lolos tiap syarat + durasi kandidat per level).
- `tune_bumps.py`: uji fisika cepat per parameter lintasan (tanpa TTS/render).

**Riwayat tuning speed bumps (JANGAN DIULANG)**
| Percobaan | Parameter utama | Hasil |
|---|---|---|
| 1 | tinggi 0.45 + 0.3–0.42/gundukan, lebar landai | mobil ringan & fire truck menang di hampir semua kecepatan |
| 2 | dh 0.45–0.6, jarak 10–14 | mobil ringan gagal terlambat (14–18 s), monster sering gagal |
| 3 | dh 0.6–0.8, h_max 2.9, jarak 6.5–8.5, mulai 17–20 m | ringan gagal di 13–15 s atau 3–4 s (terlalu awal) |
| 4 | + gundukan curam (wk 0.65–0.85) | ringan hanya `stuck`, monster gagal (terlalu curam) |
| 5 (dipakai) | mulai 40–44 m, wk 0.85–1.1, h_max 2.7, 4 gundukan | berat stuck 6–10 s, monster menang di kecepatan rendah–sedang |
| + | batas level per seri, timing narasi, definisi spektakuler | **8/10 seed bumps lolos**, potholes 6/6 (seed 3–8) |

**Hasil uji**
- `SIM_BUMPS_V2_S006`: LOLOS audit, 49.3 s (Zippy terpental lalu terbalik, Buster tersangkut, Rocky menang).
- Preview potholes seed 8 (Siren + Blaze): visual karakter baru OK.

**Masalah yang diketahui**
- Kendaraan berat hampir selalu `stuck` (potholes: selalu di lubang 1). Variasi kegagalan kendaraan berat masih sempit.
- Seri bumps paling sering berakhir `stuck`, dan momen terbaliknya jarang. Kombinasi dengan crash mendapat skor lebih tinggi, tapi tidak selalu tersedia.
- Perubahan timing outro (v2.2) membuat render ulang potholes seed 1/2 tidak lagi identik dengan video v2.1 yang sudah ada. Video lama tetap valid; jangan render ulang tanpa `--force`.

**Pelajaran (v2.2)**
- Semua perintah diagnostik ke server lewat file script (`find_seeds.sh`, `work/diag.sh`, `work/render.sh`, `work/peek.sh`). Inline `grep "a|b"` atau JSON lewat ssh dari PowerShell selalu rusak.

## 2026-09-30 — v2.3: satu engine di /root/video-engine + tokoh tetap (Claude Code, Opus)

**Tujuan:** tidak ada lagi 2 engine di 1 VM; tokoh menjadi pemeran tetap yang dirotasi.

**Yang dilakukan**
- `video-engine.service` (FastAPI `server.py`, port 8000, pipeline footage) **di-stop & disable**. Audit agent lain: 0 request sejak 29-09, dan port hanya boleh diakses dari 99.2.
- Backup lengkap sebelum migrasi: `/root/backups/pre-merge-20260930.tar.gz` (367 MB: video-engine tanpa venv, sim-prototype tanpa venv/work, renders/youtube_shorts_batch, unit systemd, credentials).
- Migrasi (hanya pindah, tanpa hapus):
  - `server.py`, `pipeline.py`, 10 modul footage di `core/`, ±35 script sekali-pakai, `presets/`, registry footage, dan dokumen lama → `archive/footage_pipeline/`
  - Engine 2D → `generators/physics_2d/` (`sim_video.py` diganti nama menjadi `sim_engine.py`, + audit, registry, find_seeds, tune_bumps)
  - Output → `renders/`, registry → `/root/video-engine/PRODUCTION_REGISTRY.json`, cache TTS → `work/physics_2d/`
  - Path di 9 manifest/audit + registry ditulis ulang
  - Satu venv: pymunk, pycairo, numpy, edge-tts dipasang ke `/root/video-engine/venv`
  - `/root/sim-prototype` → `/root/sim-prototype.MIGRATED` (menunggu hapus permanen)
- Dipertahankan: `core/youtube_uploader.py`, `core/tracker.py`, `upload_cli.py`, `auth_*.py`, `credentials/`, `VIDEO_PUBLISHING_TRACKER.*`, `PROJECT_HISTORY_AND_HANDOVER.md`.
- **Tokoh tetap** (`cast/characters.json` + `cast/CAST.md`): 6 tokoh dengan nama, warna, sifat, kalimat khas, dan rival. Engine membaca identitas dari sini (`load_cast`).
- **Ganti nama** sebelum pernah dirender/diupload: Blaze → **Hydro** (pemadam), Crusher → **Grizzly** (monster hijau). Alasan: sama dengan tokoh serial *Blaze and the Monster Machines*.
- **Rotasi adil**: `make_story` memilih tokoh yang paling jarang tampil per peran (dihitung dari registry). Seed dipakai untuk tie-break. Akibatnya susunan tokoh sebuah seed bergantung pada isi registry (tetap tercatat di manifest).
- Koreksi: di laporan v2.2 tertulis "7 karakter", yang benar **6**.

**Hasil uji**
- Audit ulang `SIM_POTHOLES_V2_S002` dengan path baru: PASS.
- `core.youtube_uploader` + `core.tracker` import OK, `upload_cli.py --help` OK (tidak ada upload).
- Render baru `SIM_BUMPS_V2_S001` (seri otomatis → bumps, rotasi → **Siren, Hydro, Grizzly**): 49.2 s, audit PASS.

## 2026-09-30 — v2.4: 10 tokoh + rebrand ke MegaWheel Arena (Claude Code, Opus)

**10 tokoh:** +Nitro (F1), Tilly (taksi), Titan (big rig, 4 roda), Sprinkles (es krim). `ROSTER` = 4 ringan / 4 berat / 2 juara. `ROLE_ORDER` + fallback otomatis kalau tokoh tidak bisa memberi hasil yang diminta di lintasan itu. `tune_cast.py` untuk uji tokoh baru. Banner digambar ulang dengan 10 tokoh.

**Rebrand (keputusan user):** tujuan utama monetisasi + penonton semua umur → channel **MegaWheel Arena**, setting "Tidak dibuat untuk anak-anak".
- `CHANNEL` konstanta; CTA: "...and smash SUBSCRIBE to MegaWheel Arena!" (engine + audit)
- Narator: `en-US-AvaNeural` (wanita dewasa enerjik), menggantikan suara anak `en-US-AnaNeural`. Sampel pembanding: `branding/voice_samples/` (Ava, Aria, Jenny, Emma).
- Tag/deskripsi video tanpa kata "kids"; teks outro di layar = nama channel.
- Banner & foto profil: "MEGAWHEEL ARENA", tagline "EPIC CAR CHALLENGES - WHO SURVIVES?".
- Semua video lama berstatus `RENDERED_PENDING_APPROVAL` (6 video, CTA "MegaWheel Kids" + suara anak) → **`SUPERSEDED_REBRAND`**. Tidak untuk diupload, dan tidak dihitung dalam rotasi/keunikan.
- BLUEPRINT Aturan Nol no. 7: aturan audiens semua umur.

## 2026-10-01 — v3.4: race25d engine v2 — pindah jalur (menghindar) + end card gaya YouTube (Claude Code, Opus)

Permintaan user: peserta bisa pindah jalur untuk menghindari rintangan, supaya pemenang tidak terlihat sekadar beruntung; animasi LIKE/SUBSCRIBE dibuat mirip tombol YouTube dan diberi highlight seperti video-video awal.

- **Rintangan tidak lagi terikat ke mobil.** Rintangan mengenai mobil mana pun yang berada di lajurnya saat ia tiba (dicek lewat `z` saat itu). Setiap rintangan hanya kena sekali, setiap mobil hanya bisa kena sekali.
- **AI menghindar.** Mobil melihat rintangan darat 9–26 m di depan pada lajurnya (genangan, lubang, lahar, dinding, pres, laser; ramp/meteor/UFO/naga tidak bisa dihindari). Mobil lincah (`AGILITY` ≥ 0.55: F1, sports, polisi, taksi, monster truck) selalu mencoba menghindar. Kendaraan besar (bus, damkar, truk es krim, truk gandeng) hanya kadang-kadang, sesuai peluangnya (0.3–0.45), dan diundi sekali per pasangan mobil–rintangan. Mobil pindah ke lajur sebelah yang kosong: tidak ada mobil dalam jarak 5 m dan tidak ada rintangan dalam 30 m. Kalau terhalang, mobil ngebut melewati tetangga yang sejajar/di belakang (×1.18) atau mengerem di belakang tetangga yang di depan (×0.8) sampai ada celah (jarak pandang 9–40 m). Setiap set rintangan acak dijamin punya minimal 1 rintangan darat yang bisa dihindari. Perpindahannya mulus, ±1.9 lajur/detik. Batas `MAX_DODGES = 1` per video, supaya tetap ada minimal 2 rintangan yang kena.
- Dodge muncul sebagai event `dodge`: bunyi whoosh, bubble "NICE!", narasi "Nice move! X dodges the lava vent!", kamera menyorot aksinya, preview `dodge.png`, dan outcome `+dodge_<rintangan>`. Mood: "scared" kalau ada rintangan di lajur sendiri, "happy" sesaat setelah berhasil menghindar.
- Cek otomatis "3 hazards triggered" diganti menjadi **"at least 2 hazards hit"**.
- **End card gaya YouTube:** panel putih dengan avatar "MW", nama channel, dan "New races every day!". Tombol LIKE abu-abu (ikon jempol) dan SUBSCRIBE merah. Sebuah tangan kartun mengetuk LIKE: tombol membiru, muncul "+1". Lalu SUBSCRIBE diketuk: berubah abu-abu "SUBSCRIBED", lonceng bergoyang, ada percikan bintang. Cincin highlight kuning berdenyut di tombol berikutnya. Suara klik dan lonceng. Panel diletakkan di bawah judul "X WINS!".
- **Engine version race25d → v2** (ID `SIM_RACE25D_V2_S###`). Pending v1 S002–S007 di-REJECT dengan alasan "superseded by race25d v2", lalu seed 2–7 dirender ulang sebagai v2. S001 v1 (Ep. 9, approved) tetap.
- Hasil render v2 S002–S007: semua PASS, `empty_frames=0`, 4 dari 6 video ada aksi menghindar. S003: Rocky menghindari lahar lalu menang. S004: Zippy menghindari lubang lalu menang. S005: Tilly menghindari dinding tapi kena meteor. S007: Nitro menghindari genangan lalu menang. Di S002 dan S006 si bus (Buster) terlalu kaku untuk menghindar.
- Catatan proses: render v2 pertama belum membawa kode terbaru karena `git_sync pull` di VM berhenti (tree kotor oleh catatan reject). Solusi: `git_sync push` dulu, baru pull (sesuai SOP).
- Uji: 6 seed dengan set paksa `puddle,lava,wall`, semua PASS, `empty_frames=0`. Dodge terjadi di seed 101 (Nitro menghindari lahar) dan 102 (Grizzly menghindari lahar).

## 2026-10-01 — v3.3: perpustakaan rintangan 2.5D + naga (Claude Code, Opus)

**Keputusan user:** program harian 11:00 CHALLENGE · 15:00 RACE · 19:00 SMASH ARENA; tambah meteor, UFO, rintangan yang membuat mobil **penyet** dan **terbelah**; **naga api** (kena → melambat karena ganti ban) dan **naga es** (kena → membeku sesaat lalu lanjut).

- `race25d.py` diubah dari 2 rintangan tetap menjadi **perpustakaan `HAZARDS`** (bobot, bubble, narasi, prioritas replay, jendela slow-mo). Tiap video: 3 rintangan berbeda, 1 per lajur, posisi acak; `--hazards a,b,c` untuk uji.
- Rintangan baru, semuanya prosedural (cairo) + suara sintetis:
  - **lubang:** terperosok lalu memantul.
  - **lahar:** air mancur lahar, mobil terlempar dan gosong berasap.
  - **dinding beton:** tabrak, terpental, serpihan, lalu memutar lewat samping.
  - **mesin pres:** pipih 26% lalu BOING (pegas).
  - **gerbang laser:** terbelah dua (clip dua bagian) + percikan, lalu plester.
  - **meteor:** bola api jatuh, ledakan, gelombang kejut, salto 360°, kawah.
  - **UFO:** sinar penarik, diangkat, dibawa mundur 14 m, lalu dijatuhkan.
  - **naga api:** naga kartun merah terbang masuk, menyembur api → gosong, berhenti ganti ban (ikon ban & kunci pas), lalu lebih pelan.
  - **naga es:** naga biru → balok es transparan 1.7 s → pecahan es → lanjut.
- Kamera: fokus ke mobil yang terkena; untuk naga, kamera membingkai mobil + naga.
- Pemeriksaan baru: `3 hazards triggered` (+ tetap `no frame without a car`).
- **Uji:** 3 set paksa mencakup kesembilan rintangan baru → semua PASS, empty_frames=0.
- **Bug saat uji:** suara laser menjumlah dua array dengan panjang berbeda (ValueError); naga di luar frame (titik melayang terlalu jauh) → diperbaiki.

## 2026-10-01 — v3.2: kamera race25d tidak pernah kosong + peran slot jadwal (Claude Code, Opus)

**Masukan user:** video race25d pertama siap tayang (→ **Ep. 9**). Video kedua ditolak: ada saat kamera tidak memperlihatkan satu mobil pun ("tidak boleh terjadi"). Jadwal: setiap hari wajib 1 Shorts balapan 2.5D; slot 11:00 / 15:00 / 19:00 ET; video 15 menit **Sabtu 19:00 ET**.

- **Penyebab:** saat pindah adegan (balapan → REPLAY → CTA) kamera *menggeser pelan* dari posisi finish ke mobil yang spin, sehingga melewati jalan kosong.
- **Perbaikan** (`race25d.py`): *hard cut* di setiap pergantian adegan; aturan keras "mobil kunci (fokus atau pemimpin) selalu di tengah frame" (clamp camx ±380 px); **pemeriksaan wajib `no frame without a car`** (setiap frame dihitung; satu frame kosong = gagal).
- Video 2 dirender ulang (`SIM_RACE25D_V1_S002`, gurun, Tilly menang, narator Michelle): empty_frames=0. Seed 3–4 juga 0.
- **Peran slot** di `publish_queue.py`: 15:00 ET = race25d, 11:00/19:00 = seri lain, Sabtu 19:00 = `story15` (video panjang). `plan` mencetak PERINGATAN STANDAR kalau ada hari tanpa race25d. BLUEPRINT bagian 10 + kedua dokumen agent diperbarui (produksi wajib ≥1 race25d/hari, stok ≥3).
- Ide user dicatat (C1d): lokasi hutan/rally, gurun/Dakar, perkampungan; mode demolition derby.

## 2026-09-30 — v3.1: seri 2.5D "race25d" — tokoh 2D persis, dunia berlajur (Claude Code, Opus)

**Keputusan user:** hasil Blender 3D terasa berat, lambat, dan tokohnya tidak dikenali → minta 2.5D dengan bentuk kartun sama persis dengan 2D. Prototipe "paper cutout" dinilai **"sudah sesuai banget"**. 3D (Blender + Modal) ditunda, kodenya disimpan.

**Engine** `generators/lanes25d/race25d.py` (cairo, CPU VM, gratis):
- Tokoh digambar dengan fungsi 2D yang sama (`draw_body/draw_face/draw_wheel`, mood, tema, speed lines, splash, READY-GO, confetti, overlay replay).
- 4 lajur dengan kedalaman: k(z) = 9000/(100 + 25z) px/m; garis lajur, kerb, pohon/kaktus/palem dengan parallax; adegan dinaikkan 260 px (aksi di tengah frame Shorts).
- Kinematika skrip 120 Hz: genangan → spin 2 putaran menyeberang lajur + senggol (bubble HEY!), ramp → lompatan balistik slow-mo 0.35×, pendaratan squash + debu + guncangan.
- Kamera: menjaga rombongan (zoom-out min 0.82), condong ke drama, fokus pemenang di 30 m terakhir.
- **Variasi per seed:** tokoh (rotasi, maks 1 kendaraan besar & 1 monster truck), lajur, posisi genangan/ramp, kecepatan (pemenang bervariasi), tema & narator en-US (rotasi registry).
- **Audio:** narasi tanpa tumpang tindih (intro, spin, lompat, pemenang, replay, CTA), mesin, beep, splash + swish, benturan, pendaratan, fanfare, rewind, musik tema + ducking.
- **Timeline** ±29 s: balapan → pemenang + confetti → INSTANT REPLAY spin (0.4×) → CTA LIKE/SUBSCRIBE.
- Output `pending/<tanggal>_race25d_s<seed>/` + manifest + preview (spin/jump/winner/outro) + pemeriksaan ringan + registry.

**Uji:** seed 1–3 preview semua PASS (28.8–29.7 s; render 40–55 s termasuk TTS). Render nyata `SIM_RACE25D_V1_S001` (Nitro menang, tema kota, narator Emma) → pending. `test_all.sh` kini ikut menguji race25d.

**Perbaikan saat uji:** efek kedalaman terlalu lemah (kamera dinaikkan); jalan menyempit saat zoom-out (jalan dibuat lebih lebar dari layar); bubble tidak ikut zoom; pemenang keluar frame saat finish; `registry._active()` butuh argumen.

## 2026-09-30 — v3.0: mode 3D — Blender + Modal GPU, tokoh 3D, "sutradara" 3D (Claude Code, Opus)

**Keputusan user:** prototipe cairo pseudo-3D ditolak ("jauh dari layak tayang"). Mode 3D pakai renderer 3D sungguhan, sehemat mungkin sebelum monetisasi, tidak semua episode 3D (rencana 7–14 Shorts 3D/minggu + video 15 menit mingguan).

**Infrastruktur**
- VM 99.3 ternyata **ARM64** → Blender 5.0.1 dari apt (build resmi x64 tidak jalan). Benchmark CPU per frame 1080×1920: Workbench 6.7 s, Eevee 37 s, Cycles 49 s → terlalu lambat untuk produksi.
- **Modal** (user memasang kartu; batas workspace $30): `generators/blender3d/modal_render.py` dan `generators/director3d/modal_director.py`. Isinya Blender 5.2.2 x64 di image, Cycles + **OptiX** di L4, adaptive sampling, persistent data, render paralel per potongan, dan encode MP4 di container. **Budget guard** memakai ledger `modal_usage.json` (di-commit): run ditolak kalau total bulan + estimasi terburuk > **$29**.
- Benchmark Modal: 90 frame / 3× L4 = 51 s, $0.032 (0.85 s/frame).

**Tokoh 3D** — `generators/blender3d/cast3d.py`: 10 tokoh prosedural (warna dari `characters.json`, ciri khas per tokoh, mata kartun di kaca, senyum + lidah, roda di pivot dengan jari-jari agar putarannya terlihat). v2: mata lebih besar di tengah, senyum terlihat, cone Sprinkles di dudukan. Catatan user: "harusnya lebih kartun" → tugas C1b.

**Sutradara 3D (tahap 1)** — `generators/director3d/`:
- `motion.py`: simulasi balapan race3d (grip ban, spin di genangan) → gerak 30 fps + putaran roda + roll di tikungan + pitch saat gas/rem + bounce, semua lewat pegas teredam. Kamera follow ke pusat rombongan sungguhan (mobil yang tertinggal > 30 m diabaikan), versi horizontal (16:9) dan vertikal (9:16).
- `blender_scene.py`: jalan, kerb, garis, garis finish digabung jadi sedikit mesh; pohon berupa instance koleksi; genangan; tokoh cast3d dengan keyframe; motion blur.
- **Demo:** 15 s × 2 aspek = 900 frame di 8× L4: **147 s wall, $0.235** (1.02 GPU-s/frame). Estimasi: Shorts 3D 45 s ≈ $0.35.
- Kekurangan: spin masih kurang dramatis (tendangan yaw race3d lemah); balapan masih rapat dan landai → perlu "event sutradara" (spin besar, tabrakan, salip, finish) + HUD/narasi/audio.

## 2026-09-30 — v2.9: pacing lebih fleksibel, smoke test, indeks episode, prototipe Top-Down pseudo-3D (Claude Code, Opus)

**Engine Shorts (`sim_engine.py`)**
- `level_timing(..., allow_replay=False)`: setiap level gagal yang punya replay juga diberi varian **tanpa replay** (sekitar 3.4 s lebih pendek).
- `pick_combo` wajib menyisakan minimal 1 replay per video kalau ada level yang layak di-replay, dan memberi skor +0.8 per replay. Ini mewujudkan roadmap "replay hanya di level paling spektakuler".
- Seri splash: lintasan lebih pendek (awal 15–18 m, genangan 4.5–6.5 m, jeda antar rintangan 6–8 / 5.5–7 m).
- **Hasil B1:** splash 3/10 → **5/10** seed lolos (seed uji 901–910). Potholes 3/3, bumps 3/3, lava 2/3 (smoke test 901–903). Target 7/10 belum tercapai. Hambatan utama: level juara splash 22–25 s.

**Alat baru**
- `generators/physics_2d/test_all.sh [seri…] [--seeds A B]`: preview saja, tidak menyentuh registry. Wajib dijalankan sebelum commit perubahan engine. Pada sesi ini alat ini langsung menangkap bug `args` tertimpa di `main()` (ERROR_LOG B).
- `EPISODES_INDEX.md` (otomatis dari `episodes.py`/`publish_queue.py`): kartu identitas setiap episode (Ep. N → VIDEO_ID, path MP4, judul, seed, tema, narator, tokoh + hasil, slot tayang).
- `publish_queue.py`: slot terlewat dijadwalkan ulang, `--max` upload per run (kuota API), `publishAt` di uploader.

**Prototipe Top-Down 2.5D / pseudo-3D (`generators/topdown/race3d.py`)**
- Fisika: dunia datar pymunk tanpa gravitasi dengan model cengkeraman ban (friction circle, grip aspal 1.15, genangan 0.10), AI pure-pursuit per lajur, rem sebelum tikungan, menghindari mobil di depan, dan tendangan yaw saat hydroplaning (mobil berputar sungguhan).
- Render: proyeksi 3D sederhana di cairo (kamera 21 m di atas, 24 m di belakang, pitch 46°, FOV 72°). Mobil berupa kotak low-poly bershading dengan back-face culling dan painter's sort. Ada jalan berkelok dengan kerb merah-putih, rumput kotak-kotak, pohon, genangan, garis finish, jejak ban (skid mark), semprotan air, label nama, menara posisi dan progress bar.
- Uji: 14 s dirender dalam 41 s (1 proses), 1 mobil berputar di genangan. Status: **uji gaya**, belum ada audio, narasi, atau pipeline episode.

## 2026-09-30 — v2.8: suara air ≠ lava, mobil meleleh, hydroplaning, antrian upload (Claude Code, Opus)

**Masukan user (review v2.7):**
1. Suara lava dan air terdengar sama.
2. Mobil yang masuk kolam lahar harus terbakar dan bodinya meleleh.
3. Mobil ngebut di air harus tergelincir atau berputar, dan cipratan harus lebih nyata.

Tambahan dari user: jadwal upload 3 video/hari mengikuti jam US.

**Audio (dibangun ulang dengan filter FFT `_fband`)**
- Air (terang, cepat): tepukan, *sploosh*, desis semprotan, gelembung dengan nada NAIK (ciri khas air), tetesan (`synth_splash`); desis ban membelah air selama di genangan (`synth_water_rush`); *swish* saat berputar (`synth_spin`); cipratan besar + gelembung *glug* untuk kolam air (`synth_gurgle`).
- Lava (rendah, kental, lambat): *GLOOP* berat, *fwoomp* api, erangan logam panas, gelembung *blorp* lambat (`synth_lava_plunge`); gemuruh sub-bass + ledakan dalam + auman api + jatuhan batu (`synth_eruption`); api menyala (`synth_ignite`); api terus berkobar + gemeretak (`synth_fire`); ambience kolam lahar yang keras-lemahnya mengikuti jarak (`synth_lava_bed`).
- `synth_sizzle` (desis, mirip air) dihapus.

**Visual**
- Mobil di kolam lahar tenggelam pelan (`sink_offset`). Bodi memerah di bawah dan gosong di atas, melorot (squash), lelehan logam mengalir di bodi, tetesan membara (`melt_amount`). Ada lapisan lahar di depan mobil (`draw_pit_front`), cincin panas, gumpalan lahar kental terlempar (`draw_lava_splash`), api kartun + bara (`draw_fire`).
- Hydroplaning: `yaw` 2.5D (mobil diskalakan cos(yaw), terlihat berbalik arah saat berputar), ekspresi wajah kaget. Semprotan *rooster tail* per ban yang arahnya mengikuti yaw, kabut, riak, dan *crown splash* dua lembar air.
- Seri splash: lubang diganti kolam air dalam (`PIT_KIND="water"`). Mobil terlihat di bawah air, ada gelembung naik.
- Latar gunung berapi: alas solid (celah biru langit hilang).

**Fisika**
- `start_slide`: masuk genangan dengan vx > `SPIN_V` (6.5 m/s) → peluang spin naik dengan kecepatan (maks 80%, maks 1 spin per run, sisa tenaga 50%). Selain itu fishtail (visual). Ban besar monster truck lebih mencengkeram (×1.35). Salju: fishtail setelah mendarat keras.
- Menyentuh cairan di kolam = event `pit` seketika (bukan `stuck`).
- Lintasan lava: rintangan pertama di 32–36 m, kolam pertama lebih lebar.
- Narasi khusus: `crash_spun`, `pit_spun`, `rollback_spun`.

**Momen khas wajib (`signature`)**
- Seri splash wajib ada spin, seri lava wajib ada mobil meleleh.
- Tanpa momen itu, kombinasi ditolak dan engine pindah ke seed berikutnya.

**Antrian upload:** `publish_queue.py` + `publishAt` di uploader, slot 11:00/15:00/19:00 ET (BLUEPRINT bagian 10). Ep. 1–6 sudah direncanakan, belum diupload.

**Bug saat uji (diperbaiki):**
- Spin terlalu sering dan terlalu banyak membuang tenaga, sehingga durasi melebihi batas.
- Roda terlihat di bawah dasar kolam saat mobil tenggelam (sekarang di-clip).
- Pemilih kombinasi awalnya hanya "mengutamakan" momen khas, sehingga video tetap tanpa spin/lelehan. Sekarang wajib.

**Render (audit PASS, pending review):** `2026-09-30_splash_s007` (Tilly → Sprinkles → Titan, malam-gurun, Titan berputar di air) dan `2026-09-30_lava_s003` (Zippy meleleh di kolam lahar → Hydro → Titan). Render v2.7 dan percobaan tanpa momen khas dipindah ke `rejected/`.

## 2026-09-30 — v2.7: seri bahaya baru — genangan air, dinding, semburan lahar + SFX realistis (Claude Code, Opus)

**Masukan user:** perlu gaya lain: genangan air yang membuat mobil tergelincir dan menabrak, lahar yang keluar dari tanah; monster truck jangan selalu menang; suara efek visual harus terasa nyata.

**Yang ditambahkan**
- **Seri `splash` "Cars VS Splash Zone"** (`make_splash_track`, rng 6000+seed): urutan acak dari dinding beton, tanjakan, dan lubang. Setiap rintangan didahului genangan air dengan gesekan per segmen 0.06 (`PUDDLE_FRICTION`). Mobil bisa tergelincir, mundur di tanjakan basah (`rollback`), atau menabrak dinding (`crash`).
- **Seri `lava` "Cars VS Lava Road"** (`make_lava_track`, rng 7000+seed, tema dipaksa `volcano`): 3 ventilasi yang menyembur berkala (`vent_active`; impuls `(m*1.0, m*7.0)`) dan 2 kolam lahar (`PIT_KIND="lava"`, kolam kedua setelah ramp). Mobil yang kena menjadi `burned` (jelaga + asap hitam).
- Tipe event baru: `crash`, `rollback`, `lava`, masing-masing dengan narasi di `FAIL_LINES`.
- **Juara fleksibel**: `win_pool` di `SERIES_DEFS` (`"any"` = tokoh mana pun bisa menang, `"monsters"` = hanya monster truck). Rotasi juara memilih tokoh yang paling jarang menang (dihitung dari registry).
- **Rotasi tema** berdasarkan registry: kombinasi waktu dan lokasi yang paling jarang dipakai didahulukan. Lokasi baru `volcano` (gunung berapi berasap, aliran lahar di lereng), khusus seri lava.
- Visual: air genangan berkilau + cipratan roda, dinding beton bergaris merah-putih, retakan ventilasi yang menggelembung sebelum menyembur, air mancur lahar, kolam lahar bergelembung, beberapa ramp.
- **SFX sintetis baru**: `synth_splash` (saat roda depan masuk genangan), `synth_eruption` (setiap semburan; volume mengikuti jarak mobil ke ventilasi), `synth_sizzle` (saat terbakar), `synth_wall_crash` (saat menabrak dinding). Versi melambat dipakai di instant replay.

**Uji preview:** splash seed 1–3: 2/3 lolos (seed 1 STOP karena durasi). Lava versi pertama hanya 2/3 lolos di preview dan STOP saat render sungguhan. Setelah perbaikan zona semburan: `tune_cast` 9/9 tokoh bisa gagal/menang, **lava seed 1–6: 6/6 lolos**, juara bervariasi (Zippy, Titan, Buster, Sprinkles).

**Render penuh (audit PASS, status pending):** `2026-09-30_splash_s003` (Nitro → Titan → Tilly, 48.7 s) dan `2026-09-30_lava_s003` (Nitro → Hydro → Buster, night-volcano, narator Aria).

**Bug yang ditemukan saat uji (sudah diperbaiki):** `KeyError 'obstacle'` untuk event crash/lava (obstacle/x kini diisi setelah deteksi); aliran lahar latar terlalu panjang sampai ke jalan; semburan pertama melempar mobil terlalu tinggi sehingga kamera zoom-out berlebihan (impuls diturunkan dari `(m*2.5, m*10)`); zona kena semburan `1.5 + panjang/3` membuat bus/big rig selalu kena di ventilasi pertama (t≈2.8 s, terlalu awal), sehingga level 2 STOP. Perbaikan: kolom semburan sempit ±1.1 m (tidak bergantung panjang mobil), dan lintasan dimulai dengan kolam lahar, baru ventilasi.

## 2026-09-30 — v2.6: anti-monoton tahap 1 — tema, narator bergilir, audio jernih (Claude Code, Opus)

**Masukan user:** 6 episode pertama membosankan/monoton; narator harus lebih enerjik & jelas; boleh ganti narator tiap episode (en-US saja); setuju re-render Ep. 1–6 (opsi B).

**Yang ditambahkan**
- **Tema lingkungan** (`make_theme`, `TIMES`/`WEATHERS`/`LOCATIONS`): 4 waktu × 3 cuaca × 5 lokasi, acak dari seed dengan aturan (tanpa salju di gurun/pantai, tanpa hujan di gurun). Langit, matahari/bulan/bintang, awan, siluet kota (jendela menyala di malam hari), gunung bersalju, laut + pohon kelapa, bukit pasir + kaktus, warna tanah per lokasi, jalan basah, tepi jalan bersalju, overlay hujan/salju, tint waktu (sunset/malam), lampu mobil di malam hari. Cuaca mengubah gesekan (hujan ×0.72, salju ×0.55).
- **Musik per tema**: tempo, progresi akor, timbre lead; lonceng saat salju.
- **Narator bergilir** (`VOICES`, 5 suara wanita en-US), rotasi paling jarang dipakai. Delivery enerjik (rate +12%, pitch +2Hz), filter kejernihan ffmpeg (highpass 90 Hz, +4 dB @3 kHz, kompresor). **Ducking** mesin + musik −8 dB saat narator bicara.
- **"READY... GO!"** + beep di awal setiap level; **zoom punch** saat benturan keras.
- `--theme` (paksa tema untuk uji), **`--replace-episode N`** (render ulang episode APPROVED di tempat: seri/seed/tokoh/nomor/judul tetap; hanya ditukar kalau audit lolos).
- Registry/manifest mencatat `theme`, `voice`; sidik jari memakai `track_id@theme`.
- Sampel suara untuk user: `branding/voice_samples_v2/` (dicampur mesin + musik + ducking).

**Bug yang ditemukan saat uji visual (sudah diperbaiki):** siluet kota tidak muncul (titik awal tiling bernilai positif, tergambar di luar layar); celah kotak pink di antara kaki gunung (tambah alas solid).

## 2026-09-30 — v2.5: mulai bersih + sistem episode/season (Claude Code, Opus)

**Pembersihan (permintaan user):** semua video dihapus (`renders/*` 107 MB, `/root/renders` 298 MB termasuk video era BeamNG, salinan lokal). Registry lama → `archive/legacy_publishing/PRODUCTION_REGISTRY_pre_arena.json`; registry baru kosong. `upload_cli.py`, `core/tracker.py`, `VIDEO_PUBLISHING_TRACKER.*` → `archive/legacy_publishing/`.

**Struktur episode** (keputusan: per season/episode + tanggal di nama folder, bukan folder harian, karena nomor episode permanen sedangkan tanggal render/upload bisa bergeser):
- Engine menulis ke `renders/megawheel_arena/pending/<tanggal>_<seri>_s<seed>/` (preview-only ke `work/physics_2d/previews/`).
- `generators/publishing/episodes.py approve` → nomor episode berikutnya (tanpa bolong), Season = 30 episode, folder `S01/E001_<tanggal>_<seri>/`, judul `"... | Ep. N #Shorts"`. `reject` → `rejected/`. `set` → metrik evaluasi. `EPISODE_LOG.md` otomatis.
- `generators/publishing/publish.py <EP>` → upload hanya episode APPROVED, metadata dari manifest, kategori Film & Animation (1), `made_for_kids=False`, status + URL tercatat.
- Template deskripsi video (nama tokoh, seri, CTA channel) dan judul "Who Survives?".
- Audit: bisa dijalankan pada folder mana pun; tidak lagi menurunkan status episode APPROVED/UPLOADED.

**Bug kritis yang diperbaiki:** `core/youtube_uploader.upload_shorts` punya default `made_for_kids=True`, kategori Gaming, dan tag BeamNG/Kids. Kalau dibiarkan, setiap upload lewat script akan berlabel "dibuat untuk anak". Default sudah diubah, dan `publish.py` mengirim nilai eksplisit.

**Uji:** sandbox `/tmp` untuk episodes.py (approve → Ep.1, reject, approve → Ep.2 tanpa bolong, path diperbarui, metrik, mark_uploaded, re-approve ditolak) LOLOS. `publish.py` menolak episode yang belum di-approve.

**Pembersihan permanen (disetujui user, 2026-09-30):** dihapus `/root/local_videos` (325 MB footage BeamNG), `/root/sim-prototype.MIGRATED` (183 MB), dan 6 draft render di root `/root/renders` (V4–V7, FINAL_MASTERPIECE, VIDEO_02_POLICE). **Dipertahankan:** 8 MP4 di `/root/renders/youtube_shorts_batch/` karena masih dirujuk `VIDEO_PUBLISHING_TRACKER.json` (tracker berisi 9 entri: 3 sudah tayang + draft; `VIDEO_03_SUV_POLICE_TURBO_COUPE.mp4` sudah tidak ada sejak sebelum pembersihan). Backup `/root/backups/pre-merge-20260930.tar.gz` tetap ada.
