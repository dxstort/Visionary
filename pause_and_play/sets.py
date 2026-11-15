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


# ================================================================ act 2+ sets
WOOD = (196, 146, 96)
CHALK = (244, 244, 236)


def floor_tiles(sc, x0, x1, z0, z1, c1, c2, step=1.5, y=0.0):
    i0, i1 = int(math.floor(x0 / step)), int(math.ceil(x1 / step))
    j0, j1 = int(math.floor(z0 / step)), int(math.ceil(z1 / step))
    for i in range(i0, i1):
        for j in range(j0, j1):
            flat(sc, i * step, i * step + step, j * step, j * step + step, c1 if (i + j) % 2 else c2, y=y)


def wall(sc, x, y, z, w, h, color, decal=None, yaw=0, d=0.4):
    sc.box(T(x, y, z) @ RY(yaw), (w, h, d), color, layer=1, decal=decal)


def chair(sc, x, z, yaw=0, c=(70, 110, 190), h=0.8):
    M = T(x, 0, z) @ RY(yaw)
    sc.box(M @ T(0, h, 0), (0.9, 0.1, 0.8), c, layer=3)
    sc.box(M @ T(0, h + 0.45, -0.36), (0.9, 0.8, 0.08), c, layer=3)
    for sx in (-1, 1):
        for sz in (-1, 1):
            sc.box(M @ T(sx * 0.38, h / 2, sz * 0.32), (0.07, h, 0.07), (60, 60, 70), layer=3)


def desk(sc, x, z, yaw=0, top=WOOD, h=1.0, w=1.4, d=0.9):
    M = T(x, 0, z) @ RY(yaw)
    sc.box(M @ T(0, h, 0), (w, 0.09, d), top, layer=3)
    for sx in (-1, 1):
        for sz in (-1, 1):
            sc.box(M @ T(sx * (w / 2 - 0.08), h / 2, sz * (d / 2 - 0.08)), (0.07, h, 0.07), (70, 72, 84), layer=3)


# ------------------------------------------------------------- power show
def _banner(D):
    D.rect(-1, -1, 1, 1, (40, 34, 120))
    for k in range(14):
        u = -0.95 + k * 0.146
        D.poly(star_poly(u, 0.78 if k % 2 else -0.78, 0.06), (255, 214, 70))
    D.text(0, 0.05, "POWER SHOW", (255, 230, 90), h=0.4)


def star_poly(u, v, r):
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((u + rr * math.cos(a), v - rr * math.sin(a) * 2.2))
    return pts


def clock_face(hour=6, minute=56, second=0):
    def decal(D):
        D.ell(0, 0, 0.98, 0.98, (40, 34, 50), n=40)
        D.ell(0, 0, 0.88, 0.88, (252, 250, 240), n=40)
        for k in range(12):
            a = math.radians(90 - k * 30)
            D.line([(0.74 * math.cos(a), 0.74 * math.sin(a)), (0.84 * math.cos(a), 0.84 * math.sin(a))],
                   (40, 34, 50), 0.06 if k % 3 == 0 else 0.03)
        ah = math.radians(90 - (hour % 12 + minute / 60) * 30)
        am = math.radians(90 - minute * 6)
        asec = math.radians(90 - second * 6)
        D.line([(0, 0), (0.45 * math.cos(ah), 0.45 * math.sin(ah))], (40, 34, 50), 0.09)
        D.line([(0, 0), (0.7 * math.cos(am), 0.7 * math.sin(am))], (40, 34, 50), 0.06)
        D.line([(-0.12 * math.cos(asec), -0.12 * math.sin(asec)), (0.78 * math.cos(asec), 0.78 * math.sin(asec))],
               (220, 50, 50), 0.025)
        D.ell(0, 0, 0.06, 0.06, (220, 50, 50), n=12)

    return decal


STAGE_TOP = 0.9
STAGE_Z = -6.0


