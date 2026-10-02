extends Node2D
## MegaWheel Arena — Godot showcase prototypes (what the cairo engines can't do well):
##   godot ... -- challenge | race | smash
## Real rigid-body cars (sprites = our cairo cast), crash detection from velocity spikes -> cars FRACTURE into
## textured pieces, wheels fly off, explosions (light flash, fireball, smoke, sparks, shockwave, blast impulse),
## camera shake + slow motion on big hits. Events -> /tmp/godot_events.json (time, type, power) for the SFX mix.

const PPM := 60.0
const BASE_Y := 1500.0
const LANE_DY := 110.0
var MODE := "race"
var cast := {}
var cars := []
var cam: Camera2D
var font: FontFile
var hook_label: Label
var winner_label: Label
var winner := ""
var shake := 0.0
var slow_until := -1.0
var events := []
var sim_t := 0.0
var meteors_next := 3.0
var hammer_pivot: Node2D
var hammer_body: AnimatableBody2D
var container_done := false


func vt() -> float:                                  # video time (Movie Maker: one process frame = 1/30 s)
	return Engine.get_process_frames() / 30.0


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		MODE = args[0]
	cast = JSON.parse_string(FileAccess.open("res://sprites/cast.json", FileAccess.READ).get_as_text())["cars"]
	font = FontFile.new()
	font.load_dynamic_font("/root/.fonts/LuckiestGuy-Regular.ttf")
	_sky()
	_parallax()
	var mod := CanvasModulate.new()
	mod.color = Color(1.0, 0.94, 0.86)
	add_child(mod)
	cam = Camera2D.new()
	cam.position_smoothing_enabled = true
	cam.position_smoothing_speed = 4.0
	add_child(cam)
	cam.make_current()
	_hud()
	match MODE:
		"challenge":
			_setup_challenge()
		"smash":
			_setup_smash()
		_:
			_setup_race()


# ================================================================== shared world
func _sky() -> void:
	var layer := CanvasLayer.new()
	layer.layer = -20
	add_child(layer)
	var g := Gradient.new()
	g.set_color(0, Color(0.25, 0.42, 0.85))
	g.set_color(1, Color(1.0, 0.7, 0.42))
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


func _parallax() -> void:
	var specs := [[0.08, Color(0.66, 0.68, 0.84), BASE_Y - 760, 520.0, 300.0, 3],
				  [0.2, Color(0.47, 0.62, 0.56), BASE_Y - 470, 260.0, 160.0, 5],
				  [0.45, Color(0.33, 0.47, 0.36), BASE_Y - 300, 120.0, 70.0, 7]]
	for s in specs:
		var px := Parallax2D.new()
		px.scroll_scale = Vector2(s[0], 1.0)
		px.repeat_size = Vector2(6000, 0)
		px.repeat_times = 3
		px.z_index = -60 + int(s[0] * 100)
		var rng := RandomNumberGenerator.new()
		rng.seed = s[5]
		var pts := PackedVector2Array([Vector2(0, s[2] + 2500)])
		var x := 0.0
		while x <= 6000.0:
			pts.append(Vector2(x, s[2] - rng.randf_range(0.35, 1.0) * s[3]))
			x += s[4]
		pts.append(Vector2(6000, s[2] + 2500))
		var p := Polygon2D.new()
		p.polygon = pts
		p.color = s[1]
		px.add_child(p)
		add_child(px)


func _ground_poly(pts: PackedVector2Array, layer_bit: int, color: Color, z: int) -> void:
	var body := StaticBody2D.new()
	body.collision_layer = layer_bit
	body.collision_mask = 0
	var poly := pts.duplicate()
	poly.append(Vector2(pts[pts.size() - 1].x, BASE_Y + 1600))
	poly.append(Vector2(pts[0].x, BASE_Y + 1600))
	var cs := CollisionPolygon2D.new()
	cs.polygon = poly
	body.add_child(cs)
	var mat := PhysicsMaterial.new()
	mat.friction = 1.0
	body.physics_material_override = mat
	add_child(body)
	var vis := Polygon2D.new()
	vis.polygon = poly
	vis.color = color
	vis.z_index = z
	add_child(vis)
	var top := Line2D.new()                         # lit road edge
	top.points = pts
	top.width = 10
	top.default_color = color.lightened(0.25)
	top.z_index = z + 1
	add_child(top)


