// DAY 38 "영유 상담 전 꼭 확인할 3가지 (2편)" (Joy, 21 Nov 2026). A lighter look than DAY 37 so the series doesn't feel repetitive:
// stock B-roll in a rounded window across the top, warm paper below where Joy's sticker stands, and "상담 노트" cards in the chalk
// fonts (Gaegu, house default since DAY 33). All text sits in y 300–1450. Yellow progress bar (Joy, DAY 37).
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Img} from 'remotion';

type Cap = {s: number; e: number; text: string; sec: string};
type Sec = {kind: string; s: number; e: number};
export type NotePlan = {part?: number; joyMedia?: string; joyMap?: {t: number; src: number; d: number}[]; hookTitle?: string[]; props?: string[]; next?: string | null; tip?: string[]; tipType?: number[]; tipRed?: number; tipImg?: string; books?: string[]; series?: {s: number; e: number; title: string; items: string[][]}[];
  fps: number; day: number; media: string; duration: number; frames: number; captions: Cap[]; sections: Sec[]; ticks: Record<string, number[]>};

const C = {paper: '#F3EADB', note: '#FFFDF7', line: '#E6DCC8', margin: '#E8A0A0', navy: '#1E2D4D', ink: '#2B2B2B', gold: '#C9A86A', yellow: '#FFD84D',
  red: '#D9534F', green: '#3E8E5E', muted: '#7A6F60', white: '#FFFFFF'};
const PRE = "'Pretendard', 'Noto Color Emoji', sans-serif";
const ROUND = "'Jua', 'Pretendard', 'Noto Color Emoji', sans-serif";
const HAND = "'Gaegu', 'Pretendard', 'Noto Color Emoji', cursive";
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const FONTS: [string, string, string, string][] = [
  ['Pretendard', 'normal', '700', 'Pretendard-Bold.woff2'], ['Pretendard', 'normal', '800', 'Pretendard-ExtraBold.woff2'],
  ['Pretendard', 'normal', '900', 'Pretendard-Black.woff2'], ['Noto Color Emoji', 'normal', '400', 'Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf'],
  ['Gaegu', 'normal', '700', 'Gaegu-Bold.ttf'], ['Jua', 'normal', '400', 'Jua-Regular.ttf'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([f, st, w, file]) => new FontFace(f, `url(${staticFile('fonts/' + file)})`, {style: st, weight: w}).load().then((x) => document.fonts.add(x))))
      .then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
  }, [h]);
};
const sp = (t: number, s: number, fps: number, damping = 14) => spring({frame: Math.round((t - s) * fps), fps, config: {damping, stiffness: 180, mass: .6}});
const Pre: React.FC<{text: string; style: React.CSSProperties}> = ({text, style}) => <div style={{whiteSpace: 'pre-line', ...style}}>{text}</div>;

// a page from a parent's consultation notebook
const NOTE: React.CSSProperties = {position: 'absolute', top: 395, left: 70, right: 70, height: 440, borderRadius: 22, overflow: 'hidden',
  background: `repeating-linear-gradient(180deg, ${C.note} 0px, ${C.note} 52px, ${C.line} 52px, ${C.line} 54px)`,
  boxShadow: '0 24px 50px rgba(0,0,0,.35)', transform: 'rotate(-1deg)'};
const Margin: React.FC = () => <div style={{position: 'absolute', top: 0, bottom: 0, left: 74, width: 3, background: C.margin}} />;

const Box: React.FC<{text: string; on: number; t: number; fps: number}> = ({text, on, t, fps}) => {
  const shown = t >= on; const k = sp(t, on, fps, 11);
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 14, height: 54}}>
      <div style={{position: 'relative', width: 40, height: 40, border: `3px solid ${C.navy}`, borderRadius: 8, flex: 'none'}}>
        {shown && <span style={{position: 'absolute', left: 2, top: -22, fontFamily: HAND, fontWeight: 700, fontSize: 64, color: C.red, transform: `scale(${k})`}}>✓</span>}
      </div>
      <div style={{fontFamily: HAND, fontWeight: 700, fontSize: 44, color: shown ? C.ink : '#A79F92'}}>{text}</div>
    </div>
  );
};

