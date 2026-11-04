// The Bear & Joy Co. reel template v2 — high-energy "daily posting" style.
// Owner-approved changes over v1: catchy reel fonts, karaoke captions, key-point pops, flags,
// Day badge, punch zooms, progress bar with the bear walking along it.
import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Img, OffthreadVideo, Sequence, continueRender, delayRender, interpolate,
  staticFile, useCurrentFrame, useVideoConfig, Easing, random, spring,
} from 'remotion';

type W = {w: string; t: number | null};
type Caption = {i: number; s: number; e: number; ko: string; en: string; hi: string; demo: boolean; words: W[]};
type Ev = {type: string; s: number; e: number; [k: string]: any};
export type PlanV2 = {
  name: string; fps: number; duration: number; frames: number; speechEnd: number; day: number;
  captions: Caption[]; events: Ev[]; zooms: {t: number; z: number}[];
};

const C = {navy: '#1E2D4D', ink: '#14203A', yellow: '#FFD23F', gold: '#C9A84C', cream: '#F5F0E6', white: '#FFFFFF', kakao: '#FEE500'};
const EMOJI = "'Noto Color Emoji'";
const HAN = `'Black Han Sans', ${EMOJI}, sans-serif`;
const JUA = `'Jua', ${EMOJI}, sans-serif`;
const LILITA = `'Lilita One', ${EMOJI}, sans-serif`;
const POPPINS = `'Poppins', ${EMOJI}, sans-serif`;
const PLAYFAIR = "'Playfair Display', Georgia, serif";
const GRADE = 'contrast(1.1) saturate(1.18) brightness(1.03) sepia(0.04)';

const FONTS: [string, string, string, string][] = [
  ['Black Han Sans', 'normal', '400', 'ea8Aad44WunzF9a-dL6toA8r8nqV.ttf'],
  ['Jua', 'normal', '400', 'co3KmW9ljjAjcw.ttf'],
  ['Lilita One', 'normal', '400', 'i7dPIFZ9Zz-WBtRtedDbUEY.ttf'],
  ['Noto Color Emoji', 'normal', '400', 'Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf'],
  ['Poppins', 'normal', '800', 'pxiByp8kv8JHgFVrLDD4V1s.ttf'],
  ['Poppins', 'normal', '900', 'pxiByp8kv8JHgFVrLBT5V1s.ttf'],
  ['Playfair Display', 'italic', '400', 'nuFRD-vYSZviVYUb_rj3ij__anPXDTnCjmHKM4nYO7KN_qiTbtY.ttf'],
];

const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([f, s, w, file]) => new FontFace(f, `url(${staticFile('fonts/' + file)})`, {style: s, weight: w}).load()
      .then((x) => document.fonts.add(x)))).then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
  }, [h]);
};

// Thick outline that works on any text (ring of hard shadows) + soft drop shadow.
const stroke = (px: number, color = C.ink, drop = true) => {
  const out: string[] = [];
  for (let a = 0; a < 16; a++) out.push(`${(Math.cos(a * Math.PI / 8) * px).toFixed(1)}px ${(Math.sin(a * Math.PI / 8) * px).toFixed(1)}px 0 ${color}`);
  if (drop) out.push(`0 ${px + 4}px ${px * 2}px rgba(0,0,0,.35)`);
  return out.join(',');
};
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

// Bouncy entrance (0 -> overshoot -> 1) and quick exit.
const usePop = (t: number, s: number, e: number, fps: number) => {
  const f = Math.round((t - s) * fps);
  const inS = spring({frame: f, fps, config: {damping: 9, stiffness: 180, mass: 0.6}});
  const out = interpolate(t, [e - 0.15, e], [1, 0], clamp);
  return {scale: inS * interpolate(out, [0, 1], [0.7, 1]), opacity: Math.min(1, inS * 3) * out};
};

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
  }
  return {z, x, y};
};

const Hi: React.FC<{text: string; hi: string; pop: number}> = ({text, hi, pop}) => {
  const i = hi ? text.indexOf(hi) : -1;
  if (i < 0) return <>{text}</>;
  return <>{text.slice(0, i)}<span style={{color: C.yellow, display: 'inline-block', transform: `scale(${pop})`}}>{hi}</span>{text.slice(i + hi.length)}</>;
};

