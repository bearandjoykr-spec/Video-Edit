// The Bear & Joy Co. reel template v2 — high-energy "daily posting" style.
// Owner-approved changes over v1: karaoke captions, key-point pops, flags, Day badge, punch zooms,
// progress bar with the bear walking along it, big follow CTA.
// Type: Pretendard throughout, soft shadows, pastel butter-yellow / sky-blue key words (owner reference, 4 Nov 2026).
import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate,
  staticFile, useCurrentFrame, useVideoConfig, Easing, random, spring,
} from 'remotion';

type W = {w: string; t: number | null};
type Caption = {i: number; s: number; e: number; ko: string; en: string; hi: string; demo: boolean; words: W[]; kwords?: W[]; mark?: boolean};
type Ev = {type: string; s: number; e: number; [k: string]: any};
export type PlanV2 = {
  name: string; fps: number; duration: number; frames: number; speechEnd: number; day: number;
  captions: Caption[]; events: Ev[]; zooms: {t: number; z: number}[];
  // optional per-video layout (defaults suit Day 23 framing)
  media?: string;
  scrim?: boolean; // dark gradient behind the lower half, for light clothing or bright backgrounds
  slots?: Record<string, {left?: number; right?: number; top: number; rot: number}>; tagPos?: {left: number; top: number}; captionTop?: number;
};

const C = {navy: '#1E2D4D', ink: '#14203A', yellow: '#F6F0BA', blue: '#AECCE6', gold: '#C9A84C', cream: '#F5F0E6', white: '#FFFFFF', kakao: '#FEE500'};
const PASTEL = [C.yellow, C.blue];
const EMOJI = "'Noto Color Emoji'";
const PRE = `'Pretendard', ${EMOJI}, 'Noto Sans KR', sans-serif`;
const HAN = PRE, JUA = PRE, LILITA = PRE, POPPINS = PRE;
const PLAYFAIR = "'Playfair Display', Georgia, serif";
const GRADE = 'contrast(1.1) saturate(1.18) brightness(1.03) sepia(0.04)';

const FONTS: [string, string, string, string][] = [
  ['Pretendard', 'normal', '600', 'Pretendard-SemiBold.woff2'],
  ['Pretendard', 'normal', '700', 'Pretendard-Bold.woff2'],
  ['Pretendard', 'normal', '800', 'Pretendard-ExtraBold.woff2'],
  ['Pretendard', 'normal', '900', 'Pretendard-Black.woff2'],
  ['Noto Color Emoji', 'normal', '400', 'Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf'],
  ['Playfair Display', 'italic', '400', 'nuFRD-vYSZviVYUb_rj3ij__anPXDTnCjmHKM4nYO7KN_qiTbtY.ttf'],
  ['Playfair Display', 'italic', '600', 'nuFRD-vYSZviVYUb_rj3ij__anPXDTnCjmHKM4nYO7KN_naUbtY.ttf'],
];

const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([f, s, w, file]) => new FontFace(f, `url(${staticFile('fonts/' + file)})`, {style: s, weight: w}).load()
      .then((x) => document.fonts.add(x)))).then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
  }, [h]);
};

// Thick outline that works on any text (ring of hard shadows) + soft drop shadow.
const stroke = (px: number) =>
  `0 ${Math.max(1, px / 3).toFixed(1)}px ${px}px rgba(10,16,30,.55), 0 ${px / 2}px ${px * 4}px rgba(10,16,30,.35)`;
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

// Bouncy entrance (0 -> overshoot -> 1) and quick exit.
const usePop = (t: number, s: number, e: number, fps: number) => {
  const f = Math.round((t - s) * fps);
  const inS = spring({frame: f, fps, config: {damping: 9, stiffness: 180, mass: 0.6}});
  const out = interpolate(t, [e - 0.15, e], [1, 0], clamp);
  return {scale: inS * interpolate(out, [0, 1], [0.7, 1]), opacity: Math.min(1, inS * 3) * out};
};

