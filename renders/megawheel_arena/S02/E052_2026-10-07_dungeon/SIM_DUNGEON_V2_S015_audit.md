# Audit otomatis: SIM_DUNGEON_V2_S015

- Tanggal: 2026-10-07 10:29 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 + godot3d (lab/godot3d_challenge) · Seed: 15 · Track: dungeon_498bf7de
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->76.3 m, 3.0->49.5 m, 3.0->127.2 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 5 rintangan [axe, ogre, lava, axe, axe] (40-106 m), finish 115 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 5.2s, 5.9s, 12.6s |
| Level gagal di rintangan berbeda | ✅ | rintangan [1, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 46.3 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 9.3s, 13.8s, 23.2s |
| Sidik jari belum ada di registry | ✅ | dungeon|taxi,bigrig,police|dungeon_498bf7de@noon-clear-volcano|smash@obs1+broken,chop@obs0+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/S02/E052_2026-10-07_dungeon/SIM_DUNGEON_V2_S015.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 49.30 s (manifest 49.3) |
| Ukuran wajar (8-35 MB) | ✅ | 29.5 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -1.1 dB |
| mean_volume -20..-12 dB | ✅ | -13.3 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 9.7s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 12.9s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 19.8s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 26.7s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 41.2s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 50% piksel panel @ 48.5s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | dungeon|taxi,bigrig,police|dungeon_498bf7de@noon-clear-volcano|smash@obs1+broken,chop@obs0+broken,win |
| Seed belum dipakai video lain | ✅ | seed 15 |
| Maks 3 video berturut-turut dari seri yang sama | ✅ | 0 video dungeon berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
