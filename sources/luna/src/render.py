#!/usr/bin/env python3
"""Reproducible T2S Tech motion graphics + original procedural score.

Run from the workspace root, with the render lock:
  flock /home/hermes/entregas/t2s-pods-model-comparison/render.lock python3 src/render.py
Optional quality-review stills: python3 src/render.py --preview
"""
from __future__ import annotations

import math
import subprocess
import sys
import time
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "final.mp4"
W, H, FPS, DURATION = 1920, 1080, 30, 30
FRAMES = FPS * DURATION
S = 2 / 3
IW, IH = round(W * S), round(H * S)
SR = 48000
WAV = ROOT / "src" / "original-score.wav"

# Exact T2S site palette and type families; colors sampled from supplied official CSS.
BG = (34, 38, 43)
PAPER = (246, 249, 251)
CYAN = (0, 180, 232)
BLUE = (50, 100, 255)
MUTED = (156, 172, 182)
HAIR = (87, 105, 119)
GREEN = (127, 203, 160)
FONT_DIR = ROOT / "input" / "fonts"
FONT_FILES = {
    "mont": FONT_DIR / "montserrat__Montserrat[wght].ttf",
    "rubik": FONT_DIR / "rubik__Rubik[wght].ttf",
}
LOGO_LIGHT = Image.open(ROOT / "src" / "t2s-logo-light.png").convert("RGBA")


def px(v: float) -> int:
    return int(round(v * S))


def box(b):
    return tuple(px(v) for v in b)


def mix(a, b, amount):
    q = max(0.0, min(1.0, amount))
    return tuple(round(a[i] * (1-q) + b[i] * q) for i in range(3))


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x*x*(3 - 2*x)


def out_cubic(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1-x)**3


def ease_out(x):
    return out_cubic(x)


def inout(x):
    x = max(0.0, min(1.0, x))
    return 4*x*x*x if x < .5 else 1 - ((-2*x+2)**3)/2


def out_back(x):
    x = max(0.0, min(1.0, x))
    c1, c3 = 1.12, 2.12
    return 1 + c3*(x-1)**3 + c1*(x-1)**2


def mix_motion(x0, x1, q):
    return x0 + (x1-x0)*q


@lru_cache(maxsize=96)
def font(family, size, weight):
    f = ImageFont.truetype(str(FONT_FILES[family]), max(1, px(size)))
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def T(d, x, y, value, size, color=PAPER, family="mont", weight=600,
      anchor="lt", tracking=0):
    f = font(family, size, weight)
    if not tracking:
        d.text((px(x), px(y)), value, font=f, fill=color, anchor=anchor)
        return
    advances = [d.textlength(c, font=f) for c in value]
    gap = px(tracking)
    total = sum(advances) + gap * max(0, len(value)-1)
    horizontal_anchor = anchor[0] if anchor else "l"
    if horizontal_anchor == "m":
        cursor = px(x) - total/2
    elif horizontal_anchor == "r":
        cursor = px(x) - total
    else:
        cursor = px(x)
    bbox = d.textbbox((0, 0), value, font=f, anchor="ls")
    baseline = px(y) - (bbox[1] + bbox[3]) / 2
    for c, advance in zip(value, advances):
        d.text((round(cursor), round(baseline)), c, font=f, fill=color, anchor="ls")
        cursor += advance + gap


def CT(d, x, y, value, size, color=PAPER, family="mont", weight=600, tracking=0):
    T(d, x, y, value, size, color, family, weight, "mm", tracking)


def line(d, points, color, width=2):
    d.line([(px(x), px(y)) for x, y in points], fill=color,
           width=max(1, px(width)), joint="curve")


def rounded(d, b, r, fill, outline=None, width=1):
    d.rounded_rectangle(box(b), radius=max(1, px(r)), fill=fill, outline=outline,
                        width=max(1, px(width)))


def circ(d, x, y, r, fill, outline=None, width=1):
    d.ellipse(box((x-r, y-r, x+r, y+r)), fill=fill, outline=outline,
              width=max(1, px(width)))


def poly(d, points, fill, outline=None, width=1):
    pts = [(px(x), px(y)) for x, y in points]
    d.polygon(pts, fill=fill)
    if outline:
        d.line(pts + [pts[0]], fill=outline, width=max(1, px(width)), joint="curve")


