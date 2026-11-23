"""When Secrets Make Statues Dance: shot list. Each shot: (number, seconds, caption text, fn(t, dur) -> Scene)."""
import os

TIMING_FILE = "dancingstatues_timing.json"
SPOKEN = {"Mrs": "missus", "Mr": "mister", "hip-hop": "hip hop"}
PHONES = {"hoodie": "HH UH D IY", "gomez": "G OW M EH Z", "lee": "L IY", "lily": "L IH L IY", "karaoke": "K EH R IY OW K IY",
          "lily's": "L IH L IY Z"}

LINES = [
    "In this town, when you tell a REAL secret out loud,",
    "the nearest statue starts to DANCE.",
    "Nobody knows why. Nobody's asked the statues.",
    "Dad whispered that he hides chocolate in the flour jar.",
    "The fountain lady twirled and splashed him.",
    "Mrs Lee admitted she still sleeps with a teddy bear.",
    "The school lion did a cartwheel.",
    "Mr Gomez confessed he sings karaoke in the shower.",
    "The bandleader statue wiggled his stone hips.",
    "I'm the kid in the red hoodie. Tonight is the talent show.",
    "My plan? Juggle five balls. Perfectly.",
    "I have never juggled five balls perfectly.",
    "My rival, Lily, has the brightest sneakers in town.",
    "And the loudest bragging.",
    "I'm the BEST dancer ever, she shouted. The statues didn't move.",
    "Bragging isn't a secret. Statues can tell.",
    "Backstage, my knees turned to jelly.",
    "The mayor called my name.",
    "I threw the first ball. I dropped it.",
    "Second ball. Dropped. Third ball. Right on my foot.",
    "The crowd went quiet. A pigeon laughed.",
    "Then I remembered Dad and the flour jar.",
    "Not bragging. The real, scary kind.",
    "So I took a breath.",
    "I can't juggle! I've dropped every ball for a month!",
    "I'm terrified!",
    "Then, high on the clock tower, the stone owl flapped,",
    "and the marble horse began to boogie.",
    "Every statue in the square joined in.",
    "The crowd gasped. Then they CHEERED.",
    "But Lily stood frozen in the wings.",
    "I'm scared of the stage, she whispered. I only dance in my closet.",
    "Behind her, a little stone frog started to hip-hop.",
    "I held out my hand. Dance with me. Badly.",
    "So we did. Terribly. Together.",
    "Dad cheered with flour on his face.",
    "Mrs Lee waved her teddy bear.",
    "Mr Gomez grabbed the mic and sang.",
    "We didn't win. The judges gave the trophy to the owl.",
    "Lily whispered, Practice tomorrow? In my closet?",
    "Only if you bring the chocolate, I said.",
    "That night, the moon statue winked.",
    "Secrets are scary. Sharing them is brave.",
    "Tell a secret. Watch a statue dance.",
]
import math  # noqa: E402

import numpy as np  # noqa: E402

import dancingstatues_sets as ds  # noqa: E402
import laughs_sets as ls  # noqa: E402
import porch_sets as ps  # noqa: E402
import sets  # noqa: E402
import shoes_sets as ss  # noqa: E402
from cast import DAD, MAYOR, _spec, character, crowd_spec, sit  # noqa: E402
from engine import RX, RY, RZ, T, add_emote, clamp, lerp, speed_lines  # noqa: E402
from laughs import dcam, dfcam, head_cu, ht  # noqa: E402
from shots import confetti, sparks, walk  # noqa: E402
from story import load_timing  # noqa: E402

NARR = _spec(name="Narrator", style="tuft", s=0.98, skin=(236, 190, 150), shirt=(222, 40, 48), hoodie=True,
             accent=(250, 250, 250), pants=(46, 56, 100), shoes=(250, 250, 250), hair=(90, 60, 40), sleeve=0.9)
DAD_A = dict(DAD, apron=(250, 250, 244), name="Dad")
LEE = _spec(name="Mrs Lee", style="bob", s=1.22, skin=(240, 205, 170), shirt=(130, 176, 150), inner=(250, 244, 232),
            cardigan=True, pants=(90, 84, 110), shoes=(120, 90, 80), hair=(60, 40, 40), glasses=True,
            accent=(240, 200, 120), sleeve=0.86)
GOMEZ = _spec(name="Mr Gomez", style="short", s=1.3, torso=(1.32, 1.0, 0.6), arm=(0.64, 1.0), skin=(190, 132, 96),
              shirt=(240, 190, 50), pants=(40, 44, 70), shoes=(240, 240, 240), hair=(30, 24, 24), stache=(30, 24, 24),
              sleeve=0.4)
LILY = _spec(name="Lily", style="pigtails", s=0.99, skin=(240, 200, 164), shirt=(80, 196, 240), pants=(240, 240, 250),
             shoes=(255, 60, 190), hair=(250, 200, 90), accent=(255, 90, 160), sleeve=0.5)
