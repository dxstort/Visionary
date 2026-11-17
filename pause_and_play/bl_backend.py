"""Blender (Eevee) backend for the shot code.

Import this module BEFORE `shots`: it replaces engine.Scene with BScene, which keeps the same API
(box / blob / solid / quad / line3 / sprite / overlay / ground) but turns every primitive into a real
3D object rendered by Blender: z-buffered, bevelled, smooth-shaded, with soft sun shadows, sky
ambient light, depth of field and a subtle surface texture. 2D sprites, emotes and captions are
still drawn with Pillow on top of the Blender frame, using the same camera maths, so they line up.

Run with the Python that has `bpy` installed (pip install bpy), e.g.
    $BVENV/bin/python render_bl.py --shots 1-9 --out out/test.mp4

Coordinates: shot code is Y-up (x right, y up, z toward the default camera); Blender is Z-up.
A shot-space point p maps to Blender as C @ p with C = [[1,0,0],[0,0,-1],[0,1,0]].
"""
import hashlib
import math
import os
import tempfile

import bpy  # noqa: I001  (bpy must be imported before bmesh / mathutils)
import bmesh
import numpy as np
from mathutils import Matrix
from PIL import Image, ImageChops, ImageDraw, ImageFilter

import engine
from engine import SS, Decal, blob_mesh, clamp, vignette

C3 = np.array([[1.0, 0, 0], [0, 0, -1.0], [0, 1.0, 0]])
C4 = np.eye(4)
C4[:3, :3] = C3

RENDER_W, RENDER_H = 576, 1024      # Blender render size (the reference's size); upscaled to 1080x1920
BOX_E, BOX_N, BOX_M = 0.16, 24, 12  # rounded-box superellipsoid (toy-part bevel)
TEX = 512                           # decal texture size


def lin(c):
    """sRGB 0-255 -> linear 0-1."""
    out = []
    for v in c[:3]:
        v = clamp(v / 255.0)
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return out


