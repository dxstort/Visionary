"""Every Tree Glows When You Tell a Secret: shot list. Each shot: (number, seconds, caption text, fn(t, dur) -> Scene)."""
import os

TIMING_FILE = "glowtree_timing.json"
SPOKEN = {"Ms": "miz", "Mrs": "missus", "Gomez's": "gomez's", "BEFORE": "before"}
PHONES = {"rudy": "R UW D IY", "patel": "P AH T EH L", "gomez": "G OW M EH Z", "gomez's": "G OW M EH Z IH Z",
          "miz": "M IH Z", "necessary": "N EH S AH S EH R IY", "pajamas": "P AH JH AA M AH Z",
          "bulldozer": "B UH L D OW Z ER", "sunhat": "S AH N HH AE T"}

LINES = [
    "In this town, when you whisper a TRUE secret to a tree,",
    "the tree GLOWS.",
    "Dad told the oak he eats the frosting BEFORE the party.",
    "Neon orange. By lunch, the whole street knew.",
    "Ms Patel told the maple she can't spell necessary.",
    "Pink. Flickering. Her class spelled it for her.",
    "Mrs Gomez told the pine she talks to her tomatoes.",
    "Green. The tomatoes stayed quiet.",
    "I'm Rudy. Last Friday, I found out something BIG.",
    "There's a hidden garden behind our school.",
    "Mrs Gomez planted it as a girl. Nobody's found the gate in forty years.",
    "Saturday at sunrise, a bulldozer makes it a parking lot.",
    "Mrs Gomez's sunhat drooped. Only the trees know the way, she said.",
    "But they only show it for a TRUE secret.",
    "So I crept out before dawn. Dinosaur pajamas under my coat.",
    "Tim was already there. Slick hair. Fast sneakers. Winning grin.",
    "He whispered to the pine: I'm the smartest kid in school!",
    "Not one glow. Bragging isn't a secret.",
    "The sky was turning pink. Ten minutes to sunrise.",
    "I put my hand on the oak and whispered my truest secret.",
    "I still sleep with the hall light ON.",
    "The oak blazed gold. A glowing trail shot down the street.",
    "Tim heard everything. I waited for the laugh. It never came.",
    "We ran past the gym, following the glow.",
    "The maple pulsed, and ivy slid off a rusty old gate.",
    "Tim tripped on a root. Sneakers are fast. Roots are faster.",
    "I could have kept running. Garden. Sunrise. Winning.",
    "I pulled him up. Why'd you stop? he asked. Who else would I race?",
    "The gate was locked. Even the maple dimmed.",
    "It wanted a secret nobody had ever told.",
    "Tim stared at the gate. Then he whispered to the pine.",
    "My grandma helped plant this garden. I just wanted to see it once.",
    "The pine exploded GOLD.",
    "The gate swung open. The sun came up.",
    "Every flower lit up at once. Even the weeds. Weeds have feelings too.",
    "Tim's pine lit up the sky. The whole town came running.",
    "Dad brought cake. Ms Patel brought chalk. Nobody asked why.",
    "Mrs Gomez cried. Then she hugged Tim. His grandma was her best friend.",
    "The bulldozer driver took one look and turned off the engine.",
    "Nobody paves a garden that glows.",
    "Now we eat lunch there every day.",
    "Dad still eats the frosting first. The oak knows.",
]
import math  # noqa: E402

import numpy as np  # noqa: E402

import glowtree_sets as gs  # noqa: E402
import laughs_sets as ls  # noqa: E402
import porch_sets as ps  # noqa: E402
import sets  # noqa: E402
import shoes_sets as ss  # noqa: E402
from cast import DAD, _spec, character, crowd_spec, sit  # noqa: E402
from engine import RX, RY, RZ, T, add_emote, clamp, lerp, speed_lines, xf  # noqa: E402
from laughs import DAY, dcam, head_cu, ht  # noqa: E402
from shots import confetti, sparks, walk  # noqa: E402
from story import load_timing  # noqa: E402

# ------------------------------------------------------------------ cast
RUDY_G = _spec(name="Rudy", style="messy", s=0.98, skin=(214, 156, 118), shirt=(255, 168, 30), pants=(40, 80, 130),
               shoes=(250, 250, 250), hair=(70, 44, 28), sleeve=0.5)
RUDY_PJ = dict(RUDY_G, shirt=(150, 98, 56), hoodie=True, accent=(250, 220, 120), pants=(90, 200, 120), sleeve=0.9)
TIM = _spec(name="Tim", style="side", s=1.04, skin=(236, 190, 150), shirt=(52, 104, 230), pants=(34, 40, 70),
            shoes=(255, 70, 60), hair=(28, 24, 32), sleeve=0.5)
DAD_G = dict(DAD, name="Dad", style="short", flannel=True, shirt=(206, 74, 62), hair=(110, 74, 44), floral=False)
PATEL = _spec(name="Ms Patel", style="bun", s=1.22, skin=(214, 156, 118), shirt=(244, 120, 60), inner=(255, 232, 130),
              cardigan=True, pants=(70, 70, 120), shoes=(90, 70, 70), hair=(30, 24, 28), glasses=True,
              accent=(240, 120, 160), sleeve=0.86)
GOMEZ = _spec(name="Mrs Gomez", style="bob", s=1.2, skin=(190, 132, 96), shirt=(120, 190, 120), pants=(110, 88, 60),
              shoes=(110, 80, 56), hair=(150, 120, 100), sleeve=0.86)
DRIVER = _spec(name="Driver", style="cap", s=1.28, skin=(214, 156, 118), shirt=(250, 150, 40), hat=(250, 210, 40),
               pants=(60, 70, 96), shoes=(60, 46, 40), sleeve=0.5)

DUSK = dict(sky=ps.DUSK_SKY, night=0.62)
NIGHT = dict(sky=ps.NIGHT_SKY, night=0.85)
PREDAWN = dict(sky=((40, 52, 120), (255, 170, 150)), night=0.55)
SUNRISE = dict(sky=((110, 150, 235), (255, 206, 150)), night=0.18)
WT = {}

