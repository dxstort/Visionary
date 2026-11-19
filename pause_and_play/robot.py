"""The Toaster Robot: shot list. Each shot: (number, seconds, caption text, fn(t, dur) -> Scene)."""
import os

TIMING_FILE = "robot_timing.json"
SPOKEN = {"9": "nine", "100": "one hundred", "Mr": "mister", "VRRRRRRRMMM": "vroom"}
PHONES = {"zara": "Z AA R AH", "kip": "K IH P", "pham": "F AA M", "lin": "L IH N", "vroom": "V R UW M",
          "turbo": "T ER B OW", "kip's": "K IH P S"}

LINES = [
    "In this town, when you turn 9,",
    "you build a robot buddy out of stuff from your house.",
    "At midnight, it comes ALIVE.",
    "Kip used his dad's sports car.",
    "His robot, Turbo, can hit 100 miles an hour.",
    "The Lin twins used a fridge.",
    "Their robot never stops handing out SNACKS.",
    "Mr Pham used a lawnmower.",
    "Now it cuts everyone's hair.",
    "Whether they want it or not.",
    "I'm Zara.",
    "My house didn't have a sports car.",
    "So I used a toaster for a head.",
    "A vacuum for a body.",
    "Two mops for arms.",
    "At midnight, it blinked.",
    "Then it popped out a piece of toast.",
    "I named him Crumbs.",
    "Crumbs is SLOW.",
    "He beeps at the wrong time.",
    "And he vacuums up EVERYTHING.",
    "But here's the weird part. Everything I lose, Crumbs finds.",
    "My left sock.",
    "My homework.",
    "The TV remote from inside the couch.",
    "He sucks it up, then spits it out right in my hands. Every time.",
    "Saturday was the Robot Rally.",
    "The winner gets the Golden Wrench.",
    "Kip laughed at the starting line.",
    "Your robot's made of a TOASTER.",
    "The horn blew.",
    "Turbo shot off like a rocket.",
    "Crumbs rolled forward. Very. Slowly.",
    "Then, on the bridge, Kip's necklace snapped.",
    "It fell straight into the storm drain.",
    "Kip froze.",
    "That was my grandpa's medal.",
    "Turbo didn't stop. Turbo only knows FAST.",
    "But Crumbs stopped.",
    "He rolled to the drain.",
    "VRRRRRRRMMM.",
    "Then he spat the medal right into Kip's hands.",
    "Turbo crossed the finish line. Alone.",
    "Nobody even looked.",
    "The whole crowd was watching a toaster hand back a medal.",
    "Kip didn't say anything.",
    "He walked over to the judges, took the Golden Wrench,",
    "and gave it to Crumbs.",
    "Now Kip comes over every day.",
    "He keeps losing things.",
    "On PURPOSE.",
]
import math  # noqa: E402

import numpy as np  # noqa: E402

import laughs_sets as ls  # noqa: E402
import porch_sets as ps  # noqa: E402
import robot_sets as rs  # noqa: E402
import sets  # noqa: E402
import wish_sets as ws  # noqa: E402
from cast import BRAX, PHAM, ZARA, character, crowd_spec, sit  # noqa: E402
from engine import RX, RY, RZ, T, add_emote, clamp, lerp, speed_lines, xf  # noqa: E402
from laughs import bob, dcam, dfcam, head_cu, ht, laugh_pose  # noqa: E402
from porch import fwd_of, ncam  # noqa: E402
from shots import sparks, walk  # noqa: E402
from story import load_timing  # noqa: E402

KIP = dict(BRAX, name="Kip")
TWIN = dict(crowd_spec(1), name="Lin twin", style="bob", hair=(30, 26, 26), skin=(240, 210, 176))
BUZZ_MAN = dict(crowd_spec(10, adult=True), name="Neighbour", style="short")
BUZZED = dict(BUZZ_MAN, style="buzz")
NIGHT_IN = dict(sky=((10, 16, 46), (44, 58, 112)), night=0.75)
ZG = (-0.7, 0, 0.6)   # Zara in her garage
CG = (1.0, 0, 0.2)    # Crumbs in the garage
WT = {}


def word_t(num, i, default=0.0):
    w = WT.get(num, [])
    return w[i][0] if i < len(w) else default


def kip_medal(sc, a, s=1.0):
    rs.medal(sc, a["Mt"] @ T(0, 0.15 * KIP["s"], KIP["torso"][2] * KIP["s"] / 2 + 0.03), s=0.6 * s)


# ------------------------------------------------------- 1-10: the rule
def r01(t, dur):
    u = t / dur
    sc = dcam((-3.0, 2.6, 9.0), (2.0, 1.6, -3.0), u, 0.12, fov=46)
    sets.town(sc)
    for i, x in enumerate((-6.5, 0.0, 6.5)):
        sets.desk(sc, x + 1.2, 1.2, h=0.9, w=1.6, d=0.9)
        character(sc, crowd_spec(4 + i), (x + 1.2, 0, 2.0), yaw=180, face="effort",
                  pose=dict(al=(70 + 10 * math.sin(t * 9 + i), -10), ar=(70, -10), el=40, er=40))
        sc.box(T(x + 1.2, 1.15, 1.2) @ RY(20 * i), (0.5, 0.4, 0.4), [(200, 200, 210), (90, 140, 220), (220, 90, 70)][i],
               layer=4)
    return sc


