# AGENT_ANALYTICS_REPORT — laporan harian MegaWheel Arena untuk agent (VM 99.2) → Telegram

> Dibuat 2026-10-03 atas permintaan user. Laporan hanya-baca (statistik). **Tidak ada token/kunci di file ini
> maupun di file laporan**; semua kredensial ada di `credentials/` VM 99.3 yang di-ignore git dan tidak boleh disalin.

## Jadwal
- VM 99.3 cron **06:30 UTC = 13:30 WIB** setiap hari: `generators/publishing/analytics_daily.sh`
  (menunggu `daily_publish.sh` 12:00 WIB selesai, lalu membuat laporan dan push ke GitHub).
- Bot user mengecek **14:00 WIB** → laporan sudah segar.

## File yang ditarik
| File (repo `megawheel-video-engine`) | Isi | Untuk |
|---|---|---|
| `renders/megawheel_arena/ANALYTICS_TELEGRAM.txt` | ringkasan teks polos < 4000 karakter (views, menit, subs, per seri, top 3, terlemah, upload 36 jam ke depan) | **langsung kirim ke Telegram** |
| `renders/megawheel_arena/ANALYTICS_LATEST.json` | data lengkap per video & per seri (`channel`, `series`, `videos`, `upcoming`, `generated`) | logika agent / grafik |
| `renders/megawheel_arena/ANALYTICS_REPORT.md` | tabel lengkap Markdown | arsip / dibaca manusia |

Catatan: data YouTube Analytics terlambat 1–3 hari (angka hari ini belum masuk).

## Cara menarik (pilih satu)
**A. Git (disarankan)** — agent 99.2 punya clone repo (akses baca):
```bash
git -C /path/megawheel-video-engine pull -q --ff-only
cat /path/megawheel-video-engine/renders/megawheel_arena/ANALYTICS_TELEGRAM.txt
```
**B. SCP lewat LAN** (kalau 99.2 punya kunci SSH ke 99.3):
```bash
scp root@192.168.99.3:/root/video-engine/renders/megawheel_arena/ANALYTICS_TELEGRAM.txt /tmp/
```

## Kirim ke Telegram (contoh; token & chat id disimpan di VM 99.2 sendiri, JANGAN di repo)
```bash
# di VM 99.2, mis. /etc/megawheel-bot.env (chmod 600):  TG_TOKEN=...  TG_CHAT=...
. /etc/megawheel-bot.env
curl -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
     -d chat_id="${TG_CHAT}" --data-urlencode text@/tmp/ANALYTICS_TELEGRAM.txt
```
(Teks polos, tanpa `parse_mode` → aman dari error karakter Markdown.)

## Pemeriksaan sehat (agent)
- `ANALYTICS_LATEST.json` → `generated` harus tanggal hari ini (UTC). Kalau tidak: laporkan
  "analytics belum diperbarui" dan cek `work/analytics_daily.log` di 99.3.
- Jangan pernah menjalankan upload/approve dari agent ini — hanya membaca & melapor.
