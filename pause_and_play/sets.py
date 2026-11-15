"""Reusable sets and props: town street, park, nursery, pigeons, bench, cookie."""
import math

import numpy as np

from engine import RX, RY, RZ, T

GRASS = (104, 196, 92)
GRASS2 = (96, 186, 86)
HOUSE_COLORS = [(244, 122, 110), (250, 204, 100), (112, 190, 232), (176, 138, 240), (250, 160, 196), (128, 212, 168)]


def flat(sc, x0, x1, z0, z1, c, y=0.01, layer=0):
    sc.quad([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], c, layer=layer)


def clouds(sc, seed=2, n=7, z=-70, drift=0.0):
    rng = np.random.RandomState(seed)
    for _ in range(n):
        x, y, w = rng.uniform(-50, 50) + drift, rng.uniform(14, 40), rng.uniform(7, 12)
        for dx, dy, k in ((0, 0, 1.0), (-0.3, -0.35, 0.7), (0.32, -0.3, 0.75), (0.1, 0.3, 0.6)):
            sc.blob(T(x + dx * w, y + dy * 2.2, z), (w * 0.6 * k, 3.4 * k, 3 * k), (255, 255, 255), layer=0, lit=False,
                    n=10, m=6)


def sun(sc, x=0.82, y=0.07):
    def fn(d, W, H):
        for i in range(10, 0, -1):
            r = W * 0.04 * i
            d.ellipse([x * W - r, y * H - r, x * W + r, y * H + r], fill=(255, 250, 215, 9))
        r = W * 0.055
        d.ellipse([x * W - r, y * H - r, x * W + r, y * H + r], fill=(255, 252, 232, 235))

    sc.items.append((0, 1e9, -1, lambda d: fn(d, sc.W, sc.H)))


def house(sc, x, z, w=5.0, h=3.6, d=4.2, color=(244, 122, 110), roof=(120, 70, 70), yaw=0):
    trim = (252, 250, 244)

    def decal(D):
        for i in range(1, 9):
            v = -1 + i * 2 / 9
            D.line([(-1, v), (1, v)], tuple(c * 0.93 for c in color), 0.012)
        D.rect(-0.2, -1, 0.2, -0.16, trim)
        D.rect(-0.16, -1, 0.16, -0.2, (132, 84, 58))
        D.rect(-0.1, -0.5, 0.1, -0.28, (170, 214, 240))
        D.ell(0.11, -0.62, 0.025, 0.025 * w / h, (255, 214, 90), n=8)
        for s in (-1, 1):
            D.rect(s * 0.62 - 0.21, -0.1, s * 0.62 + 0.21, 0.52, trim)
            D.rect(s * 0.62 - 0.17, -0.05, s * 0.62 + 0.17, 0.47, (160, 214, 244))
            D.poly([(s * 0.62 - 0.17, 0.47), (s * 0.62 + 0.02, 0.47), (s * 0.62 - 0.17, 0.12)], (200, 234, 252))
            D.line([(s * 0.62, -0.05), (s * 0.62, 0.47)], trim, 0.022)
            D.line([(s * 0.62 - 0.17, 0.21), (s * 0.62 + 0.17, 0.21)], trim, 0.022)
            D.rect(s * 0.62 - 0.24, -0.18, s * 0.62 + 0.24, -0.1, trim)
        D.rect(-1, -1, 1, -0.9, tuple(c * 0.7 for c in color))

    M = T(x, 0, z) @ RY(yaw)
    sc.box(M @ T(0, h / 2, 0), (w, h, d), color, layer=2, decal=decal)
    ov, rh = 0.45, 1.9
    verts = [(-w / 2 - ov, h, d / 2 + ov), (w / 2 + ov, h, d / 2 + ov), (w / 2 + ov, h, -d / 2 - ov),
             (-w / 2 - ov, h, -d / 2 - ov), (-w / 2 - ov, h + rh, 0), (w / 2 + ov, h + rh, 0)]
    sc.solid(M, verts, [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)], roof, layer=2, bias=-1.0)
    sc.box(M @ T(w * 0.28, h + 1.5, -d * 0.2), (0.6, 1.6, 0.6), (196, 96, 84), layer=2, bias=-1.6)
    sc.box(M @ T(w * 0.28, h + 2.34, -d * 0.2), (0.76, 0.14, 0.76), (150, 70, 62), layer=2, bias=-1.7)
    sc.box(M @ T(0, 0.09, d / 2 + 0.35), (1.3, 0.18, 0.7), (214, 210, 204), layer=2, bias=-0.6)


