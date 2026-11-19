"""The Birthday Wish: shot list. Each shot: (number, seconds, caption text, fn(t, dur) -> Scene)."""
import os

TIMING_FILE = "wish_timing.json"
SILENT = {52: 0.7}
SPOKEN = {"10": "ten", "16": "sixteen", "400": "four hundred", "Mr": "mister", "pyjamas": "pajamas"}
PHONES = {"finn": "F IH N", "olsen": "OW L S AH N", "leo": "L IY OW", "jetpack": "JH EH T P AE K",
          "loophole": "L UW P HH OW L", "unicorns": "Y UW N AH K AO R N Z"}

LINES = [
    "In this town, when you turn 10, you get ONE wish.",
    "But there's a catch.",
    "You have to wish for someone ELSE.",
    "And every wish comes with a twist.",
    "Mom wished for Dad to be a great cook.",
    "Now he can't STOP cooking.",
    "We have lasagna for breakfast.",
    "Mr Olsen wished his dog could talk.",
    "The dog won't stop talking about squirrels.",
    "I'm Finn.",
    "Tomorrow, I turn 10.",
    "And I found a loophole.",
    "I'll wish for my dog, Waffles, to get a JETPACK.",
    "Then I'll borrow it. Every day.",
    "My big brother Leo is 16.",
    "He used his wish six years ago.",
    "He never told anyone what he wished for.",
    "Mom asked.",
    "Dad asked.",
    "I asked 400 times.",
    "He just shrugs.",
    "Oh, and one more thing.",
    "I've never had a bad dream. Not ONE.",
    "Everyone in my class has nightmares.",
    "Me? Unicorns.",
    "Pizza clouds.",
    "Every single night.",
    "The night before my birthday, I couldn't sleep.",
    "Then I heard something from Leo's room.",
    "Mumbling.",
    "Tossing. Turning.",
    "I peeked in.",
    "Leo was having a nightmare. A BIG one.",
    "Then I saw a note taped above his bed.",
    "Old. Written in crayon.",
    "My wish: Finn never has a bad dream again.",
    "Mom told me once: when I was four, I had nightmares every night.",
    "I don't remember them.",
    "Leo does.",
    "He didn't just give me good dreams. He took my BAD ones.",
    "For six years.",
    "The next morning, the whole family stood around the Wish Candle.",
    "Waffles was already wearing a helmet.",
    "JETPACK! JETPACK! everyone chanted.",
    "I closed my eyes.",
    "I wish Leo never has a bad dream again.",
    "The flame turned GOLD.",
    "Leo stared at me.",
    "He didn't say anything.",
    "He just hugged me. Hard.",
    "That night, Leo slept twelve hours straight.",
    "",
    "Waffles still wants a JETPACK.",
]
import math  # noqa: E402

import numpy as np  # noqa: E402

import laughs_sets as ls  # noqa: E402
import porch_sets as ps  # noqa: E402
import sets  # noqa: E402
import wish_sets as ws  # noqa: E402
from cast import ABERNATHY, BRAX, DAD, HERO, MOM, PIP, TUCK, character, crowd_spec, sit  # noqa: E402
from engine import RX, RY, RZ, T, add_emote, clamp, lerp, speed_lines, xf  # noqa: E402
from laughs import bob, dcam, dfcam, head_cu, ht, laugh_pose  # noqa: E402
from porch import fwd_of, ncam, win_pos  # noqa: E402
from shots import probe, sparks, walk  # noqa: E402
from story import load_timing  # noqa: E402

FINN = HERO
FINN_PJ = dict(HERO, shirt=(170, 196, 246), arm_shirt=(140, 170, 236), pants=(140, 170, 236))
LITTLE_FINN = dict(FINN_PJ, s=0.6, head=(0.9, 0.86, 0.9))
LEO = dict(TUCK, name="Leo", s=1.18)
YOUNG_LEO = dict(TUCK, name="Young Leo", s=0.95)
MOM_W = dict(MOM, boots=0, shoes=(240, 240, 240))
DAD_CHEF = dict(DAD, style="chef")
OLSEN = dict(ABERNATHY, name="Mr Olsen", glasses=False, shirt=(110, 140, 100), inner=(240, 230, 210),
             hair=(200, 200, 206), bushy=(210, 210, 216))
KID, FRIEND = dict(crowd_spec(5), name="Birthday kid"), dict(crowd_spec(2), name="Friend")
WAFFLES = (196, 140, 90)
OLSEN_DOG = dict(fur=(240, 240, 240), spots=(60, 60, 64))
NIGHT_IN = dict(sky=ps.NIGHT_SKY, night=0.75)
WT = {}


def word_t(num, i, default=0.0):
    w = WT.get(num, [])
    return w[i][0] if i < len(w) else default


def ncam_room(pos, tgt, u, push=0.1, fov=40, blue=0.25, **kw):
    """Night interior camera: moonlit, slight blue grade."""
    kw.setdefault("mood", NIGHT_IN)
    kw.setdefault("bloom", 0.9)
    if blue:
        kw.setdefault("grade", "blue")
        kw.setdefault("gmix", blue)
    return ncam(pos, tgt, u, push, fov, **kw)


