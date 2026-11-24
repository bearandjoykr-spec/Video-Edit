// Paper look helpers (2D canvas): paper grain, watercolour washes, wobbly ink, white scissor-cut edges,
// and the paper families (parents, grandparents, children) drawn in the Bear & Joy pen-and-wash style
// (BRAND.md: sketchy pen line, soft watercolour). Everything is seeded, so every frame is identical on every worker.
import { rng } from './kit.js';

export const INK = '#2a2420';   // 먹 (sumi ink)
export const C = { cream: '#F5F0E6', paper: '#FBF6EC', navy: '#1E2D4D', deep: '#173B5C', yellow: '#F6F0BA', blue: '#AECCE6', gold: '#C9A84C', rose: '#E9A3A3' };

export function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }

// ---------------------------------------------------------------- paths
export function smooth(g, pts, closed = true) {
  const n = pts.length, P = i => pts[(i + n) % n];
  g.beginPath(); g.moveTo(...P(0));
  const last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = closed ? P(i - 1) : pts[Math.max(0, i - 1)], p1 = P(i), p2 = closed ? P(i + 1) : pts[Math.min(n - 1, i + 1)], p3 = closed ? P(i + 2) : pts[Math.min(n - 1, i + 2)];
    g.bezierCurveTo(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6, p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1]);
  }
  if (closed) g.closePath();
}
const jit = (pts, a, r) => pts.map(([x, y]) => [x + (r() - 0.5) * a, y + (r() - 0.5) * a]);
const ell = (cx, cy, rx, ry, n = 14) => Array.from({ length: n }, (_, i) => [cx + Math.cos(i / n * Math.PI * 2) * rx, cy + Math.sin(i / n * Math.PI * 2) * ry]);
export { ell };

