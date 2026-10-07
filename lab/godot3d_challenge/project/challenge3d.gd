extends Node3D
## LAB — 3D CHALLENGE sample. The aired engine (sim_engine.py) decides everything: physics, story, timeline, camera,
## car sizes, moods, HUD and audio (export_challenge.py writes them). This scene only re-draws the world in 3D:
## a road with real depth (pits are trenches, the front face shows the 2D profile we know), lit paper-cut cars,
## layered landscape, and much bigger crash damage (panels + glass + bolts flying with physics, sparks, flash, smoke,
## fire, POW). Camera = the engine's 2D camera: 72 px/m x zoom at the car plane, world anchor at screen y 1290.
##   godot --path project --write-movie out.avi --fixed-fps 30 --quit-after N -- <export_dir>

const ROAD_HZ = 3.0                                      # road half width (car plane z = 0)
const FOV = 28.0
const TILT = 7.0                                         # degrees down: the road top and the pits read as 3D
var dir = "/root/lab/ch3d/s1"
var scene = {}
var frames = []
var cast = {}
var tex = {}
var cam: Camera3D
var car: Node3D
var body: MeshInstance3D
var body_mat: ShaderMaterial
var wheels = []
var blob: MeshInstance3D
var fx_root: Node3D
var smoke: CPUParticles3D
var fire: CPUParticles3D
var dot_tex: GradientTexture2D
var cur_vk = ""
var start_off = 0                                        # test renders: start at this output frame
var last_li = -1
var last_st = -1.0
var fired = {}
var rng = RandomNumberGenerator.new()
var pow_tex: ImageTexture
var dmg = 0.0                                            # body crumple 0..1 (per level pass)
var dmg_target = 0.0
var hit_uv = Vector2(0.75, 0.5)
var burn = 0.0
var spray: CPUParticles3D
var vent_fx = []
var torches = []                                         # dungeon torches that flicker
var axe_fx = []                                          # dungeon axes (series dungeon)
var ogre_fx = []                                         # dungeon ogres


func _ready() -> void:
	var a = OS.get_cmdline_user_args()
	if a.size() > 0:
		dir = a[0]
	if a.size() > 1:
		start_off = int(a[1])
	scene = JSON.parse_string(FileAccess.open(dir + "/scene.json", FileAccess.READ).get_as_text())
	frames = JSON.parse_string(FileAccess.open(dir + "/frames.json", FileAccess.READ).get_as_text())["frames"]
	cast = scene["cast"]
	rng.seed = 7
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
	for vk in cast:
		for m in ["normal", "scared", "whoa", "dizzy", "happy", "broken"]:
			tex[vk + "_" + m] = _img(dir + "/sprites/" + vk + "_" + m + ".png")
		tex[vk + "_wheel"] = _img(dir + "/sprites/" + vk + "_wheel.png")
	_environment()
	_track()
	_landscape()
	_props()
	if _is_dungeon():
		_axes()
		_ogres()
	_car()
	fx_root = Node3D.new()
	add_child(fx_root)
	cam = Camera3D.new()
	cam.keep_aspect = Camera3D.KEEP_WIDTH
	cam.fov = FOV
	cam.far = 900.0
	add_child(cam)
	cam.make_current()


func is_vulkan() -> bool:
	return RenderingServer.get_current_rendering_driver_name() == "vulkan"


func _img(p: String) -> ImageTexture:
	return ImageTexture.create_from_image(Image.load_from_file(p))


func _mat(col: Color, rough := 0.85) -> StandardMaterial3D:
	var m = StandardMaterial3D.new()
	m.albedo_color = col
	m.roughness = rough
	return m


func ground_h(x: float) -> float:
	var tr = scene["track"]
	for i in range(tr.size() - 1):
		var p0 = tr[i]
		var p1 = tr[i + 1]
		if p1[0] > p0[0] and p0[0] <= x and x <= p1[0]:
			return lerpf(p0[1], p1[1], (x - p0[0]) / (p1[0] - p0[0]))
	return 0.0


# ================================================================== world
func _environment() -> void:
	var th = scene["theme"]
	var sky = scene["sky"]
	var env = Environment.new()
	var sk = Sky.new()
	var sm = ProceduralSkyMaterial.new()
	var top = sky[0][1]
	var hor = sky[sky.size() - 1][1]
	sm.sky_top_color = Color(top[0], top[1], top[2])
	sm.sky_horizon_color = Color(hor[0], hor[1], hor[2])
	sm.ground_horizon_color = Color(hor[0], hor[1], hor[2])
	sm.ground_bottom_color = Color(0.2, 0.25, 0.2)
	sm.sun_angle_max = 30.0
	sk.sky_material = sm
	env.background_mode = Environment.BG_SKY
	env.sky = sk
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(1, 0.97, 0.95) if not scene["night"] else Color(0.55, 0.6, 0.85)
	env.ambient_light_energy = 0.55 * float(scene["light"])
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.glow_enabled = true
	env.glow_intensity = 0.35
	env.fog_enabled = true                                   # aerial perspective: far layers fade into the sky
	env.fog_light_color = Color(hor[0], hor[1], hor[2])
	env.fog_density = 0.0012
	env.fog_sky_affect = 0.0
	if _is_dungeon():                                        # a torch-lit hall: no sky, warm ambient light
		env.background_mode = Environment.BG_COLOR
		env.background_color = Color(0.05, 0.04, 0.06)
		env.ambient_light_color = Color(0.9, 0.72, 0.66)
		env.ambient_light_energy = 0.9
		env.fog_light_color = Color(0.1, 0.06, 0.07)
		env.fog_density = 0.003
	var we = WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun = DirectionalLight3D.new()                       # from the camera side (CONFIG_BEST lesson 10)
	var tm = th["time"]
	sun.rotation_degrees = {"morning": Vector3(-28, 145, 0), "noon": Vector3(-62, 160, 0),
							"sunset": Vector3(-18, 125, 0), "night": Vector3(-45, 150, 0)}.get(tm, Vector3(-55, 150, 0))
	sun.light_color = {"morning": Color(1, 0.9, 0.78), "noon": Color(1, 0.98, 0.94), "sunset": Color(1, 0.72, 0.5),
					   "night": Color(0.6, 0.7, 1.0)}.get(tm, Color(1, 1, 1))
	sun.light_energy = 1.15 * float(scene["light"]) * (0.45 if scene["night"] else 1.0) * (0.35 if _is_dungeon() else 1.0)
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 90.0
	add_child(sun)


func _quad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, n: Vector3) -> void:
	for p in [a, b, c, a, c, d]:
		st.set_normal(n)
		st.set_uv(Vector2(p.x * 0.25, p.z * 0.25 + p.y * 0.25))
		st.add_vertex(p)


