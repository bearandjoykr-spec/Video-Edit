"""Day 25 edit decision list: Mark's 3 picture books at Kyobo. Shared by cut.py and build.py.

Sources are SDR H.264 copies made with macOS avconvert (the iPhone clips are HLG HDR):
  avconvert -s IMG_xxxx.MOV -p Preset1920x1080 -o sdr/IMG_xxxx.mov
VO is the owner's voice memo (raw-footage/2026-11-new/vo-memo.m4a); the false start
"Comment bear or DM us. I'm going to say that again." and the closing "Thank you" are cut.
"""
RAW = "raw-footage/2026-11-new"
SDR = f"{RAW}/sdr"
VO_SRC = "projects/2026-11-day25-kyobo/work/vo-clean.wav"  # made by voice.sh from {RAW}/vo-memo.m4a
DAY = 25
END = 5.0

HOOK = ("IMG_8407", 0.0, 5.833)  # Mark on the bench; real audio: "우리 아이에게 어떤 책 추천하세요?"

# Voice-over pieces: (memo start, memo end, program start). Each piece keeps its own breaths.
VO = [
    (1.50, 11.70, 6.00),   # This is Kyobo ... books make people.
    (11.90, 19.70, 16.20),  # I love that. So here are three English picture books ...
    (19.80, 32.50, 24.00),  # Number one, Mum, Me and the Mulberry Tree ...
    (32.80, 44.55, 36.70),  # Number two, Room on the Broom ...
    (44.55, 57.30, 48.45),  # Number three, I Love You Through and Through ...
    (57.30, 66.95, 61.20),  # And a cheeky bonus ... How a Bear Found Joy.
    (72.24, 79.35, 70.95),  # Comment bear or DM us to reserve yours ...
]
SPEECH_END = round(VO[-1][2] + VO[-1][1] - VO[-1][0], 3)  # 78.06


def memo_to_prog(t):
    for s, e, p in VO:
        if s - 0.3 <= t <= e + 0.3:
            return round(p + t - s, 3)
    raise ValueError(t)


# Picture, in program order: (clip, src_s, src_e, options). Durations add up end to end.
# options: slow=factor (slow motion, motion-interpolated), crop=(w, h, x, y) before scaling to 1080x1920
PIC = [
    ("IMG_8407", 0.0, 5.833, {}),                 # hook
    ("IMG_8408", 0.0, 6.067, {}),                 # stones, pan to Mark — "This is Kyobo"
    ("IMG_8408", 0.0, 2.15, {"slow": 2.0, "crop": (864, 1536, 108, 384)}),  # the quote on the stones, closer
    ("IMG_8411", 0.0, 4.60, {}),                  # walking in
    ("IMG_8410", 0.0, 3.20, {}),                  # the picture-book table
    ("IMG_8412", 1.0, 5.90, {}),                  # Mark picks up the books
    ("IMG_8413", 6.2, 14.0, {}),                  # 1 Mum, Me and the Mulberry Tree
    ("IMG_8412", 13.0, 16.0, {}),                 # 2 Room on the Broom
    ("IMG_8413", 16.0, 25.2, {}),
    ("IMG_8413", 25.2, 37.39, {}),                # 3 I Love You Through and Through
    ("ART", 0.0, None, {}),                       # Bear & Joy Book 1 on the watercolour art, to the end
]
