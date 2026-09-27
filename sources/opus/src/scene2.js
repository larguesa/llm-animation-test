// scene2.js — 9.6–17.0 s: pod core expands into five roles; team members fly in; human checkpoints
const S2 = (() => {
  const roles = [['Prototyper', 'explorar ideias'], ['Builder', 'construir'], ['Sweeper', 'simplificar'], ['Grower', 'evoluir'], ['Maintainer', 'manter']];
  const CW = 300, CH = 400, GAP = 30, X0 = 150, Y0 = 285, RAIL = 790, T0 = 10.5, DT = 1.0, OUT = 16.3;
  const cx = i => X0 + i * (CW + GAP), mid = i => cx(i) + CW / 2, Ti = i => T0 + i * DT;
  const cpX = i => (mid(i) + mid(i + 1)) / 2;
  const team = [];
  [0, 2, 4, 6, 8].forEach((ri, k) => team.push({ ri, card: k, slot: 0, kind: 'spec', d: k * 0.04 }));
  [1, 3, 5, 7].forEach((ri, k) => team.push({ ri, card: k, slot: 1, kind: 'agent', d: 0.1 + k * 0.04 }));
  const spawns = [{ card: 0, slot: 2 }, { card: 1, slot: 2 }, { card: 4, slot: 1 }];
  const slotPos = (card, slot) => [cx(card) + 42 + slot * 48, Y0 + CH - 34];
  function glyph(ctx, i, gx, gy, u) {
    const c = [gx + 124, gy + 75];
    ctx.save(); ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    if (i === 0) { // explore ideas: many sketches, one survives
      const off = [[-84, -30], [0, -42], [84, -30], [-42, 32], [42, 32]];
      off.forEach((o, k) => {
        const p = E.outBack(prog(u, 0.08 + k * 0.08, 0.45 + k * 0.08), 1.8); if (p <= 0) return;
        const chosen = k === 1, dim = chosen ? 0 : prog(u, 0.9, 1.2) * 0.72, sel = chosen ? E.outCubic(prog(u, 0.9, 1.2)) : 0;
        const x = c[0] + o[0] * p, y = c[1] + o[1] * p + Math.sin(u * 2 + k) * 2;
        ctx.save(); ctx.globalAlpha = 1 - dim; ctx.translate(x, y); ctx.scale(p, p);
        rr(ctx, -32, -22, 64, 44, 4);
        if (sel > 0) { ctx.fillStyle = rgba(C.cyan, sel); ctx.fill(); }
        ctx.setLineDash(sel > 0.5 ? [] : [5, 5]); ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.stroke();
        ctx.setLineDash([]); ctx.beginPath(); ctx.moveTo(-20, -6); ctx.lineTo(14, -6); ctx.moveTo(-20, 6); ctx.lineTo(4, 6);
        ctx.strokeStyle = 'rgba(255,255,255,0.7)'; ctx.stroke(); ctx.restore();
      });
    } else if (i === 1) { // build: bricks stack into a structure
      const rows = [4, 3, 2, 1]; let k = 0;
      rows.forEach((n, r) => { for (let j = 0; j < n; j++, k++) {
        const p = E.outBack(prog(u, 0.05 + k * 0.055, 0.4 + k * 0.055), 1.5); if (p <= 0) continue;
        const bw = 50, bh = 26, x = c[0] - (n * bw + (n - 1) * 6) / 2 + j * (bw + 6), y = gy + 140 - (r + 1) * (bh + 6) - (1 - p) * 70;
        ctx.globalAlpha = clamp(p * 3); rr(ctx, x, y, bw, bh, 3); ctx.fillStyle = r === 3 ? C.cyan : 'rgba(255,255,255,0.92)'; ctx.fill();
      } });
    } else if (i === 2) { // simplify: tangled path becomes a clean line, extras removed
      const m = E.inOutCubic(prog(u, 0.25, 1.0)), keep = [0, 4, 8];
      const pts = []; for (let k = 0; k < 9; k++) { const zz = [0, -48, 40, -30, 50, -44, 26, -52, 0][k]; pts.push([gx + 14 + k * 27.5, c[1] + zz * (1 - m)]); }
      ctx.beginPath(); pts.forEach((p, k) => (k ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])));
      ctx.strokeStyle = 'rgba(255,255,255,0.85)'; ctx.lineWidth = 2.5; ctx.stroke();
      pts.forEach((p, k) => { const kp = keep.includes(k); const s = kp ? 1 : 1 - prog(u, 0.55, 0.95); if (s <= 0) return;
        ctx.beginPath(); ctx.arc(p[0], p[1], (kp ? 8 : 5) * (kp ? 1 : s), 0, 7); ctx.fillStyle = kp ? (m > 0.6 ? C.cyan : '#fff') : `rgba(255,255,255,${s})`; ctx.fill(); });
      const sw = prog(u, 0.2, 1.05); if (sw > 0 && sw < 1) { const x = gx + sw * 248; const g = ctx.createLinearGradient(x - 40, 0, x, 0); g.addColorStop(0, 'rgba(0,180,232,0)'); g.addColorStop(1, 'rgba(0,180,232,0.45)'); ctx.fillStyle = g; ctx.fillRect(x - 40, gy + 5, 40, 140); }
    } else if (i === 3) { // evolve: iterative rising path
      const P = [[18, 128], [70, 104], [112, 112], [160, 66], [196, 74], [232, 22]].map(p => [gx + p[0], gy + p[1]]);
      const d = E.inOutCubic(prog(u, 0.1, 1.0)) * (P.length - 1);
      ctx.beginPath(); ctx.moveTo(P[0][0], P[0][1]);
      for (let k = 1; k <= Math.ceil(d); k++) { const f = Math.min(1, d - (k - 1)); ctx.lineTo(lerp(P[k - 1][0], P[k][0], f), lerp(P[k - 1][1], P[k][1], f)); }
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.stroke();
      P.forEach((p, k) => { if (k > d + 0.01) return; ctx.beginPath(); ctx.arc(p[0], p[1], k === P.length - 1 ? 9 : 5, 0, 7); ctx.fillStyle = k === P.length - 1 ? C.cyan : '#fff'; ctx.fill(); });
      if (d >= P.length - 1.01) { const q = (u * 1.2) % 1; ctx.beginPath(); ctx.arc(P[5][0], P[5][1], 9 + q * 18, 0, 7); ctx.strokeStyle = rgba(C.cyan, 1 - q); ctx.lineWidth = 2; ctx.stroke(); }
    } else { // maintain: shield + steady pulse
      const p = E.inOutCubic(prog(u, 0.05, 0.7));
      ctx.beginPath(); ctx.moveTo(c[0], gy + 8); ctx.lineTo(c[0] + 56, gy + 28); ctx.quadraticCurveTo(c[0] + 56, gy + 112, c[0], gy + 142); ctx.quadraticCurveTo(c[0] - 56, gy + 112, c[0] - 56, gy + 28); ctx.closePath();
      ctx.setLineDash([440 * p, 440]); ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.stroke(); ctx.setLineDash([]);
      const a = prog(u, 0.5, 0.8); if (a > 0) { ctx.save(); ctx.globalAlpha = a; ctx.beginPath();
        for (let x = -40; x <= 40; x += 2) { const ph = ((x + 40) / 80 - (u * 0.9) % 1 + 1) % 1; const y = ph > 0.42 && ph < 0.58 ? -Math.sin((ph - 0.42) / 0.16 * Math.PI) * 24 : 0; x === -40 ? ctx.moveTo(c[0] + x, c[1] + y) : ctx.lineTo(c[0] + x, c[1] + y); }
        ctx.strokeStyle = C.cyan; ctx.lineWidth = 3; ctx.stroke(); ctx.restore(); }
    }
    ctx.restore();
  }
  function drawRail(ctx, t, a) {
    ctx.save(); ctx.globalAlpha = a;
    for (let i = 0; i < 4; i++) {
      const s = Ti(i);
      lineP(ctx, mid(i), RAIL, cpX(i), RAIL, E.outCubic(prog(t, s + 0.25, s + 0.5)), 'rgba(255,255,255,0.35)', 2);
      lineP(ctx, cpX(i), RAIL, mid(i + 1), RAIL, E.outCubic(prog(t, s + 0.6, s + 0.95)), 'rgba(255,255,255,0.35)', 2);
    }
    for (let i = 0; i < 5; i++) { const p = E.outBack(prog(t, Ti(i), Ti(i) + 0.3), 2); if (p > 0) { ctx.beginPath(); ctx.arc(mid(i), RAIL, 8 * p, 0, 7); ctx.fillStyle = C.role[i]; ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.stroke(); } }
    for (let i = 0; i < 4; i++) {
      const s = Ti(i) + 0.5; checkBadge(ctx, cpX(i), RAIL, 19, prog(t, s, s + 0.45));
      wipeText(ctx, 'CHECKPOINT HUMANO', cpX(i), RAIL + 56, { size: 16, w: 800, ls: 0.14, color: C.sky, align: 'center' }, prog(t, s + 0.1, s + 0.5));
    }
    ctx.restore();
  }
  function draw(ctx, t) {
    if (t < 9.6 || t > 17.2) return;
    const col = E.inOutCubic(prog(t, OUT, OUT + 0.6)), cA = 1 - prog(t, OUT, OUT + 0.3);
    // core -> five slots
    if (t < 10.0) {
      const p = E.antic(prog(t, 9.6, 10.0), 0.08), x = lerp(S1.CORE.x, 960, p), y = lerp(S1.CORE.y, Y0 + CH / 2, p), r = lerp(92, 70, clamp(p));
      ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fillStyle = rgba(C.blue, 0.2); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,0.64)'; ctx.lineWidth = 1.5; ctx.stroke();
      txt(ctx, 'RESULTADO', x, y + 8, { size: 21, w: 800, ls: 0.14, align: 'center', alpha: 1 - prog(t, 9.6, 9.85) });
    } else {
      const p = E.outBack(prog(t, 10.0, 10.6), 1.1), pc = clamp(p);
      for (let i = 0; i < 5; i++) {
        const w = lerp(140, CW, pc), h0 = lerp(140, CH, pc), x = lerp(960, mid(i), p) - w / 2;
        const top = lerp(lerp(Y0 + CH / 2 - h0 / 2, Y0, pc), RAIL - 6, col), h = lerp(h0, 12, col);
        rr(ctx, x, top, w, h, lerp(70, 4, pc)); ctx.fillStyle = 'rgba(255,255,255,0.04)'; ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,0.24)'; ctx.lineWidth = 1.5; ctx.stroke();
        const f = E.outCubic(prog(t, Ti(i), Ti(i) + 0.4));
        if (f > 0) {
          ctx.save(); rr(ctx, x, top, w, h, 4); ctx.clip();
          ctx.fillStyle = C.role[i]; ctx.fillRect(x, top + h * (1 - f), w, h * f);
          ctx.fillStyle = `rgba(255,255,255,${0.3 * (1 - f)})`; ctx.fillRect(x, top + h * (1 - f), w, h * f);
          if (cA > 0) {
            ctx.globalAlpha = cA; ctx.fillStyle = 'rgba(13,17,22,0.28)'; ctx.fillRect(x, top + h - 68, w, 68);
            txt(ctx, '0' + (i + 1), x + 26, top + 44, { size: 17, w: 800, ls: 0.1, color: 'rgba(255,255,255,0.46)', alpha: prog(t, Ti(i) + 0.1, Ti(i) + 0.4) });
            glyph(ctx, i, x + 26, top + 70, t - Ti(i) - 0.1);
            maskWords(ctx, roles[i][0], x + 26, top + 270, { size: 42, w: 700, ls: -0.05 }, t, Ti(i) + 0.12, { dur: 0.55 });
            maskWords(ctx, roles[i][1], x + 27, top + 314, { size: 27, w: 400, fam: 'Rubik', color: 'rgba(255,255,255,0.8)' }, t, Ti(i) + 0.24, { dur: 0.55, stagger: 0.05 });
          }
          ctx.restore();
        }
      }
    }
    // headline
    maskWords(ctx, 'Especialistas + agentes supervisionados', 960, 190, { size: 66, w: 700, ls: -0.05, align: 'center' }, t, 10.05, { stagger: 0.07, out: 16.25 });
    // team members fly from the scene-1 ring into each role
    if (cA > 0) {
      ctx.save(); ctx.globalAlpha = cA;
      team.forEach(m => {
        const p = E.antic(prog(t, 9.6 + m.d, 10.5 + m.d), 0.08), [sx, sy] = S1.ringPos(m.ri, 9.6), [dx, dy] = slotPos(m.card, m.slot);
        const x = lerp(sx, dx, p), y = lerp(sy, dy, p) - Math.sin(clamp(p) * Math.PI) * 60, s = lerp(1, 0.66, clamp(p));
        (m.kind === 'spec' ? specialist : agent)(ctx, x, y, s, 1, t * 0.4);
      });
      spawns.forEach(sp => { const p = E.outBack(prog(t, Ti(sp.card) + 0.35, Ti(sp.card) + 0.7), 2.2); if (p > 0) { const [x, y] = slotPos(sp.card, sp.slot); agent(ctx, x, y, 0.66 * p, 1, t * 0.4); } });
      ctx.restore();
    }
    if (t < 16.95) drawRail(ctx, t, 1 - prog(t, 16.3, 16.85));
    const cap = prog(t, 14.75, 15.1) * (1 - prog(t, OUT - 0.1, OUT + 0.2));
    if (cap > 0) maskWords(ctx, 'Revisão humana nos pontos de decisão.', 960, 945, { size: 34, w: 400, fam: 'Rubik', color: 'rgba(255,255,255,0.78)', align: 'center' }, t, 14.75, { stagger: 0.05, out: OUT - 0.1 });
  }
  return { draw, mid, cpX, RAIL };
})();
