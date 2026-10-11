# Audit 3D: SIM_DUNGEON_V2_S031

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['ZIPPY THE SPORTS CAR', 'HYDRO THE FIRE TRUCK', 'NITRO THE RACE CAR'] |
| replay outcomes sama dengan versi review | ✅ | ['smash@obs1+broken', 'pit@obs2+broken', 'win'] vs ['smash@obs1+broken', 'pit@obs2+broken', 'win'] |
| replay theme_id sama dengan versi review | ✅ | noon-clear-volcano vs noon-clear-volcano |
| replay voice sama dengan versi review | ✅ | chatterbox:f1 vs chatterbox:f1 |
| replay track_id sama dengan versi review | ✅ | dungeon_4d73da6e vs dungeon_4d73da6e |
| replay durasi sama (tanpa cold open) | ✅ | 54.9 vs 57.9 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1737 vs 1737 |
| durasi = manifest (±0.3 s) | ✅ | 57.90 vs 57.9 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [92, 78, 82, 73, 78, 78, 78, 78, 83, 85, 104, 102] |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=6.00 |
| L2: kontak lava -> ledakan terjadwal | ✅ | t=11.63 |
| L2: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=11.70 |
