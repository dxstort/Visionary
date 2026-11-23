"""The Walking Shoes: shot list. Each shot: (number, seconds, caption text, fn(t, dur) -> Scene)."""
import os

TIMING_FILE = "shoes_timing.json"
SPOKEN = {"1965": "nineteen sixty five", "Mrs": "missus"}
PHONES = {"rudy": "R UW D IY", "doyle": "D OY L", "doyle's": "D OY L Z", "kim's": "K IH M Z"}

LINES = [
    "In this town, when you put your shoes on in the morning,",
    "they walk you wherever you're needed MOST.",
    "You don't get a say.",
    "Dad's shoes walk him to the bakery every morning.",
    "He's not a baker. He's the taste tester.",
    "Mrs Kim's shoes once walked her straight into the lake.",
    "A duck needed help.",
    "The mayor's shoes just walk him in circles.",
    "Nobody needs the mayor.",
    "I'm Rudy. I'm the goalie for the Hill Street Hawks.",
    "I want my shoes to take me somewhere COOL.",
    "The skate park. The candy store. Anywhere.",
    "But every single day, they walk me to the same place.",
    "Old Mrs Doyle's porch. Next door.",
    "She sits there with a giant jigsaw puzzle.",
    "Her eyes aren't great anymore. So I find the pieces for her.",
    "Every. Single. Day.",
    "It's the most boring puzzle in the world. Mostly green grass.",
    "And half the pieces are MISSING.",
    "Saturday was the championship game.",
    "I laced up my shoes.",
    "Field, I told them. Please. Just this once.",
    "They turned left.",
    "Mrs Doyle's porch. AGAIN.",
    "I tried to run the other way. My shoes dragged me backwards.",
    "Mrs Doyle smiled. Found the last piece this morning.",
    "She pressed it in.",
    "The puzzle wasn't just grass.",
    "It was a soccer field. And a goalie. Diving. Gloves out.",
    "A trophy behind her.",
    "Town champions. 1965, Mrs Doyle said.",
    "She reached under her chair.",
    "Old leather gloves. Cracked. Perfect.",
    "Penalty shootout, she said.",
    "Watch the striker's hips. Not the ball.",
    "Then my shoes turned around. Toward the field.",
    "And they RAN.",
    "I made it for the shootout.",
    "Last kick.",
    "I watched the hips.",
    "I dove left.",
    "SAVED IT.",
    "The Hawks won.",
    "My shoes always walk me where I'm needed most.",
    "I thought she needed me.",
    "I needed her TOO.",
]
import math  # noqa: E402

import numpy as np  # noqa: E402

import laughs_sets as ls  # noqa: E402
import shoes_sets as ss  # noqa: E402
import sets  # noqa: E402
from cast import DAD, DOYLE, MAYOR, RUDY, character, crowd_spec, sit  # noqa: E402
from engine import RX, RY, RZ, T, add_emote, clamp, lerp, speed_lines, xf  # noqa: E402
from laughs import bob, dcam, dfcam, head_cu, ht, probe  # noqa: E402
from shots import confetti, sparks, walk  # noqa: E402
from story import load_timing  # noqa: E402

MRS_KIM = dict(crowd_spec(1, adult=True), name="Mrs Kim", style="bob", hair=(30, 26, 30), skin=(240, 210, 176),
               shirt=(240, 140, 160))
STRIKER = dict(crowd_spec(6), name="Striker", shirt=(220, 60, 60), jersey=True, accent=(255, 255, 255))
HAWK = lambda i: dict(crowd_spec(i + 40), shirt=(60, 170, 90), jersey=True, accent=(250, 220, 80))
WT = {}


def word_t(num, i, default=0.0):
    w = WT.get(num, [])
    return w[i][0] if i < len(w) else default


def sub3(t, num, dur, idx=(0, 1, 2)):
    starts = [0.0] + [word_t(num, i, dur * k / 3) for k, i in enumerate(idx[1:], 1)]
    k = 0
    for i, s0 in enumerate(starts):
        if t >= s0 - 0.04:
            k = i
    return k, t - starts[k]


