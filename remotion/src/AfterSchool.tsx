// DAY 40 "하원 후, 이렇게 말해요!" (Joy, 26 Nov 2026): Mark's footage full frame; each phrase pops up as a card in the style of
// Joy's dialogue sheets (navy PARENT chip, English bold, Korean under it) while he says it, words lighting up on his timing;
// on "look at the comments below" her four sheets fan in. All text in y 300–1450, cards below Mark's face. Yellow progress bar.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, OffthreadVideo, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import plan from './day40.json';

const NAVY = '#14305C', CHIP2 = '#4D6E96', CREAM = '#FBF5EC', YEL = '#FFD84D';
const PRE = "'Pretendard', 'Noto Color Emoji', sans-serif";
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const FONTS: [string, string][] = [['700', 'Pretendard-Bold.woff2'], ['800', 'Pretendard-ExtraBold.woff2'], ['900', 'Pretendard-Black.woff2']];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all([...FONTS.map(([w, f]) => new FontFace('Pretendard', `url(${staticFile('fonts/' + f)})`, {weight: w}).load()),
      new FontFace('Noto Color Emoji', `url(${staticFile('fonts/Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf')})`).load()])
      .then((fs) => { fs.forEach((x) => document.fonts.add(x)); continueRender(h); }).catch(() => continueRender(h));
  }, [h]);
};
type Word = {w: string; s?: number};
type Phrase = {n: string; who: string; en: string; ko: string; s: number; e: number; again: number[]; words: Word[]; words2: Word[]};

