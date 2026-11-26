# Audit otomatis: SIM_DUNGEON_V2_S039

- Tanggal: 2026-11-17 01:55 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 + godot3d (lab/godot3d_challenge) · Seed: 39 · Track: dungeon_bda59df6
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: GAGAL** → JANGAN dikirim ke user. Perbaiki / render seed lain.


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->55.4 m, 3.0->56.0 m, 3.0->106.9 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 5 rintangan [axe, ogre, lava, axe, axe] (18-85 m), finish 94 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 3.7s, 8.7s, 11.4s |
| Level gagal di rintangan berbeda | ✅ | rintangan [1, 2] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 47.8 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 7.6s, 18.1s, 22.1s |
| Sidik jari belum ada di registry | ✅ | dungeon|sports,firetruck,monster|dungeon_bda59df6@night-clear-volcano|smash@obs1+broken,rollback@obs2+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S07/E181_2026-11-16_dungeon/SIM_DUNGEON_V2_S039.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 50.80 s (manifest 50.8) |
| Ukuran wajar (8-35 MB) | ⚠️ | 37.6 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -1.3 dB |
| mean_volume -20..-12 dB | ✅ | -12.4 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 7.8s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 11.2s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 22.1s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 29.3s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 42.1s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ❌ | 29% piksel panel @ 50.0s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | dungeon|sports,firetruck,monster|dungeon_bda59df6@night-clear-volcano|smash@obs1+broken,rollback@obs2+broken,win |
| Seed belum dipakai video lain | ✅ | seed 39 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video dungeon berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
