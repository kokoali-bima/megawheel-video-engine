extends Node3D
## LAB — 3D RACE. The aired RACE engine (race25d.py v3) decides everything (export_race.py writes it): cast, lanes,
## hazards and when they fire, physics, camera, HUD, narration, audio. This scene re-draws the world in 3D: a curved
## 4-lane circuit, lit paper-cut cars that dent where they are hit (panels fly, no explosions), and the ground
## hazards in real 3D (giant hammer, crusher, falling container, wall, laser, oil, puddle, pothole). Flying hazards
## (dragons, meteor, UFO) come from the engine's own drawing in the overlay.
## Projection = race25d: k(z) = F / (D0 + LANE_D z) px/m  ->  a level camera CAM_H m high, lane z at depth
## (D0 + LANE_D z) / 10 m, focal 900 px x zoom, horizon at the engine's screen y (lens shift).

var dir = "/root/lab/r3d/s11"
var start_off = 0
var scene = {}
var frames = []
var cast = {}
var tex = {}
var dot_tex: GradientTexture2D
var pow_tex: ImageTexture
var cam: Camera3D
var fx_root: Node3D
var cars = []                                             # per car: {vk, root, body, mat, wheels, blob}
var hz_nodes = []
var rng = RandomNumberGenerator.new()
var last_st = -1.0
var last_mode = ""
var fired = {}
var P = {}


func depth(zl: float) -> float:
	return -(float(P["D0"]) + float(P["LANE_D"]) * zl) / 10.0


func zc(x: float) -> float:
	var c = scene["curve"]
	if c == null:
		return 0.0
	return float(c["amp"]) * (0.5 - 0.5 * cos(2.0 * PI * x / float(c["length"]) + float(c["phase"])))


func lane_pos(x: float, zl: float, h := 0.0) -> Vector3:
	return Vector3(x, h, depth(zl + zc(x)))


func _ready() -> void:
	var a = OS.get_cmdline_user_args()
	if a.size() > 0:
		dir = a[0]
	if a.size() > 1:
		start_off = int(a[1])
	scene = JSON.parse_string(FileAccess.open(dir + "/scene.json", FileAccess.READ).get_as_text())
	frames = JSON.parse_string(FileAccess.open(dir + "/frames.json", FileAccess.READ).get_as_text())["frames"]
	cast = scene["cast"]
	P = scene["proj"]
	rng.seed = 11
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
		for m in ["normal", "scared", "whoa", "dizzy", "happy"]:
			tex[vk + "_" + m] = _img(dir + "/sprites/" + vk + "_" + m + ".png")
		tex[vk + "_wheel"] = _img(dir + "/sprites/" + vk + "_wheel.png")
	_environment()
	_road()
	_landscape()
	_hazards()
	for vk in cast:
		_car(vk)
	fx_root = Node3D.new()
	add_child(fx_root)
	cam = Camera3D.new()
	cam.keep_aspect = Camera3D.KEEP_WIDTH
	cam.projection = Camera3D.PROJECTION_FRUSTUM
	cam.near = 0.5
	cam.far = 900.0
	add_child(cam)
	cam.make_current()


# ================================================================== world
func _environment() -> void:
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
	sk.sky_material = sm
	env.background_mode = Environment.BG_SKY
	env.sky = sk
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(1, 0.97, 0.95) if not scene["night"] else Color(0.55, 0.6, 0.85)
	env.ambient_light_energy = 0.45 * float(scene["light"])
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.glow_enabled = true
	env.glow_intensity = 0.3
	env.fog_enabled = true
	env.fog_light_color = Color(hor[0], hor[1], hor[2])
	env.fog_density = 0.0012
	env.fog_sky_affect = 0.0
	var we = WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun = DirectionalLight3D.new()                       # from the camera side (CONFIG_BEST lesson 10)
	var tm = scene["theme"]["time"]
	sun.rotation_degrees = {"morning": Vector3(-30, 25, 0), "noon": Vector3(-62, 15, 0), "sunset": Vector3(-20, 40, 0),
							"night": Vector3(-45, 20, 0)}.get(tm, Vector3(-55, 20, 0))
	sun.light_color = {"morning": Color(1, 0.9, 0.78), "noon": Color(1, 0.98, 0.94), "sunset": Color(1, 0.72, 0.5),
					   "night": Color(0.6, 0.7, 1.0)}.get(tm, Color(1, 1, 1))
	sun.light_energy = 0.8 * float(scene["light"]) * (0.45 if scene["night"] else 1.0)   # front-lit cards: softer
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 120.0
	add_child(sun)


