// "AI 시대, 질문하는 아이" (Joy, 24 Nov 2026): paper-craft collage reel made on this Mac (no AI images).
// Kraft/cream paper with torn edges and soft shadows, hand-drawn arrows and question marks, Joy and Mark as printed paper dolls
// (projects/2026-11-ai-question/paper_doll.py), children seen from behind as paper figures (no real children's faces).
// All text stays inside y 300–1450. Storyboard draft: scene times are placeholders until Joy records the narration.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const C = {kraft: '#C9A47A', kraftD: '#A9825A', cream: '#F7F1E3', paper: '#FBF8F0', navy: '#1E2D4D', yellow: '#FFD84D', red: '#D9472F', ink: '#262320',
  skin: '#E9B892', hair: '#2A211C', blue: '#5B8DB8', green: '#6FA46B', pink: '#E58FA0'};
const PRE = "'Pretendard', 'Noto Color Emoji', sans-serif";
const HAND = "'Gaegu', 'Pretendard', 'Noto Color Emoji', cursive";
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const FONTS: [string, string, string][] = [['Pretendard', '700', 'Pretendard-Bold.woff2'], ['Pretendard', '800', 'Pretendard-ExtraBold.woff2'],
  ['Pretendard', '900', 'Pretendard-Black.woff2'], ['Noto Color Emoji', '400', 'Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf'], ['Gaegu', '700', 'Gaegu-Bold.ttf']];
const useFonts = () => {
  const [h] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(FONTS.map(([f, w, file]) => new FontFace(f, `url(${staticFile('fonts/' + file)})`, {weight: w}).load().then((x) => document.fonts.add(x))))
      .then(() => continueRender(h)).catch(() => continueRender(h));
  }, [h]);
};
const sp = (t: number, s: number, fps: number, damping = 13) => spring({frame: Math.round((t - s) * fps), fps, config: {damping, stiffness: 160, mass: .7}});
const rng = (seed0: number) => { let seed = (seed0 * 7919 + 12345) % 2147483647; const f = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }; f(); f(); return f; };
const SHADOW = 'drop-shadow(0 10px 14px rgba(40,25,10,.35)) drop-shadow(0 2px 3px rgba(40,25,10,.3))';

// a sheet of paper with torn edges
const tornPts = (w: number, h: number, seed: number, j = 9) => {
  const r = rng(seed); const pts: string[] = []; const step = 26;
  for (let x = 0; x <= w; x += step) pts.push(`${x},${r() * j}`);
  for (let y = 0; y <= h; y += step) pts.push(`${w - r() * j},${y}`);
  for (let x = w; x >= 0; x -= step) pts.push(`${x},${h - r() * j}`);
  for (let y = h; y >= 0; y -= step) pts.push(`${r() * j},${y}`);
  return pts.join(' ');
};
const Sheet: React.FC<{x: number; y: number; w: number; h: number; color?: string; seed?: number; rot?: number; style?: React.CSSProperties; children?: React.ReactNode}> =
  ({x, y, w, h, color = C.paper, seed = 3, rot = 0, style, children}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, transform: `rotate(${rot}deg)`, filter: SHADOW, ...style}}>
    <svg width={w} height={h} style={{position: 'absolute', inset: 0}}><polygon points={tornPts(w, h, seed)} fill={color} /></svg>
    <div style={{position: 'absolute', inset: 0}}>{children}</div>
  </div>
);

// whole-frame paper grain
const Grain: React.FC = () => (
  <AbsoluteFill style={{mixBlendMode: 'multiply', opacity: .35, pointerEvents: 'none'}}>
    <svg width="1080" height="1920"><filter id="g"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" seed="4" /><feColorMatrix values="0 0 0 0 .55  0 0 0 0 .5  0 0 0 0 .45  0 0 0 -1.1 1.05" /></filter>
      <rect width="1080" height="1920" filter="url(#g)" /></svg>
  </AbsoluteFill>
);

// a hand-drawn line that draws itself
const Draw: React.FC<{d: string; p: number; color?: string; w?: number}> = ({d, p, color = C.ink, w = 7}) => (
  <path d={d} fill="none" stroke={color} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
);

const Gear: React.FC<{x: number; y: number; r: number; a: number; color?: string}> = ({x, y, r, a, color = C.yellow}) => {
  const teeth = Array.from({length: 10}, (_, i) => i * 36);
  return <g transform={`translate(${x} ${y}) rotate(${a})`} style={{filter: SHADOW}}>
    {teeth.map((d) => <rect key={d} x={-r * .18} y={-r * 1.22} width={r * .36} height={r * .4} rx={3} fill={color} transform={`rotate(${d})`} />)}
    <circle r={r} fill={color} /><circle r={r * .38} fill={C.kraftD} /></g>;
};

