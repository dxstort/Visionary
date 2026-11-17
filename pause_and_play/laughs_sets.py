"""Sets and props for The Floating Laughs: Benny's home, dining room, classroom ceiling, garage,
the Sky Festival park with its water tower, Uncle Ray's cloud, Mittens, a dog, iron boots and stickers."""
import math

import numpy as np

import porch_sets as ps
import sets
from engine import RX, RY, RZ, T, font, glow, xf

SKY = ((95, 175, 255), (205, 235, 255))
DAY_GLASS = (170, 214, 244)
HOME_COLOR = (112, 190, 232)
TOWER = np.array([6.0, 0.0, -9.0])   # water tower base centre (park)
TANK_Y = 13.0                        # tank centre height
LEG = 1.7                            # legs at (+-LEG, +-LEG) round the base
TANK_TOP = TANK_Y + 2.0


# ------------------------------------------------------------------ stickers
def sticker(sc, anchor, text, t, start=0.0, hold=1.4, size=0.5, color=(255, 230, 80), dx=0.0, dy=0.6, rot=-8):
    """Pop-in cartoon word sticker ("HA HA", "CRACK!") above a world anchor."""
    tt = t - start
    if tt < 0 or tt > hold:
        return
    k = min(1.0, tt / 0.14)
    k = 1.0 + 0.25 * math.sin(k * math.pi) if tt < 0.14 else 1.0
    x, y, z = sc.project(np.asarray(anchor, float))
    if z < 0.2:
        return
    s = sc.fl / z
    px, py = x + dx * s, y - dy * s - math.sin(tt * 8) * s * 0.02

    def fn(d, W, H):
        from PIL import Image, ImageDraw
        sz = max(8, int(size * s * k))
        f = font(sz)
        w = int(f.getlength(text)) + sz
        im = Image.new("RGBA", (w, int(sz * 1.6)), (0, 0, 0, 0))
        di = ImageDraw.Draw(im)
        di.text((w / 2, sz * 0.8), text, font=f, fill=color + (255,), anchor="mm", stroke_width=max(2, sz // 8),
                stroke_fill=(40, 28, 48, 255))
        im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
        d._image.paste(im, (int(px - im.width / 2), int(py - im.height / 2)), im)

    sc.overlay(fn)


def moon_cow(sc, anchor, t, start=0.0, hold=1.6, size=1.0):
    """'To see the moon' sticker: a crescent moon with a little cow jumping over it."""
    tt = t - start
    if tt < 0 or tt > hold:
        return
    x, y, z = sc.project(np.asarray(anchor, float))
    s = sc.fl / max(z, 0.2) * size * min(1.0, tt / 0.15)

    def fn(d, W, H):
        r = 0.55 * s
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 236, 140, 255), outline=(40, 28, 48, 255), width=int(s * 0.04))
        d.ellipse([x - r * 0.45, y - r * 1.05, x + r * 1.35, y + r * 0.75], fill=(0, 0, 0, 0))
        cx, cy = x + r * 0.2, y - r * 1.15 - 0.15 * s * math.sin(tt * 4)
        b = 0.24 * s
        d.rounded_rectangle([cx - b, cy - b * 0.55, cx + b, cy + b * 0.55], int(b * 0.3), fill=(255, 255, 255, 255),
                            outline=(40, 28, 48, 255), width=int(s * 0.03))
        for ox, oy in ((-0.4, -0.1), (0.3, 0.15)):
            d.ellipse([cx + ox * b - b * 0.25, cy + oy * b - b * 0.22, cx + ox * b + b * 0.25, cy + oy * b + b * 0.22],
                      fill=(40, 28, 48, 255))
        hx = cx + b * 1.15
        d.ellipse([hx - b * 0.45, cy - b * 0.7, hx + b * 0.45, cy + b * 0.2], fill=(255, 255, 255, 255),
                  outline=(40, 28, 48, 255), width=int(s * 0.03))
        d.ellipse([hx - b * 0.2, cy - b * 0.15, hx + b * 0.4, cy + b * 0.2], fill=(255, 170, 180, 255))
        for lx in (-0.6, -0.2, 0.3, 0.7):
            d.line([(cx + lx * b, cy + b * 0.5), (cx + lx * b + b * 0.15, cy + b * 1.0)], fill=(40, 28, 48, 255),
                   width=int(s * 0.05))

    sc.overlay(fn)


