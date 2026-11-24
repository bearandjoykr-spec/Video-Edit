// "AI 시대, 질문하는 아이" (Joy, 24 Nov 2026): paper-craft diorama reel made on this Mac (no AI images).
// Look (Joy's reference): crumpled kraft and coloured paper with white fibre edges, layered cut-outs with soft shadows, a lit
// school classroom diorama, people made of paper (clothes with newsprint/halftone texture) wearing Joy's and Mark's real faces
// (brand avatars, printed-paper look: projects/2026-11-ai-question/face_doll.py; no microphones). Children are seen from behind.
// Textures: projects/2026-11-ai-question/textures.py. Captions: plain square box. All text inside y 300–1450.
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

const C = {kraft: '#C9A47A', kraftD: '#A47B52', cream: '#F4EDDC', paper: '#FBF7EC', navy: '#1E2D4D', yellow: '#FFD24A', red: '#D44A30', ink: '#262320',
  skin: '#EDBE98', hair: '#2B211B', blue: '#4F7FAF', green: '#5E9460', pink: '#E58FA0', wall: '#F2DEC6', board: '#2E4A3B', wood: '#8A5A35'};
const PRE = "'Pretendard', 'Noto Color Emoji', sans-serif";
const HAND = "'Gaegu', 'Pretendard', 'Noto Color Emoji', cursive";
const SERIF = "'Gowun Batang', 'Pretendard', 'Noto Color Emoji', serif";
// letters that look cut from paper: a little paper-white rim and a soft shadow under them
const CUTTYPE: React.CSSProperties = {fontFamily: SERIF, fontWeight: 700, textShadow: '0 0 1px #FBF6EA, 1px 1px 0 #FBF6EA, -1px 1px 0 #FBF6EA, 2px 3px 3px rgba(40,25,10,.35)'};
const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};
const FONTS: [string, string, string][] = [['Pretendard', '700', 'Pretendard-Bold.woff2'], ['Pretendard', '800', 'Pretendard-ExtraBold.woff2'],
  ['Pretendard', '900', 'Pretendard-Black.woff2'], ['Noto Color Emoji', '400', 'Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf'], ['Gaegu', '700', 'Gaegu-Bold.ttf'], ['Gowun Batang', '700', 'GowunBatang-Bold.ttf']];
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
const TEX = {crumple: staticFile('paper/tex-crumple.png'), news: staticFile('paper/tex-news.png'), fibre: staticFile('paper/tex-fibre.png'), mulberry: staticFile('paper/tex-mulberry.png')};