func _tex(name: String) -> ImageTexture:
	return ImageTexture.create_from_image(Image.load_from_file(ProjectSettings.globalize_path("res://sprites/" + name)))


func _car(vk: String, pos: Vector2, layer_bit: int, mask: int, power: float, z: int, dir := 1) -> Dictionary:
	var m: Dictionary = cast[vk]
	var bw: float = m["body"][0]
	var bh: float = m["body"][1]
	var r: float = m["wheel_r"]
	var ride: float = m["ride"]
	var body := RigidBody2D.new()
	body.mass = 60.0 + bw * 8.0
	body.collision_layer = layer_bit
	body.collision_mask = mask
	body.position = pos + Vector2(0, -ride * PPM)
	body.contact_monitor = true
	body.max_contacts_reported = 6
	var cs := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(bw * PPM, bh * PPM)
	cs.shape = rect
	body.add_child(cs)
	var tex := _tex(vk + "_body.png")
	var spr := Sprite2D.new()
	spr.texture = tex
	if dir < 0:
		spr.flip_h = true
	body.add_child(spr)
	add_child(body)
	var wheels := []
	var joints := []
	for wx in m["wheel_x"]:
		var w := RigidBody2D.new()
		w.mass = 8.0
		w.collision_layer = layer_bit
		w.collision_mask = mask
		var wm := PhysicsMaterial.new()
		wm.friction = 1.6
		wm.rough = true
		w.physics_material_override = wm
		w.position = body.position + Vector2(wx * PPM * dir, (ride - r) * PPM)
		var wc := CollisionShape2D.new()
		var circ := CircleShape2D.new()
		circ.radius = r * PPM
		wc.shape = circ
		w.add_child(wc)
		var ws := Sprite2D.new()
		ws.texture = _tex(vk + "_wheel.png")
		w.add_child(ws)
		add_child(w)
		var j := PinJoint2D.new()
		j.position = w.position
		j.node_a = body.get_path()
		j.node_b = w.get_path()
		j.softness = 0.3
		add_child(j)
		wheels.append(w)
		joints.append(j)
	for n in [body] + wheels:
		n.z_index = z
	return {"vk": vk, "nick": m["nick"], "body": body, "wheels": wheels, "joints": joints, "tex": tex,
			"size": Vector2(bw * PPM, bh * PPM), "power": power, "dir": dir, "alive": true, "hp": 1.0,
			"prev_v": Vector2.ZERO, "layer": layer_bit, "mask": mask, "z": z, "flip": dir < 0}


# ================================================================== FX
func _log(type: String, power: float) -> void:
	events.append({"t": vt(), "type": type, "power": power})
	var f := FileAccess.open("/tmp/godot_events.json", FileAccess.WRITE)
	f.store_string(JSON.stringify({"mode": MODE, "events": events}))


func _particles(pos: Vector2, amount: int, life: float, vel: Vector2, grav: Vector2, size: Vector2,
				c0: Color, c1: Color, spread := 180.0, z := 60) -> void:
	var p := CPUParticles2D.new()
	p.position = pos
	p.one_shot = true
	p.explosiveness = 0.92
	p.amount = amount
	p.lifetime = life
	p.spread = spread
	p.direction = Vector2(0, -1)
	p.initial_velocity_min = vel.x
	p.initial_velocity_max = vel.y
	p.gravity = grav
	p.scale_amount_min = size.x
	p.scale_amount_max = size.y
	var g := Gradient.new()
	g.set_color(0, c0)
	g.set_color(1, c1)
	p.color_ramp = g
	var curve := Curve.new()
	curve.add_point(Vector2(0, 0.6))
	curve.add_point(Vector2(0.3, 1.0))
	curve.add_point(Vector2(1, 0.2))
	p.scale_amount_curve = curve
	p.z_index = z
	add_child(p)
	p.emitting = true
	get_tree().create_timer(life + 0.5, false).timeout.connect(p.queue_free)


