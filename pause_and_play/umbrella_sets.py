"""Sets and props for The Weather Umbrella: the golden umbrella, town square with a stage, cheese roofs,
puppies, the farm on the hill (dead field that turns green), moving truck and boxes, storm clouds, rain,
snow, the farm stand, a carrot and a veggie pizza."""
import math

import numpy as np

import laughs_sets as ls
import porch_sets as ps
import sets
from engine import RX, RY, RZ, T, glow, xf

GOLD, GOLD2 = (250, 196, 50), (255, 226, 120)
SOIL, DRY = (120, 84, 56), (176, 140, 96)
LEAF = (80, 170, 80)


def S(k):
    m = np.eye(4)
    m[0, 0] = m[1, 1] = m[2, 2] = k
    return m


def umbrella(sc, M, open_k=1.0, glow_k=1.0, t=0.0):
    """The Weather Umbrella, handle at M (shaft up +y). open_k 0 closed .. 1 open."""
    sc.box(M @ T(0, 0.9, 0), (0.06, 1.8, 0.06), (120, 90, 40), layer=6)
    for i in range(5):  # J handle
        a = math.radians(180 * i / 4)
        sc.box(M @ T(0.12 - 0.12 * math.cos(a), -0.12 * math.sin(a), 0), (0.08, 0.08, 0.08), (90, 60, 30), layer=6)
    n = 10
    r = 0.15 + 1.25 * open_k
    drop = 1.0 - 0.75 * open_k
    top = (0, 1.95, 0)
    ring = [(r * math.cos(2 * math.pi * i / n), 1.95 - drop, r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    for i in range(n):
        tri = [top, ring[i], ring[(i + 1) % n]]
        sc.solid(M, tri, [(0, 1, 2), (0, 2, 1)], GOLD if i % 2 else GOLD2, layer=6)
    sc.blob(M @ T(0, 2.0, 0), (0.1, 0.16, 0.1), (255, 240, 180), layer=6, lit=False, n=8, m=6)
    if glow_k > 0:
        tip = xf(M, (0, 1.6, 0))
        sc.sprite(tip, lambda d, x, y, s, col: glow(d, x, y, 1.6 * s, (255, 220, 120), int(70 * glow_k)), layer=8,
                  live=True)
        sc.light(tip + np.array([0, 0.4, 0.6]), (255, 220, 140), 60 * glow_k, 0.5)
    return xf(M, (0, 1.95, 0))


def pedestal(sc, M):
    sc.box(M @ T(0, 0.5, 0), (0.9, 1.0, 0.9), (110, 70, 140), layer=4)
    sc.box(M @ T(0, 1.02, 0), (1.0, 0.06, 1.0), GOLD, layer=4)


def square(sc, t=0.0, umbrella_on_stand=True):
    """Town square: street of houses behind, a small stage at z = -1.5 with an UMBRELLA DAY banner."""
    sets.town(sc)
    sc.box(T(0, 0.4, -1.5), (6.0, 0.8, 2.6), (170, 110, 80), layer=3)
    sc.box(T(0, 0.82, -1.5), (6.1, 0.06, 2.7), (200, 140, 100), layer=3)

    def ban(D):
        D.rect(-1, -1, 1, 1, (60, 80, 180))
        ps.fit_text(D, ["UMBRELLA DAY"], (255, 220, 80), aspect=5.0, fill_w=0.85, fill_h=0.65)
    for sx in (-1, 1):
        sc.box(T(sx * 2.8, 2.4, -2.6), (0.15, 3.2, 0.15), (240, 240, 240), layer=3)
    sc.box(T(0, 3.8, -2.6), (5.6, 1.1, 0.06), (60, 80, 180), layer=3, decal=ban)
    ls.bunting(sc, (-2.8, 4.0, -2.4), (2.8, 4.0, -2.4))
    if umbrella_on_stand:
        pedestal(sc, T(1.8, 0.85, -1.6))
        umbrella(sc, T(1.8, 1.95, -1.6), open_k=0.0, glow_k=0.8, t=t)
    return np.array([0, 0.85, -1.2])  # centre of the stage floor


def cheese_roofs(sc, t=0.0):
    for i, x in enumerate((-19.5, -13, -6.5, 0, 6.5, 13, 19.5)):
        h = 3.4 + (i % 3) * 0.45
        for k in range(6):
            dx = -2.4 + k * 0.95
            L = 0.35 + 0.35 * ((k * 7 + i) % 3) + 0.05 * math.sin(t * 2 + k)
            sc.blob(T(x + dx, h - L / 2 + 0.1, -5.4), (0.3, L, 0.25), (255, 214, 80), layer=4, n=8, m=6)
        sc.box(T(x, h + 0.25, -6.0) @ RX(37), (5.6, 0.12, 1.4), (255, 220, 100), layer=4)


def puppy(sc, M, t=0.0, fur=(200, 150, 100)):
    return ls.dog(sc, M @ S(0.6), t, fur=fur, hat=False)


PUP_FURS = [(200, 150, 100), (240, 240, 240), (120, 80, 50), (230, 190, 120), (90, 90, 96)]


def puppies(sc, n, t, area=(-6, 6, 0, 4), seed=3):
    rng = np.random.RandomState(seed)
    for i in range(n):
        x, z = rng.uniform(area[0], area[1]), rng.uniform(area[2], area[3])
        puppy(sc, T(x, 0, z) @ RY(rng.uniform(-180, 180)), t + i, PUP_FURS[i % 5])


def name_hat(sc, M, slip=None):
    sc.blob(M @ T(0, 0.35, 0), (0.6, 0.7, 0.6), (30, 30, 36), e=0.15, e2=1.0, layer=7, n=16, m=6)
    sc.blob(M @ T(0, 0.02, 0), (0.95, 0.06, 0.95), (30, 30, 36), e=0.5, e2=1.0, layer=7, n=16, m=4)
    for i in range(5):
        sc.box(M @ T(-0.15 + 0.08 * i, 0.72, 0.05 * (i % 2)) @ RZ(15 * (i - 2)), (0.12, 0.2, 0.01), (250, 250, 240),
               layer=7)


def name_slip(sc, M, name="MIA"):
    ps.note(sc, M, [name], w=0.7, h=0.4, ink=(220, 40, 60), folds=False)


# ------------------------------------------------------------------- farm
FIELD_X0, FIELD_X1 = -12.0, 6.0
FIELD_Z0, FIELD_Z1 = -2.0, -22.0
HOUSE = np.array([10.0, 0.0, 2.0])
TRUCK = np.array([5.5, 0.0, 6.0])


def truck(sc, M, doors_open=0.0, empty=False, boxes=True, snow=0.0):
    """Moving truck, nose toward +x of M."""
    sc.box(M @ T(2.0, 1.1, 0), (1.6, 1.6, 2.0), (230, 230, 236), layer=4)
    sc.box(M @ T(2.4, 1.5, 0), (0.6, 0.6, 1.9), (150, 200, 240), layer=4)

    def side(D):
        D.rect(-1, -1, 1, 1, (240, 120, 50))
        ps.fit_text(D, ["MOVING"], (255, 255, 255), aspect=3.6 / 2.2, fill_w=0.7, fill_h=0.3)
    sc.box(M @ T(-0.6, 1.5, 0), (3.6, 2.4, 2.1), (240, 120, 50), layer=4, decal=side)
    for x in (1.8, -1.6):
        for sz in (-1, 1):
            sc.blob(M @ T(x, 0.4, sz * 1.0) @ RX(90), (0.8, 0.3, 0.8), (40, 40, 46), e=0.4, e2=1.0, layer=4, n=16,
                    m=4)
    for sz in (-1, 1):
        D = M @ T(-2.4, 1.5, sz * 1.05) @ RY(sz * 100 * doors_open) @ T(0, 0, -sz * 0.52)
        sc.box(D, (0.06, 2.3, 1.02), (220, 110, 46), layer=4)
    if boxes and not empty:
        for i in range(4):
            sc.box(M @ T(-1.8 + (i % 2) * 0.7, 0.75 + (i // 2) * 0.7, 0.3 - 0.6 * (i % 2)), (0.65, 0.65, 0.65),
                   (200, 160, 110), layer=4)
    if snow > 0:
        sc.blob(M @ T(-0.6, 1.2 * snow, 0), (5.2 * snow, 3.4 * snow, 3.6 * snow), (250, 252, 255), e=0.9, layer=5,
                n=16, m=10)


def box_pile(sc, x, z, n=7, seed=1):
    rng = np.random.RandomState(seed)
    for i in range(n):
        sc.box(T(x + rng.uniform(-1.2, 1.2), 0.33 + 0.66 * (i % 3 == 2), z + rng.uniform(-0.8, 0.8)) @ RY(rng.uniform(-30, 30)),
               (0.66, 0.66, 0.66), (200, 160, 110), layer=4)


def cracked(sc, M, w=6.0, h=6.0, wet=0.0):
    def dec(D):
        base = tuple(int(DRY[i] + (SOIL[i] - DRY[i]) * wet) for i in range(3))
        D.rect(-1, -1, 1, 1, base)
        rng = np.random.RandomState(4)
        for _ in range(40):
            x, y = rng.uniform(-1, 1), rng.uniform(-1, 1)
            pts = [(x, y)]
            for _ in range(4):
                x += rng.uniform(-0.2, 0.2)
                y += rng.uniform(-0.2, 0.2)
                pts.append((x, y))
            D.line(pts, tuple(int(v * 0.45) for v in base), 0.03)
        if wet > 0:
            for _ in range(int(60 * wet)):
                D.ell(rng.uniform(-1, 1), rng.uniform(-1, 1), 0.04, 0.03, tuple(int(v * 0.7) for v in base), n=8)
    sc.box(M @ RX(-90), (w, h, 0.02), DRY, layer=1, decal=dec)


def farm(sc, t=0.0, green=0.0, sweep=None, pumpkins=0.0, house=True, truck_kw=None, boxes=True, dead_tree=True):
    """Hilltop farm. green 0 dead .. 1 lush; sweep = x up to which the field has turned (for the wipe)."""
    sc.ground((150, 140, 90))
    sets.clouds(sc, seed=9)
    rows = 12
    for r in range(rows):
        z = FIELD_Z0 - r * (FIELD_Z0 - FIELD_Z1) / rows * -1 * -1
        z = FIELD_Z0 + (FIELD_Z1 - FIELD_Z0) * r / rows
        sets.flat(sc, FIELD_X0, FIELD_X1, z - 0.6, z + 0.6, (130, 96, 64), y=0.011)
        sc.box(T((FIELD_X0 + FIELD_X1) / 2, 0.12, z), (FIELD_X1 - FIELD_X0, 0.25, 0.5),
               (110, 80, 54) if green > 0 else DRY, layer=2)
        for k in range(16):
            x = FIELD_X0 + 0.6 + k * (FIELD_X1 - FIELD_X0 - 1.2) / 15
            g = green if sweep is None else (green if x < sweep else 0.0)
            if g > 0.02:
                hgt = 0.2 + 0.7 * g
                sc.blob(T(x, 0.25 + hgt / 2, z), (0.5 * g + 0.2, hgt, 0.5 * g + 0.2), LEAF, layer=3, n=8, m=6)
            else:
                sc.box(T(x, 0.35, z) @ RZ(30 + 20 * ((k + r) % 3)), (0.04, 0.3, 0.04), (150, 120, 80), layer=3)
    if pumpkins > 0:
        for i, (x, z, s) in enumerate(((-6, -5, 1.0), (-2, -9, 0.8), (2, -4, 1.3), (-9, -13, 0.9), (4, -15, 1.1))):
            k = pumpkins * s
            sc.blob(T(x, 0.25 + 0.9 * k, z), (2.6 * k, 1.9 * k, 2.4 * k), (240, 140, 40), e=0.8, layer=4, n=16, m=10)
            sc.box(T(x, 0.3 + 1.85 * k, z), (0.2 * k, 0.4 * k, 0.2 * k), (90, 120, 60), layer=4)
    if house:
        ps.porch_house(sc, HOUSE[0], HOUSE[2], (200, 70, 60), k=0.0, lamp_k=0.0, yaw=-70, glass=ls.DAY_GLASS)
    if dead_tree:
        sc.box(T(-14, 2.0, -3), (0.4, 4.0, 0.4), (110, 80, 60), layer=2)
        for a in (-40, 30, 70):
            sc.box(T(-14, 3.6, -3) @ RZ(a) @ T(0, 0.7, 0), (0.15, 1.4, 0.15), (110, 80, 60), layer=2)
    if truck_kw is not None:
        truck(sc, T(*TRUCK) @ RY(truck_kw.pop("yaw", 160)) if "x" not in truck_kw else
              T(truck_kw.pop("x"), 0, TRUCK[2]) @ RY(truck_kw.pop("yaw", 160)), **truck_kw)
    if boxes:
        box_pile(sc, TRUCK[0] + 2.8, TRUCK[2] - 2.6)


def hill(sc, green=0.0):
    """The farm seen from town: a big hill with a tiny farmhouse on top."""
    c = tuple(int(DRY[i] + (LEAF[i] - DRY[i]) * green) for i in range(3))
    sc.blob(T(0, -6, -60), (90, 30, 50), c, e=0.9, layer=1, n=24, m=12)
    ps.porch_house(sc, 6, -52, (200, 70, 60), k=0, lamp_k=0, glass=ls.DAY_GLASS)


def storm(sc, k=1.0, t=0.0, y=16.0):
    for i in range(14):
        a = i * 0.9
        sc.blob(T(-30 + i * 5 + 3 * math.sin(t * 0.6 + a), y + 2 * math.sin(a * 1.3), -10 - 12 * (i % 3)),
                (9 * k, 4 * k, 7 * k), (70, 74, 90), layer=1, n=12, m=8)


def rain(sc, t, k=1.0, n=160, seed=2, color=(180, 210, 255)):
    rng = np.random.RandomState(seed)
    pts = [(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0.8, 1.4)) for _ in range(n)]

    def fn(d, W, H):
        for x0, y0, sp in pts:
            y = ((y0 + t * sp * 1.6) % 1.0) * H
            x = (x0 + 0.05 * ((y0 + t * sp * 1.6) % 1.0)) * W
            d.line([(x, y), (x - 0.008 * W, y + 0.05 * H)], fill=color + (int(200 * k),), width=max(2, W // 400))
    sc.overlay(fn)


def snow(sc, t, k=1.0, n=140, seed=3):
    rng = np.random.RandomState(seed)
    pts = [(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0.15, 0.3), rng.uniform(0.004, 0.009)) for _ in range(n)]

    def fn(d, W, H):
        for x0, y0, sp, r in pts:
            y = ((y0 + t * sp) % 1.0) * H
            x = (x0 + 0.02 * math.sin(t * 2 + y0 * 9)) * W
            rr = r * W
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 255, int(230 * k)))
    sc.overlay(fn)


def falling(sc, t, kind="pizza", n=24, seed=5):
    """Pizza slices or puppies (little drawn ones) tumbling down the frame."""
    rng = np.random.RandomState(seed)
    pts = [(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0.25, 0.45), rng.uniform(0, 6)) for _ in range(n)]

    def fn(d, W, H):
        for x0, y0, sp, ph in pts:
            y = ((y0 + t * sp) % 1.1 - 0.05) * H
            x = x0 * W
            s = W * 0.05
            a = t * 3 + ph
            if kind == "pizza":
                p = [(x + s * math.cos(a), y + s * math.sin(a)), (x + s * math.cos(a + 2.4), y + s * math.sin(a + 2.4)),
                     (x + s * math.cos(a - 2.4), y + s * math.sin(a - 2.4))]
                d.polygon(p, fill=(250, 200, 90, 255), outline=(200, 140, 70, 255), width=max(2, int(s * 0.12)))
                d.ellipse([x - s * 0.18, y - s * 0.18, x + s * 0.18, y + s * 0.18], fill=(210, 60, 50, 255))
            else:
                c = [(200, 150, 100), (240, 240, 240), (120, 80, 50)][int(ph) % 3]
                d.rounded_rectangle([x - s * 0.6, y - s * 0.4, x + s * 0.6, y + s * 0.4], int(s * 0.2), fill=c + (255,))
                d.ellipse([x - s * 0.25, y - s * 0.75, x + s * 0.55, y + s * 0.05], fill=c + (255,))
                d.ellipse([x + s * 0.05, y - s * 0.5, x + s * 0.17, y - s * 0.38], fill=(40, 28, 48, 255))
    sc.overlay(fn)


def dreamy(sc):
    def fn(d, W, H):
        for i in range(12, 0, -1):
            d.rectangle([0, 0, W, H], outline=(255, 255, 255, 16), width=int(W * 0.012 * i))
    sc.overlay(fn)


def dark_grade(sc, k):
    def fn(d, W, H):
        d.rectangle([0, 0, W, H], fill=(20, 24, 40, int(90 * k)))
    sc.overlay(fn)


def farm_stand(sc, t=0.0):
    sets.town(sc)
    ls.stall(sc, 0, -1.2, (90, 170, 90), sign="FRESH FARM")
    rng = np.random.RandomState(4)
    cols = [(240, 140, 40), (90, 170, 80), (220, 60, 50), (250, 200, 60), (160, 90, 180)]
    for i in range(6):
        x = -1.0 + (i % 3) * 1.0
        z = -1.0 + 0.5 * (i // 3)
        sc.box(T(x, 1.32, z), (0.8, 0.22, 0.45), (170, 120, 80), layer=4)
        for k in range(5):
            sc.blob(T(x + rng.uniform(-0.3, 0.3), 1.5, z + rng.uniform(-0.15, 0.15)), (0.22, 0.22, 0.22), cols[i % 5],
                    layer=4, n=8, m=6)


def carrot(sc, M):
    v = [(0, -0.6, 0)] + [(0.1 * math.cos(a), 0.0, 0.1 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
    sc.solid(M, v, [(0, (i + 1) % 8 + 1, i + 1) for i in range(8)] + [tuple(range(8, 0, -1))], (250, 140, 40), layer=7)
    for a in (-20, 0, 20):
        sc.box(M @ RZ(a) @ T(0, 0.2, 0), (0.04, 0.4, 0.04), (90, 170, 70), layer=7)


def veggie_pizza(sc, M):
    sc.blob(M, (1.2, 0.08, 1.2), (230, 180, 90), e=0.5, e2=1.0, layer=7, n=20, m=4)
    sc.blob(M @ T(0, 0.04, 0), (1.05, 0.04, 1.05), (220, 90, 60), e=0.5, e2=1.0, layer=7, n=20, m=4)
    rng = np.random.RandomState(1)
    for i in range(14):
        a, r = rng.uniform(0, 2 * math.pi), rng.uniform(0, 0.45)
        c = [(90, 170, 80), (250, 200, 60), (240, 140, 40), (160, 90, 180)][i % 4]
        sc.blob(M @ T(r * math.cos(a), 0.08, r * math.sin(a)), (0.13, 0.05, 0.13), c, layer=7, n=8, m=4)
