"""Blender benchmark scene for the MegaWheel Arena 3D mode (quality + speed test, NOT an episode).

Run on VM 99.3 (CPU, arm64) or on Modal (GPU):
  blender -b -P generators/blender3d/bench_scene.py -- --engine CYCLES --samples 32 --out work/blender3d/bench_cycles.png
  engines: CYCLES | BLENDER_EEVEE_NEXT | BLENDER_WORKBENCH
Assets: Kenney Car Kit (CC0) in assets/kenney_car_kit/Models/GLB format/.
"""
import argparse
import math
import os
import sys
import time

import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GLB = os.path.join(ROOT, "assets", "kenney_car_kit", "Models", "GLB format")


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="CYCLES")
    ap.add_argument("--samples", type=int, default=32)
    ap.add_argument("--res", type=float, default=1.0, help="resolution scale (1.0 = 1080x1920)")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "blender3d", "bench.png"))
    return ap.parse_args(argv)


def mat(name, rgb, rough=0.6, metal=0.0, emit=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = 2.0
    return m


def box(name, size, loc, material, rot_z=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0, 0, rot_z))
    o = bpy.context.object
    o.name = name
    o.scale = size
    o.data.materials.append(material)
    return o


def road_points(n=90, step=1.5):
    """Gentle S-curve centreline going +Y."""
    pts, x, y, a = [], 0.0, -20.0, math.pi / 2
    for i in range(n):
        a = math.pi / 2 + 0.35 * math.sin(i / n * 2 * math.pi)
        x, y = x + math.cos(a) * step, y + math.sin(a) * step
        pts.append((x, y, a))
    return pts


def build_road(pts, width=12.0):
    asphalt = mat("asphalt", (0.09, 0.09, 0.1), rough=0.85)
    red, white = mat("kerb_red", (0.75, 0.05, 0.04), 0.5), mat("kerb_white", (0.9, 0.9, 0.9), 0.5)
    line = mat("line", (0.95, 0.95, 0.95), 0.4)
    verts, faces = [], []
    for x, y, a in pts:
        nx, ny = -math.sin(a), math.cos(a)
        verts += [(x + nx * width / 2, y + ny * width / 2, 0.02), (x - nx * width / 2, y - ny * width / 2, 0.02)]
    for i in range(len(pts) - 1):
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    me = bpy.data.meshes.new("road")
    me.from_pydata(verts, [], faces)
    o = bpy.data.objects.new("road", me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(asphalt)
    for i, (x, y, a) in enumerate(pts[:-1]):
        for side in (1, -1):
            nx, ny = -math.sin(a), math.cos(a)
            box(f"kerb{i}{side}", (1.6, 0.9, 0.12), (x + nx * side * (width / 2 + 0.45), y + ny * side * (width / 2 + 0.45),
                                                    0.06), red if i % 2 else white, rot_z=a)
        if i % 4 < 2:
            box(f"dash{i}", (1.5, 0.18, 0.02), (x, y, 0.035), line, rot_z=a)


def trees(pts, width=12.0):
    trunk, leaf, leaf2 = mat("trunk", (0.3, 0.18, 0.08)), mat("leaf", (0.12, 0.42, 0.14)), mat("leaf2", (0.2, 0.55, 0.2))
    for i in range(0, len(pts), 7):
        x, y, a = pts[i]
        for side in (1, -1):
            d = width / 2 + 5 + (i * 7 % 9)
            px, py = x - math.sin(a) * side * d, y + math.cos(a) * side * d
            bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=2.2, location=(px, py, 1.1), vertices=8)
            bpy.context.object.data.materials.append(trunk)
            bpy.ops.mesh.primitive_ico_sphere_add(radius=1.6, location=(px, py, 3.0), subdivisions=1)
            bpy.context.object.data.materials.append(leaf if i % 2 else leaf2)


