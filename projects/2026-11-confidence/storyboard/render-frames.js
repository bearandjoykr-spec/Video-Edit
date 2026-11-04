// Renders storyboard stills: footage frame + brand overlays at 1080x1920.
const {chromium} = require('playwright');
const path = require('path');
const F = p => 'file://' + path.resolve(__dirname, p);
const A = p => 'file://' + path.resolve(__dirname, '../../../brand/assets', p);
const css = `
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400;1,600&family=Gowun+Batang:wght@400;700&family=Noto+Sans+KR:wght@500;700&display=swap');
*{margin:0;box-sizing:border-box} body{width:1080px;height:1920px;overflow:hidden;background:#1E2D4D;position:relative}
.cam{position:absolute;inset:0;transform-origin:50% 38%}
.cam img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.behind{position:absolute;left:0;right:0;text-align:center;color:#1E2D4D;font-family:'Playfair Display',serif;text-shadow:0 0 40px rgba(245,240,230,.55)}
.eyebrow{position:absolute;left:50%;transform:translateX(-50%);white-space:nowrap;font:600 28px/1 'Playfair Display',serif;letter-spacing:.2em;color:#C9A84C;text-transform:uppercase;background:rgba(30,45,77,.82);padding:14px 26px;border-radius:999px}
.cap{position:absolute;left:70px;right:70px;top:1210px;text-align:center;display:grid;gap:14px}
.ko{word-break:keep-all;font:700 64px/1.25 'Gowun Batang',serif;color:#F5F0E6;text-shadow:0 3px 0 rgba(30,45,77,.9),0 0 26px rgba(30,45,77,.75);text-wrap:balance}
.en{font:italic 400 40px/1.25 'Playfair Display',serif;color:#C9A84C;text-shadow:0 2px 12px rgba(30,45,77,.9)}
.hi{color:#E7CC7E}
.tag{position:absolute;left:60px;top:250px;font:italic 400 38px/1.2 'Playfair Display',serif;color:#F5F0E6;background:rgba(30,45,77,.72);border:2px solid rgba(201,168,76,.55);padding:16px 26px;border-radius:999px}
.card{position:absolute;left:70px;right:150px;top:280px;background:rgba(30,45,77,.86);border:2px solid rgba(201,168,76,.5);border-radius:28px;padding:34px 38px;display:grid;gap:18px;color:#F5F0E6}
.chip{justify-self:start;font:600 24px/1 'Playfair Display',serif;letter-spacing:.16em;color:#C9A84C;border:2px solid rgba(201,168,76,.7);padding:12px 18px;border-radius:999px;text-transform:uppercase}
.row{display:flex;align-items:baseline;gap:18px;border-top:1px solid rgba(245,240,230,.14);padding-top:16px;font:700 44px/1.2 'Gowun Batang',serif}
.row i{font:italic 400 30px/1.2 'Playfair Display',serif;color:rgba(245,240,230,.7);flex:1}
.row b{color:#C9A84C;font:700 36px/1 'Noto Sans KR',sans-serif}
.stars{position:absolute;left:70px;top:210px;display:flex;gap:14px;font-size:34px;color:#C9A84C}
.end{position:absolute;inset:0;background:linear-gradient(rgba(30,45,77,.6),rgba(22,34,60,.95) 45%);display:grid;place-content:center;justify-items:center;gap:40px;padding:0 90px;text-align:center}
.end .line{font:400 50px/1.4 'Gowun Batang',serif;color:#F5F0E6}
.end .line i{font:italic 400 54px/1 'Playfair Display',serif;color:#C9A84C;display:block;margin-bottom:14px}
.btn{font:700 38px/1 'Noto Sans KR',sans-serif;background:#FEE500;color:#191600;padding:26px 46px;border-radius:999px}
.water{position:absolute;left:46px;top:150px;width:110px;opacity:.6}
`;
const cap = (ko, en) => `<div class="cap"><div class="ko">${ko}</div>${en ? `<div class="en">${en}</div>` : ''}</div>`;
const cam = (src, zoom = 1, cut) => `<div class="cam" style="transform:scale(${zoom})"><img src="${F('frames/' + src)}"></div>`;
const camCut = (cut, zoom = 1) => `<div class="cam" style="transform:scale(${zoom})"><img src="${F('frames/' + cut)}"></div>`;
const water = `<img class="water" src="${A('bear-butterfly.png')}">`;
const frames = {
  '01-hook': cam('f2.0.png') +
    `<div class="eyebrow" style="top:520px">Bear &amp; Joy · Little Steps</div>` +
    `<div class="behind" style="top:600px;font:italic 600 150px/1 'Playfair Display',serif">Pronunciation?</div>` +
    camCut('cut2.0.png') + cap('한국 부모들은 왜 아이 <span class="hi">영어 발음</span>을 걱정할까요?', 'Why do Korean parents worry about pronunciation?'),
  '02-korea': cam('f12.0.png', 1.05) + water + cap('겉으로 보이는 모습을<br><span class="hi">굉장히 중요하게</span> 생각하는 것 같아요.', 'appearance is so important,'),
  '03-british': cam('f25.0.png') + water + `<div class="tag">Born in Oxford. Built in Seoul.</div>` + cap('저는 <span class="hi">영국인</span>이다 보니', 'As a British person, obviously,'),
  '04-confidence': cam('f44.0.png', 1.05) +
    `<div class="behind" style="top:470px;font:700 190px/1 'Playfair Display',serif">Confidence</div>` +
    camCut('cut44.0.png', 1.05) + cap('하지만 진짜 첫걸음은 <span class="hi">자신감</span>이에요.', 'But really, the first step is confidence.'),
  '05-korean-demo': cam('f50.6.png', 1.12) + `<div class="cap" style="top:1180px;transform:rotate(-2deg)"><div class="ko" style="font-size:84px">오른쪽? 왼쪽?<br><span class="hi">배고파요?</span></div></div>`,
  '06-mistakes': cam('f67.0.png', 1.05) +
    `<div class="behind" style="top:500px;font:italic 600 210px/1 'Playfair Display',serif">It's okay.</div>` +
    camCut('cut67.0.png', 1.05) + cap('<span class="hi">실수해도 괜찮다는</span> 것을요.', 'that making mistakes is okay.'),
  '07-fun-happy-light': cam('f81.0.png') + `<div class="card"><span class="chip">The first little step · 첫걸음</span>
      <div class="row">재미있게 <i>keep it fun</i><b>✓</b></div><div class="row">즐겁게 <i>keep it happy</i><b>✓</b></div><div class="row" style="opacity:.55">부담 없이 <i>keep it light</i><b></b></div></div>` +
    cap('즐겁게, <span class="hi">부담 없이,</span>', 'Keep it happy, keep it light,'),
  '08-end': cam('f87.0.png') + `<div class="end"><img src="${A('bear-butterfly.png')}" style="width:520px"><img src="${A('wordmark-cream.png')}" style="width:860px">
      <div class="line"><i>Little Steps,</i>여기서 시작해요.</div><div class="btn">카카오톡 채널 추가하기</div></div>`,
};
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 1080, height: 1920}});
  for (const [name, body] of Object.entries(frames)) {
    const fs = require('fs'); const tmp = path.join(__dirname, 'stills', '_' + name + '.html');
    fs.writeFileSync(tmp, `<!doctype html><meta charset="utf-8"><style>${css}</style>${body}`);
    await p.goto('file://' + tmp, {waitUntil: 'networkidle'}); fs.unlinkSync(tmp);
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({path: path.join(__dirname, 'stills', name + '.jpg'), type: 'jpeg', quality: 86});
    console.log('rendered', name);
  }
  await b.close();
})();
