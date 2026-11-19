"""Stage 4 audio: synthesised music bed + sound effects, timed to the shot list.

    python3 audio.py                      -> out/music.wav, out/sfx.wav, out/mix.wav
    python3 audio.py --voice voiceover.wav (when narration exists: ducked mix with voice on top)

Everything is generated here with NumPy (no downloaded audio). Levels follow the brief: music sits
10-12 dB under the voice, one short effect per visible action, music drops to a low hum while time
is paused, and the track cuts hard to silence at the end. The final file is mastered to about
-14 LUFS with ffmpeg's loudnorm filter.
"""
import argparse
import os
import subprocess
import wave

import numpy as np

from render import FPS
from story import SHOTS, out_name

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
rng = np.random.RandomState(7)


# ------------------------------------------------------------------ timeline
def shot_starts():
    starts, acc = {}, 0.0
    for num, dur, _, _ in SHOTS:
        starts[num] = round(acc * FPS) / FPS
        acc += dur
    total = round(acc * FPS) / FPS
    return starts, total


STARTS, TOTAL = shot_starts()


def at(shot, t=0.0):
    return STARTS[shot] + t


# paused-time spans (music -> hum): (start shot, offset) .. (end shot, offset)
PAUSED = [
    ((13, 0.0), (14, 0.45)),
    ((16, 1.0), (19, 99)),
    ((21, 0.35), (22, 99)),
    ((37, 0.0), (52, 99)),
    ((54, 0.35), (59, 0.7)),
]


def span(a, b):
    s = at(*a)
    e = STARTS[b[0]] + min(b[1], [d for n, d, _, _ in SHOTS if n == b[0]][0])
    return s, e


# ------------------------------------------------------------------- synths
def t_axis(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.003, r=0.1):
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4))
    return e


def noise(d):
    return rng.uniform(-1, 1, int(d * SR))


def hp(x, k=0.95):
    y = np.empty_like(x)
    prev_x = prev_y = 0.0
    for i, v in enumerate(x):
        prev_y = k * (prev_y + v - prev_x)
        prev_x = v
        y[i] = prev_y
    return y


def lp(x, k=0.2):
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += k * (v - acc)
        y[i] = acc
    return y


def snap():
    d = 0.09
    x = hp(noise(d), 0.8) * env(int(d * SR), 0.0005, 0.012)
    click = np.sin(2 * np.pi * 2200 * t_axis(d)) * env(int(d * SR), 0.0002, 0.006)
    return 0.9 * x + 0.5 * click


def whoosh(d=0.45, up=True):
    n = int(d * SR)
    x = noise(d)
    sweep = np.linspace(0.05, 0.6, n) if up else np.linspace(0.6, 0.05, n)
    y = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += sweep[i] * (x[i] - acc)
        y[i] = acc
    shape = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    return 0.8 * y * shape


def pause_sweep():
    """Time stopping: a quick downward tape-stop zip plus a soft sub thump."""
    d = 0.35
    t = t_axis(d)
    f = 900 * np.exp(-t * 9) + 60
    ph = 2 * np.pi * np.cumsum(f) / SR
    z = np.sin(ph) * np.exp(-t * 5) * 0.5
    thump = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 10) * 0.6
    return z + thump


def pop(f=700):
    d = 0.12
    t = t_axis(d)
    fr = f * (1 + 1.6 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(len(t), 0.001, 0.035) * 0.7


def ding(f=1320):
    d = 0.8
    t = t_axis(d)
    x = sum(a * np.sin(2 * np.pi * f * m * t) for a, m in ((1, 1), (0.4, 2.76), (0.2, 5.4)))
    return x * env(len(t), 0.002, 0.25) * 0.35


def thud(f=70, d=0.35):
    t = t_axis(d)
    fr = f * (1 + np.exp(-t * 30))
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 9)
    return 0.9 * x + 0.25 * lp(noise(d), 0.1) * np.exp(-t * 25)


def zap(d=0.5):
    t = t_axis(d)
    f = 1400 + 500 * np.sin(2 * np.pi * 38 * t)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25
    return x * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.05)


def crunch(d=0.12):
    x = hp(noise(d), 0.7) * (rng.uniform(0, 1, int(d * SR)) > 0.85) * env(int(d * SR), 0.001, 0.04)
    return x * 0.8


