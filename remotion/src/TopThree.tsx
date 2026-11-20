// DAY 36 "유아교육전 다 돌고, 딱 3개만 골랐어요" (Joy, 20 Nov 2026): TOP 3 countdown, premium look (Joy: 고급진 느낌, 너무 유아틱하지 않게).
// Navy / cream / muted gold, Playfair Display for numbers and English, Pretendard for Korean, few emoji.
// Safe zone (BRAND.md, DAY 35 feedback): every text block sits between y 300 and y 1450, 70 px from the sides.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, OffthreadVideo, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

type Cap = {s: number; e: number; text: string; ko?: string; who?: string; vo?: boolean; phrase?: boolean};
type Sec = {kind: string; s: number; e: number; n?: number; title?: string; kicker?: string; big?: string; who?: string; cap?: string;
  lines?: string[]; card?: {at: number; title: string; body: string; en: string[]}; info?: {name: string; lines: string[]};
  phrases?: [string, string][]; play?: [string, string]};
export type TopPlan = {fps: number; day: number; media: string; duration: number; frames: number; captions: Cap[]; sections: Sec[]};

const C = {navy: '#121A2B', ink: '#0B1120', cream: '#F4EFE4', gold: '#C9A86A', goldHi: '#E2C68E', white: '#FFFFFF'};
const PRE = "'Pretendard', 'Noto Color Emoji', sans-serif";
const SERIF = "'Playfair Display', 'Pretendard', serif";
const SH = '0 2px 12px rgba(5,8,16,.75), 0 0 30px rgba(5,8,16,.45)';
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
const sp = (t: number, s: number, fps: number, damping = 16) => spring({frame: Math.round((t - s) * fps), fps, config: {damping, stiffness: 170, mass: .6}});
const fade = (t: number, s: number, e: number, d = .18) => interpolate(t, [s, s + d, e - d, e], [0, 1, 1, 0], clamp);
const Pre: React.FC<{text: string; style: React.CSSProperties}> = ({text, style}) => <div style={{whiteSpace: 'pre-line', ...style}}>{text}</div>;
const glass: React.CSSProperties = {background: 'rgba(11,17,32,.72)', border: `1.5px solid ${C.gold}`, borderRadius: 26, boxShadow: '0 24px 60px rgba(0,0,0,.45)', backdropFilter: 'blur(14px)'};

const Hairline: React.FC<{w: number; k: number}> = ({w, k}) => <div style={{height: 2, width: w * k, background: C.gold, margin: '0 auto'}} />;

const Hook: React.FC<{t: number; fps: number; sec: Sec; day: number}> = ({t, fps, sec, day}) => {
  const k = sp(t, 0, fps, 14), k2 = sp(t, .25, fps, 12);
  return (
    <>
      <div style={{position: 'absolute', top: 310, left: 70, right: 70, textAlign: 'center', opacity: k}}>
        <div style={{display: 'inline-block', fontFamily: PRE, fontWeight: 800, fontSize: 30, letterSpacing: 2, color: C.ink, background: C.goldHi, borderRadius: 999, padding: '6px 22px'}}>
          DAY {day} · 출간까지 매일 업로드</div>
        <div style={{marginTop: 14, fontFamily: PRE, fontWeight: 800, fontSize: 30, letterSpacing: 8, color: C.goldHi, textShadow: SH}}>{sec.kicker}</div>
        <Pre text={sec.title!} style={{marginTop: 12, fontFamily: PRE, fontWeight: 900, fontSize: 84, lineHeight: 1.12, color: C.white, textShadow: SH, transform: `translateY(${(1 - k) * 20}px)`}} />
      </div>
      <div style={{position: 'absolute', top: 1110, left: 0, right: 0, textAlign: 'center', transform: `scale(${.85 + .15 * k2})`, opacity: k2}}>
        <div style={{fontFamily: SERIF, fontStyle: 'italic', fontWeight: 600, fontSize: 200, lineHeight: 1, color: C.goldHi, textShadow: '0 10px 40px rgba(0,0,0,.6)'}}>{sec.big}</div>
        <div style={{marginTop: 10}}><Hairline w={420} k={k2} /></div>
      </div>
    </>
  );
};