def in_bed(sc, spec, bx, bz, face, t=0.0, toss=0.0, blanket=(110, 170, 240), hug_dog=False):
    """Character lying in sets.bed(bx, bz): head on the pillow, blanket over the body."""
    s = spec["s"]
    hh = spec["head"][1] * s
    feet_z = bz - 1.45 + ht(spec) - hh / 2
    roll = toss * math.sin(t * 9)
    a = character(sc, spec, (bx, 1.2, feet_z), face=face, shadow=False,
                  pose=dict(lean=-90, roll=roll, al=(10, 6), ar=(10, 6), head=(roll * 0.8, 0, 0)))
    tz = bz - 1.45 + hh / 2 + 0.25
    sc.box(T(bx, 1.32, (tz + bz + 2.0) / 2) @ RZ(roll * 0.5), (2.3, 0.4, bz + 2.0 - tz), blanket, layer=6)
    if hug_dog:
        ls.dog(sc, T(bx + 0.7, 1.2, bz - 0.6) @ RY(-60) @ RZ(70), 0, fur=WAFFLES, hat=False)
    return a


def bed_cam(bx, bz, u, push=0.12, fov=40, high=3.8, side=1.2, back=3.6, **kw):
    return ncam_room((bx + side, high, bz + back), (bx, 1.25, bz - 1.2), u, push, fov, **kw)


def sub(t, starts):
    """Index of the quick sub-cut that time t falls in."""
    k = 0
    for i, s0 in enumerate(starts):
        if t >= s0 - 0.03:
            k = i
    return k


# ------------------------------------------------------- 1-9: the rule
def w01(t, dur):
    u = t / dur
    sc = dcam((0.3, 3.3, 2.6), (0.0, 2.85, 0.0), u, 0.14, fov=36, bloom=0.8)
    ws.party_room(sc, t)
    lit = clamp((t - 0.4) / 0.25)
    tips = ws.cake(sc, T(0, 1.42, 0), t, "10", lit)
    if lit > 0:
        for i, p in enumerate(tips):
            sparks(sc, p + np.array([0, 0.15, 0]), t, seed=i, n=4, r=0.2, color=(255, 220, 120))
    return sc


def w02(t, dur):
    u = t / dur
    pos = (0, 0, -1.4)
    sc = dcam((2.6, 2.6, 0.9), (0.0, 2.3, -1.3), u, 0.08, fov=38)
    ws.party_room(sc, t)
    ws.cake(sc, T(0, 1.42, 0), t, "10", 1.0)
    a = character(sc, KID, pos, face="sleep", pose=dict(lean=12, al=(10, 6), ar=(10, 6)))
    add_emote(sc, "!", a["head_top"], t, size=0.6, dx=0.55, dy=0.25, start=0.08)
    return sc


def w03(t, dur):
    u = t / dur
    sc = dcam((0.2, 2.4, 6.0), (0.0, 2.0, -1.4), u, 0.12, fov=40)
    ws.party_room(sc, t)
    ws.cake(sc, T(0, 1.42, 0), t, "10", 0.0)
    character(sc, KID, (-0.9, 0, -1.4), yaw=40, face="grin", pose=dict(ar=(90, -8), al=(10, 6)))
    b = character(sc, FRIEND, (1.0, 0, -1.4), yaw=-30, face="shock", pose=dict(al=(30, 30), ar=(30, 30)))
    add_emote(sc, "?", b["head_top"], t, size=0.6, dx=0.4, dy=0.25, start=0.3)
    return sc


def w04(t, dur):
    u = t / dur
    sc = dcam((-6.0 + 5.0 * u, 3.0, 9.0), (-3.0 + 5.0 * u, 2.6, -4.0), u, 0.0, fov=46)
    sets.town(sc)
    # odd wishes: a floating kid, a giant sunflower, a rain cloud over one house, a dog on a roof
    character(sc, crowd_spec(7), (-6.5, 3.2 + bob(t, 0.15), 0.5), face="joy", pose=dict(al=(160, -20), ar=(160, -20)),
              shadow_y=0)
    for x, c in ((-6.3, (255, 90, 120)), (-6.8, (90, 190, 255))):
        ls.balloon(sc, x, 6.5, 0.4, c, t, string=1.6)
    ps.sunflower(sc, 0.8, -2.0, 5.0, 1.0)
    for dx in (-0.8, 0.0, 0.9):
        sc.blob(T(6.5 + dx, 8.4, -8.0), (1.8, 1.0, 1.4), (150, 160, 180), layer=2)

    def rain(d, x, y, s, col):
        for i in range(12):
            xx = x + (i - 6) * 0.25 * s
            yy = y + ((t * 3 + i * 0.37) % 1.0) * 1.5 * s
            d.line([(xx, yy), (xx - 0.04 * s, yy + 0.2 * s)], fill=(120, 170, 255, 220), width=max(2, int(s * 0.03)))
    sc.sprite((6.5, 7.6, -8.0), rain, layer=8, live=True)
    ls.dog(sc, T(-13.0, 5.2, -8.0) @ RY(20), t, fur=(200, 150, 100), hat=False)
    sparks(sc, (0.8, 5.5, -2.0), t, seed=5, n=5, r=0.8)
    return sc


def w05(t, dur):
    u = t / dur
    sc = dcam((0.3, 2.8, 7.0), (0.0, 2.4, -1.2), u, 0.08, fov=40)
    sets.kitchen(sc)
    m = character(sc, MOM_W, (-0.9, 0, -1.6), yaw=30, face="joy", pose=dict(al=(30, 20), ar=(30, 20)))
    character(sc, DAD_CHEF, (1.0, 0, -1.6), yaw=-25, face="grin", pose=dict(ar=(100, -10), er=40))
    add_emote(sc, "stars", m["head_top"], t, size=0.5, dx=0.4, dy=0.2, start=0.4)
    return sc


