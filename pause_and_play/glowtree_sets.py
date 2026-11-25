"""Sets and props for Every Tree Glows When You Tell a Secret: glowing oak / maple / pine, the school back lot with its
ivy-covered wall and rusty gate, the hidden garden (glowing flowers, weeds and the old heart tree), the gym, a bulldozer
and its parking-lot sign, Mrs Gomez's tomatoes, a glowing trail, a birthday cake, a picnic, sunhat, garden gloves and
chalk dust."""
import math

import numpy as np

import laughs_sets as ls
import porch_sets as ps
import sets
from engine import RX, RY, RZ, T, font, glow, xf

ORANGE, PINK, GREEN, GOLD = (255, 140, 30), (255, 96, 186), (70, 255, 120), (255, 212, 80)
GLOW = dict(oak=ORANGE, maple=PINK, pine=GREEN)
LEAF = dict(oak=(76, 150, 66), maple=(212, 120, 110), pine=(34, 104, 70))
BARK = (112, 78, 54)
GATE_X, WALL_Z = 6.0, -6.0          # the garden wall runs along x at z = WALL_Z; its gate is at x = GATE_X
STONE = (168, 158, 146)
RUST = (150, 88, 52)


def mix(a, b, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def pyramid(sc, M, r, h, color, n=8, lit=True, layer=2):
    ring = [(r * math.cos(2 * math.pi * i / n), 0.0, r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    faces = [(i, (i + 1) % n, n) for i in range(n)] + [((i + 1) % n, i, n) for i in range(n)]
    sc.solid(M, ring + [(0.0, h, 0.0)], faces, color, layer=layer, lit=lit)


def orbs(sc, c, rx, ry, rz, color, n, t=0.0, seed=1, size=0.3):
    """Glowing blossoms scattered over a canopy, mostly on the camera side."""
    rng = np.random.RandomState(seed)
    for i in range(n):
        th = rng.uniform(0.15, math.pi - 0.15)
        ph = rng.uniform(0.35, 1.55)
        p = np.array([c[0] + rx * math.sin(ph) * math.cos(th), c[1] + ry * math.cos(ph) * rng.uniform(-0.8, 1.0),
                      c[2] + rz * math.sin(ph) * math.sin(th)])
        s = size * (0.85 + 0.25 * math.sin(t * 5 + i))
        sc.blob(T(*p), (s, s, s), mix(color, (255, 255, 255), 0.55), layer=3, lit=False, n=8, m=5)


def glow_tree(sc, x, z, kind="oak", k=0.0, h=5.0, color=None, t=0.0, seed=1, lights=True):
    """A tree that glows with a secret. k 0 = plain tree .. 1 = blazing. Returns the canopy centre."""
    col = color or GLOW[kind]
    base = LEAF[kind]
    lit = k < 0.3
    c = mix(base, col, k * 1.25)
    w = h / 5.5          # canopy widths scale with the tree
    sc.box(T(x, h * 0.28, z), (0.55 * w, h * 0.56, 0.55 * w), BARK, layer=2)
    cen = np.array([x, h * 0.68, z])
    if kind == "pine":
        for i in range(4):
            pyramid(sc, T(x, h * (0.22 + 0.17 * i), z), (2.0 - 0.38 * i) * w, h * 0.3, c, lit=lit)
        cen = np.array([x, h * 0.58, z])
        rx, ry, rz = 1.5 * w, h * 0.3, 1.5 * w
    elif kind == "maple":
        sc.blob(T(x, h * 0.68, z), (3.8 * w, h * 0.5, 3.8 * w), c, layer=2, lit=lit, n=12, m=8)
        sc.blob(T(x + 0.4 * w, h * 0.92, z), (2.5 * w, h * 0.3, 2.5 * w), mix(c, (255, 255, 255), 0.06), layer=2, lit=lit,
                n=10, m=6)
        sc.blob(T(x - 1.4 * w, h * 0.6, z + 0.3 * w), (2.2 * w, h * 0.3, 2.2 * w), c, layer=2, lit=lit, n=10, m=6)
        rx, ry, rz = 1.9 * w, h * 0.26, 1.9 * w
    else:
        sc.blob(T(x, h * 0.66, z), (4.4 * w, h * 0.46, 4.4 * w), c, layer=2, lit=lit, n=12, m=8)
        sc.blob(T(x - 1.4 * w, h * 0.6, z + 0.4 * w), (2.6 * w, h * 0.3, 2.6 * w), mix(c, (255, 255, 255), 0.05),
                layer=2, lit=lit, n=10, m=6)
        sc.blob(T(x + 1.5 * w, h * 0.62, z - 0.2 * w), (2.6 * w, h * 0.32, 2.6 * w), c, layer=2, lit=lit, n=10, m=6)
        sc.blob(T(x, h * 0.88, z), (2.6 * w, h * 0.28, 2.6 * w), mix(c, (255, 255, 255), 0.07), layer=2, lit=lit, n=10,
                m=6)
        rx, ry, rz = 2.1 * w, h * 0.24, 2.1 * w
    if k > 0.05:
        orbs(sc, cen, rx, ry, rz, col, int(16 * k), t, seed, size=0.3 * w)
        if lights:
            sc.light(cen + np.array([0.0, -0.4, 2.6]), col, 420 * k, 0.9)
        ls.glow_at(sc, cen, h * 0.62, col, int(70 * min(1.0, k)))
    return cen


# ------------------------------------------------------------------ glowing trail
def trail(sc, pts, t, k=1.0, color=GOLD, speed=5.0):
    """Stepping stones of light along ground points (x, z); a bright wave runs along the trail."""
    for i, (x, z) in enumerate(pts):
        w = 0.5 + 0.5 * math.sin(i * 0.9 - t * speed)
        s = 0.55 + 0.25 * w
        sc.blob(T(x, 0.05, z), (s, 0.08, s), mix(color, (255, 255, 255), 0.3 * w), layer=2, lit=False, n=10, m=4)
        if k > 0.1 and i % 3 == 0:
            ls.glow_at(sc, (x, 0.2, z), 0.7 * s, color, int(80 * k))
    if k > 0.1:
        for i in range(0, len(pts), 5):
            sc.light((pts[i][0], 0.6, pts[i][1]), color, 90 * k, 0.4)


# ----------------------------------------------------------------- school back lot
def stone_decal(D):
    D.rect(-1, -1, 1, 1, STONE)
    for r in range(8):
        v = -1 + r * 0.25
        D.line([(-1, v), (1, v)], (130, 120, 110), 0.012)
        for c in range(12):
            u = -1 + c * 0.18 + (0.09 if r % 2 else 0)
            D.line([(u, v), (u, v + 0.25)], (130, 120, 110), 0.012)


def wall_run(sc, x0, x1, h=3.4):
    sc.box(T((x0 + x1) / 2, h / 2, WALL_Z), (x1 - x0, h, 0.7), STONE, layer=2, decal=stone_decal)
    sc.box(T((x0 + x1) / 2, h + 0.1, WALL_Z), (x1 - x0 + 0.1, 0.2, 0.9), (190, 180, 168), layer=2)


def ivy_blobs(ivy_off, gate_cover=True):
    """Deterministic ivy clumps: (x, y, size, shade). Clumps over the gate slide aside and up as ivy_off -> 1."""
    rng = np.random.RandomState(8)
    out = []
    for i in range(70):
        x = rng.uniform(-15, 15)
        y = rng.uniform(0.2, 3.4)
        s = rng.uniform(0.9, 1.5)
        out.append((x, y, s, rng.uniform(0.0, 1.0), False))
    if gate_cover:
        for i in range(26):
            x = GATE_X + rng.uniform(-1.6, 1.6)
            y = rng.uniform(0.2, 3.6)
            out.append((x, y, rng.uniform(1.0, 1.5), rng.uniform(0.0, 1.0), True))
    return out


def gate(sc, open_k=0.0, locked=True, rusty=True):
    """Old iron double gate at (GATE_X, WALL_Z): two leaves hinged on brick posts, swinging into the garden (-z)."""
    for sx in (-1, 1):
        sc.box(T(GATE_X + sx * 1.45, 2.1, WALL_Z), (0.7, 4.2, 0.8), (150, 80, 70), layer=2)
        sc.box(T(GATE_X + sx * 1.45, 4.3, WALL_Z), (0.9, 0.2, 1.0), (190, 180, 168), layer=2)
        a = open_k * 100.0
        H = T(GATE_X + sx * 1.1, 0.0, WALL_Z) @ RY(-sx * a)
        w = 1.1
        col = RUST if rusty else (60, 60, 70)
        for yy in (0.4, 2.0, 3.4):
            sc.box(H @ T(-sx * w / 2, yy, 0), (w, 0.1, 0.1), col, layer=3)
        for i in range(6):
            xx = -sx * (0.1 + i * 0.2)
            sc.box(H @ T(xx, 1.9, 0), (0.06, 3.6, 0.06), col, layer=3)
            sc.blob(H @ T(xx, 3.75, 0), (0.12, 0.2, 0.12), col, layer=3, n=6, m=4)
    if locked and open_k < 0.05:
        for i in range(5):
            sc.box(T(GATE_X + 0.4 * math.sin(i * 1.2) - 0.1, 1.5 - i * 0.07, WALL_Z + 0.12 + 0.01 * i), (0.14, 0.14, 0.06),
                   (110, 112, 122), layer=4)
        sc.box(T(GATE_X, 1.2, WALL_Z + 0.15), (0.34, 0.4, 0.14), (216, 170, 60), layer=4)
        sc.blob(T(GATE_X, 1.46, WALL_Z + 0.15), (0.26, 0.28, 0.06), (120, 120, 130), layer=4, n=8, m=5)


def ivy_wall(sc, ivy_off=0.0, gate_open=0.0, locked=True, t=0.0):
    """The garden wall seen from the school side (camera at +z): stone, ivy over the lot, the gate behind the ivy."""
    wall_run(sc, -16, GATE_X - 1.8)
    wall_run(sc, GATE_X + 1.8, 16)
    gate(sc, gate_open, locked)
    for x, y, s, shade, over_gate in ivy_blobs(ivy_off):
        dx = dy = 0.0
        if over_gate:
            dx = (1 if x > GATE_X else -1) * ivy_off * 3.2
            dy = ivy_off * 1.6
            if ivy_off > 0.98:
                continue
        c = mix((40, 120, 56), (88, 170, 70), shade)
        sc.blob(T(x + dx, y + dy, WALL_Z + 0.55), (s, s * 0.8, 0.5), c, layer=4, n=9, m=6, bias=-0.3)


def peeking_flowers(sc, k, t=0.0, tree_k=None):
    """Glowing tops over the wall (the garden hiding behind it) and the old heart tree's crown."""
    rng = np.random.RandomState(4)
    cols = [PINK, GOLD, (120, 190, 255), (255, 130, 80), (190, 130, 255)]
    for i in range(22):
        x = rng.uniform(-14, 14)
        y = 3.7 + rng.uniform(0.0, 0.8)
        s = rng.uniform(0.34, 0.5)
        c = cols[i % 5]
        sc.box(T(x, y - 0.3, WALL_Z - 0.8), (0.07, 0.9, 0.07), (70, 140, 70), layer=2)
        sc.blob(T(x, y + 0.1, WALL_Z - 0.8), (s, s, s), mix((200, 200, 200), c, k), layer=3, lit=k < 0.3, n=8, m=5)
    tk = k if tree_k is None else tree_k
    c = mix((70, 140, 70), GOLD, tk * 1.2)
    sc.box(T(GATE_X + 2.0, 3.0, WALL_Z - 6.0), (0.9, 6.0, 0.9), BARK, layer=2)
    sc.blob(T(GATE_X + 2.0, 7.0, WALL_Z - 6.0), (7.0, 3.6, 6.0), c, layer=2, lit=tk < 0.3, n=12, m=8)
    if tk > 0.05:
        ls.glow_at(sc, (GATE_X + 2.0, 7.0, WALL_Z - 6.0), 6.0, GOLD, int(70 * tk))


def lot(sc, t=0.0):
    """School back lot: grass, a path along the wall, a few ordinary trees."""
    sc.ground((98, 176, 84))
    sets.clouds(sc, seed=4)
    sets.flat(sc, -30, 30, -5.4, -1.0, (206, 200, 190))
    for x in (-12.0, -4.0):
        sets.tree(sc, x, -3.6, h=4.2)


def gym(sc, t=0.0):
    """The school gym along the path (front faces +z) with double doors, a sign and a bike rack."""
    sc.ground((98, 176, 84))
    sets.clouds(sc, seed=5)
    sets.flat(sc, -40, 40, -3.0, 3.2, (206, 200, 190))
    sets.flat(sc, -40, 40, 3.2, 12, (88, 92, 108))

    def front(D):
        D.rect(-1, -1, 1, 1, (232, 196, 120))
        for k in range(-10, 11):
            D.line([(-1, k / 10), (1, k / 10)], (214, 176, 104), 0.004)
        D.rect(-0.2, -1, 0.2, -0.2, (90, 70, 70))
        D.rect(-0.18, -0.98, -0.01, -0.22, (150, 208, 250))
        D.rect(0.01, -0.98, 0.18, -0.22, (150, 208, 250))
        D.rect(-0.35, 0.55, 0.35, 0.82, (250, 250, 240))
        D.text(0, 0.685, "GYM", (200, 70, 60), h=0.17)

    sc.box(T(0, 3.2, -6.0), (14, 6.4, 6.0), (232, 196, 120), layer=2, decal=front)
    sc.box(T(0, 6.5, -5.9), (14.4, 0.4, 6.4), (190, 80, 70), layer=2)
    for i in range(6):
        x = -9.5 + i * 0.7
        sc.box(T(x, 0.45, -1.5), (0.06, 0.9, 0.06), (120, 120, 134), layer=3)
        for k in range(2):
            sc.blob(T(x + 0.14, 0.4, -1.5) @ RY(90), (0.06, 0.5, 0.5), (110 + 40 * k, 120, 220), layer=3, n=6, m=4)
    sets.tree(sc, 9.0, -1.5, h=4.0)


# ------------------------------------------------------------------ the hidden garden
def flower(sc, x, z, h, color, k, t=0.0, i=0):
    sc.box(T(x, h / 2, z), (0.06, h, 0.06), (70, 150, 70), layer=3)
    sc.blob(T(x + 0.12, h * 0.45, z), (0.3, 0.06, 0.16), (80, 170, 80), layer=3, n=6, m=4)
    c = mix((210, 210, 214), color, k)
    s = 0.34 + 0.03 * math.sin(t * 4 + i)
    for a in range(5):
        an = a * 2 * math.pi / 5
        sc.blob(T(x + 0.17 * math.cos(an), h + 0.17 * math.sin(an) * 0.3, z + 0.17 * math.sin(an)), (0.2, 0.12, 0.2), c,
                layer=4, lit=k < 0.3, n=6, m=4)
    sc.blob(T(x, h + 0.04, z), (0.2, 0.14, 0.2), mix((200, 170, 60), (255, 255, 200), k), layer=4, lit=k < 0.3, n=6, m=4)
    if k > 0.2 and i % 4 == 0:
        ls.glow_at(sc, (x, h, z), 0.55, color, int(60 * k))


def weed(sc, x, z, k, t=0.0):
    sc.box(T(x, 0.25, z), (0.04, 0.5, 0.04), (110, 150, 70), layer=3)
    c = mix((236, 236, 230), (255, 255, 200), k)
    sc.blob(T(x, 0.55, z), (0.34, 0.34, 0.34), c, layer=4, lit=k < 0.3, n=10, m=6)
    for a in range(6):
        an = a * math.pi / 3
        sc.blob(T(x + 0.28 * math.cos(an), 0.55 + 0.1 * math.sin(an), z + 0.2 * math.sin(an)), (0.12, 0.12, 0.12), c,
                layer=4, lit=k < 0.3, n=6, m=4)
    if k > 0.2:
        ls.glow_at(sc, (x, 0.55, z), 0.6, (255, 255, 200), int(70 * k))


GARDEN_COLS = [PINK, GOLD, (110, 190, 255), (255, 130, 70), (190, 130, 255), (255, 255, 255)]


def garden(sc, t=0.0, k=1.0, weeds_k=None, tree_k=None, lights=True, flowers=True):
    """The hidden garden behind the wall: flowers light up in a wave from the gate (k 0 -> 1), a gold heart tree,
    a stone path, a bench. `weeds_k` lets the weeds glow later than the flowers."""
    sc.ground((108, 196, 96))
    sets.clouds(sc, seed=7)
    sets.flat(sc, GATE_X - 0.9, GATE_X + 0.9, -26, WALL_Z + 0.4, (206, 196, 176), y=0.014)
    for z in np.arange(WALL_Z - 1.0, -25, 1.6):
        sets.flat(sc, GATE_X - 0.5, GATE_X + 0.5, z - 0.5, z + 0.5, (186, 176, 156), y=0.02)
    rng = np.random.RandomState(12)
    n = 0
    if flowers:
        for row in range(7):
            for side in (-1, 1):
                for c in range(5):
                    x = GATE_X + side * (1.7 + c * 0.9 + rng.uniform(-0.2, 0.2))
                    z = WALL_Z - 2.0 - row * 2.6 + rng.uniform(-0.5, 0.5)
                    kk = max(0.0, min(1.0, k * 1.8 - (row / 7.0) * 0.8 - c * 0.04))
                    flower(sc, x, z, rng.uniform(0.7, 1.3), GARDEN_COLS[(row + c + n) % 6], kk, t, n)
                    n += 1
    wk = k if weeds_k is None else weeds_k
    for i in range(7):
        weed(sc, GATE_X + rng.uniform(-8, 8), WALL_Z - rng.uniform(1.4, 4.0) - i * 0.4, wk, t)
    tk = k if tree_k is None else tree_k
    hx, hz = GATE_X, WALL_Z - 19.0
    sc.box(T(hx, 2.6, hz), (1.4, 5.2, 1.4), BARK, layer=2)
    sc.blob(T(hx, 7.4, hz), (8.6, 5.0, 8.0), mix((70, 150, 70), GOLD, tk * 1.2), layer=2, lit=tk < 0.3, n=12, m=8)
    if tk > 0.05:
        ls.glow_at(sc, (hx, 7.2, hz), 7.0, GOLD, int(70 * tk))
        orbs(sc, np.array([hx, 7.0, hz + 1.0]), 4.0, 2.4, 3.4, GOLD, int(20 * tk), t, 9, size=0.4)
        if lights:
            sc.light((hx, 5.0, hz + 5.0), GOLD, 900 * tk, 1.2)
    sc.box(T(GATE_X - 3.2, 0.5, WALL_Z - 5.0), (1.8, 0.1, 0.6), (150, 100, 66), layer=3)
    for sx in (-0.8, 0.8):
        sc.box(T(GATE_X - 3.2 + sx, 0.25, WALL_Z - 5.0), (0.1, 0.5, 0.5), (110, 76, 50), layer=3)
    wall_run(sc, -16, GATE_X - 1.8)
    wall_run(sc, GATE_X + 1.8, 16)
    for sx in (-1, 1):
        sc.box(T(GATE_X + sx * 1.45, 2.1, WALL_Z), (0.7, 4.2, 0.8), (150, 80, 70), layer=2)
        sc.box(T(GATE_X + sx * 1.45, 4.3, WALL_Z), (0.9, 0.2, 1.0), (190, 180, 168), layer=2)
    return np.array([hx, 7.0, hz])


# -------------------------------------------------------------- bulldozer and its sign
def bulldozer(sc, M, t=0.0, engine=True):
    """Yellow bulldozer at M, blade toward +z (the camera side when M is the identity)."""
    Y, D = (250, 196, 40), (60, 60, 70)
    for sx in (-1, 1):
        sc.box(M @ T(sx * 1.25, 0.45, 0), (0.7, 0.9, 3.8), D, layer=4)
        for k in range(4):
            sc.blob(M @ T(sx * 1.25, 0.45, -1.3 + k * 0.85) @ RY(90), (0.7, 0.62, 0.3), (110, 110, 124), layer=4, n=8, m=6)
    sc.box(M @ T(0, 1.2, -0.2), (2.4, 0.9, 3.0), Y, layer=4)
    sc.box(M @ T(0, 2.1, -0.9), (1.8, 1.1, 1.5), Y, layer=4)
    sc.box(M @ T(0, 2.15, -0.15), (1.5, 0.8, 0.06), (150, 208, 250), layer=5)
    sc.box(M @ T(0, 2.75, -0.9), (2.0, 0.12, 1.7), D, layer=4)
    sc.box(M @ T(0.7, 2.6, -1.5), (0.14, 1.2, 0.14), D, layer=4)
    sc.box(M @ T(0, 0.9, 2.1), (3.6, 1.5, 0.3), (210, 150, 30), layer=4)
    for sx in (-1, 1):
        sc.box(M @ T(sx * 1.2, 1.0, 1.2), (0.2, 0.2, 1.8), D, layer=4)
    if engine:
        p = xf(M, (0.7, 3.2, -1.5))
        for i in range(4):
            ph = (t * 1.2 + i * 0.25) % 1.0
            sc.sprite(p + np.array([0.15 * ph, 1.4 * ph, 0.0]),
                      lambda d, x, y, s, col, ph=ph: d.ellipse([x - 0.22 * s * (1 + ph), y - 0.22 * s * (1 + ph),
                                                                x + 0.22 * s * (1 + ph), y + 0.22 * s * (1 + ph)],
                                                               fill=(90, 90, 96, int(150 * (1 - ph)))), layer=7, live=True)
    return xf(M, (0, 2.2, -0.9))


def lot_sign(sc, M, state="parking"):
    """Roadside board on two posts: NEW PARKING LOT / SATURDAY SUNRISE, or the garden's own sign."""
    for sx in (-1, 1):
        sc.box(M @ T(sx * 1.5, 1.2, 0), (0.14, 2.4, 0.14), (120, 84, 60), layer=3)

    def face(D):
        if state == "parking":
            D.rect(-1, -1, 1, 1, (250, 250, 250))
            D.rect(-0.96, -0.96, 0.96, 0.96, (40, 90, 200))
            ps.fit_text(D, ["NEW", "PARKING LOT", "SATURDAY", "SUNRISE"], (255, 255, 255), aspect=2.0, fill_w=0.86,
                        fill_h=0.8)
        else:
            D.rect(-1, -1, 1, 1, (250, 232, 150))
            D.rect(-0.96, -0.96, 0.96, 0.96, (80, 170, 100))
            ps.fit_text(D, ["THE GLOW", "GARDEN"], (255, 240, 170), aspect=2.0, fill_w=0.86, fill_h=0.7)

    sc.box(M @ T(0, 2.3, 0.08), (3.6, 1.7, 0.12), (250, 250, 250), layer=4, decal=face)


# ---------------------------------------------------------------------- small props
def sunhat(sc, a, spec, droop=0.0):
    """Mrs Gomez's straw sunhat on her head; droop tips the brim down."""
    s = spec["s"]
    hw, hh, hd = (v * s for v in spec["head"])
    Mh = a["Mh"]
    straw, band = (236, 200, 110), (220, 80, 90)
    sc.blob(Mh @ T(0, hh * 0.46, 0) @ RX(-droop * 18), (hw * 2.7, 0.06 * s, hd * 2.7), straw, e=0.7, layer=6, n=22, m=4)
    sc.blob(Mh @ T(0, hh * 0.66, 0), (hw * 1.2, hh * 0.46, hd * 1.2), straw, e=0.5, layer=6, n=18, m=8)
    sc.blob(Mh @ T(0, hh * 0.52, 0), (hw * 1.24, hh * 0.12, hd * 1.24), band, e=0.4, layer=6, n=18, m=4)


def garden_gloves(sc, a, s=1.0, color=(90, 200, 90)):
    for k in ("M_hand_l", "M_hand_r"):
        if k in a:
            sc.box(a[k] @ T(0, -0.05 * s, 0), (0.36 * s, 0.34 * s, 0.34 * s), color, layer=6)
            sc.box(a[k] @ T(0, 0.14 * s, 0), (0.4 * s, 0.1 * s, 0.38 * s), mix(color, (255, 255, 255), 0.3), layer=6)


def chalk(sc, a, t=0.0):
    """Chalk dust on Ms Patel's hands."""
    for k in ("M_hand_l", "M_hand_r"):
        if k in a:
            sc.blob(a[k] @ T(0, -0.04, 0), (0.24, 0.22, 0.24), (250, 250, 250), layer=6, n=8, m=6)


def dirt_cheeks(D):
    for sx in (-1, 1):
        D.ell(sx * 0.62, -0.18, 0.12, 0.07, (120, 84, 56), n=10)
        D.ell(sx * 0.42, -0.34, 0.07, 0.04, (120, 84, 56), n=8)


def tomatoes(sc, x, z, n=4):
    for i in range(n):
        px = x + i * 0.9
        sc.box(T(px, 0.7, z), (0.05, 1.4, 0.05), (160, 120, 80), layer=3)
        sc.blob(T(px, 0.7, z), (0.6, 1.0, 0.6), (60, 150, 70), layer=3, n=9, m=6)
        for j in range(3):
            sc.blob(T(px + 0.18 * (j - 1), 0.5 + 0.28 * j, z + 0.28), (0.24, 0.24, 0.24), (235, 60, 50), layer=4, n=8, m=6)


def cake(sc, M, s=1.0, flame=True, t=0.0, bite=False):
    sc.blob(M @ T(0, 0.2 * s, 0), (1.0 * s, 0.4 * s, 1.0 * s), (250, 232, 200), layer=5, e=0.4, n=16, m=6)
    sc.blob(M @ T(0, 0.52 * s, 0), (0.8 * s, 0.3 * s, 0.8 * s), (255, 150, 190), layer=5, e=0.4, n=16, m=6)
    sc.blob(M @ T(0, 0.72 * s, 0), (0.62 * s, 0.1 * s, 0.62 * s), (255, 255, 255), layer=5, e=0.5, n=14, m=4)
    sc.box(M @ T(0, 0.9 * s, 0), (0.05 * s, 0.26 * s, 0.05 * s), (90, 160, 255), layer=5)
    if flame:
        p = xf(M, (0, 1.1 * s, 0))
        sc.blob(T(*p), (0.09 * s, 0.16 * s, 0.09 * s), (255, 214, 90), layer=6, lit=False, n=8, m=6)
        ls.glow_at(sc, p, 0.3 * s, (255, 200, 90), 70)


def picnic(sc, M):
    def check(D):
        D.rect(-1, -1, 1, 1, (250, 250, 250))
        for k in range(-5, 5):
            D.rect(k * 0.2, -1, k * 0.2 + 0.1, 1, (230, 80, 80))
            D.rect(-1, k * 0.2, 1, k * 0.2 + 0.1, (230, 80, 80, 180) if False else (240, 150, 150))

    sc.box(M @ T(0, 0.02, 0), (5.0, 0.04, 3.6), (250, 250, 250), layer=2, decal=check)


def timer(sc, text, color=(255, 214, 90)):
    """Countdown plate at the top of the frame."""
    def fn(d, W, H):
        f = font(int(W * 0.085))
        w = int(f.getlength(text)) + int(W * 0.08)
        h = int(W * 0.15)
        x0, y0 = (W - w) // 2, int(H * 0.06)
        d.rounded_rectangle([x0, y0, x0 + w, y0 + h], int(h * 0.3), fill=(20, 16, 40, 200), outline=color + (255,),
                            width=int(W * 0.008))
        d.text((W // 2, y0 + h // 2), text, font=f, fill=color + (255,), anchor="mm")

    sc.overlay(fn)


def beam(sc, base, k, color=GREEN):
    """A tall light beam from a tree into the sky."""
    if k <= 0.02:
        return
    for i, (w, a) in enumerate(((1.8, 50), (1.0, 80), (0.45, 140))):
        sc.box(T(base[0], 22.0, base[2]), (w * (0.6 + 0.4 * k), 44.0, w * (0.6 + 0.4 * k)), mix(color, (255, 255, 255), 0.2 * i),
               layer=3, lit=False)
