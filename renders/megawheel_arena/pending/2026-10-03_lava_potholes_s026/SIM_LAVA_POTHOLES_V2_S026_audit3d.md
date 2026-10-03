# Audit 3D: SIM_LAVA_POTHOLES_V2_S026

- Hasil: **LULUS**

| Cek | Hasil | Nilai |
|---|---|---|
| replay tokoh sama dengan versi review | ✅ | ['SIREN THE POLICE CAR', 'TITAN THE BIG RIG', 'NITRO THE RACE CAR'] |
| replay outcomes sama dengan versi review | ✅ | ['rollback@obs2+broken', 'stuck@obs0', 'win'] vs ['rollback@obs2+broken', 'stuck@obs0', 'win'] |
| replay theme_id sama dengan versi review | ✅ | morning-clear-volcano vs morning-clear-volcano |
| replay voice sama dengan versi review | ✅ | chatterbox:m1 vs chatterbox:m1 |
| replay track_id sama dengan versi review | ✅ | lava_potholes_52feb935 vs lava_potholes_52feb935 |
| replay durasi sama (tanpa cold open) | ✅ | 45.27 vs 46.77 |
| semua roda tergambar (jumlah roda = data mobil, maks 6) | ✅ | ok |
| tidak ada SCRIPT ERROR Godot | ✅ | [] |
| 1080x1920 30 fps + audio | ✅ | 1080x1920 30/1 audio=True |
| jumlah frame = timeline + cold open (±2) | ✅ | 1403 vs 1403 |
| durasi = manifest (±0.3 s) | ✅ | 46.77 vs 46.77 |
| tidak ada frame hitam / putih (12 sampel) | ✅ | [127, 128, 136, 135, 118, 131, 135, 123, 136, 131, 141, 140] |
| L1: kontak lava -> ledakan terjadwal | ✅ | t=10.27 |
| L1: tabrakan -> panel copot (tanpa ledakan kecuali lava) | ✅ | t=8.73 |
