"""Builds the Day 0 storyboard page. Output: renders/day0/page/index.html + stills/ + sample.mp4.
Stills: run from remotion/  node class-stills.mjs ../renders/day0/sb 1 id=Day0Welcome <seconds...>
The page CSS is reused from the approved Day 1 storyboard builder."""
import html, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/../../..")
SB, OUT = f"{ROOT}/renders/day0/sb", f"{ROOT}/renders/day0/page"
os.makedirs(f"{OUT}/stills", exist_ok=True)
e = html.escape
ACTS = [
 ("The open: tell them what's coming", "0:00", [
  ("1.8", "Animated title", "The bear walks in on a watercolour sky. The title is my draft: please confirm.", "Sparkle, whoosh, pops."),
  ("5.8", "What's in this video", "No cold open. Three promises, including the free Day 1.", "Whoosh and a pop per row."),
 ]),
 ("Hello from Mark and Joy", "0:07", [
  ("12", "They stand in the sky", "You're both cut out of the white wall, so words can go behind your heads. Your cuts and captions are kept.", "Whoosh, sparkle."),
  ("22", "Not to worry", "Mark's English builds word by word. A chip repeats the idea.", "Whoosh, pop."),
  ("35", "Parents' worries", "The two questions pop up as speech bubbles.", "Pops."),
 ]),
 ("Don't teach: USE", "0:45", [
  ("47", "The first big hit", "A bear wipe, then USE slams in behind your heads with a camera shake.", "Whoosh, impact, sparkle."),
  ("60", "Hello! Look! Your turn", "Each word lands behind you, with a burst of emoji on the free side.", "Sparkle on each word."),
 ]),
 ("Parents are the key", "1:09", [
  ("70.6", "부모님", "New sky colour for the new section.", "Impact, sparkle."),
  ("84", "What we bring, what you bring", "Two cards build on the right.", "Pops."),
  ("106", "What the child thinks", "Mark's lines become the child's thought bubbles.", "Pops."),
  ("114", "자신감의 열쇠", "Key words behind you, with key emoji.", "Sparkle."),
  ("124", "유창한 영어 crossed out", "A hand-drawn line strikes through it as Joy says it isn't needed.", "Pop, then boing."),
 ]),
 ("Talking before they can answer", "2:07", [
  ("137", "The things we say in Korean", "Joy's examples stack up as bubbles, ending on the sock.", "Pops."),
  ("156.6", "Look! A bear!", "The bear flies in as Mark says it.", "Whoosh, sparkle."),
 ]),
 ("For children who already know English", "2:39", [
  ("161", "Somewhere to take the words", "Mark's line builds up at the top.", "Whoosh."),
  ("181", "Three ideas", "Bear voice, make a story, explain a game.", "Pops."),
  ("185", "Hello, I'm Bear!", "The bear pops up and speaks when Mark does the voice.", "Boing."),
 ]),
 ("What each day looks like", "3:20", [
  ("202", "1일차 무료", "A mid-video reminder that Day 1 is free.", "Impact."),
  ("207", "Slow, natural, practise", "Three chips with animals for speed.", "Pops."),
  ("219", "Real worksheets", "Your actual worksheets fan in, then a stamp says they don't need finishing.", "Whoosh, pops, impact."),
  ("239", "Try. Space. See.", "Three numbered steps with a chime each.", "Chimes."),
  ("250", "Every reaction counts", "Korean, pointing, silly sounds, surprises.", "Pops."),
  ("260", "“영어로 말해 봐” crossed out", "The same strike as before, so viewers learn the signal.", "Pop, then boing."),
 ]),
 ("Mistakes are part of it", "4:23", [
  ("267", "실수도 배움", "Bear wipe, then words behind you.", "Whoosh, sparkle."),
  ("277", "앗! 다시 해 볼까?", "Big and playful.", "Sparkle, boing."),
  ("287", "Keep going when it's messy", "Mark's line builds up.", "Whoosh."),
 ]),
 ("The send-off", "4:50", [
  ("300", "Two questions for parents", "Bubbles with ticks.", "Pops."),
  ("308", "A lovely little step", "The bear rises in as Mark says it.", "Sparkle."),
  ("314", "What to bring", "Curiosity, imperfect English, willingness to be silly.", "Pops."),
  ("324", "The first door", "Sparkle burst for the door.", "Sparkle."),
  ("328", "DAY 1 · 무료", "Stamp as you say goodbye, then your wave.", "Impact."),
 ]),
 ("The offer: the new, big ending", "5:32", [
  ("337", "1일차는 무료!", "Worksheet, website games and support land as three cards, using your real worksheet and Mark's photo.", "Impact, chime, pops. Music up."),
  ("347", "Seven days on a path", "The bear walks all seven days with the page's real titles, and each stop lights up.", "A pop per day, sparkle at the end."),
  ("355", "What's inside", "The page's exact list, with a tick on each row.", "Whoosh and chime per row."),
  ("361", "Real reviews", "The same four as Day 1, with the page's note about illustrated avatars.", "Pops."),
  ("372", "₩47,000", "The price counts up, then one payment, 24 hours, 30 days, then the page's two buttons, and a finger taps the free one.", "Impact, pops, chime."),
  ("377", "Logo", "Your logo as drawn.", "Sparkle."),
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

MUSIC = [
 ("Children Ukulele Upbeat Positive Pop Rock", "ikoliks", "https://pixabay.com/music/upbeat-children-ukulele-upbeat-positive-pop-rock-622115/", "Sounds bright and family-friendly from its title."),
 ("Happy Advertising Hip-Hop (Magic Moments)", "BombinSound", "https://pixabay.com/music/old-school-hip-hop-happy-advertising-hip-hop-magic-moments-628139/", "Closest by title to the hip hop beat in your current video."),
 ("Pop Rock Commercial", "Twisterium", "https://pixabay.com/music/indie-pop-pop-rock-commercial-627431/", "Likely the biggest-sounding, for the offer ending."),
]
music = "".join(f'<li><a href="{u}"><b>{e(n)}</b></a> by {e(a)}. {e(w)}</li>' for n, a, u, w in MUSIC)
own = "엄마·아빠의 걱정부터 내려놓기 · 7일 동안 함께하는 방법 · 무료 1일차와 전체 과정 안내 · 걱정 내려놓기 · 영어를 잘하는 아이 · 가장 중요한 이야기 · 가르치기 ✗ · 함께 사용하기 ✓ · 저희: 표현 · 발음 · 놀이 아이디어 · 부모님: 익숙한 목소리 · 따뜻한 관심 · 자신감의 열쇠 · 우리말로 생각해 볼까요? · 기다리지 않아요 · 이미 알고 있다면요? · 이야기 짓기 · 게임 설명하기 · 매일 이렇게 해요 · 놀이를 시작하는 작은 도구 · 완성 안 해도 OK! · 예상 밖의 놀이 · 반응을 받아주며 계속 놀아요 · 실수해도 괜찮아요 · 실수도 배움 · 오늘의 질문 · 장난치며 웃을 마음 · 놀이 아이디어는 저희가! · 1일차는 무료! · 웹사이트 놀이 게임 · Mark와 Joy의 지원 · 2–7일차, 전체 과정 · 다음 놀이가 열려요"

tpl = open(f"{ROOT}/projects/2026-11-day1-class/storyboard/build_page.py", encoding="utf8").read()
css = tpl[tpl.index('<meta name="claude:viewport-fit-sides"'):tpl.index("</style>") + 8].replace("{{", "{").replace("}}", "}")
page = "<title>Day 0 Welcome Storyboard</title>\n" + css + f"""
<div class="wrap">
<header>
  <span class="status">Waiting for your approval. Nothing is exported yet.</span>
  <h1>Day 0: Welcome to Little Steps</h1>
  <p>Your welcome film, rebuilt from the clean footage. You now stand in an animated sky with words behind your heads, something new lands every few seconds, and a new ending reveals the free Day 1 and everything families get.</p>
  <div class="facts"><span><b>Length</b> 6:19 (the live video is 6:18)</span><span><b>Picture</b> 1920×1080, from a 1080p source</span><span><b>Speed</b> no footage sped up</span><span><b>Cuts and captions</b> yours, from CapCut</span><span><b>On-screen moments</b> about 120</span><span><b>Sound effects</b> about 150</span></div>
</header>
<section class="block">
  <h2>Watch the sample</h2>
  <video controls preload="metadata" playsinline src="sample.mp4"></video>
  <p class="muted">About 75 seconds of the real edit, jumping between five parts: the open, USE and Hello/Look/Your turn, the talking bear, the free Day 1 card, and the price and logo. It's 720p to keep it light, and <b>it has no music yet</b>, because you choose the track. The voices have been cleaned up. I can't hear audio, so please check that they sound natural.</p>
</section>
<section class="block act">
  <h2>Your decisions</h2>
  <ul>
    <li><b>Music: please listen and pick one.</b> I can't hear these, so the notes come only from their titles.<ul>{music}</ul>All three are on Pixabay, whose licence allows free commercial use. Pixabay warns that some tracks can still trigger an automatic YouTube copyright claim, so I'd upload the video unlisted first to check. If you'd rather use a paid library, send me the track.</li>
    <li><b>Title.</b> I used “Welcome to Little Steps” with “Mark와 Joy가 전하는 첫 인사”, from your YouTube title and the page, with “DAY 0” on the title card. Is that right?</li>
    <li><b>Say the offer on camera?</b> You don't mention the price or what's included in the footage, so the ending uses graphics and music only. If you and Joy film 20–30 seconds in the same spot and clothes, I'll put you in the sky for the offer too.</li>
    <li><b>Backgrounds.</b> The skies are placeholders I generated. Your Day 1 thumbnail's watercolour sky and flowers are lovelier. If you make 3–4 versions of that without people in ChatGPT, I'll swap them in. Tell me and I'll write the prompt.</li>
    <li><b>Offer wording.</b> Day 1 “support from Mark and Joy” comes from your notes, and the page says Kakao support runs for the first 7 days. Please confirm the free day includes it.</li>
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
