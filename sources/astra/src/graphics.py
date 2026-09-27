"""Deterministic Skia vector compositor. Text is shaped from the supplied fonts."""
from pathlib import Path
from functools import lru_cache
from math import sin, cos, pi, hypot
import bootstrap
import skia
import uharfbuzz as hb

ROOT=Path(__file__).resolve().parents[1]
W,H=1920,1080
INK='#22262b'; PAPER='#f6f9fb'; WHITE='#ffffff'; CYAN='#00b4e8'; BLUE='#3264ff'
PALE='#eaf7fc'; MUTED='#65717c'; HAIR='#cbd6de'; DEEP='#1e46bd'

def clamp(v,a=0,b=1): return max(a,min(b,v))
def progress(t,a,b): return clamp((t-a)/(b-a))
def ease(v):
    v=clamp(v); return v*v*v*(v*(v*6-15)+10)
def eo(v): return 1-(1-clamp(v))**3
def back(v):
    v=clamp(v)-1; return 1+1.62*v*v*v+.62*v*v

def lerp(a,b,p): return a+(b-a)*p
def mix(a,b,p): return tuple(lerp(x,y,p) for x,y in zip(a,b))
def rgb(c):
    if isinstance(c,str): return tuple(int(c[i:i+2],16) for i in (1,3,5))
    return c[:3]
def cmix(a,b,p): return tuple(round(lerp(x,y,p)) for x,y in zip(rgb(a),rgb(b)))
def color(c,alpha=1):
    r,g,b=rgb(c); return skia.ColorSetARGB(round(255*clamp(alpha)),round(r),round(g),round(b))

def paint(c=WHITE,a=1,width=0,dash=None):
    p=skia.Paint(AntiAlias=True,Color=color(c,a))
    if width:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(width)
        p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if dash: p.setPathEffect(skia.DashPathEffect.Make(dash[0],dash[1]))
    return p

@lru_cache(None)
def typeface(family,weight): return skia.Typeface.MakeFromFile(str(ROOT/'build/fonts'/f'{family}-{weight}.ttf'))
@lru_cache(None)
def hbfont(family,weight):
    data=(ROOT/'build/fonts'/f'{family}-{weight}.ttf').read_bytes()
    face=hb.Face(data); f=hb.Font(face); f.scale=(face.upem,face.upem)
    return f,face.upem

@lru_cache(8192)
def shape(txt,size,family='montserrat',weight=600,tracking=-.035):
    hf,upem=hbfont(family,weight)
    buf=hb.Buffer(); buf.add_str(txt); buf.guess_segment_properties()
    hb.shape(hf,buf,{'kern':True,'liga':True})
    font=skia.Font(typeface(family,weight),size)
    font.setEdging(skia.Font.Edging.kAntiAlias); font.setSubpixel(True)
    glyphs=[]; pos=[]; x=0
    for info,p in zip(buf.glyph_infos,buf.glyph_positions):
        glyphs.append(info.codepoint)
        pos.append(skia.Point(x+p.x_offset*size/upem,-p.y_offset*size/upem))
        x+=p.x_advance*size/upem+tracking*size
    if glyphs: x-=tracking*size
    bounds=skia.Rect.MakeEmpty()
    for gb,pt in zip(font.getBounds(glyphs),pos):
        gb.offset(pt.x(),pt.y());bounds.join(gb)
    tb=skia.TextBlobBuilder(); tb.allocRunPos(font,glyphs,pos,bounds)
    blob=tb.make()
    return blob,x

LOGOS={k:skia.SVGDOM.MakeFromStream(skia.MemoryStream.MakeFromFile(str(ROOT/f'input/assets/assets__t2s-logo-{k}.svg'))) for k in ['light','dark']}
for dom in LOGOS.values():
    dom.setContainerSize(skia.Size(1082.4330708661416,386.755905511811))

