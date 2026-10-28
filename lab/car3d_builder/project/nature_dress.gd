class_name NatureDress
extends RefCounted

## Dense cartoon roadside nature (Quaternius Stylized Nature MegaKit, CC0) for the wide videos,
## with Poly Haven photo PBR ground (CC0).
## Static helpers only: model cache, PBR ground material cache, banded scattering on both roadside edges.

const NEAR_ITEMS := [
	"Grass_Common_Short", "Grass_Common_Tall", "Grass_Wispy_Short", "Grass_Wispy_Tall",
	"Clover_1", "Clover_2", "Flower_3_Group", "Flower_4_Group", "Pebble_Round_2", "Pebble_Square_3",
]
const MID_ITEMS := [
	"Bush_Common", "Bush_Common_Flowers", "Fern_1", "Plant_1_Big", "Plant_7_Big",
	"Rock_Medium_1", "Rock_Medium_2", "Rock_Medium_3", "Mushroom_Common",
]
const FAR_TREES := [
	"CommonTree_1", "CommonTree_2", "CommonTree_3", "CommonTree_4", "CommonTree_5",
	"Pine_1", "Pine_2", "Pine_3", "Pine_4", "Pine_5",
]
const TEX_DIR := "/root/video-engine/assets/polyhaven"
const GROUND_TEX := "aerial_grass_rock"
const GROUND_TILE_M := 6.0

static var _scene_cache: Dictionary = {}
static var _pbr_cache: Dictionary = {}


static func load_model(path: String) -> Node3D:
	if _scene_cache.has(path):
		var cached: Node3D = _scene_cache[path] as Node3D
		if cached == null:
			return null
		return cached.duplicate() as Node3D
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_file(path, state, 0, path.get_base_dir())
	if err != OK:
		return null
	var scene := doc.generate_scene(state) as Node3D
	if scene == null:
		return null
	_scene_cache[path] = scene
	return scene.duplicate() as Node3D


static func _load_tex(path: String) -> Texture2D:
	if not FileAccess.file_exists(path):
		return null
	var img := Image.load_from_file(path)
	if img == null or img.is_empty():
		return null
	return ImageTexture.create_from_image(img)


static func pbr_material(tex_dir: String, name: String, tile_m: float) -> StandardMaterial3D:
	var key: String = name + "|" + str(tile_m)
	if _pbr_cache.has(key):
		var cached: StandardMaterial3D = _pbr_cache[key] as StandardMaterial3D
		if cached != null:
			return cached
	var mat := StandardMaterial3D.new()
	var diff := _load_tex(tex_dir.path_join(name + "_diff_2k.jpg"))
	if diff != null:
		mat.albedo_texture = diff
	var norm := _load_tex(tex_dir.path_join(name + "_nor_gl_2k.jpg"))
	if norm != null:
		mat.normal_enabled = true
		mat.normal_texture = norm
	var rough := _load_tex(tex_dir.path_join(name + "_rough_2k.jpg"))
	if rough != null:
		mat.roughness_texture = rough
	mat.roughness = 1.0
	mat.uv1_triplanar = true
	mat.uv1_world_triplanar = true
	mat.uv1_scale = Vector3.ONE * (1.0 / tile_m)
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	_pbr_cache[key] = mat
	return mat


static func _model_path(kit_dir: String, name: String) -> String:
	return kit_dir.path_join("glTF").path_join(name + ".gltf")


static func _set_shadows(n: Node) -> void:
	var mi := n as MeshInstance3D
	if mi != null:
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	for c in n.get_children():
		_set_shadows(c)


static func _place(root: Node3D, kit_dir: String, name: String, rng: RandomNumberGenerator,
		x: float, z: float, scl: float) -> void:
	var scene := load_model(_model_path(kit_dir, name))
	if scene == null:
		return
	scene.position = Vector3(x, 0.0, z)
	scene.rotation.y = rng.randf() * TAU
	scene.scale = Vector3(scl, scl, scl)
	_set_shadows(scene)
	root.add_child(scene)


static func dress(parent: Node3D, kit_dir: String, x_from: float, x_to: float, road_hz: float,
		seed_v: int, base_grass: Color) -> Node3D:
	var root := Node3D.new()
	root.name = "NatureDress"
	parent.add_child(root)
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_v
	var x_mid: float = (x_from + x_to) * 0.5
	var span: float = x_to - x_from + 80.0
	var ground_mat: StandardMaterial3D = pbr_material(TEX_DIR, GROUND_TEX, GROUND_TILE_M)
	for side in [1.0, -1.0]:
		var s: float = side
		# ground
		var ground := MeshInstance3D.new()
		var plane := PlaneMesh.new()
		plane.size = Vector2(span, 200.0)
		ground.mesh = plane
		ground.material_override = ground_mat
		ground.position = Vector3(x_mid, -0.005, s * (road_hz + 0.05 + 100.0))
		root.add_child(ground)
		# near band
		var x: float = x_from
		while x < x_to:
			var name: String = NEAR_ITEMS[rng.randi() % NEAR_ITEMS.size()]
			var dist: float = road_hz + rng.randf_range(0.6, 3.0)
			_place(root, kit_dir, name, rng, x, s * dist, rng.randf_range(0.22, 0.4))   # MegaKit grass/flowers are ~1.8-2 m tall: keep them ankle-high
			x += rng.randf_range(0.6, 1.1)
		# mid band
		x = x_from
		while x < x_to:
			var name: String = MID_ITEMS[rng.randi() % MID_ITEMS.size()]
			var dist: float = road_hz + rng.randf_range(7.0, 12.0)                 # keeps the tripod corridor (z 6.5-7.5) clear
			_place(root, kit_dir, name, rng, x, s * dist, rng.randf_range(0.55, 0.9))
			x += rng.randf_range(1.8, 3.2)
		# far band: two trees per step
		x = x_from
		while x < x_to:
			for i in range(2):
				var tname: String = FAR_TREES[rng.randi() % FAR_TREES.size()]
				var dist: float = road_hz + rng.randf_range(12.5, 40.0)
				_place(root, kit_dir, tname, rng, x, s * dist, rng.randf_range(1.2, 1.8))
			x += rng.randf_range(1.6, 3.0)
	return root


## Wide BeamNG mode: remove the old cone trees of challenge3d `_landscape` (8-sided crowns + their trunks) so styles do not mix.
static func strip_cone_trees(parent: Node) -> void:
	for c in parent.get_children():
		var mi := c as MeshInstance3D
		if mi == null or not (mi.mesh is CylinderMesh):
			continue
		var cm := mi.mesh as CylinderMesh
		var crown: bool = cm.top_radius == 0.0 and cm.radial_segments == 8 and cm.height < 8.0
		var trunk: bool = cm.top_radius > 0.1 and cm.top_radius < 0.35 and cm.height < 2.8 and absf(mi.position.z) > 3.5
		if crown or trunk:
			mi.queue_free()
