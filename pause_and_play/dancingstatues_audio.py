"""Music and effects for When Secrets Make Statues Dance (all synthesised), mixed under the voice.

    STORY=dancingstatues python3 dancingstatues_audio.py --voice out/dancingstatues__voice_pre.wav
        -> out/dancingstatues_mix.wav

Bouncy music for the town part, a nervous soft piano backstage, silence when the balls drop, a stone
"crack and groove" each time a statue starts to dance, a big beat for the square, piano for the quiet
night ending, hard cut to silence.
"""
import os
import sys

os.environ.setdefault("STORY", "dancingstatues")
import numpy as np  # noqa: E402

import audio  # noqa: E402
import laughs_audio  # noqa: E402
import robot_audio as ra  # noqa: E402
import wish_audio as wa  # noqa: E402
from audio import SR, at, crunch, ding, env, hp, lp, noise, pop, sparkle, t_axis, thud, whoosh  # noqa: E402
from story import SHOTS  # noqa: E402

_bounce = laughs_audio._bed


def stone_crack():
    """A statue coming to life: grinding stone, then a bright pop."""
    s = lp(noise(0.5), 0.2) * env(int(0.5 * SR), 0.01, 0.3) * 0.7
    return np.concatenate([s, sparkle() * 0.8])


def groove(n=6, gap=0.25):
    out = np.zeros(int((n * gap + 0.3) * SR))
    for i in range(n):
        s = thud(90 if i % 2 == 0 else 130, 0.1)
        o = int(i * gap * SR)
        out[o:o + len(s)] += s * (0.9 if i % 2 == 0 else 0.6)
    return out


def coo():
    d = 0.3
    t = t_axis(d)
    return np.sin(2 * np.pi * (420 + 60 * np.sin(t * 40)) * t) * env(len(t), 0.02, 0.15) * 0.3


def flap():
    return hp(noise(0.5), 0.3) * (0.5 + 0.5 * np.sin(np.arange(int(0.5 * SR)) / SR * 60)) * env(int(0.5 * SR), 0.02, 0.3) * 0.5


def hop():
    return thud(260, 0.08) * 0.8


def boing():
    d = 0.25
    t = t_axis(d)
    return np.sin(2 * np.pi * (300 + 600 * t) * t) * env(len(t), 0.005, 0.2) * 0.4


def knees():
    out = np.zeros(int(1.2 * SR))
    for i in range(8):
        s = thud(170, 0.05)
        o = int(i * 0.15 * SR)
        out[o:o + len(s)] += s * 0.5
    return out


def dancing_cues():
    c = []
    add = lambda shot, t, snd, g=1.0: c.append((at(shot, t), snd, g))
    add(1, 0.2, stone_crack(), 0.6)
    add(2, 0.3, stone_crack(), 0.9)
    add(3, 0.8, ding(880), 0.3)
    add(4, 1.2, pop(), 0.6)
    add(5, 0.1, stone_crack(), 0.7)
    add(5, 0.7, ra.splash(), 0.9)
    add(6, 1.4, sparkle(), 0.3)
    add(7, 0.2, stone_crack(), 0.7)
    add(7, 0.9, whoosh(0.6, up=True), 0.6)
    add(8, 0.2, ra.splash() * 0.4, 0.5)
    add(9, 0.1, stone_crack(), 0.7)
    add(9, 0.7, groove(4), 0.5)
    add(10, 0.4, audio.cheer(1.2) * 0.3, 0.4)
    for k in range(5):
        add(11, 0.3 + k * 0.3, pop(), 0.35)
    add(12, 0.3, thud(200, 0.1), 0.6)
    add(12, 1.0, thud(160, 0.1), 0.5)
    add(13, 0.2, sparkle(), 0.5)
    add(14, 0.1, whoosh(0.5, up=True), 0.4)
    add(15, 0.3, groove(5), 0.4)
    add(15, 1.8, laughs_audio.cricket(1.2), 0.7)
    add(16, 0.6, ding(300), 0.4)
    add(17, 0.1, knees(), 0.7)
    add(18, 0.5, ding(1568), 0.4)
    add(19, 0.8, thud(220, 0.1), 0.7)
    add(20, 0.4, thud(220, 0.1), 0.7)
    add(20, 1.3, thud(220, 0.1), 0.7)
    add(20, 2.4, thud(120, 0.2), 0.9)
    add(21, 0.2, laughs_audio.cricket(1.5), 0.8)
    add(21, 1.1, coo(), 0.8)
    add(22, 0.1, sparkle(), 0.5)
    add(23, 0.5, wa.heartbeat(2, 0.7), 0.8)
    add(24, 0.1, whoosh(0.8, up=False), 0.5)
    add(25, 0.2, whoosh(0.5, up=True), 0.4)
    add(26, 0.3, wa.heartbeat(2, 0.7), 0.7)
    add(27, 0.4, flap(), 0.9)
    add(27, 1.2, stone_crack(), 0.7)
    add(28, 0.2, stone_crack(), 0.9)
    add(28, 0.5, groove(6), 0.8)
    add(29, 0.0, groove(6), 0.9)
    add(29, 0.1, sparkle(), 0.7)
    add(30, 0.0, audio.cheer(2.2), 0.9)
    add(31, 0.4, ding(330), 0.3)
    add(32, 0.5, sparkle(), 0.3)
    add(33, 0.2, stone_crack(), 0.7)
    for k in range(3):
        add(33, 0.5 + k * 0.5, hop(), 0.8)
    add(34, 0.3, pop(), 0.5)
    add(35, 0.0, groove(6), 0.9)
    add(35, 0.2, audio.cheer(2.0), 0.7)
    add(36, 0.1, audio.cheer(1.5), 0.8)
    add(37, 0.1, ding(1760), 0.4)
    add(38, 0.2, ding(1319), 0.4)
    add(39, 0.6, boing(), 0.7)
    add(39, 1.4, laughs_audio.cricket(1.2), 0.6)
    add(40, 0.4, sparkle(), 0.3)
    add(41, 0.4, crunch(0.15), 0.7)
    add(42, 0.9, ding(2093), 0.6)
    add(42, 0.9, sparkle(), 0.6)
    add(43, 0.2, sparkle(), 0.3)
    add(44, 0.7, stone_crack(), 1.0)
    add(44, 1.0, groove(4), 0.9)
    return c


def gains(total):
    n = int(total * SR)
    tt = np.arange(n) / SR
    bounce, piano = np.zeros(n), np.zeros(n)

    def span(s0, s1):
        a = at(s0, 0)
        b = at(s1, 0) if s1 <= len(SHOTS) else total
        return (tt >= a) & (tt < b)

    bounce[span(1, 17)] = 1.0
    piano[span(17, 19)] = 0.6
    piano[span(22, 27)] = 0.7
    bounce[span(27, 40)] = 1.15
    piano[span(40, 44)] = 0.7
    bounce[span(44, 45)] = 1.1
    m = int(0.35 * SR)
    sm = lambda g: np.convolve(g, np.ones(m) / m, mode="same")
    return sm(bounce), sm(piano)


def statues_bed(total):
    bed, hum = _bounce(total)
    pb = wa.piano_bed(total)
    pb *= np.sqrt(np.mean(bed ** 2)) / max(1e-6, np.sqrt(np.mean(pb ** 2)))
    gb, gp = gains(total)
    return bed * gb + pb * gp, hum


audio.music_bed = statues_bed
audio.PAUSED = []
audio.cues = dancing_cues
audio.MUSIC_DB_VOICE = -15

if __name__ == "__main__":
    sys.exit(audio.main())
