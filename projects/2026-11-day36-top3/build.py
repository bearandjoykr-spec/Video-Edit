"""DAY 36 유아교육전 TOP 3 (Joy, 20 Nov 2026) — countdown No.3 → No.1 with Joy and Mark up front, premium look, fast cuts on the beat.
Sources: raw-footage/day35/bg1.mov, bg2.mov (Joy's fair walk-throughs) and raw-footage/day36/IMG_49xx.MOV (links to ~/Downloads).
bg2 198.5–217.5 s is the SPOMARU floor ball game, filmed upside down → rot 180.
Joy records the voice-over after she sees the cut (like DAY 35): until then each VO line gets an estimated length, and the
sections are built around it. Original sound bites (Joy and Mark at the fair) play in sync with their picture.
Run (repo root): .venv/bin/python projects/2026-11-day36-top3/build.py → versions/main/plan.json (+ remotion/src/day36.json)
"""
import json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, BEAT = 30, 0.5          # music: "Fashion Lifestyle" (sub_clair), 120 BPM; started at its first beat (0.557 s)
B1, B2 = "raw-footage/day35/bg1.mov", "raw-footage/day35/bg2.mov"
D = lambda n: f"raw-footage/day36/IMG_49{n}.MOV"

# Sections. kind: hook / bite (original sound in sync) / rank (the No. reveal) / vo / card / end.
# shots: (src, start, beats[, extra]) — each shot lasts N beats; a bite's picture is the bite itself.
# v2 (Joy agreed, 20 Nov 2026): open on the most surprising picture (the AI floor ball game) with a question every parent feels,
# then Mark's "TOP 3!"; the ball game becomes No.1 (the climax), the poster No.2 with a comment call-to-action.
SECTIONS = [
    # 0 QUESTION HOOK: Mark kicking the bouncing ball, "NICE" on the floor
    {"kind": "q", "shot": (B2, 211.0, "rot"), "beats": 4, "title": "영어, 아직도\n책상에서 시키세요?"},
    # 1 Mark to camera, "TOP 3!" (his own voice), the fair line over it
    {"kind": "hook", "bite": (B2, 22.95, 24.85), "title": "유아교육전 다 돌고\n딱 3개만 골랐어요", "kicker": "COEX 유아교육전", "big": "TOP 3"},
    # 2 Joy: "교구와 그림책 TOP 3, 함께 소개해드릴게요" (her voice), quick cutaways of the three picks under it
    {"kind": "bite", "bite": (B2, 10.62, 14.62), "who": "Joy", "cap": "교구와 그림책 TOP 3,\n함께 소개해드릴게요",
     "inserts": [(1.4, (D(57), 1.0, None)), (1.9, (B2, 300.5, None)), (2.4, (B2, 206.0, "rot"))]},
    # 3 No.3 reveal — books
    {"kind": "rank", "n": 3, "title": "영어책, 이렇게 고르세요", "shot": (D(57), 2.0)},
    {"kind": "vo", "n": 3, "lines": ["사람이 제일 많았던 곳,\n바로 영어책 코너!",
                                    "소리책, 팝업북도 좋지만\n고를 땐 꼭 펼쳐 보세요",
                                    "바로 말해 줄 문장이 있는 책이\n제일 오래 쓰여요"],
     "shots": [(B1, 56, 2), (D(57), 3.0, 2), (D(63), 1.0, 2), (D(64), 0.5, 2), (B1, 124, 2), (D(61), 1.0, 2), (D(75), 2.0, 2), (D(62), 1.0, 2),
               (D(67), 1.0, 2), (B1, 148, 2), (D(66), 0.5, 2), (B1, 44, 2)],
     "card": {"at": 2, "title": "3초 테스트 ✓", "body": "펼쳤을 때 오늘 바로 말해 줄 문장이 3개 있으면 합격",
              "en": ["Where's the cat?", "Let's go outside!", "Night night!"]}},
    # 5 No.2 reveal — the sound poster
    {"kind": "rank", "n": 2, "title": "소리 나는 벽 포스터", "shot": (B2, 284.0)},
    {"kind": "vo", "n": 2, "lines": ["직접 누르면 소리가 나서\n새 단어를 스스로 익혀요",
                                    "집이나 어린이집\n환경 구성에 딱이에요"],
     "shots": [(B2, 282.0, 2), (B2, 286.0, 2), (B2, 289.0, 2), (B2, 293.0, 2), (B2, 297.5, 2), (B2, 301.0, 2), (B2, 305.0, 2), (B2, 309.0, 2)],
     "info": {"name": "벽에 붙이는 사운드 포스터", "lines": ["동물 · 알파벳 · 한글", "누르면 단어와 소리가 나와요"]},
     "play": ("Where's the tiger? Press it!", "호랑이 어디 있지? 눌러 봐!")},
    # 7 Mark: "Brilliant." (his voice, poster picture) + comment call-to-action
    {"kind": "bite", "bite": (B2, 316.85, 317.65), "who": "Mark", "cap": "Brilliant! 👏", "cta": "제품 정보 궁금하면\n댓글에 '포스터' 💬"},
    {"kind": "cta", "beats": 3, "shot": (B2, 312.0), "cta": "제품 정보 궁금하면\n댓글에 '포스터' 💬"},
    # 9 No.1 reveal — the AI floor ball game (the climax)
    {"kind": "rank", "n": 1, "title": "몸으로 하는 공 게임", "shot": (B2, 203.0, "rot")},
    {"kind": "vo", "n": 1, "lines": ["아이들은 앉아서 공부할 때보다\n놀 때 훨씬 빨리 배워요",
                                    "놀면서 이렇게 말해 주세요"],
     "shots": [(B2, 198.6, 2, "rot"), (B2, 200.6, 2, "rot"), (B2, 203.5, 2, "rot"), (B2, 205.5, 2, "rot"), (B2, 207.5, 2, "rot"), (B2, 209.0, 2, "rot")],
     "info": {"name": "스포마루 (SPOMARU)", "lines": ["AI 인터랙티브 바닥 놀이", "바닥에 튕기는 공을 발로 '뻥!'", "원하는 활동을 문장으로 쓰면 AI가 게임으로"]}},
    # 11 phrase cards (Joy says them in the VO), Mark kicking on the beat
    {"kind": "phrases", "n": 1, "phrases": [("Kick the ball!", "공을 차!"), ("Throw it to me!", "나한테 던져!"), ("Catch!", "잡아!"), ("Your turn!", "네 차례야!")],
     "shots": [(B2, 213.0, 2, "rot"), (B2, 215.6, 2, "rot"), (B2, 207.0, 2, "rot"), (B2, 201.0, 2, "rot")]},
    # 12 Mark on why it works (his voice; picture = the game)
    {"kind": "bite", "bite": (B2, 251.95, 255.75), "who": "Mark", "cap": "They're not just on their fingers,\nthey're actually jumping up and down!",
     "ko": "손가락만 쓰는 게 아니라, 온몸으로 뛰면서 놀아요!", "picture": (B2, 204.5, "rot")},
    # 13 end: save + share + follow (Joy's last VO line)
    {"kind": "end", "lines": ["저장해 두고\n아이랑 꼭 해 보세요!"], "shot": (B2, 129.0)},
]
END_TAIL = 1.5


