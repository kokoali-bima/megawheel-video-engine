# MegaWheel Arena — Cast Bible (tokoh tetap)

> Data mesin: `/root/video-engine/cast/characters.json` (dibaca otomatis oleh engine).
> Fisika kendaraan: `VEHICLES` di `/root/video-engine/generators/physics_2d/sim_engine.py`.

## Tokoh tetap

| Tokoh | Kendaraan | Peran | Warna | Sifat | Kalimat khas | Rival |
|---|---|---|---|---|---|---|
| **Zippy** | Sports car | Ringan | Merah | Super cepat, sedikit sombong, selalu terburu-buru | "Zoom zoom, make room!" | Siren |
| **Siren** | Mobil polisi | Ringan | Putih-hitam | Berani, agak suka mengatur, lampunya berkedip di setiap tanda bahaya | "Wee-woo! Coming through!" | Zippy |
| **Buster** | Bus sekolah | Berat | Kuning | Baik hati, sabar, hati-hati, pantang menyerah | "Slow and steady, everybody ready!" | Hydro |
| **Hydro** | Mobil pemadam | Berat | Merah | Penolong yang kuat, suka menyemprot air, ceria, agak ceroboh | "Splash and dash!" | Buster |
| **Rocky** | Monster truck | Juara | Biru | Juara yang ramah, suka lompatan besar, menyemangati teman | "Big wheels, big jump!" | Grizzly |
| **Grizzly** | Monster truck | Juara | Hijau | Rival Rocky yang galak seperti beruang, tapi sebenarnya baik | "Grrr-owl! Out of my way!" | Rocky |
| **Nitro** | Mobil F1 | Ringan | Biru | Pembalap paling cepat, tidak sabaran, cinta kecepatan | "Full throttle, no stopping!" | Zippy |
| **Tilly** | Taksi | Ringan | Kuning (kotak-kotak) | Ramah dan cerewet, hafal semua jalan, suka mengantar teman | "Hop in, let's go!" | Siren |
| **Titan** | Truk gandeng (big rig) | Berat | Oranye + trailer perak | Raksasa yang kalem, sangat kuat tapi lambat | "Big load, no problem!" | Buster |
| **Sprinkles** | Mobil es krim | Berat | Pink + mint | Manis dan ceria, favorit semua anak | "Ice cream time!" | Hydro |

## Aturan penokohan (wajib untuk semua agent)

1. **Nama, warna, dan sifat tokoh TIDAK boleh diubah** tanpa persetujuan user. Penonton mengenali tokoh dari nama dan warnanya.
2. **Tokoh tidak dibuat otomatis per video.** Tokoh baru hanya ditambah dengan sengaja sebagai "episode debut", lalu dicatat di `characters.json` dan tabel di atas.
3. **Rotasi adil (otomatis):** untuk setiap peran, engine memilih tokoh yang paling jarang tampil (dihitung dari `PRODUCTION_REGISTRY.json`). Kalau jumlahnya sama, seed yang menentukan.
4. **Cek nama baru** sebelum dipakai: jangan sama dengan tokoh kartun/brand terkenal (contoh: "Blaze" dan "Crusher" diganti karena sama dengan serial *Blaze and the Monster Machines*).
5. Peran menentukan fisika: `light` / `heavy` = biasanya gagal, `champion` = biasanya menang. Cerita underdog (tokoh berat menang) butuh lintasan khusus → roadmap.

## Riwayat
- 2026-09-30: 6 tokoh ditetapkan. "Blaze" → **Hydro**, "Crusher" → **Grizzly** (sebelum pernah dirender/diupload).
- 2026-09-30: +4 tokoh → **10**: Nitro (F1), Tilly (taksi), Titan (truk gandeng), Sprinkles (mobil es krim). Uji fisika (`tune_cast.py`): keempatnya bisa berperan gagal di potholes & bumps (3/3 seed). Nitro & Tilly kadang bisa menang di potholes.
- Kalau tokoh terpilih tidak bisa menghasilkan hasil yang diminta di lintasan itu, engine otomatis memakai tokoh berikutnya di peran yang sama (log `[cast] ... trying next character`).

## Ide ke depan
- Statistik per tokoh (tampil / menang / gagal) dari registry → konten "Siapa juara terbanyak?".
- Kalimat khas diucapkan narator saat tokoh muncul atau menang.
- Versi panjang per tokoh (kompilasi / turnamen / "hari Rocky").
- Tokoh baru terjadwal, misalnya 1 tokoh per 10 video.
