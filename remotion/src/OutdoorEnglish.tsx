// DAY 33 "바깥놀이 영어 3문장" (Joy, 17 Nov 2026): a save-and-share format.
// Fast montage hook, a chalkboard (top) over Mark (bottom) for each phrase with swap-in words, a slow-motion replay and a
// "say it again" replay, and a chalkboard summary card to screenshot before the follow card.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, OffthreadVideo, continueRender, delayRender, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

type Seg = {out_s: number; out_e: number; layout: string; note: string; phrase: number};
type Chip = {w: string; emoji: string; t: number};
type Phrase = {k: number; s: number; e: number; n: string; en: string; ko: string; say: string; fill: string; chips: Chip[];
  slow: {s: number; e: number} | null; again: {s: number; e: number} | null};
export type OutdoorPlan = {fps: number; day: number; duration: number; frames: number; speechEnd: number; summaryEnd: number; media: string;
  cardOnly?: boolean; segments: Seg[]; captions: {s: number; e: number; ko: string; en?: string}[]; phrases: Phrase[]; joke: {s: number; e: number}};

const C = {navy: '#1E2D4D', cream: '#F5F0E6', yellow: '#F6E27A', butter: '#F6F0BA', sky: '#AECCE6', board: '#23402F', chalk: '#F4F1E6', pink: '#F7B2B7'};
const PRE = "'Pretendard', 'Noto Color Emoji', sans-serif";
const CHALK_EN = "'Patrick Hand', 'Gaegu', 'Noto Color Emoji', cursive";
const CHALK_KO = "'Gaegu', 'Patrick Hand', 'Noto Color Emoji', cursive";
const SHADOW = '0 3px 10px rgba(10,16,30,.8), 0 0 26px rgba(10,16,30,.5)';
const CHALK_GLOW = '0 0 2px rgba(255,255,255,.55), 0 2px 0 rgba(0,0,0,.25)';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const BOARD_H = 860;
const FONTS: [string, string, string, string][] = [
  ['Pretendard', 'normal', '700', 'Pretendard-Bold.woff2'], ['Pretendard', 'normal', '800', 'Pretendard-ExtraBold.woff2'],
  ['Pretendard', 'normal', '900', 'Pretendard-Black.woff2'], ['Noto Color Emoji', 'normal', '400', 'Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf'],
  ['Playfair Display', 'italic', '600', 'nuFRD-vYSZviVYUb_rj3ij__anPXDTnCjmHKM4nYO7KN_naUbtY.ttf'],
  ['Gaegu', 'normal', '700', 'Gaegu-Bold.ttf'], ['Patrick Hand', 'normal', '400', 'PatrickHand.ttf'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([f, st, w, file]) => new FontFace(f, `url(${staticFile('fonts/' + file)})`, {style: st, weight: w}).load().then((x) => document.fonts.add(x))))
      .then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
  }, [h]);
};
const sp = (t: number, s: number, fps: number, damping = 11) => spring({frame: Math.round((t - s) * fps), fps, config: {damping, stiffness: 190, mass: .6}});

// chalk dust: a few faint smudges so the board reads as a real chalkboard
const Smudges: React.FC = () => (
  <>
    {Array.from({length: 9}).map((_, k) => (
      <div key={k} style={{position: 'absolute', left: random(`sx${k}`) * 1000, top: random(`sy${k}`) * (BOARD_H - 100), width: 160 + random(`sw${k}`) * 260, height: 40 + random(`sh${k}`) * 70,
        borderRadius: '50%', background: 'rgba(255,255,255,.035)', filter: 'blur(14px)', transform: `rotate(${(random(`sr${k}`) - .5) * 30}deg)`}} />
    ))}
  </>
);

