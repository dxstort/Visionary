"""Original blocky toy cast: specs, face expressions and posing."""
import math

import numpy as np

from engine import RX, RY, RZ, T, xf

INK = (40, 28, 48)
WHITE = (255, 255, 255)

# eyes(left on screen, right on screen), brow, mouth
EXPR = {
    "smile": ("dot", "dot", None, "smile"),
    "neutral": ("dot", "dot", None, "flat"),
    "smirk": ("lid", "lid", "one", "smirk"),
    "smug": ("lid", "lid", "one", "smirk"),
    "shock": ("wide", "wide", "raised", "open"),
    "jaw": ("wide", "wide", "raised", "jaw"),
    "grit": ("dot", "dot", "angry", "grit"),
    "effort": ("shut", "shut", "angry", "grit"),
    "sparkle": ("sparkle", "sparkle", None, "grin"),
    "grin": ("dot", "dot", None, "grin"),
    "sad": ("dot", "dot", "sad", "frown"),
    "stung": ("wide", "wide", "sad", "wobble"),
    "miserable": ("lid", "lid", "sad", "frown"),
    "angry": ("dot", "dot", "angry", "frown"),
    "suspicious": ("lid", "lid", "angry", "flat"),
    "sleep": ("closed", "closed", None, "o"),
    "wink": ("dot", "happy", None, "grin"),
    "cry": ("shut", "shut", "sad", "wail"),
    "laugh": ("happy", "happy", None, "laugh"),
    "chew0": ("happy", "happy", None, "chew0"),
    "chew1": ("happy", "happy", None, "chew1"),
    "worried": ("dot", "dot", "sad", "wobble"),
    "joy": ("happy", "happy", None, "grin"),
    "fade": ("dot", "dot", "sad", "flat"),
}


def _eye(D, cx, kind, side, skin):
    cy = 0.0
    if kind == "dot":
        D.ell(cx, cy, 0.115, 0.2, INK)
        D.ell(cx + 0.035, cy + 0.09, 0.035, 0.055, WHITE, n=10)
    elif kind == "lid":
        D.ell(cx, cy, 0.12, 0.19, INK)
        D.rect(cx - 0.17, cy + 0.03, cx + 0.17, cy + 0.24, skin)
        D.line([(cx - 0.17, cy + 0.04), (cx + 0.17, cy + 0.04)], INK, 0.06)
    elif kind == "wide":
        D.ell(cx, cy + 0.03, 0.2, 0.25, INK)
        D.ell(cx, cy + 0.03, 0.155, 0.205, WHITE)
        D.ell(cx, cy + 0.03, 0.06, 0.08, INK, n=12)
    elif kind == "sparkle":
        D.ell(cx, cy + 0.03, 0.19, 0.25, INK)
        D.ell(cx + 0.06, cy + 0.12, 0.075, 0.095, WHITE, n=12)
        D.ell(cx - 0.07, cy - 0.07, 0.04, 0.05, WHITE, n=10)
        D.ell(cx + 0.02, cy - 0.12, 0.09, 0.05, (120, 200, 255), n=10)
    elif kind == "closed":
        D.arc(cx, cy + 0.05, 0.15, 0.1, 200, 340, INK, 0.065)
    elif kind == "happy":
        D.arc(cx, cy - 0.06, 0.15, 0.14, 20, 160, INK, 0.07)
    elif kind == "shut":
        s = 1 if side > 0 else -1
        D.line([(cx + s * 0.15, cy + 0.12), (cx - s * 0.12, cy), (cx + s * 0.15, cy - 0.12)], INK, 0.065)


def _brow(D, kind):
    if kind == "angry":
        for s in (-1, 1):
            D.line([(s * 0.6, 0.38), (s * 0.2, 0.22)], INK, 0.085)
    elif kind == "sad":
        for s in (-1, 1):
            D.line([(s * 0.6, 0.26), (s * 0.24, 0.4)], INK, 0.07)
    elif kind == "raised":
        for s in (-1, 1):
            D.arc(s * 0.42, 0.36, 0.17, 0.07, 20, 160, INK, 0.06)
    elif kind == "one":
        D.line([(-0.58, 0.27), (-0.24, 0.27)], INK, 0.07)
        D.arc(0.42, 0.34, 0.18, 0.1, 15, 165, INK, 0.07)


def _mouth(D, kind):
    red, teeth = (225, 70, 85), (255, 255, 255)
    if kind == "smile":
        D.arc(0, -0.36, 0.28, 0.2, 200, 340, INK, 0.085)
    elif kind == "flat":
        D.line([(-0.18, -0.5), (0.18, -0.5)], INK, 0.07)
    elif kind == "smirk":
        D.line([(-0.2, -0.53), (0.0, -0.55), (0.2, -0.49), (0.33, -0.38)], INK, 0.07)
    elif kind == "open":
        D.ell(0, -0.55, 0.15, 0.2, INK)
        D.ell(0, -0.63, 0.09, 0.09, red, n=12)
    elif kind == "jaw":
        D.ell(0, -0.58, 0.24, 0.33, INK)
        D.ell(0, -0.74, 0.15, 0.13, red, n=12)
        D.rect(-0.14, -0.33, 0.14, -0.27, teeth)
    elif kind == "o":
        D.ell(0, -0.52, 0.07, 0.08, INK, n=12)
    elif kind == "grit":
        D.rect(-0.34, -0.66, 0.34, -0.38, INK)
        D.rect(-0.29, -0.62, 0.29, -0.42, teeth)
        for x in (-0.145, 0.0, 0.145):
            D.line([(x, -0.62), (x, -0.42)], INK, 0.035)
        D.line([(-0.29, -0.52), (0.29, -0.52)], INK, 0.035)
    elif kind == "frown":
        D.arc(0, -0.66, 0.24, 0.16, 25, 155, INK, 0.07)
    elif kind == "wobble":
        D.line([(-0.24, -0.52), (-0.12, -0.46), (0.0, -0.54), (0.12, -0.46), (0.24, -0.52)], INK, 0.065)
    elif kind in ("grin", "laugh", "wail"):
        w, h, top = {"grin": (0.3, 0.26, -0.36), "laugh": (0.38, 0.4, -0.3), "wail": (0.3, 0.34, -0.36)}[kind]
        pts = [(-w, top), (w, top)] + [(w * math.cos(a), top - h * math.sin(a)) for a in np.linspace(0, math.pi, 12)]
        D.poly(pts, INK)
        D.rect(-w * 0.8, top - 0.08, w * 0.8, top - 0.015, teeth)
        D.ell(0, top - h * 0.72, w * 0.5, h * 0.22, red, n=12)
    elif kind in ("chew0", "chew1"):
        k = 1 if kind == "chew0" else -1
        D.ell(0.5 * k, -0.42, 0.2, 0.17, (255, 170, 160), n=14)
        D.line([(-0.14, -0.5 + 0.03 * k), (0.0, -0.53 - 0.03 * k), (0.14, -0.5 + 0.03 * k)], INK, 0.07)


