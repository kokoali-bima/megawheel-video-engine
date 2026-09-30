# Audit otomatis: SIM_SPLASH_V2_S007

- Tanggal: 2026-09-30 10:11 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 7 · Track: splash_1ddda902
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->35.1 m, 3.0->62.1 m, 3.0->125.5 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, wall, hill] (18-99 m), finish 106 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 6.2s, 9.2s, 13.7s |
| Level gagal di rintangan berbeda | ✅ | rintangan [0, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 48.4 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 11.5s, 13.5s, 23.4s |
| Sidik jari belum ada di registry | ✅ | splash|taxi,icecream,bigrig|splash_1ddda902@night-clear-desert|pit@obs0,stuck@obs1,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-09-30_splash_s007/SIM_SPLASH_V2_S007.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 48.40 s (manifest 48.4) |
| Ukuran wajar (8-20 MB) | ✅ | 11.8 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -13.1 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 7 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 8.5s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 12.1s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 21.7s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 25.6s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 39.7s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 70% piksel panel @ 47.6s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | splash|taxi,icecream,bigrig|splash_1ddda902@night-clear-desert|pit@obs0,stuck@obs1,win |
| Seed belum dipakai video lain | ✅ | seed 7 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video splash berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