func _road() -> void:
	## the circuit: asphalt from lane -0.6 to 3.6 following the curve, red/white kerbs, dashed lane lines
	var x0 = -60.0
	var x1 = float(scene["fin_x"]) + 220.0
	var asph = SurfaceTool.new()
	var kerb_r = SurfaceTool.new()
	var kerb_w = SurfaceTool.new()
	var paint = SurfaceTool.new()
	for s in [asph, kerb_r, kerb_w, paint]:
		s.begin(Mesh.PRIMITIVE_TRIANGLES)
	var x = x0
	var step = 1.5
	var n = 0
	while x < x1:
		var xa = x
		var xb = x + step
		_strip(asph, xa, xb, -0.6, 3.6, 0.0)
		var k = kerb_r if n % 2 == 0 else kerb_w
		_strip(k, xa, xb, -0.85, -0.6, 0.02)
		_strip(k, xa, xb, 3.6, 3.85, 0.02)
		if n % 2 == 0:
			for ln in [0.5, 1.5, 2.5]:
				_strip(paint, xa, xb, ln - 0.04, ln + 0.04, 0.012)
		x = xb
		n += 1
	var mats = [[asph, _mat(Color(0.26, 0.26, 0.29), 0.85)], [kerb_r, _mat(Color(0.85, 0.12, 0.12))],
				[kerb_w, _mat(Color(0.95, 0.95, 0.95))], [paint, _mat(Color(0.95, 0.95, 0.92), 0.6)]]
	for pr in mats:
		pr[1].cull_mode = BaseMaterial3D.CULL_DISABLED
		var mi = MeshInstance3D.new()
		mi.mesh = pr[0].commit()
		mi.material_override = pr[1]
		add_child(mi)
	var fx = float(scene["fin_x"])                           # finish line + gantry
	var ck = StandardMaterial3D.new()
	var img = Image.create(8, 2, false, Image.FORMAT_RGB8)
	for xx in range(8):
		for yy in range(2):
			img.set_pixel(xx, yy, Color(1, 1, 1) if (xx + yy) % 2 == 0 else Color(0.1, 0.1, 0.1))
	ck.albedo_texture = ImageTexture.create_from_image(img)
	ck.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	var fs = SurfaceTool.new()
	fs.begin(Mesh.PRIMITIVE_TRIANGLES)
	_strip(fs, fx - 0.5, fx + 0.5, -0.6, 3.6, 0.02)
	var fm = MeshInstance3D.new()
	fm.mesh = fs.commit()
	fm.material_override = ck
	add_child(fm)
	for zl in [-1.0, 4.0]:
		var p = lane_pos(fx, zl)
		_box(Vector3(0.35, 6.5, 0.35), p + Vector3(0, 3.25, 0), _mat(Color(0.85, 0.85, 0.9)))
	var pa = lane_pos(fx, -1.0)
	var pb = lane_pos(fx, 4.0)
	var ban = _box(Vector3(0.3, 1.1, absf(pb.z - pa.z)), Vector3(fx, 6.3, (pa.z + pb.z) / 2), ck)


func _strip(s: SurfaceTool, xa: float, xb: float, za: float, zb: float, y: float) -> void:
	var a = lane_pos(xa, za, y)
	var b = lane_pos(xb, za, y)
	var c = lane_pos(xb, zb, y)
	var d = lane_pos(xa, zb, y)
	for p in [a, b, c, a, c, d]:
		s.set_normal(Vector3.UP)
		s.set_uv(Vector2(p.x * 0.2, p.z * 0.2))
		s.add_vertex(p)