def doyle_seated(sc, face="smile", pose=None, t=0.0):
    p = sit()
    p.update(al=(50, 4), ar=(50, 4))
    p.update(pose or {})
    ll = DOYLE["leg"][1] * DOYLE["s"]
    c = ss.CHAIR
    return character(sc, DOYLE, (c[0], c[1] + 0.75 - ll, c[2]), yaw=90, face=face, pose=p, shadow=False)


def dragged(t, back=False):
    """Pose for being pulled along by the feet: leaning back, arms flailing."""
    w = math.sin(t * 14)
    return dict(walk(t, 12, 28), lean=-18 if not back else 18, al=(150 + 20 * w, -30), ar=(150 - 20 * w, -30))


# ------------------------------------------------------- 1-9: the rule
DOOR = np.array([0.0, 0.0, -4.4])


def k_town_door(sc):
    sets.town(sc)


def s01(t, dur):
    u = t / dur
    pos = (0.0, 0, -4.2)
    pose = dict(lean=40, al=(70, -10), ar=(70, -10), el=30, er=30)
    sc = dfcam((0.0, 0, -4.2), 2.2, 25, u, frac=0.42, fov=40, push=0.06)
    sets.town(sc)
    a = character(sc, crowd_spec(4), pos, face="smile", pose=pose)
    return sc


def s02(t, dur):
    u = t / dur
    z = -4.0 + 2.2 * u
    sc = dcam((0.6, 0.5, z + 2.6), (0.0, 0.4, z), u, 0.0, fov=40)
    sets.town(sc)
    a = character(sc, crowd_spec(4), (0.0, 0, z), face="shock", pose=walk(t, 8, 26))
    ss.shoe_sparkles(sc, a, t)
    return sc


def s03(t, dur):
    u = t / dur
    x = -3.0 + 6.0 * u
    sc = dcam((0.0, 2.4, 9.0), (0.0, 1.6, 1.0), u, 0.0, fov=44)
    sets.town(sc)
    a = character(sc, crowd_spec(4), (x, 0, 1.0), yaw=90, face="shock", pose=dragged(t))
    ss.shoe_sparkles(sc, a, t)
    add_emote(sc, "sweat", a["head_top"], t, size=0.5, dx=-0.5, dy=0.1, start=0.2)
    return sc


def s04(t, dur):
    u = t / dur
    z = 3.0 - 3.6 * u
    sc = dcam((1.6, 2.4, 9.0), (0.0, 2.0, -1.4), u, 0.0, fov=44)
    ss.bakery(sc, t)
    a = character(sc, DAD, (0.0, 0, z), yaw=180, face="grin", pose=walk(t, 7, 22))
    ss.shoe_sparkles(sc, a, t)
    return sc


def s05(t, dur):
    u = t / dur
    pose = dict(ar=(150, -30), er=80, al=(10, 6))
    sc = head_cu(DAD, (0, 0, 0.2), 0, pose, u, dist=5.0, up=0.2, fov=36)
    ss.bakery_counter(sc, t)
    a = character(sc, DAD, (0, 0, 0.2), face="chew0" if int(t * 6) % 2 else "chew1", pose=pose)
    ss.flour(sc, a, t)
    add_emote(sc, "stars", a["head_top"], t, size=0.55, dx=0.5, dy=0.15, start=1.0)
    return sc


def s06(t, dur):
    u = t / dur
    k = clamp(t / 1.8)
    z = lerp(1.0, -5.6, k)
    y = 0.4 if z > -5.4 else 0.4 - 2.0 * clamp((t - 1.8) / 0.3)
    sc = dcam((4.0, 2.4, 3.0), (0.0, 1.2, -3.0), u, 0.0, fov=44)
    ss.lake(sc, t)
    a = character(sc, MRS_KIM, (0.0, y, z), yaw=180, face="shock" if t > 1.6 else "worried", pose=walk(t, 7, 22))
    ss.splash(sc, (0.0, 0.2, -5.8), t, start=1.85)
    return sc