def background():
    yy, xx = np.mgrid[0:IH, 0:IW].astype(np.float32)
    x, y = xx/S, yy/S
    a = y/H
    rgb = np.empty((IH, IW, 3), dtype=np.float32)
    top = np.array([38, 44, 50], dtype=np.float32)
    bottom = np.array([29, 35, 41], dtype=np.float32)
    rgb[:] = top[None, None, :] * (1-a[..., None]) + bottom[None, None, :] * a[..., None]
    # Barely-there brand light pools and soft cinematic fall-off.
    for cx, cy, color, strength, radius in (
            (1420, 230, CYAN, .105, 850), (420, 850, BLUE, .047, 930)):
        r2 = ((x-cx)**2 + (y-cy)**2) / (radius*radius)
        k = (np.maximum(0, 1-r2)**2 * strength)[..., None]
        rgb += k * np.array(color, dtype=np.float32)[None, None, :]
    vignette = 1 - .105 * np.clip(((x-W/2)**2+(y-H/2)**2)/(1570**2), 0, 1)
    rgb *= vignette[..., None]
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(im)
    grid = mix(BG, (102, 122, 139), .095)
    # A restrained registration grid, not a simulated software screen.
    for x0 in range(120, W, 160):
        line(d, [(x0, 82), (x0, 998)], grid, 1)
    for y0 in range(112, 1000, 160):
        line(d, [(85, y0), (1835, y0)], mix(BG, (102, 122, 139), .07), 1)
    for x0, sign in ((88, 1), (1832, -1)):
        for y0, sy in ((86, 1), (994, -1)):
            c = mix(BG, CYAN, .40)
            line(d, [(x0, y0), (x0+sign*18, y0)], c, 1)
            line(d, [(x0, y0), (x0, y0+sy*18)], c, 1)
    return im


BASE = background()


def new_frame():
    return BASE.copy()


def card(d, cx, cy, w, h, eyebrow, detail, accent, alpha=1.0):
    back = mix(BG, (51, 61, 70), .84*alpha)
    edge = mix(BG, accent, .56*alpha)
    quiet = mix(BG, (201, 214, 222), .67*alpha)
    rounded(d, (cx-w/2, cy-h/2, cx+w/2, cy+h/2), 8, back, edge, 1)
    rounded(d, (cx-w/2+18, cy-h/2+16, cx-w/2+58, cy-h/2+20), 2,
            mix(BG, accent, .88*alpha))
    circ(d, cx+w/2-20, cy-h/2+20, 3.0, mix(BG, accent, .90*alpha))
    T(d, cx-w/2+18, cy-h/2+36, eyebrow, 14, quiet, "mont", 650, tracking=1.05)
    T(d, cx-w/2+18, cy-h/2+72, detail, 17, mix(BG, PAPER, .78*alpha), "rubik", 400)


def human_icon(d, x, y, color=CYAN, r=16):
    circ(d, x, y, r, BG, color, 2)
    circ(d, x, y-4, 3.6, color)
    d.arc(box((x-9, y-1, x+9, y+12)), start=195, end=345,
          fill=color, width=max(1, px(2)))


def agent_icon(d, x, y, color=BLUE, r=16):
    rounded(d, (x-r, y-r, x+r, y+r), 5, BG, color, 2)
    for j in range(3):
        circ(d, x-6+j*6, y, 2, color)


def checkpoint(d, x, y, label=None, alpha=1.0):
    fg = mix(BG, PAPER, alpha)
    cyan = mix(BG, CYAN, alpha)
    human_icon(d, x, y, fg, 15)
    if label:
        T(d, x+25, y-7, label, 14, cyan, "mont", 600)


def draw_opening(t):
    im = new_frame(); d = ImageDraw.Draw(im)
    # Kinetic type resolves from the value statement to a clean evidence-pod constellation.
    title_alpha = 1 - smooth((t-4.07)/.58)
    title1 = mix(BG, PAPER, title_alpha)
    title2 = mix(BG, CYAN, title_alpha)
    title_y = -12*(1-out_cubic(t/.36))
    T(d, 148, 169+title_y, "Mais horas", 82, title1, "mont", 700)
    T(d, 148, 269+title_y, "não resolvem tudo.", 82, title2, "mont", 700)
    brand=Image.open(ROOT/"src"/"t2s-logo-light.png").convert("RGBA")
    bw,bh=114,41
    brand=brand.resize((px(bw),px(bh)),Image.Resampling.LANCZOS)
    brand.putalpha(brand.getchannel("A").point(lambda v:int(v*.95*title_alpha)))
    im.alpha_composite(brand,(px(148),px(114)))
    d=ImageDraw.Draw(im)
    T(d, 152, 370+title_y, "ENGENHARIA DE ENTREGA   /   T2S TECH", 14,
      mix(BG, MUTED, title_alpha*.85), "mont", 650, tracking=1.5)
    T(d, 152, 403+title_y, "Capacidade certa. Trabalho organizado pelo resultado.", 20,
      mix(BG, PAPER, title_alpha*.80), "rubik", 400)
    # Unruly requests and dependencies magnetically align into one accountable flow.
    starts = [(252,548),(655,540),(1058,579),(1500,548),
              (1650,823),(1218,835),(708,824),(270,817)]
    ends   = [(288,575),(735,572),(1185,572),(1630,575),
              (1630,777),(1185,821),(735,821),(288,777)]
    items = [("ESCOPO","entender o sistema"),("ACESSO","API · dependências"),
             ("IDEIA","novo fluxo"),("PEDIDO","prazo / prioridade"),
             ("REVISÃO","decisões"),("QUALIDADE","testes"),
             ("RISCO","legado"),("ENTREGA","próximo incremento")]
    gather = smooth((t-2.22)/2.15)
    card_fade = 1-smooth((t-4.36)/.47)
    hub_fade = smooth((t-3.56)/.95)
    cx, cy = 960, 627
    for i, ((sx,sy),(ex,ey),(label,detail)) in enumerate(zip(starts, ends, items)):
        q = smooth((t-2.22-i*.035)/2.12)
        q = min(1, max(0, q))
        q = .94*q + .06*smooth((t-2.22-i*.035)/2.12)
        x = mix_motion(sx,ex,q); y = mix_motion(sy,ey,q)
        wobble = math.sin(t*8.3+i*2.2) * (1-q)*4
        x += wobble; y -= wobble*.45
        accent = CYAN if i%2==0 else BLUE
        # Connection lines progressively converge on an emerging, outcome-centred pod.
        endx = x + (cx-x)*hub_fade*.42
        endy = y + (cy-y)*hub_fade*.42
        line(d, [(x,y),(endx,endy)], mix(BG,accent,.30+.24*hub_fade), 1)
        if gather < .97 and card_fade > .02:
            card(d,x,y,258,116,label,detail,accent,card_fade)
    if hub_fade > .01:
        for rr, aa in ((118,.16),(94,.24),(73,.36)):
            circ(d,cx,cy,rr*hub_fade,BG,mix(BG,CYAN,aa*hub_fade),1)
        circ(d,cx,cy,48*hub_fade,mix(BG,(42,55,64),.8),mix(BG,CYAN,.76*hub_fade),2)
        if hub_fade > .55:
            CT(d,cx,cy,"RESULTADO",13,mix(BG,PAPER,.90*hub_fade),"mont",700,tracking=.8)
    # Brief claims resolve on a calm beat after the dispersed cards start to align.
    if t>3.12:
        a = smooth((t-3.12)/.36)*(1-smooth((t-4.30)/.38))
        CT(d,960,978,"Não contrate horas. Organize uma equipe em torno do resultado.",
           22,mix(BG,PAPER,.88*a),"rubik",450)
    return im