WT = {}


def word_t(num, i, default=0.0):
    w = WT.get(num, [])
    return w[i][0] if i < len(w) else default


def sky_night():
    return dict(sky=((16, 22, 56), (60, 70, 120)), grade="blue", gmix=0.85)


def breathe(t, k=0.02):
    return math.sin(t * 3) * k


def glow_feet(sc, a, color, r=0.5):
    for k in ("foot_l", "foot_r"):
        ls.glow_at(sc, a[k] + np.array([0, 0.1, 0.1]), r, color, 90)


# ------------------------------------------------------- 1-9: the rule
def s01(t, dur):
    u = t / dur
    sc = dcam((-2.0, 3.0, 11.0), (-6.0, 2.0, -1.0), u, 0.1, fov=44)
    ds.square(sc, t, k=1.0)
    ds.dust(sc, t, 16, area=(-10, 2, 1, 6, -3, 2))
    character(sc, NARR, (-4.0, 0, 3.0), yaw=30, face="smirk", pose=dict(lean=18, al=(40, 10), ar=(40, 10)))
    return sc


def s02(t, dur):
    u = t / dur
    sc = dcam((3.0, 1.4, 8.4), (0.0, 3.2, 0.0), u, 0.1, fov=44)
    sets.town(sc)
    a = ds.statue(sc, ds.HERO_STATUE, 0.0, 0.0, t, 1.0, kind=1, h=0.9, face="grin")
    ls.music_notes(sc, a["head_top"] + np.array([0.6, 0.2, 0]), t)
    ls.glow_at(sc, a["head"], 1.2, (255, 236, 150), 50)
    return sc


def s03(t, dur):
    u = t / dur
    sc = dcam((0.8, 1.8, 6.6), (0.0, 1.5, 0.0), u, 0.06, fov=40)
    sets.town(sc)
    ds.statue(sc, ds.HERO_STATUE, 2.6, -1.6, t, 0.0, yaw=-25, face="neutral")
    a = character(sc, NARR, (0, 0, 0), face="neutral", pose=dict(al=(20, 40 + 10 * math.sin(t * 5)), ar=(20, 40 + 10 * math.sin(t * 5)),
                                                                el=70, er=70, head=(0, 0, 8)))
    add_emote(sc, "?", a["head_top"], t, size=0.55, dx=0.5, dy=0.2, start=0.5, hold=2.0)
    return sc


def kitchen_dad(sc, t, face="grin", pose=None, jar_open=0.0):
    sets.kitchen(sc)
    ds.flour_jar(sc, T(-0.6, 1.2, 0.0), s=1.1, open_k=jar_open)
    return character(sc, DAD_A, (0.0, 0, -2.4), yaw=0, face=face, pose=pose)


def s04(t, dur):
    u = t / dur
    pose = dict(ar=(165, -25), er=105, lean=8, head=(0, 0, 6))
    sc = dcam((1.6, 2.8, 5.4), (-0.2, 2.5, -2.0), u, 0.1, fov=42)
    a = kitchen_dad(sc, t, "smirk", pose, jar_open=clamp((t - 1.0) / 0.4))
    if t > 1.2:
        ds.choc_bar(sc, T(-0.6, 2.0 + 0.1 * math.sin(t * 4), 0.0) @ RY(20), 1.2)
    return sc


def s05(t, dur):
    u = t / dur
    sc = dcam((-2.4, 2.8, 5.6), (-7.2, 2.4, -1.0), u, 0.06, fov=46)
    sets.town(sc)
    ds.fountain(sc, t, -8.0, -1.0, 1.0)
    sc_y = t * 380
    # statue spins: re-draw handled by fountain's statue (yaw fixed), so add a second spin via arms already dancing
    a = character(sc, DAD_A, (-5.6, 0, 1.6), yaw=70, face="shock" if t > 0.7 else "smile", pose=dict(lean=-8, al=(60, 20), ar=(60, 20)))
    ss.splash(sc, (-6.3, 0.8, 1.0), t, start=0.6)
    sparks(sc, (-8.0, 3.4, -1.0), t, seed=5, n=5, r=0.8, color=(180, 220, 255))
    return sc


def s06(t, dur):
    u = t / dur
    pose = dict(al=(35, -22), ar=(35, -22), el=70, er=70, head=(0, 0, -6))
    pos = (0.0, 0, 0.0)
    sc = head_cu(LEE, pos, 0, pose, u, dist=5.0, up=-0.2, fov=40)
    sets.classroom(sc)
    a = character(sc, LEE, pos, face="worried" if t < 1.5 else "smile", pose=pose)
    ds.teddy(sc, T(*((a["hand_l"] + a["hand_r"]) / 2 + np.array([0, -0.15, 0.3]))), 0.6)
    add_emote(sc, "sweat", a["head_top"], t, size=0.45, dx=0.5, dy=0.1, start=0.3)
    return sc


