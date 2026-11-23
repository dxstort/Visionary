"""Music and effects for The Floating Laughs (all synthesised), mixed under the voice.

    STORY=laughs python3 laughs_audio.py --voice out/laughs__voice_pre.wav   -> out/laughs_mix.wav

Music: bouncy for the first half, low under Grandpa's intro, near silence for shots 31-43 so the joke
lands, back big at lift-off (44), hard cut to silence at the end.
"""
import os
import sys

os.environ.setdefault("STORY", "laughs")
import numpy as np  # noqa: E402

import audio  # noqa: E402
from audio import SR, at, crunch, ding, env, hp, lp, noise, pop, sparkle, t_axis, thud, whoosh  # noqa: E402
from story import WORD_TIMES  # noqa: E402


def ha(f=260, n=4, gap=0.13, d=0.09, vol=0.5):
    """Laugh: 'ha' pulses, a buzzy voice through a vowel-ish formant, pitch falling."""
    out = np.zeros(int((n * gap + 0.2) * SR))
    for i in range(n):
        t = t_axis(d)
        ff = f * (1.0 - 0.04 * i) * (1 + 0.05 * np.sin(2 * np.pi * 30 * t))
        saw = 2 * ((ff * t) % 1.0) - 1
        v = lp(saw, 0.25) * env(len(t), 0.005, 0.05)
        o = int(i * gap * SR)
        out[o:o + len(v)] += v * vol
    return out


def meow(scared=False):
    d = 0.6 if not scared else 0.8
    t = t_axis(d)
    f = (700 + 300 * np.sin(np.pi * t / d)) * (1.3 if scared else 1.0) * (1 + 0.02 * np.sin(2 * np.pi * 8 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
    return x * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.15) * 0.25


def clank(f=420, d=0.6, vol=0.6):
    t = t_axis(d)
    x = sum(a * np.sin(2 * np.pi * f * r * t) for r, a in ((1, 1.0), (2.76, 0.6), (5.4, 0.4), (8.9, 0.25)))
    return (x * env(len(t), 0.001, 0.18) + hp(noise(d), 0.5) * env(len(t), 0.001, 0.02) * 0.6) * vol * 0.4


def cricket(d=1.2):
    t = t_axis(d)
    chirp = (np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 28 * t) > 0) * (np.sin(2 * np.pi * 2.2 * t) > 0.3))
    return chirp * 0.08


def trombone():
    out = []
    for m, d in ((58, 0.3), (57, 0.3), (56, 0.3), (55, 0.9)):
        t = t_axis(d)
        f = 440 * 2 ** ((m - 69) / 12) * (1 + (0.03 * np.sin(2 * np.pi * 5 * t) if d > 0.5 else 0))
        saw = 2 * ((f * t) % 1.0) - 1
        out.append(lp(saw, 0.3) * np.minimum(1, t / 0.04) * np.minimum(1, (d - t) / 0.08) * 0.35)
    return np.concatenate(out)


def moo():
    d = 1.0
    t = t_axis(d)
    f = 120 - 30 * t
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1.0) - 1
    return lp(saw, 0.15) * np.minimum(1, t / 0.1) * np.minimum(1, (d - t) / 0.2) * 0.6


def snort():
    return lp(noise(0.18), 0.08) * env(int(0.18 * SR), 0.01, 0.06) * 1.6


def squeal(d=0.5):
    t = t_axis(d)
    return np.sin(2 * np.pi * (2400 + 600 * t) * t) * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.1) * 0.15


def whisper(d=1.6):
    t = t_axis(d)
    return hp(noise(d), 0.7) * (0.5 + 0.5 * np.sin(2 * np.pi * 3.3 * t) ** 2) * 0.12


def rumble(d=1.0):
    t = t_axis(d)
    return lp(noise(d), 0.05) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t)) * 0.9


def crack():
    return hp(noise(0.12), 0.3) * env(int(0.12 * SR), 0.0005, 0.03) * 1.2


def gasp():
    d = 0.6
    t = t_axis(d)
    return hp(noise(d), 0.6) * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.08) * 0.35


def wind(d=2.0):
    t = t_axis(d)
    return lp(noise(d), 0.03) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t)) * 0.6


def boing():
    return audio.boing()


def wt(shot, i, default):
    w = WORD_TIMES.get(shot, [])
    return w[i][0] if i < len(w) else default


