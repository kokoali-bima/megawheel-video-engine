# CHALLENGE 3D night-headlight contract

Owner requirement: night headlights must show directional illumination rather than added glowing balls.

## Interface and scope

The existing `_headlights(parent, front_x, y, back_x)` interface is retained. Character artwork supplies the lamp housing. Night renders create one `HeadlightRig` containing `RoadSpot` and `LightShaft`; no added spherical front or tail lamps. `_update_headlights(ys)` follows native facing and remains parented to the car so pitch follows jumps and flips. Daytime creates no rig.

The actual spotlight aims forward and down onto the lit road surface. The visible shaft is a soft, tapered, fading warm-white mesh, needed because a spotlight alone is invisible in air under the compatibility renderer. Avoid opaque triangles, white road plates, or effects covering the face/HUD. The road cross-section retains its existing unshaded artwork; do not change it to fabricate an illumination effect.

Keep camera/FOV28/tilt7, native frame coordinates, vehicle sizes/art, wheels, simulation, narration, HUD, slow motion and replay unchanged. Support Godot4.4.1 compatibility and Vulkan. No volumetric-fog dependency or per-frame geometry allocation.

## Acceptance procedure

1. Compile/import the actual project before rendering.
2. Run the independent runtime probe against the exact renderer and export data:

   `<godot4.4.1> --headless --path lab/godot3d_challenge/project --script res://probe_headlights.gd -- <export-directory>`

3. Require `HEADLIGHT_RUNTIME_QA.json` passed: actual spotlight and visible shaft present at night, no sphere lamps, forward/down direction, reverse-facing response, edge-on hide/restore, pitch response, and no rig left after daytime reset. Validate each character in the export.
4. Retain native production and conversion audits without relaxing thresholds. Runtime node checks do not prove the pixels of an old MP4; use the exact renderer for the new render, save its source hash, and inspect the new final images.
5. Inspect a live frame for every cast member, crash/replay frames, and the ending. Verify visible soft rays and readable faces/road on a phone-sized preview. The owner approves the review video.

## Regression evidence for the initial patch

Independent Python tests verified that cast geometry and all renderer code outside the three permitted headlight areas remained unchanged. Three daytime frames were rendered before/after; the inspected first-frame PNGs were byte-identical. Runtime checks passed on the old Splash fixture and the new Splash export. This is scoped regression evidence, not an image analysis of every daytime frame.

The runtime probe is an additional operator gate; the existing `convert3d.py` does not invoke it automatically. Do not report universal automated enforcement until that integration exists. No existing QA thresholds were changed.


## Night readability — owner review 2026-10-22
Keep the navy night sky and directional shafts, but provide enough cool fill for cast paint, faces and hazards. Outside dungeon, night ambient color is (0.78,0.82,1.0), ambient energy is 1.0 times scene.light; directional night color is (0.78,0.84,1.0), with factor0.75. Day and dungeon settings remain unchanged. Do not brighten the finished MP4 or alter the HUD.

For S021 fixed fixtures, run `venv/bin/python lab/godot3d_challenge/probe_night_readability.py <fixture-directory>`. It measures actual interior paint regions for all three cast members, requires brighter paint without clipped highlights, identical top-sky pixels and an identical S013 daytime reference frame. Retain before/after PNGs and JSON. These regions are specific to this fixture and are not a universal luminance test for every camera or character. Final cast/event/outro review remains mandatory; the probe is an additional operator gate, not automatically called by convert3d.
