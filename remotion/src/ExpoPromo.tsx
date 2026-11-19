// DAY 35 유아교육전 홍보 릴스 (Joy, 19 Nov 2026): share-first promo.
// Intro: Joy's own clip as a white-outlined sticker bottom-left, fast 1-second cuts of the fair behind her, each stamped with what it shows.
// Then Joy's voice-over: 5 tip cards, a TOP 3 teaser (the products stay hidden for the next video), follow and share cards.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Audio, Img, OffthreadVideo, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

type Shot = {src: string; ss: number; t: number; d: number; tag?: string};
type Cap = {s: number; e: number; text: string};
type Sec = {kind: string; n: number; s: number; e: number; title: string; sub: string};
export type ExpoPlan = {fps: number; day: number; media: string; duration: number; frames: number; intro: number; shots: Shot[]; captions: Cap[]; sections: Sec[]; voEstimated?: boolean; vo?: string};

const C = {navy: '#1E2D4D', cream: '#F5F0E6', yellow: '#F6E27A', honey: '#FFC93C', pink: '#F7B2B7', red: '#E4572E', sky: '#AECCE6'};
const PRE = "'Pretendard', 'Noto Color Emoji', sans-serif";
const KO = "'Gaegu', 'Pretendard', 'Noto Color Emoji', cursive";
const SH = '0 3px 10px rgba(10,16,30,.85), 0 0 24px rgba(10,16,30,.55)';
const STROKE = '-3px -3px 0 #1E2D4D, 3px -3px 0 #1E2D4D, -3px 3px 0 #1E2D4D, 3px 3px 0 #1E2D4D, 0 6px 16px rgba(0,0,0,.6)';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const FONTS: [string, string, string, string][] = [
  ['Pretendard', 'normal', '800', 'Pretendard-ExtraBold.woff2'], ['Pretendard', 'normal', '900', 'Pretendard-Black.woff2'],
  ['Noto Color Emoji', 'normal', '400', 'Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf'], ['Gaegu', 'normal', '700', 'Gaegu-Bold.ttf'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([f, st, w, file]) => new FontFace(f, `url(${staticFile('fonts/' + file)})`, {style: st, weight: w}).load().then((x) => document.fonts.add(x))))
      .then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
  }, [h]);
};
const sp = (t: number, s: number, fps: number, damping = 11) => spring({frame: Math.round((t - s) * fps), fps, config: {damping, stiffness: 200, mass: .55}});

const Lines: React.FC<{text: string; style: React.CSSProperties}> = ({text, style}) => <div style={{whiteSpace: 'pre-line', ...style}}>{text}</div>;

// Joy's clip as a sticker: white outline + soft shadow, bottom-left
const JoySticker: React.FC<{t: number; fps: number; media: string; until: number}> = ({t, fps, media, until}) => {
  const k = sp(t, 0, fps, 12);
  const out = interpolate(t, [until - .3, until], [0, 1], clamp);
  const o = 'drop-shadow(5px 0 0 #fff) drop-shadow(-5px 0 0 #fff) drop-shadow(0 5px 0 #fff) drop-shadow(0 -5px 0 #fff) drop-shadow(0 24px 30px rgba(0,0,0,.55))';
  return (
    <div style={{position: 'absolute', left: -70, bottom: -20, width: 1080 * .68, height: 1920 * .68, transform: `translateX(${(1 - k) * -300 - out * 400}px) rotate(${-2 + out * -6}deg)`, filter: o}}>
      <OffthreadVideo src={staticFile(`${media}/joy.webm`)} transparent muted style={{width: '100%', height: '100%'}} />
    </div>
  );
};

const Badge: React.FC<{day: number}> = ({day}) => (
  <div style={{position: 'absolute', top: 70, left: 40, fontFamily: PRE, fontWeight: 800, fontSize: 30, color: C.navy, background: C.yellow, borderRadius: 999, padding: '8px 22px', boxShadow: '0 6px 14px rgba(0,0,0,.3)'}}>
    DAY {day} · 출간까지 매일 업로드</div>
);

