class_name CarBuilder
extends RefCounted

## Builds the original 2D MegaWheel cast as 3D toys, one layer at a time.
## Coordinates are car-local metres: origin = body centre, +x = front, +y = up, +z = camera side.

const CAR_TOON_SHADER := """
shader_type spatial;
render_mode unshaded;
uniform sampler2D albedo_tex : source_color, filter_linear, repeat_enable;
uniform bool use_tex = false;
uniform vec3 albedo_col = vec3(1.0);
uniform vec3 emission_col = vec3(0.0);
uniform float emission_energy = 0.0;
uniform float sat = 1.25;
uniform float contrast = 1.15;
uniform vec3 dent_c = vec3(0.0);
uniform float dent_r = 1.0;
uniform float dent_k = 0.0;
void vertex() {
	vec3 dv = VERTEX - dent_c;
	float dw = dent_k * (1.0 - smoothstep(0.0, dent_r, length(dv)));
	VERTEX -= dv * dw * 0.45;
}
void fragment() {
	vec3 c = albedo_col.rgb;
	if (use_tex) { c *= texture(albedo_tex, UV).rgb; }
	float l = dot(c, vec3(0.299, 0.587, 0.114));
	c = mix(vec3(l), c, sat);
	c = clamp((c - 0.5) * contrast + 0.5, 0.0, 1.0);
	float nl = dot(normalize(NORMAL), normalize(vec3(-0.30, 0.78, 0.55)));
	float lit = 0.66 + 0.18 * step(0.05, nl) + 0.16 * step(0.55, nl);
	float rim = pow(1.0 - clamp(dot(normalize(NORMAL), normalize(VIEW)), 0.0, 1.0), 3.0);
	ALBEDO = clamp(c * lit + c * 0.12 * rim + emission_col.rgb * emission_energy, 0.0, 1.0);
}
"""

const CAR_OUTLINE_SHADER := """
shader_type spatial;
render_mode cull_front, unshaded;
uniform float width_px = 3.5;
uniform bool use_color_normal = true;
uniform vec4 line_col : source_color = vec4(0.1, 0.08, 0.12, 1.0);
uniform vec3 dent_c = vec3(0.0);
uniform float dent_r = 1.0;
uniform float dent_k = 0.0;
void vertex() {
	vec3 nd = use_color_normal ? normalize(COLOR.rgb * 2.0 - 1.0) : normalize(NORMAL);
	vec3 dv = VERTEX - dent_c;
	float dw = dent_k * (1.0 - smoothstep(0.0, dent_r, length(dv)));
	VERTEX -= dv * dw * 0.45;
	vec3 n = nd;
	vec4 clip = PROJECTION_MATRIX * (MODELVIEW_MATRIX * vec4(VERTEX, 1.0));
	vec3 vn = normalize(mat3(MODELVIEW_MATRIX) * n);
	vec2 off = (PROJECTION_MATRIX * vec4(vn, 0.0)).xy;
	float len = length(off);
	if (len > 1e-5) { off /= len; }
	clip.xy += off * width_px * 2.0 / VIEWPORT_SIZE * clip.w;
	POSITION = clip;
}
void fragment() { ALBEDO = line_col.rgb; }
"""

const GLASS := Color(0.62, 0.86, 1.0)
const INK := Color(0.1, 0.08, 0.12)
const BEVEL_BODY := 0.12
const BEVEL_SMALL := 0.05
const BEVEL_TINY := 0.03

const BODY_DIMS := {
	"sports": Vector2(4.2, 0.62),
	"police": Vector2(4.4, 0.7),
	"taxi": Vector2(4.3, 0.7),
	"f1": Vector2(4.6, 0.45),
	"monster": Vector2(4.3, 0.9),
	"monster2": Vector2(4.3, 0.9),
	"bus": Vector2(7.4, 2.1),
	"firetruck": Vector2(6.4, 1.9),
	"bigrig": Vector2(9.6, 2.3),
	"icecream": Vector2(5.6, 2.2),
}

static var _toon_cache := {}
static var _font: Font = null


# ---------------------------------------------------------------- materials

static func _toon_shader() -> Shader:
	var sh := Shader.new()
	sh.code = CAR_TOON_SHADER
	return sh


static func _outline_shader() -> Shader:
	var sh := Shader.new()
	sh.code = CAR_OUTLINE_SHADER
	return sh


static func _mat(color: Color, outline: bool, emission := 0.0) -> ShaderMaterial:
	var key := "%s|%s|%s" % [color.to_html(), outline, emission]
	if _toon_cache.has(key):
		return _toon_cache[key]
	var m := ShaderMaterial.new()
	m.shader = _toon_shader()
	m.set_shader_parameter("albedo_col", Vector3(color.r, color.g, color.b))
	m.set_shader_parameter("use_tex", false)
	m.set_shader_parameter("emission_col", Vector3(color.r, color.g, color.b))
	m.set_shader_parameter("emission_energy", emission)
	m.set_shader_parameter("sat", 1.25)
	m.set_shader_parameter("contrast", 1.15)
	if outline:
		m.next_pass = _outline_material()
	_toon_cache[key] = m
	return m


static func _outline_material(width_px := 3.5, line_col := INK) -> ShaderMaterial:
	var o := ShaderMaterial.new()
	o.shader = _outline_shader()
	var ss := OS.get_environment("CAR3D_SS")                # outline width is in internal pixels: scale with supersampling
	o.set_shader_parameter("width_px", width_px * (float(ss) if ss != "" else 1.0))
	o.set_shader_parameter("use_color_normal", false)
	o.set_shader_parameter("line_col", Color(line_col.r, line_col.g, line_col.b, 1.0))
	return o


## Sets the outline width of a mesh's own outline pass (never shared between meshes).
static func _finish(mi: MeshInstance3D) -> void:
	var mat := mi.material_override as ShaderMaterial
	if mat != null and mat.next_pass is ShaderMaterial:
		var o := mat.next_pass as ShaderMaterial
		o.set_shader_parameter("use_color_normal", mi.mesh is ArrayMesh and mi.mesh.surface_get_format(mi.mesh.get_surface_count() - 1) & Mesh.ARRAY_FORMAT_COLOR != 0)


# ---------------------------------------------------------------- geometry helpers

static func _rrect_pts(x: float, y: float, w: float, h: float, r: float, seg := 5) -> PackedVector2Array:
	var pts := PackedVector2Array()
	var corners := [
		[x + w - r, y + h - r, 0.0],
		[x + r, y + h - r, 0.5 * PI],
		[x + r, y + r, PI],
		[x + w - r, y + r, 1.5 * PI],
	]
	for c in corners:
		var cx: float = c[0]
		var cy: float = c[1]
		var a0: float = c[2]
		for i in range(seg + 1):
			var a := a0 + (0.5 * PI) * float(i) / float(seg)
			pts.append(Vector2(cx + cos(a) * r, cy + sin(a) * r))
	return pts


