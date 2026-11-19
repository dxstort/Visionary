"""Robots, sets and props for The Toaster Robot: Crumbs (toaster head, vacuum body, mop arms), Turbo (red car
robot), the fridge robot, the lawnmower robot; Zara's garage, the library, the race track with its bridge and
storm drain, the Golden Wrench and Kip's medal."""
import math

import numpy as np

import laughs_sets as ls
import porch_sets as ps
import sets
from engine import RX, RY, RZ, T, font, glow, xf

CHROME = (200, 206, 216)
GOLD = (250, 200, 60)
TRACK_Z0, TRACK_Z1 = 0.0, 6.0          # race track runs along x between these z
START_X, FINISH_X = -22.0, 26.0
BRIDGE_X0, BRIDGE_X1 = 0.0, 8.0
DRAIN = np.array([4.0, 0.0, 5.4])     # storm drain grate on the bridge, by the far railing
STAND_Z = -7.0                        # grandstand front row (crowd faces +z)


def _eye_face(D, col=(90, 230, 255), mood="happy", grille=True):
    D.rect(-1, -1, 1, 1, (40, 44, 54))
    for sx in (-1, 1):
        if mood == "blink":
            D.rect(sx * 0.45 - 0.22, -0.05, sx * 0.45 + 0.22, 0.05, col)
        else:
            D.ell(sx * 0.45, 0.15, 0.22, 0.28, col, n=16)
            D.ell(sx * 0.45 + 0.07, 0.25, 0.07, 0.09, (255, 255, 255), n=8)
    if grille:
        if mood == "happy":
            D.arc(0, -0.45, 0.35, 0.18, 200, 340, col, 0.08)
        else:
            for k in range(-2, 3):
                D.rect(k * 0.14 - 0.04, -0.6, k * 0.14 + 0.04, -0.4, (120, 126, 140))


def crumbs(sc, M, t=0.0, eyes=1.0, mood="happy", hose_to=None, toast=None, arms=(20, 20), shake=0.0, live=True):
    """Crumbs, facing +z of M. hose_to: world point the vacuum hose reaches toward. toast: 0..1 pop height.
    Returns anchors: head, slot, hand_l, hand_r, hose_end."""
    if shake:
        M = M @ T(0.03 * math.sin(t * 60) * shake, 0, 0.02 * math.cos(t * 53) * shake)
    red, dark = (214, 60, 60), (60, 60, 70)
    sc.box(M @ T(0, 0.18, 0), (1.0, 0.26, 1.2), red, layer=5, live=live)
    for sx in (-1, 1):
        for sz in (-1, 1):
            sc.blob(M @ T(sx * 0.48, 0.1, sz * 0.42) @ RZ(90), (0.2, 0.08, 0.2), dark, e=0.5, e2=1.0, layer=5, n=12,
                    m=4, live=live)
    sc.box(M @ T(0, 0.95, -0.15), (0.72, 1.3, 0.6), (236, 236, 240), layer=5, live=live)
    sc.blob(M @ T(0, 1.0, 0.18), (0.48, 0.8, 0.2), (150, 200, 240), e=0.5, layer=5, live=live)
    sc.box(M @ T(0, 1.65, -0.15), (0.78, 0.12, 0.66), red, layer=5, live=live)
    # toaster head
    H = M @ T(0, 2.05, -0.1)
    lit = tuple(int(40 + (c - 40) * eyes) for c in (90, 230, 255))

    def face(D):
        _eye_face(D, lit, mood if eyes > 0.2 else "blink")

    sc.box(H, (0.95, 0.65, 0.6), CHROME, layer=5, decal=face, live=live)
    for sx in (-1, 1):
        sc.box(H @ T(sx * 0.2, 0.33, 0), (0.14, 0.03, 0.42), (30, 30, 36), layer=5, live=live)
        if eyes > 0.2:
            sc.box(H @ T(sx * 0.2, 0.34, 0), (0.1, 0.02, 0.38), (255, 150 + int(70 * eyes), 70), layer=5, lit=False,
                   live=live)
    sc.box(H @ T(0.52, 0.0, 0.0), (0.08, 0.08, 0.2), (40, 40, 46), layer=5, live=live)
    if eyes > 0.3:
        sc.light(xf(H, (0, 0, 0.8)), (120, 220, 255), 12 * eyes, 0.2)
    slot = xf(H, (0.2, 0.35, 0))
    if toast is not None and toast > 0:
        ty = 0.25 + 1.6 * math.sin(min(1.0, toast) * math.pi) if toast < 1 else 0.25
        toast_slice(sc, H @ T(0.2, 0.3 + ty, 0) @ RY(90) @ RZ(20 * toast))
    # mop arms
    hands = {}
    for sx, key, ang in ((-1, "hand_l", arms[0]), (1, "hand_r", arms[1])):
        A = M @ T(sx * 0.42, 1.35, -0.1) @ RZ(sx * (90 - ang)) @ RX(-10)
        sc.box(A @ T(0, -0.6, 0), (0.07, 1.2, 0.07), (190, 150, 100), layer=5, live=live)
        for k in range(6):
            a = k * 60
            sc.box(A @ T(0.1 * math.cos(math.radians(a)), -1.3, 0.1 * math.sin(math.radians(a))) @ RY(a) @ RZ(8),
                   (0.08, 0.32, 0.08), (226, 226, 220), layer=5, live=live)
        hands[key] = xf(A, (0, -1.2, 0))
    # vacuum hose from the body's side
    p0 = xf(M, (0.36, 0.7, 0.1))
    end = np.asarray(hose_to if hose_to is not None else xf(M, (0.6, 0.25, 0.7)), float)
    n = 10
    for i in range(n):
        u = (i + 0.5) / n
        p = p0 + (end - p0) * u + np.array([0, 0.5 * math.sin(math.pi * u), 0])
        sc.blob(T(*p), (0.18, 0.18, 0.18), (70, 74, 86), layer=5, n=8, m=6, live=live)
    sc.blob(T(*end), (0.28, 0.2, 0.28), (40, 40, 46), layer=5, n=10, m=6, live=live)
    return dict(head=xf(H, (0, 0.4, 0)), slot=slot, hose_end=end, face=xf(H, (0, 0, 0.32)), **hands)


