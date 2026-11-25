"""Sets and props for When You SNEEZE, You SWITCH Places: Dad's and Mr Gomez's back gardens (fence, tomato patch,
garden hose), a classroom with a pizza on the board, the new Hilltop Bridge (wobbling deck, podium, ribbon, big oak)
and the swap effect itself (glow, sparkles, a flash)."""
import math

import numpy as np

import laughs_sets as ls
import porch_sets as ps
import sets
from engine import RX, RY, RZ, T, clamp, lerp
from shots import sparks

HOSE_C = (70, 176, 92)
BR_Y = 0.5                       # bridge deck top
DECK_Z0, DECK_Z1 = -5.4, 3.4     # deck spans z (the creek runs along z, the deck along x)
BR_X = 8.0
PODIUM = np.array([0.0, BR_Y, -2.0])
MAYOR_SPOT = np.array([0.0, BR_Y, -2.8])
KID_SPOT = np.array([0.0, BR_Y, -4.0])
OAK = np.array([10.4, 0.0, 0.6])
FENCE_X = 0.0
WHITE = (250, 250, 246)


# ------------------------------------------------------------- swap effect
def swap_fx(sc, pa, pb, t, start, hold=0.75, y=1.2):
    """Sparkle bursts at both spots and a streak of stars between them, with a one-frame flash."""
    tt = t - start
    if tt < 0 or tt > hold:
        return
    k = tt / hold
    pa, pb = np.asarray(pa, float) + np.array([0, y, 0]), np.asarray(pb, float) + np.array([0, y, 0])
    for p in (pa, pb):
        ls.glow_at(sc, p, 1.5 * (1.0 - 0.4 * k), (150, 226, 255), int(150 * (1 - k)))
        sparks(sc, p, tt, seed=3, n=7, r=0.9, color=(255, 255, 255))
    for i in range(6):
        q = (i + 1) / 7.0
        lift = np.array([0, 0.5 * math.sin(math.pi * q), 0])
        sparks(sc, pa * (1 - q) + pb * q + lift, tt + i * 0.03, seed=7 + i, n=2, r=0.25, color=(190, 236, 255))
    if tt < 2 / 30:
        sc.flash = 0.55


# -------------------------------------------------------------- hose props
def hose(sc, pts, k=1.0, r=0.07, color=HOSE_C, step=1.7):
    """A garden hose as a chain of beads along a polyline, drawn up to the fraction k of its length."""
    pts = [np.asarray(p, float) for p in pts]
    seg = [np.linalg.norm(b - a) for a, b in zip(pts, pts[1:])]
    total = sum(seg) * clamp(k)
    d, last = 0.0, None
    for a, b, L in zip(pts, pts[1:], seg):
        n = max(1, int(L / (r * step)))
        for i in range(n):
            if d + L * i / n > total:
                return last
            p = a + (b - a) * (i / n)
            sc.blob(T(*p), (2 * r, 2 * r, 2 * r), color, layer=6, n=6, m=4)
            last = p
        d += L
    return last


def hose_coil(sc, c, turns=2, r=0.5, r0=0.07):
    pts = []
    for i in range(turns * 16 + 1):
        a = i / 16 * 2 * math.pi
        rr = r * (1 - 0.18 * i / (turns * 16))
        pts.append((c[0] + rr * math.cos(a), c[1] + r0 + 0.1 * (i / 16), c[2] + rr * math.sin(a) * 0.9))
    hose(sc, pts, r=r0, step=2.0)
    sc.box(T(c[0] + r, c[1] + 0.15, c[2]), (0.16, 0.16, 0.34), (230, 190, 50), layer=6)


def nozzle(sc, M):
    sc.box(M, (0.14, 0.14, 0.36), (230, 190, 50), layer=7)
    sc.box(M @ T(0, 0, 0.22), (0.1, 0.1, 0.12), (190, 150, 40), layer=7)


def tissue_box(sc, M, s=1.0):
    sc.box(M, (0.5 * s, 0.34 * s, 0.34 * s), (150, 210, 250), layer=7,
           decal=lambda D: D.ell(0, 0, 0.5, 0.5, (250, 250, 250), n=12))
    sc.blob(M @ T(0, 0.26 * s, 0), (0.3 * s, 0.26 * s, 0.2 * s), (252, 252, 252), layer=7, n=8, m=5)


def feather(sc, pos, t=0.0, s=1.0):
    """A big pink feather sticking out of the mayor's hat, waving a little."""
    p = np.asarray(pos, float)
    w = 0.08 * math.sin(t * 9)
    for i in range(7):
        q = i / 6
        c = (255, 120 + int(60 * q), 190 - int(30 * q))
        sc.blob(T(p[0] + (0.3 * q + w * q) * s, p[1] + (0.3 + 0.55 * q - 0.35 * q * q) * s, p[2]),
                ((0.22 - 0.12 * q) * s, 0.2 * s, 0.1 * s), c, layer=7, n=8, m=5, bias=-0.3)


