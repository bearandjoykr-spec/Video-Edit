// The Bear & Joy Co. — landscape class video template (YouTube, 16:9), rebuilt from the Day 6 "Silly English" style.
// Spec: docs/class-video-style.md. Brand: brand/BRAND.md (Pretendard, Butter Yellow #F6F0BA, Sky Blue #AECCE6, Ink #14203A).
// Composition is 1920×1080; render 4K with --scale=2.
// Plans are written by projects/<project>/build_class.py → versions/<v>/timeline_class.json.
import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill, Img, OffthreadVideo, continueRender, delayRender, interpolate,
  staticFile, useCurrentFrame, Sequence, useVideoConfig, Easing, spring,
} from 'remotion';

type W = {w: string; t: number | null};
type Caption = {s: number; e: number; ko: string; hi?: string; en?: string; speaker?: 'mark' | 'joy'};
type Box = {left?: number; right?: number; top?: number; bottom?: number; scale?: number};
type Ev = {type: string; s: number; e: number; [k: string]: any};
export type ClassPlan = {
  name: string; fps: number; duration: number; frames: number; day: number;
  title: {en: string; ko: string; series?: string};
  media?: string; // folder under public/ holding cut.mov; omitted = placeholder background (layout previews)
  cardSide?: 'left' | 'right' | 'center'; // where phrase/title cards sit (the side away from the speaker)
  captionBottom?: number;
  watermark?: boolean; // false when the footage already carries the logo
  card?: Box; // default phrase-card box; a phrase event may override with `at`
  turn?: Box; // where the Your-turn chip sits
  titleBacking?: boolean;
  titleAt?: Box; // where the opening title card sits
  mediaDuration?: number; // seconds of footage; end cards may run past it
  scrims?: {s: number; e: number}[]; // soft dark gradient behind captions (light clothing)
  captions: Caption[]; events: Ev[]; zooms?: {t: number; z: number; x?: number; y?: number}[];
};

const C = {navy: '#1E2D4D', ink: '#14203A', yellow: '#F6F0BA', blue: '#AECCE6', white: '#FFFFFF', cream: '#F5F0E6', kakao: '#FEE500'};
const EMOJI = "'Noto Color Emoji'";
const PRE = `'Pretendard', ${EMOJI}, 'Noto Sans KR', sans-serif`;
const GRADE = 'contrast(1.05) saturate(1.08) brightness(1.02)'; // calmer than Reels: this is a class

const FONTS: [string, string, string, string][] = [
  ['Pretendard', 'normal', '600', 'Pretendard-SemiBold.woff2'],
  ['Pretendard', 'normal', '700', 'Pretendard-Bold.woff2'],
  ['Pretendard', 'normal', '800', 'Pretendard-ExtraBold.woff2'],
  ['Pretendard', 'normal', '900', 'Pretendard-Black.woff2'],
  ['Noto Color Emoji', 'normal', '400', 'Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([f, s, w, file]) => new FontFace(f, `url(${staticFile('fonts/' + file)})`, {style: s, weight: w}).load()
      .then((x) => document.fonts.add(x)))).then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
  }, [h]);
};

const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const soft = (px: number) => `0 ${px / 3}px ${px}px rgba(10,16,30,.55), 0 ${px / 2}px ${px * 3}px rgba(10,16,30,.3)`;
const chipShadow = '0 14px 36px rgba(10,16,30,.28)';

