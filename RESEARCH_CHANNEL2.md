# RESEARCH_CHANNEL2 — channel kedua (riset 2026-10-08)

> Pemilik 2026-10-08: "saya ingin punya 3 channel, targetnya akhir tahun sudah ada yang monetize. Syarat: tidak melanggar
> syariah, lagi banyak peminatnya, masih baru-baru ini in-nya, diperkirakan stabil, masih sedikit kreator yang melirik,
> terutama pasar US." Musik ringan seperti MegaWheel: boleh (pemilik).
> Data: `generators/publishing/niche_scan.py` (YouTube Data API, hanya baca) → `work/niche_scan_2026-10-08_scan1/2.{md,json}` di VM.

## 1. Batas waktu yang menentukan strategi
- YPP sekarang: 1.000 subscriber + 4.000 jam tonton (12 bulan) **atau** 10 juta view Shorts (90 hari).
- **Mulai 1 Februari 2027 pendaftar BARU butuh 8.000 jam atau 20 juta view Shorts** (blog resmi YouTube, 10 Agu 2026).
  Channel yang sudah masuk YPP sebelum itu tidak terkena. → Kejar pendaftaran sebelum 1 Feb 2027.
- MegaWheel (28 hari s/d 5 Okt): 3.541 view, ±14 jam, +14 subscriber → jauh dari syarat.
- Kebijakan "inauthentic content" (2025–2026): konten massal bertemplat tidak dimonetisasi. AI boleh, asal orisinal,
  bervariasi, dan bernilai. Channel baru harus punya nilai nyata (akurat, mendidik), bukan satu template diulang.

## 2. Cara mengukur
Per kata kunci: 25 video teratas (US, bahasa Inggris, terbit 120–180 hari terakhir, urut views). Diukur:
**permintaan** (median views), **persaingan** (jumlah channel, umur channel), dan **celah** = "hit channel kecil"
(channel < 50 rb subscriber yang dapat ≥ 500 rb views) + channel umur ≤ 12 bulan. Banyak channel muda/kecil yang
tembus jutaan view = permintaan lebih besar dari pasokan = peluang.

## 3. Hasil (ringkas)

| Kelompok | Kata kunci | Median views | Channel ≤12 bln | Hit channel kecil | Bacaan |
|---|---|---|---|---|---|
| **Teknik/fisika 3D** | how dams work | 1,29 jt | **17** | **12** | gelombang baru, banyak channel muda |
| | how tunnels are built | 1,29 jt | **15** | 6 | 〃 |
| | how bridges are built | 1,99 jt | **13** | **11** | 〃 |
| | engineering explained 3d | 1,34 jt | 9 | **12** | 〃 |
| | physics explained animation | 4,13 jt | 7 | **12** | 〃 |
| | inside machine animation | 1,26 jt | 9 | 11 | 〃 |
| | how it works 3d animation | 9,77 jt | 7 | 8 | 〃 |
| Bencana (simulasi/penjelasan) | dam break simulation | 0,77 jt | 5 | **14** | ramai saat ada berita bencana |
| | tornado simulation | 2,37 jt | 3 | 11 | sebagian besar game/Roblox |
| | earthquake simulation | 1,32 jt | 4 | 7 | |
| Mobil (niche kita sekarang) | beamng cars vs | **18,6 jt** | 5 | **1** | permintaan besar, **dikuasai channel besar** |
| Fisika "satisfying" | marble race / bouncing ball | 6–9 jt | 2–3 | 2–3 | dikuasai sedikit pemain |
| Antariksa "what if" | what if earth | 7,1 jt | 1 | 1 | dikuasai sedikit channel besar |

Contoh nyata (views / subscriber / umur channel):
- "How Does an ATM Count & Dispense Money?" — **34,9 jt** / 98 rb / **4,7 bln** (Discover Inside)
- "Kolkata Underwater Metro Tunnel Engineering Explained | 3D Animation" — **17,3 jt** / 60 rb / **2,6 bln** (Mr Decode)
- "How This Giant Machine Builds Tunnels Under the Sea" — 15,0 jt / 100 rb / 8,6 bln
- "If Dams Stop Floods, Why Do Floods Still Happen? | Explained in 3D" — 5,8 jt / 35 rb / 7,4 bln
- "How Dams Generate Electricity (3D Animation)" — 5,0 jt / **9,8 rb** / **1,7 bln**
- "How Japan Builds Skyscrapers That Survive Massive Earthquakes" — 2,3 jt / **4,9 rb** / 4,2 bln
- "Why Buildings React Differently To Earthquakes" — **21,8 jt** / 284 rb / 27 bln

