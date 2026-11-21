// DAY 37 "영유 상담 때 꼭 확인할 3가지" (Joy, 21 Nov 2026).
// Joy as a white-outlined sticker at the bottom; above her a checklist card that fills in as she talks (saveable),
// fair book footage behind the textbook story. Premium navy / cream / gold (DAY 36 look). Text only in y 300–1450.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

type Cap = {s: number; e: number; text: string; sec: string};
type Sec = {kind: string; s: number; e: number};
export type CheckPlan = {fps: number; day: number; part?: number; media: string; duration: number; frames: number; captions: Cap[]; sections: Sec[]; ticks: Record<string, number[]>};

const C = {navy: '#121A2B', ink: '#0B1120', cream: '#F6F1E6', paper: '#FFFCF5', gold: '#C9A86A', goldHi: '#E2C68E', white: '#FFFFFF', red: '#D9534F', muted: '#6B6255'};
const PRE = "'Pretendard', 'Noto Color Emoji', sans-serif";
const SERIF = "'Playfair Display', 'Pretendard', serif";
const SH = '0 2px 12px rgba(5,8,16,.8), 0 0 30px rgba(5,8,16,.5)';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const FONTS: [string, string, string, string][] = [
  ['Pretendard', 'normal', '700', 'Pretendard-Bold.woff2'], ['Pretendard', 'normal', '800', 'Pretendard-ExtraBold.woff2'],
  ['Pretendard', 'normal', '900', 'Pretendard-Black.woff2'], ['Noto Color Emoji', 'normal', '400', 'Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf'],
  ['Playfair Display', 'italic', '600', 'nuFRD-vYSZviVYUb_rj3ij__anPXDTnCjmHKM4nYO7KN_naUbtY.ttf'],
  ['Playfair Display', 'normal', '700', 'nuFvD-vYSZviVYUb_rj3ij__anPXJzDwcbmjWBN2PKeiukDQ.ttf'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([f, st, w, file]) => new FontFace(f, `url(${staticFile('fonts/' + file)})`, {style: st, weight: w}).load().then((x) => document.fonts.add(x))))
      .then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
  }, [h]);
};
const sp = (t: number, s: number, fps: number, damping = 15) => spring({frame: Math.round((t - s) * fps), fps, config: {damping, stiffness: 180, mass: .6}});
const Pre: React.FC<{text: string; style: React.CSSProperties}> = ({text, style}) => <div style={{whiteSpace: 'pre-line', ...style}}>{text}</div>;

const PANEL: React.CSSProperties = {position: 'absolute', top: 395, left: 70, right: 70, height: 440, borderRadius: 34, overflow: 'hidden', boxShadow: '0 26px 60px rgba(0,0,0,.5)'};

const POINTS: Record<string, {n: string; title: string; ticks: string[]}> = {
  p1: {n: '1', title: '교재 진도', ticks: ['지금 교재, 어디까지 진행됐나요?', '교재비는 어떻게 책정되나요?']},
  p2: {n: '2', title: '원어민 강사의 교육 경험', ticks: ['유아교육에 대한 이해가 있나요?', '아이들을 가르친 경험은 얼마나?', '학원 교육 방식으로 교육받았나요?']},
  p3: {n: '3', title: '아이들의 하루 일과', ticks: ['실제 시간표 확인하기', '하루에 얼마나 움직이나요?', '자유 놀이 시간은 충분한가요?']},
};

const Tick: React.FC<{text: string; on: number; t: number; fps: number; dark?: boolean}> = ({text, on, t, fps, dark}) => {
  const k = sp(t, on, fps, 13); const shown = t >= on;
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 14, marginTop: 10, opacity: shown ? 1 : .35}}>
      <div style={{width: 46, height: 46, borderRadius: 12, border: `3px solid ${C.gold}`, display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: shown ? C.gold : 'transparent', transform: `scale(${shown ? .8 + .2 * k : 1})`}}>
        {shown && <span style={{color: C.white, fontFamily: PRE, fontWeight: 900, fontSize: 32}}>✓</span>}</div>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 35, color: dark ? C.cream : C.navy}}>{text}</div>
    </div>
  );
};

