# QA_DEFECT_TRACKER — cacat yang lolos ke review (dan gerbang yang sekarang menangkapnya)

> Dibuat atas permintaan user 2026-10-04: "buat tracker kesalahan atau error ini, sehingga ke depannya engine kita tidak
> ceroboh seperti ini lagi dan engine auditor kita bisa melihat menggunakan sensor, sehingga yang begini tidak dilewatkan
> untuk di-review."
>
> **Aturan:**
> 1. Setiap cacat yang ditemukan user (atau agent) di video review → 1 baris di tabel, sebelum diperbaiki.
> 2. Perbaikan tidak dianggap selesai sampai kolom **Gerbang otomatis** terisi: cek di engine / audit / produce.py yang
>    akan menolak cacat yang sama di masa depan. Kalau belum ada gerbang, status tetap ⚠️.
> 3. Gerbang visual memakai **sensor piksel** (mengukur apa yang benar-benar tergambar di layar), bukan percaya pada data
>    simulasi: data bisa benar sementara gambarnya salah (kasus kontainer).
> 4. Kesalahan operasional / kebiasaan agent tetap dicatat di `ERROR_LOG.md`; tracker ini khusus cacat isi video.

| # | Tanggal | Video | Cacat (yang dilihat penonton) | Akar masalah | Perbaikan (commit) | Gerbang otomatis | Status |
|---|---|---|---|---|---|---|---|
| 1 | 2026-10-03 | 18 review 3D | Mobil melengkung / seperti plastik | Shader penyok menggeser semua titik bodi dengan noise | Logam kaku, penyok linier di ujung (3D, lab) | — (3D dihentikan; produksi = 2.5D) | ⏸️ lab |
| 2 | 2026-10-04 | SIM_POTHOLES_V2_S028 | Roda Hydro di atas bom, bom tidak meledak | Ambang pemicu isi lubang lebih rendah dari tinggi gambar bom | Ambang = tinggi gambar tiap isi (sim_engine) | Analisa: lintasan berisi isi khusus wajib punya kegagalan yang mengenainya (`content_required`) | ✅ |
| 3 | 2026-10-04 | SIM_POTHOLES_V2_S029 | Duri & Pit Muncher hanya hiasan | Tidak ada syarat isi lubang harus dipakai | `content_required()` → seed ditolak | Analisa `has_signature` (otomatis pindah seed) | ✅ |
| 4 | 2026-10-04 | RACE Ep. 31–49 (v3) | Judul bertanya mobil A + rintangan X, padahal yang kena mobil B | `question_for` memilih "underdog" + rintangan terheboh tanpa cek bertemu | Judul = mobil yang benar-benar kena rintangan bintang | produce.py: struktur/judul; race25d: `star_key` dipakai judul, cold open, replay | ✅ |
| 5 | 2026-10-04 | RACE v3 (bus menang) | Bus mengalahkan mobil balap di jalan lurus | Kecepatan semua mobil diundi dari rentang sama | race25d v4: kecepatan & akselerasi per kelas | Cek "realistic order" (mobil lambat di depan hanya bila yang cepat kena / tersenggol / terhalang) | ✅ |
| 6 | 2026-10-04 | S019, S020, S022 | Scene lompat-lompat | Kamera di-clamp keras ke mobil fokus (lompat 1 frame) | Kamera meluncur + batas kecepatan + whip pan | Cek "no frame without a car" (frame kosong saat kamera diam = gagal; whip ≤ 10 frame) + log diagnosa | ✅ |
| 7 | 2026-10-04 | S020 | Siren kena palu, Rocky di belakangnya lewat begitu saja | Rintangan "sekali pakai": lajur dianggap bersih | Mobil di belakang korban pindah lajur / mengerem + narasi | — (perilaku; dicek visual) | ⚠️ belum ada sensor perilaku |
| 8 | 2026-10-04 | S021 | Pertanyaan menutupi mobil & gelembung; adegan beda dengan judul | Teks cold open di tengah layar; momen cold open ≠ momen judul | Cold open di pita atas; satu `star_key` untuk judul/cold open/replay/fokus kamera | — (posisi tetap di kode) | ✅ |
| 9 | 2026-10-04 | S021 | Tiang mesin pres menembus Sprinkles | Pres turun ke tinggi tetap (mobil rendah) | Pres berhenti di atap korban & ikut penyet | — | ⚠️ belum ada sensor tumpang-tindih |
| 10 | 2026-10-04 | S022 | Cold open terlalu cepat | Cold open 1,5 dtk | 3,0 dtk (semua format) | — (setelan) | ✅ |
| 11 | 2026-10-04 | S033 / S029 / S035 | Cold open berisi perpindahan kamera; judul kembar | Cold open mulai 1,65 dtk sebelum momen; satu pola judul | Cold open mulai 0,45 dtk sebelum momen; 4 pola judul, tak pernah sama | produce.py struktur; race25d judul unik dari registry | ✅ |
| 12 | 2026-10-04 | S031 | Struktur sama dengan S028 | Rintangan diundi tanpa cek riwayat | Undi ulang bila struktur sama 10 video terakhir | produce.py gerbang struktur | ✅ |
| 13 | 2026-10-04 | S041 | Monster truck menyalip taksi tanpa sebab | Bonus kecepatan 3% setelah ramp | Bonus dihapus | Cek "realistic order" (menangkapnya) | ✅ |
| 14 | 2026-10-04 | **S038, S039 (semua kontainer)** | **Kontainer tidak terlihat, mobil menabrak "udara kosong"** | `draw_container`: setelah mendarat posisi diset kembali "di langit" (22 m ke atas, keluar layar) — sejak v3 | `drop = 0.0` setelah mendarat | **Sensor piksel** (piksel pekat yang benar-benar tergambar): rintangan bintang wajib jelas terlihat (median ≥ 1500 px; menetap 0–0,8 dtk setelah tabrakan, sesaat −0,6…+0,3); rintangan lain: bila mobil korban terlihat, rintangan wajib muncul (maks ≥ 1500 px dalam 1,5 dtk) — kalau tidak → GAGAL; kejadian sepenuhnya di luar layar = peringatan. Divalidasi: versi bug kontainer tertangkap (0 px), 15 jenis rintangan normal lolos | ✅ |