static func _circle_pts(cx: float, cy: float, r: float, seg := 24) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for i in range(seg):
		var a := TAU * float(i) / float(seg)
		pts.append(Vector2(cx + cos(a) * r, cy + sin(a) * r))
	return pts


static func _rect_pts(x0: float, y0: float, x1: float, y1: float) -> PackedVector2Array:
	return PackedVector2Array([Vector2(x0, y0), Vector2(x1, y0), Vector2(x1, y1), Vector2(x0, y1)])


static func _ensure_ccw(pts: PackedVector2Array) -> PackedVector2Array:
	if Geometry2D.is_polygon_clockwise(pts):
		var out := PackedVector2Array()
		for i in range(pts.size() - 1, -1, -1):
			out.append(pts[i])
		return out
	return pts


## Inward miter offset of a CCW polygon that keeps the vertex count stable.
static func _inset(poly: PackedVector2Array, d: float) -> PackedVector2Array:
	var n := poly.size()
	var out := PackedVector2Array()
	if n < 3:
		return poly
	for i in range(n):
		var p := poly[i]
		var prev := poly[(i - 1 + n) % n]
		var nxt := poly[(i + 1) % n]
		var e1 := (p - prev).normalized()
		var e2 := (nxt - p).normalized()
		var n1 := Vector2(-e1.y, e1.x)
		var n2 := Vector2(-e2.y, e2.x)
		var m := n1 + n2
		if m.length() < 1e-6:
			m = n1
		else:
			m = m.normalized()
		var miter: float = d / max(0.25, m.dot(n1))
		miter = min(miter, 3.0 * d)
		out.append(p + m * miter)
	return out


## Smallest edge-to-opposite-edge distance of a polygon, used to clamp the bevel.
static func _min_width(poly: PackedVector2Array) -> float:
	var bb := Rect2(poly[0], Vector2.ZERO)
	for p in poly:
		bb = bb.expand(p)
	var w: float = min(bb.size.x, bb.size.y)
	return w if w > 0.0 else 1.0


static func _clamp_bevel(poly: PackedVector2Array, z0: float, z1: float, bevel: float) -> float:
	if bevel <= 0.0:
		return 0.0
	var half_z: float = abs(z1 - z0) * 0.5
	var lim: float = min(half_z * 0.35, _min_width(poly) * 0.35)
	return clamp(bevel, 0.0, lim)


## A quarter-round chamfer ring: inset = bevel*(1-cos t), z offset handled by the caller.
static func _ring_offset(bevel: float, segs: int, k: int) -> Vector2:
	var t := (PI * 0.5) * float(k) / float(segs)
	return Vector2(bevel * (1.0 - cos(t)), bevel * sin(t))


static func _tri(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, flip: bool) -> void:
	var n := (b - a).cross(c - a)
	if n.length() < 1e-9:
		return
	n = n.normalized()
	if flip:
		n = -n
		var tmp := b
		b = c
		c = tmp
	# Godot treats CLOCKWISE triangles as front faces: emit a, c, b for a CCW (around n) triangle
	st.set_normal(n)
	st.add_vertex(a)
	st.set_normal(n)
	st.add_vertex(c)
	st.set_normal(n)
	st.add_vertex(b)


static func _poly_fan(st: SurfaceTool, pts: PackedVector3Array, flip: bool) -> void:
	if pts.size() < 3:
		return
	var tris_p: PackedVector2Array = PackedVector2Array()
	for p in pts:
		tris_p.append(Vector2(p.x, p.y))
	var idx := Geometry2D.triangulate_polygon(tris_p)
	if idx.is_empty():
		for i in range(1, pts.size() - 1):
			_tri(st, pts[0], pts[i], pts[i + 1], flip)
		return
	var i := 0
	while i + 2 < idx.size():
		_tri(st, pts[idx[i]], pts[idx[i + 1]], pts[idx[i + 2]], flip)
		i += 3


static func _quad(st: SurfaceTool, a0: Vector3, a1: Vector3, b1: Vector3, b0: Vector3, flip: bool) -> void:
	_tri(st, a0, a1, b1, flip)
	_tri(st, a0, b1, b0, flip)


static func _ring3(pts2: PackedVector2Array, z: float) -> PackedVector3Array:
	var out := PackedVector3Array()
	for p in pts2:
		out.append(Vector3(p.x, p.y, z))
	return out


## Turns the SurfaceTool into an ArrayMesh whose COLOR holds a smooth normal per vertex
## (n * 0.5 + 0.5); flat normals are kept for shading.
static func _build_smooth_mesh(st: SurfaceTool) -> ArrayMesh:
	st.index()
	var arrays := st.commit_to_arrays()
	var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	if verts.is_empty():
		var empty := ArrayMesh.new()
		return empty
	var vcount := verts.size()
	var normals := PackedVector3Array()
	if arrays[Mesh.ARRAY_NORMAL] != null:
		normals = arrays[Mesh.ARRAY_NORMAL]
	var smooth := PackedVector3Array()
	smooth.resize(vcount)
	for i in range(vcount):
		smooth[i] = Vector3.ZERO
	# area-weighted smooth normal per unique position
	var groups := {}
	for t in range(0, vcount - 2, 3):
		var a := verts[t]
		var b := verts[t + 1]
		var c := verts[t + 2]
		var face_n := (b - a).cross(c - a)   # length = 2 * area
		for v in [a, b, c]:
			var key := Vector3i(int(round(v.x * 10000.0)), int(round(v.y * 10000.0)), int(round(v.z * 10000.0)))
			groups[key] = (groups.get(key, Vector3.ZERO) as Vector3) + face_n
	for i in range(vcount):
		var v := verts[i]
		var key := Vector3i(int(round(v.x * 10000.0)), int(round(v.y * 10000.0)), int(round(v.z * 10000.0)))
		var acc: Vector3 = groups.get(key, Vector3.UP)
		smooth[i] = acc.normalized() if acc.length() > 1e-9 else Vector3.UP
	var cols := PackedColorArray()
	cols.resize(vcount)
	for i in range(vcount):
		var s := smooth[i]
		cols[i] = Color(s.x * 0.5 + 0.5, s.y * 0.5 + 0.5, s.z * 0.5 + 0.5, 1.0)
	arrays[Mesh.ARRAY_COLOR] = cols
	if arrays[Mesh.ARRAY_NORMAL] == null or normals.size() != vcount:
		arrays[Mesh.ARRAY_NORMAL] = normals
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh


