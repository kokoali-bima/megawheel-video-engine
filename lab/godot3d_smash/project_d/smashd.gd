extends Node3D
## LAB — 3D SMASH driven by the aired engine (smash25d.py v5, export_smash.py). The engine's overlay brings HUD,
## intros, bubbles, chaos, the shark, smoke, banners, replay and end card; this scene re-draws the world in 3D:
## the shrinking steel arena over sea / lava / mud / ice, the stands with the crowd, circling fins, and the cars,
## which dent where they are hit and shed panels (no explosions; the engine's missile/meteor stays in the overlay).
## Projection = smash25d: k(z) = 6000 / (100 + 8 z) -> level camera CAM_H m high, depth 12.5 + z m, focal 750 px x zoom.

var dir = "/root/lab/s3d/s2"
var start_off = 0
var scene = {}
var frames = []
var cast = {}
var tex = {}
var dot_tex: GradientTexture2D
var pow_tex: ImageTexture
var cam: Camera3D
var fx_root: Node3D
var cars = []
var rng = RandomNumberGenerator.new()
var last_st = -1.0
var fired = {}
var P = {}
var floor_mesh: MeshInstance3D
var rim = []
var fins = []
var crowd: MultiMeshInstance3D


func depth(z: float) -> float:
	return -(float(P["D0"]) + float(P["DZ"]) * z) / 8.0


func wp(x: float, z: float, h := 0.0) -> Vector3:
	return Vector3(x, h, depth(z))


func bounds(t: float) -> Vector2:
	var b = scene["bounds10"]
	var i = clampi(int(t * 10.0), 0, b.size() - 1)
	return Vector2(float(b[i][0]), float(b[i][1]))


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
	rng.seed = 21
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
	_arena()
	_stands()
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
	sm.ground_bottom_color = Color(top[0], top[1], top[2])   # no brown band above the stands (lens-shifted camera)
	sk.sky_material = sm
	env.background_mode = Environment.BG_SKY
	env.sky = sk
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(1, 0.97, 0.95) if not scene["night"] else Color(0.55, 0.6, 0.85)
	env.ambient_light_energy = 0.45 * float(scene["light"])
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.glow_enabled = true
	env.glow_intensity = 0.3
	var we = WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun = DirectionalLight3D.new()                       # from the camera side (CONFIG_BEST lesson 10)
	sun.rotation_degrees = Vector3(-62, 8, 0)                # high, from the camera side: short shadows behind
	sun.light_energy = 0.8 * float(scene["light"]) * (0.45 if scene["night"] else 1.0)
	# no sun shadow map: with the lens-shifted SMASH camera it put a big dark wedge on the floor (S008 test);
	# cars stand on contact blobs, like the aired 2.5D
	sun.shadow_enabled = false
	add_child(sun)