const pullAmount = (ev: Ev, t: number) =>
  interpolate(t, [ev.s, ev.s + 0.22, ev.e - 0.2, ev.e], [0, 1, 1, 0], {...clamp, easing: Easing.inOut(Easing.cubic)});

const cameraAt = (plan: PlanV2, t: number) => {
  // rhythm zoom with a fast ease into each new level
  let z = 1, prev = 1, since = 99;
  for (const k of plan.zooms) if (k.t <= t + 1e-6) { prev = z; z = k.z; since = t - k.t; }
  z = prev + (z - prev) * interpolate(since, [0, 0.12], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  let x = 0, y = 0;
  for (const ev of plan.events) {
    if (ev.type === 'punch' && t >= ev.s && t <= ev.e + 0.25) {
      if (ev.hold) { z = Math.max(z, interpolate(t, [ev.s, ev.s + 0.08, ev.e, ev.e + 0.15], [z, ev.z, ev.z, z], clamp)); }
      else z *= 1 + (ev.z - 1) * interpolate(t, [ev.s, ev.s + 0.06, ev.e + 0.25], [0, 1, 0], clamp);
      const amp = ev.shake * interpolate(t, [ev.s, ev.s + (ev.hold ? 3 : 0.35)], [1, ev.hold ? 0.4 : 0], clamp);
      x += Math.sin(t * 71) * amp; y += Math.cos(t * 57) * amp;
    }
    if (ev.type === 'push' && t >= ev.s && t <= ev.e) z *= interpolate(t, [ev.s, ev.e], [ev.from, ev.to], {easing: Easing.inOut(Easing.quad)});
    if (ev.type === 'pull' && t >= ev.s && t <= ev.e + 0.05) {
      const a = pullAmount(ev, t);
      z = z * (1 - a) + ev.z * a; y += a * 300;
    }
  }
  return {z, x, y};
};

const Hi: React.FC<{text: string; hi: string; pop: number}> = ({text, hi, pop}) => {
  const i = hi ? text.indexOf(hi) : -1;
  if (i < 0) return <>{text}</>;
  return <>{text.slice(0, i)}<span style={{color: C.yellow, display: 'inline-block', transform: `scale(${pop})`}}>{hi}</span>{text.slice(i + hi.length)}</>;
};

const CaptionV2: React.FC<{c: Caption; t: number; fps: number; top?: number}> = ({c, t, fps, top = 1170}) => {
  const f = Math.round((t - c.s) * fps);
  const inS = spring({frame: f, fps, config: {damping: 14, stiffness: 220}});
  const hiPop = 1 + 0.18 * spring({frame: f - 3, fps, config: {damping: 7, stiffness: 200}}) - 0.18 * spring({frame: f - 9, fps, config: {damping: 14}});
  const ws = c.words;
  return (
    <div style={{position: 'absolute', left: 50, right: 50, top, textAlign: 'center', display: 'grid', gap: 16,
      transform: `translateY(${(1 - inS) * 26}px) scale(${interpolate(inS, [0, 1], [0.92, 1])})`, opacity: Math.min(1, inS * 2)}}>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 74, lineHeight: 1.2, letterSpacing: '-0.02em', color: C.white, textShadow: stroke(8), wordBreak: 'keep-all', textWrap: 'balance' as any}}>
        {c.kwords && c.kwords.length ? c.kwords.map((w, k) => {
          const next = c.kwords![k + 1]?.t ?? c.e;
          const active = w.t !== null && t >= w.t && t < next;
          const said = w.t !== null && t >= w.t;
          const isHi = !!c.hi && c.hi.split(' ').some((h) => h && w.w.includes(h.replace(/[,.?!']/g, '')));
          return <React.Fragment key={k}>{k ? ' ' : ''}<span style={{display: 'inline-block', color: isHi ? C.yellow : active ? C.blue : C.white,
            opacity: said ? 1 : 0.62, transform: `scale(${active ? 1.06 : 1}) translateY(${active ? -3 : 0}px)`}}>{w.w}</span></React.Fragment>;
        }) : <Hi text={c.ko} hi={c.hi} pop={hiPop} />}
      </div>
      {c.en ? (
        <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 40, lineHeight: 1.25, textShadow: stroke(6), textWrap: 'balance' as any}}>
          {ws.length ? ws.map((w, k) => {
            const next = ws[k + 1]?.t ?? c.e;
            const active = w.t !== null && t >= w.t && t < next;
            const said = w.t !== null && t >= w.t;
            return <React.Fragment key={k}>{k ? ' ' : ''}<span style={{display: 'inline-block', padding: '0 0.08em', color: active ? C.blue : C.white,
              opacity: said ? 1 : 0.6, transform: `scale(${active ? 1.07 : 1}) translateY(${active ? -3 : 0}px)`}}>{w.w}</span></React.Fragment>;
          }) : <span style={{color: C.white, opacity: 0.9}}>{c.en}</span>}
        </div>
      ) : null}
    </div>
  );
};

// Mark's recorded English (Joy, Day 28): his avatar with a UK flag, the English line in Playfair Display italic
// (a different font from Joy's Korean captions) lighting up sky blue as he speaks, and the Korean translation under it.
const MarkCaption: React.FC<{c: Caption; t: number; fps: number; top?: number}> = ({c, t, fps, top = 1170}) => {
  const f = Math.round((t - c.s) * fps);
  const inS = spring({frame: f, fps, config: {damping: 12, stiffness: 220}});
  const av = spring({frame: f, fps, config: {damping: 9, stiffness: 200, mass: 0.6}});
  const ws = c.words;
  return (
    <div style={{position: 'absolute', left: 50, right: 50, top: top - 150, textAlign: 'center', display: 'grid', justifyItems: 'center', gap: 10,
      opacity: Math.min(1, inS * 2)}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 18, transform: `scale(${av}) rotate(${Math.sin((t - c.s) * 4) * 1.5}deg)`}}>
        <div style={{position: 'relative', width: 128, height: 128}}>
          <Img src={staticFile('brand/mark-avatar.png')} style={{width: 128, height: 128, filter: 'drop-shadow(0 8px 18px rgba(0,0,0,.35))'}} />
          <div style={{position: 'absolute', right: -14, bottom: -6, fontFamily: EMOJI, fontSize: 52, lineHeight: 1}}>🇬🇧</div>
        </div>
        <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 46, color: C.white, textShadow: stroke(8), whiteSpace: 'nowrap'}}>마크 선생님</div>
      </div>
      <div style={{fontFamily: PLAYFAIR, fontStyle: 'italic', fontWeight: 600, fontSize: 80, lineHeight: 1.12, letterSpacing: '-0.005em',
        textShadow: stroke(9), textWrap: 'balance' as any, transform: `translateY(${(1 - inS) * 22}px)`}}>
        {ws.map((w, k) => {
          const next = ws[k + 1]?.t ?? c.e;
          const active = w.t !== null && t >= w.t && t < next;
          const said = w.t !== null && t >= w.t;
          return <React.Fragment key={k}>{k ? ' ' : ''}<span style={{display: 'inline-block', color: said ? C.blue : C.white,
            opacity: said ? 1 : 0.6, transform: `scale(${active ? 1.07 : 1}) translateY(${active ? -4 : 0}px)`}}>{w.w}</span></React.Fragment>;
        })}
      </div>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 54, lineHeight: 1.2, color: C.white, textShadow: stroke(8), wordBreak: 'keep-all',
        opacity: interpolate(t, [c.s + 0.15, c.s + 0.4], [0, 1], clamp)}}>{c.ko}</div>
    </div>
  );
};