def _kitchen_mess(sc, t):
    sets.kitchen(sc)
    rng = np.random.RandomState(4)
    for i in range(14):
        x, z = rng.uniform(-1.4, 1.4), rng.uniform(-0.8, 0.8)
        h = 1.25
        for k in range(rng.randint(1, 4)):
            r = rng.uniform(0.25, 0.45)
            c = [(170, 176, 190), (210, 80, 70), (90, 120, 200), (240, 200, 90)][rng.randint(4)]
            ws.pot(sc, T(x, h, z), r=r, h=0.3, color=c)
            h += 0.32
    for x in (-3.0, 3.0):
        for k in range(5):
            sc.blob(T(x, 0.3 + k * 0.5, -2.5), (0.9 - k * 0.1, 0.45, 0.9 - k * 0.1),
                    [(240, 190, 90), (200, 90, 60), (250, 240, 210), (120, 180, 90)][k % 4], layer=3)
    for i, x in enumerate((-1.0, 0.0, 1.0)):
        ws.steam(sc, (x, 2.2, 0.0), t + i * 0.3)


def w06(t, dur):
    u = t / dur
    sc = dcam((0.6, 3.4, 8.5), (0.0, 1.8, -0.6), u, 0.25, fov=44)
    _kitchen_mess(sc, t)
    character(sc, DAD_CHEF, (2.2, 0, -1.6), yaw=-30, face="sparkle",
              pose=dict(ar=(80 + 30 * math.sin(t * 14), -10), al=(80 - 30 * math.sin(t * 14), -10), er=40, el=40))
    return sc


def w07(t, dur):
    u = t / dur
    sc = dcam((0.4, 3.4, 5.6), (0.0, 2.3, -0.6), u, 0.08, fov=40)
    sets.kitchen(sc)
    ws.lasagna(sc, T(0, 1.25, 0.3), s=0.85)
    a = character(sc, FINN_PJ, (0.0, 0, -1.3), face="worried", pose=dict(al=(5, 4), ar=(5, 4)))
    add_emote(sc, "sweat", a["head_top"], t, size=0.5, dx=0.55, dy=0.05, start=0.3)
    return sc


OLSEN_PORCH = (0.0, 0.3, 0.7)


def _olsen_home(sc):
    sc.ground(sets.GRASS)
    sets.clouds(sc, seed=4)
    sets.flat(sc, -60, 60, 4.5, 8.0, (88, 92, 108))
    sets.flat(sc, -60, 60, 3.3, 4.5, (220, 214, 204))
    ps.porch_house(sc, 0, -2.0, (240, 200, 120), k=0, lamp_k=0, glass=ls.DAY_GLASS)
    sets.bush(sc, -2.6, 0.6, 0.8)
    sets.tree(sc, 4.5, -0.5, 4.4)


def w08(t, dur):
    u = t / dur
    sc = dfcam(OLSEN_PORCH, ht(OLSEN), 10, u, frac=0.5, fov=40, push=0.12)
    _olsen_home(sc)
    character(sc, OLSEN, (-0.3, 0.3, 0.7), yaw=15, face="smile", pose=dict(ar=(30, 30)))
    ls.dog(sc, T(0.9, 0.3, 0.9) @ RY(-20), t, hat=False, **OLSEN_DOG)
    return sc


def w09(t, dur):
    u = t / dur
    sc = dcam((0.6, 3.1, 6.6), (0.2, 2.8, 0.7), u, 0.06, fov=40)
    _olsen_home(sc)
    character(sc, OLSEN, (-0.4, 0.3, 0.6), yaw=20, face="miserable",
              pose=dict(al=(170, -50), ar=(170, -50), el=95, er=95, head=(0, -6, 0)))
    head = ls.dog(sc, T(0.9, 0.3, 1.0) @ RY(-25), t, hat=False, mood="talk", **OLSEN_DOG)
    ws.speech_lines(sc, head + np.array([0.2, -0.2, 0.3]), t, side=1)
    ws.squirrel_sticker(sc, head + np.array([0.6, 0.9, 0.0]), t, start=0.2, size=0.9)
    return sc


# ------------------------------------------------------- 10-14: Finn's plan
FROOM = (0.4, 0, -1.2)


def w10(t, dur):
    u = t / dur
    sc = head_cu(FINN, FROOM, 0, None, u, dist=3.4, up=-0.5, fov=36)
    ps.nova_room(sc, lamp_k=0.4, day=True, wall=(170, 210, 160))
    a = character(sc, FINN, FROOM, face="grin", pose=dict(ar=(40, 20)))
    sparks(sc, a["head_top"] + np.array([0.5, 0.0, 0]), t, seed=6, n=4, r=0.3)
    return sc


def w11(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.0, 1.2), (0.0, 3.0, -3.0), u, 0.18, fov=38)
    ps.nova_room(sc, lamp_k=0.4, day=True, wall=(170, 210, 160))
    ws.calendar(sc, T(0.0, 3.0, -3.0))
    return sc


def w12(t, dur):
    u = t / dur
    rub = 6 * math.sin(t * 18)
    pose = dict(al=(55, -18 + rub), ar=(55, -18 - rub), el=60, er=60)
    sc = head_cu(FINN, FROOM, 0, pose, u, dist=3.6, up=0.0, fov=36)
    ps.nova_room(sc, lamp_k=0.4, day=True, wall=(170, 210, 160))
    a = character(sc, FINN, FROOM, face="smirk", pose=pose)
    add_emote(sc, "bulb", a["head_top"], t, size=0.6, dx=-0.5, dy=0.2, start=0.4)
    return sc


