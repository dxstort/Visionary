"""When You SNEEZE, You SWITCH Places: shot list. Each shot: (number, seconds, caption text, fn(t, dur) -> Scene)."""
import os

TIMING_FILE = "sneeze_timing.json"
SPOKEN = {"Mr": "mister", "Mrs": "missus", "nine-year-old": "nine year old", "Hilltop": "hill top",
          "CREEEAK": "creak", "CHOOO": "choo", "ACHOO": "achoo", "Arrr": "arr", "Dad's": "dad's"}
PHONES = {"achoo": "AH CH UW", "choo": "CH UW", "arr": "AA R", "gomez": "G OW M EH Z", "patel": "P AH T EH L",
          "whoever's": "HH UW EH V ER Z", "popsicle": "P AA P S IH K AH L", "tomatoes": "T AH M EY T OW Z",
          "creak": "K R IY K", "podium": "P OW D IY AH M", "hoodie": "HH UH D IY"}

LINES = [
    "In this town, when you SNEEZE,",
    "you swap places with whoever's standing closest.",
    "Nobody knows why. Everybody carries tissues.",
    "Dad ties EVERYTHING with his garden hose.",
    "Fences. Bikes. Wobbly chairs.",
    "Last Tuesday, he sneezed in the middle of a knot.",
    "ACHOO! He swapped with Mr Gomez, next door.",
    "Mr Gomez waters his tomatoes in a pirate hat. Nobody asks.",
    "Dad landed in the tomatoes. SPLAT.",
    "Mr Gomez landed holding the hose. Arrr, he said. Of course.",
    "Then Mrs Patel sneezed in math class. Chalk dust.",
    "She swapped with a kid in the back row.",
    "Now a nine-year-old was teaching fractions.",
    "A pizza is a fraction, he said. Nobody argued.",
    "I'm the kid in the blue hoodie.",
    "And nobody EVER listens to me.",
    "Not Dad. Not my class. Definitely not the mayor.",
    "The mayor wears a tall hat and a very nervous tie.",
    "One crowd and he freezes like a popsicle.",
    "Saturday, the whole town squeezed onto the new Hilltop Bridge.",
    "I stood right behind the mayor.",
    "CREEEAK.",
    "The bridge began to WOBBLE.",
    "The crowd screamed. The mayor froze solid.",
    "I knew the fix. Dad's garden hose!",
    "I shouted. Nobody heard me.",
    "Then the feather on the mayor's hat tickled my nose.",
    "AH... AH... CHOOO!",
    "I swapped with the mayor.",
    "Suddenly I was standing at the podium.",
    "Everyone stopped. Everyone looked at ME.",
    "Turns out people listen to whoever stands HERE.",
    "EVERYBODY FREEZE! Dad! Tie the bridge to the tree!",
    "Dad sprinted over with the hose.",
    "One knot. Two knots. Dad knots.",
    "The wobble stopped. Dead still.",
    "The whole town cheered.",
    "Confetti fell. It tickled my nose.",
    "ACHOO! I swapped back.",
    "The mayor took a deep breath. His tie stopped shaking.",
    "The kid in the blue hoodie saved our bridge, he said.",
    "And this time, everyone listened.",
    "He even let me cut the ribbon.",
    "Snip.",
    "The bridge is still tied up with that hose.",
    "Dad wants it back.",
]
import math  # noqa: E402

import numpy as np  # noqa: E402

import laughs_sets as ls  # noqa: E402
import sets  # noqa: E402
import shoes_sets as ss  # noqa: E402
import sneeze_sets as ns  # noqa: E402
from cast import DAD, MAYOR, _spec, character, crowd_spec, sit  # noqa: E402
from engine import RX, RY, RZ, T, add_emote, clamp, lerp, speed_lines, xf  # noqa: E402
from laughs import dcam, dfcam, head_cu, ht  # noqa: E402
from shots import confetti, sparks, walk  # noqa: E402
from story import load_timing  # noqa: E402

NARR = _spec(name="Narrator", style="tuft", s=0.98, skin=(236, 190, 150), shirt=(52, 112, 232), hoodie=True,
             accent=(250, 250, 250), pants=(46, 56, 100), shoes=(250, 250, 250), hair=(90, 60, 40), sleeve=0.9,
             backpack=(244, 150, 40))
DAD_S = dict(DAD, name="Dad", floral=False, shirt=(64, 156, 78), sleeve=0.5)
PATEL = _spec(name="Mrs Patel", style="bun", s=1.2, skin=(214, 156, 118), shirt=(250, 250, 252), inner=(130, 176, 232),
              cardigan=True, pants=(70, 70, 100), shoes=(90, 70, 70), hair=(30, 24, 28), glasses=True,
              accent=(240, 120, 160), sleeve=0.86)
GOMEZ = _spec(name="Mr Gomez", style="pirate", s=1.3, torso=(1.2, 1.0, 0.6), arm=(0.58, 1.0), skin=(190, 132, 96),
              shirt=(250, 250, 250), striped=((246, 246, 250), (56, 88, 168)), pants=(110, 88, 60),
              shoes=(60, 46, 40), hair=(30, 24, 24), sleeve=0.5)
MAYOR_S = dict(MAYOR, badge=True)
GLOVE = (244, 204, 56)
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


def kid_spec(i):
    return crowd_spec(i)


def sneeze_pose(t, t0, base=None):
    """Head tips back, then snaps forward at t0."""
    p = dict(base or {})
    if t < t0:
        w = clamp((t - (t0 - 0.55)) / 0.55)
        p.update(lean=-9 * w, head=(0, -22 * w, 0))
    else:
        d = clamp(1.0 - (t - t0) / 0.45)
        p.update(lean=22 * d, head=(0, 26 * d, 3 * math.sin(t * 40) * d))
    return p


def sneeze_face(t, t0):
    return "jaw" if t < t0 else ("effort" if t < t0 + 0.4 else "shock")


