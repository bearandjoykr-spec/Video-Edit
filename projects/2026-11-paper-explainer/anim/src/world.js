// The journey (owner, 24 Nov 2026): "the scale of this little blue bear from Oxford, travelling the world to find his name,
// meeting friends along the way, and ending up in Seoul with your child who gets to name him". A paper globe with
// watercolour continents on hanji; the bear hops along the top while the globe turns city by city, and each city's
// friend folds up out of the surface. Route and friends follow the 24-book series (projects/2026-11-cinematic-film).
import { THREE, keys, seg, ease, lerp, clamp, wobble, rng } from './kit.js';
import * as P from './paper.js';
import { stop } from './stencils.js';
import land from './assets/ne_110m_land.json';

export const R = 4;
export const STOPS = [ // city, lon, lat, landmark, friend, arrival (s), label (en, ko)
  ['oxford', -1.26, 51.75, 'oxford', null, 0, 'OXFORD', '옥스퍼드'],
  ['london', -0.13, 51.51, 'london', 'lion', 6.4, 'LONDON', '런던'],
  ['paris', 2.35, 48.86, 'paris', 'swan', 7.8, 'PARIS', '파리'],
  ['cairo', 31.24, 30.04, 'cairo', 'camel', 9.2, 'CAIRO', '카이로'],
  ['nairobi', 36.82, -1.29, 'nairobi', 'giraffe', 10.6, 'NAIROBI', '나이로비'],
  ['chengdu', 104.07, 30.57, 'chengdu', 'panda', 12.0, 'CHENGDU', '청두'],
  ['sydney', 151.21, -33.87, 'sydney', 'koala', 13.4, 'SYDNEY', '시드니'],
  ['rio', -43.17, -22.91, 'rio', 'toucan', 14.8, 'RIO', '리우'],
  ['newyork', -74.0, 40.71, 'newyork', 'sparrow', 16.2, 'NEW YORK', '뉴욕'],
  ['tokyo', 139.69, 35.69, 'tokyo', 'crane', 17.6, 'TOKYO', '도쿄'],
  ['seoul', 126.98, 37.57, 'seoul', 'tiger', 19.2, 'SEOUL', '서울'],
];
const D2R = Math.PI / 180;
export const vec = (lon, lat) => new THREE.Vector3(Math.cos(lat * D2R) * Math.cos(lon * D2R), Math.sin(lat * D2R), -Math.cos(lat * D2R) * Math.sin(lon * D2R));
const northOf = (lon, lat) => new THREE.Vector3(-Math.sin(lat * D2R) * Math.cos(lon * D2R), Math.cos(lat * D2R), Math.sin(lat * D2R) * Math.sin(lon * D2R)).normalize();
// local frame at a city: X = east, Y = up (surface normal), Z = south (faces the camera when the city is on top)
export function cityBasis(lon, lat) {
  const v = vec(lon, lat), n = northOf(lon, lat), e = new THREE.Vector3().crossVectors(n, v).normalize(), s = n.clone().negate();
  return new THREE.Matrix4().makeBasis(e, v, s);
}

// equirectangular paper map: hanji sea, watercolour land, pencil graticule, red dotted route
function globeTexture() {
  const W = 2048, H = 1024, c = P.paperTex(W, H, '#d8e0d6', 5, { fibres: 700, spots: 30, ring: false }), g = c.getContext('2d');
  const X = lon => (lon + 180) / 360 * W, Y = lat => (90 - lat) / 180 * H;
  g.strokeStyle = 'rgba(110,100,85,0.22)'; g.lineWidth = 1.4;
  for (let lon = -180; lon <= 180; lon += 30) { g.beginPath(); g.moveTo(X(lon), 0); g.lineTo(X(lon), H); g.stroke(); }
  for (let lat = -60; lat <= 60; lat += 30) { g.beginPath(); g.moveTo(0, Y(lat)); g.lineTo(W, Y(lat)); g.stroke(); }
  const cols = ['#c9c08e', '#b9c58f', '#d6c08f', '#c4b98a', '#bcc99a'];
  land.features.forEach((f, i) => {
    const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
    polys.forEach(poly => { const ring = poly[0]; if (ring.length < 4) return;
      const pts = ring.map(([lon, lat]) => [X(lon), Y(lat)]);
      g.save(); g.beginPath(); pts.forEach(([x, y], k) => (k ? g.lineTo(x, y) : g.moveTo(x, y))); g.closePath();
      g.fillStyle = cols[i % cols.length]; g.globalAlpha = 0.9; g.fill(); g.clip();
      g.globalAlpha = 0.25; g.strokeStyle = '#7f7a5a'; g.lineWidth = 10; g.filter = 'blur(3px)'; g.stroke(); g.filter = 'none'; g.restore();
      g.save(); g.strokeStyle = '#4a4236'; g.globalAlpha = 0.8; g.lineWidth = 2; g.beginPath(); pts.forEach(([x, y], k) => (k ? g.lineTo(x, y) : g.moveTo(x, y))); g.closePath(); g.stroke(); g.restore();
    });
  });
  // the route, a dashed red brush line (east across the Pacific from Sydney to Rio, as the books go)
  g.save(); g.strokeStyle = '#b8352b'; g.lineWidth = 4; g.setLineDash([14, 12]); g.globalAlpha = 0.85;
  for (let i = 0; i < STOPS.length - 1; i++) {
    let [, l0, a0] = STOPS[i], [, l1, a1] = STOPS[i + 1];
    if (l1 - l0 > 180) l1 -= 360; if (l0 - l1 > 180) l1 += 360;
    g.beginPath(); for (let k = 0; k <= 40; k++) { let lon = l0 + (l1 - l0) * k / 40, lat = a0 + (a1 - a0) * k / 40 + Math.sin(Math.PI * k / 40) * 6;
      lon = ((lon + 540) % 360) - 180; const x = X(lon), y = Y(lat); if (k && Math.abs(x - g._lx) > W / 2) g.moveTo(x, y); else (k ? g.lineTo(x, y) : g.moveTo(x, y)); g._lx = x; }
    g.stroke();
  }
  g.restore();
  for (const [, lon, lat] of STOPS) { g.fillStyle = '#b8352b'; g.beginPath(); g.arc(X(lon), Y(lat), 7, 0, 7); g.fill(); }
  return c;
}