// Fade and rise in (16 px), fade out — the calm class entrance. `pop` adds a gentle spring scale.
const enter = (t: number, s: number, e: number, fps: number, pop = false) => {
  const a = interpolate(t, [s, s + 0.35, e - 0.3, e], [0, 1, 1, 0], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const sc = pop ? spring({frame: Math.round((t - s) * fps), fps, config: {damping: 12, stiffness: 170}}) : 1;
  return {opacity: a, y: (1 - Math.min(1, (t - s) / 0.35)) * 16, scale: interpolate(sc, [0, 1], [0.9, 1])};
};
const pulse = (t: number, times: number[] = []) =>
  times.reduce((m, p) => Math.max(m, interpolate(t, [p - 0.05, p + 0.08, p + 0.45], [0, 1, 0], clamp)), 0);

// ---------- camera: gentle 100% / 104% jump framing --------------------------------------------
const cameraAt = (plan: ClassPlan, t: number) => {
  let cur = {z: 1, x: 0, y: 0}, prev = cur, since = 99;
  for (const k of plan.zooms ?? []) if (k.t <= t + 1e-6) { prev = cur; cur = {z: k.z, x: k.x ?? 0, y: k.y ?? 0}; since = t - k.t; }
  const a = interpolate(since, [0, 0.25], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  return {z: prev.z + (cur.z - prev.z) * a, x: prev.x + (cur.x - prev.x) * a, y: prev.y + (cur.y - prev.y) * a};
};

// ---------- opening title card beside Mark ------------------------------------------------------
const TitleCard: React.FC<{ev: Ev; plan: ClassPlan; t: number; fps: number}> = ({ev, plan, t, fps}) => {
  const p = enter(t, ev.s, ev.e, fps, true);
  const side = plan.cardSide ?? 'right';
  const b = plan.titleAt;
  const at: React.CSSProperties = b ? {top: b.top ?? 200, left: b.left, right: b.right} : {top: 200, [side === 'left' ? 'left' : 'right']: 110};
  return (
    <div style={{position: 'absolute', ...at, width: 760, opacity: p.opacity, transformOrigin: b?.left !== undefined ? '0 0' : '100% 0',
      transform: `translateY(${p.y}px) scale(${p.scale * (b?.scale ?? 1)})`, display: 'grid', gap: 18, justifyItems: 'start',
      ...(plan.titleBacking ? {background: 'rgba(20,32,58,.74)', borderRadius: 34, padding: '34px 44px', boxShadow: '0 20px 50px rgba(10,16,30,.35)'} : {})}}>
      <div style={{background: C.yellow, color: C.ink, fontFamily: PRE, fontWeight: 900, fontSize: 52, padding: '12px 30px', borderRadius: 999,
        boxShadow: chipShadow}}>DAY {plan.day}</div>
      <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 36, color: C.white, textShadow: soft(8)}}>{plan.title.series ?? 'Bear & Joy First Steps'}</div>
      <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 112, lineHeight: 1, letterSpacing: '-0.03em', color: C.yellow, textShadow: soft(14)}}>{plan.title.en}</div>
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 64, lineHeight: 1.1, color: C.blue, textShadow: soft(12), wordBreak: 'keep-all'}}>{plan.title.ko}</div>
    </div>
  );
};

// ---------- phrase card: English (lights up, stress, flow, intonation) / pronunciation pill / meaning
type Stress = {word: number; part: string; pron?: string; pulses?: number[]};
const StressedWord: React.FC<{w: string; st?: Stress; pul: number; on: boolean; tiny: number}> = ({w, st, pul, on, tiny}) => {
  const base: React.CSSProperties = {color: on ? C.blue : C.white, transition: 'none'};
  if (!st) return <span style={base}>{w}</span>;
  const i = w.toLowerCase().indexOf(st.part.toLowerCase());
  if (i < 0) return <span style={base}>{w}</span>;
  return (
    <span style={base}>{w.slice(0, i)}
      <span style={{display: 'inline-block', color: C.yellow, fontSize: '1.22em', margin: '0 0.03em', transform: `scale(${1 + 0.14 * pul})`, transformOrigin: '50% 80%',
        lineHeight: 0.9}}>{w.slice(i, i + st.part.length).toUpperCase()}</span>{w.slice(i + st.part.length)}
    </span>
  );
};

const FlowArc: React.FC = () => (
  <svg width="64" height="34" viewBox="0 0 64 34" style={{position: 'absolute', left: -32, bottom: -30}}>
    <path d="M4 6 Q32 34 60 6" fill="none" stroke={C.yellow} strokeWidth="6" strokeLinecap="round" />
  </svg>
);