// ---------------------------------------------------------------- paint
let NOISE = null;
function noiseTile() {
  if (NOISE) return NOISE;
  NOISE = canvas(256, 256); const x = NOISE.getContext('2d'), d = x.createImageData(256, 256), r = rng(7);
  for (let i = 0; i < d.data.length; i += 4) { const v = 200 + r() * 55; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
  x.putImageData(d, 0, 0); return NOISE;
}
// watercolour wash: flat colour, darker pooled edge, paper texture showing through
export function wash(g, pts, color, seed = 1, o = {}) {
  const r = rng(seed);
  g.save();
  smooth(g, jit(pts, o.wob ?? 3, r)); g.fillStyle = color; g.globalAlpha = o.alpha ?? 0.8; g.fill();
  g.clip();
  g.globalAlpha = 0.22; g.lineWidth = o.edge ?? 10; g.strokeStyle = shade(color, -0.28); g.filter = 'blur(3px)'; g.stroke(); g.filter = 'none';
  g.globalAlpha = 1; g.globalCompositeOperation = 'multiply'; g.fillStyle = g.createPattern(noiseTile(), 'repeat'); g.fill();
  if (o.light !== false) { // a soft light bloom where the brush lifted
    const b = g.getTransform(); void b;
    const [cx, cy] = pts.reduce((a, p) => [a[0] + p[0] / pts.length, a[1] + p[1] / pts.length], [0, 0]);
    const rad = Math.max(...pts.map(p => Math.hypot(p[0] - cx, p[1] - cy)));
    const gr = g.createRadialGradient(cx - rad * 0.3, cy - rad * 0.35, 0, cx - rad * 0.3, cy - rad * 0.35, rad);
    gr.addColorStop(0, 'rgba(255,255,255,0.35)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.globalCompositeOperation = 'soft-light'; g.fillStyle = gr; g.fill();
  }
  g.restore();
}
// ink brush (먹선): one tapered stroke with a little pressure wobble and a dry, broken second pass
export function ink(g, pts, seed = 1, o = {}) {
  const r = rng(seed + 99), closed = o.closed ?? true;
  const path = sample(jit(pts, o.wob ?? 2.2, r), closed);
  const n = path.length, W0 = (o.w ?? 3.2) * 1.25;
  g.save(); g.lineCap = 'round'; g.lineJoin = 'round'; g.strokeStyle = o.color || INK;
  const ph = r() * 10;
  for (let pass = 0; pass < (o.passes ?? 2); pass++) {
    g.globalAlpha = pass ? 0.32 : 0.88;
    for (let i = 1; i < n; i++) {
      const u = i / (n - 1), taper = closed ? 1 : Math.min(1, u * 5, (1 - u) * 4 + 0.25);
      const press = 0.72 + 0.38 * Math.sin(u * 9 + ph) * Math.sin(u * 3.3 + ph * 2);
      if (pass && Math.sin(i * 1.7 + ph) > 0.35) continue;          // dry-brush gaps
      g.lineWidth = Math.max(0.6, W0 * taper * press * (pass ? 0.6 : 1));
      g.beginPath(); g.moveTo(path[i - 1][0] + (pass ? 1.2 : 0), path[i - 1][1] + (pass ? 0.8 : 0)); g.lineTo(path[i][0] + (pass ? 1.2 : 0), path[i][1] + (pass ? 0.8 : 0)); g.stroke();
    }
  }
  g.restore();
}
// sample a smooth (Catmull-Rom) curve into points
function sample(pts, closed, per = 10) {
  const n = pts.length, P = i => closed ? pts[(i + n) % n] : pts[Math.max(0, Math.min(n - 1, i))], out = [];
  const last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = P(i - 1), p1 = P(i), p2 = P(i + 1), p3 = P(i + 2);
    for (let k = 0; k < per; k++) { const t = k / per, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map(d => 0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2 + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3))); }
  }
  out.push(closed ? out[0] : pts[n - 1]); return out;
}
export function shade(hex, k) {
  const n = parseInt(hex.slice(1), 16); let [r, g, b] = [n >> 16, (n >> 8) & 255, n & 255];
  const f = v => Math.round(k < 0 ? v * (1 + k) : v + (255 - v) * k);
  return `rgb(${f(r)},${f(g)},${f(b)})`;
}
// paper sheet with fibres and a soft tint
export function paperTex(w, h, base = C.paper, seed = 3, o = {}) {
  const c = canvas(w, h), g = c.getContext('2d'), r = rng(seed);
  g.fillStyle = base; g.fillRect(0, 0, w, h);
  g.globalCompositeOperation = 'multiply'; g.globalAlpha = o.grain ?? 0.5; g.fillStyle = g.createPattern(noiseTile(), 'repeat'); g.fillRect(0, 0, w, h);
  g.globalCompositeOperation = 'source-over';
  for (let i = 0; i < (o.fibres ?? 260) * 0.25; i++) { // 한지: long, curling mulberry fibres
    let x = r() * w, y = r() * h, a = r() * Math.PI * 2; g.strokeStyle = `rgba(${r() < 0.5 ? '255,255,250' : '150,120,80'},${0.10 + r() * 0.12})`; g.lineWidth = 0.6 + r() * 0.8;
    g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 8; k++) { a += (r() - 0.5) * 0.9; x += Math.cos(a) * 9; y += Math.sin(a) * 9; g.lineTo(x, y); } g.stroke();
  }
  for (let i = 0; i < (o.fibres ?? 260); i++) { // fibres
    const x = r() * w, y = r() * h, a = r() * Math.PI, l = 6 + r() * 22;
    g.strokeStyle = `rgba(120,100,70,${0.05 + r() * 0.07})`; g.lineWidth = 0.8; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke();
  }
  if (o.age !== false) { // vintage: foxing spots and a faint tea-stain ring
    for (let i = 0; i < (o.spots ?? 14); i++) { const x = r() * w, y = r() * h, rr = 2 + r() * 9; g.fillStyle = `rgba(150,105,55,${0.05 + r() * 0.10})`; g.beginPath(); g.arc(x, y, rr, 0, 7); g.fill(); }
    if (o.ring !== false && w > 600) { const x = w * (0.15 + r() * 0.7), y = h * (0.15 + r() * 0.7), rr = Math.min(w, h) * (0.08 + r() * 0.06);
      g.strokeStyle = 'rgba(150,100,50,0.10)'; g.lineWidth = 5; g.beginPath(); g.arc(x, y, rr, 0.3, 5.9); g.stroke(); }
  }
  if (o.vignette !== false) { const v = g.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.3, w / 2, h / 2, Math.max(w, h) * 0.75); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(110,80,40,0.10)'); g.fillStyle = v; g.fillRect(0, 0, w, h); }
  g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
  return c;
}
// white scissor-cut edge around anything with alpha, plus a hairline grey edge so it reads on white too
export function sticker(src, pad = 14, o = {}) {
  const w = src.width + pad * 2, h = src.height + pad * 2, c = canvas(w, h), g = c.getContext('2d');
  const sil = canvas(w, h), s = sil.getContext('2d');
  s.drawImage(src, pad, pad); s.globalCompositeOperation = 'source-in'; s.fillStyle = o.edge || '#fffdf7'; s.fillRect(0, 0, w, h);
  const r = rng(o.seed || 5);
  // grey hairline (the cut edge), then the white border, then the art
  for (let i = 0; i < 28; i++) { const a = i / 28 * Math.PI * 2; g.globalAlpha = 0.5; g.filter = 'brightness(0.72)'; g.drawImage(sil, Math.cos(a) * (pad + 1.5), Math.sin(a) * (pad + 1.5)); }
  g.filter = 'none'; g.globalAlpha = 1;
  for (let i = 0; i < 28; i++) { const a = i / 28 * Math.PI * 2, rr = pad * (0.86 + r() * 0.14); g.drawImage(sil, Math.cos(a) * rr, Math.sin(a) * rr); }
  g.drawImage(src, pad, pad);
  return c;
}
export function imgCanvas(img, maxW = 1024) {
  const k = Math.min(1, maxW / img.width), c = canvas(Math.round(img.width * k), Math.round(img.height * k));
  c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); return c;
}
// handwritten text
export function hand(g, text, x, y, o = {}) {
  g.save(); g.font = `${o.weight || 700} ${o.size || 60}px ${o.font || 'Gaegu, PatrickHand, sans-serif'}`;
  g.textAlign = o.align || 'center'; g.textBaseline = o.base || 'middle'; g.fillStyle = o.color || INK;
  if (o.rot) { g.translate(x, y); g.rotate(o.rot); x = 0; y = 0; }
  g.fillText(text, x, y); g.restore();
}

