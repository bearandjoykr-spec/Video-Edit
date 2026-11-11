"""Joy's TOP 3 English picture books (Joy, 11 Nov 2026), filmed at Youngpoong bookstore. Shared by cut.py and build.py.

Joy records the voice-over AFTER the picture is cut, reading script.md line by line at the program times below.
Sources: raw-footage/joy-top3/ (iPhone, SDR bt709, portrait). Original colours (Joy, Day 28: no warm grade).
"""
RAW = "raw-footage/joy-top3"
DAY = 29  # daily series number: confirm with Joy before export
END = 5.0

# Picture, in program order: (clip, src_s, src_e). Durations add up end to end.
PIC = [
    ("clip1.mp4", 2.60, 6.60),    # hook: Joy turns to camera, smiles, V sign
    ("clip2.mov", 2.00, 7.00),    # Youngpoong sign, Joy at the entrance
    ("clip3.mov", 1.00, 3.50),    # walking the aisles
    ("clip4.mov", 3.50, 7.00),    # crouching at the shelf, picks a book
    ("book1.mov", 0.00, 9.20),    # 1 I Want My Hat Back
    ("book2.mov", 2.50, 11.40),   # 2 The Very Hungry Caterpillar (thumbs up)
    ("book3.mov", 0.00, 5.00),    # 3 My Mum / My Dad
    ("book3.mov", 9.30, 12.60),
    ("clip1.mp4", 6.60, 11.00),   # outro: Joy waves and walks on
]
PROG = []
_t = 0.0
for _c, _s, _e in PIC:
    PROG.append(round(_t, 3)); _t += _e - _s
SPEECH_END = round(_t, 3)  # 45.8

# Voice-over script: (start, end, Korean line). " / " = caption page break. Written at about 6 syllables a second.
SCRIPT = [
    (0.15, 3.80, "영어 그림책, 뭐부터 살지 고민이라면? / 이 세 권부터!"),
    (4.10, 8.90, "조이예요! 오늘은 서점에서 / 아이랑 읽기 좋은 영어 그림책을 골라봤어요."),
    (9.20, 14.80, "기준은 딱 하나, / 아이가 '한 번 더!'를 / 외치는 책이에요. / 자, 바로 볼게요!"),
    (15.10, 24.00, "첫 번째, I Want My Hat Back. / 모자 잃은 곰이 계속 물어봐요. / 'Have you seen my hat?' / "
                   "반복이라 금방 따라 하고, / 마지막 반전에 빵 터져요!"),
    (24.30, 33.00, "두 번째, The Very Hungry Caterpillar. / 요일, 숫자, 과일까지 한 권에! / "
                   "책 구멍에 손가락 쏙 넣으며 / 읽어 주세요."),
    (33.20, 41.30, "세 번째, My Mum과 My Dad. / 'She's…', 'He's…' 짧은 문장으로 / "
                   "엄마 아빠를 자랑해요. / 읽고 나서 우리 가족 이야기로 / 이어가 보세요!"),
    (41.50, 45.60, "저장해 두고 서점 갈 때 꺼내 보세요! / 친구에게도 공유해 주세요."),
]