const ToneArrow: React.FC<{dir: 'up' | 'down'; draw: number}> = ({dir, draw}) => (
  <svg width="110" height="90" viewBox="0 0 110 90" style={{marginLeft: 12, overflow: 'visible'}}>
    <path d={dir === 'up' ? 'M8 78 Q60 74 92 18' : 'M8 18 Q60 22 92 78'} fill="none" stroke={C.blue} strokeWidth="9" strokeLinecap="round"
      pathLength={1} strokeDasharray="1" strokeDashoffset={1 - draw} />
    <path d={dir === 'up' ? 'M70 16 L94 14 L96 40' : 'M70 80 L94 82 L96 56'} fill="none" stroke={C.blue} strokeWidth="9" strokeLinecap="round"
      strokeLinejoin="round" opacity={draw > 0.9 ? 1 : 0} />
  </svg>
);

const PhraseCard: React.FC<{ev: Ev; plan: ClassPlan; t: number; fps: number; low: number}> = ({ev, plan, t, fps, low}) => {
  const p = enter(t, ev.s, ev.e, fps, true);
  const words: W[] = ev.words ?? ev.en.split(' ').map((w: string) => ({w, t: null}));
  const stress: Stress[] = ev.stress ?? [];
  const flow: number[][] = ev.flow ?? [];
  const tiny = ev.voice?.kind === 'tiny' ? interpolate(t, [ev.voice.s, ev.voice.s + 0.3, ev.voice.e, ev.voice.e + 0.3], [1, 0.55, 0.55, 1], clamp) : 1;
  const big = ev.voice?.kind === 'big' ? interpolate(t, [ev.voice.s, ev.voice.s + 0.2, ev.voice.e, ev.voice.e + 0.3], [1, 1.18, 1.18, 1], clamp) : 1;
  const side = plan.cardSide ?? 'right';
  const box: Box | undefined = ev.at ?? plan.card;
  const pos: React.CSSProperties = box ? {left: box.left, right: box.right, top: box.top, bottom: box.top === undefined ? (box.bottom ?? low) : undefined}
    : side === 'center' ? {left: 0, right: 0, display: 'flex', justifyContent: 'center', bottom: low}
    : side === 'left' ? {left: 80, bottom: low} : {right: 80, bottom: low};
  const k = box?.scale ?? 1;
  const origin = box ? `${box.left !== undefined ? 0 : 100}% ${box.top !== undefined ? 0 : 100}%` : '50% 100%';
  const tone = ev.tone as {dir: 'up' | 'down'; at?: number; why?: string} | undefined;
  const toneDraw = tone ? interpolate(t, [(tone.at ?? ev.s + 0.6), (tone.at ?? ev.s + 0.6) + 0.45], [0, 1], clamp) : 0;
  const pronStress = stress.find((s) => s.pron);
  const pronPulse = pronStress ? pulse(t, pronStress.pulses) : 0;
  const pron: string = ev.pron ?? '';
  const pi = pronStress ? pron.indexOf(pronStress.pron!) : -1;
  return (
    <div style={{position: 'absolute', ...pos, opacity: p.opacity, transform: `translateY(${p.y}px)`}}>
      <div style={{transform: `scale(${p.scale * k})`, transformOrigin: origin, background: 'rgba(20,32,58,.72)', borderRadius: 34, padding: '30px 50px 34px',
        boxShadow: '0 20px 50px rgba(10,16,30,.35)', display: 'grid', justifyItems: 'center', gap: 16, minWidth: 760, maxWidth: 1500}}>
        {ev.n ? <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 28, color: C.yellow, letterSpacing: '0.08em'}}>PHRASE {ev.n}</div> : null}
        <div style={{display: 'flex', alignItems: 'center', fontFamily: PRE, fontWeight: 900, fontSize: 96, lineHeight: 1.05, letterSpacing: '-0.02em',
          textShadow: soft(10), transform: `scale(${tiny * big})`, whiteSpace: 'nowrap'}}>
          {words.map((w, k) => {
            // `reps`: the phrase is said several times; word times are offsets from each repetition's start
            const reps: number[] | undefined = ev.reps;
            const r0 = reps ? reps.filter((r) => r <= t).pop() : undefined;
            const lt = reps ? (r0 === undefined ? -1 : t - r0) : t;
            const wt = w.t, nt = words[k + 1]?.t ?? (reps ? (words[words.length - 1].t ?? 0) + 0.7 : ev.e);
            const on = wt !== null && lt >= wt && lt < nt + 0.15;
            const st = stress.find((s) => s.word === k);
            const flowsIn = flow.some(([a, b]) => b === k && a === k - 1);
            return (
              <span key={k} style={{position: 'relative', display: 'inline-block', marginLeft: k ? (flowsIn ? 14 : 26) : 0,
                transform: `translateY(${on ? -4 : 0}px)`}}>
                {flowsIn ? <FlowArc /> : null}
                <StressedWord w={w.w} st={st} pul={st ? pulse(t, st.pulses) : 0} on={on} tiny={tiny} />
              </span>
            );
          })}
          {tone ? <ToneArrow dir={tone.dir} draw={toneDraw} /> : null}
        </div>
        <div style={{background: C.blue, color: C.ink, fontFamily: PRE, fontWeight: 800, fontSize: 50, padding: '10px 34px', borderRadius: 999}}>
          {pi < 0 ? pron : <>{pron.slice(0, pi)}<span style={{display: 'inline-block', background: C.yellow, borderRadius: 14, padding: '0 8px',
            transform: `scale(${1 + 0.12 * pronPulse})`}}>{pronStress!.pron}</span>{pron.slice(pi + pronStress!.pron!.length)}</>}
        </div>
        <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 54, color: C.white, textShadow: soft(8), wordBreak: 'keep-all'}}>{ev.ko}</div>
        {tone?.why ? <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 32, color: C.blue, opacity: toneDraw}}>{tone.dir === 'up' ? '↗' : '↘'} {tone.why}</div> : null}
        {ev.note ? <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 32, color: C.yellow}}>{ev.note}</div> : null}
      </div>
    </div>
  );
};