func _landscape() -> void:
	var loc = scene["theme"]["location"]
	var grass_col = {"desert": Color(0.86, 0.72, 0.45), "beach": Color(0.9, 0.82, 0.6), "volcano": Color(0.3, 0.24, 0.22),
					 "city": Color(0.45, 0.5, 0.42), "snow": Color(0.92, 0.95, 1.0)}.get(loc, Color(0.24, 0.42, 0.24))
	var gp = MeshInstance3D.new()
	var pm = PlaneMesh.new()
	pm.size = Vector2(900, 700)
	gp.mesh = pm
	gp.material_override = _mat(grass_col, 0.95)
	gp.position = Vector3(float(scene["fin_x"]) / 2, -0.02, -300)
	add_child(gp)
	for row in [[4.6, 9.0, 1.3], [5.6, 11.0, 1.6], [-1.3, 7.0, 0.6]]:   # trees behind, bushes in front (like the engine)
		var x = -60.0
		while x < float(scene["fin_x"]) + 200.0:
			var p = lane_pos(x, float(row[0]) + rng.randf_range(-0.2, 0.4))
			var s = float(row[2]) * rng.randf_range(0.8, 1.25)
			if row[0] < 0:
				var bush = MeshInstance3D.new()
				var sp = SphereMesh.new()
				sp.radius = 0.9 * s
				sp.height = 1.2 * s
				bush.mesh = sp
				bush.material_override = _mat(Color(0.2, 0.42, 0.2))
				bush.position = p + Vector3(0, 0.3 * s, 0)
				add_child(bush)
			else:
				var trunk = MeshInstance3D.new()
				var cy = CylinderMesh.new()
				cy.top_radius = 0.18 * s
				cy.bottom_radius = 0.25 * s
				cy.height = 1.8 * s
				trunk.mesh = cy
				trunk.material_override = _mat(Color(0.42, 0.28, 0.16))
				trunk.position = p + Vector3(0, 0.9 * s, 0)
				add_child(trunk)
				var crown = MeshInstance3D.new()
				var cs = SphereMesh.new()
				cs.radius = 1.4 * s
				cs.height = 2.4 * s
				crown.mesh = cs
				crown.material_override = _mat(Color(0.2, 0.5, 0.24).lerp(Color(0.3, 0.58, 0.22), rng.randf()))
				crown.position = p + Vector3(0, 2.6 * s, 0)
				add_child(crown)
			x += float(row[1]) * rng.randf_range(0.7, 1.4)
	var far_col = {"desert": Color(0.82, 0.6, 0.4), "volcano": Color(0.25, 0.2, 0.2), "beach": Color(0.35, 0.6, 0.8),
				   "city": Color(0.45, 0.5, 0.6)}.get(loc, Color(0.42, 0.47, 0.58))
	for i in range(14):                                      # painted far layer (mountains / skyline)
		var mx = -100.0 + i * 50.0 + rng.randf_range(-12, 12)
		var mz = -260.0 - rng.randf_range(0, 80)
		var mh = rng.randf_range(40, 80)
		if loc == "city":
			for b in range(3):
				var bm = _mat(far_col.lightened(b * 0.05))
				bm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
				bm.disable_fog = true
				_box(Vector3(14, mh * 0.6 + b * 8, 14), Vector3(mx + b * 13, (mh * 0.6 + b * 8) / 2, mz), bm)
			continue
		var m = MeshInstance3D.new()
		var cn = CylinderMesh.new()
		cn.top_radius = 0.0
		cn.bottom_radius = mh * 0.9
		cn.height = mh
		cn.radial_segments = 7
		m.mesh = cn
		var mm = _mat(far_col.lerp(Color(0.3, 0.34, 0.46), rng.randf() * 0.4))
		mm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mm.disable_fog = true
		m.material_override = mm
		m.position = Vector3(mx, mh / 2 - 2, mz)
		add_child(m)
	for i in range(8):
		var cl = Node3D.new()
		cl.position = Vector3(-80 + i * 70 + rng.randf_range(-15, 15), rng.randf_range(35, 55), -220 - rng.randf_range(0, 40))
		var ccol = scene.get("cloud", [1, 1, 1])
		for k in range(4):
			var pf = MeshInstance3D.new()
			var sp = SphereMesh.new()
			sp.radius = rng.randf_range(5, 8)
			sp.height = sp.radius * 1.2
			pf.mesh = sp
			var cm = _mat(Color(ccol[0], ccol[1], ccol[2]))
			cm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			cm.disable_fog = true
			pf.material_override = cm
			pf.position = Vector3(k * 7 - 10, rng.randf_range(-1.5, 1.5), 0)
			cl.add_child(pf)
		add_child(cl)