# ------------------------------------------------------------- blender setup
class _World:
    """One-time Blender scene: render settings, shared materials, sun, camera, sky."""

    def __init__(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc = bpy.context.scene
        self.scene = sc
        sc.render.engine = "BLENDER_EEVEE"
        sc.render.resolution_x, sc.render.resolution_y = RENDER_W, RENDER_H
        sc.render.resolution_percentage = 100
        sc.render.film_transparent = False
        sc.render.image_settings.file_format = "PNG"
        sc.render.image_settings.compression = 0
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
        ee = sc.eevee
        for k, v in (("taa_render_samples", int(os.environ.get("BL_TAA", "6"))), ("use_bokeh_jittered", False), ("bokeh_max_size", 40.0), ("use_shadows", True), ("shadow_resolution_scale", 0.5),
                     ("shadow_ray_count", 1), ("shadow_step_count", 4), ("use_raytracing", False),
                     ("use_gtao", True), ("gtao_distance", 0.6), ("fast_gi_method", "GLOBAL_ILLUMINATION")):
            try:
                setattr(ee, k, v)
            except (AttributeError, TypeError):
                pass
        self.tmp = os.path.join(tempfile.gettempdir(), f"bl_frame_{os.getpid()}.png")
        sc.render.filepath = self.tmp

        # camera
        cd = bpy.data.cameras.new("cam")
        cd.sensor_fit = "VERTICAL"
        cd.clip_start, cd.clip_end = 0.05, 600
        self.cam = bpy.data.objects.new("cam", cd)
        sc.collection.objects.link(self.cam)
        sc.camera = self.cam

        # warm sun with soft shadows
        ld = bpy.data.lights.new("sun", "SUN")
        ld.energy = 2.7
        ld.angle = math.radians(0.35)
        ld.color = (1.0, 0.95, 0.86)
        self.sun = bpy.data.objects.new("sun", ld)
        sc.collection.objects.link(self.sun)
        L = C3 @ engine.LIGHT
        z = L / np.linalg.norm(L)
        x = np.cross([0, 0, 1.0], z)
        x = x / np.linalg.norm(x)
        y = np.cross(z, x)
        R = np.eye(4)
        R[:3, 0], R[:3, 1], R[:3, 2] = x, y, z
        self.sun.matrix_world = Matrix(R.tolist())
        self.sun_day = self.sun.matrix_world.copy()

        # sky: gradient for camera rays, flat bluish ambient for lighting
        w = bpy.data.worlds.new("sky")
        sc.world = w
        nt = w.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputWorld")
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = -0.05, 0.75
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        self.sky_bot, self.sky_top = mix.inputs[6], mix.inputs[7]
        bg_cam = nt.nodes.new("ShaderNodeBackground")
        bg_amb = nt.nodes.new("ShaderNodeBackground")
        self.amb = bg_amb
        lp = nt.nodes.new("ShaderNodeLightPath")
        ms = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(tc.outputs["Generated"], sep.inputs[0])
        nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], mix.inputs["Factor"])
        # star field for night skies: sparse Voronoi points in view-direction space, scaled by star_k
        vor = nt.nodes.new("ShaderNodeTexVoronoi")
        vor.inputs["Scale"].default_value = 120.0
        nt.links.new(tc.outputs["Generated"], vor.inputs["Vector"])
        dot = nt.nodes.new("ShaderNodeMapRange")
        dot.inputs["From Min"].default_value, dot.inputs["From Max"].default_value = 0.0, 0.11
        dot.inputs["To Min"].default_value, dot.inputs["To Max"].default_value = 1.0, 0.0
        nt.links.new(vor.outputs["Distance"], dot.inputs["Value"])
        sepc = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(vor.outputs["Color"], sepc.inputs[0])
        thin = nt.nodes.new("ShaderNodeMath")
        thin.operation = "GREATER_THAN"
        thin.inputs[1].default_value = 0.93
        nt.links.new(sepc.outputs[0], thin.inputs[0])
        st = nt.nodes.new("ShaderNodeMath")
        st.operation = "MULTIPLY"
        nt.links.new(dot.outputs["Result"], st.inputs[0])
        nt.links.new(thin.outputs[0], st.inputs[1])
        st2 = nt.nodes.new("ShaderNodeMath")
        st2.operation = "MULTIPLY"
        st2.inputs[1].default_value = 0.0
        self.star_k = st2.inputs[1]
        nt.links.new(st.outputs[0], st2.inputs[0])
        add = nt.nodes.new("ShaderNodeMix")
        add.data_type = "RGBA"
        add.blend_type = "ADD"
        add.inputs[7].default_value = (1.0, 0.97, 0.85, 1.0)
        nt.links.new(st2.outputs[0], add.inputs["Factor"])
        nt.links.new(mix.outputs[2], add.inputs[6])
        nt.links.new(add.outputs[2], bg_cam.inputs["Color"])
        nt.links.new(lp.outputs["Is Camera Ray"], ms.inputs["Fac"])
        nt.links.new(bg_amb.outputs[0], ms.inputs[1])
        nt.links.new(bg_cam.outputs[0], ms.inputs[2])
        nt.links.new(ms.outputs[0], out.inputs["Surface"])

        self.mat_base = self._material("base")
        self.mat_emit = self._material("emit", emit=True)
        self.mat_decal = self._material("decal", decal=True)
        self.decal_mats = {}
        self.meshes = {}
        self.pool = []
        self.lamp_pool = []

    # -- shared materials: per-object colour comes from Object Info -> Color (no recompiles)
    def _material(self, name, emit=False, decal=False):
        m = bpy.data.materials.new(name)
        nt = m.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        oi = nt.nodes.new("ShaderNodeObjectInfo")
        if emit:
            em = nt.nodes.new("ShaderNodeEmission")
            nt.links.new(oi.outputs["Color"], em.inputs["Color"])
            nt.links.new(em.outputs[0], out.inputs["Surface"])
            return m
        # subtle surface texture: colour * (1 + strength * (noise - 0.5)), strength = object colour alpha
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 4.0
        nz.inputs["Detail"].default_value = 2.0
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        sub = nt.nodes.new("ShaderNodeMath")
        sub.operation = "SUBTRACT"
        sub.inputs[1].default_value = 0.5
        nt.links.new(nz.outputs["Fac"], sub.inputs[0])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY_ADD"
        nt.links.new(sub.outputs[0], mul.inputs[0])
        nt.links.new(oi.outputs["Alpha"], mul.inputs[1])
        mul.inputs[2].default_value = 1.0
        tint = nt.nodes.new("ShaderNodeMix")
        tint.data_type = "RGBA"
        tint.blend_type = "MULTIPLY"
        tint.inputs["Factor"].default_value = 1.0
        nt.links.new(oi.outputs["Color"], tint.inputs[6])
        comb = nt.nodes.new("ShaderNodeCombineColor")
        for i in range(3):
            nt.links.new(mul.outputs[0], comb.inputs[i])
        nt.links.new(comb.outputs[0], tint.inputs[7])
        col_out = tint.outputs[2]
        if decal:
            img = nt.nodes.new("ShaderNodeTexImage")
            img.name = "decal_img"
            img.extension = "CLIP"
            img.interpolation = "Linear"
            mx = nt.nodes.new("ShaderNodeMix")
            mx.data_type = "RGBA"
            nt.links.new(img.outputs["Alpha"], mx.inputs["Factor"])
            nt.links.new(col_out, mx.inputs[6])
            nt.links.new(img.outputs["Color"], mx.inputs[7])
            col_out = mx.outputs[2]
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = 0.62
        try:
            bsdf.inputs["Specular IOR Level"].default_value = 0.35
        except KeyError:
            pass
        nt.links.new(col_out, bsdf.inputs["Base Color"])
        nt.links.new(bsdf.outputs[0], out.inputs["Surface"])
        return m

    def decal_material(self, key, rgba):
        if key in self.decal_mats:
            return self.decal_mats[key]
        h, w = rgba.shape[:2]
        im = bpy.data.images.new(f"decal_{key[:10]}", w, h, alpha=True)
        im.alpha_mode = "STRAIGHT"
        im.pixels.foreach_set((np.flipud(rgba).astype(np.float32) / 255.0).ravel())
        im.pack()
        m = self.mat_decal.copy()
        m.node_tree.nodes["decal_img"].image = im
        self.decal_mats[key] = m
        return m

    # -- meshes (cached by shape key)
    def mesh(self, key, build):
        me = self.meshes.get(key)
        if me is None:
            me = build()
            me.materials.append(self.mat_base)
            self.meshes[key] = me
        return me

    def lamp(self, i):
        while len(self.lamp_pool) <= i:
            ld = bpy.data.lights.new(f"pt{len(self.lamp_pool)}", "POINT")
            o = bpy.data.objects.new(f"pt{len(self.lamp_pool)}", ld)
            self.scene.collection.objects.link(o)
            self.lamp_pool.append(o)
        return self.lamp_pool[i]

    def obj(self, i):
        while len(self.pool) <= i:
            o = bpy.data.objects.new(f"p{len(self.pool)}", None)
            self.pool.append(o)
        return self.pool[i]


