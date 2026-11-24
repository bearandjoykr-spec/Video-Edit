// Stencil-and-watercolour friends and landmarks for the bear's journey (owner, 24 Nov 2026: "paper animation, stencils, watercolours").
// Drawn by hand in code (the 24 story-card pictures are AI-made and not used, BRAND.md 18 Nov 2026).
// Each shape is printed like a stencil: a flat colour, a slightly offset second pass (misregistration), a sprayed edge,
// a watercolour bloom and a light ink line. Coordinates are in a 400 x 400 box with the ground at y = 380.
import { rng } from './kit.js';
import { canvas, smooth, ell, ink, shade, INK } from './paper.js';

const E = (cx, cy, rx, ry, n = 16) => ell(cx, cy, rx, ry, n);
const R = (x0, y0, x1, y1) => [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];

// straight-edged shapes (rectangles, triangles, towers) keep crisp stencil corners: densify the edges so the brush stays straight
function densify(pts, step = 10) { const out = []; for (let i = 0; i < pts.length; i++) { const [x0, y0] = pts[i], [x1, y1] = pts[(i + 1) % pts.length];
  const n = Math.max(1, Math.round(Math.hypot(x1 - x0, y1 - y0) / step)); for (let k = 0; k < n; k++) out.push([x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n]); } return out; }
const path = (g, pts, sharp) => { if (!sharp) return smooth(g, pts); g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.closePath(); };
let FINE = false;   // landmarks only: fine ink line over a pale watercolour wash (owner, 24 Nov 2026: no drawn friends for now)
// one stencil print of a closed shape
function print(g, pts0, col, seed, o = {}) {
  const r = rng(seed), sharp = o.sharp ?? (pts0.length <= 4 || o.lm), pts = sharp ? densify(pts0) : pts0;
  g.save();
  // misregistered second pass, darker, a few px off
  g.globalAlpha = FINE ? 0.12 : 0.28; g.fillStyle = shade(col, -0.25); g.translate(3, 2); path(g, pts, sharp); g.fill(); g.translate(-3, -2);
  g.globalAlpha = FINE ? 0.5 : (o.alpha ?? 0.95); g.fillStyle = col; path(g, pts, sharp); g.fill();
  // sprayed edge: fine speckle just outside the shape
  g.globalAlpha = FINE ? 0.12 : 0.35; g.fillStyle = shade(col, -0.15);
  for (let i = 0; i < pts.length; i++) { const [x, y] = pts[i]; for (let k = 0; k < 6; k++) { g.beginPath(); g.arc(x + (r() - 0.5) * 9, y + (r() - 0.5) * 9, 0.6 + r() * 1.3, 0, 7); g.fill(); } }
  // watercolour bloom inside
  g.save(); path(g, pts, sharp); g.clip();
  const [cx, cy] = pts.reduce((a, p) => [a[0] + p[0] / pts.length, a[1] + p[1] / pts.length], [0, 0]);
  const gr = g.createRadialGradient(cx - 10, cy - 14, 2, cx, cy, 120); gr.addColorStop(0, 'rgba(255,255,255,0.32)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.globalAlpha = 1; g.globalCompositeOperation = 'soft-light'; g.fillStyle = gr; g.fillRect(cx - 200, cy - 200, 400, 400); g.restore();
  g.restore();
  if (o.line !== false) ink(g, pts, seed, { w: FINE ? 1.5 : (o.w ?? 2.2), passes: FINE ? 2 : 1, color: o.ink || (FINE ? '#3a3028' : INK), wob: sharp ? 0.8 : (FINE ? 1.2 : 2.2) });
}
const stroke = (g, pts, col, w, seed) => ink(g, pts, seed, { closed: false, w, color: col, passes: 1, wob: 1.2 });
const dot = (g, x, y, r, col) => { g.fillStyle = col; g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); };

