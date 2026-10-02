extends Node2D
## MegaWheel Arena — Godot race prototype (comparison with the cairo race25d).
## 3 lanes (2.5D: deeper lanes higher + slightly darker), real rigid-body cars on wheels driving over potholes,
## a ramp and bumps; warm sunset light with shadows; parallax background; dust particles; question hook text.
## Car art = PNG sprites exported from our cairo cast (export_sprites.py) -> identical characters.

const PPM := 60.0                # pixels per metre (same as the sprites)
const LANES := 3
const LANE_DY := 95.0            # deeper lane = higher on screen
const BASE_Y := 1500.0
const TRACK_M := 230.0
const FINISH_M := 205.0
const HOOK := "CAN SPRINKLES SURVIVE THE POTHOLES?"

var cast := {}
var cars := []
var cam: Camera2D
var winner_label: Label
var winner := ""
var t := 0.0
var font: FontFile


func _ready() -> void:
	var f := FileAccess.open("res://sprites/cast.json", FileAccess.READ)
	cast = JSON.parse_string(f.get_as_text())["cars"]
	font = FontFile.new()
	font.load_dynamic_font("/root/.fonts/LuckiestGuy-Regular.ttf")
	_sky()
	_parallax()
	var mod := CanvasModulate.new()
	mod.color = Color(1.0, 0.92, 0.82)          # warm late-afternoon grade
	add_child(mod)
	for lane in range(LANES - 1, -1, -1):        # far lanes first
		_ground(lane)
	var roster := [["monster", 2, 1.18], ["sports", 1, 1.30], ["icecream", 0, 1.22]]
	for r in roster:
		cars.append(_car(r[0], r[1], r[2]))
	_sun()
	cam = Camera2D.new()
	cam.zoom = Vector2(0.58, 0.58)
	cam.position_smoothing_enabled = true
	cam.position_smoothing_speed = 2.5
	add_child(cam)
	cam.make_current()
	cam.position = Vector2(8 * PPM, BASE_Y - 260)
	_hud()


# ------------------------------------------------------------------ world
func _h(lane: int, xm: float) -> float:
	## ground height (pixels, y down) of a lane at x metres: potholes, a ramp, a bump field
	var y := BASE_Y - lane * LANE_DY
	var holes := {0: [38.0, 96.0, 150.0], 1: [64.0, 122.0], 2: [50.0, 135.0]}
	for hx in holes[lane]:
		var d: float = abs(xm - hx)
		if d < 1.6:
			y += 0.55 * PPM * cos(d / 1.6 * PI * 0.5)
	if lane == 1 and xm > 160.0 and xm < 170.0:  # kicker ramp
		y -= (xm - 160.0) / 10.0 * 1.6 * PPM
	if lane == 2 and xm > 80.0 and xm < 100.0:   # bump field
		y -= abs(sin((xm - 80.0) * 1.3)) * 0.22 * PPM
	return y


func _ground(lane: int) -> void:
	var pts := PackedVector2Array()
	var xm := -20.0
	while xm <= TRACK_M:
		pts.append(Vector2(xm * PPM, _h(lane, xm)))
		xm += 0.4
	var body := StaticBody2D.new()
	body.collision_layer = 1 << lane
	body.collision_mask = 0
	var poly := pts.duplicate()
	poly.append(Vector2(TRACK_M * PPM, BASE_Y + 900))
	poly.append(Vector2(-20 * PPM, BASE_Y + 900))
	var shape := CollisionPolygon2D.new()
	shape.polygon = poly
	body.add_child(shape)
	var mat := PhysicsMaterial.new()
	mat.friction = 1.0
	body.physics_material_override = mat
	add_child(body)
	# visuals: asphalt strip (lane top 0.95 lane-height deep), kerb on the near lane, dashes, finish
	var vis := PackedVector2Array(pts)
	for i in range(pts.size() - 1, -1, -1):
		vis.append(pts[i] + Vector2(0, LANE_DY))
	var asphalt := Polygon2D.new()
	asphalt.polygon = vis
	asphalt.color = Color(0.30, 0.30, 0.34).darkened(lane * 0.06)
	asphalt.z_index = -5 - lane * 3
	add_child(asphalt)
	var xd := 0.0
	while xd < TRACK_M:
		var dash := Line2D.new()
		dash.points = PackedVector2Array([Vector2(xd * PPM, _h(lane, xd) + LANE_DY * 0.55),
										  Vector2((xd + 1.6) * PPM, _h(lane, xd + 1.6) + LANE_DY * 0.55)])
		dash.width = 6
		dash.default_color = Color(1, 1, 1, 0.85)
		dash.z_index = asphalt.z_index + 1
		add_child(dash)
		xd += 4.0
	for row in range(4):                          # finish line checks
		for col in range(2):
			var q := Polygon2D.new()
			var x0 := (FINISH_M + col * 0.8) * PPM
			var y0 := _h(lane, FINISH_M) + row * LANE_DY / 4.0
			q.polygon = PackedVector2Array([Vector2(x0, y0), Vector2(x0 + 0.8 * PPM, y0),
											Vector2(x0 + 0.8 * PPM, y0 + LANE_DY / 4.0), Vector2(x0, y0 + LANE_DY / 4.0)])
			q.color = Color.BLACK if (row + col) % 2 == 0 else Color.WHITE
			q.z_index = asphalt.z_index + 1
			add_child(q)
	if lane == 0:                                 # dirt verge below the near lane
		var verge := Polygon2D.new()
		verge.polygon = PackedVector2Array([Vector2(-20 * PPM, BASE_Y + LANE_DY), Vector2(TRACK_M * PPM, BASE_Y + LANE_DY),
											Vector2(TRACK_M * PPM, BASE_Y + 1400), Vector2(-20 * PPM, BASE_Y + 1400)])
		verge.color = Color(0.45, 0.33, 0.22)
		verge.z_index = -2
		add_child(verge)


