# Audit otomatis: SIM_POTHOLES_V2_S002

- Tanggal: 2026-09-30 03:16 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 2 · Track: potholes_dc6ea3dd
- Mengacu: `/root/sim-prototype/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->81.8 m, 3.0->75.8 m, 3.0->130.7 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 lubang, ramp 44.3-50.0 m, finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 7.8s, 8.5s, 8.3s |
| Level gagal di rintangan berbeda | ⚠️ | rintangan [2, 2] |
| Minimal 1 momen spektakuler (hancur/terbalik) | ✅ |  |
| Durasi total 40-50 s | ✅ | 48.9 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 15.2s, 12.8s, 20.8s |
| Sidik jari belum ada di registry | ✅ | potholes|sports,bus,monster|potholes_dc6ea3dd|flip@obs2+broken,stuck@obs2,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/SIM_POTHOLES_V2_S002.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 48.87 s (manifest 48.87) |
| Ukuran wajar (8-20 MB) | ✅ | 11.8 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -13.4 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 9.0s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 15.8s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 24.9s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 28.6s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 37.6s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 66% piksel panel @ 48.1s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | potholes|sports,bus,monster|potholes_dc6ea3dd|flip@obs2+broken,stuck@obs2,win |
| Seed belum dipakai video lain | ✅ | seed 2 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
