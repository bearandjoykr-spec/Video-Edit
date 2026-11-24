// "Once upon a time…" — a Bear & Joy explainer as a paper pop-up book (vertical 1080x1920, 60 s).
// The book stands open in a V: the upper half is a painted backdrop, the lower half a stage where paper cut-outs fold up.
// Each page turn lifts the next leaf: its back becomes the new backdrop and the leaf under it becomes the new stage.
// Owner (24 Nov 2026): no complete book pages; the bear, the butterfly and small scenes are cut out of our books with a
// white paper edge and animated on the page. Families (mum, dad, grandma, friends) talk in English with their children.
import { THREE, keys, seg, ease, lerp, clamp, wobble } from './kit.js';
import * as P from './paper.js';
import cover1 from './assets/art/b1-cover.jpg';
import wbCover from './assets/art/wb-cover.jpg';
import siteMark from './assets/art/site-mark.jpg';
import siteJoy from './assets/art/site-joy.jpg';
import siteSheet from './assets/art/site-sheet.jpg';
import siteDoors from './assets/art/site-doors.jpg';
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
import cutGarden from './assets/art/cut-garden.png';
import cutLeap from './assets/art/cut-leap.png';
import cutOxford from './assets/art/cut-oxford.png';
import cutSit from './assets/art/cut-sit.png';
import cutWindow from './assets/art/cut-window.png';

export const ASSETS = { cover1, wbCover, siteMark, siteJoy, siteSheet, siteDoors, bearJoy, butterfly, markAv, joyAv, wordmark, logoArt,
  cutCat, cutDoor, cutFlowers, cutFriend, cutGarden, cutLeap, cutOxford, cutSit, cutWindow };

const W = 6.4, D = 6.4;            // leaf size (width x depth), the backdrop is the same leaf standing up
const NLEAF = 8;                    // cover + 7 leaves (spreads home, what, read, speak, talk, families, cta)
const HALF = Math.PI / 2;
const q12 = t => Math.floor(t * 12) / 12;   // paper puppets move "on twos" (12 fps) like stop-motion

