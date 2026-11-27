// DAY 41 "엄마가 영어를 못하는데, 엄마표 영어요?" (Joy, 27 Nov 2026). Joy's talking head full frame (pauses trimmed), captions at chest
// height (not on her face), a question hook, and her screen recording of the free resource in a rounded card while she talks about it
// (her reference: the hailey_ourhabit reel), then an emoji-comment CTA. All text in y 300–1450; DAY chip + yellow progress bar.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import plan from './day41.json';

const NAVY = '#14305C', YEL = '#FFD84D', CREAM = '#FBF5EC';
const PRE = "'Pretendard', 'Noto Color Emoji', sans-serif";
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all([...[['700', 'Pretendard-Bold.woff2'], ['800', 'Pretendard-ExtraBold.woff2'], ['900', 'Pretendard-Black.woff2']].map(([w, f]) =>
      new FontFace('Pretendard', `url(${staticFile('fonts/' + f)})`, {weight: w}).load()), new FontFace('Noto Color Emoji', `url(${staticFile('fonts/Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf')})`).load()])
      .then((fs) => { fs.forEach((x) => document.fonts.add(x)); continueRender(h); }).catch(() => continueRender(h));
  }, [h]);
};
const Pre: React.FC<{text: string; style: React.CSSProperties}> = ({text, style}) => <div style={style}>{text.split('\n').map((l, i) => <div key={i}>{l}</div>)}</div>;

