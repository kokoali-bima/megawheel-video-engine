# Audit otomatis: SIM_SPLASH_V2_S005

- Tanggal: 2026-09-30 10:02 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 5 · Track: splash_813d65c1
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->62.3 m, 3.0->41.6 m, 3.0->126.4 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, wall, hill] (16-102 m), finish 110 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 5.7s, 6.1s, 13.0s |
| Level gagal di rintangan berbeda | ✅ | rintangan [1, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 48.7 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 13.9s, 9.9s, 25.0s |
| Sidik jari belum ada di registry | ✅ | splash|f1,bigrig,bus|splash_813d65c1@noon-clear-city|crash@obs1+broken,stuck@obs0,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/rejected/2026-09-30_splash_s005/SIM_SPLASH_V2_S005.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 48.73 s (manifest 48.73) |
| Ukuran wajar (8-20 MB) | ✅ | 14.5 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.4 dB |
| mean_volume -20..-12 dB | ✅ | -13.4 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 7.2s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 14.5s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 20.9s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 24.4s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 38.9s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 47.9s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | splash|f1,bigrig,bus|splash_813d65c1@noon-clear-city|crash@obs1+broken,stuck@obs0,win |
| Seed belum dipakai video lain | ✅ | seed 5 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video splash berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
