# S01E02 — Riset & rencana produksi (menjawab 5 catatan user setelah menonton Ep. 1)

> User 2026-10-05: (1) backsound monoton, sama di semua situasi; (2) kamera belum optimal, tidak dapat serunya;
> (3) alur, cara tokoh membaca naskah & mimik monoton — terkesan membaca teks; (5) riset 3D + maksimalkan Modal;
> (6) riset hook yang legendaris dan diingat penonton.
> Dokumen ini: diagnosis dari kode Ep. 1 → hasil riset → rencana konkret Ep. 2 → pilot untuk dinilai user sebelum produksi penuh.

## 0. Diagnosis Ep. 1 (dari kode `generators/story/story25d.py`, bukan tebakan)
| Catatan user | Penyebab di engine |
|---|---|
| Backsound monoton | `score()` = **satu jenis bunyi sintetis** (pad sinus + arpeggio lonceng) untuk semua suasana; 6 "mood" hanya mengganti deret akor. Musik berbunyi terus (wallpaper), tanpa tema tokoh, tanpa jeda, tanpa aksen pada momen. |
| Kamera kurang seru | Jenis shot ada (close, ecu, medium, low, two, track), tetapi **kamera diam per shot** (zoom bergerak 2%), selalu dari samping, tanpa gerak kamera (push-in, pan, crane, handheld), tanpa ritme potongan mengikuti emosi. |
| Tokoh "membaca teks" | Suara: Chatterbox dengan **7 gaya emosi tetap** (exaggeration/cfg); tiap kalimat dibuat terpisah → intonasi rata, tanpa napas/tawa/desah, tanpa interupsi atau tumpang tindih. Wajah: emosi diganti per kalimat, mulut mengikuti fonem, tapi tubuh mobil hampir tidak "berakting" (tanpa antisipasi, tanpa gerak kepala/bodi saat bicara). Naskah: kalimat lengkap dan rapi seperti narasi, jarang kalimat terpotong / reaksi. |
| Hook | Cold open + teaser ada, tapi belum punya **gambar ikonik + bunyi khas + kalimat yang diulang** yang membuat orang ingat dan membicarakannya. |

## 1. Musik: dari "wallpaper" ke skor film
Prinsip riset (film & animasi): **leitmotif** (tema berulang untuk tokoh/ide), **orkestrasi sesuai emosi** (string = haru,
brass = heroik, woodwind/pizzicato = jenaka), **musik tidak terus-menerus** (diam juga alat; musik masuk di beat penting),
**stinger/hit** pada momen kaget.

Rencana Ep. 2:
1. **Perpustakaan cue** dibuat dengan ACE-Step (Apache-2.0, sudah dipakai untuk lagu tema; instrumental, di Modal):
   - Tema tokoh: *Sprinkles* (music box + ukulele, ceria), *Kraggor* (cello rendah + timpani, misterius → hangat di akhir),
     *Grandpa Cone* (piano tua, nostalgia; turunan melodi lagu truk es krim).
   - Suasana: misteri malam, kepanikan kota, petualangan gunung, tegang/kejar, komedi (pizzicato), haru, heroik, ajaib (celesta).
   - Tiap cue 3–5 variasi (intensitas rendah/sedang/tinggi + versi akhir "button") supaya tidak ada yang terdengar berulang.
2. **Spotting sheet per scene** (seperti komposer film): kapan musik masuk/keluar, kapan diam, stinger di beat kejutan.
   Target: ±60–70% durasi bermusik, bukan 100%.
3. **Tema Kraggor berkembang**: scene 1 seram → scene 9 lembut (dimainkan Sprinkles) → scene 14 penuh hangat. Ini yang
   membuat penonton "merasakan" perubahan, bukan hanya melihat.
4. Mix: musik turun otomatis di bawah dialog (sudah ada ducking) + ambience per lokasi (sudah ada).
- Biaya: ±30–40 cue × ±$0,02–0,05 di Modal L4 ≈ **$1–2 sekali**, dipakai ulang di episode berikutnya.

## 2. Kamera: sinematografi, bukan rekaman diam
Riset: sudut & gerak kamera menentukan emosi — low angle = kuat/heroik, high angle = kecil/rentan, eye level = empati;
gerak (pan, dolly, push-in, crane) mengubah cara emosi dibaca; komposisi (rule of thirds, leading lines) mengarahkan mata.