GATE_X, WALL_Z0 = gs.GATE_X, gs.WALL_Z
WHISPER = dict(ar=(128, -40), er=112)
OAK, MAPLE, PINE = (-6.0, -3.6), (0.0, -3.6), (6.5, -3.6)


def word_t(num, i, default=0.0):
    w = WT.get(num, [])
    return w[i][0] if i < len(w) else default


def subs(t, num, dur, idx):
    """Which beat of a shot we are in: beat k starts at the onset of word idx[k]. -> (k, time since beat start)."""
    starts = [0.0] + [word_t(num, i, dur * (k + 1) / len(idx)) for k, i in enumerate(idx[1:])]
    k = 0
    for i, s0 in enumerate(starts):
        if t >= s0 - 0.04:
            k = i
    return k, t - starts[k]


def cam(pos, tgt, u, push=0.08, fov=42, mood=DUSK, bloom=1.0, **kw):
    return dcam(pos, tgt, u, push, fov, mood=mood, bloom=bloom, **kw)


def town(sc, oak=0.0, maple=0.0, pine=0.0, t=0.0, oak_col=None):
    sets.town(sc)
    gs.glow_tree(sc, *OAK, "oak", oak, h=4.6, t=t, seed=1, color=oak_col)
    gs.glow_tree(sc, *MAPLE, "maple", maple, h=4.6, t=t, seed=2)
    gs.glow_tree(sc, *PINE, "pine", pine, h=4.8, t=t, seed=3)


def whisper_to(sc, spec, pos, tree_x, face="grin", t=0.0, extra=None, **kw):
    """A character cupping a hand to their mouth, leaning toward a tree on their left (tree_x < pos x) or right."""
    d = -1 if tree_x < pos[0] else 1
    p = dict(lean=14, head=(0, 0, 4 * d), **WHISPER)
    p.update(extra or {})
    return character(sc, spec, pos, yaw=90 * d - 25 * d, face=face, pose=p, **kw)


def breathe(t, k=0.02):
    return k * math.sin(t * 2.4)


# ------------------------------------------------------------ 1-8: the rule and the town
def s01(t, dur):
    u = t / dur
    k = 0.3 + 0.55 * clamp((t - 1.2) / 1.4)
    sc = cam((-0.8, 2.0, 8.6), (-0.4, 2.3, -1.0), u, 0.08, 42)
    town(sc, maple=k, t=t)
    whisper_to(sc, crowd_spec(4), (-1.9, 0, -1.6), 0.0, face="smile", t=t)
    return sc


def s02(t, dur):
    u = t / dur
    sc = cam((0.3, 0.8, 8.2), (0.0, 3.4, -3.6), u, 0.1, 46)
    town(sc, maple=1.0, oak=0.45, pine=0.45, t=t)
    sc.flash = max(0.0, 0.5 * (1 - t / 0.25))
    sparks(sc, (0.0, 3.5, -2.0), t, seed=2, n=8, r=2.2, color=gs.PINK)
    character(sc, crowd_spec(4), (-1.9, 0, -1.2), yaw=60, face="shock", pose=dict(ar=(150, -20), al=(40, 10)))
    return sc


def s03(t, dur):
    u = t / dur
    k = 0.4 * clamp((t - dur * 0.6) / (dur * 0.4))
    sc = cam((-4.0, 2.8, 11.0), (-5.4, 2.7, -2.2), u, 0.06, 44)
    town(sc, oak=k, t=t)
    a = whisper_to(sc, DAD_G, (-4.4, 0, -1.6), OAK[0], face="grin", t=t)
    ss.flour(sc, a, t)
    return sc


def s04(t, dur):
    u = t / dur
    k = clamp(t / 0.5)
    sc = cam((-1.0, 2.4, 11.0), (-3.4, 2.4, -2.0), u, 0.06, 46)
    town(sc, oak=k, maple=0.0, t=t)
    a = character(sc, DAD_G, (-4.3, 0, -1.2), yaw=20, face="grin", pose=dict(al=(30, 12), ar=(30, 12)))
    ss.flour(sc, a, t)
    for i, (x, z) in enumerate(((-1.0, 0.4), (1.6, 1.0), (3.4, -0.4))):
        b = character(sc, crowd_spec(i + 9, adult=i == 1), (x, 0, z), yaw=-50 - 10 * i, face=("laugh", "shock", "grin")[i],
                      pose=dict(ar=(100, -20 - 8 * math.sin(t * 8 + i)), al=(20, 6)))
        add_emote(sc, "!", b["head_top"], t, size=0.4, dy=0.2, start=0.5 + 0.3 * i)
    return sc


def s05(t, dur):
    u = t / dur
    k = 0.45 * clamp((t - dur * 0.55) / (dur * 0.45))
    sc = cam((-3.2, 2.8, 14.0), (-5.4, 2.6, 3.6), u, 0.05, 44)
    sets.school_building(sc)
    gs.glow_tree(sc, -6.5, 3.3, "maple", k, h=4.6, t=t, seed=2)
    a = whisper_to(sc, PATEL, (-4.6, 0, 5.2), -6.5, face="worried", t=t)
    gs.chalk(sc, a, t)
    return sc


def s06(t, dur):
    u = t / dur
    k = 0.75 + 0.25 * math.sin(t * 13)
    sc = cam((-1.0, 2.2, 13.0), (-4.2, 2.2, 5.0), u, 0.06, 44)
    sets.school_building(sc)
    gs.glow_tree(sc, -6.5, 3.3, "maple", k, h=4.6, t=t, seed=2)
    a = character(sc, PATEL, (-4.6, 0, 5.2), yaw=-20, face="worried" if t < dur * 0.5 else "laugh",
                  pose=dict(ar=(60, -20), al=(60, -20), el=70, er=70))
    gs.chalk(sc, a, t)
    for i in range(4):
        b = character(sc, crowd_spec(i + 14), (-2.2 + i * 1.1, 0, 7.4 - 0.3 * (i % 2)), yaw=-20, face="joy",
                      pose=dict(ar=(165, -10 - 10 * math.sin(t * 7 + i)), al=(20, 6)))
        if i == 1:
            ls.sticker(sc, b["head"], "N-E-C-E-S-S-A-R-Y", t, start=0.5, hold=2.6, size=0.4, dy=0.9, dx=0.1,
                       color=(255, 255, 255))
    return sc