# --------------------------------------------------------------------- props
def iron_boot(sc, M, s=1.0, text=None, color=(96, 100, 112)):
    """A single big iron boot (toe toward +z), optionally stamped with a size on its side."""
    def stamp(D):
        D.rect(-1, -1, 1, 1, color)
        for k in range(-6, 7):
            D.line([(-1, k / 6), (1, k / 6)], tuple(v * 0.94 for v in color), 0.01)
        if text:
            ps.fit_text(D, [text], (40, 40, 48), aspect=1.0, fill_w=0.6, fill_h=0.5)

    sc.box(M @ T(0, 0.45 * s, -0.1 * s), (0.7 * s, 0.9 * s, 0.75 * s), color, layer=5, decal=stamp if text else None)
    sc.box(M @ T(0, 0.18 * s, 0.25 * s), (0.72 * s, 0.36 * s, 0.85 * s), color, layer=5)
    sc.box(M @ T(0, 0.04 * s, 0.15 * s), (0.78 * s, 0.08 * s, 1.15 * s), (60, 62, 70), layer=5)
    sc.box(M @ T(0, 0.75 * s, -0.1 * s), (0.74 * s, 0.14 * s, 0.79 * s), (56, 52, 50), layer=5)
    sc.box(M @ T(0.39 * s, 0.75 * s, 0.05 * s), (0.05 * s, 0.16 * s, 0.18 * s), (236, 196, 80), layer=5)


def side_stamp(sc, M, text, s=1.0, color=(96, 100, 112)):
    """Flat side panel of a boot with a stamped number (for the 'Size 14' insert)."""
    def dec(D):
        D.rect(-1, -1, 1, 1, color)
        for k in range(-8, 9):
            D.line([(-1, k / 8), (1, k / 8)], tuple(v * 0.93 for v in color), 0.006)
        D.ell(-0.75, 0.75, 0.06, 0.06, (70, 72, 80), n=10)
        D.ell(0.75, 0.75, 0.06, 0.06, (70, 72, 80), n=10)
        ps.fit_text(D, [text], (44, 44, 52), aspect=1.0, fill_w=0.7, fill_h=0.6)

    sc.box(M, (3.4 * s, 3.4 * s, 0.3 * s), color, layer=5, decal=dec)


def fridge(sc, M):
    sc.box(M @ T(0, 1.7, 0), (1.6, 3.4, 1.4), (244, 246, 248), layer=4)
    sc.box(M @ T(0, 2.25, 0.71), (1.58, 0.04, 0.04), (200, 204, 210), layer=4)
    for y in (1.4, 2.9):
        sc.box(M @ T(-0.62, y, 0.74), (0.08, 0.6, 0.1), (190, 194, 200), layer=4)
    for i, c in enumerate(((255, 120, 120), (120, 200, 255), (255, 220, 90))):
        sc.box(M @ T(0.1 + i * 0.25, 2.9 - (i % 2) * 0.2, 0.72), (0.16, 0.16, 0.04), c, layer=4)


def pickle(sc, M, s=1.0):
    g = (110, 170, 70)
    sc.blob(M @ RZ(20), (0.42 * s, 1.2 * s, 0.42 * s), g, e=0.9, layer=6, n=16, m=10)
    rng = np.random.RandomState(4)
    for _ in range(14):
        a, v = rng.uniform(0, 2 * math.pi), rng.uniform(-0.45, 0.45)
        p = (0.2 * s * math.cos(a), v * s, 0.2 * s * math.sin(a))
        sc.blob(M @ RZ(20) @ T(*p), (0.07 * s, 0.07 * s, 0.07 * s), (90, 150, 60), layer=6, n=6, m=4)


def sock(sc, M, pattern="stripes", c1=(240, 90, 110), c2=(255, 255, 255)):
    def dec(D):
        D.rect(-1, -1, 1, 1, c1)
        if pattern == "stripes":
            for k in range(-5, 6, 2):
                D.rect(-1, k / 5.5, 1, k / 5.5 + 0.18, c2)
        else:
            rng = np.random.RandomState(1)
            for _ in range(16):
                D.ell(rng.uniform(-0.9, 0.9), rng.uniform(-0.9, 0.9), 0.1, 0.1, c2, n=10)

    sc.box(M @ T(0, 0.55, 0), (0.42, 1.1, 0.16), c1, layer=6, decal=dec)
    sc.box(M @ T(0, 0.12, 0.25), (0.42, 0.24, 0.6), c1, layer=6, decal=dec)
    sc.box(M @ T(0, 1.08, 0), (0.44, 0.12, 0.18), c2, layer=6)


