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
var body: Sprite3D
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
	_car()
	fx_root = Node3D.new()
	add_child(fx_root)
	cam = Camera3D.new()
	cam.keep_aspect = Camera3D.KEEP_WIDTH
	cam.fov = FOV
	cam.far = 900.0
	add_child(cam)
	cam.make_current()


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
	var we = WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun = DirectionalLight3D.new()                       # from the camera side (CONFIG_BEST lesson 10)
	var tm = th["time"]
	sun.rotation_degrees = {"morning": Vector3(-28, 145, 0), "noon": Vector3(-62, 160, 0),
							"sunset": Vector3(-18, 125, 0), "night": Vector3(-45, 150, 0)}.get(tm, Vector3(-55, 150, 0))
	sun.light_color = {"morning": Color(1, 0.9, 0.78), "noon": Color(1, 0.98, 0.94), "sunset": Color(1, 0.72, 0.5),
					   "night": Color(0.6, 0.7, 1.0)}.get(tm, Color(1, 1, 1))
	sun.light_energy = 1.15 * float(scene["light"]) * (0.45 if scene["night"] else 1.0)
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
	var tops = [[top, _mat(Color(0.22, 0.22, 0.25), 0.8)], [dirt, _mat(Color(0.3, 0.2, 0.15))],
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
render_mode cull_disabled;
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
	ALBEDO = mix(c, c * 0.72, pebble);
	ROUGHNESS = 0.95;
}
"""
	var fm = ShaderMaterial.new()
	fm.shader = sh
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
				lm.albedo_color = Color(1, 0.45, 0.05)
				lm.emission_enabled = true
				lm.emission = Color(1, 0.4, 0.05)
				lm.emission_energy_multiplier = 2.5
			else:
				lm.albedo_color = Color(0.1, 0.45, 0.75, 0.85)
				lm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			var depth = -p[2] + (1.3 if scene["pit_kind"] == "lava" else p[2] - 0.8)
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
	body = Sprite3D.new()
	body.pixel_size = 1.0 / 60.0
	body.shaded = true
	body.double_sided = true
	body.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	body.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	body.position = Vector3(0, 0, 0.05)
	car.add_child(body)
	for i in range(2):
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
	_burst(Vector3(x, y + 0.4, 0.6), 45, 0.9, Vector2(4, 10), Vector3(0, -22, 0), Vector2(0.04, 0.09),
		   Color(0.85, 0.97, 1.0, 1.0), Color(0.7, 0.9, 1.0, 0.6), 120.0, true)                    # glass chips (fall fast)
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
		if li != last_li or st < last_st - 0.02:
			last_st = st - 0.001
	var dst = st - last_st
	Engine.time_scale = clampf(dst * 30.0, 0.05, 1.5)       # bullet-time / replay also slows the debris
	if vk != cur_vk:
		cur_vk = vk
		for w in wheels:
			w.texture = tex[vk + "_wheel"]
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
	body.texture = tex[vk + "_" + mood]
	var ys = float(f[11])
	car.position = Vector3(float(f[8]), float(f[9]), 0)
	car.rotation = Vector3(0, 0, float(f[10]))
	var melt = float(f[16])
	body.scale = Vector3(ys, 1.0 - 0.32 * melt, 1.0)
	body.modulate = Color(0.55, 0.5, 0.5) if bool(f[17]) else Color(1, 1, 1)
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
	smoke.emitting = false                                  # no smoke / fire: keep the wreck visible
	fire.emitting = melt > 0.0                              # only the lava series' melting glow
	# events (fire once per pass; a replay pass fires them again)
	var k2 = 0
	for im in lv["impacts"]:
		var key = "i" + str(k2)
		if not fired.has(key) and float(im[0]) <= st and float(im[0]) > last_st:
			fired[key] = true
			_impact(float(im[2]), float(im[3]), float(im[1]))
		k2 += 1
	var b = lv["broken"]
	if b != null and not fired.has("b") and float(b["t"]) <= st and float(b["t"]) > last_st:
		fired["b"] = true
		_break(float(b["x"]), float(b["y"]), vk, float(f[10]), ys)
	last_li = li
	last_st = st