func _track() -> void:
	## road = the track polyline extruded across z; pits become trenches. Front face = the 2D profile.
	var tr = scene["track"]
	var top = SurfaceTool.new()
	var dirt = SurfaceTool.new()
	var wood = SurfaceTool.new()
	for t in [top, dirt, wood]:
		t.begin(Mesh.PRIMITIVE_TRIANGLES)
	var shape_faces = PackedVector3Array()
	var ramp_x = []
	for r in scene["ramps"]:
		ramp_x.append([r[0], r[1]])
	for i in range(tr.size() - 1):
		var p0 = Vector3(tr[i][0], tr[i][1], 0)
		var p1 = Vector3(tr[i + 1][0], tr[i + 1][1], 0)
		var a = Vector3(p0.x, p0.y, ROAD_HZ)
		var b = Vector3(p1.x, p1.y, ROAD_HZ)
		var c = Vector3(p1.x, p1.y, -ROAD_HZ)
		var d = Vector3(p0.x, p0.y, -ROAD_HZ)
		var target = dirt
		var n = Vector3.UP
		if p1.x > p0.x:
			var seg = (p1 - p0).normalized()
			n = Vector3(-seg.y, seg.x, 0)
			var is_ramp = false
			for rx in ramp_x:
				if p0.x >= rx[0] - 0.01 and p1.x <= rx[1] + 0.01 and p1.y > p0.y:
					is_ramp = true
			target = wood if is_ramp else (top if p0.y >= -0.01 and p1.y >= -0.01 else dirt)
		else:
			n = Vector3(1, 0, 0) if p1.y > p0.y else Vector3(-1, 0, 0)
		_quad(target, a, b, c, d, n)
		for p in [a, b, c, a, c, d]:
			shape_faces.append(p)
	var tops = [[top, _mat(Color(0.33, 0.31, 0.37) if _is_dungeon() else Color(0.22, 0.22, 0.25), 0.8)], [dirt, _mat(Color(0.26, 0.2, 0.2) if _is_dungeon() else Color(0.3, 0.2, 0.15))],
				[wood, _mat(Color(0.62, 0.42, 0.22))]]
	for pair in tops:
		pair[1].cull_mode = BaseMaterial3D.CULL_DISABLED
		var mi = MeshInstance3D.new()
		mi.mesh = pair[0].commit()
		mi.material_override = pair[1]
		add_child(mi)
	# front + back faces: the 2D profile (dirt strata, asphalt rim)
	var poly = PackedVector2Array()
	for p in tr:
		poly.append(Vector2(p[0], p[1]))
	poly.append(Vector2(tr[tr.size() - 1][0], -40.0))
	poly.append(Vector2(tr[0][0], -40.0))
	var idx = Geometry2D.triangulate_polygon(poly)
	var sh = Shader.new()
	sh.code = """
shader_type spatial;
render_mode cull_disabled, unshaded;   // a cross-section like the 2D art: same colours on GPU (Vulkan) and CPU
uniform bool lin = false;              // Vulkan: shader colours are linear -> convert the sRGB palette
uniform bool stone = false;            // dungeon: the cross-section is stone bricks, not dirt strata
float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
void fragment() {
	vec3 w = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float band = floor((w.y + sin(w.x * 0.35) * 0.5) * 0.9);
	vec3 c = mix(vec3(0.44, 0.31, 0.23), vec3(0.4, 0.28, 0.2), mod(band, 2.0));
	c = mix(c, vec3(0.3, 0.2, 0.15), smoothstep(-6.0, -12.0, w.y + sin(w.x * 0.6) * 0.8));
	vec2 cell = floor(w.xy * 1.6);
	vec2 f = fract(w.xy * 1.6) - 0.5;
	float r = 0.12 + 0.18 * h(cell + 3.0);
	float pebble = step(0.82, h(cell)) * step(length(f), r);          // round pebbles like the aired art
	if (stone) {
		float row = floor(w.y * 0.8);
		vec2 bc = vec2(w.x * 0.35 + mod(row, 2.0) * 0.5, w.y * 0.8);
		vec2 fc = fract(bc);
		float mortar = clamp(step(fc.x, 0.06) + step(fc.y, 0.1), 0.0, 1.0);
		c = mix(vec3(0.36, 0.33, 0.39) * (0.85 + 0.3 * h(floor(bc))), vec3(0.12, 0.11, 0.14), mortar);
		c = mix(c, vec3(0.15, 0.13, 0.17), smoothstep(-6.0, -12.0, w.y));
		pebble = 0.0;
	}
	vec3 o = mix(c, c * 0.72, pebble);
	ALBEDO = lin ? pow(o, vec3(2.2)) : o;
	ROUGHNESS = 0.95;
}
"""
	var fm = ShaderMaterial.new()
	fm.shader = sh
	fm.set_shader_parameter("lin", is_vulkan())
	fm.set_shader_parameter("stone", _is_dungeon())
	for zz in [ROAD_HZ, -ROAD_HZ]:
		var st = SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		for k in range(0, idx.size(), 3):
			var order = [idx[k], idx[k + 1], idx[k + 2]] if zz > 0 else [idx[k], idx[k + 2], idx[k + 1]]
			for q in order:
				st.set_normal(Vector3(0, 0, 1))                      # back face too: seen through the pits
				st.add_vertex(Vector3(poly[q].x, poly[q].y, zz))
		var mi = MeshInstance3D.new()
		mi.mesh = st.commit()
		mi.material_override = fm
		add_child(mi)
	# road paint: dashed centre line + white edge lines on the flat asphalt
	var paint = _mat(Color(0.95, 0.95, 0.9), 0.6)
	for i in range(tr.size() - 1):
		if tr[i][1] == 0 and tr[i + 1][1] == 0 and tr[i + 1][0] > tr[i][0]:
			var x = tr[i][0] + 1.0
			while x < tr[i + 1][0] - 1.0:
				_box(Vector3(1.6, 0.02, 0.16), Vector3(x + 0.8, 0.012, 1.1), paint)
				x += 3.2
			var ln = tr[i + 1][0] - tr[i][0]
			_box(Vector3(ln, 0.02, 0.12), Vector3(tr[i][0] + ln / 2, 0.012, ROAD_HZ - 0.25), paint)
	# pits filled with liquid (lava / water series)
	if scene["pit_kind"] in ["lava", "water"]:
		for p in scene["pits"]:
			var lm = StandardMaterial3D.new()
			if scene["pit_kind"] == "lava":
				lm.albedo_color = Color(0.95, 0.3, 0.03) if _is_dungeon() else Color(1, 0.45, 0.05)
				lm.emission_enabled = true
				lm.emission = Color(1, 0.28, 0.02) if _is_dungeon() else Color(1, 0.4, 0.05)
				lm.emission_energy_multiplier = 1.2 if _is_dungeon() else 2.5
			var depth = -p[2] + (1.3 if scene["pit_kind"] == "lava" else p[2] - 0.8)
			if scene["pit_kind"] == "water":
				var wm = MeshInstance3D.new()
				var pl = PlaneMesh.new()
				pl.size = Vector2(p[1] - p[0], ROAD_HZ * 2)
				wm.mesh = pl
				wm.material_override = _water_mat(false)
				wm.position = Vector3((p[0] + p[1]) / 2, depth, 0)
				add_child(wm)
				continue
			_box(Vector3(p[1] - p[0], 0.05, ROAD_HZ * 2), Vector3((p[0] + p[1]) / 2, depth, 0), lm)
			if scene["pit_kind"] == "lava":
				var o = OmniLight3D.new()
				o.position = Vector3((p[0] + p[1]) / 2, depth + 1.0, 1.0)
				o.light_color = Color(1, 0.5, 0.1)
				o.light_energy = 3.0
				o.omni_range = 8.0
				add_child(o)
	var sb = StaticBody3D.new()                              # debris bounces on the real track
	var cs = CollisionShape3D.new()
	var cps = ConcavePolygonShape3D.new()
	cps.set_faces(shape_faces)
	cs.shape = cps
	sb.add_child(cs)
	add_child(sb)


func _water_mat(alpha_edge: bool) -> ShaderMaterial:
	## wet, reflective water with ripples; puddles get a ragged natural edge (alpha noise) instead of a rectangle
	var sh = Shader.new()
	sh.code = """
shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_disabled;
uniform bool edge = true;
uniform bool lin = false;
float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float n(vec2 p) { vec2 i = floor(p); vec2 f = fract(p); f = f * f * (3.0 - 2.0 * f);
	return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
varying vec3 wp;
void vertex() { wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
	float a = 0.85;
	if (edge) {
		vec2 c = UV - 0.5;
		float r = length(c * vec2(1.0, 1.6)) * 2.0 + (n(wp.xz * 1.3) - 0.5) * 0.55 + (n(wp.xz * 4.0) - 0.5) * 0.15;
		a = smoothstep(1.0, 0.82, r);
		if (a < 0.02) discard;
	}
	float rip = n(wp.xz * 2.2 + vec2(TIME * 0.6, TIME * 0.4)) + n(wp.xz * 5.0 - TIME * 0.9) * 0.5;
	vec3 deep = vec3(0.05, 0.25, 0.42);
	vec3 sky = vec3(0.45, 0.65, 0.82);
	float fres = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 3.0);
	vec3 o = mix(deep, sky, 0.12 + 0.3 * fres + 0.12 * rip);
	ALBEDO = lin ? pow(o, vec3(2.2)) : o;
	NORMAL = normalize(NORMAL + vec3((rip - 0.75) * 0.25, 0.0, (rip - 0.75) * 0.15));
	ROUGHNESS = 0.06;
	METALLIC = 0.15;
	SPECULAR = 0.6;
	ALPHA = a;
}
"""
	var m = ShaderMaterial.new()
	m.shader = sh
	m.set_shader_parameter("edge", alpha_edge)
	m.set_shader_parameter("lin", is_vulkan())
	return m


func _box(size: Vector3, pos: Vector3, mat: Material) -> MeshInstance3D:
	var mi = MeshInstance3D.new()
	var bm = BoxMesh.new()
	bm.size = size
	mi.mesh = bm
	mi.material_override = mat
	mi.position = pos
	add_child(mi)
	return mi


