"""Sets and props for The Walking Shoes: Mrs Doyle's porch and her giant jigsaw puzzle (grass with gaps, then
the finished 1965 goalie picture), the bakery, the lake with a dock and a duck, the soccer field and goal,
the skate park, candy store and fun fair inserts, old leather gloves, a soccer ball and a shoe sparkle trail."""
import math

import numpy as np

import laughs_sets as ls
import porch_sets as ps
import sets
from engine import RX, RY, RZ, T, font, glow, xf

GRASS_C = (96, 170, 80)
LEATHER = (150, 100, 60)
SEPIA = (180, 150, 110)


# ------------------------------------------------------------------ puzzle
def puzzle_decal(state="grass", missing=0.5, reveal=1.0):
    """Jigsaw picture. state 'grass': nearly all green with gaps; 'full': the 1965 champion goalie picture."""
    rng = np.random.RandomState(11)
    cols, rows = 12, 9
    holes = {(c, r) for c in range(cols) for r in range(rows) if rng.uniform() < missing}

    def dec(D):
        D.rect(-1, -1, 1, 1, (250, 246, 236))
        if state == "grass":
            D.rect(-0.94, -0.94, 0.94, 0.94, GRASS_C)
            for k in range(60):
                x, y = rng.uniform(-0.9, 0.9), rng.uniform(-0.9, 0.9)
                D.line([(x, y), (x + 0.02, y + 0.06)], (80, 150, 70), 0.01)
        else:
            sep = lambda c: tuple(int(v * 0.35 + s * 0.65) for v, s in zip(c, SEPIA))
            D.rect(-0.94, -0.94, 0.94, 0.94, sep((110, 180, 90)))
            D.rect(-0.94, 0.45, 0.94, 0.94, sep((170, 200, 230)))
            for x in (-0.7, 0.7):  # goal posts and net
                D.rect(x - 0.03, -0.2, x + 0.03, 0.55, sep((250, 250, 250)))
            D.rect(-0.7, 0.52, 0.7, 0.58, sep((250, 250, 250)))
            for k in range(1, 8):
                D.line([(-0.7 + k * 0.175, -0.2), (-0.7 + k * 0.175, 0.52)], sep((220, 220, 220)), 0.006)
            for k in range(1, 5):
                D.line([(-0.7, -0.2 + k * 0.14), (0.7, -0.2 + k * 0.14)], sep((220, 220, 220)), 0.006)
            # the goalie, diving left, gloves out
            gk = sep((230, 80, 70))
            D.poly([(-0.25, 0.05), (0.15, 0.25), (0.2, 0.12), (-0.2, -0.08)], gk)
            D.ell(0.26, 0.24, 0.07, 0.08, sep((240, 200, 160)), n=12)
            D.ell(0.26, 0.31, 0.07, 0.04, sep((90, 60, 40)), n=12)
            for gx, gy in ((-0.38, 0.12), (-0.32, -0.02)):
                D.ell(gx, gy, 0.06, 0.05, sep((140, 90, 50)), n=10)
                D.line([(gx + 0.04, gy), (-0.2, 0.02)], gk, 0.03)
            D.line([(0.18, 0.13), (0.42, 0.0)], sep((40, 40, 60)), 0.035)
            D.line([(0.15, 0.18), (0.45, 0.12)], sep((40, 40, 60)), 0.035)
            D.ell(-0.5, 0.18, 0.06, 0.06, sep((250, 250, 250)), n=12)
            # the trophy behind her
            tr = sep((240, 196, 60))
            D.poly([(0.62, 0.62), (0.78, 0.62), (0.74, 0.42), (0.66, 0.42)], tr)
            D.rect(0.68, 0.32, 0.72, 0.42, tr)
            D.rect(0.63, 0.28, 0.77, 0.32, tr)
            if hasattr(D, "img"):
                ps.fit_text(D, ["TOWN CHAMPIONS 1965"], sep((90, 60, 40)), aspect=1.33, fill_w=0.7, fill_h=0.06,
                            dy=0.39)
        # jigsaw grid and gaps
        for c in range(cols):
            for r in range(rows):
                u0, v0 = -0.94 + c * 1.88 / cols, -0.94 + r * 1.88 / rows
                u1, v1 = u0 + 1.88 / cols, v0 + 1.88 / rows
                if (c, r) in holes and state == "grass":
                    D.rect(u0, v0, u1, v1, (120, 96, 70))
        for c in range(1, cols):
            u = -0.94 + c * 1.88 / cols
            D.line([(u, -0.94), (u, 0.94)], (60, 60, 60) if state == "grass" else (110, 96, 80), 0.004)
            for r in range(rows):
                v = -0.94 + (r + 0.5) * 1.88 / rows
                D.ell(u + (0.02 if (c + r) % 2 else -0.02), v, 0.025, 0.03,
                      GRASS_C if state == "grass" else (170, 150, 120), n=8)
        for r in range(1, rows):
            v = -0.94 + r * 1.88 / rows
            D.line([(-0.94, v), (0.94, v)], (60, 60, 60) if state == "grass" else (110, 96, 80), 0.004)

    return dec