export const HomeEnglish: React.FC = () => {
  useFonts();
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const t = frame / fps;
  const sp = (s: number, d = 14) => spring({frame: Math.round((t - s) * fps), fps, config: {damping: d, stiffness: 170, mass: .6}});
  const cap = plan.caps.find((c) => t >= c.s && t < c.e);
  const inRes = t >= plan.res[0] - .1 && t < plan.res[1] + 2.6;
  const resK = sp(plan.res[0] - .1, 15); const resOut = interpolate(t, [plan.res[1] + 2.3, plan.res[1] + 2.6], [1, 0], clamp);
  const hook = t < plan.hookEnd;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {(() => { const lift = 380 * Math.min(spring({frame: frame - Math.round((plan.res[0] - .1) * fps), fps, config: {damping: 18, stiffness: 120}}),
          1 - spring({frame: frame - Math.round((plan.res[1] + 2.3) * fps), fps, config: {damping: 18, stiffness: 120}}));
        return <AbsoluteFill style={{background: '#1d1f24'}}>
          {lift > 1 && <AbsoluteFill style={{transform: 'scale(1.25)', filter: 'blur(28px) brightness(.55)'}}><OffthreadVideo src={staticFile('day41/main.mp4')} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} /></AbsoluteFill>}
          <AbsoluteFill style={{transform: `translateY(${-lift}px)`}}>
          <OffthreadVideo src={staticFile('day41/main.mp4')} style={{width: '100%', height: '100%', objectFit: 'cover'}} /></AbsoluteFill></AbsoluteFill>; })()}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.3) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 58%, rgba(0,0,0,.35) 100%)'}} />

      {/* DAY chip + yellow progress bar */}
      <div style={{position: 'absolute', top: 300, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
        <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 26, letterSpacing: 2, color: NAVY, background: YEL, borderRadius: 999, padding: '5px 20px'}}>DAY {plan.day}</div></div>
      <div style={{position: 'absolute', top: 352, left: 90, right: 90, height: 12, borderRadius: 6, background: 'rgba(255,255,255,.3)', overflow: 'hidden'}}>
        <div style={{height: '100%', width: `${Math.min(100, t / plan.duration * 100)}%`, background: 'linear-gradient(90deg, #FFC93C, #FFE27A)'}} /></div>

      {/* Joy (27 Nov): small related photos beside her while she talks, so a sit-down talk isn't dull */}
      {(() => { const PH: [number, string][] = [[1, '8922399'], [2, '4513218'], [3, '8535598'], [4, '6437813'], [5, '6482236'], [6, '3662630'], [7, '3662630']];
        const k = plan.caps.findIndex((c) => t >= c.s && t < c.e); const ph = PH.find(([i]) => i === k); if (!ph || inRes) return null;
        const c = plan.caps[k]; const prev = PH.find(([i]) => i === k - 1); const same = prev && prev[1] === ph[1];
        const a = same ? 1 : spring({frame: Math.round((t - c.s) * fps), fps, config: {damping: 13, stiffness: 150, mass: .6}});
        const side = k % 2 ? 1 : -1; const x = side > 0 ? 735 : 45;
        return <div style={{position: 'absolute', left: x, top: 470 + Math.sin(t * 1.2) * 6, width: 300, padding: '12px 12px 40px', background: '#fff', borderRadius: 6,
          boxShadow: '0 16px 32px rgba(0,0,0,.35)', transform: `rotate(${side * 5}deg) scale(${.7 + .3 * a})`, opacity: Math.min(1, a * 1.4)}}>
          <Img src={staticFile(`day41/stock/${ph[1]}.jpg`)} style={{width: 276, height: 345, objectFit: 'cover', display: 'block'}} /></div>; })()}

      {/* hook: the thumbnail question, big */}
      {hook && (() => { const k = sp(0, 11); const o = interpolate(t, [plan.hookEnd - .2, plan.hookEnd], [1, 0], clamp);
        return <div style={{position: 'absolute', top: 1120, left: 50, right: 50, textAlign: 'center', opacity: o, transform: `scale(${.85 + .15 * k})`}}>
          <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 92, lineHeight: 1.15, color: '#fff', textShadow: '0 5px 20px rgba(0,0,0,.75), 0 0 4px rgba(0,0,0,.8)'}}>
            엄마가 영어를 못하는데,<br /><span style={{color: YEL}}>엄마표 영어요?</span></div>
          <div style={{marginTop: 18, display: 'inline-block', fontFamily: PRE, fontWeight: 800, fontSize: 38, color: NAVY, background: CREAM, borderRadius: 999, padding: '8px 28px'}}>엄마표 영어 자료 제공</div></div>; })()}
      {hook && (() => { const k = sp(.25, 13); const o = interpolate(t, [plan.hookEnd - .2, plan.hookEnd], [1, 0], clamp);
        return <div style={{position: 'absolute', left: 660, top: 450, width: 390, opacity: o * Math.min(1, k * 1.4), transform: `rotate(${6 * k}deg) scale(${.75 + .25 * k})`,
          borderRadius: 10, overflow: 'hidden', border: '6px solid #fff', boxShadow: '0 18px 36px rgba(0,0,0,.4)'}}>
          <Img src={staticFile('day41/cover.jpg')} style={{width: '100%', display: 'block'}} /></div>; })()}

      {/* the free resource: her screen recording in a card below her face (her reference: hailey_ourhabit) */}
      {inRes && <div style={{position: 'absolute', left: 120, top: 800 + (1 - resK) * 300, width: 840, height: 650, borderRadius: 24, overflow: 'hidden', opacity: resOut,
          boxShadow: '0 24px 50px rgba(0,0,0,.5)', border: '5px solid #fff', background: CREAM, transform: `rotate(${(1 - resK) * 4}deg)`}}>
          <Sequence from={Math.round((plan.res[0] - .1) * fps)} layout="none">
            <OffthreadVideo src={staticFile('day41/screen.mp4')} muted style={{width: 840, display: 'block'}} /></Sequence></div>}

      {/* Joy (27 Nov): no badges or emoji card — just her words and the resource itself */}
      {/* captions: her words, at chest height */}
      {cap && !hook && (
        <div style={{position: 'absolute', left: 60, right: 60, top: inRes ? 650 : 1305, height: 150, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
          <Pre text={cap.text} style={{fontFamily: PRE, fontWeight: 800, fontSize: cap.text.length > 30 ? 48 : 54, lineHeight: 1.3, color: '#fff', textShadow: '0 3px 12px rgba(0,0,0,.9), 0 0 4px rgba(0,0,0,.9)'}} />
        </div>)}
    </AbsoluteFill>
  );
};
