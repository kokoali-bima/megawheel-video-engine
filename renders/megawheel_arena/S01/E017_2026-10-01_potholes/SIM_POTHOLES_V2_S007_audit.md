# Audit otomatis: SIM_POTHOLES_V2_S007

- Tanggal: 2026-10-01 09:14 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 7 · Track: potholes_7b93fb9e
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->72.3 m, 3.0->27.7 m, 3.0->125.4 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, pit, pit] (26-74 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 7.2s, 5.8s, 8.4s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 49.3 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 17.7s, 12.0s, 19.6s |
| Sidik jari belum ada di registry | ✅ | potholes|sports,icecream,bus|potholes_7b93fb9e@sunset-clear-mountains|pit@obs2+broken,stuck@obs0,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S01/E017_2026-10-01_potholes/SIM_POTHOLES_V2_S007.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-58 s dan sama dengan manifest (±0.3 s) | ✅ | 49.33 s (manifest 49.33) |
| Ukuran wajar (8-20 MB) | ✅ | 11.0 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -14.2 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 11.4s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 18.3s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 27.4s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 30.3s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 41.0s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 48.5s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | potholes|sports,icecream,bus|potholes_7b93fb9e@sunset-clear-mountains|pit@obs2+broken,stuck@obs0,win |
| Seed belum dipakai video lain | ✅ | seed 7 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