export function buildWorld(B, IMG, h) { // h: helpers from story.js (stick, cutMat, tex, label…)
  const scene = new THREE.Scene();
  { const c = P.canvas(4, 512), g = c.getContext('2d'), gr = g.createLinearGradient(0, 0, 0, 512);
    gr.addColorStop(0, '#d9e2dc'); gr.addColorStop(0.55, '#efe6cf'); gr.addColorStop(1, '#f2e4c8'); g.fillStyle = gr; g.fillRect(0, 0, 4, 512);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; scene.background = t; }
  scene.add(new THREE.HemisphereLight('#fff6e6', '#d9c7aa', 1.9));
  const sun = new THREE.DirectionalLight('#ffeed2', 1.4); sun.position.set(-6, 12, 10); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -7, right: 7, top: 9, bottom: -7, near: 1, far: 50 }); sun.shadow.radius = 4; sun.shadow.bias = -0.0008; scene.add(sun);

  // paper clouds drifting far behind (stencil clouds on thin wires)
  const clouds = [];
  for (let i = 0; i < 6; i++) { const c = P.canvas(420, 200), g = c.getContext('2d'), pts = [[30, 150], [40, 90], [110, 50], [190, 40], [270, 60], [340, 90], [390, 150]];
    g.fillStyle = '#fbf6ea'; P.smooth(g, pts.concat([[210, 175]])); g.fill(); P.ink(g, pts, 70 + i, { closed: false, w: 2.4, color: '#8b98ad' });
    const m = h.stick(c, 1.4 + (i % 3) * 0.4, 6, 80 + i); m.position.set(-9 + i * 3.6, 6 + (i % 2) * 2.2, -9 - (i % 3) * 3); scene.add(m); clouds.push(m); }

  const globe = new THREE.Group(); scene.add(globe);
  const sphere = new THREE.Mesh(new THREE.SphereGeometry(R, 128, 80), new THREE.MeshLambertMaterial({ map: h.tex(globeTexture()) }));
  sphere.receiveShadow = true; sphere.castShadow = true; globe.add(sphere);

  // a friend + landmark pops up out of the surface at each stop, with a paper luggage tag for the place
  const pops = [];
  STOPS.forEach(([name, lon, lat, lm, fr, at, en, ko], i) => {
    const site = new THREE.Group(); site.applyMatrix4(cityBasis(lon, lat)); site.position.copy(vec(lon, lat).multiplyScalar(R - 0.01)); globe.add(site);
    const hinge = new THREE.Group(); site.add(hinge);
    const card = h.stick(stop(lm, fr, 7 + i * 13), name === 'oxford' ? 1.7 : 1.55, 10, 90 + i); card.position.set(0.62, 0, -0.15); hinge.add(card);   // friends stand to the right of the path, the bear on the left
    const tagC = P.canvas(420, 170), tg = tagC.getContext('2d');
    tg.fillStyle = '#f4ead2'; tg.beginPath(); tg.moveTo(40, 10); tg.lineTo(410, 10); tg.lineTo(410, 160); tg.lineTo(40, 160); tg.lineTo(8, 85); tg.closePath(); tg.fill();
    P.ink(tg, [[40, 10], [410, 10], [410, 160], [40, 160], [8, 85]], 5 + i, { w: 2.4, passes: 1 }); tg.fillStyle = '#b8352b'; tg.beginPath(); tg.arc(44, 85, 9, 0, 7); tg.fill();
    P.hand(tg, en, 232, 64, { font: 'Title, serif', weight: 700, size: 52, color: '#2a2420' }); P.hand(tg, ko, 232, 124, { font: 'Batang', weight: 700, size: 42, color: '#8a4b3a' });
    const tag = h.stick(tagC, 0.36, 4, 120 + i); tag.position.set(0.7, 0.02, 0.6); tag.rotation.z = -0.05; hinge.add(tag);
    pops.push({ hinge, at: i === 0 ? -1 : at - 0.55, i });
  });

  // the traveller: the leaping bear from Book One, always on top of the world, hopping while the globe turns under him
  const bear = h.stick(IMG.cutLeap, 1.05, 10, 140); scene.add(bear);
  const bfly = h.stick(IMG.butterfly, 0.32, 8, 141); scene.add(bfly);

  // globe orientation: each city in turn rotated to the top, north pointing away from the camera
  const Q = STOPS.map(([, lon, lat]) => new THREE.Quaternion().setFromRotationMatrix(cityBasis(lon, lat)).invert());
  const QFRONT = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), Math.PI / 2).multiply(new THREE.Quaternion().setFromRotationMatrix(cityBasis(55, 28)).invert());
  const DEPART = 4.9;   // the bear sets off from Oxford
  function orient(t) {
    let i = 0; while (i < STOPS.length - 1 && t >= STOPS[i + 1][5] - 0.95) i++;   // travel leg i -> i+1 takes the 0.95 s before arrival
    if (i >= STOPS.length - 1) return { q: Q[Q.length - 1], moving: 0, leg: STOPS.length - 1 };
    const t0 = i === 0 ? DEPART : STOPS[i + 1][5] - 0.95, t1 = STOPS[i + 1][5];
    const p = i === 0 ? ease.io(seg(t, DEPART, STOPS[1][5])) : ease.io(seg(t, t0, t1));
    return { q: Q[i].clone().slerp(Q[i + 1], p), moving: p > 0 && p < 1 ? 1 : 0, leg: i, p };
  }
  const q12 = t => Math.floor(t * 12) / 12;
  function update(t) {
    const o = orient(t); globe.quaternion.copy(o.q);
    // a slow drift spin after Seoul for the big pull-back, so the friends parade round the planet
    // the big pull-back after Seoul: swing the globe to face Europe-Africa-Asia so the whole route of friends stands round the rim,
    // then swing back to Seoul on top for the dive
    if (t > 19.6) { const k = ease.io(seg(t, 19.7, 21.0)) * (1 - ease.io(seg(t, 21.9, 22.9))); globe.quaternion.copy(Q[Q.length - 1].clone().slerp(QFRONT, k)); }
    for (const p of pops) { const tq = q12(t), u = p.at < 0 ? 1 : clamp(ease.spring(seg(tq, p.at, p.at + 0.5))); p.hinge.rotation.x = -Math.PI / 2 * (1 - u); p.hinge.visible = true; }
    // the bear: stands at Oxford, hops along every leg (three hops per leg), lands on each top
    const tq = q12(t), hopP = o.moving ? (o.leg === 0 ? seg(tq, DEPART, STOPS[1][5]) : seg(tq, STOPS[o.leg + 1][5] - 0.95, STOPS[o.leg + 1][5])) : 0;
    const hop = Math.abs(Math.sin(hopP * Math.PI * (o.leg === 0 ? 4 : 2))) * 0.55;
    const a = 0.16, enter = ease.out(seg(t, 2.6, 3.6));
    bear.position.set(lerp(-1.8, -0.72, enter), R * Math.cos(a) + hop - 0.05, R * Math.sin(a) + 0.15);
    bear.rotation.z = o.moving ? Math.sin(tq * 9) * 0.12 : 0; bear.visible = t > 2.5;
    bear.scale.setScalar(t < 2.6 ? 0.001 : clamp(ease.spring(seg(tq, 2.6, 3.1))));
    { const flap = 0.55 + 0.45 * Math.abs(Math.sin(tq * 14)); bfly.position.set(0.7 + Math.sin(t * 1.7) * 0.5, R + 1.25 + Math.sin(t * 2.3) * 0.25, 0.9); bfly.scale.set(flap, 1, 1); bfly.visible = t > 3.2; }
    clouds.forEach((m, i) => { m.position.x = -9 + i * 3.6 + Math.sin(t * 0.2 + i) * 0.6; });
  }

  // camera: close on Oxford, pull back to reveal the planet, ride the top of the world, pull right back after Seoul, then dive in
  function cam(t) {
    const CLOSE = { pos: [0.2, R + 1.4, 4.2], look: [0, R + 0.7, 0] };
    const RIDE = { pos: [0, R + 2.6, 7.4], look: [0, R + 0.2, 0] };
    const FAR = { pos: [0, 3.0, 22], look: [0, 0.6, 0] };
    const DIVE = { pos: [0, R + 0.9, 2.2], look: [0, R + 0.6, 0] };
    const k = [[0, CLOSE], [2.6, CLOSE], [4.6, FAR], [5.6, FAR], [7.0, RIDE], [19.4, RIDE], [21.4, FAR], [22.0, FAR], [23.0, DIVE]];
    const pos = keys(t, k.map(([a, v]) => [a, v.pos])), look = keys(t, k.map(([a, v]) => [a, v.look]));
    const tq = q12(t); return { pos: [pos[0] + wobble(tq * 2, 1) * 0.04, pos[1] + wobble(tq * 2.2, 2) * 0.04, pos[2]], look, fov: 40 };
  }
  return { scene, update, cam };
}
