// Day 29 — "5 Harry Potter phrases" (one-off Harry Potter look, owner 11 Nov 2026; see brand/BRAND.md "Harry Potter episodes").
// Mark (matte) in front of the Great Hall with a pulsing gold outline. After he finishes a sentence, a full-screen
// "magic cut" (gold flash + sparkle burst) goes to the film scene, captioned in the Harry Potter font (EN) and
// Gowun Batang (KO), then cuts back. Plan: projects/2026-11-day29-christmas-phrases/build_plan.py. Audio: mix.py.
import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, spring,
  staticFile, useCurrentFrame, useVideoConfig, Easing, random,
} from 'remotion';

type Seg = {kind: 'mark' | 'film'; s: number; e: number; src: number | string; srcEnd?: number;
  clip?: string; clipIn?: number; clipOut?: number; lineS?: number; en?: string; ko?: string};
type Cap = {s: number; e: number; en: string; ko: string};
type Phrase = {s: number; n: number; en: string; ko: string};
export type Day29Plan = {
  name: string; fps: number; duration: number; frames: number; day: number;
  subject: string; background: string; props: string; propsFrom: number; propsUntil: number;
  title: {s: number; e: number; en: string; sub: string; ko: string};
  segments: Seg[]; captions: Cap[]; phrases: Phrase[]; endCard: {s: number; e: number};
};

const GOLD = '#FFD970', GOLD_LIGHT = '#FFF4C8', INK = '#120C06';
const HP = "'HarryP', serif";
const PRE = "'Pretendard', sans-serif";
const KO_SERIF = "'Gowun Batang', 'Pretendard', serif";
const FONTS: [string, string, string][] = [
  ['HarryP', '400', 'HarryP.ttf'],
  ['Pretendard', '700', 'Pretendard-Bold.woff2'],
  ['Pretendard', '800', 'Pretendard-ExtraBold.woff2'],
  ['Pretendard', '900', 'Pretendard-Black.woff2'],
  ['Gowun Batang', '700', 'ijwNs5nhRMIjYsdSgcMa3wRZ4J7awg.ttf'],
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
const films = (p: Day29Plan) => p.segments.filter((s) => s.kind === 'film');
const inFilm = (p: Day29Plan, t: number) => films(p).some((s) => t >= s.s && t < s.e);

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

// ── Mark with the magic outline ──
const Mark: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const {fps} = useVideoConfig();
  // outline flares into each magic cut and settles after coming back
  const flare = films(plan).reduce((m, s) => Math.max(m, interpolate(t, [s.s - 0.5, s.s, s.e, s.e + 0.7], [0, 1, 1, 0], clamp)), 0);
  const pulse = 0.5 + 0.5 * Math.sin(t * Math.PI);
  const line = 2.2 + pulse * 0.8 + flare * 1.6, halo = 22 + pulse * 8 + flare * 26;
  const glow = `drop-shadow(0 0 ${line}px ${GOLD_LIGHT}) drop-shadow(0 0 ${line}px ${GOLD_LIGHT}) drop-shadow(0 0 ${halo}px ${GOLD}) drop-shadow(0 0 ${halo * 1.8}px rgba(255,170,60,${0.35 + flare * 0.3}))`;
  const propsFrame = Math.round((t + plan.propsFrom) * fps);
  return (
    <AbsoluteFill style={{filter: glow}}>
      {plan.segments.filter((s) => s.kind === 'mark').map((s, i) => (
        <Sequence key={i} from={Math.round(s.s * fps)} durationInFrames={Math.max(1, Math.round((s.e - s.s) * fps))} layout="none">
          <AbsoluteFill>
            <OffthreadVideo src={staticFile(plan.subject)} transparent muted startFrom={Math.round((s.src as number) * fps)} style={{width: '100%', height: '100%'}} />
          </AbsoluteFill>
        </Sequence>
      ))}
      {t < plan.propsUntil ? (
        <Img src={staticFile(`${plan.props}/${String(propsFrame).padStart(4, '0')}.png`)}
          style={{position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: fade(t, 0, plan.propsUntil, 0.2, 0.35)}} />
      ) : null}
    </AbsoluteFill>
  );
};