def cat(sc, M, t=0.0, mood="calm", fur=(240, 150, 70), s=1.0):
    """Mittens: blocky ginger cat, facing +z of M. mood: calm | scared | happy."""
    dk = tuple(int(v * 0.8) for v in fur)
    sc.box(M @ T(0, 0.32 * s, 0), (0.42 * s, 0.32 * s, 0.7 * s), fur, layer=6)
    for sx in (-1, 1):
        for sz in (-1, 1):
            sc.box(M @ T(sx * 0.14 * s, 0.1 * s, sz * 0.24 * s), (0.11 * s, 0.22 * s, 0.11 * s), fur, layer=6)
    for k in range(4):  # tail
        a = math.radians(30 + 15 * k + (10 * math.sin(t * 6 + k) if mood != "scared" else 40))
        sc.box(M @ T(0, (0.42 + 0.1 * k * math.sin(a)) * s, (-0.38 - 0.1 * k * math.cos(a)) * s),
               (0.08 * s, 0.12 * s, 0.08 * s), dk, layer=6)

    def face(D):
        eye = (40, 28, 48)
        if mood == "scared":
            for sx in (-1, 1):
                D.ell(sx * 0.42, 0.15, 0.26, 0.3, (255, 255, 255), n=14)
                D.ell(sx * 0.42, 0.15, 0.1, 0.12, eye, n=10)
            D.ell(0, -0.42, 0.12, 0.14, eye, n=10)
        else:
            for sx in (-1, 1):
                if mood == "happy":
                    D.arc(sx * 0.42, 0.05, 0.18, 0.14, 20, 160, eye, 0.07)
                else:
                    D.ell(sx * 0.42, 0.12, 0.13, 0.2, eye, n=12)
                    D.ell(sx * 0.42 + 0.04, 0.2, 0.04, 0.06, (255, 255, 255), n=8)
            D.arc(-0.1, -0.42, 0.1, 0.08, 200, 340, eye, 0.05)
            D.arc(0.1, -0.42, 0.1, 0.08, 200, 340, eye, 0.05)
        D.poly([(-0.08, -0.22), (0.08, -0.22), (0, -0.32)], (255, 150, 170))
        for sx in (-1, 1):
            for dy in (-0.25, -0.38):
                D.line([(sx * 0.3, dy), (sx * 0.85, dy + 0.06 * sx * 0)], (60, 40, 40), 0.02)
        D.rect(-1, 0.75, 1, 1, fur)

    H = M @ T(0, 0.62 * s, 0.33 * s)
    sc.box(H, (0.5 * s, 0.42 * s, 0.4 * s), fur, layer=6, decal=face)
    for sx in (-1, 1):
        v = [(0, 0.2 * s, 0), (-0.09 * s, 0, -0.06 * s), (0.09 * s, 0, -0.06 * s), (0, 0, 0.08 * s)]
        sc.solid(H @ T(sx * 0.16 * s, 0.2 * s, 0), v, [(0, 1, 2), (0, 2, 3), (0, 3, 1), (1, 3, 2)], dk, layer=6)
    return xf(H, (0, 0.35 * s, 0))


def dog(sc, M, t=0.0, fur=(196, 140, 90), hat=True):
    dk = tuple(int(v * 0.75) for v in fur)
    sc.box(M @ T(0, 0.55, 0), (0.6, 0.5, 1.1), fur, layer=5)
    for sx in (-1, 1):
        for sz in (-1, 1):
            sc.box(M @ T(sx * 0.2, 0.18, sz * 0.38), (0.16, 0.36, 0.16), fur, layer=5)
    sc.box(M @ T(0, 0.9, -0.62) @ RX(-40 + 20 * math.sin(t * 18)), (0.1, 0.4, 0.1), dk, layer=5)

    def face(D):
        for sx in (-1, 1):
            D.ell(sx * 0.4, 0.2, 0.13, 0.17, (40, 28, 48), n=12)
            D.ell(sx * 0.4 + 0.04, 0.27, 0.04, 0.05, (255, 255, 255), n=8)
        D.ell(0, -0.28, 0.22, 0.15, (40, 28, 48), n=12)
        D.arc(0, -0.5, 0.25, 0.15, 200, 340, (40, 28, 48), 0.05)
        D.ell(0.1, -0.68, 0.1, 0.12, (240, 110, 130), n=10)

    H = M @ T(0, 1.0, 0.62)
    sc.box(H, (0.56, 0.5, 0.5), fur, layer=5, decal=face)
    for sx in (-1, 1):
        sc.box(H @ T(sx * 0.32, 0.05, -0.05) @ RZ(sx * 15), (0.12, 0.38, 0.22), dk, layer=5)
    if hat:
        ps.party_hat(sc, H @ T(0.05, 0.25, 0) @ RZ(-12) @ T(0, 0, 0), color=(90, 160, 255))
    return xf(H, (0, 0.4, 0))


