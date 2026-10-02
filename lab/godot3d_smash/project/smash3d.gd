extends Node3D
## LAB plan B — SMASH ARENA in real 3D. Same format as smash25d (3/4 high camera over a lava arena, stands behind,
## HP bars, bubbles, winner, end card) but: real 3D light + shadows, glowing lava, rigid-body cars that shove,
## bounce, roll, get blasted into the air and fall into the lava, cars breaking into pieces, missiles, Kraggor's foot.
## The cast stays our paper-cutout art (sprites exported from the cairo engine), lit by the 3D lights.
##   godot --path project --write-movie out.avi --fixed-fps 30 --quit-after N -- <sprite_dir>

const ARENA_HX = 13.0
const ARENA_HZ = 5.0
const T_FIGHT = 34.0
var sprite_dir = "/root/lab/fx/sprites"
var cast = {}
var cars = []
var cam: Camera3D
var hud: CanvasLayer
var hp_rows = []
var title_lbl: Label
var sub_lbl: Label
var win_lbl: Label
var cta: Panel
var font: FontFile
var dot_tex: GradientTexture2D
var events = []
var t = 0.0
var shake = 0.0
var slow_used = false
var slow_until = -1.0
var winner = null
var chaos = [[6.0, "missile"], [11.5, "kraggor"], [16.5, "missile"], [22.0, "missile"], [27.0, "kraggor"]]
var rng = RandomNumberGenerator.new()
var CAM_FOV = 48.0
var CAM_Y = 10.0
var CAM_Z = -15.0
var LOOK_Z = 8.0


func vt() -> float:
	return Engine.get_process_frames() / 30.0


func _ready() -> void:
	rng.seed = 15
	var a = OS.get_cmdline_user_args()
	if a.size() > 0:
		sprite_dir = a[0]
	if a.size() > 4:
		CAM_FOV = float(a[1])
		CAM_Y = float(a[2])
		CAM_Z = float(a[3])
		LOOK_Z = float(a[4])
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
	_environment()
	_arena()
	_stands()
	var roster = [["firetruck", Vector3(-8, 0, 2.5), "HYDRO", Color(0.9, 0.15, 0.15)],
				  ["monster2", Vector3(-3, 0, 7.0), "GRIZZLY", Color(0.2, 0.75, 0.3)],
				  ["police", Vector3(3, 0, 2.0), "SIREN", Color(0.95, 0.95, 0.95)],
				  ["f1", Vector3(8, 0, 6.5), "NITRO", Color(0.2, 0.55, 1.0)]]
	for r in roster:
		cars.append(_car(r[0], r[1], r[2], r[3]))
	cam = Camera3D.new()
	cam.fov = CAM_FOV
	cam.position = Vector3(0, CAM_Y, CAM_Z)
	add_child(cam)
	cam.look_at(Vector3(0, 0, LOOK_Z), Vector3.UP)
	cam.make_current()
	_hud()


