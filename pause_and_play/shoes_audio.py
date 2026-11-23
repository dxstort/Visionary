"""Music and effects for The Walking Shoes (all synthesised), mixed under the voice.

    STORY=shoes python3 shoes_audio.py --voice out/shoes__voice_pre.wav   -> out/shoes_mix.wav

Bouncy music for the first part (to shot 14), soft piano on the porch, silence when the last piece goes
in (26), soft piano for the reveal, a heartbeat for the shootout, a big roar and music on the save (42),
hard cut to silence.
"""
import os
import sys

os.environ.setdefault("STORY", "shoes")
import numpy as np  # noqa: E402

import audio  # noqa: E402
import laughs_audio  # noqa: E402
import robot_audio as ra  # noqa: E402
import umbrella_audio as ua  # noqa: E402
import wish_audio as wa  # noqa: E402
from audio import SR, at, crunch, ding, env, hp, lp, noise, pop, sparkle, t_axis, thud, whoosh  # noqa: E402
from laughs_audio import cricket, meow  # noqa: E402
from story import SHOTS  # noqa: E402

_bounce = laughs_audio._bed


def footsteps(n=6, gap=0.3, f=160):
    out = np.zeros(int((n * gap + 0.2) * SR))
    for i in range(n):
        s = thud(f, 0.08)
        o = int(i * gap * SR)
        out[o:o + len(s)] += s * (0.7 + 0.3 * (i % 2))
    return out


def lace():
    return hp(noise(0.35), 0.5) * env(int(0.35 * SR), 0.02, 0.15) * 0.5


def door_bell():
    return ding(2600) * 0.6


def quack():
    out = []
    for k in range(2):
        t = t_axis(0.15)
        f = 600 - 300 * t
        ph = 2 * np.pi * np.cumsum(f) / SR
        out += [lp(np.sign(np.sin(ph)), 0.3) * env(len(t), 0.005, 0.08) * 0.4, np.zeros(int(0.08 * SR))]
    return np.concatenate(out)


def creak(d=0.9):
    return wa.creak()


def click():
    return hp(noise(0.03), 0.4) * env(int(0.03 * SR), 0.0005, 0.008) * 0.9


def heartbeat(n=3):
    return wa.heartbeat(n, 0.7)


def skid():
    d = 0.8
    t = t_axis(d)
    return np.sin(2 * np.pi * (1400 - 600 * t) * t) * (0.5 + 0.5 * hp(noise(d), 0.3)) * np.minimum(1, (d - t) / 0.1) * 0.2


def shoes_cues():
    c = []
    add = lambda shot, t, snd, g=1.0: c.append((at(shot, t), snd, g))
    add(1, 0.6, lace(), 0.7)
    add(2, 0.0, footsteps(6, 0.3), 0.5)
    add(2, 0.1, sparkle(), 0.5)
    add(3, 0.0, whoosh(1.0, up=False), 0.6)
    add(4, 1.8, door_bell(), 0.6)
    add(5, 0.3, crunch(0.15), 0.6)
    add(5, 0.8, crunch(0.15), 0.6)
    add(6, 1.85, ra.splash(), 1.0)
    add(7, 0.3, quack(), 0.8)
    add(8, 0.0, footsteps(7, 0.32), 0.4)
    add(9, 0.3, cricket(1.2), 0.7)
    for k in range(3):
        add(10, 0.2 + k * 0.4, thud(200, 0.1), 0.5)
    k_times = [0.0, 0.8, 1.6]
    for k in k_times:
        add(12, k + 0.05, ding(1760), 0.4)
    add(13, 0.6, ua.groan() * 0.6, 0.6)
    add(14, 0.2, creak(), 0.6)
    add(16, 1.0, click(), 0.6)
    for k in range(3):
        add(17, 0.05 + k * 0.6, click(), 0.6)
    add(18, 1.0, wa.yawn(), 0.6)
    add(20, 0.0, audio.cheer(1.8), 0.6)
    add(21, 0.3, lace(), 0.7)
    add(22, 1.2, wa.zip_() * 0.0, 0.0)
    add(23, 0.1, wa.scratch(), 0.8)
    add(24, 0.6, ua.groan() * 0.6, 0.6)
    add(25, 0.2, skid(), 0.8)
    add(26, 0.5, sparkle(), 0.4)
    add(27, 0.55, click(), 1.0)
    add(27, 0.6, sparkle(), 0.6)
    add(28, 0.2, ding(2093), 0.4)
    add(29, 0.3, audio.cheer(2.5) * 0.25, 0.4)
    add(30, 0.2, ding(1568), 0.6)
    add(32, 0.2, crunch(0.3), 0.4)
    add(33, 0.4, sparkle(), 0.5)
    add(36, 0.2, whoosh(0.6, up=True), 0.7)
    add(36, 0.3, wa.keys(wa.hz(72), 1.0) + wa.keys(wa.hz(76), 1.0), 0.6)
    add(37, 0.0, whoosh(0.8, up=False), 0.8)
    add(38, 0.3, audio.cheer(1.5), 0.6)
    add(39, 0.0, heartbeat(2), 0.9)
    add(40, 0.0, heartbeat(2), 1.0)
    add(41, 0.0, whoosh(0.9, up=False), 0.8)
    add(42, 0.0, thud(70, 0.4), 1.0)
    add(42, 0.02, audio.cheer(2.5), 1.0)
    add(43, 0.0, audio.cheer(1.2), 0.7)
    add(46, 0.4, sparkle(), 0.5)
    return c


def gains(total):
    n = int(total * SR)
    tt = np.arange(n) / SR
    bounce, piano = np.zeros(n), np.zeros(n)

    def span(s0, s1):
        a = at(s0, 0)
        b = at(s1, 0) if s1 <= len(SHOTS) else total
        return (tt >= a) & (tt < b)

    bounce[span(1, 15)] = 1.0
    piano[span(15, 20)] = 0.75
    bounce[span(20, 26)] = 0.8
    piano[span(28, 36)] = 0.7
    bounce[span(36, 39)] = 0.8
    bounce[span(42, 47)] = 1.15
    m = int(0.35 * SR)
    sm = lambda g: np.convolve(g, np.ones(m) / m, mode="same")
    return sm(bounce), sm(piano)


def shoes_bed(total):
    bed, hum = _bounce(total)
    pb = wa.piano_bed(total)
    pb *= np.sqrt(np.mean(bed ** 2)) / max(1e-6, np.sqrt(np.mean(pb ** 2)))
    gb, gp = gains(total)
    return bed * gb + pb * gp, hum


audio.music_bed = shoes_bed
audio.PAUSED = []
audio.cues = shoes_cues
audio.MUSIC_DB_VOICE = -15

if __name__ == "__main__":
    sys.exit(audio.main())
