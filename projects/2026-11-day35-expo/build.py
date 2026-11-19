"""DAY 35 유아교육전 홍보 릴스 (Joy, 19 Nov 2026).
Intro = Joy's own clip (raw-footage/day35/main.mov, with sound) as a cut-out sticker bottom-left over 1-second cuts of the fair.
Then Joy's voice-over (recorded later) for 5 tips, a TOP 3 teaser, follow + share cards.
Until the VO exists, each VO line gets an estimated length (5 syllables/s + pause); set VO_WAV to re-time from the real recording.
Run (repo root): .venv/bin/python projects/2026-11-day35-expo/build.py  → writes versions/main/plan.json (+ copy for Remotion)
"""
import json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
I0 = 1.85      # Joy (DAY 35 v2): only the part where she speaks — main.mov 1.85–14.35 s (speech 1.95–14.1 by level)
INTRO = 12.5
B1, B2 = "raw-footage/day35/bg1.mov", "raw-footage/day35/bg2.mov"

# Joy's own words in main.mov (Whisper, checked by ear later): two-line captions
# sentence starts/ends from the audio level (pauses at 4.5, 8.4, 12.6 s in main.mov), minus I0
INTRO_CAPS = [(0.05, 2.65, "아이 키우는 부모님들,\n주목하세요! 📢"),
              (2.65, 6.55, "오늘부터 일요일까지 코엑스에서\n유아교육전이 시작됩니다!"),
              (6.55, 10.75, "다양한 프로그램과 그림책,\n그리고 체험까지 직접 만나볼 수 있어요"),
              (10.75, 12.5, "저희와 함께\n가보실까요? 👣")]
# 1-second cuts behind the intro (src, start)
# Joy: this footage makes TWO videos. This one is the overview (what's at the fair); product demos (Cublo, animal piano
# poster, the bears' school, blue blocks, gear wall, drawing board, magnetic tiles, wooden puzzles) are kept for the TOP 3 video.
# Joy (v3): no clearly visible stranger faces — staff by the green mascot, a child, the woman at 23 s and phone-users swapped out.
# (times checked frame by frame: the 4-second contact sheets drift on this variable-frame-rate footage)
INTRO_SHOTS = [(B1, 0), (B1, 216), (B1, 56), (B1, 18), (B1, 36), (B1, 76), (B1, 28), (B2, 69), (B2, 184),
               (B1, 84), (B2, 52), (B2, 36), (B1, 64)]

# what each intro shot shows (a stamp on the right, so viewers see everything the fair has)
TAGS = ["📍 코엑스 A홀", "🗓️ 11.19 ~ 11.22", "📚 영어원서 최대 90%", "📖 그림책 가득", "📚 원서 코너", "🐴 조랑말 체험", "🧸 교구 & 장난감",
        "🦖 공룡 존", "🐥 캐릭터와 인사", "🏷️ 브랜드 대전", "🌸 포토존", "🎤 부모 세미나", "🛍️ 쇼핑 천국"]

# VO sections: (kind, n, card title, card sub, caption lines, shots)
VO = [
    ("kkul", 0, "직접 다녀온\n꿀팁 대방출 🍯", "", ["제가 오늘 다녀온 꿀팁\n알려드릴게요!"], [(B2, 128), (B2, 145), (B2, 152)]),
    ("tip", 1, "오전 10시 = 선착순 🎁", "무료 체험권은 사전등록자만!",
     ["선착순 혜택을 원한다면\n오전 10시에 가세요!", "단, 무료 체험권은\n사전등록자 대상이에요"], [(B1, 218), (B1, 4), (B1, 48), (B1, 124), (B1, 8)]),
    ("tip", 2, "여유롭게? 점심 이후 🕐", "오전엔 준비 중인 부스도 있어요",
     ["그게 목적이 아니라면\n점심 이후도 추천해요", "오늘 오전엔\n준비 중인 부스도 있었거든요"], [(B2, 28), (B1, 80), (B2, 120), (B2, 30)]),
    ("tip", 3, "중앙엔 커피 & 쉴 자리 ☕", "팔로우 이벤트로 큰 가방도! 👜",
     ["중앙엔 커피와\n쉴 자리도 있고", "일부 부스에서는 팔로우 이벤트로\n큰 가방도 줘요"], [(B1, 116), (B1, 113), (B1, 61), (B1, 52), (B1, 65)]),
    ("tip", 4, "짐은 A홀 물품보관함 🧳", "쇼핑백 하나 꼭 챙기기!",
     ["무거운 짐은 A홀 근처\n물품보관함에 맡기고", "쇼핑백 하나\n챙기세요!"], [(B2, 189), (B1, 120), (B1, 132), (B1, 136)]),
    ("tip", 5, "영어책 행사 특가 📚", "살 책은 미리 정해 오기!",
     ["영어책도 행사 특가로 판매하지만\n사람이 많으니", "사고 싶은 책은\n미리 정해 오세요!"], [(B1, 125), (B1, 144), (B1, 148), (B1, 44), (B1, 152), (B1, 184)]),
    ("top3", 0, "직접 고른 교구 & 책\nTOP 3", "COMING SOON 🔜",
     ["저희가 직접 둘러보고 고른\n추천 교구와 책 TOP 3도", "곧 소개할 예정이에요!"], [(B2, 129), (B2, 136), (B2, 150), (B2, 181)]),
    ("follow", 0, "@thebearandjoy", "팔로우하고 다음 영상도 기대해 주세요 💛",
     ["아이 영어교육에 관심 있으시다면", "@thebearandjoy 팔로우하고\n다음 영상도 기대해 주세요!"], [(B2, 146), (B2, 165), (B2, 157)]),
    ("share", 0, "이번 주말 가는\n친구에게 공유! 📤", "", ["이번 주말 방문할\n부모님께 공유해 주세요!"], [(B2, 190), (B1, 217)]),
]
END = 1.6


