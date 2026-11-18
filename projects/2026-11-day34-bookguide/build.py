"""DAY 34 "그림책 TOP 3, 이렇게 읽어주세요" (Joy, 17 Nov 2026). Rebuild of the TOP 3 reel around what makes people save it:
for each book the key sentence from inside the book, how to read it aloud, and the question to ask after. A save card closes it,
and a comment keyword ("그림책") sends the card by DM (the DAY 33 pattern).
Inside pages are NOT copied from the internet (the illustrations are copyrighted): the sentence is shown on our own page card,
and Joy can film the real page flips (hands only) to drop in. Joy records the voice-over after approval (script.md).
Run (repo root): .venv/bin/python projects/2026-11-day34-bookguide/build.py
"""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
FPS, DAY = 30, 34
T3 = "raw-footage/joy-top3"; D32 = "raw-footage/day32-books"
# sections: (kind, book, seconds, clip, clip start, korean voice-over line)
SECTIONS = [
    # visual hook (Joy, 18 Nov; like DAY 25): Joy turns to camera with a giant "TOP 3" behind her. One continuous shot split in three: Joy turning to camera (clip1 3.25 s on, 1.5x slow motion); her look-back is frame 0, the thumbnail.
    ("hook", 0, 1.0, "projects/2026-11-day34-bookguide/versions/main/hook-src.mp4", 0.0, "아이가 '한 번 더!' 외치는\n영어 그림책 3권,"),
    ("hook", 0, 1.0, "projects/2026-11-day34-bookguide/versions/main/hook-src.mp4", 1.233, ""),
    ("hook", 0, 1.0, "projects/2026-11-day34-bookguide/versions/main/hook-src.mp4", 2.466, ""),
    # Joy (18 Nov): after her look-back she says it in English and walks into Youngpoong (her live voice, then the entrance)
    ("hookgo", 0, 2.6, f"{T3}/clip1.mp4", 5.55, "I know the best place to go!\n제일 좋은 곳을 알아요! 👣"),
    ("hook", 0, 1.6, f"{T3}/clip2.mov", 2.0, "책 속 문장이랑 읽어주는 법까지\n알려드릴게요!"),
    ("cover", 1, 2.2, f"{T3}/book3.mov", 0.5, "첫 번째, 앤서니 브라운의\nMy Mum, My Dad."),
    ("page", 1, 4.2, f"{D32}/b2.mov", 0.3, "책 속에는 이런 문장이 나와요.\nShe's nice, my mum.\nHe's all right, my dad."),
    ("read", 1, 4.0, f"{T3}/book3.mov", 8.5, "읽을 때는 my mum, my dad에서\n아이를 꼭 안아주세요."),
    ("ask", 1, 4.4, f"{D32}/b1.mov", 0.3, "다 읽고 What can mummy do?\n하고 물어보면,\n아이가 엄마 자랑을 시작해요."),
    ("cover", 2, 2.2, f"{T3}/book2.mov", 2.5, "두 번째,\nThe Very Hungry Caterpillar."),
    ("page", 2, 4.4, f"{D32}/b2.mov", 2.3, "On Monday he ate through one apple.\nBut he was still hungry."),
    ("read", 2, 4.0, f"{T3}/book2.mov", 7.0, "요일이 나올 때마다 아이와 함께\nMonday, Tuesday! 리듬 타듯 읽어 주세요!"),
    ("ask", 2, 4.2, f"{D32}/b6.mov", 0.3, "What did he eat? How many?\n하고 물으면\n영어 숫자가 저절로 나와요."),
    ("cover", 3, 2.2, f"{T3}/book1.mov", 0.0, "세 번째,\nI Want My Hat Back."),
    ("page", 3, 4.0, f"{D32}/b2.mov", 1.5, "모자를 잃어버린 곰이 묻고 또 물어요.\nHave you seen my hat?\n동물들은 No."),
    ("read", 3, 4.0, f"{T3}/book1.mov", 4.5, "동물마다 목소리를 바꿔 주세요.\n아이가 No!를 맡으면 더 재밌어요."),
    ("ask", 3, 4.6, f"{T3}/clip4.mov", 2.5, "Where is the hat?\n하고 물어보세요."),
    # BONUS (Joy, 17 Nov): our own book, Bear & Joy, filmed in Oxford
    ("bonus", 4, 2.6, "raw-footage/day34/n1_sdr.mov", 1.5, "그리고 보너스!\n저희가 만든 그림책, Bear & Joy예요."),
    ("bonus1", 4, 3.6, "raw-footage/day34/n4.mov", 1.4, "영어를 읽기 두려운 부모님도,\n한글 발음 가이드로 바로 읽어줄 수 있어요."),
    ("bonus2", 4, 3.6, "raw-footage/day34/n5.mov", 0.0, "페이지마다 어울리는 질문이 있어서,\n아이의 생각과 상상력이 쑥쑥 자라요."),
    ("bonus3", 4, 3.4, "raw-footage/day34/n2_sdr.mov", 2.0, "그림책을 넘어,\n일상에서도 바로 쓰는 영어가 돼요."),
    ("summary", 0, 5.4, None, 0, "저장해 두고 읽어줄 때 꺼내 보세요."),
    ("end", 0, 4.0, None, 0, ""),
]
BOOKS = {
    1: {"title": "My Mum · My Dad", "author": "Anthony Browne", "cover": "mumdad.jpg", "age": "3세+",
        "lines": ["She's nice, my mum.", "He's all right, my dad."], "lines_ko": ["우리 엄마는 좋아요.", "우리 아빠는 괜찮아요."],
        "read": ["my mum · my dad 에서", "아이를 꼭 안아주며 읽기 🤗"], "ask": "What can mummy do?", "ask_ko": "엄마는 뭘 잘해?", "answer": "She can cook! 🍳"},
    2: {"title": "The Very Hungry Caterpillar", "author": "Eric Carle", "cover": "caterpillar.jpg", "age": "1세+",
        "lines": ["On Monday he ate through", "one apple."], "lines_ko": ["월요일에 사과 한 개를", "먹었어요."],
        "read": ["요일마다 리듬 타듯 🎵", "Monday, Tuesday!"], "ask": "What did he eat?", "ask_ko": "뭘 먹었어?", "answer": "Apple! 🍎"},
    3: {"title": "I Want My Hat Back", "author": "Jon Klassen", "cover": "hat.jpg", "age": "4세+",
        "lines": ["Have you seen my hat?", "No."], "lines_ko": ["내 모자 봤니?", "아니."],
        "read": ["동물마다 목소리 바꾸기 🎭", "아이는 'No!' 담당"], "ask": "Where is the hat?", "ask_ko": "모자는 어디 있을까?", "answer": "There! 👀"},
}


