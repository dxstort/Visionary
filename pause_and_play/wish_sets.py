"""Sets and props for The Birthday Wish: party room, messy kitchen, living room, Finn's and Leo's
bedrooms, hallway door, dream sky with a unicorn and pizza clouds, cakes and candles, crayon notes."""
import math

import numpy as np

import laughs_sets as ls
import porch_sets as ps
import sets
from engine import RX, RY, RZ, T, font, glow, xf

CRAYON = (60, 90, 200)
GOLD = (255, 200, 60)


# ------------------------------------------------------------- candles, cake
def flame(sc, pos, t, k=1.0, gold=False, watts=40.0):
    """Candle flame: emissive teardrop + warm light; gold=True for the wish."""
    if k <= 0.01:
        return
    p = np.asarray(pos, float)
    w = 1 + 0.08 * math.sin(t * 23) + 0.05 * math.sin(t * 37)
    c1 = (255, 214, 90) if gold else (255, 170, 60)
    c2 = (255, 250, 200) if gold else (255, 236, 160)
    sc.blob(T(*(p + np.array([0, 0.09 * k, 0]))), (0.1 * k, 0.22 * k * w, 0.1 * k), c1, layer=7, lit=False, n=10, m=8)
    sc.blob(T(*(p + np.array([0, 0.06 * k, 0.01]))), (0.05 * k, 0.11 * k * w, 0.05 * k), c2, layer=7, lit=False,
            n=8, m=6)
    sc.light(p + np.array([0, 0.2, 0]), (255, 214, 120) if gold else (255, 170, 90), watts * k, 0.1)


def cake(sc, M, t=0.0, candle="10", lit=1.0, gold=False, s=1.0, color=(250, 170, 200)):
    """Two-tier cake on a stand. candle: '10' (number candles) or 'wish' (one tall glowing candle)."""
    sc.blob(M @ T(0, 0.05 * s, 0), (1.6 * s, 0.1 * s, 1.6 * s), (240, 240, 245), e=0.4, e2=1.0, layer=5, n=24, m=5)
    sc.blob(M @ T(0, 0.4 * s, 0), (1.3 * s, 0.6 * s, 1.3 * s), color, e=0.25, e2=1.0, layer=5, n=28, m=8)
    sc.blob(M @ T(0, 0.88 * s, 0), (0.9 * s, 0.45 * s, 0.9 * s), (255, 250, 240), e=0.25, e2=1.0, layer=5, n=28, m=8)
    for i in range(10):
        a = 2 * math.pi * i / 10
        sc.blob(M @ T(0.6 * s * math.cos(a), 0.72 * s, 0.6 * s * math.sin(a)), (0.13 * s, 0.1 * s, 0.13 * s),
                (255, 255, 255), layer=5, n=8, m=5)
        sc.blob(M @ T(0.38 * s * math.cos(a + 0.3), 1.12 * s, 0.38 * s * math.sin(a + 0.3)),
                (0.08 * s, 0.08 * s, 0.08 * s), (230, 60, 70), layer=5, n=8, m=5)
    top = 1.1 * s
    tips = []
    if candle == "10":
        def digit(D, txt):
            D.rect(-1, -1, 1, 1, (90, 170, 250))
            ps.fit_text(D, [txt], (255, 255, 255), aspect=0.5, fill_w=0.9, fill_h=0.9)
        for x, txt in ((-0.16, "1"), (0.16, "0")):
            sc.box(M @ T(x * s, top + 0.25 * s, 0), (0.24 * s, 0.5 * s, 0.1 * s), (90, 170, 250), layer=6,
                   decal=lambda D, txt=txt: digit(D, txt))
            sc.box(M @ T(x * s, top + 0.55 * s, 0), (0.02, 0.1 * s, 0.02), (40, 40, 40), layer=6)
            tips.append(xf(M, (x * s, top + 0.6 * s, 0)))
    else:
        def stripes(D):
            D.rect(-1, -1, 1, 1, (255, 250, 230))
            for k in range(-8, 9, 2):
                D.poly([(-1, k / 8), (1, k / 8 + 0.3), (1, k / 8 + 0.42), (-1, k / 8 + 0.12)], (255, 200, 80))
        sc.box(M @ T(0, top + 0.45 * s, 0), (0.18 * s, 0.9 * s, 0.18 * s), (255, 250, 230), layer=6, decal=stripes)
        sc.box(M @ T(0, top + 0.95 * s, 0), (0.02, 0.1 * s, 0.02), (40, 40, 40), layer=6)
        tips.append(xf(M, (0, top + 1.0 * s, 0)))
    for p in tips:
        flame(sc, p, t, lit, gold, watts=60 if gold else 35)
    return tips


