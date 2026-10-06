extends Node3D
## LAB pilot C — the world of a story25d scene in 3D (town at night), behind the ORIGINAL characters (overlay.mov).
## Camera: the cairo camera matrix of every frame -> an equivalent pinhole camera. story25d projection:
##   k(z) = F / (D0 + DZ z)  (px per metre at lane depth z), ground_y(z) = Y_H + CAM_H k(z), screen = M (px, py)
## In metres: distance(z) = (D0 + DZ z) / DZ, focal = F / DZ, camera height CAM_H -> identical geometry.
## Look: toon shading (flat cartoon like the cairo art); 3D is used for light, fog and depth, not realism.
##   godot --path project --write-movie out.avi --fixed-fps 30 --quit-after N -- <export_dir> [start_frame]

var dir = "/root/lab/gs/s1"
var S = {}
var frames = []
var start_off = 0
var cam: Camera3D
var rng = RandomNumberGenerator.new()
var lamps = []                     # [SpotLight3D, head material, off_time]
var heads = {}                     # actor id -> SpotLight3D
var eyes_root: Node3D
var eye_l: MeshInstance3D
var eye_r: MeshInstance3D
var eye_glow: OmniLight3D
var head_sil: MeshInstance3D
var steam = []
var kfar = null                    # far Kraggor spec (story25d kraggor_far) + the camera x when he appears
var kfar_cam = 0.0
var keyes = []                     # [MeshInstance3D] his two glowing eyes
var keye_light: OmniLight3D
var krw = 1.0                      # eye radius in metres
var knodes = []                    # sprite + haze: shown ONLY in his shot (v7: he was visible from shot 3 on)
var NIGHT = true                   # scene time: night = moon/fog/lamps; anything else = day look (sun, sky, pastel town)
var WARM = 0.0                     # 0 day .. 1 evening (warmer, lower sun)
var timed = []                     # [Node3D, from_shot, to_shot]: props that appear with a shot (e.g. Siren's barricade)
var blinkers = []                  # [material, phase]: amber warning lights
var dimmers = []                   # [from_shot, to_shot]: the world light goes down (a lonely spotlight moment)
var world_env: Environment
var shot_t0 = {}                   # shot index -> its first frame time (props that act inside a shot)
var crates = []                    # [node, shelf_h, floor_h, fall_shot, dust emitter, landed]
var swing_lamps = []               # [pivot node] hanging lamps that sway a little
var sun_light: DirectionalLight3D


func _ready() -> void:
	var a = OS.get_cmdline_user_args()
	if a.size() > 0:
		dir = a[0]
	if a.size() > 1:
		start_off = int(a[1])
	S = JSON.parse_string(FileAccess.open(dir + "/scene.json", FileAccess.READ).get_as_text())
	frames = JSON.parse_string(FileAccess.open(dir + "/frames.json", FileAccess.READ).get_as_text())["frames"]
	rng.seed = 5
	for fr in frames:
		var si_ = int(fr[1].get("shot", 0))
		if not shot_t0.has(si_):
			shot_t0[si_] = float(fr[1]["t"])
	var tm = str(S["theme"].get("time", S["scene"].get("time", "night")))
	NIGHT = tm == "night"
	WARM = 1.0 if tm in ["evening", "dusk", "sunset"] else (0.35 if tm in ["dawn", "morning"] else 0.0)
	for fr in frames:
		if fr[1].get("kfar") != null:
			kfar = fr[1]["kfar"]
			kfar_cam = float(fr[1]["camx"])
			break
	if str(S["scene"].get("location", "town")) == "garage":
		_environment_interior()
		_garage()
	else:
		_environment()
		_ground()
	var loc = str(S["scene"].get("location", "town"))
	if loc == "garage":
		pass
	elif loc == "arena":
		_arena()
	else:
		_buildings()
		if bool(S["scene"].get("shops", not NIGHT)):
			_shops()
		_trees()
	_props()
	_eyes()
	_kraggor_far()
	cam = Camera3D.new()
	cam.projection = Camera3D.PROJECTION_FRUSTUM
	cam.keep_aspect = Camera3D.KEEP_WIDTH
	cam.near = 0.5
	cam.far = 900.0
	add_child(cam)
	cam.make_current()


# ------------------------------------------------------------------ projection helpers
func dist(z: float) -> float:
	return (float(S["D0"]) + float(S["DZ"]) * z) / float(S["DZ"])


func wp(x: float, z: float, h := 0.0) -> Vector3:
	return Vector3(x, h, -dist(z))


func toon(col: Color) -> StandardMaterial3D:
	var m = StandardMaterial3D.new()
	m.albedo_color = col
	m.diffuse_mode = BaseMaterial3D.DIFFUSE_TOON
	m.specular_mode = BaseMaterial3D.SPECULAR_TOON
	m.roughness = 1.0
	return m


func box(size: Vector3, pos: Vector3, mat: Material) -> MeshInstance3D:
	var mi = MeshInstance3D.new()
	var bm = BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	mi.position = pos
	add_child(mi)
	return mi


# ------------------------------------------------------------------ world
func _environment() -> void:
	if not NIGHT:
		_environment_day()
		return
	var fog = float(S["scene"].get("fog", 0.5))
	var env = Environment.new()
	var sky_m = ProceduralSkyMaterial.new()
	sky_m.sky_top_color = Color(0.02, 0.03, 0.10)
	sky_m.sky_horizon_color = Color(0.09, 0.10, 0.22)
	sky_m.ground_horizon_color = Color(0.09, 0.10, 0.22)
	sky_m.ground_bottom_color = Color(0.02, 0.03, 0.10)
	sky_m.sun_angle_max = 0.0
	var sk = Sky.new()
	sk.sky_material = sky_m
	env.background_mode = Environment.BG_SKY
	env.sky = sk
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.32, 0.38, 0.62)
	env.ambient_light_energy = 0.35
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.glow_enabled = true
	env.glow_intensity = 0.6
	env.glow_bloom = 0.08
	env.volumetric_fog_enabled = true                        # light beams become visible in the fog
	env.volumetric_fog_density = 0.025 + 0.055 * fog
	env.volumetric_fog_albedo = Color(0.7, 0.74, 0.85)
	env.volumetric_fog_emission = Color(0.03, 0.04, 0.08)
	env.volumetric_fog_emission_energy = 0.6
	env.volumetric_fog_length = 90.0
	env.volumetric_fog_anisotropy = 0.35
	var we = WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var moon = DirectionalLight3D.new()                      # cool moonlight from the camera side, soft shadows
	moon.rotation_degrees = Vector3(-38, 150, 0)
	moon.light_color = Color(0.62, 0.7, 1.0)
	moon.light_energy = 0.3
	moon.shadow_enabled = false                              # user 2026-10-05: no building shadows at night (moonlight
	                                                         # is too weak); shadows only from lamps and headlights
	moon.light_volumetric_fog_energy = 0.4
	add_child(moon)
	var md = MeshInstance3D.new()                            # the moon disc, far away, glowing
	var sm = SphereMesh.new()
	sm.radius = 9.0
	sm.height = 18.0
	md.mesh = sm
	var mm = StandardMaterial3D.new()
	mm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mm.albedo_color = Color(1.0, 0.97, 0.85)
	mm.emission_enabled = true
	mm.emission = Color(1.0, 0.95, 0.8)
	mm.emission_energy_multiplier = 2.0
	mm.disable_fog = true
	md.material_override = mm
	md.position = Vector3(40, 70, -320)
	add_child(md)
	for i in range(160):                                     # stars
		var st = MeshInstance3D.new()
		var q = SphereMesh.new()
		q.radius = rng.randf_range(0.25, 0.6)
		q.height = q.radius * 2
		st.mesh = q
		var smat = StandardMaterial3D.new()
		smat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		smat.albedo_color = Color(1, 1, 0.9)
		smat.disable_fog = true
		st.material_override = smat
		st.position = Vector3(rng.randf_range(-400, 500), rng.randf_range(60, 220), -rng.randf_range(380, 460))
		add_child(st)