func explode(pos: Vector2, power: float) -> void:
	_log("explode", power)
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1))
	g.set_color(1, Color(1, 1, 1, 0))
	var lt := GradientTexture2D.new()
	lt.gradient = g
	lt.fill = GradientTexture2D.FILL_RADIAL
	lt.fill_from = Vector2(0.5, 0.5)
	lt.fill_to = Vector2(1.0, 0.5)
	lt.width = 256
	lt.height = 256
	var flash := PointLight2D.new()                  # the blast lights up everything around it
	flash.texture = lt
	flash.texture_scale = 9.0 * power
	flash.color = Color(1.0, 0.65, 0.3)
	flash.energy = 3.2
	flash.position = pos
	add_child(flash)
	var tw := create_tween()
	tw.tween_property(flash, "energy", 0.0, 0.6)
	tw.tween_callback(flash.queue_free)
	_particles(pos, int(70 * power), 0.9, Vector2(250, 750) * power, Vector2(0, -120),
			   Vector2(18, 42) * power, Color(1, 0.95, 0.6), Color(0.9, 0.15, 0.05, 0.0))          # fireball
	_particles(pos, int(45 * power), 2.6, Vector2(60, 260), Vector2(0, -60), Vector2(30, 70) * power,
			   Color(0.25, 0.22, 0.22, 0.85), Color(0.5, 0.5, 0.5, 0.0), 120.0, 55)               # smoke
	_particles(pos, int(60 * power), 1.2, Vector2(400, 1100) * power, Vector2(0, 1300), Vector2(3, 7),
			   Color(1, 0.9, 0.3), Color(1, 0.4, 0.1, 0.0))                                      # sparks
	var ring := Line2D.new()                         # shockwave ring
	var pts := PackedVector2Array()
	for i in range(41):
		pts.append(Vector2.RIGHT.rotated(TAU * i / 40.0) * 10.0)
	ring.points = pts
	ring.width = 14
	ring.default_color = Color(1, 0.95, 0.8, 0.9)
	ring.position = pos
	ring.z_index = 70
	add_child(ring)
	var tr := create_tween().set_parallel(true)
	tr.tween_property(ring, "scale", Vector2.ONE * 28.0 * power, 0.45)
	tr.tween_property(ring, "modulate:a", 0.0, 0.45)
	tr.chain().tween_callback(ring.queue_free)
	for n in get_children():                         # blast impulse on every body nearby
		if n is RigidBody2D:
			var d: Vector2 = n.global_position - pos
			var dist := d.length()
			if dist < 520.0 * power and dist > 1.0:
				n.apply_central_impulse(d.normalized() * (1.0 - dist / (520.0 * power)) * 9000.0 * power
										+ Vector2(0, -4000.0 * power))
	shake = max(shake, 38.0 * power)
	slow_mo(0.9)


func slow_mo(dur: float) -> void:
	Engine.time_scale = 0.3
	slow_until = vt() + dur