func _sky() -> void:
	var layer := CanvasLayer.new()
	layer.layer = -20
	add_child(layer)
	var g := Gradient.new()
	g.set_color(0, Color(0.28, 0.45, 0.85))
	g.set_color(1, Color(1.0, 0.72, 0.45))
	var tex := GradientTexture2D.new()
	tex.gradient = g
	tex.fill_from = Vector2(0, 0)
	tex.fill_to = Vector2(0, 1)
	tex.width = 8
	tex.height = 256
	var rect := TextureRect.new()
	rect.texture = tex
	rect.stretch_mode = TextureRect.STRETCH_SCALE
	rect.size = Vector2(1080, 1920)
	layer.add_child(rect)


func _ridge(color: Color, base: float, amp: float, step: float, seed_: int) -> Polygon2D:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_
	var pts := PackedVector2Array([Vector2(0, base + 2000)])
	var x := 0.0
	while x <= 6000.0:
		pts.append(Vector2(x, base - rng.randf_range(0.3, 1.0) * amp))
		x += step
	pts.append(Vector2(6000, base + 2000))
	var p := Polygon2D.new()
	p.polygon = pts
	p.color = color
	return p


func _parallax() -> void:
	var specs := [[0.08, Color(0.62, 0.66, 0.82), BASE_Y - 700, 520.0, 260.0, 3],   # far mountains (hazy)
				  [0.2, Color(0.45, 0.6, 0.55), BASE_Y - 420, 260.0, 180.0, 5],      # hills
				  [0.45, Color(0.33, 0.47, 0.36), BASE_Y - 240, 120.0, 90.0, 7]]      # tree line
	for s in specs:
		var px := Parallax2D.new()
		px.scroll_scale = Vector2(s[0], 1.0)
		px.repeat_size = Vector2(6000, 0)
		px.repeat_times = 3
		px.z_index = -60 + int(s[0] * 100)
		px.add_child(_ridge(s[1], s[2], s[3], s[4], s[5]))
		add_child(px)


func _tex(path: String) -> ImageTexture:
	var img := Image.load_from_file(ProjectSettings.globalize_path("res://sprites/" + path))
	return ImageTexture.create_from_image(img)


