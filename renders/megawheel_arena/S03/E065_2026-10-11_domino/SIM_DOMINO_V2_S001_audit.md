# Audit otomatis: SIM_DOMINO_V2_S001

- Tanggal: 2026-10-11 03:19 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 1 · Track: domino_2076ac00
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->126.5 m, 3.0->74.1 m, 3.0->387.3 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 3 rintangan [dominoes, dominoes, dominoes] (66-178 m), finish 205 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 8.3s, 6.7s, 9.7s |
| Level gagal di rintangan berbeda | ✅ | rintangan [1, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 49.9 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 16.0s, 14.6s, 19.4s |
| Sidik jari belum ada di registry | ✅ | domino|taxi,bus,police|domino_2076ac00@sunset-clear-beach|chop@obs1+broken,chop@obs0+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S03/E065_2026-10-11_domino/SIM_DOMINO_V2_S001.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 52.93 s (manifest 52.93) |
| Ukuran wajar (8-20 MB) | ✅ | 16.9 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.4 dB |
| mean_volume -20..-12 dB | ✅ | -14.8 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 12.8s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 19.6s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 27.2s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 34.2s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 44.8s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 69% piksel panel @ 52.1s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 12 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | domino|taxi,bus,police|domino_2076ac00@sunset-clear-beach|chop@obs1+broken,chop@obs0+broken,win |
| Seed belum dipakai video lain | ✅ | seed 1 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video domino berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