def s07(t, dur):
    u = t / dur
    k = 0.4 * clamp((t - dur * 0.55) / (dur * 0.45))
    sc = cam((3.8, 2.0, 7.6), (5.4, 2.0, -2.0), u, 0.08, 42)
    town(sc, pine=k, t=t)
    gs.tomatoes(sc, 0.6, -1.8, 4)
    a = whisper_to(sc, GOMEZ, (4.7, 0, -1.4), PINE[0], face="grin", t=t)
    gs.sunhat(sc, a, GOMEZ)
    gs.garden_gloves(sc, a)
    return sc


def s08(t, dur):
    u = t / dur
    sc = cam((2.4, 1.0, 6.2), (3.0, 1.2, -1.8), u, 0.08, 44)
    town(sc, pine=1.0, t=t)
    gs.tomatoes(sc, 0.0, -1.8, 5)
    a = character(sc, GOMEZ, (4.8, 0, -1.4), yaw=-30, face="worried", pose=dict(al=(40, 6), ar=(110, -30), er=100))
    gs.sunhat(sc, a, GOMEZ)
    gs.garden_gloves(sc, a)
    add_emote(sc, "sweat", a["head_top"], t, size=0.45, dx=0.3, dy=0.05, start=0.4)
    ls.sticker(sc, (1.8, 1.8, -1.8), "...", t, start=0.8, hold=1.6, size=0.55, dy=0.3, color=(255, 255, 255))
    return sc


# ---------------------------------------------------------------- 9-14: Rudy and the garden
def s09(t, dur):
    u = t / dur
    pose = dict(head=(0, 0, 3 * math.sin(t * 1.6)), al=(20, 8), ar=(20, 8))
    sc = head_cu(RUDY_G, (0, 0, 0.6), 0, pose, u, dist=3.2, up=0.15, fov=36, mood=DUSK, bloom=1.0)
    town(sc, 0.7, 0.7, 0.7, t=t)
    character(sc, RUDY_G, (0, 0, 0.6), face="smile" if t < dur * 0.6 else "shock", pose=pose)
    return sc


def s10(t, dur):
    u = t / dur
    sc = cam((-6.0 + 11.0 * u, 2.4, 3.8), (-4.0 + 11.0 * u, 2.6, -6.0), u, 0.0, 44)
    gs.lot(sc, t)
    gs.ivy_wall(sc, 0.0, t=t)
    gs.peeking_flowers(sc, 0.25 + 0.1 * math.sin(t * 3), t, tree_k=0.1)
    character(sc, RUDY_G, (-2.0 + 11.0 * u * 0.9, 0, -2.4), yaw=180 if False else 90, face="smile",
              pose=walk(t, 7, 18))
    return sc


def s11(t, dur):
    k, tt = subs(t, 11, dur, (0, 7))
    u = t / dur
    if k == 0:
        sc = cam((GATE_X - 1.5, 2.0, 3.6), (GATE_X - 1.0, 1.8, -6.0), u, 0.08, 42)
        gs.lot(sc, t)
        gs.ivy_wall(sc, 0.0, t=t)
        gs.peeking_flowers(sc, 0.2, t, tree_k=0.1)
        a = character(sc, GOMEZ, (GATE_X - 2.6, 0, -3.2), yaw=-12, face="smile",
                      pose=dict(ar=(60, -10), er=40, al=(20, 8)), shadow=True)
        gs.sunhat(sc, a, GOMEZ)
        gs.garden_gloves(sc, a)
        character(sc, RUDY_G, (GATE_X - 1.0, 0, -2.4), yaw=-20, face="smile", pose=dict(head=(0, 4, 0)))
    else:
        sc = cam((GATE_X, 2.6, 2.4), (GATE_X, 2.4, -6.0), tt / max(0.5, dur - 3.0), 0.08, 46)
        gs.lot(sc, t)
        gs.ivy_wall(sc, 0.0, t=t)
        ls.sticker(sc, (GATE_X, 3.4, -4.2), "40 YEARS", tt, start=0.15, hold=3.0, size=0.6, dy=0.0, color=(255, 230, 80))
    return sc


def s12(t, dur):
    u = t / dur
    sc = cam((-2.0 + 4.0 * u, 2.6, 8.4), (0.0, 1.6, -4.0), u, 0.05, 46, mood=PREDAWN)
    gs.lot(sc, t)
    gs.ivy_wall(sc, 0.0, t=t)
    gs.peeking_flowers(sc, 0.2, t, tree_k=0.1)
    gs.bulldozer(sc, T(-2.4, 0, -2.6) @ RY(-10), t)
    gs.lot_sign(sc, T(2.8, 0, 0.2) @ RY(-15))
    gs.timer(sc, "SAT · SUNRISE")
    return sc


def s13(t, dur):
    u = t / dur
    d = clamp(t / 1.2)
    pose = dict(al=(25, 6), ar=(25, 6), head=(0, 10 * d, 0))
    sc = head_cu(GOMEZ, (0, 0, 0.0), 0, pose, u, dist=3.4, up=0.2, fov=36, mood=DUSK, bloom=1.0)
    gs.lot(sc, t)
    gs.glow_tree(sc, 3.4, -4.0, "pine", 0.25, h=5.5, t=t, seed=3)
    a = character(sc, GOMEZ, (0, 0, 0.0), face="sad" if t > 0.7 else "worried", pose=pose,
                  face_extra=gs.dirt_cheeks)
    gs.sunhat(sc, a, GOMEZ, droop=d)
    gs.garden_gloves(sc, a)
    return sc