// the little picture for each point, above its checklist
const Graphic: React.FC<{kind: string; t: number; s: number; fps: number; ticks?: number[]}> = ({kind, t, s, fps, ticks}) => {
  const k = interpolate(t, [s + .3, s + 1.6], [0, 1], clamp);
  if (kind === 'p1') return (
    <div style={{marginTop: 18}}>
      <div style={{display: 'flex', justifyContent: 'space-between', fontFamily: PRE, fontWeight: 800, fontSize: 28, color: C.muted}}>
        <span>📖 지금 반 교재 진도</span><span style={{color: C.red}}>{Math.round(90 * k)}% 끝</span></div>
      <div style={{marginTop: 8, height: 26, borderRadius: 13, background: '#E7DFCF', overflow: 'hidden'}}>
        <div style={{height: '100%', width: `${90 * k}%`, background: `linear-gradient(90deg, ${C.gold}, ${C.red})`}} /></div>
      <div style={{marginTop: 6, fontFamily: PRE, fontWeight: 700, fontSize: 26, color: C.muted}}>중간에 들어가면 마지막 단원만 하고 끝날 수도</div>
    </div>);
  if (kind === 'p2') return (
    <div style={{marginTop: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 22, opacity: sp(t, s + .3, fps)}}>
      <span style={{fontFamily: PRE, fontWeight: 900, fontSize: 46, color: C.navy}}>원어민</span>
      <span style={{fontFamily: SERIF, fontWeight: 700, fontSize: 80, color: C.red, lineHeight: 1}}>≠</span>
      <span style={{fontFamily: PRE, fontWeight: 900, fontSize: 46, color: C.navy}}>유아교육 전문가</span>
    </div>);
  // p3: a day split into desk time and play time
  const desk = 62 * k;
  return (
    <div style={{marginTop: 16}}>
      <div style={{display: 'flex', height: 54, borderRadius: 14, overflow: 'hidden', fontFamily: PRE, fontWeight: 800, fontSize: 26}}>
        <div style={{width: `${desk}%`, background: C.navy, color: C.cream, display: 'flex', alignItems: 'center', justifyContent: 'center', whiteSpace: 'nowrap'}}>{k > .5 && '책상 수업'}</div>
        <div style={{flex: 1, background: C.goldHi, color: C.navy, display: 'flex', alignItems: 'center', justifyContent: 'center', whiteSpace: 'nowrap'}}>놀이</div>
      </div>
      {/* Joy (21 Nov): once free play is ticked, the note becomes the why */}
      {t >= (ticks?.[2] ?? 1e9)
        ? <div style={{marginTop: 6, fontFamily: PRE, fontWeight: 900, fontSize: 28, color: C.red, opacity: sp(t, ticks![2], fps)}}>💡 앉아서 공부만 하면, 영어 자체를 싫어하게 될 수 있어요</div>
        : <div style={{marginTop: 6, fontFamily: PRE, fontWeight: 700, fontSize: 26, color: C.muted}}>'놀이형'이어도 앉아 있는 시간이 길 수 있어요</div>}
    </div>);
};

const PointCard: React.FC<{kind: string; sec: Sec; t: number; fps: number; ticks: number[]}> = ({kind, sec, t, fps, ticks}) => {
  const P = POINTS[kind]; const k = sp(t, sec.s, fps, 16);
  return (
    <div style={{...PANEL, background: C.paper, border: `3px solid ${C.gold}`, padding: '24px 34px', transform: `translateY(${(1 - k) * 50}px) scale(${.96 + .04 * k})`, opacity: k}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 18}}>
        <div style={{width: 74, height: 74, borderRadius: 37, background: C.navy, display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: SERIF, fontWeight: 700, fontSize: 48, color: C.goldHi}}>{P.n}</div>
        <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 50, color: C.navy}}>{P.title}</div>
      </div>
      <Graphic kind={kind} t={t} s={sec.s} fps={fps} ticks={ticks} />
      <div style={{marginTop: 8}}>{P.ticks.map((x, i) => <Tick key={i} text={x} on={ticks[i] ?? 1e9} t={t} fps={fps} />)}</div>
    </div>
  );
};