def stage(sc, lights=True):
    """Outdoor Power Show stage in the town plaza. Stage floor top at y=0.9, centred at z=-6, faces +z."""
    sc.ground((214, 204, 186))
    for i in range(-12, 13):
        flat(sc, i * 2.0 - 0.04, i * 2.0 + 0.04, -40, 30, (196, 186, 168), y=0.01)
    for j in range(-20, 15):
        flat(sc, -40, 40, j * 2.0 - 0.04, j * 2.0 + 0.04, (196, 186, 168), y=0.01)
    clouds(sc, seed=8)
    for i, x in enumerate((-22, -15, 15, 22)):
        c = HOUSE_COLORS[(i + 2) % len(HOUSE_COLORS)]
        house(sc, x, -16, w=6, h=4.2, color=c, roof=tuple(int(v * 0.5 + 20) for v in c))
    for x, z in ((-11, -12), (11, -12), (-14, -4), (14, -4), (-17, 4), (17, 4)):
        tree(sc, x, z, 5.0)
    sc.box(T(0, STAGE_TOP / 2, STAGE_Z), (13, STAGE_TOP, 5.2), WOOD, layer=2,
           decal=lambda D: [D.line([(-1, v), (1, v)], (170, 122, 78), 0.004) for v in (-0.5, 0.0, 0.5)])
    sc.box(T(0, STAGE_TOP + 0.02, STAGE_Z + 2.55), (13.1, 0.06, 0.12), (170, 120, 72), layer=2)
    for k in range(3):
        sc.box(T(0, 0.15 + k * 0.3, STAGE_Z + 2.9 + (2 - k) * 0.35), (3.0, 0.3, 0.35), (186, 136, 88), layer=2)
    sc.box(T(0, 3.6, STAGE_Z - 2.4), (13, 5.4, 0.4), (60, 40, 110), layer=1)
    sc.box(T(0, 5.4, STAGE_Z - 2.1), (9.0, 1.5, 0.12), (40, 34, 120), layer=1, decal=_banner)
    for sx in (-1, 1):
        sc.box(T(sx * 6.7, 3.9, STAGE_Z - 1.6), (0.9, 6.0, 1.2), (200, 40, 56), layer=2,
               decal=lambda D: [D.line([(u, -1), (u, 1)], (160, 26, 40), 0.06) for u in (-0.5, 0.0, 0.5)])
        sc.box(T(sx * 6.7, 3.2, STAGE_Z + 2.2), (0.3, 6.4, 0.3), (64, 64, 76), layer=2)
    sc.box(T(0, 6.5, STAGE_Z + 2.2), (13.7, 0.35, 0.35), (64, 64, 76), layer=2)
    sc.box(T(0, 7.25, STAGE_Z - 2.05), (1.5, 1.5, 0.22), (40, 34, 50), layer=2, decal=clock_face())
    if lights:
        cols = [(255, 90, 90), (255, 214, 70), (110, 220, 140), (110, 170, 255), (220, 120, 255)]
        for k in range(21):
            x = -6.5 + k * 0.65
            y = 6.25 - 0.35 * math.sin(math.pi * k / 20)
            sc.blob(T(x, y, STAGE_Z + 2.2), (0.16, 0.2, 0.16), cols[k % 5], layer=2, lit=False, n=8, m=5)


