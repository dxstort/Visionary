"""Shot list. Each shot: (number, seconds, narration, fn(t, dur) -> Scene)."""
import math

import numpy as np

import sets
from cast import BABY, BRAX, DAD, HERO, NURSE, PIP, TUCK, character, sit
from engine import RX, RY, RZ, Scene, T, add_emote, clamp, ease, glow, lerp, pop, speed_lines, star_pts

# Placeholder cast names used in captions; swap here once final names are confirmed.
NAMES = {"Tuck": "Tuck", "Brax": "Brax", "Pip": "Pip", "Bigsby": "Bigsby"}

SKY = ((95, 175, 255), (205, 235, 255))
INDOOR = ((170, 235, 215), (170, 235, 215))


def cam(pos, tgt, u, push=0.1, fov=38, w=None, **kw):
    """Default camera: slow push-in of `push` (fraction of the distance) across the shot.
    `w` = world width visible at the target at the start of the shot (sets the distance along pos->tgt)."""
    pos, tgt = np.asarray(pos, float), np.asarray(tgt, float)
    if w:
        dirn = (pos - tgt) / np.linalg.norm(pos - tgt)
        pos = tgt + dirn * w / (2 * math.tan(math.radians(fov) / 2) * 9 / 16)
    p = pos + (tgt - pos) * push * u
    return Scene(p, tgt, fov=fov, **kw)


def key(t, dur=0.2):
    """0 -> 1 key-pose pop with overshoot over `dur` seconds, then hold."""
    return pop(t / dur) if t < dur else 1.0


def sparks(sc, pos, t, seed=0, n=5, r=0.35, color=(255, 235, 90)):
    rng = np.random.RandomState(seed + int(t * 15))
    for i in range(n):
        off = rng.uniform(-r, r, 3)
        k = rng.uniform(0.05, 0.13)

        def fn(d, x, y, s, col, k=k):
            d.polygon(star_pts(x, y, k * s, n=4, inner=0.3, rot=rng.uniform(0, 90)), fill=col(color))

        sc.sprite(np.asarray(pos) + off, fn, layer=7, live=True)
    sc.sprite(pos, lambda d, x, y, s, col: glow(d, x, y, r * 1.1 * s, color, 45), layer=7)


def laser(sc, a, b, t):
    w = 0.1 + 0.03 * math.sin(t * 60)
    sc.line3(a, b, (255, 60, 60, 110), width=w * 3.2, layer=7)
    sc.line3(a, b, (255, 70, 70), width=w * 1.5, layer=7)
    sc.line3(a, b, (255, 235, 235), width=w * 0.5, layer=7)


# ------------------------------------------------------------------ shots 1-9
def s01(t, dur):
    u = t / dur
    sc = cam((0.5, 1.95, 3.3), (0, 1.5, 0), u, 0.14, fov=30, w=2.2, sky=INDOOR)
    sets.nursery(sc)
    sets.crib(sc, T(0, 0, 0))
    wig = math.sin(t * 16) * 8
    a = character(sc, BABY, (0, 1.0, 0.05), face="sparkle",
                  pose=dict(ll=80, lr=80, y=-0.17, al=(150 + wig, -25), ar=(150 - wig, -25), head=(0, -6, wig * 0.4)),
                  shadow=False)
    for i, h in enumerate(("hand_l", "hand_r")):
        sparks(sc, a[h] + np.array([0, 0.08, 0.1]), t, seed=i * 7, r=0.22)
    return sc


