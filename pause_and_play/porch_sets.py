"""Night street for the porch-light story: houses whose porch lamps and windows glow with happiness.

Layout (shot space, y up): the street runs along x. North row of houses at z = -8 (fronts face +z),
pavement z -2.3..2.6, road z 2.95..8.5, south pavement 8.5..11, south row at z = 15.5 (fronts face -z).
Mr Abernathy's house closes the street at x = ABER_X, its front facing back down the street (-x).
"""
import math

import numpy as np

import sets
from engine import RX, RY, RZ, T, glow, xf

NIGHT_SKY = ((10, 16, 46), (44, 58, 112))
DUSK_SKY = ((36, 40, 104), (232, 150, 140))
WARM = (255, 206, 120)
DARK_GLASS = (30, 38, 64)
NORTH_X = (-26.0, -19.5, -13.0, -6.5, 0.0, 6.5, 13.0, 19.5)
SOUTH_X = (-22.75, -16.25, -9.75, -3.25, 3.25, 9.75, 16.25)
ABER_X, ABER_Z = 30.5, 5.7
SOUTH_Z = 15.5
HOUSE_W, HOUSE_H, HOUSE_D = 5.0, 3.6, 4.2


def warm(k, base=WARM, off=DARK_GLASS):
    k = max(0.0, min(1.0, k))
    return tuple(int(off[i] + (base[i] - off[i]) * k) for i in range(3))


def night_sky(sc, moon_dir=(-0.35, 0.42, -1.0)):
    """Moon as a real far-away emissive disc, so houses and roofs hide it (stars come from the sky shader)."""
    md = np.asarray(moon_dir, float)
    md /= np.linalg.norm(md)
    c = md * 300
    sc.blob(T(*c), (17, 17, 17), (250, 248, 228), layer=0, lit=False, n=24, m=12)
    sc.sprite(c, lambda d, x, y, s_, col: glow(d, x, y, 30 * s_, (210, 220, 255), 60), layer=0)


def lamp_glow(sc, pos, k, r=0.55, color=WARM, painted=False):
    """Painted 2D glow (drawn over everything). Off by default: night scenes use the backend's bloom."""
    if k <= 0.02 or not painted:
        return
    sc.sprite(pos, lambda d, x, y, s, col: glow(d, x, y, r * (0.6 + 0.6 * k) * s, color, int(110 * k)), layer=7,
              live=True)


def porch_lamp(sc, M, k, glow_r=0.55, watts=None, shadow=False, cobweb=False):
    """Wall lantern at M (its back on the wall, facing +z). k = 0 dark .. 1 bright."""
    metal = (44, 44, 54)
    sc.box(M @ T(0, 0, 0.06), (0.12, 0.34, 0.12), metal, layer=3)
    sc.box(M @ T(0, 0.1, 0.2), (0.34, 0.06, 0.34), metal, layer=3, bias=-0.1)
    sc.box(M @ T(0, -0.16, 0.2), (0.3, 0.05, 0.3), metal, layer=3, bias=-0.1)
    sc.box(M @ T(0, -0.03, 0.2), (0.24, 0.22, 0.24), warm(k, (255, 236, 170), (70, 74, 88)), layer=3, lit=False)
    p = xf(M, (0, -0.03, 0.42))
    if k > 0.02:
        sc.light(p, (255, 200, 130), watts if watts is not None else 70 * k, 0.08, shadow)
        lamp_glow(sc, xf(M, (0, -0.03, 0.2)), k, glow_r)
    if cobweb:
        def web(d, x, y, s, col):
            c = (220, 220, 230, 150)
            r = 0.32 * s
            for a in range(0, 100, 20):
                aa = math.radians(a)
                d.line([(x, y), (x + r * math.cos(aa), y - r * math.sin(aa))], fill=c, width=max(1, int(s * 0.01)))
            for rr in (0.35, 0.65, 0.95):
                d.arc([x - r * rr, y - r * rr, x + r * rr, y + r * rr], 270, 360, fill=c, width=max(1, int(s * 0.01)))

        sc.sprite(xf(M, (0.17, 0.14, 0.3)), web, layer=7)
    return p


