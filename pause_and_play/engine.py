"""Tiny software 3D renderer for blocky toy scenes.

Pillow + NumPy only. Boxes are flat-shaded, painter-sorted per box, drawn at
SS x supersampling and box-filtered down. Colour grades (paused-time blue,
flashback sepia) are applied per colour at draw time so that "live" objects
can stay in full colour inside a graded scene.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "fonts", "Montserrat-ExtraBold.woff")
SS = 2
NEAR = 0.15
LIGHT = np.array([0.35, 0.85, 0.4])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

_font_cache = {}


def font(size):
    size = max(4, int(size))
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(FONT_PATH, size)
    return _font_cache[size]


# ---------------------------------------------------------------- transforms
def T(x, y, z):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def _rot(axis, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4)
    i, j = {"x": (1, 2), "y": (2, 0), "z": (0, 1)}[axis]
    m[i, i] = c
    m[i, j] = -s
    m[j, i] = s
    m[j, j] = c
    return m


def RX(d):
    return _rot("x", d)


def RY(d):
    return _rot("y", d)


def RZ(d):
    return _rot("z", d)


def xf(M, p):
    return M[:3, :3] @ np.asarray(p, float) + M[:3, 3]


def lerp(a, b, u):
    return a + (b - a) * u


def lerp3(a, b, u):
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def ease(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def pop(u):
    u = clamp(u)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (u - 1) ** 3 + c1 * (u - 1) ** 2


# -------------------------------------------------------------------- grades
def grade_color(c, mode, mix):
    if not mode or mix <= 0:
        return tuple(int(clamp(v, 0, 255)) for v in c[:3])
    r, g, b = c[:3]
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    if mode == "blue":
        t = (lerp(r, lum, 0.7) * 0.55 + 8, lerp(g, lum, 0.7) * 0.78 + 22, lerp(b, lum, 0.7) * 1.0 + 55)
    elif mode == "sepia":
        t = (lum * 1.05 + 28, lum * 0.88 + 14, lum * 0.62 + 4)
    else:
        t = (r, g, b)
    return tuple(int(clamp(lerp(c[i], t[i], mix), 0, 255)) for i in range(3))


def shade(c, f):
    return (c[0] * f, c[1] * f, c[2] * f)


_BOX_CORNERS = np.array([[sx, sy, sz] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)], float) * 0.5
# faces: corner indices (CCW seen from outside) and normal
_BOX_FACES = [
    ((4, 6, 7, 5), (1, 0, 0)),
    ((0, 1, 3, 2), (-1, 0, 0)),
    ((2, 3, 7, 6), (0, 1, 0)),
    ((0, 4, 5, 1), (0, -1, 0)),
    ((1, 5, 7, 3), (0, 0, 1)),   # front (+z): bl, br, tr, tl
    ((0, 2, 6, 4), (0, 0, -1)),
]


class Decal:
    """Maps face-local (u, v) in [-1, 1]^2 (v up) to screen via bilinear."""

    def __init__(self, draw, bl, br, tr, tl, colfn):
        self.d = draw
        self.c = [np.array(p[:2]) for p in (bl, br, tr, tl)]
        self.col = colfn
        self.k = 0.25 * (np.linalg.norm(self.c[1] - self.c[0]) + np.linalg.norm(self.c[2] - self.c[3]))
        self.kv = 0.25 * (np.linalg.norm(self.c[3] - self.c[0]) + np.linalg.norm(self.c[2] - self.c[1]))

    def pt(self, u, v):
        a, b = (u + 1) / 2, (v + 1) / 2
        bl, br, tr, tl = self.c
        p = (bl * (1 - a) + br * a) * (1 - b) + (tl * (1 - a) + tr * a) * b
        return (float(p[0]), float(p[1]))

    def poly(self, pts, fill):
        self.d.polygon([self.pt(u, v) for u, v in pts], fill=self.col(fill))

    def line(self, pts, fill, w=0.06):
        self.d.line([self.pt(u, v) for u, v in pts], fill=self.col(fill), width=max(1, int(w * self.k)), joint="curve")

    def ell(self, cu, cv, ru, rv, fill, n=20, rot=0):
        cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            x, y = ru * math.cos(a), rv * math.sin(a)
            pts.append((cu + x * cr - y * sr, cv + x * sr + y * cr))
        self.poly(pts, fill)

    def arc(self, cu, cv, ru, rv, a0, a1, fill, w=0.06, n=12):
        pts = []
        for i in range(n + 1):
            a = math.radians(lerp(a0, a1, i / n))
            pts.append((cu + ru * math.cos(a), cv + rv * math.sin(a)))
        self.line(pts, fill, w)

    def rect(self, u0, v0, u1, v1, fill):
        self.poly([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], fill)

    def text(self, cu, cv, txt, fill, h=0.5):
        f = font(max(6, h * 2 * self.kv))
        x, y = self.pt(cu, cv)
        self.d.text((x, y), txt, font=f, fill=self.col(fill), anchor="mm")


class Scene:
    def __init__(self, cam, tgt, fov=40, W=1080, H=1920, sky=((120, 190, 255), (215, 238, 255)),
                 grade=None, gmix=1.0, cy=0.38, roll=0.0):
        self.W, self.H = W * SS, H * SS
        self.outW, self.outH = W, H
        self.cam = np.asarray(cam, float)
        f = np.asarray(tgt, float) - self.cam
        self.f = f / np.linalg.norm(f)
        up = np.array([0.0, 1.0, 0.0])
        if abs(self.f[1]) > 0.999:
            up = np.array([0.0, 0.0, -1.0])
        r = np.cross(self.f, up)
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, self.f)
        if roll:
            a = math.radians(roll)
            self.r, self.u = (self.r * math.cos(a) + self.u * math.sin(a),
                              self.u * math.cos(a) - self.r * math.sin(a))
        self.fl = (self.H / 2) / math.tan(math.radians(fov) / 2)
        self.cx, self.cy = self.W / 2, self.H * cy
        self.sky = sky
        self.grade, self.gmix = grade, gmix
        self.items = []
        self.overlays = []
        self.flash = 0.0
        self.fade = 0.0

    # -- colour / projection helpers
    def col(self, c, live=False):
        if live:
            return tuple(int(clamp(v, 0, 255)) for v in c[:3]) + tuple(c[3:4])
        return grade_color(c, self.grade, self.gmix) + tuple(c[3:4])

    def to_cam(self, p):
        d = np.asarray(p, float) - self.cam
        return np.array([d @ self.r, d @ self.u, d @ self.f])

    def proj_c(self, c):
        z = max(c[2], 1e-3)
        return (self.cx + self.fl * c[0] / z, self.cy - self.fl * c[1] / z)

    def project(self, p):
        c = self.to_cam(p)
        x, y = self.proj_c(c)
        return x, y, c[2]

    def px_per_unit(self, p):
        return self.fl / max(self.to_cam(p)[2], 1e-3)

    def _clip(self, cpts):
        out = []
        n = len(cpts)
        for i in range(n):
            a, b = cpts[i], cpts[(i + 1) % n]
            ina, inb = a[2] >= NEAR, b[2] >= NEAR
            if ina:
                out.append(a)
            if ina != inb:
                t = (NEAR - a[2]) / (b[2] - a[2])
                out.append(a + (b - a) * t)
        return out

    # -- primitives
    def box(self, M, size, color, layer=5, decal=None, live=False, outline=True, lit=True, bias=0.0,
            decal_face=4):
        size = np.asarray(size, float)
        corners = (_BOX_CORNERS * size) @ M[:3, :3].T + M[:3, 3]
        center = M[:3, 3]
        depth = float(np.linalg.norm(center - self.cam)) + bias
        Rm = M[:3, :3]

        def draw(d):
            for fi, (idx, n) in enumerate(_BOX_FACES):
                nw = Rm @ np.array(n, float)
                fc = corners[list(idx)].mean(axis=0)
                if nw @ (self.cam - fc) <= 0:
                    continue
                cp = [self.to_cam(corners[i]) for i in idx]
                clipped = self._clip(cp)
                if len(clipped) < 3:
                    continue
                k = (0.76 + 0.28 * max(0.0, float(nw @ LIGHT))) if lit else 1.0
                fill = self.col(shade(color, k), live)
                pts = [self.proj_c(c) for c in clipped]
                if outline:
                    d.polygon(pts, fill=fill, outline=self.col(shade(color, k * 0.72), live), width=SS)
                else:
                    d.polygon(pts, fill=fill)
                if decal and fi == decal_face and len(clipped) == 4 and all(c[2] > NEAR for c in cp):
                    dc = Decal(d, *[self.proj_c(c) for c in cp], lambda c: self.col(c, live))
                    dc.lit = k
                    decal(dc)

        self.items.append((layer, -depth, len(self.items), draw))

    def quad(self, pts, color, layer=1, live=False, outline=None, depth_pt=None):
        pts = [np.asarray(p, float) for p in pts]
        ctr = np.mean(pts, axis=0) if depth_pt is None else np.asarray(depth_pt, float)
        depth = float(np.linalg.norm(ctr - self.cam))

        def draw(d):
            clipped = self._clip([self.to_cam(p) for p in pts])
            if len(clipped) < 3:
                return
            pp = [self.proj_c(c) for c in clipped]
            if outline:
                d.polygon(pp, fill=self.col(color, live), outline=self.col(outline, live), width=SS)
            else:
                d.polygon(pp, fill=self.col(color, live))

        self.items.append((layer, -depth, len(self.items), draw))

    def line3(self, a, b, color, width=0.05, layer=5, live=False, bias=0.0):
        a, b = np.asarray(a, float), np.asarray(b, float)
        depth = float(np.linalg.norm((a + b) / 2 - self.cam)) + bias

        def draw(d):
            ca, cb = self.to_cam(a), self.to_cam(b)
            cl = self._clip([ca, cb])
            if len(cl) < 2:
                return
            w = max(1, int(width * self.fl / max((ca[2] + cb[2]) / 2, NEAR)))
            d.line([self.proj_c(cl[0]), self.proj_c(cl[1])], fill=self.col(color, live), width=w)

        self.items.append((layer, -depth, len(self.items), draw))

    def sprite(self, pos, fn, layer=5, bias=0.0, live=False):
        """fn(draw, x, y, s, col): s = supersampled px per world unit."""
        pos = np.asarray(pos, float)
        depth = float(np.linalg.norm(pos - self.cam)) + bias

        def draw(d):
            x, y, z = self.project(pos)
            if z < NEAR:
                return
            fn(d, x, y, self.fl / z, lambda c: self.col(c, live))

        self.items.append((layer, -depth, len(self.items), draw))

    def overlay(self, fn):
        """fn(draw, W, H) in supersampled px, drawn after the 3D pass."""
        self.overlays.append(fn)

    def ground(self, color, y=0.0, size=400, layer=0):
        s = size
        self.quad([(-s, y, -s), (s, y, -s), (s, y, s), (-s, y, s)], color, layer=layer,
                  depth_pt=(0, y, -1e5))

    # -- render
    def _sky_img(self):
        top, bot = self.col(self.sky[0]), self.col(self.sky[1])
        g = np.linspace(0, 1, self.H)[:, None]
        col = (np.array(top[:3])[None, :] * (1 - g) + np.array(bot[:3])[None, :] * g).astype(np.uint8)
        return Image.fromarray(np.repeat(col[:, None, :], self.W, axis=1), "RGB")

    def render(self):
        img = self._sky_img()
        d = ImageDraw.Draw(img, "RGBA")
        for _, _, _, fn in sorted(self.items, key=lambda it: (it[0], it[1], it[2])):
            fn(d)
        for fn in self.overlays:
            fn(d, self.W, self.H)
        img = img.reduce(SS) if SS > 1 else img
        if self.flash > 0:
            img = Image.blend(img, Image.new("RGB", img.size, (255, 255, 255)), clamp(self.flash))
        if self.fade > 0:
            img = Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), clamp(self.fade))
        return img


# ------------------------------------------------------------------- shapes
def star_pts(x, y, r, n=5, inner=0.45, rot=-90):
    pts = []
    for i in range(n * 2):
        a = math.radians(rot + i * 180 / n)
        rr = r if i % 2 == 0 else r * inner
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return pts


def circle_pts(x, y, rx, ry=None, n=24):
    ry = rx if ry is None else ry
    return [(x + rx * math.cos(2 * math.pi * i / n), y + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def glow(d, x, y, r, color, alpha=120, rings=6):
    for i in range(rings, 0, -1):
        rr = r * i / rings
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=tuple(color) + (int(alpha / rings * 1.6),))


# ------------------------------------------------------------------- emotes
DARK = (40, 28, 48)


def _txt(d, x, y, s, t, fill, stroke=DARK):
    f = font(s)
    d.text((x, y), t, font=f, fill=fill, anchor="mm", stroke_width=max(2, int(s * 0.09)), stroke_fill=stroke)


def emote_draw(kind, d, x, y, s, t=0.0):
    """Draw emote centred at (x, y); s = height in supersampled px; t seconds since start."""
    if kind == "!":
        _txt(d, x, y, s * 1.25, "!", (255, 70, 60))
    elif kind == "?":
        _txt(d, x, y, s * 1.2, "?", (255, 214, 60))
    elif kind == "sweat":
        w = s * 0.32
        pts = [(x, y - s * 0.5)] + circle_pts(x, y + s * 0.12, w, w, 16)[0:9] + [(x, y - s * 0.5)]
        pts = [(x, y - s * 0.5), (x + w * 0.95, y + s * 0.05)] + \
              [(x + w * math.cos(a), y + s * 0.14 + w * math.sin(a)) for a in np.linspace(0, math.pi, 12)] + \
              [(x - w * 0.95, y + s * 0.05)]
        d.polygon(pts, fill=(110, 200, 255), outline=(30, 90, 170), width=max(2, int(s * 0.05)))
        d.ellipse([x - w * 0.55, y + s * 0.0, x - w * 0.15, y + s * 0.2], fill=(235, 250, 255))
    elif kind == "anger":
        w = max(3, int(s * 0.12))
        r = s * 0.5
        for qx, qy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            cx, cy = x + qx * r, y + qy * r
            a0 = math.atan2(-qy, -qx)
            pts = [(cx + r * 0.78 * math.cos(a0 + da), cy + r * 0.78 * math.sin(a0 + da))
                   for da in np.linspace(-0.62, 0.62, 9)]
            d.line(pts, fill=DARK, width=w + max(4, int(s * 0.1)), joint="curve")
        for qx, qy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            cx, cy = x + qx * r, y + qy * r
            a0 = math.atan2(-qy, -qx)
            pts = [(cx + r * 0.78 * math.cos(a0 + da), cy + r * 0.78 * math.sin(a0 + da))
                   for da in np.linspace(-0.58, 0.58, 9)]
            d.line(pts, fill=(245, 45, 55), width=w, joint="curve")
    elif kind == "bulb":
        r = s * 0.36
        for i in range(8):
            a = math.radians(i * 45 + 22)
            if 60 < (i * 45 + 22) % 360 < 120:
                continue
            d.line([(x + r * 1.25 * math.cos(a), y - s * 0.08 + r * 1.25 * math.sin(a)),
                    (x + r * 1.6 * math.cos(a), y - s * 0.08 + r * 1.6 * math.sin(a))],
                   fill=(255, 225, 80), width=max(2, int(s * 0.07)))
        d.rectangle([x - r * 0.42, y + r * 0.6, x + r * 0.42, y + r * 1.25], fill=(150, 150, 165), outline=DARK,
                    width=max(2, int(s * 0.04)))
        d.ellipse([x - r, y - s * 0.08 - r, x + r, y - s * 0.08 + r], fill=(255, 232, 90), outline=DARK,
                  width=max(2, int(s * 0.05)))
        d.ellipse([x - r * 0.55, y - s * 0.08 - r * 0.6, x - r * 0.1, y - s * 0.08 - r * 0.15], fill=(255, 252, 215))
    elif kind == "zzz":
        for i, (ox, oy, k) in enumerate(((-0.25, 0.3, 0.5), (0.05, 0.0, 0.7), (0.4, -0.38, 0.95))):
            ph = (t * 1.2 + i * 0.25) % 1.0
            _txt(d, x + ox * s + ph * s * 0.08, y + oy * s - ph * s * 0.1, s * k, "Z", (255, 255, 255), (60, 80, 170))
    elif kind == "stars":
        for i in range(3):
            a = t * 5 + i * 2.094
            sx, sy = x + math.cos(a) * s * 0.6, y + math.sin(a) * s * 0.16
            d.polygon(star_pts(sx, sy, s * 0.24, rot=-90 + t * 200), fill=(255, 220, 60), outline=DARK,
                      width=max(2, int(s * 0.04)))
    elif kind == "tears":
        for sx in (-1, 1):
            for i in range(3):
                ph = (t * 2 + i / 3) % 1.0
                px, py = x + sx * (s * 0.35 + ph * s * 0.5), y + s * 0.1 - math.sin(ph * math.pi) * s * 0.5 + ph * s * 0.5
                r = s * 0.09
                d.ellipse([px - r, py - r, px + r, py + r], fill=(110, 200, 255), outline=(30, 90, 170), width=2)


def add_emote(sc, kind, anchor, t, size=0.9, dx=0.0, dy=0.75, hold=1.1, start=0.0):
    """Pop a cartoon emote above a world anchor for about a second."""
    tt = t - start
    if tt < 0 or tt > hold:
        return
    k = pop(tt / 0.17) if tt < 0.17 else 1.0
    k *= clamp((hold - tt) / 0.1)
    x, y, z = sc.project(anchor)
    s = sc.fl / max(z, NEAR)
    px, py = x + dx * s, y - dy * s - math.sin(tt * 7) * s * 0.03

    def fn(d, W, H):
        emote_draw(kind, d, px, py, size * s * k, tt)

    sc.overlay(fn)


def speed_lines(sc, t, cx=0.5, cy=0.36, n=26, color=(255, 255, 255), seed=1, inner=0.33, alpha=200):
    rng = np.random.RandomState(seed + int(t * 15))

    def fn(d, W, H):
        for _ in range(n):
            a = rng.uniform(0, 2 * math.pi)
            r0 = rng.uniform(inner, inner + 0.25) * H
            r1 = r0 + rng.uniform(0.1, 0.4) * H
            x0, y0 = cx * W + math.cos(a) * r0, cy * H + math.sin(a) * r0
            x1, y1 = cx * W + math.cos(a) * r1, cy * H + math.sin(a) * r1
            d.line([(x0, y0), (x1, y1)], fill=tuple(color) + (alpha,), width=int(rng.uniform(4, 14) * SS / 2))

    sc.overlay(fn)


def streaks(sc, t, n=14, angle=0.0, color=(255, 255, 255), seed=3, ymax=0.62):
    """Horizontal-ish wind streaks scrolling across the frame."""
    rng = np.random.RandomState(seed)
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))

    def fn(d, W, H):
        for i in range(n):
            y = rng.uniform(0.02, ymax) * H
            ln = rng.uniform(0.12, 0.4) * W
            sp = rng.uniform(1.5, 3.0)
            x = ((rng.uniform(0, 1) + t * sp) % 1.4 - 0.2) * W
            d.line([(x, y), (x - ln * ca, y - ln * sa)], fill=tuple(color) + (170,), width=int(rng.uniform(3, 9) * SS / 2))

    sc.overlay(fn)


# ----------------------------------------------------------------- captions
_cap_cache = {}
CAP_Y = 0.63
CAP_SIZE = 86  # Montserrat ExtraBold cap height ~= 62 px at this size


def caption_sprite(word, W=1080):
    if word in _cap_cache:
        return _cap_cache[word]
    size = CAP_SIZE
    f = font(size)
    while f.getlength(word) > W - 120 and size > 40:
        size -= 4
        f = font(size)
    w, h = int(f.getlength(word)) + 80, int(size * 1.6) + 60
    sh = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sh).text((w // 2, h // 2 + 6), word, font=f, fill=200, anchor="mm", stroke_width=7)
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    spr = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    spr.putalpha(sh)
    ImageDraw.Draw(spr).text((w // 2, h // 2), word, font=f, fill=(255, 255, 255, 255), anchor="mm",
                             stroke_width=4, stroke_fill=(26, 20, 36, 255))
    _cap_cache[word] = spr
    return spr


def draw_caption(img, word, alpha=1.0):
    if not word or alpha <= 0:
        return img
    spr = caption_sprite(word, img.size[0])
    if alpha < 1:
        spr = spr.copy()
        spr.putalpha(spr.getchannel("A").point(lambda v: int(v * alpha)))
    x = (img.size[0] - spr.size[0]) // 2
    y = int(img.size[1] * CAP_Y) - spr.size[1] // 2
    img.paste(spr, (x, y), spr)
    return img
