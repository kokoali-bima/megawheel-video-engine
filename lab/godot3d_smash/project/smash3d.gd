extends Node3D
## LAB plan B v2 — SMASH ARENA in real 3D. Same format as smash25d (3/4 high camera showing the WHOLE arena, stands
## behind, HP bars, bubbles, winner, end card) but: real light + shadows, the arena is a steel platform over shark water
## (user 2026-10-03: water instead of lava, a shark eats whoever falls), rigid-body cars, progressive damage (smoke,
## fire, parts breaking off), comic POW + hit-stop on big hits, cars breaking into pieces, missiles, Kraggor's foot.
## A director keeps the fight ~24 s (video 30-40 s, user 2026-10-03): KOs are allowed only from fixed beats (edges are walled until then).
##   godot --path project --write-movie out.avi --fixed-fps 30 --quit-after N -- <sprite_dir> [fov y z look_z] [debug]

# SCALE_STANDARD.md: "classic" = the aired smash25d geometry (26 x 10 m, level camera with lens shift, 60 px/m
# at the front edge x zoom 1.0-1.45, pans with the cars); "topdown" = lab v3 framing (20 x 24 m, whole arena, 50 px/m).
var CAM_MODE = "classic"
var ARENA_HX = 13.0
var ARENA_HZ = 5.0
const WATER_Y = -1.2
# win logic copied from smash25d: tyre barriers until 9 s, then a car only leaves the floor when it was PUSHED
# (<0.8 s ago), the floor shrinks from 18 s every 7 s, last car standing always survives, time limit -> most HP wins.
# Added (user 2026-10-03): KOs at least KO_GAP apart, never several cars wiped out by one event.
const INTRO_T0 = 3.6                                     # sonic logo + title 0-3.6 s, then the fighter intros
const INTRO_SLOT = 1.9                                   # smash25d: one slot per fighter (spotlight + card + call)
const GO_T = INTRO_T0 + 4 * INTRO_SLOT + 1.2             # "Ready... set... let's go!" lands GO here (12.4 s)
const BARRIER_DOWN = GO_T + 4.7                          # fight-relative timings (smash25d rhythm, shorter fight)
const PUSH_WINDOW = 0.8
const KO_GAP = 4.0
const SHRINK_AT = GO_T + 11.0
const SHRINK_EVERY = 6.0
const SHRINK_STEP = 0.12
const T_MAX = GO_T + 19.0                                # then winner 3 s + replay + end card
# classic camera (smash25d: k(z) = 6000/(100+8z) = 750/(12.5+z) px/m, camera height 20.4 m, horizon y 276 + 20)
const C_F = 750.0
const C_H = 20.4
const C_D = 12.5
const C_YH = 276.0
const C_DY = 20.0
const C_PIV = 1190.0
var zoom = 1.0
var OFFSET_SIGN = 1.0
var cam_f = 750.0
var cam_yh = 296.0
var camx = 0.0
var last_ko_t = -99.0
var hx_now = 13.0
var hz_now = 5.0
var shrink_done = 0
var floor_shape: BoxShape3D
var floor_mesh: BoxMesh
var front_face: MeshInstance3D
var rims = []
var water_mat: ShaderMaterial
var floor_mat: ShaderMaterial
var win_t_phys = 1e9
var hop_t = -9.0
var sprite_dir = "/root/lab/fx/sprites"
var cast = {}
var cars = []
var pieces = []
var walls = []
var cam: Camera3D
var hud: CanvasLayer
var hp_rows = []
var title_lbl: Label
var sub_lbl: Label
var win_lbl: Label
var cta: Panel
var font: FontFile
var dot_tex: GradientTexture2D
var pow_tex: Texture2D
var shark_open: Texture2D
var shark_closed: Texture2D
var fins = []
var events = []
var t = 0.0
var shake = 0.0
var fov_kick = 0.0
var hitstop_until = -1.0
var last_hitstop = -9.0
var winner = null
var win_t = 1e9
# [time, action, ko-index it belongs to] — skipped when that KO already happened
# One chaos theme per video (user 2026-10-03: meteor one day, Kraggor the next) -> user arg chaos=meteor|kraggor|missile
var chaos = "meteor"
var beats = [[GO_T + 1.5, "soft"], [GO_T + 6.0, "push_weak"], [GO_T + 10.5, "storm"], [GO_T + 15.0, "push_weak"]]
var intro_logged = -1
var go_logged = false
var rng = RandomNumberGenerator.new()
var CAM_FOV = 40.0
var CAM_Y = 30.0
var CAM_Z = -8.0
var LOOK_Z = 11.5
var CARD_TILT = 0.0                                      # topdown: 0.5 rad (cards recline to the high camera)
var cam_base = Vector3.ZERO


func vt() -> float:
	return Engine.get_process_frames() / 30.0


func _ready() -> void:
	rng.seed = 15
	var a = OS.get_cmdline_user_args()
	if a.size() > 0:
		sprite_dir = a[0]
	if a.size() > 4 and a[1] != "debug":
		CAM_FOV = float(a[1])
		CAM_Y = float(a[2])
		CAM_Z = float(a[3])
		LOOK_Z = float(a[4])
	for arg in a:
		if str(arg).begins_with("chaos="):
			chaos = str(arg).substr(6)
		if str(arg).begins_with("cam="):
			CAM_MODE = str(arg).substr(4)
	if CAM_MODE == "topdown":
		ARENA_HX = 10.0
		ARENA_HZ = 12.0
		CARD_TILT = 0.5
	hx_now = ARENA_HX
	hz_now = ARENA_HZ
	cast = JSON.parse_string(FileAccess.open(sprite_dir + "/cast.json", FileAccess.READ).get_as_text())["cars"]
	font = FontFile.new()
	font.load_dynamic_font("/root/.fonts/LuckiestGuy-Regular.ttf")
	var g = Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1))
	g.add_point(0.5, Color(1, 1, 1, 0.7))
	g.set_color(g.get_point_count() - 1, Color(1, 1, 1, 0))
	dot_tex = GradientTexture2D.new()
	dot_tex.gradient = g
	dot_tex.fill = GradientTexture2D.FILL_RADIAL
	dot_tex.fill_from = Vector2(0.5, 0.5)
	dot_tex.fill_to = Vector2(1.0, 0.5)
	dot_tex.width = 64
	dot_tex.height = 64
	pow_tex = _tex("pow.png")
	shark_open = _tex("shark_open.png")
	shark_closed = _tex("shark_closed.png")
	_environment()
	_arena()
	_water()
	_stands()
	var zf = ARENA_HZ / 5.0
	var xf = ARENA_HX / 13.0
	var roster = [["firetruck", Vector3(-8.0 * xf, 0, 2.5 * zf), "HYDRO", Color(0.9, 0.15, 0.15)],
				  ["monster2", Vector3(-3.0 * xf, 0, 7.5 * zf), "GRIZZLY", Color(0.2, 0.75, 0.3)],
				  ["police", Vector3(3.0 * xf, 0, 2.0 * zf), "SIREN", Color(0.95, 0.95, 0.95)],
				  ["f1", Vector3(8.0 * xf, 0, 7.0 * zf), "NITRO", Color(0.2, 0.55, 1.0)]]
	for r in roster:
		cars.append(_car(r[0], r[1], r[2], r[3]))
	cam = Camera3D.new()
	cam.keep_aspect = Camera3D.KEEP_WIDTH                   # portrait: the width is the fixed axis
	add_child(cam)
	if CAM_MODE == "classic":
		cam.projection = Camera3D.PROJECTION_FRUSTUM
		cam.near = 0.5
		cam.far = 200.0
		cam.rotation = Vector3(0, PI, 0)                    # level camera looking down +z (no tilt: cards stay upright)
		_classic_cam(0.0, 1.0, 0.0)
	else:
		cam.fov = CAM_FOV
		cam_base = Vector3(0, CAM_Y, CAM_Z)
		cam.position = cam_base
		cam.look_at(Vector3(0, 0, LOOK_Z), Vector3.UP)
	cam.make_current()
	_hud()
	_scale_report()


func _classic_cam(x: float, z: float, punch: float) -> void:
	## smash25d projection: focal 750 px x zoom, horizon placed so the zoom pivots around screen y 1190
	var zz = z * (1.0 + punch)
	var f = C_F * zz
	var yh = C_PIV + (C_YH - C_PIV) * zz + C_DY
	cam.position = Vector3(x, C_H, -C_D)
	cam.size = 1080.0 / f * cam.near                         # KEEP_WIDTH: size = near-plane width (renders right;
	cam_f = f                                                # unproject_position() is wrong in this mode -> _proj())
	cam_yh = yh
	cam.frustum_offset = Vector2(0, -(960.0 - yh) / f * cam.near * OFFSET_SIGN)


func _proj(w: Vector3) -> Vector2:
	## world -> screen px. Classic = the smash25d formula (level camera, lens shift); topdown = Godot's own projection
	if CAM_MODE != "classic":
		return cam.unproject_position(w)
	var d = w.z - cam.position.z
	return Vector2(540.0 - (w.x - cam.position.x) * cam_f / d, cam_yh + (C_H - w.y) * cam_f / d)


func _behind(w: Vector3) -> bool:
	if CAM_MODE != "classic":
		return cam.is_position_behind(w)
	return w.z - cam.position.z < 0.5


func _scale_report() -> void:
	## measured on-screen scale vs SCALE_STANDARD.md (px per metre at the front / back edge, arena box, car sizes)
	var fl = _proj(Vector3(ARENA_HX, 0, 0))
	var fr = _proj(Vector3(-ARENA_HX, 0, 0))
	var bl = _proj(Vector3(ARENA_HX, 0, ARENA_HZ * 2))
	var br = _proj(Vector3(-ARENA_HX, 0, ARENA_HZ * 2))
	var r = {"arena_m": [ARENA_HX * 2, ARENA_HZ * 2], "front_px_per_m": absf(fr.x - fl.x) / (ARENA_HX * 2),
			 "back_px_per_m": absf(br.x - bl.x) / (ARENA_HX * 2), "front_y": fl.y, "back_y": bl.y,
			 "front_x": [minf(fl.x, fr.x), maxf(fl.x, fr.x)], "mode": CAM_MODE,
			 "cam": [CAM_FOV, CAM_Y, CAM_Z, LOOK_Z] if CAM_MODE != "classic" else [C_F, C_H, C_D, zoom]}
	for c in cars:
		r[c["vk"] + "_px_front"] = c["bw"] * r["front_px_per_m"]
	print("SCALE " + JSON.stringify(r))
	FileAccess.open("/tmp/godot_scale.json", FileAccess.WRITE).store_string(JSON.stringify(r))