func _landscape() -> void:
	if _is_dungeon():
		_dungeon_hall()
		return
	var loc = scene["theme"]["location"]
	var grass_col = {"desert": Color(0.86, 0.72, 0.45), "beach": Color(0.9, 0.82, 0.6), "volcano": Color(0.3, 0.24, 0.22),
					 "city": Color(0.45, 0.5, 0.42), "snow": Color(0.92, 0.95, 1.0)}.get(loc, Color(0.24, 0.38, 0.25))
	var gp = MeshInstance3D.new()                            # ground behind and in front of the road
	var pm = PlaneMesh.new()
	pm.size = Vector2(500, 260)
	gp.mesh = pm
	gp.material_override = _mat(grass_col, 0.95)
	gp.position = Vector3(60, -0.01, -ROAD_HZ - 130)
	add_child(gp)
	var x0 = -60.0
	while x0 < 240.0:                                        # mid layer: trees / cacti / rocks with depth
		var z = -ROAD_HZ - rng.randf_range(6, 45)
		var s = rng.randf_range(0.8, 1.6)
		if loc in ["desert", "volcano"]:
			var rk = MeshInstance3D.new()
			var sp = SphereMesh.new()
			sp.radius = 1.2 * s
			sp.height = 1.6 * s
			rk.mesh = sp
			rk.material_override = _mat(grass_col.darkened(0.3))
			rk.position = Vector3(x0, 0.3 * s, z)
			add_child(rk)
		else:
			var trunk = MeshInstance3D.new()
			var cy = CylinderMesh.new()
			cy.top_radius = 0.18 * s
			cy.bottom_radius = 0.25 * s
			cy.height = 1.6 * s
			trunk.mesh = cy
			trunk.material_override = _mat(Color(0.42, 0.28, 0.16))
			trunk.position = Vector3(x0, 0.8 * s, z)
			add_child(trunk)
			var crown = MeshInstance3D.new()
			var cn = CylinderMesh.new()
			cn.top_radius = 0.0
			cn.bottom_radius = 1.3 * s
			cn.height = 3.4 * s
			cn.radial_segments = 8
			crown.mesh = cn
			crown.material_override = _mat(Color(0.18, 0.45, 0.22).lerp(Color(0.3, 0.55, 0.2), rng.randf()))
			crown.position = Vector3(x0, 3.0 * s, z)
			add_child(crown)
		x0 += rng.randf_range(4.0, 11.0)
	# far layer: mountains (snow caps) / dunes / volcano / skyline
	var far_col = {"desert": Color(0.82, 0.6, 0.4), "volcano": Color(0.25, 0.2, 0.2), "beach": Color(0.35, 0.6, 0.8),
				   "city": Color(0.45, 0.5, 0.6)}.get(loc, Color(0.36, 0.4, 0.52))
	for i in range(9):
		var mx = -80.0 + i * 38.0 + rng.randf_range(-10, 10)
		var mz = -170.0 - rng.randf_range(0, 70)
		var mh = rng.randf_range(35, 70)
		if loc == "city":
			for b in range(4):
				_box(Vector3(10, mh * 0.6 + b * 6, 10), Vector3(mx + b * 9, (mh * 0.6 + b * 6) / 2, mz), _mat(far_col.lightened(b * 0.05)))
			continue
		var m = MeshInstance3D.new()
		var cn = CylinderMesh.new()
		cn.top_radius = 0.0 if loc != "volcano" or i != 4 else 8.0
		cn.bottom_radius = mh * 0.9
		cn.height = mh
		cn.radial_segments = 7
		m.mesh = cn
		var mm = _mat(far_col.lerp(Color(0.3, 0.34, 0.46), rng.randf() * 0.4))
		mm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED          # flat painted backdrop like the aired art
		mm.disable_fog = true
		m.material_override = mm
		m.position = Vector3(mx, mh / 2 - 2, mz)
		add_child(m)
		if loc == "mountains" or loc == "snow":
			var cap = MeshInstance3D.new()
			var cc = CylinderMesh.new()
			cc.top_radius = 0.0
			cc.bottom_radius = mh * 0.25
			cc.height = mh * 0.28
			cc.radial_segments = 7
			cap.mesh = cc
			var capm = _mat(Color(0.8, 0.8, 0.86))
			capm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			capm.disable_fog = true
			cap.material_override = capm
			cap.position = Vector3(mx, mh - 2 - mh * 0.14, mz)
			add_child(cap)
	for i in range(7):                                       # clouds
		var cl = Node3D.new()
		cl.position = Vector3(-60 + i * 45 + rng.randf_range(-12, 12), rng.randf_range(28, 45), -140 - rng.randf_range(0, 40))
		for k in range(4):
			var pf = MeshInstance3D.new()
			var sp = SphereMesh.new()
			sp.radius = rng.randf_range(4, 7)
			sp.height = sp.radius * 1.2
			pf.mesh = sp
			var cm = _mat(Color(1, 1, 1))
			cm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			var ccol = scene.get("cloud", [1, 1, 1])
			cm.albedo_color = Color(ccol[0], ccol[1], ccol[2])
			cm.disable_fog = true
			pf.material_override = cm
			pf.position = Vector3(k * 6 - 9, rng.randf_range(-1.5, 1.5), 0)
			cl.add_child(pf)
		add_child(cl)


func _props() -> void:
	for sx in scene["signs"]:                                # warning signs before each obstacle
		_box(Vector3(0.12, 2.0, 0.12), Vector3(sx, 1.0, -ROAD_HZ - 0.6), _mat(Color(0.5, 0.5, 0.55)))
		var d = _box(Vector3(0.9, 0.9, 0.06), Vector3(sx, 2.1, -ROAD_HZ - 0.55), _mat(Color(1, 0.82, 0.1)))
		d.rotation_degrees = Vector3(0, 0, 45)
		var lb = Label3D.new()
		lb.text = "!"
		lb.font_size = 96
		lb.pixel_size = 0.008
		lb.modulate = Color(0.1, 0.1, 0.12)
		lb.outline_size = 0
		lb.position = Vector3(sx, 2.08, -ROAD_HZ - 0.5)
		add_child(lb)
	var conc = _mat(Color(0.66, 0.66, 0.68))
	for b in scene.get("barriers", []):                      # concrete walls with hazard stripes
		var bx = float(b[0])
		var bw = float(b[1])
		var bh = float(b[2])
		var gy = ground_h(bx + bw / 2)
		_box(Vector3(bw, bh, ROAD_HZ * 2), Vector3(bx + bw / 2, gy + bh / 2, 0), conc)
		for k in range(4):
			var st_m = _mat(Color(1, 0.8, 0.1) if k % 2 == 0 else Color(0.1, 0.1, 0.12))
			_box(Vector3(bw + 0.02, bh * 0.12, ROAD_HZ * 2 + 0.02), Vector3(bx + bw / 2, gy + bh * (0.2 + 0.2 * k), 0), st_m)
	var water = StandardMaterial3D.new()
	water.albedo_color = Color(0.35, 0.55, 0.75, 0.75)
	water.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	water.roughness = 0.05
	water.metallic = 0.3
	var wet = _mat(Color(0.12, 0.12, 0.14), 0.25)              # darker wet asphalt under / around the puddles
	for pd in scene.get("puddles", []):
		var x0 = float(pd[0])
		var x1 = float(pd[1])
		var x = x0
		while x < x1:                                        # follow the road (slopes) in 2 m patches
			var seg = minf(2.4, x1 - x)
			var gy = ground_h(x + seg / 2)
			var nxt = ground_h(minf(x1, x + seg))
			var ang = atan2(nxt - ground_h(x), seg)
			var w = _box(Vector3(seg + 0.6, 0.01, ROAD_HZ * 1.9), Vector3(x + seg / 2, gy + 0.012, 0), wet)
			w.rotation = Vector3(0, 0, ang)
			var pm = MeshInstance3D.new()
			var pl = PlaneMesh.new()
			pl.size = Vector2(seg + 0.9, ROAD_HZ * 1.7)
			pm.mesh = pl
			pm.material_override = _water_mat(true)
			pm.position = Vector3(x + seg / 2, gy + 0.03, rng.randf_range(-0.3, 0.3))
			pm.rotation = Vector3(0, 0, ang)
			add_child(pm)
			x += seg
	for v in scene.get("vents", []):                         # lava vents: glowing crack + a fountain that erupts on time
		var vx = float(v["x"])
		var gy = ground_h(vx)
		var crack = StandardMaterial3D.new()
		crack.albedo_color = Color(1, 0.4, 0.05)
		crack.emission_enabled = true
		crack.emission = Color(1, 0.35, 0.05)
		crack.emission_energy_multiplier = 3.0
		_box(Vector3(1.2, 0.04, ROAD_HZ * 1.6), Vector3(vx, gy + 0.02, 0), crack)
		var col = MeshInstance3D.new()
		var cyl = CylinderMesh.new()
		cyl.top_radius = 0.25
		cyl.bottom_radius = 0.55
		cyl.height = 1.0
		col.mesh = cyl
		var lm = StandardMaterial3D.new()
		lm.albedo_color = Color(1, 0.5, 0.08)
		lm.emission_enabled = true
		lm.emission = Color(1, 0.45, 0.05)
		lm.emission_energy_multiplier = 3.5
		col.material_override = lm
		col.visible = false
		add_child(col)
		var drops = _emitter(60, 1.0, Vector2(3, 7), Vector3(0, -9.8, 0), Vector2(0.15, 0.4), Color(1, 0.7, 0.2, 1),
							 Color(0.9, 0.2, 0.02, 0), 25.0, true)
		add_child(drops)
		var lt = OmniLight3D.new()
		lt.light_color = Color(1, 0.45, 0.1)
		lt.omni_range = 9.0
		add_child(lt)
		vent_fx.append({"v": v, "col": col, "drops": drops, "light": lt, "gy": gy})
	var fx = float(scene["finish_x"])                        # finish arch
	for zz in [ROAD_HZ + 0.3, -ROAD_HZ - 0.3]:
		_box(Vector3(0.3, 5.0, 0.3), Vector3(fx, 2.5, zz), _mat(Color(0.85, 0.85, 0.9)))
	var ck = StandardMaterial3D.new()
	var img = Image.create(8, 2, false, Image.FORMAT_RGB8)
	for xx in range(8):
		for yy in range(2):
			img.set_pixel(xx, yy, Color(1, 1, 1) if (xx + yy) % 2 == 0 else Color(0.1, 0.1, 0.1))
	ck.albedo_texture = ImageTexture.create_from_image(img)
	ck.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	_box(Vector3(0.2, 1.0, ROAD_HZ * 2 + 0.6), Vector3(fx, 5.0, 0), ck)
	_box(Vector3(0.5, 0.02, ROAD_HZ * 2), Vector3(fx, 0.015, 0), ck)


