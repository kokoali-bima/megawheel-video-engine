# CONTRACT: car3d, a real 3D car inside the aired Challenge Short (owner decision 2026-10-27)

Goal: keep EVERYTHING of the lava / potholes Challenge Short (world, HUD, physics, camera, audio, cold open) and replace ONLY the car:
the flat sprite card + 2D wheel discs in the Godot scene become a 3D model with 4 wheels (2 per side). Camera views are discussed later.
Live scene (VM): `/root/video-engine/lab/godot3d_challenge/project/challenge3d.gd` (copy in `ref/challenge3d.gd`); we work on a COPY under `/root/lab/car3d/project`.
Data per episode dir (e.g. `/root/lab/ch3d/conv_SIM_LAVA_POTHOLES_V2_S026`): `scene.json` (`cast[vk] = {body:[len,h], wheel_r, wheel_x[], w, h, ...}`, `S`=72, `ground_y`), `frames.json`.
Frame row indexes used: f[8]=cx f[9]=cy f[10]=ca (rad, about +Z) f[11]=ys f[12]=wheels [[x,y,rot],...] (world metres, rot about Z) f[14]=mood f[15]=broken f[16]=melt f[20]=crush.
Godot axes: x forward, y up, z toward the camera (camera at +z, tilted 7 degrees). Blender axes (cast3d): x forward, y lateral, z up. glTF export maps Blender (x,y,z) -> Godot (x, z, -y).