def puzzle(sc, M, state="grass", missing=0.5, w=1.6, h=1.2):
    """Puzzle lying on a table top at M (picture faces +y)."""
    sc.box(M @ RX(-90), (w, h, 0.02), (250, 246, 236), layer=5, decal=puzzle_decal(state, missing))


def piece(sc, M, color=(110, 160, 90), s=1.0):
    sc.box(M, (0.18 * s, 0.03 * s, 0.18 * s), color, layer=7)
    for dx, dz in ((0.11, 0), (0, 0.11)):
        sc.blob(M @ T(dx * s, 0, dz * s), (0.07 * s, 0.03 * s, 0.07 * s), color, layer=7, n=8, m=4)


# --------------------------------------------------------------- the porch
PORCH_Y = 0.35
CHAIR = np.array([-1.1, PORCH_Y, 0.9])   # Mrs Doyle's rocking chair (faces +x, toward the table)
TABLE = np.array([0.2, PORCH_Y, 1.0])    # puzzle table
RUDY_P = np.array([1.4, PORCH_Y, 1.2])   # where Rudy stands to hand her pieces


def rocking_chair(sc, M, rock=0.0):
    R = M @ RX(rock)
    wood = (150, 100, 60)
    sc.box(R @ T(0, 0.75, 0), (0.9, 0.1, 0.8), wood, layer=4)
    sc.box(R @ T(0, 1.35, -0.38), (0.9, 1.2, 0.08), wood, layer=4)
    for sx in (-1, 1):
        sc.box(R @ T(sx * 0.4, 0.38, 0), (0.08, 0.75, 0.08), wood, layer=4)
        sc.box(R @ T(sx * 0.4, 0.06, 0) @ RX(90), (0.08, 1.2, 0.1), wood, layer=4)
        sc.box(R @ T(sx * 0.45, 1.05, 0.05), (0.08, 0.08, 0.7), wood, layer=4)


