"""The Porch Light: shot list. Each shot: (number, seconds, caption text, fn(t, dur) -> Scene)."""
import os

TIMING_FILE = "porch_timing.json"
SPOKEN = {"30": "thirty", "9": "nine", "8:59": "eight fifty nine", "Mr": "mister", "Mrs": "missus",
          "neighbours": "neighbors", "windowsill": "window sill"}
PHONES = {"abernathy": "AE B ER N AE TH IY", "abernathy's": "AE B ER N AE TH IY Z", "ortiz": "AO R T IY Z",
          "nova": "N OW V AH", "crummy": "K R AH M IY"}

LINES = [
    "In this town,",
    "every house has a porch light",
    "that glows when someone inside is HAPPY.",
    "Birthday?",
    "Your whole house lights up like a fireworks show.",
    "Bad day?",
    "Your light flickers.",
    "Everyone on the street knows.",
    "Our street is the brightest in town.",
    "Except for ONE house.",
    "Mr Abernathy's.",
    "At the very end.",
    "Dark for 30 YEARS.",
    "Kids say he's a grump.",
    "They cross the street to avoid him.",
    "I'm Nova.",
    "And I decided to fix his light.",
    "I left cookies on his step.",
    "Dark.",
    "I played trumpet under his window.",
    "Still dark.",
    "Also, he closed the window.",
    "I planted sunflowers in his yard.",
    "NOTHING.",
    "Meanwhile, something weird kept happening at MY house.",
    "Every night at 9 o'clock,",
    "a paper airplane landed on my windowsill.",
    "Each one had a joke written inside.",
    "Why did the cookie go to the doctor?",
    "It felt CRUMMY.",
    "My light glowed so bright",
    "the neighbours had to wear sunglasses.",
    "Then I noticed my friend Leo got paper airplanes too.",
    "And Mrs Ortiz.",
    "And the mailman.",
    "Every bright house on the street.",
    "Paper airplanes.",
    "So one night, at 8:59,",
    "I hid in the bushes.",
    "A window opened.",
    "At the end of the street.",
    "Mr Abernathy.",
    "Folding a paper airplane.",
    "Throwing it as far as he could.",
    "He wasn't a grump.",
    "For 30 years, he'd been making EVERYONE happy.",
    "And nobody ever made him happy back.",
    "So the next night, I folded my own airplane.",
    "Inside, I wrote:",
    "Thank you. From the whole street.",
    "I threw it.",
    "It landed right on his windowsill.",
    "He opened it.",
    "He read it twice.",
    "Then, for the first time in 30 years,",
    "his light turned ON.",
    "Now it's the BRIGHTEST.",
]

import math  # noqa: E402

import numpy as np  # noqa: E402

import porch_sets as ps  # noqa: E402
import sets  # noqa: E402
from cast import (ABERNATHY, BRAX, DAD, HERO, MAILMAN, ORTIZ, PIP, TUCK, character, crowd_spec)  # noqa: E402
from engine import RX, RY, RZ, T, add_emote, clamp, glow, lerp, speed_lines, xf  # noqa: E402
from shots import cam, key, sparks, walk  # noqa: E402
from story import load_timing  # noqa: E402

NOVA, LEO = HERO, TUCK
AX, AZ = ps.ABER_X, ps.ABER_Z
AFRONT = AX - ps.HOUSE_D / 2          # x of the front wall of Mr Abernathy's house (it faces -x)
NOVA_I, LEO_I, DAD_I, PARTY_I, GLOW_I = 4, 2, 1, 5, 3
ORTIZ_S = 3
NIGHT = dict(sky=ps.NIGHT_SKY, night=1.0)
DUSK = dict(sky=ps.DUSK_SKY, night=0.62)
GREY = (126, 122, 132)
PINK = sets.HOUSE_COLORS[NOVA_I % 6]
FILL = (196, 210, 255)


# ------------------------------------------------------------------ helpers
def ncam(pos, tgt, u, push=0.1, fov=38, w=None, fill=0.0, bloom=1.0, mood=NIGHT, **kw):
    """Night camera: slow push-in and bloom round lamps (the backend's moon keys from behind the camera).
    fill adds a soft point light near the camera for tight close-ups."""
    args = dict(mood)
    args.update(kw)
    sc = cam(pos, tgt, u, push, fov, w, **args)
    sc.bloom = bloom
    if fill > 0:
        d = float(np.linalg.norm(sc.cam - np.asarray(tgt, float)))
        sc.light(sc.cam + sc.u * 1.2 + sc.r * 0.9, FILL, 16 * fill * d * d, 1.5)
    return sc


def fcam(center, height, az, u, frac=0.5, top=0.14, fov=40, elev=0.4, side=0.0, push=0.1, **kw):
    """Frame a subject: `center` = (x, base y, z) of its feet, `height` tall, filling `frac` of the frame height
    with its top `top` down from the frame top. The camera sits at compass angle `az` (degrees) round the
    subject (0 = on its +z side), `elev` above eye line; `side` shifts the subject left/right (+ = left)."""
    c = np.asarray(center, float)
    k = 0.5 / math.tan(math.radians(fov) / 2)
    depth = height * k / frac
    dv = np.array([math.sin(math.radians(az)), 0.0, math.cos(math.radians(az))])
    right = -np.array([dv[2], 0.0, -dv[0]])
    y_top = c[1] + height
    ty = y_top - (0.38 - top) * depth / k
    tgt = np.array([c[0], ty, c[2]]) + right * side
    pos = tgt + dv * depth + np.array([0, elev, 0])
    return ncam(pos, tgt, u, push, fov, **kw)


def street(sc, **kw):
    ps.night_sky(sc)
    return ps.street(sc, **kw)


def win_pos(spec, win_y, x=0.0, z=-0.75):
    """Where to stand a character behind a facade window so their face sits in it."""
    s = spec["s"]
    return (x, win_y + 0.08 - (spec["leg"][1] + spec["torso"][1]) * s - spec["head"][1] * s / 2, z)