def w13(t, dur):
    u = t / dur
    sc = dcam((0.6, 2.4, 6.0), (0.4, 2.0, -1.2), u, 0.1, fov=40)
    ps.nova_room(sc, lamp_k=0.4, day=True, wall=(170, 210, 160))
    a = character(sc, FINN, FROOM, face="sparkle", pose=dict(al=(150, -10), ar=(150, -10), el=10, er=10))
    c = (a["hand_l"] + a["hand_r"]) / 2 + np.array([0, 0.45, 0.12])
    ws.jetpack_drawing(sc, T(*c), w=1.3, h=1.0)
    ls.dog(sc, T(1.6, 0, -0.6) @ RY(-30), t, fur=WAFFLES, hat=False)

    def fire(d, x, y, s, col):
        for i, c_ in enumerate(((255, 120, 40), (255, 210, 60))):
            r = (0.22 - i * 0.08) * s
            d.polygon([(x - r, y), (x, y - r * 2.4 + math.sin(t * 20) * r * 0.2), (x + r, y), (x, y + r * 0.6)],
                      fill=c_ + (255,))
    if t > 0.4:
        sc.sprite(c + np.array([0.7, 0.5, 0.1]), fire, layer=8, live=True)
    return sc


def w14(t, dur):
    u = t / dur
    fx = -6.0 + 7.0 * u
    sc = dcam((fx - 1.4, 7.4, 6.0), (fx, 7.2, 0.5), u, 0.0, fov=46)
    sets.town(sc)
    a = character(sc, FINN, (fx, 6.0 + bob(t, 0.2, 3), 0.5), yaw=90, face="laugh",
                  pose=dict(lean=25, al=(150, -30), ar=(150, -30), ll=20, lr=-10), shadow_y=0)
    ws.jetpack(sc, a["Mt"] @ T(0, 0, -0.45) @ RX(-25 - 0 * u), t)
    ls.dog(sc, T(fx - 3.0, 0, 1.2) @ RY(60), t, fur=WAFFLES, hat=False, mood="sad")
    speed_lines(sc, t, cx=0.5, cy=0.35, n=18, inner=0.35, alpha=110)

    def dreamy(d, W, H):
        for i in range(12, 0, -1):
            d.rectangle([0, 0, W, H], outline=(255, 255, 255, 14), width=int(W * 0.012 * i))
    sc.overlay(dreamy)
    return sc


# ---------------------------------------------------- 15-21: Leo's secret
COUCH_SEAT = 0.95


def _leo_couch(sc, t, face="smile", pose=None):
    ws.living_room(sc)
    p = sit()
    p.update(al=(30, 6), ar=(30, 6), head=(0, 4 * math.sin(t * 3), 0))
    p.update(pose or {})
    ll = LEO["leg"][1] * LEO["s"]
    return character(sc, LEO, (0.0, COUCH_SEAT - ll, -1.6), face=face, pose=p, shadow=False)


def w15(t, dur):
    u = t / dur
    sc = dcam((0.4, 2.6, 5.2), (0.0, 2.1, -1.6), u, 0.04, fov=40)
    _leo_couch(sc, t, "smile")
    return sc


def w16(t, dur):
    u = t / dur
    sc = dcam((0.5, 3.7, 3.2), (0.0, 2.3, -1.2), u, 0.12, fov=40, grade="sepia", gmix=0.45)
    ws.party_room(sc, t)
    ws.cake(sc, T(0, 1.42, 0), t, "10", 1.0)
    character(sc, YOUNG_LEO, (0, 0, -1.3), face="sleep", pose=dict(lean=12))
    ws.photo_border(sc)
    return sc


def w17(t, dur):
    u = t / dur
    zip_k = clamp((t - 0.5) / 0.6)
    pose = dict(ar=(120, -36), er=95, al=(30, 6))
    sc = dcam((0.3, 2.3, 1.6), (0.0, 2.05, -1.6), u, 0.08, fov=36)
    a = _leo_couch(sc, t, "smirk" if zip_k > 0.5 else "smile", pose)
    return sc


def w18(t, dur):
    u = t / dur
    sc = dfcam((0, 0, -1.0), ht(MOM_W), 0, u, frac=0.6, fov=40)
    sets.kitchen(sc)
    a = character(sc, MOM_W, (0, 0, -1.0), face="suspicious", pose=dict(al=(15, 45), ar=(15, 45), el=-70, er=-70))
    add_emote(sc, "?", a["head_top"], t, size=0.55, dx=0.5, dy=0.2, start=0.05)
    return sc


def _ladle(sc, M):
    sc.box(M @ T(0, 0.45, 0), (0.05, 0.9, 0.05), (200, 204, 212), layer=7)
    sc.blob(M @ T(0, 0.95, 0.08), (0.26, 0.14, 0.26), (200, 204, 212), layer=7, n=10, m=6)


def w19(t, dur):
    u = t / dur
    sc = dfcam((0, 0, -1.0), ht(DAD_CHEF) + 0.8, 0, u, frac=0.62, fov=40)
    sets.kitchen(sc)
    a = character(sc, DAD_CHEF, (0, 0, -1.0), face="suspicious", pose=dict(ar=(70, -10), er=50))
    _ladle(sc, T(*a["hand_r"]))
    add_emote(sc, "?", a["head_top"], t, size=0.55, dx=-0.5, dy=0.2, start=0.05)
    return sc