static func _prism(pts: PackedVector2Array, z0: float, z1: float, bevel: float, mat: Material, segs := 3) -> MeshInstance3D:
	var poly := _ensure_ccw(pts)
	var bv := _clamp_bevel(poly, z0, z1, bevel)
	var ring: float = max(1, segs + 1)
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	if z1 - z0 < 1e-6:
		# flat slab
		var face := _ring3(poly, z0)
		_poly_fan(st, face, false)
		var back := PackedVector3Array()
		for i in range(face.size() - 1, -1, -1):
			back.append(face[i])
		_poly_fan(st, back, true)
	elif bv <= 0.0 or z1 - z0 <= 2.0 * bv:
		# plain prism: no chamfer
		var front := _ring3(poly, z1)
		_poly_fan(st, front, false)
		var back_f := PackedVector3Array()
		for i in range(front.size() - 1, -1, -1):
			back_f.append(Vector3(front[i].x, front[i].y, z0))   # back face lives at z0
		_poly_fan(st, back_f, true)
		var a0 := _ring3(poly, z0)
		var b0 := _ring3(poly, z1)
		for i in range(poly.size()):
			var j := (i + 1) % poly.size()
			_quad(st, a0[i], a0[j], b0[j], b0[i], false)
	else:
		# rounded bevel: rings of the quarter-round chamfer on front and back
		var front_rings: Array = []
		var back_rings: Array = []
		for k in range(ring + 1):
			var off := _ring_offset(bv, segs, k)
			var ring_poly := _inset(poly, off.x)
			front_rings.append(_ring3(ring_poly, z1 - bv + off.y))
			back_rings.append(_ring3(ring_poly, z0 + bv - off.y))
		# front face (innermost ring, at z1)
		_poly_fan(st, front_rings[segs], false)
		# back face (innermost ring at z0, reversed winding)
		var inner_b: PackedVector3Array = back_rings[segs]
		var back := PackedVector3Array()
		for i in range(inner_b.size() - 1, -1, -1):
			back.append(inner_b[i])
		_poly_fan(st, back, true)
		var n := poly.size()
		var wall_b: PackedVector3Array = back_rings[0]
		var wall_f: PackedVector3Array = front_rings[0]
		for i in range(n):
			var j := (i + 1) % n
			_quad(st, wall_b[i], wall_b[j], wall_f[j], wall_f[i], false)   # the side wall between the two chamfers
			for k in range(segs):
				var f0: PackedVector3Array = front_rings[k]
				var f1: PackedVector3Array = front_rings[k + 1]
				_quad(st, f0[i], f0[j], f1[j], f1[i], false)
				var b0r: PackedVector3Array = back_rings[k]
				var b1r: PackedVector3Array = back_rings[k + 1]
				_quad(st, b0r[i], b1r[i], b1r[j], b0r[j], false)
	var mesh := _build_smooth_mesh(st)
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	_finish(mi)
	return mi


static func _slab(pts: PackedVector2Array, half: float, mat: Material) -> MeshInstance3D:
	return _prism(pts, -half, half, 0.0, mat)


static func _box(x0: float, y0: float, x1: float, y1: float, z0: float, z1: float, mat: Material) -> MeshInstance3D:
	return _prism(_rect_pts(x0, y0, x1, y1), z0, z1, 0.0, mat)


static func _sphere(c: Vector3, radii: Vector3, mat: Material) -> MeshInstance3D:
	var sm := SphereMesh.new()
	sm.radius = 1.0
	sm.height = 2.0
	sm.radial_segments = 32
	sm.rings = 16
	var mi := MeshInstance3D.new()
	mi.mesh = sm
	mi.material_override = mat
	mi.position = c
	mi.scale = radii
	_finish(mi)
	return mi


static func _cylinder(r: float, h: float, c: Vector3, mat: Material) -> MeshInstance3D:
	var cm := CylinderMesh.new()
	cm.top_radius = r
	cm.bottom_radius = r
	cm.height = h
	cm.radial_segments = 48
	var mi := MeshInstance3D.new()
	mi.mesh = cm
	mi.material_override = mat
	mi.position = c
	mi.rotation.x = PI * 0.5
	_finish(mi)
	return mi


static func _tube(points: PackedVector3Array, radius: float, mat: Material) -> MeshInstance3D:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var sides := 8
	for k in range(points.size() - 1):
		var p0 := points[k]
		var p1 := points[k + 1]
		var dir := (p1 - p0).normalized()
		var up := Vector3(0, 0, 1)
		if abs(dir.dot(up)) > 0.95:
			up = Vector3(0, 1, 0)
		var n1 := dir.cross(up).normalized()
		var n2 := dir.cross(n1).normalized()
		for i in range(sides):
			var a0 := TAU * float(i) / float(sides)
			var a1 := TAU * float(i + 1) / float(sides)
			var r0 := n1 * cos(a0) * radius + n2 * sin(a0) * radius
			var r1 := n1 * cos(a1) * radius + n2 * sin(a1) * radius
			_quad(st, p0 + r0, p0 + r1, p1 + r1, p1 + r0, false)
	var mesh := _build_smooth_mesh(st)
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = mat
	_finish(mi)
	return mi


static func _arc_points(cx: float, cy: float, r: float, a0: float, a1: float, z: float, steps := 10) -> PackedVector3Array:
	var pts := PackedVector3Array()
	for i in range(steps + 1):
		var a := lerp(a0, a1, float(i) / float(steps))
		pts.append(Vector3(cx + cos(a) * r, cy + sin(a) * r, z))
	return pts


static func _mirror_points(pts: PackedVector3Array) -> PackedVector3Array:
	var out := PackedVector3Array()
	for p in pts:
		out.append(Vector3(p.x, p.y, -p.z))
	return out


static func _font_res() -> Font:
	if _font != null:
		return _font
	var path := "/root/.fonts/LuckiestGuy-Regular.ttf"
	if FileAccess.file_exists(path):
		var f := FontFile.new()
		var err := f.load_dynamic_font(path)
		if err == OK:
			_font = f
		else:
			_font = null
	if _font == null:
		_font = ThemeDB.fallback_font
	return _font


static func _label(text: String, at: Vector2, size: float, color: Color, z: float) -> Node3D:
	var root := Node3D.new()
	var f := _font_res()
	var ps := size / 96.0 * 1.25
	var front := Label3D.new()
	front.text = text
	front.font = f
	front.font_size = 96
	front.pixel_size = ps
	front.outline_size = 0
	front.shaded = false
	front.double_sided = false
	front.no_depth_test = false
	front.modulate = color
	front.position = Vector3(at.x, at.y, z)
	root.add_child(front)
	var back := Label3D.new()
	back.text = text
	back.font = f
	back.font_size = 96
	back.pixel_size = ps
	back.outline_size = 0
	back.shaded = false
	back.double_sided = false
	back.no_depth_test = false
	back.modulate = color
	back.position = Vector3(at.x, at.y, -z)
	back.rotation.y = PI
	root.add_child(back)
	return root


# ---------------------------------------------------------------- layer helpers