func _environment_day() -> void:
	# Sun BEHIND the camera (light travels away from it): shadows fall behind the objects, never as dark wedges across
	# the road in front of the cars (user 2026-10-05/06: shadows must not disturb). Soft, short, toon-friendly.
	var env = Environment.new()
	var sky_m = ProceduralSkyMaterial.new()
	sky_m.sky_top_color = Color(0.28, 0.52, 0.90).lerp(Color(0.32, 0.36, 0.70), WARM)
	sky_m.sky_horizon_color = Color(0.74, 0.85, 0.96).lerp(Color(1.0, 0.72, 0.52), WARM)
	sky_m.ground_horizon_color = sky_m.sky_horizon_color
	sky_m.ground_bottom_color = Color(0.45, 0.5, 0.45)
	var sk = Sky.new()
	sk.sky_material = sky_m
	env.background_mode = Environment.BG_SKY
	env.sky = sk
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.75
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure = 1.05
	env.glow_enabled = true
	env.glow_intensity = 0.25
	env.fog_enabled = true                                   # light aerial haze: depth without hiding things
	env.fog_light_color = sky_m.sky_horizon_color
	env.fog_density = 0.0016 + 0.004 * float(S["scene"].get("fog", 0.0))
	env.fog_aerial_perspective = 0.4
	var we = WorldEnvironment.new()
	we.environment = env
	add_child(we)
	world_env = env
	var sun = DirectionalLight3D.new()
	sun_light = sun
	sun.rotation_degrees = Vector3(-52 + 30 * WARM, -28, 0)  # from behind-left of the camera
	sun.light_color = Color(1.0, 0.96, 0.88).lerp(Color(1.0, 0.72, 0.48), WARM)
	sun.light_energy = 1.25 - 0.35 * WARM
	sun.shadow_enabled = true
	sun.shadow_blur = 2.0
	sun.shadow_opacity = 0.55                                # soft: shapes read, nothing goes black
	sun.directional_shadow_max_distance = 140.0
	add_child(sun)
	for i in range(14):                                      # a few soft cartoon clouds far away
		var c = MeshInstance3D.new()
		var sp = SphereMesh.new()
		sp.radius = 1.0
		sp.height = 2.0
		c.mesh = sp
		var cm = StandardMaterial3D.new()
		cm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		cm.albedo_color = Color(1, 1, 1, 0.92).lerp(Color(1.0, 0.85, 0.75, 0.92), WARM)
		cm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		cm.disable_fog = true
		c.material_override = cm
		var w = rng.randf_range(14, 30)
		c.scale = Vector3(w, w * 0.32, 4)
		c.position = Vector3(rng.randf_range(-300, 420), rng.randf_range(70, 130), -rng.randf_range(330, 420))
		add_child(c)


func _ground() -> void:
	var road = toon(Color(0.17, 0.17, 0.2) if NIGHT else Color(0.36, 0.36, 0.4))
	var far_z = dist(3.2)
	var near_z = dist(-0.6)
	var cx = 40.0
	box(Vector3(700, 0.1, far_z - near_z), Vector3(cx, -0.05, -(near_z + far_z) / 2), road)   # asphalt
	var walk = toon(Color(0.33, 0.33, 0.37) if NIGHT else Color(0.66, 0.63, 0.6))
	box(Vector3(700, 0.25, dist(5.0) - far_z), Vector3(cx, 0.07, -(far_z + dist(5.0)) / 2), walk)   # far pavement
	box(Vector3(700, 0.12, near_z - 2.0), Vector3(cx, -0.04, -(near_z + 2.0) / 2), walk)             # near pavement
	var grass = toon(Color(0.08, 0.13, 0.1) if NIGHT else Color(0.38, 0.62, 0.32))
	box(Vector3(900, 0.1, 400), Vector3(cx, -0.06, -dist(5.0) - 200), grass)
	var dash = StandardMaterial3D.new()                      # lane dashes at z = 1.3 every 4 m (as the cairo road)
	dash.albedo_color = Color(0.9, 0.9, 0.85)
	dash.diffuse_mode = BaseMaterial3D.DIFFUSE_TOON
	var x = -300.0
	while x < 380.0:
		box(Vector3(1.6, 0.02, 0.22), Vector3(x + 0.8, 0.005, -dist(1.3)), dash)
		x += 4.0
	var curb = toon(Color(0.5, 0.5, 0.55) if NIGHT else Color(0.85, 0.85, 0.85))
	box(Vector3(700, 0.3, 0.25), Vector3(cx, 0.1, -far_z), curb)


func _buildings() -> void:
	var cols = [Color(0.18, 0.2, 0.34), Color(0.22, 0.2, 0.32), Color(0.16, 0.22, 0.3), Color(0.25, 0.23, 0.36)]
	if not NIGHT:                                            # pastel town by day
		cols = [Color(0.93, 0.78, 0.62), Color(0.72, 0.84, 0.93), Color(0.95, 0.88, 0.7), Color(0.8, 0.74, 0.9),
				Color(0.7, 0.88, 0.78), Color(0.96, 0.7, 0.66)]
	var win_on = StandardMaterial3D.new()
	win_on.albedo_color = Color(1.0, 0.85, 0.45)
	win_on.emission_enabled = NIGHT                          # by day: glass, no glow
	win_on.emission = Color(1.0, 0.8, 0.4)
	win_on.emission_energy_multiplier = 1.2
	var win_off = toon(Color(0.12, 0.13, 0.2))
	for row in range(3):                                     # three layers far back: a skyline, not walls (test 1)
		var z = [45.0, 75.0, 115.0][row]
		var x = -320.0 + rng.randf_range(0, 6)
		while x < 420.0:
			var w = rng.randf_range(9, 18)
			var h = rng.randf_range(14, 30) + row * 10.0
			var d = rng.randf_range(8, 12)
			if kfar != null and dist(z) + d < float(kfar["dist"]):   # in front of far Kraggor: low enough that
				var kd = float(kfar["dist"])                         # his chest + head stand clear (user 05-10)
				var dep = dist(z) + d / 2
				var lx = kfar_cam + (float(kfar["x"]) - kfar_cam) * dep / kd
				var half = (0.32 * float(kfar["height"]) + 3.0) * dep / kd
				if absf(x + w / 2 - lx) < half + w / 2:
					h = minf(h, float(S["CAM_H"]) + (0.42 * float(kfar["height"]) - float(S["CAM_H"])) * dep / kd)
			var bpos = Vector3(x + w / 2, h / 2, -dist(z) - d / 2)
			box(Vector3(w, h, d), bpos, toon(cols[rng.randi() % cols.size()].darkened(row * (0.12 if NIGHT else 0.07))))
			var wy = 2.0
			while wy < h - 1.0:                              # windows on the facade facing the street
				var wx = x + 1.0
				while wx < x + w - 1.0:
					var lit = rng.randf() < (0.18 if NIGHT else 0.5)
					if lit and not NIGHT:
						box(Vector3(1.0, 1.4, 0.05), Vector3(wx + 0.5, wy, -dist(z) + 0.03), toon(Color(0.55, 0.72, 0.88)))
					elif lit:
						box(Vector3(1.0, 1.4, 0.05), Vector3(wx + 0.5, wy, -dist(z) + 0.03), win_on)
					wx += 3.0
				wy += 3.6
			x += w + rng.randf_range(1.0, 4.0)