const Board: React.FC<{p: Phrase; t: number; fps: number}> = ({p, t, fps}) => {
  const inS = sp(t, p.s, fps, 14);
  const chip = [...p.chips].reverse().find((c) => t >= c.t);
  const slow = !!p.slow && t >= p.slow.s && t < p.slow.e, again = !!p.again && t >= p.again.s && t < p.again.e;
  // the replays repeat the first example ("Look, it's a car"), so the board shows that word again
  const word = slow || again ? p.fill : chip && p.fill ? chip.w : '';  // blank until Mark says the first word
  const parts = p.en.split('___');
  // chalk write-on: the sentence appears letter by letter in the first 0.9 s of the phrase
  const shown = Math.floor(interpolate(t, [p.s + .1, p.s + 1.0], [0, p.en.length], clamp));
  let left = shown;
  const take = (s: string) => { const n = Math.max(0, Math.min(s.length, left)); left -= s.length; return s.slice(0, n); };
  // in the replays each word of the sentence lights up in turn
  const rep = slow ? p.slow : again ? p.again : null;
  const words = p.en.replace('___', word || '___').split(' ');
  const lit = rep ? Math.floor(interpolate(t, [rep.s + .05, rep.e - .2], [0, words.length], clamp)) : -1;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, width: 1080, height: BOARD_H, overflow: 'hidden', opacity: Math.min(1, inS * 2)}}>
      <div style={{position: 'absolute', inset: 0, background: `radial-gradient(120% 90% at 50% 40%, #2E5440 0%, ${C.board} 70%, #1A3024 100%)`}} />
      <Smudges />
      <div style={{position: 'absolute', inset: 0, border: '22px solid #8A5A35', boxShadow: 'inset 0 0 0 4px #6E4426, inset 0 10px 30px rgba(0,0,0,.35)'}} />
      <div style={{position: 'absolute', left: 60, top: 54, fontFamily: CHALK_KO, fontWeight: 700, fontSize: 46, color: C.yellow, textShadow: CHALK_GLOW}}>
        {p.n} 바깥놀이 영어 <span style={{color: C.chalk, opacity: .7}}>{p.k}/3</span></div>
      <div style={{position: 'absolute', right: 56, top: 50, fontFamily: PRE, fontWeight: 800, fontSize: 30, color: C.navy, background: C.butter,
        borderRadius: 999, padding: '8px 20px', opacity: slow || again ? 1 : 0, transform: `scale(${slow || again ? 1 : .6})`}}>
        {slow ? '🐢 천천히 다시 듣기' : '🔁 한 번 더 따라 해요'}</div>
      {/* the sentence */}
      <div style={{position: 'absolute', left: 50, right: 50, top: 190, textAlign: 'center', fontFamily: CHALK_EN, fontSize: p.en.length > 16 ? 124 : 140, lineHeight: 1.05,
        color: C.chalk, textShadow: CHALK_GLOW}}>
        {rep ? words.map((w, i) => (
          <span key={i} style={{color: i < lit ? C.yellow : C.chalk, display: 'inline-block', transform: `scale(${i === lit - 1 ? 1.08 : 1})`,
            marginRight: i < words.length - 1 ? '.25em' : 0}}>{w}</span>
        )) : (
          <>
            {take(parts[0])}
            {parts.length > 1 ? (
              <span style={{display: 'inline-block', minWidth: word ? 0 : 210, borderBottom: `6px dashed ${word ? 'transparent' : C.chalk}`, color: C.yellow, margin: '0 .1em'}}>
                {left > 0 ? (word || ' ') : ' '}</span>
            ) : null}
            {parts.length > 1 ? take(parts[1]) : null}
          </>
        )}
      </div>
      <div style={{position: 'absolute', left: 50, right: 50, top: 410, textAlign: 'center', fontFamily: CHALK_KO, fontWeight: 700, fontSize: 76, color: C.chalk, textShadow: CHALK_GLOW,
        opacity: interpolate(t, [p.s + .7, p.s + 1.1], [0, 1], clamp)}}>{p.ko.replace('___', word ? ({car: '자동차', boat: '배', fish: '물고기', grass: '풀', trees: '나무'} as Record<string, string>)[word] ?? '○○' : '___')}</div>
      <div style={{position: 'absolute', left: 50, right: 50, top: 515, textAlign: 'center', fontFamily: CHALK_KO, fontWeight: 700, fontSize: 48, color: C.pink, textShadow: CHALK_GLOW,
        opacity: interpolate(t, [p.s + 1.0, p.s + 1.4], [0, 1], clamp)}}>[ {p.say.replace('___', ({car: '카', boat: '보트', fish: '피쉬', grass: '그래스', trees: '트리즈'} as Record<string, string>)[word] ?? '○○')} ]</div>
      {/* swap-in words */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 640, display: 'flex', justifyContent: 'center', gap: 22}}>
        {p.chips.map((c, i) => {
          const on = t >= c.t, cur = slow || again ? c.w === p.fill || (!p.fill && i === 0) : chip === c;
          const pop = sp(t, c.t, fps, 9);
          return (
            <div key={i} style={{fontFamily: CHALK_EN, fontSize: c.w.length > 8 ? 36 : 50, color: cur ? C.navy : C.chalk, background: cur ? C.yellow : 'rgba(255,255,255,.08)',
              border: `3px solid ${cur ? C.yellow : 'rgba(244,241,230,.5)'}`, borderRadius: 22, padding: '6px 22px', opacity: on ? 1 : .25,
              transform: `scale(${on ? .8 + .2 * pop : .9}) rotate(${(i - 1) * 2}deg)`, whiteSpace: 'nowrap'}}>{c.emoji} {c.w}</div>
          );
        })}
      </div>
    </div>
  );
};