// paper question mark / text cut from paper with a white border
const CutText: React.FC<{text: string; size: number; color: string; style?: React.CSSProperties}> = ({text, size, color, style}) => (
  <div style={{fontFamily: PRE, fontWeight: 900, fontSize: size, color, lineHeight: 1,
    textShadow: '0 0 0 #fff, 5px 0 0 #fff, -5px 0 0 #fff, 0 5px 0 #fff, 0 -5px 0 #fff, 4px 4px 0 #fff, -4px 4px 0 #fff, 4px -4px 0 #fff, -4px -4px 0 #fff',
    filter: SHADOW, ...style}}>{text}</div>
);

// a child seen from behind (paper figure), optional raised hand and an opening head lid
const Kid: React.FC<{x: number; y: number; s?: number; shirt: string; hair?: string; hand?: number; lid?: number; girl?: boolean}> = ({x, y, s = 1, shirt, hair = C.hair, hand = 0, lid = 0, girl}) => (
  <div style={{position: 'absolute', left: x, top: y, width: 240 * s, height: 340 * s, filter: SHADOW}}>
    <svg viewBox="0 0 240 340" width={240 * s} height={340 * s} style={{overflow: 'visible'}}>
      {/* raised arm (behind the body) */}
      <g transform={`rotate(${interpolate(hand, [0, 1], [150, 8])} 178 175)`}>
        <rect x={166} y={60} width={26} height={118} rx={13} fill={shirt} /><circle cx={179} cy={58} r={19} fill={C.skin} /></g>
      <path d="M40 340 Q44 190 120 182 Q196 190 200 340 Z" fill={shirt} />
      <circle cx={68} cy={118} r={13} fill={C.skin} /><circle cx={172} cy={118} r={13} fill={C.skin} />
      <ellipse cx={120} cy={118} rx={58} ry={64} fill={hair} />
      {girl && <><circle cx={58} cy={150} r={18} fill={hair} /><circle cx={182} cy={150} r={18} fill={hair} /></>}
      {/* head lid: the top of the hair hinges open */}
      <g transform={`rotate(${-lid * 62} 64 98)`}>
        <path d="M62 100 Q64 52 120 52 Q176 52 178 100 Z" fill={hair} /><path d="M62 100 L178 100" stroke="#000" strokeOpacity=".25" strokeWidth="3" /></g>
      {lid > .05 && <ellipse cx={120} cy={100} rx={54} ry={10 * lid} fill="#5a3b2a" />}
    </svg>
  </div>
);

// a simple paper person facing us (illustrated, not a real person)
const Person: React.FC<{x: number; y: number; s?: number; shirt: string; skin: string; hair: string; flag: string; t: number}> = ({x, y, s = 1, shirt, skin, hair, flag, t}) => (
  <div style={{position: 'absolute', left: x, top: y + Math.sin(t * 2 + x) * 4, width: 200 * s, height: 330 * s, filter: SHADOW}}>
    <svg viewBox="0 0 200 330" width={200 * s} height={330 * s}>
      <path d="M30 330 Q34 180 100 172 Q166 180 170 330 Z" fill={shirt} />
      <circle cx={100} cy={110} r={58} fill={skin} /><path d="M42 104 Q46 44 100 44 Q156 44 158 104 Q130 76 100 80 Q68 78 42 104 Z" fill={hair} />
      <circle cx={80} cy={114} r={6} fill={C.ink} /><circle cx={120} cy={114} r={6} fill={C.ink} /><path d="M84 140 Q100 152 116 140" stroke={C.ink} strokeWidth={5} fill="none" strokeLinecap="round" />
    </svg>
    <div style={{position: 'absolute', left: 70 * s, top: 236 * s, fontSize: 56 * s}}>{flag}</div>
  </div>
);

const Doll: React.FC<{src: string; x: number; y: number; w: number; rot?: number; style?: React.CSSProperties}> = ({src, x, y, w, rot = 0, style}) => (
  <Img src={staticFile(src)} style={{position: 'absolute', left: x, top: y, width: w, transform: `rotate(${rot}deg)`, filter: SHADOW, ...style}} />
);

