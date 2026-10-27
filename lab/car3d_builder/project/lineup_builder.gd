extends Node3D

## QC lineup of the rebuilt cast: two rows of five cars rendered into a SubViewport and saved as a PNG.
## Usage: godot --path project res://lineup.tscn -- <side|quarter> <out_png> [mood]

const ORDER := ["sports", "police", "taxi", "f1", "monster", "bigrig", "bus", "firetruck", "icecream", "monster2"]

const WHEEL_X := {
	"sports": [-1.35, 1.4],
	"police": [-1.45, 1.45],
	"taxi": [-1.4, 1.4],
	"f1": [-1.6, 1.7],
	"monster": [-1.75, 1.75],
	"monster2": [-1.75, 1.75],
	"bigrig": [-4.0, -2.9, 2.2, 3.8],
	"bus": [-2.5, 2.3],
	"firetruck": [-2.0, 2.1],
	"icecream": [-1.9, 1.9],
}

const BODY_OFFSET := {
	"sports": 0.45,
	"police": 0.64,
	"taxi": 0.62,
	"f1": 0.32,
	"monster": 1.25,
	"monster2": 1.25,
	"bigrig": 1.5,
	"bus": 1.45,
	"firetruck": 1.4,
	"icecream": 1.4,
}

var _view := "side"
var _out_png := "lineup.png"
var _mood := "normal"
var _sub: SubViewport = null

func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		_view = args[0]
	if args.size() > 1:
		_out_png = args[1]
	if args.size() > 2:
		_mood = args[2]
	RenderingServer.set_default_clear_color(Color(0.93, 0.86, 0.76))
	_sub = SubViewport.new()
	_sub.size = Vector2i(2000, 1000)
	_sub.transparent_bg = false
	_sub.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_sub.name = "Lineup"
	add_child(_sub)
	_build_cars()
	_build_ground()
	_build_light()
	_build_camera()

func _process(_delta: float) -> void:
	if Engine.get_process_frames() >= 4:
		var img := _sub.get_texture().get_image()
		if img != null:
			img.save_png(_out_png)
		get_tree().quit()

func _build_cars() -> void:
	for i in range(ORDER.size()):
		var vk: String = ORDER[i]
		var row := i / 5
		var col := i % 5
		var ground := 6.0 if row == 0 else 0.0
		var x := 6.0 + 12.0 * float(col)
		var spec: Dictionary = CarBuilder._wheel_data(vk)
		var r: float = spec["r"]
		var offset: float = BODY_OFFSET.get(vk, 0.45)
		var car := CarBuilder.build(vk)
		car.position = Vector3(x, ground + r + offset, 0.0)
		add_child(car)
		var wxs: Array = WHEEL_X.get(vk, [-1.35, 1.4])
		for wx in wxs:
			for s in [1.0, -1.0]:
				var w := CarBuilder.wheel(vk)
				w.position = Vector3(x + float(wx), ground + r, s * CarBuilder.track_half(vk))
				if s < 0.0:
					w.rotation.y = PI
				add_child(w)
		CarBuilder.set_mood(car, _mood, 0.3)
		var label := Label3D.new()
		label.text = vk
		label.font_size = 64
		label.pixel_size = 0.012
		label.outline_size = 0
		label.shaded = false
		label.modulate = Color(0, 0, 0)
		label.position = Vector3(x, ground - 0.6, 1.5)
		add_child(label)

func _build_ground() -> void:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.35, 0.33, 0.33)
	for ground in [6.0, 0.0]:
		var box := BoxMesh.new()
		box.size = Vector3(64, 0.2, 6)
		var mi := MeshInstance3D.new()
		mi.mesh = box
		mi.material_override = mat
		mi.position = Vector3(30, ground - 0.1, 0)
		add_child(mi)

func _build_light() -> void:
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-50, -30, 0)
	add_child(light)

func _build_camera() -> void:
	var cam := Camera3D.new()
	if _view == "quarter":
		cam.projection = Camera3D.PROJECTION_PERSPECTIVE
		cam.fov = 30.0
		cam.position = Vector3(30 + 18, 22, 70)
		_sub.add_child(cam)
		cam.look_at(Vector3(30, 4.5, 0))
	else:
		cam.projection = Camera3D.PROJECTION_ORTHOGONAL
		cam.size = 62.0
		cam.keep_aspect = Camera3D.KEEP_WIDTH
		cam.position = Vector3(30, 6.0, 50)
		_sub.add_child(cam)
		cam.look_at(Vector3(30, 6.0, 0))
	cam.current = true
