// Vertical Instagram promo cut from a landscape class video. Reels look from brand/BRAND.md (Pretendard, pastel words, soft shadows, punch zooms).
// The ending sends people to try Day 1 free instead of asking for a follow.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, staticFile, useCurrentFrame, useVideoConfig, Easing, spring} from 'remotion';

export type PromoPlan = {
  name: string; fps: number; duration: number; frames: number; speechEnd: number;
  segments: {src_s: number; src_e: number; out_s: number; cx: number}[];
  captions: {s: number; e: number; ko: string; hi: string; en: string; top?: number}[];
  pops: {s: number; e: number; small: string; big: string; tone: string; y: number}[];
  behind: {s: number; e: number; clip: string; trim: number; seg_s: number; seg_e: number; cx: number; l: string; r: string; size: number}[];
  punches: {s: number; e: number}[]; zooms: {t: number; z: number}[];
  hook: {small: string; big: string; e: number};
};
const C = {night: '#14203A', butter: '#F6F0BA', sky: '#AECCE6', white: '#FFFFFF', ink: '#14203A'};
const FF = "'Pretendard', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif";
const GRADE = 'contrast(1.1) saturate(1.16) brightness(1.02)';
const SHADOW = '0 3px 8px rgba(10,16,30,.8), 0 0 26px rgba(10,16,30,.55), 0 10px 40px rgba(10,16,30,.4)';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const SCALE = 1920 / 1080;
const tone = (k: string) => (k === 'sky' ? C.sky : C.butter);

const FONTS: [string, string][] = [['700', 'Pretendard-Bold.woff2'], ['800', 'Pretendard-ExtraBold.woff2'], ['900', 'Pretendard-Black.woff2']];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([w, file]) => new FontFace('Pretendard', `url(${staticFile('fonts/' + file)})`, {weight: w}).load().then((x) => document.fonts.add(x))))
      .then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
  }, [h]);
};
const frameStyle = (cx: number): React.CSSProperties => ({position: 'absolute', top: 0, left: 540 - cx * SCALE, width: 1920 * SCALE, height: 1920, maxWidth: 'none', filter: GRADE});

const usePop = (t: number, s: number, e: number) => {
  const {fps} = useVideoConfig();
  const k = spring({frame: Math.round((t - s) * fps), fps, config: {damping: 9, stiffness: 180, mass: .6}});
  const out = interpolate(t, [e - .15, e], [1, 0], clamp);
  return {k, opacity: Math.min(1, k * 3) * out};
};

const Caption: React.FC<{c: PromoPlan['captions'][0]; t: number}> = ({c, t}) => {
  const o = interpolate(t, [c.s, c.s + .08, c.e - .06, c.e], [0, 1, 1, 0], clamp);
  const parts = c.hi ? c.ko.split(c.hi) : [c.ko];
  const words = c.en ? c.en.split(' ') : [];
  const n = words.join('').length || 1; const p = interpolate(t, [c.s + .1, Math.min(c.e, c.s + 1.8)], [0, 1], clamp) * n;
  let acc = 0;
  return (
    <div style={{position: 'absolute', left: c.top ? 130 : 60, right: c.top ? 170 : 110, top: c.top ?? 1160, textAlign: 'center', opacity: o, fontFamily: FF, textShadow: c.top ? 'none' : SHADOW, wordBreak: 'keep-all', ...(c.top ? {background: 'rgba(30,45,77,.88)', borderRadius: 28, padding: '18px 22px'} : {})}}>
      {c.en ? <div style={{fontWeight: 900, fontSize: c.top ? 76 : 92, lineHeight: 1.1, letterSpacing: '-.02em', marginBottom: c.top ? 6 : 14}}>
        {words.map((w, i) => { const lit = p >= acc; acc += w.length; return <span key={i} style={{color: lit ? C.sky : C.white}}>{w}{i < words.length - 1 ? ' ' : ''}</span>; })}
      </div> : null}
      <div style={{fontWeight: 800, fontSize: c.top ? 52 : c.en ? 62 : 66, lineHeight: 1.3, color: C.white}}>
        {parts.map((x, i) => <React.Fragment key={i}>{x}{i < parts.length - 1 ? <span style={{color: C.butter}}>{c.hi}</span> : null}</React.Fragment>)}
      </div>
    </div>
  );
};

