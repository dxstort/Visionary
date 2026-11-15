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
    "fade": ("dot", "dot", "sad", "flat"),
}


def _eye(D, cx, kind, side, skin):
    cy = 0.0
    if kind == "dot":
        D.ell(cx, cy, 0.12, 0.19, INK)
        D.ell(cx + 0.04, cy + 0.08, 0.04, 0.06, WHITE, n=10)
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
        D.arc(0, -0.38, 0.26, 0.17, 200, 340, INK, 0.07)
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
        _brow(D, brow)
        if expr == "miserable":
            for s in (-1, 1):
                D.arc(s * 0.42, -0.2, 0.15, 0.06, 200, 340, (150, 110, 120), 0.04)
        _mouth(D, mouth)
        if spec.get("stache"):
            c = spec["stache"]
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
def _spec(**kw):
    base = dict(s=1.0, skin=(255, 205, 160), shirt=(80, 160, 255), pants=(60, 70, 120), shoes=(250, 250, 250),
                hair=(110, 70, 40), head=(1.0, 0.95, 0.95), torso=(0.92, 0.95, 0.5), arm=(0.28, 0.85),
                leg=(0.38, 0.72), sleeve=0.75, style="generic")
    base.update(kw)
    return base


HERO = _spec(name="Hero", style="cap", shirt=(255, 140, 30), pants=(45, 85, 190), shoes=(245, 245, 250),
             hair=(95, 60, 35), accent=(40, 200, 200))
PIP = _spec(name="Pip", style="pigtails", s=0.6, head=(1.25, 1.15, 1.1), torso=(0.95, 0.85, 0.55),
            arm=(0.28, 0.72), leg=(0.36, 0.5), shirt=(255, 105, 180), pants=(255, 240, 250), shoes=(160, 90, 255),
            hair=(250, 200, 70), blush=True, accent=(160, 90, 255), sleeve=0.55, skirt=True)
TUCK = _spec(name="Tuck", style="spiky", s=0.98, shirt=(60, 190, 255), pants=(40, 60, 110), shoes=(255, 220, 60),
             hair=(245, 240, 225), skin=(245, 190, 150), accent=(255, 220, 60), cape=(255, 220, 60))
BRAX = _spec(name="Brax", style="flat", s=1.22, head=(0.95, 0.9, 0.9), torso=(1.3, 1.05, 0.62), arm=(0.42, 0.92),
             leg=(0.48, 0.7), shirt=(225, 45, 55), pants=(40, 40, 50), shoes=(250, 250, 250), hair=(30, 28, 35),
             skin=(190, 130, 95), accent=(255, 255, 255), sleeve=0.3)
DAD = _spec(name="Dad", style="side", s=1.38, head=(0.9, 0.9, 0.88), torso=(1.0, 1.1, 0.52), arm=(0.28, 1.0),
            leg=(0.4, 1.0), shirt=(70, 165, 95), pants=(120, 100, 80), shoes=(90, 60, 40), hair=(110, 70, 40),
            glasses=True, stache=(110, 70, 40), tie=(235, 60, 60))
MAYOR = _spec(name="Mayor Bigsby", style="tophat", s=1.32, head=(1.05, 0.95, 0.95), torso=(2.0, 1.3, 1.25),
              arm=(0.38, 0.95), leg=(0.5, 0.6), shirt=(125, 60, 190), pants=(60, 40, 100), shoes=(30, 30, 40),
              hair=(215, 215, 225), skin=(250, 195, 165), stache=(215, 215, 225), sash=(255, 205, 50))
BABY = _spec(name="Baby", style="curl", s=0.42, head=(1.3, 1.2, 1.15), torso=(0.95, 0.8, 0.6), arm=(0.3, 0.6),
             leg=(0.36, 0.42), shirt=(255, 255, 255), pants=(255, 255, 255), shoes=(255, 205, 160), sleeve=0.0,
             blush=True)