def face_decal(expr, spec, extra=None):
    el, er, brow, mouth = EXPR[expr]
    skin = spec["skin"]

    def decal(D):
        if spec.get("blush"):
            for s in (-1, 1):
                D.ell(s * 0.66, -0.3, 0.13, 0.08, (255, 150, 165), n=12)
        lit_skin = tuple(v * D.lit for v in skin)
        _eye(D, -0.42, el, -1, lit_skin)
        _eye(D, 0.42, er, 1, lit_skin)
        if spec.get("glasses"):
            for s in (-1, 1):
                D.arc(s * 0.42, 0.02, 0.27, 0.3, 0, 360, (60, 60, 80), 0.05, n=20)
            D.line([(-0.15, 0.06), (0.15, 0.06)], (60, 60, 80), 0.05)
        if spec.get("bushy"):
            bc = spec["bushy"]
            tilt = {"angry": -0.12, "sad": 0.1, "raised": 0.0}.get(brow, 0.0)
            lift = 0.06 if brow == "raised" else 0.0
            for sgn in (-1, 1):
                inner, outer = (sgn * 0.16, 0.3 + lift + tilt), (sgn * 0.7, 0.3 + lift - tilt)
                D.poly([(inner[0], inner[1] - 0.06), (outer[0], outer[1] - 0.04), (outer[0] + sgn * 0.06, outer[1] + 0.1),
                        (sgn * 0.42, 0.44 + lift), (inner[0], inner[1] + 0.08)], bc)
        else:
            _brow(D, brow)
        if expr == "miserable":
            for s in (-1, 1):
                D.arc(s * 0.42, -0.2, 0.15, 0.06, 200, 340, (150, 110, 120), 0.04)
        _mouth(D, mouth)
        if spec.get("shades"):
            D.poly([(-0.78, 0.2), (-0.06, 0.2), (-0.12, -0.14), (-0.62, -0.18)], (24, 22, 30))
            D.poly([(0.06, 0.2), (0.78, 0.2), (0.62, -0.18), (0.12, -0.14)], (24, 22, 30))
            D.line([(-0.82, 0.2), (0.82, 0.2)], (24, 22, 30), 0.07)
            D.poly([(-0.6, 0.14), (-0.42, 0.14), (-0.56, -0.02)], (120, 120, 140))
            D.poly([(0.24, 0.14), (0.42, 0.14), (0.28, -0.02)], (120, 120, 140))
        if spec.get("stache") and not spec.get("stache_big"):
            c = spec["stache"]
            if False:
                D.poly([(0, -0.26), (-0.22, -0.2), (-0.5, -0.26), (-0.74, -0.2), (-0.86, -0.04), (-0.8, -0.3),
                        (-0.56, -0.44), (-0.24, -0.4), (0, -0.34), (0.24, -0.4), (0.56, -0.44), (0.8, -0.3),
                        (0.86, -0.04), (0.74, -0.2), (0.5, -0.26), (0.22, -0.2)], c)
            else:
                D.poly([(-0.42, -0.36), (-0.2, -0.24), (0, -0.3), (0.2, -0.24), (0.42, -0.36), (0.3, -0.42),
                        (0, -0.38), (-0.3, -0.42)], c)
        if expr == "cry":
            for s in (-1, 1):
                D.poly([(s * 0.34, -0.08), (s * 0.5, -0.08), (s * 0.54, -0.95), (s * 0.3, -0.95)], (120, 205, 255))
        if extra:
            extra(D)

    return decal


def marker_moustache(D):
    D.line([(0, -0.27), (-0.2, -0.2), (-0.42, -0.3), (-0.6, -0.16)], (20, 20, 30), 0.085)
    D.line([(0, -0.27), (0.2, -0.2), (0.42, -0.3), (0.6, -0.16)], (20, 20, 30), 0.085)


# ------------------------------------------------------------------- specs
# Proportions follow the chunky toy-avatar look: box torso, arms half as wide as the torso and flush with it,
# two legs filling the torso width, a round-cylinder head. Sizes are in units of `s`.
def _spec(**kw):
    base = dict(s=1.0, skin=(250, 204, 164), shirt=(80, 160, 255), pants=(54, 66, 112), shoes=(240, 240, 240),
                hair=(70, 46, 34), head=(0.74, 0.7, 0.74), torso=(1.0, 1.0, 0.5), arm=(0.5, 1.0), leg=(0.5, 1.0),
                sleeve=0.84, style="short")
    base.update(kw)
    return base


HERO = _spec(name="Hero", style="frog", skin=(246, 224, 192), shirt=(226, 246, 234), arm_shirt=(132, 222, 182),
             pants=(52, 62, 96), shoes=(240, 240, 240), hair=(108, 72, 46), hat=(126, 218, 160), frogtee=True,
             sleeve=0.5)
PIP = _spec(name="Pip", style="pigtails", s=0.6, head=(0.98, 0.92, 0.98), torso=(1.0, 0.86, 0.52), arm=(0.48, 0.86),
            leg=(0.5, 0.72), skin=(246, 224, 192), shirt=(190, 70, 44),
            stripes=[(190, 70, 44), (236, 140, 60), (248, 212, 120), (120, 56, 40)], pants=(78, 104, 150),
            shoes=(240, 240, 240), hair=(250, 226, 172), accent=(255, 170, 196), overalls=(78, 104, 150))
TUCK = _spec(name="Tuck", style="messy", s=0.98, skin=(150, 100, 70), shirt=(240, 112, 40), pants=(46, 50, 70),
             shoes=(240, 240, 240), hair=(26, 22, 28), headphones=True, sleeve=0.5)
BRAX = _spec(name="Brax", style="silver", s=1.14, torso=(1.16, 1.0, 0.56), arm=(0.56, 1.0), leg=(0.56, 0.98),
             skin=(246, 224, 192), shirt=(66, 50, 206), pants=(36, 36, 46), shoes=(245, 245, 245),
             hair=(222, 214, 196), shades=True, hoodie2=True, sleeve=0.86)
DAD = _spec(name="Dad", style="beanie", s=1.3, skin=(246, 224, 192), shirt=(92, 120, 80), pants=(58, 60, 72),
            shoes=(60, 46, 40), hair=(176, 92, 52), beard=(176, 92, 52), floral=True, sleeve=0.5,
            hat=(36, 36, 44))
MAYOR = _spec(name="Mayor Bigsby", style="tophat", s=1.28, head=(0.8, 0.72, 0.8), torso=(1.56, 1.16, 0.86),
              arm=(0.52, 1.02), leg=(0.56, 0.78), shirt=(30, 30, 36), pants=(30, 30, 36), shoes=(20, 20, 24),
              hair=(240, 236, 228), skin=(246, 224, 192), stache=(244, 240, 232), stache_big=True, suit=True,
              belly=True)
BABY = _spec(name="Baby", style="curl", s=0.42, head=(1.1, 1.0, 1.1), torso=(1.0, 0.82, 0.62), arm=(0.46, 0.7),
             leg=(0.5, 0.52), shirt=(255, 255, 255), pants=(255, 255, 255), shoes=(246, 224, 192), sleeve=0.3,
             blush=True, hair=(110, 70, 44), skin=(246, 224, 192))
NURSE = _spec(name="Nurse", style="nurse", s=1.28, shirt=(70, 196, 182), pants=(70, 196, 182), shoes=(255, 255, 255),
              hair=(66, 42, 34), skin=(214, 156, 118), sleeve=0.45)

ABERNATHY = _spec(name="Mr Abernathy", style="elder", s=1.24, head=(0.78, 0.74, 0.76), torso=(1.04, 1.0, 0.56),
                  skin=(240, 206, 178), shirt=(132, 104, 84), inner=(236, 226, 204), cardigan=True,
                  pants=(96, 98, 108), shoes=(88, 60, 44), hair=(236, 236, 240), bushy=(240, 240, 244),
                  glasses=True, ears=True, sleeve=0.86)
