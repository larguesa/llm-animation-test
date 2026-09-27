#!/usr/bin/env python3
"""T2S AI-Native Delivery Pods — 30 s motion graphics renderer (Pillow + numpy).

Deterministic, single-threaded. Renders 1920x1080 @ 30 fps.
  python3 src_render.py --preview 2 4.5 8.5 ...   -> work/preview/tXXXX.png
  python3 src_render.py --render                  -> work/video.mp4 (no audio)
Audio is produced by src_audio.py and muxed with ffmpeg afterwards.
"""
import os
import math
import subprocess
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FPS = 30
DUR = 30.0
NFRAMES = int(FPS * DUR)

INK = (34, 38, 43)
PAPER = (246, 249, 251)
MUTED = (150, 160, 170)
MUTED_D = (101, 113, 124)
HAIR = (203, 214, 222)
CYAN = (0, 180, 232)
CYAN_L = (114, 223, 255)
BLUE = (50, 100, 255)
BLUE_DEEP = (30, 70, 189)
GREEN = (34, 189, 81)
AMBER = (229, 159, 36)
RED = (223, 62, 86)
PURPLE = (81, 33, 255)
CARD_BG = (43, 49, 56)
WHITE = (255, 255, 255)

MONTS = "input/fonts/montserrat__Montserrat[wght].ttf"
RUBIK = "input/fonts/rubik__Rubik[wght].ttf"

# ---------------- easings ----------------
def clamp01(x):
    return 0.0 if x <= 0 else 1.0 if x >= 1 else x

def seg(t, t0, t1):
    return clamp01((t - t0) / max(1e-6, t1 - t0))

def lerp(a, b, t):
    return a + (b - a) * t

def ease_out_cubic(p):
    p = clamp01(p)
    return 1 - (1 - p) ** 3

def ease_in_cubic(p):
    p = clamp01(p)
    return p ** 3

def ease_in_out(p):
    p = clamp01(p)
    return p * p * (3 - 2 * p)

def ease_out_quart(p):
    p = clamp01(p)
    return 1 - (1 - p) ** 4

def ease_out_back(p, s=1.5):
    p = clamp01(p)
    c = s + 1
    return 1 + c * (p - 1) ** 3 + s * (p - 1) ** 2

def pulse(t, t0, dur=0.5):
    """0->1->0 bump."""
    p = seg(t, t0, t0 + dur)
    return math.sin(p * math.pi)

def blink(t, f=2.0):
    return 0.5 + 0.5 * math.sin(2 * math.pi * f * t)

# ---------------- fonts / text ----------------
_font_cache = {}

def font(family_path, size, weight):
    key = (family_path, size, weight)
    f = _font_cache.get(key)
    if f is None:
        f = ImageFont.truetype(family_path, size)
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
        _font_cache[key] = f
    return f

def text_img(s, path, size, weight, fill, tracking=0, pad=8):
    f = font(path, size, weight)
    widths = []
    for ch in s:
        b = f.getbbox(ch)
        widths.append(b[2] - b[0] if b else 0)
    adv = []
    for i, ch in enumerate(s):
        try:
            adv.append(int(f.getlength(ch)))
        except Exception:
            adv.append(widths[i])
    asc, desc = f.getmetrics()
    tw = sum(adv) + tracking * max(0, len(s) - 1)
    th = asc + desc
    img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = pad
    for i, ch in enumerate(s):
        d.text((x, pad), ch, font=f, fill=fill)
        x += adv[i] + tracking
    return img

def fit_size(s, path, weight, start, max_w, tracking=0):
    size = start
    while size > 12:
        f = font(path, size, weight)
        try:
            w = sum(int(f.getlength(ch)) for ch in s) + tracking * max(0, len(s) - 1)
        except Exception:
            b = f.getbbox(s)
            w = b[2] - b[0]
        if w <= max_w:
            return size
        size -= 2
    return size

# ---------------- compositing helpers ----------------
def paste_center(base, img, cx, cy, alpha=1.0, scale=1.0):
    if img is None or alpha <= 0.001:
        return
    w, h = img.size
    if abs(scale - 1.0) > 0.001:
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        img = img.resize((nw, nh), Image.BICUBIC)
        w, h = nw, nh
    if alpha < 0.999:
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        img = img.copy()
        img.putalpha(a)
    base.alpha_composite(img, (int(round(cx - w / 2)), int(round(cy - h / 2))))

def paste_topleft(base, img, x, y, alpha=1.0):
    if img is None or alpha <= 0.001:
        return
    if alpha < 0.999:
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        img = img.copy()
        img.putalpha(a)
    base.alpha_composite(img, (int(round(x)), int(round(y))))

def wipe_mask(w, h, prog, direction="left"):
    """Reveal mask: prog 0..1. direction = edge where reveal starts."""
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    p = clamp01(prog)
    if direction == "left":
        d.rectangle([0, 0, w * p, h], fill=255)
    elif direction == "right":
        d.rectangle([w * (1 - p), 0, w, h], fill=255)
    elif direction == "up":
        d.rectangle([0, h * (1 - p), w, h], fill=255)
    elif direction == "center":
        d.rectangle([w * (1 - p) / 2, 0, w * (1 + p) / 2, h], fill=255)
    return m

def paste_wipe(base, img, cx, cy, prog, direction="left", alpha=1.0, feather=0):
    if img is None or prog <= 0.001 or alpha <= 0.001:
        return
    w, h = img.size
    m = wipe_mask(w, h, prog, direction)
    if feather > 0:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    if alpha < 0.999:
        m = m.point(lambda v: int(v * alpha))
    c = img.copy()
    a = c.getchannel("A")
    # multiply alpha by wipe mask
    import PIL.ImageChops as Chops
    c.putalpha(Chops.multiply(a, m))
    base.alpha_composite(c, (int(round(cx - w / 2)), int(round(cy - h / 2))))

# ---------------- vector helpers ----------------
def rounded_rect(img, box, radius, fill=None, outline=None, width=1):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    return img

def card_base(w, h, radius=22, fill=CARD_BG + (238,), border=(255, 255, 255, 40),
              accent=None, shadow=True):
    pad = 30
    img = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ds = ImageDraw.Draw(sh)
        ds.rounded_rectangle([pad, pad + 12, pad + w, pad + h + 12], radius=radius, fill=(0, 0, 0, 130))
        sh = sh.filter(ImageFilter.GaussianBlur(16))
        img.alpha_composite(sh)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([pad, pad, pad + w, pad + h], radius=radius, fill=fill,
                        outline=border, width=2)
    # top highlight
    d.line([pad + radius, pad + 1, pad + w - radius, pad + 1], fill=(255, 255, 255, 46), width=2)
    if accent:
        d.rounded_rectangle([pad, pad, pad + 10, pad + h], radius=5, fill=accent)
    # content origin = (pad, pad); caller draws at +pad. Return img and pad.
    return img, pad

def bezier(p0, p1, p2, n=48):
    pts = []
    for i in range(n + 1):
        u = i / n
        x = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u ** 2 * p2[0]
        y = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u ** 2 * p2[1]
        pts.append((x, y))
    return pts

