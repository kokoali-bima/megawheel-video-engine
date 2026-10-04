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

## Sensor yang ada sekarang
| Sensor / cek | Di mana | Menangkap |
|---|---|---|
| Piksel rintangan saat tabrakan | race25d `sensed()` / `unseen_hazards()` | rintangan tak tergambar, salah koordinat, di luar layar |
| Frame tanpa mobil | race25d render loop | kamera membidik jalan kosong |
| Urutan realistis | race25d `unexplained_upsets()` | mobil lambat menang tanpa sebab |
| Struktur variasi | produce.py | tata letak + rintangan berulang (10 video terakhir) |
| Isi lubang dipakai | sim_engine `content_required()` | duri/bom/monster cuma hiasan |
| Piksel badge FAIL/WINNER, outro | audit.py (CHALLENGE) | badge/outro tidak tampil di detik kejadian |

## Belum ada (berikutnya)
- Sensor tumpang-tindih: rintangan menutupi wajah/bodi mobil secara janggal (kasus #9).
- Sensor perilaku: mobil di belakang korban harus menghindar / mengerem (kasus #7) — cek posisi relatif.
- Sensor yang sama untuk SMASH (chaos: rudal, Kraggor, UFO, retakan harus terlihat saat mengenai mobil).
