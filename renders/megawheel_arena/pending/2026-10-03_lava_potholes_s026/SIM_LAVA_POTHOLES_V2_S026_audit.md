# Audit otomatis: SIM_LAVA_POTHOLES_V2_S026

- Tanggal: 2026-10-03 08:27 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 26 · Track: lava_potholes_52feb935
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->78.9 m, 3.0->25.8 m, 3.0->144.8 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, pit, pit] (26-81 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 7.9s, 4.4s, 7.9s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 45.3 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 17.6s, 8.5s, 19.1s |
| Sidik jari belum ada di registry | ✅ | lava_potholes|police,bigrig,f1|lava_potholes_52feb935@morning-clear-volcano|rollback@obs2+broken,stuck@obs0,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-03_lava_potholes_s026/SIM_LAVA_POTHOLES_V2_S026.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-59.5 s (58 + cold open 1.5) dan sama dengan manifest (±0.3 s) | ✅ | 46.77 s (manifest 46.77) |
| Ukuran wajar (8-20 MB) | ✅ | 17.9 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -1.3 dB |
| mean_volume -20..-12 dB | ✅ | -13.8 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 2.1s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 13.1s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 19.7s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 25.1s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 28.3s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 38.8s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 67% piksel panel @ 46.0s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | lava_potholes|police,bigrig,f1|lava_potholes_52feb935@morning-clear-volcano|rollback@obs2+broken,stuck@obs0,win |
| Seed belum dipakai video lain | ✅ | seed 26 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video lava_potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