// v2 hook: one question every parent feels, over the most surprising picture (the AI floor ball game)
const QHook: React.FC<{t: number; fps: number; sec: Sec; day: number}> = ({t, fps, sec, day}) => {
  const k = sp(t, 0, fps, 13);
  return (
    <div style={{position: 'absolute', top: 330, left: 70, right: 70, textAlign: 'center'}}>
      <div style={{display: 'inline-block', fontFamily: PRE, fontWeight: 800, fontSize: 30, letterSpacing: 2, color: C.ink, background: C.goldHi, borderRadius: 999, padding: '6px 22px'}}>
        DAY {day} · 출간까지 매일 업로드</div>
      <Pre text={sec.title!} style={{marginTop: 26, fontFamily: PRE, fontWeight: 900, fontSize: 104, lineHeight: 1.12, color: C.white, textShadow: SH,
        transform: `scale(${.9 + .1 * k})`, opacity: k}} />
      <div style={{marginTop: 22}}><Hairline w={380} k={k} /></div>
    </div>
  );
};

const Cta: React.FC<{t: number; fps: number; s: number; text: string}> = ({t, fps, s, text}) => {
  const k = sp(t, s, fps, 12);
  return (
    <div style={{position: 'absolute', top: 560, left: 110, right: 110, ...glass, background: 'rgba(244,239,228,.95)', padding: '30px 30px', textAlign: 'center',
      opacity: k, transform: `scale(${.9 + .1 * k})`}}>
      <Pre text={text} style={{fontFamily: PRE, fontWeight: 900, fontSize: 56, lineHeight: 1.25, color: C.navy}} />
    </div>
  );
};

const Rank: React.FC<{t: number; fps: number; sec: Sec}> = ({t, fps, sec}) => {
  const k = sp(t, sec.s, fps, 15), k2 = sp(t, sec.s + .22, fps, 14);
  return (
    <>
      <AbsoluteFill style={{background: 'rgba(8,12,22,.62)', opacity: fade(t, sec.s, sec.e, .12)}} />
      <div style={{position: 'absolute', top: 470, left: 0, right: 0, textAlign: 'center'}}>
        <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 28, letterSpacing: 10, color: C.gold, opacity: k}}>TOP 3 · {4 - (sec.n ?? 0)} / 3</div>
        <div style={{display: 'flex', justifyContent: 'center', alignItems: 'baseline', gap: 8, marginTop: 6, transform: `scale(${1.18 - .18 * k})`, opacity: k}}>
          <span style={{fontFamily: SERIF, fontStyle: 'italic', fontWeight: 600, fontSize: 120, color: C.gold}}>No.</span>
          <span style={{fontFamily: SERIF, fontWeight: 700, fontSize: 400, lineHeight: .95, color: C.cream}}>{sec.n}</span>
        </div>
        <div style={{marginTop: 18}}><Hairline w={360} k={k2} /></div>
        <div style={{marginTop: 26, fontFamily: PRE, fontWeight: 800, fontSize: 66, letterSpacing: 2, color: C.white, opacity: k2, transform: `translateY(${(1 - k2) * 18}px)`, textShadow: SH}}>{sec.title}</div>
      </div>
    </>
  );
};

// small chip that says which pick we are on
const Chip: React.FC<{n: number; title: string; t: number; s: number; fps: number; day: number}> = ({n, title, t, s, fps, day}) => {
  const k = sp(t, s, fps, 18);
  return (
    <div style={{position: 'absolute', top: 310, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: k}}>
      <div style={{...glass, borderRadius: 999, padding: '10px 30px', display: 'flex', alignItems: 'baseline', gap: 16}}>
        <span style={{fontFamily: PRE, fontWeight: 800, fontSize: 24, color: C.gold, letterSpacing: 2}}>DAY {day}</span>
        <span style={{fontFamily: SERIF, fontStyle: 'italic', fontWeight: 600, fontSize: 40, color: C.goldHi}}>No.{n}</span>
        <span style={{fontFamily: PRE, fontWeight: 800, fontSize: 32, color: C.cream}}>{title}</span>
      </div>
    </div>
  );
};

const Info: React.FC<{t: number; s: number; fps: number; name: string; lines: string[]; top?: number}> = ({t, s, fps, name, lines, top = 420}) => {
  const k = sp(t, s, fps, 17);
  return (
    <div style={{position: 'absolute', top, left: 90, right: 90, ...glass, padding: '30px 36px', opacity: k, transform: `translateY(${(1 - k) * 24}px)`}}>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 26, letterSpacing: 6, color: C.gold}}>INFO</div>
      <div style={{marginTop: 6, fontFamily: PRE, fontWeight: 900, fontSize: 48, color: C.white}}>{name}</div>
      {lines.map((l, i) => <div key={i} style={{marginTop: 10, fontFamily: PRE, fontWeight: 700, fontSize: 36, color: C.cream, opacity: sp(t, s + .25 + .2 * i, fps)}}>· {l}</div>)}
    </div>
  );
};

