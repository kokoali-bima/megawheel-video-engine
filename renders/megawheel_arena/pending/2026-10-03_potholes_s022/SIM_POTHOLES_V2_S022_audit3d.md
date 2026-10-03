# Audit 3D: SIM_POTHOLES_V2_S022

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['TILLY THE TAXI', 'SPRINKLES THE ICE CREAM TRUCK', 'HYDRO THE FIRE TRUCK'] |
| replay outcomes sama dengan versi review | ✅ | ['rollback@obs2+broken', 'stuck@obs0', 'win'] vs ['rollback@obs2+broken', 'stuck@obs0', 'win'] |
| replay theme_id sama dengan versi review | ✅ | night-clear-mountains vs night-clear-mountains |
| replay voice sama dengan versi review | ✅ | en-US-EmmaMultilingualNeural vs en-US-EmmaMultilingualNeural |
| replay track_id sama dengan versi review | ✅ | potholes_af8a2b00 vs potholes_af8a2b00 |
| replay durasi sama (tanpa cold open) | ✅ | 46.47 vs 47.97 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1439 vs 1439 |
| durasi = manifest (±0.3 s) | ✅ | 47.97 vs 47.97 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [81, 83, 84, 61, 81, 79, 81, 79, 80, 80, 90, 100] |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=7.33 |
