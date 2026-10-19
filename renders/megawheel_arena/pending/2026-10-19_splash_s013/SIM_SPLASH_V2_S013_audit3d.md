# Audit 3D: SIM_SPLASH_V2_S013

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['SIREN THE POLICE CAR', 'HYDRO THE FIRE TRUCK', 'ROCKY THE MONSTER TRUCK'] |
| replay outcomes sama dengan versi review | ✅ | ['crash@obs2+broken', 'pit@obs0+broken', 'win'] vs ['crash@obs2+broken', 'pit@obs0+broken', 'win'] |
| replay theme_id sama dengan versi review | ✅ | noon-rain-city vs noon-rain-city |
| replay voice sama dengan versi review | ✅ | chatterbox:f1 vs chatterbox:f1 |
| replay track_id sama dengan versi review | ✅ | splash_e87583b8 vs splash_e87583b8 |
| replay durasi sama (tanpa cold open) | ✅ | 56.7 vs 59.7 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1791 vs 1791 |
| durasi = manifest (±0.3 s) | ✅ | 59.70 vs 59.7 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [160, 164, 171, 161, 162, 164, 161, 163, 164, 165, 164, 163] |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=7.90 |
| L2: masuk kolam -> cipratan terjadwal | ✅ | t=6.97 |
| L2: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=7.10 |