static func _layer_prism(root: Node3D, pts: PackedVector2Array, X: float, bevel: float, color: Color, outline := true, emission := 0.0, line_col := INK, width_px := 3.5, segs := 3) -> MeshInstance3D:
	var mat := _mat(color, outline, emission)
	if outline:
		mat.next_pass = _outline_material(width_px, line_col)
	var mi := _prism(pts, -X, X, bevel, mat, segs)
	root.add_child(mi)
	return mi


static func _decal(root: Node3D, pts: PackedVector2Array, X: float, color: Color, outline := true, line_col := INK) -> MeshInstance3D:
	var mat := _mat(color, outline)
	if outline:
		mat.next_pass = _outline_material(2.0, line_col)
	var mi := _slab(pts, X + 0.015, mat)
	root.add_child(mi)
	return mi


static func _pair(root: Node3D, pts: PackedVector2Array, Z: float, color: Color, outline := true, line_col := INK) -> void:
	var mat := _mat(color, outline)
	if outline:
		mat.next_pass = _outline_material(2.0, line_col)
	root.add_child(_prism(pts, Z - 0.06, Z + 0.06, BEVEL_TINY, mat))
	root.add_child(_prism(pts, -Z - 0.06, -Z + 0.06, BEVEL_TINY, mat))


static func _lamp(root: Node3D, x: float, y: float, r: float, B: float) -> void:
	var col := Color(1, 0.95, 0.4)
	for s in [1.0, -1.0]:
		var mat := _mat(col, true, 1.5)
		mat.next_pass = _outline_material(2.0, INK)
		var mi := _sphere(Vector3(x + r * 0.6, y, 0.62 * B * s), Vector3(r * 1.15, r * 1.15, r * 1.15), mat)
		root.add_child(mi)


# ---------------------------------------------------------------- faces

static func _face_eyes(root: Node3D, ex: float, ey: float, r: float, S: float, mood: String, side: float) -> Node3D:
	var node := Node3D.new()
	node.name = "eyes_" + mood
	var big := 1.0
	if mood == "scared":
		big = 1.25
	elif mood == "whoa":
		big = 1.45
	var rr := r * big
	var z := S + rr * 0.15
	var white := _mat(Color(1, 1, 1), true)
	white.next_pass = _outline_material(2.0, INK)
	if mood == "happy":
		var ink := _mat(INK, false)
		var arc := _arc_points(ex, ey - r * 0.2, r * 0.75, 0.15 * PI, 0.85 * PI, z, 10)
		if side < 0:
			arc = _mirror_points(arc)
		node.add_child(_tube(arc, r * 0.2, ink))
		return node
	var eye := _sphere(Vector3(ex, ey, side * z), Vector3(rr, rr * 1.25, rr * 0.45), white)
	node.add_child(eye)
	var outer := side * (z + rr * 0.4)
	if mood == "dizzy":
		var ink := _mat(INK, false)
		for s in [1.0, -1.0]:
			var p0 := Vector3(ex - r * 0.6, ey - s * r * 0.6, outer)
			var p1 := Vector3(ex + r * 0.6, ey + s * r * 0.6, outer)
			node.add_child(_tube(PackedVector3Array([p0, p1]), r * 0.17, ink))
	else:
		var pr := 0.5
		var px := 0.35
		if mood == "scared":
			pr = 0.25
			px = 0.2
		elif mood == "whoa":
			pr = 0.38
			px = 0.0
		var pupil := _mat(Color(0, 0, 0), false)
		var cxp := ex + rr * px
		var cyp := ey + rr * 0.1
		node.add_child(_sphere(Vector3(cxp, cyp, outer), Vector3(rr * pr, rr * pr, rr * pr * 0.5), pupil))
		var glint := _mat(Color(1, 1, 1), false)
		node.add_child(_sphere(Vector3(cxp + rr * pr * 0.35, cyp + rr * pr * 0.35, outer + side * rr * 0.4), Vector3(rr * pr * 0.32, rr * pr * 0.32, rr * pr * 0.16), glint))
	if mood == "scared" or mood == "whoa":
		var ink := _mat(INK, false)
		var lift := 1.75 if mood == "whoa" else 1.55
		var tilt := 0.0
		if mood == "scared":
			tilt = 0.25 if side > 0 else -0.25
		var b0 := Vector3(ex - r * 0.8, ey + r * lift - tilt * r, outer)
		var b1 := Vector3(ex + r * 0.8, ey + r * lift + tilt * r, outer)
		node.add_child(_tube(PackedVector3Array([b0, b1]), r * 0.15, ink))
	return node


static func _face_mouth(root: Node3D, mx: float, my: float, mw: float, S: float, mood: String, side: float) -> Node3D:
	var node := Node3D.new()
	node.name = "mouth_" + mood
	var z := side * S
	var ink := _mat(INK, false)
	if mood == "normal":
		var arc := _arc_points(mx, my + mw * 0.3, mw * 0.5, 1.2 * PI, 1.8 * PI, z, 10)
		node.add_child(_tube(arc, mw * 0.08, ink))
	elif mood == "scared":
		var white := _mat(Color(1, 1, 1), true)
		white.next_pass = _outline_material(2.0, INK)
		node.add_child(_slab(_rrect_pts(mx - mw / 2, my - mw * 0.22, mw, mw * 0.44, mw * 0.15), S, white))
		var ink2 := _mat(INK, false)
		for k in range(1, 4):
			var x := mx - mw / 2 + mw * k / 4
			node.add_child(_tube(PackedVector3Array([Vector3(x, my - mw * 0.22, z), Vector3(x, my + mw * 0.22, z)]), mw * 0.025, ink2))
		node.add_child(_tube(PackedVector3Array([Vector3(mx - mw / 2, my, z), Vector3(mx + mw / 2, my, z)]), mw * 0.025, ink2))
	elif mood == "whoa":
		var dark := _mat(Color(0.45, 0.05, 0.1), true)
		dark.next_pass = _outline_material(2.0, INK)
		node.add_child(_sphere(Vector3(mx, my, z), Vector3(0.26 * mw, 0.32 * mw, 0.08), dark))
	elif mood == "happy":
		var dark := _mat(Color(0.45, 0.05, 0.1), true)
		dark.next_pass = _outline_material(2.0, INK)
		var pts := PackedVector2Array()
		for i in range(13):
			var a := PI + PI * float(i) / 12.0
			pts.append(Vector2(mx + cos(a) * mw / 2, my + mw * 0.1 + sin(a) * mw / 2))
		node.add_child(_slab(pts, S, dark))
		var pink := _mat(Color(1, 0.45, 0.5), false)
		node.add_child(_sphere(Vector3(mx, my - mw * 0.22, z + side * 0.01), Vector3(mw * 0.18, mw * 0.18, mw * 0.08), pink))
	else:
		var pts2 := PackedVector3Array()
		for k in range(7):
			var x := mx - mw / 2 + mw * k / 6.0
			var y := my + (mw * 0.12 if k % 2 else -mw * 0.12)
			pts2.append(Vector3(x, y, z))
		node.add_child(_tube(pts2, mw * 0.06, ink))
	return node


