"""The Floating Laughs: shot list. Each shot: (number, seconds, caption text, fn(t, dur) -> Scene)."""
import os

TIMING_FILE = "laughs_timing.json"
SPOKEN = {"14": "fourteen", "MOOOOON.": "moon", "MOOOOON": "moon", "practising": "practicing"}
PHONES = {"benny": "B EH N IY", "gus": "G AH S", "mittens": "M IH T AH N Z", "unbuckled": "AH N B AH K AH L D"}

LINES = [
    "In this town, every time you LAUGH,",
    "you float.",
    "A giggle lifts you an inch.",
    "A belly laugh? You're on the ROOF.",
    "That's why everyone wears heavy boots.",
    "And why nobody tells jokes at the dinner table.",
    "We lost Uncle Ray that way.",
    "He's fine. He lives on a cloud now.",
    "I'm Benny.",
    "And I laugh at EVERYTHING.",
    "Dogs.",
    "Socks.",
    "The word pickle.",
    "My boots weigh as much as a fridge.",
    "I still bump my head on the classroom ceiling every day.",
    "Then there's Grandpa.",
    "Grandpa wears the heaviest boots in town.",
    "Iron. Size 14.",
    "He never smiles. Never laughs.",
    "Everybody calls him Grumpy Gus.",
    "Every night, Grandpa locks himself in the garage.",
    "Weird.",
    "Saturday was the Sky Festival.",
    "The mayor's cat, Mittens, climbed the water tower.",
    "Then the ladder broke.",
    "Mittens was stuck at the TOP.",
    "Somebody laugh! the mayor yelled.",
    "The whole town tried.",
    "Fake laughs don't work. Nobody moved an inch.",
    "I tried too.",
    "But everyone was staring at me.",
    "I couldn't laugh. Not even at pickle.",
    "Then Grandpa stomped over.",
    "Clank. Clank. CLANK.",
    "He bent down and unbuckled his iron boots.",
    "The whole town gasped.",
    "Grandpa looked at me and said,",
    "Why did the cow go to space?",
    "I shook my head.",
    "To see the MOOOOON.",
    "It was the worst joke I'd ever heard.",
    "Grandpa snorted.",
    "Then he CRACKED UP.",
    "He shot into the sky like a balloon.",
    "I laughed so hard I went right after him.",
    "We grabbed Mittens at the top.",
    "Turns out, every night in the garage, Grandpa was practising jokes.",
    "He laughs so much he needs iron boots just to stay DOWN.",
    "He wasn't grumpy. He was holding on.",
    "Now we tell jokes every night.",
    "We need a BIGGER ceiling.",
]
import math  # noqa: E402

import numpy as np  # noqa: E402

import laughs_sets as ls  # noqa: E402
import porch_sets as ps  # noqa: E402
import sets  # noqa: E402
from cast import BRAX, DAD, GUS, HERO, MAYOR, MOM, PIP, TUCK, UNCLE_RAY, character, crowd_spec, sit  # noqa: E402
from engine import RX, RY, RZ, T, add_emote, clamp, lerp, speed_lines, xf  # noqa: E402
from porch import fcam, fwd_of, ncam, win_pos  # noqa: E402
from shots import probe, sparks, walk  # noqa: E402
from story import load_timing  # noqa: E402

DAY = dict(sky=ls.SKY, night=0.0)
NIGHT = dict(sky=ps.NIGHT_SKY, night=1.0)
BOOT_GREY = (104, 108, 120)


def booted(spec, k=1.0):
    return dict(spec, boots=k, shoes=BOOT_GREY)


BENNY = booted(HERO, 1.15)
KIDS = [booted(PIP, 0.9), booted(TUCK, 1.0), booted(BRAX, 1.0)]
DAD_B, MOM_B, MAYOR_B = booted(DAD, 1.1), MOM, booted(MAYOR, 1.0)
CROWD = [booted(crowd_spec(i, adult=i % 3 != 0), 1.0) for i in range(14)]
FLOAT = dict(al=(150, -30), ar=(150, -30), ll=12, lr=-12, head=(0, 12, 0))
FOLDED = dict(al=(75, -32), ar=(75, -32), el=100, er=100)
WT = {}  # filled from the voice timing at the bottom (word onsets inside each shot)


def ht(spec):
    return (spec["leg"][1] + spec["torso"][1] + spec["head"][1]) * spec["s"]


def dcam(pos, tgt, u, push=0.1, fov=40, **kw):
    kw.setdefault("mood", DAY)
    kw.setdefault("bloom", 0.0)
    return ncam(pos, tgt, u, push, fov, **kw)


def dfcam(center, height, az, u, **kw):
    kw.setdefault("mood", DAY)
    kw.setdefault("bloom", 0.0)
    return fcam(center, height, az, u, **kw)


def head_cu(spec, pos, yaw, pose, u, dist=3.0, side=0.35, up=0.1, fov=34, push=0.08, **kw):
    h = probe(spec, pos, yaw, pose)["head"]
    f = fwd_of(yaw)
    right = np.array([f[2], 0, -f[0]])
    return dcam(h + f * dist + right * side + np.array([0, up, 0]), h - np.array([0, 0.12, 0]), u, push, fov, **kw)


