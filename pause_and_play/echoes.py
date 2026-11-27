"""When Echoes Do The Talking: shot list. Each shot: (number, seconds, caption text, fn(t, dur) -> Scene)."""
import os

TIMING_FILE = "echoes_timing.json"
SPOKEN = {"Mr": "mister", "Mrs": "missus", "Patels": "patels", "Lily's": "lily's"}
PHONES = {"rudy": "R UW D IY", "patel": "P AH T EH L", "patels": "P AH T EH L Z", "gomez": "G OW M EH Z",
          "lily": "L IH L IY", "lily's": "L IH L IY Z", "shushed": "SH AH SH T", "pancakes": "P AE N K EY K S", "wobbles": "W AA B AH L Z"}

LINES = [
    "In this town, EVERY word you say",
    "gets said back to you. Once.",
    "It's called the echo. It never takes a day off.",
    "Dad yells, PANCAKES! The echo yells it too.",
    "So Dad has to flip two.",
    "Mrs Patel says, Homework tonight. The echo agrees.",
    "Nobody argues with two Mrs Patels.",
    "Mr Gomez, the librarian, only whispers.",
    "Even his whispers echo. It's the loudest quiet place in town.",
    "I'm Rudy. The kid with the messy hair.",
    "Tonight is the school talent show, and I wrote a song.",
    "Four verses. I practiced every night, right next door to Lily.",
    "My rival, Lily, is the best dancer in school.",
    "Pink sneakers. A ponytail that never wobbles.",
    "She practices next door too, counting out loud. Five, six, seven, eight!",
    "The echo counts it again. I hear every step. Twice.",
    "Backstage, my stomach did a drum solo.",
    "Lily went first. She spun. She leaped.",
    "The whole hall yelled, WOW! And the echo yelled it back.",
    "Then Mrs Patel called, Rudy! And the echo called, Rudy!",
    "I walked on stage. The lights were hot.",
    "I opened my mouth, and my song was GONE.",
    "Not one word. Not one note.",
    "Even the echo had nothing to say back.",
    "The crowd stared. The clock ticked.",
    "Then I remembered the rule.",
    "Every word gets said back.",
    "So I whispered one word. Help.",
    "Help, said the echo. All the way to the wings.",
    "And somebody whispered back my first line.",
    "Lily. She'd heard my song through the wall every night.",
    "Twice.",
    "So I sang it back to her. Line by line.",
    "Then the whole hall joined in.",
    "Mrs Patel sang. Dad sang. Mr Gomez sang the loudest of all.",
    "Nobody shushed him.",
    "Lily danced. I sang. The echo made us a choir.",
    "The judges jumped to their feet.",
    "Best Duet, they said. Best Duet, said the echo.",
    "Thanks for listening, I told Lily. Through the wall.",
    "Dad shouted, Pizza for everyone! The echo shouted it too.",
    "Dad paid double.",
]
import math  # noqa: E402

import numpy as np  # noqa: E402

import echoes_sets as es  # noqa: E402
import laughs_sets as ls  # noqa: E402
import sets  # noqa: E402
import shoes_sets as ss  # noqa: E402
from cast import DAD, _spec, character, crowd_spec, sit  # noqa: E402
from engine import RX, RY, RZ, T, add_emote, clamp, lerp  # noqa: E402
from laughs import dcam, head_cu, ht  # noqa: E402
from shots import confetti, probe, sparks, walk  # noqa: E402
from story import load_timing  # noqa: E402

RUDY_E = _spec(name="Rudy", style="messy", s=0.98, skin=(236, 190, 150), shirt=(255, 168, 30), hoodie=True,
               accent=(250, 250, 250), pants=(46, 56, 100), shoes=(250, 250, 250), hair=(96, 62, 40), sleeve=0.9)
LILY_E = _spec(name="Lily", style="ponytail", s=0.99, skin=(240, 200, 164), shirt=(250, 250, 252), pants=(120, 90, 190),
               shoes=(255, 70, 190), hair=(58, 36, 30), accent=(255, 90, 170), sleeve=0.5)
DAD_E = dict(DAD, apron=(250, 250, 244), name="Dad")
PATEL_E = _spec(name="Mrs Patel", style="bun", s=1.2, skin=(214, 156, 118), shirt=(250, 250, 252), inner=(130, 176, 232),
                cardigan=True, pants=(70, 70, 100), shoes=(90, 70, 70), hair=(30, 24, 28), glasses=True,
                accent=(240, 120, 160), sleeve=0.86, backpack=(158, 100, 60))
GOMEZ_E = _spec(name="Mr Gomez", style="short", s=1.3, torso=(1.2, 1.0, 0.6), arm=(0.58, 1.0), skin=(190, 132, 96),
                shirt=(250, 244, 230), inner=(250, 244, 230), cardigan=True, glasses=True, pants=(96, 84, 70),
                shoes=(60, 46, 40), hair=(30, 24, 24), sleeve=0.86, accent=(150, 110, 70))
INDOOR = ((246, 232, 206), (246, 232, 206))
DARK_SKY = ((26, 22, 46), (60, 46, 80))
WT = {}


