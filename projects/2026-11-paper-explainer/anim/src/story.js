// "Once upon a time…" — the Bear & Joy method as a vintage paper pop-up book (vertical 1080x1920, 60 s, English on screen).
// The book stands open in a V: the upper half is a painted backdrop, the lower half a stage where paper cut-outs fold up.
// Each page turn lifts the next leaf: its back becomes the new backdrop and the leaf under it the new stage.
// Owner (24 Nov 2026): no complete book pages (cut the bear, Joy and scenes out, white paper edge, animate them);
// parents practise with the pronunciation guide, understand, then use the conversation starters out in the world
// (park, dinner, bedtime); it doesn't have to be perfect, just fun. Use English, don't teach it. Vintage, paper, fun.
import { THREE, keys, seg, ease, lerp, clamp, wobble, rng } from './kit.js';
import * as P from './paper.js';
import cover1 from './assets/art/b1-cover.jpg';
import wbCover from './assets/art/wb-cover.jpg';
import siteMark from './assets/art/site-mark.jpg';
import siteJoy from './assets/art/site-joy.jpg';
import bearJoy from './assets/art/bear.png';
import butterfly from './assets/art/butterfly.png';
import markAv from './assets/art/mark-avatar.png';
import joyAv from './assets/art/joy-avatar.png';
import wordmark from './assets/art/wordmark-navy.png';
import logoArt from './assets/art/bear-butterfly.png';
import cutCat from './assets/art/cut-cat.png';
import cutDoor from './assets/art/cut-door.png';
import cutFlowers from './assets/art/cut-flowers.png';
import cutFriend from './assets/art/cut-friend.png';
import cutLeap from './assets/art/cut-leap.png';
import cutOxford from './assets/art/cut-oxford.png';
import cutSit from './assets/art/cut-sit.png';
import cutWindow from './assets/art/cut-window.png';

export const ASSETS = { cover1, wbCover, siteMark, siteJoy, bearJoy, butterfly, markAv, joyAv, wordmark, logoArt,
  cutCat, cutDoor, cutFlowers, cutFriend, cutLeap, cutOxford, cutSit, cutWindow };

const W = 6.4, D = 6.4, HALF = Math.PI / 2;
const q12 = t => Math.floor(t * 12) / 12;   // paper puppets move "on twos" (12 fps) like stop-motion
const SERIF = 'Title, Georgia, serif';       // Fraunces: a vintage storybook serif
const HANDF = 'PatrickHand';

