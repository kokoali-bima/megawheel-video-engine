# Audit otomatis: SIM_LAVA_V2_S021

- Tanggal: 2026-10-01 09:24 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 21 · Track: lava_1c06d976
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->38.1 m, 3.0->69.9 m, 3.0->121.9 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 5 rintangan [lava, vent, vent, lava, vent] (36-91 m), finish 101 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 5.5s, 5.0s, 9.6s |
| Level gagal di rintangan berbeda | ✅ | rintangan [0, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 46.1 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 12.2s, 13.6s, 20.2s |
| Sidik jari belum ada di registry | ✅ | lava|police,bus,firetruck|lava_1c06d976@night-clear-volcano|pit@obs0,lava@obs1+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S01/E019_2026-10-01_lava/SIM_LAVA_V2_S021.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-58 s dan sama dengan manifest (±0.3 s) | ✅ | 46.07 s (manifest 46.07) |
| Ukuran wajar (8-20 MB) | ✅ | 12.4 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.4 dB |
| mean_volume -20..-12 dB | ✅ | -14.4 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 8.4s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 12.8s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 19.9s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 26.4s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 38.2s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 45.3s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | lava|police,bus,firetruck|lava_1c06d976@night-clear-volcano|pit@obs0,lava@obs1+broken,win |
| Seed belum dipakai video lain | ✅ | seed 21 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video lava berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