_W = None


def world():
    global _W
    if _W is None:
        _W = _World()
    return _W


# --------------------------------------------------------------- mesh build
def _finish(bm, name, smooth=True, sharp_deg=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.shade_smooth()
        if sharp_deg is not None:
            me.set_sharp_from_angle(angle=math.radians(sharp_deg))
    else:
        me.shade_flat()
    return me


def build_blob(size, e, e2, n, m, uv=None, span=1.2, decal_scale=1.0):
    """Superellipsoid mesh in Blender local space, with optional decal UVs:
    uv='front' planar on the +z (shot space) face, uv='wrap' cylindrical round the front."""
    V, Q, _ = blob_mesh(e, n, m, e2)
    Vs = (V * np.asarray(size, float)) @ C3.T
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in Vs.tolist()]
    for q in Q.tolist():
        try:
            bm.faces.new([vs[k] for k in q])
        except ValueError:
            pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6 * max(size))
    bmesh.ops.dissolve_degenerate(bm, dist=1e-7, edges=bm.edges)
    bm.normal_update()
    hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
    if uv:
        layer = bm.loops.layers.uv.new("UVMap")
        for f in bm.faces:
            nb = f.normal
            pts = [(l.vert.co.x, l.vert.co.z, -l.vert.co.y) for l in f.loops]   # back to shot space
            if uv == "front":
                ok = (-nb.y) > 0.6
                uvs = [((x / hx + 1) / 2, (y / hy + 1) / 2) if ok else (-5.0, -5.0) for x, y, z in pts]
            else:
                ang = [math.atan2(x / hx, z / hz) for x, y, z in pts]
                if max(ang) - min(ang) > math.pi:
                    ang = [a + 2 * math.pi if a < 0 else a for a in ang]
                uvs = [((a / span + 1) / 2, (y / (hy * decal_scale) + 1) / 2) for a, (x, y, z) in zip(ang, pts)]
            for l, c in zip(f.loops, uvs):
                l[layer].uv = c
    return _finish(bm, "blob", smooth=True, sharp_deg=None if e > 0.4 else 40)