func _car(vk: String, lane: int, power: float) -> Dictionary:
	var m: Dictionary = cast[vk]
	var bw: float = m["body"][0]
	var bh: float = m["body"][1]
	var r: float = m["wheel_r"]
	var ride: float = m["ride"]
	var x0 := 3.0 * PPM
	var body := RigidBody2D.new()
	body.mass = 60.0
	body.collision_layer = 1 << (8 + lane)
	body.collision_mask = 1 << lane
	body.position = Vector2(x0, _h(lane, 3.0) - ride * PPM)
	var bs := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(bw * PPM, bh * PPM)
	bs.shape = rect
	body.add_child(bs)
	var spr := Sprite2D.new()
	spr.texture = _tex(vk + "_body.png")
	body.add_child(spr)
	var occ := LightOccluder2D.new()                      # casts a real shadow from the sun
	var op := OccluderPolygon2D.new()
	op.polygon = PackedVector2Array([Vector2(-bw * PPM / 2, -bh * PPM / 2), Vector2(bw * PPM / 2, -bh * PPM / 2),
									 Vector2(bw * PPM / 2, bh * PPM / 2), Vector2(-bw * PPM / 2, bh * PPM / 2)])
	occ.occluder = op
	body.add_child(occ)
	var dust := CPUParticles2D.new()                      # dust kicked up behind the rear wheel
	dust.position = Vector2(m["wheel_x"][0] * PPM, (ride - r) * PPM + r * PPM)
	dust.amount = 40
	dust.lifetime = 0.7
	dust.direction = Vector2(-1, -0.6)
	dust.spread = 25
	dust.initial_velocity_min = 120
	dust.initial_velocity_max = 260
	dust.gravity = Vector2(0, 300)
	dust.scale_amount_min = 6
	dust.scale_amount_max = 14
	dust.color = Color(0.82, 0.74, 0.6, 0.7)
	dust.emitting = false
	body.add_child(dust)
	add_child(body)
	var wheels := []
	for wx in m["wheel_x"]:
		var w := RigidBody2D.new()
		w.mass = 6.0
		w.collision_layer = 1 << (8 + lane)
		w.collision_mask = 1 << lane
		var wm := PhysicsMaterial.new()
		wm.friction = 1.4
		wm.rough = true
		w.physics_material_override = wm
		w.position = body.position + Vector2(wx * PPM, (ride - r) * PPM)
		var cs := CollisionShape2D.new()
		var circ := CircleShape2D.new()
		circ.radius = r * PPM
		cs.shape = circ
		w.add_child(cs)
		var ws := Sprite2D.new()
		ws.texture = _tex(vk + "_wheel.png")
		w.add_child(ws)
		add_child(w)
		var j := PinJoint2D.new()
		j.position = w.position
		j.node_a = body.get_path()
		j.node_b = w.get_path()
		j.softness = 0.4
		add_child(j)
		wheels.append(w)
	for n in [body] + wheels:
		n.z_index = 20 - lane * 6
		if lane > 0:
			n.modulate = Color(1, 1, 1).darkened(0.07 * lane)
	return {"vk": vk, "nick": m["nick"], "lane": lane, "power": power, "body": body, "wheels": wheels, "dust": dust}


func _sun() -> void:
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1))
	g.set_color(1, Color(1, 1, 1, 0))
	var tex := GradientTexture2D.new()
	tex.gradient = g
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	tex.width = 512
	tex.height = 512
	var sun := PointLight2D.new()
	sun.name = "Sun"
	sun.texture = tex
	sun.texture_scale = 14.0
	sun.energy = 0.55
	sun.color = Color(1.0, 0.8, 0.55)
	sun.shadow_enabled = true
	sun.shadow_color = Color(0.1, 0.05, 0.15, 0.45)
	sun.shadow_filter = PointLight2D.SHADOW_FILTER_PCF5
	add_child(sun)


func _hud() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 10
	add_child(layer)
	var ls := LabelSettings.new()
	ls.font = font
	ls.font_size = 86
	ls.font_color = Color(1, 0.86, 0.12)
	ls.outline_size = 22
	ls.outline_color = Color(0.07, 0.07, 0.2)
	var hook := Label.new()
	hook.name = "Hook"
	hook.text = HOOK
	hook.label_settings = ls
	hook.autowrap_mode = TextServer.AUTOWRAP_WORD
	hook.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hook.position = Vector2(40, 120)
	hook.size = Vector2(1000, 300)
	layer.add_child(hook)
	winner_label = Label.new()
	var ws := ls.duplicate()
	ws.font_size = 120
	winner_label.label_settings = ws
	winner_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	winner_label.position = Vector2(0, 640)
	winner_label.size = Vector2(1080, 200)
	winner_label.visible = false
	layer.add_child(winner_label)


# ------------------------------------------------------------------ simulation
func _physics_process(delta: float) -> void:
	t += delta
	var go := clampf((t - 0.8) / 1.2, 0.0, 1.0)            # start after a beat
	for c in cars:
		var body: RigidBody2D = c["body"]
		var on_ground := false
		for w in c["wheels"]:
			var wb: RigidBody2D = w
			if wb.angular_velocity < 32.0:
				wb.apply_torque(c["power"] * 26000.0 * go)
			if wb.get_contact_count() > 0 or true:
				on_ground = true
		c["dust"].emitting = go > 0.0 and body.linear_velocity.x > 200.0
		if winner == "" and body.position.x > FINISH_M * PPM:
			winner = c["nick"]
			winner_label.text = winner.to_upper() + " WINS!"
			winner_label.visible = true


func _process(_delta: float) -> void:
	var lead: RigidBody2D = cars[0]["body"]
	for c in cars:
		if c["body"].position.x > lead.position.x:
			lead = c["body"]
	var mid_y := BASE_Y - LANE_DY - 260.0
	cam.position = Vector2(lead.position.x + 2.5 * PPM, mid_y)
	var sun := get_node("Sun") as PointLight2D
	sun.position = cam.position + Vector2(-1400, -1500)       # sun upper-left, long shadows to the right
	var hook := get_node("CanvasLayer2/Hook") if has_node("CanvasLayer2/Hook") else null
	for n in get_children():
		if n is CanvasLayer and n.layer == 10:
			var h := n.get_node("Hook") as Label
			h.modulate.a = clampf((3.6 - t) / 0.5, 0.0, 1.0)
