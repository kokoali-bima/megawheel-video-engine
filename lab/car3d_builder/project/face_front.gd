class_name FaceFront
extends RefCounted

## Windshields for every car plus "Cars-movie" faces on the windshield (wide video).
## Coordinates car-local metres: +x forward, +y up, +z camera side. Mode "side" keeps the Shorts faces.

const WIND := {
	"sports": {"front": [Vector2(0.5, 0.31), Vector2(-0.1, 0.85)], "hw": 0.62, "rear": [Vector2(-1.0, 0.85), Vector2(-1.3, 0.31)], "rhw": 0.62},
	"police": {"front": [Vector2(0.7, 0.35), Vector2(0.2, 0.95)], "hw": 0.70, "rear": [Vector2(-1.2, 0.95), Vector2(-1.4, 0.35)], "rhw": 0.70},
	"taxi": {"front": [Vector2(0.65, 0.35), Vector2(0.15, 0.95)], "hw": 0.70, "rear": [Vector2(-1.15, 0.95), Vector2(-1.35, 0.35)], "rhw": 0.70},
	"monster": {"front": [Vector2(0.4, 0.45), Vector2(0.0, 1.35)], "hw": 0.80, "rear": [Vector2(-1.3, 1.35), Vector2(-1.5, 0.45)], "rhw": 0.80},
	"monster2": {"front": [Vector2(0.4, 0.45), Vector2(0.0, 1.35)], "hw": 0.80, "rear": [Vector2(-1.3, 1.35), Vector2(-1.5, 0.45)], "rhw": 0.80},
	"bus": {"front": [Vector2(3.7, -0.05), Vector2(3.7, 0.85)], "hw": 1.10, "rear": [Vector2(-3.7, 0.85), Vector2(-3.7, 0.12)], "rhw": 1.00},
	"firetruck": {"front": [Vector2(3.2, -0.1), Vector2(3.2, 0.7)], "hw": 1.10},
	"icecream": {"front": [Vector2(2.8, -0.05), Vector2(2.8, 0.75)], "hw": 1.05},
	"bigrig": {"front": [Vector2(4.79, 0.25), Vector2(4.58, 0.95)], "hw": 1.10},
	"f1": {},
}

const FRONT_X := {
	"sports": 2.1, "police": 2.2, "taxi": 2.15, "monster": 2.15, "monster2": 2.15,
	"bus": 3.7, "firetruck": 3.2, "icecream": 2.8, "bigrig": 4.8, "f1": 2.35,
}

const MOODS := ["normal", "scared", "whoa", "dizzy", "happy"]


# ---------------------------------------------------------------- small helpers

static func _outline(width_px: float, line_col: Color) -> ShaderMaterial:
	return CarBuilder._outline_material(width_px, line_col)


## Adds the thin glass slab of one window edge.
static func _quad_slab(p00: Vector3, p10: Vector3, p11: Vector3, p01: Vector3, thick_dir: Vector3, thick: float, mat: Material, node_name: String) -> MeshInstance3D:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var h := thick_dir.normalized() * (thick * 0.5)
	var a := p00 - h
	var b := p10 - h
	var c := p11 - h
	var d := p01 - h
	var e := p00 + h
	var f := p10 + h
	var g := p11 + h
	var k := p01 + h
	# back face (-h side), then front face (+h side), then the four rims
	CarBuilder._tri(st, a, c, b, true)
	CarBuilder._tri(st, a, d, c, true)
	CarBuilder._tri(st, e, f, g, false)
	CarBuilder._tri(st, e, g, k, false)
	CarBuilder._tri(st, a, b, f, false)
	CarBuilder._tri(st, a, f, e, false)
	CarBuilder._tri(st, b, c, g, false)
	CarBuilder._tri(st, b, g, f, false)
	CarBuilder._tri(st, c, d, k, false)
	CarBuilder._tri(st, c, k, g, false)
	CarBuilder._tri(st, d, a, e, false)
	CarBuilder._tri(st, d, e, k, false)
	var mesh := CarBuilder._build_smooth_mesh(st)
	var mi := MeshInstance3D.new()
	mi.name = node_name
	mi.mesh = mesh
	mi.material_override = mat
	CarBuilder._finish(mi)
	return mi


## One window edge (a -> b in the side profile) as a glass slab at half-width hw.
static func _window(root: Node3D, a: Vector2, b: Vector2, hw: float, front: bool) -> void:
	var a2 := a.lerp(b, 0.12)
	var b2 := a.lerp(b, 0.88)
	var dir := (b2 - a2).normalized()
	var n := Vector2(-dir.y, dir.x)
	if signf(n.x) != (1.0 if front else -1.0):
		n = -n
	var lift := n * 0.02
	var a3 := a2 + lift
	var b3 := b2 + lift
	var p00 := Vector3(a3.x, a3.y, -hw)
	var p10 := Vector3(b3.x, b3.y, -hw)
	var p11 := Vector3(b3.x, b3.y, hw)
	var p01 := Vector3(a3.x, a3.y, hw)
	var thick_dir := Vector3(n.x, n.y, 0.0)
	var mat := CarBuilder._mat(CarBuilder.GLASS, true)
	var mi := _quad_slab(p00, p10, p11, p01, thick_dir, 0.03, mat, "windshield" if front else "rear_window")
	root.add_child(mi)


