"""T2S / Outcome is the organizing principle. A continuous 30-second composition.
No screenshots or stock interface assets are used in this compositor.
All timing is in seconds on a 120 BPM score; the last 3 seconds are a true hold.
"""
from graphics import *

ROLES=['Prototyper','Builder','Sweeper','Grower','Maintainer']
VERBS=['explorar ideias','construir','simplificar','evoluir','manter']
ROLE_X=[280,620,960,1300,1640]
CARD_COLORS=['#2454e8',BLUE,'#2b5bec','#2856df','#1e49cc']
DEMANDS=['Nova ideia','Integração','Dependência','Legado','Prioridade','Operação']
STARTS=[(263,665,-9),(682,584,7),(1065,730,-6),(1560,492,8),(1590,850,-5),(641,899,5)]
HUB=(1370,577)
NODES=[(1370+267*cos((-90+i*60)*pi/180),577+267*sin((-90+i*60)*pi/180)) for i in range(6)]


def header(g,t,dark=True,a=1):
    if a<=0:return
    c=WHITE if dark else INK
    g.logo(104,63,151,'light' if dark else 'dark',a)
    g.small('AI-NATIVE DELIVERY PODS',1816,101,c,.62*a,align='right',size=17)
    g.line([(104,141),(1816,141)],c,.10*a,1)


def demand_pose(t,i):
    x,y,ang=STARTS[i]
    q=ease(progress(t,2.7+i*.085,4.12+i*.07))
    # An anticipatory counter-shift creates mass before alignment.
    anti=sin(pi*progress(t,2.42+i*.045,2.82+i*.045))*9 if t<2.82+i*.045 else 0
    x-=anti
    x=lerp(x,277+i*273,q);y=lerp(y,701,q);ang=lerp(ang,0,q)
    w=lerp(304,232,q);h=lerp(130,112,q)
    k=back(progress(t,4.08+i*.07,5.55+i*.035))
    x=lerp(x,NODES[i][0],k);y=lerp(y,NODES[i][1],k)
    w=lerp(w,78,k);h=lerp(h,78,k)
    return x,y,ang,w,h,clamp(k)


def core(g,t,a=1):
    p=eo(progress(t,4.62,5.52))
    if p<=0:return
    x,y=HUB;r=122*p
    g.circle(x,y,171*p,BLUE,.055*a)
    g.circle(x,y,151*p,CYAN,.10*a,1)
    g.circle(x,y,r,BLUE,.20*a)
    g.circle(x,y,r,CYAN,.77*a,1.6)
    g.arc(x,y,163*p,-120,250*eo(progress(t,5.15,6.2)),CYAN,.7*a,3)
    g.arc(x,y,163*p,153,67*eo(progress(t,5.15,6.2)),BLUE,a,3)
    for i in range(4):
        ang=(-90+i*90)*pi/180
        xx=x+122*cos(ang); yy=y+122*sin(ang)
        g.circle(xx,yy,4,WHITE,.85*a)
    g.circle(x,y-26,23,CYAN,.95*a,2)
    g.circle(x,y-26,7,CYAN,a)
    g.line([(x-36,y-26),(x-29,y-26)],CYAN,a,2)
    g.line([(x+29,y-26),(x+36,y-26)],CYAN,a,2)
    g.line([(x,y-62),(x,y-55)],CYAN,a,2)
    g.small('RESULTADO',x,y+32,WHITE,a*p,align='center',size=19)


