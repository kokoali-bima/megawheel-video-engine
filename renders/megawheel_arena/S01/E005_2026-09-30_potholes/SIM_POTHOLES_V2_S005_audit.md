# Audit otomatis: SIM_POTHOLES_V2_S005

- Tanggal: 2026-09-30 08:27 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 5 · Track: potholes_d0311b71
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->81.7 m, 3.0->27.4 m, 3.0->124.0 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 lubang (26-79 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 7.6s, 5.6s, 9.2s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 47.8 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 16.4s, 10.6s, 20.8s |
| Sidik jari belum ada di registry | ✅ | potholes|sports,icecream,monster2|potholes_d0311b71@noon-rain-beach|flip@obs2+broken,stuck@obs0,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S01/E005_2026-09-30_potholes/SIM_POTHOLES_V2_S005.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 47.80 s (manifest 47.8) |
| Ukuran wajar (8-20 MB) | ⚠️ | 23.5 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.4 dB |
| mean_volume -20..-12 dB | ✅ | -13.9 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 10.2s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 17.0s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 23.9s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 27.6s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 37.9s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 47.0s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | potholes|sports,icecream,monster2|potholes_d0311b71@noon-rain-beach|flip@obs2+broken,stuck@obs0,win |
| Seed belum dipakai video lain | ✅ | seed 5 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
