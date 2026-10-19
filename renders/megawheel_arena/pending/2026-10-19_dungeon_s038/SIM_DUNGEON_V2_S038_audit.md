# Audit otomatis: SIM_DUNGEON_V2_S038

- Tanggal: 2026-10-19 08:17 · Auditor: audit.py (otomatis) · Engine: sim-prototype v2 · Seed: 38 · Track: dungeon_18b2aebf
- Mengacu: `/root/video-engine/BLUEPRINT.md` bagian 5, 6, 7
- **Hasil: LOLOS dengan catatan** → boleh dikirim sebagai preview (RENDERED_PENDING_APPROVAL)


## 5.1 Analisa fisika
| Cek | Hasil | Nilai |
|---|---|---|
| Semua mobil bergerak maju ke kanan (+x) | ✅ | 3.0->70.4 m, 3.0->43.2 m, 3.0->144.9 m |
| Minimal 2 rintangan di antara start dan finish | ✅ | 5 rintangan [axe, ogre, lava, axe, axe] (36-99 m), finish 108 m |
| Pola cerita sesuai STORY | ✅ | ['fail', 'fail', 'win'] (target ['fail', 'fail', 'win']) |
| Tidak ada timeout | ✅ |  |
| Waktu event masuk akal | ✅ | 10.6s, 6.5s, 7.8s |
| Level gagal di rintangan berbeda | ✅ | rintangan [2, 0] |
| Minimal 1 momen spektakuler di level gagal (hancur/terbalik/lompatan bullet-time) | ✅ |  |
| Durasi total 40-58 s | ✅ | 50.3 s |
| Level gagal <= 20 s, level menang (+outro) <= 26 s | ✅ | 20.3s, 11.0s, 19.1s |
| Sidik jari belum ada di registry | ✅ | dungeon|taxi,bigrig,sports|dungeon_18b2aebf@sunset-clear-volcano|pit@obs2+broken,chop@obs0+broken,win |

## 6.1 Teknis
| Cek | Hasil | Nilai |
|---|---|---|
| File video ada | ✅ | /root/video-engine/renders/megawheel_arena/pending/2026-10-19_dungeon_s038/SIM_DUNGEON_V2_S038.mp4 |
| H.264 1080x1920 | ✅ | h264 1080x1920 |
| Frame rate 30 | ✅ | 30/1 |
| Audio AAC ada | ✅ | aac |
| Durasi 20-175 s (tidak dibatasi kaku, user 2026-10-04; batas teknis Shorts) dan sama dengan manifest (±0.3 s) | ✅ | 53.33 s (manifest 53.33) |
| Ukuran wajar (8-20 MB) | ⚠️ | 33.8 MB |

## 6.2 Audio
| Cek | Hasil | Nilai |
|---|---|---|
| max_volume -3..-0.1 dB (tidak clipping) | ✅ | -1.4 dB |
| mean_volume -20..-12 dB | ✅ | -13.3 dB |
| Narasi terakhir = CTA baku | ✅ | Tap LIKE if you enjoyed this video, DISLIKE if you didn't, a... |
| Narasi lengkap (intro + hasil tiap level + CTA) | ✅ | 8 baris |

## 6.3 Sinkron
| Cek | Hasil | Nilai |
|---|---|---|
| L1: badge LEVEL 1 tampil di awal level | ✅ | 59% piksel warna level @ 3.6s |
| L1: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 16.4s |
| L2: badge LEVEL 2 tampil di awal level | ✅ | 56% piksel warna level @ 23.9s |
| L2: badge FAIL tampil tepat di event | ✅ | 48% piksel badge @ 31.3s |
| L3: badge LEVEL 3 tampil di awal level | ✅ | 56% piksel warna level @ 34.9s |
| L3: badge WINNER tampil tepat di event | ✅ | 28% piksel badge @ 45.2s |
| Panel outro LIKE/SUBSCRIBE tampil di akhir | ✅ | 62% piksel panel @ 52.5s |

## 5.2 Preview
| Cek | Hasil | Nilai |
|---|---|---|
| PNG preview tersedia (>= 6, termasuk outro) | ✅ | 13 file |

## 7 Keunikan
| Cek | Hasil | Nilai |
|---|---|---|
| Sidik jari unik di registry | ✅ | dungeon|taxi,bigrig,sports|dungeon_18b2aebf@sunset-clear-volcano|pit@obs2+broken,chop@obs0+broken,win |
| Seed belum dipakai video lain | ✅ | seed 38 |
| Maks 3 video berturut-turut dari seri yang sama | ⚠️ | 4 video dungeon berturut-turut sebelum ini |

Keterangan: ❌ = wajib diperbaiki (gagal audit), ⚠️ = peringatan (boleh lanjut).