def toast_slice(sc, M):
    sc.box(M, (0.5, 0.55, 0.08), (226, 170, 96), layer=7)
    sc.box(M @ T(0, 0, 0.0), (0.42, 0.47, 0.09), (244, 214, 150), layer=7)


def turbo(sc, M, t=0.0, flames=0.0, face="grin"):
    """Turbo: a sleek red car with a robot face on the windshield, nose toward +x of M."""
    red, dk = (226, 40, 46), (40, 40, 48)
    sc.box(M @ T(0, 0.55, 0), (3.0, 0.55, 1.5), red, layer=5)
    sc.box(M @ T(0.25, 0.42, 0), (3.2, 0.25, 1.55), tuple(int(v * 0.85) for v in red), layer=5)

    def wind(D):
        D.rect(-1, -1, 1, 1, (60, 70, 90))
        for sx in (-1, 1):
            D.ell(sx * 0.42, 0.1, 0.2, 0.3, (255, 240, 120), n=14)
            D.ell(sx * 0.42 + 0.06, 0.2, 0.06, 0.08, (255, 255, 255), n=8)
        if face == "grin":
            D.arc(0, -0.45, 0.4, 0.2, 200, 340, (255, 240, 120), 0.09)
        else:
            D.line([(-0.3, -0.5), (0.3, -0.5)], (255, 240, 120), 0.08)

    sc.box(M @ T(-0.1, 1.05, 0) @ RZ(-18), (1.1, 0.55, 1.3), (60, 70, 90), layer=5)
    sc.box(M @ T(0.35, 1.0, 0) @ RZ(55), (0.6, 0.02, 1.25), (60, 70, 90), layer=5, decal=wind)
    sc.box(M @ T(-1.45, 1.05, 0), (0.25, 0.08, 1.6), dk, layer=5)
    for sz in (-1, 1):
        sc.box(M @ T(-1.4, 0.85, sz * 0.6), (0.08, 0.35, 0.08), dk, layer=5)
        for x in (-0.95, 1.0):
            sc.blob(M @ T(x, 0.32, sz * 0.78) @ RX(90), (0.62, 0.3, 0.62), dk, e=0.4, e2=1.0, layer=5, n=16, m=4)
    if flames > 0:
        for sz in (-0.4, 0.4):
            L = (1.0 + 0.4 * math.sin(t * 40 + sz)) * flames
            sc.blob(M @ T(-1.6 - L / 2, 0.5, sz) @ RZ(90), (0.35, L, 0.35), (255, 140, 40), layer=6, lit=False, n=10,
                    m=6)
            sc.blob(M @ T(-1.6 - L / 3, 0.5, sz) @ RZ(90), (0.18, L * 0.6, 0.18), (255, 240, 170), layer=6, lit=False,
                    n=8, m=5)


