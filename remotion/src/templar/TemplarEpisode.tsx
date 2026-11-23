// Knights Templar channel — faceless Bible-reading episode (1920x1080).
// Not Bear & Joy: no Bear & Joy brand, colours or assets here.
import React, {useEffect, useState} from 'react';
import {noise2D} from '@remotion/noise';
import {
  AbsoluteFill, Audio, Easing, Sequence, continueRender, delayRender, interpolate,
  random, staticFile, useCurrentFrame, useVideoConfig,
} from 'remotion';

// ---------- plan types ----------
export type Tok = {t: string; s?: number | null; e?: number | null};
export type Para = {verse?: number | null; dropcap?: boolean; label?: string; center?: boolean; tokens: Tok[]};
export type Spread = {from: number; to: number; header?: string; left: Para[]; right: Para[]};
export type Chunk = {from: number; to: number; tokens: Tok[]};
export type NoteItem = {at: number; head: string; body?: string};
export type Scene =
  | {type: 'title'; from: number; to: number; kicker: string; title: string; sub: string}
  | {type: 'speech'; from: number; to: number; chunks: Chunk[]}
  | {type: 'prayer'; from: number; to: number; heading: string; kneelFrom: number; kneelTo: number; kneelText?: string; kneelSub?: string;
     blocks: {style: 'latin' | 'english' | 'say' | 'prayer'; tokens: Tok[]}[]}
  | {type: 'bible'; from: number; to: number; spreads: Spread[]}
  | {type: 'notes'; from: number; to: number; label: string; title: string; items: NoteItem[]; chunks: Chunk[]}
  | {type: 'end'; from: number; to: number; next: string; sign: string; chunks?: Chunk[]};
export type TemplarPlan = {fps: number; duration: number; audio?: string | null; music?: string | null;
  musicVolume?: number; scenes: Scene[]};

// ---------- palette ----------
const C = {
  night: '#040302', stone: '#0b0806', gold: '#b8893f', goldHi: '#ffb54a', red: '#7d1612', ember: '#ff8a2a',
  ivory: '#e6d6b8', dimIvory: 'rgba(230,214,184,.22)', ink: '#1a0f07', parch: '#b99868',
};
const SERIF = "'EB Garamond', Georgia, serif";
const CAPS = "'Cinzel', 'EB Garamond', serif";
const FRAK = "'UnifrakturMaguntia', 'Cinzel', serif";

const FONTS: [string, string, string, string][] = [
  ['Cinzel', 'normal', '400', 'Cinzel-400.woff2'], ['Cinzel', 'normal', '600', 'Cinzel-600.woff2'],
  ['Cinzel', 'normal', '700', 'Cinzel-700.woff2'], ['EB Garamond', 'normal', '400', 'EBGaramond-400.woff2'],
  ['EB Garamond', 'normal', '500', 'EBGaramond-500.woff2'], ['EB Garamond', 'normal', '600', 'EBGaramond-600.woff2'],
  ['EB Garamond', 'italic', '400', 'EBGaramond-400i.woff2'], ['EB Garamond', 'italic', '500', 'EBGaramond-500i.woff2'],
  ['UnifrakturMaguntia', 'normal', '400', 'UnifrakturMaguntia-400.woff2'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('templar-fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([f, s, w, file]) => new FontFace(f, `url(${staticFile('templar/fonts/' + file)})`, {style: s, weight: w}).load()
      .then((ff) => (document.fonts as any).add(ff)))).then(() => continueRender(h)).catch(() => continueRender(h));
  }, [h]);
};