func _shops() -> void:
	# A row of small, colourful shops close behind the far pavement: the town feels lived-in (not a wall of towers).
	var names = ["BAKERY", "GARAGE", "FLOWERS", "DINER", "TOYS", "BOOKS", "CAFE", "TIRES", "MARKET", "PHARMACY"]
	var cols = [Color(0.95, 0.55, 0.45), Color(0.45, 0.7, 0.95), Color(0.98, 0.82, 0.4), Color(0.6, 0.85, 0.55),
				Color(0.85, 0.6, 0.9), Color(0.98, 0.65, 0.3)]
	var z = float(S["scene"].get("shops_z", 13.0))
	var x = -150.0
	var k = 0
	while x < 260.0:
		var w = rng.randf_range(7, 11)
		var h = rng.randf_range(5.5, 8.5)
		var c = cols[rng.randi() % cols.size()]
		var front = -dist(z)
		box(Vector3(w, h, 6.0), Vector3(x + w / 2, h / 2, front - 3.0), toon(c if not NIGHT else c.darkened(0.6)))
		var glass = StandardMaterial3D.new()                 # shop window: lit at night
		glass.albedo_color = Color(0.6, 0.78, 0.9) if not NIGHT else Color(1.0, 0.85, 0.5)
		glass.emission_enabled = NIGHT
		glass.emission = Color(1.0, 0.8, 0.45)
		glass.emission_energy_multiplier = 0.9
		box(Vector3(w * 0.55, 1.8, 0.08), Vector3(x + w * 0.38, 1.6, front + 0.05), glass)
		box(Vector3(1.2, 2.3, 0.08), Vector3(x + w * 0.82, 1.15, front + 0.05), toon(c.darkened(0.45)))   # door
		var aw = toon(Color(1, 1, 1) if k % 2 == 0 else c.lightened(0.35))   # awning
		var awn = box(Vector3(w * 0.95, 0.12, 1.4), Vector3(x + w / 2, 2.95, front + 0.6), aw)
		awn.rotation_degrees = Vector3(-14, 0, 0)
		var lb = Label3D.new()                               # the shop sign
		lb.text = names[k % names.size()]
		lb.font_size = 96
		lb.pixel_size = 0.012
		lb.modulate = Color(1, 1, 1) if not NIGHT else Color(1.0, 0.9, 0.6)
		lb.outline_size = 18
		lb.outline_modulate = c.darkened(0.6)
		lb.position = Vector3(x + w / 2, h - 1.2, front + 0.06)
		add_child(lb)
		x += w + rng.randf_range(0.4, 1.5)
		k += 1


func _environment_interior() -> void:
	# a room at night: no sky, warm low ambient, a little volumetric haze so the hanging lamp draws a cone
	var env = Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.03, 0.025, 0.02)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.55, 0.45, 0.35)
	env.ambient_light_energy = 0.32
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.glow_enabled = true
	env.glow_intensity = 0.5
	env.volumetric_fog_enabled = true
	env.volumetric_fog_density = 0.018
	env.volumetric_fog_albedo = Color(0.9, 0.85, 0.75)
	env.volumetric_fog_length = 40.0
	var we = WorldEnvironment.new()
	we.environment = env
	add_child(we)
	world_env = env


func _garage() -> void:
	# Sprinkles' garage (S01E02 sc.4): plank walls, concrete floor, shelves with cans and boxes, a workbench with a
	# pegboard, a night window, a hanging lamp (prop "lamp"). Everything warm and a bit dusty.
	var back_z = float(S["scene"].get("wall_z", 4.6))
	box(Vector3(120, 0.1, dist(back_z) - dist(-0.6) + 4), Vector3(4, -0.05, -(dist(back_z) + dist(-0.6) - 4) / 2),
		toon(Color(0.42, 0.4, 0.37)))                         # floor
	var x = -50.0
	var k = 0
	while x < 60.0:                                          # plank wall
		var c = Color(0.55, 0.36, 0.22) if k % 2 == 0 else Color(0.5, 0.32, 0.2)
		box(Vector3(0.62, 7.0, 0.2), Vector3(x + 0.31, 3.5, -dist(back_z) - 0.1), toon(c.lerp(Color(0.6, 0.4, 0.25), rng.randf() * 0.3)))
		x += 0.64
		k += 1
	box(Vector3(120, 0.3, 12), Vector3(4, 7.1, -dist(back_z) + 5), toon(Color(0.2, 0.15, 0.1)))   # ceiling
	var cans = [Color(0.85, 0.2, 0.2), Color(0.2, 0.45, 0.85), Color(0.95, 0.8, 0.2), Color(0.3, 0.7, 0.35), Color(0.9, 0.9, 0.9)]
	for sx in [-14.0, 9.0, 18.0]:                            # shelves
		for hh in [1.3, 2.4, 3.5]:
			box(Vector3(5.0, 0.12, 0.8), Vector3(sx, hh, -dist(back_z) + 0.45), toon(Color(0.45, 0.3, 0.18)))
			var cx = sx - 2.2
			while cx < sx + 2.2:
				if rng.randf() < 0.6:
					var ch = rng.randf_range(0.3, 0.7)
					box(Vector3(rng.randf_range(0.3, 0.7), ch, 0.5), Vector3(cx, hh + 0.06 + ch / 2, -dist(back_z) + 0.45),
						toon(cans[rng.randi() % cans.size()]) if rng.randf() < 0.5 else toon(Color(0.62, 0.48, 0.32)))
				cx += rng.randf_range(0.6, 1.1)
		for sgn in [-1.0, 1.0]:
			box(Vector3(0.1, 3.7, 0.8), Vector3(sx + sgn * 2.5, 1.85, -dist(back_z) + 0.45), toon(Color(0.4, 0.26, 0.16)))
	box(Vector3(4.2, 0.18, 1.2), Vector3(-4.0, 1.05, -dist(back_z) + 0.7), toon(Color(0.5, 0.33, 0.2)))   # workbench
	for lx in [-5.9, -2.1]:
		box(Vector3(0.14, 1.0, 0.14), Vector3(lx, 0.5, -dist(back_z) + 0.7), toon(Color(0.4, 0.26, 0.16)))
	box(Vector3(3.6, 1.8, 0.05), Vector3(-4.0, 2.4, -dist(back_z) + 0.02), toon(Color(0.7, 0.6, 0.45)))   # pegboard
	for q in range(7):
		box(Vector3(0.08, rng.randf_range(0.4, 0.8), 0.06), Vector3(-5.5 + q * 0.5, 2.4, -dist(back_z) + 0.06),
			toon(Color(0.35, 0.35, 0.4)))
	var win = StandardMaterial3D.new()                       # night window
	win.albedo_color = Color(0.15, 0.25, 0.5)
	win.emission_enabled = true
	win.emission = Color(0.2, 0.3, 0.6)
	win.emission_energy_multiplier = 0.6
	box(Vector3(2.6, 1.8, 0.05), Vector3(3.0, 3.6, -dist(back_z) + 0.02), win)
	box(Vector3(2.8, 0.12, 0.08), Vector3(3.0, 3.6, -dist(back_z) + 0.05), toon(Color(0.35, 0.22, 0.12)))
	box(Vector3(0.12, 2.0, 0.08), Vector3(3.0, 3.6, -dist(back_z) + 0.05), toon(Color(0.35, 0.22, 0.12)))