def s07(t, dur):
    u = t / dur
    sc = dcam((0.8, 2.6, 6.6), (0.0, 2.0, 0.0), u, 0.0, fov=44)
    sets.school_building(sc)
    k = clamp(t / 1.6)
    ds.pedestal(sc, 0.0, 0.0, 0.7, 2.6, 1.6)
    y = 1.9 + 0.6 * math.sin(k * math.pi)
    ds.lion(sc, T(-1.6 + 3.2 * k, y, 0.0) @ RX(-360 * k), t, 1.0)
    character(sc, LEE, (2.6, 0, 1.8), yaw=-30, face="shock")
    sparks(sc, (-1.6 + 3.2 * k, y, 0.0), t, seed=2, n=4, r=0.8)
    return sc


def s08(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.8, 4.2), (0.0, 2.6, -3.0), u, 0.1, fov=42)
    ds.shower(sc, t)
    pose = dict(ar=(120, -10), er=110, al=(20, 10), head=(8 * math.sin(t * 6), 0, 0), roll=5 * math.sin(t * 6))
    a = character(sc, GOMEZ, (0.0, 0, -2.0), face="laugh", pose=pose)
    ds.mic(sc, T(*(a["hand_r"] + np.array([0, 0.2, 0.15]))), 1.2)
    ls.music_notes(sc, a["head_top"] + np.array([0.9, 0.2, 0]), t)
    ds.bubbles(sc, (0.0, 4.3, -2.2), t)
    return sc


def s09(t, dur):
    u = t / dur
    sc = dcam((-1.0, 2.4, 7.5), (0.0, 2.2, 0.0), u, 0.1, fov=44)
    sets.park(sc)
    a = ds.statue(sc, ds.BANDLEADER, 0.0, 0.0, t, 1.0, kind=1, h=0.9)
    ls.music_notes(sc, a["head_top"] + np.array([0.9, 0.2, 0]), t)
    sets.bench(sc, T(-5.0, 0, 1.0) @ RY(20))
    return sc


# ------------------------------------------------------- 10-16: the rivals
def s10(t, dur):
    u = t / dur
    sc = dfcam((0.0, 0, 1.0), ht(NARR) + 0.3, 0, u, frac=0.5, fov=42, push=0.1, elev=0.1)
    ds.stage(sc, t, crowd=False, statues=False)
    character(sc, NARR, (0.0, 0, 1.0), face="grin", pose=dict(al=(30, 25), ar=(30, 25), el=40, er=40, head=(0, 0, 4)))
    return sc


def balls_up(sc, a, t, n=5, ok=True):
    c = (a["hand_l"] + a["hand_r"]) / 2
    for i in range(n):
        ph = ((t * 1.3 + i / n) % 1.0)
        ang = i / n * 6.283 + t * 6
        p = np.array([c[0] + 0.6 * math.cos(ang), c[1] + 0.2 + 1.8 * math.sin(ph * math.pi), c[2] + 0.1])
        ds.ball(sc, p, i)


def s11(t, dur):
    u = t / dur
    pose = dict(al=(70 + 20 * math.sin(t * 12), 25), ar=(70 - 20 * math.sin(t * 12), 25), el=60, er=60)
    sc = dfcam((0.0, 0, 1.0), ht(NARR) + 0.6, 0, u, frac=0.46, fov=42, push=0.08, elev=0.1)
    ds.stage(sc, t, crowd=False, statues=False)
    a = character(sc, NARR, (0.0, 0, 1.0), face="grin", pose=pose)
    balls_up(sc, a, t)
    return sc


def s12(t, dur):
    u = t / dur
    pos = (0.0, 0, 1.0)
    sc = dfcam(pos, ht(NARR) + 0.4, 0, u, frac=0.62, fov=40, push=0.1, elev=0.2)
    ds.stage(sc, t, crowd=False, statues=False)
    a = character(sc, NARR, pos, face="worried", pose=dict(al=(30, 40), ar=(30, 40), el=50, er=50, head=(0, 0, -8)))
    for i in range(5):
        x = -1.6 + i * 0.8 + 0.2 * math.sin(t * 3 + i)
        bounce = abs(math.sin(t * 5 + i * 1.3)) * (1.2 - 0.15 * i)
        ds.ball(sc, (x, 0.22 + bounce * 0.5, 0.2 + 0.4 * (i % 2)), i)
    add_emote(sc, "sweat", a["head_top"], t, size=0.5, dx=0.5, dy=0.1, start=0.3)
    return sc


