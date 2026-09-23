"""
Renders the site's imagery in Blender (Cycles), headless:

    blender -b -P render/render_assets.py -- [planets|sun|hero|all] [--test]

Outputs to docs/img/:
  p-<segment>-<variant>.webp   planet sprites, lit from the LEFT (the page rotates
                               each sprite so the lit side faces the sun)
  x-<segment>.webp             exited companies: desaturated, ringed
  sun.webp                     the star at the centre of the system
  horizon.webp                 wide landing-page backdrop: a planet limb with the
                               sun rising behind it

Frames: planet sprites put the planet disk at 80% of the image width (atmosphere
fills the rest); exited sprites put it at 50% so the ring fits. build_system.py
relies on those two ratios.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "img"
DATA = json.loads((ROOT / "data" / "companies.json").read_text())
SEG_COLOR = {g["id"]: g["color"] for g in DATA["galaxies"]}

# each need-state gets its own kind of world, so orbits read differently at a glance
STYLE = {
    "protein":   "gas",      # banded giant
    "sugarfree": "candy",    # soft swirled bands
    "drinks":    "ocean",    # water world with cloud cover
    "gut":       "rock",     # cratered, rough
    "comfort":   "desert",   # dunes
    "culture":   "terran",   # land and sea
}
VARIANTS = 3
PLANET_PX = 320
FRAME_PLANET = 2.5   # ortho scale: disk (r=1) fills 80% of width
FRAME_EXITED = 4.0   # disk fills 50% so the ring fits

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
WHAT = args[0] if args else "all"
TEST = "--test" in args


# ---------------------------------------------------------------- helpers
def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgba(h, mul=1.0, toward_white=0.0, sat=1.0):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    r, g, b = (lum + (x - lum) * sat for x in (r, g, b))
    r, g, b = (x + (1 - x) * toward_white for x in (r, g, b))
    return (srgb_to_linear(min(1, max(0, r)) ) * mul, srgb_to_linear(min(1, max(0, g))) * mul,
            srgb_to_linear(min(1, max(0, b))) * mul, 1.0)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception as e:  # CPU fallback keeps the script portable
        print("GPU unavailable, using CPU:", e)
    sc.cycles.samples = 24 if TEST else 96
    sc.cycles.use_denoising = True
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.004, 0.006, 0.012, 1)
    bg.inputs["Strength"].default_value = 1.0
    sc.world = world
    return sc


def set_output(sc, path, w, h):
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    s = sc.render.image_settings
    try:
        s.file_format = "WEBP"
        s.quality = 90
    except TypeError:
        s.file_format = "PNG"
        path = path.with_suffix(".png")
    s.color_mode = "RGBA"
    sc.render.filepath = str(path)
    return path


def ortho_camera(scale):
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.ortho_scale = scale
    ob = bpy.data.objects.new("cam", cam)
    bpy.context.collection.objects.link(ob)
    ob.location = (0, -10, 0)
    ob.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.camera = ob
    return ob


def sun_lamp(direction, strength=4.0, color=(1, 0.95, 0.88), angle=0.02):
    lamp = bpy.data.lights.new("sun", "SUN")
    lamp.energy = strength
    lamp.color = color
    lamp.angle = angle
    ob = bpy.data.objects.new("sun", lamp)
    bpy.context.collection.objects.link(ob)
    ob.rotation_euler = Vector(direction).to_track_quat("-Z", "Y").to_euler()
    return ob


def sphere(radius=1.0, name="planet"):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=radius)
    ob = bpy.context.active_object
    ob.name = name
    bpy.ops.object.shade_smooth()
    return ob


class Nodes:
    """Tiny builder so material graphs stay readable."""

    def __init__(self, name):
        self.mat = bpy.data.materials.new(name)
        self.mat.use_nodes = True
        self.t = self.mat.node_tree
        self.t.nodes.clear()
        self.out = self.new("ShaderNodeOutputMaterial")

    def new(self, kind, **inputs):
        n = self.t.nodes.new(kind)
        for k, v in inputs.items():
            if hasattr(n, k):
                setattr(n, k, v)
            else:
                n.inputs[k].default_value = v
        return n

    def link(self, a, b):
        self.t.links.new(a, b)

    def math(self, op, a, b=None, c=None, **kw):
        n = self.new("ShaderNodeMath", operation=op, **kw)
        for i, v in enumerate((a, b, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                self.link(v, n.inputs[i])
        return n.outputs[0]

    def ramp(self, fac, stops):
        n = self.new("ShaderNodeValToRGB")
        cr = n.color_ramp
        cr.interpolation = "EASE"
        while len(cr.elements) < len(stops):
            cr.elements.new(0.5)
        for el, (pos, col) in zip(cr.elements, stops):
            el.position, el.color = pos, col
        self.link(fac, n.inputs["Fac"])
        return n.outputs["Color"]


# ---------------------------------------------------------------- planet surface
def surface_material(seg, variant, exited=False):
    col = SEG_COLOR[seg]
    style = STYLE[seg]
    sat = 0.28 if exited else 1.0
    mul = 0.6 if exited else 1.0
    deep = hex_rgba(col, 0.16 * mul, sat=sat)
    dark = hex_rgba(col, 0.45 * mul, sat=sat)
    mid = hex_rgba(col, 1.0 * mul, sat=sat)
    light = hex_rgba(col, 1.0 * mul, toward_white=0.45, sat=sat)
    pale = hex_rgba(col, 1.0 * mul, toward_white=0.8, sat=sat * 0.6)

    N = Nodes(f"{seg}-{variant}")
    tc = N.new("ShaderNodeTexCoord").outputs["Object"]
    seed = N.new("ShaderNodeVectorMath", operation="ADD")
    N.link(tc, seed.inputs[0])
    seed.inputs[1].default_value = (variant * 7.31, variant * 3.17, variant * 5.93)
    co = seed.outputs[0]

    bsdf = N.new("ShaderNodeBsdfPrincipled")
    N.link(bsdf.outputs[0], N.out.inputs["Surface"])
    rough = 0.75

    if style in ("gas", "candy"):
        warp = N.new("ShaderNodeTexNoise", **{"Scale": 2.2, "Detail": 6.0, "Roughness": 0.55})
        N.link(co, warp.inputs["Vector"])
        wave = N.new("ShaderNodeTexWave", wave_type="BANDS", bands_direction="Z",
                     **{"Scale": 2.6 + variant * 0.7 if style == "gas" else 1.6 + variant * 0.5,
                        "Distortion": 4.0 if style == "gas" else 8.0, "Detail": 2.0,
                        "Detail Roughness": 0.6})
        mix = N.new("ShaderNodeVectorMath", operation="ADD")
        N.link(co, mix.inputs[0])
        scl = N.new("ShaderNodeVectorMath", operation="SCALE", **{"Scale": 0.35})
        N.link(warp.outputs["Color"], scl.inputs[0])
        N.link(scl.outputs[0], mix.inputs[1])
        N.link(mix.outputs[0], wave.inputs["Vector"])
        stops = ([(0.0, deep), (0.3, dark), (0.55, mid), (0.8, light), (1.0, pale)] if style == "gas"
                 else [(0.0, dark), (0.4, mid), (0.75, light), (1.0, pale)])
        N.link(N.ramp(wave.outputs["Fac"], stops), bsdf.inputs["Base Color"])
        rough = 0.6

    elif style in ("rock", "desert"):
        n1 = N.new("ShaderNodeTexNoise", **{"Scale": 3.5 if style == "rock" else 2.0, "Detail": 14.0,
                                            "Roughness": 0.62 if style == "rock" else 0.5})
        N.link(co, n1.inputs["Vector"])
        vor = N.new("ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE" if style == "rock" else "F1",
                    **{"Scale": 5.0 if style == "rock" else 1.4})
        N.link(co, vor.inputs["Vector"])
        crater = N.math("MULTIPLY", vor.outputs["Distance"], 1.0)
        fac = N.math("MULTIPLY_ADD", n1.outputs["Fac"], 0.8, crater) if style == "rock" else N.math("ADD", n1.outputs["Fac"], N.math("MULTIPLY", crater, 0.25))
        fac = N.math("MULTIPLY", fac, 0.62 if style == "rock" else 0.8)
        stops = ([(0.0, deep), (0.35, dark), (0.6, mid), (1.0, light)] if style == "rock"
                 else [(0.0, dark), (0.35, mid), (0.7, light), (1.0, pale)])
        N.link(N.ramp(fac, stops), bsdf.inputs["Base Color"])
        bump = N.new("ShaderNodeBump", **{"Strength": 0.45 if style == "rock" else 0.2, "Distance": 0.05})
        N.link(fac, bump.inputs["Height"])
        N.link(bump.outputs["Normal"], bsdf.inputs["Normal"])
        rough = 0.9

    else:  # ocean / terran: land-sea mask + cloud layer
        land = N.new("ShaderNodeTexNoise", **{"Scale": 1.8, "Detail": 12.0, "Roughness": 0.58})
        N.link(co, land.inputs["Vector"])
        if style == "ocean":
            sea = N.ramp(land.outputs["Fac"], [(0.0, deep), (0.45, dark), (0.62, mid), (0.72, light)])
        else:
            sea_blue = hex_rgba("#1f4e8c", 0.5)
            sea = N.ramp(land.outputs["Fac"], [(0.0, sea_blue), (0.49, sea_blue), (0.52, dark), (0.65, mid), (0.85, light)])
        clouds = N.new("ShaderNodeTexNoise", **{"Scale": 3.2, "Detail": 8.0, "Roughness": 0.6, "Distortion": 1.2})
        N.link(co, clouds.inputs["Vector"])
        cmask = N.ramp(clouds.outputs["Fac"], [(0.0, (0, 0, 0, 1)), (0.52, (0, 0, 0, 1)), (0.68, (1, 1, 1, 1))])
        mixc = N.new("ShaderNodeMix", data_type="RGBA")
        N.link(cmask, mixc.inputs["Factor"])
        N.link(sea, mixc.inputs["A"])
        mixc.inputs["B"].default_value = hex_rgba("#ffffff", 0.9 * mul, sat=sat)
        N.link(mixc.outputs["Result"], bsdf.inputs["Base Color"])
        rough = 0.45 if style == "ocean" else 0.7

    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Specular IOR Level"].default_value = 0.35
    return N.mat


def atmosphere_material(seg, light_dir, exited=False):
    """Emissive rim that is brightest on the lit limb and fades into space."""
    N = Nodes(f"atmo-{seg}")
    col = hex_rgba(SEG_COLOR[seg], 1.0, toward_white=0.35, sat=0.3 if exited else 1.0)
    # distance from the planet surface, measured in screen space via the facing ratio
    # with blend 0.5, Facing = 1 - N.V. On a shell of radius 1.13 the planet's edge sits at
    # Facing ~0.53, the shell's silhouette at 1.0. Peak the glow at the planet edge, fade to
    # nothing at the silhouette, and keep a faint haze over the disk.
    lw = N.new("ShaderNodeLayerWeight", **{"Blend": 0.5})
    rim = N.ramp(lw.outputs["Facing"], [(0.0, (0, 0, 0, 1)), (0.3, (0.04, 0.04, 0.04, 1)), (0.5, (0.55, 0.55, 0.55, 1)),
                                        (0.56, (1, 1, 1, 1)), (0.72, (0.22, 0.22, 0.22, 1)), (1.0, (0, 0, 0, 1))])
    # Cycles flips normals on back faces, so derive the outward direction from position
    # (planet at the origin) and drop the far side of the shell entirely.
    geo = N.new("ShaderNodeNewGeometry")
    outward = N.new("ShaderNodeVectorMath", operation="NORMALIZE")
    N.link(geo.outputs["Position"], outward.inputs[0])
    d = N.new("ShaderNodeVectorMath", operation="DOT_PRODUCT")
    N.link(outward.outputs["Vector"], d.inputs[0])
    d.inputs[1].default_value = tuple(-x for x in Vector(light_dir).normalized())
    lit = N.new("ShaderNodeMapRange", clamp=True, **{"From Min": -0.35, "From Max": 1.0, "To Min": 0.05, "To Max": 1.0})
    N.link(d.outputs["Value"], lit.inputs["Value"])
    front = N.math("SUBTRACT", 1.0, geo.outputs["Backfacing"])
    fac = N.math("MULTIPLY", N.math("MULTIPLY", rim, lit.outputs["Result"]), front)
    em = N.new("ShaderNodeEmission", **{"Strength": 0.9 if exited else 2.4})
    em.inputs["Color"].default_value = col
    tr = N.new("ShaderNodeBsdfTransparent")
    mix = N.new("ShaderNodeMixShader")
    N.link(fac, mix.inputs["Fac"])
    N.link(tr.outputs[0], mix.inputs[1])
    N.link(em.outputs[0], mix.inputs[2])
    N.link(mix.outputs[0], N.out.inputs["Surface"])
    return N.mat


def ring_material(seg):
    N = Nodes(f"ring-{seg}")
    tc = N.new("ShaderNodeTexCoord").outputs["Object"]
    length = N.new("ShaderNodeVectorMath", operation="LENGTH")
    N.link(tc, length.inputs[0])
    bands = N.new("ShaderNodeTexWave", wave_type="RINGS", rings_direction="SPHERICAL", **{"Scale": 3.0, "Distortion": 0.0, "Detail": 0.0})
    N.link(tc, bands.inputs["Vector"])
    alpha = N.math("MULTIPLY", N.math("ADD", bands.outputs["Fac"], 0.6), 0.32)
    bsdf = N.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = hex_rgba(SEG_COLOR[seg], 0.9, toward_white=0.5, sat=0.35)
    bsdf.inputs["Roughness"].default_value = 0.8
    N.link(alpha, bsdf.inputs["Alpha"])
    N.link(bsdf.outputs[0], N.out.inputs["Surface"])
    return N.mat


def render_planet(seg, variant, exited=False):
    sc = reset()
    light_dir = (1.0, 0.18, -0.22)  # travels to +x: lights the left limb, terminator right of centre
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    frame = FRAME_EXITED if exited else FRAME_PLANET
    ortho_camera(frame)
    sun_lamp(light_dir, strength=5.0)
    p = sphere(1.0)
    p.rotation_euler = (math.radians(12 + variant * 9), math.radians(-18 + variant * 11), math.radians(variant * 40))
    p.data.materials.append(surface_material(seg, variant, exited))
    a = sphere(1.13, "atmo")
    a.data.materials.append(atmosphere_material(seg, light_dir, exited))
    a.visible_shadow = False
    if exited:
        bpy.ops.mesh.primitive_torus_add(major_radius=1.55, minor_radius=0.3, major_segments=128, minor_segments=24)
        r = bpy.context.active_object
        r.scale = (1, 1, 0.01)
        r.rotation_euler = (math.radians(16), math.radians(-20), 0)
        r.visible_shadow = False
        r.data.materials.append(ring_material(seg))
    name = f"x-{seg}" if exited else f"p-{seg}-{variant}"
    px = int(PLANET_PX * (FRAME_EXITED / FRAME_PLANET)) if exited else PLANET_PX
    path = set_output(sc, OUT / f"{name}.webp", px, px)
    bpy.ops.render.render(write_still=True)
    print("wrote", path)


# ---------------------------------------------------------------- sun
def render_sun():
    sc = reset()
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    ortho_camera(2.02)
    s = sphere(1.0, "star")
    N = Nodes("star")
    tc = N.new("ShaderNodeTexCoord").outputs["Object"]
    gran = N.new("ShaderNodeTexVoronoi", feature="F1", **{"Scale": 14.0, "Randomness": 1.0})
    N.link(tc, gran.inputs["Vector"])
    turb = N.new("ShaderNodeTexNoise", **{"Scale": 3.0, "Detail": 10.0, "Roughness": 0.6})
    N.link(tc, turb.inputs["Vector"])
    fac = N.math("ADD", N.math("MULTIPLY", gran.outputs["Distance"], 0.45), N.math("MULTIPLY", turb.outputs["Fac"], 0.7))
    lw = N.new("ShaderNodeLayerWeight", **{"Blend": 0.45})
    limb = N.math("POWER", lw.outputs["Facing"], 1.4)       # 0 at centre, 1 at the limb
    fac = N.math("SUBTRACT", fac, N.math("MULTIPLY", limb, 0.8))
    col = N.ramp(fac, [(0.0, hex_rgba("#8a1f06")), (0.25, hex_rgba("#e0480f")), (0.5, hex_rgba("#ff8a24")), (0.72, hex_rgba("#ffc15a")), (0.95, hex_rgba("#fff0c8"))])
    em = N.new("ShaderNodeEmission", **{"Strength": 1.0})
    N.link(col, em.inputs["Color"])
    N.link(em.outputs[0], N.out.inputs["Surface"])
    s.data.materials.append(N.mat)
    path = set_output(sc, OUT / "sun.webp", 400, 400)
    bpy.ops.render.render(write_still=True)
    print("wrote", path)


# ---------------------------------------------------------------- landing horizon
def render_hero():
    sc = reset()
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.cycles.samples = 48 if TEST else 256
    R = 30.0
    # camera just above a giant planet, looking at its limb; the sun sits behind it
    cam = bpy.data.cameras.new("cam")
    cam.lens = 38
    cam.sensor_width = 36
    ob = bpy.data.objects.new("cam", cam)
    bpy.context.collection.objects.link(ob)
    ob.location = (0, -24.0, 1.2)
    ob.rotation_euler = (math.radians(88.2), 0, 0)
    sc.camera = ob

    p = sphere(R)
    p.location = (0, 12.0, -R - 2.3)
    N = Nodes("night")
    tc = N.new("ShaderNodeTexCoord").outputs["Object"]
    n1 = N.new("ShaderNodeTexNoise", **{"Scale": 0.09, "Detail": 12.0, "Roughness": 0.6})
    N.link(tc, n1.inputs["Vector"])
    base = N.ramp(n1.outputs["Fac"], [(0.35, hex_rgba("#0a0f1e")), (0.6, hex_rgba("#1b2440")), (0.8, hex_rgba("#3a2f3a"))])
    bsdf = N.new("ShaderNodeBsdfPrincipled", **{"Roughness": 0.7})
    N.link(base, bsdf.inputs["Base Color"])
    N.link(bsdf.outputs[0], N.out.inputs["Surface"])
    p.data.materials.append(N.mat)

    # atmosphere shell: bright where the sun is behind the limb, fading along the arc
    a = sphere(R * 1.024, "atmo")
    a.location = p.location
    A = Nodes("atmo")
    lw = A.new("ShaderNodeLayerWeight", **{"Blend": 0.5})
    rim = A.ramp(lw.outputs["Facing"], [(0.0, (0, 0, 0, 1)), (0.7, (0, 0, 0, 1)), (0.765, (0.18, 0.18, 0.18, 1)), (0.8, (1, 1, 1, 1)), (0.87, (0.28, 0.28, 0.28, 1)), (1.0, (0, 0, 0, 1))])
    back = A.new("ShaderNodeNewGeometry")
    tc2 = A.new("ShaderNodeTexCoord").outputs["Object"]
    sep = A.new("ShaderNodeSeparateXYZ")
    A.link(tc2, sep.inputs[0])
    centre = A.new("ShaderNodeMapRange", clamp=True, **{"From Min": 0.0, "From Max": R * 0.75, "To Min": 1.0, "To Max": 0.0})
    A.link(A.math("ABSOLUTE", sep.outputs["X"]), centre.inputs["Value"])
    focus = A.math("POWER", centre.outputs["Result"], 2.2)
    fac = A.math("MULTIPLY", rim, A.math("ADD", A.math("MULTIPLY", focus, 0.9), 0.1))
    fac = A.math("MULTIPLY", fac, A.math("SUBTRACT", 1.0, back.outputs["Backfacing"]))
    col = A.ramp(focus, [(0.0, hex_rgba("#1c2f9e")), (0.45, hex_rgba("#4d6dff")), (0.8, hex_rgba("#ff9a55")), (1.0, hex_rgba("#ffe0b0"))])
    em = A.new("ShaderNodeEmission", **{"Strength": 2.2})
    A.link(col, em.inputs["Color"])
    tr = A.new("ShaderNodeBsdfTransparent")
    mix = A.new("ShaderNodeMixShader")
    A.link(fac, mix.inputs["Fac"])
    A.link(tr.outputs[0], mix.inputs[1])
    A.link(em.outputs[0], mix.inputs[2])
    A.link(mix.outputs[0], A.out.inputs["Surface"])
    a.data.materials.append(A.mat)
    a.visible_shadow = False

    # sun just behind the horizon: rakes a thin crescent along the limb
    sun_lamp((0, -1.0, -0.035), strength=6.0, color=(1, 0.86, 0.7), angle=0.03)
    path = set_output(sc, OUT / "horizon.webp", 1280 if TEST else 2560, 640 if TEST else 1280)
    bpy.ops.render.render(write_still=True)
    print("wrote", path)


# ---------------------------------------------------------------- main
OUT.mkdir(parents=True, exist_ok=True)
if WHAT in ("planets", "all"):
    only = [a for a in args if a in STYLE]
    segs = only or (list(STYLE) if not TEST else ["protein", "drinks", "gut"])
    for seg in segs:
        for v in range(1 if TEST else VARIANTS):
            render_planet(seg, v)
        render_planet(seg, 0, exited=True)
if WHAT in ("sun", "all"):
    render_sun()
if WHAT in ("hero", "all"):
    render_hero()