NURSE = _spec(name="Nurse", style="nurse", s=1.3, head=(0.92, 0.9, 0.88), torso=(0.95, 1.05, 0.5), arm=(0.27, 0.95),
              leg=(0.38, 0.95), shirt=(70, 200, 185), pants=(70, 200, 185), shoes=(255, 255, 255),
              hair=(70, 45, 35), skin=(225, 165, 125))

CROWD_COLORS = [(255, 99, 99), (99, 200, 120), (99, 150, 255), (255, 190, 70), (190, 110, 255), (255, 130, 200),
                (80, 210, 210), (240, 240, 110)]
CROWD_SKIN = [(255, 205, 160), (225, 165, 125), (190, 130, 95), (245, 190, 150), (140, 95, 70)]
CROWD_HAIR = [(40, 30, 30), (110, 70, 40), (250, 200, 70), (200, 80, 40), (90, 90, 100)]


def crowd_spec(i, adult=False):
    return _spec(name="Extra", style=("generic", "bob", "generic")[i % 3], s=1.3 if adult else 0.95,
                 shirt=CROWD_COLORS[i % 8], pants=CROWD_COLORS[(i * 3 + 5) % 8], skin=CROWD_SKIN[i % 5],
                 hair=CROWD_HAIR[(i * 2) % 5])


# ------------------------------------------------------------------ posing
def character(sc, spec, pos=(0, 0, 0), yaw=0, face="smile", pose=None, live=False, layer=5, face_extra=None,
              shadow=True, shadow_y=None):
    """Build a posed character. Pose keys (degrees): lean, roll, y, al/ar=(pitch, roll) for the screen-left /
    screen-right arm when facing camera, ll/lr leg pitch, head=(yaw, pitch, roll), spin (extra yaw after lean).
    Returns world-space anchors."""
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
    if shadow and sc is not None:
        gy = pos[1] if shadow_y is None else shadow_y
        r = tw * 0.75
        pts = [(pos[0] + r * math.cos(a), gy + 0.012, pos[2] + r * 0.7 * math.sin(a)) for a in np.linspace(0, 6.28, 14)[:-1]]
        sc.quad(pts, (0, 0, 0, 55), layer=1)

    # legs
    for sx, key in ((-1, "ll"), (1, "lr")):
        J = body @ T(sx * (tw / 2 - lw / 2 - 0.02 * s) if tw < 1.5 * s else sx * tw * 0.22, ll, 0) @ RX(-p.get(key, 0))
        shoe_h = min(0.2 * s, ll * 0.35)
        B(J @ T(0, -(ll - shoe_h) / 2, 0), (lw, ll - shoe_h, lw), pants)
        B(J @ T(0, -ll + shoe_h / 2, 0.05 * s), (lw * 1.04, shoe_h, lw + 0.14 * s), spec["shoes"])

    # torso
    Mt = body @ T(0, ll + th / 2, 0)
    torso_decal = None
    if spec["style"] == "cap":
        def torso_decal(D):
            D.poly([(0.1, 0.75), (-0.38, -0.05), (-0.05, -0.05), (-0.18, -0.75), (0.4, 0.15), (0.05, 0.15), (0.3, 0.75)],
                   (255, 235, 90))
    elif spec.get("tie"):
        def torso_decal(D):
            D.poly([(-0.3, 1), (0, 0.55), (0.3, 1)], (250, 250, 250))
            D.poly([(-0.1, 0.72), (0.1, 0.72), (0.14, -0.2), (0, -0.4), (-0.14, -0.2)], spec["tie"])
    elif spec.get("sash"):
        def torso_decal(D):
            D.poly([(-1, 0.95), (-0.75, 1), (1, -0.55), (1, -0.9)], spec["sash"])
            D.ell(0.1, 0.05, 0.13, 0.17, (255, 240, 150), n=14)
            for v in (0.55, 0.2, -0.15):
                D.ell(-0.45, v - 0.5, 0.05, 0.065, (255, 225, 90), n=10)
    elif spec["style"] == "flat":
        def torso_decal(D):
            D.text(0, 0.05, "1", (255, 255, 255), h=0.42)
    elif spec["style"] == "spiky":
        def torso_decal(D):
            D.poly([(-0.5, 0.25), (0, -0.35), (0.5, 0.25), (0.3, 0.25), (0, -0.1), (-0.3, 0.25)], (255, 255, 255))
    B(Mt, (tw, th, td), shirt, decal=torso_decal)
    if spec.get("skirt"):
        B(body @ T(0, ll + 0.1 * s, 0), (tw * 1.3, 0.34 * s, td * 1.45), shirt, bias=-0.02)
        B(body @ T(0, ll + 0.34 * s, 0), (tw * 1.04, 0.1 * s, td * 1.06), spec["accent"], bias=-0.03)
    if spec.get("cape"):
        B(Mt @ T(0, -0.12 * s, -td / 2 - 0.05 * s) @ RX(-p.get("cape", 8)) @ T(0, -0.1 * s, -0.02),
          (tw * 0.95, th * 1.25, 0.06 * s), spec["cape"])

    # arms
    hands = {}
    for sx, key in ((-1, "al"), (1, "ar")):
        pitch, roll = p.get(key, (0, 6))
        J = body @ T(sx * (tw / 2 + aw / 2), ll + th - 0.06 * s, 0) @ RZ(sx * roll) @ RX(-pitch)
        sl = al * spec["sleeve"]
        if sl > 0.01:
            B(J @ T(0, -sl / 2 + 0.06 * s, 0), (aw, sl, aw), shirt)
        B(J @ T(0, -sl - (al - sl) / 2 + 0.06 * s, 0), (aw * 0.98, al - sl, aw * 0.98), skin)
        hands["hand_l" if sx < 0 else "hand_r"] = xf(J, (0, -al + 0.06 * s, 0))
        hands["M_arm_l" if sx < 0 else "M_arm_r"] = J

    # head
    hy, hp, hr = p.get("head", (0, 0, 0))
    Mh = body @ T(0, ll + th, 0) @ RY(hy) @ RX(hp) @ RZ(hr) @ T(0, hh / 2, 0)
    B(Mh, (hw, hh, hd), skin, decal=face_decal(face, spec, face_extra) if face else None, bias=-0.02)
    _hair(sc, spec, Mh, hw, hh, hd, s, B)

    out = dict(hands)
    out.update(head=xf(Mh, (0, 0, 0)), head_top=xf(Mh, (0, hh / 2 + (0.35 * s if spec["style"] == "tophat" else 0.12 * s), 0)),
               Mh=Mh, Mt=Mt, body=body, height=ll + th + hh, face_pt=xf(Mh, (0, 0, hd / 2)))
    return out


