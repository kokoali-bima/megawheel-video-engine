# Audit otomatis: SIM_LAVA_V2_S003

- Tanggal: 2026-09-30 10:22 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 3 · Track: lava_8caa7073
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->36.3 m, 3.0->84.3 m, 3.0->120.6 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 5 rintangan [lava, vent, vent, lava, vent] (34-89 m), finish 98 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 4.8s, 6.1s, 9.6s |
| Level gagal di rintangan berbeda | ✅ | rintangan [0, 2] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 46.2 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 10.7s, 14.9s, 20.5s |
| Sidik jari belum ada di registry | ✅ | lava|sports,firetruck,bigrig|lava_8caa7073@morning-clear-volcano|pit@obs0,lava@obs2+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S01/E008_2026-09-30_lava/SIM_LAVA_V2_S003.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 46.20 s (manifest 46.2) |
| Ukuran wajar (8-20 MB) | ✅ | 14.7 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.4 dB |
| mean_volume -20..-12 dB | ✅ | -13.9 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 7.2s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 11.3s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 18.9s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 26.3s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 36.4s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 70% piksel panel @ 45.4s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | lava|sports,firetruck,bigrig|lava_8caa7073@morning-clear-volcano|pit@obs0,lava@obs2+broken,win |
| Seed belum dipakai video lain | ✅ | seed 3 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video lava berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