def s13(t, dur):
    u = t / dur
    sc = dcam((1.4, 0.9, 5.0), (0.0, 0.5, 0.0), u, 0.1, fov=40, blur=0)
    sets.town(sc)
    a = character(sc, LILY, (0, 0, 0), face="smug", pose=dict(ll=22 * math.sin(t * 7), lr=-22 * math.sin(t * 7)))
    glow_feet(sc, a, (255, 90, 200), 0.7)
    sparks(sc, a["foot_r"] + np.array([0, 0.2, 0]), t, seed=3, n=5, r=0.5, color=(255, 120, 220))
    return sc


def s14(t, dur):
    u = t / dur
    pos = (0.0, 0, 0.0)
    pose = dict(ar=(120, -10), er=100, al=(20, 10), lean=-6)
    sc = head_cu(LILY, pos, 0, pose, u, dist=3.6, up=0.15, fov=36)
    sets.town(sc)
    a = character(sc, LILY, pos, face="smug", pose=pose)
    ls.megaphone(sc, T(*(a["head"] + np.array([0.35, -0.35, 0.3]))) @ RY(30))
    return sc


def s15(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.2, 8.8), (0.0, 1.7, 0.0), u, 0.06, fov=44)
    sets.town(sc)
    ds.statue(sc, ds.HERO_STATUE, 3.4, -1.4, t, 0.0, yaw=-20, face="suspicious")
    ds.statue(sc, ds.FOUNTAIN_LADY, -3.4, -1.4, t, 0.0, yaw=20, face="neutral")
    w = math.sin(t * 9)
    a = character(sc, LILY, (0, 0, 1.4), face="grin", pose=dict(al=(150 + 30 * w, 10), ar=(150 - 30 * w, 10), roll=8 * w,
                                                                 y=0.1 * abs(w), ll=14 * w, lr=-14 * w))
    ls.sticker(sc, a["head"], "BEST!", t, start=0.2, hold=2.0, size=0.6, dx=0.9, dy=1.0)
    return sc


def s16(t, dur):
    u = t / dur
    h = 0.9 + 0.12
    sc = dcam((2.6, 3.6, 8.2), (0.0, 3.1, 0.0), u, 0.12, fov=36)
    sets.town(sc)
    a = ds.statue(sc, ds.HERO_STATUE, 0.0, 0.0, t, 0.0, yaw=-8, face="suspicious" if t < 1.4 else "smug")
    add_emote(sc, "?", a["head_top"], t, size=0.5, dx=0.6, dy=0.2, start=0.6, hold=2.0)
    return sc


# ------------------------------------------------------- 17-26: the show
def backstage(sc, t=0.0):
    sc.ground((120, 86, 56))
    sc.box(T(0, 3.5, -4.0), (14, 7, 0.3), (60, 30, 40), layer=1)
    for i in range(-6, 7):
        sc.box(T(i * 1.2, 3.5, -3.8), (0.5, 7, 0.1), (150 - 8 * (i % 2), 30, 44), layer=2)
    sc.box(T(6.0, 3.5, -3.0), (3.0, 7, 0.3), (130, 24, 40), layer=2)
    sc.box(T(-6.0, 3.5, -3.0), (3.0, 7, 0.3), (130, 24, 40), layer=2)
    ls.glow_at(sc, (0.0, 3.0, -3.4), 5.0, (255, 214, 140), 40 + 20 * math.sin(t * 7))


def s17(t, dur):
    u = t / dur
    w = math.sin(t * 22)
    pose = dict(kl=14 + 12 * w, kr=14 - 12 * w, al=(10, 12), ar=(10, 12), head=(0, -10, 0), lean=4)
    sc = dfcam((0.0, 0, -1.0), ht(NARR) + 0.2, 0, u, frac=0.7, fov=40, push=0.1, elev=-0.3)
    backstage(sc, t)
    a = character(sc, NARR, (0.0, 0, -1.0), face="worried", pose=pose)
    add_emote(sc, "sweat", a["head_top"], t, size=0.5, dx=0.5, dy=0.1, start=0.2)
    return sc


def s18(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.2, 7.4), (0.0, 3.0, -5.0), u, 0.08, fov=30)
    ds.stage(sc, t, crowd=False, statues=False)
    a = character(sc, MAYOR, (0.0, sets.STAGE_TOP, -5.0), face="grin", pose=dict(ar=(100, -10), er=70))
    ds.mic(sc, T(*(a["hand_r"] + np.array([0, 0.25, 0.2]))), 1.3)
    ls.sticker(sc, a["head"], "NEXT!", t, start=0.3, hold=1.6, size=0.6, dx=1.2, dy=0.8)
    return sc


def stage_cam(u, push=0.08):
    return dcam((0.0, 3.0, 7.4), (0.0, 1.9, -4.6), u, push, fov=34)


