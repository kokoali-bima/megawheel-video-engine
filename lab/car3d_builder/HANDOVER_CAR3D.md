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

---
## 6. UPDATE 2026-10-27/28 (latest state; read this first, it supersedes section 5)
Paused by the owner ("back to iPandu and iSmart-LA for a while"). Nothing is uploaded or queued; production repo untouched except AGENTS rule 5 (c77b621) and lab copies.

### Owner decisions in this round
1. TWO products:
   - **Shorts 9:16** = the v5 style (the aired 2D side camera, side diorama, eyes in the SIDE windows). This is the DEFAULT of `challenge3d.gd` builder mode (no env vars needed).
   - **Wide full video 16:9** = BeamNG-style cameras + Pixar "Cars" look (~65-70% is the target), eyes on the WINDSHIELD, mouth follows the mood (5 moods), no Challenge HUD.
     If it works it may REPLACE the weekly long video.
2. Every car must have a windshield (+ rear window) in both products (done: `project/face_front.gd`, `FaceFront.apply`).
3. Kenney Nature Kit rejected ("not mature, far from Cars"). Use **Quaternius Stylized Nature MegaKit (free Standard, CC0)** models + **Poly Haven (CC0)** PBR ground textures. TwistedTree models are excluded (red leaves).
4. No AI-generated video, ever. Real 3D physics like BeamNG (cars leaving the road, rolling sideways) needs a NEW Godot 3D physics engine (VehicleBody3D/Jolt) = stage 2, only if the wide prototype convinces.
5. GPU look (SDFGI, SSAO, volumetric fog, DOF) renders on **Modal, MegaWheel account**; owner extra allowance **US$12.5** (when spent, wait for next month). Not used yet (0 spent).
6. Re-exports must never overwrite running episodes: lab exports go to `/root/lab/car3d/eps/<id>` only.

### Env switches (all in `project/challenge3d.gd` + helpers)
| Var | Effect |
|---|---|
| (none) | Shorts v5: 2D camera, side faces, original side diorama |
| `CAR3D_CAM=program` | old hybrid 3/4 camera program (`CamProgram.pose`) + FrontWorld (kept, not the chosen Shorts style) |
| `CAR3D_CAM=beamng` | BeamNG tripod cameras (`CamProgram.beam_shot`): roadside tripod past each obstacle, front-side intro, replay from a second higher angle, orbit close-up of the wreck after FAIL, winner orbit; 3D speech bubbles (Label3D); dense nature (`NatureDress.dress`) and old cone trees stripped |
| `CAR3D_FACE=windshield` | Cars-movie face on the windshield + mouth on the front bumper (default `side`) |
| `CAR3D_DAY=1` | forces a sunny noon sky whatever the episode theme was |
| `CAR3D_WIDE=1` | camera keeps HEIGHT (16:9) |
| `CAR3D_SS=2.0` | 2x supersampling (CPU renders); outlines scale with it |
| `CAR3D_YAW`, `CAR3D_FRONT=1` | program-camera tuning / always-green front |