def r02(t, dur):
    u = t / dur
    sc = dcam((0.8, 2.3, 4.2), (0.0, 1.6, 0.0), u, 0.12, fov=40)
    sets.town(sc)
    sets.desk(sc, 0, 0.0, h=0.9, w=1.6, d=1.0)
    sc.blob(T(0, 1.25, 0), (0.7, 0.7, 0.7), (90, 140, 220), e=0.3, e2=1.0, layer=4)
    tilt = 20 * clamp(t / 0.8)
    sc.box(T(0, 1.75, 0) @ RZ(tilt), (0.1, 0.6, 0.1), (60, 60, 70), layer=4)
    sc.blob(T(0.15 * tilt / 20, 2.1, 0), (0.45, 0.3, 0.45), (250, 220, 120), e=0.5, layer=4)
    character(sc, crowd_spec(4), (0.0, 0, -1.0), face="grin", pose=dict(al=(80, -15), ar=(80, -15), el=40, er=40))
    sparks(sc, (0.0, 1.9, 0.3), t, seed=2, n=4, r=0.4)
    return sc


def r03(t, dur):
    u = t / dur
    sc = ncam((0.2, 2.2, 2.4), (0.0, 2.1, 0.0), u, 0.0, fov=36, mood=NIGHT_IN, bloom=1.4)
    rs.zara_garage(sc, day=False)
    on = clamp((t - 0.6) / 0.2)
    rs.crumbs(sc, T(0, 0, 0), t, eyes=on)
    if on > 0:
        ls.glow_at(sc, (0, 2.05, 0.4), 0.9, (120, 220, 255), int(90 * on))
    return sc


def r04(t, dur):
    u = t / dur
    sc = dcam((1.0, 2.6, 10.8), (0.2, 1.6, 0.6), u, 0.12, fov=42)
    sets.town(sc)
    rs.turbo(sc, T(1.4, 0, 0.8) @ RY(-20), t)
    character(sc, KIP, (-1.4, 0, 0.6), yaw=20, face="smirk", pose=dict(ar=(30, 20), al=(150, -30)))
    sparks(sc, (2.0, 1.4, 1.4), t, seed=3, n=3, r=0.4, color=(255, 255, 255))
    return sc


def r05(t, dur):
    u = t / dur
    x = -12 + 26 * u
    sc = dcam((x - 3.0 + 6 * u, 1.6, 9.0), (x + 1.0, 1.2, 3.0), u, 0.0, fov=46)
    sets.town(sc)
    rs.turbo(sc, T(x, 0, 3.6), t, flames=1.0)
    k = character(sc, KIP, (2.0, 0, 0.8), yaw=150, face="shock", pose=dict(lean=-10, al=(40, 40), ar=(40, 40)))
    speed_lines(sc, t, cx=0.5, cy=0.4, n=20, inner=0.3, alpha=120)
    return sc


def r06(t, dur):
    u = t / dur
    sc = dcam((0.4, 2.4, 6.4), (0.0, 1.9, -1.0), u, 0.06, fov=42)
    sets.kitchen(sc)
    head = rs.fridge_bot(sc, T(0, 0, -1.8), t)
    for sx in (-1, 1):
        character(sc, TWIN, (sx * 1.1, 0, -0.9), yaw=-sx * 50, face="joy",
                  pose=dict(al=(80, -20), ar=(80, -20), el=40, er=40))
    add_emote(sc, "stars", head + np.array([0, 1.2, 0]), t, size=0.6, dy=0.1, start=0.3)
    return sc


def r07(t, dur):
    u = t / dur
    sc = dcam((0.6, 2.4, 7.0), (0.0, 2.0, -1.0), u, 0.06, fov=44)
    sets.kitchen(sc)
    rs.fridge_bot(sc, T(0, 0, -1.8), t)
    for i in range(5):
        ph = (t * 1.4 + i * 0.2) % 1.0
        p = np.array([0.0, 2.4, -0.9]) + np.array([(i - 2) * 1.2 * ph, 1.0 * math.sin(ph * math.pi), 4.0 * ph])
        rs.sandwich(sc, T(*p) @ RY(ph * 400 + i * 50) @ RX(30 * math.sin(ph * 6)))
    for sx in (-1, 1):
        character(sc, crowd_spec(6 + sx), (sx * 1.6, 0, 1.6), yaw=180 + sx * 20, face="shock")
    return sc


def r08(t, dur):
    u = t / dur
    sc = dfcam((0.0, 0, 0.6), ht(PHAM) + 0.2, 10, u, frac=0.5, fov=42, push=0.12)
    sets.town(sc)
    character(sc, PHAM, (-0.8, 0, 0.6), yaw=20, face="grin", pose=dict(ar=(40, 30), al=(10, 5)))
    rs.mower_bot(sc, T(0.9, 0, 0.9) @ RY(-20), t)
    return sc


def r09(t, dur):
    u = t / dur
    sc = dcam((4.0, 2.0, 8.0), (1.0, 1.4, 1.0), u, 0.0, fov=44)
    sets.town(sc)
    x = 3.5 - 5.0 * u
    character(sc, BUZZ_MAN, (x - 1.6, 0, 1.0), yaw=-90, face="shock", pose=dict(walk(t, 14, 36), head=(60, 0, 0)))
    rs.mower_bot(sc, T(x + 0.8, 0, 1.0) @ RY(-90), t)
    add_emote(sc, "sweat", (x - 1.6, 3.3, 1.0), t, size=0.5, dx=0.4, dy=0.0, start=0.2)
    return sc