def bob(t, k=0.08, f=4.0):
    return k * math.sin(t * f)


def word_t(num, i, default=0.0):
    w = WT.get(num, [])
    return w[i][0] if i < len(w) else default


def laugh_pose(t, k=1.0):
    w = 10 * math.sin(t * 16)
    return dict(al=(40 + w, 30), ar=(40 - w, 30), head=(0, 10 * k, 6 * math.sin(t * 12)))


# ------------------------------------------------------- 1-8: the rule
def k01(t, dur):
    u = t / dur
    sc = dfcam((0, 0, 0.6), 2.4, 15, u, frac=0.5, fov=40)
    sets.town(sc)
    rise = 0.35 * clamp((t - 0.9) / 1.0)
    a = character(sc, CROWD[3], (0, rise + bob(t, 0.03 * (rise > 0)), 0.6), face="joy" if t < 0.9 else "laugh",
                  pose=laugh_pose(t, 0.5), shadow_y=0)
    ls.music_notes(sc, a["head_top"], t, n=3)
    return sc


def k02(t, dur):
    u = t / dur
    rise = 0.4 + 2.2 * u
    sc = dcam((1.2, 0.6, 6.4), (0.0, 2.2 + rise * 0.9, 0.6), u, 0.05, fov=44)
    sets.town(sc)
    a = character(sc, CROWD[3], (0, rise, 0.6), face="laugh", pose=dict(FLOAT, **{"head": (0, 14, 0)}), shadow_y=0)
    sparks(sc, a["foot_l"], t, seed=2, n=4, r=0.4, color=(255, 255, 220))
    return sc


def k03(t, dur):
    u = t / dur
    sc = dcam((1.2, 0.4, 4.0), (0.0, 0.55, 0.6), u, 0.08, fov=40, blur=0)
    sets.town(sc)
    hover = 0.2 + bob(t, 0.03, 6)
    character(sc, CROWD[3], (0, hover, 0.6), face="joy", pose=dict(ll=5, lr=-5), shadow_y=0)
    return sc


def k04(t, dur):
    u = t / dur
    sc = dcam((1.2, 2.2, 3.0), (0.0, 3.7, -5.6), u, 0.08, fov=44)
    sets.town(sc)
    h = 3.4  # house i=3 at x = 0
    a = character(sc, CROWD[5], (-0.2, h - 0.05, -5.35), face="laugh", shadow=False,
                  pose=dict(lean=-53, al=(170, -20), ar=(170, -20), ll=6, lr=-6, head=(0, 8 * math.sin(t * 14), 0)))
    ls.sticker(sc, a["head"], "HA HA", t, start=0.15, hold=2.3, size=0.6, dx=0.9, dy=0.4)
    return sc


def k05(t, dur):
    u = t / dur
    sc = dcam((1.4 - 1.8 * u, 1.0, 3.4), (0.4 - 1.4 * u, 0.6, 0.75), u, 0.0, fov=40)
    ls.home(sc, boots_row=True)
    return sc


def _family_table(sc, t, faces, rise=0.0, laugh=False):
    seat_y = 0.86
    out = {}
    for key, spec, x, z, yaw in (("dad", DAD_B, -1.3, -1.35, 0), ("mom", MOM_B, 0.0, -1.35, 0),
                                 ("benny", BENNY, 1.3, -1.35, 0), ("gus", booted(GUS, 1.6), 2.75, 0.0, -90)):
        if key in faces:
            r = rise if (laugh and key in ("benny", "gus")) else 0.0
            sets.chair(sc, x, z - (0.0 if yaw == 0 else 0), yaw=yaw, c=(150, 100, 70))
            pose = sit()
            if laugh and key in ("benny", "gus"):
                pose.update(laugh_pose(t))
            else:
                pose.update(al=(55, 4), ar=(55, 4))
            ll = spec["leg"][1] * spec["s"]
            out[key] = character(sc, spec, (x, seat_y - ll + r + bob(t, 0.04) * (r > 0), z), yaw=yaw,
                                 face=faces[key], pose=pose, shadow=False)
    return out


def k06(t, dur):
    u = t / dur
    sc = dcam((0.3, 3.4, 5.6), (0.3, 2.3, -0.6), u, 0.12, fov=44)
    ls.dining(sc)
    f = _family_table(sc, t, dict(dad="neutral", mom="neutral", benny="worried", gus="suspicious"))
    add_emote(sc, "sweat", f["benny"]["head_top"], t, size=0.5, dx=0.5, dy=0.1, start=0.3)
    return sc


def _fork(sc, M):
    sc.box(M @ T(0, 0.3, 0), (0.05, 0.6, 0.04), (210, 214, 222), layer=7)
    for k in (-1, 0, 1):
        sc.box(M @ T(k * 0.04, 0.68, 0), (0.025, 0.18, 0.025), (210, 214, 222), layer=7)


