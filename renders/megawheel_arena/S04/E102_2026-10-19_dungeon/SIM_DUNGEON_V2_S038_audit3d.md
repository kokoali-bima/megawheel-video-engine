# Audit 3D: SIM_DUNGEON_V2_S038

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['TILLY THE TAXI', 'TITAN THE BIG RIG', 'ZIPPY THE SPORTS CAR'] |
| replay outcomes sama dengan versi review | ✅ | ['pit@obs2+broken', 'chop@obs0+broken', 'win'] vs ['pit@obs2+broken', 'chop@obs0+broken', 'win'] |
| replay theme_id sama dengan versi review | ✅ | sunset-clear-volcano vs sunset-clear-volcano |
| replay voice sama dengan versi review | ✅ | chatterbox:m1 vs chatterbox:m1 |
| replay track_id sama dengan versi review | ✅ | dungeon_18b2aebf vs dungeon_18b2aebf |
| replay durasi sama (tanpa cold open) | ✅ | 50.33 vs 53.33 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1600 vs 1600 |
| durasi = manifest (±0.3 s) | ✅ | 53.33 vs 53.33 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [84, 79, 83, 87, 80, 76, 78, 77, 84, 82, 103, 102] |
| L1: kontak lava -> ledakan terjadwal | ✅ | t=11.80 |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=11.07 |
| L2: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=6.50 |
