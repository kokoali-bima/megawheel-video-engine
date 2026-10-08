# Audit otomatis: SIM_DUNGEON_V2_S016

- Tanggal: 2026-10-08 03:03 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 16 · Track: dungeon_03484fac
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->75.2 m, 3.0->43.4 m, 3.0->124.8 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 5 rintangan [axe, ogre, lava, axe, axe] (39-104 m), finish 114 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 5.3s, 3.8s, 14.0s |
| Level gagal di rintangan berbeda | ✅ | rintangan [1, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 47.2 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 13.2s, 9.3s, 24.6s |
| Sidik jari belum ada di registry | ✅ | dungeon|f1,bigrig,icecream|dungeon_03484fac@sunset-clear-volcano|smash@obs1+broken,chop@obs0+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-08_dungeon_s016/SIM_DUNGEON_V2_S016.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 50.17 s (manifest 50.17) |
| Ukuran wajar (8-20 MB) | ⚠️ | 30.7 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -1.0 dB |
| mean_volume -20..-12 dB | ✅ | -13.1 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 9.8s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 16.8s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 21.6s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 26.1s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 42.0s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 46% piksel panel @ 49.4s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 12 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | dungeon|f1,bigrig,icecream|dungeon_03484fac@sunset-clear-volcano|smash@obs1+broken,chop@obs0+broken,win |
| Seed belum dipakai video lain | ✅ | seed 16 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 1 video dungeon berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
