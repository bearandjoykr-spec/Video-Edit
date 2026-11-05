"""Day 0 (internal name) "Little Steps to Big Adventures" plan (re-edit of the current welcome film, Little Steps page).

Run: .venv/bin/python projects/2026-11-day0-welcome/build_timeline.py
Writes versions/main/timeline.json and prints the caption reading-speed table.
Cuts and Korean captions are the owner's, read from the CapCut "Day 0" project (capcut-timeline.txt), word for word.
c(t) converts a CapCut time to output time. Korean written for this edit is listed in KOREAN_TO_CHECK for Joy.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
MONTAGE = 12.3                 # the owner's film-style opening, as rendered
TITLE = 3.0; PROMISE = 3.0     # title, then what's coming (owner's rule: tell them what's coming)
SHIFT = TITLE + PROMISE        # every moment in the owner's edit moves this far later
INTRO = MONTAGE + SHIFT
o = lambda t: round(t + SHIFT, 3)   # owner's edit time -> this video's time

# The talk uses the owner's own cuts (owner-cuts.json, found by align_owner_edit.py); small gaps are closed.
OWNER = [(12.3, 0.3), (50.5, 39.5), (53.5, 44.1), (62.8, 54.4), (156.2, 148.8), (164.1, 159.4), (171.2, 168.2), (187.8, 186.6), (293.7, 296.6), (308.4, 315.8)]
OWNER_END = 337.5
segments = []
for k, (a, src) in enumerate(OWNER):
    b = OWNER[k + 1][0] if k + 1 < len(OWNER) else OWNER_END
    segments.append({"src_s": src, "src_e": round(src + b - a, 3), "out_s": o(a)})
MAIN_END = o(OWNER_END)

# CapCut clock (the captions and my first cue list) -> source -> this video
CAP = []
for line in open(f"{HERE}/capcut-timeline.txt"):
    g = re.match(r"\s*([\d.]+)\s+([\d.]+) src\s+([\d.]+) VID_", line)
    if g: CAP.append(tuple(map(float, g.groups())))
def c(t):
    src = next((sr + t - a for a, b, sr in CAP if a <= t < b), None)
    if src is None:
        src = CAP[0][2] if t < CAP[0][0] else CAP[-1][2] + t - CAP[-1][0]
    for g in segments:
        if g["src_s"] <= src < g["src_e"]: return round(g["out_s"] + src - g["src_s"], 3)
    nxt = [g for g in segments if g["src_s"] >= src]
    return nxt[0]["out_s"] if nxt else MAIN_END

# ------------------------------------------------------------ the owner's captions, one yellow word each
KEYS = ["걱정", "Little Steps", "little step", "7일", "작은 순간", "영어를 더해", "함께", "너무 이른", "너무 쉬운", "가장 중요하게", "사용하세요", "사용해", "의미", "“Hello”", "“Look!“", "“Your turn”",
        "부모님의 역할", "표현과 발음", "놀이 아이디어", "따뜻한 관심", "웃게", "재밌네", "한번 해 볼 수", "다 맞힐", "자신감", "열쇠", "유창한", "우리말", "잘 잤어", "배고파", "양말", "대답할", "자연스럽게", "조금씩",
        "우리 아가", "곰이다", "이미", "더 많은 걸", "새로운 놀이", "곰의 목소리", "이야기를", "게임", "난 곰이야", "아침밥", "배가 고픈", "짧은 표현", "아이의 생각", "매일", "천천히", "연습할", "워크시트", "도구", "완성", "활동 방법",
        "화면", "표현 하나", "잠깐", "어떤 반응", "한국어로", "손가락", "재미있는 소리", "예상하지", "받아주며", "영어로 말해", "실수도", "배우는", "웃어도", "다시", "가볍게", "앗!", "이어갈", "서툴고", "질문", "함께한 순간", "발견", "첫걸음", "호기심", "서툰 영어", "장난치며", "저희가 준비", "첫 번째 문", "DAY 1", "조이", "마크", "환영"]
captions = []
caps = []
for line in open(f"{HERE}/capcut-timeline.txt"):
    g = re.match(r"\s*([\d.]+)\s+([\d.]+) '(.*)'\s*$", line) or re.match(r'\s*([\d.]+)\s+([\d.]+) "(.*)"\s*$', line)
    if g and g.group(3) not in ("", "Mark", "Joy"):
        caps.append((float(g.group(1)), float(g.group(2)), g.group(3).strip()))
for i, (a, b, ko) in enumerate(caps):
    hi = next((k for k in KEYS if k in ko), "")
    nxt = caps[i + 1][0] if i + 1 < len(caps) else b + 1
    end = max(b, min(a + 1.2, nxt))     # at least 1.2 s where the next line allows it
    end = min(end + .25, nxt)           # hold slightly into a pause
    captions.append({"s": c(a), "e": max(c(end), c(a) + 1.0), "ko": ko, "hi": hi, "cap": a})

# ------------------------------------------------------------ helpers
ev, sfx, shakes = [], [], []
def cue(t, sound, gain=-20): sfx.append({"t": round(t, 3), "sound": sound, "gain": gain})
def add(type_, s, e, sound=None, gain=-20, **k):
    ev.append({"type": type_, "s": s, "e": e, **k})
    if sound: cue(s, sound, gain)
def behind(s, e, big, small=None, tone="butter", size=300, y=40, sound="sparkle"):
    size = min(size, 190 if small else 210)   # keep the word readable above their heads
    add("behind", c(s), c(e), sound, -19, big=big, small=small, tone=tone, size=size, y=y)
def phrase(s, e, text, hot=(), y=48, size=92, sound="whoosh"):
    add("phrase", c(s), c(e), sound, -24, text=text, hot=list(hot), y=y, size=size)
def chip(s, e, text, emoji=None, x=None, right=None, y=200, tone="butter", size=44, sound="pop"):
    add("chip", c(s), c(e), sound, -21, text=text, emoji=emoji, x=x, right=right, y=y, tone=tone, size=size)
def bubble(s, e, text, x=None, right=None, y=140, w=560, size=50, sound="pop"):
    add("bubble", c(s), c(e), sound, -20, text=text, x=x, right=right, y=y, w=w, size=size)
def burst(s, x, y, emoji, n=18, d=1.8, sound="sparkle"):
    add("burst", c(s), c(s) + d, sound, -21, x=x, y=y, emoji=emoji, n=n)
def stamp(s, e, big, small=None, x=None, right=None, y=120, size=92, rot=-7):
    add("stamp", c(s), c(e), "impact", -17, big=big, small=small, x=x, right=right, y=y, size=size, rot=rot)
    shakes.append(c(s))
def hit(s): shakes.append(c(s)); cue(c(s), "impact", -18)
def wipe(s, text=None, color="#F6F0BA"):
    add("wipe", c(s) - .45, c(s) + .45, "whoosh", -17, text=text, color=color)

# ------------------------------------------------------------ the open
add("montage", 0, MONTAGE)
add("wipe", MONTAGE - .4, MONTAGE + .4, "whoosh", -16, text=None, color="#AECCE6")
add("title", MONTAGE, MONTAGE + TITLE + .1, "sparkle", -17)
cue(MONTAGE + .5, "whoosh", -20); cue(MONTAGE + .9, "pop", -18); cue(MONTAGE + 1.2, "pop", -19)
p0 = MONTAGE + TITLE
add("promise", p0, INTRO, "whoosh", -20, rows=[
    {"emoji": "🧸", "text": "엄마·아빠의 걱정부터 내려놓기", "at": p0 + .2},
    {"emoji": "✏️", "text": "7일 동안 함께하는 방법", "at": p0 + .7},
    {"emoji": "🎁", "text": "무료 1일차와 전체 과정 안내", "at": p0 + 1.2}])
cue(p0 + .2, "pop", -20); cue(p0 + .7, "pop", -20); cue(p0 + 1.2, "pop", -19)
add("wipe", INTRO - .4, INTRO + .4, "whoosh", -17, text=None, color="#F6F0BA")

# ------------------------------------------------------------ hello
chip(4.43, 6.7, "Joy", x=1060, y=640, tone="butter", size=54, sound="chime")
chip(5.4, 6.7, "Mark", x=360, y=640, tone="butter", size=54, sound="chime")
phrase(6.77, 9.1, "And welcome to Bear & Joy", (3, 4, 5))
behind(9.3, 11.0, "Little Steps", size=230, y=40)
burst(9.5, 1640, 300, ["✨", "🦋", "⭐"])
add("mini", c(11.0), c(16.2))
chip(10.97, 16.2, "앞으로 7일", "🗓️", right=44, y=120, tone="sky", size=50)
phrase(16.43, 19.3, "the first little step is not to worry", (5, 6, 7))
chip(17.9, 21.8, "걱정 내려놓기", "☁️", x=64, y=180, tone="butter")
phrase(19.5, 21.8, "that's why we're here to help", (3, 4, 5, 6), y=165, size=60, sound=None)

bubble(25.4, 33.9, "“너무 이른 건 아닐까요?”", right=64, y=90, w=390, size=46, sound="pop")
bubble(29.3, 33.9, "“너무 쉬운 건 아닐까요?”", right=64, y=430, w=390, size=46)
chip(25.4, 33.9, "아기", "👶", right=64, y=290, tone="sky", sound=None)
chip(29.3, 33.9, "영어를 잘하는 아이", "🌟", right=64, y=630, tone="sky", size=38, sound=None)
behind(36.0, 40.7, "가장 중요한 이야기", size=170, y=40)

# ------------------------------------------------------------ don't teach: use
wipe(41.4, "Don't teach: USE")
add("scene", c(41.4), c(41.4))
behind(42.1, 47.9, "USE", small="Don't teach:", size=300, y=40, sound=None)
hit(42.4)
burst(42.4, 1660, 420, ["⭐", "✨", "💛"], n=26, sound=None)
chip(44.9, 48.1, "가르치기 ✗", x=64, y=620, tone="navy", sound="pop")
chip(46.53, 51.2, "함께 사용하기 ✓", right=64, y=620, tone="butter")
chip(48.13, 54.7, "함께하는 순간", "🤝", right=64, y=170, tone="butter", size=46)
chip(51.33, 54.7, "짧은 표현에도 의미가", "💡", right=64, y=300, tone="sky", size=40)
behind(55.03, 57.4, "Hello!", small="becomes a greeting", size=230, y=40)
behind(57.6, 61.1, "Look!", small="becomes a shared discovery", tone="sky", size=230, y=40)
behind(61.4, 65.3, "Your turn", small="becomes an invitation", size=220, y=40)

# ------------------------------------------------------------ parents are the key
add("scene", c(65.4), c(65.4))
behind(65.5, 69.8, "부모님", small="바로 여기에서", size=230, y=40)
hit(65.7)
phrase(70.1, 76.3, "저희: 표현 · 발음 · 놀이 아이디어", (1, 3, 5, 6), size=62)
phrase(76.4, 83.0, "부모님: 익숙한 목소리 · 따뜻한 관심", (1, 2, 4, 5), size=62)
behind(83.2, 87.5, "우리 아이를 웃게", size=170, y=40)
burst(83.6, 1660, 420, ["😄", "😂", "💛"], n=14, sound=None)
bubble(90.3, 96.7, "“영어는 재밌네?”", right=64, y=160, w=390, size=60)
phrase(97.27, 98.9, "something where they can think", (), size=68, sound="whoosh")
bubble(99.4, 104.3, "“I can have a go!”", right=64, y=170, w=390, size=52)
bubble(101.0, 104.3, "“I don't have to get everything right.”", right=64, y=430, w=390, size=42)
behind(104.9, 112.4, "자신감의 열쇠", small="🔑", size=170, y=40)
burst(108.2, 1660, 420, ["🔑", "✨", "⭐"], n=18)
chip(112.57, 118.4, "영어를 말할 때도", "🗣️", right=64, y=170, tone="sky", size=42)
chip(113.9, 118.4, "새로운 것을 배울 때도", "📚", right=64, y=300, tone="butter", size=40)
add("strike", c(118.5), c(122.9), "pop", -20, text="유창한 영어", at=2.6, y=70, size=78)
cue(c(121.1), "boing", -20)

# ------------------------------------------------------------ we don't wait to talk
wipe(122.8, "우리말로 생각해 볼까요?", "#AECCE6")
add("scene", c(122.8), c(122.8))
bubble(128.3, 137.0, "잘 잤어?", right=64, y=90, w=390, size=62)
bubble(129.8, 137.0, "배고파?", right=64, y=290, w=390, size=62)
bubble(131.4, 137.0, "양말 어디 갔지? 🧦", right=64, y=490, w=390, size=54)
chip(137.07, 143.7, "기다리지 않아요", "💬", right=64, y=170, tone="butter", size=40)
chip(139.67, 143.7, "함께 하루를 보내며", "☀️", right=64, y=290, tone="sky", size=38)
behind(143.7, 147.8, "영어도 조금씩", size=180, y=40)
phrase(148.7, 150.5, "Hello, little one", (2, ), size=104)
phrase(151.9, 154.3, "Look! A bear!", (0, ), size=120, sound="whoosh")
burst(152.0, 1660, 560, ["✨", "⭐", "🦋"], sound=None)

# ------------------------------------------------------------ for kids who already know
wipe(155.0, "이미 알고 있다면요?", "#F6F0BA")
add("scene", c(155.0), c(155.0))
phrase(155.63, 159.2, "and if your child already knows these words", (6, 7), size=70)
phrase(159.7, 162.3, "give them somewhere to take them", (2, 3, 4, 5), size=76)
chip(162.43, 168.5, "새로운 놀이", "🎈", right=64, y=170, tone="butter", size=52)
chip(168.63, 178.8, "곰의 목소리", "🐻", right=64, y=170, tone="butter")
chip(172.2, 178.8, "이야기 짓기", "📖", right=64, y=290, tone="sky")
chip(174.97, 178.8, "게임 설명하기", "🎲", right=64, y=410, tone="sky")
add("bear", c(179.47), c(184.0), "boing", -17, x=1440, y=500, h=500)
bubble(179.47, 181.6, "Hello, I'm Bear!", right=64, y=170, size=62, w=390, sound=None)
bubble(181.8, 184.0, "Where's my breakfast?", right=64, y=170, size=58, w=390)
burst(184.1, 1660, 500, ["🍯", "🥞", "🍓"], n=14)
behind(191.2, 196.0, "아이의 생각을 따라가 보세요", size=104, y=40)
burst(191.5, 1660, 420, ["🦋", "✨"], n=16, sound=None)

# ------------------------------------------------------------ what each day looks like
wipe(196.4, "매일 이렇게 해요", "#AECCE6")
add("scene", c(196.4), c(196.4))
phrase(197.07, 201.4, "each day I'll guide you through a few useful phrases", (8, 9), size=68)
stamp(196.9, 201.2, "1일차 무료", x=64, y=190, size=56, rot=-5)
chip(201.93, 207.5, "천천히", "🐢", x=64, y=170, tone="sky", size=54)
chip(204.43, 207.5, "자연스럽게", "🐇", x=64, y=300, tone="butter", size=54)
chip(205.83, 207.5, "연습", "🎤", x=64, y=430, tone="sky", size=54)
add("sheets", c(208.1), o(219.9), "whoosh", -18, days=[1, 4, 6])
cue(c(208.4), "pop", -20); cue(c(208.7), "pop", -20)
chip(216.33, 222.6, "놀이를 시작하는 작은 도구", "✂️", x=64, y=110, tone="butter", size=36)
stamp(220.03, 222.7, "완성 안 해도 OK!", x=64, y=250, size=40)
behind(225.4, 229.6, "화면은 잠시 내려놓고", small="📱", size=140, y=40)
add("chip", c(229.73), c(236.9), "chime", -19, text="Try a phrase.", emoji="1️⃣", right=64, y=170, tone="butter", size=40)
add("chip", c(232.1), c(236.9), "chime", -19, text="Leave a little space.", emoji="2️⃣", right=64, y=290, tone="sky", size=40)
add("chip", c(234.5), c(236.9), "chime", -19, text="See what happens.", emoji="3️⃣", right=64, y=410, tone="butter", size=40)

chip(237.0, 247.0, "한국어로 대답", "🇰🇷", right=64, y=150, tone="sky")
chip(240.2, 247.0, "손가락으로 가리키기", "👉", right=64, y=270, tone="butter", size=36)
chip(242.9, 248.6, "재미있는 소리", "🤪", right=64, y=390, tone="butter")
chip(244.8, 248.6, "예상 밖의 놀이", "🌀", right=64, y=510, tone="sky")
chip(248.67, 253.0, "반응을 받아주며 계속 놀아요", "🙌", right=64, y=170, tone="butter", size=40)
add("strike", c(253.2), c(259.4), "pop", -20, text="“영어로 말해 봐”", at=2.2, y=60, size=78)
cue(c(255.4), "boing", -19)

# ------------------------------------------------------------ mistakes are fine
wipe(259.6, "실수해도 괜찮아요", "#F6F0BA")
add("scene", c(259.6), c(259.6))
behind(259.93, 266.2, "실수도 배움", small="🙈", size=210, y=40)
burst(266.6, 1660, 420, ["😂", "😄", "🔁", "💛"], n=22)
behind(272.0, 276.3, "앗! 다시 해 볼까?", tone="sky", size=170, y=40)
cue(c(272.1), "boing", -18)
phrase(276.73, 281.5, "you're showing your child that learning is something you can keep doing", (5, 6, 7), size=58)
phrase(282.43, 285.3, "even when it gets a little messy", (5, 6), size=80)

chip(285.47, 290.3, "오늘의 질문", "🤔", right=64, y=170, tone="sky", size=50)
# ------------------------------------------------------------ how to know it went well
add("scene", c(285.3), c(285.3))
bubble(290.47, 298.9, "함께한 순간이 있었나? ✓", right=64, y=130, w=390, size=48)
bubble(294.47, 298.9, "함께 발견했나? ✓", right=64, y=390, w=390, size=48)
phrase(300.47, 303.0, "one phrase you actually use", (2, ), size=84)
phrase(303.53, 306.3, "is a lovely little step", (3, 4), size=96)
add("bear", c(303.6), c(306.5), "sparkle", -19, x=1440, y=500, h=440)
chip(306.7, 314.4, "호기심", "🔎", right=64, y=170, tone="butter", size=50)
chip(308.3, 314.4, "조금 서툰 영어", "🗣️", right=64, y=290, tone="sky", size=50)
chip(312.0, 314.4, "장난치며 웃을 마음", "😂", right=64, y=410, tone="sky", size=36)
stamp(315.1, 318.2, "놀이 아이디어는 저희가!", y=210, right=64, size=44, rot=-3)
behind(318.3, 322.2, "첫 번째 문", small="🚪", size=200, y=40)
burst(320.0, 1660, 420, ["✨", "⭐", "🦋"], n=20, sound=None)
stamp(322.47, 325.9, "DAY 1 · 무료", small="그럼 DAY 1에서 만나요!", y=190, right=64, size=62, rot=4)
burst(326.2, 1660, 420, ["👋", "💛"], n=14)

add("progress", INTRO, MAIN_END, marks=[c(41.4), c(122.8), c(155.0), c(196.4), c(259.6)])

# ------------------------------------------------------------ the owner's lesson clips and stickers (times are the owner's edit)
def pip(s, e, clips, tag=None, sound="whoosh"):
    add("pip", o(s), o(e), sound, -19, clips=clips, tag=tag)
pip(64.0, 73.0, [{"src": "pip-a"}], "HELLO")
pip(79.0, 84.3, [{"src": "pip-b1"}])
pip(86.0, 90.4, [{"src": "pip-b2"}], sound="pop")
pip(207.0, 215.3, [{"src": "pip-c1"}, {"src": "pip-c2"}, {"src": "pip-c3"}])
pip(220.0, 227.7, [{"src": "pip-d1"}, {"src": "pip-d2"}, {"src": "pip-d3"}])
def stick(s, e, emoji=None, who=None, dx=0, dy=0, x=None, y=None, size=120, rot=0, text=None, sound="pop", gain=-19, kind=None):
    add("stick", o(s), o(e), sound, gain, emoji=emoji, who=who, dx=dx, dy=dy, x=x, y=y, size=size, rot=rot, text=text, kind=kind)
stick(99.0, 101.5, who="joy", kind="lines", dy=-.1, size=340, sound="boing")        # surprise lines on Joy
stick(109.0, 111.0, "🌱", who="mark", dy=-.22, dx=.1, size=86)
stick(127.0, 131.5, "👑", who="joy", dy=-.42, dx=.02, size=190, rot=8, sound="sparkle", gain=-17)
stick(127.0, 131.5, "💂", who="mark", dx=-1.25, dy=.55, size=170, sound="pop")
stick(157.0, 159.4, "🐥", x=40, y=510, size=330, text="HELLO!", sound="boing", gain=-16)
stick(159.5, 163.6, who=None, kind="palm", x=760, y=510, size=300, sound="sparkle")
stick(169.0, 171.8, "⬆️", x=800, y=320, size=120, text="LEVEL UP", sound="chime", gain=-15)
stick(189.3, 191.0, kind="giant", x=-280, y=70, size=1000, sound="impact", gain=-14)
shakes.append(o(189.3))
stick(192.0, 194.6, "🐹", x=1100, y=720, size=210, sound="pop")
stick(239.5, 244.4, kind="row", emoji="🌻", x=500, y=470, size=96, sound="pop")
add("burst", o(244.4), o(244.4) + 2.2, "impact", -16, x=760, y=480, emoji=["🌻"], n=46, big=True)
stick(274.2, 276.6, "😎", who="joy", dx=1.15, dy=.15, size=150)
stick(324.2, 326.6, "💡", who="mark", dx=.85, dy=-.1, size=170, sound="chime", gain=-16)

# ------------------------------------------------------------ the offer (music up, big finish)
scenes = [{"t": -1, "bg": "art-both"}]   # the owner's watercolour backgrounds
for e in [x for x in ev if x["type"] == "scene"]:
    scenes.append({"t": e["s"], "bg": ["art-lawn", "art-river", "art-both", "art-lawn", "art-river", "art-both", "art-lawn"][len(scenes) - 1]})
ev = [x for x in ev if x["type"] not in ("scene", "mini")]

beats = json.load(open(f"{HERE}/music/beats.json"))["from_end"]
LENS = [8.5, 9.0, 7.5, 7.5, 10.0, 5.0]        # free, journey, inside, reviews, price, logo
END = round(MAIN_END + sum(LENS), 3)
def on_beat(t):
    b = min(beats, key=lambda x: abs(END - x - t))
    return round(END - b, 3)
wip = lambda at, col="#F6F0BA", **k: add("wipe", at - .45, at + .45, "whoosh", -16, text=None, color=col, **k)
marks = [MAIN_END]
for L in LENS[:-1]:
    marks.append(on_beat(marks[-1] + L))
t = marks[0]; wip(t, "#FFFFFF", cloud=True)
nx = marks[1]
add("free", t, nx, "impact", -15, items=[
    {"title": "워크시트", "sheet": "sheets/day1.jpg"},
    {"title": "웹사이트 놀이 게임", "emoji": "🎮"},
    {"title": "Mark와 Joy의 지원", "photo": "brand/mark-joy-photo.jpg"}])
shakes.append(round(t, 3))
for i in range(3): cue(t + 1.1 + i * .55, "pop", -18)
cue(t + 2.8, "chime", -19)
t = nx; nx = marks[2]; wip(t, "#AECCE6")
add("journey", t, nx, walk=6.5)
for i in range(7): cue(t + .5 + (i / 6) * 6.0, "pop", -21)
cue(t + 6.6, "sparkle", -17)
t = nx; nx = marks[3]; wip(t, "#F6F0BA")
add("inside", t, nx, rows=[
    {"avatar": "brand/mark-avatar.png", "text": "Mark의 발음 영상 7편"},
    {"avatar": "brand/joy-avatar.png", "text": "Joy의 워크시트 놀이 안내 영상 7편"},
    {"emoji": "🖨️", "text": "매일 인쇄해서 즐기는 워크시트"},
    {"emoji": "🏅", "text": "내 이름을 담은 Bear & Joy 완주 기념장"},
    {"emoji": "📖", "text": "새 이야기책을 먼저 만나볼 기회"}])
for i in range(5): cue(t + .7 + i * .75, "whoosh", -22); cue(t + 1.1 + i * .75, "chime", -24)
t = nx; nx = marks[4]; wip(t, "#AECCE6")
add("reviews", t, nx)
for i in range(4): cue(t + .5 + i * .7, "pop", -21)
t = nx; nx = marks[5]; wip(t, "#F6F0BA")
add("price", t, nx, facts=[
    {"emoji": "💳", "big": "한 번만 결제", "small": "정기결제가 아니에요"},
    {"emoji": "⏰", "big": "24시간마다", "small": "다음 놀이가 열려요"},
    {"emoji": "📅", "big": "30일 동안", "small": "다시 즐겨요"}])
cue(t + 1.5, "impact", -15); shakes.append(round(t + 1.5, 3))
for i in range(3): cue(t + 1.6 + i * .5, "pop", -19)
cue(t + 3.6, "whoosh", -18); cue(t + 5.6, "chime", -17)
t = nx
add("logoend", t, END, "sparkle", -18)
wip(t, "#F8EEDF")
DURATION = END

# ------------------------------------------------------------ camera
MARK = [(6.7, 10.7), (16, 21.9), (41.8, 44.8), (55, 65), (97, 104.3), (148, 154.4), (155.7, 162.3), (179.1, 183.8), (196.8, 207.6), (229.7, 237), (276.6, 285.4), (300.4, 306.4), (322.4, 324.7)]
zooms, big = [{"t": 0, "z": 1.0, "ox": 960, "oy": 420}], 0
for cp in captions:
    tc = cp["cap"]
    mark = any(a <= tc < b for a, b in MARK)
    big = 1 - big
    zooms.append({"t": cp["s"], "z": 1.09 if big else 1.0, "ox": 527 if mark else 1088, "oy": 450})
for s in shakes:
    zooms.append({"t": s, "z": 1.14, "ox": 800, "oy": 430})
zooms.sort(key=lambda z: z["t"])

plan = {"name": "day0-main", "fps": FPS, "duration": DURATION, "frames": round(DURATION * FPS), "mainStart": INTRO, "mainEnd": MAIN_END,
        "segments": segments, "faces": json.load(open(f"{HERE}/versions/main/faces.json")), "captions": captions, "scenes": scenes, "events": ev, "zooms": zooms, "shakes": sorted(shakes), "sfx": sorted(sfx, key=lambda x: x["t"])}
os.makedirs(f"{HERE}/versions/main", exist_ok=True)
json.dump(plan, open(f"{HERE}/versions/main/timeline.json", "w"), ensure_ascii=False, indent=1)

print(f"duration {DURATION:.1f}s  main ends {MAIN_END:.1f}  captions {len(captions)}  events {len(ev)}  sfx {len(sfx)}  segments {len(segments)}")
gaps = sorted(x["s"] for x in ev if x["s"] < MAIN_END)
print("longest gaps between cues:", sorted(((round(b - a, 1), round(a, 1)) for a, b in zip(gaps, gaps[1:])), reverse=True)[:6])
fast = [(round(len(re.sub(r"\s", "", x["ko"])) / (x["e"] - x["s"]), 1), round(x["e"] - x["s"], 2), x["ko"]) for x in captions]
print("captions over 6 chars/s:", sum(1 for f in fast if f[0] > 6), "of", len(fast))
for f in sorted(fast, reverse=True)[:8]: print(" ", f)