def w20(t, dur):
    """'I asked 400 times': four quick cuts."""
    q = dur / 4
    k = min(3, int(t / q))
    tt = t - k * q
    if k == 0:  # at the door
        sc = ncam_room((0.2, 2.2, 4.0), (0.0, 2.0, -2.0), 0, 0, 40, blue=0, mood=dict(sky=ls.SKY, night=0.0), bloom=0)
        ws.hallway_door(sc, 0.0)
        a = character(sc, FINN, (0.6, 0, -1.8), yaw=200, face="grin", pose=dict(ar=(100, -20), er=60))
    elif k == 1:  # at breakfast
        sc = dcam((0.3, 2.6, 4.6), (0.0, 2.0, -1.4), 0, 0, 40)
        sets.kitchen(sc)
        ws.lasagna(sc, T(0, 1.25, 0.2), s=0.9)
        a = character(sc, FINN_PJ, (0.2, 0, -1.4), face="grin", pose=dict(ar=(60, 20)))
    elif k == 2:  # upside down on the couch
        sc = dcam((0.3, 2.0, 4.4), (0.0, 1.4, -1.6), 0, 0, 40)
        ws.living_room(sc)
        a = character(sc, FINN, (0.0, 3.3, -1.5), face="grin", pose=dict(lean=180, al=(20, 20), ar=(20, 20)),
                      shadow=False)
        a["head_top"] = a["head"] + np.array([0, -0.6, 0])
    else:  # through the window
        sc = dcam((0.3, 2.5, 2.8), (0.0, 2.35, -0.5), 0, 0, 36)
        sc.ground(sets.GRASS)
        ps.facade(sc, ls.HOME_COLOR, open_k=1.0, room_k=0.3, lamp_k=0.0, win_y=2.4)
        a = character(sc, FINN, win_pos(FINN, 2.4), face="grin")
    add_emote(sc, "?", a["head_top"], tt, size=0.6, dx=0.5, dy=0.15, start=0.0, hold=q)
    return sc


def w21(t, dur):
    u = t / dur
    k = clamp((t - 0.25) / 0.2) * (1 - clamp((t - 1.2) / 0.3))
    sc = dcam((0.3, 2.3, 1.7), (0.0, 2.0, -1.6), u, 0.04, fov=38)
    _leo_couch(sc, t, "smirk", dict(al=(25, 40 * k), ar=(25, 40 * k), el=-60 * k, er=-60 * k, head=(0, 0, 8 * k)))
    return sc


# ------------------------------------------------------- 22-27: the clue
def w22(t, dur):
    u = t / dur
    turn = clamp(t / 0.6)
    sc = head_cu(FINN, FROOM, 0, None, u, dist=3.2, up=0.0, push=0.12)
    ps.nova_room(sc, lamp_k=0.4, day=True, wall=(170, 210, 160))
    character(sc, FINN, FROOM, yaw=lerp(70, 0, turn), face="smile", pose=dict(head=(lerp(30, 0, turn), 0, 0)))
    return sc


def w23(t, dur):
    u = t / dur
    sc = bed_cam(-2.6, -0.6, u, push=0.14)
    ps.nova_room(sc, lamp_k=0.1)
    a = in_bed(sc, FINN_PJ, -2.6, -0.6, "sleep", t)
    add_emote(sc, "zzz", a["head"], t, size=0.6, dx=0.5, dy=0.6, start=0.2, hold=3.0)
    return sc


def w24(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.8, 8.6), (0.0, 1.6, -1.0), u, 0.06, fov=44)
    ls.classroom_ceiling(sc)
    sets.class_desks(sc, faces=("miserable", "sad", "miserable"))
    for i, (x, z) in enumerate(((-4.2, 1.2), (1.4, 1.2), (4.2, -1.2))):
        add_emote(sc, "sweat", (x, 2.1, z), t, size=0.4, dx=0.3, dy=0.1, start=0.2 + 0.2 * i, hold=2.0)
    return sc


DREAM_SKY = ((255, 200, 230), (200, 220, 255))


def w25(t, dur):
    u = t / dur
    sc = dcam((1.4, 3.6, 8.0), (0.0, 2.6, 0.0), u, 0.08, fov=42, sky=DREAM_SKY)
    ws.pastel_clouds(sc, seed=2, n=9, t=t)
    ws.rainbow(sc, (0.0, -2.0, -14.0), r=9.0)
    M = T(0, 0.4 + bob(t, 0.25, 3), 0) @ RY(80)
    ws.unicorn(sc, M, t)
    ll = FINN_PJ["leg"][1]
    character(sc, FINN_PJ, xf(M, (0, 1.6 - ll * 0.55, 0.1)), yaw=80, face="joy",
              pose=dict(ll=70, lr=70, al=(150, -20), ar=(40, 20)), shadow=False)
    sparks(sc, (0.5, 4.2, 0.5), t, seed=8, n=6, r=1.0)
    return sc


def w26(t, dur):
    u = t / dur
    sc = dcam((-3.0 + 4.0 * u, 4.0, 10.0), (-1.0 + 3.0 * u, 3.0, 0.0), u, 0.0, fov=46, sky=DREAM_SKY)
    ws.pastel_clouds(sc, seed=5, n=10, pizza=True, t=t)
    character(sc, FINN_PJ, (0.5, 2.0 + bob(t, 0.2, 2), 0.5), yaw=20, face="laugh",
              pose=dict(lean=-20, al=(150, -30), ar=(150, -30), ll=20, lr=-10), shadow=False)
    return sc


def w27(t, dur):
    u = t / dur
    sc = bed_cam(-2.6, -0.6, u, push=0.08)
    ps.nova_room(sc, lamp_k=0.1)
    a = in_bed(sc, FINN_PJ, -2.6, -0.6, "joy", t, hug_dog=True)
    add_emote(sc, "stars", a["head"], t, size=0.6, dx=0.5, dy=0.6, start=0.2, hold=1.6)
    return sc


# ------------------------------------------------------- 28-36: the night
def w28(t, dur):
    u = t / dur
    sc = ncam_room((-2.4, 5.6, 2.6), (-2.6, 1.2, -1.6), u, 0.12, fov=40, blue=0.4)
    ps.nova_room(sc, lamp_k=0.0)
    in_bed(sc, FINN_PJ, -2.6, -0.6, "neutral", t)

    def tick(d, W, H):
        pass
    return sc