const ease = Easing.bezier(0.33, 0, 0.2, 1);
export const fire = (t: number) => {
  const n = 0.55 * noise2D('fire', t * 1.7, 0) + 0.3 * noise2D('fire2', t * 5.3, 1) + 0.15 * noise2D('fire3', t * 11, 2);
  return 0.78 + 0.22 * n;   // ~0.56–1.0
};
// film grain: SVG turbulence re-seeded every frame
const Grain: React.FC<{t: number; o?: number}> = ({t, o = 0.16}) => {
  const seed = Math.floor(t * 24) % 97;
  return (
    <AbsoluteFill style={{opacity: o, mixBlendMode: 'overlay', pointerEvents: 'none'}}>
      <svg width="1920" height="1080"><filter id={`g${seed}`}><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves={2} seed={seed} stitchTiles="stitch" />
        <feColorMatrix type="saturate" values="0" /></filter><rect width="1920" height="1080" filter={`url(#g${seed})`} /></svg>
    </AbsoluteFill>
  );
};
const fade = (t: number, a: number, b: number, inD = 0.8, outD = 0.8) =>
  Math.min(interpolate(t, [a, a + inD], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease}),
    interpolate(t, [b - outD, b], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease}));

// ---------- the cross (simple cross pattée) ----------
export const Cross: React.FC<{size: number; color?: string; glow?: number}> = ({size, color = C.red, glow = 0}) => (
  <svg width={size} height={size} viewBox="-50 -50 100 100" style={{filter: glow ? `drop-shadow(0 0 ${glow}px rgba(255,120,30,.5))` : undefined}}>
    <filter id="worn" x="-20%" y="-20%" width="140%" height="140%">
      <feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves={3} seed={3} result="n" />
      <feDisplacementMap in="SourceGraphic" in2="n" scale={3.2} result="d" />
      <feTurbulence type="fractalNoise" baseFrequency="0.6" numOctaves={2} seed={9} result="s" />
      <feColorMatrix in="s" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.5 1.45" result="m" />
      <feComposite in="d" in2="m" operator="in" />
    </filter>
    <g filter="url(#worn)">
      {[0, 90, 180, 270].map((r) => (
        <path key={r} transform={`rotate(${r})`} d="M -7 -4 L -20 -46 Q 0 -40 20 -46 L 7 -4 Z" fill={color} />
      ))}
      <rect x={-8} y={-8} width={16} height={16} fill={color} transform="rotate(45)" />
    </g>
  </svg>
);

// ---------- background: night camp, firelight from below, sparks, smoke ----------
const Backdrop: React.FC<{t: number; warm?: number}> = ({t, warm = 1}) => {
  const f = fire(t) * warm;
  const sparks = Array.from({length: 70}, (_, i) => {
    const sp = 60 + random(`s${i}`) * 120;            // px per second, fast like sparks
    const life = 900 / sp + 1.5;
    const ph = ((t + random(`p${i}`) * life) % life) / life;
    const x0 = 760 + random(`x${i}`) * 400;
    const x = x0 + (random(`d${i}`) - 0.5) * 500 * ph + noise2D(`w${i}`, t * 0.8, i) * 60 * ph;
    const y = 1110 - ph * 1000;
    const o = (1 - ph) ** 1.5 * (0.5 + random(`o${i}`) * 0.5);
    const r = 0.8 + random(`r${i}`) * 1.8;
    return <div key={i} style={{position: 'absolute', left: x, top: y, width: r * 2, height: r * 2 + 3 * ph, borderRadius: '50%',
      background: '#ffd08a', opacity: o * warm, boxShadow: `0 0 ${r * 6}px #ff6a12`}} />;
  });
  const smokeX = noise2D('smx', t * 0.05, 0) * 120;
  return (
    <AbsoluteFill style={{background: C.night}}>
      <AbsoluteFill style={{background: `radial-gradient(ellipse 95% 80% at 50% 122%, rgba(255,120,30,${0.85 * f}) 0%, rgba(190,60,12,${0.55 * f}) 26%, rgba(70,22,6,${0.55 * f}) 52%, ${C.night} 84%)`}} />
      <AbsoluteFill style={{background: `radial-gradient(ellipse 30% 18% at ${50 + 4 * noise2D('fx', t * 0.9, 0)}% 104%, rgba(255,190,90,${0.55 * f * f}), rgba(255,120,30,0) 100%)`}} />
      <AbsoluteFill style={{opacity: 0.22, transform: `translateX(${smokeX}px)`, background:
        `radial-gradient(ellipse 40% 30% at ${40 + 10 * noise2D('a', t * 0.04, 1)}% ${45 + 8 * noise2D('b', t * 0.03, 2)}%, rgba(120,95,80,.35), transparent 70%),
         radial-gradient(ellipse 35% 25% at ${62 + 10 * noise2D('c', t * 0.035, 3)}% ${30 + 8 * noise2D('d', t * 0.05, 4)}%, rgba(110,90,75,.3), transparent 70%)`}} />
      {sparks}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 75% 85% at 50% 72%, transparent 35%, rgba(0,0,0,.85) 100%)'}} />
    </AbsoluteFill>
  );
};

