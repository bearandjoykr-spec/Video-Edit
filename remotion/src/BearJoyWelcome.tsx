// Day 0 "Welcome to Little Steps": landscape, high-energy. Mark and Joy are cut out of the white wall and
// stand in an animated sky, with words behind their heads, cards in front and a big offer ending.
// Rules: brand/BRAND.md, docs/class-video-style.md. All timing comes from projects/2026-11-day0-welcome/.
import React from 'react';
import {AbsoluteFill, Easing, Img, OffthreadVideo, Sequence, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {evolvePath, getPointAtLength, getLength} from '@remotion/paths';
import {noise2D} from '@remotion/noise';
import {Caption, LogoCard, Progress, Reviews, Sparkles, useFonts} from './BearJoyClass';

type Ev = {type: string; s: number; e: number; [k: string]: any};
export type WelcomePlan = {
  name: string; fps: number; duration: number; frames: number; mainStart: number; mainEnd: number;
  segments: {src_s: number; src_e: number; out_s: number}[];
  captions: {s: number; e: number; ko: string; hi: string}[];
  scenes: {t: number; bg: string}[];
  events: Ev[]; zooms: {t: number; z: number; ox: number; oy: number}[]; shakes: number[];
};

const C = {navy: '#1E2D4D', deep: '#173B5C', ink: '#14203A', butter: '#F6F0BA', sky: '#AECCE6', white: '#FFFFFF', cream: '#F8EEDF', paper: '#FFF8EE', gold: '#E9C766'};
const FF = "'Pretendard', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif";
const SHADOW = '0 2px 6px rgba(10,16,30,.7), 0 0 26px rgba(10,16,30,.42), 0 10px 40px rgba(10,16,30,.35)';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const tone = (k?: string) => (k === 'sky' ? C.sky : k === 'white' ? C.white : C.butter);
const pop = (t: number, at: number, soft = false) => spring({frame: Math.round((t - at) * 30), fps: 30, config: soft ? {damping: 14, stiffness: 130, mass: .8} : {damping: 8, stiffness: 210, mass: .55}});
const fadeOut = (t: number, e: number, d = .22) => interpolate(t, [e - d, e], [1, 0], clamp);
const img = (f: string) => staticFile(`day0/${f}`);
const BEAR = 'brand/bear-butterfly.png';

// ------------------------------------------------------------ the world behind them
const Backdrop: React.FC<{scenes: WelcomePlan['scenes']; t: number}> = ({scenes, t}) => {
  const dx = noise2D('bgx', t * .05, 0) * 40, dy = noise2D('bgy', t * .05, 1) * 20;
  let cur = 0;
  scenes.forEach((s, i) => { if (s.t <= t) cur = i; });
  return (
    <AbsoluteFill>
      {scenes.map((s, i) => {
        if (i !== cur && i !== cur - 1) return null;
        const o = i === cur ? interpolate(t, [s.t, s.t + .7], [0, 1], clamp) : 1;
        return <Img key={i} src={img(`${s.bg}.jpg`)} style={{position: 'absolute', left: -160, top: -90, width: 2240, height: 1260, opacity: o, transform: `translate(${dx}px,${dy}px)`}} />;
      })}
      {[0, 1, 2, 0, 1].map((c, i) => {
        const w = 2500, speed = 14 + i * 6, x = ((i * 530 + t * speed) % w) - 500;
        return <Img key={i} src={img(`cloud${c}.png`)} style={{position: 'absolute', left: x, top: 20 + (i * 170) % 620, width: 520 + i * 90, opacity: .8}} />;
      })}
    </AbsoluteFill>
  );
};

const Drift: React.FC<{t: number}> = ({t}) => (
  <>
    {Array.from({length: 16}).map((_, i) => {
      const x = random(`dx${i}`) * 1920 + Math.sin(t * .4 + i) * 40;
      const y = 1080 - (((t * (14 + random(`dy${i}`) * 26) + random(`d0${i}`) * 1080)) % 1160);
      return <div key={i} style={{position: 'absolute', left: x, top: y, fontSize: 18 + random(`ds${i}`) * 26, color: i % 2 ? C.gold : C.white, opacity: .75 * Math.abs(Math.sin(t * 1.3 + i)), textShadow: '0 1px 6px rgba(20,32,58,.25)'}}>✦</div>;
    })}
  </>
);

// ------------------------------------------------------------ words
const INK_GLOW = '0 0 2px rgba(255,255,255,.9), 0 2px 18px rgba(255,255,255,.75), 0 10px 30px rgba(23,59,92,.25)';
const Behind: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const k = pop(t, ev.s), o = Math.min(1, k * 2.5) * fadeOut(t, ev.e, .3);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: ev.y ?? 20, textAlign: 'center', opacity: o, transform: `scale(${.55 + .45 * k})`, fontFamily: FF, textShadow: INK_GLOW}}>
      {ev.small ? <div style={{color: C.deep, fontWeight: 800, fontSize: 52}}>{ev.small}</div> : null}
      <div style={{color: ev.tone === 'sky' ? '#2C6AA6' : C.deep, fontWeight: 900, fontSize: ev.size ?? 300, lineHeight: 1, letterSpacing: '-.03em', whiteSpace: 'nowrap'}}>{ev.big}</div>
    </div>
  );
};

