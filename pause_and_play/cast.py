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
    base = dict(s=1.0, skin=(250, 200, 160), shirt=(80, 160, 255), pants=(60, 70, 120), shoes=(250, 250, 250),
                hair=(100, 62, 38), head=(1.08, 0.98, 1.0), torso=(0.98, 0.95, 0.52), arm=(0.3, 0.88),
                leg=(0.4, 0.74), sleeve=1.0, style="generic")
    base.update(kw)
    return base


HERO = _spec(name="Hero", style="beanie", shirt=(255, 138, 40), pants=(52, 78, 150), shoes=(240, 240, 245),
             hair=(86, 54, 36), hat=(38, 170, 175), accent=(255, 214, 70))
PIP = _spec(name="Pip", style="buns", s=0.62, head=(1.3, 1.16, 1.18), torso=(0.95, 0.82, 0.56),
            arm=(0.28, 0.7), leg=(0.36, 0.48), shirt=(150, 110, 235), pants=(255, 246, 235), shoes=(255, 120, 150),
            hair=(250, 196, 84), blush=True, accent=(255, 120, 150), sleeve=0.5, skirt=True)
TUCK = _spec(name="Tuck", style="spiky", s=0.98, shirt=(56, 176, 240), pants=(44, 58, 100), shoes=(255, 214, 70),
             hair=(238, 232, 220), skin=(236, 178, 140), accent=(255, 214, 70), cape=(255, 214, 70))
BRAX = _spec(name="Brax", style="flat", s=1.2, head=(1.02, 0.94, 0.96), torso=(1.32, 1.05, 0.64), arm=(0.42, 0.94),
             leg=(0.48, 0.72), shirt=(214, 48, 58), pants=(44, 44, 54), shoes=(245, 245, 245), hair=(34, 30, 36),
             skin=(176, 118, 86), accent=(250, 250, 250), sleeve=0.5)
DAD = _spec(name="Dad", style="side", s=1.36, head=(0.98, 0.94, 0.94), torso=(1.02, 1.1, 0.54), arm=(0.29, 1.0),
            leg=(0.4, 1.0), shirt=(74, 150, 96), pants=(118, 98, 80), shoes=(84, 58, 42), hair=(104, 66, 40),
            glasses=True, stache=(104, 66, 40), tie=(226, 66, 62))
MAYOR = _spec(name="Mayor Bigsby", style="bowler", s=1.3, head=(1.08, 0.96, 1.0), torso=(1.9, 1.4, 1.5),
              arm=(0.38, 0.95), leg=(0.5, 0.56), shirt=(120, 62, 180), pants=(58, 40, 96), shoes=(34, 30, 40),
              hair=(222, 222, 230), skin=(246, 190, 160), stache=(222, 222, 230), sash=(255, 200, 60), belly=True)
BABY = _spec(name="Baby", style="curl", s=0.42, head=(1.36, 1.22, 1.22), torso=(0.95, 0.8, 0.62), arm=(0.3, 0.6),
             leg=(0.36, 0.42), shirt=(255, 255, 255), pants=(255, 255, 255), shoes=(250, 200, 160), sleeve=0.0,
             blush=True)
NURSE = _spec(name="Nurse", style="nurse", s=1.3, head=(0.98, 0.94, 0.94), torso=(0.96, 1.05, 0.5), arm=(0.27, 0.95),
              leg=(0.38, 0.95), shirt=(70, 196, 182), pants=(70, 196, 182), shoes=(255, 255, 255),
              hair=(66, 42, 34), skin=(214, 156, 118), sleeve=0.5)

CROWD_COLORS = [(240, 96, 96), (96, 190, 120), (96, 146, 240), (250, 186, 76), (180, 110, 240), (250, 130, 190),
                (80, 200, 200), (232, 226, 110)]
CROWD_SKIN = [(250, 200, 160), (214, 156, 118), (176, 118, 86), (236, 178, 140), (130, 88, 66)]
CROWD_HAIR = [(40, 30, 30), (104, 66, 40), (240, 190, 80), (190, 80, 44), (90, 90, 100)]


