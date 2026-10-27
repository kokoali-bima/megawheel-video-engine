class_name CarBuilderBig
extends RefCounted

## The five big/special vehicles of the original cast, built layer by layer.
## Coordinates are car-local metres: origin = body centre, +x = front, +y = up, +z = camera side.
## Geometry helpers, materials, faces and labels are shared with CarBuilder.


# ---------------------------------------------------------------- f1 (Nitro)

static func build_f1() -> Node3D:
	var root := Node3D.new()
	var c := Color(0.1, 0.55, 0.95)
	var dark := c * 0.65
	var B := 0.42
	var W := 0.9
	# rear wing + post
	_layer(root, _rrect( -2.5, 0.55, 0.75, 0.14, 0.04), W, 0.03, dark)
	_layer(root, _rect(-2.2, 0.2, -2.08, 0.56), 0.08, 0.02, Color(0.15, 0.15, 0.18))
	# body shell
	_layer(root, _poly([Vector2(-2.3, -0.22), Vector2(2.3, -0.22), Vector2(2.35, -0.08), Vector2(1.2, 0.04), Vector2(0.55, 0.22), Vector2(-1.7, 0.22), Vector2(-2.1, 0.08)]), B, 0.06, c)
	_decal(root, _rect(-1.6, -0.06, 1.0, 0.01), B, Color(1, 1, 1), false)
	# driver helmet + visor
	var helmet := CarBuilder._sphere(Vector3(-0.35, 0.42, 0), Vector3(0.21, 0.21, 0.21), _mat(Color(1, 0.85, 0.1), true))
	root.add_child(helmet)
	var visor := CarBuilder._box(-0.3, 0.36, -0.1, 0.46, -0.16, 0.16, _mat(Color(0.1, 0.1, 0.15), false))
	root.add_child(visor)
	# front wing
	_layer(root, _rrect(1.85, -0.3, 0.7, 0.1, 0.03), W, 0.03, dark)
	root.add_child(CarBuilder._label("1", Vector2(-1.05, 0.03), 0.3, Color(1, 1, 1), B + 0.03))
	CarBuilder._lamp(root, 1.95, 0.02, 0.09, B)
	CarBuilder._build_face(root, "f1", B + 0.03)
	return root


# ---------------------------------------------------------------- bus (Buster)

static func build_bus() -> Node3D:
	var root := Node3D.new()
	var c := Color(1, 0.78, 0.05)
	var B := 1.25
	_layer(root, _rrect(-3.7, -1.05, 7.4, 2.1, 0.3), B, 0.1, c)
	_decal(root, _rect(-3.7, -0.35, 3.7, -0.21), B, Color(0.1, 0.1, 0.1), false)
	for i in range(6):
		_decal(root, _rrect(-3.3 + i * 0.95, 0.12, 0.78, 0.7, 0.1), B, CarBuilder.GLASS)
	_decal(root, _rrect(2.55, -0.05, 0.95, 0.9, 0.12), B, CarBuilder.GLASS)
	root.add_child(CarBuilder._label("SCHOOL BUS", Vector2(-0.7, -0.7), 0.42, Color(0.1, 0.1, 0.1), B + 0.03))
	# bumpers front and back
	_layer(root, _rect(3.62, -1.0, 3.8, -0.65), 1.15, 0.02, Color(0.15, 0.15, 0.15))
	_layer(root, _rect(-3.8, -1.0, -3.62, -0.65), 1.15, 0.02, Color(0.15, 0.15, 0.15))
	CarBuilder._lamp(root, 3.55, -0.35, 0.11, B)
	CarBuilder._build_face(root, "bus", B + 0.03)
	return root


# ---------------------------------------------------------------- fire truck (Hydro)

