# Audit 3D: SIM_DUNGEON_V2_S016

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['NITRO THE RACE CAR', 'TITAN THE BIG RIG', 'SPRINKLES THE ICE CREAM TRUCK'] |
| replay outcomes sama dengan versi review | ✅ | ['smash@obs1+broken', 'chop@obs0+broken', 'win'] vs ['smash@obs1+broken', 'chop@obs0+broken', 'win'] |
| replay theme_id sama dengan versi review | ✅ | sunset-clear-volcano vs sunset-clear-volcano |
| replay voice sama dengan versi review | ✅ | chatterbox:m1 vs chatterbox:m1 |
| replay track_id sama dengan versi review | ✅ | dungeon_03484fac vs dungeon_03484fac |
| replay durasi sama (tanpa cold open) | ✅ | 47.17 vs 50.17 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1505 vs 1505 |
| durasi = manifest (±0.3 s) | ✅ | 50.17 vs 50.17 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [94, 79, 83, 86, 77, 86, 78, 83, 79, 83, 101, 101] |
| L1: kontak lava -> ledakan terjadwal | ✅ | t=8.77 |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=5.27 |
| L2: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=3.80 |
