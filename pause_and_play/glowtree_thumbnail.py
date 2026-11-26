"""Thumbnails for When Trees Light Up at LUNCH: out/glowtree_thumbnail_vertical.png (1080x1920),
out/glowtree_thumbnail.png (1280x720).
Stills (caption-free renders, made on the first run): out/_gtthumb_before.png (the pink maple glowing, shot 2) and
out/_gtthumb_after.png (the gold pine blazing, shot 33)."""
import os

os.environ.setdefault("STORY", "glowtree")
from PIL import Image, ImageDraw  # noqa: E402

from porch_thumbnail import split_h  # noqa: E402
from thumbnail import INK, WHITE, YELLOW, cover, fit_px, text, vignette  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
STILLS = {"_gtthumb_before.png": (2, 0.9), "_gtthumb_after.png": (33, 0.9)}


def make_stills():
    import render
    for name, (shot, t) in STILLS.items():
        path = os.path.join(OUT, name)
        if os.path.exists(path):
            continue
        si = [i for i, s in enumerate(render.SHOTS) if s[0] == shot][0]
        render.render_frame(si, round(t * render.FPS), captions=False).save(path)


def vertical(top_im, bot_im):
    W, H, mid, sl = 1080, 1920, 900, 70
    top = cover(top_im, W, mid + sl + 10, cx=0.5, cy=0.42, zoom=1.2)
    bot = cover(bot_im, W, H - (mid - sl - 10), cx=0.5, cy=0.54, zoom=1.0)
    img = vignette(split_h(W, H, top, bot, mid, sl), 0.3)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2, 150), "WHISPER!", fit_px("WHISPER!", 230, W - 70), YELLOW)
    text(d, (W / 2, 1440), "TELL A SECRET", fit_px("TELL A SECRET", 120, W - 80), WHITE)
    text(d, (W / 2, 1620), "TREES GLOW!", fit_px("TREES GLOW!", 220, W - 80), YELLOW)
    return img


def landscape(top_im, bot_im):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H))
    img.paste(cover(top_im, W // 2, H, cx=0.5, cy=0.42, zoom=1.0), (0, 0))
    img.paste(cover(bot_im, W // 2, H, cx=0.5, cy=0.42, zoom=1.0), (W // 2, 0))
    d = ImageDraw.Draw(img)
    for col, wd in ((INK, 26), (WHITE, 12)):
        d.line([(W // 2, -10), (W // 2, H + 10)], fill=col, width=wd)
    img = vignette(img, 0.25)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 4, 640), "WHISPER!", fit_px("WHISPER!", 120, W // 2 - 50), YELLOW)
    text(d, (W * 3 / 4, 640), "IT GLOWS!", fit_px("IT GLOWS!", 120, W // 2 - 50), WHITE)
    return img


def main():
    make_stills()
    a = Image.open(os.path.join(OUT, "_gtthumb_before.png")).convert("RGB")
    b = Image.open(os.path.join(OUT, "_gtthumb_after.png")).convert("RGB")
    vertical(a, b).save(os.path.join(OUT, "glowtree_thumbnail_vertical.png"))
    landscape(a, b).save(os.path.join(OUT, "glowtree_thumbnail.png"))
    print("wrote out/glowtree_thumbnail_vertical.png, out/glowtree_thumbnail.png")


if __name__ == "__main__":
    main()
