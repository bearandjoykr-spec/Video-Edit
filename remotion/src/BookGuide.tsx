// DAY 34 "그림책 TOP 3, 이렇게 읽어주세요" (Joy, 17 Nov 2026): each book gets a cover reveal, a page card with the key sentence
// (our own card, not the copyrighted illustration), a "how to read it" card and a "what to ask" card; a save card closes it.
// Chalk fonts (Gaegu + Patrick Hand) are the house style from DAY 33.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, OffthreadVideo, continueRender, delayRender, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

type Sec = {kind: string; book: number; s: number; e: number; vo: string};
type Book = {title: string; author: string; cover: string; age: string; lines: string[]; lines_ko: string[]; read: string[]; ask: string; ask_ko: string; answer: string};
export type GuidePlan = {fps: number; day: number; duration: number; frames: number; media: string; sections: Sec[]; books: Record<string, Book>; showVo?: boolean};

const C = {navy: '#1E2D4D', cream: '#F5F0E6', paper: '#FFFDF6', yellow: '#F6E27A', butter: '#F6F0BA', sky: '#AECCE6', board: '#23402F', chalk: '#F4F1E6', pink: '#F7B2B7', red: '#E4572E'};
const PRE = "'Pretendard', 'Noto Color Emoji', sans-serif";
const EN = "'Patrick Hand', 'Gaegu', 'Noto Color Emoji', cursive";
const KO = "'Gaegu', 'Patrick Hand', 'Noto Color Emoji', cursive";
const SHADOW = '0 3px 10px rgba(10,16,30,.8), 0 0 26px rgba(10,16,30,.5)';
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
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
const sp = (t: number, s: number, fps: number, damping = 12) => spring({frame: Math.round((t - s) * fps), fps, config: {damping, stiffness: 190, mass: .6}});

// the number tab that tells viewers where they are (1/3, 2/3, 3/3)
const Tabs: React.FC<{book: number}> = ({book}) => (
  <div style={{position: 'absolute', top: 120, left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 14}}>
    {[1, 2, 3].map((n) => <div key={n} style={{width: n === book ? 120 : 64, height: 64, borderRadius: 32, display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: PRE, fontWeight: 900, fontSize: 34, background: n <= book ? C.yellow : 'rgba(255,255,255,.3)', color: C.navy, boxShadow: '0 6px 14px rgba(0,0,0,.25)'}}>
      {n === book ? `📚 ${n}` : n}</div>)}
  </div>
);

const Label: React.FC<{text: string; color: string; t: number; s: number; fps: number}> = ({text, color, t, s, fps}) => {
  const k = sp(t, s, fps, 10);
  return <div style={{display: 'inline-block', fontFamily: PRE, fontWeight: 900, fontSize: 40, color: C.navy, background: color, borderRadius: 999, padding: '8px 26px',
    transform: `scale(${.7 + .3 * k}) rotate(-3deg)`, boxShadow: '0 8px 18px rgba(0,0,0,.25)'}}>{text}</div>;
};

// an open picture-book page with the sentence written on it
const PageCard: React.FC<{b: Book; t: number; s: number; fps: number}> = ({b, t, s, fps}) => {
  const k = sp(t, s, fps, 13);
  const flip = interpolate(t, [s, s + .45], [-80, 0], clamp);
  return (
    <div style={{position: 'absolute', left: 60, right: 60, top: 520, perspective: 1600}}>
      <div style={{transform: `rotateY(${flip}deg) scale(${.9 + .1 * k})`, transformOrigin: '0 50%', opacity: Math.min(1, k * 2)}}>
        <div style={{position: 'relative', background: C.paper, borderRadius: 26, padding: '56px 50px 44px', boxShadow: '0 30px 70px rgba(0,0,0,.45)',
          backgroundImage: 'linear-gradient(90deg, rgba(0,0,0,.06) 0, rgba(0,0,0,0) 40px, rgba(0,0,0,0) calc(100% - 40px), rgba(0,0,0,.05) 100%)'}}>
          <div style={{position: 'absolute', top: -34, left: 40}}><Label text="📖 책 속 문장" color={C.yellow} t={t} s={s + .2} fps={fps} /></div>
          {b.lines.map((l, i) => {
            const q = sp(t, s + .5 + .6 * i, fps, 12);
            return (
              <div key={i} style={{opacity: q, transform: `translateY(${(1 - q) * 20}px)`, marginTop: i ? 26 : 0}}>
                <div style={{fontFamily: EN, fontSize: 96, lineHeight: 1.05, color: C.navy}}>{l}</div>
                <div style={{fontFamily: KO, fontWeight: 700, fontSize: 50, color: '#7A6A55', marginTop: 6}}>{b.lines_ko[i]}</div>
              </div>
            );
          })}
          <div style={{fontFamily: PRE, fontWeight: 700, fontSize: 26, color: '#9A8C78', marginTop: 26, textAlign: 'right'}}>{b.title} · {b.author}</div>
        </div>
      </div>
    </div>
  );
};