def achoo(sc, a, t, t0, size=0.62, dx=0.6, dy=0.5):
    ls.sticker(sc, a["head_top"], "ACHOO!", t, start=t0, hold=0.9, size=size, dx=dx, dy=dy)


def hose_sash(sc, a):
    Mt = a["Mt"]
    pts = [xf(Mt, p) for p in ((-0.55, 0.62, 0.0), (-0.3, 0.35, 0.4), (0.1, -0.1, 0.44), (0.5, -0.55, 0.4),
                               (0.64, -0.62, 0.0))]
    ns.hose(sc, pts, r=0.09, step=1.3)


def dad(sc, pos, yaw=0, face="grin", pose=None, hose_on=False, shadow=True):
    a = character(sc, DAD_S, pos, yaw=yaw, face=face, pose=pose, shadow=shadow)
    ss.gloves(sc, a, color=GLOVE)
    if hose_on:
        hose_sash(sc, a)
    return a


# ======================================================= 1-3: the rule
def s01(t, dur):
    u = t / dur
    t0 = word_t(1, 5, 1.1)
    sw = t0 + 0.4
    A, B = kid_spec(4), kid_spec(2)
    sc = dcam((0.2, 0.8, 11.0), (0.0, 1.9, 0.0), u, 0.06, fov=42)
    sets.town(sc)
    a = character(sc, A, (0.9 if t >= sw else -0.9, 0, 0), yaw=0, face=sneeze_face(t, t0), pose=sneeze_pose(t, t0))
    b = character(sc, B, (-0.9 if t >= sw else 0.9, 0, 0), yaw=0, face="shock" if t >= sw else "neutral")
    achoo(sc, a, t, t0)
    ns.swap_fx(sc, (-0.9, 0, 0), (0.9, 0, 0), t, sw)
    return sc


def s02(t, dur):
    u = t / dur
    sw = word_t(2, 1, 0.5) + 0.6
    xs = (-1.9, 0.0, 1.9)
    specs = [kid_spec(i) for i in (5, 6, 3)]
    sc = dcam((0.0, 3.6, 12.5), (0.0, 1.5, 0.0), u, 0.0, fov=44)
    sets.town(sc)
    order = [0, 1, 2]
    if t >= sw:
        order[1], order[2] = order[2], order[1]
    for i, x in enumerate(xs):
        who = order[i]
        pose = sneeze_pose(t, sw - 0.15) if who == 1 and t < sw + 0.4 else None
        character(sc, specs[who], (x, 0, 0), yaw=0, face="shock" if (who in (1, 2) and t >= sw) else "smile", pose=pose)
    ls.sticker(sc, (0.0, 3.0, 0), "SWAP!", t, start=sw, hold=1.0, size=0.8, dx=0.0, dy=0.6, color=(130, 230, 255))
    ns.swap_fx(sc, (0.0, 0, 0), (1.9, 0, 0), t, sw)
    return sc


def s03(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.8, 12.0), (0.0, 1.7, 0.0), u, 0.1, fov=42)
    sets.town(sc)
    xs = (-2.0, 0.0, 2.0)
    for i, x in enumerate(xs):
        spec = kid_spec(i + 8)
        face = "shock" if i % 2 == 0 and t < 1.3 else "smile"
        a = character(sc, spec, (x, 0, 0), yaw=0, face=face, pose=dict(ar=(60, -10), er=70, al=(20, 6)))
        ns.tissue_box(sc, T(*(a["hand_r"] + np.array([0.0, 0.1, 0.25]))))
    add_emote(sc, "?", (-2.0, 3.3, 0), t, size=0.55, dx=0.0, dy=0.2, start=0.2, hold=1.4)
    return sc


# ======================================================= 4-10: Dad and Mr Gomez
def s04(t, dur):
    u = t / dur
    k = clamp((t - 0.2) / 1.3)
    sc = dcam((-4.6, 3.2, 10.6), (-0.8, 2.1, 0.4), u, 0.08, fov=42)
    ns.garden(sc, t, fence_hose=k)
    dad(sc, (-1.4, 0, 0.5), yaw=90, face="grin", pose=dict(lean=14, ar=(75, -10), er=50, al=(30, 6)), hose_on=True)
    sparks(sc, (-0.2, 1.4, 0.5), t, seed=5, n=3, r=0.5)
    return sc


def s05(t, dur):
    k, tt = sub3(t, 5, dur)
    if k == 0:
        sc = dcam((-3.4, 2.6, 9.6), (-0.4, 1.7, 0.8), 0, 0, 42)
        ns.garden(sc, t, fence_hose=1.0)
        dad(sc, (-1.2, 0, 1.4), yaw=90, face="smirk", pose=dict(ar=(40, 10)))
    elif k == 1:
        sc = dcam((2.0, 2.4, 9.6), (0.0, 1.2, 0.0), 0, 0, 42)
        sets.town(sc)
        bk = np.array([0.0, 0.0, 0.0])
        for wx in (-0.9, 0.9):
            sc.blob(T(wx, 0.55, 0), (1.1, 1.1, 0.12), (40, 40, 48), layer=5, n=14, m=5)
            sc.blob(T(wx, 0.55, 0), (0.85, 0.85, 0.14), (210, 210, 220), layer=5, n=14, m=5)
        sc.box(T(0, 0.95, 0) @ RZ(18), (1.8, 0.1, 0.1), (230, 70, 60), layer=6)
        sc.box(T(0.5, 1.2, 0), (0.1, 0.8, 0.1), (230, 70, 60), layer=6)
        sc.box(T(0.5, 1.7, 0), (0.7, 0.08, 0.08), (60, 60, 70), layer=6)
        ns.hose(sc, [(-0.9 + 0.08 * i, 0.3 + 0.7 * ((i % 4) / 3.0), 0.12) for i in range(24)], r=0.07)
        ns.hose(sc, [(0.4 + 0.12 * math.sin(i), 1.7 - 0.07 * i, 0.12) for i in range(14)], r=0.07)
    else:
        sc = dcam((1.0, 2.6, 9.0), (0.0, 1.3, 0.0), 0, 0, 42)
        sets.town(sc)
        sets.chair(sc, 0.0, 0.0, yaw=0, h=1.3)
        ns.hose(sc, [(-0.7, 0.2 + 0.18 * i, 0.5 * math.sin(i)) for i in range(8)] +
                [(0.7, 1.4 - 0.18 * i, 0.4 * math.cos(i)) for i in range(8)], r=0.08)
        add_emote(sc, "sweat", (0.0, 2.3, 0), tt, size=0.5, dx=0.6, dy=0.1, start=0.2)
    return sc


