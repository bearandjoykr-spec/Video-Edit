"""First Steps Day 5 "Story Detectives" — edit plan (times in seconds on the source; footage is used uncut).

Usage: python3 make_spec.py > spec.json   then   python3 build_class.py spec.json versions/main
Mark's Korean captions: Claude's translations (no owner script) — a fluent speaker should check them.
Joy's captions: her own words from the Whisper transcript, with obvious mishearings fixed; lines marked
# condensed were shortened to meet the reading-speed rule (<= ~6 Korean chars/s, >= 1.2 s).
"""
import json

M, J = "mark", "joy"
caps = []
def c(s, e, ko, hi="", en="", who=M):
    caps.append({"s": s, "e": e, "ko": ko, "hi": hi, **({"en": en} if en else {}), "speaker": who})

# ---- Mark (English; Korean captions underneath) ----
c(0.1, 6.0, "안녕하세요, 5일차에 오신 걸 환영해요!", "5일차", "Hello, and welcome to Day 5.")
c(6.2, 10.9, "오늘은 우리가 이야기 탐정이 돼 볼 거예요.", "이야기 탐정", "Today we're becoming story detectives.")
c(11.1, 15.6, "자세히 들여다보고, 작은 것들을 발견하고,", "자세히", "We're going to look closely, notice little things,")
c(15.8, 19.0, "함께 찾아내는 즐거움을 누려 봐요.", "즐거움", "and enjoy discovering them together.")
c(19.2, 21.7, "그거 아세요?", "", "You see?")
c(21.8, 25.9, "아이가 여러분도 못 본 걸 먼저 찾을지도 몰라요.", "먼저", "Your child might spot something you haven't even noticed,")
c(26.0, 28.8, "아이가 여러분을 놀라게 해 주도록 두세요.", "놀라게", "so let them surprise you.")
c(28.9, 34.0, "먼저 세 가지 표현을 연습해 볼게요.", "세 가지", "So first, let's practise our three phrases.")
c(35.1, 38.1, "첫 번째 표현은,", "첫 번째", "So our first phrase is,")
c(40.8, 42.6, "천천히 들어보세요.", "천천히", "Listen slowly.")
c(46.0, 48.2, "이번엔 따라 해보세요.", "따라", "Now you try.")
c(51.8, 53.4, "좋아요!", "좋아요", "Good.")
c(53.5, 56.5, "'can'은 짧고 부드럽게,", "짧고", "Keep 'can' soft and quick,")
c(56.6, 59.4, "'see'는 또렷하게 들리게 해요.", "또렷하게", "and let 'see' stand out.")
c(59.5, 62.2, "조금씩 늘려 가며 말해요.", "조금씩", "I can… I can see…")
c(68.7, 73.7, "좋아요! 내가 발견한 걸 나누는 말이에요.", "나누는", "Good. So you're sharing something you've noticed.")
c(75.4, 78.0, "다음 표현은,", "다음", "Okay. Our next phrase is,")
c(83.4, 85.8, "다시 들어보세요.", "다시", "Listen again.")
c(88.6, 91.3, "자, 여러분 차례예요.", "차례", "Okay, your turn.")
c(94.2, 98.4, "'can you'는 부드럽게 이어서 말해요.", "이어서", "Let 'can you' flow together softly.")
c(100.5, 103.2, "궁금한 마음으로 묻고,", "궁금한", "Ask with curiosity,")
c(103.3, 107.1, "잠깐 기다려 주세요.", "기다려", "then leave a little space.")
c(107.2, 110.6, "아이가 말로 대답하지 않을 수도 있어요.", "말로", "Your child might not answer with words.")
c(110.7, 114.9, "몸짓이나 손가락으로 가리켜도 충분해요.", "충분해요", "A gesture or pointing a finger is just as good.")
c(116.4, 118.8, "마지막 표현은,", "마지막", "Our last phrase,")
c(122.4, 124.3, "천천히 들어보세요.", "천천히", "Listen slowly.")
c(128.0, 130.0, "이번엔 따라 해보세요.", "따라", "Now you try.")
c(132.7, 136.8, "'together'는 가운데를 힘주어 말해요.", "가운데", "In 'together', stress the middle part.")
c(136.9, 139.3, "투-게-더", "게", "geth… together.")
c(142.3, 144.7, "목소리는 부드럽게,", "부드럽게", "Keep your voice gentle.")
c(144.8, 147.0, "함께하자는 초대니까요.", "초대", "It's an invitation.")
c(147.1, 149.9, "자, 세 가지를 모두 말해 볼까요?", "세 가지", "Okay, let's say all three.")
c(158.5, 160.2, "아주 좋아요!", "좋아요", "Lovely.")
c(160.3, 166.4, "조이, 우리 정원을 탐험해 볼까요?", "정원", "Joy, shall we explore the garden?")