static func _build_face(root: Node3D, vk: String, S: float) -> void:
	var face: Dictionary = FACES[vk]
	var r: float = face["r"]
	var eyes: Array = face["eyes"]
	var mood_list := ["normal", "scared", "whoa", "happy", "dizzy"]
	for s in [1.0, -1.0]:
		var side_root := Node3D.new()
		side_root.name = "face_side_%s" % ("pos" if s > 0 else "neg")
		root.add_child(side_root)
		for i in range(eyes.size()):
			var ex: float = eyes[i][0]
			var ey: float = eyes[i][1]
			for mood in mood_list:
				var node := _face_eyes(side_root, ex, ey, r, S, mood, s)
				side_root.add_child(node)
		var mx: float = face["mouth"][0]
		var my: float = face["mouth"][1]
		var mw: float = face["mw"]
		for mood in mood_list:
			var node := _face_mouth(side_root, mx, my, mw, S + 0.03, mood, s)
			side_root.add_child(node)


static func set_mood(root: Node3D, mood: String, t: float) -> void:
	var m := mood
	if m == "broken":
		m = "dizzy"
	if not (m in ["normal", "scared", "whoa", "happy", "dizzy"]):
		m = "normal"
	for child in _all_children(root):
		var name := String(child.name)
		if name.begins_with("eyes_") or name.begins_with("mouth_"):
			(child as Node3D).visible = name.ends_with(m)
		elif name == "cracks":
			(child as Node3D).visible = mood == "broken"
	var flash: Array = []
	if root.has_meta("flash"):
		flash = root.get_meta("flash")
	var lit := int(t * 6.0) % 2 == 0
	for i in range(flash.size()):
		var item: Array = flash[i]
		var mi: MeshInstance3D = item[0]
		var on_col: Color = item[1]
		var idx: int = item[2]
		var on := lit if idx == 0 else not lit
		var mat := mi.material_override as ShaderMaterial
		if mat == null:
			continue
		if on:
			mat.set_shader_parameter("albedo_col", Vector3(on_col.r, on_col.g, on_col.b))
			mat.set_shader_parameter("emission_col", Vector3(on_col.r, on_col.g, on_col.b))
			mat.set_shader_parameter("emission_energy", 2.0)
		else:
			var d := on_col * 0.45
			mat.set_shader_parameter("albedo_col", Vector3(d.r, d.g, d.b))
			mat.set_shader_parameter("emission_col", Vector3(d.r, d.g, d.b))
			mat.set_shader_parameter("emission_energy", 0.0)


static func _all_children(node: Node) -> Array:
	var out: Array = []
	for c in node.get_children():
		out.append(c)
		out.append_array(_all_children(c))
	return out


# ---------------------------------------------------------------- 3D damage

## Dents: pushes every car-local mesh (relative transform = identity) inward at `center`.
static func set_damage(root: Node3D, center: Vector3, radius: float, amount: float) -> void:
	for mi in _identity_meshes(root):
		var mat: Material = mi.material_override
		if mat is ShaderMaterial:
			_apply_dent(mat as ShaderMaterial, center, radius, amount)
		if mat is ShaderMaterial and (mat as ShaderMaterial).next_pass is ShaderMaterial:
			_apply_dent((mat as ShaderMaterial).next_pass as ShaderMaterial, center, radius, amount)


static func _apply_dent(mat: ShaderMaterial, center: Vector3, radius: float, amount: float) -> void:
	mat.set_shader_parameter("dent_c", center)
	mat.set_shader_parameter("dent_r", radius)
	mat.set_shader_parameter("dent_k", amount)


## All MeshInstance3D under root whose transform relative to root is identity (car-local meshes).
static func _identity_meshes(root: Node3D) -> Array:
	var out: Array = []
	for child in _all_children(root):
		if child is MeshInstance3D:
			var mi := child as MeshInstance3D
			if mi.transform.is_equal_approx(Transform3D.IDENTITY):
				out.append(mi)
	return out


## Cracks on both sides of the body (hidden until mood == "broken").
static func _build_cracks(root: Node3D, vk: String) -> void:
	var node := Node3D.new()
	node.name = "cracks"
	node.visible = false
	var dims: Vector2 = BODY_DIMS.get(vk, Vector2(4.2, 0.62))
	var bw := dims.x
	var bh := dims.y
	var S := _max_abs_z(root)
	var ink := _mat(INK, false)
	for s in [1.0, -1.0]:
		var z: float = s * (S + 0.02)
		var c1 := PackedVector3Array([Vector3(-bw * 0.2, 0.0, z), Vector3(-bw * 0.2 + 0.2, 0.15, z), Vector3(-bw * 0.2 + 0.35, -0.05, z), Vector3(-bw * 0.2 + 0.55, 0.12, z)])
		node.add_child(_tube(c1, 0.025, _ink_alone()))
		var c2 := PackedVector3Array([Vector3(bw * 0.18, -bh * 0.15, z), Vector3(bw * 0.18 + 0.15, -bh * 0.15 - 0.12, z), Vector3(bw * 0.18 + 0.3, -bh * 0.15 + 0.05, z), Vector3(bw * 0.18 + 0.5, -bh * 0.15 - 0.1, z)])
		node.add_child(_tube(c2, 0.025, _ink_alone()))
	root.add_child(node)


## A non-cached ink material so crack tubes never share a material with other parts.
static func _ink_alone() -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = _toon_shader()
	m.set_shader_parameter("albedo_col", Vector3(INK.r, INK.g, INK.b))
	m.set_shader_parameter("use_tex", false)
	m.set_shader_parameter("emission_col", Vector3(0, 0, 0))
	m.set_shader_parameter("emission_energy", 0.0)
	m.set_shader_parameter("sat", 1.25)
	m.set_shader_parameter("contrast", 1.15)
	return m


## Max |z| of the merged AABB of the root's identity-transform meshes.
static func _max_abs_z(root: Node3D) -> float:
	var max_z := 0.0
	for mi in _identity_meshes(root):
		var aabb: AABB = (mi as MeshInstance3D).get_aabb()
		var lo: float = abs(aabb.position.z)
		var hi: float = abs(aabb.position.z + aabb.size.z)
		max_z = max(max_z, max(lo, hi))
	return max_z


