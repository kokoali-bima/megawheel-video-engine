# Audit otomatis: SIM_PINBALL_V2_S006

- Tanggal: 2026-10-11 10:14 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 6 · Track: pinball_01f38df1
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->76.3 m, 3.0->45.9 m, 3.0->106.3 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 2 rintangan [lava, lava] (38-79 m), finish 97 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 6.5s, 4.4s, 13.7s |
| Level gagal di rintangan berbeda | ✅ | rintangan [1, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 54.5 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 16.2s, 9.7s, 28.5s |
| Sidik jari belum ada di registry | ✅ | pinball|sports,firetruck,bigrig|pinball_01f38df1@sunset-clear-volcano|pit@obs1+broken,pit@obs0+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S04/E097_2026-10-11_pinball/SIM_PINBALL_V2_S006.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 57.50 s (manifest 57.5) |
| Ukuran wajar (8-20 MB) | ✅ | 17.5 MB |

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
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 13.5s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 19.8s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 25.8s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 29.6s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 49.1s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 56.7s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | pinball|sports,firetruck,bigrig|pinball_01f38df1@sunset-clear-volcano|pit@obs1+broken,pit@obs0+broken,win |
| Seed belum dipakai video lain | ✅ | seed 6 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video pinball berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