const Head: React.FC<{n: string; title: string}> = ({n, title}) => (
  <div style={{display: 'flex', alignItems: 'baseline', gap: 14, height: 70}}>
    <span style={{fontFamily: PRE, fontWeight: 900, fontSize: 50, color: C.red}}>{n}</span>
    <span style={{fontFamily: PRE, fontWeight: 900, fontSize: 48, color: C.navy}}>{title}</span>
  </div>
);

const P1: React.FC<{sec: Sec; t: number; fps: number; ticks: number[]}> = ({sec, t, fps, ticks}) => {
  const step = Math.floor(Math.max(0, t - sec.s - .6) / 1.1) % 3;
  const faces = ['👩‍🏫', '👨‍🏫', '🧑‍🏫'];
  return (
    <div style={{...NOTE, padding: '18px 36px 0 100px'}}><Margin />
      <Head n="①" title="교사의 근속 기간" />
      <div style={{display: 'flex', alignItems: 'center', gap: 16, height: 104}}>
        {faces.map((f, i) => <span key={i} style={{fontSize: 62, opacity: i === step ? 1 : .3, transform: `scale(${i === step ? 1.15 : .9})`}}>{f}</span>)}
        <span style={{fontFamily: HAND, fontWeight: 700, fontSize: 40, color: C.muted}}>↻ 적응, 또 적응…</span>
      </div>
      <Box text="선생님들 평균 근무 기간은?" on={ticks[0] ?? 1e9} t={t} fps={fps} />
      <Box text="바뀌면 인수인계는 어떻게?" on={ticks[1] ?? 1e9} t={t} fps={fps} />
    </div>
  );
};

const P2: React.FC<{sec: Sec; t: number; fps: number; ticks: number[]; caps: Cap[]}> = ({sec, t, fps, ticks, caps}) => {
  const cs = caps.filter((c) => c.sec === 'p2');
  const cross = cs[3] ? interpolate(t, [cs[3].s, cs[3].s + .5], [0, 1], clamp) : 0;    // "하지만 유명한 교과서를 쓴다고…"
  return (
    <div style={{...NOTE, padding: '18px 36px 0 100px'}}><Margin />
      <Head n="②" title="교과서" />
      <div style={{display: 'flex', alignItems: 'center', gap: 14, height: 104}}>
        {[['🇺🇸', '미국 교과서', cs[1]], ['🇬🇧', '영국 교과서', cs[2]]].map(([e, x, c], i) => (
          <div key={i} style={{position: 'relative', fontFamily: HAND, fontWeight: 700, fontSize: 38, color: C.navy, border: `3px solid ${C.navy}`, borderRadius: 14,
            padding: '2px 14px', opacity: c && t >= (c as Cap).s ? 1 : .25, transform: 'rotate(-3deg)'}}>{e as string} {x as string}
            <div style={{position: 'absolute', left: -6, right: -6, top: '50%', height: 4, background: C.red, transform: `scaleX(${cross})`, transformOrigin: '0 50%'}} /></div>))}
        <span style={{fontFamily: HAND, fontWeight: 700, fontSize: 40, color: C.red, opacity: cross}}>≠ 좋은 수업</span>
      </div>
      <Box text="교재로 어떤 활동을 하나요?" on={ticks[0] ?? 1e9} t={t} fps={fps} />
      <Box text="배운 영어를 써 볼 기회는?" on={ticks[1] ?? 1e9} t={t} fps={fps} />
    </div>
  );
};