def s07(t, dur):
    u = t / dur
    pos = (0.0, -0.8, -3.0)
    sc = head_cu(MRS_KIM, pos, 0, dict(al=(70, -20), ar=(70, -20)), u, dist=3.4, fov=38)
    ss.lake(sc, t)
    a = character(sc, MRS_KIM, pos, face="joy", pose=dict(al=(70, -20), ar=(70, -20)), shadow=False)
    h = ss.duck(sc, T(*((a["hand_l"] + a["hand_r"]) / 2 + np.array([0, -0.2, 0.3]))), t, s=0.9)
    add_emote(sc, "stars", h, t, size=0.45, dy=0.3, start=0.2)
    return sc


def s08(t, dur):
    u = t / dur
    sc = dcam((0.0, 9.0, 9.5), (0.0, 1.0, 0.6), u, 0.0, fov=44)
    sets.town(sc)
    a_ = t * 2.4
    p = (1.4 * math.cos(a_), 0, 0.6 + 1.4 * math.sin(a_))
    a = character(sc, MAYOR, p, yaw=math.degrees(-a_), face="worried", pose=walk(t, 7, 22))
    add_emote(sc, "stars", a["head_top"], t, size=0.6, dy=0.2, start=0.2, hold=2.5)
    return sc


def s09(t, dur):
    u = t / dur
    sc = head_cu(MAYOR, (0, 0, 0.6), 0, None, u, dist=3.6, fov=36)
    sets.town(sc)
    a = character(sc, MAYOR, (0, 0, 0.6), face="worried", pose=dict(head=(10 * math.sin(t * 6), 0, 8 * math.sin(t * 5))))
    add_emote(sc, "?", a["head_top"], t, size=0.6, dx=0.5, dy=0.2, start=0.1)
    return sc


# ------------------------------------------------------- 10-14: Rudy
RUDY_H = (0.0, 0, 0.8)


def s10(t, dur):
    u = t / dur
    sc = dfcam(RUDY_H, ht(RUDY) + 0.4, 0, u, frac=0.6, fov=42, push=0.12, elev=-0.6)
    sets.town(sc)
    a = character(sc, RUDY, RUDY_H, face="grin", pose=dict(al=(40, 10), ar=(40, 10), el=50, er=50))
    by = 0.6 + abs(math.sin(t * 5)) * 1.0
    ss.ball(sc, T(RUDY_H[0] + 0.5, by, RUDY_H[2] + 0.6))
    ss.gloves(sc, a, color=(240, 240, 240))
    sparks(sc, a["head_top"] + np.array([0.5, 0, 0]), t, seed=3, n=4, r=0.3)
    return sc


def s11(t, dur):
    u = t / dur
    pose = dict(lean=14, al=(60, -20), ar=(60, -20), el=60, er=60, head=(0, -25, 0))
    sc = head_cu(RUDY, RUDY_H, 0, pose, u, dist=3.2, up=0.6, fov=36)
    sets.town(sc)
    character(sc, RUDY, RUDY_H, face="worried", pose=pose)
    return sc


def s12(t, dur):
    k, tt = sub3(t, 12, dur, (0, 2, 5))
    if k == 0:
        sc = dcam((0.0, 3.0, 8.0), (0.0, 1.0, -2.0), 0, 0, 44)
        ss.skate_park(sc)
        p = (0.0, 0.6, -2.0)
    elif k == 1:
        sc = dcam((0.4, 2.6, 6.4), (0.0, 1.8, -1.0), 0, 0, 42)
        ss.candy_store(sc)
        p = (0.0, 2.2, -1.0)
    else:
        sc = dcam((0.0, 4.0, 10.0), (0.0, 5.0, -6.0), 0, 0, 46)
        ss.fun_fair(sc, t)
        p = (0.0, 7.0, -10.0)
    sparks(sc, p, tt, seed=k + 2, n=6, r=1.0)
    return sc


def s13(t, dur):
    u = t / dur
    k = clamp(t / 1.6)
    x = lerp(0.0, -3.0, clamp((t - 1.6) / 1.6))
    z = lerp(-4.2, 0.6, k)
    sc = dcam((2.0, 2.6, 7.4), (x * 0.5, 1.6, z * 0.5), u, 0.0, fov=44)
    sets.town(sc)
    a = character(sc, RUDY, (x, 0, z), yaw=180 if k < 1 else -90, face="angry", pose=dragged(t, back=False))
    ss.shoe_sparkles(sc, a, t)
    return sc