Rencana engine (story25d, 2.5D tetap — tanpa biaya GPU):
| Gerak / teknik | Kapan dipakai |
|---|---|
| **Push-in** pelan ke wajah | kalimat penting, keputusan, rasa takut yang tumbuh |
| **Pull-out reveal** | memperlihatkan sesuatu yang besar (jejak kaki raksasa, gua, Kraggor) |
| **Pan / tilt** mengikuti pandangan tokoh | "lihat ke sana…" → kamera ikut menoleh |
| **Crane naik** | akhir babak, pemandangan kota/gunung |
| **Handheld shake halus** | panik, kejar, gempa langkah Kraggor |
| **Dutch tilt** (miring) | sesuatu tidak beres, malam mencekam |
| **Rack focus** (latar ↔ depan buram) | dua tokoh, rahasia di latar |
| **Over-the-shoulder + reverse shot** | percakapan (bukan two-shot statis) |
| **Ritme potongan** | santai = shot panjang; tegang = potongan makin cepat; haru = tahan lama |
Plus: **storyboard per scene** (thumbnail PNG otomatis per shot) untuk dicek sebelum render penuh.

## 3. Akting suara & mimik: tokoh "bermain", bukan membaca
1. **Model suara** (lisensi komersial dicek):
   - **Chatterbox-Turbo** (MIT, satu keluarga dengan suara kita sekarang): tag `[laugh] [chuckle] [cough]` + kloning
     suara tokoh yang sudah ada → kandidat utama.
   - **Dia** (Apache-2.0, kode & bobot): dialog dua pembicara dalam satu generasi (intonasi saling menanggapi) + tag
     `(laughs) (sighs) (gasps) (screams) (whispers…)`; konsistensi suara lewat audio prompt → uji untuk adegan dialog.
   - Orpheus: tag emosi bagus, tetapi bobot berbasis Llama (lisensi terpisah) → tidak dipakai kecuali dicek ulang.
2. **Penyutradaraan per kalimat** di naskah: emosi + intensitas + tempo + jeda + aksi kecil, mis.
   `SPRINKLES (berbisik, takut, pelan): "Did you... hear that?" (gasps)`.
3. **Naskah ditulis untuk diucapkan**: kalimat pendek, terpotong, saling menyela, reaksi ("Wha—?", "Hmm…", tawa gugup),
   bukan paragraf rapi. Narator dikurangi; cerita lewat aksi & dialog.
4. **Akting tubuh mobil**: antisipasi sebelum bicara, bodi condong saat bicara, lompat kecil saat senang, menciut saat
   takut, kepala (kabin) menoleh ke lawan bicara, kedip & lirik mata, keringat/air mata — dengan aturan *squash & stretch*.
5. **QA**: Whisper (sudah ada) + cek variasi intonasi (pitch range per kalimat) agar tidak datar.

## 4. 3D & Modal: riset biaya dan jalur yang masuk akal
- Infrastruktur sudah ada sejak 2026-09-30: Blender di Modal (Cycles OptiX L4 ±1 GPU-detik/frame), tokoh 3D prosedural
  (`generators/blender3d/cast3d.py`, catatan user saat itu: "harusnya lebih kartun").
- Hitungan kasar 15 menit penuh 3D: 27.000 frame × ±1 GPU-s = **±$6–10/episode (Cycles)** → terlalu mahal untuk budget
  $29/bulan bersama Shorts. **Eevee** (rasterisasi, GPU) diperkirakan 4–8× lebih cepat → **±$1–2/episode**.
- Rekomendasi bertahap: (a) Ep. 2 tetap 2.5D dengan kamera & musik baru; (b) **uji 3D untuk 1 adegan kunci** (cold open
  jejak kaki Kraggor di malam berkabut) dengan Blender Eevee di Modal + tokoh 3D yang lebih kartun; (c) kalau user
  menilai jauh lebih bagus dan biayanya aman → adegan hook & klimaks 3D, sisanya 2.5D (hybrid).
- Modal juga dipakai lebih maksimal untuk: perpustakaan musik (ACE-Step), suara ekspresif (Turbo/Dia), QA Whisper.

## 5. Hook yang legendaris
Riset retensi: 15–30 detik pertama menentukan apakah YouTube merekomendasikan video; animasi pendek sehat di rata-rata
tontonan 60–70%. Pixar menanam hal yang dibicarakan penonton (callback, easter egg).
Resep hook Ep. 2 (dan pola tetap seri):
1. **Gambar ikonik**: jejak kaki raksasa yang masih berasap di jalan basah, lampu jalan padam satu per satu menuju kamera,
   lalu **dua mata kuning** terbuka di kabut — gambar yang bisa jadi thumbnail dan dikenali.
2. **Bunyi khas Kraggor**: 3 nada rendah + dentuman (motif yang selalu muncul sebelum ia tampil) — penonton belajar
   "bunyi ini = Kraggor".
3. **Pertanyaan yang tak terjawab**: "Who is Kraggor?" — dijawab pelan-pelan (misteri berlapis), bukan sekaligus.
4. **Taruhan emosional dalam 30 detik**: Sprinkles kecil sendirian di depan sesuatu yang raksasa.
5. **Callback/easter egg**: lagu truk es krim Grandpa (Ep. 1) muncul lagi sebagai kunci cerita; detail kecil yang bisa
   dicari penonton ulang (foto lama, ukiran "K.").
6. **Kalimat yang diulang** (catchphrase) di akhir tiap episode.

