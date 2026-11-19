"""Thumbnails for The Floating Laughs: out/laughs_thumbnail_vertical.png (1080x1920), out/laughs_thumbnail.png
(1280x720). Stills (caption-free renders): out/_lthumb_grumpy.png (shot 19), out/_lthumb_fly.png (shot 44)."""
import os

from PIL import Image, ImageDraw

from porch_thumbnail import split_h
from thumbnail import INK, WHITE, YELLOW, cover, fit_px, line, text, vignette

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def vertical(grumpy, fly):
    W, H, mid, sl = 1080, 1920, 900, 70
    top = cover(grumpy, W, mid + sl + 10, cx=0.5, cy=0.33, zoom=1.0)
    bot = cover(fly, W, H - (mid - sl - 10), cx=0.5, cy=0.42, zoom=1.05)
    img = vignette(split_h(W, H, top, bot, mid, sl), 0.3)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2, 140), "HE NEVER LAUGHS...", fit_px("HE NEVER LAUGHS...", 140, W - 70), WHITE)
    text(d, (W / 2, 1440), "...OR HE'D", fit_px("...OR HE'D", 140, W - 80), WHITE)
    text(d, (W / 2, 1610), "FLOAT AWAY!", fit_px("FLOAT AWAY!", 200, W - 80), YELLOW)
    return img


def landscape(grumpy, fly):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H))
    img.paste(cover(grumpy, W // 2, H, cx=0.5, cy=0.25, zoom=1.0), (0, 0))
    img.paste(cover(fly, W // 2, H, cx=0.5, cy=0.3, zoom=1.0), (W // 2, 0))
    d = ImageDraw.Draw(img)
    for col, wd in ((INK, 26), (WHITE, 12)):
        d.line([(W // 2, -10), (W // 2, H + 10)], fill=col, width=wd)
    img = vignette(img, 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 4, 80), "NEVER LAUGHS", fit_px("NEVER LAUGHS", 90, W // 2 - 40), WHITE)
    text(d, (W * 3 / 4, 80), "UNTIL...", fit_px("UNTIL...", 90, W // 2 - 40), YELLOW)
    line(d, 630, [("WHY GRANDPA WEARS", 64, WHITE), ("IRON BOOTS", 92, YELLOW)], W - 70)
    return img


def main():
    grumpy = Image.open(os.path.join(OUT, "_lthumb_grumpy.png")).convert("RGB")
    fly = Image.open(os.path.join(OUT, "_lthumb_fly.png")).convert("RGB")
    vertical(grumpy, fly).save(os.path.join(OUT, "laughs_thumbnail_vertical.png"))
    landscape(grumpy, fly).save(os.path.join(OUT, "laughs_thumbnail.png"))
    print("wrote out/laughs_thumbnail_vertical.png, out/laughs_thumbnail.png")


if __name__ == "__main__":
    main()