def tree(sc, x, z, h=4.0, layer=2, leaf=(78, 176, 92)):
    lite = tuple(min(255, v + 20) for v in leaf)
    sc.box(T(x, h * 0.26, z), (0.46, h * 0.52, 0.46), (132, 90, 60), layer=layer)
    sc.blob(T(x, h * 0.66, z), (2.5, h * 0.5, 2.5), leaf, layer=layer, bias=-0.3, n=10, m=7)
    sc.blob(T(x - 0.55, h * 0.84, z + 0.2), (1.6, h * 0.34, 1.6), lite, layer=layer, bias=-0.6, n=9, m=6)
    sc.blob(T(x + 0.6, h * 0.9, z - 0.1), (1.4, h * 0.3, 1.4), leaf, layer=layer, bias=-0.5, n=9, m=6)


def bush(sc, x, z, s=1.0, layer=2, c=(70, 164, 84)):
    sc.blob(T(x, 0.42 * s, z), (1.5 * s, 0.95 * s, 1.0 * s), c, layer=layer, n=10, m=6)
    sc.blob(T(x + 0.55 * s, 0.34 * s, z + 0.1), (0.9 * s, 0.7 * s, 0.8 * s), tuple(v + 14 for v in c), layer=layer,
            bias=-0.2, n=9, m=5)


def lamp(sc, x, z, layer=2):
    sc.box(T(x, 2.0, z), (0.14, 4.0, 0.14), (64, 68, 84), layer=layer)
    sc.box(T(x, 4.05, z), (0.5, 0.12, 0.5), (64, 68, 84), layer=layer, bias=-0.1)
    sc.blob(T(x, 4.35, z), (0.44, 0.5, 0.44), (255, 244, 190), layer=layer, bias=-0.2, lit=False, n=8, m=5)


def town(sc, shift=0.0):
    """Street set: characters stand on the pavement around z=0, houses behind, road in front."""
    sc.ground(GRASS)
    for i in range(-14, 14):
        if i % 2:
            flat(sc, i * 3 + shift, i * 3 + 3 + shift, -40, -2.3, GRASS2)
    flat(sc, -80, 80, -2.3, 2.6, (228, 222, 212))
    for i in range(-20, 21):
        flat(sc, i * 2.2 + shift - 0.03, i * 2.2 + shift + 0.03, -2.3, 2.6, (204, 198, 190), y=0.012)
    flat(sc, -80, 80, 2.6, 2.95, (196, 192, 186), y=0.014)
    flat(sc, -80, 80, 2.95, 12, (88, 92, 108))
    for i in range(-10, 11):
        flat(sc, i * 4 - 1 + shift, i * 4 + 1 + shift, 7.0, 7.3, (246, 236, 196), y=0.012)
    clouds(sc)
    sun(sc)
    for i, x in enumerate((-19.5, -13, -6.5, 0, 6.5, 13, 19.5)):
        c = HOUSE_COLORS[i % len(HOUSE_COLORS)]
        hx = x + shift
        house(sc, hx, -8.0, h=3.4 + (i % 3) * 0.45, color=c, roof=tuple(int(v * 0.5 + 20) for v in c))
        flat(sc, hx - 0.6, hx + 0.6, -5.6, -2.3, (214, 208, 198), y=0.012)
        tree(sc, hx + 3.25, -5.4, h=3.6 + (i % 2) * 0.9)
        bush(sc, hx - 1.8, -5.5, 0.9)
        bush(sc, hx + 1.7, -5.55, 0.75, c=(84, 172, 96))
        for k in range(8):
            px = hx - 2.9 + k * 0.42
            if abs(px - hx) < 0.75:
                continue
            sc.box(T(px, 0.42, -3.3), (0.2, 0.84, 0.08), (252, 252, 250), layer=2)
        for sx in (-1, 1):
            sc.box(T(hx + sx * 1.85, 0.5, -3.32), (2.3, 0.1, 0.06), (240, 240, 238), layer=2, bias=0.05)
        if i % 2 == 0:
            lamp(sc, hx - 3.2, -2.0)
        else:
            sc.box(T(hx - 3.0, 0.5, -2.2), (0.1, 1.0, 0.1), (120, 84, 60), layer=2)
            sc.box(T(hx - 3.0, 1.1, -2.2), (0.36, 0.3, 0.56), (220, 70, 70), layer=2, bias=-0.1)


