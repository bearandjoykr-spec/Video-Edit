// Vertical Instagram reels cut from the Little Steps welcome film. Mark and Joy stand cut out in the owner's paintings,
// big words above their heads, stickers following their faces, and the approved "Day 1 is free" end card.
// Plans: projects/2026-11-welcome-reels/build.py
import React from 'react';
import {AbsoluteFill, Easing, Img, OffthreadVideo, Sequence, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {useFonts} from './BearJoyClass';

type Ev = {type: string; s: number; e: number; [k: string]: any};
export type WelcomeReelPlan = {
  name: string; fps: number; duration: number; frames: number; speechEnd: number; bg: string; bgx: number;
  segments: {src_s: number; src_e: number; out_s: number}[];
  captions: {s: number; e: number; ko: string; hi: string; en?: string}[];
  events: Ev[]; zooms: {t: number; z: number; cx: number}[];
  faces: {fps: number; mark: number[][]; joy: number[][]};
};
const C = {navy: '#1E2D4D', deep: '#173B5C', ink: '#14203A', butter: '#F6F0BA', sky: '#AECCE6', white: '#FFFFFF', paper: '#FFF8EE', gold: '#E9C766'};
const FF = "'Pretendard', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif";
const SHADOW = '0 3px 8px rgba(10,16,30,.85), 0 0 26px rgba(10,16,30,.55), 0 10px 40px rgba(10,16,30,.4)';
const GLOW = '0 0 3px rgba(255,255,255,.95), 0 2px 22px rgba(255,255,255,.8), 0 12px 34px rgba(23,59,92,.25)';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const BEAR = 'brand/bear-butterfly.png';
const S = .92;                  // Mark and Joy, drawn at this size, standing on the bottom of the frame
const TOP = 1920 - 1080 * S;
const pop = (t: number, at: number, soft = false) => spring({frame: Math.round((t - at) * 30), fps: 30, config: soft ? {damping: 14, stiffness: 130, mass: .8} : {damping: 8, stiffness: 210, mass: .55}});
const out = (t: number, e: number, d = .18) => interpolate(t, [e - d, e], [1, 0], clamp);

const Sky: React.FC<{plan: WelcomeReelPlan; t: number}> = ({plan, t}) => {
  const w = 1920 / 941 * 1672;   // the painting at full frame height
  const x = -plan.bgx - t * 7;
  return (
    <AbsoluteFill>
      <Img src={staticFile(`day0/${plan.bg}.jpg`)} style={{position: 'absolute', left: x, top: 0, width: w, height: 1920, maxWidth: 'none'}} />
      {[0, 1, 2, 0].map((c, i) => {
        const xx = ((i * 500 + t * (22 + i * 8)) % 1800) - 620;
        return <Img key={i} src={staticFile(`day0/cloud${c}.png`)} style={{position: 'absolute', left: xx, top: 120 + (i * 190) % 560, width: 620 + i * 60, opacity: .9}} />;
      })}
      {Array.from({length: 14}).map((_, i) => {
        const xx = random(`rx${i}`) * 1080, yy = 1920 - ((t * (18 + random(`ry${i}`) * 30) + random(`r0${i}`) * 1920) % 2000);
        return <div key={i} style={{position: 'absolute', left: xx, top: yy, fontSize: 22 + random(`rs${i}`) * 30, color: i % 2 ? C.gold : C.white, opacity: .75 * Math.abs(Math.sin(t * 1.3 + i))}}>✦</div>;
      })}
    </AbsoluteFill>
  );
};

const headAt = (plan: WelcomeReelPlan, who: 'mark' | 'joy', t: number) => {
  const g = plan.segments.find((x) => t >= x.out_s && t < x.out_s + x.src_e - x.src_s) ?? plan.segments[0];
  const src = g.src_s + t - g.out_s, list = plan.faces[who], f = src * plan.faces.fps;
  const a = list[Math.min(list.length - 1, Math.max(0, Math.floor(f)))], b = list[Math.min(list.length - 1, Math.max(0, Math.floor(f) + 1))], m = f - Math.floor(f);
  const mix = (i: number) => a[i] + (b[i] - a[i]) * m;
  return {x: mix(0), y: mix(1), w: mix(2)};   // source pixels
};

const Word: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const k = pop(t, ev.s), o = Math.min(1, k * 3) * out(t, ev.e);
  return (
    <div style={{position: 'absolute', left: 50, right: 110, top: ev.y ?? 340, textAlign: 'center', opacity: o, transform: `scale(${.5 + .5 * k})`, fontFamily: FF, textShadow: GLOW, wordBreak: 'keep-all'}}>
      {ev.small ? <div style={{color: C.deep, fontWeight: 800, fontSize: 62, marginBottom: 6}}>{ev.small}</div> : null}
      <div style={{color: ev.tone === 'sky' ? '#2C6AA6' : C.deep, fontWeight: 900, fontSize: ev.size ?? 190, lineHeight: 1.04, letterSpacing: '-.03em'}}>{ev.big}</div>
    </div>
  );
};