def s14(t, dur):
    u = t / dur
    sc = cam((0.6, 2.2, 9.6), (0.0, 3.0, -3.6), u, 0.08, 46)
    town(sc, 0.0, 0.0, 0.0, t=t)
    r = character(sc, RUDY_G, (0.4, 0, 1.4), yaw=180, face="worried", pose=dict(head=(0, -14, 0)))
    add_emote(sc, "?", r["head_top"], t, size=0.55, dx=0.5, dy=0.2, start=0.5)
    return sc


# ------------------------------------------------------------ 15-23: before dawn
def s15(t, dur):
    u = t / dur
    x = 2.4 - 3.2 * u
    sc = cam((x + 0.5, 2.0, 9.6), (x - 0.2, 1.5, 0.6), u, 0.05, 44, mood=NIGHT)
    town(sc, 0.1, 0.1, 0.1, t=t)
    sw = math.sin(t * 5)
    character(sc, RUDY_PJ, (x, 0, 0.6), yaw=-90, face="worried", pose=dict(ll=26 * sw, lr=-26 * sw, lean=8, al=(10, 6),
              ar=(90, -10), er=60))
    add_emote(sc, "sweat", (x, 1.8, 0.6), t, size=0.4, dy=0.1, start=1.0)
    return sc


def s16(t, dur):
    k, tt = subs(t, 16, dur, (0, 4, 6, 8))
    u = tt / max(0.5, dur / 4)
    if k == 0:
        sc = cam((1.8, 1.6, 6.6), (3.0, 1.2, -1.0), u, 0.1, 42, mood=NIGHT)
        town(sc, 0.0, 0.0, 0.0, t=t)
        character(sc, TIM, (4.2, 0, -0.4), yaw=-35, face="smirk", pose=dict(al=(60, -20), ar=(60, -20), el=110, er=110))
    elif k == 1:
        pose = dict(head=(0, 0, 3))
        sc = head_cu(TIM, (4.2, 0, 0.0), 0, pose, u, dist=2.4, fov=34, up=0.3, mood=NIGHT, bloom=1.0)
        town(sc, 0.0, 0.0, 0.0, t=t)
        character(sc, TIM, (4.2, 0, 0.0), face="smirk", pose=pose)
    elif k == 2:
        sc = cam((4.8, 0.45, 2.6), (4.2, 0.25, 0.0), u, 0.1, 42, mood=NIGHT)
        town(sc, 0.0, 0.0, 0.0, t=t)
        a = character(sc, TIM, (4.2, 0, 0.0), face="smirk", pose=dict(ll=6 * math.sin(t * 9), lr=-6 * math.sin(t * 9)))
        ls.glow_at(sc, a["foot_l"] + np.array([0, 0.1, 0.1]), 0.35, (255, 120, 90), 60)
    else:
        pose = dict(head=(8, 0, -4))
        sc = head_cu(TIM, (4.2, 0, 0.0), 0, pose, u, dist=2.0, fov=32, up=0.3, mood=NIGHT, bloom=1.0)
        town(sc, 0.0, 0.0, 0.0, t=t)
        character(sc, TIM, (4.2, 0, 0.0), face="grin", pose=pose)
        sparks(sc, (4.7, 1.9, 0.2), tt, seed=4, n=3, r=0.3, color=(255, 255, 255))
    return sc


def s17(t, dur):
    u = t / dur
    sc = cam((4.0, 2.0, 5.6), (6.0, 2.0, -2.2), u, 0.08, 40, mood=NIGHT)
    town(sc, 0.0, 0.0, 0.0, t=t)
    whisper_to(sc, TIM, (4.9, 0, -1.5), PINE[0], face="smirk", t=t)
    return sc


def s18(t, dur):
    u = t / dur
    sc = cam((4.6, 1.7, 5.4), (5.8, 2.2, -2.0), u, 0.12, 42, mood=NIGHT)
    town(sc, 0.0, 0.0, 0.0, t=t)
    a = character(sc, TIM, (4.9, 0, -1.2), yaw=-20, face="stung" if t > 0.8 else "smirk",
                  pose=dict(al=(30, 10), ar=(30, 10), head=(0, -6, 0)))
    add_emote(sc, "?", a["head_top"], t, size=0.55, dx=0.5, dy=0.2, start=1.2)
    ls.sticker(sc, (6.5, 4.0, -3.6), "...", t, start=0.9, hold=2.0, size=0.7, dy=0.0, color=(255, 255, 255))
    return sc


def s19(t, dur):
    u = t / dur
    left = max(0, int(600 - 8 * t))
    sc = cam((0.0, 2.4, 11.0), (0.0, 3.0, -6.0), u, 0.04, 46, mood=PREDAWN)
    town(sc, 0.0, 0.0, 0.0, t=t)
    character(sc, RUDY_PJ, (-1.0, 0, 1.6), yaw=180, face="worried", pose=dict(head=(0, -8, 0)))
    character(sc, TIM, (0.6, 0, 1.6), yaw=180, face="grit")
    gs.timer(sc, f"SUNRISE {left // 60:02d}:{left % 60:02d}")
    return sc


def s20(t, dur):
    u = t / dur
    k = 0.3 * clamp((t - 1.0) / 2.0)
    pos = (-5.2, 0, -1.2)
    sc = cam((-3.0, 2.2, 7.0), (-5.4, 2.2, -2.0), u, 0.06, 44, mood=NIGHT)
    town(sc, oak=k, t=t, oak_col=gs.GOLD)
    a = character(sc, RUDY_PJ, pos, yaw=-90, face="sleep" if False else "neutral",
                  pose=dict(lean=8, ar=(95, -20), er=10, al=(15, 8)))
    ls.glow_at(sc, a["hand_r"] + np.array([-0.2, 0.0, 0.0]), 0.6, gs.GOLD, int(120 * clamp(t / 1.5)))
    return sc