def r10(t, dur):
    u = t / dur
    pos = (0, 0, 0.6)
    sc = head_cu(BUZZED, pos, 0, None, u, dist=3.4, fov=36)
    sets.town(sc)
    a = character(sc, BUZZED, pos, face="angry")
    add_emote(sc, "anger", a["head_top"], t, size=0.55, dx=0.55, dy=0.0, start=0.3)
    return sc


# ------------------------------------------------------- 11-18: Crumbs is built
def r11(t, dur):
    u = t / dur
    sc = head_cu(ZARA, ZG, 0, None, u, dist=3.2, up=-0.5, fov=36)
    rs.zara_garage(sc)
    a = character(sc, ZARA, ZG, face="grin", pose=dict(ar=(40, 20)))
    sparks(sc, a["head_top"] + np.array([0.5, 0, 0]), t, seed=5, n=4, r=0.3)
    return sc


def r12(t, dur):
    u = t / dur
    sc = dcam((-2.5 + 4.0 * u, 2.6, 6.0), (-1.5 + 3.0 * u, 1.6, -1.2), u, 0.0, fov=46)
    rs.zara_garage(sc)
    character(sc, ZARA, ZG, yaw=-20, face="worried", pose=dict(al=(10, 30), ar=(10, 30)))
    return sc


def _bench_cam(u, push=0.14):
    return dcam((-2.6, 2.6, -0.4), (-3.0, 1.3, -2.6), u, push, fov=40)


def r13(t, dur):
    u = t / dur
    sc = _bench_cam(u)
    rs.zara_garage(sc)
    drop = 1.0 - clamp(t / 0.25)
    sc.box(T(-3.0, 1.46 + 1.2 * drop ** 2, -2.6), (0.95, 0.6, 0.6), rs.CHROME, layer=5)
    for sx in (-1, 1):
        sc.box(T(-3.0 + sx * 0.2, 1.77 + 1.2 * drop ** 2, -2.6), (0.14, 0.03, 0.42), (30, 30, 36), layer=5)
    if drop <= 0:
        ls.dust(sc, (-3.0, 1.2, -2.3), t, 0.25, n=6)
    return sc


def r14(t, dur):
    u = t / dur
    sc = dcam((1.4, 2.2, 4.6), (0.6, 1.2, 0.0), u, 0.08, fov=40)
    rs.zara_garage(sc)
    x = lerp(3.5, 1.0, clamp(t / 0.8))
    sc.box(T(x, 0.18, 0), (1.0, 0.26, 1.2), (214, 60, 60), layer=5)
    sc.box(T(x, 0.95, -0.15), (0.72, 1.3, 0.6), (236, 236, 240), layer=5)
    sc.blob(T(x, 1.0, 0.18), (0.48, 0.8, 0.2), (150, 200, 240), e=0.5, layer=5)
    character(sc, ZARA, (x + 1.3, 0, 0.2), yaw=-80, face="effort", pose=dict(al=(70, -10), ar=(70, -10), lean=-10))
    return sc


def r15(t, dur):
    u = t / dur
    sc = dcam((0.4, 2.2, 4.4), (1.0, 1.6, 0.2), u, 0.04, fov=40)
    rs.zara_garage(sc)
    k1, k2 = clamp(t / 0.3), clamp((t - 0.6) / 0.3)
    rs.crumbs(sc, T(*CG), t, eyes=0.0, arms=(lerp(-60, 20, k1), lerp(-60, 20, k2)))
    for k, sx in ((k1, -1), (k2, 1)):
        if 0 < k < 1:
            sparks(sc, (CG[0] + sx * 0.5, 1.3, CG[2] + 0.2), t, seed=4 + sx, n=3, r=0.2, color=(200, 200, 210))
    return sc


def r16(t, dur):
    u = t / dur
    sc = ncam((1.1, 2.15, 1.9), (1.0, 2.1, 0.2), u, 0.0, fov=36, mood=NIGHT_IN, bloom=1.4)
    rs.zara_garage(sc, day=False)
    eyes = 1.0 if (t > 0.3 and not (0.75 < t < 0.85)) else 0.0
    rs.crumbs(sc, T(*CG), t, eyes=eyes)
    return sc


def r17(t, dur):
    u = t / dur
    pop = clamp((t - 0.2) / 0.9)
    sc = dcam((0.2, 2.8, 5.4), (0.2, 2.4 + 0.8 * math.sin(pop * math.pi), 0.2), u, 0.0, fov=42)
    rs.zara_garage(sc)
    c = rs.crumbs(sc, T(*CG), t, eyes=1.0, toast=pop if pop < 1 else None)
    z = character(sc, ZARA, ZG, yaw=30, face="joy" if pop >= 1 else "shock",
                  pose=dict(al=(110, -20), ar=(110, -20)) if pop > 0.6 else None)
    if pop >= 1:
        rs.toast_slice(sc, T(*((z["hand_l"] + z["hand_r"]) / 2 + np.array([0, 0.25, 0.1]))) @ RY(20))
    ls.sticker(sc, c["slot"], "POP!", t, start=0.2, hold=1.2, size=0.5, dx=0.6, dy=0.6, color=(255, 200, 80))
    return sc


