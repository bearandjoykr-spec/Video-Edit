// The Bear & Joy Co. landscape class video (YouTube / Little Steps), rebuilt from the Day 6 style.
// Rules: docs/class-video-style.md and brand/BRAND.md. All timing comes from the project's timeline.json.
import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate,
  staticFile, useCurrentFrame, useVideoConfig, Easing, random, spring,
} from 'remotion';

type Ev = {type: string; s: number; e: number; [k: string]: any};
export type ClassPlan = {
  name: string; fps: number; duration: number; frames: number; offset: number; mainEnd: number; media?: string;
  segments: {src_s: number; src_e: number; out_s: number}[];
  captions: {s: number; e: number; ko: string; hi: string; left?: number}[];
  events: Ev[]; zooms: {t: number; z: number; ox: number; oy: number}[];
};

const C = {navy: '#1E2D4D', deep: '#173B5C', ink: '#14203A', butter: '#F6F0BA', sky: '#AECCE6', white: '#FFFFFF', cream: '#F8EEDF', paper: '#FFF8EE', gray: '#BFC4CE'};
const tone = (k?: string) => (k === 'sky' ? C.sky : C.butter);
const FF = "'Pretendard', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif";
const GRADE = 'contrast(1.06) saturate(1.12) brightness(1.01)';
const SHADOW = '0 2px 6px rgba(10,16,30,.75), 0 0 22px rgba(10,16,30,.5), 0 8px 34px rgba(10,16,30,.4)';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

const FONTS: [string, string, string][] = [
  ['Pretendard', '600', 'Pretendard-SemiBold.woff2'], ['Pretendard', '700', 'Pretendard-Bold.woff2'],
  ['Pretendard', '800', 'Pretendard-ExtraBold.woff2'], ['Pretendard', '900', 'Pretendard-Black.woff2'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([f, w, file]) => new FontFace(f, `url(${staticFile('fonts/' + file)})`, {weight: w}).load().then((x) => document.fonts.add(x))))
      .then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
  }, [h]);
};

const useEnter = (t: number, s: number, e: number, soft = false) => {
  const {fps} = useVideoConfig();
  const k = spring({frame: Math.round((t - s) * fps), fps, config: soft ? {damping: 16, stiffness: 120, mass: .8} : {damping: 10, stiffness: 170, mass: .6}});
  const out = interpolate(t, [e - .22, e], [1, 0], clamp);
  return {k, out, opacity: Math.min(1, k * 2.5) * out};
};

// ---------------------------------------------------------------- phrase card (Day 6 layout)
const wordState = (reads: number[][], words: string[], t: number) => {
  const r = reads.find(([a, b]) => t >= a - .05 && t <= b + .25);
  if (!r) return words.map(() => 'plain');
  const total = words.reduce((n, w) => n + w.length, 0);
  let acc = 0; const p = interpolate(t, [r[0], r[1]], [0, 1], clamp) * total;
  return words.map((w) => { const a = acc; acc += w.length; return p >= acc ? 'done' : p >= a ? 'now' : 'next'; });
};

const Flow: React.FC<{w: number}> = () => (
  <svg viewBox="0 0 100 24" preserveAspectRatio="none" style={{position: 'absolute', left: '12%', right: '12%', width: '76%', bottom: -14, height: 28, overflow: 'visible'}}>
    <path d="M2 3 Q50 34 98 3" fill="none" stroke={C.butter} strokeWidth="5" strokeLinecap="round" vectorEffect="non-scaling-stroke" />
  </svg>
);

