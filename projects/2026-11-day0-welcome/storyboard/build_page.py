"""Builds the Day 0 storyboard page. Output: renders/day0/page/index.html + stills/ + sample.mp4.
Stills: run from remotion/  node class-stills.mjs ../renders/day0/sb 1 id=Day0Welcome <seconds...>
The page CSS is reused from the approved Day 1 storyboard builder."""
import html, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/../../..")
SB, OUT = f"{ROOT}/renders/day0/sb", f"{ROOT}/renders/day0/page"
os.makedirs(f"{OUT}/stills", exist_ok=True)
e = html.escape
ACTS = [
 ("The open", "0:00", [
  ("6", "Your montage", "Your film-style opening with the typed lines, exactly as you made it.", "Your own sound."),
  ("13.5", "Little Steps to Big Adventures", "The title lands in your watercolour world. \"Day 0\" is gone.", "Ukulele starts. Sparkle, whoosh, pops."),
  ("16.5", "What's in this video", "Three quick promises, including the free Day 1.", "A pop per row."),
 ]),
 ("Hello from Mark and Joy", "0:18", [
  ("24", "You're in the painting", "Your cuts and captions, your paintings, your logo at top left, and moving clouds now cut from your own paintings.", "Whoosh, sparkle."),
  ("44", "Parents' worries", "The two questions pop up as speech bubbles.", "Pops."),
 ]),
 ("Don't teach: USE", "0:57", [
  ("57.5", "The first big hit", "USE lands behind your heads with a camera shake.", "Impact, sparkle."),
  ("72", "Your HELLO lesson clip", "Your real lesson clips slide in beside you while Hello, Look and Your turn land above.", "Whoosh, sparkle."),
  ("88", "Joy's lesson clip", "Joy's clip, as in your edit, with what we bring and what parents bring above.", "Whoosh, pop."),
 ]),
 ("Parents are the key", "1:30", [
  ("105", "Surprise lines on Joy", "From your edit. They follow her head as she moves.", "Boing."),
  ("135", "Crown and guard", "Your Korea and Britain joke. The crown stays on Joy's head as she moves.", "Sparkle, pop."),
  ("146", "The things we say in Korean", "Joy's examples stack up as bubbles.", "Pops."),
 ]),
 ("Bear time", "2:43", [
  ("165", "HELLO chick", "From your edit.", "Boing."),
  ("168", "The bear in Mark's hand", "From your edit, using your bear art.", "Sparkle."),
  ("176", "LEVEL UP", "From your edit.", "Chime."),
  ("195.6", "The giant bear", "Your big jump-in, with a camera shake.", "Impact."),
  ("198", "Hello, I'm Bear!", "The bear speaks when Mark does the voice, then your hamster appears.", "Boing, pop."),
 ]),
 ("What each day looks like", "3:30", [
  ("217", "Mark's lessons", "Your three real lesson clips, plus a reminder that Day 1 is free.", "Whoosh, impact."),
  ("224", "Real worksheets", "Your worksheets fan in.", "Whoosh, pops."),
  ("230", "Joy's lessons", "Your three clips of Joy with the worksheets.", "Whoosh."),
  ("245", "Try. Space. See.", "Numbered steps, with your row of sunflowers.", "Chimes, pops."),
  ("252", "The sunflower explosion", "From your edit, and bigger.", "Impact."),
  ("268", "\u201c영어로 말해 봐\u201d crossed out", "A hand-drawn line strikes it through.", "Pop, then boing."),
 ]),
 ("Mistakes and the send-off", "4:32", [
  ("280", "Mistakes are fine", "Your sunglasses moment.", "Pop, sparkle."),
  ("314", "A lovely little step", "The bear rises in as Mark says it.", "Sparkle."),
  ("332", "We'll bring the ideas", "Your lightbulb, next to Mark's head.", "Chime."),
  ("342", "Goodbye", "Your wave, then your cloud transition into the offer.", "Sparkle."),
 ]),
 ("The offer: new, in place of the long logo hold", "5:43", [
  ("348", "1일차는 무료!", "Worksheet, website games and your joint photo for support.", "Ukulele up. Impact, pops, chime."),
  ("357", "Seven days on a path", "The bear walks all seven days, and each stop lights up.", "A pop per day."),
  ("366", "What's inside", "The page's exact list, with Mark's and Joy's photos.", "Whoosh and chime per row."),
  ("373", "Real reviews", "The same four as Day 1.", "Pops."),
  ("382", "₩47,000", "The price counts up, then the page's two buttons, and a finger taps the free one.", "Impact, pops, chime."),
  ("388", "Your animated logo", "Your bear logo from your edit, ending with the track's natural finish.", "Sparkle."),
 ]),
]
TIMES = [s for _, _, scenes in ACTS for s, *_ in scenes]
if __name__ == "__main__":
    import sys
    if "--times" in sys.argv:
        print(" ".join(TIMES)); raise SystemExit