def opening(g,t):
    # Demand cards remain the same objects while they change scale and topology.
    active=1-ease(progress(t,9.25,9.93))
    titleout=1-ease(progress(t,3.86,4.65))
    g.small('ENTRE DEMANDAS E DEPENDÊNCIAS',113,215,CYAN,titleout, size=18)
    g.text('Mais horas',105,351,123,WHITE,titleout,weight=600,tracking=-.064,reveal=progress(t,.06,.76))
    g.text('não resolvem tudo.',105,481,123,WHITE,titleout,weight=600,tracking=-.064,reveal=progress(t,.35,1.06))
    # Underline tracks the last word, then becomes the first connection.
    g.line([(106,523),(106+680*eo(progress(t,.85,1.65)),523)],CYAN,.74*titleout,3)
    poses=[demand_pose(t,i) for i in range(6)]
    for i,j in [(0,1),(1,3),(0,5),(5,2),(2,4),(3,4),(1,2)]:
        x,y,_,_,_,k=poses[i];xx,yy,*_=poses[j]
        m=1-ease(progress(t,4.15,5.42))
        pts=[(x,y),(lerp(x,xx,.45),y-88),(lerp(x,xx,.55),yy+88),(xx,yy)]
        g.curve(pts,HAIR,.25*active*m,1.3,dash=([5,10],-t*11))
    p=eo(progress(t,4.60,5.65))
    for i,(x,y,_,_,_,k) in enumerate(poses):
        if k>0:
            g.line([HUB,(x,y)],CYAN,.25*active*k,1.4)
            start=5.8+i*.38
            pulse=progress(t,start,start+.65)
            if 0<pulse<1:
                px,py=mix((x,y),HUB,ease(pulse))
                g.circle(px,py,4.5,CYAN,active)
    core(g,t,active)
    for i,(x,y,ang,w,h,k) in enumerate(poses):
        arrival=eo(progress(t,.04+i*.08,.72+i*.08))
        g.c.save();g.c.translate(x,y+24*(1-arrival));g.c.rotate(ang)
        fill=cmix(INK,BLUE,.08+.24*k)
        g.rect(-w/2,-h/2,w,h,fill,active*arrival,lerp(3,39 if i%2==0 else 12,k))
        g.rect(-w/2,-h/2,w,h,cmix(HAIR,CYAN,k),active*arrival*(.42+.4*k),lerp(3,39 if i%2==0 else 12,k),1.5)
        tx=-w/2+22
        la=1-ease(progress(t,4.18+i*.07,4.9+i*.07))
        g.small('DEMANDA' if i%2==0 else 'DEPENDÊNCIA',tx,-20,HAIR,.63*la*active*arrival,size=12)
        g.text(DEMANDS[i],tx,21,26,WHITE,la*active*arrival,family='rubik',weight=400,tracking=-.012)
        if la>.1:
            g.line([(tx,h/2-17),(tx+24,h/2-17)],CYAN,la*active,2)
            g.circle(w/2-17,0,3,CYAN,la*active)
        sym=ease(progress(t,4.95+i*.035,5.65+i*.035))*active
        if i%2==0:g.human(0,0,27,WHITE,sym)
        else:g.agent(0,0,27,CYAN,sym)
        g.c.restore()
    if t>=4.5:
        a=active
        g.small('UMA NOVA FORMA DE ENTREGAR',113,254,CYAN,a*eo(progress(t,5.15,5.8)),size=18)
        g.text('AI-Native',105,394,116,WHITE,a,weight=600,tracking=-.065,reveal=progress(t,4.83,5.61))
        g.text('Delivery Pods',105,511,116,WHITE,a,weight=600,tracking=-.065,reveal=progress(t,5.07,5.87))
        g.text('Uma equipe moldada',113,608,34,WHITE,a,family='rubik',weight=400,tracking=-.012,reveal=progress(t,5.72,6.35))
        g.text('pelo resultado.',113,655,34,CYAN,a,family='rubik',weight=500,tracking=-.012,reveal=progress(t,5.88,6.50))
        legend=eo(progress(t,6.35,7.0))*a
        g.human(139,772,25,WHITE,legend)
        g.text('Especialistas',180,782,27,WHITE,legend,family='rubik',weight=400,tracking=-.01)
        g.agent(468,772,24,CYAN,legend)
        g.text('Agentes de IA',509,782,27,WHITE,legend,family='rubik',weight=400,tracking=-.01)
        g.line([(113,828),(740,828)],HAIR,.23*legend,1)
        g.text('Capacidade mensal ou etapa focada de entrega.',113,873,24,HAIR,legend,family='rubik',weight=400,tracking=-.012)
        ck=eo(progress(t,7.35,7.8))
        # A human decision point is visible in the pod itself, not just at its end.
        x,y=mix(HUB,NODES[1],.55)
        g.human(x,y,21,WHITE,a*ck,INK,check=eo(progress(t,7.95,8.3)))


