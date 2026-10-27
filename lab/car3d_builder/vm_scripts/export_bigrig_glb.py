"""Export the bigrig (Titan) as a Godot-ready body/wheel GLB pair + meta JSON.

Part 1c of CONTRACT.md: Kenney `delivery-flat.glb` cab built in ENGINE metres (s = 1 in Godot),
wheels removed into the wheel file, plus a white trailer box, chassis, "MEGA HAUL" text and eyes.
Run:
  blender -b --python-use-system-env -P export_bigrig_glb.py -- \
      --kit "/root/video-engine/assets/kenney_car_kit/Models/GLB format" --outdir glb2

Kenney axes after import: front = -Y, up = +Z, lateral = X. We rotate the whole car by
+90 deg about Z so that front = +X (Blender); glTF export (export_yup) maps that to Godot
x forward, y up, z toward the camera. Camera-side wheels are then those with y < 0.

Outputs: bigrig_body.glb, bigrig_wheel.glb, bigrig_meta.json in --outdir.
"""
import argparse
import json
import math
import os
import sys
from typing import List, Tuple

import bpy
import mathutils
from mathutils import Vector

STEM = "delivery-flat"
SCALE = 1.7                        # import scale -> engine metres (wheel centre z = 0.3 * 1.7 = 0.51)
WHEEL_NAMES = ("wheel-front-left", "wheel-front-right", "wheel-back-left", "wheel-back-right")


# ---------------------------------------------------------------- helpers
def _mat(name: str, rgb: Tuple[float, float, float], rough: float = 0.5) -> bpy.types.Material:
    """Simple untextured Principled material."""
    key = f"bigrig_{name}"
    m = bpy.data.materials.get(key)
    if m is not None:
        return m
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*rgb, 1.0)
    return m


def _select(objs: List[bpy.types.Object]) -> None:
    """Make objs the only selected + active objects."""
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    if objs:
        bpy.context.view_layer.objects.active = objs[0]


def _export(path: str) -> int:
    """Export the current selection as GLB, return the file size in bytes."""
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True,
                              export_apply=True, export_yup=True,
                              export_cameras=False, export_lights=False)
    return os.path.getsize(path)


def _import_car(kit_dir: str, stem: str) -> List[bpy.types.Object]:
    """Import one kenney GLB into the (already cleaned) scene, return all imported objects."""
    path = os.path.join(kit_dir, f"{stem}.glb")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.context.scene.objects if o not in before]


def _rotate_to_front_x(imported: List[bpy.types.Object]) -> List[bpy.types.Object]:
    """Parent everything to an empty, rotate it +90 deg about Z and bake the rotation into the meshes."""
    rig = bpy.data.objects.new("rig", None)
    bpy.context.collection.objects.link(rig)
    for o in imported:
        if o.parent is None:
            o.parent = rig
            o.matrix_parent_inverse = rig.matrix_world.inverted()
    rig.rotation_euler = (0.0, 0.0, math.radians(90.0))
    bpy.context.view_layer.update()
    # Bake: un-parent with keep transform, then apply the object transforms.
    for o in imported:
        if o.parent is rig:
            mw = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = mw
    meshes = [o for o in imported if o.type == "MESH"]
    _select(meshes)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.data.objects.remove(rig, do_unlink=True)
    bpy.context.view_layer.update()
    return meshes