### Files added in this round (PC `car3d/` = source of truth; VM `/root/lab/car3d/`)
- `project/cam_program.gd` (`CamProgram`: pose, beam_shot, pois_from_scene, ground_y, ease helpers, FrontWorld)
- `project/face_front.gd` (`FaceFront`: windows + windshield face, moods named eyes_*/mouth_* under per-eye holders)
- `project/nature_dress.gd` (`NatureDress`: MegaKit bands near/mid/far both sides, Poly Haven triplanar ground, `strip_cone_trees`)
- `project/look_upgrade.gd` (`LookUpgrade`: Forward+ only; AGX/ACES, SSAO/SSIL/SDFGI, volumetric fog, glow, soft 4-split shadows, DOF; no-op on CPU)
- `modal_godot3d.py` (lab copy of the live `modal_godot.py`: app `megawheel-car3d`, font in the image, env.json carries CAR3D_* vars, passes `builder`, class cache shipped)
- `export_challenge_3d.py` (lab copy of export_challenge.py: `--no-bubbles` removes bubbles + speed lines from overlay.mov and writes `levels[].bubbles` into scene.json; ROOT pinned to /root/video-engine)
- `vm_scripts/wide.sh EPISODE_DIR OUT [N] [START]` (1920x1080 project copy `project_wide`, beamng+windshield+day+wide, audio from mix.wav)
- `beamng_ref/` (reference BeamNG videos 3VynaM2zSDU "Cars vs Potholes #4" 30M views and tJCHZOlPXeA cinematic crash test, contact sheets, `_pylib` yt-dlp + ffmpeg for the PC; YouTube blocks the VM IP)
- Assets on the VM (gitignored `assets/`): `/root/video-engine/assets/quaternius_nature` (glTF + Textures copied next to the .gltf), `/root/video-engine/assets/polyhaven` (asphalt_02, aerial_grass_rock, forest_ground_04, brown_mud_leaves_01, rock_face; 2k diff/nor_gl/rough), `/root/video-engine/assets/kenney_nature_kit` (rejected, unused).
- Lab export used for tests: `/root/lab/car3d/eps/S022` (seed 22 potholes, `--no-bubbles`; NOTE the sim differs a bit from the aired Ep because the registry changed since: fine for tests, new episodes must be exported this way from the start).

### Camera analysis (BeamNG vs ours, side by side, `beamng_ref/` sheets)
BeamNG: static roadside tripod ~4-5 m high, 12-15 m from the impact, looking diagonally down the road; car fills ~25-35% of a 16:9 frame; hard cuts per obstacle;
replay from a second higher angle; orbit close-ups of the wreck; dense roadside (grass, bushes, trees close to the road, tree shadows on asphalt, road markings, signs), daylight.
Ours (beamng v1): tripod 2.2 m high at z 6.5 (too low/close for 9:16; for 16:9 it reads better) -> TODO raise to ~4 m and pull back.

### Latest outputs
- Shorts 9:16: `samples/S026_car3d_v5.mp4` (owner's reference for the Shorts style), `S021bumps_car3d_v6.mp4`, `S022potholes_car3d_v8.mp4` (two headlight beams), `S022potholes_car3d_v9cam.mp4`.
- BeamNG camera 9:16 test: `samples/S022_beamng_v1.mp4`; VM `/root/lab/car3d/S022potholes_car3d_v10.mp4` (rejected hybrid camera).
- Wide 16:9 test (CPU, 160 frames): VM `/root/lab/car3d/wide_test.mp4`, sheet `wide1.png` (green MegaKit trees, Poly Haven ground, windshield face, mood mouths).

### NEXT STEPS (in order)
1. Wide video polish: ground texture too yellow/dry (tint `aerial_grass_rock` greener or switch to `forest_ground_04` mix); left side of the road sparser than the right; raise the tripod (~4 m) and pull back (~12 m) per the BeamNG analysis.
2. Windshield faces on CAB cars (police, taxi, monster): check from the front at full resolution (fixed the eye-node naming bug; verify).
3. First GPU test on Modal (MegaWheel): `modal_godot3d.py` with `project_gpu` (Forward+: `renderer/rendering_method="forward_plus"`, shadow 4096, soft quality 4). Run a 10 s piece first, read the real bill (`modal billing report --for today --json`), keep the total under US$12.5.
   Budget guard: `reconcile_budget.py` settled the 10 old reservations (backup `backups/ledger_before_reconcile_20261027.sqlite3`), but `modal_cli_preflight`/`reserve` still STOP with
   "Modal native workspace limits are above $31/unverified": policy.json says megawheel native limit 35 and the old preflight compares against `channel_month_usd` 31.
   Do NOT edit the ledger/policy without the owner: ask whether to set `native_channel_limits_usd.megawheel` to the real workspace limit or raise the cap by the US$12.5 allowance.
   Month spend so far (official): MegaWheel metered US$28.66 in Oct (credits cover it).
4. Then a full wide episode (S022 lab export) with audio; owner review; then cost per episode and the decision on the weekly long video.
5. Stage 2 (only after owner approval): Godot 3D vehicle physics (VehicleBody3D + Jolt) for real sideways crashes; reuse CarBuilder cars as the visual.
