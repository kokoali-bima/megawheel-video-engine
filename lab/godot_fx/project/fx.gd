extends Node2D
## LAB — Godot FX layer over the original cairo frames (method A): the video's format, camera, HUD and characters
## stay 100% identical; Godot adds light that really lights the picture, fireballs, smoke, sparks, shockwave
## distortion and cars breaking into textured pieces, at the exact screen spots captured from the engine.
##   godot --path project --write-movie out.avi --fixed-fps 30 --quit-after N -- <cue_dir> <sprite_dir>

var cue_dir = "/root/lab/fx/LAB"
var sprite_dir = ""
var cues = []
var frames = 0
var f = -1
var bg: TextureRect
var bg_tex: ImageTexture
var shake = 0.0
var light_tex: GradientTexture2D
var wave_mat: ShaderMaterial
var wave_rect: ColorRect


func _ready() -> void:
	var a = OS.get_cmdline_user_args()
	if a.size() > 0:
		cue_dir = a[0]
	if a.size() > 1:
		sprite_dir = a[1]
	var data = JSON.parse_string(FileAccess.open(cue_dir + "/cues.json", FileAccess.READ).get_as_text())
	cues = data["fx"]
	frames = int(data["frames"])
	bg = TextureRect.new()
	bg.size = Vector2(1080, 1920)
	bg.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(bg)
	var g = Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1))
	g.set_color(1, Color(1, 1, 1, 0))
	light_tex = GradientTexture2D.new()
	light_tex.gradient = g
	light_tex.fill = GradientTexture2D.FILL_RADIAL
	light_tex.fill_from = Vector2(0.5, 0.5)
	light_tex.fill_to = Vector2(1.0, 0.5)
	light_tex.width = 256
	light_tex.height = 256
	# screen-space shockwave distortion (reads the screen behind it)
	var sh = Shader.new()
	sh.code = """
shader_type canvas_item;
uniform sampler2D screen_tex : hint_screen_texture, filter_linear;
uniform vec2 center = vec2(0.5, 0.5);
uniform float radius = 0.0;
uniform float strength = 0.0;
void fragment() {
	vec2 uv = SCREEN_UV;
	vec2 d = uv - center;
	d.y *= 1920.0 / 1080.0;
	float dist = length(d);
	float ring = smoothstep(radius - 0.06, radius, dist) * (1.0 - smoothstep(radius, radius + 0.06, dist));
	vec2 off = normalize(d + 1e-5) * ring * strength;
	off.y /= 1920.0 / 1080.0;
	COLOR = texture(screen_tex, uv - off);
}
"""
	wave_mat = ShaderMaterial.new()
	wave_mat.shader = sh
	wave_rect = ColorRect.new()
	wave_rect.size = Vector2(1080, 1920)
	wave_rect.material = wave_mat
	wave_rect.z_index = 200
	add_child(wave_rect)


func _load_frame(i: int) -> void:
	var path = cue_dir + "/frames/%05d.png" % (i + 1)
	if not FileAccess.file_exists(path):
		return
	var img = Image.load_from_file(path)
	if bg_tex == null:
		bg_tex = ImageTexture.create_from_image(img)
		bg.texture = bg_tex
	else:
		bg_tex.update(img)


func _process(_d: float) -> void:
	f += 1
	_load_frame(f)
	for c in cues:
		if int(c["f"]) == f:
			_fx(c)
	shake *= 0.85
	bg.position = Vector2(randf_range(-shake, shake), randf_range(-shake, shake))