def s21(t, dur):
    u = t / dur
    k = 0.65 * clamp(t / 1.5)
    pose = dict(head=(0, -6, 0), al=(15, 8), ar=(15, 8))
    sc = head_cu(RUDY_PJ, (-4.0, 0, -0.4), 0, pose, u, dist=2.6, side=0.2, fov=34, mood=NIGHT, bloom=1.0)
    town(sc, oak=k, t=t, oak_col=gs.GOLD)
    a = character(sc, RUDY_PJ, (-4.0, 0, -0.4), face="worried" if t < 1.5 else "smile", pose=pose)
    add_emote(sc, "bulb", a["head_top"], t, size=0.55, dx=0.5, dy=0.15, start=1.0)
    return sc


def s22(t, dur):
    u = t / dur
    k = clamp(t / 0.4)
    pts = [(-4.2 + 0.9 * i, 0.4 + 0.5 * math.sin(i * 0.7)) for i in range(26)]
    sc = cam((-2.4, 2.4, 10.8), (-2.4, 1.8, 0.0), u, 0.0, 50, mood=NIGHT)
    town(sc, oak=k, t=t, oak_col=gs.GOLD)
    gs.trail(sc, [p for p in pts if p[0] > -3.6][: int(3 + 40 * clamp(t / 1.4))], t, k)
    sc.flash = max(0.0, 0.45 * (1 - t / 0.2))
    character(sc, RUDY_PJ, (-4.4, 0, 0.0), yaw=70, face="joy", pose=dict(ar=(150, -20)))
    return sc


def s23(t, dur):
    u = t / dur
    sc = cam((-2.8, 2.4, 12.5), (-2.8, 1.8, 0.4), u, 0.05, 44, mood=NIGHT)
    town(sc, oak=0.9, t=t, oak_col=gs.GOLD)
    character(sc, RUDY_PJ, (-3.6, 0, 0.4), yaw=40, face="worried" if t < dur * 0.6 else "smile", pose=dict(head=(0, 6, 0)))
    face = "smirk" if t < dur * 0.62 else "smile"
    character(sc, TIM, (-2.0, 0, 0.5), yaw=-40, face=face, pose=dict(head=(0, 0, 0)))
    return sc


# ------------------------------------------------------------ 24-30: the gate
def s24(t, dur):
    u = t / dur
    x = -8.0 + 16.0 * u
    sc = cam((x + 0.4, 2.2, 11.5), (x + 0.6, 1.6, 0.6), u, 0.0, 46, mood=PREDAWN)
    gs.gym(sc, t)
    pts = [(x0, 0.6) for x0 in np.arange(-12, 14, 0.8)]
    gs.trail(sc, pts, t, 1.0)
    for i, (spec, dx) in enumerate(((RUDY_PJ, 0.0), (TIM, 1.9))):
        character(sc, spec, (x + 1.0 + dx - 1.4, 0, 0.6 + 0.3 * i), yaw=90, face="grit", pose=dict(walk(t, 16, 40), lean=18))
    speed_lines(sc, t, cx=0.5, cy=0.4, n=12, inner=0.4, alpha=80)
    return sc


def s25(t, dur):
    u = t / dur
    off = clamp((t - 1.3) / 1.6)
    k = 0.6 + 0.4 * math.sin(t * 6)
    sc = cam((GATE_X - 2.0, 2.8, 14.0), (GATE_X - 1.9, 2.4, -6.0), u, 0.05, 46, mood=PREDAWN)
    gs.lot(sc, t)
    gs.ivy_wall(sc, off, t=t)
    gs.glow_tree(sc, GATE_X - 5.2, -2.6, "maple", k, h=5.2, t=t, seed=2)
    gs.peeking_flowers(sc, 0.2 + 0.3 * off, t, tree_k=0.2)
    character(sc, RUDY_PJ, (GATE_X - 3.4, 0, 1.0), yaw=180 - 20, face="shock", pose=dict(al=(20, 8), ar=(20, 8)))
    character(sc, TIM, (GATE_X - 1.8, 0, 1.2), yaw=180 + 20, face="shock")
    return sc


def s26(t, dur):
    u = t / dur
    run = clamp(t / 1.3)
    fall = clamp((t - 1.3) / 0.35)
    x = lerp(GATE_X - 5.0, GATE_X - 1.0, run)
    sc = cam((GATE_X - 2.4, 2.4, 11.2), (GATE_X - 2.4, 1.4, -1.0), u, 0.0, 48, mood=PREDAWN)
    gs.lot(sc, t)
    gs.ivy_wall(sc, 1.0, t=t)
    sc.blob(T(GATE_X - 1.0, 0.1, -1.0), (1.4, 0.2, 0.4), (110, 76, 52), layer=3, n=8, m=4)
    pose = walk(t, 16, 40) if run < 1 else {}
    pose = dict(pose, lean=lerp(18, 80, fall), al=(150 * fall, -20), ar=(150 * fall, -20))
    character(sc, TIM, (x, 0.0 + 0.0 * fall, -1.0), yaw=90, face="shock" if fall > 0 else "grit", pose=pose)
    if fall > 0.5:
        ls.sticker(sc, (GATE_X - 1.0, 1.2, -1.0), "THUD!", t, start=1.45, hold=1.4, size=0.7, dy=0.5, color=(255, 230, 80))
    character(sc, RUDY_PJ, (GATE_X - 4.6, 0, 0.6), yaw=90, face="shock", pose=dict(walk(t, 14, 30), lean=12))
    return sc