def draw_reveal(t):
    im = new_frame(); d = ImageDraw.Draw(im)
    p = out_cubic((t-5.0)/.55)
    a = p*(1-smooth((t-9.53)/.44))
    top = mix(BG,CYAN,.92*a)
    headline = mix(BG,PAPER,a)
    CT(d,960,112,"AI-Native Delivery Pods",64,headline,"mont",700)
    CT(d,960,190,"Uma equipe moldada pelo resultado.",29,
       mix(BG,MUTED,.98*a),"rubik",400)
    # Official site lockup replaces a separate text brand signature.
    brand=Image.open(ROOT/"src"/"t2s-logo-light.png").convert("RGBA")
    bw,bh=124,44
    brand=brand.resize((px(bw),px(bh)),Image.Resampling.LANCZOS)
    brand.putalpha(brand.getchannel("A").point(lambda v:int(v*.95*a)))
    im.alpha_composite(brand,(px(150),px(126)))
    d=ImageDraw.Draw(im)
    line(d,[(605,237),(1315,237)],mix(BG,CYAN,.58*a),2)

    cx,cy=960,581
    core_p=smooth((t-5.17)/.75)*(1-smooth((t-9.58)/.43))
    for rr,ratio in ((230,.13),(184,.23),(135,.36)):
        circ(d,cx,cy,rr*core_p,BG,mix(BG,CYAN,ratio*core_p),1)
    circ(d,cx,cy,103*core_p,mix(BG,(41,54,63),.87*core_p),
         mix(BG,CYAN,.78*core_p),2)
    if core_p>.3:
        CT(d,cx,cy-12,"EQUIPE",16,mix(BG,PAPER,.95*core_p),"mont",600,tracking=1.1)
        CT(d,cx,cy+19,"RESULTADO",23,mix(BG,PAPER,.98*core_p),"mont",700,tracking=.5)

    nodes=[(624,454,"ESPECIALISTAS","human",CYAN),
           (1296,454,"AGENTES DE IA","agent",BLUE),
           (624,728,"SUPERVISÃO","human",BLUE),
           (1296,728,"DECISÕES","human",CYAN)]
    for i,(x,y,label,kind,color) in enumerate(nodes):
        arrive=out_cubic((t-(5.30+i*.12))/.64)
        collapse=smooth((t-9.40)/.57)
        q=arrive*(1-.72*collapse)
        xx=mix_motion(cx,x,q); yy=mix_motion(cy,y,q)
        line(d,[(cx,cy),(xx,yy)],mix(BG,color,.38*q),1)
        if kind=="agent":agent_icon(d,xx,yy,color,20*q)
        else:human_icon(d,xx,yy,color,20*q)
        if t<9.42:
            CT(d,x,y+43,label,15,mix(BG,PAPER,.86*arrive*(1-smooth((t-9.18)/.28))),"mont",600,tracking=.9)
    # Decision checkpoints are explicit and on-route; they do not sit at the very end.
    for i,x in enumerate((811,1109)):
        appear=smooth((t-6.05-i*.62)/.44)*(1-smooth((t-9.38)/.35))
        circ(d,x,cy,19*appear,BG,mix(BG,PAPER,.88*appear),2)
        circ(d,x,cy-4*appear,4*appear,mix(BG,CYAN,.95*appear))
        d.arc(box((x-10*appear,cy-1*appear,x+10*appear,cy+13*appear)),195,345,
              fill=mix(BG,PAPER,.85*appear),width=max(1,px(2)))
        if appear>.1:
            CT(d,x,cy+40,"CHECKPOINT HUMANO",11,mix(BG,CYAN,.95*appear),"mont",650,tracking=.15)
    for i,(label,x,width,color) in enumerate([
            ("CAPACIDADE MENSAL",741,324,CYAN),("ETAPA FOCADA",1179,274,BLUE)]):
        q=out_cubic((t-7.00-i*.17)/.5)*(1-smooth((t-9.40)/.37))
        rounded(d,(x-width/2,887-24*(1-q),x+width/2,939-24*(1-q)),25,
                mix(BG,(43,53,61),.85*q),mix(BG,color,.75*q),1)
        circ(d,x-width/2+22,908-24*(1-q),4,mix(BG,color,.94*q))
        CT(d,x+5,908-24*(1-q),label,15,mix(BG,PAPER,.92*q),"mont",650,tracking=.8)
    return im