## Body colour used for debris chunks.
static func body_color(vk: String) -> Color:
	match vk:
		"sports": return Color(0.93, 0.16, 0.18)
		"police": return Color(0.96, 0.96, 0.98)
		"taxi": return Color(1, 0.8, 0)
		"monster": return Color(0.12, 0.45, 0.95)
		"monster2": return Color(0.2, 0.72, 0.25)
		"f1": return Color(0.1, 0.55, 0.95)
		"bus": return Color(1, 0.78, 0.05)
		"firetruck": return Color(0.88, 0.1, 0.1)
		"bigrig": return Color(0.9, 0.9, 0.94) if rng_pick_white() else Color(0.95, 0.42, 0.1)
		"icecream": return Color(1, 0.6, 0.76)
		_: return Color(0.93, 0.16, 0.18)


## bigrig: 50% trailer white, 50% cab orange (deterministic pick for body_color()).
static func rng_pick_white() -> bool:
	return true


static func debris(vk: String, rng: RandomNumberGenerator) -> MeshInstance3D:
	var rx := rng.randf_range(0.18, 0.42)
	var ry := rng.randf_range(0.15, 0.35)
	var pts := PackedVector2Array()
	for i in range(5):
		var a := TAU * float(i) / 5.0 + rng.randf_range(-0.25, 0.25)
		var k := rng.randf_range(0.75, 1.0)
		pts.append(Vector2(cos(a) * rx * k, sin(a) * ry * k))
	var col: Color
	var pick := rng.randf()
	if pick < 0.6:
		col = body_color(vk)
	elif pick < 0.75:
		col = INK
	elif pick < 0.9:
		col = GLASS
	else:
		col = Color(1, 1, 1)
	var mat := _mat(col, true)
	mat.next_pass = _outline_material(2.5, INK)
	var mi := _prism(pts, -0.06, 0.06, BEVEL_TINY, mat)
	return mi


# ---------------------------------------------------------------- wheels

static func track_half(vk: String) -> float:
	match vk:
		"sports": return 0.80
		"police": return 0.85
		"taxi": return 0.85
		"monster": return 1.15
		"monster2": return 1.15
		"f1": return 0.85
		"bus": return 1.05
		"firetruck": return 1.05
		"bigrig": return 1.05
		"icecream": return 1.0
		_: return 0.80


static func _wheel_data(vk: String) -> Dictionary:
	match vk:
		"sports": return {"r": 0.42, "tw": 0.30, "monster": false}
		"police": return {"r": 0.43, "tw": 0.30, "monster": false}
		"taxi": return {"r": 0.42, "tw": 0.30, "monster": false}
		"monster": return {"r": 1.0, "tw": 0.75, "monster": true}
		"monster2": return {"r": 1.0, "tw": 0.75, "monster": true}
		"f1": return {"r": 0.36, "tw": 0.38, "monster": false}
		"bus": return {"r": 0.55, "tw": 0.40, "monster": false}
		"firetruck": return {"r": 0.6, "tw": 0.40, "monster": false}
		"bigrig": return {"r": 0.6, "tw": 0.40, "monster": false}
		"icecream": return {"r": 0.5, "tw": 0.40, "monster": false}
		_: return {"r": 0.42, "tw": 0.30, "monster": false}


static func wheel(vk: String) -> Node3D:
	var d := _wheel_data(vk)
	var r: float = d["r"]
	var tw: float = d["tw"]
	var monster: bool = d["monster"]
	var root := Node3D.new()
	root.name = "wheel"
	var tyre := _cylinder(r, tw, Vector3.ZERO, _mat(Color(0.12, 0.12, 0.14), true))
	root.add_child(tyre)
	var outer_z := tw / 2 + 0.01
	var hub := _cylinder(r * 0.55, 0.05, Vector3.ZERO, _mat(Color(0.78, 0.78, 0.84), true))
	hub.position = Vector3(0, 0, outer_z)
	root.add_child(hub)
	var spoke_mat := _mat(Color(0.35, 0.35, 0.4), false)
	for i in range(5):
		var a := TAU * float(i) / 5.0
		var pivot := Node3D.new()
		pivot.position = Vector3.ZERO
		pivot.rotation.z = a
		root.add_child(pivot)
		var bar := _box(r * 0.15, -r * 0.05, r * 0.5, r * 0.05, outer_z - 0.01, outer_z + 0.04, spoke_mat)
		pivot.add_child(bar)
	var cap := _cylinder(r * 0.16, 0.06, Vector3.ZERO, _mat(Color(0.25, 0.25, 0.3), true))
	cap.position = Vector3(0, 0, outer_z + 0.03)
	root.add_child(cap)
	if monster:
		var lug_mat := _mat(Color(0.2, 0.2, 0.22), false)
		for i in range(18):
			var a := TAU * float(i) / 18.0
			var pivot := Node3D.new()
			pivot.rotation.z = a
			root.add_child(pivot)
			var lug := _box(r * 0.86, -r * 0.07, r * 1.06, r * 0.07, -tw * 0.5, tw * 0.5, lug_mat)
			pivot.add_child(lug)
	return root


# ---------------------------------------------------------------- vehicle data

const SPORTS := {
	"cabin": [Vector2(-1.3, 0.31), Vector2(0.5, 0.31), Vector2(-0.1, 0.85), Vector2(-1.0, 0.85)],
	"glass": [Vector2(-1.15, 0.36), Vector2(0.32, 0.36), Vector2(-0.15, 0.76), Vector2(-0.95, 0.76)],
	"body": [Vector2(-2.1, -0.31), Vector2(2.1, -0.31), Vector2(2.1, -0.05), Vector2(1.6, 0.2), Vector2(0.6, 0.31), Vector2(-2.0, 0.31), Vector2(-2.1, 0.1)],
	"stripe": [Vector2(-1.9, -0.06), Vector2(1.2, -0.06), Vector2(1.2, 0.04), Vector2(-1.9, 0.04)],
	"post": [Vector2(-2.05, 0.31), Vector2(-1.85, 0.31), Vector2(-1.9, 0.52), Vector2(-2.05, 0.52)],
	"wing": [Vector2(-2.35, 0.5), Vector2(-1.65, 0.5), Vector2(-1.65, 0.6), Vector2(-2.35, 0.6)],
}

const POLICE := {
	"cabin": [Vector2(-1.4, 0.35), Vector2(0.7, 0.35), Vector2(0.2, 0.95), Vector2(-1.2, 0.95)],
	"glass": [Vector2(-1.25, 0.4), Vector2(0.52, 0.4), Vector2(0.12, 0.86), Vector2(-1.08, 0.86)],
	"body": [Vector2(-2.2, -0.35), Vector2(2.2, -0.35), Vector2(2.2, 0.0), Vector2(1.8, 0.3), Vector2(0.8, 0.35), Vector2(-2.1, 0.35), Vector2(-2.2, 0.15)],
	"panel": [Vector2(-1.0, -0.35), Vector2(0.9, -0.35), Vector2(0.9, 0.3), Vector2(-1.0, 0.33)],
}