Catatan penting: banyak pemenangnya channel India/Asia yang berbahasa Inggris atau Hindi. Untuk pasar **US**, penjelasan
berbahasa Inggris dengan aksen US, contoh lokal US (Hoover Dam, Golden Gate, terowongan NYC, jalan tol AS), dan akurasi
tinggi masih jarang → **celah pasar US**.

## 4. Rekomendasi channel kedua
**"Cara kerja & kekuatan rekayasa, dalam 3D"** — penjelasan teknik dan fisika: cara kerja mesin dan infrastruktur
(bendungan, terowongan, jembatan, pesawat, mesin), dan kenapa bangunan bertahan atau runtuh saat gempa, banjir, angin.

Kenapa cocok dengan syarat pemilik:
| Syarat | Bukti |
|---|---|
| Banyak peminat | median 1–10 jt view per kata kunci (6 bulan terakhir) |
| Baru naik & sedikit kreator | 9–17 dari 25 video teratas berasal dari channel umur ≤ 12 bulan; channel 2–8 bulan tembus 5–35 jt |
| Stabil | rasa ingin tahu "bagaimana cara kerjanya" itu abadi (evergreen); berita bencana memberi lonjakan berkala |
| Syariah | mesin, bangunan, alam; tanpa tokoh makhluk, tanpa judi/aurat; musik ringan atau tanpa musik |
| Pasar US | konten berbahasa Inggris dengan contoh US masih jarang di hasil pencarian US |
| Monetisasi | kategori Pendidikan & Sains = RPM tertinggi (median ±$10 untuk video panjang); bernilai edukasi = aman dari kebijakan "inauthentic" |
| Cocok mesin kita | Godot 3D + fisika (sudah ada), Blender di Modal (director3d), narator voice C, pipeline QA dan jadwal upload |

Risiko:
1. **Celah bisa cepat tertutup** — banyak channel baru masuk (justru itu sebabnya harus mulai sekarang).
2. **Akurasi wajib** — salah fakta merusak kepercayaan dan rawan dilaporkan. Setiap naskah perlu sumber dan pengecekan.
3. **Aset 3D** — mesin/infrastruktur butuh model 3D. Sumber: model CC0 (Poly Haven, NASA, dll.), model prosedural
   di Blender/Godot. Jangan pakai video AI mentah (mudah salah dan rawan "inauthentic").
4. Topik tragedi (korban jiwa) dibatasi iklannya → fokus ke "cara kerja" dan "kenapa bertahan", bukan sensasi korban.

## 5. Kandidat channel ketiga (dicatat, belum diuji)
- Penjelasan bencana alam + simulasi (gempa, banjir, tornado) yang cepat mengikuti berita — bisa jadi seri di channel 2 dulu.
- Antariksa "what if" — permintaan besar tapi dikuasai sedikit channel besar (bukan prioritas).

## 6. Rencana uji (2 minggu, sebelum membuat channel)
1. **Validasi lanjutan (1–2 hari):** scan 30–50 topik spesifik US (Hoover Dam, Golden Gate, Lincoln Tunnel, I-35W bridge,
   jet engine, elevator, escalator, traffic light, water tower...) → pilih 20 topik dengan celah terbesar.
2. **Prototipe 3 Shorts (30–60 dtk) + 1 video panjang (8–10 mnt)** dengan pipeline Godot/Blender kita, narator voice C,
   naskah bersumber. Self-review dengan sensor QA yang sudah ada.
3. **Review pemilik** → baru buat channel, upload 1/hari, ukur 14 hari: % "tetap menonton" (target ≥ 70%), views per
   video, subscriber per 1.000 view. Pertahankan format yang menang.
4. MegaWheel tetap jalan seperti sekarang (Ep. 52 3D tayang 20 Okt jadi uji 3D vs 2.5D).

Sumber: YouTube Official Blog (10 Agu 2026, perubahan YPP 2027); YouTube Help 72851 (syarat YPP); AIR Media-Tech (RPM per
niche 2026); OutlierKit/lenspov (kebijakan inauthentic content 2026); data YouTube Data API (scan di atas).