def audience(sc, t=0.0, frozen=False, faces=None, popcorn=False, rows=4, per_row=6, standing=False, seed=1):
    """Seated (or standing) crowd facing the stage (-z). Returns list of (spec, pos)."""
    from cast import character, crowd_spec, sit
    rng = np.random.RandomState(seed)
    out = []
    for r in range(rows):
        for c in range(per_row):
            i = r * per_row + c
            x = -5.0 + c * (10.0 / max(1, per_row - 1)) + (0.45 if r % 2 else 0)
            z = 1.0 + r * 1.9
            spec = crowd_spec(i + seed * 3, adult=(i % 4 == 1))
            face = (faces[i % len(faces)] if faces else "smile")
            if standing:
                cheer = 0.5 + 0.5 * math.sin(t * 9 + i)
                pose = dict(al=(150 + 25 * cheer, 12), ar=(150 + 25 * cheer, 12), y=0.06 * cheer)
                p = character(sc, spec, (x, 0, z), yaw=180 + rng.uniform(-12, 12), face=face, pose=pose)
            else:
                chair(sc, x, z, yaw=180, c=(84, 70, 150))
                ll = spec["leg"][1] * spec["s"]
                pose = sit()
                pose["head"] = (rng.uniform(-15, 15), 0, 0)
                if popcorn and i % 3 == 0:
                    pose["ar"] = (55, 4)
                p = character(sc, spec, (x, 0.86 - ll, z + 0.05), yaw=180, face=face, pose=pose, shadow=False)
                if popcorn and i % 3 == 0:
                    h = p["hand_r"]
                    sc.box(T(h[0], h[1] + 0.12, h[2]), (0.32, 0.4, 0.32), (230, 50, 50), layer=6,
                           decal=lambda D: [D.rect(u - 0.12, -1, u + 0.12, 1, (250, 250, 250)) for u in (-0.6, 0, 0.6)])
                    for k in range(4):
                        py = h[1] + 0.55 + k * 0.28 + (0 if frozen else ((t * 2 + k * 0.3) % 1.0))
                        sc.blob(T(h[0] + rng.uniform(-0.25, 0.25), py, h[2] + rng.uniform(-0.2, 0.2)),
                                (0.12, 0.11, 0.12), (255, 244, 200), layer=6, n=8, m=5)
            out.append((spec, p))
    return out


def stage_crowd(sc, n=40, face="neutral", seed=5, t=0.0, confused=False, clear=None):
    """People packed onto the stage, facing the audience (+z). clear=(x, z, r) leaves a gap (e.g. for Pip)."""
    from cast import character, crowd_spec
    from engine import add_emote
    rng = np.random.RandomState(seed)
    out = []
    cols = 8
    for i in range(n):
        r, c = divmod(i, cols)
        x = -5.2 + c * 1.48 + (0.6 if r % 2 else 0) + rng.uniform(-0.2, 0.2)
        z = STAGE_Z + 1.9 - r * 0.95
        spec = crowd_spec(i + 11, adult=(i % 5 == 2))
        a = rng.uniform(-30, 40)
        if clear and (x - clear[0]) ** 2 + (z - clear[1]) ** 2 < clear[2] ** 2:
            rng.uniform(-20, 60), rng.uniform(-30, 30), rng.uniform(-8, 8), rng.uniform(-25, 25)
            continue
        pose = dict(al=(a, 8), ar=(rng.uniform(-20, 60), 8), head=(rng.uniform(-30, 30), rng.uniform(-8, 8), 0))
        p = character(sc, spec, (x, STAGE_TOP, z), yaw=rng.uniform(-25, 25),
                      face=("shock" if confused and i % 3 == 0 else face), pose=pose, shadow=False)
        if confused and i % 4 == 1 and i < 24:
            add_emote(sc, "?", p["head_top"], t, size=0.5, dy=0.35, start=0.05 * (i % 6), hold=2.0)
        out.append((spec, p))
    return out


# ----------------------------------------------------------------- school
def classroom(sc):
    floor_tiles(sc, -10, 10, -6, 10, (206, 162, 112), (196, 152, 104), step=1.0)

    def back(D):
        D.rect(-1, -1, 1, -0.7, (120, 160, 200))
        for u in (-0.62, 0.0, 0.62):
            D.rect(u - 0.2, -0.2, u + 0.2, 0.6, (252, 252, 250))
            D.rect(u - 0.17, -0.16, u + 0.17, 0.56, (150, 208, 250))
            D.line([(u, -0.16), (u, 0.56)], (252, 252, 250), 0.01)
        for k, c in enumerate(((255, 140, 140), (255, 214, 110), (140, 210, 160), (160, 170, 255))):
            u = -0.85 + k * 0.08
            D.rect(u, 0.66, u + 0.06, 0.86, c)
        D.text(0.62, 0.78, "ABC", (60, 60, 90), h=0.06)

    wall(sc, 0, 3.5, -6.2, 22, 7, (238, 226, 196), decal=back)
    for sx in (-1, 1):
        wall(sc, sx * 9.5, 3.5, 0, 16, 7, (232, 218, 186), yaw=90)