# ================================================================== world
func _environment() -> void:
	var env = Environment.new()
	var sky = Sky.new()
	var sm = ProceduralSkyMaterial.new()
	sm.sky_top_color = Color(0.25, 0.5, 0.92)
	sm.sky_horizon_color = Color(0.72, 0.84, 1.0)
	sm.ground_bottom_color = Color(0.1, 0.3, 0.45)
	sky.sky_material = sm
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR   # neutral fill: the steel floor stays gray, not blue
	env.ambient_light_color = Color(0.92, 0.9, 0.88)
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.glow_enabled = true
	env.glow_intensity = 0.4
	env.glow_bloom = 0.1
	var we = WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun = DirectionalLight3D.new()
	# midday sun, high and from behind-left of the camera: shadows fall AWAY from the camera (behind cars and stands).
	# The old setting lit from behind the stands, so their shadow covered the arena (only plausible near sunset).
	sun.rotation_degrees = Vector3(-55, 140, 0)
	sun.light_energy = 1.15
	sun.light_color = Color(1.0, 0.96, 0.9)
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 70.0
	add_child(sun)


func _box(size: Vector3, pos: Vector3, mat: Material, collide := false) -> Node3D:
	var mi = MeshInstance3D.new()
	var bm = BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	if collide:
		var sb = StaticBody3D.new()
		sb.position = pos
		var cs = CollisionShape3D.new()
		var bs = BoxShape3D.new()
		bs.size = size
		cs.shape = bs
		sb.add_child(cs)
		sb.add_child(mi)
		var pm = PhysicsMaterial.new()
		pm.friction = 0.6
		sb.physics_material_override = pm
		add_child(sb)
		return sb
	mi.position = pos
	add_child(mi)
	return mi


func _mat(col: Color, emit := Color(0, 0, 0), emit_e := 0.0) -> StandardMaterial3D:
	var m = StandardMaterial3D.new()
	m.albedo_color = col
	m.roughness = 0.75
	if emit_e > 0.0:
		m.emission_enabled = true
		m.emission = emit
		m.emission_energy_multiplier = emit_e
	return m


func _arena() -> void:
	var floor_sh = Shader.new()                           # steel tread plate, neutral gray
	floor_sh.code = """
shader_type spatial;
float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
void fragment() {
	vec3 w = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec2 g = abs(fract(w.xz / 2.4) - 0.5);
	float grout = step(0.485, max(g.x, g.y));
	vec2 q = fract(w.xz * vec2(1.6, 3.2) + vec2(floor(w.z * 3.2) * 0.5, 0.0)) - 0.5;
	float tread = smoothstep(0.2, 0.1, abs(q.x * 0.7 + q.y * 0.35)) * step(abs(q.y), 0.3);
	float wear = h(floor(w.xz / 2.4)) * 0.06;
	vec3 base = vec3(0.34, 0.35, 0.36) + wear + tread * 0.06;
	ALBEDO = mix(base, vec3(0.18, 0.18, 0.19), grout);
	METALLIC = 0.2;
	ROUGHNESS = 0.65 - tread * 0.15;
}
"""
	var fm = ShaderMaterial.new()
	fm.shader = floor_sh
	floor_mat = fm
	var fb = _box(Vector3(ARENA_HX * 2, 3.0, ARENA_HZ * 2), Vector3(0, -1.5, ARENA_HZ), fm, true)
	floor_shape = fb.get_child(0).shape
	floor_mesh = fb.get_child(1).mesh
	var side = _mat(Color(0.3, 0.31, 0.33))                 # platform front face going down into the water
	side.metallic = 0.4
	front_face = _box(Vector3(ARENA_HX * 2 + 0.02, 2.6, 0.05), Vector3(0, -1.6, -0.02), side)
	var stripe_sh = Shader.new()                           # yellow/black hazard rim
	stripe_sh.code = """
shader_type spatial;
void fragment() {
	vec3 w = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float s = step(0.5, fract((w.x + w.z) * 0.9));
	ALBEDO = mix(vec3(1.0, 0.8, 0.08), vec3(0.08, 0.08, 0.1), s);
	ROUGHNESS = 0.6;
}
"""
	var edge = ShaderMaterial.new()
	edge.shader = stripe_sh
	for i in range(4):
		rims.append(_box(Vector3(1, 0.35, 0.35), Vector3.ZERO, edge))
	# invisible edge walls (layer 2) = smash25d tyre barrier / "nobody pushed it: drive back in"
	for wdef in [[Vector3(ARENA_HX * 2 + 2, 5, 0.5), Vector3(0, 2.5, -0.3)],
				 [Vector3(ARENA_HX * 2 + 2, 5, 0.5), Vector3(0, 2.5, ARENA_HZ * 2 + 0.3)],
				 [Vector3(0.5, 5, ARENA_HZ * 2 + 2), Vector3(-ARENA_HX - 0.3, 2.5, ARENA_HZ)],
				 [Vector3(0.5, 5, ARENA_HZ * 2 + 2), Vector3(ARENA_HX + 0.3, 2.5, ARENA_HZ)]]:
		var sb = StaticBody3D.new()
		sb.position = wdef[1]
		sb.collision_layer = 2
		sb.collision_mask = 0
		var cs = CollisionShape3D.new()
		var bs = BoxShape3D.new()
		bs.size = wdef[0]
		cs.shape = bs
		sb.add_child(cs)
		add_child(sb)
		walls.append(sb)
	_set_bounds(ARENA_HX, ARENA_HZ)


func _set_bounds(hx: float, hz: float) -> void:
	## floor, rim, front face, edge walls and water foam follow the (shrinking) floor; centre stays at z = ARENA_HZ
	hx_now = hx
	hz_now = hz
	var cz = ARENA_HZ
	floor_shape.size = Vector3(hx * 2, 3.0, hz * 2)
	floor_mesh.size = Vector3(hx * 2, 3.0, hz * 2)
	front_face.mesh.size = Vector3(hx * 2 + 0.02, 2.6, 0.05)
	front_face.position = Vector3(0, -1.6, cz - hz - 0.02)
	var rdef = [[Vector3(hx * 2 + 0.5, 0.35, 0.35), Vector3(0, 0, cz - hz - 0.05)],
				[Vector3(hx * 2 + 0.5, 0.35, 0.35), Vector3(0, 0, cz + hz + 0.05)],
				[Vector3(0.35, 0.35, hz * 2), Vector3(-hx - 0.05, 0, cz)],
				[Vector3(0.35, 0.35, hz * 2), Vector3(hx + 0.05, 0, cz)]]
	for i in range(4):
		rims[i].mesh.size = rdef[i][0]
		rims[i].position = rdef[i][1]
	var wdef = [Vector3(0, 2.5, cz - hz - 0.3), Vector3(0, 2.5, cz + hz + 0.3), Vector3(-hx - 0.3, 2.5, cz),
				Vector3(hx + 0.3, 2.5, cz)]
	for i in range(4):
		walls[i].position = wdef[i]
	if water_mat != null:
		water_mat.set_shader_parameter("hx", hx)
		water_mat.set_shader_parameter("hz", hz)


func bounds(tt: float) -> Vector2:
	## smash25d bounds(): eased 12% steps from SHRINK_AT every SHRINK_EVERY, down to 65% x / 72% z
	var hx = ARENA_HX
	var hz = ARENA_HZ
	var sft = minf(tt, win_t_phys) - SHRINK_AT
	while sft > 0:
		var p = minf(1.0, sft / 1.2)
		var e = p * p * (3 - 2 * p)
		var nhx = maxf(ARENA_HX * 0.654, hx * (1 - SHRINK_STEP))
		var nhz = maxf(ARENA_HZ * 0.72, hz * (1 - SHRINK_STEP * 0.75))
		hx = hx + (nhx - hx) * e
		hz = hz + (nhz - hz) * e
		sft -= SHRINK_EVERY
	return Vector2(hx, hz)


