# Audit otomatis: SIM_POTHOLES_V2_S025

- Tanggal: 2026-10-03 05:20 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 25 · Track: potholes_054ab746
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: GAGAL** → JANGAN dikirim ke user. Perbaiki / render seed lain.


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->79.3 m, 3.0->32.0 m, 3.0->134.9 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, pit, pit] (31-82 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 7.3s, 5.6s, 8.5s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 49.1 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 17.5s, 11.0s, 20.7s |
| Sidik jari belum ada di registry | ✅ | potholes|police,icecream,sports|potholes_054ab746@noon-clear-beach|rollback@obs2+broken,stuck@obs0,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-03_potholes_s025/SIM_POTHOLES_V2_S025.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-58 s dan sama dengan manifest (±0.3 s) | ❌ | 50.63 s (manifest 49.13) |
| Ukuran wajar (8-20 MB) | ✅ | 13.4 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -15.8 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ❌ | 0% piksel badge @ 10.5s |
| L2: badge LEVEL 2 tampil di awal level | ❌ | 0% piksel warna level @ 18.1s |
| L2: badge FAIL tampil tepat di event | ❌ | 0% piksel badge @ 26.2s |
| L3: badge LEVEL 3 tampil di awal level | ❌ | 0% piksel warna level @ 29.1s |
| L3: badge WINNER tampil tepat di event | ❌ | 0% piksel badge @ 40.3s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 66% piksel panel @ 49.8s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | potholes|police,icecream,sports|potholes_054ab746@noon-clear-beach|rollback@obs2+broken,stuck@obs0,win |
| Seed belum dipakai video lain | ✅ | seed 25 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