// ---------------------------------------------------------------- the paper families
// A seated person, front view, legs crossed on a rug, arms coming round to the front.
// Body and head are separate pieces so the head can tilt and talk. 'book' draws an open book in the hands.
// Families drawn as in a vintage Korean ink-and-colour (수묵담채) picture: hanbok jeogori with a white collar band (동정) and a tied
// ribbon (고름), 색동 rainbow sleeves on the children, braids with a red 댕기 for girls, a hairpin bun (쪽머리 + 비녀) for mum and grandma.
const SAEKDONG = ['#c8553d', '#e2c271', '#7fa36a', '#5b7a99', '#e6b5ae', '#8e4a5a'];
export const PEOPLE = {
  mum: { adult: true, top: '#e9b9ae', bottom: '#6a86a6', goreum: '#8e4a5a', hair: '#2a2420', hairStyle: 'jjok', skin: '#f3dcc4', book: '#5b7a99' },
  dad: { adult: true, top: '#a9cbbf', bottom: '#56606f', goreum: '#5b7a99', hair: '#2a2420', hairStyle: 'short', skin: '#efd3b6', book: '#c8553d' },
  grandma: { adult: true, top: '#e6dcc4', bottom: '#7b6a8e', goreum: '#8e4a5a', hair: '#cfcac0', hairStyle: 'jjok', skin: '#f2dac2', glasses: true, book: '#7fa36a' },
  girl: { top: '#ecd27e', bottom: '#d0614a', goreum: '#c8553d', hair: '#2a2420', hairStyle: 'braid', skin: '#f6dfc8', saekdong: true, yeonji: true },
  boy: { top: '#bccb8e', bottom: '#5b7a99', goreum: '#5b7a99', hair: '#2a2420', hairStyle: 'boy', skin: '#f2d8bd', saekdong: true },
  girl2: { top: '#efc2b8', bottom: '#8fb7ab', goreum: '#8e4a5a', hair: '#2a2420', hairStyle: 'braid', skin: '#f5dcc4', saekdong: true, yeonji: true },
  boy2: { top: '#a9cbbf', bottom: '#8e4a5a', goreum: '#c8553d', hair: '#2a2420', hairStyle: 'boy', skin: '#f2d6ba', saekdong: true },
};
const BW = 440, BH = 400; // body canvas
export function drawBody(p, seed = 1) {
  const c = canvas(BW, BH), g = c.getContext('2d');
  // a full skirt / baji folded in a cross-legged sit
  const legs = [[30, 320], [92, 284], [220, 296], [348, 284], [410, 320], [418, 364], [350, 392], [220, 384], [90, 392], [22, 364]];
  wash(g, legs, p.bottom, seed + 1); ink(g, legs, seed + 1);
  for (const x of [160, 280]) ink(g, [[x, 300], [x - 8, 380]], seed + x, { closed: false, w: 1.8, passes: 1 });   // fold lines
  for (const x of [118, 322]) { const f = ell(x, 364, 32, 14, 10); wash(g, f, '#f4efe6', seed + x); ink(g, f, seed + x, { w: 2.2 }); }   // 버선
  const neck = [[202, 44], [238, 44], [240, 92], [200, 92]]; wash(g, neck, p.skin, seed + 3, { light: false }); ink(g, neck, seed + 3, { w: 2 });
  // jeogori: short jacket over a long skirt/baji
  const torso = [[162, 80], [278, 80], [316, 108], [312, 200], [304, 286], [136, 286], [128, 200], [124, 108]];
  wash(g, torso, p.top, seed + 4); ink(g, torso, seed + 4);
  // crossed collar (깃) with the white band (동정), right over left
  const git = [[200, 82], [222, 130], [246, 82], [258, 84], [226, 160], [214, 160], [188, 84]];
  wash(g, git, shade(p.top, -0.18), seed + 5, { light: false }); ink(g, git, seed + 5, { w: 2 });
  ink(g, [[198, 84], [222, 138], [250, 84]], seed + 6, { closed: false, w: 4.5, color: '#fbf7ee', passes: 1 });
  // goreum: the long ribbon tied at the chest
  const bow = [[212, 160], [246, 150], [250, 170], [220, 172]]; wash(g, bow, p.goreum, seed + 7, { light: false }); ink(g, bow, seed + 7, { w: 2 });
  for (const [x0, x1] of [[222, 206], [230, 236]]) { const rib = [[x0, 168], [x1, 260], [x1 + 14, 262], [x0 + 10, 168]]; wash(g, rib, p.goreum, seed + x0, { light: false }); ink(g, rib, seed + x0, { w: 1.8 }); }
  // sleeves round to the hands; children get 색동 rainbow stripes
  const armL = [[126, 110], [96, 200], [112, 270], [190, 292], [198, 262], [140, 246], [132, 200], [150, 128]];
  for (const [k, a] of [[0, armL], [1, armL.map(([x, y]) => [BW - x, y])]]) {
    wash(g, a, shade(p.top, -0.06), seed + 8 + k);
    if (p.saekdong) { g.save(); smooth(g, a); g.clip(); for (let b = 0; b < 6; b++) { g.globalAlpha = 0.78; g.fillStyle = SAEKDONG[b]; g.fillRect(0, 128 + b * 22, BW, 22); } g.restore(); }
    ink(g, a, seed + 8 + k);
    const cuff = k ? [[BW - 198, 262], [BW - 190, 292]] : [[198, 262], [190, 292]]; ink(g, cuff, seed + 30 + k, { closed: false, w: 4, color: '#fbf7ee', passes: 1 });
  }
  for (const x of [196, 244]) { const h = ell(x, 276, 20, 17, 10); wash(g, h, p.skin, seed + x, { light: false }); ink(g, h, seed + x, { w: 2.2 }); }
  if (p.book) { // an open book held in front
    const cov = [[96, 236], [220, 254], [344, 236], [350, 322], [220, 336], [90, 322]];
    wash(g, cov, p.book, seed + 8, { light: false }); ink(g, cov, seed + 8);
    const L = [[108, 230], [214, 248], [214, 322], [104, 310]], R = L.map(([x, y]) => [BW - x, y]);
    for (const [k, pg] of [[0, L], [1, R]]) {
      wash(g, pg, '#fbf6ea', seed + 9 + k, { light: false }); ink(g, pg, seed + 9 + k, { w: 2.2 });
      for (let i = 0; i < 4; i++) { const x0 = k ? 236 : 124, y0 = 262 + i * 13; ink(g, [[x0, y0], [x0 + 66, y0 + (k ? -5 : 5)]], seed + 20 + i + k * 9, { closed: false, w: 1.3, color: '#9a8f80', passes: 1 }); }
    }
  }
  return c;
}
const HW = 280, HH = 300; // head canvas; chin at y ~ 250
export function drawHead(p, state = 'idle', seed = 1) { // state: idle | talk | blink
  const c = canvas(HW, HH), g = c.getContext('2d'), cx = 140, cy = 158;
  if (p.hairStyle === 'braid') { // a long braid behind with a red 댕기
    const br = [[190, 200], [214, 230], [206, 290], [190, 296], [180, 240]]; wash(g, br, p.hair, seed + 2, { light: false }); ink(g, br, seed + 2, { w: 2.2 });
    const dg = [[186, 282], [216, 290], [210, 300], [184, 296]]; wash(g, dg, '#c8553d', seed + 3, { light: false });
  }
  if (p.hairStyle === 'jjok') { // low bun at the nape with a hairpin (비녀)
    const bun = ell(cx + 72, 214, 36, 28, 12); wash(g, bun, p.hair, seed + 3, { light: false }); ink(g, bun, seed + 3);
    ink(g, [[cx + 22, 222], [cx + 128, 202]], seed + 4, { closed: false, w: 5, color: '#c9a84c', passes: 1 });
  }
  for (const s of [-1, 1]) { const e = ell(cx + s * 86, cy + 8, 16, 20, 10); wash(g, e, p.skin, seed + 4 + s, { light: false }); ink(g, e, seed + 4 + s, { w: 2 }); }
  const face = ell(cx, cy, p.adult ? 82 : 86, p.adult ? 90 : 84, 16); wash(g, face, p.skin, seed + 5); ink(g, face, seed + 5);
  // hair: smooth, centre-parted ink wash (adults and girls); a soft cap for boys and dad
  const top = { jjok: [[58, 140], [62, 80], [100, 56], [140, 50], [180, 56], [218, 80], [222, 140], [198, 100], [142, 72], [138, 72], [82, 100]],
    braid: [[58, 140], [62, 80], [100, 54], [140, 48], [180, 54], [218, 80], [222, 140], [196, 104], [142, 76], [138, 76], [84, 104]],
    short: [[58, 126], [62, 74], [140, 50], [218, 74], [222, 126], [196, 98], [140, 90], [84, 98]],
    boy: [[58, 128], [60, 76], [100, 58], [140, 48], [184, 58], [220, 76], [222, 128], [196, 104], [166, 110], [140, 100], [110, 110], [84, 104]] }[p.hairStyle];
  wash(g, top, p.hair, seed + 6, { light: false, alpha: 0.9 }); ink(g, top, seed + 6);
  if (p.hairStyle === 'jjok' || p.hairStyle === 'braid') ink(g, [[140, 54], [140, 76]], seed + 7, { closed: false, w: 1.6, color: '#fbf7ee', passes: 1 });   // centre part
  // face in the old-painting manner: short brow strokes, small eyes, a little mouth; 연지 dots for the girls
  const ey = cy + 8;
  for (const s of [-1, 1]) {
    ink(g, [[cx + s * 22, ey - 22], [cx + s * 42, ey - 24]], seed + 10 + s, { closed: false, w: 2.2, passes: 1 });
    if (state === 'blink') ink(g, [[cx + s * 32 - 9, ey], [cx + s * 32, ey + 3], [cx + s * 32 + 9, ey]], seed + 7, { closed: false, w: 2.6, passes: 1 });
    else { g.fillStyle = INK; g.beginPath(); g.ellipse(cx + s * 32, ey, 6.5, 7.5, 0, 0, Math.PI * 2); g.fill(); g.fillStyle = '#fff'; g.beginPath(); g.arc(cx + s * 32 + 2.2, ey - 2.6, 1.9, 0, Math.PI * 2); g.fill(); }
    g.fillStyle = p.yeonji ? 'rgba(200,70,60,0.55)' : 'rgba(226,128,118,0.28)'; g.beginPath(); g.arc(cx + s * 50, ey + 30, p.yeonji ? 10 : 15, 0, Math.PI * 2); g.fill();
    if (p.glasses) { g.strokeStyle = INK; g.lineWidth = 2.4; g.beginPath(); g.arc(cx + s * 32, ey, 20, 0, Math.PI * 2); g.stroke(); }
  }
  if (p.glasses) ink(g, [[cx - 12, ey - 2], [cx + 12, ey - 2]], seed + 8, { closed: false, w: 2, passes: 1 });
  if (state === 'talk') { const m = ell(cx, ey + 44, 12, 10, 10); g.fillStyle = '#7a2e36'; smooth(g, m); g.fill(); ink(g, m, seed + 9, { w: 1.8, passes: 1 }); }
  else ink(g, [[cx - 13, ey + 40], [cx, ey + 47], [cx + 13, ey + 40]], seed + 9, { closed: false, w: 2.6, passes: 1 });
  return c;
}
export const BODY = { w: BW, h: BH, neckY: 78 }, HEAD = { w: HW, h: HH, chinY: 250 };