const Live: React.FC<{t: number}> = ({t}) => (
  <div style={{position: 'absolute', top: 70, right: 40, display: 'flex', alignItems: 'center', gap: 12, fontFamily: PRE, fontWeight: 900, fontSize: 34, color: '#fff',
    background: C.red, borderRadius: 14, padding: '8px 20px', boxShadow: '0 6px 14px rgba(0,0,0,.35)'}}>
    <div style={{width: 18, height: 18, borderRadius: 9, background: '#fff', opacity: .4 + .6 * Math.abs(Math.sin(t * 4))}} />지금 코엑스</div>
);

const Intro: React.FC<{t: number; fps: number; sec: Sec; shots: Shot[]}> = ({t, fps, sec, shots}) => {
  const k = sp(t, 0, fps, 9);
  const shot = [...shots].reverse().find((x) => x.tag && t >= x.t);
  const q = shot ? sp(t, shot.t, fps, 9) : 0;
  const [l1, l2] = sec.title.split('\n');
  return (
    <>
      <div style={{position: 'absolute', top: 175, left: 0, right: 0, textAlign: 'center', transform: `scale(${.6 + .4 * k}) rotate(-2deg)`, opacity: Math.min(1, k * 2)}}>
        <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 118, lineHeight: 1.08, color: '#fff', textShadow: STROKE}}>{l1}</div>
        <div style={{display: 'inline-block', marginTop: 10, fontFamily: PRE, fontWeight: 900, fontSize: 126, lineHeight: 1.1, color: C.navy, background: C.yellow, borderRadius: 22, padding: '0 28px',
          boxShadow: '0 12px 26px rgba(0,0,0,.45)', transform: `rotate(${Math.sin(t * 6) * 1.2}deg)`}}>{l2}</div>
      </div>
      <div style={{position: 'absolute', top: 505, left: 0, right: 0, textAlign: 'center', opacity: sp(t, .35, fps)}}>
        <span style={{fontFamily: PRE, fontWeight: 800, fontSize: 40, color: '#fff', background: 'rgba(30,45,77,.85)', borderRadius: 999, padding: '10px 28px'}}>{sec.sub}</span>
      </div>
      {shot && <div style={{position: 'absolute', right: 36, top: 1150, transform: `scale(${.5 + .5 * q}) rotate(${4 - 2 * (shots.indexOf(shot) % 3)}deg)`, transformOrigin: '100% 50%',
        fontFamily: KO, fontWeight: 700, fontSize: 62, color: C.navy, background: '#fff', borderRadius: 18, padding: '6px 24px', boxShadow: '0 10px 22px rgba(0,0,0,.4)', border: `5px solid ${C.yellow}`}}>
        {shot.tag}</div>}
    </>
  );
};

const Progress: React.FC<{n: number}> = ({n}) => (
  <div style={{position: 'absolute', top: 160, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 12}}>
    {[1, 2, 3, 4, 5].map((i) => <div key={i} style={{width: i === n ? 130 : 60, height: 60, borderRadius: 30, display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: PRE, fontWeight: 900, fontSize: 30, background: i <= n ? C.honey : 'rgba(255,255,255,.35)', color: C.navy, boxShadow: '0 6px 14px rgba(0,0,0,.3)'}}>
      {i === n ? `꿀팁 ${i}` : i}</div>)}
  </div>
);

const Tip: React.FC<{t: number; fps: number; sec: Sec}> = ({t, fps, sec}) => {
  const k = sp(t, sec.s, fps, 10); const q = sp(t, sec.s + .45, fps, 10);
  return (
    <>
      <Progress n={sec.n} />
      <div style={{position: 'absolute', top: 270, left: 50, right: 50, transform: `translateX(${(1 - k) * -700}px) rotate(-1.5deg)`}}>
        <div style={{background: 'rgba(30,45,77,.9)', borderRadius: 30, padding: '40px 36px 34px', boxShadow: '0 20px 44px rgba(0,0,0,.5)', border: `5px solid ${C.honey}`}}>
          <div style={{position: 'absolute', top: -34, left: 34, fontFamily: PRE, fontWeight: 900, fontSize: 40, color: C.navy, background: C.honey, borderRadius: 999, padding: '6px 26px'}}>🍯 꿀팁 {sec.n}</div>
          <div style={{fontFamily: KO, fontWeight: 700, fontSize: 96, lineHeight: 1.1, color: '#fff', textAlign: 'center'}}>{sec.title}</div>
          {sec.sub && <div style={{marginTop: 14, opacity: q, transform: `scale(${.8 + .2 * q})`, fontFamily: KO, fontWeight: 700, fontSize: 60, color: C.yellow, textAlign: 'center'}}>{sec.sub}</div>}
        </div>
      </div>
    </>
  );
};