def aber_facade(sc, open_k=1.0, room_k=0.25, lamp_k=0.0, lamp_watts=None):
    sc.ground((60, 104, 62))
    ps.night_sky(sc)
    return ps.facade(sc, GREY, open_k=open_k, room_k=room_k, old=True, lamp_k=lamp_k, shelf=True,
                     curtains=(90, 84, 90), lamp_watts=lamp_watts)


def nova_facade(sc, open_k=1.0, room_k=1.0):
    sc.ground((60, 104, 62))
    ps.night_sky(sc)
    return ps.facade(sc, PINK, open_k=open_k, room_k=room_k, lamp_k=0.9, win_y=2.4, curtains=(150, 70, 70))


def hold_pose(fold=0.0):
    """Both hands together in front of the chest (holding a note or a plane)."""
    return dict(al=(62, -16), ar=(62, -16), el=48 + fold, er=48 + fold)


def between_hands(a, fwd, up=0.12, out=0.12):
    return (a["hand_l"] + a["hand_r"]) / 2 + np.array([0, up, 0]) + fwd * out


def fwd_of(yaw):
    return np.array([math.sin(math.radians(yaw)), 0.0, math.cos(math.radians(yaw))])


def plane_at(sc, p, vel, s=0.5, bank=0.0, live=True):
    v = np.asarray(vel, float)
    yaw = math.degrees(math.atan2(v[0], v[2]))
    pitch = -math.degrees(math.atan2(v[1], math.hypot(v[0], v[2]) + 1e-6))
    ps.paper_plane(sc, T(*p) @ RY(yaw) @ RX(pitch) @ RZ(bank), s=s, live=live)