func _hanging_lamp(p) -> void:
	# a bulb under a tin shade on a cord, swaying a little; warm cone of light + dust motes floating in it
	var pivot = Node3D.new()
	pivot.position = wp(float(p.get("x", 2.0)), float(p.get("z", 2.0)), 7.0)
	add_child(pivot)
	var L = float(p.get("drop", 2.2))
	var cord = MeshInstance3D.new()
	var cm = BoxMesh.new()
	cm.size = Vector3(0.03, L, 0.03)
	cord.mesh = cm
	cord.material_override = toon(Color(0.1, 0.1, 0.1))
	cord.position = Vector3(0, -L / 2, 0)
	pivot.add_child(cord)
	var shade = MeshInstance3D.new()
	var sm = CylinderMesh.new()
	sm.top_radius = 0.12
	sm.bottom_radius = 0.55
	sm.height = 0.4
	shade.mesh = sm
	shade.material_override = toon(Color(0.25, 0.4, 0.3))
	shade.position = Vector3(0, -L - 0.1, 0)
	pivot.add_child(shade)
	var bulb = MeshInstance3D.new()
	var bm = SphereMesh.new()
	bm.radius = 0.14
	bm.height = 0.28
	bulb.mesh = bm
	var em = StandardMaterial3D.new()
	em.albedo_color = Color(1, 0.9, 0.6)
	em.emission_enabled = true
	em.emission = Color(1, 0.85, 0.5)
	em.emission_energy_multiplier = 6.0
	bulb.material_override = em
	bulb.position = Vector3(0, -L - 0.3, 0)
	pivot.add_child(bulb)
	var sl = SpotLight3D.new()
	sl.position = Vector3(0, -L - 0.3, 0)
	sl.rotation_degrees = Vector3(-90, 0, 0)
	sl.light_color = Color(1, 0.85, 0.55)
	sl.light_energy = float(p.get("energy", 9.0))
	sl.spot_range = 9.0
	sl.spot_angle = 48.0
	sl.spot_attenuation = 0.8
	sl.light_volumetric_fog_energy = 3.0
	sl.shadow_enabled = true
	pivot.add_child(sl)
	var fill = OmniLight3D.new()                             # bounce from the bulb: the room is not black
	fill.position = Vector3(0, -L - 0.4, 0)
	fill.light_color = Color(1, 0.8, 0.55)
	fill.light_energy = 1.2
	fill.omni_range = 14.0
	pivot.add_child(fill)
	var dust = CPUParticles3D.new()                          # motes in the light
	dust.position = Vector3(0, -L - 2.2, 0)
	dust.amount = 70
	dust.lifetime = 6.0
	dust.preprocess = 6.0
	dust.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	dust.emission_box_extents = Vector3(1.6, 1.8, 1.0)
	dust.direction = Vector3(0.2, 1, 0)
	dust.spread = 180.0
	dust.initial_velocity_min = 0.02
	dust.initial_velocity_max = 0.08
	dust.gravity = Vector3(0, -0.01, 0)
	var qm = QuadMesh.new()
	qm.size = Vector2(0.035, 0.035)
	var dm = StandardMaterial3D.new()
	dm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	dm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	dm.albedo_color = Color(1, 0.95, 0.8, 0.8)
	dm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	qm.material = dm
	dust.mesh = qm
	pivot.add_child(dust)
	swing_lamps.append(pivot)


func _crate(p) -> void:
	# Grandpa's wooden box: on a shelf until its shot, then it falls, bounces and puffs dust
	var node = Node3D.new()
	var x = float(p.get("x", 9.0))
	var z = float(p.get("z", 4.2))
	var shelf = float(p.get("shelf_h", 2.4))
	node.position = wp(x, z, shelf + 0.06)
	add_child(node)
	var body = MeshInstance3D.new()
	var bm = BoxMesh.new()
	bm.size = Vector3(1.1, 0.7, 0.8)
	body.mesh = bm
	body.material_override = toon(Color(0.55, 0.36, 0.2))
	body.position = Vector3(0, 0.35, 0)
	node.add_child(body)
	for yy in [0.15, 0.55]:
		var band = MeshInstance3D.new()
		var bb = BoxMesh.new()
		bb.size = Vector3(1.12, 0.06, 0.82)
		band.mesh = bb
		band.material_override = toon(Color(0.3, 0.2, 0.1))
		band.position = Vector3(0, yy, 0)
		node.add_child(band)
	var dust = CPUParticles3D.new()
	dust.emitting = false
	dust.one_shot = true
	dust.amount = 60
	dust.lifetime = 2.2
	dust.explosiveness = 0.9
	dust.direction = Vector3(0, 1, 0)
	dust.spread = 80.0
	dust.initial_velocity_min = 0.6
	dust.initial_velocity_max = 1.6
	dust.gravity = Vector3(0, -0.4, 0)
	var qm = QuadMesh.new()
	qm.size = Vector2(0.35, 0.35)
	var dmat = StandardMaterial3D.new()
	dmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	dmat.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	dmat.albedo_color = Color(0.85, 0.78, 0.65, 0.4)
	dmat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	qm.material = dmat
	dust.mesh = qm
	dust.position = wp(x, z, 0.2)
	add_child(dust)
	crates.append([node, shelf, float(p.get("floor_z", z)), int(p.get("fall_shot", 1)), dust, false, x])


func _arena() -> void:
	# MegaWheel Raceway (scene 3 town meeting): stepped grandstand with coloured seats and a roof behind the track,
	# catch fence, a banner, floodlight towers (lit at dusk / night, no shadows: contract L01), far skyline.
	var seat_cols = [Color(0.9, 0.25, 0.25), Color(0.95, 0.8, 0.2), Color(0.25, 0.55, 0.95), Color(0.95, 0.95, 0.95)]
	var concrete = toon(Color(0.72, 0.72, 0.76) if not NIGHT else Color(0.3, 0.3, 0.36))
	var z0 = 6.5
	for r in range(7):                                       # tiers
		var z = z0 + r * 1.1
		var h = 0.9 + r * 0.95
		box(Vector3(260, h, 1.6), Vector3(20, h / 2, -dist(z)), concrete)
		var x = -110.0
		var k = 0
		while x < 150.0:                                     # seat blocks
			var c = seat_cols[(k + r) % seat_cols.size()]
			box(Vector3(5.6, 0.45, 0.7), Vector3(x + 2.8, h + 0.22, -dist(z) + 0.3), toon(c if not NIGHT else c.darkened(0.5)))
			x += 6.0
			k += 1
	var top = 0.9 + 6 * 0.95
	var roof = box(Vector3(260, 0.35, 9.0), Vector3(20, top + 4.2, -dist(z0 + 3.5)), toon(Color(0.85, 0.85, 0.9)))
	roof.rotation_degrees = Vector3(6, 0, 0)
	var x2 = -100.0
	while x2 < 140.0:                                        # roof pillars
		box(Vector3(0.35, top + 4.2, 0.35), Vector3(x2, (top + 4.2) / 2, -dist(z0 + 7.0)), toon(Color(0.6, 0.6, 0.66)))
		x2 += 24.0
	var fence = StandardMaterial3D.new()                     # catch fence along the far edge of the track
	fence.albedo_color = Color(0.85, 0.88, 0.9, 0.35)
	fence.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	box(Vector3(260, 1.8, 0.05), Vector3(20, 0.9, -dist(4.6)), fence)
	var x3 = -110.0
	while x3 < 150.0:
		box(Vector3(0.08, 1.9, 0.08), Vector3(x3, 0.95, -dist(4.6)), toon(Color(0.5, 0.5, 0.55)))
		x3 += 4.0
	var banner = box(Vector3(40, 2.2, 0.1), Vector3(10, top + 1.4, -dist(z0 + 6.5) + 0.2), toon(Color(0.12, 0.2, 0.55)))
	var lb = Label3D.new()
	lb.text = str(S["scene"].get("stands_text", "MEGAWHEEL RACEWAY"))
	lb.font_size = 200
	lb.pixel_size = 0.012
	lb.modulate = Color(1, 0.85, 0.2)
	lb.outline_size = 24
	lb.outline_modulate = Color(0.05, 0.05, 0.2)
	lb.position = banner.position + Vector3(0, 0, 0.08)
	add_child(lb)
	var lit = NIGHT or WARM > 0.6
	for tx in [-60.0, -20.0, 20.0, 60.0, 100.0]:             # floodlight towers
		var tz = z0 + 8.5
		box(Vector3(0.5, 26, 0.5), Vector3(tx, 13, -dist(tz)), toon(Color(0.55, 0.55, 0.6)))
		var hm = StandardMaterial3D.new()
		hm.albedo_color = Color(1, 1, 0.92)
		hm.emission_enabled = lit
		hm.emission = Color(1, 0.97, 0.85)
		hm.emission_energy_multiplier = 4.0
		box(Vector3(4.0, 2.2, 0.4), Vector3(tx, 26.5, -dist(tz) + 0.3), hm)
		if lit:
			var sl = SpotLight3D.new()
			sl.position = Vector3(tx, 26, -dist(tz) + 1.0)
			sl.look_at_from_position(sl.position, Vector3(tx, 0, -dist(1.3)))
			sl.light_color = Color(1, 0.96, 0.85)
			sl.light_energy = 6.0
			sl.spot_range = 70.0
			sl.spot_angle = 32.0
			sl.shadow_enabled = false                        # L01: no messy floodlight shadows
			add_child(sl)
	_buildings_far()