def megaphone(sc, M):
    v = [(0, 0, 0)]
    n = 10
    for i in range(n):
        a = 2 * math.pi * i / n
        v.append((0.12 * math.cos(a), 0.12 * math.sin(a), 0.0))
    for i in range(n):
        a = 2 * math.pi * i / n
        v.append((0.38 * math.cos(a), 0.38 * math.sin(a), 0.75))
    f = [(1 + i, 1 + (i + 1) % n, 1 + n + (i + 1) % n, 1 + n + i) for i in range(n)]
    sc.solid(M, v, f + [tuple(range(n, 0, -1))], (240, 240, 244), layer=7)
    sc.box(M @ T(0, -0.2, 0.15), (0.1, 0.32, 0.12), (230, 70, 60), layer=7)
    sc.box(M @ T(0, 0, 0.78), (0.8, 0.8, 0.04), (230, 70, 60), layer=7)


def joke_book(sc, M, title="JOKES", color=(230, 80, 70), open_k=0.0):
    def cover_d(D):
        D.rect(-1, -1, 1, 1, color)
        D.rect(-0.8, -0.8, 0.8, 0.8, tuple(min(255, v + 30) for v in color))
        ps.fit_text(D, [title], (255, 250, 220), aspect=0.7 / 0.9, fill_w=0.8, fill_h=0.4)

    if open_k <= 0:
        sc.box(M @ T(0, 0.08, 0), (0.7, 0.16, 0.9), color, layer=6)
        sc.box(M @ T(0, 0.165, 0), (0.7, 0.01, 0.9), color, layer=6, decal=None)
        sc.box(M @ T(0, 0.17, 0) @ RX(-90), (0.7, 0.9, 0.01), color, layer=6, decal=cover_d)
    else:
        for sx in (-1, 1):
            P = M @ RZ(sx * 8 * open_k) @ T(sx * 0.36, 0.04, 0)
            sc.box(P, (0.7, 0.06, 0.9), (250, 248, 236), layer=6)
            sc.box(P @ T(0, -0.04, 0), (0.72, 0.03, 0.92), color, layer=6)
            for k in range(5):
                sc.box(P @ T(0, 0.035, -0.3 + k * 0.15), (0.5, 0.005, 0.03), (90, 90, 110), layer=6)


def balloon(sc, x, y, z, color, t=0.0, string=1.6):
    b = math.sin(t * 2 + x) * 0.1
    sc.blob(T(x + b, y, z), (0.55, 0.7, 0.55), color, layer=4, n=12, m=8)
    sc.line3((x + b, y - 0.35, z), (x, y - 0.35 - string, z), (240, 240, 240), width=0.02, layer=4)


def stall(sc, x, z, color, yaw=0, sign=None):
    M = T(x, 0, z) @ RY(yaw)

    def stripes(D):
        for k in range(-6, 6):
            D.rect(k / 6, -1, k / 6 + 1 / 12, 1, (255, 255, 255))
        D.rect(-1, -1, 1, -0.75, color)

    sc.box(M @ T(0, 0.6, 0), (2.6, 1.2, 1.2), (236, 214, 170), layer=3)
    sc.box(M @ T(0, 1.2, 0.05), (2.7, 0.08, 1.3), (200, 170, 120), layer=3)
    for sx in (-1, 1):
        sc.box(M @ T(sx * 1.25, 1.5, 0.5), (0.1, 3.0, 0.1), (240, 240, 240), layer=3)
    sc.box(M @ T(0, 3.0, 0.35) @ RX(18), (2.9, 0.08, 1.6), color, layer=3, decal=stripes)
    if sign:
        def dec(D):
            D.rect(-1, -1, 1, 1, (255, 250, 230))
            ps.fit_text(D, [sign], (60, 40, 50), aspect=2.2 / 0.5)
        sc.box(M @ T(0, 2.45, 0.62), (2.2, 0.5, 0.05), (255, 250, 230), layer=3, decal=dec)