def window(sc, M, k, w=0.85, h=1.0, color=None, curtains=(150, 70, 70), open_k=0.0):
    """Window at M (centre of the pane, facing +z). Glows warm with k. open_k swings the right sash out."""
    trim = (250, 248, 240)
    sc.box(M @ T(0, 0, -0.04), (w + 0.16, h + 0.16, 0.08), trim, layer=2)
    glass = color or warm(k)
    if open_k <= 0.01:
        sc.box(M @ T(0, 0, 0.01), (w, h, 0.03), glass, layer=2, lit=False)
        sc.box(M @ T(0, 0, 0.04), (0.05, h, 0.03), trim, layer=2, bias=-0.05)
    else:
        sc.box(M @ T(0, 0, -0.02), (w, h, 0.02), glass, layer=2, lit=False)
        sc.box(M @ T(-w / 4, 0, 0.01), (w / 2, h, 0.03), glass, layer=2, lit=False, bias=-0.02)
        S = M @ T(w / 2, 0, 0.02) @ RY(-110 * open_k) @ T(-w / 4, 0, 0)
        sc.box(S, (w / 2, h, 0.04), (180, 200, 230), layer=3)
        sc.box(S @ T(0, 0, 0.025), (w / 2 + 0.06, h + 0.06, 0.02), trim, layer=3)
    sc.box(M @ T(0, h / 2 - 0.05, 0.05), (w + 0.1, 0.06, 0.04), trim, layer=2, bias=-0.06)
    for sx in (-1, 1):
        sc.box(M @ T(sx * (w / 2 - 0.1), 0.08, 0.035), (0.16, h * 0.84, 0.02), curtains, layer=2, bias=-0.04)
    sc.box(M @ T(0, -h / 2 - 0.08, 0.1), (w + 0.3, 0.08, 0.26), trim, layer=2, bias=-0.06)  # sill
    if k > 0.05:
        sc.light(xf(M, (0, 0, 0.6)), (255, 196, 120), 40 * k, 0.4)
    return xf(M, (0, -h / 2 - 0.02, 0.12))  # top of the sill