const TestCard: React.FC<{t: number; s: number; fps: number; card: NonNullable<Sec['card']>}> = ({t, s, fps, card}) => {
  const k = sp(t, s, fps, 16);
  return (
    <div style={{position: 'absolute', top: 420, left: 90, right: 90, ...glass, padding: '34px 40px', opacity: k, transform: `scale(${.94 + .06 * k})`}}>
      <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 54, color: C.goldHi}}>{card.title}</div>
      <div style={{marginTop: 10, fontFamily: PRE, fontWeight: 700, fontSize: 36, lineHeight: 1.35, color: C.cream}}>{card.body}</div>
      <div style={{marginTop: 18}}>{card.en.map((e, i) => (
        <div key={i} style={{fontFamily: SERIF, fontStyle: 'italic', fontWeight: 600, fontSize: 50, color: C.white, opacity: sp(t, s + .4 + .35 * i, fps), marginTop: 4}}>“{e}”</div>))}</div>
    </div>
  );
};

const Phrase: React.FC<{t: number; fps: number; c: Cap; i: number; n: number}> = ({t, fps, c, i, n}) => {
  const k = sp(t, c.s, fps, 13);
  return (
    <div style={{position: 'absolute', top: 560, left: 70, right: 70, textAlign: 'center'}}>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 28, letterSpacing: 8, color: C.gold}}>PLAY ENGLISH · {i + 1}/{n}</div>
      <div style={{marginTop: 14, fontFamily: SERIF, fontStyle: 'italic', fontWeight: 600, fontSize: 116, lineHeight: 1.05, color: C.white, textShadow: SH,
        transform: `translateY(${(1 - k) * 40}px)`, opacity: k}}>{c.text}</div>
      <div style={{marginTop: 18}}><Hairline w={300} k={k} /></div>
      <div style={{marginTop: 16, fontFamily: PRE, fontWeight: 800, fontSize: 46, color: C.cream, opacity: sp(t, c.s + .15, fps), textShadow: SH}}>{c.ko}</div>
    </div>
  );
};

const End: React.FC<{t: number; fps: number; sec: Sec}> = ({t, fps, sec}) => {
  const k = sp(t, sec.s, fps, 16);
  return (
    <div style={{position: 'absolute', top: 420, left: 90, right: 90, background: C.cream, borderRadius: 30, padding: '40px 40px 36px', textAlign: 'center',
      boxShadow: '0 30px 70px rgba(0,0,0,.5)', border: `2px solid ${C.gold}`, opacity: k, transform: `translateY(${(1 - k) * 40}px)`}}>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 26, letterSpacing: 3, color: '#8A6A35'}}>DAY 36 · 출간까지 매일 업로드</div>
      <Img src={staticFile('brand/logo-full.png')} style={{height: 150, objectFit: 'contain', marginTop: 10}} />
      <div style={{marginTop: 18, fontFamily: PRE, fontWeight: 900, fontSize: 54, color: C.navy}}>저장해 두고 아이랑 해 보세요</div>
      <div style={{marginTop: 18, display: 'flex', justifyContent: 'center', gap: 14}}>
        {['📌 저장', '📤 공유', '+ 팔로우'].map((x, i) => <div key={i} style={{fontFamily: PRE, fontWeight: 800, fontSize: 32, color: i === 2 ? C.cream : C.navy,
          background: i === 2 ? C.navy : 'transparent', border: `2px solid ${C.navy}`, borderRadius: 999, padding: '8px 24px', opacity: sp(t, sec.s + .3 + .15 * i, fps)}}>{x}</div>)}
      </div>
      <div style={{marginTop: 20, fontFamily: SERIF, fontStyle: 'italic', fontWeight: 600, fontSize: 52, color: '#8A6A35'}}>@thebearandjoy</div>
    </div>
  );
};