def kite(sc, x, y, z, color, t=0.0):
    M = T(x + 0.3 * math.sin(t * 1.5 + x), y + 0.2 * math.sin(t * 2 + z), z) @ RZ(15 * math.sin(t + x))
    v = [(0, 0.9, 0), (0.6, 0, 0), (0, -1.2, 0), (-0.6, 0, 0)]
    sc.solid(M, v, [(0, 1, 2, 3), (3, 2, 1, 0)], color, layer=1)
    for k in range(4):
        sc.box(M @ T(0.1 * math.sin(k + t * 3), -1.4 - k * 0.35, 0), (0.18, 0.1, 0.02), (255, 255, 255), layer=1)


def bunting(sc, a, b, n=14, colors=((255, 90, 90), (255, 214, 70), (90, 190, 255), (120, 220, 130))):
    a, b = np.asarray(a, float), np.asarray(b, float)
    for i in range(n):
        u0, u1 = i / n, (i + 0.8) / n
        sag = lambda u: np.array([0, -0.8 * 4 * u * (1 - u), 0])
        p0, p1 = a + (b - a) * u0 + sag(u0), a + (b - a) * u1 + sag(u1)
        mid = (p0 + p1) / 2 + np.array([0, -0.45, 0])
        sc.solid(np.eye(4), [tuple(p0), tuple(p1), tuple(mid)], [(0, 1, 2), (2, 1, 0)], colors[i % len(colors)],
                 layer=3)


def water_tower(sc, ladder="whole", fall_k=0.0):
    """Tall water tower at TOWER. ladder: whole | broken (lower half lying on the grass) | falling (fall_k 0..1)."""
    x0, _, z0 = TOWER
    steel = (176, 186, 200)
    for sx in (-1, 1):
        for sz in (-1, 1):
            sc.box(T(x0 + sx * LEG, 5.5, z0 + sz * LEG), (0.32, 11.0, 0.32), steel, layer=2)
    for y in (3.5, 7.5):
        for sz in (-1, 1):
            sc.box(T(x0, y, z0 + sz * LEG), (2 * LEG, 0.16, 0.16), steel, layer=2)
            sc.box(T(x0 + sz * LEG, y, z0), (0.16, 0.16, 2 * LEG), steel, layer=2)
    sc.box(T(x0, 11.05, z0), (5.6, 0.16, 5.6), (150, 160, 176), layer=2)  # catwalk
    for i in range(16):
        a = 2 * math.pi * i / 16
        sc.box(T(x0 + 2.75 * math.cos(a), 11.55, z0 + 2.75 * math.sin(a)), (0.08, 1.0, 0.08), steel, layer=2)

    def tank_dec(D):
        D.rect(-1, -1, 1, 1, (236, 120, 110))
        D.rect(-1, -0.15, 1, 0.15, (255, 255, 255))
        ps.fit_text(D, ["SKY TOWN"], (230, 80, 70), aspect=3.0, fill_w=0.5, fill_h=0.25)

    sc.blob(T(x0, TANK_Y, z0), (4.6, 3.8, 4.6), (236, 120, 110), e=0.22, e2=1.0, layer=2, n=40, m=14, span=1.0,
            decal=tank_dec)
    roof = [(0, 1.6, 0)] + [(2.5 * math.cos(2 * math.pi * i / 12), 0, 2.5 * math.sin(2 * math.pi * i / 12))
                            for i in range(12)]
    sc.solid(T(x0, TANK_Y + 1.85, z0), roof, [(0, (i + 1) % 12 + 1, i + 1) for i in range(12)], (200, 90, 84), layer=2)
    # ladder up the front (+z) face, between the two front legs
    lz = z0 + LEG + 0.25

    def ladder_part(M, y0, y1):
        for sx in (-1, 1):
            sc.box(M @ T(sx * 0.32, (y0 + y1) / 2, 0), (0.08, y1 - y0, 0.08), (130, 96, 64), layer=3)
        y = y0 + 0.3
        while y < y1:
            sc.box(M @ T(0, y, 0), (0.64, 0.06, 0.08), (150, 112, 76), layer=3)
            y += 0.42

    ladder_part(T(x0, 0, lz), 5.5, 11.0)
    if ladder == "whole":
        ladder_part(T(x0, 0, lz), 0.0, 5.5)
    elif ladder in ("falling", "broken"):
        k = 1.0 if ladder == "broken" else fall_k
        ladder_part(T(x0, 0, lz + 0.05) @ RX(80 * k * k), 0.0, 5.5)
    return dict(top=np.array([x0, TANK_TOP + 0.1, z0 + 1.2]), lz=lz, catwalk=np.array([x0, 11.15, z0 + 2.6]))