def draw_dashed(draw, pts, dash=10, gap=8, phase=0.0, fill=(255, 255, 255, 120), width=2):
    # walk polyline
    segs = []
    for a, b in zip(pts[:-1], pts[1:]):
        segs.append((a, b, math.hypot(b[0] - a[0], b[1] - a[1])))
    total = sum(s[2] for s in segs)
    if total <= 0:
        return
    pos = -phase
    cur = 0.0
    si = 0
    acc = 0.0
    # precompute cumulative
    out = []
    d = pos
    while d < total:
        d0 = max(d, 0)
        d1 = min(d + dash, total)
        if d1 > d0:
            out.append((d0, d1))
        d += dash + gap
    # map arc distance to points
    cum = [0.0]
    for _, _, L in segs:
        cum.append(cum[-1] + L)

    def point_at(dd):
        for i in range(len(segs)):
            if dd <= cum[i + 1]:
                a, b, L = segs[i]
                u = 0 if L == 0 else (dd - cum[i]) / L
                return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
        return segs[-1][1]
    for d0, d1 in out:
        steps = max(2, int((d1 - d0) / 4) + 1)
        line = [point_at(d0 + (d1 - d0) * i / (steps - 1)) for i in range(steps)]
        draw.line(line, fill=fill, width=width, joint="curve")

def draw_trim(draw, pts, prog, fill, width=3):
    p = clamp01(prog)
    if p <= 0.001:
        return
    n = max(2, int(len(pts) * p))
    draw.line(pts[:n], fill=fill, width=width, joint="curve")

def draw_check(draw, cx, cy, r, color=(255, 255, 255, 255), width=5):
    draw.line([(cx - r * 0.55, cy + r * 0.05), (cx - r * 0.1, cy + r * 0.45),
               (cx + r * 0.6, cy - r * 0.4)], fill=color, width=width, joint="curve")

def glow_sprite(size, color, power=2.0):
    s = size
    y, x = np.ogrid[:s, :s]
    d = np.sqrt((x - s / 2) ** 2 + (y - s / 2) ** 2) / (s / 2)
    a = np.clip(1 - d, 0, 1) ** power
    img = np.zeros((s, s, 4), np.uint8)
    img[..., 0] = color[0]
    img[..., 1] = color[1]
    img[..., 2] = color[2]
    img[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(img, "RGBA")

def ring_sprite(size, color, thickness=6):
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([thickness, thickness, s - thickness, s - thickness], outline=color, width=thickness)
    return img

def star_points(cx, cy, r_out, r_in, n=4, rot=0.0):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = rot + math.pi * i / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

# ---------------- background ----------------
def build_bg():
    y = np.linspace(0, 1, H)[:, None]
    top = np.array([38, 43, 49], np.float64)
    bot = np.array([24, 27, 32], np.float64)
    arr = top[None, None, :] * (1 - y[..., None]) + bot[None, None, :] * y[..., None]
    arr = np.repeat(arr, W, axis=1)
    # radial washes
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    d1 = np.sqrt(((xx - 1620) / 900) ** 2 + ((yy - 180) / 620) ** 2)
    arr += (np.clip(1 - d1, 0, 1) ** 2)[..., None] * np.array([0, 60, 80])
    d2 = np.sqrt(((xx - 300) / 1000) ** 2 + ((yy - 950) / 640) ** 2)
    arr += (np.clip(1 - d2, 0, 1) ** 2)[..., None] * np.array([18, 30, 90])
    # vignette
    dv = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    arr *= (1 - 0.34 * np.clip(dv - 0.55, 0, 1) ** 1.5)[..., None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(img)
    # faint dot grid
    for gy in range(60, H, 56):
        for gx in range(40, W, 56):
            d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(255, 255, 255, 10))
    # faint perspective lines bottom (kept low to avoid crossing text)
    for i in range(9):
        x0 = W / 2 + (i - 4) * 260
        d.line([(W / 2 + (i - 4) * 60, 1080), (x0, 935)], fill=(255, 255, 255, 6), width=2)
    return img

BG = None
GLOW_CYAN = None
GLOW_BLUE = None
GLOW_WHITE = None

# deterministic drifting dust
_rng = np.random.default_rng(11)
DUST = [(float(_rng.uniform(0, W)), float(_rng.uniform(0, H)),
         float(_rng.uniform(4, 16)), float(_rng.uniform(0.5, 1.6))) for _ in range(46)]

def draw_dust(base, t, alpha=0.5):
    d = ImageDraw.Draw(base, "RGBA")
    for x, y, sp, r in DUST:
        yy = (y - t * sp) % (H + 40) - 20
        xx = (x + math.sin(t * 0.3 + y * 0.01) * 14) % W
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(160, 200, 220, int(26 * alpha)))

# ============================================================
#  PRERENDERED ASSETS
# ============================================================
CHAOS = [
    ("Nova funcionalidade", "escopo aberto", AMBER),
    ("Bug em produção", "sem dono definido", RED),
    ("Integração externa", "dependência externa", AMBER),
    ("Lentidão no app", "sem contexto", RED),
    ("Débito técnico", "retrabalho", AMBER),
    ("Novo relatório", "prioridade incerta", AMBER),
    ("Migração de dados", "bloqueado", RED),
    ("Pedido do cliente", "prazo apertado", AMBER),
]
CHAOS_POS = [(345, 215, -9), (730, 165, 6), (1180, 185, -6), (1575, 235, 9),
             (300, 770, 7), (640, 845, -5), (1300, 825, 8), (1620, 745, -8)]
CHAOS_SLOT = [(250, 760), (675, 760), (1100, 760), (1525, 760),
              (250, 900), (675, 900), (1100, 900), (1525, 900)]

def build_chaos_card(title, meta, dot):
    img, pad = card_base(380, 116, accent=dot + (255,))
    d = ImageDraw.Draw(img)
    d.ellipse([pad + 30, pad + 30, pad + 48, pad + 48], fill=dot + (255,))
    ti = text_img(title, RUBIK, 30, "SemiBold", WHITE + (255,))
    img.alpha_composite(ti, (pad + 60, pad + 12))
    mi = text_img(meta, RUBIK, 22, "Regular", (170, 180, 190, 255))
    img.alpha_composite(mi, (pad + 60, pad + 56))
    return img

CHAOS_IMGS = {}   # (i, angle) -> img
CHAOS_ANGLES = [-12, -9, -6, -3, 0, 3, 6, 9, 12]

ROLES = [
    ("Prototyper", "explorar ideias", CYAN),
    ("Builder", "construir", BLUE),
    ("Sweeper", "simplificar", CYAN_L),
    ("Grower", "evoluir", GREEN),
    ("Maintainer", "manter", AMBER),
]
ROLE_X = [240, 600, 960, 1320, 1680]
ROLE_Y = 610

