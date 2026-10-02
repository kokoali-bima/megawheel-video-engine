# RESEARCH_W2 — riset kanal sukses → upgrade minggu 2–3

> Permintaan user 2026-10-02: riset video mirip yang sudah sukses (judul/hook, cahaya & suara, cerita & struktur,
> animasi 2D + lip-sync, theme song, hal lain) untuk produksi minggu 2–3. **Tidak mengubah apa pun yang sudah
> di-approve / di antrean upload.** Lengkapi PRODUCTION_STANDARD.md (standar umum) dengan temuan di bawah.

## 0. Pembanding
- **BeamNG "cars vs ..." Shorts** (mis. BeamngShorts, >7 juta subscriber): format perbandingan (mobil vs rintangan,
  besar vs kecil, beruntung vs sial), kekacauan fisika = pemicu retensi. Kita punya formatnya, ditambah tokoh bernama.
- **Bluey** (episode 7–11 menit): tiga babak / story circle, hampir tanpa B-story ("condense and condense").
- **CoComelon/Moonbug**: jadwal tetap, judul & thumbnail diuji, keputusan berbasis data audiens.
- **Kartun TV klasik** (theme song): lagu singkat, kait berulang, nama acara dinyanyikan, gampang dihafal.
- Data channel kita (minggu 1): Potholes 860 + 524 views vs Speed Bumps 274 + 82 + 64 → tema lubang ≈ 3×.

## 1. Judul & hook (cara yang benar, bukan clickbait)
| Temuan | Terapkan |
|---|---|
| Curiosity gap: tunjukkan situasi, sembunyikan hasilnya; janji yang **ditepati** (algoritma Shorts menilai retensi & kepuasan, clickbait dihukum) | judul = **tokoh + tantangan + pertanyaan**: "Can an Ice Cream Truck Survive Giant Potholes?" |
| Pola efektif: pertanyaan, kontras/underdog, "what happens if…" | "Tiny Taxi vs Monster Truck — Who Wins?", "What Happens If a Bus Hits Giant Potholes?" |
| Hook berlapis (visual + suara + teks) di 1–3 detik pertama → 3-second hold ±3× | frame 1 sudah aksi + teks besar + suara (bukan intro); narator langsung "Can Sprinkles…?" |
| Judul Shorts tampil kecil; **frame pertama & teks di layar** lebih menentukan | teks atas = pertanyaan yang sama dengan judul |
| Tema yang terbukti di channel kita | perbanyak **Potholes** & variasinya (lubang air, lumpur, lubang berjalan) |

## 2. Pencahayaan & suara
| Standar | Kita sekarang | Upgrade |
|---|---|---|
| Key + fill + **rim light** (siluet terpisah dari latar) | warna datar | rim light tipis di tepi bodi mobil (arah sesuai matahari/bulan) |
| Bayangan lembut + arah cahaya konsisten | bayangan elips | bayangan diarahkan sesuai waktu (pagi panjang, siang pendek) |
| Cahaya = emosi (badai → gelap & dramatis; sore → hangat) | preset waktu | **color grading per mood** per scene + vignette |
| Suara 5 lapis (dialog, SFX, foley, ambience, musik) | dialog, SFX, ambience ✅, musik synth | **foley** (mesin idle, ban, rem), musik orkestra per mood |
| SFX sinkron gerak ("mickey-mousing" ringan) | sebagian | bunyi tepat di frame tabrakan/lompat/kedip |
| Stereo, -14…-16 LUFS | lagu tema stereo ✅ | seluruh mix stereo (musik & ambience lebar, dialog tengah) |

## 3. Cerita & struktur
- **Story circle / 3 babak, satu A-story** (Bluey): masalah → mencoba → gagal → belajar → berhasil → berubah.
  → Ep. 2: buang sub-plot "Meanwhile in Town" atau jadikan 1 scene pendek; fokus Sprinkles ↔ Kraggor.
- Cold open + kait per babak (sudah di Ep. 1) + **recap 20–30 dtk** di Ep. 2.
- **Shorts** = cerita mini 3 ketukan: tantangan (0–3 dtk) → percobaan/kekacauan → payoff + **ending yang nyambung ke
  awal** (loop) supaya ditonton ulang.

