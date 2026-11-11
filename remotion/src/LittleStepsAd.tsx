// Little Steps Day 1 ad (Joy, 11 Nov 2026): Mark says a phrase, Joy plays it in the peekaboo-window game.
// Ad look, not the Reels brand look (Joy: "clean, like an ad"): white page, black Pretendard headline with a yellow marker,
// the landscape class footage in a rounded 4:5 card that pans to follow the action, speaker badges, white end card.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, OffthreadVideo, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';

type Head = {kicker: string; big: string; ko: string; step?: number; words: number[]};
type Shot = {who: 'mark' | 'joy'; src_s: number; src_e: number; out_s: number; out_e: number; cx0: number; cx1: number; head: Head; hook: boolean; mirror?: boolean};
export type AdPlan = {fps: number; duration: number; frames: number; speechEnd: number; shots: Shot[]; caps: {s: number; e: number; ko: string}[]; media: string; theme?: 'cream' | 'oxford'};

const FF = "'Pretendard', 'Noto Color Emoji', sans-serif";
// Page themes. Mark (11 Nov 2026): not white, use our cream. Joy also asked to see Oxford blue.
const THEMES = {
  cream: {page: '#F5F0E6', glow: '#FAEEDF', ink: '#1E2D4D', sub: '#55607A', step: '#3A6EA5', mark: '#FFE14D', chip: '#EAE1D0', dot: '#D8CFBE', btn: '#1E2D4D', btnOn: '#2C3E66', btnText: '#FFFFFF', logo: 'full'},
  oxford: {page: '#002147', glow: '#0B3166', ink: '#F5F0E6', sub: '#C3CEE0', step: '#AECCE6', mark: '#C9A84C', chip: 'rgba(255,255,255,.12)', dot: '#2A4470', btn: '#F5F0E6', btnOn: '#FFFFFF', btnText: '#002147', logo: 'cream'},
};
let T = THEMES.cream;
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const CARD = {x: 40, y: 470, w: 1000, h: 1250};
const K = CARD.h / 1080; // source px -> card px

const FONTS: [string, string, string, string][] = [
  ['Pretendard', 'normal', '700', 'Pretendard-Bold.woff2'],
  ['Pretendard', 'normal', '800', 'Pretendard-ExtraBold.woff2'],
  ['Pretendard', 'normal', '900', 'Pretendard-Black.woff2'],
  ['Noto Color Emoji', 'normal', '400', 'Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf'],
  ['Playfair Display', 'italic', '600', 'nuFRD-vYSZviVYUb_rj3ij__anPXDTnCjmHKM4nYO7KN_naUbtY.ttf'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([fam, style, w, file]) => new FontFace(fam, `url(${staticFile('fonts/' + file)})`, {style, weight: w}).load().then((x) => document.fonts.add(x))))
      .then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
  }, [h]);
};

const Header: React.FC<{sh: Shot; t: number; fps: number; first: boolean}> = ({sh, t, fps, first}) => {
  const h = sh.head;
  // the headline pops in when it changes; a Mark/Joy pair shares one phrase, so Joy's shot keeps it still
  const k = first ? spring({frame: Math.round((t - sh.out_s) * fps), fps, config: {damping: 11, stiffness: 190, mass: .6}}) : 1;
  const words = h.big.split(' ');
  const size = sh.hook ? 124 : h.big.length > 16 ? 104 : 116;
  return (
    <div style={{position: 'absolute', left: 50, right: 50, top: 150, height: 300, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', alignItems: 'center',
      fontFamily: FF, textAlign: 'center', transform: `translateY(${(1 - k) * 40}px) scale(${0.9 + 0.1 * k})`, opacity: Math.min(1, k * 2)}}>
      {h.kicker ? <div style={{fontWeight: 800, fontSize: h.step ? 40 : 50, letterSpacing: h.step ? '.12em' : '-.01em', color: h.step ? T.step : T.sub, marginBottom: 12}}>
        {h.step ? <>PHRASE <span style={{color: T.ink}}>{h.step}</span> / 3</> : h.kicker}</div> : null}
      <div style={{fontWeight: 900, fontSize: size, lineHeight: 1.05, letterSpacing: '-.035em', color: T.ink, whiteSpace: 'nowrap'}}>
        {words.map((w, i) => {
          const at = h.words[i];
          const lit = at === undefined ? (h.words.length ? 0 : 1) : interpolate(t, [at - .02, at + .12], [0, 1], clamp);
          return (
            <span key={i} style={{position: 'relative', display: 'inline-block', marginRight: i < words.length - 1 ? '.24em' : 0}}>
              <span style={{position: 'absolute', left: '-.06em', right: '-.06em', bottom: '.06em', height: '.42em', background: T.mark, borderRadius: 8,
                transform: `scaleX(${lit})`, transformOrigin: 'left', zIndex: 0}} />
              <span style={{position: 'relative', zIndex: 1}}>{w}</span>
            </span>
          );
        })}
      </div>
      {h.ko ? <div style={{fontWeight: 700, fontSize: 50, color: T.sub, marginTop: 14}}>{h.ko}</div> : null}
    </div>
  );
};

