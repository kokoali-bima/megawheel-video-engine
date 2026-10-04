# Audit otomatis: SIM_POTHOLES_V2_S028

- Tanggal: 2026-10-04 01:37 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 28 · Track: potholes_fbaf774a
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->38.6 m, 3.0->29.7 m, 3.0->113.5 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, pit, pit] (29-67 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 4.6s, 5.3s, 11.3s |
| Level gagal di rintangan berbeda | ⚠️ | rintangan [0, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 45.7 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 13.2s, 10.4s, 22.0s |
| Sidik jari belum ada di registry | ✅ | potholes|f1,firetruck,icecream|potholes_fbaf774a@morning-clear-countryside|pit@obs0+broken,stuck@obs0,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S02/E050_2026-10-04_potholes/SIM_POTHOLES_V2_S028.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-59.5 s (58 + cold open 1.5) dan sama dengan manifest (±0.3 s) | ✅ | 47.17 s (manifest 47.17) |
| Ukuran wajar (8-20 MB) | ✅ | 11.5 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -14.5 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 2.1s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 8.4s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 15.3s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 22.8s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 25.8s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 39.0s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 46.4s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | potholes|f1,firetruck,icecream|potholes_fbaf774a@morning-clear-countryside|pit@obs0+broken,stuck@obs0,win |
| Seed belum dipakai video lain | ✅ | seed 28 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
