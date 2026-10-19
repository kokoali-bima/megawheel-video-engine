# Audit 3D: SIM_SPLASH_V2_S013

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['SIREN THE POLICE CAR', 'HYDRO THE FIRE TRUCK', 'ROCKY THE MONSTER TRUCK'] |
| replay outcomes sama dengan versi review | ✅ | ['crash@obs2+broken', 'pit@obs0+broken', 'win'] vs ['crash@obs2+broken', 'pit@obs0+broken', 'win'] |
| replay theme_id sama dengan versi review | ✅ | noon-rain-city vs noon-rain-city |
| replay voice sama dengan versi review | ✅ | en-US-JennyNeural vs en-US-JennyNeural |
| replay track_id sama dengan versi review | ✅ | splash_e87583b8 vs splash_e87583b8 |
| replay durasi sama (tanpa cold open) | ✅ | 55.57 vs 58.57 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1757 vs 1757 |
| durasi = manifest (±0.3 s) | ✅ | 58.57 vs 58.57 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [160, 163, 171, 161, 161, 163, 160, 162, 162, 166, 162, 164] |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=7.90 |
| L2: masuk kolam -> cipratan terjadwal | ✅ | t=6.97 |
| L2: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=7.10 |
