# Audit 3D: SIM_DUNGEON_V2_S032

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['TILLY THE TAXI', 'BUSTER THE SCHOOL BUS', 'SPRINKLES THE ICE CREAM TRUCK'] |
| replay outcomes sama dengan versi review | ✅ | ['rollback@obs2+broken', 'chop@obs0+broken', 'win'] vs ['rollback@obs2+broken', 'chop@obs0+broken', 'win'] |
| replay theme_id sama dengan versi review | ✅ | morning-clear-volcano vs morning-clear-volcano |
| replay voice sama dengan versi review | ✅ | chatterbox:f1 vs chatterbox:f1 |
| replay track_id sama dengan versi review | ✅ | dungeon_5e996d6b vs dungeon_5e996d6b |
| replay durasi sama (tanpa cold open) | ✅ | 54.9 vs 57.9 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1737 vs 1737 |
| durasi = manifest (±0.3 s) | ✅ | 57.90 vs 57.9 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [82, 79, 81, 82, 78, 90, 84, 79, 80, 82, 103, 101] |
| L1: kontak lava -> ledakan terjadwal | ✅ | t=11.63 |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=10.97 |
| L2: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=5.40 |