def build_poly(verts, faces, smooth=False):
    bm = bmesh.new()
    vs = [bm.verts.new((C3 @ np.asarray(p, float)).tolist()) for p in verts]
    for f in faces:
        try:
            bm.faces.new([vs[k] for k in f])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(bm, "poly", smooth=smooth)


def build_cyl(length, radius, n=10):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=radius, radius2=radius, depth=length)
    return _finish(bm, "cyl", smooth=True)


def _r(x, k=3):
    return tuple(round(float(v), k) for v in np.ravel(x))


# ------------------------------------------------------------- decal texture
class TexDecal(Decal):
    """Decal API drawn into a texture: u, v in [-1, 1] -> pixels (v up)."""

    def __init__(self, w=TEX, h=TEX):
        w, h = int(w), int(h)
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self.w, self.h = w, h
        self.k, self.kv = w / 2, h / 2
        self.lit = 1.0
        self.col = lambda c: tuple(int(clamp(v, 0, 255)) for v in c[:3]) + tuple(c[3:4])

    def pt(self, u, v):
        return ((u + 1) / 2 * self.w, (1 - v) / 2 * self.h)


def decal_texture(fn, size=(1.0, 1.0)):
    """Texture sized to the decal's physical aspect; big surfaces (walls) get more pixels."""
    sx, sy = max(size[0], 1e-3), max(size[1], 1e-3)
    long = 2048 if max(sx, sy) > 3.0 else TEX
    w, h = (long, max(64, long * sy / sx)) if sx >= sy else (max(64, long * sx / sy), long)
    if long == TEX:
        w = h = TEX
    D = TexDecal(w, h)
    fn(D)
    a = np.asarray(D.img)
    if a[..., 3].max() == 0:
        return None, None
    return hashlib.md5(a.tobytes()).hexdigest(), a


