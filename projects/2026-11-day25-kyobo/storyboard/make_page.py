"""Builds the Day 25 storyboard page (stills embedded, sample video published beside it).
Run from the repo root: .venv/bin/python projects/2026-11-day25-kyobo/storyboard/make_page.py OUT_HTML"""
import base64, html, subprocess, sys, os
H = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1]
SHOTS = [
    (1.5, "Hook", "Mark on the bench; real audio asks the question. \"TOP 3\" sits behind his head. DAY 25 badge."),
    (9, "Kyobo", "\"This is Kyobo, Seoul's most famous bookshop…\" Name tag for Mark."),
    (14.5, "The quote", "Closer, slowed shot of the stones. 사람은 책을 만들고 / 책은 사람을 만든다 pops in as he says it."),
    (19, "Inside", "Walking in. \"TOP 3\" pop."),
    (22.5, "Save it", "Picture-book table. \"📌 저장 필수!\" pop to drive saves."),
    (25.5, "Book 1", "Close on Mum, Me and the Mulberry Tree in Mark's hands. \"No.1 · BEDTIME\" with a punch zoom."),
    (33.5, "Mulberry Tree", "Close on the cover. English keyword pops: GENTLE, SLOW & COZY, TOGETHER."),
    (38, "Book 2", "Room on the Broom. \"No.2 · RHYME\"."),
    (42.5, "Rhythm", "REPEAT, RHYTHM, KINDNESS pops."),
    (50, "Book 3", "I Love You Through and Through. \"No.3 · LOVE\"."),
    (55, "Cuddle", "SIMPLE, CUDDLE pops."),
    (62.5, "Bonus", "Cut to the Oxford watercolour. \"🎁 BONUS\", \"COMING SOON\"."),
    (67, "Book 1 reveal", "Bear & Joy cover bounces in with a light sweep and sparkles."),
    (73, "Reserve", "\"🐻 BEAR · 댓글 = 예약\"."),
    (76.5, "First in Korea", "\"FIRST IN KOREA 🇰🇷\"."),
    (79.5, "End card", "Follow tap, \"🐻 댓글 남기고 Book 1 예약하기\", Kakao button."),
]
cards = []
for t, name, note in SHOTS:
    src = f"{H}/stills/t{t:g}.jpg"
    jpg = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", "scale=432:-1", "-q:v", "4", "-f", "image2", "-"], capture_output=True, check=True).stdout
    m, s = divmod(t, 60)
    cards.append(f'<figure class="shot"><img src="data:image/jpeg;base64,{base64.b64encode(jpg).decode()}" alt="{html.escape(name)} at {t:g} seconds" loading="lazy">'
                 f'<figcaption><span class="tc">{int(m)}:{s:04.1f}</span><b>{html.escape(name)}</b><p>{html.escape(note)}</p></figcaption></figure>')
page = open(f"{H}/page.tmpl.html", encoding="utf8").read().replace("{{SHOTS}}", "\n".join(cards))
open(out, "w", encoding="utf8").write(page)
print("wrote", out, len(page) // 1024, "KB")