def park(sc):
    sc.ground(GRASS)
    for i in range(-10, 10):
        if i % 2:
            flat(sc, -60, 60, i * 4.0 - 20, i * 4.0 - 16, GRASS2)
    flat(sc, -60, 60, -1.6, 2.3, (238, 220, 172))
    flat(sc, -60, 60, -1.75, -1.6, (214, 194, 150), y=0.012)
    flat(sc, -60, 60, 2.3, 2.45, (214, 194, 150), y=0.012)
    clouds(sc, seed=5)
    sun(sc, x=0.2, y=0.06)
    sc.box(T(0, 1.4, -34), (140, 2.8, 1), (92, 178, 106), layer=1)
    for x, z, h in ((-7.5, -6, 5), (-3.2, -9.5, 4.4), (4.6, -7, 5.4), (9, -11, 4.6), (-12, -12, 5), (14, -6, 4.8),
                    (0.5, -16, 5.5), (-18, -8, 4.6)):
        tree(sc, x, z, h)
    for x in (-5.4, 1.2, 6.8):
        bush(sc, x, -4.0, 1.1)
        for k, c in enumerate(((255, 120, 160), (255, 226, 96), (255, 255, 255), (255, 150, 90))):
            sc.blob(T(x - 0.6 + k * 0.42, 0.2 + 0.1 * (k % 2), -3.2 + 0.25 * (k % 2)), (0.22, 0.22, 0.22), c, layer=2,
                    bias=-0.3, n=6, m=4)
    lamp(sc, -3.4, -2.4)


def bench(sc, M, layer=5, live=False, w=3.0):
    wood, iron = (186, 122, 70), (62, 66, 82)
    for k in range(3):
        sc.box(M @ T(0, 0.78, -0.3 + k * 0.3), (w, 0.1, 0.26), wood if k != 1 else (198, 134, 80), layer=layer, live=live)
    for k in range(2):
        sc.box(M @ T(0, 1.14 + k * 0.34, -0.5) @ RX(-8), (w, 0.26, 0.1), wood, layer=layer, live=live, bias=0.05)
    for sx in (-1, 1):
        sc.box(M @ T(sx * (w / 2 - 0.22), 0.37, 0), (0.12, 0.74, 0.86), iron, layer=layer, live=live, bias=0.1)
        sc.box(M @ T(sx * (w / 2 - 0.22), 1.2, -0.52) @ RX(-8), (0.12, 0.9, 0.1), iron, layer=layer, live=live, bias=0.12)


def pigeon(sc, pos, yaw=0, bob=0.0, layer=5, live=False, s=1.0, wing=0.0, tint=0):
    grey = (146 + tint, 152 + tint, 174 + tint)
    light = (188 + tint, 194 + tint, 210 + tint)
    M = T(*pos) @ RY(yaw)
    for sx in (-1, 1):
        sc.box(M @ T(sx * 0.07 * s, 0.07 * s, 0), (0.04 * s, 0.14 * s, 0.04 * s), (250, 138, 64), layer=layer, live=live)
    sc.blob(M @ T(0, 0.28 * s, -0.02 * s) @ RX(-14), (0.34 * s, 0.32 * s, 0.52 * s), grey, layer=layer, live=live,
            bias=-0.02, n=9, m=6)
    sc.box(M @ T(0, 0.3 * s, -0.33 * s) @ RX(-25), (0.2 * s, 0.07 * s, 0.26 * s), (108, 114, 138), layer=layer, live=live)
    for sx in (-1, 1):
        sc.blob(M @ T(sx * 0.17 * s, 0.31 * s, -0.04 * s) @ RZ(sx * wing), (0.08 * s, 0.22 * s, 0.4 * s),
                (118, 124, 150), layer=layer, live=live, bias=-0.03, n=7, m=4)
    H = M @ T(0, 0.52 * s, 0.2 * s + bob * 0.08 * s) @ RX(bob * 18)

    def eyes(D):
        for sx in (-1, 1):
            D.ell(sx * 0.5, 0.15, 0.22, 0.22, (255, 150, 40), n=10)
            D.ell(sx * 0.5, 0.15, 0.11, 0.11, (30, 25, 35), n=8)

    sc.blob(M @ T(0, 0.42 * s, 0.14 * s), (0.2 * s, 0.14 * s, 0.2 * s), (112, 190, 156), layer=layer, live=live,
            bias=-0.04, n=8, m=4)
    sc.blob(H, (0.23 * s, 0.24 * s, 0.23 * s), light, e=0.6, layer=layer, live=live, decal=eyes, bias=-0.05, n=9, m=6)
    sc.box(H @ T(0, -0.03 * s, 0.15 * s), (0.07 * s, 0.06 * s, 0.1 * s), (250, 166, 64), layer=layer, live=live, bias=-0.1)


def cookie(sc, M, s=1.0, layer=5, live=False):
    def chips(D):
        D.ell(0, 0, 0.98, 0.98, (226, 168, 96), n=20)
        for u, v in ((-0.42, 0.38), (0.3, 0.48), (0.5, -0.2), (-0.2, -0.45), (0.02, 0.05), (-0.6, -0.08)):
            D.ell(u, v, 0.13, 0.13, (92, 54, 36), n=8)

    sc.blob(M, (0.44 * s, 0.44 * s, 0.1 * s), (206, 146, 80), e=0.9, layer=layer, live=live, decal=chips, bias=-0.4,
            n=12, m=4)