const Kkul: React.FC<{t: number; fps: number; sec: Sec}> = ({t, fps, sec}) => {
  const k = sp(t, sec.s, fps, 8);
  return <div style={{position: 'absolute', top: 380, left: 0, right: 0, textAlign: 'center', transform: `scale(${.4 + .6 * k}) rotate(-3deg)`}}>
    <Lines text={sec.title} style={{display: 'inline-block', fontFamily: KO, fontWeight: 700, fontSize: 130, lineHeight: 1.05, color: C.navy, background: C.honey, borderRadius: 36, padding: '24px 44px', boxShadow: '0 18px 40px rgba(0,0,0,.5)'}} />
  </div>;
};

const Top3: React.FC<{t: number; fps: number; sec: Sec}> = ({t, fps, sec}) => {
  const k = sp(t, sec.s, fps, 9); const q = sp(t, sec.s + .6, fps, 8);
  const [l1, l2] = sec.title.split('\n');
  return (
    <>
      <div style={{position: 'absolute', top: 250, left: 0, right: 0, textAlign: 'center', opacity: k}}>
        <div style={{fontFamily: KO, fontWeight: 700, fontSize: 70, color: '#fff', textShadow: SH}}>{l1}</div>
        <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 300, lineHeight: 1, color: C.yellow, textShadow: '0 14px 40px rgba(0,0,0,.6)', transform: `scale(${.5 + .5 * k})`}}>{l2}</div>
        <div style={{display: 'inline-block', marginTop: 20, transform: `scale(${q}) rotate(-4deg)`, fontFamily: PRE, fontWeight: 900, fontSize: 54, color: '#fff', background: C.red, borderRadius: 16, padding: '8px 30px'}}>{sec.sub}</div>
      </div>
      {['❓', '🎁', '❓'].map((e, i) => <div key={i} style={{position: 'absolute', fontSize: 120, left: [90, 470, 850][i], top: 860 + 30 * Math.sin(t * 3 + i * 2), transform: `scale(${sp(t, sec.s + .3 + .2 * i, fps, 8)})`}}>{e}</div>)}
    </>
  );
};

const Follow: React.FC<{t: number; fps: number; sec: Sec}> = ({t, fps, sec}) => {
  const k = sp(t, sec.s, fps, 10);
  const tap = (t - sec.s - 1.6) % 2.2; const press = tap > 0 && tap < .25;
  return (
    <div style={{position: 'absolute', top: 300, left: 70, right: 70, transform: `translateY(${(1 - k) * 300}px)`, opacity: k}}>
      <div style={{background: C.cream, borderRadius: 36, padding: '50px 40px', textAlign: 'center', boxShadow: '0 24px 50px rgba(0,0,0,.5)'}}>
        <Img src={staticFile('brand/logo-full.png')} style={{height: 170, objectFit: 'contain'}} />
        <Lines text={sec.title} style={{marginTop: 16, fontFamily: KO, fontWeight: 700, fontSize: 92, lineHeight: 1.05, color: C.navy}} />
        <div style={{marginTop: 8, fontFamily: KO, fontWeight: 700, fontSize: 52, color: '#8A6D3B'}}>{sec.sub}</div>
        <div style={{display: 'inline-block', marginTop: 26, fontFamily: PRE, fontWeight: 900, fontSize: 52, color: '#fff', background: press ? '#2b3f6a' : '#4C6EF5', borderRadius: 18, padding: '14px 70px',
          transform: `scale(${press ? .93 : 1})`}}>{press || tap > .25 && tap < 1.2 ? '✓ 팔로잉' : '+ 팔로우'}</div>
      </div>
    </div>
  );
};