const Phrase: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const words: string[] = ev.text.split(' ');
  const step = Math.min(.28, (ev.e - ev.s - .3) / words.length);
  return (
    <div style={{position: 'absolute', left: 40, right: 40, top: ev.y ?? 24, display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '0 22px', opacity: fadeOut(t, ev.e), fontFamily: FF, fontWeight: 900, fontSize: ev.size ?? 92, letterSpacing: '-.02em', textShadow: INK_GLOW}}>
      {words.map((w, i) => {
        const k = pop(t, ev.s + i * step);
        const hot = (ev.hot ?? []).includes(i);
        return <span key={i} style={{display: 'inline-block', opacity: Math.min(1, k * 3), transform: `translateY(${(1 - k) * 46}px) scale(${.6 + .4 * k})`, color: hot ? C.white : C.deep, background: hot ? C.deep : 'transparent', borderRadius: 16, padding: hot ? '0 14px' : 0, textShadow: hot ? 'none' : undefined}}>{w}</span>;
      })}
    </div>
  );
};

const ChipEl: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const k = pop(t, ev.s), bob = Math.sin((t - ev.s) * 2.4 + (ev.x ?? 0)) * 5;
  const o = Math.min(1, k * 3) * fadeOut(t, ev.e);
  return (
    <div style={{position: 'absolute', left: ev.x, right: ev.right, top: ev.y, opacity: o, transform: `translateY(${bob}px) scale(${.5 + .5 * k}) rotate(${(1 - k) * (ev.right != null ? 8 : -8) + (ev.tilt ?? 0)}deg)`, transformOrigin: ev.right != null ? 'right center' : 'left center',
      background: ev.tone === 'navy' ? C.navy : tone(ev.tone), color: ev.tone === 'navy' ? C.white : C.ink, borderRadius: 26, padding: '16px 30px', fontFamily: FF, fontWeight: 900, fontSize: ev.size ?? 44, display: 'flex', gap: 14, alignItems: 'center', boxShadow: '0 12px 34px rgba(10,16,30,.28)', border: '3px solid rgba(255,255,255,.75)', maxWidth: 450, wordBreak: 'keep-all', lineHeight: 1.15}}>
      {ev.emoji ? <span style={{fontSize: (ev.size ?? 44) * 1.25}}>{ev.emoji}</span> : null}{ev.text}
    </div>
  );
};

