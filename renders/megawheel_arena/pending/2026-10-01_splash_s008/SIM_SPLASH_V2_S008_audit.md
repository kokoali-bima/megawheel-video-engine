# Audit otomatis: SIM_SPLASH_V2_S008

- Tanggal: 2026-10-01 02:08 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 8 · Track: splash_eedbcd73
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->55.5 m, 3.0->63.0 m, 3.0->118.1 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [wall, pit, hill] (15-94 m), finish 98 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 8.6s, 9.1s, 9.5s |
| Level gagal di rintangan berbeda | ⚠️ | rintangan [1, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 48.1 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 14.8s, 12.4s, 20.8s |
| Sidik jari belum ada di registry | ✅ | splash|f1,bigrig,firetruck|splash_eedbcd73@morning-clear-desert|pit@obs1,stuck@obs1,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-01_splash_s008/SIM_SPLASH_V2_S008.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 48.07 s (manifest 48.07) |
| Ukuran wajar (8-20 MB) | ✅ | 12.8 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -13.2 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 7 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 11.0s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 15.4s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 24.3s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 27.8s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 39.1s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 70% piksel panel @ 47.3s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 12 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | splash|f1,bigrig,firetruck|splash_eedbcd73@morning-clear-desert|pit@obs1,stuck@obs1,win |
| Seed belum dipakai video lain | ✅ | seed 8 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video splash berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
