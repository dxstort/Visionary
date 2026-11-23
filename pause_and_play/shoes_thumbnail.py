"""Thumbnails for The Walking Shoes: out/shoes_thumbnail_vertical.png (1080x1920), out/shoes_thumbnail.png (1280x720).
Stills (caption-free renders): out/_sthumb_back.png, out/_sthumb_win.png."""
import os

from PIL import Image, ImageDraw

from porch_thumbnail import split_h
from thumbnail import INK, WHITE, YELLOW, cover, fit_px, text, vignette

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def vertical(top_im, bot_im):
    W, H, mid, sl = 1080, 1920, 900, 70
    top = cover(top_im, W, mid + sl + 10, cx=0.75, cy=0.4, zoom=1.1)
    bot = cover(bot_im, W, H - (mid - sl - 10), cx=0.5, cy=0.3, zoom=1.0)
    img = vignette(split_h(W, H, top, bot, mid, sl), 0.3)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2, 610), "MY SHOES", fit_px("MY SHOES", 120, W - 70), WHITE)
    text(d, (W / 2, 750), "WALK ME", fit_px("WALK ME", 160, W - 70), YELLOW)
    text(d, (W / 2, 1480), "AROUND...", fit_px("AROUND...", 120, W - 80), WHITE)
    text(d, (W / 2, 1640), "TO THE WIN", fit_px("TO THE WIN", 200, W - 80), YELLOW)
    return img


def landscape(top_im, bot_im):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H))
    img.paste(cover(top_im, W // 2, H, cx=0.78, cy=0.4, zoom=1.0), (0, 0))
    img.paste(cover(bot_im, W // 2, H, cx=0.5, cy=0.3, zoom=1.0), (W // 2, 0))
    d = ImageDraw.Draw(img)
    for col, wd in ((INK, 26), (WHITE, 12)):
        d.line([(W // 2, -10), (W // 2, H + 10)], fill=col, width=wd)
    img = vignette(img, 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 4, 640), "WALKING SHOES", fit_px("WALKING SHOES", 100, W // 2 - 50), WHITE)
    text(d, (W * 3 / 4, 640), "THE WIN", fit_px("THE WIN", 110, W // 2 - 50), YELLOW)
    return img


def main():
    a = Image.open(os.path.join(OUT, "_sthumb_back.png")).convert("RGB")
    b = Image.open(os.path.join(OUT, "_sthumb_win.png")).convert("RGB")
    vertical(a, b).save(os.path.join(OUT, "shoes_thumbnail_vertical.png"))
    landscape(a, b).save(os.path.join(OUT, "shoes_thumbnail.png"))
    print("wrote out/shoes_thumbnail_vertical.png, out/shoes_thumbnail.png")


if __name__ == "__main__":
    main()
