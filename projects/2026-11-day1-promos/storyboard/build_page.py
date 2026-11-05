"""Storyboard page for the three Day 1 Instagram promos. Output: renders/day1/ig/page/index.html"""
import html, json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(f"{HERE}/../../..")
IG, OUT = f"{ROOT}/renders/day1/ig", f"{ROOT}/renders/day1/ig/page"
os.makedirs(f"{OUT}/stills", exist_ok=True)
e = html.escape
V = [
 ("kkakkung", "A. 까꿍 game", "The most visual one. It opens on “Where's the bear?”, shows the window opening, then the tiny voice, then the 함께 message.",
  ["Hook: 창문 하나로 영어 까꿍 놀이!", "The window starts to open", "까꿍! The bear appears", "놀이 완성!", "Tiny voice", "Happy voice", "함께, behind Joy", "Try Day 1 free"],
  [1, 5, 8.5, 11.5, 18, 21.5, 27.5, 33]),
 ("three-phrases", "B. Three phrases", "The most useful one. Mark teaches all three phrases fast, repeats them, then reassures parents.",
  ["Hook: 아이와 오늘 바로 쓰는 영어 세 문장", "Phrase 1, with the bear", "Phrase 2, curious voice", "Phrase 3, a big reveal", "All three together", "다 기억 안 해도 돼요", "You can always come back", "Try Day 1 free"],
  [1, 5, 7.5, 9.5, 14, 24, 28, 33]),
 ("mistakes-ok", "C. Mistakes are OK", "The most emotional one, for parents who worry about their own English. It uses only Joy talking to camera.",
  ["Hook: 영어로 다시 말해봐? 안 해도 돼요", "함께, behind Joy", "Nobody plays 까꿍 for right answers", "Smile and play together", "실수 OK, behind Joy", "조금씩 자신감", "Try Day 1 free"],
  [1, 6, 10, 15, 22, 26, 32]),
]
blocks = []
for name, title, why, labels, times in V:
    plan = json.load(open(f"{ROOT}/projects/2026-11-day1-promos/versions/{name}/timeline.json"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{IG}/final/{name}.mp4", "-vf", "scale=720:-2", "-c:v", "libx264", "-preset", "slow", "-b:v", "1500k", "-maxrate", "2200k", "-bufsize", "4400k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", f"{OUT}/{name}.mp4"], check=True)
    figs = ""
    for t, lab in zip(times, labels):
        fn = f"{name}-t{t:g}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{IG}/sb-{name}/t{t:g}.jpg", "-vf", "scale=480:-1", "-q:v", "5", f"{OUT}/stills/{fn}"], check=True)
        figs += f'<figure><img src="stills/{fn}" alt="{e(lab)}" loading="lazy" width="480" height="853"><figcaption><b>0:{int(t):02d}</b> {e(lab)}</figcaption></figure>'
    d = plan["duration"]
    blocks.append(f'''<section class="cut"><div class="lead"><div class="side"><h2>{e(title)}</h2><p class="facts">{int(d // 60)}:{int(d % 60):02d} long</p><p>{e(why)}</p></div>
<video controls preload="metadata" playsinline src="{name}.mp4"></video></div><div class="strip">{figs}</div></section>''')