def s06(t, dur):
    u = t / dur
    t0 = word_t(6, 9, 1.5) + 0.25
    pos = (-1.4, 0, 0.5)
    pose = sneeze_pose(t, t0, dict(ar=(75, -10), er=50, al=(30, 6)))
    sc = head_cu(DAD_S, pos, 90, pose, u, dist=6.4, up=0.3, fov=38, push=0.1)
    ns.garden(sc, t, fence_hose=1.0)
    a = dad(sc, pos, yaw=90, face=sneeze_face(t, t0), pose=pose)
    return sc


def s07(t, dur):
    u = t / dur
    t0 = word_t(7, 0, 0.25)
    sw = t0 + 0.35
    sc = dcam((0.0, 3.4, 12.0), (0.0, 1.9, 0.0), u, 0.05, fov=44)
    ns.garden(sc, t, fence_hose=1.0)
    pa, pb = (-1.3, 0, 0.6), (1.3, 0, 0.6)
    swp = t >= sw
    a = dad(sc, pb if swp else pa, yaw=90 if not swp else -90, face=sneeze_face(t, t0) if t < sw + 0.3 else "shock",
            pose=sneeze_pose(t, t0) if t < sw else None)
    character(sc, GOMEZ, pa if swp else pb, yaw=-90 if not swp else 90, face="shock" if swp else "smile")
    achoo(sc, a, t, t0, dx=-0.6)
    ns.swap_fx(sc, pa, pb, t, sw)
    return sc


def s08(t, dur):
    u = t / dur
    sc = dcam((-1.5, 3.0, 10.4), (0.7, 2.2, 0.0), u, 0.1, fov=42)
    ns.garden(sc, t)
    g = character(sc, GOMEZ, (1.6, 0, 0.4), yaw=-20, face="smirk", pose=dict(ar=(55, 10), er=50, al=(20, 6)))
    sc.box(T(*(g["hand_r"] + np.array([0.15, 0.0, 0.2]))), (0.5, 0.4, 0.3), (60, 140, 200), layer=7)
    k = character(sc, kid_spec(3), (-0.8, 0, 2.6), yaw=40, face="neutral")
    add_emote(sc, "?", k["head_top"], t, size=0.55, dx=0.4, dy=0.2, start=0.8, hold=1.6)
    return sc


def s09(t, dur):
    u = t / dur
    sc = dcam((1.4, 2.8, 11.0), (1.7, 1.6, 0.0), u, 0.0, fov=42)
    ns.garden(sc, t)
    tl = word_t(9, 1, 0.3)
    th = word_t(9, 5, 1.5) - 0.12 if WT.get(9) else tl + 0.9
    fall = clamp((t - th + 0.35) / 0.35)
    a = dad(sc, (1.7, lerp(3.2, 0.0, fall ** 2), 0.2), yaw=0,
            face="shock" if t < th + 0.15 else "stung",
            pose=dict(roll=lerp(-30, 8, fall), al=(150 + 20 * math.sin(t * 20), 20), ar=(150 - 20 * math.sin(t * 20), 20)))
    for k in range(7):
        a_ = k * 0.9
        if t > th:
            sparks(sc, (1.7 + 0.8 * math.cos(a_), 0.5 + 1.2 * clamp((t - th) * 2), 0.5 * math.sin(a_)), t - th,
                   seed=k, n=2, r=0.15, color=(226, 56, 48))
    ls.sticker(sc, a["head_top"], "SPLAT!", t, start=th, hold=1.2, size=0.8, dx=0.9, dy=0.3, color=(255, 90, 80))
    return sc


def s10(t, dur):
    u = t / dur
    pos = (-1.5, 0, 0.6)
    sc = dcam((-3.9, 2.8, 10.0), (-1.5, 2.2, 0.0), u, 0.1, fov=42)
    ns.garden(sc, t, fence_hose=0.6)
    a = character(sc, GOMEZ, pos, yaw=70, face="laugh" if t > word_t(10, 6, 1.4) else "shock",
                  pose=dict(ar=(80, -10), er=70, al=(40, 6), head=(0, 0, 5 * math.sin(t * 8))))
    ns.nozzle(sc, a["M_hand_r"] @ T(0, -0.1, 0.1))
    ns.hose(sc, [(-1.3, 0.8, 0.9), (-1.0, 0.3, 1.4), (-1.9, 0.3, 1.8), (-2.4, 0.9, 1.2)], r=0.08)
    ls.sticker(sc, a["head_top"], "ARRR!", t, start=word_t(10, 6, 1.4), hold=1.2, size=0.8, dx=0.8, dy=0.4,
               color=(255, 214, 80))
    return sc


# ======================================================= 11-14: Mrs Patel's class
BACK_ROW = (1, 0)


def patel_pose(t, t0):
    return sneeze_pose(t, t0, dict(ar=(70, -10), er=70, al=(20, 6)))


def s11(t, dur):
    u = t / dur
    t0 = word_t(11, 3, 1.3) + 0.3
    sc = dcam((-0.5, 4.0, -5.6), (0.0, 2.6, 4.4), u, 0.06, fov=50)
    ns.class_front(sc)
    sets.class_desks(sc, t, frozen=False, faces=("smile", "neutral"))
    a = character(sc, PATEL, (0.0, 0, 4.4), yaw=180, face=sneeze_face(t, t0), pose=patel_pose(t, t0))
    ls.dust(sc, a["head_top"] + np.array([0, -0.8, -0.3]), t, t0 - 0.3, n=10)
    ls.dust(sc, a["hand_r"], t, t0 - 0.8, n=8)
    achoo(sc, a, t, t0)
    return sc


