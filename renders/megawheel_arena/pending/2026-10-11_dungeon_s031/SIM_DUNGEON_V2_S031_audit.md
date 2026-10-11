# Audit otomatis: SIM_DUNGEON_V2_S031

- Tanggal: 2026-10-11 11:55 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 31 · Track: dungeon_4d73da6e
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->66.5 m, 3.0->73.4 m, 3.0->130.5 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 5 rintangan [axe, ogre, lava, axe, axe] (37-103 m), finish 113 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 6.0s, 11.1s, 10.4s |
| Level gagal di rintangan berbeda | ✅ | rintangan [1, 2] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 54.9 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 14.1s, 19.0s, 21.8s |
| Sidik jari belum ada di registry | ✅ | dungeon|sports,firetruck,f1|dungeon_4d73da6e@noon-clear-volcano|smash@obs1+broken,pit@obs2+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-11_dungeon_s031/SIM_DUNGEON_V2_S031.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 57.90 s (manifest 57.9) |
| Ukuran wajar (8-20 MB) | ✅ | 15.3 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -0.5 dB |
| mean_volume -20..-12 dB | ✅ | -14.2 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 10.7s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 17.7s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 32.3s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 36.7s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 49.0s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 66% piksel panel @ 57.1s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | dungeon|sports,firetruck,f1|dungeon_4d73da6e@noon-clear-volcano|smash@obs1+broken,pit@obs2+broken,win |
| Seed belum dipakai video lain | ✅ | seed 31 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 2 video dungeon berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
