extends Node3D
## LAB — HYBRID background. The aired 2.5D CHALLENGE frame (cars, road, pits, effects, HUD) is laid over this render
## untouched; Godot draws ONLY the world behind the road, in real 3D: sky from the theme's own colours, a low sun
## with glow, a sea with moving waves and a path of sun glitter, foam at the shore, sand dunes, swaying palm trees,
## layered clouds, gulls and evening haze. Camera = the cairo background camera: the car plane (z = 0) maps exactly
## like cairo (72 px/m x zoom, ground at GROUND_Y + camy*S*zoom) and the horizon sits where cairo puts it.
##   godot --path project --write-movie out.avi --fixed-fps 30 --quit-after N -- <export_dir> [start_frame]

const D = 18.0                                           # camera distance to the car plane (sets 3D parallax)
const SHORE_Z = -16.0                                    # sand from the road back to here, then the sea
var dir = "/root/lab/hy/s27"
var scene = {}
var frames = []
var cam: Camera3D
var start_off = 0
var rng = RandomNumberGenerator.new()
var sway = []                                            # [node, phase, amp]
var drift = []                                           # [node, speed]
var gulls = []                                           # [node, wingL, wingR, speed, phase]
var sun_dir = Vector3(0, 0.1, -1)
var sky_top: Color
var sky_hor: Color
var sun_col: Color


func _ready() -> void:
	var a = OS.get_cmdline_user_args()
	if a.size() > 0:
		dir = a[0]
	if a.size() > 1:
		start_off = int(a[1])
	scene = JSON.parse_string(FileAccess.open(dir + "/scene.json", FileAccess.READ).get_as_text())
	frames = JSON.parse_string(FileAccess.open(dir + "/frames.json", FileAccess.READ).get_as_text())["frames"]
	rng.seed = 11
	_theme_colours()
	_environment()
	var flags = scene["loc_flags"]
	if bool(flags.get("ocean", false)):
		_sea()
	_land()
	if bool(flags.get("palms", false)):
		_palms()
	_clouds()
	if not bool(scene["night"]):
		_gulls()
	cam = Camera3D.new()
	cam.keep_aspect = Camera3D.KEEP_WIDTH
	cam.projection = Camera3D.PROJECTION_FRUSTUM
	cam.near = 0.5
	cam.far = 5000.0
	add_child(cam)
	cam.make_current()


func _c(v) -> Color:
	return Color(float(v[0]), float(v[1]), float(v[2]))


func _theme_colours() -> void:
	var sky = scene["sky"]
	sky_top = _c(sky[0][1])
	sky_hor = _c(sky[sky.size() - 1][1])
	sun_col = Color(1, 0.85, 0.6)
	var f0 = frames[0]
	var fpx0 = float(scene["S"]) * float(f0[5]) * D
	var yh0 = float(f0[6])
	if scene["sun"] != null:                                 # the cairo sun's screen spot -> a direction at infinity
		var s = scene["sun"]
		sun_col = _c(s[3])
		sun_dir = Vector3((float(s[0]) - 540.0) / fpx0, (yh0 - float(s[1])) / fpx0, -1.0).normalized()
	elif scene["moon"] != null:
		var m = scene["moon"]
		sun_col = Color(0.92, 0.95, 1.0)
		sun_dir = Vector3((float(m[0]) - 540.0) / fpx0, (yh0 - float(m[1])) / fpx0, -1.0).normalized()