ORTIZ = _spec(name="Mrs Ortiz", style="bun", s=1.2, skin=(214, 156, 118), shirt=(150, 90, 170), inner=(250, 240, 220),
              cardigan=True, pants=(70, 60, 90), shoes=(60, 50, 60), hair=(150, 146, 150), glasses=True,
              accent=(240, 120, 160), sleeve=0.86)
MAILMAN = _spec(name="Mailman", style="cap", s=1.26, skin=(176, 118, 86), shirt=(130, 170, 220), uniform=True,
                pants=(40, 52, 96), shoes=(30, 30, 36), hair=(30, 24, 22), hat=(40, 52, 96), sleeve=0.5)

ZARA = _spec(name="Zara", style="puffs", s=0.98, skin=(176, 118, 86), shirt=(250, 190, 60), pants=(70, 92, 150),
             shoes=(240, 240, 240), hair=(40, 30, 28), goggles_head=True, sleeve=0.5)
PHAM = _spec(name="Mr Pham", style="elder", s=1.2, head=(0.76, 0.72, 0.74), skin=(232, 196, 160), shirt=(200, 96, 84),
             inner=(244, 236, 220), cardigan=True, pants=(80, 84, 96), shoes=(70, 56, 46), hair=(120, 120, 126),
             bushy=(140, 140, 146), glasses=True, ears=True, sleeve=0.86)
MIA = _spec(name="Mia", style="bob", s=0.98, skin=(236, 190, 150), shirt=(255, 210, 60), raincoat=True,
            pants=(60, 80, 130), shoes=(220, 60, 60), boots=0.6, strap=(190, 50, 50), hair=(110, 66, 40), sleeve=0.86)
OMAR = _spec(name="Omar", style="tuft", s=0.98, skin=(150, 100, 70), shirt=(90, 170, 110), pants=(70, 70, 90),
             shoes=(240, 240, 240), hair=(30, 24, 22), sleeve=0.5)
FARMER = _spec(name="Omar's dad", style="cap", s=1.28, skin=(150, 100, 70), shirt=(70, 120, 180), flannel=True,
               suspenders=(120, 90, 60), pants=(110, 90, 60), shoes=(90, 70, 50), hair=(30, 24, 22),
               beard=(36, 28, 26), hat=(200, 60, 50), sleeve=0.86)
BRYCE = _spec(name="Bryce", style="messy", s=1.0, skin=(250, 214, 180), shirt=(240, 100, 60), pants=(60, 70, 110),
              shoes=(240, 240, 240), hair=(220, 120, 60), sleeve=0.5)
RUDY = _spec(name="Rudy", style="side", s=0.98, skin=(214, 156, 118), shirt=(60, 170, 90), jersey=True,
             accent=(250, 220, 80), pants=(30, 40, 60), shoes=(240, 240, 240), hair=(70, 46, 30), sleeve=0.86)
DOYLE = _spec(name="Mrs Doyle", style="bun", s=1.14, skin=(246, 214, 190), shirt=(200, 150, 200), inner=(250, 244, 232),
              cardigan=True, pants=(90, 80, 110), shoes=(120, 90, 80), hair=(242, 242, 246), glasses=True,
              accent=(150, 200, 240), sleeve=0.86)
GUS = _spec(name="Grandpa Gus", style="elder", s=1.3, head=(0.8, 0.74, 0.78), torso=(1.1, 1.0, 0.58),
            skin=(236, 198, 168), shirt=(170, 62, 52), flannel=True, suspenders=(66, 50, 40), pants=(70, 74, 92),
            shoes=(96, 100, 112), boots=1.6, strap=(56, 52, 50), hair=(232, 232, 236), bushy=(236, 236, 240),
            stache=(236, 236, 240), ears=True, sleeve=0.86)
MOM = _spec(name="Mom", style="bob", s=1.24, skin=(246, 224, 192), shirt=(110, 176, 222), pants=(70, 80, 110),
            shoes=(96, 100, 112), boots=1.0, hair=(120, 74, 44), sleeve=0.5)
UNCLE_RAY = _spec(name="Uncle Ray", style="beanie", s=1.26, skin=(246, 224, 192), shirt=(244, 160, 60), pants=(60, 70, 96),
                  shoes=(60, 46, 40), hair=(176, 92, 52), beard=(176, 92, 52), hat=(214, 70, 64), sleeve=0.5)

CROWD_COLORS = [(240, 96, 96), (96, 190, 120), (96, 146, 240), (250, 186, 76), (180, 110, 240), (250, 130, 190),
                (80, 200, 200), (232, 226, 110)]
CROWD_SKIN = [(250, 204, 164), (214, 156, 118), (176, 118, 86), (236, 178, 140), (130, 88, 66)]
CROWD_HAIR = [(40, 30, 30), (104, 66, 40), (240, 190, 80), (190, 80, 44), (90, 90, 100)]


def crowd_spec(i, adult=False):
    return _spec(name="Extra", style=("short", "bob", "spiky", "tuft")[i % 4], s=1.25 if adult else 0.95,
                 shirt=CROWD_COLORS[i % 8], pants=CROWD_COLORS[(i * 3 + 5) % 8], skin=CROWD_SKIN[i % 5],
                 hair=CROWD_HAIR[(i * 2) % 5])


