# Audit otomatis: SIM_POTHOLES_V2_S022

- Tanggal: 2026-10-03 15:57 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 + godot3d (lab/godot3d_challenge) · Seed: 22 · Track: potholes_af8a2b00
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: GAGAL** → JANGAN dikirim ke user. Perbaiki / render seed lain.


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->74.5 m, 3.0->27.4 m, 3.0->125.6 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, pit, pit] (26-77 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 5.8s, 4.9s, 9.8s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 46.5 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 14.6s, 10.3s, 21.6s |
| Sidik jari belum ada di registry | ✅ | potholes|taxi,icecream,firetruck|potholes_af8a2b00@night-clear-mountains|rollback@obs2+broken,stuck@obs0,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-03_potholes_s022/SIM_POTHOLES_V2_S022.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-59.5 s (58 + cold open 1.5) dan sama dengan manifest (±0.3 s) | ✅ | 47.97 s (manifest 47.97) |
| Ukuran wajar (8-20 MB) | ✅ | 19.7 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -1.5 dB |
| mean_volume -20..-12 dB | ✅ | -13.2 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 2.1s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 10.0s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 16.7s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 24.0s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 26.9s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 39.1s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 40% piksel panel @ 47.2s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ❌ | 12 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | potholes|taxi,icecream,firetruck|potholes_af8a2b00@night-clear-mountains|rollback@obs2+broken,stuck@obs0,win |
| Seed belum dipakai video lain | ✅ | seed 22 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