def scissors(sc, M, open_k=0.5, s=1.0):
    gold = (246, 196, 50)
    for sx in (-1, 1):
        R = M @ RZ(sx * (6 + 26 * open_k))
        sc.box(R @ T(0, 0.55 * s, 0), (0.1 * s, 1.1 * s, 0.05 * s), (214, 216, 224), layer=7)
        sc.box(R @ T(sx * 0.0, -0.3 * s, 0), (0.1 * s, 0.6 * s, 0.07 * s), gold, layer=7)
        sc.blob(R @ T(sx * 0.12 * s, -0.7 * s, 0), (0.34 * s, 0.34 * s, 0.07 * s), gold, layer=7, n=10, m=5)


# ----------------------------------------------------------------- gardens
def tomato(sc, x, z, s=1.0, ripe=1.0):
    sc.box(T(x, 0.55 * s, z), (0.06 * s, 1.1 * s, 0.06 * s), (150, 108, 70), layer=3)
    sc.blob(T(x, 0.62 * s, z), (0.9 * s, 0.9 * s, 0.9 * s), (64, 150, 70), layer=3, n=10, m=6)
    sc.blob(T(x + 0.12 * s, 0.9 * s, z + 0.1 * s), (0.6 * s, 0.6 * s, 0.6 * s), (78, 168, 82), layer=3, n=8, m=5)
    for dx, dy, dz in ((0.3, 0.35, 0.25), (-0.28, 0.55, 0.3), (0.1, 0.8, 0.38), (-0.1, 0.25, 0.35)):
        sc.blob(T(x + dx * s, dy * s, z + dz * s), (0.3 * s, 0.3 * s, 0.3 * s), (224, 52, 44), layer=4, n=8, m=6,
                bias=-0.2)


TOMATO_SPOTS = [(2.6, -1.8), (3.8, -1.2), (5.0, -2.0), (2.8, 1.6), (4.2, 1.2), (5.4, 0.6), (6.4, -1.0), (6.6, 1.8),
                (4.6, -3.2), (3.2, -3.4)]


def garden(sc, t=0.0, tomatoes=True, fence_hose=0.0):
    """Two back gardens side by side: Dad's lawn (x<0), a picket fence, Mr Gomez's tomato patch (x>0)."""
    sc.ground(sets.GRASS)
    sets.clouds(sc, seed=4)
    sets.sun(sc)
    sets.flat(sc, -9, -0.3, -6, 5, (96, 190, 90), y=0.008)
    sets.flat(sc, 0.3, 9, -6, 5, (120, 92, 66), y=0.008)
    for i in range(7):
        sets.flat(sc, 1.9 + i * 0.1, 2.0 + i * 0.1, -4.4, 3.2, (104, 78, 56), y=0.012)
    sets.house(sc, -6.2, -9.0, h=3.8, color=(112, 190, 232), roof=(60, 100, 130))
    sets.house(sc, 6.2, -9.0, h=3.6, color=(250, 204, 100), roof=(130, 100, 60))
    sets.tree(sc, -9.5, -4.0, h=4.6)
    sets.tree(sc, 9.8, -4.5, h=4.0)
    for z in np.arange(-5.5, 4.6, 0.55):
        sc.box(T(FENCE_X, 0.5, z), (0.08, 1.0, 0.26), WHITE, layer=3)
    for y in (0.3, 0.75):
        sc.box(T(FENCE_X, y, -0.5), (0.07, 0.09, 10.4), (232, 232, 226), layer=3)
    if tomatoes:
        for x, z in TOMATO_SPOTS:
            tomato(sc, x, z)
    if fence_hose > 0:
        pts = [(-0.18, 0.9 - 0.4 * (i % 2), -2.5 + i * 0.5) for i in range(11)]
        hose(sc, pts, k=fence_hose, r=0.06)
    # watering can near Gomez's patch
    sc.box(T(1.0, 0.25, 3.0), (0.5, 0.5, 0.5), (60, 140, 200), layer=3)
    sc.box(T(1.4, 0.45, 3.0) @ RZ(-35), (0.5, 0.08, 0.08), (60, 140, 200), layer=3)