def s12(t, dur):
    u = t / dur
    sw = word_t(12, 1, 0.6) + 0.25
    sc = dcam((0.8, 4.8, -5.8), (0.0, 1.8, 2.4), u, 0.04, fov=54)
    ns.class_front(sc)
    pa = (0.0, 0, 4.4)
    pos = sets.class_desks(sc, t, frozen=False, skip=(BACK_ROW,), faces=("smile",))
    bx, bz = pos[BACK_ROW]
    spec = kid_spec(11)
    ll = spec["leg"][1] * spec["s"]
    swp = t >= sw
    if swp:
        character(sc, spec, pa, yaw=180, face="shock")
        sets.chair(sc, bx, bz, yaw=0, c=(214, 96, 70))
        character(sc, PATEL, (bx, 0.86 - PATEL["leg"][1] * PATEL["s"], bz + 0.05), yaw=0, face="shock",
                  pose=sit(), shadow=False)
    else:
        character(sc, PATEL, pa, yaw=180, face="worried", pose=sneeze_pose(t, sw - 0.2))
        character(sc, spec, (bx, 0.86 - ll, bz + 0.05), yaw=0, face="smile", pose=sit(), shadow=False)
    ns.swap_fx(sc, pa, (bx, 0.0, bz), t, sw)
    return sc


def teacher_kid(sc, t, face="grin", pose=None):
    return character(sc, kid_spec(11), (0.0, 0, 4.4), yaw=180, face=face, pose=pose)


def s13(t, dur):
    u = t / dur
    sc = dcam((0.6, 3.8, -5.0), (0.0, 2.4, 5.0), u, 0.06, fov=48)
    ns.class_front(sc)
    sets.class_desks(sc, t, frozen=False, skip=(BACK_ROW,), faces=("smile", "neutral"))
    sets.chair(sc, -4.2, -3.6, yaw=0, c=(214, 96, 70))
    p = sit()
    p.update(ar=(70, 6), head=(0, -10, 0))
    character(sc, PATEL, (-4.2, 0.86 - PATEL["leg"][1] * PATEL["s"], -3.55), yaw=0, face="shock", pose=p, shadow=False)
    a = teacher_kid(sc, t, "grin", dict(ar=(120, -10), er=30, al=(10, 6)))
    sc.box(T(*(a["hand_r"] + np.array([0.0, 0.5, 0.0]))), (0.07, 1.2, 0.07), (230, 190, 90), layer=7)
    return sc


def s14(t, dur):
    u = t / dur
    sc = dcam((1.0, 3.8, -5.0), (-0.4, 2.8, 5.5), u, 0.08, fov=46)
    ns.class_front(sc, ns.pizza_board)
    sets.class_desks(sc, t, frozen=False, skip=(BACK_ROW,), faces=("smile", "joy"))
    a = character(sc, kid_spec(11), (-1.9, 0, 4.2), yaw=180, face="smug",
                  pose=dict(ar=(125, -10), er=25, al=(10, 6), head=(0, 0, -5)))
    sc.box(T(*(a["hand_r"] + np.array([0.0, 0.4, 0.0]))), (0.07, 1.2, 0.07), (230, 190, 90), layer=7)
    add_emote(sc, "stars", a["head_top"], t, size=0.5, dx=0.5, dy=0.1, start=word_t(14, 6, 1.6), hold=1.4)
    return sc


# ======================================================= 15-19: the narrator and the mayor
def s15(t, dur):
    u = t / dur
    sc = dfcam((0.0, 0, 0.0), ht(NARR), 18, u, frac=0.62, fov=40, push=0.08, elev=-0.5)
    sets.town(sc)
    character(sc, NARR, (0, 0, 0), face="grin", pose=dict(ar=(40, 14), er=20, head=(0, 0, 5)))
    return sc


def s16(t, dur):
    u = t / dur
    sc = dcam((1.4, 3.0, 11.0), (-0.4, 2.0, 0.0), u, 0.08, fov=42)
    sets.town(sc)
    w = math.sin(t * 9)
    a = character(sc, NARR, (-0.6, 0, 0), yaw=-10, face="shock", pose=dict(ar=(170 + 10 * w, 10), er=0, lean=-6))
    ls.sticker(sc, a["head_top"], "HEY!", t, start=0.4, hold=1.0, size=0.7, dx=0.8, dy=0.1, color=(255, 255, 255))
    for i, spec in enumerate((DAD_S, PATEL)):
        character(sc, spec, (3.4 + 2.0 * i + 0.5 * t, 0, -1.0), yaw=90, face="smile", pose=walk(t, 6, 18))
    return sc


def s17(t, dur):
    k, tt = sub3(t, 17, dur, (0, 2, 5))
    sc = dcam((0.0, 2.4, 7.0), (0.0, 2.0, 0.0), 0, 0.0, 42)
    if k == 0:
        sets.town(sc)
        dad(sc, (0, 0, 0), yaw=160, face="grin", pose=dict(al=(40, 12)), hose_on=True)
    elif k == 1:
        sets.classroom(sc)
        for i in range(3):
            c = character(sc, kid_spec(i + 14), (-2.8 + 2.8 * i, 0, 0), yaw=180 - 30 * (i - 1), face="laugh",
                          pose=dict(head=(20, 0, 0)))
    else:
        sets.town(sc)
        character(sc, MAYOR_S, (0, 0, 0), yaw=-20, face="smug", pose=dict(ar=(50, 8), er=110, head=(-30, 0, 0)))
    return sc


def mayor_pose(t, shake=0.0):
    return dict(head=(0, 0, 0), roll=shake * math.sin(t * 40))


