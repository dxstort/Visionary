"""Music and effects for The Toaster Robot (all synthesised), mixed under the voice.

    STORY=robot python3 robot_audio.py --voice out/robot__voice_pre.wav   -> out/robot_mix.wav

Bouncy music until the necklace snaps (34), stopped from Kip freezing (36), soft piano back when Crumbs
returns the medal (42), the bouncy music swells when Kip hands over the wrench (48), hard cut to silence.
"""
import os
import sys

os.environ.setdefault("STORY", "robot")
import numpy as np  # noqa: E402

import audio  # noqa: E402
import laughs_audio  # noqa: E402
import wish_audio as wa  # noqa: E402
from audio import SR, at, crunch, ding, env, hp, lp, noise, pop, sparkle, t_axis, thud, whoosh  # noqa: E402
from laughs_audio import clank, cricket, ha, meow, trombone  # noqa: E402
from story import SHOTS  # noqa: E402

_bounce = laughs_audio._bed


def beep(f=1400, d=0.12, n=1, gap=0.16):
    out = np.zeros(int((n * gap + d) * SR))
    for i in range(n):
        t = t_axis(d)
        b = np.sign(np.sin(2 * np.pi * (f + 200 * (i % 2)) * t)) * env(len(t), 0.002, 0.06) * 0.2
        o = int(i * gap * SR)
        out[o:o + len(b)] += b
    return out


def vacuum(d=1.0, vol=1.0):
    t = t_axis(d)
    x = lp(noise(d), 0.25) * 0.8 + np.sin(2 * np.pi * (180 + 40 * t) * t) * 0.2
    return x * np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.15) * 0.5 * vol


def engine(d=1.0, rev=True):
    t = t_axis(d)
    f = 60 + (120 * t / d if rev else 40)
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1.0) - 1
    return lp(saw, 0.2) * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.1) * 0.5


def mower(d=1.4):
    t = t_axis(d)
    saw = 2 * ((45 * t) % 1.0) - 1
    return lp(saw + 0.3 * noise(d), 0.15) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * t)) * 0.4


def buzz(d=1.2):
    t = t_axis(d)
    return np.sign(np.sin(2 * np.pi * 120 * t)) * lp(np.ones_like(t), 0.5) * 0.12


def tape():
    return hp(noise(0.3), 0.4) * env(int(0.3 * SR), 0.01, 0.12) * 0.6


def toaster_ding():
    a = ding(2200) * 0.8
    b = clank(900, 0.3) * 0.3
    a[:len(b)] += b[:len(a)]
    return a


def squeak(d=0.4):
    t = t_axis(d)
    return np.sin(2 * np.pi * (900 + 300 * np.sin(2 * np.pi * 3 * t)) * t) * np.minimum(1, (d - t) / 0.1) * 0.15


def shush():
    return hp(noise(0.7), 0.85) * env(int(0.7 * SR), 0.05, 0.3) * 0.5


def horn():
    d = 0.9
    t = t_axis(d)
    x = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (440, 554, 659))
    return lp(x, 0.3) * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.08) * 0.25


def splash():
    return lp(noise(0.5), 0.2) * env(int(0.5 * SR), 0.005, 0.15) * 0.8


def kazoo():
    d = 0.5
    t = t_axis(d)
    return np.sign(np.sin(2 * np.pi * 330 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 25 * t)) * \
        np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.08) * 0.12


def aww():
    d = 1.2
    t = t_axis(d)
    f = 300 - 60 * t
    ph = 2 * np.pi * np.cumsum(f) / SR
    return lp(np.sign(np.sin(ph)) + 0.5 * np.sign(np.sin(1.5 * ph)), 0.12) * np.sin(np.pi * t / d) * 0.25


def bell():
    a, b = ding(988) * 0.7, ding(784) * 0.7
    out = np.zeros(int(0.25 * SR) + max(len(a), len(b)))
    out[:len(a)] += a
    out[int(0.25 * SR):int(0.25 * SR) + len(b)] += b
    return out