func fracture(c: Dictionary, impact: Vector2) -> void:
	## the car breaks into textured pieces (jittered 4x2 grid of the sprite), wheels come off
	if not c["alive"]:
		return
	c["alive"] = false
	_log("fracture", 1.0)
	var body: RigidBody2D = c["body"]
	var sz: Vector2 = c["size"]
	var tex: Texture2D = c["tex"]
	var tsz := tex.get_size()
	var rng := RandomNumberGenerator.new()
	rng.seed = int(body.position.x)
	var nx := 4
	var ny := 2
	var grid := []
	for iy in range(ny + 1):
		var row := []
		for ix in range(nx + 1):
			var p := Vector2(-sz.x / 2 + sz.x * ix / nx, -sz.y / 2 + sz.y * iy / ny)
			if ix > 0 and ix < nx:
				p.x += rng.randf_range(-0.25, 0.25) * sz.x / nx
			if iy > 0 and iy < ny:
				p.y += rng.randf_range(-0.25, 0.25) * sz.y / ny
			row.append(p)
		grid.append(row)
	for iy in range(ny):
		for ix in range(nx):
			var quad := PackedVector2Array([grid[iy][ix], grid[iy][ix + 1], grid[iy + 1][ix + 1], grid[iy + 1][ix]])
			var centre := (quad[0] + quad[1] + quad[2] + quad[3]) / 4.0
			var local := PackedVector2Array()
			var uv := PackedVector2Array()
			for q in quad:
				local.append(q - centre)
				var u := q + tsz / 2.0
				if c["flip"]:
					u.x = tsz.x - u.x
				uv.append(u)
			var frag := RigidBody2D.new()
			frag.mass = 10.0
			frag.collision_layer = c["layer"]
			frag.collision_mask = c["mask"] & 0xFF
			frag.global_transform = body.global_transform * Transform2D(0, centre)
			var col := CollisionPolygon2D.new()
			col.polygon = local
			frag.add_child(col)
			var pv := Polygon2D.new()
			pv.texture = tex
			pv.polygon = local
			pv.uv = uv
			frag.add_child(pv)
			frag.z_index = c["z"] + 2
			add_child(frag)
			var out := (frag.global_position - impact).normalized()
			frag.linear_velocity = body.linear_velocity * 0.6 + out * rng.randf_range(350, 900) + Vector2(0, -500)
			frag.angular_velocity = rng.randf_range(-12, 12)
	for j in c["joints"]:
		j.queue_free()
	for w in c["wheels"]:
		w.apply_central_impulse(Vector2(rng.randf_range(-1500, 1500), -2500))
	_particles(body.global_position, 40, 1.0, Vector2(300, 800), Vector2(0, 1400), Vector2(4, 9),
			   Color(0.85, 0.95, 1.0), Color(0.6, 0.8, 1.0, 0.0))                                 # glass shards
	body.queue_free()


func _crash_check(c: Dictionary, threshold: float) -> void:
	## a sudden velocity change (hammer, container, meteor, wall, landing in a pit) = damage
	if not c["alive"]:
		return
	var body: RigidBody2D = c["body"]
	var v := body.linear_velocity
	var dv := (v - c["prev_v"]).length()
	c["prev_v"] = v
	if dv > threshold:
		c["hp"] -= (dv - threshold) / 900.0
		_log("crash", clampf(dv / 2500.0, 0.2, 1.0))
		shake = max(shake, clampf(dv / 80.0, 6.0, 30.0))
		if c["hp"] <= 0.0:
			var at := body.global_position
			fracture(c, at + Vector2(0, 30))
			explode(at, 1.0)


func _drive(c: Dictionary, go: float, cap: float) -> void:
	if not c["alive"]:
		return
	for w in c["wheels"]:
		var wb: RigidBody2D = w
		if abs(wb.angular_velocity) < cap:
			wb.apply_torque(c["power"] * 52000.0 * go * c["dir"])


# ================================================================== CHALLENGE: giant pits
func _setup_challenge() -> void:
	hook_label.text = "CAN THEY CROSS THE GIANT PITS?"
	var pts := PackedVector2Array()
	var xm := -30.0
	while xm <= 260.0:
		var y := BASE_Y
		for pit in [[60.0, 7.0, 3.2], [130.0, 9.0, 4.5]]:       # x, width, depth (m) - steep walls
			if xm > pit[0] and xm < pit[0] + pit[1]:
				y += pit[2] * PPM
		if xm > 52.0 and xm < 60.0:                              # take-off ramp before pit 1
			y -= (xm - 52.0) / 8.0 * 1.1 * PPM
		if xm > 122.0 and xm < 130.0:
			y -= (xm - 122.0) / 8.0 * 1.4 * PPM
		pts.append(Vector2(xm * PPM, y))
		xm += 0.25
	_ground_poly(pts, 1, Color(0.42, 0.34, 0.26), -5)
	var roster := [["sports", 1.55, 0.0], ["icecream", 1.0, 2.2], ["monster", 1.25, 4.4]]
	for r in roster:
		var c := _car(r[0], Vector2(4.0 * PPM, BASE_Y), 2, 1 | 2, r[1], 20)
		c["start"] = r[2]
		cars.append(c)
	cam.zoom = Vector2(0.7, 0.7)