// ---------- spoken-word text ----------
type WordStyle = 'dark' | 'light';
const Word: React.FC<{tok: Tok; t: number; mode: WordStyle; lead?: number}> = ({tok, t, mode, lead = 0.05}) => {
  const s = tok.s ?? null, e = tok.e ?? null;
  let state: 'future' | 'now' | 'past' = 'past';
  if (s != null && e != null) state = t < s - lead ? 'future' : t <= Math.max(e, s + 0.18) ? 'now' : 'past';
  const glowIn = s != null ? interpolate(t, [s - lead - 0.06, s - lead], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
  const after = e != null ? interpolate(t, [e, e + 0.35], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
  const hl = state === 'now' ? glowIn : state === 'past' ? after : 0;
  const colorFuture = mode === 'dark' ? 'rgba(26,15,7,.42)' : C.dimIvory;
  const colorPast = mode === 'dark' ? C.ink : C.ivory;
  const color = state === 'future' ? colorFuture : colorPast;
  return (
    <span style={{position: 'relative', color, whiteSpace: 'pre-wrap'}}>
      {hl > 0 ? (
        <span style={{position: 'absolute', left: '-0.12em', right: '-0.12em', top: '0.08em', bottom: '0.02em', borderRadius: '0.18em', opacity: hl,
          background: mode === 'dark' ? 'radial-gradient(ellipse 70% 75% at 50% 58%, rgba(255,150,40,.75), rgba(230,90,20,.35) 60%, rgba(230,90,20,0) 100%)'
            : 'radial-gradient(ellipse at 50% 60%, rgba(255,140,40,.32), rgba(255,140,40,0) 70%)', filter: 'blur(1px)'}} />
      ) : null}
      <span style={{position: 'relative', textShadow: hl > 0 ? (mode === 'light' ? `0 0 ${20 * hl}px rgba(255,130,30,${0.95 * hl})` : `0 0 ${8 * hl}px rgba(255,200,120,${0.8 * hl})`) : undefined,
        color: mode === 'light' && hl > 0.5 ? C.goldHi : undefined}}>{tok.t}</span>
    </span>
  );
};
const Words: React.FC<{tokens: Tok[]; t: number; mode: WordStyle}> = ({tokens, t, mode}) => (
  <>{tokens.map((k, i) => <React.Fragment key={i}><Word tok={k} t={t} mode={mode} />{i < tokens.length - 1 ? ' ' : ''}</React.Fragment>)}</>
);

// ---------- scenes ----------
const TitleScene: React.FC<{s: Extract<Scene, {type: 'title'}>; t: number}> = ({s, t}) => {
  const o = fade(t, s.from, s.to, 1.4, 1.2);
  const cross = interpolate(t, [s.from + 0.3, s.from + 2.4], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: o, flexDirection: 'column'}}>
      <div style={{opacity: cross, transform: `scale(${0.9 + 0.1 * cross})`}}><Cross size={150} glow={22} /></div>
      <div style={{fontFamily: CAPS, color: C.gold, letterSpacing: '0.42em', fontSize: 26, marginTop: 46, opacity: fade(t, s.from + 1.2, s.to, 1, 1)}}>{s.kicker}</div>
      <div style={{fontFamily: CAPS, color: C.ivory, fontSize: 92, fontWeight: 600, marginTop: 18, letterSpacing: '0.06em',
        textShadow: '0 0 40px rgba(255,120,30,.35), 0 4px 0 rgba(0,0,0,.6)', opacity: fade(t, s.from + 1.8, s.to, 1.2, 1)}}>{s.title}</div>
      <div style={{width: 420, height: 1, background: `linear-gradient(90deg, transparent, ${C.gold}, transparent)`, margin: '28px 0', opacity: fade(t, s.from + 2.2, s.to, 1, 1)}} />
      <div style={{fontFamily: SERIF, fontStyle: 'italic', color: C.ivory, opacity: 0.8 * fade(t, s.from + 2.5, s.to, 1, 1), fontSize: 38}}>{s.sub}</div>
    </AbsoluteFill>
  );
};