def s18(t, dur):
    u = t / dur
    pos = (0, 0, 0)
    sc = head_cu(MAYOR_S, pos, 0, None, u, dist=5.2, up=0.0, fov=38, push=0.1)
    sets.town(sc)
    a = character(sc, MAYOR_S, pos, face="worried", pose=dict(roll=1.5 * math.sin(t * 30)))
    add_emote(sc, "sweat", a["head_top"], t, size=0.55, dx=0.8, dy=-0.2, start=0.6, hold=1.6)
    return sc


def s19(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.2, 9.0), (0.0, 2.6, 0.0), u, 0.06, fov=42)
    sets.town(sc)
    a = character(sc, MAYOR_S, (0, 0, 0.0), yaw=0, face="shock", pose=dict(al=(30, 14), ar=(30, 14)))
    for i, x in enumerate((-4.4, -3.2, -2.0, 2.0, 3.2, 4.4)):
        character(sc, kid_spec(i + 20), (x, 0, 3.4 + 0.3 * (i % 2)), yaw=180, face="smile")
    sparks(sc, a["head_top"] + np.array([0, -1.2, 0]), t, seed=9, n=6, r=1.2, color=(190, 236, 255))
    if t > 1.0:
        ls.glow_at(sc, a["head_top"] + np.array([0, -1.6, 0]), 2.0, (170, 220, 255), 60)
    return sc


# ======================================================= 20-29: the bridge
DAD_X = -3.1
ROWS = (0.6, 1.9)
XS = [-6.0 + 1.5 * i for i in range(9)]


def bridge_crowd(sc, t, mode="calm", wob=0.0, skip_dad=False, dad_pose=None):
    out = {}
    for r, z in enumerate(ROWS):
        for i, x in enumerate(XS):
            if r == 1 and abs(x - DAD_X) < 0.2:
                continue
            if r == 0 and abs(x) < 1.1:
                continue
            spec = crowd_spec(i + r * 9 + 30, adult=(i + r) % 3 != 1)
            dy = ns.sway(x, t, wob)
            ph = i * 1.7 + r
            if mode == "panic":
                w = math.sin(t * 14 + ph)
                pose = dict(al=(150 + 25 * w, 20), ar=(150 - 25 * w, 20), y=dy + 0.05 * abs(w), head=(0, 0, 8 * w))
                face = "shock"
            elif mode == "still":
                pose = dict(al=(160, 14), ar=(160, 14), y=dy)
                face = "shock"
            elif mode == "cheer":
                w = abs(math.sin(t * 9 + ph))
                pose = dict(al=(150 + 20 * w, 12), ar=(150 + 20 * w, 12), y=0.12 * w)
                face = "joy"
            else:
                pose = dict(al=(20, 6), ar=(40 * (1 if i % 2 else 0), 6), y=dy)
                face = "smile"
            out[(r, i)] = character(sc, spec, (x, ns.BR_Y, z), yaw=180, face=face, pose=pose, shadow=False)
    if not skip_dad:
        dp = dict(al=(20, 6), ar=(40, 6), y=ns.sway(DAD_X, t, wob))
        if mode == "panic":
            w = math.sin(t * 14)
            dp = dict(al=(150 + 25 * w, 20), ar=(150 - 25 * w, 20), y=ns.sway(DAD_X, t, wob))
        if mode == "cheer":
            dp = dict(al=(150, 12), ar=(150, 12), y=0.12 * abs(math.sin(t * 9)))
        dp.update(dad_pose or {})
        out["dad"] = dad(sc, (DAD_X, ns.BR_Y, ROWS[1]), yaw=180, face="shock" if mode in ("panic", "still") else "grin",
                         pose=dp, hose_on=True, shadow=False)
    return out


def mayor_up(sc, t, face="smile", pose=None, spot=None, yaw=0, wob=0.0):
    p = np.array(spot if spot is not None else ns.MAYOR_SPOT, float)
    p[1] += ns.sway(p[0], t, wob)
    return character(sc, MAYOR_S, p, yaw=yaw, face=face, pose=pose, shadow=False)


def kid_at(sc, t, spot, face="smile", pose=None, yaw=0, wob=0.0):
    p = np.array(spot, float)
    p[1] += ns.sway(p[0], t, wob)
    return character(sc, NARR, p, yaw=yaw, face=face, pose=pose, shadow=False)


def ccam(tgt, dist, az, el, u, fov=40, push=0.06):
    """Orbit camera: `dist` from the target at compass angle `az` (0 = on its +z side), `el` above it."""
    tgt = np.asarray(tgt, float)
    dv = np.array([math.sin(math.radians(az)), 0.0, math.cos(math.radians(az))])
    return dcam(tgt + dv * dist + np.array([0.0, el, 0.0]), tgt, u, push, fov)


PAIR = (0.0, 3.2, -3.4)       # between the mayor's spot and the kid's spot, chest height


def s20(t, dur):
    u = t / dur
    sc = dcam((-14.0 + 6.0 * u, 6.5, 15.5), (0.0, 1.6, 0.0), u, 0.0, fov=46)
    ns.bridge(sc, t)
    bridge_crowd(sc, t, "calm")
    mayor_up(sc, t)
    kid_at(sc, t, ns.KID_SPOT)
    confetti(sc, t, n=14)
    return sc


def s21(t, dur):
    u = t / dur
    sc = ccam(PAIR, 9.5, 158, 0.8, u, 38, 0.1)
    ns.bridge(sc, t)
    bridge_crowd(sc, t, "calm")
    mayor_up(sc, t, "smile", yaw=0)
    kid_at(sc, t, ns.KID_SPOT, "smile", yaw=0)
    return sc


def s22(t, dur):
    u = t / dur
    w = clamp(t / 0.5) * 0.6
    sc = dcam((0.0, 2.6, 15.5), (0.0, 2.2, 0.0), u, 0.05, fov=46)
    ns.bridge(sc, t, wobble=w, podium=False)
    bridge_crowd(sc, t, "calm", wob=w)
    ls.sticker(sc, (0.0, 4.4, 0.0), "CREEEAK", t, start=0.15, hold=1.2, size=0.9, dx=0.0, dy=0.6, color=(255, 214, 80))
    return sc