def r18(t, dur):
    u = t / dur
    sc = dcam((0.2, 2.5, 5.0), (0.3, 1.9, 0.3), u, 0.12, fov=40)
    rs.zara_garage(sc)
    rs.crumbs(sc, T(*CG) @ RY(-20), t, eyes=1.0, arms=(60, 20))
    z = character(sc, ZARA, (0.0, 0, 0.6), yaw=60, face="joy", pose=dict(al=(80, -30), ar=(80, -30), el=40, er=40))
    add_emote(sc, "stars", z["head_top"] + np.array([0.6, 0, 0]), t, size=0.55, dy=0.1, start=0.2)
    return sc


# ------------------------------------------------------- 19-26: Crumbs finds things
def r19(t, dur):
    u = t / dur
    sc = dcam((0.5, 1.2, 6.4), (0.0, 1.0, 1.0), u, 0.0, fov=40)
    sets.town(sc)
    rs.crumbs(sc, T(-0.6 + 0.2 * u, 0, 1.0) @ RY(90), t, eyes=1.0, mood="blink" if int(t * 2) % 3 == 0 else "happy")
    sx = -1.6 + 3.4 * u  # a snail overtakes him
    sc.blob(T(sx, 0.2, 2.0), (0.5, 0.3, 0.3), (200, 170, 120), layer=6, n=10, m=6)
    sc.blob(T(sx - 0.05, 0.38, 2.0) @ RZ(30), (0.34, 0.34, 0.2), (190, 120, 80), e=0.8, layer=6, n=12, m=6)
    return sc


def r20(t, dur):
    u = t / dur
    sc = dcam((0.4, 2.6, 6.6), (0.0, 1.8, 0.0), u, 0.04, fov=44)
    rs.library(sc)
    c = rs.crumbs(sc, T(-1.2, 0, 2.6) @ RY(20), t, eyes=1.0, mood="happy")
    for i, (x, z, yaw) in enumerate(((0.6, 0.0, -30), (2.2, 0.4, -50), (-2.6, 0.3, 30))):
        character(sc, crowd_spec(12 + i, adult=i == 0), (x, 0, z), yaw=yaw, face="angry" if t > 0.3 else "neutral",
                  pose=dict(ar=(140, -40), er=110) if t > 0.35 else None)
    add_emote(sc, "!", c["head"], t, size=0.6, dx=0.3, dy=0.2, start=0.1)
    return sc


def r21(t, dur):
    u = t / dur
    sc = dcam((0.5, 2.4, 7.6), (0.4, 1.2, 1.0), u, 0.04, fov=44)
    sets.town(sc)
    c = rs.crumbs(sc, T(-0.8, 0, 1.0) @ RY(40), t, eyes=1.0, hose_to=(0.8, 0.3, 1.6))
    rng = np.random.RandomState(int(t * 3))
    for i in range(6):  # leaves flying into the hose
        ph = (t * 1.5 + i / 6) % 1.0
        p = np.array([2.4 - 1.6 * ph, 0.3 + 0.3 * math.sin(ph * 7 + i), 2.2 - 0.6 * ph])
        sc.box(T(*p) @ RZ(ph * 600 + i * 40), (0.2, 0.02, 0.14), (220, 150, 60), layer=6)
    hat_k = clamp((t - 0.5) / 0.5)
    sc.blob(T(lerp(2.6, 0.9, hat_k), 0.3 + 0.2 * math.sin(hat_k * 3), 1.8), (0.5, 0.25, 0.5), (60, 120, 200), layer=6)
    if 1.4 < t < 2.2:  # the cat pops back out
        k = (t - 1.4) / 0.8
        ls.cat(sc, T(0.9 + 0.6 * k, 0.3 + 1.2 * math.sin(k * math.pi), 1.7) @ RY(60), t, mood="scared", s=0.8)
    return sc


def r22(t, dur):
    u = t / dur
    sc = head_cu(ZARA, (0, 0, 0.4), 0, None, u, dist=3.6, fov=36, push=0.12)
    ws.living_room(sc)
    a = character(sc, ZARA, (0, 0, 0.4), face="suspicious", pose=dict(ar=(60, 20), er=60))
    rs.crumbs(sc, T(1.3, 0, -0.9) @ RY(-20), t, eyes=1.0)
    add_emote(sc, "bulb", a["head_top"], t, size=0.6, dx=-0.5, dy=0.2, start=1.6)
    return sc


def _spit(sc, t, item_fn, start=0.15):
    """Crumbs spits item_fn(M) into Zara's waiting hands."""
    rs.crumbs(sc, T(1.0, 0, -0.2) @ RY(-50), t, eyes=1.0, hose_to=(0.2, 1.5, 0.8))
    z = character(sc, ZARA, (-0.6, 0, 0.9), yaw=50, face="joy", pose=dict(al=(70, -20), ar=(70, -20), el=30, er=30))
    hands = (z["hand_l"] + z["hand_r"]) / 2 + np.array([0, 0.15, 0.1])
    k = clamp((t - start) / 0.3)
    p = np.array([0.2, 1.5, 0.8]) * (1 - k) + hands * k + np.array([0, 0.5 * math.sin(k * math.pi), 0])
    item_fn(T(*p) @ RY(30 + 200 * (1 - k)))
    if k >= 1:
        ls.sticker(sc, hands, "POP!", t, start=start + 0.3, hold=0.6, size=0.35, dy=0.5)
    return z