# ================================================================== world
func _environment() -> void:
	var env = Environment.new()
	var sky = Sky.new()
	var sm = ProceduralSkyMaterial.new()
	sm.sky_top_color = Color(0.3, 0.55, 0.95)
	sm.sky_horizon_color = Color(0.75, 0.85, 1.0)
	sm.ground_bottom_color = Color(0.3, 0.2, 0.15)
	sky.sky_material = sm
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	env.ambient_light_energy = 0.5
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.glow_enabled = true
	env.glow_intensity = 0.45
	env.glow_bloom = 0.15
	var we = WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, -35, 0)
	sun.light_energy = 1.1
	sun.light_color = Color(1.0, 0.95, 0.85)
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 60.0
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
	var floor_sh = Shader.new()                           # steel tiles
	floor_sh.code = """
shader_type spatial;
void fragment() {
	vec3 w = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec2 g = abs(fract(w.xz / 1.6) - 0.5);
	float line = step(0.47, max(g.x, g.y));
	ALBEDO = mix(vec3(0.27, 0.28, 0.31), vec3(0.17, 0.18, 0.2), line);
	ROUGHNESS = 0.8;
	METALLIC = 0.05;
}
"""
	var fm = ShaderMaterial.new()
	fm.shader = floor_sh
	_box(Vector3(ARENA_HX * 2, 1.0, ARENA_HZ * 2), Vector3(0, -0.5, ARENA_HZ), fm, true)
	var edge = _mat(Color(1, 0.82, 0.1))                   # yellow rim
	_box(Vector3(ARENA_HX * 2 + 0.3, 1.02, 0.3), Vector3(0, -0.49, 0), edge)
	_box(Vector3(ARENA_HX * 2 + 0.3, 1.02, 0.3), Vector3(0, -0.49, ARENA_HZ * 2), edge)
	_box(Vector3(0.3, 1.02, ARENA_HZ * 2), Vector3(-ARENA_HX, -0.49, ARENA_HZ), edge)
	_box(Vector3(0.3, 1.02, ARENA_HZ * 2), Vector3(ARENA_HX, -0.49, ARENA_HZ), edge)
	var lava_sh = Shader.new()                             # glowing, slowly moving lava
	lava_sh.code = """
shader_type spatial;
render_mode unshaded;
uniform float tm = 0.0;
float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float n(vec2 p) { vec2 i = floor(p); vec2 f = fract(p); f = f * f * (3.0 - 2.0 * f);
	return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
void fragment() {
	vec3 w = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec2 p = w.xz * 0.35 + vec2(TIME * 0.15, TIME * 0.07);
	float v = n(p) * 0.6 + n(p * 2.3 + 4.0) * 0.4;
	vec3 col = mix(vec3(0.85, 0.18, 0.02), vec3(1.0, 0.75, 0.15), smoothstep(0.45, 0.85, v));
	ALBEDO = col * 1.6;
}
"""
	var lm = ShaderMaterial.new()
	lm.shader = lava_sh
	var lava = MeshInstance3D.new()
	var pm = PlaneMesh.new()
	pm.size = Vector2(120, 80)
	lava.mesh = pm
	lava.material_override = lm
	lava.position = Vector3(0, -1.6, 10)
	add_child(lava)
	for x in [-14.0, 0.0, 14.0]:                           # warm glow from the lava onto the cars
		for z in [-1.5, 11.5]:
			var o = OmniLight3D.new()
			o.position = Vector3(x, -0.6, z)
			o.light_color = Color(1, 0.45, 0.1)
			o.light_energy = 1.6
			o.omni_range = 9.0
			add_child(o)


func _stands() -> void:
	var stand = _mat(Color(0.32, 0.34, 0.42))
	for row in range(6):
		_box(Vector3(46, 0.9, 1.6), Vector3(0, 0.45 + row * 0.9, 13.5 + row * 1.6), stand)
	var mm = MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	var sp = SphereMesh.new()
	sp.radius = 0.32
	sp.height = 0.64
	mm.mesh = sp
	mm.instance_count = 360
	for i in range(360):
		var row = i % 6
		var x = rng.randf_range(-22.0, 22.0)
		mm.set_instance_transform(i, Transform3D(Basis(), Vector3(x, 1.2 + row * 0.9, 13.4 + row * 1.6)))
		mm.set_instance_color(i, Color.from_hsv(rng.randf(), 0.55, 0.9))
	var mmi = MultiMeshInstance3D.new()
	mmi.multimesh = mm
	var cm = StandardMaterial3D.new()
	cm.vertex_color_use_as_albedo = true
	mmi.material_override = cm
	add_child(mmi)
	var banner = Label3D.new()
	banner.text = "SMASH ARENA"
	banner.font = font
	banner.font_size = 150
	banner.outline_size = 30
	banner.modulate = Color(1, 0.86, 0.12)
	banner.position = Vector3(0, 4.0, 13.0)
	banner.rotation_degrees = Vector3(0, 180, 0)
	banner.pixel_size = 0.012
	# banner removed: the HUD already shows the title (it overlapped the HP panel)


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
	var pm = PhysicsMaterial.new()
	pm.friction = 0.8
	pm.bounce = 0.25
	body.physics_material_override = pm
	var cs = CollisionShape3D.new()
	var bs = BoxShape3D.new()
	bs.size = Vector3(bw, bh + 2.0 * (ride - bh / 2.0), 1.7)
	cs.shape = bs
	cs.position = Vector3(0, -(ride - bh / 2.0), 0)
	body.add_child(cs)
	var tex = _tex(vk + "_body.png")
	var spr = Sprite3D.new()
	spr.texture = tex
	spr.pixel_size = 1.0 / 60.0
	spr.shaded = true
	spr.double_sided = true
	spr.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	spr.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	body.add_child(spr)
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
		body.add_child(w)
		wheels.append(w)
	add_child(body)
	var c = {"vk": vk, "nick": nick, "col": col, "body": body, "spr": spr, "wheels": wheels, "tex": tex,
			 "bw": bw, "bh": bh, "ride": ride, "hp": 100.0, "alive": true, "out": false,
			 "vmax": 8.0 if vk in ["f1", "sports", "police"] else 6.5, "last_hit": -9.0}
	body.body_entered.connect(func(other): call_deferred("_on_hit", c, other))
	return c