def porch_house(sc, x, z, color, k=1.0, yaw=0, roof=None, old=False, lamp_k=None, party=0.0, win_open=0.0,
                win_k=None, glow_r=0.55, lamp_watts=None, shadow=False):
    """House with a covered porch, porch lamp and two front windows. Returns anchors (lamp, sills, door)."""
    w, h, d = HOUSE_W, HOUSE_H, HOUSE_D
    roof = roof or tuple(int(v * 0.5 + 20) for v in color)
    lamp_k = k if lamp_k is None else lamp_k
    win_k = k if win_k is None else win_k
    trim = (250, 248, 240) if not old else (150, 146, 150)

    def siding(D):
        for i in range(1, 12):
            v = -1 + i * 2 / 12
            D.line([(-1, v), (1, v)], tuple(c * 0.9 for c in color), 0.012)
        D.rect(-0.2, -1, 0.2, -0.16, trim)
        D.rect(-0.16, -1, 0.16, -0.2, (110, 70, 50) if not old else (80, 64, 56))
        D.ell(0.11, -0.62, 0.025, 0.025 * w / h, (230, 190, 90), n=8)
        D.rect(-1, -1, 1, -0.9, tuple(c * 0.7 for c in color))
        if old:
            rng = np.random.RandomState(int(abs(x) * 7))
            for _ in range(14):
                u, v = rng.uniform(-1, 1), rng.uniform(-0.8, 0.9)
                D.rect(u, v, u + rng.uniform(0.08, 0.2), v + 0.05, tuple(c * 0.8 for c in color))

    M = T(x, 0, z) @ RY(yaw)
    sc.box(M @ T(0, h / 2, 0), (w, h, d), color, layer=2, decal=siding)
    ov, rh = 0.45, 1.9
    verts = [(-w / 2 - ov, h, d / 2 + ov), (w / 2 + ov, h, d / 2 + ov), (w / 2 + ov, h, -d / 2 - ov),
             (-w / 2 - ov, h, -d / 2 - ov), (-w / 2 - ov, h + rh, 0), (w / 2 + ov, h + rh, 0)]
    sc.solid(M, verts, [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)], roof, layer=2, bias=-1.0)
    sc.box(M @ T(w * 0.28, h + 1.5, -d * 0.2), (0.6, 1.6, 0.6), (150, 80, 70) if not old else (90, 80, 80), layer=2)
    # porch: deck, steps, two posts and a little roof over the door
    deck = (200, 176, 150) if not old else (130, 118, 108)
    sc.box(M @ T(0, 0.15, d / 2 + 0.6), (2.6, 0.3, 1.2), deck, layer=2)
    sc.box(M @ T(0, 0.07, d / 2 + 1.35), (1.4, 0.14, 0.4), deck, layer=2, bias=-0.1)
    for sx in (-1, 1):
        sc.box(M @ T(sx * 1.15, 1.2, d / 2 + 1.1), (0.14, 1.8, 0.14), trim, layer=2)
    sc.box(M @ T(0, 2.16, d / 2 + 0.62), (2.8, 0.12, 1.4), roof, layer=2, bias=-0.2)
    lamp = porch_lamp(sc, M @ T(0.82, 1.85, d / 2), lamp_k, glow_r, lamp_watts, shadow, cobweb=old)
    sills = []
    for sx in (-1, 1):
        sills.append(window(sc, M @ T(sx * 1.6, 2.15, d / 2 + 0.02), win_k, open_k=win_open if sx > 0 else 0.0,
                            curtains=(150, 70, 70) if not old else (90, 84, 90)))
    if party > 0:
        rng = np.random.RandomState(int(abs(x) * 3 + 1))
        cols = [(255, 90, 120), (90, 200, 255), (255, 220, 80), (150, 230, 120), (210, 120, 255)]
        for i in range(9):
            u = -1.3 + i * 0.32
            sc.box(M @ T(u, 2.06 - 0.12 * math.sin(i * 1.3), d / 2 + 1.33) @ RZ(45), (0.16, 0.16, 0.04),
                   cols[i % 5], layer=3, lit=False)
        for sx in (-1.25, 1.25):
            sc.light(xf(M, (sx, 1.6, d / 2 + 1.6)), cols[int(rng.randint(5))], 50 * party, 0.3)
    return dict(lamp=lamp, sill_l=sills[0], sill_r=sills[1], door=xf(M, (0, 0.8, d / 2 + 1.2)), M=M,
                win_r=xf(M, (1.6, 2.15, d / 2 + 0.06)), win_l=xf(M, (-1.6, 2.15, d / 2 + 0.06)))


def sunflower(sc, x, z, h=1.5, k=1.0, face=0.0):
    """Sunflower growing to k (0..1) of its height."""
    if k <= 0.02:
        return
    hh = h * k
    sc.box(T(x, hh / 2, z), (0.07, hh, 0.07), (70, 150, 70), layer=4)
    for sy, sx in ((0.35, 1), (0.6, -1)):
        sc.blob(T(x + sx * 0.14, hh * sy, z) @ RZ(sx * -35), (0.26, 0.08, 0.14), (80, 170, 80), layer=4, n=10, m=5)
    H = T(x, hh, z + 0.02) @ RY(face) @ RX(-10)
    sc.blob(H, (0.22 * k + 0.1, 0.22 * k + 0.1, 0.08), (120, 76, 40), e=0.8, layer=4, n=14, m=5)
    for i in range(12):
        a = i * 30
        sc.blob(H @ RZ(a) @ T(0, 0.2 * k + 0.08, -0.01), (0.1, 0.22 * k + 0.05, 0.04), (255, 206, 50), layer=4,
                bias=0.01, n=10, m=4)


