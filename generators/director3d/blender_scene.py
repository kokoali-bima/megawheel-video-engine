"""director3d step 2 — build the 3D race scene from motion.json and render a frame range (inside Blender).

  blender -b -P generators/director3d/blender_scene.py -- --motion work/director3d/demo/motion.json \
      --aspect horizontal|vertical --frame-start 1 --frame-end 450 --outdir /tmp/frames [--gpu] [--samples 16]

Scene is kept light for fast renders: kerbs / lane dashes / finish line are merged meshes, trees are
collection instances of one prototype, cars come from ../blender3d/cast3d.py (wheels spin on pivots).
"""
import argparse
import json
import math
import os
import sys
import time

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "blender3d"))
import cast3d  # noqa: E402

RES = {"horizontal": (1920, 1080, 28), "vertical": (1080, 1920, 24)}     # width, height, lens (mm)


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--motion", required=True)
    ap.add_argument("--aspect", default="horizontal", choices=list(RES))
    ap.add_argument("--frame-start", type=int, default=1)
    ap.add_argument("--frame-end", type=int, default=0, help="0 = last frame")
    ap.add_argument("--outdir", default="/tmp/frames")
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--still", default="", help="render only this frame number to <outdir>/still.png")
    return ap.parse_args(argv)


def mesh_from_quads(name, quads, material, z=0.02):
    verts, faces = [], []
    for q in quads:
        base = len(verts)
        verts += [(x, y, z) for x, y in q]
        faces.append(tuple(range(base, base + len(q))))
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(material)
    return o


def edge(p, d):
    x, y, a = p
    return x - math.sin(a) * d, y + math.cos(a) * d


def build_track(m):
    pts, w = m["track"]["points"], m["track"]["width"]
    mat = cast3d.mat
    road, red, white = [], [], []
    dashes = []
    for i in range(len(pts) - 1):
        p0, p1 = pts[i], pts[i + 1]
        road.append([edge(p0, w / 2), edge(p0, -w / 2), edge(p1, -w / 2), edge(p1, w / 2)])
        for side in (1, -1):
            e0, e1 = w / 2 * side, (w / 2 + 0.9) * side
            (red if i % 2 else white).append([edge(p0, e0), edge(p0, e1), edge(p1, e1), edge(p1, e0)])
        if i % 2 == 0:
            for dl in (-2.5, 2.5):
                dashes.append([edge(p0, dl - 0.12), edge(p0, dl + 0.12), edge(p1, dl + 0.12), edge(p1, dl - 0.12)])
    mesh_from_quads("road", road, mat("asphalt", (0.05, 0.05, 0.055), 0.8), z=0.02)
    mesh_from_quads("kerb_red", red, mat("kerb_red", (0.7, 0.04, 0.03), 0.5), z=0.03)
    mesh_from_quads("kerb_white", white, mat("kerb_white", (0.85, 0.85, 0.85), 0.5), z=0.03)
    mesh_from_quads("dashes", dashes, mat("line", (0.9, 0.9, 0.9), 0.4), z=0.028)
    fx, fy, fa = m["track"]["finish"]                                # checkered finish line
    blk, wht = [], []
    for row in range(2):
        for k in range(int(w)):
            d0 = -w / 2 + k
            ax, ay = fx + math.cos(fa) * row, fy + math.sin(fa) * row
            q = [edge((ax, ay, fa), d0), edge((ax, ay, fa), d0 + 1),
                 edge((ax + math.cos(fa), ay + math.sin(fa), fa), d0 + 1), edge((ax + math.cos(fa), ay + math.sin(fa), fa), d0)]
            (blk if (k + row) % 2 else wht).append(q)
    mesh_from_quads("finish_b", blk, mat("chk_b", (0.02, 0.02, 0.02), 0.5), z=0.032)
    mesh_from_quads("finish_w", wht, mat("chk_w", (0.9, 0.9, 0.9), 0.5), z=0.032)
    for i, ring in enumerate(m["puddles"]):
        mesh_from_quads(f"puddle{i}", [[tuple(p) for p in ring]], mat("water", (0.04, 0.14, 0.32), 0.05), z=0.035)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx, cy, size = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(max(xs) - min(xs), max(ys) - min(ys)) + 260
    bpy.ops.mesh.primitive_plane_add(size=size, location=(cx, cy, 0))
    bpy.context.object.data.materials.append(mat("grass", (0.07, 0.3, 0.05), 0.9))


