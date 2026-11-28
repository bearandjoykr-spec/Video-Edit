// DAY 42 (Joy, 28 Nov 2026): Mark (cut out with a little of his room, bottom-left) introduces his favourite childhood picture books;
// as he says "these are my favourite books…" the 12 books from Joy's image drop onto a 4-shelf bookcase, 3 per shelf.
// No countdown bar (Joy). Text in y 300–1450; captions English (Mark) over Korean.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Freeze, Img, OffthreadVideo, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

export const D42 = {
  fps: 30, duration: 15.2, talk: 12.4,
  caps: [{s: 0, e: 6.0, en: "Hello everyone, my name is Mark,\nI'm a British teacher based here in Seoul.", ko: '안녕하세요, 서울에 사는 영국 선생님 마크예요.'},
    {s: 6.0, e: 10.15, en: 'And these are my favourite books\nfrom when I was a child.', ko: '제가 어릴 때 가장 좋아했던 그림책들이에요.'},
    {s: 10.15, e: 12.4, en: 'Make sure you save!', ko: '꼭 저장해 두세요! 📌'}],
  cta: 12.4,
  books: {start: 6.3, step: .33},
};
const NAVY = '#173B5C', CREAM = '#F5F0E6', WOOD = '#9A6B43';
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
const PLANKS = [814, 1026, 1238, 1450];                      // top of each shelf board
const BW = 162, BH = 196, GAP = 48, SW = 3 * BW + 2 * GAP + 44, SX = (1080 - SW) / 2;                                     // bookcase x and width (right of Mark)

export const Bookshelf: React.FC = () => {
  useFonts();
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const t = frame / fps;
  const cap = D42.caps.find((c) => t >= c.s && t < c.e);
  const MW = 640, MH = MW * 1920 / 1080;
  return (
    <AbsoluteFill style={{background: CREAM, overflow: 'hidden'}}>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 900px 1100px at 60% 45%, #FFFDF7 0%, #F5F0E6 60%, #E9DFCC 100%)'}} />
      {/* bookcase: back panel, sides and four boards */}
      <div style={{position: 'absolute', left: SX - 22, top: PLANKS[0] - 212, width: SW + 44, height: PLANKS[3] - PLANKS[0] + 252, background: '#EFE3CF', borderRadius: 10,
        boxShadow: 'inset 0 0 40px rgba(120,80,40,.18)', border: `14px solid ${WOOD}`, borderBottom: 'none'}} />
      {PLANKS.map((y, i) => <div key={i} style={{position: 'absolute', left: SX - 30, top: y, width: SW + 60, height: 26, background: `linear-gradient(${WOOD}, #7E5432)`, borderRadius: 4,
        boxShadow: '0 10px 14px rgba(80,50,20,.25)'}} />)}
      {/* the 12 books, 3 per shelf, dropping in one after another */}
      {Array.from({length: 12}, (_, i) => { const row = Math.floor(i / 3), col = i % 3; const at = D42.books.start + i * D42.books.step;
        const k = spring({frame: frame - Math.round(at * fps), fps, config: {damping: 11, stiffness: 140, mass: .7}}); if (frame < at * fps) return null;
        const h = BH + 6; const w = Math.round(h * (i < 6 ? 172 / 218 : 159 / 245)); const x = SX + 22 + col * (BW + GAP) + (BW - w) / 2; const y = PLANKS[row] - h;   // whole cover, titles fully visible
        const tilt = [-3, 2, -1.5, 2.5, -2, 1.5, -2.5, 3, -1, 2, -3, 1.5][i];
        return <Img key={i} src={staticFile(`day42/b${String(i).padStart(2, '0')}.jpg`)} style={{position: 'absolute', left: x, top: y - (1 - k) * 260, width: w, height: h, objectFit: 'fill',
          borderRadius: 5, transform: `rotate(${tilt * (1 - k * .6)}deg)`, transformOrigin: '50% 100%', opacity: Math.min(1, k * 2),
          boxShadow: '4px 6px 10px rgba(60,35,10,.35)'}} />; })}
      {/* Mark: clean cut-out (Joy, 28 Nov: no room or desk), smaller, bottom-left under the bookcase — the books are the main thing */}
      {(() => { const MW2 = 520, sc = MW2 / 1080; const v = <OffthreadVideo src={staticFile('day42/mark-clean.webm')} transparent muted style={{width: MW2, height: 1700 * sc}} />;
        return <div style={{position: 'absolute', left: -30, top: 1480 - 720 * sc, width: MW2, height: 1700 * sc,
          filter: 'drop-shadow(5px 0 0 #fff) drop-shadow(-5px 0 0 #fff) drop-shadow(0 -5px 0 #fff) drop-shadow(0 14px 20px rgba(60,40,10,.3))',
          WebkitMaskImage: 'linear-gradient(180deg, #000 82%, transparent 100%)'}}>
          {t < D42.talk - .05 ? v : <Freeze frame={Math.round((D42.talk - .1) * fps)}>{v}</Freeze>}</div>; })()}
      {/* DAY chip + title */}
      <div style={{position: 'absolute', top: 300, left: 0, right: 0, textAlign: 'center'}}>
        <span style={{fontFamily: PRE, fontWeight: 800, fontSize: 26, letterSpacing: 2, color: NAVY, background: '#FFD84D', borderRadius: 999, padding: '5px 20px'}}>DAY 42</span>
        <div style={{marginTop: 12, fontFamily: PRE, fontWeight: 900, fontSize: 56, lineHeight: 1.15, color: NAVY}}>영국 선생님이<br />추천하는 그림책 12권 🇬🇧</div></div>
      {/* captions: Mark's English over Korean */}
      {cap && (() => { const k = spring({frame: frame - Math.round(cap.s * fps), fps, config: {damping: 16}});
        // Joy (28 Nov): Korean only, under the bookcase beside Mark (the English under the title looked crowded)
        return <div key={cap.s} style={{position: 'absolute', top: 1490, left: 430, right: 50, height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center',
          opacity: k, transform: `translateY(${(1 - k) * 10}px)`}}>
          <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 40, lineHeight: 1.3, color: NAVY, wordBreak: 'keep-all'}}>{cap.ko}</div></div>; })()}
      {/* Joy (28 Nov): end — comment for the book list */}
      {t >= D42.cta && (() => { const k = spring({frame: frame - Math.round(D42.cta * fps), fps, config: {damping: 12}});
        return <div style={{position: 'absolute', left: 120, right: 120, top: 960, textAlign: 'center', transform: `scale(${k})`}}>
          <div style={{display: 'inline-block', background: 'rgba(255,255,255,.96)', borderRadius: 24, padding: '24px 34px', boxShadow: '0 16px 36px rgba(0,0,0,.25)', fontFamily: PRE, color: NAVY}}>
            <div style={{fontWeight: 900, fontSize: 44, lineHeight: 1.28}}>책 목록이 필요하면<br />댓글에 '그림책' 남겨 주세요</div>
            <div style={{marginTop: 6, fontWeight: 700, fontSize: 28, color: '#7A6A55'}}>Comment for the book list 📚</div></div></div>; })()}
    </AbsoluteFill>
  );
};