// ── Full-screen magic cut to the film scene ──
const FilmCut: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const {fps} = useVideoConfig();
  return <>{films(plan).map((s, i) => {
    if (t < s.s - 0.05 || t > s.e + 0.05) return null;
    const pin = interpolate(t, [s.s, s.s + 0.3], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
    const pout = interpolate(t, [s.e - 0.25, s.e], [0, 1], {...clamp, easing: Easing.in(Easing.cubic)});
    const blur = (1 - pin) * 14 + pout * 14;
    const zoom = 1.08 - 0.08 * pin + 0.06 * pout;
    const capO = fade(t, s.lineS! - 0.1, s.e - 0.15, 0.2, 0.2);
    return (
      <Sequence key={i} from={Math.round(s.s * fps)} durationInFrames={Math.round((s.e - s.s) * fps)} layout="none">
        <AbsoluteFill style={{opacity: Math.min(1, pin * 3)}}>
          <AbsoluteFill style={{background: '#000'}} />
          {/* blurred fill of the same scene behind the letterboxed clip */}
          <OffthreadVideo src={staticFile(s.src as string)} muted startFrom={Math.round((s.clipIn! - 0.32) * fps)}
            style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'cover', filter: 'blur(28px) brightness(.45) saturate(1.2)', transform: 'scale(1.15)'}} />
          <div style={{position: 'absolute', left: 0, right: 0, top: 560, display: 'flex', justifyContent: 'center',
            transform: `scale(${zoom})`, filter: `blur(${blur}px)`}}>
            <div style={{width: 1080, border: `3px solid ${GOLD}`, borderLeft: 'none', borderRight: 'none', boxShadow: `0 0 40px rgba(255,200,90,.45)`}}>
              <OffthreadVideo src={staticFile(s.src as string)} muted startFrom={Math.round((s.clipIn! - 0.32) * fps)}
                style={{width: '100%', display: 'block'}} />
            </div>
          </div>
          <div style={{position: 'absolute', left: 50, right: 50, top: 1240, textAlign: 'center', opacity: capO,
            transform: `translateY(${(1 - capO) * 14}px)`}}>
            <div style={{fontFamily: HP, fontSize: s.en!.length > 30 ? 74 : 96, lineHeight: 1.05, color: GOLD, textShadow: glowText()}}>{s.en}</div>
            <div style={{fontFamily: KO_SERIF, fontWeight: 700, fontSize: 54, lineHeight: 1.3, color: GOLD_LIGHT, marginTop: 18,
              textShadow: '0 0 14px rgba(255,200,90,.6), 0 4px 16px rgba(0,0,0,.9)', wordBreak: 'keep-all'}}>{s.ko}</div>
          </div>
        </AbsoluteFill>
      </Sequence>
    );
  })}</>;
};