func _car() -> void:
	car = Node3D.new()
	add_child(car)
	body = MeshInstance3D.new()                              # the card can dent: subdivided plane + crumple shader
	var sh = Shader.new()
	sh.code = """
shader_type spatial;
render_mode cull_disabled;
uniform sampler2D tex : source_color, filter_linear;
uniform float dmg = 0.0;
uniform vec2 hit = vec2(0.75, 0.5);
uniform float burn = 0.0;
float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float n(vec2 p) { vec2 i = floor(p); vec2 f = fract(p); f = f * f * (3.0 - 2.0 * f);
	return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
// rigid metal: the body stays straight; only the struck end crumples, and every move is linear in x / y
// (straight lines stay straight). Sprite png = (body + 1.6 m) x (body + 3 m) at 60 px/m (export *_png)
varying float ez;                                   // metres from the struck end of the body (before crushing)
varying float vy;                                   // local height, metres from the body centre
float zone_of(float e, float L) { return clamp((L - e) / L, 0.0, 1.0); }
void vertex() {
	vec2 ts = vec2(textureSize(tex, 0)) / 60.0;
	float bw = max(ts.x - 1.6, 0.5);
	float bh = max(ts.y - 3.0, 0.5);
	float s = hit.x > 0.5 ? 1.0 : -1.0;                 // which end was hit
	float L = 0.3 * bw;                                 // crumple zone = 30% of the body length
	ez = bw * 0.5 - s * VERTEX.x;
	vy = VERTEX.y;
	float dm = clamp(dmg, 0.0, 1.0);
	float z = zone_of(ez, L);
	float top = clamp(VERTEX.y / (bh * 0.5), 0.0, 1.0);
	VERTEX.x -= s * dm * 0.45 * L * z;                  // the end is pushed in: shorter, still straight
	VERTEX.y -= dm * 0.2 * bh * z * top;                // the roof / hood line drops in a straight slope
	VERTEX.z += dm * 0.35 * L * z;                      // and folds out of the plane (3D crease)
}
void fragment() {
	vec4 c = texture(tex, UV);
	if (c.a < 0.5) discard;
	vec2 ts = vec2(textureSize(tex, 0)) / 60.0;
	float L = 0.3 * max(ts.x - 1.6, 0.5);
	float dm = clamp(dmg, 0.0, 1.0);
	float z = zone_of(ez, L) * step(0.02, dm);
	vec3 col = c.rgb * (1.0 - 0.08 * dm);               // overall: a little dull, never warped
	float crease = 1.0 - smoothstep(0.0, 0.035, abs(ez - L)) ;          // the fold line where the crush starts
	float folds = step(0.88, fract((ez * 1.0 + vy * 0.55) * 3.2)) * z;   // straight diagonal creases in the crushed end
	col *= 1.0 - (0.3 * folds + 0.35 * crease * step(0.15, dm)) ;
	col *= 1.0 - 0.22 * z * dm;                         // the crushed panel is in shade
	float scratch = step(0.965, fract((ez * 1.7 + vy) * 9.0)) * z * step(0.3, dm);
	col = mix(col, vec3(0.8, 0.8, 0.82), scratch * 0.85);   // bare metal scratches, only where it was hit
	col = mix(col, vec3(0.09, 0.07, 0.06), burn * (0.6 + 0.2 * n(UV * 3.0)));   // soot, smooth (no speckles)
	ALBEDO = col;
	ROUGHNESS = 0.6;
}
"""
	body_mat = ShaderMaterial.new()
	body_mat.shader = sh
	body.material_override = body_mat
	body.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	body.position = Vector3(0, 0, 0.05)
	car.add_child(body)
	for i in range(6):                                       # up to 6 wheels; the data decides how many show (Titan = 4)
		var w = Sprite3D.new()
		w.pixel_size = 1.0 / 60.0
		w.shaded = true
		w.double_sided = true
		w.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		w.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		add_child(w)
		wheels.append(w)
	blob = MeshInstance3D.new()                              # contact shadow (cairo look)
	var cm = CylinderMesh.new()
	cm.top_radius = 0.5
	cm.bottom_radius = 0.5
	cm.height = 0.01
	blob.mesh = cm
	var bm = StandardMaterial3D.new()
	bm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	bm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	bm.albedo_texture = dot_tex
	bm.albedo_color = Color(0, 0, 0, 0.5)
	blob.material_override = bm
	blob.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(blob)
	smoke = _emitter(30, 2.4, Vector2(0.8, 2.2), Vector3(0, 1.6, 0), Vector2(0.5, 1.4), Color(0.15, 0.14, 0.14, 0.85),
					 Color(0.35, 0.35, 0.37, 0), 25.0, false)
	smoke.local_coords = false
	smoke.position = Vector3(0.3, 0.4, 0.2)
	car.add_child(smoke)
	fire = _emitter(26, 0.55, Vector2(1.0, 2.6), Vector3(0, 3.0, 0), Vector2(0.3, 0.75), Color(1, 0.85, 0.3, 0.95),
					Color(0.95, 0.2, 0.02, 0), 20.0, true)
	fire.local_coords = false
	fire.position = Vector3(0.6, 0.3, 0.25)
	car.add_child(fire)
	spray = _emitter(140, 0.9, Vector2(4, 9), Vector3(0, -12, 0), Vector2(0.2, 0.55), Color(0.95, 0.98, 1.0, 0.95),
					 Color(0.8, 0.92, 1.0, 0), 30.0, false)            # rooster tails of water from the tyres
	spray.direction = Vector3(-0.8, 0.9, 0.25)
	spray.local_coords = false
	add_child(spray)


func _body_mesh(vk: String) -> void:
	var c = cast[vk]
	for ch in car.get_children():
		if ch is SpotLight3D or (ch is MeshInstance3D and ch != body and ch.mesh is SphereMesh):
			ch.queue_free()
	_headlights(car, float(c["body"][0]) / 2.0, 0.0, -float(c["body"][0]) / 2.0)
	var pm = PlaneMesh.new()
	pm.size = Vector2(float(c["w"]) / 60.0, float(c["h"]) / 60.0)
	pm.orientation = PlaneMesh.FACE_Z
	pm.subdivide_width = 40
	pm.subdivide_depth = 14
	body.mesh = pm


# ================================================================== FX
func _emitter(n: int, life: float, vel: Vector2, grav: Vector3, size: Vector2, c0: Color, c1: Color,
			  spread := 180.0, unshaded := true) -> CPUParticles3D:
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
	g.set_color(0, c0)
	g.set_color(1, c1)
	p.color_ramp = g
	p.emitting = false
	return p


func _burst(pos: Vector3, n: int, life: float, vel: Vector2, grav: Vector3, size: Vector2, c0: Color, c1: Color,
			spread := 180.0, unshaded := true) -> void:
	var p = _emitter(n, life, vel, grav, size, c0, c1, spread, unshaded)
	p.position = pos
	p.one_shot = true
	p.explosiveness = 0.92
	fx_root.add_child(p)
	p.emitting = true


func _flash(pos: Vector3, energy: float, r: float, col: Color, fade: float) -> void:
	var o = OmniLight3D.new()
	o.position = pos
	o.light_color = col
	o.light_energy = energy
	o.omni_range = r
	fx_root.add_child(o)
	var tw = create_tween()
	tw.tween_property(o, "light_energy", 0.0, fade)


func _pow(pos: Vector3, size: float, text: String) -> void:
	var holder = Node3D.new()
	holder.position = pos
	fx_root.add_child(holder)
	if pow_tex == null:
		pow_tex = _pow_texture()
	var s = Sprite3D.new()
	s.texture = pow_tex
	s.pixel_size = size / 256.0
	s.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	s.no_depth_test = true
	s.shaded = false
	s.render_priority = 5
	holder.add_child(s)
	var lb = Label3D.new()
	lb.text = text
	lb.font_size = 120
	lb.pixel_size = size / 900.0
	lb.modulate = Color(0.85, 0.12, 0.08)
	lb.outline_modulate = Color(1, 1, 1)
	lb.outline_size = 24
	lb.no_depth_test = true
	lb.render_priority = 6
	lb.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	holder.add_child(lb)
	holder.scale = Vector3(0.2, 0.2, 0.2)
	var tw = create_tween()
	tw.tween_property(holder, "scale", Vector3(1.1, 1.1, 1.1), 0.1).set_trans(Tween.TRANS_BACK)
	tw.tween_interval(0.35)
	tw.tween_property(holder, "scale", Vector3(0.0, 0.0, 0.0), 0.15)


func _pow_texture() -> ImageTexture:
	var img = Image.create(256, 256, false, Image.FORMAT_RGBA8)
	var c = Vector2(128, 128)
	for yy in range(256):
		for xx in range(256):
			var d = Vector2(xx, yy) - c
			var ang = atan2(d.y, d.x)
			var spike = 0.62 + 0.38 * (0.5 + 0.5 * cos(ang * 14.0))
			var r = d.length() / 128.0
			if r < spike * 0.98:
				var col = Color(0.9, 0.2, 0.1)
				if r < spike * 0.82:
					col = Color(1, 0.86, 0.12)
				if r < spike * 0.5:
					col = Color(1, 1, 1)
				img.set_pixel(xx, yy, col)
	return ImageTexture.create_from_image(img)


func _impact(x: float, y: float, s: float) -> void:
	var p = Vector3(x, y - 0.4, 0.4)
	_burst(p, int(8 + 14 * s), 0.6, Vector2(1.5, 3.5), Vector3(0, -6, 0), Vector2(0.12, 0.3),
		   Color(0.45, 0.34, 0.25, 0.6), Color(0.45, 0.36, 0.3, 0), 60.0, false)                 # a little dirt kick
	if s > 0.45:
		_burst(p + Vector3(0, 0.5, 0), int(30 * s), 0.5, Vector2(6, 14), Vector3(0, -14, 0), Vector2(0.06, 0.14),
			   Color(1, 0.95, 0.6), Color(1, 0.5, 0.1, 0))                                       # sparks
	if s > 0.75:
		_pow(Vector3(x + 1.0, y + 3.0, 1.5), 2.2, "BAM!")
		_bolts(Vector3(x, y, 0.3), 6, 7.0)