const Card: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const {k, out, opacity} = useEnter(t, ev.s, ev.e, true);
  const alt = (ev.alts as any[]).find((a) => t >= a.s && t < a.e);
  const src = alt ?? ev;
  const reads = alt ? alt.reads : ev.reads;
  const states = wordState(reads, src.en, t);
  const chip = (ev.chips as any[]).find((c) => t >= c.s && t < c.e);
  const emph = !alt ? (ev.emph as any[]).find((x) => t >= x.s && t < x.e) : null;
  const small = ev.compact;
  const fs = (small ? 84 : 118) * (ev.shrink ? interpolate(t, ev.shrink, [1, .58], clamp) : 1);
  const beat = 1 + .05 * Math.max(0, Math.sin((t - ev.s) * 6.2));
  return (
    <div style={{position: 'absolute', left: small ? 300 : 70, right: small ? 300 : 70, bottom: small ? 34 : 40, opacity,
      transform: `translateY(${(1 - k) * 60 + (1 - out) * 20}px)`, background: 'rgba(30,45,77,.9)', borderRadius: 30,
      padding: small ? '30px 36px 22px' : '46px 48px 28px', textAlign: 'center', boxShadow: '0 16px 50px rgba(10,16,30,.28)', fontFamily: FF}}>
      <div style={{position: 'absolute', top: -28, left: 40, background: C.sky, color: C.ink, fontWeight: 800, fontSize: small ? 26 : 30, padding: '9px 26px', borderRadius: 99}}>{ev.tag}</div>
      {chip ? <Chip c={chip} t={t} /> : null}
      <div style={{height: small ? 104 : 136, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: fs * .26}}>
        {src.en.map((w: string, i: number) => {
          const st = states[i]; const isEmph = emph?.words.includes(i);
          const flow = alt?.flow && (i === alt.flow[0]);
          const color = st === 'now' || isEmph ? C.butter : st === 'next' ? C.gray : C.white;
          const w2 = w === '→' ? C.sky : color;
          const node = <span style={{display: 'inline-block', fontWeight: 900, fontSize: fs, lineHeight: 1, letterSpacing: '-.02em', color: w2, transform: isEmph ? `scale(${beat})` : undefined}}>{w}</span>;
          if (alt?.flow && i === alt.flow[1]) return null;
          if (flow) {
            return (
              <span key={i} style={{position: 'relative', display: 'inline-flex', gap: fs * .22}}>
                {node}
                <span style={{display: 'inline-block', fontWeight: 900, fontSize: fs, lineHeight: 1, letterSpacing: '-.02em', color: states[i + 1] === 'now' ? C.butter : states[i + 1] === 'next' ? C.gray : C.white}}>{src.en[i + 1]}</span>
                <Flow w={0} />
              </span>
            );
          }
          return <span key={i}>{node}</span>;
        })}
      </div>
      <div style={{marginTop: small ? 10 : 18, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 34}}>
        <span style={{background: C.sky, color: C.ink, fontWeight: 900, fontSize: small ? 42 : 60, padding: small ? '6px 30px' : '8px 44px', borderRadius: 99}}>{src.pron}</span>
        <span style={{color: C.butter, fontWeight: 800, fontSize: small ? 36 : 48}}>{src.ko}</span>
      </div>
      {ev.arrow && t >= ev.arrow.s && t < ev.arrow.e ? <Rise a={ev.arrow} t={t} /> : null}
    </div>
  );
};

const Chip: React.FC<{c: any; t: number}> = ({c, t}) => {
  const isTurn = c.kind === 'turn';
  const left = isTurn ? interpolate(t, [c.s, c.e], [1, 0], clamp) : 0;
  return (
    <div style={{position: 'absolute', top: -34, right: 40, borderRadius: 99, overflow: 'hidden', background: isTurn ? C.butter : C.navy, color: isTurn ? C.ink : C.white, fontWeight: 800, fontSize: 34, padding: '10px 32px'}}>
      {c.text}
      {isTurn ? <div style={{position: 'absolute', left: 0, bottom: 0, height: 7, width: `${left * 100}%`, background: C.deep}} /> : null}
    </div>
  );
};

const Rise: React.FC<{a: any; t: number}> = ({a, t}) => {
  const p = interpolate(t, [a.s, a.s + .7], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  return (
    <div style={{position: 'absolute', top: -142, left: '50%', transform: 'translateX(-50%)', display: 'flex', alignItems: 'center', gap: 18, background: 'rgba(30,45,77,.9)', padding: '10px 28px', borderRadius: 99, whiteSpace: 'nowrap', opacity: p}}>
      <svg width="70" height="46" viewBox="0 0 70 46"><path d="M4 40 C28 40 44 30 60 8" fill="none" stroke={C.butter} strokeWidth="6" strokeLinecap="round" strokeDasharray="90" strokeDashoffset={90 * (1 - p)} /><path d="M46 8 L62 5 L60 22" fill="none" stroke={C.butter} strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" opacity={p} /></svg>
      <span style={{color: C.white, fontWeight: 800, fontSize: 32}}>{a.text}</span>
    </div>
  );
};

// ---------------------------------------------------------------- Korean captions
const Caption: React.FC<{c: {s: number; e: number; ko: string; hi: string; left?: number}; t: number; raised: boolean; compact: boolean}> = ({c, t, raised, compact}) => {
  const o = interpolate(t, [c.s, c.s + .12, c.e - .1, c.e], [0, 1, 1, 0], clamp);
  const parts = c.hi ? c.ko.split(c.hi) : [c.ko];
  return (
    <div style={{position: 'absolute', left: c.left ?? 90, right: 90, bottom: raised ? (compact ? 268 : 356) : 74, textAlign: 'center', opacity: o, fontFamily: FF, fontWeight: 800, fontSize: 54, lineHeight: 1.28, color: C.white, textShadow: SHADOW, textWrap: 'balance' as any}}>
      {parts.map((p, i) => (
        <React.Fragment key={i}>{p}{i < parts.length - 1 ? <span style={{color: C.butter}}>{c.hi}</span> : null}</React.Fragment>
      ))}
    </div>
  );
};

// ---------------------------------------------------------------- small pieces
const Label: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const {k, opacity} = useEnter(t, ev.s, ev.e);
  return <div style={{position: 'absolute', left: ev.x ?? undefined, right: ev.right ?? undefined, top: ev.y, opacity, transform: `scale(${.7 + .3 * k})`, transformOrigin: ev.right != null ? 'right center' : 'left center',
    background: tone(ev.tone), color: C.ink, fontFamily: FF, fontWeight: 800, fontSize: 38, padding: '12px 30px', borderRadius: 99, boxShadow: '0 8px 24px rgba(10,16,30,.22)'}}>{ev.text}</div>;
};

