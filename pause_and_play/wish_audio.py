"""Music and effects for The Birthday Wish (all synthesised), mixed under the voice.

    STORY=wish python3 wish_audio.py --voice out/wish__voice_pre.wav   -> out/wish_mix.wav

Bouncy music for the first part, quieter for the night, soft piano from Leo's nightmare (33), silence on the
note (36) with a single piano note, happy music back at the Wish Candle (42), hard cut to silence.
"""
import os
import sys

os.environ.setdefault("STORY", "wish")
import numpy as np  # noqa: E402

import audio  # noqa: E402
from audio import SR, at, crunch, ding, env, hp, lp, noise, pop, sparkle, t_axis, thud, whoosh  # noqa: E402
import laughs_audio  # noqa: E402
from laughs_audio import clank, ha  # noqa: E402
from story import SHOTS  # noqa: E402

_music_bed = laughs_audio._bed  # the original bouncy loop (importing laughs_audio swapped in its own bed)


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def keys(f, d, vel=1.0):
    t = t_axis(d)
    tone = sum(a * np.sin(2 * np.pi * f * k * t) for k, a in ((1, 1.0), (2, 0.35), (3, 0.12), (4, 0.05)))
    return tone * env(len(t), 0.006, 0.7) * 0.18 * vel


def piano_bed(total):
    """Gentle piano: slow arpeggios, Am-F-C-G, 70 BPM."""
    beat = 60 / 70
    n = int(total * SR)
    out = np.zeros(n)
    prog = [(57, (69, 72, 76)), (53, (65, 69, 72)), (48, (64, 67, 72)), (55, (62, 67, 71))]
    b = 0
    while True:
        s0 = int(b * beat * SR)
        if s0 >= n:
            break
        root, chord = prog[(b // 4) % 4]
        if b % 4 == 0:
            seg = keys(hz(root - 12), beat * 4, 0.9)
            out[s0:s0 + len(seg)] += seg[: n - s0]
        m = (chord + (chord[1] + 12,))[b % 4]
        seg = keys(hz(m), beat * 2.5, 0.7)
        out[s0:s0 + len(seg)] += seg[: n - s0]
        b += 1
    return out


def bark():
    out = []
    for f in (520, 470):
        t = t_axis(0.12)
        x = np.sign(np.sin(2 * np.pi * f * t * (1 - 0.6 * t))) * env(len(t), 0.002, 0.05)
        out += [lp(x, 0.3) * 0.5, np.zeros(int(0.08 * SR))]
    return np.concatenate(out)


def whine():
    d = 1.0
    t = t_axis(d)
    f = 900 - 350 * t
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * (1 + 0.3 * np.sin(2 * np.pi * 7 * t)) * np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.3) * 0.18


def chatter(d=2.2):
    out = np.zeros(int(d * SR))
    rng = np.random.RandomState(3)
    t0 = 0.0
    while t0 < d - 0.1:
        g = ha(rng.uniform(380, 560), 1, 0.06, rng.uniform(0.04, 0.07), 0.4)
        o = int(t0 * SR)
        out[o:o + len(g)] += g[: len(out) - o]
        t0 += rng.uniform(0.06, 0.1)
    return out


def scratch():
    d = 0.35
    t = t_axis(d)
    f = 300 + 1500 * np.abs(np.sin(2 * np.pi * 3 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * 0.3 + hp(noise(d), 0.6) * 0.3) * np.minimum(1, (d - t) / 0.05)


def zip_():
    d = 0.4
    t = t_axis(d)
    return hp(noise(d), 0.7) * (np.sin(2 * np.pi * (40 + 120 * t) * t) > 0) * np.minimum(1, (d - t) / 0.05) * 0.5


def sizzle(d=1.5):
    t = t_axis(d)
    return hp(noise(d), 0.85) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 13 * t))) * 0.25


def squeak():
    d = 0.25
    t = t_axis(d)
    return np.sin(2 * np.pi * (2200 + 900 * t) * t) * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.05) * 0.2


def snore(d=2.0):
    t = t_axis(d)
    breath = np.maximum(0, np.sin(2 * np.pi * 0.5 * t)) ** 2
    return lp(noise(d), 0.03) * breath * 0.9


def yawn():
    d = 1.0
    t = t_axis(d)
    f = 260 - 120 * t
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1.0) - 1
    return lp(saw, 0.12) * np.sin(np.pi * t / d) * 0.25


def tick(n=6, gap=0.5):
    out = np.zeros(int((n * gap + 0.1) * SR))
    for i in range(n):
        c = hp(noise(0.02), 0.5) * env(int(0.02 * SR), 0.0005, 0.004) * (0.5 if i % 2 else 0.35)
        o = int(i * gap * SR)
        out[o:o + len(c)] += c
    return out


def mumble(d=0.9):
    return lp(ha(170, 6, 0.13, 0.1, 0.5), 0.1)[: int(d * SR)] * 1.5


def rustle(d=1.2):
    t = t_axis(d)
    return hp(noise(d), 0.5) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 2.5 * t))) * 0.25


def creak():
    d = 0.8
    t = t_axis(d)
    f = 180 + 60 * np.sin(2 * np.pi * 1.5 * t)
    pulses = (np.sin(2 * np.pi * 35 * t) > 0.6).astype(float)
    return np.sin(2 * np.pi * f * t) * pulses * np.minimum(1, (d - t) / 0.1) * 0.25


