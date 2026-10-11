# Audit otomatis: SIM_POTHOLES_V2_S033

- Tanggal: 2026-10-11 11:05 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 33 · Track: potholes_4aef05c9
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->59.7 m, 3.0->40.6 m, 3.0->122.6 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [pit, pit, pit] (36-77 m), finish 100 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 5.9s, 6.6s, 10.5s |
| Level gagal di rintangan berbeda | ✅ | rintangan [1, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 52.3 s |
| Level gagal <= 20 s, level menang (+outro) <= 24 s | ✅ | 12.5s, 16.6s, 23.2s |
| Sidik jari belum ada di registry | ✅ | potholes|police,icecream,firetruck|potholes_4aef05c9@noon-clear-mountains|stuck@obs1,pit@obs0+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-11_potholes_s033/SIM_POTHOLES_V2_S033.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 55.30 s (manifest 55.3) |
| Ukuran wajar (8-20 MB) | ✅ | 13.0 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.4 dB |
| mean_volume -20..-12 dB | ✅ | -14.5 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 12.7s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 16.1s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 25.6s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 32.7s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 46.4s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 66% piksel panel @ 54.5s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 14 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | potholes|police,icecream,firetruck|potholes_4aef05c9@noon-clear-mountains|stuck@obs1,pit@obs0+broken,win |
| Seed belum dipakai video lain | ✅ | seed 33 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video potholes berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