# --------------------------------------------------------------------- props
def crayon_note(sc, M, lines, star=0.0, w=1.0, h=0.8, live=False, age=True):
    """Old paper with wobbly crayon writing (+ a gold star when star > 0). Text on the +z side."""
    paper = (250, 242, 214) if age else (252, 250, 240)

    def dec(D):
        D.rect(-1, -1, 1, 1, paper)
        if age:
            rng = np.random.RandomState(3)
            for _ in range(12):
                D.ell(rng.uniform(-0.9, 0.9), rng.uniform(-0.9, 0.9), rng.uniform(0.05, 0.2), rng.uniform(0.03, 0.1),
                      (238, 224, 186), n=10)
            D.rect(-1, 0.86, 1, 1, (236, 222, 184))
        if hasattr(D, "img"):
            from PIL import Image, ImageDraw
            W, H = D.w, D.h
            asp = w / h
            VW, VH = (int(H * asp), H) if (W == H and abs(asp - 1) > 0.05) else (W, H)
            canvas = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
            d = ImageDraw.Draw(canvas)
            n = len(lines)
            size = int(min(VH * 0.62 / (n * 1.3), min(VW * 0.86 * 100 / max(1.0, font(100).getlength(t_)) for t_ in lines)))
            cols = [(60, 90, 200), (220, 60, 70), (40, 150, 80)]
            for i, line_ in enumerate(lines):
                y = VH * (0.42 if star else 0.5) + (i - (n - 1) / 2) * size * 1.3
                x = VW / 2 - font(size).getlength(line_) / 2
                for j, ch in enumerate(line_):  # wobble each letter like a kid's handwriting
                    cw = font(size).getlength(ch)
                    if ch != " ":
                        dy = math.sin(j * 1.7 + i) * size * 0.08
                        rot = math.sin(j * 2.3 + i * 0.7) * 8
                        g = Image.new("RGBA", (int(size * 1.4), int(size * 1.6)), (0, 0, 0, 0))
                        ImageDraw.Draw(g).text((size * 0.7, size * 0.8), ch, font=font(size), anchor="mm",
                                               fill=cols[i % len(cols)] + (230,))
                        g = g.rotate(rot, resample=Image.BICUBIC)
                        canvas.alpha_composite(g, (max(0, int(x + cw / 2 - size * 0.7)), max(0, int(y + dy - size * 0.8))))
                    x += cw
            if W == H and abs(asp - 1) > 0.05:
                canvas = canvas.resize((W, H), Image.LANCZOS)
            D.img.alpha_composite(canvas)
        if star > 0:
            r = 0.22 * star
            D.poly(sets.star_poly(0.0, -0.62, r), GOLD)
        for sx in (-1, 1):  # tape
            D.poly([(sx * 0.95, 0.85), (sx * 0.65, 1.0), (sx * 0.55, 0.85), (sx * 0.85, 0.7)], (236, 236, 200))

    th = 0.004 * max(1.0, w)
    sc.box(M @ T(0, 0, th / 2), (w, h, th), paper, layer=7, decal=dec, live=live)
    sc.box(M @ T(0, 0, -th / 2), (w, h, th), paper, layer=7, live=live)