func _arena() -> void:
	var ar = str(scene["arena"])
	var zc = float(P["ZC"])
	# the danger zone around the floor (sea / lava / mud / ice), out to the stands
	var dz = MeshInstance3D.new()
	var pm = PlaneMesh.new()
	pm.size = Vector2(200, 30)
	pm.subdivide_width = 100
	pm.subdivide_depth = 15
	dz.mesh = pm
	if ar == "sea" or ar == "ice":
		dz.material_override = _water_mat(false)
	elif ar == "lava":
		var lm = StandardMaterial3D.new()
		lm.albedo_color = Color(1, 0.4, 0.05)
		lm.emission_enabled = true
		lm.emission = Color(1, 0.35, 0.05)
		lm.emission_energy_multiplier = 2.0
		dz.material_override = lm
	else:
		dz.material_override = _mat(Color(0.36, 0.24, 0.13), 0.9)
	dz.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	dz.position = Vector3(0, -0.6, (depth(zc - 9.0) + depth(zc + 9.0)) / 2.0)
	dz.scale = Vector3(1, 1, absf(depth(zc + 9.0) - depth(zc - 9.0)) / 30.0)
	add_child(dz)
	# the floor: a slab whose size follows the engine's shrinking bounds
	floor_mesh = MeshInstance3D.new()
	var bm = BoxMesh.new()
	bm.size = Vector3(1, 0.5, 1)
	floor_mesh.mesh = bm
	var top = {"lava": Color(0.44, 0.45, 0.5), "sea": Color(0.44, 0.45, 0.5), "mud": Color(0.72, 0.56, 0.36),
			   "ice": Color(0.85, 0.94, 1.0)}.get(ar, Color(0.55, 0.56, 0.6))
	var fm = _mat(Color(1, 1, 1), 0.55 if ar != "ice" else 0.1)
	fm.metallic = 0.25 if ar in ["sea", "lava"] else 0.0
	var img = Image.create(64, 64, false, Image.FORMAT_RGB8)  # steel plates like the aired floor (world-space tiles)
	img.fill(top)
	var line = top.darkened(0.45) if ar in ["sea", "lava"] else top.darkened(0.15)
	for q in range(64):
		for w in range(2):
			img.set_pixel(q, w, line)
			img.set_pixel(w, q, line)
	fm.albedo_texture = ImageTexture.create_from_image(img)
	fm.uv1_triplanar = true
	fm.uv1_world_triplanar = true
	fm.uv1_scale = Vector3(0.4, 0.5, 0.4)
	floor_mesh.material_override = fm
	floor_mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(floor_mesh)
	for i in range(4):                                       # hazard-striped rim
		var r = _box(Vector3(1, 0.3, 0.3), Vector3.ZERO, _mat(Color(1, 0.85, 0.1)))
		r.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		rim.append(r)
	if ar == "sea":                                          # two shark fins circling the floor
		var fin_mat = _mat(Color(0.42, 0.56, 0.7))
		for i in range(2):
			var f = MeshInstance3D.new()
			var pr = PrismMesh.new()
			pr.size = Vector3(1.2, 1.1, 0.12)
			pr.left_to_right = 0.7
			f.mesh = pr
			f.material_override = fin_mat
			f.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			add_child(f)
			fins.append(f)


func _arena_update(t: float) -> void:
	var b = bounds(t)
	var hx = b.x
	var hz = b.y
	var zc = float(P["ZC"])
	var zf = depth(zc - hz)
	var zb = depth(zc + hz)
	floor_mesh.scale = Vector3(hx * 2.0, 1, absf(zf - zb))
	floor_mesh.position = Vector3(0, -0.25, (zf + zb) / 2.0)
	var d = absf(zf - zb)
	rim[0].scale = Vector3(hx * 2 + 0.3, 1, 1)
	rim[0].position = Vector3(0, 0.0, zf + 0.15)
	rim[1].scale = Vector3(hx * 2 + 0.3, 1, 1)
	rim[1].position = Vector3(0, 0.0, zb - 0.15)
	rim[2].scale = Vector3(1, 1, d / 0.3)
	rim[2].position = Vector3(-hx - 0.15, 0.0, (zf + zb) / 2)
	rim[3].scale = Vector3(1, 1, d / 0.3)
	rim[3].position = Vector3(hx + 0.15, 0.0, (zf + zb) / 2)
	for i in range(fins.size()):
		var a = t * (0.35 + 0.06 * i) + i * PI + 0.6
		var back = sin(a) > 0
		var fz = zc + sin(a) * ((hz + 1.2) if back else (hz + 2.4))
		var fx = cos(a) * (hx + 3.0)
		fins[i].position = Vector3(fx, -0.2, depth(fz))
		fins[i].rotation = Vector3(0, PI if sin(a) > 0 else 0.0, 0)