def w29(t, dur):
    u = t / dur
    sc = ncam_room((-0.2, 2.8, 4.0), (-2.6, 2.0, -1.2), u, 0.06, fov=40, blue=0.4)
    ps.nova_room(sc, lamp_k=0.0)
    ll = FINN_PJ["leg"][1]
    p = sit()
    p.update(head=(-30, 0, 10), al=(150, -40), el=100)
    a = character(sc, FINN_PJ, (-2.6, 1.15 - ll, -1.4), yaw=-30, face="suspicious", pose=p, shadow=False)
    sc.box(T(-2.6, 1.3, 0.3), (2.3, 0.4, 2.8), (110, 170, 240), layer=6)
    add_emote(sc, "!", a["head_top"], t, size=0.6, dx=0.5, dy=0.2, start=0.3)
    return sc


def w30(t, dur):
    u = t / dur
    sc = ncam_room((0.4, 1.3, 2.8), (0.0, 1.2, -3.0), u, 0.0, fov=40, blue=0.45, bloom=1.3)
    ws.hallway_door(sc, 1.0 + 0.3 * math.sin(t * 20))
    return sc


def w31(t, dur):
    """'Tossing. Turning.': two quick cuts of Leo's blanket thrashing."""
    k = sub(t, [0.0, word_t(31, 1, dur / 2)])
    room = ws.leo_room
    if k == 0:
        sc = ncam_room((1.6, 2.6, 2.4), (0.0, 1.3, -0.4), 0, 0, 40, blue=0.4)
    else:
        sc = ncam_room((-1.5, 2.2, 1.8), (0.0, 1.3, -0.8), 0, 0, 40, blue=0.4)
    room(sc)
    in_bed(sc, LEO, 0.0, -0.6, "effort", t, toss=18, blanket=(70, 110, 170))
    return sc


def _door_crack(sc, k=1.0):
    def fn(d, W, H):
        g = int(W * (0.36 - 0.06 * k))
        d.rectangle([0, 0, g, H], fill=(14, 12, 20, 255))
        d.rectangle([W - g, 0, W, H], fill=(14, 12, 20, 255))
        d.rectangle([g - 6, 0, g, H], fill=(60, 50, 40, 255))
    sc.overlay(fn)


def w32(t, dur):
    u = t / dur
    sc = ncam_room((3.2, 2.4, 4.0), (0.0, 1.4, -1.0), u, 0.14, fov=40, blue=0.45)
    ws.leo_room(sc)
    in_bed(sc, LEO, 0.0, -0.6, "effort", t, toss=10, blanket=(70, 110, 170))
    _door_crack(sc, u)
    return sc


def w33(t, dur):
    u = t / dur
    sc = ncam_room((1.2, 3.8, 3.2), (0.0, 1.3, -1.6), u, 0.14, fov=40, blue=0.45)
    ws.leo_room(sc)
    a = in_bed(sc, LEO, 0.0, -0.6, "effort", t, toss=14, blanket=(70, 110, 170))
    add_emote(sc, "sweat", a["head"], t, size=0.5, dx=0.4, dy=0.5, start=0.3, hold=2.6)
    ws.shadow_overlay(sc, clamp(t / 0.6), t)
    return sc


def w34(t, dur):
    u = t / dur
    note = np.array([0.0, 2.7, -2.96])
    sc = ncam_room((1.0, 2.3, 2.8), np.array([0.0, 1.3 + 1.5 * u, -2.6]), u, 0.0, fov=40, blue=0.35)
    ws.leo_room(sc)
    in_bed(sc, LEO, 0.0, -0.6, "worried", t, toss=4, blanket=(70, 110, 170))
    ws.crayon_note(sc, T(*note) @ RZ(3), ["MY WISH:", "FINN NEVER HAS", "A BAD DREAM AGAIN"], w=1.0, h=0.8)
    return sc


NOTE_LINES = ["MY WISH:", "FINN NEVER HAS", "A BAD DREAM", "AGAIN"]


def w35(t, dur):
    u = t / dur
    sc = ncam_room((0.1, 2.75, -0.1), (0.0, 2.7, -2.96), u, 0.15, fov=40, blue=0.25, bloom=0.4)
    ws.leo_room(sc)
    ws.crayon_note(sc, T(0.0, 2.7, -2.96) @ RZ(3), NOTE_LINES, w=1.0, h=0.8)
    return sc


def w36(t, dur):
    u = t / dur
    sc = dcam((0.0, 0.0, 10.0), (0.0, 0.3, 0.0), u, 0.1, fov=38, sky=((30, 30, 40), (30, 30, 40)), bloom=0.6)
    sc.light((0, 1.0, 5.0), (255, 236, 200), 420, 2.0)
    ws.crayon_note(sc, T(0, 0, 0) @ RZ(2), NOTE_LINES, w=3.6, h=3.6)
    ls.glow_at(sc, (0, 0.2, 0.1), 3.2, (255, 236, 180), 30)
    return sc


# ------------------------------------------------------- 37-41: the reveal
def w37(t, dur):
    u = t / dur
    sc = ncam_room((-0.4, 3.0, 5.4), (-1.9, 1.5, -0.4), u, 0.12, fov=44, blue=0, grade="sepia", gmix=0.5, fill=0.5)
    ps.nova_room(sc, lamp_k=0.7)
    a = in_bed(sc, LITTLE_FINN, -2.6, -0.6, "cry", t, toss=6)
    character(sc, YOUNG_LEO, (-0.9, 0, 1.4), yaw=-120, face="worried")
    add_emote(sc, "sweat", a["head"], t, size=0.4, dx=0.3, dy=0.4, start=0.4, hold=3.5)
    return sc


