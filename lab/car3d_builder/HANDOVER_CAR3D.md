# HANDOVER: MegaWheel 3D characters (car3d), state 2026-10-27

Start here in a new session. Read this file, then `CONTRACT.md` + `CONTRACT_PART4_BUILDER.md` (the spec), then look at the
latest lineup/frames in `../samples/` (names below). Talk to the owner in Bahasa Indonesia.

## 1. What the owner wants (decisions, in order)
1. 2026-10-27: MegaWheel Arena must NOT use AI video (Hunyuan/Wan) for crashes: damage and impacts are not consistent.
2. Keep the aired Challenge Shorts exactly (world, HUD, physics, camera, audio, cold open) and make ONLY the characters 3D,
   with 4 wheels. Camera views are discussed only after the characters are right (still open).
3. Kenney Car Kit models (v2/v3) were rejected: "an upgrade must be better than the original, not a downgrade". The accepted
   direction (v4+) rebuilds the ORIGINAL 2D designs of `sim_engine.draw_body/draw_face/draw_wheel` as 3D toys inside Godot.
4. Polish rounds: ink outline like the 2D stroke, rounded bevels, supersampling (v5); 3D wreck pieces, dents, cracks (v6);
   ice cream truck and fire truck identity details (v7); two 3D headlight beams instead of one 2D shaft (v8).
5. AGENTS.md rule 5 in the production repo was changed by the owner's order (commit c77b621): 3D characters are allowed only
   when rebuilt from the exact aired 2D designs; generic/off-model cars stay forbidden.
6. S021 (Bumps) v6 was approved and then WITHDRAWN by the owner: it is the same simulation as the already-aired Ep. 45
   (YouTube reused-content risk). Nothing was queued or uploaded. To air 3D Shorts: render NEW seeds, never re-air an aired story.
8. Camera (owner 2026-10-27): hybrid program in `project/cam_program.gd` (`CamProgram.pose`): level intro low FRONT (like
   samples/megawheel_hero_v1_gaya3D_tampak_depan.mp4) swinging to 3/4, live 3/4 yaw 16 deg with LIFT 10 deg ("a bit higher, it is 3D now"),
   replay swings to front-side 75 deg raised 12 deg (odd replays from behind) and dollies in, winner = slow orbit. The camera is rotated
   rigidly around the CAR point, so the 2D overlay (HUD, FAIL, bubbles) stays aligned. A "FrontWorld" (green ground + trees + hills on the
   camera side) rises only when |yaw| > 30 deg; live frames keep the brown cross-section so pits stay readable (owner chose this, option
   `CAR3D_FRONT=1` = always green). Camera never goes below ground_h + 1.5 m. Tuning: `CAR3D_YAW`, constants in cam_program.gd.
7. No Modal: everything renders on the VM CPU (Godot 4.4.1 opengl3/llvmpipe under xvfb), about 7-8 min per episode with
   supersampling 2x. DeepSeek cap raised by the owner to US$10 cumulative (`DEEPSEEK_BUDGET_USD=10` env on ds_run calls).

## 2. Where everything is
| What | Where |
|---|---|
| Spec | `car3d/CONTRACT.md` (parts 1-3: GLB/Kenney era, kept for history), `car3d/CONTRACT_PART4_BUILDER.md` (THE spec: builder 4, polish 4b, damage 4c, identity 4d) |
| Builder code (source of truth on PC/Drive) | `car3d/project/car_builder.gd` (`class_name CarBuilder`: shaders, geometry, faces/moods, wheels, damage, debris, headlights, 5 cars) and `car3d/project/car_builder_big.gd` (`CarBuilderBig`: f1, bus, firetruck, bigrig, icecream) |
| Game scene (lab copy) | `car3d/project/challenge3d.gd` = copy of the live `video-engine/lab/godot3d_challenge/project/challenge3d.gd` + the builder mode (`glb_dir == "builder"`), `_break3d`, dent call, supersampling (`CAR3D_SS`), headlights hook |
| Camera program | `car3d/project/cam_program.gd` (pose + FrontWorld), wired in `challenge3d.gd` builder camera block |
| QC lineup | `car3d/project/lineup_builder.gd` + `lineup.tscn` (side = orthographic like the 2D, quarter = 3/4 view) |
| VM lab (runs) | `/root/lab/car3d/` (project/, gr.sh, fullb.sh, lu.sh, videos) and `/root/lab/crash3d/` (parked solver). Both have a `.keep` file (retention keeps them). |
| GitHub copy | `video-engine/lab/car3d_builder/` (commit after c77b621): contracts, project scripts, vm_scripts. Production never imports lab/. |
| VM scripts copy | `car3d/vm_scripts/` (gr.sh, fullb.sh, lu.sh, Kenney/GLB exporters of the rejected era) |
| DeepSeek briefs/replies | `car3d/tasks/T7..T22`, `car3d/runs/T*` ; packs `DS/tool/packs/megawheel-car3d*.txt` |
| 2D reference | `car3d/ref/sim_engine_draw.py` (VEHICLES, FACES, draw_face, draw_body, draw_wheel), `car3d/ref2d/*_normal.png`, `car3d/ref2d_sheet.png` |
| Latest outputs (PC `videogen/samples/`) | lineup: `builder_side_v3_crop.png`, `builder_quarter_v5_crop.png`; game: `fire_ice_game.png`, `hl_compare.png`; videos `S026_car3d_v5.mp4`, `S021bumps_car3d_v6.mp4`, `S022potholes_car3d_v6.mp4` (v7/v8 on the VM: `/root/lab/car3d/S022potholes_car3d_v7.mp4`, `..._v8.mp4`) |

