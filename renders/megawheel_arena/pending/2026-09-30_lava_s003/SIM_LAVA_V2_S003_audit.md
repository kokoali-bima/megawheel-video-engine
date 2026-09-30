# Audit otomatis: SIM_LAVA_V2_S003

- Tanggal: 2026-09-30 09:27 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 3 · Track: lava_79de68da
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->24.3 m, 3.0->62.5 m, 3.0->108.9 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 5 rintangan [lava, vent, vent, lava, vent] (22-75 m), finish 85 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 5.8s, 5.6s, 7.2s |
| Level gagal di rintangan berbeda | ✅ | rintangan [0, 2] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 47.1 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 15.9s, 12.8s, 18.4s |
| Sidik jari belum ada di registry | ✅ | lava|f1,firetruck,bus|lava_79de68da@night-clear-volcano|flip@obs0,lava@obs2+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-09-30_lava_s003/SIM_LAVA_V2_S003.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 47.10 s (manifest 47.1) |
| Ukuran wajar (8-20 MB) | ✅ | 12.6 MB |

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
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 9.7s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 16.5s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 22.0s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 29.3s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 37.2s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 46.3s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | lava|f1,firetruck,bus|lava_79de68da@night-clear-volcano|flip@obs0,lava@obs2+broken,win |
| Seed belum dipakai video lain | ✅ | seed 3 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video lava berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
