// "AI 시대, 질문하는 아이" (Joy, 24 Nov 2026): paper-craft diorama reel made on this Mac (no AI images).
// Look (Joy's reference): crumpled kraft and coloured paper with white fibre edges, layered cut-outs with soft shadows, a lit
// school classroom diorama, people made of paper (clothes with newsprint/halftone texture) wearing Joy's and Mark's real faces
// (brand avatars, printed-paper look: projects/2026-11-ai-question/face_doll.py; no microphones). Children are seen from behind.
// Textures: projects/2026-11-ai-question/textures.py. Captions: plain square box. All text inside y 300–1450.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const C = {kraft: '#C9A47A', kraftD: '#A47B52', cream: '#F4EDDC', paper: '#FBF7EC', navy: '#1E2D4D', yellow: '#FFD24A', red: '#D44A30', ink: '#262320',
  skin: '#EDBE98', hair: '#2B211B', blue: '#4F7FAF', green: '#5E9460', pink: '#E58FA0', wall: '#DDE2C6', board: '#2E4A3B', wood: '#8A5A35'};
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
const SHADOW = 'drop-shadow(0 12px 16px rgba(35,20,8,.38)) drop-shadow(0 2px 3px rgba(35,20,8,.35))';
const TEX = {crumple: staticFile('paper/tex-crumple.png'), news: staticFile('paper/tex-news.png'), fibre: staticFile('paper/tex-fibre.png')};

// torn outline in px, as a CSS polygon()
const tornPoly = (w: number, h: number, seed: number, j = 8, step = 22) => {
  const r = rng(seed); const pts: string[] = [];
  for (let x = 0; x <= w; x += step) pts.push(`${x}px ${r() * j}px`);
  for (let y = 0; y <= h; y += step) pts.push(`${w - r() * j}px ${y}px`);
  for (let x = w; x >= 0; x -= step) pts.push(`${x}px ${h - r() * j}px`);
  for (let y = h; y >= 0; y -= step) pts.push(`${r() * j}px ${y}px`);
  return `polygon(${pts.join(',')})`;
};
// a sheet of crumpled paper with a white fibre edge where it was torn
const Sheet: React.FC<{x: number; y: number; w: number; h: number; color?: string; seed?: number; rot?: number; tex?: 'crumple' | 'news' | 'fibre'; edge?: boolean;
  style?: React.CSSProperties; children?: React.ReactNode}> = ({x, y, w, h, color = C.paper, seed = 3, rot = 0, tex = 'crumple', edge = true, style, children}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, transform: `rotate(${rot}deg)`, filter: SHADOW, ...style}}>
    {edge && <div style={{position: 'absolute', left: -5, top: -5, width: w + 10, height: h + 10, background: '#F6F1E6', clipPath: tornPoly(w + 10, h + 10, seed + 500, 11)}} />}
    <div style={{position: 'absolute', inset: 0, clipPath: tornPoly(w, h, seed), background: color}}>
      <div style={{position: 'absolute', inset: 0, backgroundImage: `url(${TEX[tex]})`, backgroundSize: tex === 'news' ? '420px' : '520px', mixBlendMode: tex === 'news' ? 'multiply' : 'overlay',
        opacity: tex === 'news' ? .35 : .9}} />
    </div>
    <div style={{position: 'absolute', inset: 0}}>{children}</div>
  </div>
);

// SVG pattern defs: paper textures inside drawn figures
const Defs: React.FC<{id: string}> = ({id}) => (
  <defs>
    <pattern id={`cr${id}`} patternUnits="userSpaceOnUse" width="260" height="260"><image href={TEX.crumple} width="260" height="260" /></pattern>
    <pattern id={`nw${id}`} patternUnits="userSpaceOnUse" width="220" height="220"><image href={TEX.news} width="220" height="220" /></pattern>
  </defs>
);
// a filled paper shape: colour + crumple light + optional newsprint
const P: React.FC<{d: string; fill: string; id: string; news?: boolean; stroke?: boolean}> = ({d, fill, id, news, stroke}) => (
  <g style={{filter: 'drop-shadow(2px 4px 2px rgba(30,15,5,.38))'}}><path d={d} fill={fill} stroke={stroke ? 'rgba(0,0,0,.18)' : undefined} strokeWidth={stroke ? 2 : undefined} />
    <path d={d} fill={`url(#cr${id})`} style={{mixBlendMode: 'overlay'}} opacity={.85} />
    {news && <path d={d} fill={`url(#nw${id})`} style={{mixBlendMode: 'multiply'}} opacity={.28} />}</g>
);