# ================================================================== sky + light
func _environment() -> void:
	var sky = scene["sky"]
	var f0 = frames[0]
	var fpx0 = float(scene["S"]) * float(f0[5]) * D
	var yh0 = float(f0[6])
	var sh = Shader.new()                                    # the theme's own screen gradient + sun, exactly as cairo
	sh.code = """
shader_type sky;
uniform vec3 c0 : source_color; uniform vec3 c1 : source_color; uniform vec3 c2 : source_color; uniform vec3 c3 : source_color;
uniform float s0; uniform float s1; uniform float s2; uniform float s3;
uniform vec2 sun_px; uniform float sun_r = 100.0; uniform vec3 sun_col : source_color; uniform float has_sun = 1.0;
void sky() {
	float y = SCREEN_UV.y;
	vec3 col = c0;
	col = mix(col, c1, smoothstep(s0, s1, y));
	col = mix(col, c2, smoothstep(s1, s2, y));
	col = mix(col, c3, smoothstep(s2, s3, y));
	vec2 p = SCREEN_UV * vec2(1080.0, 1920.0);
	float d = length(p - sun_px) / sun_r;
	col = mix(col, sun_col, has_sun * 0.9 * clamp(1.0 - (d - 0.6) / 2.2, 0.0, 1.0) * clamp(1.0 - (d - 0.6) / 2.2, 0.0, 1.0));
	col += has_sun * sun_col * 0.35 * exp(-d * 0.45);         // wide atmospheric glow
	col = mix(col, sun_col * 1.25 + vec3(0.25, 0.2, 0.1), has_sun * smoothstep(1.02, 0.97, d));   // the disc
	COLOR = col;
}
"""
	var mat = ShaderMaterial.new()
	mat.shader = sh
	var n = sky.size()
	for k in range(4):
		var idx = mini(k, n - 1)
		mat.set_shader_parameter("c" + str(k), _c(sky[idx][1]))
		mat.set_shader_parameter("s" + str(k), float(sky[idx][0]) + 0.0001 * k)
	if scene["sun"] != null:
		mat.set_shader_parameter("sun_px", Vector2(float(scene["sun"][0]), float(scene["sun"][1])))
		mat.set_shader_parameter("sun_r", float(scene["sun"][2]))
	elif scene["moon"] != null:
		mat.set_shader_parameter("sun_px", Vector2(float(scene["moon"][0]), float(scene["moon"][1])))
		mat.set_shader_parameter("sun_r", float(scene["moon"][2]))
	else:
		mat.set_shader_parameter("has_sun", 0.0)
	mat.set_shader_parameter("sun_col", sun_col)
	var sk = Sky.new()
	sk.sky_material = mat
	var env = Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = sk
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = sky_top.lerp(sky_hor, 0.5)
	env.ambient_light_energy = 0.55 * float(scene["light"])
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.glow_enabled = true
	env.glow_intensity = 0.45
	env.glow_bloom = 0.05
	env.fog_enabled = true                                   # evening haze: far sea and hills melt into the horizon
	env.fog_light_color = sky_hor
	env.fog_density = 0.0016
	env.fog_sky_affect = 0.0
	var we = WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var key = DirectionalLight3D.new()                       # low warm light from the camera side (lesson 10)
	key.rotation_degrees = Vector3(-24, 150, 0)
	key.light_color = sun_col.lerp(Color(1, 1, 1), 0.35)
	key.light_energy = 1.0 * float(scene["light"]) * (0.4 if bool(scene["night"]) else 1.0)
	key.shadow_enabled = true
	key.directional_shadow_max_distance = 120.0
	add_child(key)


