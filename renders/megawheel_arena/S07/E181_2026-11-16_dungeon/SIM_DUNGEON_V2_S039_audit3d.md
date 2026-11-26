# Audit 3D: SIM_DUNGEON_V2_S039

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['ZIPPY THE SPORTS CAR', 'HYDRO THE FIRE TRUCK', 'ROCKY THE MONSTER TRUCK'] |
| replay outcomes sama dengan versi review | ✅ | ['smash@obs1+broken', 'rollback@obs2+broken', 'win'] vs ['smash@obs1+broken', 'rollback@obs2+broken', 'win'] |
| replay theme_id sama dengan versi review | ✅ | night-clear-volcano vs night-clear-volcano |
| replay voice sama dengan versi review | ✅ | chatterbox:m1 vs chatterbox:m1 |
| replay track_id sama dengan versi review | ✅ | dungeon_bda59df6 vs dungeon_bda59df6 |
| replay durasi sama (tanpa cold open) | ✅ | 47.8 vs 50.8 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1524 vs 1524 |
| durasi = manifest (±0.3 s) | ✅ | 50.80 vs 50.8 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [91, 81, 81, 82, 79, 84, 101, 82, 79, 80, 100, 100] |
| L1: kontak lava -> ledakan terjadwal | ✅ | t=8.57 |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=3.70 |
| L2: kontak lava -> ledakan terjadwal | ✅ | t=9.97 |
| L2: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=9.73 |