func _buildings_far() -> void:
	# the town's skyline far behind the arena (one row, low, hazy)
	var cols = [Color(0.85, 0.7, 0.6), Color(0.65, 0.72, 0.85), Color(0.8, 0.75, 0.65)]
	var x = -260.0
	while x < 320.0:
		var w = rng.randf_range(12, 22)
		var h = rng.randf_range(14, 32)
		var c = cols[rng.randi() % cols.size()]
		box(Vector3(w, h, 10), Vector3(x + w / 2, h / 2, -dist(150.0)), toon(c if not NIGHT else c.darkened(0.7)))
		x += w + rng.randf_range(2, 8)


func _trees() -> void:
	var trunk = toon(Color(0.28, 0.18, 0.12) if NIGHT else Color(0.45, 0.3, 0.2))
	var leaf = toon(Color(0.12, 0.3, 0.18) if NIGHT else Color(0.3, 0.62, 0.3))
	var x = -200.0
	while x < 260.0:
		var z = rng.randf_range(7.0, 10.0)                  # behind the lamps, not under them
		var s = rng.randf_range(0.9, 1.4)
		var tr = MeshInstance3D.new()
		var cy = CylinderMesh.new()
		cy.top_radius = 0.18 * s
		cy.bottom_radius = 0.24 * s
		cy.height = 2.2 * s
		tr.mesh = cy
		tr.material_override = trunk
		tr.position = Vector3(x, 1.1 * s, -dist(z))
		add_child(tr)
		var cr = MeshInstance3D.new()
		var sp = SphereMesh.new()
		sp.radius = 1.5 * s
		sp.height = 2.8 * s
		cr.mesh = sp
		cr.material_override = leaf
		cr.position = Vector3(x, 3.2 * s, -dist(z))
		add_child(cr)
		x += rng.randf_range(9, 18)


func _props() -> void:
	for p in S["scene"].get("props", []):
		if str(p["type"]) == "streetlamps":
			var offs = p.get("off", [])
			var xs = p["xs"]
			for i in range(xs.size()):
				var x = float(xs[i])
				var z = float(p.get("z", 3.4))
				var pole = toon(Color(0.22, 0.23, 0.27))
				box(Vector3(0.18, 5.2, 0.18), wp(x, z, 2.6), pole)
				box(Vector3(0.95, 0.12, 0.14), wp(x + 0.45, z, 5.2), pole)
				var hm = StandardMaterial3D.new()
				hm.albedo_color = Color(1.0, 0.92, 0.6)
				hm.emission_enabled = true
				hm.emission = Color(1.0, 0.85, 0.5)
				hm.emission_energy_multiplier = 3.0
				box(Vector3(0.55, 0.2, 0.3), wp(x + 0.9, z, 5.05), hm)
				if not NIGHT:
					hm.emission_enabled = false
					continue
				var sl = SpotLight3D.new()                   # a real pool of light on the road + a cone in the fog
				sl.position = wp(x + 0.9, z, 4.95)
				sl.rotation_degrees = Vector3(-90, 0, 0)
				sl.light_color = Color(1.0, 0.82, 0.52)
				sl.light_energy = 12.0
				sl.spot_range = 10.0
				sl.spot_angle = 45.0
				sl.spot_attenuation = 0.7
				sl.light_volumetric_fog_energy = 5.0
				sl.shadow_enabled = true
				add_child(sl)
				lamps.append([sl, hm, float(offs[i]) if i < offs.size() else -1.0])
		elif str(p["type"]) == "lamp":
			_hanging_lamp(p)
		elif str(p["type"]) == "crate":
			_crate(p)
		elif str(p["type"]) == "stage":
			_stage(p)
		elif str(p["type"]) == "spotlight":
			_spot(p)
		elif str(p["type"]) == "barricade":
			_barricade(p)
		elif str(p["type"]) == "footprints":
			var tex = _foot_tex()
			var sz = float(p.get("size", 1.0))
			var dr = float(p.get("dir", 1))
			var xs = p["xs"]
			for n in range(xs.size()):
				var zc = float(p.get("z", 1.3)) + (float(p.get("stagger", 0.45)) * (1.0 if n % 2 == 1 else -1.0))
				var dc = Decal.new()                          # flat on the asphalt, toes pointing the way he walked
				dc.size = Vector3(5.6 * sz, 1.0, 3.2 * sz)
				dc.texture_albedo = tex
				dc.albedo_mix = 1.0
				dc.position = wp(float(xs[n]) + dr * 0.06 * sz, zc, 0.2)
				if dr < 0:
					dc.rotation_degrees = Vector3(0, 180, 0)
				add_child(dc)
				steam.append(_steam(wp(float(xs[n]), zc, 0.1)))