def k07(t, dur):
    u = t / dur
    rise = 2.2 + 2.6 * u
    sc = dcam((0.8, 0.6, 9.5), (1.3, 3.2 + 1.4 * u, 0.0), u, 0.05, fov=44)
    ls.home(sc)
    ps.window  # (the right window is open: Ray floated out of it)
    a = character(sc, UNCLE_RAY, (1.9, rise, 0.7), yaw=-15, face="laugh", pose=dict(FLOAT, ar=(160, -40)),
                  shadow_y=0)
    _fork(sc, T(*a["hand_r"]) @ RZ(-20))
    return sc


def k08(t, dur):
    u = t / dur
    sc = dcam((0.6, 3.0, 10.5), (0.3, 2.4, 0.0), u, 0.1, fov=40, sky=((120, 190, 255), (220, 240, 255)))
    ls.cloud_home(sc, t)
    pose = sit()
    pose.update(ar=(165, -20 - 15 * math.sin(t * 10)), al=(30, 10), lean=-20)
    ll = UNCLE_RAY["leg"][1] * UNCLE_RAY["s"]
    a = character(sc, UNCLE_RAY, (0.0, 1.85 - ll, 0.2), face="grin", pose=pose, shadow=False)
    add_emote(sc, "stars", a["head_top"], t, size=0.6, dx=0.7, dy=0.2, start=0.4, hold=2.0)
    return sc


# ------------------------------------------------------------ 9-15: Benny
def k09(t, dur):
    u = t / dur
    sc = head_cu(BENNY, (0, 0, 0.6), 0, None, u, dist=3.6, up=-0.5, fov=36)
    sets.town(sc)
    a = character(sc, BENNY, (0, 0, 0.6), face="grin", pose=dict(ar=(30, 25), al=(10, 6)))
    sparks(sc, a["head_top"] + np.array([0.5, 0.1, 0]), t, seed=4, n=4, r=0.3)
    return sc


def k10(t, dur):
    u = t / dur
    rise = 0.6 * clamp((t - 0.4) / 1.2)
    sc = dfcam((0, 0, 0.6), 3.4, 10, u, frac=0.55, fov=40, push=0.12)
    sets.town(sc)
    a = character(sc, BENNY, (0, rise + bob(t, 0.05), 0.6), face="laugh", pose=laugh_pose(t), shadow_y=0)
    ls.music_notes(sc, a["head_top"], t)
    return sc


def k11(t, dur):
    u = t / dur
    sc = dfcam((0.2, 0, 0.6), 3.3, 0, u, frac=0.55, fov=42)
    sets.town(sc)
    ls.dog(sc, T(1.0, 0, 1.2) @ RY(-35), t)
    character(sc, BENNY, (-0.8, 0.15 + bob(t, 0.05), 0.4), yaw=25, face="laugh", pose=laugh_pose(t), shadow_y=0)
    return sc


def k12(t, dur):
    u = t / dur
    sc = dcam((0.3, 4.6, 2.8), (0.0, 0.0, 0.0), u, 0.1, fov=40)
    sets.floor_tiles(sc, -6, 6, -6, 6, (150, 112, 90), (140, 104, 84), step=1.0)
    ls.sock(sc, T(-0.45, 0.08, 0) @ RX(-90) @ RZ(15), "stripes", (240, 90, 110), (255, 255, 255))
    ls.sock(sc, T(0.5, 0.08, 0.1) @ RX(-90) @ RZ(-25), "dots", (90, 200, 120), (255, 230, 90))
    ls.sticker(sc, (0.0, 0.3, 0.9), "HA!", t, start=0.1, size=0.35, dy=0.0, dx=0.5)
    return sc


def k13(t, dur):
    u = t / dur
    sc = dcam((0.2, 2.0, 3.8), (0.2, 1.8, 0.0), u, 0.12, fov=40)
    ls.dining(sc, ceiling=False)
    sets.plate(sc, T(0, 1.42, 0.3), crumbs=False)
    ls.pickle(sc, T(0, 1.75, 0.3), s=0.32)
    character(sc, BENNY, (1.35, 0, 0.55), yaw=-35, face="laugh", pose=laugh_pose(t))
    ls.sticker(sc, (0.0, 2.2, 0.3), "PICKLE", t, start=0.25, size=0.32, dy=0.0, color=(150, 230, 110))
    return sc


def k14(t, dur):
    u = t / dur
    sc = dcam((0.6, 1.6, 8.4), (0.3, 1.6, 0.0), u, 0.08, fov=42)
    sets.floor_tiles(sc, -6, 6, -4, 8, (210, 210, 214), (200, 200, 206), step=1.0)
    sets.wall(sc, 0, 3.5, -1.2, 14, 7, (250, 236, 200))
    ls.fridge(sc, T(1.3, 0, -0.4))
    for sx in (-1, 1):
        ls.iron_boot(sc, T(-0.8 + sx * 0.55, 0, 0.3) @ RY(-8), s=1.6)
    return sc