def doyle_porch(sc, t=0.0, state="grass", missing=0.5, cat=True, table=True, rock=True):
    """Mrs Doyle's porch: a long deck at y = PORCH_Y in front of her house (front wall at z = -0.3)."""
    sc.ground(sets.GRASS)
    sets.clouds(sc, seed=2)
    sets.sun(sc, x=0.85, y=0.08)
    sets.flat(sc, -60, 60, 5.5, 9.0, (88, 92, 108))
    sets.flat(sc, -60, 60, 4.3, 5.5, (220, 214, 204))
    color = (250, 214, 120)

    def siding(D):
        for i in range(1, 14):
            v = -1 + i * 2 / 14
            D.line([(-1, v), (1, v)], tuple(c * 0.9 for c in color), 0.01)
    sc.box(T(0, 2.2, -2.4), (8.0, 4.4, 4.2), color, layer=2, decal=siding)
    for x in (-2.6, 2.6):
        ps.window(sc, T(x, 2.5, -0.28), 0.0, color=ls.DAY_GLASS)
    sc.box(T(0, 1.4, -0.29), (1.1, 2.4, 0.06), (120, 80, 60), layer=2)
    verts = [(-4.4, 4.4, -0.0), (4.4, 4.4, -0.0), (4.4, 4.4, -4.8), (-4.4, 4.4, -4.8), (-4.4, 6.2, -2.4), (4.4, 6.2, -2.4)]
    sc.solid(np.eye(4), verts, [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)], (150, 80, 70), layer=2)
    sc.box(T(0, PORCH_Y / 2, 1.0), (8.0, PORCH_Y, 2.6), (196, 160, 120), layer=2)
    sc.box(T(0, 0.1, 2.55), (2.0, 0.2, 0.5), (196, 160, 120), layer=2)
    sc.box(T(0, 3.3, 1.0), (8.4, 0.14, 2.9), (150, 80, 70), layer=2)
    for x in (-3.8, 3.8):
        sc.box(T(x, 1.8, 2.2), (0.16, 2.9, 0.16), (250, 248, 240), layer=2)
    for i in range(14):  # rail
        x = -3.8 + i * 0.58
        if abs(x) < 1.0:
            continue
        sc.box(T(x, PORCH_Y + 0.45, 2.25), (0.08, 0.9, 0.08), (250, 248, 240), layer=3)
    sc.box(T(-2.4, PORCH_Y + 0.9, 2.25), (2.8, 0.08, 0.1), (250, 248, 240), layer=3)
    sc.box(T(2.4, PORCH_Y + 0.9, 2.25), (2.8, 0.08, 0.1), (250, 248, 240), layer=3)
    rocking_chair(sc, T(*CHAIR) @ RY(90), 6 * math.sin(t * 2.2) if rock else 0.0)
    if table:
        sc.box(T(TABLE[0], PORCH_Y + 0.8, TABLE[2]), (2.0, 0.08, 1.4), (170, 120, 80), layer=4)
        for sx in (-1, 1):
            for sz in (-1, 1):
                sc.box(T(TABLE[0] + sx * 0.9, PORCH_Y + 0.4, TABLE[2] + sz * 0.6), (0.08, 0.8, 0.08), (140, 96, 64),
                       layer=4)
        puzzle(sc, T(TABLE[0], PORCH_Y + 0.85, TABLE[2]), state, missing)
    if cat:
        ls.cat(sc, T(2.8, PORCH_Y, 0.4) @ RY(-40), t, mood="happy" if int(t) % 3 else "calm")
    return np.array([TABLE[0], PORCH_Y + 0.86, TABLE[2]])


# ----------------------------------------------------------- town places
def bakery(sc, t=0.0):
    sets.town(sc)
    sc.box(T(0, 2.0, -3.0), (6.0, 4.0, 3.0), (250, 220, 200), layer=2)

    def sign(D):
        D.rect(-1, -1, 1, 1, (150, 90, 60))
        ps.fit_text(D, ["BAKERY"], (255, 240, 210), aspect=4.0, fill_w=0.8, fill_h=0.6)
    sc.box(T(0, 4.3, -1.45), (4.0, 0.9, 0.08), (150, 90, 60), layer=3, decal=sign)

    def stripes(D):
        for k in range(-6, 6):
            D.rect(k / 6, -1, k / 6 + 1 / 12, 1, (255, 255, 255))
        D.rect(-1, -1, 1, -0.7, (230, 90, 90))
    sc.box(T(0, 3.3, -1.1) @ RX(20), (6.2, 0.06, 1.2), (230, 90, 90), layer=3, decal=stripes)
    sc.box(T(0, 1.3, -1.48), (1.1, 2.4, 0.05), (130, 90, 60), layer=3)
    sc.box(T(-2.0, 1.8, -1.48), (1.6, 1.2, 0.05), (190, 220, 240), layer=3, lit=False)
    for i in range(3):
        sc.blob(T(-2.4 + i * 0.4, 1.4, -1.4), (0.35, 0.18, 0.2), (220, 160, 90), layer=4, n=10, m=6)