static func build_firetruck() -> Node3D:
	var root := Node3D.new()
	var c := Color(0.88, 0.1, 0.1)
	var B := 1.25
	var R := 0.5
	# body, front window, white stripe
	_layer(root, _rrect(-3.2, -0.95, 6.4, 1.9, 0.2), B, 0.06, c)
	_decal(root, _rrect(1.95, -0.1, 1.05, 0.8, 0.12), B, CarBuilder.GLASS)
	_decal(root, _rect(-3.2, -0.45, 3.2, -0.29), B, Color(1, 1, 1), false)
	# 3 roller-shutter compartment doors per side with horizontal ribs + handle bar
	var door_col := Color(0.80, 0.82, 0.86)
	var rib_col := Color(0.55, 0.57, 0.62)
	var rib_mat := CarBuilder._mat(rib_col, false)
	var handle_mat := CarBuilder._mat(Color(0.3, 0.3, 0.33), false)
	for i in range(3):
		var dx: float = -3.0 + float(i) * 1.45
		_decal(root, _rrect(dx, -0.22, 1.3, 0.98, 0.08), B + 0.02, door_col)
		for s in [1.0, -1.0]:
			for k in range(7):
				var ry: float = -0.12 + float(k) * 0.13
				var rib := CarBuilder._box(dx + 0.04, ry - 0.0125, dx + 1.3 - 0.04, ry + 0.0125, B + 0.02, B + 0.04, rib_mat)
				if s < 0.0:
					rib.scale = Vector3(1.0, 1.0, -1.0)
				root.add_child(rib)
			var handle := CarBuilder._box(dx + 0.45, -0.195, dx + 0.85, -0.145, B + 0.02, B + 0.04, handle_mat)
			if s < 0.0:
				handle.scale = Vector3(1.0, 1.0, -1.0)
			root.add_child(handle)
	# cab seam
	var seam_mat := CarBuilder._mat(CarBuilder.INK, false)
	for s in [1.0, -1.0]:
		var seam := CarBuilder._box(1.56, -0.95, 1.64, 0.95, B, B + 0.01, seam_mat)
		if s < 0.0:
			seam.scale = Vector3(1.0, 1.0, -1.0)
		root.add_child(seam)
	# front: chrome grille + bumper
	root.add_child(CarBuilder._box(3.18, -0.8, 3.26, -0.3, -0.8, 0.8, CarBuilder._mat(Color(0.8, 0.8, 0.84), true)))
	root.add_child(CarBuilder._box(3.0, -0.98, 3.34, -0.8, -1.2, 1.2, CarBuilder._mat(Color(0.2, 0.2, 0.22), true)))
	# ladder: two racks at z = +-0.55, rails + rungs + support posts
	var rail_col := Color(0.75, 0.75, 0.8)
	var rail_mat := CarBuilder._mat(rail_col, false)
	for s in [1.0, -1.0]:
		var z: float = 0.55 * s
		for y in [1.02, 1.28]:
			var rail := CarBuilder._box(-3.0, y - 0.045, 1.4, y + 0.045, z - 0.045, z + 0.045, rail_mat)
			root.add_child(rail)
		for i in range(12):
			var x := -2.9 + i * 0.37
			var rung := CarBuilder._box(x - 0.03, 1.02, x + 0.03, 1.28, z - 0.03, z + 0.03, rail_mat)
			root.add_child(rung)
		for x in [-2.6, -0.8, 1.0]:
			var post := CarBuilder._box(x - 0.03, 0.95, x + 0.03, 1.03, z - 0.03, z + 0.03, rail_mat)
			root.add_child(post)
	# flashing roof light
	var flash: Array = []
	var light := _layer(root, _rrect(2.1, 0.95, 0.6, 0.18, 0.05), R, 0.03, Color(1, 0.15, 0.15))
	flash.append([light, Color(1, 0.15, 0.15), 0])
	root.set_meta("flash", flash)
	# hose reel on the rear end (cylinder axis along z)
	var hose := CarBuilder._cylinder(0.32, 1.6, Vector3(-3.1, -0.1, 0), CarBuilder._mat(Color(0.85, 0.85, 0.2), true))
	root.add_child(hose)
	root.add_child(CarBuilder._label("FIRE", Vector2(-0.9, -0.72), 0.32, Color(1, 1, 1), B + 0.03))
	CarBuilder._lamp(root, 3.05, -0.4, 0.11, B)
	CarBuilder._build_face(root, "firetruck", B + 0.03)
	return root


# ---------------------------------------------------------------- big rig (Titan)