const CaptionV2: React.FC<{c: Caption; t: number; fps: number}> = ({c, t, fps}) => {
  const f = Math.round((t - c.s) * fps);
  const inS = spring({frame: f, fps, config: {damping: 14, stiffness: 220}});
  const hiPop = 1 + 0.18 * spring({frame: f - 3, fps, config: {damping: 7, stiffness: 200}}) - 0.18 * spring({frame: f - 9, fps, config: {damping: 14}});
  const ws = c.words;
  return (
    <div style={{position: 'absolute', left: 50, right: 50, top: 1170, textAlign: 'center', display: 'grid', gap: 16,
      transform: `translateY(${(1 - inS) * 26}px) scale(${interpolate(inS, [0, 1], [0.92, 1])})`, opacity: Math.min(1, inS * 2)}}>
      <div style={{fontFamily: JUA, fontSize: 76, lineHeight: 1.18, color: C.white, textShadow: stroke(7), wordBreak: 'keep-all', textWrap: 'balance' as any}}>
        <Hi text={c.ko} hi={c.hi} pop={hiPop} />
      </div>
      {c.en ? (
        <div style={{fontFamily: POPPINS, fontWeight: 800, fontSize: 40, lineHeight: 1.25, textShadow: stroke(4), textWrap: 'balance' as any}}>
          {ws.length ? ws.map((w, k) => {
            const next = ws[k + 1]?.t ?? c.e;
            const active = w.t !== null && t >= w.t && t < next;
            const said = w.t !== null && t >= w.t;
            return <React.Fragment key={k}>{k ? ' ' : ''}<span style={{display: 'inline-block', padding: '0 0.08em', color: active ? C.yellow : C.white,
              opacity: said ? 1 : 0.55, transform: `scale(${active ? 1.07 : 1}) translateY(${active ? -3 : 0}px)`}}>{w.w}</span></React.Fragment>;
          }) : <span style={{color: C.white, opacity: 0.9}}>{c.en}</span>}
        </div>
      ) : null}
    </div>
  );
};

const Behind: React.FC<{ev: Ev; t: number; fps: number}> = ({ev, t, fps}) => {
  const p = usePop(t, ev.s, ev.e, fps);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: ev.top - 90, textAlign: 'center', opacity: p.opacity,
      transform: `scale(${p.scale}) rotate(-3deg)`, transformOrigin: '50% 70%'}}>
      <div style={{fontFamily: LILITA, fontSize: 70, color: C.white, letterSpacing: '.04em', textShadow: stroke(6)}}>{ev.en}</div>
      <div style={{fontFamily: HAN, fontSize: ev.size, lineHeight: 1, color: C.yellow, textShadow: stroke(12), whiteSpace: 'nowrap'}}>{ev.ko}</div>
    </div>
  );
};

const SLOTS: Record<string, React.CSSProperties & {rot: number}> = {
  tl: {left: 50, top: 420, rot: -6}, tr: {right: 50, top: 420, rot: 6}, center: {left: 0, right: 0, top: 380, rot: -3},
  stack0: {left: 0, right: 0, top: 300, rot: -4}, stack1: {left: 0, right: 0, top: 460, rot: 3}, stack2: {left: 0, right: 0, top: 620, rot: -3},
};
const Pop: React.FC<{ev: Ev; t: number; fps: number}> = ({ev, t, fps}) => {
  const p = usePop(t, ev.s, ev.e, fps);
  const {rot, ...pos} = SLOTS[ev.slot];
  const centered = pos.left === 0 && pos.right === 0;
  const wobble = Math.sin((t - ev.s) * 6) * 1.5;
  return (
    <div style={{position: 'absolute', ...pos, display: 'flex', justifyContent: centered ? 'center' : undefined, opacity: p.opacity}}>
      <div style={{transform: `scale(${p.scale}) rotate(${rot + wobble}deg)`, background: C.yellow, color: C.ink, fontFamily: HAN, fontSize: 74,
        lineHeight: 1, padding: '20px 30px 18px', borderRadius: 26, border: `6px solid ${C.ink}`, boxShadow: `0 10px 0 ${C.ink}, 0 18px 30px rgba(0,0,0,.3)`,
        whiteSpace: 'nowrap'}}>{ev.text}</div>
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
            <span style={{fontFamily: HAN, fontSize: size, color: k === 2 ? C.yellow : C.white, textShadow: stroke(11)}}>{w.w}</span>
          </div>
        );
      })}
    </>
  );
};