def s19(t, dur):
    u = t / dur
    sc = stage_cam(u)
    ds.stage(sc, t, crowd=False, statues=False)
    pos = (0.0, sets.STAGE_TOP, -4.5)
    k = clamp((t - 0.2) / 0.5)
    a = character(sc, NARR, pos, face="grit" if t < 1.0 else "shock", pose=dict(ar=(60 + 110 * (1 - k) ** 2, 10), al=(30, 12)))
    if t < 0.9:
        ds.ball(sc, (0.4, 1.9 + 2.5 * math.sin(clamp(t / 0.9) * math.pi), -4.2), 0)
    else:
        ds.ball(sc, (0.4, sets.STAGE_TOP + 0.22 + abs(math.sin((t - 0.9) * 8)) * 0.7 * math.exp(-(t - 0.9) * 2), -4.2 + (t - 0.9) * 0.6), 0)
    ls.sticker(sc, a["head"], "OOPS", t, start=1.1, hold=1.3, size=0.6, dx=1.2, dy=0.8)
    return sc


def s20(t, dur):
    u = t / dur
    sc = stage_cam(u)
    ds.stage(sc, t, crowd=False, statues=False)
    pos = (0.0, sets.STAGE_TOP, -4.5)
    a = character(sc, NARR, pos, face="stung" if t > 1.4 else "worried",
                  pose=dict(ar=(40, 14), al=(40, 14), ll=0 if t < 1.4 else -40, el=30, er=30))
    ds.ball(sc, (-0.7, sets.STAGE_TOP + 0.22 + abs(math.sin(t * 6)) * 0.6 * math.exp(-t), -4.0), 1)
    if t < 1.4:
        ds.ball(sc, (0.25, 4.4 - 4.0 * clamp((t - 0.5) / 0.9), -4.4), 2)
    else:
        ds.ball(sc, (0.3, sets.STAGE_TOP + 0.22, -4.3), 2)
    add_emote(sc, "stars", a["head_top"], t, size=0.5, dx=0.5, dy=0.1, start=1.5, hold=1.0)
    return sc


def s21(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.3, -6.2), (0.0, 1.5, 2.0), u, 0.08, fov=46)
    sets.stage(sc) if False else None
    sc.ground((214, 204, 186))
    sets.audience(sc, t, frozen=True, faces=("neutral", "worried"), rows=3, per_row=7, seed=2)
    sc.box(T(0, sets.STAGE_TOP / 2, -6.0), (13, sets.STAGE_TOP, 5.2), (170, 130, 90), layer=2)
    sets.pigeon(sc, (0.9, sets.STAGE_TOP + 0.1, -4.3), yaw=180, bob=math.sin(t * 14) * 0.1, s=1.4)
    ls.sticker(sc, (0.9, sets.STAGE_TOP + 1.3, -4.3), "HA HA", t, start=0.9, hold=1.6, size=0.5, dx=0.6, dy=0.5)
    return sc


def s22(t, dur):
    u = t / dur
    sc = dcam((1.4, 2.8, 4.6), (-0.2, 2.6, -2.2), u, 0.1, fov=42)
    a = kitchen_dad(sc, t, "smirk", dict(ar=(165, -25), er=105), jar_open=1.0)
    ds.choc_bar(sc, T(-0.6, 2.2, 0.0) @ RY(20), 1.2)
    ls.glow_at(sc, a["head"], 2.0, (255, 236, 170), 60)
    sparks(sc, a["head_top"], t, seed=1, n=6, r=1.0)
    return sc


def s23(t, dur):
    u = t / dur
    pose = dict(al=(30, 22), ar=(30, 22), el=70, er=70, lean=6)
    sc = head_cu(NARR, (0, 0, 0), 0, pose, u, dist=3.0, up=0.1, fov=34, push=0.14)
    sc.ground((120, 86, 56))
    backstage(sc, t)
    a = character(sc, NARR, (0, 0, 0), face="grit", pose=pose)
    add_emote(sc, "!", a["head_top"], t, size=0.6, dx=0.5, dy=0.2, start=0.4)
    return sc


def s24(t, dur):
    u = t / dur
    k = clamp(t / 1.0)
    pos = (0.0, sets.STAGE_TOP, -4.5)
    sc = dcam((0.0, 2.8, 7.2), (0.0, 2.0, -4.6), u, 0.14, fov=30)
    ds.stage(sc, t, crowd=False, statues=False)
    character(sc, NARR, pos, face="grit", pose=dict(lean=-10 * k, al=(20 + 20 * k, 30), ar=(20 + 20 * k, 30), head=(0, 10, 0)))
    return sc


