# Audit 3D: SIM_DUNGEON_V2_S026

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['ZIPPY THE SPORTS CAR', 'SPRINKLES THE ICE CREAM TRUCK', 'BUSTER THE SCHOOL BUS'] |
| replay outcomes sama dengan versi review | ✅ | ['chop@obs0+broken', 'smash@obs1+broken', 'win'] vs ['chop@obs0+broken', 'smash@obs1+broken', 'win'] |
| replay theme_id sama dengan versi review | ✅ | night-clear-volcano vs night-clear-volcano |
| replay voice sama dengan versi review | ✅ | chatterbox:m1 vs chatterbox:m1 |
| replay track_id sama dengan versi review | ✅ | dungeon_3ec589ba vs dungeon_3ec589ba |
| replay durasi sama (tanpa cold open) | ✅ | 47.1 vs 50.1 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1503 vs 1503 |
| durasi = manifest (±0.3 s) | ✅ | 50.10 vs 50.1 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [90, 80, 86, 82, 85, 81, 81, 84, 76, 78, 99, 99] |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=3.27 |
| L2: kontak lava -> ledakan terjadwal | ✅ | t=8.03 |
| L2: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=5.03 |