ROLE_DATA=[
    (350,408,"Prototyper",CYAN,"Explorar ideias","prototype"),
    (960,408,"Builder",BLUE,"Construir","build"),
    (1570,408,"Sweeper",CYAN,"Simplificar","simplify"),
    (650,744,"Grower",BLUE,"Evoluir","grow"),
    (1270,744,"Maintainer",CYAN,"Manter","maintain"),
]


def role_icon(d,x,y,kind,color,q=1):
    q=max(0,min(1,q)); co=mix(BG,color,.30+.67*q)
    if kind=="prototype":
        pts=[(x-28,y+11),(x-9,y-17),(x+17,y-10),(x+30,y+18),(x-2,y+27)]
        for j in range(len(pts)-1):
            r=ease_out((q-j*.10)/.62)
            p0,p1=pts[j],pts[j+1]
            line(d,[p0,(mix_motion(p0[0],p1[0],r),mix_motion(p0[1],p1[1],r))],co,2)
        line(d,[pts[-1],(x-28,y+11)],mix(BG,co,.84*q),1)
        for j,(xx,yy) in enumerate(pts):
            circ(d,xx,yy,3.5*q,mix(BG,color,.5+.48*q))
        circ(d,x,y-33,5*q,mix(BG,CYAN,.9*q))
    elif kind=="build":
        for j,w in enumerate((59,74,86)):
            p=ease_out((q-j*.16)/.72)
            yy=y+(j-1)*15
            rounded(d,(x-w*p/2,yy-5,x+w*p/2,yy+6),2,
                    mix(BG,color,.20*p),mix(BG,color,.83*p),1)
            circ(d,x-w*p/2+8*p,yy,2.2*p,mix(BG,color,.98*p))
    elif kind=="simplify":
        p=ease_out(q)
        for j,dy in enumerate((-19,0,19)):
            end=x-32+(18*j)
            line(d,[(x-37,y+dy),(end,y+dy)],mix(BG,color,.64*p),2)
            line(d,[(end,y+dy),(x+29,y)],mix(BG,color,.87*p),2)
        circ(d,x+32,y,4* p,mix(BG,color,.96*p))
    elif kind=="grow":
        points=[(x-32,y+25),(x-13,y+8),(x+2,y+11),(x+18,y-9),(x+36,y-29)]
        n=max(2,min(len(points),int(2+3*q)))
        line(d,points[:n],mix(BG,color,.90*q),3)
        poly(d,[(x+31,y-31),(x+44,y-28),(x+37,y-18)],mix(BG,color,.96*q))
        circ(d,x-29,y-27,7*q,BG,mix(BG,color,.72*q),2)
        line(d,[(x-37,y-27),(x-35,y-27)],mix(BG,color,.8*q),2)
    elif kind=="maintain":
        shape=[(x,y-34),(x+28,y-22),(x+24,y+9),(x,y+33),(x-24,y+9),(x-28,y-22)]
        poly(d,shape,mix(BG,(38,51,60),.6*q),mix(BG,color,.85*q),2)
        line(d,[(x-12,y),(x-3,y+10),(x+15,y-12)],mix(BG,color,.95*q),3)


