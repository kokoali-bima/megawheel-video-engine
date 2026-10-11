# Audit otomatis: SIM_GAUNTLET_V2_S004

- Tanggal: 2026-10-11 06:59 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 4 · Track: gauntlet_32cc7e21
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->101.1 m, 3.0->48.2 m, 3.0->507.7 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 4 rintangan [lava, pit, dominoes, pendulum] (40-114 m), finish 139 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 7.7s, 6.0s, 7.4s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 46.3 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 17.0s, 10.7s, 18.6s |
| Sidik jari belum ada di registry | ✅ | gauntlet|police,bigrig,f1|gauntlet_32cc7e21@morning-clear-beach|chop@obs2+broken,rollback@obs0,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-11_gauntlet_s004/SIM_GAUNTLET_V2_S004.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 49.33 s (manifest 49.3) |
| Ukuran wajar (8-20 MB) | ✅ | 16.3 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -15.4 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 13.7s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 20.6s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 27.6s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 31.3s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 41.3s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 68% piksel panel @ 48.5s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | gauntlet|police,bigrig,f1|gauntlet_32cc7e21@morning-clear-beach|chop@obs2+broken,rollback@obs0,win |
| Seed belum dipakai video lain | ✅ | seed 4 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video gauntlet berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
