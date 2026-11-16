"""Thumbnails: out/thumbnail_vertical.png (1080x1920, Shorts) and out/thumbnail.png (1280x720).

    <bpy python> thumbnail.py        (renders the two caption-free stills in Blender, then lays out)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
HERO, PIP = os.path.join(OUT, "_thumb_hero.png"), os.path.join(OUT, "_thumb_pip.png")

YELLOW, WHITE, INK = (255, 214, 10), (255, 255, 255), (16, 14, 30)


def render_stills():
    import bl_backend  # noqa: F401  (patch engine.Scene before shots import)
    from render import FPS, render_frame
    from shots import SHOTS
    idx = {s[0]: i for i, s in enumerate(SHOTS)}
    render_frame(idx[44], round(0.9 * FPS), captions=False).save(HERO)   # hero panicking, frozen time
    render_frame(idx[59], round(0.4 * FPS), captions=False).save(PIP)    # Pip, smug


def font(px):
    from engine import font as f
    return f(px)


def cover(img, w, h, cx=0.5, cy=0.5, zoom=1.0):
    """Scale to cover w x h (times zoom), crop around the relative centre (cx, cy)."""
    s = max(w / img.width, h / img.height) * zoom
    im = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x = min(max(0, round(im.width * cx - w / 2)), im.width - w)
    y = min(max(0, round(im.height * cy - h / 2)), im.height - h)
    return im.crop((x, y, x + w, y + h))


def text(d, xy, s, px, fill, stroke=None, anchor="mm"):
    stroke = stroke or max(6, px // 9)
    d.text((xy[0] + px // 18, xy[1] + px // 14), s, font=font(px), fill=(0, 0, 0, 150), anchor=anchor,
           stroke_width=stroke, stroke_fill=(0, 0, 0, 150))
    d.text(xy, s, font=font(px), fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=INK)


def fit_px(s, px, maxw):
    while font(px).getlength(s) > maxw and px > 20:
        px -= 4
    return px


def pause_icon(d, cx, cy, h, col=WHITE):
    w, g = h * 0.3, h * 0.22
    for x0 in (cx - g / 2 - w, cx + g / 2):
        d.rounded_rectangle([x0 - 8, cy - h / 2 - 8, x0 + w + 8, cy + h / 2 + 8], 14, fill=INK)
        d.rounded_rectangle([x0, cy - h / 2, x0 + w, cy + h / 2], 8, fill=col)


def play_icon(d, cx, cy, h, col=YELLOW):
    pts = [(cx - h * 0.4, cy - h / 2), (cx - h * 0.4, cy + h / 2), (cx + h * 0.5, cy)]
    d.polygon(pts, fill=INK, outline=INK, width=22)
    d.polygon(pts, fill=col)


def split(w, h, hero, pip, slant, mid=None):
    """Hero panel on the left, Pip panel on the right, slanted white divider centred at x = mid."""
    mid = w / 2 if mid is None else mid
    base = Image.new("RGB", (w, h))
    base.paste(hero, (0, 0))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([(mid + slant, 0), (w, 0), (w, h), (mid - slant, h)], fill=255)
    right = Image.new("RGB", (w, h))
    right.paste(pip, (w - pip.width, 0))
    base.paste(right, (0, 0), m)
    d = ImageDraw.Draw(base)
    for col, wd in ((INK, 30), (WHITE, 16)):
        d.line([(mid + slant, -10), (mid - slant, h + 10)], fill=col, width=wd)
    return base


def vignette(img, k=0.55):
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse([-w * 0.25, -h * 0.15, w * 1.25, h * 1.15], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(w // 6))
    dark = Image.new("RGB", (w, h), (8, 8, 30))
    return Image.composite(img, Image.blend(img, dark, k), m)


def line(d, y, parts, maxw):
    """Centred line of (text, px, colour) parts, shrunk together to fit maxw."""
    k = 1.0
    while True:
        ws = [font(round(px * k)).getlength(t) for t, px, _ in parts]
        gap = 24 * k
        if sum(ws) + gap * (len(parts) - 1) <= maxw:
            break
        k -= 0.04
    x = (d.im.size[0] - sum(ws) - gap * (len(parts) - 1)) / 2
    for (t, px, col), wd in zip(parts, ws):
        text(d, (x, y), t, round(px * k), col, anchor="lm")
        x += wd + gap
    return x


# source stills are 1080x1920; both faces sit ~27% down; the hero's face is centred, Pip's is at ~30% across
def vertical(hero, pip):
    """Hero on top, Pip below, slanted divider across the middle."""
    W, H, mid, sl = 1080, 1920, 880, 70
    img = Image.new("RGB", (W, H))
    img.paste(cover(hero, W, mid + sl + 10, cx=0.5, cy=0.25), (0, 0))
    top = mid - sl - 10
    low = Image.new("RGB", (W, H))
    low.paste(cover(pip, W, H - top, cx=0.5, cy=0.395), (0, top))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(0, mid + sl), (W, mid - sl), (W, H), (0, H)], fill=255)
    img.paste(low, (0, 0), m)
    d = ImageDraw.Draw(img, "RGBA")
    for col, wd in ((INK, 30), (WHITE, 16)):
        d.line([(-10, mid + sl), (W + 10, mid - sl)], fill=col, width=wd)
    img = vignette(img, 0.4)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2, 150), "I PAUSED TIME...", fit_px("I PAUSED TIME...", 150, W - 80), WHITE)
    pause_icon(d, 950, 780, 120)
    text(d, (W / 2, 1450), "...SHE PRESSED", fit_px("...SHE PRESSED", 140, W - 80), WHITE)
    x = line(d, 1610, [("PLAY", 210, YELLOW)], W)
    play_icon(d, x + 70, 1610, 150)
    return img


def landscape(hero, pip):
    W, H, sl = 1280, 720, 70
    mid = 540
    img = split(W, H, cover(hero, mid + sl + 10, H, cx=0.62, cy=0.294), cover(pip, W - mid + sl + 10, H, cx=0.1, cy=0.291),
                sl, mid)
    img = vignette(img, 0.45)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2, 90), "I PAUSED TIME...", fit_px("I PAUSED TIME...", 110, W - 60), WHITE)
    x = line(d, 625, [("SHE PRESSED", 84, WHITE), ("PLAY", 124, YELLOW)], W - 200)
    play_icon(d, x + 40, 625, 100)
    return img


def main():
    if not (os.path.exists(HERO) and os.path.exists(PIP)) or "--render" in sys.argv:
        render_stills()
    hero, pip = Image.open(HERO).convert("RGB"), Image.open(PIP).convert("RGB")
    vertical(hero, pip).save(os.path.join(OUT, "thumbnail_vertical.png"))
    landscape(hero, pip).save(os.path.join(OUT, "thumbnail.png"))
    print("wrote out/thumbnail_vertical.png, out/thumbnail.png")


if __name__ == "__main__":
    main()