func _water() -> void:
	var sh = Shader.new()
	sh.code = """
shader_type spatial;
uniform float hx = 9.5;
uniform float hz = 7.0;
uniform float cz = 7.0;
float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float n(vec2 p) { vec2 i = floor(p); vec2 f = fract(p); f = f * f * (3.0 - 2.0 * f);
	return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
void vertex() {
	vec3 w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	VERTEX.y += sin(w.x * 0.55 + TIME * 1.7) * 0.07 + sin(w.z * 0.8 + TIME * 1.3) * 0.05;
}
void fragment() {
	vec3 w = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec2 p = w.xz * 0.8 + vec2(TIME * 0.07, TIME * 0.05);
	float v = n(p) * 0.6 + n(p * 2.7 - TIME * 0.12) * 0.4;
	float caust = smoothstep(0.62, 0.8, n(p * 3.1 + vec2(TIME * 0.2, -TIME * 0.15)));
	vec2 d = abs(w.xz - vec2(0.0, cz)) - vec2(hx, hz);
	float dist = length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
	float foam = smoothstep(1.1, 0.0, dist + (v - 0.5) * 1.3);
	vec3 col = mix(vec3(0.02, 0.2, 0.38), vec3(0.05, 0.42, 0.6), v) + caust * 0.08;
	ALBEDO = mix(col, vec3(0.96, 0.98, 1.0), foam * 0.9);
	float e = 0.08;
	float dx = (n(p + vec2(e, 0.0)) - n(p)) / e;
	float dz = (n(p + vec2(0.0, e)) - n(p)) / e;
	NORMAL = normalize(NORMAL + (VIEW_MATRIX * vec4(-dx * 0.12, 0.0, -dz * 0.12, 0.0)).xyz);
	ROUGHNESS = 0.3 + foam * 0.5;
	SPECULAR = 0.35;
}
"""
	var m = ShaderMaterial.new()
	m.shader = sh
	m.set_shader_parameter("hx", ARENA_HX)
	m.set_shader_parameter("hz", ARENA_HZ)
	m.set_shader_parameter("cz", ARENA_HZ)
	water_mat = m
	var w = MeshInstance3D.new()
	var pm = PlaneMesh.new()
	pm.size = Vector2(130, 110)
	pm.subdivide_width = 110
	pm.subdivide_depth = 90
	w.mesh = pm
	w.material_override = m
	w.position = Vector3(0, WATER_Y, ARENA_HZ + 6.0)
	add_child(w)
	var ft = _tex("fin.png")
	for i in range(2):                                     # two shark fins circling the platform
		var f = Sprite3D.new()
		f.texture = ft
		f.pixel_size = 1.0 / 110.0
		f.shaded = true
		f.double_sided = true
		f.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		f.offset = Vector2(0, 80)
		add_child(f)
		var trail = _emitter(40, 1.4, Vector2(0.2, 0.8), Vector3.ZERO, Vector2(0.25, 0.55), Color(1, 1, 1, 0.85),
							 Color(1, 1, 1, 0), 60.0, true)
		trail.local_coords = false
		trail.position = Vector3(0, -0.1, 0)
		f.add_child(trail)
		trail.emitting = true
		fins.append({"node": f, "phase": i * PI + 0.6, "speed": 0.32 + 0.06 * i, "prev": Vector3.ZERO})


func _stands() -> void:
	var stand = _mat(Color(0.33, 0.35, 0.42))
	# classic: tall stands right behind the arena (smash25d: stands fill the top third); topdown: low and far
	var rise = 2.2 if CAM_MODE == "classic" else 1.0
	var z0 = ARENA_HZ * 2 + (3.5 if CAM_MODE == "classic" else 7.0)
	var rows = 8 if CAM_MODE == "classic" else 7
	for row in range(rows):
		_box(Vector3(60, rise, 1.7), Vector3(0, rise / 2.0 + row * rise - 0.6, z0 + row * 1.7), stand)
	var mm = MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	var sp = SphereMesh.new()
	sp.radius = 0.36
	sp.height = 0.72
	mm.mesh = sp
	mm.instance_count = 600
	for i in range(600):
		var row = i % rows
		var x = rng.randf_range(-29.0, 29.0)
		mm.set_instance_transform(i, Transform3D(Basis().scaled(Vector3.ONE * (1.5 if CAM_MODE == "classic" else 1.0)),
							  Vector3(x, rise + 0.5 + row * rise - 0.6, z0 - 0.1 + row * 1.7)))
		mm.set_instance_color(i, Color.from_hsv(rng.randf(), 0.55, 0.9))
	var mmi = MultiMeshInstance3D.new()
	mmi.multimesh = mm
	var cm = StandardMaterial3D.new()
	cm.vertex_color_use_as_albedo = true
	mmi.material_override = cm
	add_child(mmi)
	var dock = _mat(Color(0.55, 0.42, 0.3))                # wooden dock in front of the stands
	_box(Vector3(60, 0.4, 2.2), Vector3(0, -0.9, z0 - 1.4), dock)


func _tex(name: String) -> ImageTexture:
	return ImageTexture.create_from_image(Image.load_from_file(sprite_dir + "/" + name))


func _car(vk: String, pos: Vector3, nick: String, col: Color) -> Dictionary:
	var m = cast[vk]
	var bw = float(m["body"][0])
	var bh = float(m["body"][1])
	var ride = float(m["ride"])
	var body = RigidBody3D.new()
	body.mass = 400.0 + bw * 220.0
	body.position = pos + Vector3(0, ride + 0.05, 0)
	body.axis_lock_angular_x = true                       # paper card: rolls in the screen plane only
	body.axis_lock_angular_y = true
	body.contact_monitor = true
	body.max_contacts_reported = 4
	body.continuous_cd = true
	body.can_sleep = false                               # a sleeping body ignores the drive force
	body.collision_mask = 1 | 2                          # floor + director walls
	var pm = PhysicsMaterial.new()
	pm.friction = 0.12                                    # a sliding box stands in for rolling wheels
	pm.bounce = 0.3
	body.physics_material_override = pm
	var cs = CollisionShape3D.new()
	var bs = BoxShape3D.new()
	bs.size = Vector3(bw, ride + bh / 2.0, 1.7)           # from the wheel bottom (-ride) to the roof (+bh/2)
	cs.shape = bs
	cs.position = Vector3(0, (bh / 2.0 - ride) / 2.0, 0)
	body.add_child(cs)
	var tex = _tex(vk + "_body.png")
	var spr = Sprite3D.new()
	spr.texture = tex
	spr.pixel_size = 1.0 / 60.0
	spr.shaded = true
	spr.double_sided = true
	spr.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	spr.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	var card = Node3D.new()
	card.rotation.x = CARD_TILT
	body.add_child(card)
	card.add_child(spr)
	var wheels = []
	var wt = _tex(vk + "_wheel.png")
	for wx in m["wheel_x"]:
		var w = Sprite3D.new()
		w.texture = wt
		w.pixel_size = 1.0 / 60.0
		w.shaded = true
		w.double_sided = true
		w.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		w.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		w.position = Vector3(float(wx), -(ride - float(m["wheel_r"])), 0.02)
		card.add_child(w)
		wheels.append(w)
	# damage emitters (off until HP drops): smoke trail, then fire
	var smoke = _emitter(18, 1.6, Vector2(0.8, 2.0), Vector3(0, 1.8, 0), Vector2(0.6, 1.3), Color(0.35, 0.35, 0.37, 0.7),
						 Color(0.2, 0.2, 0.22, 0), 25.0, false)
	smoke.local_coords = false
	smoke.position = Vector3(0, bh * 0.35, -0.2)
	body.add_child(smoke)
	var fire = _emitter(22, 0.5, Vector2(1.0, 2.5), Vector3(0, 3.0, 0), Vector2(0.35, 0.8), Color(1, 0.85, 0.3, 0.95),
						Color(0.95, 0.2, 0.02, 0), 20.0, true)
	fire.local_coords = false
	fire.position = Vector3(bw * 0.15, bh * 0.3, -0.3)
	body.add_child(fire)
	add_child(body)
	var blob = MeshInstance3D.new()                          # contact shadow under the car (like the cairo engine)
	var bcm = CylinderMesh.new()
	bcm.top_radius = 0.5
	bcm.bottom_radius = 0.5
	bcm.height = 0.01
	blob.mesh = bcm
	var bmat = StandardMaterial3D.new()
	bmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	bmat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	bmat.albedo_texture = dot_tex
	bmat.albedo_color = Color(0, 0, 0, 0.55)
	blob.material_override = bmat
	blob.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	blob.scale = Vector3(bw * 1.1, 1, 1.6)
	add_child(blob)
	var c = {"vk": vk, "blob": blob, "blob_mat": bmat, "nick": nick, "col": col, "body": body, "spr": spr, "wheels": wheels, "tex": tex,
			 "bw": bw, "bh": bh, "ride": ride, "hp": 100.0, "alive": true, "out": false, "smoke": smoke, "fire": fire,
			 "vmax": 9.0 if vk in ["f1", "sports", "police"] else 7.5, "last_hit": -9.0,
			 "mode": "charge", "mode_t": 0.0, "stall": 0.0, "last_push": -9.0}
	body.body_entered.connect(func(other): call_deferred("_on_hit", c, other))
	return c


# ================================================================== FX helpers
func _log(type: String, power: float, pos = null, who := "") -> void:
	var e = {"t": vt(), "type": type, "power": power}
	if who != "":
		e["who"] = who
	if pos != null and cam != null and not _behind(pos):
		var p = _proj(pos)
		e["sx"] = p.x
		e["sy"] = p.y
	events.append(e)
	FileAccess.open("/tmp/godot_events.json", FileAccess.WRITE).store_string(JSON.stringify({"events": events}))


func _emitter(n: int, life: float, vel: Vector2, grav: Vector3, size: Vector2, c0: Color, c1: Color,
			  spread := 180.0, unshaded := true, additive := false, radius := 0.0, fade_in := false) -> CPUParticles3D:
	var p = CPUParticles3D.new()
	var q = QuadMesh.new()
	q.size = Vector2(1, 1)
	var m = StandardMaterial3D.new()
	m.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_texture = dot_tex
	m.vertex_color_use_as_albedo = true
	if unshaded:
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	if additive:
		m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	q.material = m
	p.mesh = q
	p.amount = n
	p.lifetime = life
	p.direction = Vector3(0, 1, 0)
	p.spread = spread
	p.initial_velocity_min = vel.x
	p.initial_velocity_max = vel.y
	p.gravity = grav
	p.scale_amount_min = size.x
	p.scale_amount_max = size.y
	var g = Gradient.new()
	if fade_in:                                          # smoke: grows in softly instead of popping
		g.set_color(0, Color(c0.r, c0.g, c0.b, 0.0))
		g.add_point(0.12, c0)
	else:
		g.set_color(0, c0)
	g.add_point(0.55, c0.lerp(c1, 0.6))
	g.set_color(g.get_point_count() - 1, c1)
	p.color_ramp = g
	if radius > 0.0:
		p.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
		p.emission_sphere_radius = radius
	var cv = Curve.new()
	cv.add_point(Vector2(0, 0.5))
	cv.add_point(Vector2(0.25, 1.0))
	cv.add_point(Vector2(1, 0.4))
	p.scale_amount_curve = cv
	p.emitting = false
	return p