const Bubble: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const k = pop(t, ev.s), o = Math.min(1, k * 3) * fadeOut(t, ev.e);
  const left = ev.x != null;
  return (
    <div style={{position: 'absolute', left: ev.x, right: ev.right, top: ev.y, maxWidth: ev.w ?? 560, opacity: o, transform: `scale(${.4 + .6 * k})`, transformOrigin: left ? 'right bottom' : 'left bottom', background: C.paper, color: C.deep, borderRadius: 40, padding: '26px 36px', fontFamily: FF, fontWeight: 900, fontSize: ev.size ?? 50, lineHeight: 1.2, boxShadow: '0 14px 40px rgba(10,16,30,.28)', textAlign: 'center', textWrap: 'balance' as any, wordBreak: 'keep-all'}}>
      {ev.text}
      <div style={{position: 'absolute', bottom: -24, [left ? 'right' : 'left']: 56, width: 0, height: 0, borderLeft: '22px solid transparent', borderRight: '22px solid transparent', borderTop: `30px solid ${C.paper}`}} />
    </div>
  );
};

const Strike: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const k = pop(t, ev.s), o = Math.min(1, k * 3) * fadeOut(t, ev.e);
  const line = interpolate(t, [ev.s + ev.at, ev.s + ev.at + .25], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: ev.y ?? 60, display: 'grid', justifyItems: 'center', opacity: o, transform: `scale(${.6 + .4 * k})`, fontFamily: FF}}>
      <div style={{position: 'relative', background: C.navy, color: C.white, borderRadius: 26, padding: '16px 40px', fontWeight: 900, fontSize: ev.size ?? 72, boxShadow: '0 12px 34px rgba(10,16,30,.28)'}}>
        {ev.text}
        <svg viewBox="0 0 100 20" preserveAspectRatio="none" style={{position: 'absolute', left: 14, right: 14, top: '38%', width: 'calc(100% - 28px)', height: 26}}><path d="M2 14 Q50 2 98 8" {...evolvePath(line, 'M2 14 Q50 2 98 8')} fill="none" stroke="#F2877B" strokeWidth="5" strokeLinecap="round" vectorEffect="non-scaling-stroke" /></svg>
      </div>
    </div>
  );
};

const EmojiBurst: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const p = (t - ev.s) / (ev.e - ev.s);
  if (p < 0 || p > 1) return null;
  const list: string[] = ev.emoji;
  return (
    <>
      {Array.from({length: ev.n ?? 18}).map((_, i) => {
        const a = random(`ea${ev.s}${i}`) * Math.PI * 2, d = (ev.x > 1400 ? 50 : 160) + random(`ed${ev.s}${i}`) * (ev.x > 1400 ? 250 : 620), q = Easing.out(Easing.cubic)(p);
        return <div key={i} style={{position: 'absolute', left: ev.x + Math.cos(a) * d * q, top: ev.y + Math.sin(a) * d * q * .7 + p * p * 240, fontSize: 44 + random(`ez${ev.s}${i}`) * 50, opacity: interpolate(p, [0, .1, .7, 1], [0, 1, 1, 0]), transform: `rotate(${p * 200 * (i % 2 ? 1 : -1)}deg) scale(${interpolate(p, [0, .2], [.3, 1], clamp)})`}}>{list[i % list.length]}</div>;
      })}
    </>
  );
};

const FlyBear: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const k = pop(t, ev.s), out = fadeOut(t, ev.e), wob = Math.sin((t - ev.s) * 7) * 4;
  return <Img src={staticFile(BEAR)} style={{position: 'absolute', left: ev.x, top: ev.y + (1 - k) * 500, height: ev.h ?? 420, opacity: out, transform: `rotate(${wob}deg)`, filter: 'drop-shadow(0 16px 26px rgba(10,16,30,.3))'}} />;
};