def k15(t, dur):
    u = t / dur
    sc = dcam((0.6, 1.6, 7.6), (0.0, 3.6, 0.0), u, 0.06, fov=46)
    ls.classroom_ceiling(sc)
    sets.class_desks(sc, skip={(2, 1), (2, 2)}, faces=("laugh", "grin"))
    hit = (t * 1.3) % 1.0
    top = 5.1 - 0.04
    bonk = max(0.0, 1 - hit * 3)
    y = top - ht(BENNY) - 0.62 - 0.25 * (1 - abs(math.cos(hit * math.pi)))
    a = character(sc, BENNY, (0.0, y, 0.2), face="laugh" if hit > 0.25 else "effort", pose=FLOAT, shadow_y=0)
    if bonk > 0:
        add_emote(sc, "stars", a["head_top"], t, size=0.7, dx=0.0, dy=0.05, start=t - hit / 1.3, hold=0.6)
    return sc


# ---------------------------------------------------------- 16-22: Grumpy Gus
GUS_B = booted(GUS, 1.6)
PORCH = (0.0, 0.3, 0.7)


def k16(t, dur):
    u = t / dur
    sc = dfcam(PORCH, ht(GUS_B), 8, u, frac=0.42, fov=40, push=0.12)
    ls.home(sc)
    character(sc, GUS_B, PORCH, face="suspicious", pose=FOLDED)
    return sc


def k17(t, dur):
    u = t / dur
    sc = dcam((0.5, 0.45, 3.0), (0.0, 0.5 + 1.6 * u, PORCH[2]), u, 0.04, fov=40)
    ls.home(sc)
    character(sc, GUS_B, PORCH, face="suspicious", pose=FOLDED)
    return sc


def k18(t, dur):
    u = t / dur
    sc = dcam((0.0, 0.0, 5.6), (0.0, 0.0, 0.0), u, 0.12, fov=40, sky=((60, 60, 70), (60, 60, 70)))
    ls.side_stamp(sc, T(0, 0, 0), "14", s=1.0)
    for k in range(int(t / 0.55) + 1):
        ls.dust(sc, (0.0, -1.2, 0.4), t, k * 0.55, n=5)
    return sc


def k19(t, dur):
    u = t / dur
    sc = head_cu(GUS_B, PORCH, 0, FOLDED, u, dist=3.4, up=0.0)
    ls.home(sc)
    a = character(sc, GUS_B, PORCH, face="angry" if t > 1.2 else "suspicious", pose=FOLDED)
    add_emote(sc, "anger", a["head_top"], t, size=0.55, dx=0.6, dy=0.0, start=1.25)
    return sc


def k20(t, dur):
    u = t / dur
    sc = dcam((1.5, 2.6, 13.0), (0.6, 2.0, 1.0), u, 0.06, fov=44)
    ls.home(sc)
    character(sc, GUS_B, PORCH, face="suspicious", pose=FOLDED)
    for j, spec in enumerate(KIDS):
        x = -5.5 + t * 3.4 + j * 1.3
        pose = dict(walk(t + j * 0.3, 12, 30), head=(-50, 0, 0))
        if j == 1:
            pose.update(ar=(90, -40))
        a = character(sc, spec, (x, 0, 3.9 + 0.3 * (j % 2)), yaw=90, face="worried", pose=pose)
    return sc


def k21(t, dur):
    u = t / dur
    sc = ncam((7.5, 2.4, 11.5), (4.8, 1.8, -0.5), u, 0.06, fov=44, bloom=1.2)
    ps.night_sky(sc)
    door = 1.0 - clamp((t - 1.4) / 0.9)
    ls.home(sc, night=True, garage_k=door, k=0.7)
    z = lerp(2.5, -1.2, clamp(t / 1.3))
    if t < 1.5:
        character(sc, GUS_B, (5.4, 0, z), yaw=180, face="suspicious", pose=walk(t, 7, 20))
    return sc


def k22(t, dur):
    u = t / dur
    sc = ncam((0.3, 2.5, 2.8), (0.0, 2.35, -0.5), u, 0.1, fov=34, w=2.4)
    sc.ground((60, 104, 62))
    ps.night_sky(sc)
    ps.facade(sc, ls.HOME_COLOR, open_k=0.7, room_k=1.0, lamp_k=0.8, win_y=2.4, curtains=(150, 70, 70))
    a = character(sc, BENNY, win_pos(BENNY, 2.4), yaw=-20, face="suspicious", pose=dict(head=(-25, 0, 0)))
    add_emote(sc, "?", a["head_top"], t, size=0.55, dx=0.55, dy=0.2, start=0.1)
    return sc


# ------------------------------------------------------- 23-32: the festival
def k23(t, dur):
    u = t / dur
    sc = dcam((-6.0 + 5.0 * u, 3.0, 13.0), (2.0 + 3.0 * u, 5.0, -6.0), u, 0.0, fov=48)
    ls.festival(sc, t)
    ls.crowd_line(sc, CROWD[:8], [-8, -5.5, -3, -0.5, 2, 4.5, 9, 11.5], 0.5, faces=("joy", "grin", "smile"),
                  poses=[walk(t + i, 6, 10) for i in range(4)])
    from shots import confetti
    confetti(sc, t, n=40)
    return sc


def k24(t, dur):
    u = t / dur
    y = 1.0 + 6.0 * u
    tw = ls.TOWER
    sc = dcam((tw[0] + 1.4, 1.2 + 5.0 * u, tw[2] + 6.0), (tw[0], y + 0.6, tw[2] + 1.9), u, 0.0, fov=44)
    ls.festival(sc, t)
    ls.cat(sc, T(tw[0], y, tw[2] + ls.LEG + 0.45) @ RX(-80), t)
    return sc