def drone(d=2.8):
    t = t_axis(d)
    x = np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 58 * t) + 0.3 * np.sin(2 * np.pi * 110 * t)
    return x * np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.4) * 0.12


def heartbeat(n=4, gap=0.8):
    out = np.zeros(int((n * gap + 0.3) * SR))
    for i in range(n):
        for dt, g in ((0.0, 1.0), (0.18, 0.7)):
            b = thud(55, 0.18) * g
            o = int((i * gap + dt) * SR)
            out[o:o + len(b)] += b
    return out * 0.6


def match():
    return hp(noise(0.25), 0.4) * env(int(0.25 * SR), 0.005, 0.08) * 0.6


def chant():
    """'JET-PACK!' chant: two shouted syllables from a few voices."""
    out = np.zeros(int(1.0 * SR))
    for f0 in (180, 230, 300):
        for i, (f, d) in enumerate(((1.0, 0.16), (1.25, 0.22))):
            g = ha(f0 * f, 1, 0.1, d, 0.35)
            o = int((0.02 * (f0 % 3) + i * 0.25) * SR)
            out[o:o + len(g)] += g[: len(out) - o]
    return out


def wish_cues():
    c = []
    add = lambda shot, t, snd, g=1.0: c.append((at(shot, t), snd, g))
    add(1, 0.35, match(), 0.7)
    add(1, 0.45, ding(1568), 0.5)
    add(2, 0.05, scratch(), 0.7)
    add(4, 0.1, sparkle(), 0.5)
    add(4, 0.1, keys(hz(57), 1.6) + keys(hz(60), 1.6) + keys(hz(64), 1.6), 0.8)
    add(5, 0.4, ding(1320), 0.5)
    add(6, 0.0, sizzle(1.6), 0.8)
    for k in range(4):
        add(6, 0.2 + k * 0.3, clank(500 + 80 * k, 0.25), 0.25)
    add(7, 0.3, thud(110, 0.25), 0.6)
    add(8, 0.6, bark(), 0.6)
    add(9, 0.1, chatter(2.3), 0.7)
    add(10, 0.05, sparkle(), 0.4)
    add(11, 0.3, squeak(), 0.6)
    add(12, 0.4, ding(1760), 0.5)
    add(13, 1.6, whoosh(0.8, up=True), 0.6)
    add(14, 0.0, whoosh(1.2, up=False), 0.5)
    add(14, 1.0, whine(), 0.6)
    add(16, 0.2, ding(2093), 0.3)
    add(17, 0.5, zip_(), 0.8)
    add(18, 0.05, pop(800), 0.5)
    add(19, 0.05, pop(700), 0.5)
    for k in range(4):
        add(20, k * 0.41, pop(900 + 100 * k), 0.6)
    add(23, 0.3, snore(2.8), 0.5)
    add(24, 0.3, yawn(), 0.6)
    add(24, 1.0, yawn(), 0.4)
    add(25, 0.1, sparkle(), 0.6)
    add(26, 0.2, pop(1000), 0.5)
    add(28, 0.0, tick(6, 0.5), 0.7)
    add(29, 0.5, mumble(1.0), 0.5)
    add(30, 0.0, mumble(0.9), 0.6)
    add(31, 0.0, rustle(1.8), 0.8)
    add(32, 0.0, creak(), 0.8)
    add(33, 0.0, drone(2.9), 1.0)
    add(34, 0.2, crunch(0.25), 0.4)
    add(36, 0.4, keys(hz(76), 3.0, 1.2), 1.0)
    add(40, 0.2, heartbeat(4, 0.8), 0.8)
    add(42, 0.2, sparkle(), 0.5)
    add(43, 0.3, bark(), 0.6)
    q = [a for a in SHOTS if a[0] == 44][0][1] / 3
    for k in range(3):
        add(44, k * q + 0.05, chant(), 0.6)
    add(47, 0.25, sparkle(), 0.9)
    add(47, 0.27, ding(1047), 0.6)
    add(47, 0.3, ding(1568), 0.5)
    add(50, 0.1, sparkle(), 0.4)
    add(51, 0.3, snore(2.2), 0.4)
    add(52, 0.05, ding(2093), 0.4)
    add(53, 0.4, whine(), 0.6)
    return c


def gains(total):
    n = int(total * SR)
    tt = np.arange(n) / SR
    bounce, piano = np.zeros(n), np.zeros(n)

    def span(s0, s1):
        a = at(s0, 0)
        b = at(s1, 0) if s1 <= len(SHOTS) else total
        return (tt >= a) & (tt < b)

    bounce[span(1, 28)] = 1.0
    bounce[span(28, 33)] = 0.3
    piano[span(33, 36)] = 0.8
    piano[span(37, 42)] = 0.8
    bounce[span(42, 45)] = 1.0
    bounce[span(45, 47)] = 0.35
    bounce[span(47, 54)] = 1.0
    m = int(0.35 * SR)
    sm = lambda g: np.convolve(g, np.ones(m) / m, mode="same")
    return sm(bounce), sm(piano)


def wish_bed(total):
    bed, hum = _music_bed(total)
    pb = piano_bed(total)
    pb *= np.sqrt(np.mean(bed ** 2)) / max(1e-6, np.sqrt(np.mean(pb ** 2)))
    gb, gp = gains(total)
    return bed * gb + pb * gp, hum


audio.music_bed = wish_bed
audio.PAUSED = []
audio.cues = wish_cues
audio.MUSIC_DB_VOICE = -15

if __name__ == "__main__":
    sys.exit(audio.main())