const TAXI := {
	"cabin": [Vector2(-1.35, 0.35), Vector2(0.65, 0.35), Vector2(0.15, 0.95), Vector2(-1.15, 0.95)],
	"glass": [Vector2(-1.2, 0.4), Vector2(0.48, 0.4), Vector2(0.08, 0.86), Vector2(-1.03, 0.86)],
	"body": [Vector2(-2.15, -0.35), Vector2(2.15, -0.35), Vector2(2.15, 0.0), Vector2(1.75, 0.3), Vector2(0.75, 0.35), Vector2(-2.05, 0.35), Vector2(-2.15, 0.15)],
}

const MONSTER := {
	"cabin": [Vector2(-1.5, 0.45), Vector2(0.4, 0.45), Vector2(0.0, 1.35), Vector2(-1.3, 1.35)],
	"glass": [Vector2(-1.35, 0.52), Vector2(0.22, 0.52), Vector2(-0.08, 1.25), Vector2(-1.2, 1.25)],
	"body": [Vector2(-2.15, -0.45), Vector2(2.15, -0.45), Vector2(2.15, 0.2), Vector2(1.9, 0.45), Vector2(-2.15, 0.45)],
	"flame": [Vector2(-0.3, -0.25), Vector2(0.6, -0.3), Vector2(0.3, -0.1), Vector2(1.3, -0.05), Vector2(0.5, 0.1), Vector2(1.0, 0.3), Vector2(-0.3, 0.2)],
}

const FACES := {
	"sports": {"eyes": [Vector2(-0.75, 0.56), Vector2(-0.35, 0.56)], "r": 0.13, "mouth": Vector2(1.62, -0.17), "mw": 0.3},
	"police": {"eyes": [Vector2(-0.7, 0.62), Vector2(-0.28, 0.62)], "r": 0.13, "mouth": Vector2(1.72, -0.18), "mw": 0.3},
	"taxi": {"eyes": [Vector2(-0.68, 0.62), Vector2(-0.26, 0.62)], "r": 0.13, "mouth": Vector2(1.65, -0.18), "mw": 0.3},
	"monster": {"eyes": [Vector2(-0.8, 0.9), Vector2(-0.35, 0.9)], "r": 0.16, "mouth": Vector2(1.7, -0.22), "mw": 0.34},
	"monster2": {"eyes": [Vector2(-0.8, 0.9), Vector2(-0.35, 0.9)], "r": 0.16, "mouth": Vector2(1.7, -0.22), "mw": 0.34},
	"f1": {"eyes": [Vector2(0.55, 0.13), Vector2(0.9, 0.13)], "r": 0.1, "mouth": Vector2(1.95, -0.1), "mw": 0.22},
	"bus": {"eyes": [Vector2(2.8, 0.42), Vector2(3.22, 0.42)], "r": 0.16, "mouth": Vector2(3.3, -0.72), "mw": 0.38},
	"firetruck": {"eyes": [Vector2(2.35, 0.3), Vector2(2.75, 0.3)], "r": 0.15, "mouth": Vector2(2.85, -0.62), "mw": 0.36},
	"bigrig": {"eyes": [Vector2(3.85, 0.5), Vector2(4.25, 0.5)], "r": 0.17, "mouth": Vector2(4.4, -0.7), "mw": 0.4},
	"icecream": {"eyes": [Vector2(2.05, 0.38), Vector2(2.45, 0.38)], "r": 0.15, "mouth": Vector2(2.5, -0.62), "mw": 0.35},
}


# ---------------------------------------------------------------- vehicles

static func _build_sports() -> Node3D:
	var root := Node3D.new()
	var c := Color(0.93, 0.16, 0.18)
	var dark := c * 0.65
	var B := 0.95
	var C := 0.72
	_layer_prism(root, PackedVector2Array(SPORTS["cabin"]), C, BEVEL_BODY, c, true, 0.0, INK, 3.5)
	_decal(root, PackedVector2Array(SPORTS["glass"]), C, GLASS)
	_layer_prism(root, PackedVector2Array(SPORTS["body"]), B, BEVEL_BODY, c, true, 0.0, INK, 3.5)
	_decal(root, PackedVector2Array(SPORTS["stripe"]), B, Color(1, 1, 1), false)
	_pair(root, PackedVector2Array(SPORTS["post"]), 0.6, dark)
	_layer_prism(root, PackedVector2Array(SPORTS["wing"]), 0.85, BEVEL_SMALL, dark, true, 0.0, INK, 3.5)
	_lamp(root, 1.95, 0.02, 0.09, B)
	_build_face(root, "sports", C + 0.03)
	return root


static func _build_police() -> Node3D:
	var root := Node3D.new()
	var c := Color(0.96, 0.96, 0.98)
	var B := 1.0
	var C := 0.80
	var R := 0.45
	_layer_prism(root, PackedVector2Array(POLICE["cabin"]), C, BEVEL_BODY, c, true, 0.0, INK, 3.5)
	_decal(root, PackedVector2Array(POLICE["glass"]), C, GLASS)
	_decal(root, _rect_pts(-0.375, 0.4, -0.325, 0.86), C, INK, false)
	_layer_prism(root, PackedVector2Array(POLICE["body"]), B, BEVEL_BODY, c, true, 0.0, INK, 3.5)
	_decal(root, PackedVector2Array(POLICE["panel"]), B, Color(0.1, 0.12, 0.2))
	root.add_child(_label("POLICE", Vector2(-0.05, -0.02), 0.26, Color(1, 1, 1), B + 0.03))
	var flash: Array = []
	var r0 := _layer_prism(root, _rrect_pts(-0.75, 0.95, 0.38, 0.16, 0.05), R, BEVEL_SMALL, Color(1, 0.15, 0.15), true, 0.0, INK, 3.5)
	flash.append([r0, Color(1, 0.15, 0.15), 0])
	var r1 := _layer_prism(root, _rrect_pts(-0.35, 0.95, 0.38, 0.16, 0.05), R, BEVEL_SMALL, Color(0.15, 0.4, 1), true, 0.0, INK, 3.5)
	flash.append([r1, Color(0.15, 0.4, 1), 1])
	root.set_meta("flash", flash)
	_lamp(root, 2.05, 0.05, 0.09, B)
	_build_face(root, "police", C + 0.03)
	return root


