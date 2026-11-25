"""Music and effects for When You SNEEZE, You SWITCH Places (all synthesised), mixed under the voice.

    STORY=sneeze python3 sneeze_audio.py --voice out/sneeze__voice_pre.wav   -> out/sneeze_mix.wav

Bouncy music for the town gags, softer piano while the bridge creaks and the mayor freezes (22-29), a sparkly
"swap" whoosh on every sneeze-swap, a gasp and a beat of silence when the whole town stares (31), the bounce
comes back for the fix and the cheers, hard cut to silence.
"""
import os
import sys

os.environ.setdefault("STORY", "sneeze")
import numpy as np  # noqa: E402

import audio  # noqa: E402
import laughs_audio  # noqa: E402
import robot_audio as ra  # noqa: E402
import umbrella_audio as ua  # noqa: E402
import wish_audio as wa  # noqa: E402
from audio import SR, at, crunch, ding, env, hp, lp, noise, pop, sparkle, t_axis, thud, whoosh  # noqa: E402
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


def sneeze_fx():
    """A quick 'tchoo': rising hiss, a pop on the burst."""
    d = 0.3
    n = hp(noise(d), 0.6) * env(int(d * SR), 0.03, 0.09) * 0.7
    return mx(n, np.concatenate([np.zeros(int(0.06 * SR)), pop(520) * 0.6]))


def swap_fx():
    return mx(whoosh(0.7, up=True) * 0.8, sparkle() * 0.7, ding(1760) * 0.35)


def inhale():
    return ua.breath() * 0.6


def puff():
    d = 0.4
    return lp(noise(d), 0.15) * env(int(d * SR), 0.01, 0.15) * 0.8


def splat():
    return mx(thud(90, 0.25) * 0.9, lp(noise(0.3), 0.25) * env(int(0.3 * SR), 0.005, 0.1) * 0.8)


def rustle():
    return wa.rustle(0.7) * 0.8


def footsteps(n=8, gap=0.2, f=170):
    out = np.zeros(int((n * gap + 0.2) * SR))
    for i in range(n):
        s = thud(f, 0.07)
        o = int(i * gap * SR)
        out[o:o + len(s)] += s * (0.7 + 0.3 * (i % 2))
    return out


def snip():
    return mx(hp(noise(0.05), 0.5) * env(int(0.05 * SR), 0.0005, 0.012) * 0.9, ding(2349) * 0.5)