def syl(t):
    return len(re.findall(r"[가-힣0-9]", t)) + 1.5 * len(re.findall(r"[A-Za-z]+", t))


def main():
    shots, caps, secs = [], [], []
    # intro: equal ~1 s cuts, the last one runs to the end of Joy's clip
    d = INTRO / len(INTRO_SHOTS)
    for k, (src, s) in enumerate(INTRO_SHOTS):
        shots.append({"src": src, "ss": s, "t": round(k * d, 3), "d": round(d, 3), "tag": TAGS[k]})
    caps += [{"s": a, "e": b, "text": x} for a, b, x in INTRO_CAPS]
    secs.append({"kind": "intro", "n": 0, "s": 0, "e": INTRO, "title": "유아교육전\n시작됐다! 🎉", "sub": "📍 코엑스 A홀 · 11.19(목) ~ 11.22(일)"})
    t = INTRO + 0.15
    for kind, n, title, sub, lines, sh in VO:
        s0 = t
        for ln in lines:  # estimated: 5 syllables/s + a breath
            dur = syl(ln) / 5.0 + 0.35
            caps.append({"s": round(t, 3), "e": round(t + dur, 3), "text": ln})
            t += dur
        t += 0.25
        secs.append({"kind": kind, "n": n, "s": round(s0, 3), "e": round(t, 3), "title": title, "sub": sub})
        d = (t - s0) / len(sh)
        for k, (src, s) in enumerate(sh):
            shots.append({"src": src, "ss": s, "t": round(s0 + k * d, 3), "d": round(d, 3)})
    secs[-1]["e"] = round(t + END, 3); shots[-1]["d"] = round(t + END - shots[-1]["t"], 3)
    total = round(t + END, 3)
    for a, b in zip(shots, shots[1:]):  # no gaps between shots (first VO shot starts at INTRO)
        a["d"] = round(b["t"] - a["t"], 3)
    sfx = []
    for x in secs[1:]:
        sfx.append({"t": round(x["s"], 3), "sound": "whoosh", "gain": -16})
        sfx.append({"t": round(x["s"] + .1, 3), "sound": "pop", "gain": -12})
    sfx.append({"t": round(secs[0]["s"] + .1, 3), "sound": "sparkle", "gain": -14})
    plan = {"fps": FPS, "day": 35, "media": "day35", "duration": total, "frames": int(math.ceil(total * FPS)), "intro": INTRO,
            "shots": shots, "captions": caps, "sections": secs, "voEstimated": True, "i0": I0, "sfx": sfx}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    for p in (f"{HERE}/versions/main/plan.json", f"{HERE}/../../remotion/src/day35.json"):
        json.dump(plan, open(p, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s, {len(shots)} shots, {len(caps)} captions")
    for c in caps:
        n = syl(c["text"]); dd = c["e"] - c["s"]
        print(f"  {c['s']:6.2f} {dd:4.2f}s {n / dd:4.1f}/s {c['text']!r}")


if __name__ == "__main__":
    main()
