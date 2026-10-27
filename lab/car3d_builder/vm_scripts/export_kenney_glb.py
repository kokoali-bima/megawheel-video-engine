"""Export Kenney Car Kit (CC0) vehicles as Godot-ready body/wheel GLBs + meta JSON.

Replaces the procedural cast3d boxes of export_cast_glb.py (Part 1b of CONTRACT.md).
Part 1d: full cast with engine-driven meta (s, yz_k, hub_z), paint recolor and the
icecream roof topper. The Titan (bigrig) lives in export_bigrig_glb.py.

Run:
  blender -b --python-use-system-env -P export_kenney_glb.py -- \
      --kit "/root/video-engine/assets/kenney_car_kit/Models/GLB format" \
      --ids police,taxi,sports --outdir glb2 [--ids all]

Kenney axes after import: front = -Y, up = +Z, lateral = X. We rotate the whole car by
+90 deg about Z so that front = +X (Blender), which glTF export (export_yup) maps to
Godot x forward, y up, z toward the camera. Camera-side wheels are then those with y < 0.

Outputs per vk (same names / meta keys as Part 1, so challenge3d.gd works unchanged):
  <vk>_body.glb, <vk>_wheel.glb, <vk>_meta.json
"""
import argparse
import colorsys
import json
import math
import os
import sys
from typing import Dict, List, Optional, Tuple

import bpy
import mathutils
from mathutils import Vector
import numpy as np

# vk -> (kenney file stem, engine wheelbase wb (m), target body height h (m, without lift),
#        recolor rgb 0-255 or None, lift (m, body raised above the axle),
#        eye spec (x_frac_a, x_frac_b, z_frac, radius_frac))
ENGINE: Dict[str, Tuple[str, float, float, Optional[Tuple[int, int, int]], float,
                        Tuple[float, float, float, float]]] = {
    "sports": ("sedan-sports", 2.75, 1.80, (237, 41, 46), 0.0, (0.36, 0.64, 0.66, 0.20)),
    "police": ("police", 2.90, 2.05, None, 0.0, (0.36, 0.64, 0.66, 0.20)),
    "taxi": ("taxi", 2.80, 2.05, None, 0.0, (0.36, 0.64, 0.68, 0.20)),
    "f1": ("race-future", 3.30, 1.30, None, 0.0, (0.26, 0.46, 0.84, 0.21)),
    "firetruck": ("firetruck", 4.10, 3.10, None, 0.0, (0.58, 0.82, 0.68, 0.15)),
    "bus": ("van", 4.80, 3.00, (255, 199, 13), 0.0, (0.55, 0.80, 0.66, 0.15)),
    "icecream": ("van", 3.80, 2.80, (255, 153, 194), 0.0, (0.55, 0.80, 0.66, 0.15)),
    "monster": ("suv", 3.50, 2.30, (31, 115, 242), 0.7, (0.36, 0.64, 0.68, 0.19)),
    "monster2": ("suv-luxury", 3.50, 2.30, (51, 184, 64), 0.7, (0.36, 0.64, 0.68, 0.19)),
}

# Backwards compatible alias: older code / docs refer to the table as VEHICLES.
VEHICLES = ENGINE

WHEEL_NAMES = ("wheel-front-left", "wheel-front-right", "wheel-back-left", "wheel-back-right")


# ---------------------------------------------------------------- helpers
def _mat(name: str, rgb: Tuple[float, float, float], rough: float = 0.4) -> bpy.types.Material:
    """Simple untextured Principled material."""
    key = f"kenney_{name}"
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


def _meshes() -> List[bpy.types.Object]:
    """All mesh objects in the scene."""
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


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


def _bbox(objs: List[bpy.types.Object]) -> Tuple[List[float], List[float]]:
    """World-space axis-aligned bbox of objs as [[minx,miny,minz],[maxx,maxy,maxz]]."""
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], w[i])
                hi[i] = max(hi[i], w[i])
    return lo, hi


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


