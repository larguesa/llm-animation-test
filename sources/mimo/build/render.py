#!/usr/bin/env python3
"""
Motion graphics renderer — "AI-Native Delivery Pods" (T2S Tech), 30s @30fps 1920x1080.
Pure Pillow/numpy scene-graph renderer with temporal supersampling (motion blur).
Brand system extracted from the official T2S site CSS (frozen in ./input).
Usage:
  python3 build/render.py --frame 13.2 --out build/test/f132.png
  python3 build/render.py --full build/video.mp4
"""
import sys, os, math, argparse, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDIR = os.path.join(WORK, "input", "fonts")
BUILD = os.path.join(WORK, "build")
MONT = os.path.join(FDIR, "montserrat__Montserrat[wght].ttf")
RUB = os.path.join(FDIR, "rubik__Rubik[wght].ttf")

W, H = 1920, 1080
SS = 2                       # spatial supersample
FPS = 30
DUR = 30.0

# ---- T2S brand palette (from official stylesheet) ---------------------------
PAPER      = (246, 249, 251)
SURFACE    = (255, 255, 255)
SURF_BLUE  = (234, 247, 252)
INK        = (63, 63, 63)
INK_DEEP   = (34, 38, 43)
MUTED      = (101, 113, 124)
HAIRLINE   = (203, 214, 222)
CYAN       = (0, 180, 232)
BLUE       = (50, 100, 255)
BLUE_DEEP  = (30, 70, 189)
RED        = (223, 62, 86)
AMBER      = (229, 159, 36)
GREEN      = (34, 189, 81)
PURPLE     = (81, 33, 255)
WHITE_SOFT = (255, 255, 255)

# ------------------------------------------------------------------ fonts
_FC = {}
def F(kind, size, wght):
    key = (kind, size, wght)
    if key not in _FC:
        f = ImageFont.truetype(MONT if kind == "m" else RUB, int(round(size * SS)))
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
        _FC[key] = f
    return _FC[key]

def tw(font, s, tracking=0.0):
    return sum(font.getlength(ch) for ch in s) + tracking * SS * max(len(s) - 1, 0)

# ------------------------------------------------------------------ easing
def _c(x): return 0.0 if x < 0 else (1.0 if x > 1 else x)

def ez(x, kind="out3"):
    x = _c(x)
    if kind == "lin":   return x
    if kind == "out3":  return 1 - (1 - x) ** 3
    if kind == "out5":  return 1 - (1 - x) ** 5
    if kind == "outx":  return 1 if x >= 1 else 1 - 2 ** (-10 * x)
    if kind == "in3":   return x ** 3
    if kind == "in2":   return x * x
    if kind == "inout": return 3 * x * x - 2 * x * x * x
    if kind == "back":
        s = 1.35
        x -= 1
        return 1 + x * x * ((s + 1) * x + s)
    return x

def A(t, t0, d, kind="out3"):
    return ez((t - t0) / max(d, 1e-6), kind)

def M(v0, v1, p):
    return v0 + (v1 - v0) * p

def seg(t, t0, t1, v0, v1, kind="inout"):
    return M(v0, v1, ez((t - t0) / max(t1 - t0, 1e-6), kind))

