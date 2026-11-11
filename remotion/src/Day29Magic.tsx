// Day 29 — "5 Harry Potter phrases" (one-off Harry Potter look, owner 11 Nov 2026; see brand/BRAND.md "Harry Potter episodes").
// Mark (matte) in front of the Great Hall, a pulsing gold outline, film clips playing behind him while he freezes for each film line.
// Plan: projects/2026-11-day29-christmas-phrases/build_plan.py → versions/<v>/plan.json. Audio is mixed separately (mix.py).
import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Img, OffthreadVideo, Sequence, Freeze, continueRender, delayRender, interpolate, spring,
  staticFile, useCurrentFrame, useVideoConfig, Easing, random,
} from 'remotion';

type Seg = {kind: 'mark' | 'film'; s: number; e: number; src?: number; srcEnd?: number; freeze?: number};
type Clip = {clip: string; src: string; s: number; e: number; clipIn: number};
type Cap = {s: number; e: number; en: string; ko: string; film?: boolean};
type Phrase = {s: number; n: number; en: string; ko: string};
export type Day29Plan = {
  name: string; fps: number; duration: number; frames: number; day: number;
  subject: string; background: string; props: string; propsUntil: number;
  title: {s: number; e: number; en: string; sub: string; ko: string};
  segments: Seg[]; clips: Clip[]; captions: Cap[]; phrases: Phrase[]; endCard: {s: number; e: number};
};

const GOLD = '#FFD970', GOLD_LIGHT = '#FFF4C8', INK = '#120C06';
const HP = "'HarryP', serif";
const PRE = "'Pretendard', sans-serif";
const FONTS: [string, string, string][] = [
  ['HarryP', '400', 'HarryP.ttf'],
  ['Pretendard', '700', 'Pretendard-Bold.woff2'],
  ['Pretendard', '800', 'Pretendard-ExtraBold.woff2'],
  ['Pretendard', '900', 'Pretendard-Black.woff2'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([f, w, file]) => new FontFace(f, `url(${staticFile('fonts/' + file)})`, {weight: w}).load().then((x) => document.fonts.add(x))))
      .then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
  }, [h]);
};
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const fade = (t: number, s: number, e: number, i = 0.3, o = 0.35) =>
  interpolate(t, [s, s + i, e - o, e], [0, 1, 1, 0], {...clamp, easing: Easing.inOut(Easing.cubic)});
const glowText = (c = GOLD) => `0 0 18px ${c}, 0 0 42px rgba(255,190,80,.55), 0 6px 22px rgba(0,0,0,.8)`;

// ── Background: the Great Hall, slow push-in, flickering candle light ──
const Hall: React.FC<{src: string; t: number}> = ({src, t}) => {
  const flick = 0.06 * Math.sin(t * 7.3) + 0.04 * Math.sin(t * 13.1 + 1) + 0.03 * Math.sin(t * 3.1);
  return (
    <AbsoluteFill style={{overflow: 'hidden', background: '#0b0806'}}>
      <Img src={staticFile(src)} style={{position: 'absolute', height: '100%', left: '50%', top: 0,
        transform: `translateX(-50%) scale(${1.04 + t * 0.0012})`, filter: `blur(2.5px) brightness(${0.82 + flick}) saturate(1.1)`}} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 35%, rgba(255,190,90,.10), rgba(0,0,0,.55) 75%)'}} />
    </AbsoluteFill>
  );
};

// ── Film clips behind Mark ──
const Clips: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const {fps} = useVideoConfig();
  return <>{plan.clips.map((c, i) => (
    <Sequence key={i} from={Math.round(c.s * fps)} durationInFrames={Math.round((c.e - c.s) * fps)} layout="none">
      <AbsoluteFill style={{opacity: fade(t, c.s, c.e, 0.25, 0.45)}}>
        <OffthreadVideo src={staticFile(c.src)} muted startFrom={Math.round(c.clipIn * fps)}
          style={{width: '100%', height: '100%', objectFit: 'cover', filter: 'blur(1.5px) brightness(.85) saturate(1.05)'}} />
        <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, transparent 40%, rgba(0,0,0,.55))'}} />
      </AbsoluteFill>
    </Sequence>
  ))}</>;
};

