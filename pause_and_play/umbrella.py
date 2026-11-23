"""The Weather Umbrella: shot list. Each shot: (number, seconds, caption text, fn(t, dur) -> Scene)."""
import os

TIMING_FILE = "umbrella_timing.json"
SPOKEN = {"400": "four hundred"}
PHONES = {"mia": "M IY AH", "omar": "OW M AA R", "bryce": "B R AY S", "omar's": "OW M AA R Z"}

LINES = [
    "In this town, every year one kid gets the Weather Umbrella.",
    "Whatever you shout when you open it falls from the sky.",
    "For one whole DAY.",
    "Last year, Bryce shouted PIZZA!",
    "There's still cheese on the roofs.",
    "The year before, a little kid shouted PUPPIES!",
    "The town has 400 dogs now.",
    "Nobody's complaining.",
    "This year, the mayor drew a name from the hat.",
    "MIA!",
    "That's me.",
    "Everyone crowded around me.",
    "Snow day! Candy! Money!",
    "PIZZA AGAIN! That was Bryce.",
    "But there was only one thing I wanted.",
    "My best friend Omar was moving away. On Saturday.",
    "His family's farm is up on the hill.",
    "Nothing grows there anymore.",
    "It hasn't really rained in TWO years.",
    "Everybody asks the umbrella for fun stuff.",
    "Nobody ever asks for rain.",
    "So I made a plan.",
    "I'd shout SNOW! So much snow, the moving truck could never leave.",
    "Saturday morning, I climbed the hill with the umbrella.",
    "The moving truck was already there. Boxes everywhere.",
    "Omar's dad stood at the edge of the dead field.",
    "He didn't say anything. He just looked.",
    "Omar saw me. He smiled like everything was fine.",
    "It wasn't.",
    "I held up the umbrella.",
    "I took a deep breath.",
    "I opened it.",
    "RAIN!",
    "Down in town, everyone groaned.",
    "RAIN? You could've had CANDY!",
    "Then the clouds rolled in. Big. Dark. Heavy.",
    "And it RAINED.",
    "On every dry, cracked inch of that farm.",
    "The field turned green right in front of us.",
    "Sprouts. Vines. Pumpkins the size of cars.",
    "Omar's dad dropped the box he was holding.",
    "The moving truck drove away. EMPTY.",
    "Omar didn't move away.",
    "His farm grows the best food in town now.",
    "Even Bryce eats his vegetables.",
    "On PIZZA.",
]
import math  # noqa: E402

import numpy as np  # noqa: E402

import laughs_sets as ls  # noqa: E402
import sets  # noqa: E402
import umbrella_sets as us  # noqa: E402
from cast import BRYCE, FARMER, MAYOR, MIA, OMAR, character, crowd_spec  # noqa: E402
from engine import RX, RY, RZ, T, add_emote, clamp, lerp, xf  # noqa: E402
from laughs import bob, dcam, dfcam, head_cu, ht, laugh_pose  # noqa: E402
from shots import sparks, walk  # noqa: E402
from story import load_timing  # noqa: E402

PUPPY_KID = dict(crowd_spec(3), name="Puppy kid", s=0.7)
STORM_SKY = ((90, 96, 120), (150, 156, 176))
HOLD_UP = dict(ar=(170, -10), al=(10, 6))
MIA_SQ = (0.0, 0, 1.6)
FIELD_EDGE = (-2.0, 0, 1.0)  # where Mia, Omar and his dad stand looking over the field
WT = {}


def word_t(num, i, default=0.0):
    w = WT.get(num, [])
    return w[i][0] if i < len(w) else default


def with_umbrella(sc, spec, pos, yaw=0, face="grin", open_k=1.0, t=0.0, glow_k=1.0, pose=None):
    p = dict(HOLD_UP)
    p.update(pose or {})
    a = character(sc, spec, pos, yaw=yaw, face=face, pose=p)
    us.umbrella(sc, T(*a["hand_r"]) @ RY(yaw) @ T(0, -0.1, 0), open_k=open_k, glow_k=glow_k, t=t)
    return a