func _lava_blast(x: float, y: float) -> void:
	## user rule: a car touched by lava burns and explodes (like a real car fire). The blast starts at the lava
	## surface but rises ABOVE the pit rim and in front of the dirt wall, so it is never hidden inside the pit.
	var top = maxf(y, ground_h(x) + 0.5) + 1.0
	var front = ROAD_HZ + 0.8
	_flash(Vector3(x, top + 1.0, 3.0), 12.0, 18.0, Color(1, 0.6, 0.25), 0.8)
	_fireball3(Vector3(x, top + 0.6, front), 3.2)
	_burst(Vector3(x, top, front), 120, 1.0, Vector2(5, 12), Vector3(0, 4, 0), Vector2(1.0, 2.4),
		   Color(1, 0.9, 0.45), Color(0.9, 0.18, 0.02, 0), 70.0)                                 # rising fireball
	_burst(Vector3(x, top + 1.5, front - 0.5), 70, 3.6, Vector2(1.5, 3.5), Vector3(0, 2.0, 0), Vector2(1.4, 3.2),
		   Color(0.12, 0.11, 0.11, 0.9), Color(0.3, 0.3, 0.32, 0), 60.0, false)                   # black smoke column
	_burst(Vector3(x, top, front), 90, 1.4, Vector2(8, 18), Vector3(0, -12, 0), Vector2(0.08, 0.22),
		   Color(1, 0.8, 0.3), Color(1, 0.3, 0.05, 0))                                           # embers
	_pow(Vector3(x + 1.2, top + 3.4, front), 3.4, "KABOOM!")
	_bolts(Vector3(x, top, front - 1.0), 12, 10.0)
	var flames = _emitter(60, 0.9, Vector2(2, 4.5), Vector3(0, 3.0, 0), Vector2(0.6, 1.5), Color(1, 0.8, 0.3, 0.95),
						  Color(0.95, 0.2, 0.02, 0), 25.0, true)          # the wreck keeps burning on the lava
	flames.position = Vector3(x, ground_h(x) + 0.3 if y < ground_h(x) else y, 1.0)
	fx_root.add_child(flames)
	flames.emitting = true


func _fireball3(pos: Vector3, size: float) -> void:
	var mi = MeshInstance3D.new()
	var sm = SphereMesh.new()
	sm.radius = 0.5
	sm.height = 1.0
	mi.mesh = sm
	var m = StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.albedo_color = Color(1, 0.75, 0.3, 0.9)
	mi.material_override = m
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.position = pos
	mi.scale = Vector3.ONE * size * 0.3
	fx_root.add_child(mi)
	var tw = create_tween().set_parallel(true)
	tw.tween_property(mi, "scale", Vector3.ONE * size, 0.35).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tw.tween_property(mi, "position:y", pos.y + size * 0.6, 0.9)
	tw.tween_property(m, "albedo_color", Color(0.9, 0.2, 0.03, 0.0), 0.9)


func _water_splash(x: float, y: float, big: float) -> void:
	_burst(Vector3(x, y, 0.2), int(220 * big), 1.6, Vector2(7, 17) * big, Vector3(0, -15, 0), Vector2(0.25, 0.7) * big,
		   Color(1, 1, 1, 0.95), Color(0.75, 0.9, 1.0, 0), 28.0, false)                          # tall column of spray
	_burst(Vector3(x, y + 0.1, 0.2), int(120 * big), 1.2, Vector2(5, 10) * big, Vector3(0, -14, 0), Vector2(0.15, 0.4) * big,
		   Color(0.95, 0.98, 1.0, 0.9), Color(0.7, 0.88, 1.0, 0), 80.0, false)                   # sideways crown
	var ring = MeshInstance3D.new()                          # shock ring on the water surface
	var tm = TorusMesh.new()
	tm.inner_radius = 0.85
	tm.outer_radius = 1.0
	ring.mesh = tm
	var rm = StandardMaterial3D.new()
	rm.albedo_color = Color(1, 1, 1, 0.9)
	rm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	rm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	ring.material_override = rm
	ring.position = Vector3(x, y - 0.3, 0)
	ring.scale = Vector3(0.3, 0.1, 0.3)
	fx_root.add_child(ring)
	var tw = create_tween().set_parallel(true)
	tw.tween_property(ring, "scale", Vector3(4.5, 0.1, 3.0), 0.9)
	tw.tween_property(rm, "albedo_color:a", 0.0, 0.9)
	_burst(Vector3(x, y + 0.2, 0.6), int(40 * big), 1.8, Vector2(1, 3), Vector3(0, 0.3, 0), Vector2(1.0, 2.2) * big,
		   Color(1, 1, 1, 0.65), Color(0.85, 0.95, 1.0, 0), 90.0, true)                            # mist
	_pow(Vector3(x + 1.0, y + 3.4, 1.8), 2.8, "SPLASH!")


func _bolts(pos: Vector3, n: int, vel: float) -> void:
	var bm = _mat(Color(0.72, 0.72, 0.76), 0.3)
	bm.metallic = 0.8
	for i in range(n):
		var rb = RigidBody3D.new()
		rb.mass = 4.0
		var cs = CollisionShape3D.new()
		var bs = BoxShape3D.new()
		bs.size = Vector3(0.18, 0.18, 0.18)
		cs.shape = bs
		rb.add_child(cs)
		var mi = MeshInstance3D.new()
		var cy = CylinderMesh.new()
		cy.top_radius = 0.1
		cy.bottom_radius = 0.1
		cy.height = 0.2
		cy.radial_segments = 6
		mi.mesh = cy
		mi.material_override = bm
		rb.add_child(mi)
		rb.position = pos
		fx_root.add_child(rb)
		rb.linear_velocity = Vector3(rng.randf_range(-1, 1) * vel, rng.randf_range(0.5, 1.2) * vel, rng.randf_range(-0.2, 1.0) * vel)
		rb.angular_velocity = Vector3(rng.randf_range(-20, 20), rng.randf_range(-20, 20), rng.randf_range(-20, 20))


func _break(x: float, y: float, vk: String, ca: float, ys: float) -> void:
	## the big one: the car's own panels tear off and fly (physics on the real track), glass, bolts, wheels' hubcaps,
	## sparks, a flash, a CRASH! burst; the wreck keeps smoking (and burning) afterwards.
	var c = cast[vk]
	var bw = float(c["body"][0])
	var bh = float(c["body"][1])
	var t = tex[vk + "_normal"]
	var tsz = t.get_size()
	var ppm = 60.0
	# user 2026-10-03: no explosion (fireball / flash / smoke hide the damage) -> the damage itself is the show
	_burst(Vector3(x, y + 0.3, 0.5), 50, 0.45, Vector2(6, 14), Vector3(0, -15, 0), Vector2(0.05, 0.11),
		   Color(1, 0.95, 0.6), Color(1, 0.6, 0.2, 0))                                          # short metal sparks
	# (glass chips removed: they rendered as big white squares; the flying panels are mess enough)
	_pow(Vector3(x + 1.2, y + 3.6, 1.8), 2.8, "CRASH!")                                   # above, clear of the car
	var n = 22
	for i in range(n):                                       # panels cut from the car's own artwork
		var fw = rng.randf_range(0.22, 0.42)
		var fh = rng.randf_range(0.35, 0.7)
		var rx = rng.randf_range(0.0, 1.0 - fw)
		var ry = rng.randf_range(0.0, 1.0 - fh)
		var pw = bw * fw
		var ph = bh * fh
		var rb = RigidBody3D.new()
		rb.mass = 30.0
		rb.continuous_cd = true
		var cs = CollisionShape3D.new()
		var bs = BoxShape3D.new()
		bs.size = Vector3(pw, ph, 0.2)
		cs.shape = bs
		rb.add_child(cs)
		var s = Sprite3D.new()
		s.texture = t
		s.region_enabled = true
		s.region_rect = Rect2(tsz.x / 2 - bw * ppm / 2 + rx * bw * ppm, tsz.y / 2 - bh * ppm / 2 + ry * bh * ppm,
							  fw * bw * ppm, fh * bh * ppm)
		s.pixel_size = 1.0 / ppm
		s.shaded = true
		s.double_sided = true
		s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		s.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		s.flip_h = ys < 0
		rb.add_child(s)
		var local = Vector2((rx + fw / 2 - 0.5) * bw, (0.5 - ry - fh / 2) * bh).rotated(ca)
		rb.position = Vector3(x + local.x, y + local.y, 0.1 + 0.02 * i)
		fx_root.add_child(rb)
		rb.linear_velocity = Vector3(rng.randf_range(-9, 9), rng.randf_range(7, 16), rng.randf_range(-1.0, 6.0))
		rb.angular_velocity = Vector3(rng.randf_range(-9, 9), rng.randf_range(-9, 9), rng.randf_range(-12, 12))
	_bolts(Vector3(x, y, 0.3), 16, 10.0)
	for k in range(2):                                       # two spare wheels / hubcaps fly out
		var wb = RigidBody3D.new()
		wb.mass = 40.0
		var wc = CollisionShape3D.new()
		var cyl = CylinderShape3D.new()
		cyl.radius = float(c["wheel_r"])
		cyl.height = 0.3
		wc.shape = cyl
		wc.rotation_degrees = Vector3(90, 0, 0)
		wb.add_child(wc)
		var ws = Sprite3D.new()
		ws.texture = tex[vk + "_wheel"]
		ws.pixel_size = 1.0 / 60.0
		ws.shaded = true
		ws.double_sided = true
		ws.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		wb.add_child(ws)
		wb.position = Vector3(x + (k - 0.5) * bw * 0.6, y + 0.3, 0.6)
		fx_root.add_child(wb)
		wb.linear_velocity = Vector3((k - 0.5) * 16.0, rng.randf_range(9, 14), rng.randf_range(1, 4))
		wb.angular_velocity = Vector3(0, 0, rng.randf_range(-20, 20))