# ================================================================== hazards (3D, the engine's timing)
func _hazards() -> void:
	for h in scene["hazards"]:
		var ty = str(h["type"])
		var x = float(h["x"])
		var ln = float(h["lane"])
		var node = Node3D.new()
		add_child(node)
		var d = {"h": h, "node": node, "parts": {}}
		var base = lane_pos(x, ln)
		if ty == "pothole" or ty == "meteor":
			var hole = MeshInstance3D.new()
			var cm = CylinderMesh.new()
			cm.top_radius = 1.0
			cm.bottom_radius = 0.8
			cm.height = 0.05
			hole.mesh = cm
			hole.material_override = _mat(Color(0.07, 0.06, 0.06))
			var r = 1.6 if ty == "pothole" else 2.4
			hole.scale = Vector3(r, 1, 1.1)
			hole.position = lane_pos(x + (0.8 if ty == "pothole" else 0.0), ln, 0.015)
			node.add_child(hole)
			d["parts"]["hole"] = hole
			hole.visible = ty == "pothole"
		elif ty == "oil" or ty == "puddle":
			var pl = MeshInstance3D.new()
			var plm = PlaneMesh.new()
			plm.size = Vector2(9.4, 2.4)
			pl.mesh = plm
			if ty == "puddle":
				pl.material_override = _water_mat(true)
			else:
				var om = StandardMaterial3D.new()
				om.albedo_color = Color(0.03, 0.03, 0.05)
				om.roughness = 0.05
				om.metallic = 0.6
				pl.material_override = om
			pl.position = lane_pos(x + 2.5, ln, 0.02)
			node.add_child(pl)
		elif ty == "wall":
			var wall = _box(Vector3(1.0, 1.7, 2.3), lane_pos(x + 0.4, ln, 0.85), _mat(Color(0.72, 0.72, 0.75)))
			for j in range(4):
				var st = _box(Vector3(1.02, 0.16, 2.32), lane_pos(x + 0.4, ln, 0.35 + j * 0.35), _mat(Color(0.85, 0.1, 0.1)))
		elif ty == "crusher":
			for dx in [-1.6, 1.6]:
				_box(Vector3(0.4, 7.5, 0.4), lane_pos(x + dx, ln, 3.75) + Vector3(0, 0, -1.2), _mat(Color(0.3, 0.32, 0.38)))
				_box(Vector3(0.4, 7.5, 0.4), lane_pos(x + dx, ln, 3.75) + Vector3(0, 0, 1.2), _mat(Color(0.3, 0.32, 0.38)))
			_box(Vector3(4.0, 0.6, 2.8), lane_pos(x, ln, 7.8), _mat(Color(0.3, 0.32, 0.38)))
			var slab = _box(Vector3(3.0, 1.0, 2.2), lane_pos(x, ln, 6.3), _mat(Color(0.95, 0.75, 0.1)))
			var rod = _box(Vector3(0.5, 1.0, 0.5), lane_pos(x, ln, 7.0), _mat(Color(0.35, 0.35, 0.4)))
			d["parts"]["slab"] = slab
			d["parts"]["rod"] = rod
		elif ty == "hammer":
			for dx in [-2.8, 3.6]:
				_box(Vector3(0.44, 9.9, 0.44), lane_pos(x + dx, ln, 4.95), _mat(Color(0.32, 0.34, 0.4)))
			_box(Vector3(7.2, 0.7, 0.7), lane_pos(x + 0.4, ln, 9.85), _mat(Color(0.32, 0.34, 0.4)))
			var piv = Node3D.new()
			piv.position = lane_pos(x + 0.6, ln, 9.5)
			node.add_child(piv)
			var arm = MeshInstance3D.new()
			var am = BoxMesh.new()
			am.size = Vector3(0.3, 7.6, 0.3)
			arm.mesh = am
			arm.material_override = _mat(Color(0.55, 0.38, 0.2))
			arm.position = Vector3(0, -3.8, 0)
			piv.add_child(arm)
			var head = MeshInstance3D.new()
			var hm = BoxMesh.new()
			hm.size = Vector3(4.4, 1.9, 2.0)
			head.mesh = hm
			head.material_override = _mat(Color(0.55, 0.57, 0.62), 0.4)
			head.position = Vector3(0, -7.6 - 0.75, 0)
			piv.add_child(head)
			for side in [-1, 1]:
				var band = MeshInstance3D.new()
				var bm = BoxMesh.new()
				bm.size = Vector3(0.36, 1.92, 2.02)
				band.mesh = bm
				band.material_override = _mat(Color(0.85, 0.1, 0.1))
				band.position = Vector3(side * 2.0, -7.6 - 0.75, 0)
				piv.add_child(band)
			d["parts"]["pivot"] = piv
		elif ty == "laser":
			for dz in [-0.45, 0.45]:
				_box(Vector3(0.36, 2.2, 0.36), lane_pos(x, ln + dz, 1.1), _mat(Color(0.35, 0.36, 0.42)))
			var beams = []
			for hh in [0.6, 1.2, 1.8]:
				var pa = lane_pos(x, ln - 0.45, hh)
				var pb = lane_pos(x, ln + 0.45, hh)
				var bmat = StandardMaterial3D.new()
				bmat.albedo_color = Color(1, 0.1, 0.15)
				bmat.emission_enabled = true
				bmat.emission = Color(1, 0.1, 0.15)
				bmat.emission_energy_multiplier = 4.0
				bmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
				beams.append(_box(Vector3(0.06, 0.06, absf(pb.z - pa.z)), (pa + pb) / 2, bmat))
			d["parts"]["beams"] = beams
		elif ty == "container":
			var cols = [Color(0.9, 0.45, 0.1), Color(0.15, 0.45, 0.8), Color(0.75, 0.15, 0.15)]
			var box = _box(Vector3(3.3, 2.6, 2.4), lane_pos(x + 1.55, ln, 1.3), _mat(cols[int(x) % 3], 0.6))
			box.visible = false
			var lb = Label3D.new()
			lb.text = "MEGA"
			lb.font_size = 160
			lb.pixel_size = 0.006
			lb.outline_size = 20
			lb.position = Vector3(0, 0, 1.22)
			box.add_child(lb)
			d["parts"]["box"] = box
		elif ty == "ramp":
			var rp = MeshInstance3D.new()
			var pm = PrismMesh.new()
			pm.size = Vector3(5.5, 1.3, 2.2)
			pm.left_to_right = 1.0
			rp.mesh = pm
			rp.material_override = _mat(Color(0.85, 0.55, 0.25))
			rp.position = lane_pos(x - 2.75, ln, 0.65)
			node.add_child(rp)
		elif ty == "lava":
			var crack = StandardMaterial3D.new()
			crack.albedo_color = Color(1, 0.45, 0.05)
			crack.emission_enabled = true
			crack.emission = Color(1, 0.4, 0.05)
			crack.emission_energy_multiplier = 3.0
			_box(Vector3(2.4, 0.04, 1.6), lane_pos(x, ln, 0.02), crack)
		hz_nodes.append(d)