func _particles(pos: Vector3, n: int, life: float, vel: Vector2, grav: Vector3, size: Vector2, c0: Color, c1: Color,
				spread := 180.0, unshaded := true, additive := false, radius := 0.0, fade_in := false, burst := 0.92) -> void:
	var p = _emitter(n, life, vel, grav, size, c0, c1, spread, unshaded, additive, radius, fade_in)
	p.position = pos
	p.one_shot = true
	p.explosiveness = burst
	add_child(p)
	p.emitting = true
	get_tree().create_timer(life + 0.5, false).timeout.connect(p.queue_free)


func _flash(pos: Vector3, energy: float, rng_m: float, col: Color, fade: float) -> void:
	var o = OmniLight3D.new()
	o.position = pos
	o.light_color = col
	o.light_energy = energy
	o.omni_range = rng_m
	add_child(o)
	var tw = create_tween()
	tw.tween_property(o, "light_energy", 0.0, fade)
	tw.tween_callback(o.queue_free)


func _ring(pos: Vector3, radius: float, col: Color, dur: float) -> void:
	var mi = MeshInstance3D.new()
	var tm = TorusMesh.new()
	tm.inner_radius = 0.85
	tm.outer_radius = 1.0
	mi.mesh = tm
	var m = _mat(col, col, 2.5)
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mi.material_override = m
	mi.position = pos + Vector3(0, 0.08, 0)
	mi.scale = Vector3(0.2, 0.05, 0.2)
	add_child(mi)
	var tw = create_tween().set_parallel(true)
	tw.tween_property(mi, "scale", Vector3(radius, 0.05, radius), dur)
	tw.tween_property(m, "albedo_color:a", 0.0, dur)
	tw.chain().tween_callback(mi.queue_free)


func _pow(pos: Vector3, size: float) -> void:
	## comic impact star, always on top, pops in 3 frames and fades
	var s = Sprite3D.new()
	s.texture = pow_tex
	s.pixel_size = size / 512.0
	s.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	s.no_depth_test = true
	s.shaded = false
	s.render_priority = 5
	s.position = pos
	s.rotation_degrees = Vector3(0, 0, rng.randf_range(-25, 25))
	s.scale = Vector3(0.2, 0.2, 0.2)
	add_child(s)
	var tw = create_tween()
	tw.tween_property(s, "scale", Vector3(1.15, 1.15, 1.15), 0.08).set_trans(Tween.TRANS_BACK)
	tw.tween_interval(0.08)
	tw.tween_property(s, "modulate:a", 0.0, 0.16)
	tw.tween_callback(s.queue_free)


func _hitstop(frames: int) -> void:
	if vt() - last_hitstop < 1.0:
		return
	last_hitstop = vt()
	hitstop_until = vt() + frames / 30.0
	Engine.time_scale = 0.04


func _splash(pos: Vector3, big: float) -> void:
	var p = Vector3(pos.x, WATER_Y + 0.1, pos.z)
	_particles(p, int(90 * big), 1.3, Vector2(5, 12) * big, Vector3(0, -16, 0), Vector2(0.2, 0.5) * big,
			   Color(1, 1, 1, 0.95), Color(0.6, 0.85, 1.0, 0), 35.0, false)
	_particles(p, int(30 * big), 1.6, Vector2(1, 3), Vector3(0, 0.5, 0), Vector2(1.2, 2.4) * big,
			   Color(1, 1, 1, 0.7), Color(0.85, 0.95, 1.0, 0), 90.0, true)
	_ring(Vector3(p.x, WATER_Y + 0.05, p.z), 3.5 * big, Color(1, 1, 1, 0.9), 0.9)


func _shards(c: Dictionary, n: int, vel: float) -> void:
	## bits of the car's own artwork break off (bumpers, panels) + small bolts
	var body = c["body"]
	var tex = c["tex"]
	var tsz = tex.get_size()
	var bw_px = c["bw"] * 60.0
	var bh_px = c["bh"] * 60.0
	for i in range(n):
		var fw = rng.randf_range(0.18, 0.32)
		var fh = rng.randf_range(0.25, 0.45)
		var rx = rng.randf_range(0.0, 1.0 - fw)
		var ry = rng.randf_range(0.0, 1.0 - fh)
		var pw = c["bw"] * fw
		var ph = c["bh"] * fh
		var pc = RigidBody3D.new()
		pc.mass = 25.0
		pc.collision_layer = 4
		pc.collision_mask = 1
		var cs = CollisionShape3D.new()
		var bs = BoxShape3D.new()
		bs.size = Vector3(pw, ph, 0.25)
		cs.shape = bs
		pc.add_child(cs)
		var s = Sprite3D.new()
		s.texture = tex
		s.region_enabled = true
		s.region_rect = Rect2(tsz.x / 2 - bw_px / 2 + rx * bw_px, tsz.y / 2 - bh_px / 2 + ry * bh_px, fw * bw_px, fh * bh_px)
		s.pixel_size = 1.0 / 60.0
		s.shaded = true
		s.double_sided = true
		s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		s.flip_h = c["spr"].flip_h
		pc.add_child(s)
		pc.position = body.global_position + Vector3((rx + fw / 2 - 0.5) * c["bw"], (0.5 - ry - fh / 2) * c["bh"], -0.3)
		add_child(pc)
		pc.linear_velocity = Vector3(rng.randf_range(-1, 1) * vel, rng.randf_range(0.5, 1.0) * vel, rng.randf_range(-0.6, 0.6) * vel)
		pc.angular_velocity = Vector3(rng.randf_range(-10, 10), rng.randf_range(-10, 10), rng.randf_range(-10, 10))
		pieces.append(pc)
	var bolt_m = _mat(Color(0.7, 0.7, 0.74))
	bolt_m.metallic = 0.8
	for i in range(n + 2):
		var bb = RigidBody3D.new()
		bb.mass = 4.0
		bb.collision_layer = 4
		bb.collision_mask = 1
		var cs = CollisionShape3D.new()
		var bs = BoxShape3D.new()
		bs.size = Vector3(0.22, 0.22, 0.22)
		cs.shape = bs
		bb.add_child(cs)
		var mi = MeshInstance3D.new()
		var cm = CylinderMesh.new()
		cm.top_radius = 0.12
		cm.bottom_radius = 0.12
		cm.height = 0.22
		cm.radial_segments = 6
		mi.mesh = cm
		mi.material_override = bolt_m
		bb.add_child(mi)
		bb.position = body.global_position + Vector3(rng.randf_range(-1, 1) * c["bw"] * 0.4, rng.randf_range(0, 0.6), -0.2)
		add_child(bb)
		bb.linear_velocity = Vector3(rng.randf_range(-1, 1) * vel * 1.2, rng.randf_range(0.6, 1.2) * vel, rng.randf_range(-0.5, 0.5) * vel)
		bb.angular_velocity = Vector3(rng.randf_range(-20, 20), rng.randf_range(-20, 20), rng.randf_range(-20, 20))
		pieces.append(bb)


func _squash(c: Dictionary, amt: float) -> void:
	var s = c["spr"]
	var tw = create_tween()
	tw.tween_property(s, "scale", Vector3(1.0 + amt, 1.0 - amt, 1.0), 0.05)
	tw.tween_property(s, "scale", Vector3.ONE, 0.35).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)


func explode(pos: Vector3, power: float, push := true, lethal = null, push_h := 9.0) -> void:
	_log("explode", power, pos)
	_flash(pos + Vector3(0, 1.5, 0), 8.0 * power, 13.0 * power, Color(1, 0.6, 0.25), 0.6)
	var fb = minf(power, 1.4)                                # cap the fireball so it never blobs the screen
	_fireball(pos + Vector3(0, 1.0, 0), 2.4 * fb)                # smooth expanding glow ball
	_particles(pos + Vector3(0, 0.9, 0), int(70 * fb), 0.55, Vector2(2, 6) * fb, Vector3(0, 3, 0),
			   Vector2(0.5, 1.2) * fb, Color(1, 0.95, 0.75, 0.9), Color(1, 0.5, 0.1, 0), 180.0, true, true, 0.7 * fb, false, 0.8)
	_particles(pos + Vector3(0, 1.1, 0), int(90 * fb), 1.0, Vector2(3, 8) * fb, Vector3(0, 2.5, 0),
			   Vector2(0.7, 1.6) * fb, Color(1, 0.62, 0.18, 0.85), Color(0.7, 0.12, 0.03, 0), 180.0, true, true, 0.9 * fb, false, 0.7)
	_particles(pos + Vector3(0, 1.4, 0), int(55 * fb), 3.6, Vector2(0.8, 2.6), Vector3(0, 1.4, 0),
			   Vector2(1.2, 2.8) * fb, Color(0.16, 0.15, 0.15, 0.85), Color(0.32, 0.32, 0.34, 0), 80.0, false, false, 1.0 * fb, true, 0.55)
	_particles(pos + Vector3(0, 0.5, 0), int(90 * fb), 1.3, Vector2(9, 22) * fb, Vector3(0, -15, 0),
			   Vector2(0.06, 0.14), Color(1, 0.92, 0.4), Color(1, 0.4, 0.1, 0), 180.0, true, true)       # sparks
	_ring(pos, 7.0 * power, Color(1, 0.85, 0.5, 0.9), 0.45)
	_pow(pos + Vector3(0, 1.8, -0.5), 3.6 * fb)
	_scorch(pos, 1.1 * fb)
	shake = max(shake, 0.5 * power)
	fov_kick = max(fov_kick, 3.0 * fb)
	if lethal != null and not _lethal_ok(lethal):
		lethal = null
	if push:
		for c in cars:
			if not c["alive"]:
				continue
			var d = c["body"].global_position - pos
			var dist = d.length()
			if dist < 7.0 * power:
				var f = (1.0 - dist / (7.0 * power))
				c["body"].apply_central_impulse((Vector3(d.x, 0, d.z).normalized() * push_h + Vector3(0, 8.0, 0))
												* f * c["body"].mass * power)
				c["body"].apply_torque_impulse(Vector3(0, 0, rng.randf_range(-1, 1) * 6.0 * c["body"].mass * f))
				c["last_push"] = t
				_shards(c, 3, 7.0)
				_damage(c, 100.0 if c == lethal else 45.0 * f * power, "KABOOM!", c == lethal)
	if lethal != null and lethal["alive"]:                    # a direct hit always lands
		_damage(lethal, 100.0, "KABOOM!", true)