// torn outline in px, as a CSS polygon()
const tornPoly = (w: number, h: number, seed: number, j = 12, step = 9) => {
  const r = rng(seed); const pts: string[] = [];
  for (let x = 0; x <= w; x += step) pts.push(`${x}px ${r() * j}px`);
  for (let y = 0; y <= h; y += step) pts.push(`${w - r() * j}px ${y}px`);
  for (let x = w; x >= 0; x -= step) pts.push(`${x}px ${h - r() * j}px`);
  for (let y = h; y >= 0; y -= step) pts.push(`${r() * j}px ${y}px`);
  return `polygon(${pts.join(',')})`;
};
// a sheet of crumpled paper with a white fibre edge where it was torn
const Sheet: React.FC<{x: number; y: number; w: number; h: number; color?: string; seed?: number; rot?: number; tex?: 'crumple' | 'news' | 'fibre' | 'mulberry'; edge?: boolean;
  style?: React.CSSProperties; children?: React.ReactNode}> = ({x, y, w, h, color = C.paper, seed = 3, rot = 0, tex = 'mulberry', edge = true, style, children}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, height: h, transform: `rotate(${rot}deg)`, filter: SHADOW, ...style}}>
    {edge && <div style={{position: 'absolute', left: -5, top: -5, width: w + 10, height: h + 10, background: '#F6F1E6', clipPath: tornPoly(w + 10, h + 10, seed + 500, 14, 7)}} />}
    <div style={{position: 'absolute', inset: 0, clipPath: tornPoly(w, h, seed), background: color}}>
      <div style={{position: 'absolute', inset: 0, backgroundImage: `url(${TEX[tex]})`, backgroundSize: tex === 'news' ? '420px' : tex === 'mulberry' ? '640px' : '520px', mixBlendMode: tex === 'news' ? 'multiply' : 'overlay',
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
    <pattern id={`mb${id}`} patternUnits="userSpaceOnUse" width="300" height="300"><image href={TEX.mulberry} width="300" height="300" /></pattern>
    <filter id={`rg${id}`} x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".09" numOctaves="3" seed="3" /><feDisplacementMap in="SourceGraphic" scale="7" /></filter>
    <filter id={`rw${id}`} x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".12" numOctaves="3" seed="9" /><feDisplacementMap in="SourceGraphic" scale="9" /></filter>
  </defs>
);
// a filled paper shape: colour + crumple light + optional newsprint
const P: React.FC<{d: string; fill: string; id: string; news?: boolean; stroke?: boolean}> = ({d, fill, id, news, stroke}) => (
  <g style={{filter: 'drop-shadow(2px 4px 2px rgba(30,15,5,.38))'}}>
    <path d={d} fill="#F3EDE0" stroke="#F3EDE0" strokeWidth={5} filter={`url(#rw${id})`} />
    <g filter={`url(#rg${id})`}><path d={d} fill={fill} />
    <path d={d} fill={`url(#mb${id})`} style={{mixBlendMode: 'overlay'}} opacity={.9} /></g>
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

const Dino: React.FC<{w: number; t: number}> = ({w, t}) => (
  <svg viewBox="0 0 320 220" width={w} height={w * 220 / 320} style={{overflow: 'visible'}}><Defs id="dino" />
    <g transform={`rotate(${Math.sin(t * 2) * 2} 160 160)`}>
      <P id="dino" d="M40 150 Q20 120 60 112 Q110 100 140 96 L150 60 Q156 20 196 18 Q236 18 244 44 Q246 62 222 64 L196 66 L190 104 Q260 112 300 160 Q250 150 200 152 L196 196 L174 196 L170 156 L120 158 L116 196 L94 196 L92 158 Q60 160 40 150 Z" fill="#6F9A5B" />
      <P id="dino" d="M150 100 Q170 92 188 100 L186 130 Q168 136 150 128 Z" fill="#88B070" />
      {[[110, 118], [130, 108], [210, 128], [240, 140]].map(([x, y], i) => <circle key={i} cx={x} cy={y} r={7} fill="#4E7A42" />)}
      <circle cx={214} cy={36} r={5} fill="#222" /><path d="M224 52 Q232 56 238 50" stroke="#222" strokeWidth={3} fill="none" /></g></svg>
);

// ---------- a real-looking computer (Joy: the monitor is a real computer, not paper) ----------
const Monitor: React.FC<{x: number; y: number; w: number; h: number; children: React.ReactNode}> = ({x, y, w, h, children}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w, filter: 'drop-shadow(0 30px 40px rgba(0,0,0,.35))'}}>
    <div style={{width: w, height: h, borderRadius: 26, background: 'linear-gradient(160deg, #3a3d44, #15161a 60%, #0c0c0e)', padding: 22, boxShadow: 'inset 0 1px 0 rgba(255,255,255,.25)'}}>
      <div style={{position: 'relative', width: '100%', height: '100%', borderRadius: 8, overflow: 'hidden', background: '#F4F6FA'}}>
        {children}
        <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(125deg, rgba(255,255,255,.28) 0%, rgba(255,255,255,0) 38%)', pointerEvents: 'none'}} /></div></div>
    <div style={{width: 46, height: 10, borderRadius: 5, background: '#0b0b0d', margin: '-16px auto 0', position: 'relative'}} />
    <div style={{width: 120, height: 110, margin: '0 auto', background: 'linear-gradient(90deg, #b9bcc2, #e6e8ec 50%, #a9acb2)'}} />
    <div style={{width: 320, height: 22, margin: '0 auto', borderRadius: '12px 12px 4px 4px', background: 'linear-gradient(#e9ebef, #a6a9af)'}} />
  </div>
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
const Teacher: React.FC<{who: 'joy' | 'mark'; x: number; y: number; w: number; t: number; glasses?: number; wave?: number}> = ({who, x, y, w, t, glasses = 0, wave = 0}) => {
  // Joy's own torn-paper portrait of the two of us (raw-footage/ai-question/joy-paper-portrait.webp), cut into busts.
  // joy-bust 695x802: eyes at (148,233) and (258,193), waving hand as its own piece (joy-hand.png, wrist ~ (112,640)); mark-bust 831x876.
  const joy = who === 'joy'; const W0 = joy ? 695 : 831; const k = w / W0;
  const off = glasses >= 1 ? 0 : 1 - glasses;
  const sway = Math.sin(t * 1.1 + (joy ? 1 : 0)) * 1.2, breathe = 1 + Math.sin(t * 2.1 + (joy ? .5 : 0)) * .006;
  const handA = wave * (Math.sin(t * 9) * 13 + 4);
  return <div style={{position: 'absolute', left: x, top: y, width: w, filter: SHADOW, transformOrigin: '50% 100%', transform: `rotate(${sway}deg) scaleY(${breathe})`}}>
    <Img src={staticFile(`paper/${who}-bust.png`)} style={{width: w, display: 'block'}} />
    {joy && <Img src={staticFile('paper/joy-hand.png')} style={{position: 'absolute', left: 0, top: 0, width: w, transformOrigin: `${112 * k}px ${640 * k}px`, transform: `rotate(${handA}deg)`}} />}
    {joy && glasses > 0 && <div style={{position: 'absolute', left: 203 * k - 130 * k + off * 260, top: 213 * k - 34 * k - off * 460, width: 260 * k,
      transform: `rotate(${-20 + off * 40}deg)`, transformOrigin: '50% 50%', filter: SHADOW}}>
      <svg viewBox="0 0 260 92" width={260 * k} height={92 * k}><rect x={6} y={16} width={104} height={62} rx={24} fill="#9FD3F2" fillOpacity=".8" stroke={C.ink} strokeWidth={8} />
        <rect x={150} y={16} width={104} height={62} rx={24} fill="#9FD3F2" fillOpacity=".8" stroke={C.ink} strokeWidth={8} /><path d="M110 42 Q130 26 150 42" stroke={C.ink} strokeWidth={8} fill="none" /></svg>
      <div style={{position: 'absolute', left: '40%', top: -32 * k, fontFamily: PRE, fontWeight: 900, fontSize: 34 * k, color: '#fff', background: C.blue, padding: '0 10px'}}>AI</div></div>}
  </div>;
};

// Joy's torn-paper children (kids-base.png from y 250 of the 1254 px picture; the two raised arms rise on their own)
const KK = 1080 / 1254;
const ARMS = [{src: 'paper/kid-arm-a.png', x: 494, y: 196, w: 126, h: 365, px: 552, py: 555}, {src: 'paper/kid-arm-b.png', x: 1132, y: 225, w: 100, h: 341, px: 1200, py: 560}];
export const KID_HEADS = [138, 336, 672, 930];
const Kids: React.FC<{t: number; fps: number; top: number; raise: (number | null)[]}> = ({t, fps, top, raise}) => (
  <div style={{position: 'absolute', left: 0, top, width: 1080, height: 1920 - top}}>
    <Img src={staticFile('paper/kids-base.png')} style={{position: 'absolute', left: 0, top: 0, width: 1080, transformOrigin: '50% 100%', transform: `scaleY(${1 + Math.sin(t * 2) * .004})`}} />
    {ARMS.map((a, i) => { const r = raise[i]; if (r == null) return null;
      const p = Math.max(0, spring({frame: Math.round((t - r) * fps), fps, config: {damping: 9, stiffness: 110, mass: .8}}));
      const wob = Math.sin(t * (p > .9 ? 5 : 2.2) + i * 2) * (p > .9 ? 3 : 1.5);
      return <Img key={i} src={staticFile(a.src)} style={{position: 'absolute', left: a.x * KK, top: (a.y - 250) * KK, width: a.w * KK, height: a.h * KK,
        transformOrigin: `${(a.px - a.x) * KK}px ${(a.py - a.y) * KK}px`, transform: `rotate(${(1 - p) * (i ? 30 : -30) + wob}deg) scaleY(${.42 + .58 * Math.min(p, 1.06)})`, filter: SHADOW}} />; })}
  </div>
);

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
    <div style={{background: C.paper, borderRadius: 40, padding: '22px 30px', ...CUTTYPE, fontSize: 42, color: C.navy, textAlign: 'center', lineHeight: 1.25}}>{children}</div>
    <div style={{position: 'absolute', bottom: -26, [tail]: 60, width: 0, height: 0, borderLeft: '22px solid transparent', borderRight: '22px solid transparent', borderTop: `30px solid ${C.paper}`}} />
  </div>
);

