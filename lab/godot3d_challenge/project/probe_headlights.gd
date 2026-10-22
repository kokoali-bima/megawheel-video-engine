extends SceneTree
## Independent runtime gate: execute against the actual Godot project.
var errors: Array = []
var evidence: Array = []

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var packed = load("res://main.tscn") as PackedScene
	var world = packed.instantiate()
	root.add_child(world)
	world.set_process(false)
	await process_frame
	var data_path: String = OS.get_cmdline_user_args()[0]
	for vk in world.cast:
		world.scene["night"] = true
		world.call("_body_mesh", vk)
		await process_frame
		var rig = world.car.get_node_or_null("HeadlightRig")
		if rig == null:
			errors.append(str(vk) + ": no night rig")
			continue
		var spot = rig.find_child("RoadSpot", true, false)
		var beam = rig.find_child("LightShaft", true, false)
		if not spot is SpotLight3D or not beam is MeshInstance3D:
			errors.append(str(vk) + ": missing actual spotlight/visible shaft")
			continue
		var direction: Vector3 = -spot.transform.basis.z.normalized()
		if direction.x <= 0.5 or direction.y >= -0.02:
			errors.append(str(vk) + ": spot not forward/downward")
		for mesh in rig.find_children("*", "MeshInstance3D", true, false):
			if mesh.mesh is SphereMesh:
				errors.append(str(vk) + ": visible lamp sphere")
		world.call("_update_headlights", -1.0)
		var reverse: Vector3 = -spot.global_transform.basis.z.normalized()
		if reverse.x >= -0.5:
			errors.append(str(vk) + ": lamp ignores reversed yaw")
		world.call("_update_headlights", 0.0)
		if rig.visible:
			errors.append(str(vk) + ": edge-on shaft still visible")
		world.call("_update_headlights", 1.0)
		if not rig.visible:
			errors.append(str(vk) + ": shaft not restored")
		world.car.rotation.z = PI
		var inverted: Vector3 = -spot.global_transform.basis.z.normalized()
		if inverted.x >= -0.5 or inverted.y <= 0.02:
			errors.append(str(vk) + ": shaft ignores vehicle pitch")
		world.car.rotation.z = 0.0
		evidence.append({"cast": vk, "spot_direction": [direction.x,direction.y,direction.z]})
		world.scene["night"] = false
		world.call("_body_mesh", vk)
		await process_frame
		if world.car.get_node_or_null("HeadlightRig") != null:
			errors.append(str(vk) + ": rig survives daytime reset")
	var result = {"passed":errors.is_empty(),"errors":errors,"evidence":evidence}
	var output = FileAccess.open(data_path + "/HEADLIGHT_RUNTIME_QA.json", FileAccess.WRITE)
	output.store_string(JSON.stringify(result,"  "))
	output.close()
	print(JSON.stringify(result))
	quit(0 if errors.is_empty() else 5)
