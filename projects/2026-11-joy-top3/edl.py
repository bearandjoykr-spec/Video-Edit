"""Joy's TOP 3 English picture books (Joy, 11 Nov 2026), filmed at Youngpoong bookstore. Shared by cut.py and build.py.

Joy records the voice-over AFTER the picture is cut, reading script.md line by line at the program times below.
Sources: raw-footage/joy-top3/ (iPhone, SDR bt709, portrait). Original colours (Joy, Day 28: no warm grade).
"""
RAW = "raw-footage/joy-top3"
DAY = 29  # daily series number: confirm with Joy before export
END = 4.5

# v2 (Joy, 11 Nov 2026: "not exciting enough"): mystery hook with three "?" books, a 3-2-1 countdown with card-flip reveals,
# a save-worthy info card per book and a summary card at the end.
# Picture, in program order: (clip, src_s, src_e, scene).
PIC = [
    ("clip3.mov", 1.00, 4.80, "hook"),     # aisles, darkened: three mystery books
    ("clip1.mp4", 2.60, 5.20, "joy"),      # Joy turns to camera, V sign
    ("clip2.mov", 3.00, 4.20, "joy"),      # Youngpoong sign
    ("clip4.mov", 3.50, 4.90, "reveal3"),  # card flip: No.3
    ("book3.mov", 0.00, 5.00, "book3"),    # My Mum / My Dad
    ("book3.mov", 9.30, 12.60, "book3"),
    ("clip4.mov", 4.90, 6.30, "reveal2"),
    ("book2.mov", 2.50, 11.40, "book2"),   # The Very Hungry Caterpillar (thumbs up)
    ("clip3.mov", 3.50, 4.90, "reveal1"),
    ("book1.mov", 0.00, 9.20, "book1"),    # I Want My Hat Back
    ("clip1.mp4", 6.60, 11.40, "summary"), # Joy waves (under the summary card)
]
PROG = []
_t = 0.0
for _c, _s, _e, _n in PIC:
    PROG.append(round(_t, 3)); _t += _e - _s
SPEECH_END = round(_t, 3)  # 43.0

# Voice-over script: (start, end, Korean line). " / " = caption page break. Written at about 6 syllables a second.
SCRIPT = [
    (0.15, 3.60, "수천 권 중에 / 아이가 '한 번 더!' 외치는 책, / 딱 3권!"),
    (3.90, 7.40, "영어 선생님 조이가 직접 골랐어요. / 3위부터 갈게요!"),
    (7.70, 17.10, "3위! 앤서니 브라운의 My Mum, My Dad. / 'She's…', 'He's…' 짧은 문장으로 / 엄마 아빠를 자랑하는 책이에요. / "
                  "다 읽으면 '우리 엄마는?' 하고 / 물어봐 주세요."),
    (17.40, 27.40, "2위! The Very Hungry Caterpillar. / 요일, 숫자, 음식 이름이 / 한 권에 다 들어 있어요. / "
                   "책 구멍에 손가락을 쏙 넣으면서 / 읽어 주세요!"),
    (27.70, 38.00, "대망의 1위! I Want My Hat Back. / 모자 잃은 곰이 계속 물어봐요. / 'Have you seen my hat?' / "
                   "아이가 금방 따라 하는데요, / 결말은… 직접 확인해 보세요! 🤫"),
    (38.30, 43.00, "저장해 두고 서점 갈 때 꺼내 보세요! / 친구에게도 꼭 보내 주세요."),
]