func _stands() -> void:
	var zb = float(P["ZC"]) + float(P["HZ0"]) + 3.0
	var rows = int(P["STANDS_ROWS"])
	var stand = _mat(Color(0.45, 0.47, 0.55))
	for row in range(rows):
		var z = zb + row * 1.6
		_box(Vector3(220, 1.25, absf(depth(z + 0.8) - depth(z - 0.8))), Vector3(0, 0.62 + row * 1.25, depth(z)), stand)
	var wall = _box(Vector3(220, 0.9, 0.4), Vector3(0, 0.45, depth(zb - 0.6)), _mat(Color(0.12, 0.12, 0.2)))
	var mm = MultiMesh.new()                                  # the crowd
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	var sp = SphereMesh.new()
	sp.radius = 0.32
	sp.height = 0.64
	mm.mesh = sp
	mm.instance_count = rows * 200
	var cols = [Color(0.95, 0.3, 0.3), Color(0.3, 0.6, 0.95), Color(0.98, 0.8, 0.2), Color(0.4, 0.8, 0.4), Color(0.9, 0.5, 0.9)]
	var k = 0
	for row in range(rows):
		for j in range(200):
			var x = -100.0 + j * 1.0 + rng.randf_range(0, 0.4)
			mm.set_instance_transform(k, Transform3D(Basis(), Vector3(x, 1.25 + row * 1.25 + 0.3, depth(zb + row * 1.6))))
			mm.set_instance_color(k, cols[rng.randi() % 5])
			k += 1
	crowd = MultiMeshInstance3D.new()
	crowd.multimesh = mm
	var cm = StandardMaterial3D.new()
	cm.vertex_color_use_as_albedo = true
	crowd.material_override = cm
	crowd.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(crowd)
	var x0 = -96.0
	while x0 < 96.0:                                         # SMASH ARENA banner on the front wall
		var lb = Label3D.new()
		lb.text = "SMASH ARENA"
		lb.font_size = 96
		lb.pixel_size = 0.012
		lb.modulate = Color(1, 0.86, 0.12)
		lb.outline_size = 16
		lb.outline_modulate = Color(0.12, 0.12, 0.2)
		lb.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		lb.position = Vector3(x0, 0.45, depth(zb - 0.6) + 0.21)
		add_child(lb)
		x0 += 12.0


