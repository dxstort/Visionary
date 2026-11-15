"""Render shots with the Blender backend (run with the Python that has bpy).

    $BVENV/bin/python render_bl.py --shots 1-9 --out out/test_shots_1-9.mp4
    $BVENV/bin/python render_bl.py --still 8:0.9 --out out/still.png
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

import bl_backend  # noqa: F401  (patches engine.Scene before shots is imported)
import render
from render import FPS, render_frame, timeline
from shots import SHOTS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", default="1-9")
    ap.add_argument("--out", default="out/test.mp4")
    ap.add_argument("--still")
    ap.add_argument("--tmp", default="/tmp/claude-0/-home-user-Visionary/baff548d-c254-5f6a-95a3-85890410ea9b/scratchpad/bframes")
    ap.add_argument("--resume", action="store_true", help="keep frames already rendered in --tmp")
    ap.add_argument("--part", default="0/1", help="k/n: render every n-th frame starting at k (parallel workers)")
    ap.add_argument("--encode-only", action="store_true")
    ap.add_argument("--contact", help="write one mid-shot frame per shot as a contact sheet")
    a = ap.parse_args()

    if a.still:
        num, t = a.still.split(":")
        si = [i for i, s in enumerate(SHOTS) if s[0] == int(num)][0]
        t0 = time.time()
        render_frame(si, round(float(t) * FPS)).save(a.out)
        print(f"wrote {a.out} in {time.time() - t0:.1f} s")
        return

    first, last = (int(x) for x in a.shots.split("-"))
    if a.contact:
        from PIL import Image
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
    k_part, n_part = (int(x) for x in a.part.split("/"))
    if a.encode_only:
        return encode(a, frames)
    if not a.resume:
        shutil.rmtree(a.tmp, ignore_errors=True)
    os.makedirs(a.tmp, exist_ok=True)
    t0 = time.time()
    for idx, (si, f, _) in enumerate(frames):
        if idx % n_part != k_part:
            continue
        path = os.path.join(a.tmp, f"f{idx:05d}.png")
        if a.resume and os.path.exists(path):
            continue
        render_frame(si, f).save(path, compress_level=1)
        if idx % 15 == 0:
            el = time.time() - t0
            print(f"  {idx + 1}/{len(frames)} frames, {el / (idx + 1):.1f} s/frame", flush=True)
    if n_part > 1:
        print(f"part {a.part} done in {time.time() - t0:.0f} s")
        return
    encode(a, frames)


def encode(a, frames):
    missing = [i for i in range(len(frames)) if not os.path.exists(os.path.join(a.tmp, f"f{i:05d}.png"))]
    if missing:
        raise SystemExit(f"{len(missing)} frames missing, first {missing[:5]}")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(a.tmp, "f%05d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", a.out], check=True)
    print(f"wrote {a.out}: {len(frames)} frames, {len(frames) / FPS:.2f} s")


if __name__ == "__main__":
    sys.exit(main())
