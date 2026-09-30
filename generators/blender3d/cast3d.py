"""MegaWheel Arena — 3D models of the fixed cast (procedural, same colours/traits as the 2D characters).

Every character is built from code (no external assets): body, cabin, wheels, signature details,
cartoon eyes on the windshield and a smile on the front bumper. Colours come from cast/characters.json.
Local axes of every model: +X = forward, +Z = up, origin on the ground at the body centre.

Preview (one render per character + contact sheet):
  blender -b -P generators/blender3d/cast3d.py -- --outdir work/blender3d/cast [--only zippy,rocky] [--samples 16]
In another script:  import cast3d; root = cast3d.build("zippy")
"""
import glob
import json
import math
import os
import sys

import bpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CAST_FILE = os.path.join(ROOT, "cast", "characters.json")
_MATS, _FONT = {}, [None]


# ---------------------------------------------------------------- helpers
def lin(c):
    """sRGB 0-255 -> linear 0-1 (Blender colours are linear)."""
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def cast_colors():
    with open(CAST_FILE) as fh:
        return {c["id"]: tuple(lin(v) for v in c["color_rgb"]) for c in json.load(fh)["characters"]}


def mat(name, rgb, rough=0.45, metal=0.0, coat=0.0, emit=0.0):
    key = (name, rgb, rough, metal, coat, emit)
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    for k, v in (("Base Color", (*rgb, 1)), ("Roughness", rough), ("Metallic", metal), ("Coat Weight", coat)):
        try:
            b.inputs[k].default_value = v
        except KeyError:
            pass
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    m.diffuse_color = (*rgb, 1)
    _MATS[key] = m
    return m


RUBBER = ((0.018, 0.018, 0.02), 0.8)
GLASS = ((0.16, 0.32, 0.5), 0.08)
CHROME = ((0.8, 0.8, 0.82), 0.15, 1.0)
WHITE = (0.85, 0.85, 0.85)
BLACK = (0.01, 0.01, 0.012)


def _parent(o, root, loc=None):
    o.parent = root
    if loc is not None:
        o.location = loc
    return o


