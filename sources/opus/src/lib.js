// lib.js — shared constants, easing, drawing primitives (T2S brand tokens from site CSS :root)
const W = 1920, H = 1080, FPS = 30, BEAT = 0.5; // music: 120 BPM, 1 beat = 0.5 s = 15 frames
const C = {
  cyan: '#00b4e8', blue: '#3264ff', blueDeep: '#1e46bd', inkDeep: '#22262b', ink: '#3f3f3f',
  paper: '#f6f9fb', surfaceBlue: '#eaf7fc', muted: '#65717c', hair: '#cbd6de', red: '#df3e56',
  amber: '#e59f24', green: '#22bd51', night: '#0d1116', sky: '#72dfff', ice: '#bdefff', pale: '#c8effa',
  role: ['#2454e8', '#3264ff', '#2b5bec', '#2856df', '#1e49cc'] // .role-card backgrounds on the site
};
const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
const lerp = (a, b, t) => a + (b - a) * t;
const prog = (t, a, b) => clamp((t - a) / (b - a));
const E = {
  lin: x => x,
  inCubic: x => x * x * x,
  outCubic: x => 1 - Math.pow(1 - x, 3),
  inOutCubic: x => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  outQuint: x => 1 - Math.pow(1 - x, 5), // ~ site easing cubic-bezier(.22,1,.36,1)
  inOutQuint: x => (x < 0.5 ? 16 * x ** 5 : 1 - Math.pow(-2 * x + 2, 5) / 2),
  outExpo: x => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
  inOutExpo: x => (x <= 0 ? 0 : x >= 1 ? 1 : x < 0.5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2),
  outBack: (x, s = 1.35) => 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2),
  inBack: (x, s = 1.5) => (s + 1) * x * x * x - s * x * x,
  // anticipation then fast move with soft landing
  antic: (x, s = 0.12) => { const a = 0.22; if (x < a) { const u = x / a; return -s * Math.sin(u * Math.PI / 2) * (1 - u * 0.2); } const u = (x - a) / (1 - a); return lerp(-s * 0.8, 1, E.outQuint(u)); }
};
function rgba(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}
function mulberry32(a) { return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

// ---------- text ----------
function setFont(ctx, o) {
  const size = o.size || 40;
  ctx.font = `${o.w || 700} ${size}px ${o.fam || 'Montserrat'}`;
  ctx.letterSpacing = ((o.ls || 0) * size).toFixed(2) + 'px';
  ctx.textBaseline = o.base || 'alphabetic';
}
function tw(ctx, s, o) { ctx.save(); setFont(ctx, o); const m = ctx.measureText(s).width - (o.ls || 0) * (o.size || 40); ctx.restore(); return m; }
function txt(ctx, s, x, y, o) {
  ctx.save(); setFont(ctx, o);
  ctx.fillStyle = o.color || '#fff'; ctx.globalAlpha *= (o.alpha == null ? 1 : o.alpha);
  let xx = x; const w = tw(ctx, s, o);
  if (o.align === 'center') xx = x - w / 2; else if (o.align === 'right') xx = x - w;
  ctx.textAlign = 'left'; ctx.fillText(s, xx, y); ctx.restore(); return w;
}
// kinetic word-by-word mask reveal (slide up inside a clip), optional exit (slide up and out)
function maskWords(ctx, s, x, y, o, t, t0, k = {}) {
  const st = k.stagger == null ? 0.06 : k.stagger, dur = k.dur || 0.6, size = o.size || 40;
  const words = s.split(' ');
  const sp = tw(ctx, 'a a', o) - tw(ctx, 'aa', o);
  const ws = words.map(wd => tw(ctx, wd, o));
  const total = ws.reduce((a, b) => a + b, 0) + sp * (words.length - 1);
  let cx = o.align === 'center' ? x - total / 2 : o.align === 'right' ? x - total : x;
  words.forEach((wd, i) => {
    const p = E.outQuint(prog(t, t0 + i * st, t0 + i * st + dur));
    let dy = (1 - p) * size * 1.2;
    let a = p > 0 ? 1 : 0;
    if (k.out != null) { const q = E.inCubic(prog(t, k.out + i * st * 0.6, k.out + i * st * 0.6 + (k.outDur || 0.4))); dy -= q * size * 1.25; if (q >= 1) a = 0; }
    if (a > 0) {
      ctx.save(); ctx.beginPath(); ctx.rect(cx - size * 0.2, y - size * 1.08, ws[i] + size * 0.4, size * 1.42); ctx.clip();
      txt(ctx, wd, cx, y + dy, Object.assign({}, o, { align: 'left' }));
      ctx.restore();
    }
    cx += ws[i] + sp;
  });
  return total;
}
// horizontal wipe mask for a whole line (used for eyebrows / small labels)
function wipeText(ctx, s, x, y, o, p) {
  if (p <= 0) return; const w = tw(ctx, s, o), size = o.size || 20;
  let x0 = o.align === 'center' ? x - w / 2 : o.align === 'right' ? x - w : x;
  ctx.save(); ctx.beginPath(); ctx.rect(x0 - 4, y - size * 1.2, (w + 8) * E.outCubic(p), size * 1.6); ctx.clip();
  txt(ctx, s, x0 + (1 - E.outCubic(p)) * -18, y, Object.assign({}, o, { align: 'left' })); ctx.restore();
}

// ---------- shapes ----------
function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, Math.max(0, Math.min(r, w / 2, h / 2))); }
function glow(ctx, x, y, r, col, a) {
  if (a <= 0) return; const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, rgba(col, a)); g.addColorStop(1, rgba(col, 0));
  ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2);
}
// specialist = solid cyan disc with halo ring (person, experienced)
function specialist(ctx, x, y, s, a = 1) {
  if (a <= 0 || s <= 0) return; ctx.save(); ctx.globalAlpha *= a;
  glow(ctx, x, y, 34 * s, C.cyan, 0.35);
  ctx.beginPath(); ctx.arc(x, y, 25 * s, 0, 7); ctx.strokeStyle = rgba(C.cyan, 0.45); ctx.lineWidth = 2 * s; ctx.stroke();
  ctx.beginPath(); ctx.arc(x, y, 15 * s, 0, 7); ctx.fillStyle = C.cyan; ctx.fill();
  ctx.beginPath(); ctx.arc(x, y - 3 * s, 5 * s, 0, 7); ctx.fillStyle = '#ffffff'; ctx.fill();
  ctx.beginPath(); ctx.ellipse(x, y + 7 * s, 7.5 * s, 4 * s, 0, Math.PI, 0); ctx.fill();
  ctx.restore();
}
// supervised agent = outlined blue square with inner diamond (non-humanoid)
function agent(ctx, x, y, s, a = 1, spin = 0) {
  if (a <= 0 || s <= 0) return; ctx.save(); ctx.globalAlpha *= a;
  glow(ctx, x, y, 30 * s, C.blue, 0.3);
  rr(ctx, x - 15 * s, y - 15 * s, 30 * s, 30 * s, 6 * s); ctx.fillStyle = rgba(C.blue, 0.28); ctx.fill();
  ctx.strokeStyle = '#6f93ff'; ctx.lineWidth = 2.4 * s; ctx.stroke();
  ctx.translate(x, y); ctx.rotate(Math.PI / 4 + spin); ctx.fillStyle = '#ffffff';
  ctx.fillRect(-4.2 * s, -4.2 * s, 8.4 * s, 8.4 * s); ctx.restore();
}
// checkpoint badge: cyan disc + check drawn progressively (site .check-list marker)
function checkBadge(ctx, x, y, r, p, col = C.cyan) {
  if (p <= 0) return; const s = E.outBack(prog(p, 0, 0.55), 2.0), q = E.outCubic(prog(p, 0.35, 1));
  ctx.save(); glow(ctx, x, y, r * 2.4, col, 0.35 * s);
  ctx.beginPath(); ctx.arc(x, y, r * s, 0, 7); ctx.fillStyle = col; ctx.fill();
  ctx.beginPath(); ctx.arc(x, y, r * s + 7, 0, 7); ctx.strokeStyle = rgba(col, 0.3 * s); ctx.lineWidth = 2; ctx.stroke();
  if (q > 0) {
    const pts = [[-0.38, 0.02], [-0.1, 0.3], [0.4, -0.26]];
    const L1 = Math.hypot(0.28, 0.28), L2 = Math.hypot(0.5, 0.56), L = (L1 + L2) * q;
    ctx.beginPath(); ctx.moveTo(x + pts[0][0] * r, y + pts[0][1] * r);
    if (L <= L1) { const u = L / L1; ctx.lineTo(x + lerp(pts[0][0], pts[1][0], u) * r, y + lerp(pts[0][1], pts[1][1], u) * r); }
    else { const u = (L - L1) / L2; ctx.lineTo(x + pts[1][0] * r, y + pts[1][1] * r); ctx.lineTo(x + lerp(pts[1][0], pts[2][0], u) * r, y + lerp(pts[1][1], pts[2][1], u) * r); }
    ctx.strokeStyle = '#fff'; ctx.lineWidth = r * 0.2; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.stroke();
  }
  ctx.restore();
}
// partial straight line (draw-on)
function lineP(ctx, x1, y1, x2, y2, p, col, lw, dash) {
  if (p <= 0) return; ctx.save(); ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(lerp(x1, x2, p), lerp(y1, y2, p));
  ctx.strokeStyle = col; ctx.lineWidth = lw; if (dash) { ctx.setLineDash(dash.a); ctx.lineDashOffset = dash.o || 0; } ctx.stroke(); ctx.restore();
}
// official logo drawing (paths from input/assets/assets__t2s-logo-light.svg)
const LOGO_P = { emblem: LOGO.emblem.map(e => ({ fill: e.fill, p: new Path2D(e.d) })), letters: LOGO.letters.map(e => ({ fill: e.fill, p: new Path2D(e.d) })) };