const Bubble: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const k = pop(t, ev.s), o = Math.min(1, k * 3) * out(t, ev.e);
  return (
    <div style={{position: 'absolute', left: ev.x, right: ev.right, top: ev.y, maxWidth: ev.w ?? 640, opacity: o, transform: `scale(${.4 + .6 * k})`, background: C.paper, color: C.deep, borderRadius: 44, padding: '28px 40px', fontFamily: FF, fontWeight: 900, fontSize: ev.size ?? 66, lineHeight: 1.18, boxShadow: '0 16px 44px rgba(10,16,30,.3)', textAlign: 'center', wordBreak: 'keep-all', textWrap: 'balance' as any}}>{ev.text}</div>
  );
};

const Chip: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const k = pop(t, ev.s), o = Math.min(1, k * 3) * out(t, ev.e);
  return (
    <div style={{position: 'absolute', left: ev.x, right: ev.right, top: ev.y, opacity: o, transform: `scale(${.5 + .5 * k}) translateY(${Math.sin((t - ev.s) * 2.4 + (ev.y ?? 0)) * 5}px)`, background: ev.tone === 'sky' ? C.sky : C.butter, color: C.ink, border: '4px solid rgba(255,255,255,.8)', borderRadius: 30, padding: '16px 30px', fontFamily: FF, fontWeight: 900, fontSize: ev.size ?? 56, display: 'flex', gap: 14, alignItems: 'center', boxShadow: '0 12px 34px rgba(10,16,30,.28)', wordBreak: 'keep-all'}}>
      {ev.emoji ? <span style={{fontSize: (ev.size ?? 56) * 1.2}}>{ev.emoji}</span> : null}{ev.text}
    </div>
  );
};

const Strike: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const k = pop(t, ev.s), o = Math.min(1, k * 3) * out(t, ev.e);
  const line = interpolate(t, [ev.s + ev.at, ev.s + ev.at + .25], [0, 100], {...clamp, easing: Easing.out(Easing.cubic)});
  return (
    <div style={{position: 'absolute', left: 50, right: 110, top: ev.y ?? 460, display: 'grid', justifyItems: 'center', opacity: o, transform: `scale(${.6 + .4 * k})`, fontFamily: FF}}>
      <div style={{position: 'relative', background: C.navy, color: C.white, borderRadius: 30, padding: '20px 46px', fontWeight: 900, fontSize: ev.size ?? 104, boxShadow: '0 14px 38px rgba(10,16,30,.3)', whiteSpace: 'nowrap'}}>
        {ev.text}
        <div style={{position: 'absolute', left: 16, top: '47%', height: 11, width: `calc(${line}% - ${line * .32}px)`, background: '#F2877B', borderRadius: 9, transform: 'rotate(-2deg)'}} />
      </div>
    </div>
  );
};

const Burst: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const p = (t - ev.s) / (ev.e - ev.s);
  if (p < 0 || p > 1) return null;
  return (
    <>
      {Array.from({length: ev.n ?? 20}).map((_, i) => {
        const a = random(`ba${ev.s}${i}`) * Math.PI * 2, d = 120 + random(`bd${ev.s}${i}`) * (ev.big ? 800 : 440), q = Easing.out(Easing.cubic)(p);
        return <div key={i} style={{position: 'absolute', left: ev.x + Math.cos(a) * d * q, top: ev.y + Math.sin(a) * d * q + p * p * 220, fontSize: 56 + random(`bz${ev.s}${i}`) * (ev.big ? 110 : 60), opacity: interpolate(p, [0, .1, .7, 1], [0, 1, 1, 0]), transform: `rotate(${p * 200 * (i % 2 ? 1 : -1)}deg) scale(${interpolate(p, [0, .2], [.3, 1], clamp)})`}}>{(ev.emoji as string[])[i % ev.emoji.length]}</div>;
      })}
    </>
  );
};

// Emoji sticker that follows a face, drawn inside the camera
const Stick: React.FC<{ev: Ev; t: number; plan: WelcomeReelPlan}> = ({ev, t, plan}) => {
  const k = pop(t, ev.s), o = Math.min(1, k * 3) * out(t, ev.e);
  const wob = Math.sin((t - ev.s) * 5) * 4;
  const h = headAt(plan, ev.who, t);
  return <div style={{position: 'absolute', left: h.x + ev.dx * h.w - ev.size / 2, top: h.y + ev.dy * h.w - ev.size / 2, fontSize: ev.size, lineHeight: 1, opacity: o, fontFamily: FF, transform: `scale(${.4 + .6 * k}) rotate(${(ev.rot ?? 0) + wob}deg)`, filter: 'drop-shadow(0 8px 12px rgba(10,16,30,.3))'}}>{ev.emoji}</div>;
};

