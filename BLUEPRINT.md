# CETAK BIRU — MegaWheel Arena 2D Physics Video Engine

> Versi: 1.3 (2026-09-30) · Engine: **physics_2d v2.3** di `/root/video-engine` (2 seri, 6 tokoh tetap, analisa/audit/registry otomatis)
> Berlaku untuk SEMUA agent (Antigravity/Gemini, Claude Code, OpenAI/Codex, dll.) dan operator manusia.
> Baca dokumen ini SAMPAI HABIS sebelum membuat, mengubah, atau mengaudit video.

---

> **Agent yang ditugasi produksi atau jadwal upload:** baca juga `AGENT_VIDEO_PRODUCER.md` (buat video, tanpa upload)
> atau `AGENT_UPLOAD_SCHEDULER.md` (jadwalkan episode APPROVED). Riwayat render ada di `PRODUCTION_LOG.md`.

## 0. Aturan Nol (baca dulu)

1. **Jangan menulis engine baru.** Semua video 2D MegaWheel Arena WAJIB dibuat dengan engine yang sudah ada (bagian 1). Kalau kamu merasa perlu menulis script fisika/render sendiri, BERHENTI dan tanya user.
2. **Jangan pakai pipeline footage lama** (`/root/video-engine/archive/footage_pipeline/`: server.py, downloader, scene detector, dll.). Itu sudah pensiun karena memakai footage pihak lain. `video-engine.service` (port 8000) sengaja di-stop & disable.
6. **Nama dan sifat tokoh sudah baku** (`/root/video-engine/cast/`). Jangan ganti atau karang tokoh baru tanpa izin user.
7. **Audiens: SEMUA UMUR, bukan konten anak** (keputusan user 2026-09-30, channel **MegaWheel Arena**, setting YouTube "Tidak dibuat untuk anak-anak"). Konsekuensi wajib:
   - Jangan pakai kata "kids", "for kids", "children", atau "toddler" di judul, deskripsi, tag, teks layar, maupun narasi.
   - Narator: **bergilir per episode** di antara suara wanita dewasa **en-US saja** (`VOICES`: Aria, AvaMultilingual, EmmaMultilingual, Jenny, Michelle). Yang paling jarang dipakai didahulukan. DILARANG suara anak (`en-US-AnaNeural`) dan aksen non-US (keputusan user). Gaya enerjik (rate +12%, pitch +2Hz) + filter kejernihan + ducking 8 dB pada mesin/musik saat narator bicara.
   - Gaya bahasa: kompetisi / crash test / "who survives?", bukan bahasa balita.
   - Tetap aman untuk keluarga: tanpa darah/sadis, tanpa kata kasar. Tokoh kartun berwajah boleh (ciri khas channel).
3. **Video harus lolos Analisa (bagian 5) dan Audit (bagian 6)** sebelum preview dikirim ke user.
4. **Dilarang upload ke YouTube tanpa kata "approved" / perintah upload eksplisit dari user.**
5. **Setiap video harus unik**: cek dan catat di registry (bagian 7).

Contoh kegagalan nyata yang dicegah dokumen ini: agent membuat script sendiri → mobil berjalan mundur dan lintasan tanpa rintangan. Penyebabnya salah mengenali mesin dan tidak ada analisa/audit.

---

## 1. Identitas Engine (jangan sampai salah mesin)

| Item | Nilai pasti |
|---|---|
| Server | VM **sumber-mesin**, IP privat `192.168.99.3`, SSH port `22022`, user `root` |
| Folder engine | `/root/video-engine/` |
| File engine (satu-satunya) | `/root/video-engine/generators/physics_2d/sim_engine.py` |
| Audit otomatis | `/root/video-engine/generators/physics_2d/audit.py` (dipanggil otomatis oleh engine; bisa dijalankan manual) |
| Registry keunikan | `/root/video-engine/generators/physics_2d/registry.py` + `/root/video-engine/PRODUCTION_REGISTRY.json` |
| Python | `/root/video-engine/venv/bin/python` (satu venv untuk engine + uploader) |
| Tokoh tetap | `/root/video-engine/cast/characters.json` + `cast/CAST.md` |
| Episode & upload | `generators/publishing/episodes.py` (approve/reject/log) + `generators/publishing/publish.py` (upload HANYA episode APPROVED) + `core/youtube_uploader.py` |
| Repo GitHub (private) | `kokoali-bima/megawheel-video-engine`, branch `main`. Push dari 99.3: `cd /root/video-engine && git push` (deploy key `/root/.ssh/id_ed25519_megawheel`, alias ssh `github-megawheel`) |
| Library | pymunk 7.x (fisika), pycairo (grafis), numpy, edge-tts |
| Font | `/root/.fonts/LuckiestGuy-Regular.ttf` |
| Output | `/root/video-engine/renders/megawheel_arena/pending/<tanggal>_<seri>_s<seed>/` berisi `<VIDEO_ID>.mp4`, `<VIDEO_ID>.json` (manifest), `<VIDEO_ID>_audit.md`, `preview/*.png`. Setelah approve: `renders/megawheel_arena/S01/E001_<tanggal>_<seri>/`. Daftar episode: `renders/megawheel_arena/EPISODE_LOG.md` |
| Versi lama | `/root/video-engine/archive/physics_2d_v1/sim_video_v1.py` (jangan dipakai untuk produksi) |