// The resident bear: sits on a cloud in the free space on the right, so that side is never empty
const Resident: React.FC<{t: number; hide: boolean}> = ({t, hide}) => {
  const y = Math.sin(t * 1.1) * 12, o = hide ? 0 : 1;
  return (
    <div style={{position: 'absolute', left: 1500, top: 600, width: 400, height: 330, opacity: o, transform: `translateY(${y}px)`}}>
      <Img src={staticFile(BEAR)} style={{position: 'absolute', left: 60, top: 0, height: 270, transform: `rotate(${Math.sin(t * 1.7) * 3}deg)`, transformOrigin: '50% 100%'}} />
      <Img src={img('cloud1.png')} style={{position: 'absolute', left: 30, top: 165, width: 380}} />
    </div>
  );
};

const Sheets: React.FC<{ev: Ev; t: number}> = ({ev, t}) => (
  <div style={{position: 'absolute', left: 1290, top: 130, width: 620, height: 680, opacity: fadeOut(t, ev.e, .3)}}>
    {(ev.days as number[]).map((d, i) => {
      const k = pop(t, ev.s + i * .28, true), rot = (i - 1) * 9 + Math.sin(t * 1.2 + i) * 1.2;
      return <Img key={d} src={img(`sheets/day${d}.jpg`)} style={{position: 'absolute', left: 70 + i * 46, top: 30 + Math.abs(i - 1) * 22 + (1 - k) * 900, height: 560, borderRadius: 10, transform: `rotate(${rot}deg)`, boxShadow: '0 18px 44px rgba(10,16,30,.35)'}} />;
    })}
  </div>
);

const STOPS: [number, number][] = [[150, 800], [400, 560], [680, 760], [960, 520], [1240, 740], [1510, 500], [1770, 690]];
const PATH = 'M 150 800 C 240 640 300 560 400 560 S 560 800 680 760 S 840 520 960 520 S 1120 760 1240 740 S 1400 500 1510 500 S 1660 700 1770 690';
const DAYS = ['안녕, 곰아!', '같이 찾아봐요', '조이와 움직여요', '무엇을 좋아하나요?', '이야기 탐정', '깔깔 영어놀이', '우리의 모험'];

// ------------------------------------------------------------ full-screen moments
const Scene: React.FC<{bg: string; children: React.ReactNode; t: number}> = ({bg, children, t}) => (
  <AbsoluteFill style={{fontFamily: FF, color: C.deep}}>
    <Backdrop scenes={[{t: -1, bg}]} t={t} />
    <Drift t={t} />
    {children}
  </AbsoluteFill>
);

const Title: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const walk = interpolate(t, [ev.s, ev.s + 1.4], [-900, 0], {...clamp, easing: Easing.out(Easing.cubic)});
  const bob = t < ev.s + 1.4 ? Math.abs(Math.sin(t * 9)) * 22 : Math.sin(t * 2) * 5;
  const a = pop(t, ev.s + .7), b = pop(t, ev.s + 1.05), c = pop(t, ev.s + 1.4);
  return (
    <Scene bg="bg-sky" t={t}>
      <Img src={staticFile(BEAR)} style={{position: 'absolute', left: 90, top: 230, height: 620, transform: `translateX(${walk}px) translateY(${-bob}px)`, filter: 'drop-shadow(0 20px 30px rgba(10,16,30,.22))'}} />
      <div style={{position: 'absolute', left: 800, right: 40, top: 210}}>
        <div style={{transform: `scale(${a})`, transformOrigin: 'left center', display: 'inline-block', background: C.navy, color: C.butter, fontWeight: 900, fontSize: 60, padding: '12px 44px', borderRadius: 99}}>DAY 0</div>
        <div style={{transform: `translateY(${(1 - b) * 60}px)`, opacity: Math.min(1, b * 2), fontWeight: 900, fontSize: 136, lineHeight: 1.04, letterSpacing: '-.03em', marginTop: 34, color: C.deep}}>Welcome to<br />Little Steps</div>
        <div style={{transform: `translateY(${(1 - c) * 60}px)`, opacity: Math.min(1, c * 2), fontWeight: 800, fontSize: 62, marginTop: 26}}>Mark와 Joy가 전하는 첫 인사</div>
      </div>
    </Scene>
  );
};

