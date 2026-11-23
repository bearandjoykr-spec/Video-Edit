// Knights Templar channel — faceless Bible-reading episode (1920x1080).
// Not Bear & Joy: no Bear & Joy brand, colours or assets here.
import React, {useEffect, useState} from 'react';
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
  night: '#07060a', stone: '#14110f', gold: '#c9a24a', goldHi: '#f1d48a', red: '#9e1b1b',
  ivory: '#efe4cc', dimIvory: 'rgba(239,228,204,.28)', ink: '#2a1b10', parch: '#e8d7b0',
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
const fade = (t: number, a: number, b: number, inD = 0.8, outD = 0.8) =>
  Math.min(interpolate(t, [a, a + inD], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease}),
    interpolate(t, [b - outD, b], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease}));

// ---------- the cross (simple cross pattée) ----------
export const Cross: React.FC<{size: number; color?: string; glow?: number}> = ({size, color = C.red, glow = 0}) => (
  <svg width={size} height={size} viewBox="-50 -50 100 100" style={{filter: glow ? `drop-shadow(0 0 ${glow}px rgba(201,162,74,.55))` : undefined}}>
    {[0, 90, 180, 270].map((r) => (
      <path key={r} transform={`rotate(${r})`} d="M -7 -4 L -20 -46 Q 0 -40 20 -46 L 7 -4 Z" fill={color} />
    ))}
    <rect x={-8} y={-8} width={16} height={16} fill={color} transform="rotate(45)" />
  </svg>
);

// ---------- background: dark stone, candlelight, embers ----------
const Backdrop: React.FC<{t: number; warm?: number}> = ({t, warm = 1}) => {
  const flick = 0.92 + 0.05 * Math.sin(t * 7.3) + 0.03 * Math.sin(t * 13.1 + 1.2);
  const embers = Array.from({length: 26}, (_, i) => {
    const sp = 14 + random(`s${i}`) * 22;
    const life = 1080 / sp + 4;
    const ph = ((t + random(`p${i}`) * life) % life) / life;
    const x = random(`x${i}`) * 1920 + Math.sin(t * 0.6 + i) * 30;
    const y = 1120 - ph * 1200;
    const o = Math.sin(ph * Math.PI) * (0.25 + random(`o${i}`) * 0.45);
    const r = 1.2 + random(`r${i}`) * 2.4;
    return <div key={i} style={{position: 'absolute', left: x, top: y, width: r * 2, height: r * 2, borderRadius: '50%',
      background: '#ffb35c', opacity: o * warm, boxShadow: `0 0 ${r * 5}px #ff9a3c`}} />;
  });
  return (
    <AbsoluteFill style={{background: `radial-gradient(ellipse 70% 60% at 50% 62%, rgba(120,62,20,${0.42 * flick * warm}) 0%, rgba(40,22,12,.55) 45%, ${C.night} 100%), linear-gradient(${C.stone}, ${C.night})`}}>
      <AbsoluteFill style={{opacity: 0.07, backgroundImage:
        'repeating-linear-gradient(0deg, rgba(255,255,255,.5) 0 1px, transparent 1px 4px), repeating-linear-gradient(90deg, rgba(0,0,0,.6) 0 2px, transparent 2px 7px)'}} />
      {embers}
      <AbsoluteFill style={{boxShadow: 'inset 0 0 260px 120px rgba(0,0,0,.9)'}} />
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
  const colorFuture = mode === 'dark' ? 'rgba(42,27,16,.36)' : C.dimIvory;
  const colorPast = mode === 'dark' ? C.ink : C.ivory;
  const color = state === 'future' ? colorFuture : colorPast;
  return (
    <span style={{position: 'relative', color, whiteSpace: 'pre-wrap'}}>
      {hl > 0 ? (
        <span style={{position: 'absolute', left: '-0.12em', right: '-0.12em', top: '0.08em', bottom: '0.02em', borderRadius: '0.18em', opacity: hl,
          background: mode === 'dark' ? 'linear-gradient(180deg, rgba(240,196,90,.0) 10%, rgba(236,186,72,.62) 55%, rgba(214,150,40,.55))'
            : 'radial-gradient(ellipse at 50% 60%, rgba(241,212,138,.35), rgba(241,212,138,0) 70%)'}} />
      ) : null}
      <span style={{position: 'relative', textShadow: mode === 'light' && hl > 0 ? `0 0 ${18 * hl}px rgba(241,212,138,${0.9 * hl})` : undefined,
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
        textShadow: '0 0 40px rgba(201,162,74,.35)', opacity: fade(t, s.from + 1.8, s.to, 1.2, 1)}}>{s.title}</div>
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
    fontFamily: SERIF, fontSize: 33, lineHeight: 1.42, color: C.ink, textAlign: 'justify', hyphens: 'manual'} as React.CSSProperties}>
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
            {p.verse ? <sup style={{color: C.red, fontSize: 20, fontWeight: 600, marginRight: 6, fontFamily: SERIF}}>{p.verse}</sup> : null}
            <Words tokens={p.tokens} t={t} mode="dark" />
          </span>
        )}
      </div>
    ))}
  </div>
);

