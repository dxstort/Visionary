"""Sets and props for When Secrets Make Statues Dance: stone statues (people, a lion, an owl, a horse, a frog)
that stand still until a real secret is told, the town square with its clock tower, a talent-show stage,
a kitchen with a flour jar, a shower, juggling balls, a teddy bear, a microphone and sparkle dust."""
import math

import numpy as np

import sets
from cast import _spec, character
from engine import RX, RY, RZ, T, clamp
from shots import sparks

STONE = (176, 176, 186)
STONE_D = (142, 142, 154)
STONE_L = (206, 206, 214)
MOSS = (110, 150, 100)
BALLS = [(240, 80, 80), (250, 200, 60), (80, 190, 120), (90, 150, 250), (200, 110, 240)]


# ------------------------------------------------------------------ stone people
def stone_spec(style="short", s=1.3, hat=None):
    d = _spec(name="Statue", style=style, s=s, skin=STONE, shirt=STONE_L, pants=STONE_D, shoes=STONE_D, hair=STONE_D,
              accent=STONE_D, sleeve=0.7)
    if hat:
        d["hat"] = STONE_D
    return d


FOUNTAIN_LADY = stone_spec("bun", 1.3)
BANDLEADER = stone_spec("tophat", 1.3)
MOON_STATUE = stone_spec("bob", 1.4)
HERO_STATUE = stone_spec("short", 1.45)


def dance_pose(t, k=1.0, kind=0):
    """Stone boogie: arms pumping, hips rolling, knees bouncing. k = 0 still, 1 full dance."""
    w = math.sin(t * 9 + kind)
    v = math.sin(t * 9 + kind + 1.6)
    if kind % 3 == 0:
        p = dict(al=(130 + 40 * w * k, 10), ar=(130 - 40 * w * k, 10), roll=9 * w * k, y=0.1 * abs(v) * k,
                 head=(14 * w * k, 0, 0))
    elif kind % 3 == 1:
        p = dict(al=(80 * abs(w) * k, 20), ar=(150 * abs(v) * k, 20), ll=18 * w * k, lr=-18 * w * k, roll=-8 * w * k,
                 y=0.08 * abs(v) * k)
    else:
        p = dict(al=(170 * k, 10 * w), ar=(170 * k, -10 * w), lean=8 * w * k, y=0.12 * abs(w) * k, head=(0, 0, 10 * v * k))
    return p


def pedestal(sc, x, z, h=0.9, w=1.5, d=1.5):
    sc.box(T(x, h / 2, z), (w, h, d), STONE_L, layer=3)
    sc.box(T(x, h + 0.06, z), (w + 0.2, 0.12, d + 0.2), STONE, layer=3)
    sc.box(T(x, 0.1, z), (w + 0.25, 0.2, d + 0.25), STONE_D, layer=3)


def statue(sc, spec, x, z, t=0.0, k=0.0, kind=0, yaw=0, face="neutral", h=0.9, ped=True, extra=None):
    """A stone person on a pedestal; k > 0 makes it dance."""
    if ped:
        pedestal(sc, x, z, h)
    p = dance_pose(t, k, kind) if k > 0 else dict(al=(8, 5), ar=(8, 5))
    p.update(extra or {})
    a = character(sc, spec, (x, h + 0.12, z), yaw=yaw, face=face if k == 0 else "grin", pose=p, shadow=False)
    if k > 0:
        sparks(sc, a["head_top"] + np.array([0.0, 0.2, 0.0]), t, seed=kind + 3, n=3, r=0.5, color=(255, 240, 180))
    return a


# ------------------------------------------------------------------ stone animals
def _b(sc, M, size, c=STONE, **kw):
    sc.blob(M, size, c, layer=kw.pop("layer", 5), n=12, m=8, **kw)


def lion(sc, M, t=0.0, k=0.0):
    """Stone lion, facing +x. M = body-centre matrix (hips height ~0.9)."""
    w = math.sin(t * 9)
    _b(sc, M @ T(0, 0, 0), (1.6, 0.8, 0.8))
    _b(sc, M @ T(0.95, 0.3, 0), (0.9, 0.9, 0.9), STONE_D)
    _b(sc, M @ T(1.05, 0.3, 0), (0.62, 0.62, 0.62), STONE_L)
    sc.blob(M @ T(1.4, 0.2, 0), (0.28, 0.2, 0.3), STONE, layer=5, n=8, m=6)
    for sz in (-1, 1):
        sc.blob(M @ T(1.3, 0.55, sz * 0.2), (0.12, 0.12, 0.12), (40, 40, 50), layer=5, n=6, m=4, lit=False)
        sc.blob(M @ T(1.05, 0.75, sz * 0.3), (0.2, 0.2, 0.12), STONE, layer=5, n=6, m=4)
    for i, (lx, lz) in enumerate(((0.55, 0.28), (0.55, -0.28), (-0.55, 0.28), (-0.55, -0.28))):
        sc.box(M @ T(lx, -0.5, lz) @ RZ(18 * w * k * (1 if i % 2 else -1)), (0.24, 0.7, 0.24), STONE_D, layer=5)
    sc.box(M @ T(-1.0, 0.1, 0) @ RZ(60 + 30 * w * k), (0.1, 0.8, 0.1), STONE_D, layer=5)


