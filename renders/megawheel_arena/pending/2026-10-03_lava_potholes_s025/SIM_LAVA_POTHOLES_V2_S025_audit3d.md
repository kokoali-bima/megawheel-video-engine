# Audit 3D: SIM_LAVA_POTHOLES_V2_S025

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['NITRO THE RACE CAR', 'SPRINKLES THE ICE CREAM TRUCK', 'TILLY THE TAXI'] |
| replay outcomes sama dengan versi review | ✅ | ['pit@obs2+broken', 'stuck@obs0', 'win'] vs ['pit@obs2+broken', 'stuck@obs0', 'win'] |
| replay theme_id sama dengan versi review | ✅ | noon-clear-volcano vs noon-clear-volcano |
| replay voice sama dengan versi review | ✅ | chatterbox:f1 vs chatterbox:f1 |
| replay track_id sama dengan versi review | ✅ | lava_potholes_f018885c vs lava_potholes_f018885c |
| replay durasi sama (tanpa cold open) | ✅ | 49.27 vs 50.77 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1523 vs 1523 |
| durasi = manifest (±0.3 s) | ✅ | 50.77 vs 50.77 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [128, 129, 135, 129, 132, 131, 136, 126, 139, 137, 143, 142] |
| L1: kontak lava -> ledakan terjadwal | ✅ | t=7.50 |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=7.63 |