const TipCard: React.FC<{b: Book; kind: string; t: number; s: number; fps: number}> = ({b, kind, t, s, fps}) => {
  const k = sp(t, s, fps, 12);
  const ask = kind === 'ask';
  const ansAt = s + 2.0;
  return (
    <div style={{position: 'absolute', left: 60, right: 60, top: 560, transform: `translateY(${(1 - k) * 80}px) rotate(${ask ? 1.5 : -1.5}deg)`, opacity: Math.min(1, k * 2)}}>
      <div style={{position: 'relative', background: `radial-gradient(120% 90% at 50% 40%, #2E5440 0%, ${C.board} 75%)`, border: '16px solid #8A5A35', borderRadius: 22,
        padding: '58px 44px 44px', boxShadow: '0 30px 70px rgba(0,0,0,.45)'}}>
        <div style={{position: 'absolute', top: -36, left: 36}}><Label text={ask ? '💬 다 읽고 이렇게 물어봐요' : '🎙 이렇게 읽어주세요'} color={ask ? C.sky : C.pink} t={t} s={s + .15} fps={fps} /></div>
        {ask ? (
          <>
            <div style={{fontFamily: EN, fontSize: 100, color: C.yellow, lineHeight: 1}}>{b.ask}</div>
            <div style={{fontFamily: KO, fontWeight: 700, fontSize: 54, color: C.chalk, marginTop: 8}}>{b.ask_ko}</div>
            <div style={{marginTop: 30, display: 'inline-block', fontFamily: EN, fontSize: 70, color: C.navy, background: C.chalk, borderRadius: '30px 30px 30px 6px', padding: '8px 30px',
              opacity: interpolate(t, [ansAt, ansAt + .2], [0, 1], clamp), transform: `scale(${.7 + .3 * sp(t, ansAt, fps, 9)})`}}>👧 {b.answer}</div>
          </>
        ) : b.read.map((l, i) => {
          const q = sp(t, s + .4 + .7 * i, fps, 12);
          return <div key={i} style={{fontFamily: KO, fontWeight: 700, fontSize: 76, lineHeight: 1.2, color: i ? C.yellow : C.chalk, opacity: q, transform: `translateX(${(1 - q) * 40}px)`}}>{l}</div>;
        })}
      </div>
    </div>
  );
};