const Behind: React.FC<{ev: Ev; t: number; fps: number}> = ({ev, t, fps}) => {
  const p = usePop(t, ev.s, ev.e, fps);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: ev.top - 90, textAlign: 'center', opacity: p.opacity,
      transform: `scale(${p.scale})`, transformOrigin: '50% 70%'}}>
      <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 66, color: C.white, textShadow: stroke(10), marginBottom: 6}}>{ev.en}</div>
      <div style={{fontFamily: PRE, fontWeight: 900, fontSize: ev.size, lineHeight: 1, letterSpacing: '-0.03em', color: PASTEL[ev.k % 2],
        textShadow: stroke(16), whiteSpace: 'nowrap'}}>{ev.ko}</div>
    </div>
  );
};

const SLOTS: Record<string, React.CSSProperties & {rot: number}> = {
  tl: {left: 50, top: 420, rot: -6}, tr: {right: 50, top: 420, rot: 6}, center: {left: 0, right: 0, top: 380, rot: -3},
  stack0: {left: 0, right: 0, top: 300, rot: -4}, stack1: {left: 0, right: 0, top: 460, rot: 3}, stack2: {left: 0, right: 0, top: 620, rot: -3},
};
const Pop: React.FC<{ev: Ev; t: number; fps: number; slots?: PlanV2['slots']}> = ({ev, t, fps, slots}) => {
  const p = usePop(t, ev.s, ev.e, fps);
  const {rot, ...pos} = (slots && slots[ev.slot]) || SLOTS[ev.slot];
  const centered = pos.left === 0 && pos.right === 0;
  const wobble = Math.sin((t - ev.s) * 6) * 1.5;
  return (
    <div style={{position: 'absolute', ...pos, display: 'flex', justifyContent: centered ? 'center' : undefined, opacity: p.opacity}}>
      <div style={{transform: `scale(${p.scale}) rotate(${(rot + wobble) * 0.3}deg)`, textAlign: 'center', display: 'grid', justifyItems: 'center', gap: 4}}>
        {ev.kicker ? <div style={{fontFamily: PRE, fontWeight: 700, fontSize: ev.size ? 62 : 50, color: C.white, textShadow: stroke(10)}}>{ev.kicker}</div> : null}
        <div style={{color: PASTEL[ev.k % 2], fontFamily: PRE, fontWeight: 900, fontSize: ev.size ?? (ev.text.length > 12 ? 80 : 92),
          lineHeight: 1.05, letterSpacing: '-0.03em', textShadow: stroke(14), whiteSpace: 'nowrap'}}>{ev.text}</div>
      </div>
    </div>
  );
};

