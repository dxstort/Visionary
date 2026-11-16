"""Shot list. Each shot: (number, seconds, narration, fn(t, dur) -> Scene)."""
import math
import os

import numpy as np

import sets
from cast import BABY, BRAX, DAD, HERO, MAYOR, NURSE, PIP, TUCK, character, sit
from engine import RX, RY, RZ, Scene, T, add_emote, clamp, ease, glow, lerp, pop, speed_lines, star_pts

# Placeholder cast names used in captions; swap here once final names are confirmed.
NAMES = {"Tuck": "Tuck", "Brax": "Brax", "Pip": "Pip", "Bigsby": "Bigsby"}

SKY = ((95, 175, 255), (205, 235, 255))
INDOOR = ((170, 235, 215), (170, 235, 215))


def cam(pos, tgt, u, push=0.1, fov=38, w=None, blur=None, **kw):
    """Default camera: slow push-in of `push` (fraction of the distance) across the shot.
    `w` = world width visible at the target at the start of the shot (sets the distance along pos->tgt)."""
    pos, tgt = np.asarray(pos, float), np.asarray(tgt, float)
    if w:
        dirn = (pos - tgt) / np.linalg.norm(pos - tgt)
        pos = tgt + dirn * w / (2 * math.tan(math.radians(fov) / 2) * 9 / 16)
    p = pos + (tgt - pos) * push * u
    focus = float(np.linalg.norm(tgt - p))
    if blur is None:
        blur = min(12.0, 60.0 / focus)
    return Scene(p, tgt, fov=fov, dof=(focus, blur) if blur > 0 else None, **kw)


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
    c = character(sc, BABY, (1.2, 0, 1.3), face="effort", pose=dict(al=(178, -4), ar=(178, -4)), layer=7)
    top = c["head_top"][1] + 0.02
    lift = lerp(-0.45, top - 0.7, clamp(k)) + 0.03 * math.sin(t * 20)
    M = T(1.2, lift, 1.3) @ RZ(4 * math.sin(t * 9)) @ RY(-10)
    sets.crib(sc, M, layer=6, legs=False)
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
    sets.bench(sc, T(mid[0], mid[1] - 0.5, mid[2]) @ RZ(wob) @ RY(8), layer=6)
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



# ================================================================ helpers 10+
BLUE = dict(grade="blue", gmix=1.0)
STAGE_FRONT = sets.STAGE_Z + 1.6
BABY_PIP = dict(BABY, hair=(250, 226, 172), style="curl", name="Baby Pip")


def probe(spec, pos=(0, 0, 0), yaw=0, pose=None):
    """Anchors of a posed character without drawing it (for aiming cameras at hands etc.)."""
    sc = Scene((0, 2, 10), (0, 1, 0))
    return character(sc, spec, pos, yaw=yaw, face=None, pose=pose)


def flash_at(sc, t, ts):
    if ts <= t < ts + 2 / 30 + 1e-6:
        sc.flash = 1.0


SNAP = dict(ar=(150, -32), er=55, al=(6, 4))


def snap_fx(sc, hand, t, ts, live=True):
    if ts - 0.12 <= t <= ts + 0.35:
        sparks(sc, np.asarray(hand) + np.array([0, 0.12, 0.1]), t, seed=9, n=7, r=0.25, color=(255, 240, 140))

        def burst(d, x, y, s, col, k=clamp((t - ts) / 0.3)):
            for i in range(8):
                a = i * math.pi / 4
                r0, r1 = s * (0.1 + 0.25 * k), s * (0.25 + 0.4 * k)
                d.line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r1, y + math.sin(a) * r1)],
                       fill=(255, 255, 255, int(255 * (1 - k))), width=max(2, int(s * 0.05)))

        if t >= ts:
            sc.sprite(np.asarray(hand) + np.array([0, 0.12, 0.1]), burst, layer=8, live=True)


def hero(sc, pos=(0, 0, 0), yaw=0, face="smile", pose=None, live=True, extra=None, **kw):
    return character(sc, HERO, pos, yaw=yaw, face=face, pose=pose, live=live, face_extra=extra, **kw)


def pip(sc, pos=(0, 0, 0), yaw=0, face="smile", pose=None, live=True, **kw):
    return character(sc, PIP, pos, yaw=yaw, face=face, pose=pose, live=live, **kw)


def head_cam(spec, pos, yaw, pose, u, dist=1.6, push=0.08, side=0.25, up=0.05, fov=32, **kw):
    a = probe(spec, pos, yaw, pose)
    h = a["head"]
    fwd = np.array([math.sin(math.radians(yaw)), 0, math.cos(math.radians(yaw))])
    right = np.array([fwd[2], 0, -fwd[0]])
    k = 2.4
    return cam(h + (fwd * dist + right * side) * k + np.array([0, up, 0]), h + np.array([0, -0.15, 0]), u, push,
               fov=fov, **kw)


def walk(t, speed=7.0, amp=28):
    k = math.sin(t * speed)
    return dict(ll=amp * k, lr=-amp * k, al=(-amp * k * 0.8, 3), ar=(amp * k * 0.8, 3), y=0.03 * abs(k))


# ------------------------------------------------------------- shots 10-15
def s10(t, dur):
    u = t / dur
    sc = cam((0.5, 0.9, 3.4), (0, 2.2, 0), u, 0.12, fov=40, w=2.3, sky=SKY)
    sets.town(sc)
    a = hero(sc, face="smirk", pose=dict(al=(0, 6), ar=(30, 30), er=60, head=(0, 6, -6)))
    return sc


def s11(t, dur):
    u = t / dur
    k = key(t, 0.25)
    pose = dict(ar=(lerp(20, 150, k), lerp(4, -32, k)), er=lerp(0, 55, k), head=(-8, 0, 0))
    sc = head_cam(HERO, (0, 0, 0), 0, pose, u, dist=2.0, side=0.35, up=-0.15, sky=SKY)
    sets.town(sc)
    a = hero(sc, face="grin", pose=pose)
    if t > 0.25:
        sparks(sc, a["hand_r"] + np.array([0, 0.1, 0.1]), t, seed=3, n=6, r=0.22, color=(140, 220, 255))
        sc.sprite(a["hand_r"] + np.array([0, 0.1, 0.1]),
                  lambda d, x, y, s, col: glow(d, x, y, 0.35 * s, (140, 220, 255), 110), layer=8, live=True)
    return sc


def _snap_ecu(t, dur, set_fn, sky, ts, flash=True, extra=None, spec=None, **kw):
    spec = spec or HERO
    wob = 0.02 * math.sin(t * 40) if t < ts else 0.0
    pose = dict(SNAP, er=55 + (8 if t < ts else -6))
    a = probe(spec, (0, 0, 0), 0, pose)
    h = a["hand_r"]
    sc = cam(h + np.array([1.6, 0.3, 3.4]), h + np.array([-0.25, -0.1 + wob, 0]), t / dur, 0.15, fov=34, sky=sky,
             **kw)
    set_fn(sc)
    a = character(sc, spec, (0, 0, 0), face="smirk", pose=pose, live=True)
    snap_fx(sc, a["hand_r"], t, ts)
    if flash:
        flash_at(sc, t, ts)
    return sc


