"""Joy's TOP 3 English picture books (Joy, 11 Nov 2026), filmed at Youngpoong bookstore. Shared by cut.py and build.py.

Joy records the voice-over AFTER the picture is cut, reading script.md line by line at the program times below.
Sources: raw-footage/joy-top3/ (iPhone, SDR bt709, portrait). Original colours (Joy, Day 28: no warm grade).
"""
RAW = "raw-footage/joy-top3"
DAY = 30  # Joy: DAY 29 is a Mark video
END = 3.5

# v2 (Joy, 11 Nov 2026: "not exciting enough"): mystery hook with three "?" books, card-flip reveals numbered 1-2-3
# (Joy: no ranking, the three books are in no particular order),
# a save-worthy info card per book and a summary card at the end.
# Picture, in program order: (clip, src_s, src_e, scene).
# v5 (Joy, 12 Nov 2026: "will parents lying in bed watch to the end?"): 39 s, a call-out hook that promises the
# summary card at the end, 7 s per book, no entrance shot.
PIC = [
    ("clip3.mov", 1.00, 4.40, "hook"),     # aisles, darkened: three mystery books
    ("clip1.mp4", 3.40, 5.55, "markq"),    # LIVE: Mark asks "What's your favourite children's book?", Joy turns and smiles
    ("clip4.mov", 3.50, 4.40, "reveal1"),  # card flip: 1
    ("book3.mov", 0.00, 3.60, "book1"),    # 1 My Mum / My Dad
    ("book3.mov", 9.60, 12.40, "book1"),
    ("clip4.mov", 4.90, 5.80, "reveal2"),
    ("book2.mov", 5.00, 11.40, "book2"),   # 2 The Very Hungry Caterpillar (thumbs up)
    ("clip3.mov", 3.50, 4.40, "reveal3"),
    ("book1.mov", 0.40, 6.80, "book3"),    # 3 I Want My Hat Back
    ("clip2.mov", 9.00, 13.00, "summary"), # walking in the shop (under the summary card)
    ("clip1.mp4", 5.55, 9.80, "outro"),    # LIVE: Joy "I know the best place to go!" and walks off; "oh okay" after 8.0 is muted
]
LIVE = {"markq": None, "outro": 8.0}  # scenes whose own sound plays at full level (value: source time to fade out at)
# On-screen lines for the live sound (program times are filled in by build.py from these source times)
LIVE_LINES = [
    {"scene": "markq", "src_s": 3.65, "src_e": 5.55, "who": "mark", "en": "What's your favourite children's book?", "ko": "가장 좋아하는 어린이책이 뭐예요?"},
    {"scene": "outro", "src_s": 5.60, "src_e": 8.00, "who": "joy", "en": "I know the best place to go!", "ko": "제일 좋은 곳을 알아요!"},
]
PROG = []
_t = 0.0
for _c, _s, _e, _n in PIC:
    PROG.append(round(_t, 3)); _t += _e - _s
SPEECH_END = round(_t, 3)  # 35.7

# Voice-over script: (start, end, Korean line). " / " = caption page break. Written at about 6 syllables a second.
SCRIPT = [
    (0.10, 3.20, "아이가 '한 번 더!' 외치는 영어 그림책, / 딱 3권!"),
    (5.60, 12.60, "첫 번째! My Mum, My Dad. / 'She's…', 'He's…'로 / 엄마 아빠 자랑하는 책! / "
                  "다 읽고 '우리 엄마는?' 물어보세요."),
    (12.90, 20.00, "두 번째! The Very Hungry Caterpillar. / 요일, 숫자, 음식이 한 권에! / 구멍에 손가락 쏙 넣으며 / 읽어 주세요."),
    (20.20, 27.30, "세 번째! I Want My Hat Back. / 모자 잃은 곰이 계속 물어요. / 'Have you seen my hat?' / 결말은… 직접 확인하세요! 🤫"),
    (27.60, 31.20, "우리 아이 취향은 몇 번? / 댓글로 숫자만 남겨 주세요!"),
    (34.00, 35.60, "다음엔 어디로 갈까요? 👀"),
]