# ================================================================== per frame
func _process(_d: float) -> void:
	var i = clampi(start_off + Engine.get_process_frames() - 1, 0, frames.size() - 1)
	var f = frames[i]
	var li = int(f[0])
	var st = float(f[2])
	var lv = scene["levels"][li]
	var vk = lv["vk"]
	if li != last_li or st < last_st - 0.02:                 # new level or a replay rewinds: fresh effects
		for ch in fx_root.get_children():
			ch.queue_free()
		fired = {}
		dmg = 0.0
		dmg_target = 0.0
		burn = 0.0
		smoke.emitting = false                                # clear the soot / fire left over from the previous level:
		smoke.restart()                                       # their particles follow the car and showed as a black dot
		smoke.emitting = false
		fire.emitting = false
		fire.restart()
		fire.emitting = false
		for a_ in axe_fx:
			a_["slam"] = -1
		for o_ in ogre_fx:
			o_["slam"] = -1
		if li != last_li or st < last_st - 0.02:
			last_st = st - 0.001
	var dst = st - last_st
	Engine.time_scale = clampf(dst * 30.0, 0.05, 1.5)       # bullet-time / replay also slows the debris
	if vk != cur_vk:
		cur_vk = vk
		for w in wheels:
			w.texture = tex[vk + "_wheel"]
		_body_mesh(vk)
	# camera: the engine's 2D camera rebuilt in 3D (px/m at the car plane = 72 * zoom)
	var z = float(f[5])
	var ppm = float(scene["S"]) * z
	# KEEP_WIDTH: fov spans the 1080 px width -> 72 px/m x zoom at the car plane (verified against the aired frame)
	var D = 1080.0 / (2.0 * tan(deg_to_rad(FOV / 2.0)) * ppm) * cos(deg_to_rad(TILT))
	var X = float(f[3]) - float(f[6]) / ppm
	var Y = float(f[4]) + (float(scene["ground_y"]) - 960.0) / ppm + float(f[7]) / ppm
	cam.position = Vector3(X, Y + D * tan(deg_to_rad(TILT)), D)
	cam.look_at(Vector3(X, Y, 0), Vector3.UP)
	# car
	var broken = bool(f[15])
	var mood = "broken" if broken else str(f[14])
	body_mat.set_shader_parameter("tex", tex[vk + "_" + mood])
	var ys = float(f[11])
	car.position = Vector3(float(f[8]), float(f[9]), 0)
	car.rotation = Vector3(0, 0, float(f[10]))
	var melt = float(f[16])
	var crush = float(f[20]) if f.size() > 20 else 0.0     # an axe came down on the car: flat, a little wider
	body.scale = Vector3(ys * (1.0 + 0.2 * crush), (1.0 - 0.32 * melt) * (1.0 - 0.5 * crush), 1.0)
	dmg += (dmg_target - dmg) * 0.35                        # dents appear fast but not in one frame
	body_mat.set_shader_parameter("dmg", dmg)
	body_mat.set_shader_parameter("hit", hit_uv)
	if bool(f[17]) or melt > 0.0:
		burn = minf(1.0, burn + 0.08)
	body_mat.set_shader_parameter("burn", burn)
	var wl = f[12]
	for k in range(wheels.size()):
		if k < wl.size():
			wheels[k].visible = true
			wheels[k].position = Vector3(float(wl[k][0]), float(wl[k][1]), -0.05)
			wheels[k].rotation = Vector3(0, 0, float(wl[k][2]))
		else:
			wheels[k].visible = false
	var gh = ground_h(float(f[8]))
	var above = float(f[9]) - gh
	blob.visible = above < 6.0
	blob.position = Vector3(float(f[8]), gh + 0.02, 0)
	blob.scale = Vector3(float(cast[vk]["body"][0]) * 1.05, 1, 1.4)
	blob.material_override.albedo_color.a = 0.5 * clampf(1.0 - above / 6.0, 0.0, 1.0)
	var lava_hit = scene["pit_kind"] == "lava" and lv["sunk"] != null and st >= float(lv["sunk"])
	lava_hit = lava_hit or (lv["burned"] != null and st >= float(lv["burned"]))
	smoke.emitting = lava_hit                               # only a lava-touched car burns (user rule)
	fire.emitting = lava_hit
	smoke.visible = lava_hit                                # an idle emitter must not draw its parked particles
	fire.visible = lava_hit                                 # (they showed as black discs / a yellow glow on the car)
	var cx = float(f[8])
	var on_puddle = false
	for pd in scene.get("puddles", []):
		if float(pd[0]) <= cx and cx <= float(pd[1]):
			on_puddle = true
	spray.emitting = on_puddle and float(f[18]) > 3.0 and float(f[19]) < 0.5
	spray.visible = spray.emitting
	if spray.emitting and not fired.has("pd" + str(int(cx / 3.0))):   # entering water: side sheets of spray
		fired["pd" + str(int(cx / 3.0))] = true
		_burst(Vector3(cx, ground_h(cx) + 0.2, 0.4), 90, 0.9, Vector2(4, 9), Vector3(0, -13, 0), Vector2(0.18, 0.45),
			   Color(1, 1, 1, 0.95), Color(0.8, 0.92, 1.0, 0), 75.0, false)
	if wl.size() > 0:
		spray.position = Vector3(float(wl[0][0]), float(wl[0][1]) - 0.3, 0.4)
	for vf in vent_fx:                                      # eruptions on the engine's exact schedule
		var v = vf["v"]
		var ph = fmod(st + float(v["phase"]), float(v["period"]))
		var dur = float(v["dur"])
		var on = ph < dur + 0.9
		var top = 0.0
		if on:
			var rise = minf(1.0, ph / (dur * 0.35))
			var fall = 1.0 if ph < dur else maxf(0.0, 1.0 - (ph - dur) / 0.9)
			top = float(v["height"]) * rise * fall
		vf["col"].visible = top > 0.2
		vf["col"].scale = Vector3(1, maxf(0.01, top), 1)
		vf["col"].position = Vector3(float(v["x"]), vf["gy"] + top / 2, 0)
		vf["drops"].position = Vector3(float(v["x"]), vf["gy"] + top, 0)
		vf["drops"].emitting = top > 0.5
		vf["light"].position = Vector3(float(v["x"]), vf["gy"] + 1.5, 1.0)
		vf["light"].light_energy = 0.6 + 3.0 * clampf(top / 4.0, 0.0, 1.0)
	if _is_dungeon():
		_dungeon_update(st, last_st)
	# events (fire once per pass; a replay pass fires them again)
	var k2 = 0
	for im in lv["impacts"]:
		var key = "i" + str(k2)
		if not fired.has(key) and float(im[0]) <= st and float(im[0]) > last_st:
			fired[key] = true
			_impact(float(im[2]), float(im[3]), float(im[1]))
			if float(im[1]) > 0.45:                         # a hard hit dents the body where it struck
				_set_hit(float(im[2]), float(im[3]), f)
				dmg_target = minf(0.6, dmg_target + 0.3 * float(im[1]))
		k2 += 1
	var b = lv["broken"]
	if b != null and not fired.has("b") and float(b["t"]) <= st and float(b["t"]) > last_st:
		fired["b"] = true
		_set_hit(float(b["x"]), float(b["y"]), f)
		dmg_target = 1.0
		_break(float(b["x"]), float(b["y"]), vk, float(f[10]), ys)
	var sk = lv["sunk"]
	if sk != null and not fired.has("s") and float(sk) <= st and float(sk) > last_st:
		fired["s"] = true
		if scene["pit_kind"] == "lava":
			_lava_blast(float(f[8]), float(f[9]))
		elif scene["pit_kind"] == "water":
			_water_splash(float(f[8]), float(f[9]), 1.3)
	var bu = lv["burned"]
	var same_as_sink = sk != null and absf(float(bu if bu != null else -9.0) - float(sk)) < 0.05
	if bu != null and not fired.has("u") and float(bu) <= st and float(bu) > last_st and not same_as_sink:
		fired["u"] = true                                    # blasted by a lava fountain
		_lava_blast(float(f[8]), float(f[9]))
	last_li = li
	last_st = st


func _is_dungeon() -> bool:
	return str(scene.get("series", "")) == "dungeon"


func _brick_tex(base: Color, mortar: Color, seed_v: int) -> ImageTexture:
	# a 256x256 brick pattern (8 rows of 60x28 px bricks with mortar), each brick a little different in tone
	var img = Image.create(256, 256, false, Image.FORMAT_RGB8)
	img.fill(mortar)
	var r = RandomNumberGenerator.new()
	r.seed = seed_v
	for row in range(8):
		var off = 0 if row % 2 == 0 else 32
		for col in range(-1, 5):
			var x0 = col * 64 + off + 2
			var y0 = row * 32 + 2
			var sh = r.randf_range(-0.07, 0.07)
			var c = Color(clampf(base.r + sh, 0.0, 1.0), clampf(base.g + sh, 0.0, 1.0), clampf(base.b + sh, 0.0, 1.0))
			for yy in range(y0, y0 + 28):
				for xx in range(x0, x0 + 60):
					if xx >= 0 and xx < 256 and yy >= 0 and yy < 256:
						img.set_pixel(xx, yy, c)
	return ImageTexture.create_from_image(img)