const Hook: React.FC<{sec: Sec; t: number; fps: number; caps: Cap[]}> = ({sec, t, fps, caps}) => {
  const c2 = caps.filter((c) => c.sec === 'hook')[1];
  const second = c2 && t >= c2.s;
  return (
    <div style={{position: 'absolute', top: 420, left: 70, right: 70, textAlign: 'center'}}>
      <div style={{display: 'inline-block', fontFamily: PRE, fontWeight: 800, fontSize: 30, color: C.ink, background: C.goldHi, borderRadius: 999, padding: '6px 20px',
        opacity: sp(t, 0, fps)}}>영유 보내기 전, 이것 모르면 손해</div>
      {!second && <div style={{marginTop: 26, fontFamily: PRE, fontWeight: 900, fontSize: 92, lineHeight: 1.12, color: C.white, textShadow: SH,
        transform: `scale(${.85 + .15 * sp(t, .1, fps, 12)})`}}>교재비는<br />다 냈는데 💸</div>}
      {second && <div style={{marginTop: 26, fontFamily: PRE, fontWeight: 900, fontSize: 88, lineHeight: 1.12, color: C.white, textShadow: SH,
        transform: `scale(${.85 + .15 * sp(t, c2.s, fps, 12)})`}}>몇 페이지만 하고<br /><span style={{color: C.goldHi}}>새 책 그대로 집에?!</span></div>}
      <div style={{marginTop: 22, display: 'inline-block', fontFamily: PRE, fontWeight: 800, fontSize: 36, color: C.navy, background: C.cream, borderRadius: 16,
        padding: '10px 22px', opacity: sp(t, .8, fps), transform: `translateY(${(1 - sp(t, .8, fps)) * 20}px)`}}>📌 끝까지 보면 '영유 상담 체크리스트' 완성</div>
    </div>
  );
};

// Part 2 opener: the line that stops native-teacher assumptions
const Hook2: React.FC<{sec: Sec; t: number; fps: number}> = ({sec, t, fps}) => (
  <div style={{position: 'absolute', top: 400, left: 70, right: 70, textAlign: 'center'}}>
    <div style={{display: 'inline-block', fontFamily: PRE, fontWeight: 800, fontSize: 30, color: C.ink, background: C.goldHi, borderRadius: 999, padding: '6px 20px',
      opacity: sp(t, 0, fps)}}>영유 보내기 전, 이것 모르면 손해</div>
    <div style={{marginTop: 26, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 18, transform: `scale(${.85 + .15 * sp(t, .1, fps, 12)})`}}>
      <span style={{fontFamily: PRE, fontWeight: 900, fontSize: 96, color: C.white, textShadow: SH}}>원어민</span>
      <span style={{fontFamily: SERIF, fontWeight: 700, fontSize: 130, color: C.goldHi, lineHeight: 1, textShadow: SH}}>≠</span>
    </div>
    <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 88, color: C.goldHi, textShadow: SH, opacity: sp(t, .5, fps)}}>유아 영어 전문가</div>
    <div style={{marginTop: 22, display: 'inline-block', fontFamily: PRE, fontWeight: 800, fontSize: 36, color: C.navy, background: C.cream, borderRadius: 16,
      padding: '10px 22px', opacity: sp(t, 1.0, fps)}}>📌 끝까지 보면 '영유 상담 체크리스트' 완성</div>
  </div>
);

