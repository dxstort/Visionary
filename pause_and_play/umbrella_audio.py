"""Music and effects for The Weather Umbrella (all synthesised), mixed under the voice.

    STORY=umbrella python3 umbrella_audio.py --voice out/umbrella__voice_pre.wav   -> out/umbrella_mix.wav

Bouncy music for the first part (to shot 14), soft piano for Omar's part, silence at "It wasn't." (29),
thunder on "RAIN!", a big happy swell when it rains (37), hard cut to silence.
"""
import os
import sys

os.environ.setdefault("STORY", "umbrella")
import numpy as np  # noqa: E402

import audio  # noqa: E402
import laughs_audio  # noqa: E402
import robot_audio as ra  # noqa: E402
import wish_audio as wa  # noqa: E402
from audio import SR, at, crunch, ding, env, hp, lp, noise, pop, sparkle, t_axis, thud, whoosh  # noqa: E402
from laughs_audio import cricket, ha  # noqa: E402
from story import SHOTS  # noqa: E402

_bounce = laughs_audio._bed


def thunder(d=2.5, vol=1.0):
    t = t_axis(d)
    x = lp(noise(d), 0.02) * 3.0 + lp(noise(d), 0.08) * np.exp(-t / 0.25)
    return x * np.minimum(1, t / 0.03) * np.exp(-t / (d * 0.5)) * vol


def rain_noise(d=3.0, vol=1.0):
    t = t_axis(d)
    return hp(noise(d), 0.6) * 0.35 * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4) * vol


def drumroll(d=2.0):
    t = t_axis(d)
    hits = (np.sin(2 * np.pi * 18 * t) > 0.7).astype(float)
    return lp(noise(d), 0.3) * hits * np.minimum(1, t / d + 0.3) * 0.6


def cymbal():
    return hp(noise(1.2), 0.8) * env(int(1.2 * SR), 0.002, 0.4) * 0.5


def wind(d=2.0):
    t = t_axis(d)
    return lp(noise(d), 0.03) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t)) * 0.6


def barks(n=5):
    out = np.zeros(int((n * 0.22 + 0.5) * SR))
    for i in range(n):
        b = wa.bark()
        o = int(i * 0.22 * SR)
        out[o:o + len(b)] += b[: len(out) - o] * (0.6 + 0.4 * (i % 2))
    return out


def groan():
    d = 1.2
    t = t_axis(d)
    out = np.zeros(len(t))
    for f0 in (140, 170, 200):
        f = f0 - 40 * t
        ph = 2 * np.pi * np.cumsum(f) / SR
        out += lp(np.sign(np.sin(ph)), 0.1) * 0.15
    return out * np.sin(np.pi * t / d)


def breath():
    d = 1.0
    t = t_axis(d)
    return hp(noise(d), 0.5) * np.sin(np.pi * t / d) ** 2 * 0.25


def shimmer(d=2.0):
    out = np.zeros(int(d * SR))
    for i in range(8):
        s = sparkle()
        o = int(i * d / 8 * SR)
        out[o:o + len(s)] += s[: len(out) - o] * 0.5
    return out


def umbrella_cues():
    c = []
    add = lambda shot, t, snd, g=1.0: c.append((at(shot, t), snd, g))
    add(1, 0.2, sparkle(), 0.6)
    add(1, 0.3, ding(1568), 0.5)
    add(2, 0.1, whoosh(1.0, up=True), 0.6)
    add(2, 0.8, thunder(1.5, 0.5), 0.6)
    add(3, 0.0, wind(1.8), 0.7)
    add(4, 0.6, ha(260, 2, 0.12, 0.1), 0.6)
    add(5, 0.3, wa.sizzle(1.0) * 0.3, 0.5)
    add(6, 0.3, barks(4), 0.6)
    add(7, 0.0, barks(10), 0.7)
    add(8, 0.2, breath(), 0.7)
    add(9, 0.3, drumroll(2.2), 0.7)
    add(10, 0.05, cymbal(), 0.8)
    add(12, 0.0, audio.cheer(1.4), 0.5)
    for k in range(3):
        add(13, k * 0.6, pop(800 + 150 * k), 0.6)
    add(14, 0.1, ha(220, 3, 0.12, 0.09), 0.5)
    add(17, 0.0, wind(1.9), 0.6)
    add(18, 0.0, wind(1.2), 0.6)
    add(19, 0.3, crunch(0.15), 0.6)
    for k in range(3):
        add(20, k * 0.7 + 0.1, pop(900 + 100 * k), 0.5)
    add(22, 0.3, ding(1760), 0.5)
    add(23, 0.2, whoosh(1.5, up=False), 0.5)
    for k in range(6):
        add(24, 0.1 + k * 0.38, thud(150, 0.08), 0.3)
    add(25, 0.0, ra.engine(3.2, rev=False) * 0.4, 0.5)
    add(26, 0.0, wind(2.3), 0.7)
    add(30, 0.2, wa.drone(1.4) * 0.6, 0.6)
    add(31, 0.1, breath(), 0.9)
    add(32, 0.15, whoosh(0.4, up=True), 0.9)
    add(33, 0.05, thunder(2.5, 1.0), 1.0)
    add(34, 0.2, groan(), 0.8)
    add(36, 0.3, thunder(3.0, 0.6), 0.9)
    add(37, 0.0, rain_noise(6.0), 1.0)
    add(38, 0.0, rain_noise(3.0), 0.7)
    add(39, 0.2, shimmer(2.0), 0.6)
    starts = [0.0] + [w[0] for w in (laughs_audio.WORD_TIMES if False else [])]
    for k in range(3):
        add(40, 0.1 + k * 1.2, pop(700 + 200 * k), 0.8)
    add(41, 0.85, thud(110, 0.25), 0.8)
    add(42, 0.0, ra.engine(2.4, rev=True) * 0.5, 0.5)
    add(42, 1.2, audio.cheer(1.2), 0.5)
    add(44, 0.0, audio.cheer(2.0) * 0.4, 0.4)
    add(46, 0.3, crunch(0.2), 0.9)
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
    piano[span(15, 29)] = 0.75
    piano[span(30, 33)] = 0.4
    bounce[span(37, 47)] = 1.15
    m = int(0.35 * SR)
    sm = lambda g: np.convolve(g, np.ones(m) / m, mode="same")
    return sm(bounce), sm(piano)


def umbrella_bed(total):
    bed, hum = _bounce(total)
    pb = wa.piano_bed(total)
    pb *= np.sqrt(np.mean(bed ** 2)) / max(1e-6, np.sqrt(np.mean(pb ** 2)))
    gb, gp = gains(total)
    return bed * gb + pb * gp, hum


audio.music_bed = umbrella_bed
audio.PAUSED = []
audio.cues = umbrella_cues
audio.MUSIC_DB_VOICE = -15

if __name__ == "__main__":
    sys.exit(audio.main())