const Promise_: React.FC<{ev: Ev; t: number}> = ({ev, t}) => (
  <Scene bg="bg-butter" t={t}>
    <div style={{position: 'absolute', left: 130, top: 120, fontWeight: 900, fontSize: 92, letterSpacing: '-.02em', transform: `scale(${pop(t, ev.s)})`, transformOrigin: 'left center'}}>이 영상에서 알려드려요</div>
    <div style={{position: 'absolute', left: 130, right: 130, top: 300, display: 'grid', gap: 30}}>
      {(ev.rows as any[]).map((r, i) => {
        const k = pop(t, r.at);
        return (
          <div key={i} style={{display: 'flex', gap: 34, alignItems: 'center', background: C.paper, borderRadius: 34, padding: '30px 44px', fontWeight: 900, fontSize: 66, boxShadow: '0 14px 34px rgba(23,59,92,.14)', opacity: Math.min(1, k * 3), transform: `translateX(${(1 - k) * -400}px)`}}>
            <span style={{fontSize: 86}}>{r.emoji}</span>{r.text}
          </div>
        );
      })}
    </div>
  </Scene>
);

const Wipe: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const mid = (ev.s + ev.e) / 2;
  const x = interpolate(t, [ev.s, mid, ev.e], [-110, 0, 110], {...clamp, easing: Easing.inOut(Easing.cubic)});
  return (
    <AbsoluteFill style={{transform: `translateX(${x}%)`, background: ev.color ?? C.butter, justifyContent: 'center', alignItems: 'center', fontFamily: FF}}>
      <Img src={staticFile(BEAR)} style={{height: 400, transform: `translateY(${-Math.abs(Math.sin(t * 10)) * 26}px)`}} />
      {ev.text ? <div style={{color: C.deep, fontWeight: 900, fontSize: 90, letterSpacing: '-.02em', marginTop: 10}}>{ev.text}</div> : null}
    </AbsoluteFill>
  );
};

const Stamp: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const k = spring({frame: Math.round((t - ev.s) * 30), fps: 30, config: {damping: 9, stiffness: 240, mass: .7}});
  const o = Math.min(1, k * 4) * fadeOut(t, ev.e);
  return (
    <div style={{position: 'absolute', left: ev.x, right: ev.right, top: ev.y, opacity: o, transform: `scale(${2.4 - 1.4 * k}) rotate(${ev.rot ?? -7}deg)`, fontFamily: FF, background: C.butter, color: C.ink, border: `8px solid ${C.navy}`, borderRadius: 36, padding: '18px 44px', textAlign: 'center', boxShadow: '0 18px 50px rgba(10,16,30,.35)'}}>
      <div style={{fontWeight: 900, fontSize: ev.size ?? 92, lineHeight: 1.05, letterSpacing: '-.02em', whiteSpace: 'nowrap'}}>{ev.big}</div>
      {ev.small ? <div style={{fontWeight: 800, fontSize: 36, marginTop: 6, whiteSpace: 'nowrap'}}>{ev.small}</div> : null}
    </div>
  );
};