def r23(t, dur):
    u = t / dur
    sc = dcam((0.2, 2.0, 3.6), (0.0, 1.4, 0.6), u, 0.06, fov=40)
    ws.living_room(sc)
    _spit(sc, t, lambda M: ls.sock(sc, M @ T(0, -0.3, 0) @ RZ(70), "stripes", (240, 90, 110), (255, 255, 255)))
    return sc


def r24(t, dur):
    u = t / dur
    sc = dcam((0.2, 2.0, 3.6), (0.0, 1.4, 0.6), u, 0.06, fov=40)
    ws.living_room(sc)
    _spit(sc, t, lambda M: rs.homework(sc, M), start=0.05)
    return sc


def r25(t, dur):
    u = t / dur
    sc = dcam((0.4, 2.6, 5.2), (0.0, 1.0, -1.6), u, 0.04, fov=42)
    ws.living_room(sc)
    shoot = clamp((t - 1.2) / 0.4)
    rs.crumbs(sc, T(1.6, 0, -0.4) @ RY(-60), t, eyes=1.0, hose_to=(0.3, 0.9, -1.7), shake=0.6 if t < 1.2 else 0)
    p = np.array([0.3, 0.95, -1.7]) + np.array([-0.8, 1.6, 1.4]) * shoot + np.array([0, -1.6 * shoot ** 2, 0])
    rs.remote(sc, T(*p) @ RX(400 * shoot))
    if shoot > 0:
        ls.sticker(sc, p, "POP!", t, start=1.2, hold=0.8, size=0.35, dy=0.4)
    return sc


def r26(t, dur):
    u = t / dur
    sc = dcam((0.2, 2.3, 5.0), (0.2, 1.6, 0.4), u, 0.14, fov=40)
    ws.living_room(sc)
    z = _spit(sc, t, lambda M: rs.remote(sc, M), start=0.2)
    base = (z["hand_l"] + z["hand_r"]) / 2 + np.array([0, 0.2, 0.1])
    items = [lambda M: rs.homework(sc, M), lambda M: ls.sock(sc, M @ RZ(80) @ T(0, -0.3, 0)),
             lambda M: sc.box(M, (0.5, 0.3, 0.4), (90, 160, 230), layer=7)]
    for i, fn in enumerate(items):
        if t > 0.9 + i * 0.6:
            fn(T(*(base + np.array([0, 0.12 * (i + 1), 0]))) @ RY(20 * i))
    sparks(sc, base + np.array([0, 0.5, 0]), t, seed=7, n=4, r=0.4)
    return sc


# ------------------------------------------------------- 27-33: the Robot Rally
def r27(t, dur):
    u = t / dur
    sc = dcam((-30 + 10 * u, 6.0, 18.0), (-14 + 10 * u, 1.6, 0.0), u, 0.0, fov=46)
    rs.race_track(sc, t)
    from shots import confetti
    confetti(sc, t, n=40)
    return sc


def r28(t, dur):
    u = t / dur
    w = np.array([rs.FINISH_X + 3.0, 0, -1.6])
    sc = dcam(w + np.array([0.6, 2.6, 6.4]), w + np.array([0, 2.4, 0]), u, 0.14, fov=38)
    rs.race_track(sc, t, crowd=False)
    sparks(sc, w + np.array([0.3, 3.4, 0.3]), t, seed=3, n=4, r=0.3, color=(255, 255, 220))
    return sc


SL = np.array([rs.START_X + 1.5, 0, 1.6])   # Kip's lane at the start
SC = np.array([rs.START_X + 1.5, 0, 4.4])   # Crumbs's lane


def _start_line(sc, t, kip_face="laugh", kip_pose=None, crumbs_kw=None):
    rs.race_track(sc, t, crowd=False)
    rs.turbo(sc, T(*(SL + np.array([0.5, 0, 0]))), t)
    k = character(sc, KIP, SL + np.array([-0.6, 0, -1.2]), yaw=20, face=kip_face, pose=kip_pose)
    kip_medal(sc, k)
    c = rs.crumbs(sc, T(*SC) @ RY(90), t, eyes=1.0, **(crumbs_kw or {}))
    z = character(sc, ZARA, SC + np.array([-0.6, 0, 1.3]), yaw=60, face="smile")
    return k, c, z


def r29(t, dur):
    u = t / dur
    sc = dcam(SL + np.array([0.6, 2.4, 6.6]), SL + np.array([0, 1.8, 0.6]), u, 0.04, fov=44)
    _start_line(sc, t, "laugh", dict(laugh_pose(t), lean=-8))
    return sc


def r30(t, dur):
    u = t / dur
    sc = dcam(SL + np.array([1.0, 2.6, 8.6]), SL + np.array([0, 1.8, 1.4]), u, 0.04, fov=44)
    pop = clamp((t - 0.9) / 0.7)
    k, c, z = _start_line(sc, t, "smirk", dict(ar=(90, -40)), dict(toast=pop if 0 < pop < 1 else None))
    if t > 0.3:
        def fire(d, x, y, s, col):
            for i, c_ in enumerate(((255, 120, 40), (255, 210, 60))):
                r = (0.25 - i * 0.09) * s
                d.polygon([(x - r, y), (x, y - r * 2.4 + math.sin(t * 20) * r * 0.2), (x + r, y), (x, y + r * 0.6)],
                          fill=c_ + (255,))
        sc.sprite(k["head_top"] + np.array([0, 0.2, 0]), fire, layer=8, live=True)
    return sc