# ---- Joy (Korean, her words) ----
c(168.7, 170.4, "짜잔!", "짜잔", who=J)
c(170.5, 174.6, "오늘은 정원으로 작은 탐험을 떠나볼 거예요.", "탐험", who=J)
c(174.7, 179.1, "가만히 보면 여기저기 작은 친구들과 물건들이 숨어 있어요.", "숨어", who=J)
c(179.2, 181.5, "이것은 그림 힌트 페이지예요.", "힌트", who=J)
c(181.6, 185.2, "이쪽에서는 정원에서 찾아볼 수 있는 그림들이 있어요.", "그림들", who=J)
c(185.3, 187.4, "처음에는 곰부터 찾아도 좋고", "곰부터", who=J)
c(187.5, 191.2, "아이가 관심 보이는 그림 하나로 시작해도 좋아요.", "관심", who=J)  # condensed
c(191.3, 196.5, "그림이 많이 보인다면 종이로 가리고 하나만 보여주셔도 좋아요.", "하나만", who=J)
c(196.6, 199.9, "그리고 아이와 나란히 앉아 말해주세요.", "나란히", who=J)
c(200.0, 202.9, "라고 말이죠.", "", "Let's look together!", J)
c(203.0, 207.1, "그리고 부모님과 함께 그림을 천천히 살펴보다가", "천천히", who=J)
c(207.2, 210.3, "곰을 발견하면 가리키고 얘기하면 돼요.", "가리키고", who=J)
c(210.4, 212.4, "곰이 보여요!", "곰", "I can see a bear!", J)
c(212.5, 214.4, "그리고 한 번 더 물어볼까요?", "한 번 더", who=J)
c(214.5, 216.8, "뭐가 보이니?", "", "What can you see?", J)
c(216.9, 219.4, "대답이 늦어도 조금 기다려주세요.", "기다려", who=J)  # condensed
c(219.5, 223.6, "아이가 가리키거나 한국어로 말해도 좋아요.", "한국어", who=J)
c(223.7, 225.9, "너는 그걸 봤구나!", "봤구나", who=J)
c(226.0, 229.4, "아이의 발견을 함께 반가워해 주시면 돼요.", "반가워해", who=J)
c(229.5, 233.2, "곰을 찾다가 아이가 나비에 관심을 보이면", "나비", who=J)  # condensed
c(233.3, 236.1, "그 나비를 함께 봐주세요.", "함께", who=J)
c(236.2, 239.1, "오늘 놀이의 주인공은 아이의 호기심이에요.", "호기심", who=J)
c(239.2, 243.6, "12가지를 모두 찾거나 순서대로 진행할 필요는 없어요.", "필요는 없어요", who=J)
c(243.7, 247.0, "하나를 찾고 이야기 나누면 충분해요.", "충분해요", who=J)  # condensed
c(247.1, 254.0, "아직 어린 아기라면 부모님이 관심 있는 것을 가리키며 짧게 이야기해주세요.", "짧게", who=J)
c(254.1, 260.6, "이야기를 좋아하는 아이라면 발견한 곰이 무엇을 하고 있을지 상상해도 좋아요.", "상상", who=J)
c(260.7, 263.8, "한국어로 이야기가 길어져도 함께 즐겨주세요.", "즐겨주세요", who=J)
c(263.9, 268.1, "영어 이름을 몰라도 멈추고 찾아볼 필요는 없어요.", "멈추고", who=J)  # condensed
c(268.2, 269.6, "뭐가 보이니?", "", "What can you see?", J)
c(269.7, 276.5, "같은 질문도 어떤 마음으로 묻느냐에 따라 달라질 수 있어요.", "마음", who=J)
c(276.6, 279.1, "정답을 아는지 확인하기보다", "정답", who=J)  # condensed
c(279.2, 284.3, "아이의 눈에 무엇이 들어왔는지 궁금해하며 물어봐주세요.", "궁금해하며", who=J)
c(284.4, 290.2, "부모님은 곰을 보고 있는데 아이는 작은 달팽이를 보고 있었을 수도 있잖아요.", "달팽이", who=J)
c(290.3, 296.0, "그 이야기를 들어주면 영어도 아이 자신의 발견을 나누는 말이 될 수 있어요.", "발견", who=J)
c(296.1, 303.9, "이게 베어앤조이가 말하는 가르치기보다 함께 사용하기랍니다.", "함께 사용하기", who=J)
c(304.2, 309.2, "이제 화면은 잠시 내려놓고 아이와 정원을 함께 살펴봐주세요.", "정원", who=J)
c(309.3, 313.1, "오늘 나중에 그림책을 보거나 산책하면서 말해보세요.", "산책", who=J)
c(313.2, 315.7, "라고 말이죠.", "", "Let's look together!", J)
c(315.8, 320.2, "영어로 한마디 건네고 한국어로 이야기를 이어가도 좋아요.", "한마디", who=J)
c(320.3, 325.3, "아이가 발견하는 것을 함께 바라보는 순간부터 시작하는 거예요.", "바라보는", who=J)
c(325.4, 329.7, "다섯 번째 작은 모험에도 함께해 주셔서 감사합니다.", "감사합니다", who=J)
c(329.8, 333.9, "오늘은 우리 아이가 무엇을 발견할지 기대해 볼까요?", "발견", who=J)
c(334.0, 336.6, "그럼 내일 만나요. 안녕! 👋", "내일", who=J)