const Share: React.FC<{t: number; fps: number; sec: Sec}> = ({t, fps, sec}) => {
  const k = sp(t, sec.s, fps, 8);
  const fly = ((t - sec.s) % 1.6) / 1.6;
  return (
    <div style={{position: 'absolute', top: 330, left: 0, right: 0, textAlign: 'center'}}>
      <div style={{fontSize: 190, transform: `translate(${fly * 120 - 60}px, ${-fly * 60}px) rotate(${-10 + fly * 20}deg) scale(${k})`}}>📤</div>
      <Lines text={sec.title} style={{display: 'inline-block', marginTop: 10, transform: `scale(${.5 + .5 * k}) rotate(-2deg)`, fontFamily: PRE, fontWeight: 900, fontSize: 96, lineHeight: 1.12, color: C.navy,
        background: C.yellow, borderRadius: 30, padding: '20px 40px', boxShadow: '0 18px 40px rgba(0,0,0,.5)'}} />
      <div style={{marginTop: 30, opacity: sp(t, sec.s + .5, fps), fontFamily: KO, fontWeight: 700, fontSize: 60, color: '#fff', textShadow: SH}}>👉 같이 갈 친구를 @태그해 주세요!</div>
    </div>
  );
};

export const ExpoPromo: React.FC<{plan: ExpoPlan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const t = frame / fps;
  const sec = plan.sections.find((x) => t >= x.s && t < x.e) ?? plan.sections[plan.sections.length - 1];
  const shot = [...plan.shots].reverse().find((x) => t >= x.t) ?? plan.shots[0];
  const dt = t - shot.t;
  const punch = interpolate(dt, [0, .22], [1.14, 1.02], clamp) + dt * .02;
  const flash = interpolate(dt, [0, .1], [t < plan.intro ? .4 : .22, 0], clamp);
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const intro = sec.kind === 'intro';
  const blur = sec.kind === 'top3' ? 16 : sec.kind === 'follow' || sec.kind === 'share' ? 6 : 0;
  const cq = cap ? sp(t, cap.s, fps, 12) : 0;
  return (
    <AbsoluteFill style={{background: '#000', overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `scale(${punch})`, filter: blur ? `blur(${blur}px) brightness(.8)` : undefined}}>
        <OffthreadVideo src={staticFile(`${plan.media}/bg.mp4`)} muted style={{width: '100%', height: '100%'}} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,16,30,.6) 0%, rgba(10,16,30,0) 34%, rgba(10,16,30,0) 58%, rgba(10,16,30,.55) 100%)'}} />
      <AbsoluteFill style={{background: '#fff', opacity: flash}} />
      {intro && <JoySticker t={t} fps={fps} media={plan.media} until={15.2} />}
      {intro && <Intro t={t} fps={fps} sec={sec} shots={plan.shots} />}
      {intro && <Live t={t} />}
      {!intro && <Badge day={plan.day} />}
      {sec.kind === 'kkul' && <Kkul t={t} fps={fps} sec={sec} />}
      {sec.kind === 'tip' && <Tip t={t} fps={fps} sec={sec} />}
      {sec.kind === 'top3' && <Top3 t={t} fps={fps} sec={sec} />}
      {sec.kind === 'follow' && <Follow t={t} fps={fps} sec={sec} />}
      {sec.kind === 'share' && <Share t={t} fps={fps} sec={sec} />}
      {cap && <div style={{position: 'absolute', left: 50, right: 50, top: intro ? 610 : 1290, textAlign: 'center', transform: `translateY(${(1 - cq) * 16}px)`, opacity: Math.min(1, cq * 2)}}>
        <Lines text={cap.text} style={{display: 'inline-block', fontFamily: PRE, fontWeight: 800, fontSize: 54, lineHeight: 1.3, color: '#fff', textShadow: STROKE}} />
      </div>}
      <Audio src={staticFile(`${plan.media}/intro.wav`)} endAt={Math.round(plan.intro * fps)} />
      {plan.vo && <Audio src={staticFile(`${plan.media}/${plan.vo}`)} />}
    </AbsoluteFill>
  );
};