def draw_roles(t):
    im=new_frame(); d=ImageDraw.Draw(im)
    incoming=smooth((t-10.0)/.45)
    outgoing=1-smooth((t-15.95)/.78)
    alpha=incoming*outgoing
    CT(d,960,133,"Especialistas + agentes supervisionados",40,
       mix(BG,PAPER,alpha),"mont",650)
    CT(d,960,207,"Cinco funções. Uma equipe organizada pelo resultado.",19,
       mix(BG,MUTED,.94*alpha),"rubik",400)

    yroute=568
    route=mix(BG,(121,145,158),.36*alpha)
    # A common pod spine connects five changing capabilities to two human decision gates.
    line(d,[(350,493),(350,yroute),(1570,yroute)],route,2)
    for x in (350,960,1570):
        line(d,[(x,yroute),(x,493)],route,2)
    for x in (650,1270):
        line(d,[(x,yroute),(x,655)],route,2)
        circ(d,x,yroute,4,mix(BG,CYAN,.9*alpha))
    for idx,(x,y,label,accent,action,kind) in enumerate(ROLE_DATA):
        start=10.38+idx*.74
        q=out_back((t-start)/.48)
        q=max(0,min(1.04,q))*outgoing
        if q<=0: continue
        w,h=448,178
        back=mix(BG,(48,58,67),.91*q)
        edge=mix(BG,accent,.78*q)
        rounded(d,(x-w/2,y-h/2,x+w/2,y+h/2),9,back,edge,1)
        rounded(d,(x-w/2+22,y-h/2+17,x-w/2+68,y-h/2+21),2,mix(BG,accent,.96*q))
        role_icon(d,x,y-37,kind,accent,q)
        CT(d,x,y+20,label,24,mix(BG,PAPER,q),"mont",650)
        CT(d,x,y+53,action,17,mix(BG,MUTED,.98*q),"rubik",400)
    for i,x in enumerate((650,1270)):
        q=smooth((t-(10.8+i*.68))/.46)*outgoing
        if q<=0: continue
        human_icon(d,x,yroute,mix(BG,PAPER,.95*q),17)
        CT(d,x,yroute+42,"Revisão humana" if i==0 else "Decisão humana",
           14,mix(BG,CYAN,.98*q),"mont",600)
    # Focused sign-off to the role constellation, set at a safer text size.
    foot=smooth((t-13.35)/.32)*outgoing
    CT(d,960,963,"O mix muda com o trabalho. A responsabilidade permanece clara.",
       20,mix(BG,PAPER,.99*foot),"rubik",500)
    return im


def artifact_card(d,x,y,w,h,title,accent):
    rounded(d,(x-w/2,y-h/2,x+w/2,y+h/2),8,mix(BG,(47,57,66),.84),
            mix(BG,accent,.59),1)
    rounded(d,(x-w/2+22,y-h/2+18,x-w/2+61,y-h/2+22),2,
            mix(BG,accent,.91))
    T(d,x-w/2+23,y-h/2+38,title,20,PAPER,"mont",650)


