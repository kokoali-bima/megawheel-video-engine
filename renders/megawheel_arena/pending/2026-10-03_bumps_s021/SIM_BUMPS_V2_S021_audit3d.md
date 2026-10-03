# Audit 3D: SIM_BUMPS_V2_S021

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['ZIPPY THE SPORTS CAR', 'BUSTER THE SCHOOL BUS', 'ROCKY THE MONSTER TRUCK'] |
| replay outcomes sama dengan versi review | ✅ | ['flip@obs2', 'flip@obs1+broken', 'win'] vs ['flip@obs2', 'flip@obs1+broken', 'win'] |
| replay theme_id sama dengan versi review | ✅ | sunset-rain-beach vs sunset-rain-beach |
| replay voice sama dengan versi review | ✅ | chatterbox:m1 vs chatterbox:m1 |
| replay track_id sama dengan versi review | ✅ | bumps_75aba530 vs bumps_75aba530 |
| replay durasi sama (tanpa cold open) | ✅ | 47.83 vs 49.33 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1480 vs 1480 |
| durasi = manifest (±0.3 s) | ✅ | 49.33 vs 49.33 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [145, 144, 145, 144, 147, 148, 147, 151, 152, 149, 149, 150] |
| L2: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=5.53 |