# ---------------------------------------------------------------- windshield face

static func _frame_node(o: Vector3, R: Vector3, U: Vector3, N: Vector3, node_name: String) -> Node3D:
	var node := Node3D.new()
	node.name = node_name
	node.transform = Transform3D(Basis(R, U, N), o)
	return node


static func _local_circle(cx: float, cy: float, r: float, seg := 16) -> PackedVector3Array:
	var pts := PackedVector3Array()
	for i in range(seg + 1):
		var a := TAU * float(i) / float(seg)
		pts.append(Vector3(cx + cos(a) * r, cy + sin(a) * r, 0.0))
	return pts


static func _arc_local(cx: float, cy: float, r: float, a0: float, a1: float, steps := 10) -> PackedVector3Array:
	var pts := PackedVector3Array()
	for i in range(steps + 1):
		var a := lerp(a0, a1, float(i) / float(steps))
		pts.append(Vector3(cx + cos(a) * r, cy + sin(a) * r, 0.0))
	return pts


## Builds one mood variant of one eye in a local frame (x = right, y = up, z = out).
static func _eye_mood(rr: float, mood: String, eye_idx: int) -> Node3D:
	var node := Node3D.new()
	var white_mat := CarBuilder._mat(Color(1, 1, 1), true)
	white_mat.next_pass = _outline(2.0, CarBuilder.INK)
	if mood == "happy":
		var ink := CarBuilder._mat(CarBuilder.INK, false)
		node.add_child(CarBuilder._tube(_arc_local(0.0, -rr * 0.2, rr * 0.75, 0.15 * PI, 0.85 * PI, 10), rr * 0.2, ink))
		return node
	node.add_child(CarBuilder._sphere(Vector3.ZERO, Vector3(rr, rr * 1.2, rr * 0.45), white_mat))
	var outer := rr * 0.4
	if mood == "dizzy":
		var ink := CarBuilder._mat(CarBuilder.INK, false)
		for s in [1.0, -1.0]:
			var p0 := Vector3(-rr * 0.6, -s * rr * 0.6, outer)
			var p1 := Vector3(rr * 0.6, s * rr * 0.6, outer)
			node.add_child(CarBuilder._tube(PackedVector3Array([p0, p1]), rr * 0.17, ink))
	else:
		var pr := 0.5
		var px := 0.0
		var py := -0.1
		if mood == "scared":
			pr = 0.25
		elif mood == "whoa":
			pr = 0.38
		var pupil := CarBuilder._mat(Color(0, 0, 0), false)
		var cxp := rr * px
		var cyp := rr * py
		node.add_child(CarBuilder._sphere(Vector3(cxp, cyp, outer), Vector3(rr * pr, rr * pr, rr * pr * 0.5), pupil))
		var glint := CarBuilder._mat(Color(1, 1, 1), false)
		node.add_child(CarBuilder._sphere(Vector3(cxp + rr * pr * 0.35, cyp + rr * pr * 0.35, outer + rr * 0.4), Vector3(rr * pr * 0.32, rr * pr * 0.32, rr * pr * 0.16), glint))
	if mood == "scared" or mood == "whoa":
		var ink := CarBuilder._mat(CarBuilder.INK, false)
		var lift := 1.75 if mood == "whoa" else 1.55
		var tilt := 0.0
		if mood == "scared":
			tilt = 0.25 if eye_idx == 0 else -0.25
		var b0 := Vector3(-rr * 0.8, rr * lift - tilt * rr, outer)
		var b1 := Vector3(rr * 0.8, rr * lift + tilt * rr, outer)
		node.add_child(CarBuilder._tube(PackedVector3Array([b0, b1]), rr * 0.15, ink))
	return node