def s12(t, dur):
    return _snap_ecu(t, dur, sets.town, SKY, 0.25)


def frozen_street(sc, tm, live_hero=True):
    """Street with a bird mid-air, a kid mid-jump and a hose spray. tm = seconds of motion since unfreeze."""
    from cast import crowd_spec
    sets.town(sc)
    sets.pigeon(sc, (-1.6 + 1.8 * tm, 2.6 + 0.8 * tm, -0.8), yaw=80, s=1.6, wing=55, bob=0)
    kid = crowd_spec(2)
    jy = max(0.0, 0.85 - 2.6 * tm * tm) if tm > 0 else 0.85
    character(sc, kid, (1.6, jy, -0.6), yaw=-15, face="laugh",
              pose=dict(al=(170, 10), ar=(170, 10), ll=-30, lr=40, kl=60, kr=50), shadow_y=0)
    adult = crowd_spec(5, adult=True)
    g = character(sc, adult, (3.6, 0, -1.4), yaw=-60, face="smile", pose=dict(ar=(80, 0), al=(10, 4)))
    hz = g["hand_r"]
    sc.box(T(*hz) @ RY(-60), (0.12, 0.12, 0.5), (60, 170, 80), layer=6)
    for i in range(12):
        f = i / 11
        tt = f * 0.9 + tm
        x = hz[0] - 3.2 * f - 1.0 * tm
        y = hz[1] + 1.6 * f - 3.0 * f * f - 2.5 * tm * tm
        if y < 0.05:
            continue
        sc.blob(T(x, y, hz[2] + 0.6 * f), (0.16, 0.2, 0.16), (110, 190, 255), layer=6, n=8, m=5)
    if live_hero:
        hero(sc, (-1.3, 0, 1.2), yaw=20, face="smirk", pose=dict(ar=(30, 20), al=(30, -10)), live=True)


def s13(t, dur):
    u = t / dur
    sc = cam((0.5, 3.0, 13.5), (0.8, 1.6, -0.6), u, 0.08, fov=48, sky=SKY, **BLUE)
    frozen_street(sc, 0.0)
    return sc


def s14(t, dur):
    u = t / dur
    sc = cam((0.5, 3.0, 13.5 * 0.92), (0.8, 1.6, -0.6), u, -0.15, fov=48, sky=SKY, grade="blue",
             gmix=1 - clamp(t / 0.45))
    frozen_street(sc, max(0.0, t - 0.45) * 0.5)
    return sc


def s15(t, dur):
    u = t / dur
    k = key(t - 0.15, 0.25) if t > 0.15 else 0.0
    sc = cam((0.4, 1.4, 5.0), (0, 1.5, 0), u, 0.1, fov=38, w=3.0, sky=SKY)
    sets.town(sc)
    hero(sc, face="smirk" if t < 0.2 else "smile",
         pose=dict(al=(lerp(0, 40, k), lerp(4, 60, k)), ar=(lerp(0, 40, k), lerp(4, 60, k)), el=60 * k, er=60 * k,
                   head=(0, 0, 8 * k), y=0.04 * k))
    sx = lerp(0.9, -2.6, ease(clamp((t - 0.4) / 0.7)))
    sc.box(T(sx, 0.08, -1.0), (0.32, 0.16, 0.45), (255, 255, 255), layer=4)
    sc.box(T(sx, 0.2, -1.12), (0.3, 0.1, 0.25), (255, 130, 170), layer=4)
    return sc


# ------------------------------------------------------------- shots 16-22
CLASS_CAM = ((1.2, 2.6, 6.8), (0.0, 1.5, -1.0))
HERO_DESK = (1, 2)


def _class_scene(sc, frozen, t):
    sets.classroom(sc)
    pos = sets.class_desks(sc, t, frozen, skip=(HERO_DESK,))
    return pos[HERO_DESK]


def _seated_hero(sc, x, z, face, pose, live=True, extra=None):
    from cast import sit as _sit
    ll = HERO["leg"][1] * HERO["s"]
    pp = _sit()
    pp.update(pose)
    return hero(sc, (x, 0.86 - ll, z + 0.05), face=face, pose=pp, live=live, extra=extra, shadow=False)


def s16(t, dur):
    u = t / dur
    ts = 1.0
    x, z = 0.0, 1.2
    blue = t >= ts
    sc = cam((x + 1.4, 2.6, z + 7.0), (x, 1.75, z), u, 0.1, fov=40, sky=INDOOR, **(BLUE if blue else {}))
    sets.classroom(sc)
    sets.class_desks(sc, t, blue, skip=(HERO_DESK,))
    k = key(t - 0.5, 0.25) if t > 0.5 else 0.0
    a = _seated_hero(sc, x, z, "smirk", dict(ar=(lerp(70, 150, k), lerp(6, -32, k)), er=55 * k, al=(70, 6)))
    if t > 0.5:
        snap_fx(sc, a["hand_r"], t, ts)
    flash_at(sc, t, ts)
    return sc


def s17(t, dur):
    u = t / dur
    x, z = 0.0, 1.2
    sc = cam((x - 2.4, 3.2, z + 5.6), (x, 1.5, z + 0.3), u, 0.12, fov=40, sky=INDOOR, **BLUE)
    sets.classroom(sc)
    sets.class_desks(sc, t, True, skip=(HERO_DESK,))
    w = math.sin(t * 22)
    a = _seated_hero(sc, x, z, "grit", dict(ar=(72 + 6 * w, 6 + 4 * w), al=(66, 6), head=(0, -18, 0)))
    h = a["hand_r"]
    sc.box(T(h[0], h[1] + 0.12, h[2]) @ RX(-30), (0.05, 0.4, 0.05), (255, 214, 60), layer=7, live=True)
    sc.box(T(x + 0.15, 1.06, z + 0.75), (0.7, 0.02, 0.5), (252, 252, 248), layer=4, live=True)
    add_emote(sc, "sweat", a["head_top"], t, size=0.45, dx=0.45, dy=0.0, start=0.2)
    return sc


def s18(t, dur):
    u = t / dur
    tz = 4.0
    sc = cam((0.01, 9.5, tz + 0.6), (0, 1.2, tz + 0.4), u, 0.12, fov=40, sky=INDOOR, **BLUE)
    sets.classroom(sc)
    sets.class_desks(sc, t, True)
    sets.desk(sc, 0, tz + 0.1, w=1.8, d=3.2, h=1.1, top=(150, 104, 70))
    hero(sc, (0, 1.2, tz + 1.3), face="sleep", pose=dict(lean=-90, al=(170, 20), ar=(150, -10)), shadow=False)
    a = probe(HERO, (0, 1.2, tz + 1.3), 0, dict(lean=-90))
    add_emote(sc, "zzz", a["head"] + np.array([0.5, 0.8, 0.3]), t, size=0.9, dy=0.0, hold=2.0)
    return sc