### Perintah resmi (dijalankan di 99.3)

```bash
cd /root/video-engine
./venv/bin/python generators/physics_2d/sim_engine.py --seed <N>                  # seri otomatis (yang videonya paling sedikit)
./venv/bin/python generators/physics_2d/sim_engine.py --series bumps --seed <N>   # atau pilih seri: potholes | bumps
./venv/bin/python generators/physics_2d/sim_engine.py --series potholes --seed <N> --preview-only   # analisa + PNG saja (~25 s)
./venv/bin/python generators/physics_2d/audit.py <VIDEO_ID>                      # audit ulang video yang sudah ada
bash generators/physics_2d/find_seeds.sh <series> <dari> <sampai>                # cari seed yang lolos analisa (tanpa render)
# opsional: --fps 60 (lebih halus, render ~2x lebih lama)
# opsional: --theme <waktu>,<cuaca>,<lokasi>  (paksa tema, untuk uji; default acak dari seed)
# render ulang episode APPROVED (belum diupload) di tempat, dengan tokoh/nomor/judul tetap:
./venv/bin/python generators/physics_2d/sim_engine.py --replace-episode <EP>
# JANGAN pakai --force / --allow-duplicate kecuali diminta user
```

- VIDEO_ID otomatis: `SIM_<SERI>_V2_S<seed 3 digit>`, misalnya `SIM_POTHOLES_V2_S004` atau `SIM_BUMPS_V2_S006`. Tidak perlu `--name`.
- Seed yang sama (di seri yang sama) menghasilkan video yang sama persis (deterministik).
- **Setiap seed punya lintasan sendiri DAN susunan karakter sendiri** (bagian 4.1). Pengecualian: potholes seed 1 = lintasan dan karakter referensi.
- Kalau engine berhenti dengan `[analysis] STOP` atau `[registry] STOP`: itu **perlindungan, bukan error**. Cukup pakai seed berikutnya. Tingkat lolos saat ini: potholes ±9/10 seed, bumps ±8/10 seed. Pesan STOP kombinasi menyertakan diagnosis (berapa kombinasi gagal di syarat mana).

### Arti exit code
| Exit | Arti | Tindakan agent |
|---|---|---|
| 0 | Render selesai, audit LOLOS, status `RENDERED_PENDING_APPROVAL` | Kirim preview ke user |
| 1 | `STOP` dari analisa / registry (video tidak dirender) | Coba seed lain |
| 5 | Render selesai tapi audit GAGAL (`AUDIT_FAILED`) | Jangan kirim. Baca `_audit.md`, laporkan ke user/developer |

### Tanda engine yang BENAR bekerja (sidik jari)

Log berisi baris-baris ini, berurutan:
```
[track] potholes_xxxxxxxx {...}        (atau bumps_xxxxxxxx)
[story] potholes: police(fail) -> bus(fail) -> monster(win)
[font] Luckiest Guy
[sim] sports: ...   [sim] bus: ...   [sim] monster: ...
[timeline] 4x.xs, NNNN frames @ 30fps
[analysis] OK   forward: ...          (10 baris analisa)
[preview] /root/video-engine/renders/megawheel_arena/pending/<tanggal>_<seri>_s<seed>/preview
[render] NNNN frames in xx.xs -> .../pending/<tanggal>_<seri>_s<seed>/<VIDEO_ID>.mp4
[audit] PASS -> .../pending/<tanggal>_<seri>_s<seed>/<VIDEO_ID>_audit.md
[result] {"video_id": ..., "status": "RENDERED_PENDING_APPROVAL", ...}
```
Kalau tidak ada `[sim]`, `[analysis]`, `[audit]` dan `[result]`, berarti kamu TIDAK memakai engine ini.