def syl(t):
    return len(re.findall(r"[가-힣0-9]", t)) + 1.5 * len(re.findall(r"[A-Za-z']+", t))


def q(x):  # snap to the beat grid
    return round(round(x / BEAT) * BEAT, 3)


def main():
    t, secs, shots, caps, bites, sfx = 0.0, [], [], [], [], []

    def shot(src, ss, d, rot=None, tag=None):
        s = {"src": src, "ss": ss, "t": round(t_shot[0], 3), "d": round(d, 3)}
        if rot: s["rot"] = 180
        shots.append(s); t_shot[0] += d

    t_shot = [0.0]
    for k, S in enumerate(SECTIONS):
        s0 = t
        kind = S["kind"]
        if kind in ("hook", "bite"):
            src, a, b = S["bite"]; d = b - a
            pic = S.get("picture")
            if pic:
                shot(pic[0], pic[1], d, pic[2] if len(pic) > 2 else None)
            elif S.get("inserts"):
                last = 0.0
                for at, (isrc, iss, irot) in S["inserts"]:
                    shot(src, a + last, at - last); shot(isrc, iss, .5, irot == "rot"); last = at + .5
                shot(src, a + last, d - last)
            else:
                shot(src, a, d)
            bites.append({"src": src, "ss": a, "t": round(s0, 3), "d": round(d, 3)})
            if S.get("cap"):
                caps.append({"s": round(s0 + .05, 3), "e": round(s0 + d, 3), "text": S["cap"], "ko": S.get("ko", ""), "who": S.get("who", "")})
            t += d
        elif kind in ("q", "cta"):
            d = S["beats"] * BEAT; sh = S["shot"]
            shot(sh[0], sh[1], d, sh[2] if len(sh) > 2 else None)
            if kind == "q":
                sfx.append({"t": 0.0, "sound": "impact", "gain": -12})
            t += d
        elif kind == "rank":
            d = 3 * BEAT; sh = S["shot"]
            shot(sh[0], sh[1], d, sh[2] if len(sh) > 2 else None)
            sfx.append({"t": round(s0, 3), "sound": "whoosh", "gain": -12}); sfx.append({"t": round(s0 + .1, 3), "sound": "impact", "gain": -13})
            t += d
        elif kind in ("vo", "end"):
            for ln in S["lines"]:  # estimated: 5.3 syllables/s + a breath
                dd = syl(ln) / 5.3 + .25
                caps.append({"s": round(t, 3), "e": round(t + dd, 3), "text": ln, "vo": True}); t += dd
            if kind == "end":
                t += END_TAIL
            t = max(q(t), s0 + BEAT)
            if kind == "end":
                shot(S["shot"][0], S["shot"][1], t - s0, S["shot"][2] if len(S["shot"]) > 2 else None)
            else:
                # fill the section with the listed shots (each N beats), looping if the VO runs longer
                i, sh = 0, S["shots"]
                while t_shot[0] < t - 1e-6:
                    x = sh[i % len(sh)]; d = min(x[2] * BEAT, t - t_shot[0])
                    shot(x[0], x[1] + (i // len(sh)) * 1.0, d, x[3] if len(x) > 3 else None); i += 1
        elif kind == "phrases":
            per = 3 * BEAT
            for j, (en, ko) in enumerate(S["phrases"]):
                caps.append({"s": round(t + j * per, 3), "e": round(t + (j + 1) * per, 3), "text": en, "ko": ko, "phrase": True})
                sfx.append({"t": round(t + j * per, 3), "sound": "pop", "gain": -14})
            for x in S["shots"]:
                shot(x[0], x[1], per, x[3] if len(x) > 3 else None)
            t += per * len(S["phrases"])
        sec = {k2: v for k2, v in S.items() if k2 not in ("shots", "bite", "inserts", "picture", "shot")}
        sec.update({"s": round(s0, 3), "e": round(t, 3)})
        secs.append(sec)
    total = round(t, 3)
    plan = {"fps": FPS, "day": 36, "media": "day36", "duration": total, "frames": int(math.ceil(total * FPS)), "beat": BEAT,
            "shots": shots, "captions": caps, "sections": secs, "bites": bites, "sfx": sfx, "voEstimated": True}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    for p in (f"{HERE}/versions/main/plan.json", f"{HERE}/../../remotion/src/day36.json"):
        json.dump(plan, open(p, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s, {len(shots)} shots, {len(caps)} captions")
    for s in secs:
        print(f"  {s['s']:6.2f}-{s['e']:6.2f} {s['kind']:8s} {s.get('n', '')}")


if __name__ == "__main__":
    main()
