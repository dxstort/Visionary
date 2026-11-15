"""Reusable sets and props: town street, park, nursery, pigeons, bench, cookie."""
import math

import numpy as np

from engine import RX, RY, RZ, T

GRASS = (112, 205, 92)
HOUSE_COLORS = [(255, 120, 110), (255, 205, 90), (110, 200, 240), (190, 140, 255), (255, 160, 200), (130, 220, 170)]


def clouds(sc, seed=2, n=7, z=-60, drift=0.0):
    rng = np.random.RandomState(seed)
    for _ in range(n):
        x, y, w = rng.uniform(-45, 45) + drift, rng.uniform(16, 34), rng.uniform(5, 10)
        sc.box(T(x, y, z), (w, 1.8, 2), (255, 255, 255), layer=0, outline=False, lit=False)
        sc.box(T(x + w * 0.15, y + 1.3, z), (w * 0.5, 1.6, 2), (255, 255, 255), layer=0, outline=False, lit=False)


def house(sc, x, z, w=5.0, h=4.0, d=4.0, color=(255, 120, 110), roof=(120, 70, 70), yaw=0):
    def decal(D):
        D.rect(-0.18, -1, 0.18, -0.25, (120, 75, 50))
        D.ell(0.1, -0.62, 0.035, 0.035 * w / h, (255, 220, 90), n=8)
        for s in (-1, 1):
            D.rect(s * 0.62 - 0.2, -0.05, s * 0.62 + 0.2, 0.5, (255, 255, 255))
            D.rect(s * 0.62 - 0.16, 0.0, s * 0.62 + 0.16, 0.45, (150, 220, 255))
            D.line([(s * 0.62, 0.0), (s * 0.62, 0.45)], (255, 255, 255), 0.03)

    M = T(x, 0, z) @ RY(yaw)
    sc.box(M @ T(0, h / 2, 0), (w, h, d), color, layer=2, decal=decal)
    sc.box(M @ T(0, h + 0.3, 0), (w + 0.7, 0.6, d + 0.7), roof, layer=2, bias=-0.5)
    sc.box(M @ T(0, h + 0.9, 0), (w * 0.62, 0.6, d * 0.62), roof, layer=2, bias=-1.0)
    sc.box(M @ T(w * 0.28, h + 1.3, -d * 0.1), (0.6, 1.4, 0.6), (200, 90, 80), layer=2, bias=-1.2)


def tree(sc, x, z, h=4.0, layer=2, leaf=(70, 180, 90)):
    sc.box(T(x, h * 0.25, z), (0.5, h * 0.5, 0.5), (140, 95, 60), layer=layer)
    sc.box(T(x, h * 0.68, z), (2.2, h * 0.45, 2.2), leaf, layer=layer, bias=-0.3)
    sc.box(T(x + 0.1, h * 0.98, z), (1.4, h * 0.3, 1.4), tuple(min(255, v + 22) for v in leaf), layer=layer, bias=-0.6)


def town(sc, shift=0.0):
    """Street set: characters stand on the pavement around z=0, houses behind, road in front."""
    sc.ground(GRASS)
    q = lambda x0, x1, z0, z1, c: sc.quad([(x0, 0.01, z0), (x1, 0.01, z0), (x1, 0.01, z1), (x0, 0.01, z1)], c, layer=0)
    q(-80, 80, -2.2, 2.6, (226, 222, 214))
    q(-80, 80, 2.6, 11, (92, 96, 112))
    for i in range(-10, 11):
        q(i * 4 - 1 + shift, i * 4 + 1 + shift, 6.6, 7.0, (250, 240, 200))
    clouds(sc)
    for i, x in enumerate((-19.5, -13, -6.5, 0, 6.5, 13, 19.5)):
        c = HOUSE_COLORS[i % len(HOUSE_COLORS)]
        house(sc, x + shift, -7.5, w=5.0, h=3.6 + (i % 3) * 0.5, color=c, roof=tuple(int(v * 0.55) for v in c))
        tree(sc, x + 3.25 + shift, -5.2, h=3.4 + (i % 2) * 0.8)
        for k in range(6):
            sc.box(T(x - 2.4 + k * 0.6 + shift, 0.4, -3.4), (0.16, 0.8, 0.1), (255, 255, 255), layer=2)
        sc.box(T(x - 0.9 + shift, 0.5, -3.4), (3.3, 0.12, 0.08), (255, 255, 255), layer=2, bias=-0.1)