def s19(t, dur):
    u = t / dur
    sc = cam((0.8, 2.6, 8.6), (0, 1.5, 0), u, 0.1, fov=40, sky=INDOOR, **BLUE)
    sets.classroom(sc)
    sets.desk(sc, -1.0, -0.6, w=3.4, d=1.2, h=1.0, top=(230, 230, 236))
    from cast import sit as _sit
    bl = BRAX["leg"][1] * BRAX["s"]
    pp = _sit()
    pp.update(ar=(70, 4), al=(70, 4))
    character(sc, BRAX, (-1.6, 0.86 - bl, -1.5), face="grin", pose=pp, shadow=False)
    sets.chair(sc, -1.6, -1.55, c=(214, 96, 70))
    hx = lerp(2.0, -0.4, t / dur)
    pose = walk(t)
    pose.update(al=(80, 0), ar=(80, 0))
    a = hero(sc, (hx, 0, 0.9), yaw=-80, face="smirk", pose=pose)
    m = (a["hand_l"] + a["hand_r"]) / 2
    sets.lunch_tray(sc, T(m[0], m[1] + 0.05, m[2]) @ RY(-80), live=True)
    return sc


def s20(t, dur):
    u = t / dur
    sc = cam((-1.5, 0.6, 16.0), (0.6, 4.2, 3.0), u, 0.08, fov=56, sky=SKY)
    sets.school_building(sc)
    sets.lunch_tray(sc, T(1.0, 8.5, 1.9) @ RY(10))
    b = character(sc, BRAX, (1.2, 0, 6.2), yaw=195, face="shock", pose=dict(head=(0, -28, 0), al=(10, 8)))
    add_emote(sc, "?", b["head_top"], t, size=0.8, dx=0.4, dy=0.4, start=0.1)
    return sc


def s21(t, dur):
    u = t / dur
    ts = 0.35
    k = key(t, 0.15)
    pose = dict(ar=(lerp(30, 150, k), lerp(4, -32, k)), er=55 * k)
    sc = cam((1.0, 2.2, 6.0), (0, 1.7, 0), u, 0.12, fov=40, sky=INDOOR, **(BLUE if t >= ts else {}))
    sets.hallway(sc)
    a = hero(sc, face="smirk", pose=pose)
    snap_fx(sc, a["hand_r"], t, ts)
    flash_at(sc, t, ts)
    return sc


def s22(t, dur):
    sc = _snap_ecu(t, dur, sets.hallway, INDOOR, 0.3)
    speed_lines(sc, t, cx=0.5, cy=0.38, n=30, inner=0.22, alpha=170)
    return sc


# ------------------------------------------------------------- shots 23-26
def s23(t, dur):
    u = t / dur
    pose = dict(head=(10, 0, 0), al=(0, 4), ar=(0, 4))
    sc = head_cam(HERO, (0, 0, 0), 0, pose, u, dist=2.2, side=-0.3, up=-0.25, push=0.14, sky=INDOOR)
    sets.hallway(sc)
    a = hero(sc, face="suspicious", pose=pose)
    add_emote(sc, "sweat", a["head_top"], t, size=0.45, dx=0.5, dy=-0.1, start=0.3)
    return sc


def s24(t, dur):
    u = t / dur
    sc = cam((0.02, 4.0, 0.3), (0, 1.25, 0), u, 0.12, fov=36, sky=INDOOR)
    sets.kitchen(sc)
    sets.plate(sc, T(0, 1.3, 0), crumbs=True)
    return sc


def s25(t, dur):
    u = t / dur
    f = ease(clamp((t - 0.3) / 0.55))
    sc = cam((2.4, 0.9, 8.0), (0, 1.1, -0.4), u, 0.06, fov=46, sky=INDOOR)
    sets.hallway(sc)
    a = hero(sc, face="shock" if t > 0.3 else "smile", pose=dict(lean=78 * f, al=(110 * f, 20), ar=(110 * f, 20),
                                                                 ll=-12 * f, lr=-12 * f))
    fl, fr = a["foot_l"], a["foot_r"]
    sc.line3(fl + np.array([0, 0.1, 0.12]), fr + np.array([0, 0.1, 0.12]), (250, 250, 250), width=0.05)
    for sx in (-1, 1):
        sc.blob(T((fl[0] + fr[0]) / 2 + sx * 0.08, fl[1] + 0.12, fl[2] + 0.2), (0.14, 0.08, 0.06), (250, 250, 250),
                n=8, m=5)
    if t > 0.75:
        add_emote(sc, "stars", a["head"], t, size=0.7, dy=0.55, start=0.75)
    return sc


def s26(t, dur):
    u = t / dur
    from cast import marker_moustache
    pose = dict(ll=88, lr=88, al=(10, 4), ar=(10, 4))
    sc = head_cam(HERO, (0, 0.05, 0.2), 0, pose, u, dist=2.0, side=0.3, up=0.0, push=0.12, sky=INDOOR)
    sets.bedroom(sc)
    sets.bed(sc, 0, 1.0)
    a = hero(sc, (0, 0.05, 0.2), face="shock" if t > 0.5 else "sleep", pose=pose, extra=marker_moustache,
             shadow=False)
    add_emote(sc, "!", a["head_top"], t, size=0.6, dx=0.5, dy=0.2, start=0.5)
    return sc


# ------------------------------------------------------------- shots 27-35
def s27(t, dur):
    u = t / dur
    sc = cam((0, 7.0, 17.5), (0, 2.6, -4.0), u, 0.1, fov=46, sky=SKY)
    sets.stage(sc)
    sets.audience(sc, t, faces=("smile", "grin", "laugh"), popcorn=True)
    return sc


def s28(t, dur):
    u = t / dur
    k = key(t, 0.3)
    sc = cam((0.5, 1.2, 9.5), (0, 4.2, sets.STAGE_Z), u, 0.1, fov=50, sky=SKY)
    sets.stage(sc)
    b = character(sc, BRAX, (0, sets.STAGE_TOP, sets.STAGE_Z + 0.6), face="grit" if t < 0.5 else "laugh",
                  pose=dict(al=(lerp(100, 180, k), -4), ar=(lerp(100, 180, k), -4), ll=-10, lr=10))
    m = (b["hand_l"] + b["hand_r"]) / 2
    sets.bus(sc, T(m[0], m[1] + 1.5 + 0.05 * math.sin(t * 14), m[2]) @ RZ(3 * math.sin(t * 9)))
    return sc