const Hero: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const {k, opacity} = useEnter(t, ev.s, ev.e);
  return (
    <div style={{position: 'absolute', left: ev.x, top: ev.y, opacity, transform: `scale(${.5 + .5 * k})`, transformOrigin: 'left top', fontFamily: FF, textShadow: SHADOW, whiteSpace: 'nowrap'}}>
      {ev.small ? <div style={{color: C.white, fontWeight: 700, fontSize: Math.max(36, ev.size * .42)}}>{ev.small}</div> : null}
      <div style={{color: tone(ev.tone), fontWeight: 900, fontSize: ev.size, lineHeight: 1.05, letterSpacing: '-.02em'}}>{ev.big}</div>
    </div>
  );
};

const Sparkles: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const p = (t - ev.s) / (ev.e - ev.s);
  if (p < 0 || p > 1) return null;
  return (
    <>
      {Array.from({length: ev.n}).map((_, i) => {
        const a = random(`a${ev.s}${i}`) * Math.PI * 2, d = 90 + random(`d${ev.s}${i}`) * 300, sz = 22 + random(`s${ev.s}${i}`) * 46;
        const q = Easing.out(Easing.cubic)(p);
        return <div key={i} style={{position: 'absolute', left: ev.x + Math.cos(a) * d * q - sz / 2, top: ev.y + Math.sin(a) * d * q - sz / 2 + p * p * 60, fontSize: sz, color: i % 2 ? C.butter : '#E9C766',
          opacity: interpolate(p, [0, .12, .65, 1], [0, 1, 1, 0]), transform: `rotate(${p * 180 * (i % 2 ? 1 : -1)}deg) scale(${interpolate(p, [0, .2, 1], [.3, 1, .5])})`, textShadow: '0 2px 8px rgba(20,32,58,.35)'}}>✦</div>;
      })}
    </>
  );
};

const Badge: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const o = interpolate(t, [ev.s, ev.s + .5, ev.e - .3, ev.e], [0, 1, 1, 0], clamp);
  return <div style={{position: 'absolute', right: 56, top: 44, textAlign: 'right', opacity: o, fontFamily: FF, color: C.white, textShadow: SHADOW, lineHeight: 1.2}}>
    <div style={{fontWeight: 900, fontSize: 46}}>{ev.l1}</div><div style={{fontWeight: 700, fontSize: 34}}>{ev.l2}</div>
  </div>;
};

const Nudge: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const {k, opacity} = useEnter(t, ev.s, ev.e, true);
  return <div style={{position: 'absolute', right: 56, bottom: 210, opacity, transform: `translateX(${(1 - k) * 50}px)`, background: 'rgba(255,248,238,.95)', color: C.deep, fontFamily: FF, fontWeight: 800, fontSize: 34, padding: '14px 30px', borderRadius: 20, boxShadow: '0 10px 30px rgba(10,16,30,.2)'}}>{ev.text}</div>;
};

const Level: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const {k, opacity} = useEnter(t, ev.s, ev.e);
  return (
    <div style={{position: 'absolute', right: 70, top: 210, width: 620, opacity, transform: `translateX(${(1 - k) * 60}px)`, background: 'rgba(30,45,77,.9)', borderRadius: 28, padding: '28px 34px', display: 'flex', gap: 24, alignItems: 'center', fontFamily: FF, boxShadow: '0 14px 40px rgba(10,16,30,.25)'}}>
      <div style={{fontSize: 84, lineHeight: 1}}>{ev.emoji}</div>
      <div><div style={{color: tone(ev.tone), fontWeight: 900, fontSize: 46}}>{ev.title}</div><div style={{color: C.white, fontWeight: 700, fontSize: 34, marginTop: 6}}>{ev.body}</div></div>
    </div>
  );
};

