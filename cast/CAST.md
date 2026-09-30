# MegaWheel Kids — Cast Bible (tokoh tetap)

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

## Aturan penokohan (wajib untuk semua agent)

1. **Nama, warna, dan sifat tokoh TIDAK boleh diubah** tanpa persetujuan user. Penonton mengenali tokoh dari nama dan warnanya.
2. **Tokoh tidak dibuat otomatis per video.** Tokoh baru hanya ditambah dengan sengaja sebagai "episode debut", lalu dicatat di `characters.json` dan tabel di atas.
3. **Rotasi adil (otomatis):** untuk setiap peran, engine memilih tokoh yang paling jarang tampil (dihitung dari `PRODUCTION_REGISTRY.json`). Kalau jumlahnya sama, seed yang menentukan.
4. **Cek nama baru** sebelum dipakai: jangan sama dengan tokoh kartun/brand terkenal (contoh: "Blaze" dan "Crusher" diganti karena sama dengan serial *Blaze and the Monster Machines*).
5. Peran menentukan fisika: `light` / `heavy` = biasanya gagal, `champion` = biasanya menang. Cerita underdog (tokoh berat menang) butuh lintasan khusus → roadmap.

## Riwayat
- 2026-09-30: 6 tokoh ditetapkan. "Blaze" → **Hydro**, "Crusher" → **Grizzly** (sebelum pernah dirender/diupload).

## Ide ke depan
- Statistik per tokoh (tampil / menang / gagal) dari registry → konten "Siapa juara terbanyak?".
- Kalimat khas diucapkan narator saat tokoh muncul atau menang.
- Versi panjang per tokoh (kompilasi / turnamen / "hari Rocky").
- Tokoh baru terjadwal, misalnya 1 tokoh per 10 video.