static func build_bigrig() -> Node3D:
	var root := Node3D.new()
	var c := Color(0.95, 0.42, 0.1)
	var TB := 1.3
	var CB := 1.25
	var K := 0.9
	# trailer
	_layer(root, _rrect(-4.8, -0.9, 7.3, 2.05, 0.12), TB, 0.08, Color(0.9, 0.9, 0.94))
	for i in range(1, 7):
		_decal(root, _rect(-4.8 + i * 1.04 - 0.02, -0.9, -4.8 + i * 1.04 + 0.02, 1.15), TB, Color(0.75, 0.75, 0.8), false)
	root.add_child(CarBuilder._label("MEGA HAUL", Vector2(-1.15, 0.15), 0.55, Color(0.12, 0.3, 0.7), TB + 0.03))
	# chassis
	_layer(root, _rect(-4.8, -1.15, 4.8, -0.9), K, 0.03, Color(0.2, 0.2, 0.24))
	# exhaust stacks (CylinderMesh is along Y: stands vertical)
	var stack_mat := _mat(Color(0.7, 0.7, 0.75), true)
	for s in [1.0, -1.0]:
		var stack := CarBuilder._cylinder(0.08, 0.75, Vector3(2.87, 1.225, 1.0 * s), stack_mat)
		root.add_child(stack)
	# cab
	_layer(root, _poly([Vector2(2.7, -1.1), Vector2(4.8, -1.1), Vector2(4.8, 0.2), Vector2(4.55, 1.0), Vector2(2.7, 1.0)]), CB, 0.08, c)
	_decal(root, _rrect(3.55, 0.08, 1.0, 0.8, 0.1), CB, CarBuilder.GLASS)
	_decal(root, _rect(4.62, -0.95, 4.78, -0.25), CB, Color(0.25, 0.25, 0.28))
	CarBuilder._lamp(root, 4.68, -0.12, 0.1, CB)
	CarBuilder._build_face(root, "bigrig", CB + 0.03)
	return root


# ---------------------------------------------------------------- ice cream truck (Sprinkles)

static func build_icecream() -> Node3D:
	var root := Node3D.new()
	var c := Color(1.0, 0.6, 0.76)
	var accent := Color(0.6, 0.95, 0.8)
	var B := 1.2
	# body split at y = -0.55: upper part = main colour, lower band = accent
	var body_pts := CarBuilder._rrect_pts(-2.8, -1.05, 5.6, 2.1, 0.3)
	var upper_rect := CarBuilder._rect_pts(-3.5, -0.55, 3.5, 2.0)
	var lower_rect := CarBuilder._rect_pts(-3.5, -2.0, 3.5, -0.55)
	var upper := _intersect(body_pts, upper_rect)
	var lower := _intersect(body_pts, lower_rect)
	_layer(root, lower, B, 0.06, accent)
	_layer(root, upper, B, 0.06, c)
	# open hatch (dark interior) with two small cones + scoops per side
	var hatch_pts := _rrect(-2.0, -0.15, 2.3, 0.8, 0.1)
	_decal(root, hatch_pts, B, Color(0.22, 0.16, 0.28))
	var cone_mat := CarBuilder._mat(Color(0.85, 0.62, 0.3), true)
	var scoop_pink := CarBuilder._mat(Color(1, 0.6, 0.8), false)
	var scoop_white := CarBuilder._mat(Color(0.98, 0.95, 0.9), false)
	var scoop_x := [-1.4, -0.6]
	for s in [1.0, -1.0]:
		var z: float = s * (B + 0.05)
		for k in range(2):
			var cx: float = scoop_x[k]
			var cone := MeshInstance3D.new()
			var cm := CylinderMesh.new()
			cm.top_radius = 0.09
			cm.bottom_radius = 0.0
			cm.height = 0.3
			cm.radial_segments = 32
			cone.mesh = cm
			cone.material_override = cone_mat
			cone.position = Vector3(cx, 0.1, z)
			cone.rotation.x = PI
			root.add_child(cone)
			var smat := scoop_pink if k == 0 else scoop_white
			root.add_child(CarBuilder._sphere(Vector3(cx, 0.3, z), Vector3(0.1, 0.1, 0.1), smat))
	# counter shelf under the hatch
	var shelf_mat := CarBuilder._mat(Color(0.97, 0.97, 0.97), true)
	root.add_child(CarBuilder._box(-2.1, -0.22, 0.4, -0.15, B, B + 0.32, shelf_mat))
	root.add_child(CarBuilder._box(-2.1, -0.22, 0.4, -0.15, -B - 0.32, -B, shelf_mat))
	# awning that sticks out: 8 stripes + scalloped front edge
	for s in [1.0, -1.0]:
		for i in range(8):
			var col: Color = Color(1, 0.35, 0.55) if i % 2 == 1 else Color(1, 1, 1)
			var x0: float = -2.1 + float(i) * 0.31
			var stripe: MeshInstance3D
			if s > 0.0:
				stripe = CarBuilder._box(x0, 0.80, x0 + 0.31, 0.88, B, B + 0.5, CarBuilder._mat(col, true))
			else:
				stripe = CarBuilder._box(x0, 0.80, x0 + 0.31, 0.88, -B - 0.5, -B, CarBuilder._mat(col, true))
			root.add_child(stripe)
			var hpts := _half_disc_pts(x0 + 0.155, 0.80, 0.155)
			var hz: float = B + 0.5 if s > 0.0 else -B - 0.5
			root.add_child(CarBuilder._prism(hpts, hz - 0.02, hz + 0.02, 0.0, CarBuilder._mat(col, true)))
	# sprinkles on the pink upper body
	var rng := RandomNumberGenerator.new()
	rng.seed = 1234
	var sprinkle_cols := [Color(0.95, 0.2, 0.25), Color(1, 0.85, 0.2), Color(0.25, 0.55, 1), Color(0.3, 0.85, 0.4), Color(1, 1, 1)]
	var placed := 0
	var tries := 0
	while placed < 26 and tries < 500:
		tries += 1
		var sx: float = rng.randf_range(-2.6, 2.6)
		var sy: float = rng.randf_range(0.0, 0.95)
		if sx >= -2.1 and sx <= 0.4 and sy >= -0.25 and sy <= 0.9:
			continue
		if sx >= 1.75 and sx <= 2.8:
			continue
		var spts: PackedVector2Array
		if placed % 2 == 0:
			spts = _rrect(sx - 0.07, sy - 0.0225, 0.14, 0.045, 0.02)
		else:
			spts = _rrect(sx - 0.0225, sy - 0.07, 0.045, 0.14, 0.02)
		_decal(root, spts, B, sprinkle_cols[placed % sprinkle_cols.size()], false)
		placed += 1
	# front window
	_decal(root, _rrect(1.85, -0.05, 0.85, 0.8, 0.12), B, CarBuilder.GLASS)
	root.add_child(CarBuilder._label("ICE CREAM", Vector2(-0.85, -0.8), 0.34, Color(0.55, 0.1, 0.35), B + 0.03))
	# giant cone on the roof
	var roof_cone := MeshInstance3D.new()
	var rcm := CylinderMesh.new()
	rcm.top_radius = 0.35
	rcm.bottom_radius = 0.0
	rcm.height = 0.9
	rcm.radial_segments = 32
	roof_cone.mesh = rcm
	roof_cone.material_override = _mat(Color(0.85, 0.62, 0.3), true)
	roof_cone.position = Vector3(0, 1.5, 0)
	root.add_child(roof_cone)
	root.add_child(CarBuilder._sphere(Vector3(0, 2.1, 0), Vector3(0.42, 0.42, 0.42), _mat(Color(1, 0.85, 0.9), true)))
	root.add_child(CarBuilder._sphere(Vector3(0, 2.55, 0), Vector3(0.12, 0.12, 0.12), _mat(Color(0.9, 0.1, 0.2), true)))
	CarBuilder._lamp(root, 2.65, -0.35, 0.1, B)
	CarBuilder._build_face(root, "icecream", B + 0.03)
	return root