def s14(t, dur):
    u = t / dur
    sc = dcam((1.0, 2.8, 9.0), (0.0, 1.6, 0.6), u, 0.12, fov=44)
    ss.doyle_porch(sc, t, table=False)
    return sc


# ------------------------------------------------------- 15-19: the puzzle
def s15(t, dur):
    u = t / dur
    sc = dcam((0.8, 3.2, 6.8), (-0.3, 1.6, 0.9), u, 0.04, fov=40)
    ss.doyle_porch(sc, t)
    doyle_seated(sc, "smile", t=t)
    return sc


def s16(t, dur):
    u = t / dur
    sc = dcam((0.6, 2.9, 6.4), (0.1, 1.9, 1.0), u, 0.12, fov=40)
    ss.doyle_porch(sc, t)
    d = doyle_seated(sc, "suspicious" if t < 1.5 else "joy", dict(ar=(70, -10), er=40), t=t)
    r = character(sc, RUDY, ss.RUDY_P, yaw=-80, face="smile", pose=dict(ar=(80, -10), al=(10, 6)))
    k = clamp((t - 0.6) / 0.8)
    pp = r["hand_r"] * (1 - k) + d["hand_r"] * k + np.array([0, 0.08, 0])
    ss.piece(sc, T(*pp))
    return sc


def s17(t, dur):
    k, tt = sub3(t, 17, dur)
    sky = [((95, 175, 255), (205, 235, 255)), ((120, 130, 150), (170, 176, 190)), ((240, 190, 140), (255, 220, 180))][k]
    sc = dcam((0.6, 2.9, 6.4), (0.1, 1.9, 1.0), 0, 0, 40, sky=sky)
    ss.doyle_porch(sc, t)
    doyle_seated(sc, "smile", t=t)
    character(sc, RUDY, ss.RUDY_P, yaw=-80, face=("smile", "neutral", "sleep")[k], pose=dict(ar=(80, -10)))
    if k == 1:
        from umbrella_sets import rain
        rain(sc, t, 0.7)
    elif k == 2:
        def leaves(d, W, H):
            rng = np.random.RandomState(5)
            for i in range(20):
                x, y0, sp = rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0.2, 0.4)
                y = ((y0 + tt * sp) % 1.0) * H
                c = [(220, 120, 40), (240, 180, 60), (200, 80, 40)][i % 3]
                d.ellipse([x * W - 14, y - 8, x * W + 14, y + 8], fill=c + (255,))
        sc.overlay(leaves)
    return sc


def s18(t, dur):
    u = t / dur
    top = np.array([ss.TABLE[0], ss.PORCH_Y + 0.86, ss.TABLE[2]])
    sc = dcam(top + np.array([0.0, 1.7, 1.9]), top, u, 0.14, fov=40)
    ss.doyle_porch(sc, t)
    return sc


def s19(t, dur):
    u = t / dur
    top = np.array([ss.TABLE[0], ss.PORCH_Y + 0.86, ss.TABLE[2]])
    sc = dcam(top + np.array([0.3, 1.4, 0.4]), top + np.array([0.3, 0, 0]), u, 0.06, fov=40)
    ss.doyle_porch(sc, t, missing=0.6)
    add_emote(sc, "?", top + np.array([0.3, 0.3, 0]), t, size=0.5, dy=0.3, start=0.3)
    return sc


# ------------------------------------------------------- 20-25: game day
def s20(t, dur):
    u = t / dur
    sc = dcam((-4.0 + 6.0 * u, 3.6, 10.0), (0.0 + 2.0 * u, 2.0, -4.0), u, 0.0, fov=46)
    ss.soccer_field(sc, t)
    confetti(sc, t, n=40)
    return sc


def s21(t, dur):
    u = t / dur
    pose = dict(lean=40, al=(70, -10), ar=(70, -10), el=30, er=30)
    sc = dcam((0.8, 1.2, 2.6), (0.0, 0.5, 0.2), u, 0.0, fov=40)
    sets.town(sc)
    a = character(sc, RUDY, (0, 0, 0), face="grit", pose=pose)
    if int(t * 6) % 2:
        sparks(sc, a["foot_r"] + np.array([0, 0.2, 0.2]), t, seed=4, n=2, r=0.2, color=(255, 255, 255))
    return sc