# ================================================================== FX
func _log(type: String, power: float) -> void:
	events.append({"t": vt(), "type": type, "power": power})
	FileAccess.open("/tmp/godot_events.json", FileAccess.WRITE).store_string(JSON.stringify({"events": events}))


func _particles(pos: Vector3, n: int, life: float, vel: Vector2, grav: Vector3, size: Vector2, c0: Color, c1: Color,
				spread := 180.0, unshaded := true) -> void:
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
	p.position = pos
	p.one_shot = true
	p.explosiveness = 0.9
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
	var cv = Curve.new()
	cv.add_point(Vector2(0, 0.5))
	cv.add_point(Vector2(0.25, 1.0))
	cv.add_point(Vector2(1, 0.3))
	p.scale_amount_curve = cv
	add_child(p)
	p.emitting = true
	get_tree().create_timer(life + 0.5, false).timeout.connect(p.queue_free)


func _flash(pos: Vector3, energy: float, rng_m: float, col: Color, fade: float) -> void:
	var o = OmniLight3D.new()
	o.position = pos
	o.light_color = col
	o.light_energy = energy
	o.omni_range = rng_m
	o.shadow_enabled = energy >= 6.0
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
	var m = _mat(col, col, 3.0)
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mi.material_override = m
	mi.position = pos + Vector3(0, 0.08, 0)
	mi.scale = Vector3(0.2, 0.05, 0.2)
	add_child(mi)
	var tw = create_tween().set_parallel(true)
	tw.tween_property(mi, "scale", Vector3(radius, 0.05, radius), dur)
	tw.tween_property(m, "albedo_color:a", 0.0, dur)
	tw.chain().tween_callback(mi.queue_free)


func explode(pos: Vector3, power: float, push := true) -> void:
	_log("explode", power)
	_flash(pos + Vector3(0, 1.5, 0), 9.0 * power, 14.0 * power, Color(1, 0.6, 0.25), 0.7)
	_particles(pos + Vector3(0, 0.8, 0), int(80 * power), 0.9, Vector2(4, 11) * power, Vector3(0, 2, 0),
			   Vector2(0.8, 2.2) * power, Color(1, 0.95, 0.6), Color(0.9, 0.15, 0.03, 0))           # fireball
	_particles(pos + Vector3(0, 1.0, 0), int(50 * power), 3.0, Vector2(1, 3.5), Vector3(0, 1.4, 0),
			   Vector2(1.4, 3.2) * power, Color(0.2, 0.18, 0.18, 0.85), Color(0.45, 0.45, 0.45, 0), 90.0, false)
	_particles(pos + Vector3(0, 0.5, 0), int(70 * power), 1.4, Vector2(8, 20) * power, Vector3(0, -14, 0),
			   Vector2(0.08, 0.18), Color(1, 0.9, 0.35), Color(1, 0.4, 0.1, 0))                       # sparks
	_ring(pos, 7.0 * power, Color(1, 0.85, 0.5, 0.9), 0.45)
	shake = max(shake, 0.55 * power)
	if push:
		for c in cars:
			if not c["alive"]:
				continue
			var d = c["body"].global_position - pos
			var dist = d.length()
			if dist < 7.0 * power:
				var f = (1.0 - dist / (7.0 * power))
				c["body"].apply_central_impulse((Vector3(d.x, 0, d.z).normalized() * 9.0 + Vector3(0, 8.0, 0))
												* f * c["body"].mass * power)
				c["body"].apply_torque_impulse(Vector3(0, 0, rng.randf_range(-1, 1) * 6.0 * c["body"].mass * f))
				_damage(c, 70.0 * f * power, "KABOOM!")
	if not slow_used:
		slow_used = true
		Engine.time_scale = 0.45
		slow_until = vt() + 0.6