const activeChunk = (chunks: Chunk[], t: number) => chunks.find((c) => t >= c.from && t < c.to);

const SpeechScene: React.FC<{s: Extract<Scene, {type: 'speech'}>; t: number}> = ({s, t}) => {
  const c = activeChunk(s.chunks, t);
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: fade(t, s.from, s.to, 0.8, 0.8)}}>
      <div style={{position: 'absolute', opacity: 0.07}}><Cross size={760} color={C.gold} /></div>
      {c ? (
        <div style={{width: 1440, textAlign: 'center', fontFamily: SERIF, fontSize: 64, lineHeight: 1.32, opacity: fade(t, c.from, c.to, 0.35, 0.35),
          transform: `translateY(${interpolate(t, [c.from, c.from + 0.5], [14, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease})}px)`}}>
          <Words tokens={c.tokens} t={t} mode="light" />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const PrayerScene: React.FC<{s: Extract<Scene, {type: 'prayer'}>; t: number}> = ({s, t}) => {
  const kneel = fade(t, s.kneelFrom, s.kneelTo, 1.0, 1.2);
  const body = interpolate(t, [s.kneelFrom + 0.6, s.kneelFrom + 2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{opacity: fade(t, s.from, s.to, 1, 1.2), alignItems: 'center', justifyContent: 'center', flexDirection: 'column'}}>
      <div style={{position: 'absolute', top: 86, display: 'flex', alignItems: 'center', gap: 22}}>
        <Cross size={34} /><span style={{fontFamily: CAPS, color: C.gold, letterSpacing: '0.5em', fontSize: 24}}>{s.heading}</span><Cross size={34} />
      </div>
      <div style={{position: 'absolute', top: 170, opacity: kneel, textAlign: 'center', transform: `translateY(${(1 - kneel) * 10}px)`}}>
        <div style={{fontFamily: CAPS, color: C.ivory, fontSize: 40, letterSpacing: '0.18em'}}>{s.kneelText ?? 'Brothers, take a knee'}</div>
        <div style={{fontFamily: SERIF, fontStyle: 'italic', color: C.ivory, opacity: 0.65, fontSize: 28, marginTop: 8}}>{s.kneelSub ?? 'Bow your head and pray with me'}</div>
      </div>
      <div style={{width: 1500, marginTop: 120, textAlign: 'center', opacity: Math.max(body, 0.0)}}>
        {s.blocks.map((b, i) => {
          const st: React.CSSProperties = b.style === 'latin'
            ? {fontFamily: CAPS, fontSize: 50, letterSpacing: '0.04em', lineHeight: 1.35, marginBottom: 14}
            : b.style === 'english' ? {fontFamily: SERIF, fontStyle: 'italic', fontSize: 40, lineHeight: 1.35, marginBottom: 40, opacity: 0.92}
            : b.style === 'say' ? {fontFamily: SERIF, fontSize: 34, lineHeight: 1.4, marginBottom: 26, opacity: 0.85}
            : {fontFamily: SERIF, fontSize: 42, lineHeight: 1.42, marginBottom: 10};
          return <div key={i} style={st}><Words tokens={b.tokens} t={t} mode="light" /></div>;
        })}
      </div>
    </AbsoluteFill>
  );
};

// open Bible: two parchment pages, verses with red verse numbers, spoken word highlighted
const Page: React.FC<{paras: Para[]; t: number; side: 'l' | 'r'}> = ({paras, t, side}) => (
  <div style={{position: 'absolute', top: 0, bottom: 0, [side === 'l' ? 'left' : 'right']: 0, width: '50%',
    padding: side === 'l' ? '70px 70px 60px 92px' : '70px 92px 60px 70px', boxSizing: 'border-box',
    fontFamily: SERIF, fontSize: 40, lineHeight: 1.4, color: C.ink, textAlign: 'justify', hyphens: 'manual'} as React.CSSProperties}>
    {paras.map((p, i) => (
      <div key={i} style={{marginBottom: p.label ? 0 : 6}}>
        {p.label ? <div style={{fontFamily: CAPS, fontSize: 30, letterSpacing: '0.24em', textAlign: 'center', color: C.red, margin: '0 0 18px'}}>{p.label}</div> : null}
        {p.center ? (
          <div style={{textAlign: 'center', fontStyle: 'italic', fontSize: 36, marginTop: 30, color: C.red}}>
            <div style={{width: 120, height: 1, background: 'rgba(158,27,27,.5)', margin: '0 auto 18px'}} />
            <Words tokens={p.tokens} t={t} mode="dark" />
          </div>
        ) : p.dropcap && p.tokens.length ? (
          <span>
            <span style={{float: 'left', fontFamily: CAPS, fontWeight: 700, fontSize: 112, lineHeight: 0.84, color: C.red, margin: '8px 14px 0 0', textShadow: '0 1px 0 rgba(201,162,74,.6)'}}>{p.tokens[0].t[0]}</span>
            <Word tok={{...p.tokens[0], t: p.tokens[0].t.slice(1)}} t={t} mode="dark" />{' '}
            <Words tokens={p.tokens.slice(1)} t={t} mode="dark" />
          </span>
        ) : (
          <span>
            {p.verse ? <sup style={{color: C.red, fontSize: 23, fontWeight: 600, marginRight: 6, fontFamily: SERIF}}>{p.verse}</sup> : null}
            <Words tokens={p.tokens} t={t} mode="dark" />
          </span>
        )}
      </div>
    ))}
  </div>
);

const PaperTexture: React.FC = () => (
  <AbsoluteFill style={{mixBlendMode: 'multiply', opacity: 0.55}}>
    <svg width="100%" height="100%"><filter id="paper"><feTurbulence type="fractalNoise" baseFrequency="0.012 0.02" numOctaves={5} seed={4} />
      <feColorMatrix values="0 0 0 0 0.55  0 0 0 0 0.40  0 0 0 0 0.24  0 0 0 1.1 -0.25" /></filter>
      <rect width="100%" height="100%" filter="url(#paper)" /></svg>
  </AbsoluteFill>
);
const FIBRE = (
  <AbsoluteFill style={{mixBlendMode: 'multiply', opacity: 0.35}}>
    <svg width="100%" height="100%"><filter id="fibre"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={11} />
      <feColorMatrix values="0 0 0 0 0.4  0 0 0 0 0.3  0 0 0 0 0.2  0 0 0 0.9 -0.2" /></filter>
      <rect width="100%" height="100%" filter="url(#fibre)" /></svg>
  </AbsoluteFill>
);

const BibleScene: React.FC<{s: Extract<Scene, {type: 'bible'}>; t: number}> = ({s, t}) => {
  const o = fade(t, s.from, s.to, 1.2, 1.2);
  const k = interpolate(t, [s.from, s.to], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sp = s.spreads.find((x) => t >= x.from && t < x.to) ?? s.spreads[s.spreads.length - 1];
  const turn = fade(t, sp.from, sp.to, 0.5, 0.5);
  const f = fire(t);
  const lx = 30 + 6 * noise2D('lx', t * 0.6, 0);      // the fire's light wanders a little
  return (
    <AbsoluteFill style={{opacity: o, alignItems: 'center', justifyContent: 'center', perspective: 2400}}>
      <div style={{position: 'relative', width: 1720, height: 1000, marginTop: 30,
        transform: `rotateX(9deg) scale(${0.9 + 0.03 * k}) translateY(${noise2D('cam', t * 0.15, 0) * 4}px)`}}>
        {/* battered leather cover + page block */}
        <div style={{position: 'absolute', inset: '10px -16px -26px -16px', borderRadius: 18, background: 'linear-gradient(160deg, #2b120b, #120604 60%, #1d0a06)',
          boxShadow: '0 50px 120px rgba(0,0,0,.95), inset 0 0 30px rgba(0,0,0,.9)'}} />
        <div style={{position: 'absolute', inset: '4px 0 -10px 0', borderRadius: 8, background: 'repeating-linear-gradient(0deg, #8d7148 0 2px, #5e4527 2px 3px)'}} />
        {/* pages */}
        <div style={{position: 'absolute', inset: 0, borderRadius: 6, overflow: 'hidden',
          background: `linear-gradient(90deg, #6e5230 0%, ${C.parch} 6%, #c7a878 38%, #9c7b4c 48.6%, #3d2814 50%, #9c7b4c 51.4%, #c7a878 62%, ${C.parch} 94%, #6e5230 100%)`}}>
          <PaperTexture />
          {FIBRE}
          {/* stains and scorch marks */}
          <AbsoluteFill style={{mixBlendMode: 'multiply', opacity: 0.5, background:
            `radial-gradient(circle at 12% 88%, #5a3a1a 0, transparent 14%), radial-gradient(circle at 86% 9%, #4a2c12 0, transparent 11%),
             radial-gradient(ellipse 9% 6% at 72% 80%, #7a5530 0, transparent 100%), radial-gradient(circle at 33% 18%, #8a6438 0, transparent 9%)`}} />
          <div style={{position: 'absolute', top: 26, left: 92, right: 92, display: 'flex', justifyContent: 'space-between', fontFamily: CAPS, fontSize: 20, letterSpacing: '0.3em', color: 'rgba(110,24,16,.8)'}}>
            <span>{sp.header ?? 'GENESIS'}</span><span>{sp.header ?? 'GENESIS'}</span>
          </div>
          <div style={{position: 'absolute', inset: 0, opacity: turn}}>
            <Page paras={sp.left} t={t} side="l" />
            <Page paras={sp.right} t={t} side="r" />
          </div>
          {/* firelight from below-left, darkness above */}
          <AbsoluteFill style={{mixBlendMode: 'soft-light', background: `radial-gradient(ellipse 90% 110% at ${lx}% 120%, rgba(255,150,50,${0.95 * f}), rgba(255,110,30,${0.4 * f}) 45%, rgba(0,0,0,0) 80%)`}} />
          <AbsoluteFill style={{mixBlendMode: 'multiply', background: `linear-gradient(180deg, rgba(40,20,8,${0.48 - 0.12 * f}) 0%, rgba(60,30,10,.12) 40%, rgba(0,0,0,0) 60%, rgba(30,12,4,.25) 100%)`}} />
          <AbsoluteFill style={{boxShadow: 'inset 0 0 90px 18px rgba(30,12,3,.85), inset 0 0 14px 4px rgba(10,4,0,.9)'}} />
        </div>
        {/* ribbon */}
        <div style={{position: 'absolute', left: 1180, top: 985, width: 26, height: 110, background: `linear-gradient(${C.red}, #3e0907)`, clipPath: 'polygon(0 0,100% 0,100% 100%,50% 86%,0 100%)'}} />
      </div>
      <AbsoluteFill style={{background: `radial-gradient(ellipse 80% 80% at ${lx + 15}% 75%, transparent 45%, rgba(0,0,0,${0.9 - 0.15 * f}) 100%)`}} />
    </AbsoluteFill>
  );
};

const NotesScene: React.FC<{s: Extract<Scene, {type: 'notes'}>; t: number}> = ({s, t}) => {
  const c = activeChunk(s.chunks, t);
  const shown = s.items.filter((it) => t >= it.at);
  return (
    <AbsoluteFill style={{opacity: fade(t, s.from, s.to, 1, 1)}}>
      <div style={{position: 'absolute', top: 90, left: 0, right: 0, textAlign: 'center'}}>
        <div style={{fontFamily: CAPS, color: C.gold, letterSpacing: '0.5em', fontSize: 22}}>{s.label}</div>
        <div style={{fontFamily: CAPS, color: C.ivory, fontSize: 58, marginTop: 14, letterSpacing: '0.05em'}}>{s.title}</div>
        <div style={{width: 360, height: 1, margin: '22px auto 0', background: `linear-gradient(90deg, transparent, ${C.gold}, transparent)`}} />
      </div>
      <div style={{position: 'absolute', top: 300, left: 260, right: 260}}>
        {shown.map((it, i) => {
          const a = interpolate(t, [it.at, it.at + 0.9], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
          const latest = i === shown.length - 1;
          return (
            <div key={i} style={{display: 'flex', gap: 30, alignItems: 'flex-start', marginBottom: 34, opacity: a * (latest ? 1 : 0.55),
              transform: `translateX(${(1 - a) * -24}px)`}}>
              <div style={{marginTop: 10}}><Cross size={36} glow={latest ? 10 : 0} /></div>
              <div>
                <div style={{fontFamily: CAPS, fontSize: 44, color: latest ? C.goldHi : C.ivory, letterSpacing: '0.03em'}}>{it.head}</div>
                {it.body ? <div style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: 34, color: C.ivory, opacity: 0.85, marginTop: 6, lineHeight: 1.3}}>{it.body}</div> : null}
              </div>
            </div>
          );
        })}
      </div>
      {c ? (
        <div style={{position: 'absolute', bottom: 70, left: 220, right: 220, textAlign: 'center', fontFamily: SERIF, fontSize: 36, lineHeight: 1.3,
          opacity: fade(t, c.from, c.to, 0.3, 0.3)}}>
          <Words tokens={c.tokens} t={t} mode="light" />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const EndScene: React.FC<{s: Extract<Scene, {type: 'end'}>; t: number}> = ({s, t}) => (
  <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', flexDirection: 'column', opacity: fade(t, s.from, s.to, 1.2, 1.5)}}>
    <Cross size={110} glow={18} />
    <div style={{fontFamily: CAPS, color: C.gold, letterSpacing: '0.42em', fontSize: 24, marginTop: 44}}>NEXT TIME</div>
    <div style={{fontFamily: CAPS, color: C.ivory, fontSize: 60, marginTop: 14}}>{s.next}</div>
    <div style={{fontFamily: SERIF, fontStyle: 'italic', color: C.ivory, opacity: 0.85, fontSize: 44, marginTop: 50}}>{s.sign}</div>
    {(() => {
      const c = s.chunks ? activeChunk(s.chunks, t) : undefined;
      return c ? <div style={{position: 'absolute', bottom: 70, left: 220, right: 220, textAlign: 'center', fontFamily: SERIF, fontSize: 36,
        opacity: fade(t, c.from, c.to, 0.3, 0.3)}}><Words tokens={c.tokens} t={t} mode="light" /></div> : null;
    })()}
  </AbsoluteFill>
);

export const TemplarEpisode: React.FC<{plan: TemplarPlan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const visible = plan.scenes.filter((s) => t >= s.from - 0.01 && t < s.to + 0.01);
  const warm = visible.some((s) => s.type === 'bible') ? 0.7 : 1;
  return (
    <AbsoluteFill style={{background: C.night}}>
      <Backdrop t={t} warm={warm} />
      {visible.map((s, i) => {
        switch (s.type) {
          case 'title': return <TitleScene key={i} s={s} t={t} />;
          case 'speech': return <SpeechScene key={i} s={s} t={t} />;
          case 'prayer': return <PrayerScene key={i} s={s} t={t} />;
          case 'bible': return <BibleScene key={i} s={s} t={t} />;
          case 'notes': return <NotesScene key={i} s={s} t={t} />;
          case 'end': return <EndScene key={i} s={s} t={t} />;
        }
      })}
      <Grain t={t} />
      {plan.audio ? <Audio src={staticFile(plan.audio)} /> : null}
      {plan.music ? <Audio src={staticFile(plan.music)} volume={plan.musicVolume ?? 0.12} /> : null}
    </AbsoluteFill>
  );
};