def word_t(num, i, default=0.0):
    w = WT.get(num, [])
    return w[i][0] if i < len(w) else default


def kid(i):
    return crowd_spec(i)


def shout_pose(k=1.0):
    return dict(lean=-6 * k, head=(0, -10 * k, 0), al=(30, 10), ar=(30, 10))


def cup_pose():
    return dict(ar=(100, 26), er=100, al=(100, -26), el=100, head=(0, -8, 0))


def ear_pose():
    return dict(ar=(120, 8), er=130, al=(8, 4), head=(14, 0, 8))


def tremble(t, k=0.015):
    return math.sin(t * 38) * k


# ------------------------------------------------------- 1-3: the rule
def s01(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.8, 12.5), (0.0, 1.9, 0.0), u, 0.08, fov=42)
    sets.town(sc)
    a = character(sc, kid(4), (-1.5, 0, 0.5), yaw=15, face="shock", pose=shout_pose())
    b = character(sc, kid(2), (1.6, 0, -0.6), yaw=-12, face="grin", pose=dict(ar=(40, 10), al=(20, 6)))
    character(sc, RUDY_E, (0.1, 0, -1.4), yaw=0, face="smile")
    es.echo(sc, a["head_top"], "HELLO!", t, 0.12, delay=0.75, hold=1.4, size=0.6, dx=0.5, dy=0.4)
    return sc


def s02(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.4, 9.4), (0.0, 1.9, 0.0), u, 0.08, fov=40)
    sets.town(sc)
    a = character(sc, kid(5), (-1.2, 0, 0.0), yaw=40, face="jaw", pose=cup_pose())
    b = character(sc, kid(2), (1.3, 0, 0.0), yaw=-40, face="shock", pose=dict(ar=(30, 10), al=(20, 8)))
    t0 = word_t(2, 1, 0.4)
    es.say(sc, a["head_top"], "HI!", t, 0.15, hold=0.9, size=0.6, dx=0.3)
    es.say(sc, b["head_top"], "hi!", t, t0 + 0.2, hold=1.3, size=0.6, color=es.ECHO_B, dx=-0.3)
    es.rings(sc, b["head"], t, t0 + 0.2, es.ECHO_B, 3, 1.2, 1.4)
    return sc


def s03(t, dur):
    u = t / dur
    sc = dcam((-0.6, 2.4, 9.0), (0.0, 2.2, 0.0), u, 0.1, fov=42)
    sets.town(sc)
    a = character(sc, RUDY_E, (0.0, 0, 0.0), yaw=-10, face="smirk", pose=ear_pose())
    for k in range(3):
        es.rings(sc, (0.0, 3.4, -3.0), t, 0.2 + k * 0.6, es.ECHO_B if k % 2 else es.ECHO_A, 3, 1.6, 3.4)
    es.say(sc, (-1.2, 3.6, -2.0), "ECHO", t, 0.35, hold=1.5, size=0.6, dx=0.0, ring=False)
    es.say(sc, (1.0, 4.6, -2.0), "echo", t, 1.1, hold=1.5, size=0.5, color=es.ECHO_B, ring=False)
    return sc


# ------------------------------------------------------- 4-9: Dad, Mrs Patel, Mr Gomez
def kitchen_set(sc):
    sets.kitchen(sc)


def s04(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.0, 9.0), (0.0, 2.2, -2.0), u, 0.08, fov=42, sky=INDOOR)
    kitchen_set(sc)
    a = character(sc, DAD_E, (0.0, 0, -2.4), yaw=0, face="jaw", pose=shout_pose())
    es.echo(sc, a["head_top"], "PANCAKES!", t, word_t(4, 2, 0.8), delay=max(0.5, word_t(4, 5, 1.7) - word_t(4, 2, 0.8)),
            hold=1.5, size=0.55, dx=-0.5, dy=0.4)
    return sc


def s05(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.4, 8.6), (0.0, 2.6, -2.0), u, 0.06, fov=42, sky=INDOOR)
    kitchen_set(sc)
    a = character(sc, DAD_E, (0.0, 0, -2.4), yaw=0, face="shock", pose=dict(ar=(70, 6), er=70, al=(20, 4)))
    es.spatula(sc, T(*(a["hand_r"] + np.array([0.0, 0.1, 0.3]))) @ RX(70), 1.5)
    for k in range(2):
        ph = ((t * 0.7 + k * 0.5) % 1.0)
        y = 3.0 + 2.4 * math.sin(math.pi * ph)
        es.pancake(sc, T(-0.7 + 1.4 * k, y, -1.4), 1.7, flip=ph * 360)
    es.say(sc, a["head_top"], "x2", t, 0.4, hold=1.4, size=0.7, color=es.ECHO_B, dx=0.6, dy=0.5, ring=False)
    return sc