def _scale_and_place(meshes: List[bpy.types.Object], wheels: List[bpy.types.Object]) -> None:
    """Scale the whole car by SCALE about the origin, then move the cab centre to x = 3.0, wheels on z = 0."""
    rig = bpy.data.objects.new("rig2", None)
    bpy.context.collection.objects.link(rig)
    for o in meshes:
        if o.parent is None:
            o.parent = rig
            o.matrix_parent_inverse = rig.matrix_world.inverted()
    rig.scale = (SCALE, SCALE, SCALE)
    bpy.context.view_layer.update()
    for o in meshes:
        if o.parent is rig:
            mw = o.matrix_world.copy()
            o.parent = None
            o.matrix_world = mw
    bpy.data.objects.remove(rig, do_unlink=True)
    _select(meshes)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Cab = the front half of the model; put its x centre at 3.0 and keep the wheels on the ground.
    lo, hi = _bbox(meshes)
    cab_mid = (hi[0] + (lo[0] + hi[0]) / 2.0) / 2.0
    dz = -min(_centre(o)[2] - max(o.dimensions) / 2.0 for o in wheels) if wheels else 0.0
    dx = 3.0 - cab_mid if hi[0] > 0 else 0.0
    for o in meshes:
        o.location = (o.location[0] + dx, o.location[1], o.location[2] + dz)
    _select(meshes)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    for o in meshes:                                   # taller cab (cartoon proportion); wheels keep their round shape
        if o not in wheels:
            for v in o.data.vertices:
                v.co.z = 0.51 + (v.co.z - 0.51) * 1.3
    bpy.context.view_layer.update()


def _bbox(objs: List[bpy.types.Object]) -> Tuple[List[float], List[float]]:
    """World-space axis-aligned bbox of objs as ([minx,miny,minz],[maxx,maxy,maxz])."""
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], w[i])
                hi[i] = max(hi[i], w[i])
    return lo, hi


def _find_wheels(meshes: List[bpy.types.Object]) -> List[bpy.types.Object]:
    """Pick the 4 wheel objects (by name, else every mesh whose name starts with 'wheel')."""
    out = []
    for o in meshes:
        n = o.name.lower()
        if n in WHEEL_NAMES or n.startswith("wheel"):
            out.append(o)
    return out


def _centre(o: bpy.types.Object) -> List[float]:
    """World-space centre of an object's bounding box."""
    pts = [o.matrix_world @ mathutils.Vector(c) for c in o.bound_box]
    return [sum(p[i] for p in pts) / len(pts) for i in range(3)]


def _recentre_mesh(o: bpy.types.Object) -> None:
    """Translate the mesh data so the wheel's bounding-box centre becomes the origin."""
    off = mathutils.Vector(_centre(o))
    for v in o.data.vertices:
        v.co -= off
    o.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()


