"""Joy's TOP 3 English picture books (Joy, 11 Nov 2026), filmed at Youngpoong bookstore. Shared by cut.py and build.py.

Joy records the voice-over AFTER the picture is cut, reading script.md line by line at the program times below.
Sources: raw-footage/joy-top3/ (iPhone, SDR bt709, portrait). Original colours (Joy, Day 28: no warm grade).
"""
RAW = "raw-footage/joy-top3"
DAY = 30  # Joy: DAY 29 is a Mark video
END = 4.5

# v2 (Joy, 11 Nov 2026: "not exciting enough"): mystery hook with three "?" books, card-flip reveals numbered 1-2-3
# (Joy: no ranking, the three books are in no particular order),
# a save-worthy info card per book and a summary card at the end.
# Picture, in program order: (clip, src_s, src_e, scene).
PIC = [
    ("clip3.mov", 1.00, 4.80, "hook"),     # aisles, darkened: three mystery books
    ("clip1.mp4", 3.40, 5.55, "markq"),    # LIVE: Mark asks "What's your favourite children's book?", Joy turns and smiles
    ("clip2.mov", 3.00, 4.40, "joy"),      # Youngpoong sign
    ("clip4.mov", 3.50, 4.90, "reveal1"),  # card flip: 1
    ("book3.mov", 0.00, 5.00, "book1"),    # 1 My Mum / My Dad
    ("book3.mov", 9.30, 12.60, "book1"),
    ("clip4.mov", 4.90, 6.30, "reveal2"),
    ("book2.mov", 2.50, 11.40, "book2"),   # The Very Hungry Caterpillar (thumbs up)
    ("clip3.mov", 3.50, 4.90, "reveal3"),
    ("book1.mov", 0.00, 9.20, "book3"),    # 3 I Want My Hat Back
    ("clip2.mov", 9.00, 13.80, "summary"), # walking in the shop (under the summary card)
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
SPEECH_END = round(_t, 3)  # 47.0

# Voice-over script: (start, end, Korean line). " / " = caption page break. Written at about 6 syllables a second.
SCRIPT = [
    (0.15, 3.60, "수천 권 중에 / 아이가 '한 번 더!' 외치는 책, / 딱 3권!"),
    (6.05, 7.25, "그럼, 첫 번째 책부터 볼게요!"),
    (7.45, 16.85, "첫 번째! 앤서니 브라운의 My Mum, My Dad. / 'She's…', 'He's…' 짧은 문장으로 / 엄마 아빠를 자랑하는 책이에요. / "
                  "다 읽으면 '우리 엄마는?' 하고 / 물어봐 주세요."),
    (17.15, 27.15, "두 번째! The Very Hungry Caterpillar. / 요일, 숫자, 음식 이름이 / 한 권에 다 들어 있어요. / "
                   "책 구멍에 손가락을 쏙 넣으면서 / 읽어 주세요!"),
    (27.45, 37.75, "세 번째! I Want My Hat Back. / 모자 잃은 곰이 계속 물어봐요. / 'Have you seen my hat?' / "
                   "아이가 금방 따라 하는데요, / 결말은… 직접 확인해 보세요! 🤫"),
    (38.05, 42.60, "저장해 두고 서점 갈 때 꺼내 보세요! / 친구에게도 꼭 보내 주세요."),
    (45.30, 46.90, "다음엔 어디로 갈까요? 👀"),
]
