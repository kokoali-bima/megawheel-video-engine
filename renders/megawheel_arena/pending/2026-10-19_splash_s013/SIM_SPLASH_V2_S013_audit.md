# Audit otomatis: SIM_SPLASH_V2_S013

- Tanggal: 2026-10-19 10:32 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 + godot3d (lab/godot3d_challenge) · Seed: 13 · Track: splash_e87583b8
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->91.8 m, 3.0->34.8 m, 3.0->113.6 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, hill, wall] (17-93 m), finish 97 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 7.9s, 6.8s, 9.1s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 55.6 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 19.2s, 14.2s, 22.2s |
| Sidik jari belum ada di registry | ✅ | splash|police,firetruck,monster|splash_e87583b8@noon-rain-city|crash@obs2+broken,pit@obs0+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-19_splash_s013/SIM_SPLASH_V2_S013.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 59.70 s (manifest 59.7) |
| Ukuran wajar (8-35 MB) | ✅ | 24.9 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -1.3 dB |
| mean_volume -20..-12 dB | ✅ | -12.9 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 15.2s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 22.5s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 32.6s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 37.2s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 49.8s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 66% piksel panel @ 58.9s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 26 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | splash|police,firetruck,monster|splash_e87583b8@noon-rain-city|crash@obs2+broken,pit@obs0+broken,win |
| Seed belum dipakai video lain | ✅ | seed 13 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video splash berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