def robot_cues():
    c = []
    add = lambda shot, t, snd, g=1.0: c.append((at(shot, t), snd, g))
    for k in range(4):
        add(1, 0.2 + k * 0.4, clank(600 + 90 * k, 0.25), 0.3)
    add(2, 0.5, tape(), 0.7)
    add(2, 0.5, sparkle(), 0.3)
    add(3, 0.4, ding(1046), 0.4)
    add(3, 0.6, beep(1200, 0.2, 3, 0.12), 0.7)
    add(4, 0.3, engine(0.9), 0.7)
    add(5, 0.0, whoosh(1.0, up=True), 0.8)
    add(6, 0.2, wa.drone(1.4), 0.4)
    for k in range(5):
        add(7, 0.2 + k * 0.28, pop(600 + 60 * k), 0.6)
    add(8, 0.4, mower(1.6), 0.6)
    add(9, 0.0, buzz(1.5), 0.7)
    add(10, 0.3, trombone(), 0.5)
    add(11, 0.05, sparkle(), 0.4)
    add(13, 0.25, thud(120, 0.25), 0.8)
    add(13, 0.27, clank(700, 0.3), 0.4)
    add(14, 0.2, vacuum(0.9), 0.6)
    add(15, 0.15, tape(), 0.6)
    add(15, 0.75, tape(), 0.6)
    add(16, 0.3, beep(1500, 0.1), 0.8)
    add(17, 0.2, toaster_ding(), 0.8)
    add(18, 0.3, beep(1300, 0.1, 3, 0.13), 0.6)
    add(19, 0.3, squeak(0.8), 0.6)
    add(20, 0.1, beep(1800, 0.25, 2, 0.3), 0.9)
    add(20, 0.5, shush(), 0.8)
    add(21, 0.0, vacuum(2.2), 0.9)
    add(21, 1.5, meow(scared=True), 0.5)
    add(22, 1.6, ding(1760), 0.4)
    for s, t0 in ((23, 0.45), (24, 0.35), (25, 1.4)):
        add(s, t0, pop(1100), 0.8)
    add(25, 0.2, vacuum(1.0), 0.5)
    for k in range(4):
        add(26, 0.5 + k * 0.6, pop(900 + 100 * k), 0.5)
        add(26, 0.55 + k * 0.6, beep(1600, 0.08), 0.4)
    add(27, 0.0, audio.cheer(1.8), 0.6)
    add(28, 0.3, ding(1568), 0.6)
    add(28, 0.35, sparkle(), 0.4)
    add(29, 0.1, ha(220, 5, 0.13, 0.09), 0.6)
    add(30, 0.95, toaster_ding(), 0.8)
    add(31, 0.05, horn(), 0.9)
    add(32, 0.0, engine(1.8), 0.9)
    add(32, 0.1, whoosh(1.2, up=False), 0.6)
    add(33, 1.4, squeak(0.4), 0.7)
    add(34, 1.8, crunch(0.06), 0.9)
    add(35, 0.5, clank(1800, 0.3), 0.6)
    add(35, 0.9, splash(), 0.6)
    add(37, 0.3, wa.keys(wa.hz(64), 2.0, 1.0), 0.8)
    add(38, 0.0, engine(2.5, rev=False), 0.5)
    add(39, 0.1, squeak(0.5), 0.8)
    add(41, 0.0, vacuum(1.0, 1.6), 1.0)
    add(42, 1.5, pop(1000), 0.8)
    add(42, 1.5, sparkle(), 0.5)
    add(43, 0.6, kazoo(), 0.8)
    add(44, 0.2, cricket(1.2), 0.7)
    add(45, 0.4, aww(), 0.7)
    for k in range(5):
        add(47, 0.1 + k * 0.28, thud(180, 0.08), 0.3)
    add(47, 1.6, sparkle(), 0.4)
    add(48, 0.3, audio.cheer(1.5), 0.7)
    add(48, 0.3, sparkle(), 0.5)
    add(49, 0.2, bell(), 0.6)
    add(51, 0.6, pop(1100), 0.8)
    add(51, 0.6, beep(1500, 0.08, 2, 0.12), 0.5)
    return c


def gains(total):
    n = int(total * SR)
    tt = np.arange(n) / SR
    bounce, piano = np.zeros(n), np.zeros(n)

    def span(s0, s1):
        a = at(s0, 0)
        b = at(s1, 0) if s1 <= len(SHOTS) else total
        return (tt >= a) & (tt < b)

    bounce[span(1, 34)] = 1.0
    bounce[span(34, 36)] = 0.5
    piano[span(42, 48)] = 0.7
    bounce[span(48, 52)] = 1.15
    m = int(0.35 * SR)
    sm = lambda g: np.convolve(g, np.ones(m) / m, mode="same")
    return sm(bounce), sm(piano)


def robot_bed(total):
    bed, hum = _bounce(total)
    pb = wa.piano_bed(total)
    pb *= np.sqrt(np.mean(bed ** 2)) / max(1e-6, np.sqrt(np.mean(pb ** 2)))
    gb, gp = gains(total)
    return bed * gb + pb * gp, hum


audio.music_bed = robot_bed
audio.PAUSED = []
audio.cues = robot_cues
audio.MUSIC_DB_VOICE = -15

if __name__ == "__main__":
    sys.exit(audio.main())
