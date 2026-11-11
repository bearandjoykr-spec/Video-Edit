"""Day 29 — Harry Potter phrases. Builds versions/<v>/plan.json (Remotion Day29Magic) from Mark's take plus film-line pauses.

Mark freezes while each film line plays (owner, 11 Nov 2026: "clips can play, you can pause me when i speak").
Times: Mark source = raw-footage/day29/day29.mov; clip times = raw-footage/day29/clips/<name>.mp4 (Whisper word timings).
Usage (repo root): python3 projects/2026-11-day29-christmas-phrases/build_plan.py [version]
"""
import json, sys, os

V = sys.argv[1] if len(sys.argv) > 1 else "test"
P = os.path.dirname(os.path.abspath(__file__))
FPS = 30
GAP = 0.18      # beat of silence either side of a film line
TAIL = 1.4      # clip keeps playing (muted) behind Mark after he resumes

# (pause after Mark source time, clip, clip in, clip out, film line EN, KO)
PAUSES = [
    (7.40,  "christmas", 10.25, 12.05, "Happy Christmas, Harry!", "해피 크리스마스, 해리!"),
    (21.00, "christmas", 12.05, 14.05, "Happy Christmas, Ron.", "해피 크리스마스, 론."),
    (26.30, "brilliant", 15.00, 18.10, "Brilliant, but scary.", "최고야, 근데 좀 무서워."),
    (32.60, "blimey",    14.95, 15.85, "Blimey.", "세상에."),
    (39.95, "platform", 138.60, 141.00, "Best do it at a bit of a run if you're nervous.", "긴장되면 살짝 뛰어서 가렴."),
    (50.70, "map",      116.30, 119.60, "Just give it a tap and say… “Mischief managed.”", "톡 치고 말하렴… “장난 완료.”"),
]
MARK_END = 59.6

# Mark's lines (source times) with the phrase-number moments
LINES = [
    (0.74, 7.28, "Why does Ron say Happy Christmas, not Merry Christmas?", "론은 왜 '메리 크리스마스'가 아니라 '해피 크리스마스'라고 할까요?"),
    (8.38, 11.34, "Because that's how we say it in Britain.", "영국에서는 그렇게 말하거든요."),
    (12.00, 17.70, "Five Harry Potter phrases to teach your child before Christmas Day.", "크리스마스 전에 아이에게 알려 줄 해리 포터 표현 5가지!"),
    (18.28, 21.00, "Number five, Happy Christmas.", "5. 해피 크리스마스"),
    (21.00, 23.78, "Same meaning, more British.", "뜻은 같아요, 더 영국식일 뿐!"),
    (24.30, 26.30, "Four, Brilliant.", "4. 브릴리언트"),
    (26.30, 29.48, "Not “good job” — brilliant.", "“잘했어” 말고, “최고야!”"),
    (30.38, 32.60, "Number three, Blimey.", "3. 블라이미"),
    (32.60, 37.42, "For when the snow is this deep… Blimey.", "눈이 이만큼 쌓였을 때, “세상에!”"),
    (38.02, 39.95, "Two, Off you go.", "2. 오프 유 고"),
    (39.95, 44.18, "Shoes on, coat on, off you go.", "신발 신고, 코트 입고, “자, 출발!”"),
    (44.18, 50.70, "And number one, for when the toys are finally tidied away…", "그리고 1번, 장난감을 다 정리했을 때…"),
    (50.70, 53.62, "(whisper) Mischief managed.", "(속삭이며) “장난 완료.”"),
    (54.12, 58.76, "Save this and try one tonight. Happy Christmas from Oxford.", "저장해 두고 오늘 밤 하나 써 보세요. 옥스퍼드에서, 해피 크리스마스!"),
]
# Big phrase cards (source time the card appears, number, phrase, Korean gloss)
PHRASES = [
    (18.28, 5, "Happy Christmas", "해피 크리스마스"),
    (24.30, 4, "Brilliant", "최고야!"),
    (30.38, 3, "Blimey", "세상에!"),
    (38.02, 2, "Off you go", "자, 출발!"),
    (45.20, 1, "Mischief managed", "장난 완료"),
]

segs, t, src = [], 0.0, 0.0
for at, clip, cs, ce, en, ko in PAUSES:
    segs.append({"kind": "mark", "src": src, "srcEnd": at, "s": t, "e": t + at - src}); t += at - src
    d = GAP + (ce - cs) + GAP
    segs.append({"kind": "film", "clip": clip, "clipIn": cs, "clipOut": ce, "freeze": at, "s": t, "e": t + d,
                 "lineS": t + GAP, "en": en, "ko": ko}); t += d
    src = at
segs.append({"kind": "mark", "src": src, "srcEnd": MARK_END, "s": t, "e": t + MARK_END - src}); t += MARK_END - src
END_CARD = 2.6
total = t + END_CARD

def out(srct):
    for s in segs:
        if s["kind"] == "mark" and s["src"] - 1e-6 <= srct <= s["srcEnd"] + 1e-6:
            return s["s"] + srct - s["src"]
    raise ValueError(srct)

captions = [{"s": round(out(a), 3), "e": round(out(b), 3), "en": en, "ko": ko} for a, b, en, ko in LINES]
for s in segs:
    if s["kind"] == "film":
        captions.append({"s": round(s["lineS"], 3), "e": round(s["e"] - GAP / 2, 3), "en": s["en"], "ko": s["ko"], "film": True})
captions.sort(key=lambda c: c["s"])
# a film clip is visible from its pause start until TAIL after Mark resumes
clips = [{"clip": s["clip"], "src": f"day29/clips/{s['clip']}.mp4", "s": round(s["s"], 3), "e": round(s["e"] + TAIL, 3),
          "clipIn": round(s["clipIn"] - GAP, 3)} for s in segs if s["kind"] == "film"]
phrases = [{"s": round(out(a), 3), "n": n, "en": en, "ko": ko} for a, n, en, ko in PHRASES]

plan = {
    "name": f"day29-{V}", "fps": FPS, "duration": round(total, 3), "frames": int(round(total * FPS)), "day": 29,
    "subject": "day29/subject.webm", "background": "day29/great-hall.jpg", "props": "day29/props",
    "propsUntil": 3.5, "title": {"s": round(out(12.0), 3), "e": round(out(17.7), 3),
        "en": "5 Harry Potter Phrases", "sub": "to teach your child before Christmas", "ko": "크리스마스 전에 알려 줄 해리 포터 표현 5가지"},
    "segments": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()} for s in segs],
    "clips": clips, "captions": captions, "phrases": phrases, "endCard": {"s": round(t, 3), "e": round(total, 3)},
}
os.makedirs(f"{P}/versions/{V}", exist_ok=True)
json.dump(plan, open(f"{P}/versions/{V}/plan.json", "w"), ensure_ascii=False, indent=1)
print(f"{V}: {total:.2f} s, {plan['frames']} frames, {len(clips)} film pauses")