| 15 | 2026-10-05 | Ep.2 pilot C v5 | Mobil melayang di adegan footprint (Godot) | Decal jejak 6,7×7,4 m menjorok ke depan mobil; tanpa bayangan kontak | Jejak rebah sejajar jalan 5,5×3 m; `draw_contact` | story3d `grounding` | ✅ |
| 16 | 2026-10-06 | Ep.2 pilot C v6 | Mobil melayang di shot miring (dutch) | Tanda roll kamera Godot terbalik | Rumus kamera diturunkan ulang (roll +, lens shift di sumbu layar) | story3d `roll/proyeksi` (Godot vs cairo ≤ 2 px) | ✅ |
| 17 | 2026-10-06 | Ep.2 pilot v6 | Noise saat adegan sepi; langkah Kraggor tak terdengar | Ambience = desis 1–2 kHz; langkah < 200 Hz (HP tak bisa memutar) | `fft_band`, `phone_step`, heartbeat knock | story3d `audio` (desis + `phone_band`) | ✅ |
| 18 | 2026-10-06 | Ep.2 pilot v6 (+Ep.1) | Awal lirik / kalimat panjang tidak tampil | Subtitle hanya 2 baris terakhir | Subtitle berhalaman (`|`, waktu halaman) | — (kode) | ✅ |
| 19 | 2026-10-06 | Ep.2 pilot C v7 | Siluet Kraggor terlihat sejak shot 3 | Sprite dipasang statis | Tampil hanya di frame `kfar` | story3d `reveal` | ✅ |
| 20 | 2026-10-06 | story3d scene 2 r1 | Dunia meleset 283 px di shot low | Regangan y 1,12 cam "low" (2.5D) tak bisa ditiru kamera 3D | `ISO_CAMERA` | story3d `roll/proyeksi` | ✅ |
| 21 | 2026-10-06 | story3d scene 1–2 r1 | Kamera "swoosh" antar shot (20 m / 1 dtk) — kesan lompat | Glide 1,1–1,4 dtk ke setiap shot | `CUT_RULE="auto"`: perubahan besar = cut, kecil = glide pelan | story3d `kamera` (gerak bidang tokoh ≤ 70 px/f) | ✅ |
| 22 | 2026-10-06 | story3d scene 2 r1 | Zippy tertutup Sprinkles 46% | Posisi parkir bertumpuk | Posisi digeser | story3d `framing` (tertutup > 30% = FAIL) | ✅ |
| 23 | 2026-10-06 | story3d scene 2 r1 | Klakson/sorakan menimpa kalimat; musik menutupi | Efek di detik tetap; cue terlalu keras | sfx `"end+0.1"`; vol cue | story3d `audio` masking (≥ 6 dB) | ✅ |
| 24 | 2026-10-06 | story3d scene 2 r2 | Tulisan "SCHOOL BUS"/"POLICE" terbalik (cermin) | Mobil menghadap kiri dicerminkan beserta tulisan | `TEXT_UNMIRROR` (story3d) | — (visual; Shorts belum diubah) | ✅ story3d |