def crowd(sc, t, n=8, z=2.2, faces=("joy", "grin", "smile"), seed=1, poses=None, yaw=180):
    out = []
    for i in range(n):
        x = -4.2 + i * 8.4 / max(1, n - 1)
        out.append(character(sc, crowd_spec(i + seed, adult=i % 3 != 0), (x, 0, z + 0.4 * math.sin(i * 2.1)),
                             yaw=yaw + 15 * math.sin(i), face=faces[i % len(faces)],
                             pose=(poses[i % len(poses)] if poses else None)))
    return out


# ------------------------------------------------------- 1-8: the rule
def u01(t, dur):
    u = t / dur
    sc = dcam((0.6, 3.4, 1.4), (1.8, 3.1, -1.6), u, 0.16, fov=36, bloom=0.8)
    us.square(sc, t)
    sparks(sc, (1.8, 3.6, -1.6), t, seed=1, n=5, r=0.6)
    return sc


def u02(t, dur):
    u = t / dur
    sc = dcam((0.6, 0.9, 5.0), (0.0, 2.6 + 1.6 * u, 0.6), u, 0.0, fov=44)
    us.square(sc, t, umbrella_on_stand=False)
    with_umbrella(sc, crowd_spec(4), (0, 0, 0.6), face="jaw", open_k=clamp(t / 0.3), t=t,
                  pose=dict(head=(0, 25, 0)))

    def swirl(d, W, H):
        for i in range(5):
            r = W * (0.15 + 0.07 * i)
            a0 = (t * 140 + i * 50) % 360
            d.arc([W * 0.5 - r, H * 0.12 - r * 0.4, W * 0.5 + r, H * 0.12 + r * 0.4], a0, a0 + 120,
                  fill=(255, 255, 255, 150), width=max(3, W // 200))
    sc.overlay(swirl)
    return sc


def u03(t, dur):
    u = t / dur
    sc = dcam((-8, 6.0, 14.0), (2.0, 7.0, -10.0), u, 0.0, fov=48, sky=STORM_SKY)
    sets.town(sc)
    us.storm(sc, 1.0, t * 3, y=14.0)
    return sc


def u04(t, dur):
    u = t / dur
    sc = head_cu(BRYCE, (0, 0, 0.6), 0, HOLD_UP, u, dist=4.0, up=-0.8, fov=40)
    us.square(sc, t, umbrella_on_stand=False)
    a = with_umbrella(sc, BRYCE, (0, 0, 0.6), face="jaw", t=t, pose=dict(head=(0, 15, 0)))
    ls.sticker(sc, a["head"], "PIZZA!", t, start=0.6, hold=1.2, size=0.5, dx=-0.9, dy=0.5, color=(255, 200, 70))
    us.falling(sc, t, "pizza", n=12)
    return sc


def u05(t, dur):
    u = t / dur
    sc = dcam((-6 + 6 * u, 3.0, 4.0), (-4 + 6 * u, 3.6, -6.0), u, 0.0, fov=46)
    sets.town(sc)
    us.cheese_roofs(sc, t)
    return sc


def u06(t, dur):
    u = t / dur
    sc = dcam((0.4, 2.4, 4.6), (0.0, 2.6 - 1.0 * u, 0.6), u, 0.0, fov=42)
    sets.town(sc)
    a = with_umbrella(sc, PUPPY_KID, (0, 0, 0.6), face="laugh", t=t, pose=dict(head=(0, 15, 0)))
    for i in range(5):
        ph = (t * 0.7 + i * 0.2) % 1.0
        us.puppy(sc, T(-1.5 + 0.7 * i, 4.0 - 4.0 * ph, 0.8 + 0.3 * (i % 2)) @ RZ(40 * math.sin(t * 5 + i)), t,
                 us.PUP_FURS[i % 5])
    add_emote(sc, "stars", a["head_top"], t, size=0.5, dx=0.5, dy=0.2, start=0.6)
    return sc


def u07(t, dur):
    u = t / dur
    sc = dcam((0.0, 6.0, 12.0), (0.0, 0.6, 1.0), u, 0.04, fov=46)
    sets.town(sc)
    us.puppies(sc, 34, t, area=(-6, 6, -1.5, 6.0))
    return sc


def u08(t, dur):
    u = t / dur
    pos = (0, -0.9, 0.6)
    sc = head_cu(crowd_spec(9, adult=True), pos, 0, None, u, dist=4.6, up=0.6, fov=38)
    sets.town(sc)
    a = character(sc, crowd_spec(9, adult=True), pos, face="joy", shadow=False)
    us.puppies(sc, 9, t, area=(-1.2, 1.2, 0.8, 1.6), seed=7)
    add_emote(sc, "stars", a["head_top"], t, size=0.5, dx=0.5, dy=0.15, start=0.3)
    return sc


# ------------------------------------------------------- 9-14: Mia is chosen
STAGE = np.array([0.0, 0.85, -1.4])


def u09(t, dur):
    u = t / dur
    sc = dcam((0.5, 4.8, 9.0), (0.0, 3.0, -1.4), u, 0.1, fov=42)
    us.square(sc, t)
    m = character(sc, MAYOR, STAGE, face="neutral", pose=dict(ar=(70, -20), er=40))
    us.name_hat(sc, T(*(m["hand_r"] + np.array([0.0, -0.3, 0.25]))))
    crowd(sc, t, n=7, z=2.6)
    return sc


def u10(t, dur):
    u = t / dur
    pose = dict(ar=(170, -10), al=(20, 6))
    sc = head_cu(MAYOR, STAGE, 0, pose, u, dist=3.6, up=0.3, fov=36)
    us.square(sc, t)
    m = character(sc, MAYOR, STAGE, face="jaw", pose=pose)
    us.name_slip(sc, T(*(m["hand_r"] + np.array([0, 0.3, 0.1]))))
    return sc


def u11(t, dur):
    u = t / dur
    sc = head_cu(MIA, MIA_SQ, 0, None, u, dist=3.2, fov=36)
    us.square(sc, t)
    a = character(sc, MIA, MIA_SQ, yaw=0, face="shock")
    add_emote(sc, "!", a["head_top"], t, size=0.6, dx=0.5, dy=0.2, start=0.05)
    return sc


def u12(t, dur):
    u = t / dur
    sc = dcam((0.3, 9.0, 7.0), (0.0, 0.5, 1.6), u, 0.0, fov=44)
    us.square(sc, t)
    character(sc, MIA, MIA_SQ, yaw=180, face="shock")
    k = clamp(t / 1.0)
    for i in range(10):
        a = 2 * math.pi * i / 10
        r = lerp(5.5, 1.5, k)
        p = (MIA_SQ[0] + r * math.cos(a), 0, MIA_SQ[2] + r * math.sin(a))
        character(sc, crowd_spec(i + 2), p, yaw=math.degrees(math.atan2(-math.cos(a), -math.sin(a))), face="grin",
                  pose=walk(t + i, 10, 25) if k < 1 else dict(ar=(150, -20)))
    return sc


def u13(t, dur):
    """'Snow day!' 'Candy!' 'Money!' — three quick cuts."""
    starts = [0.0, word_t(13, 2, dur / 3), word_t(13, 3, 2 * dur / 3)]
    k = 0 if t < starts[1] - 0.05 else (1 if t < starts[2] - 0.05 else 2)
    tt = t - starts[k]
    spec = crowd_spec((5, 7, 11)[k])
    pos = (0, 0, 1.6)
    sc = head_cu(spec, pos, 0, dict(ar=(150, -20)), 0, dist=3.0, side=0.3 * (k - 1), fov=38)
    us.square(sc, t)
    a = character(sc, spec, pos, face=("jaw", "grin", "sparkle")[k], pose=dict(ar=(150, -20)))
    ls.sticker(sc, a["head"], ("SNOW DAY!", "CANDY!", "MONEY!")[k], tt, start=0.0, hold=1.0, size=0.38, dy=0.75,
               color=((180, 220, 255), (255, 140, 200), (120, 230, 120))[k])
    return sc


def u14(t, dur):
    u = t / dur
    sc = head_cu(BRYCE, (0.0, 0, 2.0), 0, dict(lean=12), u, dist=2.6, fov=36, push=0.15)
    us.square(sc, t)
    a = character(sc, BRYCE, (0.0, 0, 2.0), face="laugh", pose=dict(lean=12, ar=(150, -20)))
    ls.sticker(sc, a["head"], "PIZZA!", t, start=0.1, hold=1.4, size=0.42, dx=-0.6, dy=0.7, color=(255, 200, 70))
    return sc


# ------------------------------------------------------- 15-23: Omar
def u15(t, dur):
    u = t / dur
    sc = head_cu(MIA, MIA_SQ, 0, None, u, dist=3.0, fov=36, push=0.14, blur=14.0)
    us.square(sc, t)
    character(sc, MIA, MIA_SQ, yaw=0, face="worried")
    crowd(sc, t, n=6, z=-0.2, faces=("grin",))
    return sc


BENCH = np.array([0.0, 0.0, 0.8])


def _bench(sc, t, mia_face="sad", omar_face="smile", box=True):
    sets.town(sc)
    sets.bench(sc, T(*BENCH))
    from cast import sit
    for spec, x, face in ((MIA, -0.55, mia_face), (OMAR, 0.55, omar_face)):
        p = sit()
        p.update(al=(40, 4), ar=(40, 4))
        ll = spec["leg"][1] * spec["s"]
        a = character(sc, spec, (BENCH[0] + x, 0.92 - ll, BENCH[2] + 0.05), face=face, pose=p, shadow=False)
        if spec is OMAR and box:
            sc.box(T(*(a["hand_l"] + a["hand_r"]) / 2) @ T(0, 0.2, 0.25), (0.7, 0.6, 0.6), (200, 160, 110), layer=6)


def u16(t, dur):
    u = t / dur
    sc = dcam((0.3, 2.2, 6.0), (0.0, 1.6, 0.8), u, 0.04, fov=40)
    _bench(sc, t)
    return sc


def u17(t, dur):
    u = t / dur
    sc = dcam((0.0, 15.0, 16.0), (3.0, 4.0, -55.0), u, 0.12, fov=40)
    sets.town(sc)
    us.hill(sc)
    return sc


def u18(t, dur):
    u = t / dur
    sc = dcam((-3.0, 3.0, 6.0), (-3.0, 0.6, -8.0), u, 0.04, fov=46)
    us.farm(sc, t, green=0.0, truck_kw=None, boxes=False)
    return sc


def u19(t, dur):
    u = t / dur
    sc = dcam((0.0, 4.0, 0.4), (0.0, 0.0, 0.0), u, 0.16, fov=40)
    sc.ground(us.DRY)
    us.cracked(sc, T(0, 0.02, 0), w=8.0, h=8.0)
    return sc


def u20(t, dur):
    u = t / dur
    sc = dcam((0.3, 2.2, 6.0), (0.0, 2.4, 0.8), u, 0.0, fov=42)
    _bench(sc, t, "smile", "smile", box=False)
    q = dur / 3
    k = min(2, int(t / q))
    if k == 0:
        us.falling(sc, t, "pizza", n=16)
    elif k == 1:
        us.falling(sc, t, "puppies", n=12)
    else:
        def candy(d, W, H):
            import numpy as _np
            rng = _np.random.RandomState(8)
            for i in range(20):
                x, y0, sp = rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0.3, 0.5)
                y = ((y0 + t * sp) % 1.1 - 0.05) * H
                c = [(255, 90, 140), (90, 200, 255), (255, 220, 70)][i % 3]
                s = W * 0.025
                d.ellipse([x * W - s, y - s * 0.7, x * W + s, y + s * 0.7], fill=c + (255,))
                d.polygon([(x * W - s, y), (x * W - s * 1.8, y - s * 0.6), (x * W - s * 1.8, y + s * 0.6)], fill=c + (255,))
                d.polygon([(x * W + s, y), (x * W + s * 1.8, y - s * 0.6), (x * W + s * 1.8, y + s * 0.6)], fill=c + (255,))
        sc.overlay(candy)
    return sc


def u21(t, dur):
    u = t / dur
    sc = head_cu(MIA, (BENCH[0] - 0.55, 0.92 - MIA["leg"][1] * MIA["s"], BENCH[2] + 0.05), 0,
                 dict(ll=88, lr=88, head=(-30, 12, 0)), u, dist=3.0, side=0.6, fov=36)
    _bench(sc, t, "worried", "smile")
    return sc


def u22(t, dur):
    u = t / dur
    sc = head_cu(MIA, MIA_SQ, 0, None, u, dist=3.2, up=-0.6, fov=36, push=0.14)
    sets.town(sc)
    a = character(sc, MIA, MIA_SQ, face="grit", pose=dict(ar=(60, 20), er=60))
    add_emote(sc, "bulb", a["head_top"], t, size=0.6, dx=-0.5, dy=0.2, start=0.3)
    return sc


def u23(t, dur):
    u = t / dur
    sc = dcam((TRUCK_X := us.TRUCK[0]) + 1.0 - 3.0 * u, 3.4 + 2.0 * u, us.TRUCK[2] + 9.0 + 4.0 * u) if False else \
        dcam((us.TRUCK[0] - 1.0, 3.0 + 1.6 * u, us.TRUCK[2] + 11.0 + 4.0 * u), (us.TRUCK[0] - 1.6, 2.2, us.TRUCK[2] + 1.0), u, 0.0,
             fov=44, sky=((200, 220, 240), (240, 246, 255)))
    us.farm(sc, t, green=0.0, truck_kw=dict(snow=1.0), boxes=False)
    sc.ground((250, 252, 255))
    character(sc, OMAR, (us.TRUCK[0] - 4.2, 0, us.TRUCK[2] + 4.4), yaw=20, face="joy",
              pose=dict(ar=(165, -20 - 15 * math.sin(t * 10))))
    us.snow(sc, t)
    us.dreamy(sc)
    return sc


# ------------------------------------------------------- 24-29: the hill
FARM_KW = dict(green=0.0)


def _farm(sc, t, truck=True, **kw):
    args = dict(FARM_KW)
    args.update(kw)
    us.farm(sc, t, truck_kw=dict(doors_open=1.0) if truck else None, **args)


def u24(t, dur):
    u = t / dur
    z = 10.0 - 5.0 * u
    sc = dcam((-1.0, 2.6, z + 6.0), (0.0, 1.8, z), u, 0.0, fov=44)
    _farm(sc, t)
    a = character(sc, MIA, (0.0, 0, z), yaw=180, face="grit", pose=dict(walk(t, 7, 20), ar=(150, 20), er=40))
    us.umbrella(sc, T(*a["hand_r"]) @ RZ(-60) @ T(0, -0.2, 0), open_k=0.0, glow_k=0.6, t=t)
    return sc


def u25(t, dur):
    u = t / dur
    sc = dcam((us.TRUCK[0] - 6 + 4 * u, 2.6, us.TRUCK[2] + 9.0), (us.TRUCK[0] + 1.0, 1.5, us.TRUCK[2]), u, 0.0, fov=46)
    _farm(sc, t)
    for i, x in enumerate((-1.5, 0.5)):
        us.box_pile(sc, us.TRUCK[0] + x, us.TRUCK[2] + 2.5 + i, n=5, seed=i + 3)
    return sc


def u26(t, dur):
    u = t / dur
    sc = dcam((-1.4, 2.4, 6.4), (-2.4, 1.4, -6.0), u, 0.02, fov=44)
    _farm(sc, t)
    character(sc, FARMER, (-2.4, 0, -0.6), yaw=180, face="sad", pose=dict(al=(4, 2), ar=(4, 2)))
    return sc


def u27(t, dur):
    u = t / dur
    pos = (-2.4, 0, -0.6)
    sc = head_cu(FARMER, pos, 160, None, u, dist=3.0, side=-0.3, fov=36, push=0.14)
    _farm(sc, t)
    character(sc, FARMER, pos, yaw=160, face="miserable")
    return sc


OMAR_F = (1.2, 0, 2.6)


def u28(t, dur):
    u = t / dur
    sc = dfcam(OMAR_F, ht(OMAR) + 0.4, 10, u, frac=0.7, fov=40)
    _farm(sc, t)
    a = character(sc, OMAR, OMAR_F, yaw=-20, face="smile", pose=dict(al=(40, -20), ar=(40, -20), el=50, er=50))
    sc.box(T(*(a["hand_l"] + a["hand_r"]) / 2) @ T(0, -0.05, 0.3), (0.7, 0.5, 0.55), (200, 160, 110), layer=6)
    return sc


def u29(t, dur):
    u = t / dur
    pose = dict(al=(70, -20), ar=(70, -20), el=40, er=40, head=(0, -10, 0))
    sc = head_cu(OMAR, OMAR_F, -20, pose, u, dist=2.4, fov=34)
    _farm(sc, t)
    character(sc, OMAR, OMAR_F, yaw=-20, face="smile" if t < 0.3 else "sad", pose=pose)
    return sc


# ------------------------------------------------------- 30-37: the wish
MIA_F = (-0.6, 0, 3.2)


def u30(t, dur):
    u = t / dur
    sc = dcam((0.8, 0.8, 7.6), (-0.6, 2.6 + 1.2 * u, 3.2), u, 0.0, fov=44)
    _farm(sc, t)
    lift = clamp(t / 0.8)
    with_umbrella(sc, MIA, MIA_F, face="grit", open_k=0.0, t=t, glow_k=0.6 + 0.4 * lift,
                  pose=dict(ar=(90 + 80 * lift, -10)))
    return sc


def u31(t, dur):
    u = t / dur
    sc = head_cu(MIA, MIA_F, 0, HOLD_UP, u, dist=2.6, fov=34)
    _farm(sc, t)
    with_umbrella(sc, MIA, MIA_F, face="sleep", open_k=0.0, t=t)
    return sc


def u32(t, dur):
    u = t / dur
    sc = dcam((-0.4, 3.0, 5.6), (-0.6, 4.1, 3.2), u, 0.0, fov=36, bloom=0.8)
    _farm(sc, t)
    with_umbrella(sc, MIA, MIA_F, face="grit", open_k=clamp((t - 0.1) / 0.12), t=t, glow_k=1.5)
    if 0.15 <= t < 0.15 + 2 / 30:
        sc.flash = 1.0
    return sc


def u33(t, dur):
    u = t / dur
    sh = 0.08 * math.sin(t * 60) * (1 - u)
    sc = dcam((0.8 + sh, 0.7, 7.0), (-0.6, 3.0 + sh, 3.2), u, 0.0, fov=46, sky=STORM_SKY)
    _farm(sc, t)
    a = with_umbrella(sc, MIA, MIA_F, face="jaw", t=t, pose=dict(head=(0, 25, 0)))
    ls.sticker(sc, a["head"], "RAIN!", t, start=0.05, hold=1.0, size=0.7, dx=0.0, dy=1.6, color=(150, 210, 255))
    return sc


def u34(t, dur):
    u = t / dur
    sc = dcam((0.4, 2.6, 9.0), (0.0, 1.8, 1.0), u, 0.0, fov=44)
    us.square(sc, t, umbrella_on_stand=False)
    cs = crowd(sc, t, n=8, z=1.2, faces=("miserable", "sad"), poses=[dict(lean=12, head=(0, -12, 0))], yaw=0)
    for i, a in enumerate(cs[::2]):
        add_emote(sc, "sweat", a["head_top"], t, size=0.45, dx=0.3, dy=0.1, start=0.2 + 0.1 * i)
    return sc


def u35(t, dur):
    u = t / dur
    pose = dict(head=(0, 20, 0), ar=(150, -20), al=(150, -20))
    sc = head_cu(BRYCE, MIA_SQ, 0, pose, u, dist=3.2, up=-0.6, fov=36)
    us.square(sc, t, umbrella_on_stand=False)
    a = character(sc, BRYCE, MIA_SQ, face="angry", pose=pose)
    add_emote(sc, "anger", a["head_top"], t, size=0.55, dx=0.5, dy=0.05, start=0.2)
    return sc


def u36(t, dur):
    u = t / dur
    sc = dcam((0.0, 1.0, 14.0), (0.0, 4.0 + 6.0 * u, -10.0), u, 0.0, fov=46, sky=STORM_SKY)
    _farm(sc, t)
    us.storm(sc, clamp(t / 1.2), t, y=lerp(30, 16, clamp(t / 2.0)))
    us.dark_grade(sc, clamp(t / 2.0))
    return sc


def u37(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.0, 12.0), (-2.0, 1.4, -4.0), u, 0.0, fov=44, sky=STORM_SKY)
    _farm(sc, t)
    us.storm(sc, 1.0, t, y=16)
    us.rain(sc, t, 1.0)
    return sc