DOOR = (3.4, 0, 1.4)


def w38(t, dur):
    u = t / dur
    sc = head_cu(FINN_PJ, DOOR, -120, None, u, dist=3.2, side=0.3, fov=36, mood=NIGHT_IN, bloom=0.9,
                 grade="blue", gmix=0.2, fill=0.7)
    ws.leo_room(sc)
    character(sc, FINN_PJ, DOOR, yaw=-120, face="shock")
    return sc


def w39(t, dur):
    u = t / dur
    sc = bed_cam(0.0, -0.6, u, push=0.06, back=2.6, side=0.8, high=3.2, blue=0.35)
    ws.leo_room(sc)
    in_bed(sc, LEO, 0.0, -0.6, "angry", t, toss=3, blanket=(70, 110, 170))
    return sc


def w40(t, dur):
    u = t / dur
    sc = ncam_room((1.0, 3.3, 6.4), (1.0, 1.8, -0.2), u, 0.12, fov=44, blue=0.3, fill=0.5)
    ws.leo_room(sc)
    a = in_bed(sc, LEO, 0.0, -0.6, "angry", t, toss=5, blanket=(70, 110, 170))
    character(sc, FINN_PJ, (2.0, 0, 0.9), yaw=-120, face="stung")
    ws.dark_cloud(sc, a["head"] + np.array([0, 1.1, 0]), t, clamp(t / 0.5))
    return sc


def w41(t, dur):
    u = t / dur
    sc = head_cu(FINN_PJ, DOOR, -120, None, u, dist=2.4, side=0.2, fov=34, mood=NIGHT_IN, bloom=0.9,
                 grade="blue", gmix=0.2, fill=0.7)
    ws.leo_room(sc)
    a = character(sc, FINN_PJ, DOOR, yaw=-120, face="stung")
    add_emote(sc, "tears", a["head_top"], t, size=0.6, dx=0.0, dy=-0.25, start=0.3)
    return sc


# ------------------------------------------------------- 42-50: the wish
def _wish_table(sc, t, gold=0.0, lit=1.0, waffles=True, faces=None):
    faces = faces or {}
    ls.dining(sc, ceiling=True, lamp=False)
    tips = ws.cake(sc, T(0, 1.42, 0), t, "wish", lit, gold=gold > 0, s=1.2)
    out = {}
    for key, spec, x, z, yaw in (("mom", MOM_W, -1.5, -1.5, 15), ("dad", DAD_CHEF, -0.2, -1.6, 0),
                                 ("leo", LEO, 1.4, -1.5, -15), ("finn", FINN, 2.9, 0.2, -90)):
        out[key] = character(sc, spec, (x, 0, z), yaw=yaw, face=faces.get(key, "smile"))
    if waffles:
        out["waffles"] = ls.dog(sc, T(-2.9, 0, 0.6) @ RY(60), t, fur=WAFFLES, hat=False, helmet=True)
    return out, tips


def w42(t, dur):
    u = t / dur
    sc = dcam((0.5, 3.2, 6.4), (0.4, 2.4, -0.4), u, -0.2, fov=44, bloom=0.8)
    _, tips = _wish_table(sc, t)
    sparks(sc, tips[0] + np.array([0, 0.3, 0]), t, seed=2, n=5, r=0.4, color=(255, 230, 140))
    return sc


def w43(t, dur):
    u = t / dur
    sc = dcam((-1.4, 1.4, 3.6), (-2.7, 1.1, 0.6), u, 0.06, fov=36)
    _wish_table(sc, t)
    return sc


def w44(t, dur):
    """'JETPACK! JETPACK!' — three quick cuts: Dad, Mom, Mr Olsen's dog."""
    q = dur / 3
    k = min(2, int(t / q))
    tt = t - k * q
    pump = dict(ar=(150 + 20 * math.sin(tt * 18), -20), er=20 + 30 * abs(math.sin(tt * 9)))
    if k == 0:
        sc = head_cu(DAD_CHEF, (-0.2, 0, -1.6), 0, pump, 0, dist=3.6, fov=38, up=0.3)
        _wish_table(sc, t, waffles=False)
        a = character(sc, DAD_CHEF, (-0.2, 0, -1.6), face="laugh", pose=pump)
    elif k == 1:
        sc = head_cu(MOM_W, (-1.5, 0, -1.5), 15, pump, 0, dist=3.4, fov=38, up=0.3)
        _wish_table(sc, t, waffles=False)
        a = character(sc, MOM_W, (-1.5, 0, -1.5), yaw=15, face="laugh", pose=pump)
    else:
        sc = dcam((0.4, 1.6, 3.2), (0.0, 1.3, 0.0), 0, 0, 38)
        _olsen_home(sc)
        head = ls.dog(sc, T(0, 0.3, 0.4), t, hat=False, mood="talk", **OLSEN_DOG)
        a = dict(head=head)
    ls.sticker(sc, a["head"], "JETPACK!", tt, start=0.05, hold=q, size=0.34, dx=0.0, dy=0.3)
    return sc


def w45(t, dur):
    u = t / dur
    pos = (2.9, 0, 0.2)
    sc = head_cu(FINN, pos, -90, None, u, dist=1.5, side=1.5, fov=36, push=0.15, bloom=0.8)
    _wish_table(sc, t)
    character(sc, FINN, pos, yaw=-90, face="smile" if t < 0.5 else "joy")
    return sc