def street(sc, lights=None, aber_k=0.0, aber_win=0.0, north=True, south=True, lamps=True, party=None,
           flowers=0.0, aber_lamp_watts=None, watts=None, aber_win_k=None):
    """Whole street. lights: {('n', i) or ('s', i): k}; houses not listed glow at 0.9."""
    lights = lights or {}
    sc.ground((60, 120, 70))
    sets.flat(sc, -80, ABER_X - 3.0, -2.3, 2.6, (180, 176, 170))
    sets.flat(sc, -80, ABER_X - 3.0, 2.6, 2.95, (150, 148, 144), y=0.014)
    sets.flat(sc, -80, ABER_X - 3.0, 2.95, 8.5, (64, 68, 82))
    sets.flat(sc, -80, ABER_X - 3.0, 8.5, 8.85, (150, 148, 144), y=0.014)
    sets.flat(sc, -80, ABER_X - 3.0, 8.85, 11.2, (180, 176, 170))
    for i in range(-10, 7):
        sets.flat(sc, i * 4 - 1, i * 4 + 1, 5.6, 5.8, (230, 220, 180), y=0.012)
    treeline(sc)
    out = {}
    colors = sets.HOUSE_COLORS
    if north:
        for i, x in enumerate(NORTH_X):
            k = lights.get(("n", i), 0.9)
            out[("n", i)] = porch_house(sc, x, -8.0, colors[i % 6], k=k, party=(party or {}).get(("n", i), 0.0),
                                        lamp_watts=(watts or {}).get(("n", i)))
            sets.flat(sc, x - 0.6, x + 0.6, -4.5, -2.3, (190, 184, 176), y=0.012)
            sets.bush(sc, x - 2.4, -5.0, 0.7)
            sets.bush(sc, x + 2.3, -5.1, 0.6, c=(84, 172, 96))
    if south:
        for i, x in enumerate(SOUTH_X):
            k = lights.get(("s", i), 0.9)
            out[("s", i)] = porch_house(sc, x, SOUTH_Z, colors[(i + 3) % 6], k=k, yaw=180,
                                        party=(party or {}).get(("s", i), 0.0), lamp_watts=(watts or {}).get(("s", i)))
            sets.flat(sc, x - 0.6, x + 0.6, 11.2, 12.5, (190, 184, 176), y=0.012)
            sets.bush(sc, x - 2.4, 12.6, 0.7)
    if lamps:
        for x in (-23, -10, 3, 16):
            street_lamp(sc, x, 2.3)
    # Mr Abernathy's house closes the street
    grey = (126, 122, 132)
    out["aber"] = porch_house(sc, ABER_X, ABER_Z, grey, k=aber_k, yaw=-90, roof=(70, 64, 74), old=True,
                              win_k=aber_k if aber_win_k is None else aber_win_k, win_open=aber_win,
                              lamp_watts=aber_lamp_watts)
    sets.flat(sc, ABER_X - 3.0, ABER_X + 4, -2.3, 11.2, (70, 110, 66), y=0.011)
    for i in range(12):
        z = ABER_Z - 4.4 + i * 0.8
        if abs(z - ABER_Z) < 0.9:
            continue
        sc.box(T(ABER_X - 4.3, 0.42, z), (0.08, 0.84, 0.2), (120, 112, 104), layer=2)
    if flowers > 0:
        for j, z in enumerate((ABER_Z - 3.4, ABER_Z - 2.6, ABER_Z - 1.8, ABER_Z + 1.8, ABER_Z + 2.6, ABER_Z + 3.4)):
            sunflower(sc, ABER_X - 3.6, z, 1.4 + 0.15 * (j % 2), flowers, face=-90)
    return out


def treeline(sc, seed=9):
    """Dark round trees behind both rows and beyond the dead end, so high angles don't end in bare ground."""
    rng = np.random.RandomState(seed)
    spots = [(x, rng.uniform(-17, -14)) for x in np.arange(-40, 40, 3.1)]
    spots += [(x, rng.uniform(22, 25)) for x in np.arange(-40, 40, 3.1)]
    spots += [(ABER_X + rng.uniform(6, 9), z) for z in np.arange(-14, 25, 3.0)]
    for x, z in spots:
        h = rng.uniform(4.5, 7.5)
        c = (40 + rng.randint(15), 84 + rng.randint(25), 56 + rng.randint(15))
        sc.box(T(x, h * 0.25, z), (0.5, h * 0.5, 0.5), (90, 64, 48), layer=1)
        sc.blob(T(x, h * 0.68, z), (3.2, h * 0.62, 3.2), c, layer=1, n=10, m=7)


