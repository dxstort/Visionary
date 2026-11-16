"""Music and effects for The Porch Light (all synthesised). Mixes the voice on top when given.

    STORY=porch python3 porch_audio.py --voice out/porch__voice_pre.wav   -> out/porch_mix.wav
"""
import os
import sys

os.environ.setdefault("STORY", "porch")
import numpy as np  # noqa: E402

import audio  # noqa: E402
from audio import (SR, at, crunch, ding, env, hp, noise, pop, sparkle, t_axis, thud, whoosh, zap)  # noqa: E402


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def keys(f, d, vel=1.0):
    """Soft felt-piano note: a few decaying partials."""
    t = t_axis(d)
    tone = sum(a * np.sin(2 * np.pi * f * k * t) for k, a in ((1, 1.0), (2, 0.35), (3, 0.12), (4, 0.05)))
    return tone * env(len(t), 0.006, 0.55) * 0.16 * vel


def section_gain(tt):
    """Music dynamics by story beat: soft through the gloomy middle, very soft at 'nobody made him happy back',
    full at the ending."""
    g = np.full_like(tt, 1.0)
    for (s0, t0), (s1, t1), k in (((10, 0), (25, 0), 0.75), ((47, 0), (48, 0), 0.5), ((55, 0), (57, 9), 1.15)):
        a, b = at(s0, t0), at(s1, 0) + (t1 if t1 < 9 else 9)
        g[(tt >= a) & (tt < b)] = k
    k = int(0.4 * SR)
    return np.convolve(g, np.ones(k) / k, mode="same")


def porch_bed(total):
    """Warm, gentle loop: 92 BPM, I-V-vi-IV in F, rolling piano arpeggios, soft pad and bass."""
    beat = 60 / 92
    n = int(total * SR)
    out = np.zeros(n)
    prog = [(41, (65, 69, 72)), (48, (64, 67, 72)), (50, (62, 65, 69)), (46, (62, 65, 70))]
    nb = int(total / beat) + 2
    for b in range(nb):
        root, chord = prog[(b // 4) % 4]
        s0 = int(b * beat * SR)
        if s0 >= n:
            break
        if b % 4 == 0:  # bass + pad once per bar
            d = beat * 4
            t = t_axis(d)
            bass = np.sin(2 * np.pi * hz(root - 12) * t) * env(len(t), 0.02, 1.4) * 0.22
            pad = sum(np.sin(2 * np.pi * hz(m) * t) * 0.03 for m in chord)
            pad *= np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)
            seg = bass + pad
            out[s0:s0 + len(seg)] += seg[: n - s0]
        for k in range(2):  # eighth-note arpeggio
            m = (chord + (chord[0] + 12,))[(b * 2 + k) % 4] + 12
            o = s0 + int(k * beat / 2 * SR)
            if o < n:
                seg = keys(hz(m), beat * 1.6, 0.8 if k else 1.0)
                out[o:o + len(seg)] += seg[: n - o]
    tt = np.arange(n) / SR
    out *= section_gain(tt)
    fade = int(0.6 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    return out, np.zeros(n)


def beep(f=2000, d=0.09):
    t = t_axis(d)
    return np.sin(2 * np.pi * f * t) * env(len(t), 0.002, 0.05) * 0.5


def trumpet_riff():
    """Cheerful, slightly off 'da-da-daaa' on a buzzy brass tone."""
    out = []
    for m, d in ((67, 0.16), (67, 0.16), (72, 0.5), (71, 0.16), (74, 0.6)):
        t = t_axis(d)
        f = hz(m) * (1 + 0.006 * np.sin(2 * np.pi * 6 * t))
        saw = 2 * ((f * t) % 1.0) - 1
        tone = saw * np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.04) * 0.22
        out.append(tone)
        out.append(np.zeros(int(0.03 * SR)))
    x = np.concatenate(out)
    k = 6
    return np.convolve(x, np.ones(k) / k, mode="same")


def scribble(d=0.9):
    x = hp(noise(d), 0.8)
    t = t_axis(d)
    return x * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 7 * t))) * 0.18