def laughs_cues():
    c = []
    add = lambda shot, t, snd, g=1.0: c.append((at(shot, t), snd, g))
    add(1, 0.9, ha(330, 3, 0.11, 0.07), 0.5)
    add(2, 0.0, whoosh(1.0, up=True), 0.5)
    add(3, 0.2, boing(), 0.35)
    add(4, 0.1, ha(200, 6, 0.14, 0.1), 0.6)
    add(4, 0.05, thud(70, 0.3), 0.6)
    add(5, 0.2, clank(380), 0.6)
    add(5, 0.9, clank(340), 0.4)
    add(6, 0.3, ding(3200), 0.15)
    add(6, 0.6, cricket(1.6), 0.6)
    add(7, 0.0, whoosh(1.2, up=True), 0.5)
    add(8, 0.2, ding(1568), 0.5)
    add(9, 0.05, sparkle(), 0.4)
    add(10, 0.3, ha(320, 6, 0.12, 0.08), 0.55)
    add(11, 0.05, ha(330, 3, 0.1, 0.07), 0.5)
    add(12, 0.05, ha(340, 3, 0.1, 0.07), 0.5)
    add(13, 0.2, ha(300, 7, 0.13, 0.09), 0.6)
    add(14, 0.1, thud(55, 0.5), 0.9)
    for k in range(3):
        add(15, 1.0 / 1.3 * k + 0.75, thud(160, 0.15), 0.8)
        add(15, 1.0 / 1.3 * k + 0.77, pop(500), 0.4)
    add(15, 0.9, ha(380, 8, 0.1, 0.06), 0.3)
    add(17, 0.3, clank(160, 0.9), 0.8)
    add(18, 0.0, clank(300), 0.6)
    add(18, 0.55, clank(300), 0.6)
    add(19, 1.25, pop(300), 0.4)
    add(20, 0.1, whisper(2.2), 0.8)
    add(21, 1.4, rumble(0.9), 0.7)
    add(21, 2.35, crunch(0.05), 0.7)
    add(23, 0.0, audio.cheer(1.6), 0.4)
    add(24, 0.6, meow(), 0.6)
    add(25, 0.2, crack(), 0.9)
    add(25, 0.85, thud(90, 0.4), 0.8)
    add(25, 0.86, crunch(0.2), 0.6)
    add(26, 0.2, meow(scared=True), 0.7)
    add(27, 0.0, squeal(), 0.5)
    add(28, 0.1, ha(220, 3, 0.25, 0.1), 0.25)
    add(28, 0.3, ha(180, 2, 0.3, 0.1), 0.2)
    add(29, 0.4, cricket(3.0), 0.7)
    add(32, 0.5, trombone(), 0.5)
    for i, g in enumerate((0.5, 0.75, 1.0)):
        add(34, wt(34, i, 0.08 + 0.7 * i) + 0.08, clank(260 - 30 * i, 0.7), g)
    add(35, 1.6, crunch(0.04), 0.9)
    add(35, 1.65, ding(2600), 0.3)
    add(36, 0.1, gasp(), 0.9)
    add(40, 0.7, moo(), 0.7)
    add(41, 0.0, wind(2.3), 0.5)
    add(41, 0.6, cricket(1.5), 0.6)
    add(42, 0.45, snort(), 0.8)
    add(43, 0.1, ha(170, 10, 0.13, 0.1), 0.75)
    add(44, 0.15, whoosh(1.4, up=True), 0.9)
    add(44, 0.2, ha(170, 8, 0.14, 0.1), 0.4)
    add(45, 0.2, ha(330, 9, 0.11, 0.08), 0.55)
    add(45, 0.4, whoosh(1.2, up=True), 0.6)
    add(46, 0.7, meow(), 0.6)
    add(46, 0.8, audio.cheer(1.0), 0.5)
    add(46, 0.8, sparkle(), 0.5)
    add(47, 0.3, ha(210, 4, 0.16, 0.08), 0.3)
    add(47, 2.2, ha(200, 4, 0.16, 0.08), 0.3)
    add(50, 0.2, ha(320, 6, 0.12, 0.08), 0.4)
    add(50, 0.3, ha(190, 6, 0.14, 0.09), 0.4)
    add(51, 0.05, thud(150, 0.15), 0.9)
    add(51, 0.07, pop(450), 0.5)
    add(51, 0.2, ha(300, 10, 0.11, 0.08), 0.4)
    return c


def gain(total):
    n = int(total * SR)
    tt = np.arange(n) / SR
    g = np.ones(n)
    for s0, s1, k in ((16, 23, 0.55), (31, 44, 0.05), (44, 52, 1.15)):
        a = at(s0, 0)
        b = at(s1, 0) if s1 <= 51 else total
        g[(tt >= a) & (tt < b)] = k
    m = int(0.3 * SR)
    return np.convolve(g, np.ones(m) / m, mode="same")


_bed = audio.music_bed


def laughs_bed(total):
    bed, hum = _bed(total)
    return bed * gain(total), hum


audio.music_bed = laughs_bed
audio.PAUSED = []
audio.cues = laughs_cues
audio.MUSIC_DB_VOICE = -15.5

if __name__ == "__main__":
    sys.exit(audio.main())