const Demo: React.FC<{ev: Ev; t: number; fps: number}> = ({ev, t, fps}) => {
  const pos = [{left: 60, top: 360, rot: -8, size: 120}, {right: 60, top: 540, rot: 7, size: 120}, {left: 0, right: 0, top: 1150, rot: -4, size: 150}];
  return (
    <>
      {ev.words.map((w: W, k: number) => {
        if (w.t === null || t < w.t) return null;
        const p = usePop(t, w.t, ev.e + 0.2, fps);
        const {rot, size, ...at} = pos[k];
        return (
          <div key={k} style={{position: 'absolute', ...at, textAlign: 'center', opacity: p.opacity,
            transform: `scale(${p.scale}) rotate(${rot}deg)`}}>
            <span style={{fontFamily: PRE, fontWeight: 900, fontSize: size, letterSpacing: '-0.03em', color: [C.white, C.blue, C.yellow][k], textShadow: stroke(14)}}>{w.w}</span>
          </div>
        );
      })}
    </>
  );
};

const Avatar: React.FC<{ev: Ev; t: number; fps: number; slots?: PlanV2['slots']}> = ({ev, t, fps, slots}) => {
  const p = usePop(t, ev.s, ev.e, fps);
  const top = ((slots && slots[ev.slot]) || SLOTS.center).top - 40;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top, display: 'flex', justifyContent: 'center', opacity: p.opacity}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 26, transform: `scale(${p.scale}) rotate(-2deg)`}}>
        <Img src={staticFile(ev.img)} style={{width: 250, height: 250, filter: 'drop-shadow(0 12px 24px rgba(0,0,0,.35))',
          transform: `rotate(${Math.sin((t - ev.s) * 5) * 4}deg)`}} />
        <div style={{display: 'grid', gap: 4, textAlign: 'left'}}>
          <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 48, color: C.white, textShadow: stroke(10)}}>{ev.kicker}</div>
          <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 84, color: C.blue, textShadow: stroke(14), whiteSpace: 'nowrap', letterSpacing: '-0.03em'}}>{ev.text}</div>
        </div>
      </div>
    </div>
  );
};