def _add_box(size: Tuple[float, float, float], loc: Tuple[float, float, float], m: bpy.types.Material,
             bevel: float = 0.0) -> bpy.types.Object:
    """Bevelled (optional, applied) box object with material m."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bv = o.modifiers.new("bevel", "BEVEL")
        bv.width, bv.segments, bv.limit_method = bevel, 3, "ANGLE"
        _select([o])
        bpy.ops.object.modifier_apply(modifier=bv.name)
    o.data.materials.append(m)
    return o


def _add_text(body: str, size: float, loc: Tuple[float, float, float],
              rgb: Tuple[float, float, float]) -> bpy.types.Object:
    """Text object on the camera side (readable from -Y), rotated (90,0,0), converted to a mesh."""
    cu = bpy.data.curves.new("t", "FONT")
    cu.body = body
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.size = size
    cu.extrude = 0.02
    o = bpy.data.objects.new("MEGA_HAUL", cu)
    bpy.context.collection.objects.link(o)
    o.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    o.location = loc
    o.data.materials.append(_mat("text_blue", rgb, 0.3))
    _select([o])
    bpy.ops.object.convert(target="MESH")
    return bpy.context.object


def _add_eyes(cx: Tuple[float, float], z: float, y: float, radius: float) -> List[bpy.types.Object]:
    """Two cartoon eyes (white + black pupil + glint) on the camera-side cab face."""
    white = _mat("eye_white", (0.95, 0.95, 0.95), 0.3)
    black = _mat("eye_black", (0.01, 0.01, 0.012), 0.2)
    eyes: List[bpy.types.Object] = []
    for ex in cx:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=20, ring_count=12,
                                             location=(ex, y, z))
        eye = bpy.context.object
        eye.scale = (1.0, 0.35, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(white)
        eyes.append(eye)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius * 0.5, segments=16, ring_count=10,
                                             location=(ex + 0.25 * radius, y - radius * 0.15, z))
        pup = bpy.context.object
        pup.scale = (1.0, 0.4, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        pup.data.materials.append(black)
        eyes.append(pup)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius * 0.14, segments=10, ring_count=8,
                                             location=(ex + 0.1 * radius, y - radius * 0.22,
                                                       z + radius * 0.25))
        glint = bpy.context.object
        glint.data.materials.append(_mat("eye_glint", (1.0, 1.0, 1.0), 0.1))
        eyes.append(glint)
    return eyes


# ---------------------------------------------------------------- the vehicle
def export_bigrig(kit_dir: str, outdir: str) -> None:
    """Build body/wheel GLBs + meta JSON for the bigrig."""
    vk = "bigrig"
    bpy.ops.wm.read_factory_settings(use_empty=True)

    imported = _import_car(kit_dir, STEM)
    meshes = _rotate_to_front_x(imported)
    wheels = _find_wheels(meshes)
    if len(wheels) != 4:
        print(f"[export] WARNING {vk}: found {len(wheels)} wheel objects, expected 4", flush=True)
    _scale_and_place(meshes, wheels)

    # Wheel file first (recentring mutates the object's mesh data).
    wheel_path = os.path.join(outdir, f"{vk}_wheel.glb")
    wheel_bytes = 0
    if wheels:
        near = min(wheels, key=lambda o: _centre(o)[1])
        _recentre_mesh(near)
        _select([near])
        wheel_bytes = _export(wheel_path)

    # Trailer, chassis, text and eyes on the cab.
    white = _mat("trailer_white", (0.93, 0.93, 0.95), 0.6)
    trailer = _add_box((7.4, 2.5, 2.4), (-1.9, 0.0, 1.1 + 1.2), white, bevel=0.08)
    chassis = _add_box((7.0, 1.6, 0.25), (-1.9, 0.0, 0.98), _mat("chassis_dark", (0.12, 0.12, 0.13), 0.6))
    txt = _add_text("MEGA HAUL", 0.8, (-1.9, -1.27, 2.3), (0.05, 0.25, 0.75))

    body_objs = [o for o in meshes if o not in wheels] + [trailer, chassis, txt]
    lo, hi = _bbox([o for o in meshes if o not in wheels])
    cab_half_w = (hi[1] - lo[1]) / 2.0
    eyes = _add_eyes((2.6, 3.6), 1.75, -(cab_half_w) - 0.02, 0.36)
    body_objs += eyes

    _select(body_objs)
    body_path = os.path.join(outdir, f"{vk}_body.glb")
    body_bytes = _export(body_path)

    # Meta: engine-metre values on purpose (the engine wheel positions are the truth).
    meta = {
        "vk": vk,
        "cid": "titan",
        "wheel_r": 0.433,
        "wheel_w": 0.4,
        "wheels": [[3.8, -1.05, 0.51], [3.8, 1.05, 0.51], [-4.0, -1.05, 0.51], [-4.0, 1.05, 0.51]],
        "front_x": 3.8,
        "rear_x": -4.0,
        "hub_z": 0.51,
        "track_half": 1.05,
        "yz_k": 1.0,
        "body_bbox": [_bbox(body_objs)[0], _bbox(body_objs)[1]],
        "source": "kenney car-kit 3.1 CC0",
    }
    with open(os.path.join(outdir, f"{vk}_meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)

    print(f"[export] {vk} body={body_bytes} wheel={wheel_bytes}", flush=True)


def main() -> None:
    """Parse args after `--` and export the bigrig."""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(description="Kenney delivery-flat -> bigrig body/wheel GLB exporter")
    ap.add_argument("--kit", required=True, help="folder with kenney GLB files")
    ap.add_argument("--outdir", required=True, help="output folder")
    args = ap.parse_args(argv)

    os.makedirs(args.outdir, exist_ok=True)
    export_bigrig(args.kit, args.outdir)


if __name__ == "__main__":
    main()