def _add_eyes(body_objs: List[bpy.types.Object], bbox: Tuple[List[float], List[float]],
              spec: Tuple[float, float, float, float]) -> List[bpy.types.Object]:
    """Add two cartoon eyes on the camera-side body face (y = bbox_min_y + 0.02)."""
    lo, hi = bbox
    fa, fb, fz, fr = spec
    length = hi[0] - lo[0]
    height = hi[2] - lo[2]
    radius = max(1e-3, fr * height)
    ey = lo[1] + 0.02
    ez = lo[2] + fz * height
    white = _mat("eye_white", (0.95, 0.95, 0.95), 0.3)
    black = _mat("eye_black", (0.01, 0.01, 0.012), 0.2)
    eyes: List[bpy.types.Object] = []
    for fa_ in (fa, fb):
        ex = lo[0] + fa_ * length
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=20, ring_count=12,
                                             location=(ex, ey, ez))
        eye = bpy.context.object
        eye.scale = (1.0, 0.35, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(white)
        eyes.append(eye)
        # Pupil shifted +x by 0.25*radius.
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius * 0.5, segments=16, ring_count=10,
                                             location=(ex + 0.25 * radius, ey - radius * 0.15, ez))
        pup = bpy.context.object
        pup.scale = (1.0, 0.4, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.shade_smooth()
        pup.data.materials.append(black)
        eyes.append(pup)
        # Tiny glint.
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius * 0.14, segments=10, ring_count=8,
                                             location=(ex + 0.1 * radius, ey - radius * 0.22,
                                                       ez + radius * 0.25))
        glint = bpy.context.object
        glint.data.materials.append(_mat("eye_glint", (1.0, 1.0, 1.0), 0.1))
        eyes.append(glint)
    return eyes


def _find_wheels(meshes: List[bpy.types.Object]) -> List[bpy.types.Object]:
    """Pick the 4 wheel objects (by name, else every mesh whose name contains 'wheel')."""
    out = []
    for o in meshes:
        n = o.name.lower()
        if n in WHEEL_NAMES:                       # exact names only: the suv "wheel-back" is a spare tyre (body part)
            out.append(o)
    return out


def _centre(o: bpy.types.Object) -> List[float]:
    """World-space centre of an object's bounding box (object origins are baked to 0 by transform_apply)."""
    pts = [o.matrix_world @ mathutils.Vector(c) for c in o.bound_box]
    return [sum(p[i] for p in pts) / len(pts) for i in range(3)]


def _recentre_mesh(o: bpy.types.Object) -> None:
    """Translate the mesh data so the wheel's bounding-box centre becomes the origin."""
    off = mathutils.Vector(_centre(o))
    for v in o.data.vertices:
        v.co -= off
    o.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()


# ---------------------------------------------------------------- recolor
def _colormap_image(body_objs: List[bpy.types.Object]) -> Optional[bpy.types.Image]:
    """The image of the first material image texture node found on the body objects."""
    for o in body_objs:
        for slot in o.material_slots:
            m = slot.material
            if m is None or not m.use_nodes:
                continue
            for n in m.node_tree.nodes:
                if n.type == "TEX_IMAGE" and n.image is not None:
                    return n.image
    return None


def _image_np(image: bpy.types.Image) -> np.ndarray:
    """Image pixels as a (h, w, 4) float array (RGBA, linear)."""
    w, h = image.size
    flat = np.empty(w * h * 4, dtype=np.float32)
    image.pixels.foreach_get(flat)
    return flat.reshape(h, w, 4)


def _find_paint(body_objs: List[bpy.types.Object], image: bpy.types.Image) -> Tuple[float, float, float]:
    """Body paint colour as the (h, s, v) with the largest area*saturation over face UV centres."""
    w, h = image.size
    pix = _image_np(image)
    buckets: Dict[Tuple[int, int, int], float] = {}
    for o in body_objs:
        mesh = o.data
        uv = mesh.uv_layers.active
        if uv is None:
            continue
        for poly in mesh.polygons:
            acc_u = acc_v = 0.0
            n = 0
            for li in poly.loop_indices:
                u, v = uv.data[li].uv
                acc_u += u
                acc_v += v
                n += 1
            if not n:
                continue
            u = (acc_u / n) % 1.0
            v = (acc_v / n) % 1.0
            x = min(w - 1, max(0, int(u * w)))
            y = min(h - 1, max(0, int(v * h)))
            r, g, b = pix[y, x, 0], pix[y, x, 1], pix[y, x, 2]
            hh, ss, vv = colorsys.rgb_to_hsv(float(r), float(g), float(b))
            if ss <= 0.3:
                continue
            key = (int(round(hh * 12)) % 12, int(round(ss * 4)), int(round(vv * 4)))
            buckets[key] = buckets.get(key, 0.0) + 1.0 * ss
    if buckets:
        bh, bs, bv = max(buckets.items(), key=lambda kv: kv[1])[0]
        return (bh / 12.0, bs / 4.0 + 0.125, bv / 4.0 + 0.125)
    # Fallback: the most saturated pixel of the whole image.
    flat = pix.reshape(-1, 4)
    mx = flat[:, :3].max(axis=1)
    mn = flat[:, :3].min(axis=1)
    sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    i = int(np.argmax(sat))
    r, g, b = flat[i, 0], flat[i, 1], flat[i, 2]
    return colorsys.rgb_to_hsv(float(r), float(g), float(b))