// ---------- "Your turn": yellow chip + bar counting down the pause ------------------------------
const YourTurn: React.FC<{ev: Ev; t: number; fps: number; box?: Box}> = ({ev, t, fps, box}) => {
  const p = enter(t, ev.s - 0.1, ev.e + 0.25, fps, true);
  const left = interpolate(t, [ev.s, ev.e], [1, 0], clamp);
  const secs = Math.max(1, Math.ceil(ev.e - t));
  return (
    <div style={box ? {position: 'absolute', top: box.top, left: box.left, right: box.right, opacity: p.opacity}
      : {position: 'absolute', top: 70, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: p.opacity}}>
      <div style={{transform: `scale(${p.scale * (box?.scale ?? 1)})`, transformOrigin: box ? `${box.left !== undefined ? 0 : 100}% 0` : '50% 0',
        display: 'grid', justifyItems: 'center', gap: 14}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 22, background: C.yellow, color: C.ink, fontFamily: PRE, fontWeight: 900, fontSize: 60,
          padding: '16px 40px', borderRadius: 999, boxShadow: chipShadow}}>
          <span>🗣️ Your turn!</span><span style={{fontWeight: 800, fontSize: 40}}>{ev.ko ?? '따라 해보세요'}</span>
          <span style={{background: C.ink, color: C.yellow, borderRadius: 999, width: 70, height: 70, display: 'grid', placeItems: 'center', fontSize: 44}}>{secs}</span>
        </div>
        <div style={{width: 560, height: 16, borderRadius: 999, background: 'rgba(20,32,58,.45)', overflow: 'hidden'}}>
          <div style={{width: `${left * 100}%`, height: '100%', background: C.yellow, borderRadius: 999}} />
        </div>
      </div>
    </div>
  );
};

