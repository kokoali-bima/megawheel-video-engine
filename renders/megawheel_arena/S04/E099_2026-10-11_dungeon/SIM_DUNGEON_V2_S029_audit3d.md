# Audit 3D: SIM_DUNGEON_V2_S029

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['SIREN THE POLICE CAR', 'TITAN THE BIG RIG', 'NITRO THE RACE CAR'] |
| replay outcomes sama dengan versi review | ✅ | ['pit@obs2', 'chop@obs0+broken', 'win'] vs ['pit@obs2', 'chop@obs0+broken', 'win'] |
| replay theme_id sama dengan versi review | ✅ | sunset-clear-volcano vs sunset-clear-volcano |
| replay voice sama dengan versi review | ✅ | chatterbox:m1 vs chatterbox:m1 |
| replay track_id sama dengan versi review | ✅ | dungeon_93c5dcfa vs dungeon_93c5dcfa |
| replay durasi sama (tanpa cold open) | ✅ | 48.27 vs 51.27 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1538 vs 1538 |
| durasi = manifest (±0.3 s) | ✅ | 51.27 vs 51.27 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [82, 79, 85, 83, 84, 77, 86, 78, 87, 83, 102, 101] |
| L1: kontak lava -> ledakan terjadwal | ✅ | t=10.60 |
| L2: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=4.60 |
