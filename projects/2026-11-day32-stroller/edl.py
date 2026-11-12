"""DAY 32 "유모차 산책 영어" (Joy, 12 Nov 2026). Joy wanted more excitement, related footage and backgrounds, not only her face.
Source: raw-footage/day32/main.mp4 (Joy to camera, 1080x1920, 72 s). B-roll: Joy's autumn walks (walk1 red trees, walk2 ginkgo,
walk3 sky and road) and one Pexels stroller clip (STOCK.md). Joy's voice runs throughout; over B-roll she stays in a round
picture-in-picture. Nothing is sped up. Original colours.
"""
RAW = "raw-footage/day32"
DAY = 32
END = 5.0
BROLL = {"stroller": f"{RAW}/stock/stroller1.mp4", "walk1": f"{RAW}/walk1.mov", "walk2": f"{RAW}/walk2.mov", "walk3": f"{RAW}/walk3.mov"}
# (kind, voice src_s, voice src_e, b-roll name, b-roll start). Times are snapped to quiet points by build/cut.
SEGS = [
    ("cold", 24.70, 27.00, "stroller", 0.0),   # cold open: stroller POV on autumn leaves + Joy's "Here we go!"
    ("joy", 4.55, 8.10, None, 0),              # 아직 말을 시작하지 않은 아기에게…
    ("joy", 8.60, 11.70, None, 0),             # 특히 아기랑 단둘이 산책을 하거나 유모차를 끌 때
    ("broll", 11.70, 15.35, "walk3", 1.0),     # 무슨 말을 해야 할지 막막한…
    ("joy", 15.80, 22.30, None, 0),            # 어렵게 생각하지 않으셔도 돼요…
    ("broll", 22.95, 27.00, "stroller", 3.0),  # 1 Here we go!
    ("broll", 27.55, 32.80, "walk1", 2.0),     # 2 Look at that tree!
    ("broll", 32.80, 37.80, "walk2", 1.0),     # 3 Can you feel the breeze?
    ("joy", 38.35, 45.00, None, 0),            # 작은 것들을 짧은 영어 한마디로
    ("joy", 45.60, 54.15, None, 0),            # 대답 못 해도 괜찮아요…
    ("joy", 54.15, 61.80, None, 0),            # 표현이 더 필요하신가요? 댓글에 '산책'
    ("broll", 61.80, 68.25, "walk1", 9.0),     # 20가지를 정리해서 보내드릴게요
    ("joy", 68.20, 69.90, None, 0),            # 그럼 안녕~
]
# Captions in SOURCE time: (s, e, korean, english or ""). " / " = page break. English lines also get a big phrase pop.
LINES = [
    (4.60, 8.04, "아직 말을 시작하지 않은 아기에게 / 영어로는 뭐라고 말하면 좋을까?", ""),
    (8.68, 11.70, "특히 아기랑 단둘이 산책을 하거나 / 유모차를 끌 때", ""),
    (11.70, 15.28, "무슨 말을 해야 할지 / 막막한 부모님들도 계실 것 같아요.", ""),
    (15.88, 17.94, "그런데 어렵게 생각하지 않으셔도 돼요.", ""),
    (18.48, 22.24, "지금 아이와 함께 보고 느끼는 것들을 / 영어로 이야기해 보세요.", ""),
    (23.02, 24.78, "유모차를 끌고 출발할 때는", ""),
    (24.78, 26.92, "자, 출발!", "Here we go!"),
    (27.64, 29.88, "산책하다가 나무를 발견했다면", ""),
    (29.88, 32.76, "저 나무 좀 봐!", "Look at that tree!"),
    (32.76, 35.20, "바람이 살랑살랑 불 때는", ""),
    (35.20, 37.70, "바람 느껴져?", "Can you feel the breeze?"),
    (38.44, 44.94, "이렇게 아이와 함께 발견하는 작은 것들을 / 짧은 영어 한마디로 이야기해 주는 거예요.", ""),
    (45.68, 48.22, "아직 아기가 대답하지 못해도 괜찮아요.", ""),
    (48.78, 54.12, "아기의 표정이나 옹알이, 몸짓에 반응하면서 / 자연스럽게 대화를 이어가 보세요.", ""),
    (54.12, 58.42, "아기와 산책할 때 사용할 수 있는 / 영어 표현이 더 필요하신가요?", ""),
    (58.88, 61.76, "댓글에 '산책'이라고 남겨 주세요.", ""),
    (61.76, 68.20, "유모차를 끌거나 아기와 산책할 때 / 바로 쓸 수 있는 영어 표현 / 20가지를 정리해서 보내드릴게요.", ""),
    (68.20, 69.76, "그럼 안녕~!", ""),
]