def build_role_card(name, verb, accent):
    img, pad = card_base(300, 330, accent=None)
    d = ImageDraw.Draw(img)
    # accent top bar
    d.rounded_rectangle([pad + 26, pad + 16, pad + 274, pad + 22], radius=3, fill=accent + (255,))
    ni = text_img(name, MONTS, 35, "Bold", WHITE + (255,))
    img.alpha_composite(ni, (pad + 150 - ni.width // 2, pad + 150))
    vi = text_img(verb, RUBIK, 27, "Medium", accent + (255,) if False else CYAN_L + (255,))
    img.alpha_composite(vi, (pad + 150 - vi.width // 2, pad + 205))
    d.line([pad + 40, pad + 262, pad + 260, pad + 262], fill=(255, 255, 255, 44), width=2)
    # blend bar: especialista (cyan) + agente (blue)
    d.rounded_rectangle([pad + 40, pad + 280, pad + 170, pad + 292], radius=6, fill=CYAN + (255,))
    d.rounded_rectangle([pad + 174, pad + 280, pad + 260, pad + 292], radius=6, fill=BLUE + (255,))
    l1 = text_img("especialista", RUBIK, 17, "Regular", (172, 184, 196, 255))
    l2 = text_img("agente", RUBIK, 17, "Regular", (172, 184, 196, 255))
    img.alpha_composite(l1, (pad + 40, pad + 296))
    img.alpha_composite(l2, (pad + 260 - l2.width, pad + 296))
    return img

STATIONS = [
    ("Contexto", "entender o que existe", CYAN),
    ("Entrega", "incrementos visíveis", BLUE),
    ("Qualidade", "testes e revisão", GREEN),
]
ST_X = [430, 960, 1490]
ST_Y = 470

def build_station(name, desc, accent):
    img, pad = card_base(320, 150, accent=accent + (255,))
    ni = text_img(name, MONTS, 36, "Bold", WHITE + (255,))
    img.alpha_composite(ni, (pad + 48, pad + 22))
    di = text_img(desc, RUBIK, 23, "Regular", (175, 186, 196, 255))
    img.alpha_composite(di, (pad + 48, pad + 82))
    return img

TOKENS = ["protótipo", "incremento", "teste", "revisão"]

def build_token(label):
    f = font(RUBIK, 25, "Medium")
    try:
        tw = int(sum(f.getlength(ch) for ch in label))
    except Exception:
        tw = 25 * len(label) // 2
    w = tw + 72
    img = Image.new("RGBA", (w + 60, 56 + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([30, 32, 30 + w, 32 + 56], radius=28, fill=(0, 0, 0, 130))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d.rounded_rectangle([30, 30, 30 + w, 30 + 56], radius=28, fill=(30, 66, 150, 245),
                        outline=CYAN + (255,), width=3)
    d.ellipse([30 + 20, 30 + 22, 30 + 36, 30 + 38], fill=CYAN + (255,))
    ti = text_img(label, RUBIK, 25, "Medium", WHITE + (255,))
    img.alpha_composite(ti, (30 + 46, 30 + 8))
    return img

EVIDENCE = ["dono definido", "incremento demonstrável", "testes executados", "revisão registrada"]

def build_evidence(label):
    f = font(RUBIK, 24, "Regular")
    try:
        tw = int(sum(f.getlength(ch) for ch in label))
    except Exception:
        tw = 24 * len(label) // 2
    w = tw + 92
    img = Image.new("RGBA", (w + 40, 60 + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([20, 20, 20 + w, 20 + 60], radius=30, fill=(28, 34, 40, 240),
                        outline=(255, 255, 255, 44), width=2)
    d.ellipse([20 + 18, 20 + 16, 20 + 50, 20 + 48], fill=GREEN + (255,))
    draw_check(d, 20 + 34, 20 + 32, 10, WHITE + (255,), 4)
    ti = text_img(label, RUBIK, 24, "Regular", (225, 232, 238, 255))
    img.alpha_composite(ti, (20 + 60, 20 + 12))
    return img

ASSETS = {}

def prerender():
    global BG, GLOW_CYAN, GLOW_BLUE, GLOW_WHITE
    BG = build_bg()
    GLOW_CYAN = glow_sprite(320, CYAN)
    GLOW_BLUE = glow_sprite(320, BLUE)
    GLOW_WHITE = glow_sprite(320, WHITE)
    for i, (ti, me, dot) in enumerate(CHAOS):
        base = build_chaos_card(ti, me, dot)
        for a in CHAOS_ANGLES:
            ASSETS[("chaos", i, a)] = base.rotate(a, expand=True, resample=Image.BICUBIC) if a else base
    for name, verb, ac in ROLES:
        ASSETS[("role", name)] = build_role_card(name, verb, ac)
    for name, desc, ac in STATIONS:
        ASSETS[("st", name)] = build_station(name, desc, ac)
    for tk in TOKENS:
        ASSETS[("tok", tk)] = build_token(tk)
    for ev in EVIDENCE:
        ASSETS[("ev", ev)] = build_evidence(ev)
    # headlines
    s = fit_size("não resolvem tudo.", MONTS, "ExtraBold", 116, 1500)
    ASSETS["h1a"] = text_img("Mais horas", MONTS, s, "ExtraBold", WHITE + (255,))
    ASSETS["h1b"] = text_img("não resolvem tudo.", MONTS, s, "ExtraBold", CYAN + (255,))
    s = fit_size("AI-Native Delivery Pods", MONTS, "ExtraBold", 92, 1500)
    ASSETS["t2"] = text_img("AI-Native Delivery Pods", MONTS, s, "ExtraBold", WHITE + (255,))
    ASSETS["t2sub"] = text_img("Uma equipe moldada pelo resultado.", RUBIK, 36, "Regular",
                               (205, 214, 222, 255))
    ASSETS["eyebrow_pod"] = text_img("DENTRO DO POD", MONTS, 26, "ExtraBold", CYAN_L + (255,), tracking=6)
    s = fit_size("Especialistas + agentes supervisionados", MONTS, "Bold", 62, 1680)
    a = text_img("Especialistas ", MONTS, s, "Bold", WHITE + (255,))
    b = text_img("+", MONTS, s, "Bold", CYAN + (255,))
    c = text_img(" agentes supervisionados", MONTS, s, "Bold", WHITE + (255,))
    w = a.width + b.width + c.width
    h = max(a.height, b.height, c.height)
    combo = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    combo.alpha_composite(a, (0, 0))
    combo.alpha_composite(b, (a.width, 0))
    combo.alpha_composite(c, (a.width + b.width, 0))
    ASSETS["t3"] = combo
    ASSETS["ckpt_label"] = text_img("checkpoints humanos nas decisões", RUBIK, 28, "Medium",
                                    (205, 214, 222, 255))
    s = fit_size("Responsabilidade clara.", MONTS, "ExtraBold", 76, 1500)
    ASSETS["h4a"] = text_img("Progresso visível.", MONTS, s, "ExtraBold", WHITE + (255,))
    ASSETS["h4b"] = text_img("Responsabilidade clara.", MONTS, s, "ExtraBold", CYAN + (255,))
    ASSETS["eyebrow_ev"] = text_img("EVIDÊNCIAS DE PROGRESSO", MONTS, 24, "ExtraBold",
                                    CYAN_L + (255,), tracking=6)
    # finale
    logo = Image.open("work/logo-light-t.png").convert("RGBA")
    ASSETS["logo"] = logo
    s = fit_size("AI-Native Delivery Pods", MONTS, "ExtraBold", 76, 1500)
    ASSETS["t5"] = text_img("AI-Native Delivery Pods", MONTS, s, "ExtraBold", WHITE + (255,))
    ASSETS["url"] = text_img("t2stech.com", RUBIK, 42, "Medium", (232, 238, 243, 255), tracking=4)
    ASSETS["eyebrow_next"] = text_img("PRÓXIMO PASSO", MONTS, 26, "ExtraBold", CYAN_L + (255,), tracking=6)
    # CTA button
    bw, bh = 620, 100
    btn = Image.new("RGBA", (bw + 80, bh + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(btn)
    sh = Image.new("RGBA", btn.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([40, 48, 40 + bw, 48 + bh], radius=50, fill=(20, 40, 160, 200))
    btn.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    d.rounded_rectangle([40, 40, 40 + bw, 40 + bh], radius=50, fill=BLUE + (255,))
    d.rounded_rectangle([40, 40, 40 + bw, 40 + bh], radius=50, outline=(255, 255, 255, 70), width=2)
    d.line([40 + 60, 40 + 6, 40 + bw - 60, 40 + 6], fill=(255, 255, 255, 60), width=3)
    bt = text_img("Converse com um engenheiro  ↗", MONTS, 30, "Bold", WHITE + (255,))
    btn.alpha_composite(bt, (40 + bw // 2 - bt.width // 2, 40 + bh // 2 - bt.height // 2))
    ASSETS["btn"] = btn
    # node icons
    ASSETS["person"] = build_person()
    ASSETS["agent"] = build_agent()
    ASSETS["pod"] = text_img("POD", MONTS, 44, "ExtraBold", WHITE + (255,), tracking=4)
    ASSETS["lab_esp"] = text_img("Especialistas", RUBIK, 30, "Medium", (225, 235, 242, 255))
    ASSETS["lab_age"] = text_img("Agentes supervisionados", RUBIK, 30, "Medium", (225, 235, 242, 255))

def build_person():
    img = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([14, 14, 106, 106], fill=(16, 40, 54, 255), outline=CYAN + (255,), width=4)
    d.ellipse([48, 34, 72, 58], fill=WHITE + (255,))
    d.pieslice([36, 58, 84, 106], 180, 360, fill=WHITE + (255,))
    return img

def build_agent():
    img = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, r = 60, 60, 46
    pts = [(cx + r * math.cos(math.pi / 6 + i * math.pi / 3),
            cy + r * math.sin(math.pi / 6 + i * math.pi / 3)) for i in range(6)]
    d.line(pts + [pts[0]], fill=BLUE + (255,), width=5, joint="curve")
    d.polygon(star_points(cx, cy, 20, 7), fill=CYAN_L + (255,))
    return img

# ============================================================
#  ROLE ICONS (drawn live, small)
# ============================================================
def draw_role_icon(base, name, cx, cy, t, reveal_p):
    d = ImageDraw.Draw(base, "RGBA")
    p = ease_out_cubic(reveal_p)
    if p <= 0.01:
        return
    a = int(255 * p)
    if name == "Prototyper":
        rot = t * 0.8
        for k in range(12):
            a0 = rot + k * math.pi / 6
            a1 = a0 + math.pi / 9
            d.arc([cx - 34, cy - 34, cx + 34, cy + 34], math.degrees(a0), math.degrees(a1),
                  fill=CYAN + (a,), width=3)
        d.polygon(star_points(cx, cy, 20 * p, 7 * p, rot=t * 1.4), fill=WHITE + (a,))
        tw = blink(t, 3.0)
        d.ellipse([cx + 30, cy - 34, cx + 36, cy - 28], fill=CYAN_L + (int(a * tw),))
        d.ellipse([cx - 38, cy + 22, cx - 32, cy + 28], fill=CYAN_L + (int(a * (1 - tw)),))
    elif name == "Builder":
        # stacking blocks
        offs = [(0, 26, 72), (0, 2, 56), (0, -22, 40)]
        for i, (ox, oy, wdt) in enumerate(offs):
            q = ease_out_back(seg(t * 1.0, 0, 1) if False else clamp01(reveal_p * 1.6 - i * 0.2))
            yy = cy + oy + (1 - q) * 30
            al = int(a * clamp01(reveal_p * 1.6 - i * 0.2))
            if al > 0:
                d.rounded_rectangle([cx - wdt / 2, yy - 10, cx + wdt / 2, yy + 10], radius=5,
                                    fill=(52, 100, 255, al) if i < 2 else (0, 180, 232, al))
        d.polygon(star_points(cx + 44, cy - 30, 9, 3.5, rot=t), fill=CYAN_L + (a,))
    elif name == "Sweeper":
        for i, ln in enumerate((56, 72, 48)):
            yy = cy - 20 + i * 20
            d.line([cx - ln / 2, yy, cx + ln / 2, yy], fill=(200, 212, 222, a), width=5)
        sy = cy - 34 + ((t * 60) % 68)
        d.line([cx - 44, sy, cx + 44, sy], fill=CYAN + (int(a * 0.85),), width=4)
        d.line([cx + 48, cy - 26, cx + 58, cy - 16], fill=(255, 255, 255, a), width=3)
        d.line([cx + 58, cy - 26, cx + 48, cy - 16], fill=(255, 255, 255, a), width=3)
    elif name == "Grower":
        # static stepped growth line + arrow (always complete) + traveling dot
        pts = [(cx - 40, cy + 26), (cx - 14, cy + 26), (cx - 14, cy + 4),
               (cx + 10, cy + 4), (cx + 10, cy - 18), (cx + 38, cy - 18)]
        d.line(pts, fill=GREEN + (a,), width=6, joint="curve")
        hx, hy = pts[-1]
        d.polygon([(hx - 2, hy - 13), (hx + 14, hy), (hx - 2, hy + 13)],
                  fill=GREEN + (a,))
        d.line([cx - 44, cy + 34, cx + 44, cy + 34], fill=(255, 255, 255, int(a * 0.35)), width=2)
        # traveling dot along the steps
        u = (t * 0.4) % 1.0
        seglens = [math.hypot(b[0] - a0[0], b[1] - a0[1]) for a0, b in zip(pts[:-1], pts[1:])]
        tot = sum(seglens)
        dd = u * tot
        px, py = pts[0]
        for (a0, b), sl in zip(zip(pts[:-1], pts[1:]), seglens):
            if dd <= sl:
                v = dd / max(sl, 1e-6)
                px, py = a0[0] + (b[0] - a0[0]) * v, a0[1] + (b[1] - a0[1]) * v
                break
            dd -= sl
        else:
            px, py = pts[-1]
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=(255, 255, 255, a))
    elif name == "Maintainer":
        pr = 1 + 0.05 * math.sin(t * 3)
        r = 34 * pr
        shield = [(cx, cy - r), (cx + r * 0.8, cy - r * 0.45), (cx + r * 0.8, cy + r * 0.2),
                  (cx, cy + r), (cx - r * 0.8, cy + r * 0.2), (cx - r * 0.8, cy - r * 0.45)]
        d.line(shield + [shield[0]], fill=AMBER + (a,), width=4, joint="curve")
        draw_check(d, cx, cy + 2, 14, WHITE + (a,), 5)
        rp = (t * 0.5) % 1.0
        d.ellipse([cx - r - rp * 22, cy - r - rp * 22, cx + r + rp * 22, cy + r + rp * 22],
                  outline=AMBER + (int(a * (1 - rp) * 0.5),), width=2)

# ============================================================
#  SCENES
# ============================================================
def _h1_scrim(base, img, cx, cy, prog, alpha):
    """Soft dark halo behind opening headline so card edges/links passing
    underneath never hurt glyph legibility. Follows the wipe progress."""
    p = clamp01(prog)
    if p <= 0.01 or alpha <= 0.01:
        return
    halo = Image.new("RGBA", (img.width + 120, img.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(halo).rounded_rectangle([0, 0, halo.width, halo.height], radius=30,
                                           fill=(18, 22, 27, int(150 * alpha)))
    m = wipe_mask(halo.width, halo.height, p, "left").point(lambda v: int(v * 0.9))
    import PIL.ImageChops as _Chops
    halo.putalpha(_Chops.multiply(halo.getchannel("A"), m))
    base.alpha_composite(halo, (int(round(cx - halo.width / 2)), int(round(cy - halo.height / 2))))


def scene1(base, t):
    # envelopes
    enter = ease_out_cubic(seg(t, 0.0, 0.5))
    exit_p = seg(t, 4.9, 5.7)
    if t > 6.4 or exit_p >= 1 and t > 6.0:
        return
    alpha = enter * (1 - ease_in_cubic(exit_p))
    if alpha <= 0.001:
        return
    # NOTE (correction v2): headline is drawn AFTER the cards (see end of
    # scene1) so in-flight cards can never cover the text. Reveal progress
    # is computed here for reuse below.
    r1 = ease_out_cubic(seg(t, 0.8, 1.6))
    r2 = ease_out_cubic(seg(t, 1.1, 1.9))
    yoff = -160 * ease_in_cubic(exit_p)
    und = ease_out_cubic(seg(t, 1.9, 2.4))
    # cards
    align = ease_in_out(seg(t, 3.2, 4.7))
    snap = 1 + 0.03 * pulse(t, 4.55, 0.4)
    jitter_amp = (1 - align) * 9
    d = ImageDraw.Draw(base, "RGBA")
    # links (chaos phase)
    link_a = (1 - align) * alpha
    if link_a > 0.01:
        pairs = [(0, 3), (1, 4), (2, 5), (0, 6), (3, 7), (1, 2)]
        for k, (i, j) in enumerate(pairs):
            p0 = CHAOS_POS[i][:2]
            p1 = CHAOS_POS[j][:2]
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            ctrl = (mx + (30 if k % 2 else -40), my - 60 + k * 12)
            pts = bezier(p0, ctrl, p1)
            draw_dashed(d, pts, dash=12, gap=10, phase=(t * 90 + k * 40) % 22,
                        fill=(229, 159, 36, int(120 * link_a)), width=3)
    for i in range(8):
        pop = ease_out_back(seg(t, 0.15 + i * 0.09, 0.75 + i * 0.09))
        if pop <= 0.01:
            continue
        # cards morph into core: hold slots -> accelerate to core 5.4-6.1
        q = ease_in_out(seg(t, 5.4 + i * 0.05, 6.1 + i * 0.05))
        card_a = enter * (1 - q) * clamp01(pop)
        if card_a <= 0.003:
            continue
        cx0, cy0, a0 = CHAOS_POS[i]
        sx, sy = CHAOS_SLOT[i]
        jx = math.sin(t * 2.1 + i * 2.4) * jitter_amp
        jy = math.cos(t * 1.7 + i * 1.3) * jitter_amp
        cx = lerp(lerp(cx0 + jx, sx, align), 960, q)
        cy = lerp(lerp(cy0 + jy, sy, align), 730, q) - math.sin(q * math.pi) * 50 * (1 if i % 2 else -1) * 0.4
        ang = lerp(a0, 0, align)
        nearest = min(CHAOS_ANGLES, key=lambda a: abs(a - ang))
        img = ASSETS[("chaos", i, nearest)]
        sc = (0.7 + 0.3 * pop) * lerp(1.0, 0.92, align) * snap * (1 - q * 0.7)
        paste_center(base, img, cx, cy, card_a, sc)
    # align flash ring at grid lock
    if 4.4 < t < 5.4:
        q = seg(t, 4.55, 5.3)
        r = 60 + q * 700
        dd = ImageDraw.Draw(base, "RGBA")
        dd.ellipse([960 - r, 830 - r * 0.45, 960 + r, 830 + r * 0.45],
                   outline=(0, 180, 232, int(120 * (1 - q) * alpha)), width=3)
    # headline ON TOP of cards + links (correction v2): full phrase readable
    # during the whole opening reading interval, nothing overlaps the text.
    d = ImageDraw.Draw(base, "RGBA")
    # both scrims first, then both text lines: the two halos overlap each
    # other slightly, so drawing scrim2 before text1 keeps line 1 at full
    # brightness instead of dimmed under line 2's halo.
    if r1 > 0:
        _h1_scrim(base, ASSETS["h1a"], 960, 360 + yoff + (1 - r1) * 40, r1, alpha)
    if r2 > 0:
        _h1_scrim(base, ASSETS["h1b"], 960, 470 + yoff + (1 - r2) * 40, r2, alpha)
    if r1 > 0:
        paste_wipe(base, ASSETS["h1a"], 960, 360 + yoff + (1 - r1) * 40, r1, "left", alpha)
    if r2 > 0:
        paste_wipe(base, ASSETS["h1b"], 960, 470 + yoff + (1 - r2) * 40, r2, "left", alpha)
    if und > 0 and alpha > 0:
        wdt = 340 * und
        d.rounded_rectangle([960 - wdt / 2, 545 + yoff, 960 + wdt / 2, 551 + yoff], radius=3,
                            fill=(0, 180, 232, int(255 * alpha)))

def scene2(base, t):
    if t < 4.9 or t > 10.9:
        return
    enter = seg(t, 4.9, 5.4)
    exit_p = seg(t, 9.55, 10.35)
    alpha = clamp01(enter) * (1 - ease_in_cubic(exit_p))
    if alpha <= 0.001:
        return
    CORE = (960, 730)
    # title
    tr = ease_out_cubic(seg(t, 6.1, 7.1))
    sr = ease_out_cubic(seg(t, 7.15, 7.85))
    dy = -160 * ease_in_cubic(exit_p)
    t_alpha = alpha * (1 - seg(t, 9.55, 9.95))  # title gone before S3 header wipes in
    if tr > 0 and t_alpha > 0.001:
        paste_wipe(base, ASSETS["t2"], 960, 250 + dy + (1 - tr) * 36, tr, "left", t_alpha)
    if sr > 0 and t_alpha > 0.001:
        paste_center(base, ASSETS["t2sub"], 960, 360 + dy + (1 - sr) * 24, t_alpha * sr)
    if tr > 0.9 and t_alpha > 0.001:
        d = ImageDraw.Draw(base, "RGBA")
        uw = 520 * ease_out_cubic(seg(t, 7.2, 7.9))
        d.rounded_rectangle([960 - uw / 2, 300 + dy, 960 + uw / 2, 305 + dy], radius=2,
                            fill=(0, 180, 232, int(255 * t_alpha)))
    # core glow + disc (S1 cards morph into this disc; no separate fly-in layer)
    breathe = 1 + 0.03 * math.sin(t * 2.4)
    core_sc = 0.3 + 0.7 * ease_out_back(seg(t, 5.5, 6.7))
    gsc = 2.6 * core_sc * breathe
    paste_center(base, GLOW_BLUE, CORE[0], CORE[1], 0.55 * alpha * core_sc, gsc)
    paste_center(base, GLOW_CYAN, CORE[0], CORE[1], 0.35 * alpha * core_sc, gsc * 0.6)
    d = ImageDraw.Draw(base, "RGBA")
    R = 86 * core_sc * breathe
    if R > 4:
        d.ellipse([CORE[0] - R, CORE[1] - R, CORE[0] + R, CORE[1] + R],
                  fill=(24, 40, 80, int(245 * alpha)), outline=CYAN + (int(255 * alpha),), width=4)
        d.ellipse([CORE[0] - R + 12, CORE[1] - R + 12, CORE[0] + R - 12, CORE[1] + R - 12],
                  outline=(255, 255, 255, int(60 * alpha)), width=2)
        paste_center(base, ASSETS["pod"], CORE[0], CORE[1], alpha * core_sc, core_sc)
    # rotating dashed orbit
    if core_sc > 0.5:
        for k in range(18):
            a0 = t * 0.5 + k * math.pi / 9
            a1 = a0 + math.pi / 14
            d.arc([CORE[0] - R - 26, CORE[1] - R - 26, CORE[0] + R + 26, CORE[1] + R + 26],
                  math.degrees(a0), math.degrees(a1), fill=(0, 180, 232, int(150 * alpha)), width=3)
    # nodes
    angles = [150, 180, 210, -30, 0, 30]
    kinds = ["person"] * 3 + ["agent"] * 3
    for k in range(6):
        pop = ease_out_back(seg(t, 6.0 + k * 0.22, 6.7 + k * 0.22))
        if pop <= 0.01:
            continue
        ang = math.radians(angles[k])
        # exit: fly to role slots
        ex = ease_in_out(exit_p)
        nx = CORE[0] + math.cos(ang) * 265 + math.sin(t * 1.6 + k) * 8 * (1 - ex)
        ny = CORE[1] + math.sin(ang) * 190 + math.cos(t * 1.3 + k * 2) * 8 * (1 - ex)
        tx = ROLE_X[k % 5] if k < 5 else ROLE_X[4]
        # map 6 nodes -> 5 cards (merge last two visually)
        if k == 5:
            tx = ROLE_X[4]
        fx = lerp(nx, tx, ex)
        fy = lerp(ny, ROLE_Y - 40, ex)
        # link core->node (stop short of disc edge so lines never cross POD text)
        exx = ex
        dx, dy2 = fx - CORE[0], fy - CORE[1]
        dl = max(math.hypot(dx, dy2), 1.0)
        sx = CORE[0] + dx / dl * (R + 4)
        sy = CORE[1] + dy2 / dl * (R + 4)
        pts = bezier((sx, sy), ((sx + fx) / 2, (sy + fy) / 2 - 30), (fx, fy))
        col = CYAN if k < 3 else BLUE
        draw_trim(d, pts, pop * (1 - exx * 0.5), col + (int(200 * alpha),), 3)
        # traveling pulse dot from node toward core edge (never inside the disc)
        if pop > 0.9 and exx < 0.5:
            u = (t * 0.5 + k * 0.17) % 1.0
            idx = int((1 - u) * (len(pts) - 1))
            px, py = pts[idx]
            d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(255, 255, 255, int(220 * alpha)))
        img = ASSETS["person"] if kinds[k] == "person" else ASSETS["agent"]
        paste_center(base, img, fx, fy, alpha * clamp01(pop), 0.85 * max(0.05, pop))
    # group labels
    lr = ease_out_cubic(seg(t, 7.4, 8.0))
    if lr > 0:
        ex = ease_in_out(exit_p)
        lab_a = alpha * lr * (1 - ex) * (1 - seg(t, 9.55, 9.9))  # gone before exit dive
        if lab_a <= 0.003:
            return_node_labels_done = True
        else:
            for lab, lx in ((ASSETS["lab_esp"], 560), (ASSETS["lab_age"], 1360)):
                scrim = Image.new("RGBA", (lab.width + 80, 60), (0, 0, 0, 0))
                ImageDraw.Draw(scrim).rounded_rectangle([0, 0, lab.width + 80, 60], radius=30,
                                                         fill=(20, 24, 28, int(150 * lab_a)))
                paste_center(base, scrim, lx, 950, 1.0)
                paste_center(base, lab, lx, 950 + (1 - lr) * 20, lab_a)
            d = ImageDraw.Draw(base, "RGBA")
            d.ellipse([560 - ASSETS["lab_esp"].width // 2 - 46, 950 - 9, 560 - ASSETS["lab_esp"].width // 2 - 28, 950 + 9],
                      fill=CYAN + (int(255 * lab_a),))
            d.ellipse([1360 - ASSETS["lab_age"].width // 2 - 46, 950 - 9, 1360 - ASSETS["lab_age"].width // 2 - 28, 950 + 9],
                      fill=BLUE + (int(255 * lab_a),))

ROLE_HITS = [10.5, 11.5, 12.5, 13.5, 14.5]

def scene3(base, t):
    if t < 9.9 or t > 17.4:
        return
    enter = seg(t, 9.9, 10.3)
    exit_p = seg(t, 16.35, 17.1)
    alpha = clamp01(enter) * (1 - ease_in_cubic(exit_p))
    if alpha <= 0.001:
        return
    d = ImageDraw.Draw(base, "RGBA")
    # header (fades out before S4 header wipes in)
    h_alpha = alpha * (1 - seg(t, 16.35, 16.7))
    er = ease_out_cubic(seg(t, 10.15, 10.65))
    hr = ease_out_cubic(seg(t, 10.35, 11.05))
    dy = -110 * ease_in_cubic(exit_p)
    if er > 0 and h_alpha > 0.001:
        paste_center(base, ASSETS["eyebrow_pod"], 960, 170 + dy + (1 - er) * 24, h_alpha * er)
    if hr > 0 and h_alpha > 0.001:
        paste_wipe(base, ASSETS["t3"], 960, 258 + dy + (1 - hr) * 30, hr, "left", h_alpha)
    # spine
    spine = ease_out_cubic(seg(t, 10.0, 10.9))
    if spine > 0:
        x1 = lerp(120, 1800, spine)
        d.line([(120, ROLE_Y), (x1, ROLE_Y)], fill=(0, 180, 232, int(120 * alpha)), width=3)
    for i, (name, verb, ac) in enumerate(ROLES):
        hit = ROLE_HITS[i]
        rp = ease_out_back(seg(t, hit, hit + 0.5))
        if rp <= 0.01:
            continue
        # exit: sink + shrink staggered
        ex = ease_in_cubic(seg(t, 16.35 + i * 0.05, 17.05 + i * 0.05))
        sc = max(0.05, rp) * (1 - ex * 0.5)
        yy = ROLE_Y + (1 - min(1.0, rp)) * 60 + ex * 90
        # hit flash ring + glow
        fl = pulse(t, hit, 0.6)
        if fl > 0.01:
            r = 40 + (1 - fl) * 160 + 60
            rr = 40 + seg(t, hit, hit + 0.6) * 220
            d.ellipse([ROLE_X[i] - rr, yy - rr * 0.7, ROLE_X[i] + rr, yy + rr * 0.7],
                      outline=ac + (int(160 * fl * alpha),), width=4)
            paste_center(base, GLOW_WHITE, ROLE_X[i], yy, 0.5 * fl * alpha, 1.6)
        paste_center(base, ASSETS[("role", name)], ROLE_X[i], yy, alpha * (1 - ex) * clamp01(rp + 0.2), sc)
        # live icon
        icon_a = alpha * (1 - ex)
        if icon_a > 0.01 and rp > 0.3:
            # draw icon on overlay then composite scaled? draw at final pos approx (scale ignored for icon, cards ~1)
            draw_role_icon(base, name, ROLE_X[i], yy - 88 * sc, t, clamp01((rp - 0.3) / 0.7))
    # checkpoints
    ck_times = [15.35, 15.75, 16.15]
    ck_x = [780, 1140, 1500]
    lr = ease_out_cubic(seg(t, 15.6, 16.2))
    ex = ease_in_cubic(exit_p)
    for cx, ct in zip(ck_x, ck_times):
        cp = ease_out_back(seg(t, ct, ct + 0.45))
        if cp <= 0.01:
            continue
        cy = ROLE_Y - 150
        fl = pulse(t, ct, 0.7)
        if fl > 0.01:
            paste_center(base, GLOW_WHITE, cx, cy, 0.4 * fl * alpha, 1.0)
        r = 30 * max(0.05, cp)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(34, 189, 81, int(255 * alpha * (1 - ex))),
                  outline=(255, 255, 255, int(220 * alpha * (1 - ex))), width=3)
        if cp > 0.6:
            draw_check(d, cx, cy, 13, WHITE + (int(255 * alpha * (1 - ex)),), 5)
        # stem down toward caption (fades before touching text)
        d.line([(cx, cy + r), (cx, cy + 210)], fill=(34, 189, 81, int(110 * alpha * (1 - ex))), width=3)
        d.ellipse([cx - 5, cy + 210 - 5, cx + 5, cy + 210 + 5],
                  fill=(34, 189, 81, int(160 * alpha * (1 - ex))))
    if lr > 0:
        # dark scrim behind caption for legibility over rays
        cap = ASSETS["ckpt_label"]
        scrim = Image.new("RGBA", (cap.width + 90, 64), (0, 0, 0, 0))
        ImageDraw.Draw(scrim).rounded_rectangle([0, 0, cap.width + 90, 64], radius=32,
                                                 fill=(20, 24, 28, int(150 * alpha * lr * (1 - ex))))
        paste_center(base, scrim, 960, 950 + dy * 0.3, 1.0)
        paste_center(base, cap, 960, 950 + dy * 0.3 + (1 - lr) * 20,
                     alpha * lr * (1 - ex))

TRACK_Y = 640
TRACK_X0, TRACK_X1 = 200, 1720

def scene4(base, t):
    if t < 16.6 or t > 24.35:
        return
    d = ImageDraw.Draw(base, "RGBA")
    exit_p = seg(t, 23.9, 24.35)
    alpha = 1 - ease_in_cubic(exit_p)
    if alpha <= 0.001:
        return
    # header (delayed until S3 titles are gone)
    r1 = ease_out_cubic(seg(t, 17.3, 17.95))
    r2 = ease_out_cubic(seg(t, 17.55, 18.15))
    if r1 > 0:
        paste_wipe(base, ASSETS["h4a"], 960, 200 + (1 - r1) * 30, r1, "left", alpha)
    if r2 > 0:
        paste_wipe(base, ASSETS["h4b"], 960, 285 + (1 - r2) * 30, r2, "left", alpha)
    # track (spine continuity: S3 spine at y=610 bends down to 640)
    tp = ease_out_cubic(seg(t, 16.7, 17.6))
    riser = seg(t, 22.6, 24.0)
    glow_boost = 1 + riser * 1.6
    if tp > 0:
        x1 = lerp(TRACK_X0, TRACK_X1, tp)
        d.line([(TRACK_X0, TRACK_Y), (x1, TRACK_Y)], fill=(255, 255, 255, int(40 * alpha)), width=10)
        d.line([(TRACK_X0, TRACK_Y), (x1, TRACK_Y)], fill=(0, 180, 232, int(min(255, 150 * glow_boost) * alpha)), width=4)
        # flow dashes
        pts = [(TRACK_X0 + i * 20, TRACK_Y) for i in range(int((x1 - TRACK_X0) / 20) + 1)]
        if len(pts) > 2:
            draw_dashed(d, pts, dash=16, gap=26, phase=(t * 260) % 42,
                        fill=(114, 223, 255, int(min(255, 200 * glow_boost) * alpha)), width=4)
    # stations
    for i, (name, desc, ac) in enumerate(STATIONS):
        sp = ease_out_back(seg(t, 17.15 + i * 0.3, 17.75 + i * 0.3))
        if sp <= 0.01:
            continue
        # station pulse when tokens pass / ticks
        pl = 0
        for tk_start in (17.9, 18.6, 19.3, 20.0):
            # token x at station?
            pass
        paste_center(base, GLOW_CYAN if i < 2 else GLOW_WHITE, ST_X[i], ST_Y,
                     0.25 * alpha * sp * glow_boost, 1.8)
        paste_center(base, ASSETS[("st", name)], ST_X[i], ST_Y + (1 - min(1.0, sp)) * 50,
                     alpha * clamp01(sp), max(0.05, sp))
        # connector to track
        cp = seg(t, 17.4 + i * 0.3, 17.9 + i * 0.3)
        if cp > 0:
            y1 = lerp(ST_Y + 75, TRACK_Y, cp)
            d.line([(ST_X[i], ST_Y + 75), (ST_X[i], y1)], fill=ac + (int(180 * alpha),), width=4)
            d.ellipse([ST_X[i] - 8, TRACK_Y - 8, ST_X[i] + 8, TRACK_Y + 8],
                      fill=ac + (int(255 * alpha),))
    # tokens
    starts = [17.9, 18.6, 19.3, 20.0]
    dur = 3.4
    for k, (label, ts) in enumerate(zip(TOKENS, starts)):
        p = seg(t, ts, ts + dur)
        if p <= 0 or p >= 1:
            continue
        # ease: constant speed with slight accel in riser
        e = p
        x = lerp(TRACK_X0 - 60, TRACK_X1 + 60, e)
        y = TRACK_Y - 52
        img = ASSETS[("tok", label)]
        # motion blur ghosts
        for g, ga in ((36, 0.25), (72, 0.12)):
            paste_center(base, img, x - g, y, alpha * ga, 1.0)
        sc = 0.6 + 0.4 * ease_out_cubic(seg(t, ts, ts + 0.3))
        fade = 1 - seg(t, ts + dur - 0.3, ts + dur)
        paste_center(base, img, x, y, alpha * fade, sc)
        paste_center(base, GLOW_CYAN, x, TRACK_Y, 0.35 * alpha * fade, 1.1)
    # gate flashes at audio ticks
    for tg in (19.9, 20.6, 21.3, 22.0):
        fl = pulse(t, tg, 0.5)
        if fl > 0.01:
            # lead token x at tg
            p = clamp01((tg - 17.9) / dur)
            x = lerp(TRACK_X0 - 60, TRACK_X1 + 60, p)
            rr = 20 + (1 - fl) * 90
            d.ellipse([x - rr, TRACK_Y - rr, x + rr, TRACK_Y + rr],
                      outline=(114, 223, 255, int(220 * fl * alpha)), width=4)
    # arrival bursts at Qualidade (21.3, 22.0)
    for ta in (21.3, 22.0, 22.7, 23.4):
        fl = pulse(t, ta, 0.6)
        if fl > 0.01:
            rr = 30 + (1 - fl) * 130
            d.ellipse([ST_X[2] - rr, TRACK_Y - rr, ST_X[2] + rr, TRACK_Y + rr],
                      outline=(34, 189, 81, int(200 * fl * alpha)), width=4)
    # evidence
    er = ease_out_cubic(seg(t, 17.9, 18.4))
    if er > 0:
        evl = ASSETS["eyebrow_ev"]
        scrim = Image.new("RGBA", (evl.width + 80, 56), (0, 0, 0, 0))
        ImageDraw.Draw(scrim).rounded_rectangle([0, 0, evl.width + 80, 56], radius=28,
                                                fill=(20, 24, 28, int(140 * alpha * er)))
        paste_center(base, scrim, 960, 800, 1.0)
        paste_center(base, evl, 960, 800 + (1 - er) * 20, alpha * er)
    ev_x = [330, 730, 1130, 1520]
    for i, (label, ex_) in enumerate(zip(EVIDENCE, ev_x)):
        ep = ease_out_back(seg(t, 18.2 + i * 0.8, 18.7 + i * 0.8))
        if ep <= 0.01:
            continue
        paste_center(base, ASSETS[("ev", label)], ex_, 872 + (1 - min(1.0, ep)) * 30,
                     alpha * clamp01(ep), max(0.05, ep))

def scene5(base, t):
    if t < 23.9:
        return
    d = ImageDraw.Draw(base, "RGBA")
    # flash
    if t < 24.6:
        fl = 1 - seg(t, 24.0, 24.5)
        if fl > 0.01:
            white = Image.new("RGBA", (W, H), (200, 230, 245, int(200 * fl * fl)))
            base.alpha_composite(white)
    # shockwave rings
    for t0, maxr, col in ((24.0, 1400, CYAN), (24.08, 1000, WHITE)):
        q = seg(t, t0, t0 + 1.1)
        if 0 < q < 1:
            r = 60 + ease_out_quart(q) * maxr
            d.ellipse([960 - r, 540 - r * 0.56, 960 + r, 540 + r * 0.56],
                      outline=col + (int(180 * (1 - q)),), width=5)
    breathe = 1 + 0.025 * math.sin((t - 24) * 2.0)
    # ambient glows ramp
    ga = ease_out_cubic(seg(t, 24.0, 25.0))
    if ga > 0:
        paste_center(base, GLOW_BLUE, 960, 480, 0.5 * ga, 4.2 * breathe)
        paste_center(base, GLOW_CYAN, 960, 480, 0.3 * ga, 2.6 * breathe)
    # logo
    lp = ease_out_back(seg(t, 24.12, 24.85), s=1.2)
    if lp > 0.01:
        logo = ASSETS["logo"]
        lw = 640
        sc = lw / logo.width * max(0.05, lp)
        paste_center(base, logo, 960, 330 + (1 - min(1.0, lp)) * 60, clamp01(lp + 0.1), sc)
    # shimmer sweep across logo at 27.0
    sh = seg(t, 26.9, 27.6)
    if 0 < sh < 1:
        sx = lerp(600, 1320, sh)
        band = glow_sprite(64, WHITE)
        paste_center(base, band, sx, 330, 0.35 * math.sin(sh * math.pi), 3.0)
    # eyebrow + title
    er = ease_out_cubic(seg(t, 24.4, 24.9))
    if er > 0:
        paste_center(base, ASSETS["eyebrow_next"], 960, 492 + (1 - er) * 20, er)
    tr = ease_out_cubic(seg(t, 24.55, 25.2))
    if tr > 0:
        # dark scrim behind title for legibility over rays
        ttl = ASSETS["t5"]
        scrim = Image.new("RGBA", (ttl.width + 80, 112), (0, 0, 0, 0))
        ImageDraw.Draw(scrim).rounded_rectangle([0, 0, ttl.width + 80, 112], radius=40,
                                                fill=(20, 24, 28, int(120 * tr)))
        paste_center(base, scrim, 960, 588, 1.0)
        paste_wipe(base, ttl, 960, 588 + (1 - tr) * 30, tr, "center", 1.0)
    # divider
    dv = seg(t, 25.1, 25.5)
    if dv > 0:
        wdt = 420 * dv
        d.rounded_rectangle([960 - wdt / 2, 648, 960 + wdt / 2, 651], radius=2,
                            fill=(255, 255, 255, 70))
    # CTA
    bp = ease_out_back(seg(t, 25.15, 25.75), s=1.3)
    if bp > 0.01:
        pulse27 = 1 + 0.04 * pulse(t, 27.0, 0.5)
        paste_center(base, ASSETS["btn"], 960, 745 + (1 - min(1.0, bp)) * 70,
                     clamp01(bp), max(0.05, bp) * pulse27)
        # shine sweep
        for t0 in (25.7, 27.0):
            q = seg(t, t0, t0 + 0.7)
            if 0 < q < 1:
                sx = lerp(960 - 260, 960 + 260, q)
                shine = glow_sprite(48, WHITE)
                paste_center(base, shine, sx, 738, 0.22 * math.sin(q * math.pi), 1.6)
    # URL
    ur = ease_out_cubic(seg(t, 25.7, 26.3))
    if ur > 0:
        url = ASSETS["url"]
        scrim = Image.new("RGBA", (url.width + 80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(scrim).rounded_rectangle([0, 0, url.width + 80, 80], radius=40,
                                                fill=(20, 24, 28, int(150 * ur)))
        paste_center(base, scrim, 960, 880, 1.0)
        paste_center(base, url, 960, 880 + (1 - ur) * 20, ur)

# ============================================================
#  FRAME RENDER
# ============================================================
def render_frame(t):
    frame = BG.copy()
    draw_dust(frame, t, alpha=0.6)
    scene1(frame, t)
    scene2(frame, t)
    scene3(frame, t)
    scene4(frame, t)
    scene5(frame, t)
    # global fade from black
    fi = seg(t, 0.0, 0.35)
    if fi < 1:
        black = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (1 - fi))))
        frame.alpha_composite(black)
    # riser zoom 22.6-24 + settle
    z = 1.0
    if 22.6 < t < 24.0:
        z = 1 + seg(t, 22.6, 24.0) * 0.035
    elif 24.0 <= t < 24.6:
        z = 1.035 - seg(t, 24.0, 24.6) * 0.035
    if abs(z - 1.0) > 0.0005:
        nw, nh = int(W * z), int(H * z)
        big = frame.resize((nw, nh), Image.BICUBIC)
        frame = big.crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
    return frame.convert("RGB")

def main():
    prerender()
    if "--preview" in sys.argv:
        idx = sys.argv.index("--preview")
        times = [float(x) for x in sys.argv[idx + 1:]]
        os.makedirs("work/preview", exist_ok=True)
        import time
        for tt in times:
            t0 = time.time()
            img = render_frame(tt)
            img.save(f"work/preview/t{tt:05.2f}.png")
            print(f"t={tt:5.2f} -> work/preview/t{tt:05.2f}.png  ({time.time()-t0:.1f}s)", flush=True)
    elif "--render" in sys.argv:
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-framerate", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
               "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", "work/video.mp4"]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import time
        t0 = time.time()
        for f in range(NFRAMES):
            tt = f / FPS
            img = render_frame(tt)
            p.stdin.write(img.tobytes())
            if f % 60 == 0:
                el = time.time() - t0
                print(f"frame {f}/{NFRAMES} ({el:.0f}s, eta {el/(f+1)*NFRAMES:.0f}s)", flush=True)
        p.stdin.close()
        p.wait()
        print("done work/video.mp4", flush=True)

if __name__ == "__main__":
    main()