def s23(t, dur):
    u = t / dur
    sc = dcam((-3.0 + 5.0 * u, 2.4, 14.0), (0.5, 2.2, 0.0), u, 0.0, fov=46)
    ns.bridge(sc, t, wobble=1.0)
    bridge_crowd(sc, t, "panic", wob=1.0)
    mayor_up(sc, t, "shock", wob=1.0)
    kid_at(sc, t, ns.KID_SPOT, "shock", wob=1.0)
    return sc


def s24(t, dur):
    k, tt = sub3(t, 24, dur, (0, 3))
    if k == 0:
        sc = dcam((-0.4, 5.2, 13.5), (0.0, 2.6, 0.0), 0, 0, 46)
        ns.bridge(sc, t, wobble=1.0)
        bridge_crowd(sc, t, "panic", wob=1.0)
        mayor_up(sc, t, "shock", wob=1.0)
        kid_at(sc, t, ns.KID_SPOT, "shock", wob=1.0)
        ls.sticker(sc, (0.0, 5.0, 1.0), "AAAH!", t, start=0.2, hold=1.0, size=0.9, dx=-1.4, dy=0.3, color=(255, 255, 255))
    else:
        sc = ccam((0.0, 3.9, -2.8), 9.5, 22, 1.2, 0, 36, 0.0)
        ns.bridge(sc, t, wobble=1.0)
        a = mayor_up(sc, t, "shock", pose=dict(al=(30, 14), ar=(30, 14), roll=2 * math.sin(t * 40)), wob=1.0)
        sparks(sc, a["head_top"] + np.array([0, -1.2, 0]), t, seed=9, n=6, r=1.2, color=(190, 236, 255))
        add_emote(sc, "sweat", a["head_top"], t, size=0.5, dx=0.9, dy=-0.2, start=0.1, hold=1.4)
    return sc


def s25(t, dur):
    k, tt = sub3(t, 25, dur, (0, 4))
    if k == 0:
        sc = ccam((0.0, 3.2, -4.0), 8.5, 40, 2.0, 0, 38, 0.0)
        ns.bridge(sc, t, wobble=1.0)
        a = kid_at(sc, t, ns.KID_SPOT, "smirk", pose=dict(ar=(60, -10), er=70), wob=1.0)
        mayor_up(sc, t, "shock", wob=1.0)
        add_emote(sc, "bulb", a["head_top"], t, size=0.7, dx=0.5, dy=0.1, start=0.2, hold=1.4)
    else:
        sc = ccam((-2.4, 2.6, -1.0), 8.5, 5, 1.2, 0, 38, 0.0)
        ns.bridge(sc, t, wobble=1.0, podium=False)
        dad(sc, (-2.4, ns.BR_Y + ns.sway(-2.4, t, 1.0), -1.0), yaw=0, face="grin",
            pose=dict(al=(30, 10), ar=(30, 10)), hose_on=True, shadow=False)
    return sc


def s26(t, dur):
    u = t / dur
    sc = ccam((0.0, 3.2, -4.0), 8.5, 30, 2.4, u, 38, 0.08)
    ns.bridge(sc, t, wobble=1.0)
    w = math.sin(t * 12)
    a = kid_at(sc, t, ns.KID_SPOT, "angry", pose=dict(ar=(170 + 10 * w, 10), er=0, lean=-4), wob=1.0)
    mayor_up(sc, t, "shock", wob=1.0)
    ls.sticker(sc, a["head_top"], "HOSE!!", t, start=0.2, hold=1.0, size=0.8, dx=-0.9, dy=0.2, color=(255, 255, 255))
    add_emote(sc, "sweat", a["head_top"], t, size=0.45, dx=-0.5, dy=0.1, start=1.2, hold=1.2)
    return sc


def s27(t, dur):
    u = t / dur
    sc = ccam((0.0, 4.4, -3.2), 7.6, 32, 1.8, u, 34, 0.14)
    ns.bridge(sc, t, wobble=1.0)
    m = mayor_up(sc, t, "shock", wob=1.0)
    k = kid_at(sc, t, ns.KID_SPOT, "worried", pose=dict(head=(0, 0, 0), lean=-4), wob=1.0)
    ns.feather(sc, m["head_top"] + np.array([0.1, -0.35, 0.0]), t)
    sparks(sc, k["head"] + np.array([0.0, 0.3, 0.4]), t, seed=3, n=3, r=0.2, color=(255, 120, 190))
    return sc


def s28(t, dur):
    u = t / dur
    t0 = word_t(28, 2, 1.3)
    sc = ccam((0.0, 3.6, -3.4), 9.0, 35, 1.8, u, 38, 0.1)
    ns.bridge(sc, t, wobble=1.0)
    m = mayor_up(sc, t, "shock", wob=1.0)
    k = kid_at(sc, t, ns.KID_SPOT, sneeze_face(t, t0), pose=sneeze_pose(t, t0), wob=1.0)
    ns.feather(sc, m["head_top"] + np.array([0.1, -0.35, 0.0]), t)
    achoo(sc, k, t, t0, size=0.8)
    return sc


def s29(t, dur):
    u = t / dur
    sw = 0.45
    swp = t >= sw
    sc = ccam(PAIR, 12.0, 30, 2.4, u, 42, 0.05)
    ns.bridge(sc, t, wobble=1.0, podium=True)
    kp, mp = ns.KID_SPOT, ns.MAYOR_SPOT
    mayor_up(sc, t, "shock", spot=kp if swp else mp, wob=1.0)
    kid_at(sc, t, mp if swp else kp, "shock", wob=1.0)
    ns.swap_fx(sc, mp, kp, t, sw, y=2.0)
    return sc


def swapped_stage(sc, t, wob=1.0, kid_face="shock", mayor_face="shock", kid_pose=None, mayor_pose_=None):
    """After the swap: the kid stands where the mayor stood (behind the podium), the mayor in the kid's spot."""
    k = kid_at(sc, t, ns.MAYOR_SPOT, kid_face, pose=kid_pose, wob=wob)
    m = mayor_up(sc, t, mayor_face, spot=ns.KID_SPOT, pose=mayor_pose_, wob=wob)
    return k, m