# ================================================================== RACE: 3 lanes, hammer + container
func _lane_y(lane: int) -> float:
	return BASE_Y - lane * LANE_DY


func _setup_race() -> void:
	hook_label.text = "CAN SPRINKLES SURVIVE THE GIANT HAMMER?"
	for lane in range(2, -1, -1):
		var pts := PackedVector2Array()
		var xm := -30.0
		while xm <= 330.0:
			var y := _lane_y(lane)
			if lane == 1 and abs(xm - 120.0) < 1.8:              # pothole
				y += 0.6 * PPM * cos(abs(xm - 120.0) / 1.8 * PI * 0.5)
			pts.append(Vector2(xm * PPM, y))
			xm += 0.5
		_ground_poly(pts, 1 << lane, Color(0.3, 0.3, 0.34).darkened(lane * 0.07), -10 - lane * 4)
	var roster := [["monster", 2, 1.15], ["sports", 1, 1.35], ["icecream", 0, 1.2]]
	for r in roster:
		cars.append(_car(r[0], Vector2(4.0 * PPM, _lane_y(r[1])), 1 << (8 + r[1]), 1 << r[1], r[2], 30 - r[1] * 8))
	# giant hammer over lane 0 at x = 150 m: kinematic pendulum (pushes the car like a real mass)
	hammer_pivot = Node2D.new()
	hammer_pivot.position = Vector2(150.0 * PPM, _lane_y(0) - 8.6 * PPM)
	add_child(hammer_pivot)
	hammer_body = AnimatableBody2D.new()
	hammer_body.position = Vector2(0, 7.2 * PPM)
	hammer_body.collision_layer = 1 << 0
	hammer_body.collision_mask = 1 << 8
	var hs := CollisionShape2D.new()
	var hr := RectangleShape2D.new()
	hr.size = Vector2(4.4 * PPM, 2.0 * PPM)
	hs.shape = hr
	hammer_body.add_child(hs)
	var head := Polygon2D.new()
	head.polygon = PackedVector2Array([Vector2(-2.2, -1), Vector2(2.2, -1), Vector2(2.2, 1), Vector2(-2.2, 1)]) * Transform2D.IDENTITY.scaled(Vector2(PPM, PPM))
	head.color = Color(0.58, 0.6, 0.66)
	hammer_body.add_child(head)
	for sx in [-2.2, 1.85]:
		var band := Polygon2D.new()
		band.polygon = PackedVector2Array([Vector2(sx, -1), Vector2(sx + 0.35, -1), Vector2(sx + 0.35, 1), Vector2(sx, 1)]) * Transform2D.IDENTITY.scaled(Vector2(PPM, PPM))
		band.color = Color(0.85, 0.1, 0.1)
		hammer_body.add_child(band)
	var arm := Line2D.new()
	arm.points = PackedVector2Array([Vector2.ZERO, Vector2(0, 6.4 * PPM)])
	arm.width = 26
	arm.default_color = Color(0.55, 0.38, 0.2)
	hammer_pivot.add_child(arm)
	hammer_pivot.add_child(hammer_body)
	hammer_pivot.z_index = 40
	cam.zoom = Vector2(0.62, 0.62)


