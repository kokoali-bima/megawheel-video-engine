# Audit otomatis: SIM_POTHOLES_V2_S031

- Tanggal: 2026-10-04 01:53 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 31 · Track: potholes_1983c5c3
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->56.9 m, 3.0->40.1 m, 3.0->129.9 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, pit, pit] (35-74 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 6.6s, 6.3s, 9.1s |
| Level gagal di rintangan berbeda | ✅ | rintangan [1, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 48.5 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 15.6s, 12.9s, 20.0s |
| Sidik jari belum ada di registry | ✅ | potholes|police,firetruck,sports|potholes_1983c5c3@morning-clear-desert|stuck@obs1+broken,pit@obs0+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-04_potholes_s031/SIM_POTHOLES_V2_S031.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-59.5 s (58 + cold open 1.5) dan sama dengan manifest (±0.3 s) | ✅ | 50.03 s (manifest 50.03) |
| Ukuran wajar (8-20 MB) | ✅ | 12.5 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -14.1 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 2.1s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 10.6s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 17.7s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 26.4s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 30.6s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 41.9s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 49.2s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | potholes|police,firetruck,sports|potholes_1983c5c3@morning-clear-desert|stuck@obs1+broken,pit@obs0+broken,win |
| Seed belum dipakai video lain | ✅ | seed 31 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 1 video potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