// ── Mark with the magic outline ──
const Mark: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const {fps} = useVideoConfig();
  const f = useCurrentFrame();
  // shrink to 86% while a clip plays behind him
  const clipOn = plan.clips.some((c) => t >= c.s && t < c.e - 0.3);
  const near = plan.clips.reduce((m, c) => Math.max(m, fade(t, c.s, c.e, 0.35, 0.45)), 0);
  const scale = interpolate(near, [0, 1], [1, 0.86]);
  // outline: gentle breathing pulse; flares at each film line
  const flare = plan.segments.filter((s) => s.kind === 'film').reduce((m, s) => Math.max(m, fade(t, s.s, s.e + 0.4, 0.15, 0.6)), 0);
  const pulse = 0.5 + 0.5 * Math.sin(t * Math.PI);
  const line = 2.2 + pulse * 0.8 + flare * 1.6, halo = 22 + pulse * 8 + flare * 26;
  const glow = `drop-shadow(0 0 ${line}px ${GOLD_LIGHT}) drop-shadow(0 0 ${line}px ${GOLD_LIGHT}) drop-shadow(0 0 ${halo}px ${GOLD}) drop-shadow(0 0 ${halo * 1.8}px rgba(255,170,60,${0.35 + flare * 0.3}))`;
  void clipOn;
  return (
    <AbsoluteFill style={{transform: `scale(${scale})`, transformOrigin: '50% 100%', filter: glow}}>
      {plan.segments.map((s, i) => (
        <Sequence key={i} from={Math.round(s.s * fps)} durationInFrames={Math.max(1, Math.round((s.e - s.s) * fps))} layout="none">
          <AbsoluteFill>
            {s.kind === 'mark'
              ? <OffthreadVideo src={staticFile(plan.subject)} transparent muted startFrom={Math.round(s.src! * fps)} style={{width: '100%', height: '100%'}} />
              : <Freeze frame={Math.round(s.freeze! * fps) - 1}>
                  <OffthreadVideo src={staticFile(plan.subject)} transparent muted style={{width: '100%', height: '100%'}} />
                </Freeze>}
          </AbsoluteFill>
        </Sequence>
      ))}
      {f < plan.propsUntil * fps ? (
        <Img src={staticFile(`${plan.props}/${String(f).padStart(4, '0')}.png`)}
          style={{position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: fade(t, 0.05, plan.propsUntil, 0.2, 0.35)}} />
      ) : null}
    </AbsoluteFill>
  );
};

// ── Sparkles: drifting wand dust + bursts ──
const Star: React.FC<{x: number; y: number; r: number; o: number; rot?: number}> = ({x, y, r, o, rot = 0}) => (
  <svg style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, opacity: o, transform: `rotate(${rot}deg)`,
    filter: `drop-shadow(0 0 ${r * 0.6}px ${GOLD})`}} viewBox="-10 -10 20 20">
    <path d="M0 -10 L2 -2 L10 0 L2 2 L0 10 L-2 2 L-10 0 L-2 -2 Z" fill={GOLD_LIGHT} />
  </svg>
);
const Sparkles: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const stars: React.ReactNode[] = [];
  const LIFE = 2.6;
  for (let i = 0; i < 46; i++) { // drifting dust rising from around Mark's outline
    const off = random(`o${i}`) * LIFE, cyc = Math.floor((t + off) / LIFE), ph = ((t + off) % LIFE) / LIFE;
    const side = random(`s${i}-${cyc}`) < 0.5 ? -1 : 1;
    const x = 540 + side * (170 + random(`x${i}-${cyc}`) * 330), y = 1750 - random(`y${i}-${cyc}`) * 1150 - ph * 220;
    stars.push(<Star key={`d${i}`} x={x + Math.sin(ph * 6 + i) * 12} y={y} r={4 + random(`r${i}`) * 9} o={Math.sin(ph * Math.PI) * 0.9} rot={ph * 90} />);
  }
  const bursts = [0.05, plan.propsUntil - 0.3, ...plan.segments.filter((s) => s.kind === 'film').map((s) => s.s)];
  bursts.forEach((b, k) => {
    const p = (t - b) / 1.1;
    if (p < 0 || p > 1) return;
    const cx = 540, cy = k < 2 ? 640 : 760;
    for (let i = 0; i < 26; i++) {
      const a = random(`ba${k}-${i}`) * Math.PI * 2, d = (160 + random(`bd${k}-${i}`) * 300) * Easing.out(Easing.cubic)(p);
      stars.push(<Star key={`b${k}-${i}`} x={cx + Math.cos(a) * d} y={cy + Math.sin(a) * d * 0.9} r={6 + random(`br${k}-${i}`) * 12} o={(1 - p) * 0.95} rot={p * 180} />);
    }
  });
  return <AbsoluteFill style={{pointerEvents: 'none'}}>{stars}</AbsoluteFill>;
};

