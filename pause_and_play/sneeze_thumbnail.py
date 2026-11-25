"""Thumbnails for When You SNEEZE, You SWITCH Places: out/sneeze_thumbnail_vertical.png (1080x1920),
out/sneeze_thumbnail.png (1280x720).
Stills (caption-free renders, made on the first run): out/_snthumb_before.png (the sneeze, shot 28) and
out/_snthumb_after.png (the swap, shot 29)."""
import os

os.environ.setdefault("STORY", "sneeze")
from PIL import Image, ImageDraw  # noqa: E402

from porch_thumbnail import split_h  # noqa: E402
from thumbnail import INK, WHITE, YELLOW, cover, fit_px, text, vignette  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
STILLS = {"_snthumb_before.png": (28, 1.55), "_snthumb_after.png": (29, 0.72)}


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
    bot = cover(bot_im, W, H - (mid - sl - 10), cx=0.5, cy=0.42, zoom=1.15)
    img = vignette(split_h(W, H, top, bot, mid, sl), 0.3)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2, 150), "ACHOO!", fit_px("ACHOO!", 230, W - 70), YELLOW)
    text(d, (W / 2, 1440), "SNEEZE = SWITCH", fit_px("SNEEZE = SWITCH", 120, W - 80), WHITE)
    text(d, (W / 2, 1620), "PLACES!", fit_px("PLACES!", 220, W - 80), YELLOW)
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
    text(d, (W / 4, 640), "ACHOO!", fit_px("ACHOO!", 120, W // 2 - 50), YELLOW)
    text(d, (W * 3 / 4, 640), "SWITCH!", fit_px("SWITCH!", 120, W // 2 - 50), WHITE)
    return img


def main():
    make_stills()
    a = Image.open(os.path.join(OUT, "_snthumb_before.png")).convert("RGB")
    b = Image.open(os.path.join(OUT, "_snthumb_after.png")).convert("RGB")
    vertical(a, b).save(os.path.join(OUT, "sneeze_thumbnail_vertical.png"))
    landscape(a, b).save(os.path.join(OUT, "sneeze_thumbnail.png"))
    print("wrote out/sneeze_thumbnail_vertical.png, out/sneeze_thumbnail.png")


if __name__ == "__main__":
    main()