P1 = {"en": "I can see a bear.", "pron": "아이 컨 씨 어 베어", "ko": "곰이 보여요!",
      "words": [{"w": "I", "t": 0}, {"w": "can", "t": 0.15}, {"w": "see", "t": 0.6}, {"w": "a", "t": 1.0}, {"w": "bear.", "t": 1.2}]}
P2 = {"en": "What can you see?", "pron": "왓 캐뉴 씨?", "ko": "뭐가 보이니?",
      "words": [{"w": "What", "t": 0}, {"w": "can", "t": 0.5}, {"w": "you", "t": 0.85}, {"w": "see?", "t": 1.3}], "flow": [[1, 2]]}
P3 = {"en": "Let's look together.", "pron": "렛츠 룩 투게더", "ko": "우리 같이 보자.",
      "words": [{"w": "Let's", "t": 0}, {"w": "look", "t": 0.7}, {"w": "together.", "t": 1.3}]}

MARK_CARD = {"right": 40, "top": 300, "scale": 0.56}
JOY_CARD = {"right": 36, "top": 330, "scale": 0.44}
ev = [
    {"type": "title", "s": 0.1, "e": 6.0},
    {"type": "phrase", "s": 37.6, "e": 68.6, "n": 1, **P1, "reps": [38.2, 43.3, 63.4, 66.1],
     "stress": [{"word": 2, "part": "see", "pron": "씨", "pulses": [57.9, 61.2, 64.0, 66.7]}],
     "note": "'can'은 짧고 약하게, 'see'는 또렷하게"},
    {"type": "yourturn", "s": 48.2, "e": 51.8},
    {"type": "phrase", "s": 75.4, "e": 107.1, "n": 2, **P2, "reps": [78.1, 80.8, 85.9, 98.6],
     "note": "'can you'는 이어서 → 캐뉴 · 묻고 나서 잠깐 기다려요"},
    {"type": "yourturn", "s": 91.3, "e": 94.2},
    {"type": "phrase", "s": 116.3, "e": 147.0, "n": 3, **P3, "reps": [118.9, 124.6, 139.4],
     "stress": [{"word": 2, "part": "geth", "pron": "게", "pulses": [134.6, 137.0, 138.1, 140.9]}],
     "note": "부드러운 목소리로 — 함께하자는 초대예요"},
    {"type": "yourturn", "s": 130.0, "e": 132.7},
    {"type": "phrase", "s": 149.9, "e": 153.5, "n": 1, **P1, "reps": [150.0]},
    {"type": "phrase", "s": 153.5, "e": 155.0, "n": 2, **P2, "reps": [153.6]},
    {"type": "phrase", "s": 155.0, "e": 158.4, "n": 3, **P3, "reps": [155.0]},
    # Joy
    {"type": "voice", "s": 168.7, "e": 171.2, "kind": "tada", "text": "짜잔!", "side": "right", "top": 150},
    {"type": "label", "s": 171.4, "e": 178.8, "text": "Joy · 조이", "sub": "정원 탐험 놀이", "pos": "tr"},
    {"type": "label", "s": 179.2, "e": 185.0, "text": "그림 힌트 페이지", "sub": "Picture clues", "pos": "tr"},
    {"type": "phrase", "s": 199.9, "e": 203.0, "n": 3, **P3, "reps": [200.0], "at": JOY_CARD},
    {"type": "phrase", "s": 210.3, "e": 212.5, "n": 1, **P1, "reps": [210.4], "at": JOY_CARD},
    {"type": "phrase", "s": 214.4, "e": 216.9, "n": 2, **P2, "reps": [214.5], "at": JOY_CARD},
    {"type": "voice", "s": 231.0, "e": 235.8, "kind": "butterfly", "text": "나비!", "ko": "butterfly", "side": "right", "top": 150},
    {"type": "message", "s": 236.2, "e": 241.5, "left": 80, "top": 400, "width": 760,
     "kicker": "오늘 놀이의 주인공", "ko": "아이의 호기심 ✨", "en": "Your child's curiosity leads the way"},
    {"type": "phrase", "s": 268.1, "e": 269.8, "n": 2, **P2, "reps": [268.2], "at": JOY_CARD},
    {"type": "voice", "s": 286.4, "e": 290.2, "kind": "snail", "text": "달팽이!", "ko": "a little snail", "side": "right", "top": 150},
    {"type": "message", "s": 296.1, "e": 303.8, "left": 80, "top": 400, "width": 760,
     "kicker": "Bear & Joy 방식", "ko": "가르치기보다\n함께 사용하기", "en": "Don't just teach English — use it together"},
    {"type": "phrase", "s": 313.1, "e": 315.8, "n": 3, **P3, "reps": [313.2], "at": JOY_CARD},
    # ending: the recap covers the black gap in the source, then the logo card
    {"type": "recap", "s": 336.6, "e": 346.6, "phrases": [
        {"en": P1["en"], "pron": P1["pron"], "ko": P1["ko"]},
        {"en": P2["en"], "pron": P2["pron"], "ko": P2["ko"]},
        {"en": P3["en"], "pron": P3["pron"], "ko": P3["ko"]}], "next": "다음 시간: DAY 6 👋"},
    {"type": "logo", "s": 346.6, "e": 356.6, "ko": "오늘도 아이와 함께 한 걸음 🐾"},
]