func _hazards_update(t: float) -> void:
	for d in hz_nodes:
		var h = d["h"]
		var ty = str(h["type"])
		var tr = h["trig"]
		var a = null if tr == null else t - float(tr)
		var x = float(h["x"])
		var ln = float(h["lane"])
		if ty == "hammer":                                   # same pendulum as draw_hammer
			var ang = 0.0
			if a == null or a < -0.35:
				ang = 0.75 * sin(t * 2.4)
			elif a < 0.0:
				ang = 0.75 * pow(1.0 - (a + 0.35) / 0.35, 2.0)
			elif a < 1.1:
				ang = 0.0
			else:
				ang = 0.9 * minf(1.0, (a - 1.1) / 0.8) * sin(minf(PI / 2, (a - 1.1) * 2.0))
			d["parts"]["pivot"].rotation = Vector3(0, 0, ang)
		elif ty == "crusher":                                # same press timing as draw_hazard_front
			var drop = 0.0
			if a != null:
				if a < 0:
					drop = 0.0
				elif a < 0.08:
					drop = a / 0.08
				elif a < 1.2:
					drop = 1.0
				else:
					drop = maxf(0.0, 1.0 - (a - 1.2) / 0.8)
				if -0.25 < a and a < 0:
					drop = (a + 0.25) / 0.25 * 0.9
			var bottom_y = 7.5 - 1.2 - drop * (7.5 - 1.2 - 0.5)
			d["parts"]["slab"].position = lane_pos(x, ln, bottom_y + 0.5)
			var rod_len = maxf(0.2, 7.5 - (bottom_y + 1.0))
			d["parts"]["rod"].scale = Vector3(1, rod_len, 1)
			d["parts"]["rod"].position = lane_pos(x, ln, 7.5 - rod_len / 2)
		elif ty == "container":
			var box = d["parts"]["box"]
			if a == null or a < -0.45:
				box.visible = false
			else:
				box.visible = true
				var drop = 1.0 if a >= -0.05 else 1.0 - pow((a + 0.45) / 0.4, 2.0)
				box.position = lane_pos(x + 1.55, ln, 1.3 + (1.0 - drop) * 22.0)
		elif ty == "laser":
			var on = 0.7 + 0.3 * sin(t * 40)
			for b in d["parts"]["beams"]:
				b.material_override.emission_energy_multiplier = 2.0 + 3.0 * on
		elif ty == "meteor":
			d["parts"]["hole"].visible = a != null and a >= 0.0