# ------------------------------------------------------- 38-42: the field
def u38(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.6, 0.4), (0.0, 0.0, 0.0), u, 0.16, fov=40, sky=STORM_SKY)
    sc.ground(us.DRY)
    us.cracked(sc, T(0, 0.02, 0), w=8.0, h=8.0, wet=clamp(t / 2.4))
    us.rain(sc, t, 0.8)
    return sc


def u39(t, dur):
    u = t / dur
    sweep = lerp(-13, 7, clamp(t / (dur * 0.85)))
    sc = dcam((-3.0, 4.0 + 1.5 * u, 7.0 + 3.0 * u), (-3.0, 0.6, -8.0), u, 0.0, fov=46)
    us.farm(sc, t, green=1.0, sweep=sweep, truck_kw=dict(doors_open=1.0))
    sparks(sc, (sweep, 0.8, -6.0), t, seed=3, n=6, r=1.5, color=(200, 255, 160))
    return sc


def u40(t, dur):
    """'Sprouts. Vines. Pumpkins the size of cars.' — three quick cuts."""
    starts = [0.0, word_t(40, 1, dur / 3), word_t(40, 2, 2 * dur / 3)]
    k = 0 if t < starts[1] - 0.05 else (1 if t < starts[2] - 0.05 else 2)
    tt = t - starts[k]
    if k == 0:
        sc = dcam((0.2, 0.8, 2.0), (0.0, 0.5, 0.0), 0, 0, 38)
        sc.ground((110, 80, 54))
        g = clamp(tt / 0.4)
        sc.box(T(0, 0.15 + 0.25 * g, 0), (0.06, 0.5 * g + 0.05, 0.06), (90, 170, 80), layer=5)
        for sx in (-1, 1):
            sc.blob(T(sx * 0.15 * g, 0.4 + 0.25 * g, 0) @ RZ(sx * -40), (0.3 * g + 0.01, 0.1, 0.16), (110, 190, 90),
                    layer=5, n=10, m=5)
    elif k == 1:
        sc = dcam((0.4, 1.6, 3.6), (0.0, 1.2, 0.0), 0, 0, 40)
        sc.ground((100, 150, 80))
        for i in range(14):
            a = i * 0.5 + tt * 2
            if i / 14 < clamp(tt / 0.8):
                sc.blob(T(0.5 * math.cos(a) * (1 + i * 0.05), 0.2 + i * 0.14, 0.5 * math.sin(a)), (0.18, 0.18, 0.18),
                        (80, 170, 80), layer=5, n=8, m=6)
                if i % 3 == 0:
                    sc.blob(T(0.7 * math.cos(a), 0.2 + i * 0.14, 0.7 * math.sin(a)), (0.4, 0.1, 0.3), (110, 190, 90),
                            layer=5, n=8, m=5)
    else:
        sc = dcam((us.TRUCK[0] - 3.0, 2.6, us.TRUCK[2] + 9.0), (us.TRUCK[0] - 3.0, 1.8, us.TRUCK[2]), 0, 0, 44)
        us.farm(sc, t, green=1.0, truck_kw=dict(doors_open=1.0), boxes=False)
        g = clamp(tt / 0.4)
        sc.blob(T(us.TRUCK[0] - 4.5, 0.2 + 1.2 * g, us.TRUCK[2] + 0.6), (3.6 * g, 2.6 * g, 3.4 * g), (240, 140, 40),
                e=0.8, layer=4, n=16, m=10)
        sc.box(T(us.TRUCK[0] - 4.5, 0.3 + 2.6 * g, us.TRUCK[2] + 0.6), (0.3 * g, 0.5 * g, 0.3 * g), (90, 120, 60),
               layer=4)
    return sc