def s22(t, dur):
    u = t / dur
    pose = dict(lean=10, al=(70, -30), ar=(70, -30), el=70, er=70, head=(0, -30, 0))
    sc = dcam((0.4, 4.0, 2.2), (0.0, 1.6, 0.0), u, 0.0, fov=40)
    sets.town(sc)
    a = character(sc, RUDY, (0, 0, 0), face="worried", pose=pose)
    add_emote(sc, "sweat", a["head_top"], t, size=0.5, dx=0.5, dy=0.1, start=0.4)
    return sc


def s23(t, dur):
    u = t / dur
    sc = dcam((1.2, 0.6, 3.4), (0.0, 0.45, 0.0), u, 0.0, fov=40, blur=0)
    sets.town(sc)
    turn = clamp((t - 0.1) / 0.25)
    a = character(sc, RUDY, (0, 0, 0), yaw=-90 * turn, face="shock")
    ss.shoe_sparkles(sc, a, t)
    return sc


def s24(t, dur):
    u = t / dur
    sc = dcam((1.2, 2.8, 8.4), (0.2, 1.8, 1.4), u, 0.04, fov=44)
    ss.doyle_porch(sc, t)
    doyle_seated(sc, "smile", t=t)
    a = character(sc, RUDY, (1.6, 0, 3.4), yaw=-30, face="angry", pose=dict(lean=12, al=(4, 2), ar=(4, 2), head=(0, -14, 0)))
    add_emote(sc, "anger", a["head_top"], t, size=0.55, dx=0.5, dy=0.05, start=0.3)
    return sc


def s25(t, dur):
    u = t / dur
    x = 2.0 - 4.0 * u
    sc = dcam((0.0, 2.4, 9.0), (0.0, 1.6, 1.0), u, 0.0, fov=44)
    sets.town(sc)
    w = math.sin(t * 16)
    a = character(sc, RUDY, (x, 0, 1.0), yaw=90, face="effort",
                  pose=dict(lean=30, al=(120 + 40 * w, -20), ar=(120 - 40 * w, -20), ll=30 * w, lr=-30 * w))
    ss.shoe_sparkles(sc, a, t)
    speed_lines(sc, t, cx=0.5, cy=0.4, n=12, inner=0.4, alpha=90)
    return sc


# ------------------------------------------------------- 26-35: the reveal
def s26(t, dur):
    u = t / dur
    pose = dict(ar=(110, -20), er=40)
    c = ss.CHAIR
    ll = DOYLE["leg"][1] * DOYLE["s"]
    pos = (c[0], c[1] + 0.75 - ll, c[2])
    sc = doyle_cam(pose, u, dist=5.0, push=0.06, ang=40)
    ss.doyle_porch(sc, t, rock=False)
    d = doyle_seated(sc, "joy", pose)
    ss.piece(sc, T(*(d["hand_r"] + np.array([0, 0.12, 0.05]))) @ RX(-70), s=1.3)
    sparks(sc, d["hand_r"] + np.array([0, 0.25, 0.05]), t, seed=2, n=3, r=0.2, color=(255, 255, 230))
    return sc


def s27(t, dur):
    u = t / dur
    top = np.array([ss.TABLE[0], ss.PORCH_Y + 0.86, ss.TABLE[2]])
    k = clamp((t - 0.2) / 0.4)
    sc = dcam(top + np.array([0.15, 1.1, 0.35]), top + np.array([0.1, 0, 0.1]), u, 0.0, fov=38)
    ss.doyle_porch(sc, t, missing=0.04)
    ss.piece(sc, T(*(top + np.array([0.12, 0.02 + 0.5 * (1 - k), 0.12]))), s=1.0)
    if k >= 1:
        sparks(sc, top + np.array([0.12, 0.1, 0.12]), t, seed=4, n=5, r=0.3)
    return sc


def s28(t, dur):
    u = t / dur
    top = np.array([ss.TABLE[0], ss.PORCH_Y + 0.86, ss.TABLE[2]])
    sc = dcam(top + np.array([0.0, 1.5 + 0.3 * u, 1.6 + 0.5 * u]), top, u, 0.0, fov=40)
    ss.doyle_porch(sc, t, state="full")
    return sc