func fracture(c: Dictionary) -> void:
	## the card breaks into 8 textured pieces flying in 3D
	_log("fracture", 1.0)
	var body = c["body"]
	var tex = c["tex"]
	var tsz = tex.get_size()
	var pos = body.global_position
	var bw_px = c["bw"] * 60.0
	var bh_px = c["bh"] * 60.0
	for iy in range(2):
		for ix in range(4):
			var piece = RigidBody3D.new()
			piece.mass = 60.0
			var pw = c["bw"] / 4.0
			var ph = c["bh"] / 2.0
			var cs = CollisionShape3D.new()
			var bs = BoxShape3D.new()
			bs.size = Vector3(pw, ph, 0.3)
			cs.shape = bs
			piece.add_child(cs)
			var s = Sprite3D.new()
			s.texture = tex
			s.region_enabled = true
			s.region_rect = Rect2(tsz.x / 2 - bw_px / 2 + ix * bw_px / 4, tsz.y / 2 - bh_px / 2 + iy * bh_px / 2,
								  bw_px / 4, bh_px / 2)
			s.pixel_size = 1.0 / 60.0
			s.shaded = true
			s.double_sided = true
			s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
			s.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
			piece.add_child(s)
			piece.position = pos + Vector3(-c["bw"] / 2 + pw * (ix + 0.5), c["bh"] / 2 - ph * (iy + 0.5), 0)
			add_child(piece)
			piece.linear_velocity = body.linear_velocity * 0.5 + Vector3(rng.randf_range(-6, 6), rng.randf_range(5, 11),
																		 rng.randf_range(-4, 4))
			piece.angular_velocity = Vector3(rng.randf_range(-8, 8), rng.randf_range(-8, 8), rng.randf_range(-8, 8))
	for w in c["wheels"]:                                   # wheels fly off and roll
		var wb = RigidBody3D.new()
		wb.mass = 40.0
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
		wb.linear_velocity = Vector3(rng.randf_range(-7, 7), rng.randf_range(4, 9), rng.randf_range(-3, 3))
		wb.angular_velocity = Vector3(0, 0, rng.randf_range(-15, 15))
	body.queue_free()


# ================================================================== battle
func _damage(c: Dictionary, amount: float, word: String) -> void:
	if not c["alive"]:
		return
	c["hp"] = max(0.0, c["hp"] - amount)
	_bubble(c["body"].global_position + Vector3(0, c["bh"] + 1.2, 0), word)
	if c["hp"] <= 0.0:
		c["alive"] = false
		var at = c["body"].global_position
		call_deferred("fracture", c)
		call_deferred("explode", at, 1.0, false)


func _on_hit(c: Dictionary, other) -> void:
	if not c["alive"] or vt() - c["last_hit"] < 0.4:
		return
	for o in cars:
		if o["body"] == other and o["alive"]:
			var rel = (c["body"].linear_velocity - o["body"].linear_velocity).length()
			if rel > 3.0:
				c["last_hit"] = vt()
				var dmg = rel * 3.2 * o["body"].mass / c["body"].mass
				_log("crash", clampf(rel / 14.0, 0.2, 1.0))
				var mid = (c["body"].global_position + o["body"].global_position) / 2.0
				_particles(mid + Vector3(0, 1.0, 0), 30, 0.5, Vector2(5, 12), Vector3(0, -12, 0), Vector2(0.06, 0.14),
						   Color(1, 1, 0.8), Color(1, 0.6, 0.1, 0))
				_flash(mid + Vector3(0, 1.2, 0), 2.5, 5.0, Color(1, 0.9, 0.7), 0.2)
				shake = max(shake, 0.18)
				_damage(c, dmg, ["BAM!", "WHAM!", "CRUNCH!", "BONK!"][rng.randi() % 4])