def u41(t, dur):
    u = t / dur
    pos = (-2.4, 0, -0.6)
    pose = dict(al=(70, -20), ar=(70, -20), el=40, er=40) if t < 0.6 else dict(al=(30, 20), ar=(30, 20))
    sc = dfcam(pos, ht(FARMER) + 0.3, 20, u, frac=0.55, fov=40)
    us.farm(sc, t, green=1.0, pumpkins=1.0, truck_kw=dict(doors_open=1.0))
    a = character(sc, FARMER, pos, yaw=20, face="neutral" if t < 0.6 else "jaw", pose=pose)
    f = clamp((t - 0.6) / 0.35)
    bp = (a["hand_l"] + a["hand_r"]) / 2 + np.array([0, 0.15, 0.25])
    sc.box(T(*(bp + np.array([0, -bp[1] * f * f + 0.3 * f * (bp[1] > 0) * 0 + (0.33 - 0.15) * f, 0]))) @ RZ(30 * f),
           (0.75, 0.6, 0.6), (200, 160, 110), layer=6)
    add_emote(sc, "!", a["head_top"], t, size=0.6, dx=0.5, dy=0.2, start=0.65)
    return sc


def u42(t, dur):
    u = t / dur
    sc = dcam((us.TRUCK[0] - 4.0, 2.4, us.TRUCK[2] + 10.0), (us.TRUCK[0] + 2.0, 1.4, us.TRUCK[2]), u, 0.0, fov=46)
    us.farm(sc, t, green=1.0, pumpkins=1.0, truck_kw=dict(doors_open=1.0, empty=True, x=us.TRUCK[0] + 8.0 * u ** 1.5,
                                                         yaw=180), boxes=False)
    return sc


