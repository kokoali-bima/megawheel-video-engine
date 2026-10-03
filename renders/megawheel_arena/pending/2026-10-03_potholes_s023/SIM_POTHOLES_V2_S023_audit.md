# Audit otomatis: SIM_POTHOLES_V2_S023

- Tanggal: 2026-10-03 05:15 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 23 · Track: potholes_87f344a7
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: GAGAL** → JANGAN dikirim ke user. Perbaiki / render seed lain.


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->78.2 m, 3.0->28.9 m, 3.0->126.0 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, pit, pit] (28-82 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 8.2s, 5.9s, 10.1s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 50.5 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 17.3s, 10.8s, 22.3s |
| Sidik jari belum ada di registry | ✅ | potholes|taxi,icecream,firetruck|potholes_87f344a7@night-clear-mountains|rollback@obs2+broken,stuck@obs0,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-03_potholes_s023/SIM_POTHOLES_V2_S023.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-58 s dan sama dengan manifest (±0.3 s) | ❌ | 51.97 s (manifest 50.47) |
| Ukuran wajar (8-20 MB) | ✅ | 11.3 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -14.8 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ❌ | 0% piksel badge @ 10.9s |
| L2: badge LEVEL 2 tampil di awal level | ❌ | 0% piksel warna level @ 17.9s |
| L2: badge FAIL tampil tepat di event | ❌ | 0% piksel badge @ 25.9s |
| L3: badge LEVEL 3 tampil di awal level | ❌ | 0% piksel warna level @ 28.8s |
| L3: badge WINNER tampil tepat di event | ❌ | 0% piksel badge @ 41.6s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 66% piksel panel @ 51.2s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | potholes|taxi,icecream,firetruck|potholes_87f344a7@night-clear-mountains|rollback@obs2+broken,stuck@obs0,win |
| Seed belum dipakai video lain | ✅ | seed 23 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
