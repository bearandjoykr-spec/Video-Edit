// Antique paintings layer for the Templar channel: Ken Burns movement, sepia/firelit grade,
// film dust + scratches + gate weave, and "burn-in" transitions (ragged, ember-edged dissolve).
import React from 'react';
import {AbsoluteFill, Easing, interpolate, random, staticFile} from 'remotion';
import {noise2D} from '@remotion/noise';

export type ArtCue = {src: string; from: number; to: number; focus: [number, number]; zoom: [number, number]; w: number; h: number};

const W = 1920, H = 1080;
const BURN = 1.8;   // seconds for a painting to burn in over the previous one
const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
const smooth = (x: number) => x * x * (3 - 2 * x);

// SVG table for feFuncA: noise value -> alpha, a soft step at threshold thr (reveal) or a band (ember edge)
const table = (fn: (v: number) => number, n = 48) => Array.from({length: n + 1}, (_, i) => fn(i / n).toFixed(3)).join(' ');

const Painting: React.FC<{c: ArtCue; t: number; fire: number; id: string; dim: number}> = ({c, t, fire, id, dim}) => {
  const k = clamp01((t - c.from) / Math.max(1, c.to - c.from));
  const z = c.zoom[0] + (c.zoom[1] - c.zoom[0]) * Easing.inOut(Easing.sin)(k);
  // cover the frame, then Ken Burns around the focus point (kept inside the picture)
  const s0 = Math.max(W / c.w, H / c.h) * z;
  const dw = c.w * s0, dh = c.h * s0;
  const x = Math.min(0, Math.max(W - dw, W / 2 - c.focus[0] * dw));
  const y = Math.min(0, Math.max(H - dh, H / 2 - c.focus[1] * dh));
  const p = clamp01((t - c.from) / BURN);           // burn-in progress
  const burning = p < 1;
  const thr = 0.86 - 0.78 * smooth(p);              // noise threshold sweeps down: more of the picture shows
  const reveal = table((v) => clamp01((v - thr) / 0.035));
  const ember = table((v) => Math.exp(-(((v - thr + 0.02) / 0.022) ** 2)));
  const seed = Math.floor(random(c.src) * 90);
  const b = (0.5 + 0.22 * fire) * dim;
  return (
    <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
      {burning ? (
        <defs>
          <filter id={`n${id}`} x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
            <feTurbulence type="fractalNoise" baseFrequency="0.0045 0.006" numOctaves={5} seed={seed} />
            <feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  1.6 0 0 0 -0.3" />
            <feComponentTransfer><feFuncA type="table" tableValues={reveal} /></feComponentTransfer>
          </filter>
          <filter id={`e${id}`} x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
            <feTurbulence type="fractalNoise" baseFrequency="0.0045 0.006" numOctaves={5} seed={seed} />
            <feColorMatrix values="0 0 0 0 1  0 0 0 0 0.45  0 0 0 0 0.08  1.6 0 0 0 -0.3" />
            <feComponentTransfer><feFuncA type="table" tableValues={ember} /></feComponentTransfer>
            <feGaussianBlur stdDeviation="1.2" />
          </filter>
          <mask id={`m${id}`}><rect width={W} height={H} fill="white" filter={`url(#n${id})`} /></mask>
        </defs>
      ) : null}
      <g mask={burning ? `url(#m${id})` : undefined}>
        <image href={staticFile(c.src)} x={x} y={y} width={dw} height={dh} preserveAspectRatio="none"
          style={{filter: `sepia(0.7) grayscale(0.15) contrast(1.22) brightness(${b.toFixed(3)})`}} />
      </g>
      {burning ? <rect width={W} height={H} filter={`url(#e${id})`} opacity={0.95 * (1 - smooth(clamp01((p - 0.75) / 0.25)))}
        style={{mixBlendMode: 'screen'}} /> : null}
    </svg>
  );
};

// old film: dust specks, the odd scratch, slight gate weave
const FilmWear: React.FC<{t: number}> = ({t}) => {
  const fr = Math.floor(t * 24);
  const specks = Array.from({length: 9}, (_, i) => {
    const on = random(`sp${fr}-${i}`) < 0.55;
    if (!on) return null;
    const r = 0.8 + random(`sr${fr}-${i}`) * 2.6;
    return <div key={i} style={{position: 'absolute', left: random(`sx${fr}-${i}`) * W, top: random(`sy${fr}-${i}`) * H, width: r * 2, height: r * (1 + random(`sh${fr}-${i}`) * 2),
      borderRadius: '50%', background: random(`sc${fr}-${i}`) < 0.5 ? 'rgba(20,12,6,.55)' : 'rgba(240,225,190,.35)'}} />;
  });
  const sc = Math.floor(t * 3);
  const scratch = random(`scr${sc}`) < 0.35
    ? <div style={{position: 'absolute', top: 0, bottom: 0, left: random(`scx${sc}`) * W + noise2D('sw', t * 4, 0) * 6, width: 1.2, background: 'rgba(235,220,190,.18)'}} /> : null;
  return <AbsoluteFill style={{pointerEvents: 'none'}}>{specks}{scratch}</AbsoluteFill>;
};

export const ArtLayer: React.FC<{cues: ArtCue[]; t: number; fire: number; opacity: number; dim?: number; vignette?: number}> = ({cues, t, fire, opacity, dim = 1, vignette = 0.88}) => {
  if (opacity <= 0.001) return null;
  const vis = cues.map((c, i) => ({c, i})).filter(({c}) => t >= c.from && t < c.to);
  if (!vis.length) return null;
  const weave = {x: noise2D('gwx', t * 7, 0) * 1.4, y: noise2D('gwy', t * 6, 1) * 1.8};
  return (
    <AbsoluteFill style={{opacity, transform: `translate(${weave.x}px, ${weave.y}px) scale(1.004)`}}>
      {vis.map(({c, i}) => <Painting key={c.src + i} c={c} t={t} fire={fire} id={`a${i}`} dim={dim} />)}
      <FilmWear t={t} />
      {/* warm firelight from below + heavy vignette so text and the book stay readable */}
      <AbsoluteFill style={{background: `radial-gradient(ellipse 90% 70% at 50% 115%, rgba(255,120,30,${0.22 * fire}), transparent 70%)`, mixBlendMode: 'screen'}} />
      <AbsoluteFill style={{background: `radial-gradient(ellipse 72% 72% at 50% 50%, rgba(0,0,0,${0.15 * vignette / 0.88}) 30%, rgba(0,0,0,${vignette}) 100%)`}} />
    </AbsoluteFill>
  );
};

// how strongly paintings show behind each kind of scene
export const ART_LEVEL: Record<string, number> = {speech: 0.66, notes: 0.5, prayer: 0.4, end: 0.45};
export {BURN};
export const pullAmount = (t: number, breaks: {at: number; until: number}[] | undefined) => {
  if (!breaks) return 0;
  let m = 0;
  for (const b of breaks) {
    const len = b.until - b.at;
    if (len < 0.5) continue;
    const depth = Math.min(1, len / 2.2);
    const a = interpolate(t, [b.at, b.at + Math.min(0.9, len / 2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    const o = interpolate(t, [b.until - Math.min(0.8, len / 2), b.until], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    m = Math.max(m, depth * smooth(Math.min(a, o)));
  }
  return m;
};