# ================================================================== cars
func _car(vk: String) -> void:
	var c = cast[vk]
	var root = Node3D.new()
	add_child(root)
	var flip = Node3D.new()                                  # yaw squeeze / squash pivot at the ground point
	root.add_child(flip)
	var body = MeshInstance3D.new()
	var sh = Shader.new()
	sh.code = """
shader_type spatial;
render_mode cull_disabled;
uniform sampler2D tex : source_color, filter_linear;
uniform float dmg = 0.0;
uniform vec2 hit = vec2(0.75, 0.5);
uniform float burn = 0.0;
uniform float split = 0.0;
uniform float ice = 0.0;
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
	if (split > 0.01) { float side = VERTEX.x > 0.0 ? 1.0 : -1.0; VERTEX.x += side * split * 0.5; }
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
	col = mix(col, vec3(0.7, 0.9, 1.0), ice * 0.55);   // frozen by the ice dragon
	ALBEDO = col;
	ROUGHNESS = 0.6;
}
"""
	var mat = ShaderMaterial.new()
	mat.shader = sh
	body.material_override = mat
	body.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	var pm = PlaneMesh.new()
	pm.size = Vector2(float(c["w"]) / 60.0, float(c["h"]) / 60.0)
	pm.orientation = PlaneMesh.FACE_Z
	pm.subdivide_width = 40
	pm.subdivide_depth = 14
	body.mesh = pm
	var bh = float(c["body"][1])
	var r = float(c["wheel_r"])
	var ride = r + 0.6 * float(c["travel"]) + bh / 2.0
	body.position = Vector3(0, ride, 0.03)
	flip.add_child(body)
	var wl = []
	for lx in c["wheel_x"]:
		var w = Sprite3D.new()
		w.texture = tex[vk + "_wheel"]
		w.pixel_size = 1.0 / 60.0
		w.shaded = true
		w.double_sided = true
		w.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		w.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
		w.position = Vector3(float(lx), r, -0.02)
		flip.add_child(w)
		wl.append(w)
	_headlights(flip, float(c["body"][0]) / 2.0, ride, -float(c["body"][0]) / 2.0)
	var blob = MeshInstance3D.new()
	var cm = CylinderMesh.new()
	cm.top_radius = 0.5
	cm.bottom_radius = 0.5
	cm.height = 0.01
	blob.mesh = cm
	var bm = StandardMaterial3D.new()
	bm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	bm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	bm.albedo_texture = dot_tex
	bm.albedo_color = Color(0, 0, 0, 0.45)
	blob.material_override = bm
	blob.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	blob.scale = Vector3(float(c["body"][0]) * 1.1, 1, 1.4)
	add_child(blob)
	var smoke = _emitter(20, 1.6, Vector2(0.6, 1.8), Vector3(0, 1.5, 0), Vector2(0.4, 1.0), Color(0.25, 0.24, 0.24, 0.7),
						 Color(0.4, 0.4, 0.42, 0), 25.0, false)
	smoke.local_coords = false
	smoke.position = Vector3(0, ride + bh / 2, 0.1)
	flip.add_child(smoke)
	cars.append({"vk": vk, "root": root, "flip": flip, "body": body, "mat": mat, "wheels": wl, "blob": blob,
				 "smoke": smoke, "dmg": 0.0, "dmg_t": 0.0, "hit": Vector2(0.75, 0.5), "ride": ride})