def w46(t, dur):
    u = t / dur
    pos = (2.9, 0, 0.2)
    sc = head_cu(FINN, pos, -90, dict(lean=6), u, dist=1.6, side=1.6, fov=36, push=0.12, bloom=0.9)
    _wish_table(sc, t)
    a = character(sc, FINN, pos, yaw=-90, face="joy", pose=dict(lean=6))
    sc.light(a["face_pt"] + np.array([-0.4, -0.5, 0]), (255, 190, 110), 40, 0.3)
    return sc


def w47(t, dur):
    u = t / dur
    gold = clamp((t - 0.25) / 0.15)
    sc = dcam((0.1, 4.0, 2.2), (0.0, 3.75, 0.0), u, 0.0, fov=36, bloom=0.8 + 1.4 * gold)
    tips = ws.cake(sc, T(0, 1.42, 0), t, "wish", 1.0 + 0.6 * gold, gold=gold > 0, s=1.2)
    ls.dining(sc, ceiling=True, lamp=False)
    if gold > 0:
        sparks(sc, tips[0] + np.array([0, 0.25, 0]), t, seed=4, n=8, r=0.5, color=(255, 220, 90))
    ws.gold_flash(sc, max(0.0, 1 - abs(t - 0.32) / 0.12) * 0.8)
    return sc


def w48(t, dur):
    u = t / dur
    sc = head_cu(LEO, (1.4, 0, -1.5), -15, None, u, dist=3.4, fov=36)
    _wish_table(sc, t, gold=1.0)
    a = character(sc, LEO, (1.4, 0, -1.5), yaw=-15, face="shock")
    add_emote(sc, "!", a["head_top"], t, size=0.6, dx=0.55, dy=0.25, start=0.1)
    return sc


def w49(t, dur):
    u = t / dur
    sc = head_cu(LEO, (1.4, 0, -1.5), -15, None, u, dist=3.0, fov=36, push=0.12)
    _wish_table(sc, t, gold=1.0)
    character(sc, LEO, (1.4, 0, -1.5), yaw=-15, face="worried" if t < 0.6 else "smile")
    return sc


def w50(t, dur):
    u = t / dur
    sc = dcam((0.6, 3.0, 6.4), (0.4, 2.2, 0.8), u, 0.14, fov=42)
    ls.dining(sc, ceiling=True, lamp=False)
    ws.cake(sc, T(-1.2, 1.42, 0), t, "wish", 1.0, gold=True, s=1.0)
    hug = dict(al=(80, -30), ar=(80, -30), el=50, er=50)
    character(sc, LEO, (0.75, 0, 1.4), yaw=-75, face="joy", pose=hug)
    b = character(sc, FINN, (0.0, 0, 1.4), yaw=80, face="joy", pose=hug)
    character(sc, MOM_W, (-1.6, 0, -1.5), yaw=20, face="joy")
    character(sc, DAD_CHEF, (0.2, 0, -1.6), yaw=-10, face="grin")
    add_emote(sc, "stars", b["head_top"] + np.array([0.4, 0.2, 0]), t, size=0.55, dy=0.2, start=0.3)
    return sc


# ------------------------------------------------------- 51-53: the ending
def w51(t, dur):
    u = t / dur
    sc = bed_cam(0.0, -0.6, u, push=0.12, blue=0.2)
    ws.leo_room(sc)
    a = in_bed(sc, LEO, 0.0, -0.6, "sleep", t, blanket=(70, 110, 170))
    ws.crayon_note(sc, T(0.0, 2.7, -2.96) @ RZ(3), NOTE_LINES, w=1.0, h=0.8, star=1.0)
    add_emote(sc, "zzz", a["head"], t, size=0.6, dx=0.5, dy=0.6, start=0.2, hold=2.4)
    return sc


def w52(t, dur):
    u = t / dur
    sc = dcam((0.0, 0.0, 10.0), (0.0, 0.3, 0.0), u, 0.04, fov=38, sky=((30, 30, 40), (30, 30, 40)), bloom=0.6)
    sc.light((0, 1.0, 5.0), (255, 236, 200), 420, 2.0)
    ws.crayon_note(sc, T(0, 0, 0) @ RZ(2), NOTE_LINES, w=3.6, h=3.6, star=1.0)
    sparks(sc, (0.0, -1.9, 0.2), t, seed=9, n=6, r=0.6, color=(255, 220, 90))
    return sc


def w53(t, dur):
    u = t / dur
    sc = dcam((0.8, 1.5, 3.4), (0.0, 1.0, 0.0), u, 0.12, fov=38)
    ps.nova_room(sc, lamp_k=0.4, day=True, wall=(170, 210, 160))
    head = ls.dog(sc, T(0.3, 0, 0.3) @ RY(-30), t, fur=WAFFLES, hat=False, helmet=True, mood="sad")
    ws.jetpack_drawing(sc, T(-0.9, 0.02, 0.6) @ RX(-90) @ RZ(15), w=1.3, h=1.0)
    add_emote(sc, "sweat", head, t, size=0.45, dx=0.4, dy=0.1, start=0.4)
    return sc


_FNS = [globals()[f"w{i:02d}"] for i in range(1, len(LINES) + 1)]
SHOTS = [(i + 1, 1.4, txt, fn) for i, (txt, fn) in enumerate(zip(LINES, _FNS))]
SHOTS, WORD_TIMES = load_timing(SHOTS, TIMING_FILE)
# the last word of shot 51 is still being spoken over the silent note shot: keep its caption up
if WORD_TIMES.get(51) and not WORD_TIMES.get(52):
    WORD_TIMES[52] = [(-0.1, WORD_TIMES[51][-1][1])]
WT.update(WORD_TIMES)