# ================================================================== sea
func _sea() -> void:
	var sh = Shader.new()
	sh.code = """
shader_type spatial;
render_mode unshaded, cull_disabled;
uniform vec3 deep : source_color; uniform vec3 shallow : source_color; uniform vec3 horizon : source_color;
uniform vec3 sun_col : source_color; uniform vec3 sun_dir; uniform float shore_z;
varying vec3 wpos;
float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float wave(vec2 p, float t) {
	return sin(p.x * 0.35 + t * 1.1) * 0.18 + sin(p.y * 0.5 - t * 1.5 + p.x * 0.12) * 0.14 + sin((p.x + p.y) * 0.9 + t * 2.3) * 0.05;
}
void vertex() {
	vec3 w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float damp = clamp((shore_z - w.z) / 8.0, 0.0, 1.0);
	VERTEX.y += wave(w.xz, TIME) * damp;
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}
void fragment() {
	float t = TIME;
	float e = 0.6;
	vec2 p = wpos.xz;
	vec3 n = normalize(vec3(-(wave(p + vec2(e, 0.0), t) - wave(p - vec2(e, 0.0), t)) / (2.0 * e), 1.0,
	                        -(wave(p + vec2(0.0, e), t) - wave(p - vec2(0.0, e), t)) / (2.0 * e)));
	n = normalize(n + vec3(sin(p.x * 3.1 + t * 3.0) * 0.04, 0.0, cos(p.y * 2.7 - t * 2.4) * 0.04));
	vec3 v = normalize(CAMERA_POSITION_WORLD - wpos);
	float dist = length(CAMERA_POSITION_WORLD - wpos);
	float fres = pow(1.0 - clamp(dot(n, v), 0.0, 1.0), 4.0);
	vec3 col = mix(shallow, deep, clamp((shore_z - wpos.z) / 60.0, 0.0, 1.0));
	col = mix(col, horizon, clamp(fres * 0.55 + dist / 3500.0, 0.0, 0.85));
	vec3 r = reflect(-v, n);
	float sd = max(dot(r, normalize(sun_dir)), 0.0);
	float sparkle = step(0.82, h(floor(p * 1.7) + floor(t * 8.0)));
	col += sun_col * (pow(sd, 60.0) * 0.6 + pow(sd, 900.0) * 3.5 * (0.4 + sparkle));   // path of light + glitter
	ALBEDO = col;
}
"""
	var mat = ShaderMaterial.new()
	mat.shader = sh
	var sea_c = _c(scene["hills"][0])
	mat.set_shader_parameter("deep", sea_c.darkened(0.45))
	mat.set_shader_parameter("shallow", sea_c.lerp(Color(0.2, 0.75, 0.8), 0.3))
	mat.set_shader_parameter("horizon", sky_hor)
	mat.set_shader_parameter("sun_col", sun_col)
	mat.set_shader_parameter("sun_dir", sun_dir)
	mat.set_shader_parameter("shore_z", SHORE_Z)
	var near = MeshInstance3D.new()                          # detailed waves near the shore, a flat far sea beyond
	var pm = PlaneMesh.new()
	pm.size = Vector2(900, 240)
	pm.subdivide_width = 360
	pm.subdivide_depth = 96
	near.mesh = pm
	near.material_override = mat
	near.position = Vector3(120, -0.4, SHORE_Z - 119)
	add_child(near)
	var far = MeshInstance3D.new()
	var fm = PlaneMesh.new()
	fm.size = Vector2(9000, 4800)
	far.mesh = fm
	far.material_override = mat
	far.position = Vector3(120, -0.36, SHORE_Z - 240 - 2400)
	add_child(far)
	var sh2 = Shader.new()                                   # breaking foam lines rolling onto the sand
	sh2.code = """
shader_type spatial;
render_mode unshaded, cull_disabled, blend_mix;
varying vec3 wpos;
void vertex() { wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
	float u = UV.y;                                      // 0 = sea side, 1 = sand side
	float a = 0.0;
	for (int k = 0; k < 3; k++) {
		float ph = fract(TIME * 0.12 + float(k) / 3.0);
		float line = ph + sin(wpos.x * 0.15 + float(k) * 2.0) * 0.04;
		a += smoothstep(0.05, 0.0, abs(u - line)) * (1.0 - ph);
	}
	a += smoothstep(0.75, 1.0, u) * 0.35 * (0.6 + 0.4 * sin(TIME * 0.8 + wpos.x * 0.2));
	ALBEDO = vec3(1.0);
	ALPHA = clamp(a, 0.0, 0.85);
}
"""
	var fmat = ShaderMaterial.new()
	fmat.shader = sh2
	var foam = MeshInstance3D.new()
	var qm = PlaneMesh.new()
	qm.size = Vector2(900, 7)
	foam.mesh = qm
	foam.material_override = fmat
	foam.position = Vector3(120, -0.2, SHORE_Z - 2.5)
	add_child(foam)