const Intro: React.FC<{sec: Sec; t: number; fps: number}> = ({sec, t, fps}) => {
  const k = sp(t, sec.s, fps, 15);
  return (
    <div style={{...PANEL, background: C.navy, border: `3px solid ${C.gold}`, padding: '40px 44px', opacity: k, transform: `scale(${.94 + .06 * k})`}}>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 30, letterSpacing: 6, color: C.gold}}>영유 상담 전 체크리스트</div>
      <div style={{marginTop: 10, fontFamily: PRE, fontWeight: 900, fontSize: 64, lineHeight: 1.15, color: C.white}}>상담 때 꼭 확인할<br /><span style={{color: C.goldHi}}>3가지</span></div>
      <div style={{marginTop: 26, display: 'flex', gap: 18}}>
        {['1', '2', '3'].map((n, i) => (
          <div key={n} style={{flex: 1, height: 104, borderRadius: 20, border: `2px dashed ${C.gold}`, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
            opacity: sp(t, sec.s + .3 + .2 * i, fps), fontFamily: SERIF, fontWeight: 700, fontSize: 52, color: C.goldHi}}>{n}<span style={{fontSize: 40}}>🔒</span></div>))}
      </div>
    </div>
  );
};

const Next: React.FC<{sec: Sec; t: number; fps: number; caps: Cap[]}> = ({sec, t, fps, caps}) => {
  const k = sp(t, sec.s, fps, 15); const cs = caps.filter((c) => c.sec === 'next');
  const items = [['🔄', '선생님이 자주 바뀐다면?', cs[1]], ['🏫', '운영진은 아이 교육을 이해할까?', cs[2]]] as const;
  return (
    <div style={{...PANEL, background: C.navy, border: `3px solid ${C.gold}`, padding: '36px 42px', opacity: k}}>
      <div style={{fontFamily: SERIF, fontStyle: 'italic', fontWeight: 600, fontSize: 40, color: C.goldHi}}>Next episode</div>
      <div style={{marginTop: 4, fontFamily: PRE, fontWeight: 900, fontSize: 56, color: C.white}}>영유의 진짜 문제 👀</div>
      {items.map(([e, txt, c], i) => {
        const on = c ? t >= c.s : false;
        return (
          <div key={i} style={{marginTop: 20, display: 'flex', alignItems: 'center', gap: 16, background: 'rgba(255,255,255,.08)', borderRadius: 18, padding: '16px 22px',
            filter: on ? 'none' : 'blur(7px)', opacity: on ? 1 : .6}}>
            <span style={{fontSize: 44}}>{e}</span><span style={{fontFamily: PRE, fontWeight: 800, fontSize: 40, color: C.cream}}>{txt}</span></div>);
      })}
      <div style={{marginTop: 22, fontFamily: PRE, fontWeight: 800, fontSize: 32, color: C.goldHi, opacity: sp(t, (cs[3]?.s ?? sec.e) , fps)}}>다음 영상 놓치지 않게 팔로우 · @thebearandjoy</div>
    </div>
  );
};

const Tip: React.FC<{sec: Sec; t: number; fps: number; ticks: number[]}> = ({sec, t, fps, ticks}) => {
  const k = sp(t, sec.s, fps, 15);
  const items = [['🏃', '신체 활동'], ['🧸', '자유로운 놀이'], ['🌱', '다양한 경험']];
  return (
    <div style={{...PANEL, background: C.navy, border: `3px solid ${C.gold}`, padding: '30px 38px', opacity: k, transform: `scale(${.95 + .05 * k})`}}>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 28, letterSpacing: 4, color: C.gold}}>PLUS TIP</div>
      <div style={{marginTop: 6, fontFamily: PRE, fontWeight: 900, fontSize: 54, color: C.white}}>학습형 영유에 다닌다면?</div>
      <div style={{marginTop: 8, fontFamily: PRE, fontWeight: 700, fontSize: 32, color: C.cream}}>정규 수업 후에는 '학습 더'보다</div>
      <div style={{marginTop: 18, display: 'flex', gap: 14}}>
        {items.map(([e, x], i) => {
          const on = t >= (ticks[i] ?? 1e9); const q = sp(t, ticks[i] ?? 1e9, fps, 12);
          return <div key={i} style={{flex: 1, height: 130, borderRadius: 20, background: on ? C.goldHi : 'rgba(255,255,255,.08)', display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center', transform: `scale(${on ? .85 + .15 * q : 1})`}}>
            <span style={{fontSize: 50}}>{e}</span><span style={{fontFamily: PRE, fontWeight: 900, fontSize: 30, color: on ? C.navy : C.cream}}>{x}</span></div>;
        })}
      </div>
    </div>
  );
};

