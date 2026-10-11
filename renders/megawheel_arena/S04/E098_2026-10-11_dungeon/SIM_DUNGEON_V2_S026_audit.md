# Audit otomatis: SIM_DUNGEON_V2_S026

- Tanggal: 2026-10-11 12:05 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 26 · Track: dungeon_3ec589ba
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->37.1 m, 3.0->73.8 m, 3.0->122.1 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 5 rintangan [axe, ogre, lava, axe, axe] (37-100 m), finish 110 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 3.3s, 5.0s, 12.0s |
| Level gagal di rintangan berbeda | ✅ | rintangan [0, 1] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 47.1 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 11.7s, 12.9s, 22.5s |
| Sidik jari belum ada di registry | ✅ | dungeon|sports,icecream,bus|dungeon_3ec589ba@night-clear-volcano|chop@obs0+broken,smash@obs1+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S04/E098_2026-10-11_dungeon/SIM_DUNGEON_V2_S026.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 50.10 s (manifest 50.1) |
| Ukuran wajar (8-20 MB) | ⚠️ | 30.3 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -1.2 dB |
| mean_volume -20..-12 dB | ✅ | -13.3 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 7.8s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 15.3s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 21.3s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 28.2s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 41.8s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 47% piksel panel @ 49.3s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | dungeon|sports,icecream,bus|dungeon_3ec589ba@night-clear-volcano|chop@obs0+broken,smash@obs1+broken,win |
| Seed belum dipakai video lain | ✅ | seed 26 |
| Maks 3 video berturut-turut dari seri yang sama | ⚠️ | 3 video dungeon berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