def s06(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.0, 10.0), (0.0, 2.1, -1.0), u, 0.08, fov=42, sky=INDOOR)
    sets.classroom(sc)
    sets.class_desks(sc, t, frozen=True, faces=("worried", "shock"))
    a = character(sc, PATEL_E, (0.0, 0, -2.6), yaw=0, face="jaw", pose=shout_pose(0.6))
    es.echo(sc, a["head_top"], "HOMEWORK!", t, word_t(6, 2, 0.5), delay=0.8, hold=1.6, size=0.55, dx=-0.3, dy=0.4)
    return sc


def s07(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.0, 10.0), (0.0, 2.1, -1.0), u, 0.08, fov=42, sky=INDOOR)
    sets.classroom(sc)
    ghost = dict(PATEL_E, shirt=(180, 226, 255), inner=(120, 190, 255), name="Echo Patel")
    a = character(sc, PATEL_E, (-1.5, 0, -2.2), yaw=-12, face="angry", pose=dict(ar=(70, 8), er=80))
    b = character(sc, ghost, (1.5, 0, -2.2), yaw=12, face="angry", pose=dict(al=(70, 8), el=80))
    for k, x in enumerate((-2.6, 0.0, 2.6)):
        character(sc, kid(k + 12), (x, 0, 1.4), yaw=180 if False else 0, face="worried",
                  pose=dict(head=(0, 6, 0), al=(30, 6), ar=(30, 6)))
    es.say(sc, (0.0, 4.6, -2.2), "x2!", t, 0.3, hold=1.8, size=0.9, color=es.ECHO_B, dy=0.0, ring=False)
    add_emote(sc, "sweat", a["head_top"], t, size=0.5, start=0.5)
    return sc


def s08(t, dur):
    u = t / dur
    sc = dcam((1.4, 2.8, 9.0), (0.0, 2.2, -1.0), u, 0.1, fov=42, sky=INDOOR)
    es.library(sc, t)
    a = character(sc, GOMEZ_E, (0.0, 0, -1.2), yaw=0, face="smile", pose=dict(ar=(120, 20), er=120, head=(0, 0, 4)))
    es.say(sc, a["head_top"], "shh...", t, 0.7, hold=1.4, size=0.32, color=es.ECHO_A, dx=0.3, dy=0.3, ring=False)
    return sc


def s09(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.4, 10.0), (0.0, 2.4, -1.5), u, 0.1, fov=44, sky=INDOOR)
    es.library(sc, t)
    character(sc, GOMEZ_E, (0.0, 0, -1.2), yaw=0, face="worried", pose=dict(ar=(150, -10), er=60, al=(150, -10), el=60))
    for k, x in enumerate((-3.2, 3.2)):
        character(sc, kid(k + 20), (x, 0, 1.2), yaw=0, face="shock", pose=dict(al=(150, -40), ar=(150, -40), el=110, er=110))
    es.shush_signs(sc, t, 0.5, 6)
    es.rings(sc, (0.0, 3.0, -1.2), t, 0.3, es.ECHO_B, 3, 1.6, 4.0)
    return sc


# ------------------------------------------------------- 10-16: Rudy, the song, Lily
def s10(t, dur):
    u = t / dur
    pose = dict(head=(-6, 0, 4), ar=(30, 30), er=60)
    sc = head_cu(RUDY_E, (0, 0, 0), 0, pose, u, dist=3.0, side=0.3, up=0.05, fov=34)
    sets.town(sc)
    character(sc, RUDY_E, (0, 0, 0), face="grin", pose=pose)
    return sc


def s11(t, dur):
    u = t / dur
    pose = dict(ar=(70, 10), er=75, al=(70, -10), el=75, head=(0, 0, -4))
    sc = dcam((0.0, 2.8, 8.0), (0.0, 2.1, 0.0), u, 0.1, fov=40)
    sets.town(sc)
    a = character(sc, RUDY_E, (0, 0, 0), face="sparkle", pose=pose)
    es.song_page(sc, T(*(a["hand_r"] + a["hand_l"]) / 2 + np.array([0.0, -0.25, 0.35])) @ RX(-10), 0.8, 1.0)
    es.notes(sc, a["head_top"] + np.array([0.7, 0.2, 0.0]), t)
    return sc


def s12(t, dur):
    u = t / dur
    sc = dcam((0.0, 4.0, 14.0), (0.0, 2.4, -1.0), u, 0.05, fov=42, sky=INDOOR)
    es.two_rooms(sc, t)
    a = character(sc, RUDY_E, (-1.5, 0, 1.4), yaw=40, face="grin", pose=dict(ar=(100, 8), er=110, lean=-6))
    sc.blob(T(*(a["hand_r"] + np.array([0.0, 0.2, 0.2]))), (0.2, 0.2, 0.2), (190, 190, 200), layer=7, n=8, m=6)
    es.notes(sc, a["head_top"] + np.array([1.0, 0.4, 0.0]), t, n=5)
    for k in range(3):
        es.notes(sc, (-0.4 + 0.4 * k, 3.4 + 0.2 * k, 0.0), t + k * 0.3, n=1)
    b = character(sc, LILY_E, (1.5, 0, 1.4), yaw=-50, face="suspicious", pose=dict(al=(110, 20), el=120, ar=(110, -20), er=120))
    add_emote(sc, "?", b["head_top"], t, size=0.5, start=0.8, hold=1.4)
    return sc