def rbox(root, size, loc, m, bevel=0.06, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bv = o.modifiers.new("bevel", "BEVEL")
        bv.width, bv.segments, bv.limit_method = bevel, 3, "ANGLE"
    o.rotation_euler = rot
    o.data.materials.append(m)
    return _parent(o, root, loc)


def cyl(root, r, depth, loc, m, rot=(math.pi / 2, 0, 0), verts=24, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=verts, location=(0, 0, 0))
    o = bpy.context.object
    o.rotation_euler = rot
    if bevel:
        bv = o.modifiers.new("bevel", "BEVEL")
        bv.width, bv.segments = bevel, 2
    o.data.materials.append(m)
    return _parent(o, root, loc)


def sphere(root, r, loc, m, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=24, ring_count=12, location=(0, 0, 0))
    o = bpy.context.object
    o.scale = scale
    o.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return _parent(o, root, loc)


def wheel(root, x, y, r, width, monster=False):
    """Wheel on its own pivot empty ("wheelpivot*", at the axle) so animation can spin it about local Y."""
    piv = bpy.data.objects.new(f"wheelpivot_{x:+.2f}_{y:+.2f}", None)
    bpy.context.collection.objects.link(piv)
    _parent(piv, root, (x, y, r))
    piv["radius"] = r
    side = 1 if y > 0 else -1
    tire = cyl(piv, r, width, (0, 0, 0), mat("rubber", *RUBBER), verts=32 if not monster else 20, bevel=r * 0.12)
    cyl(piv, r * 0.55, 0.04, (0, side * width / 2, 0), mat("hub", *CHROME), verts=24)
    cyl(piv, r * 0.18, 0.06, (0, side * (width / 2 + 0.02), 0), mat("hubcap", (0.15, 0.15, 0.17), 0.4))
    for k in range(5):                                           # spokes: make the rotation visible
        a = 2 * math.pi * k / 5
        rbox(piv, (r * 0.34, 0.03, r * 0.09), (math.cos(a) * r * 0.3, side * (width / 2 + 0.025), math.sin(a) * r * 0.3),
             mat("spoke", (0.3, 0.3, 0.33), 0.35, metal=0.6), bevel=0, rot=(0, -a, 0))
    if monster:                                                  # chunky tread blocks
        for k in range(14):
            a = 2 * math.pi * k / 14
            rbox(piv, (r * 0.32, width * 1.02, r * 0.16), (math.cos(a) * r * 0.97, 0, math.sin(a) * r * 0.97),
                 mat("rubber", *RUBBER), bevel=0.02, rot=(0, -a + math.pi / 2, 0))
    return piv


def wheel_pivots(root):
    """All wheel pivots of a character (recursive), for animation."""
    return [o for o in root.children_recursive if o.name.startswith("wheelpivot")]


def font():
    if _FONT[0] is None:
        paths = glob.glob("/usr/share/fonts/**/LuckiestGuy*.ttf", recursive=True) + \
            glob.glob(os.path.expanduser("~/.fonts/**/LuckiestGuy*.ttf"), recursive=True) + \
            glob.glob(os.path.expanduser("~/.local/share/fonts/**/LuckiestGuy*.ttf"), recursive=True)
        _FONT[0] = bpy.data.fonts.load(paths[0]) if paths else False
    return _FONT[0] or None


def text(root, s, loc, size, m, side=-1, extrude=0.01):
    """Text on the left (-Y, side=-1) or right (+Y) flank, reading front-to-back direction naturally."""
    cu = bpy.data.curves.new("txt", "FONT")
    cu.body = s
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    cu.size, cu.extrude = size, extrude
    f = font()
    if f:
        cu.font = f
    o = bpy.data.objects.new("txt", cu)
    bpy.context.collection.objects.link(o)
    o.rotation_euler = (math.pi / 2, 0, 0) if side < 0 else (math.pi / 2, 0, math.pi)
    o.data.materials.append(m)
    return _parent(o, root, loc)


def face(root, x, z, width, tilt_deg, eye_r=0.19, mouth=None, look=(0.0, 0.0)):
    """Cartoon eyes on a windshield plane at (x, z) tilted back by tilt_deg; optional smile on the bumper."""
    fr = bpy.data.objects.new("face", None)
    bpy.context.collection.objects.link(fr)
    _parent(fr, root, (x, 0, z))
    fr.rotation_euler = (0, math.radians(tilt_deg), 0)             # tilt_deg = windshield angle from horizontal; local +Z = outward normal, local -X = up the glass
    for side in (-1, 1):
        ey = side * width * 0.24
        sphere(fr, eye_r, (0, ey, 0.02), mat("eye_white", (0.95, 0.95, 0.95), 0.3), scale=(1.0, 0.92, 0.35))
        sphere(fr, eye_r * 0.5, (look[1] * eye_r * 0.3, ey + look[0] * eye_r * 0.35, eye_r * 0.3),
               mat("pupil", BLACK, 0.2), scale=(1, 1, 0.4))
        sphere(fr, eye_r * 0.14, (-eye_r * 0.2, ey - eye_r * 0.15, eye_r * 0.42), mat("glint", (1, 1, 1), 0.1, emit=1.0))
        rbox(fr, (eye_r * 0.35, eye_r * 1.3, 0.05), (-eye_r * 1.25, ey, 0.06), mat("brow", BLACK, 0.5), bevel=0.02,
             rot=(0, 0, side * 0.18))
    if mouth:                                                    # smile arc on the front bumper
        mx, mz, mw = mouth
        cu = bpy.data.curves.new("smile", "CURVE")
        cu.dimensions, cu.bevel_depth, cu.bevel_resolution = "3D", 0.055, 4
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(2)
        for bp, (yy, zz) in zip(sp.bezier_points, ((-mw / 2, 0.08), (0, -0.11), (mw / 2, 0.08))):
            bp.co = (0, yy, zz)
            bp.handle_left_type = bp.handle_right_type = "AUTO"
        o = bpy.data.objects.new("smile", cu)
        bpy.context.collection.objects.link(o)
        o.data.materials.append(mat("mouth", (0.05, 0.02, 0.02), 0.5))
        _parent(o, root, (mx, 0, mz))
        sphere(root, mw * 0.13, (mx - 0.02, 0, mz - 0.06), mat("tongue", (0.9, 0.25, 0.35), 0.4),
               scale=(0.35, 1.3, 0.6))
    return fr


def lights(root, x, z, y_off, rear_x=None):
    for side in (-1, 1):
        sphere(root, 0.11, (x, side * y_off, z), mat("headlight", (1, 0.96, 0.8), 0.2, emit=2.5), scale=(0.4, 1, 1))
        if rear_x is not None:
            rbox(root, (0.05, 0.22, 0.12), (rear_x, side * y_off, z), mat("taillight", (0.9, 0.05, 0.03), 0.3, emit=2),
                 bevel=0.01)


# ---------------------------------------------------------------- the cast
def sedan(root, col, L=4.7, W=2.0, cab_len=2.3, low=False):
    zb, hb = (0.3, 0.52) if low else (0.35, 0.62)
    rbox(root, (L, W, hb), (0, 0, zb + hb / 2), mat("paint", col, 0.3, coat=0.6), bevel=0.12)
    ch = 0.45 if low else 0.55
    cz = zb + hb + ch / 2 - 0.02
    rbox(root, (cab_len, W * 0.86, ch), (-0.25, 0, cz), mat("paint", col, 0.3, coat=0.6), bevel=0.1)
    for side in (-1, 1):                                         # side windows
        rbox(root, (cab_len * 0.8, 0.02, ch * 0.7), (-0.25, side * W * 0.43, cz + 0.02), mat("glass", *GLASS), bevel=0)
    rbox(root, (0.05, W * 0.8, ch * 0.9), (-0.25 + cab_len / 2 + 0.08, 0, cz), mat("glass", *GLASS), bevel=0,
         rot=(0, -math.radians(35), 0))
    r = 0.36 if low else 0.38
    for x in (L * 0.31, -L * 0.31):
        for y in (W / 2 - 0.1, -W / 2 + 0.1):
            wheel(root, x, y, r, 0.3)
    lights(root, L / 2 + 0.01, zb + hb * 0.62, W * 0.36, rear_x=-L / 2 - 0.01)
    rbox(root, (0.12, W * 0.9, 0.16), (L / 2 + 0.02, 0, zb + 0.1), mat("bumper", (0.12, 0.12, 0.13), 0.5), bevel=0.04)
    face(root, -0.25 + cab_len / 2 + 0.12, cz + 0.02, W * 0.8, 55, eye_r=0.27,
         mouth=(L / 2 + 0.05, zb + hb * 0.55, 0.62))
    return zb + hb, cz + ch / 2


def build_zippy(root, col):
    top, roof = sedan(root, col, L=4.4, W=2.0, cab_len=1.9, low=True)
    rbox(root, (4.2, 0.35, 0.02), (0, 0, top + 0.005), mat("stripe", WHITE, 0.3), bevel=0)      # racing stripe
    for y in (-0.6, 0.6):
        rbox(root, (0.08, 0.08, 0.35), (-2.0, y, top + 0.17), mat("post", BLACK, 0.4), bevel=0.01)
    rbox(root, (0.45, 2.0, 0.06), (-2.05, 0, top + 0.37), mat("spoiler", BLACK, 0.4), bevel=0.02)


def build_siren(root, col):
    top, roof = sedan(root, col)
    for side in (-1, 1):
        rbox(root, (2.4, 0.02, 0.28), (0.5, side * 1.005, 0.62), mat("police_blue", (0.02, 0.05, 0.3), 0.35), bevel=0)
    text(root, "POLICE", (0.55, -1.03, 0.63), 0.26, mat("police_txt", WHITE, 0.3))
    rbox(root, (0.35, 1.2, 0.12), (-0.25, 0, roof + 0.06), mat("bar", BLACK, 0.4), bevel=0.02)
    rbox(root, (0.3, 0.5, 0.14), (-0.25, -0.3, roof + 0.16), mat("siren_red", (1, 0.05, 0.05), 0.2, emit=4), bevel=0.03)
    rbox(root, (0.3, 0.5, 0.14), (-0.25, 0.3, roof + 0.16), mat("siren_blue", (0.05, 0.2, 1), 0.2, emit=4), bevel=0.03)


def build_tilly(root, col):
    top, roof = sedan(root, col)
    for k in range(12):                                          # checker band
        for side in (-1, 1):
            rbox(root, (0.2, 0.02, 0.1), (-1.2 + k * 0.2, side * 1.005, 0.74 + (0.1 if k % 2 else 0)),
                 mat("checker", BLACK, 0.4), bevel=0)
    rbox(root, (0.5, 0.9, 0.3), (-0.25, 0, roof + 0.15), mat("taxi_sign", (1, 0.95, 0.6), 0.3, emit=0.8), bevel=0.05)
    text(root, "TAXI", (-0.25, -0.46, roof + 0.15), 0.2, mat("taxi_txt", BLACK, 0.4))


def build_nitro(root, col):
    paint = mat("paint", col, 0.25, coat=0.8)
    rbox(root, (4.6, 0.75, 0.42), (0, 0, 0.36), paint, bevel=0.15)                                # tub + nose
    rbox(root, (1.7, 1.75, 0.38), (-0.6, 0, 0.36), paint, bevel=0.12)                            # sidepods
    rbox(root, (0.55, 2.1, 0.07), (2.2, 0, 0.14), paint, bevel=0.02)                             # front wing
    rbox(root, (0.5, 1.7, 0.08), (-2.2, 0, 1.0), paint, bevel=0.02)                              # rear wing
    rbox(root, (0.12, 0.12, 0.55), (-2.1, 0, 0.7), mat("post", BLACK, 0.4), bevel=0.01)
    rbox(root, (0.9, 0.55, 0.3), (-0.9, 0, 0.72), paint, bevel=0.1)                              # engine cover
    sphere(root, 0.26, (-0.15, 0, 0.78), mat("helmet", (1, 0.84, 0.1), 0.2, coat=1))              # driver helmet
    rbox(root, (0.08, 0.34, 0.1), (0.08, 0, 0.8), mat("visor", (0.05, 0.05, 0.08), 0.1), bevel=0.02)
    for x, r, w in ((1.6, 0.34, 0.38), (-1.55, 0.37, 0.45)):
        for y in (1.0, -1.0):
            wheel(root, x, y, r, w)
    text(root, "1", (-0.6, -0.9, 0.38), 0.3, mat("num", WHITE, 0.3))
    face(root, 1.25, 0.6, 0.72, 20, eye_r=0.18, mouth=(2.3, 0.3, 0.45))


def build_monster(root, col):
    paint = mat("paint", col, 0.3, coat=0.6)
    rbox(root, (4.0, 2.2, 0.75), (0, 0, 2.2), paint, bevel=0.14)                                 # lifted body
    rbox(root, (1.8, 2.0, 0.85), (-0.35, 0, 2.95), paint, bevel=0.12)                            # cab
    for side in (-1, 1):
        rbox(root, (1.4, 0.02, 0.5), (-0.4, side * 1.005, 3.0), mat("glass", *GLASS), bevel=0)
    rbox(root, (0.05, 1.8, 0.7), (0.6, 0, 2.97), mat("glass", *GLASS), bevel=0, rot=(0, -math.radians(25), 0))
    rbox(root, (3.4, 1.6, 0.25), (0, 0, 1.55), mat("frame", (0.1, 0.1, 0.11), 0.5), bevel=0.04)  # chassis
    for x in (1.6, -1.6):
        for side in (-1, 1):
            wheel(root, x, side * 1.45, 1.0, 0.85, monster=True)
            cyl(root, 0.07, 0.9, (x, side * 0.85, 1.55), mat("shock", (0.9, 0.75, 0.1), 0.3, metal=0.6),
                rot=(math.radians(side * 60), 0, 0))
    rbox(root, (0.12, 2.0, 0.12), (-0.35, 0, 3.47), mat("rollbar", BLACK, 0.4), bevel=0.03)
    for side in (-1, 1):
        sphere(root, 0.13, (-0.35, side * 0.7, 3.55), mat("roof_light", (1, 0.95, 0.7), 0.2, emit=3))
    lights(root, 2.01, 2.3, 0.75, rear_x=-2.01)
    face(root, 0.66, 2.98, 1.7, 65, eye_r=0.29, mouth=(2.03, 2.0, 0.9))


def build_buster(root, col):
    paint = mat("paint", col, 0.35, coat=0.3)
    rbox(root, (8.4, 2.5, 2.2), (-0.8, 0, 1.6), paint, bevel=0.15)                               # body
    rbox(root, (1.5, 2.3, 1.1), (4.0, 0, 1.05), paint, bevel=0.15)                               # nose
    for side in (-1, 1):
        for k in range(7):
            rbox(root, (0.85, 0.02, 0.7), (-4.2 + k * 1.1, side * 1.255, 2.05), mat("glass", *GLASS), bevel=0)
        for zz in (1.45, 1.1):
            rbox(root, (8.3, 0.02, 0.06), (-0.8, side * 1.26, zz), mat("stripe", BLACK, 0.4), bevel=0)
    text(root, "SCHOOL BUS", (-0.9, -1.28, 1.27), 0.34, mat("bus_txt", BLACK, 0.4))
    rbox(root, (0.05, 2.2, 1.0), (3.26, 0, 2.15), mat("glass", *GLASS), bevel=0, rot=(0, -math.radians(10), 0))
    for x in (3.6, -3.4):
        for side in (-1, 1):
            wheel(root, x, side * 1.1, 0.55, 0.4)
    rbox(root, (0.3, 0.12, 0.35), (-0.8, 0, 2.78), mat("roof_lamp", (1, 0.4, 0.05), 0.3, emit=2), bevel=0.03)
    lights(root, 4.76, 1.05, 0.8, rear_x=-5.01)
    face(root, 3.3, 2.15, 2.1, 80, eye_r=0.3, mouth=(4.77, 0.75, 1.0))


def build_hydro(root, col):
    paint = mat("paint", col, 0.3, coat=0.5)
    rbox(root, (2.6, 2.4, 2.3), (3.0, 0, 1.65), paint, bevel=0.15)                               # cab
    rbox(root, (6.2, 2.5, 1.8), (-1.4, 0, 1.4), paint, bevel=0.12)                               # body
    for side in (-1, 1):
        rbox(root, (1.6, 0.02, 0.8), (3.2, side * 1.205, 2.1), mat("glass", *GLASS), bevel=0)
        rbox(root, (8.8, 0.02, 0.18), (0.3, side * 1.26, 1.0), mat("stripe", WHITE, 0.3), bevel=0)
        for k in range(4):                                       # equipment doors
            rbox(root, (1.2, 0.02, 0.9), (-3.8 + k * 1.45, side * 1.255, 1.6), mat("door", (0.55, 0.02, 0.02), 0.4),
                 bevel=0)
    text(root, "FIRE", (-1.4, -1.28, 1.6), 0.45, mat("fire_txt", (1, 0.85, 0.2), 0.3))
    for side in (-1, 1):                                         # ladder rails + rungs
        rbox(root, (6.4, 0.08, 0.08), (-1.2, side * 0.45, 2.45), mat("ladder", *CHROME), bevel=0.01)
    for k in range(13):
        rbox(root, (0.06, 0.9, 0.06), (-4.2 + k * 0.5, 0, 2.45), mat("ladder", *CHROME), bevel=0.01)
    rbox(root, (0.35, 1.4, 0.14), (2.9, 0, 2.87), mat("bar", BLACK, 0.4), bevel=0.02)
    rbox(root, (0.3, 0.6, 0.14), (2.9, -0.35, 2.98), mat("siren_red", (1, 0.05, 0.05), 0.2, emit=4), bevel=0.03)
    rbox(root, (0.3, 0.6, 0.14), (2.9, 0.35, 2.98), mat("siren_red2", (1, 0.3, 0.05), 0.2, emit=4), bevel=0.03)
    for x in (3.1, -2.4, -3.6):
        for side in (-1, 1):
            wheel(root, x, side * 1.1, 0.55, 0.42)
    lights(root, 4.31, 1.0, 0.85, rear_x=-4.51)
    face(root, 4.2, 2.2, 2.0, 82, eye_r=0.3, mouth=(4.32, 0.75, 1.0))


def build_titan(root, col):
    paint = mat("paint", col, 0.3, coat=0.5)
    rbox(root, (2.4, 2.5, 2.9), (4.2, 0, 2.05), paint, bevel=0.15)                               # cab
    rbox(root, (1.3, 2.3, 1.4), (5.9, 0, 1.3), paint, bevel=0.15)                                # hood
    for side in (-1, 1):
        rbox(root, (1.3, 0.02, 0.8), (4.5, side * 1.255, 2.7), mat("glass", *GLASS), bevel=0)
        cyl(root, 0.1, 2.2, (3.2, side * 1.1, 3.3), mat("stack", *CHROME), rot=(0, 0, 0), verts=16)
    rbox(root, (0.05, 2.2, 1.0), (5.42, 0, 2.75), mat("glass", *GLASS), bevel=0, rot=(0, -math.radians(8), 0))
    rbox(root, (0.1, 2.0, 1.1), (6.56, 0, 1.3), mat("grille", *CHROME), bevel=0.02)
    rbox(root, (9.2, 2.6, 3.1), (-2.2, 0, 2.75), mat("trailer", (0.8, 0.8, 0.8), 0.4), bevel=0.08)
    text(root, "MEGA HAUL", (-2.2, -1.32, 2.8), 0.75, mat("haul_txt", (0.05, 0.25, 0.75), 0.3))
    for x in (5.7, 3.3, 2.1, -4.6, -5.8):
        for side in (-1, 1):
            wheel(root, x, side * 1.1, 0.55, 0.42)
    lights(root, 6.61, 1.2, 0.85, rear_x=-6.81)
    face(root, 5.47, 2.75, 2.1, 82, eye_r=0.32, mouth=(6.63, 0.75, 1.0))


def build_sprinkles(root, col):
    paint = mat("paint", col, 0.35, coat=0.4)
    mint = mat("mint", (0.45, 0.85, 0.65), 0.4)
    rbox(root, (5.2, 2.4, 2.5), (-0.7, 0, 1.75), paint, bevel=0.15)                              # box body
    rbox(root, (1.6, 2.3, 1.7), (2.6, 0, 1.35), paint, bevel=0.15)                               # cab
    for side in (-1, 1):
        rbox(root, (6.6, 0.02, 0.45), (0.0, side * 1.205, 0.85), mint, bevel=0)
        rbox(root, (1.0, 0.02, 0.6), (2.6, side * 1.155, 1.75), mat("glass", *GLASS), bevel=0)
        rbox(root, (2.0, 0.02, 1.0), (-0.9, side * 1.21, 2.1), mat("hatch", (0.1, 0.05, 0.08), 0.4), bevel=0)
    text(root, "ICE CREAM", (-0.9, -1.24, 1.35), 0.32, mat("ice_txt", (0.95, 0.2, 0.5), 0.3))
    rbox(root, (0.05, 2.1, 0.9), (3.42, 0, 1.8), mat("glass", *GLASS), bevel=0, rot=(0, -math.radians(25), 0))
    cyl(root, 0.36, 0.28, (-0.7, 0, 3.12), mat("holder", (0.95, 0.95, 0.95), 0.4), rot=(0, 0, 0))  # roof holder
    bpy.ops.mesh.primitive_cone_add(radius1=0.38, radius2=0.03, depth=0.95, vertices=20, location=(0, 0, 0),
                                    rotation=(math.pi, 0, 0))    # giant cone on the roof
    cone = bpy.context.object
    cone.data.materials.append(mat("waffle", (0.8, 0.5, 0.2), 0.6))
    _parent(cone, root, (-0.7, 0, 3.66))
    sphere(root, 0.43, (-0.7, 0, 4.3), mat("scoop", (1.0, 0.75, 0.85), 0.5))
    sphere(root, 0.12, (-0.7, 0, 4.78), mat("cherry", (0.85, 0.02, 0.05), 0.2, coat=1))
    for x in (2.6, -2.3):
        for side in (-1, 1):
            wheel(root, x, side * 1.05, 0.5, 0.38)
    lights(root, 3.41, 0.95, 0.8, rear_x=-3.31)
    face(root, 3.44, 1.82, 1.9, 65, eye_r=0.31, mouth=(3.42, 0.7, 0.9))


BUILDERS = {"zippy": build_zippy, "siren": build_siren, "tilly": build_tilly, "nitro": build_nitro,
            "rocky": build_monster, "grizzly": build_monster, "buster": build_buster, "hydro": build_hydro,
            "titan": build_titan, "sprinkles": build_sprinkles}
LENGTH = {"zippy": 4.4, "siren": 4.7, "tilly": 4.7, "nitro": 4.8, "rocky": 5.0, "grizzly": 5.0, "buster": 10.0,
          "hydro": 9.0, "titan": 13.6, "sprinkles": 6.8}


def build(cid, colors=None):
    colors = colors or cast_colors()
    root = bpy.data.objects.new(f"char_{cid}", None)
    bpy.context.collection.objects.link(root)
    BUILDERS[cid](root, colors[cid])
    return root


# ---------------------------------------------------------------- preview renders
def studio(samples):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = 1080
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("studio")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.68, 0.9, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(45), 0, math.radians(-40)))
    bpy.context.object.data.energy = 3.0
    bpy.context.object.data.angle = math.radians(4)
    bpy.ops.mesh.primitive_plane_add(size=200)
    bpy.context.object.data.materials.append(mat("floor", (0.35, 0.37, 0.4), 0.7))


