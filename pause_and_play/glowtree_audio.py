"""Music and effects for When Trees Light Up at LUNCH (all synthesised), mixed under the voice.

    STORY=glowtree python3 glowtree_audio.py --voice out/glowtree__voice_pre.wav   -> out/glowtree_mix.wav

Bouncy music for the whisper rule and the town gags (1-8), soft piano while Rudy sneaks out before dawn, races
Tim and meets the locked gate (9-35), a shimmer + swell every time a tree lights up, a creak for the gate, a
THUD for Tim's trip, then the bounce comes back for the town running to the garden and the picnic (36-42);
hard cut to silence at the end.
"""
import os
import sys

os.environ.setdefault("STORY", "glowtree")
import numpy as np  # noqa: E402

import audio  # noqa: E402
import laughs_audio  # noqa: E402
import umbrella_audio as ua  # noqa: E402
import wish_audio as wa  # noqa: E402
from audio import SR, at, crunch, ding, env, hp, lp, noise, pop, sparkle, thud, whoosh  # noqa: E402
from story import SHOTS, WORD_TIMES  # noqa: E402

_bounce = laughs_audio._bed


def wt(shot, i, default=0.0):
    w = WORD_TIMES.get(shot, [])
    return w[i][0] if i < len(w) else default


def mx(*xs):
    out = np.zeros(max(len(x) for x in xs))
    for x in xs:
        out[:len(x)] += x
    return out


def glow_fx():
    """A tree lighting up: rising shimmer, a bell on top."""
    return mx(sparkle() * 0.8, whoosh(0.9, up=True) * 0.45, ding(1568) * 0.4)


def gold_fx():
    """The big gold blaze: longer swell, two bells."""
    return mx(sparkle() * 0.9, whoosh(1.2, up=True) * 0.6, ding(1760) * 0.45, ding(2349) * 0.3)


def whisper_fx():
    d = 0.9
    return hp(noise(d), 0.55) * env(int(d * SR), 0.2, 0.3) * 0.35


def footsteps(n=8, gap=0.2, f=170):
    out = np.zeros(int((n * gap + 0.2) * SR))
    for i in range(n):
        s = thud(f, 0.07)
        o = int(i * gap * SR)
        out[o:o + len(s)] += s * (0.7 + 0.3 * (i % 2))
    return out


def clunk():
    return mx(thud(240, 0.12) * 0.9, ding(520) * 0.25)


def glowtree_cues():
    c = []

    def add(shot, t, snd, g=1.0):
        c.append((at(shot, t), snd, g))

    add(1, wt(1, 5, 1.0), whisper_fx(), 0.8)
    add(2, 0.0, glow_fx(), 0.9)
    add(3, 0.1, whisper_fx(), 0.8)
    add(4, 0.0, glow_fx(), 0.9)
    add(5, 0.1, whisper_fx(), 0.8)
    add(6, 0.0, glow_fx(), 0.8)
    add(7, 0.1, whisper_fx(), 0.8)
    add(8, 0.05, glow_fx(), 0.8)
    add(9, wt(9, 6, 1.5), ding(1760), 0.4)
    add(10, 0.5, sparkle(), 0.3)
    add(11, 0.2, wa.rustle(0.7), 0.5)
    add(12, 0.0, laughs_audio.rumble(1.6), 0.6)
    add(13, 0.3, ding(392), 0.4)
    add(14, 0.3, laughs_audio.cricket(1.0), 0.5)
    add(15, 0.1, footsteps(9, 0.28), 0.5)
    add(16, 0.2, laughs_audio.wind(1.2), 0.4)
    add(17, 0.1, whisper_fx(), 0.8)
    add(18, 0.5, wa.tick(1, 0.3), 0.6)
    add(18, 0.9, laughs_audio.cricket(1.0), 0.5)
    add(19, 0.1, wa.tick(5, 0.5), 0.7)
    add(20, 0.2, whisper_fx(), 0.8)
    add(21, 0.1, ding(1319), 0.4)
    add(22, 0.0, gold_fx(), 1.0)
    add(23, 0.5, ding(1175), 0.3)
    add(24, 0.05, footsteps(12, 0.2), 0.6)
    add(24, 0.2, whoosh(0.6, up=True), 0.4)
    add(25, 0.2, wa.rustle(1.0), 0.6)
    add(25, 1.0, glow_fx(), 0.8)
    add(25, 1.6, wa.creak(), 0.8)
    for k in range(4):
        add(26, 0.1 + 0.3 * k, thud(180, 0.07), 0.6)
    add(26, 1.4, thud(90, 0.25), 1.0)
    add(26, 1.42, crunch(0.2), 0.7)
    add(27, 0.4, footsteps(4, 0.25), 0.4)
    add(28, 0.2, ding(1047), 0.35)
    add(29, 0.1, ding(330) * 0.5, 0.6)
    add(30, 0.2, clunk(), 0.9)
    add(30, 0.6, laughs_audio.cricket(1.0), 0.4)
    add(31, wt(31, 5, 1.2), whisper_fx(), 0.8)
    add(32, 0.2, ding(880), 0.3)
    add(33, 0.0, gold_fx(), 1.0)
    add(34, 0.2, wa.creak(), 0.9)
    add(34, 0.4, sparkle(), 0.8)
    add(34, 1.0, audio.cheer(1.2), 0.5)
    add(35, 0.1, sparkle(), 0.9)
    add(35, wt(35, 8, 2.0), glow_fx(), 0.6)
    add(36, 0.0, footsteps(14, 0.2), 0.5)
    add(36, 0.1, wa.chatter(2.4), 0.5)
    add(37, 0.3, audio.cheer(1.2), 0.7)
    add(38, 0.1, ding(1568), 0.4)
    add(38, 1.6, audio.cheer(1.2), 0.6)
    add(39, 0.0, laughs_audio.rumble(1.2), 0.6)
    add(39, wt(39, 8, 1.6), thud(70, 0.3), 0.8)
    add(40, 0.3, sparkle(), 0.5)
    add(41, 0.2, wa.chatter(2.0), 0.5)
    add(41, 0.9, audio.cheer(1.0), 0.6)
    add(42, wt(42, 6, 1.8), laughs_audio.boing(), 0.7)
    add(42, wt(42, 6, 1.8) + 0.2, glow_fx(), 0.7)
    return c


def gains(total):
    n = int(total * SR)
    tt = np.arange(n) / SR
    bounce, piano = np.zeros(n), np.zeros(n)

    def span(s0, s1):
        a = at(s0, 0)
        b = at(s1, 0) if s1 <= len(SHOTS) else total
        return (tt >= a) & (tt < b)

    bounce[span(1, 9)] = 1.0
    piano[span(9, 36)] = 0.8
    bounce[span(36, 43)] = 1.1
    m = int(0.35 * SR)
    sm = lambda g: np.convolve(g, np.ones(m) / m, mode="same")
    return sm(bounce), sm(piano)


def glowtree_bed(total):
    bed, hum = _bounce(total)
    pb = wa.piano_bed(total)
    pb *= np.sqrt(np.mean(bed ** 2)) / max(1e-6, np.sqrt(np.mean(pb ** 2)))
    gb, gp = gains(total)
    return bed * gb + pb * gp, hum


audio.music_bed = glowtree_bed
audio.PAUSED = []
audio.cues = glowtree_cues
audio.MUSIC_DB_VOICE = -15

if __name__ == "__main__":
    sys.exit(audio.main())