func _race_physics(go: float) -> void:
	# hammer: idles, then slams down when the lane-0 car is close
	var ice: Dictionary = cars[2]
	var target_ang := 1.1 * sin(sim_t * 1.6)
	if ice["alive"]:
		var dx: float = hammer_pivot.position.x - ice["body"].position.x
		if dx < 9.0 * PPM and dx > -2.0 * PPM:
			target_ang = -0.15 + clampf(dx / (9.0 * PPM), 0.0, 1.0) * 1.2
	hammer_pivot.rotation = lerp_angle(hammer_pivot.rotation, target_ang, 0.25)
	# container drops on lane 1 in front of the sports car
	var sp: Dictionary = cars[1]
	if not container_done and sp["alive"] and sp["body"].position.x > 200.0 * PPM:
		container_done = true
		var box := RigidBody2D.new()
		box.mass = 900.0
		box.collision_layer = 1 << 1
		box.collision_mask = (1 << 1) | (1 << 9)
		box.position = Vector2(sp["body"].position.x + 12.0 * PPM, _lane_y(1) - 22.0 * PPM)
		var bs := CollisionShape2D.new()
		var br := RectangleShape2D.new()
		br.size = Vector2(6.0 * PPM, 2.6 * PPM)
		bs.shape = br
		box.add_child(bs)
		var bp := Polygon2D.new()
		bp.polygon = PackedVector2Array([Vector2(-3, -1.3), Vector2(3, -1.3), Vector2(3, 1.3), Vector2(-3, 1.3)]) * Transform2D.IDENTITY.scaled(Vector2(PPM, PPM))
		bp.color = Color(0.92, 0.45, 0.1)
		box.add_child(bp)
		box.z_index = 25
		add_child(box)
		_log("container", 1.0)


# ================================================================== SMASH: arena, collisions, meteors
func _setup_smash() -> void:
	hook_label.text = "4 CARS, 1 ARENA... WHO SURVIVES?"
	var pts := PackedVector2Array()
	for xm in [-14.0, -12.0, 12.0, 14.0]:
		pass
	pts = PackedVector2Array([Vector2(-16 * PPM, BASE_Y - 6 * PPM), Vector2(-14 * PPM, BASE_Y), Vector2(14 * PPM, BASE_Y),
							  Vector2(16 * PPM, BASE_Y - 6 * PPM)])
	_ground_poly(pts, 1, Color(0.36, 0.3, 0.28), -5)
	var roster := [["sports", -9.0, 1.3, 1], ["police", -3.0, 1.2, 1], ["taxi", 3.0, 1.2, -1], ["monster", 9.0, 1.25, -1]]
	for r in roster:
		var c := _car(r[0], Vector2(r[1] * PPM, BASE_Y), 2, 1 | 2, r[2], 20, r[3])
		cars.append(c)
	cam.zoom = Vector2(0.62, 0.62)
	cam.position = Vector2(0, BASE_Y - 600)


func _smash_physics(go: float) -> void:
	for c in cars:                                    # bounce off the arena walls: reverse direction
		if not c["alive"]:
			continue
		var x: float = c["body"].position.x
		if (x > 11.0 * PPM and c["dir"] > 0) or (x < -11.0 * PPM and c["dir"] < 0):
			c["dir"] = -c["dir"]
	if sim_t > meteors_next:
		meteors_next = sim_t + 2.6
		var rng := RandomNumberGenerator.new()
		rng.seed = int(sim_t * 100)
		var alive := cars.filter(func(cc): return cc["alive"])
		if alive.size() > 1:
			var tgt: Dictionary = alive[rng.randi_range(0, alive.size() - 1)]
			var m := RigidBody2D.new()
			m.mass = 200.0
			m.collision_layer = 4
			m.collision_mask = 1 | 2
			m.contact_monitor = true
			m.max_contacts_reported = 2
			m.position = Vector2(tgt["body"].position.x + rng.randf_range(-60, 60), BASE_Y - 26.0 * PPM)
			m.linear_velocity = Vector2(rng.randf_range(-200, 200), 1400)
			var ms := CollisionShape2D.new()
			var mc := CircleShape2D.new()
			mc.radius = 0.9 * PPM
			ms.shape = mc
			m.add_child(ms)
			var rock := Polygon2D.new()
			var rp := PackedVector2Array()
			for i in range(10):
				rp.append(Vector2.RIGHT.rotated(TAU * i / 10.0) * PPM * rng.randf_range(0.8, 1.05))
			rock.polygon = rp
			rock.color = Color(0.45, 0.25, 0.15)
			m.add_child(rock)
			var trail := CPUParticles2D.new()           # fire trail
			trail.amount = 50
			trail.lifetime = 0.5
			trail.direction = Vector2(0, -1)
			trail.initial_velocity_min = 80
			trail.initial_velocity_max = 200
			trail.scale_amount_min = 14
			trail.scale_amount_max = 30
			var tg := Gradient.new()
			tg.set_color(0, Color(1, 0.85, 0.3))
			tg.set_color(1, Color(0.9, 0.2, 0.05, 0))
			trail.color_ramp = tg
			m.add_child(trail)
			m.z_index = 45
			m.body_entered.connect(func(_b): _meteor_hit(m))
			add_child(m)
			_log("meteor", 1.0)