def street_lamp(sc, x, z, k=0.8):
    sc.box(T(x, 2.0, z), (0.14, 4.0, 0.14), (54, 58, 72), layer=2)
    sc.box(T(x, 4.05, z), (0.5, 0.12, 0.5), (54, 58, 72), layer=2, bias=-0.1)
    sc.blob(T(x, 4.35, z), (0.44, 0.5, 0.44), (255, 236, 180), layer=2, bias=-0.2, lit=False, n=8, m=5)
    sc.light((x, 4.2, z), (255, 220, 160), 120 * k, 0.2)
    lamp_glow(sc, (x, 4.35, z), k * 0.7, 0.8, (255, 230, 170))


def paper_plane(sc, M, s=1.0, color=(244, 242, 228), live=False):
    """Folded paper airplane, nose toward +z of M. Faintly self-lit so it reads at night."""
    v = [(0, 0.02, 0.5), (-0.36, 0.0, -0.4), (0, -0.08, -0.4), (0.36, 0.0, -0.4)]
    v = [(a * s, b * s, c * s) for a, b, c in v]
    sc.solid(M, v, [(0, 1, 2), (0, 2, 3), (1, 0, 2), (2, 0, 3)], color, layer=7, live=live, lit=False)
    sc.solid(M, [(0, 0.02 * s, 0.5 * s), (0, -0.08 * s, -0.4 * s), (0, -0.2 * s, -0.36 * s)],
             [(0, 1, 2), (2, 1, 0)], tuple(v_ * 0.82 for v_ in color), layer=7, live=live, lit=False)


def fit_text(D, lines, ink, aspect=1.0, fill_w=0.86, fill_h=0.8, gap=1.25, dy=0.0):
    """Centred lines sized to fill the surface. aspect = the face's real width / height (small decals are
    drawn into a square texture, so the text is drawn at the true aspect and squeezed to fit)."""
    from PIL import Image, ImageDraw

    from engine import font
    if not hasattr(D, "img"):
        for i, line in enumerate(lines):
            D.text(0, 0.4 - i * 0.35, line, ink, h=0.12)
        return
    W, H = D.w, D.h
    sq = W == H and abs(aspect - 1) > 0.05
    VW, VH = (int(H * aspect), H) if sq else (W, H)
    n = len(lines)
    size = int(min(VH * fill_h / (n * gap), min(VW * fill_w * 100 / max(1.0, font(100).getlength(t)) for t in lines)))
    canvas = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    for i, line in enumerate(lines):
        d.text((VW / 2, VH / 2 + (i - (n - 1) / 2) * size * gap + dy * VH), line, font=font(size),
               fill=tuple(ink) + (255,), anchor="mm")
    if sq:
        canvas = canvas.resize((W, H), Image.LANCZOS)
    D.img.alpha_composite(canvas)


def note(sc, M, lines, w=0.7, h=0.7, ink=(40, 40, 90), folds=True, heart=False, live=False):
    """Unfolded note: text on the +z side of M, plain paper on the back. Keep it square for small notes
    (their texture is square); notes bigger than 3 units get a sharp texture at any aspect."""
    paper = (252, 250, 240)

    def decal(D):
        D.rect(-1, -1, 1, 1, paper)
        if folds:
            for u in (-0.33, 0.33):
                D.line([(u, -1), (u, 1)], (222, 218, 204), 0.008)
            D.line([(-1, 0), (1, 0)], (222, 218, 204), 0.008)
        if lines:
            fit_text(D, lines, ink, aspect=w / h, fill_h=0.62 if heart else 0.72, dy=-0.08 if heart else 0.0)
        if heart:
            hp = [(0.0, -0.78), (-0.16, -0.6), (-0.17, -0.5), (-0.1, -0.44), (0.0, -0.5), (0.1, -0.44), (0.17, -0.5),
                  (0.16, -0.6)]
            D.poly(hp, (230, 70, 90))

    th = 0.004 * max(1.0, w)
    sc.box(M @ T(0, 0, th / 2), (w, h, th), paper, layer=7, decal=decal, live=live)
    sc.box(M @ T(0, 0, -th / 2), (w * 1.002, h * 1.002, th), paper, layer=7, live=live)