def role_icon(g,i,x,y,u,a=1,s=1):
    """A distinct verb animation for each function, never an invented product UI."""
    g.c.save();g.c.translate(x,y);g.c.scale(s,s)
    white=WHITE;light='#b8edfc'
    p=ease(u)
    if i==0:
        # Alternatives spread; the selected idea gains a solid silhouette.
        spread=lerp(13,62,p)
        g.line([(-spread,-29),(0,17),(spread,-29)],light,.40*a,2)
        g.rect(-spread-22,-57,44,45,white,.30*a,3,2)
        g.diamond(spread,-35,27,white,.48*a,2)
        g.rect(-36,8,72,64,white,a,4,2)
        g.circle(0,40,10,CYAN,a)
        g.line([(-21,92),(21,92)],white,.8*a,3,part=p)
        for k in range(3):g.circle(-17+k*17,-93,3,light,a*progress(u,k*.14,k*.14+.25))
    elif i==1:
        # Modules land one by one, with a small overshoot at contact.
        for k,(bx,by) in enumerate([(-55,33),(10,33),(-55,-26),(10,-26),(-55,-85),(10,-85)]):
            pp=back(progress(u,k*.09,k*.09+.45))
            yy=by-55*(1-pp)
            g.rect(bx,yy,47,45,WHITE,a*eo(progress(u,k*.09,k*.09+.22)),4)
            g.rect(bx+5,yy+5,37,35,BLUE,.6*a,2)
        g.line([(-76,97),(73,97)],light,a,2)
    elif i==2:
        # A tangled dependency path is simplified into one deliberate line.
        tangled=[(-76,-69),(-10,-30),(57,-76),(-58,32),(73,35),(-12,-7),(56,89)]
        clean=[(-65,-68),(-65,-25),(-23,-25),(-23,25),(30,25),(30,69),(68,69)]
        pts=[mix(q,r,p) for q,r in zip(tangled,clean)]
        g.line(pts,white,a,3)
        for k,pt in enumerate(pts):g.circle(*pt,4,light,a)
        sweepy=lerp(-102,110,p)
        g.line([(-89,sweepy),(89,sweepy)],CYAN,a*sin(pi*clamp(u)),5)
        for k in range(3):
            g.circle(-70+k*62,16-k*46,6,light,a*(1-p),1.4)
    elif i==3:
        # A shipped core is extended; this is a topology, not a growth chart.
        g.rect(-34,-35,68,70,white,a,5,2)
        g.diamond(0,0,13,CYAN,a)
        targets=[(-74,-76),(74,-76),(-74,76),(74,76)]
        for k,(xx,yy) in enumerate(targets):
            pp=eo(progress(u,k*.12,k*.12+.5))
            g.line([(xx*.44,yy*.43),(xx*pp,yy*pp)],white,.72*a,2)
            g.circle(xx*pp,yy*pp,11,white,a*pp,2)
        g.arc(0,0,107,-24,78*p,light,.56*a,2)
    else:
        # The protection/maintenance loop closes and a checked state settles.
        path=skia.Path();path.moveTo(0,-83);path.lineTo(61,-60);path.lineTo(52,18)
        path.cubicTo(44,52,17,72,0,86);path.cubicTo(-17,72,-44,52,-52,18);path.lineTo(-61,-60);path.close()
        g.path(path,white,a,2.5,part=lerp(.1,1,eo(u)))
        g.check(0,-3,1.8,white,a,eo(progress(u,.42,.9)))
        g.arc(0,0,111,22,276*eo(u),light,.50*a,2)
        end=(22+276*eo(u))*pi/180
        g.circle(111*cos(end),111*sin(end),4,CYAN,a)
    g.c.restore()