const Bubble: React.FC<{x: number; y: number; w: number; k: number; children: React.ReactNode; tail?: 'left' | 'right'}> = ({x, y, w, k, children, tail = 'left'}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, transform: `scale(${k})`, transformOrigin: tail === 'left' ? '10% 100%' : '90% 100%', filter: SHADOW}}>
    <div style={{background: C.paper, borderRadius: 40, padding: '22px 30px', fontFamily: PRE, fontWeight: 800, fontSize: 42, color: C.navy, textAlign: 'center', lineHeight: 1.25}}>{children}</div>
    <div style={{position: 'absolute', bottom: -26, [tail]: 60, width: 0, height: 0, borderLeft: '22px solid transparent', borderRight: '22px solid transparent', borderTop: `30px solid ${C.paper}`}} />
  </div>
);

type Cap = {s: number; e: number; text: string};
export const PT_CAPS: Cap[] = [
  {s: 0.3, e: 3, text: 'AI가 다 알려주는 시대,\n우리 아이에게 필요한 건 뭘까요?'},
  {s: 3, e: 8, text: '이제 궁금한 건 AI에게 물으면\n몇 초 만에 답이 나와요'},
  {s: 8, e: 13, text: '책을 찾지 않아도, 검색하지 않아도,\n누군가에게 묻지 않아도요'},
  {s: 13, e: 17, text: '그런데 정말 중요한 건 정답이 아니라,\n어떤 질문을 하느냐예요'},
  {s: 17, e: 22, text: '그림책을 읽으며\n\'너는 어떻게 생각해?\'라고 물으면'},
  {s: 22, e: 27, text: '아이들 머릿속은\n질문과 상상으로 가득 차요'},
  {s: 27, e: 34, text: '다른 나라 사람을 만났을 때도\n내 생각을 내 말로 표현하는 힘'},
  {s: 34, e: 38, text: 'AI는 우리가 쓰는 도구예요.\n생각은 우리 아이가 하는 거고요'},
  {s: 38, e: 42, text: '여러분 아이는 요즘 어떤 질문을 하나요?'},
];
export const PT_SCENES = {hook: [0, 3], ai: [3, 8], cross: [8, 13], turn: [13, 17], cls: [17, 27], world: [27, 34], msg: [34, 38], end: [38, 42]};