def class_desks(sc, t=0.0, frozen=True, skip=(), seed=2, faces=("neutral",)):
    """Grid of desks with seated classmates facing +z (camera side). Returns positions."""
    from cast import character, crowd_spec, sit
    rng = np.random.RandomState(seed)
    out = {}
    for r in range(3):
        for c in range(4):
            x, z = -4.2 + c * 2.8, -3.6 + r * 2.4
            desk(sc, x, z + 0.75)
            chair(sc, x, z, yaw=0, c=(214, 96, 70))
            if (r, c) in skip:
                out[(r, c)] = (x, z)
                continue
            spec = crowd_spec(r * 4 + c + 20)
            ll = spec["leg"][1] * spec["s"]
            pose = sit()
            pose["ar"] = (70, 6)
            pose["head"] = (rng.uniform(-20, 20), -10, 0)
            character(sc, spec, (x, 0.86 - ll, z + 0.05), face=faces[(r + c) % len(faces)], pose=pose,
                      shadow=False)
            out[(r, c)] = (x, z)
            sc.box(T(x + 0.2, 1.06, z + 0.75), (0.7, 0.02, 0.5), (252, 252, 248), layer=4)
    return out


def hallway(sc):
    floor_tiles(sc, -3, 3, -30, 10, (226, 226, 232), (196, 204, 222), step=1.0)

    def locker(D):
        D.rect(-1, -1, 1, 1, (80, 140, 220))
        for k in range(-3, 4):
            u = k * 0.28
            D.line([(u, -1), (u, 1)], (50, 96, 170), 0.02)
            for v in (0.62, 0.68, 0.74):
                D.line([(u - 0.08, v), (u + 0.08, v)], (50, 96, 170), 0.012)
            D.rect(u + 0.06, 0.0, u + 0.09, 0.14, (220, 220, 230))

    for sx in (-1, 1):
        for k in range(8):
            sc.box(T(sx * 3.2, 1.6, -k * 4.0) @ RY(-sx * 90), (4.0, 3.2, 0.8), (80, 140, 220), layer=2, decal=locker)
        wall(sc, sx * 3.5, 4.5, -12, 40, 3, (236, 230, 214), yaw=90)
    wall(sc, 0, 3, -31, 8, 6, (236, 230, 214))
    for k in range(6):
        sc.blob(T(0, 6.2, -k * 5.0), (1.6, 0.12, 0.6), (255, 252, 230), layer=2, lit=False, e=0.3)
    sc.box(T(0, 6.4, -12), (8, 0.2, 40), (240, 240, 236), layer=1)


def school_building(sc):
    sc.ground(GRASS)
    flat(sc, -30, 30, 3.0, 8.0, (214, 208, 198))
    clouds(sc, seed=4)

    def front(D):
        D.rect(-1, -1, 1, 1, (196, 86, 70))
        for k in range(-12, 13):
            D.line([(-1, k / 12), (1, k / 12)], (176, 74, 60), 0.004)
        for row in (-0.25, 0.45):
            for u in (-0.75, -0.45, -0.15, 0.15, 0.45, 0.75):
                D.rect(u - 0.1, row - 0.17, u + 0.1, row + 0.17, (252, 250, 240))
                D.rect(u - 0.085, row - 0.15, u + 0.085, row + 0.15, (150, 208, 250))
        D.rect(-0.12, -1, 0.12, -0.55, (252, 250, 240))
        D.rect(-0.1, -1, 0.1, -0.58, (120, 80, 56))
        D.rect(-0.3, 0.8, 0.3, 0.95, (250, 250, 240))
        D.text(0, 0.875, "SCHOOL", (60, 50, 70), h=0.055)

    sc.box(T(0, 4.0, -2.0), (16, 8.0, 8.0), (196, 86, 70), layer=2, decal=front)
    sc.box(T(0, 8.15, 1.9), (16.4, 0.5, 0.3), (220, 210, 196), layer=2)
    sc.box(T(0, 8.15, -5.9), (16.4, 0.5, 0.3), (220, 210, 196), layer=2)
    for x in (-9.5, 9.5):
        tree(sc, x, 3.0, 5.0)


