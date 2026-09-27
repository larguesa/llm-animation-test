// scene3.js — 16.9–24.6 s: rail becomes flow track "Contexto → Entrega → Qualidade"; artifacts travel; evidence row
const LOGO_T = { x: 700, y: 250, s: 520 / 1082.4330708661416 };
const PETAL_C = [[215, 100], [90, 120], [330, 110], [235, 280], [100, 270], [340, 250]]; // approx centroids (svg units)
const petalXY = k => [LOGO_T.x + PETAL_C[k][0] * LOGO_T.s, LOGO_T.y + PETAL_C[k][1] * LOGO_T.s];
const S3 = (() => {
  const TY = 540, TX0 = 300, TX1 = 1620, LB = 440;
  const nodes = [{ x: 400, l: 'Contexto', c: 'entender o que existe' }, { x: 960, l: 'Entrega', c: 'incrementos com dono claro' }, { x: 1520, l: 'Qualidade', c: 'testes, revisão e evidências' }];
  const NT = [17.25, 17.75, 18.25];
  const ART = [['Protótipo', 'ideia testável'], ['Incremento de software', 'demonstrável'], ['Teste', 'verificação'], ['Revisão', 'checkpoint humano']];
  const A = i => 18.5 + i * 0.75, SLOT = [390, 770, 1150, 1530], ROWY = 820;
  const conv = [{ petal: 1, s0: 23.7 }, { petal: 4, s0: 23.74 }, { petal: 0, s0: 23.78 }, { petal: 3, s0: 23.82 }, { petal: 2, s0: 23.86 }, { petal: 5, s0: 23.9 }];
  function artPos(i, t) {
    const a = A(i); let x, y = TY, s = 1, u = 0;
    if (t < a + 0.3) x = nodes[0].x;
    else if (t < a + 1.05) x = lerp(nodes[0].x, nodes[1].x, E.antic(prog(t, a + 0.3, a + 0.75), 0.06));
    else x = lerp(nodes[1].x, nodes[2].x, E.antic(prog(t, a + 1.05, a + 1.5), 0.06));
    if (t > a + 1.9) { // drop into evidence row along a curve
      const v = prog(t, a + 1.9, a + 2.6); u = E.inOutCubic(v); // drop below the track first, then slide into its slot
      y = lerp(TY, ROWY, E.outBack(prog(v, 0, 0.5), 1.2)); x = lerp(nodes[2].x, SLOT[i], E.inOutCubic(prog(v, 0.2, 1))); s = lerp(1, 0.86, u);
    }
    return { x, y, s, u, pop: E.outBack(prog(t, a, a + 0.35), 1.8), chk: prog(t, a + 1.5, a + 1.95) };
  }
  function card(ctx, i, x, y, s, a, chk, subA, t) {
    const [n, sub] = ART[i], nw = tw(ctx, n, { size: 22, w: 700, ls: -0.02 }), sw = tw(ctx, sub, { size: 16, w: 400, fam: 'Rubik' });
    const w = Math.max(nw, sw) + 118, h = lerp(56, 72, subA), x0 = -w / 2, y0 = -h / 2;
    ctx.save(); ctx.globalAlpha *= a; ctx.translate(x, y); ctx.scale(s, s);
    ctx.shadowColor = 'rgba(0,0,0,0.35)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 8;
    rr(ctx, x0, y0, w, h, 4); ctx.fillStyle = 'rgba(34,38,43,0.94)'; ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.strokeStyle = chk > 0.5 ? rgba(C.cyan, 0.75) : 'rgba(255,255,255,0.22)'; ctx.lineWidth = 1.5; ctx.stroke();
    specialist(ctx, x0 + 30, 0, 0.62); agent(ctx, x0 + 62, 0, 0.5, 1, t * 0.5);
    txt(ctx, n, x0 + 90, subA > 0.02 ? -5 : 8, { size: 22, w: 700, ls: -0.02 });
    if (subA > 0.02) txt(ctx, sub, x0 + 90, 20, { size: 16, w: 400, fam: 'Rubik', color: 'rgba(255,255,255,0.58)', alpha: subA });
    ctx.restore();
    if (chk > 0) checkBadge(ctx, x + (w / 2 - 2) * s, y - (h / 2 - 2) * s, 14 * s, chk);
  }
  function draw(ctx, t) {
    if (t < 16.9 || t > 24.8) return;
    const out = prog(t, 23.55, 23.9);
    // track: five role bars merge into one line and rise
    const p = E.antic(prog(t, 16.9, 17.6), 0.1), pc = clamp(p), trA = 1 - prog(t, 23.9, 24.4);
    const tc = E.inOutCubic(prog(t, 23.7, 24.3)), tx0 = lerp(TX0, 900, tc), tx1 = lerp(TX1, 1020, tc), ty = lerp(TY, 478, tc);
    if (pc < 1) {
      for (let i = 0; i < 5; i++) {
        const x0 = lerp(150 + i * 330, TX0 + i * 264, p), x1 = lerp(450 + i * 330, TX0 + (i + 1) * 264, p), y = lerp(790, TY, p), h = lerp(12, 4, pc);
        ctx.fillStyle = C.role[i]; ctx.globalAlpha = 1 - pc * 0.8; ctx.fillRect(x0, y - h / 2, x1 - x0, h);
        ctx.fillStyle = 'rgba(255,255,255,0.22)'; ctx.globalAlpha = pc; ctx.fillRect(x0, y - h / 2, x1 - x0, h); ctx.globalAlpha = 1;
      }
    } else if (trA > 0) {
      ctx.save(); ctx.globalAlpha = trA; ctx.fillStyle = 'rgba(255,255,255,0.22)'; ctx.fillRect(tx0, ty - 2, tx1 - tx0, 4);
      let fx = TX0; for (let i = 0; i < 4; i++) if (t > A(i)) fx = Math.max(fx, Math.min(artPos(i, Math.min(t, A(i) + 1.9)).x, nodes[2].x));
      fx = lerp(fx, TX1, E.inOutCubic(prog(t, 22.4, 23.0)));
      const g = ctx.createLinearGradient(TX0, 0, TX1, 0); g.addColorStop(0, C.cyan); g.addColorStop(1, C.blue);
      ctx.fillStyle = g; ctx.fillRect(tx0, ty - 2, Math.max(0, lerp(fx, tx1, tc) - tx0), 4);
      ctx.restore();
    }
    // nodes, labels, arrows, captions
    const la = 1 - out;
    nodes.forEach((n, k) => {
      const ap = E.outBack(prog(t, NT[k], NT[k] + 0.4), 2.2); if (ap <= 0) return;
      const isConv = k > 0, cv = isConv ? conv[3 + k] : null;
      if (isConv ? t < cv.s0 + 0.2 : t < 23.9) { // Contexto node fades fully (no stray dot)
        const sh = isConv ? 1 - prog(t, cv.s0, cv.s0 + 0.2) : 1 - prog(t, 23.6, 23.9), na = isConv ? 1 : sh;
        ctx.globalAlpha = na; ctx.beginPath(); ctx.arc(n.x, TY, 18 * ap * (0.5 + 0.5 * sh), 0, 7); ctx.fillStyle = rgba(C.cyan, 0.16 + 0.5 * (1 - sh)); ctx.fill();
        ctx.strokeStyle = C.cyan; ctx.lineWidth = 2; ctx.globalAlpha = sh > 0 ? na : 0; ctx.stroke();
        ctx.beginPath(); ctx.arc(n.x, TY, 6 * ap, 0, 7); ctx.fillStyle = C.cyan; ctx.fill(); ctx.globalAlpha = 1;
      }
      for (let i = 0; i < 4; i++) { const ta = A(i) + [0, 0.75, 1.5][k], q = prog(t, ta, ta + 0.45); if (q > 0 && q < 1) { ctx.beginPath(); ctx.arc(n.x, TY, 18 + q * 36, 0, 7); ctx.strokeStyle = rgba(C.cyan, 0.7 * (1 - q)); ctx.lineWidth = 2; ctx.stroke(); } }
      if (la > 0) {
        ctx.save(); ctx.globalAlpha = la;
        maskWords(ctx, n.l, n.x, LB, { size: 50, w: 700, ls: -0.05, align: 'center' }, t, NT[k] + 0.05, { dur: 0.55 });
        maskWords(ctx, n.c, n.x, LB + 42, { size: 22, w: 400, fam: 'Rubik', color: 'rgba(255,255,255,0.62)', align: 'center' }, t, NT[k] + 0.2, { dur: 0.5, stagger: 0.03 });
        if (k < 2) { // vector arrow between labels: "Contexto → Entrega → Qualidade"
          const e0 = n.x + tw(ctx, n.l, { size: 50, w: 700, ls: -0.05 }) / 2, e1 = nodes[k + 1].x - tw(ctx, nodes[k + 1].l, { size: 50, w: 700, ls: -0.05 }) / 2;
          const m = (e0 + e1) / 2, ay = LB - 17, d = E.outCubic(prog(t, NT[k] + 0.25, NT[k] + 0.6));
          if (d > 0) { ctx.strokeStyle = C.cyan; ctx.lineWidth = 4.5; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
            ctx.beginPath(); ctx.moveTo(m - 34, ay); ctx.lineTo(m - 34 + 68 * d, ay); ctx.stroke();
            if (d > 0.6) { const hq = (d - 0.6) / 0.4; ctx.beginPath(); ctx.moveTo(m + 34 - 16 * hq, ay - 15 * hq); ctx.lineTo(m + 34, ay); ctx.lineTo(m + 34 - 16 * hq, ay + 15 * hq); ctx.stroke(); } }
        }
        ctx.restore();
      }
    });
    // eyebrows + main text
    wipeText(ctx, 'COMO TRABALHAMOS', TX0, 128, { size: 20, w: 800, ls: 0.16, color: C.sky, alpha: 1 - out }, prog(t, 17.0, 17.5));
    wipeText(ctx, 'EVIDÊNCIAS DE PROGRESSO', TX0, 745, { size: 20, w: 800, ls: 0.16, color: C.sky, alpha: 1 - out }, prog(t, 19.9, 20.4));
    maskWords(ctx, 'Progresso visível.', TX0 - 4, 226, { size: 76, w: 700, ls: -0.055 }, t, 20.75, { stagger: 0.08, out: 23.5 });
    maskWords(ctx, 'Responsabilidade clara.', TX0 - 4, 310, { size: 76, w: 700, ls: -0.055, color: C.cyan }, t, 21.0, { stagger: 0.08, out: 23.56 });
    // artifacts
    for (let i = 3; i >= 0; i--) {
      if (t < A(i)) continue; const s = artPos(i, t), cv = conv[i];
      if (t < cv.s0 + 0.22) {
        const sh = 1 - E.inCubic(prog(t, cv.s0, cv.s0 + 0.22));
        card(ctx, i, s.x, s.y, s.s * s.pop * sh, 1, s.chk, 1 - s.u, t);
      }
    }
    // convergence: chips / nodes collapse to dots that fly into the six logo petals
    conv.forEach((cv, k) => {
      const f = prog(t, cv.s0 + 0.15, cv.s0 + 0.75); if (f <= 0 || f >= 1) return;
      const from = k < 4 ? [SLOT[k], ROWY] : [nodes[k - 3].x, TY], to = petalXY(cv.petal), e = E.antic(f, 0.08);
      const x = lerp(from[0], to[0], e), y = lerp(from[1], to[1], e) - Math.sin(f * Math.PI) * 50;
      const col = LOGO.emblem[cv.petal].fill; glow(ctx, x, y, 40, col, 0.5);
      ctx.beginPath(); ctx.arc(x, y, lerp(12, 7, f), 0, 7); ctx.fillStyle = col; ctx.fill();
    });
  }
  return { draw, conv };
})();