def roles(g,t):
    a=1-ease(progress(t,16.2,17.15))
    entry=eo(progress(t,9.5,10.5))
    if entry<=0 or a<=0:return
    g.small('A COMPOSIÇÃO MUDA COM O TRABALHO',113,205,WHITE,.74*a,size=18)
    g.text('Especialistas + agentes supervisionados',105,299,65,WHITE,a,weight=600,tracking=-.048,reveal=progress(t,9.65,10.48),maxwidth=1720)
    # The original core unfolds into five editable capability shapes.
    for i,x in enumerate(ROLE_X):
        ent=back(progress(t,9.52+i*.065,10.55+i*.065))
        px=lerp(HUB[0],x,ent);py=lerp(HUB[1],562,ent)
        collapse=ease(progress(t,16.05+i*.045,17.10))
        py=lerp(py,526,collapse)
        ww=lerp(68,300,clamp(ent))*(1-.67*collapse)
        hh=lerp(68,373,clamp(ent))*(1-.72*collapse)
        top=py-hh/2
        g.rect(px-ww/2,top,ww,hh,CARD_COLORS[i],a,4)
        g.rect(px-ww/2,top,ww,hh,WHITE,a*.25,4,1)
        glow=progress(t,10.5+i,11.18+i)
        g.line([(px-ww/2+1,top),(px-ww/2+1+(ww-2)*eo(glow),top)],WHITE,a,3)
        g.c.save();g.c.clipRect(skia.Rect.MakeXYWH(px-ww/2+1,top+2,ww-2,hh-3))
        icon_a=a*eo(progress(t,10.05+i*.06,10.7+i*.06))*(1-collapse)
        role_icon(g,i,px,py-53,progress(t,10.5+i,11.45+i),icon_a,.83)
        g.text(ROLES[i],px,py+115,35,WHITE,a*(1-collapse),weight=600,tracking=-.05,align='center',reveal=progress(t,10.0+i*.05,10.7+i*.05))
        g.text(VERBS[i],px,py+156,24,WHITE,a*.8*(1-collapse),family='rubik',weight=400,tracking=-.015,align='center',reveal=progress(t,10.70+i,11.2+i))
        g.c.restore()
        g.line([(px,py+hh/2),(px,827)],WHITE,.24*a*(1-collapse),1.6)
    railp=eo(progress(t,10.3,11.3))
    g.line([(190,827),(1730,827)],WHITE,.46*a,1.6,part=railp)
    for i,xx in enumerate([450,960,1470]):
        pa=eo(progress(t,10.72+i*.12,11.23+i*.12))*a
        pp=eo(progress(t,[11.4,13.4,15.4][i],[11.72,13.72,15.72][i]))
        g.circle(xx,827,37,BLUE,pa)
        g.human(xx,827,27,WHITE,pa,BLUE,pp)
        g.text(['validar','revisar','liberar'][i],xx,895,21,WHITE,pa*.82,family='rubik',weight=400,tracking=0,align='center')
        # A supervised agent approaches, then continues only after the checkpoint.
        p=progress(t,10.8+i*2,11.8+i*2)
        if 0<p<1:
            off=lerp(-152,152,ease(p))
            g.diamond(xx+off,827,8,'#b8edfc',a)
    g.text('Decisões com revisão humana.',960,987,31,WHITE,a,weight=500,tracking=-.025,align='center',reveal=progress(t,11.15,11.75))


