"""Stage 1: character sheet (full body + 4 expressions per cast member)."""
import os
import sys

from PIL import Image, ImageDraw

from cast import BRAX, DAD, HERO, MAYOR, PIP, TUCK, character
from engine import Scene, font

ROWS = [
    (HERO, ["smirk", "shock", "grit", "sparkle"], "HERO", "yellow bucket hat with pause pin, clock hoodie"),
    (PIP, ["smile", "smug", "chew0", "sparkle"], "PIP", "little sister, age 4, overalls"),
    (TUCK, ["grin", "shock", "grit", "sparkle"], "TUCK", "flying, goggles + cape"),
    (BRAX, ["laugh", "shock", "grit", "smirk"], "BRAX", "super strength, shades"),
    (DAD, ["smile", "shock", "miserable", "sparkle"], "DAD", "talks to pigeons"),
    (MAYOR, ["smile", "shock", "grit", "sleep"], "MAYOR BIGSBY", "top hat, sash, weighs a LOT"),
]
BG = ((255, 244, 214), (255, 226, 180))


def body_cell(spec, w=420, h=470):
    hgt = (spec["leg"][1] + spec["torso"][1] + spec["head"][1]) * spec["s"]
    k = max(hgt + 0.5, spec["torso"][0] * spec["s"] * 1.9) / 3.3
    sc = Scene((2.6 * k, hgt * 0.5 + 0.9 * k, 8.5 * k), (0, hgt * 0.5 + 0.05, 0), fov=27, W=w, H=h, sky=BG, cy=0.47, post=False)
    sc.ground((238, 205, 150))
    character(sc, spec, yaw=18, face="smile", pose=dict(al=(0, 10), ar=(0, 10)))
    return sc.render()


def face_cell(spec, expr, w=300, h=300):
    s = spec["s"]
    hy = (spec["leg"][1] + spec["torso"][1] + spec["head"][1] * (0.72 if spec["style"] == "tophat" else 0.55)) * s
    d = 3.3 * s * spec["head"][0] + 0.6
    sc = Scene((0.5 * s, hy + 0.15 * s, d), (0, hy, 0), fov=30, W=w, H=h, sky=BG, cy=0.5, post=False)
    character(sc, spec, yaw=8, face=expr, shadow=False)
    return sc.render()


def main(out):
    W, rowh, top = 1800, 480, 150
    img = Image.new("RGB", (W, top + rowh * len(ROWS) + 30), (255, 248, 232))
    d = ImageDraw.Draw(img)
    d.text((W // 2, 62), "PAUSE & PLAY  —  CHARACTER SHEET", font=font(64), fill=(40, 28, 48), anchor="mm")
    d.text((W // 2, 118), "original blocky toy cast  ·  4 swap-in faces each", font=font(26), fill=(150, 110, 90),
           anchor="mm")
    for r, (spec, exprs, name, note) in enumerate(ROWS):
        y = top + r * rowh
        d.rounded_rectangle([20, y + 5, W - 20, y + rowh - 5], 28, fill=(255, 236, 200))
        img.paste(body_cell(spec), (40, y + 5))
        d.text((250, y + 440), name, font=font(30), fill=(40, 28, 48), anchor="mm", stroke_width=5,
               stroke_fill=(255, 236, 200))
        for i, e in enumerate(exprs):
            x = 500 + i * 320
            cell = face_cell(spec, e)
            mask = Image.new("L", cell.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, 299, 299], 24, fill=255)
            img.paste(cell, (x, y + 60), mask)
            d.text((x + 150, y + 392), e.rstrip("01").upper(), font=font(26), fill=(40, 28, 48), anchor="mm")
        d.text((500, y + 34), note, font=font(24), fill=(150, 110, 90), anchor="lm")
    img.save(out)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "out", "character_sheet.png"))
