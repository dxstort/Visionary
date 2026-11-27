"""Sets and props for When Echoes Do The Talking: the echo effect itself (a word sticker, a sound ring and the same
word coming back a beat later), Mr Gomez's library, Rudy's and Lily's bedrooms with the thin wall between them,
the kitchen props (pancakes), backstage, the talent-show stage, judges' table, pizza boxes and the song sign."""
import math

import numpy as np

import laughs_sets as ls
import sets
from engine import RX, RY, RZ, T, clamp, font, glow, lerp

ECHO_A = (255, 226, 90)     # the word as it is said
ECHO_B = (130, 226, 255)    # the echo
WOOD = (190, 140, 92)
BOOK_COLORS = [(220, 80, 80), (80, 150, 220), (240, 190, 60), (90, 180, 120), (180, 110, 220), (250, 140, 70)]


# ------------------------------------------------------------- the echo itself
def rings(sc, anchor, t, start, color=ECHO_B, n=3, hold=1.0, size=1.2):
    """Sound rings spreading from a world anchor."""
    tt = t - start
    if tt < 0 or tt > hold:
        return
    k = tt / hold
    anchor = np.asarray(anchor, float)

    def fn(d, x, y, s, col):
        for i in range(n):
            q = k - i * 0.16
            if q <= 0 or q >= 1:
                continue
            r = size * s * (0.15 + 0.85 * q)
            a = int(210 * (1 - q))
            w = max(3, int(s * 0.05 * (1 - q) + 2))
            d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], outline=tuple(color) + (a,), width=w)

    sc.sprite(anchor, fn, layer=8, live=True)


def say(sc, anchor, text, t, start=0.0, hold=1.3, size=0.5, color=ECHO_A, dx=0.0, dy=0.6, rot=-8, ring=True):
    ls.sticker(sc, anchor, text, t, start=start, hold=hold, size=size, color=color, dx=dx, dy=dy, rot=rot)
    if ring:
        rings(sc, anchor, t, start, color=color, n=2, hold=0.9, size=1.0)


def echo(sc, anchor, text, t, start=0.0, delay=0.7, hold=1.3, size=0.5, dx=0.0, dy=0.6, soft=None):
    """A word, then the same word again in blue a beat later, a little further out and smaller."""
    say(sc, anchor, text, t, start, hold, size, ECHO_A, dx, dy, -8)
    low = (text.lower() if soft is None else soft)
    say(sc, anchor, low, t, start + delay, hold, size * 0.86, ECHO_B, dx + size * 0.35, dy + size * 1.2, 7)


def echo_text(sc, anchor, text, t, start=0.0, delay=0.7, hold=1.3, size=0.5, dx=0.0, dy=0.6):
    """Echo with the second copy in the same case and an extra ring (for whispers and names)."""
    echo(sc, anchor, text, t, start, delay, hold, size, dx, dy, soft=text)


def notes(sc, origin, t, n=4):
    ls.music_notes(sc, origin, t, n=n)


def spotlight(sc, pos, r=2.0, a=70, color=(255, 246, 200)):
    ls.glow_at(sc, pos, r, color, a)


# ------------------------------------------------------------------- props
def pancake(sc, M, s=1.0, flip=0.0):
    sc.blob(M @ T(0, 0.04 * s, 0) @ RX(flip), (0.55 * s, 0.12 * s, 0.55 * s), (232, 176, 96), e=0.5, layer=7, n=12, m=5)
    sc.blob(M @ T(0, 0.1 * s, 0) @ RX(flip), (0.4 * s, 0.05 * s, 0.4 * s), (252, 214, 120), e=0.5, layer=7, n=10, m=4)


def spatula(sc, M, s=1.0):
    sc.box(M @ T(0, 0.0, 0), (0.05 * s, 0.5 * s, 0.05 * s), (110, 80, 60), layer=7)
    sc.box(M @ T(0, 0.4 * s, 0.0), (0.3 * s, 0.22 * s, 0.03 * s), (200, 200, 210), layer=7)


def pizza_box(sc, M, s=1.0, open_k=0.0):
    sc.box(M @ T(0, 0.08 * s, 0), (1.0 * s, 0.16 * s, 1.0 * s), (236, 200, 150), layer=6,
           decal=lambda D: None)
    sc.box(M @ T(0, 0.17 * s, 0), (0.96 * s, 0.02 * s, 0.96 * s), (252, 244, 226), layer=6,
           decal=lambda D: (D.ell(0, 0, 0.7, 0.7, (240, 170, 70), n=24), D.ell(0, 0, 0.55, 0.55, (230, 80, 60), n=24),
                            [D.ell(0.3 * math.cos(a), 0.3 * math.sin(a), 0.09, 0.09, (60, 150, 70), n=8)
                             for a in (0.4, 1.9, 3.3, 4.6)]))