def jetpack_drawing(sc, M, w=1.0, h=0.8):
    """Finn's crayon drawing: a dog wearing a jetpack, with flames and 'WAFFLES!!'."""
    def dec(D):
        D.rect(-1, -1, 1, 1, (252, 250, 240))
        brown, ink = (180, 120, 70), (60, 60, 70)
        D.ell(-0.05, -0.05, 0.42, 0.24, brown, n=20)
        D.ell(0.42, 0.18, 0.2, 0.2, brown, n=16)
        D.ell(0.5, 0.22, 0.04, 0.05, ink, n=8)
        D.ell(0.58, 0.32, 0.08, 0.14, (140, 90, 50), n=10, rot=30)
        for x in (-0.3, -0.1, 0.12, 0.28):
            D.line([(x, -0.22), (x, -0.42)], brown, 0.05)
        D.rect(-0.38, 0.05, -0.18, 0.42, (150, 150, 165))
        D.rect(-0.16, 0.05, 0.04, 0.42, (150, 150, 165))
        for x in (-0.28, -0.06):
            D.poly([(x - 0.1, 0.05), (x + 0.1, 0.05), (x, -0.32)], (255, 140, 40))
            D.poly([(x - 0.05, 0.05), (x + 0.05, 0.05), (x, -0.16)], (255, 220, 60))
        if hasattr(D, "img"):
            ps.fit_text(D, ["WAFFLES!!"], (220, 60, 70), aspect=w / h, fill_w=0.6, fill_h=0.15, dy=-0.36)

    sc.box(M, (w, h, 0.01), (252, 250, 240), layer=7, decal=dec)


def calendar(sc, M, circled=17):
    def dec(D):
        D.rect(-1, -1, 1, 1, (255, 255, 255))
        D.rect(-1, 0.62, 1, 1, (230, 80, 70))
        if hasattr(D, "img"):
            ps.fit_text(D, ["NOVEMBER"], (255, 255, 255), aspect=1.0, fill_w=0.6, fill_h=0.14, dy=-0.4)
        for r in range(5):
            for c in range(7):
                n = r * 7 + c + 1
                if n > 30:
                    continue
                u, v = -0.86 + c * 0.287, 0.44 - r * 0.3
                D.rect(u - 0.12, v - 0.12, u + 0.12, v + 0.12, (244, 244, 248))
                D.text(u, v, str(n), (70, 70, 90), h=0.06)
                if n == circled:
                    D.arc(u, v, 0.16, 0.16, 0, 360, (230, 40, 50), 0.035, n=24)
                    D.text(u + 0.16, v + 0.18, "!!", (230, 40, 50), h=0.07)

    sc.box(M, (1.4, 1.4, 0.03), (255, 255, 255), layer=4, decal=dec)


def lasagna(sc, M, s=1.0):
    layers = [(220, 170, 90), (200, 70, 50), (250, 240, 210), (220, 170, 90), (200, 70, 50), (250, 240, 210),
              (230, 180, 90)]
    for i, c in enumerate(layers):
        sc.box(M @ T(0, (0.07 + i * 0.14) * s, 0), (1.6 * s, 0.14 * s, 1.1 * s), c, layer=5)
    sc.box(M @ T(0, (0.08 + len(layers) * 0.14) * s, 0), (1.62 * s, 0.06 * s, 1.12 * s), (240, 190, 80), layer=5)
    rng = np.random.RandomState(2)
    for _ in range(10):
        sc.blob(M @ T(rng.uniform(-0.6, 0.6) * s, (0.1 + len(layers) * 0.14) * s, rng.uniform(-0.4, 0.4) * s),
                (0.08 * s, 0.03 * s, 0.08 * s), (90, 160, 70), layer=5, n=6, m=4)


def pot(sc, M, r=0.5, h=0.5, color=(170, 176, 190)):
    sc.blob(M @ T(0, h / 2, 0), (2 * r, h, 2 * r), color, e=0.2, e2=1.0, layer=5, n=20, m=6)
    for sx in (-1, 1):
        sc.box(M @ T(sx * (r + 0.08), h * 0.8, 0), (0.16, 0.06, 0.08), (60, 60, 70), layer=5)


def steam(sc, pos, t, n=3):
    for i in range(n):
        ph = (t * 0.8 + i / n) % 1.0
        p = np.asarray(pos, float) + np.array([0.2 * math.sin(ph * 6 + i), 1.2 * ph, 0])

        def fn(d, x, y, s, col, ph=ph):
            r = (0.12 + 0.25 * ph) * s
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(150 * (1 - ph))))

        sc.sprite(p, fn, layer=8, live=True)