// speech bubble: English (Patrick Hand) with an optional small Korean line (Gaegu)
export function bubble(en, ko = '', o = {}) {
  const W = o.w || 640, H = ko ? 250 : 190, c = canvas(W + 40, H + 70), g = c.getContext('2d');
  const box = [[30, 26], [W * 0.5, 14], [W + 10, 26], [W + 22, H * 0.5], [W + 10, H - 6], [W * 0.5, H + 6], [W * (o.tail === 'right' ? 0.70 : 0.30) + 24, H + 2], [30, H - 6], [16, H * 0.5]];
  const tailX = W * (o.tail === 'right' ? 0.72 : 0.28);
  const tail = [[tailX - 22, H - 2], [tailX + (o.tail === 'right' ? 34 : -34), H + 58], [tailX + 24, H]];
  g.fillStyle = '#fffdf7'; smooth(g, box); g.fill(); g.beginPath(); g.moveTo(...tail[0]); g.lineTo(...tail[1]); g.lineTo(...tail[2]); g.closePath(); g.fill();
  ink(g, box, 3); ink(g, tail, 4, { closed: false, w: 2.8 });
  hand(g, en, (W + 32) / 2, ko ? 92 : H / 2 + 6, { font: o.font || 'PatrickHand', weight: o.font ? 700 : 400, size: o.size || 82, color: o.color || C.deep });
  if (ko) hand(g, ko, (W + 32) / 2, 182, { size: 54, color: '#5b6070' });
  return c;
}

