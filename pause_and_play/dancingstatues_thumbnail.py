"""Thumbnails for When Secrets Make Statues Dance: out/dancingstatues_thumbnail_vertical.png (1080x1920),
out/dancingstatues_thumbnail.png (1280x720). Stills (caption-free renders): out/_dthumb_still.png, out/_dthumb_dance.png."""
import os

os.environ.setdefault("STORY", "dancingstatues")
from PIL import Image, ImageDraw  # noqa: E402

from porch_thumbnail import split_h  # noqa: E402
from thumbnail import INK, WHITE, YELLOW, cover, fit_px, text, vignette  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def stills():
    from render import FPS, render_frame
    from story import SHOTS
    for num, t, name in ((16, 0.5, "_dthumb_still.png"), (29, 1.2, "_dthumb_dance.png")):
        si = [i for i, s in enumerate(SHOTS) if s[0] == num][0]
        render_frame(si, round(t * FPS), captions=False).save(os.path.join(OUT, name))


def vertical(top_im, bot_im):
    W, H, mid, sl = 1080, 1920, 900, 70
    top = cover(top_im, W, mid + sl + 10, cx=0.5, cy=0.12, zoom=1.0)
    bot = cover(bot_im, W, H - (mid - sl - 10), cx=0.5, cy=0.45, zoom=1.0)
    img = vignette(split_h(W, H, top, bot, mid, sl), 0.3)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2, 600), "TELL A SECRET", fit_px("TELL A SECRET", 130, W - 70), WHITE)
    text(d, (W / 2, 745), "...AND", fit_px("...AND", 120, W - 70), YELLOW)
    text(d, (W / 2, 1530), "THE STATUES", fit_px("THE STATUES", 150, W - 80), WHITE)
    text(d, (W / 2, 1700), "DANCE!", fit_px("DANCE!", 230, W - 80), YELLOW)
    return img


def landscape(top_im, bot_im):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H))
    img.paste(cover(top_im, W // 2, H, cx=0.5, cy=0.3, zoom=1.0), (0, 0))
    img.paste(cover(bot_im, W // 2, H, cx=0.5, cy=0.45, zoom=1.0), (W // 2, 0))
    d = ImageDraw.Draw(img)
    for col, wd in ((INK, 26), (WHITE, 12)):
        d.line([(W // 2, -10), (W // 2, H + 10)], fill=col, width=wd)
    img = vignette(img, 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 4, 640), "SECRET?", fit_px("SECRET?", 110, W // 2 - 50), WHITE)
    text(d, (W * 3 / 4, 640), "THEY DANCE!", fit_px("THEY DANCE!", 110, W // 2 - 50), YELLOW)
    return img


def main():
    stills()
    a = Image.open(os.path.join(OUT, "_dthumb_still.png")).convert("RGB")
    b = Image.open(os.path.join(OUT, "_dthumb_dance.png")).convert("RGB")
    vertical(a, b).save(os.path.join(OUT, "dancingstatues_thumbnail_vertical.png"))
    landscape(a, b).save(os.path.join(OUT, "dancingstatues_thumbnail.png"))
    print("wrote out/dancingstatues_thumbnail_vertical.png, out/dancingstatues_thumbnail.png")


if __name__ == "__main__":
    main()
