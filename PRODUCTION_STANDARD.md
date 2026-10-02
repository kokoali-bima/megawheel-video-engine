# PRODUCTION_STANDARD — standar produksi internasional MegaWheel Arena

> Tujuan (user, 2026-10-02): "biar video buatan kamu dan saya, standar yang kita pakai tetap harus standar
> internasional, siap bersaing di dunia." Setiap episode harus lebih baik dari sebelumnya.
> Dokumen ini = hasil riset + gap analysis mesin `story25d` + prioritas. Diperbarui setiap episode.

## 1. Retensi & struktur (riset YouTube 2025–2026)

| Standar | Kenapa | Status kita |
|---|---|---|
| **Cold open dulu, baru ident + lagu tema** | Intro panjang di depan menjatuhkan retensi (kasus: 30-detik retensi 52% → 78% setelah intro dipangkas); 20% penonton pergi di 10 detik pertama | ✅ v9: `edit.json` → `order` [scene 1, ident, tema, ...] |
| 0–5 detik: visual/emosi paling kuat, mulai di tengah aksi | algoritma menilai distribusi dari retensi 30–60 detik pertama | ✅ v9: teaser kilat + mata kuning di gelap |
| Kait di akhir setiap babak, payoff dulu baru pertanyaan | cliffhanger yang hanya menahan informasi terasa menipu | ✅ freeze-frame cliffhanger per scene |
| **Recap "Previously on…" 20–30 dtk** di episode lanjutan | penonton baru langsung paham; penonton lama ingat | ⏳ Ep. 2 |
| Chapters di deskripsi | navigasi + SEO | ✅ v9: `<ep>_h_chapters.txt` otomatis |
| End screen 5–20 dtk area bersih | elemen end screen YouTube (video berikut, subscribe) | ✅ v9: 14 dtk |
| Iterasi berbasis data (cara Moonbug membesarkan CoComelon: jadwal tetap, judul/thumbnail diuji, umpan balik audiens) | | ⏳ baca kurva retensi Ep. 1 di Analytics → ubah Ep. 2 |

## 2. Gambar & environment

| Teknik standar | Penjelasan | Status | Prioritas |
|---|---|---|---|
| **Parallax 3–4 lapis** | jauh bergerak lambat, dekat cepat; elemen *foreground* (semak, tiang, pagar) lewat di depan kamera saat tracking | sebagian (props depan/belakang) | **P1** |
| **Atmospheric perspective** | makin jauh makin pucat, kurang kontras, kebiruan | sebagian | P1 |
| **Depth of field** pada close-up | latar diburamkan → wajah tokoh menonjol (kesan sinematik) | belum | **P1** |
| **Color script / grading per mood** | tiap scene punya palet emosi (hangat=harapan, biru=sedih, ungu-merah=bahaya) + vignette | sebagian (waktu hari, sepia) | P1 |
| Rim light | garis cahaya di tepi siluet: siluet terbaca + dramatis | belum | P2 |
| **Acting tokoh**: anticipation, squash & stretch, *secondary motion* (cone bergoyang, antena), napas/idle saat diam | mobil diam terasa "mati" (review v6 poin 19–20) | sebagian (hop, squash) | **P1** |
| Asap knalpot / debu roda / percikan | menjual gerak | sebagian (lumpur) | P2 |
| Komposisi 3 lapis (foreground framing, midground fokus, background suasana) | | sebagian | P2 |

## 3. Transisi & editing

| Teknik | Kapan dipakai | Status |
|---|---|---|
| **Match cut** (bentuk/warna/gerak/suara nyambung: mata Kraggor → bulan) | pindah waktu/tempat dengan makna | ⏳ Ep. 2 (butuh fitur "shape match") |
| Whip pan + motion blur, potongan disembunyikan di gerak kamera | energi, balapan | ✅ `hblur` |
| Dissolve panjang | kenangan / kilas balik | ✅ |
| Fade hitam / putih | akhir babak / kejutan | ✅ |
| Wipe / iris | gaya retro — **jarang** | — |
| Kamera meluncur antar-shot, tidak terburu-buru | review v6–v7 | ✅ glide + jeda akhir scene |

## 4. Suara (5 lapis: dialog · SFX · foley · ambience · musik)

| Lapis | Standar | Status |
|---|---|---|
| Dialog | jelas, di tengah (center), tidak tertutup musik (ducking) | ✅ Chatterbox + QA Whisper + ducking |
| SFX | menandai aksi penting; tidak ada suara yang "tidak cocok" (lebih baik hening) | ✅ (hentakan kaget dihapus, v8) |
| **Foley** | mesin menyala/idle per mobil, ban di aspal/kerikil, rem, klakson | belum | **P1** |
| Ambience | tiap tempat punya "dunia suara" (arena=penonton, siang=burung, malam=jangkrik, garasi=room tone, hujan) | ✅ v9 |
| **Musik latar orkestra** | underscore per mood (piano sedih, string tegang, orkestra harapan) — bukan synth chiptune | belum (synth) | **P1**: ACE-Step instrumental per mood |
| **Stereo** | musik & ambience lebar, dialog di tengah | ✅ lagu tema (v9); ⏳ seluruh mix scene | P1 |
| Loudness | -14…-16 LUFS, true peak ≤ -1.5 dB | ✅ loudnorm -16 |

## 5. Prioritas untuk Episode 2 (urut)

1. Recap "Previously on MegaWheel Arena" (20–30 dtk) setelah cold open.
2. Musik latar orkestra per mood (ACE-Step instrumental, lisensi Apache-2.0) + mix scene stereo penuh.
3. Depth of field close-up + parallax foreground + color grading per mood.
4. Foley mesin/ban per mobil; idle "napas" mobil diam.
5. Match cut untuk perpindahan waktu (mata Kraggor ↔ bulan; foto lama ↔ masa kini).
6. Analitik Ep. 1 (retensi per menit, titik penonton pergi) → masukan naskah Ep. 2.

## Sumber riset (2026-10-02)
- Retensi & intro: teleprompter.com "How long should a YouTube intro be"; subscribr.ai hooks; wpreset.com Shorts 2026; capcut.com cliffhanger series
- Background/depth: Binus DKV "Backgrounds that Breathe"; pixune.com "How to make 2D art look 3D"; gamemaker.io parallax
- Transisi: Yale Film Analysis (editing devices); melies.co transitions; neilchasefilm.com
- Suara: IRPR Sound (sound design for animation, checklist); krotos.studio
- Industri: Bloomberg/Fortune tentang Moonbug & CoComelon (strategi berbasis data)
