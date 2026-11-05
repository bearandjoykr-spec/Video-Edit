"""Day 1 "Hello, Little Bear!" class video plan (YouTube / Little Steps page).

Run: .venv/bin/python projects/2026-11-day1-class/build_timeline.py
Writes versions/main/timeline.json (picture + SFX cues) and prints the caption reading-speed table.
All times below are SOURCE seconds unless named otherwise; m() converts to output time.
Rules: docs/class-video-style.md, brand/BRAND.md. No music on this video (owner, 5 Nov 2026).
Mark's Korean is Joy's translation, word for word. Joy's captions follow what she says on camera.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
MAIN_END = 346.0               # just before the footage's own fade to the logo
OFF = 0.0                      # the cold open was dropped (owner, 5 Nov 2026): plan and countdown instead
ENDING = [("recap", 7.5), ("reviews", 8.5), ("offer", 9.0), ("logo", 4.0)]
m = lambda s: round(s + OFF, 3)

P1 = {"en": ["Look!", "It's", "a", "bear!"], "pron": "룩! 잇츠 어 베어!", "ko": "봐! 곰이야!"}
P2 = {"en": ["Where's", "the", "bear?"], "pron": "웨어즈 더 베어?", "ko": "곰이 어디 있지?"}
P3 = {"en": ["There", "he", "is!"], "pron": "데어 히 이즈!", "ko": "여기 있었네!"}

ev, sfx = [], []
def cue(t, sound, gain=-20): sfx.append({"t": round(t, 3), "sound": sound, "gain": gain})

def card(s, e, phrase, tag, reads=(), chips=(), alts=(), emph=(), arrow=None, compact=False, shrink=None, clock=m):
    """Phrase card. reads = windows when each word lights up in turn."""
    ev.append({"type": "card", "s": clock(s), "e": clock(e), **phrase, "tag": tag, "compact": compact,
               "reads": [[clock(a), clock(b)] for a, b in reads],
               "chips": [{**x, "s": clock(x["s"]), "e": clock(x["e"])} for x in chips],
               "alts": [{**x, "s": clock(x["s"]), "e": clock(x["e"])} for x in alts],
               "emph": [{**x, "s": clock(x["s"]), "e": clock(x["e"])} for x in emph],
               "arrow": {**arrow, "s": clock(arrow["s"]), "e": clock(arrow["e"])} if arrow else None,
               "shrink": [clock(shrink[0]), clock(shrink[1])] if shrink else None})
    cue(clock(s), "whoosh", -22)

def listen(s, e): return {"s": s, "e": e, "kind": "listen", "text": "👂 천천히 들어보세요"}
def turn(s, e):
    cue(m(s), "chime", -20)
    return {"s": s, "e": e, "kind": "turn", "text": "🎤 이제 따라 해보세요"}

def label(s, e, text, x=None, y=None, tone="sky", right=None, clock=m, sound="pop"):
    ev.append({"type": "label", "s": clock(s), "e": clock(e), "text": text, "x": x, "y": y, "right": right, "tone": tone})
    if sound: cue(clock(s), sound, -24)

def hero(s, e, small, big, x, y, tone="butter", size=150, clock=m, sound="pop", align="left"):
    ev.append({"type": "hero", "s": clock(s), "e": clock(e), "small": small, "big": big, "x": x, "y": y, "tone": tone, "size": size, "align": align})
    if sound: cue(clock(s), sound, -20)

def behind(clip, clip_s, clip_e, s, e, small, big, x=1020, y=70, size=250, tone="butter"):
    ev.append({"type": "behind", "clip": clip, "clip_s": m(clip_s), "clip_e": m(clip_e), "s": m(s), "e": m(e),
               "small": small, "big": big, "x": x, "y": y, "size": size, "tone": tone})
    cue(m(s), "sparkle", -22)

def sparkle(t, x, y, n=14, clock=m, gain=-24):
    ev.append({"type": "sparkles", "s": clock(t), "e": clock(t) + 1.3, "x": x, "y": y, "n": n})
    cue(clock(t), "sparkle", gain)

# ------------------------------------------------------------------ captions
# (source start, source end, text, yellow word). Empty hi = no highlight.
MARK = [
 (5.0, 8.7, "Little Steps 첫날에 오신 걸 환영해요!", "첫날"),  # Joy's line; Mark says "Little Steps" on camera
 (8.7, 12.7, "오늘은 세 가지 짧은 영어 표현을 연습해 볼 거예요.", "세 가지"),
 (12.7, 17.84, "그다음 조이가 아이와 놀이하면서 이 표현들을 어떻게 활용하는지 보여드릴게요.", "놀이"),
 (17.84, 21.94, "처음부터 모든 걸 기억하려고 하지 않으셔도 돼요.", "모든 걸"),
 (21.94, 25.4, "언제든 다시 돌아와 저와 함께 연습하시면 됩니다.", "언제든"),
 (25.5, 28.6, "준비되셨나요? 그럼 시작해 볼까요?", "시작"),
 (32.6, 34.6, "첫 번째 표현은 바로 이거예요.", "첫 번째"),
 (39.6, 41.7, "한 번 더 들어보세요.", "한 번 더"),
 (45.5, 47.4, "이번엔 직접 따라 해보세요.", "직접"),
 (48.3, 52.2, "‘it’s a’는 끊지 않고 자연스럽게 이어서 말해 보세요.", "이어서"),
 (54.6, 57.9, "그리고 ‘Look!’은 반가운 무언가를 발견한 것처럼", "발견"),
 (57.9, 61.0, "조금 신나는 목소리로 말해 보세요.", "신나는"),
 (72.0, 73.7, "다음 표현은 이거예요.", "다음"),
 (77.0, 81.1, "‘Where’s’는 ‘Where is’를 줄인 표현이에요.", "줄인"),
 (81.2, 84.0, "하나의 단어처럼 자연스럽게 말해 보세요.", "하나의 단어"),
 (86.9, 88.7, "이번엔 여러분 차례예요.", "여러분"),
 (90.5, 91.75, "좋아요!", ""),
 (91.78, 95.5, "궁금해하는 느낌을 목소리에 담아보세요.", "궁금해하는"),
 (95.6, 98.2, "아이와 함께 곰을 찾고 있는 거예요.", "함께"),
 (103.8, 105.05, "아주 잘했어요!", ""),
 (107.9, 110.7, "그리고 곰을 찾았을 땐 이렇게 말해요.", "찾았을 땐"),
 (112.2, 114.2, "다시 한번 들어보세요.", "다시"),
 (116.45, 118.2, "이번엔 직접 따라 해보세요.", "직접"),
 (120.5, 121.75, "아주 잘했어요!", ""),
 (121.8, 124.2, "웃는 듯한 밝은 목소리로 말해 보세요.", "밝은"),
 (124.3, 126.9, "드디어 곰을 찾았으니까요!", "찾았으니까요"),
 (131.8, 133.03, "좋아요!", ""),
 (133.05, 136.5, "이제 세 가지 표현을 함께 연습해 볼게요.", "세 가지"),
 (150.7, 155.9, "좋아요! 이제 배운 표현들을 실제 놀이에서 사용해 볼 차례예요.", "놀이"),
 (156.2, 158.4, "그럼 이제 조이에게 넘겨볼게요!", "조이"),
]
JOY = [
 (160.0, 163.1, "마크와 오늘의 세 문장 연습 잘 해보셨나요?", "세 문장"),
 (163.3, 167.0, "이제 이 문장들을 아이와 놀면서 한번 사용해 볼게요.", "놀면서"),
 (167.4, 170.8, "오늘은 아주 작은 창문 뒤에 곰을 숨겼다가", "창문"),
 (170.8, 173.6, "까꿍 하고 보여주는 놀이예요.", "까꿍"),
 (173.8, 178.0, "이 워크시트는 놀이 전에 우리 부모님께서 미리 잘라주세요.", "미리"),
 (178.2, 183.0, "창문의 양옆에 접는 부분과 곰 아래의 넓은 손잡이는 남겨주세요.", "남겨주세요"),
 (183.3, 188.4, "놀이할 때도 부모님이 손잡이를 잡고 곰과 창문을 움직여주시면 돼요.", "손잡이"),
 (188.6, 191.3, "자, 그럼 먼저 아이에게 곰을 보여주세요.", "곰"),
 (196.4, 201.8, "이번에는 곰 그림을 창문 종이 뒤로 쏙 숨기고 창문을 닫아볼게요.", "쏙"),
 (206.7, 209.5, "그리고 창문을 열면…", "열면"),
 (219.0, 222.5, "이렇게만 해도 짧은 놀이 하나가 완성돼요.", "완성"),
 (222.9, 225.3, "아이가 좋아한다면 한 번 더 해보세요.", "한 번 더"),
 (225.5, 227.8, "이번에는 작은 목소리로", "작은 목소리"),
 (236.2, 241.3, "같은 문장도 목소리와 표정이 달라지면 새로운 재미가 생겨요.", "새로운 재미"),
 (241.4, 246.1, "우리 아이가 웃었던 부분이 있다면 그 부분을 다시 해주세요.", "웃었던"),
 (246.2, 250.7, "아직 아기라면 부모님이 질문도 하고 대답도 하며 보여주세요.", "아기"),
 (250.7, 254.9, "아이가 꼭 따라 말하거나 곰을 찾아야 하는 건 아니에요.", "꼭"),
 (255.0, 259.7, "영어가 이미 익숙한 아이라면 아이가 원할 때 질문하는 역할을 맡겨보세요.", "질문하는 역할"),
 (259.7, 264.5, "아이가 “Where’s the bear?”라고 물으면 창문을 열어주세요.", "창문"),
 (264.6, 267.5, "아이가 한국어로 “여기!”라고 말해도 좋아요.", "“여기!”"),
 (267.6, 272.5, "받아주면서 “Yes! Right! There he is!”라고 말해주세요.", "받아주면서"),
 (272.6, 277.9, "꼭 영어로 다시 한번 말해봐, 영어로 뭐라고 했지? 라고 확인하지 않으셔도 돼요.", "확인"),
 (278.1, 281.3, "저희 베어앤조이가 중요하게 생각하는 건", "중요하게"),
 (281.3, 284.9, "영어를 가르치려고 하기보다는 함께 사용하는 거예요.", "함께"),
 (285.1, 291.1, "우리말로 까꿍 놀이를 할 때 아이에게 정답을 말하게 하려고 놀지는 않잖아요.", "정답"),
 (291.2, 294.9, "서로의 반응을 보고 웃으며 함께 하려는 거죠.", "웃으며"),
 (295.0, 297.5, "영어도 그렇게 사용해 볼 수 있어요.", "영어도"),
 (297.6, 304.0, "부모님이 편하게 시도해보고 실수해도 웃으며 다시 해보는 모습을 보여주세요.", "실수해도"),
 (304.2, 309.9, "아이에게도 “나도 한번 해봐도 괜찮겠구나”라는 마음이 생길 수 있도록요.", "괜찮겠구나"),
 (310.1, 315.9, "그렇게 부모님과 아이 모두 영어를 사용하는 데 조금씩 자신감을 쌓아가는 거예요.", "자신감"),
 (316.1, 319.2, "이제 화면을 내려놓고 아이와 직접 놀아보세요.", "내려놓고"),
 (319.3, 321.2, "길게 하지 않아도 괜찮아요.", "괜찮아요"),
 (321.3, 323.9, "아이가 즐거워하는 만큼 함께 해주세요.", "즐거워하는"),
 (323.95, 330.3, "그리고 오늘 나중에 곰 그림이나 인형을 다시 만났을 때 한 번 더 말해보세요.", "다시"),
 (332.9, 337.5, "워크시트에서 사용한 영어가 우리 생활 속에도 쓰이는 순간이에요.", "생활 속"),
 (337.6, 339.6, "오늘의 첫 번째 작은 모험.", "작은 모험"),
 (339.65, 341.9, "그럼 즐겁게 시작해볼까요?", "즐겁게"),
 (342.1, 346.0, "즐겁게 놀아요! 2일차에 만나요! 안녕!", "2일차"),
]
captions = [{"s": m(a), "e": m(b), "ko": t, "hi": h, **({"left": 600} if a == 12.7 else {})} for a, b, t, h in MARK + JOY]  # 12.7: clear of the preview window burned into the footage

# ------------------------------------------------------------------ title over Mark's greeting
ev.append({"type": "title", "s": 0.0, "e": m(4.9), "day": 1, "en": "Hello, Little Bear!", "ko": "안녕, 곰아!"})
cue(m(0.5), "sparkle", -22); cue(m(4.4), "whoosh", -22)
ev.append({"type": "badge", "s": m(5.0), "e": m(MAIN_END), "l1": "Day 1", "l2": "Hello, Little Bear!"})
# Today's plan: viewers know what's coming and how long each part takes.
ev.append({"type": "plan", "s": m(8.9), "e": m(25.2), "steps": [
    {"from": m(9.2), "title": "세 가지 표현", "who": "마크와 연습해요", "time": "약 2분"},
    {"from": m(13.3), "title": "까꿍 놀이", "who": "조이가 보여줘요", "time": "약 1분 30초"},
    {"from": m(15.0), "title": "우리 아이에 맞게", "who": "놀이 팁과 이유", "time": "약 2분"}]})
cue(m(8.9), "whoosh", -24)
for t_ in (9.2, 13.3, 15.0): cue(m(t_), "pop", -24)
behind("ready", 25.0, 28.8, 25.5, 27.25, "준비되셨나요?", "READY?", x=1110, y=150, size=180)

# Countdown into the first phrase, over "Let's begin".
ev.append({"type": "count", "s": m(27.2), "e": m(30.0), "text": "첫 번째 표현까지"})
for t_ in (27.2, 28.13, 29.07): cue(m(t_), "pop", -20)
cue(m(29.95), "chime", -20)

# ------------------------------------------------------------------ phrase 1
card(30.0, 65.4, P1, "오늘의 표현 1 · Phrase 1",
     reads=[(30.06, 32.4), (35.4, 37.6), (42.46, 45.02), (61.6, 64.18)],
     chips=[listen(30.0, 45.6), turn(46.82, 48.46)],
     alts=[{"s": 48.46, "e": 54.6, "en": ["It's", "a", "bear."], "pron": "잇츠 어 베어", "ko": "곰이야.", "flow": [0, 1], "reads": [[m(52.34), m(54.18)]]}],
     emph=[{"s": 54.77, "e": 64.2, "words": [0]}])
sparkle(30.3, 1400, 400); sparkle(61.3, 1400, 430, n=18, gain=-20)

# ------------------------------------------------------------------ phrase 2
card(70.3, 102.5, P2, "오늘의 표현 2 · Phrase 2",
     reads=[(70.54, 71.54), (73.9, 75.9), (85.58, 86.86), (98.96, 100.66)],
     chips=[listen(70.3, 87.3), turn(88.46, 90.5)],
     alts=[{"s": 77.0, "e": 83.8, "en": ["Where", "is", "→", "Where's"], "pron": "웨어 이즈 → 웨어즈", "ko": "한 단어처럼!", "flow": [0, 1], "reads": []}],
     arrow={"s": 91.78, "e": 101.0, "dir": "up", "text": "궁금한 목소리로, 끝을 살짝 올려요"})
hero(99.0, 101.5, "", "?", 1420, 240, size=280, tone="sky")

# ------------------------------------------------------------------ phrase 3
card(106.4, 131.0, P3, "오늘의 표현 3 · Phrase 3",
     reads=[(106.66, 108.44), (110.7, 112.2), (114.86, 116.42), (128.06, 129.84)],
     chips=[listen(106.4, 116.7), turn(118.14, 120.56)],
     emph=[{"s": 121.88, "e": 130.5, "words": [0, 1, 2]}])
behind("discovery", 124.0, 127.2, 124.34, 127.0, "드디어", "찾았다!", x=1120, y=140, size=180)
sparkle(128.1, 1400, 430, n=20, gain=-20)

# ------------------------------------------------------------------ all three
ev.append({"type": "stack", "s": m(136.6), "e": m(149.9), "rows": [
    {**P1, "from": m(137.0), "lit": [m(137.52), m(140.42)]},
    {**P2, "from": m(141.8), "lit": [m(142.64), m(144.14)]},
    {**P3, "from": m(145.0), "lit": [m(145.52), m(149.14)]}]})
cue(m(136.6), "whoosh", -22)
for t in (137.0, 141.8, 145.0): cue(m(t), "pop", -22)

# ------------------------------------------------------------------ handover
ev.append({"type": "wipe", "s": m(158.75), "e": m(159.75), "text": "조이와 놀아요!"})
cue(m(158.8), "whoosh", -18)

# ------------------------------------------------------------------ Joy: the game
label(161.0, 166.8, "🏠 오늘의 놀이 · 까꿍 창문", right=70, y=210)
label(174.2, 178.0, "✂️ 놀이 전에 미리 잘라요", right=70, y=210)
label(178.6, 183.0, "📄 접는 부분 · 손잡이는 남겨요", right=70, y=210, tone="butter")
label(183.6, 188.4, "✋ 부모님이 손잡이를 잡아요", right=70, y=210)
card(191.8, 195.9, P1, "까꿍 놀이 · 1단계", reads=[(192.0, 193.58)], compact=True)
sparkle(192.1, 620, 420, n=12)
card(203.4, 206.6, P2, "까꿍 놀이 · 2단계", reads=[(203.64, 204.5)], compact=True)
hero(203.8, 206.4, "", "?", 1500, 330, size=220, tone="sky")
card(210.7, 217.6, P3, "까꿍 놀이 · 3단계", reads=[(210.96, 212.4), (215.08, 216.16)], compact=True)
hero(210.95, 214.0, "", "까꿍!", 1400, 170, size=150)
sparkle(210.95, 760, 480, n=22, gain=-18)
# one small, polite note about the rest of the course (facts from the Little Steps page)
ev.append({"type": "nudge", "s": m(219.4), "e": m(224.4), "text": "🦋 7일 동안 매일 새로운 놀이가 이어져요"})
cue(m(219.4), "pop", -26)
card(227.9, 231.2, P2, "작은 목소리로 🤫", reads=[(228.2, 230.5)], compact=True, shrink=(228.0, 228.8))
card(232.1, 235.6, P3, "반가운 목소리로 😊", reads=[(232.5, 234.1)], compact=True)
sparkle(232.5, 760, 480, n=14)

# ------------------------------------------------------------------ Joy: fit your child
def level(s, e, emoji, title, body, tone):
    ev.append({"type": "level", "s": m(s), "e": m(e), "emoji": emoji, "title": title, "body": body, "tone": tone})
    cue(m(s), "pop", -22)
level(246.3, 254.9, "👶", "아직 아기라면", "부모님이 묻고, 답해요", "butter")
level(255.1, 264.5, "🧒", "영어가 익숙하다면", "아이가 묻는 역할을 해요", "sky")
level(264.7, 272.5, "🇰🇷", "“여기!”라고 말해도", "좋아요! 받아주세요", "butter")
label(272.8, 277.9, "🙅 “다시 말해 봐” 안 해도 돼요", right=70, y=210)

# ------------------------------------------------------------------ Joy: why we play
behind("together", 278.0, 285.0, 281.0, 284.9, "가르치기보다", "함께", x=1075, y=120, size=300)
hero(297.9, 303.9, "", "실수해도 괜찮아요 😊", 1240, 220, size=58, tone="butter")
hero(310.4, 315.9, "조금씩", "자신감 쌓기", 1300, 200, size=80, tone="sky")

# ------------------------------------------------------------------ Joy: back to life
label(316.3, 319.2, "📱 화면은 잠시 내려놓고", right=70, y=210)
card(330.3, 332.8, P1, "일상에서 한 번 더", reads=[(330.6, 332.32)], compact=True)
sparkle(330.6, 1400, 430, n=12)
behind("adventure", 337.4, 341.4, 337.6, 341.0, "오늘의 첫 번째", "작은 모험", x=1150, y=170, size=150, tone="sky")

# ------------------------------------------------------------------ ending (new cards, no voice)
t = m(MAIN_END)
ev.append({"type": "wipe", "s": t - 0.3, "e": t + 0.1})
cue(t - 0.3, "whoosh", -18)
rows = [P1, P2, P3]
for name, d in ENDING:
    e = {"type": name, "s": round(t, 3), "e": round(t + d, 3)}
    if name == "recap":
        e["rows"] = rows; cue(t + 0.1, "sparkle", -20)
        for k in range(3): cue(t + 0.5 + k * 0.5, "pop", -20)
    if name == "reviews":
        cue(t, "whoosh", -22)
        for k in range(4): cue(t + 0.5 + k * 0.7, "pop", -22)
    if name == "offer":
        cue(t, "whoosh", -22); cue(t + 3.4, "sparkle", -18)
    if name == "logo":
        cue(t + 0.2, "chime", -18)
    ev.append(e); t += d

dur = round(t, 3)
ev.append({"type": "progress", "s": 5.0, "e": m(MAIN_END), "marks": [m(30.0), m(160.0), m(246.2)]})

# Zoom: gentle levels only. The source is 1080p, so stay at or under 106%.
zooms = []
for s, z, ox, oy in [(0, 1.0, 960, 500)]:
    zooms.append({"t": 0, "z": z, "ox": ox, "oy": oy})
for s, z in [(8.7, 1.03), (25.4, 1.06), (30.0, 1.0), (54.7, 1.05), (66.0, 1.0), (91.8, 1.05), (106.4, 1.0), (121.8, 1.05), (136.5, 1.0),
             (150.7, 1.04), (160.0, 1.0), (219.0, 1.04), (236.2, 1.0), (246.2, 1.04), (278.1, 1.0), (285.1, 1.05), (316.1, 1.0), (333.0, 1.04)]:
    zooms.append({"t": m(s), "z": z, "ox": 960, "oy": 320})

segments = [{"src_s": 0.0, "src_e": MAIN_END, "out_s": 0.0}]
sfx.sort(key=lambda x: x["t"])
plan = {"name": "day1-main", "fps": FPS, "duration": dur, "frames": round(dur * FPS), "offset": OFF, "segments": segments,
        "captions": captions, "events": ev, "zooms": zooms, "sfx": sfx, "mainEnd": MAIN_END,
        # Music only for the goodbye and the ending (owner, 5 Nov 2026): low under Joy, full under recap, reviews and offer.
        "music": {"start": m(342.0), "full": m(MAIN_END), "end": dur}}
out = f"{HERE}/versions/main"; os.makedirs(out, exist_ok=True)
json.dump(plan, open(f"{out}/timeline.json", "w"), ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ reading-speed table
bad = 0
for a, b, text, _ in MARK + JOY:
    n = len(re.sub(r"[^가-힣A-Za-z0-9]", "", text)); d = b - a; cps = n / d
    flag = "" if cps <= 6.5 and d >= 1.2 else "  <-- CHECK"
    bad += bool(flag)
    if cps > 6.05: over6 = globals().get("over6", 0) + 1
    if flag: print(f"{a:7.2f} {d:4.1f}s {cps:4.1f}/s {text}{flag}")
print(f"captions {len(captions)}, over the rule {bad}, between 6 and 6.5: {globals().get('over6', 0)}, duration {dur:.1f}s ({int(dur // 60)}:{int(dur % 60):02d}), frames {plan['frames']}, sfx {len(sfx)}")