def festival(sc, t=0.0, ladder="whole", fall_k=0.0, crowd=False):
    sets.park(sc)
    tw = water_tower(sc, ladder, fall_k)
    for i, (x, z, c, sign) in enumerate(((-6.0, -4.0, (255, 120, 120), "POPCORN"), (-11.0, -6.0, (120, 180, 255), "PIE"),
                                         (14.0, -4.5, (255, 200, 80), "LEMONADE"))):
        stall(sc, x, z, c, yaw=15 if x < 0 else -15, sign=sign)
    for x, y, z in ((-3, 4.2, -3), (-2.4, 4.8, -3.4), (11, 4.5, -3), (11.6, 5.1, -3.3), (-8.5, 4.4, -2.5)):
        balloon(sc, x, y, z, ((255, 90, 120), (255, 214, 70), (90, 190, 255), (150, 230, 120), (220, 130, 255))[int(x) % 5],
                t)
    for x, y, z, c in ((-14, 15, -25, (255, 90, 90)), (18, 17, -28, (90, 190, 255)), (-2, 19, -30, (255, 214, 70))):
        kite(sc, x, y, z, c, t)
    bunting(sc, (-10, 4.0, -2.0), (0, 4.0, -2.4))
    bunting(sc, (12, 4.0, -2.0), (20, 4.0, -3.0))
    for x in (-10, 0, 12, 20):
        sc.box(T(x, 2.0, -2.2), (0.12, 4.0, 0.12), (240, 240, 240), layer=3)
    return tw


def crowd_line(sc, specs, xs, z, yaw=0, faces=None, poses=None, live=False):
    from cast import character
    out = []
    for i, (spec, x) in enumerate(zip(specs, xs)):
        out.append(character(sc, spec, (x, 0, z + 0.25 * math.sin(i * 2.3)), yaw=yaw,
                             face=(faces[i % len(faces)] if faces else "neutral"),
                             pose=(poses[i % len(poses)] if poses else None), live=live))
    return out


# --------------------------------------------------------------- interiors
def home(sc, boots_row=False, garage_k=0.0, night=False, k=0.0):
    """Benny & Grandpa's house: porch house at the origin (front faces +z), garage to its right."""
    sc.ground(sets.GRASS if not night else (60, 110, 66))
    if not night:
        sets.clouds(sc, seed=3)
        sets.sun(sc, x=0.85, y=0.08)
    sets.flat(sc, -60, 60, 4.5, 8.0, (88, 92, 108))
    sets.flat(sc, -60, 60, 3.3, 4.5, (220, 214, 204))
    sets.flat(sc, -0.6, 0.6, 3.1, 4.5, (214, 208, 198), y=0.012)
    h = ps.porch_house(sc, 0, -2.0, HOME_COLOR, k=k, lamp_k=k, glass=None if night else DAY_GLASS)
    # garage: box to the right with a roll-up door
    gx = 5.4
    sc.box(T(gx, 1.6, -2.2), (3.6, 3.2, 3.8), (236, 230, 220), layer=2)
    sc.box(T(gx, 3.3, -2.2), (3.9, 0.22, 4.1), (100, 70, 64), layer=2)
    door_h = 2.4 * (1 - garage_k)
    if door_h > 0.05:
        def slats(D):
            for k_ in range(-6, 7):
                D.line([(-1, k_ / 6.5), (1, k_ / 6.5)], (200, 196, 190), 0.02)
        sc.box(T(gx, 2.6 - door_h / 2, -0.28), (2.8, door_h, 0.06), (226, 222, 214), layer=3, decal=slats)
    if garage_k > 0:
        sc.box(T(gx, 1.2, -0.32), (2.8, 2.4, 0.04), (255, 214, 140) if night else (60, 56, 60), layer=2, lit=not night)
    sets.flat(sc, gx - 1.5, gx + 1.5, -0.3, 4.5, (196, 192, 186), y=0.011)
    sets.tree(sc, -5.0, -0.5, 4.6)
    sets.bush(sc, -2.6, 0.6, 0.8)
    sets.bush(sc, 2.3, 0.6, 0.7)
    if boots_row:
        for i in range(5):
            iron_boot(sc, T(-1.0 + i * 0.5, 0.3, 0.75) @ RY(-10 + 6 * i), s=0.55 - 0.03 * i)
    return h