// ---------------------------------------------------------------- landmarks (muted, drawn behind the friend)
const LM = {
  oxford(g, s) { print(g, R(120, 210, 280, 330), '#e3d2ac', s); print(g, E(200, 205, 80, 62), '#d8c59a', s + 1); print(g, R(190, 120, 210, 150), '#cdb88c', s + 2); print(g, E(200, 116, 12, 12), '#cdb88c', s + 3);
    for (let x = 135; x < 280; x += 24) stroke(g, [[x, 230], [x, 325]], '#9c8763', 3, s + x);
    print(g, R(300, 250, 360, 380), '#3d5a80', s + 9); dot(g, 350, 318, 4, '#c9a84c'); },          // the little blue door
  london(g, s) { print(g, R(230, 110, 290, 380), '#cdb88c', s); print(g, [[230, 110], [260, 40], [290, 110]], '#9c8763', s + 1); print(g, E(260, 160, 24, 24), '#f4ecd8', s + 2);
    stroke(g, [[260, 160], [260, 146]], INK, 2.4, s + 3); stroke(g, [[260, 160], [270, 165]], INK, 2.4, s + 4); },
  paris(g, s) { print(g, [[200, 40], [215, 140], [250, 260], [300, 380], [255, 380], [230, 320], [170, 320], [145, 380], [100, 380], [150, 260], [185, 140]], '#9c8b7a', s, { lm: true });
    print(g, R(165, 250, 235, 262), '#8a7a6a', s + 1); },
  cairo(g, s) { print(g, [[60, 380], [180, 170], [300, 380]], '#e2c48a', s); print(g, [[230, 380], [320, 230], [400, 380]], '#d6b77a', s + 1); },
  nairobi(g, s) { stroke(g, [[300, 380], [300, 230], [270, 190]], '#7a5a3a', 8, s); stroke(g, [[300, 250], [340, 200]], '#7a5a3a', 6, s + 1);
    print(g, E(300, 180, 110, 26), '#8fa86a', s + 2); print(g, E(340, 168, 60, 18), '#9fb87a', s + 3); },
  chengdu(g, s) { for (const x of [70, 110, 330]) { stroke(g, [[x, 380], [x + 6, 60]], '#6f9a5a', 9, s + x); for (let y = 100; y < 360; y += 60) print(g, [[x, y], [x + 50, y - 20], [x + 60, y - 8]], '#7fae66', s + x + y, { w: 1.4 }); } },
  sydney(g, s) { for (const [x, h, w] of [[150, 150, 70], [215, 120, 60], [275, 95, 50]]) print(g, [[x - w, 330], [x, 330 - h], [x + w * 0.5, 330]], '#f4ecd8', s + x);
    print(g, R(60, 330, 340, 350), '#cdb88c', s + 9); },
  rio(g, s) { print(g, [[40, 380], [80, 220], [140, 150], [200, 210], [230, 380]], '#7fa36a', s); print(g, [[200, 380], [260, 260], [310, 250], [350, 380]], '#8fb37a', s + 1); },
  newyork(g, s) { for (const [x, w, h, c] of [[40, 50, 170, '#a8a29a'], [95, 45, 230, '#9a948c'], [250, 50, 200, '#a8a29a'], [305, 55, 150, '#b3ada4']]) print(g, R(x, 380 - h, x + w, 380), c, s + x);
    print(g, R(150, 120, 230, 380), '#8f8a82', s + 5); print(g, R(170, 70, 210, 120), '#8f8a82', s + 6); print(g, [[183, 70], [190, 20], [197, 70]], '#8f8a82', s + 7); },
  tokyo(g, s) { for (let k = 0; k < 4; k++) { const y = 340 - k * 70, w = 110 - k * 18; print(g, [[200 - w, y], [200 + w, y], [200 + w * 0.7, y - 22], [200 - w * 0.7, y - 22]], '#6b4a32', s + k);
      print(g, R(200 - w * 0.55, y, 200 + w * 0.55, y + 48), '#c8553d', s + 10 + k); } stroke(g, [[200, 110], [200, 50]], '#6b4a32', 5, s + 20); },
  seoul(g, s) { print(g, [[40, 300], [200, 250], [360, 300], [330, 310], [70, 310]], '#4a4744', s, { lm: true }); print(g, R(80, 310, 320, 380), '#c8553d', s + 1);
    for (let x = 100; x < 320; x += 44) print(g, R(x, 320, x + 24, 380), '#7fa36a', s + x, { w: 1.4 });
    stroke(g, [[330, 250], [330, 60]], '#9c8b7a', 7, s + 3); print(g, E(330, 110, 22, 12), '#9c8b7a', s + 4); print(g, [[326, 60], [330, 20], [334, 60]], '#9c8b7a', s + 5); },   // palace gate + N Seoul Tower
};