def paper_shape(g,x,y,w,h,a=1,stroke=HAIR,fill=WHITE):
    # Clipped-corner paper rather than a pretend application window.
    p=skia.Path();p.moveTo(x-w/2,y-h/2);p.lineTo(x+w/2-22,y-h/2)
    p.lineTo(x+w/2,y-h/2+22);p.lineTo(x+w/2,y+h/2);p.lineTo(x-w/2,y+h/2);p.close()
    g.path(p,fill,a);g.path(p,stroke,.78*a,1.5)
    g.line([(x+w/2-22,y-h/2),(x+w/2-22,y-h/2+22),(x+w/2,y-h/2+22)],stroke,.78*a,1.3)


def artifact_icon(g,i,x,y,a=1,p=1):
    if i==0:
        g.rect(x-44,y-30,55,50,BLUE,.9*a,3,2)
        g.circle(x+35,y-20,17,CYAN,a,2)
        g.line([(x-44,y+42),(x+45,y+42)],HAIR,a,2)
        g.line([(x+13,y+3),(x+39,y+27)],BLUE,a,2)
    elif i==1:
        for k in range(3):
            yy=y+21-k*23;xx=x-35+k*12
            g.rect(xx,yy,64,38,PALE,a,3)
            g.rect(xx,yy,64,38,BLUE,a,3,1.5)
        g.line([(x-11,y-15),(x-23,y-4),(x-11,y+7)],BLUE,a,2)
        g.line([(x+22,y-15),(x+34,y-4),(x+22,y+7)],BLUE,a,2)
    elif i==2:
        for j in range(3):
            yy=y-29+j*30
            g.circle(x-39,yy,9,CYAN,a)
            g.check(x-39,yy,.45,WHITE,a,progress(p,j*.2,j*.2+.3))
            g.line([(x-15,yy),(x+44-j*10,yy)],BLUE,a*.75,2)
    elif i==3:
        g.human(x-5,y,35,BLUE,a,PALE,check=p)
        g.line([(x+42,y-20),(x+59,y-20),(x+59,y+7)],CYAN,a,2)


