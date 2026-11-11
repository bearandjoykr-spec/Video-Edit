"""Day 29 — Harry Potter phrases. Builds versions/<v>/plan.json for Remotion Day29Magic.

v2 (owner feedback on the test, 11 Nov 2026): no clips behind Mark and no freezing. After Mark finishes a sentence,
a full-screen "magic cut" to the film scene plays the line with Harry Potter-font captions (English + Korean),
then cuts back. Cut points sit inside real silences (ffmpeg silencedetect -35 dB), not Whisper word times
(Whisper ended words ~0.35 s early, which made the test pause mid-word).
Usage (repo root): python3 projects/2026-11-day29-christmas-phrases/build_plan.py [version]
"""
import json, sys, os

V = sys.argv[1] if len(sys.argv) > 1 else "main"
P = os.path.dirname(os.path.abspath(__file__))
FPS = 30
PAD = 0.32   # clip picture before/after the film line (covers the magic-cut transition)

# (Mark stops, Mark resumes, clip, clip in, clip out, EN, KO) — stop/resume = silence start + 0.12 / silence end − 0.10
FILMS = [
    (7.78, 8.78,  "christmas", 10.25, 12.05, "Happy Christmas, Harry!", "해피 크리스마스, 해리!"),
    (24.31, 24.56, "christmas", 12.05, 14.05, "Happy Christmas, Ron.", "해피 크리스마스, 론."),
    (29.97, 30.36, "brilliant", 15.00, 18.10, "Brilliant, but scary.", "최고야, 근데 좀 무서워."),
    (37.58, 38.23, "blimey",    14.95, 15.85, "Blimey.", "세상에."),
    (44.43, 44.93, "platform", 138.60, 141.00, "Best do it at a bit of a run if you're nervous.", "긴장되면 살짝 뛰어서 가렴."),
    (53.89, 54.09, "map",      116.30, 119.60, "Just give it a tap and say… Mischief managed.", "톡 치고 말하렴… 장난 완료."),
]
MARK_START, MARK_END = 0.55, 59.36

LINES = [  # Mark's captions in source time; boundaries sit in silences
    (0.55, 7.78, "Why does Ron say Happy Christmas, not Merry Christmas?", "론은 왜 '메리 크리스마스'가 아니라 '해피 크리스마스'라고 할까요?"),
    (8.78, 11.60, "Because that's how we say it in Britain.", "영국에서는 그렇게 말하거든요."),
    (11.60, 17.90, "Five Harry Potter phrases to teach your child before Christmas Day.", "크리스마스 전에 아이에게 알려 줄 해리 포터 표현 5가지!"),
    (17.90, 21.34, "Number five, Happy Christmas.", "5번, 해피 크리스마스."),
    (21.34, 24.31, "Same meaning, more British.", "뜻은 같아요, 더 영국식일 뿐!"),
    (24.56, 27.05, "Four, Brilliant.", "4번, 브릴리언트."),
    (27.05, 29.97, "Not “good job” — brilliant.", "“잘했어” 말고, “최고야!”"),
    (30.36, 33.20, "Number three, Blimey.", "3번, 블라이미."),
    (33.20, 37.58, "For when the snow is this deep… Blimey.", "눈이 이만큼 쌓였을 때, “세상에!”"),
    (38.23, 40.65, "Two, Off you go.", "2번, 오프 유 고."),
    (40.65, 44.43, "Shoes on, coat on, off you go.", "신발 신고, 코트 입고, “자, 출발!”"),
    (44.93, 50.34, "And number one, for when the toys are finally tidied away…", "그리고 1번, 장난감을 다 정리했을 때…"),
    (50.34, 53.89, "(whisper) Mischief managed.", "(속삭이며) “장난 완료.”"),
    (54.09, 59.11, "Save this and try one tonight. Happy Christmas from Oxford.", "저장해 두고 오늘 밤 하나 써 보세요. 옥스퍼드에서, 해피 크리스마스!"),
]
PHRASES = [(17.90, 5, "Happy Christmas", "해피 크리스마스"), (24.56, 4, "Brilliant", "최고야!"),
           (30.36, 3, "Blimey", "세상에!"), (38.23, 2, "Off you go", "자, 출발!"), (44.93, 1, "Mischief managed", "장난 완료")]