def r31(t, dur):
    u = t / dur
    p = SL + np.array([-2.0, 0, -1.6])
    sc = dcam(p + np.array([1.2, 2.3, 3.6]), p + np.array([0, 1.7, 0]), u, 0.0, fov=38)
    rs.race_track(sc, t, crowd=False)
    character(sc, crowd_spec(9, adult=True), p + np.array([-0.4, 0, -0.4]), yaw=30, face="grin",
              pose=dict(ar=(70, -10), er=30))
    rs.air_horn(sc, T(*(p + np.array([0.15, 1.1, 0.2]))))
    if 0.08 <= t < 0.08 + 2 / 30:
        sc.flash = 1.0
    return sc


def r32(t, dur):
    u = t / dur
    x = SL[0] + 0.5 + 30 * u ** 1.5
    sc = dcam((SL[0] - 4 + 14 * u, 1.6, 10.5), (x - 2.0, 1.2, 2.0), u, 0.0, fov=46)
    rs.race_track(sc, t, crowd=False)
    rs.turbo(sc, T(x, 0, SL[2]), t, flames=1.0)
    rs.crumbs(sc, T(*SC) @ RY(90), t, eyes=1.0)
    for i in range(6):
        ls.dust(sc, (x - 2.0 - i * 1.2, 0.2, SL[2]), t, max(0.0, t - 0.2), n=3)
    speed_lines(sc, t, cx=0.6, cy=0.5, n=16, inner=0.35, alpha=110)
    return sc


def r33(t, dur):
    u = t / dur
    sc = dcam(SC + np.array([1.0, 1.8, 6.0]), SC + np.array([0.5, 1.4, 0]), u, 0.0, fov=44)
    rs.race_track(sc, t, crowd=False)
    rs.crumbs(sc, T(*(SC + np.array([0.3 * u, 0, 0]))) @ RY(90), t, eyes=1.0)

    def dustcloud(d, W, H):
        a = int(90 * (1 - u))
        for i in range(8):
            d.ellipse([W * (i / 8 - 0.1), H * 0.55, W * (i / 8 + 0.25), H * 0.75], fill=(220, 210, 190, a))
    sc.overlay(dustcloud)
    return sc


# ------------------------------------------------------- 34-42: the drain
BR = np.array([3.4, 0, 4.6])  # Kip on the bridge, near the drain


def r34(t, dur):
    u = t / dur
    sc = dcam(BR + np.array([1.4, 2.4, 6.4]), BR + np.array([0.6, 1.8, 0]), u, 0.0, fov=44)
    rs.race_track(sc, t, crowd=False)
    x = BR[0] - 2.0 + 2.0 * u
    k = character(sc, KIP, (x, 0, BR[2]), yaw=90, face="grin" if t < 1.8 else "shock", pose=walk(t, 12, 30))
    rs.turbo(sc, T(x + 6 + 10 * u, 0, 1.6), t, flames=0.6)
    snap = word_t(34, 5, 1.8)
    if t < snap:
        kip_medal(sc, k)
    else:
        f = clamp((t - snap) / 0.6)
        rs.medal(sc, T(*(k["Mt"][:3, 3] + np.array([0.3 * f, 0.3 - 1.8 * f * f, 0.4]))) @ RZ(300 * f), s=0.6)
        ls.sticker(sc, k["Mt"][:3, 3], "SNAP!", t, start=snap, hold=0.8, size=0.4, dx=0.8, dy=0.3)
    return sc


def r35(t, dur):
    u = t / dur
    sc = dcam(rs.DRAIN + np.array([0.1, 2.2, 0.6]), rs.DRAIN + np.array([0, 0, 0]), u, 0.18, fov=40)
    rs.race_track(sc, t, crowd=False)
    f = clamp(t / 0.9)
    rs.medal(sc, T(*(rs.DRAIN + np.array([0.0, 1.5 * (1 - f) ** 2 + 0.07 - 0.12 * f, 0]))) @ RX(-80) @ RZ(250 * f), s=0.7)
    return sc


def r36(t, dur):
    u = t / dur
    sc = head_cu(KIP, BR, 90, None, u, dist=3.0, side=-0.4, fov=36)
    rs.race_track(sc, t, crowd=False)
    a = character(sc, KIP, BR, yaw=90, face="shock")
    add_emote(sc, "!", a["head_top"], t, size=0.6, dx=0.4, dy=0.2, start=0.05)
    return sc


KNEEL = dict(lean=30, ll=70, lr=70, kl=-80, kr=-80, al=(40, 6), ar=(40, 6), y=-0.9)


def r37(t, dur):
    u = t / dur
    pos = rs.DRAIN + np.array([0, 0, -1.3])
    sc = head_cu(KIP, pos, 0, KNEEL, u, dist=2.6, side=0.3, up=-0.8, fov=36, push=0.12)
    rs.race_track(sc, t, crowd=False)
    a = character(sc, KIP, pos, face="stung", pose=KNEEL)
    add_emote(sc, "tears", a["head_top"], t, size=0.55, dy=-0.25, start=0.3)
    return sc


def r38(t, dur):
    u = t / dur
    x = 12 + 14 * u
    sc = dcam((x - 9.0, 1.8, 9.0), (x - 1.0, 1.2, 1.6), u, 0.0, fov=40)
    rs.race_track(sc, t, crowd=False)
    rs.turbo(sc, T(x, 0, 1.6), t, flames=1.0)
    speed_lines(sc, t, cx=0.7, cy=0.5, n=12, inner=0.4, alpha=90)
    return sc