def k25(t, dur):
    u = t / dur
    tw = ls.TOWER
    fall = clamp((t - 0.2) / 0.7)
    sc = dcam((tw[0] + 5.0, 3.0, tw[2] + 10.5), (tw[0], 4.5, tw[2] + 1.9), u, 0.04, fov=46)
    ls.festival(sc, t, ladder="falling", fall_k=fall)
    ls.cat(sc, T(tw[0], 9.6, tw[2] + ls.LEG + 0.45) @ RX(-80), t, mood="scared")
    ls.sticker(sc, (tw[0], 5.5, tw[2] + 2.0), "CRACK!", t, start=0.2, size=0.9, color=(255, 120, 80), dx=1.6)
    if fall >= 1:
        ls.dust(sc, (tw[0], 0.2, tw[2] + 4.5), t, 0.9, n=8)
    return sc


def k26(t, dur):
    u = t / dur
    tw = ls.TOWER
    c = np.array([tw[0] + 0.2, 11.15, tw[2] + 2.55])
    sc = dcam(c + np.array([1.2, 1.4, 4.2]), c + np.array([0, 0.5, 0]), u, 0.15, fov=40)
    ls.festival(sc, t, ladder="broken")
    head = ls.cat(sc, T(*c) @ RY(10), t, mood="scared")
    add_emote(sc, "sweat", head, t, size=0.5, dx=0.4, dy=0.05, start=0.2)
    return sc


def k27(t, dur):
    u = t / dur
    pos = (1.5, 0, 1.0)
    pose = dict(ar=(95, 4), er=70, al=(40, 20), head=(0, 10, 0), lean=-6)
    sc = head_cu(MAYOR_B, pos, 10, pose, u, dist=4.6, up=-1.2, fov=40, side=-0.6)
    ls.festival(sc, t, ladder="broken")
    a = character(sc, MAYOR_B, pos, yaw=10, face="jaw", pose=pose)
    ls.megaphone(sc, T(*(a["face_pt"] + np.array([-0.25, -0.15, 0.05]))) @ RY(-70) @ RX(-10))
    add_emote(sc, "!", a["head_top"], t, size=0.7, dx=-0.7, dy=0.3, start=0.1, hold=2.2)
    return sc


def _crowd(sc, t, faces, poses=None, z=-1.0):
    return ls.crowd_line(sc, CROWD[:9], [-4.8, -3.6, -2.4, -1.2, 0.0, 1.2, 2.4, 3.6, 4.8], z, faces=faces,
                         poses=poses)


def k28(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.6, 9.5), (0.0, 2.1, -1.0), u, 0.06, fov=44)
    ls.festival(sc, t, ladder="broken")
    _crowd(sc, t, ("grit", "effort", "grin", "worried"),
           poses=[dict(al=(20, 20), ar=(20, 20), head=(0, 6 * math.sin(t * 8 + i), 0)) for i in range(4)])
    for i, x in enumerate((-3.6, 0.0, 3.6)):
        ls.sticker(sc, (x, 3.2, -1.0), "ha...", t, start=0.1 + 0.2 * i, size=0.32, color=(230, 230, 230), dy=0.0)
    return sc


def k29(t, dur):
    u = t / dur
    sc = dcam((-5.5 + 1.0 * u, 0.35, 1.8), (4.0, 0.3, -1.0), u, 0.0, fov=40, blur=0)
    ls.festival(sc, t, ladder="broken")
    _crowd(sc, t, ("neutral",))
    return sc


def k30(t, dur):
    u = t / dur
    z = 2.0 + 0.8 * clamp(t / 0.8)
    sc = dfcam((0.0, 0, 2.8), 3.4, 0, u, frac=0.55, fov=40, push=0.1)
    ls.festival(sc, t, ladder="broken")
    character(sc, BENNY, (0.0, 0, z), face="worried", pose=walk(t, 8, 22) if t < 0.8 else None)
    return sc


def k31(t, dur):
    u = t / dur
    sc = dcam((1.3, 3.8, 8.0), (0.0, 2.0, -1.0), u, 0.1, fov=44)
    ls.festival(sc, t, ladder="broken")
    _crowd(sc, t, ("neutral", "suspicious", "neutral"))
    character(sc, BENNY, (0.6, 0, 3.6), yaw=180, face="worried")
    return sc


def k32(t, dur):
    u = t / dur
    pos = (0.0, 0, 2.8)
    sc = head_cu(BENNY, pos, 0, None, u, dist=3.4, up=0.0, side=0.2)
    ls.festival(sc, t, ladder="broken")
    a = character(sc, BENNY, pos, face="stung")
    add_emote(sc, "sweat", a["head_top"], t, size=0.5, dx=-0.5, dy=0.0, start=0.1, hold=2.4)
    h = a["head"]
    ls.pickle(sc, T(*(h + np.array([0.95, -0.3, 0.4]))), s=0.28)
    sc.box(T(*(h + np.array([1.5, -0.75, 0.4]))) @ RZ(50), (0.24, 1.0, 0.24), (214, 156, 118), layer=7)
    return sc


