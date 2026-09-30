"""Blender benchmark scene for the MegaWheel Arena 3D mode (quality + speed test, NOT an episode).

Still frame:   blender -b -P generators/blender3d/bench_scene.py -- --engine CYCLES --samples 16 --out x.png
Animation:     ... -- --engine CYCLES --gpu --frame-start 1 --frame-end 90 --outdir /tmp/frames
  engines: CYCLES | BLENDER_EEVEE | BLENDER_WORKBENCH
Assets: Kenney Car Kit (CC0). Folder from env MW_GLB_DIR, default assets/kenney_car_kit/Models/GLB format/.
"""
import argparse
import math
import os
import sys
import time

import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GLB = os.environ.get("MW_GLB_DIR", os.path.join(ROOT, "assets", "kenney_car_kit", "Models", "GLB format"))
FPS = 30
STEP = 1.5                      # centreline sample spacing (m)


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="CYCLES")
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--res", type=float, default=1.0, help="resolution scale (1.0 = 1080x1920)")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "blender3d", "bench.png"))
    ap.add_argument("--frame-start", type=int, default=0, help="0 = still frame")
    ap.add_argument("--frame-end", type=int, default=0)
    ap.add_argument("--outdir", default=os.path.join(ROOT, "work", "blender3d", "frames"))
    return ap.parse_args(argv)


def mat(name, rgb, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    m.diffuse_color = (*rgb, 1)                                  # Workbench uses the viewport colour
    return m


def box(name, size, loc, material, rot_z=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0, 0, rot_z))
    o = bpy.context.object
    o.name = name
    o.scale = size
    o.data.materials.append(material)
    return o


def road_points(n=140):
    """Gentle S-curve centreline going +Y: list of (x, y, heading)."""
    pts, x, y = [], 0.0, -20.0
    for i in range(n):
        a = math.pi / 2 + 0.35 * math.sin(i / 90 * 2 * math.pi)
        x, y = x + math.cos(a) * STEP, y + math.sin(a) * STEP
        pts.append((x, y, a))
    return pts


def along(pts, s, lat=0.0):
    """Point + heading at arc length s (m) and lateral offset lat (+ = left)."""
    f = min(max(s / STEP, 0.0), len(pts) - 1.001)
    i, t = int(f), f - int(f)
    (x0, y0, a0), (x1, y1, a1) = pts[i], pts[i + 1]
    x, y, a = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, a0 + (a1 - a0) * t
    return x - math.sin(a) * lat, y + math.cos(a) * lat, a


def build_road(pts, width=12.0):
    asphalt = mat("asphalt", (0.045, 0.045, 0.05), rough=0.8)
    red, white = mat("kerb_red", (0.7, 0.04, 0.03), 0.5), mat("kerb_white", (0.85, 0.85, 0.85), 0.5)
    line = mat("line", (0.9, 0.9, 0.9), 0.4)
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
        nx, ny = -math.sin(a), math.cos(a)
        for side in (1, -1):
            box(f"kerb{i}{side}", (1.6, 0.9, 0.12), (x + nx * side * (width / 2 + 0.45), y + ny * side * (width / 2 + 0.45),
                                                    0.06), red if i % 2 else white, rot_z=a)
        if i % 4 < 2:
            box(f"dash{i}", (1.5, 0.18, 0.02), (x, y, 0.035), line, rot_z=a)


def trees(pts, width=12.0):
    trunk, leaf, leaf2 = mat("trunk", (0.25, 0.14, 0.06)), mat("leaf", (0.05, 0.3, 0.07)), mat("leaf2", (0.1, 0.42, 0.1))
    for i in range(0, len(pts), 6):
        x, y, a = pts[i]
        for side in (1, -1):
            d = width / 2 + 5 + (i * 7 % 9)
            px, py = x - math.sin(a) * side * d, y + math.cos(a) * side * d
            bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=2.2, location=(px, py, 1.1), vertices=8)
            bpy.context.object.data.materials.append(trunk)
            bpy.ops.mesh.primitive_ico_sphere_add(radius=1.6, location=(px, py, 3.0), subdivisions=1)
            bpy.context.object.data.materials.append(leaf if i % 2 else leaf2)


def import_car(name, length=4.4):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(GLB, f"{name}.glb"))
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(f"car_{name}", None)
    bpy.context.collection.objects.link(root)
    for o in new:
        if o.parent is None:
            o.parent = root
    bpy.context.view_layer.update()
    mins, maxs = Vector((1e9,) * 3), Vector((-1e9,) * 3)
    for o in new:
        if o.type == "MESH":
            for c in o.bound_box:
                w = o.matrix_world @ Vector(c)
                mins, maxs = Vector(map(min, mins, w)), Vector(map(max, maxs, w))
    size = maxs - mins
    s = length / max(size.x, size.y)
    root.scale = (s, s, s)
    return root