func _meteor_hit(m: RigidBody2D) -> void:
	if not is_instance_valid(m) or m.is_queued_for_deletion():
		return
	var at := m.global_position
	m.queue_free()
	explode(at, 1.3)
	for c in cars:
		if c["alive"] and c["body"].global_position.distance_to(at) < 3.2 * PPM:
			fracture(c, at)


# ================================================================== loop
func _physics_process(delta: float) -> void:
	sim_t += delta
	var go := clampf((sim_t - 0.6) / 1.0, 0.0, 1.0)
	for c in cars:
		var cap := 75.0
		if MODE == "challenge":
			if sim_t < 0.6 + c["start"]:
				continue
			cap = 60.0
		_drive(c, go, cap)
		_crash_check(c, 1500.0 if MODE != "challenge" else 1250.0)
	if MODE == "race":
		_race_physics(go)
	elif MODE == "smash":
		_smash_physics(go)
		var alive := cars.filter(func(cc): return cc["alive"])
		if alive.size() == 1 and winner == "":
			_win(alive[0])
	if MODE != "smash" and winner == "":
		for c in cars:
			if c["alive"] and c["body"].position.x > (290.0 if MODE == "race" else 200.0) * PPM:
				_win(c)
				break


func _win(c: Dictionary) -> void:
	winner = c["nick"]
	winner_label.text = winner.to_upper() + " WINS!"
	winner_label.visible = true
	_log("win", 1.0)


func _process(_delta: float) -> void:
	if slow_until > 0.0 and vt() > slow_until:
		Engine.time_scale = 1.0
		slow_until = -1.0
	hook_label.modulate.a = clampf((3.4 - vt()) / 0.5, 0.0, 1.0)
	if MODE != "smash":
		var lead: Node2D = null
		for c in cars:
			if c["alive"] and (lead == null or c["body"].position.x > lead.position.x):
				lead = c["body"]
		if lead == null:
			for n in get_children():
				if n is RigidBody2D and (lead == null or n.position.x > lead.position.x):
					lead = n
		if lead:
			cam.position = Vector2(lead.position.x + 2.0 * PPM, BASE_Y - LANE_DY - 330.0)
	shake *= 0.88
	cam.offset = Vector2(randf_range(-shake, shake), randf_range(-shake, shake))


func _hud() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 10
	add_child(layer)
	var ls := LabelSettings.new()
	ls.font = font
	ls.font_size = 84
	ls.font_color = Color(1, 0.86, 0.12)
	ls.outline_size = 22
	ls.outline_color = Color(0.07, 0.07, 0.2)
	hook_label = Label.new()
	hook_label.label_settings = ls
	hook_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	hook_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hook_label.position = Vector2(40, 120)
	hook_label.size = Vector2(1000, 300)
	layer.add_child(hook_label)
	winner_label = Label.new()
	var ws := ls.duplicate()
	ws.font_size = 124
	winner_label.label_settings = ws
	winner_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	winner_label.position = Vector2(0, 560)
	winner_label.size = Vector2(1080, 200)
	winner_label.visible = false
	layer.add_child(winner_label)