# ------------------------------------------------------------ 33-41: the boots
def k33(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.8, 10.0), (0.0, 2.2, -2.0), u, 0.06, fov=44)
    ls.festival(sc, t, ladder="broken")
    part = clamp(t / 0.6)
    ls.crowd_line(sc, CROWD[:4], [-5.2, -4.0, -2.8 - 0.6 * part, -1.6 - 0.8 * part], -0.5, yaw=40,
                  faces=("shock", "worried"))
    ls.crowd_line(sc, CROWD[4:8], [1.6 + 0.8 * part, 2.8 + 0.6 * part, 4.0, 5.2], -0.5, yaw=-40,
                  faces=("shock", "worried"))
    character(sc, GUS_B, (0.0, 0, -3.5 + t * 1.6), face="suspicious", pose=walk(t, 6, 18))
    return sc


def k34(t, dur):
    """Three quick cuts on the three clanks, each closer."""
    starts = [word_t(34, i, d) for i, d in enumerate((0.08, 0.7, 1.4))]
    k = 0 if t < starts[1] - 0.05 else (1 if t < starts[2] - 0.05 else 2)
    ts = starts[k]
    dist = (5.0, 3.2, 1.9)[k]
    foot = np.array([0.3, 0.0, 0.0])
    sc = dcam(foot + np.array([dist * 0.5, 0.45, dist]), foot + np.array([0, 0.45, 0]), 0, 0, fov=40, blur=0)
    ls.festival(sc, t, ladder="broken")
    lift = max(0.0, 1 - (t - ts) / 0.12) if t >= ts else 1.0
    character(sc, GUS_B, (0.0, 0, -0.2), face="suspicious", pose=dict(lr=-30 * lift, kr=40 * lift, ll=8))
    ls.dust(sc, foot + np.array([0, 0, 0.3]), t, ts + 0.1, n=7)
    return sc


def k35(t, dur):
    u = t / dur
    click = 1.6
    sc = dcam((0.9, 0.7, 3.0), (0.0, 0.6, -0.2), u, 0.12, fov=40)
    ls.festival(sc, t, ladder="broken")
    bend = clamp(t / 0.6)
    character(sc, dict(GUS_B, strap=(56, 52, 50) if t < click else (110, 100, 90)), (0.0, 0, -0.4),
              face="suspicious", pose=dict(lean=38 * bend, al=(60 * bend, -10), ar=(60 * bend, -10), el=30, er=30))
    if click <= t < click + 0.35:
        sparks(sc, (0.3, 0.6, 0.3), t, seed=7, n=4, r=0.2, color=(255, 240, 160))
    return sc


def k36(t, dur):
    u = t / dur
    sc = dcam((0.0, 2.6, 9.0), (0.0, 2.2, -1.0), u, 0.06, fov=44)
    ls.festival(sc, t, ladder="broken")
    k = clamp((t - 0.1) / 0.2)
    crowd = _crowd(sc, t, ("shock", "jaw"), poses=[dict(al=(150 * k, 25), el=70 * k, ar=(20, 6))] * 2)
    for i, a in enumerate(crowd[::2]):
        add_emote(sc, "!", a["head_top"], t, size=0.55, dx=0.3, dy=0.2, start=0.1 + 0.08 * i)
    return sc


GPOS, BPOS = (-0.95, 0, 0.0), (0.95, 0, 0.0)


def k37(t, dur):
    u = t / dur
    sc = head_cu(GUS_B, GPOS, 20, dict(barefoot=True), u, dist=3.6, up=-0.6, fov=36)
    ls.festival(sc, t, ladder="broken")
    character(sc, GUS_B, GPOS, yaw=20, face="neutral", pose=dict(barefoot=True))
    return sc


def _two(sc, t, gface, bface, bpose=None, gpose=None):
    gp = dict(barefoot=True)
    gp.update(gpose or {})
    a = character(sc, GUS_B, GPOS, yaw=70, face=gface, pose=gp)
    b = character(sc, BENNY, BPOS, yaw=-70, face=bface, pose=bpose)
    for i, x in enumerate((-0.7, -0.3)):
        ls.iron_boot(sc, T(-1.9 + x, 0, 0.7) @ RY(40 + 20 * i), s=0.75)
    return a, b


def k38(t, dur):
    u = t / dur
    sc = dcam((0.2, 2.9, 6.6), (0.0, 2.6, 0.0), u, 0.1, fov=40)
    ls.festival(sc, t, ladder="broken")
    _two(sc, t, "neutral", "neutral")
    return sc


def k39(t, dur):
    u = t / dur
    pose = dict(head=(25 * math.sin(t * 11), 0, 0))
    sc = head_cu(BENNY, BPOS, -70, pose, u, dist=3.2, side=-0.3)
    ls.festival(sc, t, ladder="broken")
    a = character(sc, BENNY, BPOS, yaw=-70, face="neutral", pose=pose)
    add_emote(sc, "?", a["head_top"], t, size=0.5, dx=0.5, dy=0.2, start=0.1)
    return sc


