"""Thumbnails for The Toaster Robot: out/robot_thumbnail_vertical.png (1080x1920), out/robot_thumbnail.png (1280x720).
Stills (caption-free renders): out/_rthumb_turbo.png (shot 5), out/_rthumb_hug.png (shot 18)."""
import os

from PIL import Image, ImageDraw

from porch_thumbnail import split_h
from thumbnail import INK, WHITE, YELLOW, cover, fit_px, text, vignette

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def vertical(turbo, hug):
    W, H, mid, sl = 1080, 1920, 900, 70
    top = cover(turbo, W, mid + sl + 10, cx=0.5, cy=0.3, zoom=1.15)
    bot = cover(hug, W, H - (mid - sl - 10), cx=0.5, cy=0.3, zoom=1.0)
    img = vignette(split_h(W, H, top, bot, mid, sl), 0.3)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2, 610), "HIS ROBOT:", fit_px("HIS ROBOT:", 120, W - 70), WHITE)
    text(d, (W / 2, 750), "A SPORTS CAR", fit_px("A SPORTS CAR", 150, W - 70), YELLOW)
    text(d, (W / 2, 1480), "MINE:", fit_px("MINE:", 120, W - 80), WHITE)
    text(d, (W / 2, 1640), "A TOASTER", fit_px("A TOASTER", 200, W - 80), YELLOW)
    return img


def landscape(turbo, hug):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H))
    img.paste(cover(turbo, W // 2, H, cx=0.5, cy=0.33, zoom=1.0), (0, 0))
    img.paste(cover(hug, W // 2, H, cx=0.5, cy=0.28, zoom=1.0), (W // 2, 0))
    d = ImageDraw.Draw(img)
    for col, wd in ((INK, 26), (WHITE, 12)):
        d.line([(W // 2, -10), (W // 2, H + 10)], fill=col, width=wd)
    img = vignette(img, 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 4, 640), "SPORTS CAR", fit_px("SPORTS CAR", 100, W // 2 - 50), WHITE)
    text(d, (W * 3 / 4, 640), "TOASTER", fit_px("TOASTER", 110, W // 2 - 50), YELLOW)
    d.ellipse([W / 2 - 70, H / 2 - 70, W / 2 + 70, H / 2 + 70], fill=(230, 60, 60), outline=INK, width=8)
    text(d, (W / 2, H / 2), "VS", 80, WHITE)
    return img


def main():
    turbo = Image.open(os.path.join(OUT, "_rthumb_turbo.png")).convert("RGB")
    hug = Image.open(os.path.join(OUT, "_rthumb_hug.png")).convert("RGB")
    vertical(turbo, hug).save(os.path.join(OUT, "robot_thumbnail_vertical.png"))
    landscape(turbo, hug).save(os.path.join(OUT, "robot_thumbnail.png"))
    print("wrote out/robot_thumbnail_vertical.png, out/robot_thumbnail.png")


if __name__ == "__main__":
    main()