// ---------------------------------------------------------------- props for the real-world scenes
export function drawTree(seed = 1) {
  const c = canvas(520, 760), g = c.getContext('2d');
  const trunk = [[230, 760], [236, 500], [214, 420], [250, 430], [270, 380], [292, 432], [318, 420], [292, 500], [298, 760]];
  wash(g, trunk, '#9a7454', seed); ink(g, trunk, seed);
  for (const [x, y, r, col] of [[160, 330, 130, '#8cbf6e'], [360, 320, 140, '#7fb463'], [260, 200, 170, '#96c877'], [190, 160, 110, '#a3cf82'], [340, 170, 120, '#8cbf6e']]) {
    const blob = ell(x, y, r, r * 0.85, 14); wash(g, blob, col, seed + x); ink(g, blob, seed + x, { w: 2.6, color: '#4f7a3e' });
  }
  for (let i = 0; i < 9; i++) { const x = 120 + (i * 53) % 300, y = 120 + (i * 97) % 260; g.fillStyle = '#e9776b'; g.beginPath(); g.arc(x, y, 9, 0, 7); g.fill(); ink(g, ell(x, y, 9, 9, 8), seed + i, { w: 1.6 }); }
  return c;
}
export function drawTable(seed = 1) { // a low Korean dinner table (밥상), front view, with bowls
  const c = canvas(900, 380), g = c.getContext('2d');
  for (const x of [120, 760]) { const leg = [[x, 230], [x + 30, 230], [x + 26, 370], [x + 4, 370]]; wash(g, leg, '#a77b52', seed + x); ink(g, leg, seed + x); }
  const top = [[40, 170], [860, 170], [880, 200], [870, 250], [30, 250], [20, 200]]; wash(g, top, '#c99a6a', seed); ink(g, top, seed);
  ink(g, [[60, 222], [840, 222]], seed + 3, { closed: false, w: 2, color: '#8a643f', passes: 1 });
  const bowl = (x, w, col, fill, s) => { const b = [[x - w, 120], [x + w, 120], [x + w * 0.7, 175], [x - w * 0.7, 175]]; wash(g, b, col, s); ink(g, b, s);
    const tp = ell(x, 120, w, 16, 12); wash(g, tp, fill, s + 1, { light: false }); ink(g, tp, s + 1, { w: 2.2 }); };
  bowl(230, 70, '#fffdf7', '#ffffff', seed + 10);               // rice
  bowl(450, 80, '#AECCE6', '#e9b46b', seed + 20);               // soup
  const plate = ell(680, 158, 110, 22, 14); wash(g, plate, '#fffdf7', seed + 30); ink(g, plate, seed + 30, { w: 2.4 });
  for (const [x, y] of [[640, 140], [690, 132], [728, 146]]) { const tm = ell(x, y, 26, 24, 10); wash(g, tm, '#e2554a', seed + x); ink(g, tm, seed + x, { w: 2.2 }); }
  ink(g, [[300, 95], [380, 160]], seed + 40, { closed: false, w: 3, color: '#8a643f', passes: 1 }); ink(g, [[312, 90], [392, 156]], seed + 41, { closed: false, w: 3, color: '#8a643f', passes: 1 });
  return c;
}
export function drawBlanket(seed = 1) { // the front of a bed: a patchwork quilt pulled up to the waist
  const c = canvas(1000, 360), g = c.getContext('2d');
  const q = [[20, 70], [300, 40], [700, 40], [980, 70], [990, 340], [10, 340]]; wash(g, q, '#F6F0BA', seed); ink(g, q, seed);
  g.save(); P_clip(g, q);
  for (let i = 0; i < 9; i++) for (let j = 0; j < 4; j++) if ((i + j) % 2) { g.fillStyle = 'rgba(174,204,230,0.75)'; g.fillRect(i * 112, 40 + j * 80, 112, 80); }
  g.restore(); ink(g, q, seed + 1, { w: 2.4 });
  for (let i = 1; i < 9; i++) ink(g, [[i * 112, 46], [i * 112, 336]], seed + i, { closed: false, w: 1.4, color: '#8b98ad', passes: 1 });
  return c;
}
function P_clip(g, pts) { smooth(g, pts); g.clip(); }
export function drawHeadboard(seed = 1) {
  const c = canvas(1000, 560), g = c.getContext('2d');
  const h = [[40, 560], [40, 170], [200, 60], [500, 20], [800, 60], [960, 170], [960, 560]]; wash(g, h, '#c99a6a', seed); ink(g, h, seed);
  const p = [[180, 560], [180, 250], [500, 200], [820, 250], [820, 560]]; wash(g, p, '#fffdf7', seed + 2, { light: false }); ink(g, p, seed + 2, { w: 2.4 }); // pillow
  return c;
}
export function drawAha(seed = 1) {
  const c = canvas(360, 420), g = c.getContext('2d');
  for (let i = 0; i < 8; i++) { const a = -Math.PI / 2 + (i - 3.5) * 0.36; ink(g, [[180 + Math.cos(a) * 130, 150 + Math.sin(a) * 130], [180 + Math.cos(a) * 168, 150 + Math.sin(a) * 168]], seed + i, { closed: false, w: 5, color: '#e0a92e', passes: 1 }); }
  const bulb = ell(180, 160, 92, 100, 16); wash(g, bulb, '#F6E07E', seed); ink(g, bulb, seed);
  const base = [[140, 250], [220, 250], [214, 300], [146, 300]]; wash(g, base, '#9aa0ad', seed + 3); ink(g, base, seed + 3);
  hand(g, 'Aha!', 180, 368, { font: 'PatrickHand', weight: 400, size: 86, color: '#c0605e' });
  return c;
}
export function starterCard([en, ko], seed = 1, col = '#a9cbbf') { // a Walkbook conversation-starter card: English question, its Korean line
  const c = canvas(700, 420), g = c.getContext('2d');
  const box = [[20, 24], [680, 14], [686, 404], [14, 410]]; wash(g, box, '#fbf6ea', seed, { light: false }); ink(g, box, seed);
  const band = [[20, 24], [680, 14], [682, 96], [18, 104]]; wash(g, band, col, seed + 1, { light: false });
  hand(g, '대화를 여는 질문', 350, 62, { font: 'Batang', weight: 700, size: 42, color: '#3a2e24' });
  const words = en.split(' '); let l1 = '', l2 = '';
  for (const w of words) ((l1 + ' ' + w).length < 20 && !l2 ? (l1 = (l1 + ' ' + w).trim()) : (l2 = (l2 + ' ' + w).trim()));
  hand(g, l1, 350, l2 ? 170 : 200, { font: 'PatrickHand', weight: 400, size: 66, color: INK });
  if (l2) hand(g, l2, 350, 240, { font: 'PatrickHand', weight: 400, size: 66, color: INK });
  hand(g, ko, 350, 336, { font: 'Batang', weight: 700, size: 40, color: '#6b4a32' });
  return c;
}
export function picnic(g, x, y, rx, ry, seed = 1) { // a checked picnic blanket printed on the page
  const pts = ell(x, y, rx, ry, 18); wash(g, pts, '#f3e3c3', seed, { alpha: 0.9 });
  g.save(); smooth(g, pts); g.clip(); g.globalAlpha = 0.55; g.fillStyle = '#e88f86';
  for (let i = -12; i < 12; i++) { g.fillRect(x + i * 40, y - ry, 20, ry * 2); g.fillRect(x - rx, y + i * 30, rx * 2, 14); }
  g.restore(); ink(g, pts, seed, { w: 2.4, color: '#b26a5f' });
}