const P3: React.FC<{sec: Sec; t: number; fps: number; ticks: number[]; caps: Cap[]}> = ({sec, t, fps, ticks, caps}) => {
  const cs = caps.filter((c) => c.sec === 'p3');
  const go = cs[2] ? Math.max(0, t - cs[2].s) : 0;   // the message travels while she explains it
  const chain = ['학부모', '상담실', '한국인 강사', '원어민 강사'];
  return (
    <div style={{...NOTE, padding: '18px 36px 0 100px'}}><Margin />
      <Head n="③" title="운영진의 소통 방식" />
      <div style={{display: 'flex', alignItems: 'center', gap: 6, height: 104}}>
        {chain.map((x, i) => {
          const on = go > i * .7;
          return <React.Fragment key={i}>
            {i > 0 && <span style={{fontFamily: HAND, fontWeight: 700, fontSize: 36, color: C.muted, opacity: on ? 1 : .3}}>→</span>}
            <span style={{fontFamily: HAND, fontWeight: 700, fontSize: 31, color: i === 3 ? C.red : C.navy, background: on ? '#FFF1B8' : 'transparent', borderRadius: 10,
              padding: '2px 8px', opacity: on ? 1 : .35, filter: i === 3 && on && t < (ticks[0] ?? 1e9) ? 'blur(.6px)' : 'none'}}>{i === 3 && on && t < (ticks[0] ?? 1e9) ? x + ' ❓' : x}</span>
          </React.Fragment>;
        })}
      </div>
      <Box text="운영진 ↔ 원어민 강사, 소통은?" on={ticks[0] ?? 1e9} t={t} fps={fps} />
      <Box text="학부모 의견, 수업에 반영되나요?" on={ticks[1] ?? 1e9} t={t} fps={fps} />
    </div>
  );
};