def s25(t, dur):
    u = t / dur
    pos = (0.0, sets.STAGE_TOP, -4.5)
    sc = dcam((0.0, 2.8, 7.2), (0.0, 2.7, -4.6), u, 0.12, fov=28)
    ds.stage(sc, t, crowd=False, statues=False)
    a = character(sc, NARR, pos, face="jaw", pose=dict(al=(150, 40), ar=(150, 40), lean=-6, head=(0, 8, 0)))
    ls.sticker(sc, a["head"], "I CAN'T JUGGLE!", t, start=0.3, hold=2.4, size=0.36, dx=0.0, dy=0.9)
    return sc


def s26(t, dur):
    u = t / dur
    pos = (0.0, sets.STAGE_TOP, -4.5)
    pose = dict(al=(20, 10), ar=(20, 10), el=60, er=60, head=(0, 0, 8))
    sc = head_cu(NARR, pos, 0, pose, u, dist=2.4, up=0.1, fov=34, push=0.15)
    ds.stage(sc, t, crowd=False, statues=False)
    a = character(sc, NARR, pos, face="stung", pose=pose)
    ls.sticker(sc, a["head"], "TERRIFIED", t, start=0.2, hold=1.6, size=0.4, dx=1.0, dy=0.8, rot=6)
    return sc


# ------------------------------------------------------- 27-30: the dance
def s27(t, dur):
    u = t / dur
    sc = dcam((8.0, 6.0, 4.0), (12.0, 11.0, -5.0), u, 0.1, fov=44)
    ds.square(sc, t, 0.0, owl_flap=clamp(t / 0.4))
    sparks(sc, (12.0, 12.5, -5.0), t, seed=2, n=6, r=1.2)
    character(sc, NARR, (6.4, 0, 3.0), yaw=160, face="shock")
    return sc


def s28(t, dur):
    u = t / dur
    sc = dcam((-4.0, 1.4, 7.4), (0.0, 1.8, 0.0), u, 0.1, fov=44)
    sets.town(sc)
    k = 1.0
    ds.horse(sc, T(-0.6, 1.4, 0.4) @ RY(10 * math.sin(t * 5)), t, k)
    sparks(sc, (-0.6, 3.2, 0.4), t, seed=7, n=6, r=1.0)
    ls.music_notes(sc, (0.6, 3.0, 0.4), t)
    return sc


def s29(t, dur):
    u = t / dur
    sc = dcam((0.0, 5.6, 13.0), (0.0, 1.8, -1.0), u, 0.0, fov=46)
    ds.square(sc, t, 1.0, owl_flap=1.0)
    for i, (x, z) in enumerate(((-3.0, 0.8), (0.0, 1.4), (3.0, 0.8))):
        ds.statue(sc, (ds.HERO_STATUE, ds.BANDLEADER, ds.MOON_STATUE)[i], x, z, t, 1.0, kind=i + 1)
    ds.lion(sc, T(6.4, 1.1, 1.8) @ RY(-30), t, 1.0)
    ds.horse(sc, T(-5.6, 1.4, 2.4) @ RY(30), t, 1.0)
    ds.dust(sc, t, 40, area=(-10, 10, 1, 8, -3, 6))
    return sc


def s30(t, dur):
    u = t / dur
    sc = dcam((0.0, 4.0, -3.4), (0.0, 1.4, 4.6), u, 0.06, fov=56)
    sc.ground((214, 204, 186))
    sets.audience(sc, t, standing=True, faces=("joy", "laugh", "grin"), rows=3, per_row=7, seed=2)
    return sc


# ------------------------------------------------------- 31-35: Lily
LILY_P = (3.0, 0.0, -2.2)


def s31(t, dur):
    u = t / dur
    sc = dfcam(LILY_P, ht(LILY) + 0.3, 0, u, frac=0.6, fov=42, push=0.08, elev=0.2)
    backstage(sc, t)
    character(sc, LILY, LILY_P, face="worried", pose=dict(al=(8, 8), ar=(8, 8), kl=6 * math.sin(t * 20), kr=-6 * math.sin(t * 20)))
    return sc


def s32(t, dur):
    u = t / dur
    pose = dict(al=(60, -15), ar=(60, -15), el=100, er=100, head=(0, 10, 6))
    sc = head_cu(LILY, LILY_P, 0, pose, u, dist=2.8, up=0.1, fov=34, push=0.14)
    backstage(sc, t)
    a = character(sc, LILY, LILY_P, face="sad", pose=pose)
    add_emote(sc, "sweat", a["head_top"], t, size=0.45, dx=0.5, dy=0.1, start=0.4)
    return sc


def s33(t, dur):
    u = t / dur
    sc = dcam((1.0, 1.6, 4.4), (LILY_P[0] - 0.4, 1.0, LILY_P[2]), u, 0.08, fov=42)
    backstage(sc, t)
    character(sc, LILY, (LILY_P[0] + 0.8, 0, LILY_P[2] + 0.8), yaw=-20, face="shock")
    hop = abs(math.sin(t * 8))
    ds.frog(sc, T(LILY_P[0] - 1.2, 0.2 + 0.5 * hop, LILY_P[2] + 0.8) @ RY(40), hop)
    ls.music_notes(sc, (LILY_P[0] - 1.2, 1.2, LILY_P[2] + 0.8), t)
    return sc