// ---------- captions: Korean (one yellow word), optional small English above --------------------
const ClassCaption: React.FC<{c: Caption; t: number; fps: number; bottom: number}> = ({c, t, fps, bottom}) => {
  const a = interpolate(t, [c.s, c.s + 0.18, c.e - 0.12, c.e], [0, 1, 1, 0], clamp);
  const i = c.hi ? c.ko.indexOf(c.hi) : -1;
  return (
    <div style={{position: 'absolute', left: 120, right: 120, bottom, textAlign: 'center', opacity: a, display: 'grid', gap: 6}}>
      {c.en ? <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 34, color: c.speaker === 'joy' ? C.yellow : C.white, opacity: 0.92, textShadow: soft(6)}}>{c.en}</div> : null}
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 56, lineHeight: 1.25, color: C.white, textShadow: soft(8), wordBreak: 'keep-all',
        textWrap: 'balance' as any}}>
        {i < 0 ? c.ko : <>{c.ko.slice(0, i)}<span style={{color: C.yellow}}>{c.hi}</span>{c.ko.slice(i + c.hi!.length)}</>}
      </div>
    </div>
  );
};

// ---------- Joy's playful voice cards -----------------------------------------------------------
const VOICE: Record<string, {emoji: string; color: string}> = {
  robot: {emoji: '🤖', color: C.blue}, sleepy: {emoji: '💤', color: C.blue}, sing: {emoji: '🎵', color: C.yellow},
  tiny: {emoji: '🐭', color: C.yellow}, big: {emoji: '🐻', color: C.yellow}, joke: {emoji: '😆', color: C.yellow},
  tada: {emoji: '🎉', color: C.yellow}, butterfly: {emoji: '🦋', color: C.blue}, snail: {emoji: '🐌', color: C.yellow}, look: {emoji: '🔍', color: C.blue},
};
const VoiceCard: React.FC<{ev: Ev; t: number; fps: number}> = ({ev, t, fps}) => {
  const p = enter(t, ev.s, ev.e, fps, true);
  const v = VOICE[ev.kind] ?? VOICE.joke;
  const words: string[] = (ev.text as string).split(' ');
  const lt = t - ev.s;
  return (
    <div style={{position: 'absolute', top: ev.top ?? 150, [ev.side === 'left' ? 'left' : 'right']: 90, opacity: p.opacity,
      transform: `translateY(${p.y}px) scale(${p.scale}) rotate(${ev.side === 'left' ? -3 : 3}deg)`}}>
      <div style={{display: 'grid', justifyItems: 'center', gap: 6, textAlign: 'center',
        ...(ev.backing !== false ? {background: 'rgba(20,32,58,.62)', borderRadius: 30, padding: '18px 34px 22px', boxShadow: chipShadow} : {})}}>
        {ev.label ? <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 30, background: C.white, color: C.ink, padding: '6px 18px', borderRadius: 999}}>{ev.label}</div> : null}
        <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 92, lineHeight: 1.05, color: v.color, textShadow: soft(12), whiteSpace: 'nowrap'}}>
          {words.map((w, k) => {
            let tr = '';
            if (ev.kind === 'robot') tr = `translate(${Math.round(Math.sin(Math.floor(lt * 6) + k * 2) * 6)}px, ${Math.round(Math.cos(Math.floor(lt * 6) + k) * 5)}px)`;
            if (ev.kind === 'sleepy') tr = `translateY(${Math.min(28, lt * 10) * (k + 1) / words.length}px) rotate(${Math.min(10, lt * 4) * (k % 2 ? 1 : -1)}deg)`;
            if (ev.kind === 'sing') tr = `translateY(${Math.sin(lt * 5 + k) * 10}px)`;
            if (ev.kind === 'butterfly') tr = `translate(${Math.sin(lt * 3 + k) * 8}px, ${Math.cos(lt * 4 + k) * 10}px)`;
            if (ev.kind === 'snail') tr = `translateX(${Math.min(30, lt * 8)}px)`;
            if (ev.kind === 'tada') tr = `scale(${1 + 0.08 * Math.sin(lt * 10) * Math.exp(-lt * 1.5)})`;
            if (ev.kind === 'tiny') tr = `scale(${interpolate(lt, [0, 0.6], [1, 0.6], clamp)})`;
            return <span key={k} style={{display: 'inline-block', marginLeft: k ? 22 : 0, transform: tr}}>{w}</span>;
          })}
          <span style={{marginLeft: 16, display: 'inline-block', transform: `translateY(${Math.sin(lt * 4) * 6}px)`}}>{v.emoji}</span>
        </div>
        {ev.ko ? <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 44, color: C.white, textShadow: soft(8)}}>{ev.ko}</div> : null}
      </div>
    </div>
  );
};