# Joy + Mark's voice-over (raw-footage/day34/vo.m4a, 17 Nov 2026). Takes picked by ear-probing the recording: the interrupted
# "What did he eat?" (46-50 s) and the mixed-up first "동물마다…" take (73-78 s) are dropped for their retakes; "아이가 먼저 모자를
# 찾아요" is left out (Joy removed that caption). Per section: list of (src_s, src_e) pieces placed back to back.
VO = {
    3: [(5.60, 8.05, 0.15, "raw-footage/joy-top3/clip1.mp4")],  # Joy live: "I know the best place to go!"
    0: [(1.60, 4.95)], 4: [(5.30, 8.20)],
    5: [(8.55, 12.55)], 6: [(13.15, 19.35)], 7: [(19.75, 24.52)], 8: [(24.78, 29.55)],  # (Joy) 안아주세요 ends at 24.5: keep its last syllable
    9: [(29.82, 33.50)], 10: [(34.35, 40.15)], 11: [(40.38, 42.56), (42.60, 43.43, 0.02), (43.72, 44.70), (44.74, 46.00)],  # Monday / Tuesday on the beat, with claps
    12: [(57.22, 62.80)],
    13: [(63.18, 66.30)], 14: [(66.82, 73.30)], 15: [(80.38, 84.90)], 16: [(85.48, 88.32)],
    17: [(90.40, 93.98)], 18: [(94.04, 98.60)], 19: [(99.06, 104.55)], 20: [(104.76, 108.16)],
    21: [(108.70, 110.70), (111.22, 114.10)], 22: [(114.52, 116.25)],
}
GAP = 0.35   # breath after each line
HOOK_SPLIT = (0, 3)  # the hook's four quick cuts share the two hook lines