func _physics_process(delta: float) -> void:
	t += delta
	var go = clampf((t - 2.5) / 1.0, 0.0, 1.0)              # intro: 4 fighters... 1 survivor
	var alive = cars.filter(func(cc): return cc["alive"])
	for c in alive:
		var b = c["body"]
		if b.global_position.y < -0.8 and not c["out"]:      # into the lava
			c["out"] = true
			c["alive"] = false
			c["hp"] = 0.0
			_log("ringout", 1.0)
			_flash(b.global_position, 6.0, 10.0, Color(1, 0.5, 0.1), 1.2)
			_particles(b.global_position + Vector3(0, 0.5, 0), 120, 1.5, Vector2(5, 12), Vector3(0, -9, 0),
					   Vector2(0.25, 0.6), Color(1, 0.85, 0.25), Color(0.9, 0.15, 0.0, 0))
			_bubble(b.global_position + Vector3(0, 2.5, 0), "HOT HOT!")
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
		var want = to.normalized() * c["vmax"] * go
		var v = b.linear_velocity
		var dv = Vector3(want.x - v.x, 0, want.z - v.z)
		if b.global_position.y < c["ride"] + 0.4:            # only drive when the wheels are on the floor
			b.apply_central_force(dv * b.mass * 2.2)
		c["spr"].flip_h = v.x < -0.3 if abs(v.x) > 0.3 else c["spr"].flip_h
		for w in c["wheels"]:
			w.flip_h = c["spr"].flip_h
			w.rotation.z -= v.x * delta / 0.5
	if OS.get_cmdline_user_args().has("debug") and Engine.get_physics_frames() % 120 == 0:
		var line = "t=%.1f" % t
		for c in cars:
			if is_instance_valid(c["body"]):
				var bp = c["body"].global_position
				line += " | %s (%.1f,%.1f,%.1f) v=%.1f hp=%d" % [c["nick"], bp.x, bp.y, bp.z, c["body"].linear_velocity.length(), c["hp"]]
		print(line)
	for ch in chaos:
		if ch[0] > 0 and t >= ch[0] and alive.size() > 1:
			ch[0] = -1.0
			var tgt = alive[rng.randi() % alive.size()]
			var spot = tgt["body"].global_position
			spot.y = 0
			if ch[1] == "missile":
				_missile(spot)
			else:
				_kraggor(spot)
	if winner == null and alive.size() == 1 and t > 4.0:
		winner = alive[0]
		win_lbl.text = winner["nick"] + " WINS!"
		win_lbl.visible = true
		_log("win", 1.0)
		_particles(winner["body"].global_position + Vector3(0, 6, 0), 160, 3.0, Vector2(2, 7), Vector3(0, -4, 0),
				   Vector2(0.12, 0.25), Color(1, 0.9, 0.2), Color(0.3, 0.6, 1.0, 0.8))


func _missile(spot: Vector3) -> void:
	_log("missile", 1.0)
	_ring(spot, 2.2, Color(1, 0.15, 0.1, 0.9), 1.3)
	var m = MeshInstance3D.new()
	var cap = CapsuleMesh.new()
	cap.radius = 0.35
	cap.height = 2.2
	m.mesh = cap
	m.material_override = _mat(Color(0.75, 0.75, 0.8))
	m.position = spot + Vector3(2, 30, 6)
	add_child(m)
	var trail = CPUParticles3D.new()
	var q = QuadMesh.new()
	var qm = StandardMaterial3D.new()
	qm.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	qm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	qm.albedo_texture = dot_tex
	qm.vertex_color_use_as_albedo = true
	qm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	q.material = qm
	trail.mesh = q
	trail.amount = 60
	trail.lifetime = 0.5
	trail.direction = Vector3(0, 1, 0)
	trail.initial_velocity_min = 2
	trail.initial_velocity_max = 5
	trail.scale_amount_min = 0.5
	trail.scale_amount_max = 1.2
	var tg = Gradient.new()
	tg.set_color(0, Color(1, 0.9, 0.4))
	tg.set_color(1, Color(0.5, 0.5, 0.5, 0))
	trail.color_ramp = tg
	m.add_child(trail)
	var tw = create_tween()
	tw.tween_interval(0.6)
	tw.tween_property(m, "position", spot, 0.7).set_ease(Tween.EASE_IN)
	tw.tween_callback(func(): explode(spot, 1.4); m.queue_free())


func _kraggor(spot: Vector3) -> void:
	_log("kraggor", 1.0)
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
	_bubble(Vector3(0, 9, 8), "KRAGGOR ATTACK!")
	var tw = create_tween()
	tw.tween_interval(1.0)
	tw.tween_property(foot, "position", spot, 0.35).set_ease(Tween.EASE_IN)
	tw.tween_callback(func(): _stomp(spot))
	tw.tween_interval(1.2)
	tw.tween_property(foot, "position", spot + Vector3(0, 30, 0), 0.8).set_ease(Tween.EASE_IN)
	tw.tween_callback(foot.queue_free)