def trumpet(sc, M):
    gold = (240, 196, 70)
    sc.box(M @ T(0, 0, 0.3), (0.07, 0.07, 0.7), gold, layer=7)
    sc.blob(M @ T(0, 0, 0.72) @ RX(90), (0.3, 0.2, 0.3), gold, e=0.6, e2=1.0, layer=7, n=16, m=6)
    sc.box(M @ T(0, 0.08, 0.1), (0.12, 0.12, 0.3), gold, layer=7)
    for k in range(3):
        sc.box(M @ T(0, 0.17, 0.02 + k * 0.08), (0.03, 0.08, 0.03), (220, 220, 230), layer=7)


def music_notes(sc, origin, t, n=4, color=(255, 236, 120)):
    for i in range(n):
        ph = (t * 0.9 + i / n) % 1.0
        p = np.asarray(origin, float) + np.array([0.35 * math.sin(ph * 6 + i), 1.4 * ph, 0.3 * ph])

        def fn(d, x, y, s, col, ph=ph, i=i):
            a = int(255 * min(1.0, (1 - ph) * 2.5))
            r = 0.09 * s
            c = color + (a,)
            d.ellipse([x - r * 1.3, y - r, x + r * 1.3, y + r], fill=c)
            d.line([(x + r * 1.2, y), (x + r * 1.2, y - r * 4)], fill=c, width=max(2, int(r * 0.5)))
            if i % 2:
                d.line([(x + r * 1.2, y - r * 4), (x + r * 3, y - r * 3.2)], fill=c, width=max(2, int(r * 0.5)))

        sc.sprite(p, fn, layer=8, live=True)


def firework(sc, pos, t, color, r=1.6, seed=0):
    """Burst of sparks around pos, t in seconds since launch (0..1.2)."""
    if t < 0 or t > 1.3:
        return
    rng = np.random.RandomState(seed)
    k = min(1.0, t / 0.35)
    fade = max(0.0, 1 - max(0.0, t - 0.5) / 0.8)
    for i in range(22):
        a, b = rng.uniform(0, 2 * math.pi), rng.uniform(-0.6, 0.6)
        d = np.array([math.cos(a) * math.cos(b), math.sin(b) + 0.2, math.sin(a) * math.cos(b)])
        p = np.asarray(pos, float) + d * r * (1 - (1 - k) ** 2) - np.array([0, 0.5 * t * t, 0])

        def fn(dr, x, y, s, col, fade=fade):
            rr = 0.07 * s
            dr.ellipse([x - rr, y - rr, x + rr, y + rr], fill=tuple(color) + (int(255 * fade),))

        sc.sprite(p, fn, layer=8, live=True)
    sc.sprite(pos, lambda dr, x, y, s, col: glow(dr, x, y, r * s, color, int(70 * fade)), layer=8, live=True)


