// The Bear & Joy Co. reel template. Follows brand/BRAND.md (approved 4 Nov 2026).
// Layers, back to front: graded footage -> word behind head -> graded cutout of the speaker
// -> grain + vignette -> watermark, captions, tag, card -> end card.
import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate,
  staticFile, useCurrentFrame, useVideoConfig, Easing, random,
} from 'remotion';

export type Caption = {i: number; s: number; e: number; ko: string; en: string; hi: string; demo: boolean};
export type Ev = {type: string; s: number; e: number; [k: string]: any};
export type Plan = {
  name: string; fps: number; duration: number; frames: number; speechEnd: number;
  captions: Caption[]; events: Ev[]; zooms: {t: number; z: number}[];
};

const C = {night: '#1E2D4D', deep: '#173B5C', gold: '#C9A84C', goldHi: '#E7CC7E', cream: '#F5F0E6', kakao: '#FEE500'};
const PLAYFAIR = "'Playfair Display', Georgia, serif";
const GOWUN = "'Gowun Batang', serif";
const NOTO = "'Noto Sans KR', sans-serif";
// Warm storybook grade, applied identically to footage and cutout so they always match.
const GRADE = 'contrast(1.07) saturate(0.9) sepia(0.1) brightness(1.02) hue-rotate(-4deg)';

const FONT_FILES: [string, string, string, string][] = [
  ['Gowun Batang', 'normal', '400', 'ijwSs5nhRMIjYsdSgcMa3wRhXA.ttf'],
  ['Gowun Batang', 'normal', '700', 'ijwNs5nhRMIjYsdSgcMa3wRZ4J7awg.ttf'],
  ['Noto Sans KR', 'normal', '500', 'PbyxFmXiEBPT4ITbgNA5Cgms3VYcOA-vvnIzztgyeLQ.ttf'],
  ['Noto Sans KR', 'normal', '700', 'PbyxFmXiEBPT4ITbgNA5Cgms3VYcOA-vvnIzzg01eLQ.ttf'],
  ['Playfair Display', 'italic', '400', 'nuFRD-vYSZviVYUb_rj3ij__anPXDTnCjmHKM4nYO7KN_qiTbtY.ttf'],
  ['Playfair Display', 'italic', '600', 'nuFRD-vYSZviVYUb_rj3ij__anPXDTnCjmHKM4nYO7KN_naUbtY.ttf'],
  ['Playfair Display', 'normal', '600', 'nuFvD-vYSZviVYUb_rj3ij__anPXJzDwcbmjWBN2PKebukDQ.ttf'],
  ['Playfair Display', 'normal', '700', 'nuFvD-vYSZviVYUb_rj3ij__anPXJzDwcbmjWBN2PKeiukDQ.ttf'],
];

const useFonts = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONT_FILES.map(([family, style, weight, file]) => {
      const f = new FontFace(family, `url(${staticFile('fonts/' + file)})`, {style, weight});
      return f.load().then((loaded) => document.fonts.add(loaded));
    })).then(() => continueRender(handle)).catch((e) => { console.error(e); continueRender(handle); });
  }, [handle]);
};

const ease = Easing.bezier(0.22, 1, 0.36, 1);
// 0 -> 1 over `inD` seconds after s, 1 -> 0 over `outD` seconds before e.
const life = (t: number, s: number, e: number, inD = 0.4, outD = 0.25) =>
  Math.min(interpolate(t, [s, s + inD], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease}),
    interpolate(t, [e - outD, e], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}));

const zoomAt = (plan: Plan, t: number) => {
  let z = 1;
  for (const k of plan.zooms) if (k.t <= t + 1e-6) z = k.z;
  for (const ev of plan.events) {
    if (ev.type !== 'zoom' || t < ev.s || t > ev.e) continue;
    z = ev.snap ? ev.to : interpolate(t, [ev.s, ev.e], [ev.from, ev.to], {easing: Easing.inOut(Easing.quad)});
  }
  return z;
};

const Highlight: React.FC<{text: string; hi: string}> = ({text, hi}) => {
  const i = hi ? text.indexOf(hi) : -1;
  if (i < 0) return <>{text}</>;
  return <>{text.slice(0, i)}<span style={{color: C.goldHi}}>{hi}</span>{text.slice(i + hi.length)}</>;
};

