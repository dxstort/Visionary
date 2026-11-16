"""Fit the video to a recorded voiceover.

    python3 voice_align.py voiceover.mp3 [--speed 1.1]

1. Cleans the voice (high-pass, optional tempo-up with pitch kept, light compression, -15 LUFS)
   -> out/_voice_pre.wav
2. Force-aligns the shot-list text to it with pocketsphinx (pip install pocketsphinx; English
   model is bundled, nothing downloaded) to get every word's onset.
3. Writes voice_timing.json: per-shot duration (each cut lands just before the shot's first
   spoken word) and per-word caption times. shots.py picks this file up automatically.

Then: python3 audio.py --voice out/_voice_pre.wav, and re-render.
"""
import argparse
import json
import os
import re
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
_vt = os.path.join(HERE, "voice_timing.json")
if os.path.exists(_vt):  # align against the shot list's own text, not a previous timing
    os.rename(_vt, _vt + ".old")
from shots import SHOTS  # noqa: E402

NUM = {"3": "three", "4": "four", "9": "nine", "10": "ten", "40": "forty", "50": "fifty", "100": "one hundred"}
EXTRA = {"brax": "B R AE K S", "brax's": "B R AE K S IH Z", "unpause": "AH N P AO Z"}
LEAD = 0.08   # cut this long before the first word of each shot
TAIL = 0.85   # hold after the last word (covers the dip to black)


def spoken(word):
    k = re.sub(r"[^\w']", "", word)
    return NUM.get(k, k).lower().split()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("voice")
    ap.add_argument("--speed", type=float, default=1.0, help="tempo factor (pitch kept), e.g. 1.1 to fit 90 s")
    a = ap.parse_args()
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    pre = os.path.join(HERE, "out", "_voice_pre.wav")
    tempo = f"atempo={a.speed}," if a.speed != 1.0 else ""
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.voice, "-af",
                    f"highpass=f=80,{tempo}acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
                    "loudnorm=I=-15:TP=-2:LRA=7", "-ar", "48000", "-ac", "1", pre], check=True)

    from pocketsphinx import Decoder
    words = [w for _, _, txt, _ in SHOTS for tok in txt.split() for w in spoken(tok)]
    with tempfile.NamedTemporaryFile(suffix=".raw") as raw:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.voice, "-ar", "16000", "-ac", "1", "-f", "s16le",
                        raw.name], check=True)
        dec = Decoder(samprate=16000, bestpath=False)
        for w, ph in EXTRA.items():
            dec.add_word(w, ph, True)
        dec.set_align_text(" ".join(words))
        dec.start_utt()
        dec.process_raw(open(raw.name, "rb").read(), full_utt=True)
        dec.end_utt()
        # aligned at natural speed (more reliable), then scaled to the sped-up track
        seg = [(s.start_frame / 100 / a.speed, (s.end_frame + 1) / 100 / a.speed) for s in dec.seg()
               if s.word not in ("<s>", "</s>", "<sil>")]
    assert len(seg) == len(words), f"aligned {len(seg)} of {len(words)} words"

    k, shots = 0, []
    for num, _, txt, _ in SHOTS:
        toks = []
        for tok in txt.split():
            toks.append((seg[k][0], tok))
            k += len(spoken(tok))
        shots.append((num, toks))
    starts = [0.0] + [toks[0][0] - LEAD for _, toks in shots[1:]] + [seg[-1][1] + TAIL]
    out = {num: dict(dur=round(starts[i + 1] - starts[i], 3),
                     words=[[round(max(0.0, t - starts[i]), 3), w] for t, w in toks])
           for i, (num, toks) in enumerate(shots)}
    json.dump(out, open(_vt, "w"), indent=0)
    if os.path.exists(_vt + ".old"):
        os.remove(_vt + ".old")
    print(f"wrote voice_timing.json: {starts[-1]:.2f} s, {len(seg)} words; voice -> {pre}")


if __name__ == "__main__":
    main()
