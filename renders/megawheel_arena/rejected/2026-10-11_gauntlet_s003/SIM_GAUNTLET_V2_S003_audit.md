# Audit otomatis: SIM_GAUNTLET_V2_S003

- Tanggal: 2026-10-11 04:32 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 3 · Track: gauntlet_1e4e5ac3
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->71.2 m, 3.0->73.9 m, 3.0->192.0 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 4 rintangan [pendulum, dominoes, pit, bump] (39-114 m), finish 145 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 6.9s, 7.9s, 14.0s |
| Level gagal di rintangan berbeda | ⚠️ | rintangan [1, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 50.8 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 11.3s, 15.7s, 23.7s |
| Sidik jari belum ada di registry | ✅ | gauntlet|police,bigrig,taxi|gauntlet_1e4e5ac3@morning-clear-desert|chop@obs1+broken,chop@obs1+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/rejected/2026-10-11_gauntlet_s003/SIM_GAUNTLET_V2_S003.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 53.80 s (manifest 53.8) |
| Ukuran wajar (8-20 MB) | ✅ | 15.1 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.4 dB |
| mean_volume -20..-12 dB | ✅ | -14.6 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 11.5s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 14.9s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 23.8s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 30.7s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 45.6s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 53.0s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 11 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | gauntlet|police,bigrig,taxi|gauntlet_1e4e5ac3@morning-clear-desert|chop@obs1+broken,chop@obs1+broken,win |
| Seed belum dipakai video lain | ✅ | seed 3 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video gauntlet berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