static func _build_taxi() -> Node3D:
	var root := Node3D.new()
	var c := Color(1, 0.8, 0)
	var B := 1.0
	var C := 0.80
	var R := 0.35
	_layer_prism(root, PackedVector2Array(TAXI["cabin"]), C, BEVEL_BODY, c, true, 0.0, INK, 3.5)
	_decal(root, PackedVector2Array(TAXI["glass"]), C, GLASS)
	_decal(root, _rect_pts(-0.355, 0.4, -0.305, 0.86), C, INK, false)
	_layer_prism(root, PackedVector2Array(TAXI["body"]), B, BEVEL_BODY, c, true, 0.0, INK, 3.5)
	for i in range(16):
		for j in range(2):
			var col := Color(0.1, 0.1, 0.1) if (i + j) % 2 == 0 else Color(1, 1, 1)
			_decal(root, _rect_pts(-1.9 + i * 0.23, -0.1 + j * 0.1, -1.9 + i * 0.23 + 0.23, -0.1 + j * 0.1 + 0.1), B, col, false)
	_layer_prism(root, _rrect_pts(-0.75, 0.95, 0.62, 0.22, 0.05), R, BEVEL_SMALL, Color(1, 1, 0.85), true, 0.0, INK, 3.5)
	root.add_child(_label("TAXI", Vector2(-0.44, 1.06), 0.15, Color(0.1, 0.1, 0.1), R + 0.03))
	_lamp(root, 2.0, 0.08, 0.09, B)
	_build_face(root, "taxi", C + 0.03)
	return root


static func _build_monster(vk: String) -> Node3D:
	var root := Node3D.new()
	var c := Color(0.12, 0.45, 0.95)
	if vk == "monster2":
		c = Color(0.2, 0.72, 0.25)
	var B := 1.1
	var C := 0.9
	var R := 0.5
	_layer_prism(root, PackedVector2Array(MONSTER["cabin"]), C, BEVEL_BODY, c, true, 0.0, INK, 3.5)
	_decal(root, PackedVector2Array(MONSTER["glass"]), C, GLASS)
	_layer_prism(root, PackedVector2Array(MONSTER["body"]), B, BEVEL_BODY, c, true, 0.0, INK, 3.5)
	_decal(root, PackedVector2Array(MONSTER["flame"]), B, Color(1, 0.6, 0.1), true, Color(0.9, 0.2, 0.1))
	for i in range(3):
		_layer_prism(root, _rect_pts(-1.2 + i * 0.35, 1.35, -1.2 + i * 0.35 + 0.25, 1.49), R, BEVEL_SMALL, Color(1, 0.85, 0.2), true, 0.8, INK, 3.5)
	_lamp(root, 2.02, 0.08, 0.1, B)
	_build_face(root, vk, C + 0.03)
	return root


# ---------------------------------------------------------------- public API

const LAMPS := {
	"sports": {"x": 1.95, "y": 0.02, "r": 0.09, "B": 0.95},
	"police": {"x": 2.05, "y": 0.05, "r": 0.09, "B": 1.0},
	"taxi": {"x": 2.0, "y": 0.08, "r": 0.09, "B": 1.0},
	"monster": {"x": 2.02, "y": 0.08, "r": 0.1, "B": 1.1},
	"monster2": {"x": 2.02, "y": 0.08, "r": 0.1, "B": 1.1},
	"f1": {"x": 2.3, "y": -0.05, "r": 0.08, "B": 0.42},
	"bus": {"x": 3.55, "y": -0.35, "r": 0.11, "B": 1.25},
	"firetruck": {"x": 3.05, "y": -0.4, "r": 0.11, "B": 1.25},
	"bigrig": {"x": 4.68, "y": -0.12, "r": 0.1, "B": 1.25},
	"icecream": {"x": 2.65, "y": -0.35, "r": 0.1, "B": 1.2},
}

const HEADLIGHT_BEAM_SHADER := """
shader_type spatial;
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, shadows_disabled;
uniform vec4 beam_color : source_color = vec4(1.0, 0.95, 0.82, 1.0);
uniform float beam_alpha = 0.16;
varying float v_along;
void vertex() { v_along = clamp(0.5 - VERTEX.y / 8.0, 0.0, 1.0); }
void fragment() {
	float fade = (1.0 - smoothstep(0.35, 1.0, v_along)) * smoothstep(0.0, 0.06, v_along);
	float edge = pow(clamp(abs(dot(normalize(NORMAL), normalize(VIEW))), 0.0, 1.0), 1.5);
	ALBEDO = beam_color.rgb;
	ALPHA = beam_alpha * fade * edge;
}
"""


## Two real 3D headlights (a SpotLight3D + a volumetric beam cone per side) on a car built by `build`.
static func headlights(root: Node3D, vk: String) -> Node3D:
	var rig := Node3D.new()
	rig.name = "HeadlightRig3D"
	root.add_child(rig)
	if not LAMPS.has(vk):
		return rig
	var lamp: Dictionary = LAMPS[vk]
	var lx: float = float(lamp["x"])
	var ly: float = float(lamp["y"])
	var lr: float = float(lamp["r"])
	var lb: float = float(lamp["B"])
	var beam_shader := Shader.new()
	beam_shader.code = HEADLIGHT_BEAM_SHADER
	var dir := Vector3(cos(deg_to_rad(-12.0)), sin(deg_to_rad(-12.0)), 0.0)
	for s in [-1.0, 1.0]:
		var origin := Vector3(lx + lr * 0.6, ly, s * 0.62 * lb)
		var spot := SpotLight3D.new()
		spot.position = origin
		spot.rotation_degrees = Vector3(-14, -90, 0)
		spot.light_color = Color(1.0, 0.94, 0.78)
		spot.light_energy = 3.0
		spot.spot_range = 16.0
		spot.spot_angle = 30.0
		spot.spot_angle_attenuation = 1.4
		spot.shadow_enabled = false
		rig.add_child(spot)
		var cm := CylinderMesh.new()
		cm.top_radius = 0.10
		cm.bottom_radius = 1.25
		cm.height = 8.0
		cm.radial_segments = 24
		cm.rings = 1
		cm.cap_top = false
		cm.cap_bottom = false
		var beam_mat := ShaderMaterial.new()
		beam_mat.shader = beam_shader
		beam_mat.set_shader_parameter("beam_color", Color(1.0, 0.95, 0.82, 1.0))
		beam_mat.set_shader_parameter("beam_alpha", 0.16)
		var beam := MeshInstance3D.new()
		beam.name = "HeadlightBeam3D"
		beam.mesh = cm
		beam.material_override = beam_mat
		beam.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		beam.transform = Transform3D(Basis(Quaternion(Vector3.UP, -dir)), origin + dir * 4.0)
		rig.add_child(beam)
	return rig


static func build(vk: String) -> Node3D:
	var root: Node3D
	match vk:
		"sports": root = _build_sports()
		"police": root = _build_police()
		"taxi": root = _build_taxi()
		"monster": root = _build_monster("monster")
		"monster2": root = _build_monster("monster2")
		"f1": root = CarBuilderBig.build_f1()
		"bus": root = CarBuilderBig.build_bus()
		"firetruck": root = CarBuilderBig.build_firetruck()
		"bigrig": root = CarBuilderBig.build_bigrig()
		"icecream": root = CarBuilderBig.build_icecream()
		_: root = _build_sports()
	root.name = "car_" + vk
	_build_cracks(root, vk)
	set_mood(root, "normal", 0.0)
	return root