// ── Text ──
const DayChip: React.FC = () => (
  <div style={{position: 'absolute', top: 92, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
    <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 34, color: GOLD_LIGHT, padding: '10px 28px', borderRadius: 999,
      border: `2px solid ${GOLD}`, background: 'rgba(18,12,6,.55)', boxShadow: `0 0 22px rgba(255,200,90,.35)`}}>DAY 29 · 출간까지 매일 업로드</div>
  </div>
);
const Title: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const {fps} = useVideoConfig();
  const {s, e, en, sub, ko} = plan.title;
  if (t < s || t > e) return null;
  const sp = spring({frame: Math.round((t - s) * fps), fps, config: {damping: 11, stiffness: 120}});
  return (
    <div style={{position: 'absolute', top: 190, left: 40, right: 40, textAlign: 'center', opacity: fade(t, s, e, 0.2, 0.4), transform: `scale(${0.8 + 0.2 * sp})`}}>
      <div style={{fontFamily: HP, fontSize: 150, lineHeight: 0.95, color: GOLD, textShadow: glowText()}}>{en}</div>
      <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 40, color: '#fff', marginTop: 14, textShadow: glowText('rgba(0,0,0,0)')}}>{sub}</div>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 44, color: GOLD_LIGHT, marginTop: 8, textShadow: '0 4px 18px rgba(0,0,0,.9)', wordBreak: 'keep-all'}}>{ko}</div>
    </div>
  );
};
const PhraseCard: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const {fps} = useVideoConfig();
  const i = plan.phrases.findIndex((p, k) => t >= p.s && t < (plan.phrases[k + 1]?.s ?? plan.endCard.s - 4.5));
  if (i < 0) return null;
  const p = plan.phrases[i], e = plan.phrases[i + 1]?.s ?? plan.endCard.s - 4.5;
  const sp = spring({frame: Math.round((t - p.s) * fps), fps, config: {damping: 10, stiffness: 140}});
  return (
    <div style={{position: 'absolute', top: 175, left: 30, right: 30, textAlign: 'center', opacity: fade(t, p.s, e, 0.15, 0.3)}}>
      <div style={{fontFamily: HP, fontSize: 92, color: GOLD_LIGHT, textShadow: glowText(), transform: `scale(${0.6 + 0.4 * sp})`}}>No. {p.n}</div>
      <div style={{fontFamily: HP, fontSize: p.en.length > 12 ? 128 : 160, lineHeight: 0.95, color: GOLD, textShadow: glowText(), transform: `scale(${0.75 + 0.25 * sp})`}}>{p.en}</div>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 48, color: '#fff', marginTop: 10, textShadow: '0 4px 18px rgba(0,0,0,.9)'}}>{p.ko}</div>
    </div>
  );
};
const Captions: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const c = plan.captions.filter((c) => t >= c.s && t < c.e).pop();
  if (!c) return null;
  const o = fade(t, c.s, c.e, 0.12, 0.15);
  return (
    <div style={{position: 'absolute', bottom: 210, left: 60, right: 60, textAlign: 'center', opacity: o}}>
      {c.film ? <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 28, letterSpacing: '0.2em', color: GOLD, marginBottom: 8, textShadow: '0 2px 10px #000'}}>⚡ FILM ⚡</div> : null}
      <div style={{display: 'inline-block', padding: '14px 26px', borderRadius: 22, background: 'rgba(18,12,6,.62)', border: c.film ? `2px solid ${GOLD}` : '1px solid rgba(255,217,112,.35)'}}>
        <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 46, lineHeight: 1.2, color: '#fff', fontStyle: c.film ? 'italic' : 'normal'}}>{c.en}</div>
        <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 40, lineHeight: 1.25, color: GOLD_LIGHT, marginTop: 6, wordBreak: 'keep-all'}}>{c.ko}</div>
      </div>
    </div>
  );
};
const EndCard: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const {s, e} = plan.endCard;
  if (t < s - 0.6) return null;
  const o = interpolate(t, [s - 0.6, s], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: `rgba(10,7,4,${0.7 * o})`, justifyContent: 'center', alignItems: 'center', opacity: o}}>
      <div style={{background: '#F5F0E6', borderRadius: 48, padding: '40px 60px', boxShadow: `0 0 60px rgba(255,200,90,.5)`, border: `3px solid ${GOLD}`}}>
        <Img src={staticFile('day29/logo.png')} style={{width: 520}} />
      </div>
      <div style={{fontFamily: HP, fontSize: 112, color: GOLD, textShadow: glowText(), marginTop: 50, textAlign: 'center'}}>Happy Christmas</div>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 46, color: GOLD_LIGHT, marginTop: 6}}>옥스퍼드에서, 해피 크리스마스!</div>
    </AbsoluteFill>
  );
};

export const Day29Magic: React.FC<{plan: Day29Plan}> = ({plan}) => {
  useFonts();
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = f / fps;
  return (
    <AbsoluteFill style={{background: INK}}>
      <Hall src={plan.background} t={t} />
      <Clips plan={plan} t={t} />
      <Mark plan={plan} t={t} />
      <Sparkles plan={plan} t={t} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.45), transparent 22%, transparent 70%, rgba(0,0,0,.55))'}} />
      <DayChip />
      <Title plan={plan} t={t} />
      <PhraseCard plan={plan} t={t} />
      <Captions plan={plan} t={t} />
      <EndCard plan={plan} t={t} />
    </AbsoluteFill>
  );
};