# --------------------------------------------------------------- classroom
def pizza_board(D):
    D.rect(-1, -1, 1, 1, (52, 92, 70))
    D.ell(-0.38, 0.0, 0.52, 0.62, (246, 200, 90), n=28)
    D.ell(-0.38, 0.0, 0.42, 0.5, (240, 150, 60), n=28)
    for a in range(0, 360, 90):
        r = math.radians(a)
        D.line([(-0.38, 0.0), (-0.38 + 0.52 * math.cos(r), 0.62 * math.sin(r))], (250, 250, 240), 0.03)
    for u, v in ((-0.5, 0.2), (-0.2, 0.28), (-0.3, -0.25), (-0.55, -0.15), (-0.12, -0.05)):
        D.ell(u, v, 0.07, 0.08, (206, 60, 50), n=10)
    D.text(0.56, 0.3, "1/4", (250, 250, 240), h=0.34)
    D.text(0.56, -0.28, "+ 1/4", (250, 250, 240), h=0.2)


def fraction_board(D):
    D.rect(-1, -1, 1, 1, (52, 92, 70))
    D.text(0, 0.35, "1/2 + 1/2", (250, 250, 240), h=0.34)
    D.text(0, -0.25, "= ?", (255, 220, 120), h=0.34)


def class_front(sc, drawing=fraction_board):
    """Classroom: desks in rows facing +z, the board and teacher's desk on the front wall at z=6."""
    sets.classroom(sc)
    sets.wall(sc, 0, 3.5, 6.2, 22, 7, (238, 226, 196), yaw=180)
    sc.box(T(0, 3.2, 6.0) @ RY(180), (7.6, 3.6, 0.2), (150, 104, 70), layer=2)
    sc.box(T(0, 3.2, 5.88) @ RY(180), (7.2, 3.2, 0.1), (52, 92, 70), layer=3, decal=drawing)
    sc.box(T(0, 1.55, 5.75), (7.4, 0.12, 0.35), (150, 104, 70), layer=3)
    sets.desk(sc, -6.0, 4.4, w=2.0)


# ------------------------------------------------------------------ bridge
def sway(x, t, amp):
    return amp * 0.3 * math.sin(x * 0.55 + t * 13.0) if amp else 0.0