CD = rs.DRAIN + np.array([-1.8, 0, 0.0])   # Crumbs stops beside the drain


def r39(t, dur):
    u = t / dur
    sc = dcam(CD + np.array([0.8, 2.0, 5.0]), CD + np.array([0.3, 1.4, 0]), u, 0.0, fov=42)
    rs.race_track(sc, t, crowd=False)
    rs.crumbs(sc, T(*(CD + np.array([-1.2 * (1 - clamp(t / 0.5)) ** 2, 0, 0]))) @ RY(90), t, eyes=1.0)
    return sc


def r40(t, dur):
    u = t / dur
    sc = dcam(CD + np.array([0.6, 0.8, 4.0]), CD + np.array([0.8, 0.9, 0]), u, 0.14, fov=40)
    rs.race_track(sc, t, crowd=False)
    k = clamp(t / 1.0)
    rs.crumbs(sc, T(*CD) @ RY(90), t, eyes=1.0, hose_to=rs.DRAIN + np.array([-0.2, 0.2 + 0.6 * (1 - k), 0]))
    character(sc, KIP, rs.DRAIN + np.array([0.9, 0, -1.3]), yaw=-30, face="stung", pose=KNEEL)
    return sc


def r41(t, dur):
    u = t / dur
    sc = dcam(CD + np.array([0.9, 2.2, 2.4]), CD + np.array([0.3, 1.6, 0]), u, 0.0, fov=40)
    rs.race_track(sc, t, crowd=False)
    c = rs.crumbs(sc, T(*CD) @ RY(90), t, eyes=1.0, mood="blink", hose_to=rs.DRAIN + np.array([-0.2, 0.15, 0]),
                  shake=1.0)
    ls.sticker(sc, c["head"], "VRRRMMM", t, start=0.0, hold=1.0, size=0.42, dx=0.0, dy=0.5, color=(120, 220, 255))
    return sc


def r42(t, dur):
    u = t / dur
    sc = dcam(CD + np.array([1.6, 2.4, 5.4]), CD + np.array([1.4, 1.5, 0]), u, 0.04, fov=42)
    rs.race_track(sc, t, crowd=False)
    rs.crumbs(sc, T(*CD) @ RY(60), t, eyes=1.0, hose_to=(CD[0] + 1.4, 1.4, CD[2] - 0.2))
    k = character(sc, KIP, rs.DRAIN + np.array([0.6, 0, -0.9]), yaw=-60, face="shock" if t < 1.6 else "joy",
                  pose=KNEEL if t < 1.0 else dict(al=(60, -20), ar=(60, -20), el=30, er=30))
    f = clamp((t - 1.0) / 0.5)
    hands = (k["hand_l"] + k["hand_r"]) / 2 + np.array([0, 0.15, 0.1])
    src = np.array([CD[0] + 1.4, 1.4, CD[2] - 0.2])
    if t > 1.0:
        p = src * (1 - f) + hands * f + np.array([0, 0.4 * math.sin(f * math.pi), 0])
        rs.medal(sc, T(*p) @ RY(360 * (1 - f)), s=0.6)
        if f >= 1:
            sparks(sc, hands, t, seed=6, n=5, r=0.4)
    return sc


# ------------------------------------------------------- 43-51: the ending
def r43(t, dur):
    u = t / dur
    sc = dcam((rs.FINISH_X - 2.0, 2.2, 9.0), (rs.FINISH_X, 1.4, 2.0), u, 0.0, fov=44)
    rs.race_track(sc, t, crowd=False)
    rs.turbo(sc, T(rs.FINISH_X - 6 + 10 * u, 0, 1.6), t, flames=0.5, face="flat")
    return sc


def r44(t, dur):
    u = t / dur
    sc = dcam((rs.FINISH_X - 2, 3.0, 4.0), (rs.FINISH_X - 2, 2.0, rs.STAND_Z - 1), u, 0.04, fov=46)
    rs.race_track(sc, t, crowd=False)
    return sc


def r45(t, dur):
    u = t / dur
    c0 = rs.DRAIN + np.array([-0.4, 0, -0.4])
    sc = dcam(c0 + np.array([0.6, 3.4 + 2.0 * u, 7.0 + 3.0 * u]), c0 + np.array([0, 1.4, 0]), u, 0.0, fov=44)
    rs.race_track(sc, t, crowd=False)
    rs.crumbs(sc, T(*CD) @ RY(60), t, eyes=1.0)
    k = character(sc, KIP, rs.DRAIN + np.array([0.6, 0, -0.9]), yaw=-60, face="joy",
                  pose=dict(al=(60, -20), ar=(60, -20), el=30, er=30))
    rs.medal(sc, T(*((k["hand_l"] + k["hand_r"]) / 2 + np.array([0, 0.15, 0.1]))), s=0.6)
    ring = [(c0[0] + 3.0 * math.cos(a), c0[2] + 2.4 * math.sin(a)) for a in np.linspace(0.3, 2.9, 7)]
    for i, (x, z) in enumerate(ring):
        z = min(z, rs.TRACK_Z1 - 0.3)
        a = character(sc, crowd_spec(20 + i, adult=i % 2 == 0), (x, 0, z - 3.0), yaw=0, face="joy")
        add_emote(sc, "stars", a["head_top"], t, size=0.4, dy=0.1, start=0.3 + 0.15 * i, hold=1.4)
    return sc