const End1: React.FC<{sec: Sec; t: number; fps: number}> = ({sec, t, fps}) => {
  const k = sp(t, sec.s, fps, 15);
  return (
    <div style={{...PANEL, background: C.navy, border: `3px solid ${C.gold}`, padding: '34px 42px', opacity: k, transform: `scale(${.95 + .05 * k})`}}>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 30, letterSpacing: 6, color: C.gold}}>영유 상담 체크리스트</div>
      {[['1', '교재 진도 · 교재비', true], ['2', '원어민 강사의 교육 경험', false], ['3', '아이들의 하루 일과', false]].map(([n, x, open], i) => (
        <div key={i} style={{marginTop: 18, display: 'flex', alignItems: 'center', gap: 16, opacity: sp(t, sec.s + .15 * i, fps)}}>
          <div style={{width: 54, height: 54, borderRadius: 27, background: open ? C.goldHi : 'transparent', border: `2px solid ${C.gold}`, color: open ? C.navy : C.goldHi,
            fontFamily: SERIF, fontWeight: 700, fontSize: 32, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{n as string}</div>
          <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 40, color: C.cream, filter: open ? 'none' : 'blur(8px)'}}>{x as string}</div>
          <span style={{marginLeft: 'auto', fontSize: 38}}>{open ? '✅' : '🔒'}</span>
        </div>))}
      <div style={{marginTop: 26, fontFamily: PRE, fontWeight: 900, fontSize: 40, color: C.goldHi, opacity: sp(t, sec.s + .6, fps)}}>② ③은 다음 영상에서 공개 👀</div>
      <div style={{marginTop: 8, fontFamily: PRE, fontWeight: 800, fontSize: 30, color: C.cream, opacity: sp(t, sec.s + .8, fps)}}>놓치지 않게 팔로우 · @thebearandjoy</div>
    </div>
  );
};

const End: React.FC<{sec: Sec; t: number; fps: number}> = ({sec, t, fps}) => {
  const k = sp(t, sec.s, fps, 15);
  const rows = [['1', '교재 진도 · 교재비'], ['2', '원어민 강사의 유아교육 경험'], ['3', '하루 일과 · 놀이 시간']];
  return (
    <div style={{...PANEL, background: C.paper, border: `3px solid ${C.gold}`, padding: '32px 40px', opacity: k, transform: `scale(${.95 + .05 * k})`}}>
      <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 48, color: C.navy}}>📌 영유 상담 체크리스트</div>
      {rows.map(([n, x], i) => (
        <div key={n} style={{marginTop: 18, display: 'flex', alignItems: 'center', gap: 16, opacity: sp(t, sec.s + .2 + .15 * i, fps)}}>
          <div style={{width: 52, height: 52, borderRadius: 26, background: C.navy, color: C.goldHi, fontFamily: SERIF, fontWeight: 700, fontSize: 32,
            display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{n}</div>
          <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 40, color: C.navy}}>{x}</div><span style={{marginLeft: 'auto', color: C.gold, fontSize: 40, fontWeight: 900}}>✓</span>
        </div>))}
      <div style={{marginTop: 24, display: 'flex', gap: 12, flexWrap: 'wrap'}}>
        {['📌 저장해서 상담 때 보기', '📤 영유 고민하는 친구에게', '💬 궁금한 점은 댓글로'].map((x, i) => (
          <div key={i} style={{fontFamily: PRE, fontWeight: 800, fontSize: 27, color: C.navy, border: `2px solid ${C.navy}`, borderRadius: 999, padding: '6px 16px',
            opacity: sp(t, sec.s + .7 + .15 * i, fps)}}>{x}</div>))}
      </div>
    </div>
  );
};