def s13(t, dur):
    u = t / dur
    pose = dict(head=(0, 4, 6), al=(30, 10), ar=(30, 10))
    sc = head_cu(LILY_E, (0, 0, 0), 0, pose, u, dist=3.0, side=0.3, up=0.05, fov=34)
    sets.town(sc)
    character(sc, LILY_E, (0, 0, 0), face="smug", pose=pose)
    return sc


def s14(t, dur):
    u = t / dur
    sc = dcam((1.4, 0.7, 6.0), (0.0, 1.5, 0.0), u, 0.1, fov=44)
    sets.town(sc)
    pose = dict(ll=-14, lr=10, al=(20, 30), ar=(20, 30), y=0.0)
    a = character(sc, LILY_E, (0, 0, 0), yaw=-16, face="smug", pose=pose)
    ss.shoe_sparkles(sc, a, t, color=(255, 150, 220))
    return sc


def s15(t, dur):
    u = t / dur
    sc = dcam((1.5, 3.2, 9.0), (1.5, 2.3, 0.0), u, 0.06, fov=42, sky=INDOOR)
    es.two_rooms(sc, t)
    k = int(t * 2.2) % 4
    p = dict(al=(40 + 60 * (k % 2), 10), ar=(40 + 60 * ((k + 1) % 2), 10), ll=14 * (1 - 2 * (k % 2)),
             lr=-14 * (1 - 2 * (k % 2)), y=0.06 * (k % 2))
    a = character(sc, LILY_E, (1.5, 0, 1.2), yaw=0, face="grin", pose=p)
    for i, w in enumerate(("FIVE!", "SIX!", "SEVEN!", "EIGHT!")):
        es.say(sc, a["head_top"], w, t, word_t(15, 8 + i, 1.0 + i * 0.5), hold=0.7, size=0.45, dx=-0.5 + 0.35 * (i % 2),
               dy=0.4 + 0.22 * i, ring=False)
    return sc


def s16(t, dur):
    u = t / dur
    sc = dcam((-1.3, 3.4, 9.0), (-1.3, 2.4, 0.0), u, 0.06, fov=42, sky=INDOOR)
    es.two_rooms(sc, t)
    a = character(sc, RUDY_E, (-0.55, 0, 1.2), yaw=90, face="shock", pose=ear_pose())
    es.echo(sc, a["head_top"], "5 6 7 8!", t, 0.1, delay=max(0.6, word_t(16, 3, 1.4) - 0.1), hold=1.5, size=0.5,
            dx=-1.0, dy=0.6)
    return sc


# ------------------------------------------------------- 17-25: the talent show
def s17(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.8, 7.0), (0.0, 2.2, 0.0), u, 0.1, fov=42, sky=DARK_SKY)
    es.backstage(sc, t)
    pose = dict(lean=14, al=(60, -20), ar=(60, 20), el=80, er=80, y=tremble(t, 0.02))
    a = character(sc, RUDY_E, (0.0, 0, 0.0), yaw=0, face="worried", pose=pose)
    for k, w in enumerate(("BA-DUM", "BUM-BUM", "RAT-TAT")):
        es.say(sc, a["head_top"], w, t, word_t(17, 4 + k, 0.8 + 0.5 * k), hold=0.9, size=0.3, dx=-0.9 + 0.9 * (k % 2),
               dy=0.5 + 0.3 * k, color=es.ECHO_A, ring=False)
    add_emote(sc, "sweat", a["head_top"], t, size=0.5, start=0.2, dx=0.5)
    return sc


def lily_spin(t, u0=0.0):
    return dict(al=(90, 10), ar=(90, 10), ll=12, lr=-12, y=0.5 * abs(math.sin(t * 5)))


def s18(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.0, 7.4), (0.0, 2.0, -4.6), u, 0.08, fov=34)
    es.hall(sc, t, crowd=False)
    es.spotlight(sc, (0.0, 3.0, -5.6), 3.0)
    a = character(sc, LILY_E, (0.0, sets.STAGE_TOP, -4.6), yaw=(u * 720) % 360, face="joy", pose=lily_spin(t))
    ss.shoe_sparkles(sc, a, t, color=(255, 150, 220))
    sparks(sc, a["head"], t, seed=2, n=4, r=1.2)
    return sc


def s19(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.6, -5.0), (0.0, 2.6, 4.0), u, 0.06, fov=50)
    es.hall(sc, t, faces=("joy", "laugh", "grin"), standing=True)
    t0 = word_t(19, 4, 1.0)
    es.echo(sc, (0.0, 4.6, 1.5), "WOW!", t, t0, delay=max(0.5, word_t(19, 8, 2.0) - t0), hold=1.7, size=0.9,
            dx=-0.3, dy=0.6)
    if t > t0:
        confetti(sc, t, 40, 3)
    return sc