export const TopThree: React.FC<{plan: TopPlan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const t = frame / fps;
  const secs = plan.sections;
  const si = Math.max(0, secs.findIndex((x) => t >= x.s && t < x.e)); const sec = secs[si] ?? secs[secs.length - 1];
  const cur = [...secs.slice(0, si + 1)].reverse().find((x) => x.kind === 'rank');  // which pick we are on
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const drift = 1.03 + .012 * Math.sin(t * .6);
  const showChip = cur && !['rank', 'hook', 'q', 'end'].includes(sec.kind) && si > secs.indexOf(cur);
  const phrases = plan.captions.filter((c) => c.phrase);
  return (
    <AbsoluteFill style={{background: C.ink, overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `scale(${drift})`}}>
        <OffthreadVideo src={staticFile(`${plan.media}/bg.mp4`)} muted style={{width: '100%', height: '100%'}} />
      </AbsoluteFill>
      {/* premium grade: soft vignette + darker top/bottom for legibility */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 80% 70% at 50% 48%, rgba(0,0,0,0) 55%, rgba(5,8,16,.55) 100%)'}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(8,12,22,.55) 0%, rgba(8,12,22,0) 30%, rgba(8,12,22,0) 58%, rgba(8,12,22,.6) 82%, rgba(8,12,22,.75) 100%)'}} />
      {sec.kind === 'q' && <QHook t={t} fps={fps} sec={sec} day={plan.day} />}
      {(sec as Sec & {cta?: string}).cta && <Cta t={t} fps={fps} s={secs.find((x) => (x as Sec & {cta?: string}).cta)!.s + .2} text={(sec as Sec & {cta?: string}).cta!} />}
      {sec.kind === 'hook' && <Hook t={t} fps={fps} sec={sec} day={plan.day} />}
      {sec.kind === 'rank' && <Rank t={t} fps={fps} sec={sec} />}
      {showChip && cur && <Chip n={cur.n!} title={cur.title!} t={t} s={cur.e} fps={fps} day={plan.day} />}
      {sec.kind === 'vo' && sec.card && plan.captions.filter((c) => c.vo && c.s >= sec.s - .01 && c.s < sec.e)[sec.card.at] &&
        t >= plan.captions.filter((c) => c.vo && c.s >= sec.s - .01 && c.s < sec.e)[sec.card.at].s &&
        <TestCard t={t} s={plan.captions.filter((c) => c.vo && c.s >= sec.s - .01 && c.s < sec.e)[sec.card.at].s} fps={fps} card={sec.card} />}
      {sec.kind === 'vo' && sec.info && <Info t={t} s={sec.s + .3} fps={fps} name={sec.info.name} lines={sec.info.lines} />}
      {sec.kind === 'vo' && sec.play && t > (sec.s + sec.e) / 2 && (
        <div style={{position: 'absolute', top: 820, left: 90, right: 90, ...glass, padding: '22px 30px', textAlign: 'center', opacity: sp(t, (sec.s + sec.e) / 2, fps)}}>
          <div style={{fontFamily: SERIF, fontStyle: 'italic', fontWeight: 600, fontSize: 52, color: C.white}}>“{sec.play[0]}”</div>
          <div style={{marginTop: 6, fontFamily: PRE, fontWeight: 700, fontSize: 34, color: C.cream}}>{sec.play[1]}</div>
        </div>)}
      {cap && cap.phrase && <Phrase t={t} fps={fps} c={cap} i={phrases.indexOf(cap)} n={phrases.length} />}
      {sec.kind === 'end' && <End t={t} fps={fps} sec={sec} />}
      {cap && !cap.phrase && (
        <div style={{position: 'absolute', left: 70, right: 70, top: 1230, textAlign: 'center', opacity: fade(t, cap.s, cap.e, .1)}}>
          {cap.who && <div style={{display: 'inline-block', marginBottom: 12, fontFamily: PRE, fontWeight: 800, fontSize: 28, letterSpacing: 3, color: C.ink, background: C.goldHi,
            borderRadius: 999, padding: '4px 18px'}}>{cap.who === 'Mark' ? 'Mark T · 영국 원어민 선생님' : 'Joy · Bear & Joy 공동 저자'}</div>}
          <Pre text={cap.text} style={{fontFamily: /[A-Za-z]/.test(cap.text) && !/[가-힣]/.test(cap.text) ? SERIF : PRE, fontStyle: /[가-힣]/.test(cap.text) ? 'normal' : 'italic',
            fontWeight: /[가-힣]/.test(cap.text) ? 700 : 600, fontSize: /[가-힣]/.test(cap.text) ? 50 : 54, lineHeight: 1.32, color: C.white, textShadow: SH}} />
          {cap.ko && <div style={{marginTop: 8, fontFamily: PRE, fontWeight: 700, fontSize: 38, color: C.cream, textShadow: SH}}>{cap.ko}</div>}
        </div>)}
    </AbsoluteFill>
  );
};