## 4. Animasi 2D lebih keren, smooth, lip-sync
| Teknik | Kita sekarang | Upgrade (open source) |
|---|---|---|
| **Lip-sync berbasis fonem (viseme)**: 6–12 bentuk mulut Preston Blair (M-B-P tertutup, O bulat, E lebar, F-V) | mulut buka-tutup dari volume suara | **Rhubarb Lip Sync** (MIT, CLI Linux): audio + teks → urutan bentuk mulut A–H/X per waktu → gambar 8 bentuk mulut mobil |
| Squash & stretch saat bicara, tekanan di suku kata keras | — | badan sedikit memantul di puncak volume |
| **Anticipation → action → follow-through** | sebagian | mundur sedikit sebelum melesat; bergoyang setelah berhenti |
| **Secondary action**: cone/antena/lampu bergoyang, napas/idle saat diam | hop, squash | idle "napas" + goyangan aksesori |
| Akting pendengar: mengangguk, mata melirik ke pembicara | — | mata tokoh lain menoleh ke pembicara; kedip di jeda kalimat |
| Gerak halus (easing) | glide kamera, easing gerak ✅ | ease in/out juga untuk ekspresi & alis |

## 5. Theme song — penilaian jujur
**Cukup baik untuk sekarang (nilai B):** energik, ceria, nama "MegaWheel Arena" dinyanyikan berulang, chorus gampang
diikuti, 28 dtk (ideal 20–30 dtk), cocok dengan semangat channel.
**Kekurangan:** vokal AI kadang kurang jelas ("Mega-Mega"), lirik masih umum (belum menyebut tokoh), belum ada
**sonic logo**. **Upgrade:** (a) potong **jingle 3–5 dtk "MegaWheel... ARENA!"** untuk pembuka/penutup Shorts dan
end card (identitas suara di setiap video); (b) varian instrumental untuk background; (c) nanti: lirik bait
berisi tokoh (usulan user sebelumnya) bila ada take yang jelas.

## 6. Hal lain yang perlu
1. **Panjang Shorts**: 15–30 dtk sering >80% retensi + loop ulang; Shorts kita 44–57 dtk → uji varian 30–40 dtk
   (A/B per seri) tanpa mengubah stok yang sudah approved.
2. **Thumbnail video panjang**: wajah ekspresif (Sprinkles kaget + Kraggor), kontras tinggi, maks 3–4 kata,
   2–3 elemen, 1280×720.
3. **Subtitle .srt** dari naskah (kita punya teks & waktu tiap kalimat) → upload ke YouTube: aksesibilitas + SEO.
4. **Audio multi-bahasa** (dubbing ES/PT/ID dengan TTS kita) → fitur multi-language audio YouTube: jangkauan global.
5. **Analitik mingguan**: retensi per detik, swipe-away Shorts, CTR thumbnail → tabel di EPISODE_LOG (episodes.py set).
6. Kebijakan konten tidak autentik: terus variasikan arena, rintangan, tokoh, cerita.

## Roadmap upgrade (tanpa menyentuh yang approved)
| Minggu | Shorts | Story (Ep. 2–3) |
|---|---|---|
| **2** | judul pola baru + teks pertanyaan di frame 1; jingle sonic logo; tema potholes diperbanyak; uji panjang 30–40 dtk | Rhubarb lip-sync + 8 bentuk mulut; idle/napas; rim light + grading; recap; thumbnail; .srt |
| **3** | loop ending; foley mesin/ban | musik orkestra per mood; mix stereo penuh; depth of field; match cut; dubbing 1 bahasa (uji) |

## Sumber
- Judul/hook: vidIQ "Viral Hooks for YouTube Shorts 2026"; clipspeed.ai titles; joinotto hooks & curiosity loops;
  blitzcutai hooks 2026
- Lip-sync: Rhubarb Lip Sync (via LipKit/TotalLipSync docs); highonfilms lip-sync techniques (Preston Blair)
- Theme song: musicalwonders "How to write a cartoon theme song"; thefwoosh top cartoon themes
- Struktur: Ragan "Lessons from the creator of Bluey"; zanevoss "Bluey's Guide to Story Structure"
- Cahaya: cg-wire "How Light Shapes Emotion in Animation (2026)"; Google Research "Tweakable Light and Shade"
- Panjang Shorts: toptal, async.com, eliro.pro (2026)
- Thumbnail: vidIQ thumbnail tips 2026; subscribr thumbnail best practices
- Prinsip animasi: Thomas & Johnston (12 principles)
- BeamNG Shorts: BeamngShorts channel profile