def crowd_spec(i, adult=False):
    return _spec(name="Extra", style=("generic", "bob", "tuft")[i % 3], s=1.3 if adult else 0.95,
                 shirt=CROWD_COLORS[i % 8], pants=CROWD_COLORS[(i * 3 + 5) % 8], skin=CROWD_SKIN[i % 5],
                 hair=CROWD_HAIR[(i * 2) % 5])


# ------------------------------------------------------------------ posing
def character(sc, spec, pos=(0, 0, 0), yaw=0, face="smile", pose=None, live=False, layer=5, face_extra=None,
              shadow=True, shadow_y=None):
    """Build a posed character. Pose keys (degrees): lean, roll, y; al/ar=(pitch, roll) shoulder for the
    screen-left / screen-right arm when facing camera, el/er elbow bend; ll/lr hip pitch, kl/kr knee bend;
    head=(yaw, pitch, roll). Returns world-space anchors."""
    p = pose or {}
    s = spec["s"]
    hw, hh, hd = (v * s for v in spec["head"])
    tw, th, td = (v * s for v in spec["torso"])
    aw, al = (v * s for v in spec["arm"])
    lw, ll = (v * s for v in spec["leg"])
    skin, shirt, pants = spec["skin"], spec["shirt"], spec["pants"]

    def B(M, size, color, **kw):
        sc.box(M, size, color, layer=layer, live=live, **kw)

    def R(M, size, color, e=1.0, **kw):
        sc.blob(M, size, color, e=e, layer=layer, live=live, **kw)

    body = T(pos[0], pos[1] + p.get("y", 0.0), pos[2]) @ RY(yaw) @ RX(p.get("lean", 0)) @ RZ(p.get("roll", 0))
    if shadow:
        gy = pos[1] if shadow_y is None else shadow_y
        for k, a in ((1.0, 26), (0.78, 30), (0.55, 34)):
            r = max(tw, hw) * 0.72 * k
            pts = [(pos[0] + r * math.cos(t), gy + 0.012, pos[2] + r * 0.62 * math.sin(t))
                   for t in np.linspace(0, 6.283, 17)[:-1]]
            sc.quad(pts, (10, 20, 40, a), layer=1)

    # legs: thigh + shin with a knee
    hipx = tw * 0.2 if spec.get("belly") else tw / 2 - lw / 2 - 0.02 * s
    feet = {}
    for sx, key, kk in ((-1, "ll", "kl"), (1, "lr", "kr")):
        J = body @ T(sx * hipx, ll, 0) @ RX(-p.get(key, 0))
        knee = p.get(kk, 0)
        thigh = ll * 0.5
        shoe_h = min(0.2 * s, ll * 0.3)
        if abs(knee) < 1:
            B(J @ T(0, -(ll - shoe_h) / 2, 0), (lw, ll - shoe_h, lw), pants)
            K = J @ T(0, -thigh, 0)
        else:
            B(J @ T(0, -thigh / 2, 0), (lw, thigh, lw), pants)
            K = J @ T(0, -thigh, 0) @ RX(knee)
            B(K @ T(0, -(ll - thigh - shoe_h) / 2, 0), (lw * 0.99, ll - thigh - shoe_h, lw * 0.99), pants)
        B(K @ T(0, -(ll - thigh) + shoe_h / 2, 0.06 * s), (lw * 1.06, shoe_h, lw + 0.16 * s), spec["shoes"])
        feet["foot_l" if sx < 0 else "foot_r"] = xf(K, (0, -(ll - thigh), 0))

    # torso
    Mt = body @ T(0, ll + th / 2, 0)
    torso_decal = None
    st = spec["style"]
    if st == "beanie":
        def torso_decal(D):
            D.poly([(0.1, 0.7), (-0.36, -0.05), (-0.05, -0.05), (-0.18, -0.72), (0.38, 0.14), (0.05, 0.14), (0.3, 0.7)],
                   spec["accent"])
    elif spec.get("tie"):
        def torso_decal(D):
            D.poly([(-0.34, 1), (0, 0.5), (0.34, 1)], (250, 250, 250))
            D.poly([(-0.1, 0.72), (0.1, 0.72), (0.14, -0.2), (0, -0.4), (-0.14, -0.2)], spec["tie"])
            for sx in (-1, 1):
                D.line([(sx * 0.34, 1), (sx * 0.12, 0.2), (sx * 0.12, -1)], (56, 120, 76), 0.05)
    elif spec.get("sash"):
        def torso_decal(D):
            D.poly([(-0.86, 0.8), (-0.6, 0.92), (0.9, -0.5), (0.84, -0.8)], spec["sash"])
            D.ell(0.12, 0.1, 0.13, 0.15, (255, 240, 150), n=14)
            D.poly([(0.12, 0.2), (0.16, 0.12), (0.24, 0.1), (0.17, 0.06), (0.18, -0.02), (0.12, 0.03), (0.06, -0.02),
                    (0.07, 0.06), (0.0, 0.1), (0.08, 0.12)], (230, 150, 40))
            for v in (-0.05, -0.3, -0.55):
                D.ell(-0.4, v, 0.045, 0.05, (255, 225, 90), n=10)
    elif st == "flat":
        def torso_decal(D):
            D.rect(-1, 0.42, 1, 0.56, spec["accent"])
            D.text(0, -0.1, "7", spec["accent"], h=0.42)
    elif st == "spiky":
        def torso_decal(D):
            D.poly([(-0.46, 0.3), (0, -0.3), (0.46, 0.3), (0.28, 0.3), (0, -0.06), (-0.28, 0.3)], (255, 255, 255))
    elif st == "buns":
        def torso_decal(D):
            D.poly([(0, 0.55), (0.14, 0.2), (0.5, 0.18), (0.22, -0.04), (0.32, -0.4), (0, -0.18), (-0.32, -0.4),
                    (-0.22, -0.04), (-0.5, 0.18), (-0.14, 0.2)], (255, 226, 110))
    if spec.get("belly"):
        R(Mt @ T(0, -0.05 * s, 0.02 * s), (tw, th * 1.08, td), shirt, e=0.75, decal=torso_decal, n=16, m=10)
    else:
        B(Mt, (tw, th, td), shirt, decal=torso_decal)
        B(Mt @ T(0, th / 2 - 0.03 * s, 0), (tw * 0.5, 0.07 * s, td * 0.7), tuple(v * 0.8 for v in skin), bias=-0.01)
    if spec.get("skirt"):
        B(body @ T(0, ll + 0.08 * s, 0), (tw * 1.34, 0.36 * s, td * 1.5), shirt, bias=-0.02)
        B(body @ T(0, ll + 0.3 * s, 0), (tw * 1.05, 0.09 * s, td * 1.08), spec["accent"], bias=-0.03)
    if spec.get("cape"):
        B(Mt @ T(0, 0.3 * s, -td / 2 - 0.05 * s) @ RX(-p.get("cape", 8)) @ T(0, -th * 0.62, -0.02),
          (tw * 0.95, th * 1.25, 0.06 * s), spec["cape"])

    # arms: upper + forearm with an elbow
    hands = {}
    for sx, key, ek in ((-1, "al", "el"), (1, "ar", "er")):
        pitch, roll = p.get(key, (0, 6))
        J = body @ T(sx * (tw / 2 + aw / 2 - (0.12 * s if spec.get("belly") else 0)), ll + th - 0.08 * s, 0) \
            @ RZ(sx * roll) @ RX(-pitch)
        up = al * 0.5
        sl = spec["sleeve"]
        B(J @ T(0, -up / 2 + 0.08 * s, 0), (aw, up, aw), shirt if sl >= 0.4 else skin)
        E = J @ T(0, -up + 0.08 * s, 0) @ RX(-p.get(ek, 0))
        hand = al * 0.24
        if sl >= 0.9:
            B(E @ T(0, -(al - up - hand) / 2, 0), (aw * 0.99, al - up - hand, aw * 0.99), shirt)
            B(E @ T(0, -(al - up) + hand / 2, 0), (aw * 0.97, hand, aw * 0.97), skin)
        else:
            B(E @ T(0, -(al - up) / 2, 0), (aw * 0.97, al - up, aw * 0.97), skin)
        hands["hand_l" if sx < 0 else "hand_r"] = xf(E, (0, -(al - up), 0))
        hands["M_hand_l" if sx < 0 else "M_hand_r"] = E @ T(0, -(al - up), 0)

    # head: rounded
    hy, hp, hr = p.get("head", (0, 0, 0))
    Mh = body @ T(0, ll + th, 0) @ RY(hy) @ RX(hp) @ RZ(hr) @ T(0, hh / 2 - 0.02 * s, 0)
    R(Mh, (hw, hh, hd), skin, e=0.42, decal=face_decal(face, spec, face_extra) if face else None, bias=-0.02,
      n=18, m=10)
    top = _hair(sc, spec, Mh, hw, hh, hd, s, B, R)

    out = dict(hands)
    out.update(feet)
    out.update(head=xf(Mh, (0, 0, 0)), head_top=xf(Mh, (0, hh / 2 + top * s, 0)), Mh=Mh, Mt=Mt, body=body,
               height=ll + th + hh, face_pt=xf(Mh, (0, 0, hd / 2)))
    return out