# ---------------------------------------------------------------- clothing
def _torso_decal(spec):
    st = spec["style"]

    def decal(D):
        if spec.get("apron"):
            a = spec["apron"]
            D.poly([(-0.5, 0.7), (0.5, 0.7), (0.75, -1), (-0.75, -1)], a)
            D.line([(-0.5, 0.7), (-0.2, 1.0)], a, 0.04)
            D.line([(0.5, 0.7), (0.2, 1.0)], a, 0.04)
            D.rect(-0.35, -0.7, 0.35, -0.2, tuple(v * 0.9 for v in a))
        elif spec.get("frogtee"):
            D.arc(0, 0.92, 0.3, 0.2, 180, 360, spec["arm_shirt"], 0.07)
            for sx in (-1, 1):
                D.poly([(sx * 1, 1), (sx * 0.56, 1), (sx * 1, 0.4)], spec["arm_shirt"])
            D.ell(-0.16, 0.36, 0.11, 0.1, (96, 190, 100), n=14)
            D.ell(0.16, 0.36, 0.11, 0.1, (96, 190, 100), n=14)
            D.ell(0, 0.18, 0.3, 0.2, (96, 190, 100), n=20)
            for sx in (-1, 1):
                D.ell(sx * 0.16, 0.38, 0.06, 0.06, (255, 255, 255), n=10)
                D.ell(sx * 0.16, 0.37, 0.03, 0.035, (30, 30, 30), n=8)
                D.ell(sx * 0.2, 0.14, 0.035, 0.025, (255, 150, 160), n=8)
            D.arc(0, 0.2, 0.1, 0.06, 200, 340, (30, 60, 30), 0.03)
        elif spec.get("floral"):
            rnd = np.random.RandomState(7)
            D.rect(-1, -1, 1, 1, spec["shirt"])
            for _ in range(70):
                u, v = rnd.uniform(-1, 1, 2)
                c = [(60, 90, 50), (140, 120, 70), (200, 90, 110), (230, 200, 120), (40, 70, 60)][rnd.randint(5)]
                D.ell(u, v, rnd.uniform(0.06, 0.16), rnd.uniform(0.05, 0.12), c, n=8, rot=rnd.uniform(0, 180))
            D.poly([(-0.32, 1), (0, 0.62), (0.32, 1)], spec["skin"])
        elif spec.get("suit"):
            D.poly([(-0.36, 1), (0.36, 1), (0.12, -0.2), (-0.12, -0.2)], (250, 250, 250))
            D.poly([(-0.08, 0.86), (0.08, 0.86), (0.11, 0.0), (0, -0.16), (-0.11, 0.0)], (200, 30, 40))
            for sx in (-1, 1):
                D.poly([(sx * 0.36, 1), (sx * 0.12, -0.2), (sx * 0.3, 0.3), (sx * 0.5, 1)], (16, 16, 20))
            D.arc(-0.42, 0.1, 0.4, 0.3, 200, 340, (240, 196, 60), 0.035)
            D.ell(-0.8, 0.08, 0.06, 0.06, (240, 196, 60), n=10)
        elif spec.get("hoodie2"):
            D.arc(0, 0.92, 0.36, 0.26, 180, 360, tuple(v * 0.75 for v in spec["shirt"]), 0.08)
            D.rect(-0.6, -0.85, 0.6, -0.3, tuple(v * 0.88 for v in spec["shirt"]))
            for sx in (-1, 1):
                D.line([(sx * 0.16, 0.8), (sx * 0.18, 0.3)], (230, 230, 240), 0.03)
        elif spec.get("hoodie"):
            D.rect(-0.62, -0.9, 0.62, -0.32, tuple(v * 0.9 for v in spec["shirt"]))
            D.line([(-0.62, -0.32), (0.62, -0.32)], tuple(v * 0.75 for v in spec["shirt"]), 0.03)
            for sx in (-1, 1):
                D.line([(sx * 0.18, 0.92), (sx * 0.2, 0.42)], (250, 250, 250), 0.035)
                D.ell(sx * 0.2, 0.4, 0.04, 0.04, (250, 250, 250), n=8)
            D.ell(0.0, 0.08, 0.26, 0.26, (60, 56, 70), n=20)
            D.ell(0.0, 0.08, 0.21, 0.21, spec["accent"], n=20)
            D.line([(0.0, 0.08), (0.0, 0.24)], (60, 56, 70), 0.04)
            D.line([(0.0, 0.08), (0.11, 0.02)], (60, 56, 70), 0.04)
            D.arc(0, 0.86, 0.36, 0.24, 180, 360, tuple(v * 0.8 for v in spec["shirt"]), 0.05)
        elif spec.get("overalls"):
            st_ = spec["stripes"]
            for k in range(-10, 10):
                D.rect(-1, k * 0.1, 1, k * 0.1 + 0.1, st_[k % len(st_)])
            o = spec["overalls"]
            D.rect(-0.62, -1, 0.62, 0.15, o)
            D.rect(-1, -1, 1, -0.55, o)
            for sx in (-1, 1):
                D.poly([(sx * 0.62, 0.15), (sx * 0.4, 0.15), (sx * 0.58, 1), (sx * 0.8, 1)], o)
                D.ell(sx * 0.48, 0.05, 0.07, 0.07, (255, 220, 90), n=10)
            D.rect(-0.3, -0.5, 0.3, -0.1, tuple(v * 0.9 for v in o))
            D.line([(-0.3, -0.1), (0.3, -0.1), (0.3, -0.5), (-0.3, -0.5), (-0.3, -0.1)], (200, 170, 110), 0.02)
            D.line([(-0.62, 0.12), (0.62, 0.12)], (200, 170, 110), 0.02)
        elif spec.get("jersey"):
            D.rect(-1, 0.55, 1, 0.68, spec["accent"])
            D.rect(-1, -0.95, 1, -0.85, spec["accent"])
            D.poly([(-0.3, 1), (0, 0.66), (0.3, 1)], spec["skin"])
            D.text(0, -0.12, "7", spec["accent"], h=0.44)
        elif spec.get("tie"):
            v = spec["vest"]
            for sx in (-1, 1):
                D.poly([(sx * 1, 1), (sx * 0.3, 1), (sx * 0.0, 0.3), (sx * 0.0, -1), (sx * 1, -1)], v)
            D.poly([(-0.3, 1), (0, 0.72), (0.3, 1)], (255, 255, 255))
            D.poly([(-0.09, 0.78), (0.09, 0.78), (0.13, -0.05), (0, -0.25), (-0.13, -0.05)], spec["tie"])
            for vv in (-0.35, -0.6):
                D.ell(0.12, vv, 0.04, 0.045, (230, 220, 190), n=8)
            for k in range(-4, 5):
                D.line([(-1, k * 0.2), (-0.3, k * 0.2)], tuple(c * 0.92 for c in v), 0.015)
                D.line([(0.3, k * 0.2), (1, k * 0.2)], tuple(c * 0.92 for c in v), 0.015)
        elif spec.get("sash"):
            D.rect(-0.12, -1, 0.12, 1, (250, 250, 250))
            D.poly([(-0.2, 1), (0, 0.6), (0.2, 1)], (250, 250, 250))
            D.poly([(-0.07, 0.78), (0.07, 0.78), (0, 0.66)], (40, 30, 50))
            D.poly([(-0.95, 0.8), (-0.72, 0.95), (0.95, -0.55), (0.9, -0.82)], spec["sash"])
            D.ell(0.22, 0.12, 0.13, 0.15, (255, 236, 140), n=14)
            D.ell(0.22, 0.12, 0.08, 0.09, (235, 160, 40), n=12)
            for vv in (-0.25, -0.5, -0.75):
                D.ell(-0.28, vv, 0.045, 0.05, (255, 225, 90), n=10)
        elif spec.get("cape"):
            D.poly([(-0.46, 0.32), (0, -0.28), (0.46, 0.32), (0.28, 0.32), (0, -0.04), (-0.28, 0.32)], (255, 255, 255))
            D.arc(0, 0.9, 0.3, 0.22, 180, 360, tuple(v * 0.8 for v in spec["shirt"]), 0.05)
        elif spec.get("flannel"):
            dk = tuple(v * 0.62 for v in spec["shirt"])
            lt = tuple(min(255, v * 1.25) for v in spec["shirt"])
            for k in range(-5, 6):
                D.rect(k * 0.2 - 0.04, -1, k * 0.2 + 0.04, 1, dk)
                D.rect(-1, k * 0.2 - 0.04, 1, k * 0.2 + 0.04, dk)
                D.line([(-1, k * 0.2 + 0.1), (1, k * 0.2 + 0.1)], lt, 0.012)
            D.poly([(-0.3, 1), (0, 0.66), (0.3, 1)], spec["skin"])
            for sx in (-1, 1):
                D.rect(sx * 0.5 - 0.07, -1, sx * 0.5 + 0.07, 1, spec.get("suspenders", (70, 50, 40)))
                D.ell(sx * 0.5, -0.55, 0.06, 0.06, (236, 196, 80), n=8)
        elif spec.get("raincoat"):
            dk = tuple(int(v * 0.8) for v in spec["shirt"])
            D.poly([(-0.36, 1), (0, 0.6), (0.36, 1)], dk)
            D.line([(0.0, 0.6), (0.0, -1)], dk, 0.03)
            for vv in (0.3, -0.05, -0.4, -0.75):
                D.ell(-0.12, vv, 0.06, 0.06, (60, 60, 70), n=10)
            for sx in (-1, 1):
                D.rect(sx * 0.6 - 0.22, -0.7, sx * 0.6 + 0.22, -0.35, dk)
        elif spec.get("cardigan"):
            D.poly([(-0.42, 1), (0.42, 1), (0.0, -0.2)], spec["inner"])
            D.poly([(-0.2, 1), (0, 0.78), (0.2, 1)], spec["skin"])
            D.line([(-0.42, 1), (0.0, -0.2), (0.0, -1)], tuple(v * 0.78 for v in spec["shirt"]), 0.05)
            D.line([(0.42, 1), (0.0, -0.2)], tuple(v * 0.78 for v in spec["shirt"]), 0.05)
            for vv in (-0.35, -0.6, -0.85):
                D.ell(-0.1, vv, 0.045, 0.05, (230, 210, 170), n=8)
            for sx in (-1, 1):
                D.rect(sx * 0.62 - 0.2, -0.75, sx * 0.62 + 0.2, -0.45, tuple(v * 0.88 for v in spec["shirt"]))
            D.rect(-1, -1, 1, -0.88, tuple(v * 0.8 for v in spec["shirt"]))
        elif spec.get("uniform"):
            D.poly([(-0.4, 1), (0, 0.6), (0.4, 1)], spec["skin"])
            for sx in (-1, 1):
                D.poly([(sx * 0.05, 0.6), (sx * 0.4, 1), (sx * 0.62, 0.88), (sx * 0.2, 0.55)],
                       tuple(v * 0.86 for v in spec["shirt"]))
            D.line([(0, 0.6), (0, -1)], tuple(v * 0.8 for v in spec["shirt"]), 0.03)
            for vv in (0.3, -0.05, -0.4, -0.75):
                D.ell(0.06, vv, 0.035, 0.04, (250, 250, 250), n=8)
            D.rect(-0.66, 0.0, -0.26, 0.36, tuple(v * 0.9 for v in spec["shirt"]))
            D.ell(0.46, 0.22, 0.14, 0.16, (220, 60, 60), n=14)
            D.poly([(0.38, 0.3), (0.54, 0.3), (0.46, 0.12)], (255, 255, 255))
        elif st == "nurse":
            D.poly([(-0.34, 1), (0, 0.55), (0.34, 1)], spec["skin"])
            D.rect(0.3, 0.1, 0.66, 0.45, tuple(v * 0.88 for v in spec["shirt"]))
            D.rect(0.36, 0.3, 0.4, 0.62, (60, 60, 80))
        elif spec["name"] == "Baby":
            D.ell(0, -0.1, 0.32, 0.3, (190, 228, 255), n=16)
        else:
            D.arc(0, 0.9, 0.3, 0.22, 180, 360, tuple(v * 0.8 for v in spec["shirt"]), 0.05)

    return decal


