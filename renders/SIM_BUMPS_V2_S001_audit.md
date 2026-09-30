# Audit otomatis: SIM_BUMPS_V2_S001

- Tanggal: 2026-09-30 03:17 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 1 · Track: bumps_a3f04e8b
- Mengacu: `/root/sim-prototype/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->60.2 m, 3.0->50.2 m, 3.0->121.7 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 4 polisi tidur (42-80 m), finish 90 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 7.1s, 6.0s, 12.9s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 49.2 s |
| Level gagal <= 18 s, level menang (+outro) <= 27 s | ✅ | 12.2s, 11.0s, 25.9s |
| Sidik jari belum ada di registry | ✅ | bumps|police,firetruck,monster2|bumps_a3f04e8b|stuck@obs2,stuck@obs1,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/SIM_BUMPS_V2_S001.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 49.17 s (manifest 49.17) |
| Ukuran wajar (8-20 MB) | ✅ | 11.5 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -13.4 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 7 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 8.7s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 12.8s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 19.8s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 23.9s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 38.0s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 68% piksel panel @ 48.4s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | bumps|police,firetruck,monster2|bumps_a3f04e8b|stuck@obs2,stuck@obs1,win |
| Seed belum dipakai video lain | ✅ | seed 1 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 1 video bumps berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