def dining(sc, ceiling=True, lamp=True):
    """Dining room: table along x at z = 0, window wall behind (z = -3), ceiling at y = 4.4."""
    sets.floor_tiles(sc, -7, 7, -3, 8, (176, 132, 96), (166, 124, 90), step=1.0)

    def paper(D):
        D.rect(-1, -1, 1, 1, (250, 226, 190))
        for k in range(-20, 21):
            D.line([(k / 20, -1), (k / 20, 1)], (244, 214, 176), 0.01)
        D.rect(-0.95, -1, 0.95, -0.82, (190, 140, 100))

    sets.wall(sc, 0, 3.0, -3.2, 14, 6, (250, 226, 190), decal=paper)
    for sx in (-1, 1):
        sets.wall(sc, sx * 6.8, 3.0, 2.0, 10, 6, (246, 220, 182), yaw=90)
    sc.box(T(-2.6, 2.6, -2.98), (1.8, 1.6, 0.05), (170, 214, 244), layer=2, lit=False)
    sc.box(T(-2.6, 2.6, -2.95), (0.08, 1.6, 0.06), (255, 255, 255), layer=2)
    sc.box(T(2.6, 2.7, -2.98), (1.3, 1.0, 0.05), (120, 90, 70), layer=2)
    sc.box(T(2.6, 2.7, -2.94), (1.1, 0.8, 0.04), (140, 200, 150), layer=2)
    if ceiling:
        sc.box(T(0, 4.5, 2.0), (14, 0.2, 12), (250, 246, 236), layer=1)
    if lamp:
        sc.box(T(0, 4.1, 0), (0.05, 0.8, 0.05), (60, 60, 70), layer=2)
        sc.blob(T(0, 3.6, 0), (0.9, 0.5, 0.9), (255, 230, 170), e=0.4, layer=2, lit=False)
    # table, chairs, food
    sc.box(T(0, 1.3, 0), (4.2, 0.14, 1.9), (170, 112, 72), layer=3)
    sc.box(T(0, 1.39, 0), (4.0, 0.02, 1.7), (255, 255, 255), layer=3)
    for sx in (-1, 1):
        for sz in (-1, 1):
            sc.box(T(sx * 1.9, 0.62, sz * 0.8), (0.14, 1.24, 0.14), (140, 92, 60), layer=3)
    for x in (-1.3, 0.0, 1.3):
        sets.plate(sc, T(x, 1.42, 0.45), crumbs=False)
        sc.blob(T(x, 1.5, 0.45), (0.45, 0.12, 0.35), (230, 200, 120), layer=4)
        sets.plate(sc, T(x, 1.42, -0.45), crumbs=False)
        sc.blob(T(x, 1.5, -0.45), (0.4, 0.14, 0.32), (190, 120, 80), layer=4)
    sc.blob(T(0, 1.55, 0), (0.6, 0.3, 0.6), (255, 255, 255), e=0.5, layer=4)
    sc.blob(T(0, 1.68, 0), (0.5, 0.18, 0.5), (120, 200, 110), layer=4)


def classroom_ceiling(sc):
    sets.classroom(sc)
    sc.box(T(0, 5.2, 1.0), (22, 0.2, 16), (246, 244, 236), layer=1)
    for x in (-4, 0, 4):
        sc.box(T(x, 5.05, -1.0), (2.4, 0.08, 0.5), (255, 255, 240), layer=1, lit=False)


