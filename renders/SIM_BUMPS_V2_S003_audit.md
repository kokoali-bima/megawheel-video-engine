# Audit otomatis: SIM_BUMPS_V2_S003

- Tanggal: 2026-09-30 05:11 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 3 · Track: bumps_d3de3b02
- Mengacu: `/root/sim-prototype/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->53.6 m, 3.0->59.6 m, 3.0->93.5 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 4 polisi tidur (41-78 m), finish 88 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 8.0s, 7.4s, 8.5s |
| Level gagal di rintangan berbeda | ✅ | rintangan [1, 2] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 48.0 s |
| Level gagal <= 18 s, level menang (+outro) <= 27 s | ✅ | 12.8s, 13.2s, 21.9s |
| Sidik jari belum ada di registry | ✅ | bumps|f1,icecream,monster2|bumps_d3de3b02|stuck@obs1,stuck@obs2,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/SIM_BUMPS_V2_S003.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 47.97 s (manifest 47.97) |
| Ukuran wajar (8-20 MB) | ✅ | 11.7 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.4 dB |
| mean_volume -20..-12 dB | ✅ | -13.6 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 7 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 9.3s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 13.4s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 22.5s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 26.6s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 36.8s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 67% piksel panel @ 47.2s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | bumps|f1,icecream,monster2|bumps_d3de3b02|stuck@obs1,stuck@obs2,win |
| Seed belum dipakai video lain | ✅ | seed 3 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video bumps berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