def park(sc):
    sc.ground(GRASS)
    sc.quad([(-60, 0.01, -1.6), (60, 0.01, -1.6), (60, 0.01, 2.2), (-60, 0.01, 2.2)], (240, 222, 170), layer=0)
    clouds(sc, seed=5)
    for x, z, h in ((-7.5, -6, 5), (-3.2, -9, 4.2), (4.6, -7, 5.2), (9, -10, 4.4), (-12, -11, 4.8), (14, -6, 4.6)):
        tree(sc, x, z, h)
    for x in (-5, 0.8, 6.5):
        sc.box(T(x, 0.35, -4.0), (1.6, 0.7, 1.0), (60, 165, 85), layer=2)
        for k, c in enumerate(((255, 120, 160), (255, 230, 90), (255, 255, 255))):
            sc.box(T(x - 0.5 + k * 0.5, 0.75, -3.8 + 0.2 * (k % 2)), (0.2, 0.14, 0.2), c, layer=2, bias=-0.3)
    sc.box(T(0, 1.2, -30), (120, 2.4, 1), (90, 190, 110), layer=1, outline=False)


def bench(sc, M, layer=5, live=False, w=3.0):
    wood, iron = (190, 125, 70), (70, 75, 90)
    sc.box(M @ T(0, 0.75, 0), (w, 0.14, 0.9), wood, layer=layer, live=live)
    sc.box(M @ T(0, 1.3, -0.42), (w, 0.7, 0.12), wood, layer=layer, live=live, bias=0.05)
    for sx in (-1, 1):
        sc.box(M @ T(sx * (w / 2 - 0.2), 0.35, 0), (0.14, 0.7, 0.8), iron, layer=layer, live=live, bias=0.1)


def pigeon(sc, pos, yaw=0, bob=0.0, layer=5, live=False, s=1.0, wing=0.0):
    grey, light = (150, 155, 175), (190, 195, 210)
    M = T(*pos) @ RY(yaw)
    for sx in (-1, 1):
        sc.box(M @ T(sx * 0.07 * s, 0.07 * s, 0), (0.04 * s, 0.14 * s, 0.04 * s), (255, 140, 60), layer=layer, live=live)
    sc.box(M @ T(0, 0.27 * s, 0) @ RX(-12), (0.3 * s, 0.26 * s, 0.46 * s), grey, layer=layer, live=live, bias=-0.02)
    sc.box(M @ T(0, 0.3 * s, -0.3 * s) @ RX(-25), (0.2 * s, 0.08 * s, 0.26 * s), (110, 115, 140), layer=layer, live=live)
    for sx in (-1, 1):
        sc.box(M @ T(sx * 0.17 * s, 0.3 * s, -0.02 * s) @ RZ(sx * wing), (0.05 * s, 0.2 * s, 0.36 * s), (120, 125, 150),
               layer=layer, live=live, bias=-0.03)
    H = M @ T(0, 0.5 * s, 0.2 * s + bob * 0.08 * s) @ RX(bob * 18)

    def eyes(D):
        for sx in (-1, 1):
            D.ell(sx * 0.5, 0.15, 0.2, 0.2, (255, 150, 40), n=10)
            D.ell(sx * 0.5, 0.15, 0.1, 0.1, (30, 25, 35), n=8)

    sc.box(H, (0.2 * s, 0.22 * s, 0.2 * s), light, layer=layer, live=live, decal=eyes, bias=-0.05)
    sc.box(H @ T(0, -0.03 * s, 0.14 * s), (0.07 * s, 0.06 * s, 0.1 * s), (255, 170, 60), layer=layer, live=live, bias=-0.1)
    sc.box(M @ T(0, 0.4 * s, 0.14 * s), (0.22 * s, 0.07 * s, 0.2 * s), (120, 200, 160), layer=layer, live=live, bias=-0.04)


