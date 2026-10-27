"""Export the cast cars as glTF binaries (body + one wheel + meta) for the 3D Challenge Short.

Run with Blender:
  blender -b -P export_cast_glb.py -- --cast-dir DIR --ids sports,police,... --outdir OUT

`--cast-dir` is the folder that contains `cast3d.py`; it is put on sys.path so the procedural
builders and `cast/characters.json` (found through cast3d's own ROOT) are used as-is.
Implements Part 1 of CONTRACT.md: only the car is replaced, the rest of the short stays 2D.
"""
import argparse
import json
import math
import os
import sys

import bpy
import bmesh


EXPORT_OPTS = dict(export_format="GLB", use_selection=True, export_apply=True, export_yup=True,
                   export_cameras=False, export_lights=False)


# ---------------------------------------------------------------- scene helpers
def clean_scene() -> None:
    """Start every vehicle from an empty factory scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cast3d_mod = sys.modules.get("cast3d")
    if cast3d_mod is not None:                 # cast3d caches materials/fonts that the reset just deleted
        cast3d_mod._MATS.clear()
        cast3d_mod._FONT[0] = None


def deselect_all() -> None:
    for o in bpy.context.scene.objects:
        o.select_set(False)


def select_objects(objs: list) -> None:
    """Deselect everything, select exactly `objs` and make the first one active."""
    deselect_all()
    if not objs:
        return
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]


def descendant_meshes(objs: list) -> list:
    """All MESH objects in `objs` or below them (empties have no geometry)."""
    out = []
    for o in objs:
        for d in o.children_recursive:
            if d.type == "MESH" and d not in out:
                out.append(d)
    return out


def convert_curves_to_meshes(objs: list) -> None:
    """CURVE/FONT objects (text decals, the smile) must become meshes before export."""
    curves = [d for o in objs for d in o.children_recursive if d.type in ("CURVE", "FONT")]
    if not curves:
        return
    deselect_all()
    for o in curves:
        o.select_set(True)
    bpy.context.view_layer.objects.active = curves[0]
    bpy.ops.object.convert(target="MESH")


def is_in_wheel(obj, pivots: list) -> bool:
    """True if `obj` lives inside one of the wheel pivots."""
    for p in pivots:
        if obj is p or p in obj.parent_recursive if hasattr(obj, "parent_recursive") else False:
            return True
    # explicit parent walk (parent_recursive is not a stable API across versions)
    parent = obj.parent
    while parent is not None:
        if parent in pivots:
            return True
        parent = parent.parent
    return False


def world_bbox(objs: list) -> list:
    """Axis-aligned bounds of `objs` in world space (Blender coords), or zeros when empty."""
    if not objs:
        return [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for o in objs:
        for corner in o.bound_box:
            p = o.matrix_world @ __import__("mathutils").Vector(corner)
            for i in range(3):
                lo[i] = min(lo[i], p[i])
                hi[i] = max(hi[i], p[i])
    return [[round(v, 4) for v in lo], [round(v, 4) for v in hi]]


def tyre_width(pivot) -> float:
    """Tyre width = max Y extent of the tyre cylinder among the pivot's children."""
    best = 0.0
    for d in pivot.children_recursive:
        if d.type != "MESH":
            continue
        ys = [(d.matrix_world @ __import__("mathutils").Vector(c))[1] for c in d.bound_box]
        best = max(best, max(ys) - min(ys))
    return round(best, 4)


# ---------------------------------------------------------------- per-vehicle export
def body_objects(root, pivots: list) -> list:
    """Mesh objects under root that are not inside a wheel pivot."""
    out = []
    for d in root.children_recursive:
        if d.type != "MESH":
            continue
        if any(d is p or _has_parent(d, p) for p in pivots):
            continue
        out.append(d)
    return out


def _has_parent(obj, pivot) -> bool:
    p = obj.parent
    while p is not None:
        if p is pivot:
            return True
        p = p.parent
    return False