type Cap = {s: number; e: number; text: string; en?: string};
export const PT_CAPS: Cap[] = [
  {s: 0.3, e: 3, text: 'AI가 다 알려주는 시대,\n우리 아이에게 필요한 건 뭘까요?', en: 'In an age when AI tells us everything,\nwhat do our children really need?'},
  {s: 3, e: 8, text: '이제 궁금한 건 AI에게 물으면\n몇 초 만에 답이 나와요', en: 'Ask AI anything,\nand the answer comes in seconds.'},
  {s: 8, e: 13, text: '책을 찾지 않아도, 검색하지 않아도,\n누군가에게 묻지 않아도요', en: 'No need to find a book, search,\nor ask anyone.'},
  {s: 13, e: 17, text: '그런데 정말 중요한 건 정답이 아니라,\n어떤 질문을 하느냐예요', en: "But what matters most isn't the answer.\nIt's the question we ask."},
  {s: 17, e: 22, text: '그림책을 읽으며\n\'너는 어떻게 생각해?\'라고 물으면', en: 'When we read a picture book together\nand ask, "What do you think?"'},
  {s: 22, e: 27, text: '아이들 머릿속은\n질문과 상상으로 가득 차요', en: "children's minds fill up\nwith questions and imagination."},
  {s: 27, e: 34, text: '다른 나라 사람을 만났을 때도\n내 생각을 내 말로 표현하는 힘', en: 'Meeting people from other countries,\nwe say what we think, in our own words.'},
  {s: 34, e: 38, text: 'AI는 우리가 쓰는 도구예요.\n생각은 우리 아이가 하는 거고요', en: "AI is a tool we use.\nThe thinking is our children's."},
  {s: 38, e: 42, text: 'AI 시대, 우리 아이에게\n어떤 AI 교육이 필요할까요?', en: 'What kind of AI education do our children need?\nLet\'s talk in the comments.'},
];
export const PT_SCENES = {hook: [0, 3], ai: [3, 8], cross: [8, 13], turn: [13, 17], cls: [17, 27], world: [27, 34], msg: [34, 38], end: [38, 42]};