# ------------------------------------------------------------------- scene
class BScene(engine.Scene):
    """engine.Scene with the same camera maths; primitives become Blender objects."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.prims = []

    # primitives ----------------------------------------------------------
    def box(self, M, size, color, layer=5, decal=None, live=False, lit=True, **kw):
        size = tuple(float(v) for v in size)
        key = ("box", _r(size))
        uv = "front" if decal else None
        if uv:
            key += ("uv",)
        build = lambda: build_blob(size, BOX_E, BOX_E, BOX_N, BOX_M, uv=uv)
        self.prims.append((key, build, np.asarray(M, float), self.col(color, live), lit, decal, 0.05, size))

    def blob(self, M, size, color, e=1.0, layer=5, live=False, bias=0.0, decal=None, n=14, m=8, lit=True,
             e2=None, span=1.2):
        e2 = e if e2 is None else e2
        size = tuple(float(v) for v in size)
        n, m = max(n, 16), max(m, 8)
        if e2 >= 0.8 and e < 0.5 and n >= 30:
            n, m = 48, 16
        uv = ("wrap" if e2 >= 0.8 else "front") if decal else None
        key = ("blob", _r(size), round(e, 3), round(e2, 3), n, m, uv, round(span, 3))
        build = lambda: build_blob(size, e, e2, n, m, uv=uv, span=span, decal_scale=1.08)
        self.prims.append((key, build, np.asarray(M, float), self.col(color, live), lit, decal, 0.04, size))

    def solid(self, M, verts, faces, color, layer=2, live=False, bias=0.0, lit=True):
        key = ("solid", _r(verts, 4), tuple(tuple(f) for f in faces))
        build = lambda: build_poly(verts, faces)
        self.prims.append((key, build, np.asarray(M, float), self.col(color, live), lit, None, 0.05, None))

    def quad(self, pts, color, layer=1, live=False, outline=None, depth_pt=None):
        if len(color) > 3 and color[3] < 255:
            return  # fake shadows / glows: Blender casts real shadows
        pts = [np.asarray(p, float).copy() for p in pts]
        for p in pts:
            if 0.0 < p[1] < 0.05:
                p[1] *= 3.0  # separate coplanar ground layers for the z-buffer
        key = ("quad", _r(pts))
        self.prims.append((key, lambda: build_poly(pts, [list(range(len(pts)))]), np.eye(4),
                           self.col(color, live), True, None, 0.12, None))

    def line3(self, a, b, color, width=0.05, layer=5, live=False, bias=0.0):
        a, b = np.asarray(a, float), np.asarray(b, float)
        if len(color) > 3 and color[3] < 255:
            # translucent glow round a beam: soft 2D stroke on the overlay layer
            def glow_line(d, W_, H_, a=a, b=b, color=color, width=width):
                ca, cb = self.to_cam(a), self.to_cam(b)
                cl = self._clip([ca, cb])
                if len(cl) < 2:
                    return
                wpx = width * self.fl / max((ca[2] + cb[2]) / 2, 0.2)
                p0, p1 = self.proj_c(cl[0]), self.proj_c(cl[1])
                for k in (1.0, 0.7, 0.45):
                    d.line([p0, p1], fill=tuple(color[:3]) + (int(color[3] * 0.45),), width=max(1, int(wpx * k)))

            self.overlays.insert(0, glow_line)
            return
        d = b - a
        L = float(np.linalg.norm(d))
        if L < 1e-6:
            return
        z = d / L
        x = np.cross(z, [0, 1.0, 0]) if abs(z[1]) < 0.95 else np.cross(z, [1.0, 0, 0])
        x /= np.linalg.norm(x)
        y = np.cross(z, x)
        M = np.eye(4)
        M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = x, y, z, (a + b) / 2
        # cylinder is built along Blender Z == shot -y... build it along shot z instead:
        key = ("line", round(L, 2), round(width, 3))
        build = lambda: _cyl_shot_z(L, width / 2)
        self.prims.append((key, build, M, self.col(color, live), False, None, 0.0, None))

    # render --------------------------------------------------------------
    def _sync(self):
        W = world()
        bsc = W.scene
        for i, (key, build, M, col, lit, decal, tex, size) in enumerate(self.prims):
            o = W.obj(i)
            me = W.mesh(key, build)
            if o.type != "MESH" or o.data is not me:
                if o.type != "MESH":
                    nm = o.name
                    bpy.data.objects.remove(o)
                    o = bpy.data.objects.new(nm, me)
                    W.pool[i] = o
                else:
                    o.data = me
            if o.name not in bsc.collection.objects:
                bsc.collection.objects.link(o)
            mat = W.mat_base if lit else W.mat_emit
            if decal:
                k, rgba = decal_texture(decal, size if size else (1.0, 1.0))
                if k:
                    mat = W.decal_material(k, rgba)
            slot = o.material_slots[0]
            if slot.link != "OBJECT":
                slot.link = "OBJECT"
            if slot.material is not mat:
                slot.material = mat
            o.color = lin(col) + [tex]
            o.matrix_world = Matrix((C4 @ M @ C4.T).tolist())
            o.hide_render = False
        for o in W.pool[len(self.prims):]:
            o.hide_render = True
        for i, (pos, color, energy, radius, shadow) in enumerate(self.lights):
            o = W.lamp(i)
            o.location = tuple(C3 @ pos)
            o.data.color = lin(color)
            o.data.energy = energy
            o.data.shadow_soft_size = radius
            o.data.use_shadow = bool(shadow)
            o.hide_render = False
        for o in W.lamp_pool[len(self.lights):]:
            o.hide_render = True

    def _camera(self):
        W = world()
        if (self.outW, self.outH) == (1080, 1920):
            rx, ry = RENDER_W, RENDER_H
        else:
            k = min(1.5, 900 / max(self.outW, self.outH))
            rx, ry = int(self.outW * k), int(self.outH * k)
        if (W.scene.render.resolution_x, W.scene.render.resolution_y) != (rx, ry):
            W.scene.render.resolution_x, W.scene.render.resolution_y = rx, ry
        R = np.eye(4)
        R[:3, 0] = C3 @ self.r
        R[:3, 1] = C3 @ self.u
        R[:3, 2] = -(C3 @ self.f)
        R[:3, 3] = C3 @ self.cam
        W.cam.matrix_world = Matrix(R.tolist())
        cd = W.cam.data
        cd.angle = 2 * math.atan((self.H / 2) / self.fl)
        cd.shift_x = 0.0
        cd.shift_y = (self.cy / self.H) - 0.5
        if self.dof:
            focus, rad = self.dof
            cd.dof.use_dof = True
            cd.dof.focus_distance = focus
            cd.dof.aperture_fstop = max(0.9, 24.0 / max(rad, 0.5) * (focus / 6.0))
        else:
            cd.dof.use_dof = False
        top, bot = (lin(self.col(c)) for c in self.sky)
        W.sky_top.default_value = top + [1.0]
        W.sky_bot.default_value = bot + [1.0]
        amb = [0.55 * top[0] + 0.45 * bot[0], 0.55 * top[1] + 0.45 * bot[1], 0.55 * top[2] + 0.45 * bot[2]]
        W.amb.inputs["Color"].default_value = amb + [1.0]
        # night: the sun becomes a dim cool moon and the sky fill drops
        n = clamp(self.night)
        W.amb.inputs["Strength"].default_value = 0.62 * (1 - n) + 0.55 * n
        W.sun.data.energy = 2.7 * (1 - n) + 0.85 * n
        if n > 0:
            # night: the moon keys from behind the camera (above, to the left), so faces facing us read
            src = -self.f * 0.75 + self.u * 0.65 - self.r * 0.4
            zb = C3 @ (src / np.linalg.norm(src))
            xb = np.cross([0, 0, 1.0], zb)
            xb = xb / max(1e-6, np.linalg.norm(xb))
            yb = np.cross(zb, xb)
            Rm = np.eye(4)
            Rm[:3, 0], Rm[:3, 1], Rm[:3, 2] = xb, yb, zb
            W.sun.matrix_world = Matrix(Rm.tolist())
        else:
            W.sun.matrix_world = W.sun_day
        W.star_k.default_value = 2.5 * max(0.0, n - 0.7) / 0.3
        W.sun.data.color = tuple((1 - n) * a + n * b for a, b in zip((1.0, 0.95, 0.86), (0.62, 0.72, 1.0)))

    def render(self):
        W = world()
        self._sync()
        self._camera()
        bpy.ops.render.render(write_still=True)
        img = Image.open(W.tmp).convert("RGB").resize((self.outW, self.outH), Image.LANCZOS)
        if self.bloom > 0:
            # bloom from the rendered frame itself, so anything in front of a lamp blocks its glow
            q = (img.size[0] // 4, img.size[1] // 4)
            bright = img.resize(q, Image.BILINEAR).point(lambda v: max(0, v - 150) * 2.4)
            for r, k in ((5, 1.0), (16, 0.9)):
                g = bright.filter(ImageFilter.GaussianBlur(r)).point(lambda v, k=k: min(255, int(v * k * self.bloom)))
                img = ImageChops.screen(img, g.resize(img.size, Image.BILINEAR))
        # 2D layer: sprites (sparks, glows), emotes and other overlays, drawn supersampled
        ov = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov, "RGBA")
        for it in sorted(self.items, key=lambda it: (it[0], it[1], it[2])):
            if it[2] == -1:
                continue  # painted sun disc: not needed with real lighting
            it[3](d)
        for fn in self.overlays:
            fn(d, self.W, self.H)
        ov = ov.reduce(SS) if SS > 1 else ov
        img.paste(ov, (0, 0), ov)
        if self.post:
            small = img.resize((img.size[0] // 6, img.size[1] // 6), Image.BILINEAR)
            small = small.point(lambda v: max(0, v - 165) * 2.0).filter(ImageFilter.GaussianBlur(7))
            img = Image.blend(img, ImageChops.screen(img, small.resize(img.size, Image.BILINEAR)), 0.25)
            img = Image.composite(img, Image.new("RGB", img.size, self.col((20, 14, 50))), vignette(img.size))
        if self.flash > 0:
            img = Image.blend(img, Image.new("RGB", img.size, (255, 255, 255)), clamp(self.flash))
        if self.fade > 0:
            img = Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), clamp(self.fade))
        return img


def _cyl_shot_z(length, radius):
    """Cylinder along shot-space z (so the M built in line3 orients it)."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=radius, radius2=radius, depth=length)
    # create_cone is along Blender Z (= shot y); rotate so it runs along Blender -Y (= shot z)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    return _finish(bm, "cyl", smooth=True)


engine.Scene = BScene
