"""Builds the Day 1 storyboard page (approved layout from the Day 6 storyboard). Output: renders/day1/page/index.html + stills/."""
import html, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(f"{HERE}/../../..")
SB, OUT = f"{ROOT}/renders/day1/sb2", f"{ROOT}/renders/day1/page"
os.makedirs(f"{OUT}/stills", exist_ok=True)
e = html.escape

ACTS = [
 ("Title, today's plan and countdown", "0:00", [
  ("13", "0:13", "Animated title", "The bear walks in over Mark's greeting. This also hides the logo overlay burned into the start of the footage.", "Sparkle, then a whoosh as the card lifts."),
  ("17", "0:06", "Mark's first line", "Korean captions start here, using Joy's translation.", "No effect."),
  ("28", "0:17", "Today's plan", "The three parts appear as Mark describes them, with how long each one takes. The caption moves right to clear the small Joy preview already in the footage.", "Whoosh, and a soft pop for each step."),
  ("37", "0:26", "READY?", "The first word behind Mark's head.", "Sparkle."),
  ("39", "0:28", "3, 2, 1", "A countdown with a ring runs over “Let's begin” and ends exactly as the first phrase starts.", "A pop on each number, then a chime."),
 ]),
 ("Phrase 1: Look! It's a bear!", "0:41", [
  ("42", "0:42", "Listen", "The Day 6 card: English, pronunciation, meaning. Each word lights up as Mark says it.", "Whoosh and sparkle as he shows the bear."),
  ("58", "0:58", "Your turn", "The yellow chip and countdown bar run for the pause Mark leaves.", "Chime."),
  ("62", "1:02", "Flow", "A curved line joins it's and a.", "No effect."),
  ("68", "1:08", "Excitement", "Look! turns yellow and pulses.", "No effect."),
  ("73", "1:13", "Show the bear", "The whole phrase returns as Mark shows the card.", "Sparkle."),
 ]),
 ("Phrase 2: Where's the bear?", "1:21", [
  ("90", "1:30", "One word", "Where is → Where's, with the two words joined.", "No effect."),
  ("100", "1:40", "Your turn", "The same chip and bar, so viewers know where to look.", "Chime."),
  ("105", "1:45", "Curious voice", "An arrow shows the voice rising.", "No effect."),
  ("110.5", "1:50", "Hide the bear", "A question mark pops in as Mark looks around.", "Soft pop."),
 ]),
 ("Phrase 3: There he is!", "1:57", [
  ("130", "2:10", "Your turn", "The same layout for the third phrase.", "Chime."),
  ("136.5", "2:16", "찾았다!", "“Let your voice smile”: the phrase glows while a word sits behind Mark.", "Sparkle."),
  ("155", "2:35", "All three", "Three rows build up, and each one lights as he says it.", "Pop on each row."),
 ]),
 ("Joy's game", "2:50", [
  ("170.25", "2:50", "Handover", "The bear crosses the screen to take us to Joy.", "Whoosh."),
  ("187", "3:07", "Getting ready", "Small labels sit away from the worksheet and repeat the steps.", "Soft pop."),
  ("204", "3:24", "Step 1", "A shorter card, so the worksheet stays visible.", "Whoosh, sparkle."),
  ("223", "3:43", "Step 3: 까꿍!", "The window opens with the biggest moment of her section.", "Sparkle burst."),
  ("232", "3:52", "The one sales note", "One small line while she finishes the first game. It's on screen for 5 seconds.", "Very soft pop."),
  ("240", "4:00", "Tiny voice", "The English shrinks to match her voice, and the pronunciation stays readable.", "Whoosh."),
 ]),
 ("Fit your child, and why we play", "4:17", [
  ("262", "4:22", "Baby", "A card for each kind of child, kept to one side.", "Pop."),
  ("270", "4:30", "Confident child", "The child gets to ask the question.", "Pop."),
  ("277", "4:37", "“여기!”", "Answering in Korean is fine.", "Pop."),
  ("294", "4:54", "함께", "The brand's key message, with the biggest word in the video behind Joy.", "Sparkle."),
  ("310", "5:10", "Mistakes are fine", "A short reassurance while she talks.", "Pop."),
  ("350", "5:50", "작은 모험", "The final word behind Joy, just before she says goodbye.", "Sparkle."),
 ]),
 ("Ending (new, with music)", "5:57", [
  ("360", "6:00", "Recap", "The three phrases, with Day 2 named underneath.", "Music rises under Joy's goodbye. Sparkle and a pop on each row."),
  ("368", "6:08", "Parents' words", "The four reviews from your page, with their illustrated pictures and the page's note about them.", "Pop on each card."),
  ("377", "6:17", "The offer", "Days 2–7 with the page's titles, what's included and the page's own button wording.", "Sparkle when the price arrives."),
  ("384", "6:24", "Logo", "Your logo, then a fade.", "Chime as the music fades out."),
 ]),
]