# ------------------------------------------------------------------ FX library
func _fx(c) -> void:
	var p = Vector2(c["x"], c["y"])
	var s = float(c["s"])                       # screen pixels per metre at that spot
	match c["type"]:
		"hit":
			var pw = float(c.get("power", 0.5))
			_light(p, s * 5.0, Color(1, 0.9, 0.6), 1.3 * pw + 0.4, 0.25)
			_parts(p, int(26 + 30 * pw), 0.5, Vector2(6, 16) * s, s * 18.0, Vector2(0.05, 0.12) * s,
				   Color(1, 1, 0.8), Color(1, 0.6, 0.1, 0))
			shake = max(shake, 6.0 + 8.0 * pw)
		"wreck":
			_explode(p, s, 1.0)
			_fracture(c, p, s)
		"ringout":                                   # falls into the lava: big lava burst + glow + small wave
			_light(p, s * 12.0, Color(1, 0.5, 0.12), 2.8, 1.2)
			_parts(p, 110, 1.4, Vector2(6, 16) * s, s * 14.0, Vector2(0.15, 0.4) * s,
				   Color(1, 0.85, 0.25), Color(0.9, 0.15, 0.0, 0))
			_parts(p + Vector2(0, -s), 30, 2.2, Vector2(1, 3) * s, -s * 1.5, Vector2(0.5, 1.1) * s,
				   Color(0.25, 0.2, 0.2, 0.7), Color(0.4, 0.4, 0.4, 0), 100.0)
			_ring(p, s * 7.0, Color(1, 0.6, 0.2, 0.8), 0.5, 16)
			shake = max(shake, 12.0)
		"missile":
			_explode(p, s, 1.6)
		"kraggor":
			_ring(p, s * 9.0, Color(0.85, 0.78, 0.6, 0.9), 0.6, 30)
			_parts(p, 70, 1.6, Vector2(2, 6) * s, s * 2.0, Vector2(0.4, 0.9) * s,
				   Color(0.8, 0.72, 0.6, 0.8), Color(0.6, 0.55, 0.5, 0), 140.0)
			shake = max(shake, 26.0)
		"crack":
			_light(p, s * 10.0, Color(1, 0.45, 0.1), 1.8, 1.4)
			_parts(p, 80, 1.3, Vector2(4, 11) * s, s * 12.0, Vector2(0.06, 0.16) * s,
				   Color(1, 0.85, 0.3), Color(1, 0.3, 0.0, 0))
		"ufo":
			_light(p + Vector2(0, -s * 4.0), s * 7.0, Color(0.6, 1.0, 0.7), 1.6, 2.0)


func _light(p: Vector2, size_px: float, col: Color, energy: float, fade: float) -> void:
	var l = PointLight2D.new()
	l.texture = light_tex
	l.texture_scale = size_px / 128.0
	l.color = col
	l.energy = energy
	l.position = p
	add_child(l)
	var tw = create_tween()
	tw.tween_property(l, "energy", 0.0, fade)
	tw.tween_callback(l.queue_free)


func _parts(p: Vector2, n: int, life: float, vel: Vector2, grav: float, size: Vector2, c0: Color, c1: Color,
			spread := 180.0) -> void:
	var e = CPUParticles2D.new()
	e.position = p
	e.one_shot = true
	e.explosiveness = 0.9
	e.amount = n
	e.lifetime = life
	e.spread = spread
	e.direction = Vector2(0, -1)
	e.initial_velocity_min = vel.x
	e.initial_velocity_max = vel.y
	e.gravity = Vector2(0, grav)
	e.scale_amount_min = size.x
	e.scale_amount_max = size.y
	var g = Gradient.new()
	g.set_color(0, c0)
	g.set_color(1, c1)
	e.color_ramp = g
	var cv = Curve.new()
	cv.add_point(Vector2(0, 0.7))
	cv.add_point(Vector2(0.25, 1.0))
	cv.add_point(Vector2(1, 0.25))
	e.scale_amount_curve = cv
	e.z_index = 50
	add_child(e)
	e.emitting = true
	get_tree().create_timer(life + 0.4).timeout.connect(e.queue_free)


func _ring(p: Vector2, r_px: float, col: Color, dur: float, width: float) -> void:
	var ring = Line2D.new()
	var pts = PackedVector2Array()
	for i in range(49):
		var a = TAU * i / 48.0
		pts.append(Vector2(cos(a), sin(a) * 0.42) * 10.0)          # flat ellipse: lies on the arena floor
	ring.points = pts
	ring.width = width / 10.0
	ring.default_color = col
	ring.position = p
	ring.z_index = 60
	add_child(ring)
	var tw = create_tween().set_parallel(true)
	tw.tween_property(ring, "scale", Vector2.ONE * r_px / 10.0, dur)
	tw.tween_property(ring, "modulate:a", 0.0, dur)
	tw.chain().tween_callback(ring.queue_free)