def s30(t, dur):
    u = t / dur
    sc = ccam((0.0, 3.0, -3.2), 9.0, 22, 2.2, u, 38, 0.1)
    ns.bridge(sc, t, wobble=1.0)
    k, m = swapped_stage(sc, t, kid_face="shock", mayor_face="shock",
                         kid_pose=dict(ar=(50, 10), er=40, al=(20, 6)))
    add_emote(sc, "!", k["head_top"], t, size=0.55, dx=0.6, dy=0.1, start=0.3, hold=1.2)
    return sc


def s31(t, dur):
    """Seen from the podium: the whole town turns and stares."""
    u = t / dur
    sc = dcam((0.0, 3.8, -5.0), (0.0, 2.8, 3.0), u, 0.06, fov=56)
    ns.bridge(sc, t, wobble=0.8 * (1 - 0.5 * u))
    bridge_crowd(sc, t, "still" if t > 0.3 else "panic", wob=0.8 * (1 - 0.5 * u))
    return sc


def s32(t, dur):
    u = t / dur
    sc = ccam((0.0, 3.0, -2.8), 8.0, 18, 2.0, u, 36, 0.08)
    ns.bridge(sc, t, wobble=0.5)
    k, m = swapped_stage(sc, t, wob=0.5, kid_face="smug", kid_pose=dict(ar=(70, 8), er=0, al=(30, 14), el=60,
                                                                       head=(0, 0, -4)))
    sparks(sc, k["head_top"] + np.array([0.0, 0.2, 0.0]), t, seed=4, n=4, r=0.5)
    ls.sticker(sc, k["head_top"], "HERE!", t, start=word_t(32, 7, 1.6), hold=1.2, size=0.8, dx=-0.9, dy=0.3,
               color=(255, 230, 80))
    return sc


def s33(t, dur):
    u = t / dur
    sc = ccam((0.0, 3.4, -2.8), 9.5, 20, 2.4, u, 40, 0.1)
    ns.bridge(sc, t, wobble=0.6)
    w = math.sin(t * 10)
    k, m = swapped_stage(sc, t, wob=0.6, kid_face="grin", kid_pose=dict(ar=(165 + 8 * w, 10), er=0, al=(30, 6)))
    ls.sticker(sc, k["head_top"], "FREEZE!", t, start=0.2, hold=1.4, size=0.9, dx=-1.3, dy=0.1, color=(130, 230, 255))
    return sc


def dad_path(t, num=34):
    """Dad runs from his spot along the front rail, east to the oak."""
    return DAD_X + (8.8 - DAD_X) * clamp(t / 2.0)


def s34(t, dur):
    u = t / dur
    x = dad_path(t)
    sc = dcam((x - 3.2, 3.6, 12.6), (x + 1.2, 2.0, 2.4), u, 0.0, fov=44)
    ns.bridge(sc, t, wobble=0.5 * (1 - u))
    d = dad(sc, (x, ns.BR_Y if x < 8 else 0.4, 2.6), yaw=90, face="effort", pose=dict(walk(t, 16, 40), lean=22),
            hose_on=True, shadow=False)
    speed_lines(sc, t, cx=0.5, cy=0.4, n=12, inner=0.4, alpha=90)
    return sc


def s35(t, dur):
    k, tt = sub3(t, 35, dur, (0, 2, 4))
    ks = (0.34, 0.67, 1.0)[k]
    sc = dcam((6.0, 3.8, 11.2), (9.3, 2.0, 1.2), 0, 0, 42)
    ns.bridge(sc, t, wobble=0.3 * (1 - ks), hose_k=ks)
    dad(sc, (8.8, 0.4, 2.2), yaw=60, face="effort" if k < 2 else "joy",
        pose=dict(lean=20, ar=(80, -10), er=60, al=(80, -10), el=60, y=0.05 * math.sin(tt * 18)), shadow=False)
    ls.sticker(sc, (9.4, 4.0, 1.0), ("KNOT!", "KNOT!", "DAD KNOT!")[k], tt, start=0.05, hold=1.0, size=0.8, dx=0.0,
               dy=0.2, color=(255, 230, 80))
    return sc


def s36(t, dur):
    u = t / dur
    sc = dcam((-3.0 + 3.0 * u, 3.0, 14.5), (1.0, 2.2, 0.0), u, 0.02, fov=46)
    ns.bridge(sc, t, wobble=0.0, hose_k=1.0)
    bridge_crowd(sc, t, "still", wob=0.0)
    swapped_stage(sc, t, wob=0.0, kid_face="smile", mayor_face="shock")
    sparks(sc, (0.0, 2.4, -2.0), t, seed=3, n=3, r=0.6, color=(255, 255, 255))
    return sc


def s37(t, dur):
    u = t / dur
    sc = dcam((-11.0 + 3.0 * u, 7.5, 13.0), (0.0, 2.2, 0.0), u, 0.0, fov=46)
    ns.bridge(sc, t, hose_k=1.0)
    bridge_crowd(sc, t, "cheer")
    swapped_stage(sc, t, wob=0.0, kid_face="joy", mayor_face="joy", kid_pose=dict(al=(30, 14), ar=(30, 14)))
    confetti(sc, t, n=20)
    return sc


def s38(t, dur):
    u = t / dur
    sc = ccam((0.0, 3.0, -2.8), 8.5, 20, 2.2, u, 38, 0.08)
    ns.bridge(sc, t, hose_k=1.0)
    k, m = swapped_stage(sc, t, wob=0.0, kid_face="smile", mayor_face="joy", kid_pose=dict(al=(30, 14), ar=(30, 14)))
    confetti(sc, t, n=60)
    sparks(sc, k["head"] + np.array([0.0, 0.1, 0.5]), t, seed=3, n=3, r=0.2, color=(255, 120, 190))
    return sc