## 3. How to run (VM 192.168.99.4 via `ssh -i mykey/id_ed25519 -J root@2.28.128.77:22022 -p 22022 root@192.168.99.4`)
- Deploy: copy the changed files from `car3d/project/` to `/root/lab/car3d/project/` (`cat file | ssh ... "cat > /root/lab/car3d/project/file"`).
- Parse check: `cd /root/lab/car3d; GD=/root/tools/godot/Godot_v4.4.1-stable_linux.x86_64; GODOT_SILENCE_ROOT_WARNING=1 $GD --headless --path project --check-only --script res://car_builder.gd`
  (after adding a new class_name file run `$GD --headless --path project --import` once).
- Quick test (N frames from frame S): `CAR3D_SS=2.0 D=/root/lab/ch3d/conv_SIM_POTHOLES_V2_S022 bash gr.sh 12 470` -> `t1.avi`, `t1_sheet.png`, `godot_t1.log`.
- Full episode: `CAR3D_SS=2.0 bash fullb.sh <episode_dir> /root/lab/car3d/<name>.mp4` (Godot render + compose with the original overlay, mix.wav and cold open); writes `fullb_done.log`.
- Lineup: `CAR3D_SS= bash lu.sh side|quarter [mood]` -> `lineup_side.png` / `lineup_quarter.png` (do NOT set CAR3D_SS for the lineup: the SubViewport is not supersampled, outlines would double).
- Game args: `godot --path project ... -- <episode_dir> <start_frame> builder` (third arg `builder` = 3D cast; a GLB dir = old Kenney mode; empty = the original card).
- Episode dirs with 2D export data: `/root/lab/ch3d/conv_SIM_*` (scene.json, frames.json, overlay.mov, mix.wav, meta.json, sprites/). Cast per episode: S026 police/bigrig/f1, S021 bumps sports/bus/monster, S022 taxi/icecream/firetruck, S025 f1/icecream/taxi, S027 f1/firetruck/bus, POTHOLES_S021 police/bigrig/sports. Grizzly (monster2) has no episode yet.

## 4. Godot / DeepSeek gotchas (learned the hard way)
- Front faces are CLOCKWISE: `_tri` emits a, c, b. The rounded `_prism` must include the side wall between the two chamfers.
- `inference_on_variant` is an error unless `gdscript/warnings/inference_on_variant=0` (set in project.godot); still declare `: float` for min/max/Dictionary values.
- `load()` cannot read `/root/.fonts/LuckiestGuy-Regular.ttf`: use `FontFile.load_dynamic_font`.
- Outline = screen-space inverted hull with SMOOTH normals stored in COLOR; width scales with `CAR3D_SS`.
- DeepSeek (flash) slips into Python tuples `(x, y)`, module-level assignments, multi-line PATCH anchors that do not match (give it single-line anchors), and drops helper functions when it rewrites a whole file: always check parse + grep the old fixes after a full-file reply.
- `ds_run.py` paths are relative to the CWD, not the repo: pass absolute `--brief`/`--out-dir`.

## 5. Open items (in the owner's order)
1. Owner review of v8 (two headlight beams) and any remaining characters that look off.
2. Camera: DONE as above (v10 = first full episode with the camera program); owner review pending.
3. Animated mood transitions (now an instant switch), panels tearing off the body itself (now only dents + flying pieces).
4. Promotion to production (needs the owner): the live converter is `video-engine/lab/godot3d_challenge/convert3d.py <video_id>`
   (export_challenge.py -> Godot -> compose.py). Promotion = put `car_builder*.gd` + the builder mode into that Godot project
   (or a generators/ copy), render NEW seeds only, QA, Drive review copy, owner approval, then the normal `episodes.py approve` + cron publish.
5. Parked: `../crash3d/` (own node-beam solver + Blender, see memory megawheel-crash3d-solver) and the Modal budget-guard block
   (118 unsettled MegaWheel reservations; never edit that ledger).