// A book cover that bounces in, floats, and catches a light sweep (Day 25: Bear & Joy Book 1).
const Cover: React.FC<{ev: Ev; t: number; fps: number}> = ({ev, t, fps}) => {
  const f = Math.round((t - ev.s) * fps);
  const inS = spring({frame: f, fps, config: {damping: 10, stiffness: 120, mass: 0.8}});
  const out = interpolate(t, [ev.e - 0.2, ev.e], [1, 0], clamp);
  const sweep = interpolate((t - ev.s - 0.5) % 3.2, [0, 0.9], [-60, 160], clamp);
  const bob = Math.sin((t - ev.s) * 2.2) * 10;
  const width = ev.width ?? 680;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: ev.top ?? 440, display: 'flex', justifyContent: 'center', opacity: Math.min(1, inS * 2) * out}}>
      <div style={{position: 'relative', width, height: width, borderRadius: 18, overflow: 'hidden',
        transform: `translateY(${(1 - inS) * 260 + bob}px) scale(${interpolate(inS, [0, 1], [0.5, 1])}) rotate(${interpolate(inS, [0, 1], [-14, -2])}deg)`,
        boxShadow: '0 30px 70px rgba(10,16,30,.55), 0 0 0 10px rgba(255,255,255,.95)'}}>
        <Img src={staticFile(ev.img)} style={{width: '100%', height: '100%'}} />
        <div style={{position: 'absolute', inset: 0, background: `linear-gradient(115deg, rgba(255,255,255,0) ${sweep - 20}%, rgba(255,255,255,.55) ${sweep}%, rgba(255,255,255,0) ${sweep + 20}%)`}} />
      </div>
      {[[-0.42, -0.08, 0], [0.44, 0.1, 0.7], [-0.36, 0.86, 1.4], [0.4, 0.92, 2.1]].map(([x, y, d], k) => {
        const tw = 0.6 + 0.4 * Math.sin((t - ev.s) * 5 + d * 3);
        return <div key={k} style={{position: 'absolute', left: `calc(50% + ${x * width * 1.1}px)`, top: y * width - 30, fontSize: 80, fontFamily: EMOJI,
          opacity: inS * tw, transform: `scale(${tw}) rotate(${k * 20}deg)`}}>✨</div>;
      })}
    </div>
  );
};

const FollowNow: React.FC<{ev: Ev; t: number; fps: number}> = ({ev, t, fps}) => {
  const p = usePop(t, ev.s, ev.e, fps);
  const press = (tt: number) => interpolate(t, [tt - 0.06, tt, tt + 0.16], [0, 1, 0], clamp);
  const pressed = Math.max(press(ev.tap1), press(ev.tap2));
  const following = t >= ev.tap2;
  const handIn = interpolate(t, [ev.s + 0.1, ev.s + 0.4], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.6))});
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: 860, display: 'flex', justifyContent: 'center', opacity: p.opacity}}>
      <div style={{position: 'relative', transform: `scale(${p.scale * (1 - pressed * 0.07)})`}}>
        <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 96, lineHeight: 1, padding: '40px 120px', borderRadius: 999, letterSpacing: '-0.02em',
          background: following ? C.white : C.blue, color: C.ink, boxShadow: '0 18px 44px rgba(0,0,0,.4)'}}>{following ? '팔로잉 ✓' : '＋ 팔로우'}</div>
        <div style={{position: 'absolute', right: -50, top: 70, fontFamily: PRE, fontSize: 130, opacity: handIn,
          transform: `translateY(${(1 - handIn) * 160 + pressed * 20}px) rotate(-12deg)`}}>👆</div>
      </div>
    </div>
  );
};

