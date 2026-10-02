# lab/ — eksperimen (BUKAN produksi)

Keputusan user 2026-10-03: eksperimen tidak boleh bercampur dengan jalur produksi. Tidak ada skrip produksi
(cron, publish, episodes, generators/*) yang boleh mengimpor atau memanggil apa pun dari `lab/`.
Data besar eksperimen (mis. Sonniss SFX) di VM: `/root/lab/` (di luar repo). Gagal → hapus foldernya.

| Folder | Isi |
|---|---|
| `godot_prototype/` | Godot 4 (sampel CHALLENGE/RACE/SMASH, efek hancur & ledakan) — lihat GODOT_PLAYBOOK.md |
| `sfx_bank/` (rencana) | SFX bank dari Sonniss GDC + CC0 — lihat SFX_PLAN.md |
