# Audit otomatis: SIM_POTHOLES_V2_S029

- Tanggal: 2026-10-04 01:46 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 29 · Track: potholes_0f457e95
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->47.0 m, 3.0->39.8 m, 3.0->146.5 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, pit, pit] (39-78 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 5.7s, 5.0s, 9.0s |
| Level gagal di rintangan berbeda | ⚠️ | rintangan [0, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 48.5 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 17.3s, 10.3s, 20.9s |
| Sidik jari belum ada di registry | ✅ | potholes|police,bigrig,f1|potholes_0f457e95@sunset-clear-beach|flip@obs0,stuck@obs0,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S02/E051_2026-10-04_potholes/SIM_POTHOLES_V2_S029.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-59.5 s (58 + cold open 1.5) dan sama dengan manifest (±0.3 s) | ✅ | 50.00 s (manifest 50.0) |
| Ukuran wajar (8-20 MB) | ✅ | 12.4 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -15.3 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 2.1s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 12.5s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 19.4s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 26.7s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 29.7s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 41.1s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 66% piksel panel @ 49.2s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | potholes|police,bigrig,f1|potholes_0f457e95@sunset-clear-beach|flip@obs0,stuck@obs0,win |
| Seed belum dipakai video lain | ✅ | seed 29 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