# ================================================================== sand / land
func _land() -> void:
	var flags = scene["loc_flags"]
	var col = _c(scene["hills"][1]) if scene["hills"].size() > 1 else Color(0.85, 0.75, 0.55)
	var noise = FastNoiseLite.new()
	noise.seed = 3
	noise.frequency = 0.08
	var img = noise.get_seamless_image(256, 256)
	var tex = ImageTexture.create_from_image(img)
	var m = StandardMaterial3D.new()
	m.albedo_color = col
	m.detail_enabled = true
	m.detail_blend_mode = BaseMaterial3D.BLEND_MODE_MUL
	m.detail_albedo = tex
	m.uv1_scale = Vector3(40, 10, 1)
	m.roughness = 0.95
	var st = SurfaceTool.new()                               # gentle dunes rising away from the road
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var x0 = -200.0
	var x1 = 520.0
	var zs = [-0.2, -2.0, -4.5, -7.5, -10.5, -13.5, SHORE_Z + 0.5]
	var nx = 240
	for i in range(nx):
		for k in range(zs.size() - 1):
			var xa = lerpf(x0, x1, float(i) / nx)
			var xb = lerpf(x0, x1, float(i + 1) / nx)
			var za = float(zs[k])
			var zb = float(zs[k + 1])
			var pa = Vector3(xa, _dune(xa, za), za)
			var pb = Vector3(xb, _dune(xb, za), za)
			var pc = Vector3(xb, _dune(xb, zb), zb)
			var pd = Vector3(xa, _dune(xa, zb), zb)
			var nrm = (pb - pa).cross(pd - pa).normalized()
			if nrm.y < 0:
				nrm = -nrm
			for q in [[pa, Vector2(xa / 20.0, za / 20.0)], [pb, Vector2(xb / 20.0, za / 20.0)], [pc, Vector2(xb / 20.0, zb / 20.0)],
					  [pa, Vector2(xa / 20.0, za / 20.0)], [pc, Vector2(xb / 20.0, zb / 20.0)], [pd, Vector2(xa / 20.0, zb / 20.0)]]:
				st.set_normal(nrm)
				st.set_uv(q[1])
				st.add_vertex(q[0])
	var land = MeshInstance3D.new()
	land.mesh = st.commit()
	m.uv1_scale = Vector3(1, 1, 1)
	land.material_override = m
	add_child(land)
	if bool(flags.get("ocean", false)):                      # far headlands on the horizon, both sides
		for hx in [-420.0, -150.0, 380.0, 700.0]:
			var hl = MeshInstance3D.new()
			var sp = SphereMesh.new()
			sp.radius = rng.randf_range(140, 230)
			sp.height = sp.radius * 0.55
			hl.mesh = sp
			var hm = StandardMaterial3D.new()
			hm.albedo_color = sky_hor.lerp(Color(0.25, 0.22, 0.35), 0.55)
			hm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			hl.material_override = hm
			hl.position = Vector3(hx, -20, -1500 - rng.randf_range(0, 400))
			add_child(hl)


func _dune(x: float, z: float) -> float:
	var back = clampf(-z / 9.0, 0.0, 1.0)                    # low dunes, the beach slopes down to the water
	var shore = clampf((z - SHORE_Z) / 4.0, 0.0, 1.0)
	return (sin(x * 0.07) * 0.22 + sin(x * 0.19 + 1.3) * 0.1 + 0.25) * back * shore - 0.3 * (1.0 - shore)


func _mat(col: Color, rough := 0.85) -> StandardMaterial3D:
	var m = StandardMaterial3D.new()
	m.albedo_color = col
	m.roughness = rough
	return m