## 6. Rencana pilot (dinilai user sebelum produksi penuh)
| Pilot | Isi | Yang diuji |
|---|---|---|
| A | Scene 1 cold open (±60 dtk) | kamera baru (dolly/pan/handheld/dutch), musik cue + motif Kraggor, hook ikonik |
| B | Scene 9 "Face to Face" (±60 dtk) | akting suara Turbo vs Dia, naskah lisan, akting tubuh mobil, tema Kraggor versi lembut |
| C (opsional) | Cold open versi 3D Eevee di Modal | perbandingan 2.5D vs 3D + biaya nyata per menit |

## 7. Keputusan yang dibutuhkan dari user
1. Kerangka cerita Ep. 2 (outline.md): inti Grandpa ↔ Kraggor kecil, Kraggor tidak bicara, kait Ep. 3, Rocky ikut — setuju?
2. Setuju urutan kerja: pilot A + B dulu (lalu C bila 3D ingin diuji), baru produksi 15 scene?
3. Data retensi Ep. 1 (YouTube Studio, 2–3 hari lagi) akan dipakai untuk menentukan di menit berapa penonton pergi →
   pacing Ep. 2.

## Sumber
- TTS: [Chatterbox (MIT, Turbo paralinguistic tags)](https://github.com/resemble-ai/chatterbox) · [Dia (Apache-2.0)](https://github.com/nari-labs/dia) ·
  [Orpheus](https://github.com/canopyai/Orpheus-TTS) · [BentoML: open-source TTS 2026](https://www.bentoml.com/blog/exploring-the-world-of-open-source-text-to-speech-models)
- Musik film: [Leitmotif (AudioCipher)](https://www.audiocipher.com/post/leitmotif) · [Scoring techniques](https://flipeducation.ai/curriculum/us/arts/grade-12/music-and-visual-media-scoring-techniques)
- Kamera: [Cinematography language in animation](https://quizzly.ai/play/cinematography-language-in-animation) · [How to tell a story with camera](https://23014835.myblog.arts.ac.uk/?p=18)
- Hook & retensi: [Retention benchmarks for animated YouTube videos](https://longstories.ai/blog/retention-benchmarks-animated-youtube-videos) ·
  [YouTube hooks & retention](https://outlierkit.com/resources/youtube-hooks-and-retention/) · [How Pixar hooks audiences](https://scottdikkers.substack.com/p/how-pixar-hooks-audiences-before)

## 8. Pilot C (Godot) — analisa dari pelajaran 3–4 Okt agar hasilnya jauh lebih baik & konsisten
| Pelajaran kemarin (QA_DEFECT_TRACKER / ERROR_LOG) | Aturan untuk pilot C |
|---|---|
| Konversi mobil ke 3D → bodi melengkung, Kraggor aneh, tidak konsisten | **Tokoh tidak digambar ulang**: mobil, wajah, subtitle, letterbox = gambar asli story25d (overlay alpha). Godot hanya dunia, cahaya, kabut, jejak kaki, mata Kraggor (gaya hybrid, sampel pantai S027). |
| Kamera tebakan → salah skala / posisi | **Kamera dari data**: matriks kamera story25d per frame (zoom, pan, dutch, handheld, push) dibaca langsung dari cairo; proyeksi story = pinhole (k = F/(D0+DZ·z), horizon Y_H, tinggi CAM_H) → kamera Godot setara (fokus, roll, lens shift). Diverifikasi frame-per-frame terhadap overlay sebelum render penuh. |
| Warna pucat di Vulkan; matahari/bayangan salah; bayangan dimatikan untuk menutupi | Warna lewat `source_color`; cahaya malam dirancang (bulan + lampu jalan + lampu mobil), bayangan tidak dimatikan. Mode **Forward+** (kabut volumetrik butuh ini). |
| Gaya 3D realistis vs tokoh kartun datar = terlihat tempelan | **Toon shading** (diffuse/specular toon), palet warna sama dengan set cairo, garis siluet sederhana; 3D dipakai untuk **cahaya, kedalaman, kabut**, bukan realisme. Malam: tokoh diberi tint malam yang sama (hanya pada piksel tokoh). |
| Bug tak terlihat lolos review (kontainer) | **Sensor**: jejak kaki & mata Kraggor wajib terlihat (piksel) di shot-nya; lampu padam sesuai jadwal; cek otomatis sebelum dikirim. |
| Batch/paralel di VM → OOM, kode lama | Render di Modal T4 (per bagian), compose ringan di VM, satu proses, cek HEAD. |
Yang dibuat lebih baik oleh 3D (alasan memakai Godot di adegan ini): sorotan lampu mobil **menyinari kabut sungguhan** (volumetrik), genangan cahaya lampu jalan nyata yang **padam satu per satu**, jejak kaki sebagai decal yang **terungkap saat tersorot**, mata Kraggor yang **memancarkan cahaya di kabut**, kedalaman kota (gedung berlapis, jendela menyala).