export function buildStory(stage, B, IMG) {
  stage.renderer.toneMapping = THREE.NoToneMapping;  // keep the paper colours true
  const cue = B.cues, TURN = B.turns, NS = B.spreads.length, NLEAF = NS + 1;
  const spreadStart = s => TURN[s][1], spreadEnd = s => (TURN[s + 1] ? TURN[s + 1][0] : B.duration);
  const tex = c => { const x = new THREE.CanvasTexture(c); x.colorSpace = THREE.SRGBColorSpace; x.anisotropy = 8; return x; };
  const paperMat = c => new THREE.MeshLambertMaterial({ map: tex(c) });
  const cutMat = c => new THREE.MeshLambertMaterial({ map: tex(c), alphaTest: 0.5, side: THREE.DoubleSide });

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#e4d3b4');
  scene.add(new THREE.HemisphereLight('#fff6e6', '#e0cdb0', 1.95));
  const sun = new THREE.DirectionalLight('#ffeed2', 1.5);
  sun.position.set(-5, 10, 9); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 10, bottom: -6, near: 1, far: 40 }); sun.shadow.radius = 4; sun.shadow.bias = -0.0008;
  scene.add(sun);

  // desk: an old linen-paper tabletop
  const desk = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), paperMat(P.paperTex(1024, 1024, '#e2cfae', 11, { fibres: 900, spots: 40 })));
  desk.rotation.x = -HALF; desk.position.y = -0.09; desk.receiveShadow = true; scene.add(desk);
  const board = new THREE.MeshLambertMaterial({ color: '#2a3a5a' });
  const lower = new THREE.Mesh(new THREE.BoxGeometry(W + 0.36, 0.08, D + 0.3), board); lower.position.set(0, -0.05, D / 2 + 0.08); lower.receiveShadow = true; scene.add(lower);
  const upper = new THREE.Mesh(new THREE.BoxGeometry(W + 0.36, D + 0.3, 0.08), board); upper.position.set(0, D / 2 + 0.06, -0.08); upper.receiveShadow = true; scene.add(upper);

  // ------------------------------------------------ pieces
  const stick = (img, h, pad = 12, seed = 3) => { // a paper cut-out standing on its base, solid white scissor edge
    const c = P.sticker(img instanceof HTMLCanvasElement ? img : P.imgCanvas(img, 900), pad, { seed });
    const w = h * c.width / c.height, geo = new THREE.PlaneGeometry(w, h); geo.translate(0, h / 2, 0);
    const m = new THREE.Mesh(geo, cutMat(c)); m.castShadow = true; m.receiveShadow = true; m.userData.w = w; return m;
  };
  const card = (img, h, o = {}) => { // a cover printed on a card with a white margin
    const iw = img.width, ih = img.height, m = o.margin ?? 0.06, c = P.canvas(Math.round(iw * (1 + 2 * m)), Math.round(ih + iw * 2 * m));
    const g = c.getContext('2d'); g.fillStyle = '#fffdf7'; g.fillRect(0, 0, c.width, c.height); g.drawImage(img, iw * m, iw * m, iw, ih);
    return stick(c, h, 4, o.seed || 9);
  };

  // pop-up: a group on a leaf that folds up from flat (hinge at its base) at 'at', and folds down before its page turns
  const pops = [];
  function pop(leaf, x, z, kids, at, o = {}) {
    const gp = new THREE.Group(); gp.position.set(x, 0.006 + (o.layer || 0) * 0.004, z);
    kids.forEach(k => gp.add(k)); leaf.surface.add(gp);
    pops.push({ gp, at, foldAt: o.foldAt ?? (TURN[leaf.idx] ? TURN[leaf.idx][0] : 1e9), leafIdx: leaf.idx, wiggle: o.wiggle ?? 0.03, seed: x * 7 + z });
    return gp;
  }
  const unfold = (p, t) => clamp(ease.spring(seg(q12(t), p.at, p.at + 0.55))) * (1 - ease.io(seg(t, p.foldAt - 0.42, p.foldAt - 0.05)));

  // ------------------------------------------------ leaves
  const leaves = [];
  for (let k = 0; k < NLEAF; k++) { const g = new THREE.Group(), surface = new THREE.Group(); g.add(surface); scene.add(g); leaves.push({ idx: k, g, surface }); }
  function face(leaf, canvasFront, canvasBack) {
    const geoF = new THREE.PlaneGeometry(W, D); geoF.rotateX(-HALF); geoF.translate(0, 0, D / 2);
    const f = new THREE.Mesh(geoF, paperMat(canvasFront)); f.receiveShadow = true; f.castShadow = true; leaf.g.add(f);
    if (canvasBack) { const geoB = new THREE.PlaneGeometry(W, D); geoB.rotateX(HALF); geoB.translate(0, -0.002, D / 2);
      const b = new THREE.Mesh(geoB, paperMat(canvasBack)); b.receiveShadow = true; leaf.g.add(b); }
  }
  function leafPose(k, t) { // leaf k lifts during TURN[k]: a little overshoot and settle, like real card stock
    const tr = TURN[k], p = tr ? seg(t, tr[0], tr[1]) : 0;
    const th = tr ? HALF * (ease.io(p) + Math.sin(Math.PI * clamp((t - tr[1]) / 0.35)) * 0.04 * (t > tr[1] ? 1 : 0)) : 0;
    const n = clamp(th / HALF), l = leaves[k];
    l.g.rotation.x = -th;
    l.g.position.set(0, lerp(0.035 * (NLEAF - k), 0, n), lerp(0, 0.03 * k + 0.02, n));
    l.g.visible = !(n >= 1 && TURN[k + 1] && t > TURN[k + 1][1] + 0.1 && k < NLEAF - 2);
  }

  // ------------------------------------------------ paper textures
  const S = 1024;
  const floorTex = (seed, draw, base) => { const c = P.paperTex(S, S, base || P.C.paper, seed, { spots: 22 }), g = c.getContext('2d');
    const r = rng(seed * 31 + 7); for (let i = 0; i < 22; i++) P.ink(g, P.ell(r() * S, r() * S, 5, 5, 6), seed + i, { w: 1.6, color: '#b49a7a', passes: 1 });
    draw && draw(g); return c; };
  const rug = (g, x, y, rx, ry, col, seed) => P.wash(g, P.ell(x, y, rx, ry, 18), col, seed, { alpha: 0.75, edge: 16 });
  const backdrop = (seed, wash, draw) => {
    const c = P.paperTex(S, S, P.C.paper, seed, { spots: 20 }), g = c.getContext('2d');
    if (wash) { const gr = g.createLinearGradient(0, 0, 0, S); wash.forEach(([p, col]) => gr.addColorStop(p, col)); g.globalAlpha = 0.85; g.fillStyle = gr; g.fillRect(0, 0, S, S); g.globalAlpha = 1;
      g.globalCompositeOperation = 'multiply'; g.drawImage(P.paperTex(S, S, '#ffffff', seed + 1, { vignette: false, fibres: 120, age: false }), 0, 0); g.globalCompositeOperation = 'source-over'; }
    draw && draw(g);
    const v = g.createRadialGradient(S / 2, S / 2, S * 0.35, S / 2, S / 2, S * 0.75); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(120,80,30,0.18)'); g.fillStyle = v; g.fillRect(0, 0, S, S);
    return c;
  };
  const paste = (g, img, x, y, h, rot = 0, pad = 14) => {
    const s = P.sticker(img instanceof HTMLCanvasElement ? img : P.imgCanvas(img, 900), pad), w = h * s.width / s.height;
    g.save(); g.translate(x, y); g.rotate(rot); g.shadowColor = 'rgba(60,40,20,0.28)'; g.shadowBlur = 18; g.shadowOffsetY = 8;
    g.drawImage(s, -w / 2, -h / 2, w, h); g.restore();
  };
  const cloud = (g, x, y, s, seed) => { const pts = [[-90, 20], [-70, -20], [-30, -40], [10, -50], [50, -30], [90, -10], [100, 20], [40, 34], [-40, 34]].map(([a, b]) => [x + a * s, y + b * s]);
    g.save(); g.shadowColor = 'rgba(60,40,20,0.18)'; g.shadowBlur = 10; g.shadowOffsetY = 5; g.fillStyle = '#fffdf7'; P.smooth(g, pts); g.fill(); g.restore(); P.ink(g, pts, seed, { w: 2.2, color: '#8b98ad' }); };
  const stars = (g, n, seed) => { const r = rng(seed); for (let i = 0; i < n; i++) { const x = r() * S, y = r() * S * 0.8; g.fillStyle = `rgba(246,240,186,${0.3 + r() * 0.6})`; g.beginPath(); g.arc(x, y, 2 + r() * 3, 0, 7); g.fill(); } };
  const bigWord = (g, num, en, col) => { // vintage chapter heading: small number over a big serif word, with a flourish
    P.hand(g, `Step ${num}`, S / 2, 330, { font: SERIF, weight: 500, size: 70, color: '#8a6a4a' });
    P.hand(g, en, S / 2, 470, { font: SERIF, weight: 700, size: 190, color: col });
    P.ink(g, [[300, 570], [420, 555], [512, 575], [604, 555], [724, 570]], num * 3, { closed: false, w: 3.4, color: '#c9a84c' });
  };
  const hills = (g, cols) => cols.forEach(([y, col, seed]) => { const pts = [[-40, S + 40], [-40, y + 60], [200, y], [460, y + 50], [720, y - 20], [1060, y + 40], [1060, S + 40]];
    P.wash(g, pts, col, seed, { alpha: 0.85 }); P.ink(g, pts.slice(1, -1), seed, { closed: false, w: 2.4, color: '#6f8f55' }); });

  const coverC = backdrop(2, [[0, '#1E2D4D'], [1, '#2c4a78']], g => {
    stars(g, 60, 3);
    P.hand(g, 'Once upon a time…', S / 2, 300, { font: SERIF, weight: 600, size: 100, color: '#F6F0BA' });
    P.ink(g, [[300, 380], [420, 365], [512, 385], [604, 365], [724, 380]], 5, { closed: false, w: 3.4, color: '#c9a84c' });
    paste(g, IMG.logoArt, S / 2, 680, 330, -0.04, 10);
  });
  const BD = {
    home: backdrop(4, [[0, '#cfe3f3'], [0.7, '#f3eedf'], [1, '#f7efe0']], g => { cloud(g, 200, 150, 1.0, 1); cloud(g, 790, 220, 0.8, 2); paste(g, IMG.cutOxford, 560, 560, 760, 0.02); }),
    what: backdrop(6, [[0, '#fbf3c9'], [1, '#f6ecd6']], g => {
      g.drawImage(IMG.wordmark, S / 2 - 330, 300, 660, 660 * IMG.wordmark.height / IMG.wordmark.width);
      paste(g, IMG.cutWindow, 200, 640, 420, -0.05); paste(g, IMG.cutCat, 800, 660, 400, 0.05); }),
    read: backdrop(8, [[0, '#dcebf7'], [1, '#f4efe3']], g => { bigWord(g, 1, 'Read', '#3d6fa8'); cloud(g, 160, 700, 0.7, 4); cloud(g, 860, 760, 0.6, 5); }),
    practise: backdrop(10, [[0, '#f8e3dc'], [1, '#f6efe4']], g => { bigWord(g, 2, 'Practise', '#c0605e'); }),
    starters: backdrop(12, [[0, '#e3f0d9'], [1, '#f5efe2']], g => { bigWord(g, 3, 'Talk', '#4f8a4a'); }),
    park: backdrop(14, [[0, '#cfe3f3'], [0.55, '#eef3e3'], [1, '#e3edc9']], g => {
      g.fillStyle = 'rgba(246,224,120,0.9)'; g.beginPath(); g.arc(820, 400, 70, 0, 7); g.fill(); P.ink(g, P.ell(820, 400, 70, 70, 14), 2, { w: 2.4, color: '#c9a84c' });
      cloud(g, 230, 420, 0.9, 6); hills(g, [[640, '#b9d99a', 3], [760, '#9fca82', 4]]); }),
    dinner: backdrop(16, [[0, '#f7e7c4'], [1, '#f3e2c8']], g => {
      for (let x = 0; x < S; x += 64) { g.fillStyle = 'rgba(233,163,163,0.18)'; g.fillRect(x, 0, 28, S); }        // old striped wallpaper
      g.fillStyle = '#cfe3f3'; g.fillRect(330, 380, 370, 320); g.strokeStyle = '#2b2d3a'; g.lineWidth = 6; g.strokeRect(330, 380, 370, 320);
      P.ink(g, [[515, 380], [515, 700]], 8, { closed: false, w: 3 }); P.ink(g, [[330, 540], [700, 540]], 9, { closed: false, w: 3 });
      g.fillStyle = 'rgba(246,224,120,0.9)'; g.beginPath(); g.arc(610, 460, 34, 0, 7); g.fill();
      P.ink(g, [[200, 300], [200, 380]], 10, { closed: false, w: 2.6 }); const lamp = [[150, 380], [250, 380], [230, 430], [170, 430]]; P.wash(g, lamp, '#F6F0BA', 11); P.ink(g, lamp, 11); }),
    bedtime: backdrop(18, [[0, '#1E2D4D'], [1, '#34507e']], g => {
      stars(g, 80, 19); g.fillStyle = '#F6F0BA'; g.beginPath(); g.arc(780, 380, 80, 0, 7); g.fill(); g.fillStyle = '#25395f'; g.beginPath(); g.arc(810, 360, 72, 0, 7); g.fill();
      paste(g, IMG.cutWindow, 260, 520, 360, -0.04); }),
    fun: backdrop(20, [[0, '#fbf3c9'], [1, '#f4ecd9']], g => {
      const r = rng(21); for (let i = 0; i < 70; i++) { g.fillStyle = ['#e9a3a3', '#AECCE6', '#F6E07E', '#9fca82'][i % 4]; g.save(); g.translate(r() * S, 300 + r() * 700); g.rotate(r() * 3); g.fillRect(-9, -5, 18, 10); g.restore(); }
      P.hand(g, 'Not perfect.', S / 2, 360, { font: SERIF, weight: 600, size: 110, color: '#8a6a4a' });
      P.hand(g, 'Just fun!', S / 2, 500, { font: SERIF, weight: 800, size: 150, color: '#c0605e' }); }),
    cta: backdrop(22, [[0, '#1E2D4D'], [1, '#2c4a78']], g => { stars(g, 70, 23); }),
  };
  const FL = {
    home: floorTex(31, g => rug(g, 480, 600, 380, 170, '#e9cfa4', 1)),
    what: floorTex(33, g => rug(g, 512, 860, 470, 120, '#d7e6c6', 2)),
    read: floorTex(35, g => rug(g, 640, 640, 300, 150, '#cfe0ee', 3)),
    practise: floorTex(37, g => rug(g, 360, 640, 300, 150, '#f0d6d6', 4)),
    starters: floorTex(39, g => { rug(g, 512, 640, 440, 160, '#dce9cf', 5); }),
    park: floorTex(41, g => { g.fillStyle = 'rgba(159,202,130,0.55)'; g.fillRect(0, 0, S, S); P.picnic(g, 470, 640, 360, 170, 6); }, '#eef3e0'),
    dinner: floorTex(43, g => rug(g, 512, 600, 440, 170, '#e9cfa4', 7), '#f1e4cc'),
    bedtime: floorTex(45, g => rug(g, 512, 640, 460, 170, '#c7d3ea', 8), '#e9e6ef'),
    fun: floorTex(47, g => rug(g, 400, 640, 360, 160, '#f3d9a6', 9)),
    cta: floorTex(49, g => rug(g, 512, 700, 400, 150, '#2c4a78', 10)),
  };
  face(leaves[0], coverC, BD[B.spreads[0]]);
  for (let k = 1; k < NLEAF; k++) face(leaves[k], FL[B.spreads[k - 1]], k < NS ? BD[B.spreads[k]] : null);
  const stg = name => leaves[B.spreads.indexOf(name) + 1];      // spread s lives on leaves[s + 1]

  // ------------------------------------------------ people
  const people = [];
  function person(kind, scale, seed) {
    const p = P.PEOPLE[kind], book = p.adult ? p : { ...p, book: null };
    const heads = ['idle', 'talk', 'blink'].map(st => cutMat(P.sticker(P.drawHead(p, st, seed), 10, { seed })));
    const bodyS = P.sticker(P.drawBody(book, seed), 10, { seed: seed + 1 });
    const wB = 1.65 * scale, hB = wB * bodyS.height / bodyS.width;
    const geoB = new THREE.PlaneGeometry(wB, hB); geoB.translate(0, hB / 2, 0);
    const bm = new THREE.Mesh(geoB, cutMat(bodyS)); bm.castShadow = true;
    const hs = p.adult ? 1 : 1.16, wH = wB * 300 / bodyS.width * hs, hH = wH * 320 / 300;
    const geoH = new THREE.PlaneGeometry(wH, hH); geoH.translate(0, hH * (260 / 320 - 0.5), 0);
    const hm = new THREE.Mesh(geoH, heads[0]); hm.castShadow = true;
    const neck = new THREE.Group(); neck.position.set(0, hB * (1 - 88 / bodyS.height), 0.012); neck.add(hm);
    const g = new THREE.Group(); g.add(bm, neck);
    const pr = { g, neck, hm, heads, seed, talks: [], laugh: [], topY: hB * (1 - 88 / bodyS.height) + hH * (260 / 320) };
    people.push(pr); return pr;
  }
  function personUpdate(pr, t) {
    const tq = q12(t), talking = pr.talks.some(([a, b]) => t >= a && t < b), laughing = pr.laugh.some(([a, b]) => t >= a && t < b);
    const blink = ((tq + pr.seed * 0.37) % 3.3) < 0.12;
    pr.hm.material = pr.heads[talking || laughing ? (Math.floor(tq * 6) % 2 ? 1 : 0) : blink ? 2 : 0];
    pr.neck.rotation.z = wobble(tq * 0.8, pr.seed) * 0.07 + (talking ? Math.sin(tq * 9) * 0.05 : 0) + (laughing ? Math.sin(tq * 14) * 0.12 : 0);
    pr.g.position.y = talking || laughing ? Math.abs(Math.sin(tq * (laughing ? 14 : 9))) * (laughing ? 0.06 : 0.02) : 0;
  }
  function pair(adult, child, sc, seed, gap = 1) {
    const a = person(adult, sc, seed), c = person(child, sc * 0.7, seed + 5);
    a.g.position.set(-0.52 * sc * gap, 0, 0); c.g.position.set(0.66 * sc * gap, 0, 0.02);
    return { a, c, kids: [a.g, c.g] };
  }
  const bubbles = [];
  function bub(parent, en, s, e, x, y, o = {}) { // speech bubble (English only), pops in with a spring
    const c = P.sticker(P.bubble(en, '', { tail: o.tail, w: o.w || Math.max(360, en.length * 34), size: 86 }), 6), h = o.h || 0.84, w = h * c.width / c.height;
    const geo = new THREE.PlaneGeometry(w, h); geo.translate(o.tail === 'right' ? -w * 0.22 : w * 0.22, h / 2, 0);
    const m = new THREE.Mesh(geo, cutMat(c)); m.position.set(x, y, 0.08); m.castShadow = true; parent.add(m);
    bubbles.push({ m, s, e }); return m;
  }
  const talkOf = name => B.talks.filter(r => r[0] === name);
  function talkPair(pr, name, gp) {
    for (const r of talkOf(name)) {
      const who = r[1] === 'adult' ? pr.a : pr.c; who.talks.push([r[2], r[3]]);
      bub(gp, r[4], r[2], r[3], who.g.position.x + (r[1] === 'adult' ? -0.15 : 0.15), who.topY + 0.06, { tail: r[1] === 'adult' ? 'left' : 'right' });
    }
  }
  // paper confetti bursts (fun moments)
  const bursts = [];
  function confetti(parent, at, x, y, n = 26, seed = 1) {
    const r = rng(seed), cols = ['#e9a3a3', '#AECCE6', '#F6E07E', '#9fca82', '#c9a84c'], ms = [];
    for (let i = 0; i < n; i++) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(0.11, 0.07), new THREE.MeshLambertMaterial({ color: cols[i % 5], side: THREE.DoubleSide }));
      m.userData = { vx: (r() - 0.5) * 3.2, vy: 2.2 + r() * 2.2, spin: (r() - 0.5) * 14 }; m.visible = false; parent.add(m); ms.push(m);
    }
    bursts.push({ ms, at, x, y });
  }

  // ------------------------------------------------ home — you and your child, a worry, the bear arrives
  const home = pair('mum', 'girl', 1.0, 1);
  pop(stg('home'), -0.3, 3.6, home.kids, spreadStart(0) + 0.15);
  const worryC = P.canvas(700, 420), wg = worryC.getContext('2d');
  { const pts = [[80, 210], [70, 120], [170, 60], [300, 40], [430, 50], [560, 70], [640, 150], [630, 260], [540, 330], [380, 350], [220, 340], [110, 300]];
    wg.fillStyle = '#fffdf7'; P.smooth(wg, pts); wg.fill(); P.ink(wg, pts, 4, { w: 3 });
    for (const [x, y, r] of [[140, 390, 22], [90, 410, 12]]) { wg.fillStyle = '#fffdf7'; wg.beginPath(); wg.arc(x, y - 30, r, 0, 7); wg.fill(); P.ink(wg, P.ell(x, y - 30, r, r, 8), 5, { w: 2.4 }); }
    P.hand(wg, 'My accent…?', 360, 150, { font: HANDF, weight: 400, size: 92, color: P.C.deep });
    for (let i = 0; i < 3; i++) P.ink(wg, [[230 + i * 40, 250], [260 + i * 40, 225], [290 + i * 40, 262], [320 + i * 40, 230]], 20 + i, { closed: false, w: 3, color: '#c0605e', passes: 1 }); }
  const worry = new THREE.Mesh((() => { const gg = new THREE.PlaneGeometry(2.2, 1.32); gg.translate(0.4, 0.66, 0); return gg; })(), cutMat(P.sticker(worryC, 8)));
  worry.position.set(-0.9, 2.3, 0.1); home.a.g.add(worry); bubbles.push({ m: worry, s: cue['worry'], e: cue['bear-in'] + 0.3 });
  const leap = stick(IMG.cutLeap, 1.55, 10, 21);
  pop(stg('home'), 2.1, 4.4, [leap], cue['bear-in'] - 0.05, { layer: 2 });
  const bfly = stick(IMG.butterfly, 0.55, 8, 22); scene.add(bfly);

  // ------------------------------------------------ what Bear & Joy is — cut-outs from our books
  pop(stg('what'), -1.55, 2.3, [stick(IMG.cutDoor, 2.5, 14, 31)], cue['door']);
  pop(stg('what'), 1.5, 3.1, [stick(IMG.cutFriend, 2.0, 12, 32)], cue['friend']);
  pop(stg('what'), 0, 5.4, [stick(IMG.cutFlowers, 1.15, 10, 33)], cue['flowers'], { layer: 2 });

  // ------------------------------------------------ 1 · read the storybook together
  pop(stg('read'), -1.5, 2.1, [card(IMG.cover1, 2.3, { margin: 0.03, seed: 41 })], cue['read-book']);
  const readPair = pair('mum', 'girl', 0.95, 1);
  const readGp = pop(stg('read'), 1.1, 3.9, readPair.kids, cue['read-pair'], { layer: 1 });
  talkPair(readPair, 'read', readGp);
  pop(stg('read'), -1.9, 5.2, [stick(IMG.cutSit, 0.9, 10, 43)], cue['read-bear'], { layer: 2 });

  // ------------------------------------------------ 2 · practise with the pronunciation guide (mum practises, then: aha!)
  const prPair = pair('mum', 'girl', 0.95, 1);
  const prGp = pop(stg('practise'), -1.3, 4.0, prPair.kids, cue['practise-pair'], { layer: 1 });
  talkPair(prPair, 'practise', prGp);
  const pronC = P.canvas(880, 560); let pronState = -1;
  const pronMat = cutMat(pronC), pronTex = pronMat.map;
  function drawPron(k) { // the guide's idea, set by hand: the English line, its Korean sound under it, a pencil circle drawing round the sound
    const g = pronC.getContext('2d'); g.clearRect(0, 0, 880, 560);
    g.drawImage(P.sticker(P.paperTex(840, 520, '#fbf3e6', 52, { fibres: 80, ring: false }), 18), 2, 2, 876, 556);
    P.hand(g, 'Walkbook · Pronunciation Guide', 440, 80, { font: HANDF, weight: 400, size: 48, color: '#9a8a70' });
    P.hand(g, 'One morning,', 440, 210, { font: SERIF, weight: 500, size: 92, color: '#2c4a78' });
    P.hand(g, '원 모닝,', 440, 360, { size: 120, color: '#8a4b3a' });
    if (k > 0) { g.save(); g.strokeStyle = '#d65a4a'; g.lineWidth = 7; g.lineCap = 'round'; g.beginPath();
      for (let i = 0; i <= 40 * k; i++) { const a = -2.6 + i / 40 * Math.PI * 2.15; g.lineTo(440 + Math.cos(a) * (200 + Math.sin(i) * 4), 360 + Math.sin(a) * (80 + Math.cos(i * 1.3) * 3)); } g.stroke(); g.restore(); }
    pronTex.needsUpdate = true;
  }
  drawPron(0);
  const pronH = 1.55, pronGeo = new THREE.PlaneGeometry(pronH * 880 / 560, pronH); pronGeo.translate(0, pronH / 2, 0);
  const pronCard = new THREE.Mesh(pronGeo, pronMat); pronCard.castShadow = true; pronCard.position.y = 0.25;
  pop(stg('practise'), 1.4, 2.2, [pronCard], cue['practise-card']);
  pop(stg('practise'), 2.0, 4.6, [card(IMG.wbCover, 1.3, { margin: 0.03, seed: 51 })], cue['practise-card'] + 0.3, { layer: 2 });
  const aha = stick(P.drawAha(5), 1.45, 8, 53); aha.position.set(-0.15, prPair.a.topY + 0.15, 0.1); prGp.add(aha);
  bubbles.push({ m: aha, s: cue['aha'], e: spreadEnd(3) - 0.3 });
  confetti(prGp, cue['aha'] + 0.1, -0.6, prPair.a.topY + 0.4, 26, 3);

  // ------------------------------------------------ 3 · conversation starters take the story outside
  B.starters.forEach((q, i) => {
    const c = stick(P.starterCard(q, 60 + i, ['#AECCE6', '#F6E07E', '#e9a3a3'][i]), 1.75, 6, 60 + i);
    c.rotation.z = (i - 1) * -0.1; c.position.y = i === 1 ? 1.35 : 0.15;
    pop(stg('starters'), (i - 1) * 1.75, i === 1 ? 1.8 : 3.4, [c], cue['starters'] + i * 0.4, { layer: i });
  });
  const stBear = stick(IMG.cutLeap, 1.2, 10, 64); pop(stg('starters'), 2.2, 5.0, [stBear], cue['starters'] + 1.6, { layer: 3 });

  // ------------------------------------------------ out in the world: park, dinner, bedtime
  const parkPair = pair('dad', 'boy', 0.9, 12);
  const parkGp = pop(stg('park'), -0.4, 3.7, parkPair.kids, cue['park'], { layer: 1 });
  talkPair(parkPair, 'park', parkGp);
  pop(stg('park'), -2.1, 1.7, [stick(P.drawTree(7), 2.6, 8, 71)], cue['park-tree']);
  const friends = pair('boy2', 'girl2', 0.62, 14, 0.9); friends.c.g.scale.setScalar(1.35);
  pop(stg('park'), 1.9, 2.3, friends.kids, cue['park-friends']);
  pop(stg('park'), 2.3, 4.9, [stick(IMG.cutFlowers, 0.7, 8, 72)], cue['park-friends'] + 0.2, { layer: 2 });

  const dinPair = pair('grandma', 'girl2', 0.9, 13);
  const dinGp = pop(stg('dinner'), 0, 3.4, dinPair.kids, cue['dinner'], { layer: 1 });
  talkPair(dinPair, 'dinner', dinGp);
  const table = stick(P.drawTable(9), 1.0, 8, 81); table.position.set(0.1, -0.02, 0.45); dinGp.add(table);

  const bedPair = pair('mum', 'girl', 0.92, 1);
  const headb = stick(P.drawHeadboard(11), 1.75, 8, 91); headb.position.set(0.1, 0, -0.35);
  const blanket = stick(P.drawBlanket(12), 0.62, 8, 92); blanket.position.set(0.1, 0, 0.3);
  const bedGp = pop(stg('bedtime'), 0, 3.6, [headb, ...bedPair.kids, blanket], cue['bed'], { layer: 1 });
  talkPair(bedPair, 'bedtime', bedGp);

  // ------------------------------------------------ not perfect, just fun — and Little Steps + our team
  const funPair = pair('mum', 'girl', 0.95, 1);
  const funGp = pop(stg('fun'), -1.2, 3.9, funPair.kids, cue['fun-pair'], { layer: 1 });
  talkPair(funPair, 'fun', funGp);
  funPair.a.laugh.push([47.6, 50.1]); funPair.c.laugh.push([47.4, 50.1]);
  confetti(funGp, 47.9, 0.2, 2.2, 34, 7);
  const tabC = P.canvas(1000, 760), tabTex = tex(tabC); let tabState = -1;
  function drawTab(i) {
    const g = tabC.getContext('2d'); g.clearRect(0, 0, 1000, 760);
    g.fillStyle = '#2a3a5a'; g.beginPath(); g.roundRect(24, 30, 952, 630, 46); g.fill(); P.ink(g, [[30, 40], [970, 40], [970, 650], [30, 650]], 71, { w: 3 });
    const im = [IMG.siteMark, IMG.siteJoy][i], sw = 880, sh = 520;
    g.save(); g.beginPath(); g.roundRect(60, 70, sw, sh, 14); g.clip(); const k = Math.max(sw / im.width, sh / im.height);
    g.drawImage(im, 60 + (sw - im.width * k) / 2, 70 + (sh - im.height * k) / 2, im.width * k, im.height * k); g.restore();
    g.fillStyle = 'rgba(255,253,247,0.94)'; g.beginPath(); g.roundRect(300, 615, 400, 90, 40); g.fill();
    P.hand(g, 'Little Steps · 7 days', 500, 660, { font: HANDF, weight: 400, size: 56, color: P.C.deep });
    tabTex.needsUpdate = true;
  }
  drawTab(0);
  const tabH = 1.85, tabGeo = new THREE.PlaneGeometry(tabH * 1000 / 760, tabH); tabGeo.translate(0, tabH / 2, 0);
  const tablet = new THREE.Mesh(tabGeo, new THREE.MeshLambertMaterial({ map: tabTex, alphaTest: 0.5, side: THREE.DoubleSide })); tablet.castShadow = true;
  pop(stg('fun'), 1.2, 2.0, [tablet], cue['fun-tablet']);
  const avatar = (img, name, seed) => { const c = P.canvas(420, 620), g = c.getContext('2d');
    P.ink(g, [[210, 380], [210, 610]], seed, { closed: false, w: 8, color: '#8a6a4a' }); g.drawImage(img, 20, 0, 380, 380);
    P.hand(g, name, 210, 450, { font: HANDF, weight: 400, size: 70, color: P.C.deep }); return stick(c, 1.5, 10, seed); };
  pop(stg('fun'), 0.6, 4.6, [avatar(IMG.markAv, 'Mark T', 73)], cue['mark'], { layer: 2 });
  const joyGp = pop(stg('fun'), 1.8, 4.5, [avatar(IMG.joyAv, 'Joy T', 74)], cue['joy'], { layer: 2 });
  bub(joyGp, "We're here to help!", cue['joy'] + 0.4, spreadEnd(8) - 0.3, 0.2, 1.5, { tail: 'right', h: 0.7 });

  // ------------------------------------------------ Book 1 and the comment call
  pop(stg('cta'), -0.55, 1.9, [card(IMG.cover1, 3.0, { margin: 0.03, seed: 81 })], cue['cta-book']);
  pop(stg('cta'), -2.0, 3.9, [stick(IMG.bearJoy, 1.75, 12, 82)], cue['cta-bear'], { layer: 1 });
  const comC = P.canvas(900, 300), cg = comC.getContext('2d');
  { cg.fillStyle = '#fffdf7'; cg.beginPath(); cg.roundRect(10, 10, 880, 280, 40); cg.fill(); P.ink(cg, [[20, 20], [880, 20], [880, 280], [20, 280]], 3, { w: 3 });
    cg.fillStyle = '#AECCE6'; cg.beginPath(); cg.arc(110, 150, 60, 0, 7); cg.fill(); P.ink(cg, P.ell(110, 150, 60, 60, 12), 4, { w: 2.6 });
    P.hand(cg, 'Bear', 300, 150, { font: HANDF, weight: 400, size: 130, color: P.C.deep, align: 'left' });
    P.hand(cg, '♥', 800, 150, { font: HANDF, weight: 400, size: 90, color: '#d65a4a' }); }
  const comment = new THREE.Mesh((() => { const gg = new THREE.PlaneGeometry(2.7, 0.9); gg.translate(0, 0.45, 0); return gg; })(), cutMat(P.sticker(comC, 8)));
  comment.position.y = 1.15;  // lifted clear of Instagram's buttons at the bottom of the frame
  const ctaGp = pop(stg('cta'), 1.05, 4.3, [comment], cue['cta-comment'], { layer: 2 });
  confetti(ctaGp, cue['cta-comment'] + 0.15, 0, 1.2, 34, 9);

  // ------------------------------------------------ the world over time
  function world(t) {
    for (let k = 0; k < NLEAF; k++) leafPose(k, t);
    for (const p of pops) { const u = unfold(p, t); p.gp.rotation.x = -HALF * (1 - u); p.gp.rotation.z = u > 0.98 ? wobble(q12(t) * 0.7, p.seed) * p.wiggle : 0;
      p.gp.visible = t >= TURN[p.leafIdx - 1][0] && (u > 0.001 || t < p.at); }
    for (const pr of people) personUpdate(pr, t);
    for (const b of bubbles) { const tq = q12(t), a = clamp(ease.spring(seg(tq, b.s, b.s + 0.4))), z = 1 - seg(t, b.e - 0.18, b.e), k = a * z;
      b.m.scale.setScalar(Math.max(0.001, k)); b.m.visible = k > 0.01; b.m.rotation.z = Math.sin(tq * 3 + b.s) * 0.025; }
    for (const bu of bursts) { const d = q12(t) - bu.at; bu.ms.forEach(m => { const on = d > 0 && d < 1.6; m.visible = on; if (!on) return; const u = m.userData;
      m.position.set(bu.x + u.vx * d, bu.y + u.vy * d - 4.2 * d * d, 0.15); m.rotation.set(u.spin * d, u.spin * 0.6 * d, u.spin * 0.3 * d); }); }
    { const tq = q12(t), a = cue['bear-in'], p = seg(tq, a, a + 1.1);
      leap.position.set(lerp(2.2, 0, ease.out(p)), Math.abs(Math.sin(p * Math.PI * 3)) * 0.7 * (1 - p), 0); leap.rotation.z = (1 - p) * Math.sin(p * 19) * 0.2; }
    { const tq = q12(t), a = cue['starters'] + 1.6, p = seg(tq, a, a + 0.9); stBear.position.set(lerp(1.2, 0, ease.out(p)), Math.abs(Math.sin(p * Math.PI * 2)) * 0.5 * (1 - p), 0); }
    { const tq = q12(t), flap = 0.55 + 0.45 * Math.abs(Math.sin(tq * 14)); let pos = null;
      if (t > cue['bear-in'] + 0.4 && t < spreadEnd(1) - 0.3) pos = [1.6 + Math.sin(t * 1.3) * 1.6, 3.0 + Math.sin(t * 2.1) * 0.5, 3.2 + Math.cos(t * 1.1) * 0.8];
      if (t > cue['park'] + 0.3 && t < spreadEnd(5) - 0.2) pos = [0.6 + Math.sin(t * 1.6) * 1.2, 2.6 + Math.sin(t * 2.4) * 0.4, 3.0 + Math.cos(t * 1.3) * 0.5];
      if (t > cue['cta-bear'] + 0.3) { const p = ease.io(seg(t, cue['cta-bear'] + 0.3, cue['cta-bear'] + 2.2)); pos = [lerp(-2.2, 0.2, p), lerp(2.6, 3.4, p) + Math.sin(p * Math.PI) * 0.6, lerp(4.0, 2.05, p)]; }
      bfly.visible = !!pos; if (pos) { bfly.position.set(...pos); bfly.scale.set(flap, 1, 1); bfly.rotation.z = Math.sin(tq * 5) * 0.15; } }
    { const k = Math.round(seg(t, cue['practise-circle'], cue['practise-circle'] + 0.9) * 12) / 12; if (k !== pronState) { pronState = k; drawPron(k); } }
    { const i = t < cue['fun-joy-screen'] ? 0 : 1; if (i !== tabState) { tabState = i; drawTab(i); } }
  }

  // ------------------------------------------------ camera (a little bump on every page turn, old-projector weave on twos)
  const BASE = { pos: [0, 6.6, 18.6], look: [0, 2.55, 2.1] };
  const CLOSE = { pos: [0, 5.6, 15.8], look: [0, 2.2, 2.6] };   // the real-world scenes come a little closer
  function cam(t) {
    const top = { pos: [0, 18.5, 4.5], look: [0, 0, 3.4] };
    let pos = keys(t, [[0, top.pos], [1.1, top.pos], [3.3, BASE.pos, 'io']]);
    let look = keys(t, [[0, top.look], [1.1, top.look], [3.3, BASE.look, 'io']]);
    const near = clamp(seg(t, 33.2, 34.2) - seg(t, 46.2, 47.2));
    pos = pos.map((v, j) => lerp(v, CLOSE.pos[j], ease.io(near))); look = look.map((v, j) => lerp(v, CLOSE.look[j], ease.io(near)));
    let bump = 0; for (const [, b] of TURN.slice(1)) bump += Math.sin(Math.PI * clamp((t - b) / 0.3)) * (t > b ? 1 : 0) * 0.12;
    const tq = q12(t), h = 0.035;
    pos = [pos[0] + wobble(tq * 2.2, 1) * h, pos[1] + wobble(tq * 2.0, 2) * h - bump, pos[2]];
    return { pos, look, fov: 40 };
  }

  // ------------------------------------------------ words on screen: a torn paper label held by washi tape (safe zone y 300-1450)
  const label = P.canvas(980, 300);
  { const g = label.getContext('2d'), r = rng(92); g.beginPath(); g.moveTo(0, 6);
    for (let x = 0; x <= 980; x += 14) g.lineTo(x, 4 + r() * 8); for (let x = 980; x >= 0; x -= 14) g.lineTo(x, 288 + r() * 8);
    g.closePath(); g.save(); g.clip(); g.drawImage(P.paperTex(980, 300, '#fbf2df', 91, { fibres: 60, ring: false }), 0, 0); g.restore(); }
  const tape = (g, x, y, rot, col) => { g.save(); g.translate(x, y); g.rotate(rot); g.globalAlpha = 0.72; g.fillStyle = col; g.fillRect(-70, -20, 140, 40);
    g.globalAlpha = 0.25; g.fillStyle = '#fff'; for (let i = -60; i < 70; i += 20) g.fillRect(i, -20, 8, 40); g.restore(); };
  function line(g, t, [a, b, en], i) {
    const k = seg(q12(t), a, a + 0.3) * (1 - seg(t, b - 0.2, b)); if (k <= 0) return;
    g.save(); g.globalAlpha = ease.out(k); g.translate(540, 410 + (1 - ease.out(k)) * 18); g.rotate(i % 2 ? 0.01 : -0.012);
    g.shadowColor = 'rgba(60,40,20,0.28)'; g.shadowBlur = 14; g.shadowOffsetY = 6; g.drawImage(label, -490, -115, 980, 230); g.shadowColor = 'transparent';
    tape(g, -440, -105, -0.5, ['#e9a3a3', '#AECCE6', '#F6E07E'][i % 3]); tape(g, 440, -105, 0.45, ['#AECCE6', '#F6E07E', '#e9a3a3'][i % 3]);
    g.font = `600 62px ${SERIF}`; let l1 = '', l2 = '';
    for (const w of en.split(' ')) { const tryL = (l1 + ' ' + w).trim(); if (!l2 && g.measureText(tryL).width < 860) l1 = tryL; else l2 = (l2 + ' ' + w).trim(); }
    const sz = l2 ? 56 : 66;
    P.hand(g, l1, 0, l2 ? -34 : 2, { font: SERIF, weight: 600, size: sz, color: '#2a3550' });
    if (l2) P.hand(g, l2, 0, 40, { font: SERIF, weight: 600, size: sz, color: '#2a3550' });
    g.restore();
  }
  function ctaCard(g, t) {
    const a = cue['cta-comment'] - 0.1, k = clamp(ease.spring(seg(q12(t), a, a + 0.6))); if (k <= 0) return;
    g.save(); g.translate(540, 430); g.scale(k, k); g.rotate(-0.012);
    g.shadowColor = 'rgba(20,20,40,0.35)'; g.shadowBlur = 22; g.shadowOffsetY = 8; g.drawImage(label, -490, -150, 980, 300); g.shadowColor = 'transparent';
    tape(g, -430, -140, -0.45, '#F6E07E'); tape(g, 430, -140, 0.4, '#AECCE6');
    P.hand(g, 'Comment “Bear”', 0, -48, { font: SERIF, weight: 700, size: 92, color: '#c0605e' });
    P.hand(g, 'to be the first to own Book 1!', 0, 52, { font: SERIF, weight: 600, size: 58, color: '#2a3550' });
    g.restore();
  }
  // vintage finish: warm sepia wash, a soft vignette for a tall frame, dust and hairline scratches on twos, a slow light leak
  function vintage(g, t) {
    const Wd = 1080, Hd = 1920, r = rng(Math.floor(t * 12) * 7 + 3);
    g.save(); g.globalCompositeOperation = 'soft-light'; g.fillStyle = 'rgba(180,130,70,0.35)'; g.fillRect(0, 0, Wd, Hd); g.restore();
    const v = g.createRadialGradient(Wd / 2, Hd * 0.45, Hd * 0.32, Wd / 2, Hd * 0.45, Hd * 0.78); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(60,35,10,0.42)');
    g.fillStyle = v; g.fillRect(0, 0, Wd, Hd);
    const leak = 0.5 + 0.5 * Math.sin(t * 0.7), lg = g.createRadialGradient(Wd * 1.05, Hd * 0.15, 0, Wd * 1.05, Hd * 0.15, Hd * 0.45);
    lg.addColorStop(0, `rgba(255,170,90,${0.16 * leak})`); lg.addColorStop(1, 'rgba(255,170,90,0)'); g.fillStyle = lg; g.fillRect(0, 0, Wd, Hd);
    g.fillStyle = 'rgba(40,25,10,0.5)'; for (let i = 0; i < 10; i++) { g.beginPath(); g.arc(r() * Wd, r() * Hd, 0.8 + r() * 2.2, 0, 7); g.fill(); }
    if (r() < 0.5) { const x = r() * Wd; g.strokeStyle = 'rgba(255,245,220,0.25)'; g.lineWidth = 1.2; g.beginPath(); g.moveTo(x, 0); g.lineTo(x + (r() - 0.5) * 30, Hd); g.stroke(); }
  }
  function overlay(g, t) {
    vintage(g, t);
    B.lines.forEach((l, i) => line(g, t, l, i));
    ctaCard(g, t);
  }

  const sets = { book: { scene, update: t => world(t), grade: 'sepia(0.18) saturate(0.95) contrast(1.04)' } };
  const shots = [{ set: 'book', dur: B.duration, cam: (l) => cam(l) }];
  return { sets, shots, overlay, design: [], designTitle: B.title, finish: { grain: 0.08, vignette: 0, fadeIn: 0.4, fadeOut: 0.6 } };
}
