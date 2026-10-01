# Audit otomatis: SIM_LAVA_V2_S008

- Tanggal: 2026-10-01 02:12 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 8 · Track: lava_f0e06872
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->38.0 m, 3.0->36.7 m, 3.0->150.2 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 5 rintangan [lava, vent, vent, lava, vent] (36-91 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 6.9s, 5.3s, 7.0s |
| Level gagal di rintangan berbeda | ⚠️ | rintangan [0, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 42.7 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 14.0s, 9.9s, 18.9s |
| Sidik jari belum ada di registry | ✅ | lava|f1,bigrig,monster|lava_f0e06872@night-clear-volcano|pit@obs0,stuck@obs0,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/rejected/2026-10-01_lava_s008/SIM_LAVA_V2_S008.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 42.73 s (manifest 42.73) |
| Ukuran wajar (8-20 MB) | ✅ | 10.8 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -13.3 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 7 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 10.3s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 14.6s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 21.0s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 24.5s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 32.8s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 70% piksel panel @ 41.9s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | lava|f1,bigrig,monster|lava_f0e06872@night-clear-volcano|pit@obs0,stuck@obs0,win |
| Seed belum dipakai video lain | ✅ | seed 8 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video lava berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