// Offer 1: Day 1 is free, and what's in it
const FreeDay: React.FC<{ev: Ev; t: number}> = ({ev, t}) => (
  <Scene bg="bg-butter" t={t}>
    <EmojiBurst ev={{...ev, e: ev.s + 2, x: 960, y: 300, n: 26, emoji: ['✨', '🎉', '⭐', '🦋']}} t={t} />
    <div style={{position: 'absolute', left: 0, right: 0, top: 60, textAlign: 'center', transform: `scale(${pop(t, ev.s)})`}}>
      <div style={{fontWeight: 900, fontSize: 210, letterSpacing: '-.04em', lineHeight: 1}}>1일차는 무료!</div>
      <div style={{fontWeight: 800, fontSize: 56, marginTop: 14}}>무료 계정으로 시작해요</div>
    </div>
    <div style={{position: 'absolute', left: 90, right: 90, top: 440, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 36}}>
      {(ev.items as any[]).map((it, i) => {
        const k = pop(t, ev.s + 1.1 + i * .55);
        return (
          <div key={i} style={{background: C.paper, borderRadius: 40, padding: '44px 26px', textAlign: 'center', boxShadow: '0 18px 44px rgba(23,59,92,.16)', transform: `translateY(${(1 - k) * 500}px) rotate(${(1 - k) * 12}deg)`, opacity: Math.min(1, k * 3), minHeight: 420}}>
            {it.sheet ? <Img src={img(it.sheet)} style={{height: 210, borderRadius: 8, boxShadow: '0 8px 20px rgba(10,16,30,.25)', transform: 'rotate(-4deg)'}} /> : it.avatar ? <Img src={staticFile(it.avatar)} style={{height: 210}} /> : <div style={{fontSize: 170, lineHeight: '210px'}}>{it.emoji}</div>}
            <div style={{fontWeight: 900, fontSize: 56, marginTop: 28}}>{it.title}</div>
          </div>
        );
      })}
    </div>
  </Scene>
);

// Offer 2: seven days on a path, the bear walks it
const Journey: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const p = interpolate(t, [ev.s + .5, ev.s + ev.walk], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
  const len = getLength(PATH), at = getPointAtLength(PATH, p * len);
  return (
    <Scene bg="bg-sky" t={t}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 60, textAlign: 'center', fontWeight: 900, fontSize: 104, letterSpacing: '-.03em', transform: `scale(${pop(t, ev.s)})`}}>7번의 작은 걸음. 하나의 큰 모험.</div>
      <svg width="1920" height="1080" style={{position: 'absolute', inset: 0}}>
        <path d={PATH} fill="none" stroke={C.white} strokeWidth="18" strokeLinecap="round" strokeDasharray="4 34" />
        <path d={PATH} {...evolvePath(p, PATH)} fill="none" stroke={C.gold} strokeWidth="18" strokeLinecap="round" />
      </svg>
      {STOPS.map(([x, y], i) => {
        const when = ev.s + .5 + (i / 6) * (ev.walk - .5);
        const k = pop(t, when), lit = t >= when, up = i % 2 === 1;
        return (
          <React.Fragment key={i}>
            <div style={{position: 'absolute', left: x - 62, top: y - 62, width: 124, height: 124, borderRadius: 99, background: lit ? (i === 0 ? C.butter : C.navy) : C.white, color: lit ? (i === 0 ? C.ink : C.white) : C.deep, display: 'grid', placeItems: 'center', fontWeight: 900, fontSize: 62, boxShadow: '0 10px 26px rgba(10,16,30,.25)', transform: `scale(${lit ? .85 + .15 * k + (1 - k) * .4 : .85})`}}>{i + 1}</div>
            <div style={{position: 'absolute', left: x - 170, width: 340, top: up ? y - 150 : y + 76, textAlign: 'center', fontWeight: 900, fontSize: 38, whiteSpace: 'nowrap', opacity: Math.min(1, k * 3), color: C.deep, textShadow: '0 0 14px rgba(255,255,255,.9)'}}>{DAYS[i]}{i === 0 ? <div style={{display: 'inline-block', marginLeft: 10, background: C.navy, color: C.butter, fontSize: 28, padding: '3px 14px', borderRadius: 99}}>무료</div> : null}</div>
          </React.Fragment>
        );
      })}
      <Img src={staticFile(BEAR)} style={{position: 'absolute', left: at.x - 80, top: at.y - 210 - Math.abs(Math.sin(t * 8)) * 16, height: 170}} />
    </Scene>
  );
};