def s29(t, dur):
    u = t / dur
    sc = cam((0, 1.0, 10.5), (0, 8.4, -4.0), u, 0.06, fov=62, sky=SKY)
    sets.stage(sc)
    c = np.array([0.0, 9.5, -4.0])
    R = 2.0
    ang = t * 2 * math.pi * 1.6
    for i in range(16):
        a2 = ang - (i + 1) * 0.22
        p = c + np.array([R * math.sin(a2), R * math.cos(a2), 0])
        sz = 0.5 - i * 0.025
        sc.blob(T(*p), (sz, sz, sz), (255, 255, 255), lit=False, n=10, m=6)
    p = c + np.array([R * math.sin(ang), R * math.cos(ang), 0])
    character(sc, TUCK, tuple(p), yaw=90, face="grin",
              pose=dict(lean=90, roll=-math.degrees(ang) * 0 , ar=(178, -6), al=(178, 6), ll=-10, lr=10),
              shadow=False)
    return sc


def s30(t, dur):
    u = t / dur
    sc = cam((0.4, 2.0, 7.0), (0, 1.9, 0), u, 0.1, fov=40, sky=SKY)
    sets.stage(sc)
    lf = 0.5 + 0.5 * math.sin(t * 18)
    b = character(sc, BRAX, (-1.0, 0, 0.3), yaw=55, face="laugh",
                  pose=dict(ar=(90, 0), al=(30 + 20 * lf, 30), head=(0, -6, 4 * lf), lean=-4 * lf))
    hero(sc, (1.3, 0, 0.0), yaw=-45, face="stung", pose=dict(al=(10, 4), ar=(10, 4)))
    return sc


def s31(t, dur):
    u = t / dur
    pose = dict(head=(0, 8, 0))
    sc = head_cam(HERO, (0, 0, 0), -10, pose, u, dist=1.7, side=0.2, up=0.0, push=0.1, sky=SKY)
    sets.stage(sc)
    a = hero(sc, yaw=-10, face="stung", pose=pose)
    add_emote(sc, "sweat", a["head_top"], t, size=0.4, dx=0.45, dy=-0.1, start=0.2)
    return sc


def s32(t, dur):
    u = t / dur
    pose = dict(ar=(60, 30), er=80, head=(0, -5, 0))
    sc = head_cam(HERO, (0, 0, 0), 10, pose, u, dist=2.4, side=-0.4, up=-0.2, push=0.14, sky=INDOOR)
    sets.bedroom(sc)
    a = hero(sc, yaw=10, face="grin" if t > 0.3 else "smirk", pose=pose)
    add_emote(sc, "bulb", a["head_top"], t, size=0.75, dy=0.45, start=0.35, hold=1.4)
    return sc


def _board_pause(D):
    D.text(-0.6, 0.6, "PLAN", (244, 244, 236), h=0.12)
    D.line([(-0.85, 0.42), (-0.35, 0.42)], (244, 244, 236), 0.012)
    D.text(-0.72, 0.1, "1.", (244, 244, 236), h=0.15)
    D.ell(-0.2, 0.1, 0.22, 0.38, (244, 244, 236), n=30)
    D.ell(-0.2, 0.1, 0.2, 0.355, (52, 92, 70), n=30)
    D.rect(-0.28, -0.08, -0.23, 0.28, (244, 244, 236))
    D.rect(-0.17, -0.08, -0.12, 0.28, (244, 244, 236))


def _board_carry(D):
    _board_pause(D)
    D.text(0.25, 0.1, "2.", (244, 244, 236), h=0.15)
    for k in range(5):
        x = 0.4 + k * 0.07
        D.ell(x, -0.25, 0.018, 0.035, (244, 244, 236), n=10)
        D.line([(x, -0.29), (x, -0.42)], (244, 244, 236), 0.006)
        D.line([(x - 0.025, -0.36), (x + 0.025, -0.36)], (244, 244, 236), 0.006)
        D.line([(x, -0.42), (x - 0.02, -0.5)], (244, 244, 236), 0.006)
        D.line([(x, -0.42), (x + 0.02, -0.5)], (244, 244, 236), 0.006)
    D.line([(0.4, -0.6), (0.62, -0.62), (0.82, -0.3)], (255, 220, 120), 0.012)
    D.poly([(0.82, -0.22), (0.86, -0.36), (0.77, -0.33)], (255, 220, 120))
    D.rect(0.68, -0.05, 0.95, 0.02, (244, 244, 236))
    D.text(0.82, 0.12, "STAGE", (244, 244, 236), h=0.06)
    D.text(0.25, -0.75, "3. UNPAUSE!", (255, 160, 170), h=0.09)


def s33(t, dur):
    u = t / dur
    sc = cam((-1.0, 2.4, 4.0), (-0.9, 2.5, -0.6), u, 0.1, fov=40, sky=INDOOR, blur=0)
    sets.chalkboard(sc, _board_pause)
    return sc


def s34(t, dur):
    u = t / dur
    sc = cam((lerp(-0.6, 1.4, u), 2.1, 4.2), (lerp(-0.4, 1.6, u), 2.2, -0.6), 0, 0.0, fov=42, sky=INDOOR, blur=0)
    sets.chalkboard(sc, _board_carry)
    return sc


def s35(t, dur):
    u = t / dur
    pose = dict(head=(0, 0, 8))
    sc = head_cam(HERO, (0, 0, 0), 5, pose, u, dist=1.6, side=0.1, up=0.0, push=0.1, sky=INDOOR)
    sets.bedroom(sc)
    hero(sc, yaw=5, face="wink" if t > 0.1 else "smirk", pose=pose)
    return sc


# ------------------------------------------------------------- shots 36-49
def s36(t, dur):
    return _snap_ecu(t, dur, sets.stage, SKY, 0.2)


def s37(t, dur):
    u = t / dur
    sc = cam((0, 8.5, 14.0), (0, 1.2, 3.0), u, 0.1, fov=46, sky=SKY, **BLUE)
    sets.stage(sc)
    sets.audience(sc, t, frozen=True, faces=("smile", "laugh", "grin"), popcorn=True)
    hero(sc, (0, sets.STAGE_TOP, STAGE_FRONT - 0.4), face="smirk", pose=dict(al=(20, 30), ar=(20, 30)))
    return sc


def _blue_stage(sc, t, crowd=True):
    sets.stage(sc)
    if crowd:
        sets.audience(sc, t, frozen=True, faces=("smile", "laugh"), popcorn=False)


def _carry_set(sc, t, n=12):
    sets.stage(sc)
    sets.stage_crowd(sc, n, face="smile", seed=21)


def s38(t, dur):
    from cast import crowd_spec
    u = t / dur
    sc = cam((1.0, 2.4, 10.5), (0.4, 1.5, 2.6), u, 0.1, fov=40, sky=SKY, **BLUE)
    _carry_set(sc, t, 8)
    hx = lerp(1.2, 0.2, u)
    pose = walk(t, 5, 18)
    pose.update(al=(80, 6), ar=(80, 6), lean=-14)
    a = hero(sc, (hx, 0, 3.2), yaw=-90, face="grit", pose=pose)
    character(sc, crowd_spec(7), (hx - 2.3, 0.05, 3.2), yaw=90, face="smile",
              pose=dict(lean=62, al=(150, 4), ar=(150, 4), ll=-20, lr=-30), shadow_y=0)
    return sc


