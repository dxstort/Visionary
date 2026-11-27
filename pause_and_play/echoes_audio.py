"""Music and effects for When Echoes Do The Talking (all synthesised), mixed under the voice.

    STORY=echoes python3 echoes_audio.py --voice out/echoes__voice_pre.wav   -> out/echoes_mix.wav

Bouncy music for the rule and the build-up, an "echo" ping (a note, then the same note again, softer) on every
echoed word, a drum-solo rumble backstage (17), soft piano from the walk on stage, silence when the song is gone
(22-25), a hush for the whisper (28-31), the bounce comes back as the hall joins in (34), cheers for the judges,
hard cut to silence.
"""
import os
import sys

os.environ.setdefault("STORY", "echoes")
import numpy as np  # noqa: E402

import audio  # noqa: E402
import laughs_audio  # noqa: E402
import wish_audio as wa  # noqa: E402
from audio import SR, at, crunch, ding, env, hp, lp, noise, pop, sparkle, t_axis, thud, whoosh  # noqa: E402
from laughs_audio import cricket  # noqa: E402
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


def echo_ping(f=880, gap=0.55, soft=0.45):
    """A note, then the same note again a beat later, softer and a little further away."""
    a = ding(f)
    b = lp(ding(f), 0.4) * soft
    out = np.zeros(int(gap * SR) + len(b))
    out[:len(a)] += a * 0.7
    out[int(gap * SR):] += b
    return out


def drum_roll(n=8):
    out = np.zeros(int(1.4 * SR))
    for i in range(n):
        s = thud(110 + 20 * (i % 2), 0.12)
        o = int(i * 0.14 * SR)
        out[o:o + len(s)] += s * 0.8
    return out


def tick(n=4, gap=0.5):
    return wa.tick(n, gap)


def gasp():
    return laughs_audio.gasp()


def echoes_cues():
    c = []
    add = lambda shot, t, snd, g=1.0: c.append((at(shot, t), snd, g))
    add(1, 0.12, echo_ping(1047, 0.75), 0.7)
    add(2, 0.2, echo_ping(784, 0.7), 0.7)
    add(3, 0.3, whoosh(1.2, up=True), 0.4)
    add(4, wt(4, 2, 0.8), echo_ping(659, 0.9), 0.8)
    add(5, 0.3, whoosh(0.6, up=True), 0.6)
    add(5, 0.9, crunch(0.2), 0.6)
    add(6, wt(6, 2, 0.5), echo_ping(587, 0.8), 0.8)
    add(7, 0.3, sparkle(), 0.5)
    add(8, 0.7, echo_ping(1319, 0.6, 0.3), 0.4)
    add(9, 0.5, echo_ping(1175, 0.4, 0.5), 0.6)
    add(9, 0.9, echo_ping(1397, 0.4, 0.5), 0.5)
    add(11, 0.3, sparkle(), 0.4)
    add(14, 0.2, sparkle(), 0.5)
    for i in range(4):
        add(15, wt(15, 8 + i, 1.0 + 0.5 * i), pop(600 + 80 * i), 0.7)
    add(16, 0.1, echo_ping(698, 0.6), 0.6)
    add(17, wt(17, 4, 0.8), drum_roll(8), 0.9)
    add(18, 0.1, whoosh(0.7, up=True), 0.6)
    add(18, 0.9, sparkle(), 0.6)
    add(19, 0.0, audio.cheer(2.2), 0.7)
    add(19, wt(19, 4, 1.0), echo_ping(988, 0.8), 0.7)
    add(20, wt(20, 3, 0.8), echo_ping(740, 0.8), 0.7)
    add(21, 0.0, audio.cheer(1.2) * 0.5, 0.4)
    add(22, wt(22, 4, 1.0), whoosh(0.8, up=False), 0.8)
    add(22, wt(22, 4, 1.0) + 0.3, thud(60, 0.5), 0.9)
    add(24, 0.2, cricket(1.5), 0.7)
    add(25, 0.0, tick(5, 0.5), 0.8)
    add(26, 0.3, ding(1568), 0.7)
    add(27, 0.2, sparkle(), 0.5)
    add(29, wt(29, 2, 0.4), echo_ping(523, 0.7, 0.55), 0.6)
    add(30, 0.3, laughs_audio.whisper(1.4), 0.4)
    add(31, 0.4, sparkle(), 0.4)
    add(32, 0.2, echo_ping(659, 0.5), 0.7)
    add(33, 0.3, echo_ping(880, 0.8), 0.6)
    add(34, 0.0, audio.cheer(1.6) * 0.6, 0.6)
    add(36, 0.1, pop(900), 0.6)
    add(37, 0.0, whoosh(0.8, up=True), 0.7)
    add(37, 0.3, sparkle(), 0.7)
    add(38, 0.0, audio.cheer(2.4), 0.9)
    add(39, wt(39, 0, 0.4), echo_ping(1047, 0.9), 0.8)
    add(40, 0.4, sparkle(), 0.6)
    add(41, wt(41, 2, 0.8), echo_ping(784, 0.9), 0.8)
    add(42, 0.3, ding(1760), 0.7)
    add(42, 0.9, crunch(0.3), 0.5)
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
    bounce[span(17, 21)] = 0.7
    piano[span(21, 22)] = 0.75
    piano[span(25, 34)] = 0.7
    bounce[span(34, 43)] = 1.15
    m = int(0.35 * SR)
    sm = lambda g: np.convolve(g, np.ones(m) / m, mode="same")
    return sm(bounce), sm(piano)


def echoes_bed(total):
    bed, hum = _bounce(total)
    pb = wa.piano_bed(total)
    pb *= np.sqrt(np.mean(bed ** 2)) / max(1e-6, np.sqrt(np.mean(pb ** 2)))
    gb, gp = gains(total)
    return bed * gb + pb * gp, hum


audio.music_bed = echoes_bed
audio.PAUSED = []
audio.cues = echoes_cues
audio.MUSIC_DB_VOICE = -15

if __name__ == "__main__":
    sys.exit(audio.main())