const Grain: React.FC = () => (
  <AbsoluteFill style={{mixBlendMode: 'multiply', opacity: .25, pointerEvents: 'none'}}>
    <svg width="1080" height="1920"><filter id="g"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4" /><feColorMatrix values="0 0 0 0 .55  0 0 0 0 .5  0 0 0 0 .45  0 0 0 -1.1 1.05" /></filter>
      <rect width="1080" height="1920" filter="url(#g)" /></svg>
  </AbsoluteFill>
);
const Vignette: React.FC<{k?: number}> = ({k = .55}) => <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 45%, rgba(20,10,0,${k}) 100%)`, pointerEvents: 'none'}} />;

const Draw: React.FC<{d: string; p: number; color?: string; w?: number}> = ({d, p, color = C.ink, w = 7}) => (
  <path d={d} fill="none" stroke={color} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
);
const Gear: React.FC<{x: number; y: number; r: number; a: number; color?: string}> = ({x, y, r, a, color = C.yellow}) => (
  <g transform={`translate(${x} ${y}) rotate(${a})`}>
    {Array.from({length: 10}, (_, i) => <rect key={i} x={-r * .18} y={-r * 1.22} width={r * .36} height={r * .4} rx={3} fill={color} transform={`rotate(${i * 36})`} />)}
    <circle r={r} fill={color} /><circle r={r * .38} fill={C.kraftD} /></g>
);
const CutText: React.FC<{text: string; size: number; color: string; style?: React.CSSProperties}> = ({text, size, color, style}) => (
  <div style={{fontFamily: PRE, fontWeight: 900, fontSize: size, color, lineHeight: 1,
    textShadow: '5px 0 0 #F6F1E6, -5px 0 0 #F6F1E6, 0 5px 0 #F6F1E6, 0 -5px 0 #F6F1E6, 4px 4px 0 #F6F1E6, -4px 4px 0 #F6F1E6, 4px -4px 0 #F6F1E6, -4px -4px 0 #F6F1E6',
    filter: SHADOW, ...style}}>{text}</div>
);

// ---------- the classroom diorama ----------
const Classroom: React.FC<{t: number; board?: React.ReactNode}> = ({t, board}) => {
  const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
  return <AbsoluteFill>
    <Sheet x={-30} y={-30} w={1140} h={1240} color={C.wall} seed={1} edge={false} />
    {/* wainscot + floor planks */}
    <Sheet x={-20} y={1000} w={1120} h={200} color="#B98A5E" seed={2} />
    <Sheet x={-30} y={1170} w={1140} h={800} color="#9C6F47" seed={3}>
      {Array.from({length: 7}, (_, i) => <div key={i} style={{position: 'absolute', left: 0, right: 0, top: 70 + i * 105, height: 3, background: 'rgba(60,35,15,.35)'}} />)}</Sheet>
    {/* hanging lamp with warm light */}
    <div style={{position: 'absolute', left: 539, top: 0, width: 2, height: 170, background: '#333'}} />
    <svg width={200} height={110} style={{position: 'absolute', left: 440, top: 160, filter: SHADOW}}><path d="M20 90 Q100 -10 180 90 Z" fill="#E9E1CF" /><ellipse cx={100} cy={92} rx={28} ry={12} fill="#FFE58A" /></svg>
    <AbsoluteFill style={{background: 'radial-gradient(ellipse 520px 700px at 540px 330px, rgba(255,220,140,.35), rgba(255,220,140,0) 70%)', pointerEvents: 'none'}} />
    {/* alphabet bunting */}
    <svg width={1080} height={120} style={{position: 'absolute', top: 290}}><path d="M0 20 Q540 90 1080 20" stroke="#5a4636" strokeWidth={3} fill="none" /></svg>
    {letters.map((l, i) => { const x = 60 + i * 125; const y = 300 + Math.sin((x / 1080) * Math.PI) * 35;
      return <Sheet key={l} x={x} y={y + Math.sin(t * 2 + i) * 3} w={80} h={96} color={[C.red, C.yellow, C.blue, C.green][i % 4]} seed={20 + i} rot={Math.sin(t * 1.5 + i) * 4}
        style={{clipPath: 'polygon(0 0, 100% 0, 50% 100%)'}}><div style={{textAlign: 'center', paddingTop: 6, fontFamily: HAND, fontWeight: 700, fontSize: 40, color: '#fff'}}>{l}</div></Sheet>; })}
    {/* window with sky */}
    <Sheet x={30} y={450} w={190} h={330} color="#F2EBDB" seed={30}>
      <div style={{position: 'absolute', left: 16, top: 16, right: 16, bottom: 16, background: 'linear-gradient(#9FC6E4, #CFE3F1)', overflow: 'hidden'}}>
        <div style={{position: 'absolute', left: 20 + Math.sin(t * .3) * 10, top: 60, width: 90, height: 34, borderRadius: 20, background: '#fff'}} />
        <div style={{position: 'absolute', left: 0, right: 0, top: '50%', height: 10, background: '#F2EBDB'}} /><div style={{position: 'absolute', top: 0, bottom: 0, left: '50%', width: 10, background: '#F2EBDB'}} /></div></Sheet>
    {/* chalkboard */}
    <Sheet x={250} y={440} w={580} h={330} color={C.wood} seed={40}>
      <div style={{position: 'absolute', left: 18, top: 18, right: 18, bottom: 18, background: C.board}}>
        <div style={{position: 'absolute', inset: 0, backgroundImage: `url(${TEX.crumple})`, backgroundSize: '400px', mixBlendMode: 'overlay', opacity: .6}} />{board}</div></Sheet>
    {/* clock */}
    <div style={{position: 'absolute', left: 900, top: 430, width: 130, height: 130, borderRadius: '50%', background: '#FBF7EC', border: `10px solid ${C.red}`, filter: SHADOW}}>
      <div style={{position: 'absolute', left: 54, top: 18, width: 6, height: 42, background: C.ink, transformOrigin: '50% 100%', transform: `rotate(${t * 30}deg)`}} />
      <div style={{position: 'absolute', left: 54, top: 30, width: 6, height: 30, background: C.ink, transformOrigin: '50% 100%', transform: 'rotate(110deg)'}} /></div>
    {/* bookshelf */}
    <Sheet x={870} y={600} w={190} h={400} color={C.wood} seed={50}>
      {[0, 1, 2].map((r) => <div key={r} style={{position: 'absolute', left: 14, right: 14, top: 18 + r * 125, height: 105, display: 'flex', alignItems: 'flex-end', gap: 4}}>
        {Array.from({length: 6}, (_, i) => <div key={i} style={{width: 20, height: 70 + ((i * 37 + r * 13) % 30), background: [C.red, C.yellow, C.blue, C.green, C.pink, C.cream][(i + r) % 6], borderRadius: 2}} />)}</div>)}</Sheet>
    {/* children's drawings pinned on the wall */}
    {[['☀️', 40, 820, -5], ['🏠', 150, 840, 4]].map(([e, x, y, r], i) => (
      <Sheet key={i} x={x as number} y={y as number} w={110} h={130} color="#FFFDF6" seed={60 + i} rot={r as number}><div style={{textAlign: 'center', fontSize: 64, paddingTop: 22}}>{e as string}</div>
        <div style={{position: 'absolute', left: 45, top: -6, width: 18, height: 18, borderRadius: '50%', background: C.red}} /></Sheet>))}
  </AbsoluteFill>;
};

// ---------- a child seen from behind, in paper ----------
type Hair = 'short' | 'long' | 'pigtails' | 'bob';
const Kid: React.FC<{x: number; y: number; s?: number; shirt: string; hair?: string; style?: Hair; hand?: number; lid?: number; id: string; skin?: string}> =
  ({x, y, s = 1, shirt, hair = C.hair, style = 'short', hand = 0, lid = 0, id, skin = C.skin}) => {
  const arm = interpolate(hand, [0, 1], [165, 12]);
  return <div style={{position: 'absolute', left: x, top: y, width: 300 * s, height: 460 * s, filter: SHADOW}}>
    <svg viewBox="0 0 300 460" width={300 * s} height={460 * s} style={{overflow: 'visible'}}><Defs id={id} />
      {/* raised arm: sleeve + forearm + hand with fingers */}
      {hand > .04 && <g transform={`rotate(${arm} 222 282)`}>
        <P id={id} d="M206 282 L238 282 L236 200 L208 200 Z" fill={shirt} news />
        <P id={id} d="M210 204 L234 204 L232 128 L212 128 Z" fill={skin} />
        <P id={id} d="M204 132 Q204 104 222 102 Q240 104 240 132 Z" fill={skin} />
        {[0, 1, 2, 3].map((f) => <rect key={f} x={205 + f * 8.5} y={78 + Math.abs(f - 1.5) * 5} width={7.5} height={30} rx={4} fill={skin} />)}
        <rect x={238} y={110} width={8} height={22} rx={4} fill={skin} transform="rotate(30 242 120)" /></g>}
      {/* torso with shoulders, sleeves and folds */}
      <P id={id} d="M38 460 L46 330 Q52 276 110 262 Q150 256 190 262 Q248 276 254 330 L262 460 Z" fill={shirt} news stroke />
      <path d="M100 300 Q96 380 104 460 M200 300 Q206 380 196 460" stroke="rgba(0,0,0,.14)" strokeWidth={4} fill="none" />
      <P id={id} d="M118 262 Q150 280 182 262 L178 252 Q150 266 122 252 Z" fill="#F3EEE2" />
      {/* neck, ears, head */}
      <P id={id} d="M130 262 L130 222 L170 222 L170 262 Z" fill={skin} />
      {style === 'long' && <P id={id} d="M78 150 Q70 260 92 318 L208 318 Q230 260 222 150 Z" fill={hair} />}
      {style === 'pigtails' && <><P id={id} d="M70 170 Q40 230 66 290 Q86 250 84 180 Z" fill={hair} /><P id={id} d="M230 170 Q260 230 234 290 Q214 250 216 180 Z" fill={hair} />
        <circle cx={78} cy={182} r={9} fill={C.red} /><circle cx={222} cy={182} r={9} fill={C.red} /></>}
      <ellipse cx={82} cy={160} rx={12} ry={19} fill={skin} /><ellipse cx={218} cy={160} rx={12} ry={19} fill={skin} />
      <P id={id} d={style === 'bob' ? 'M78 150 Q76 60 150 58 Q224 60 222 150 Q226 210 214 236 L86 236 Q74 210 78 150 Z' :
        style === 'short' ? 'M84 150 Q80 64 150 62 Q220 64 216 150 Q216 200 196 228 Q150 214 104 228 Q84 200 84 150 Z' :
        'M82 150 Q78 62 150 60 Q222 62 218 150 Q218 206 204 232 Q150 220 96 232 Q82 206 82 150 Z'} fill={hair} />
      {/* hair strands */}
      <path d="M110 80 Q104 150 112 222 M134 66 Q128 150 134 220 M160 64 Q166 150 160 218 M186 74 Q194 150 188 224" stroke="rgba(255,255,255,.12)" strokeWidth={4} fill="none" />
      <path d="M122 72 Q116 150 122 222 M172 68 Q180 150 174 222" stroke="rgba(0,0,0,.25)" strokeWidth={3} fill="none" />
      {style === 'short' && <path d="M112 226 Q150 236 188 226 L188 236 Q150 246 112 236 Z" fill={skin} opacity={.0} />}
      {/* head lid for the hook: the crown hinges open */}
      {lid > 0 && <g transform={`rotate(${-lid * 70} 80 120)`}><P id={id} d="M80 120 Q82 56 150 56 Q218 56 220 120 Z" fill={hair} /></g>}
      {lid > .05 && <ellipse cx={150} cy={121} rx={68} ry={12 * lid} fill="#4a2e20" />}
    </svg>
  </div>;
};

// ---------- Joy and Mark: paper bodies with their real (printed) faces ----------
const Teacher: React.FC<{who: 'joy' | 'mark'; x: number; y: number; s?: number; book?: boolean; rot?: number; glasses?: number}> = ({who, x, y, s = 1, book, rot = 0, glasses = 0}) => {
  const joy = who === 'joy'; const id = `t${who}`;
  const jacket = joy ? '#34343C' : '#CFC3AE'; const shirt = joy ? '#26262B' : '#EEF1F4';
  // face image: joy-head 822x840 (eyes ~ .37,.555, tilted -24°), mark-head 807x857 (eyes ~ .52,.43)
  const hw = joy ? 215 : 185; const hh = joy ? hw * 832 / 813 : hw * 849 / 671;
  return <div style={{position: 'absolute', left: x, top: y, width: 420 * s, height: 1400 * s, transform: `rotate(${rot}deg)`, filter: SHADOW}}>
    <div style={{position: 'absolute', left: 0, top: 0, width: 420, height: 1400, transform: `scale(${s})`, transformOrigin: '0 0'}}>
      {joy && <svg width={420} height={1400} style={{position: 'absolute', left: 0, top: 0}}><Defs id={id + 'h'} />
        <P id={id + 'h'} d="M108 90 Q100 6 212 2 Q326 6 318 100 Q342 250 318 340 L104 340 Q80 250 108 90 Z" fill={C.hair} /></svg>}
      <svg width={420} height={1400} style={{position: 'absolute', left: 0, top: 0}}><Defs id={id} /><g transform="translate(0 -108)">
        {/* neck */}
        <P id={id} d="M180 270 L240 270 L240 330 L180 330 Z" fill={C.skin} />
        {/* body */}
        <P id={id} d="M40 870 L52 420 Q62 350 140 330 L280 330 Q358 350 368 420 L380 870 Z" fill={jacket} news stroke />
        {joy ? <><P id={id} d="M150 330 L270 330 L238 470 L182 470 Z" fill="#E4DED2" />
          <P id={id} d="M140 332 L184 336 L206 640 L176 640 Z" fill="#45454E" news /><P id={id} d="M280 332 L236 336 L214 640 L244 640 Z" fill="#45454E" news />
          <P id={id} d="M78 600 L150 600 L150 640 L78 640 Z" fill="#2A2A30" /><P id={id} d="M270 600 L342 600 L342 640 L270 640 Z" fill="#2A2A30" /></> : <>
          <P id={id} d="M168 330 L252 330 L246 560 L174 560 Z" fill={shirt} />
          <P id={id} d="M200 340 L220 340 L226 470 L210 500 L194 470 Z" fill="#22314F" news />
          <P id={id} d="M140 332 L196 340 L186 460 Z" fill="#BDB09A" /><P id={id} d="M280 332 L224 340 L234 460 Z" fill="#BDB09A" /></>}
        {joy && [0, 1, 2].map((b) => <circle key={b} cx={228} cy={500 + b * 60} r={7} fill="#15151A" />)}
        {!joy && <><P id={id} d="M80 610 L150 610 L150 646 L80 646 Z" fill="#BDB09A" /><P id={id} d="M270 610 L340 610 L340 646 L270 646 Z" fill="#BDB09A" />
          <P id={id} d="M290 420 L330 420 L330 436 L290 436 Z" fill="#BDB09A" /></>}
        {/* arms holding a book, or resting */}
        {book ? <>
          <P id={id} d="M58 430 Q40 560 120 600 L200 590 L196 548 L130 540 Q110 500 116 440 Z" fill={jacket} news />
          <P id={id} d="M362 430 Q380 560 300 600 L220 590 L224 548 L290 540 Q310 500 304 440 Z" fill={jacket} news />
          <g transform="translate(110 470) rotate(-4)">
            <rect x={0} y={0} width={100} height={130} fill="#FBF7EC" /><rect x={100} y={0} width={100} height={130} fill="#F4EEDF" />
            <rect x={-6} y={-6} width={212} height={142} fill="none" stroke="#7B5A3A" strokeWidth={6} />
            <image href={staticFile('brand/bear-butterfly.png')} x={112} y={16} width={78} height={100} />
            {[0, 1, 2, 3].map((l) => <rect key={l} x={12} y={22 + l * 22} width={70 - l * 8} height={6} fill="#B8AE9C" />)}</g>
          <ellipse cx={118} cy={598} rx={22} ry={18} fill={C.skin} /><ellipse cx={302} cy={598} rx={22} ry={18} fill={C.skin} /></> : <>
          <P id={id} d="M56 426 Q30 560 70 660 Q120 700 196 690 L196 650 Q128 650 110 620 Q100 540 118 440 Z" fill={jacket} news />
          <P id={id} d="M364 426 Q390 560 350 660 Q300 700 224 690 L224 650 Q292 650 310 620 Q320 540 302 440 Z" fill={jacket} news />
          <P id={id} d="M184 646 L204 646 L204 696 L184 696 Z" fill={shirt === '#EEF1F4' ? shirt : '#E4DED2'} />
          <ellipse cx={206} cy={676} rx={30} ry={24} fill={C.skin} /><ellipse cx={226} cy={668} rx={26} ry={22} fill="#E3B08A" /></>}
        <P id={id} d="M84 860 L204 860 L196 1290 L102 1290 Z" fill={joy ? '#1C1C20' : '#2C3A55'} news />
        <P id={id} d="M216 860 L336 860 L318 1290 L224 1290 Z" fill={joy ? '#1C1C20' : '#2C3A55'} news />
        <ellipse cx={142} cy={1296} rx={62} ry={22} fill="#141414" /><ellipse cx={278} cy={1296} rx={62} ry={22} fill="#141414" /></g>
      </svg>
      <Img src={staticFile(`paper/${who}-head.png`)} style={{position: 'absolute', left: 210 - hw / 2 + (joy ? 6 : 0), top: joy ? 14 : 4, width: hw, height: hh, filter: 'drop-shadow(2px 5px 3px rgba(30,15,5,.4))'}} />
      {glasses > 0 && (() => { const gx = joy ? 210 - hw / 2 + 6 + hw * .37 : 210 - hw / 2 + hw * .52; const gy = (joy ? 14 : 4) + hh * (joy ? .555 : .40);
        const off = glasses >= 1 ? 0 : 1 - glasses;   // glasses: 1 = worn, 0..1 = flying off
        return <div style={{position: 'absolute', left: gx - 120 + off * 260, top: gy - 40 - off * 460, transform: `rotate(${(joy ? -24 : 0) + off * 40}deg) scale(.72)`, filter: SHADOW}}>
          <svg width={240} height={84}><rect x={6} y={14} width={98} height={56} rx={22} fill="#9FD3F2" fillOpacity=".8" stroke={C.ink} strokeWidth={8} />
            <rect x={136} y={14} width={98} height={56} rx={22} fill="#9FD3F2" fillOpacity=".8" stroke={C.ink} strokeWidth={8} /><path d="M104 38 Q120 24 136 38" stroke={C.ink} strokeWidth={8} fill="none" /></svg>
          <div style={{position: 'absolute', left: 92, top: -30, fontFamily: PRE, fontWeight: 900, fontSize: 28, color: '#fff', background: C.blue, padding: '0 10px'}}>AI</div></div>; })()}
    </div>
  </div>;
};

// a paper person from another country (illustrated, not a real person)
const Person: React.FC<{x: number; y: number; s?: number; shirt: string; skin: string; hair: string; flag: string; t: number; id: string}> = ({x, y, s = 1, shirt, skin, hair, flag, t, id}) => (
  <div style={{position: 'absolute', left: x, top: y + Math.sin(t * 2 + x) * 4, width: 220 * s, height: 380 * s, filter: SHADOW}}>
    <svg viewBox="0 0 220 380" width={220 * s} height={380 * s}><Defs id={id} />
      <P id={id} d="M24 380 L32 250 Q40 205 110 198 Q180 205 188 250 L196 380 Z" fill={shirt} news stroke />
      <P id={id} d="M94 170 L126 170 L126 204 L94 204 Z" fill={skin} />
      <P id={id} d="M50 112 Q50 46 110 44 Q170 46 170 112 Q170 176 110 182 Q50 176 50 112 Z" fill={skin} />
      <P id={id} d="M46 112 Q40 30 110 28 Q182 30 174 112 Q160 70 110 66 Q62 70 46 112 Z" fill={hair} />
      <ellipse cx={86} cy={118} rx={6} ry={8} fill={C.ink} /><ellipse cx={134} cy={118} rx={6} ry={8} fill={C.ink} />
      <path d="M90 146 Q110 160 130 146" stroke={C.ink} strokeWidth={5} fill="none" strokeLinecap="round" /><ellipse cx={74} cy={138} rx={10} ry={6} fill="#E88" opacity={.35} /><ellipse cx={146} cy={138} rx={10} ry={6} fill="#E88" opacity={.35} /></svg>
    <div style={{position: 'absolute', left: 78 * s, top: 270 * s, fontSize: 56 * s}}>{flag}</div>
  </div>
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
  const drift = Math.sin(t * .6) * 6;
  return (
    <AbsoluteFill style={{background: C.kraft, overflow: 'hidden'}}>
      {/* HOOK: in the classroom, a child's head opens and question marks burst out */}
      {inS('hook') && (() => { const l = lt('hook'); const lid = interpolate(l, [.5, 1.1], [0, 1], clamp);
        return <AbsoluteFill style={{transform: `scale(${1.06 - l * .02})`}}>
          <Classroom t={t} />
          <Kid id="hk" x={210} y={700 + drift} s={2.2} shirt={C.blue} style="short" lid={lid} />
          {['?', '?', '!', '?', '?', '?', '?'].map((q, i) => { const k = sp(t, .9 + i * .1, fps, 11); const ang = (200 + i * 23) * Math.PI / 180;
            return <CutText key={i} text={q} size={120 + (i % 3) * 34} color={i % 2 ? C.yellow : C.red}
              style={{position: 'absolute', left: 540 + Math.cos(ang) * 400 * k - 50, top: 840 + Math.sin(ang) * 280 * k - 90, transform: `rotate(${(i - 3) * 9}deg) scale(${k})`}} />; })}
          <Sheet x={70} y={330} w={940} h={250} color={C.paper} seed={5} rot={-1.5}>
            <div style={{padding: '34px 40px', fontFamily: PRE, fontWeight: 900, fontSize: 64, lineHeight: 1.18, color: C.navy, textAlign: 'center'}}>
              AI가 다 알려주는 시대,<br /><span style={{color: C.red}}>우리 아이에게 필요한 힘은?</span></div></Sheet>
        </AbsoluteFill>; })()}

      {/* AI: a paper laptop pours out answer slips */}
      {inS('ai') && (() => { const l = lt('ai'); const typed = '공룡은 왜 사라졌어?'; const n = Math.floor(interpolate(l, [.3, 1.6], [0, typed.length], clamp));
        return <AbsoluteFill>
          <Sheet x={-30} y={-30} w={1140} h={1980} color={C.cream} seed={7} edge={false} />
          <Sheet x={-30} y={1060} w={1140} h={900} color={C.kraftD} seed={8} />
          <Sheet x={180} y={420 + drift} w={720} h={470} color={C.navy} seed={21}>
            <div style={{position: 'absolute', left: 36, top: 36, right: 36, bottom: 36, background: '#EAF2F8', padding: 30}}>
              <div style={{fontFamily: PRE, fontWeight: 900, fontSize: 40, color: C.blue}}>🤖 AI</div>
              <div style={{marginTop: 24, fontFamily: PRE, fontWeight: 800, fontSize: 46, color: C.ink}}>{typed.slice(0, n)}<span style={{opacity: Math.floor(t * 3) % 2}}>|</span></div>
            </div></Sheet>
          <Sheet x={110} y={880 + drift} w={860} h={70} color="#8E8A84" seed={22} />
          {Array.from({length: 16}, (_, i) => { const s0 = 1.8 + i * .15; const p = interpolate(l, [s0, s0 + .9], [0, 1], clamp); const r = rng(i + 3);
            const xx = 120 + r() * 780; const yy = interpolate(p, [0, 1], [700, 980 + r() * 300]);
            return p > 0 && <Sheet key={i} x={xx} y={yy} w={180} h={110} color={i % 3 ? C.paper : '#FFF6D6'} seed={30 + i} tex="news" rot={-25 + r() * 50} />; })}
          <CutText text="⚡ 3초" size={70} color={C.red} style={{position: 'absolute', left: 760, top: 330, transform: `rotate(8deg) scale(${sp(t, S.ai[0] + 1.8, fps)})`}} />
          <Vignette k={.35} />
        </AbsoluteFill>; })()}

      {/* CROSS: books, search and asking someone get crossed out */}
      {inS('cross') && (() => { const l = lt('cross');
        const items: [string, string][] = [['📚', '책 찾기'], ['🔍', '검색하기'], ['🙋', '누군가에게 묻기']];
        return <AbsoluteFill>
          <Sheet x={-30} y={-30} w={1140} h={1980} color="#E6DCC5" seed={9} edge={false} />
          {items.map(([e, w], i) => { const k = sp(t, S.cross[0] + i * .5, fps); const y0 = 380 + i * 300;
            const xp = interpolate(l, [1.6 + i * 1.1, 2.2 + i * 1.1], [0, 1], clamp);
            return <div key={i} style={{position: 'absolute', left: 120, top: y0, width: 840, height: 260, transform: `scale(${k}) rotate(${i % 2 ? 1.5 : -1.5}deg)`}}>
              <Sheet x={0} y={0} w={840} h={250} color={i === 1 ? '#E3EEF6' : C.paper} seed={40 + i}>
                <div style={{display: 'flex', alignItems: 'center', height: 250, padding: '0 50px', gap: 40}}>
                  <span style={{fontSize: 120}}>{e}</span><span style={{fontFamily: PRE, fontWeight: 900, fontSize: 70, color: C.navy}}>{w}</span></div></Sheet>
              <svg width={840} height={260} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
                <Draw d="M60 40 L780 220" p={xp} color={C.red} w={16} /><Draw d="M780 40 L60 220" p={interpolate(xp, [.4, 1], [0, 1], clamp)} color={C.red} w={16} /></svg>
            </div>; })}
          <Vignette k={.35} />
        </AbsoluteFill>; })()}

      {/* TURN: the answers blow away, one big question mark stays */}
      {inS('turn') && (() => { const l = lt('turn'); const k = sp(t, S.turn[0] + .5, fps, 10);
        return <AbsoluteFill>
          <Sheet x={-30} y={-30} w={1140} h={1980} color={C.navy} seed={10} edge={false} />
          {Array.from({length: 10}, (_, i) => { const r = rng(i + 50); const p = interpolate(l, [0, 1.4], [0, 1], clamp);
            return <Sheet key={i} x={100 + r() * 800 - p * 700} y={300 + r() * 1000 - p * 600} w={170} h={100} color={C.paper} tex="news" seed={60 + i} rot={r() * 60 - 30 + p * 90} style={{opacity: 1 - p}} />; })}
          <CutText text="?" size={760} color={C.yellow} style={{position: 'absolute', left: 300, top: 420, transform: `scale(${k}) rotate(${-6 + Math.sin(t * 1.5) * 3}deg)`}} />
          <Sheet x={140} y={330} w={800} h={130} color={C.paper} seed={70} rot={-2} style={{opacity: interpolate(l, [1.2, 1.6], [0, 1], clamp)}}>
            <div style={{textAlign: 'center', lineHeight: '130px', fontFamily: PRE, fontWeight: 900, fontSize: 58, color: C.navy}}>정답보다 <span style={{color: C.red}}>질문</span></div></Sheet>
          <Vignette k={.5} />
        </AbsoluteFill>; })()}

      {/* CLASS: Joy and Mark read a picture book, the children raise their hands and their heads fill with ideas */}
      {inS('cls') && (() => { const l = lt('cls');
        const kids: {x: number; shirt: string; style: Hair; hair?: string}[] = [{x: -10, shirt: C.yellow, style: 'pigtails'}, {x: 255, shirt: C.green, style: 'short', hair: '#4A3020'},
          {x: 520, shirt: C.pink, style: 'long'}, {x: 785, shirt: C.blue, style: 'bob', hair: '#3A2A20'}];
        const ideas = ['🐻', '🚀', '🌊', '🦋'];
        return <AbsoluteFill>
          <Classroom t={t} board={<div style={{fontFamily: HAND, fontWeight: 700, fontSize: 62, color: '#F2EEDC', textAlign: 'center', paddingTop: 70, lineHeight: 1.15}}>What happens<br />next? 🤔</div>} />
          <Teacher who="joy" x={-30} y={500 + drift * .4} s={1.22} book />
          <Teacher who="mark" x={560} y={470 - drift * .4} s={1.25} />
          {l > .5 && l < 5 && <Bubble x={560} y={400} w={480} k={sp(t, S.cls[0] + .6, fps)} tail="right">What do you think<br />happens next?</Bubble>}
          {kids.map((kd, i) => { const hs = S.cls[0] + 2.2 + i * .7; const hand = sp(t, hs, fps, 10); const think = sp(t, hs + 3.2, fps, 12);
            return <React.Fragment key={i}>
              <Kid id={`k${i}`} x={kd.x} y={1060} s={1} shirt={kd.shirt} style={kd.style} hair={kd.hair} hand={hand} />
              {think > .02 && <div style={{position: 'absolute', left: kd.x + 40, top: 860, width: 230, height: 200, transform: `scale(${think})`, transformOrigin: '50% 100%', filter: SHADOW}}>
                <svg width={230} height={200}><ellipse cx={115} cy={84} rx={104} ry={76} fill={C.paper} /><circle cx={76} cy={180} r={12} fill={C.paper} /><circle cx={96} cy={158} r={18} fill={C.paper} />
                  <Gear x={52} y={62} r={20} a={t * 120} /><Gear x={86} y={96} r={14} a={-t * 160} color={C.red} /></svg>
                <div style={{position: 'absolute', left: 116, top: 30, fontSize: 82}}>{ideas[i]}</div></div>}
            </React.Fragment>; })}
          <Vignette k={.45} />
        </AbsoluteFill>; })()}

      {/* WORLD: Joy takes off the AI glasses and speaks for herself */}
      {inS('world') && (() => { const l = lt('world'); const g = l < 2.2 ? 1 : interpolate(l, [2.2, 3.2], [.999, 0], clamp);
        const people = [{x: 560, y: 640, shirt: C.green, skin: '#8D5A3B', hair: '#1D1612', flag: '🇰🇪'}, {x: 810, y: 610, shirt: C.red, skin: '#F1CDB0', hair: '#C99A4A', flag: '🇫🇷'},
          {x: 690, y: 860, shirt: C.yellow, skin: '#D9A77F', hair: '#2A1E16', flag: '🇧🇷'}];
        return <AbsoluteFill>
          <Sheet x={-30} y={-30} w={1140} h={1300} color="#D7E4EA" seed={12} edge={false} />
          <Sheet x={-30} y={1170} w={1140} h={800} color={C.kraftD} seed={13} />
          {/* paper world map strip */}
          <Sheet x={60} y={430} w={960} h={420} color="#BFD6E2" seed={14} rot={-1}>
            {[[90, 80, 220, 140], [380, 60, 170, 110], [600, 90, 260, 170], [300, 220, 120, 150], [720, 270, 120, 90]].map(([x, y, w, h], i) => (
              <div key={i} style={{position: 'absolute', left: x, top: y, width: w, height: h, background: '#9DBF8E', borderRadius: '40% 55% 45% 60%', opacity: .9}} />))}</Sheet>
          {['🇬🇧', '🇺🇸', '🇯🇵', '🇰🇷', '🇫🇷', '🇧🇷', '🇰🇪', '🇮🇳'].map((f, i) => (
            <div key={i} style={{position: 'absolute', left: 40 + i * 128, top: 320 + Math.sin(i * 1.3) * 14, fontSize: 70, transform: `rotate(${Math.sin(t * 2 + i) * 6}deg)`, filter: SHADOW}}>{f}</div>))}
          <svg width={1080} height={200} style={{position: 'absolute', top: 300}}><path d="M0 30 Q540 120 1080 30" stroke="#5a4636" strokeWidth={3} fill="none" /></svg>
          {people.map((p, i) => <Person key={i} id={`p${i}`} {...p} s={1.05} t={t} />)}
          <Teacher who="joy" x={-70} y={470} s={1.45} glasses={g} />
          {g < .1 && <Bubble x={300} y={430} w={420} k={sp(t, S.world[0] + 3.3, fps)}>I think…<div style={{fontSize: 32, color: C.red}}>내 생각은요!</div></Bubble>}
          <Vignette k={.4} />
        </AbsoluteFill>; })()}

      {/* MESSAGE */}
      {inS('msg') && (() => { const k = sp(t, S.msg[0] + .2, fps);
        return <AbsoluteFill>
          <Sheet x={-30} y={-30} w={1140} h={1980} color={C.navy} seed={15} edge={false} />
          <Sheet x={90} y={560} w={900} h={560} color={C.cream} seed={100} rot={-1.5} style={{transform: `rotate(-1.5deg) scale(${.9 + .1 * k})`, opacity: k}}>
            <div style={{padding: '80px 60px', textAlign: 'center', fontFamily: PRE, fontWeight: 900, fontSize: 76, lineHeight: 1.3, color: C.navy}}>
              AI는 <span style={{background: C.yellow, padding: '0 10px'}}>쓰는 것</span>,<br />생각은 <span style={{color: C.red}}>내가</span> 하는 것</div>
            <div style={{position: 'absolute', bottom: 60, left: 0, right: 0, textAlign: 'center', fontFamily: HAND, fontWeight: 700, fontSize: 44, color: C.kraftD}}>질문하는 아이, 생각을 말하는 아이</div></Sheet>
          <Vignette k={.5} />
        </AbsoluteFill>; })()}

      {/* END */}
      {t >= S.end[0] && (() => { const k = sp(t, S.end[0] + .2, fps);
        return <AbsoluteFill>
          <Sheet x={-30} y={-30} w={1140} h={1980} color={C.cream} seed={16} edge={false} />
          <Img src={staticFile('brand/logo-full.png')} style={{position: 'absolute', left: 290, top: 420, width: 500, opacity: k, filter: SHADOW}} />
          <Sheet x={140} y={980} w={800} h={150} color={C.yellow} seed={110} rot={-1.5} style={{opacity: k}}>
            <div style={{textAlign: 'center', lineHeight: '150px', fontFamily: PRE, fontWeight: 900, fontSize: 54, color: C.navy}}>💬 우리 아이 요즘 질문은?</div></Sheet>
          <div style={{position: 'absolute', top: 1180, left: 0, right: 0, textAlign: 'center', fontFamily: PRE, fontWeight: 800, fontSize: 40, color: C.navy, opacity: k}}>@thebearandjoy 팔로우</div>
        </AbsoluteFill>; })()}

      <Grain />
      {/* captions: a plain square box (Joy, 24 Nov) */}
      {cap && !inS('msg') && !inS('end') && (
        <div style={{position: 'absolute', left: 70, right: 70, top: 1300, display: 'flex', justifyContent: 'center'}}>
          <div style={{background: 'rgba(22,20,18,.85)', borderRadius: 0, padding: '14px 26px', fontFamily: PRE, fontWeight: 800, fontSize: 42, lineHeight: 1.3, color: '#fff', textAlign: 'center', whiteSpace: 'pre-line'}}>{cap.text}</div>
        </div>)}
    </AbsoluteFill>
  );
};