def draw_flow(t):
    im=new_frame(); d=ImageDraw.Draw(im)
    xs=[350,960,1570]; y=311
    titles=["Contexto","Entrega","Qualidade"]
    subs=["entender antes de propor", "incrementos demonstráveis",
          "testes, revisão e evidências"]
    stage_alpha=out_cubic((t-16.34)/.72)*(1-smooth((t-23.70)/.43))
    claim=smooth((t-16.34)/.48)*(1-smooth((t-23.72)/.30))
    CT(d,960,109,"Progresso visível. Responsabilidade clara.",36,
       mix(BG,PAPER,.99*claim),"mont",650)
    if t<17.24:
        old=smooth((t-16.08)/.35)*(1-smooth((t-16.93)/.30))
        CT(d,960,177,"Especialistas + agentes supervisionados",26,
           mix(BG,MUTED,.92*old),"rubik",450)
    stage_reveal=[out_cubic((t-16.30-i*.23)/.48) for i in range(3)]
    stage_entrance=min(stage_reveal)
    for i,(x,title,sub) in enumerate(zip(xs,titles,subs)):
        reveal=stage_reveal[i]
        width,height=394,102
        q=stage_alpha*reveal
        accent=CYAN if i!=1 else BLUE
        rounded(d,(x-width/2,y-height/2,x+width/2,y+height/2),7,
                mix(BG,(47,57,66),.86*q),mix(BG,accent,.75*q),1)
        circ(d,x-width/2+28,y,5,mix(BG,accent,.96*q))
        T(d,x-width/2+49,y-25,title,27,mix(BG,PAPER,q),"mont",650)
        T(d,x-width/2+49,y+13,sub,14,mix(BG,MUTED,.97*q),"rubik",400)

    # A restrained editorial rule makes the workflow read as one directed sequence.
    for xa,xb in ((552,763),(1157,1368)):
        line(d,[(xa,y),(xb,y)],mix(BG,(116,141,154),.55*stage_alpha),2)
        line(d,[(xb-11,y-7),(xb,y),(xb-11,y+7)],mix(BG,CYAN,.92*stage_alpha),2)
    # Two explicit decision moments stay visible between the linked stages.
    gate=smooth((t-16.80)/.50)*(1-smooth((t-23.70)/.35))
    for x,label in ((763,"Revisão humana"),(1368,"Decisão humana")):
        human_icon(d,x,410,mix(BG,PAPER,.96*gate),14)
        CT(d,x,445,label,12,mix(BG,CYAN,.97*gate),"mont",600)
        line(d,[(x,464),(x,491)],mix(BG,(113,134,148),.50*gate),1)

    # Conceptual artifact panels are introduced by a short staggered vertical lift.
    artifact_alpha=smooth((t-17.18)/.44)*(1-smooth((t-23.68)/.34))
    panel_stagger=(.00,.13,.26)
    artifact_titles=["Protótipo","Incremento de software","Teste + revisão"]
    evidence=[("CONTEXTO","premissas e decisões"),
              ("ENTREGA","incremento demonstrável"),
              ("QUALIDADE","testes · revisão · operação")]
    for i,x in enumerate(xs):
        q=out_cubic((t-17.10-panel_stagger[i])/.47)*(1-smooth((t-23.68)/.34))
        accent=CYAN if i!=1 else BLUE
        # Cards enter from below, overshoot softly, and settle on the same baseline.
        lift=44*(1-out_back((t-17.10-panel_stagger[i])/.54))
        top=522+lift
        x0,x1=x-223,x+223; y0,y1=top,top+222
        rounded(d,(x0,y0,x1,y1),8,mix(BG,(44,54,63),.94*q),
                mix(BG,(102,124,138),.52*q),1)
        rounded(d,(x0+20,y0+18,x0+63,y0+22),2,mix(BG,accent,.76*q))
        T(d,x0+24,top+37,artifact_titles[i],18,mix(BG,PAPER,.95*q),"mont",650)
        if i==0:
            py=top+111
            pts=[(x-137,py+35),(x-78,py-9),(x-12,py+12),(x+54,py-34),(x+123,py-7)]
            line(d,pts,mix(BG,PAPER,.74*q),2)
            for xx,yy in pts:circ(d,xx,yy,4,mix(BG,CYAN,.94*q))
            line(d,[(x-137,py+56),(x+127,py+56)],mix(BG,CYAN,.37*q),1)
        elif i==1:
            py=top+82
            for j,bw in enumerate((181,221,158,201)):
                yy=py+j*24
                rounded(d,(x-106,yy,x-106+bw,yy+11),3,
                        mix(BG,BLUE,.20*q),mix(BG,BLUE,.78*q),1)
                circ(d,x+111,yy+5.5,2.5,mix(BG,BLUE,.94*q))
        else:
            py=top+82
            for j,label in enumerate(("Testes","Revisão humana","Evidência operacional")):
                yy=py+j*31
                circ(d,x0+27,yy+8,6,mix(BG,(49,59,67),.92*q),mix(BG,CYAN,.72*q),1)
                circ(d,x0+27,yy+8,2,mix(BG,CYAN,.91*q))
                T(d,x0+43,yy,label,15,mix(BG,PAPER,.94*q),"rubik",400)
        # A fine stem aligns each panel with its matching process stage.
        line(d,[(x,464),(x,top)],mix(BG,(109,128,142),.42*q),1)
        # Evidence labels are a compact second reading line, not a numeric dashboard.
        eyebrow,detail=evidence[i]
        yev=858
        ev=smooth((t-18.30-.12*i)/.44)*(1-smooth((t-23.70)/.32))
        rounded(d,(x-215,yev+21,x+215,yev+84),5,
                mix(BG,(43,53,61),.92*ev),mix(BG,(114,137,151),.45*ev),1)
        T(d,x-198,yev+31,eyebrow,12,mix(BG,CYAN,.97*ev),"mont",700,tracking=.55)
        T(d,x-198,yev+52,detail,16,mix(BG,PAPER,.91*ev),"rubik",400)

    # A single family of work tokens glides through all three stages and changes form.
    progress=inout((t-18.02)/5.15)
    lane_alpha=smooth((t-17.78)/.35)*(1-smooth((t-23.67)/.34))
    line(d,[(246,476),(1674,476)],mix(BG,(97,121,136),.52*lane_alpha),1)
    fx=mix_motion(252,1668,progress); fy=476
    circ(d,fx,fy,20,mix(BG,CYAN,.11*lane_alpha),mix(BG,CYAN,.63*lane_alpha),1)
    rounded(d,(fx-16,fy-12,fx+16,fy+12),3,
            mix(BG,(45,56,64),.94*lane_alpha),mix(BG,CYAN,.80*lane_alpha),1)
    if progress<.38:
        for ox,oy in ((-8,0),(0,-4),(8,3)):
            circ(d,fx+ox,fy+oy,2.4,mix(BG,CYAN,.96*lane_alpha))
        line(d,[(fx-8,fy),(fx,fy-4),(fx+8,fy+3)],mix(BG,PAPER,.80*lane_alpha),1)
    elif progress<.72:
        for j,bw in enumerate((13,19,11)):
            rounded(d,(fx-8,fy-6+j*5,fx-8+bw,fy-3+j*5),1,
                    mix(BG,BLUE,.88*lane_alpha),mix(BG,BLUE,.94*lane_alpha),1)
    else:
        human_icon(d,fx,fy,mix(BG,PAPER,.94*lane_alpha),11)

    # Ends on documented context/delivery/quality evidence; no invented metrics.
    line(d,[(267,858),(1655,858)],mix(BG,HAIR,.78*artifact_alpha),1)
    return im