def flow(g,t):
    a=eo(progress(t,16.72,17.52))*(1-ease(progress(t,24.05,24.8)))
    if a<=0:return
    g.small('EVIDÊNCIAS ANTES DE EXPANDIR',113,203,BLUE,a,size=18)
    cx=[352,960,1550]
    for i,(title,sub) in enumerate(zip(['Contexto','Entrega','Qualidade'],['Contexto compartilhado','Incrementos demonstráveis','Testes, revisão e operação'])):
        rv=progress(t,16.88+i*.1,17.55+i*.1)
        g.text(title,cx[i],311,63,INK,a,weight=600,tracking=-.055,align='center',reveal=rv)
        g.text(sub,cx[i],360,24,MUTED,a,family='rubik',weight=400,tracking=-.01,align='center',reveal=rv)
    g.arrow(659,287,48,BLUE,a,2.3);g.arrow(1263,287,48,BLUE,a,2.3)
    g.line([(155,555),(1770,555)],HAIR,a,2)
    g.arrow(1787,555,30,BLUE,a,2)
    # Blue activity trace becomes a stable, verifiable chain.
    xp=350
    if t<18.15:xp=350
    elif t<19.20:xp=lerp(350,944,ease(progress(t,18.15,19.2)))
    elif t<20.30:xp=lerp(944,1190,ease(progress(t,19.62,20.3)))
    else:xp=lerp(1190,1545,ease(progress(t,20.48,21.25)))
    g.line([(155,555),(xp,555)],BLUE,a,3)
    for j,xx in enumerate([659,1263]):
        tp=[18.56,20.66][j]
        checked=eo(progress(t,tp,tp+.3))
        g.line([(xx,441),(xx,456)],BLUE,.48*a,1.5)
        g.line([(xx,494),(xx,555)],BLUE,.48*a,1.5)
        g.human(xx,418,24,BLUE,a,PAPER,checked)
        g.text(['Validação humana','Revisão humana'][j],xx,483,19,MUTED,a,family='rubik',weight=400,tracking=-.01,align='center')
        g.circle(xx,555,7,PAPER,a)
        g.circle(xx,555,6,BLUE,a,1.7)
    # One hero artifact changes state as it advances. Evidence remains behind it.
    index=0 if t<18.8 else 1 if t<19.83 else 2 if t<20.75 else 3
    changing=[17.2,18.8,19.83,20.75][index]
    flip=sin(pi*progress(t,changing,changing+.24))*.055
    g.c.save();g.c.translate(xp,555);g.c.scale(1-flip,1)
    g.shadow(-164,-103,328,206,3,.07*a)
    paper_shape(g,0,0,328,206,a,HAIR,WHITE)
    artifact_icon(g,index,0,-27,a,eo(progress(t,changing,changing+.36)))
    g.text(['Protótipo','Incremento de software','Teste','Revisão'][index],0,71,25,INK,a,family='rubik',weight=500,tracking=-.022,align='center',maxwidth=287)
    g.c.restore()
    # Persistent conceptual evidence cards; no scores, invented metrics or dashboards.
    ev_x=[312,744,1176,1608]
    for i,x in enumerate(ev_x):
        ea=eo(progress(t,[18.1,19.35,20.3,21.25][i],[18.53,19.8,20.8,21.7][i]))*a
        if ea<=0:continue
        yy=782+18*(1-eo(progress(t,18.1+i*1.08,18.6+i*1.08)))
        g.line([(x-170,733),(x+170,733)],HAIR,ea,1)
        g.circle(x-153,779,15,CYAN,ea)
        g.check(x-153,779,.62,WHITE,ea)
        g.text(['Protótipo','Incremento de software','Teste','Revisão'][i],x-121,786,25,INK,ea,family='rubik',weight=500,tracking=-.012,maxwidth=300)
        g.text(['Demonstrável','Com responsável','Verificável','Decisão registrada'][i],x-121,824,21,MUTED,ea,family='rubik',weight=400,tracking=-.012)
    g.small('EVIDÊNCIAS OPERACIONAIS',113,712,BLUE,a*eo(progress(t,19.6,20.2)),size=15)
    r=progress(t,21.0,21.65)
    w=g.text('Progresso visível.',107,974,61,INK,a,weight=600,tracking=-.055,reveal=r)
    g.text('Responsabilidade clara.',107+w+25,974,61,BLUE,a,weight=600,tracking=-.055,reveal=progress(t,21.22,21.95))


def continuity(g,t):
    # Role outlines shrink into the same paper-like artifacts used by the delivery chain.
    if 16.0<t<17.7:
        p=ease(progress(t,16.1,17.45))
        a=sin(pi*progress(t,16.0,17.7))
        for i,x in enumerate(ROLE_X):
            xx=lerp(x,350+i*285,p); yy=lerp(562,555,p)
            w=lerp(300,92,p);h=lerp(373,66,p)
            g.rect(xx-w/2,yy-h/2,w,h,WHITE,.65*a,4,1.5)
        g.line([(lerp(190,155,p),lerp(827,555,p)),(lerp(1730,1770,p),lerp(827,555,p))],CYAN,.5*a,2)
    # All verified artifacts converge on a single point, which carries into the end card.
    if 23.85<t<25.55:
        p=ease(progress(t,23.9,25.35))
        for i,x in enumerate([312,744,1176,1608]):
            pts=[(x,779),(x,525),(960,525),(960,410)]
            xx,yy=bezier(*pts,p)
            g.curve(pts,CYAN,.36*sin(pi*p),1.5,part=p)
            g.circle(xx,yy,lerp(15,4,p),CYAN,(1-p)*.9)
            if p<.65:g.check(xx,yy,lerp(.62,.16,p),WHITE,1-p)


