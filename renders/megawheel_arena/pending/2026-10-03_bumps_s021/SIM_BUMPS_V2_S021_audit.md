# Audit otomatis: SIM_BUMPS_V2_S021

- Tanggal: 2026-10-03 16:52 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 + godot3d (lab/godot3d_challenge) · Seed: 21 · Track: bumps_75aba530
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->61.9 m, 3.0->59.8 m, 3.0->116.7 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 4 rintangan [bump, bump, bump, bump] (43-79 m), finish 89 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 4.8s, 4.7s, 12.6s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 47.8 s |
| Level gagal <= 18 s, level menang (+outro) <= 27 s | ✅ | 13.3s, 10.1s, 24.5s |
| Sidik jari belum ada di registry | ✅ | bumps|sports,bus,monster|bumps_75aba530@sunset-rain-beach|flip@obs2,flip@obs1+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-03_bumps_s021/SIM_BUMPS_V2_S021.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-59.5 s (58 + cold open 1.5) dan sama dengan manifest (±0.3 s) | ✅ | 49.33 s (manifest 49.33) |
| Ukuran wajar (8-20 MB) | ⚠️ | 20.5 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -1.4 dB |
| mean_volume -20..-12 dB | ✅ | -13.1 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 2.1s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 9.1s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 15.4s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 22.5s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 25.5s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 40.7s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 67% piksel panel @ 48.5s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | bumps|sports,bus,monster|bumps_75aba530@sunset-rain-beach|flip@obs2,flip@obs1+broken,win |
| Seed belum dipakai video lain | ✅ | seed 21 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video bumps berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
