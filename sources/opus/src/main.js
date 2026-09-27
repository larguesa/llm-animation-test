// main.js — background, final logo scene (S4), frame renderer with temporal-supersampled motion blur
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
const off = document.createElement('canvas'); off.width = W; off.height = H; const octx = off.getContext('2d');
const grain = document.createElement('canvas'); grain.width = grain.height = 256;
{ const g = grain.getContext('2d'), id = g.createImageData(256, 256), r = mulberry32(99);
  for (let i = 0; i < id.data.length; i += 4) { const v = 96 + r() * 64; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; } g.putImageData(id, 0, 0); }

function keyed(t, keys) { // piecewise smooth interpolation of [time, x, y]
  if (t <= keys[0][0]) return keys[0].slice(1);
  for (let i = 1; i < keys.length; i++) if (t < keys[i][0]) { const a = keys[i - 1], b = keys[i], u = E.inOutCubic((t - a[0]) / (b[0] - a[0])); return [lerp(a[1], b[1], u), lerp(a[2], b[2], u)]; }
  return keys[keys.length - 1].slice(1);
}
function bg(c, t) {
  // .hero:before -> linear-gradient(105deg,#22262b 0%,#303941 50%,#1c252b 100%)
  const vx = Math.sin(105 * Math.PI / 180), vy = -Math.cos(105 * Math.PI / 180), L = Math.abs(W * vx) + Math.abs(H * vy);
  const g = c.createLinearGradient(W / 2 - vx * L / 2, H / 2 - vy * L / 2, W / 2 + vx * L / 2, H / 2 + vy * L / 2);
  g.addColorStop(0, '#22262b'); g.addColorStop(0.5, '#303941'); g.addColorStop(1, '#1c252b');
  c.fillStyle = g; c.fillRect(0, 0, W, H);
  c.fillStyle = 'rgba(13,17,22,0.42)'; c.fillRect(0, 0, W, H); // toward #0d1116 (cinematic hero)
  // radial cyan glow (circle at 76% 28%, #00b4e82e) — follows the dominant action
  const [gx, gy] = keyed(t, [[0, 1459, 302], [4.8, 1459, 302], [6.0, 1390, 540], [9.6, 1390, 540], [10.6, 960, 470], [23.6, 960, 470], [24.6, 960, 360]]);
  glow(c, gx, gy, 520, C.cyan, 0.16);
  // .signal-grid: 46px grid, perspective(520px) rotateX(58deg) rotate(-14deg), subtle parallax drift
  c.save(); c.strokeStyle = 'rgba(255,255,255,0.05)'; c.lineWidth = 1;
  const ox = W * 0.6, oy = H * 0.68, P = 520, th = 58 * Math.PI / 180, ro = -14 * Math.PI / 180, S = 1.35;
  const drift = (t * 7) % 46, ph = E.inOutCubic(prog(t, 23.6, 24.8));
  const proj = (x, y) => { x = x * S; y = (y + drift) * S; const xr = x * Math.cos(ro) - y * Math.sin(ro), yr = x * Math.sin(ro) + y * Math.cos(ro);
    const z = yr * Math.sin(th), k = P / (P - z * 0.5); return [ox + xr * k, oy + yr * Math.cos(th) * k + ph * 60]; };
  c.beginPath();
  for (let i = -18; i <= 18; i++) { const a = proj(i * 46, -460), b = proj(i * 46, 460); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); }
  for (let j = -10; j <= 10; j++) { const a = proj(-830, j * 46), b = proj(830, j * 46); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); }
  c.stroke(); c.restore();
  // vignette
  const v = c.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 1.05);
  v.addColorStop(0, 'rgba(8,12,16,0)'); v.addColorStop(1, 'rgba(8,12,16,0.62)'); c.fillStyle = v; c.fillRect(0, 0, W, H);
}