const Last: React.FC<{sec: Sec; t: number; fps: number; caps: Cap[]}> = ({sec, t, fps, caps}) => {
  const cs = caps.filter((c) => c.sec === 'last');
  const vsAt = cs[5]?.s ?? 1e9, kidAt = cs[6]?.s ?? 1e9, quoteAt = cs.find((c) => c.text.startsWith('결국'))?.s ?? 1e9;
  if (t >= quoteAt) {
    const k = sp(t, quoteAt, fps, 12);
    return (
      <div style={{...NOTE, background: C.navy, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', transform: `rotate(-1deg) scale(${.94 + .06 * k})`}}>
        <div style={{fontFamily: HAND, fontWeight: 700, fontSize: 40, color: C.gold}}>결국 중요한 건</div>
        <div style={{marginTop: 10, fontFamily: HAND, fontWeight: 700, fontSize: 62, lineHeight: 1.2, color: C.white, textAlign: 'center'}}>
          <span style={{opacity: .55}}>어디에서</span> 배우느냐보다<br /><span style={{color: C.yellow}}>어떤 경험으로</span> 배우느냐</div>
      </div>);
  }
  return (
    <div style={{...NOTE, padding: '26px 36px 0 100px'}}><Margin />
      <div style={{fontFamily: HAND, fontWeight: 700, fontSize: 46, color: C.red}}>✏️ 꼭 말씀드리고 싶은 것</div>
      <div style={{marginTop: 18, display: 'flex', gap: 12, flexWrap: 'wrap', opacity: t >= vsAt ? 1 : .0}}>
        {['🏷️ 학원 이름', '📚 유명한 교재', '✨ 화려한 시설'].map((x, i) => (
          <span key={i} style={{position: 'relative', fontFamily: HAND, fontWeight: 700, fontSize: 38, color: C.muted, border: `2px solid ${C.muted}`, borderRadius: 999, padding: '0 14px'}}>{x}
            <span style={{position: 'absolute', left: 0, right: 0, top: '52%', height: 3, background: C.red, transform: `scaleX(${interpolate(t, [kidAt, kidAt + .4], [0, 1], clamp)})`, transformOrigin: '0 50%'}} /></span>))}
      </div>
      <div style={{marginTop: 26, fontFamily: HAND, fontWeight: 700, fontSize: 50, color: C.navy, opacity: sp(t, kidAt, fps), transform: `translateY(${(1 - sp(t, kidAt, fps)) * 16}px)`}}>
        👉 우리 아이가 <span style={{background: '#FFF1B8'}}>매일 만나는 선생님</span>과<br />&nbsp;&nbsp;&nbsp;&nbsp;<span style={{background: '#FFF1B8'}}>보내는 시간</span></div>
    </div>
  );
};

const Intro: React.FC<{sec: Sec; t: number; fps: number}> = ({sec, t, fps}) => (
  <div style={{...NOTE, padding: '22px 36px 0 100px'}}><Margin />
    <div style={{fontFamily: HAND, fontWeight: 700, fontSize: 44, color: C.red}}>📝 상담 전 체크리스트 2편</div>
    {['교사의 근속 기간', '교과서', '운영진의 소통 방식'].map((x, i) => ( // intro list
      <div key={i} style={{display: 'flex', alignItems: 'center', gap: 14, height: 70, opacity: sp(t, sec.s + .3 + .25 * i, fps)}}>
        <span style={{fontFamily: HAND, fontWeight: 700, fontSize: 52, color: C.red}}>{'①②③'[i]}</span>
        <span style={{fontFamily: HAND, fontWeight: 700, fontSize: 48, color: C.navy, filter: 'blur(9px)'}}>{x}</span><span style={{fontSize: 36}}>🔒</span>
      </div>))}
    <div style={{fontFamily: HAND, fontWeight: 700, fontSize: 34, color: C.muted, marginTop: 6, opacity: sp(t, sec.s + 1.2, fps)}}>③은 제가 근무하며 정말 중요하다고 느낀 것</div>
  </div>
);

const Follow: React.FC<{sec: Sec; t: number; fps: number; next?: string | null; part?: number}> = ({sec, t, fps, next, part}) => {
  const k = sp(t, sec.s, fps, 13);
  const tap = t - sec.s - 1.4; const done = tap > .15;
  return (
    <div style={{...NOTE, background: C.note, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: k, transform: `rotate(-1deg) scale(${.94 + .06 * k})`}}>
      <Img src={staticFile('brand/logo-full.png')} style={{height: 120, objectFit: 'contain'}} />
      <div style={{marginTop: 10, fontFamily: PRE, fontWeight: 900, fontSize: 54, color: C.navy}}>@thebearandjoy</div>
      {part ? <div style={{marginTop: 8, textAlign: 'center', fontFamily: HAND, fontWeight: 700, fontSize: 40, color: next ? C.red : C.green, opacity: sp(t, sec.s + .4, fps)}}>
          {next ? <>다음 편 👉 {next}</> : <>✓ 영유 상담 체크리스트 완성!</>}</div>
        : <div style={{marginTop: 6, fontFamily: HAND, fontWeight: 700, fontSize: 40, color: C.muted}}>팔로우하고 다음 체크리스트도 받아 가세요</div>}
      <div style={{marginTop: 18, fontFamily: PRE, fontWeight: 900, fontSize: 44, color: '#fff', background: done ? '#7A8599' : '#4C6EF5', borderRadius: 16, padding: '10px 54px',
        transform: `scale(${tap > 0 && tap < .15 ? .92 : 1})`}}>{done ? '✓ 팔로잉' : '+ 팔로우'}</div>
    </div>
  );
};

// silent bonus tip, typed out line by line (Joy, 22 Nov)
const TypeCard: React.FC<{sec: Sec; t: number; fps: number; lines: string[]; span: number[]; red?: number; img?: string}> = ({sec, t, fps, lines, span, red = 6, img}) => {
  const total = lines.reduce((n, l) => n + [...l].length, 0);
  const shown = Math.floor(interpolate(t - sec.s, span, [0, total], clamp));
  let left = shown;
  const k = sp(t, sec.s, fps, 14);
  return (
    <div style={{...NOTE, top: 420, height: 980, padding: '40px 40px 0 104px', opacity: k, transform: `rotate(-1deg) scale(${.95 + .05 * k})`}}><Margin />
      {lines.map((l, i) => {
        const ch = [...l]; const n = Math.max(0, Math.min(ch.length, left)); left -= ch.length;
        const typing = n > 0 && n < ch.length || (n === ch.length && left < 0 && left + ch.length === 0);
        return <div key={i} style={{minHeight: i === 0 ? 96 : 104, whiteSpace: 'nowrap', fontFamily: i === 0 ? PRE : ROUND, fontWeight: i === 0 ? 900 : 400, fontSize: i === 0 ? 62 : 46,
          color: i === 0 ? C.red : i >= red ? C.red : C.navy, lineHeight: '104px'}}>
          {ch.slice(0, n).join('')}{(n > 0 && n < ch.length) || (i === lines.length - 1 && n === ch.length) ?
            <span style={{opacity: Math.floor(t * 2.5) % 2 ? 1 : 0, color: C.navy}}>|</span> : null}</div>;
      })}
      {img && (() => {   // a blurred peek at the table people get by commenting
        const q = sp(t, sec.s + span[1] + .1, fps, 14);
        return <div style={{position: 'absolute', left: 110, right: 50, bottom: 24, height: 250, borderRadius: 16, overflow: 'hidden', opacity: q, transform: `translateY(${(1 - q) * 40}px) rotate(1.5deg)`,
          boxShadow: '0 10px 24px rgba(60,40,10,.3)'}}>
          <Img src={staticFile(img)} style={{width: '100%', filter: 'blur(5px)', transform: 'translateY(-12%)'}} />
          <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: PRE, fontWeight: 900, fontSize: 44, color: C.navy}}>
            <span style={{background: C.yellow, borderRadius: 14, padding: '6px 22px'}}>💬 '교과서' 댓글 → 📩 DM</span></div>
        </div>;
      })()}
    </div>
  );
};