acts = ""
for title, at, scenes in ACTS:
    rows = ""
    for s, name, what, sound in scenes:
        shutil.copy(f"{SB}/t{s}.jpg", f"{OUT}/stills/t{s}.jpg")
        v = float(s); clock = f"{int(v // 60)}:{int(v % 60):02d}"
        rows += f"""<article class="scene"><img src="stills/t{s}.jpg" alt="{e(name)}" loading="lazy"><div class="note"><span class="time">{clock}</span><h3>{e(name)}</h3><p>{e(what)}</p><p class="sound"><b>Sound</b>{e(sound)}</p></div></article>"""
    acts += f"""<section class="act"><h2>{e(title)} <span class="at">{at}</span></h2>{rows}</section>"""

own = "엄마·아빠의 걱정부터 내려놓기 · 7일 동안 함께하는 방법 · 무료 1일차와 전체 과정 안내 · 걱정 내려놓기 · 영어를 잘하는 아이 · 가장 중요한 이야기 · 가르치기 ✗ · 함께 사용하기 ✓ · 저희: 표현 · 발음 · 놀이 아이디어 · 부모님: 익숙한 목소리 · 따뜻한 관심 · 자신감의 열쇠 · 우리말로 생각해 볼까요? · 기다리지 않아요 · 이미 알고 있다면요? · 이야기 짓기 · 게임 설명하기 · 매일 이렇게 해요 · 놀이를 시작하는 작은 도구 · 완성 안 해도 OK! · 예상 밖의 놀이 · 반응을 받아주며 계속 놀아요 · 실수해도 괜찮아요 · 실수도 배움 · 오늘의 질문 · 장난치며 웃을 마음 · 놀이 아이디어는 저희가! · 1일차는 무료! · 웹사이트 놀이 게임 · Mark와 Joy의 지원 · 2–7일차, 전체 과정 · 다음 놀이가 열려요"

tpl = open(f"{ROOT}/projects/2026-11-day1-class/storyboard/build_page.py", encoding="utf8").read()
css = tpl[tpl.index('<meta name="claude:viewport-fit-sides"'):tpl.index("</style>") + 8].replace("{{", "{").replace("}}", "}")
page = "<title>Day 0 Welcome Storyboard</title>\n" + css + f"""
<div class="wrap">
<header>
  <span class="status">Waiting for your approval. This is not the final export.</span>
  <h1>Little Steps to Big Adventures</h1>
  <p>Your edit and my animation, combined: your montage, cuts, lesson clips, stickers and logo, in your watercolour paintings, with your ukulele track and a big new offer ending.</p>
  <div class="facts"><span><b>Length</b> 6:31 (your edit is 6:18)</span><span><b>Picture</b> 1920×1080</span><span><b>Speed</b> no footage sped up</span><span><b>Music</b> your ukulele pick</span><span><b>On-screen moments</b> about 135</span><span><b>Sound effects</b> about 165</span></div>
</header>
<section class="block">
  <h2>Watch the highlights</h2>
  <video controls preload="metadata" playsinline src="sample.mp4"></video>
  <p class="muted">About 100 seconds from the full video at 720p, with music. The full video is too large for this page, so it's in a separate file. I can't hear audio, so please check the voices, the music level and how the ukulele loops.</p>
</section>
<section class="block act">
  <h2>Your decisions</h2>
  <ul>
    <li><b>The child in your montage.</b> Please confirm the parents have agreed to showing the child's face.</li>
    <li><b>Lesson clips and logo.</b> I cut these out of your finished video, so they're a little softer than the originals. Send the original clips, or the Little Steps logo file, if you'd like them sharper.</li>
    <li><b>Stickers.</b> I recreated your stickers using emoji and your bear art, so that they can follow your heads. If you want your exact CapCut stickers, send them.</li>
    <li><b>Offer wording.</b> Day 1 “support from Mark and Joy” comes from your notes, and the page says Kakao support runs for the first 7 days. Please confirm the free day includes it.</li>
    <li><b>Music licence.</b> Pixabay's licence allows commercial use, but they warn that tracks can still get an automatic YouTube copyright claim. I'd upload the final video unlisted first to check.</li>
  </ul>
</section>
{acts}
<section class="block act">
  <h2>For Joy to check</h2>
  <p><b>New Korean I wrote.</b> Everything else comes from your captions or the page.</p>
  <p class="ko">{own}</p>
  <p><b>Two captions that may not match the speech.</b> Speech recognition isn't reliable here, so please listen. In the source footage at about 1:46, the caption says “중요한 열쇠를” and the recogniser heard “중요한 역할을”. At about 1:30, the caption says “한번 말해 봐도 괜찮겠다” and it heard “나도 한번 말해볼까?”. I kept your captions.</p>
  <p class="muted"><b>Reading speed.</b> I kept your captions word for word. 24 of 114 run faster than the 6 characters per second rule, up to 8.6. I held them longer where there was a pause, and going further would mean shortening your wording. Tell me if you want that.</p>
</section>
</div>
"""
open(f"{OUT}/index.html", "w", encoding="utf8").write(page)
print("page written", len(page))