def s39(t, dur):
    u = t / dur
    t0 = word_t(39, 0, 0.35)
    sw = t0 + 0.4
    swp = t >= sw
    sc = ccam(PAIR, 11.0, 35, 2.4, u, 42, 0.04)
    ns.bridge(sc, t, hose_k=1.0)
    ks, ms = ns.MAYOR_SPOT, ns.KID_SPOT
    k = kid_at(sc, t, ms if swp else ks, sneeze_face(t, t0) if not swp else "shock",
               pose=sneeze_pose(t, t0) if not swp else None)
    mayor_up(sc, t, "shock" if swp else "smile", spot=ks if swp else ms)
    achoo(sc, k, t, t0, size=0.8)
    ns.swap_fx(sc, ks, ms, t, sw, y=2.0)
    confetti(sc, t, n=50)
    return sc


def s40(t, dur):
    u = t / dur
    pose = dict(al=(40, 14), ar=(40, 14), roll=2.0 * math.sin(t * 30) * clamp(1 - t / 1.6))
    sc = ccam((0.0, 4.0, -2.8), 8.5, 25, 1.4, u, 36, 0.1)
    ns.bridge(sc, t, hose_k=1.0)
    m = mayor_up(sc, t, "worried" if t < 1.6 else "smile", pose=pose)
    add_emote(sc, "sweat", m["head_top"], t, size=0.5, dx=0.8, dy=-0.2, start=0.2, hold=1.2)
    return sc


def s41(t, dur):
    u = t / dur
    sc = dcam((0.0, 6.2, 12.5), (0.0, 2.8, -2.0), u, 0.08, fov=44)
    ns.bridge(sc, t, hose_k=1.0)
    bridge_crowd(sc, t, "calm")
    m = mayor_up(sc, t, "smile", pose=dict(ar=(60, -8), er=30, al=(20, 6)))
    kid_at(sc, t, (1.8, ns.BR_Y, -2.8), "smile")
    sparks(sc, m["head_top"], t, seed=2, n=3, r=0.6)
    return sc


def s42(t, dur):
    u = t / dur
    sc = dcam((0.0, 5.8, 12.0), (0.0, 2.8, -1.0), u, 0.1, fov=44)
    ns.bridge(sc, t, hose_k=1.0)
    bridge_crowd(sc, t, "cheer")
    mayor_up(sc, t, "joy", pose=dict(al=(150, 12), ar=(150, 12)))
    kid_at(sc, t, (1.8, ns.BR_Y, -2.8), "joy", pose=dict(al=(150, 12), ar=(150, 12)))
    confetti(sc, t, n=50)
    return sc


RIB_SPOT = np.array([ns.BR_X - 2.2, ns.BR_Y, 1.0])


def scissors_at(sc, k, open_k):
    ns.scissors(sc, T(*(k["hand_r"] + np.array([0.6, 0.15, 0.0]))) @ RZ(-90), open_k=open_k, s=0.9)


def s43(t, dur):
    u = t / dur
    sc = ccam((RIB_SPOT[0] + 0.4, 2.6, 1.0), 9.5, 12, 0.8, u, 38, 0.1)
    ns.bridge(sc, t, hose_k=1.0, podium=False)
    k = character(sc, NARR, RIB_SPOT, yaw=90, face="grin", pose=dict(ar=(85, 0), er=10, al=(40, 6)), shadow=False)
    scissors_at(sc, k, 0.6)
    sparks(sc, RIB_SPOT + np.array([1.0, 2.0, 0.0]), t, seed=3, n=4, r=0.4)
    return sc


def s44(t, dur):
    cut = t >= 0.12
    sc = ccam((RIB_SPOT[0] + 0.6, 2.6, 0.8), 8.5, 12, 0.8, 0, 38, 0.0)
    ns.bridge(sc, t, hose_k=1.0, podium=False, ribbon=1.0 if cut else 0.0)
    k = character(sc, NARR, RIB_SPOT, yaw=90, face="joy", pose=dict(ar=(85, 0), er=10, al=(40, 6)), shadow=False)
    scissors_at(sc, k, 0.0 if cut else 0.9)
    ls.sticker(sc, RIB_SPOT + np.array([0.8, 3.8, 0.0]), "SNIP!", t, start=0.12, hold=1.2, size=1.0, dx=0.0, dy=0.3,
               color=(255, 230, 80))
    if cut and t < 0.12 + 2 / 30:
        sc.flash = 0.6
    confetti(sc, t, n=40)
    return sc


def s45(t, dur):
    u = t / dur
    sc = dcam((lerp(-1.0, 6.0, u), 3.4, 13.5), (lerp(0.0, 8.0, u), 2.0, 1.5), u, 0.0, fov=44)
    ns.bridge(sc, t, hose_k=1.0, ribbon=1.0)
    bridge_crowd(sc, t, "cheer")
    mayor_up(sc, t, "joy", pose=dict(al=(150, 12), ar=(150, 12)))
    kid_at(sc, t, (1.8, ns.BR_Y, -2.8), "joy", pose=dict(al=(150, 12), ar=(150, 12)))
    return sc


def s46(t, dur):
    u = t / dur
    sc = ccam((9.0, 2.4, 2.0), 8.5, 28, 0.6, u, 38, 0.04)
    ns.bridge(sc, t, hose_k=1.0, ribbon=1.0, podium=False)
    d = dad(sc, (9.5, 0.0, 2.2), yaw=-30, face="angry" if t > 0.6 else "smirk",
            pose=dict(al=(100, -10), ar=(100, 10), er=60, el=60), shadow=False)
    if t > 0.6:
        add_emote(sc, "anger", d["head_top"], t, size=0.55, dx=0.5, dy=0.05, start=0.6, hold=1.6)
    return sc


_FNS = [globals()[f"s{i:02d}"] for i in range(1, len(LINES) + 1)]
SHOTS = [(i + 1, 1.6, txt, fn) for i, (txt, fn) in enumerate(zip(LINES, _FNS))]
SHOTS, WORD_TIMES = load_timing(SHOTS, TIMING_FILE)
WT.update(WORD_TIMES)
