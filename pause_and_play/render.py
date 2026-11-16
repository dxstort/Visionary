"""Render shots to frames and encode with ffmpeg.

    python3 render.py --shots 1-9 --out out/test_shots_1-9.mp4
    python3 render.py --still 5:0.6 --out out/still.png     (shot 5 at 0.6 s, with caption)
    python3 render.py --contact out/contact.png --shots 1-9 (one mid-frame per shot)
"""
import argparse
import os
import shutil
import subprocess
import sys
from multiprocessing import Pool

from PIL import Image

from engine import draw_caption
from shots import SHOTS, WORD_TIMES

FPS = 30


def word_times(text, dur):
    """No narration track yet: spread words over the shot, weighted by length."""
    words = text.split()
    w = [len(x.strip(".,?!")) + 3 for x in words]
    tot, acc, out = float(sum(w)), 0.0, []
    for word, wt in zip(words, w):
        out.append((acc / tot * dur, word))
        acc += wt
    return out


def timeline(first, last):
    """-> list of (shot index, local frame, shot frames) per output frame; cuts snapped to frames."""
    frames, acc = [], 0.0
    for i, (num, dur, _, _) in enumerate(SHOTS):
        if not first <= num <= last:
            continue
        start = round(acc * FPS)
        acc += dur
        n = round(acc * FPS) - start
        frames += [(i, f, n) for f in range(n)]
    return frames


def render_frame(si, f, captions=True):
    num, dur, text, fn = SHOTS[si]
    t = f / FPS
    img = fn(t, dur).render()
    if captions:
        cur = None
        for st, word in WORD_TIMES.get(num) or word_times(text, dur):
            if st <= t + 1e-6:
                cur = (st, word)
        if cur:
            img = draw_caption(img, cur[1], min(1.0, (round((t - cur[0]) * FPS) + 1) / 3))
    return img


def _job(a):
    idx, si, f, tmp = a
    render_frame(si, f).save(os.path.join(tmp, f"f{idx:05d}.png"), compress_level=1)
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", default="1-9")
    ap.add_argument("--out", default="out/test.mp4")
    ap.add_argument("--still")
    ap.add_argument("--contact")
    ap.add_argument("--tmp", default="/tmp/claude-0/-home-user-Visionary/baff548d-c254-5f6a-95a3-85890410ea9b/scratchpad/frames")
    a = ap.parse_args()
    first, last = (int(x) for x in a.shots.split("-"))

    if a.still:
        num, t = a.still.split(":")
        si = [i for i, s in enumerate(SHOTS) if s[0] == int(num)][0]
        render_frame(si, round(float(t) * FPS)).save(a.out)
        return
    if a.contact:
        sel = [i for i, s in enumerate(SHOTS) if first <= s[0] <= last]
        cols = min(len(sel), 5)
        rows = (len(sel) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 360, rows * 640), (20, 20, 20))
        for k, si in enumerate(sel):
            f = int(SHOTS[si][1] * FPS * 0.62)
            sheet.paste(render_frame(si, f).resize((360, 640), Image.LANCZOS), ((k % cols) * 360, (k // cols) * 640))
        sheet.save(a.contact)
        return

    frames = timeline(first, last)
    shutil.rmtree(a.tmp, ignore_errors=True)
    os.makedirs(a.tmp)
    jobs = [(idx, si, f, a.tmp) for idx, (si, f, _) in enumerate(frames)]
    with Pool(4) as pool:
        for k, _ in enumerate(pool.imap_unordered(_job, jobs, chunksize=4)):
            if k % 60 == 0:
                print(f"  {k}/{len(jobs)} frames", flush=True)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(a.tmp, "f%05d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", a.out], check=True)
    print(f"wrote {a.out}: {len(frames)} frames, {len(frames) / FPS:.2f} s")


if __name__ == "__main__":
    sys.exit(main())