def _arm_decal(spec):
    if spec.get("overalls"):
        def decal(D):
            st_ = spec["stripes"]
            for k in range(-10, 10):
                D.rect(-1, k * 0.1, 1, k * 0.1 + 0.1, st_[k % len(st_)])
        return decal
    if spec.get("floral"):
        def decal(D):
            rnd = np.random.RandomState(3)
            for _ in range(25):
                u, v = rnd.uniform(-1, 1, 2)
                c = [(60, 90, 50), (140, 120, 70), (200, 90, 110), (230, 200, 120)][rnd.randint(4)]
                D.ell(u, v, 0.2, 0.08, c, n=8, rot=rnd.uniform(0, 180))
        return decal
    if spec.get("hoodie"):
        return lambda D: D.rect(-1, -1, 1, -0.86, tuple(v * 0.8 for v in spec["shirt"]))
    return None


# ------------------------------------------------------------------ posing
def character(sc, spec, pos=(0, 0, 0), yaw=0, face="smile", pose=None, live=False, layer=5, face_extra=None,
              shadow=True, shadow_y=None):
    """Build a posed character. Pose keys (degrees): lean, roll, y; al/ar=(pitch, roll) shoulder for the
    screen-left / screen-right arm when facing camera, el/er elbow bend; ll/lr hip pitch, kl/kr knee bend;
    head=(yaw, pitch, roll); cape. Returns world-space anchors."""
    p = pose or {}
    s = spec["s"]
    hw, hh, hd = (v * s for v in spec["head"])
    tw, th, td = (v * s for v in spec["torso"])
    aw, al = (v * s for v in spec["arm"])
    lw, ll = (v * s for v in spec["leg"])
    skin, shirt, pants = spec["skin"], spec["shirt"], spec["pants"]

    def B(M, size, color, **kw):
        sc.box(M, size, color, layer=layer, live=live, **kw)

    body = T(pos[0], pos[1] + p.get("y", 0.0), pos[2]) @ RY(yaw) @ RX(p.get("lean", 0)) @ RZ(p.get("roll", 0))
    if shadow:
        gy = pos[1] if shadow_y is None else shadow_y
        for k, a in ((1.0, 24), (0.75, 30), (0.5, 36)):
            r = (tw + aw) * 0.62 * k
            pts = [(pos[0] + r * math.cos(t), gy + 0.012, pos[2] + r * 0.6 * math.sin(t))
                   for t in np.linspace(0, 6.283, 17)[:-1]]
            sc.quad(pts, (10, 20, 40, a), layer=1)

    # legs (hip pivot at the top, optional knee)
    hipx = min(tw / 4, lw / 2 + 0.01 * s)
    shoe_h = ll * 0.18
    leg_col = spec.get("overalls", pants)
    feet = {}
    for sx, key, kk in ((-1, "ll", "kl"), (1, "lr", "kr")):
        J = body @ T(sx * hipx, ll, 0) @ RX(-p.get(key, 0))
        knee = p.get(kk, 0)
        if abs(knee) < 1:
            B(J @ T(0, -(ll - shoe_h) / 2, 0), (lw, ll - shoe_h, lw), leg_col)
            K = J @ T(0, -ll / 2, 0)
        else:
            B(J @ T(0, -ll / 4, 0), (lw, ll / 2, lw), leg_col)
            K = J @ T(0, -ll / 2, 0) @ RX(knee)
            B(K @ T(0, -(ll / 2 - shoe_h) / 2, 0), (lw * 0.995, ll / 2 - shoe_h, lw * 0.995), leg_col)
        bk = spec.get("boots", 0)
        if bk and not p.get("barefoot"):
            # heavy iron boots: big, tall, with a strap and buckle round the top
            bh = shoe_h * (1.2 + 0.9 * bk)
            bw, bd = lw * (1.0 + 0.32 * bk), lw * (1.12 + 0.42 * bk)
            Mb = K @ T(0, -ll / 2 + bh / 2, 0.05 * s * bk)
            B(Mb, (bw, bh, bd), spec["shoes"])
            B(Mb @ T(0, bh * 0.28, 0), (bw * 1.04, bh * 0.16, bd * 1.04), spec.get("strap", (70, 60, 52)))
            B(Mb @ T(sx * bw * 0.52, bh * 0.28, bd * 0.1), (0.05 * s, bh * 0.2, bh * 0.22), (236, 196, 80))
        else:
            B(K @ T(0, -ll / 2 + shoe_h / 2, 0.025 * s), (lw * 1.02, shoe_h, lw * 1.1),
              (236, 236, 240) if p.get("barefoot") else spec["shoes"])
        feet["foot_l" if sx < 0 else "foot_r"] = xf(K, (0, -ll / 2, 0))

    # torso
    Mt = body @ T(0, ll + th / 2, 0)
    B(Mt, (tw, th, td), shirt, decal=_torso_decal(spec))
    if spec.get("belly"):
        def buttons(D):
            for v in (0.45, 0.05, -0.35):
                D.ell(0, v, 0.07, 0.07, (255, 214, 90), n=10)
            D.arc(0.38, 0.25, 0.4, 0.3, 200, 330, (255, 214, 90), 0.035)

        sc.blob(Mt @ T(0, -0.12 * s, td / 2 + 0.01 * s), (tw * 0.82, th * 0.76, 0.28 * s), shirt, e=0.8, e2=0.5,
                layer=layer, live=live, bias=-0.06, n=12, m=8, decal=buttons)
    if spec.get("cape"):
        B(Mt @ T(0, th / 2 - 0.04 * s, -td / 2 - 0.04 * s) @ RX(-p.get("cape", 8)) @ T(0, -th * 0.65, -0.02),
          (tw * 0.98, th * 1.3, 0.05 * s), spec["cape"])

    # arms: flush with the torso, pivot at the shoulder
    hands = {}
    adec = _arm_decal(spec)
    for sx, key, ek in ((-1, "al", "el"), (1, "ar", "er")):
        pitch, roll = p.get(key, (0, 2))
        J = body @ T(sx * (tw / 2 + aw / 2), ll + th - aw / 2, 0) @ RZ(sx * roll) @ RX(-pitch)
        top = aw / 2
        sl = al * spec["sleeve"]
        shirt = spec.get("arm_shirt", spec["shirt"])
        bend = p.get(ek, 0)
        if abs(bend) < 1:
            B(J @ T(0, top - sl / 2, 0), (aw, sl, aw), shirt, decal=adec)
            B(J @ T(0, top - sl - (al - sl) / 2, 0), (aw * 0.98, al - sl, aw * 0.98), skin)
            H = J @ T(0, top - al, 0)
        else:
            half = al / 2
            up_sl = min(sl, half)
            B(J @ T(0, top - up_sl / 2, 0), (aw, up_sl, aw), shirt, decal=adec)
            if up_sl < half:
                B(J @ T(0, top - up_sl - (half - up_sl) / 2, 0), (aw * 0.98, half - up_sl, aw * 0.98), skin)
            E = J @ T(0, top - half, 0) @ RX(-bend)
            lo_sl = max(0.0, sl - half)
            if lo_sl > 0:
                B(E @ T(0, -lo_sl / 2, 0), (aw * 0.99, lo_sl, aw * 0.99), shirt)
            B(E @ T(0, -lo_sl - (half - lo_sl) / 2, 0), (aw * 0.98, half - lo_sl, aw * 0.98), skin)
            H = E @ T(0, -half, 0)
        hands["hand_l" if sx < 0 else "hand_r"] = H[:3, 3].copy()
        hands["M_hand_l" if sx < 0 else "M_hand_r"] = H

    # head: rounded cylinder with the face wrapped round the front
    hy, hp, hr = p.get("head", (0, 0, 0))
    Mh = body @ T(0, ll + th, 0) @ RY(hy) @ RX(hp) @ RZ(hr) @ T(0, hh / 2, 0)
    sc.blob(Mh, (hw, hh, hd), skin, e=0.28, e2=1.0, layer=layer, live=live, bias=-0.02, n=36, m=12, span=1.4,
            decal=face_decal(face, spec, face_extra) if face else None)
    top = _hair(sc, spec, Mh, hw, hh, hd, s, layer, live)

    out = dict(hands)
    out.update(feet)
    out.update(head=xf(Mh, (0, 0, 0)), head_top=xf(Mh, (0, hh / 2 + top * s, 0)), Mh=Mh, Mt=Mt, body=body,
               height=ll + th + hh, face_pt=xf(Mh, (0, 0, hd / 2)))
    return out


