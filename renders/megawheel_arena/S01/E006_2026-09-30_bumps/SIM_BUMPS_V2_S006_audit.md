# Audit otomatis: SIM_BUMPS_V2_S006

- Tanggal: 2026-09-30 08:28 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 6 · Track: bumps_a1184bfc
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->73.5 m, 3.0->58.7 m, 3.0->104.4 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 4 polisi tidur (44-80 m), finish 90 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 5.4s, 4.3s, 9.0s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 47.3 s |
| Level gagal <= 18 s, level menang (+outro) <= 27 s | ✅ | 14.6s, 11.9s, 20.8s |
| Sidik jari belum ada di registry | ✅ | bumps|police,bus,monster|bumps_a1184bfc@sunset-clear-countryside|flip@obs2+broken,flip@obs1+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S01/E006_2026-09-30_bumps/SIM_BUMPS_V2_S006.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 47.27 s (manifest 47.27) |
| Ukuran wajar (8-20 MB) | ✅ | 13.6 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.4 dB |
| mean_volume -20..-12 dB | ✅ | -13.5 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 8.4s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 15.2s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 20.5s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 27.1s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 38.1s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 65% piksel panel @ 46.5s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 15 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | bumps|police,bus,monster|bumps_a1184bfc@sunset-clear-countryside|flip@obs2+broken,flip@obs1+broken,win |
| Seed belum dipakai video lain | ✅ | seed 6 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video bumps berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