// Key message card (e.g. "Don't correct pronunciation, respond to the child").
const MessageCard: React.FC<{ev: Ev; t: number; fps: number}> = ({ev, t, fps}) => {
  const p = enter(t, ev.s, ev.e, fps, true);
  return (
    <div style={ev.left !== undefined ? {position: 'absolute', top: ev.top ?? 110, left: ev.left, width: ev.width ?? 800, opacity: p.opacity}
      : {position: 'absolute', top: ev.top ?? 110, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: p.opacity}}>
      <div style={{transform: `translateY(${p.y}px) scale(${p.scale})`, background: C.yellow, borderRadius: 34, padding: '28px 56px', maxWidth: ev.width ?? 1400,
        boxShadow: chipShadow, textAlign: 'center', display: 'grid', gap: 10}}>
        {ev.kicker ? <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 32, color: C.ink, opacity: 0.7}}>{ev.kicker}</div> : null}
        <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 66, lineHeight: 1.15, color: C.ink, wordBreak: 'keep-all', whiteSpace: 'pre-line'}}>{ev.ko}</div>
        {ev.en ? <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 36, color: C.ink, opacity: 0.8}}>{ev.en}</div> : null}
      </div>
    </div>
  );
};

// Small label (speaker name, section) — kept to a corner, away from worksheets.
const Label: React.FC<{ev: Ev; t: number; fps: number}> = ({ev, t, fps}) => {
  const p = enter(t, ev.s, ev.e, fps);
  const corner: React.CSSProperties = {tl: {left: 60, top: 150}, tr: {right: 60, top: 110}, bl: {left: 60, bottom: 60}, br: {right: 60, bottom: 60}}[ev.pos as string ?? 'tl'] ?? {left: 60, top: 60};
  return (
    <div style={{position: 'absolute', ...corner, opacity: p.opacity, transform: `translateY(${p.y}px)`, background: 'rgba(20,32,58,.66)', borderRadius: 22,
      padding: '12px 24px', display: 'grid', gap: 2}}>
      <span style={{fontFamily: PRE, fontWeight: 900, fontSize: 40, color: C.yellow}}>{ev.text}</span>
      {ev.sub ? <span style={{fontFamily: PRE, fontWeight: 600, fontSize: 26, color: C.white}}>{ev.sub}</span> : null}
    </div>
  );
};

// Mark as a picture: always brand/assets/mark-photo.jpg via mark-avatar.png (BRAND.md · People).
const MarkAvatar: React.FC<{ev: Ev; t: number; fps: number}> = ({ev, t, fps}) => {
  const p = enter(t, ev.s, ev.e, fps, true);
  return (
    <div style={{position: 'absolute', top: ev.top ?? 80, [ev.side === 'left' ? 'left' : 'right']: 80, opacity: p.opacity, display: 'flex', alignItems: 'center', gap: 20,
      transform: `translateY(${p.y}px) scale(${p.scale})`}}>
      <Img src={staticFile('brand/mark-avatar.png')} style={{width: 190, height: 190, filter: 'drop-shadow(0 10px 22px rgba(0,0,0,.3))'}} />
      <div style={{display: 'grid', gap: 2}}>
        <span style={{fontFamily: PRE, fontWeight: 700, fontSize: 32, color: C.white, textShadow: soft(8)}}>{ev.kicker ?? 'Mark · 마크 선생님'}</span>
        {ev.text ? <span style={{fontFamily: PRE, fontWeight: 900, fontSize: 56, color: C.blue, textShadow: soft(10)}}>{ev.text}</span> : null}
      </div>
    </div>
  );
};