def couch(sc, M, color=(110, 90, 160)):
    sc.box(M @ T(0, 0.45, 0), (3.2, 0.5, 1.2), color, layer=3)
    sc.box(M @ T(0, 1.0, -0.48), (3.2, 1.1, 0.3), color, layer=3)
    for sx in (-1, 1):
        sc.box(M @ T(sx * 1.55, 0.75, 0), (0.3, 0.8, 1.2), tuple(int(v * 0.9) for v in color), layer=3)
    for sx in (-0.75, 0.75):
        sc.box(M @ T(sx, 0.78, 0.05), (1.4, 0.18, 1.0), tuple(min(255, v + 15) for v in color), layer=3)


def living_room(sc):
    sets.floor_tiles(sc, -7, 7, -3, 8, (176, 140, 110), (168, 132, 104), step=1.0)

    def paper(D):
        D.rect(-1, -1, 1, 1, (200, 226, 210))
        for k in range(-16, 17):
            D.line([(k / 16, -1), (k / 16, 1)], (190, 216, 200), 0.008)

    sets.wall(sc, 0, 3.0, -3.2, 14, 6, (200, 226, 210), decal=paper)
    couch(sc, T(0, 0, -1.8))
    sc.box(T(0, 0.02, 0.6), (4.0, 0.03, 2.4), (220, 120, 100), layer=2)
    sc.box(T(-3.2, 2.6, -2.98), (1.4, 1.0, 0.05), (120, 90, 70), layer=2)
    sc.box(T(-3.2, 2.6, -2.94), (1.2, 0.8, 0.04), (150, 200, 240), layer=2)
    sc.box(T(3.4, 0.9, -2.6), (0.5, 1.8, 0.5), (190, 150, 110), layer=3)
    sc.blob(T(3.4, 2.1, -2.6), (0.7, 0.6, 0.7), (255, 236, 180), layer=3, lit=False)


def leo_room(sc, moon=True):
    """Leo's room at night: bed against the back wall (headboard at z = -2.6), the old note above it,
    posters, a door on the right wall (x = 4)."""
    sets.floor_tiles(sc, -6, 6, -4, 8, (110, 96, 90), (104, 90, 84), step=1.0)

    def paper(D):
        D.rect(-1, -1, 1, 1, (80, 96, 130))
        for k in range(-24, 25):
            D.line([(k / 24, -1), (k / 24, 1)], (74, 90, 122), 0.006)
        D.rect(0.42, 0.05, 0.75, 0.6, (230, 90, 70))
        D.rect(0.46, 0.1, 0.71, 0.55, (250, 210, 90))
        D.rect(-0.95, 0.1, -0.68, 0.55, (90, 200, 160))

    sets.wall(sc, 0, 3.5, -3.2, 12, 7, (80, 96, 130), decal=paper)
    sets.wall(sc, 4.2, 3.5, 0.5, 8, 7, (76, 92, 124), yaw=90)
    sets.bed(sc, 0.0, -0.6, blanket=(70, 110, 170))
    sc.box(T(1.8, 0.5, -2.4), (0.8, 1.0, 0.7), (120, 90, 70), layer=3)
    if moon:
        sc.box(T(-2.6, 3.4, -3.0), (1.4, 1.4, 0.05), (14, 22, 58), layer=2, lit=False)
        sc.blob(T(-2.4, 3.6, -2.96), (0.3, 0.3, 0.02), (240, 240, 220), layer=2, lit=False, n=12, m=6)
        sc.light((-2.4, 3.2, -1.6), (150, 170, 255), 70, 1.0)
    return dict(note=np.array([0.0, 2.7, -2.96]), pillow=np.array([0.0, 1.1, -2.05]))