const BearArt: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const k = pop(t, ev.s), o = out(t, ev.e);
  if (ev.giant) {
    const x = interpolate(t, [ev.s, ev.s + .18], [-800, 0], {...clamp, easing: Easing.out(Easing.back(1.6))});
    return <div style={{position: 'absolute', left: ev.x, top: ev.y, width: ev.h * .68, height: ev.h, overflow: 'hidden', opacity: o, transform: `translateX(${x}px) rotate(${-8 + Math.sin(t * 7) * 3}deg)`}}><Img src={staticFile(BEAR)} style={{height: ev.h, maxWidth: 'none'}} /></div>;
  }
  return <Img src={staticFile(BEAR)} style={{position: 'absolute', left: ev.x, top: ev.y + (1 - k) * 500, height: ev.h, opacity: o, maxWidth: 'none', transform: `rotate(${Math.sin((t - ev.s) * 7) * 4}deg)`, filter: 'drop-shadow(0 16px 26px rgba(10,16,30,.3))'}} />;
};

const Caption: React.FC<{c: WelcomeReelPlan['captions'][0]; t: number}> = ({c, t}) => {
  const o = interpolate(t, [c.s, c.s + .08, c.e - .06, c.e], [0, 1, 1, 0], clamp);
  const parts = c.hi ? c.ko.split(c.hi) : [c.ko];
  return (
    <div style={{position: 'absolute', left: 60, right: 110, top: 1400, textAlign: 'center', opacity: o, fontFamily: FF, fontWeight: 800, fontSize: 58, lineHeight: 1.28, color: C.white, textShadow: SHADOW, wordBreak: 'keep-all', textWrap: 'balance' as any}}>
      {c.en ? <div style={{fontWeight: 900, fontSize: 60, color: C.sky, marginBottom: 6, letterSpacing: '-.01em'}}>{c.en}</div> : null}
      {parts.map((x, i) => <React.Fragment key={i}>{x}{i < parts.length - 1 ? <span style={{color: C.butter}}>{c.hi}</span> : null}</React.Fragment>)}
    </div>
  );
};

const Top: React.FC<{plan: WelcomeReelPlan; t: number}> = ({plan, t}) => {
  const p = interpolate(t, [0, plan.speechEnd], [0, 1], clamp);
  return (
    <>
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 12, background: 'rgba(20,32,58,.3)'}}>
        <div style={{height: '100%', width: `${p * 100}%`, background: C.butter}} />
        <Img src={staticFile(BEAR)} style={{position: 'absolute', left: `calc(${p * 100}% - 48px)`, top: 12, height: 90, maxWidth: 'none', transform: `translateY(${Math.abs(Math.sin(t * 5)) * 4}px)`}} />
      </div>
      <div style={{position: 'absolute', right: 40, top: 150, background: C.butter, color: C.ink, fontFamily: FF, fontWeight: 800, fontSize: 36, padding: '10px 26px', borderRadius: 99, boxShadow: '0 8px 24px rgba(10,16,30,.25)'}}>🐾 Little Steps · 첫날 무료</div>
    </>
  );
};

// The approved end card, with what a free account gets, as confirmed by the owner on 5 Nov 2026
const End: React.FC<{plan: WelcomeReelPlan; t: number}> = ({plan, t}) => {
  const {fps} = useVideoConfig();
  const s = plan.speechEnd;
  const bg = interpolate(t, [s - .05, s + .3], [0, 1], clamp);
  const sp = (d: number, damping = 11) => spring({frame: Math.round((t - s - d) * fps), fps, config: {damping, stiffness: 170}});
  const top = sp(.1), l1 = sp(.5, 9), l2 = sp(.7, 9), row = sp(1.2), btn = sp(1.6, 8), url = sp(2);
  const pulse = 1 + .03 * Math.sin((t - s) * 7);
  return (
    <AbsoluteFill style={{background: `rgba(20,32,58,${.96 * bg})`, display: 'grid', placeContent: 'center', justifyItems: 'center', gap: 24, textAlign: 'center', padding: '0 70px', fontFamily: FF}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 16, opacity: top, transform: `translateY(${(1 - top) * 24}px)`}}>
        <Img src={staticFile(BEAR)} style={{width: 200, transform: `translateY(${Math.sin(t * 4) * 6}px)`}} />
        <Img src={staticFile('brand/wordmark-cream.png')} style={{width: 540}} />
      </div>
      <div style={{fontWeight: 900, fontSize: 132, lineHeight: 1.08, letterSpacing: '-.04em', textShadow: SHADOW, marginTop: 20}}>
        <div style={{color: C.butter, transform: `scale(${l1})`}}>1일차는</div>
        <div style={{color: C.sky, transform: `scale(${l2})`}}>무료예요!</div>
      </div>
      <div style={{opacity: row, transform: `translateY(${(1 - row) * 20}px)`, display: 'grid', justifyItems: 'center', gap: 14, marginTop: 10, color: C.white, fontWeight: 800, fontSize: 48}}>
        <div>1일차 전체 영상 · 워크시트</div>
        <div>웹사이트 놀이 게임</div>
        <div style={{display: 'flex', alignItems: 'center', gap: 12}}>
          <Img src={staticFile('brand/mark-avatar.png')} style={{width: 88, height: 88}} />
          <Img src={staticFile('brand/joy-avatar.png')} style={{width: 88, height: 88}} />
          <span style={{marginLeft: 6}}>Mark와 Joy의 지원까지</span>
        </div>
      </div>
      <div style={{marginTop: 26, background: C.sky, color: C.ink, fontWeight: 900, fontSize: 70, padding: '30px 66px', borderRadius: 999, transform: `scale(${btn * pulse})`, boxShadow: '0 16px 40px rgba(0,0,0,.35)'}}>1일차 무료로 시작하기</div>
      <div style={{color: C.white, fontWeight: 700, fontSize: 44, opacity: url}}>bearandjoy.com/littlesteps</div>
    </AbsoluteFill>
  );
};