def r46(t, dur):
    u = t / dur
    pos = rs.DRAIN + np.array([0.6, 0, -0.9])
    sc = head_cu(KIP, pos, -60, None, u, dist=3.0, side=0.3, fov=36)
    rs.race_track(sc, t, crowd=False)
    k = character(sc, KIP, pos, yaw=-60, face="neutral", pose=dict(al=(40, 6)))
    rs.medal(sc, T(*k["hand_l"]) @ T(0, 0.15, 0.1), s=0.6)
    return sc


def r47(t, dur):
    u = t / dur
    w = np.array([rs.FINISH_X + 3.0, 0, -1.6])
    x = lerp(w[0] - 3.5, w[0] - 0.9, clamp(t / 1.4))
    sc = dcam((w[0] - 1.0, 2.4, 6.6), (w[0] - 1.0, 1.8, -1.2), u, 0.0, fov=44)
    rs.race_track(sc, t, crowd=False)
    lift = clamp((t - 1.5) / 0.4)
    k = character(sc, KIP, (x, 0, w[2] + 0.4), yaw=90 if t < 1.4 else 60, face="neutral",
                  pose=walk(t, 8, 22) if t < 1.4 else dict(ar=(90 * lift, -10), al=(90 * lift, -10)))
    for i, xx in enumerate((w[0] + 1.6, w[0] + 2.8)):
        character(sc, crowd_spec(30 + i, adult=True), (xx, 0, w[2] - 0.6), yaw=-40, face="shock")
    return sc


def r48(t, dur):
    u = t / dur
    sc = dcam(CD + np.array([1.2, 2.8, 7.4]), CD + np.array([1.0, 1.6, 0.4]), u, 0.14, fov=42)
    rs.race_track(sc, t, crowd=False)
    c = rs.crumbs(sc, T(*CD) @ RY(60), t, eyes=1.0, arms=(60, 60))
    k = character(sc, KIP, CD + np.array([1.8, 0, 0.4]), yaw=-100, face="smile", pose=dict(ar=(90, -10), al=(90, -10)))
    rs.golden_wrench(sc, T(*(CD + np.array([0.9, 0.2, 0.3]))) @ RZ(70), s=0.55, stand=False)
    z = character(sc, ZARA, CD + np.array([-0.6, 0, 1.6]), yaw=40, face="shock")
    from shots import confetti
    confetti(sc, t, n=50)
    sparks(sc, c["head"], t, seed=8, n=5, r=0.6)
    return sc


def r49(t, dur):
    u = t / dur
    sc = dcam((0.6, 2.4, 6.6), (0.6, 1.8, 0.8), u, 0.0, fov=44)
    rs.zara_garage(sc)
    rs.crumbs(sc, T(*CG) @ RY(-30), t, eyes=1.0)
    character(sc, ZARA, ZG, yaw=30, face="smile")
    character(sc, KIP, (1.8, 0, 2.6), yaw=-50, face="grin", pose=dict(ar=(160, -20 - 15 * math.sin(t * 10))))
    return sc


def r50(t, dur):
    u = t / dur
    sc = dcam((0.6, 2.4, 6.4), (0.6, 1.6, 0.8), u, 0.0, fov=44)
    rs.zara_garage(sc)
    rs.crumbs(sc, T(*CG) @ RY(-30), t, eyes=1.0)
    k = character(sc, KIP, (1.4, 0, 2.0), yaw=-40, face="smirk", pose=dict(ar=(60 - 50 * clamp((t - 0.4) / 0.3), 10)))
    if t < 0.7:
        sc.blob(T(*(k["hand_r"] + np.array([0, 0.1, 0]))), (0.5, 0.25, 0.5), (220, 60, 60), layer=6)
    else:
        f = clamp((t - 0.7) / 0.3)
        sc.blob(T(*(k["hand_r"] * (1 - f) + np.array([1.0, 0.12, 2.8]) * f)), (0.5, 0.25, 0.5), (220, 60, 60), layer=6)
    return sc


def r51(t, dur):
    u = t / dur
    sc = dcam((0.6, 2.4, 6.4), (0.6, 1.7, 0.8), u, 0.0, fov=44)
    rs.zara_garage(sc)
    k = clamp((t - 0.2) / 0.4)
    rs.crumbs(sc, T(*CG) @ RY(-30), t, eyes=1.0, hose_to=(1.0, 0.3 + 1.0 * k, 2.6 - 0.4 * k))
    kp = character(sc, KIP, (1.4, 0, 2.0), yaw=-40, face="grin", pose=dict(al=(60, -20), ar=(60, -20)))
    z = character(sc, ZARA, ZG, yaw=30, face="suspicious", pose=dict(head=(0, 12, 0)))
    if k >= 1:
        sc.blob(T(*((kp["hand_l"] + kp["hand_r"]) / 2 + np.array([0, 0.15, 0.05]))), (0.5, 0.25, 0.5), (220, 60, 60),
                layer=6)
        ls.sticker(sc, kp["head"], "POP!", t, start=0.6, hold=1.0, size=0.4, dx=0.5, dy=0.7)
    return sc


_FNS = [globals()[f"r{i:02d}"] for i in range(1, len(LINES) + 1)]
SHOTS = [(i + 1, 1.4, txt, fn) for i, (txt, fn) in enumerate(zip(LINES, _FNS))]
SHOTS, WORD_TIMES = load_timing(SHOTS, TIMING_FILE)
WT.update(WORD_TIMES)