# ------------------------------------------------------------------ canvas
class G:
    """drawing context over an RGBA image, coordinates in local design units"""
    def __init__(self, img):
        self.img = img
        self.d = ImageDraw.Draw(img)

    def rrect(self, x, y, w, h, r, fill=None, outline=None, ow=2):
        self.d.rounded_rectangle([x * SS, y * SS, (x + w) * SS - 1, (y + h) * SS - 1],
                                 radius=max(r * SS, 1), fill=fill,
                                 outline=outline, width=max(int(ow * SS), 1) if outline else 0)

    def circle(self, cx, cy, r, fill=None, outline=None, ow=2):
        self.d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS],
                       fill=fill, outline=outline, width=max(int(ow * SS), 1) if outline else 0)

    def line(self, x1, y1, x2, y2, color, w=2):
        self.d.line([x1 * SS, y1 * SS, x2 * SS, y2 * SS], fill=color,
                    width=max(int(w * SS), 1))

    def poly(self, pts, fill=None, outline=None, ow=2):
        p = [(x * SS, y * SS) for x, y in pts]
        self.d.polygon(p, fill=fill, outline=outline,
                       width=max(int(ow * SS), 1) if outline else 0)

    def dash(self, x1, y1, x2, y2, color, w=2, dash=10, gap=8):
        L = math.hypot(x2 - x1, y2 - y1)
        if L < 1: return
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        d = 0.0
        while d < L:
            e = min(d + dash, L)
            self.line(x1 + ux * d, y1 + uy * d, x1 + ux * e, y1 + uy * e, color, w)
            d = e + gap

    def text(self, x, y, s, font, color, tracking=0.0, anchor="lt", alpha=255):
        color = tuple(color)
        if len(color) == 3:
            color = color + (255,)
        wpx = tw(font, s, tracking)
        asc, desc = font.getmetrics()
        bb = font.getbbox("Hxg")
        hpx = bb[3] - bb[1] + int(font.size * 0.55)
        ox, oy = int(font.size * 0.3), int(font.size * 0.3)
        m = Image.new("L", (int(wpx) + 2 * ox, max(hpx + 2 * oy, asc + desc + 2 * oy)), 0)
        md = ImageDraw.Draw(m)
        cx = float(ox)
        for ch in s:
            md.text((cx, oy + asc), ch, font=font, fill=255, anchor="ls")
            cx += font.getlength(ch) + tracking * SS
        if alpha < 255:
            m = m.point(lambda v: v * alpha // 255)
        px, py = x * SS, y * SS
        if anchor[0] == "m": px -= (wpx / 2 + ox)
        elif anchor[0] == "r": px -= (wpx + ox)
        else: px -= ox
        if anchor[1] in "sm": py -= (hpx / 2 + oy)
        elif anchor[1] == "b": py -= (hpx + oy)
        else: py -= oy
        lay = Image.new("RGBA", m.size, color)
        lay.putalpha(m)
        self.img.paste(lay, (int(px), int(py)), m)

class Cv:
    def __init__(self):
        self.img = Image.new("RGBA", (W * SS, H * SS), PAPER + (255,))

    def sprite(self, w, h, drawfn, x, y, alpha=1.0, angle=0.0, scale=1.0):
        bw, bh = max(int(w * SS), 2), max(int(h * SS), 2)
        lay = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        g = G(lay)
        drawfn(g, w, h)
        if abs(scale - 1.0) > 1e-3:
            lay = lay.resize((max(int(bw * scale), 2), max(int(bh * scale), 2)),
                             Image.LANCZOS)
        sw, sh = lay.size
        if abs(angle) > 1e-3:
            lay = lay.rotate(angle, resample=Image.BICUBIC, expand=True)
        ox = x - (lay.size[0] - sw) / 2 / SS
        oy = y - (lay.size[1] - sh) / 2 / SS
        if alpha < 0.999:
            a = lay.split()[3].point(lambda v: int(v * max(alpha, 0.0)))
            lay.putalpha(a)
        self.img.paste(lay, (int(round(ox * SS)), int(round(oy * SS))), lay.split()[3])

def shadow(cv, x, y, w, h, r, blur=16, strength=34, dy=10):
    def fn(g, ww, hh):
        g.rrect(0, 0, ww, hh, r, fill=(30, 40, 55, strength))
    cv.sprite(w, h, fn, x, y + dy)
    # blur pass on the pasted area: cheap approximation via layered soft rects
    def fn2(g, ww, hh):
        g.rrect(-6, -6, ww + 12, hh + 12, r + 6, fill=(30, 40, 55, strength // 3))
    cv.sprite(w + 12, h + 12, fn2, x - 6, y + dy - 6)

def text(cv, x, y, s, kind, size, wght, color, alpha=255, tracking=0.0,
         anchor="lt", reveal=None, maxw=None):
    """direct mask text paste; reveal: (p, mode) with mode 'wipe' | 'rise'"""
    font = F(kind, size, wght)
    if maxw:
        while tw(font, s, tracking) > maxw * SS and size > 10:
            size *= 0.96
            font = F(kind, size, wght)
    wpx = tw(font, s, tracking)
    asc, desc = font.getmetrics()
    bb = font.getbbox("Hxg")
    hpx = bb[3] - bb[1] + int(font.size * 0.55)
    ox = oy = int(font.size * 0.3)
    m = Image.new("L", (int(wpx) + 2 * ox, max(hpx + 2 * oy, asc + desc + 2 * oy)), 0)
    md = ImageDraw.Draw(m)
    cx = float(ox)
    for ch in s:
        md.text((cx, oy + asc), ch, font=font, fill=255, anchor="ls")
        cx += font.getlength(ch) + tracking * SS
    dy = 0
    if reveal is not None:
        p, mode = reveal
        p = _c(p)
        if mode == "wipe":
            edge = ox + p * wpx
            md.rectangle([edge, 0, m.size[0], m.size[1]], fill=0)
        elif mode == "rise":
            dy = int((1 - p) * size * SS * 0.35)
            alpha = alpha * min(p * 2.2, 1.0)
        elif mode == "fade":
            alpha = alpha * p
    if alpha < 255:
        m = m.point(lambda v: int(v * max(alpha, 0) / 255))
    px, py = x * SS, y * SS
    if anchor[0] == "m": px -= (wpx / 2 + ox)
    elif anchor[0] == "r": px -= (wpx + ox)
    else: px -= ox
    if anchor[1] in "sm": py -= (hpx / 2 + oy)
    elif anchor[1] == "b": py -= (hpx + oy)
    else: py -= oy
    lay = Image.new("RGBA", m.size, tuple(color) + (255,))
    lay.putalpha(m)
    cv.img.paste(lay, (int(px), int(py + dy)), m)
    return wpx / SS

def text_w(s, kind, size, wght, tracking=0.0):
    return tw(F(kind, size, wght), s, tracking) / SS

# ------------------------------------------------------------------ glyphs
def gl_human(g, x, y, s, color, ow=3):
    g.circle(x, y - s * 0.18, s * 0.22, fill=color)
    g.d.arc([(x - s * 0.34) * SS, (y + s * 0.02) * SS, (x + s * 0.34) * SS, (y + s * 0.72) * SS],
            180, 360, fill=color, width=max(int(ow * SS), 1))

def gl_agent(g, x, y, s, color):
    r = s * 0.36
    g.poly([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=color)
    d = s * 0.11
    for k in (-1, 0, 1):
        g.circle(x + k * s * 0.17, y, d * 0.5, fill=(255, 255, 255, 255))

def gl_check(g, x, y, s, color, ow=3, p=1.0):
    if p <= 0: return
    x1, y1 = x - s * 0.28, y + s * 0.02
    x2, y2 = x - s * 0.05, y + s * 0.24
    x3, y3 = x + s * 0.32, y - s * 0.26
    p1 = min(p * 2, 1.0); p2 = max(p * 2 - 1, 0.0)
    if p1 > 0:
        g.line(x1, y1, M(x1, x2, p1), M(y1, y2, p1), color, ow)
    if p2 > 0:
        g.line(x2, y2, M(x2, x3, p2), M(y2, y3, p2), color, ow)

def gl_idea(g, x, y, s, color, p=1.0, ow=3.2):
    # explore ideas: branching nodes + spark
    g.circle(x, y + s * 0.26, s * 0.09, fill=color)
    ends = [(x - s * 0.3, y - s * 0.14), (x, y - s * 0.3), (x + s * 0.3, y - s * 0.14)]
    for i, (ex, ey) in enumerate(ends):
        q = _c((p - i * 0.18) / 0.5)
        if q > 0:
            g.line(x, y + s * 0.26, M(x, ex, q), M(y + s * 0.26, ey, q), color, ow)
        if q >= 1:
            g.circle(ex, ey, s * 0.075, fill=color)
    if p > 0.8:
        g.line(x + s * 0.3, y + s * 0.2, x + s * 0.3, y + s * 0.34, color, ow)
        g.line(x + s * 0.23, y + s * 0.27, x + s * 0.37, y + s * 0.27, color, ow)

def gl_build(g, x, y, s, color, p=1.0, ow=3.2):
    q1 = _c(p / 0.4); q2 = _c((p - 0.3) / 0.4); q3 = _c((p - 0.6) / 0.4)
    g.rrect(x - s * 0.3, y + s * 0.16, s * 0.6, s * 0.16, s * 0.03, fill=color)
    if q1 > 0:
        g.rrect(x - s * 0.3, y + s * 0.16 - s * 0.2 * q1, s * 0.6, s * 0.16, s * 0.03, fill=color)
    if q2 > 0:
        g.rrect(x - s * 0.3, y + s * 0.16 - s * 0.4 * q2, s * 0.6, s * 0.16, s * 0.03, fill=color)
    if q3 > 0:
        yy = M(y - s * 0.5, y - s * 0.34, q3)
        g.line(x + s * 0.42, yy + s * 0.16, x + s * 0.42, yy - s * 0.02, color, ow)
        g.line(x + s * 0.42, yy - s * 0.02, x + s * 0.35, yy + s * 0.05, color, ow)
        g.line(x + s * 0.42, yy - s * 0.02, x + s * 0.49, yy + s * 0.05, color, ow)

def gl_simplify(g, x, y, s, color, p=1.0, ow=3.2):
    q = ez(p, "inout")
    for k, yy in ((-1, y - s * 0.22), (0, y), (1, y + s * 0.22)):
        half = s * 0.32 * (1 - q * (1 if k else 0.55))
        yk = M(yy, y, q * (0 if k == 0 else 1))
        g.line(x - half, yk, x + half, yk, color, ow)
    if p > 0.85:
        g.line(x + s * 0.36, y - s * 0.1, x + s * 0.36, y + s * 0.1, color, ow)

def gl_grow(g, x, y, s, color, p=1.0, ow=3.2):
    hs = [0.18, 0.3, 0.44]
    for i, hh in enumerate(hs):
        q = _c((p - i * 0.2) / 0.5)
        if q <= 0: continue
        h = s * hh * q
        g.rrect(x - s * 0.3 + i * s * 0.21, y + s * 0.3 - h, s * 0.13, h, s * 0.02, fill=color)
    if p > 0.7:
        g.line(x - s * 0.05, y - s * 0.1, x + s * 0.3, y - s * 0.4, color, ow)
        g.line(x + s * 0.3, y - s * 0.4, x + s * 0.14, y - s * 0.38, color, ow)
        g.line(x + s * 0.3, y - s * 0.4, x + s * 0.28, y - s * 0.24, color, ow)

def gl_maintain(g, x, y, s, color, p=1.0, ow=3.2):
    q = _c(p / 0.6)
    pts = [(x, y - s * 0.36), (x + s * 0.28, y - s * 0.22), (x + s * 0.28, y + s * 0.05),
           (x, y + s * 0.34), (x - s * 0.28, y + s * 0.05), (x - s * 0.28, y - s * 0.22)]
    n = max(int(len(pts) * q + 0.99), 2)
    seq = [pts[i % len(pts)] for i in range(n)]
    if q >= 0.98:
        g.poly(pts, outline=color, ow=ow)
    else:
        for i in range(len(seq) - 1):
            g.line(seq[i][0], seq[i][1], seq[i + 1][0], seq[i + 1][1], color, ow)
    if p > 0.75:
        rr = s * 0.13
        g.d.arc([(x - rr) * SS, (y - rr) * SS, (x + rr) * SS, (y + rr) * SS],
                -60, 180, fill=color, width=max(int(ow * SS), 1))
        g.line(x + rr * 0.6, y - rr * 0.9, x + rr * 1.05, y - rr * 0.55, color, ow)
        g.line(x + rr * 0.6, y - rr * 0.9, x + rr * 1.0, y - rr * 1.1, color, ow)

def gl_wire(g, x, y, s, color, p=1.0, ow=3.0):
    g.rrect(x - s * 0.36, y - s * 0.3, s * 0.72, s * 0.6, s * 0.05, outline=color, ow=ow)
    g.line(x - s * 0.26, y - s * 0.14, x + s * 0.1, y - s * 0.14, color, ow)
    g.line(x - s * 0.26, y - s * 0.0, x + s * 0.26, y - s * 0.0, color, ow)
    g.rrect(x - s * 0.26, y + s * 0.08, s * 0.24, s * 0.14, s * 0.02, outline=color, ow=ow * 0.8)
    g.line(x + s * 0.06, y + s * 0.15, x + s * 0.26, y + s * 0.15, color, ow)

def gl_code(g, x, y, s, color, p=1.0, ow=3.0):
    g.line(x - s * 0.1, y - s * 0.26, x - s * 0.3, y, color, ow)
    g.line(x - s * 0.3, y, x - s * 0.1, y + s * 0.26, color, ow)
    g.line(x + s * 0.1, y - s * 0.26, x + s * 0.3, y, color, ow)
    g.line(x + s * 0.3, y, x + s * 0.1, y + s * 0.26, color, ow)
    g.line(x + s * 0.06, y - s * 0.28, x - s * 0.06, y + s * 0.28, color, ow)

def gl_test(g, x, y, s, color, p=1.0, ow=3.0):
    ys = [y - s * 0.2, y, y + s * 0.2]
    for i, yy in enumerate(ys):
        g.line(x - s * 0.32, yy, x + s * 0.32, yy, color, ow)
        gl_check(g, x - s * 0.32, yy, s * 0.34, color, ow=ow, p=_c(p * 1.4 - i * 0.25))

def gl_review(g, x, y, s, color, p=1.0, ow=3.0):
    r = s * 0.2
    g.circle(x - s * 0.06, y - s * 0.05, r, outline=color, ow=ow)
    g.line(x + s * 0.09, y + s * 0.1, x + s * 0.24, y + s * 0.26, color, ow)
    gl_check(g, x - s * 0.06, y - s * 0.05, s * 0.24, color, ow=ow, p=p)

def gl_dot3(g, x, y, s, color):
    for k in (-1, 0, 1):
        g.circle(x + k * s * 0.16, y, s * 0.05, fill=color)

# ------------------------------------------------------------------ story data
HUB = (960.0, 640.0)
RING_R = 225.0
CHIPS = [
    dict(label="Bug no checkout",     dot=RED,    scat=(440, 632, -6.5), grid=(430, 625), kind="human", ph=0.0),
    dict(label="Relatórios manuais",  dot=AMBER,  scat=(858, 588,  4.2), grid=(835, 625), kind="human", ph=1.3),
    dict(label="Dívida técnica",      dot=PURPLE, scat=(1288, 640, -3.2), grid=(1240, 625), kind="human", ph=2.1),
    dict(label="Migração pendente",   dot=BLUE,   scat=(1626, 596,  6.1), grid=(1645, 625), kind="agent", ph=0.7),
    dict(label="Fila de suporte",     dot=CYAN,   scat=(622, 862,  3.6), grid=(630, 808), kind="agent", ph=1.8),
    dict(label="Onboarding lento",    dot=GREEN,  scat=(1082, 876, -5.1), grid=(1035, 808), kind="agent", ph=2.6),
    dict(label="Ajustes de UI",       dot=AMBER,  scat=(1518, 860,  2.6), grid=(1440, 808), kind="agent", ph=0.4),
]
for i, c in enumerate(CHIPS):
    a = math.radians(-90 + 360 / 7 * (i + 0.5))
    c["ring"] = (HUB[0] + RING_R * math.cos(a), HUB[1] + RING_R * math.sin(a))
    c["ringang"] = math.degrees(a)

DEPS = [(0, 2), (1, 4), (2, 5), (3, 6), (1, 3)]

ROLES = [
    ("01", "Prototyper", "explorar ideias", gl_idea),
    ("02", "Builder", "construir", gl_build),
    ("03", "Sweeper", "simplificar", gl_simplify),
    ("04", "Grower", "evoluir", gl_grow),
    ("05", "Maintainer", "manter", gl_maintain),
]
CARD_W, CARD_H = 300.0, 430.0
CARD_X0 = 150.0
CARD_GAP = 30.0

ARTS = [
    ("Protótipo", "wireframe", gl_wire, 18.2),
    ("Incremento de software", "incremento", gl_code, 19.0),
    ("Teste", "teste", gl_test, 19.8),
    ("Revisão", "revisão", gl_review, 20.6),
]
EVID = [
    ("Protótipo demonstrável", 19.8),
    ("Incremento entregue", 20.6),
    ("Testes executados", 21.4),
    ("Revisão registrada", 22.2),
]
ART_TRAVEL = 1.6

# ------------------------------------------------------------------ scenes
def chip_state(i, t):
    """position/rot/scale of demand chip i across scenes 1-2"""
    c = CHIPS[i]
    driftx = math.sin(t * 0.9 + c["ph"]) * 3.5
    drifty = math.cos(t * 0.7 + c["ph"] * 1.7) * 3.0
    scx, scy, scr = c["scat"]
    t0 = 4.0 + i * 0.07
    p1 = A(t, t0, 0.7, "back")           # snap to grid
    gx, gy = c["grid"]
    t1 = 5.0 + i * 0.05
    p2 = A(t, t1, 1.1, "inout")          # grid -> ring
    rx, ry = c["ring"]
    t2 = 9.55 + i * 0.04
    p3 = A(t, t2, 0.85, "in3")           # ring -> expand out (exit)
    ex = HUB[0] + (rx - HUB[0]) * 1.85
    ey = HUB[1] + (ry - HUB[1]) * 1.85
    x = M(M(M(scx + driftx * (1 - p1), gx, p1), rx, p2), ex, p3)
    y = M(M(M(scy + drifty * (1 - p1), gy, p1), ry, p2), ey, p3)
    rot = M(scr + math.sin(t * 0.6 + c["ph"]) * 0.8 * (1 - p1), 0.0, p1)
    scale = M(M(1.0, 0.66, p2), 0.4, p3)
    alpha = 1.0 - A(t, t2 + 0.25, 0.55, "in2")
    return x, y, rot, scale, alpha

def draw_chip(cv, i, t):
    x, y, rot, scale, alpha = chip_state(i, t)
    if alpha <= 0.004:
        return
    c = CHIPS[i]
    morph = A(t, 5.6 + i * 0.05, 0.8, "inout")   # chip body -> token
    lab_a = (1.0 - A(t, 5.0 + i * 0.05, 0.5, "in2")) * alpha
    w, h = 320.0, 116.0

    def body(g, ww, hh):
        if morph < 0.98:
            g.rrect(0, 0, ww, hh, 5, fill=SURFACE + (int(255 * (1 - morph) * 1.0),),
                    outline=HAIRLINE + (int(255 * (1 - morph)),), ow=2)
            g.circle(38, 42, 7, fill=c["dot"])
            g.text(60, 32, c["label"], F("r", 26, 500), INK + (255,))
            g.line(60, 76, 60 + 150, 76, HAIRLINE + (255,), 2.5)
            g.line(60, 76, 60 + 90 * (0.4 + 0.6 * abs(math.sin(t * 0.8 + c["ph"]))), 76,
                   c["dot"] + (255,), 2.5)
        if morph > 0.02:
            if c["kind"] == "human":
                g.circle(ww / 2, hh / 2, 24, fill=SURFACE + (int(255 * morph),),
                         outline=INK_DEEP + (int(255 * morph),), ow=2.5)
                gl_human(g, ww / 2, hh / 2 + 3, 40, INK_DEEP + (int(255 * morph),), ow=3)
            else:
                gl_agent(g, ww / 2, hh / 2, 88, tuple(BLUE) + (int(255 * morph),))
    cv.sprite(w, h, body, x - w * scale / 2, y - h * scale / 2,
              alpha=alpha, angle=rot, scale=scale)

def draw_s1(cv, t):
    # dependency lines (dashed, tangled)
    lin_a = (1.0 - A(t, 4.6, 0.7, "in2")) * (0.25 + 0.75 * A(t, 0.3, 0.8))
    if lin_a > 0.01:
        for i, j in DEPS:
            x1, y1, *_ = chip_state(i, t)
            x2, y2, *_ = chip_state(j, t)
            L = math.hypot(x2 - x1, y2 - y1)
            if L < 2: continue
            ux, uy = (x2 - x1) / L, (y2 - y1) / L
            d = 0.0
            while d < L:
                e = min(d + 9, L)
                seg_len = abs(e - d)
                mx1, my1 = x1 + ux * d, y1 + uy * d
                mx2, my2 = x1 + ux * e, y1 + uy * e
                bw = seg_len + 6
                bh = abs(my2 - my1) + 6
                def segfn(g, ww, hh, mx1=mx1, my1=my1, mx2=mx2, my2=my2,
                          ox=min(mx1, mx2), oy=min(my1, my2)):
                    g.line(mx1 - ox + 3, my1 - oy + 3, mx2 - ox + 3, my2 - oy + 3,
                           HAIRLINE + (255,), 2.5)
                cv.sprite(max(bw, 7), max(bh, 7), segfn,
                          min(mx1, mx2) - 3, min(my1, my2) - 3, alpha=0.9 * lin_a)
                d = e + 8
    # chips
    for i in range(len(CHIPS)):
        draw_chip(cv, i, t)
    # headline: "Mais horas" / "não resolvem tudo." (cyan em, brand style)
    a1 = A(t, 0.30, 0.7, "out5")
    a2 = A(t, 0.62, 0.7, "out5")
    exit_p = A(t, 4.55, 0.5, "in2")
    y0 = 214 - 26 * (1 - a1) - 150 * exit_p
    y1 = 336 - 26 * (1 - a2) - 150 * exit_p
    al = 255 * (1 - exit_p)
    text(cv, 150, y0, "Mais horas", "m", 116, 700, INK_DEEP,
         alpha=al, tracking=-0.085 * 116, reveal=(a1, "rise"))
    text(cv, 150, y1, "não resolvem tudo.", "m", 116, 700, CYAN,
         alpha=al, tracking=-0.085 * 116, reveal=(a2, "rise"))
    # small rule under headline (brand hairline, sized to the copy)
    rp = A(t, 1.1, 0.8, "out5") * (1 - exit_p)
    if rp > 0:
        lw = text_w("não resolvem tudo.", "m", 116, 700, tracking=-0.085 * 116)

        def fn(g, ww, hh):
            g.line(0, 1.5, ww * rp, 1.5, HAIRLINE + (255,), 3)
        cv.sprite(lw, 4, fn, 150, 452, alpha=0.9)

def draw_s2(cv, t):
    if t < 5.2 or t > 10.7:
        pass
    # spokes hub->nodes
    sp_a = 1.0 - A(t, 9.5, 0.6, "in2")
    if sp_a > 0.01:
        for i, c in enumerate(CHIPS):
            x, y, *_ = chip_state(i, t)
            hx, hy = HUB
            hx += math.sin(t * 1.3 + c["ph"]) * 2
            p = A(t, 5.35 + i * 0.08, 0.8, "out3")
            if p <= 0: continue
            x2, y2 = M(hx, x, p), M(hy, y, p)
            L = math.hypot(x2 - hx, y2 - hy)
            if L < 2: continue
            ux, uy = (x2 - hx) / L, (y2 - hy) / L
            ex1, ey1 = hx + ux * 78, hy + uy * 78
            ex2, ey2 = x2 - ux * 44, y2 - uy * 44
            LL = math.hypot(ex2 - ex1, ey2 - ey1)
            if LL < 2: continue
            def fn(g, ww, hh, ex1=ex1, ey1=ey1, ex2=ex2, ey2=ey2,
                   ox=min(ex1, ex2), oy=min(ey1, ey2)):
                g.line(ex1 - ox + 3, ey1 - oy + 3, ex2 - ox + 3, ey2 - oy + 3,
                       (BLUE_DEEP if c["kind"] == "human" else CYAN) + (255,), 3)
            cv.sprite(abs(ex2 - ex1) + 6, abs(ey2 - ey1) + 6, fn,
                      min(ex1, ex2) - 3, min(ey1, ey2) - 3, alpha=0.75 * sp_a)
            # pulse dot traveling to node
            ph = ((t * 0.5 + c["ph"] * 0.13) % 1.0)
            if ph < 0.62:
                q = ph / 0.62
                px, py = M(ex1, ex2, q), M(ey1, ey2, q)
                def dfn(g, ww, hh):
                    g.circle(5, 5, 5, fill=CYAN + (255,))
                cv.sprite(10, 10, dfn, px - 5, py - 5, alpha=0.9 * sp_a)
    # hub
    hub_a = (1.0 - A(t, 9.5, 0.55, "in2")) * A(t, 5.1, 0.5, "back")
    if hub_a > 0.01:
        pulse = 1 + 0.014 * math.sin(t * 2 * math.pi / 2.0)
        s = 150 * pulse * (1 + 0.75 * A(t, 9.5, 0.6, "in3"))

        def hubfn(g, ww, hh):
            g.rrect(0, 0, ww, hh, 34, fill=BLUE + (255,))
            g.text(ww / 2, hh / 2 - 17, "POD", F("m", 34, 800), (255, 255, 255, 255),
                   tracking=2.0, anchor="mm")
        cv.sprite(s, s, hubfn, HUB[0] - s / 2, HUB[1] - s / 2, alpha=hub_a)
        # orbiting ring
        def ringfn(g, ww, hh):
            g.circle(ww / 2, hh / 2, ww / 2 - 2, outline=BLUE + (255,), ow=2)
        rs = s + 46
        cv.sprite(rs, rs, ringfn, HUB[0] - rs / 2, HUB[1] - rs / 2, alpha=0.35 * hub_a)
    # chips carry the ring nodes (drawn in s1)
    # title
    ex = A(t, 9.35, 0.4, "in2")
    tt_p = A(t, 6.25, 0.75, "out5")
    title = "AI-Native Delivery Pods"
    al = 255 * (1 - ex)
    y = 205 - 24 * (1 - tt_p) - 90 * ex
    if tt_p > 0:
        text(cv, 960, y, title, "m", 104, 700, INK_DEEP, alpha=al,
             tracking=-0.085 * 104, anchor="mm", maxw=1620, reveal=(tt_p, "rise"))
    # cyan accent divider
    up = A(t, 6.85, 0.7, "out5") * (1 - ex)
    if up > 0:
        def fn(g, ww, hh):
            g.rrect(0, 0, ww * up, hh, 3, fill=CYAN + (255,))
        cv.sprite(170, 7, fn, 960 - 85, y + 92, alpha=0.95)
    # support text
    st_p = A(t, 7.0, 0.7, "out5") * (1 - ex)
    if st_p > 0:
        text(cv, 960, 352 - 16 * (1 - st_p), "Uma equipe moldada pelo resultado.",
             "r", 44, 500, MUTED, alpha=255 * st_p, anchor="mm",
             reveal=(st_p, "rise"))
    # legend
    lp1 = A(t, 8.0, 0.5, "out3") * (1 - ex)
    lp2 = A(t, 8.4, 0.5, "out3") * (1 - ex)
    if lp1 > 0:
        def fn(g, ww, hh):
            g.circle(18, 18, 17, fill=SURFACE + (255,), outline=INK_DEEP + (255,), ow=2)
            gl_human(g, 18, 18, 30, INK_DEEP + (255,), ow=2.5)
        cv.sprite(36, 36, fn, 583, 938, alpha=lp1)
        text(cv, 631, 938 + 18, "Especialistas", "r", 31, 500, INK,
             alpha=255 * lp1, anchor="lm", reveal=(lp1, "rise"))
    if lp2 > 0:
        def fn(g, ww, hh):
            gl_agent(g, 24, 24, 44, BLUE + (255,))
        cv.sprite(48, 48, fn, 897, 932, alpha=lp2)
        text(cv, 953, 938 + 18, "Agentes supervisionados", "r", 31, 500, INK,
             alpha=255 * lp2, anchor="lm", reveal=(lp2, "rise"))

def band_rect(t):
    """blue band geometry: grows 9.8-10.4, morphs to strip 16.7-17.5, collapses to spine 17.5-18.1"""
    if t < 9.8:
        return None
    g = A(t, 9.8, 0.6, "out5")
    if t < 16.7:
        w = M(560, 2100, g); h = M(320, 1240, g)
        return (960 - w / 2, 540 - h / 2, w, h, 26)
    p1 = A(t, 16.7, 0.8, "inout")   # to strip
    p2 = A(t, 17.5, 0.6, "inout")   # strip -> spine line
    w = M(M(2100, 2100, p1), 1500 * 2, p2)
    h = M(M(1240, 260, p1), 6, p2)
    y = M(M(540 - 1240 / 2, 440, p1), 560, p2)
    x = 960 - min(w, 2200) / 2
    r = M(M(26, 10, p1), 3, p2)
    return (x, y, min(w, 2200), h, r)

def draw_s3(cv, t):
    band = band_rect(t)
    if band:
        x, y, w, h, r = band
        band_a = 1.0 - A(t, 18.1, 0.5, "in2")

        def fn(g, ww, hh):
            g.rrect(0, 0, ww, hh, r, fill=BLUE + (255,))
        if band_a > 0.01:
            cv.sprite(w, h, fn, x, y, alpha=band_a)
        # subtle grid on band
        if h > 400 and band_a > 0.5:
            def gridfn(g, ww, hh):
                for gx in range(80, int(ww), 120):
                    g.line(gx, 0, gx, hh, (255, 255, 255, 255), 1)
                for gy in range(80, int(hh), 120):
                    g.line(0, gy, ww, gy, (255, 255, 255, 255), 1)
            cv.sprite(w, h, gridfn, x, y, alpha=0.05 * band_a)
    if t < 10.1:
        return
    ex = A(t, 16.5, 0.7, "in2")      # exit progress for card system
    # main text
    mt = A(t, 10.3, 0.7, "out5")
    exm = A(t, 16.3, 0.5, "in2")
    if mt > 0:
        text(cv, 960, 168 - 18 * (1 - mt) - 80 * exm,
             "Especialistas + agentes supervisionados", "m", 62, 700,
             (255, 255, 255), alpha=255 * (1 - exm), tracking=-0.055 * 62,
             anchor="mm", maxw=1560, reveal=(mt, "rise"))
    # five role cards
    for i, (idx, name, act, icon) in enumerate(ROLES):
        t0 = 10.45 + i * 0.38
        p = A(t, t0, 0.6, "back")
        ip = A(t, t0 + 0.25, 0.75, "out3")
        if p <= 0:
            continue
        cx = CARD_X0 + i * (CARD_W + CARD_GAP) + CARD_W / 2
        x = M(960, cx, p) - CARD_W / 2 * M(0.35, 1, p)
        y = M(500, 330, p)
        sc = M(0.5, 1, p)
        al = (1 - ex) * min(p * 1.8, 1)

        def cardfn(g, ww, hh, i=i, idx=idx, name=name, act=act, icon=icon, ip=ip):
            g.rrect(0, 0, ww, hh, 6, fill=(255, 255, 255, 36),
                    outline=(255, 255, 255, 97), ow=2)
            g.text(24, 22, idx, F("m", 22, 800), (255, 255, 255, 150), tracking=2.2)
            icon(g, ww / 2, 150, 128, (255, 255, 255, 255), p=ip)
            g.text(ww / 2, 240, name, F("m", 38, 700), (255, 255, 255, 255),
                   tracking=-0.05 * 38, anchor="mt")
            g.text(ww / 2, 306, act, F("r", 27, 400), (255, 255, 255, 205), anchor="mt")
            g.line(24, hh - 46, 24 + (ww - 48) * ip, hh - 46, (255, 255, 255, 130), 2)
        cv.sprite(CARD_W, CARD_H, cardfn, x, y, alpha=al, scale=sc)
    # checkpoint spine + pills
    sp = A(t, 12.0, 0.6, "out5")
    exs = A(t, 16.4, 0.5, "in2")
    if sp > 0 and exs < 1:
        def fn(g, ww, hh):
            g.line(0, 2, ww * sp, 2, (255, 255, 255, 255), 3)
        cv.sprite(1420, 5, fn, 300, 838, alpha=0.5 * (1 - exs))
    for k, tt in enumerate([12.4, 12.9, 13.4, 13.9]):
        p = A(t, tt, 0.45, "back")
        if p <= 0 or exs >= 1:
            continue
        px = 465 + k * 330
        al = (1 - exs) * min(p * 1.6, 1)

        def pillfn(g, ww, hh):
            g.rrect(0, 0, ww, hh, 23, fill=(255, 255, 255, 255))
            gl_check(g, 28, hh / 2, 26, BLUE + (255,), ow=3)
            g.text(54, hh / 2, "Checkpoint humano", F("m", 21, 700), BLUE + (255,),
                   tracking=0.2, anchor="lm")
        cv.sprite(286, 46, pillfn, px - 143, 816, alpha=al)

def draw_s4(cv, t):
    ex = A(t, 23.2, 0.7, "in2")
    if ex >= 1.0 and t > 23.9:
        return
    cxm, cym = 960.0, 540.0
    def conv(x, y, scale=1.0):
        return (M(x, cxm, ex * 0.9), M(y, cym, ex * 0.9), scale * M(1, 0.55, ex))
    # headline
    h1 = A(t, 17.45, 0.7, "out5")
    h2 = A(t, 17.85, 0.7, "out5")
    if h1 > 0:
        x, y, sc = conv(150, 150)
        text(cv, x, y, "Progresso visível.", "m", 68 * sc, 700, INK_DEEP,
             alpha=255 * (1 - ex), tracking=-0.06 * 68, reveal=(h1, "rise"))
    if h2 > 0:
        x, y, sc = conv(150, 232)
        text(cv, x, y, "Responsabilidade clara.", "m", 68 * sc, 700, CYAN,
             alpha=255 * (1 - ex), tracking=-0.06 * 68, reveal=(h2, "rise"))
    # stage chips: Contexto -> Entrega -> Qualidade
    stages = ["Contexto", "Entrega", "Qualidade"]
    sx = [560, 960, 1360]
    for i, s in enumerate(stages):
        p = A(t, 18.0 + i * 0.22, 0.5, "back")
        if p <= 0: continue
        x, y, sc = conv(sx[i], 372)
        al = (1 - ex) * min(p * 1.6, 1)

        def fn(g, ww, hh, s=s):
            g.rrect(0, 0, ww, hh, 4, fill=SURF_BLUE + (255,), outline=HAIRLINE + (255,), ow=2)
            g.text(ww / 2, hh / 2, s, F("m", 44, 700), INK_DEEP + (255,),
                   tracking=-0.04 * 44, anchor="mm")
        w, h = 280 * sc, 92 * sc
        cv.sprite(280, 92, fn, x - w / 2, y - h / 2, alpha=al, scale=sc)
        if i < 2:
            ap = A(t, 18.55 + i * 0.22, 0.4, "out3")
            ax = M(sx[i] + 150, sx[i + 2] - 150 if False else sx[i] + 250, 1)
            gx, gy, gsc = conv(sx[i] + 200, 372)
            def arow(g, ww, hh, ap=ap):
                g.line(2, hh / 2, ww - 10, hh / 2, CYAN + (255,), 4)
                g.line(ww - 10, hh / 2, ww - 22, hh / 2 - 9, CYAN + (255,), 4)
                g.line(ww - 10, hh / 2, ww - 22, hh / 2 + 9, CYAN + (255,), 4)
            cv.sprite(100, 24, arow, gx - 50 * gsc, gy - 12, alpha=al * ap, scale=gsc)
    # flow spine (continues from the collapsed band)
    sp = A(t, 17.7, 0.7, "out5")
    if sp > 0:
        x, y, sc = conv(260, 560)

        def fn(g, ww, hh):
            g.line(ww / 2 - ww / 2 * sp, 3, ww / 2 + ww / 2 * sp, 3, BLUE + (255,), 5)
        cv.sprite(1400, 8, fn, x, y, alpha=(1 - ex) * 0.9)
        for i in range(3):
            tx = sx[i]
            gx, gy, gsc = conv(tx, 560)

            def tfn(g, ww, hh):
                g.line(ww / 2, 0, ww / 2, hh, BLUE_DEEP + (255,), 3)
            cv.sprite(20, 34, tfn, gx - 10, gy - 17, alpha=(1 - ex) * A(t, 18.3, 0.4) * 0.8)
            # faint guide linking stage chip to spine
            def gfn(g, ww, hh):
                g.dash(1, 0, 1, hh, HAIRLINE + (255,), 2, dash=8, gap=8)
            cv.sprite(4, 130, gfn, gx - 2, 424, alpha=(1 - ex) * A(t, 18.6, 0.5) * 0.9)
    # artifacts travelling
    for k, (label, sub, icon, t0) in enumerate(ARTS):
        p = A(t, t0, ART_TRAVEL, "inout")
        if p <= 0 or ex >= 1: continue
        ax = M(280, 1560, p)
        ay = 560 + math.sin(p * math.pi) * -14
        done = A(t, t0 + ART_TRAVEL, 0.4, "out3")
        al = (1 - ex) * (1 - A(t, t0 + ART_TRAVEL + 0.25, 0.4, "in2"))
        if al <= 0.01: continue
        bump = 1 + 0.05 * max(0, math.sin(min(p, 1) * math.pi * 3)) ** 8
        gx, gy, gsc = conv(ax, ay)
        asc = gsc * bump

        def fn(g, ww, hh, label=label, icon=icon, done=done, t0=t0):
            g.rrect(3, 6, ww - 6, hh - 6, 6, fill=(30, 40, 55, 30))
            g.rrect(0, 0, ww, hh, 6, fill=SURFACE + (255,), outline=HAIRLINE + (255,), ow=2)
            icon(g, 54, hh / 2, 62, CYAN + (255,), p=1.0)
            ls = 27
            while ls > 15 and text_w(label, "m", ls, 700, tracking=-0.03 * ls) > 268:
                ls -= 1
            g.text(96, hh / 2, label, F("m", ls, 700),
                   INK_DEEP + (255,), tracking=-0.03 * ls, anchor="lm")
            if done > 0:
                g.circle(ww - 34, 34, 17, fill=GREEN + (255,))
                gl_check(g, ww - 34, 34, 24, (255, 255, 255, 255), ow=3)
        cv.sprite(380, 132, fn, gx - 380 * asc / 2, gy - 132 * asc / 2,
                  alpha=al, scale=asc)
    # evidence panel
    if t > 19.0:
        ep = A(t, 19.1, 0.5, "out3")
        x, y, sc = conv(150, 700)
        text(cv, x, y, "Evidências", "m", 24 * sc, 800, BLUE,
             alpha=255 * (1 - ex) * ep, tracking=0.16 * 24, reveal=(ep, "wipe"))
    for k, (label, tt) in enumerate(EVID):
        p = A(t, tt, 0.5, "back")
        if p <= 0 or ex >= 1: continue
        x, y, sc = conv(150 + k * 420, 740)
        al = (1 - ex) * min(p * 1.5, 1)
        w, h = 380 * sc, 96 * sc

        def fn(g, ww, hh, label=label):
            g.rrect(0, 0, ww, hh, 4, fill=SURFACE + (255,), outline=HAIRLINE + (255,), ow=2)
            g.circle(38, hh / 2, 17, fill=GREEN + (255,))
            gl_check(g, 38, hh / 2, 23, (255, 255, 255, 255), ow=3)
            g.text(72, hh / 2, label, F("r", 25, 500), INK + (255,), anchor="lm")
        cv.sprite(380, 96, fn, x, y - 48 * sc, alpha=al, scale=sc)

def draw_s5(cv, t):
    if t < 23.85:
        return
    # ink-deep stage grows from center (shape continuity with converging elements)
    g = A(t, 23.9, 0.8, "out5")
    if g > 0:
        w = M(420, 2380, g); h = M(300, 1420, g)
        r = M(30, 0, min(g * 1.4, 1))

        def fn(gg, ww, hh):
            gg.rrect(0, 0, ww, hh, r, fill=INK_DEEP + (255,))
        cv.sprite(w, h, fn, 960 - w / 2, 540 - h / 2)
        if g > 0.6:
            def gridfn(gg, ww, hh):
                for gx in range(120, int(ww), 140):
                    gg.line(gx, 0, gx, hh, (255, 255, 255, 255), 1)
                for gy in range(120, int(hh), 140):
                    gg.line(0, gy, ww, gy, (255, 255, 255, 255), 1)
            cv.sprite(w, h, gridfn, 960 - w / 2, 540 - h / 2, alpha=0.04 * g)
    # logo (official, white-wordmark variant for dark stage)
    lp = A(t, 24.85, 0.6, "back")
    if lp > 0:
        logo = LOGO_DARKBG
        lw = 520 * M(0.94, 1.0, lp)
        lh = lw * logo.size[1] / logo.size[0]
        al = min(lp * 1.7, 1.0)
        lay = logo.resize((int(lw * SS), int(lh * SS)), Image.LANCZOS)
        if al < 1:
            a = lay.split()[3].point(lambda v: int(v * al))
            lay.putalpha(a)
        cv.img.paste(lay, (int((960 - lw / 2) * SS), int((368 - lh / 2) * SS)), lay.split()[3])
    # title
    tp = A(t, 25.55, 0.7, "out5")
    if tp > 0:
        text(cv, 960, 560 - 14 * (1 - tp), "AI-Native Delivery Pods", "m", 86, 700,
             (255, 255, 255), alpha=255 * min(tp * 1.8, 1), tracking=-0.085 * 86,
             anchor="mm", maxw=1500, reveal=(tp, "rise"))
    # CTA pill
    cp = A(t, 26.25, 0.55, "back")
    if cp > 0:
        label = "Converse com um engenheiro."
        bw, bh = 620, 88

        def fn(g, ww, hh):
            g.rrect(0, 0, ww, hh, 3, fill=BLUE + (255,))
            g.text(ww / 2, hh / 2, label, F("m", 33, 700), (255, 255, 255, 255),
                   tracking=0.02 * 33, anchor="mm")
        cv.sprite(bw, bh, fn, 960 - bw / 2, 730 - bh / 2, alpha=min(cp * 1.6, 1))
    # url
    up = A(t, 26.5, 0.5, "out5")
    if up > 0:
        text(cv, 960, 830, "t2stech.com", "r", 36, 500, HAIRLINE,
             alpha=255 * min(up * 1.8, 1), anchor="mm", reveal=(up, "rise"))

# ------------------------------------------------------------------ frame
DOTS = [(x, y) for y in range(80, H, 96) for x in range(72, W, 96)]
_VIG = None
def vignette():
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        a = np.clip((d - 0.75) / 0.8, 0, 1) * 46
        _VIG = a.astype(np.uint8)
    return _VIG

def draw_frame(t):
    cv = Cv()
    # paper base + dot grid
    def bgfn(g, ww, hh):
        g.d.rectangle([0, 0, ww * SS, hh * SS], fill=PAPER + (255,))
    cv.sprite(W, H, bgfn, 0, 0)
    par = (t * 6) % 96
    def dotfn(g, ww, hh):
        for x, y in DOTS:
            g.circle(x, y + par * 0.08, 2.4, fill=(214, 225, 233, 255))
    cv.sprite(W, H + 10, dotfn, 0, -5)

    if t < 5.3:
        draw_s1(cv, t)
    else:
        draw_s1(cv, t)   # chips persist into scene 2 as ring nodes
    if t >= 5.0:
        draw_s2(cv, t)
    if t >= 9.7:
        draw_s3(cv, t)
    if t >= 16.9:
        draw_s4(cv, t)
    if t >= 23.8:
        draw_s5(cv, t)

    img = cv.img.convert("RGB").resize((W, H), Image.LANCZOS)
    # vignette
    v = vignette()
    arr = np.asarray(img).astype(np.uint8)
    arr = (arr.astype(np.uint16) * (255 - v)[..., None] // 255).astype(np.uint8)
    return Image.fromarray(arr)

def frame_rgb(t, samples):
    acc = None
    offs = [0.0] if samples == 1 else [-0.09 / FPS, 0.09 / FPS]
    if samples == 3:
        offs = [-0.13 / FPS, 0.0, 0.13 / FPS]
    for o in offs:
        im = np.asarray(draw_frame(min(max(t + o, 0.0), DUR - 0.001))).astype(np.float32)
        acc = im if acc is None else acc + im
    return Image.fromarray((acc / len(offs)).astype(np.uint8))

# ------------------------------------------------------------------ main
LOGO_DARKBG = None
def load_logos():
    global LOGO_DARKBG, LOGO_LIGHTBG
    LOGO_DARKBG = Image.open(os.path.join(BUILD, "logo_on_dark.png")).convert("RGBA")
    LOGO_LIGHTBG = Image.open(os.path.join(BUILD, "logo_on_light.png")).convert("RGBA")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", type=str, default=None, help="comma-separated times")
    ap.add_argument("--out", type=str, default="build/test")
    ap.add_argument("--full", type=str, default=None)
    args = ap.parse_args()
    load_logos()
    if args.frame:
        os.makedirs(args.out, exist_ok=True)
        for ts in args.frame.split(","):
            t = float(ts)
            im = frame_rgb(t, 2 if t < 27.1 else 1)
            p = os.path.join(args.out, f"f{t:06.2f}.png")
            im.save(p)
            print("wrote", p)
        return
    if args.full:
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "17",
               "-pix_fmt", "yuv420p", args.full]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n = int(DUR * FPS)
        for i in range(n):
            t = i / FPS
            im = frame_rgb(t, 1 if t >= 27.1 else 2)
            proc.stdin.write(im.tobytes())
            if i % 30 == 0:
                print(f"frame {i}/{n}", flush=True)
        proc.stdin.close()
        proc.wait()
        print("done", args.full)

if __name__ == "__main__":
    main()