const End: React.FC<{sec: Sec; t: number; fps: number}> = ({sec, t, fps}) => {
  const k = sp(t, sec.s, fps, 14);
  return (
    <div style={{...NOTE, padding: '20px 36px 0 100px', opacity: k}}><Margin />
      <div style={{fontFamily: HAND, fontWeight: 700, fontSize: 46, color: C.red}}>📌 상담 전 체크리스트 2편</div>
      {['① 교사의 근속 기간 · 인수인계', '② 교재로 하는 활동 · 써 볼 기회', '③ 운영진 ↔ 원어민 강사 소통'].map((x, i) => (
        <div key={i} style={{display: 'flex', alignItems: 'center', height: 54, fontFamily: HAND, fontWeight: 700, fontSize: 42, color: C.navy, opacity: sp(t, sec.s + .2 + .15 * i, fps)}}>
          {x}<span style={{marginLeft: 'auto', color: C.red, fontSize: 52}}>✓</span></div>))}
      <div style={{marginTop: 18, display: 'flex', gap: 10, flexWrap: 'wrap'}}>
        {['📌 저장', '📤 영유 고민하는 친구에게', '💬 궁금한 점은 댓글로'].map((x, i) => (
          <span key={i} style={{fontFamily: PRE, fontWeight: 800, fontSize: 26, color: C.navy, border: `2px solid ${C.navy}`, borderRadius: 999, padding: '4px 14px',
            opacity: sp(t, sec.s + .7 + .15 * i, fps)}}>{x}</span>))}
      </div>
      <div style={{marginTop: 10, fontFamily: HAND, fontWeight: 700, fontSize: 36, color: C.muted, opacity: sp(t, sec.s + 1.2, fps)}}>@thebearandjoy</div>
    </div>
  );
};