const Stack: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const {out} = useEnter(t, ev.s, ev.e, true);
  return (
    <div style={{position: 'absolute', left: 70, right: 70, bottom: 40, display: 'grid', gap: 12, opacity: out, fontFamily: FF}}>
      {(ev.rows as any[]).map((r, i) => {
        const k = spring({frame: Math.round((t - r.from) * 30), fps: 30, config: {damping: 13, stiffness: 150}});
        const lit = t >= r.lit[0] && t <= r.lit[1] + .3;
        return (
          <div key={i} style={{opacity: Math.min(1, k * 2), transform: `translateY(${(1 - k) * 40}px) scale(${lit ? 1.015 : 1})`, background: lit ? 'rgba(30,45,77,.96)' : 'rgba(30,45,77,.84)', borderRadius: 24, padding: '16px 36px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', outline: lit ? `4px solid ${C.butter}` : 'none'}}>
            <span style={{color: lit ? C.butter : C.white, fontWeight: 900, fontSize: 70, letterSpacing: '-.02em'}}>{r.en.join(' ')}</span>
            <span style={{display: 'flex', alignItems: 'center', gap: 24}}>
              <span style={{background: C.sky, color: C.ink, fontWeight: 900, fontSize: 38, padding: '5px 26px', borderRadius: 99}}>{r.pron}</span>
              <span style={{color: C.butter, fontWeight: 800, fontSize: 34, minWidth: 250, textAlign: 'right'}}>{r.ko}</span>
            </span>
          </div>
        );
      })}
    </div>
  );
};

const BehindWords: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const {k, opacity} = useEnter(t, ev.s, ev.e);
  return (
    <div style={{position: 'absolute', left: ev.x, top: ev.y, whiteSpace: 'nowrap', opacity, transform: `scale(${.72 + .28 * k})`, transformOrigin: 'left center', fontFamily: FF, textShadow: SHADOW}}>
      <div style={{color: C.white, fontWeight: 700, fontSize: 50, paddingLeft: 90}}>{ev.small}</div>
      <div style={{color: tone(ev.tone), fontWeight: 900, fontSize: ev.size, lineHeight: 1.02, letterSpacing: '-.02em'}}>{ev.big}</div>
    </div>
  );
};