func _stage(p) -> void:
	# a low stage for the one who leads (actor "h" = its height in story25d), skirt + sign
	var x = float(p.get("x", 0.0))
	var z = float(p.get("z", 2.6))
	var w = float(p.get("w", 7.0))
	var h = float(p.get("h", 0.75))
	var d = 2.6
	box(Vector3(w, h, d), Vector3(x, h / 2, -dist(z)), toon(Color(0.55, 0.32, 0.2)))
	box(Vector3(w + 0.1, 0.12, d + 0.1), Vector3(x, h + 0.06, -dist(z)), toon(Color(0.75, 0.5, 0.3)))
	box(Vector3(w, h * 0.7, 0.04), Vector3(x, h * 0.45, -dist(z) + d / 2 + 0.03), toon(Color(0.8, 0.15, 0.15)))
	var ramp = float(p.get("ramp", 1.8))                     # ramps: cars drive on and off (G04)
	var rl = sqrt(ramp * ramp + h * h)
	for sgn in [-1.0, 1.0]:
		var rp = box(Vector3(rl, 0.12, d * 0.9), Vector3(x + sgn * (w / 2 + ramp / 2), h / 2, -dist(z)),
			toon(Color(0.6, 0.38, 0.24)))
		rp.rotation.z = sgn * -atan2(h, ramp)
	if p.get("text"):
		var pole_l = box(Vector3(0.1, 3.2, 0.1), Vector3(x - w * 0.45, 1.6, -dist(z) - d / 2), toon(Color(0.4, 0.4, 0.45)))
		var pole_r = box(Vector3(0.1, 3.2, 0.1), Vector3(x + w * 0.45, 1.6, -dist(z) - d / 2), toon(Color(0.4, 0.4, 0.45)))
		box(Vector3(w * 0.92, 0.8, 0.05), Vector3(x, 3.0, -dist(z) - d / 2), toon(Color(1, 0.95, 0.85)))
		var lb = Label3D.new()
		lb.text = str(p["text"])
		lb.font_size = 72
		lb.pixel_size = 0.008
		lb.modulate = Color(0.75, 0.1, 0.1)
		lb.outline_size = 0
		lb.position = Vector3(x, 3.0, -dist(z) - d / 2 + 0.04)
		add_child(lb)


func _spot(p) -> void:
	# a single spotlight pool on one place (e.g. Sprinkles alone in the empty arena); appears with its shot
	var holder = Node3D.new()
	add_child(holder)
	var sl = SpotLight3D.new()
	var tgt = wp(float(p.get("x", 0.0)), float(p.get("z", 1.0)), 0.0)
	sl.position = tgt + Vector3(0, 18, -6)
	sl.look_at_from_position(sl.position, tgt)
	sl.light_color = Color(1, 0.95, 0.8)
	sl.light_energy = float(p.get("energy", 14.0))
	sl.spot_range = 40.0
	sl.spot_angle = float(p.get("angle", 9.0))
	sl.light_volumetric_fog_energy = 3.0
	sl.shadow_enabled = false
	holder.add_child(sl)
	timed.append([holder, int(p.get("from_shot", 0)), int(p.get("to_shot", 9999))])
	if bool(p.get("dim_world", false)):                      # the rest of the arena goes dark in that shot
		dimmers.append([int(p.get("from_shot", 0)), int(p.get("to_shot", 9999))])


func _barricade(p) -> void:
	# Siren's road block ACROSS the road (user 2026-10-06: "garis merahnya harus menyeberangi jalan"): a striped board
	# from the near kerb to the far kerb, a little diagonal so the stripes still read from the side camera, posts at
	# both ends + middle, blinking amber lamps, and the DANGER sign on the far end facing the camera. Appears with its shot.
	var x0 = float(p.get("x", 12.0))
	var skew = float(p.get("skew", 2.6))                     # metres the far end sits further along the road
	var a = Vector3(x0 - skew / 2, 0, -dist(-0.45))          # near kerb
	var b = Vector3(x0 + skew / 2, 0, -dist(3.05))           # far kerb
	var holder = Node3D.new()
	add_child(holder)
	var root = Node3D.new()
	root.position = (a + b) / 2
	root.rotation.y = atan2(a.z - b.z, b.x - a.x)            # local +X runs from the near to the far kerb
	holder.add_child(root)
	var L = a.distance_to(b)
	var n = 64
	var img = Image.create(n, 8, false, Image.FORMAT_RGBA8)
	for xx in range(n):
		for yy in range(8):
			img.set_pixel(xx, yy, Color(0.92, 0.12, 0.1) if int((xx + yy * 1.0) / 8) % 2 == 0 else Color(1, 1, 1))
	var stripe = StandardMaterial3D.new()
	stripe.albedo_texture = ImageTexture.create_from_image(img)
	stripe.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	stripe.uv1_scale = Vector3(L / 3.6, 1, 1)
	stripe.cull_mode = BaseMaterial3D.CULL_DISABLED
	for f in [-0.5, 0.0, 0.5]:
		var post = MeshInstance3D.new()
		var pm = BoxMesh.new()
		pm.size = Vector3(0.14, 1.3, 0.14)
		post.mesh = pm
		post.material_override = toon(Color(0.95, 0.95, 0.95))
		post.position = Vector3(f * L * 0.96, 0.65, 0)
		root.add_child(post)
		if f != 0.0:
			var lamp = MeshInstance3D.new()
			var lm = SphereMesh.new()
			lm.radius = 0.13
			lm.height = 0.26
			lamp.mesh = lm
			var am = StandardMaterial3D.new()
			am.albedo_color = Color(1.0, 0.65, 0.1)
			am.emission_enabled = true
			am.emission = Color(1.0, 0.6, 0.1)
			lamp.material_override = am
			lamp.position = Vector3(f * L * 0.96, 1.4, 0)
			root.add_child(lamp)
			blinkers.append([am, 0.0 if f < 0 else 0.5])
	for hgt in [0.95, 0.45]:                                 # two striped rails, kerb to kerb
		var board = MeshInstance3D.new()
		var bm = BoxMesh.new()
		bm.size = Vector3(L, 0.34 if hgt > 0.5 else 0.22, 0.06)
		board.mesh = bm
		board.material_override = stripe
		board.position = Vector3(0, hgt, 0)
		root.add_child(board)
	var sign_root = Node3D.new()                             # DANGER sign on the far end, facing the camera
	sign_root.position = b + Vector3(0.6, 0, -0.4)
	holder.add_child(sign_root)
	var spole = MeshInstance3D.new()
	var spm = BoxMesh.new()
	spm.size = Vector3(0.12, 2.0, 0.12)
	spole.mesh = spm
	spole.material_override = toon(Color(0.9, 0.9, 0.9))
	spole.position = Vector3(0, 1.0, 0)
	sign_root.add_child(spole)
	var sboard = MeshInstance3D.new()
	var sgm = BoxMesh.new()
	sgm.size = Vector3(2.6, 0.9, 0.05)
	sboard.mesh = sgm
	sboard.material_override = toon(Color(1.0, 0.92, 0.2))
	sboard.position = Vector3(0, 2.15, 0.02)
	sign_root.add_child(sboard)
	var lb = Label3D.new()
	lb.text = str(p.get("text", "DANGER - ROAD CLOSED"))
	lb.font_size = 64
	lb.pixel_size = 0.0052
	lb.modulate = Color(0.1, 0.05, 0.05)
	lb.outline_size = 0
	lb.width = 460
	lb.autowrap_mode = TextServer.AUTOWRAP_WORD
	lb.position = Vector3(0, 2.15, 0.06)
	sign_root.add_child(lb)
	timed.append([holder, int(p.get("from_shot", 0)), int(p.get("to_shot", 9999))])