def two_shot(sc, t, nf="grin", lf="grin", dancing=0.0, hand=False):
    w = math.sin(t * 9)
    np_ = dict(al=(90 if hand else 150 * dancing + 20, 5), ar=(150 * dancing + 20, 5), y=0.1 * abs(w) * dancing, roll=8 * w * dancing)
    lp_ = dict(al=(150 * dancing + 20, 5), ar=(150 * dancing + 20, 5), y=0.1 * abs(w + 1) * dancing, roll=-8 * w * dancing)
    if hand:
        np_ = dict(ar=(110, 0), er=20, al=(10, 6))
    n = character(sc, NARR, (-0.9, 0, 0), yaw=25, face=nf, pose=np_)
    l = character(sc, LILY, (0.9, 0, 0), yaw=-25, face=lf, pose=lp_)
    return n, l


def s34(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.2, 7.6), (0.0, 1.5, 0.0), u, 0.1, fov=38)
    backstage(sc, t)
    two_shot(sc, t, "smile", "worried", hand=True)
    sparks(sc, (0.0, 1.8, 0.2), t, seed=3, n=3, r=0.4)
    return sc


def s35(t, dur):
    u = t / dur
    sc = dcam((0.0, 5.2, 9.4), (0.0, 1.5, -3.0), u, 0.1, fov=40)
    ds.stage(sc, t, crowd=True, standing=True, statues_k=1.0, statues=True)
    w = math.sin(t * 9)
    for i, (x, spec, kd) in enumerate(((-0.9, NARR, 0), (0.9, LILY, 1))):
        character(sc, spec, (x, sets.STAGE_TOP, -3.6), yaw=0, face="laugh",
                  pose=dance_pose_kid(t, kd))
    confetti(sc, t, n=50)
    return sc


def dance_pose_kid(t, kd):
    w = math.sin(t * 9 + kd * 1.7)
    v = math.sin(t * 9 + kd * 1.7 + 1.6)
    return dict(al=(120 + 50 * w, 10), ar=(120 - 50 * w, 10), ll=16 * v, lr=-16 * v, roll=8 * w, y=0.1 * abs(v))


# ------------------------------------------------------- 36-39: the cheer
def s36(t, dur):
    u = t / dur
    pose = dict(al=(160 + 20 * math.sin(t * 10), 10), ar=(160 - 20 * math.sin(t * 10), 10), y=0.08 * abs(math.sin(t * 10)))
    sc = dfcam((0, 0, 1.0), ht(DAD) + 0.3, 0, u, frac=0.5, fov=42, push=0.08, elev=0.1)
    sets.town(sc)
    a = character(sc, DAD_A, (0, 0, 1.0), face="laugh", pose=pose)
    sc.blob(T(*(a["head"] + np.array([0.28, -0.05, 0.38]))), (0.2, 0.12, 0.05), (252, 252, 248), layer=7, n=8, m=5, lit=False)
    sc.blob(T(*(a["head"] + np.array([-0.2, 0.2, 0.36]))), (0.14, 0.09, 0.05), (252, 252, 248), layer=7, n=8, m=5, lit=False)
    ds.statue(sc, ds.HERO_STATUE, 3.4, -1.2, t, 1.0, kind=1)
    return sc


def s37(t, dur):
    u = t / dur
    pose = dict(ar=(150 + 25 * math.sin(t * 9), 10), al=(40, 6), lean=-3)
    sc = dfcam((0, 0, 1.0), ht(LEE) + 0.3, 0, u, frac=0.5, fov=42, push=0.08, elev=0.1)
    sets.town(sc)
    a = character(sc, LEE, (0, 0, 1.0), face="laugh", pose=pose)
    ds.teddy(sc, T(*(a["hand_r"] + np.array([0, 0.05, 0.1]))), 0.7)
    ds.statue(sc, ds.FOUNTAIN_LADY, -3.4, -1.2, t, 1.0, kind=2)
    return sc


def s38(t, dur):
    u = t / dur
    pos = (0.0, sets.STAGE_TOP, -4.2)
    pose = dict(ar=(125, -10), er=105, al=(20, 10), roll=4 * math.sin(t * 6))
    sc = dcam((0.0, 5.0, 9.0), (0.0, 2.2, -4.2), u, 0.08, fov=34)
    ds.stage(sc, t, crowd=True, standing=True, statues_k=1.0)
    a = character(sc, GOMEZ, pos, face="laugh", pose=pose)
    ds.mic(sc, T(*(a["hand_r"] + np.array([0, 0.2, 0.15]))), 1.2)
    ls.music_notes(sc, a["head_top"] + np.array([0.9, 0.3, 0]), t)
    return sc