def s27(t, dur):
    k, tt = subs(t, 27, dur, (0, 5))
    u = t / dur
    if k == 0:
        sc = cam((GATE_X - 0.6, 1.6, 3.4), (GATE_X, 1.9, -6.0), u, 0.1, 40, mood=SUNRISE)
        gs.lot(sc, t)
        gs.ivy_wall(sc, 1.0, t=t)
        gs.peeking_flowers(sc, 0.5, t, tree_k=0.4)
        character(sc, RUDY_PJ, (GATE_X - 0.4, 0, -2.6), yaw=180, face="grit", pose=dict(walk(t, 16, 30), lean=16))
    else:
        pose = dict(head=(25, 0, 0), lean=8)
        sc = head_cu(RUDY_PJ, (GATE_X, 0, -2.4), 0, pose, tt / 3.0, dist=2.4, fov=34, up=0.25, mood=SUNRISE, bloom=1.0)
        gs.lot(sc, t)
        gs.ivy_wall(sc, 1.0, t=t)
        character(sc, RUDY_PJ, (GATE_X, 0, -2.4), face="worried", pose=pose)
    return sc


def s28(t, dur):
    u = t / dur
    k = clamp((t - 0.3) / 0.9)
    sc = cam((GATE_X - 1.2, 2.2, 9.0), (GATE_X - 1.2, 1.5, -1.2), u, 0.06, 46, mood=PREDAWN)
    gs.lot(sc, t)
    gs.ivy_wall(sc, 1.0, t=t)
    character(sc, RUDY_PJ, (GATE_X - 1.9, 0, -1.2), yaw=60, face="smile", pose=dict(al=(20, 8), ar=(60, -10), lean=8))
    after = t > dur * 0.5
    character(sc, TIM, (GATE_X - 0.4, 0, -1.0), yaw=-60, face="shock" if not after else "grin",
              pose=dict(roll=lerp(78, 0, k), y=lerp(0.2, 0.0, k)) if k < 1 else dict(ar=(20, 8)))
    return sc


def s29(t, dur):
    u = t / dur
    k = lerp(1.0, 0.1, clamp(t / 1.4))
    sc = cam((GATE_X - 0.5, 1.6, 2.6), (GATE_X, 1.4, -6.0), u, 0.12, 36, mood=PREDAWN)
    gs.lot(sc, t)
    gs.ivy_wall(sc, 1.0, t=t)
    gs.glow_tree(sc, GATE_X - 3.4, -3.0, "maple", k, h=5.2, t=t, seed=2)
    return sc


def s30(t, dur):
    u = t / dur
    sc = cam((GATE_X - 0.4, 1.7, 1.6), (GATE_X, 1.4, -6.0), u, 0.2, 32, mood=PREDAWN)
    gs.lot(sc, t)
    gs.ivy_wall(sc, 1.0, t=t)
    gs.glow_tree(sc, GATE_X - 3.4, -3.0, "maple", 0.1, h=5.2, t=t, seed=2)
    ls.glow_at(sc, (GATE_X, 1.2, -5.8), 0.6, gs.GOLD, int(40 + 40 * math.sin(t * 4)))
    add_emote(sc, "?", (GATE_X, 2.2, -5.8), t, size=0.6, dy=0.2, start=0.6)
    return sc


# ------------------------------------------------------------ 31-35: Tim's secret
def s31(t, dur):
    k, tt = subs(t, 31, dur, (0, 5))
    u = t / dur
    if k == 0:
        pose = dict(head=(0, 8, 0))
        sc = head_cu(TIM, (GATE_X - 1.0, 0, -2.0), 0, pose, tt / 2.4, dist=2.4, fov=34, up=0.3, mood=PREDAWN, bloom=1.0)
        gs.lot(sc, t)
        gs.ivy_wall(sc, 1.0, t=t)
        character(sc, TIM, (GATE_X - 1.0, 0, -2.0), face="worried", pose=pose)
    else:
        sc = cam((GATE_X + 4.0, 2.0, 3.0), (GATE_X + 6.2, 2.0, -3.4), tt / 2.4, 0.1, 40, mood=PREDAWN)
        gs.lot(sc, t)
        gs.ivy_wall(sc, 1.0, t=t)
        gs.glow_tree(sc, GATE_X + 6.2, -3.0, "pine", 0.0, h=5.6, t=t, seed=3)
        whisper_to(sc, TIM, (GATE_X + 4.8, 0, -1.8), GATE_X + 6.2, face="worried", t=t)
    return sc


def s32(t, dur):
    u = t / dur
    k = clamp((t - 0.8) / max(0.5, dur - 1.6))
    sc = cam((GATE_X + 4.2, 2.4, 7.8), (GATE_X + 5.5, 2.2, -2.0), u, 0.08, 42, mood=PREDAWN)
    gs.lot(sc, t)
    gs.ivy_wall(sc, 1.0, t=t)
    gs.glow_tree(sc, GATE_X + 6.2, -3.0, "pine", k, h=5.6, t=t, seed=3, color=gs.GOLD)
    a = whisper_to(sc, TIM, (GATE_X + 4.9, 0, -1.8), GATE_X + 6.2, face="sad", t=t)
    if t > 1.5:
        add_emote(sc, "tears", a["head_top"], t, size=0.4, dx=0.2, dy=0.0, start=1.6, hold=3.0)
    return sc


def s33(t, dur):
    u = t / dur
    sc = cam((GATE_X + 3.8, 2.0, 10.6), (GATE_X + 4.4, 3.6, -3.0), u, 0.05, 50, mood=PREDAWN)
    gs.lot(sc, t)
    gs.ivy_wall(sc, 1.0, t=t)
    gs.glow_tree(sc, GATE_X + 6.2, -3.0, "pine", 1.0, h=5.6, t=t, seed=3, color=gs.GOLD)
    sc.flash = max(0.0, 0.8 * (1 - t / 0.3))
    sparks(sc, (GATE_X + 6.2, 4.0, -1.0), t, seed=5, n=10, r=2.6, color=gs.GOLD)
    character(sc, TIM, (GATE_X + 3.8, 0, 0.6), yaw=-30, face="shock", pose=dict(al=(40, 12), ar=(40, 12), head=(0, -14, 0)))
    character(sc, RUDY_PJ, (GATE_X + 2.6, 0, 0.8), yaw=-20, face="shock", pose=dict(head=(0, -14, 0)))
    return sc