def s20(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.0, 7.4), (0.0, 2.0, -4.6), u, 0.08, fov=34)
    es.hall(sc, t, crowd=False)
    es.mic_stand(sc, 0.0, -4.0)
    a = character(sc, PATEL_E, (0.0, sets.STAGE_TOP, -4.8), yaw=0, face="jaw", pose=dict(ar=(80, 10), er=100, al=(30, 6)))
    t0 = word_t(20, 3, 0.8)
    es.echo(sc, a["head_top"], "RUDY!", t, t0, delay=max(0.5, word_t(20, 9, 2.0) - t0), hold=1.6, size=0.7, dx=-0.3,
            dy=0.3)
    return sc


def s21(t, dur):
    u = t / dur
    sc = dcam((2.0, 3.0, 7.4), (0.0, 2.2, -4.6), u, 0.08, fov=36)
    es.hall(sc, t, crowd=False)
    x = lerp(-2.6, -0.3, clamp(t / (dur * 0.8)))
    es.mic_stand(sc, 0.4, -4.6)
    a = character(sc, RUDY_E, (x, sets.STAGE_TOP, -4.8), yaw=90 - 60 * clamp(t / dur), face="worried", pose=walk(t, 8, 22))
    es.spotlight(sc, (0.0, 3.0, -4.6), 4.0, 90)
    add_emote(sc, "sweat", a["head_top"], t, size=0.5, start=0.8, hold=1.6)
    return sc


def s22(t, dur):
    u = t / dur
    t0 = word_t(22, 4, 1.0)
    pose = dict(head=(0, -6, 0), al=(20, 8), ar=(20, 8))
    a0 = probe(RUDY_E, (0, sets.STAGE_TOP, -6.0), 0, pose)
    sc = dcam(a0["head"] + np.array([0.2, 0.2, 3.2]), a0["head"] + np.array([0.0, -0.1, 0]), u, 0.08, fov=34)
    es.hall(sc, t, crowd=False)
    a = character(sc, RUDY_E, (0, sets.STAGE_TOP, -6.0), face="jaw", pose=pose)
    if t > t0:
        for k in range(4):
            tt = t - t0 - k * 0.1
            if tt > 0:
                p = a["head"] + np.array([0.2 * k, 0.4 + tt * 1.6, 0.4])
                es.notes(sc, p, 0.0, n=1)
        es.say(sc, a["head_top"], "POOF!", t, t0 + 0.1, hold=1.4, size=0.6, dx=0.5, dy=0.5, ring=False)
    add_emote(sc, "?", a["head_top"], t, size=0.55, start=t0 + 0.6, dx=-0.4)
    return sc


def s23(t, dur):
    u = t / dur
    pose = dict(ar=(70, 10), er=80, al=(70, -10), el=80, head=(0, 8, 0))
    a0 = probe(RUDY_E, (0, sets.STAGE_TOP, -5.0), 0, pose)
    c = (a0["hand_r"] + a0["hand_l"]) / 2
    sc = dcam(c + np.array([0.8, 1.4, 5.4]), c + np.array([0.0, 0.7, 0.0]), u, 0.1, fov=36)
    es.hall(sc, t, crowd=False)
    a = character(sc, RUDY_E, (0, sets.STAGE_TOP, -5.0), face="miserable", pose=pose)
    es.song_page(sc, T(*(a["hand_r"] + a["hand_l"]) / 2 + np.array([0.0, 0.2, 0.35])) @ RX(-8), 0.8, 1.05, text=False)
    add_emote(sc, "sweat", a["head_top"], t, size=0.5, start=0.3)
    return sc


def s24(t, dur):
    u = t / dur
    sc = dcam((0.0, 4.4, 12.5), (0.0, 2.6, -5.0), u, 0.05, fov=38)
    es.hall(sc, t, faces=("neutral", "shock"), crowd=True)
    es.mic_stand(sc, 0.0, -5.4)
    a = character(sc, RUDY_E, (0.0, sets.STAGE_TOP, -6.2), face="stung", pose=dict(al=(14, 6), ar=(14, 6)))
    ls.tumbleweed(sc, (lerp(4.0, -4.0, clamp(u * 1.1)), sets.STAGE_TOP + 0.5, -4.6), t, 0.5)
    es.say(sc, a["head_top"], "...", t, 0.4, hold=1.5, size=0.7, color=es.ECHO_A, dx=-0.5, ring=False)
    es.say(sc, a["head_top"], "...", t, 1.2, hold=1.5, size=0.6, color=es.ECHO_B, dx=0.7, dy=0.9, ring=False)
    return sc


def s25(t, dur):
    u = t / dur
    sc = dcam((0.0, 4.8, 12.5), (0.0, 4.2, -6.0), u, 0.1, fov=40)
    es.hall(sc, t, faces=("neutral",), crowd=True)
    character(sc, RUDY_E, (0.0, sets.STAGE_TOP, -5.6), face="worried", pose=dict(y=tremble(t)))
    sec = int(t * 2)
    es.say(sc, (0.0, 7.5, -8.0), "TICK" if sec % 2 == 0 else "TOCK", t, sec / 2.0, hold=0.48, size=0.6,
           color=es.ECHO_A if sec % 2 == 0 else es.ECHO_B, dx=1.2, dy=0.0, ring=False)
    return sc


