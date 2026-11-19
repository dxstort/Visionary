"""Thumbnails for The Birthday Wish: out/wish_thumbnail_vertical.png (1080x1920), out/wish_thumbnail.png (1280x720).
Stills (caption-free renders): out/_wthumb_jetpack.png (shot 13), out/_wthumb_note.png (shot 36)."""
import os

from PIL import Image, ImageDraw

from porch_thumbnail import split_h
from thumbnail import INK, WHITE, YELLOW, cover, fit_px, line, text, vignette

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def vertical(jet, note):
    W, H, mid, sl = 1080, 1920, 900, 70
    top = cover(jet, W, mid + sl + 10, cx=0.42, cy=0.2, zoom=1.0)
    bot = cover(note, W, H - (mid - sl - 10), cx=0.5, cy=0.36, zoom=1.0)
    img = vignette(split_h(W, H, top, bot, mid, sl), 0.3)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2, 140), "I WANTED A JETPACK...", fit_px("I WANTED A JETPACK...", 140, W - 70), WHITE)
    text(d, (W / 2, 1480), "...THEN I FOUND", fit_px("...THEN I FOUND", 130, W - 80), WHITE)
    text(d, (W / 2, 1640), "HIS NOTE", fit_px("HIS NOTE", 200, W - 80), YELLOW)
    return img


def landscape(jet, note):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H))
    img.paste(cover(jet, W // 2, H, cx=0.42, cy=0.27, zoom=1.0), (0, 0))
    img.paste(cover(note, W // 2, H, cx=0.5, cy=0.33, zoom=1.0), (W // 2, 0))
    d = ImageDraw.Draw(img)
    for col, wd in ((INK, 26), (WHITE, 12)):
        d.line([(W // 2, -10), (W // 2, H + 10)], fill=col, width=wd)
    img = vignette(img, 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 4, 75), "MY WISH: JETPACK", fit_px("MY WISH: JETPACK", 80, W // 2 - 40), WHITE)
    text(d, (W * 3 / 4, 75), "HIS WISH...", fit_px("HIS WISH...", 90, W // 2 - 40), YELLOW)
    line(d, 650, [("MY BROTHER'S", 66, WHITE), ("SECRET WISH", 92, YELLOW)], W - 70)
    return img


def main():
    jet = Image.open(os.path.join(OUT, "_wthumb_jetpack.png")).convert("RGB")
    note = Image.open(os.path.join(OUT, "_wthumb_note.png")).convert("RGB")
    vertical(jet, note).save(os.path.join(OUT, "wish_thumbnail_vertical.png"))
    landscape(jet, note).save(os.path.join(OUT, "wish_thumbnail.png"))
    print("wrote out/wish_thumbnail_vertical.png, out/wish_thumbnail.png")


if __name__ == "__main__":
    main()