const CaptionView: React.FC<{c: Caption; t: number}> = ({c, t}) => {
  const a = life(t, c.s, c.e, 0.18, 0.12);
  const rise = (1 - a) * 18;
  const shadow = '0 3px 0 rgba(30,45,77,.9), 0 0 26px rgba(30,45,77,.75)';
  return (
    <div style={{position: 'absolute', left: 70, right: 70, top: c.demo ? 1180 : 1210, textAlign: 'center', display: 'grid', gap: 14,
      opacity: a, transform: `translateY(${rise}px) rotate(${c.demo ? -2 : 0}deg) scale(${c.demo ? interpolate(a, [0, 1], [0.9, 1]) : 1})`}}>
      <div style={{fontFamily: GOWUN, fontWeight: 700, fontSize: c.demo ? 84 : 64, lineHeight: 1.25, color: C.cream, textShadow: shadow,
        wordBreak: 'keep-all', textWrap: 'balance' as any}}>
        <Highlight text={c.ko} hi={c.hi} />
      </div>
      {c.en && !c.demo ? <div style={{fontFamily: PLAYFAIR, fontStyle: 'italic', fontWeight: 400, fontSize: 40, lineHeight: 1.25, color: C.gold,
        textShadow: '0 2px 12px rgba(30,45,77,.9)'}}>{c.en}</div> : null}
    </div>
  );
};

const Behind: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const a = life(t, ev.s, ev.e, 0.45, 0.3);
  return (
    <>
      {ev.eyebrow ? <div style={{position: 'absolute', left: '50%', top: ev.top - 80, transform: `translateX(-50%) translateY(${(1 - a) * 12}px)`,
        opacity: a, whiteSpace: 'nowrap', fontFamily: PLAYFAIR, fontWeight: 600, fontSize: 28, letterSpacing: '.2em', color: C.gold,
        textTransform: 'uppercase', background: 'rgba(30,45,77,.82)', padding: '14px 26px', borderRadius: 999}}>Bear &amp; Joy · Little Steps</div> : null}
      <div style={{position: 'absolute', left: 0, right: 0, top: ev.top, textAlign: 'center', color: C.night, fontFamily: PLAYFAIR,
        fontStyle: ev.style === 'italic' ? 'italic' : 'normal', fontWeight: ev.style === 'italic' ? 600 : 700, fontSize: ev.size, lineHeight: 1,
        opacity: a, transform: `translateY(${(1 - a) * 60}px)`, textShadow: '0 0 40px rgba(245,240,230,.55)', whiteSpace: 'nowrap'}}>{ev.text}</div>
    </>
  );
};

const Tag: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const a = life(t, ev.s, ev.e, 0.4, 0.3);
  return (
    <div style={{position: 'absolute', left: 60, top: 250, opacity: a, transform: `translateX(${(1 - a) * -40}px)`, display: 'grid', gap: 12, justifyItems: 'start'}}>
      <div style={{background: 'rgba(30,45,77,.86)', border: '2px solid rgba(201,168,76,.6)', borderRadius: 22, padding: '18px 28px', display: 'grid', gap: 6}}>
        <span style={{fontFamily: PLAYFAIR, fontWeight: 700, fontSize: 46, color: C.cream, lineHeight: 1}}>{ev.name}</span>
        <span style={{fontFamily: GOWUN, fontWeight: 700, fontSize: 30, color: C.gold, lineHeight: 1.2}}>{ev.role}</span>
      </div>
      <span style={{fontFamily: PLAYFAIR, fontStyle: 'italic', fontSize: 32, color: C.cream, textShadow: '0 2px 10px rgba(30,45,77,.9)'}}>{ev.line}</span>
    </div>
  );
};

const Card: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const a = life(t, ev.s, ev.e, 0.4, 0.3);
  return (
    <div style={{position: 'absolute', left: 70, right: 150, top: 280, background: 'rgba(30,45,77,.86)', border: '2px solid rgba(201,168,76,.5)',
      borderRadius: 28, padding: '34px 38px', display: 'grid', gap: 18, color: C.cream, opacity: a, transform: `translateY(${(1 - a) * 16}px)`}}>
      <span style={{justifySelf: 'start', fontFamily: PLAYFAIR, fontWeight: 600, fontSize: 24, letterSpacing: '.16em', color: C.gold,
        border: '2px solid rgba(201,168,76,.7)', padding: '12px 18px', borderRadius: 999, textTransform: 'uppercase'}}>The first little step · 첫걸음</span>
      {ev.rows.map((r: any, k: number) => {
        const on = r.t !== null && t >= r.t;
        const ra = interpolate(t, [ev.s + 0.2 + k * 0.08, ev.s + 0.5 + k * 0.08], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const tick = r.t === null ? 0 : interpolate(t, [r.t, r.t + 0.2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.back(2))});
        return (
          <div key={k} style={{display: 'flex', alignItems: 'baseline', gap: 18, borderTop: '1px solid rgba(245,240,230,.14)', paddingTop: 16,
            opacity: ra * (on ? 1 : 0.55), fontFamily: GOWUN, fontWeight: 700, fontSize: 44}}>
            {r.ko} <i style={{fontFamily: PLAYFAIR, fontWeight: 400, fontSize: 30, color: 'rgba(245,240,230,.7)', flex: 1}}>{r.en}</i>
            <b style={{color: C.gold, fontFamily: NOTO, fontSize: 36, display: 'inline-block', transform: `scale(${tick})`}}>✓</b>
          </div>
        );
      })}
    </div>
  );
};