def s02(t, dur):
    u = t / dur
    sc = cam((0.4, 0.95, 8.6), (0, 2.0, 0), u, 0.1, fov=44, w=5.4, sky=INDOOR)
    sets.nursery(sc)
    # left: floating baby
    sets.crib(sc, T(-1.75, 0, -0.6))
    sets.crib_front(sc, T(-1.75, 0, -0.6), layer=4)
    fy = 3.1 + 0.25 * math.sin(t * 5)
    character(sc, BABY, (-1.7, fy, -0.4), face="laugh", shadow_y=0,
              pose=dict(lean=-18, roll=10 * math.sin(t * 4), al=(60, 60), ar=(60, 60), ll=40, lr=-10))
    # middle: laser eyes
    sets.crib(sc, T(0.1, 0, -0.2))
    b = character(sc, BABY, (0.1, 1.0, -0.2), yaw=30 + 18 * math.sin(t * 6), face="grit", shadow=False,
                  pose=dict(al=(40, 30), ar=(40, 30)))
    sets.crib_front(sc, T(0.1, 0, -0.2))
    fwd = b["Mh"][:3, 2]
    laser(sc, b["face_pt"], b["face_pt"] + fwd * 14 + np.array([0, 5.0, 0]), t)
    sc.sprite(b["face_pt"], lambda d, x, y, s, col: glow(d, x, y, 0.3 * s, (255, 80, 80), 130), layer=8)
    # right: baby lifting its crib
    k = key(t, 0.25)
    lift = 0.35 + 0.5 * k + 0.04 * math.sin(t * 20)
    c = character(sc, BABY, (1.7, 0, 0.1), face="effort", pose=dict(al=(180, -8), ar=(180, -8)), layer=7)
    M = T(1.7, lift - 0.62, 0.1) @ RZ(5 * math.sin(t * 9))
    sets.crib(sc, M, layer=6)
    sets.crib_front(sc, M, layer=6)
    return sc


def s03(t, dur):
    u = t / dur
    sc = cam((0.4, 2.2, 4.6), (0, 2.1, 0), u, 0.08, fov=30, w=3.6, sky=INDOOR)
    sets.nursery(sc)
    k = key(t, 0.16)
    n = character(sc, NURSE, (0, -0.75 * k, 0), face="shock", shadow=False,
                  pose=dict(lean=14 * k, al=(165 * k, 18), ar=(165 * k, 18), head=(0, 8 * k, -6 * k)))
    sc.box(T(0, 0.55, 1.0), (3.2, 1.1, 0.9), (245, 245, 250), layer=6)
    sc.box(T(0, 1.13, 1.0), (3.4, 0.08, 1.0), (120, 200, 215), layer=6, bias=-0.2)
    for i, c in enumerate(((255, 180, 200), (255, 230, 120), (160, 220, 255))):
        sc.box(T(-1.0 + i * 0.45, 1.33, 1.0), (0.24, 0.32, 0.24), c, layer=6, bias=-0.4)
    y = 3.5
    laser(sc, (-9, y - 0.25, 0.3), (9, y + 0.35, 0.3), t)
    add_emote(sc, "!", n["head_top"], t, size=0.75, dx=0.95, dy=0.25)
    return sc


def s04(t, dur):
    u = t / dur
    sc = cam((1.4, 1.2, 8.0), (0, 4.6, 0), u, 0.12, fov=44, w=4.6, sky=SKY)
    sets.town(sc)
    y = 3.1 + 0.18 * math.sin(t * 6)
    character(sc, TUCK, (0, y, 0), yaw=-12, face="grin", shadow_y=0,
              pose=dict(lean=30, roll=-6, ar=(165, -14), al=(10, 38), ll=-25, lr=-50, cape=40 + 14 * math.sin(t * 22),
                        head=(0, 4, 0)))
    speed_lines(sc, t, cx=0.5, cy=0.33, n=24, inner=0.3, alpha=150)
    return sc


def s05(t, dur):
    u = t / dur
    sc = cam((-1.4, 1.3, 8.6), (0, 2.6, 0), u, 0.12, fov=38, w=4.8, sky=SKY)
    sets.park(sc)
    k = key(t, 0.22)
    arm = lerp(95, 180, k)
    wob = 2.5 * math.sin(t * 13)
    b = character(sc, BRAX, (0, 0, 0), face="grit" if t < 0.55 else "grin",
                  pose=dict(al=(arm, -10), ar=(arm, -10), ll=-8, lr=8, roll=wob * 0.3))
    mid = (b["hand_l"] + b["hand_r"]) / 2
    sets.bench(sc, T(mid[0], mid[1] - 0.75 + 0.42 * clamp(k), mid[2]) @ RZ(wob) @ RY(8), layer=6)
    return sc


