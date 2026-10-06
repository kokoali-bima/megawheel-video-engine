# SOP story3d — video cerita panjang (opsi C: dunia Godot 3D + tokoh asli story25d, render Modal)

> Disetujui user 2026-10-06 ("lanjut opsi C ... pakai modal.com agar lebih cepat"; "buatkan mesin ini bener2 siap
> otomasi sehingga agen mana pun yang menjalankan hasil generatenya mirip2"). Berlaku untuk S01E02 dan seterusnya.
> Shorts (CHALLENGE / RACE / SMASH) TIDAK memakai ini — tetap engine 2.5D.

## 0. Wajib dibaca dulu
BLUEPRINT, CONFIG_BEST, PRODUCTION_STANDARD, CHARACTERS.md, ERROR_LOG, QA_DEFECT_TRACKER, naskah episode
(`stories/<ep>/script.md`, harus sudah disetujui user), file ini.

## 1. Satu perintah baku (di VM 99.3)
```
cd /root/video-engine && bash git_sync.sh pull
venv/bin/python generators/story3d/produce_story3d.py --episode <ep> --scenes 2,3,4 [--upload]
```
| Exit | Arti | Tindakan |
|---|---|---|
| 0 | selesai, QA PASS/WARN | baca laporan QA; WARN boleh lanjut tapi catat |
| 2 | preflight (kode VM ≠ GitHub, file scene rusak) | `git_sync.sh pull` / perbaiki JSON |
| 3 | suara belum siap | cek log Chatterbox (QA ucapan), ulangi |
| 4 | render Modal gagal | baca log overlay/world; jangan render di VM sebagai gantinya |
| 5 | QA FAIL | perbaiki sesuai §5, jalankan lagi. **Jangan pernah unggah FAIL** |

Hasil: `work/story3d/<ep>/<ep>_scene_NN.mp4`, `..._qa.json`, `QA_<job>.md`. `--upload` → Drive
`ipandu-video/story3d/<ep>/` untuk review user. Biaya tercatat otomatis di `modal_usage.json` (budget $29/bulan).

## 2. Arsitektur (jangan diubah tanpa persetujuan user)
1. **prepare (VM sebagai pengendali)** — semua kalimat → Chatterbox (Modal GPU, cache + QA speech-recognition).
   Lip-sync dibuat di container Modal (rhubarb x86 1.13.0, versi sama dengan build VM; cache di volume Modal
   `/vol/visemes`) — keputusan user 2026-10-06, ±$0,01/episode. VM tidak perlu x86.
2. **overlay (Modal CPU)** — story25d menggambar tokoh, wajah, mulut, subtitle, caption, letterbox persis seperti
   yang tayang; dunia dihapus; kamera cairo per frame dicatat (`frames.json`).
3. **world (Modal T4)** — Godot 4.4.1 Forward+ menggambar dunia dari matriks kamera tiap frame (bagian 450 frame paralel).
4. **compose (Modal CPU)** — dunia + overlay + audio, loudnorm -16 LUFS, lalu sensor QA.
Repo di-mount di `/root/video-engine` dalam container (path sama dengan VM). Font Luckiest Guy wajib (gate).

## 3. Aturan menulis scene JSON (agar hasil konsisten)
- **Tokoh tidak pernah digambar ulang di 3D.** Dunia saja yang 3D.
- **Variasi gambar** (sensor `variasi`): ≥3 ukuran shot per scene (wide / medium / close / ecu / low / two / track);
  maks 2 ukuran sama berturut-turut; ≥2 jenis gerak kamera (`push`, `pull`, `pan`, `crane`, `dutch`, `handheld`);
  shot >7 dtk wajib ada gerak kamera atau mobil bergerak. Kait akhir scene: `push`/`low`/`punch`.
- **Musik = spotting, bukan karpet** (user 05-10): `score` per rentang shot dari pustaka cue
  (`branding/music/cues_<ep>.json`). Satu scene >40 dtk tidak boleh satu cue saja dari awal sampai akhir. Bagian
  sunyi dibawa ambience + efek. Musik seram hanya saat bukti/ancaman terlihat. Lagu tokoh = baris nyanyi
  (`[spk, text, emo, wav, cut, pre, [page times]]`, suara asli tokoh via Seed-VC), teks dipisah `|` per frasa.
- **Efek suara harus terdengar di HP**: energi utama 200–4000 Hz (sensor `phone_band`). Langkah raksasa =
  `steps_far`/`stomp_near` (boom + retak), bukan hanya sub-bass. Klakson = `honk`.
- **Ambience**: kota malam = `city_night` (tanpa jangkrik); pedesaan/hutan malam = `night` (jangkrik pelan);
  siang = `birds`. Tidak boleh ada desis >3 kHz di bagian sepi (sensor `hiss`).
- **Cahaya**: malam = tanpa bayangan gedung (bulan tanpa shadow), cahaya dari lampu jalan + lampu sorot mobil;
  siang = matahari di belakang kamera, bayangan lembut (opacity 0.55) jatuh ke belakang objek.
- **Objek kejutan** (Kraggor jauh, mata) hanya muncul di shot-nya (`kraggor_far` per shot; Godot menyembunyikan di
  frame lain). Prop yang muncul belakangan pakai `from_shot` / `to_shot`.
- Mobil selalu di pita jalan z −0.6…3.2, bayangan kontak aktif (`contact_shadow` jangan dimatikan).
- Jejak kaki: `footprints` rebah sejajar jalan (`size` 1.0 = 5.5 × 3 m), selang-seling (`stagger`).

## 4. Sensor QA (generators/story3d/audit_story3d.py) — ambang tetap di `THRESH`
| Sensor | Mengukur | FAIL / WARN |
|---|---|---|
| roll/proyeksi | selisih proyeksi Godot vs cairo untuk titik jalan | FAIL > 2 px (jalan miring / mobil melayang) |
| grounding | mobil di pita jalan; contact shadow | WARN |
| kamera | kecepatan & sentakan jangkar dunia dalam satu shot | FAIL > 70 px/frame (kecuali `whip`), WARN sentakan > 22 |
| lompatan | lonjakan beda-frame > 5× median shot | WARN |
| framing | tokoh fokus/pembicara terlihat ≥80%, tidak tertutup mobil lain >30%, tidak di bawah subtitle >35% | FAIL tertutup, WARN lain |
| variasi | ukuran shot, gerak kamera, shot diam lama | WARN |
| cahaya | luma per shot 28–215, kontras tokoh vs latar ≥1.35, bayangan gelap di jalan ≤22% (siang) | WARN |
| audio | desis di bagian sepi, sunyi total ≥1.6 dtk, musik/efek menutupi suara (<6 dB), efek tak terdengar di HP, musik monoton, LUFS -17.5…-14.5 | FAIL desis, WARN lain |
| reveal | titik kuning (mata) sebelum shot Kraggor | WARN |

Mengubah ambang = keputusan user (catat di QA_DEFECT_TRACKER).

## 5. Buku perbaikan (sensor → apa yang diubah)
- **roll/proyeksi FAIL** → rumus kamera di `project/story3d.gd _process()` dan `audit_story3d.godot_px` harus identik
  (keduanya dikunci bersama). Jangan "membetulkan" satu sisi saja.
- **kamera FAIL** → kurangi `pan`/`push` atau perpanjang shot; tandai `"move": {"whip": true}` hanya jika memang
  whip-pan yang disengaja (dengan whoosh).
- **framing tertutup** → geser `x`/`z` aktor (yang lebih dekat kamera = z lebih kecil menutupi), atau ganti `cam`.
- **subtitle menutupi** → `cam` lebih rapat (close) atau `lift` kamera.
- **desis** → jangan pakai noise mentah; semua noise lewat `fft_band(...)` < 1 kHz untuk latar.
- **musik menutupi suara** → turunkan `vol` cue di rentang itu atau pindahkan cue keluar dari kalimat penting.
- **efek tak terdengar di HP** → tambah lapisan 200–4000 Hz (lihat `phone_step`, `honk`).
- **variasi** → tambah gerak kamera / ganti ukuran shot sesuai §3.
- **cahaya gelap** → malam: dekatkan lampu jalan / lampu sorot; siang: `tonemap_exposure`.

## 6. Konsistensi antar agen
- Versi terkunci: Godot 4.4.1, Python 3.12 container, font Luckiest Guy dari VM, cue & suara dari cache repo.
- Dunia Godot memakai seed tetap (`rng.seed = 5`): kota yang sama setiap render.
- Jangan render tokoh/dunia di luar pipeline ini; jangan menyunting mp4 hasil secara manual.
- Setiap temuan baru dari review user → tambahkan sensor + baris di QA_DEFECT_TRACKER, lalu perbarui SOP ini.