func _tiled(base: Color, mortar: Color, sx: float, sy: float, seed_v: int) -> StandardMaterial3D:
	var m = StandardMaterial3D.new()
	m.albedo_texture = _brick_tex(base, mortar, seed_v)
	m.uv1_scale = Vector3(sx, sy, 1.0)
	m.roughness = 1.0
	return m


func _dungeon_hall() -> void:
	## the dungeon behind the road (series dungeon): a brick back wall, a stone floor, beams, columns, flickering torches
	var wz = -ROAD_HZ - 14.0
	_box(Vector3(420, 30, 0.6), Vector3(70, 14, wz), _tiled(Color(0.4, 0.33, 0.3), Color(0.14, 0.12, 0.12), 110.0, 9.0, 9))
	var fl = _box(Vector3(420, 0.3, 40), Vector3(70, -0.16, -ROAD_HZ - 20), _tiled(Color(0.34, 0.33, 0.38), Color(0.12, 0.12, 0.15), 100.0, 8.0, 4))
	_box(Vector3(420, 0.6, 60), Vector3(70, 30.0, wz + 30), _mat(Color(0.1, 0.09, 0.12)))
	var wood = _mat(Color(0.2, 0.13, 0.09))
	var x = -70.0
	while x < 230.0:                                         # ceiling beams, columns
		_box(Vector3(0.8, 0.8, 50), Vector3(x, 16.0, wz + 25), wood)
		x += 8.0
	var stone = _mat(Color(0.3, 0.29, 0.34))
	x = -66.0
	while x < 230.0:
		_box(Vector3(1.6, 30, 1.6), Vector3(x, 14, wz + 0.9), stone)
		_box(Vector3(2.2, 0.5, 2.2), Vector3(x, 0.25, wz + 0.9), stone)
		x += 24.0
	var fm = StandardMaterial3D.new()
	fm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	fm.albedo_color = Color(1.0, 0.62, 0.15)
	x = -60.0
	var q = 0
	while x < 230.0:                                         # torches (real orange lights)
		_box(Vector3(0.2, 0.8, 0.2), Vector3(x, 5.2, wz + 0.5), wood)
		var flm = MeshInstance3D.new()
		var sp = SphereMesh.new()
		sp.radius = 0.34
		sp.height = 0.8
		flm.mesh = sp
		flm.material_override = fm
		flm.position = Vector3(x, 6.0, wz + 0.5)
		add_child(flm)
		var ol = OmniLight3D.new()
		ol.light_color = Color(1.0, 0.62, 0.28)
		ol.light_energy = 3.0
		ol.omni_range = 16.0
		ol.position = Vector3(x, 6.0, wz + 2.5)
		add_child(ol)
		torches.append([ol, float(q) * 1.7])
		x += 14.0
		q += 1
	var fx = float(scene["finish_x"])                        # the exit: a heavy door and a glowing treasure chest
	_box(Vector3(6.0, 8.0, 0.5), Vector3(fx + 4.0, 4.0, wz + 0.4), _mat(Color(0.28, 0.17, 0.1)))
	for hb in [1.4, 4.0, 6.6]:
		_box(Vector3(6.2, 0.3, 0.6), Vector3(fx + 4.0, hb, wz + 0.45), _mat(Color(0.15, 0.15, 0.2)))
	var gold = StandardMaterial3D.new()
	gold.albedo_color = Color(1.0, 0.8, 0.2)
	gold.metallic = 0.8
	gold.roughness = 0.35
	gold.emission_enabled = true
	gold.emission = Color(1.0, 0.7, 0.1)
	gold.emission_energy_multiplier = 1.4
	_box(Vector3(2.6, 1.3, 1.6), Vector3(fx + 11.0, 0.65, -ROAD_HZ - 2.0), _mat(Color(0.4, 0.22, 0.1)))
	_box(Vector3(2.7, 0.5, 1.7), Vector3(fx + 11.0, 1.4, -ROAD_HZ - 2.0), gold)
	var gl = OmniLight3D.new()
	gl.light_color = Color(1.0, 0.82, 0.35)
	gl.light_energy = 3.5
	gl.omni_range = 14.0
	gl.position = Vector3(fx + 9.0, 3.0, -ROAD_HZ)
	add_child(gl)


func _axe_bottom(ax: Dictionary, t: float) -> float:
	var c = scene["chop"]
	var P = float(ax["period"])
	var up = float(c["up"])
	var fall = float(c["fall"])
	var down = float(c["down"])
	var h_up = float(c["h_up"])
	var h_dn = float(c["h_dn"])
	var rise = P - up - fall - down
	var tau = fmod(t + float(ax["phase"]), P)
	if tau < up:
		return h_up
	tau -= up
	if tau < fall:
		return h_up + (h_dn - h_up) * pow(tau / fall, 2.0)
	tau -= fall
	if tau < down:
		return h_dn
	return h_dn + (h_up - h_dn) * minf(1.0, (tau - down) / rise)


func _blade_mesh() -> ArrayMesh:
	## the crescent axe blade (x,y outline) extruded in z: horned tips, curved cutting edge
	var pts = [Vector2(-0.55, 1.5), Vector2(-1.55, 0.95), Vector2(-1.2, 0.0)]
	for k in range(1, 10):                                   # the curved cutting edge: a bezier from the left to the right horn
		var u = float(k) / 10.0
		var a = Vector2(-1.2, 0.0)
		var b = Vector2(-0.6, 0.6)
		var c = Vector2(0.6, 0.6)
		var d = Vector2(1.2, 0.0)
		pts.append(a * pow(1 - u, 3.0) + b * 3.0 * u * pow(1 - u, 2.0) + c * 3.0 * u * u * (1 - u) + d * pow(u, 3.0))
	pts.append(Vector2(1.2, 0.0))
	pts.append(Vector2(1.55, 0.95))
	pts.append(Vector2(0.55, 1.5))
	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var zt = 0.25
	var n = pts.size()
	var ctr = Vector2(0.0, 0.8)
	for i in range(n):
		var p0 = pts[i]
		var p1 = pts[(i + 1) % n]
		st.add_vertex(Vector3(ctr.x, ctr.y, zt))
		st.add_vertex(Vector3(p0.x, p0.y, zt))
		st.add_vertex(Vector3(p1.x, p1.y, zt))
		st.add_vertex(Vector3(ctr.x, ctr.y, -zt))
		st.add_vertex(Vector3(p1.x, p1.y, -zt))
		st.add_vertex(Vector3(p0.x, p0.y, -zt))
		st.add_vertex(Vector3(p0.x, p0.y, zt))
		st.add_vertex(Vector3(p0.x, p0.y, -zt))
		st.add_vertex(Vector3(p1.x, p1.y, -zt))
		st.add_vertex(Vector3(p0.x, p0.y, zt))
		st.add_vertex(Vector3(p1.x, p1.y, -zt))
		st.add_vertex(Vector3(p1.x, p1.y, zt))
	st.generate_normals()
	return st.commit()


func _axes() -> void:
	## giant dungeon axes (in front of the car plane): chain + haft up to the ceiling, an iron hub, a crescent blade
	var steel = StandardMaterial3D.new()
	steel.albedo_color = Color(0.86, 0.88, 0.96)
	steel.metallic = 0.2
	steel.roughness = 0.35
	steel.emission_enabled = true
	steel.emission = Color(0.3, 0.32, 0.4)
	steel.emission_energy_multiplier = 0.7
	steel.cull_mode = BaseMaterial3D.CULL_DISABLED
	var iron = _mat(Color(0.22, 0.22, 0.3), 0.5)
	var wood = _mat(Color(0.5, 0.33, 0.18))
	var bm = _blade_mesh()
	for ax in scene.get("axes", []):
		var root = Node3D.new()
		add_child(root)
		var blade = MeshInstance3D.new()
		blade.mesh = bm
		blade.material_override = steel
		root.add_child(blade)
		var hub = MeshInstance3D.new()
		var hb = BoxMesh.new()
		hb.size = Vector3(1.1, 0.75, 0.7)
		hub.mesh = hb
		hub.material_override = iron
		hub.position = Vector3(0, 1.55, 0)
		root.add_child(hub)
		var haft = MeshInstance3D.new()
		var hf = BoxMesh.new()
		hf.size = Vector3(0.34, 30.0, 0.34)
		haft.mesh = hf
		haft.material_override = wood
		haft.position = Vector3(0, 1.9 + 15.0, 0)
		root.add_child(haft)
		for bi in range(6):                                  # iron bands on the haft
			var band = MeshInstance3D.new()
			var bb = BoxMesh.new()
			bb.size = Vector3(0.44, 0.1, 0.44)
			band.mesh = bb
			band.material_override = iron
			band.position = Vector3(0, 2.8 + bi * 1.4, 0)
			root.add_child(band)
		axe_fx.append({"ax": ax, "root": root, "slam": -1})