page = f"""<title>Day 1 Instagram Promos</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;700;900&display=swap">
<style>
/* Layout: one row per cut. The playable preview sits beside its reason, with its frames in a sideways strip below. Brand pastels. */
:root {{ --bg:#FBF9EE; --fg:#14203A; --muted:#55607A; --line:#DDDCCB; --butter:#F6F0BA; --on:#14203A; --f:"Noto Sans KR","Apple SD Gothic Neo",system-ui,sans-serif; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#14203A; --fg:#F5F0E6; --muted:#AEB8CC; --line:#2E3C5C; color-scheme:dark }} }}
:root[data-theme="dark"] {{ --bg:#14203A; --fg:#F5F0E6; --muted:#AEB8CC; --line:#2E3C5C; color-scheme:dark }}
body {{ background:var(--bg); color:var(--fg); font-family:var(--f); font-size:16px; line-height:1.65; }}
.wrap {{ max-width:1080px; margin:0 auto; padding-block:40px 72px; padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)); display:grid; gap:44px; }}
h1 {{ font-size:clamp(32px,5vw,50px); line-height:1.12; font-weight:900; letter-spacing:-.025em; margin:0; }}
h2 {{ font-size:25px; line-height:1.3; font-weight:900; margin:0; }}
p {{ margin:0; max-width:65ch; }}
header, .notes {{ display:grid; gap:14px; }}
.status {{ justify-self:start; background:var(--butter); color:var(--on); font-weight:700; font-size:14px; padding:5px 14px; border-radius:99px; }}
.cut {{ display:grid; gap:20px; border-top:2px solid var(--line); padding-top:24px; }}
.lead {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,320px); gap:28px; align-items:start; }}
.side {{ display:grid; gap:10px; min-width:0; }}
.facts {{ color:var(--muted); font-size:15px; }}
video {{ width:100%; max-width:100%; aspect-ratio:9/16; border-radius:14px; background:#14203A; display:block; }}
.strip {{ display:flex; gap:12px; overflow-x:auto; padding-bottom:8px; }}
figure {{ margin:0; flex:0 0 170px; display:grid; gap:6px; }}
figure img {{ width:100%; height:auto; border-radius:10px; display:block; }}
figcaption {{ font-size:14px; line-height:1.4; color:var(--muted); }} figcaption b {{ color:var(--fg); font-variant-numeric:tabular-nums; }}
ul {{ margin:0; padding-left:20px; display:grid; gap:8px; max-width:70ch; }}
@media (max-width:640px) {{ .lead {{ grid-template-columns:minmax(0,1fr); }} }}
</style>
<div class="wrap">
<header>
  <span class="status">Waiting for your approval. Nothing is exported yet.</span>
  <h1>Day 1 Instagram promos</h1>
  <p>Three vertical cuts from the Day 1 class, each with a different hook, all ending on “1일차 무료로 시작하기”. These previews are 720p with the real sound. The final versions will be 1080×1920.</p>
</header>
{''.join(blocks)}
<section class="cut notes">
  <h2>Please decide or check</h2>
  <ul>
    <li><b>Series badge.</b> Your Reels rule uses “DAY N · 출간까지 매일 업로드” and a follow card. These are promos, so I used “Little Steps · 첫날 무료” and a try-it-free ending. If they should count as daily posts, tell me the day number.</li>
    <li><b>Music.</b> These use the Reels lo-fi under the voice, about 8–10 dB lower before ducking, close to what BRAND.md asks. Tell me if you'd prefer sound effects only, as in the lesson.</li>
    <li><b>Picture sharpness.</b> The footage is 1080p and a vertical crop enlarges it about 1.8×, so it's softer than Day 23 or 24. A 4K original would fix that.</li>
    <li><b>Mirrored worksheet.</b> The worksheet reads backwards in cut A, as in the class video. The crop removes the burned-in logo, so I can flip these shots to make the worksheet read correctly. Everything else in the shot would flip too, including Joy.</li>
    <li><b>Length.</b> Each runs 34–35 seconds, at the top of your 15–35 second range for reach reels.</li>
    <li><b>Korean to check.</b> Hooks and labels are my wording: 창문 하나로 영어 까꿍 놀이, 아이와 오늘 바로 쓰는 영어 세 문장, 영어로 다시 말해봐? 안 해도 돼요, 놀이 완성, 1일차는 무료예요, 워크시트 · 인터랙티브 게임 · 마크와 조이의 도움까지.</li>
    <li><b>After your OK.</b> Each promo gets an export, a cover image and a Korean caption, in <code>exports/instagram/</code>.</li>
  </ul>
</section>
</div>
"""
open(f"{OUT}/index.html", "w", encoding="utf8").write(page)
print("page", len(page))