func _fireball(pos: Vector3, size: float) -> void:
	## additive noisy sphere: grows fast with ease-out, cools from white to orange to red while fading (no hard edges)
	var mi = MeshInstance3D.new()
	var sm = SphereMesh.new()
	sm.radius = 0.5
	sm.height = 1.0
	mi.mesh = sm
	var sh = Shader.new()
	sh.code = """
shader_type spatial;
render_mode unshaded, blend_add, depth_draw_never, cull_back;
uniform float life = 0.0;
float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float n(vec2 p) { vec2 i = floor(p); vec2 f = fract(p); f = f * f * (3.0 - 2.0 * f);
	return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
void fragment() {
	float v = n(UV * vec2(9.0, 5.0) + TIME * 1.7) * 0.6 + n(UV * vec2(19.0, 11.0) - TIME * 2.3) * 0.4;
	float rim = 1.0 - abs(dot(NORMAL, VIEW));
	vec3 col = mix(vec3(1.0, 0.96, 0.78), vec3(1.0, 0.55, 0.12), smoothstep(0.0, 0.55, life + v * 0.25));
	col = mix(col, vec3(0.55, 0.1, 0.03), smoothstep(0.5, 1.0, life + v * 0.2));
	float a = (1.0 - life) * (1.0 - rim * 0.85) * (0.55 + 0.45 * v);
	ALBEDO = col * a * 1.6;
}
"""
	var m = ShaderMaterial.new()
	m.shader = sh
	mi.material_override = m
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.position = pos
	mi.scale = Vector3.ONE * size * 0.25
	add_child(mi)
	var tw = create_tween().set_parallel(true)
	tw.tween_property(mi, "scale", Vector3.ONE * size, 0.35).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tw.tween_property(mi, "position:y", pos.y + size * 0.35, 0.8).set_ease(Tween.EASE_OUT)
	tw.tween_method(func(v): m.set_shader_parameter("life", v), 0.0, 1.0, 0.8)
	tw.chain().tween_callback(mi.queue_free)


func _scorch(pos: Vector3, r: float) -> void:
	if absf(pos.x) > ARENA_HX or pos.z < 0.0 or pos.z > ARENA_HZ * 2:
		return
	var mi = MeshInstance3D.new()
	var cm = CylinderMesh.new()
	cm.top_radius = r
	cm.bottom_radius = r
	cm.height = 0.02
	mi.mesh = cm
	var m = StandardMaterial3D.new()
	m.albedo_color = Color(0.05, 0.04, 0.04, 0.45)
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mi.material_override = m
	mi.position = Vector3(pos.x, 0.015, pos.z)
	add_child(mi)


func fracture(c: Dictionary) -> void:
	## the card breaks into 12 textured pieces + shards, wheels fly off, the wreck keeps burning
	_log("fracture", 1.0, c["body"].global_position)
	var body = c["body"]
	var tex = c["tex"]
	var tsz = tex.get_size()
	var pos = body.global_position
	var bw_px = c["bw"] * 60.0
	var bh_px = c["bh"] * 60.0
	_hitstop(4)
	for iy in range(3):
		for ix in range(4):
			var piece = RigidBody3D.new()
			piece.mass = 60.0
			piece.collision_layer = 4
			piece.collision_mask = 1
			var pw = c["bw"] / 4.0
			var ph = c["bh"] / 3.0
			var cs = CollisionShape3D.new()
			var bs = BoxShape3D.new()
			bs.size = Vector3(pw, ph, 0.3)
			cs.shape = bs
			piece.add_child(cs)
			var s = Sprite3D.new()
			s.texture = tex
			s.region_enabled = true
			s.region_rect = Rect2(tsz.x / 2 - bw_px / 2 + ix * bw_px / 4, tsz.y / 2 - bh_px / 2 + iy * bh_px / 3,
								  bw_px / 4, bh_px / 3)
			s.pixel_size = 1.0 / 60.0
			s.shaded = true
			s.double_sided = true
			s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
			s.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
			s.modulate = Color(0.85, 0.8, 0.78)
			piece.add_child(s)
			piece.position = pos + Vector3(-c["bw"] / 2 + pw * (ix + 0.5), c["bh"] / 2 - ph * (iy + 0.5), 0)
			add_child(piece)
			piece.linear_velocity = body.linear_velocity * 0.4 + Vector3(rng.randf_range(-9, 9), rng.randf_range(7, 15),
																		 rng.randf_range(-5, 5))
			piece.angular_velocity = Vector3(rng.randf_range(-10, 10), rng.randf_range(-10, 10), rng.randf_range(-10, 10))
			if (ix + iy) % 4 == 0:                           # some pieces trail smoke
				var tr = _emitter(20, 0.9, Vector2(0.2, 0.8), Vector3(0, 1, 0), Vector2(0.4, 0.9),
								  Color(0.18, 0.17, 0.17, 0.8), Color(0.35, 0.35, 0.36, 0), 30.0, false)
				tr.local_coords = false
				piece.add_child(tr)
				tr.emitting = true
			pieces.append(piece)
	_shards(c, 4, 10.0)
	_particles(pos + Vector3(0, 1.0, -0.4), 40, 1.2, Vector2(6, 14), Vector3(0, -15, 0), Vector2(0.1, 0.22),
			   Color(0.8, 0.95, 1.0, 0.95), Color(0.6, 0.85, 1.0, 0), 120.0, false)        # glass
	for w in c["wheels"]:                                   # wheels fly off and roll
		var wb = RigidBody3D.new()
		wb.mass = 40.0
		wb.collision_layer = 4
		wb.collision_mask = 1
		var wc = CollisionShape3D.new()
		var sh = CylinderShape3D.new()
		sh.radius = 0.45
		sh.height = 0.3
		wc.shape = sh
		wc.rotation_degrees = Vector3(90, 0, 0)
		wb.add_child(wc)
		var ws = w.duplicate()
		ws.position = Vector3.ZERO
		wb.add_child(ws)
		wb.position = w.global_position
		add_child(wb)
		wb.linear_velocity = Vector3(rng.randf_range(-9, 9), rng.randf_range(6, 12), rng.randf_range(-3, 3))
		wb.angular_velocity = Vector3(0, 0, rng.randf_range(-18, 18))
		pieces.append(wb)
	if pos.y > -0.5:                                        # burning wreck spot
		var fire = _emitter(30, 0.7, Vector2(1.0, 3.0), Vector3(0, 3, 0), Vector2(0.5, 1.2), Color(1, 0.8, 0.3, 0.95),
							Color(0.9, 0.15, 0.02, 0), 25.0, true)
		fire.position = Vector3(pos.x, 0.2, pos.z)
		add_child(fire)
		fire.emitting = true
		var smoke = _emitter(26, 3.0, Vector2(1.0, 2.5), Vector3(0, 1.6, 0), Vector2(1.2, 2.6), Color(0.12, 0.11, 0.11, 0.85),
							 Color(0.3, 0.3, 0.32, 0), 20.0, false)
		smoke.position = Vector3(pos.x, 0.8, pos.z)
		add_child(smoke)
		smoke.emitting = true
		get_tree().create_timer(7.0, false).timeout.connect(func(): fire.emitting = false; smoke.emitting = false)
	body.queue_free()


# ================================================================== director + battle
func dead_count() -> int:
	return cars.filter(func(cc): return not cc["alive"]).size()


func _lethal_ok(c) -> bool:
	## a 'finishing' hit only counts for the KO it was planned for (no double KO from a late meteor)
	return c != null and c["alive"] and int(c.get("ko_idx", -1)) == dead_count()


func ko_allowed() -> bool:
	## smash25d: no eliminations before the barriers drop; ours: and at least KO_GAP after the previous KO
	return t >= BARRIER_DOWN and t - last_ko_t >= KO_GAP and cars.filter(func(cc): return cc["alive"]).size() > 1


func _ko(c: Dictionary, how: String) -> void:
	c["alive"] = false
	last_ko_t = t
	c["hp"] = 0.0
	_log("ko", 1.0, c["body"].global_position, c["nick"] + ("|fall" if how == "fall" else "|boom"))
	_bubble(c["body"].global_position + Vector3(0, c["bh"] + 2.0, 0), "K.O.!", 80)


func _damage(c: Dictionary, amount: float, word: String, lethal := false) -> void:
	if not c["alive"]:
		return
	if lethal or ko_allowed():
		c["hp"] = max(0.0, c["hp"] - amount)
	else:
		c["hp"] = max(min(c["hp"], 8.0), c["hp"] - amount)    # too early for a KO: badly hurt, still alive
	_bubble(c["body"].global_position + Vector3(0, c["bh"] + 1.2, 0), word)
	if c["hp"] <= 0.0:
		_ko(c, "boom")
		var at = c["body"].global_position
		call_deferred("fracture", c)
		call_deferred("explode", at, 1.0, false)


func _on_hit(c: Dictionary, other) -> void:
	if not c["alive"] or vt() - c["last_hit"] < 0.4:
		return
	for o in cars:
		if o["body"] == other and o["alive"]:
			var rel = (c["body"].linear_velocity - o["body"].linear_velocity).length()
			c["mode"] = "back"                              # rammed: reverse, then charge again
			c["mode_t"] = t
			if rel > 3.0:
				c["last_hit"] = vt()
				c["last_push"] = t                         # a pushed car may leave the floor (smash25d last_push)
				var dmg = rel * 1.3 * o["body"].mass / c["body"].mass
				var p = clampf(rel / 13.0, 0.2, 1.0)
				var mid = (c["body"].global_position + o["body"].global_position) / 2.0
				_log("crash", p, mid)
				_particles(mid + Vector3(0, 1.0, 0), int(25 + 40 * p), 0.55, Vector2(5, 14), Vector3(0, -14, 0),
						   Vector2(0.06, 0.16), Color(1, 1, 0.8), Color(1, 0.6, 0.1, 0))
				_flash(mid + Vector3(0, 1.2, 0), 2.5 + 3.0 * p, 6.0, Color(1, 0.9, 0.7), 0.2)
				_squash(c, 0.08 + 0.12 * p)
				shake = max(shake, 0.12 + 0.25 * p)
				if rel > 8.0:                               # big hit: POW, parts fly, 3-frame hit-stop
					_pow(mid + Vector3(0, 1.4, -0.6), 2.6)
					_shards(c, 2, 6.0)
					_log("chunk", 1.0, mid)
					fov_kick = max(fov_kick, 2.0)
					_hitstop(3)
				_damage(c, dmg, ["BAM!", "WHAM!", "CRUNCH!", "BONK!"][rng.randi() % 4])