def _dad_bench(sc, t, face, pig_head=False):
    sets.park(sc)
    sets.bench(sc, T(0, 0, -0.1), layer=4)
    hy = 18 * math.sin(t * 3.2)
    d = character(sc, DAD, (0, -0.52, 0.12), face=face,
                  pose=dict(ll=88, lr=88, al=(18, 4), ar=(18, 4), head=(0 if pig_head else hy, 6, 0), lean=-3),
                  shadow=False)
    rng = np.random.RandomState(4)
    for i in range(11):
        a = math.radians(-100 + i * 20 + rng.uniform(-5, 5))
        r = 2.3 + rng.uniform(-0.25, 0.5)
        x, z = r * math.sin(a), 1.3 + r * math.cos(a) * 0.62
        bob = max(0.0, math.sin(t * 9 + i * 1.7))
        sets.pigeon(sc, (x, 0.02, z), yaw=math.degrees(math.atan2(-x, 0.2 - z)), bob=bob, layer=6 if z > 0.6 else 4,
                    s=1.25)
    for x in (-1.15, 1.2):
        sets.pigeon(sc, (x, 1.66, -0.5), yaw=-70 * np.sign(x), bob=max(0.0, math.sin(t * 8 + x)), layer=4, s=1.2)
    return d


def s06(t, dur):
    u = t / dur
    sc = cam((1.8, 2.6, 8.8), (0, 1.9, 0.3), u, 0.12, fov=36, w=5.6, sky=SKY)
    _dad_bench(sc, t, "worried")
    return sc


def s07(t, dur):
    u = t / dur
    sc = cam((0.5, 3.2, 4.3), (0, 3.15, 0.2), u, 0.07, fov=30, w=2.7, sky=SKY)
    d = _dad_bench(sc, t, "miserable", pig_head=True)
    top = d["Mh"] @ T(0, DAD["head"][1] * DAD["s"] / 2 + 0.12, 0)
    sets.pigeon(sc, top[:3, 3], yaw=20, bob=max(0.0, math.sin(t * 11)), layer=6, s=1.5, wing=20 * max(0, math.sin(t * 11)))
    add_emote(sc, "anger", d["head_top"], t, size=0.55, dx=0.85, dy=-0.15)
    return sc


def _pip_yard(sc):
    sets.town(sc, shift=1.6)


def s08(t, dur):
    u = t / dur
    sc = cam((0.7, 1.15, 5.4), (0, 0.95, 0), u, 0.12, fov=32, w=2.9, sky=SKY)
    _pip_yard(sc)
    sway = math.sin(t * 3.5)
    p = character(sc, PIP, (0, 0, 0), yaw=sway * 5, face="smile",
                  pose=dict(roll=sway * 3, ar=(72, 30), al=(0, 8), head=(0, 0, sway * 5)))
    hp = p["hand_r"]
    sets.cookie(sc, T(hp[0], hp[1] + 0.14, hp[2] + 0.1) @ RY(sway * 5) @ RZ(8), s=0.85, layer=6)
    return sc


def s09(t, dur):
    u = t / dur
    sc = cam((0.35, 1.3, 3.6), (0, 1.15, 0), u, 0.08, fov=30, w=2.2, sky=SKY)
    _pip_yard(sc)
    k = key(t - 0.15, 0.2) if t > 0.15 else 0.0
    p = character(sc, PIP, (0, 0, 0), face="smile",
                  pose=dict(y=0.05 * k, al=(25 * k, 6 + 62 * k), ar=(25 * k, 6 + 62 * k), head=(0, 0, 9 * k)))
    add_emote(sc, "?", p["head_top"], t, size=0.55, dx=0.6, dy=0.3, start=0.25)
    return sc


def N(s):
    for k, v in NAMES.items():
        s = s.replace(k, v)
    return s


SHOTS = [
    (1, 0.9, "In this town,", s01),
    (2, 1.8, "every kid gets a random superpower", s02),
    (3, 0.7, "at BIRTH.", s03),
    (4, 0.9, N("Tuck got flying."), s04),
    (5, 1.2, N("Brax got super strength."), s05),
    (6, 1.5, "Dad got talking to PIGEONS.", s06),
    (7, 1.2, "They never stop complaining.", s07),
    (8, 1.8, N("My little sister Pip is 4."), s08),
    (9, 1.5, "Hers hasn't shown up yet.", s09),
]