export const BearJoyWelcomeReel: React.FC<{plan: WelcomeReelPlan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const E = (type: string) => plan.events.filter((e) => e.type === type && t >= e.s - .05 && t <= e.e + .05);

  let z = 1, prev = 1, since = 99, cx = 948;
  for (const k of plan.zooms) if (k.t <= t) { prev = z; z = k.z; since = t - k.t; cx = k.cx; }
  z = prev + (z - prev) * interpolate(since, [0, .25], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  z *= 1 + .012 * Math.sin(t * .6);
  const hit = plan.events.find((e) => e.type === 'shake' && t >= e.s && t < e.s + .4);
  const sx = hit ? Math.sin(t * 90) * 12 * (1 - (t - hit.s) / .4) : 0;
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const main = t < plan.speechEnd + .4;
  // cx stays smooth so the camera glides between the two of them
  const smooth = plan.zooms.filter((k) => k.t <= t).slice(-1)[0];
  const before = plan.zooms.filter((k) => k.t <= t).slice(-2)[0];
  const glide = smooth && before ? before.cx + (smooth.cx - before.cx) * interpolate(t - smooth.t, [0, .4], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)}) : cx;
  // this box is the source frame; its size and position place Mark and Joy on the bottom of the reel
  const stage: React.CSSProperties = {position: 'absolute', left: 540 - glide * S + sx, top: TOP, width: 1920, height: 1080, transform: `scale(${S})`, transformOrigin: '0 0'};

  return (
    <AbsoluteFill style={{background: C.navy}}>
      {main ? (
        <>
          <Sky plan={plan} t={t} />
          {E('word').map((ev, k) => <Word key={k} ev={ev} t={t} />)}
          <div style={{position: 'absolute', inset: 0, transform: `scale(${z})`, transformOrigin: '50% 72%'}}>
            <div style={stage}>
              {plan.segments.map((g, i) => (
                <Sequence key={i} from={Math.round(g.out_s * fps)} durationInFrames={Math.round((g.src_e - g.src_s) * fps) + (i === plan.segments.length - 1 ? 12 : 0)} layout="none">
                  <AbsoluteFill><OffthreadVideo src={staticFile('day0/subject.webm')} transparent muted trimBefore={Math.round(g.src_s * fps)} style={{width: 1920, height: 1080, filter: 'contrast(1.05) saturate(1.1)'}} /></AbsoluteFill>
                </Sequence>
              ))}
              {E('stick').map((ev, k) => <Stick key={k} ev={ev} t={t} plan={plan} />)}
            </div>
          </div>
          {cap ? <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,16,30,0) 66%, rgba(10,16,30,.6) 74%, rgba(10,16,30,.68) 84%, rgba(10,16,30,.3) 100%)'}} /> : null}
          {E('strike').map((ev, k) => <Strike key={k} ev={ev} t={t} />)}
          {E('bubble').map((ev, k) => <Bubble key={k} ev={ev} t={t} />)}
          {E('chip').map((ev, k) => <Chip key={k} ev={ev} t={t} />)}
          {E('bear').map((ev, k) => <BearArt key={k} ev={ev} t={t} />)}
          {E('burst').map((ev, k) => <Burst key={k} ev={ev} t={t} />)}
          <Top plan={plan} t={t} />
          {cap && t < plan.speechEnd ? <Caption c={cap} t={t} /> : null}
        </>
      ) : null}
      {t >= plan.speechEnd - .1 ? <End plan={plan} t={t} /> : null}
    </AbsoluteFill>
  );
};