const PlanCard: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const {k, out} = useEnter(t, ev.s, ev.e, true);
  return (
    <div style={{position: 'absolute', right: 56, top: 170, width: 590, opacity: Math.min(1, k * 2) * out, transform: `translateX(${(1 - k) * 60}px)`, background: 'rgba(30,45,77,.92)', borderRadius: 28, padding: '26px 30px', fontFamily: FF, boxShadow: '0 14px 40px rgba(10,16,30,.25)'}}>
      <div style={{color: C.butter, fontWeight: 900, fontSize: 40, marginBottom: 14}}>오늘의 순서</div>
      <div style={{display: 'grid', gap: 14}}>
        {(ev.steps as any[]).map((st, i) => {
          const a = spring({frame: Math.round((t - st.from) * 30), fps: 30, config: {damping: 12, stiffness: 150}});
          return (
            <div key={i} style={{display: 'flex', alignItems: 'center', gap: 18, opacity: Math.min(1, a * 2), transform: `translateX(${(1 - a) * 30}px)`}}>
              <span style={{width: 58, height: 58, flex: 'none', borderRadius: 99, background: i % 2 ? C.sky : C.butter, color: C.ink, display: 'grid', placeItems: 'center', fontWeight: 900, fontSize: 32}}>{i + 1}</span>
              <span style={{flex: 1, minWidth: 0}}>
                <div style={{color: C.white, fontWeight: 900, fontSize: 36, lineHeight: 1.2}}>{st.title}</div>
                <div style={{color: C.white, fontWeight: 700, fontSize: 25, opacity: .82}}>{st.who} · {st.time}</div>
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const Countdown: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const step = (ev.e - ev.s) / 3;
  const i = Math.min(2, Math.max(0, Math.floor((t - ev.s) / step)));
  const local = t - ev.s - i * step;
  const k = spring({frame: Math.round(local * 30), fps: 30, config: {damping: 9, stiffness: 190, mass: .55}});
  const ring = interpolate(t, [ev.s, ev.e], [0, 1], clamp);
  const o = interpolate(t, [ev.s, ev.s + .12, ev.e - .12, ev.e], [0, 1, 1, 0], clamp);
  const R = 150, L = 2 * Math.PI * R;
  return (
    <div style={{position: 'absolute', left: 1290, top: 190, width: 400, display: 'grid', justifyItems: 'center', gap: 22, opacity: o, fontFamily: FF}}>
      <div style={{background: C.butter, color: C.ink, fontWeight: 800, fontSize: 36, padding: '10px 30px', borderRadius: 99, boxShadow: '0 8px 24px rgba(10,16,30,.22)'}}>{ev.text}</div>
      <div style={{position: 'relative', width: 340, height: 340}}>
        <svg width="340" height="340" viewBox="0 0 340 340" style={{position: 'absolute', inset: 0}}>
          <circle cx="170" cy="170" r={R + 10} fill="rgba(30,45,77,.92)" />
          <circle cx="170" cy="170" r={R} fill="none" stroke="rgba(255,255,255,.2)" strokeWidth="14" />
          <circle cx="170" cy="170" r={R} fill="none" stroke={C.butter} strokeWidth="14" strokeLinecap="round" strokeDasharray={L} strokeDashoffset={L * ring} transform="rotate(-90 170 170)" />
        </svg>
        <div style={{position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', color: C.white, fontWeight: 900, fontSize: 200, lineHeight: 1, transform: `scale(${.55 + .45 * k})`}}>{3 - i}</div>
      </div>
    </div>
  );
};

const Progress: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const p = interpolate(t, [ev.s, ev.e], [0, 1], clamp);
  const o = interpolate(t, [ev.s, ev.s + .5, ev.e - .3, ev.e], [0, 1, 1, 0], clamp);
  const bob = Math.abs(Math.sin(t * 5)) * 3;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 8, background: 'rgba(20,32,58,.25)', opacity: o}}>
      <div style={{height: '100%', width: `${p * 100}%`, background: C.butter}} />
      {((ev.marks ?? []) as number[]).map((x, i) => <div key={i} style={{position: 'absolute', left: `${((x - ev.s) / (ev.e - ev.s)) * 100}%`, top: -5, width: 5, height: 18, borderRadius: 3, background: C.sky}} />)}
      <Img src={staticFile('brand/bear-butterfly.png')} style={{position: 'absolute', left: `calc(${p * 100}% - 34px)`, bottom: 4 + bob, height: 58}} />
    </div>
  );
};

const Wipe: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const mid = (ev.s + ev.e) / 2;
  const x = interpolate(t, [ev.s, mid, ev.e], [-105, 0, 105], {...clamp, easing: Easing.inOut(Easing.cubic)});
  return (
    <AbsoluteFill style={{background: C.cream, transform: `translateX(${x}%)`, justifyContent: 'center', alignItems: 'center', gap: 20, fontFamily: FF}}>
      <Img src={staticFile('brand/bear-butterfly.png')} style={{height: 380, transform: `translateY(${-Math.abs(Math.sin(t * 9)) * 16}px)`}} />
      {ev.text ? <div style={{color: C.deep, fontWeight: 900, fontSize: 78}}>{ev.text}</div> : null}
    </AbsoluteFill>
  );
};

const Title: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const {fps} = useVideoConfig();
  const walk = interpolate(t, [ev.s, ev.s + 1.5], [-760, 0], {...clamp, easing: Easing.out(Easing.cubic)});
  const bob = t < ev.s + 1.5 ? Math.abs(Math.sin(t * 9)) * 18 : 0;
  const a = spring({frame: Math.round((t - ev.s - .7) * fps), fps, config: {damping: 11, stiffness: 130}});
  const b = spring({frame: Math.round((t - ev.s - 1.1) * fps), fps, config: {damping: 11, stiffness: 130}});
  const up = interpolate(t, [ev.e - .5, ev.e], [0, -106], {...clamp, easing: Easing.inOut(Easing.cubic)});
  return (
    <AbsoluteFill style={{background: C.cream, transform: `translateY(${up}%)`, fontFamily: FF}}>
      <Img src={staticFile('brand/bear-butterfly.png')} style={{position: 'absolute', left: 150, top: 230, height: 620, transform: `translateX(${walk}px) translateY(${-bob}px)`}} />
      <div style={{position: 'absolute', left: 860, right: 60, top: 300}}>
        <div style={{opacity: Math.min(1, a * 2), transform: `translateY(${(1 - a) * 40}px)`}}>
          <span style={{background: C.sky, color: C.ink, fontWeight: 900, fontSize: 52, padding: '10px 36px', borderRadius: 99}}>DAY {ev.day} · 첫날 무료</span>
          <div style={{color: C.deep, fontWeight: 900, fontSize: 118, letterSpacing: '-.03em', lineHeight: 1.08, marginTop: 44}}>{ev.en}</div>
        </div>
        <div style={{opacity: Math.min(1, b * 2), transform: `translateY(${(1 - b) * 40}px)`, color: C.deep, fontWeight: 800, fontSize: 84, marginTop: 20}}>{ev.ko}</div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- ending cards
const Page: React.FC<{children: React.ReactNode; bear?: boolean}> = ({children, bear = true}) => (
  <AbsoluteFill style={{background: C.cream, fontFamily: FF, color: C.deep, padding: '76px 90px'}}>
    {bear ? <Img src={staticFile('brand/bear-butterfly.png')} style={{position: 'absolute', right: 70, top: 44, height: 200}} /> : null}
    {children}
  </AbsoluteFill>
);
const Rise2: React.FC<{t: number; at: number; children: React.ReactNode; style?: React.CSSProperties}> = ({t, at, children, style}) => {
  const k = spring({frame: Math.round((t - at) * 30), fps: 30, config: {damping: 13, stiffness: 140}});
  return <div style={{opacity: Math.min(1, k * 2), transform: `translateY(${(1 - k) * 44}px)`, ...style}}>{children}</div>;
};

const Recap: React.FC<{ev: Ev; t: number}> = ({ev, t}) => (
  <Page>
    <div style={{fontWeight: 800, fontSize: 36, opacity: .75}}>Day 1 · Hello, Little Bear!</div>
    <div style={{fontWeight: 900, fontSize: 78, letterSpacing: '-.02em'}}>오늘의 표현 3가지</div>
    <div style={{display: 'grid', gap: 26, marginTop: 84}}>
      {(ev.rows as any[]).map((r, i) => (
        <Rise2 key={i} t={t} at={ev.s + .5 + i * .5} style={{background: C.paper, borderRadius: 26, padding: '34px 44px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', boxShadow: '0 8px 24px rgba(23,59,92,.08)'}}>
          <span style={{display: 'flex', alignItems: 'center', gap: 28}}>
            <span style={{width: 76, height: 76, borderRadius: 99, background: i % 2 ? C.sky : C.butter, display: 'grid', placeItems: 'center', fontWeight: 900, fontSize: 40}}>{i + 1}</span>
            <span style={{fontWeight: 900, fontSize: 70, letterSpacing: '-.02em'}}>{r.en.join(' ')}</span>
          </span>
          <span style={{textAlign: 'right'}}>
            <span style={{background: C.sky, fontWeight: 900, fontSize: 38, padding: '5px 26px', borderRadius: 99, color: C.ink}}>{r.pron}</span>
            <div style={{fontWeight: 800, fontSize: 32, marginTop: 10}}>{r.ko}</div>
          </span>
        </Rise2>
      ))}
    </div>
    <Rise2 t={t} at={ev.s + 2.3} style={{position: 'absolute', left: 0, right: 0, bottom: 56, textAlign: 'center', fontWeight: 800, fontSize: 44}}>다음은 2일차 · 같이 찾아봐요 🦋</Rise2>
  </Page>
);

const AV = (hair: string, top: string, shirt: string, bg: string, bun = false) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80"><circle cx="40" cy="40" r="39" fill="${bg}"/>${bun ? `<circle cx="41" cy="17" r="11" fill="${hair}"/>` : ''}<path d="${top}" fill="${hair}"/><path d="M12 78c1-19 13-24 28-24s27 5 28 24" fill="${shirt}"/><path d="M34 48h12v12c-4 5-8 5-12 0Z" fill="#e7bca0"/><ellipse cx="40" cy="35" rx="15" ry="19" fill="#f2cfad"/><path d="M25 31c9-1 17-5 22-13 2 7 5 11 9 14-1-20-31-25-31-1Z" fill="${hair === '#33475a' ? '#35485b' : hair}"/><g fill="#33475a"><circle cx="34" cy="36" r="1.2"/><circle cx="46" cy="36" r="1.2"/></g><path d="M36 44q4 4 8 0" fill="none" stroke="#a26c57" stroke-width="1.4" stroke-linecap="round"/><path d="m28 57 12 10 12-10" fill="none" stroke="#fff9f0" stroke-width="2"/></svg>`;
// The site's own illustrated avatars (bearandjoy.com/littlesteps), reproduced exactly.
const REVIEWS = [
  {name: 'Park H.', who: '6세, 4세, 10개월 세 아이의 엄마', text: '아이랑 눈 맞추며 놀 수 있어서 좋아요.', av: AV('#35485b', 'M21 47V31c0-24 38-24 38 0v16L47 55H32Z', '#a9bac9', '#efe0cc', true)},
  {name: 'Kim S.', who: '28개월 아들을 둔 엄마', text: '영어를 어떻게 알려줄 수 있는지 알 수 있는 기회가 생겨서 정말 좋아요.', av: AV('#55483e', 'M20 53V31c0-27 40-27 40 0v22l-13 7H31Z', '#a7b397', '#e5e9df')},
  {name: 'Ahn J.', who: '임신 32주 | 아빠', text: '부모가 될 준비를 한 걸음 더 할 수 있어 감사해요.', av: AV('#33475a', 'M23 37V29c0-19 34-20 35 0v8l-8-14c-7 6-16 8-27 8Z', '#a9bac9', '#efe0cc')},
  {name: 'Pyo J.', who: '신혼부부', text: '영어 공부에 대한 막연한 두려움을 설렘으로 바꿔준, 너무너무 즐겁고 감사한 7일이었습니다!', av: AV('#705343', 'M19 50V31c0-25 42-25 42 0v19l-9 5-3-9H30l-3 9Z', '#bb8f82', '#e9d8cf')},
];
const Reviews: React.FC<{ev: Ev; t: number}> = ({ev, t}) => (
  <Page>
    <div style={{fontWeight: 900, fontSize: 78, letterSpacing: '-.02em'}}>함께한 작은 순간들</div>
    <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 30, marginTop: 92}}>
      {REVIEWS.map((r, i) => (
        <Rise2 key={r.name} t={t} at={ev.s + .5 + i * .7} style={{background: C.paper, borderRadius: 26, padding: 40, display: 'flex', gap: 30, alignItems: 'center', minHeight: 300, boxShadow: '0 8px 24px rgba(23,59,92,.08)'}}>
          <img src={`data:image/svg+xml;utf8,${encodeURIComponent(r.av)}`} style={{width: 136, height: 136, flex: 'none'}} />
          <div>
            <div style={{fontWeight: 800, fontSize: 40, lineHeight: 1.34}}>{r.text}</div>
            <div style={{fontWeight: 700, fontSize: 26, opacity: .7, marginTop: 10}}>{r.name} · {r.who}</div>
          </div>
        </Rise2>
      ))}
    </div>
    <div style={{position: 'absolute', left: 90, bottom: 44, fontWeight: 600, fontSize: 24, opacity: .6}}>후기 발췌 · 프로필 이미지는 실제 사진이 아닌 일러스트예요.</div>
  </Page>
);