def build_trees(m):
    proto = bpy.data.collections.new("tree_proto")                  # not linked to the scene: instances only
    mat = cast3d.mat
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=2.4, vertices=8, location=(0, 0, 1.2))
    trunk = bpy.context.object
    trunk.data.materials.append(mat("trunk", (0.25, 0.14, 0.06), 0.8))
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1.0, subdivisions=1, location=(0, 0, 3.2))
    crown = bpy.context.object
    crown.scale = (1.5, 1.5, 1.35)
    crown.data.materials.append(mat("leaf", (0.06, 0.32, 0.08), 0.8))
    for o in (trunk, crown):
        for col in list(o.users_collection):
            col.objects.unlink(o)
        proto.objects.link(o)
    for i, (x, y, r) in enumerate(m["trees"]):
        inst = bpy.data.objects.new(f"tree{i}", None)
        inst.instance_type, inst.instance_collection = "COLLECTION", proto
        inst.location = (x, y, 0)
        inst.scale = (r / 1.8,) * 3
        bpy.context.collection.objects.link(inst)


def animate_cars(m):
    colors = cast3d.cast_colors()
    for car in m["cars"]:
        root = cast3d.build(car["id"], colors)
        root.rotation_mode = "XYZ"                                   # roll(X), pitch(Y) in body frame, then yaw(Z)
        wheels = cast3d.wheel_pivots(root)
        for f, (x, y, yaw, roll, pitch, bounce, wheel, speed) in enumerate(car["frames"], start=1):
            root.location = (x, y, bounce)
            root.rotation_euler = (roll, -pitch, yaw)
            root.keyframe_insert("location", frame=f)
            root.keyframe_insert("rotation_euler", frame=f)
            for w in wheels:
                w.rotation_euler = (0, wheel, 0)
                w.keyframe_insert("rotation_euler", index=1, frame=f)


def cameras(m, aspect):
    wpx, hpx, lens = RES[aspect]
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = wpx, hpx, 100
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.data.lens = lens
    look = bpy.data.objects.new("look", None)
    bpy.context.collection.objects.link(look)
    tc = cam.constraints.new("TRACK_TO")
    tc.target, tc.track_axis, tc.up_axis = look, "TRACK_NEGATIVE_Z", "UP_Y"
    for f, (cx, cy, cz, lx, ly, lz) in enumerate(m["cams"][aspect], start=1):
        cam.location, look.location = (cx, cy, cz), (lx, ly, lz)
        cam.keyframe_insert("location", frame=f)
        look.keyframe_insert("location", frame=f)
    sc.camera = cam


def world_and_render(samples, gpu, fps):
    sc = bpy.context.scene
    sc.render.fps = fps
    sc.render.engine = "CYCLES"
    w = bpy.data.worlds.new("sky")
    sc.world = w
    w.use_nodes = True
    rgb = w.node_tree.nodes.new("ShaderNodeRGB")
    rgb.outputs[0].default_value = (0.42, 0.6, 0.9, 1)
    w.node_tree.links.new(rgb.outputs[0], w.node_tree.nodes["Background"].inputs["Color"])
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(215)))
    sun = bpy.context.object.data
    sun.energy, sun.color, sun.angle = 3.2, (1.0, 0.93, 0.82), math.radians(2)
    sc.view_settings.view_transform, sc.view_settings.look = "Standard", "None"
    c = sc.cycles
    c.samples, c.use_adaptive_sampling, c.adaptive_threshold, c.use_denoising = samples, True, 0.05, True
    c.max_bounces, c.diffuse_bounces, c.glossy_bounces, c.transmission_bounces = 4, 2, 2, 2
    c.volume_bounces, c.transparent_max_bounces = 0, 4
    c.caustics_reflective = c.caustics_refractive = False
    sc.render.use_persistent_data = True
    sc.render.use_motion_blur, sc.render.motion_blur_shutter = True, 0.35    # smooth wheels / fast passes
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
                except (AttributeError, TypeError):
                    pass
                print(f"[scene] GPU backend {kind}: {[d.name for d in devs]}", flush=True)
                break
            except TypeError:
                continue


def main():
    a = args()
    with open(a.motion) as fh:
        m = json.load(fh)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    t0 = time.time()
    world_and_render(a.samples, a.gpu, m["fps"])
    build_track(m)
    build_trees(m)
    animate_cars(m)
    cameras(m, a.aspect)
    sc = bpy.context.scene
    f1 = a.frame_end or m["frames"]
    sc.frame_start, sc.frame_end = a.frame_start, f1
    build = time.time() - t0
    os.makedirs(a.outdir, exist_ok=True)
    t1 = time.time()
    if a.still:
        sc.frame_set(int(a.still))
        sc.render.filepath = os.path.join(a.outdir, "still.png")
        bpy.ops.render.render(write_still=True)
        n = 1
    else:
        sc.render.filepath = os.path.join(a.outdir, "frame_")
        sc.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(animation=True)
        n = f1 - a.frame_start + 1
    print(f"[scene] aspect={a.aspect} frames={n} samples={a.samples} gpu={a.gpu} build={build:.1f}s "
          f"render={time.time() - t1:.1f}s ({(time.time() - t1) / n:.2f}s/frame)", flush=True)


main()