def _recolor_paint(body_objs: List[bpy.types.Object], target_rgb: Tuple[int, int, int]) -> None:
    """Rewrite the shared colormap image: every pixel hue-close to the paint gets the target colour."""
    image = _colormap_image(body_objs)
    if image is None:
        print("[export] WARNING recolor: no colormap image found", flush=True)
        return
    paint_h, paint_s, paint_v = _find_paint(body_objs, image)
    tgt_h, tgt_s, tgt_v = colorsys.rgb_to_hsv(target_rgb[0] / 255.0, target_rgb[1] / 255.0,
                                              target_rgb[2] / 255.0)
    pix = _image_np(image)
    rgba = pix.reshape(-1, 4)
    rgb = rgba[:, :3]
    mx = rgb.max(axis=1)
    mn = rgb.min(axis=1)
    delta = mx - mn
    sat = np.where(mx > 1e-6, delta / np.maximum(mx, 1e-6), 0.0)
    val = mx
    # Reverse hue (standard colorsys hsv_to_rgb) for float RGB.
    hue = np.zeros_like(mx)
    nz = delta > 1e-6
    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    idx = nz & (mx == r)
    hue[idx] = ((g[idx] - b[idx]) / delta[idx]) % 6.0
    idx = nz & (mx == g) & (mx != r)
    hue[idx] = (b[idx] - r[idx]) / delta[idx] + 2.0
    idx = nz & (mx == b) & (mx != r) & (mx != g)
    hue[idx] = (r[idx] - g[idx]) / delta[idx] + 4.0
    hue = (hue / 6.0) % 1.0
    # Circular hue distance to the paint hue.
    dh = np.abs(hue - paint_h)
    dh = np.minimum(dh, 1.0 - dh)
    mask = (dh < 0.06) & (sat > 0.25)
    if not mask.any():
        return
    new_s = np.clip(sat * (tgt_s / max(paint_s, 1e-6)), 0.0, 1.0)
    new_v = np.clip(val * (tgt_v / max(paint_v, 1e-6)), 0.0, 1.0)
    # hsv -> rgb for the masked pixels (vectorised, colorsys compatible).
    hh = np.full_like(mx, tgt_h)
    i = (hh * 6.0).astype(np.int64) % 6
    f = hh * 6.0 - np.floor(hh * 6.0)
    p = new_v * (1.0 - new_s)
    q = new_v * (1.0 - f * new_s)
    t = new_v * (1.0 - (1.0 - f) * new_s)
    out_r = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
                      [new_v, q, p, p, t, new_v])
    out_g = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
                      [t, new_v, new_v, q, p, p])
    out_b = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
                      [p, p, t, new_v, new_v, q])
    rgb[mask, 0] = out_r[mask]
    rgb[mask, 1] = out_g[mask]
    rgb[mask, 2] = out_b[mask]
    rgba[:, :3] = rgb
    pix = rgba.reshape(pix.shape)
    image.pixels.foreach_set(pix.reshape(-1).astype(np.float32))
    image.update()
    image.pack()


# ---------------------------------------------------------------- topper
def _add_icecream_topper(bbox: Tuple[List[float], List[float]]) -> List[bpy.types.Object]:
    """Vanilla cone + two scoops on the roof centre of the icecream van."""
    lo, hi = bbox
    cx = (lo[0] + hi[0]) / 2.0
    cz = hi[2] + 0.45
    cone_mat = _mat("topper_cone", (0.85, 0.62, 0.32), 0.5)
    pink = _mat("topper_pink", (1.0, 0.55, 0.75), 0.5)
    cream = _mat("topper_cream", (0.98, 0.95, 0.9), 0.5)
    out: List[bpy.types.Object] = []
    bpy.ops.mesh.primitive_cone_add(radius1=0.38, depth=0.8, vertices=20, location=(cx, 0.0, cz), rotation=(math.pi, 0.0, 0.0))
    cone = bpy.context.object
    cone.data.materials.append(cone_mat)
    out.append(cone)
    ring = cone.dimensions[2] / 2.0
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.36, segments=20, ring_count=12,
                                         location=(cx, 0.0, cz + ring + 0.28))
    s1 = bpy.context.object
    s1.data.materials.append(pink)
    bpy.ops.object.shade_smooth()
    out.append(s1)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.36, segments=20, ring_count=12,
                                         location=(cx, 0.0, cz + ring + 0.86))
    s2 = bpy.context.object
    s2.data.materials.append(cream)
    bpy.ops.object.shade_smooth()
    out.append(s2)
    return out