# Times above were written before the cold open was dropped: every moment is 11 s earlier now.
def mmss(x): return f"{int(x // 60)}:{int(x % 60):02d}"
def back(tm):
    a, b = tm.split(":"); return mmss(max(0, int(a) * 60 + int(b) - 11))
def scene(a):
    s, tm, h, body, snd = a
    s = f"{float(s) - 11:g}"; tm = mmss(float(s))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SB}/t{s}.jpg", "-vf", "scale=1280:-1", "-q:v", "5", f"{OUT}/stills/t{s}.jpg"], check=True)
    return (f'<article class="scene"><img src="stills/t{s}.jpg" alt="{e(h)} at {tm}" loading="lazy" width="1280" height="720"><div class="note"><div class="time">{tm}</div>'
            f'<h3>{e(h)}</h3><p>{e(body)}</p><p class="sound"><b>Sound</b> {e(snd)}</p></div></article>')

acts = "".join(f'<section class="act"><h2>{e(t)} <span class="at">from {back(at)}</span></h2>{"".join(scene(a) for a in rows)}</section>' for t, at, rows in ACTS)

def table(head, rows, cls=()):
    th = "".join(f"<th>{e(h)}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f'<td class="{cls[i] if i < len(cls) else ""}">{c if c.startswith("<") else e(c)}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><tr>{th}</tr>{tr}</table></div>'

pron = table(["English", "Korean pronunciation (my draft)", "Meaning (Joy's)"], [
 ["Look! It's a bear!", '<span class="pill">룩! 잇츠 어 베어!</span>', "봐! 곰이야!"],
 ["Where's the bear?", '<span class="pill">웨어즈 더 베어?</span>', "곰이 어디 있지?"],
 ["There he is!", '<span class="pill">데어 히 이즈!</span>', "여기 있었네!"]], ("ko", "", "ko"))

joy = table(["Moment", "Script", "On camera", "On screen"], [
 ["2:40", "마크와 오늘의 세 문장을 연습해 봤어요.", "…연습 잘 해보셨나요?", "What she says"],
 ["2:53", "워크시트는… 보호자께서 미리 잘라 준비해 주세요.", "우리 부모님께서 미리 잘라주세요.", "What she says"],
 ["3:12", "(card) 봐! 곰이야!", "봐, 여기 곰이 있어.", "The card keeps “봐! 곰이야!”, so it matches Mark's lesson"],
 ["4:20", "아이가 물으면 부모님이 창문을 열어주는 거죠.", "같은 뜻, 조금 더 길게", "Shortened for reading speed: 창문을 열어주세요"],
 ["4:28", "…자연스럽게 이어가 주세요.", "Yes! Right! There he is! 라고 말해주면 돼요.", "Shortened for reading speed: 받아주면서… 말해주세요"],
 ["5:04", "“나도 한번 해 봐도 괜찮겠구나”", "The recogniser heard “해보면 좋겠는걸?”", "<b>Please check.</b> I used the script's wording"],
 ["5:42", "(not in the script)", "Have fun! We'll see you on Day 2! Bye bye!", "My translation: 즐겁게 놀아요! 2일차에 만나요! 안녕!"]])

own = table(["Where", "My wording"], [
 ["Mark's praise, not in the script", "좋아요! · 아주 잘했어요! (his “Great”, “Good” and “Excellent”, using the Day 6 wording)"],
 ["Small labels", "놀이 전에 미리 잘라요 · 접는 부분 · 손잡이는 남겨요 · 부모님이 손잡이를 잡아요"],
 ["Child cards", "아직 아기라면 / 부모님이 묻고, 답해요 · 영어가 익숙하다면 / 아이가 묻는 역할을 해요 · “여기!”라고 말해도 / 좋아요! 받아주세요"],
 ["Today's plan and countdown", "오늘의 순서 · 세 가지 표현 / 마크와 연습해요 · 까꿍 놀이 / 조이가 보여줘요 · 우리 아이에 맞게 / 놀이 팁과 이유 · 첫 번째 표현까지"],
 ["Sales note", "7일 동안 매일 새로운 놀이가 이어져요"],
 ["Offer heading", "첫걸음을 뗐다면, 다음 날도 함께해요"],
 ["Offer details", "2–7일차, 24시간마다 하나씩 열려요 · 시작일부터 30일 동안 다시 보기 · 한 번만 결제해요 · 정기결제가 아니에요"]], ("", "ko"))

page = f"""<title>Day 1 Hello Little Bear Storyboard</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;700;900&display=swap">
<style>
/* Layout: the shot list approved on Day 6. A real frame on the left, timing and sound on the right. Colours are the brand pastels. */
:root {{ --bg:#FBF9EE; --fg:#14203A; --muted:#55607A; --line:#DDDCCB; --panel:#FFFFFF; --butter:#F6F0BA; --sky:#AECCE6; --on:#14203A;
  --f:"Noto Sans KR","Apple SD Gothic Neo",system-ui,sans-serif; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#14203A; --fg:#F5F0E6; --muted:#AEB8CC; --line:#2E3C5C; --panel:#1E2D4D; color-scheme:dark }} }}
:root[data-theme="dark"] {{ --bg:#14203A; --fg:#F5F0E6; --muted:#AEB8CC; --line:#2E3C5C; --panel:#1E2D4D; color-scheme:dark }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--f); font-size:16px; line-height:1.65; }}
.wrap {{ max-width:1080px; margin:0 auto; padding-block:40px 72px; padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)); display:grid; gap:44px; }}
h1 {{ font-size:clamp(32px,5vw,50px); line-height:1.12; font-weight:900; letter-spacing:-.025em; margin:0; text-wrap:balance; }}
h2 {{ font-size:25px; line-height:1.3; font-weight:900; letter-spacing:-.015em; margin:0; text-wrap:balance; }}
h3 {{ font-size:18px; line-height:1.35; font-weight:700; margin:0; }}
p {{ margin:0; max-width:65ch; }}
.status {{ justify-self:start; background:var(--butter); color:var(--on); font-weight:700; font-size:14px; padding:5px 14px; border-radius:99px; }}
header {{ display:grid; gap:14px; }}
.facts {{ display:flex; flex-wrap:wrap; gap:6px 24px; color:var(--muted); font-size:15px; }} .facts b {{ color:var(--fg); }}
.block {{ display:grid; gap:14px; }}
video {{ width:100%; max-width:100%; aspect-ratio:16/9; border-radius:14px; background:#14203A; display:block; }}
.muted {{ color:var(--muted); }}
.act {{ display:grid; gap:22px; border-top:2px solid var(--line); padding-top:24px; }}
.at {{ color:var(--muted); font-size:15px; font-weight:500; margin-left:6px; white-space:nowrap; }}
.scene {{ display:grid; grid-template-columns:minmax(0,1.75fr) minmax(0,1fr); gap:24px; align-items:start; }}
.scene img {{ width:100%; height:auto; border-radius:12px; display:block; }}
.note {{ display:grid; gap:7px; min-width:0; }}
.time {{ font-variant-numeric:tabular-nums; font-weight:700; color:var(--muted); font-size:14px; }}
.sound {{ color:var(--muted); font-size:15px; }} .sound b {{ color:var(--fg); margin-right:4px; }}
.scroll {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; min-width:520px; font-size:15.5px; }}
th {{ text-align:left; font-size:13.5px; color:var(--muted); font-weight:700; padding:8px 14px 8px 0; border-bottom:2px solid var(--line); }}
td {{ padding:10px 14px 10px 0; border-bottom:1px solid var(--line); vertical-align:top; }}
.ko {{ font-weight:700; }}
.pill {{ background:var(--sky); color:var(--on); font-weight:700; padding:2px 12px; border-radius:99px; white-space:nowrap; }}
ul {{ margin:0; padding-left:20px; display:grid; gap:8px; max-width:70ch; }}
@media (max-width:720px) {{ .scene {{ grid-template-columns:minmax(0,1fr); gap:12px; }} }}
</style>
<div class="wrap">
<header>
  <span class="status">Waiting for your approval. Nothing is exported yet.</span>
  <h1>Day 1: Hello, Little Bear!</h1>
  <p>The free day, built to make parents want Day 2. It keeps the Day 6 teaching cards and adds an animated title, a clear plan for the lesson, a countdown, words behind Mark and Joy, parents' reviews and the offer, with music under the ending.</p>
  <div class="facts"><span><b>Length</b> 6:15</span><span><b>Picture</b> 1920×1080, from a 1080p source</span><span><b>Speed</b> no footage sped up</span><span><b>Sound</b> voices and sound effects, with music from the goodbye to the end</span></div>
</header>

<section class="block">
  <h2>Watch the sample</h2>
  <video controls preload="metadata" playsinline src="sample.mp4"></video>
  <p class="muted">The first 1:06, which covers the title, the plan, the countdown and all of phrase 1, then Joy's goodbye and the ending with the music. It's 720p with the real sound. Please judge the music and sound effect levels by ear, because I can only measure them. The full mix measures -14.0 LUFS, with peaks at -1.5 dB.</p>
</section>

<section class="block act">
  <h2>Please decide or check</h2>
  <ul>
    <li><b>Name.</b> You called it “Hello, Bear”, the script says “Hello, Little Bear!” and the page says “안녕, 곰아!”. I used “Hello, Little Bear!” with “안녕, 곰아!”, which also matches the worksheet.</li>
    <li><b>Little Steps or First Steps.</b> The script says “First Steps”, but Mark says “Little Steps” on camera. The caption says Little Steps.</li>
    <li><b>Lesson times.</b> The plan says about 2 minutes, 1:30 and 2 minutes, rounded from the real sections of the video.</li>
    <li><b>Mirrored worksheet.</b> Joy's worksheet reads backwards in the footage, including its “Hello, little Bear” title. The logo is burned in the normal way round, so I can't flip the picture without flipping the logo. A version without the logo would let me fix this.</li>
    <li><b>Burned-in logo.</b> It stays in the top-left corner throughout, as in the source. I've kept my labels away from it.</li>
    <li><b>Offer wording.</b> You said Days 2–7 are unlocked, but the page says they open one every 24 hours, so the card follows the page. Tell me if the page is out of date.</li>
  </ul>
</section>

{acts}

<section class="block act">
  <h2>Pronunciation to approve</h2>
  <p class="muted">These are the largest Korean words on screen and they weren't in the script, so they are my draft in the style of your Day 6 card.</p>
  {pron}
</section>

<section class="block act">
  <h2>Where Joy's captions differ from her script</h2>
  <p class="muted">Joy mostly follows the script. Where she changed a line, the caption follows what viewers hear, unless the table says otherwise. Mark's captions are Joy's translation, word for word, with “First Steps” changed to “Little Steps”.</p>
  {joy}
  <p class="muted">All 68 captions stay on screen for at least 1.2 seconds. 58 are at 6 Korean characters per second or less. The other 10 run a little faster, up to 6.5, because I kept the wording rather than shorten it further.</p>
</section>

<section class="block act">
  <h2>My Korean, for a fluent speaker to read</h2>
  <p class="muted">None of this comes from the script or the page's exact sentences, and it's your main sales video, so please have Joy read it before export.</p>
  {own}
</section>
</div>
"""
open(f"{OUT}/index.html", "w", encoding="utf8").write(page)
print("page written", len(page))