def coo():
    d = 0.35
    t = t_axis(d)
    f = 420 + 60 * np.sin(2 * np.pi * 7 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2 * 0.25


def cheer(d=1.3):
    n = int(d * SR)
    x = lp(noise(d), 0.35)
    mod = 0.6 + 0.4 * np.sin(2 * np.pi * 3.1 * t_axis(d)) * np.sin(2 * np.pi * 1.3 * t_axis(d))
    shape = np.minimum(1, t_axis(d) / 0.15) * np.minimum(1, (d - t_axis(d)) / 0.3)
    return x * mod * shape * 1.2


def boing():
    d = 0.4
    t = t_axis(d)
    f = 180 + 120 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * 0.5


def sparkle():
    out = np.zeros(int(0.5 * SR))
    for k in range(5):
        p = ding(1800 + 300 * k)[: int(0.3 * SR)] * 0.5
        o = int(k * 0.05 * SR)
        out[o:o + len(p)] += p[: len(out) - o]
    return out


# --------------------------------------------------------------------- music
def music_bed(total):
    """Light bouncy loop, 150 BPM, I-vi-IV-V in C, plus a paused-time hum track."""
    bpm = 150
    beat = 60 / bpm
    n = int(total * SR)
    out = np.zeros(n)
    prog = [(48, (60, 64, 67)), (45, (57, 60, 64)), (41, (53, 57, 60)), (43, (55, 59, 62))]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    nb = int(total / beat) + 1
    for b in range(nb):
        root, chord = prog[(b // 4) % 4]
        s0 = int(b * beat * SR)
        # bass on every beat, octave bounce
        d = beat * 0.9
        t = t_axis(d)
        f = hz(root + (12 if b % 2 else 0))
        bass = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * env(len(t), 0.004, 0.18) * 0.35
        # off-beat chord pluck
        t2 = t_axis(beat * 0.5)
        pl = sum(np.sign(np.sin(2 * np.pi * hz(m) * t2)) * 0.06 for m in chord) * env(len(t2), 0.002, 0.07)
        # hats
        hat = hp(noise(0.04), 0.6) * env(int(0.04 * SR), 0.0005, 0.01) * 0.18
        for seg, off in ((bass, 0), (pl, int(beat * 0.5 * SR)), (hat, int(beat * 0.5 * SR))):
            o = s0 + off
            if o < n:
                out[o:o + len(seg)] += seg[: n - o]
        # simple melody on beats 1 and 3
        if b % 2 == 0:
            m = chord[(b // 2) % 3] + 12
            t3 = t_axis(beat * 0.8)
            mel = np.sin(2 * np.pi * hz(m) * t3) * env(len(t3), 0.003, 0.2) * 0.12
            out[s0:s0 + len(mel)] += mel[: n - s0]
    hum_t = np.arange(n) / SR
    hum = (np.sin(2 * np.pi * 55 * hum_t) + 0.5 * np.sin(2 * np.pi * 82.4 * hum_t)
           + 0.25 * np.sin(2 * np.pi * 110.3 * hum_t)) * 0.12 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.5 * hum_t))
    return out, hum


# --------------------------------------------------------------------- cues
def cues():
    c = []
    add = lambda shot, t, snd, g=1.0: c.append((at(shot, t), snd, g))
    add(1, 0.0, sparkle(), 0.6)
    add(2, 0.1, zap(1.6), 0.35)
    add(2, 0.3, whoosh(0.5), 0.5)
    add(2, 0.35, thud(90, 0.3), 0.6)
    add(3, 0.0, pop(900), 0.8)
    add(4, 0.0, whoosh(0.6), 0.8)
    add(5, 0.22, thud(60), 0.9)
    add(6, 0.2, coo(), 0.7)
    add(6, 0.8, coo(), 0.6)
    add(7, 0.0, pop(500), 0.8)
    add(7, 0.4, coo(), 0.7)
    add(9, 0.25, pop(800), 0.8)
    add(11, 0.25, sparkle(), 0.5)
    for shot, ts in ((12, 0.25), (16, 1.0), (21, 0.35), (22, 0.3), (36, 0.2), (54, 0.35)):
        add(shot, ts, snap(), 1.0)
        add(shot, ts + 0.02, pause_sweep(), 0.7)
    add(14, 0.0, whoosh(0.5, up=True), 0.6)
    add(15, 0.5, whoosh(0.3, up=False), 0.3)
    add(17, 0.2, pop(1000), 0.6)
    add(18, 0.0, pop(400), 0.5)
    add(19, 0.0, whoosh(0.4), 0.3)
    add(20, 0.1, pop(800), 0.8)
    add(23, 0.3, pop(1100), 0.6)
    add(24, 0.2, crunch(0.2), 0.6)
    add(25, 0.5, whoosh(0.35, up=False), 0.6)
    add(25, 0.85, thud(80), 0.9)
    add(25, 0.9, boing(), 0.6)
    add(26, 0.5, pop(950), 0.9)
    add(27, 0.0, cheer(1.4), 0.5)
    add(28, 0.1, thud(45, 0.5), 1.0)
    add(29, 0.0, whoosh(1.1), 0.8)
    add(30, 0.2, boing(), 0.3)
    add(31, 0.2, pop(1100), 0.6)
    add(32, 0.35, ding(1568), 0.9)
    add(33, 0.05, crunch(0.15), 0.3)
    add(34, 0.3, crunch(0.15), 0.3)
    add(35, 0.1, ding(2093), 0.5)
    add(37, 0.0, pop(300), 0.4)
    add(38, 0.3, whoosh(0.6, up=False), 0.3)
    for k in range(3):
        add(39, 0.05 + k * 0.3, thud(110, 0.2), 0.5)
    add(40, 0.1, thud(50, 0.6), 1.0)
    add(40, 0.1, pop(1100), 0.5)
    add(42, 0.35, whoosh(0.4, up=False), 0.25)
    add(43, 0.35, snap(), 1.0)
    for k in range(4):
        add(44, 0.1 + k * 0.3, snap(), 0.9)
    add(45, 0.0, thud(70, 0.3), 0.7)
    add(47, 0.0, ding(523), 0.25)
    add(48, 0.35, pop(1000), 0.9)
    for k in range(5):
        add(49, 0.05 + k * 0.13, crunch(0.1), 1.0)
    for k in range(3):
        add(50, 0.05 + k * 0.15, crunch(0.1), 0.8)
    add(51, 0.0, whoosh(0.9), 1.0)
    for k in range(6):
        add(52, 0.05 + k * 0.14, crunch(0.1), 0.9)
    add(53, 0.1, sparkle(), 0.7)
    add(55, 0.1, sparkle(), 0.8)
    for k in range(3):
        add(56, 0.05 + k * 0.6, pop(600 + 200 * k), 0.6)
    add(57, 0.3, pop(500), 0.4)
    add(59, 0.7, snap(), 1.0)
    add(59, 0.72, whoosh(0.5, up=True), 0.8)
    add(60, 0.0, sparkle(), 0.6)
    add(61, 0.05, pop(800), 0.6)
    add(61, 0.35, pop(900), 0.6)
    add(62, 0.0, cheer(1.6), 1.0)
    add(62, 0.0, sparkle(), 0.5)
    add(63, 0.1, cheer(0.9), 0.6)
    add(64, 0.1, ding(1047), 0.9)
    add(65, 0.2, crunch(0.15), 0.6)
    return c


# ---------------------------------------------------------------------- io
def write_wav(path, x):
    x = np.clip(x, -1, 1)
    st = np.stack([x, x], axis=1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


def loudnorm_filter(raw, voice=None):
    """Two-pass loudnorm to -14 LUFS: measure first, then normalise linearly with the measured values."""
    import json
    base = "loudnorm=I=-14:TP=-1.5:LRA=11"
    if voice:
        inputs = ["-i", voice, "-i", raw]
        graph = [f"-filter_complex", f"[0:a]aformat=sample_rates={SR}:channel_layouts=stereo[v];"
                 f"[v][1:a]amix=inputs=2:normalize=0,{base}:print_format=json"]
    else:
        inputs = ["-i", raw]
        graph = ["-af", f"{base}:print_format=json"]
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats"] + inputs + graph + ["-f", "null", "-"],
                       capture_output=True, text=True)
    txt = r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1]
    m = json.loads(txt)
    return (f"{base}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
            f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")


MUSIC_DB_VOICE = -13  # music level (re. the voice reference) when narration is mixed in


def db(x):
    return 10 ** (x / 20)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", help="narration file; when given the music is ducked under it")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    n = int(TOTAL * SR)

    bed, hum = music_bed(TOTAL)
    paused = np.zeros(n)
    for s, e in (span(x, y) for x, y in PAUSED):
        paused[int(s * SR):int(e * SR)] = 1.0
    k = int(0.06 * SR)
    paused = np.convolve(paused, np.ones(k) / k, mode="same")  # 60 ms crossfade into / out of the hum
    music = bed * (1 - paused) + hum * paused

    sfx = np.zeros(n)
    for t0, snd, g in cues():
        o = int(t0 * SR)
        if o >= n:
            continue
        sfx[o:o + len(snd)] += g * snd[: n - o]

    # levels: voice reference at 0 dB; music ~11 dB under it, effects ~5 dB under it
    music *= db(MUSIC_DB_VOICE if a.voice else -11) / max(1e-6, np.sqrt(np.mean(bed ** 2)) / 0.2)
    sfx *= db(-6 if a.voice else -5)
    mix = music + sfx
    tail = int(0.02 * SR)
    mix[-tail:] = 0.0  # hard cut to silence at the end
    write_wav(out_name("music.wav"), music)
    write_wav(out_name("sfx.wav"), sfx)
    raw = out_name("_mix_raw.wav")
    write_wav(raw, mix / max(1.0, np.abs(mix).max()))
    filt = loudnorm_filter(raw, a.voice)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", raw]
    if a.voice:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", a.voice, "-i", raw, "-filter_complex",
               f"[0:a]aformat=sample_rates={SR}:channel_layouts=stereo[v];[v][1:a]amix=inputs=2:normalize=0,{filt}"]
    else:
        cmd += ["-af", filt]
    cmd += ["-ar", str(SR), out_name("mix.wav")]
    subprocess.run(cmd, check=True)
    os.remove(raw)
    print(f"wrote {out_name('music.wav')}, sfx.wav, mix.wav ({TOTAL:.2f} s, {len(cues())} effects)")


if __name__ == "__main__":
    main()