const BibleScene: React.FC<{s: Extract<Scene, {type: 'bible'}>; t: number}> = ({s, t}) => {
  const o = fade(t, s.from, s.to, 1.2, 1.2);
  const k = interpolate(t, [s.from, s.to], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sp = s.spreads.find((x) => t >= x.from && t < x.to) ?? s.spreads[s.spreads.length - 1];
  const turn = fade(t, sp.from, sp.to, 0.5, 0.5);
  const flick = 0.95 + 0.03 * Math.sin(t * 6.1) + 0.02 * Math.sin(t * 11.7);
  return (
    <AbsoluteFill style={{opacity: o, alignItems: 'center', justifyContent: 'center'}}>
      <div style={{position: 'relative', width: 1720, height: 1000, transform: `scale(${0.9 + 0.025 * k})`}}>
        {/* book block + edges */}
        <div style={{position: 'absolute', inset: '14px -8px -18px -8px', borderRadius: 14, background: 'linear-gradient(#3a1410, #1c0807)', boxShadow: '0 40px 90px rgba(0,0,0,.85)'}} />
        <div style={{position: 'absolute', inset: '4px 2px -6px 2px', borderRadius: 8, background: `repeating-linear-gradient(0deg, #d9c49a 0 2px, #b89c6a 2px 3px)`}} />
        {/* pages */}
        <div style={{position: 'absolute', inset: 0, borderRadius: 6, overflow: 'hidden',
          background: `radial-gradient(ellipse 60% 80% at 50% 50%, rgba(255,240,205,${0.25 * flick}), rgba(0,0,0,0) 70%),
            linear-gradient(90deg, #cdb58a 0%, ${C.parch} 7%, #efe0bd 40%, #c9ac7c 49.2%, #8a6a40 50%, #c9ac7c 50.8%, #efe0bd 60%, ${C.parch} 93%, #cdb58a 100%)`}}>
          <AbsoluteFill style={{opacity: 0.18, mixBlendMode: 'multiply', background:
            'radial-gradient(circle at 20% 30%, #a4793e 0, transparent 30%), radial-gradient(circle at 80% 75%, #9a6d36 0, transparent 28%), radial-gradient(circle at 65% 15%, #b0874c 0, transparent 22%)'}} />
          <div style={{position: 'absolute', top: 26, left: 92, right: 92, display: 'flex', justifyContent: 'space-between', fontFamily: CAPS, fontSize: 20, letterSpacing: '0.3em', color: 'rgba(120,30,20,.75)'}}>
            <span>{sp.header ?? 'GENESIS'}</span><span>{sp.header ?? 'GENESIS'}</span>
          </div>
          <div style={{position: 'absolute', inset: 0, opacity: turn}}>
            <Page paras={sp.left} t={t} side="l" />
            <Page paras={sp.right} t={t} side="r" />
          </div>
          <AbsoluteFill style={{boxShadow: 'inset 0 0 120px rgba(60,30,8,.55)'}} />
        </div>
        {/* ribbon */}
        <div style={{position: 'absolute', left: 1180, top: 960, width: 26, height: 120, background: `linear-gradient(${C.red}, #5e0d0d)`, clipPath: 'polygon(0 0,100% 0,100% 100%,50% 86%,0 100%)'}} />
      </div>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 75% 75% at 50% 50%, transparent 55%, rgba(0,0,0,.75) 100%)'}} />
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
  const warm = visible.some((s) => s.type === 'bible') ? 0.5 : 1;
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
      {plan.audio ? <Audio src={staticFile(plan.audio)} /> : null}
      {plan.music ? <Audio src={staticFile(plan.music)} volume={plan.musicVolume ?? 0.12} /> : null}
    </AbsoluteFill>
  );
};