const Pop: React.FC<{ev: PromoPlan['pops'][0]; t: number}> = ({ev, t}) => {
  const {k, opacity} = usePop(t, ev.s, ev.e);
  return (
    <div style={{position: 'absolute', left: 60, right: 110, top: ev.y, textAlign: 'center', opacity, transform: `scale(${.4 + .6 * k})`, fontFamily: FF, textShadow: SHADOW}}>
      {ev.small ? <div style={{color: C.white, fontWeight: 700, fontSize: 56}}>{ev.small}</div> : null}
      <div style={{color: tone(ev.tone), fontWeight: 900, fontSize: 150, lineHeight: 1.05, letterSpacing: '-.03em'}}>{ev.big}</div>
    </div>
  );
};

const Hook: React.FC<{h: PromoPlan['hook']; t: number}> = ({h, t}) => {
  const {k, opacity} = usePop(t, 0, h.e);
  return (
    <div style={{position: 'absolute', left: 50, right: 100, top: 880, textAlign: 'center', opacity, transform: `scale(${.6 + .4 * k})`, fontFamily: FF, textShadow: SHADOW, wordBreak: 'keep-all'}}>
      <div style={{color: C.white, fontWeight: 800, fontSize: 68}}>{h.small}</div>
      <div style={{color: C.butter, fontWeight: 900, fontSize: 128, lineHeight: 1.08, letterSpacing: '-.03em'}}>{h.big}</div>
    </div>
  );
};

const Top: React.FC<{plan: PromoPlan; t: number}> = ({plan, t}) => {
  const p = interpolate(t, [0, plan.speechEnd], [0, 1], clamp);
  return (
    <>
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 12, background: 'rgba(20,32,58,.3)'}}>
        <div style={{height: '100%', width: `${p * 100}%`, background: C.butter}} />
        <Img src={staticFile('brand/bear-butterfly.png')} style={{position: 'absolute', left: `calc(${p * 100}% - 48px)`, top: 12, height: 90, transform: `translateY(${Math.abs(Math.sin(t * 5)) * 4}px)`}} />
      </div>
      <div style={{position: 'absolute', right: 40, top: 150, background: C.butter, color: C.ink, fontFamily: FF, fontWeight: 800, fontSize: 36, padding: '10px 26px', borderRadius: 99, boxShadow: '0 8px 24px rgba(10,16,30,.25)'}}>🐾 Little Steps · 첫날 무료</div>
    </>
  );
};

const End: React.FC<{plan: PromoPlan; t: number}> = ({plan, t}) => {
  const {fps} = useVideoConfig();
  const s = plan.speechEnd;
  const bg = interpolate(t, [s - .05, s + .3], [0, 1], clamp);
  const sp = (d: number, damping = 11) => spring({frame: Math.round((t - s - d) * fps), fps, config: {damping, stiffness: 170}});
  const top = sp(.1), l1 = sp(.5, 9), l2 = sp(.7, 9), row = sp(1.2), btn = sp(1.6, 8), url = sp(2);
  const pulse = 1 + .03 * Math.sin((t - s) * 7);
  return (
    <AbsoluteFill style={{background: `rgba(20,32,58,${.96 * bg})`, display: 'grid', placeContent: 'center', justifyItems: 'center', gap: 24, textAlign: 'center', padding: '0 70px', fontFamily: FF}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 16, opacity: top, transform: `translateY(${(1 - top) * 24}px)`}}>
        <Img src={staticFile('brand/bear-butterfly.png')} style={{width: 200, transform: `translateY(${Math.sin(t * 4) * 6}px)`}} />
        <Img src={staticFile('brand/wordmark-cream.png')} style={{width: 540}} />
      </div>
      <div style={{fontWeight: 900, fontSize: 132, lineHeight: 1.08, letterSpacing: '-.04em', textShadow: SHADOW, marginTop: 20}}>
        <div style={{color: C.butter, transform: `scale(${l1})`}}>1일차는</div>
        <div style={{color: C.sky, transform: `scale(${l2})`}}>무료예요!</div>
      </div>
      <div style={{opacity: row, transform: `translateY(${(1 - row) * 20}px)`, display: 'grid', justifyItems: 'center', gap: 16, marginTop: 10}}>
        <div style={{color: C.white, fontWeight: 800, fontSize: 50}}>워크시트 · 인터랙티브 게임</div>
        <div style={{display: 'flex', alignItems: 'center', gap: 18, color: C.white, fontWeight: 800, fontSize: 50}}>
          <Img src={staticFile('brand/mark-avatar.png')} style={{width: 92, height: 92}} />마크와 조이의 도움까지
        </div>
      </div>
      <div style={{marginTop: 26, background: C.sky, color: C.ink, fontWeight: 900, fontSize: 70, padding: '30px 66px', borderRadius: 999, transform: `scale(${btn * pulse})`, boxShadow: '0 16px 40px rgba(0,0,0,.35)'}}>1일차 무료로 시작하기</div>
      <div style={{color: C.white, fontWeight: 700, fontSize: 44, opacity: url}}>bearandjoy.com/littlesteps</div>
    </AbsoluteFill>
  );
};