func _stomp(spot: Vector3) -> void:
	_log("stomp", 1.0)
	_ring(spot, 9.0, Color(0.85, 0.78, 0.6, 0.9), 0.6)
	_particles(spot + Vector3(0, 0.3, 0), 90, 1.8, Vector2(3, 8), Vector3(0, -2, 0), Vector2(0.8, 1.8),
			   Color(0.8, 0.72, 0.6, 0.8), Color(0.6, 0.55, 0.5, 0), 100.0, false)
	shake = max(shake, 0.8)
	for c in cars:
		if not c["alive"]:
			continue
		var d = c["body"].global_position - spot
		var dist = Vector2(d.x, d.z).length()
		if dist < 3.0:
			_damage(c, 100.0, "SPLAT!")
		elif dist < 8.0:
			var f = 1.0 - dist / 8.0
			c["body"].apply_central_impulse((Vector3(d.x, 0, d.z).normalized() * 7.0 + Vector3(0, 6.0, 0)) * f * c["body"].mass)
			_damage(c, 25.0 * f, "WHOA!")


# ================================================================== camera + HUD
func _process(_d: float) -> void:
	if slow_until > 0.0 and vt() > slow_until:
		Engine.time_scale = 1.0
		slow_until = -1.0
	var xs = []
	for c in cars:
		if c["alive"] and is_instance_valid(c["body"]):
			xs.append(c["body"].global_position.x)
	if xs.size() > 0:
		var cx = (xs.max() + xs.min()) / 2.0
		var spread = xs.max() - xs.min() + 8.0
		var dist = clampf(spread / 26.0, 0.75, 1.0)
		var want = Vector3(cx * 0.7, CAM_Y * dist, LOOK_Z + (CAM_Z - LOOK_Z) * dist)
		cam.position = cam.position.lerp(want, 0.04)
		cam.look_at(Vector3(cx * 0.7, 0, LOOK_Z), Vector3.UP)
	shake *= 0.86
	cam.h_offset = randf_range(-shake, shake)
	cam.v_offset = randf_range(-shake, shake)
	for i in range(cars.size()):
		var c = cars[i]
		var row = hp_rows[i]
		row["bar"].size.x = 150.0 * c["hp"] / 100.0
		row["bar"].color = Color(0.2, 0.85, 0.3) if c["hp"] > 60 else (Color(1, 0.8, 0.1) if c["hp"] > 30 else Color(0.95, 0.2, 0.15))
		row["out"].visible = not c["alive"]
	title_lbl.visible = true
	sub_lbl.modulate.a = clampf((3.2 - vt()) / 0.4, 0.0, 1.0)
	cta.visible = winner != null and vt() > winner_time() + 3.0


func winner_time() -> float:
	for e in events:
		if e["type"] == "win":
			return e["t"]
	return 1e9


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
		hp_rows.append({"bar": bar, "out": out})
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
	hud.add_child(cta)
	var cl = Label.new()
	cl.text = "MEGAWHEEL ARENA\nLIKE  •  SUBSCRIBE"
	cl.label_settings = _ls(62, Color(1, 1, 1))
	cl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	cl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	cl.size = Vector2(800, 330)
	cta.add_child(cl)


func _bubble(world: Vector3, text: String) -> void:
	if cam == null or cam.is_position_behind(world):
		return
	var p = cam.unproject_position(world)
	var l = Label.new()
	l.text = text
	var ls = _ls(54, Color(0.9, 0.15, 0.2))
	ls.outline_color = Color(1, 1, 1)
	ls.outline_size = 16
	l.label_settings = ls
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.size = Vector2(420, 80)
	l.position = p - Vector2(210, 40)
	l.pivot_offset = Vector2(210, 40)
	l.scale = Vector2(0.3, 0.3)
	hud.add_child(l)
	var tw = create_tween()
	tw.tween_property(l, "scale", Vector2.ONE, 0.18).set_trans(Tween.TRANS_BACK)
	tw.tween_interval(0.8)
	tw.tween_property(l, "modulate:a", 0.0, 0.3)
	tw.tween_callback(l.queue_free)