# ================================================================== palms
func _leaf_tex() -> ImageTexture:
	var w = 256
	var hh = 64
	var img = Image.create(w, hh, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	for x in range(w):
		var u = float(x) / w
		var half = sin(u * PI) * 0.5 * (1.0 - 0.3 * u)        # frond outline, thinner at the tip
		for y in range(hh):
			var v = absf(float(y) / hh - 0.5)
			var notch = 0.08 * absf(sin(u * 46.0))            # serrated palm leaflets
			if v < half * 0.95 - notch * (v / maxf(half, 0.01)):
				var c = Color(0.16, 0.42, 0.18).lerp(Color(0.38, 0.6, 0.22), u * 0.6 + v)
				if v < 0.02:
					c = Color(0.45, 0.55, 0.25)
				img.set_pixel(x, y, c)
	return ImageTexture.create_from_image(img)


func _palms() -> void:
	var lt = _leaf_tex()
	var lm = StandardMaterial3D.new()
	lm.albedo_texture = lt
	lm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA_SCISSOR
	lm.alpha_scissor_threshold = 0.5
	lm.cull_mode = BaseMaterial3D.CULL_DISABLED
	lm.roughness = 0.8
	var tm = _mat(Color(0.5, 0.36, 0.22))
	var x = -150.0
	while x < 480.0:
		var z = rng.randf_range(-3.0, -11.0)
		_palm(Vector3(x, _dune(x, z), z), rng.randf_range(0.85, 1.25), lm, tm)
		x += rng.randf_range(7.0, 16.0)


func _palm(base: Vector3, s: float, lm: Material, tm: Material) -> void:
	var root = Node3D.new()
	root.position = base
	add_child(root)
	var lean = rng.randf_range(-0.35, 0.35)
	var p = Vector3.ZERO
	var segs = 7
	var seg_h = 1.15 * s
	for k in range(segs):                                    # curved, ringed trunk
		var cy = MeshInstance3D.new()
		var cm = CylinderMesh.new()
		cm.top_radius = (0.2 - 0.012 * k) * s
		cm.bottom_radius = (0.24 - 0.012 * k) * s
		cm.height = seg_h * 1.04
		cm.radial_segments = 8
		cy.mesh = cm
		cy.material_override = tm
		var ang = lean * (float(k) / segs) * 1.4
		var d = Vector3(sin(ang), cos(ang), 0) * seg_h
		cy.position = p + d * 0.5
		cy.rotation = Vector3(0, 0, -ang)
		root.add_child(cy)
		p += d
	var crown = Node3D.new()
	crown.position = p
	root.add_child(crown)
	sway.append([crown, rng.randf_range(0, TAU), rng.randf_range(0.04, 0.08)])
	for k in range(13):                                      # fronds: arching leaves around the top
		var piv = Node3D.new()
		piv.rotation = Vector3(0, k * TAU / 13.0 + rng.randf_range(-0.2, 0.2), 0)
		crown.add_child(piv)
		var tilt = Node3D.new()
		tilt.rotation = Vector3(0, 0, -rng.randf_range(0.35, 0.75))   # droop
		piv.add_child(tilt)
		var lf = MeshInstance3D.new()
		var qm = QuadMesh.new()
		qm.size = Vector2(3.8 * s, 1.35 * s)
		lf.mesh = qm
		lf.material_override = lm
		lf.position = Vector3(1.8 * s, 0, 0)
		lf.rotation = Vector3(PI / 2, 0, 0)
		tilt.add_child(lf)
	for k in range(3):                                       # coconuts
		var cn = MeshInstance3D.new()
		var sp = SphereMesh.new()
		sp.radius = 0.16 * s
		sp.height = 0.32 * s
		cn.mesh = sp
		cn.material_override = _mat(Color(0.35, 0.25, 0.12))
		cn.position = Vector3(cos(k * 2.1) * 0.22 * s, -0.25 * s, sin(k * 2.1) * 0.22 * s)
		crown.add_child(cn)


# ================================================================== clouds / gulls
func _cloud_tex(seed_: int) -> ImageTexture:
	var noise = FastNoiseLite.new()
	noise.seed = seed_
	noise.frequency = 0.012
	noise.fractal_octaves = 5
	var w = 256
	var hh = 128
	var img = Image.create(w, hh, false, Image.FORMAT_RGBA8)
	for y in range(hh):
		for x in range(w):
			var dx = (float(x) / w - 0.5) * 2.0
			var dy = (float(y) / hh - 0.62) * 2.6
			var fall = clampf(1.0 - (dx * dx + dy * dy), 0.0, 1.0)
			var n = noise.get_noise_2d(x, y) * 0.5 + 0.5
			var a = clampf((n * 1.3 - 0.45) * 2.2 * fall + fall * 0.25, 0.0, 1.0)
			var shade = clampf(1.0 - float(y) / hh * 0.55, 0.0, 1.0)   # lit tops, shaded bellies
			img.set_pixel(x, y, Color(shade, shade, shade, a))
	return ImageTexture.create_from_image(img)


func _clouds() -> void:
	var ccol = _c(scene["cloud"])
	for i in range(14):
		var q = MeshInstance3D.new()
		var qm = QuadMesh.new()
		var w = rng.randf_range(140, 320)
		qm.size = Vector2(w, w * 0.42)
		q.mesh = qm
		var m = StandardMaterial3D.new()
		m.albedo_texture = _cloud_tex(100 + i)
		m.albedo_color = ccol.lerp(sun_col, 0.35)
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		m.disable_fog = true
		m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
		q.material_override = m
		q.position = Vector3(rng.randf_range(-500, 900), rng.randf_range(70, 190), -rng.randf_range(700, 1300))
		add_child(q)
		drift.append([q, rng.randf_range(1.0, 2.5)])


func _gulls() -> void:
	var gm = StandardMaterial3D.new()
	gm.albedo_color = Color(0.95, 0.95, 0.97)
	gm.cull_mode = BaseMaterial3D.CULL_DISABLED
	for i in range(6):
		var g = Node3D.new()
		g.position = Vector3(rng.randf_range(-60, 260), rng.randf_range(14, 30), -rng.randf_range(40, 110))
		add_child(g)
		var wings = []
		for side in [-1.0, 1.0]:
			var piv = Node3D.new()
			g.add_child(piv)
			var w = MeshInstance3D.new()
			var qm = QuadMesh.new()
			qm.size = Vector2(1.1, 0.28)
			w.mesh = qm
			w.material_override = gm
			w.position = Vector3(side * 0.55, 0, 0)
			w.rotation = Vector3(PI / 2, 0, 0)
			piv.add_child(w)
			wings.append(piv)
		gulls.append([g, wings[0], wings[1], rng.randf_range(2.0, 4.0), rng.randf_range(0, TAU)])


# ================================================================== per frame
func _process(_d: float) -> void:
	var i = clampi(start_off + Engine.get_process_frames() - 1, 0, frames.size() - 1)
	var f = frames[i]
	var t = float(i) / 30.0
	var z = float(f[5])
	var ppm = float(scene["S"]) * z
	var fpx = ppm * D
	var yh = float(f[6])
	cam.position = Vector3(float(f[3]), float(f[4]) + (float(scene["ground_y"]) - yh) / ppm, D)
	cam.size = 1080.0 / fpx * cam.near
	cam.frustum_offset = Vector2(0, -(960.0 - yh) / fpx * cam.near)
	for s in sway:
		s[0].rotation = Vector3(sin(t * 1.3 + s[1]) * s[2] * 0.5, 0, sin(t * 1.1 + s[1]) * s[2])
	for d in drift:
		d[0].position.x += d[1] / 30.0
	for g in gulls:
		g[0].position.x += g[3] / 30.0
		g[0].position.y += sin(t * 0.7 + g[4]) * 0.02
		var flap = sin(t * 7.0 + g[4]) * 0.5
		g[1].rotation = Vector3(0, 0, -flap)
		g[2].rotation = Vector3(0, 0, flap)
