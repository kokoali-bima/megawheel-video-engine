class_name CamProgram
extends RefCounted

# Hybrid cinematic camera program (builder mode, challenge3d.gd).
# Pure angle/dolly decisions: the caller rotates the finished camera transform around `piv`
# (yaw about world UP, lift about the camera right axis) and then dollies along (origin - piv).

const INTRO_S := 2.6
const LIVE_LIFT := 10.0                                  # owner 2026-10-27: a bit higher than the 2D camera, the scene is 3D now
const INTRO_YAW := 90.0
const INTRO_LIFT := -3.0
const INTRO_DOLLY := 0.55
const REPLAY_SWING := 0.3
const REPLAY_YAW := 75.0
const REPLAY_LIFT := 12.0
const REPLAY_DOLLY := 0.6
const WIN_RATE := 35.0
const WIN_LIFT := 6.0
const WIN_DOLLY := 0.7

# Ground colour per location (same table as challenge3d.gd `_landscape`).
const GRASS := {
	"desert": Color(0.86, 0.72, 0.45),
	"beach": Color(0.9, 0.82, 0.6),
	"volcano": Color(0.3, 0.24, 0.22),
	"city": Color(0.45, 0.5, 0.42),
	"snow": Color(0.92, 0.95, 1.0),
}
const GRASS_DEFAULT := Color(0.24, 0.38, 0.25)


## Clamped smoothstep (cairo-free, 0 when x <= 0, 1 when x >= 1).
static func ease01(x: float) -> float:
	x = clampf(x, 0.0, 1.0)
	return x * x * (3.0 - 2.0 * x)


## Returns Vector3(yaw_deg, lift_deg, dolly) for the given frame.
## Priority: replay > winner orbit > level intro > live default.
## yaw0 is the live 3/4 camera yaw (cam_yaw_deg).
static func pose(st: float, replay_u: float, replay_k: int, is_win: bool, t_win: float, yaw0: float) -> Vector3:
	if replay_u >= 0.0:                                            # 3. crash replay: swing to low head-on front/behind
		var side := 1.0 if (replay_k % 2 == 0) else -1.0
		var a := ease01(replay_u / REPLAY_SWING)
		var yaw := lerpf(yaw0, REPLAY_YAW * side, a)
		var lift := lerpf(LIVE_LIFT, REPLAY_LIFT, a)
		var dolly := lerpf(1.0, REPLAY_DOLLY, ease01(replay_u))
		return Vector3(yaw, lift, dolly)
	if is_win and st >= t_win:                                     # 4. winner orbit: slow turn, rising, closing in
		var w := st - t_win
		var yaw := yaw0 + WIN_RATE * w
		var lift := LIVE_LIFT + WIN_LIFT * ease01(w / 2.0)
		var dolly := lerpf(1.0, WIN_DOLLY, ease01(w / 2.0))
		return Vector3(yaw, lift, dolly)
	if st < INTRO_S:                                               # 2. level intro: low front camera, swinging to 3/4
		var x := ease01(st / INTRO_S)
		var yaw := lerpf(INTRO_YAW, yaw0, x)
		var lift := lerpf(INTRO_LIFT, LIVE_LIFT, x)
		var dolly := lerpf(INTRO_DOLLY, 1.0, x)
		return Vector3(yaw, lift, dolly)
	return Vector3(yaw0, LIVE_LIFT, 1.0)                           # 1. live default


## Vertical offset of the whole FrontWorld node: 60 m under the ground while the camera is near the
## side view, rising smoothly to road level once the camera has swung towards the front.
static func front_world_y(yaw_deg: float) -> float:
	var wrapped := fposmod(yaw_deg + 180.0, 360.0) - 180.0
	var k := ease01((absf(wrapped) - 30.0) / 30.0)
	return lerpf(-60.0, 0.0, k)


## Builds the +z side of the road (the side the swung cameras look at), hidden under the ground
## until `front_world_y` lifts it. Style mirrors the mid layer of challenge3d.gd `_landscape`.
static func build_front_world(parent: Node3D, loc: String, road_hz: float, seed_v: int) -> Node3D:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_v
	var grass: Color = GRASS.get(loc, GRASS_DEFAULT)
	var root := Node3D.new()
	root.name = "FrontWorld"

	# (a) ground plane on the camera side
	var ground := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(500.0, 300.0)
	ground.mesh = pm
	var gm := StandardMaterial3D.new()
	gm.albedo_color = grass
	gm.roughness = 0.95
	gm.cull_mode = BaseMaterial3D.CULL_DISABLED
	ground.material_override = gm
	ground.position = Vector3(60.0, -0.02, road_hz + 0.05 + 150.0)
	root.add_child(ground)

	# (b) trees every 4..11 m in x, or rocks for desert/volcano
	var rocks: bool = loc == "desert" or loc == "volcano"
	var x := -60.0
	while x <= 240.0:
		var s := rng.randf_range(0.8, 1.6)
		var z := road_hz + rng.randf_range(6.0, 45.0)
		if rocks:
			var rock := MeshInstance3D.new()
			var rm := SphereMesh.new()
			rm.radius = 1.2 * s
			rm.height = 1.6 * s
			rock.mesh = rm
			var rmat := StandardMaterial3D.new()
			rmat.albedo_color = grass.darkened(0.3)
			rmat.roughness = 0.95
			rock.material_override = rmat
			rock.position = Vector3(x, 0.0, z)
			root.add_child(rock)
		else:
			var trunk := MeshInstance3D.new()
			var tm := CylinderMesh.new()
			tm.top_radius = 0.18 * s
			tm.bottom_radius = 0.25 * s
			tm.height = 1.6 * s
			trunk.mesh = tm
			var tmat := StandardMaterial3D.new()
			tmat.albedo_color = Color(0.42, 0.28, 0.16)
			tmat.roughness = 0.95
			trunk.material_override = tmat
			trunk.position = Vector3(x, 0.8 * s, z)
			root.add_child(trunk)
			var crown := MeshInstance3D.new()
			var cm := CylinderMesh.new()
			cm.top_radius = 0.0
			cm.bottom_radius = 1.3 * s
			cm.height = 3.4 * s
			cm.radial_segments = 8
			crown.mesh = cm
			var cmat := StandardMaterial3D.new()
			cmat.albedo_color = Color(0.18, 0.45, 0.22).lerp(Color(0.3, 0.55, 0.2), rng.randf())
			cmat.roughness = 0.95
			crown.material_override = cmat
			crown.position = Vector3(x, 3.0 * s, z)
			root.add_child(crown)
		x += rng.randf_range(4.0, 11.0)

	# (c) second row of low hills on the horizon of the camera side
	for i in 7:
		var hill := MeshInstance3D.new()
		var hm := CylinderMesh.new()
		hm.top_radius = 0.0
		hm.bottom_radius = rng.randf_range(26.0, 40.0)
		hm.height = rng.randf_range(14.0, 24.0)
		hm.radial_segments = 7
		hill.mesh = hm
		var hmat := StandardMaterial3D.new()
		hmat.albedo_color = grass.darkened(0.15)
		hmat.roughness = 0.95
		hill.material_override = hmat
		var hx := lerpf(-40.0, 220.0, (float(i) + rng.randf_range(0.0, 1.0)) / 7.0)
		var hz := road_hz + rng.randf_range(70.0, 110.0)
		hill.position = Vector3(hx, 0.0, hz)
		root.add_child(hill)

	parent.add_child(root)
	return root