func _car(vk: String) -> void:
	var c = cast[vk]
	var root = Node3D.new()
	add_child(root)
	var flip = Node3D.new()
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
uniform float lift = 0.0;
float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float n(vec2 p) { vec2 i = floor(p); vec2 f = fract(p); f = f * f * (3.0 - 2.0 * f);
	return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
float local(vec2 uv) { vec2 d = uv - hit; return dmg * exp(-dot(d, d) / 0.05) + dmg * 0.22; }
void vertex() {
	float d = local(UV);
	vec2 dir = normalize(UV - hit + vec2(1e-4));
	VERTEX.x += dir.x * d * 0.45;                       // the impact side is pushed in (crushed)
	VERTEX.y += (n(UV * 9.0) - 0.5) * d * 0.45;         // wrinkles
	VERTEX.z += (n(UV * 6.0 + 3.0) - 0.5) * d * 0.9;     // bent out of shape (really 3D)
	if (split > 0.01) { float side = UV.x > 0.5 ? 1.0 : -1.0; VERTEX.x += side * split * 0.5; VERTEX.y += side * split * 0.15; }
}
void fragment() {
	vec4 c = texture(tex, UV);
	if (c.a < 0.5) discard;
	float d = local(UV);
	vec3 col = c.rgb * (1.0 - 0.35 * min(d, 1.0));
	float scratch = step(0.96, fract((UV.x * 1.3 + UV.y) * 38.0 + n(UV * 20.0) * 2.0)) * step(0.3, d);
	col = mix(col, vec3(0.78, 0.78, 0.8), scratch * 0.8);   // bare metal scratches
	col = mix(col, vec3(0.08, 0.06, 0.05), burn * (0.55 + 0.35 * n(UV * 14.0)));
	col = mix(col, vec3(0.7, 0.9, 1.0), ice * 0.55);   // frozen by the ice dragon
	ALBEDO = col;
	EMISSION = col * lift;                              // night: the arena floodlights still show the paint
	ROUGHNESS = 0.6;
}
"""
	var mat = ShaderMaterial.new()
	mat.shader = sh
	mat.set_shader_parameter("lift", 0.35 if scene["night"] else 0.0)
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
	cars.append({"vk": vk, "root": root, "flip": flip, "body": body, "mat": mat, "wheels": wl, "blob": blob,
				 "dmg": 0.0, "dmg_t": 0.0, "hit": Vector2(0.75, 0.5), "ride": ride})


func _panels(ci: int, n: int, vel: float) -> void:
	var cr = cars[ci]
	var c = cast[cr["vk"]]
	var bw = float(c["body"][0])
	var bh = float(c["body"][1])
	var t = tex[cr["vk"] + "_normal"]
	var tsz = t.get_size()
	var p = cr["root"].global_position
	for i in range(n):
		var fw = minf(rng.randf_range(0.45, 0.85) / bw, 0.34)          # 0.45-0.85 m pieces whatever the car size
		var fh = minf(rng.randf_range(0.35, 0.65) / bh, 0.5)
		var rx = rng.randf_range(0.0, 1.0 - fw)
		var ry = rng.randf_range(0.0, 1.0 - fh)
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
		rb.linear_velocity = Vector3(rng.randf_range(-1, 1) * vel, rng.randf_range(0.5, 1.2) * vel, rng.randf_range(-0.2, 0.5) * vel)
		rb.angular_velocity = Vector3(rng.randf_range(-9, 9), rng.randf_range(-9, 9), rng.randf_range(-12, 12))
	_bolts(p + Vector3(0, float(cr["ride"]), 0.3), n / 2 + 2, vel)


func _process(_d: float) -> void:
	var i = clampi(start_off + Engine.get_process_frames() - 1, 0, frames.size() - 1)
	var f = frames[i]
	var mode = str(f[0])
	var t = 0.0 if mode == "i" else float(f[1])
	if t < last_st - 0.05:                                    # replay rewinds: fresh effects
		for ch in fx_root.get_children():
			ch.queue_free()
		fired = {}
		for cr in cars:
			cr["dmg"] = 0.0
			cr["dmg_t"] = 0.0
		last_st = t - 0.001
	if last_st < 0:
		last_st = t - 0.001
	Engine.time_scale = clampf((t - last_st) * 30.0, 0.05, 1.5) if mode != "i" else 1.0
	var zoom = float(f[3])
	var fpx = 750.0 * zoom
	var yh = float(P["PIV_Y"]) + (float(P["Y_H"]) - float(P["PIV_Y"])) * zoom + float(P["WORLD_DY"]) + float(f[5])
	cam.position = Vector3(float(f[2]), float(P["CAM_H"]), 0)
	cam.size = 1080.0 / fpx * cam.near
	cam.frustum_offset = Vector2(-float(f[4]) / fpx * cam.near, -(960.0 - yh) / fpx * cam.near)
	_arena_update(t)
	var cs = f[6]
	for ci in range(cars.size()):
		var cr = cars[ci]
		var s = cs[ci]
		var x = float(s[0])
		var z = float(s[1])
		var h = float(s[2])
		var sink = float(s[13])
		var out_kind = str(s[16])
		cr["root"].visible = sink < 1.0
		cr["blob"].visible = sink <= 0.0
		var y = maxf(0.0, h) - (sink * 2.2 if out_kind == "ring" else 0.0)
		if bool(s[15]) and out_kind == "ring" and sink <= 0.0:
			y = maxf(y, h)
		cr["root"].position = Vector3(x, y, depth(z))
		cr["root"].rotation = Vector3(0, 0, float(s[4]) + (0.22 if out_kind == "wreck" else 0.0))
		var ys = _yaw_scale(float(s[3]))
		var sq = float(s[6]) * (0.88 if out_kind == "wreck" else 1.0)
		var widen = 1.0 + 0.35 * maxf(0.0, 1.0 - sq)
		cr["flip"].scale = Vector3((ys if absf(ys) > 0.05 else 0.05) * widen, sq, 1.0)
		cr["mat"].set_shader_parameter("tex", tex[cr["vk"] + "_" + str(s[12])])
		var hp = float(s[14])
		cr["dmg_t"] = maxf(float(cr["dmg_t"]), clampf((100.0 - hp) / 100.0, 0.0, 1.0) * 0.8 + (0.3 if out_kind == "wreck" else 0.0))
		cr["dmg"] = float(cr["dmg"]) + (float(cr["dmg_t"]) - float(cr["dmg"])) * 0.3
		cr["mat"].set_shader_parameter("dmg", cr["dmg"])
		cr["mat"].set_shader_parameter("hit", cr["hit"])
		cr["mat"].set_shader_parameter("burn", 0.7 if float(s[8]) > 0.5 else 0.0)
		cr["mat"].set_shader_parameter("split", 0.0)
		cr["mat"].set_shader_parameter("ice", 0.0)
		for w in cr["wheels"]:
			w.rotation = Vector3(0, 0, -x / float(cast[cr["vk"]]["wheel_r"]))
		cr["blob"].position = Vector3(x, 0.03, depth(z))
		cr["blob"].material_override.albedo_color.a = 0.45 * clampf(1.0 - maxf(0.0, h) / 5.0, 0.0, 1.0)
	var k2 = 0
	for ev in scene["events"]:
		var key = "e" + str(k2)
		k2 += 1
		var et = float(ev[1])
		if fired.has(key) or et > t or et <= last_st or mode == "i":
			continue
		fired[key] = true
		var kind = str(ev[0])
		var ex = float(ev[2])
		var ez = float(ev[3])
		var best = -1
		var bd = 1e9
		for ci in range(cars.size()):
			var dd = absf(float(cs[ci][0]) - ex) + absf(float(cs[ci][1]) - ez)
			if dd < bd:
				bd = dd
				best = ci
		if kind == "hit" and ev.size() > 4 and float(ev[4]) > 0.5 and best >= 0:
			cars[best]["hit"] = Vector2(0.8 if ex > float(cs[best][0]) else 0.2, 0.5)
			_panels(best, 8, 7.0)
		elif kind == "wreck" and best >= 0:
			cars[best]["dmg_t"] = 1.0
			_panels(best, 16, 9.0)
		elif kind == "ringout":
			var ar = str(scene["arena"])
			if ar == "sea" or ar == "ice":
				_burst(wp(ex, ez, -0.4), 160, 1.3, Vector2(5, 12), Vector3(0, -14, 0), Vector2(0.2, 0.5),
					   Color(1, 1, 1, 0.95), Color(0.75, 0.9, 1.0, 0), 40.0, false)
			elif ar == "lava":
				_burst(wp(ex, ez, -0.2), 120, 1.0, Vector2(4, 10), Vector3(0, -10, 0), Vector2(0.2, 0.6),
					   Color(1, 0.8, 0.3), Color(1, 0.3, 0.05, 0), 40.0)
		elif kind == "land":
			_burst(wp(ex, ez, 0.1), 16, 0.6, Vector2(1.5, 3.5), Vector3(0, -6, 0), Vector2(0.15, 0.35),
				   Color(0.6, 0.6, 0.62, 0.6), Color(0.55, 0.55, 0.57, 0), 60.0, false)
	last_st = t


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
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF   # scenery: no shadow on the floor
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
	## night theme: real headlights (a spot on the floor ahead) + glowing lamp + red tail light; inside `flip`,
	## so they turn with the car. Tilted down more than RACE: the SMASH camera looks from 20 m high.
	if not scene["night"]:
		return
	var sp = SpotLight3D.new()
	sp.position = Vector3(front_x, y, 0.3)
	sp.rotation_degrees = Vector3(0, -90, 0)               # along +x (the way the sprite faces)
	sp.rotate_object_local(Vector3.RIGHT, deg_to_rad(-22))
	sp.light_color = Color(1, 0.95, 0.75)
	sp.light_energy = 5.0
	sp.spot_range = 12.0
	sp.spot_angle = 28.0
	parent.add_child(sp)
	for pr in [[front_x, Color(1, 0.97, 0.8), 0.2], [back_x, Color(1, 0.1, 0.1), 0.13]]:
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