def import_car(name, loc, heading, length=4.4):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(GLB, f"{name}.glb"))
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(f"car_{name}", None)
    bpy.context.collection.objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
    bpy.context.view_layer.update()
    mins = Vector((1e9,) * 3)
    maxs = Vector((-1e9,) * 3)
    for o in new:
        if o.type == "MESH":
            for c in o.bound_box:
                w = o.matrix_world @ Vector(c)
                mins, maxs = Vector(map(min, mins, w)), Vector(map(max, maxs, w))
    size = maxs - mins
    s = length / max(size.x, size.y)
    root.scale = (s, s, s)
    root.location = loc
    root.rotation_euler = (0, 0, heading)
    return root


def setup_world(engine, samples, res, gpu):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = int(1080 * res), int(1920 * res)
    sc.render.resolution_percentage = 100
    sc.render.engine = engine
    w = bpy.data.worlds.new("sky")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    sky = nt.nodes.new("ShaderNodeTexSky")
    try:
        sky.sky_type = "NISHITA"
        sky.sun_elevation = math.radians(28)
        sky.sun_rotation = math.radians(210)
    except (AttributeError, TypeError):
        pass
    nt.links.new(sky.outputs["Color"], nt.nodes["Background"].inputs["Color"])
    nt.nodes["Background"].inputs["Strength"].default_value = 0.6
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(55), 0, math.radians(210)))
    sun = bpy.context.object.data
    sun.energy = 4.0
    sun.color = (1.0, 0.9, 0.78)
    sun.angle = math.radians(3)
    if engine == "CYCLES":
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        sc.cycles.max_bounces = 4
        if gpu:
            prefs = bpy.context.preferences.addons["cycles"].preferences
            for kind in ("OPTIX", "CUDA"):
                try:
                    prefs.compute_device_type = kind
                    prefs.get_devices()
                    for d in prefs.devices:
                        d.use = True
                    sc.cycles.device = "GPU"
                    break
                except TypeError:
                    continue
    elif engine == "BLENDER_WORKBENCH":
        sh = sc.display.shading
        sh.light = "STUDIO"
        sh.color_type = "MATERIAL"
        sh.show_shadows = True
        sh.show_cavity = True
        sc.display.shading.shadow_intensity = 0.5
    else:
        try:
            sc.eevee.taa_render_samples = samples
            sc.eevee.use_shadows = True
        except AttributeError:
            pass
    sc.view_settings.view_transform = "AgX" if "AgX" in [v.identifier for v in
                                                         type(sc.view_settings).bl_rna.properties["view_transform"]
                                                         .enum_items] else "Filmic"


def main():
    a = args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    t0 = time.time()
    setup_world(a.engine, a.samples, a.res, a.gpu)
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 60, 0))
    bpy.context.object.data.materials.append(mat("grass", (0.16, 0.42, 0.12), rough=0.9))
    pts = road_points()
    build_road(pts)
    trees(pts)
    # puddle (glossy water) on the road + 3 cars racing through the S-curve
    px, py, pa = pts[34]
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=0.02, location=(px + 1.5, py, 0.04), vertices=32)
    pud = bpy.context.object
    pud.scale = (2.6, 4.2, 1)
    pud.data.materials.append(mat("water", (0.1, 0.3, 0.55), rough=0.05))
    cars = [("taxi", 22, -2.8), ("police", 26, 2.6), ("race", 31, -0.4)]
    for name, i, lat in cars:
        x, y, ang = pts[i]
        import_car(name, (x - math.sin(ang) * lat, y + math.cos(ang) * lat, 0), ang - math.pi / 2)
    # camera: above/behind, looking down the road (portrait 9:16)
    cx, cy, ca = pts[12]
    bpy.ops.object.camera_add(location=(cx - 2, cy - 14, 13), rotation=(math.radians(58), 0, math.radians(-6)))
    cam = bpy.context.object
    cam.data.lens = 26
    bpy.context.scene.camera = cam
    t_build = time.time() - t0
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    bpy.context.scene.render.filepath = a.out
    t1 = time.time()
    bpy.ops.render.render(write_still=True)
    print(f"[bench] engine={a.engine} samples={a.samples} res={a.res} gpu={a.gpu} build={t_build:.1f}s "
          f"render={time.time() - t1:.1f}s -> {a.out}", flush=True)


main()