export const Checklist: React.FC<{plan: CheckPlan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const t = frame / fps;
  const secs = plan.sections; const sec = secs.find((x) => t >= x.s && t < x.e) ?? secs[secs.length - 1];
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const bump = 1 + .025 * (1 - sp(t, sec.s, fps, 12)) * (sec.s > 0 ? 1 : 0);
  const outline = 'drop-shadow(6px 0 0 #fff) drop-shadow(-6px 0 0 #fff) drop-shadow(0 6px 0 #fff) drop-shadow(0 -6px 0 #fff) drop-shadow(0 24px 34px rgba(0,0,0,.55))';
  const W = 1080 * .64, H = 1920 * .64, DROP = -40;   // Joy (21 Nov): captions at hand/chest height, never near the face
  return (
    <AbsoluteFill style={{background: `radial-gradient(ellipse 90% 70% at 50% 30%, #22304F 0%, ${C.navy} 55%, ${C.ink} 100%)`, overflow: 'hidden'}}>
      {/* stock scenes (Pexels) behind everything, dimmed so the cards and Joy stay clear */}
      <AbsoluteFill style={{transform: `scale(${1.04 + .01 * Math.sin(t * .5)})`}}>
        <OffthreadVideo src={staticFile(`${plan.media}/bg.mp4`)} muted style={{width: '100%', height: '100%'}} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,12,22,.55) 0%, rgba(8,12,22,.35) 40%, rgba(8,12,22,.6) 75%, rgba(8,12,22,.8) 100%)'}} />
      {/* Joy: white-outlined sticker at the bottom */}
      <div style={{position: 'absolute', left: (1080 - W) / 2, top: 1920 - H + DROP, width: W, height: H, filter: outline, transform: `scale(${bump})`, transformOrigin: '50% 100%'}}>
        <OffthreadVideo src={staticFile(`${plan.media}/joy.webm`)} transparent muted style={{width: '100%', height: '100%'}} />
      </div>
      <div style={{position: 'absolute', top: 300, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
        <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 26, letterSpacing: 2, color: C.ink, background: C.goldHi, borderRadius: 999, padding: '5px 20px'}}>
          DAY {plan.day}</div>
      </div>
      <div style={{position: 'absolute', top: 352, left: 90, right: 90, display: 'flex', alignItems: 'center', gap: 14}}>
        <div style={{flex: 1, height: 10, borderRadius: 5, background: 'rgba(255,255,255,.22)', overflow: 'hidden'}}>
          <div style={{height: '100%', width: `${Math.min(100, (t / plan.duration) * 100)}%`, background: `linear-gradient(90deg, ${C.gold}, ${C.goldHi})`}} /></div>
        <div style={{width: 80, textAlign: 'right', fontFamily: PRE, fontWeight: 800, fontSize: 26, color: C.goldHi}}>{Math.min(100, Math.round((t / plan.duration) * 100))}%</div>
      </div>
      {sec.kind === 'hook' && <Hook sec={sec} t={t} fps={fps} caps={plan.captions} />}
      {sec.kind === 'hook2' && <Hook2 sec={sec} t={t} fps={fps} />}
      {sec.kind === 'intro' && <Intro sec={sec} t={t} fps={fps} />}
      {POINTS[sec.kind] && <PointCard kind={sec.kind} sec={sec} t={t} fps={fps} ticks={plan.ticks[sec.kind] ?? []} />}
      {sec.kind === 'next' && <Next sec={sec} t={t} fps={fps} caps={plan.captions} />}
      {sec.kind === 'p4' && <Tip sec={sec} t={t} fps={fps} ticks={plan.ticks.p4 ?? []} />}
      {sec.kind === 'end1' && <End1 sec={sec} t={t} fps={fps} />}
      {(sec.kind === 'end' || sec.kind === 'end2') && <End sec={sec} t={t} fps={fps} />}
      {cap && (
        <div style={{position: 'absolute', left: 60, right: 60, top: 1305, height: 140, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
          <Pre text={cap.text} style={{fontFamily: PRE, fontWeight: 800, fontSize: 52, lineHeight: 1.3, color: C.white, textShadow: '0 3px 12px rgba(0,0,0,.9), 0 0 4px rgba(0,0,0,.9)'}} />
        </div>)}
    </AbsoluteFill>
  );
};