func _fall(c: Dictionary) -> void:
	## into the water: splash, the car bobs, then the shark breaches and swallows it
	var b = c["body"]
	b.freeze = true
	var p = b.global_position
	b.global_position = Vector3(p.x, WATER_Y - 0.2, p.z)
	b.rotation = Vector3(0, 0, rng.randf_range(-0.3, 0.3))
	_log("fall", 1.0, p)
	_splash(p, 1.2)
	_bubble(p + Vector3(0, 3.0, 0), "SPLASH!")
	var tw = create_tween().set_loops(3)
	tw.tween_property(b, "position:y", WATER_Y - 0.05, 0.22)
	tw.tween_property(b, "position:y", WATER_Y - 0.3, 0.22)
	get_tree().create_timer(0.9, false).timeout.connect(func(): _shark(c))


func _shark(c: Dictionary) -> void:
	var b = c["body"]
	if not is_instance_valid(b):
		return
	var at = b.global_position
	var sh = Sprite3D.new()
	sh.texture = shark_open
	sh.pixel_size = 1.0 / 110.0
	sh.shaded = true
	sh.double_sided = true
	sh.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	sh.flip_h = true                                        # faces screen-right, rotated nose-up
	sh.rotation = Vector3(0, 0, -PI / 2 + 0.12)
	sh.position = Vector3(at.x, WATER_Y - 5.6, at.z + 0.2)
	add_child(sh)
	_log("shark", 1.0, at)
	_splash(at, 1.5)
	var st = {"chomped": false, "resplash": false}
	var peak = WATER_Y + 1.1
	var f = func(u: float):
		var y = 0.0
		if u < 0.35:
			y = lerpf(WATER_Y - 5.6, peak, 1.0 - pow(1.0 - u / 0.35, 2.0))
		elif u < 0.5:
			y = peak
		else:
			var k = (u - 0.5) / 0.5
			y = lerpf(peak, WATER_Y - 7.0, k * k)
			sh.rotation.z = -PI / 2 + 0.12 + 0.7 * k
		sh.position.y = y
		if not st["chomped"] and is_instance_valid(b):
			b.global_position.y = max(WATER_Y - 0.2, y + 2.9)   # the car rides up in the open jaws
		if u >= 0.36 and not st["chomped"]:
			st["chomped"] = true
			sh.texture = shark_closed
			if is_instance_valid(b):
				b.visible = false
			_log("chomp", 1.0, Vector3(at.x, peak + 3.0, at.z))
			_pow(Vector3(at.x, peak + 3.4, at.z - 0.6), 3.0)
			_bubble(Vector3(at.x, peak + 5.5, at.z), "CHOMP!", 80)
			shake = max(shake, 0.4)
		if u >= 0.82 and not st["resplash"]:
			st["resplash"] = true
			_splash(at, 1.3)
	var tw = create_tween()
	tw.tween_method(f, 0.0, 1.0, 1.5)
	tw.tween_callback(func(): sh.queue_free(); if is_instance_valid(b): b.queue_free())


func _physics_process(delta: float) -> void:
	t += delta
	var go = clampf((t - GO_T) / 0.6, 0.0, 1.0)             # intro: jingle + fighter intros, then GO
	if not go_logged and t >= GO_T:
		go_logged = true
		_log("go", 1.0)
	var allowed = ko_allowed()
	var bb = bounds(t)
	if absf(bb.x - hx_now) > 0.004 or absf(bb.y - hz_now) > 0.004:
		_set_bounds(bb.x, bb.y)
	var step = int((t - SHRINK_AT) / SHRINK_EVERY) + 1 if t >= SHRINK_AT else 0
	if step > shrink_done and winner == null:
		shrink_done = step
		var nb = bounds(t + 1.3)
		if nb.x < hx_now - 0.05:
			_shrink_fx(hx_now, hz_now, nb.x, nb.y)
	var ahead = bounds(t + 1.5)                               # drivers see the floor shrinking coming
	var alive = cars.filter(func(cc): return cc["alive"])
	for c in alive:                                          # barrier per car: only a freshly pushed car gets through
		var free_ = allowed and t - c["last_push"] < PUSH_WINDOW
		c["body"].collision_mask = 1 if free_ else (1 | 2)
	for c in alive:
		var b = c["body"]
		if b.global_position.y < WATER_Y + 0.3 and not c["out"]:   # off the platform -> shark food
			c["out"] = true
			_ko(c, "fall")
			_fall(c)
			continue
		if go <= 0.0 or winner != null:
			continue
		var target = null
		var best = 1e9
		for o in alive:
			if o != c:
				var d = o["body"].global_position.distance_to(b.global_position)
				if d < best:
					best = d
					target = o
		if target == null:
			continue
		var to = target["body"].global_position - b.global_position
		to.y = 0
		if c["mode"] == "charge" and to.length() < 3.6 and b.linear_velocity.length() < 1.2:
			c["stall"] += delta                             # pushing match: back off
			if c["stall"] > 0.5:
				c["mode"] = "back"
				c["mode_t"] = t
				c["stall"] = 0.0
		if c["mode"] == "back" and t - c["mode_t"] > 0.9:
			c["mode"] = "charge"
		var want = to.normalized() * c["vmax"] * go
		var centre = Vector3(0, 0, ARENA_HZ) - b.global_position
		centre.y = 0
		if c["mode"] == "back":
			want = (-to.normalized() * 0.6 + centre.normalized() * 0.4).normalized() * c["vmax"] * 0.7
		var bp0 = b.global_position
		if absf(bp0.x) > ahead.x - 2.0 or absf(bp0.z - ARENA_HZ) > ahead.y - 1.2:
			want += centre.normalized() * c["vmax"] * 0.6        # scared of the edge
		var v = b.linear_velocity
		var dv = Vector3(want.x - v.x, 0, want.z - v.z)
		if b.global_position.y < c["ride"] + 0.4 and b.global_position.y > c["ride"] - 0.6:
			b.apply_central_force(dv * b.mass * 2.2)         # only drive with the wheels on the floor
		c["spr"].flip_h = v.x < -0.3 if abs(v.x) > 0.3 else c["spr"].flip_h
		for w in c["wheels"]:
			w.flip_h = c["spr"].flip_h
			w.rotation.z -= v.x * delta / 0.5
	for pc in pieces:                                       # debris hitting the water
		if is_instance_valid(pc) and pc.global_position.y < WATER_Y - 0.3:
			_particles(Vector3(pc.global_position.x, WATER_Y + 0.1, pc.global_position.z), 14, 0.8, Vector2(3, 6),
					   Vector3(0, -14, 0), Vector2(0.12, 0.3), Color(1, 1, 1, 0.9), Color(0.7, 0.9, 1, 0), 30.0, false)
			pc.queue_free()
	pieces = pieces.filter(func(p): return is_instance_valid(p) and not p.is_queued_for_deletion())
	if OS.get_cmdline_user_args().has("debug") and Engine.get_physics_frames() % 60 == 0:
		var line = "t=%.1f allowed=%s" % [t, allowed]
		for c in cars:
			if is_instance_valid(c["body"]):
				var bp = c["body"].global_position
				line += " | %s (%.1f,%.1f,%.1f) hp=%d %s" % [c["nick"], bp.x, bp.y, bp.z, c["hp"], "" if c["alive"] else "OUT"]
		print(line)
	_director(alive)
	alive = cars.filter(func(cc): return cc["alive"])
	if winner != null and is_instance_valid(winner["body"]) and t - hop_t > 1.0 \
			and winner["body"].global_position.y < winner["ride"] + 0.3:
		hop_t = t                                             # victory hops (smash25d winner showcase)
		winner["body"].apply_central_impulse(Vector3(0, 5.5, 0) * winner["body"].mass)
	if winner == null and alive.size() == 1 and t > 4.0:
		winner = alive[0]
		win_t = vt()
		win_t_phys = t
		win_lbl.text = winner["nick"] + " WINS!"
		win_lbl.visible = true
		_log("win", 1.0, winner["body"].global_position, winner["nick"])
		_particles(winner["body"].global_position + Vector3(0, 7, 0), 220, 3.2, Vector2(3, 9), Vector3(0, -4, 0),
				   Vector2(0.14, 0.3), Color(1, 0.9, 0.2), Color(0.3, 0.6, 1.0, 0.8))