export const PaperThink: React.FC = () => {
  useFonts();
  const frame = useCurrentFrame(); const {fps} = useVideoConfig(); const t = frame / fps;
  const S = PT_SCENES; const inS = (k: keyof typeof S) => t >= S[k][0] && t < S[k][1];
  const vis = (k: keyof typeof S) => t >= S[k][0] && t < S[k][1] + .7;
  const W = (k: keyof typeof S, node: React.ReactNode) => { const s0 = S[k][0]; const dur = S[k][1] - s0;
    const e = s0 === 0 ? 1 : spring({frame: frame - Math.round(s0 * fps), fps, config: {damping: 18, stiffness: 90, mass: .9}});
    const cam = 1.02 + .045 * Math.min(1, (t - s0) / dur); const dir = ['ai', 'turn', 'world', 'end'].includes(k) ? -1 : 1;
    return <AbsoluteFill style={{transform: `translateX(${(1 - e) * 1150 * dir}px) rotate(${(1 - e) * 5 * dir}deg)`, boxShadow: e < .99 ? '0 0 60px rgba(0,0,0,.45)' : undefined, overflow: 'hidden'}}>
      <AbsoluteFill style={{transform: `scale(${cam}) translateY(${-(cam - 1) * 120}px)`}}>{node}</AbsoluteFill></AbsoluteFill>; };
  const lt = (k: keyof typeof S) => t - S[k][0];
  const cap = PT_CAPS.find((c) => t >= c.s && t < c.e);
  const drift = Math.sin(t * .6) * 6;
  return (
    <AbsoluteFill style={{background: C.kraft, overflow: 'hidden'}}>
      {/* HOOK: in the classroom, a child's head opens and question marks burst out */}
      {vis('hook') && W('hook', (() => { const l = lt('hook');
        return <AbsoluteFill style={{transform: `scale(${1.05 - l * .015})`, transformOrigin: '50% 70%'}}>
          <Classroom t={t} />
          <Kids t={t} fps={fps} top={1000} raise={[.35, .75]} />
          {KID_HEADS.flatMap((hx, i) => [0, 1].map((j) => { const st = .5 + i * .22 + j * .35; const k = sp(t, st, fps, 9); const up = interpolate(t - st, [0, 1.6], [0, 1], clamp);
            return k > .02 && <CutText key={`${i}${j}`} text={j ? '!' : '?'} size={j ? 96 : 130} color={(i + j) % 2 ? C.yellow : C.red}
              style={{position: 'absolute', left: hx - 40 + (j ? 60 : -10) + Math.sin(t * 3 + i) * 6, top: 1010 - 230 * k - up * 60, transform: `rotate(${(i - 1.5) * 8 + Math.sin(t * 4 + i * 2) * 5}deg) scale(${k})`}} />; }))}
          <Sheet x={70} y={330} w={940} h={250} color={C.paper} seed={5} rot={-1.5}>
            <div style={{padding: '36px 40px', ...CUTTYPE, fontSize: 64, lineHeight: 1.2, color: C.navy, textAlign: 'center'}}>
              AI가 다 알려주는 시대,<br /><span style={{color: C.red}}>우리 아이에게 필요한 힘은?</span></div></Sheet>
        </AbsoluteFill>; })())}

      {/* AI: a paper laptop pours out answer slips */}
      {vis('ai') && W('ai', (() => { const l = lt('ai');
        const msgs: {at: number; me?: boolean; text?: string; dino?: boolean}[] = [{at: .4, me: true, text: '공룡은 왜 사라졌어? 🦖'},
          {at: 1.5, dino: true, text: '약 6,600만 년 전, 커다란 소행성이 지구에 떨어졌어요 ☄️'}, {at: 2.3, text: '화산 폭발로 하늘이 어두워지고 ☁️'},
          {at: 2.9, text: '날씨가 추워져 먹이가 사라졌대요 🍂'}, {at: 3.5, text: '더 궁금한 거 있어요? 😊'}];
        const shown = msgs.filter((m) => l >= m.at); const typing = (l > .9 && l < 1.5) || (l > 2.0 && l < 2.3);
        const scroll = interpolate(l, [2.3, 3.9], [0, -250], clamp);
        return <AbsoluteFill>
          <Sheet x={-30} y={-30} w={1140} h={1980} color={C.cream} seed={7} edge={false} />
          <Sheet x={-30} y={1080} w={1140} h={900} color={C.kraftD} seed={8} />
          <Monitor x={90} y={360} w={900} h={640}>
            <div style={{height: 58, background: '#fff', borderBottom: '1px solid #e3e6ec', display: 'flex', alignItems: 'center', gap: 12, padding: '0 22px', fontFamily: PRE, fontWeight: 800, fontSize: 26, color: '#334'}}>
              <span style={{width: 34, height: 34, borderRadius: 17, background: 'linear-gradient(135deg,#6C8CFF,#9E6CFF)', display: 'inline-block'}} /> AI 도우미
              <span style={{marginLeft: 'auto', fontSize: 20, color: '#2BA84A'}}>● 온라인</span></div>
            <div style={{position: 'absolute', left: 0, right: 0, top: 58, bottom: 0, padding: '18px 22px', overflow: 'hidden'}}>
              <div style={{transform: `translateY(${scroll}px)`}}>
                {shown.map((m, i) => { const k = sp(t, S.ai[0] + m.at, fps, 12);
                  return <div key={i} style={{display: 'flex', justifyContent: m.me ? 'flex-end' : 'flex-start', marginBottom: 14, transform: `translateY(${(1 - k) * 30}px) scale(${.9 + .1 * k})`, opacity: k, transformOrigin: m.me ? '100% 100%' : '0 100%'}}>
                    <div style={{maxWidth: 560, padding: '14px 20px', borderRadius: 22, borderBottomRightRadius: m.me ? 6 : 22, borderBottomLeftRadius: m.me ? 22 : 6,
                      background: m.me ? '#3B7CF6' : '#fff', color: m.me ? '#fff' : '#222', boxShadow: '0 2px 6px rgba(0,0,0,.08)', fontFamily: PRE, fontWeight: 700, fontSize: 30, lineHeight: 1.35}}>
                      {m.dino && <div style={{background: '#EAF3E2', borderRadius: 14, padding: 10, marginBottom: 10, display: 'flex', justifyContent: 'center'}}><Dino w={300} t={t} /></div>}
                      {m.text}</div></div>; })}
                {typing && <div style={{display: 'flex', gap: 8, padding: '16px 22px', background: '#fff', borderRadius: 22, width: 90}}>
                  {[0, 1, 2].map((d) => <span key={d} style={{width: 12, height: 12, borderRadius: 6, background: '#9aa', opacity: .4 + .6 * Math.max(0, Math.sin(t * 8 - d))}} />)}</div>}
              </div></div>
          </Monitor>
          <CutText text="⚡ 3초" size={74} color={C.red} style={{position: 'absolute', left: 770, top: 310, transform: `rotate(8deg) scale(${sp(t, S.ai[0] + 1.6, fps, 9)})`}} />
          <Vignette k={.3} />
        </AbsoluteFill>; })())}

      {/* CROSS: books, search and asking someone get crossed out */}
      {vis('cross') && W('cross', (() => { const l = lt('cross');
        const items: [string, string][] = [['📚', '책 찾기'], ['🔍', '검색하기'], ['🙋', '누군가에게 묻기']];
        return <AbsoluteFill>
          <Sheet x={-30} y={-30} w={1140} h={1980} color="#E6DCC5" seed={9} edge={false} />
          {items.map(([e, w], i) => { const k = sp(t, S.cross[0] + i * .5, fps); const y0 = 380 + i * 300;
            const xp = interpolate(l, [1.6 + i * 1.1, 2.2 + i * 1.1], [0, 1], clamp);
            return <div key={i} style={{position: 'absolute', left: 120, top: y0, width: 840, height: 260, transform: `scale(${k}) rotate(${i % 2 ? 1.5 : -1.5}deg)`}}>
              <Sheet x={0} y={0} w={840} h={250} color={i === 1 ? '#E3EEF6' : C.paper} seed={40 + i}>
                <div style={{display: 'flex', alignItems: 'center', height: 250, padding: '0 50px', gap: 40}}>
                  <span style={{fontSize: 120}}>{e}</span><span style={{...CUTTYPE, fontSize: 72, color: C.navy}}>{w}</span></div></Sheet>
              <svg width={840} height={260} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
                <Draw d="M60 40 L780 220" p={xp} color={C.red} w={16} /><Draw d="M780 40 L60 220" p={interpolate(xp, [.4, 1], [0, 1], clamp)} color={C.red} w={16} /></svg>
            </div>; })}
          <Vignette k={.35} />
        </AbsoluteFill>; })())}

      {/* TURN: the answers blow away, one big question mark stays */}
      {vis('turn') && W('turn', (() => { const l = lt('turn'); const k = sp(t, S.turn[0] + .5, fps, 10);
        return <AbsoluteFill>
          <Sheet x={-30} y={-30} w={1140} h={1980} color={C.navy} seed={10} edge={false} />
          {Array.from({length: 10}, (_, i) => { const r = rng(i + 50); const p = interpolate(l, [0, 1.4], [0, 1], clamp);
            return <Sheet key={i} x={100 + r() * 800 - p * 700} y={300 + r() * 1000 - p * 600} w={170} h={100} color={C.paper} tex="news" seed={60 + i} rot={r() * 60 - 30 + p * 90} style={{opacity: 1 - p}} />; })}
          <CutText text="?" size={520} color={C.yellow} style={{position: 'absolute', left: 400, top: 600, transform: `scale(${k}) rotate(${-6 + Math.sin(t * 1.5) * 3}deg)`}} />
          {/* Joy (24 Nov): the questions we ask children rise out of the ? like thought bubbles */}
          {([[.9, 80, 560, 400, '너는 어떻게 생각해?', 'What do you think?'], [1.5, 545, 640, 480, '네가 주인공이라면\n어떤 마음이었을 것 같아?', 'If you were the hero, how would you feel?'],
            [2.1, 80, 950, 390, '왜 그렇게 생각했어?', 'Why do you think so?'], [2.7, 610, 985, 400, '다음엔 무슨 일이\n일어날까?', 'What happens next?']] as [number, number, number, number, string, string][]).map(([at, bx, by, bw, ko, en], i) => {
            const q = spring({frame: Math.round((t - S.turn[0] - at) * fps), fps, config: {damping: 8, stiffness: 140, mass: .6}}); if (q < .01) return null;
            const fy = -(t - S.turn[0] - at) * 9 + Math.sin(t * 2.2 + i) * 6; const fx = Math.sin(t * 1.4 + i * 2) * 5;
            const cx = bx + bw / 2, cy = by + 80; const ox = 620, oy = 760;   // trail from the top of the ?
            return <React.Fragment key={i}>
              {[.25, .5, .72].map((f, j) => { const d = spring({frame: Math.round((t - S.turn[0] - at + .25 - j * .08) * fps), fps, config: {damping: 10, stiffness: 160}});
                return d > .02 && <div key={j} style={{position: 'absolute', left: ox + (cx - ox) * f - (8 + j * 6) + fx, top: oy + (cy - oy) * f + fy * f, width: (16 + j * 12), height: (16 + j * 12), borderRadius: '50%',
                  background: '#FBF5E8', transform: `scale(${d})`, filter: SHADOW}} />; })}
              <div style={{position: 'absolute', left: bx + fx, top: by + fy, width: bw, transform: `scale(${q})`, transformOrigin: '50% 100%', filter: SHADOW}}>
                <div style={{background: '#FBF5E8', borderRadius: '50%', padding: '34px 30px', textAlign: 'center', boxShadow: 'inset 0 -6px 0 rgba(0,0,0,.05)'}}>
                  <div style={{...CUTTYPE, fontSize: 34, lineHeight: 1.3, color: C.navy, whiteSpace: 'pre'}}>{ko}</div>
                  <div style={{...CUTTYPE, fontSize: 22, lineHeight: 1.3, color: '#7A5B3A', marginTop: 6}}>{en}</div></div></div>
            </React.Fragment>; })}
          <Sheet x={140} y={330} w={800} h={130} color={C.paper} seed={70} rot={-2} style={{opacity: interpolate(l, [1.2, 1.6], [0, 1], clamp)}}>
            <div style={{textAlign: 'center', lineHeight: '130px', ...CUTTYPE, fontSize: 60, color: C.navy}}>정답보다 <span style={{color: C.red}}>질문</span></div></Sheet>
          <Vignette k={.5} />
        </AbsoluteFill>; })())}

      {/* CLASS: Joy and Mark read a picture book, the children raise their hands and their heads fill with ideas */}
      {vis('cls') && W('cls', (() => { const l = lt('cls');
        const ideas = ['🐻', '🚀', '🌊', '🦋'];
        return <AbsoluteFill>
          <Classroom t={t} board={<div style={{fontFamily: HAND, fontWeight: 700, fontSize: 62, color: '#F2EEDC', textAlign: 'center', paddingTop: 70, lineHeight: 1.15}}>What happens<br />next? 🤔</div>} />
          <Teacher who="mark" x={-50} y={590} w={600} t={t} />
          <Teacher who="joy" x={560} y={650} w={520} t={t} wave={interpolate(l, [6.2, 6.5, 8.4, 8.8], [0, 1, 1, 0], clamp)} />
          <Sheet x={110} y={950} w={380} h={260} color="#FBF5E6" seed={77} tex="mulberry" rot={-5 + Math.sin(t * 1.3) * .8}>
            <Img src={staticFile('brand/bear-butterfly.png')} style={{position: 'absolute', left: 210, top: 34, width: 135}} />
            {[0, 1, 2, 3, 4].map((q) => <div key={q} style={{position: 'absolute', left: 30, top: 54 + q * 34, width: 140 - q * 12, height: 8, background: '#C4B9A4'}} />)}
            <div style={{position: 'absolute', left: 188, top: 10, bottom: 10, width: 3, background: 'rgba(0,0,0,.12)'}} /></Sheet>
          {l > .5 && l < 5 && <Bubble x={470} y={420} w={520} k={sp(t, S.cls[0] + .6, fps)} tail="left">What do you think<br />happens next?</Bubble>}
          <Kids t={t} fps={fps} top={1055} raise={[S.cls[0] + 1.6, S.cls[0] + 2.3]} />
          {KID_HEADS.map((hx, i) => { const think = sp(t, S.cls[0] + 4.6 + i * .45, fps, 11);
            return think > .02 && <div key={i} style={{position: 'absolute', left: hx - 115, top: 860 - (i % 2) * 40 + Math.sin(t * 1.6 + i) * 6, width: 230, height: 200, transform: `scale(${think})`, transformOrigin: '50% 100%', filter: SHADOW}}>
              <svg width={230} height={200}><ellipse cx={115} cy={84} rx={104} ry={76} fill={C.paper} /><circle cx={100} cy={180} r={12} fill={C.paper} /><circle cx={110} cy={158} r={18} fill={C.paper} />
                <Gear x={52} y={62} r={20} a={t * 120} /><Gear x={86} y={96} r={14} a={-t * 160} color={C.red} /></svg>
              <div style={{position: 'absolute', left: 116, top: 30, fontSize: 82, transform: `rotate(${Math.sin(t * 2.4 + i) * 8}deg)`}}>{ideas[i]}</div></div>; })}
          <Vignette k={.45} />
        </AbsoluteFill>; })())}

      {/* WORLD: Joy takes off the AI glasses and speaks for herself */}
      {vis('world') && W('world', (() => { const l = lt('world'); const g = l < 2.2 ? 1 : interpolate(l, [2.2, 3.2], [.999, 0], clamp);
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
          <Teacher who="joy" x={-60} y={640} w={640} t={t} glasses={g} wave={interpolate(l, [3.4, 3.7, 6.2, 6.6], [0, 1, 1, 0], clamp)} />
          <Sheet x={-40} y={1290} w={1160} h={700} color="#B48A60" seed={131} />
          {g < .1 && <Bubble x={300} y={430} w={420} k={sp(t, S.world[0] + 3.3, fps)}>I think…<div style={{fontSize: 32, color: C.red}}>내 생각은요!</div></Bubble>}
          <Vignette k={.4} />
        </AbsoluteFill>; })())}

      {/* MESSAGE */}
      {vis('msg') && W('msg', (() => { const k = sp(t, S.msg[0] + .2, fps);
        return <AbsoluteFill>
          <Sheet x={-30} y={-30} w={1140} h={1980} color={C.navy} seed={15} edge={false} />
          <Sheet x={90} y={560} w={900} h={560} color={C.cream} seed={100} rot={-1.5} style={{transform: `rotate(-1.5deg) scale(${.9 + .1 * k})`, opacity: k}}>
            <div style={{padding: '80px 60px', textAlign: 'center', ...CUTTYPE, fontSize: 78, lineHeight: 1.3, color: C.navy}}>
              AI는 <span style={{background: C.yellow, padding: '0 10px'}}>쓰는 것</span>,<br />생각은 <span style={{color: C.red}}>내가</span> 하는 것</div>
            <div style={{position: 'absolute', bottom: 60, left: 0, right: 0, textAlign: 'center', fontFamily: HAND, fontWeight: 700, fontSize: 44, color: C.kraftD}}>질문하는 아이, 생각을 말하는 아이</div></Sheet>
          <Vignette k={.5} />
        </AbsoluteFill>; })())}

      {/* END */}
      {t >= S.end[0] && W('end', (() => { const k = sp(t, S.end[0] + .2, fps);
        return <AbsoluteFill>
          <Sheet x={-30} y={-30} w={1140} h={1980} color={C.cream} seed={16} edge={false} />
          <Img src={staticFile('brand/logo-full.png')} style={{position: 'absolute', left: 300, top: 330, width: 480, opacity: k, filter: SHADOW}} />
          <Sheet x={120} y={840} w={840} h={150} color={C.yellow} seed={110} rot={-1.5} style={{opacity: k}}>
            <div style={{textAlign: 'center', lineHeight: '150px', ...CUTTYPE, fontSize: 56, color: C.navy}}>💬 어떤 AI 교육이 좋을까요?</div></Sheet>
          <div style={{position: 'absolute', top: 1030, left: 0, right: 0, textAlign: 'center', ...CUTTYPE, fontSize: 40, color: C.navy, opacity: k}}>@thebearandjoy 팔로우</div>
        </AbsoluteFill>; })())}

      <Grain />
      {/* captions: a torn strip of mulberry paper with paper-cut letters (Joy, 24 Nov: square, and made of paper) */}
      {cap && !inS('msg') && (() => { const lines = cap.text.split('\n'); const en = (cap.en ?? '').split('\n').filter(Boolean);
        const wpx = Math.min(980, 110 + Math.max(...lines.map((x) => x.length * 40), ...en.map((x) => x.length * 16.5))); const hpx = 52 + lines.length * 56 + en.length * 38 + (en.length ? 8 : 0);
        const k = sp(t, cap.s, fps, 16); const tilt = Math.round(cap.s) % 2 ? .8 : -.8;
        return <Sheet key={cap.s} x={540 - wpx / 2} y={1450 - hpx} w={wpx} h={hpx} color="#F7EFDF" seed={Math.round(cap.s * 10) + 200} rot={tilt}
          style={{opacity: k, transform: `rotate(${tilt}deg) translateY(${(1 - k) * 14}px)`}}>
          <div style={{height: hpx, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center'}}>
            {lines.map((x, i) => <div key={i} style={{...CUTTYPE, fontSize: 44, lineHeight: '56px', color: C.navy}}>{x}</div>)}
            {en.length > 0 && <div style={{marginTop: 8}}>{en.map((x, i) => <div key={i} style={{...CUTTYPE, fontSize: 29, lineHeight: '38px', color: '#7A5B3A', letterSpacing: .3}}>{x}</div>)}</div>}
          </div></Sheet>; })()}
    </AbsoluteFill>
  );
};