// Offer 3: what's inside (the page's own list)
const Inside: React.FC<{ev: Ev; t: number}> = ({ev, t}) => (
  <Scene bg="bg-lilac" t={t}>
    <div style={{position: 'absolute', left: 110, top: 60, fontWeight: 900, fontSize: 100, letterSpacing: '-.03em', transform: `scale(${pop(t, ev.s)})`, transformOrigin: 'left center'}}>Little Steps에 담긴 것들</div>
    <div style={{position: 'absolute', left: 110, right: 110, top: 220, display: 'grid', gap: 22}}>
      {(ev.rows as any[]).map((r, i) => {
        const k = pop(t, ev.s + .7 + i * .75);
        return (
          <div key={i} style={{display: 'flex', alignItems: 'center', gap: 30, background: C.paper, borderRadius: 30, padding: '20px 40px', fontWeight: 900, fontSize: 62, height: 128, boxShadow: '0 12px 30px rgba(23,59,92,.13)', opacity: Math.min(1, k * 3), transform: `translateX(${(1 - k) * (i % 2 ? 900 : -900)}px)`}}>
            {r.avatar ? <Img src={staticFile(r.avatar)} style={{height: 100}} /> : <span style={{fontSize: 80, width: 100, textAlign: 'center'}}>{r.emoji}</span>}
            <span style={{flex: 1}}>{r.text}</span>
            <span style={{color: '#fff', background: C.deep, width: 70, height: 70, borderRadius: 99, display: 'grid', placeItems: 'center', fontSize: 42, transform: `scale(${pop(t, ev.s + 1.1 + i * .75)})`}}>✓</span>
          </div>
        );
      })}
    </div>
  </Scene>
);

// Offer 4: the price and the page's two buttons
const Price: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const n = Math.round(interpolate(t, [ev.s + .2, ev.s + 1.5], [0, 47000], {...clamp, easing: Easing.out(Easing.cubic)}));
  const pulse = 1 + .03 * Math.max(0, Math.sin((t - ev.s) * 4.5));
  const tap = interpolate(t, [ev.s + 5.2, ev.s + 5.7], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  return (
    <Scene bg="bg-butter" t={t}>
      <div style={{position: 'absolute', left: 0, right: 0, top: 40, textAlign: 'center', transform: `scale(${pop(t, ev.s)})`}}>
        <div style={{fontWeight: 900, fontSize: 60}}>2–7일차, 전체 과정</div>
        <div style={{fontWeight: 900, fontSize: 250, letterSpacing: '-.04em', lineHeight: 1.02}}>₩{n.toLocaleString('en-US')}</div>
      </div>
      <div style={{position: 'absolute', left: 90, right: 90, top: 410, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 26}}>
        {(ev.facts as any[]).map((f, i) => {
          const k = pop(t, ev.s + 1.6 + i * .5);
          return <div key={i} style={{background: C.navy, color: C.white, borderRadius: 30, padding: '26px 16px', textAlign: 'center', transform: `scale(${k})`, opacity: Math.min(1, k * 3)}}><div style={{fontSize: 70}}>{f.emoji}</div><div style={{color: C.butter, fontWeight: 900, fontSize: 46, marginTop: 6}}>{f.big}</div><div style={{fontWeight: 700, fontSize: 30, marginTop: 6}}>{f.small}</div></div>;
        })}
      </div>
      <div style={{position: 'absolute', left: 90, right: 90, top: 730, display: 'grid', gridTemplateColumns: '1fr 1.15fr', gap: 30, transform: `translateY(${(1 - pop(t, ev.s + 3.6, true)) * 500}px)`}}>
        <div style={{position: 'relative', background: C.paper, border: `5px solid ${C.deep}`, borderRadius: 30, padding: '40px 10px', textAlign: 'center', fontWeight: 900, fontSize: 60, color: C.deep, transform: `scale(${pulse})`}}>
          1일차 무료로 시작하기
          <div style={{position: 'absolute', right: 40, bottom: -70 + (1 - tap) * 120, fontSize: 110, opacity: tap, transform: 'rotate(-12deg)'}}>👆</div>
        </div>
        <div style={{background: C.deep, borderRadius: 30, padding: '40px 10px', textAlign: 'center', fontWeight: 900, fontSize: 60, color: C.white}}>전체 과정 열기 · ₩47,000</div>
      </div>
    </Scene>
  );
};