def fridge_bot(sc, M, t=0.0):
    ls.fridge(sc, M)

    def face(D):
        _eye_face(D, (120, 255, 160), "happy")
    sc.box(M @ T(0.1, 2.75, 0.72), (0.9, 0.6, 0.02), (40, 44, 54), layer=4, decal=face)
    for sx in (-1, 1):
        a = 30 * math.sin(t * 8 + sx)
        A = M @ T(sx * 0.88, 2.0, 0) @ RZ(sx * 30) @ RX(-60 - a)
        sc.box(A @ T(0, -0.45, 0), (0.18, 0.9, 0.18), (200, 204, 210), layer=4)
    return xf(M, (0, 2.0, 0.9))


def sandwich(sc, M):
    for i, c in enumerate(((236, 200, 140), (120, 200, 90), (230, 90, 80), (250, 220, 120), (236, 200, 140))):
        sc.box(M @ T(0, i * 0.06, 0), (0.5, 0.06, 0.5), c, layer=7)


def mower_bot(sc, M, t=0.0):
    green = (70, 170, 80)
    sc.box(M @ T(0, 0.35, 0), (1.2, 0.35, 1.5), green, layer=5)
    for sx in (-1, 1):
        for sz in (-1, 1):
            sc.blob(M @ T(sx * 0.62, 0.22, sz * 0.55) @ RZ(90), (0.36, 0.12, 0.36), (40, 40, 46), e=0.5, e2=1.0,
                    layer=5, n=12, m=4)
    sc.box(M @ T(0, 0.75, 0.1), (0.6, 0.5, 0.6), (60, 60, 70), layer=5)

    def face(D):
        _eye_face(D, (255, 220, 80), "happy")
    sc.box(M @ T(0, 0.78, 0.41), (0.56, 0.42, 0.02), (40, 44, 54), layer=5, decal=face)
    for sx in (-1, 1):
        sc.box(M @ T(sx * 0.45, 1.2, -0.65) @ RX(30), (0.06, 1.2, 0.06), (180, 184, 192), layer=5)
    sc.box(M @ T(0, 1.68, -0.95), (0.96, 0.06, 0.06), (40, 40, 46), layer=5)
    for sx in (-1, 1):  # clippers
        a = 20 * math.sin(t * 30)
        C = M @ T(sx * 0.7, 0.8, 0.5) @ RZ(sx * (40 + a))
        sc.box(C @ T(0, 0.35, 0), (0.08, 0.7, 0.08), (200, 204, 212), layer=5)
        sc.box(C @ T(0, 0.75, 0), (0.25, 0.15, 0.05), (220, 70, 60), layer=5)


def golden_wrench(sc, M, s=1.0, stand=True):
    if stand:
        sc.box(M @ T(0, 0.6, 0), (1.0, 1.2, 1.0), (60, 50, 90), layer=4)
        sc.box(M @ T(0, 1.22, 0), (1.1, 0.06, 1.1), GOLD, layer=4)
        base = 1.25
    else:
        base = 0.0
    W = M @ T(0, base + 1.0 * s, 0) @ RZ(20)
    sc.box(W, (0.25 * s, 1.9 * s, 0.12 * s), GOLD, layer=5)
    for sx in (-1, 1):
        sc.box(W @ T(sx * 0.22 * s, 1.1 * s, 0), (0.16 * s, 0.5 * s, 0.12 * s), GOLD, layer=5)
    sc.blob(W @ T(0, -1.0 * s, 0), (0.45 * s, 0.45 * s, 0.14 * s), GOLD, e=0.8, layer=5, n=14, m=6)
    return xf(W, (0, 0.6 * s, 0.1 * s))


def medal(sc, M, ribbon=True, s=1.0):
    if ribbon:
        for sx in (-1, 1):
            sc.box(M @ T(sx * 0.12 * s, 0.35 * s, 0) @ RZ(sx * 25), (0.12 * s, 0.6 * s, 0.02 * s),
                   (60, 90, 200) if sx < 0 else (220, 60, 60), layer=7)
    sc.blob(M, (0.32 * s, 0.32 * s, 0.06 * s), GOLD, e=0.8, e2=1.0, layer=7, n=16, m=6)
    sc.blob(M @ T(0, 0, 0.03 * s), (0.2 * s, 0.2 * s, 0.03 * s), (255, 230, 120), e=0.8, e2=1.0, layer=7, n=12, m=4)


