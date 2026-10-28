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

# BeamNG-style roadside tripod cameras (owner 2026-10-27, cinematic pass).
const BEAM_INTRO_S := 1.8
const BEAM_STATION_X := 7.0                              # tripod sits this far past each obstacle
const BEAM_STATION_Z := 6.5
const BEAM_STATION_H := 2.2
const BEAM_REPLAY_X := 7.0
const BEAM_REPLAY_Z := 7.5
const BEAM_REPLAY_H := 4.5

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


## Ease-out-back (overshoot): 0 -> 0, 1 -> 1, x clamped to 0..1.
static func ease_out_back(x: float) -> float:
	x = clampf(x, 0.0, 1.0)
	var c1 := 1.70158
	var c3 := c1 + 1.0
	var u := x - 1.0
	return 1.0 + c3 * u * u * u + c1 * u * u


## Height of the ground under `x`: linear interpolation on the track polyline
## `[[x, y], ...]` (sorted by x), clamped at both ends (challenge3d.gd `ground_h`).
static func ground_y(track: Array, x: float) -> float:
	if track.is_empty():
		return 0.0
	if x <= float(track[0][0]):
		return float(track[0][1])
	for i in range(1, track.size()):
		var x0: float = float(track[i - 1][0])
		var y0: float = float(track[i - 1][1])
		var x1: float = float(track[i][0])
		var y1: float = float(track[i][1])
		if x <= x1:
			if x1 - x0 <= 1e-6:
				return y1
			return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
	return float(track[track.size() - 1][1])


## Obstacle intervals of interest (x0, x1) from the scene, sorted by x0, finish line last.
static func pois_from_scene(scene: Dictionary) -> Array:
	var out: Array = []
	for key in ["pits", "ramps", "bumps", "barriers"]:
		var lst = scene.get(key, [])
		if not (lst is Array):
			continue
		for e in lst:
			if not (e is Array) or e.is_empty():
				continue
			if not (e[0] is float or e[0] is int):
				continue
			if e.size() >= 2 and (e[1] is float or e[1] is int):
				out.append([float(e[0]), float(e[1])])
			else:
				out.append([float(e[0]), float(e[0])])
	out.sort_custom(func(a, b): return a[0] < b[0])
	var fin = scene.get("finish_x", null)
	if fin is float or fin is int:
		out.append([float(fin), float(fin)])
	return out


## Nearest POI (by interval centre) for a given x.
static func _nearest_poi(pois: Array, x: float) -> Array:
	var best: Array = pois[0]
	var bd := INF
	for p in pois:
		var c := (float(p[0]) + float(p[1])) * 0.5
		var d: float = absf(c - x)
		if d < bd:
			bd = d
			best = p
	return best


## BeamNG-style camera: roadside tripod, replay, crash orbit, showroom, intro.
## Returns {"pos": Vector3, "target": Vector3, "fov": float}.
static func beam_shot(car: Vector3, st: float, replay: bool, start_x: float, pois: Array, track: Array, failed: bool, t_fail: float, is_win: bool, t_win: float) -> Dictionary:
	var pos := car + Vector3(0.0, 1.0, 5.0)
	var target := car + Vector3(0.0, 0.5, 0.0)
	var fov := 45.0
	if replay and not pois.is_empty():                              # a) replay: roadside tripod near the crash POI
		var poi: Array = _nearest_poi(pois, car.x)                    # GDScript has no for/else: nearest unless one contains the car
		for p in pois:
			if float(p[0]) - 6.0 <= car.x and car.x <= float(p[1]) + 6.0:
				poi = p
				break
		var px := float(poi[0]) - BEAM_REPLAY_X
		pos = Vector3(px, maxf(0.0, ground_y(track, px)) + BEAM_REPLAY_H, BEAM_REPLAY_Z)
		target = car + Vector3(0.0, 0.5, 0.0)
		fov = 40.0
	elif is_win and st >= t_win:                                    # b) showroom orbit around the winner
		var w := st - t_win
		var a := deg_to_rad(25.0 + 18.0 * w)
		pos = Vector3(car.x + 7.0 * sin(a), maxf(0.0, ground_y(track, car.x)) + 1.6, car.z + 7.0 * cos(a))
		target = car + Vector3(0.0, 0.4, 0.0)
		fov = 45.0
	elif failed and st >= t_fail + 0.4:                             # c) low close-up orbit around the wreck
		var w := st - t_fail
		var a := deg_to_rad(35.0 + 10.0 * w)
		pos = Vector3(car.x + 7.5 * sin(a), maxf(0.0, ground_y(track, car.x)) + 2.0, car.z + 7.5 * cos(a))   # wreck close-up, clear of the FAIL badge
		target = car + Vector3(0.0, 0.3, 0.0)
		fov = 45.0
	elif st < BEAM_INTRO_S:                                         # d) level intro: low frontal camera
		var ix := start_x + 14.0                                     # car drives toward and past a roadside camera 7 m off the road
		pos = Vector3(ix, maxf(0.0, ground_y(track, ix)) + 1.6, 7.0)
		target = car + Vector3(0.0, 0.5, 0.0)
		fov = 42.0
	else:                                                           # e) station: tripod past the next obstacle
		var poi: Array = pois[pois.size() - 1] if not pois.is_empty() else [car.x, car.x]
		for p in pois:
			if float(p[1]) > car.x - 1.5:
				poi = p
				break
		var sx := float(poi[1]) + BEAM_STATION_X
		pos = Vector3(sx, maxf(0.0, ground_y(track, sx)) + BEAM_STATION_H, BEAM_STATION_Z)
		var cx := (float(poi[0]) + float(poi[1])) * 0.5
		var centre := Vector3(cx, ground_y(track, cx), 0.0)
		target = (car + Vector3(0.0, 0.5, 0.0)).lerp(centre, 0.3)
		fov = 45.0
	var min_y := ground_y(track, pos.x) + 0.8
	if pos.y < min_y:
		pos.y = min_y
	return {"pos": pos, "target": target, "fov": fov}


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
		var z := road_hz + rng.randf_range(9.0, 45.0)               # owner 2026-10-27: clear of the z 5.2 tripod
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