# ------------------------------------------------------- 26-33: the rule, and help
def s26(t, dur):
    u = t / dur
    pose = dict(head=(0, -4, 0), al=(20, 8), ar=(20, 8))
    sc = head_cu(RUDY_E, (0, sets.STAGE_TOP, -6.0), 0, pose, u, dist=3.0, side=0.3, up=0.05, fov=34)
    es.hall(sc, t, crowd=False)
    a = character(sc, RUDY_E, (0, sets.STAGE_TOP, -6.0), face="shock", pose=pose)
    add_emote(sc, "bulb", a["head_top"], t, size=0.8, start=0.2, hold=2.0)
    es.spotlight(sc, a["head"], 1.4, 60, (255, 240, 150))
    return sc


def s27(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.6, 8.0), (0.0, 3.4, -4.0), u, 0.1, fov=40, sky=INDOOR)
    kitchen_set(sc)
    es.sign(sc, T(0.0, 4.4, -3.7), ["EVERY WORD", "GETS SAID", "BACK!"], size=(3.0, 2.2), ink=(190, 60, 70))
    es.rings(sc, (0.0, 4.4, -3.3), t, 0.2, es.ECHO_B, 3, 1.4, 2.2)
    es.rings(sc, (0.0, 4.4, -3.3), t, 1.0, es.ECHO_A, 3, 1.4, 2.2)
    character(sc, DAD_E, (-0.9, 0, -1.6), yaw=10, face="grin", pose=dict(ar=(60, 20), er=90))
    return sc


def s28(t, dur):
    u = t / dur
    pose = dict(lean=14, head=(0, 6, 0), al=(40, 6), ar=(70, 6), er=100)
    sc = dcam((0.3, 2.8, 6.4), (0.0, 2.6, -5.0), u, 0.14, fov=34)
    es.hall(sc, t, crowd=False)
    es.mic_stand(sc, 0.0, -4.7)
    a = character(sc, RUDY_E, (0.0, sets.STAGE_TOP, -5.2), face="worried", pose=pose)
    es.say(sc, a["head_top"], "help", t, word_t(28, 5, 1.0), hold=1.4, size=0.4, color=es.ECHO_A, dx=-0.4, dy=0.3,
           ring=False)
    return sc


def s29(t, dur):
    u = t / dur
    sc = dcam((0.0, 5.4, 12.5), (0.0, 3.2, -4.0), u, 0.04, fov=44)
    es.hall(sc, t, crowd=True)
    a = character(sc, RUDY_E, (0.0, sets.STAGE_TOP, -5.2), face="worried", pose=dict(al=(14, 6), ar=(14, 6)))
    es.mic_stand(sc, 0.0, -4.7)
    t0 = word_t(29, 2, 0.4)
    for k in range(4):
        es.rings(sc, (0.0, 3.0, -4.8), t, t0 + 0.25 * k, es.ECHO_B, 2, 1.8, 2.4 + 1.2 * k)
    es.say(sc, (-1.6, 5.4, -3.0), "help...", t, t0, hold=1.8, size=0.5, color=es.ECHO_B, ring=False)
    es.say(sc, (1.4, 6.2, -3.0), "help...", t, t0 + 0.5, hold=1.8, size=0.42, color=es.ECHO_B, ring=False)
    return sc


def s30(t, dur):
    u = t / dur
    sc = dcam((-0.6, 2.6, 5.6), (0.2, 2.4, -1.6), u, 0.1, fov=38, sky=DARK_SKY)
    es.backstage(sc, t)
    a = character(sc, LILY_E, (0.6, 0, -1.4), yaw=-30, face="smile", pose=dict(ar=(120, 20), er=120, head=(0, -4, 6)))
    es.say(sc, a["head_top"], "hello, moon...", t, 0.3, hold=1.9, size=0.32, color=es.ECHO_A, dx=-0.7, dy=0.5)
    es.rings(sc, a["head"], t, 0.3, es.ECHO_A, 2, 1.2, 1.0)
    return sc


def s31(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.4, 9.0), (0.0, 2.4, 0.0), u, 0.1, fov=42, sky=INDOOR)
    es.two_rooms(sc, t)
    r = character(sc, RUDY_E, (-1.2, 0, 0.6), yaw=70, face="grin", pose=dict(ar=(100, 8), er=110))
    es.notes(sc, r["head_top"] + np.array([0.5, 0.3, 0.0]), t, n=3)
    l = character(sc, LILY_E, (0.8, 0, 0.6), yaw=-90, face="smile", pose=dict(head=(0, 0, 12), ar=(60, 10), er=100))
    es.say(sc, l["head_top"], "la la", t, 0.6, hold=1.6, size=0.32, color=es.ECHO_B, dx=0.2, dy=0.4, ring=False)
    return sc