def fly(sc, t, t0, t1, p0, p1, arc=0.8, s=0.5, bank=10.0, land=True):
    """Plane gliding p0 -> p1 between t0 and t1 (eases into the landing); parked at p1 afterwards."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    if t < t0:
        return None
    k = clamp((t - t0) / (t1 - t0))
    if k >= 1 and not land:
        return None
    e = 1 - (1 - k) ** 2
    p = p0 + (p1 - p0) * e + np.array([0, arc * 4 * e * (1 - e), 0])
    d = p1 - p0
    dy = arc * 4 * (1 - 2 * e)
    vel = np.array([d[0], d[1] + dy if k < 1 else 0.0, d[2]])
    wob = math.sin(t * 9) * bank * (1 - k)
    plane_at(sc, p + (np.array([0, 0.03 * math.sin(t * 20), 0]) if k >= 1 and t - t1 < 0.25 else 0), vel, s, wob)
    return p


def flicker(t, lo=0.08, hi=0.6, seed=1.0):
    v = math.sin(t * 37 * seed) + math.sin(t * 23.3 + seed) + 0.6 * math.sin(t * 71)
    return hi if v > 0.2 else lo


def fade_out(sc, t, dur, k=0.45):
    if t > dur - k:
        sc.fade = clamp((t - (dur - k)) / k)


# ----------------------------------------------------------- 1-15: the street
def p01(t, dur):
    u = t / dur
    sc = ncam((-30, 13, 5.7), (22, 1.0, 5.7), u, 0.12, fov=48, fill=0, bloom=1.2)
    street(sc)
    return sc


def p02(t, dur):
    u = t / dur
    sc = ncam((-8, 2.0, 10.5), (6.5, 2.4, -4.0), u, 0.12, fov=50, fill=0, bloom=1.2)
    lights = {("n", i): clamp(t * 4.5 - (i - 1) * 0.55) * 0.85 + 0.1 for i in range(8)}
    street(sc, lights=lights)
    return sc


def p03(t, dur):
    u = t / dur
    x = ps.NORTH_X[2]
    k = 0.2 + 0.8 * clamp((t - 0.45) / 0.35)
    sc = ncam((x + 0.9, 2.3, -0.9), (x + 0.3, 2.0, -5.1), u, 0.1, fov=40, w=3.4, bloom=1.3)
    street(sc, lights={("n", 2): k}, south=False)
    a = character(sc, crowd_spec(3, adult=True), (x - 0.35, 0.3, -5.0), yaw=10, face="laugh" if k > 0.6 else "smile",
                  pose=dict(al=(20, 30), ar=(150 if k > 0.6 else 20, -20), head=(0, 6 * (k > 0.6), 0)))
    add_emote(sc, "stars", a["head_top"], t, size=0.5, dx=0.6, dy=0.2, start=0.75)
    return sc


def p04(t, dur):
    u = t / dur
    x = ps.NORTH_X[PARTY_I]
    sc = ncam((x + 0.2, 1.6, -1.6), (x, 1.45, -5.0), u, 0.1, fov=36, w=2.4, bloom=1.3)
    street(sc, lights={("n", PARTY_I): 1.0}, party={("n", PARTY_I): 1.0}, south=False)
    a = character(sc, crowd_spec(5), (x, 0.3, -5.0), face="joy", pose=dict(al=(160, -20), ar=(160, -20)))
    ps.party_hat(sc, a["Mh"] @ T(0, crowd_spec(5)["head"][1] * 0.95 / 2 + 0.02, 0) @ RZ(-12))
    add_emote(sc, "?", a["head_top"], t, size=0.5, dx=0.75, dy=0.35, start=0.05)
    from shots import confetti
    confetti(sc, t, n=50)
    return sc


def p05(t, dur):
    u = t / dur
    x = ps.NORTH_X[PARTY_I]
    sc = ncam((x + 1.2, 2.0, 7.0), (x, 4.2, -6.0), u, 0.1, fov=50, bloom=1.2)
    street(sc, lights={("n", PARTY_I): 1.0}, party={("n", PARTY_I): 1.0}, watts={("n", PARTY_I): 140})
    cols = [(255, 90, 140), (90, 210, 255), (255, 220, 80), (160, 240, 120), (220, 130, 255)]
    for j, (dx, y, t0) in enumerate(((-2.5, 8.5, 0.05), (2.0, 9.6, 0.4), (0.2, 11.0, 0.75), (-3.2, 10.4, 1.1),
                                      (3.0, 8.2, 1.35))):
        ps.firework(sc, (x + dx, y, -9.0), t - t0, cols[j % 5], r=1.8, seed=j)
    return sc


def p06(t, dur):
    u = t / dur
    x = ps.NORTH_X[DAD_I]
    sc = ncam((x + 0.5, 3.4, -1.6), (x, 3.0, -5.0), u, 0.08, fov=34, w=2.4, bloom=1.0)
    street(sc, lights={("n", DAD_I): flicker(t, 0.1, 0.45)}, south=False)
    a = character(sc, DAD, (x, 0.3, -5.0), face="miserable", pose=dict(lean=8, al=(4, 2), ar=(4, 2), head=(0, -10, 0)))
    add_emote(sc, "sweat", a["head_top"], t, size=0.5, dx=0.6, dy=0.1, start=0.1)
    return sc


def p07(t, dur):
    u = t / dur
    x = ps.NORTH_X[DAD_I]
    lamp = np.array([x + 0.82, 1.82, -5.48])
    sc = ncam(lamp + np.array([-0.6, 0.1, 2.4]), lamp + np.array([-0.35, -0.1, 0]), u, 0.12, fov=34, bloom=1.4)
    street(sc, lights={("n", DAD_I): flicker(t, 0.06, 0.55)}, south=False)
    character(sc, DAD, (x - 1.0, 0.3, -5.3), yaw=25, face="miserable", pose=dict(lean=8, head=(0, -12, 0)))
    return sc


def p08(t, dur):
    u = t / dur
    sc = ncam((-19.0, 2.3, -0.5), (-15.5, 2.2, 12.8), u, 0.12, fov=40, fill=0.5, bloom=1.2)
    street(sc, lights={("n", DAD_I): flicker(t, 0.1, 0.5)})
    sc.light((-19.0, 3.0, -4.0), (255, 200, 130), 160 * flicker(t, 0.1, 0.9), 0.5)
    for j, (i, face, emo, st) in enumerate(((0, "shock", "!", 0.1), (1, "worried", "?", 0.3), (2, "shock", "!", 0.5))):
        xx = ps.SOUTH_X[i]
        turn = clamp((t - st + 0.15) / 0.2)
        a = character(sc, crowd_spec(j + 2, adult=True), (xx + 0.6, 0.3, 12.85), yaw=180 + 25 * turn, face=face,
                      pose=dict(head=(30 * turn, 0, 0)))
        add_emote(sc, emo, a["head_top"], t, size=0.6, dx=0.5, dy=0.25, start=st)
    return sc


def p09(t, dur):
    u = t / dur
    sc = ncam((-42, 22, 5.7), (18, 0.0, 5.7), u, 0.18, fov=50, fill=0, bloom=1.3)
    street(sc, lights={k: 1.0 for k in [("n", i) for i in range(8)] + [("s", i) for i in range(7)]})
    return sc


def p10(t, dur):
    u = t / dur
    sc = ncam((4.0, 2.1, 5.7), (AX, 2.4, AZ), u, 0.3, fov=34, fill=0, bloom=1.2)
    street(sc)
    return sc


def p11(t, dur):
    u = t / dur
    sc = ncam((AX - 11.0, 2.3, AZ + 1.6), (AFRONT, 2.5, AZ), u, 0.15, fov=36, w=7.5, fill=0.25)
    street(sc)
    return sc


def p12(t, dur):
    u = t / dur
    sc = ncam((12.0, 12.0, 5.7), (AX - 1, 1.0, AZ), u, 0.1, fov=46, fill=0, bloom=1.2)
    street(sc)
    return sc


def aber_lamp(out):
    return out["aber"]["lamp"]


def p13(t, dur):
    u = t / dur
    lamp = np.array([AFRONT - 0.32, 1.82, AZ + 0.82])
    sc = ncam(lamp + np.array([-1.7, -0.15, -0.7]), lamp, u, 0.14, fov=32, fill=0.6)
    street(sc)
    rng = np.random.RandomState(int(t * 8))
    for i in range(6):  # dust motes
        p = lamp + np.array([-0.3, rng.uniform(-0.4, 0.4), rng.uniform(-0.5, 0.5)])
        sc.sprite(p, lambda d, x, y, s, col: d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(220, 220, 230, 120)),
                  layer=8, live=True)
    return sc


def p14(t, dur):
    u = t / dur
    sc = ncam((0.4, 2.85, 3.4), (0, 2.75, -0.5), u, 0.1, fov=34, w=2.7)
    aber_facade(sc, open_k=0.55, room_k=0.12)
    a = character(sc, ABERNATHY, win_pos(ABERNATHY, 2.6), face="angry", pose=dict(al=(10, 4), ar=(10, 4)))
    add_emote(sc, "anger", a["head_top"], t, size=0.5, dx=0.55, dy=0.0, start=0.15)
    return sc


def p15(t, dur):
    u = t / dur
    sc = fcam((20.0, 0, 4.0), 2.6, -40, u, frac=0.42, fov=44, push=0.06)
    street(sc)
    for j, (spec, dx, dz) in enumerate(((PIP, 0.0, 0.0), (TUCK, -1.0, -0.6), (BRAX, 1.0, -0.9))):
        z = 2.4 + t * 2.6 + dz
        x = 20.6 + dx - t * 0.9
        character(sc, spec, (x, 0, z), yaw=-15, face="worried",
                  pose=dict(walk(t + j * 0.4, 9, 26), head=(35, 0, 0)))
    return sc


# ------------------------------------------------------------- 16-24: Nova tries
def p16(t, dur):
    u = t / dur
    x = ps.NORTH_X[NOVA_I]
    sc = ncam((x + 0.5, 2.3, 3.6), (x, 2.2, 0.4), u, 0.1, fov=34, w=2.6)
    street(sc, south=False)
    k = key(t, 0.18)
    character(sc, NOVA, (x, 0, 0.4), face="grin", pose=dict(ar=(165 * k, -10 - 12 * math.sin(t * 14)), al=(0, 4)))
    return sc


def p17(t, dur):
    u = t / dur
    x = ps.NORTH_X[NOVA_I]
    sc = ncam((x - 1.4, 2.3, 3.4), (x, 2.2, 0.4), u, 0.1, fov=34, w=2.6)
    street(sc, south=False)
    a = character(sc, NOVA, (x, 0, 0.4), yaw=45, face="grit", pose=dict(ar=(70, 20), er=60, al=(0, 4), head=(10, 0, 0)))
    add_emote(sc, "bulb", a["head_top"], t, size=0.6, dx=-0.5, dy=0.2, start=0.25)
    return sc


def p18(t, dur):
    u = t / dur
    sc = fcam((26.6, 0, AZ - 0.2), 2.7, -40, u, frac=0.55, fov=44, mood=DUSK)
    street(sc, lights={k: 0.5 for k in [("n", i) for i in range(8)]})
    k = clamp(t / 0.5)
    a = character(sc, NOVA, (26.25, 0, AZ - 0.45), yaw=75, face="smile",
                  pose=dict(lean=22 + 6 * (1 - k), al=(62, -6), ar=(62, -6), head=(0, -8, 0)))
    pp = np.array([27.05, 0.15, AZ + 0.1]) if k >= 1 else (a["hand_l"] + a["hand_r"]) / 2 + np.array([0.0, 0.05, 0])
    sets.plate(sc, T(*pp), crumbs=False, cookie=True)
    sets.cookie(sc, T(pp[0] + 0.12, pp[1] + 0.12, pp[2] - 0.15) @ RX(-80), s=0.7)
    return sc


def p19(t, dur):
    u = t / dur
    lamp = np.array([AFRONT - 0.32, 1.82, AZ + 0.82])
    sc = ncam((24.6, 1.4, AZ + 0.9), (27.8, 1.2, AZ + 0.4), u, 0.12, fov=40, mood=DUSK)
    street(sc)
    sets.plate(sc, T(27.05, 0.15, AZ + 0.3), crumbs=False, cookie=True)
    return sc


def _trumpet_nova(sc, t, pos, yaw, face="effort"):
    a = character(sc, NOVA, pos, yaw=yaw, face=face,
                  pose=dict(al=(95, -12), ar=(95, -12), el=55, er=55, head=(0, 22, 0), lean=-6))
    f = fwd_of(yaw)
    mouth = a["face_pt"] + np.array([0, -0.12, 0])
    M = T(*(mouth + f * 0.05)) @ RY(yaw) @ RX(-25)
    ps.trumpet(sc, M)
    ps.music_notes(sc, xf(M, (0, 0, 0.8)), t)
    return a


def p20(t, dur):
    u = t / dur
    sc = fcam((0.6, 0, 1.4), 3.4, 40, u, frac=0.6, fov=44, mood=DUSK)
    aber_facade(sc, open_k=1.0, room_k=0.05)
    _trumpet_nova(sc, t, (0.6, 0, 1.5), 145)
    return sc


def p21(t, dur):
    u = t / dur
    sc = ncam((-2.6, 1.6, 5.2), (0.5, 2.7, 0.0), u, 0.08, fov=44, mood=DUSK)
    aber_facade(sc, open_k=1.0, room_k=0.05)
    _trumpet_nova(sc, t, (0.2, 0, 1.4), 160)
    return sc


def p22(t, dur):
    u = t / dur
    sc = ncam((0.6, 2.0, 4.6), (0.0, 2.2, 0.8), u, 0.06, fov=40, w=3.6, mood=DUSK)
    shut = clamp((t - 0.22) / 0.12)
    aber_facade(sc, open_k=1.0 - shut, room_k=0.05)
    face = "effort" if shut < 1 else "shock"
    a = character(sc, NOVA, (0.25, 0, 1.6), yaw=180 + 25 * (shut >= 1), face=face,
                  pose=dict(al=(95 * (shut < 1), -12), ar=(95 * (shut < 1), -12), el=55, er=55,
                            head=(0, 22 if shut < 1 else 0, 0)))
    if shut < 1:
        ps.trumpet(sc, T(*(a["face_pt"] + np.array([0, -0.12, -0.05]))) @ RY(180) @ RX(-25))
    else:
        add_emote(sc, "sweat", a["head_top"], t, size=0.55, dx=0.5, dy=0.1, start=0.36)
        speed_lines(sc, t, cx=0.5, cy=0.3, n=14, inner=0.42, alpha=90) if t < 0.6 else None
    return sc


def p23(t, dur):
    u = t / dur
    sc = fcam((25.9, 0, AZ - 2.6), 2.8, -125, u, frac=0.5, fov=44, side=-0.5, mood=DUSK)
    street(sc, flowers=clamp(u * 1.6))
    character(sc, NOVA, (25.5, 0, AZ - 2.9), yaw=-120, face="joy", pose=dict(al=(150, -20), ar=(30, 30)))
    return sc


def p24(t, dur):
    u = t / dur
    sc = ncam((20.5, 2.4, AZ + 0.6), (AFRONT, 2.2, AZ), u, 0.08, fov=40, w=8.5, mood=DUSK, fill=0.5)
    street(sc, flowers=1.0)
    character(sc, NOVA, (25.0, 0, AZ - 0.9), yaw=-60, face="miserable",
              pose=dict(lean=10, al=(2, 2), ar=(2, 2), head=(0, -14, 0)))
    return sc


# ------------------------------------------------------- 25-37: paper airplanes
def p25(t, dur):
    u = t / dur
    x = ps.NORTH_X[NOVA_I]
    sc = ncam((x + 1.0, 2.0, 1.6), (x, 1.9, -5.0), u, 0.14, fov=40, w=4.2, bloom=1.2)
    street(sc, south=False)
    a = character(sc, NOVA, (x - 0.2, 0.3, -4.9), face="suspicious",
                  pose=dict(ar=(150, -40), er=70, head=(0, 0, 8)))
    add_emote(sc, "?", a["head_top"], t, size=0.6, dx=0.6, dy=0.25, start=0.3, hold=2.4)
    return sc


def p26(t, dur):
    u = t / dur
    sc = ncam((0.3, 1.75, 0.2), (-0.6, 1.2, -2.3), u, 0.14, fov=34, mood=dict(sky=ps.NIGHT_SKY, night=0.8),
              bloom=1.2)
    ps.nova_room(sc, lamp_k=0.25)
    ps.alarm_clock(sc, T(-0.6, 1.0, -2.3) @ RY(10), "9:00" if t > 0.25 else "8:59")
    return sc


def p27(t, dur):
    u = t / dur
    sc = ncam((-0.6, 2.35, 3.8), (0.0, 2.15, 0.0), u, 0.1, fov=38, w=2.9)
    f = nova_facade(sc, open_k=1.0)
    a = character(sc, NOVA, win_pos(NOVA, 2.4, x=0.15), face="smile" if t < 1.3 else "shock")
    sill = f["sill"] + np.array([0.15, 0.05, 0.02])
    fly(sc, t, 0.1, 1.3, (-4.0, 4.4, 2.5), sill, arc=0.5, s=0.45)
    if t > 1.3:
        add_emote(sc, "!", a["head_top"], t, size=0.55, dx=0.5, dy=0.15, start=1.32)
    return sc


def p28(t, dur):
    u = t / dur
    sc = ncam((0.3, 2.45, 2.6), (0.0, 2.25, -0.5), u, 0.1, fov=34, w=2.3)
    nova_facade(sc, open_k=1.0)
    a = character(sc, NOVA, win_pos(NOVA, 2.4), face="sparkle", pose=dict(hold_pose(), head=(0, -12, 0)))
    c = between_hands(a, fwd_of(0), up=0.02, out=0.05)
    if t < 0.5:
        plane_at(sc, c, (0.3, 0, -1), s=0.45)
    else:
        ps.note(sc, T(*c) @ RY(180) @ RX(-15), ["HA!"], w=0.55, h=0.55)
    return sc


def p29(t, dur):
    u = t / dur
    sc = ncam((0.0, 10.5, 0.9), (0.0, 0.0, 0.0), u, 0.1, fov=36, mood=dict(sky=ps.NIGHT_SKY, night=0.6),
              bloom=0.4)
    sc.ground((150, 112, 90))
    ps.note(sc, T(0, 0.03, 0) @ RX(-90), ["Why did the", "cookie go to", "the doctor?"], w=3.4, h=3.4)
    sc.light((0.0, 3.0, 2.0), (255, 220, 170), 300, 1.0)
    return sc


def p30(t, dur):
    u = t / dur
    sc = ncam((0.3, 2.45, 2.6), (0.0, 2.25, -0.5), u, 0.1, fov=34, w=2.3)
    nova_facade(sc, open_k=1.0)
    bob = abs(math.sin(t * 14)) * 0.04
    a = character(sc, NOVA, np.array(win_pos(NOVA, 2.4)) + np.array([0, bob, 0]), face="laugh",
                  pose=dict(hold_pose(), head=(0, 8, 6 * math.sin(t * 9))))
    c = between_hands(a, fwd_of(0), up=0.02, out=0.05)
    ps.note(sc, T(*c) @ RY(180) @ RX(-15), ["HA!"], w=0.55, h=0.55)
    add_emote(sc, "stars", a["head_top"], t, size=0.55, dx=-0.55, dy=0.15, start=0.15)
    return sc


def p31(t, dur):
    u = t / dur
    x = ps.NORTH_X[NOVA_I]
    k = clamp(t / 0.9)
    sc = ncam((x + 1.2, 2.4, 4.6), (x, 3.0, -6.0), u, 0.12, fov=44, w=7.5, bloom=1.0 + 0.9 * k)
    street(sc, lights={("n", NOVA_I): 1.0}, watts={("n", NOVA_I): 70 + 330 * k})
    sc.light((x, 2.5, -4.0), (255, 220, 160), 260 * k, 1.5)
    return sc


def p32(t, dur):
    u = t / dur
    sc = ncam((0.0, 2.3, 4.6), (0.0, 2.3, 9.8), u, 0.1, fov=40, w=5.6, bloom=1.2)
    street(sc, lights={("n", NOVA_I): 1.0}, watts={("n", NOVA_I): 400})
    sc.light((0.0, 3.0, 3.2), (255, 214, 150), 500, 2.0)
    crew = ((dict(DAD, shades=True), -1.9, "grin"), (BRAX, -0.6, "grin"), (dict(ORTIZ, shades=True, glasses=False), 0.65, "smile"),
            (dict(MAILMAN, shades=True), 1.95, "grin"))
    for j, (spec, x, face) in enumerate(crew):
        a = character(sc, spec, (x, 0, 9.9), yaw=180, face=face,
                      pose=dict(ar=(150, -30) if j % 2 else (0, 4), er=80 if j % 2 else 0, head=(0, -4, 0)))
    def flare(d, W, H, k=clamp(t / 0.3)):
        for i in range(10, 0, -1):
            r = W * 0.06 * i
            d.ellipse([W * 0.5 - r, -r, W * 0.5 + r, r], fill=(255, 240, 200, int(9 * k)))
    sc.overlay(flare)
    return sc


def p33(t, dur):
    u = t / dur
    x = ps.NORTH_X[LEO_I]
    sc = ncam((x + 0.8, 2.2, -1.0), (x, 2.0, -5.0), u, 0.12, fov=36, w=2.8, bloom=1.2)
    street(sc, lights={("n", LEO_I): 1.0}, south=False)
    a = character(sc, LEO, (x, 0.3, -5.0), yaw=8, face="laugh" if t > 0.6 else "grin",
                  pose=dict(ar=(120, -20), er=30, al=(10, 6)))
    plane_at(sc, a["hand_r"] + np.array([0.05, 0.12, 0.05]), (1, 0.2, 0.4), s=0.45)
    return sc


def p34(t, dur):
    u = t / dur
    x = ps.SOUTH_X[ORTIZ_S]
    sc = ncam((x - 0.8, 2.3, 8.6), (x, 2.1, 12.7), u, 0.12, fov=36, w=2.8, bloom=1.2)
    street(sc, lights={("s", ORTIZ_S): 1.0}, north=False)
    a = character(sc, ORTIZ, (x, 0.3, 12.7), yaw=180, face="joy", pose=dict(ar=(115, -20), er=30, al=(10, 6)))
    plane_at(sc, a["hand_r"] + np.array([0.0, 0.12, -0.05]), (-1, 0.2, -0.4), s=0.45)
    return sc


def p35(t, dur):
    u = t / dur
    sc = ncam((9.0, 2.6, 4.4), (8.4, 2.4, 0.6), u, 0.1, fov=36, w=2.9)
    street(sc, south=False)
    a = character(sc, MAILMAN, (8.4, 0, 0.6), yaw=-10, face="grin", pose=dict(ar=(120, -18), er=30, al=(15, 20)))
    plane_at(sc, a["hand_r"] + np.array([0.05, 0.12, 0.05]), (1, 0.2, 0.4), s=0.45)
    sc.box(T(7.7, 1.45, 0.75) @ RZ(-8), (0.32, 0.8, 0.8), (130, 90, 60), layer=6)
    sc.box(T(7.85, 1.75, 0.75), (0.06, 0.3, 0.86), (160, 116, 80), layer=6)
    return sc


def _planes_on_sills(sc, out, t=0.0):
    for key_, h in out.items():
        if key_ == "aber":
            continue
        yaw = 0 if key_[0] == "n" else 180
        p = h["door"] + fwd_of(yaw) * 0.2 + np.array([0, -0.15, 0])
        ps.paper_plane(sc, T(*(p + np.array([0, 0.05 * math.sin(t * 3 + p[0]), 0]))) @ RY(yaw + 70), s=1.2)
        sc.sprite(p + np.array([0, 0.35, 0]), lambda d, x, y, s, col: glow(d, x, y, 0.5 * s, (255, 255, 230), 70),
                  layer=8)


def p36(t, dur):
    u = t / dur
    sc = ncam((-2.5, 1.5, 2.6), (6.0, 1.2, -5.2), u, 0.14, fov=44, bloom=1.2)
    out = street(sc, lights={k: 1.0 for k in [("n", i) for i in range(8)]})
    _planes_on_sills(sc, out)
    return sc


def p37(t, dur):
    u = t / dur
    x = ps.NORTH_X[GLOW_I]
    mat = np.array([x + 0.2, 0.42, -4.75])
    sc = ncam((x + 0.5, 1.0, -2.2), mat + np.array([0, 0.25, 0]), u, 0.12, fov=40, bloom=1.2)
    street(sc, lights={("n", GLOW_I): 1.0}, south=False)
    ps.paper_plane(sc, T(*mat) @ RY(50), s=0.55)
    sparks(sc, mat + np.array([0, 0.25, 0]), t, seed=3, n=4, r=0.3, color=(255, 250, 220))
    return sc


# ------------------------------------------------------- 38-47: the stake-out
def p38(t, dur):
    u = t / dur
    sc = fcam((0.2, 0, -2.5), 2.8, 10, u, frac=0.62, fov=40, mood=dict(sky=ps.NIGHT_SKY, night=0.8), bloom=1.2)
    ps.nova_room(sc, lamp_k=0.2)
    ps.alarm_clock(sc, T(-0.6, 1.0, -2.3) @ RY(18), "8:59")
    character(sc, NOVA, (1.0, 0, -2.7), yaw=-30, face="suspicious", pose=dict(lean=8, head=(-10, 0, 0)))
    return sc


def _bush_nova(sc, t, face, emote=None, start=0.0):
    sc_ = sc
    ps.big_bush(sc_, 24.0, 0.6, s=1.15)
    a = character(sc_, NOVA, (24.1, -0.36, 0.2), yaw=25, face=face, pose=dict(head=(35, 0, 0)))
    for dx, dy in ((-0.45, 2.0), (0.4, 1.95), (0.0, 2.1)):  # leaves stuck in the hat
        sc_.blob(T(24.1 + dx * 0.6, dy, 0.5), (0.2, 0.1, 0.12), (70, 160, 80), layer=6, n=8, m=5)
    if emote:
        add_emote(sc_, emote, a["head_top"], t, size=0.6, dx=-0.55, dy=0.25, start=start)
    return a


def p39(t, dur):
    u = t / dur
    sc = ncam((23.0, 1.75, 4.4), (24.1, 1.6, 0.4), u, 0.1, fov=36)
    street(sc)
    _bush_nova(sc, t, "suspicious")
    return sc


def p40(t, dur):
    u = t / dur
    sc = ncam((0.6, 2.8, 3.8), (0.0, 2.6, 0.0), u, 0.1, fov=36, w=3.2)
    op = clamp((t - 0.15) / 0.4)
    aber_facade(sc, open_k=op, room_k=0.15 + 0.25 * op)
    return sc


def p41(t, dur):
    u = t / dur
    sc = ncam((19.5, 1.7, 2.2), (AFRONT, 2.3, AZ + 1.4), u, 0.12, fov=34, bloom=1.2)
    street(sc, aber_win=1.0, aber_win_k=0.35)
    ps.big_bush(sc, 20.9, 2.4, s=0.6)
    return sc


def p42(t, dur):
    u = t / dur
    sc = ncam((0.5, 2.85, 3.6), (0.0, 2.75, -0.5), u, 0.12, fov=34, w=2.8)
    aber_facade(sc, open_k=1.0, room_k=0.4)
    character(sc, ABERNATHY, win_pos(ABERNATHY, 2.6), face="neutral", pose=dict(al=(10, 4), ar=(10, 4)))
    return sc


def p43(t, dur):
    u = t / dur
    sc = ncam((0.25, 2.6, 2.4), (0.0, 2.5, -0.5), u, 0.1, fov=34, w=1.9)
    aber_facade(sc, open_k=1.0, room_k=0.4)
    a = character(sc, ABERNATHY, win_pos(ABERNATHY, 2.6), face="smile",
                  pose=dict(hold_pose(fold=8 * math.sin(t * 10)), head=(0, -14, 0)))
    c = between_hands(a, fwd_of(0), up=0.18, out=0.08)
    k = clamp((t - 0.2) / 0.8)
    if k < 1:
        ps.note(sc, T(*c) @ RX(-60 * k) @ RZ(30 * k), [], w=0.6 * (1 - 0.5 * k), h=0.6)
    else:
        plane_at(sc, c, (0.4, 0.1, 1), s=0.45)
    return sc


def p44(t, dur):
    u = t / dur
    sc = ncam((1.0, 2.7, 3.6), (0.0, 2.9, 0.0), u, 0.08, fov=40, w=2.9)
    aber_facade(sc, open_k=1.0, room_k=0.4)
    sw = clamp((t - 0.15) / 0.25)
    arm = 150 - 100 * sw
    pos = np.array(win_pos(ABERNATHY, 2.6)) + np.array([0, 0, 0.15 * sw])
    a = character(sc, ABERNATHY, pos, face="effort" if sw < 1 else "smile",
                  pose=dict(ar=(arm, -10), al=(20, 6), lean=-10 * sw))
    if t < 0.4:
        plane_at(sc, a["hand_r"] + np.array([0, 0.1, 0.05]), (0, 0.3, 1), s=0.45)
    else:
        fly(sc, t, 0.4, 2.0, a["hand_r"] + np.array([0, 0.1, 0.1]), (-6.0, 7.0, 9.0), arc=0.6, s=0.45, land=False)
        if t < 0.8:
            speed_lines(sc, t, cx=0.4, cy=0.3, n=12, inner=0.35, alpha=80)
    return sc


def p45(t, dur):
    u = t / dur
    sc = ncam((23.4, 1.75, 3.2), (24.1, 1.65, 0.4), u, 0.1, fov=34)
    street(sc)
    _bush_nova(sc, t, "shock", "!", 0.05)
    return sc


def p46(t, dur):
    u = t / dur
    sc = ncam((AX + 5.0, 10.5, AZ), (6.0, 0.0, AZ), u, 0.08, fov=50, bloom=1.3)
    targets = [("n", 7), ("s", 6), ("n", 6), ("s", 5), ("n", 5), ("s", 4), ("n", 4), ("s", 3), ("n", 3), ("s", 2)]
    lights = {}
    plan = []
    for j, k_ in enumerate(targets):
        t0 = 0.05 + j * 0.16
        t1 = t0 + 0.75
        lights[k_] = 0.3 + 0.7 * clamp((t - t1) / 0.15)
        plan.append((k_, t0, t1))
    out = street(sc, lights=lights, aber_win=1.0, aber_win_k=0.35)
    for k_, t0, t1 in plan:
        p = fly(sc, t, t0, t1, (AFRONT - 0.5, 3.0, AZ + 1.6), out[k_]["sill_r"] + np.array([0, 0.08, 0]), arc=2.0,
                s=1.4)
        if p is not None and t < t1:
            sc.sprite(p, lambda d, x, y, s, col: glow(d, x, y, 1.2 * s, (255, 255, 235), 110), layer=8, live=True)
    return sc


def p47(t, dur):
    u = t / dur
    sc = ncam((0.9, 2.9, 5.2), (0.0, 2.7, -0.5), u, 0.2, fov=36, w=3.8)
    aber_facade(sc, open_k=1.0, room_k=0.12)
    character(sc, ABERNATHY, win_pos(ABERNATHY, 2.6), face="sad", pose=dict(al=(4, 2), ar=(4, 2), head=(0, -10, 0)))
    return sc


# ------------------------------------------------------- 48-57: thank you
def p48(t, dur):
    u = t / dur
    sc = ncam((0.4, 2.35, 0.9), (-0.25, 2.1, -2.0), u, 0.1, fov=36, w=2.4,
              mood=dict(sky=ps.NIGHT_SKY, night=0.8), fill=0.6, bloom=1.1)
    ps.nova_room(sc, lamp_k=1.0)
    a = character(sc, NOVA, (-0.25, 0, -2.0), face="smile" if t < 1.4 else "grin",
                  pose=dict(hold_pose(fold=10 * math.sin(t * 9)), head=(0, -16, 0)))
    c = between_hands(a, fwd_of(0), up=0.15, out=0.08)
    k = clamp((t - 0.3) / 1.0)
    if k < 1:
        ps.note(sc, T(*c) @ RX(-70 * k) @ RZ(25 * k), [], w=0.7 * (1 - 0.5 * k), h=0.7)
    else:
        plane_at(sc, c, (0.4, 0.1, 1), s=0.42)
    return sc


def _pencil(sc, p):
    M = T(*p) @ RZ(-35) @ RX(-20)
    sc.box(M @ T(0, 0.55, 0), (0.12, 1.1, 0.12), (250, 204, 60), layer=8)
    sc.box(M @ T(0, 1.12, 0), (0.12, 0.08, 0.12), (200, 200, 210), layer=8)
    sc.box(M @ T(0, 1.22, 0), (0.12, 0.14, 0.12), (250, 150, 160), layer=8)
    sc.blob(M @ T(0, -0.04, 0), (0.1, 0.14, 0.1), (240, 210, 160), layer=8, n=8, m=5)


def p49(t, dur):
    u = t / dur
    sc = ncam((0.0, 10.5, 0.9), (0.0, 0.0, 0.0), u, 0.1, fov=36, mood=dict(sky=ps.NIGHT_SKY, night=0.6),
              bloom=0.4)
    sc.ground((150, 112, 90))
    msg = "Thank you."
    n = int(len(msg) * clamp(t / (dur * 0.85)))
    ps.note(sc, T(0, 0.03, 0) @ RX(-90), [msg[:n] + " " * (len(msg) - n), " ", " "], w=3.4, h=3.4, folds=False)
    sc.light((0.0, 3.0, 2.0), (255, 220, 170), 300, 1.0)
    _pencil(sc, (-0.9 + 1.8 * n / len(msg), 0.1, -0.6))
    return sc


def p50(t, dur):
    u = t / dur
    sc = ncam((0.0, 10.5, 0.9), (0.0, 0.0, 0.0), u, 0.1, fov=36, mood=dict(sky=ps.NIGHT_SKY, night=0.6),
              bloom=0.4)
    sc.ground((150, 112, 90))
    ps.note(sc, T(0, 0.03, 0) @ RX(-90), ["Thank you.", "From the", "whole street."], w=3.4, h=3.4, folds=False,
            heart=True)
    sc.light((0.0, 3.0, 2.0), (255, 220, 170), 300, 1.0)
    return sc


def p51(t, dur):
    u = t / dur
    sc = fcam((14.0, 0, 5.7), 2.7, 35, u, frac=0.5, fov=42, side=0.3)
    street(sc)
    sw = clamp((t - 0.12) / 0.2)
    a = character(sc, NOVA, (14.0, 0, 5.7), yaw=90, face="effort" if sw < 1 else "grin",
                  pose=dict(ar=(150 - 110 * sw, -10), al=(20, 6), lean=8 * sw, ll=-15 * sw, lr=15 * sw))
    if t < 0.3:
        plane_at(sc, a["hand_r"] + np.array([0, 0.1, 0]), (1, 0.3, 0), s=0.45)
    else:
        fly(sc, t, 0.3, 2.5, a["hand_r"] + np.array([0.1, 0.1, 0]), (AFRONT, 2.0, AZ + 1.6), arc=1.5, s=0.45,
            land=False)
    return sc


def p52(t, dur):
    u = t / dur
    sc = ncam((-0.5, 2.6, 3.8), (0.0, 2.3, 0.0), u, 0.1, fov=38, w=3.4)
    f = aber_facade(sc, open_k=1.0, room_k=0.3)
    character(sc, ABERNATHY, win_pos(ABERNATHY, 2.6, z=-1.6), yaw=20, face="neutral")
    fly(sc, t, 0.05, 1.0, (-4.5, 4.6, 3.0), f["sill"] + np.array([0.1, 0.06, 0.02]), arc=0.4, s=0.45)
    return sc


def _aber_note(sc, t, face, lines=("Thank you.",), head=(0, -12, 0), y_off=0.0):
    a = character(sc, ABERNATHY, np.array(win_pos(ABERNATHY, 2.6)) + np.array([0, y_off, 0]), face=face,
                  pose=dict(hold_pose(), head=head))
    c = between_hands(a, fwd_of(0), up=0.04, out=0.06)
    ps.note(sc, T(*c) @ RY(180) @ RX(-20), list(lines), w=0.6, h=0.6)
    return a


def p53(t, dur):
    u = t / dur
    sc = ncam((0.3, 2.75, 3.0), (0.0, 2.6, -0.5), u, 0.1, fov=34, w=2.4)
    aber_facade(sc, open_k=1.0, room_k=0.35)
    a = character(sc, ABERNATHY, win_pos(ABERNATHY, 2.6), face="neutral" if t < 0.35 else "shock",
                  pose=dict(hold_pose(), head=(0, -10, 0)))
    c = between_hands(a, fwd_of(0), up=0.2, out=0.06)
    k = clamp((t - 0.05) / 0.3)
    if k < 1:
        plane_at(sc, c, (0.4, 0.1, 1), s=0.45)
    else:
        ps.note(sc, T(*c) @ RY(180) @ RX(-20), ["Thank you."], w=0.6, h=0.6)
    return sc


def p54(t, dur):
    u = t / dur
    sc = ncam((0.2, 2.95, 2.1), (0.0, 2.85, -0.5), u, 0.1, fov=32, w=1.5)
    aber_facade(sc, open_k=1.0, room_k=0.35)
    nod = -10 - 8 * math.sin(t * 5.5) ** 2
    a = _aber_note(sc, t, "stung" if t < 0.75 else "cry", head=(0, nod, 0))
    return sc


def p55(t, dur):
    u = t / dur
    sc = ncam((-0.4, 2.8, 4.2), (0.5, 2.7, 0.0), u, 0.1, fov=36, w=3.4)
    aber_facade(sc, open_k=1.0, room_k=0.35, lamp_k=flicker(t, 0.0, 0.35, 1.7) * clamp((t - 0.6) / 0.2))
    a = _aber_note(sc, t, "joy", head=(0, -4, 0))
    return sc


def p56(t, dur):
    u = t / dur
    sc = ncam((-0.6, 2.8, 4.4), (0.6, 2.75, 0.0), u, 0.12, fov=38, w=3.6, bloom=1.0 + 0.8 * clamp((t - 0.25) / 0.3))
    on = clamp((t - 0.25) / 0.12)
    f = aber_facade(sc, open_k=1.0, room_k=0.35 + 0.6 * on, lamp_k=max(on, flicker(t, 0.0, 0.3, 1.7) * (t < 0.25)),
                    lamp_watts=60 + 260 * on)
    a = _aber_note(sc, t, "laugh" if on >= 1 else "joy", head=(0, 4, 0))
    if on > 0:
        sparks(sc, f["lamp"] + np.array([0, 0, 0.1]), t, seed=2, n=7, r=0.5, color=(255, 236, 160))
    if 0.25 <= t < 0.25 + 2 / 30:
        sc.flash = 0.6
    return sc


def p57(t, dur):
    u = t / dur
    sc = ncam((6.0, 9.5, 5.7), (AX - 1.0, 2.0, AZ), u, 0.15, fov=46, fill=0, bloom=1.5)
    out = street(sc, aber_k=1.0, aber_lamp_watts=500,
                 lights={k: 1.0 for k in [("n", i) for i in range(8)] + [("s", i) for i in range(7)]})
    sc.light((AFRONT - 1.5, 3.0, AZ), (255, 214, 150), 700, 2.0)
    sparks(sc, out["aber"]["lamp"], t, seed=5, n=8, r=1.2, color=(255, 240, 170))
    fade_out(sc, t, dur)
    return sc


_FNS = [globals()[f"p{i:02d}"] for i in range(1, len(LINES) + 1)]
SHOTS = [(i + 1, 1.4, txt, fn) for i, (txt, fn) in enumerate(zip(LINES, _FNS))]
SHOTS, WORD_TIMES = load_timing(SHOTS, TIMING_FILE)