def export_glb(objs: list, path: str) -> int:
    """Select exactly `objs` and write a GLB; returns the file size in bytes."""
    select_objects(objs)
    bpy.ops.export_scene.gltf(filepath=path, **EXPORT_OPTS)
    return os.path.getsize(path)


def wheel_objects(root, pivots: list) -> tuple:
    """Pick the camera-side pivot (negative Y) and return (pivot, body objects of it)."""
    if not pivots:
        return None, []
    pivot = min(pivots, key=lambda p: p.matrix_world.translation.y)
    return pivot, [d for d in pivot.children_recursive if d.type == "MESH"]


def recentre_children(pivot) -> None:
    """Un-parent the pivot's children (keeping their world transform) and move them to the origin."""
    loc = pivot.matrix_world.translation.copy()
    for child in list(pivot.children):
        mw = child.matrix_world.copy()
        child.parent = None
        child.matrix_world = mw
        child.matrix_world.translation -= loc


def export_vehicle(cast3d, vk: str, cid: str, outdir: str) -> dict:
    """Build one vehicle, export body + wheel GLB and write its meta file."""
    clean_scene()
    root = cast3d.build(cid)
    pivots = cast3d.wheel_pivots(root)

    convert_curves_to_meshes([root])
    pivots = cast3d.wheel_pivots(root)  # convert may have replaced curve objects only, but re-read anyway

    centres = [[round(c, 4) for c in p.matrix_world.translation] for p in pivots]
    wheel_r = round(pivots[0]["radius"], 4) if pivots else 0.0
    wheel_w = tyre_width(pivots[0]) if pivots else 0.0

    # body: everything that is not a wheel
    body = body_objects(root, pivots)
    bbox = world_bbox(body)
    body_path = os.path.join(outdir, f"{vk}_body.glb")
    body_bytes = export_glb(body, body_path)

    # wheel: one camera-side pivot, re-centred at the origin
    pivot, wmesh = wheel_objects(root, pivots)
    wheel_bytes = 0
    wheel_path = os.path.join(outdir, f"{vk}_wheel.glb")
    if pivot is not None and wmesh:
        recentre_children(pivot)
        wheel_bytes = export_glb(wmesh, wheel_path)

    meta = {
        "vk": vk,
        "cid": cid,
        "wheel_r": wheel_r,
        "wheel_w": wheel_w,
        "wheels": centres,
        "front_x": round(max((c[0] for c in centres), default=0.0), 4),
        "rear_x": round(min((c[0] for c in centres), default=0.0), 4),
        "hub_z": round(centres[0][2], 4) if centres else 0.0,
        "track_half": round(max((abs(c[1]) for c in centres), default=0.0), 4),
        "body_bbox": bbox,
    }
    with open(os.path.join(outdir, f"{vk}_meta.json"), "w") as fh:
        json.dump(meta, fh, indent=1)

    print(f"[export] {vk} body={body_bytes} wheel={wheel_bytes}", flush=True)
    return meta


# ---------------------------------------------------------------- entry point
def load_id_map(cast3d) -> dict:
    """vehicle_id -> cast3d id, read from characters.json next to cast3d.CAST_FILE."""
    with open(cast3d.CAST_FILE) as fh:
        chars = json.load(fh)["characters"]
    return {c["vehicle_id"]: c["id"] for c in chars if c.get("vehicle_id")}


def main(argv: list) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cast-dir", required=True)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args(argv)

    sys.path.insert(0, os.path.abspath(args.cast_dir))
    import cast3d  # noqa: E402  (needs the cast dir on sys.path first)

    ids = [v.strip() for v in args.ids.split(",") if v.strip()]
    os.makedirs(args.outdir, exist_ok=True)
    vmap = load_id_map(cast3d)
    for vk in ids:
        cid = vmap.get(vk, vk)
        export_vehicle(cast3d, vk, cid, args.outdir)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    main(argv)