def s39(t, dur):
    from cast import crowd_spec
    i = min(2, int(t / 0.3))
    tt = t - i * 0.3
    sc = cam(((3.0, 2.4, 8.0), (-3.4, 2.2, 7.6), (0.6, 1.8, 8.0))[i], (0, 1.9, 1.0), tt / 0.3, 0.12, fov=40,
             sky=SKY, **BLUE)
    _carry_set(sc, t, (16, 22, 28)[i])
    pose = walk(t, 8, 18)
    if i == 0:
        pose.update(al=(180, 8), ar=(180, 8))
        a = hero(sc, (0, 0, 1.0), yaw=20, face="grit", pose=pose)
        character(sc, crowd_spec(9), (0, a["hand_l"][1] + 0.2, 1.0 - 0.9), yaw=110, face="smile",
                  pose=dict(lean=90, ll=0, lr=0), shadow=False)
    elif i == 1:
        pose.update(al=(90, 10), ar=(90, 10))
        a = hero(sc, (0, 0, 1.0), yaw=-30, face="effort", pose=pose)
        character(sc, crowd_spec(14, adult=True), (0.35, 1.1, 1.0 + 0.4), yaw=60, face="laugh",
                  pose=dict(lean=-80, al=(150, 20), ar=(150, 20)), shadow=False)
    else:
        pose.update(al=(140, -30), ar=(140, -30))
        a = hero(sc, (0, 0, 1.0), yaw=5, face="grit", pose=pose)
        character(sc, crowd_spec(3), (0, 1.75, 0.8), yaw=5, face="grin",
                  pose=dict(ll=80, lr=80, al=(40, 10), ar=(40, 10)), shadow=False)
    return sc


def s40(t, dur):
    u = t / dur
    sc = cam((0.6, 0.8, 9.5), (0, 2.6, 1.0), u, 0.1, fov=44, sky=SKY, **BLUE)
    _carry_set(sc, t, 32)
    wob = 0.06 * math.sin(t * 30)
    a = hero(sc, (0, -0.25 + wob, 1.0), face="effort",
             pose=dict(al=(178, 14), ar=(178, 14), ll=28, lr=-10, kl=-50, kr=-30, head=(0, -10, 0)))
    m = (a["hand_l"] + a["hand_r"]) / 2
    td = MAYOR["torso"][2] * MAYOR["s"]
    character(sc, MAYOR, (m[0] + 1.7, m[1] + td / 2, m[2]), yaw=90, face="joy",
              pose=dict(lean=-90, al=(60, 30), ar=(60, 30), head=(0, 0, 0)), shadow=False)
    add_emote(sc, "sweat", a["head_top"], t, size=0.45, dx=0.55, dy=-0.2, start=0.1, hold=1.4)
    add_emote(sc, "sweat", a["head_top"], t, size=0.35, dx=-0.55, dy=-0.1, start=0.4, hold=1.0)
    return sc


def s41(t, dur):
    u = t / dur
    sc = cam((1.0, 3.0, 10.0), (0, 2.0, -5.0), u, 0.03, fov=44, sky=SKY, **BLUE)
    _blue_stage(sc, t, crowd=False)
    sets.stage_crowd(sc, 40, face="smile")
    ll = HERO["leg"][1] * HERO["s"]
    hero(sc, (2.5, sets.STAGE_TOP - ll, STAGE_FRONT + 0.75), face="smile",
         pose=dict(ll=88, lr=88, kl=88, kr=88, al=(20, 20), ar=(20, 20)), shadow=False)
    return sc


def _hero_cu(t, dur, face, pose=None, emote=None, set_fn=None, grade=BLUE, side=0.2, dist=1.6, yaw=0):
    pose = pose or {}
    sc = head_cam(HERO, (0, sets.STAGE_TOP, STAGE_FRONT), yaw, pose, t / dur, dist=dist, side=side, up=0.0,
                  push=0.1, sky=SKY, **grade)
    (set_fn or _blue_stage)(sc, t) if set_fn is None else set_fn(sc)
    a = hero(sc, (0, sets.STAGE_TOP, STAGE_FRONT), yaw=yaw, face=face, pose=pose)
    return sc, a


def s42(t, dur):
    sc, a = _hero_cu(t, dur, "grin" if t < 0.35 else "fade")
    return sc


def s43(t, dur):
    k = key(t, 0.15)
    pose = dict(ar=(lerp(40, 150, k), lerp(4, -32, k)), er=55 * k)
    sc, a = _hero_cu(t, dur, "smirk" if t < 0.5 else "worried", pose=pose, dist=2.1, side=0.4)
    snap_fx(sc, a["hand_r"], t, 0.35)
    return sc


def s44(t, dur):
    i = min(3, int(t / 0.3))
    tt = t - i * 0.3
    k = key(tt, 0.1)
    yaw = (-30, 25, -10, 40)[i]
    pose = dict(ar=(lerp(60, 150, k), -32), er=55, al=((140, 60, 120, 30)[i], 40), head=(0, (-10, 5, -20, 0)[i], 0))
    sc, a = _hero_cu(tt, 0.3, ("grit", "effort", "grit", "cry")[i], pose=pose, dist=(2.2, 1.8, 2.6, 1.7)[i],
                     side=(0.4, -0.5, 0.0, 0.3)[i], yaw=yaw)
    snap_fx(sc, a["hand_r"], tt, 0.1)
    add_emote(sc, "sweat", a["head_top"], tt, size=0.4, dx=0.5, dy=-0.1, start=0.0)
    return sc


def s45(t, dur):
    u = t / dur
    p = (0, sets.STAGE_TOP + 0.26, STAGE_FRONT - 0.6)
    sc = cam((0.01, 7.0, p[2] - 1.1), (0, 1.0, p[2] - 1.2), u, 0.12, fov=40, sky=SKY, **BLUE)
    _blue_stage(sc, t)
    a = hero(sc, p, face="cry", pose=dict(lean=-90, al=(90, 60), ar=(90, 60), ll=10, lr=-10), shadow=False)
    add_emote(sc, "tears", a["head"] + np.array([0, 0.4, 0]), t, size=0.6, dy=0.0, hold=2.0)
    return sc


def s46(t, dur):
    u = t / dur
    c = np.array([0, 7.25, sets.STAGE_Z - 1.9])
    sc = cam(c + np.array([0.3, -0.2, 2.6]), c, u, 0.12, fov=38, sky=SKY, **BLUE)
    sets.stage(sc)
    return sc