const DAYS = [['2', '같이 찾아봐요'], ['3', '조이와 움직여요'], ['4', '무엇을 좋아하나요?'], ['5', '이야기 탐정'], ['6', '깔깔 영어놀이'], ['7', '우리의 모험']];
const Offer: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const pulse = 1 + .025 * Math.max(0, Math.sin((t - ev.s) * 4));
  return (
    <Page bear={false}>
      <div style={{fontWeight: 900, fontSize: 76, letterSpacing: '-.02em'}}>첫걸음을 뗐다면, 다음 날도 함께해요</div>
      <div style={{display: 'grid', gridTemplateColumns: '1.02fr 1fr', gap: 44, marginTop: 70}}>
        <div style={{display: 'grid', gap: 13}}>
          {DAYS.map(([d, name], i) => (
            <Rise2 key={d} t={t} at={ev.s + .35 + i * .22} style={{background: i === 0 ? C.butter : C.paper, borderRadius: 20, padding: '27px 30px', display: 'flex', gap: 24, alignItems: 'center', fontWeight: 800, fontSize: 42}}>
              <span style={{fontWeight: 900, minWidth: 116}}>{d}일차</span>{name}
            </Rise2>
          ))}
        </div>
        <Rise2 t={t} at={ev.s + 1.9} style={{background: C.navy, color: C.white, borderRadius: 30, padding: '40px 44px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between'}}>
          <div style={{fontWeight: 700, fontSize: 37, lineHeight: 1.9}}>
            <div>✓ Mark의 발음 영상 · Joy의 놀이 영상</div>
            <div>✓ 매일 인쇄해서 즐기는 워크시트</div>
            <div>✓ 내 이름을 담은 완주 기념장</div>
            <div>✓ 2–7일차, 24시간마다 하나씩 열려요</div>
            <div>✓ 시작일부터 30일 동안 다시 보기</div>
          </div>
          <Rise2 t={t} at={ev.s + 3.3} style={{marginTop: 26}}>
            <div style={{background: C.butter, color: C.ink, borderRadius: 22, padding: '20px 26px', textAlign: 'center', fontWeight: 900, fontSize: 52, transform: `scale(${pulse})`}}>전체 과정 열기 · ₩47,000</div>
            <div style={{textAlign: 'center', fontWeight: 700, fontSize: 28, marginTop: 16}}>한 번만 결제해요 · 정기결제가 아니에요</div>
          </Rise2>
        </Rise2>
      </div>
    </Page>
  );
};