def porch_cues():
    c = []
    add = lambda shot, t, snd, g=1.0: c.append((at(shot, t), snd, g))
    add(1, 0.0, ding(1568), 0.35)
    for i in range(6):
        add(2, 0.2 + i * 0.12, pop(700 + 90 * i), 0.45)
    add(3, 0.5, ding(1320), 0.6)
    add(3, 0.75, sparkle(), 0.4)
    add(4, 0.05, pop(900), 0.7)
    for k, t0 in enumerate((0.05, 0.4, 0.75, 1.1, 1.35)):
        add(5, t0 - 0.05, whoosh(0.25, up=True), 0.35)
        add(5, t0 + 0.12, thud(55 + 8 * k, 0.4), 0.7)
        add(5, t0 + 0.15, sparkle(), 0.35)
    add(6, 0.1, thud(90, 0.3), 0.35)
    for k in range(4):
        add(7, 0.1 + k * 0.22, zap(0.07), 0.25)
    for t0 in (0.1, 0.3, 0.5):
        add(8, t0, pop(1000), 0.6)
    add(9, 0.0, sparkle(), 0.4)
    add(10, 0.1, whoosh(0.6, up=False), 0.3)
    add(13, 0.0, whoosh(0.8, up=False), 0.25)
    add(14, 0.15, thud(80, 0.3), 0.6)
    for k in range(5):
        add(15, 0.05 + k * 0.28, thud(140, 0.08), 0.3)
    add(16, 0.05, pop(900), 0.6)
    add(17, 0.25, ding(1760), 0.6)
    add(18, 0.5, ding(2600), 0.25)
    add(20, 0.05, trumpet_riff(), 0.9)
    add(21, 0.0, trumpet_riff()[: int(0.9 * SR)], 0.7)
    add(22, 0.32, thud(70, 0.3), 1.0)
    add(22, 0.34, crunch(0.08), 0.6)
    add(23, 0.1, sparkle(), 0.6)
    add(24, 0.05, thud(100, 0.3), 0.35)
    add(25, 0.3, pop(900), 0.6)
    add(26, 0.25, beep(), 0.5)
    add(26, 0.45, beep(), 0.5)
    add(27, 0.1, whoosh(1.1, up=False), 0.45)
    add(27, 1.3, pop(1300), 0.7)
    add(28, 0.45, crunch(0.18), 0.5)
    add(30, 0.15, sparkle(), 0.6)
    add(31, 0.1, sparkle(), 0.5)
    add(31, 0.6, ding(2093), 0.5)
    add(32, 0.05, ding(1568), 0.4)
    for s in (33, 34, 35):
        add(s, 0.05, pop(1000), 0.55)
    add(36, 0.1, sparkle(), 0.5)
    add(37, 0.0, sparkle(), 0.4)
    add(38, 0.1, beep(1800), 0.4)
    add(39, 0.05, crunch(0.25), 0.4)
    add(40, 0.15, whoosh(0.4, up=True), 0.3)
    add(43, 0.2, crunch(0.2), 0.4)
    add(43, 0.7, crunch(0.15), 0.35)
    add(44, 0.38, whoosh(0.7, up=True), 0.7)
    add(45, 0.05, pop(1100), 0.8)
    for j in range(10):
        add(46, 0.05 + j * 0.16, whoosh(0.4, up=False), 0.18)
        add(46, 0.8 + j * 0.16, ding(1320 + 60 * j), 0.25)
    add(48, 0.4, crunch(0.2), 0.4)
    add(49, 0.0, scribble(0.85), 0.8)
    add(51, 0.3, whoosh(0.8, up=True), 0.7)
    add(52, 1.0, pop(1300), 0.7)
    add(53, 0.3, crunch(0.2), 0.5)
    for k in range(3):
        add(55, 0.65 + k * 0.25, zap(0.06), 0.25)
    add(56, 0.25, ding(1047), 0.9)
    add(56, 0.27, sparkle(), 0.8)
    add(56, 0.3, ding(1568), 0.6)
    add(57, 0.0, sparkle(), 0.6)
    return c


audio.MUSIC_DB_VOICE = -15  # this bed is denser than Pause & Play's; keep it ~11 dB under the voice
audio.music_bed = porch_bed
audio.PAUSED = []
audio.cues = porch_cues

if __name__ == "__main__":
    sys.exit(audio.main())