// gold flash at each magic cut (in and out)
const Flash: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const a = films(plan).reduce((m, s) => Math.max(m,
    interpolate(t, [s.s - 0.12, s.s, s.s + 0.22], [0, 0.85, 0], clamp),
    interpolate(t, [s.e - 0.12, s.e, s.e + 0.22], [0, 0.75, 0], clamp)), 0);
  if (a <= 0) return null;
  return <AbsoluteFill style={{background: `radial-gradient(circle at 50% 45%, rgba(255,248,220,${a}), rgba(255,200,90,${a * 0.6}) 45%, rgba(255,170,60,${a * 0.15}) 80%)`}} />;
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
  const dust = inFilm(plan, t) ? 0.35 : 1;
  for (let i = 0; i < 46; i++) {
    const off = random(`o${i}`) * LIFE, cyc = Math.floor((t + off) / LIFE), ph = ((t + off) % LIFE) / LIFE;
    const side = random(`s${i}-${cyc}`) < 0.5 ? -1 : 1;
    const x = 540 + side * (170 + random(`x${i}-${cyc}`) * 330), y = 1750 - random(`y${i}-${cyc}`) * 1150 - ph * 220;
    stars.push(<Star key={`d${i}`} x={x + Math.sin(ph * 6 + i) * 12} y={y} r={4 + random(`r${i}`) * 9} o={Math.sin(ph * Math.PI) * 0.9 * dust} rot={ph * 90} />);
  }
  const bursts = [0.02, plan.propsUntil - 0.3, ...films(plan).flatMap((s) => [s.s - 0.05, s.e - 0.05])];
  bursts.forEach((b, k) => {
    const p = (t - b) / 1.0;
    if (p < 0 || p > 1) return;
    const cx = 540, cy = k < 2 ? 640 : 860;
    for (let i = 0; i < 30; i++) {
      const a = random(`ba${k}-${i}`) * Math.PI * 2, d = (180 + random(`bd${k}-${i}`) * 380) * Easing.out(Easing.cubic)(p);
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
      <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 40, color: '#fff', marginTop: 14, textShadow: '0 4px 18px rgba(0,0,0,.9)'}}>{sub}</div>
      <div style={{fontFamily: KO_SERIF, fontWeight: 700, fontSize: 46, color: GOLD_LIGHT, marginTop: 8, textShadow: '0 4px 18px rgba(0,0,0,.9)', wordBreak: 'keep-all'}}>{ko}</div>
    </div>
  );
};
const PhraseCard: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const {fps} = useVideoConfig();
  const last = plan.endCard.s - 4.8;
  const i = plan.phrases.findIndex((p, k) => t >= p.s && t < (plan.phrases[k + 1]?.s ?? last));
  if (i < 0) return null;
  const p = plan.phrases[i], e = plan.phrases[i + 1]?.s ?? last;
  const sp = spring({frame: Math.round((t - p.s) * fps), fps, config: {damping: 10, stiffness: 140}});
  return (
    <div style={{position: 'absolute', top: 175, left: 30, right: 30, textAlign: 'center', opacity: fade(t, p.s, e, 0.15, 0.3)}}>
      <div style={{fontFamily: HP, fontSize: 92, color: GOLD_LIGHT, textShadow: glowText(), transform: `scale(${0.6 + 0.4 * sp})`}}>No. {p.n}</div>
      <div style={{fontFamily: HP, fontSize: p.en.length > 12 ? 128 : 160, lineHeight: 0.95, color: GOLD, textShadow: glowText(), transform: `scale(${0.75 + 0.25 * sp})`}}>{p.en}</div>
      <div style={{fontFamily: KO_SERIF, fontWeight: 700, fontSize: 50, color: '#fff', marginTop: 10, textShadow: '0 4px 18px rgba(0,0,0,.9)'}}>{p.ko}</div>
    </div>
  );
};
const Captions: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const c = plan.captions.filter((c) => t >= c.s && t < c.e).pop();
  if (!c) return null;
  return (
    <div style={{position: 'absolute', bottom: 210, left: 60, right: 60, textAlign: 'center', opacity: fade(t, c.s, c.e, 0.12, 0.15)}}>
      <div style={{display: 'inline-block', padding: '14px 26px', borderRadius: 22, background: 'rgba(18,12,6,.62)', border: '1px solid rgba(255,217,112,.35)'}}>
        <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 46, lineHeight: 1.2, color: '#fff'}}>{c.en}</div>
        <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 40, lineHeight: 1.25, color: GOLD_LIGHT, marginTop: 6, wordBreak: 'keep-all'}}>{c.ko}</div>
      </div>
    </div>
  );
};
const EndCard: React.FC<{plan: Day29Plan; t: number}> = ({plan, t}) => {
  const {s} = plan.endCard;
  if (t < s - 0.6) return null;
  const o = interpolate(t, [s - 0.6, s], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: `rgba(10,7,4,${0.7 * o})`, justifyContent: 'center', alignItems: 'center', opacity: o}}>
      <div style={{background: '#F5F0E6', borderRadius: 48, padding: '40px 60px', boxShadow: `0 0 60px rgba(255,200,90,.5)`, border: `3px solid ${GOLD}`}}>
        <Img src={staticFile('day29/logo.png')} style={{width: 520}} />
      </div>
      <div style={{fontFamily: HP, fontSize: 112, color: GOLD, textShadow: glowText(), marginTop: 50, textAlign: 'center'}}>Happy Christmas</div>
      <div style={{fontFamily: KO_SERIF, fontWeight: 700, fontSize: 48, color: GOLD_LIGHT, marginTop: 6}}>옥스퍼드에서, 해피 크리스마스!</div>
    </AbsoluteFill>
  );
};

export const Day29Magic: React.FC<{plan: Day29Plan}> = ({plan}) => {
  useFonts();
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = f / fps;
  const film = inFilm(plan, t);
  return (
    <AbsoluteFill style={{background: INK}}>
      <Hall src={plan.background} t={t} />
      <Mark plan={plan} t={t} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.45), transparent 22%, transparent 70%, rgba(0,0,0,.55))'}} />
      <FilmCut plan={plan} t={t} />
      <Sparkles plan={plan} t={t} />
      <DayChip />
      {film ? null : <><Title plan={plan} t={t} /><PhraseCard plan={plan} t={t} /><Captions plan={plan} t={t} /></>}
      <EndCard plan={plan} t={t} />
      <Flash plan={plan} t={t} />
    </AbsoluteFill>
  );
};