# gentle 100% / 104% framing changes on new thoughts (not during phrase repeats)
zooms = [{"t": 0, "z": 1}]
for t, z in [(6.2, 1.04), (21.8, 1), (35.1, 1.04), (68.7, 1), (75.4, 1.04), (107.2, 1), (116.4, 1.04), (147.1, 1), (160.3, 1.04),
             (168.7, 1), (196.6, 1.03), (219.5, 1), (247.1, 1.04), (269.7, 1), (284.4, 1.04), (304.2, 1), (320.3, 1.04), (336.6, 1)]:
    zooms.append({"t": t, "z": z})

spec = {
    "name": "main", "day": 5, "duration": 356.6, "mediaDuration": 353.0, "media": "day5",
    "title": {"en": "Story Detectives", "ko": "이야기 탐정 놀이 🔍", "series": "Bear & Joy First Steps"},
    "watermark": False, "card": MARK_CARD, "turn": {"right": 50, "top": 110, "scale": 0.72},
    "titleAt": {"right": 40, "top": 120, "scale": 0.62}, "titleBacking": True, "captionBottom": 56,
    "scrims": [{"s": 0, "e": 336.6}],
    "musicOn": [[168.4, 356.6, 0.5], [336.6, 356.6, 1.0]],
    "captions": caps, "events": ev, "zooms": zooms,
}
print(json.dumps(spec, ensure_ascii=False, indent=1))