// ---------------------------------------------------------------- Korean vintage props
export function drawPine(seed = 1) { // 소나무: a leaning trunk and flat, layered needle clouds
  const c = canvas(560, 800), g = c.getContext('2d');
  const trunk = [[250, 800], [262, 600], [230, 470], [262, 360], [300, 250], [322, 260], [290, 370], [270, 470], [302, 600], [300, 800]];
  wash(g, trunk, '#8a6a52', seed); ink(g, trunk, seed, { w: 3.6 });
  for (let i = 0; i < 6; i++) ink(g, [[262, 760 - i * 90], [286, 750 - i * 90]], seed + i, { closed: false, w: 2, passes: 1 });
  for (const [x, y, rx, ry] of [[150, 420, 120, 46], [380, 330, 140, 50], [250, 220, 150, 52], [330, 130, 120, 44], [110, 300, 90, 36]]) {
    const pts = ell(x, y, rx, ry, 14); wash(g, pts, '#5f7f5a', seed + x, { alpha: 0.85 }); ink(g, pts, seed + x, { w: 2.4, color: '#2f3a2a' });
    for (let k = 0; k < 9; k++) ink(g, [[x - rx * 0.8 + k * rx * 0.2, y + ry * 0.1], [x - rx * 0.7 + k * rx * 0.2, y - ry * 0.5]], seed + x + k, { closed: false, w: 1.2, color: '#2f3a2a', passes: 1 });
  }
  return c;
}
export function mountains(g, W, layers, seed = 1) { // ink-wash mountain ranges fading into mist
  layers.forEach(([y, amp, col, alpha], li) => {
    const r = rng(seed + li * 13), pts = [[-20, W + 20], [-20, y]];
    const f1 = r() * 6, f2 = r() * 6, f3 = r() * 6;
    for (let x = 0; x <= W + 20; x += 24) { const v = 0.55 * Math.sin(x * 0.0045 + f1 + li * 1.7) + 0.3 * Math.sin(x * 0.011 + f2) + 0.15 * Math.sin(x * 0.027 + f3);
      pts.push([x, y - Math.max(0, 0.35 + v) * amp]); }
    pts.push([W + 20, W + 20]);
    g.save(); g.globalAlpha = alpha; const gr = g.createLinearGradient(0, y - amp, 0, y + amp * 1.5); gr.addColorStop(0, col); gr.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = gr; g.beginPath(); g.moveTo(...pts[0]); pts.forEach(p => g.lineTo(...p)); g.closePath(); g.fill(); g.restore();
    ink(g, pts.slice(2, -1), seed + li, { closed: false, w: 2.6, color: col, passes: 1 });
  });
}
export function lattice(g, x, y, w, h, seed = 1) { // 창호: wooden lattice with hanji panes
  g.fillStyle = 'rgba(251,246,234,0.95)'; g.fillRect(x, y, w, h);
  g.fillStyle = 'rgba(255,220,150,0.25)'; g.fillRect(x, y, w, h);
  const step = w / 6;
  for (let i = 1; i < 6; i++) ink(g, [[x + i * step, y], [x + i * step, y + h]], seed + i, { closed: false, w: 4, color: '#6b4a32', passes: 1 });
  for (let j = 1; j < 8; j++) ink(g, [[x, y + j * h / 8], [x + w, y + j * h / 8]], seed + 20 + j, { closed: false, w: 4, color: '#6b4a32', passes: 1 });
  ink(g, [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], seed + 40, { w: 7, color: '#5a3c28' });
}
export function seal(g, x, y, size, text, seed = 1) { // 낙관: a red seal stamp
  g.save(); g.translate(x, y); g.rotate(-0.04); g.globalAlpha = 0.85; g.fillStyle = '#b8352b'; g.fillRect(-size / 2, -size / 2, size, size);
  g.globalCompositeOperation = 'destination-out'; const r = rng(seed); for (let i = 0; i < 40; i++) { g.beginPath(); g.arc((r() - 0.5) * size, (r() - 0.5) * size, r() * 2.2, 0, 7); g.fill(); }
  g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1;
  g.fillStyle = '#fbf2df'; g.font = `400 ${size * 0.42}px Brush`; g.textAlign = 'center'; g.textBaseline = 'middle';
  const ch = [...text]; if (ch.length <= 2) g.fillText(text, 0, 2); else { g.fillText(ch.slice(0, 2).join(''), 0, -size * 0.2); g.fillText(ch.slice(2).join(''), 0, size * 0.24); }
  g.restore();
}
// cut-paper flowers in the ink-and-colour style (owner, 24 Nov 2026: "create your own paper flowers"): brushed stems and leaves,
// plum-blossom and peony-like heads in traditional colours, each blossom its own little paper shape
export function drawPaperFlowers(seed = 1, w = 1000, h = 360, n = 9) {
  const c = canvas(w, h), g = c.getContext('2d'), r = rng(seed);
  const cols = ['#c8553d', '#e6a3a8', '#e2c271', '#f4ede0', '#d27a8a', '#8e4a5a'];
  const heads = [];
  for (let i = 0; i < n; i++) {
    const x = 50 + (i + r() * 0.6) * (w - 100) / n, top = 70 + r() * 120, lean = (r() - 0.5) * 60;
    ink(g, [[x, h - 6], [x + lean * 0.4, (h + top) / 2], [x + lean, top]], seed + i, { closed: false, w: 5, color: '#4f6a45', passes: 1 });
    for (const s of [-1, 1]) { const ly = h - 60 - r() * 90, lx = x + lean * 0.25;           // a pair of brushed leaves
      const leaf = [[lx, ly], [lx + s * 44, ly - 38], [lx + s * 90, ly - 20], [lx + s * 44, ly + 4]]; wash(g, leaf, '#7f9a64', seed + i * 3 + s, { light: false }); ink(g, leaf, seed + i * 3 + s, { w: 1.8, color: '#3f5a38', passes: 1 }); }
    heads.push([x + lean, top, cols[i % cols.length], i]);
  }
  for (const [x, y, col, i] of heads) {                                                        // the blossoms on top
    const big = i % 3 === 1, pr = big ? 44 : 34, k = big ? 7 : 5;
    for (let p = 0; p < k; p++) { const a = p / k * Math.PI * 2 + i; const px = x + Math.cos(a) * pr, py = y + Math.sin(a) * pr * 0.9;
      const pet = ell(px, py, pr * 0.72, pr * 0.62, 10); g.save(); g.shadowColor = 'rgba(60,40,20,0.25)'; g.shadowBlur = 4; g.shadowOffsetY = 2;
      wash(g, pet, col, seed + i * 11 + p, { light: false, alpha: 0.95 }); g.restore(); ink(g, pet, seed + i * 11 + p, { w: 1.6, passes: 1 }); }
    const ctr = ell(x, y, pr * 0.38, pr * 0.38, 8); wash(g, ctr, '#e2a92e', seed + i, { light: false }); ink(g, ctr, seed + i, { w: 1.4, passes: 1 });
    for (let d = 0; d < 6; d++) { const a = d * 1.05; g.fillStyle = '#6b4a32'; g.beginPath(); g.arc(x + Math.cos(a) * pr * 0.22, y + Math.sin(a) * pr * 0.22, 2.2, 0, 7); g.fill(); }
  }
  return c;
}
