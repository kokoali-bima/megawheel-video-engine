# Audit otomatis: MW_SPLASH_3D_S021

- Tanggal: 2026-10-22 14:30 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 + godot3d (Godot3D splash director pilot) · Seed: 21 · Track: splash_b1402a47
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->61.1 m, 3.0->60.1 m, 3.0->110.2 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [hill, wall, pit] (16-93 m), finish 98 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 6.4s, 6.9s, 13.6s |
| Level gagal di rintangan berbeda | ⚠️ | rintangan [1, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 54.0 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 16.0s, 13.2s, 24.8s |
| Sidik jari belum ada di registry | ✅ | splash|police,icecream,bus|splash_b1402a47@night-clear-city|crash@obs1+broken,crash@obs1+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/lab/mw_splash_bright_r2_20261022/s021/MW_SPLASH_3D_S021.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 57.00 s (manifest 57.0) |
| Ukuran wajar (8-35 MB) | ✅ | 27.6 MB |

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
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 12.7s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 19.6s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 28.9s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 32.8s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 48.7s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 65% piksel panel @ 56.2s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 7 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | splash|police,icecream,bus|splash_b1402a47@night-clear-city|crash@obs1+broken,crash@obs1+broken,win |
| Seed belum dipakai video lain | ✅ | seed 21 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 2 video splash berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