def crib(sc, M, layer=4, live=False, color=(252, 252, 250), blanket=(150, 212, 250), legs=True):
    """Crib ~1.9 wide, mattress top at y=1.0, rails to y=1.7. legs=False drops the legs (for carrying)."""
    B = lambda m, size, c, **kw: sc.box(M @ m, size, c, layer=layer, live=live, **kw)
    y0 = 0.0 if legs else 0.68
    for sx in (-1, 1):
        for sz in (-1, 1):
            B(T(sx * 0.9, (1.7 + y0) / 2, sz * 0.55), (0.12, 1.7 - y0, 0.12), color)
    B(T(0, 0.82, 0), (1.8, 0.26, 1.1), (236, 232, 226))
    B(T(0, 0.96, 0.05), (1.7, 0.1, 0.9), blanket, bias=-0.05)
    B(T(0, 1.68, -0.55), (1.8, 0.1, 0.08), color)
    for k in range(7):
        B(T(-0.72 + k * 0.24, 1.3, -0.55), (0.06, 0.7, 0.06), color)


def crib_front(sc, M, layer=6, live=False, color=(252, 252, 250)):
    sc.box(M @ T(0, 1.68, 0.55), (1.8, 0.1, 0.08), color, layer=layer, live=live)
    for k in range(7):
        sc.box(M @ T(-0.72 + k * 0.24, 1.3, 0.55), (0.06, 0.7, 0.06), color, layer=layer, live=live)


def nursery(sc, wall=(168, 228, 212)):
    for i in range(-8, 9):
        for j in range(-3, 16):
            c = (248, 246, 240) if (i + j) % 2 else (206, 230, 242)
            flat(sc, i * 1.5, i * 1.5 + 1.5, j * 1.5, j * 1.5 + 1.5, c, y=0)

    def deco(D):
        D.rect(-1, -1, 1, -0.5, (250, 246, 238))
        D.rect(-1, -0.5, 1, -0.44, (255, 196, 210))
        for k in range(-12, 13):
            D.line([(k / 12, -1), (k / 12, -0.5)], (232, 226, 216), 0.004)
        for u in (-0.42, 0.42):
            D.rect(u - 0.14, -0.1, u + 0.14, 0.72, (252, 252, 250))
            D.rect(u - 0.12, -0.05, u + 0.12, 0.67, (150, 208, 250))
            D.ell(u + 0.03, 0.4, 0.06, 0.08, (255, 255, 255), n=12)
            D.ell(u - 0.03, 0.36, 0.05, 0.07, (255, 255, 255), n=12)
            D.line([(u, -0.05), (u, 0.67)], (252, 252, 250), 0.01)
            D.line([(u - 0.12, 0.31), (u + 0.12, 0.31)], (252, 252, 250), 0.01)
            for s in (-1, 1):
                D.poly([(u + s * 0.12, 0.7), (u + s * 0.2, 0.7), (u + s * 0.19, -0.12), (u + s * 0.14, -0.12)],
                       (255, 214, 120))
        D.ell(0, 0.45, 0.07, 0.21, (60, 60, 80), n=20)
        D.ell(0, 0.45, 0.062, 0.186, (255, 255, 255), n=20)
        D.line([(0, 0.45), (0, 0.58)], (60, 60, 80), 0.008)
        D.line([(0, 0.45), (0.032, 0.45)], (60, 60, 80), 0.008)
        for k, c in enumerate(((255, 150, 150), (255, 220, 120), (150, 220, 170), (170, 190, 255))):
            D.poly([(-0.2 + k * 0.1, 0.93), (-0.12 + k * 0.1, 0.93), (-0.16 + k * 0.1, 0.8)], c)
        D.line([(-0.24, 0.94), (0.24, 0.94)], (120, 110, 120), 0.006)

    sc.box(T(0, 4, -3.2), (26, 8, 0.4), wall, layer=1, decal=deco)
    sc.box(T(0, 20, -3.2), (26, 24, 0.4), wall, layer=1)
    for x, cols in ((-5.2, ((255, 150, 150), (150, 200, 255))), (5.0, ((255, 220, 120), (150, 220, 170)))):
        sc.box(T(x, 0.5, -2.4), (1.6, 1.0, 0.8), (240, 200, 150), layer=2)
        for k, c in enumerate(cols):
            sc.box(T(x - 0.35 + k * 0.6, 1.22, -2.4) @ RY(20 * k), (0.42, 0.42, 0.42), c, layer=2, bias=-0.3)