# ---------------------------------------------------------------- per vehicle
def export_vehicle(vk: str, kit_dir: str, outdir: str) -> None:
    """Build body/wheel GLBs + meta JSON for one vehicle id."""
    stem, wb, h, target_rgb, lift, eye_spec = ENGINE[vk]
    bpy.ops.wm.read_factory_settings(use_empty=True)

    imported = _import_car(kit_dir, stem)
    meshes = _rotate_to_front_x(imported)

    wheels = _find_wheels(meshes)
    if len(wheels) != 4:
        print(f"[export] WARNING {vk}: found {len(wheels)} wheel objects, expected 4", flush=True)

    # Wheel centres in the rotated frame.
    centres = [_centre(o) for o in wheels]
    wheel_dim = [list(o.dimensions) for o in wheels]
    wheel_r = max(max(d) for d in wheel_dim) / 2.0 if wheel_dim else 0.0
    wheel_w = min(min(d) for d in wheel_dim) if wheel_dim else 0.0
    front_x = max(c[0] for c in centres) if centres else 0.0
    rear_x = min(c[0] for c in centres) if centres else 0.0
    measured_hub_z = sum(c[2] for c in centres) / len(centres) if centres else 0.0
    track_half = max(abs(c[1]) for c in centres) if centres else 0.0

    body_objs = [o for o in meshes if o not in wheels]
    lo, hi = _bbox(body_objs)

    # Sanity check: front (grill) side should be +X after the rotation.
    if hi[0] <= 0.0:
        print(f"[export] WARNING {vk}: body max x = {hi[0]:.3f} is not > 0 (front may be wrong)", flush=True)

    # Engine driven scale: model wheelbase -> engine wheelbase, and body height -> h.
    s = wb / (front_x - rear_x) if front_x > rear_x else 1.0
    yz_k = h / (hi[2] * s) if hi[2] > 0 else 1.0
    hub_z = -lift / (s * yz_k) if lift > 0 else measured_hub_z

    if target_rgb is not None:
        _recolor_paint(body_objs, target_rgb)

    extra_objs: List[bpy.types.Object] = []
    if vk == "icecream":
        extra_objs = _add_icecream_topper((lo, hi))

    eyes = _add_eyes(body_objs, (lo, hi), eye_spec)

    # Body file: body meshes + eyes (+ topper), wheels excluded.
    _select(body_objs + eyes + extra_objs)
    body_path = os.path.join(outdir, f"{vk}_body.glb")
    body_bytes = _export(body_path)

    # Wheel file: the y-most-negative wheel, re-centred at the origin.
    wheel_path = os.path.join(outdir, f"{vk}_wheel.glb")
    wheel_bytes = 0
    if wheels:
        near = min(wheels, key=lambda o: _centre(o)[1])
        _recentre_mesh(near)
        _select([near])
        wheel_bytes = _export(wheel_path)

    # Meta file (Blender coords, world space).
    meta = {
        "vk": vk,
        "cid": vk,
        "wheel_r": wheel_r,
        "wheel_w": wheel_w,
        "wheels": centres,
        "front_x": front_x,
        "rear_x": rear_x,
        "hub_z": hub_z,
        "track_half": track_half,
        "body_bbox": [lo, hi],
        "s": s,
        "yz_k": yz_k,
        "source": "kenney car-kit 3.1 CC0",
    }
    with open(os.path.join(outdir, f"{vk}_meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)

    print(f"[export] {vk} body={body_bytes} wheel={wheel_bytes}", flush=True)


def main() -> None:
    """Parse args after `--` and export the requested vehicles."""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(description="Kenney car-kit -> body/wheel GLB exporter")
    ap.add_argument("--kit", required=True, help="folder with kenney GLB files")
    ap.add_argument("--ids", default=",".join(ENGINE),
                    help="comma separated vehicle ids, or 'all'")
    ap.add_argument("--outdir", required=True, help="output folder")
    args = ap.parse_args(argv)

    os.makedirs(args.outdir, exist_ok=True)
    ids = [s.strip() for s in args.ids.split(",") if s.strip()]
    if len(ids) == 1 and ids[0] == "all":
        ids = list(ENGINE)
    for vk in ids:
        if vk not in ENGINE:
            print(f"[export] skip unknown vehicle id {vk!r}", flush=True)
            continue
        export_vehicle(vk, args.kit, args.outdir)


if __name__ == "__main__":
    main()