def s32(t, dur):
    u = t / dur
    pose = dict(head=(-14, 0, 14), al=(40, 10), ar=(40, 10))
    sc = head_cu(LILY_E, (0, 0, 0), -14, pose, u, dist=4.6, side=0.3, up=0.05, fov=36, sky=INDOOR)
    es.two_rooms(sc, t)
    a = character(sc, LILY_E, (0, 0, 0), yaw=-14, face="smug", pose=pose)
    es.say(sc, a["head_top"], "TWICE.", t, 0.15, hold=1.6, size=0.55, color=es.ECHO_A, dx=-0.3, dy=0.5, ring=False)
    es.say(sc, a["head_top"], "twice.", t, 0.7, hold=1.6, size=0.5, color=es.ECHO_B, dx=0.2, dy=1.1, ring=False)
    return sc


def s33(t, dur):
    u = t / dur
    sc = dcam((0.0, 4.6, 12.5), (0.0, 3.0, -5.0), u, 0.06, fov=40)
    es.hall(sc, t, crowd=True)
    es.mic_stand(sc, 0.0, -5.0)
    r = character(sc, RUDY_E, (0.0, sets.STAGE_TOP, -5.6), face="grin", pose=dict(ar=(70, 10), er=110, head=(0, -8, 0)))
    es.notes(sc, r["head_top"] + np.array([0.9, 0.3, 0.0]), t, n=4)
    es.rings(sc, r["head"], t, 0.2, es.ECHO_A, 3, 1.6, 1.6)
    es.rings(sc, r["head"], t, 1.0, es.ECHO_B, 3, 1.6, 2.2)
    l = character(sc, LILY_E, (-2.8, sets.STAGE_TOP, -5.6), yaw=30, face="smile", pose=dict(ar=(110, 20), er=120))
    es.say(sc, l["head_top"], "...", t, 0.2, hold=1.0, size=0.4, dx=0.0, ring=False)
    return sc


# ------------------------------------------------------- 34-39: the hall joins in
def s34(t, dur):
    u = t / dur
    sc = dcam((0.0, 4.2, -4.6), (0.0, 2.8, 5.0), u, 0.08, fov=56)
    es.hall(sc, t, faces=("laugh", "joy", "grin"), standing=True)
    for k in range(8):
        es.notes(sc, (-4.0 + k * 1.1, 4.6 + 0.4 * (k % 3), 0.0 + 1.6 * (k % 3)), t + k * 0.21, n=1)
    return sc


def s35(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.4, -7.8), (0.0, 2.4, 2.0), u, 0.06, fov=50)
    es.hall(sc, t, crowd=False)
    for sp, x in ((PATEL_E, -1.9), (DAD_E, 0.0), (GOMEZ_E, 1.9)):
        sway = math.sin(t * 5 + x) * 6
        a = character(sc, sp, (x, 0.0, 1.8), yaw=180 + sway, face="laugh",
                      pose=dict(al=(30 + 40 * abs(math.sin(t * 4 + x)), 8), ar=(30 + 40 * abs(math.cos(t * 4 + x)), 8),
                                head=(0, -6, sway)))
        es.notes(sc, a["head_top"] + np.array([0.4, 0.2, 0.0]), t + x, n=2)
    return sc


def s36(t, dur):
    u = t / dur
    sc = dcam((0.7, 3.0, 8.6), (0.8, 2.3, 0.0), u, 0.08, fov=38, sky=INDOOR)
    es.library(sc, t)
    a = character(sc, GOMEZ_E, (0, 0, 0), face="jaw", pose=dict(head=(0, -12, 0), lean=-8, al=(40, 10), ar=(40, 10)))
    es.say(sc, a["head_top"], "LA LA LAAA!", t, 0.1, hold=1.3, size=0.5, dx=0.3, dy=0.4)
    p = character(sc, PATEL_E, (1.9, 0, 0.3), yaw=-30, face="shock", pose=dict(ar=(120, 20) if t < 1.2 else (30, 10), er=120 if t < 1.2 else 10), shadow=False)
    es.say(sc, p["head_top"], "no shush!", t, 1.2, hold=1.4, size=0.32, color=es.ECHO_B, dx=0.0, dy=0.3, ring=False)
    return sc


def s37(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.0, 7.4), (0.0, 2.2, -4.6), u, 0.08, fov=34)
    es.hall(sc, t, crowd=False)
    es.mic_stand(sc, 1.5, -4.2)
    r = character(sc, RUDY_E, (1.5, sets.STAGE_TOP, -4.8), yaw=-12, face="grin", pose=dict(ar=(70, 10), er=110))
    l = character(sc, LILY_E, (-1.4, sets.STAGE_TOP, -4.8), yaw=(t * 200) % 360, face="joy", pose=lily_spin(t))
    ss.shoe_sparkles(sc, l, t, color=(255, 150, 220))
    for k in range(4):
        es.rings(sc, (0.0, 3.6, -5.0), t, 0.2 + 0.3 * k, es.ECHO_B if k % 2 else es.ECHO_A, 2, 1.4, 2.0 + 0.7 * k)
    es.notes(sc, r["head_top"] + np.array([0.9, 0.3, 0.0]), t, n=4)
    confetti(sc, t, 20, 5)
    return sc