def mic_stand(sc, x, z, y=0.9, s=1.0):
    sc.box(T(x, y + 0.7 * s, z), (0.06 * s, 1.4 * s, 0.06 * s), (70, 70, 80), layer=5)
    sc.blob(T(x, y + 1.45 * s, z + 0.05), (0.22 * s, 0.26 * s, 0.22 * s), (190, 190, 200), layer=6, n=10, m=7)


def song_page(sc, M, w=0.7, h=0.95, text=True, live=False):
    def deco(D):
        D.rect(-1, -1, 1, 1, (252, 250, 240))
        if text:
            for k in range(6):
                D.line([(-0.7, 0.7 - k * 0.28), (0.7 - (k % 3) * 0.15, 0.7 - k * 0.28)], (110, 110, 140), 0.05)
            D.text(0, 0.9, "MY SONG", (60, 50, 140), h=0.13)

    sc.box(M, (w, h, 0.02), (252, 250, 240), layer=7, decal=deco, live=live)


def sign(sc, M, lines, size=(2.6, 1.5), color=(250, 240, 200), ink=(60, 50, 90), live=False):
    def deco(D):
        D.rect(-1, -1, 1, 1, color)
        D.rect(-0.96, -0.94, 0.96, 0.94, tuple(int(v * 0.88) for v in color))
        n = len(lines)
        for k, ln in enumerate(lines):
            D.text(0, 0.55 - k * (1.1 / max(1, n - 1)) if n > 1 else 0, ln, ink, h=0.3 if n > 1 else 0.4)

    sc.box(M, (size[0], size[1], 0.12), color, layer=4, decal=deco, live=live)


def bookshelf(sc, x, z, yaw=0, w=3.0, h=4.2, seed=1):
    rng = np.random.RandomState(seed)
    M = T(x, 0, z) @ RY(yaw)
    sc.box(M @ T(0, h / 2, 0), (w, h, 0.7), (130, 92, 62), layer=3)
    for r in range(5):
        y = 0.25 + r * (h - 0.4) / 5
        k = 0.2
        while k < w - 0.25:
            bw = rng.uniform(0.12, 0.28)
            bh = rng.uniform(0.55, 0.78)
            c = BOOK_COLORS[rng.randint(0, 6)]
            sc.box(M @ T(-w / 2 + k + bw / 2, y + bh / 2 + 0.06, 0.1), (bw, bh, 0.5), c, layer=4)
            k += bw + 0.02
        sc.box(M @ T(0, y, 0.08), (w, 0.07, 0.62), (100, 70, 48), layer=4)


def library(sc, t=0.0, shush=0.0):
    """Mr Gomez's library: tall shelves, a carpet, a reading table and a QUIET sign. Characters near z=0."""
    sets.floor_tiles(sc, -12, 12, -6, 12, (176, 132, 96), (166, 122, 88), step=1.5)
    sets.wall(sc, 0, 3.5, -6.5, 26, 7, (238, 222, 190))
    for i, x in enumerate((-8, -4.2, 4.2, 8)):
        bookshelf(sc, x, -5.9, 0, w=3.4, h=5.2, seed=i + 2)
    sc.box(T(0, 5.6, -6.2), (3.6, 1.4, 0.12), (250, 240, 200), layer=3,
           decal=lambda D: D.text(0, 0.0, "QUIET PLEASE", (180, 60, 60), h=0.3))
    sets.desk(sc, -1.2, -2.6, top=(190, 150, 100), h=1.1, w=3.0, d=1.2)
    for k in range(3):
        sc.box(T(-2.0 + k * 0.4, 1.25 + k * 0.1, -2.6), (0.5, 0.14, 0.38), BOOK_COLORS[k + 2], layer=5)


def shush_signs(sc, t, start, n=5):
    """Floating 'shh' pennants that grow as the library echoes."""
    for i in range(n):
        ang = i * 0.9 + 0.3
        say(sc, (math.cos(ang) * 2.4, 2.6 + 0.35 * (i % 3), -1.0 + math.sin(ang) * 0.5), "shh",
            t, start + i * 0.16, hold=1.0, size=0.42, color=ECHO_B if i % 2 else ECHO_A, dx=0.0, dy=0.2,
            rot=-10 + 5 * i, ring=False)


def two_rooms(sc, t=0.0, lamp=True):
    """Rudy's room (x<0, blue) and Lily's room (x>0, pink) with one thin wall between them; open to the camera (+z).
    Each room is 3.4 wide so both fit in a portrait frame."""
    sets.floor_tiles(sc, -6, 6, -4, 5, (206, 168, 120), (196, 158, 112), step=1.5)
    sets.wall(sc, -2.6, 3.5, -4.2, 5.6, 7, (150, 188, 240))
    sets.wall(sc, 2.6, 3.5, -4.2, 5.6, 7, (250, 176, 206))
    sets.wall(sc, 0.0, 3.5, 0.0, 0.5, 7, (236, 226, 214), yaw=0, d=7.8)
    sets.bed(sc, -3.6, -1.6, blanket=(80, 120, 220))
    sets.bed(sc, 3.6, -1.6, blanket=(240, 110, 170))
    sc.box(T(-1.9, 4.6, -3.95), (1.7, 1.0, 0.1), (252, 252, 250), layer=2,
           decal=lambda D: D.text(0, 0, "ROCK STAR", (80, 80, 160), h=0.4))
    sc.box(T(1.9, 4.6, -3.95), (1.7, 1.0, 0.1), (252, 252, 250), layer=2,
           decal=lambda D: D.text(0, 0, "DANCE QUEEN", (220, 80, 150), h=0.32))