def owl(sc, M, t=0.0, flap=0.0):
    """Stone owl, facing +z. flap 0..1 spreads and beats the wings."""
    w = math.sin(t * 16) * flap
    _b(sc, M @ T(0, 0.9, 0), (1.2, 1.7, 1.0))
    _b(sc, M @ T(0, 1.95, 0.05), (1.2, 0.9, 0.9), STONE_L)
    for sx in (-1, 1):
        sc.blob(M @ T(sx * 0.3, 2.0, 0.5), (0.34, 0.34, 0.2), (250, 250, 250), layer=5, n=10, m=6)
        sc.blob(M @ T(sx * 0.3, 2.0, 0.62), (0.15, 0.15, 0.1), (30, 30, 40), layer=6, n=8, m=5, lit=False)
        sc.box(M @ T(sx * 0.46, 2.55, 0.0) @ RZ(-sx * 20), (0.16, 0.34, 0.16), STONE_D, layer=5)
        ang = sx * (20 + 55 * flap + 30 * w)
        sc.box(M @ T(sx * 0.62, 1.2, -0.05) @ RZ(-ang) @ T(sx * 0.35, 0.0, 0), (0.7, 1.2, 0.14), STONE_D, layer=5)
    sc.blob(M @ T(0, 1.85, 0.55), (0.18, 0.2, 0.2), (220, 170, 90), layer=6, n=8, m=6)
    sc.box(M @ T(0, 0.1, 0), (1.1, 0.12, 0.6), STONE_D, layer=4)


def horse(sc, M, t=0.0, k=0.0):
    """Stone horse, facing +x."""
    w = math.sin(t * 10)
    _b(sc, M @ T(0, 0, 0), (2.0, 0.95, 0.8))
    sc.box(M @ T(1.0, 0.7, 0) @ RZ(-35), (0.5, 1.2, 0.45), STONE, layer=5)
    _b(sc, M @ T(1.5, 1.35, 0) @ RZ(-25), (0.95, 0.5, 0.45), STONE_L)
    sc.blob(M @ T(1.95, 1.2, 0), (0.28, 0.3, 0.3), STONE, layer=5, n=8, m=6)
    for sz in (-1, 1):
        sc.box(M @ T(1.2, 1.7, sz * 0.12), (0.12, 0.3, 0.1), STONE_D, layer=5)
    sc.box(M @ T(1.0, 0.75, 0) @ RZ(-35) @ T(-0.18, 0.1, 0), (0.1, 1.2, 0.2), STONE_D, layer=5)
    for i, (lx, lz) in enumerate(((0.75, 0.25), (0.75, -0.25), (-0.75, 0.25), (-0.75, -0.25))):
        ph = w * k * (1 if i % 2 else -1)
        sc.box(M @ T(lx, -0.45, lz) @ RZ(28 * ph), (0.2, 0.95, 0.2), STONE_D, layer=5)
    _b(sc, M @ T(-1.1, 0.1, 0) @ RZ(-30), (0.25, 0.9, 0.3), STONE_D)


def frog(sc, M, hop=0.0):
    _b(sc, M @ T(0, 0.2, 0), (0.7, 0.45, 0.6))
    for sz in (-1, 1):
        _b(sc, M @ T(0.25, 0.5, sz * 0.18), (0.2, 0.2, 0.2), STONE_L)
        sc.blob(M @ T(0.34, 0.52, sz * 0.18), (0.08, 0.08, 0.08), (30, 30, 40), layer=6, n=6, m=4, lit=False)
        sc.box(M @ T(-0.25, 0.1, sz * 0.38) @ RZ(20 * hop), (0.4, 0.14, 0.14), STONE_D, layer=5)
    sc.box(M @ T(0.4, 0.2, 0), (0.12, 0.04, 0.4), STONE_D, layer=6)