def setup_world(engine, samples, res, gpu):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = int(1080 * res), int(1920 * res)
    sc.render.resolution_percentage = 100
    sc.render.fps = FPS
    sc.render.engine = engine
    w = bpy.data.worlds.new("sky")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    grad = nt.nodes.new("ShaderNodeRGB")                        # soft blue sky fill (no blown-out sky)
    grad.outputs[0].default_value = (0.42, 0.6, 0.9, 1)
    nt.links.new(grad.outputs[0], nt.nodes["Background"].inputs["Color"])
    nt.nodes["Background"].inputs["Strength"].default_value = 0.35
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(215)))
    sun = bpy.context.object.data
    sun.energy = 3.2
    sun.color = (1.0, 0.93, 0.82)
    sun.angle = math.radians(2)
    sc.view_settings.view_transform = "Standard"                # punchy cartoon colours (AgX/Filmic look washed out)
    sc.view_settings.look = "None"
    if engine == "CYCLES":
        c = sc.cycles
        c.samples = samples
        c.use_adaptive_sampling = True
        c.adaptive_threshold = 0.05
        c.use_denoising = True
        c.max_bounces, c.diffuse_bounces, c.glossy_bounces = 4, 2, 2
        c.transmission_bounces, c.volume_bounces, c.transparent_max_bounces = 2, 0, 4
        c.caustics_reflective = c.caustics_refractive = False
        sc.render.use_persistent_data = True                    # keep BVH/textures between frames
        if gpu:
            prefs = bpy.context.preferences.addons["cycles"].preferences
            for kind in ("OPTIX", "CUDA"):
                try:
                    prefs.compute_device_type = kind
                    prefs.get_devices()
                    devs = [d for d in prefs.devices if d.type == kind]
                    if not devs:
                        continue
                    for d in prefs.devices:
                        d.use = d.type == kind
                    c.device = "GPU"
                    try:
                        c.denoiser = "OPTIX" if kind == "OPTIX" else "OPENIMAGEDENOISE"
                        c.denoising_use_gpu = True
                    except (AttributeError, TypeError):
                        pass
                    print(f"[bench] GPU backend {kind}: {[d.name for d in devs]}", flush=True)
                    break
                except TypeError:
                    continue
    elif engine == "BLENDER_WORKBENCH":
        sh = sc.display.shading
        sh.light = "STUDIO"
        sh.color_type = "MATERIAL"
        sh.show_shadows = True
        sh.show_cavity = True
    else:
        try:
            sc.eevee.taa_render_samples = samples
        except AttributeError:
            pass


def animate(pts, cars, cam, f0, f1):
    """Cars race along the road (different speeds, lanes); camera follows the pack from above/behind."""
    for f in range(f0, f1 + 1):
        t = (f - 1) / FPS
        ss = []
        for obj, s0, v, lat in cars:
            s = s0 + v * t
            x, y, a = along(pts, s, lat)
            obj.location = (x, y, 0)
            obj.rotation_euler = (0, 0, a + math.pi / 2)            # Kenney models face -Y; + pi/2 -> drive forward
            obj.keyframe_insert("location", frame=f)
            obj.keyframe_insert("rotation_euler", frame=f)
            ss.append(s)
        cs = sum(ss) / len(ss) - 11.0
        x, y, a = along(pts, cs, 0)
        cam.location = (x, y, 9.5)
        cam.rotation_euler = (math.radians(55), 0, a - math.pi / 2)
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)


def main():
    a = args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    t0 = time.time()
    setup_world(a.engine, a.samples, a.res, a.gpu)
    bpy.ops.mesh.primitive_plane_add(size=500, location=(0, 90, 0))
    bpy.context.object.data.materials.append(mat("grass", (0.07, 0.3, 0.05), rough=0.9))
    pts = road_points()
    build_road(pts)
    trees(pts)
    x, y, _ = along(pts, 72, 1.8)                               # puddle on the racing line
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=0.02, location=(x, y, 0.04), vertices=32)
    pud = bpy.context.object
    pud.scale = (2.4, 4.0, 1)
    pud.data.materials.append(mat("water", (0.05, 0.16, 0.35), rough=0.08))
    cars = [(import_car("taxi"), 30.0, 17.0, -2.6), (import_car("police"), 36.0, 16.0, 2.4),
            (import_car("race"), 42.0, 15.0, -0.2)]
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.data.lens = 24
    bpy.context.scene.camera = cam
    f0, f1 = (a.frame_start, a.frame_end) if a.frame_start else (1, 1)
    animate(pts, cars, cam, f0, f1)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = f0, f1
    t_build = time.time() - t0
    t1 = time.time()
    if a.frame_start:
        os.makedirs(a.outdir, exist_ok=True)
        sc.render.filepath = os.path.join(a.outdir, "frame_")
        sc.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(animation=True)
        n = f1 - f0 + 1
        print(f"[bench] engine={a.engine} samples={a.samples} gpu={a.gpu} frames={n} build={t_build:.1f}s "
              f"render={time.time() - t1:.1f}s ({(time.time() - t1) / n:.2f}s/frame) -> {a.outdir}", flush=True)
    else:
        sc.frame_set(1)
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        sc.render.filepath = a.out
        bpy.ops.render.render(write_still=True)
        print(f"[bench] engine={a.engine} samples={a.samples} res={a.res} gpu={a.gpu} build={t_build:.1f}s "
              f"render={time.time() - t1:.1f}s -> {a.out}", flush=True)


main()