def draw_end(t):
    im=new_frame(); d=ImageDraw.Draw(im)
    intro=out_cubic((t-23.90)/.75)
    # Flow rails converge into a quiet signature and the supplied exact official T2S lockup.
    reveal=smooth((t-24.04)/.72)
    line(d,[(472,254),(1448,254)],mix(BG,CYAN,.77*intro),2)
    logo_h=208
    ratio=1082.4330708661416/386.755905511811
    logo_w=logo_h*ratio
    logo=LOGO_LIGHT.resize((px(logo_w),px(logo_h)),Image.Resampling.LANCZOS)
    logo.putalpha(logo.getchannel("A").point(lambda v:int(v*reveal)))
    lx,ly=960-logo_w/2,304+24*(1-intro)
    im.alpha_composite(logo,(px(lx),px(ly)))
    d=ImageDraw.Draw(im)
    CT(d,960,571+15*(1-intro),"AI-Native Delivery Pods",43,
       mix(BG,PAPER,.99*intro),"mont",650)
    bq=out_cubic((t-25.0)/.55)
    rounded(d,(702,649,1218,721),4,mix(BG,BLUE,.94*bq),mix(BG,BLUE,.96*bq),1)
    CT(d,960,685,"Converse com um engenheiro.",21,
       mix(BG,PAPER,bq),"mont",650)
    CT(d,960,790,"t2stech.com",25,mix(BG,MUTED,.98*bq),"mont",600,tracking=1.2)
    # Stillness, generous contrast and central alignment hold comfortably for the final seconds.
    if 25.0<t<26.6:
        q=smooth((t-25.0)/1.6)
        line(d,[(630,870),(1290,870)],mix(BG,PAPER,.10*q),1)
    return im


def make_frame(t):
    if t < 5.0:
        return draw_opening(t)
    if t < 10.0:
        return draw_reveal(t)
    if t < 17.0:
        return draw_roles(t)
    if t < 24.0:
        return draw_flow(t)
    return draw_end(t)


def render_preview():
    folder=ROOT/"output"/"review-frames"
    folder.mkdir(parents=True,exist_ok=True)
    times=(2.50,7.50,13.95,20.50,27.50)
    for t in times:
        image=make_frame(t).resize((W,H),Image.Resampling.LANCZOS)
        path=folder/f"frame-{t:05.2f}s.png"
        image.save(path,optimize=True)
        print(f"[preview] {t:.2f}s -> {path}")


def midi(note):
    return 440.0*2.0**((note-69)/12.0)