def fountain(sc, t=0.0, x=-8.0, z=-1.0, k=0.0, splash=0.0):
    """Round fountain with the fountain lady on top; water jets arc into the basin."""
    sc.box(T(x, 0.35, z), (4.2, 0.7, 4.2), STONE, layer=3)
    sc.box(T(x, 0.72, z), (3.6, 0.1, 3.6), (110, 190, 240), layer=3)
    sc.box(T(x, 1.2, z), (0.7, 1.2, 0.7), STONE_L, layer=3)
    rng = np.random.RandomState(4)
    for i in range(14):
        a = i / 14 * 6.283
        r = 0.4 + ((t * 1.5 + i * 0.13) % 1.0) * 1.3
        yy = 1.9 + 1.4 * math.sin(((t * 1.5 + i * 0.13) % 1.0) * math.pi) - 0.0
        sc.blob(T(x + r * math.cos(a), yy, z + r * math.sin(a)), (0.1, 0.1, 0.1), (200, 232, 255), layer=5, n=6, m=4,
                lit=False)
    return statue(sc, FOUNTAIN_LADY, x, z, t, k, kind=0, yaw=0, h=1.6, ped=False, face="smile")


def clock_tower(sc, x=12.0, z=-5.0, owl_flap=None, t=0.0, hour=7, minute=58):
    sc.box(T(x, 4.0, z), (2.6, 8.0, 2.6), (196, 150, 120), layer=2)
    sc.box(T(x, 8.3, z), (3.0, 0.6, 3.0), (130, 90, 80), layer=2)
    sc.box(T(x, 9.6, z), (1.8, 2.0, 1.8), (150, 110, 90), layer=2)
    sc.box(T(x, 3.0, z + 1.32), (2.0, 2.0, 0.08), (40, 34, 50), layer=3, decal=sets.clock_face(hour, minute))
    sc.box(T(x, 11.4, z) @ RZ(0), (2.2, 0.3, 2.2), (120, 80, 70), layer=2)
    if owl_flap is not None:
        owl(sc, T(x, 11.55, z) @ RY(0), t, owl_flap)


# ------------------------------------------------------------------ squares and stages
def square(sc, t=0.0, k=0.0, owl_flap=None, statues=True, fountain_on=True):
    """Town street with a fountain and a clock tower; k dances the fountain lady."""
    sets.town(sc)
    clock_tower(sc, 12.0, -5.0, owl_flap, t)
    if fountain_on:
        fountain(sc, t, -8.0, -1.0, k)


def banner_tal(D):
    D.rect(-1, -1, 1, 1, (40, 34, 120))
    D.text(0, 0.05, "TALENT SHOW", (255, 230, 90), h=0.45)


def stage(sc, t=0.0, crowd=True, faces=None, standing=False, statues_k=0.0, statues=True):
    """Talent-show stage; audience faces the stage; stone statues flank the plaza."""
    sets.stage(sc)
    sc.box(T(0, 5.4, sets.STAGE_Z - 2.0), (9.0, 1.5, 0.1), (40, 34, 120), layer=2, bias=-0.3, decal=banner_tal)
    if crowd:
        sets.audience(sc, t, faces=faces, standing=standing, rows=3, per_row=7, seed=2)
    if statues:
        statue(sc, HERO_STATUE, -9.5, 2.0, t, statues_k, kind=1, yaw=40)
        statue(sc, BANDLEADER, 9.5, 2.0, t, statues_k, kind=2, yaw=-40)
        horse(sc, T(-11.5, 1.6, -3.0), t, statues_k) if statues_k > 0 else horse(sc, T(-11.5, 1.6, -3.0), t, 0)


# ------------------------------------------------------------------ small props
def teddy(sc, M, s=1.0):
    br = (170, 110, 70)
    sc.blob(M @ T(0, 0.3 * s, 0), (0.5 * s, 0.6 * s, 0.4 * s), br, layer=6, n=10, m=7)
    sc.blob(M @ T(0, 0.8 * s, 0), (0.46 * s, 0.42 * s, 0.4 * s), br, layer=6, n=10, m=7)
    for sx in (-1, 1):
        sc.blob(M @ T(sx * 0.22 * s, 1.02 * s, 0), (0.18 * s, 0.18 * s, 0.14 * s), br, layer=6, n=8, m=5)
        sc.blob(M @ T(sx * 0.1 * s, 0.84 * s, 0.2 * s), (0.07 * s, 0.07 * s, 0.05 * s), (30, 30, 40), layer=7, n=6, m=4,
                lit=False)
    sc.blob(M @ T(0, 0.74 * s, 0.2 * s), (0.18 * s, 0.14 * s, 0.1 * s), (230, 190, 150), layer=7, n=8, m=5)