// Joy (23 Nov): DAY 39 opens on her real textbook photos landing one on another (0.3 s each) before she speaks; the question sits below
const Books: React.FC<{sec: Sec; t: number; fps: number; books: string[]; title: string[]}> = ({sec, t, fps, books, title}) => {
  const step = (sec.e - sec.s) / books.length; const n = Math.min(books.length - 1, Math.floor((t - sec.s) / step));
  const rot = [-4, 3, -2, 5, -3, 2, -5, 3];
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: 'rgba(243,234,219,.92)'}} />
      {books.slice(0, n + 1).map((b, i) => {
        const k = sp(t, sec.s + i * step, fps, 16);
        return <div key={i} style={{position: 'absolute', left: 60, right: 60, top: 405, height: 720, display: 'flex', alignItems: 'center', justifyContent: 'center',
          transform: `translate(${(i % 2 ? 1 : -1) * 18}px, ${(1 - k) * -60}px) scale(${1.25 - .25 * k}) rotate(${rot[i % rot.length]}deg)`, opacity: Math.min(1, k * 1.5)}}>
          <Img src={staticFile(b)} style={{maxWidth: '100%', maxHeight: '100%', border: '14px solid #fff', borderRadius: 10, boxShadow: '0 18px 40px rgba(60,40,10,.45)'}} />
        </div>;
      })}
      <div style={{position: 'absolute', top: 1170, left: 60, right: 60, textAlign: 'center'}}>
        <div style={{display: 'inline-block', fontFamily: HAND, fontWeight: 700, fontSize: 40, color: C.navy, background: C.yellow, borderRadius: 12, padding: '0 18px', transform: 'rotate(-2deg)'}}>영유 상담 체크리스트 ②</div>
        <div style={{marginTop: 14, fontFamily: PRE, fontWeight: 900, fontSize: 84, lineHeight: 1.12, color: C.navy, transform: `scale(${.9 + .1 * sp(t, sec.s, fps, 12)})`}}>
          {title[0]}<br /><span style={{color: '#D9534F'}}>{title[1]}</span></div>
      </div>
    </AbsoluteFill>
  );
};

// Joy (23 Nov): famous series shown book by book (cover + English name + what it is for) while she talks about textbooks
const Series: React.FC<{sr: {s: number; e: number; title: string; items: string[][]}; t: number; fps: number}> = ({sr, t, fps}) => {
  const step = Math.min(.9, (sr.e - sr.s - .4) / sr.items.length);
  const out = interpolate(t, [sr.e - .25, sr.e], [1, 0], clamp);
  return (
    <div style={{...NOTE, background: C.note, padding: '18px 26px 0', opacity: Math.min(sp(t, sr.s, fps, 16), out)}}>
      <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 40, color: C.navy, textAlign: 'center'}}>{sr.title}</div>
      <div style={{display: 'flex', gap: 14, marginTop: 14, height: 330}}>
        {sr.items.map(([img, en, ko], i) => {
          const k = sp(t, sr.s + .25 + i * step, fps, 14);
          return <div key={i} style={{flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', opacity: Math.min(1, k * 1.4), transform: `translateY(${(1 - k) * 40}px) scale(${.85 + .15 * k})`}}>
            <div style={{height: 230, display: 'flex', alignItems: 'flex-end', justifyContent: 'center'}}>
              <Img src={staticFile(img)} style={{maxWidth: 210, maxHeight: 230, borderRadius: 6, boxShadow: '0 8px 18px rgba(60,40,10,.35)'}} /></div>
            <div style={{marginTop: 12, fontFamily: PRE, fontWeight: 800, fontSize: 21, lineHeight: 1.15, color: C.navy, textAlign: 'center'}}>{en}</div>
            <div style={{marginTop: 4, fontFamily: PRE, fontWeight: 700, fontSize: 24, color: C.navy, background: C.yellow, borderRadius: 8, padding: '0 8px'}}>{ko}</div>
          </div>;
        })}
      </div>
    </div>
  );
};