func _ogre_arm(og: Dictionary, t: float) -> Array:
	var th = -1.9
	var bob = 0.05 * sin(t * 2.4)
	var P = float(og["period"])
	var tau = fmod(t + float(og["phase"]), P)
	var d = tau if tau < P / 2.0 else tau - P
	var wu = float(scene["ogre_windup"])
	if d >= -wu and d < -0.08:
		var e = (d + wu) / (wu - 0.08)
		th = -1.9 - 0.8 * e * e * (3.0 - 2.0 * e)
	elif d >= -0.08 and d < 0.08:
		var e2 = (d + 0.08) / 0.16
		th = -2.7 + 3.42 * e2 * e2
	elif d >= 0.08 and d < 1.0:
		th = 0.72
		bob -= 0.12 * exp(-(d - 0.08) * 7.0)
	elif d >= 1.0 and d < 1.9:
		var e3 = (d - 1.0) / 0.9
		th = 0.72 - 2.62 * e3 * e3 * (3.0 - 2.0 * e3)
	return [th, bob]


func _part(parent: Node3D, mesh: Mesh, mat: Material, pos: Vector3, scl := Vector3.ONE) -> MeshInstance3D:
	var mi = MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	mi.position = pos
	mi.scale = scl
	parent.add_child(mi)
	return mi


func _sphere(r: float) -> SphereMesh:
	var s = SphereMesh.new()
	s.radius = r
	s.height = 2.0 * r
	return s


func _cone(r: float, h: float) -> CylinderMesh:
	var c = CylinderMesh.new()
	c.top_radius = 0.0
	c.bottom_radius = r
	c.height = h
	return c


func _ogres() -> void:
	## the dungeon ogre: built from primitives, the club arm swings on the engine's exact schedule
	var skin = _mat(Color(0.42, 0.58, 0.3), 0.8)
	var dark = _mat(Color(0.28, 0.4, 0.21), 0.8)
	var light = _mat(Color(0.62, 0.74, 0.45), 0.8)
	var leather = _mat(Color(0.3, 0.2, 0.12), 0.9)
	var bone = _mat(Color(0.92, 0.9, 0.82), 0.6)
	var club = _mat(Color(0.5, 0.33, 0.18), 0.85)
	var iron = _mat(Color(0.75, 0.77, 0.85), 0.35)
	var eye = StandardMaterial3D.new()
	eye.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	eye.albedo_color = Color(1, 0.9, 0.2)
	for og in scene.get("ogres", []):
		var f = -1.0
		var root = Node3D.new()
		root.position = Vector3(float(og["x"]), 0.0, -1.6)
		add_child(root)
		var body = Node3D.new()
		root.add_child(body)
		for lx in [-0.65, 0.65]:
			var cap = CapsuleMesh.new()
			cap.radius = 0.5
			cap.height = 1.9
			_part(body, cap, dark, Vector3(lx, 1.0, 0))
			var boot = BoxMesh.new()
			boot.size = Vector3(1.3, 0.55, 1.2)
			_part(body, boot, leather, Vector3(lx + f * 0.15, 0.28, 0.1))
		_part(body, _sphere(1.0), skin, Vector3(0, 2.9, 0), Vector3(1.6, 1.5, 1.2))
		_part(body, _sphere(1.0), light, Vector3(f * 0.2, 2.5, 0.55), Vector3(1.0, 0.95, 0.7))
		var belt = BoxMesh.new()
		belt.size = Vector3(3.1, 0.45, 2.5)
		_part(body, belt, leather, Vector3(0, 1.95, 0))
		var head = Node3D.new()
		head.position = Vector3(f * 0.35, 4.6, 0.1)
		body.add_child(head)
		_part(head, _sphere(1.0), skin, Vector3.ZERO, Vector3(1.0, 0.88, 0.95))
		for sg in [-1.0, 1.0]:
			_part(head, _cone(0.22, 0.9), bone, Vector3(sg * 0.75, 0.9, 0), Vector3(1, 1, 1)).rotation = Vector3(0, 0, -sg * 0.35)
			_part(head, _sphere(0.2), eye, Vector3(sg * 0.42 + f * 0.1, 0.12, 0.85))
			_part(head, _cone(0.14, 0.5), bone, Vector3(sg * 0.4, -0.45, 0.8), Vector3(1, 1, 1)).rotation = Vector3(PI, 0, 0)
		var jaw = BoxMesh.new()
		jaw.size = Vector3(1.1, 0.3, 0.5)
		_part(head, jaw, _mat(Color(0.25, 0.05, 0.05)), Vector3(0, -0.4, 0.78))
		var idle = CapsuleMesh.new()
		idle.radius = 0.4
		idle.height = 1.9
		_part(body, idle, dark, Vector3(-f * 1.05, 2.7, 0))
		var sh = Node3D.new()                                # the club arm: pivots at the shoulder, in the plane just behind the cars
		sh.position = Vector3(f * 0.9, 3.7, 1.0)
		root.add_child(sh)
		var arm = CapsuleMesh.new()
		arm.radius = 0.4
		arm.height = 1.9
		_part(sh, arm, skin, Vector3(0, -0.75, 0))
		var cl = CylinderMesh.new()
		cl.top_radius = 0.2
		cl.bottom_radius = 0.55
		cl.height = 3.4
		_part(sh, cl, club, Vector3(0, -3.2, 0))
		for q in range(5):
			var sp = _part(sh, _cone(0.14, 0.45), iron, Vector3(0.5 * (1.0 if q % 2 == 0 else -1.0), -2.4 - 0.4 * q, 0.0))
			sp.rotation = Vector3(0, 0, -1.57 * (1.0 if q % 2 == 0 else -1.0))
		ogre_fx.append({"og": og, "root": root, "body": body, "sh": sh, "f": f, "slam": -1})


func _dungeon_update(st: float, last: float) -> void:
	for tq in torches:                                       # torches flicker
		tq[0].light_energy = 3.0 + 0.6 * sin(st * 13.0 + float(tq[1])) + 0.4 * sin(st * 29.0 + float(tq[1]) * 2.0)
	var c = scene["chop"]
	for af in axe_fx:
		var ax = af["ax"]
		var b = _axe_bottom(ax, st)
		af["root"].position = Vector3(float(ax["x"]), b, 0.55)
		var P = float(ax["period"])
		var kk = floor((st + float(ax["phase"]) - float(c["up"]) - float(c["fall"])) / P)
		if kk != af["slam"]:
			if af["slam"] != -1 and st > last:                # the edge just landed: dust rolls out both ways
				_burst(Vector3(float(ax["x"]), 0.3, 0.9), 26, 0.9, Vector2(2, 5), Vector3(0, -3, 0), Vector2(0.4, 1.1),
					   Color(0.8, 0.76, 0.7, 0.8), Color(0.6, 0.58, 0.55, 0), 80.0, false)
			af["slam"] = kk
	for oz in ogre_fx:
		var r = _ogre_arm(oz["og"], st)
		oz["sh"].rotation = Vector3(0, 0, float(oz["f"]) * float(r[0]))
		oz["body"].position = Vector3(0, float(r[1]), 0)
		oz["sh"].position = Vector3(float(oz["f"]) * 0.9, 3.7 + float(r[1]), 1.0)
		var P = float(oz["og"]["period"])
		var kk = floor((st + float(oz["og"]["phase"])) / P)
		if kk != oz["slam"]:
			if oz["slam"] != -1 and kk >= 1.0 and st > last:
				_burst(Vector3(float(oz["og"]["x"]) - 3.6, 0.3, 0.9), 30, 1.0, Vector2(2, 6), Vector3(0, -4, 0), Vector2(0.5, 1.3),
					   Color(0.78, 0.72, 0.64, 0.85), Color(0.55, 0.5, 0.46, 0), 80.0, false)
			oz["slam"] = kk


func _set_hit(x: float, y: float, f) -> void:
	## impact point -> body UV (car local frame), so the dent is where the car actually hit
	var c = cast[cur_vk]
	var loc = Vector2(x - float(f[8]), y - float(f[9])).rotated(-float(f[10]))
	var wm = float(c["w"]) / 60.0
	var hm = float(c["h"]) / 60.0
	hit_uv = Vector2(clampf(loc.x / wm + 0.5, 0.15, 0.85), clampf(0.5 - loc.y / hm, 0.2, 0.8))


func _headlights(parent: Node3D, front_x: float, y: float, back_x: float) -> void:
	## night theme: real headlights (a spot that lights the road ahead) + glowing lamp + red tail light
	if not scene["night"]:
		return
	var sp = SpotLight3D.new()
	sp.position = Vector3(front_x, y, 0.3)
	sp.rotation_degrees = Vector3(0, -90, 0)               # points along +x (the driving direction)
	sp.rotate_object_local(Vector3.RIGHT, deg_to_rad(-8))
	sp.light_color = Color(1, 0.95, 0.75)
	sp.light_energy = 6.0
	sp.spot_range = 22.0
	sp.spot_angle = 24.0
	parent.add_child(sp)
	for pr in [[front_x, Color(1, 0.97, 0.8), 0.22], [back_x, Color(1, 0.1, 0.1), 0.14]]:
		var lamp = MeshInstance3D.new()
		var sm = SphereMesh.new()
		sm.radius = pr[2]
		sm.height = pr[2] * 2
		lamp.mesh = sm
		var lm = StandardMaterial3D.new()
		lm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		lm.albedo_color = pr[1]
		lm.emission_enabled = true
		lm.emission = pr[1]
		lm.emission_energy_multiplier = 4.0
		lamp.material_override = lm
		lamp.position = Vector3(pr[0], y, 0.12)
		parent.add_child(lamp)