def write_score(path):
    """Synthesize and write an original 120-BPM instrumental, with no source samples."""
    n=SR*DURATION
    left=np.zeros(n,dtype=np.float32)
    right=np.zeros(n,dtype=np.float32)
    rng=np.random.default_rng(8231)

    def event(start_s,duration,freq,amp,channel="both",decay=None,partials=.12):
        start=max(0,int(round(start_s*SR)))
        end=min(n,start+int(round(duration*SR)))
        if end<=start:return
        tt=np.arange(end-start,dtype=np.float32)/SR
        tau=decay if decay is not None else max(.10,duration*.48)
        env=np.minimum(1,tt/.018).astype(np.float32)*np.exp(-tt/tau)
        tail=min(len(tt),int(SR*.055))
        if tail>0 and len(tt)>tail:
            env[-tail:]*=np.linspace(1,0,tail,dtype=np.float32)**1.5
        phase=2*np.pi*freq*tt
        sig=amp*env*(np.sin(phase)+partials*np.sin(phase*2+.31)+.035*np.sin(phase*3+.72))
        if channel in ("left","both"):left[start:end]+=sig
        if channel in ("right","both"):right[start:end]+=sig

    def pad(start_s,duration,freq,amp,channel,phase=0):
        start=int(round(start_s*SR)); end=min(n,start+int(round(duration*SR)))
        if end<=start:return
        tt=np.arange(end-start,dtype=np.float32)/SR
        attack=np.minimum(1,tt/.60)
        env=attack.astype(np.float32)
        rel=min(len(tt),int(SR*.62))
        if rel>0 and len(tt)>rel:
            env[-rel:]*=np.linspace(1,0,rel,dtype=np.float32)**1.5
        chorus=.17*np.sin(2*np.pi*.09*tt+phase)+.07*np.sin(2*np.pi*.051*tt+phase+.6)
        sig=amp*env*(np.sin(2*np.pi*freq*tt+chorus)+
                     .28*np.sin(4*np.pi*freq*tt+chorus+.38)+
                     .075*np.sin(6*np.pi*freq*tt+chorus+.9))
        if channel=="left":left[start:end]+=sig.astype(np.float32)
        else:right[start:end]+=sig.astype(np.float32)

    # Four warm, restrained major/minor ninth voicings cycle over an original 120 BPM pulse.
    chord_specs=[(0,[50,54,57,61,64]),(4,[47,50,54,57,62]),
                 (8,[43,47,50,54,57]),(12,[45,49,52,55,59]),
                 (16,[50,54,57,61,64]),(20,[47,50,54,57,62]),
                 (24,[43,47,50,54,57]),(28,[45,49,52,55,57])]
    for start,notes in chord_specs:
        length=min(4.25,DURATION-start)
        for i,note in enumerate(notes):
            f=midi(note)
            pad(start,length,f,.020 if i%2==0 else .015,"left",i*.19)
            pad(start+.023,length,f*1.0011,.020 if i%2 else .015,"right",i*.23+.4)
        event(start,1.05,midi(notes[0]-12),.074,decay=.42,partials=.08)

    beat=.5
    roots=[38,35,31,33]
    melody=[62,66,69,73,76,73,69,66,62,66,71,74,78,74,71,66,
            62,66,69,73,76,73,69,66,64,67,71,74,76,74,71,67]
    for b in range(int(DURATION/beat)):
        t=b*beat
        chord=min(7,int(t//4))
        if b%2==0:
            note=roots[min(3,chord%4)]
            # soft, subby kick/bass composite; spaced every downbeat of each second bar.
            start=int(t*SR); span=int(.20*SR); end=min(n,start+span)
            if end>start:
                tt=np.arange(end-start,dtype=np.float32)/SR
                kick=.108*np.exp(-tt*21)*np.sin(2*np.pi*(58-17*tt)*tt)
                left[start:end]+=kick; right[start:end]+=kick
            event(t,.45,midi(note),.087,decay=.22,partials=.035)
        # A rounded, warm bell-like pluck; the offset echo is another synthesized note.
        idx=(b+3*(b//8))%len(melody)
        m=melody[idx]+(12 if 8<=t<14 or 22<=t<28 else 0)
        amp=.076 if b%2==0 else .053
        event(t+.015,.49,midi(m),amp,"left",decay=.23,partials=.23)
        event(t+.060,.43,midi(m)*1.001,.032,"right",decay=.22,partials=.18)
        # A very quiet, muted rim pulse gives the sections definition without EDM impacts.
        if b%4==2:
            start=int((t+.004)*SR); length=min(int(.095*SR),n-start)
            if length>0:
                tt=np.arange(length,dtype=np.float32)/SR
                noise=rng.standard_normal(length).astype(np.float32)
                smooth_noise=np.convolve(noise,np.ones(21,dtype=np.float32)/21,mode="same")
                hit=.0065*np.exp(-tt*37)*smooth_noise
                left[start:start+length]+=hit; right[start:start+length]+=hit

    # Brief, musical sine chimes underscore alignment, human gates and the clean logo resolve.
    for t,note,amp in ((4.5,81,.027),(5.0,86,.035),(7.5,81,.021),
                       (10.5,83,.025),(12.0,86,.022),(13.5,81,.019),
                       (17.0,86,.030),(19.0,83,.022),(21.5,86,.021),
                       (24.0,86,.035),(26.5,81,.019)):
        event(t,.20,midi(note),amp,"both",decay=.12,partials=.11)
    # Final subtle wide fade; no accidental audio-pop at either edge.
    fade=int(SR*.85)
    ramp=np.linspace(0,1,fade,dtype=np.float32)**1.3
    left[:fade]*=ramp; right[:fade]*=ramp
    ramp=np.linspace(1,0,fade,dtype=np.float32)**1.5
    left[-fade:]*=ramp; right[-fade:]*=ramp
    peak=float(max(np.max(np.abs(left)),np.max(np.abs(right))))
    if peak>0.80:
        left*=.78/peak; right*=.78/peak
    stereo=np.stack((left,right),axis=1)
    pcm=np.clip(stereo*32767,-32768,32767).astype("<i2")
    with wave.open(str(path),"wb") as wav:
        wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(SR)
        wav.writeframes(pcm.tobytes())
    print(f"[audio] original synthesized score: {path}, peak={peak:.3f}",flush=True)


def render_video():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if not WAV.exists():
        write_score(WAV)
    command=["ffmpeg","-hide_banner","-loglevel","warning","-y",
      "-f","rawvideo","-pixel_format","rgb24","-video_size",f"{IW}x{IH}",
      "-framerate",str(FPS),"-i","pipe:0","-i",str(WAV),
      "-map","0:v:0","-map","1:a:0","-vf",f"scale={W}:{H}:flags=lanczos,setsar=1",
      "-frames:v",str(FRAMES),"-c:v","libx264","-preset","faster","-crf","17",
      "-pix_fmt","yuv420p","-threads","1","-filter_threads","1",
      "-c:a","aac","-b:a","192k","-ar",str(SR),"-t","30",
      "-movflags","+faststart","-metadata","title=T2S Tech — AI-Native Delivery Pods",
      "-metadata","artist=T2S Tech",
      "-metadata","comment=Original programmatic motion graphics and synthesized instrumental score",
      str(OUT)]
    print(f"[render] {FRAMES} frames · {W}x{H} · {FPS} fps · 30 seconds",flush=True)
    start=time.monotonic()
    encoder=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for i in range(FRAMES):
            frame=make_frame(i/FPS).convert("RGB")
            encoder.stdin.write(frame.tobytes())
            if i%60==0:
                print(f"[render] {i:03}/{FRAMES}  {i/FPS:05.1f}s",flush=True)
        encoder.stdin.close()
        status=encoder.wait()
    except BaseException:
        encoder.kill(); encoder.wait(); raise
    if status!=0:
        raise RuntimeError(f"ffmpeg exited with status {status}")
    print(f"[render] complete in {time.monotonic()-start:.1f}s: {OUT}",flush=True)


if __name__=="__main__":
    if len(sys.argv)>1 and sys.argv[1]=="--preview":
        render_preview()
    elif len(sys.argv)>1:
        raise SystemExit("Usage: python3 src/render.py [--preview]")
    else:
        render_video()
