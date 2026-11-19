"""DAY 35 유아교육전 홍보 릴스 (Joy, 19 Nov 2026).
Intro = Joy's own clip (raw-footage/day35/main.mov, with sound) as a cut-out sticker bottom-left over 1-second cuts of the fair.
Then Joy's voice-over (recorded later) for 5 tips, a TOP 3 teaser, follow + share cards.
Until the VO exists, each VO line gets an estimated length (5 syllables/s + pause); set VO_WAV to re-time from the real recording.
Run (repo root): .venv/bin/python projects/2026-11-day35-expo/build.py  → writes versions/main/plan.json (+ copy for Remotion)
"""
import json, math, os, re, shutil, subprocess

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
# Joy's recording (raw-footage/day35/vo.m4a, 19 Nov 2026): one take. Speech starts at 4.1 s; we use VO_IN..VO_OUT and place it
# right after the intro. Each caption line carries the time (in vo.m4a) where it starts — word onsets from Whisper on the
# trimmed audio, checked against the pauses. Caption text = her own words (she said "선착순 혜택", "베어앤조이를 팔로우하고").
VO_IN, VO_OUT, GAP = 4.02, 66.20, 0.05
# Joy (v5): no dead air between sentences. Pauses of 0.33 s or more in her recording (level below -34 dB, found by
# measuring) shrink to KEEP s; "알려드릴게요" goes straight into "선착순 혜택을 원한다면". Shorter pauses inside a sentence stay.
PAUSES = [(6.70, 7.80), (11.72, 12.38), (15.80, 16.20), (19.58, 19.94), (23.10, 24.10), (27.02, 27.42), (31.72, 32.40),
          (37.32, 38.10), (41.56, 42.12), (45.12, 45.86), (52.34, 53.02), (58.42, 59.36), (63.64, 64.30)]
KEEP = 0.20
CUTS = [(a + KEEP / 2, b - KEEP / 2) for a, b in PAUSES]  # removed spans (vo.m4a time)


def vo_map(x):
    """vo.m4a time -> time in the tightened voice track (a time inside a removed span lands on the cut)."""
    y = x - VO_IN
    for a, b in CUTS:
        if x >= b: y -= b - a
        elif x > a: y -= x - a
    return y


