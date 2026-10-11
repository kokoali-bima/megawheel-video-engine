# Audit otomatis: SIM_GAUNTLET_V2_S001

- Tanggal: 2026-10-11 03:56 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 1 · Track: gauntlet_5ed61ba7
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->99.5 m, 3.0->79.5 m, 3.0->351.1 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 4 rintangan [pit, dominoes, bump, lava] (36-126 m), finish 154 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 6.8s, 5.9s, 11.0s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 48.1 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 15.8s, 10.3s, 22.0s |
| Sidik jari belum ada di registry | ✅ | gauntlet|sports,bigrig,f1|gauntlet_5ed61ba7@sunset-clear-beach|flip@obs2,chop@obs1+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/rejected/2026-10-11_gauntlet_s001/SIM_GAUNTLET_V2_S001.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 51.10 s (manifest 51.1) |
| Ukuran wajar (8-20 MB) | ✅ | 15.0 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -15.1 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 13.2s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 19.4s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 26.3s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 29.7s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 43.1s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 50.3s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | gauntlet|sports,bigrig,f1|gauntlet_5ed61ba7@sunset-clear-beach|flip@obs2,chop@obs1+broken,win |
| Seed belum dipakai video lain | ✅ | seed 1 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video gauntlet berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
