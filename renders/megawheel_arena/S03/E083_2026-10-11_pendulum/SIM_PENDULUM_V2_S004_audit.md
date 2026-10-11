# Audit otomatis: SIM_PENDULUM_V2_S004

- Tanggal: 2026-10-11 07:48 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 4 · Track: pendulum_489383cb
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->76.8 m, 3.0->76.6 m, 3.0->119.7 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pendulum, lava, pendulum] (39-86 m), finish 108 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 8.1s, 8.0s, 12.3s |
| Level gagal di rintangan berbeda | ⚠️ | rintangan [2, 2] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 54.0 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 17.3s, 14.0s, 22.8s |
| Sidik jari belum ada di registry | ✅ | pendulum|f1,firetruck,bus|pendulum_489383cb@morning-clear-volcano|smash@obs2+broken,smash@obs2+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S03/E083_2026-10-11_pendulum/SIM_PENDULUM_V2_S004.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 57.00 s (manifest 57.0) |
| Ukuran wajar (8-20 MB) | ✅ | 15.4 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.6 dB |
| mean_volume -20..-12 dB | ✅ | -13.9 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 13.6s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 20.9s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 30.9s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 34.8s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 48.7s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 68% piksel panel @ 56.2s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | pendulum|f1,firetruck,bus|pendulum_489383cb@morning-clear-volcano|smash@obs2+broken,smash@obs2+broken,win |
| Seed belum dipakai video lain | ✅ | seed 4 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video pendulum berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