def lunch_tray(sc, M, live=False):
    sc.box(M, (1.0, 0.08, 0.7), (230, 120, 60), live=live, layer=6)
    sc.blob(M @ T(-0.22, 0.1, 0), (0.36, 0.14, 0.36), (255, 214, 100), live=live, layer=6, n=10, m=5)
    sc.box(M @ T(0.22, 0.12, -0.08), (0.34, 0.16, 0.22), (180, 90, 60), live=live, layer=6)
    sc.blob(M @ T(0.25, 0.1, 0.2), (0.16, 0.16, 0.16), (230, 50, 60), live=live, layer=6, n=8, m=5)


# ------------------------------------------------------------------- home
def kitchen(sc):
    floor_tiles(sc, -8, 8, -6, 10, (236, 232, 222), (214, 226, 230), step=1.0)

    def back(D):
        D.rect(-1, -1, 1, -0.2, (250, 250, 246))
        for k in range(-10, 11):
            D.line([(k / 10, -1), (k / 10, -0.2)], (226, 226, 222), 0.004)
        D.rect(-0.3, 0.05, 0.3, 0.6, (252, 252, 250))
        D.rect(-0.27, 0.08, 0.27, 0.57, (150, 208, 250))

    wall(sc, 0, 3.5, -4.0, 16, 7, (255, 220, 150), decal=back)
    desk(sc, 0, 0, top=(232, 232, 236), h=1.2, w=3.2, d=2.0)


def plate(sc, M, crumbs=True, cookie=False, live=False):
    sc.blob(M, (0.9, 0.08, 0.9), (250, 250, 252), e=0.5, e2=1.0, layer=6, live=live, n=20, m=5)
    if cookie:
        cookie_obj(sc, M @ T(0, 0.08, 0) @ RX(-90), live=live)
    if crumbs:
        rng = np.random.RandomState(3)
        for _ in range(9):
            sc.box(M @ T(rng.uniform(-0.25, 0.25), 0.06, rng.uniform(-0.25, 0.25)) @ RY(rng.uniform(0, 90)),
                   (0.05, 0.04, 0.05), (200, 140, 80), layer=6, live=live)


def cookie_obj(sc, M, s=1.0, live=False):
    cookie(sc, M, s=s, live=live)


def bedroom(sc):
    floor_tiles(sc, -8, 8, -6, 10, (180, 140, 110), (170, 132, 104), step=1.0)

    def back(D):
        D.rect(-1, -1, 1, 1, (176, 206, 250))
        for k in range(-20, 21):
            D.line([(k / 20, -1), (k / 20, 1)], (166, 196, 240), 0.004)
        D.rect(0.3, 0.0, 0.8, 0.6, (252, 252, 250))
        D.rect(0.33, 0.03, 0.77, 0.57, (30, 40, 90))
        D.ell(0.6, 0.4, 0.05, 0.08, (250, 245, 200), n=12)
        for u, v in ((0.42, 0.45), (0.5, 0.2), (0.7, 0.15)):
            D.ell(u, v, 0.01, 0.015, (255, 255, 255), n=6)
        D.rect(-0.8, 0.1, -0.45, 0.6, (255, 230, 120))
        D.text(-0.625, 0.35, "★", (230, 120, 60), h=0.1)

    wall(sc, 0, 3.5, -3.0, 16, 7, (176, 206, 250), decal=back)