def s34(t, dur):
    u = t / dur
    k = clamp((t - 0.2) / 1.2)
    sc = cam((GATE_X, 2.6, 11.0 - 1.5 * u), (GATE_X, 2.6, -8.0), u, 0.0, 46, mood=SUNRISE)
    gs.lot(sc, t)
    gs.ivy_wall(sc, 1.0, gate_open=k, locked=False, t=t)
    gs.peeking_flowers(sc, 0.8, t, tree_k=0.8)
    sc.light((GATE_X, 2.0, -3.0), (255, 214, 130), 700 * k, 1.0)
    character(sc, RUDY_PJ, (GATE_X - 1.1, 0, 1.4), yaw=180, face="joy", pose=dict(al=(30, 10), ar=(30, 10)))
    character(sc, TIM, (GATE_X + 1.1, 0, 1.4), yaw=180, face="joy", pose=dict(al=(30, 10), ar=(30, 10)))
    return sc


def s35(t, dur):
    k, tt = subs(t, 35, dur, (0, 8))
    u = t / dur
    glow_k = clamp(t / 1.4)
    if k == 0:
        sc = cam((GATE_X - 0.4 + 0.4 * u, 2.8, WALL_Z0 - 1.4), (GATE_X, 2.6, WALL_Z0 - 14.0), u, 0.04, 50, mood=SUNRISE)
        gs.garden(sc, t, glow_k, weeds_k=0.0, tree_k=glow_k)
        character(sc, RUDY_PJ, (GATE_X - 0.9, 0, WALL_Z0 - 9.0), yaw=180, face="joy", pose=dict(al=(150, -20), ar=(150, -20)))
        character(sc, TIM, (GATE_X + 0.9, 0, WALL_Z0 - 9.0), yaw=180, face="joy", pose=dict(al=(150, -20), ar=(150, -20)))
    else:
        sc = cam((GATE_X + 0.4, 0.6, WALL_Z0 - 2.4), (GATE_X + 0.6, 0.5, WALL_Z0 - 6.0), tt / 3.4, 0.1, 38, mood=SUNRISE)
        gs.garden(sc, t, 1.0, weeds_k=clamp(tt / 0.6), tree_k=1.0)
        gs.weed(sc, GATE_X + 0.6, WALL_Z0 - 4.0, clamp(tt / 0.6), t)
        add_emote(sc, "stars", (GATE_X + 0.6, 0.9, WALL_Z0 - 4.0), t, size=0.5, dy=0.2, start=0.5)
    return sc



# ------------------------------------------------------------ 36-42: the town comes running
def s36(t, dur):
    u = t / dur
    sc = cam((0.5, 3.4, 12.5), (0.5, 3.6, -3.0), u, 0.04, 50, mood=SUNRISE)
    town(sc, 0.5, 0.5, 1.0, t=t)
    gs.beam(sc, (PINE[0], 0, PINE[1]), 1.0, gs.GOLD)
    for i in range(8):
        a_ = i * 0.8 + t * 1.2
        x = -9.0 + ((i * 2.9 + t * 4.0) % 18.0)
        character(sc, crowd_spec(i + 20, adult=i % 2 == 0), (x, 0, 1.2 + 0.5 * (i % 3)), yaw=90, face=("shock", "joy")[i % 2],
                  pose=dict(walk(t + i, 14, 36), lean=10))
    return sc


def s37(t, dur):
    k, tt = subs(t, 37, dur, (0, 3, 7))
    u = tt / max(0.5, dur / 3)
    run = lambda tt_: walk(tt_, 14, 34)
    if k == 0:
        x = lerp(-4.0, 1.0, clamp(tt / 1.6))
        sc = cam((x - 0.4, 2.4, 10.0), (x, 1.8, 0.0), u, 0.05, 44, mood=SUNRISE)
        town(sc, 0.4, 0.4, 0.8, t=t)
        a = character(sc, DAD_G, (x, 0, 0.0), yaw=0, face="joy", pose=dict(run(t), ar=(110, -20), er=70))
        ss.flour(sc, a, t)
        gs.cake(sc, T(*(a["hand_r"] + np.array([0.0, 0.15, 0.1]))), 0.45, t=t)
    elif k == 1:
        x = lerp(-3.0, 1.5, clamp(tt / 1.6))
        sc = cam((x + 0.4, 2.4, 10.0), (x, 1.8, 0.0), u, 0.05, 44, mood=SUNRISE)
        town(sc, 0.4, 0.4, 0.8, t=t)
        a = character(sc, PATEL, (x, 0, 0.0), yaw=0, face="joy", pose=dict(run(t), ar=(160, -20)))
        gs.chalk(sc, a, t)
        sc.box(T(*(a["hand_r"] + np.array([0.0, 0.2, 0.0]))), (0.08, 0.34, 0.08), (255, 255, 255), layer=6)
    else:
        sc = cam((0.0, 2.6, 11.5), (0.0, 1.9, 0.4), u, 0.06, 46, mood=SUNRISE)
        town(sc, 0.4, 0.4, 0.8, t=t)
        for i, (spec, x) in enumerate(((DAD_G, -1.8), (PATEL, 0.0), (GOMEZ, 1.8))):
            a = character(sc, spec, (x, 0, 0.4), face="neutral", pose=dict(al=(20, 8), ar=(20, 8), head=(0, 0, 4 * (i - 1))))
            add_emote(sc, "?", a["head_top"], t, size=0.45, dx=0.4, dy=0.15, start=0.2 + 0.2 * i)
            if i == 2:
                gs.sunhat(sc, a, GOMEZ)
                gs.garden_gloves(sc, a)
    return sc