# ----------------------------------------------------------- close-up sets
def facade(sc, color, open_k=0.0, room_k=0.3, old=False, lamp_k=None, win_y=2.6, win_w=1.3, win_h=1.4,
           lamp_x=1.45, glass=None, shelf=False, curtains=None, lamp_watts=None):
    """Wall in the z = 0 plane (outside faces +z) with a real window opening and a dim room behind it,
    so a character standing at z ~ -0.7 is seen through the window. Returns anchors."""
    wall_w, wall_h, th = 9.0, 6.0, 0.24
    trim = (250, 248, 240) if not old else (176, 170, 176)

    def siding(D):
        for i in range(1, 26):
            v = -1 + i * 2 / 26
            D.line([(-1, v), (1, v)], tuple(c * 0.88 for c in color), 0.006)
        if old:
            rng = np.random.RandomState(5)
            for _ in range(30):
                u, v = rng.uniform(-1, 1), rng.uniform(-1, 1)
                D.rect(u, v, u + rng.uniform(0.04, 0.12), v + 0.03, tuple(c * 0.78 for c in color))

    x0, x1 = -win_w / 2, win_w / 2
    y0, y1 = win_y - win_h / 2, win_y + win_h / 2
    zc = -th / 2
    sc.box(T((-wall_w / 2 + x0) / 2, wall_h / 2, zc), (x0 + wall_w / 2, wall_h, th), color, layer=2, decal=siding)
    sc.box(T((wall_w / 2 + x1) / 2, wall_h / 2, zc), (wall_w / 2 - x1, wall_h, th), color, layer=2, decal=siding)
    sc.box(T(0, y0 / 2, zc), (win_w, y0, th), color, layer=2)
    sc.box(T(0, (wall_h + y1) / 2, zc), (win_w, wall_h - y1, th), color, layer=2)
    for sx in (-1, 1):  # frame
        sc.box(T(sx * (win_w / 2 + 0.06), win_y, 0.03), (0.14, win_h + 0.26, 0.1), trim, layer=3)
    sc.box(T(0, y1 + 0.07, 0.03), (win_w + 0.26, 0.14, 0.1), trim, layer=3)
    sc.box(T(0, y0 - 0.06, 0.14), (win_w + 0.5, 0.1, 0.34), trim, layer=3)        # outside sill
    sc.box(T(0, y0 - 0.06, -th - 0.1), (win_w + 0.3, 0.08, 0.26), trim, layer=3)  # inside sill
    if glass is not None and open_k <= 0.01:
        sc.box(T(0, win_y, zc), (win_w, win_h, 0.04), glass, layer=3, lit=False)
    else:
        for sx in (-1, 1):  # casement sashes, hinged at the sides, swing outward
            S = T(sx * win_w / 2, win_y, 0.0) @ RY(-sx * 105 * open_k) @ T(-sx * win_w / 4, 0, 0.02)
            sc.box(S, (win_w / 2, win_h, 0.05), trim, layer=3)
            sc.box(S @ T(0, 0, 0.02), (win_w / 2 - 0.12, win_h - 0.12, 0.03), (150, 176, 214), layer=3)
    if curtains:
        for sx in (-1, 1):
            sc.box(T(sx * (win_w / 2 - 0.08), win_y + 0.05, -th - 0.12), (0.28, win_h + 0.1, 0.06), curtains, layer=3)
    # room behind the window
    room = tuple(int(v * 0.55) for v in (210, 190, 160)) if old else (236, 200, 160)
    sc.box(T(0, 3.0, -4.0), (8.0, 6.0, 0.2), room, layer=1)
    sc.box(T(0, 0.9, -1.5), (8.0, 0.1, 5.0), (120, 96, 80), layer=1)
    for sx in (-1, 1):
        sc.box(T(sx * 3.4, 3.0, -2.0), (0.2, 6.0, 4.0), room, layer=1)
    if shelf:
        sc.box(T(-1.4, 2.6, -3.75), (1.8, 0.08, 0.4), (120, 90, 70), layer=2)
        rng = np.random.RandomState(2)
        for i in range(6):
            paper_plane(sc, T(-2.1 + i * 0.28, 2.66, -3.7) @ RY(rng.uniform(-30, 30)), s=0.32)
    if room_k > 0:
        sc.light((0.8, 3.4, -2.6), (255, 190, 120), 120 * room_k, 0.6)
    lamp_k = 0.0 if lamp_k is None else lamp_k
    lamp = porch_lamp(sc, T(lamp_x, win_y + 0.1, 0), lamp_k, watts=lamp_watts, cobweb=old and lamp_k < 0.5)
    return dict(sill=np.array([0, y0 - 0.0, 0.18]), sill_in=np.array([0, y0 - 0.02, -th - 0.1]),
                win=np.array([0, win_y, 0]), lamp=lamp, inside=np.array([0, 0.9, -0.75]))