# ------------------------------------------------------- 43-46: the ending
def u43(t, dur):
    u = t / dur
    sc = dcam((0.4, 2.4, 6.4), (0.0, 1.9, 2.6), u, 0.12, fov=40, sky=STORM_SKY)
    us.farm(sc, t, green=1.0, pumpkins=1.0, truck_kw=None, boxes=False)
    hug = dict(al=(80, -30), ar=(80, -30), el=50, er=50)
    character(sc, MIA, (-0.35, 0, 2.6), yaw=75, face="joy", pose=hug)
    b = character(sc, OMAR, (0.35, 0, 2.6), yaw=-75, face="joy", pose=hug)
    us.rain(sc, t, 0.6)
    add_emote(sc, "stars", b["head_top"] + np.array([-0.35, 0.1, 0]), t, size=0.55, dy=0.2, start=0.3)
    return sc


def u44(t, dur):
    u = t / dur
    sc = dcam((-2.0 + 3.0 * u, 2.8, 7.6), (-0.5 + 2.0 * u, 1.8, -0.8), u, 0.0, fov=44)
    us.farm_stand(sc, t)
    character(sc, FARMER, (0.0, 0, -2.2), face="grin", pose=dict(ar=(60, 20)))
    for i, x in enumerate((-2.6, -1.4, 1.6, 2.8)):
        character(sc, crowd_spec(i + 12, adult=i % 2 == 0), (x, 0, 0.6 + 0.3 * (i % 2)), yaw=180 + 20 * (i - 1.5),
                  face="joy", pose=dict(ar=(60, 20)))
    sparks(sc, (0.0, 2.0, -0.5), t, seed=2, n=5, r=1.0)
    return sc