def s38(t, dur):
    u = t / dur
    hug = clamp((t - word_t(38, 4, dur * 0.4)) / 0.4)
    sc = cam((GATE_X - 0.2, 2.6, WALL_Z0 - 0.9), (GATE_X + 0.2, 1.9, WALL_Z0 - 8.0), u, 0.06, 50, mood=SUNRISE)
    gs.garden(sc, t, 1.0)
    pose = dict(al=(80, -30), ar=(80, -30), el=50, er=50) if hug >= 1 else dict(al=(20, 8), ar=(100, -20), er=80)
    a = character(sc, GOMEZ, (GATE_X - lerp(1.0, 0.5, hug), 0, WALL_Z0 - 7.6), yaw=-10 + 90 * 0, face="cry" if hug < 1 else "joy",
                  pose=pose, face_extra=gs.dirt_cheeks)
    gs.sunhat(sc, a, GOMEZ)
    gs.garden_gloves(sc, a)
    character(sc, TIM, (GATE_X + lerp(1.2, 0.5, hug), 0, WALL_Z0 - 7.6), yaw=10, face="joy" if hug >= 1 else "shock",
              pose=pose if hug >= 1 else dict(al=(20, 8), ar=(20, 8)))
    character(sc, RUDY_G, (GATE_X + 1.7, 0, WALL_Z0 - 8.6), yaw=-30, face="joy", pose=dict(ar=(40, 10)))
    return sc


def s39(t, dur):
    u = t / dur
    off = t > word_t(39, 8, dur * 0.6)
    sc = cam((1.6, 2.8, 15.0), (3.4, 2.4, -4.0), u, 0.05, 44, mood=SUNRISE)
    gs.lot(sc, t)
    gs.ivy_wall(sc, 1.0, gate_open=1.0, locked=False, t=t)
    gs.peeking_flowers(sc, 1.0, t, tree_k=1.0)
    gs.bulldozer(sc, T(GATE_X - 4.5, 0, 0.0) @ RY(-10), t, engine=not off)
    character(sc, DRIVER, (GATE_X - 2.6, 0, 2.6), yaw=-20, face="shock" if not off else "joy",
              pose=dict(al=(20, 8), ar=(150, -20) if off else (20, 8)))
    gs.lot_sign(sc, T(GATE_X - 8.0, 0, 0.5) @ RY(20))
    return sc


def s40(t, dur):
    u = t / dur
    sc = cam((GATE_X - 0.6, 2.8, 16.0), (GATE_X - 0.6, 2.6, -4.0), u, 0.04, 46, mood=SUNRISE)
    gs.lot(sc, t)
    gs.ivy_wall(sc, 1.0, gate_open=1.0, locked=False, t=t)
    gs.peeking_flowers(sc, 1.0, t, tree_k=1.0)
    gs.bulldozer(sc, T(GATE_X - 3.2 - 3.0 * u, 0, -0.4) @ RY(-60), t, engine=True)
    gs.lot_sign(sc, T(GATE_X + 1.8, 0, 1.0) @ RY(-10), state="garden")
    sparks(sc, (GATE_X, 2.6, -5.0), t, seed=7, n=8, r=3.0, color=gs.GOLD)
    return sc


def s41(t, dur):
    u = t / dur
    c = np.array([GATE_X, 0.0, WALL_Z0 - 8.0])
    sc = cam((GATE_X, 8.8, WALL_Z0 + 3.0), (GATE_X, 0.6, WALL_Z0 - 8.0), u, 0.04, 50, mood=DAY, bloom=0.4)
    gs.garden(sc, t, 1.0, lights=False)
    gs.picnic(sc, T(*c))
    gs.cake(sc, T(c[0], 0.04, c[2]), 0.8, flame=False)
    ring = [(RUDY_G, -0.9, 0.9, "joy"), (TIM, 0.9, 0.9, "grin"), (DAD_G, -1.4, -1.1, "joy"), (PATEL, 1.4, -1.1, "laugh"),
            (GOMEZ, 0.0, -1.5, "joy")]
    for spec, dx, dz, face in ring:
        ll = spec["leg"][1] * spec["s"]
        p = sit()
        p.update(ar=(40, 10), al=(40, 10))
        a = character(sc, spec, (c[0] + dx, 0.05, c[2] + dz), yaw=math.degrees(math.atan2(-dx, -dz)) + 0, face=face, pose=p)
        if spec is GOMEZ:
            gs.sunhat(sc, a, GOMEZ)
            gs.garden_gloves(sc, a)
    return sc


def s42(t, dur):
    u = t / dur
    k = clamp((t - word_t(42, 6, dur * 0.6)) / 0.5)
    pose = dict(ar=(120, -20), er=100, head=(0, 6, 0))
    sc = head_cu(DAD_G, (GATE_X, 0, WALL_Z0 - 8.0), 0, pose, u, dist=5.2, up=0.1, fov=36, mood=DAY, bloom=0.8)
    gs.garden(sc, t, 1.0, lights=False)
    gs.glow_tree(sc, GATE_X + 3.2, WALL_Z0 - 12.0, "oak", k, h=5.0, t=t, seed=1)
    a = character(sc, DAD_G, (GATE_X, 0, WALL_Z0 - 8.0), face="grin" if t < dur * 0.5 else "joy", pose=pose)
    ss.flour(sc, a, t)
    sc.blob(T(*(a["hand_r"] + np.array([0.0, 0.1, 0.05]))), (0.16, 0.16, 0.16), (255, 150, 190), layer=7, n=8, m=6)
    sc.blob(T(*(a["face_pt"] + np.array([0.1, -0.05, 0.04]))), (0.12, 0.12, 0.12), (255, 150, 190), layer=7, n=8, m=6)
    ls.sticker(sc, a["head"], "BUSTED!", t, start=word_t(42, 6, dur * 0.6), hold=2.4, size=0.5, dx=0.0, dy=1.6,
               color=(255, 160, 40))
    return sc


_FNS = [globals()[f"s{i:02d}"] for i in range(1, len(LINES) + 1)]
SHOTS = [(i + 1, 1.6, txt, fn) for i, (txt, fn) in enumerate(zip(LINES, _FNS))]
SHOTS, WORD_TIMES = load_timing(SHOTS, TIMING_FILE)
WT.update(WORD_TIMES)