def backstage(sc, t=0.0, glow_k=1.0):
    """Dark wings: curtains, rope, a bright sliver of stage. Camera looks toward -z; the stage is at z<-3."""
    sc.ground((84, 60, 58))
    sets.wall(sc, 0, 3.5, -4.0, 18, 7, (46, 30, 62))
    red = (170, 36, 56)
    for i, x in enumerate((-6.5, -3.6, 3.6, 6.5)):
        sc.box(T(x, 3.5, -2.2), (2.6, 7.0, 0.5), red if i % 2 else tuple(int(v * 0.85) for v in red), layer=2,
               decal=lambda D: [D.line([(u, -1), (u, 1)], (120, 20, 40), 0.06) for u in (-0.6, -0.2, 0.2, 0.6)])
    sc.box(T(0, 3.5, -3.6), (3.8, 7.0, 0.2), (255, 244, 210), layer=1, lit=False)
    ls.glow_at(sc, (0.0, 2.0, -3.4), 3.4, (255, 240, 190), int(90 * glow_k))
    sc.box(T(-2.0, 0.6, 1.0), (0.8, 1.2, 0.8), (110, 80, 60), layer=3)
    sc.box(T(2.2, 0.9, 1.4), (1.0, 1.8, 0.7), (96, 70, 52), layer=3)


def hall(sc, t=0.0, faces=None, standing=False, crowd=True, banner="TALENT NIGHT"):
    """The talent-show stage (sets.stage) with our banner; audience faces the stage."""
    sets.stage(sc)

    def deco(D):
        D.rect(-1, -1, 1, 1, (40, 34, 120))
        D.text(0, 0.05, banner, (255, 230, 90), h=0.45)

    sc.box(T(0, 5.4, sets.STAGE_Z - 2.0), (9.0, 1.5, 0.1), (40, 34, 120), layer=2, bias=-0.3, decal=deco)
    if crowd:
        sets.audience(sc, t, faces=faces, standing=standing, rows=3, per_row=7, seed=2)


def clock(sc, x, y, z, minute=56, second=0, hour=6, s=1.5):
    sc.box(T(x, y, z), (s, s, 0.22), (40, 34, 50), layer=3, decal=sets.clock_face(hour, minute, second))


def judge_table(sc, x=0.0, z=2.0, t=0.0):
    sets.desk(sc, x, z, top=(250, 250, 246), h=1.0, w=6.0, d=1.3)
    sc.box(T(x, 0.6, z - 0.66) @ RY(180), (5.6, 0.9, 0.06), (60, 50, 140), layer=4,
           decal=lambda D: D.text(0, 0, "JUDGES", (255, 230, 90), h=0.5))


def paddle(sc, M, n="10", s=1.0):
    sc.box(M @ T(0, -0.35 * s, 0), (0.06 * s, 0.7 * s, 0.06 * s), (110, 80, 60), layer=7)
    sc.box(M @ T(0, 0.15 * s, 0), (0.7 * s, 0.7 * s, 0.05 * s), (255, 250, 240), layer=7,
           decal=lambda D: D.text(0, 0, n, (200, 40, 60), h=0.85))


def trophy_duet(sc, M, s=1.0):
    gold = (250, 200, 60)
    sc.box(M @ T(0, 0.25 * s, 0), (1.5 * s, 0.5 * s, 1.0 * s), (90, 60, 40), layer=5,
           decal=lambda D: None)
    for sx in (-1, 1):
        sc.blob(M @ T(sx * 0.4 * s, 0.9 * s, 0), (0.3 * s, 0.6 * s, 0.3 * s), gold, e=0.8, layer=5)
        sc.blob(M @ T(sx * 0.4 * s, 1.7 * s, 0), (1.0 * s, 1.1 * s, 1.0 * s), gold, e=0.9, layer=5)
    sc.box(M @ T(0, 0.25 * s, 0.51 * s), (1.2 * s, 0.3 * s, 0.02 * s), (250, 220, 120), layer=5,
           decal=lambda D: D.text(0, 0, "BEST DUET", (60, 40, 20), h=0.6))


def hands_up(t, i=0, k=1.0):
    c = 0.5 + 0.5 * math.sin(t * 9 + i)
    return dict(al=(150 + 25 * c * k, 12), ar=(150 + 25 * c * k, 12), y=0.06 * c * k)