def hallway_door(sc, light_k=1.0):
    """Dark hallway, Leo's door closed, warm light under it."""
    sets.floor_tiles(sc, -5, 5, -3, 6, (120, 100, 86), (112, 94, 80), step=1.0)
    sets.wall(sc, 0, 3.0, -3.2, 10, 6, (70, 80, 110))
    sc.box(T(0, 1.6, -3.0), (1.5, 3.2, 0.12), (150, 110, 80), layer=3)
    sc.box(T(0, 1.6, -2.93), (1.7, 3.4, 0.04), (220, 220, 230), layer=2)
    sc.blob(T(0.55, 1.5, -2.9), (0.12, 0.12, 0.1), (230, 200, 90), layer=4, n=8, m=5)
    sc.box(T(0, 0.03, -2.86), (1.4, 0.04, 0.02), (255, 214, 140), layer=4, lit=False)
    sc.light((0, 0.1, -2.6), (255, 200, 130), 25 * light_k, 0.3)
    sc.box(T(-2.6, 2.2, -3.05), (0.9, 0.7, 0.04), (180, 160, 120), layer=2)


def unicorn(sc, M, t=0.0):
    white, gold = (250, 250, 255), (255, 210, 80)
    rain = [(255, 110, 130), (255, 190, 90), (255, 240, 110), (130, 220, 140), (120, 180, 255), (190, 130, 255)]
    gal = math.sin(t * 8)
    sc.box(M @ T(0, 1.2, 0), (0.8, 0.7, 1.7), white, layer=5)
    for sx in (-1, 1):
        for sz in (-1, 1):
            sc.box(M @ T(sx * 0.26, 0.5, sz * 0.62) @ RX(25 * gal * sx * sz), (0.2, 0.9, 0.2), white, layer=5)
    N = M @ T(0, 1.55, 0.75) @ RX(-35)
    sc.box(N @ T(0, 0.3, 0), (0.42, 0.7, 0.42), white, layer=5)

    def face(D):
        for sx in (-1, 1):
            D.arc(sx * 0.45, 0.1, 0.18, 0.15, 20, 160, (40, 28, 48), 0.07)
            D.ell(sx * 0.6, -0.3, 0.12, 0.08, (255, 160, 190), n=10)
    H = M @ T(0, 2.25, 0.95)
    sc.box(H, (0.46, 0.5, 0.7), white, layer=5, decal=face)
    v = [(0, 0.55, 0)] + [(0.09 * math.cos(a), 0, 0.09 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1]]
    sc.solid(H @ T(0, 0.24, 0.12) @ RX(20), v, [(0, (i + 1) % 6 + 1, i + 1) for i in range(6)], gold, layer=5)
    for i, c in enumerate(rain):  # mane and tail
        sc.box(M @ T(0, 2.05 - i * 0.14, 0.62 - i * 0.12), (0.12, 0.24, 0.16), c, layer=5)
        sc.box(M @ T(0, 1.3 - i * 0.1, -0.95 - i * 0.08) @ RX(-30), (0.14, 0.22, 0.14), c, layer=5)


def rainbow(sc, center, r=8.0, t=0.0):
    cols = [(255, 110, 130), (255, 190, 90), (255, 240, 110), (130, 220, 140), (120, 180, 255), (190, 130, 255)]
    cx, cy, cz = center
    for i, c in enumerate(cols):
        rr = r - i * 0.5
        for k in range(24):
            a0 = math.pi * k / 24
            a1 = math.pi * (k + 1) / 24
            p = [(cx + rr * math.cos(a0), cy + rr * math.sin(a0), cz), (cx + rr * math.cos(a1), cy + rr * math.sin(a1), cz),
                 (cx + (rr - 0.5) * math.cos(a1), cy + (rr - 0.5) * math.sin(a1), cz),
                 (cx + (rr - 0.5) * math.cos(a0), cy + (rr - 0.5) * math.sin(a0), cz)]
            sc.solid(np.eye(4), p, [(0, 1, 2, 3), (3, 2, 1, 0)], c, layer=1, lit=False)