// ---------- ending: recap of the day's phrases, then the logo card ------------------------------
const Recap: React.FC<{ev: Ev; plan: ClassPlan; t: number; fps: number}> = ({ev, plan, t, fps}) => {
  const bg = interpolate(t, [ev.s, ev.s + 0.5, ev.e - 0.4, ev.e], [0, 1, 1, 0], clamp);
  const rows: {en: string; pron: string; ko: string}[] = ev.phrases;
  return (
    <AbsoluteFill style={{background: `rgba(30,45,77,${bg})`, display: 'grid', placeContent: 'center', justifyItems: 'center', gap: 26, opacity: Math.min(1, bg * 1.4)}}>
      <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 44, background: C.yellow, color: C.ink, padding: '10px 30px', borderRadius: 999}}>DAY {plan.day} · 오늘의 표현</div>
      {rows.map((r, k) => {
        const a = spring({frame: Math.round((t - ev.s - 0.4 - k * 0.35) * fps), fps, config: {damping: 14, stiffness: 150}});
        return (
          <div key={k} style={{display: 'grid', gridTemplateColumns: '720px 520px 460px', alignItems: 'center', gap: 30, opacity: a,
            transform: `translateY(${(1 - a) * 16}px)`, background: 'rgba(255,255,255,.06)', borderRadius: 26, padding: '18px 34px'}}>
            <span style={{fontFamily: PRE, fontWeight: 900, fontSize: 60, color: k % 2 ? C.blue : C.yellow, whiteSpace: 'nowrap'}}>{r.en}</span>
            <span style={{justifySelf: 'start', background: C.blue, color: C.ink, fontFamily: PRE, fontWeight: 800, fontSize: 38, padding: '6px 24px', borderRadius: 999}}>{r.pron}</span>
            <span style={{fontFamily: PRE, fontWeight: 800, fontSize: 44, color: C.white}}>{r.ko}</span>
          </div>
        );
      })}
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 44, color: C.white, marginTop: 20}}>{ev.next ?? `다음 시간: DAY ${plan.day + 1} 👋`}</div>
    </AbsoluteFill>
  );
};

const LogoCard: React.FC<{ev: Ev; t: number}> = ({ev, t}) => {
  const a = interpolate(t, [ev.s, ev.s + 0.6], [0, 1], clamp);
  const art = interpolate(t, [ev.s + 0.2, ev.s + 1.2], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const word = interpolate(t, [ev.s + 0.9, ev.s + 1.7], [0, 1], clamp);
  const line = interpolate(t, [ev.s + 1.6, ev.s + 2.4], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: C.navy, opacity: a, display: 'grid', placeContent: 'center', justifyItems: 'center', gap: 30}}>
      <Img src={staticFile('brand/bear-butterfly.png')} style={{width: 360, opacity: art, transform: `translateY(${(1 - art) * 30 + Math.sin(t * 1.6) * 6}px)`}} />
      <Img src={staticFile('brand/wordmark-cream.png')} style={{width: 760, opacity: word}} />
      <div style={{fontFamily: PRE, fontWeight: 800, fontSize: 46, color: C.cream, opacity: line}}>{ev.ko ?? '오늘도 아이와 함께 한 걸음 🐾'}</div>
      <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 30, background: C.kakao, color: '#191600', padding: '14px 32px', borderRadius: 999, opacity: line}}>카카오톡 채널 추가하기</div>
    </AbsoluteFill>
  );
};

const DayPill: React.FC<{plan: ClassPlan; t: number; from: number}> = ({plan, t, from}) => (
  <div style={{position: 'absolute', top: 44, right: 54, opacity: 0.92 * interpolate(t, [from, from + 0.5], [0, 1], clamp), background: 'rgba(20,32,58,.55)',
    borderRadius: 999, padding: '8px 22px', fontFamily: PRE, fontWeight: 800, fontSize: 28, color: C.yellow}}>DAY {plan.day} · {plan.title.en}</div>
);

