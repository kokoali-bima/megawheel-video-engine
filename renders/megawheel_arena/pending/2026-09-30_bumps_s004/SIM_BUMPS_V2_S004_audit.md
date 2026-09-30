# Audit otomatis: SIM_BUMPS_V2_S004

- Tanggal: 2026-09-30 07:36 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 4 · Track: bumps_085ce19c
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->65.2 m, 3.0->60.5 m, 3.0->113.6 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 4 polisi tidur (43-80 m), finish 90 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 5.8s, 4.6s, 13.1s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 48.0 s |
| Level gagal <= 18 s, level menang (+outro) <= 27 s | ✅ | 11.6s, 12.1s, 24.3s |
| Sidik jari belum ada di registry | ✅ | bumps|police,firetruck,monster2|bumps_085ce19c|stuck@obs2,flip@obs1+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-09-30_bumps_s004/SIM_BUMPS_V2_S004.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 48.00 s (manifest 48.0) |
| Ukuran wajar (8-20 MB) | ✅ | 12.1 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -13.6 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 8.8s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 12.2s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 17.8s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 24.3s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 38.7s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 65% piksel panel @ 47.2s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | bumps|police,firetruck,monster2|bumps_085ce19c|stuck@obs2,flip@obs1+broken,win |
| Seed belum dipakai video lain | ✅ | seed 4 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video bumps berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
