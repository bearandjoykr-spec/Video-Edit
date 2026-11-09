"""Builds the reels approval page. Output: renders/reels/page/index.html (plus previews copied there). CSS reused from the Day 1 storyboard."""
import html, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/../.."); e = html.escape
tpl = open(f"{ROOT}/projects/2026-11-day1-class/storyboard/build_page.py", encoding="utf8").read()
css = tpl[tpl.index('<meta name="claude:viewport-fit-sides"'):tpl.index("</style>")].replace("{{", "{").replace("}}", "}")
css += """.reels { display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr)); gap:24px; align-items:start; }
.reel { display:grid; gap:10px; min-width:0; }
.reel video { aspect-ratio:9/16; border-radius:14px; }
.reel pre { margin:0; white-space:pre-wrap; word-break:keep-all; font:inherit; font-size:14.5px; line-height:1.6; color:var(--muted); }
details summary { cursor:pointer; font-weight:700; }
</style>"""
R = [("use", "USE", "영어, 가르치지 말고 USE", "0:28", "The fastest and shortest. Don't teach: USE, then Hello, Look and Your turn landing one by one."),
     ("perfect", "Perfect English", "유창한 영어, 꼭 필요할까요?", "0:43", "Answers parents' biggest worry. The line gets crossed out, then Joy's Korean examples, ending on “Look! A bear!”."),
     ("bearvoice", "Bear voice", "이미 영어를 잘하는 아이라면?", "0:46", "The funny one, for parents of children who already speak some English. The giant bear jumps in as Mark does the voice.")]
cards = ""
for k, name, hook, ln, why in R:
    cap = open(f"{HERE}/captions/{k}.txt", encoding="utf8").read().strip()
    cards += f"""<article class="reel"><video controls preload="metadata" playsinline src="{k}.mp4"></video><h2>{e(name)} <span class="at">{ln}</span></h2><p class="ko"><b>{e(hook)}</b></p><p>{e(why)}</p><details><summary>Instagram caption</summary><pre>{e(cap)}</pre></details></article>"""
own = "영어, 가르치지 말고 · 가르치기 ✗ · 함께 사용하기 ✓ · 함께하는 순간 · 짧은 표현에도 의미가 생겨요 · 반가운 인사 · 함께 발견하는 말 · 함께하자는 초대 · 유창한 영어, 꼭 필요할까요? · 아기에게 우리말로 · 기다리지 않잖아요 · 함께 하루를 보내며 · 영어도 조금씩 · 이미 영어를 잘하는 아이라면? · 더 많은 걸 · 새로운 놀이 · 곰의 목소리 · 이야기 짓기 · 게임 설명하기 · 배고픈 곰! · 짧은 표현 하나로 이야기는 계속돼요 · 아이의 생각을 따라가 보세요"
page = "<title>Little Steps Instagram Reels</title>\n" + css + f"""
<div class="wrap">
<header>
  <span class="status">Waiting for your approval. These are previews, not the final export.</span>
  <h1>Three reels from Little Steps to Big Adventures</h1>
  <p>Vertical cuts with you both in your paintings, big words above your heads, the ukulele, and the “1일차는 무료예요!” ending.</p>
  <div class="facts"><span><b>Format</b> 1080×1920, shown here at 540p</span><span><b>Captions</b> yours, word for word</span><span><b>Sound</b> voices, effects and ukulele</span></div>
</header>
<section class="reels">{cards}</section>
<section class="block act">
  <h2>Please check</h2>
  <ul>
    <li><b>By ear.</b> I can't hear audio, so please check the voices and the ukulele level.</li>
    <li><b>Length.</b> Your brand rules aim for 15–35 seconds for reach. USE fits. The other two are longer, so tell me if you'd like them cut down.</li>
    <li><b>Reading speed.</b> Some captions run up to 8 Korean characters per second, because they're your exact wording. I can shorten them if you prefer.</li>
    <li><b>Posting schedule.</b> These use the “Little Steps · 첫날 무료” badge, like the Day 1 promos, not the “DAY N” series badge. Tell me if you want them numbered.</li>
  </ul>
</section>
<section class="block act">
  <h2>For Joy to check</h2>
  <p><b>Words on screen that I wrote or shortened:</b></p>
  <p class="ko">{e(own)}</p>
  <p>Please also read the three Instagram captions above.</p>
</section>
</div>
"""
open(f"{ROOT}/renders/reels/page/index.html", "w", encoding="utf8").write(page); print(len(page))
