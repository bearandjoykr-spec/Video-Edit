// DAY 41 "엄마가 영어를 못하는데, 엄마표 영어요?" (Joy, 27 Nov 2026). Joy's talking head full frame (pauses trimmed), captions at chest
// height (not on her face), a question hook, and her screen recording of the free resource in a rounded card while she talks about it
// (her reference: the hailey_ourhabit reel), then an emoji-comment CTA. All text in y 300–1450; DAY chip + yellow progress bar.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
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

      {/* hook: the thumbnail question, big */}
      {hook && (() => { const k = sp(0, 11); const o = interpolate(t, [plan.hookEnd - .2, plan.hookEnd], [1, 0], clamp);
        return <div style={{position: 'absolute', top: 1120, left: 50, right: 50, textAlign: 'center', opacity: o, transform: `scale(${.85 + .15 * k})`}}>
          <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 92, lineHeight: 1.15, color: '#fff', textShadow: '0 5px 20px rgba(0,0,0,.75), 0 0 4px rgba(0,0,0,.8)'}}>
            엄마가 영어를 못하는데,<br /><span style={{color: YEL}}>엄마표 영어요?</span></div></div>; })()}

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