const Caption: React.FC<{c: {s: number; e: number; ko: string; en?: string}; t: number; top: number}> = ({c, t, top}) => {
  const o = interpolate(t, [c.s, c.s + .08, c.e - .06, c.e], [0, 1, 1, 0], clamp);
  return <div style={{position: 'absolute', left: 60, right: 60, top, textAlign: 'center', fontFamily: PRE, fontWeight: 800, fontSize: 60, lineHeight: 1.3,
    color: '#fff', textShadow: SHADOW, wordBreak: 'keep-all', whiteSpace: 'pre-line', opacity: o, transform: `translateY(${(1 - o) * 10}px)`}}>{c.ko}
    {c.en ? <div style={{fontFamily: CHALK_KO, fontWeight: 700, fontSize: 78, color: C.yellow, marginTop: 8}}>{c.en}</div> : null}</div>;
};

export const OutdoorEnglish: React.FC<{plan: OutdoorPlan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const seg = plan.segments.find((g) => t >= g.out_s && t < g.out_e);
  const lay = seg?.layout ?? 'end';
  const phrase = seg && seg.phrase ? plan.phrases.find((p) => p.k === seg.phrase) : undefined;
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const boardOn = ['board', 'boardb', 'replay'].includes(lay);
  const hookEnd = plan.segments.find((g) => g.layout === 'full')!.out_s;
  const hookA = seg?.note === 'hookA' ? seg : undefined;
  const segStart = seg ? seg.out_s : 0;
  const flash = interpolate(t - segStart, [0, .12], [.5, 0], clamp);
  return (
    <AbsoluteFill style={{background: C.navy, fontFamily: PRE}}>
      <OffthreadVideo src={staticFile(`${plan.media}/cut.mov`)} muted style={{width: '100%', height: '100%'}} />
      {lay === 'montage' ? <AbsoluteFill style={{background: '#fff', opacity: flash}} /> : null}
      {lay === 'full' || lay === 'montage' ? <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,16,30,.25) 0%, rgba(10,16,30,0) 25%, rgba(10,16,30,0) 55%, rgba(10,16,30,.55) 85%)'}} /> : null}
      {boardOn && phrase ? <Board p={phrase} t={t} fps={fps} /> : null}
      {/* Hook A: the result first. The board writes "Look, it's a car!" while Mark says it and a real car drives by */}
      {hookA ? (() => {
        const p0 = plan.phrases[0];
        const hp = {...p0, s: hookA.out_s - .9, chips: [{...p0.chips[0], t: hookA.out_s + .85}, {...p0.chips[1], t: 1e9}, {...p0.chips[2], t: 1e9}]};
        const k = sp(t, -.4, fps, 9);
        return (
          <>
            <Board p={hp} t={t} fps={fps} />
            <div style={{position: 'absolute', left: 30, right: 30, top: 1250, textAlign: 'center', transform: `scale(${.85 + .15 * k}) rotate(-2deg)`}}>
              <div style={{display: 'inline-block', fontWeight: 900, fontSize: 92, lineHeight: 1.1, color: '#fff', textShadow: SHADOW, letterSpacing: '-.03em'}}>
                밖에서는 <span style={{color: C.yellow}}>이 한 문장</span>이면<br />끝! 👆</div>
            </div>
          </>
        );
      })() : null}

      {/* HOOK: the first frame is the thumbnail */}
      {t < hookEnd && !hookA ? (() => {
        const k = sp(t, -.4, fps, 12);
        return (
          <>
          {/* Joy: Mark's cut-out on a torn-paper panel, so the thumbnail shows the native-speaker teacher */}
          <svg width="1080" height="1920" style={{position: 'absolute', inset: 0}}>
            <defs><filter id="paperShadow"><feDropShadow dx="0" dy="-6" stdDeviation="10" floodOpacity=".35" /></filter></defs>
            <polygon filter="url(#paperShadow)" fill="#F5F0E6" points={`0,1920 0,${1180} ` + Array.from({length: 28}).map((_, i) => {
              const x = (i + 1) * 1080 / 28; return `${x},${1150 + (random(`tp${i}`) - .5) * 70 + (i % 2 ? 18 : -18)}`; }).join(' ') + ' 1080,1920'} />
            <polygon fill="#F6E27A" opacity=".9" points={`0,${1235} ` + Array.from({length: 28}).map((_, i) => {
              const x = (i + 1) * 1080 / 28; return `${x},${1210 + (random(`tq${i}`) - .5) * 50 + (i % 2 ? 12 : -12)}`; }).join(' ') + ` 1080,1262 1080,1250 0,1262`} />
          </svg>
          <Img src={staticFile(`${plan.media}/mark-cut.png`)} style={{position: 'absolute', left: 300, top: 1000, width: 820, transform: `translateY(${(1 - k) * 60}px)`,
            filter: 'drop-shadow(0 0 0 #fff) drop-shadow(6px 0 0 #fff) drop-shadow(-6px 0 0 #fff) drop-shadow(0 -6px 0 #fff) drop-shadow(0 18px 24px rgba(0,0,0,.35))'}} />
          <div style={{position: 'absolute', left: 40, top: 1330, transform: `rotate(-5deg) scale(${.8 + .2 * k})`, background: C.navy, borderRadius: 26, padding: '16px 26px',
            boxShadow: '0 12px 26px rgba(0,0,0,.3)'}}>
            <div style={{fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontWeight: 600, fontSize: 70, color: C.yellow, lineHeight: 1}}>Mark T <span style={{fontFamily: PRE, fontStyle: 'normal'}}>🇬🇧</span></div>
            <div style={{fontFamily: CHALK_KO, fontWeight: 700, fontSize: 44, color: '#fff', marginTop: 6}}>원어민 쌤이 알려줘요!</div>
          </div>
          <div style={{position: 'absolute', left: 30, right: 30, top: 300, textAlign: 'center', transform: `scale(${.9 + .1 * k})`}}>
            <div style={{display: 'inline-block', fontWeight: 800, fontSize: 40, color: C.navy, background: C.butter, borderRadius: 999, padding: '8px 26px'}}>📌 저장해두고 산책할 때 꺼내 보기</div>
            <div style={{fontWeight: 900, fontSize: 100, lineHeight: 1.12, color: '#fff', textShadow: SHADOW, marginTop: 26, letterSpacing: '-.03em'}}>
              아이랑 밖에 나가면<br /><span style={{color: C.yellow}}>영어로 뭐라고 하지?</span></div>
            <div style={{fontFamily: CHALK_KO, fontWeight: 700, fontSize: 66, color: '#fff', textShadow: SHADOW, marginTop: 24}}>바깥놀이 영어 3문장 ✨</div>
          </div>
          </>
        );
      })() : null}

      {/* Mark's name on his first shot */}
      {lay === 'full' && seg?.note === 'intro' ? (() => {
        const k = sp(t, seg.out_s + .2, fps, 13);
        return (
          <div style={{position: 'absolute', left: 50, top: 1090, display: 'flex', alignItems: 'center', gap: 16, background: 'rgba(20,32,58,.7)', borderRadius: 999,
            padding: '10px 32px 10px 10px', opacity: k, transform: `translateX(${(1 - k) * -60}px)`}}>
            <Img src={staticFile('brand/mark-avatar.png')} style={{width: 110, height: 110}} />
            <div><div style={{fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontWeight: 600, fontSize: 64, color: C.yellow, lineHeight: 1}}>Mark T <span style={{fontFamily: PRE, fontStyle: 'normal'}}>🇬🇧</span></div>
              <div style={{fontWeight: 700, fontSize: 30, color: '#fff', marginTop: 4}}>20년 이상 영어를 가르친 영국인 선생님</div></div>
          </div>
        );
      })() : null}

      {cap && t >= hookEnd && t < plan.speechEnd ? <Caption c={cap} t={t} top={boardOn ? 1660 : 1330} /> : null}

      {t >= plan.joke.s && t < plan.joke.e ? (() => {
        const k = sp(t, plan.joke.s, fps, 9);
        return <div style={{position: 'absolute', left: 0, right: 0, top: 230, textAlign: 'center', fontFamily: CHALK_KO, fontWeight: 700, fontSize: 64, color: C.yellow,
          textShadow: SHADOW, transform: `scale(${.7 + .3 * k}) rotate(${-4 + (1 - k) * -6}deg)`, opacity: Math.min(1, k * 2) * interpolate(t, [plan.joke.e - .25, plan.joke.e], [1, 0], clamp)}}>점심 사주실 분? 🍜</div>;
      })() : null}

      {/* SUMMARY: the card people save */}
      {t >= plan.speechEnd && t < plan.summaryEnd + .3 ? (() => {
        const s = plan.speechEnd;
        const o = interpolate(t, [s, s + .25, plan.summaryEnd, plan.summaryEnd + .3], [0, 1, 1, 0], clamp);
        return (
          <AbsoluteFill style={{opacity: o}}>
            <AbsoluteFill style={{background: `radial-gradient(120% 90% at 50% 40%, #2E5440 0%, ${C.board} 70%, #1A3024 100%)`}} />
            <Smudges />
            <AbsoluteFill style={{border: '26px solid #8A5A35', boxShadow: 'inset 0 0 0 5px #6E4426'}} />
            <div style={{position: 'absolute', top: 170, left: 0, right: 0, textAlign: 'center'}}>
              <div style={{display: 'inline-block', fontFamily: PRE, fontWeight: 800, fontSize: 40, color: C.navy, background: C.butter, borderRadius: 999, padding: '8px 26px'}}>📌 저장하고 산책 갈 때 꺼내 보세요</div>
              <div style={{fontFamily: CHALK_KO, fontWeight: 700, fontSize: 92, color: C.yellow, marginTop: 30, textShadow: CHALK_GLOW}}>바깥놀이 영어 3문장</div>
            </div>
            {plan.phrases.map((p, i) => {
              const k = sp(t, s + .35 + .3 * i, fps, 12);
              return (
                <div key={i} style={{position: 'absolute', left: 90, right: 90, top: 520 + i * 330, opacity: k, transform: `translateX(${(1 - k) * 60}px)`}}>
                  <div style={{fontFamily: CHALK_EN, fontSize: 92, color: C.chalk, lineHeight: 1, textShadow: CHALK_GLOW}}>{p.n} {p.en.replace('___', p.fill || '___')}</div>
                  <div style={{fontFamily: CHALK_KO, fontWeight: 700, fontSize: 54, color: C.chalk, marginTop: 10, opacity: .9}}>{p.ko.replace('___', {car: '자동차', grass: '풀'}[p.fill as 'car' | 'grass'] ?? '')}
                    <span style={{color: C.pink, fontSize: 40}}>  [{p.say.replace('___', ({car: '카', grass: '그래스'} as Record<string, string>)[p.fill] ?? '')}]</span></div>
                  <div style={{fontFamily: CHALK_EN, fontSize: 42, color: C.yellow, marginTop: 6}}>{p.chips.filter((c) => c.w.length < 9 && c.w !== '…').map((c) => `${c.emoji} ${c.w}`).join('   ')}</div>
                </div>
              );
            })}
            {plan.cardOnly ? (
              <div style={{position: 'absolute', bottom: 120, left: 0, right: 0, textAlign: 'center'}}>
                <Img src={staticFile('brand/wordmark-cream.png')} style={{width: 380, opacity: .9}} /></div>
            ) : (
              <div style={{position: 'absolute', bottom: 130, left: 0, right: 0, textAlign: 'center', fontFamily: PRE, fontWeight: 800, fontSize: 40, color: '#fff', lineHeight: 1.45}}>
                💬 댓글에 <span style={{color: C.yellow}}>'바깥놀이'</span> 남기면 이 카드를 DM으로 보내드려요<br />💌 아이랑 산책 가는 친구에게 공유해 주세요</div>
            )}
          </AbsoluteFill>
        );
      })() : null}

      {/* END: follow card */}
      {t >= plan.summaryEnd ? (() => {
        const s = plan.summaryEnd;
        const k = (d: number) => sp(t, s + d, fps, 12);
        const on = t > s + 2.85;
        return (
          <AbsoluteFill style={{background: C.navy, opacity: interpolate(t, [s, s + .3], [0, 1], clamp), alignItems: 'center'}}>
            <Img src={staticFile('brand/bear-butterfly.png')} style={{width: 260, marginTop: 330, transform: `scale(${k(0)})`}} />
            <Img src={staticFile('brand/wordmark-cream.png')} style={{width: 460, marginTop: 10, opacity: k(.1)}} />
            <div style={{fontWeight: 800, fontSize: 38, color: C.butter, marginTop: 50, opacity: k(.25)}}>DAY {plan.day} ✅ · 출간까지 매일 업로드 중 📚</div>
            <div style={{fontWeight: 900, fontSize: 96, color: '#fff', textAlign: 'center', lineHeight: 1.15, marginTop: 24, opacity: k(.4), transform: `scale(${.85 + .15 * k(.4)})`}}>
              팔로우하고<br /><span style={{color: C.yellow}}>DAY {plan.day + 1}</span> 같이 봐요!</div>
            <div style={{marginTop: 50, background: on ? 'rgba(255,255,255,.15)' : C.sky, color: on ? '#fff' : C.navy, fontWeight: 900, fontSize: 52, borderRadius: 999, padding: '24px 70px',
              transform: `scale(${interpolate(t, [s + 2.7, s + 2.85, s + 3], [1, .9, 1], clamp) * (.8 + .2 * k(.7))})`, opacity: k(.7)}}>{on ? '팔로잉 ✓' : '＋ 팔로우'}</div>
            <div style={{position: 'absolute', top: 1360 + interpolate(t, [s + 2.2, s + 2.7], [90, 0], clamp), left: 600, fontSize: 96,
              opacity: interpolate(t, [s + 2.2, s + 2.4, s + 3.6, s + 3.8], [0, 1, 1, 0], clamp)}}>👆</div>
          </AbsoluteFill>
        );
      })() : null}

      {/* progress bar with the bear walking along it */}
      {t < plan.summaryEnd && !plan.cardOnly ? (() => {
        const p = Math.min(1, t / plan.summaryEnd);
        return (
          <>
            <div style={{position: 'absolute', top: 0, left: 0, right: 0, height: 12, background: 'rgba(255,255,255,.25)'}} />
            <div style={{position: 'absolute', top: 0, left: 0, width: 1080 * p, height: 12, background: C.yellow}} />
            <Img src={staticFile('brand/bear-butterfly.png')} style={{position: 'absolute', top: 6 - Math.abs(Math.sin(t * 9)) * 5, left: 1080 * p - 34, width: 64}} />
          </>
        );
      })() : null}
      {t >= hookEnd && t < plan.speechEnd && !boardOn ? (
        <div style={{position: 'absolute', top: 110, right: 50, background: 'rgba(30,45,77,.85)', color: '#fff', borderRadius: 999, padding: '10px 24px', fontWeight: 800, fontSize: 30}}>🔥 DAY {plan.day}</div>
      ) : null}
    </AbsoluteFill>
  );
};
