"""Day 25 plan for BearJoyReelV2: Mark's 3 picture books at Kyobo. Korean-only captions,
English keywords as pops and behind Mark's head (owner, 6 Nov 2026).

Run: .venv/bin/python projects/2026-11-day25-kyobo/build.py
Writes versions/main/timeline_v2.json and prints the reading-speed table. All times are PROGRAM seconds
(cut.py lays the voice-over at fixed program times, and the word times come from whisper on each piece).
Korean is Claude's draft: Joy checks it before export.
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from edl import DAY, END, SPEECH_END, PIC  # noqa: E402

FPS = 30
TOTAL = round(SPEECH_END + END, 3)

# (start, end, korean, highlight word)
CAPS = [
    (0.00, 5.80, "우리 아이에게 어떤 책 추천하세요?", "어떤 책"),
    (6.00, 10.40, "여기는 서울에서 가장 유명한 서점, 교보문고", "교보문고"),
    (10.40, 16.15, "입구 앞 돌에 새겨진 글귀 👀", "글귀"),
    (16.20, 17.90, "정말 멋진 말이죠.", "멋진"),
    (17.90, 23.95, "그래서 모든 부모님께 추천하는 영어 그림책 3권!", "영어 그림책 3권!"),
    (24.00, 27.95, "첫 번째 책 Mum, Me and the Mulberry Tree", "첫 번째 책"),
    (27.95, 31.30, "잔잔하고 아름다운 이야기", "아름다운"),
    (31.30, 34.40, "천천히 읽는 잠자리 독서에 딱이고", "잠자리 독서에"),
    (34.40, 36.75, "그림 보며 함께 이야기 나눠요", "함께"),
    (36.75, 41.00, "두 번째 책 줄리아 도널드슨의 Room on the Broom", "두 번째 책"),
    (41.00, 44.50, "라임과 반복, 아이가 저절로 따라 해요", "저절로"),
    (44.50, 46.55, "그렇게 영어 리듬이 몸에 배요", "영어 리듬이"),
    (46.55, 48.60, "친절함을 배우는 이야기", "친절함을"),
    (48.60, 52.10, "세 번째 책 I Love You Through and Through", "세 번째 책"),
    (52.10, 56.80, "아이의 모든 모습을 사랑한다는 짧고 쉬운 문장", "모든 모습을"),
    (56.80, 61.15, "어린아이에게 딱! 꼭 안고 읽어주세요 🤗", "꼭 안고"),
    (61.20, 65.30, "그리고 깜짝 보너스! 곧 나와요", "깜짝 보너스!"),
    (65.30, 68.60, "저희 책 Bear & Joy 1권", "Bear & Joy"),
    (68.60, 70.90, "곰이 기쁨을 찾은 이야기 🐻🦋", "기쁨을"),
    (70.95, 74.90, "🐻 댓글 또는 DM으로 예약하세요", "예약하세요"),
    (74.90, 78.06, "한국에서 가장 먼저 만나보세요!", "가장 먼저"),
]

# Key-point pops: (start, end, small line, big line, slot, sound, punch?)
POPS = [
    (11.80, 16.10, "교보문고 앞 ✍️", "사람은 책을 만들고", "q1", "pop", False),
    (13.70, 16.10, "", "책은 사람을 만든다", "q2", "sparkle", False),
    (18.10, 20.90, "부모님 추천 📚", "TOP 3", "top", "pop", True),
    (21.00, 23.90, "", "📌 저장 필수!", "top", "boing", False),
    (24.12, 27.90, "추천 No.1", "📗 BEDTIME", "top", "impact", True),
    (28.10, 30.90, "", "GENTLE 🍃", "top", "pop", False),
    (32.90, 34.40, "", "SLOW & COZY 🌙", "top", "pop", False),
    (34.50, 36.60, "", "TOGETHER 💬", "top", "pop", False),
    (36.84, 40.90, "추천 No.2", "🧹 RHYME", "top", "impact", True),
    (42.20, 43.90, "", "REPEAT 🔁", "top", "pop", False),
    (44.60, 46.50, "", "RHYTHM 🥁", "top", "pop", False),
    (47.25, 48.55, "", "KINDNESS 💛", "top", "pop", False),
    (48.68, 52.00, "추천 No.3", "💛 LOVE", "top", "impact", True),
    (52.80, 54.90, "", "SIMPLE ✨", "top", "pop", False),
    (59.40, 61.10, "", "CUDDLE 🤗", "top", "boing", False),
    (61.37, 63.60, "깜짝", "🎁 BONUS", "mid", "boing", True),
    (63.60, 65.30, "곧 출간", "COMING SOON 🎉", "mid", "pop", False),
    (71.00, 74.90, "댓글 = 예약 ✅", "🐻 BEAR", "ctop", "boing", True),
    (75.50, 78.00, "한국에서 가장 먼저", "FIRST IN KOREA 🇰🇷", "ctop", "sparkle", False),
]
SLOTS = {"top": {"left": 0, "right": 0, "top": 300, "rot": -3}, "mid": {"left": 0, "right": 0, "top": 700, "rot": -2},
         "q1": {"left": 0, "right": 0, "top": 500, "rot": -2}, "q2": {"left": 0, "right": 0, "top": 690, "rot": 2},
         "ctop": {"left": 0, "right": 0, "top": 150, "rot": -2}}
# English keyword behind Mark's head during the hook (matte covers program 0-6.2 s)
BEHIND = [{"kicker": "영국인 선생님이 고른 영어 그림책", "ko": "TOP 3", "s": 0.25, "e": 5.70, "size": 300, "top": 640}]
TAG = {"s": 8.30, "e": 11.70, "name": "Mark", "flags": "🇬🇧", "role": "영국인 선생님 · Bear & Joy 작가"}
COVER = {"s": 65.40, "e": SPEECH_END, "img": "brand/book1-cover.png"}
CAPTION_TOP = 1330


def main():
    clean = lambda s: re.sub(r"[^0-9A-Za-z가-힣]", "", s)
    C = [{"i": k, "s": s, "e": e, "ko": ko, "en": "", "hi": hi, "demo": False, "words": []} for k, (s, e, ko, hi) in enumerate(CAPS)]
    ev, sfx = [], []
    add = lambda t, s, g: sfx.append({"t": round(max(0, t), 3), "sound": s, "gain": g})
    for k, b in enumerate(BEHIND):
        ev.append({"type": "behind", "ko": b["ko"], "en": b["kicker"], "size": b["size"], "top": b["top"], "s": b["s"], "e": b["e"], "k": k})
        add(b["s"] - 0.15, "whoosh", -9); add(b["s"], "impact", -7); add(b["s"] + 0.05, "sparkle", -13)
    for k, (s, e, kick, text, slot, snd, punch) in enumerate(POPS):
        ev.append({"type": "pop", "s": s, "e": e, "text": text, "kicker": kick, "slot": slot, "k": k})
        add(s, snd, {"pop": -9, "impact": -8}.get(snd, -11))
        if punch:
            ev.append({"type": "punch", "s": s, "e": s + 0.3, "z": 1.08, "shake": 7})
    ev.append({"type": "tag", **TAG}); add(TAG["s"], "whoosh", -12)
    ev.append({"type": "cover", **COVER})
    add(COVER["s"] - 0.2, "whoosh", -8); add(COVER["s"], "impact", -6); add(COVER["s"] + 0.1, "sparkle", -9); add(COVER["s"] + 0.5, "chime", -9)
    ev.append({"type": "punch", "s": COVER["s"], "e": COVER["s"] + 0.35, "z": 1.06, "shake": 6})
    art_s = round(sum(((e or 0) - s) * o.get("slow", 1) for c, s, e, o in PIC if c != "ART"), 3)
    ev.append({"type": "push", "s": art_s, "e": TOTAL, "from": 1.0, "to": 1.1})
    # a whoosh on every picture cut
    t = 0
    for c, s, e, o in PIC[:-1]:
        t += (e - s) * o.get("slow", 1); add(t - 0.08, "whoosh", -16)
    ev.append({"type": "end", "s": round(SPEECH_END - 0.1, 3), "e": TOTAL, "short": False, "share": "🐻 댓글 남기고 Book 1 예약하기"})
    ev.append({"type": "badge", "s": 0.0, "e": art_s, "day": DAY})
    add(SPEECH_END - 0.1, "impact", -8); add(SPEECH_END + 0.05, "sparkle", -10)
    add(SPEECH_END + 1.9, "pop", -6); add(SPEECH_END + 2.8, "pop", -6); add(SPEECH_END + 2.85, "chime", -9)
    zooms = [{"t": c["s"], "z": 1.06 if k % 2 else 1.0} for k, c in enumerate(C)]
    plan = {"name": "day25-main", "media": "day25/main", "fps": FPS, "duration": TOTAL, "frames": int(math.ceil(TOTAL * FPS)),
            "speechEnd": SPEECH_END, "day": DAY, "segments": [{"src_s": 0, "src_e": TOTAL, "out_s": 0}], "captions": C, "events": ev,
            "zooms": zooms, "music": {"dropouts": [], "drops": []}, "slots": SLOTS, "tagPos": {"left": 50, "top": 330},
            "scrim": True, "captionTop": CAPTION_TOP, "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/main/timeline_v2.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{TOTAL:.1f}s, {len(C)} captions, {sum(e['type'] == 'pop' for e in ev)} pops, {len(sfx)} sfx")
    for c in C:
        n = len(clean(c["ko"])); d = c["e"] - c["s"]
        flag = "  <-- fast" if n / d > 6 else ("  <-- short" if d < 1.2 else "")
        print(f"  {c['s']:6.2f} {d:4.2f}s {n:2d}자 {n / d:4.1f}/s {c['ko']}{flag}")


if __name__ == "__main__":
    main()