func _director(alive: Array) -> void:
	if alive.size() < 2 or winner != null:
		return
	var weakest = alive[0]
	for c in alive:
		if c["hp"] < weakest["hp"]:
			weakest = c
	for bt in beats:
		if bt[0] > 0 and t >= bt[0]:
			bt[0] = -1.0
			var act = bt[1]
			if act == "push_weak" and weakest["hp"] >= 60.0:
				act = "soft"                                 # smash25d: only a weak car gets dropped off the edge
			if act == "soft":
				var spot = alive[rng.randi() % alive.size()]["body"].global_position
				_chaos_hit(Vector3(spot.x + 1.5, 0, spot.z), null, 7.0)
			elif act == "push_weak":
				var p = weakest["body"].global_position
				var opts = [[hx_now - p.x, Vector3(1, 0, 0)], [hx_now + p.x, Vector3(-1, 0, 0)],
							[p.z - (ARENA_HZ - hz_now), Vector3(0, 0, -1)], [(ARENA_HZ + hz_now) - p.z, Vector3(0, 0, 1)]]
				var bout = opts[0][1]
				var bd = opts[0][0]
				for o in opts:
					if o[0] < bd:
						bd = o[0]
						bout = o[1]
				_chaos_hit(Vector3(p.x, 0, p.z) - bout * 3.0, null, 14.0)
			elif act == "storm" and chaos == "meteor":
				_bubble(Vector3(0, 6, ARENA_HZ), "METEOR SHOWER!", 80)
				for i in range(3):                           # only 3 rocks, nobody is finished off by a script
					get_tree().create_timer(0.9 * i, false).timeout.connect(func():
						var al = cars.filter(func(cc): return cc["alive"])
						if al.size() < 2:
							return
						var tp = al[rng.randi() % al.size()]["body"].global_position
						_meteor(Vector3(tp.x + rng.randf_range(-3.0, 3.0), 0, tp.z + rng.randf_range(-1.5, 1.5)), null))
			elif act == "storm":
				_chaos_hit(Vector3(weakest["body"].global_position.x, 0, weakest["body"].global_position.z), null, 9.0)
	if t >= T_MAX:                                          # smash25d T_MAX: time is up, most HP wins
		var best = alive[0]
		for c in alive:
			if c["hp"] > best["hp"]:
				best = c
		_bubble(Vector3(0, 5, ARENA_HZ), "TIME'S UP!", 90)
		for c in alive:
			if c != best:
				c["alive"] = false
				c["out"] = true
				c["spr"].modulate = Color(0.5, 0.5, 0.55)
				c["smoke"].emitting = true
				_log("ko", 0.5, c["body"].global_position, c["nick"] + "|boom")


func _shrink_fx(hx0: float, hz0: float, hx1: float, hz1: float) -> void:
	## the outer floor plates break off and sink (smash25d "ARENA SHRINKING!")
	_log("shrink", 1.0, Vector3(0, 0, ARENA_HZ))
	_bubble(Vector3(0, 5, ARENA_HZ), "ARENA SHRINKING!", 80)
	shake = max(shake, 0.25)
	var cz = ARENA_HZ
	var slabs = []
	for sgn in [-1.0, 1.0]:
		for i in range(3):
			var l = hz0 * 2 / 3.0
			slabs.append([Vector3(hx0 - hx1, 0.5, l - 0.1), Vector3(sgn * (hx1 + hx0) / 2.0, -0.25, cz - hz0 + l * (i + 0.5))])
		for i in range(4):
			var w = hx1 * 2 / 4.0
			slabs.append([Vector3(w - 0.1, 0.5, hz0 - hz1), Vector3(-hx1 + w * (i + 0.5), -0.25, cz + sgn * (hz1 + hz0) / 2.0)])
	for i in range(slabs.size()):
		var sd = slabs[i]
		var rb = RigidBody3D.new()
		rb.collision_layer = 4
		rb.collision_mask = 0
		rb.gravity_scale = 0.0
		var mi = MeshInstance3D.new()
		var bm = BoxMesh.new()
		bm.size = sd[0]
		mi.mesh = bm
		mi.material_override = floor_mat
		rb.add_child(mi)
		rb.position = sd[1]
		add_child(rb)
		pieces.append(rb)
		var delay = 0.05 * i
		get_tree().create_timer(delay, false).timeout.connect(func():
			if is_instance_valid(rb):
				rb.gravity_scale = 1.0
				rb.angular_velocity = Vector3(rng.randf_range(-1.5, 1.5), 0, rng.randf_range(-1.5, 1.5)))


func _missile(spot: Vector3, lethal, push_h := 9.0) -> void:
	_log("missile", 1.0, spot)
	_ring(spot, 2.2, Color(1, 0.15, 0.1, 0.9), 1.3)
	var m = MeshInstance3D.new()
	var cap = CapsuleMesh.new()
	cap.radius = 0.35
	cap.height = 2.2
	m.mesh = cap
	m.material_override = _mat(Color(0.75, 0.75, 0.8))
	m.position = spot + Vector3(2, 30, 6)
	add_child(m)
	var trail = _emitter(60, 0.5, Vector2(2, 5), Vector3.ZERO, Vector2(0.5, 1.2), Color(1, 0.9, 0.4),
						 Color(0.5, 0.5, 0.5, 0), 180.0, true)
	m.add_child(trail)
	trail.emitting = true
	var tw = create_tween()
	tw.tween_interval(0.6)
	tw.tween_property(m, "position", spot, 0.7).set_ease(Tween.EASE_IN)
	tw.tween_callback(func(): explode(spot, 1.4, true, lethal, push_h); m.queue_free())


func _chaos_hit(spot: Vector3, lethal, push_h: float) -> void:
	if chaos == "kraggor":
		_kraggor(spot, push_h, lethal)
	elif chaos == "missile":
		_missile(spot, lethal, push_h)
	else:
		_meteor(spot, lethal, push_h)


func _meteor(spot: Vector3, lethal, push_h := 9.0) -> void:
	## flaming rock falling at an angle (the look the user liked in the first Godot test), crater + rock spray
	_log("meteor", 1.0, spot)
	_ring(spot, 1.8, Color(1, 0.45, 0.1, 0.9), 0.9)
	var m = MeshInstance3D.new()
	var sp = SphereMesh.new()
	sp.radius = 0.85
	sp.height = 1.5
	sp.radial_segments = 7
	sp.rings = 4
	m.mesh = sp
	m.material_override = _mat(Color(0.35, 0.22, 0.15), Color(1, 0.4, 0.08), 1.6)
	m.position = spot + Vector3(-9, 30, 12)
	add_child(m)
	var fire = _emitter(70, 0.45, Vector2(1, 3), Vector3.ZERO, Vector2(0.9, 2.0), Color(1, 0.9, 0.4, 1),
						Color(0.95, 0.25, 0.03, 0), 25.0, true)
	fire.local_coords = false
	m.add_child(fire)
	fire.emitting = true
	var smk = _emitter(30, 1.4, Vector2(0.5, 1.5), Vector3(0, 0.8, 0), Vector2(1.0, 2.0), Color(0.2, 0.18, 0.17, 0.75),
					   Color(0.35, 0.35, 0.36, 0), 40.0, false)
	smk.local_coords = false
	m.add_child(smk)
	smk.emitting = true
	var tw = create_tween()
	tw.tween_property(m, "position", spot + Vector3(0, 0.6, 0), 0.75).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(m, "rotation", Vector3(6, 4, 3), 0.75)
	tw.tween_callback(func():
		explode(spot, 1.2, true, lethal, push_h)
		_particles(spot + Vector3(0, 0.4, 0), 40, 1.5, Vector2(5, 12), Vector3(0, -16, 0), Vector2(0.25, 0.6),
				   Color(0.4, 0.3, 0.25), Color(0.3, 0.25, 0.2, 0.6), 50.0, false)   # rock spray
		var glow = _emitter(16, 0.6, Vector2(0.5, 1.5), Vector3(0, 2, 0), Vector2(0.4, 0.9), Color(1, 0.6, 0.15, 0.9),
							Color(0.9, 0.2, 0.02, 0), 30.0, true)
		glow.position = Vector3(spot.x, 0.1, spot.z)
		add_child(glow)
		glow.emitting = true
		get_tree().create_timer(3.0, false).timeout.connect(func(): glow.emitting = false)
		m.queue_free())


func _kraggor(spot: Vector3, push_h: float, lethal) -> void:
	_log("kraggor", 1.0, spot)
	var foot = Node3D.new()
	var green = _mat(Color(0.24, 0.55, 0.36))
	var leg = MeshInstance3D.new()
	var lm = BoxMesh.new()
	lm.size = Vector3(3.2, 30, 3.0)
	leg.mesh = lm
	leg.material_override = green
	leg.position = Vector3(0, 15.6, 0)
	foot.add_child(leg)
	var sole = MeshInstance3D.new()
	var sm = BoxMesh.new()
	sm.size = Vector3(5.2, 1.2, 4.0)
	sole.mesh = sm
	sole.material_override = green
	sole.position = Vector3(0, 0.6, 0)
	foot.add_child(sole)
	for dx in [-1.7, 0.0, 1.7]:                              # white claws
		var claw = MeshInstance3D.new()
		var cm = PrismMesh.new()
		cm.size = Vector3(0.6, 0.8, 0.6)
		claw.mesh = cm
		claw.material_override = _mat(Color(1, 1, 1))
		claw.position = Vector3(dx, 0.4, -2.1)
		claw.rotation_degrees = Vector3(180, 0, 0)
		foot.add_child(claw)
	foot.position = spot + Vector3(0, 26, 0)
	add_child(foot)
	_bubble(Vector3(0, 6, ARENA_HZ), "KRAGGOR ATTACK!", 70)
	var tw = create_tween()
	tw.tween_interval(1.0)
	tw.tween_property(foot, "position", spot, 0.35).set_ease(Tween.EASE_IN)
	tw.tween_callback(func(): _stomp(spot, push_h, lethal))
	tw.tween_interval(1.2)
	tw.tween_property(foot, "position", spot + Vector3(0, 30, 0), 0.8).set_ease(Tween.EASE_IN)
	tw.tween_callback(foot.queue_free)


func _stomp(spot: Vector3, push_h: float, lethal) -> void:
	_log("stomp", 1.0, spot)
	_ring(spot, 9.0, Color(0.85, 0.85, 0.85, 0.9), 0.6)
	_particles(spot + Vector3(0, 0.3, 0), 90, 1.8, Vector2(3, 8), Vector3(0, -2, 0), Vector2(0.8, 1.8),
			   Color(0.62, 0.62, 0.64, 0.8), Color(0.5, 0.5, 0.52, 0), 100.0, false)          # gray dust
	_scorch(spot, 1.6)
	shake = max(shake, 0.8)
	fov_kick = max(fov_kick, 3.5)
	_hitstop(3)
	if lethal != null and not _lethal_ok(lethal):
		lethal = null
	for c in cars:
		if not c["alive"]:
			continue
		var d = c["body"].global_position - spot
		var dist = Vector2(d.x, d.z).length()
		if c == lethal or dist < 2.6:
			_shards(c, 4, 8.0)
			_damage(c, 100.0 if c == lethal else 55.0, "SPLAT!", c == lethal)
		elif dist < 8.0:
			var f = 1.0 - dist / 8.0
			f = maxf(f, 0.45)
			c["body"].apply_central_impulse((Vector3(d.x, 0, d.z).normalized() * push_h + Vector3(0, 6.0, 0)) * f * c["body"].mass)
			c["last_push"] = t
			_shards(c, 2, 6.0)
			_damage(c, 25.0 * f, "WHOA!")