def s47(t, dur):
    u = t / dur
    sc = cam((0.5, 15.0, 9.0), (0, 0.9, -4.0), u, 0.18, fov=42, sky=SKY, **BLUE)
    sets.stage(sc)
    sets.stage_crowd(sc, 40, face="smile")
    sets.audience(sc, t, frozen=True)
    ll = HERO["leg"][1] * HERO["s"]
    hero(sc, (1.5, sets.STAGE_TOP - 0.0, STAGE_FRONT + 0.2), face="sad",
         pose=dict(ll=88, lr=88, al=(40, 10), ar=(40, 10)), shadow=False)
    hero_y = sets.STAGE_TOP + 0.005
    for g in range(6):
        gx, gz = -2.2 + g * 0.65, STAGE_FRONT + 1.0
        for k in range(4):
            x = gx + k * 0.1
            sc.quad([(x, hero_y, gz), (x + 0.035, hero_y, gz), (x + 0.035, hero_y, gz + 0.45), (x, hero_y, gz + 0.45)],
                    (250, 250, 250), layer=2)
        sc.quad([(gx - 0.05, hero_y + 0.002, gz + 0.32), (gx + 0.36, hero_y + 0.002, gz + 0.1),
                 (gx + 0.37, hero_y + 0.002, gz + 0.14), (gx - 0.04, hero_y + 0.002, gz + 0.36)], (250, 250, 250),
                layer=2)
    return sc


def s48(t, dur):
    u = t / dur
    p = (0, sets.STAGE_TOP + 0.26, STAGE_FRONT - 0.6)
    a = probe(HERO, p, 0, dict(lean=-90))
    h = a["head"]
    sc = cam(h + np.array([0.2, 1.9, 0.15]), h + np.array([0.0, 0.0, 0.1]), u, 0.1, fov=34, sky=SKY, **BLUE)
    _blue_stage(sc, t, crowd=False)
    hero(sc, p, face="sleep" if t < 0.35 else "shock", pose=dict(lean=-90, al=(90, 60), ar=(90, 60)), shadow=False)
    if t > 0.35:
        add_emote(sc, "!", h, t, size=0.35, dx=0.3, dy=0.4, start=0.35)
    return sc


def s49(t, dur):
    u = t / dur
    c = np.array([0.2, sets.STAGE_TOP, STAGE_FRONT - 1.4])
    sc = cam(c + np.array([0.4, 0.35, 1.6]), c + np.array([0, 0.25, 0]), u, 0.12, fov=40, sky=SKY, **BLUE)
    sets.stage(sc)
    rng = np.random.RandomState(4)
    for i in range(10):
        ph = (t * 1.2 + i * 0.1) % 1.0
        y = c[1] + 1.2 * (1 - ph) + 0.03
        sc.box(T(c[0] + rng.uniform(-0.3, 0.3), y, c[2] + rng.uniform(-0.2, 0.2)) @ RY(rng.uniform(0, 90)),
               (0.06, 0.05, 0.06), (200, 140, 80), live=True)
    for i in range(8):
        sc.box(T(c[0] + rng.uniform(-0.4, 0.4), c[1] + 0.03, c[2] + rng.uniform(-0.3, 0.3)), (0.06, 0.04, 0.06),
               (200, 140, 80), live=True)
    return sc


# ------------------------------------------------------------- shots 50-58
PIP_SPOT = (0.0, sets.STAGE_TOP, STAGE_FRONT - 0.5)


def _pip_stage(sc, t, crowd=True):
    sets.stage(sc)
    if crowd:
        sets.stage_crowd(sc, 40, face="smile", clear=(PIP_SPOT[0], PIP_SPOT[2] + 0.4, 1.9))


def _chew_face(t):
    return "chew0" if int(t * 8) % 2 == 0 else "chew1"


def _pip_eating(sc, t, pos=PIP_SPOT, yaw=0):
    pose = dict(ar=(120, -20), er=50, al=(10, 6))
    a = pip(sc, pos, yaw=yaw, face=_chew_face(t), pose=pose)
    h = a["hand_r"]
    sets.cookie(sc, T(h[0], h[1] + 0.12, h[2] + 0.12) @ RY(yaw), s=0.8, live=True)
    return a


def s50(t, dur):
    u = t / dur
    sc = cam((0.5, 2.0, PIP_SPOT[2] + 4.0), (0, 1.6, PIP_SPOT[2]), u, 0.1, fov=40, sky=SKY, **BLUE)
    _pip_stage(sc, t)
    _pip_eating(sc, t)
    return sc


def s51(t, dur):
    u = ease(t / dur)
    p0 = np.array([0.0, 2.6, 11.0])
    p1 = np.array([0.15, 1.7, PIP_SPOT[2] + 2.0])
    tgt = np.array([0.0, 1.55, PIP_SPOT[2]])
    sc = cam(p0 + (p1 - p0) * u, tgt, 0, 0.0, fov=44, sky=SKY, **BLUE)
    _pip_stage(sc, t)
    sets.audience(sc, t, frozen=True)
    _pip_eating(sc, t)
    return sc


def s52(t, dur):
    u = t / dur
    pose = dict(ar=(120, -20), er=50)
    sc = head_cam(PIP, PIP_SPOT, 0, pose, u, dist=1.3, side=0.15, up=-0.05, push=0.1, sky=SKY, **BLUE)
    _pip_stage(sc, t)
    _pip_eating(sc, t)
    return sc


def s53(t, dur):
    u = t / dur
    sc = cam((0.5, 1.9, 3.6), (0, 1.45, 0), u, 0.1, fov=32, w=2.6, sky=INDOOR, grade="sepia", gmix=1.0)
    sets.nursery(sc)
    sets.crib(sc, T(0, 0, 0))
    a = character(sc, BABY_PIP, (0, 1.0, 0.05), face="joy",
                  pose=dict(ll=80, lr=80, y=-0.17, ar=(140, -20), al=(20, 10)), shadow=False)
    play_sprite(sc, a["hand_r"] + np.array([0, 0.12, 0.08]), t, size=0.16)
    return sc


def play_sprite(sc, pos, t, size=0.2):
    def fn(d, x, y, s, col):
        r = size * s * (1 + 0.06 * math.sin(t * 12))
        glow(d, x, y, r * 2.2, (255, 220, 90), 120)
        d.polygon([(x - r * 0.6, y - r), (x - r * 0.6, y + r), (x + r, y)], fill=(255, 236, 120),
                  outline=(120, 80, 20), width=max(2, int(r * 0.12)))

    sc.sprite(pos, fn, layer=9, live=True)


def s54(t, dur):
    u = t / dur
    ts = 0.35
    k = key(t, 0.18)
    pose = dict(ar=(lerp(30, 150, k), lerp(4, -32, k)), er=55 * k)
    sc = cam((0.9, 1.9, 4.6), (0, 1.8, 0), u, 0.12, fov=40, sky=SKY, **(BLUE if t >= ts else {}))
    sets.town(sc)
    a = hero(sc, face="smirk", pose=pose)
    snap_fx(sc, a["hand_r"], t, ts)
    flash_at(sc, t, ts)
    return sc