class G:
    def __init__(self,canvas,audit=False):
        self.c=canvas; self.audit=audit; self.bounds=[]
    def line(self,points,c=WHITE,a=1,width=2,dash=None,part=1):
        if a<=0 or part<=0 or len(points)<2:return
        p=skia.Path();p.moveTo(*points[0])
        for pt in points[1:]:p.lineTo(*pt)
        self.path(p,c,a,width,dash,part)
    def path(self,p,c=WHITE,a=1,width=0,dash=None,part=1):
        if a<=0 or part<=0:return
        if part<1:
            pm=skia.PathMeasure(p,False); out=skia.Path()
            pm.getSegment(0,pm.getLength()*clamp(part),out,True);p=out
        self.c.drawPath(p,paint(c,a,width,dash))
    def curve(self,pts,c=WHITE,a=1,width=2,part=1,dash=None):
        p=skia.Path();p.moveTo(*pts[0]);p.cubicTo(*pts[1],*pts[2],*pts[3]);self.path(p,c,a,width,dash,part)
    def rect(self,x,y,w,h,c=WHITE,a=1,r=0,stroke=0):
        if a<=0 or w<=0 or h<=0:return
        rect=skia.Rect.MakeXYWH(x,y,w,h)
        if r:self.c.drawRoundRect(rect,r,r,paint(c,a,stroke))
        else:self.c.drawRect(rect,paint(c,a,stroke))
    def circle(self,x,y,r,c=WHITE,a=1,stroke=0):
        if r>0 and a>0:self.c.drawCircle(x,y,r,paint(c,a,stroke))
    def arc(self,x,y,r,start,sweep,c=WHITE,a=1,width=2):
        if a>0:self.c.drawArc(skia.Rect.MakeLTRB(x-r,y-r,x+r,y+r),start,sweep,False,paint(c,a,width))
    def text(self,txt,x,y,size=40,c=WHITE,a=1,family='montserrat',weight=600,tracking=-.035,align='left',reveal=1,maxwidth=None,audit=True):
        if a<=0 or reveal<=0:return 0
        blob,w=shape(txt,size,family,weight,tracking)
        if maxwidth and w>maxwidth:
            size*=maxwidth/w;blob,w=shape(txt,size,family,weight,tracking)
        xx=x-w/2 if align=='center' else x-w if align=='right' else x
        self.c.save()
        if reveal<1:
            self.c.clipRect(skia.Rect.MakeLTRB(xx-8,y-size*1.2,xx+w+10,y+size*.28))
            self.c.translate(0,size*1.4*(1-eo(reveal)))
        self.c.drawTextBlob(blob,xx,y,paint(c,a))
        self.c.restore()
        if self.audit and audit and reveal>=.99 and a>=.9:
            b=blob.bounds()
            local=skia.Rect.MakeLTRB(xx+b.left(),y+b.top(),xx+b.right(),y+b.bottom())
            bb=self.c.getTotalMatrix().mapRect(local)
            self.bounds.append({'text':txt,'x':round(bb.left(),2),'y':round(bb.top(),2),'right':round(bb.right(),2),'bottom':round(bb.bottom(),2),'size':round(size,2)})
        return w
    def small(self,txt,x,y,c=WHITE,a=1,align='left',size=20):
        return self.text(txt,x,y,size,c,a,weight=700,tracking=.13,align=align)
    def logo(self,x,y,w,variant='light',a=1):
        if a<=0:return
        self.c.saveLayer(None,paint(WHITE,a));self.c.translate(x,y);self.c.scale(w/1082.4330708661416,w/1082.4330708661416)
        LOGOS[variant].render(self.c);self.c.restore()
    def shadow(self,x,y,w,h,r=8,a=.13):
        p=paint(INK,a);p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.BlurStyle.kNormal_BlurStyle,12))
        self.c.drawRoundRect(skia.Rect.MakeXYWH(x,y+12,w,h),r,r,p)
    def arrow(self,x,y,length=46,c=WHITE,a=1,width=3):
        self.line([(x-length/2,y),(x+length/2,y)],c,a,width)
        self.line([(x+length/2-10,y-10),(x+length/2,y),(x+length/2-10,y+10)],c,a,width)
    def check(self,x,y,s=1,c=WHITE,a=1,p=1):
        self.line([(x-10*s,y),(x-3*s,y+7*s),(x+12*s,y-9*s)],c,a,3*s,part=p)
    def human(self,x,y,r=30,c=WHITE,a=1,fill=None,check=0):
        if fill:self.circle(x,y,r,fill,a)
        self.circle(x,y,r,c,a,2)
        self.circle(x,y-r*.18,r*.19,c,a,2)
        p=skia.Path();p.moveTo(x-r*.38,y+r*.34);p.cubicTo(x-r*.38,y-r*.02,x+r*.38,y-r*.02,x+r*.38,y+r*.34)
        self.path(p,c,a,2)
        if check:
            self.circle(x+r*.73,y+r*.65,r*.39,CYAN,a)
            self.check(x+r*.73,y+r*.65,r/54,WHITE,a,check)
    def agent(self,x,y,r=28,c=CYAN,a=1,fill=None):
        self.c.save();self.c.translate(x,y);self.c.rotate(45)
        if fill:self.rect(-r*.74,-r*.74,1.48*r,1.48*r,fill,a,5)
        self.rect(-r*.74,-r*.74,1.48*r,1.48*r,c,a,5,2)
        self.rect(-r*.25,-r*.25,r*.5,r*.5,c,a,2)
        for z in [-1,1]:
            self.line([(z*r*.45,-r*.1),(z*r*.45,r*.1)],c,a,2)
            self.line([(-r*.1,z*r*.45),(r*.1,z*r*.45)],c,a,2)
        self.c.restore()
    def diamond(self,x,y,r,c=CYAN,a=1,stroke=0):
        p=skia.Path();p.moveTo(x,y-r);p.lineTo(x+r,y);p.lineTo(x,y+r);p.lineTo(x-r,y);p.close();self.path(p,c,a,stroke)

def bezier(a,b,c,d,p):
    q=1-p;return (q*q*q*a[0]+3*q*q*p*b[0]+3*q*p*p*c[0]+p*p*p*d[0],q*q*q*a[1]+3*q*q*p*b[1]+3*q*p*p*c[1]+p*p*p*d[1])