def cookie(sc, M, s=1.0, layer=5, live=False, bitten=False):
    def chips(D):
        for u, v in ((-0.45, 0.4), (0.3, 0.5), (0.5, -0.2), (-0.2, -0.45), (0.0, 0.05), (-0.6, -0.1)):
            D.ell(u, v, 0.13, 0.13, (95, 55, 35), n=8)
        if bitten:
            D.ell(0.95, 0.9, 0.5, 0.5, (0, 0, 0, 0), n=10)

    sc.box(M, (0.42 * s, 0.42 * s, 0.09 * s), (225, 165, 90), layer=layer, live=live, decal=chips, bias=-0.4)


def crib(sc, M, layer=4, live=False, color=(255, 255, 255), blanket=(150, 215, 255)):
    """Crib ~1.9 wide, mattress top at y=1.0, rails to y=1.7."""
    B = lambda m, size, c, **kw: sc.box(M @ m, size, c, layer=layer, live=live, **kw)
    for sx in (-1, 1):
        for sz in (-1, 1):
            B(T(sx * 0.9, 0.85, sz * 0.55), (0.12, 1.7, 0.12), color)
    B(T(0, 0.85, 0), (1.8, 0.3, 1.1), blanket)
    B(T(0, 1.68, -0.55), (1.8, 0.1, 0.08), color)
    for k in range(7):
        B(T(-0.72 + k * 0.24, 1.3, -0.55), (0.06, 0.7, 0.06), color)
    return M


def crib_front(sc, M, layer=6, live=False, color=(255, 255, 255)):
    sc.box(M @ T(0, 1.68, 0.55), (1.8, 0.1, 0.08), color, layer=layer, live=live)
    for k in range(7):
        sc.box(M @ T(-0.72 + k * 0.24, 1.3, 0.55), (0.06, 0.7, 0.06), color, layer=layer, live=live)


def nursery(sc, wall=(170, 235, 215)):
    for i in range(-8, 9):
        for j in range(-3, 16):
            c = (250, 250, 250) if (i + j) % 2 else (205, 232, 245)
            sc.quad([(i * 1.5, 0, j * 1.5), (i * 1.5 + 1.5, 0, j * 1.5), (i * 1.5 + 1.5, 0, j * 1.5 + 1.5),
                     (i * 1.5, 0, j * 1.5 + 1.5)], c, layer=0)

    def deco(D):
        D.rect(-1, -1, 1, -0.78, (255, 255, 255))
        D.rect(-1, -0.2, 1, -0.08, (255, 200, 215))
        for u in (-0.55, 0.55):
            D.rect(u - 0.16, 0.05, u + 0.16, 0.75, (255, 255, 255))
            D.rect(u - 0.14, 0.09, u + 0.14, 0.71, (150, 215, 255))
            D.line([(u, 0.09), (u, 0.71)], (255, 255, 255), 0.012)
            D.line([(u - 0.14, 0.4), (u + 0.14, 0.4)], (255, 255, 255), 0.012)
        D.ell(0, 0.42, 0.07, 0.2, (255, 255, 255), n=20)
        D.line([(0, 0.42), (0, 0.56)], (60, 60, 80), 0.008)
        D.line([(0, 0.42), (0.035, 0.42)], (60, 60, 80), 0.008)

    sc.box(T(0, 4, -3.2), (26, 8, 0.4), wall, layer=1, decal=deco)
    sc.box(T(0, 20, -3.2), (26, 24, 0.4), wall, layer=1, outline=False)