// ---------------------------------------------------------------- friends (bold, in front)
const FR = {
  lion(g, s) { print(g, E(150, 220, 82, 86), '#b9783a', s); print(g, [[150, 250], [300, 240], [345, 280], [345, 372], [300, 380], [200, 380], [150, 330]], '#d9a55a', s + 1);
    print(g, R(160, 300, 196, 380), '#d9a55a', s + 2); print(g, E(140, 222, 50, 48), '#e0b066', s + 3); print(g, E(106, 240, 22, 16), '#f0d39b', s + 4);
    dot(g, 126, 212, 4, INK); dot(g, 88, 236, 5, INK); stroke(g, [[345, 340], [385, 300]], '#9a5a2a', 5, s + 5); print(g, E(388, 296, 14, 12), '#9a5a2a', s + 6); },
  swan(g, s) { print(g, E(235, 365, 170, 18), '#8fb7c9', s, { line: false, alpha: 0.7 }); print(g, [[120, 330], [200, 290], [320, 300], [372, 330], [330, 362], [180, 366]], '#fbf7ee', s + 1);
    print(g, [[200, 312], [300, 296], [352, 324], [290, 344], [220, 340]], '#ece6d8', s + 2);
    stroke(g, [[155, 320], [130, 250], [162, 200], [150, 160]], '#fbf7ee', 22, s + 3); stroke(g, [[155, 320], [130, 250], [162, 200], [150, 160]], INK, 1.5, s + 4);
    print(g, E(140, 155, 20, 16), '#fbf7ee', s + 5); print(g, [[122, 152], [92, 163], [122, 166]], '#e2853c', s + 6); dot(g, 134, 152, 4, INK); },
  camel(g, s) { for (const x of [120, 160, 240, 280]) print(g, R(x, 280, x + 18, 380), '#b98350', s + x, { w: 1.6 });
    print(g, [[100, 240], [140, 180], [180, 225], [215, 175], [260, 230], [300, 250], [300, 290], [110, 292]], '#c9935a', s);
    print(g, [[290, 250], [320, 200], [330, 150], [372, 140], [382, 160], [346, 170], [336, 258]], '#c9935a', s + 1); dot(g, 360, 150, 4, INK); },
  giraffe(g, s) { for (const x of [135, 165, 235, 265]) print(g, R(x, 285, x + 15, 380), '#d8a64e', s + x, { w: 1.6 });
    print(g, [[120, 250], [260, 230], [292, 262], [260, 292], [130, 296]], '#e2b45a', s); print(g, [[240, 242], [282, 92], [306, 98], [276, 252]], '#e2b45a', s + 1);
    print(g, [[290, 80], [340, 86], [342, 100], [292, 104]], '#e2b45a', s + 2); for (const x of [296, 306]) stroke(g, [[x, 82], [x, 64]], '#8a5a2a', 3, s + x);
    for (const [x, y] of [[150, 262], [190, 255], [230, 270], [262, 175], [255, 215], [280, 130]]) print(g, E(x, y, 11, 9), '#a8652d', s + x + y, { line: false }); dot(g, 322, 90, 3.5, INK); },
  panda(g, s) { print(g, E(200, 305, 92, 78), '#fbf7ee', s); for (const x of [128, 272]) print(g, E(x, 285, 28, 46), '#2a2420', s + x); for (const x of [150, 250]) print(g, E(x, 365, 36, 20), '#2a2420', s + x + 1);
    print(g, E(200, 182, 72, 62), '#fbf7ee', s + 1); for (const x of [146, 254]) print(g, E(x, 130, 22, 20), '#2a2420', s + x + 2);
    for (const x of [176, 224]) { print(g, E(x, 182, 17, 13), '#2a2420', s + x + 3, { line: false }); dot(g, x + 2, 180, 3.5, '#fff'); } dot(g, 200, 206, 7, INK); },
  koala(g, s) { stroke(g, [[330, 380], [300, 60]], '#8a6a4a', 22, s); print(g, E(220, 290, 74, 82), '#9aa1a8', s + 1); print(g, E(220, 300, 40, 52), '#c4c8cc', s + 2, { line: false });
    for (const x of [138, 302]) { print(g, E(x, 140, 38, 34), '#9aa1a8', s + x); print(g, E(x, 142, 20, 18), '#e8e2d8', s + x + 1, { line: false }); }
    print(g, E(220, 170, 74, 62), '#9aa1a8', s + 3); print(g, E(220, 186, 18, 24), '#3a3532', s + 4); dot(g, 186, 162, 5, INK); dot(g, 254, 162, 5, INK);
    print(g, E(290, 230, 34, 18), '#9aa1a8', s + 5); },
  toucan(g, s) { stroke(g, [[40, 320], [370, 300]], '#7a5a3a', 12, s); print(g, R(240, 300, 270, 370), '#2a2420', s + 1); print(g, E(240, 240, 56, 80), '#2a2420', s + 2);
    print(g, E(214, 205, 30, 34), '#f6e07e', s + 3); print(g, [[190, 170], [86, 182], [70, 204], [190, 212]], '#f0913a', s + 4); print(g, [[86, 182], [70, 204], [100, 200]], '#2a2420', s + 5, { line: false });
    print(g, E(214, 172, 12, 12), '#7fb0d8', s + 6); dot(g, 214, 172, 4, INK); },
  sparrow(g, s) { stroke(g, [[40, 330], [370, 318]], '#7a5a3a', 10, s); print(g, E(220, 270, 76, 50), '#a87a4f', s + 1); print(g, [[280, 250], [350, 230], [330, 270]], '#8a5f3a', s + 2);
    print(g, E(240, 262, 44, 22), '#8a5f3a', s + 3); print(g, E(160, 232, 38, 34), '#8a5f3a', s + 4); print(g, E(170, 248, 22, 16), '#e8dcc8', s + 5, { line: false });
    print(g, [[124, 228], [104, 236], [124, 240]], '#e2b45a', s + 6); dot(g, 150, 224, 4, INK); stroke(g, [[210, 318], [205, 332]], '#7a5a3a', 3, s + 7); },
  crane(g, s) { for (const x of [218, 246]) stroke(g, [[x, 230], [x - 6, 380]], INK, 3, s + x); print(g, E(232, 210, 72, 40), '#fbf7ee', s);
    print(g, [[290, 196], [356, 214], [300, 232]], '#2a2420', s + 1); stroke(g, [[178, 205], [152, 140], [150, 96]], '#fbf7ee', 15, s + 2); stroke(g, [[178, 205], [152, 140], [150, 96]], INK, 1.4, s + 3);
    print(g, E(150, 90, 17, 12), '#fbf7ee', s + 4); dot(g, 152, 80, 6, '#c8553d'); stroke(g, [[136, 92], [100, 102]], '#6b6b6b', 3.5, s + 5); dot(g, 146, 88, 3, INK); },
  tiger(g, s) { print(g, [[120, 330], [180, 286], [330, 290], [372, 326], [352, 366], [140, 370]], '#e08a3c', s); print(g, E(120, 304, 52, 46), '#e08a3c', s + 1);
    for (const x of [90, 150]) print(g, E(x, 262, 14, 13), '#e08a3c', s + x); print(g, E(96, 322, 22, 15), '#f6e6c8', s + 2); dot(g, 84, 316, 5, INK); dot(g, 112, 294, 4, INK);
    for (const x of [200, 235, 270, 305, 335]) stroke(g, [[x, 292], [x - 8, 322], [x + 2, 352]], INK, 5, s + x); for (const x of [130, 148]) stroke(g, [[x, 272], [x - 4, 292]], INK, 4, s + x + 1);
    stroke(g, [[365, 330], [395, 300], [385, 268]], '#e08a3c', 9, s + 3); },
};

// a stop card: landmark behind (faded, like a watercolour wash), the friend in front
export function stop(landmark, friend, seed = 1) {
  const c = canvas(400, 400), g = c.getContext('2d');
  if (landmark) { g.save(); FINE = !friend; LM[landmark](g, seed); FINE = false; g.restore(); }
  if (friend) { g.save(); if (landmark) { g.translate(70, 90); g.scale(0.72, 0.72); } FR[friend](g, seed + 50); g.restore(); }
  return c;
}
export const FRIENDS = Object.keys(FR), LANDMARKS = Object.keys(LM);