def bed(sc, x, z, blanket=(110, 170, 240)):
    sc.box(T(x, 0.35, z), (2.4, 0.7, 4.0), (150, 104, 70), layer=3)
    sc.box(T(x, 0.8, z), (2.3, 0.3, 3.9), (250, 250, 250), layer=3)
    sc.box(T(x, 1.0, z + 0.5), (2.35, 0.2, 2.9), blanket, layer=3)
    sc.blob(T(x, 1.1, z - 1.45), (1.6, 0.3, 0.7), (255, 255, 255), e=0.5, layer=3)
    sc.box(T(x, 1.1, z - 2.0), (2.4, 2.2, 0.2), (150, 104, 70), layer=3)


# ------------------------------------------------------------------ props
def bus(sc, M):
    yel = (255, 196, 40)

    def side(D):
        D.rect(-1, -1, 1, 1, yel)
        D.rect(-1, -0.35, 1, -0.25, (30, 30, 36))
        for k in range(6):
            u = -0.8 + k * 0.3
            D.rect(u - 0.11, 0.05, u + 0.11, 0.7, (40, 44, 60))
            D.rect(u - 0.09, 0.08, u + 0.09, 0.66, (160, 214, 250))
        D.text(0, -0.65, "SCHOOL BUS", (30, 30, 36), h=0.14)

    sc.box(M, (2.4, 2.4, 8.0) if False else (8.0, 2.4, 2.4), yel, layer=6, decal=side)
    sc.box(M @ T(4.05, -0.4, 0), (0.2, 1.2, 2.2), (220, 220, 230), layer=6)
    for sx in (-1, 1):
        for sz in (-1, 1):
            sc.blob(M @ T(sx * 2.6, -1.3, sz * 1.1) @ RX(90), (0.9, 0.9, 0.4), (30, 30, 36), e=1.0, layer=6,
                    n=14, m=6)


def trophy(sc, M, s=1.0):
    gold = (250, 200, 60)
    sc.box(M @ T(0, 0.25 * s, 0), (1.2 * s, 0.5 * s, 1.2 * s), (90, 60, 40), layer=5)
    sc.blob(M @ T(0, 0.8 * s, 0), (0.4 * s, 0.6 * s, 0.4 * s), gold, e=0.8, layer=5)
    sc.blob(M @ T(0, 1.9 * s, 0), (1.6 * s, 1.7 * s, 1.6 * s), gold, e=0.9, layer=5)
    for sx in (-1, 1):
        sc.blob(M @ T(sx * 0.95 * s, 2.1 * s, 0) @ RZ(sx * 20), (0.3 * s, 0.9 * s, 0.25 * s), gold, layer=5)
    sc.box(M @ T(0, 0.25 * s, 0.61 * s), (0.7 * s, 0.25 * s, 0.02 * s), (250, 220, 120), layer=5,
           decal=lambda D: D.text(0, 0, "1ST", (60, 40, 20), h=0.6))


def chalkboard(sc, drawing):
    sc.ground((120, 96, 76))
    wall(sc, 0, 3, -1.0, 20, 8, (226, 214, 190))
    sc.box(T(0, 2.4, -0.7), (6.4, 3.6, 0.2), (150, 104, 70), layer=2)
    sc.box(T(0, 2.4, -0.58), (6.0, 3.2, 0.1), (52, 92, 70), layer=3, decal=drawing)
    sc.box(T(0, 0.55, -0.45), (6.2, 0.12, 0.35), (150, 104, 70), layer=3)
    for k, c in enumerate(((250, 250, 250), (255, 220, 120), (255, 150, 170))):
        sc.box(T(-2.2 + k * 0.4, 0.66, -0.4), (0.25, 0.07, 0.07), c, layer=4)
