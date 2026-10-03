# Audit 3D: SIM_POTHOLES_V2_S021

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['SIREN THE POLICE CAR', 'TITAN THE BIG RIG', 'ZIPPY THE SPORTS CAR'] |
| replay outcomes sama dengan versi review | ✅ | ['rollback@obs2+broken', 'stuck@obs1', 'win'] vs ['rollback@obs2+broken', 'stuck@obs1', 'win'] |
| replay theme_id sama dengan versi review | ✅ | night-rain-city vs night-rain-city |
| replay voice sama dengan versi review | ✅ | chatterbox:m1 vs chatterbox:m1 |
| replay track_id sama dengan versi review | ✅ | potholes_3c6546c2 vs potholes_3c6546c2 |
| replay durasi sama (tanpa cold open) | ✅ | 49.57 vs 51.07 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1532 vs 1532 |
| durasi = manifest (±0.3 s) | ✅ | 51.07 vs 51.07 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [77, 73, 72, 56, 74, 71, 71, 74, 67, 73, 96, 96] |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=8.33 |
