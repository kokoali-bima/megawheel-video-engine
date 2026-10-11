# Audit otomatis: SIM_BUMPS_V2_S022

- Tanggal: 2026-10-11 11:06 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 22 · Track: bumps_56282b86
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->71.5 m, 3.0->56.1 m, 3.0->115.5 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 4 rintangan [bump, bump, bump, bump] (41-77 m), finish 87 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 4.1s, 5.5s, 10.9s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 47.1 s |
| Level gagal <= 18 s, level menang (+outro) <= 27 s | ✅ | 12.4s, 10.8s, 23.9s |
| Sidik jari belum ada di registry | ✅ | bumps|taxi,bigrig,monster|bumps_56282b86@morning-clear-beach|flip@obs2+broken,stuck@obs1,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S04/E091_2026-10-11_bumps/SIM_BUMPS_V2_S022.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 50.13 s (manifest 50.13) |
| Ukuran wajar (8-20 MB) | ✅ | 16.1 MB |

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
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 9.6s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 16.0s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 23.9s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 26.8s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 40.2s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 66% piksel panel @ 49.3s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | bumps|taxi,bigrig,monster|bumps_56282b86@morning-clear-beach|flip@obs2+broken,stuck@obs1,win |
| Seed belum dipakai video lain | ✅ | seed 22 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video bumps berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