| 25 | 2026-10-06 | story3d scene 2 | Adegan terasa per pemeran (zoom ke tiap yang bicara) | Close-up tiap kalimat | cam `group`, pendengar melirik, J-cut | STYLE_CONTRACT C01/C04 (linter + sensor J-cut ≥ 50%) | ✅ |
| 26 | 2026-10-06 | story3d scene 2 | Mobil berbaris menempel / menembus palang | Posisi tanpa jarak | Staging ulang | STYLE_CONTRACT C02/C03 (linter) | ✅ |
| 27 | 2026-10-06 | story3d scene 1 | Sunyi tanpa makna sebelum footprint | Tidak ada lapisan tegang | `drone` + `thud_far` | STYLE_CONTRACT A01 (sensor ≤ 2,2 dtk) | ✅ |
| 28 | 2026-10-06 | sambungan 1→2 | Transisi terburu-buru; suara terpotong ke hitam | Fade 1 dtk; crossfade ke klip hitam memotong suara | fade out 1,0 + hitam 0,5 (room tone) + fade in 1,3; afade qsin eksplisit | STYLE_CONTRACT J01/J02 (sensor sambungan, diukur) | ✅ |

| 29 | 2026-10-06 | scene 3 | Mobil polisi melayang setelah turun dari panggung | Ketinggian tetap h=0.75 | `platform_h` (panggung + ramp) | STYLE_CONTRACT G04 (linter + sensor) | ✅ |
| 30 | 2026-10-06 | scene 2-3 | Terlalu banyak zoom-in | Close-up potong tiap momen | Push-in, maks 2 close-up bertanda | STYLE_CONTRACT C09-C11 | ✅ |
| 31 | 2026-10-06 | scene 4 | Foto Ep.1 dipakai untuk sobekan (Ep.1 tidak ada Kraggor) | Kesinambungan antar episode | Album + foto gunung baru, seed sobekan | STYLE_CONTRACT K01 (linter) | ✅ |
| 32 | 2026-10-06 | scene 4 | Render macet 3x / crash di cloud (suara narator, stroke=None) | Modal client menggantung; kode gambar baru tak diuji | watchdog + SMOKE preflight + mount branding/voice | produce_story3d (otomatis) | ✅ |
| 33 | 2026-10-06 | sambungan | Transisi antar scene seperti drama China panjang | Fade polos | Kartu "PART N + judul" + lonceng | STYLE_CONTRACT J03 | ✅ |