def u45(t, dur):
    u = t / dur
    pose = dict(ar=(70, -10), er=50)
    sc = head_cu(BRYCE, (0, 0, 0.6), 0, pose, u, dist=3.2, fov=36)
    us.farm_stand(sc, t)
    a = character(sc, BRYCE, (0, 0, 0.6), face="suspicious", pose=pose)
    us.carrot(sc, T(*(a["hand_r"] + np.array([0, 0.25, 0.05]))) @ RZ(-20))
    add_emote(sc, "?", a["head_top"], t, size=0.55, dx=0.5, dy=0.2, start=0.2)
    return sc


def u46(t, dur):
    u = t / dur
    pose = dict(ar=(80, -20), er=60, al=(80, -20), el=60)
    sc = head_cu(BRYCE, (0, 0, 0.6), 0, pose, u, dist=3.4, fov=34)
    us.farm_stand(sc, t)
    a = character(sc, BRYCE, (0, 0, 0.6), face="chew0" if int(t * 8) % 2 else "chew1", pose=pose)
    us.veggie_pizza(sc, T(*((a["hand_l"] + a["hand_r"]) / 2 + np.array([0, -0.1, 0.25]))) @ RX(-35) @ us.S(0.55))
    return sc


_FNS = [globals()[f"u{i:02d}"] for i in range(1, len(LINES) + 1)]
SHOTS = [(i + 1, 1.4, txt, fn) for i, (txt, fn) in enumerate(zip(LINES, _FNS))]
SHOTS, WORD_TIMES = load_timing(SHOTS, TIMING_FILE)
WT.update(WORD_TIMES)