def bakery_counter(sc, t=0.0):
    sets.floor_tiles(sc, -6, 6, -4, 6, (230, 220, 200), (220, 210, 190), step=1.0)
    sets.wall(sc, 0, 3.0, -3.2, 12, 6, (250, 230, 210))
    sc.box(T(0, 0.6, -1.2), (4.0, 1.2, 1.0), (180, 130, 90), layer=3)
    for i in range(6):
        sc.blob(T(-1.6 + i * 0.64, 1.32, -1.2), (0.5, 0.25, 0.3), [(220, 160, 90), (240, 200, 140), (200, 120, 70)][i % 3],
                layer=4, n=10, m=6)
    for i in range(4):
        sc.box(T(-1.5 + i, 2.6, -3.0), (0.8, 0.06, 0.4), (180, 130, 90), layer=3)
        sc.blob(T(-1.5 + i, 2.8, -2.95), (0.5, 0.3, 0.3), (230, 180, 110), layer=3, n=10, m=6)


def flour(sc, a, t):
    def fn(d, x, y, s, col):
        rng = np.random.RandomState(4)
        for i in range(14):
            dx, dy = rng.uniform(-0.6, 0.6), rng.uniform(-0.9, 0.6)
            r = rng.uniform(0.03, 0.07) * s
            d.ellipse([x + dx * s - r, y + dy * s - r, x + dx * s + r, y + dy * s + r], fill=(255, 255, 255, 200))
    sc.sprite(a["head"], fn, layer=8, live=True)


def lake(sc, t=0.0):
    sc.ground(sets.GRASS)
    sets.clouds(sc, seed=3)
    sets.flat(sc, -60, 60, -40, -1.0, (80, 150, 220), y=0.012)
    for i in range(10):
        sc.box(T(0, 0.35, 0.2 - i * 0.6), (1.6, 0.1, 0.5), (170, 120, 80), layer=3)
    for z in (0.2, -2.8, -5.2):
        for sx in (-1, 1):
            sc.box(T(sx * 0.75, 0.0, z), (0.14, 0.9, 0.14), (130, 90, 60), layer=3)
    for x, z in ((-6, -8), (5, -10), (-3, -14)):
        sc.blob(T(x, 0.05, z), (1.4, 0.1, 0.4), (60, 120, 70), layer=2, n=8, m=4)


def duck(sc, M, t=0.0, s=1.0):
    sc.blob(M @ T(0, 0.2 * s, 0), (0.45 * s, 0.32 * s, 0.6 * s), (250, 250, 250), layer=6, n=12, m=8)
    sc.blob(M @ T(0, 0.48 * s, 0.22 * s), (0.25 * s, 0.25 * s, 0.25 * s), (250, 250, 250), layer=6, n=10, m=8)
    sc.box(M @ T(0, 0.46 * s, 0.38 * s), (0.12 * s, 0.05 * s, 0.14 * s), (250, 160, 40), layer=6)
    for sx in (-1, 1):
        sc.blob(M @ T(sx * 0.1 * s, 0.53 * s, 0.32 * s), (0.04 * s, 0.05 * s, 0.02 * s), (30, 30, 36), layer=6, n=6, m=4)
    return xf(M, (0, 0.7 * s, 0.2 * s))


def splash(sc, pos, t, start=0.0):
    tt = t - start
    if tt < 0 or tt > 0.8:
        return
    p = np.asarray(pos, float)
    for i in range(12):
        a = 2 * math.pi * i / 12

        def fn(d, x, y, s, col, a=a):
            r = (0.12 + tt * 0.1) * s
            px = x + math.cos(a) * tt * 2.2 * s
            py = y - (math.sin(a) * 0.6 + 2.4 * tt - 4 * tt * tt) * s
            d.ellipse([px - r, py - r, px + r, py + r], fill=(200, 230, 255, int(230 * (1 - tt / 0.8))))
        sc.sprite(p, fn, layer=8, live=True)