def s38(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.2, -4.0), (0.0, 2.6, 1.0), u, 0.08, fov=50)
    es.hall(sc, t, crowd=True, faces=("joy",), standing=True)
    es.judge_table(sc, 0.0, -1.0, t)
    for k, x in enumerate((-1.9, 0.0, 1.9)):
        j = character(sc, crowd_spec(k + 30, adult=True), (x, 0.0, -0.1), yaw=180, face="joy",
                      pose=dict(ar=(150 + 20 * abs(math.sin(t * 7 + k)), 12), al=(150 + 20 * abs(math.cos(t * 7 + k)), 12),
                                y=0.12 * abs(math.sin(t * 7 + k))))
        es.paddle(sc, T(*(j["hand_r"] + np.array([0.0, 0.5, 0.0]))) @ RY(180), "10")
    return sc


def s39(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.0, 7.4), (0.0, 2.2, -4.6), u, 0.08, fov=34)
    es.hall(sc, t, crowd=False)
    es.trophy_duet(sc, T(0.0, sets.STAGE_TOP, -4.4), 0.9)
    character(sc, RUDY_E, (-1.5, sets.STAGE_TOP, -5.0), yaw=15, face="joy", pose=dict(ar=(150, 12), er=50))
    character(sc, LILY_E, (1.5, sets.STAGE_TOP, -5.0), yaw=-15, face="joy", pose=dict(al=(150, 12), el=50))
    t0 = word_t(39, 0, 0.4)
    es.echo(sc, (0.0, 5.2, -4.4), "BEST DUET!", t, t0, delay=max(0.6, word_t(39, 4, 1.6) - t0), hold=1.8, size=0.6,
            dx=0.0, dy=0.6)
    confetti(sc, t, 20, 11)
    return sc


# ------------------------------------------------------- 40-42: thanks, pizza, the bill
def s40(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.0, 9.0), (0.0, 2.3, 0.0), u, 0.12, fov=42, sky=INDOOR)
    es.two_rooms(sc, t)
    r = character(sc, RUDY_E, (-0.85, 0, 0.0), yaw=90, face="joy", pose=dict(ar=(90, 0), er=10, head=(0, 0, 0)))
    l = character(sc, LILY_E, (0.85, 0, 0.0), yaw=-90, face="joy", pose=dict(al=(90, 0), el=10))
    es.say(sc, r["head_top"], "THANKS!", t, 0.3, hold=1.5, size=0.38, dx=-0.3, dy=0.5)
    es.say(sc, l["head_top"], "thanks!", t, 1.0, hold=1.5, size=0.38, color=es.ECHO_B, dx=0.3, dy=0.5)
    sparks(sc, (0.0, 2.4, 0.2), t, seed=4, n=6, r=0.5)
    return sc


def s41(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.2, 7.0), (0.0, 3.0, -4.6), u, 0.1, fov=34)
    es.hall(sc, t, crowd=False)
    a = character(sc, DAD_E, (0.0, sets.STAGE_TOP, -4.8), face="jaw", pose=dict(ar=(60, 10), er=110, head=(0, -8, 0)))
    ls.megaphone(sc, T(*(a["hand_r"] + np.array([0.1, 0.1, 0.3]))) @ RX(-70))
    t0 = word_t(41, 2, 0.8)
    es.echo(sc, a["head_top"], "PIZZA!", t, t0, delay=max(0.6, word_t(41, 7, 2.0) - t0), hold=1.6, size=0.6, dx=-0.3,
            dy=0.4)
    confetti(sc, t, 20, 13)
    return sc


def s42(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.4, 8.6), (0.0, 1.8, 0.0), u, 0.1, fov=40)
    sets.town(sc)
    a = character(sc, DAD_E, (0.0, 0, 0.0), yaw=0, face="stung", pose=dict(ar=(70, 8), er=80, al=(70, -8), el=80))
    for x in (-1.1, 1.1):
        for k in range(2):
            es.pizza_box(sc, T(x, 0.16 + 0.32 * k, 1.4), 1.3)
    c = (a["hand_r"] + a["hand_l"]) / 2 + np.array([0.0, 0.15, 0.35])
    sc.box(T(*c), (0.9, 0.55, 0.06), (120, 80, 50), layer=7)
    es.say(sc, a["head_top"], "-$$", t, 0.4, hold=2.0, size=0.7, color=(120, 235, 120), dx=0.5, dy=0.5, ring=False)
    add_emote(sc, "sweat", a["head_top"], t, size=0.5, start=0.2, dx=-0.5)
    return sc


_FNS = [globals()[f"s{i:02d}"] for i in range(1, len(LINES) + 1)]
SHOTS = [(i + 1, 2.3, txt, fn) for i, (txt, fn) in enumerate(zip(LINES, _FNS))]
SHOTS, WORD_TIMES = load_timing(SHOTS, TIMING_FILE)
WT.update(WORD_TIMES)