static func _mouth_mood(mw: float, mood: String) -> Node3D:
	var node := Node3D.new()
	var ink := CarBuilder._mat(CarBuilder.INK, false)
	if mood == "normal":
		node.add_child(CarBuilder._tube(_arc_local(0.0, 0.3 * mw, 0.5 * mw, 1.2 * PI, 1.8 * PI, 10), mw * 0.08, ink))
	elif mood == "scared":
		var white_mat := CarBuilder._mat(Color(1, 1, 1), true)
		white_mat.next_pass = _outline(2.0, CarBuilder.INK)
		node.add_child(CarBuilder._prism(CarBuilder._rrect_pts(-mw / 2.0, -mw * 0.22, mw, mw * 0.44, mw * 0.15), -0.015, 0.015, 0.0, white_mat))
		var ink2 := CarBuilder._mat(CarBuilder.INK, false)
		for k in range(1, 4):
			var x := -mw / 2.0 + mw * k / 4.0
			node.add_child(CarBuilder._tube(PackedVector3Array([Vector3(x, -mw * 0.22, 0.03), Vector3(x, mw * 0.22, 0.03)]), mw * 0.025, ink2))
		node.add_child(CarBuilder._tube(PackedVector3Array([Vector3(-mw / 2.0, 0.0, 0.03), Vector3(mw / 2.0, 0.0, 0.03)]), mw * 0.025, ink2))
	elif mood == "whoa":
		var dark := CarBuilder._mat(Color(0.45, 0.05, 0.1), true)
		dark.next_pass = _outline(2.0, CarBuilder.INK)
		node.add_child(CarBuilder._sphere(Vector3(0, 0, 0.03), Vector3(0.26 * mw, 0.32 * mw, 0.08), dark))
	elif mood == "happy":
		var dark := CarBuilder._mat(Color(0.45, 0.05, 0.1), true)
		dark.next_pass = _outline(2.0, CarBuilder.INK)
		var pts := PackedVector2Array()
		for i in range(13):
			var a := PI + PI * float(i) / 12.0
			pts.append(Vector2(cos(a) * mw / 2.0, 0.1 * mw + sin(a) * mw / 2.0))
		node.add_child(CarBuilder._prism(pts, -0.015, 0.015, 0.0, dark))
		var pink := CarBuilder._mat(Color(1, 0.45, 0.5), false)
		node.add_child(CarBuilder._sphere(Vector3(0, -0.22 * mw, 0.04), Vector3(mw * 0.18, mw * 0.18, mw * 0.08), pink))
	else:
		var pts2 := PackedVector3Array()
		for k in range(7):
			var x := -mw / 2.0 + mw * k / 6.0
			var y := (mw * 0.12 if k % 2 else -mw * 0.12)
			pts2.append(Vector3(x, y, 0.0))
		node.add_child(CarBuilder._tube(pts2, mw * 0.06, ink))
	return node


## Eyes + mouth on the windshield plane (named for CarBuilder.set_mood).
static func _build_windshield_face(root: Node3D, vk: String) -> void:
	var data: Dictionary = WIND[vk]
	var front: Array = data["front"]
	var a: Vector2 = front[0]
	var b: Vector2 = front[1]
	var hw: float = data["hw"]
	var a3 := Vector3(a.x, a.y, 0.0)
	var b3 := Vector3(b.x, b.y, 0.0)
	var a2 := a3.lerp(b3, 0.12)
	var b2 := a3.lerp(b3, 0.88)
	var edge := b2 - a2
	var U := edge.normalized()
	var N := Vector3(0.0, 0.0, 0.0)
	var dir2 := (b - a).normalized()
	N = Vector3(-dir2.y, dir2.x, 0.0)
	if N.x < 0.0:
		N = -N
	var R := N.cross(U).normalized()
	var O := a2.lerp(b2, 0.55) + N * 0.04
	var face: Dictionary = CarBuilder.FACES[vk]
	var fr: float = face["r"]
	var rr: float = clamp(fr * 1.7, 0.10, 0.40 * edge.length())
	var eye_off: float = 0.42 * hw
	var mouth_y: float = (face["mouth"] as Vector2).y
	var mw: float = float(face["mw"]) * 1.4
	var mouth_o := Vector3(FRONT_X[vk] + 0.03, mouth_y, 0.0)
	var mouth_R := Vector3(0.0, 0.0, 1.0)
	var mouth_U := Vector3(0.0, 1.0, 0.0)
	var mouth_N := Vector3(1.0, 0.0, 0.0)
	for side in [-1.0, 1.0]:
		var eye_o: Vector3 = O + R * (eye_off * float(side))
		var holder := Node3D.new()                       # one holder per eye: sibling names must stay exactly "eyes_<mood>"
		holder.name = "face_front_eye_%s" % ("l" if side < 0.0 else "r")
		root.add_child(holder)
		for mood in MOODS:
			var wrap := _frame_node(eye_o, R, U, N, "eyes_" + mood)
			wrap.add_child(_eye_mood(rr, mood, 0 if side < 0.0 else 1))
			holder.add_child(wrap)
	if face.has("mouth"):
		for mood in MOODS:
			var wrap := _frame_node(mouth_o, mouth_R, mouth_U, mouth_N, "mouth_" + mood)
			wrap.add_child(_mouth_mood(mw, mood))
			root.add_child(wrap)


# ---------------------------------------------------------------- public API

## Adds windshields to every car; mode "windshield" swaps the side faces for a Cars-movie front face.
static func apply(root: Node3D, vk: String, mode: String) -> void:
	if not WIND.has(vk):
		return
	var data: Dictionary = WIND[vk]
	if data.is_empty():
		return
	if data.has("front"):
		var front: Array = data["front"]
		_window(root, front[0], front[1], float(data["hw"]), true)
	if data.has("rear"):
		var rear: Array = data["rear"]
		var rhw: float = float(data.get("rhw", data["hw"]))
		_window(root, rear[0], rear[1], rhw, false)
	if mode != "windshield":
		return
	for side_name in ["face_side_pos", "face_side_neg"]:
		var c := root.get_node_or_null(side_name)
		if c != null:
			root.remove_child(c)
			c.free()
	_build_windshield_face(root, vk)