export const PaperThink: React.FC = () => {
  useFonts();
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const t = frame / fps;
  const S = PT_SCENES; const inS = (k: keyof typeof S) => t >= S[k][0] && t < S[k][1];
  const lt = (k: keyof typeof S) => t - S[k][0];
  const cap = PT_CAPS.find((c) => t >= c.s && t < c.e);
  const drift = Math.sin(t * .6) * 8;
  return (
    <AbsoluteFill style={{background: C.kraft, overflow: 'hidden'}}>
      {/* HOOK: a child's head opens and question marks burst out */}
      {inS('hook') && (() => { const l = lt('hook'); const lid = interpolate(l, [.5, 1.1], [0, 1], clamp);
        return <AbsoluteFill style={{background: C.red}}>
          <Sheet x={-30} y={1180} w={1140} h={800} color={C.kraftD} seed={11} />
          <Kid x={250} y={760 + drift} s={2.4} shirt={C.blue} lid={lid} />
          {['?', '?', '!', '?', '?', '?', '?'].map((q, i) => { const k = sp(t, .9 + i * .1, fps, 11); const ang = (200 + i * 23) * Math.PI / 180;
            return <CutText key={i} text={q} size={120 + (i % 3) * 34} color={i % 2 ? C.yellow : C.paper}
              style={{position: 'absolute', left: 540 + Math.cos(ang) * 400 * k - 50, top: 860 + Math.sin(ang) * 300 * k - 90,
                transform: `rotate(${(i - 3) * 9}deg) scale(${k})`}} />; })}
          <Sheet x={70} y={330} w={940} h={250} color={C.paper} seed={5} rot={-1.5}>
            <div style={{padding: '34px 40px', fontFamily: PRE, fontWeight: 900, fontSize: 64, lineHeight: 1.18, color: C.navy, textAlign: 'center'}}>
              AI가 다 알려주는 시대,<br /><span style={{color: C.red}}>우리 아이에게 필요한 힘은?</span></div></Sheet>
        </AbsoluteFill>; })()}

      {/* AI: a paper laptop pours out answer slips */}
      {inS('ai') && (() => { const l = lt('ai'); const typed = '공룡은 왜 사라졌어?'; const n = Math.floor(interpolate(l, [.3, 1.6], [0, typed.length], clamp));
        return <AbsoluteFill style={{background: C.cream}}>
          <Sheet x={180} y={420 + drift} w={720} h={470} color={C.navy} seed={21}>
            <div style={{position: 'absolute', left: 36, top: 36, right: 36, bottom: 36, background: '#EAF2F8', borderRadius: 8, padding: 30}}>
              <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 40, color: C.blue}}>🤖 AI</div>
              <div style={{marginTop: 24, fontFamily: PRE, fontWeight: 800, fontSize: 46, color: C.ink}}>{typed.slice(0, n)}<span style={{opacity: Math.floor(t * 3) % 2}}>|</span></div>
            </div></Sheet>
          <Sheet x={110} y={880 + drift} w={860} h={70} color={C.kraftD} seed={22} />
          {Array.from({length: 14}, (_, i) => { const s0 = 1.8 + i * .17; const p = interpolate(l, [s0, s0 + .9], [0, 1], clamp); const r = rng(i + 3);
            const xx = 220 + r() * 600; const yy = interpolate(p, [0, 1], [700, 1000 + r() * 380]);
            return p > 0 && <Sheet key={i} x={xx} y={yy} w={190} h={110} color={C.paper} seed={30 + i} rot={-25 + r() * 50}>
              <div style={{padding: '18px 20px'}}>{[0, 1, 2].map((j) => <div key={j} style={{height: 8, background: '#B8B0A0', borderRadius: 4, marginBottom: 14, width: `${90 - j * 20}%`}} />)}</div></Sheet>; })}
          <CutText text="⚡ 3초" size={70} color={C.red} style={{position: 'absolute', left: 760, top: 330, transform: `rotate(8deg) scale(${sp(t, S.ai[0] + 1.8, fps)})`}} />
        </AbsoluteFill>; })()}

      {/* CROSS: books, search and asking someone get crossed out */}
      {inS('cross') && (() => { const l = lt('cross');
        const items: [string, string][] = [['📚', '책 찾기'], ['🔍', '검색하기'], ['🙋', '누군가에게 묻기']];
        return <AbsoluteFill style={{background: C.cream}}>
          {items.map(([e, w], i) => { const k = sp(t, S.cross[0] + i * .5, fps); const x0 = 120; const y0 = 380 + i * 310;
            const xp = interpolate(l, [1.6 + i * 1.1, 2.2 + i * 1.1], [0, 1], clamp);
            return <div key={i} style={{position: 'absolute', left: x0, top: y0, width: 840, height: 270, transform: `scale(${k}) rotate(${i % 2 ? 1.5 : -1.5}deg)`}}>
              <Sheet x={0} y={0} w={840} h={260} color={i === 1 ? '#EAF2F8' : C.paper} seed={40 + i}>
                <div style={{display: 'flex', alignItems: 'center', height: 260, padding: '0 50px', gap: 40}}>
                  <span style={{fontSize: 130}}>{e}</span><span style={{fontFamily: PRE, fontWeight: 900, fontSize: 70, color: C.navy}}>{w}</span></div></Sheet>
              <svg width={840} height={270} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
                <Draw d="M60 40 L780 230" p={xp} color={C.red} w={16} /><Draw d="M780 40 L60 230" p={interpolate(xp, [.4, 1], [0, 1], clamp)} color={C.red} w={16} /></svg>
            </div>; })}
        </AbsoluteFill>; })()}

      {/* TURN: the answers blow away, one big question mark stays */}
      {inS('turn') && (() => { const l = lt('turn'); const k = sp(t, S.turn[0] + .5, fps, 10);
        return <AbsoluteFill style={{background: C.navy}}>
          {Array.from({length: 10}, (_, i) => { const r = rng(i + 50); const p = interpolate(l, [0, 1.4], [0, 1], clamp);
            return <Sheet key={i} x={100 + r() * 800 - p * 700} y={300 + r() * 1100 - p * 600} w={170} h={100} color={C.paper} seed={60 + i} rot={r() * 60 - 30 + p * 90}
              style={{opacity: 1 - p}} />; })}
          <CutText text="?" size={760} color={C.yellow} style={{position: 'absolute', left: 300, top: 420, transform: `scale(${k}) rotate(${-6 + Math.sin(t * 1.5) * 3}deg)`}} />
          <Sheet x={140} y={330} w={800} h={130} color={C.paper} seed={70} rot={-2} style={{opacity: interpolate(l, [1.2, 1.6], [0, 1], clamp)}}>
            <div style={{textAlign: 'center', lineHeight: '130px', fontFamily: PRE, fontWeight: 900, fontSize: 58, color: C.navy}}>정답보다 <span style={{color: C.red}}>질문</span></div></Sheet>
        </AbsoluteFill>; })()}

      {/* CLASS: Joy and Mark read a picture book, the children raise their hands and their heads fill with ideas */}
      {inS('cls') && (() => { const l = lt('cls');
        const kids = [{x: 30, shirt: C.yellow, girl: true}, {x: 280, shirt: C.green}, {x: 540, shirt: C.pink, girl: true}, {x: 790, shirt: C.blue}];
        const ideas = ['🐻', '🚀', '🌊', '🦋'];
        return <AbsoluteFill style={{background: '#8FB3C9'}}>
          <Sheet x={-20} y={1150} w={1120} h={800} color={C.kraftD} seed={80} />
          <Sheet x={330} y={330} w={420} h={170} color="#2F4A3C" seed={81} rot={-1}>
            <div style={{fontFamily: HAND, fontWeight: 700, fontSize: 44, color: '#F2EEDC', textAlign: 'center', paddingTop: 30, lineHeight: 1.1}}>What happens<br />next?</div></Sheet>
          <Doll src="paper/joy.png" x={-40} y={520 + drift * .5} w={470} rot={-2} />
          <Doll src="paper/mark.png" x={640} y={520 - drift * .5} w={480} rot={2} />
          <div style={{position: 'absolute', left: 390, top: 820, width: 300, height: 200, filter: SHADOW, transform: 'rotate(-3deg)'}}>
            <div style={{position: 'absolute', left: 0, top: 0, width: 150, height: 200, background: C.paper, borderRadius: '8px 0 0 8px'}} />
            <div style={{position: 'absolute', left: 150, top: 0, width: 150, height: 200, background: C.paper, borderRadius: '0 8px 8px 0', borderLeft: '2px solid #ddd'}} />
            <Img src={staticFile('brand/bear-butterfly.png')} style={{position: 'absolute', left: 170, top: 30, width: 110}} /></div>
          {l > .5 && l < 5 && <Bubble x={560} y={410} w={480} k={sp(t, S.cls[0] + .6, fps)} tail="right">What do you think<br />happens next?</Bubble>}
          {kids.map((kd, i) => { const hs = S.cls[0] + 2.2 + i * .7; const hand = sp(t, hs, fps, 10); const think = sp(t, hs + 3.2, fps, 12);
            return <React.Fragment key={i}>
              <Kid x={kd.x} y={1110} s={1.05} shirt={kd.shirt} girl={kd.girl} hand={hand} />
              {think > .02 && <div style={{position: 'absolute', left: kd.x + 20, top: 890, width: 220, height: 190, transform: `scale(${think})`, transformOrigin: '50% 100%', filter: SHADOW}}>
                <svg width={220} height={190}><ellipse cx={110} cy={80} rx={100} ry={72} fill={C.paper} /><circle cx={70} cy={170} r={12} fill={C.paper} /><circle cx={92} cy={150} r={18} fill={C.paper} />
                  <Gear x={50} y={60} r={20} a={t * 120} /><Gear x={82} y={92} r={14} a={-t * 160} color={C.red} /></svg>
                <div style={{position: 'absolute', left: 110, top: 30, fontSize: 80}}>{ideas[i]}</div></div>}
            </React.Fragment>; })}
        </AbsoluteFill>; })()}

      {/* WORLD: Joy takes off the AI glasses and speaks for herself */}
      {inS('world') && (() => { const l = lt('world'); const off = interpolate(l, [2.2, 3.2], [0, 1], clamp);
        const people = [{x: 560, y: 690, shirt: C.green, skin: '#8D5A3B', hair: '#1D1612', flag: '🇰🇪'}, {x: 800, y: 660, shirt: C.red, skin: '#F1CDB0', hair: '#C99A4A', flag: '🇫🇷'},
          {x: 680, y: 900, shirt: C.yellow, skin: '#D9A77F', hair: '#2A1E16', flag: '🇧🇷'}];
        const W = 560; const sc = W / 1125;   // joy.png is 1125 px wide; her eyes are at about (690, 282)
        const gx = -60 + 690 * sc, gy = 640 + 282 * sc;
        return <AbsoluteFill style={{background: '#E9DFC9'}}>
          {['🇬🇧', '🇺🇸', '🇯🇵', '🇰🇷', '🇫🇷', '🇧🇷', '🇰🇪', '🇮🇳'].map((f, i) => (
            <div key={i} style={{position: 'absolute', left: 40 + i * 128, top: 320 + Math.sin(i * 1.3) * 14, fontSize: 70, transform: `rotate(${Math.sin(t * 2 + i) * 6}deg)`, filter: SHADOW}}>{f}</div>))}
          <svg width={1080} height={420} style={{position: 'absolute', top: 300}}><Draw d="M0 30 Q540 120 1080 30" p={1} w={4} /></svg>
          <Sheet x={-20} y={1180} w={1120} h={760} color={C.kraftD} seed={90} />
          {people.map((p, i) => <Person key={i} {...p} s={1.05} t={t} />)}
          <Doll src="paper/joy.png" x={-60} y={640} w={W} rot={-1} />
          <div style={{position: 'absolute', left: gx - 150 + off * 260, top: gy - 50 - off * 420, transform: `rotate(${off * 35}deg)`, filter: SHADOW}}>
            <svg width={300} height={100}><rect x={10} y={20} width={120} height={62} rx={26} fill="#9FD3F2" fillOpacity=".85" stroke={C.ink} strokeWidth={8} />
              <rect x={170} y={20} width={120} height={62} rx={26} fill="#9FD3F2" fillOpacity=".85" stroke={C.ink} strokeWidth={8} /><path d="M130 45 Q150 30 170 45" stroke={C.ink} strokeWidth={8} fill="none" /></svg>
            <div style={{position: 'absolute', left: 112, top: -34, fontFamily: PRE, fontWeight: 900, fontSize: 30, color: '#fff', background: C.blue, borderRadius: 8, padding: '0 10px'}}>AI</div></div>
          {off > .9 && <Bubble x={330} y={470} w={420} k={sp(t, S.world[0] + 3.3, fps)}>I think…<div style={{fontSize: 32, color: C.red}}>내 생각은요!</div></Bubble>}
        </AbsoluteFill>; })()}

      {/* MESSAGE */}
      {inS('msg') && (() => { const k = sp(t, S.msg[0] + .2, fps);
        return <AbsoluteFill style={{background: C.navy}}>
          <Sheet x={90} y={560} w={900} h={560} color={C.cream} seed={100} rot={-1.5} style={{transform: `rotate(-1.5deg) scale(${.9 + .1 * k})`, opacity: k}}>
            <div style={{padding: '80px 60px', textAlign: 'center', fontFamily: PRE, fontWeight: 900, fontSize: 76, lineHeight: 1.3, color: C.navy}}>
              AI는 <span style={{background: C.yellow, padding: '0 10px'}}>쓰는 것</span>,<br />생각은 <span style={{color: C.red}}>내가</span> 하는 것</div>
            <div style={{position: 'absolute', bottom: 60, left: 0, right: 0, textAlign: 'center', fontFamily: HAND, fontWeight: 700, fontSize: 44, color: C.kraftD}}>질문하는 아이, 생각을 말하는 아이</div></Sheet>
        </AbsoluteFill>; })()}

      {/* END */}
      {t >= S.end[0] && (() => { const k = sp(t, S.end[0] + .2, fps);
        return <AbsoluteFill style={{background: C.cream}}>
          <Img src={staticFile('brand/logo-full.png')} style={{position: 'absolute', left: 290, top: 420, width: 500, opacity: k, filter: SHADOW}} />
          <Sheet x={140} y={980} w={800} h={150} color={C.yellow} seed={110} rot={-1.5} style={{opacity: k}}>
            <div style={{textAlign: 'center', lineHeight: '150px', fontFamily: PRE, fontWeight: 900, fontSize: 54, color: C.navy}}>💬 우리 아이 요즘 질문은?</div></Sheet>
          <div style={{position: 'absolute', top: 1180, left: 0, right: 0, textAlign: 'center', fontFamily: PRE, fontWeight: 800, fontSize: 40, color: C.navy, opacity: k}}>@thebearandjoy 팔로우</div>
        </AbsoluteFill>; })()}

      <Grain />
      {cap && !inS('msg') && !inS('end') && (
        <div style={{position: 'absolute', left: 70, right: 70, top: 1300, display: 'flex', justifyContent: 'center'}}>
          <div style={{background: 'rgba(25,22,20,.82)', borderRadius: 14, padding: '14px 26px', fontFamily: PRE, fontWeight: 800, fontSize: 42, lineHeight: 1.3, color: '#fff', textAlign: 'center', whiteSpace: 'pre-line'}}>{cap.text}</div>
        </div>)}
    </AbsoluteFill>
  );
};
