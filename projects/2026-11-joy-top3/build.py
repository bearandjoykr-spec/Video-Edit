"""Joy TOP 3 v2 plan for remotion/src/JoyTop3Reel.tsx. All times are PROGRAM seconds.
Captions follow the script timing (edl.SCRIPT) until Joy records; then they are re-timed to her voice.
Run: .venv/bin/python projects/2026-11-joy-top3/build.py   -> versions/main/timeline.json + reading-speed table
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from edl import DAY, END, SPEECH_END, SCRIPT, PROG, PIC  # noqa: E402

FPS = 30
TOTAL = round(SPEECH_END + END, 3)
syl = lambda p: len(re.findall(r"[가-힣0-9]", p)) + 1.5 * len(re.findall(r"[A-Za-z']+", p))
HI = ["한 번 더!", "딱 3권!", "직접", "3위부터", "My Mum, My Dad.", "짧은 문장", "자랑하는", "우리 엄마는?", "물어봐", "Caterpillar.",
      "요일, 숫자, 음식", "한 권에", "손가락을 쏙", "읽어", "1위!", "계속", "Have you seen my hat?", "따라 하는데요,", "직접 확인해",
      "저장해 두고", "친구에게", "보내"]
# Books, in countdown order. Info cards are the save-worthy part (age, key sentence, how to read it).
BOOKS = {
    3: {"title": "My Mum · My Dad", "author": "Anthony Browne", "cover": "mumdad.jpg",
        "info": [("👶", "추천 나이", "3세부터"), ("🗣", "핵심 문장", "She's… / He's…"), ("💡", "읽는 팁", "다 읽고 \"우리 엄마는?\" 물어보기")]},
    2: {"title": "The Very Hungry Caterpillar", "author": "Eric Carle", "cover": "caterpillar.jpg",
        "info": [("👶", "추천 나이", "1세부터 (보드북)"), ("🗣", "핵심 문장", "On Monday he ate…"), ("💡", "읽는 팁", "책 구멍에 손가락 쏙!")]},
    1: {"title": "I Want My Hat Back", "author": "Jon Klassen", "cover": "hat.jpg",
        "info": [("👶", "추천 나이", "4세부터"), ("🗣", "핵심 문장", "Have you seen my hat?"), ("💡", "읽는 팁", "동물 역할 나눠 읽기")]},
}


def pages():
    out = []
    for s, e, text in SCRIPT:
        ps = [p.strip() for p in text.split(" / ")]
        n = [max(1, syl(p)) for p in ps]
        t = s
        for p, k in zip(ps, n):
            d = (e - s) * k / sum(n)
            out.append([round(t, 3), round(t + d, 3), p]); t += d
    return out


def main():
    C = []
    for k, (s, e, ko) in enumerate(pages()):
        C.append({"s": s, "e": e, "ko": ko, "hi": next((h for h in HI if h in ko), "")})
    for a, b in zip(C, C[1:]):
        if 0 < b["s"] - a["e"] < 0.6:
            a["e"] = b["s"]
    # scenes from the picture list (consecutive shots of one scene merge)
    scenes = []
    for (clip, s, e, name), t in zip(PIC, PROG):
        if scenes and scenes[-1]["name"] == name:
            scenes[-1]["e"] = round(t + e - s, 3)
        else:
            scenes.append({"name": name, "s": t, "e": round(t + e - s, 3)})
    scenes[-1]["e"] = SPEECH_END
    sc = {x["name"]: x for x in scenes}
    sfx = []
    add = lambda t, s, g: sfx.append({"t": round(max(0, t), 3), "sound": s, "gain": g})
    for k in range(3):  # hook: three mystery books thud in
        add(0.25 + 0.4 * k, "impact", -9 - k)
    add(1.6, "sparkle", -12)
    for t in PROG[1:]:
        add(t - 0.08, "whoosh", -15)
    for r in (3, 2, 1):
        rv = sc[f"reveal{r}"]
        add(rv["s"], "boing", -10); add(rv["s"] + 0.5, "impact", -6); add(rv["s"] + 0.55, "sparkle", -10)
        bk = sc[f"book{r}"]
        add(bk["e"] - 3.6, "pop", -9)  # info card
    add(sc["summary"]["s"] + 0.1, "chime", -9)
    add(SPEECH_END, "impact", -8); add(SPEECH_END + 0.05, "sparkle", -10)
    add(SPEECH_END + 1.9, "pop", -6); add(SPEECH_END + 2.8, "pop", -6); add(SPEECH_END + 2.85, "chime", -9)
    plan = {"fps": FPS, "duration": TOTAL, "frames": int(math.ceil(TOTAL * FPS)), "speechEnd": SPEECH_END, "day": DAY,
            "media": "joytop3/main", "scenes": scenes, "captions": C, "books": {str(k): v for k, v in BOOKS.items()},
            "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/main/timeline.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{TOTAL:.1f}s, {len(C)} captions, scenes: " + ", ".join(f"{x['name']} {x['s']:.1f}-{x['e']:.1f}" for x in scenes))
    for c in C:
        n = syl(c["ko"]); d = c["e"] - c["s"]
        flag = "  <-- fast" if n / d > 6.5 else ("  <-- short" if d < 1.2 else "")
        print(f"  {c['s']:6.2f} {d:4.2f}s {n:4.1f}자 {n / d:4.1f}/s [{c['hi']}] {c['ko']}{flag}")


if __name__ == "__main__":
    main()