export const BookGuide: React.FC<{plan: GuidePlan}> = ({plan}) => {
  useFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const sec = plan.sections.find((x) => t >= x.s && t < x.e) ?? plan.sections[plan.sections.length - 1];
  const b = sec.book ? plan.books[String(sec.book)] : undefined;
  const local = t - sec.s;
  const punch = interpolate(local, [0, .3], [1.07, 1], clamp);
  const hookEnd = plan.sections.find((x) => x.kind !== 'hook')!.s;
  const dim = sec.kind === 'page' || sec.kind === 'read' || sec.kind === 'ask' ? .45 : sec.kind.startsWith('bonus') ? .4 : sec.kind === 'hook' ? (t < plan.sections[3].s ? .08 : .25) : .1;
  return (
    <AbsoluteFill style={{background: C.navy, fontFamily: PRE}}>
      <AbsoluteFill style={{transform: `scale(${punch})`}}>
        <OffthreadVideo src={staticFile(`${plan.media}/cut.mov`)} muted style={{width: '100%', height: '100%'}} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: `rgba(14,22,40,${dim})`}} />
      {/* VISUAL HOOK (Joy, 18 Nov, like DAY 25): a giant "TOP 3" behind Joy's head; her cut-out sits on top of the word */}
      {t < plan.sections[3].s + .05 ? (() => {
        const k = sp(t, -.3, fps, 10);
        return (
          <>
            <div style={{position: 'absolute', left: 0, right: 0, top: 360, textAlign: 'center', fontFamily: PRE, fontWeight: 900, fontSize: 330, lineHeight: 1, letterSpacing: '-.04em',
              color: C.cream, textShadow: '0 10px 40px rgba(0,0,0,.35)', transform: `scale(${.9 + .1 * k})`}}>TOP 3</div>
            <OffthreadVideo src={staticFile(`${plan.media}/hook-joy.webm`)} transparent muted style={{position: 'absolute', inset: 0, width: '100%', height: '100%'}} />
          </>
        );
      })() : null}
      {sec.kind === 'hook' && sec.s >= plan.sections[3].s ? <AbsoluteFill style={{background: '#fff', opacity: interpolate(local, [0, .12], [.45, 0], clamp)}} /> : null}

      {/* HOOK / thumbnail */}
      {t < plan.sections[3].s ? (() => {
        const k = sp(t, -.3, fps, 12);
        return (
          <>
            <div style={{position: 'absolute', top: 280, left: 0, right: 0, textAlign: 'center', fontWeight: 800, fontSize: 54, color: '#fff', textShadow: SHADOW, opacity: k}}>
              영어 선생님이 고른 영어 그림책</div>
            <div style={{position: 'absolute', top: 1380, left: 30, right: 30, textAlign: 'center', fontWeight: 900, fontSize: 76, lineHeight: 1.2, color: '#fff', textShadow: SHADOW,
              transform: `scale(${.9 + .1 * k})`}}>아이가 <span style={{color: C.yellow}}>"한 번 더!"</span><br />외치는 책은? 📚</div>
            <div style={{position: 'absolute', top: 1640, left: 0, right: 0, textAlign: 'center'}}>
              <span style={{fontWeight: 800, fontSize: 36, color: C.navy, background: C.butter, borderRadius: 999, padding: '8px 24px'}}>📌 책 속 문장 + 읽어주는 법 + 질문까지</span></div>
          </>
        );
      })() : t < hookEnd ? (() => {
        const k = sp(t, plan.sections[3].s - .3, fps, 12);
        return (
          <div style={{position: 'absolute', left: 30, right: 30, top: 420, textAlign: 'center', transform: `scale(${.92 + .08 * k})`}}>
            <div style={{display: 'inline-block', fontWeight: 800, fontSize: 40, color: C.navy, background: C.butter, borderRadius: 999, padding: '8px 26px'}}>📌 저장하고 읽어줄 때 꺼내 보기</div>
            <div style={{fontWeight: 900, fontSize: 104, lineHeight: 1.1, color: '#fff', textShadow: SHADOW, marginTop: 24, letterSpacing: '-.03em'}}>
              같은 그림책도<br /><span style={{color: C.yellow}}>이렇게 읽으면</span><br />"한 번 더!" 🙌</div>
            <div style={{fontFamily: KO, fontWeight: 700, fontSize: 60, color: '#fff', textShadow: SHADOW, marginTop: 22}}>책 속 문장 + 읽어주는 법 + 질문까지</div>
          </div>
        );
      })() : null}

      {/* COVER: the book slams in with its number */}
      {sec.kind === 'cover' && b ? (() => {
        const k = sp(t, sec.s, fps, 9);
        return (
          <>
            <div style={{position: 'absolute', top: 260, left: 0, right: 0, textAlign: 'center', fontFamily: PRE, fontWeight: 900, fontSize: 200, color: C.yellow, textShadow: SHADOW,
              transform: `scale(${2 - k})`, opacity: Math.min(1, k * 2), lineHeight: 1}}>{sec.book}</div>
            <div style={{position: 'absolute', left: 40, right: 40, top: 1220, textAlign: 'center', opacity: k}}>
              <div style={{fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontWeight: 600, fontSize: b.title.length > 20 ? 72 : 86, color: '#fff', textShadow: SHADOW, lineHeight: 1.05}}>{b.title}</div>
              <div style={{fontWeight: 800, fontSize: 36, color: C.butter, textShadow: SHADOW, marginTop: 10}}>{b.author} · 추천 {b.age}</div>
            </div>
          </>
        );
      })() : null}
      {sec.kind === 'page' && b ? <PageCard b={b} t={t} s={sec.s} fps={fps} /> : null}
      {(sec.kind === 'read' || sec.kind === 'ask') && b ? <TipCard b={b} kind={sec.kind} t={t} s={sec.s} fps={fps} /> : null}
      {sec.book && sec.kind !== 'cover' ? <Tabs book={sec.book} /> : null}
      {/* Joy: the book's cover sits small at the top right while its sentence, reading tip and question are on screen */}
      {b && ['page', 'read', 'ask'].includes(sec.kind) ? (() => {
        const first = plan.sections.find((x) => x.book === sec.book && x.kind === 'page')!.s;
        const k = sp(t, first, fps, 11);
        return <Img src={staticFile(`${plan.media}/covers/${b.cover}`)} style={{position: 'absolute', right: 56, top: 300, width: 170, height: 215, objectFit: 'cover', borderRadius: 12,
          border: '6px solid #fff', boxShadow: '0 14px 30px rgba(0,0,0,.45)', transform: `rotate(6deg) scale(${.6 + .4 * k})`, opacity: Math.min(1, k * 2), zIndex: 5}} />;
      })() : null}
      {sec.book && sec.kind !== 'cover' && b ? (
        <div style={{position: 'absolute', top: 210, left: 0, right: 0, textAlign: 'center', fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontWeight: 600, fontSize: 44, color: '#fff', textShadow: SHADOW}}>{b.title}</div>
      ) : null}

      {/* captions (Joy, 17 Nov: posted as captions with music; line breaks set by hand in build.py) */}
      {plan.showVo && sec.vo && sec.kind !== 'summary' && t >= plan.sections[3].s ? (
        <div style={{position: 'absolute', left: 50, right: 50, bottom: 260, textAlign: 'center', fontWeight: 800, fontSize: 46, lineHeight: 1.35, color: '#fff', textShadow: SHADOW,
          wordBreak: 'keep-all', whiteSpace: 'pre-line'}}>{sec.vo}</div>
      ) : null}

      {/* SAVE CARD (Joy: a clean page, not a chalkboard) */}
      {sec.kind === 'summary' ? (() => {
        const o = interpolate(local, [0, .25], [0, 1], clamp);
        const all = [1, 2, 3].map((n) => plan.books[String(n)]);
        return (
          <AbsoluteFill style={{opacity: o, background: C.cream}}>
            <div style={{position: 'absolute', top: 130, left: 0, right: 0, textAlign: 'center'}}>
              <div style={{display: 'inline-block', fontWeight: 800, fontSize: 36, color: C.navy, background: C.yellow, borderRadius: 999, padding: '8px 26px'}}>📌 저장하고 읽어줄 때 꺼내 보세요</div>
              <div style={{fontFamily: KO, fontWeight: 700, fontSize: 84, color: C.navy, marginTop: 20}}>그림책 3권 읽어주기 카드</div>
            </div>
            {all.map((bk, i) => {
              const k = sp(t, sec.s + .3 + .3 * i, fps, 12);
              return (
                <div key={i} style={{position: 'absolute', left: 60, right: 60, top: 400 + i * 400, display: 'flex', gap: 28, background: '#fff', borderRadius: 28,
                  padding: 26, boxShadow: '0 12px 30px rgba(30,45,77,.12)', opacity: k, transform: `translateX(${(1 - k) * 60}px)`}}>
                  <Img src={staticFile(`${plan.media}/covers/${bk.cover}`)} style={{width: 150, height: 190, objectFit: 'cover', borderRadius: 12}} />
                  <div style={{flex: 1}}>
                    <div style={{fontFamily: EN, fontSize: 52, color: C.navy, lineHeight: 1}}>{i + 1}. {bk.title}</div>
                    <div style={{fontFamily: EN, fontSize: 44, color: '#5A6A84', marginTop: 10}}>📖 "{bk.lines[0]}"</div>
                    <div style={{fontFamily: KO, fontWeight: 700, fontSize: 40, color: '#C0392B', marginTop: 4}}>🎙 {bk.read[0]} {bk.read[1]}</div>
                    <div style={{fontFamily: EN, fontSize: 44, color: '#2F6DA8', marginTop: 4}}>💬 {bk.ask}</div>
                  </div>
                </div>
              );
            })}
            <div style={{position: 'absolute', bottom: 120, left: 0, right: 0, textAlign: 'center', fontWeight: 800, fontSize: 40, color: C.navy}}>
              💬 댓글에 <span style={{color: '#C0392B'}}>'그림책'</span> 남기면 이 카드를 DM으로 보내드려요</div>
          </AbsoluteFill>
        );
      })() : null}

      {/* BONUS: Bear & Joy (Joy, 17 Nov) */}
      {sec.kind.startsWith('bonus') ? (() => {
        const bonus = plan.sections.filter((x) => x.kind.startsWith('bonus'));
        const b0 = bonus[0].s;
        const pts: [string, string, string][] = [
          ['🔤', '영어 읽기가 두려워도 OK', '한글 발음 가이드로 바로 읽어줘요'],
          ['💭', '페이지마다 질문 가이드', '사고력 · 상상력이 쑥쑥'],
          ['🌳', '그림책을 넘어 일상으로', '오늘 바로 쓰는 영어 문장'],
        ];
        const k0 = sp(t, b0, fps, 9);
        return (
          <>
            <div style={{position: 'absolute', top: 150, left: 0, right: 0, textAlign: 'center', transform: `scale(${.7 + .3 * k0})`, opacity: Math.min(1, k0 * 2)}}>
              <div style={{display: 'inline-block', fontWeight: 900, fontSize: 58, color: C.navy, background: C.yellow, borderRadius: 999, padding: '10px 38px', transform: `rotate(-4deg) scale(${1 + .06 * Math.sin(t * 6)})`,
                boxShadow: '0 0 0 8px rgba(246,226,122,.35), 0 12px 26px rgba(0,0,0,.35)'}}>🎁 BONUS · 베어앤조이 추천</div>
              <div style={{fontFamily: "'Playfair Display', serif", fontStyle: 'italic', fontWeight: 600, fontSize: 120, color: '#fff', textShadow: SHADOW, marginTop: 14, lineHeight: 1}}>Bear &amp; Joy</div>
              <div style={{fontFamily: KO, fontWeight: 700, fontSize: 54, color: C.butter, textShadow: SHADOW}}>베어앤조이가 직접 만든 영어 그림책</div>
            </div>
            <div style={{position: 'absolute', left: 60, right: 60, top: 560, display: 'grid', gap: 16}}>
              {pts.map(([ic, h, sub], i) => {
                const at = bonus[i + 1]?.s ?? 1e9; const k = sp(t, at, fps, 11);
                if (t < at) return null;
                const now = sec === bonus[i + 1];
                if (!now) return (
                  <div key={i} style={{display: 'flex', alignItems: 'center', gap: 14, background: 'rgba(30,45,77,.75)', borderRadius: 999, padding: '10px 24px', alignSelf: 'start',
                    fontWeight: 800, fontSize: 34, color: '#fff', width: 'fit-content'}}>✅ {h}</div>
                );
                return (
                  <div key={i} style={{display: 'flex', alignItems: 'center', gap: 22, background: C.yellow, borderRadius: 26, padding: '22px 28px',
                    outline: '6px solid rgba(255,255,255,.9)',
                    boxShadow: '0 14px 30px rgba(0,0,0,.3)', transform: `translateX(${(1 - k) * 80}px) scale(${now ? 1 : .96})`, opacity: k}}>
                    <div style={{fontSize: 70}}>{ic}</div>
                    <div><div style={{fontWeight: 900, fontSize: 46, color: C.navy}}>{h}</div>
                      <div style={{fontFamily: KO, fontWeight: 700, fontSize: 40, color: '#5A6A84', marginTop: 2}}>{sub}</div></div>
                  </div>
                );
              })}
            </div>
            {Array.from({length: 10}).map((_, i) => {
              const ph = (t * .8 + i / 10) % 1;
              return <div key={i} style={{position: 'absolute', left: 80 + random(`bx${i}`) * 900, top: 600 + random(`by${i}`) * 700 - ph * 120, fontSize: 40 + random(`bz${i}`) * 30,
                opacity: Math.sin(ph * Math.PI), fontFamily: PRE}}>✨</div>;
            })}
            <Img src={staticFile(`${plan.media}/covers/bearjoy.png`)} style={{position: 'absolute', right: 50, top: 1290, width: 250, borderRadius: 10, boxShadow: '0 18px 40px rgba(0,0,0,.45)',
              transform: `rotate(6deg) scale(${sp(t, b0 + .3, fps, 10)})`}} />
          </>
        );
      })() : null}

      {/* END */}
      {sec.kind === 'end' ? (() => {
        const s = sec.s; const k = (d: number) => sp(t, s + d, fps, 12); const on = t > s + 2.85;
        return (
          <AbsoluteFill style={{background: C.navy, opacity: interpolate(t, [s, s + .3], [0, 1], clamp), alignItems: 'center'}}>
            <Img src={staticFile('brand/bear-butterfly.png')} style={{width: 260, marginTop: 330, transform: `scale(${k(0)})`}} />
            <Img src={staticFile('brand/wordmark-cream.png')} style={{width: 460, marginTop: 10, opacity: k(.1)}} />
            <div style={{fontWeight: 800, fontSize: 38, color: C.butter, marginTop: 50, opacity: k(.25)}}>DAY {plan.day} ✅ · 출간까지 매일 업로드 중 📚</div>
            <div style={{fontWeight: 900, fontSize: 96, color: '#fff', textAlign: 'center', lineHeight: 1.15, marginTop: 24, opacity: k(.4)}}>팔로우하고<br /><span style={{color: C.yellow}}>DAY {plan.day + 1}</span> 같이 봐요!</div>
            <div style={{marginTop: 50, background: on ? 'rgba(255,255,255,.15)' : C.sky, color: on ? '#fff' : C.navy, fontWeight: 900, fontSize: 52, borderRadius: 999, padding: '24px 70px',
              transform: `scale(${interpolate(t, [s + 2.7, s + 2.85, s + 3], [1, .9, 1], clamp) * (.8 + .2 * k(.7))})`, opacity: k(.7)}}>{on ? '팔로잉 ✓' : '＋ 팔로우'}</div>
          </AbsoluteFill>
        );
      })() : null}

      {sec.kind !== 'end' ? (() => {
        const endS = plan.sections.find((x) => x.kind === 'end')!.s; const p = Math.min(1, t / endS);
        return (<>
          <div style={{position: 'absolute', top: 0, left: 0, right: 0, height: 12, background: 'rgba(255,255,255,.25)'}} />
          <div style={{position: 'absolute', top: 0, left: 0, width: 1080 * p, height: 12, background: C.yellow}} />
          <Img src={staticFile('brand/bear-butterfly.png')} style={{position: 'absolute', top: 6 - Math.abs(Math.sin(t * 9)) * 5, left: 1080 * p - 34, width: 64}} />
        </>);
      })() : null}
      {random('x') < 0 ? null : null}
    </AbsoluteFill>
  );
};
