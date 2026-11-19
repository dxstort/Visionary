"""Thumbnails for The Porch Light: out/porch_thumbnail_vertical.png (1080x1920), out/porch_thumbnail.png (1280x720).

Stills (caption-free renders): out/_pthumb_sad.png (shot 47) and out/_pthumb_bright.png (shot 57), e.g.
    STORY=porch <bpy python> -c "import bl_backend; from render import render_frame; ..."
"""
import os

from PIL import Image, ImageDraw

from thumbnail import INK, WHITE, YELLOW, cover, fit_px, line, text, vignette

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def split_h(W, H, top, bot, mid, sl):
    img = Image.new("RGB", (W, H))
    img.paste(top, (0, 0))
    low = Image.new("RGB", (W, H))
    low.paste(bot, (0, mid - sl - 10))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(0, mid + sl), (W, mid - sl), (W, H), (0, H)], fill=255)
    img.paste(low, (0, 0), m)
    d = ImageDraw.Draw(img)
    for col, wd in ((INK, 30), (WHITE, 16)):
        d.line([(-10, mid + sl), (W + 10, mid - sl)], fill=col, width=wd)
    return img


def vertical(sad, on):
    W, H, mid, sl = 1080, 1920, 900, 70
    top = cover(sad, W, mid + sl + 10, cx=0.47, cy=0.36, zoom=1.7)
    bot = cover(on, W, H - (mid - sl - 10), cx=0.5, cy=0.38, zoom=1.25)
    img = vignette(split_h(W, H, top, bot, mid, sl), 0.35)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2, 140), "DARK FOR 30 YEARS...", fit_px("DARK FOR 30 YEARS...", 140, W - 70), WHITE)
    text(d, (W / 2, 1440), "...UNTIL I SAID", fit_px("...UNTIL I SAID", 130, W - 80), WHITE)
    text(d, (W / 2, 1610), "THANK YOU", fit_px("THANK YOU", 200, W - 80), YELLOW)
    return img


def landscape(sad, on):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H))
    img.paste(cover(sad, W // 2, H, cx=0.47, cy=0.4, zoom=1.5), (0, 0))
    img.paste(cover(on, W // 2, H, cx=0.5, cy=0.32, zoom=1.15), (W // 2, 0))
    d = ImageDraw.Draw(img)
    for col, wd in ((INK, 26), (WHITE, 12)):
        d.line([(W // 2, -10), (W // 2, H + 10)], fill=col, width=wd)
    img = vignette(img, 0.3)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 4, 80), "30 YEARS DARK", fit_px("30 YEARS DARK", 90, W // 2 - 40), WHITE)
    text(d, (W * 3 / 4, 80), "ONE NOTE...", fit_px("ONE NOTE...", 90, W // 2 - 40), YELLOW)
    line(d, 630, [("HIS LIGHT TURNED", 70, WHITE), ("ON", 110, YELLOW)], W - 80)
    return img


def main():
    sad = Image.open(os.path.join(OUT, "_pthumb_sad.png")).convert("RGB")
    on = Image.open(os.path.join(OUT, "_pthumb_bright.png")).convert("RGB")  # shot 57: his house, brightest
    vertical(sad, on).save(os.path.join(OUT, "porch_thumbnail_vertical.png"))
    landscape(sad, on).save(os.path.join(OUT, "porch_thumbnail.png"))
    print("wrote out/porch_thumbnail_vertical.png, out/porch_thumbnail.png")


if __name__ == "__main__":
    main()
