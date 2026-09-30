# MegaWheel Arena — Video Engine

Engine otomatis untuk channel YouTube **MegaWheel Arena**: video Shorts simulasi fisika 2D kartun, **100% dibuat sendiri** (tanpa footage pihak lain). Fisika pymunk, grafis cairo, audio sintetis, dan narasi Edge-TTS.

**Wajib baca sebelum bekerja:** [`BLUEPRINT.md`](BLUEPRINT.md) (standar baku), [`DEV_HISTORY.md`](DEV_HISTORY.md) (riwayat dan pelajaran), [`cast/CAST.md`](cast/CAST.md) (tokoh tetap).

## Struktur
```
core/                      youtube_uploader.py (dipanggil lewat publish.py)
generators/physics_2d/     sim_engine.py (engine), audit.py, registry.py, find_seeds.sh, tune_bumps.py, tune_cast.py
generators/publishing/     episodes.py (approve/reject/log episode), publish.py (upload HANYA episode APPROVED)
renders/megawheel_arena/   pending/ → S01/E001_<tanggal>_<seri>/ ; rejected/ ; EPISODE_LOG.md
cast/                      characters.json + CAST.md (10 tokoh tetap: Zippy, Siren, Nitro, Tilly, Buster, Hydro, Titan, Sprinkles, Rocky, Grizzly)
branding/                  foto profil, banner, CHANNEL_SETUP.md (generator: generators/branding/make_branding.py)
                           (MP4/PNG tidak di-commit; manifest .json + audit .md + EPISODE_LOG.md di-commit)
PRODUCTION_REGISTRY.json   registry keunikan semua video
auth_*.py                  otorisasi YouTube (credentials/ tidak di-commit)
archive/                   pipeline footage lama + engine v1 (tidak dipakai)
```

## Cepat mulai
```bash
cd /root/video-engine
./venv/bin/python generators/physics_2d/sim_engine.py --seed 2            # seri & tokoh otomatis
./venv/bin/python generators/physics_2d/sim_engine.py --series bumps --seed 3 --preview-only
```
Exit 0 = video lolos audit (`RENDERED_PENDING_APPROVAL`), exit 1 = STOP analisa/registry (coba seed lain), exit 5 = audit gagal.
**Dilarang upload ke YouTube tanpa approval eksplisit dari user.**

## Setup server baru
```bash
apt-get install -y ffmpeg libcairo2-dev pkg-config build-essential python3-dev
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
mkdir -p ~/.fonts && curl -sSL -o ~/.fonts/LuckiestGuy-Regular.ttf \
  https://github.com/google/fonts/raw/main/apache/luckiestguy/LuckiestGuy-Regular.ttf && fc-cache -f
```
