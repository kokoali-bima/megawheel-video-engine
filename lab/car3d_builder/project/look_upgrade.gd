class_name LookUpgrade
extends RefCounted

## Forward+ "Cars-movie" look upgrade (owner 2026-10-27).
## Realistic sun/shadows, SSAO/SSIL/SDFGI depth, glow, volumetric fog and a warm tonemapper.
## Everything here is a no-op on the CPU Compatibility renderer.


static func is_forward_plus() -> bool:
	return RenderingServer.get_current_rendering_method() == "forward_plus"


## Sets a property only when the object actually has it, so renamed engine properties never break the script.
static func _set_if(obj: Object, prop: String, value: Variant) -> void:
	if obj == null:
		return
	if prop in obj:
		obj.set(prop, value)


static func apply(env: Environment, sun: DirectionalLight3D, night: bool) -> void:
	if not is_forward_plus():
		return
	if env != null:
		# Tonemap
		if "tonemap_mode" in env:
			if Environment.TONE_MAPPER_AGX:
				_set_if(env, "tonemap_mode", Environment.TONE_MAPPER_AGX)
			else:
				_set_if(env, "tonemap_mode", Environment.TONE_MAPPER_ACES)
		_set_if(env, "tonemap_exposure", 1.0)
		# Ambient from the sky
		_set_if(env, "ambient_light_source", Environment.AMBIENT_SOURCE_SKY)
		_set_if(env, "ambient_light_sky_contribution", 0.8)
		_set_if(env, "ambient_light_energy", 0.9 if not night else 0.7)
		# SSAO
		_set_if(env, "ssao_enabled", true)
		_set_if(env, "ssao_radius", 1.2)
		_set_if(env, "ssao_intensity", 1.6)
		_set_if(env, "ssao_power", 1.5)
		# SSIL
		_set_if(env, "ssil_enabled", true)
		_set_if(env, "ssil_radius", 4.0)
		_set_if(env, "ssil_intensity", 0.8)
		# SDFGI
		_set_if(env, "sdfgi_enabled", true)
		_set_if(env, "sdfgi_use_occlusion", true)
		_set_if(env, "sdfgi_cascades", 4)
		_set_if(env, "sdfgi_min_cell_size", 0.2)
		_set_if(env, "sdfgi_energy", 1.0)
		# Glow
		_set_if(env, "glow_enabled", true)
		_set_if(env, "glow_intensity", 0.6)
		_set_if(env, "glow_bloom", 0.04)
		_set_if(env, "glow_hdr_threshold", 1.1)
		# Volumetric fog
		_set_if(env, "volumetric_fog_enabled", true)
		_set_if(env, "volumetric_fog_density", 0.006 if not night else 0.012)
		_set_if(env, "volumetric_fog_albedo", Color(0.9, 0.92, 1.0))
		_set_if(env, "volumetric_fog_length", 140.0)
		_set_if(env, "volumetric_fog_gi_inject", 0.6)
		_set_if(env, "volumetric_fog_sky_affect", 0.2)
		# Colour grade
		_set_if(env, "adjustment_enabled", true)
		_set_if(env, "adjustment_saturation", 1.12)
		_set_if(env, "adjustment_contrast", 1.06)
	if sun != null:
		_set_if(sun, "shadow_enabled", true)
		_set_if(sun, "directional_shadow_mode", DirectionalLight3D.SHADOW_PARALLEL_4_SPLITS)
		_set_if(sun, "directional_shadow_max_distance", 140.0)
		_set_if(sun, "shadow_blur", 1.4)
		_set_if(sun, "light_angular_distance", 1.2)
		_set_if(sun, "light_volumetric_fog_energy", 1.0)
		_set_if(sun, "light_energy", sun.light_energy * 1.15)


static func apply_camera(cam: Camera3D) -> void:
	if not is_forward_plus():
		return
	if cam == null:
		return
	var ca := CameraAttributesPractical.new()
	ca.dof_blur_far_enabled = true
	ca.dof_blur_far_distance = 55.0
	ca.dof_blur_far_transition = 40.0
	ca.dof_blur_amount = 0.05
	ca.auto_exposure_enabled = false
	cam.attributes = ca