# ================================================================== camera + HUD
func _process(_d: float) -> void:
	if hitstop_until > 0.0 and vt() >= hitstop_until:
		Engine.time_scale = 1.0
		hitstop_until = -1.0
	var xs = []
	for c in cars:
		if (c["alive"] or c == winner) and is_instance_valid(c["body"]) and not c["out"]:
			xs.append(c["body"].global_position.x)
	var cx = 0.0
	if xs.size() > 0:
		cx = (xs.max() + xs.min()) / 2.0
	shake *= 0.86
	fov_kick *= 0.84
	var slot = int(floor((t - INTRO_T0) / INTRO_SLOT)) if t >= INTRO_T0 else -1
	if CAM_MODE == "classic" and slot >= 0 and slot < cars.size() and t < GO_T - 1.2:
		var fc = cars[slot]
		var fp = fc["body"].global_position
		camx = fp.x                                         # cut (no glide) like smash25d intro shots
		zoom = 1.55
		_classic_cam(camx, zoom, 0.0)
		if intro_logged < slot:
			intro_logged = slot
			_log("intro", float(slot), fp + Vector3(0, 0.3, 0), fc["nick"] + "|" + fc["vk"] + ("|last" if slot == cars.size() - 1 else ""))
	elif CAM_MODE == "classic" and t < GO_T - 1.2 and slot >= cars.size():
		zoom = 1.0
		camx = 0.0
		_classic_cam(camx, zoom, 0.0)
	elif CAM_MODE == "classic":                             # smash25d camera: pan to the cars, zoom 1.0-1.45 to fit them
		var spread = (xs.max() - xs.min() + 6.0) if xs.size() > 0 else 26.0
		var fit = clampf(1080.0 * 0.95 / (spread * C_F / (C_D + ARENA_HZ - 1.0)), 1.0, 1.45)
		camx += (cx - camx) * 0.1
		zoom += (fit - zoom) * 0.1
		_classic_cam(camx, zoom, fov_kick * 0.025)
	else:
		cam.position = cam.position.lerp(cam_base + Vector3(-cx * 0.12, 0, 0), 0.03)   # whole arena; gentle drift
		cam.look_at(Vector3(cam.position.x, 0, LOOK_Z), Vector3.UP)
		cam.fov = CAM_FOV - fov_kick
	cam.h_offset = randf_range(-shake, shake)
	cam.v_offset = randf_range(-shake, shake)
	for f in fins:                                          # circling fins (ellipse outside the platform)
		var a = f["phase"] + t * f["speed"]
		var p = Vector3(cos(a) * (ARENA_HX + 5.0), WATER_Y + 0.05, ARENA_HZ + sin(a) * (ARENA_HZ + (3.0 if CAM_MODE == "classic" else 6.0)))
		var n = f["node"]
		n.flip_h = (p.x - n.position.x) > 0.0
		n.position = p
	for i in range(cars.size()):
		var c = cars[i]
		var row = hp_rows[i]
		row["bar"].size.x = 150.0 * c["hp"] / 100.0
		row["bar"].color = Color(0.2, 0.85, 0.3) if c["hp"] > 60 else (Color(1, 0.8, 0.1) if c["hp"] > 30 else Color(0.95, 0.2, 0.15))
		row["out"].visible = not c["alive"] and t >= GO_T
		if is_instance_valid(c["body"]) and not c["out"] and c["body"].visible:   # contact shadow follows the car
			var bpos = c["body"].global_position
			c["blob"].visible = bpos.y > -0.5
			c["blob"].position = Vector3(bpos.x, 0.03, bpos.z)
			c["blob_mat"].albedo_color.a = 0.55 * clampf(1.0 - (bpos.y - c["ride"]) / 4.0, 0.0, 1.0)
		else:
			c["blob"].visible = false
		if c["alive"] and is_instance_valid(c["body"]):     # progressive damage look
			var k = 1.0 - c["hp"] / 100.0
			c["spr"].modulate = Color(1, 1, 1).lerp(Color(0.6, 0.55, 0.55), k * 0.85)
			c["smoke"].emitting = c["hp"] < 70.0
			c["fire"].emitting = c["hp"] < 35.0
	title_lbl.visible = true
	sub_lbl.modulate.a = clampf((INTRO_T0 - 0.2 - vt()) / 0.4, 0.0, 1.0)
	for r in hp_rows:                                       # smash25d: no HP panel during the intro
		for nd in r["nodes"]:
			nd.visible = t >= GO_T - 0.5
	if t < GO_T:                                            # engines revving before the start
		for i in range(cars.size()):
			var cc = cars[i]
			if is_instance_valid(cc["body"]):
				cc["spr"].scale = Vector3(1.0, 1.0 + 0.035 * sin(t * 19.0 + i * 1.7), 1.0)
	cta.visible = false                                    # end card = cairo draw_cta overlay (mix3d)
	if winner != null and vt() > win_t + 9.5:              # banner 3 s + end card 6.5 s (CTA line), then stop
		get_tree().quit()


func _ls(size: int, col := Color(1, 0.86, 0.12)) -> LabelSettings:
	var ls = LabelSettings.new()
	ls.font = font
	ls.font_size = size
	ls.font_color = col
	ls.outline_size = int(size * 0.2)
	ls.outline_color = Color(0.07, 0.07, 0.2)
	return ls


func _hud() -> void:
	hud = CanvasLayer.new()
	add_child(hud)
	title_lbl = Label.new()
	title_lbl.text = "SMASH ARENA!"
	title_lbl.label_settings = _ls(96)
	title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_lbl.size = Vector2(1080, 140)
	title_lbl.position = Vector2(0, 90)
	hud.add_child(title_lbl)
	sub_lbl = Label.new()
	sub_lbl.text = "4 FIGHTERS... 1 SURVIVOR!"
	sub_lbl.label_settings = _ls(70, Color(1, 1, 1))
	sub_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub_lbl.size = Vector2(1080, 120)
	sub_lbl.position = Vector2(0, 1480)
	hud.add_child(sub_lbl)
	for i in range(cars.size()):                             # HP panel, top-left (same layout as smash25d)
		var c = cars[i]
		var y = 240 + i * 64
		var bg = ColorRect.new()
		bg.color = Color(0.05, 0.05, 0.15, 0.7)
		bg.position = Vector2(26, y - 26)
		bg.size = Vector2(390, 54)
		hud.add_child(bg)
		var dot = ColorRect.new()
		dot.color = c["col"]
		dot.position = Vector2(40, y - 8)
		dot.size = Vector2(16, 16)
		hud.add_child(dot)
		var nm = Label.new()
		nm.text = c["nick"]
		nm.label_settings = _ls(34, Color(1, 1, 1))
		nm.position = Vector2(66, y - 24)
		hud.add_child(nm)
		var back = ColorRect.new()
		back.color = Color(0.15, 0.15, 0.2)
		back.position = Vector2(246, y - 10)
		back.size = Vector2(150, 20)
		hud.add_child(back)
		var bar = ColorRect.new()
		bar.position = Vector2(246, y - 10)
		bar.size = Vector2(150, 20)
		hud.add_child(bar)
		var out = Label.new()
		out.text = "OUT"
		out.label_settings = _ls(34, Color(1, 0.3, 0.25))
		out.position = Vector2(300, y - 24)
		out.visible = false
		hud.add_child(out)
		hp_rows.append({"bar": bar, "out": out, "nodes": [bg, dot, nm, back, bar]})
	win_lbl = Label.new()
	win_lbl.label_settings = _ls(120)
	win_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	win_lbl.size = Vector2(1080, 180)
	win_lbl.position = Vector2(0, 560)
	win_lbl.visible = false
	hud.add_child(win_lbl)
	cta = Panel.new()
	cta.position = Vector2(140, 820)
	cta.size = Vector2(800, 330)
	cta.visible = false
	var sb = StyleBoxFlat.new()                              # white rounded card like the cairo end card
	sb.bg_color = Color(1, 1, 1, 0.97)
	sb.set_corner_radius_all(36)
	sb.border_color = Color(1, 0.86, 0.12)
	sb.set_border_width_all(8)
	cta.add_theme_stylebox_override("panel", sb)
	hud.add_child(cta)
	var cl = Label.new()
	cl.text = "MEGAWHEEL ARENA\nLIKE  •  SUBSCRIBE"
	cl.label_settings = _ls(62, Color(0.9, 0.12, 0.15))
	cl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	cl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	cl.size = Vector2(800, 330)
	cta.add_child(cl)


func _bubble(world: Vector3, text: String, size := 54) -> void:
	if cam == null or _behind(world):
		return
	var p = _proj(world)
	var l = Label.new()
	l.text = text
	var ls = _ls(size, Color(0.9, 0.15, 0.2))
	ls.outline_color = Color(1, 1, 1)
	ls.outline_size = 16
	l.label_settings = ls
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.size = Vector2(520, 110)
	l.position = Vector2(clampf(p.x - 260, 10, 550), clampf(p.y - 55, 420, 1700))
	l.pivot_offset = Vector2(260, 55)
	l.scale = Vector2(0.3, 0.3)
	hud.add_child(l)
	var tw = create_tween()
	tw.tween_property(l, "scale", Vector2.ONE, 0.18).set_trans(Tween.TRANS_BACK)
	tw.tween_interval(0.8)
	tw.tween_property(l, "modulate:a", 0.0, 0.3)
	tw.tween_callback(l.queue_free)