def s39(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.6, 7.2), (0.0, 1.9, -4.0), u, 0.05, fov=44)
    ds.stage(sc, t, crowd=False, statues=False)
    ds.pedestal(sc, 0.0, -4.4, sets.STAGE_TOP + 0.05, 1.8, 1.4)
    ds.owl(sc, T(0.0, sets.STAGE_TOP + 0.65, -4.4), t, 0.0)
    sets.trophy(sc, T(1.8, sets.STAGE_TOP, -3.6), 0.8)
    character(sc, MAYOR, (-1.8, sets.STAGE_TOP, -3.6), yaw=20, face="grin", pose=dict(ar=(120, -10)))
    character(sc, NARR, (-3.4, sets.STAGE_TOP, -3.2), yaw=30, face="neutral")
    character(sc, LILY, (-4.5, sets.STAGE_TOP, -3.2), yaw=40, face="neutral")
    sparks(sc, (1.8, sets.STAGE_TOP + 2.2, -3.6), t, seed=4, n=5, r=0.6)
    return sc


# ------------------------------------------------------- 40-44: the ending
SUNSET = dict(sky=((250, 160, 120), (255, 214, 170)), night=0.0)


def s40(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.0, 7.6), (0.0, 1.5, 0.0), u, 0.1, fov=38, **SUNSET)
    sets.town(sc)
    two_shot(sc, t, "smile", "smile")
    return sc


def s41(t, dur):
    u = t / dur
    pos = (0, 0, 0)
    pose = dict(ar=(40, 20), er=70)
    sc = head_cu(NARR, pos, 0, pose, u, dist=3.0, up=0.1, fov=34, push=0.12, **SUNSET)
    sets.town(sc)
    a = character(sc, NARR, pos, face="smirk", pose=pose)
    ds.choc_bar(sc, T(*(a["hand_r"] + np.array([0.0, 0.18, 0.1]))) @ RX(-30), 0.9)
    return sc


def s42(t, dur):
    u = t / dur
    sc = dcam((2.4, 3.6, 9.0), (0.0, 3.4, 0.0), u, 0.14, fov=40, **sky_night())
    sc.ground((70, 90, 110))
    ds.pedestal(sc, 0.0, 0.0, 0.9)
    a = character(sc, ds.MOON_STATUE, (0.0, 1.02, 0.0), face="wink" if t > 0.9 else "smile", pose=dict(ar=(120, 0), er=60, al=(8, 5)),
                  shadow=False)
    ds.moon(sc, T(*(a["hand_r"] + np.array([0.0, 0.7, 0.2]))))
    ls.glow_at(sc, a["hand_r"] + np.array([0.0, 0.7, 0.2]), 2.2, (255, 244, 190), 70)
    if t > 0.9:
        sparks(sc, a["head"] + np.array([0.4, 0.1, 0.4]), t, seed=3, n=4, r=0.4)
    return sc


def s43(t, dur):
    u = t / dur
    sc = dcam((0.0, 3.4, 12.0), (0.0, 1.6, 0.0), u, 0.1, fov=44, **sky_night())
    sets.town(sc)
    ds.fountain(sc, t, -6.0, -1.0, 0.0)
    character(sc, NARR, (-0.8, 0, 2.0), yaw=20, face="smile", pose=sit())
    character(sc, LILY, (0.8, 0, 2.0), yaw=-20, face="smile", pose=sit())
    ds.statue(sc, ds.HERO_STATUE, 4.5, -1.0, t, 0.0, yaw=-30, face="sleep")
    ds.dust(sc, t, 24, area=(-6, 6, 0, 6, 0, 4))
    return sc


def s44(t, dur):
    u = t / dur
    k = clamp((t - 0.7) / 0.3)
    sc = dcam((1.8, 3.4, 10.5), (0.0, 3.0, 0.0), u, 0.08, fov=42)
    sets.town(sc)
    ds.statue(sc, ds.HERO_STATUE, 0.0, 0.0, t, k, kind=1, face="grin")
    character(sc, NARR, (-2.6, 0, 2.4), yaw=30, face="smirk",
              pose=dict(ar=(165, -25), er=105, lean=8) if t < 0.8 else dict(ar=(20, 10), al=(20, 10)))
    if k > 0:
        ds.dust(sc, t, 20, area=(-4, 4, 1, 6, -2, 2))
    return sc


_FNS = [globals()[f"s{i:02d}"] for i in range(1, len(LINES) + 1)]
SHOTS = [(i + 1, 1.4, txt, fn) for i, (txt, fn) in enumerate(zip(LINES, _FNS))]
SHOTS, WORD_TIMES = load_timing(SHOTS, TIMING_FILE)
WT.update(WORD_TIMES)