def k40(t, dur):
    u = t / dur
    sc = head_cu(GUS_B, GPOS, 70, dict(barefoot=True), u, dist=3.0, side=0.4, fov=34)
    ls.festival(sc, t, ladder="broken")
    a = character(sc, GUS_B, GPOS, yaw=70, face="neutral", pose=dict(barefoot=True))
    ls.moon_cow(sc, a["head"] + np.array([0.4, 1.0, 0.6]), t, start=0.7, hold=1.3, size=0.9)
    return sc


def k41(t, dur):
    u = t / dur
    sc = head_cu(BENNY, BPOS, -70, None, u, dist=4.2, side=-0.2, up=-0.2, fov=38)
    ls.festival(sc, t, ladder="broken")
    character(sc, BENNY, BPOS, yaw=-70, face="neutral")
    ls.tumbleweed(sc, (BPOS[0] - 4.0 + 3.6 * u, 0.5 + 0.2 * abs(math.sin(t * 6)), -3.5), t)
    return sc


# ------------------------------------------------------------ 42-46: lift-off
def k42(t, dur):
    u = t / dur
    sc = head_cu(GUS_B, GPOS, 70, dict(barefoot=True), u, dist=2.7, side=0.4, fov=34)
    ls.festival(sc, t, ladder="broken")
    character(sc, GUS_B, GPOS, yaw=70, face="smirk" if t < 0.45 else "grin",
              pose=dict(barefoot=True, head=(0, -6 + 8 * (t > 0.45), 0)))
    return sc


def k43(t, dur):
    u = t / dur
    rise = 0.3 * u
    pose = dict(laugh_pose(t), barefoot=True)
    sc = head_cu(GUS_B, (GPOS[0], rise, GPOS[2]), 70, pose, u, dist=3.4, side=0.4, fov=36, push=0.15)
    ls.festival(sc, t, ladder="broken")
    a = character(sc, GUS_B, (GPOS[0], rise + bob(t, 0.04), GPOS[2]), yaw=70, face="cry" if int(t * 5) % 2 else "laugh",
                  pose=pose, shadow_y=0)
    ls.sticker(sc, a["head"], "HA HA HA", t, start=0.1, hold=1.6, size=0.5, dx=-0.2, dy=1.0)
    return sc


def k44(t, dur):
    u = t / dur
    rise = 0.4 + 9.0 * u ** 1.6
    sc = dcam((1.8, 0.9, 8.0), (GPOS[0], 2.5 + rise * 0.75, 0.0), u, 0.0, fov=48)
    ls.festival(sc, t, ladder="broken")
    character(sc, GUS_B, (GPOS[0], rise, GPOS[2]), yaw=20, face="laugh", pose=dict(FLOAT, barefoot=True),
              shadow_y=0)
    for x in (-0.25, 0.25):
        ls.iron_boot(sc, T(GPOS[0] + x, 0, 0.2) @ RY(10), s=0.75)
    if t > 0.2:
        speed_lines(sc, t, cx=0.5, cy=0.3, n=22, inner=0.3, alpha=140)
    return sc


def k45(t, dur):
    u = t / dur
    rise = 0.2 + 6.0 * clamp((t - 0.3) / 2.0) ** 1.4
    sc = dcam((BPOS[0] + 2.2, 1.0 + rise * 0.8, 7.0), (BPOS[0], 2.4 + rise, 0.0), u, 0.0, fov=46)
    ls.festival(sc, t, ladder="broken")
    a = character(sc, BENNY, (BPOS[0], rise + bob(t, 0.05), BPOS[2]), face="laugh", pose=dict(FLOAT, **laugh_pose(t)),
                  shadow_y=0)
    ls.music_notes(sc, a["head_top"], t)
    return sc


def k46(t, dur):
    u = t / dur
    tw = ls.TOWER
    c = np.array([tw[0] + 0.2, 11.15, tw[2] + 2.55])
    sc = dcam(c + np.array([0.5, 0.4, 7.6]), c + np.array([0, 1.2, 0.6]), u, 0.08, fov=44)
    ls.festival(sc, t, ladder="broken")
    lift = 0.3 * clamp((t - 0.7) / 0.5)
    head = ls.cat(sc, T(*(c + np.array([0, lift, 0.6]))), t, mood="happy" if t > 0.7 else "scared")
    character(sc, GUS_B, c + np.array([-1.0, -1.6 + bob(t, 0.06), 1.1]), yaw=40, face="joy",
              pose=dict(barefoot=True, ar=(120, -10), al=(150, -30), ll=10, lr=-10), shadow=False)
    character(sc, BENNY, c + np.array([1.0, -1.5 + bob(t + 1, 0.06), 1.1]), yaw=-40, face="joy",
              pose=dict(al=(120, -10), ar=(150, -30), ll=10, lr=-10), shadow=False)
    add_emote(sc, "stars", head, t, size=0.5, dx=0.0, dy=0.4, start=0.8)
    sparks(sc, head, t, seed=3, n=5, r=0.6)
    return sc