def pastel_clouds(sc, seed=1, n=10, pizza=False, t=0.0):
    rng = np.random.RandomState(seed)
    cols = [(255, 220, 240), (230, 220, 255), (255, 240, 220), (220, 240, 255)]
    for i in range(n):
        x, y, z = rng.uniform(-14, 14), rng.uniform(-3, 9), rng.uniform(-18, -3)
        k = rng.uniform(0.8, 1.6)
        c = cols[i % 4]
        for dx, dy, kk in ((0, 0, 1.0), (-1.0, -0.3, 0.7), (1.1, -0.2, 0.75), (0.2, 0.5, 0.6)):
            sc.blob(T(x + dx * k, y + dy * k + 0.2 * math.sin(t + i), z), (2.2 * k * kk, 1.3 * k * kk, 1.6 * k * kk), c,
                    layer=2, n=12, m=8)
        if pizza:
            for j in range(3):
                a = j * 2.1 + i
                P = T(x + 0.9 * k * math.cos(a), y + 0.9 * k + 0.2 * math.sin(t * 2 + j), z + 0.8) @ RZ(math.degrees(a))
                tri = [(0, 0.7, 0), (-0.45, -0.4, 0), (0.45, -0.4, 0)]
                sc.solid(P, tri, [(0, 1, 2), (2, 1, 0)], (250, 200, 90), layer=3)
                sc.box(P @ T(0, -0.45, 0), (0.95, 0.14, 0.12), (200, 140, 70), layer=3)
                for px, py in ((-0.12, -0.15), (0.12, 0.05), (0.0, 0.3)):
                    sc.blob(P @ T(px, py, 0.03), (0.13, 0.13, 0.03), (210, 60, 50), layer=3, n=8, m=4)


def jetpack(sc, M, t=0.0, flames=True):
    for sx in (-1, 1):
        sc.blob(M @ T(sx * 0.2, 0, 0), (0.28, 0.8, 0.28), (170, 176, 190), e=0.3, e2=1.0, layer=6, n=14, m=6)
        sc.blob(M @ T(sx * 0.2, 0.42, 0), (0.24, 0.16, 0.24), (220, 70, 60), layer=6, n=10, m=6)
        if flames:
            L = 0.5 + 0.15 * math.sin(t * 30 + sx)
            sc.blob(M @ T(sx * 0.2, -0.45 - L / 2, 0), (0.2, L, 0.2), (255, 170, 60), layer=6, lit=False, n=10, m=6)
            sc.blob(M @ T(sx * 0.2, -0.45 - L / 3, 0), (0.1, L * 0.6, 0.1), (255, 245, 180), layer=6, lit=False,
                    n=8, m=5)


def squirrel_sticker(sc, anchor, t, start=0.0, hold=2.4, size=1.0):
    tt = t - start
    if tt < 0 or tt > hold:
        return
    x, y, z = sc.project(np.asarray(anchor, float))
    s = sc.fl / max(z, 0.2) * size * min(1.0, tt / 0.15)

    def fn(d, W, H):
        o = (40, 28, 48, 255)
        b = (190, 120, 60, 255)
        tx, ty = x + 0.25 * s, y - 0.1 * s
        d.ellipse([tx - 0.22 * s, ty - 0.45 * s, tx + 0.18 * s, ty + 0.25 * s], fill=(210, 140, 70, 255), outline=o,
                  width=int(s * 0.03))
        d.ellipse([x - 0.2 * s, y - 0.12 * s, x + 0.15 * s, y + 0.25 * s], fill=b, outline=o, width=int(s * 0.03))
        d.ellipse([x - 0.3 * s, y - 0.32 * s, x - 0.02 * s, y - 0.04 * s], fill=b, outline=o, width=int(s * 0.03))
        d.ellipse([x - 0.22 * s, y - 0.24 * s, x - 0.16 * s, y - 0.17 * s], fill=o)
        d.polygon([(x - 0.22 * s, y - 0.3 * s), (x - 0.18 * s, y - 0.42 * s), (x - 0.12 * s, y - 0.3 * s)], fill=b)
        d.ellipse([x - 0.08 * s, y - 0.08 * s, x + 0.05 * s, y + 0.06 * s], fill=(150, 100, 50, 255))
        f = font(max(8, int(0.16 * s)))
        d.text((x, y + 0.42 * s), "SQUIRRELS!", font=f, fill=(255, 230, 80, 255), anchor="mm",
               stroke_width=max(2, int(s * 0.02)), stroke_fill=o)

    sc.overlay(fn)