export const BearJoyPromo: React.FC<{plan: PromoPlan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  let z = 1, prev = 1, since = 99;
  for (const k of plan.zooms) if (k.t <= t) { prev = z; z = k.z; since = t - k.t; }
  z = prev + (z - prev) * interpolate(since, [0, .12], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  for (const p of plan.punches) if (t >= p.s && t <= p.e + .3) z *= 1 + .06 * interpolate(t, [p.s, p.s + .06, p.e + .3], [0, 1, 0], clamp);
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const main = t < plan.speechEnd + .4;
  return (
    <AbsoluteFill style={{background: C.night}}>
      <div style={{position: 'absolute', inset: 0, transform: `scale(${z})`, transformOrigin: '50% 30%', overflow: 'hidden'}}>
        {plan.segments.map((g, i) => (
          <Sequence key={i} from={Math.round(g.out_s * fps)} durationInFrames={Math.round((g.src_e - g.src_s) * fps) + (i === plan.segments.length - 1 ? 15 : 0)} layout="none">
            <AbsoluteFill><OffthreadVideo src={staticFile('day1/source.mov')} muted trimBefore={Math.round(g.src_s * fps)} style={frameStyle(g.cx)} /></AbsoluteFill>
          </Sequence>
        ))}
        {plan.behind.map((b, i) => {
          if (t < b.s - .05 || t > b.e + .1) return null;
          const k = spring({frame: Math.round((t - b.s) * fps), fps, config: {damping: 9, stiffness: 170, mass: .6}});
          const word = (txt: string, side: 'left' | 'right') => <div style={{position: 'absolute', top: 210, [side]: 18, color: side === 'left' ? C.butter : C.sky, fontFamily: FF, fontWeight: 900, fontSize: b.size, lineHeight: 1, letterSpacing: '-.04em', textShadow: SHADOW, transform: `scale(${.5 + .5 * k})`, opacity: Math.min(1, k * 3)}}>{txt}</div>;
          return <React.Fragment key={i}>{word(b.l, 'left')}{word(b.r, 'right')}</React.Fragment>;
        })}
        {plan.behind.map((b, i) => (
          <Sequence key={`m${i}`} from={Math.round(b.seg_s * fps)} durationInFrames={Math.round((b.seg_e - b.seg_s) * fps)} layout="none">
            <AbsoluteFill style={{opacity: t >= b.s - .05 && t <= b.e + .1 ? 1 : 0}}><OffthreadVideo src={staticFile(`day1/${b.clip}.webm`)} transparent muted trimBefore={b.trim} style={frameStyle(b.cx)} /></AbsoluteFill>
          </Sequence>
        ))}
      </div>
      {main && !cap?.top ? <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,16,30,0) 52%, rgba(10,16,30,.42) 66%, rgba(10,16,30,.5) 82%, rgba(10,16,30,.2) 100%)'}} /> : null}
      {main ? <Top plan={plan} t={t} /> : null}
      {t < plan.hook.e ? <Hook h={plan.hook} t={t} /> : null}
      {plan.pops.map((p, i) => (t >= p.s - .05 && t <= p.e + .05 ? <Pop key={i} ev={p} t={t} /> : null))}
      {cap && t < plan.speechEnd ? <Caption c={cap} t={t} /> : null}
      {t >= plan.speechEnd - .1 ? <End plan={plan} t={t} /> : null}
    </AbsoluteFill>
  );
};