def air_horn(sc, M):
    sc.blob(M @ T(0, 0.3, 0), (0.3, 0.6, 0.3), (230, 230, 236), e=0.3, e2=1.0, layer=6, n=14, m=6)
    v = [(0, 0, 0)] + [(0.08 * math.cos(a), 0.0, 0.08 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
    v += [(0.25 * math.cos(a), 0.5, 0.25 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
    f = [(1 + i, 1 + (i + 1) % 8, 9 + (i + 1) % 8, 9 + i) for i in range(8)]
    sc.solid(M @ T(0, 0.62, 0), v, f, (220, 50, 50), layer=6)


def remote(sc, M):
    sc.box(M, (0.18, 0.06, 0.6), (40, 40, 46), layer=7)
    for i in range(4):
        sc.box(M @ T(0, 0.035, -0.18 + i * 0.1), (0.1, 0.02, 0.05), ((220, 60, 60), (90, 200, 90), (90, 140, 240),
                                                                         (240, 240, 240))[i], layer=7)


def homework(sc, M):
    ps.note(sc, M @ RZ(8), ["Math HW", "2+2 = 4"], w=0.6, h=0.6, ink=(60, 60, 90))


def zara_garage(sc, day=True):
    ls.garage(sc, boots=False, books=False)
    rng = np.random.RandomState(6)
    for i in range(6):  # boxes
        sc.box(T(3.6 + rng.uniform(-0.6, 0.6), 0.35 + 0.7 * (i % 2), -2.2 + rng.uniform(-0.4, 0.4)) @ RY(rng.uniform(-20, 20)),
               (0.9, 0.7, 0.8), (190, 150, 100), layer=3)
    for x in (-4.2, -3.0):  # bike wheels + frame
        sc.blob(T(x, 0.55, -1.6) @ RX(90), (1.0, 0.1, 1.0), (40, 40, 46), e=0.3, e2=1.0, layer=3, n=20, m=4)
    sc.box(T(-3.6, 0.95, -1.6) @ RZ(15), (1.3, 0.1, 0.1), (60, 140, 220), layer=3)
    sc.box(T(1.2, 0.03, 1.4) @ RZ(80), (0.15, 1.4, 0.15), (220, 180, 90), layer=3)  # broken lamp
    sc.blob(T(1.9, 0.25, 1.5), (0.6, 0.45, 0.6), (250, 230, 160), e=0.6, layer=3)
    if day:
        sc.light((1.0, 3.5, 3.0), (255, 240, 220), 200, 1.5)


def library(sc):
    sets.floor_tiles(sc, -8, 8, -4, 8, (176, 140, 100), (168, 132, 94), step=1.0)
    sets.wall(sc, 0, 3.5, -3.6, 16, 7, (230, 214, 186))
    rng = np.random.RandomState(2)

    def books(D):
        D.rect(-1, -1, 1, 1, (120, 84, 60))
        for r in range(4):
            u = -1
            while u < 1:
                w = rng.uniform(0.04, 0.09)
                D.rect(u, -1 + r * 0.5 + 0.04, u + w, -1 + r * 0.5 + 0.42 - rng.uniform(0, 0.1),
                       [(200, 70, 60), (60, 120, 200), (240, 200, 80), (90, 170, 100), (160, 90, 180)][rng.randint(5)])
                u += w + 0.01

    for x in (-4.0, 0.0, 4.0):
        sc.box(T(x, 2.2, -3.1), (3.4, 4.4, 0.8), (120, 84, 60), layer=2, decal=books)
    sc.box(T(0, 1.0, 1.2), (4.0, 0.12, 1.6), (170, 120, 80), layer=3)
    for sx in (-1, 1):
        sc.box(T(sx * 1.8, 0.5, 1.2), (0.14, 1.0, 1.4), (140, 96, 64), layer=3)


def race_track(sc, t=0.0, crowd=True, crowd_at_bridge=False, banner=True):
    """Day race track along x; grandstand behind (z < 0); bridge over a creek; finish line and Golden Wrench."""
    sc.ground(sets.GRASS)
    sets.clouds(sc, seed=7)
    sets.sun(sc, x=0.85, y=0.08)
    sets.flat(sc, -60, 60, TRACK_Z0, TRACK_Z1, (90, 92, 104))
    for i in range(-30, 30):
        sets.flat(sc, i * 3.0, i * 3.0 + 1.6, 2.92, 3.08, (240, 240, 230), y=0.013)
    sets.flat(sc, -60, 60, TRACK_Z0 - 0.2, TRACK_Z0, (230, 230, 230), y=0.012)
    sets.flat(sc, -60, 60, TRACK_Z1, TRACK_Z1 + 0.2, (230, 230, 230), y=0.012)
    # creek under the bridge
    sets.flat(sc, BRIDGE_X0 + 1.0, BRIDGE_X1 - 1.0, -30, TRACK_Z0 - 0.2, (90, 160, 230), y=0.011)
    sets.flat(sc, BRIDGE_X0 + 1.0, BRIDGE_X1 - 1.0, TRACK_Z1 + 0.2, 40, (90, 160, 230), y=0.011)
    for z in (TRACK_Z0 - 0.1, TRACK_Z1 + 0.1):
        sc.box(T((BRIDGE_X0 + BRIDGE_X1) / 2, 0.55, z), (BRIDGE_X1 - BRIDGE_X0, 0.1, 0.12), (200, 120, 70), layer=3)
        for i in range(9):
            sc.box(T(BRIDGE_X0 + i, 0.3, z), (0.12, 0.6, 0.12), (180, 104, 60), layer=3)

    def grate(D):
        D.rect(-1, -1, 1, 1, (30, 30, 36))
        for k in range(-4, 5):
            D.rect(k / 4.6 - 0.04, -1, k / 4.6 + 0.04, 1, (110, 114, 124))
    sc.box(T(*DRAIN) @ T(0, 0.05, 0) @ RX(-90), (1.0, 0.7, 0.02), (30, 30, 36), layer=2, decal=grate)

    def checker(D):
        for i in range(8):
            for j in range(2):
                D.rect(-1 + i * 0.25, -1 + j, -1 + (i + 1) * 0.25, j, (255, 255, 255) if (i + j) % 2 else (30, 30, 30))
    for x in (START_X, FINISH_X):
        sc.box(T(x, 0.015, (TRACK_Z0 + TRACK_Z1) / 2) @ RY(90), (TRACK_Z1 - TRACK_Z0, 0.01, 0.5), (255, 255, 255),
               layer=2, decal=checker)
    if banner:
        def ban(D):
            D.rect(-1, -1, 1, 1, (40, 60, 160))
            ps.fit_text(D, ["ROBOT RALLY"], (255, 220, 70), aspect=7.0, fill_w=0.85, fill_h=0.7)
        for z in (TRACK_Z0 - 0.4, TRACK_Z1 + 0.4):
            sc.box(T(START_X, 2.2, z), (0.2, 4.4, 0.2), (240, 240, 240), layer=3)
        sc.box(T(START_X, 4.3, (TRACK_Z0 + TRACK_Z1) / 2) @ RY(90), (TRACK_Z1 - TRACK_Z0 + 1.0, 0.9, 0.08),
               (40, 60, 160), layer=3, decal=ban)
        for z in (TRACK_Z0 - 0.4, TRACK_Z1 + 0.4):
            sc.box(T(FINISH_X, 2.2, z), (0.2, 4.4, 0.2), (240, 240, 240), layer=3)
        sc.box(T(FINISH_X, 4.3, (TRACK_Z0 + TRACK_Z1) / 2) @ RY(90), (TRACK_Z1 - TRACK_Z0 + 1.0, 0.6, 0.08),
               (255, 255, 255), layer=3, decal=checker)
    # grandstand behind the finish
    for r in range(4):
        sc.box(T(FINISH_X - 2, 0.35 + r * 0.6, STAND_Z - r * 1.0), (16, 0.7 + r * 1.2 * 0, 1.0), (180, 180, 190), layer=2)
        sc.box(T(FINISH_X - 2, (0.7 + r * 0.6) / 2, STAND_Z - r * 1.0), (16, 0.7 + r * 0.6, 1.0), (150, 150, 160),
               layer=2)
    if crowd and not crowd_at_bridge:
        from cast import character, crowd_spec
        for r in range(2):
            for i in range(8):
                spec = crowd_spec(i + r * 8 + 3, adult=(i + r) % 3 != 0)
                ll = spec["leg"][1] * spec["s"]
                character(sc, spec, (FINISH_X - 9 + i * 2.0 + r, 0.7 + r * 0.6 - 0.05, STAND_Z - r * 1.0),
                          face=("grin", "joy", "smile")[(i + r) % 3],
                          pose=dict(al=(150 * ((i + int(t * 3)) % 2), -20), ar=(30, 10)))
    golden_wrench(sc, T(FINISH_X + 3.0, 0, -1.6))
