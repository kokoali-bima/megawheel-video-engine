# SFX_PLAN — suara efek kelas profesional untuk MegaWheel Arena

> Permintaan user 2026-10-03: suara efek kita (synth buatan sendiri) kurang seru, misalnya meteor jatuh. Riset mesin
> yang lebih baik. Keputusan lisensi mengikuti Jalur A (channel dimonetisasi → hanya lisensi komersial).

## 1. Masalah sekarang
SFX = sintesis matematis (noise + sinus) di `sim_engine.py`. Murah & bebas lisensi, tapi terdengar "elektronik/datar":
tidak ada tekstur nyata (puing besi, kaca, api menderu, gemuruh), tidak ada variasi, tidak ada ruang (stereo/reverb).

## 2. Pilihan (riset)
| Sumber | Kualitas | Lisensi untuk channel monetisasi | Catatan |
|---|---|---|---|
| **Sonniss GDC Game Audio Bundle** (2015–2026, ±200 GB, 7,5 GB edisi 2026) | ⭐⭐⭐⭐⭐ pro (sama dengan versi berbayar) | ✅ royalty-free komersial, tanpa atribusi, seumur hidup | **dilarang untuk melatih AI** (kita hanya memakai, aman) |
| Kenney audio packs, BigSoundBank, SFXMint | ⭐⭐⭐ | ✅ CC0 (public domain) | UI, klik, langkah, ambient sederhana |
| Freesound (filter **CC0** saja) | ⭐⭐–⭐⭐⭐⭐ bervariasi | ✅ hanya yang CC0; CC-BY wajib kredit, CC-BY-NC ❌ | butuh API key gratis |
| **Stable Audio Open** (generator AI, Modal GPU) | ⭐⭐⭐⭐ untuk efek unik (auman Kraggor, meteor kartun) | ✅ Stability Community License: komersial gratis selama pendapatan < $1 juta/tahun | output 47 dtk stereo 44,1 kHz |
| ElevenLabs Sound Effects (API) | ⭐⭐⭐⭐⭐ | ✅ dengan paket berbayar (Starter ±$5–6/bulan); free tier tanpa lisensi komersial | ±$0,12/menit audio via API |
| TangoFlux, Woosh, AudioGen, AudioLDM-NC | ⭐⭐⭐⭐ | ❌ non-komersial | jangan |

## 3. Rekomendasi: "SFX bank" berlapis
1. **Basis = Sonniss GDC** (unduh di VM 99.3, simpan di `/root/sfx/`, tidak masuk git) + CC0 (Kenney/BigSoundBank).
2. **Indeks berlabel** `branding/sfx/bank.json`: kategori → beberapa varian (explosion_big, explosion_small,
   meteor_whoosh, metal_crash, glass_shatter, debris_rain, tire_skid, engine_loop_{truck,sports,monster}, crowd_cheer,
   crowd_gasp, whoosh_cartoon, boing, kraggor_roar, ...), dengan loudness ternormalisasi.
3. **Layering otomatis per kejadian** (cara studio): mis. ledakan = boom rendah + crack tengah + puing/kaca + ekor
   reverb; meteor = whoosh mendekat (Doppler/pitch turun) → impact → gemuruh.
4. **Variasi**: pilih varian acak + pitch ±5–10% → tidak pernah sama di tiap video.
5. **Ruang**: panning stereo sesuai posisi di layar (Godot AudioStreamPlayer2D melakukannya otomatis), reverb ringan
   untuk arena, ducking di bawah narasi.
6. **Celah yang tak ada di library** (auman Kraggor, efek kartun khas) → Stable Audio Open di Modal (lisensi aman),
   hasil di-QA telinga user sebelum masuk bank.

## 4. Langkah
1. Unduh Sonniss GDC 2026 (+ beberapa tahun sebelumnya) ke VM; tandai kategori yang dibutuhkan (±1–2 GB terpakai).
2. Buat `bank.json` + `sfx_bank.py` (pilih varian, layer, pitch, pan) → dipakai `godot_mix.py` dan mesin cairo.
3. Uji A/B: SMASH Godot dengan synth lama vs SFX bank → user menilai.
4. Generator Stable Audio Open di Modal untuk 5–10 efek khas MegaWheel.

## Sumber
Sonniss GDC 2026 bundle (rekkerd.org; zeli.app "10 years of GDC sound effects"); Stability AI — Stable Audio Open 1.0
(Hugging Face) & Community License; TangoFlux (Hugging Face, non-komersial); Woosh (arXiv 2604.01929, non-komersial);
ElevenLabs SFX API pricing (costbench.com); SFXMint & BigSoundBank (CC0).