def s55(t, dur):
    u = t / dur
    pose = dict(ar=(150, -10), er=10, head=(0, 8, 0))
    a = probe(PIP, PIP_SPOT, 0, pose)
    h = a["hand_r"]
    sc = cam(h + np.array([0.6, -0.3, 2.0]), h + np.array([-0.1, -0.35, 0]), u, 0.12, fov=40, sky=SKY, **BLUE)
    _pip_stage(sc, t)
    a = pip(sc, PIP_SPOT, face="smug", pose=pose)
    play_sprite(sc, a["hand_r"] + np.array([0, 0.08, 0.08]), t, size=0.14)
    return sc


def s56(t, dur):
    i = min(2, int(t / 0.6))
    tt = t - i * 0.6
    u = tt / 0.6
    if i == 0:
        sc = cam((2.6, 2.8, 5.6), (-0.2, 1.2, 0.4), u, 0.1, fov=40, sky=INDOOR, **BLUE)
        sets.kitchen(sc)
        sets.plate(sc, T(0.3, 1.27, 0), crumbs=False)
        a = pip(sc, (-0.6, 0.35, 1.2), yaw=150, face="smug", pose=dict(ar=(100, -20), al=(10, 6)))
        h = a["hand_r"]
        sets.cookie(sc, T(h[0], h[1] + 0.1, h[2]) @ RX(-60), s=0.8, live=True)
    elif i == 1:
        sc = cam((2.0, 1.6, 5.2), (0, 0.8, 0), u, 0.1, fov=42, sky=INDOOR, **BLUE)
        sets.hallway(sc)
        a = hero(sc, (0, 0, -0.3), face="smirk", pose=dict(al=(20, 6), ar=(20, 6)), live=False)
        w = math.sin(tt * 30)
        pip(sc, (0.55, -0.15, 0.55), yaw=-130, face="smug",
            pose=dict(ll=-70, lr=-70, kl=110, kr=110, lean=30, al=(60 + 10 * w, 10), ar=(60 - 10 * w, 10)))
        fl, fr = a["foot_l"], a["foot_r"]
        sc.line3(fl + np.array([0, 0.1, 0.12]), fr + np.array([0, 0.1, 0.12]), (250, 250, 250), width=0.05)
    else:
        from cast import marker_moustache
        sc = cam((3.0, 3.6, 5.6), (0.2, 1.1, 0.2), u, 0.1, fov=40, sky=INDOOR, **BLUE)
        sets.bedroom(sc)
        sets.bed(sc, 0, 1.0)
        hero(sc, (0, 1.12, 2.3), face="sleep", pose=dict(lean=-90), extra=marker_moustache, live=False,
             shadow=False)
        a = pip(sc, (1.5, 0, 0.0), yaw=-70, face="smug", pose=dict(ar=(100 + 15 * math.sin(tt * 30), 0), al=(10, 6)))
        h = a["hand_r"]
        sc.box(T(h[0] - 0.1, h[1] + 0.1, h[2]) @ RZ(60), (0.06, 0.3, 0.06), (30, 30, 34), live=True)
    return sc


def s57(t, dur):
    u = t / dur
    pose = dict(al=(85, -40), ar=(85, -40), el=30, er=30, head=(0, -6, -6))
    sc = cam((0.6, 0.6, PIP_SPOT[2] + 3.0), (0, 1.5, PIP_SPOT[2]), u, 0.12, fov=40, sky=SKY, **BLUE)
    _pip_stage(sc, t)
    pip(sc, PIP_SPOT, face="smug", pose=pose)
    return sc


def spotlight(sc, x, z, y=sets.STAGE_TOP, r=1.0):
    pts = [(x + r * math.cos(a), y + 0.012, z + r * 0.8 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 25)[:-1]]
    sc.quad(pts, (255, 246, 200), layer=2, live=True)
    sc.line3((x, y + 7.5, z - 1.0), (x, y + 0.1, z), (255, 250, 210, 70), width=1.6, live=True)


def s58(t, dur):
    u = t / dur
    sc = cam((2.4, 2.4, PIP_SPOT[2] + 6.5), (0, 1.6, PIP_SPOT[2]), u, 0.1, fov=40, sky=SKY, **BLUE)
    _pip_stage(sc, t, crowd=False)
    sets.stage_crowd(sc, 24, face="smile", seed=8, clear=(0, PIP_SPOT[2] + 0.4, 2.6))
    spotlight(sc, -1.8, PIP_SPOT[2] - 0.4)
    pip(sc, PIP_SPOT, yaw=30, face="smug", pose=dict(al=(95, -20), ar=(0, 6), head=(-30, 0, 0)))
    hero(sc, (1.4, sets.STAGE_TOP - 0.62, PIP_SPOT[2] + 0.4), yaw=-50, face="worried",
         pose=dict(kl=90, kr=90, al=(80, -20), ar=(80, -20), el=40, er=40))
    return sc


# ------------------------------------------------------------- shots 59-65
def s59(t, dur):
    sc = _snap_ecu(t, dur, lambda s: _pip_stage(s, t), SKY, 0.7, spec=PIP, **BLUE)
    return sc


def s60(t, dur):
    u = t / dur
    sc = cam((0, 4.2, 15.0), (0, 2.5, -4.0), u, 0.08, fov=46, sky=SKY, grade="blue", gmix=1 - clamp(t / 0.5))
    sets.stage(sc)
    sets.stage_crowd(sc, 40, face="smile")
    sets.audience(sc, t, frozen=True)
    return sc


def s61(t, dur):
    u = t / dur
    sc = cam((0.5, 0.6, 6.5), (0, 2.3, sets.STAGE_Z), u, 0.1, fov=50, sky=SKY)
    sets.stage(sc)
    sets.stage_crowd(sc, 40, face="neutral", confused=True, t=t)
    return sc


def confetti(sc, t, n=70, seed=6):
    rng = np.random.RandomState(seed)
    cols = [(255, 90, 90), (255, 214, 70), (110, 220, 140), (110, 170, 255), (220, 120, 255), (255, 255, 255)]
    pts = [(rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0.3, 0.7), rng.randint(6), rng.uniform(0, 6))
           for _ in range(n)]

    def fn(d, W, H):
        for x0, y0, sp, ci, ph in pts:
            y = ((y0 + t * sp) % 1.1 - 0.05) * H
            x = (x0 + 0.03 * math.sin(t * 4 + ph)) * W
            w, h = W * 0.012, W * 0.02 * abs(math.sin(t * 6 + ph)) + 2
            d.rectangle([x - w, y - h, x + w, y + h], fill=cols[ci])

    sc.overlay(fn)