def flour_jar(sc, M, s=1.0, open_k=0.0):
    sc.box(M @ T(0, 0.5 * s, 0), (0.8 * s, 1.0 * s, 0.8 * s), (230, 240, 248), layer=5)
    sc.box(M @ T(0, 0.45 * s, 0.01), (0.7 * s, 0.8 * s, 0.7 * s), (252, 252, 248), layer=5)
    sc.box(M @ T(0, 1.05 * s + 0.4 * open_k * s, -0.2 * open_k * s) @ RX(-30 * open_k), (0.86 * s, 0.14 * s, 0.86 * s),
           (200, 120, 90), layer=6)
    sc.box(M @ T(0, 0.55 * s, 0.4 * s), (0.5 * s, 0.3 * s, 0.02), (250, 200, 80), layer=6,
           decal=lambda D: D.text(0, 0, "FLOUR", (80, 50, 30), h=0.7))


def choc_bar(sc, M, s=1.0):
    sc.box(M, (0.5 * s, 0.1 * s, 0.9 * s), (96, 58, 40), layer=7)
    sc.box(M @ T(0, 0.06 * s, 0), (0.46 * s, 0.03 * s, 0.4 * s), (230, 70, 80), layer=7)


def ball(sc, p, i=0, r=0.22):
    sc.blob(T(*p), (r, r, r), BALLS[i % 5], layer=7, n=10, m=6)


def mic(sc, M, s=1.0):
    sc.box(M @ T(0, -0.15 * s, 0), (0.08 * s, 0.36 * s, 0.08 * s), (50, 50, 60), layer=7)
    sc.blob(M @ T(0, 0.12 * s, 0), (0.2 * s, 0.22 * s, 0.2 * s), (180, 180, 190), layer=7, n=10, m=7)


def shower(sc, t=0.0, water=True):
    """Tiled shower stall seen from the front; back wall at z=-3."""
    sc.ground((226, 236, 240))

    def tiles(D):
        D.rect(-1, -1, 1, 1, (200, 230, 240))
        for k in range(-10, 11):
            D.line([(k / 10, -1), (k / 10, 1)], (170, 205, 218), 0.004)
            D.line([(-1, k / 10), (1, k / 10)], (170, 205, 218), 0.004)

    sets.wall(sc, 0, 3.0, -3.0, 9, 6, (200, 230, 240), decal=tiles)
    for sx in (-1, 1):
        sets.wall(sc, sx * 4.0, 3.0, -0.5, 6, 6, (190, 222, 236), yaw=90)
    sc.box(T(0, 5.0, -2.6), (0.7, 0.18, 0.5), (190, 190, 200), layer=3)
    sc.box(T(0, 5.4, -2.9), (0.1, 0.7, 0.1), (190, 190, 200), layer=3)
    if water:
        rng = np.random.RandomState(8)
        for i in range(36):
            x = rng.uniform(-0.9, 0.9)
            yy = 5.0 - ((t * 3.0 + rng.uniform(0, 1)) % 1.0) * 4.6
            sc.blob(T(x, yy, -2.5 + rng.uniform(-0.2, 0.3)), (0.04, 0.12, 0.04), (170, 215, 255), layer=6, n=6, m=4,
                    lit=False)


def bubbles(sc, origin, t, n=8):
    rng = np.random.RandomState(3)
    for i in range(n):
        ph = (t * 0.6 + rng.uniform(0, 1)) % 1.0
        sc.blob(T(origin[0] + rng.uniform(-0.8, 0.8), origin[1] + ph * 2.0, origin[2] + rng.uniform(-0.4, 0.4)),
                (0.14, 0.14, 0.14), (230, 245, 255), layer=7, n=8, m=5, lit=False)


def dust(sc, t, n=30, seed=2, area=(-8, 8, 1, 8, -3, 6)):
    """Secret-sparkle dust drifting down over the square."""
    rng = np.random.RandomState(seed)
    for i in range(n):
        x = rng.uniform(area[0], area[1])
        z = rng.uniform(area[4], area[5])
        yy = area[3] - ((t * 0.8 + rng.uniform(0, 1)) % 1.0) * (area[3] - area[2])
        c = [(255, 236, 140), (255, 160, 220), (160, 220, 255)][i % 3]
        sc.blob(T(x, yy, z), (0.09, 0.09, 0.09), c, layer=7, n=6, m=4, lit=False)


def moon(sc, M, glow=1.0):
    sc.blob(M, (1.4, 1.4, 1.4), (250, 244, 200), layer=5, n=14, m=9, lit=False)
    sc.blob(M @ T(0.5, 0.3, 0.2), (0.9, 0.9, 0.9), (252, 248, 222), layer=5, n=12, m=8, lit=False)


def trophy_owl(sc, M, s=1.0):
    sets.trophy(sc, M, s)