func _hit_car(ci: int, kind: String, x: float, zl: float) -> void:
	## BeamNG-style: dent where it struck + panels / bolts off, never an explosion (meteor / fire excepted)
	var cr = cars[ci]
	var c = cast[cr["vk"]]
	var bw = float(c["body"][0])
	var p = cr["root"].global_position
	var spot = {"wall": Vector2(0.85, 0.5), "container": Vector2(0.85, 0.5), "hammer": Vector2(0.5, 0.2),
				"crusher": Vector2(0.5, 0.2), "laser": Vector2(0.5, 0.5), "meteor": Vector2(0.5, 0.3)}.get(kind, Vector2(0.7, 0.6))
	cr["hit"] = spot
	cr["dmg_t"] = minf(1.0, float(cr["dmg_t"]) + (1.0 if kind in ["wall", "hammer", "crusher", "container", "meteor"] else 0.45))
	var t = tex[cr["vk"] + "_normal"]
	var tsz = t.get_size()
	var n = 12 if kind in ["wall", "container", "hammer", "crusher"] else 6
	for i in range(n):                                       # panels cut from the car's own art
		var fw = rng.randf_range(0.18, 0.34)
		var fh = rng.randf_range(0.25, 0.5)
		var rx = rng.randf_range(0.0, 1.0 - fw)
		var ry = rng.randf_range(0.0, 1.0 - fh)
		var bh = float(c["body"][1])
		var rb = RigidBody3D.new()
		rb.mass = 25.0
		var cs = CollisionShape3D.new()
		var bs = BoxShape3D.new()
		bs.size = Vector3(bw * fw, bh * fh, 0.2)
		cs.shape = bs
		rb.add_child(cs)
		var s = Sprite3D.new()
		s.texture = t
		s.region_enabled = true
		s.region_rect = Rect2(tsz.x / 2 - bw * 30 + rx * bw * 60, tsz.y / 2 - bh * 30 + ry * bh * 60, fw * bw * 60, fh * bh * 60)
		s.pixel_size = 1.0 / 60.0
		s.shaded = true
		s.double_sided = true
		s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
		rb.add_child(s)
		rb.position = p + Vector3((rx + fw / 2 - 0.5) * bw, float(cr["ride"]) + (0.5 - ry - fh / 2) * bh, 0.3)
		fx_root.add_child(rb)
		rb.linear_velocity = Vector3(rng.randf_range(-7, 7), rng.randf_range(4, 11), rng.randf_range(-1.5, 3.5))
		rb.angular_velocity = Vector3(rng.randf_range(-9, 9), rng.randf_range(-9, 9), rng.randf_range(-12, 12))
	_bolts(p + Vector3(0, float(cr["ride"]), 0.3), 8, 8.0)
	_burst(p + Vector3(0, float(cr["ride"]), 0.4), 40, 0.45, Vector2(5, 12), Vector3(0, -14, 0), Vector2(0.05, 0.11),
		   Color(1, 0.95, 0.6), Color(1, 0.6, 0.2, 0))


func _event_fx(kind: String, x: float, zl: float) -> void:
	var p = lane_pos(x, zl)
	if kind in ["land", "bump", "pothole"]:
		_burst(p + Vector3(0, 0.2, 0), 18, 0.7, Vector2(1.5, 3.5), Vector3(0, -6, 0), Vector2(0.15, 0.35),
			   Color(0.6, 0.52, 0.42, 0.6), Color(0.55, 0.5, 0.45, 0), 60.0, false)
	elif kind == "puddle":
		_burst(p + Vector3(0, 0.2, 0), 160, 1.1, Vector2(5, 11), Vector3(0, -14, 0), Vector2(0.18, 0.45),
			   Color(1, 1, 1, 0.95), Color(0.75, 0.9, 1.0, 0), 45.0, false)
	elif kind == "oil":
		_burst(p + Vector3(0, 0.2, 0), 70, 0.9, Vector2(3, 7), Vector3(0, -14, 0), Vector2(0.12, 0.3),
			   Color(0.05, 0.05, 0.07, 0.95), Color(0.1, 0.1, 0.12, 0), 50.0, false)
	elif kind in ["wall", "container"]:
		for i in range(10):                                  # concrete / steel chunks
			var rb = RigidBody3D.new()
			rb.mass = 20.0
			var cs = CollisionShape3D.new()
			var bs = BoxShape3D.new()
			bs.size = Vector3(0.3, 0.25, 0.3)
			cs.shape = bs
			rb.add_child(cs)
			var mi = MeshInstance3D.new()
			var bmm = BoxMesh.new()
			bmm.size = bs.size
			mi.mesh = bmm
			mi.material_override = _mat(Color(0.65, 0.65, 0.67))
			rb.add_child(mi)
			rb.position = p + Vector3(0, 1.0, 0)
			fx_root.add_child(rb)
			rb.linear_velocity = Vector3(rng.randf_range(-6, 3), rng.randf_range(3, 8), rng.randf_range(-2, 3))
		_burst(p + Vector3(0, 0.6, 0), 40, 1.0, Vector2(2, 5), Vector3(0, -3, 0), Vector2(0.4, 0.9),
			   Color(0.75, 0.7, 0.6, 0.7), Color(0.7, 0.68, 0.62, 0), 70.0, false)


