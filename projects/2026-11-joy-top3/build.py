"""Joy TOP 3 plan for BearJoyReelV2. All times are PROGRAM seconds.
Before Joy records, captions follow script timing (edl.SCRIPT); after she records, align.py re-times them to her voice.
Run: .venv/bin/python projects/2026-11-joy-top3/build.py   -> versions/main/timeline_v2.json + reading-speed table
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from edl import DAY, END, SPEECH_END, SCRIPT, PROG  # noqa: E402

FPS = 30
TOTAL = round(SPEECH_END + END, 3)
clean = lambda s: re.sub(r"[^0-9A-Za-z가-힣]", "", s)
# one butter-yellow word per caption page
HI = ["고민이라면?", "세 권", "서점에서", "영어 그림책", "딱 하나", "한 번 더!", "바로", "I Want My Hat Back.", "계속", "Have you seen my hat?", "따라 하고",
      "빵 터져요!", "The Very Hungry Caterpillar.", "한 권에!", "손가락 쏙", "읽어", "My Dad.", "짧은 문장", "자랑해요.", "가족 이야기로", "이어가",
      "저장해 두고", "공유해"]
# pops: (start, end, small line, big line, slot, sound, punch, size)
POPS = [
    (0.00, 4.00, "📌 저장 필수 · 조이쌤 영어 그림책", "TOP 3", "hook", "impact", True, 230),
    (9.40, 12.60, "기준은 딱 하나", "\"한 번 더!\" 👆", "top", "boing", True, None),
    (15.10, 18.20, "No.1 · Jon Klassen", "🎩 I Want My Hat Back", "top", "impact", True, 92),
    (19.30, 21.40, "", "REPEAT 🔁", "top", "pop", False, None),
    (22.20, 24.10, "", "TWIST 😲", "top", "boing", False, None),
    (24.30, 27.60, "No.2 · Eric Carle", "🐛 The Very Hungry Caterpillar", "top", "impact", True, 62),
    (27.70, 30.10, "", "DAYS · NUMBERS · FOOD", "top", "pop", False, 72),
    (30.30, 33.00, "", "TOUCH 👆", "top", "pop", False, None),
    (33.20, 36.40, "No.3 · Anthony Browne", "💛 My Mum & My Dad", "top", "impact", True, 92),
    (36.50, 38.80, "", "She's… He's…", "top", "pop", False, None),
    (39.00, 41.30, "", "TALK 💬", "top", "pop", False, None),
    (41.50, 43.60, "", "📌 저장", "top", "pop", True, None),
    (43.60, 45.70, "", "💌 공유", "top", "sparkle", False, None),
]
SLOTS = {"top": {"left": 0, "right": 0, "top": 300, "rot": -3}, "hook": {"left": 0, "right": 0, "top": 620, "rot": -3}}
TAG = {"s": 4.30, "e": 8.70, "name": "Joy T", "flags": "🇰🇷", "role": "Bear & Joy 공동 저자"}
CAPTION_TOP = 1330


def pages():
    """Split each script line into caption pages and spread the line's time over them by syllable count."""
    out = []
    for s, e, text in SCRIPT:
        ps = [p.strip() for p in text.split(" / ")]
        n = [max(1, len(re.findall(r"[가-힣0-9]", p)) + 1.5 * len(re.findall(r"[A-Za-z']+", p))) for p in ps]
        t = s
        for p, k in zip(ps, n):
            d = (e - s) * k / sum(n)
            out.append([round(t, 3), round(t + d, 3), p]); t += d
    return out


def main():
    C = []
    for k, (s, e, ko) in enumerate(pages()):
        hi = next((h for h in HI if h in ko), "")
        C.append({"i": k, "s": s, "e": e, "ko": ko, "en": "", "hi": hi, "demo": False, "words": []})
    for a, b in zip(C, C[1:]):
        if 0 < b["s"] - a["e"] < 0.6:
            a["e"] = b["s"]
    ev, sfx = [], []
    add = lambda t, s, g: sfx.append({"t": round(max(0, t), 3), "sound": s, "gain": g})
    for k, (s, e, kick, text, slot, snd, punch, size) in enumerate(POPS):
        p = {"type": "pop", "s": -0.3 if s == 0 else s, "e": e, "text": text, "kicker": kick, "slot": slot, "k": k}
        if size:
            p["size"] = size
        if slot == "hook":
            p["kickerSize"] = 64
        ev.append(p)
        add(s, snd, {"pop": -9, "impact": -7}.get(snd, -11))
        if punch:
            ev.append({"type": "punch", "s": s, "e": s + 0.3, "z": 1.08, "shake": 7})
    ev.append({"type": "tag", **TAG}); add(TAG["s"], "whoosh", -12)
    for t in PROG[1:]:
        add(t - 0.08, "whoosh", -15)
    ev.append({"type": "end", "s": round(SPEECH_END - 0.1, 3), "e": TOTAL, "short": False, "share": "💌 영어 그림책 고민하는 친구에게 공유해 주세요"})
    ev.append({"type": "badge", "s": 4.0, "e": SPEECH_END - 0.1, "day": DAY, "docked": True})
    add(SPEECH_END - 0.1, "impact", -8); add(SPEECH_END + 0.05, "sparkle", -10)
    add(SPEECH_END + 1.9, "pop", -6); add(SPEECH_END + 2.8, "pop", -6); add(SPEECH_END + 2.85, "chime", -9)
    zooms = [{"t": c["s"], "z": 1.06 if k % 2 else 1.0} for k, c in enumerate(C)]
    plan = {"name": "joytop3-main", "media": "joytop3/main", "fps": FPS, "duration": TOTAL, "frames": int(math.ceil(TOTAL * FPS)),
            "speechEnd": SPEECH_END, "day": DAY, "segments": [{"src_s": 0, "src_e": TOTAL, "out_s": 0}], "captions": C, "events": ev,
            "zooms": zooms, "music": {"dropouts": [], "drops": []}, "slots": SLOTS, "tagPos": {"left": 50, "top": 1120},
            "scrim": True, "look": "original", "captionTop": CAPTION_TOP, "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/main/timeline_v2.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{TOTAL:.1f}s, {len(C)} captions, {sum(e['type'] == 'pop' for e in ev)} pops")
    for c in C:
        n = len(re.findall(r"[가-힣0-9]", c["ko"])) + 1.5 * len(re.findall(r"[A-Za-z']+", c["ko"])); d = c["e"] - c["s"]
        flag = "  <-- fast" if n / d > 6.5 else ("  <-- short" if d < 1.2 else "")
        print(f"  {c['s']:6.2f} {d:4.2f}s {n:4.1f}자 {n / d:4.1f}/s [{c['hi']}] {c['ko']}{flag}")


if __name__ == "__main__":
    main()
