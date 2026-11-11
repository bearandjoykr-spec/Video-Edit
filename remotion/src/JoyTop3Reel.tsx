// Joy's TOP 3 picture books, v2 (Joy, 11 Nov 2026: make it exciting, built for saves and shares).
// Mystery hook (three "?" books), a 3-2-1 countdown with card-flip reveals, a save-worthy info card per book,
// a summary card to screenshot, then the Bear & Joy follow end card. Footage keeps its own colours (Joy, Day 28).
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, OffthreadVideo, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';

type Scene = {name: string; s: number; e: number};
type Book = {title: string; author: string; cover: string; info: [string, string, string][]};
export type Top3Plan = {fps: number; duration: number; frames: number; speechEnd: number; day: number; media: string;
  scenes: Scene[]; captions: {s: number; e: number; ko: string; hi: string}[]; books: Record<string, Book>;
  live: {who: 'mark' | 'joy'; en: string; ko: string; s: number; e: number}[]; next: {s: number; text: string}};

const C = {navy: '#1E2D4D', deep: '#173B5C', cream: '#F5F0E6', yellow: '#F6E27A', butter: '#F6F0BA', sky: '#AECCE6', white: '#FFFFFF', kakao: '#FEE500'};
const FF = "'Pretendard', 'Noto Color Emoji', sans-serif";
const SHADOW = '0 3px 10px rgba(10,16,30,.75), 0 0 28px rgba(10,16,30,.5)';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const FONTS: [string, string, string, string][] = [
  ['Pretendard', 'normal', '700', 'Pretendard-Bold.woff2'], ['Pretendard', 'normal', '800', 'Pretendard-ExtraBold.woff2'],
  ['Pretendard', 'normal', '900', 'Pretendard-Black.woff2'], ['Noto Color Emoji', 'normal', '400', 'Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf'],
  ['Playfair Display', 'italic', '600', 'nuFRD-vYSZviVYUb_rj3ij__anPXDTnCjmHKM4nYO7KN_naUbtY.ttf'],
];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([f, st, w, file]) => new FontFace(f, `url(${staticFile('fonts/' + file)})`, {style: st, weight: w}).load().then((x) => document.fonts.add(x))))
      .then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
  }, [h]);
};
const sp = (t: number, s: number, fps: number, damping = 10) => spring({frame: Math.round((t - s) * fps), fps, config: {damping, stiffness: 190, mass: .6}});

// A book card: front is a cream "?" card, back is the cover photo. flip 0 -> 1 turns it over.
const BookCard: React.FC<{w: number; h: number; flip: number; cover?: string; rot?: number; media: string}> = ({w, h, flip, cover, rot = 0, media}) => (
  <div style={{width: w, height: h, perspective: 1600, transform: `rotate(${rot}deg)`}}>
    <div style={{position: 'relative', width: '100%', height: '100%', transformStyle: 'preserve-3d', transform: `rotateY(${flip * 180}deg)`}}>
      <div style={{position: 'absolute', inset: 0, backfaceVisibility: 'hidden', borderRadius: 26, background: C.cream, boxShadow: '0 24px 60px rgba(0,0,0,.45)',
        border: `10px solid ${C.butter}`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{fontFamily: FF, fontWeight: 900, fontSize: h * .55, color: C.deep, lineHeight: 1}}>?</div>
        <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 26, background: C.deep, borderRadius: '16px 0 0 16px', opacity: .9}} />
      </div>
      {cover ? <Img src={staticFile(`${media}/covers/${cover}`)} style={{position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', borderRadius: 26,
        backfaceVisibility: 'hidden', transform: 'rotateY(180deg)', boxShadow: '0 24px 60px rgba(0,0,0,.45)', border: `8px solid ${C.white}`}} /> : null}
    </div>
  </div>
);

const Caption: React.FC<{c: Top3Plan['captions'][0]; t: number}> = ({c, t}) => {
  const o = interpolate(t, [c.s, c.s + .08, c.e - .06, c.e], [0, 1, 1, 0], clamp);
  const parts = c.hi ? c.ko.split(c.hi) : [c.ko];
  return (
    <div style={{position: 'absolute', left: 70, right: 110, top: 1330, textAlign: 'center', fontFamily: FF, fontWeight: 800, fontSize: 64, lineHeight: 1.3,
      color: C.white, textShadow: SHADOW, wordBreak: 'keep-all', opacity: o, transform: `translateY(${(1 - o) * 12}px) scale(${.96 + .04 * o})`}}>
      {parts.map((x, i) => <React.Fragment key={i}>{x}{i < parts.length - 1 ? <span style={{color: C.yellow}}>{c.hi}</span> : null}</React.Fragment>)}
    </div>
  );
};