def _hair(sc, spec, Mh, hw, hh, hd, s, B, R):
    """Hair and headwear. The big mass sits behind the head centre so painter-sorting keeps it off the face;
    only pieces above the brow line are biased in front. Returns extra height above the skull (in s units)."""
    st, hair = spec["style"], spec["hair"]
    dark = tuple(v * 0.82 for v in hair)

    def mass(h=0.95, y=0.1, z=-0.14, w=1.12, d=1.0, c=hair, e=0.6):
        R(Mh @ T(0, hh * y, hd * z), (hw * w, hh * h, hd * d), c, e=e, n=14, m=8)

    def cap(h=0.36, y=0.42, c=hair, w=1.1, e=0.55, z=-0.02):
        R(Mh @ T(0, hh * y, hd * z), (hw * w, hh * h, hd * w), c, e=e, bias=-0.3, n=14, m=6)

    def tuft(x, y, z, size, rz=0, c=hair, bias=-0.45, e=0.7):
        R(Mh @ T(hw * x, hh * y, hd * z) @ RZ(rz), tuple(v * s for v in size), c, e=e, bias=bias, n=8, m=5)

    if st == "beanie":
        mass(0.8, 0.02, -0.16, 1.1)
        for x, rz in ((-0.34, 24), (-0.1, 8), (0.16, -10), (0.38, -26)):
            tuft(x, 0.25, 0.47, (0.2, 0.26, 0.12), rz, bias=-0.4)
        R(Mh @ T(0, hh * 0.5, -0.02 * s), (hw * 1.1, hh * 0.62, hd * 1.1), spec["hat"], e=0.8, bias=-0.5, n=14, m=6)
        R(Mh @ T(0, hh * 0.35, 0), (hw * 1.16, hh * 0.2, hd * 1.16), tuple(v * 0.86 for v in spec["hat"]), e=0.35,
          bias=-0.55, n=14, m=4)
        R(Mh @ T(0, hh * 0.86, -0.02 * s), (0.3 * s, 0.3 * s, 0.3 * s), spec["accent"], bias=-0.7, n=8, m=6)
        return 0.5
    if st == "buns":
        mass(0.98, 0.06, -0.14, 1.14)
        cap(0.34, 0.42)
        tuft(-0.2, 0.3, 0.46, (0.5, 0.2, 0.14), 14)
        tuft(0.24, 0.3, 0.46, (0.4, 0.2, 0.14), -16)
        for sx in (-1, 1):
            R(Mh @ T(sx * hw * 0.6, hh * 0.48, -0.08 * s), (0.46 * s, 0.46 * s, 0.46 * s), hair, bias=-0.35, n=10, m=6)
            R(Mh @ T(sx * hw * 0.5, hh * 0.36, 0.0), (0.2 * s, 0.14 * s, 0.24 * s), spec["accent"], e=0.5, bias=-0.4,
              n=8, m=4)
        return 0.3
    if st == "spiky":
        mass(0.8, 0.12, -0.14, 1.1)
        cap(0.3, 0.44)
        for i, (x, z, rz, h) in enumerate(((-0.36, 0.1, 30, 0.4), (-0.12, 0.2, 10, 0.5), (0.14, 0.15, -12, 0.52),
                                           (0.38, 0.05, -34, 0.4), (0.0, -0.2, 4, 0.5))):
            R(Mh @ T(hw * x, hh * 0.62, hd * z) @ RZ(rz) @ RY(25 * i), (0.26 * s, h * s, 0.26 * s), hair, e=1.6,
              bias=-0.5, n=6, m=6)
        R(Mh @ T(0, hh * 0.3, 0), (hw * 1.13, 0.12 * s, hd * 1.13), (56, 56, 70), e=0.35, bias=-0.42, n=14, m=4)
        for sx in (-1, 1):
            R(Mh @ T(sx * 0.21 * s, hh * 0.31, hd / 2 + 0.03 * s), (0.34 * s, 0.24 * s, 0.14 * s), spec["accent"],
              e=0.5, bias=-0.7, n=10, m=4)
            R(Mh @ T(sx * 0.21 * s, hh * 0.31, hd / 2 + 0.08 * s), (0.22 * s, 0.14 * s, 0.06 * s), (190, 240, 255),
              e=0.5, bias=-0.75, n=8, m=4)
        return 0.5
    if st == "flat":
        mass(0.7, 0.12, -0.14, 1.08)
        R(Mh @ T(0, hh * 0.56, -0.02 * s), (hw * 1.06, hh * 0.42, hd * 1.04), hair, e=0.3, bias=-0.3, n=14, m=6)
        R(Mh @ T(0, hh * 0.3, 0), (hw * 1.12, 0.13 * s, hd * 1.12), spec["accent"], e=0.35, bias=-0.45, n=14, m=4)
        return 0.38
    if st == "side":
        mass(0.75, 0.1, -0.14, 1.08)
        cap(0.26, 0.45)
        R(Mh @ T(-0.14 * s, hh * 0.5, 0.12 * s) @ RZ(9), (hw * 0.82, 0.24 * s, hd * 0.9), hair, e=0.6, bias=-0.5,
          n=12, m=5)
        tuft(0.42, 0.44, 0.2, (0.26, 0.2, 0.5), -20, c=dark)
        return 0.2
    if st == "bowler":
        mass(0.7, 0.0, -0.16, 1.1)
        for sx in (-1, 1):
            tuft(sx * 0.5, -0.08, 0.2, (0.16, 0.5, 0.5), 0, bias=-0.1)
        hat = (64, 44, 110)
        R(Mh @ T(0, hh * 0.46, 0), (hw * 1.42, 0.1 * s, hd * 1.42), hat, e=0.9, bias=-0.4, n=16, m=4)
        R(Mh @ T(0, hh * 0.52, 0), (hw * 0.98, 0.14 * s, hd * 0.98), spec["sash"], e=0.5, bias=-0.5, n=14, m=4)
        R(Mh @ T(0, hh * 0.72, 0), (hw * 0.94, 0.56 * s, hd * 0.94), hat, e=0.85, bias=-0.6, n=14, m=7)
        return 0.6
    if st == "curl":
        tuft(0.0, 0.5, 0.1, (0.2, 0.26, 0.2), 20, bias=-0.4)
        return 0.15
    if st == "nurse":
        mass(0.98, 0.04, -0.14, 1.1)
        cap(0.26, 0.44)
        R(Mh @ T(0, hh * 0.66, -hd * 0.25), (0.4 * s, 0.4 * s, 0.4 * s), hair, bias=-0.2, n=8, m=6)
        B(Mh @ T(0, hh / 2 + 0.1 * s, 0.14 * s), (hw * 0.7, 0.26 * s, hd * 0.4), (255, 255, 255), bias=-0.55,
          decal=lambda D: (D.rect(-0.12, -0.6, 0.12, 0.6, (228, 54, 62)), D.rect(-0.4, -0.2, 0.4, 0.2, (228, 54, 62))))
        return 0.32
    if st == "bob":
        mass(1.1, -0.02, -0.12, 1.16)
        cap(0.3, 0.44)
        for sx in (-1, 1):
            tuft(sx * 0.52, -0.05, 0.12, (0.16, 0.7, 0.6), 0, bias=-0.1, e=0.5)
        return 0.14
    if st == "tuft":
        mass(0.75, 0.12, -0.14, 1.08)
        cap(0.28, 0.45)
        tuft(0.1, 0.62, 0.2, (0.36, 0.3, 0.3), -18)
        return 0.3
    mass(0.78, 0.1, -0.14, 1.1)
    cap(0.3, 0.44)
    return 0.14


def sit():
    """Seated pose: hips forward, knees bent back down."""
    return dict(ll=88, lr=88, kl=-88, kr=-88)