const Placeholder: React.FC = () => (
  <AbsoluteFill style={{background: 'linear-gradient(160deg, #8fa7b8 0%, #c9b9a0 60%, #a08c78 100%)'}}>
    <div style={{position: 'absolute', left: 560, top: 180, width: 800, height: 900, borderRadius: '400px 400px 0 0', background: 'rgba(30,45,77,.35)'}} />
    <div style={{position: 'absolute', left: 0, right: 0, top: 40, textAlign: 'center', fontFamily: PRE, fontWeight: 700, fontSize: 28, color: 'rgba(255,255,255,.7)'}}>
      LAYOUT PREVIEW — footage goes here
    </div>
  </AbsoluteFill>
);

export const BearJoyClass: React.FC<{plan: ClassPlan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const cam = cameraAt(plan, t);
  const E = (type: string) => plan.events.filter((e) => e.type === type);
  const live = (e: Ev, pad = 0.4) => t >= e.s - 0.1 && t <= e.e + pad;
  const title = E('title')[0];
  const phrase = E('phrase').find((e) => live(e, 0));
  const capBottom = plan.captionBottom ?? 60;
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const fullCard = [...E('recap'), ...E('logo')].some((e) => t >= e.s + 0.5 && t <= e.e);
  return (
    <AbsoluteFill style={{background: C.navy}}>
      <AbsoluteFill style={{transform: `translate(${cam.x}px, ${cam.y}px) scale(${cam.z})`, transformOrigin: '50% 40%'}}>
        {plan.media ? (
          <Sequence durationInFrames={Math.floor((plan.mediaDuration ?? plan.duration) * fps)} layout="none">
            <OffthreadVideo src={staticFile(`${plan.media}/cut.mov`)} muted style={{width: '100%', height: '100%', objectFit: 'cover', filter: GRADE}} />
          </Sequence>
        ) : <Placeholder />}
      </AbsoluteFill>
      {(plan.scrims ?? []).map((r, k) => (t >= r.s - 0.5 && t <= r.e + 0.5 ? <AbsoluteFill key={`sc${k}`} style={{opacity: interpolate(t, [r.s - 0.5, r.s, r.e, r.e + 0.5], [0, 1, 1, 0], clamp),
        background: 'linear-gradient(180deg, rgba(10,16,30,0) 72%, rgba(10,16,30,.38) 86%, rgba(10,16,30,.5) 100%)'}} /> : null))}
      {!fullCard ? (
        <>
          {plan.watermark !== false ? <Img src={staticFile('brand/bear-butterfly.png')} style={{position: 'absolute', top: 34, left: 44, width: 96, opacity: 0.6}} /> : null}
          {title && t > title.e ? <DayPill plan={plan} t={t} from={title.e} /> : null}
          {title && live(title) ? <TitleCard ev={title} plan={plan} t={t} fps={fps} /> : null}
          {E('label').map((ev, k) => (live(ev) ? <Label key={k} ev={ev} t={t} fps={fps} /> : null))}
          {E('avatar').map((ev, k) => (live(ev) ? <MarkAvatar key={k} ev={ev} t={t} fps={fps} /> : null))}
          {E('voice').map((ev, k) => (live(ev) ? <VoiceCard key={k} ev={ev} t={t} fps={fps} /> : null))}
          {E('message').map((ev, k) => (live(ev) ? <MessageCard key={k} ev={ev} t={t} fps={fps} /> : null))}
          {E('phrase').map((ev, k) => (live(ev) ? <PhraseCard key={k} ev={ev} plan={plan} t={t} fps={fps} low={cap ? capBottom + 120 : 60} /> : null))}
          {E('yourturn').map((ev, k) => (live(ev) ? <YourTurn key={k} ev={ev} t={t} fps={fps} box={ev.at ?? plan.turn} /> : null))}
          {cap ? <ClassCaption c={cap} t={t} fps={fps} bottom={capBottom} /> : null}
        </>
      ) : null}
      {E('recap').map((ev, k) => (live(ev, 0) ? <Recap key={k} ev={ev} plan={plan} t={t} fps={fps} /> : null))}
      {E('logo').map((ev, k) => (live(ev, 0) ? <LogoCard key={k} ev={ev} t={t} /> : null))}
    </AbsoluteFill>
  );
};
