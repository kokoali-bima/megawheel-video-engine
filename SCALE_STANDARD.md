# SCALE_STANDARD — ukuran baku dunia, mobil, arena, dan layar

> Permintaan user 2026-10-03: "harus ada standar semua ukuran, jadinya ga menebak-nebak".
> Berlaku untuk semua mesin (cairo 2.5D dan Godot 3D). Kalau sebuah angka di sini berubah, ubah juga
> `CONFIG_BEST.md` dan catat alasannya. Angka yang **terukur** diambil dari kode/render, bukan perkiraan.

## 1. Satuan
- **1 unit dunia = 1 meter** (cairo: x/z dalam meter; Godot: 1 unit = 1 m).
- Layar: **1080 × 1920 px (9:16), 30 fps**.
- Sprite mobil: **60 px gambar = 1 m** (`pixel_size = 1/60` di Godot; `export_sprites.py` dari cast cairo).

## 2. Ukuran mobil (sumber: `cast.json`, dari cast cairo; jangan diubah per mesin)
| Kunci | Nama | Panjang bodi (m) | Tinggi bodi (m) | Jari-jari roda (m) | Ride (m) |
|---|---|---|---|---|---|
| sports | Zippy | 4.2 | 0.62 | 0.42 | 1.00 |
| police | Siren | 4.4 | 0.70 | 0.43 | 1.05 |
| taxi | Tilly | 4.3 | 0.70 | 0.42 | 1.04 |
| f1 | Nitro | 4.6 | 0.45 | 0.36 | 0.77 |
| monster | Rocky | 4.3 | 0.90 | 1.00 | 2.05 |
| monster2 | Grizzly | 4.3 | 0.90 | 1.00 | 2.05 |
| icecream | Sprinkles | 5.6 | 2.20 | 0.50 | 1.81 |
| firetruck | Hydro | 6.4 | 1.90 | 0.60 | 1.76 |
| bus | Buster | 7.4 | 2.10 | 0.55 | 1.81 |
| bigrig | Titan | 9.6 | 2.30 | 0.60 | 1.96 |

Props (Godot lab): hiu 8,7 m panjang (`pixel_size 1/110`, gambar 960 px), sirip 2,2 m, POW 2,6–3,6 m.

## 3. Arena
| Mesin | Lantai (lebar × dalam) | Skala layar terukur | Kamera |
|---|---|---|---|
| SMASH cairo `smash25d.py` (tayang) | **26 × 10 m**, menyusut ke 17 × 7,2 m (mulai 18 s, tiap 7 s) | k(z) = 6000/(100+8z): **60 px/m depan**, 33 px/m belakang, × zoom 1,0–1,45 | pan horizontal + zoom mengikuti mobil (arena lebih lebar dari layar) |
| **SMASH Godot 3D v4 "classic" (standar)** | **26 × 10 m** sama dengan cairo, platform baja di atas air (y air = −1,2 m), menyusut seperti cairo | **identik cairo: 60 px/m depan, 33,3 px/m belakang** × zoom 1,0–1,45 | kamera datar (tanpa miring) tinggi 20,4 m, 12,5 m di depan tepi arena, fokus 750 px × zoom, lensa digeser (horizon y = 1190 + (276−1190)·zoom + 20), pan + zoom mengikuti mobil |
| SMASH Godot 3D v3 "topdown" (alternatif, `cam=topdown`) | 20 × 24 m | 50 px/m depan, 35 px/m belakang | statis (0, 30, −8) → (0, 0, 11,5), fov 40°, kartu miring 0,5 rad |

Kamera klasik memakai rumus proyeksi smash25d persis, jadi sudut pandang, letak horizon, ukuran mobil, dan tribun
(sepertiga atas layar) sama dengan versi tayang. Karena kameranya datar, kartu mobil tetap tegak tanpa dimiringkan.
Catatan teknis Godot 4.4: pada `PROJECTION_FRUSTUM` + `KEEP_WIDTH`, render memakai `size` sebagai lebar, tetapi
`unproject_position()` menganggapnya tinggi (selisih 1,78×). Karena itu proyeksi layar dihitung sendiri (`_proj()`).

## 4. Zona layar (px, 1080 × 1920) — berlaku semua format
| Zona | y (px) | Isi |
|---|---|---|
| Judul | 90–230 | "SMASH ARENA!" |
| Panel HP | x 26–416, y 214–480 | 4 baris HP |
| Tepi belakang arena | **520–640** | di bawah panel HP |
| Banner pemenang | 560–740 | "X WINS!" |
| End card | 820–1150 | kartu putih |
| Tepi depan arena | **1380–1480** | di atas UI Shorts |
| Subjudul | 1480–1600 | intro saja |
| UI Shorts (tombol, caption) | 1600–1920 dan x > 960 | **jangan taruh aksi penting** |

## 5. Toleransi dan cara cek (otomatis)
`lab/godot3d_smash/run.sh` mencetak baris `SCALE {...}` dari `smash3d.gd` (`_scale_report()`) dan menyimpannya
ke `/root/lab/smash3d/scale_<tag>.json`. Render dianggap **lolos standar** bila (pada zoom 1):
- classic: `front_px_per_m` = 60 ± 1, `back_px_per_m` = 33,3 ± 1, `front_y` 1520 ± 10, `back_y` 976 ± 10
- topdown: `front_px_per_m` = 50 ± 4, `back_px_per_m` ≥ 32, `front_x` di dalam [20, 1060], `front_y` 1380–1480, `back_y` 520–640

Terukur 2026-10-03: classic 60,0 / 33,3 px/m, front_y 1520, back_y 976 ✅ · topdown 50,3 / 34,8 px/m, front_y 1445, back_y 595 ✅

## 6. Logika menang SMASH (sama di cairo dan 3D)
- HP 100. Damage dari tabrakan (kecepatan relatif × rasio massa), ledakan, dan injakan.
- **0–9 dtk: barrier ban.** Mobil memantul di tepi, belum ada eliminasi.
- **Setelah 9 dtk:** mobil hanya bisa jatuh dari arena kalau **didorong** (< 0,8 dtk sejak tabrakan atau ledakan).
  Kalau tidak didorong, mobil berhenti di tepi lalu kembali masuk.
- KO = HP habis (hancur) atau jatuh ke luar arena (cairo: lava/lumpur/air; 3D: air, lalu dimakan hiu).
- **Lantai menyusut** mulai 18 dtk, tiap 7 dtk 12% (menyusut sampai 65% × 72%).
- Mobil terakhir yang masih bertahan **selalu selamat**.
- **Batas waktu:** HP terbanyak menang. Cairo 40 dtk; 3D 27 dtk karena video 30–40 dtk.
- Tambahan 3D (user 2026-10-03): jarak antar-KO minimal 4,5 dtk, dan satu kejadian tidak boleh menghabisi beberapa mobil.
- Chaos dengan ritme cairo (sekitar 5 / 10 / 15 / 20 dtk), satu tema per video. "Lempar ke tepi" hanya untuk mobil dengan HP < 60.