const S4 = (() => {
  const HIT = 24.5, cen = k => PETAL_C[k];
  function logo(c, t) {
    c.save(); c.translate(LOGO_T.x, LOGO_T.y); c.scale(LOGO_T.s, LOGO_T.s);
    LOGO_P.emblem.forEach((e, k) => {
      const d = [0.02, 0, 0.04, 0.03, 0.05, 0.06][k], p = E.outBack(prog(t, HIT + d, HIT + d + 0.5), 1.7); if (p <= 0) return;
      const [x, y] = cen(k); c.save(); c.translate(x, y); c.scale(p, p); c.translate(-x, -y); c.fillStyle = e.fill; c.fill(e.p); c.restore();
    });
    LOGO_P.letters.forEach((e, k) => {
      const p = E.outQuint(prog(t, HIT + 0.22 + k * 0.08, HIT + 0.82 + k * 0.08)); if (p <= 0) return;
      c.save(); c.beginPath(); c.rect(440, 66, 650, 250); c.clip(); c.translate(0, (1 - p) * 260); c.fillStyle = e.fill; c.fill(e.p); c.restore();
    });
    c.restore();
  }
  function draw(c, t) {
    if (t < 24.3) return;
    const w = E.outCubic(prog(t, HIT, HIT + 1.1)); // impact ring on the resolution hit
    if (w > 0 && w < 1) { c.beginPath(); c.arc(960, 343, 150 + w * 560, 0, 7); c.strokeStyle = rgba(C.cyan, 0.32 * (1 - w)); c.lineWidth = 2; c.stroke();
      c.beginPath(); c.arc(960, 343, 120 + w * 420, 0, 7); c.strokeStyle = rgba(C.blue, 0.4 * (1 - w)); c.stroke(); }
    logo(c, t);
    if (t >= 24.8) { c.fillStyle = 'rgba(255,255,255,0.22)'; c.fillRect(900, 476, 120, 4); const g = c.createLinearGradient(300, 0, 1620, 0); g.addColorStop(0, C.cyan); g.addColorStop(1, C.blue); c.fillStyle = g; c.fillRect(900, 476, 120, 4); }
    const o = { size: 88, w: 700, ls: -0.055 }, w1 = tw(c, 'AI-Native', o), sp = tw(c, 'a a', o) - tw(c, 'aa', o), w2 = tw(c, 'Delivery Pods', o), x0 = 960 - (w1 + sp + w2) / 2;
    maskWords(c, 'AI-Native', x0, 612, o, t, 25.0, { stagger: 0.08 });
    maskWords(c, 'Delivery Pods', x0 + w1 + sp, 612, Object.assign({}, o, { color: C.cyan }), t, 25.1, { stagger: 0.08 });
    const bt = 'Converse com um engenheiro.', bo = { size: 32, w: 700, ls: -0.01 }, bw = tw(c, bt, bo) + 68 + 46, bh = 80, by = 690;
    const bp = E.outBack(prog(t, 25.5, 25.95), 1.4);
    if (bp > 0) {
      c.save(); c.translate(960, by + bh / 2); c.scale(lerp(0.3, 1, bp), 1); c.globalAlpha = clamp(bp * 2);
      rr(c, -bw / 2, -bh / 2, bw, bh, 3); c.fillStyle = C.blue; c.fill(); c.restore();
      const bx = 960 - bw / 2; maskWords(c, bt, bx + 34, by + 51, bo, t, 25.62, { stagger: 0.04, dur: 0.5 });
      const ap = E.outBack(prog(t, 25.85, 26.2), 2), ax = bx + bw - 58, ay = by + bh / 2;
      if (ap > 0) { c.save(); c.translate(ax + 10, ay); c.scale(ap, ap); c.strokeStyle = '#fff'; c.lineWidth = 3.5; c.lineCap = 'round'; c.lineJoin = 'round';
        c.beginPath(); c.moveTo(-9, 9); c.lineTo(9, -9); c.moveTo(-5, -9); c.lineTo(9, -9); c.lineTo(9, 5); c.stroke(); c.restore(); }
    }
    maskWords(c, 't2stech.com', 960, 868, { size: 36, w: 600, ls: 0.01, color: C.cyan, align: 'center' }, t, 26.0, { dur: 0.55 });
  }
  return { draw };
})();

function scene(c, t) {
  c.save(); bg(c, t); c.restore();
  for (const s of [S1, S2, S3, S4]) { c.save(); s.draw(c, t); c.restore(); }
}
window.renderAt = function (t) { ctx.globalAlpha = 1; scene(ctx, t); };
window.renderFrame = function (f, N = 4, shutter = 0.5) {
  for (let k = 0; k < N; k++) {
    const t = (f + (N > 1 ? ((k + 0.5) / N - 0.5) * shutter : 0)) / FPS;
    octx.save(); scene(octx, t); octx.restore();
    ctx.globalAlpha = 1 / (k + 1); ctx.drawImage(off, 0, 0);
  }
  ctx.globalAlpha = 0.06; ctx.globalCompositeOperation = 'overlay';
  const r = mulberry32(f + 1), gx = -Math.floor(r() * 256), gy = -Math.floor(r() * 256);
  for (let y = gy; y < H; y += 256) for (let x = gx; x < W; x += 256) ctx.drawImage(grain, x, y);
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  return cv.toDataURL('image/png');
};
window.ready = (async () => {
  await Promise.all(['700 40px Montserrat', '800 40px Montserrat', '600 40px Montserrat', '400 40px Rubik'].map(f => document.fonts.load(f)));
  await document.fonts.ready;
  return document.fonts.check('700 40px Montserrat') && document.fonts.check('400 40px Rubik');
})();
