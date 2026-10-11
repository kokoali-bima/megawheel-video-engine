# Audit otomatis: SIM_PINBALL_V2_S004

- Tanggal: 2026-10-11 03:24 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 4 · Track: pinball_09e072b1
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->76.1 m, 3.0->25.6 m, 3.0->116.2 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 2 rintangan [lava, lava] (39-79 m), finish 98 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 7.8s, 3.9s, 12.1s |
| Level gagal di rintangan berbeda | ✅ | rintangan [1, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 56.9 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 16.5s, 13.0s, 27.4s |
| Sidik jari belum ada di registry | ✅ | pinball|f1,firetruck,icecream|pinball_09e072b1@noon-clear-volcano|pit@obs1+broken,rollback@obs0+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-11_pinball_s004/SIM_PINBALL_V2_S004.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 59.87 s (manifest 59.87) |
| Ukuran wajar (8-20 MB) | ✅ | 17.1 MB |

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
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 16.6s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 20.1s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 25.1s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 33.1s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 50.9s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 65% piksel panel @ 59.1s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | pinball|f1,firetruck,icecream|pinball_09e072b1@noon-clear-volcano|pit@obs1+broken,rollback@obs0+broken,win |
| Seed belum dipakai video lain | ✅ | seed 4 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video pinball berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