segs, t, src = [], 0.0, MARK_START
for stop, resume, clip, cs, ce, en, ko in FILMS:
    segs.append({"kind": "mark", "src": src, "srcEnd": stop, "s": t, "e": t + stop - src}); t += stop - src
    d = PAD + (ce - cs) + PAD
    segs.append({"kind": "film", "clip": clip, "src": f"day29/clips/{clip}.mp4", "clipIn": cs, "clipOut": ce,
                 "s": t, "e": t + d, "lineS": t + PAD, "en": en, "ko": ko}); t += d
    src = resume
segs.append({"kind": "mark", "src": src, "srcEnd": MARK_END, "s": t, "e": t + MARK_END - src}); t += MARK_END - src
END_CARD = 4.2  # logo + "new Harry Potter series 25 Dec — is your English ready? Follow for more"
total = t + END_CARD

def out(x):
    for s in segs:
        if s["kind"] == "mark" and s["src"] - 1e-6 <= x <= s["srcEnd"] + 1e-6:
            return s["s"] + x - s["src"]
    raise ValueError(x)

r = lambda v: round(v, 3)
plan = {
    "name": f"day29-{V}", "fps": FPS, "duration": r(total), "frames": int(round(total * FPS)), "day": 29,
    "subject": "day29/subject.webm", "background": "day29/great-hall.jpg",
    # glasses + scar (owner: on from the very first frame through the hook question, and again for the sign-off)
    "props": [{"dir": "day29/props-start", "srcFrom": 0.0, "frames": 237, "s": 0.0, "e": r(out(7.78)), "poofIn": False},
              {"dir": "day29/props-end", "srcFrom": 53.9, "frames": 168, "s": r(out(54.6)), "e": r(out(MARK_END)) + 0.3, "poofIn": True}],
    "hook": {"s": 0.0, "e": r(out(7.78)), "strike": r(out(1.6)), "happy": r(out(2.3)),
             "top": "Why does Ron say…", "no": "Merry Christmas", "yes": "Happy Christmas?", "ko": "왜 ‘메리’가 아니라 ‘해피’ 크리스마스일까?"},
    "cta": {"en1": "The new Harry Potter series", "en2": "arrives 25 December", "q": "Is your English ready?",
            "ko": "새 해리 포터 시리즈가 12월 25일에 찾아와요. 영어 준비됐나요?", "follow": "Follow for more", "followKo": "팔로우하고 함께 준비해요"},
    "title": {"s": r(out(12.0)), "e": r(out(17.7)), "en": "5 Harry Potter Phrases",
              "sub": "to teach your child before Christmas", "ko": "크리스마스 전에 알려 줄 해리 포터 표현 5가지"},
    "segments": [{k: (r(v) if isinstance(v, float) else v) for k, v in s.items()} for s in segs],
    "captions": [{"s": r(out(a)), "e": r(out(b)), "en": en, "ko": ko} for a, b, en, ko in LINES[1:]],  # hook text replaces line 1
    "phrases": [{"s": r(out(a)), "n": n, "en": en, "ko": ko} for a, n, en, ko in PHRASES],
    "endCard": {"s": r(t), "e": r(total)},
}
os.makedirs(f"{P}/versions/{V}", exist_ok=True)
json.dump(plan, open(f"{P}/versions/{V}/plan.json", "w"), ensure_ascii=False, indent=1)
print(f"{V}: {total:.2f} s, {plan['frames']} frames, {sum(s['kind'] == 'film' for s in segs)} film cuts")