def s29(t, dur):
    u = t / dur
    top = np.array([ss.TABLE[0], ss.PORCH_Y + 0.86, ss.TABLE[2]])
    off = np.array([-0.5 + 1.0 * u, 0, 0])
    sc = dcam(top + off + np.array([0, 1.2, 0.25]), top + off, u, 0.0, fov=38)
    ss.doyle_porch(sc, t, state="full")
    return sc


def s30(t, dur):
    u = t / dur
    top = np.array([ss.TABLE[0], ss.PORCH_Y + 0.86, ss.TABLE[2]])
    tr = top + np.array([0.56, 0.0, -0.3])
    sc = dcam(tr + np.array([0, 0.8, 0.15]), tr, u, 0.2, fov=38)
    ss.doyle_porch(sc, t, state="full")
    sparks(sc, tr + np.array([0, 0.05, 0]), t, seed=2, n=3, r=0.1, color=(255, 240, 160))
    return sc


def doyle_cam(pose, u, dist=3.0, push=0.08, ang=50, up=0.15, fov=36):
    """Close-up on Mrs Doyle as she actually sits (facing +x): aim at her real head, camera `ang` degrees
    round from her front toward the porch front (+z)."""
    p = sit()
    p.update(al=(50, 4), ar=(50, 4))
    p.update(pose or {})
    ll = DOYLE["leg"][1] * DOYLE["s"]
    c = ss.CHAIR
    h = probe(DOYLE, (c[0], c[1] + 0.75 - ll, c[2]), 90, p)["head"]
    a = math.radians(ang)
    dv = np.array([math.cos(a), 0.0, math.sin(a)])
    return dcam(h + dv * dist + np.array([0, up, 0]), h - np.array([0, 0.1, 0]), u, push, fov)


def _doyle_cu(t, dur, face, pose=None, dist=3.0, push=0.08):
    u = t / dur
    c = ss.CHAIR
    ll = DOYLE["leg"][1] * DOYLE["s"]
    pos = (c[0], c[1] + 0.75 - ll, c[2])
    sc = doyle_cam(pose, u, dist=dist * 1.7, push=push * 0.5)
    ss.doyle_porch(sc, t, state="full", rock=False)
    d = doyle_seated(sc, face, pose)
    return sc, d


def s31(t, dur):
    sc, d = _doyle_cu(t, dur, "sparkle")
    return sc


def s32(t, dur):
    sc, d = _doyle_cu(t, dur, "smile", dict(lean=25, al=(20, 30), el=20), dist=3.6)
    return sc


def s33(t, dur):
    u = t / dur
    sc, d = _doyle_cu(t, dur, "smile", dict(al=(60, -20), ar=(60, -20), el=50, er=50), dist=2.6, push=0.1)
    ss.glove_pair(sc, T(*((d["hand_l"] + d["hand_r"]) / 2 + np.array([0, 0.12, 0.15]))) @ RY(-40))
    ls.glow_at(sc, (d["hand_l"] + d["hand_r"]) / 2 + np.array([0, 0.2, 0.15]), 0.7, (255, 230, 160), 50)
    return sc


def s34(t, dur):
    sc, d = _doyle_cu(t, dur, "suspicious", dist=2.6)
    return sc


def s35(t, dur):
    sc, d = _doyle_cu(t, dur, "wink", dict(ar=(30, 60), er=-40), dist=2.4, push=0.14)
    sparks(sc, d["head_top"] + np.array([0.3, -0.2, 0]), t, seed=6, n=3, r=0.3)
    return sc


# ------------------------------------------------------- 36-43: the shootout
def s36(t, dur):
    u = t / dur
    sc = dcam((0.9, 0.6, 6.4), (0.0, 0.45, 3.4), u, 0.0, fov=40, blur=0)
    ss.doyle_porch(sc, t)
    turn = clamp((t - 0.2) / 0.5)
    a = character(sc, RUDY, (0.0, 0, 1.4 + 2.0), yaw=lerp(0, 180, turn), face="joy")
    ss.shoe_sparkles(sc, a, t, color=(255, 210, 90))
    ls.glow_at(sc, a["foot_l"] + np.array([0.2, 0.1, 0]), 0.6, (255, 210, 90), 70)
    return sc


