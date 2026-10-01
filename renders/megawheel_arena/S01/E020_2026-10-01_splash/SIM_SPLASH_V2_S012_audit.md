# Audit otomatis: SIM_SPLASH_V2_S012

- Tanggal: 2026-10-01 09:29 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 12 · Track: splash_faddff76
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->87.0 m, 3.0->35.6 m, 3.0->128.6 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, hill, wall] (17-91 m), finish 95 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 7.4s, 6.2s, 8.0s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 48.9 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 17.2s, 11.6s, 20.0s |
| Sidik jari belum ada di registry | ✅ | splash|f1,icecream,taxi|splash_faddff76@noon-clear-city|flip@obs2,pit@obs0+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S01/E020_2026-10-01_splash/SIM_SPLASH_V2_S012.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-58 s dan sama dengan manifest (±0.3 s) | ✅ | 48.90 s (manifest 48.9) |
| Ukuran wajar (8-20 MB) | ✅ | 13.8 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.4 dB |
| mean_volume -20..-12 dB | ✅ | -14.1 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 11.5s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 17.8s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 26.1s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 29.5s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 40.7s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 48.1s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 15 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | splash|f1,icecream,taxi|splash_faddff76@noon-clear-city|flip@obs2,pit@obs0+broken,win |
| Seed belum dipakai video lain | ✅ | seed 12 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video splash berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