const Tag: React.FC<{ev: Ev; t: number; fps: number; pos?: {left: number; top: number}}> = ({ev, t, fps, pos = {left: 50, top: 235}}) => {
  const p = usePop(t, ev.s, ev.e, fps);
  return (
    <div style={{position: 'absolute', left: pos.left, top: pos.top, opacity: p.opacity, transform: `scale(${p.scale}) rotate(-2deg)`, transformOrigin: '0 50%'}}>
      <div style={{background: 'rgba(20,32,58,.62)', borderRadius: 28, padding: '20px 30px', display: 'grid', gap: 8, boxShadow: '0 14px 34px rgba(0,0,0,.25)'}}>
        <span style={{fontFamily: PRE, fontWeight: 900, fontSize: 62, color: C.yellow, lineHeight: 1, letterSpacing: '-0.02em'}}>{ev.name} <span style={{fontSize: 52}}>{ev.flags}</span></span>
        <span style={{fontFamily: PRE, fontWeight: 600, fontSize: 32, color: C.white, lineHeight: 1.25}}>{ev.role}</span>
      </div>
    </div>
  );
};

const Badge: React.FC<{ev: Ev; t: number; fps: number}> = ({ev, t, fps}) => {
  const f = Math.round(t * fps);
  const inS = spring({frame: f - 4, fps, config: {damping: 10, stiffness: 160}});
  const shrink = interpolate(t, [3.2, 3.7], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const out = interpolate(t, [ev.e - 0.2, ev.e], [1, 0], clamp);
  // big and centred during the hook, then docks top-right
  const x = interpolate(shrink, [0, 1], [540, 900]), y = interpolate(shrink, [0, 1], [250, 205]), s = interpolate(shrink, [0, 1], [1, 0.5]);
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, 0) scale(${s * inS})`, transformOrigin: '50% 0', opacity: out,
      display: 'grid', justifyItems: 'center', gap: 10}}>
      <div style={{background: C.yellow, color: C.ink, fontFamily: PRE, fontWeight: 900, fontSize: 66, lineHeight: 1, padding: '18px 34px', borderRadius: 999,
        boxShadow: '0 10px 28px rgba(0,0,0,.28)', whiteSpace: 'nowrap', letterSpacing: '-0.01em'}}>🔥 DAY {ev.day}</div>
      <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 38, color: C.white, textShadow: stroke(8), opacity: 1 - shrink, whiteSpace: 'nowrap'}}>출간까지 매일 업로드 📚</div>
    </div>
  );
};

const Progress: React.FC<{t: number; total: number}> = ({t, total}) => {
  const p = Math.min(1, t / total);
  return (
    <>
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 12, background: 'rgba(20,32,58,.45)'}} />
      <div style={{position: 'absolute', left: 0, top: 0, height: 12, width: `${p * 100}%`, background: C.yellow}} />
      <Img src={staticFile('brand/bear-butterfly.png')} style={{position: 'absolute', top: 4, left: `calc(${p * 100}% - 46px)`, width: 92,
        transform: `rotate(${Math.sin(t * 9) * 6}deg) translateY(${Math.abs(Math.sin(t * 9)) * -6}px)`}} />
    </>
  );
};

const EndV2: React.FC<{ev: Ev; t: number; fps: number; day: number}> = ({ev, t, fps, day}) => {
  const bg = interpolate(t, [ev.s, ev.s + 0.35], [0, 1], clamp);
  const sp = (d: number, damping = 11) => spring({frame: Math.round((t - ev.s - d) * fps), fps, config: {damping, stiffness: 170}});
  const top = sp(0.15), small = sp(0.4), l1 = sp(0.6, 9), l2 = sp(0.8, 9), btn = sp(1.1, 8), kakao = sp(1.5);
  // the hand taps the follow button twice; on the second tap it flips to "following"
  const tap1 = ev.short ? 1e9 : ev.s + 2.0, tap2 = ev.short ? 1e9 : ev.s + 2.9;
  const press = (tt: number) => interpolate(t, [tt - 0.06, tt, tt + 0.16], [0, 1, 0], clamp);
  const pressed = Math.max(press(tap1), press(tap2));
  const following = t >= tap2;
  const handIn = ev.short ? 0 : interpolate(t, [ev.s + 1.5, ev.s + 1.85], [0, 1], {...clamp, easing: Easing.out(Easing.back(1.6))});
  const handY = (1 - handIn) * 160 + pressed * 18;
  const pulse = following ? 1 : 1 + 0.035 * Math.sin((t - ev.s) * 7);
  return (
    <AbsoluteFill style={{background: `rgba(20,32,58,${0.94 * bg})`, display: 'grid', placeContent: 'center', justifyItems: 'center', gap: 22,
      textAlign: 'center', padding: '0 60px', fontFamily: PRE}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 18, opacity: top, transform: `translateY(${(1 - top) * 24}px)`}}>
        <Img src={staticFile('brand/bear-butterfly.png')} style={{width: 210, transform: `translateY(${Math.sin(t * 4) * 6}px)`}} />
        <Img src={staticFile('brand/wordmark-cream.png')} style={{width: 560}} />
      </div>
      <div style={{fontWeight: 700, fontSize: 42, color: C.white, opacity: small, marginTop: 30}}>DAY {day} ✅ · 출간까지 매일 업로드 중 📚</div>
      <div style={{fontWeight: 900, fontSize: 116, lineHeight: 1.06, letterSpacing: '-0.04em', textShadow: stroke(14), wordBreak: 'keep-all'}}>
        <div style={{color: C.yellow, transform: `scale(${l1})`}}>{ev.short ? `내일 DAY ${day + 1}` : '팔로우하고'}</div>
        <div style={{color: C.blue, transform: `scale(${l2})`}}>{ev.short ? '또 만나요! 👋' : `DAY ${day + 1} 같이 봐요!`}</div>
      </div>
      <div style={{position: 'relative', marginTop: 26, transform: `scale(${btn * pulse * (1 - pressed * 0.06)})`}}>
        <div style={{fontWeight: 900, fontSize: 88, lineHeight: 1, padding: '36px 110px', borderRadius: 999, letterSpacing: '-0.02em',
          background: following ? C.white : C.blue, color: C.ink, boxShadow: '0 16px 40px rgba(0,0,0,.35)'}}>{following ? '팔로잉 ✓' : '＋ 팔로우'}</div>
        <div style={{position: 'absolute', right: -40, top: 60, fontSize: 120, opacity: handIn, transform: `translateY(${handY}px) rotate(-12deg)`}}>👆</div>
      </div>
      {ev.share ? <div style={{fontWeight: 800, fontSize: 46, color: C.white, marginTop: 34, opacity: kakao, textShadow: stroke(8),
        transform: `translateY(${(1 - kakao) * 16}px)`}}>{ev.share}</div> : null}
      <div style={{fontWeight: 700, fontSize: 34, background: C.kakao, color: '#191600', padding: '18px 38px', borderRadius: 999, marginTop: 40,
        opacity: kakao, transform: `scale(${0.9 + 0.1 * kakao})`}}>카카오톡 채널 추가하기</div>
    </AbsoluteFill>
  );
};

const Grain: React.FC<{frame: number}> = ({frame}) => (
  <svg width="1080" height="1920" style={{position: 'absolute', inset: 0, opacity: 0.05, mixBlendMode: 'overlay'}}>
    <filter id={`g${frame}`}><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={Math.floor(random(`g${frame}`) * 999)} /><feColorMatrix type="saturate" values="0" /></filter>
    <rect width="100%" height="100%" filter={`url(#g${frame})`} />
  </svg>
);

export const BearJoyReelV2: React.FC<{plan: PlanV2}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const cam = cameraAt(plan, t);
  const dir = plan.media ?? `confidence/${plan.name}`;
  const E = (type: string) => plan.events.filter((e) => e.type === type);
  const end = E('end')[0];
  const live = (e: Ev, pad = 0.2) => t >= e.s - 0.05 && t <= e.e + pad;
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const camStyle: React.CSSProperties = {position: 'absolute', inset: 0, transform: `translate(${cam.x}px, ${cam.y}px) scale(${cam.z})`, transformOrigin: '50% 36%'};
  const vid: React.CSSProperties = {width: '100%', height: '100%', objectFit: 'cover', filter: GRADE};
  return (
    <AbsoluteFill style={{background: C.navy}}>
      {E('pull').map((ev, k) => {
        const from = Math.max(0, Math.floor(ev.s * fps)), to = Math.ceil((ev.e + 0.1) * fps);
        return (
          <Sequence key={`b${k}`} from={from} durationInFrames={to - from} layout="none">
            <AbsoluteFill style={{opacity: pullAmount(ev, t)}}>
              <OffthreadVideo src={staticFile(`${dir}/cut.mov`)} muted trimBefore={from}
                style={{...vid, transform: 'scale(1.4)', filter: `${GRADE} blur(36px) brightness(.85)`}} />
            </AbsoluteFill>
          </Sequence>
        );
      })}
      <div style={camStyle}>
        <OffthreadVideo src={staticFile(`${dir}/cut.mov`)} muted style={vid} />
        {E('behind').map((ev, k) => (live(ev) ? <Behind key={k} ev={ev} t={t} fps={fps} /> : null))}
        {E('behind').map((ev, k) => {
          const from = Math.max(0, Math.floor((ev.s - 0.2) * fps)), to = Math.ceil((ev.e + 0.3) * fps);
          return (
            <Sequence key={`m${k}`} from={from} durationInFrames={to - from} layout="none">
              <AbsoluteFill><OffthreadVideo src={staticFile(`${dir}/matte.webm`)} transparent muted trimBefore={from} style={vid} /></AbsoluteFill>
            </Sequence>
          );
        })}
      </div>
      <AbsoluteFill style={{background: 'radial-gradient(130% 85% at 50% 40%, rgba(0,0,0,0) 62%, rgba(20,32,58,.3) 100%)'}} />
      <Grain frame={frame} />
      {plan.scrim ? <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,16,30,0) 38%, rgba(10,16,30,.42) 52%, rgba(10,16,30,.62) 72%, rgba(10,16,30,.45) 100%)'}} /> : null}
      {E('tag').map((ev, k) => (live(ev) ? <Tag key={k} ev={ev} t={t} fps={fps} pos={plan.tagPos} /> : null))}
      {E('cover').map((ev, k) => (live(ev) ? <Cover key={k} ev={ev} t={t} fps={fps} /> : null))}
      {E('pop').map((ev, k) => (live(ev) ? <Pop key={k} ev={ev} t={t} fps={fps} slots={plan.slots} /> : null))}
      {E('avatar').map((ev, k) => (live(ev) ? <Avatar key={k} ev={ev} t={t} fps={fps} slots={plan.slots} /> : null))}
      {E('follow').map((ev, k) => (live(ev) ? <FollowNow key={k} ev={ev} t={t} fps={fps} /> : null))}
      {E('demo').map((ev, k) => (live(ev, 0.4) ? <Demo key={k} ev={ev} t={t} fps={fps} /> : null))}
      {cap && !cap.demo && !cap.mark && t < end.s ? <CaptionV2 c={cap} t={t} fps={fps} top={plan.captionTop} /> : null}
      {cap && cap.mark && t < end.s ? <MarkCaption c={cap} t={t} fps={fps} top={plan.captionTop} /> : null}
      {E('badge').map((ev, k) => (t <= ev.e ? <Badge key={k} ev={ev} t={t} fps={fps} /> : null))}
      {t >= end.s ? <EndV2 ev={end} t={t} fps={fps} day={plan.day} /> : null}
      <Progress t={t} total={plan.duration} />
    </AbsoluteFill>
  );
};