export const AfterSchool: React.FC = () => {
  useFonts();
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const t = frame / fps;
  const sp = (s: number, d = 14) => spring({frame: Math.round((t - s) * fps), fps, config: {damping: d, stiffness: 170, mass: .6}});
  const P = plan.phrases as Phrase[]; const cur = P.find((p) => t >= p.s && t < p.e);
  const outro = t >= plan.outro;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <OffthreadVideo src={staticFile('day40/src.mp4')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      {/* soft dark at the bottom so the cards read; dim while the comment sheets show */}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,.25) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 55%, rgba(0,0,0,.35) 100%)'}} />
      {outro && <AbsoluteFill style={{background: `rgba(10,20,40,${interpolate(t, [plan.outro, plan.outro + .4], [0, .55], clamp)})`}} />}

      {/* DAY chip + yellow progress bar */}
      <div style={{position: 'absolute', top: 300, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
        <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 26, letterSpacing: 2, color: NAVY, background: YEL, borderRadius: 999, padding: '5px 20px'}}>DAY {plan.day}</div></div>
      <div style={{position: 'absolute', top: 352, left: 90, right: 90, height: 12, borderRadius: 6, background: 'rgba(255,255,255,.3)', overflow: 'hidden'}}>
        <div style={{height: '100%', width: `${Math.min(100, t / plan.duration * 100)}%`, background: 'linear-gradient(90deg, #FFC93C, #FFE27A)'}} /></div>

      {/* hook */}
      {t < plan.hook[1] + .2 && (() => { const k = sp(.1, 12); const o = interpolate(t, [plan.hook[1] - .1, plan.hook[1] + .2], [1, 0], clamp);
        return <div style={{position: 'absolute', top: 400, left: 70, right: 70, textAlign: 'center', opacity: o}}>
          <div style={{display: 'inline-block', background: CREAM, borderRadius: 22, padding: '26px 36px', boxShadow: '0 12px 30px rgba(0,0,0,.3)', transform: `scale(${.85 + .15 * k})`}}>
            <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 76, color: NAVY, lineHeight: 1.15}}>하원 후, 이렇게 말해요!</div>
            <div style={{marginTop: 10, fontFamily: PRE, fontWeight: 700, fontSize: 36, color: CHIP2}}>아이와 바로 쓰는 영어 3문장 🏠</div></div>
          {/* Joy (26 Nov): the question in English too */}
          <div style={{marginTop: 520, fontFamily: PRE, fontWeight: 900, fontSize: 64, lineHeight: 1.18, color: '#fff', textShadow: '0 4px 16px rgba(0,0,0,.75), 0 0 3px rgba(0,0,0,.8)', opacity: sp(.5, 14)}}>What can I say in English<br />to my child after school?</div></div>; })()}

      {/* the three phrases */}
      {cur && (() => { const k = sp(cur.s); const out = interpolate(t, [cur.e - .2, cur.e], [1, 0], clamp);
        const second = t >= cur.again[1] - .1; const ws = second ? cur.words2 : cur.words;
        const againK = t >= cur.again[0] && t < cur.again[1] + .6 ? sp(cur.again[0], 10) : 0;
        return <div style={{position: 'absolute', left: 60, right: 60, top: 1110, opacity: out, transform: `translateY(${(1 - k) * 40}px)`}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14}}>
            <span style={{fontFamily: PRE, fontWeight: 900, fontSize: 34, color: NAVY, background: YEL, borderRadius: 10, padding: '2px 14px'}}>{cur.n}</span>
            {againK > .01 && <span style={{fontFamily: PRE, fontWeight: 800, fontSize: 30, color: '#fff', background: 'rgba(20,48,92,.85)', borderRadius: 999, padding: '4px 16px', transform: `scale(${againK})`}}>🔁 따라 해 보세요</span>}
          </div>
          <div style={{display: 'flex', borderRadius: 26, overflow: 'hidden', background: CREAM, border: `3px solid ${NAVY}`, boxShadow: '0 14px 34px rgba(0,0,0,.35)', transform: `scale(${.92 + .08 * k})`, transformOrigin: '50% 100%'}}>
            <div style={{width: 190, background: NAVY, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: PRE, fontWeight: 800, fontSize: 32, color: '#fff', letterSpacing: 1}}>{cur.who}</div>
            <div style={{flex: 1, padding: '22px 28px'}}>
              <div style={{fontFamily: PRE, fontWeight: 900, fontSize: cur.en.length > 26 ? 44 : 54, lineHeight: 1.22, color: NAVY}}>
                {ws.map((w, i) => w.w === '\n' ? <br key={i} /> : <span key={i} style={{color: t >= (w.s ?? 1e9) ? NAVY : 'rgba(20,48,92,.32)', transition: 'none'}}>{w.w} </span>)}</div>
              <div style={{marginTop: 8, fontFamily: PRE, fontWeight: 700, fontSize: 36, color: '#3B4A63'}}>{cur.ko}</div></div></div>
        </div>; })()}

      {/* "look at the comments below": Joy's four dialogue sheets fan in */}
      {outro && (() => { const cards = ['day40/card48.jpg', 'day40/card49.jpg', 'day40/card50.jpg', 'day40/card51.jpg'];
        const pos: [number, number, number][] = [[60, 430, -8], [300, 410, -2], [540, 430, 4], [780, 450, 9]];
        const lab = sp(plan.outro + .1, 12); const arrow = Math.sin(t * 6) * 8;
        return <>
          <div style={{position: 'absolute', top: 400, left: 0, right: 0, textAlign: 'center', transform: `scale(${lab})`}}>
            <span style={{fontFamily: PRE, fontWeight: 900, fontSize: 58, color: NAVY, background: YEL, borderRadius: 16, padding: '8px 26px'}}>상황별 대화문 4가지</span></div>
          {cards.map((c, i) => { const k = sp(plan.outro + .35 + i * .18, 13); const [x, y, r] = pos[i];
            return <Img key={c} src={staticFile(c)} style={{position: 'absolute', left: x - 40, top: y + 130 + (1 - k) * 200, width: 320, transform: `rotate(${r * k}deg) scale(${k})`,
              borderRadius: 8, boxShadow: '0 16px 30px rgba(0,0,0,.45)', border: '4px solid #fff'}} />; })}
          {(() => { const k = sp(plan.comments, 11);
            return <div style={{position: 'absolute', top: 1110, left: 0, right: 0, textAlign: 'center', transform: `scale(${k})`}}>
              <div style={{display: 'inline-block', background: CREAM, borderRadius: 22, padding: '20px 34px', boxShadow: '0 12px 30px rgba(0,0,0,.35)'}}>
                <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 50, color: NAVY}}>💬 댓글에서 확인하세요!</div>
                <div style={{marginTop: 6, fontFamily: PRE, fontWeight: 700, fontSize: 32, color: CHIP2}}>Check the comments below</div></div>
              <div style={{marginTop: 18 + arrow, fontSize: 70, color: YEL, textShadow: '0 4px 10px rgba(0,0,0,.5)'}}>⬇</div></div>; })()}
        </>; })()}
    </AbsoluteFill>
  );
};