## Part 1 `export_cast_glb.py` (Blender script, runs `blender -b -P export_cast_glb.py -- --cast-dir DIR --ids sports,police,... --outdir OUT`)
`--cast-dir` = folder containing `cast3d.py` (put it on sys.path). Mapping vehicle id (vk) -> cast3d id from `characters.json` next to `cast3d.CAST_FILE` (`vehicle_id` -> `id`), e.g. police->siren, bigrig->titan, f1->nitro, sports->zippy, taxi->tilly.
For every requested vk: `root = cast3d.build(cid)` in a clean scene (`bpy.ops.wm.read_factory_settings(use_empty=True)` once per vehicle), then:
- Collect `wheelpivot_*` empties (cast3d.wheel_pivots(root)), each has `["radius"]` and a location in root space = wheel centre. Record all centres, `wheel_r` (first pivot radius) and `wheel_w` (tyre width = max extent of the tyre cylinder along Y, from the tyre object's dimensions).
- BODY file `<vk>_body.glb`: every MESH object under root that is NOT inside a wheel pivot (first convert CURVE/FONT objects to meshes with `bpy.ops.object.convert(target="MESH")`), exported with `bpy.ops.export_scene.gltf(filepath=..., export_format="GLB", use_selection=True, export_apply=True, export_yup=True, export_cameras=False, export_lights=False)`. The empty `root` and the wheel pivots are NOT exported.
- WHEEL file `<vk>_wheel.glb`: the content of ONE pivot with a NEGATIVE y location (the camera side), re-centred at the origin (move its children so the pivot centre is at (0,0,0), axle along Blender Y, i.e. along Godot Z), same export options.
- META file `<vk>_meta.json`: `{"vk":..,"cid":..,"wheel_r":..,"wheel_w":..,"wheels":[[x,y,z],..],"front_x":max wheel x,"rear_x":min wheel x,"hub_z":wheel z,"track_half":max |y| of wheel centres,"body_bbox":[[minx,miny,minz],[maxx,maxy,maxz]] (Blender coords, body objects only, world space)}`.
Print one line per vehicle: `[export] <vk> body=<bytes> wheel=<bytes>`.

## Part 2 Godot patch (task T8) on `project/challenge3d.gd` (copy of the live script)
GLB files exist per vehicle in a folder (`glb/<vk>_body.glb`, `<vk>_wheel.glb`, `<vk>_meta.json`, meta keys as in Part 1; the body GLB is already in Godot axes: x forward, y up, z toward the camera for Blender -y).
Enable: a cmdline user arg #3 (index 2) = glb folder; when absent the script behaves exactly as before (card + sprite wheels). Args today: `[dir, start_off]`.
New code (keep it in small functions, GDScript 4.4, tabs):
- `_load_glb(path) -> Node3D`: `GLTFDocument.new()`, `GLTFState.new()`, `append_from_file(path, state)` (check `OK`), `generate_scene(state)`; returns null on error. Every `MeshInstance3D` found recursively gets `cast_shadow = SHADOW_CASTING_SETTING_ON`.
- `_car3d_setup(vk)` called from the existing `if vk != cur_vk:` block (after `_body_mesh(vk)`): frees the previous 3D nodes, loads `meta` (JSON) and the two GLBs, creates `car3d_body` (the body node, added as child of this scene root) and, for every engine wheel `k` in `cast[vk]["wheel_x"]`, two wheel instances (near, far; each `_load_glb` of the wheel file, added to the scene root). Stores `car3d_meta`.
- `_update_car3d(f, vk, ys, melt, crush, broken, wl)` called at the end of the car block of `_process` (just after the existing wheel loop). Math (all in the car frame, then rotated by `ca = float(f[10])` about Z and moved by the car position `(float(f[8]), float(f[9]))`):
  `wx = cast[vk]["wheel_x"]` (engine local x of each wheel), `ex_f = max(wx)`, `ex_r = min(wx)`, `s = (ex_f - ex_r) / (meta.front_x - meta.rear_x)`, `mx = (meta.front_x + meta.rear_x) / 2`.
  Engine hub height in the car frame: `h_e` = mean over wheels k of `dot(Vector2(wl[k][0] - cx, wl[k][1] - cy), Vector2(-sin(ca), cos(ca)))`.
  Body: `rot = Basis(Vector3(0,0,1), ca)`; `local = Vector3((ex_f + ex_r)/2 - s*mx, h_e - s*meta.hub_z, 0)`; `car3d_body.position = Vector3(cx, cy, 0) + rot * local`; `car3d_body.rotation = Vector3(0, 0, ca)`; `car3d_body.scale = Vector3(s*ys*(1.0 + 0.2*crush), s*(1.0 - 0.32*melt)*(1.0 - 0.5*crush), s)`. (`ys`, `melt`, `crush` as already used for the card.)
  Wheels: for `k < wl.size()`: near position `Vector3(wl[k][0], wl[k][1], s*meta.track_half)`, far `Vector3(wl[k][0], wl[k][1], -s*meta.track_half)`, both `rotation = Vector3(0, 0, float(wl[k][2]))`, `scale = Vector3(s, s, s)`.
  Visibility: when 3D is enabled hide the card (`body.visible = false`) and the 2D wheel pivots (`wheel_pivots[k].visible = false`, each frame, after the existing code sets them); the 3D body and wheels are visible only when `not broken` and `abs(ys) >= 0.25` (wheels: also `k < wl.size()`). `_break(...)` keeps spawning its sprite shards as today.
- The blob contact shadow, smoke, fire, headlights, impacts, dents (`dmg`) logic stay untouched (dents apply to the hidden card only in this first version).

## Part 1b `export_kenney_glb.py` (replaces cast3d boxes by Kenney Car Kit 3.1 models, CC0; owner: the box cars look ugly)
Run: `blender -b --python-use-system-env -P export_kenney_glb.py -- --kit "/root/video-engine/assets/kenney_car_kit/Models/GLB format" --ids police,taxi,... --outdir glb2` (PYTHONPATH gives numpy to the glTF exporter).
Kenney files: root-level meshes `body` (children like `grill`, `spoiler`), `wheel-front-left`, `wheel-front-right`, `wheel-back-left`, `wheel-back-right`, one material `colormap`. After `bpy.ops.import_scene.gltf` Blender axes: the FRONT of the car points to -Y, up is +Z, x is lateral. We want front = +X: rotate the whole car by +90 degrees about Z (x,y) -> (-y,x), then the camera-side wheels are those with y < 0.
Vehicle table (vk -> kenney file, eye spec `(x_frac_a, x_frac_b, z_frac, radius_frac)` relative to the body bbox AFTER rotation: x = bbox_min_x + frac*length, z = bbox_min_z + frac*height, eye radius = radius_frac*height): 
`sports: sedan-sports (0.40,0.58,0.62,0.12)`, `police: police (0.40,0.58,0.62,0.12)`, `taxi: taxi (0.40,0.58,0.64,0.12)`, `firetruck: firetruck (0.62,0.80,0.66,0.12)`, `f1: race-future (0.30,0.42,0.80,0.14)`, `bigrig: delivery (0.62,0.80,0.66,0.11)`, `bus: van (0.40,0.58,0.62,0.12)`, `icecream: van (0.40,0.58,0.62,0.12)`, `monster: suv (0.40,0.58,0.64,0.12)`.
Eyes: two eyes on the CAMERA-SIDE body face (y = bbox_min_y + 0.02 outward, i.e. slightly in front of the side window plane), each = white UV sphere squashed along Y (scale (1,0.35,1)) + black pupil sphere (0.5 radius, scale (1,0.4,1)) shifted +x by 0.25*radius and a tiny white glint; materials simple Principled (no textures). They belong to the BODY object set (exported with the body).
Outputs per vk (same names and meta keys as Part 1, so Part 2 works unchanged): `<vk>_body.glb` (rotated body + children + eyes, wheels excluded), `<vk>_wheel.glb` (the wheel with y<0 centred at the origin, axle along Y), `<vk>_meta.json` with wheel centres `wheels` (after rotation), `wheel_r` = wheel diameter/2 (from the wheel object dimensions: max of its dims / 2), `wheel_w` = min dim, `front_x`, `rear_x`, `hub_z` (wheel z), `track_half` (max |y|), `body_bbox`, plus `"source": "kenney car-kit 3.1 CC0"`.
Print `[export] <vk> body=<bytes> wheel=<bytes>` per vehicle. Clean scene per vehicle (`read_factory_settings(use_empty=True)`).

## Part 3 stylised look (2026-10-27; owner: "still far, the shape must be right and pleasant to look at")
Diagnosis from the v2 frames: jagged edges (msaa_3d=0), no outline (the 2D sprites have a dark outline), pastel colours under the scene light, low-slung proportions, tiny eyes.
In `project/challenge3d.gd` add `_stylize_car3d(root: Node3D, outline: float)`; it is called from `_car3d_setup` on the body node and on every wheel node right after `_load_glb` (outline thickness argument in MODEL units: `0.035 / s` for the body where `s` is the scale used for that vehicle, `0.035 / ws` for wheels; compute the same numbers `_update_car3d` uses: `s = (ex_f - ex_r)/(front_x - rear_x)`, `ws = cast[vk]["wheel_r"]/meta.wheel_r*1.25`).
For each `MeshInstance3D` under `root` (recursive) and each surface `i`: take `m = mi.get_active_material(i)` (a `BaseMaterial3D` from the glTF: read `albedo_texture`, `albedo_color`, `emission_enabled`, `emission`, `emission_energy_multiplier`), build a `ShaderMaterial` with the TOON shader below, copy those values into its uniforms, set `sm.next_pass` to a `ShaderMaterial` with the OUTLINE shader, and `mi.set_surface_override_material(i, sm)`. Outline uniform `centre` = the mesh AABB centre in model space (`mi.get_aabb().get_center()`), `thickness` = the `outline` argument.
TOON shader (exact):
```
shader_type spatial;
render_mode diffuse_toon, specular_toon;
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap, repeat_enable;
uniform bool use_tex = false;
uniform vec4 albedo_col : source_color = vec4(1.0);
uniform vec4 emission_col : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float emission_energy = 0.0;
uniform float sat = 1.5;
uniform float contrast = 1.15;
void fragment() {
	vec3 c = albedo_col.rgb;
	if (use_tex) { c *= texture(albedo_tex, UV).rgb; }
	float l = dot(c, vec3(0.299, 0.587, 0.114));
	c = mix(vec3(l), c, sat);
	c = clamp((c - 0.5) * contrast + 0.5, 0.0, 1.0);
	ALBEDO = c;
	ROUGHNESS = 0.55;
	SPECULAR = 0.3;
	RIM = 0.35;
	RIM_TINT = 0.4;
	EMISSION = emission_col.rgb * emission_energy;
}
```
OUTLINE shader (exact; radial expansion because the low-poly normals are flat and would crack at the corners):
```
shader_type spatial;
render_mode cull_front, unshaded;
uniform float thickness = 0.03;
uniform vec3 centre = vec3(0.0);
uniform vec4 line_col : source_color = vec4(0.06, 0.04, 0.08, 1.0);
void vertex() { VERTEX += normalize(VERTEX - centre) * thickness; }
void fragment() { ALBEDO = line_col.rgb; }
```
Also in `_update_car3d` the wheel size factor becomes `* 1.25` instead of `* 1.12`. `project/project.godot`: `anti_aliasing/quality/msaa_3d=2`.

## Part 1c `export_bigrig_glb.py` (Titan, built in ENGINE metres: s = 1 in Godot)
Run like Part 1b. Source: Kenney `delivery-flat.glb` (orange-red cab + grey flat bed; front = -Y after import). Steps (Blender axes, after the +90 degree rotation about Z so the front is +X, same helper logic as `export_kenney_glb.py`):
1. Import, rotate front to +X, scale the whole car by 1.35 about the origin, then translate so the cab centre sits at x = 3.0 (cab = the front half of the model) and the wheels touch z = 0 plus nothing else (wheel centre z = 0.3*1.35 = 0.405; keep it).
2. Remove nothing but the four wheel objects (they go to the wheel file as in Part 1b: the camera side wheel y<0, re-centred at the origin).
3. Add a TRAILER: a bevelled box (Bevel modifier 0.08, segments 3, applied) of size (7.4, 2.5, 2.6) centred at (-1.9, 0, 0.9 + 1.3) (so it sits above the chassis: bottom at z = 0.9, top at 3.5), white material `Principled` base colour (0.93, 0.93, 0.95), roughness 0.6. A thin dark-grey chassis box (7.0, 1.6, 0.25) at (-1.9, 0, 0.78) under it, and a text object "MEGA HAUL" (default Blender font, size 0.8, extrude 0.02, blue (0.05,0.25,0.75), rotated to read on the camera side y = -1.27, i.e. rotation (90deg, 0, 0), centred at x=-1.9, z=2.2) converted to a mesh.
4. Eyes on the cab side as in Part 1b (white + black pupil, camera side, radius 0.3, centres at x = 2.7 and 3.5, z = 2.1, y = -(cab half width)-0.02).
5. Export BODY GLB (cab + trailer + chassis + text + eyes, no wheels), WHEEL GLB, META JSON with: `"front_x": 3.8, "rear_x": -4.0, "hub_z": 0.75, "track_half": 1.05, "wheel_r": 0.405, "wheel_w": 0.4, "yz_k": 1.0, "wheels": [[3.8,-1.05,0.75],[3.8,1.05,0.75],[-4.0,-1.05,0.75],[-4.0,1.05,0.75]]` (these override the measured values on purpose: the engine wheel positions are the truth and the model is built in engine metres). Output names `bigrig_body.glb`, `bigrig_wheel.glb`, `bigrig_meta.json` in `--outdir`.

## Part 1d full cast (9 Kenney based characters + the Titan of Part 1c), 2026-10-27
Extend `export_kenney_glb.py` (PATCH). Replace the `VEHICLES` eye-only table by an ENGINE table; for each vk the exporter computes the Godot-side numbers itself so nothing is hand-edited on the VM any more:
```
ENGINE = {   # kenney file, engine wheelbase wb (m, max-min wheel_x of sim_engine), target body height h (m, from the model bottom incl. cabin, WITHOUT lift), recolor rgb 0-255 or None, lift (m, body raised above the axle), eye spec (x_frac_a, x_frac_b, z_frac, radius_frac)
 "sports":   ("sedan-sports", 2.75, 1.35, (237, 41, 46),  0.0, (0.38, 0.62, 0.64, 0.17)),
 "police":   ("police",       2.90, 1.60, None,           0.0, (0.38, 0.62, 0.64, 0.17)),
 "taxi":     ("taxi",         2.80, 1.60, None,           0.0, (0.38, 0.62, 0.66, 0.17)),
 "f1":       ("race-future",  3.30, 1.00, None,           0.0, (0.28, 0.44, 0.84, 0.17)),
 "firetruck":("firetruck",    4.10, 3.10, None,           0.0, (0.58, 0.82, 0.68, 0.15)),
 "bus":      ("van",          4.80, 3.00, (255, 199, 13), 0.0, (0.55, 0.80, 0.66, 0.15)),
 "icecream": ("van",          3.80, 2.80, (255, 153, 194),0.0, (0.55, 0.80, 0.66, 0.15)),
 "monster":  ("suv",          3.50, 1.70, (31, 115, 242), 0.9, (0.38, 0.62, 0.66, 0.17)),
 "monster2": ("suv-luxury",   3.50, 1.70, (51, 184, 64),  0.9, (0.38, 0.62, 0.66, 0.17)),
}
```
Computed meta (written into `<vk>_meta.json`, in addition to the existing keys): `s = wb / (front_x - rear_x)` (model wheelbase after the rotation), `yz_k = h / ((body_bbox max z) * s)` (so the scaled body is `h` tall), and if `lift > 0`: `hub_z = -(lift) / (s * yz_k)` (the body floats `lift` metres above the axle line; the Godot formula `local.y = h_e - s*yz_k*hub_z` then raises it), else the measured `hub_z`. Keep `wheel_r`, `wheel_w`, `track_half` measured.
RECOLOR (`_recolor_paint(body_objs, target_rgb)`): find the body paint colour = for every face of the body objects (mesh polygons) take the UV centre, sample the colormap image there (the image of the first material image texture node), and pick the colour with the largest `area * saturation` among samples with saturation > 0.3; call it `paint`. Then rewrite the image: convert every pixel to HSV; for pixels with `|hue - paint_hue| < 0.06` (circular) and `sat > 0.25`: set `hue = target_hue`, `sat = min(1, sat * target_sat / paint_sat)`, `val = min(1, val * target_val / paint_val)`; write back to `image.pixels`, then `image.update()` and `image.pack()`. The images are shared by the materials of that scene only (clean scene per vehicle), so no cross contamination. Use numpy for the pixel maths (bundled with Blender; the run uses PYTHONPATH numpy).
TOPPER for `icecream` (after the body bbox is known): add a vanilla cone + two scoops on the roof, camera-side visible: cone = `primitive_cone_add(radius1=0.32, depth=0.9)` pointing UP at the roof centre (x = bbox centre, y = 0, z = bbox max z + 0.45), colour (0.85, 0.62, 0.32); scoops = two UV spheres radius 0.36 (pink (1.0,0.55,0.75), white (0.98,0.95,0.9)) stacked above the cone tip; they join the body export.
Keep: eyes as before (white + black pupil + glint, camera side), clean scene per vehicle, the per-vehicle print line, `--ids` list handling (`all` = every key of ENGINE). Do not touch the bigrig (separate file).
