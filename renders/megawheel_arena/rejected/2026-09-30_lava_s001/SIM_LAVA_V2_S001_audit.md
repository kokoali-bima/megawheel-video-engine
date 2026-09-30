# Audit otomatis: SIM_LAVA_V2_S001

- Tanggal: 2026-09-30 10:04 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 1 · Track: lava_dca3135d
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->105.2 m, 3.0->52.7 m, 3.0->113.4 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 5 rintangan [lava, vent, vent, lava, vent] (23-78 m), finish 87 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 5.9s, 5.3s, 7.7s |
| Level gagal di rintangan berbeda | ✅ | rintangan [4, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-50 s | ✅ | 45.7 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 14.2s, 13.2s, 18.3s |
| Sidik jari belum ada di registry | ✅ | lava|taxi,firetruck,sports|lava_dca3135d@morning-clear-volcano|lava@obs4+broken,lava@obs1+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/rejected/2026-09-30_lava_s001/SIM_LAVA_V2_S001.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 40-50 s dan sama dengan manifest (±0.3 s) | ✅ | 45.73 s (manifest 45.73) |
| Ukuran wajar (8-20 MB) | ✅ | 15.4 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.4 dB |
| mean_volume -20..-12 dB | ✅ | -13.3 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 0.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 8.0s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 14.8s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 21.1s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 28.0s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 37.1s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 70% piksel panel @ 44.9s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 15 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | lava|taxi,firetruck,sports|lava_dca3135d@morning-clear-volcano|lava@obs4+broken,lava@obs1+broken,win |
| Seed belum dipakai video lain | ✅ | seed 1 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video lava berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
