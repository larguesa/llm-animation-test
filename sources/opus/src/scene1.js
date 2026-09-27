// scene1.js — 0–10.4 s: scattered demands -> aligned grid -> connected pod core
const S1 = (() => {
  const R = mulberry32(7);
  const labels = ['Backlog', 'Integração', 'Legado', 'Novo requisito', 'Bug em produção', 'Dependência', 'Prazo', 'Aprovação', 'Infraestrutura'];
  const subs = ['pendente', 'bloqueada', 'sem dono', 'aguardando', 'urgente', 'externa', 'apertado', 'em espera', 'instável'];
  const acc = [C.amber, C.red, C.amber, C.cyan, C.red, C.amber, C.red, C.amber, C.amber];
  const scatter = [[330, 210], [800, 150], [1480, 190], [240, 520], [1140, 330], [1700, 470], [620, 400], [1330, 640], [940, 690]];
  const CORE = { x: 1330, y: 540 }, RING = 205;
  const cards = labels.map((l, i) => ({
    l, sub: subs[i], acc: acc[i], sx: scatter[i][0], sy: scatter[i][1], rot: (R() - 0.5) * 0.5,
    ph: R() * 6.28, grid: [660 + (i % 3) * 300, 250 + Math.floor(i / 3) * 120],
    kind: i % 2 === 0 ? 'spec' : 'agent', ang: -Math.PI / 2 + i * (Math.PI * 2 / 9)
  }));
  const deps = [[0, 6], [6, 4], [4, 2], [1, 4], [3, 6], [6, 8], [8, 7], [7, 5], [2, 5], [1, 0], [4, 7], [3, 8]];
  const CW = 262, CH = 88, ORDER = [4, 6, 1, 0, 2, 3, 5, 7, 8]; // cards sitting on other slots move first
  function ringPos(i, t) {
    const a = cards[i].ang + Math.max(0, t - 5.6) * 0.06;
    return [CORE.x + Math.cos(a) * RING, CORE.y + Math.sin(a) * RING];
  }
  function state(i, t) {
    const c = cards[i];
    const inP = E.outBack(prog(t, 0.05 + i * 0.07, 0.6 + i * 0.07), 1.6);
    const tense = 1 - prog(t, 2.0, 4.4);
    let x = c.sx + Math.sin(t * 1.3 + c.ph) * 14 * tense, y = c.sy + Math.cos(t * 1.1 + c.ph) * 9 * tense;
    let rot = c.rot + Math.sin(t * 0.9 + c.ph) * 0.03 * tense;
    const aS = 2.0 + ORDER.indexOf(i) * 0.25, aP = E.outBack(prog(t, aS, aS + 0.55), 1.2);
    x = lerp(x, c.grid[0], aP); y = lerp(y, c.grid[1], aP); rot = lerp(rot, 0, clamp(aP));
    // beat pulse while tense
    const beatK = 1 + 0.025 * Math.exp(-((t % BEAT) / 0.08)) * tense;
    let w = CW * inP * beatK, h = CH * inP * beatK, rad = 4, labA = 1;
    const mS = 5.0 + i * 0.045, mP = E.antic(prog(t, mS, mS + 0.85), 0.1);
    let iconA = 0;
    if (t > mS) {
      const [rx, ry] = ringPos(i, t);
      x = lerp(x, rx, mP); y = lerp(y, ry, mP);
      const sz = 44; w = lerp(CW, sz, clamp(mP)); h = lerp(CH, sz, clamp(mP));
      rad = lerp(4, c.kind === 'spec' ? sz / 2 : 8, clamp(mP));
      labA = 1 - prog(t, mS + 0.18, mS + 0.4); iconA = prog(t, mS + 0.55, mS + 0.85);
    }
    return { x, y, w, h, rot, rad, labA, iconA, aP, inP };
  }
  function drawCard(ctx, c, s, t) {
    if (s.inP <= 0) return;
    ctx.save(); ctx.translate(s.x, s.y); ctx.rotate(s.rot);
    const bodyA = 1 - s.iconA;
    if (bodyA > 0) {
      ctx.globalAlpha = bodyA;
      rr(ctx, -s.w / 2, -s.h / 2, s.w, s.h, s.rad);
      ctx.fillStyle = 'rgba(34,38,43,0.86)'; ctx.fill();
      ctx.strokeStyle = s.labA < 1 ? rgba(C.cyan, 0.7) : 'rgba(255,255,255,0.2)'; ctx.lineWidth = 1.5; ctx.stroke();
      const accC = s.aP > 0.5 ? C.cyan : c.acc;
      if (s.labA > 0) {
        ctx.fillStyle = accC; ctx.fillRect(-s.w / 2, -s.h / 2, 4, s.h);
        ctx.globalAlpha = bodyA * s.labA;
        txt(ctx, c.l, -s.w / 2 + 22, -4, { size: 24, w: 700, ls: -0.02 });
        ctx.beginPath(); ctx.arc(-s.w / 2 + 27, 22, 4.5, 0, 7); ctx.fillStyle = accC; ctx.fill();
        const st = s.aP > 0.5 ? 'priorizado' : c.sub;
        txt(ctx, st, -s.w / 2 + 40, 28, { size: 17, w: 400, fam: 'Rubik', color: 'rgba(255,255,255,0.6)' });
      }
    }
    ctx.restore();
    if (s.iconA > 0) (c.kind === 'spec' ? specialist : agent)(ctx, s.x, s.y, 1, s.iconA, t * 0.4);
  }
  function draw(ctx, t) {
    if (t > 10.6) return;
    const S = cards.map((c, i) => state(i, t));
    // dependency lines (tension -> order)
    const depA = prog(t, 0.5, 1.2) * (1 - prog(t, 4.9, 5.2));
    if (depA > 0) {
      deps.forEach(([a, b], k) => {
        const A = S[a], B = S[b], al = Math.min(A.aP, B.aP);
        const d = E.outCubic(prog(t, 0.4 + k * 0.08, 1.2 + k * 0.08));
        ctx.save(); ctx.globalAlpha = depA;
        ctx.beginPath(); ctx.moveTo(A.x, A.y);
        const mx = (A.x + B.x) / 2 + Math.sin(k * 3 + t * 1.5) * 60 * (1 - al), my = (A.y + B.y) / 2 + Math.cos(k * 2 + t) * 50 * (1 - al);
        const ex = lerp(A.x, B.x, d), ey = lerp(A.y, B.y, d);
        ctx.quadraticCurveTo(lerp(A.x, mx, d), lerp(A.y, my, d), ex, ey);
        ctx.strokeStyle = al > 0.5 ? rgba(C.cyan, 0.35) : rgba(k % 3 === 0 ? C.red : C.amber, 0.45);
        ctx.lineWidth = 1.6; ctx.setLineDash(al > 0.5 ? [] : [6, 8]); ctx.lineDashOffset = -t * 40; ctx.stroke();
        ctx.restore();
      });
    }
    // pod core + orbit rings
    const coreP = prog(t, 5.1, 6.0), fade = 1 - prog(t, 9.35, 9.75);
    if (coreP > 0) {
      ctx.save(); ctx.globalAlpha = fade;
      glow(ctx, CORE.x, CORE.y, 330, C.cyan, 0.13 * coreP);
      ctx.beginPath(); ctx.arc(CORE.x, CORE.y, RING, -Math.PI / 2, -Math.PI / 2 + 6.2832 * E.inOutCubic(coreP));
      ctx.strokeStyle = rgba(C.cyan, 0.3); ctx.lineWidth = 1.5; ctx.stroke();
      ctx.beginPath(); ctx.arc(CORE.x, CORE.y, RING + 62, Math.PI / 2, Math.PI / 2 + 6.2832 * E.inOutCubic(prog(t, 5.4, 6.4)));
      ctx.strokeStyle = rgba(C.blue, 0.45); ctx.stroke();
      // spokes (connections) drawn on beat
      cards.forEach((c, i) => {
        const p = E.outCubic(prog(t, 5.9 + i * 0.06, 6.3 + i * 0.06)); if (p <= 0) return;
        const [x, y] = ringPos(i, t);
        lineP(ctx, x, y, lerp(x, CORE.x, 0.62), lerp(y, CORE.y, 0.62), p, rgba(c.kind === 'spec' ? C.cyan : C.blue, 0.55), 1.5);
        // travelling pulse on spokes
        const q = ((t - 6.3 - i * 0.11) % 1.0 + 1) % 1.0;
        if (t > 6.3) { ctx.beginPath(); ctx.arc(lerp(x, CORE.x, q * 0.62), lerp(y, CORE.y, q * 0.62), 3, 0, 7); ctx.fillStyle = rgba('#ffffff', 0.7 * (1 - q)); ctx.fill(); }
      });
      const cs = E.outBack(prog(t, 5.5, 6.1), 1.8), beat = 1 + 0.03 * Math.exp(-(((t - 6) % BEAT + BEAT) % BEAT) / 0.1) * prog(t, 6, 6.2);
      const r = 92 * cs * beat;
      ctx.globalAlpha = 1;
      if (r > 0 && t < 9.6) { // after 9.6 the core is carried by scene 2
        ctx.beginPath(); ctx.arc(CORE.x, CORE.y, r + 20, 0, 7); ctx.fillStyle = rgba(C.blue, 0.07); ctx.fill();
        ctx.beginPath(); ctx.arc(CORE.x, CORE.y, r, 0, 7); ctx.fillStyle = rgba(C.blue, 0.2); ctx.fill();
        ctx.strokeStyle = 'rgba(255,255,255,0.64)'; ctx.lineWidth = 1.5; ctx.stroke();
        const la = prog(t, 5.9, 6.3);
        txt(ctx, 'RESULTADO', CORE.x, CORE.y + 8, { size: 21, w: 800, ls: 0.14, align: 'center', alpha: la });
      }
      ctx.restore();
    }
    if (t < 9.6) cards.forEach((c, i) => drawCard(ctx, c, S[i], t)); // members then fly into roles (scene 2)
    // legend: specialists vs agents
    const lg = prog(t, 7.2, 7.8) * (1 - prog(t, 9.2, 9.6));
    if (lg > 0) {
      const y = 880, dy = (1 - E.outCubic(lg)) * 16;
      ctx.save(); ctx.globalAlpha = lg;
      specialist(ctx, 1085, y + dy, 0.8); txt(ctx, 'Especialistas', 1115, y + 8 + dy, { size: 24, w: 400, fam: 'Rubik', color: 'rgba(255,255,255,0.82)' });
      agent(ctx, 1320, y + dy, 0.8, 1, t * 0.4); txt(ctx, 'Agentes supervisionados', 1350, y + 8 + dy, { size: 24, w: 400, fam: 'Rubik', color: 'rgba(255,255,255,0.82)' });
      ctx.restore();
    }
    // typography
    if (t < 5.0) {
      maskWords(ctx, 'Mais horas', 150, 880, { size: 96, w: 700, ls: -0.05 }, t, 0.45, { stagger: 0.1, out: 4.35 });
      maskWords(ctx, 'não resolvem tudo.', 150, 985, { size: 96, w: 700, ls: -0.05, color: C.cyan }, t, 0.75, { stagger: 0.1, out: 4.45 });
    }
    if (t > 5.4 && t < 10) {
      wipeText(ctx, 'T2S TECH  ·  SERVIÇO', 150, 360, { size: 20, w: 800, ls: 0.16, color: C.sky, alpha: 1 - prog(t, 9.0, 9.3) }, prog(t, 5.6, 6.1));
      maskWords(ctx, 'AI-Native', 146, 480, { size: 124, w: 700, ls: -0.06 }, t, 5.95, { stagger: 0.08, out: 9.0 });
      maskWords(ctx, 'Delivery Pods', 146, 600, { size: 124, w: 700, ls: -0.06, color: C.cyan }, t, 6.1, { stagger: 0.1, out: 9.08 });
      maskWords(ctx, 'Uma equipe moldada pelo resultado.', 152, 700, { size: 38, w: 400, fam: 'Rubik', color: 'rgba(255,255,255,0.8)' }, t, 7.0, { stagger: 0.05, out: 9.15 });
    }
  }
  return { draw, ringPos, CORE, cards };
})();