def bridge(sc, t=0.0, wobble=0.0, hose_k=0.0, ribbon=0.0, banner=True, podium=True, bunting=True):
    """The Hilltop Bridge: plank deck along x with creek below, podium mid-deck, big oak at the east end.
    wobble>0 rides the deck up and down in a travelling wave; hose_k draws the tie-down hose to the oak."""
    sc.ground(sets.GRASS)
    sets.clouds(sc, seed=5)
    sets.sun(sc)
    sets.flat(sc, -5.2, 5.2, -30, 30, (90, 160, 230), y=0.011)
    for i in range(-5, 6):
        sets.flat(sc, i * 0.9 - 0.4 + 0.2 * math.sin(t * 2 + i), i * 0.9 + 0.1, -9, 9, (130, 190, 245), y=0.013)
    sets.flat(sc, -9, -5.2, -30, 30, (150, 120, 90), y=0.009)
    sets.flat(sc, 5.2, 9, -30, 30, (150, 120, 90), y=0.009)
    for x, z in ((-12, -8), (-14, 4), (14, -9), (15, 6), (-9, -9)):
        sets.tree(sc, x, z, h=5.0)
    sets.house(sc, -10, -15, h=4.0, color=(244, 122, 110), roof=(120, 70, 70))
    sets.house(sc, 6, -16, h=4.4, color=(128, 212, 168), roof=(70, 110, 90))
    # piers
    for x in (-4.0, 0.0, 4.0):
        for z in (DECK_Z0 + 0.4, DECK_Z1 - 0.4):
            sc.box(T(x, 0.2, z), (0.5, 0.9, 0.5), (140, 96, 64), layer=2)
    # deck planks, railings
    n = 16
    w = 2 * BR_X / n
    for i in range(n):
        x = -BR_X + w * (i + 0.5)
        dy = sway(x, t, wobble)
        sc.box(T(x, BR_Y - 0.1 + dy, (DECK_Z0 + DECK_Z1) / 2), (w - 0.05, 0.2, DECK_Z1 - DECK_Z0),
               (206, 154, 100) if i % 2 else (196, 144, 92), layer=3)
        for z in (DECK_Z0 + 0.1, DECK_Z1 - 0.1):
            sc.box(T(x, BR_Y + 0.9 + dy, z), (w, 0.1, 0.12), (250, 250, 244) if i % 2 else (240, 90, 80), layer=3)
            if i % 2 == 0:
                sc.box(T(x, BR_Y + 0.45 + dy, z), (0.12, 0.9, 0.12), (140, 96, 64), layer=3)
    for x in (-BR_X - 0.5, BR_X + 0.5):
        sc.box(T(x, 0.2, (DECK_Z0 + DECK_Z1) / 2), (1.0, 0.4, DECK_Z1 - DECK_Z0), (196, 144, 92), layer=2)
    if banner:
        def ban(D):
            D.rect(-1, -1, 1, 1, (40, 70, 150))
            ps.fit_text(D, ["HILLTOP BRIDGE"], (255, 224, 90), aspect=7.0, fill_w=0.9, fill_h=0.7)
        for z in (DECK_Z0 + 0.2, DECK_Z1 - 0.2):
            sc.box(T(-BR_X + 0.4, 2.4, z), (0.2, 4.8, 0.2), (240, 240, 240), layer=2)
        sc.box(T(-BR_X + 0.4, 4.6, (DECK_Z0 + DECK_Z1) / 2), (0.14, 0.9, DECK_Z1 - DECK_Z0 + 0.8), (40, 70, 150),
               layer=3, decal=None)
        sc.box(T(-BR_X + 0.3, 4.6, (DECK_Z0 + DECK_Z1) / 2) @ RY(-90), (DECK_Z1 - DECK_Z0 + 0.8, 0.9, 0.04),
               (40, 70, 150), layer=3, decal=ban)
    if bunting:
        for z in (DECK_Z1 - 0.1,):
            ls.bunting(sc, (-BR_X + 0.4, BR_Y + 1.7, z), (BR_X - 0.4, BR_Y + 1.7, z), n=18)
    if podium:
        sway0 = sway(0.0, t, wobble)
        pm = T(PODIUM[0], BR_Y + sway0, PODIUM[2])

        def front(D):
            D.rect(-1, -1, 1, 1, (150, 100, 66))
            D.ell(0, 0.1, 0.3, 0.3, (250, 200, 60), n=16)
            D.ell(0, 0.1, 0.18, 0.18, (230, 150, 40), n=14)
            D.rect(-0.7, -0.8, 0.7, -0.55, (250, 200, 60))
        sc.box(pm @ T(0, 0.5, 0), (1.5, 1.0, 0.8), (150, 100, 66), layer=4, decal=front)
        sc.box(pm @ T(0, 1.02, 0), (1.62, 0.08, 0.92), (176, 124, 82), layer=4)
        sc.box(pm @ T(0, 1.35, -0.1), (0.05, 0.6, 0.05), (60, 60, 70), layer=6)
        sc.blob(pm @ T(0, 1.68, -0.05), (0.2, 0.22, 0.2), (190, 190, 200), layer=6, n=10, m=7)
    # the oak and the hose that ties the bridge to it
    sc.box(T(OAK[0], 3.0, OAK[2]), (1.3, 6.0, 1.3), (116, 82, 56), layer=2)
    for dx, dy, dz, r in ((0, 7.4, 0, 4.2), (-2.0, 6.4, 0.8, 3.2), (2.0, 6.6, -0.6, 3.4)):
        sc.blob(T(OAK[0] + dx, dy, OAK[2] + dz), (r, r * 0.8, r), (70, 160, 84), layer=2, n=12, m=8)
    if hose_k > 0:
        z = DECK_Z1 - 0.1
        pts = [(-6.0, BR_Y + 0.75, z), (-3.0, BR_Y + 0.55, z + 0.15), (0.0, BR_Y + 0.75, z + 0.2),
               (3.0, BR_Y + 0.55, z + 0.15), (6.0, BR_Y + 0.75, z), (8.4, BR_Y + 1.0, z - 0.4),
               (9.6, 1.1, OAK[2] + 1.0), (9.8, 1.4, OAK[2] - 0.3), (9.6, 1.7, OAK[2] - 0.9),
               (9.8, 1.9, OAK[2] + 0.3), (9.7, 2.2, OAK[2] + 1.0)]
        hose(sc, pts, k=hose_k, r=0.1, step=1.5)
    # ribbon across the east end
    rx = BR_X - 1.2
    zc = (DECK_Z0 + DECK_Z1) / 2
    ribbon_col = (232, 50, 70)
    if ribbon < 0.5:
        sc.box(T(rx, BR_Y + 0.8, zc), (0.06, 0.2, DECK_Z1 - DECK_Z0), ribbon_col, layer=4)
        sc.blob(T(rx, BR_Y + 0.8, zc + 1.2), (0.4, 0.4, 0.4), ribbon_col, layer=5, n=8, m=6)
    else:
        for sgn, z0 in ((1, DECK_Z0), (-1, DECK_Z1)):
            sc.box(T(rx, BR_Y + 0.5, z0 + sgn * 1.2), (0.06, 1.0, 0.2), ribbon_col, layer=4)
            sc.box(T(rx, BR_Y + 0.9, z0 + sgn * 0.5) @ RX(sgn * 10), (0.06, 0.2, 1.1), ribbon_col, layer=4)