const Badge: React.FC<{who: 'mark' | 'joy'; t: number; s: number; fps: number}> = ({who, t, s, fps}) => {
  const k = spring({frame: Math.round((t - s - .05) * fps), fps, config: {damping: 13, stiffness: 200}});
  const mark = who === 'mark';
  return (
    <div style={{position: 'absolute', left: CARD.x + 28, top: CARD.y + 28, display: 'flex', alignItems: 'center', gap: 14, background: 'rgba(255,255,255,.94)',
      borderRadius: 999, padding: '10px 28px 10px 10px', boxShadow: '0 8px 24px rgba(0,0,0,.18)', fontFamily: FF, transform: `translateX(${(1 - k) * -60}px)`, opacity: k}}>
      <Img src={staticFile(mark ? 'brand/mark-avatar.png' : 'brand/joy-avatar.png')} style={{width: 84, height: 84, borderRadius: '50%'}} />
      <div style={{lineHeight: 1.1}}>
        <div style={{fontWeight: 900, fontSize: 40, color: '#111'}}>{mark ? 'Mark T' : 'Joy'} <span style={{fontSize: 44}}>{mark ? '🇬🇧' : '🇰🇷'}</span></div>
        <div style={{fontWeight: 700, fontSize: 28, color: mark ? '#2F6BFF' : '#E2556B'}}>{mark ? '영국 원어민 발음' : '놀이로 바로 써보기'}</div>
      </div>
    </div>
  );
};

const EndCard: React.FC<{t: number; s: number; fps: number}> = ({t, s, fps}) => {
  const k = (d: number) => spring({frame: Math.round((t - s - d) * fps), fps, config: {damping: 12, stiffness: 170}});
  const tap = interpolate(t, [s + 1.45, s + 1.6, s + 1.75], [1, .9, 1], clamp);
  const on = t > s + 1.6;
  return (
    <AbsoluteFill style={{background: T.page, opacity: interpolate(t, [s, s + .2], [0, 1], clamp), alignItems: 'center', fontFamily: FF}}>
      {T.logo === 'full' ? <Img src={staticFile('brand/logo-full.png')} style={{width: 420, marginTop: 250, transform: `scale(${k(0)})`}} />
        : <div style={{marginTop: 250, display: 'flex', flexDirection: 'column', alignItems: 'center', transform: `scale(${k(0)})`}}>
          <Img src={staticFile('brand/bear-butterfly.png')} style={{width: 300}} /><Img src={staticFile('brand/wordmark-cream.png')} style={{width: 420, marginTop: 10}} /></div>}
      <div style={{fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontWeight: 600, fontSize: 64, color: T.ink, marginTop: 40, opacity: k(.15)}}>Little Steps to Big Adventures</div>
      <div style={{fontWeight: 900, fontSize: 92, color: T.ink, marginTop: 50, letterSpacing: '-.03em', textAlign: 'center', lineHeight: 1.15, transform: `scale(${.85 + .15 * k(.3)})`, opacity: k(.3)}}>
        하루 <span style={{background: `linear-gradient(transparent 58%, ${T.mark} 58%)`}}>영어 3문장</span>,<br />놀면서 익혀요
      </div>
      <div style={{display: 'flex', gap: 20, marginTop: 50, opacity: k(.5)}}>
        {[['brand/mark-avatar.png', 'Mark T 🇬🇧'], ['brand/joy-avatar.png', 'Joy 🇰🇷']].map(([img, n]) => (
          <div key={n} style={{display: 'flex', alignItems: 'center', gap: 12, background: T.chip, color: T.ink, borderRadius: 999, padding: '8px 26px 8px 8px'}}>
            <Img src={staticFile(img)} style={{width: 70, height: 70, borderRadius: '50%'}} /><span style={{fontWeight: 800, fontSize: 36}}>{n}</span>
          </div>
        ))}
      </div>
      {/* Joy (11 Nov 2026): the ad sends people to the free Day 1 trial; sign-up is on the profile link */}
      <div style={{marginTop: 60, fontWeight: 800, fontSize: 40, color: '#E2556B', opacity: k(.6)}}>🎁 DAY 1 무료 체험</div>
      <div style={{marginTop: 18, background: on ? T.btnOn : T.btn, color: T.btnText, fontWeight: 900, fontSize: 48, borderRadius: 999, padding: '30px 60px', whiteSpace: 'nowrap',
        boxShadow: on ? `0 0 0 10px ${T.mark}` : 'none', transform: `scale(${tap * (.8 + .2 * k(.7))})`, opacity: k(.7)}}>무료 체험 신청은 프로필 링크에서 👆</div>
      <div style={{position: 'absolute', top: 1460 + interpolate(t, [s + 1.1, s + 1.5], [80, 0], clamp), left: 640, fontSize: 90, opacity: interpolate(t, [s + 1.1, s + 1.3, s + 2.2, s + 2.4], [0, 1, 1, 0], clamp)}}>👆</div>
    </AbsoluteFill>
  );
};

