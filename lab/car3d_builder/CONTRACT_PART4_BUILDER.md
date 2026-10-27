# CONTRACT Part 4: `car_builder.gd`, the ORIGINAL MegaWheel characters rebuilt in 3D inside Godot (owner 2026-10-27)

Owner: "an upgrade must be better than the original, not a downgrade". Kenney cars lost the identity of the cast.
So we rebuild EXACTLY the 2D designs of `sim_engine.draw_body / draw_face / draw_wheel` (copy in `ref/sim_engine_draw.py`)
as 3D toys: every 2D shape becomes an extruded prism with a chamfer, every shape keeps its own dark outline
(like `fill_stroke`), the face lives in the side windows on BOTH sides, the 5 moods animate per frame.

## Coordinates
Car-local metres, exactly the 2D drawing frame: origin = body centre (the engine's car position), +x = front, +y = up.
The 3D depth axis is z (Godot): z > 0 is the camera side. Everything is built in metres at scale 1 (no fitting).

## Materials (reuse the game shaders)
`CAR_TOON_SHADER` (uniforms `albedo_col`, `use_tex=false`, `emission_col`, `emission_energy`, `sat`, `contrast`) and
`CAR_OUTLINE_SHADER` (uniforms `thickness`, `centre`, `line_col`) are copied verbatim from `project/challenge3d.gd`.
`_mat(color: Color, outline: bool, emission := 0.0) -> ShaderMaterial`: toon material, `next_pass` = outline material
when `outline` (thickness 0.03 m, `line_col` = Color(0.1, 0.08, 0.12)); cache materials by (color, outline, emission).
The outline `centre` uniform must be set per mesh instance to its AABB centre: use `set_instance_shader_parameter`
is NOT available for next_pass in Compatibility, so create one outline material per mesh instance (do not cache the outline pass).

## Geometry helpers (SurfaceTool, flat shading, CCW polygons; reverse a polygon if `Geometry2D.is_polygon_clockwise`)
- `_rrect_pts(x, y, w, h, r, seg := 5) -> PackedVector2Array` (same corners as cairo `rrect`), `_circle_pts(cx, cy, r, seg := 24)`.
- `_prism(pts, z0, z1, bevel, mat) -> MeshInstance3D`: front face at z1 and back face at z0 are the polygon shrunk by
  `bevel` (`Geometry2D.offset_polygon(pts, -bevel)[0]`, fall back to `pts` when the offset fails or bevel = 0), the side
  walls run between the full polygon at `z0 + bevel` and `z1 - bevel`, and a chamfer strip joins each shrunk face to the
  full polygon ring (when bevel = 0 the walls go straight from z0 to z1). Triangulate faces with `Geometry2D.triangulate_polygon`.
  Normals: `st.generate_normals()` after `st.index()` is NOT wanted (it smooths); compute flat normals per triangle.
- `_slab(pts, half, mat)` = `_prism(pts, -half, half, 0.0, mat)` (decals/glass: thin, sharp).
- `_tube(points: PackedVector3Array, radius, mat)`: 8-sided tube along the points (mouth arcs, brows, ladder rails are boxes instead).
- `_box(x0, y0, x1, y1, z0, z1, mat)`, `_sphere(c: Vector3, r: Vector3 /* radii x,y,z */, mat)` (SphereMesh scaled), `_cone(...)` for the ice cream.
- `_label(text, at: Vector2, size, color, z)`: two `Label3D` (one at +z facing +z, one at -z rotated 180 degrees about Y so it reads
  correctly from the far side), font = `FontFile` loaded from `/root/.fonts/LuckiestGuy-Regular.ttf` (fallback: default font),
  `font_size = 96`, `pixel_size = size / 96.0 * 1.25`, `outline_size = 0`, `shaded = false`, `double_sided = false`, `no_depth_test = false`, `modulate = color`.

## Z classes (per vehicle half-widths, metres)
`B` body, `C` cabin, `R` roof items, `W` wings (f1/spoiler), `K` chassis. Layer kinds:
- `body`/`cabin`/`roof`/`wing`/`chassis`: `_prism(pts, -X, X, bevel, mat(fill, outline=true))` with X = that half-width; bevel = 0.06 for body/cabin, 0.03 otherwise.
- `decal_body` / `decal_cabin`: `_slab(pts, X + 0.015, mat(fill, outline))` (sits just outside that surface on both sides).
- `glass_body` / `glass_cabin`: like decal with fill = glass (0.62, 0.86, 1.0), outline true.
- `pair Z`: two `_prism(pts, ±Z - 0.06, ±Z + 0.06, 0.02, ...)` (spoiler posts, exhaust stacks).
- `centre H`: `_prism(pts, -H, H, 0.02, ...)`.
Lamps (cairo circles r at (x, y) near the front): two spheres radius 1.15*r, colour (1, 0.95, 0.4), emission 1.5, at
`(x + r*0.6, y, ±0.62*B)` and an outline.

## Faces (from FACES; `on` = which half-width the eye sits on) and moods (port of `draw_face`)
Eye white: sphere radii (rr, rr*1.25, rr*0.45) centred at `(ex, ey, ±(S + rr*0.15))` where S = the surface half-width (+ 0.03),
rr = r * big (big: scared 1.25, whoa 1.45, else 1). Pupil: black sphere radii (rr*pr, rr*pr, rr*pr*0.5) on the outer surface of the
white (`z = ±(S + rr*0.15 + rr*0.4)`), offset (rr*px, rr*0.1); glint: white sphere radius rr*pr*0.32 offset +rr*pr*0.35 in x and y,
slightly further out. pr/px: normal 0.5/0.35, scared 0.25/0.2, whoa 0.38/0.0. Dizzy: no pupil; two crossing ink tubes (from
`(ex - 0.6r, ey ∓ 0.6r)` to `(ex + 0.6r, ey ± 0.6r)`, radius 0.17r) on the white. Happy: no white; an ink tube arc (centre (ex, ey - 0.2r),
radius 0.75r, angles 0.15π..0.85π, tube radius 0.2r). Scared/whoa brows: ink tube from `(ex - 0.8r, ey + r*lift - tilt*r)` to
`(ex + 0.8r, ey + r*lift + tilt*r)` (lift whoa 1.75 / scared 1.55; tilt scared ±0.25 (first eye +, second −), whoa 0), tube radius 0.15r.
Scared sweat drop: light-blue sphere radii (0.6r, 0.9r, 0.3r) at `(ex0 - 2.4r, ey0 + 0.9r + 0.05 sin(12t))`.
Mouth at (mx, my), width mw, on the body surface (S = B + 0.03): normal = ink tube arc centre (mx, my + 0.3mw), radius 0.5mw,
angles 1.2π..1.8π (cairo y is up here, so this is a smile), tube radius 0.08mw; scared = white rounded slab (mw x 0.44mw) with 3 ink
vertical tubes + a horizontal one; whoa = dark-red (0.45, 0.05, 0.1) ellipse sphere radii (0.26mw, 0.32mw, 0.08); happy = dark-red half
disc slab (polygon of the lower half circle radius mw/2 at (mx, my + 0.1mw)) + pink (1, 0.45, 0.5) disc at (mx, my - 0.22mw) r 0.18mw;
any other mood = ink zig-zag tube (7 points). Every face part exists on both sides (+z and −z), mirrored.
Implementation: build all mood variants once per side under named child nodes (`eyes_normal`, `eyes_scared`, ..., `mouth_normal`, ...)
and `set_mood(root, mood, t)` toggles `visible`; moods `broken` -> show `dizzy`; unknown -> `normal`. `set_mood` also flashes lights:
police bar: red lit when `int(t*6) % 2 == 0`, blue lit otherwise (lit = full colour + emission 2.0, unlit = colour*0.45, no emission);
fire truck roof light red/dark the same way. Store the flashing mesh instances in `root.set_meta("flash", [...])`.

## Wheels (`wheel(vk) -> Node3D`, port of `draw_wheel`, axle along z, spins with `rotation.z`)
Tyre: cylinder radius r, height (width) tw, colour (0.12, 0.12, 0.14), outline. Hub: cylinder radius 0.55r, thickness 0.05, colour
(0.78, 0.78, 0.84), outline, centred on the OUTER face (+z side of the wheel node: z = tw/2 + 0.01). 5 spokes: boxes from radius 0.15r to
0.5r, width 0.1r, colour (0.35, 0.35, 0.4), at the hub face; centre cap radius 0.16r colour (0.25, 0.25, 0.3). Monster: 18 lug boxes
(radial 0.86r..1.06r, tangential 0.14r, full tw) colour (0.2, 0.2, 0.22). The far-side wheel is the same node rotated 180 degrees about Y
by the caller. Cylinder axis: CylinderMesh is along Y, rotate it 90 degrees about X.

## Public API
`static func build(vk: String) -> Node3D` (root node, children = all layers + face sets), `static func wheel(vk: String) -> Node3D`,
`static func set_mood(root: Node3D, mood: String, t: float) -> void`, `static func track_half(vk) -> float`. File `project/car_builder.gd`,
`class_name CarBuilder`, `extends RefCounted`.

## Vehicle data (transcribe EXACTLY from `ref/sim_engine_draw.py`, `draw_body` branch per vehicle; `c` = VEHICLES color, `dark` = c*0.65)
Half-widths and wheels: `sports B .95 C .72 W .85 track .80 tw .30`; `police B 1.0 C .80 R .45 track .85 tw .30`; `taxi B 1.0 C .80 R .35 track .85 tw .30`;
`monster/monster2 B 1.1 C .9 R .5 track 1.15 tw .75 (monster wheels)`; `f1 B .42 W .9 track .85 tw .38`; `bus B 1.25 track 1.05 tw .40`;
`firetruck B 1.25 R .5 track 1.05 tw .40`; `bigrig B(trailer) 1.3, cab 1.25, K .9, track 1.05 tw .40`; `icecream B 1.2 track 1.0 tw .40`.
Colours: sports (0.93,0.16,0.18), police (0.96,0.96,0.98), taxi (1,0.8,0), monster (0.12,0.45,0.95), monster2 (0.2,0.72,0.25), f1 (0.1,0.55,0.95),
bus (1,0.78,0.05), firetruck (0.88,0.1,0.1), bigrig cab (0.95,0.42,0.1), icecream (1,0.6,0.76).
Layer kinds per vehicle (shape coordinates = the reference file):
- sports: cabin poly→`cabin`; glass poly→`glass_cabin`; body poly→`body`; white stripe rect→`decal_body` (no outline); spoiler post poly→`pair 0.6` (dark); spoiler wing poly→`wing` (dark); lamp (1.95, 0.02, r .09). Face: eyes on `C`.
- police: cabin→`cabin`; glass→`glass_cabin`; pillar line x=-0.35 y .4..0.86 → `decal_cabin` box 0.05 wide (dark (0.1,0.08,0.12), no outline); body→`body`; dark panel poly→`decal_body` (0.1,0.12,0.2) outline; text POLICE (-0.05,-0.02) 0.26 white on `B`; light bar two rrects→`roof` (flashing red (1,0.15,0.15) / blue (0.15,0.4,1)); lamp (2.05,0.05,r .09). Eyes on `C`.
- taxi: cabin, glass, pillar x=-0.33, roof sign rrect→`roof` (1,1,0.85) + text TAXI (-0.44,1.06) 0.15 dark (0.1,0.1,0.1) at z = R + 0.03; body; checker 16x2 cells→`decal_body` no outline (dark (0.1,0.1,0.1) / white alternating exactly as the loop); lamp (2.0,0.08). Eyes on `C`.
- monster & monster2: cabin, glass, body, flame poly→`decal_body` fill (1,0.6,0.1) outline colour (0.9,0.2,0.1) (use a dedicated outline colour), 3 roof lights rects→`roof` (1,0.85,0.2) emission 0.8; lamp (2.02,0.08,r .1). Eyes on `C`.
- f1: rear wing rrect→`wing` dark; post rect→`centre 0.08` (0.15,0.15,0.18); body poly→`body` (B .42); white stripe→`decal_body` no outline; helmet = sphere (−0.35, 0.42, 0) radius .21 colour (1,0.85,0.1) outline; visor = box x −0.3..−0.1, y .36..0.46, z −0.16..0.16 colour (0.1,0.1,0.15); front wing rrect→`wing` dark; text "1" (−1.05,0.03) 0.3 white on `B`. Eyes on `B` (r .1), mouth (1.95,−0.1) mw .22.
- bus: body rrect→`body` (bevel 0.1); black stripe rect→`decal_body` no outline (0.1,0.1,0.1); 6 windows→`glass_body`; front window→`glass_body`; text SCHOOL BUS (−0.7,−0.7) 0.42 (0.1,0.1,0.1); 2 bumper rects→`centre 1.15` (0.15,0.15,0.15); lamp (3.55,−0.35,r .11). Eyes on `B`.
- firetruck: body rrect→`body`; front window→`glass_body`; white stripe→`decal_body` no outline; 4 side windows→`decal_body` fill c*0.8 outline; ladder: two racks at z = ±0.55, each = 2 rail boxes (x −3.0..1.4, y = 1.02 and 1.28, thickness 0.07 in y, 0.07 in z) + 12 rung boxes (x = −2.9 + i*0.37, y 1.02..1.28, 0.06 thick), colour (0.75,0.75,0.8), plus 3 support posts (x −2.6, −0.8, 1.0; y 0.95..1.02) per rack; roof light rrect→`roof` flashing red; text FIRE (−0.9,−0.72) 0.32 white; lamp (3.05,−0.4,r .11). Eyes on `B`.
- bigrig: trailer rrect→`body` with B=1.3 colour (0.9,0.9,0.94) bevel 0.08; 6 ribs = boxes 0.04 wide x = −4.8 + i*1.04, y −0.9..1.15, `decal_body` (0.75,0.75,0.8) no outline; text MEGA HAUL (−1.15,0.15) 0.55 (0.12,0.3,0.7) on 1.3; chassis rect→`chassis` K .9 (0.2,0.2,0.24); exhaust stack = cylinder radius 0.08 from y 0.85 to 1.6 at x 2.87 at z = ±1.0 (0.7,0.7,0.75) outline; cab poly→prism ±1.25 colour c bevel 0.08; cab window rrect→glass at ±1.25; grille rect→ `decal` at ±1.25 (0.25,0.25,0.28); lamp (4.68,−0.12,r .1) with B = 1.25. Eyes on 1.25.
- icecream: body rrect split at y = −0.55 into the upper part (colour c) and the lower band (accent (0.6,0.95,0.8)) with `Geometry2D.intersect_polygons` against a big rectangle above/below the split, both `body`; serving window→`glass_body`; awning 8 rects→`decal_body` no outline alternating (1,0.35,0.55)/white; front window→`glass_body`; text ICE CREAM (−0.85,−0.8) 0.34 (0.55,0.1,0.35); roof cone: cone radius 0.35 at the top (y 1.95) to a point at y 1.05, colour (0.85,0.62,0.3), outline; scoop sphere (0, 2.1, 0) r .42 (1,0.85,0.9); cherry (0, 2.55, 0) r .12 (0.9,0.1,0.2); lamp (2.65,−0.35,r .1). Eyes on `B`.
Faces (eyes, r, mouth, mw) = FACES in the reference file (monster2 = monster).

## QC
A lineup render in pure side view (orthographic) is compared by eye with `ref2d_sheet.png`: same silhouettes, colours, decals, face
positions. A second render at a 3/4 view shows the depth. Then the game render.

## Part 4b polish (owner 2026-10-27: "some parts are still not smooth"), measured on 1:1 crops of the v4 videos
1. Ink outline like the 2D stroke: constant SCREEN-SPACE width, crack-free. Every SurfaceTool mesh stores a SMOOTH normal per
   vertex in the COLOR attribute (`n * 0.5 + 0.5`): after `st.commit_to_arrays()`, group vertices by position (key = position
   rounded to 1e-4), average the (area-weighted) face normals of the group, write ARRAY_COLOR, keep the flat ARRAY_NORMAL for shading,
   build with `ArrayMesh.add_surface_from_arrays`. Primitive meshes (SphereMesh, CylinderMesh) use their own smooth NORMAL.
   New OUTLINE shader (replaces the radial one everywhere in car_builder.gd; keep the old constant name):
```
shader_type spatial;
render_mode cull_front, unshaded;
uniform float width_px = 3.5;
uniform bool use_color_normal = true;
uniform vec4 line_col : source_color = vec4(0.1, 0.08, 0.12, 1.0);
void vertex() {
	vec3 n = use_color_normal ? normalize(COLOR.rgb * 2.0 - 1.0) : normalize(NORMAL);
	vec4 clip = PROJECTION_MATRIX * (MODELVIEW_MATRIX * vec4(VERTEX, 1.0));
	vec3 vn = normalize(mat3(MODELVIEW_MATRIX) * n);
	vec2 off = (PROJECTION_MATRIX * vec4(vn, 0.0)).xy;
	float len = length(off);
	if (len > 1e-5) { off /= len; }
	clip.xy += off * width_px * 2.0 / VIEWPORT_SIZE * clip.w;
	POSITION = clip;
}
void fragment() { ALBEDO = line_col.rgb; }
```
   Width: 3.5 px for bodies/cabins/wheels, 2.0 px for small parts (eyes, pupils, lamps, decals, labels have none). `_finish(mi)` sets
   `use_color_normal` = true only when the mesh is an ArrayMesh built by our helpers (it has ARRAY_COLOR), false for primitive meshes.
   The outline material must NOT be shared between a COLOR mesh and a primitive mesh (one outline material per mesh instance, as now).
2. Rounded bevel: `_prism(pts, z0, z1, bevel, mat, segs := 3)`: the chamfer becomes a quarter-round with `segs` rings: ring k (0..segs)
   has angle t = k/segs * PI/2, inset `bevel * (1 - cos(t))` (via `_inset`) and z = `z1 - bevel + bevel * sin(t)` (front) /
   `z0 + bevel - bevel * sin(t)` (back); ring 0 is the wall edge, ring segs is the face polygon. Default bevels: body/cabin 0.12,
   roof/wing/chassis 0.05, pairs/centre 0.03 (update the callers' numbers accordingly; never more than 35% of the smaller of
   (z1 - z0)/2 and the polygon's minimum width, clamp it).
3. Segments: SphereMesh radial_segments 32, rings 16; CylinderMesh radial_segments 48 (tyres, hubs, stacks).

## Part 4c 3D damage (owner "gas", 2026-10-27)
1. Dents. Both shaders (toon and outline) get the same deformation, applied to VERTEX first in `vertex()` (the toon shader gets a
   `vertex()` function; the outline applies it before computing `clip`):
```
uniform vec3 dent_c = vec3(0.0);
uniform float dent_r = 1.0;
uniform float dent_k = 0.0;
// in vertex():
vec3 dv = VERTEX - dent_c;
float dw = dent_k * (1.0 - smoothstep(0.0, dent_r, length(dv)));
VERTEX -= dv * dw * 0.45;
```
   `static func set_damage(root: Node3D, center: Vector3, radius: float, amount: float) -> void`: for every MeshInstance3D under root whose
   transform relative to root is identity (the prisms/slabs/boxes built in car-local coordinates), set `dent_c/dent_r/dent_k` on its
   `material_override` and on its `next_pass`. (Toon materials are cached per colour; the dent values are re-set every frame by the game,
   so sharing is acceptable.)
2. Cracks (the `if broken:` block of `draw_body`): table `BODY_DIMS := {"sports": Vector2(4.2, 0.62), "police": Vector2(4.4, 0.7), "taxi": Vector2(4.3, 0.7),
   "f1": Vector2(4.6, 0.45), "monster": Vector2(4.3, 0.9), "monster2": Vector2(4.3, 0.9), "bus": Vector2(7.4, 2.1), "firetruck": Vector2(6.4, 1.9),
   "bigrig": Vector2(9.6, 2.3), "icecream": Vector2(5.6, 2.2)}`. In `build(vk)`, after the vehicle build, add a node "cracks" (hidden) with,
   on both sides (z = ±(S + 0.02) where S = the max z of the merged AABB of the root's identity-transform meshes), two ink tubes (radius 0.025):
   start (sx, sy) and points (sx + px, sy + py) exactly as the reference: crack 1 start (-bw*0.2, 0) points (0.2,0.15) (0.35,-0.05) (0.55,0.12);
   crack 2 start (bw*0.18, -bh*0.15) points (0.15,-0.12) (0.3,0.05) (0.5,-0.1). `set_mood`: "cracks" visible only when mood == "broken".
3. Debris: `static func body_color(vk) -> Color` (the vehicle colour of the contract; bigrig = trailer white (0.9,0.9,0.94) 50% / cab orange) and
   `static func debris(vk: String, rng: RandomNumberGenerator) -> MeshInstance3D`: a convex 5-point polygon on an ellipse (rx in 0.18..0.42,
   ry in 0.15..0.35, each point's angle jittered by ±0.25 rad and radius by ×0.75..1.0), `_prism(pts, -0.06, 0.06, 0.02, mat)` where the
   colour is picked with weights: body colour 0.6, INK 0.15, GLASS 0.15, white 0.1; outline width 2.5 px.

## Part 4d identity fixes (owner feedback on v6 frames, 2026-10-27)
"Sprinkles is not clear, the window just looks like that; the fire truck's rear still looks like bus windows." The 2D silhouettes stay;
the side details become recognisable 3D equipment. Coordinates car-local metres, B = body half-width (1.25 fire truck, 1.2 ice cream).
### Fire truck (`build_firetruck`)
- Keep: body rrect, front window glass, white stripe (y -0.45..-0.29), ladder racks (rails now 0.09 x 0.09), roof light (flashing), FIRE label, lamp, face.
- REMOVE the 4 dark-red side windows. ADD 3 roller-shutter compartment doors per side: rrect(-3.0 + i*1.45, -0.22, 1.3, 0.98, 0.08) (i = 0..2),
  colour (0.80, 0.82, 0.86) as `decal` (outline on) protruding 0.02 beyond B; on each door 7 horizontal ribs = boxes x across the door minus 0.08
  margins, height 0.025, at y = -0.12 + k*0.13 (k = 0..6), colour (0.55, 0.57, 0.62), z from B+0.02 to B+0.04 (both sides mirrored); a handle bar box
  (0.4 x 0.05) centred at the door's bottom (y = -0.17), colour (0.3, 0.3, 0.33).
- Cab seam: a dark box (INK) x 1.56..1.64, y -0.95..0.95, protruding 0.01 beyond B on both sides (separates the cab from the equipment body).
- Front: chrome grille box x 3.18..3.26, y -0.8..-0.3, z -0.8..0.8 colour (0.8, 0.8, 0.84) outline; bumper box x 3.0..3.34, y -0.98..-0.8,
  z -1.2..1.2 colour (0.2, 0.2, 0.22) outline.
- Hose reel on the rear end: cylinder radius 0.32 length 1.6 (axis along z) at (-3.1, -0.1, 0), colour (0.85, 0.85, 0.2) (yellow hose) with outline.
### Ice cream truck (`build_icecream`)
- Keep: split pink/mint body, front window glass, ICE CREAM label, roof cone + scoop + cherry, lamp, face.
- REPLACE the glass serving window by an OPEN hatch: a dark interior slab rrect(-2.0, -0.15, 2.3, 0.8, 0.1) colour (0.22, 0.16, 0.28) as decal
  (outline on); inside it two small cones (cone height 0.3, top radius 0.09, pointing down, colour (0.85, 0.62, 0.3)) with scoops (sphere r 0.1,
  pink (1, 0.6, 0.8) and white (0.98, 0.95, 0.9)) at x = -1.4 and -0.6, y = 0.1, z = ±(B + 0.05) on both sides.
- Counter shelf under the hatch: box x -2.1..0.4, y -0.22..-0.15, z from B to B + 0.32 (and the mirrored -B-0.32..-B), white (0.97, 0.97, 0.97), outline.
- Awning that sticks OUT: 8 stripes, each a box x = -2.1 + i*0.31 .. +0.31, y 0.80..0.88, z from B to B + 0.5 (both sides mirrored), alternating
  pink (1, 0.35, 0.55) (odd i) / white (even i), outline on (2.5 px); plus a scalloped front edge: for each stripe a small half-disc slab (radius 0.155)
  hanging below the outer edge at z = B + 0.5, same colour.
- Sprinkles on the pink upper body (both sides, decal z = B + 0.016): 26 tiny rounded rects 0.14 x 0.045 (or 0.045 x 0.14 for every second one), positions
  from a fixed RandomNumberGenerator seed 1234 inside x -2.6..2.6, y 0.0..0.95, rejecting any that fall inside the hatch rectangle (x -2.1..0.4, y -0.25..0.9)
  or the front window (x 1.75..2.8), colours cycling red (0.95,0.2,0.25), yellow (1,0.85,0.2), blue (0.25,0.55,1), green (0.3,0.85,0.4), white; no outline.