def make_vo(out):
    keep, t = [], VO_IN
    for a, b in CUTS:
        keep.append((t, a)); t = b
    keep.append((t, VO_OUT))
    fc = [f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={b - a - 0.02:.3f}:d=0.02[p{k}]" for k, (a, b) in enumerate(keep)]
    fc.append("".join(f"[p{k}]" for k in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1,aformat=sample_rates=48000:channel_layouts=stereo[o]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "raw-footage/day35/vo.m4a", "-filter_complex", ";".join(fc), "-map", "[o]", out], check=True)

VO = [
    ("kkul", 0, "직접 다녀온\n꿀팁 대방출 🍯", "", [(4.08, "저희가 오늘 다녀온 꿀팁\n알려드릴게요!")], [(B2, 128), (B2, 145), (B2, 152)]),
    ("tip", 1, "오전 10시 = 선착순 🎁", "무료 체험권은 사전등록자만!",
     [(7.65, "선착순 혜택을 원한다면\n오전 10시 오픈할 때 가세요!"), (12.30, "단, 무료 체험권은\n사전등록자 대상이에요")], [(B1, 218), (B1, 4), (B1, 48), (B1, 124), (B1, 8)]),
    ("tip", 2, "여유롭게? 점심 이후 🕐", "오전엔 준비 중인 부스도 있어요",
     [(16.15, "그게 목적이 아니라면\n점심 이후로도 추천드려요"), (20.03, "왜냐하면 오늘 오전에\n준비 중인 부스도 있었거든요")], [(B2, 28), (B1, 80), (B2, 120), (B2, 30)]),
    ("tip", 3, "중앙엔 커피 & 쉴 자리 ☕", "팔로우하면 기념품·가방 선물! 👜",
     [(24.03, "중앙에는 커피와 쉴 자리도\n정말 많이 있고"), (26.88, "일부 부스에는 팔로우 이벤트로\n작은 기념품과 가방도 선물로 줘요")], [(B1, 116), (B1, 113), (B1, 61), (B1, 52), (B1, 65)]),
    ("tip", 4, "짐은 A홀 물품보관함 🧳", "쇼핑백 하나 꼭 챙기기!",
     [(32.48, "무거운 짐은 A홀 근처\n물품보관함에 맡기고"), (35.62, "쇼핑백 하나\n챙기세요!")], [(B2, 189), (B1, 120), (B1, 132), (B1, 136)]),
    ("tip", 5, "영어책 행사 특가 📚", "살 책은 미리 정해 오기!",
     [(37.82, "영어책도 행사 특가로 판매하지만\n사람이 정말 많으니"), (41.53, "사고 싶은 책은 미리\n정해 오시는 걸 추천드려요")], [(B1, 125), (B1, 144), (B1, 148), (B1, 44), (B1, 152), (B1, 184)]),
    ("top3", 0, "직접 고른 교구 & 책\nTOP 3", "COMING SOON 🔜",
     [(45.75, "저희가 직접 둘러보고 고른\n추천 교구와 책 TOP 3도"), (50.23, "곧 소개할 예정이니\n기다려 주세요!")], [(B2, 129), (B2, 136), (B2, 150), (B2, 181)]),
    ("follow", 0, "@thebearandjoy", "팔로우하고 다음 영상도 기대해 주세요 💛",
     [(53.00, "아이 영어교육에\n관심 있으시다면"), (54.85, "베어앤조이를 팔로우하고\n다음 영상도 기대해 주세요!")], [(B2, 146), (B2, 165), (B2, 157)]),
    ("share", 0, "이번 주말 가는\n친구에게 공유! 📤", "",
     [(59.52, "이번 주말 방문할 친구나 부모님께\n이 영상을 공유해 주세요!"), (64.20, "그럼 내일 만나요, 안녕! 👋")], [(B2, 190), (B1, 217)]),
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
    o = lambda x: round(INTRO + GAP + vo_map(x), 3)  # vo.m4a time -> video time
    make_vo(f"{HERE}/versions/main/vo.wav"); shutil.copy(f"{HERE}/versions/main/vo.wav", f"{HERE}/../../remotion/public/day35/vo.wav")
    starts = [st for *_, lines, _ in VO for st, _ in lines]
    nxt = dict(zip(starts, starts[1:] + [VO_OUT - .1]))
    for j, (kind, n, title, sub, lines, sh) in enumerate(VO):
        s0 = INTRO if j == 0 else o(lines[0][0] - .12)  # sections change just before her first word
        e0 = o(VO[j + 1][4][0][0] - .12) if j + 1 < len(VO) else o(VO_OUT)
        for st, ln in lines:
            caps.append({"s": o(st - .05), "e": o(nxt[st] - (.3 if nxt[st] - st > 6 else .08)), "text": ln})
        secs.append({"kind": kind, "n": n, "s": s0, "e": e0, "title": title, "sub": sub})
        d = (e0 - s0) / len(sh)
        for k, (src, ss) in enumerate(sh):
            shots.append({"src": src, "ss": ss, "t": round(s0 + k * d, 3), "d": round(d, 3)})
    t = o(VO_OUT)
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
            "shots": shots, "captions": caps, "sections": secs, "voEstimated": False, "vo": "vo.wav", "i0": I0, "voIn": VO_IN, "voOut": VO_OUT, "voAt": INTRO + GAP, "sfx": sfx}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    for p in (f"{HERE}/versions/main/plan.json", f"{HERE}/../../remotion/src/day35.json"):
        json.dump(plan, open(p, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s, {len(shots)} shots, {len(caps)} captions")
    for c in caps:
        n = syl(c["text"]); dd = c["e"] - c["s"]
        print(f"  {c['s']:6.2f} {dd:4.2f}s {n / dd:4.1f}/s {c['text']!r}")


if __name__ == "__main__":
    main()