export function buildStory(stage, B, IMG) {
  stage.renderer.toneMapping = THREE.NoToneMapping;  // keep the paper colours true
  const cue = B.cues, TURN = B.turns;
  const spreadStart = s => TURN[s][1], spreadEnd = s => (TURN[s + 1] ? TURN[s + 1][0] : B.duration);
  const tex = c => { const x = new THREE.CanvasTexture(c); x.colorSpace = THREE.SRGBColorSpace; x.anisotropy = 8; return x; };
  const paperMat = c => new THREE.MeshLambertMaterial({ map: tex(c) });
  const cutMat = c => new THREE.MeshLambertMaterial({ map: tex(c), alphaTest: 0.5, side: THREE.DoubleSide });

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#e9dcc6');
  scene.add(new THREE.HemisphereLight('#fffaf2', '#e3d4bb', 1.95));
  const sun = new THREE.DirectionalLight('#fff3df', 1.5);
  sun.position.set(-5, 10, 9); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 10, bottom: -6, near: 1, far: 40 }); sun.shadow.radius = 4; sun.shadow.bias = -0.0008;
  scene.add(sun);

  // desk: soft linen paper
  const desk = new THREE.Mesh(new THREE.PlaneGeometry(40, 40), paperMat(P.paperTex(1024, 1024, '#e7d8bf', 11, { fibres: 900 })));
  desk.rotation.x = -HALF; desk.position.y = -0.09; desk.receiveShadow = true; scene.add(desk);
  // the book's boards (navy cloth), lower and upper
  const board = new THREE.MeshLambertMaterial({ color: '#22355a' });
  const lower = new THREE.Mesh(new THREE.BoxGeometry(W + 0.36, 0.08, D + 0.3), board); lower.position.set(0, -0.05, D / 2 + 0.08); lower.receiveShadow = true; scene.add(lower);
  const upper = new THREE.Mesh(new THREE.BoxGeometry(W + 0.36, D + 0.3, 0.08), board); upper.position.set(0, D / 2 + 0.06, -0.08); upper.receiveShadow = true; scene.add(upper);

  // ------------------------------------------------ pieces
  const stick = (img, h, pad = 12, seed = 3) => { // a paper cut-out standing on its base, white scissor edge
    const c = P.sticker(img instanceof HTMLCanvasElement ? img : P.imgCanvas(img, 900), pad, { seed });
    const w = h * c.width / c.height, geo = new THREE.PlaneGeometry(w, h); geo.translate(0, h / 2, 0);
    const m = new THREE.Mesh(geo, cutMat(c)); m.castShadow = true; m.receiveShadow = true; m.userData.w = w; return m;
  };
  const card = (img, h, o = {}) => { // a photo / cover printed on a card with a white margin
    const iw = img.width, ih = img.height, m = o.margin ?? 0.06, c = P.canvas(Math.round(iw * (1 + 2 * m)), Math.round(ih + iw * 2 * m));
    const g = c.getContext('2d'); g.fillStyle = '#fffdf7'; g.fillRect(0, 0, c.width, c.height); g.drawImage(img, iw * m, iw * m, iw, ih);
    if (o.label) P.hand(g, o.label, c.width / 2, c.height - iw * m * 0.5, { size: iw * m * 0.6, font: 'PatrickHand', weight: 400, color: P.C.deep });
    return stick(c, h, 4, o.seed || 9);
  };

  // pop-up: a group on a leaf that folds up from flat (hinge at its base) between 'at' and the next page turn
  const pops = [];
  function pop(leaf, x, z, kids, at, o = {}) {
    const gp = new THREE.Group(); gp.position.set(x, 0.006 + (o.layer || 0) * 0.004, z);
    kids.forEach(k => gp.add(k));
    leaf.surface.add(gp);
    const foldAt = o.foldAt ?? (TURN[leaf.idx] ? TURN[leaf.idx][0] : 1e9);
    pops.push({ gp, at, foldAt, leafIdx: leaf.idx, slide: o.slide, ...o });
    return gp;
  }
  const unfold = (p, t) => {
    const tq = q12(t), a = seg(tq, p.at, p.at + 0.55), f = seg(t, p.foldAt - 0.42, p.foldAt - 0.05);
    return clamp(ease.spring(a)) * (1 - ease.io(f));
  };

  // ------------------------------------------------ the leaves
  const leaves = [];
  for (let k = 0; k < NLEAF; k++) {
    const g = new THREE.Group(), surface = new THREE.Group();
    g.add(surface); scene.add(g);
    leaves.push({ idx: k, g, surface, front: null, back: null });
  }
  function face(leaf, canvasFront, canvasBack) {
    const geoF = new THREE.PlaneGeometry(W, D); geoF.rotateX(-HALF); geoF.translate(0, 0, D / 2);
    const f = new THREE.Mesh(geoF, paperMat(canvasFront)); f.receiveShadow = true; f.castShadow = true; leaf.g.add(f);
    if (canvasBack) { const geoB = new THREE.PlaneGeometry(W, D); geoB.rotateX(HALF); geoB.translate(0, -0.002, D / 2);
      const b = new THREE.Mesh(geoB, paperMat(canvasBack)); b.receiveShadow = true; leaf.g.add(b); }
  }
  // leaf k lifts during TURN[k] (leaf 0 is the cover); leaf k's back is the backdrop of spread k, its front the stage of spread k-1
  function leafPose(k, t) {
    const tr = TURN[k];
    const th = tr ? HALF * ease.io(seg(t, tr[0], tr[1])) : 0;
    const n = th / HALF, l = leaves[k];
    l.g.rotation.x = -th;
    l.g.position.set(0, lerp(0.035 * (NLEAF - k), 0, n), lerp(0, 0.03 * k + 0.02, n));
    l.g.visible = !(n >= 1 && TURN[k + 1] && t > TURN[k + 1][1] + 0.1 && k < NLEAF - 2); // hide leaves buried under later backdrops
  }

  // ------------------------------------------------ paper textures for each face
  const S = 1024;
  const floorTex = (seed, rugs = [], o = {}) => {
    const c = P.paperTex(S, S, o.base || P.C.paper, seed), g = c.getContext('2d');
    rugs.forEach(([x, y, rx, ry, col], i) => P.wash(g, P.ell(x, y, rx, ry, 18), col, seed + i * 7, { alpha: 0.75, edge: 16 }));
    const r = (i => () => ((i = (i * 16807) % 2147483647) / 2147483647))(seed * 31 + 7);
    for (let i = 0; i < 26; i++) { const x = r() * S, y = r() * S; P.ink(g, P.ell(x, y, 5, 5, 6), seed + i, { w: 1.6, color: '#b49a7a', passes: 1 }); }
    return c;
  };
  const backdrop = (seed, wash, draw) => {
    const c = P.paperTex(S, S, P.C.paper, seed), g = c.getContext('2d');
    if (wash) { const gr = g.createLinearGradient(0, 0, 0, S); wash.forEach(([p, col]) => gr.addColorStop(p, col)); g.globalAlpha = 0.85; g.fillStyle = gr; g.fillRect(0, 0, S, S); g.globalAlpha = 1;
      g.globalCompositeOperation = 'multiply'; g.drawImage(P.paperTex(S, S, '#ffffff', seed + 1, { vignette: false, fibres: 120 }), 0, 0); g.globalCompositeOperation = 'source-over'; }
    draw && draw(g);
    return c;
  };
  const paste = (g, img, x, y, h, rot = 0, pad = 14) => { // glue a cut-out onto a backdrop with a soft shadow
    const s = P.sticker(P.imgCanvas(img, 900), pad), w = h * s.width / s.height;
    g.save(); g.translate(x, y); g.rotate(rot); g.shadowColor = 'rgba(60,40,20,0.28)'; g.shadowBlur = 18; g.shadowOffsetY = 8;
    g.drawImage(s, -w / 2, -h / 2, w, h); g.restore();
  };
  const cloud = (g, x, y, s, seed) => { const pts = [[-90, 20], [-70, -20], [-30, -40], [10, -50], [50, -30], [90, -10], [100, 20], [40, 34], [-40, 34]].map(([a, b]) => [x + a * s, y + b * s]);
    g.save(); g.shadowColor = 'rgba(60,40,20,0.18)'; g.shadowBlur = 10; g.shadowOffsetY = 5; g.fillStyle = '#fffdf7'; P.smooth(g, pts); g.fill(); g.restore(); P.ink(g, pts, seed, { w: 2.2, color: '#8b98ad' }); };
  const bigWord = (g, en, ko, num, col) => {
    P.hand(g, en, S / 2, 380, { font: 'PatrickHand', weight: 400, size: 230, color: col });
    P.hand(g, `${num} ${ko}`, S / 2, 545, { size: 110, color: P.C.deep });
  };

  const coverC = backdrop(2, [[0, '#1E2D4D'], [1, '#2c4a78']], g => {
    for (let i = 0; i < 60; i++) { const x = (i * 197) % S, y = (i * 389) % S; g.fillStyle = `rgba(246,240,186,${0.25 + (i % 5) * 0.12})`; g.beginPath(); g.arc(x, y, 2 + (i % 3), 0, 7); g.fill(); }
    P.hand(g, 'Once upon a time…', S / 2, 300, { font: 'Title, serif', weight: 600, size: 96, color: '#F6F0BA' });
    P.hand(g, '옛날 옛적에', S / 2, 420, { size: 80, color: '#fffaf0' });
    paste(g, IMG.logoArt, S / 2, 700, 330, -0.04, 10);
  });
  const bdHome = backdrop(4, [[0, '#cfe3f3'], [0.7, '#f3eedf'], [1, '#f7efe0']], g => {
    cloud(g, 200, 150, 1.0, 1); cloud(g, 790, 220, 0.8, 2);
    paste(g, IMG.cutOxford, 560, 560, 760, 0.02);
  });
  const bdWhat = backdrop(6, [[0, '#fbf3c9'], [1, '#f6ecd6']], g => {
    g.drawImage(IMG.wordmark, S / 2 - 330, 110, 660, 660 * IMG.wordmark.height / IMG.wordmark.width);
    paste(g, IMG.cutWindow, 210, 560, 520, -0.05); paste(g, IMG.cutCat, 790, 600, 470, 0.05);
    P.ink(g, [[330, 330], [450, 280], [580, 300], [700, 270]], 3, { closed: false, w: 3, color: '#c9a84c' });
  });
  const bdRead = backdrop(8, [[0, '#dcebf7'], [1, '#f4efe3']], g => { bigWord(g, 'READ', '읽기', '①', '#3d6fa8'); cloud(g, 160, 640, 0.7, 4); cloud(g, 860, 720, 0.6, 5); });
  const bdSpeak = backdrop(10, [[0, '#f8dede'], [1, '#f6efe4']], g => { bigWord(g, 'SPEAK', '말하기', '②', '#c0605e'); });
  const bdTalk = backdrop(12, [[0, '#e3f0d9'], [1, '#f5efe2']], g => { bigWord(g, 'TALK', '대화', '③', '#4f8a4a'); P.ink(g, [[150, 620], [260, 560], [380, 640]], 9, { closed: false, w: 3, color: '#4f8a4a' }); });
  const bdFam = backdrop(14, [[0, '#cfe3f3'], [0.55, '#eef3e3'], [1, '#e3edc9']], g => {
    g.fillStyle = 'rgba(246,224,120,0.9)'; g.beginPath(); g.arc(820, 170, 70, 0, 7); g.fill(); P.ink(g, P.ell(820, 170, 70, 70, 14), 2, { w: 2.4, color: '#c9a84c' });
    cloud(g, 230, 160, 0.9, 6);
    const hill = (y, col, seed) => { const pts = [[-40, S + 40], [-40, y + 60], [200, y], [460, y + 50], [720, y - 20], [1060, y + 40], [1060, S + 40]]; P.wash(g, pts, col, seed, { alpha: 0.85 }); P.ink(g, pts.slice(1, -1), seed, { closed: false, w: 2.4, color: '#6f8f55' }); };
    hill(560, '#b9d99a', 3); hill(700, '#9fca82', 4);
    paste(g, IMG.cutGarden, 760, 640, 360, 0.03); paste(g, IMG.cutSit, 230, 560, 220, -0.04);
  });
  const bdCta = backdrop(16, [[0, '#1E2D4D'], [1, '#2c4a78']], g => {
    for (let i = 0; i < 70; i++) { const x = (i * 211) % S, y = (i * 347) % S; g.fillStyle = `rgba(246,240,186,${0.2 + (i % 5) * 0.12})`; g.beginPath(); g.arc(x, y, 2 + (i % 3), 0, 7); g.fill(); }
  });
  const rugA = '#e9cfa4', rugB = '#cfe0ee', rugC = '#f0d6d6', rugD = '#dce9cf';
  face(leaves[0], coverC, bdHome);
  face(leaves[1], floorTex(21, [[512, 640, 380, 170, rugA]]), bdWhat);
  face(leaves[2], floorTex(23, [[512, 860, 470, 120, '#d7e6c6']]), bdRead);
  face(leaves[3], floorTex(25, [[640, 640, 300, 150, rugB]]), bdSpeak);
  face(leaves[4], floorTex(27, [[512, 860, 440, 110, rugC]]), bdTalk);
  face(leaves[5], floorTex(29, [[330, 640, 270, 120, rugA]]), bdFam);
  face(leaves[6], floorTex(31, [[280, 850, 260, 100, rugA], [760, 850, 260, 100, rugB], [280, 420, 240, 90, rugC], [760, 420, 240, 90, rugD]], { base: '#f3f1e2' }), bdCta);
  face(leaves[7], floorTex(33, [[512, 700, 400, 150, '#2c4a78']]), null);
  // leaf k's front is the stage of spread k-1: spread s pops live on leaves[s + 1]
  const stage_ = s => leaves[s + 1];

  // ------------------------------------------------ people
  const people = [];
  function person(kind, scale, seed) {
    const p = P.PEOPLE[kind], body = P.drawBody(p.adult ? p : { ...p, book: null }, seed);
    const heads = ['idle', 'talk', 'blink'].map(st => cutMat(P.sticker(P.drawHead(p, st, seed), 10, { seed })));
    const bodyS = P.sticker(body, 10, { seed: seed + 1 });
    const wB = 1.65 * scale, hB = wB * bodyS.height / bodyS.width;
    const geoB = new THREE.PlaneGeometry(wB, hB); geoB.translate(0, hB / 2, 0);
    const bm = new THREE.Mesh(geoB, cutMat(bodyS)); bm.castShadow = true;
    const hs = p.adult ? 1 : 1.16, hc = P.sticker(P.drawHead(p, 'idle', seed), 10, { seed });
    const wH = wB * hc.width / bodyS.width * hs, hH = wH * hc.height / hc.width;
    const geoH = new THREE.PlaneGeometry(wH, hH); geoH.translate(0, hH * (260 / 320 - 0.5), 0);
    const hm = new THREE.Mesh(geoH, heads[0]); hm.castShadow = true;
    const neck = new THREE.Group(); neck.position.set(0, hB * (1 - 88 / bodyS.height), 0.012); neck.add(hm);
    const g = new THREE.Group(); g.add(bm, neck);
    const pr = { g, neck, hm, heads, seed, talks: [], topY: hB * (1 - 88 / bodyS.height) + hH * (260 / 320) };
    people.push(pr); return pr;
  }
  function personUpdate(pr, t) {
    const tq = q12(t), talking = pr.talks.some(([a, b]) => t >= a && t < b);
    const blink = ((tq + pr.seed * 0.37) % 3.3) < 0.12;
    pr.hm.material = pr.heads[talking ? (Math.floor(tq * 6) % 2 ? 1 : 0) : blink ? 2 : 0];
    pr.neck.rotation.z = wobble(tq * 0.8, pr.seed) * 0.07 + (talking ? Math.sin(tq * 9) * 0.04 : 0);
    pr.g.position.y = talking ? Math.abs(Math.sin(tq * 9)) * 0.02 : 0;
  }
  function pair(adult, child, sc, seed) { // grown-up on the left, child on the right, sharing the book
    const a = person(adult, sc, seed), c = person(child, sc * 0.7, seed + 5);
    a.g.position.set(-0.52 * sc, 0, 0); c.g.position.set(0.66 * sc, 0, 0.02);
    return { a, c, kids: [a.g, c.g] };
  }
  // speech bubbles ride on their pop-up and pop in with a spring
  const bubbles = [];
  function bub(parent, en, ko, s, e, x, y, o = {}) {
    const c = P.sticker(P.bubble(en, ko, { tail: o.tail, w: o.w }), 6), h = o.h || 0.85, w = h * c.width / c.height;
    const geo = new THREE.PlaneGeometry(w, h); geo.translate(0, h / 2, 0);
    const m = new THREE.Mesh(geo, cutMat(c)); m.position.set(x, y, 0.08); m.castShadow = true; parent.add(m);
    bubbles.push({ m, s, e }); return m;
  }
  const talkOf = name => B.talks.filter(r => r[0] === name);

  // ------------------------------------------------ spread 0: home — you and your child, a worry, the bear arrives
  const home = pair('mum', 'girl', 1.0, 1);
  pop(stage_(0), -0.3, 3.6, home.kids, spreadStart(0) + 0.15);
  const worryC = P.canvas(700, 420), wg = worryC.getContext('2d');
  { const pts = [[80, 210], [70, 120], [170, 60], [300, 40], [430, 50], [560, 70], [640, 150], [630, 260], [540, 330], [380, 350], [220, 340], [110, 300]];
    wg.fillStyle = '#fffdf7'; P.smooth(wg, pts); wg.fill(); P.ink(wg, pts, 4, { w: 3 });
    for (const [x, y, r] of [[140, 390, 22], [90, 410, 12]]) { wg.fillStyle = '#fffdf7'; wg.beginPath(); wg.arc(x, y - 30, r, 0, 7); wg.fill(); P.ink(wg, P.ell(x, y - 30, r, r, 8), 5, { w: 2.4 }); }
    P.hand(wg, '내 발음이…', 360, 150, { size: 82, color: P.C.deep }); P.hand(wg, '괜찮을까?', 360, 250, { size: 82, color: '#c0605e' }); }
  const worry = new THREE.Mesh((() => { const gg = new THREE.PlaneGeometry(2.2, 1.32); gg.translate(0.4, 0.66, 0); return gg; })(), cutMat(P.sticker(worryC, 8)));
  worry.position.set(-0.9, 2.3, 0.1); home.a.g.add(worry); bubbles.push({ m: worry, s: cue['worry'], e: spreadStart(0) + 6.0 + 2.7 });
  const leap = stick(IMG.cutLeap, 1.55, 10, 21);
  const leapPop = pop(stage_(0), 2.1, 4.4, [leap], cue['bear-in'] - 0.05, { layer: 2 });
  const bfly = stick(IMG.butterfly, 0.55, 8, 22); scene.add(bfly);

  // ------------------------------------------------ spread 1: what Bear & Joy is — cut-outs from our books
  pop(stage_(1), -1.55, 2.2, [stick(IMG.cutDoor, 2.7, 14, 31)], cue['door']);
  pop(stage_(1), 1.5, 3.1, [stick(IMG.cutFriend, 2.0, 12, 32)], cue['friend']);
  pop(stage_(1), 0, 5.4, [stick(IMG.cutFlowers, 1.15, 10, 33)], cue['flowers'], { layer: 2 });

  // ------------------------------------------------ spread 2: READ — the storybook
  pop(stage_(2), -1.5, 2.0, [card(IMG.cover1, 2.35, { margin: 0.03, seed: 41 })], cue['read-book']);
  const readPair = pair('mum', 'girl', 0.95, 1);
  pop(stage_(2), 1.1, 3.9, readPair.kids, cue['read-pair'], { layer: 1 });
  pop(stage_(2), -1.9, 5.2, [stick(IMG.cutSit, 0.9, 10, 43)], cue['read-bear'], { layer: 2 });
  for (const r of talkOf('read')) { readPair.c.talks.push([r[2], r[3]]); bub(readPair.c.g, r[4], r[5], r[2], r[3], 0.4, readPair.c.topY + 0.05, { h: 0.75, w: 460, tail: 'left' }); }

  // ------------------------------------------------ spread 3: SPEAK — the Walkbook's Korean-sound guide and STOP · LOOK · LISTEN
  pop(stage_(3), -1.75, 1.7, [card(IMG.wbCover, 2.2, { margin: 0.03, seed: 51 })], cue['speak-book']);
  const pronC = P.canvas(880, 560); let pronState = -1;
  const pronMat = cutMat(pronC); const pronTex = pronMat.map;
  function drawPron(k) { // the guide's idea, set by hand: English line, Korean sound under it; a pencil circle draws round the sound
    const g = pronC.getContext('2d'); g.clearRect(0, 0, 880, 560);
    const pc = P.paperTex(840, 520, '#fbf3e6', 52, { fibres: 80 }); g.drawImage(P.sticker(pc, 18), 2, 2, 876, 556);
    P.hand(g, 'Walkbook · 발음 가이드', 440, 80, { size: 46, color: '#9a8a70' });
    P.hand(g, 'One morning,', 440, 210, { font: 'Title, serif', weight: 500, size: 92, color: '#2c4a78' });
    P.hand(g, '원 모닝,', 440, 360, { size: 120, color: '#8a4b3a' });
    if (k > 0) { g.save(); g.strokeStyle = '#d65a4a'; g.lineWidth = 7; g.lineCap = 'round'; g.beginPath();
      for (let i = 0; i <= 40 * k; i++) { const a = -2.6 + i / 40 * Math.PI * 2.15; g.lineTo(440 + Math.cos(a) * (200 + Math.sin(i) * 4), 360 + Math.sin(a) * (80 + Math.cos(i * 1.3) * 3)); } g.stroke(); g.restore(); }
    pronTex.needsUpdate = true;
  }
  drawPron(0);
  const pronH = 1.6, pronGeo = new THREE.PlaneGeometry(pronH * 880 / 560, pronH); pronGeo.translate(0, pronH / 2, 0);
  const pronCard = new THREE.Mesh(pronGeo, pronMat); pronCard.castShadow = true; pronCard.position.y = 0.35;
  pop(stage_(3), 1.25, 2.4, [pronCard], cue['speak-card']);
  const flagMesh = (en, ko, col, seed) => {
    const c = P.canvas(420, 640), g = c.getContext('2d');
    P.ink(g, [[60, 40], [60, 630]], seed, { closed: false, w: 9, color: '#8a6a4a' });
    const fl = [[66, 50], [400, 70], [370, 190], [400, 320], [66, 300]]; P.wash(g, fl, col, seed); P.ink(g, fl, seed);
    P.hand(g, en, 228, 150, { font: 'PatrickHand', weight: 400, size: 86, color: '#fffdf7' }); P.hand(g, ko, 228, 248, { size: 56, color: '#fffdf7' });
    return stick(P.sticker(c, 6), 1.3, 2, seed);
  };
  pop(stage_(3), -1.9, 5.2, [flagMesh('STOP', '멈추고', '#d9776f', 61)], cue['stop'], { layer: 1 });
  pop(stage_(3), 0.0, 5.45, [flagMesh('LOOK', '함께 보고', '#6f9fcf', 62)], cue['look'], { layer: 1 });
  pop(stage_(3), 1.9, 5.2, [flagMesh('LISTEN', '들어주기', '#7fb36f', 63)], cue['listen'], { layer: 1 });

  // ------------------------------------------------ spread 4: TALK — Little Steps on a paper tablet, Mark and Joy helping
  const tabC = P.canvas(1000, 760), tabTex = tex(tabC); let tabState = -1;
  function drawTab(i) {
    const g = tabC.getContext('2d'); g.clearRect(0, 0, 1000, 760);
    const frame = [[30, 40], [970, 40], [970, 650], [30, 650]]; g.fillStyle = '#22355a'; g.beginPath(); g.roundRect(24, 30, 952, 630, 46); g.fill();
    P.ink(g, frame, 71, { w: 3 });
    const im = [IMG.siteMark, IMG.siteJoy, IMG.siteSheet][i]; const sw = 880, sh = 520;
    g.save(); g.beginPath(); g.roundRect(60, 70, sw, sh, 14); g.clip(); g.fillStyle = '#fff'; g.fillRect(60, 70, sw, sh);
    const k = Math.max(sw / im.width, sh / im.height); g.drawImage(im, 60 + (sw - im.width * k) / 2, 70 + (sh - im.height * k) / 2, im.width * k, im.height * k); g.restore();
    g.fillStyle = 'rgba(255,253,247,0.92)'; g.beginPath(); g.roundRect(330, 610, 340, 90, 40); g.fill();
    P.hand(g, ['Mark T · 영어 소리', 'Joy T · 함께 놀기', '무료 활동지'][i], 500, 656, { size: 52, color: P.C.deep });
    tabTex.needsUpdate = true;
  }
  drawTab(0);
  const tabH = 2.35, tabGeo = new THREE.PlaneGeometry(tabH * 1000 / 760, tabH); tabGeo.translate(0, tabH / 2, 0);
  const tablet = new THREE.Mesh(tabGeo, new THREE.MeshLambertMaterial({ map: tabTex, alphaTest: 0.5, side: THREE.DoubleSide })); tablet.castShadow = true;
  const tabPop = pop(stage_(4), -0.35, 1.6, [tablet], cue['talk-tablet']);
  const doorsCard = card(IMG.siteDoors, 0.62, { margin: 0.025, seed: 72 }); void doorsCard;
  const tPair = pair('mum', 'girl', 0.9, 1);
  pop(stage_(4), -1.45, 4.4, tPair.kids, cue['talk-pair'], { layer: 1 });
  for (const r of talkOf('talk')) { tPair.a.talks.push([r[2], r[3]]); bub(tPair.a.g, r[4], r[5], r[2], r[3], -0.4, tPair.a.topY + 0.02, { h: 0.7, w: 640, tail: 'left' }); }
  const avatar = (img, name, seed) => {
    const c = P.canvas(420, 620), g = c.getContext('2d');
    P.ink(g, [[210, 380], [210, 610]], seed, { closed: false, w: 8, color: '#8a6a4a' });
    g.drawImage(img, 20, 0, 380, 380); P.hand(g, name, 210, 450, { font: 'PatrickHand', weight: 400, size: 70, color: P.C.deep });
    return stick(c, 1.85, 10, seed);
  };
  const markPop = pop(stage_(4), 1.35, 4.3, [avatar(IMG.markAv, 'Mark T', 73)], cue['mark'], { layer: 2 });
  const joyPop = pop(stage_(4), 2.45, 3.6, [avatar(IMG.joyAv, 'Joy T', 74)], cue['joy'], { layer: 2 });
  bub(joyPop, 'Ask us anytime!', '언제든 물어보세요', cue['joy'] + 0.4, spreadEnd(4) - 0.4, -0.95, 1.62, { h: 0.78, w: 620, tail: 'right' });

  // ------------------------------------------------ spread 5: families talking in English
  const FAM = { fam1: ['mum', 'girl', -1.55, 4.35, 11], fam2: ['dad', 'boy', 1.55, 4.35, 12], fam3: ['grandma', 'girl2', -1.55, 1.95, 13], fam4: ['boy2', 'girl', 1.55, 1.95, 14] };
  const famPairs = {};
  for (const [k, [ad, ch, x, z, seed]] of Object.entries(FAM)) {
    const pr = k === 'fam4' ? (() => { const a = person('boy2', 0.66, seed), c = person('girl', 0.66, seed + 5); a.g.position.set(-0.42, 0, 0); c.g.position.set(0.42, 0, 0.05); return { a, c, kids: [a.g, c.g] }; })()
      : pair(ad, ch, 0.82, seed);
    famPairs[k] = pr;
    const gp = pop(stage_(5), x, z, pr.kids, cue[k], { layer: k === 'fam1' || k === 'fam2' ? 1 : 0 });
    for (const r of talkOf(k)) {
      const who = r[1] === 'adult' ? pr.a : pr.c; who.talks.push([r[2], r[3]]);
      bub(gp, r[4], r[5], r[2], r[3], r[1] === 'adult' ? -0.35 : 0.45, (r[1] === 'adult' ? pr.a.topY : pr.c.topY) + 0.08, { h: 0.8, w: 620, tail: r[1] === 'adult' ? 'left' : 'right' });
    }
  }
  if (famPairs.fam4) { /* friends: a book between them */ }

  // ------------------------------------------------ spread 6: Book 1 and the comment call
  pop(stage_(6), -0.55, 1.9, [card(IMG.cover1, 3.0, { margin: 0.03, seed: 81 })], cue['cta-book']);
  pop(stage_(6), -2.0, 3.9, [stick(IMG.bearJoy, 1.75, 12, 82)], cue['cta-bear'], { layer: 1 });
  const comC = P.canvas(900, 300), cg = comC.getContext('2d');
  { cg.fillStyle = '#fffdf7'; cg.beginPath(); cg.roundRect(10, 10, 880, 280, 40); cg.fill(); P.ink(cg, [[20, 20], [880, 20], [880, 280], [20, 280]], 3, { w: 3 });
    cg.fillStyle = '#AECCE6'; cg.beginPath(); cg.arc(110, 150, 60, 0, 7); cg.fill(); P.ink(cg, P.ell(110, 150, 60, 60, 12), 4, { w: 2.6 });
    P.hand(cg, '나', 110, 156, { size: 60, color: P.C.deep });
    P.hand(cg, 'Bear', 300, 150, { font: 'PatrickHand', weight: 400, size: 130, color: P.C.deep, align: 'left' });
    P.hand(cg, '♥', 800, 150, { font: 'PatrickHand', weight: 400, size: 90, color: '#d65a4a' }); }
  const comment = new THREE.Mesh((() => { const gg = new THREE.PlaneGeometry(2.7, 0.9); gg.translate(0, 0.4, 0); return gg; })(), cutMat(P.sticker(comC, 8)));
  comment.position.y = 0.15; // floats above the page, clear of the bottom of the frame
  const comPop = pop(stage_(6), 0.95, 4.6, [comment], cue['cta-comment'], { layer: 2 });

  // ------------------------------------------------ the world over time
  function world(t) {
    for (let k = 0; k < NLEAF; k++) leafPose(k, t);
    for (const p of pops) { const u = unfold(p, t); p.gp.rotation.x = -HALF * (1 - u); p.gp.visible = t >= TURN[p.leafIdx - 1][0] && (u > 0.001 || t < p.at); } // hidden until the page above starts to turn
    for (const pr of people) personUpdate(pr, t);
    for (const b of bubbles) {
      const tq = q12(t), a = clamp(ease.spring(seg(tq, b.s, b.s + 0.4))), z = 1 - seg(t, b.e - 0.18, b.e);
      const k = a * z; b.m.scale.setScalar(Math.max(0.001, k)); b.m.visible = k > 0.01;
      b.m.rotation.z = Math.sin(tq * 3 + b.s) * 0.02;
    }
    // the leaping bear: hops in from the right edge, lands beside the family
    { const tq = q12(t), a = cue['bear-in'], p = seg(tq, a, a + 1.1);
      leap.position.set(lerp(2.2, 0, ease.out(p)), Math.abs(Math.sin(p * Math.PI * 3)) * 0.7 * (1 - p), 0);
      leap.rotation.z = (1 - p) * Math.sin(p * 19) * 0.2; void leapPop; }
    // Joy the butterfly flutters over spread 0 and spread 1, then lands on Book 1 at the end
    { const tq = q12(t), flap = 0.55 + 0.45 * Math.abs(Math.sin(tq * 14));
      let pos = null;
      if (t > cue['bear-in'] + 0.4 && t < spreadEnd(1) - 0.3) pos = [1.6 + Math.sin(t * 1.3) * 1.6, 3.0 + Math.sin(t * 2.1) * 0.5, 3.2 + Math.cos(t * 1.1) * 0.8];
      if (t > cue['cta-bear'] + 0.3) { const p = ease.io(seg(t, cue['cta-bear'] + 0.3, cue['cta-bear'] + 2.2)); pos = [lerp(-2.2, 1.0, p), lerp(2.6, 2.95, p) + Math.sin(p * Math.PI) * 0.6, lerp(4.0, 2.05, p)]; }
      bfly.visible = !!pos; if (pos) { bfly.position.set(...pos); bfly.scale.set(flap, 1, 1); bfly.rotation.z = Math.sin(tq * 5) * 0.15; } }
    // the pronunciation circle draws itself; the tablet changes screens
    { const k = Math.round(seg(t, cue['speak-circle'], cue['speak-circle'] + 0.9) * 12) / 12; if (k !== pronState) { pronState = k; drawPron(k); } }
    { const i = t < cue['talk-joy-screen'] ? 0 : t < cue['talk-sheet'] ? 1 : 2; if (i !== tabState) { tabState = i; drawTab(i); } }
    void comPop; void markPop;
  }

  // ------------------------------------------------ camera
  const BASE = { pos: [0, 6.6, 18.6], look: [0, 2.55, 2.1], fov: 40 };
  const famFocus = [[0, 0, 0], [0, -0.2, -1.4], [0, -0.2, -1.4], [0, 0.1, -2.0], [0, 0.1, -2.0], [0, 0, 0]];  // push in, no side pan (bubbles stay in frame)
  function cam(t) {
    const top = { pos: [0, 18.5, 4.5], look: [0, 0, 3.4], fov: 40 };
    let pos = keys(t, [[0, top.pos], [1.2, top.pos], [3.4, BASE.pos, 'io']]);
    let look = keys(t, [[0, top.look], [1.2, top.look], [3.4, BASE.look, 'io']]);
    const fov = keys(t, [[0, 40], [3.4, BASE.fov, 'io']]);
    // families: glide to each pair while it talks
    const F = (i) => { const f = famFocus[i]; return [BASE.pos[0] + f[0], BASE.pos[1] + f[1], BASE.pos[2] + f[2]]; };
    const ts = B.talks.filter(r => r[0].startsWith('fam'));
    if (t > 44.0 && t < 52.2) {
      const k = [[44.0, 0], [44.6, 1], [46.3, 2], [48.1, 3], [49.7, 4], [51.6, 5]];
      const fp = keys(t, k.map(([a, i]) => [a, F(i)])), lk = keys(t, k.map(([a, i]) => [a, [0, BASE.look[1] - 0.6 * (i ? 1 : 0), BASE.look[2] + (i ? 1.0 : 0)]]));
      const w = seg(t, 44.0, 44.4) * (1 - seg(t, 51.6, 52.2)); pos = pos.map((v, j) => lerp(v, fp[j], w)); look = look.map((v, j) => lerp(v, lk[j], w)); void ts;
    }
    const cta = ease.io(seg(t, 53.0, 56.0)); pos = pos.map((v, j) => lerp(v, [0, 6.0, 16.8][j], cta)); look = look.map((v, j) => lerp(v, [0, 2.6, 2.1][j], cta));
    const h = 0.05; pos = [pos[0] + wobble(t * 0.4, 1) * h, pos[1] + wobble(t * 0.35, 2) * h, pos[2]];
    return { pos, look, fov };
  }

  // ------------------------------------------------ words on screen: a paper ribbon of story text at the top (safe zone y 300-1450)
  const ribbon = P.paperTex(980, 260, '#fffaf0', 91, { fibres: 60 });
  function line(g, t, [a, b, ko, en]) {
    const k = seg(t, a, a + 0.35) * (1 - seg(t, b - 0.25, b)); if (k <= 0) return;
    g.save(); g.globalAlpha = ease.out(k); g.translate(540, 400 + (1 - ease.out(k)) * 16);
    g.rotate(-0.008); g.shadowColor = 'rgba(60,40,20,0.25)'; g.shadowBlur = 14; g.shadowOffsetY = 6;
    g.drawImage(ribbon, -490, -96, 980, 214); g.shadowColor = 'transparent';
    g.font = '700 64px Gaegu'; const kw = g.measureText(ko).width, ks = Math.min(1, 900 / kw);
    P.hand(g, ko, 0, -22, { size: 64 * ks, color: P.C.deep });
    g.font = '400 40px PatrickHand'; const ew = g.measureText(en).width, es = Math.min(1, 900 / ew);
    P.hand(g, en, 0, 56, { font: 'PatrickHand', weight: 400, size: 40 * es, color: '#7a6a55' });
    g.restore();
  }
  function ctaCard(g, t) {
    const a = cue['cta-comment'] - 0.1, k = clamp(ease.spring(seg(q12(t), a, a + 0.6)));
    if (k <= 0) return;
    g.save(); g.translate(540, 420); g.scale(k, k); g.rotate(-0.012);
    g.shadowColor = 'rgba(20,20,40,0.35)'; g.shadowBlur = 22; g.shadowOffsetY = 8;
    g.drawImage(P.paperTex(980, 300, '#fffaf0', 93, { fibres: 60 }), -490, -150, 980, 300); g.shadowColor = 'transparent';
    P.hand(g, '댓글에 ‘Bear’ 남기고', 0, -70, { size: 76, color: P.C.deep });
    P.hand(g, 'Book 1을 가장 먼저 만나보세요!', 0, 20, { size: 72, color: '#c0605e' });
    P.hand(g, 'Comment “Bear” to be the first to own Book 1.', 0, 100, { font: 'PatrickHand', weight: 400, size: 42, color: '#7a6a55' });
    g.restore();
  }
  function overlay(g, t) {
    for (const l of B.lines) line(g, t, l);
    ctaCard(g, t);
  }

  const sets = { book: { scene, update: t => world(t) } };
  const shots = [{ set: 'book', dur: B.duration, cam: (l) => cam(l) }];
  const design = [];
  return { sets, shots, overlay, design, designTitle: B.title, finish: { grain: 0.04, vignette: 0, fadeIn: 0.4, fadeOut: 0.6 } };
}