def preview(outdir, only, samples):
    colors = cast_colors()
    os.makedirs(outdir, exist_ok=True)
    for cid in only:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        _MATS.clear()
        _FONT[0] = None
        studio(samples)
        build(cid, colors)
        L = LENGTH[cid]
        d = max(6.0, L * 1.05)
        bpy.ops.object.camera_add(location=(d * 0.95, -d * 0.62, d * 0.45))
        cam = bpy.context.object
        cam.data.lens = 40
        target = bpy.data.objects.new("target", None)
        bpy.context.collection.objects.link(target)
        target.location = (0, 0, 1.0 if L < 7 else 1.8)
        tc = cam.constraints.new("TRACK_TO")
        tc.target, tc.track_axis, tc.up_axis = target, "TRACK_NEGATIVE_Z", "UP_Y"
        bpy.context.scene.camera = cam
        bpy.context.scene.render.filepath = os.path.join(outdir, f"{cid}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[cast3d] rendered {cid}", flush=True)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    outdir, only, samples = os.path.join(ROOT, "work", "blender3d", "cast"), list(BUILDERS), 16
    for i, a in enumerate(argv):
        if a == "--outdir":
            outdir = argv[i + 1]
        elif a == "--only":
            only = argv[i + 1].split(",")
        elif a == "--samples":
            samples = int(argv[i + 1])
    preview(outdir, only, samples)