def nova_room(sc, lamp_k=1.0):
    """Nova's bedroom at night: wall with an open window (night outside), bed, nightstand with alarm clock."""
    sets.floor_tiles(sc, -6, 6, -4, 8, (150, 112, 90), (140, 104, 84), step=1.0)

    def paper(D):
        for k in range(-30, 31):
            D.line([(k / 30, -1), (k / 30, 1)], (150, 160, 214), 0.004)
        for u, v in ((-0.7, 0.5), (-0.4, -0.2), (0.6, 0.6), (0.75, -0.4), (-0.85, -0.6)):
            D.poly(star_poly(u, v, 0.03), (250, 220, 120))

    sets.wall(sc, 0, 3.5, -3.2, 12, 7, (160, 170, 226), decal=paper)
    # window opening in the back wall, sky behind
    sc.box(T(1.6, 3.0, -3.0), (1.6, 1.6, 0.05), (14, 22, 58), layer=2, lit=False)
    for u, v in ((1.2, 3.4), (1.9, 2.6), (2.1, 3.5), (1.4, 2.5)):
        sc.blob(T(u, v, -2.95), (0.035, 0.035, 0.01), (255, 250, 220), layer=2, lit=False, n=6, m=4)
    trim = (250, 248, 240)
    for sx in (-1, 1):
        sc.box(T(1.6 + sx * 0.86, 3.0, -2.98), (0.12, 1.84, 0.12), trim, layer=3)
    sc.box(T(1.6, 3.86, -2.98), (1.84, 0.12, 0.12), trim, layer=3)
    sc.box(T(1.6, 2.14, -2.85), (2.0, 0.1, 0.42), trim, layer=3)  # sill
    sets.bed(sc, -2.6, -0.6)
    sc.box(T(-0.6, 0.5, -2.4), (0.9, 1.0, 0.8), (190, 140, 100), layer=3)  # nightstand
    sc.light((-1.0, 3.8, 1.0), (255, 200, 140), 260 * lamp_k, 1.0)
    return dict(sill=np.array([1.6, 2.2, -2.85]), clock=np.array([-0.6, 1.0, -2.3]))


def star_poly(u, v, r):
    return sets.star_poly(u, v, r)


def alarm_clock(sc, M, text="9:00", glow_k=1.0):
    """Digital alarm clock (display faces +z of M)."""
    sc.box(M @ T(0, 0.22, 0), (0.9, 0.44, 0.34), (60, 64, 80), layer=6)

    def face(D):
        D.rect(-1, -1, 1, 1, (20, 10, 14))
        fit_text(D, [text], (255, 80, 64), aspect=0.76 / 0.32, fill_w=0.86, fill_h=0.8)

    sc.box(M @ T(0, 0.23, 0.172), (0.76, 0.32, 0.01), (20, 10, 14), layer=6, decal=face, lit=False)
    if glow_k > 0:
        sc.light(xf(M, (0, 0.25, 0.5)), (255, 80, 60), 6 * glow_k, 0.2)


def party_hat(sc, M, color=(255, 90, 140)):
    v = [(0, 0.5, 0)] + [(0.2 * math.cos(a), 0, 0.2 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
    f = [(0, i + 1, (i + 1) % 8 + 1) for i in range(8)] + [tuple(range(8, 0, -1))]
    sc.solid(M, v, f, color, layer=6)
    sc.blob(M @ T(0, 0.52, 0), (0.12, 0.12, 0.12), (255, 230, 90), layer=6, n=8, m=6)


def big_bush(sc, x, z, s=1.6, c=(56, 140, 70)):
    for dx, dy, dz, k in ((0, 0.55, 0, 1.0), (-0.6, 0.4, 0.2, 0.75), (0.65, 0.42, 0.1, 0.8), (0.1, 0.95, -0.1, 0.65)):
        sc.blob(T(x + dx * s, dy * s, z + dz * s), (1.5 * s * k, 1.1 * s * k, 1.2 * s * k),
                tuple(min(255, v + int(10 * dx)) for v in c), layer=4, n=12, m=8)