export const LittleStepsAd: React.FC<{plan: AdPlan}> = ({plan}) => {
  useFonts();
  T = THEMES[plan.theme ?? 'cream'];
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const i = Math.max(0, plan.shots.findIndex((s) => t < s.out_e));
  const sh = t >= plan.speechEnd ? plan.shots[plan.shots.length - 1] : plan.shots[i];
  const prev = plan.shots[i - 1];
  const first = !prev || prev.head.big !== sh.head.big;
  const local = t - sh.out_s, dur = sh.out_e - sh.out_s;
  const cx = interpolate(local, [0, dur], [sh.cx0, sh.cx1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const punch = interpolate(local, [0, .35], [1.07, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const bump = interpolate(local, [0, .12, .3], [.97, 1.01, 1], clamp);
  const cap = plan.caps.find((c) => t >= c.s && t < c.e);
  const capO = cap ? interpolate(t, [cap.s, cap.s + .1, cap.e - .08, cap.e], [0, 1, 1, 0], clamp) : 0;
  return (
    <AbsoluteFill style={{background: T.page}}>
      <AbsoluteFill style={{background: `radial-gradient(120% 60% at 50% 0%, ${T.glow} 0%, ${T.page} 55%)`}} />
      {/* progress: three phrase dots */}
      <div style={{position: 'absolute', top: 92, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 16}}>
        {[1, 2, 3].map((n) => {
          const done = plan.shots.some((s) => s.head.step === n && t >= s.out_s);
          return <div key={n} style={{width: done ? 56 : 18, height: 18, borderRadius: 9, background: done ? T.ink : T.dot}} />;
        })}
      </div>
      <Header sh={sh} t={t} fps={fps} first={first} />
      <div style={{position: 'absolute', left: CARD.x, top: CARD.y, width: CARD.w, height: CARD.h, borderRadius: 44, overflow: 'hidden',
        boxShadow: '0 30px 70px rgba(0,0,0,.22)', transform: `scale(${bump})`, background: '#ddd'}}>
        <div style={{position: 'absolute', inset: 0, transform: `scale(${punch})`, transformOrigin: '50% 35%'}}>
          <OffthreadVideo src={staticFile(`${plan.media}/cut.mov`)} muted
            style={{position: 'absolute', top: 0, height: CARD.h, width: 1920 * K, maxWidth: 'none', left: CARD.w / 2 - (sh.mirror ? 1920 - cx : cx) * K,
              transform: sh.mirror ? 'scaleX(-1)' : undefined}} />
        </div>
        <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,0) 62%, rgba(0,0,0,.45) 100%)', opacity: cap ? 1 : 0}} />
        {cap ? <div style={{position: 'absolute', left: 40, right: 40, bottom: 70, textAlign: 'center', fontFamily: FF, fontWeight: 800, fontSize: 60, color: '#fff',
          lineHeight: 1.3, wordBreak: 'keep-all', textShadow: '0 3px 14px rgba(0,0,0,.6)', opacity: capO, transform: `translateY(${(1 - capO) * 14}px)`}}>{cap.ko}</div> : null}
      </div>
      {t < plan.speechEnd ? <Badge key={i} who={sh.who} t={t} s={sh.out_s} fps={fps} /> : null}
      {t >= plan.speechEnd - .05 ? <EndCard t={t} s={plan.speechEnd} fps={fps} /> : null}
    </AbsoluteFill>
  );
};
