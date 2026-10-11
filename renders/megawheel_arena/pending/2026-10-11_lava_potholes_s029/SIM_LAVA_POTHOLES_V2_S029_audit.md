# Audit otomatis: SIM_LAVA_POTHOLES_V2_S029

- Tanggal: 2026-10-11 07:39 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 29 · Track: lava_potholes_7c7078a6
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->63.6 m, 3.0->66.1 m, 3.0->111.8 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 2 rintangan [pit, pit] (34-70 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 8.7s, 8.9s, 11.7s |
| Level gagal di rintangan berbeda | ⚠️ | rintangan [1, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 55.3 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 14.5s, 18.6s, 22.3s |
| Sidik jari belum ada di registry | ✅ | lava_potholes|taxi,bus,icecream|lava_potholes_7c7078a6@sunset-clear-volcano|pit@obs1,rollback@obs1+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-11_lava_potholes_s029/SIM_LAVA_POTHOLES_V2_S029.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 58.33 s (manifest 58.33) |
| Ukuran wajar (8-20 MB) | ✅ | 14.9 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -13.7 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 15.3s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 18.1s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 29.8s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 36.6s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 50.2s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 57.5s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | lava_potholes|taxi,bus,icecream|lava_potholes_7c7078a6@sunset-clear-volcano|pit@obs1,rollback@obs1+broken,win |
| Seed belum dipakai video lain | ✅ | seed 29 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video lava_potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