# ---------------------------------------------------------------- helpers for Part 4d

## Points of a lower half circle (angles PI..2*PI) around (cx, cy).
static func _half_disc_pts(cx: float, cy: float, r: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for i in range(11):
		var a: float = PI + PI * float(i) / 10.0
		pts.append(Vector2(cx + cos(a) * r, cy + sin(a) * r))
	return pts


## A mesh that is identical on both z sides: set_damage keeps its dent values on the shared material.


static func _mat(color: Color, outline: bool, emission := 0.0) -> ShaderMaterial:
	return CarBuilder._mat(color, outline, emission)


static func _layer(root: Node3D, pts: PackedVector2Array, X: float, bevel: float, color: Color, outline := true, emission := 0.0, line_col := CarBuilder.INK) -> MeshInstance3D:
	return CarBuilder._layer_prism(root, pts, X, bevel, color, outline, emission, line_col)


static func _decal(root: Node3D, pts: PackedVector2Array, X: float, color: Color, outline := true, line_col := CarBuilder.INK) -> MeshInstance3D:
	return CarBuilder._decal(root, pts, X, color, outline, line_col)


static func _rrect(x: float, y: float, w: float, h: float, r: float) -> PackedVector2Array:
	return CarBuilder._rrect_pts(x, y, w, h, r)


static func _rect(x0: float, y0: float, x1: float, y1: float) -> PackedVector2Array:
	return CarBuilder._rect_pts(x0, y0, x1, y1)


static func _poly(coords: Array) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for p in coords:
		pts.append(Vector2(p[0], p[1]))
	return pts


static func _intersect(a: PackedVector2Array, b: PackedVector2Array) -> PackedVector2Array:
	var out := Geometry2D.intersect_polygons(a, b)
	if out.size() > 0 and out[0].size() >= 3:
		return out[0]
	return a