def s62(t, dur):
    u = t / dur
    sc = cam((0, 4.2, -3.6), (0, 1.4, 6.0), u, 0.1, fov=50, sky=SKY)
    sets.stage(sc)
    sets.audience(sc, t, faces=("laugh", "joy", "grin"), standing=True)
    confetti(sc, t)
    return sc


def s63(t, dur):
    u = t / dur
    k = key(t - 0.1, 0.3) if t > 0.1 else 0
    sc = cam((0.8, 1.0, PIP_SPOT[2] + 6.0), (0.5, 1.8, PIP_SPOT[2] - 0.6), u, 0.1, fov=42, sky=SKY)
    sets.stage(sc)
    spotlight(sc, 0, PIP_SPOT[2])
    pip(sc, PIP_SPOT, face="joy", pose=dict(lean=35 * k, al=(20, 30), ar=(20, 30)))
    hero(sc, (1.5, sets.STAGE_TOP, PIP_SPOT[2] - 1.6), yaw=-20, face="jaw", pose=dict(al=(10, 20), ar=(10, 20)))
    confetti(sc, t, n=40, seed=9)
    return sc


def s64(t, dur):
    u = t / dur
    sc = cam((0.4, 1.8, PIP_SPOT[2] + 7.5), (0.4, 2.2, PIP_SPOT[2]), u, 0.12, fov=40, sky=SKY)
    sets.stage(sc)
    sets.trophy(sc, T(1.0, sets.STAGE_TOP, PIP_SPOT[2] - 0.2), s=1.0)
    pip(sc, (-0.6, sets.STAGE_TOP, PIP_SPOT[2] + 0.1), yaw=20, face="joy", pose=dict(ar=(150, -20), al=(20, 10)))
    confetti(sc, t, n=35, seed=12)
    return sc


def s65(t, dur):
    u = t / dur
    sc = cam((1.2, 2.6, 7.0), (0.3, 1.3, -0.3), u, 0.1, fov=40, sky=INDOOR)
    sets.bedroom(sc)
    sets.desk(sc, 0, 0.7, w=1.4, d=0.8, h=0.55, top=(255, 214, 110))
    for k, c in enumerate(((240, 60, 60), (60, 140, 240), (80, 200, 100), (255, 200, 40))):
        sc.box(T(-0.45 + k * 0.12, 0.62, 0.95) @ RY(15 * k), (0.06, 0.06, 0.32), c, layer=4)
    sc.box(T(0.2, 0.6, 0.65), (0.7, 0.02, 0.5), (252, 252, 248), layer=4,
           decal=lambda D: [D.line([(-0.8, v), (0.8, v)], (200, 200, 220), 0.02) for v in (-0.5, 0, 0.5)])
    w = math.sin(t * 20)
    hero(sc, (0, -0.55, -0.1), face="miserable",
         pose=dict(kl=90, kr=90, ar=(60 + 8 * w, 8 * w), al=(50, 6), head=(0, -12, 0)))
    a = _pip_eating(sc, t, pos=(1.1, 0, -1.2), yaw=-25)
    sc.fade = clamp((t - (dur - 0.45)) / 0.4)
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
    (10, 0.5, "Mine?", s10),
    (11, 1.2, "I can pause TIME.", s11),
    (12, 0.6, "One snap.", s12),
    (13, 0.8, "Everything stops.", s13),
    (14, 2.7, "A few minutes later, it starts again by itself.", s14),
    (15, 1.2, "I never wondered why.", s15),
    (16, 1.8, "I paused 3 times a day.", s16),
    (17, 0.9, "To finish homework.", s17),
    (18, 0.6, "To nap.", s18),
    (19, 1.2, N("To put Brax's lunch"), s19),
    (20, 0.9, "on the ROOF.", s20),
    (21, 0.9, "Then 10 times.", s21),
    (22, 0.6, "Then 50.", s22),
    (23, 1.2, "But something was WRONG.", s23),
    (24, 1.5, "Every pause, my cookie disappeared.", s24),
    (25, 1.5, "My shoes got tied TOGETHER.", s25),
    (26, 2.1, "Once, I woke up with a moustache.", s26),
    (27, 1.5, "Friday was the Power Show.", s27),
    (28, 1.2, N("Brax lifted a BUS."), s28),
    (29, 1.2, N("Tuck did 9 loops."), s29),
    (30, 1.8, N("Brax said my power was FAKE."), s30),
    (31, 1.5, "Nobody had ever seen it.", s31),
    (32, 2.1, "So I planned the biggest trick ever.", s32),
    (33, 0.6, "Pause time.", s33),
    (34, 2.1, "Carry the whole audience onto the stage.", s34),
    (35, 0.5, "Unpause.", s35),
    (36, 0.6, "I snapped.", s36),
    (37, 0.8, "Everything stopped.", s37),
    (38, 1.2, "I carried 40 people.", s38),
    (39, 0.9, "One by one.", s39),
    (40, 1.5, N("Mayor Bigsby weighs a LOT."), s40),
    (41, 2.3, "Then I waited for time to start.", s41),
    (42, 0.8, "It didn't.", s42),
    (43, 0.9, "I snapped. Nothing.", s43),
    (44, 1.2, "I snapped 100 times.", s44),
    (45, 0.7, "NOTHING.", s45),
    (46, 2.1, "The clock said 4 minutes to showtime.", s46),
    (47, 2.3, "It said that for 3 DAYS.", s47),
    (48, 1.2, "Then I heard it.", s48),
    (49, 0.7, "Chewing.", s49),
    (50, 0.5, N("Pip."), s50),
    (51, 0.9, "On the stage.", s51),
    (52, 0.9, "Eating my cookie.", s52),
    (53, 1.8, "Her power showed up YEARS ago.", s53),
    (54, 0.9, "I pause time.", s54),
    (55, 0.9, N("Pip presses PLAY."), s55),
    (56, 1.8, "Every pause, she'd been walking around.", s56),
    (57, 2.1, "And this time, she wasn't pressing anything.", s57),
    (58, 2.4, "Not until I gave her what she wanted.", s58),
    (59, 1.5, N("So Pip did the snap."), s59),
    (60, 0.7, "Time started.", s60),
    (61, 1.5, "Forty people appeared on stage.", s61),
    (62, 1.2, "The crowd went WILD.", s62),
    (63, 0.7, N("For Pip."), s63),
    (64, 1.2, "She won first place.", s64),
    (65, 1.8, "Now I do HER homework.", s65),
]


# Narration timing: when voice_timing.json exists (built from the recorded voiceover),
# each shot takes its duration from the voice and captions use the spoken word onsets.
WORD_TIMES = {}
_vt = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_timing.json")
if os.path.exists(_vt):
    import json as _json
    _timing = {int(k): v for k, v in _json.load(open(_vt)).items()}
    SHOTS = [(n, _timing[n]["dur"], txt, fn) if n in _timing else (n, d, txt, fn) for n, d, txt, fn in SHOTS]
    WORD_TIMES = {n: [(t, w) for t, w in v["words"]] for n, v in _timing.items()}