| 34 | 2026-10-06 | scene 5-8 r1 (review sendiri) | Kerucut Kraggor kecil tersembunyi di balik kepala; hutan/gunung/gua terlalu gelap, tokoh menyatu dengan latar; titik putih (bulan) di gunung; teks papan Grandpa meluber; Sprinkles terpotong tepi di shot grup | Posisi kerucut di belakang kepala; ambient rendah; bulan terlihat lewat batu; fon papan besar; dx grup 0 | kerucut digambar di depan; ambient 0,62/0,45; bulan disembunyikan di gunung; fon 0,0028; dx 1,6 | STYLE_CONTRACT L02 + sensor cahaya/kontras (sudah ada) + lembar kontak wajib (tools/contact_sheet.py) | ✅ |
| 35 | 2026-10-06 | scene 5-7 r1 | Guntur/bisikan/mesin menutupi kalimat (masking 4 titik) | Efek & musik terlalu keras di dekat kalimat | gain efek (elemen ke-3), musik 0,38-0,42, jeda | STYLE_CONTRACT A09 (sensor masking A04) | ✅ |
| 36 | 2026-10-06 | scene 5,6 r1 | WARN "lompatan gambar" tiap kilat petir | Kilat = lonjakan kecerahan disengaja | didokumentasikan: lompatan tepat di waktu kilat adalah wajar | audit `lompatan` (WARN, dilaporkan ke user) | ✅ catat |
| 37 | 2026-10-06 | sambungan 5->6 | Suara terpotong (turun 14,6 dB/0,1 dtk): guntur akhir scene masih keras saat fade-out | Ambience badai keras + kurva qsin berhenti curam di skala dB | guntur selesai sebelum fade (hold 6,8; end+0,3) + kurva fade-out sambungan qsin -> cub (diukur pada audio nyata: qsin 22 dB, cub 7,6 dB per 0,1 dtk) | sensor sambungan J02 (drop_db 14) | ✅ |
| 38 | 2026-10-06 | seluruh film (scene 1-8) | Backsound berisik dan ada terus sepanjang film | Musik menutupi ~85-100% shot, gain 0,32 + duck hanya -7 dB | Riset (dialog = jangkar, musik 12-20 dB di bawah suara, spotting + diam disengaja): musik maks 60% shot & 30 dtk menerus, gain 0,24, duck 0,75 (smooth 0,6 dtk); scene 2-8 di-spotting ulang (scene 1 sudah 56%) | STYLE_CONTRACT A10: linter (maks 60% shot bermusik, ERROR) + sensor QA (share musik, run terpanjang, selisih dB di bawah suara, WARN) | ✅ |
| 39 | 2026-10-07 | sambungan 11->12, 13->14 | Teriakan "NOW!" terpotong fade (drop 18 dB); dissolve same-place melompat level 12 dB | Ekor scene 11 terlalu pendek; same-place tanpa kartu | hold akhir scene 11 = 4,4 dtk; kartu PART di SETIAP sambungan (every_join) | STYLE_CONTRACT J03/J04 + sensor sambungan | ✅ |

## Sensor yang ada sekarang
| Sensor / cek | Di mana | Menangkap |
|---|---|---|
| Piksel rintangan saat tabrakan | race25d `sensed()` / `unseen_hazards()` | rintangan tak tergambar, salah koordinat, di luar layar |
| Frame tanpa mobil | race25d render loop | kamera membidik jalan kosong |
| Urutan realistis | race25d `unexplained_upsets()` | mobil lambat menang tanpa sebab |
| Struktur variasi | produce.py | tata letak + rintangan berulang (10 video terakhir) |
| Isi lubang dipakai | sim_engine `content_required()` | duri/bom/monster cuma hiasan |
| Piksel badge FAIL/WINNER, outro | audit.py (CHALLENGE) | badge/outro tidak tampil di detik kejadian |
| story3d (A10): porsi musik, run musik terpanjang, musik vs suara | audit_story3d.py | backsound terlalu ramai (#38) |
| story3d: roll/proyeksi, grounding, kamera, lompatan, framing, variasi, cahaya/kontras/bayangan, audio (desis, sunyi, masking, HP, monoton, LUFS), reveal | generators/story3d/audit_story3d.py | semua cacat #15–23 (ambang tetap, lihat SOP_STORY3D §4) |

## Belum ada (berikutnya)
- Sensor tumpang-tindih: rintangan menutupi wajah/bodi mobil secara janggal (kasus #9).
- Sensor perilaku: mobil di belakang korban harus menghindar / mengerem (kasus #7) — cek posisi relatif.
- Sensor yang sama untuk SMASH (chaos: rudal, Kraggor, UFO, retakan harus terlihat saat mengenai mobil).