def skate_park(sc):
    sc.ground((200, 200, 206))
    sets.clouds(sc, seed=5)
    for x in (-3.0, 3.0):
        verts = [(-1.5, 0, 1.5), (1.5, 0, 1.5), (1.5, 0, -1.5), (-1.5, 0, -1.5), (-1.5, 2.0, -1.5), (1.5, 2.0, -1.5)]
        sc.solid(T(x, 0, -2) @ RY(0 if x < 0 else 180), verts, [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)],
                 (170, 176, 190), layer=3)
    sc.box(T(0, 0.3, -2.0), (2.0, 0.6, 1.0), (240, 200, 60), layer=3)


def candy_store(sc):
    sets.town(sc)
    ls.stall(sc, 0, -1.2, (255, 120, 180), sign="CANDY")
    rng = np.random.RandomState(6)
    for i in range(16):
        sc.blob(T(-1.0 + (i % 8) * 0.28, 1.45 + 0.1 * (i // 8), -1.0 + 0.3 * (i // 8)), (0.2, 0.2, 0.2),
                [(255, 90, 140), (90, 200, 255), (255, 220, 70), (150, 230, 120)][i % 4], layer=4, n=8, m=6)


def fun_fair(sc, t=0.0):
    sc.ground(sets.GRASS)
    sets.clouds(sc, seed=6)
    W = T(0, 7.0, -10) @ RZ(t * 20)
    for i in range(12):
        a = 30 * i
        sc.box(W @ RZ(a) @ T(0, 2.8, 0), (0.12, 5.6, 0.12), (240, 240, 240), layer=3)
        sc.box(W @ RZ(a) @ T(0, 5.6, 0) @ RZ(-a - t * 20), (0.9, 0.8, 0.9),
               [(255, 90, 90), (90, 190, 255), (255, 214, 70), (150, 230, 120)][i % 4], layer=3)
    for sx in (-1, 1):
        sc.box(T(sx * 2.4, 3.5, -10) @ RZ(sx * 20), (0.3, 7.5, 0.3), (200, 200, 210), layer=3)
    ls.stall(sc, -4, -2, (120, 180, 255), sign="FUN FAIR")


# ------------------------------------------------------------ soccer field
GOAL_Z = -6.0
SPOT = np.array([0.0, 0.0, 0.5])


def soccer_field(sc, t=0.0, crowd=True, banner=True):
    sc.ground((90, 170, 80))
    sets.clouds(sc, seed=4)
    for i in range(-10, 10):
        if i % 2:
            sets.flat(sc, -30, 30, i * 3.0, i * 3.0 + 3.0, (100, 180, 90), y=0.011)
    for z0, z1, x0, x1 in ((GOAL_Z - 0.05, GOAL_Z + 0.05, -12, 12), (GOAL_Z, GOAL_Z + 4.5, -6.0, -5.9),
                           (GOAL_Z, GOAL_Z + 4.5, 5.9, 6.0), (GOAL_Z + 4.45, GOAL_Z + 4.55, -6.0, 6.0)):
        sets.flat(sc, x0, x1, z0, z1, (250, 250, 250), y=0.013)
    sc.blob(T(SPOT[0], 0.014, SPOT[2]), (0.25, 0.01, 0.25), (250, 250, 250), layer=1, n=12, m=4)
    # goal
    for x in (-2.4, 2.4):
        sc.box(T(x, 1.2, GOAL_Z), (0.14, 2.4, 0.14), (250, 250, 250), layer=3)
    sc.box(T(0, 2.4, GOAL_Z), (4.94, 0.14, 0.14), (250, 250, 250), layer=3)
    for k in range(13):
        x = -2.4 + k * 0.4
        sc.box(T(x, 1.2, GOAL_Z - 1.0), (0.02, 2.4, 0.02), (230, 230, 230), layer=2)
    for k in range(7):
        sc.box(T(0, 0.2 + k * 0.36, GOAL_Z - 1.0), (4.8, 0.02, 0.02), (230, 230, 230), layer=2)
    sc.box(T(0, 2.4, GOAL_Z - 0.5), (4.8, 0.02, 1.0), (230, 230, 230), layer=2)
    if banner:
        def ban(D):
            D.rect(-1, -1, 1, 1, (40, 120, 60))
            ps.fit_text(D, ["CHAMPIONSHIP"], (255, 230, 90), aspect=6.0, fill_w=0.85, fill_h=0.65)
        sc.box(T(0, 4.2, GOAL_Z - 3.0), (9.0, 1.4, 0.1), (40, 120, 60), layer=2, decal=ban)
        for sx in (-1, 1):
            sc.box(T(sx * 4.4, 2.2, GOAL_Z - 3.0), (0.15, 4.4, 0.15), (240, 240, 240), layer=2)
    if crowd:
        from cast import character, crowd_spec
        for r in range(2):
            sc.box(T(-11 - r * 1.0, 0.3 + r * 0.6, -2.0), (1.0, 0.6 + r * 1.2, 14.0), (170, 170, 180), layer=2)
            for i in range(6):
                spec = crowd_spec(i + r * 6 + 30, adult=(i + r) % 3 != 0)
                character(sc, spec, (-11 - r * 1.0, 0.6 + r * 0.6, -7.0 + i * 2.2), yaw=90,
                          face=("grin", "joy", "shock")[(i + r) % 3],
                          pose=dict(al=(150 * ((i + int(t * 3)) % 2), -20), ar=(30, 10)))


def ball(sc, M, s=1.0):
    sc.blob(M, (0.45 * s, 0.45 * s, 0.45 * s), (250, 250, 250), layer=6, n=16, m=10)
    for a, b in ((0, 0), (72, 30), (144, -30), (216, 30), (288, -30), (36, 80)):
        p = (0.2 * s * math.cos(math.radians(a)) * math.cos(math.radians(b)), 0.2 * s * math.sin(math.radians(b)),
             0.2 * s * math.sin(math.radians(a)) * math.cos(math.radians(b)))
        sc.blob(M @ T(*p), (0.13 * s, 0.13 * s, 0.13 * s), (30, 30, 36), layer=6, n=8, m=6)


def gloves(sc, a, s=1.0, color=LEATHER):
    for k in ("M_hand_l", "M_hand_r"):
        if k in a:
            sc.box(a[k] @ T(0, -0.08 * s, 0), (0.42 * s, 0.4 * s, 0.38 * s), color, layer=6)
            sc.box(a[k] @ T(0, 0.16 * s, 0), (0.46 * s, 0.12 * s, 0.42 * s), tuple(int(v * 0.8) for v in color), layer=6)


def glove_pair(sc, M):
    for sx in (-1, 1):
        G = M @ T(sx * 0.3, 0, 0) @ RZ(sx * 12)
        sc.box(G, (0.36, 0.1, 0.5), LEATHER, layer=7)
        for k in range(4):
            sc.box(G @ T(-0.13 + k * 0.087, 0.0, 0.33), (0.07, 0.08, 0.2), LEATHER, layer=7)
        sc.box(G @ T(0, 0.0, -0.3), (0.38, 0.12, 0.14), (120, 80, 50), layer=7)
        sc.box(G @ T(0.05, 0.055, 0.05) @ RZ(30), (0.2, 0.01, 0.02), (90, 60, 40), layer=7)


def shoe_sparkles(sc, a, t, color=(255, 236, 140)):
    for k in ("foot_l", "foot_r"):
        if k in a:
            ls.glow_at(sc, a[k] + np.array([0, 0.15, 0.1]), 0.35, color, 70)
            from shots import sparks
            sparks(sc, a[k] + np.array([0, 0.15, 0.1]), t, seed=3 if k == "foot_l" else 7, n=3, r=0.25, color=color)