const RankDots: React.FC<{t: number; scenes: Scene[]}> = ({t, scenes}) => {
  const at = (n: number) => scenes.find((s) => s.name === `reveal${n}`)?.s ?? 1e9;
  return (
    <div style={{position: 'absolute', top: 236, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 18, fontFamily: FF}}>
      {[1, 2, 3].map((n) => {
        const on = t >= at(n);
        return <div key={n} style={{minWidth: 60, height: 60, borderRadius: 30, fontWeight: 900, fontSize: 36, display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: on ? C.yellow : 'rgba(255,255,255,.22)', color: on ? C.navy : 'rgba(255,255,255,.85)', boxShadow: '0 6px 16px rgba(0,0,0,.25)'}}>{n}</div>;
      })}
    </div>
  );
};



export const JoyTop3Reel: React.FC<{plan: Top3Plan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const sc = plan.scenes.find((s) => t >= s.s && t < s.e) ?? plan.scenes[plan.scenes.length - 1];
  const name = t >= plan.speechEnd ? 'end' : sc.name;
  const local = t - sc.s;
  const cap = plan.captions.find((c) => t >= c.s && t < c.e);
  const dark = name === 'hook' ? .55 : name.startsWith('reveal') ? .62 : name === 'summary' ? 0 : 0;
  // a quick punch-in on every scene change
  const punch = interpolate(local, [0, .3], [1.08, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const rank = name.startsWith('reveal') || name.startsWith('book') ? Number(name.slice(-1)) : 0;
  const book = rank ? plan.books[String(rank)] : undefined;
  return (
    <AbsoluteFill style={{background: C.navy, fontFamily: FF}}>
      <AbsoluteFill style={{transform: `scale(${punch})`}}>
        <OffthreadVideo src={staticFile(`${plan.media}/cut.mov`)} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: `rgba(14,22,40,${dark})`}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,16,30,.35) 0%, rgba(10,16,30,0) 22%, rgba(10,16,30,0) 60%, rgba(10,16,30,.45) 78%, rgba(10,16,30,.3) 100%)'}} />

      {/* HOOK: three mystery books on the shelves */}
      {name === 'hook' ? (() => {
        const hk = sp(t, -0.6, fps, 12); // title already on screen at frame 1 (thumbnail)
        return (
          <>
            <div style={{position: 'absolute', top: 300, left: 40, right: 40, textAlign: 'center', transform: `scale(${.85 + .15 * hk})`, opacity: hk}}>
              <div style={{fontWeight: 800, fontSize: 50, color: C.white, textShadow: SHADOW}}>📌 서점 가기 전 저장 필수</div>
              <div style={{fontWeight: 900, fontSize: 104, lineHeight: 1.12, color: C.white, textShadow: SHADOW, marginTop: 14, letterSpacing: '-.03em'}}>
                아이가 <span style={{color: C.yellow}}>"한 번 더!"</span><br />외치는 영어 그림책</div>
            </div>
            <div style={{position: 'absolute', top: 760, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 34}}>
              {[0, 1, 2].map((k) => {
                // the three books are on screen from frame 1 (thumbnail); each one jumps on its thud
                const d = t - (.25 + .4 * k);
                const bump = d > 0 && d < .35 ? Math.sin(d / .35 * Math.PI) : 0;
                const wob = Math.sin((t + k) * 3.2) * 2;
                return <div key={k} style={{transform: `translateY(${-40 * bump}px) scale(${1 + .1 * bump})`}}>
                  <BookCard w={290} h={400} flip={0} rot={(k - 1) * 7 + wob} media={plan.media} /></div>;
              })}
            </div>
            <div style={{position: 'absolute', top: 1210, left: 0, right: 0, textAlign: 'center', fontWeight: 900, fontSize: 92, color: C.yellow, textShadow: SHADOW,
              opacity: sp(t, 1.5, fps), transform: `scale(${.7 + .3 * sp(t, 1.5, fps, 8)})`}}>딱 3권!</div>
          </>
        );
      })() : null}

      {/* Joy's intro tag */}
      {name === 'joy' ? (() => {
        const p = sp(t, sc.s + .1, fps, 13);
        return (
          <div style={{position: 'absolute', left: 50, top: 1130, display: 'flex', alignItems: 'center', gap: 16, background: 'rgba(30,45,77,.9)', borderRadius: 999,
            padding: '12px 34px 12px 12px', transform: `translateX(${(1 - p) * -80}px)`, opacity: p, boxShadow: '0 10px 24px rgba(0,0,0,.3)'}}>
            <Img src={staticFile('brand/joy-avatar.png')} style={{width: 96, height: 96, borderRadius: '50%'}} />
            <div><div style={{fontWeight: 900, fontSize: 46, color: C.white}}>Joy T <span style={{fontSize: 48}}>🇰🇷</span></div>
              <div style={{fontWeight: 700, fontSize: 28, color: C.butter}}>Bear & Joy 공동 저자</div></div>
          </div>
        );
      })() : null}

      {/* REVEAL: rank slams in, the "?" card flips to the cover */}
      {name.startsWith('reveal') && book ? (() => {
        const r = sp(t, sc.s, fps, 8);
        const flip = interpolate(local, [.45, .85], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
        return (
          <>
            <div style={{position: 'absolute', top: 330, left: 0, right: 0, textAlign: 'center', fontWeight: 900, fontSize: 280, color: C.yellow, lineHeight: 1,
              textShadow: SHADOW, transform: `scale(${2.2 - 1.2 * r})`, opacity: Math.min(1, r * 2)}}>{rank}</div>
            <div style={{position: 'absolute', top: 640, left: 0, right: 0, display: 'flex', justifyContent: 'center', transform: `scale(${.9 + .1 * r})`}}>
              <BookCard w={500} h={660} flip={flip} cover={book.cover} media={plan.media} rot={(1 - flip) * -4} />
            </div>
          </>
        );
      })() : null}

      {/* BOOK: title strip, then the save card in the last 3.6 s */}
      {name.startsWith('book') && book ? (() => {
        const p = sp(t, sc.s, fps, 12);
        const cardAt = sc.e - 3.6;
        const k = sp(t, cardAt, fps, 12);
        return (
          <>
            <div style={{position: 'absolute', top: 310, left: 50, right: 50, textAlign: 'center', transform: `translateY(${(1 - p) * -30}px)`, opacity: p}}>
              <div style={{fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontWeight: 600, fontSize: book.title.length > 20 ? 66 : 80, color: C.white,
                textShadow: SHADOW, marginTop: 12, lineHeight: 1.1}}>{book.title}</div>
              <div style={{fontWeight: 700, fontSize: 34, color: C.butter, textShadow: SHADOW, marginTop: 6}}>by {book.author}</div>
            </div>
            {t >= cardAt - .05 ? (
              <>
                <AbsoluteFill style={{background: `rgba(14,22,40,${.5 * Math.min(1, k * 1.5)})`}} />
                <div style={{position: 'absolute', left: 70, right: 70, top: 560, background: C.cream, borderRadius: 40, padding: '34px 40px 30px',
                  boxShadow: '0 30px 70px rgba(0,0,0,.4)', transform: `translateY(${(1 - k) * 120}px) scale(${.9 + .1 * k})`, opacity: Math.min(1, k * 2)}}>
                  <div style={{display: 'flex', alignItems: 'center', gap: 24, marginBottom: 18}}>
                    <Img src={staticFile(`${plan.media}/covers/${book.cover}`)} style={{width: 150, height: 190, objectFit: 'cover', borderRadius: 14, boxShadow: '0 8px 18px rgba(0,0,0,.25)'}} />
                    <div>
                      <div style={{fontWeight: 900, fontSize: 34, color: '#C0392B'}}>📌 저장해 두세요</div>
                      <div style={{fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontWeight: 600, fontSize: book.title.length > 20 ? 46 : 54, color: C.deep, lineHeight: 1.1}}>{book.title}</div>
                    </div>
                  </div>
                  {book.info.map(([ic, label, val], i) => {
                    const q = sp(t, cardAt + .25 + .22 * i, fps, 13);
                    return (
                      <div key={i} style={{display: 'flex', alignItems: 'center', gap: 18, padding: '16px 0', borderTop: '2px solid rgba(23,59,92,.12)', opacity: q, transform: `translateX(${(1 - q) * 40}px)`}}>
                        <div style={{fontSize: 48, width: 64, textAlign: 'center'}}>{ic}</div>
                        <div style={{fontWeight: 800, fontSize: 34, color: '#6B7A90', width: 170}}>{label}</div>
                        <div style={{fontWeight: 900, fontSize: 42, color: C.navy, flex: 1, lineHeight: 1.2}}>{val}</div>
                      </div>
                    );
                  })}
                </div>
              </>
            ) : null}
          </>
        );
      })() : null}

      {/* SUMMARY: the whole list on one card, to screenshot */}
      {name === 'summary' ? (() => {
        const p = sp(t, sc.s, fps, 13);
        return (
          <AbsoluteFill style={{background: `rgba(245,240,230,${.97 * Math.min(1, p * 1.5)})`, alignItems: 'center'}}>
            <div style={{marginTop: 250, fontWeight: 900, fontSize: 44, color: '#C0392B', opacity: p}}>📌 저장 · 💌 공유 필수</div>
            <div style={{fontWeight: 900, fontSize: 84, color: C.navy, letterSpacing: '-.03em', opacity: p, marginTop: 6}}>영어 그림책 TOP 3</div>
            <div style={{marginTop: 40, width: 940}}>
              {[1, 2, 3].map((r, i) => {
                const b = plan.books[String(r)];
                const q = sp(t, sc.s + .25 + .25 * i, fps, 12);
                return (
                  <div key={r} style={{display: 'flex', alignItems: 'center', gap: 28, background: C.white, borderRadius: 28, padding: 20, marginBottom: 22,
                    boxShadow: '0 10px 26px rgba(30,45,77,.12)', opacity: q, transform: `translateX(${(1 - q) * 80}px)`}}>
                    <div style={{fontWeight: 900, fontSize: 56, color: C.deep, width: 90, textAlign: 'center'}}>{r}</div>
                    <Img src={staticFile(`${plan.media}/covers/${b.cover}`)} style={{width: 130, height: 165, objectFit: 'cover', borderRadius: 12}} />
                    <div style={{flex: 1}}>
                      <div style={{fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontWeight: 600, fontSize: b.title.length > 20 ? 40 : 46, color: C.deep, lineHeight: 1.1}}>{b.title}</div>
                      <div style={{fontWeight: 800, fontSize: 32, color: '#6B7A90', marginTop: 8}}>{b.info[0][2]} · {b.info[1][2]}</div>
                    </div>
                  </div>
                );
              })}
            </div>
            {/* Joy: the bottom looked empty, so the Bear & Joy logo sits at the bottom centre */}
            <Img src={staticFile('brand/logo-full.png')} style={{position: 'absolute', bottom: 400, left: '50%', width: 340, transform: `translateX(-50%) scale(${.8 + .2 * sp(t, sc.s + 1, fps, 12)})`, opacity: sp(t, sc.s + 1, fps, 12)}} />
          </AbsoluteFill>
        );
      })() : null}

      {!['hook', 'summary', 'end', 'markq', 'outro'].includes(name) ? <RankDots t={t} scenes={plan.scenes} /> : null}
      {name !== 'hook' && name !== 'end' ? (
        <div style={{position: 'absolute', top: 120, right: 60, background: 'rgba(30,45,77,.85)', color: C.white, borderRadius: 999, padding: '10px 24px', fontWeight: 800, fontSize: 30}}>
          🔥 DAY {plan.day}</div>
      ) : null}
      {/* the hook title and the summary card already carry the words, so no captions there */}
      {cap && !['hook', 'summary', 'end'].includes(name) && t < plan.next.s ? <Caption c={cap} t={t} /> : null}

      {/* live lines: Mark's question at the start, Joy's answer at the end (their own voices) */}
      {plan.live.map((l, i) => (t >= l.s - .1 && t < l.e + .3 ? (() => {
        const p = sp(t, l.s - .1, fps, 12);
        const o = interpolate(t, [l.e, l.e + .3], [1, 0], clamp);
        const mark = l.who === 'mark';
        return (
          <div key={i} style={{position: 'absolute', left: 60, right: 60, top: 1180, textAlign: 'center', opacity: Math.min(1, p * 2) * o, transform: `translateY(${(1 - p) * 30}px)`}}>
            <div style={{display: 'inline-flex', alignItems: 'center', gap: 14, background: 'rgba(30,45,77,.9)', borderRadius: 999, padding: '8px 28px 8px 8px'}}>
              <Img src={staticFile(mark ? 'brand/mark-avatar.png' : 'brand/joy-avatar.png')} style={{width: 84, height: 84, borderRadius: '50%'}} />
              <span style={{fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontWeight: 600, fontSize: 48, color: C.yellow}}>{mark ? 'Mark T' : 'Joy T'}</span>
              <span style={{fontSize: 56}}>{mark ? '🇬🇧' : '🇰🇷'}</span>
            </div>
            <div style={{fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontWeight: 600, fontSize: 76, lineHeight: 1.1, color: C.white, textShadow: SHADOW, marginTop: 18}}>{l.en}</div>
            <div style={{fontWeight: 800, fontSize: 50, color: C.butter, textShadow: SHADOW, marginTop: 10}}>{l.ko}</div>
          </div>
        );
      })() : null))}
      {/* teaser for the next episode (Joy) */}
      {t >= plan.next.s && t < plan.speechEnd ? (() => {
        const p = sp(t, plan.next.s, fps, 8);
        return <div style={{position: 'absolute', top: 1250, left: 40, right: 40, textAlign: 'center', fontWeight: 900, fontSize: 84, whiteSpace: 'nowrap', color: C.yellow, textShadow: SHADOW,
          transform: `scale(${.6 + .4 * p}) rotate(${(1 - p) * -6}deg)`, opacity: Math.min(1, p * 2)}}>{plan.next.text}</div>;
      })() : null}

      {/* END: follow card */}
      {t >= plan.speechEnd - .05 ? (() => {
        const s = plan.speechEnd;
        const k = (d: number) => sp(t, s + d, fps, 12);
        const on = t > s + 2.85;
        return (
          <AbsoluteFill style={{background: C.navy, opacity: interpolate(t, [s, s + .25], [0, 1], clamp), alignItems: 'center'}}>
            <Img src={staticFile('brand/bear-butterfly.png')} style={{width: 260, marginTop: 300, transform: `scale(${k(0)})`}} />
            <Img src={staticFile('brand/wordmark-cream.png')} style={{width: 460, marginTop: 10, opacity: k(.1)}} />
            <div style={{fontWeight: 800, fontSize: 38, color: C.butter, marginTop: 50, opacity: k(.25)}}>DAY {plan.day} ✅ · 출간까지 매일 업로드 중 📚</div>
            <div style={{fontWeight: 900, fontSize: 96, color: C.white, textAlign: 'center', lineHeight: 1.15, marginTop: 24, transform: `scale(${.85 + .15 * k(.4)})`, opacity: k(.4)}}>
              팔로우하고<br /><span style={{color: C.yellow}}>DAY {plan.day + 1}</span> 같이 봐요!</div>
            <div style={{marginTop: 50, background: on ? 'rgba(255,255,255,.15)' : C.sky, color: on ? C.white : C.navy, fontWeight: 900, fontSize: 52, borderRadius: 999,
              padding: '24px 70px', transform: `scale(${interpolate(t, [s + 2.7, s + 2.85, s + 3], [1, .9, 1], clamp) * (.8 + .2 * k(.7))})`, opacity: k(.7)}}>{on ? '팔로잉 ✓' : '＋ 팔로우'}</div>
            <div style={{position: 'absolute', top: 1340 + interpolate(t, [s + 2.2, s + 2.7], [90, 0], clamp), left: 600, fontSize: 96,
              opacity: interpolate(t, [s + 2.2, s + 2.4, s + 3.6, s + 3.8], [0, 1, 1, 0], clamp)}}>👆</div>
            <div style={{position: 'absolute', top: 1500, fontWeight: 800, fontSize: 36, color: C.white, opacity: k(1)}}>💌 영어 그림책 고민하는 친구에게 공유해 주세요</div>
          </AbsoluteFill>
        );
      })() : null}
    </AbsoluteFill>
  );
};