const Tag: React.FC<{ev: Ev; t: number; fps: number}> = ({ev, t, fps}) => {
  const p = usePop(t, ev.s, ev.e, fps);
  return (
    <div style={{position: 'absolute', left: 50, top: 400, opacity: p.opacity, transform: `scale(${p.scale}) rotate(-2deg)`, transformOrigin: '0 50%'}}>
      <div style={{background: C.navy, border: `5px solid ${C.yellow}`, borderRadius: 26, padding: '20px 30px', display: 'grid', gap: 8,
        boxShadow: `0 10px 0 ${C.ink}, 0 18px 30px rgba(0,0,0,.3)`}}>
        <span style={{fontFamily: LILITA, fontSize: 62, color: C.white, lineHeight: 1}}>{ev.name} <span style={{fontSize: 52}}>{ev.flags}</span></span>
        <span style={{fontFamily: JUA, fontSize: 34, color: C.yellow, lineHeight: 1.2}}>{ev.role}</span>
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
      <div style={{background: C.yellow, color: C.ink, fontFamily: LILITA, fontSize: 70, lineHeight: 1, padding: '16px 30px 12px', borderRadius: 999,
        border: `6px solid ${C.ink}`, boxShadow: `0 8px 0 ${C.ink}`, whiteSpace: 'nowrap', transform: `rotate(${-3 + Math.sin(t * 3) * 1.5}deg)`}}>🔥 DAY {ev.day}</div>
      <div style={{fontFamily: JUA, fontSize: 38, color: C.white, textShadow: stroke(5), opacity: 1 - shrink, whiteSpace: 'nowrap'}}>출간까지 매일 업로드 📚</div>
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
  const sp = (d: number) => spring({frame: Math.round((t - ev.s - d) * fps), fps, config: {damping: 10, stiffness: 170}});
  const bear = sp(0.2), wm = sp(0.45), stamp = sp(0.75), line = sp(1.0), btn = sp(1.25);
  return (
    <AbsoluteFill style={{background: `rgba(20,32,58,${0.93 * bg})`, display: 'grid', placeContent: 'center', justifyItems: 'center', gap: 30, textAlign: 'center', padding: '0 70px'}}>
      <Img src={staticFile('brand/bear-butterfly.png')} style={{width: 470, transform: `scale(${bear}) translateY(${Math.sin(t * 4) * 8}px)`}} />
      <Img src={staticFile('brand/wordmark-cream.png')} style={{width: 820, opacity: wm, transform: `translateY(${(1 - wm) * 30}px)`}} />
      <div style={{background: C.yellow, color: C.ink, fontFamily: LILITA, fontSize: 64, padding: '12px 30px 8px', borderRadius: 18, border: `6px solid ${C.ink}`,
        transform: `scale(${stamp}) rotate(-5deg)`, boxShadow: `0 8px 0 ${C.ink}`}}>DAY {day} ✅</div>
      <div style={{fontFamily: JUA, fontSize: 54, color: C.white, lineHeight: 1.35, opacity: line, transform: `translateY(${(1 - line) * 20}px)`}}>
        내일 DAY {day + 1}에서 만나요! 👋<br /><span style={{fontSize: 40, color: C.yellow}}>팔로우하고 출간까지 함께해요 📚</span>
      </div>
      <div style={{fontFamily: JUA, fontSize: 42, background: C.kakao, color: '#191600', padding: '22px 44px 18px', borderRadius: 999, transform: `scale(${btn})`}}>카카오톡 채널 추가하기</div>
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
  const dir = `confidence/${plan.name}`;
  const E = (type: string) => plan.events.filter((e) => e.type === type);
  const end = E('end')[0];
  const live = (e: Ev, pad = 0.2) => t >= e.s - 0.05 && t <= e.e + pad;
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const camStyle: React.CSSProperties = {position: 'absolute', inset: 0, transform: `translate(${cam.x}px, ${cam.y}px) scale(${cam.z})`, transformOrigin: '50% 36%'};
  const vid: React.CSSProperties = {width: '100%', height: '100%', objectFit: 'cover', filter: GRADE};
  return (
    <AbsoluteFill style={{background: C.navy}}>
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
      {E('tag').map((ev, k) => (live(ev) ? <Tag key={k} ev={ev} t={t} fps={fps} /> : null))}
      {E('pop').map((ev, k) => (live(ev) ? <Pop key={k} ev={ev} t={t} fps={fps} /> : null))}
      {E('demo').map((ev, k) => (live(ev, 0.4) ? <Demo key={k} ev={ev} t={t} fps={fps} /> : null))}
      {cap && !cap.demo && t < end.s ? <CaptionV2 c={cap} t={t} fps={fps} /> : null}
      {E('badge').map((ev, k) => (t <= ev.e ? <Badge key={k} ev={ev} t={t} fps={fps} /> : null))}
      {t >= end.s ? <EndV2 ev={end} t={t} fps={fps} day={plan.day} /> : null}
      <Progress t={t} total={plan.duration} />
    </AbsoluteFill>
  );
};