func _explode(p: Vector2, s: float, power: float) -> void:
	_light(p, s * 16.0 * power, Color(1.0, 0.62, 0.28), 3.0 * power, 0.7)
	_parts(p + Vector2(0, -s), int(70 * power), 0.9, Vector2(4, 13) * s * power, -s * 2.0,
		   Vector2(0.35, 0.8) * s * power, Color(1, 0.95, 0.6), Color(0.9, 0.15, 0.05, 0))          # fireball
	_parts(p + Vector2(0, -s), int(40 * power), 2.6, Vector2(1, 4) * s, -s * 1.2, Vector2(0.5, 1.3) * s * power,
		   Color(0.22, 0.2, 0.2, 0.85), Color(0.45, 0.45, 0.45, 0), 110.0)                          # smoke
	_parts(p + Vector2(0, -s), int(60 * power), 1.2, Vector2(8, 22) * s * power, s * 22.0,
		   Vector2(0.05, 0.12) * s, Color(1, 0.9, 0.35), Color(1, 0.4, 0.1, 0))                      # sparks
	_ring(p, s * 10.0 * power, Color(1, 0.95, 0.8, 0.85), 0.45, 18)
	wave_mat.set_shader_parameter("center", p / Vector2(1080, 1920))
	wave_mat.set_shader_parameter("strength", 0.03 * power)
	var tw = create_tween()
	tw.tween_method(func(r): wave_mat.set_shader_parameter("radius", r), 0.0, 0.45 * power, 0.5)
	tw.tween_callback(func(): wave_mat.set_shader_parameter("strength", 0.0))
	shake = max(shake, 22.0 * power)


func _fracture(c, p: Vector2, s: float) -> void:
	## the car breaks into textured pieces that bounce on the arena floor (screen-space physics)
	var key = str(c.get("key", ""))
	var path = sprite_dir + "/" + key + "_body.png"
	if key == "" or not FileAccess.file_exists(path):
		return
	var tex = ImageTexture.create_from_image(Image.load_from_file(path))
	var meta = JSON.parse_string(FileAccess.open(sprite_dir + "/cast.json", FileAccess.READ).get_as_text())["cars"][key]
	var sc = s / 60.0                                   # sprites are 60 px per metre
	var bw = float(meta["body"][0]) * 60.0
	var bh = float(meta["body"][1]) * 60.0
	var tsz = tex.get_size()
	var centre_y = p.y - (float(meta["ride"])) * s
	var floor_body = StaticBody2D.new()                 # the arena floor line under the car
	var fl = CollisionShape2D.new()
	var seg = SegmentShape2D.new()
	seg.a = Vector2(-2000, p.y)
	seg.b = Vector2(3000, p.y)
	fl.shape = seg
	floor_body.add_child(fl)
	add_child(floor_body)
	get_tree().create_timer(3.2).timeout.connect(floor_body.queue_free)
	var rng = RandomNumberGenerator.new()
	rng.seed = int(p.x * 13 + p.y)
	var nx = 4
	var ny = 2
	for iy in range(ny):
		for ix in range(nx):
			var x0 = -bw / 2 + bw * ix / nx
			var x1 = -bw / 2 + bw * (ix + 1) / nx
			var y0 = -bh / 2 + bh * iy / ny
			var y1 = -bh / 2 + bh * (iy + 1) / ny
			var quad = PackedVector2Array([Vector2(x0, y0), Vector2(x1, y0), Vector2(x1, y1), Vector2(x0, y1)])
			var cen = Vector2((x0 + x1) / 2, (y0 + y1) / 2)
			var local = PackedVector2Array()
			var uv = PackedVector2Array()
			for q in quad:
				local.append((q - cen) * sc)
				var u = q + tsz / 2.0
				if c.get("flip", false):
					u.x = tsz.x - u.x
				uv.append(u)
			var b = RigidBody2D.new()
			b.mass = 4.0
			b.gravity_scale = s * 9.8 / 980.0
			b.continuous_cd = RigidBody2D.CCD_MODE_CAST_SHAPE
			var col = CollisionPolygon2D.new()
			col.polygon = local
			b.add_child(col)
			var poly = Polygon2D.new()
			poly.texture = tex
			poly.polygon = local
			poly.uv = uv
			b.add_child(poly)
			b.position = Vector2(p.x + cen.x * sc * (-1.0 if c.get("flip", false) else 1.0), centre_y + cen.y * sc)
			b.z_index = 40
			add_child(b)
			b.linear_velocity = Vector2(rng.randf_range(-8, 8) * s, rng.randf_range(-14, -6) * s)
			b.angular_velocity = rng.randf_range(-10, 10)
			var tw = create_tween()
			tw.tween_interval(2.2)
			tw.tween_property(b, "modulate:a", 0.0, 0.8)
			tw.tween_callback(b.queue_free)