---

## 2. Cara Kerja Engine (model mental untuk agent)

```
1. SIMULASI   pymunk 240 Hz, gravitasi 9.81, sumbu y ke ATAS, mobil bergerak ke +x (kanan)
              → tiap kendaraan dicoba 21 kecepatan
2. SELEKSI    pilih run yang cocok dengan STORY (fail, fail, win) + batas waktu,
              lalu pilih KOMBINASI run yang durasinya pas 42–49.5 s (pick_combo)
              → utamakan rintangan gagal berbeda + mobil hancur/terbalik
3. TIMELINE   live (1.0x) + bullet-time (0.38x di lompatan tertinggi sebelum hasil)
              + instant replay slow-mo (0.4x) untuk level gagal yang hancur/terbalik
4. AUDIO      narasi Edge-TTS (narator en-US bergilir, VOICES) + suara mesin/benturan/kaca/buzzer/fanfare/BGM sintetis
5. RENDER     cairo 1080x1920, 4 worker paralel → ffmpeg H.264 + AAC
6. MANIFEST   <VIDEO_ID>.json (status RENDERED_PENDING_APPROVAL)
```

Parameter konten ada di bagian atas `sim_engine.py`:

| Konstanta | Fungsi |
|---|---|
| `SERIES_DEFS` | Daftar seri: judul layar, kata rintangan untuk narasi, judul/tag YouTube, batas durasi level (`max_fail`, `max_win`), `speed_scale` |
| `make_potholes_track()`, `make_bumps_track()` + `BUMP_CFG` | Generator lintasan per seri (acak dari seed). Mengisi `TRACK`, `PITS`/`BUMPS`, `RAMP`, `OBSTACLES`, `DANGER_X`, `SIGNS`, `FINISH_X`. Rintangan WAJIB di antara START_X dan FINISH_X. |
| `VEHICLES` | Karakter: nama, warna, bodi, massa, roda, suspensi (`travel`), rentang kecepatan uji, `break_dv` (batas hancur), zoom, template narasi intro (`{lvl}`, `{obst}`) |
| `FACES` | Posisi mata & mulut tiap karakter |
| `ROSTER` / `STORY` | Peran level: seed memilih 1 kendaraan per peran (ringan-gagal, berat-gagal, monster-menang) |
| `CTA`, `FAIL_LINES`, `WIN_LINE`, `REPLAY_LINE` | Teks narasi |
| `VOL_NARR/ENGINE/BGM/SFX` | Keseimbangan audio (Standar #8) |

---

## 3. 8 Standar Emas Produksi (wajib dipenuhi setiap video)

| # | Standar | Cara engine memenuhinya | Cara mengecek (Audit) |
|---|---|---|---|
| 1 | **Analisa menyeluruh sebelum produksi** | Mode `--preview-only` + checklist bagian 5 | Checklist bagian 5 terisi semua |
| 2 | **Deteksi presisi start → finish/crash** | Momen crash/finish diambil langsung dari data fisika, bukan ditebak | `levels[].event_t` ada dan masuk akal |
| 3 | **Scene setiap kendaraan utuh** | Satu level = satu run utuh dari start sampai hasil, tanpa potongan | Tidak ada lompatan posisi di progress bar |
| 4 | **Sinkron badge, narasi, SFX** | Badge FAIL/WINNER muncul 0.2 s sebelum event. Narasi hasil +0.25 s setelah event (atau langsung setelah narasi intro selesai, kalau event terjadi saat intro masih berjalan; narasi tidak pernah bertumpuk). SFX dipasang di waktu event. | Audit piksel badge + PNG `L*_event.png` |
| 5 | **Outro lengkap** | Level terakhir: WINNER → confetti → panel LIKE/SUBSCRIBE + narasi CTA baku | `outro.png` ada; narasi terakhir = CTA |
| 6 | **Render lokal, tanpa upload otomatis** | Manifest selalu `RENDERED_PENDING_APPROVAL` | Status di manifest & registry |
| 7 | **Format Shorts 9:16 & safe zone** | 1080x1920, 30/60 fps. Teks penting di y 150–1300. Tidak ada elemen penting di y > 1400. | `ffprobe` + cek PNG |
| 8 | **Keseimbangan audio** | Narasi 1.60, mesin 0.85, BGM 0.10, SFX 0.85 (stem dinormalisasi dulu), limiter −0.5 dBFS | Tidak clipping; narasi selalu terdengar paling jelas |

CTA baku (jangan diubah tanpa izin user):
*"Tap LIKE if you enjoyed this video, DISLIKE if you didn't, and smash SUBSCRIBE to MegaWheel Arena!"*

---

## 4. Standar Kualitas Visual & Durasi (target cetak biru)

Status: ✅ sudah ada di v2 · 🟡 sebagian · ⬜ belum (roadmap, bagian 9)

### 4.1 Desain karakter kartun
- ✅ Bodi warna solid + outline, kaca biru, velg berputar, lampu depan
- ✅ Wajah dengan 5 mood: normal, scared (alis cemas + keringat), whoa (mata besar + mulut O), happy (mata ^^ + senyum lebar), dizzy (mata X + bintang berputar)
- ✅ 6 tokoh tetap dalam 3 peran (cast bible: `cast/CAST.md`). Engine memilih tokoh yang paling jarang tampil untuk setiap peran (rotasi adil dari registry):
  - Ringan (gagal): **Zippy** sports car merah, **Siren** mobil polisi (lampu sirene berkedip)
  - Berat (gagal): **Buster** school bus kuning, **Hydro** mobil pemadam kebakaran (tangga, lampu darurat)
  - Juara (menang): **Rocky** monster truck biru, **Grizzly** monster truck hijau
- ✅ 4 seri (`--series`):
  - `potholes` **Cars VS Giant Potholes**: 3 lubang + ramp. Juara: monster truck.
  - `bumps` **Cars VS Giant Speed Bumps**: 4–5 polisi tidur kuning-hitam yang makin tinggi. Juara: monster truck.
  - `splash` **Cars VS Splash Zone** (v2.7): genangan air licin (gesekan 0.06) sebelum dinding beton, tanjakan, dan lubang. Mobil gagal karena `crash` (menabrak dinding), `rollback` (mundur di tanjakan basah), atau jatuh. Juara: `win_pool="any"`, tokoh mana pun.
  - `lava` **Cars VS Lava Road** (v2.7): 3 ventilasi yang menyembur berkala + 2 kolam lahar; tema selalu `volcano`. Mobil gagal karena `lava` (terlempar/terbakar). Juara: `win_pool="any"`.
- ✅ Juara bergilir: untuk `win_pool="any"`, engine memilih tokoh yang paling jarang menang (dari registry). Monster truck tidak selalu menang.
- ✅ SFX efek visual (v2.7): cipratan air (roda masuk genangan), gemuruh semburan lahar (volume mengikuti jarak), desis terbakar, hantaman dinding beton. Versi melambat di replay.
- ⬜ Highlight mengkilap / gradasi bodi, sorot lampu (light beam), velg chrome

### 4.2 Kerusakan kartun
- ✅ Roda terlepas, panel/bemper/dop/kaca terlempar, percikan api, retakan bodi, asap kartun
- ⬜ Bodi penyok (deformasi), kap mesin terbuka

### 4.3 Suspensi "juicy"
- 🟡 Pegas + peredam pymunk sudah ada (redaman 0.6)
- ⬜ Dibuat lebih "bouncy" (redaman 0.35–0.45) + squash & stretch visual saat mendarat

### 4.3b Tema lingkungan (acak per seed, tercatat di manifest `theme_id` dan registry `theme`)
- ✅ Waktu: `morning`, `noon`, `sunset`, `night` (bintang, bulan, lampu mobil menyala, jendela gedung menyala)
- ✅ Cuaca: `clear`, `rain` (rintik, awan kelabu, jalan basah, gesekan ×0.72), `snow` (salju turun, puncak bukit putih, gesekan ×0.55)
- ✅ Lokasi: `countryside`, `city` (siluet gedung), `desert` (bukit pasir, kaktus), `mountains` (gunung bersalju), `beach` (laut, pohon kelapa), `volcano` (khusus seri lava, lewat `force_theme`)
- ✅ Rotasi (v2.7): waktu dan lokasi yang paling jarang dipakai di registry didahulukan.
- Aturan: tidak ada salju di gurun/pantai, tidak ada hujan di gurun. Musik ikut tema (tempo, akor, instrumen; lonceng saat salju).
- Tema masuk ke sidik jari registry (`track_id@theme`), jadi lintasan yang sama dengan tema berbeda dihitung video berbeda.

### 4.4 Kamera & efek
- ✅ "READY... GO!" + bunyi beep di awal setiap level; zoom mendadak (punch-in) saat benturan keras
- ✅ Kamera mengikuti mobil, zoom out saat melayang, guncangan saat benturan, speed lines
- ✅ Bullet-time di lompatan besar, INSTANT REPLAY slow-mo
- ✅ Speech bubble: "UH OH!", "WHOA!", "OUCH!", "YEAH!"

### 4.5 Pacing (target 40–48 detik)

| Level | Target cetak biru | Isi |
|---|---|---|
| 1 | 0–12 s | Kendaraan ringan, gagal di rintangan pertama/kedua (+ jeda reaksi ±3 s) |
| 2 | 12–24 s | Kendaraan berat (bus/truk), gagal (+ jeda ±3 s) |
| 3 | 24–45 s | Monster truck / big rig, lolos semua, lompat juara, selebrasi, outro CTA |

**Yang dijaga otomatis oleh engine:** engine menghitung durasi semua kombinasi run dan hanya memilih kombinasi dengan total **42–49.5 s**. Analisa menolak video di luar total 40–50 s. Batas per level tergantung seri:

| Seri | Level gagal | Level menang (+ outro) | Alasan |
|---|---|---|---|
| potholes | ≤ 20 s | ≤ 24 s | |
| bumps | ≤ 18 s | ≤ 27 s | Monster truck melewati gundukan lebih lambat daripada melompati lubang |

Level 1 saat ini masih 13–17 s karena ada replay (target 12 s ada di roadmap).

---

## 5. ANALISA MENYELURUH (wajib, sebelum render penuh)

**Otomatis:** poin 5.1 dan 5.3 dicek oleh engine sendiri (fungsi `analyze()` di `sim_engine.py`) sebelum render. Hasilnya tampil sebagai baris `[analysis] OK/WARN/FAIL` dan disimpan di manifest (`analysis`). Kalau ada FAIL, engine berhenti (`[analysis] STOP`) dan video **tidak** dirender.
**Manual (tetap wajib untuk agent):** poin 5.2, yaitu buka dan lihat PNG preview.

### 5.1 Analisa fisika (otomatis; di sini sebagai referensi)
- [ ] **Arah gerak benar**: mobil bergerak ke kanan (+x). Posisi x di akhir level harus lebih besar dari `START_X` (engine akan error `motor sign is wrong` kalau mobil mundur).
- [ ] **Rintangan ada di lintasan**: `PITS` tidak kosong, dan semua rintangan berada di antara `START_X` dan `FINISH_X`. Kalau lintasan diubah, minimal 2 rintangan.
- [ ] **Pola cerita sesuai `STORY`**: `levels[].outcome` = gagal (`pit`/`flip`/`stuck`), gagal, `win`.
- [ ] **Tidak ada `timeout`**: mobil tidak boleh sekadar berhenti tanpa sebab.
- [ ] **Waktu event masuk akal**: event ≥ maks(2.5 s, durasi narasi intro − 1.0 s); event level gagal ≤ 11.5 s; event menang ≤ 15 s.
- [ ] **Variasi rintangan**: level 1 dan level 2 sebaiknya gagal di rintangan yang berbeda (`levels[].obstacle`).
- [ ] **Minimal 1 momen spektakuler di level gagal**: `broken: true`, `outcome: flip`, atau `bullet_time: true` (lompatan tinggi). Engine tetap memberi skor lebih pada kombinasi yang ada mobil hancur/terbalik.

### 5.2 Analisa visual (buka PNG di `<folder video>/preview/`)
- [ ] `L1_start.png`: judul, badge LEVEL, nama karakter, progress bar, dan mobil di jalan menghadap kanan
- [ ] `L*_bubble.png`: speech bubble dekat mobil dan tidak menutupi badge
- [ ] `L*_event.png`: badge FAIL/WINNER cocok dengan kejadian di gambar
- [ ] `L*_replay.png` (kalau ada): label INSTANT REPLAY + kamera zoom ke mobil
- [ ] `outro.png`: panel LIKE/SUBSCRIBE tidak menutupi mobil pemenang
- [ ] Tidak ada teks terpotong, tumpang tindih, atau elemen penting di y > 1400

- [ ] **Durasi**: total 40–50 s; batas per level sesuai tabel di bagian 4.5.

### 5.3 Analisa keunikan (otomatis)
- [ ] Seed belum pernah dipakai (registry menolak dengan `[registry] STOP`)
- [ ] Sidik jari (seri, kendaraan, lintasan, hasil) belum ada di registry

---

## 6. AUDIT SEBELUM PREVIEW (wajib, setelah render penuh)

**Otomatis:** setelah render, engine menjalankan `audit.py`. Audit ini memeriksa 6.1–6.3 pada file MP4 yang sebenarnya, termasuk **mengukur warna piksel** badge LEVEL, FAIL/WINNER, dan panel outro tepat di detik kejadian. Hasilnya ditulis ke `<folder video>/<VIDEO_ID>_audit.md` dan `_audit.json`, dan status diperbarui di manifest dan registry.
Hanya kirim preview ke user kalau audit **LOLOS** (`[audit] PASS`, exit 0). Perintah manual di bawah ini untuk investigasi kalau audit gagal.

### 6.1 Audit teknis
```bash
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact <folder video>/<VIDEO_ID>.mp4
```
- [ ] Video `h264`, 1080x1920, 30/1 (atau 60/1)
- [ ] Audio `aac` ada
- [ ] Durasi 40–50 s (sama dengan `duration` di manifest, selisih ±0.2 s)
- [ ] Ukuran file wajar (8–20 MB untuk 30 fps)

### 6.2 Audit audio
```bash
ffmpeg -i <VIDEO_ID>.mp4 -af volumedetect -f null - 2>&1 | grep -E "max_volume|mean_volume"
```
- [ ] `max_volume` antara −3 dB dan −0.1 dB (tidak clipping, tidak terlalu pelan)
- [ ] `mean_volume` antara −20 dB dan −12 dB (YouTube menormalisasi ke ±−14 LUFS; di luar rentang ini berarti terlalu pelan atau terlalu keras/pecah)
- [ ] Narasi berurutan: intro L1 → hasil L1 → (replay) → intro L2 → ... → CTA (lihat `narration` di manifest)

### 6.3 Audit sinkronisasi (ambil frame di waktu tertentu)
```bash
ffmpeg -ss <detik> -i <VIDEO_ID>.mp4 -frames:v 1 /tmp/check_<detik>.png
```
Detik yang dicek dihitung dari manifest (`levels[].start` + waktu kejadian):
- [ ] Di waktu event setiap level terlihat badge yang benar dan mobil dalam kondisi yang sesuai
- [ ] Di 1.0 s terakhir video terlihat panel outro

### 6.4 Laporan audit
Ditulis otomatis ke `<folder video>/<VIDEO_ID>_audit.md` (✅ lolos, ❌ wajib diperbaiki, ⚠️ peringatan). Tanpa file audit berstatus LOLOS, video dianggap belum siap preview. Untuk audit ulang: `./venv/bin/python generators/physics_2d/audit.py <VIDEO_ID>`.

---

## 7. TRACKING & KEUNIKAN (agar video tidak sama terus)

### 7.1 Registry
File: `/root/video-engine/PRODUCTION_REGISTRY.json`. **Diisi otomatis oleh engine** setelah audit (jangan diedit manual, kecuali untuk mengisi status upload/approval). Satu entri per video:

```json
{
  "video_id": "SIM_POTHOLES_V2_S001",
  "series": "potholes",
  "engine_version": "v2",
  "seed": 1,
  "created": "2026-09-30",
  "vehicles": ["sports", "bus", "monster"],
  "track_id": "potholes_std",
  "outcomes": ["pit@obs2+broken", "stuck@obs0", "win"],
  "duration": 46.93,
  "status": "RENDERED_PENDING_APPROVAL",
  "audit": "renders/megawheel_arena/S01/E001_2026-09-30_potholes/SIM_POTHOLES_V2_S001_audit.md",
  "youtube_url": null
}
```

### 7.2 Aturan keunikan
1. **Seed tidak boleh dipakai ulang** dalam seri yang sama.
2. **Sidik jari** = `series + vehicles + track_id + outcomes`. Sidik jari yang sama dengan video mana pun **dilarang**.
3. Maksimal **3 video berturut-turut** dari seri yang sama. Setelah itu, ganti seri, lintasan, atau susunan kendaraan.
4. Setiap 5 video, minimal 1 variabel besar harus berubah: seri, lintasan (`track_id` baru), tema, atau karakter.
5. Nama VIDEO_ID: `SIM_<SERIES>_V<engine>_S<seed 3 digit>`, contoh `SIM_POTHOLES_V2_S004`.
6. Setelah upload (dengan approval), isi `status` dan `youtube_url`.

Aturan 1 dan 2 ditegakkan oleh engine (`[registry] STOP` / analisa `unique`). Aturan 3 muncul sebagai peringatan ⚠️ di audit. Aturan 4 wajib diperhatikan agent/user.

### 7.3 Status video
`ANALYZED` → `RENDERED_PENDING_APPROVAL` (folder `pending/`) → `APPROVED` (dapat nomor episode, pindah ke `S01/E00x_...`, judul "| Ep. N") atau `REJECTED` (folder `rejected/`) → `UPLOADED_PRIVATE` / `UPLOADED_UNLISTED` / `UPLOADED_PUBLIC`.
Status lain: `ANALYSIS_FAILED` (tidak dirender), `AUDIT_FAILED` (dirender tapi tidak boleh dikirim), `PROTOTYPE_NOT_FOR_UPLOAD`.
Video berstatus `AUDIT_FAILED` / `REJECTED` / `PROTOTYPE_NOT_FOR_UPLOAD` tidak dihitung dalam pengecekan keunikan.

---

## 8. Alur Kerja Standar untuk Agent (ringkas)

```
1. Baca BLUEPRINT.md (file ini) + DEV_HISTORY.md + ERROR_LOG.md
2. Lihat PRODUCTION_REGISTRY.json → pilih seri (atau biarkan otomatis) → seed terbesar di seri itu + 1
3. cd /root/video-engine && ./venv/bin/python generators/physics_2d/sim_engine.py [--series <seri>] --seed <N>
     exit 1 (STOP analisa/registry) → seed + 1, ulangi (maks 5x, lalu lapor ke user)
     exit 5 (AUDIT_FAILED)          → jangan kirim; laporkan isi _audit.md
     exit 0                         → video ada di renders/megawheel_arena/pending/<tanggal>_<seri>_s<seed>/
4. Buka & periksa PNG preview (bagian 5.2) — mata agent tetap wajib
5. Kirim ke user: VIDEO_ID, durasi, tokoh, hasil audit, dan 2–3 PNG (L1_event, L1_replay/L2_event, outro)
6. APPROVE — HANYA setelah user bilang approve untuk VIDEO_ID tertentu:
     ./venv/bin/python generators/publishing/episodes.py approve <VIDEO_ID> [<VIDEO_ID> ...]
   (urutan argumen = urutan nomor episode; folder pindah ke S01/E00x_..., judul "| Ep. N #Shorts")
   Ditolak user → ./venv/bin/python generators/publishing/episodes.py reject <VIDEO_ID> "<alasan>"
7. UPLOAD — HANYA atas perintah user, HANYA episode APPROVED:
     ./venv/bin/python generators/publishing/publish.py <EP> --privacy private|unlisted|public
   (judul/deskripsi/tag dari manifest, kategori Film & Animation, made_for_kids=False; status + URL tercatat otomatis)
8. EVALUASI: isi metrik dari YouTube Analytics → episodes.py set <EP> views=.. likes=.. retention=..% note="..."
   Daftar lengkap: renders/megawheel_arena/EPISODE_LOG.md (dibuat ulang otomatis)
9. Kalau engine diubah: uji --preview-only, tambahkan entri di DEV_HISTORY.md, lalu
   git add -A && git commit -m "<ringkasan>" && git push
   (credentials/, venv/, work/, MP4/PNG otomatis diabaikan .gitignore. Jangan pernah commit credentials.)
```

---

## 9. Roadmap Pengembangan (urut prioritas)

| # | Fitur | Keterangan |
|---|---|---|
| ✅ | Audit otomatis | `audit.py`: 30 pengecekan, termasuk warna piksel di detik kejadian |
| ✅ | Registry otomatis | Menolak seed dan sidik jari duplikat |
| ✅ | Lintasan acak per seed | Posisi, lebar, dan kedalaman lubang, serta tinggi ramp berbeda di tiap seed |
| ✅ | Seri 2: Giant Speed Bumps | `--series bumps`, 4–5 gundukan setengah-sinus makin tinggi (hingga 2.7 m) |
| ✅ | Tokoh tetap + rotasi adil | 6 tokoh, 3 peran, `cast/characters.json`; yang paling jarang tampil didahulukan |
| ✅ | Satu engine | sim-prototype digabung ke `/root/video-engine` (2026-09-30), pipeline footage diarsipkan |
| ✅ | Tema lingkungan + narator bergilir + ducking | v2.6 (2026-09-30) |
| 1 | **Seri Roller Coaster Road** | Bukit raksasa, turunan curam, lompatan, loop 360°; tokoh jagoan per sirkuit |
| 2 | **Format balapan** | 3 mobil sekaligus, hitung mundur, urutan finish |
| 3 | Variasi kegagalan kendaraan berat | Bus/fire truck hampir selalu `stuck` (di potholes selalu di lubang 1) → rintangan yang membuat kendaraan berat terbalik / hancur |
| 2 | Pacing Level 1 ≤ 12 s | Replay lebih pendek atau hanya di level paling spektakuler |
| 3 | Suspensi juicy + squash & stretch | Redaman lebih rendah + deformasi visual saat mendarat |
| 4 | Polish vektor | Highlight bodi, gradasi kaca, velg chrome, light beam |
| 6 | Seri 3: Giant Pendulum Wrecking Ball | Bola berayun (pymunk PinJoint) |
| 7 | Seri 4: Collapsing Wooden Bridge | Papan jembatan dengan sambungan yang bisa putus |
| 8 | Seri 5: Hydraulic Car Grizzly | Pres bergerak naik-turun |

Setiap seri baru WAJIB tetap memakai engine yang sama (tambah fungsi lintasan/rintangan di `sim_engine.py`), bukan script terpisah.

### Cara menambah seri baru (untuk developer/agent)
1. Tambah entri di `SERIES_DEFS` (judul, `obst`, `yt_title`, `tags`, `max_fail`, `max_win`, opsional `speed_scale`).
2. Buat `make_<seri>_track(seed)` yang mengisi `TRACK`, `OBSTACLES`, `DANGER_X`, `SIGNS`, `FINISH_X`, `TRACK_PARAMS`, `TRACK_ID` (dan `PITS`/`BUMPS`/`RAMP`), lalu daftarkan di `make_track()`.
3. Tambah gambar rintangannya di `draw_track()`.
4. Setel parameter fisika dengan script mirip `generators/physics_2d/tune_bumps.py` (tanpa TTS/render, cepat), lalu `generators/physics_2d/find_seeds.sh <seri> 1 10`. Targetnya ≥ 7/10 seed lolos.
5. Render 1 video, cek PNG, dan tulis entri di `DEV_HISTORY.md` (termasuk parameter akhir dan tingkat lolos).
6. Kalau seri punya momen khas, isi `signature` di `SERIES_DEFS` (`"spin"`, `"melt"`). Kombinasi tanpa momen itu ditolak, jadi engine pindah ke seed berikutnya.

---

## 10. SOP Publikasi (jadwal upload)

**Aturan:** hanya episode `APPROVED` yang boleh masuk antrian. Upload ke YouTube hanya atas instruksi eksplisit user.

| Slot | Jam New York (ET) | Alasan | WIB saat EDT (s/d 1 Nov 2026) | WIB saat EST |
|---|---|---|---|---|
| 1 | 11:00 | Istirahat siang Pantai Timur, pagi Pantai Barat | 22:00 | 23:00 |
| 2 | 15:00 | Pulang sekolah/kerja Pantai Timur, siang Pantai Barat | 02:00 (+1 hari) | 03:00 (+1 hari) |
| 3 | 19:00 | Prime time malam | 06:00 (+1 hari) | 07:00 (+1 hari) |

- 3 Shorts per hari, satu per slot, urut nomor episode.
- Zona waktu disimpan sebagai `America/New_York`, jadi pergantian daylight saving otomatis.
- Mekanisme: video diupload sebagai `private` dengan `publishAt`. YouTube yang menayangkan tepat di jamnya, tidak ada cron di server kita.

**Perintah:**
```
./venv/bin/python generators/publishing/publish_queue.py plan      # isi slot kosong untuk episode APPROVED baru
./venv/bin/python generators/publishing/publish_queue.py show      # renders/megawheel_arena/PUBLISH_QUEUE.md
./venv/bin/python generators/publishing/publish_queue.py upload --confirm   # HANYA atas instruksi user
```

**Evaluasi:**
- Setelah 2 minggu, bandingkan views per jam tayang dan persentase penonton yang bertahan di YouTube Analytics per slot.
- Slot dengan hasil terburuk digeser. Setiap perubahan dicatat di DEV_HISTORY.