const LogoCard: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const k = spring({frame: Math.round((t - ev.s) * 30), fps: 30, config: {damping: 16, stiffness: 90}});
  const fade = interpolate(t, [ev.e - .7, ev.e], [1, 0], clamp);
  return (
    <AbsoluteFill style={{background: C.cream, justifyContent: 'center', alignItems: 'center', opacity: fade}}>
      <Img src={staticFile('brand/logo-full.png')} style={{height: 620, opacity: Math.min(1, k * 1.5), transform: `translateY(${(1 - k) * 24}px)`}} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- main
export const BearJoyClass: React.FC<{plan: ClassPlan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const dir = plan.media ?? 'day1';
  const E = (type: string) => plan.events.filter((e) => e.type === type);
  const live = (e: Ev, pad = .05) => t >= e.s - .05 && t <= e.e + pad;

  let z = 1, prev = 1, since = 99, ox = 960, oy = 500;
  for (const k of plan.zooms) if (k.t <= t) { prev = z; z = k.z; since = t - k.t; ox = k.ox; oy = k.oy; }
  z = prev + (z - prev) * interpolate(since, [0, .8], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const cam: React.CSSProperties = {position: 'absolute', inset: 0, transform: `scale(${z})`, transformOrigin: `${ox}px ${oy}px`};
  const vid: React.CSSProperties = {width: '100%', height: '100%', objectFit: 'cover', filter: GRADE};

  const cardNow = E('card').find((c) => t >= c.s && t < c.e) ?? null;
  const stackNow = E('stack').some((c) => t >= c.s && t < c.e);
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const coldCap = E('cap').find((c) => t >= c.s && t < c.e);
  const showCap = !stackNow && t < plan.offset + plan.mainEnd;

  return (
    <AbsoluteFill style={{background: C.cream}}>
      <div style={cam}>
        {plan.segments.map((g, i) => (
          <Sequence key={i} from={Math.round(g.out_s * fps)} durationInFrames={Math.round((g.src_e - g.src_s) * fps)} layout="none">
            <AbsoluteFill><OffthreadVideo src={staticFile(`${dir}/source.mov`)} muted trimBefore={Math.round(g.src_s * fps)} style={vid} /></AbsoluteFill>
          </Sequence>
        ))}
        {E('behind').map((ev, k) => (live(ev, .1) ? <BehindWords key={k} ev={ev} t={t} /> : null))}
        {E('behind').map((ev, k) => {
          const from = Math.round(ev.clip_s * fps), n = Math.round((ev.clip_e - ev.clip_s) * fps);
          return (
            <Sequence key={`m${k}`} from={from} durationInFrames={n} layout="none">
              <AbsoluteFill style={{opacity: t >= ev.s - .1 && t <= ev.e + .15 ? 1 : 0}}>
                <OffthreadVideo src={staticFile(`${dir}/${ev.clip}.webm`)} transparent muted style={vid} />
              </AbsoluteFill>
            </Sequence>
          );
        })}
      </div>
      {cap && showCap && !cardNow ? <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,16,30,0) 72%, rgba(10,16,30,.38) 100%)'}} /> : null}
      {E('badge').map((ev, k) => (live(ev) ? <Badge key={k} ev={ev} t={t} /> : null))}
      {E('label').map((ev, k) => (live(ev) ? <Label key={k} ev={ev} t={t} /> : null))}
      {E('plan').map((ev, k) => (live(ev) ? <PlanCard key={k} ev={ev} t={t} /> : null))}
      {E('count').map((ev, k) => (live(ev) ? <Countdown key={k} ev={ev} t={t} /> : null))}
      {E('hero').map((ev, k) => (live(ev) ? <Hero key={k} ev={ev} t={t} /> : null))}
      {E('level').map((ev, k) => (live(ev) ? <Level key={k} ev={ev} t={t} /> : null))}
      {E('nudge').map((ev, k) => (live(ev) ? <Nudge key={k} ev={ev} t={t} /> : null))}
      {E('stack').map((ev, k) => (live(ev) ? <Stack key={k} ev={ev} t={t} /> : null))}
      {E('card').map((ev, k) => (live(ev) ? <Card key={k} ev={ev} t={t} /> : null))}
      {coldCap ? <Caption c={coldCap as any} t={t} raised={false} compact={false} /> : null}
      {cap && showCap ? <Caption c={cap} t={t} raised={!!cardNow} compact={!!cardNow?.compact} /> : null}
      {E('sparkles').map((ev, k) => (live(ev) ? <Sparkles key={k} ev={ev} t={t} /> : null))}
      {E('progress').map((ev, k) => (live(ev) ? <Progress key={k} ev={ev} t={t} /> : null))}
      {E('title').map((ev, k) => (live(ev) ? <Title key={k} ev={ev} t={t} /> : null))}
      {E('recap').map((ev, k) => (live(ev) ? <Recap key={k} ev={ev} t={t} /> : null))}
      {E('reviews').map((ev, k) => (live(ev) ? <Reviews key={k} ev={ev} t={t} /> : null))}
      {E('offer').map((ev, k) => (live(ev) ? <Offer key={k} ev={ev} t={t} /> : null))}
      {E('logo').map((ev, k) => (live(ev) ? <LogoCard key={k} ev={ev} t={t} /> : null))}
      {E('wipe').map((ev, k) => (live(ev) ? <Wipe key={k} ev={ev} t={t} /> : null))}
    </AbsoluteFill>
  );
};