def speech_lines(sc, anchor, t, side=1):
    def fn(d, x, y, s, col):
        for i in range(3):
            a = math.radians(-30 + i * 30)
            k = 0.6 + 0.15 * math.sin(t * 30 + i)
            d.line([(x + side * 0.3 * s * math.cos(a), y + 0.3 * s * math.sin(a)),
                    (x + side * (0.3 + 0.3 * k) * s * math.cos(a), y + (0.3 + 0.3 * k) * s * math.sin(a))],
                   fill=(40, 28, 48, 255), width=max(2, int(s * 0.04)))

    sc.sprite(np.asarray(anchor, float), fn, layer=8, live=True)


def shadow_overlay(sc, k=1.0, t=0.0):
    """Nightmare: dark vignette plus drifting shadow blobs on the walls."""
    def fn(d, W, H):
        rng = np.random.RandomState(5)
        for i in range(7):
            cx = (rng.uniform(0, 1) + 0.03 * math.sin(t * 1.3 + i)) * W
            cy = rng.uniform(0, 0.55) * H
            r = rng.uniform(0.15, 0.3) * W
            d.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7], fill=(10, 6, 20, int(70 * k)))
        for i in range(10, 0, -1):
            m = i / 10
            d.rectangle([0, 0, W, H], outline=(5, 4, 12, int(25 * k)), width=int(W * 0.03 * m))

    sc.overlay(fn)


def dark_cloud(sc, pos, t, k=1.0):
    p = np.asarray(pos, float)
    for dx, dy, r in ((0, 0, 0.6), (-0.5, -0.1, 0.45), (0.5, -0.05, 0.5), (0.2, 0.25, 0.4)):
        def fn(d, x, y, s, col, r=r):
            rr = r * s
            d.ellipse([x - rr, y - rr * 0.8, x + rr, y + rr * 0.8], fill=(40, 34, 60, int(220 * k)))
        sc.sprite(p + np.array([dx, dy + 0.05 * math.sin(t * 3), 0]), fn, layer=8, live=True)
    for i in range(3):
        if int(t * 6 + i) % 3 == 0:
            def bolt(d, x, y, s, col, i=i):
                pts = [(x + (i - 1) * 0.35 * s, y + 0.3 * s), (x + (i - 1) * 0.35 * s - 0.1 * s, y + 0.55 * s),
                       (x + (i - 1) * 0.35 * s + 0.05 * s, y + 0.55 * s), (x + (i - 1) * 0.35 * s - 0.05 * s, y + 0.8 * s)]
                d.line(pts, fill=(250, 230, 120, int(255 * k)), width=max(2, int(s * 0.04)))
            sc.sprite(p, bolt, layer=8, live=True)


def photo_border(sc, tilt=-3):
    """Old-photo frame round the whole picture (white border, slight dark edge)."""
    def fn(d, W, H):
        b = int(W * 0.06)
        d.rectangle([0, 0, W, b], fill=(246, 240, 226, 255))
        d.rectangle([0, H - b * 3, W, H], fill=(246, 240, 226, 255))
        d.rectangle([0, 0, b, H], fill=(246, 240, 226, 255))
        d.rectangle([W - b, 0, W, H], fill=(246, 240, 226, 255))
        d.rectangle([b, b, W - b, H - b * 3], outline=(150, 130, 100, 255), width=max(2, b // 10))

    sc.overlay(fn)


def gold_flash(sc, k):
    if k <= 0:
        return

    def fn(d, W, H):
        d.rectangle([0, 0, W, H], fill=(255, 210, 90, int(200 * k)))

    sc.overlay(fn)


def party_room(sc, t=0.0):
    ls.dining(sc, ceiling=True, lamp=False)

    def banner(D):
        D.rect(-1, -1, 1, 1, (255, 250, 230))
        if hasattr(D, "img"):
            ps.fit_text(D, ["HAPPY BIRTHDAY!"], (230, 80, 120), aspect=5.0, fill_w=0.9, fill_h=0.7)

    sc.box(T(0, 3.7, -3.05), (5.0, 1.0, 0.04), (255, 250, 230), layer=2, decal=banner)
    for x, c in ((-4.0, (255, 90, 120)), (-3.4, (90, 190, 255)), (3.6, (255, 214, 70)), (4.2, (150, 230, 120))):
        ls.balloon(sc, x, 3.2, -2.6, c, t, string=2.0)