// ------------------------------------------------------------ main
export const BearJoyWelcome: React.FC<{plan: WelcomePlan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const E = (type: string) => plan.events.filter((e) => e.type === type);
  const live = (e: Ev, pad = .05) => t >= e.s - .05 && t <= e.e + pad;
  const R = (type: string, C_: React.FC<{ev: Ev; t: number}>) => E(type).map((ev, k) => (live(ev) ? <C_ key={`${type}${k}`} ev={ev} t={t} /> : null));

  // camera: a quick punch on each cue, a slow breath in between, a shake on the big hits
  let z = 1, prev = 1, since = 99, ox = 960, oy = 420;
  for (const k of plan.zooms) if (k.t <= t) { prev = z; z = k.z; since = t - k.t; ox = k.ox; oy = k.oy; }
  z = prev + (z - prev) * interpolate(since, [0, .3], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  z *= 1 + .012 * Math.sin(t * .5);
  const hit = plan.shakes.find((s) => t >= s && t < s + .4);
  const sx = hit != null ? noise2D('sx', t * 30, 0) * 14 * (1 - (t - hit) / .4) : 0;
  const sy = hit != null ? noise2D('sy', t * 30, 1) * 14 * (1 - (t - hit) / .4) : 0;
  const cam: React.CSSProperties = {position: 'absolute', inset: 0, transform: `translate(${sx}px,${sy}px) scale(${z})`, transformOrigin: `${ox}px ${oy}px`};
  const vid: React.CSSProperties = {width: '100%', height: '100%', objectFit: 'cover', filter: 'contrast(1.05) saturate(1.1)'};
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const inMain = t >= plan.mainStart - .1 && t < plan.mainEnd + .1;

  return (
    <AbsoluteFill style={{background: C.cream}}>
      {inMain ? (
        <>
          <div style={{...cam, transform: `translate(${sx * .5}px,${sy * .5}px) scale(${1 + (z - 1) * .4})`}}><Backdrop scenes={plan.scenes} t={t} /><Drift t={t} /></div>
          <div style={cam}>
            {R('behind', Behind)}
            {plan.segments.map((g, i) => (
              <Sequence key={i} from={Math.round(g.out_s * fps)} durationInFrames={Math.round((g.src_e - g.src_s) * fps)} layout="none">
                <AbsoluteFill style={{transform: 'scale(.88)', transformOrigin: '0 100%'}}><OffthreadVideo src={staticFile('day0/subject.webm')} transparent muted trimBefore={Math.round(g.src_s * fps)} style={vid} /></AbsoluteFill>
              </Sequence>
            ))}
          </div>
          {cap ? <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,16,30,0) 74%, rgba(10,16,30,.5) 100%)'}} /> : null}
          <Resident t={t} hide={E('bear').some((b) => live(b)) || E('sheets').some((b) => live(b, .3))} />
          {R('phrase', Phrase)}
          {R('chip', ChipEl)}
          {R('bubble', Bubble)}
          {R('strike', Strike)}
          {R('bear', FlyBear)}
          {R('sheets', Sheets)}
          {R('stamp', Stamp)}
          {R('burst', EmojiBurst)}
          {R('sparkles', Sparkles as any)}
          {cap ? <Caption c={cap} t={t} raised={false} compact={false} /> : null}
          {R('progress', Progress as any)}
        </>
      ) : null}
      {R('title', Title)}
      {R('promise', Promise_)}
      {R('free', FreeDay)}
      {R('journey', Journey)}
      {R('inside', Inside)}
      {R('reviews', Reviews as any)}
      {R('price', Price)}
      {R('logo', LogoCard as any)}
      {R('wipe', Wipe)}
    </AbsoluteFill>
  );
};