def garage(sc, warm=True, books=True, boots=True, bulb_x=0.0):
    """Garage interior at night: bare bulb, workbench, shelf of joke books. Back wall z = -3."""
    sets.floor_tiles(sc, -6, 6, -3, 7, (150, 150, 156), (142, 142, 148), step=2.0)

    def boards(D):
        D.rect(-1, -1, 1, 1, (176, 140, 104))
        for k in range(-12, 13):
            D.line([(k / 12, -1), (k / 12, 1)], (150, 116, 84), 0.012)

    sets.wall(sc, 0, 3.0, -3.2, 12, 6, (176, 140, 104), decal=boards)
    for sx in (-1, 1):
        sets.wall(sc, sx * 5.4, 3.0, 1.5, 10, 6, (168, 132, 98), yaw=90)
    sc.box(T(0, 5.2, 1.0), (12, 0.2, 10), (120, 96, 76), layer=1)
    sc.box(T(bulb_x, 4.6, 0.2), (0.03, 1.0, 0.03), (40, 40, 40), layer=2)
    sc.blob(T(bulb_x, 4.0, 0.2), (0.28, 0.36, 0.28), (255, 240, 190), layer=2, lit=False)
    sc.light((bulb_x, 3.8, 0.4), (255, 196, 130), 260, 0.3)
    sc.box(T(-3.0, 1.1, -2.6), (3.2, 0.12, 1.0), (140, 100, 70), layer=3)  # workbench
    for sx in (-1, 1):
        sc.box(T(-3.0 + sx * 1.45, 0.55, -2.6), (0.12, 1.1, 0.9), (110, 80, 56), layer=3)
    sc.box(T(2.4, 2.6, -2.9), (3.6, 0.1, 0.5), (130, 96, 70), layer=3)  # shelf
    if books:
        for i, c in enumerate(((230, 80, 70), (90, 160, 230), (250, 200, 70), (120, 200, 120), (200, 120, 220),
                               (240, 140, 60), (90, 200, 200))):
            sc.box(T(1.0 + i * 0.42, 2.98, -2.85), (0.32, 0.66 + 0.08 * (i % 3), 0.42), c, layer=3)
    if boots:
        iron_boot(sc, T(-3.6, 0, 1.6) @ RY(30), s=0.7)
        iron_boot(sc, T(-3.0, 0, 1.9) @ RY(10), s=0.7)


def cloud_home(sc, t=0.0):
    """Uncle Ray's cloud: big cloud, hammock between two posts, a little TV."""
    sets.clouds(sc, seed=8, n=5, z=-60)
    for dx, dy, dz, k in ((0, 0, 0, 1.0), (-2.2, -0.3, 0.4, 0.75), (2.4, -0.2, 0.2, 0.8), (0.6, 0.6, -0.8, 0.7),
                          (-1.2, 0.4, -0.6, 0.65)):
        sc.blob(T(dx, dy, dz), (4.4 * k, 1.8 * k, 3.2 * k), (255, 255, 255), layer=2, n=14, m=8)
    for sx in (-1, 1):
        sc.box(T(sx * 1.6, 1.6, 0.0), (0.14, 1.6, 0.14), (150, 110, 80), layer=3)
    for i in range(9):
        u = -1.6 + i * 0.4
        sag = 0.5 * (1 - (u / 1.6) ** 2)
        sc.box(T(u, 2.1 - sag, 0.0), (0.42, 0.06, 0.9), (240, 110, 90) if i % 2 else (255, 230, 120), layer=3)
    sc.box(T(2.6, 1.6, 0.6) @ RY(-30), (1.0, 0.75, 0.5), (60, 60, 70), layer=3)
    sc.box(T(2.6, 1.62, 0.6) @ RY(-30) @ T(0, 0, 0.26), (0.8, 0.55, 0.02),
           (120, 200, 255) if int(t * 4) % 2 else (150, 230, 160), layer=3, lit=False)
    sc.box(T(2.6, 1.15, 0.6), (0.4, 0.2, 0.3), (80, 80, 90), layer=3)


def tumbleweed(sc, pos, t, r=0.5):
    p = np.asarray(pos, float)

    def fn(d, x, y, s, col):
        rr = r * s
        a0 = t * 6
        for i in range(10):
            a = a0 + i * 0.6
            d.arc([x - rr * (0.5 + 0.05 * i), y - rr * (0.5 + 0.05 * i), x + rr * (0.5 + 0.05 * i),
                   y + rr * (0.5 + 0.05 * i)], math.degrees(a), math.degrees(a) + 200, fill=(150, 112, 70, 255),
                  width=max(2, int(rr * 0.08)))

    sc.sprite(p, fn, layer=8, live=True)


def music_notes(sc, origin, t, n=4):
    ps.music_notes(sc, origin, t, n=n, color=(255, 236, 120))


def dust(sc, pos, t, start, n=6):
    tt = t - start
    if tt < 0 or tt > 0.5:
        return
    rng = np.random.RandomState(int(start * 100))
    for i in range(n):
        a = rng.uniform(0, math.pi)
        p = np.asarray(pos, float) + np.array([math.cos(a) * (0.3 + tt * 2), 0.1 + tt * 0.8, math.sin(a) * 0.3])

        def fn(d, x, y, s, col, tt=tt):
            r = (0.12 + tt * 0.3) * s
            d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 210, 190, int(200 * (1 - tt / 0.5))))

        sc.sprite(p, fn, layer=8, live=True)


def glow_at(sc, pos, r, color, a=80):
    sc.sprite(pos, lambda d, x, y, s, col: glow(d, x, y, r * s, color, a), layer=8, live=True)