# ------------------------------------------------------------ 47-51: the twist
def k47(t, dur):
    u = t / dur
    sc = ncam((0.6, 2.6, 6.6), (0.0, 2.0, -0.4), u, 0.15, fov=40, mood=dict(sky=ps.NIGHT_SKY, night=0.7), bloom=0.8,
              grade="sepia", gmix=0.35)
    ls.garage(sc, boots=True, bulb_x=-1.8)
    sets.chair(sc, 0.0, -0.4, c=(120, 90, 70))
    pose = sit()
    pose.update(laugh_pose(t), al=(60, -10), ar=(60, -10), el=40, er=40, barefoot=True)
    ll = GUS["leg"][1] * GUS["s"]
    up = 0.25 + bob(t, 0.06, 5)
    a = character(sc, GUS_B, (0.0, 0.86 - ll + up, -0.35), face="laugh", pose=pose, shadow=False)
    for y in (1.4, 1.9):  # rope round Gus and the chair
        sc.box(T(0, y + up * 0.5, -0.35), (1.25, 0.08, 0.85), (200, 170, 110), layer=6)
    ls.joke_book(sc, T(*((a["hand_l"] + a["hand_r"]) / 2 + np.array([0, 0.05, 0.15]))) @ RX(-60), open_k=1.0)
    ls.sticker(sc, a["head"], "HA HA", t, start=0.3, hold=1.2, size=0.45, dx=0.9, dy=0.6)
    ls.sticker(sc, a["head"], "HA!", t, start=2.2, hold=1.2, size=0.45, dx=-0.9, dy=0.7)
    return sc


def k48(t, dur):
    u = t / dur
    sc = ncam((1.8, 1.2, 4.6), (-1.0, 0.7, 1.0), u, 0.0, fov=40, mood=dict(sky=ps.NIGHT_SKY, night=0.7), bloom=0.8)
    ls.garage(sc, boots=False)
    for i in range(9):
        ls.joke_book(sc, T(-1.4 + 0.08 * math.sin(i * 2), i * 0.17, 1.0) @ RY(12 * math.sin(i * 1.7)),
                     title=("JOKES", "MORE JOKES", "PUNS", "KNOCK KNOCK")[i % 4],
                     color=((230, 80, 70), (90, 160, 230), (250, 200, 70), (120, 200, 120))[i % 4])
    ls.iron_boot(sc, T(-0.2, 0, 1.6) @ RY(-20), s=0.8)
    ls.iron_boot(sc, T(0.45, 0, 1.4) @ RY(-35), s=0.8, text="14")
    return sc


def k49(t, dur):
    u = t / dur
    sc = dcam((0.4, 6.4, 7.6), (0.0, 6.2, 0.0), u, 0.12, fov=40)
    sets.clouds(sc, seed=6, n=9, z=-40)
    a = character(sc, GUS_B, (-0.9, 3.6 + bob(t, 0.08), 0.0), yaw=40, face="smile",
                  pose=dict(barefoot=True, al=(20, 20), ar=(90, -20), ll=8, lr=-8), shadow=False)
    character(sc, BENNY, (0.9, 3.7 + bob(t + 1.3, 0.08), 0.0), yaw=-40, face="joy",
              pose=dict(al=(90, -20), ar=(20, 20), ll=8, lr=-8), shadow=False)
    return sc


def k50(t, dur):
    u = t / dur
    sc = dcam((0.3, 3.2, 5.6), (0.6, 2.6, -0.6), u, 0.08, fov=44)
    ls.dining(sc)
    rise = 0.7 * clamp(t / 0.6)
    f = _family_table(sc, t, dict(dad="grin", mom="grin", benny="laugh", gus="laugh"), rise=rise, laugh=True)
    ls.music_notes(sc, f["benny"]["head_top"], t)
    ls.music_notes(sc, f["gus"]["head_top"], t + 0.4)
    return sc


def k51(t, dur):
    u = t / dur
    sc = dcam((0.0, 1.2, 6.0), (0.0, 3.4, -0.5), u, 0.05, fov=48)
    ls.dining(sc, lamp=False)
    ceil = 4.4
    for j, (spec, x) in enumerate(((DAD_B, -2.1), (MOM_B, -0.7), (BENNY, 0.7), (GUS_B, 2.1))):
        hat = 0.62 * spec["s"] if spec is BENNY else (0.4 * spec["s"] if spec in (DAD_B,) else 0.2 * spec["s"])
        y = ceil - ht(spec) - hat + 0.02 * math.sin(t * 15 + j)
        a = character(sc, spec, (x, y, -0.6 + 0.3 * (j % 2)), face="laugh", pose=dict(FLOAT, **laugh_pose(t + j)),
                      shadow=False)
        if t < 0.5:
            add_emote(sc, "stars", a["head_top"], t, size=0.45, dy=-0.1, hold=0.5)
    return sc


_FNS = [globals()[f"k{i:02d}"] for i in range(1, len(LINES) + 1)]
SHOTS = [(i + 1, 1.4, txt, fn) for i, (txt, fn) in enumerate(zip(LINES, _FNS))]
SHOTS, WORD_TIMES = load_timing(SHOTS, TIMING_FILE)
WT.update(WORD_TIMES)