def _hair(sc, spec, Mh, hw, hh, hd, s, B):
    st, hair = spec["style"], spec["hair"]
    top = lambda h=0.26, c=hair, g=1.07, **kw: B(Mh @ T(0, hh / 2 - hh * h / 2 + 0.035 * s, 0),
                                                 (hw * g, hh * h, hd * g), c, bias=-0.3, **kw)
    back = lambda h=0.7, c=hair: B(Mh @ T(0, hh / 2 - hh * h / 2 + 0.03 * s, -hd / 2 + 0.08 * s),
                                   (hw * 1.07, hh * h, 0.26 * s), c, bias=-0.1)
    if st == "cap":
        back(0.62)
        top(0.3, spec["shirt"])
        B(Mh @ T(0, hh / 2 - hh * 0.25, hd / 2 + 0.2 * s), (hw * 0.8, 0.07 * s, 0.42 * s), spec["accent"], bias=-0.5)
        B(Mh @ T(0, hh / 2 + 0.07 * s, 0), (0.16 * s, 0.08 * s, 0.16 * s), spec["accent"], bias=-0.6)
    elif st == "pigtails":
        back(0.8)
        top(0.24)
        for sx in (-1, 1):
            B(Mh @ T(sx * (hw / 2 + 0.2 * s), 0.08 * s, -0.05 * s) @ RZ(sx * -14), (0.34 * s, 0.5 * s, 0.34 * s), hair,
              bias=-0.25)
            B(Mh @ T(sx * (hw / 2 + 0.05 * s), 0.3 * s, -0.05 * s), (0.14 * s, 0.16 * s, 0.2 * s), spec["accent"],
              bias=-0.35)
        B(Mh @ T(0.28 * s, hh / 2 + 0.1 * s, 0.25 * s) @ RZ(-12), (0.42 * s, 0.2 * s, 0.12 * s), spec["accent"],
          bias=-0.6)
    elif st == "spiky":
        back(0.6)
        top(0.22)
        for i, (x, z, r) in enumerate(((-0.3, 0.1, 20), (0.0, 0.2, -8), (0.3, 0.05, -24), (0.1, -0.2, 12))):
            B(Mh @ T(x * s, hh / 2 + 0.12 * s, z * s) @ RZ(r) @ RY(30 * i), (0.26 * s, 0.34 * s, 0.26 * s), hair,
              bias=-0.5)
        B(Mh @ T(0, hh * 0.27, 0), (hw * 1.1, 0.13 * s, hd * 1.1), (60, 60, 75), bias=-0.4)
        for sx in (-1, 1):
            B(Mh @ T(sx * 0.2 * s, hh * 0.27, hd / 2 + 0.06 * s), (0.3 * s, 0.2 * s, 0.1 * s), spec["accent"],
              bias=-0.7)
    elif st == "flat":
        back(0.55)
        B(Mh @ T(0, hh / 2 + 0.1 * s, 0), (hw * 1.06, 0.36 * s, hd * 1.06), hair, bias=-0.3)
        B(Mh @ T(0, hh * 0.3, 0), (hw * 1.1, 0.12 * s, hd * 1.1), spec["accent"], bias=-0.45)
    elif st == "side":
        back(0.6)
        top(0.2)
        B(Mh @ T(-0.18 * s, hh / 2 + 0.03 * s, 0.1 * s) @ RZ(8), (hw * 0.75, 0.16 * s, hd * 0.9), hair, bias=-0.5)
    elif st == "tophat":
        back(0.65)
        for sx in (-1, 1):
            B(Mh @ T(sx * hw / 2, 0.05 * s, -0.05 * s), (0.1 * s, 0.45 * s, hd * 0.8), hair, bias=-0.2)
        B(Mh @ T(0, hh / 2 + 0.03 * s, 0), (hw * 1.4, 0.07 * s, hd * 1.4), (35, 30, 45), bias=-0.4)
        B(Mh @ T(0, hh / 2 + 0.1 * s, 0), (hw * 0.9, 0.1 * s, hd * 0.9), spec["sash"], bias=-0.5)
        B(Mh @ T(0, hh / 2 + 0.4 * s, 0), (hw * 0.86, 0.52 * s, hd * 0.86), (35, 30, 45), bias=-0.6)
    elif st == "curl":
        B(Mh @ T(0, hh / 2 + 0.05 * s, 0.05 * s) @ RZ(20), (0.22 * s, 0.22 * s, 0.22 * s), hair, bias=-0.4)
    elif st == "nurse":
        back(0.75)
        top(0.2)
        B(Mh @ T(0, hh / 2 + 0.14 * s, 0.05 * s), (hw * 0.8, 0.26 * s, hd * 0.5), (255, 255, 255), bias=-0.5,
          decal=lambda D: (D.rect(-0.12, -0.6, 0.12, 0.6, (235, 50, 60)), D.rect(-0.4, -0.2, 0.4, 0.2, (235, 50, 60))))
    elif st == "bob":
        back(0.95)
        top(0.24)
        for sx in (-1, 1):
            B(Mh @ T(sx * hw / 2, -0.02 * s, -0.08 * s), (0.12 * s, hh * 0.85, hd * 0.75), hair, bias=-0.2)
    else:
        back(0.6)
        top(0.24)


# convenience poses
def sit():
    return dict(ll=88, lr=88)
