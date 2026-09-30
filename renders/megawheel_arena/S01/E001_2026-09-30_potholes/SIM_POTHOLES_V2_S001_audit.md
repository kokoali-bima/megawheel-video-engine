# Audit otomatis: SIM_POTHOLES_V2_S001

- Tanggal: 2026-09-30 08:22 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 1 · Track: potholes_std
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->80.7 m, 3.0->30.4 m, 3.0->135.9 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 lubang (30-83 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 7.9s, 6.3s, 7.9s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 44.6 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 16.8s, 9.6s, 18.3s |
| Sidik jari belum ada di registry | ✅ | potholes|sports,bus,monster|potholes_std@sunset-clear-beach|pit@obs2+broken,stuck@obs0,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S01/E001_2026-09-30_potholes/SIM_POTHOLES_V2_S001.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 44.63 s (manifest 44.63) |
| Ukuran wajar (8-20 MB) | ✅ | 12.5 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -12.4 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 10.5s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 17.4s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 24.0s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 27.0s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 35.9s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 43.8s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | potholes|sports,bus,monster|potholes_std@sunset-clear-beach|pit@obs2+broken,stuck@obs0,win |
| Seed belum dipakai video lain | ✅ | seed 1 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