def s37(t, dur):
    u = t / dur
    x = -5.0 + 10.0 * u
    sc = dcam((x - 2.0, 2.0, 7.0), (x, 1.6, 1.0), u, 0.0, fov=44)
    sets.town(sc)
    a = character(sc, RUDY, (x, 0, 1.0), yaw=90, face="grit", pose=dict(walk(t, 16, 40), lean=20))
    ss.gloves(sc, a)
    ss.shoe_sparkles(sc, a, t)
    speed_lines(sc, t, cx=0.5, cy=0.4, n=18, inner=0.35, alpha=120)
    return sc


GK = np.array([0.0, 0.0, ss.GOAL_Z + 0.5])


def s38(t, dur):
    u = t / dur
    x = lerp(-5.0, 0.0, clamp(t / 1.4))
    sc = dcam((4.0, 3.0, 6.0), (0.0, 1.4, ss.GOAL_Z + 1.0), u, 0.0, fov=46)
    ss.soccer_field(sc, t)
    a = character(sc, RUDY, (x, 0, GK[2]), yaw=90 if t < 1.4 else 0, face="grit", pose=walk(t, 14, 34) if t < 1.4 else None)
    ss.gloves(sc, a)
    return sc


def s39(t, dur):
    u = t / dur
    sc = dcam((2.4, 2.0, ss.SPOT[2] + 6.4), (0.3, 1.2, ss.SPOT[2] + 0.6), u, 0.0, fov=40)
    ss.soccer_field(sc, t)
    character(sc, STRIKER, ss.SPOT + np.array([0.6, 0, 1.0]), yaw=180, face="grit", pose=dict(lean=25, ar=(40, 10)))
    ss.ball(sc, T(*(ss.SPOT + np.array([0, 0.23, 0]))))
    return sc


def s40(t, dur):
    """'I watched the hips': Rudy's eyes, then the striker's hips turning."""
    if t < dur * 0.5:
        sc = head_cu(RUDY, GK, 0, dict(lean=12), t / dur, dist=1.8, fov=34, push=0.15)
        ss.soccer_field(sc, t, crowd=False)
        a = character(sc, RUDY, GK, face="suspicious", pose=dict(lean=12, al=(40, 30), ar=(40, 30)))
        ss.gloves(sc, a)
    else:
        tt = t - dur * 0.5
        hip = ss.SPOT + np.array([0.3, 1.1, 0.6])
        sc = dcam(hip + np.array([0.0, 0.1, -2.4]), hip, 0, 0, 38)
        ss.soccer_field(sc, t, crowd=False)
        character(sc, STRIKER, ss.SPOT + np.array([0.3, 0, 0.6]), yaw=180 + 30 * clamp(tt / 0.3), face="grit",
                  pose=dict(lean=20, roll=10 * clamp(tt / 0.3)))
        ss.ball(sc, T(*(ss.SPOT + np.array([0, 0.23, 0]))))
    return sc


def s41(t, dur):
    u = t / dur
    k = clamp(t / dur) ** 0.7
    sc = dcam((1.5, 1.6, ss.GOAL_Z + 6.0), (-0.8, 1.2, ss.GOAL_Z + 0.5), u, 0.0, fov=42)
    ss.soccer_field(sc, t)
    a = character(sc, RUDY, (lerp(0, -1.5, k), 0.2 + 0.9 * math.sin(k * math.pi * 0.8), GK[2]), yaw=0, face="grit",
                  pose=dict(roll=lerp(0, 75, k), al=(170, -10), ar=(170, -10), ll=20, lr=-20), shadow_y=0)
    ss.gloves(sc, a)
    ss.ball(sc, T(lerp(0.0, -2.0, k), lerp(0.25, 1.4, k), lerp(ss.SPOT[2], GK[2] + 0.3, k)))
    speed_lines(sc, t, cx=0.4, cy=0.45, n=14, inner=0.4, alpha=90)
    return sc


