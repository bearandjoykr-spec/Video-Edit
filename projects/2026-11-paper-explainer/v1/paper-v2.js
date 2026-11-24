// Paper look helpers (2D canvas): paper grain, watercolour washes, wobbly ink, white scissor-cut edges,
// and the paper families (parents, grandparents, children) drawn in the Bear & Joy pen-and-wash style
// (BRAND.md: sketchy pen line, soft watercolour). Everything is seeded, so every frame is identical on every worker.
import { rng } from './kit.js';

export const INK = '#2b2d3a';
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
  smooth(g, jit(pts, o.wob ?? 3, r)); g.fillStyle = color; g.globalAlpha = o.alpha ?? 0.92; g.fill();
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
// sketchy pen line: two loose passes
export function ink(g, pts, seed = 1, o = {}) {
  const r = rng(seed + 99);
  g.save(); g.lineCap = g.lineJoin = 'round'; g.strokeStyle = o.color || INK;
  for (let k = 0; k < (o.passes ?? 2); k++) {
    g.globalAlpha = k ? 0.45 : 0.9; g.lineWidth = (o.w ?? 3.2) * (k ? 0.7 : 1);
    smooth(g, jit(pts, o.wob ?? 2.6, r), o.closed ?? true); g.stroke();
  }
  g.restore();
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
export const PEOPLE = {
  mum: { adult: true, top: '#E7A4A0', bottom: '#7088B8', hair: '#4a3328', hairStyle: 'long', skin: '#F3D4B8', book: '#1E3A66' },
  dad: { adult: true, top: '#8DB3D3', bottom: '#4D5A70', hair: '#2d2724', hairStyle: 'short', skin: '#EFCDB0', book: '#E9C46A' },
  grandma: { adult: true, top: '#B9A6D2', bottom: '#8E7B6B', hair: '#d9d6d0', hairStyle: 'bun', skin: '#F2D5BD', glasses: true, book: '#6E9E6A' },
  girl: { top: '#F4DE7E', bottom: '#E8896B', hair: '#3b2a22', hairStyle: 'pigtails', skin: '#F6D9C0' },
  boy: { top: '#9CCB8C', bottom: '#5E7FA8', hair: '#33261f', hairStyle: 'boy', skin: '#F1D2B6' },
  girl2: { top: '#F3B6C8', bottom: '#7C9CC9', hair: '#2f231d', hairStyle: 'bob', skin: '#F4D7BE' },
  boy2: { top: '#AECCE6', bottom: '#C98A5A', hair: '#3a2b22', hairStyle: 'boy', skin: '#F2D3B5' },
};
const BW = 440, BH = 400; // body canvas
export function drawBody(p, seed = 1) {
  const c = canvas(BW, BH), g = c.getContext('2d');
  // legs crossed: one soft wide shape, feet tucked
  const legs = [[34, 322], [92, 292], [220, 306], [348, 292], [406, 322], [414, 362], [350, 388], [220, 380], [90, 388], [26, 362]];
  wash(g, legs, p.bottom, seed + 1); ink(g, legs, seed + 1);
  ink(g, [[220, 318], [205, 368]], seed + 2, { closed: false, w: 2.2 });
  for (const [x, s] of [[120, -1], [320, 1]]) { const f = ell(x, 360, 34, 16, 10); wash(g, f, '#efe6da', seed + x); ink(g, f, seed + x, { w: 2.4 }); void s; }
  // neck
  const neck = [[200, 40], [240, 40], [242, 92], [198, 92]]; wash(g, neck, p.skin, seed + 3, { light: false }); ink(g, neck, seed + 3, { w: 2.2 });
  // torso
  const torso = [[160, 78], [280, 78], [318, 108], [312, 210], [300, 318], [140, 318], [128, 210], [122, 108]];
  wash(g, torso, p.top, seed + 4); ink(g, torso, seed + 4);
  ink(g, [[198, 82], [220, 104], [242, 82]], seed + 5, { closed: false, w: 2.4 }); // collar
  // arms round to the hands in front of the lap
  const armL = [[126, 110], [96, 200], [112, 270], [190, 292], [198, 262], [140, 246], [132, 200], [150, 128]];
  const armR = armL.map(([x, y]) => [BW - x, y]);
  for (const [k, a] of [[0, armL], [1, armR]]) { wash(g, a, shade(p.top, -0.08), seed + 6 + k); ink(g, a, seed + 6 + k); }
  for (const x of [196, 244]) { const h = ell(x, 276, 22, 18, 10); wash(g, h, p.skin, seed + x, { light: false }); ink(g, h, seed + x, { w: 2.4 }); }
  if (p.book) { // open book held in front
    const cov = [[96, 236], [220, 254], [344, 236], [350, 322], [220, 336], [90, 322]];
    wash(g, cov, p.book, seed + 8, { light: false }); ink(g, cov, seed + 8);
    const L = [[108, 230], [214, 248], [214, 322], [104, 310]], R = L.map(([x, y]) => [BW - x, y]);
    for (const [k, pg] of [[0, L], [1, R]]) {
      wash(g, pg, '#fffaf0', seed + 9 + k, { light: false }); ink(g, pg, seed + 9 + k, { w: 2.4 });
      for (let i = 0; i < 4; i++) { const x0 = k ? 236 : 124, y0 = 262 + i * 13 + (k ? 0 : 0); ink(g, [[x0, y0 + (k ? -4 : 4) * 0], [x0 + 70, y0 + (k ? -6 : 6)]], seed + 20 + i + k * 9, { closed: false, w: 1.6, color: '#9aa0ad', passes: 1 }); }
    }
    // a tiny bear sketched on the page
    const b = ell(282, 300, 9, 9, 8); ink(g, b, seed + 40, { w: 1.6 });
  }
  return c;
}
const HW = 280, HH = 300; // head canvas; chin at y ~ 250
export function drawHead(p, state = 'idle', seed = 1) { // state: idle | talk | blink
  const c = canvas(HW, HH), g = c.getContext('2d'), cx = 140, cy = 158;
  const back = { long: [[48, 120], [60, 60], [140, 34], [220, 60], [232, 120], [244, 250], [200, 268], [140, 236], [80, 268], [36, 250]],
    bob: [[46, 130], [62, 62], [140, 36], [218, 62], [234, 130], [230, 214], [190, 226], [90, 226], [50, 214]] }[p.hairStyle];
  if (back) { wash(g, back, p.hair, seed + 1, { light: false }); ink(g, back, seed + 1); }
  if (p.hairStyle === 'pigtails') for (const s of [-1, 1]) { const t = ell(cx + s * 98, 182, 26, 40, 10); wash(g, t, p.hair, seed + 2 + s, { light: false }); ink(g, t, seed + 2 + s); }
  if (p.hairStyle === 'bun') { const b = ell(cx, 52, 40, 32, 12); wash(g, b, p.hair, seed + 3, { light: false }); ink(g, b, seed + 3); }
  for (const s of [-1, 1]) { const e = ell(cx + s * 88, cy + 6, 18, 22, 10); wash(g, e, p.skin, seed + 4 + s, { light: false }); ink(g, e, seed + 4 + s, { w: 2.4 }); }
  const face = ell(cx, cy, p.adult ? 84 : 88, p.adult ? 92 : 86, 16); wash(g, face, p.skin, seed + 5); ink(g, face, seed + 5);
  // fringe / top hair
  const top = { long: [[60, 128], [64, 76], [140, 50], [216, 76], [222, 128], [182, 96], [128, 112], [92, 104]],
    short: [[60, 126], [62, 72], [140, 52], [218, 72], [222, 126], [196, 100], [140, 92], [84, 100]],
    bun: [[60, 124], [66, 80], [140, 60], [214, 80], [220, 124], [180, 98], [140, 104], [100, 98]],
    pigtails: [[58, 132], [66, 74], [140, 52], [214, 74], [222, 132], [176, 102], [140, 116], [104, 102]],
    bob: [[58, 140], [64, 76], [140, 54], [216, 76], [222, 140], [196, 110], [140, 100], [84, 110]],
    boy: [[58, 128], [60, 76], [100, 58], [140, 48], [184, 58], [220, 76], [222, 128], [196, 104], [166, 112], [140, 100], [110, 112], [84, 104]] }[p.hairStyle];
  wash(g, top, p.hair, seed + 6, { light: false }); ink(g, top, seed + 6);
  // face
  const ey = cy + 8;
  for (const s of [-1, 1]) {
    if (state === 'blink') ink(g, [[cx + s * 32 - 9, ey], [cx + s * 32, ey + 4], [cx + s * 32 + 9, ey]], seed + 7, { closed: false, w: 3 });
    else { g.fillStyle = INK; g.beginPath(); g.ellipse(cx + s * 32, ey, 7, 8.5, 0, 0, Math.PI * 2); g.fill(); g.fillStyle = '#fff'; g.beginPath(); g.arc(cx + s * 32 + 2.5, ey - 3, 2.2, 0, Math.PI * 2); g.fill(); }
    g.fillStyle = 'rgba(236,128,128,0.34)'; g.beginPath(); g.ellipse(cx + s * 52, ey + 30, 17, 11, 0, 0, Math.PI * 2); g.fill();
    if (p.glasses) { g.strokeStyle = INK; g.lineWidth = 2.6; g.beginPath(); g.arc(cx + s * 32, ey, 21, 0, Math.PI * 2); g.stroke(); }
  }
  if (p.glasses) ink(g, [[cx - 11, ey - 2], [cx + 11, ey - 2]], seed + 8, { closed: false, w: 2.4, passes: 1 });
  if (state === 'talk') { const m = ell(cx, ey + 46, 13, 11, 10); g.fillStyle = '#7a2e36'; smooth(g, m); g.fill(); ink(g, m, seed + 9, { w: 2.2 }); g.fillStyle = '#e98b8b'; g.beginPath(); g.ellipse(cx, ey + 52, 7, 4, 0, 0, Math.PI * 2); g.fill(); }
  else ink(g, [[cx - 16, ey + 40], [cx, ey + 49], [cx + 16, ey + 40]], seed + 9, { closed: false, w: 3 });
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
  hand(g, en, (W + 32) / 2, ko ? 92 : H / 2 + 6, { font: 'PatrickHand', weight: 400, size: o.size || 82, color: o.color || C.deep });
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
export function starterCard(q, seed = 1, col = '#AECCE6') {
  const c = canvas(700, 400), g = c.getContext('2d');
  const box = [[20, 24], [680, 14], [686, 384], [14, 390]]; wash(g, box, '#fffdf7', seed, { light: false }); ink(g, box, seed);
  const band = [[20, 24], [680, 14], [682, 96], [18, 104]]; wash(g, band, col, seed + 1, { light: false });
  hand(g, 'Conversation Starter', 350, 62, { font: 'PatrickHand', weight: 400, size: 46, color: '#173B5C' });
  const words = q.split(' '); let l1 = '', l2 = '';
  for (const w of words) ((l1 + ' ' + w).length < 18 && !l2 ? (l1 = (l1 + ' ' + w).trim()) : (l2 = (l2 + ' ' + w).trim()));
  hand(g, l1, 350, l2 ? 196 : 240, { font: 'PatrickHand', weight: 400, size: 76, color: INK });
  if (l2) hand(g, l2, 350, 296, { font: 'PatrickHand', weight: 400, size: 76, color: INK });
  return c;
}
export function picnic(g, x, y, rx, ry, seed = 1) { // a checked picnic blanket printed on the page
  const pts = ell(x, y, rx, ry, 18); wash(g, pts, '#f3e3c3', seed, { alpha: 0.9 });
  g.save(); smooth(g, pts); g.clip(); g.globalAlpha = 0.55; g.fillStyle = '#e88f86';
  for (let i = -12; i < 12; i++) { g.fillRect(x + i * 40, y - ry, 20, ry * 2); g.fillRect(x - rx, y + i * 30, rx * 2, 14); }
  g.restore(); ink(g, pts, seed, { w: 2.4, color: '#b26a5f' });
}