# ================================================================== per frame
func _process(_d: float) -> void:
	var i = clampi(start_off + Engine.get_process_frames() - 1, 0, frames.size() - 1)
	var f = frames[i]
	var mode = str(f[0])
	var t = float(f[1])
	if t < last_st - 0.05 or (mode != last_mode and mode == "r" and last_mode != ""):   # replay / rewind: fresh fx
		for ch in fx_root.get_children():
			ch.queue_free()
		fired = {}
		for cr in cars:
			cr["dmg"] = 0.0
			cr["dmg_t"] = 0.0
		last_st = t - 0.001
	if last_st < 0:
		last_st = t - 0.001
	Engine.time_scale = clampf((t - last_st) * 30.0, 0.05, 1.5)
	# camera = race25d's camera (focal 900 x zoom, horizon at the engine's y, lens shift for the shake)
	var zoom = float(f[3])
	var fpx = 900.0 * zoom
	var yh = 1520.0 + (float(P["Y_H"]) - 1520.0) * zoom + float(P["WORLD_DY"]) + float(f[5])
	cam.position = Vector3(float(f[2]), float(P["CAM_H"]), 0)
	cam.size = 1080.0 / fpx * cam.near
	cam.frustum_offset = Vector2(-float(f[4]) / fpx * cam.near, -(960.0 - yh) / fpx * cam.near)
	_hazards_update(t)
	var cs = f[6]
	for ci in range(cars.size()):
		var cr = cars[ci]
		var s = cs[ci]
		var x = float(s[0])
		var z = float(s[1])                                  # already includes the curve
		var h = float(s[2])
		var ys = clampf(_yaw_scale(float(s[3])), -1.0, 1.0)
		var sq = float(s[6])
		cr["root"].position = Vector3(x, maxf(0.0, h), depth(z))
		cr["root"].rotation = Vector3(0, 0, float(s[4]))
		var widen = 1.0 + 0.35 * maxf(0.0, 1.0 - sq)
		cr["flip"].scale = Vector3((ys if absf(ys) > 0.05 else 0.05) * widen, sq, 1.0)
		cr["mat"].set_shader_parameter("tex", tex[cr["vk"] + "_" + str(s[12])])
		cr["dmg"] = float(cr["dmg"]) + (float(cr["dmg_t"]) - float(cr["dmg"])) * 0.35
		cr["mat"].set_shader_parameter("dmg", cr["dmg"])
		cr["mat"].set_shader_parameter("hit", cr["hit"])
		var burn = 1.0 if float(s[8]) > 0.5 else 0.0
		cr["mat"].set_shader_parameter("burn", burn * 0.7)
		cr["smoke"].emitting = burn > 0.5
		cr["body"].position.x = 0.0
		if float(s[7]) > 0.01:                               # laser: the two halves drift apart (shader split)
			cr["mat"].set_shader_parameter("split", float(s[7]))
		else:
			cr["mat"].set_shader_parameter("split", 0.0)
		var ice = float(s[10])
		cr["body"].transparency = 0.0
		cr["mat"].set_shader_parameter("ice", ice)
		for k in range(cr["wheels"].size()):
			cr["wheels"][k].rotation = Vector3(0, 0, -x / float(cast[cr["vk"]]["wheel_r"]))
		cr["blob"].position = Vector3(x, 0.03, depth(z))
		cr["blob"].material_override.albedo_color.a = 0.45 * clampf(1.0 - maxf(0.0, h) / 5.0, 0.0, 1.0)
	# events: impacts / splashes, and the hit car dents (fire once per pass; a replay fires them again)
	var k2 = 0
	for ev in scene["events"]:
		var key = "e" + str(k2)
		k2 += 1
		var et = float(ev[1])
		if fired.has(key) or et > t or et <= last_st:
			continue
		fired[key] = true
		var kind = str(ev[0])
		_event_fx(kind, float(ev[2]), float(ev[3]))
		if kind in ["wall", "hammer", "crusher", "container", "meteor", "laser", "pothole"]:
			var best = -1
			var bd = 1e9
			for ci in range(cars.size()):
				var dd = absf(float(cs[ci][0]) - float(ev[2])) + absf(float(cs[ci][1]) - float(ev[3])) * 3.0
				if dd < bd:
					bd = dd
					best = ci
			if best >= 0:
				_hit_car(best, kind, float(ev[2]), float(ev[3]))
	last_st = t
	last_mode = mode


func _yaw_scale(yaw: float) -> float:
	var c = cos(yaw)
	return 1.0 if absf(yaw) < 1e-4 else signf(c) * maxf(absf(c), 0.16)


func _img(p: String) -> ImageTexture:
	return ImageTexture.create_from_image(Image.load_from_file(p))


func is_vulkan() -> bool:
	return RenderingServer.get_current_rendering_driver_name() == "vulkan"


func _mat(col: Color, rough := 0.85) -> StandardMaterial3D:
	var m = StandardMaterial3D.new()
	m.albedo_color = col
	m.roughness = rough
	return m


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