export const ConsultNote: React.FC<{plan: NotePlan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const t = frame / fps;
  const secs = plan.sections; const sec = secs.find((x) => t >= x.s && t < x.e) ?? secs[secs.length - 1];
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const W = 1080 * .64, H = 1920 * .64;
  const outline = 'drop-shadow(6px 0 0 #fff) drop-shadow(-6px 0 0 #fff) drop-shadow(0 6px 0 #fff) drop-shadow(0 -6px 0 #fff) drop-shadow(0 20px 30px rgba(60,40,10,.35))';
  const hk = sp(t, 0, fps, 12);
  return (
    <AbsoluteFill style={{background: C.paper, overflow: 'hidden'}}>
      <AbsoluteFill style={{backgroundImage: 'radial-gradient(rgba(120,100,70,.14) 2px, transparent 2px)', backgroundSize: '40px 40px'}} />
      {/* B-roll window: top 58% of the frame, rounded bottom corners */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 1120, borderRadius: '0 0 70px 70px', overflow: 'hidden', boxShadow: '0 14px 40px rgba(60,40,10,.3)'}}>
        <AbsoluteFill style={{transform: `scale(${1.04 + .012 * Math.sin(t * .5)})`}}>
          <OffthreadVideo src={staticFile(`${plan.media}/bg.mp4`)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
        </AbsoluteFill>
        <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(20,24,34,.55) 0%, rgba(20,24,34,.15) 30%, rgba(20,24,34,.1) 70%, rgba(20,24,34,.35) 100%)'}} />
      </div>
      {/* Joy */}
      <div style={{position: 'absolute', left: (1080 - W) / 2, top: 1920 - H - 40, width: W, height: H, filter: outline,
        opacity: sec.kind === 'tip' ? interpolate(t - sec.s, [0, .35], [1, 0], clamp) : 1, transform: sec.kind === 'tip' ? `translateY(${interpolate(t - sec.s, [0, .35], [0, 200], clamp)}px)` : undefined}}>
        {plan.joyMap ? plan.joyMap.map((r, i) => (
          <Sequence key={i} from={Math.round(r.t * fps)} durationInFrames={Math.round((i === plan.joyMap!.length - 1 ? plan.duration - r.t : plan.joyMap![i + 1].t - r.t) * fps)} layout="none">
            <OffthreadVideo src={staticFile(plan.joyMedia!)} transparent muted startFrom={Math.round(r.src * fps)} style={{position: 'absolute', width: '100%', height: '100%'}} />
          </Sequence>))
          : <OffthreadVideo src={staticFile(`${plan.media}/joy.webm`)} transparent muted style={{width: '100%', height: '100%'}} />}
      </div>
      {/* hook: flags of the native teachers' countries either side of Joy's face */}
      {(() => {
        const pts: [number, number, number][] = [[70, 1180, -8], [90, 1380, 6], [850, 1170, 7], [830, 1390, -6]];
        const flags = ['🇬🇧', '🇺🇸', '🇨🇦', '🇦🇺'];
        const pointSec = secs.find((x) => /^p\d$/.test(x.kind));
        const usePart = plan.props && (plan.part !== 1 || sec.kind !== 'hook');
        const show = sec.kind === 'hook' || (plan.props && /^p\d$/.test(sec.kind));
        if (!show) return null;
        const items = usePart ? plan.props! : flags;
        const s0 = usePart && sec.kind !== 'hook' ? (pointSec?.s ?? 0) : 0;
        return items.map((f, i) => [f, ...pts[i]] as [string, number, number, number]);
      })()?.map(([f, x, y, r], i) => {
        const k = sp(t, (sec.kind === 'hook' ? 0 : sec.s) + .2 + .15 * i, fps, 10);
        return <div key={i} style={{position: 'absolute', left: x as number, top: (y as number) + Math.sin(t * 2 + i) * 6, fontSize: 130, transform: `scale(${k}) rotate(${r}deg)`,
          filter: 'drop-shadow(0 8px 14px rgba(60,40,10,.35))'}}>{f as string}</div>;
      })}
      {sec.kind === 'books' && plan.books && <Books sec={sec} t={t} fps={fps} books={plan.books} title={plan.hookTitle ?? ['', '']} />}
      {/* DAY chip + yellow progress bar */}
      <div style={{position: 'absolute', top: 300, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
        <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 26, letterSpacing: 2, color: C.navy, background: C.yellow, borderRadius: 999, padding: '5px 20px'}}>DAY {plan.day}</div>
      </div>
      <div style={{position: 'absolute', top: 352, left: 90, right: 90, display: 'flex', alignItems: 'center', gap: 14}}>
        <div style={{flex: 1, height: 14, borderRadius: 7, background: 'rgba(255,255,255,.3)', overflow: 'hidden', boxShadow: '0 0 12px rgba(255,214,90,.35)'}}>
          <div style={{height: '100%', width: `${Math.min(100, (t / plan.duration) * 100)}%`, background: 'linear-gradient(90deg, #FFC93C, #FFE27A)', boxShadow: '0 0 10px rgba(255,214,90,.8)'}} /></div>
        <div style={{width: 84, textAlign: 'right', fontFamily: PRE, fontWeight: 900, fontSize: 28, color: C.yellow, textShadow: '0 2px 6px rgba(0,0,0,.6)'}}>{Math.min(100, Math.round((t / plan.duration) * 100))}%</div>
      </div>
      {sec.kind === 'hook' && (
        <div style={{position: 'absolute', top: 420, left: 60, right: 60, textAlign: 'center'}}>
          <div style={{display: 'inline-block', fontFamily: HAND, fontWeight: 700, fontSize: 40, color: C.navy, background: C.yellow, borderRadius: 12, padding: '0 18px', transform: 'rotate(-2deg)',
            opacity: hk}}>{plan.part ? `영유 상담 체크리스트 ${'①②③'[plan.part - 1]}` : '영유 상담 전 체크리스트 2편'}</div>
          <div style={{marginTop: 22, fontFamily: PRE, fontWeight: 900, fontSize: (plan.hookTitle?.[1]?.length ?? 0) > 10 ? 80 : 100, lineHeight: 1.12, color: C.white, textShadow: '0 4px 18px rgba(0,0,0,.7)', transform: `scale(${.85 + .15 * hk})`}}>
            {(plan.hookTitle ?? ['영유 선생님이', '자주 바뀐다면?'])[0]}<br /><span style={{color: C.yellow}}>{(plan.hookTitle ?? ['', '자주 바뀐다면?'])[1]}</span></div>
        </div>)}
      {sec.kind === 'intro' && <Intro sec={sec} t={t} fps={fps} />}
      {sec.kind === 'p1' && <P1 sec={sec} t={t} fps={fps} ticks={plan.ticks.p1 ?? []} />}
      {sec.kind === 'p2' && (() => {
        const sr = plan.series?.find((x) => t >= x.s && t < x.e);
        const near = plan.series?.find((x) => t >= x.e && t < x.e + .3);
        return <>
          <div style={{opacity: sr ? 0 : near ? interpolate(t, [near.e, near.e + .3], [0, 1], clamp) : 1}}><P2 sec={sec} t={t} fps={fps} ticks={plan.ticks.p2 ?? []} caps={plan.captions} /></div>
          {sr && <Series sr={sr} t={t} fps={fps} />}
        </>;
      })()}
      {sec.kind === 'p3' && <P3 sec={sec} t={t} fps={fps} ticks={plan.ticks.p3 ?? []} caps={plan.captions} />}
      {sec.kind === 'last' && <Last sec={sec} t={t} fps={fps} caps={plan.captions} />}
      {sec.kind === 'end' && <End sec={sec} t={t} fps={fps} />}
      {sec.kind === 'tip' && plan.tip && <TypeCard sec={sec} t={t} fps={fps} lines={plan.tip} span={plan.tipType ?? [.3, 6]} red={plan.tipRed} img={plan.tipImg} />}
      {sec.kind === 'bye' && <Follow sec={sec} t={t} fps={fps} next={plan.next} part={plan.part} />}
      {cap && (
        <div style={{position: 'absolute', left: 60, right: 60, top: 1305, height: 140, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
          {cap.text.includes('마크') && <div style={{position: 'absolute', top: -70, left: 0, right: 0, textAlign: 'center', fontSize: 76,
            transform: `scale(${sp(t, cap.s, fps, 10)})`, filter: 'drop-shadow(0 6px 10px rgba(0,0,0,.4))'}}>🇬🇧</div>}
          <Pre text={cap.text} style={{fontFamily: PRE, fontWeight: 800, fontSize: 52, lineHeight: 1.3, color: C.white, textShadow: '0 3px 12px rgba(0,0,0,.9), 0 0 4px rgba(0,0,0,.9)'}} />
        </div>)}
    </AbsoluteFill>
  );
};