def sneeze_cues():
    c = []

    def add(shot, t, snd, g=1.0):
        c.append((at(shot, t), snd, g))

    t01 = wt(1, 5, 1.1)
    add(1, t01, sneeze_fx(), 0.9)
    add(1, t01 + 0.4, swap_fx(), 0.9)
    add(2, wt(2, 1, 0.5) + 0.6, swap_fx(), 0.9)
    add(3, 0.3, rustle(), 0.5)
    add(3, 1.4, rustle(), 0.5)
    add(4, 0.2, rustle(), 0.7)
    for k, i in enumerate((0, 1, 2)):
        add(5, wt(5, i, 0.8 * k) + 0.05, rustle() if k != 1 else crunch(0.2), 0.7)
    add(6, wt(6, 5, 1.0), inhale(), 0.8)
    t6 = wt(6, 9, 1.5) + 0.25
    add(6, t6, sneeze_fx(), 0.9)
    t7 = wt(7, 0, 0.25)
    add(7, t7, sneeze_fx(), 0.9)
    add(7, t7 + 0.35, swap_fx(), 0.9)
    add(8, 0.9, ding(1568), 0.4)
    th = (wt(9, 5, 1.5) - 0.12) if WORD_TIMES.get(9) else 1.2
    add(9, th - 0.4, whoosh(0.4, up=False), 0.7)
    add(9, th, splat(), 1.0)
    add(10, wt(10, 6, 1.4), sparkle(), 0.5)
    t11 = wt(11, 3, 1.3) + 0.3
    add(11, t11 - 0.3, puff(), 0.7)
    add(11, t11 - 0.6, inhale(), 0.7)
    add(11, t11, sneeze_fx(), 0.9)
    add(12, wt(12, 1, 0.6) + 0.25, swap_fx(), 0.9)
    for k in range(3):
        add(13, 0.2 + 0.35 * k, thud(1100, 0.03), 0.5)
    add(14, wt(14, 6, 1.6), ding(1760), 0.5)
    add(15, 0.2, sparkle(), 0.4)
    add(16, 0.5, laughs_audio.cricket(1.0), 0.6)
    add(17, 0.1, ua.groan() * 0.6, 0.5)
    add(18, 0.7, ra.squeak(), 0.5)
    add(19, 0.3, laughs_audio.wind(1.6), 0.5)
    add(19, 1.0, laughs_audio.crack(), 0.6)
    add(20, 0.1, wa.chatter(2.4), 0.5)
    add(21, 0.2, wa.tick(3, 0.4), 0.4)
    add(22, 0.05, wa.creak(), 0.9)
    for k in range(3):
        add(23, 0.15 + 0.4 * k, wa.creak(), 0.7)
    add(23, 0.1, laughs_audio.rumble(1.0), 0.6)
    for k in range(3):
        add(24, 0.1 + 0.18 * k, laughs_audio.squeal(0.5), 0.45)
    add(24, wt(24, 3, 1.0), laughs_audio.gasp(), 0.7)
    add(25, 0.2, ding(2093), 0.5)
    add(26, 0.2, wa.creak(), 0.6)
    add(27, 0.5, sparkle(), 0.3)
    t28 = wt(28, 2, 1.3)
    add(28, 0.1, inhale(), 0.8)
    add(28, t28, sneeze_fx(), 1.0)
    add(29, 0.45, swap_fx(), 1.0)
    add(30, 0.35, laughs_audio.gasp(), 0.7)
    add(31, 0.05, laughs_audio.gasp(), 0.9)
    add(32, wt(32, 7, 1.6), ding(1568), 0.5)
    add(33, 0.2, whoosh(0.6, up=True), 0.6)
    add(34, 0.05, footsteps(9, 0.2), 0.6)
    for k, i in enumerate((0, 2, 4)):
        add(35, wt(35, i, 0.5 * k) + 0.05, crunch(0.25), 0.8)
        add(35, wt(35, i, 0.5 * k) + 0.2, rustle(), 0.5)
    add(35, wt(35, 4, 1.4) + 0.5, ding(1760), 0.5)
    add(36, 0.1, sparkle(), 0.4)
    add(37, 0.0, audio.cheer(1.6), 0.9)
    for k in range(5):
        add(38, 0.1 + 0.3 * k, pop(500 + 120 * k), 0.4)
    t39 = wt(39, 0, 0.35)
    add(39, t39, sneeze_fx(), 0.9)
    add(39, t39 + 0.4, swap_fx(), 0.9)
    add(40, 0.2, inhale(), 0.8)
    add(41, 0.6, sparkle(), 0.3)
    add(42, 0.0, audio.cheer(1.4), 0.9)
    add(43, 0.3, wa.tick(2, 0.5), 0.4)
    add(44, 0.1, snip(), 1.0)
    add(44, 0.12, audio.cheer(1.6), 0.9)
    add(45, 0.2, sparkle(), 0.4)
    add(46, 0.6, laughs_audio.boing(), 0.7)
    return c


def gains(total):
    n = int(total * SR)
    tt = np.arange(n) / SR
    bounce, piano = np.zeros(n), np.zeros(n)

    def span(s0, s1):
        a = at(s0, 0)
        b = at(s1, 0) if s1 <= len(SHOTS) else total
        return (tt >= a) & (tt < b)

    bounce[span(1, 22)] = 1.0
    piano[span(22, 29)] = 0.75
    bounce[span(29, 31)] = 0.6
    bounce[span(32, 47)] = 1.0
    bounce[span(37, 47)] = 1.15
    m = int(0.35 * SR)
    sm = lambda g: np.convolve(g, np.ones(m) / m, mode="same")
    return sm(bounce), sm(piano)


def sneeze_bed(total):
    bed, hum = _bounce(total)
    pb = wa.piano_bed(total)
    pb *= np.sqrt(np.mean(bed ** 2)) / max(1e-6, np.sqrt(np.mean(pb ** 2)))
    gb, gp = gains(total)
    return bed * gb + pb * gp, hum


audio.music_bed = sneeze_bed
audio.PAUSED = []
audio.cues = sneeze_cues
audio.MUSIC_DB_VOICE = -15

if __name__ == "__main__":
    sys.exit(audio.main())
