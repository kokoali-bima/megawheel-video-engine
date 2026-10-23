# S01E03 — Revisi outro v5 (DRAFT)

Approval versi sebelumnya dibatalkan sesuai permintaan pemilik. Kandidat ini BELUM APPROVED; gate publikasi tetap HOLD. Tidak ada registrasi, penjadwalan, promosi produksi, atau upload.

## Perubahan

Kartu NEXT SUNDAY / THE FORGOTTEN SPEEDWAY diganti dengan MORE ADVENTURES AHEAD / SEE YOU NEXT TIME!. Judul resmi episode tetap The Forgotten Speedway. Penutup tidak lagi menjanjikan episode/tanggal berikutnya.

DeepSeek-Flash (thinking, max8192) mengimplementasikan fix_outro.py dan finalize_outro.py melalui runner proyek. Enam konteks stabil dipertahankan; cache hit panggilan terkait 98–99%. Codex menulis brief/probe, memeriksa kode, menjalankan mesin dan memverifikasi hasil. Respons kosong/terpotong ditolak sebelum dijalankan.

Sumber scene_20.json diperbaiki hanya di engine lab. Kartu 3,5 detik dibangkitkan ulang lewat story25d di CPU VM dan mengganti shot yang sama; seluruh audio outro disalin. Sumber/cache sebelumnya berbeda secara semantik, sehingga hash file saja tidak cukup sebagai bukti kecocokan. Tidak ada generasi TTS atau render Modal. Cache narator yang hilang memblokir upaya render penuh; jalur itu tidak dijalankan.

## Hasil verifikasi

- Video lengkap: S01E03_The_Forgotten_Speedway_REVIEW_v5_DRAFT.mp4, 589,164 detik, 1920x1080, 30fps, 165254098 byte.
- SHA256: 364cb9eda380a4cd9aada2003214fa48f77cd61fe612b7b088f76ca5f8222c84.
- Audio lengkap decode PCM16 identik dengan v4: SHA256 01cae5c226b5028970ba51648b6accd4b6d38dfd01f09d3495f4896d7cdc9741.
- Seluruh 17673 frame dipindai pada grayscale320x180: 0 frame hitam tidak terencana, 354 frame hitam transisi terencana; 0 sampel audio clipping; selisih durasi A/V 0,065 detik.
- Outro: 1805 frame dibandingkan grayscale480x270. Di luar shot kartu (frame1098–1202), selisih maksimum14/255 dan 0 frame di atas40/255. Audio decode identik. Ini pengukuran resolusi pemeriksaan, bukan perbandingan seluruh piksel1080p.
- Frame resolusi penuh dari outro dan video lengkap pada566,4s dilihat Codex: teks netral benar dan terbaca. Bukan review tontonan film bersuara penuh.
- Mesin merakit ulang hanya bagian outro dan transisi di sebelahnya; 54 bagian rakitan lama dipakai ulang. Sebelas input klip lain hash-identik.

## Temuan lama tetap terbuka

Audit sambungan tetap FAIL pada1->0 di8,6s (turun15dB) dan2->3 di91,83s (turun22dB). Tidak ada ambang QA diubah dan tidak dinyatakan PASS menyeluruh. Known issues adegan lain tetap mengikuti laporan v4. Chapters yang tersalin belum diverifikasi dan tidak boleh dipakai untuk metadata publikasi.

## Produksi dan approval

Registry SHA256 6605e0b36970a6ef1726ea1f260fbe248cdbc93a80f43656b87ba3780860eddf dan queue 28955d0824784cc14dbe52f95ff091ccfdbb21798936753bfb6d79dfa6c0a6c1 tetap sama. Master produksi lama tidak berubah. Versi v5 baru dapat diproses publikasi setelah approval baru dari pemilik; approval lama tidak diwariskan.

Bukti di VM: /root/lab/s01e03_rebuild_20261022/outro_fix_v1/ dan delivery_v5/. Gate independen LOLOS_FOR_DRAFT hanya mengizinkan perakitan kandidat, bukan publikasi.