def main():
    # section lengths follow the voice: each voiced section = its audio + a short breath
    durs = [x[2] for x in SECTIONS]
    for i, pcs in VO.items():
        a = sum(pc[1] - pc[0] for pc in pcs) + GAP + 0.15 * (len(pcs) - 1)
        if i == 0:     # line 1 spans hook cuts 0-2
            for j in range(3):
                durs[j] = round(a / 3, 3)
        elif i == 3:
            durs[3] = round(max(a, 2.6), 3)
        elif i == 4:
            durs[4] = round(a, 3)
        elif SECTIONS[i][0] == "end":
            durs[i] = max(4.0, a)
        else:
            durs[i] = round(max(a, 2.0), 3)
    t, secs, vo_place, sfx_extra = 0.0, [], [], []
    for k, (kind, book, d, clip, cs, vo) in enumerate(SECTIONS):
        d = durs[k]
        secs.append({"kind": kind, "book": book, "s": round(t, 3), "e": round(t + d, 3), "clip": clip, "cs": cs, "vo": vo}); t += d
    for i, pcs in VO.items():
        at = secs[i]["s"] + (0.1 if SECTIONS[i][0] not in ("hook", "hookgo") else 0)
        for pc in pcs:
            s_, e_ = pc[0], pc[1]; gap = pc[2] if len(pc) > 2 else 0.15
            vo_place.append({"src_s": s_, "src_e": e_, "at": round(at, 3), "src": pc[3] if len(pc) > 3 else "raw-footage/day34/vo.m4a"}); at += e_ - s_ + gap
    # Monday! Tuesday!: a clap on every syllable (MON-day, TUES-day) so the rhythm is heard
    mon = next(v for v in vo_place if v["src_s"] == 42.60); tue = next(v for v in vo_place if v["src_s"] == 43.72)
    for at in (mon["at"] + .05, mon["at"] + .40, tue["at"] + .05, tue["at"] + .49):
        sfx_extra.append({"t": round(at, 3), "sound": "clap", "gain": -6})
    # captions: the hook's first line runs across cuts 0-2
    for x in secs[:3]:
        x["vo"] = SECTIONS[0][5]
    total = round(t, 3)
    sfx = []
    add = lambda tt, s_, g: sfx.append({"t": round(tt, 3), "sound": s_, "gain": g})
    for x in secs:
        if x["kind"] == "hook":
            add(x["s"], "whoosh", -10)
        if x["kind"] == "cover":
            add(x["s"], "impact", -7); add(x["s"] + .05, "sparkle", -12)
        if x["kind"] in ("page", "read", "ask"):
            add(x["s"], "pop", -10)
        if x["kind"] == "bonus":
            add(x["s"], "impact", -6); add(x["s"] + .05, "sparkle", -10)
        if x["kind"].startswith("bonus") and x["kind"] != "bonus":
            add(x["s"], "pop", -9)
        if x["kind"] == "summary":
            add(x["s"], "chime", -8)
        if x["kind"] == "end":
            add(x["s"], "whoosh", -10); add(x["s"] + 1.9, "pop", -6); add(x["s"] + 2.8, "pop", -6); add(x["s"] + 2.85, "chime", -9)
    plan = {"fps": FPS, "day": DAY, "duration": total, "frames": int(math.ceil(total * FPS)), "media": "day34/main",
            "sections": [{k: v for k, v in x.items() if k not in ("clip", "cs")} for x in secs], "vo": vo_place, "books": {str(k): v for k, v in BOOKS.items()},
            "sfx": sorted(sfx + sfx_extra, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/main/timeline.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    json.dump(secs, open(f"{HERE}/versions/main/sections_src.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s, {len(secs)} sections")


if __name__ == "__main__":
    main()