def s42(t, dur):
    u = t / dur
    sh = 0.08 * math.sin(t * 60) * max(0.0, 1 - t / 0.5)
    pose = dict(roll=75, al=(170, -10), ar=(170, -10), ll=20, lr=-20)
    pos = (-1.5, 1.0, GK[2])
    a = None
    sc = dcam((-0.2 + sh, 1.8 + sh, GK[2] + 2.6), (-2.2, 1.4, GK[2]), u, 0.0, fov=38)
    ss.soccer_field(sc, t)
    a = character(sc, RUDY, pos, face="grit", pose=pose, shadow_y=0)
    ss.gloves(sc, a)
    ss.ball(sc, T(*((a["hand_l"] + a["hand_r"]) / 2 + np.array([-0.2, 0.0, 0.25]))))
    if t < 2 / 30:
        sc.flash = 1.0
    ls.sticker(sc, a["head"], "SAVED!", t, start=0.05, hold=1.0, size=0.6, dx=1.0, dy=0.9, color=(255, 230, 80))
    return sc


def s43(t, dur):
    u = t / dur
    sc = dcam((0.6, 3.6, 7.0), (0.0, 1.2, GK[2] + 1.5), u, 0.0, fov=44)
    ss.soccer_field(sc, t)
    character(sc, RUDY, (0.0, 0, GK[2] + 1.5), face="laugh", pose=dict(al=(160, -20), ar=(160, -20)))
    for i in range(6):
        a_ = i * 1.05
        character(sc, HAWK(i), (1.2 * math.cos(a_), 0.3 * (i % 2), GK[2] + 1.5 + 1.0 * math.sin(a_)),
                  yaw=math.degrees(math.atan2(-math.cos(a_), -math.sin(a_))), face="laugh",
                  pose=dict(al=(150, -20), ar=(150, -20), lean=15))
    confetti(sc, t, n=60)
    return sc


# ------------------------------------------------------- 44-46: the ending
def s44(t, dur):
    u = t / dur
    sc = dcam((-6.0, 2.4, 2.6), (-11.0, 1.8, -2.0), u, 0.12, fov=40)
    ss.soccer_field(sc, t)
    a = character(sc, DOYLE, (-10.4, 0, -1.2), yaw=60, face="joy", pose=dict(ar=(160, -20 - 15 * math.sin(t * 8))))
    ss.piece(sc, T(*(a["hand_r"] + np.array([0, 0.15, 0]))) @ RX(-80), s=1.6)
    add_emote(sc, "stars", a["head_top"], t, size=0.55, dx=0.5, dy=0.2, start=0.4)
    return sc


def s45(t, dur):
    u = t / dur
    sc = dcam((-8.6, 2.2, 4.2), (-9.8, 1.4, -1.1), u, 0.04, fov=42)
    ss.soccer_field(sc, t)
    k = clamp(t / 0.7)
    hug = dict(al=(80, -30), ar=(80, -30), el=50, er=50)
    character(sc, DOYLE, (-10.2, 0, -1.2), yaw=70, face="joy", pose=hug if k >= 1 else None)
    a = character(sc, RUDY, (lerp(-7.6, -9.5, k), 0, -1.0), yaw=-100, face="joy",
                  pose=hug if k >= 1 else walk(t, 12, 30))
    ss.gloves(sc, a)
    return sc


def s46(t, dur):
    u = t / dur
    sc = dcam((0.8, 2.9, 6.4), (0.1, 1.8, 1.0), u, 0.0, fov=40)
    ss.doyle_porch(sc, t, missing=0.3)
    doyle_seated(sc, "joy", dict(ar=(70, -10), er=40), t=t)
    r = character(sc, RUDY, ss.RUDY_P, yaw=-80, face="joy", pose=dict(ar=(80, -10)))
    ss.piece(sc, T(*(r["hand_r"] + np.array([0, 0.1, 0]))))
    sparks(sc, np.array([ss.TABLE[0], ss.PORCH_Y + 1.0, ss.TABLE[2]]), t, seed=3, n=4, r=0.5)
    return sc


_FNS = [globals()[f"s{i:02d}"] for i in range(1, len(LINES) + 1)]
SHOTS = [(i + 1, 1.4, txt, fn) for i, (txt, fn) in enumerate(zip(LINES, _FNS))]
SHOTS, WORD_TIMES = load_timing(SHOTS, TIMING_FILE)
WT.update(WORD_TIMES)