def endcard(g,t):
    p=eo(progress(t,24.2,25.15))
    if p<=0:return
    # Converging signal arcs decelerate completely before the three-second reading hold.
    r=lerp(307,166,ease(progress(t,24.1,25.2)))
    arca=(1-ease(progress(t,25.1,26.55)))*p
    g.arc(960,429,r,-90,230,CYAN,.55*arca,1.8)
    g.arc(960,429,r+18,146,108,BLUE,.8*arca,2)
    la=eo(progress(t,24.65,25.25))
    g.logo(803,169,314,'light',la)
    g.text('AI-Native',960,436,112,WHITE,1,weight=600,tracking=-.066,align='center',reveal=progress(t,24.77,25.55))
    g.text('Delivery Pods',960,552,112,WHITE,1,weight=600,tracking=-.066,align='center',reveal=progress(t,25.0,25.8))
    g.text('Uma equipe moldada pelo resultado.',960,621,32,HAIR,1,family='rubik',weight=400,tracking=-.015,align='center',reveal=progress(t,25.2,25.86))
    cta=back(progress(t,25.55,26.4))
    cy=lerp(798,768,cta)
    cw=784*clamp(cta)
    g.rect(960-cw/2,cy-48,cw,96,BLUE,clamp(cta),4)
    g.c.save();g.c.clipRect(skia.Rect.MakeXYWH(960-cw/2,cy-48,cw,96))
    g.text('Converse com um engenheiro.',928,cy+13,35,WHITE,eo(progress(t,25.87,26.38)),family='rubik',weight=400,tracking=-.013,align='center')
    g.line([(1290,cy+12),(1311,cy-9),(1291,cy-9)],WHITE,eo(progress(t,26.0,26.45)),2.6)
    g.line([(1311,cy-9),(1311,cy+11)],WHITE,eo(progress(t,26.0,26.45)),2.6)
    g.c.restore()
    g.text('t2stech.com',960,911,33,WHITE,1,family='rubik',weight=400,tracking=.006,align='center',reveal=progress(t,26.05,26.70))
    g.line([(902,978),(1018,978)],CYAN,eo(progress(t,26.25,26.75)),3)


def render(canvas,t,audit=False):
    t=min(max(t,0),27.0)
    g=G(canvas,audit)
    canvas.clear(color(INK))
    # A stable drawing plane. Background grids are traces of the site's signal motif.
    if t<10.4:
        grid_a=(.028+.027*eo(progress(t,4.2,6.0)))*(1-ease(progress(t,9.1,10.1)))
        for x in range(104,1840,92):g.line([(x,164),(x,985)],WHITE,grid_a,1)
        for y in range(233,1020,92):g.line([(104,y),(1816,y)],WHITE,grid_a,1)
        opening(g,t)
    # The pod's circle grows into the capability field: a geometric wipe, not a cut.
    blue_p=ease(progress(t,9.12,10.42))
    if blue_p>0 and t<17.65:
        if blue_p<1:g.circle(HUB[0],HUB[1],2250*blue_p,BLUE)
        else:g.rect(0,0,W,H,BLUE)
    if 9.12<t<17.65:roles(g,t)
    # A role card expands into the paper plane, preserving the shared rail.
    paper_p=ease(progress(t,16.18,17.35))
    if paper_p>0 and t<25.40:
        if paper_p<1:
            w=lerp(304,2070,paper_p);h=lerp(375,1300,paper_p)
            g.rect(960-w/2,562-h/2,w,h,PAPER,1,4*(1-paper_p))
        else:g.rect(0,0,W,H,PAPER)
    if 16.5<t<24.85:flow(g,t)
    if t<24.4:
        if 16.55<t<17.4:
            a=ease(progress(t,16.55,17.4));header(g,t,True,1-a);header(g,t,False,a)
        else:header(g,t,t<16.55,1-ease(progress(t,23.85,24.4)))
    continuity(g,t)
    final_p=ease(progress(t,24.0,25.30))
    if final_p>0:
        if final_p<1:g.circle(960,555,1220*final_p,INK)
        else:g.rect(0,0,W,H,INK)
        endcard(g,t)
    return g.bounds