func _foot_tex() -> ImageTexture:
	# story25d FOOT_PADS (along-road m, across m, radius along, radius across) on a 5.6 x 3.2 m decal;
	# u runs along +X (toes at +X), v along +Z (towards the camera)
	var pads = [[-1.25, 0.0, 1.2, 0.95], [1.55, -0.95, 0.62, 0.42], [1.95, 0.0, 0.62, 0.42], [1.55, 0.95, 0.62, 0.42]]
	var nu = 448
	var nv = 256
	var img = Image.create(nu, nv, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	for y in range(nv):
		for x in range(nu):
			var px = (float(x) / nu - 0.5) * 5.6 - 0.06
			var pz = (float(y) / nv - 0.5) * 3.2
			var inside = false
			var rim = 0.0
			for pr in pads:
				var d = Vector2((px - pr[0]) / pr[2], (pz - pr[1]) / pr[3]).length()
				var dg = Vector2((px - pr[0]) / (pr[2] + 0.28), (pz - pr[1]) / (pr[3] + 0.28)).length()
				if d < 1.0:
					inside = true
				elif dg < 1.0:
					rim = maxf(rim, 0.6 + 0.4 * (1.0 - dg))
			if inside:
				img.set_pixel(x, y, Color(0.02, 0.02, 0.03, 0.95))
			elif rim > 0.0:
				img.set_pixel(x, y, Color(0.55, 0.57, 0.62, 0.8 * rim))     # crushed, lighter asphalt rim
	return ImageTexture.create_from_image(img)


func _kraggor_far() -> void:
	# the sprite of story25d's own Kraggor drawing (sprites/kraggor_far.png), standing between the building rows
	if kfar == null or S.get("kfar") == null:
		return
	var meta = S["kfar"]
	var ext = meta["ext"]
	var hu = float(ext[3])
	var mpu = float(kfar["height"]) / hu                     # metres per drawing unit
	var padu = float(meta["pad"]) / float(meta["spx"])
	var kx = float(kfar["x"])
	var kd = float(kfar["dist"])
	var img = Image.load_from_file(dir + "/sprites/kraggor_far.png")
	var qm = QuadMesh.new()
	qm.size = Vector2((float(ext[2]) + 2 * padu) * mpu, (hu + 2 * padu) * mpu)
	var m = StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_texture = ImageTexture.create_from_image(img)
	m.albedo_color = Color(1, 1, 1, float(kfar.get("silhouette", 0.92)))
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	m.disable_fog = true                                     # 78 m of volumetric fog left 2 % of him (v6 render):
	var q = MeshInstance3D.new()
	q.mesh = qm
	q.material_override = m
	q.position = Vector3(kx, hu / 2 * mpu, -kd)
	q.visible = false
	add_child(q)
	knodes.append(q)
	var bg = MeshInstance3D.new()                            # city haze lit behind him: the shape reads at night
	var bq = QuadMesh.new()
	bq.size = Vector2(qm.size.x * 2.6, qm.size.y * 1.6)
	var bm = StandardMaterial3D.new()
	bm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	bm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	var g = Gradient.new()
	g.set_color(0, Color(0.42, 0.48, 0.66, 0.55))
	g.set_color(1, Color(0.42, 0.48, 0.66, 0.0))
	var gt = GradientTexture2D.new()
	gt.gradient = g
	gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5)
	gt.fill_to = Vector2(1.0, 0.5)
	bm.albedo_texture = gt
	bm.disable_fog = true                                    # the shape reads by alpha, not by the fog
	bg.mesh = bq
	bg.material_override = bm
	bg.position = Vector3(kx, hu * 0.72 * mpu, -kd - 6.0)
	bg.visible = false
	add_child(bg)
	knodes.append(bg)
	var em = StandardMaterial3D.new()
	em.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	em.albedo_color = Color(1.0, 0.85, 0.2)
	em.emission_enabled = true
	em.emission = Color(1.0, 0.8, 0.15)
	em.emission_energy_multiplier = 8.0
	em.disable_fog = true
	krw = 32.0 * mpu
	var cxu = float(ext[0]) + float(ext[2]) / 2
	for e in meta["eyes"]:
		var s = MeshInstance3D.new()
		var sp = SphereMesh.new()
		sp.radius = 1.0
		sp.height = 2.0
		s.mesh = sp
		s.material_override = em
		s.position = Vector3(kx + (float(e[0]) - cxu) * mpu, (float(ext[1]) + hu - float(e[1])) * mpu, -kd + 1.0)
		s.visible = false
		add_child(s)
		keyes.append(s)
	keye_light = OmniLight3D.new()
	keye_light.light_color = Color(1.0, 0.75, 0.2)
	keye_light.light_volumetric_fog_energy = 4.0
	keye_light.omni_range = krw * 10.0
	keye_light.position = (keyes[0].position + keyes[1].position) / 2 + Vector3(0, 0, 2.0)
	keye_light.visible = false
	add_child(keye_light)


func _steam(pos: Vector3) -> CPUParticles3D:
	var e = CPUParticles3D.new()
	e.position = pos
	e.amount = 26
	e.lifetime = 2.2
	e.direction = Vector3(0, 1, 0)
	e.spread = 18.0
	e.initial_velocity_min = 0.4
	e.initial_velocity_max = 0.9
	e.gravity = Vector3(0, 0.05, 0)
	e.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	e.emission_sphere_radius = 1.4
	e.scale_amount_min = 0.6
	e.scale_amount_max = 1.4
	var qm = QuadMesh.new()
	qm.size = Vector2(0.9, 0.9)
	var m = StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	m.vertex_color_use_as_albedo = true
	var g = Gradient.new()
	g.set_color(0, Color(0.85, 0.88, 0.95, 0.35))
	g.set_color(1, Color(0.85, 0.88, 0.95, 0.0))
	var gt = GradientTexture2D.new()
	gt.gradient = g
	gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5)
	gt.fill_to = Vector2(1.0, 0.5)
	m.albedo_texture = gt
	qm.material = m
	e.mesh = qm
	var ramp = Gradient.new()
	ramp.set_color(0, Color(1, 1, 1, 0.9))
	ramp.set_color(1, Color(1, 1, 1, 0.0))
	e.color_ramp = ramp
	add_child(e)
	return e


func _eyes() -> void:
	eyes_root = Node3D.new()
	add_child(eyes_root)
	var em = StandardMaterial3D.new()
	em.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	em.albedo_color = Color(1.0, 0.85, 0.2)
	em.emission_enabled = true
	em.emission = Color(1.0, 0.8, 0.15)
	em.emission_energy_multiplier = 6.0
	for side in [-1, 1]:
		var e = MeshInstance3D.new()
		var sp = SphereMesh.new()
		sp.radius = 0.5
		sp.height = 1.0
		e.mesh = sp
		e.material_override = em
		eyes_root.add_child(e)
		if side < 0:
			eye_l = e
		else:
			eye_r = e
	eye_glow = OmniLight3D.new()
	eye_glow.light_color = Color(1.0, 0.75, 0.2)
	eye_glow.light_energy = 3.0
	eye_glow.light_volumetric_fog_energy = 4.0
	eyes_root.add_child(eye_glow)
	head_sil = MeshInstance3D.new()                          # the giant head: a dark shape in the fog
	var hs = SphereMesh.new()
	hs.radius = 1.0
	hs.height = 1.6
	head_sil.mesh = hs
	var hm = StandardMaterial3D.new()
	hm.albedo_color = Color(0.03, 0.04, 0.06)
	hm.roughness = 1.0
	head_sil.material_override = hm
	eyes_root.add_child(head_sil)
	eyes_root.visible = false