const EndCard: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const bg = interpolate(t, [ev.s, ev.s + 0.7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const step = (d: number) => interpolate(t, [ev.s + d, ev.s + d + 0.6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
  const art = step(0.5), wm = step(1.0), line = step(1.4), btn = step(1.8);
  const drift = Math.sin((t - ev.s) * 1.6) * 6;
  return (
    <AbsoluteFill style={{background: `linear-gradient(rgba(30,45,77,${0.6 * bg}), rgba(22,34,60,${0.96 * bg}) 45%)`,
      display: 'grid', placeContent: 'center', justifyItems: 'center', gap: 40, padding: '0 90px', textAlign: 'center'}}>
      <Img src={staticFile('brand/bear-butterfly.png')} style={{width: 520, opacity: art, transform: `translateY(${(1 - art) * 30 + drift}px)`}} />
      <Img src={staticFile('brand/wordmark-cream.png')} style={{width: 860, opacity: wm, transform: `translateY(${(1 - wm) * 20}px)`}} />
      <div style={{fontFamily: GOWUN, fontSize: 50, lineHeight: 1.4, color: C.cream, opacity: line}}>
        <i style={{fontFamily: PLAYFAIR, fontStyle: 'italic', fontSize: 54, color: C.gold, display: 'block', marginBottom: 14}}>Little Steps,</i>여기서 시작해요.
      </div>
      <div style={{fontFamily: NOTO, fontWeight: 700, fontSize: 38, background: C.kakao, color: '#191600', padding: '26px 46px', borderRadius: 999,
        opacity: btn, transform: `scale(${interpolate(btn, [0, 1], [0.92, 1])})`}}>카카오톡 채널 추가하기</div>
    </AbsoluteFill>
  );
};

const Grain: React.FC<{frame: number}> = ({frame}) => {
  const seed = Math.floor(random(`g${frame}`) * 1000);
  return (
    <svg width="1080" height="1920" style={{position: 'absolute', inset: 0, opacity: 0.07, mixBlendMode: 'overlay'}}>
      <filter id={`n${frame}`}><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={seed} stitchTiles="stitch" /><feColorMatrix type="saturate" values="0" /></filter>
      <rect width="100%" height="100%" filter={`url(#n${frame})`} />
    </svg>
  );
};

export const BearJoyReel: React.FC<{plan: Plan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const z = zoomAt(plan, t);
  const dir = `confidence/${plan.name}`;
  const behind = plan.events.filter((e) => e.type === 'behind');
  const tag = plan.events.find((e) => e.type === 'tag');
  const card = plan.events.find((e) => e.type === 'card');
  const end = plan.events.find((e) => e.type === 'end')!;
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const topBusy = [tag, card].some((e) => e && t > e.s - 0.3 && t < e.e + 0.3) || t > end.s;
  const cam: React.CSSProperties = {position: 'absolute', inset: 0, transform: `scale(${z})`, transformOrigin: '50% 36%'};
  const vid: React.CSSProperties = {width: '100%', height: '100%', objectFit: 'cover', filter: GRADE};
  return (
    <AbsoluteFill style={{background: C.night}}>
      <div style={cam}>
        <OffthreadVideo src={staticFile(`${dir}/cut.mov`)} muted style={vid} />
        {behind.map((ev, k) => (t >= ev.s - 0.1 && t <= ev.e + 0.1 ? <Behind key={k} ev={ev} t={t} /> : null))}
        {behind.map((ev, k) => {
          const from = Math.max(0, Math.floor((ev.s - 0.2) * fps));
          const to = Math.ceil((ev.e + 0.2) * fps);
          return (
            <Sequence key={`m${k}`} from={from} durationInFrames={to - from} layout="none">
              <AbsoluteFill><OffthreadVideo src={staticFile(`${dir}/matte.webm`)} transparent muted trimBefore={from} style={vid} /></AbsoluteFill>
            </Sequence>
          );
        })}
      </div>
      {/* vignette + grain */}
      <AbsoluteFill style={{background: 'radial-gradient(120% 80% at 50% 42%, rgba(0,0,0,0) 55%, rgba(30,45,77,.38) 100%)'}} />
      <Grain frame={frame} />
      <Img src={staticFile('brand/bear-butterfly.png')} style={{position: 'absolute', left: 46, top: 232, width: 110,
        opacity: interpolate(topBusy ? 0 : 1, [0, 1], [0, 0.6])}} />
      {tag ? <Tag ev={tag} t={t} /> : null}
      {card ? <Card ev={card} t={t} /> : null}
      {cap && t < end.s ? <CaptionView c={cap} t={t} /> : null}
      {t >= end.s ? <EndCard ev={end} t={t} /> : null}
    </AbsoluteFill>
  );
};