# -------------------------------------------------------------------- hair
def _spike(sc, M, base, dirn, length, width, color, layer, live, bias=0.0):
    """Four-sided hair spike: base square on the head, apex `length` along `dirn` (head-local)."""
    dirn = np.asarray(dirn, float)
    dirn = dirn / np.linalg.norm(dirn)
    ref = np.array([0.0, 1.0, 0.0]) if abs(dirn[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    p1 = np.cross(dirn, ref)
    p1 /= np.linalg.norm(p1)
    p2 = np.cross(dirn, p1)
    b, h = np.asarray(base, float), width / 2
    verts = [b + h * p1 + h * p2, b - h * p1 + h * p2, b - h * p1 - h * p2, b + h * p1 - h * p2, b + dirn * length]
    sc.solid(M, verts, [(0, 1, 2, 3), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], color, layer=layer, live=live,
             bias=bias)


def _hair(sc, spec, Mh, hw, hh, hd, s, layer, live):
    """Hair and headwear in head-local space. Returns extra height above the head top (in s units)."""
    st, hair = spec["style"], spec["hair"]
    rx, ry, rz = hw / 2, hh / 2, hd / 2
    dark = tuple(v * 0.8 for v in hair)

    def blob(M, size, c, e=0.6, e2=1.0, bias=-0.3, n=14, m=6, decal=None, span=1.2):
        sc.blob(Mh @ M, size, c, e=e, e2=e2, layer=layer, live=live, bias=bias, n=n, m=m, decal=decal, span=span)

    def spike(bx, by, bz, dx, dy, dz, length, width=0.2, c=hair, bias=0.0):
        _spike(sc, Mh, (bx * rx, by * ry, bz * rz), (dx, dy, dz), length * s, width * s, c, layer, live, bias)

    def cap(h=0.42, y=0.44, c=hair, w=1.1, z=-0.03):
        blob(T(0, hh * y, hd * z), (hw * w, hh * h, hd * w), c, e=0.5)

    def back(h=0.9, y=0.0, c=hair):
        blob(T(0, hh * y, -hd * 0.18), (hw * 1.1, hh * h, hd * 0.86), c, e=0.4, bias=0.05)

    def fringe(n=5, y=0.78, length=0.2, c=hair, spread=0.8):
        for i in range(n):
            u = -spread + 2 * spread * i / max(1, n - 1)
            spike(u * 0.9, y, math.cos(u * 0.9) * 0.92, u * 0.25, -0.9, 0.4, length, 0.22, c, bias=-0.05)

    if spec.get("beard"):
        bc = spec["beard"]
        blob(T(0, -hh * 0.32, rz * 0.62), (hw * 1.0, hh * 0.56, hd * 0.62), bc, e=0.7, bias=-0.2, n=16, m=8)
        blob(T(0, -hh * 0.05, rz * 0.9), (hw * 0.62, hh * 0.16, 0.2 * s), bc, e=0.6, bias=-0.3, n=12, m=6)
        for sx in (-1, 1):
            blob(T(sx * rx * 0.92, hh * 0.02, 0.0), (0.16 * s, hh * 0.6, hd * 0.6), bc, e=0.6, bias=-0.1, n=10, m=6)
    if spec.get("headphones"):
        grey = (200, 204, 212)
        for sx in (-1, 1):
            blob(T(sx * (rx + 0.06 * s), 0.0, 0.0) @ RZ(90), (0.36 * s, 0.14 * s, 0.36 * s), grey, e=0.5, bias=-0.2,
                 n=14, m=4)
        for k in range(9):
            a = math.pi * k / 8
            blob(T(math.cos(a) * (rx + 0.08 * s), hh * 0.5 + math.sin(a) * 0.22 * s, -0.02 * s),
                 (0.11 * s, 0.11 * s, 0.11 * s), (90, 92, 104), e=0.8, bias=-0.4, n=8, m=4)
    if spec.get("stache_big"):
        wc = spec["stache"]
        for sx in (-1, 1):
            blob(T(sx * 0.15 * s, -hh * 0.2, rz + 0.04 * s) @ RZ(sx * -14), (0.3 * s, 0.13 * s, 0.12 * s), wc, e=0.8,
                 bias=-0.5, n=12, m=6)
            blob(T(sx * 0.3 * s, -hh * 0.14, rz + 0.0 * s) @ RZ(sx * 40), (0.14 * s, 0.08 * s, 0.1 * s), wc, e=0.8,
                 bias=-0.5, n=10, m=5)
    if st in ("messy", "silver"):
        st = "spiky"
    if st == "frog":
        back(0.62, 0.05)
        for i in range(7):
            a = -1.2 + i * 0.4
            spike(math.sin(a) * 1.0, 0.55, math.cos(a) * 1.0, math.sin(a) * 0.7, -0.6, math.cos(a) * 0.7, 0.13, 0.2,
                  bias=-0.05)
        hat = spec["hat"]
        dk = tuple(v * 0.85 for v in hat)
        blob(T(0, hh * 0.56, -0.01 * s), (hw * 1.1, hh * 0.52, hd * 1.1), hat, e=0.45, bias=-0.35, n=24, m=8)
        blob(T(0, hh * 0.3, 0.01 * s) @ RX(-4), (hw * 1.5, 0.1 * s, hd * 1.5), dk, e=0.7, bias=-0.45, n=24, m=5)
        for sx in (-1, 1):
            ex, ey, ez = sx * 0.2 * s, hh * 0.84, 0.16 * s
            blob(T(ex, ey, ez), (0.24 * s, 0.22 * s, 0.22 * s), hat, e=0.9, bias=-0.6, n=12, m=8)
            blob(T(ex, ey + 0.02 * s, ez + 0.08 * s), (0.15 * s, 0.15 * s, 0.1 * s), (255, 255, 255), e=0.9,
                 bias=-0.7, n=10, m=6)
            blob(T(ex, ey + 0.02 * s, ez + 0.12 * s), (0.08 * s, 0.09 * s, 0.05 * s), (24, 24, 28), e=0.9,
                 bias=-0.8, n=8, m=6)
        return 0.62
    if st == "beanie":
        hat = spec["hat"]
        blob(T(0, hh * 0.58, -0.02 * s), (hw * 1.12, hh * 0.66, hd * 1.12), hat, e=0.6, bias=-0.35, n=24, m=8)
        blob(T(0, hh * 0.38, 0), (hw * 1.16, hh * 0.17, hd * 1.16), tuple(v * 0.8 for v in hat), e=0.3, bias=-0.4,
             n=24, m=4)
        blob(T(0, hh * 0.4, rz + 0.06 * s), (0.24 * s, 0.07 * s, 0.03 * s), (235, 235, 240), e=0.4, bias=-0.6,
             n=8, m=4)
        return 0.4
    if st == "bucket":
        back(0.62, 0.05)
        for i in range(7):
            a = -1.2 + i * 0.4
            spike(math.sin(a) * 1.0, 0.45, math.cos(a) * 1.0, math.sin(a) * 0.6, -0.7, math.cos(a) * 0.6, 0.2, 0.22,
                  bias=-0.05)
        for sx in (-1, 1):
            spike(sx * 1.0, 0.3, -0.2, sx * 0.7, -0.6, -0.1, 0.18, 0.2)
        hat, band = spec["hat"], tuple(v * 0.78 for v in spec["hat"])

        def pin(D):
            D.ell(0.0, 0.0, 0.2, 0.32, (60, 56, 70), n=18)
            D.ell(0.0, 0.0, 0.17, 0.27, (250, 250, 250), n=18)
            D.rect(-0.1, -0.16, -0.03, 0.16, (60, 56, 70))
            D.rect(0.03, -0.16, 0.1, 0.16, (60, 56, 70))

        blob(T(0, hh * 0.56, -0.01 * s), (hw * 1.08, hh * 0.5, hd * 1.08), hat, e=0.35, bias=-0.35, n=20, m=8,
             decal=pin, span=1.3)
        blob(T(0, hh * 0.36, 0), (hw * 1.13, hh * 0.13, hd * 1.13), band, e=0.3, bias=-0.4, n=20, m=4)
        blob(T(0, hh * 0.3, 0.01 * s) @ RX(-4), (hw * 1.62, 0.07 * s, hd * 1.62), hat, e=0.7, bias=-0.45, n=22, m=4)
        return 0.38
    if st == "spiky":
        back(0.7, 0.1)
        cap(0.4, 0.44)
        for i in range(9):
            a = i * 2 * math.pi / 9 + 0.3
            spike(math.sin(a) * 0.62, 0.86, math.cos(a) * 0.62 - 0.1, math.sin(a) * 0.8, 0.85, math.cos(a) * 0.7,
                  0.3, 0.26)
        for x, z in ((-0.2, 0.0), (0.22, -0.1), (0.0, -0.4)):
            spike(x, 0.95, z, x * 0.5, 1.0, z * 0.3, 0.34, 0.26)
        fringe(5, 0.8, 0.2)
        for sx in (-1, 1):
            spike(sx * 1.0, 0.5, -0.1, sx * 0.8, -0.5, -0.2, 0.2, 0.22)
        if spec.get("goggles"):
            blob(T(0, hh * 0.42, 0), (hw * 1.14, 0.1 * s, hd * 1.14), (52, 52, 66), e=0.3, bias=-0.5, n=20, m=4)
            for sx in (-1, 1):
                blob(T(sx * 0.17 * s, hh * 0.44, rz + 0.03 * s), (0.24 * s, 0.18 * s, 0.1 * s), spec["accent"],
                     e=0.6, bias=-0.7, n=10, m=4)
                blob(T(sx * 0.17 * s, hh * 0.44, rz + 0.07 * s), (0.16 * s, 0.11 * s, 0.04 * s), (176, 230, 255),
                     e=0.6, bias=-0.75, n=8, m=4)
        return 0.5
    if st == "pigtails":
        back(0.86, 0.05)
        cap(0.44, 0.44)
        blob(T(0, hh * 0.3, rz * 0.82), (hw * 0.9, hh * 0.2, 0.14 * s), hair, e=0.5, bias=-0.1, n=14, m=4)
        for sx in (-1, 1):
            blob(T(sx * (rx + 0.1 * s), -hh * 0.05, -0.04 * s) @ RZ(sx * 18), (0.3 * s, 0.6 * s, 0.3 * s), hair,
                 e=0.8, bias=0.0, n=10, m=6)
            for k in range(2):
                spike(sx * 1.25, -0.5 - k * 0.3, 0.0, sx * 0.3, -1, 0.0, 0.18, 0.18, bias=-0.01)
            _spike(sc, Mh, (sx * rx * 0.55, hh * 0.62, 0.0), (sx * 0.3, 1.0, 0.0), 0.2 * s, 0.22 * s,
                   spec["accent"], layer, live)
        return 0.28
    if st == "side":
        back(0.6, 0.1)
        cap(0.36, 0.46)
        blob(T(-0.1 * s, hh * 0.55, rz * 0.32) @ RZ(10), (hw * 0.86, hh * 0.24, hd * 0.8), hair, e=0.6, bias=-0.4,
             n=12, m=5)
        spike(0.6, 0.85, 0.6, 1.0, -0.2, 0.3, 0.16, 0.2, dark)
        for sx in (-1, 1):
            spike(sx * 1.0, 0.25, 0.1, sx * 0.3, -1.0, 0.0, 0.16, 0.18)
        return 0.22
    if st == "tophat":
        for sx in (-1, 1):
            blob(T(sx * rx * 0.96, hh * 0.08, -0.05 * s), (0.18 * s, hh * 0.52, hd * 0.72), hair, e=0.6, bias=-0.05,
                 n=10, m=6)
        blob(T(0, hh * 0.02, -rz * 0.6), (hw * 0.9, hh * 0.52, 0.2 * s), hair, e=0.6, bias=0.05, n=10, m=6)
        hat = (36, 32, 44)
        blob(T(0, hh * 0.5, 0), (hw * 1.5, 0.06 * s, hd * 1.5), hat, e=0.6, bias=-0.4, n=22, m=4)
        blob(T(0, hh * 0.5 + 0.08 * s, 0), (hw * 0.92, 0.12 * s, hd * 0.92), spec["shirt"], e=0.2, bias=-0.45, n=20,
             m=4)
        blob(T(0, hh * 0.5 + 0.34 * s, 0), (hw * 0.9, 0.58 * s, hd * 0.9), hat, e=0.15, bias=-0.5, n=20, m=8)
        return 0.68
    if st == "curl":
        blob(T(0, hh * 0.52, 0.06 * s) @ RZ(25), (0.2 * s, 0.24 * s, 0.2 * s), hair, e=0.8, bias=-0.4, n=8, m=5)
        return 0.18
    if st == "nurse":
        back(0.94, 0.0)
        cap(0.4, 0.44)
        blob(T(0, hh * 0.5, -rz * 0.9), (0.4 * s, 0.4 * s, 0.4 * s), hair, e=0.8, bias=0.1, n=10, m=6)

        def cross(D):
            D.rect(-0.12, -0.6, 0.12, 0.6, (228, 54, 62))
            D.rect(-0.4, -0.2, 0.4, 0.2, (228, 54, 62))

        sc.box(Mh @ T(0, hh / 2 + 0.1 * s, 0.1 * s), (hw * 0.66, 0.26 * s, hd * 0.4), (255, 255, 255), layer=layer,
               live=live, bias=-0.55, decal=cross)
        return 0.34
    if st == "puffs":
        back(0.8, 0.05)
        cap(0.42, 0.44)
        for sx in (-1, 1):
            blob(T(sx * rx * 0.62, hh * 0.72, -0.05 * s), (0.5 * s, 0.46 * s, 0.5 * s), hair, e=0.85, bias=-0.2, n=14,
                 m=8)
        if spec.get("goggles_head"):
            blob(T(0, hh * 0.4, 0), (hw * 1.12, 0.1 * s, hd * 1.12), (60, 56, 64), e=0.3, bias=-0.5, n=20, m=4)
            for sx in (-1, 1):
                blob(T(sx * 0.17 * s, hh * 0.44, rz + 0.04 * s), (0.24 * s, 0.2 * s, 0.1 * s), (200, 150, 60), e=0.6,
                     bias=-0.7, n=12, m=4)
                blob(T(sx * 0.17 * s, hh * 0.44, rz + 0.08 * s), (0.16 * s, 0.13 * s, 0.04 * s), (170, 230, 255),
                     e=0.6, bias=-0.75, n=10, m=4)
        return 0.6
    if st == "buzz":
        blob(T(0, hh * 0.44, -0.02 * s), (hw * 1.04, hh * 0.3, hd * 1.04), hair, e=0.5, bias=-0.3, n=16, m=6)
        for x, z in ((-0.15, 0.25), (0.2, -0.1), (0.05, 0.35)):
            blob(T(x * s, hh * 0.58, z * s), (0.2 * s, 0.06 * s, 0.18 * s), spec["skin"], e=0.6, bias=-0.4, n=10, m=4)
        return 0.06
    if st == "chef":
        back(0.62, 0.05)
        cap(0.36, 0.44)
        blob(T(0, hh * 0.46, 0), (hw * 1.06, hh * 0.22, hd * 1.06), (250, 250, 250), e=0.3, bias=-0.4, n=22, m=4)
        blob(T(0, hh * 0.5 + 0.42 * s, 0), (hw * 1.25, 0.7 * s, hd * 1.25), (255, 255, 255), e=0.9, bias=-0.5, n=16,
             m=10)
        for a in (-0.6, 0.0, 0.6):
            blob(T(math.sin(a) * hw * 0.42, hh * 0.5 + 0.62 * s, math.cos(a) * hd * 0.3), (0.42 * s, 0.4 * s, 0.42 * s),
                 (255, 255, 255), e=0.9, bias=-0.55, n=12, m=8)
        return 1.0
    if st == "elder":
        # bald crown with a white horseshoe of hair round the sides and back
        for sx in (-1, 1):
            blob(T(sx * rx * 0.97, hh * 0.12, -0.02 * s), (0.2 * s, hh * 0.46, hd * 0.66), hair, e=0.7, bias=-0.05,
                 n=10, m=6)
            spike(sx * 1.02, 0.35, 0.25, sx * 0.8, 0.3, 0.2, 0.12, 0.16)
        blob(T(0, hh * 0.12, -rz * 0.72), (hw * 0.86, hh * 0.46, 0.22 * s), hair, e=0.7, bias=0.05, n=10, m=6)
        if spec.get("ears"):
            for sx in (-1, 1):
                blob(T(sx * (rx + 0.04 * s), -hh * 0.04, 0.04 * s), (0.12 * s, 0.22 * s, 0.14 * s), spec["skin"],
                     e=0.8, bias=-0.1, n=10, m=6)
        return 0.02
    if st == "bun":
        back(0.95, -0.02)
        cap(0.46, 0.44)
        blob(T(0, hh * 0.3, rz * 0.8), (hw * 0.86, hh * 0.18, 0.12 * s), hair, e=0.5, bias=-0.1, n=14, m=4)
        blob(T(0, hh * 0.68, -rz * 0.45), (0.36 * s, 0.32 * s, 0.36 * s), hair, e=0.8, bias=0.05, n=12, m=8)
        if spec.get("accent"):
            blob(T(0, hh * 0.62, -rz * 0.2), (0.4 * s, 0.07 * s, 0.1 * s), spec["accent"], e=0.6, bias=-0.1, n=8,
                 m=4)
        return 0.42
    if st == "cap":
        back(0.6, 0.05)
        hat = spec["hat"]
        blob(T(0, hh * 0.52, -0.02 * s), (hw * 1.1, hh * 0.48, hd * 1.1), hat, e=0.5, bias=-0.35, n=22, m=8,
             decal=spec.get("cap_decal"), span=1.0)
        sc.box(Mh @ T(0, hh * 0.36, rz + 0.18 * s) @ RX(-8), (hw * 0.9, 0.05 * s, 0.42 * s), tuple(v * 0.85 for v in hat),
               layer=layer, live=live, bias=-0.5)
        for sx in (-1, 1):
            spike(sx * 1.0, 0.3, -0.1, sx * 0.6, -0.8, -0.1, 0.14, 0.18)
        return 0.3
    if st == "bob":
        back(1.1, -0.1)
        cap(0.44, 0.44)
        for sx in (-1, 1):
            blob(T(sx * rx * 0.98, -hh * 0.12, 0.02 * s), (0.18 * s, hh * 0.9, hd * 0.8), hair, e=0.5, bias=-0.05,
                 n=10, m=6)
        fringe(4, 0.78, 0.16)
        return 0.18
    if st == "tuft":
        back(0.6, 0.1)
        cap(0.4, 0.44)
        for a in (-0.4, 0.0, 0.4):
            spike(a, 0.9, 0.2, a * 0.6, 1.0, 0.4, 0.3, 0.26)
        return 0.38
    back(0.62, 0.1)
    cap(0.4, 0.44)
    fringe(5, 0.78, 0.17)
    return 0.16


# convenience poses
def sit():
    """Seated pose: toy-style legs straight out from the hip."""
    return dict(ll=88, lr=88)
