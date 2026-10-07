# Audit 3D: SIM_DUNGEON_V2_S015

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['TILLY THE TAXI', 'TITAN THE BIG RIG', 'SIREN THE POLICE CAR'] |
| replay outcomes sama dengan versi review | ✅ | ['smash@obs1+broken', 'chop@obs0+broken', 'win'] vs ['smash@obs1+broken', 'chop@obs0+broken', 'win'] |
| replay theme_id sama dengan versi review | ✅ | noon-clear-volcano vs noon-clear-volcano |
| replay voice sama dengan versi review | ✅ | chatterbox:m1 vs chatterbox:m1 |
| replay track_id sama dengan versi review | ✅ | dungeon_498bf7de vs dungeon_498bf7de |
| replay durasi sama (tanpa cold open) | ✅ | 46.3 vs 49.3 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1479 vs 1479 |
| durasi = manifest (±0.3 s) | ✅ | 49.30 vs 49.3 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [91, 78, 81, 76, 81, 76, 78, 86, 80, 84, 101, 102] |
| L1: kontak lava -> ledakan terjadwal | ✅ | t=7.83 |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=5.17 |
| L2: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=5.93 |