# ------------------------------------------------------------------ per frame
func _process(_d: float) -> void:
	var i = clampi(start_off + Engine.get_process_frames() - 1, 0, frames.size() - 1)
	var f = frames[i][1]
	var t = float(f["t"])
	var m = f["m"]                                           # cairo: x' = xx x + xy y + x0, y' = yx x + yy y + y0
	var xx = float(m[0])
	var yx = float(m[1])
	var xy = float(m[2])
	var yy = float(m[3])
	var x0 = float(m[4])
	var y0 = float(m[5])
	var Wd = float(S["W"])
	var Hd = float(S["H"])
	var fpx = float(S["F"]) / float(S["DZ"])
	var sc = sqrt(absf(xx * yy - xy * yx))
	var roll = atan2(yx, xx)
	var px = xx * float(S["CX"]) + xy * float(S["Y_H"]) + x0      # where the optical axis lands on screen
	var py = yx * float(S["CX"]) + yy * float(S["Y_H"]) + y0
	# v7 fix (user 2026-10-06, car "floating" in the dutch shot): the roll sign was flipped, so the road tilted one
	# way and the cairo car the other. Derivation: Godot view = Rz(-roll)^-1 applied to the world; for a world offset
	# (dx, dy) at depth d it gives screen (dx cos + dy sin, dx sin - dy cos) f/d = cairo rotate(tilt). The lens shift
	# is applied after the roll, i.e. directly in screen axes.
	var v = Vector2(px - Wd / 2, py - Hd / 2)
	var focal = fpx * sc
	cam.position = Vector3(float(f["camx"]), float(S["CAM_H"]), 0)
	cam.rotation = Vector3(0, 0, roll)
	cam.size = Wd / focal * cam.near
	cam.frustum_offset = Vector2(-v.x / focal * cam.near, v.y / focal * cam.near)
	var shot = int(f.get("shot", 0))
	if sun_light != null:                                    # dim the world for a spotlight moment (eased)
		var dim = false
		for dm in dimmers:
			if shot >= int(dm[0]) and shot <= int(dm[1]):
				dim = true
		var target = 0.25 if dim else 1.0
		sun_light.light_energy = lerpf(sun_light.light_energy, (1.25 - 0.35 * WARM) * target, 0.06)
		world_env.ambient_light_energy = lerpf(world_env.ambient_light_energy, 0.75 * target, 0.06)
	for tp in timed:
		tp[0].visible = shot >= int(tp[1]) and shot <= int(tp[2])
	for lp in swing_lamps:                                   # a gentle sway
		lp.rotation.z = 0.05 * sin(t * 1.1)
		lp.rotation.x = 0.03 * sin(t * 0.8 + 1.0)
	for cr in crates:                                        # fall: g = 9.8, a small bounce, then rests
		var fs = int(cr[3])
		if shot < fs or not shot_t0.has(fs):
			continue
		var u = t - float(shot_t0[fs]) - 0.4
		var y = float(cr[1])
		if u > 0:
			var tf = sqrt(2.0 * y / 9.8)
			if u < tf:
				y = y - 4.9 * u * u
				cr[0].rotation.z = -0.9 * u / tf
			else:
				var ub = u - tf
				y = maxf(0.0, 0.35 * sin(minf(ub / 0.35, 1.0) * PI)) if ub < 0.35 else 0.0
				cr[0].rotation.z = -0.25
				if not cr[5]:
					cr[4].restart()
					cr[4].emitting = true
					cr[5] = true
		cr[0].position.y = y + 0.06 * float(y > 0.0)
		cr[0].position.z = -dist(float(cr[2])) if u > 0 else cr[0].position.z
	for bl in blinkers:
		bl[0].emission_energy_multiplier = 3.0 if fmod(t * 1.5 + float(bl[1]), 1.0) < 0.5 else 0.2
	# street lamps: flicker for half a second, then dark (same schedule as the cairo version)
	for L in lamps:
		var on = 1.0
		var off_t = float(L[2])
		if off_t >= 0.0 and t > off_t - 0.5:
			on = 0.0 if t >= off_t else (1.0 if int((t - off_t) * 23) % 3 != 0 else 0.15)
		L[0].light_energy = 12.0 * on
		L[1].emission_energy_multiplier = 3.0 * on + 0.05
	# headlights: one spot per car, at the front, aimed down the road; flicker = Kraggor is near
	var seen = {}
	for a in f["actors"]:
		var aid = str(a[0])
		seen[aid] = true
		if not heads.has(aid):
			var sl = SpotLight3D.new()
			sl.light_color = Color(1.0, 0.95, 0.78)
			sl.spot_range = 22.0
			sl.spot_angle = 24.0
			sl.spot_attenuation = 0.6
			sl.light_volumetric_fog_energy = 7.0
			sl.shadow_enabled = true
			add_child(sl)
			heads[aid] = sl
		var face = float(a[3])
		var small = float(a[5])
		var bw = float(a[6])
		var bh = float(a[7])
		var wr = float(a[8])
		var hl = heads[aid]
		hl.visible = NIGHT                                       # by day no headlight beams
		hl.position = wp(float(a[1]) + face * bw * 0.5 * small, float(a[2]), (wr + bh * 0.35 + float(a[4])) * small)
		hl.rotation = Vector3(deg_to_rad(-6), deg_to_rad(-90 if face > 0 else 90), 0)
		var on2 = 1.0
		if bool(a[9]):
			var ph = fmod(t * 7.3, 1.0)
			on2 = 0.12 if (ph < 0.22 or (ph > 0.5 and ph < 0.58)) else 1.0
		hl.light_energy = 9.0 * on2
	for aid in heads:
		if not seen.has(aid):
			heads[aid].visible = false
	# far Kraggor: his eyes open a beat after the cut, slow blink
	if keyes.size() > 0:
		var kf = f.get("kfar")
		for nd in knodes:
			nd.visible = kf != null
		var op = 0.0
		if kf != null:
			op = 1.0
			if kf.get("eyes_at") != null:
				op = clampf((float(kf["u"]) - float(kf["eyes_at"])) / 0.5, 0.0, 1.0)
			if fmod(t * 0.6, 3.0) < 0.12:
				op = 0.0
		for e in keyes:
			e.visible = op > 0.0
			e.scale = Vector3(krw * 0.45, krw * 0.45 * maxf(0.08, op), krw * 0.45)
		keye_light.visible = op > 0.0
		keye_light.light_energy = 3.0 * op
	# Kraggor's eyes: given in screen space by the shot -> placed deep in the fog on that screen spot
	var ey = f.get("eyes")
	eyes_root.visible = ey != null
	if ey != null:
		var depth = 36.0                                     # in front of the skyline, deep in the fog
		var ex = float(ey.get("sx", 0.8)) * Wd
		var eyy = float(ey.get("sy", 0.3)) * Hd
		var r = float(ey.get("r", 14)) * Hd / 1080.0
		var det = xx * yy - xy * yx                          # screen -> pre-zoom cairo px -> world at that depth
		var qx = ex - x0
		var qy = eyy - y0
		var pxw = (yy * qx - xy * qy) / det
		var pyw = (-yx * qx + xx * qy) / det
		var wx = float(f["camx"]) + (pxw - float(S["CX"])) * depth / fpx
		var wy = float(S["CAM_H"]) - (pyw - float(S["Y_H"])) * depth / fpx
		eyes_root.position = Vector3(wx, wy, -depth)
		var sep = 2.4 * r * depth / focal
		var er = 0.9 * r * depth / focal
		var blink = 0.08 if fmod(t * 0.6, 3.0) < 0.12 else 1.0
		eye_l.visible = false                                # the eyes + head are drawn by story25d (overlay)
		eye_r.visible = false
		eye_l.position = Vector3(-sep, 0, 0)
		eye_r.position = Vector3(sep, 0, 0)
		eye_l.scale = Vector3(er, er * blink, er)
		eye_r.scale = Vector3(er, er * blink, er)
		eye_glow.omni_range = sep * 5.0
		var sil = float(ey.get("silhouette", 0.0))
		head_sil.visible = false                             # (sil kept for reference: the overlay draws the head)
		head_sil.position = Vector3(0, sep * 0.8, -sep * 1.5)
		head_sil.scale = Vector3(sep * 4.5, sep * 4.0, sep * 3.0)
