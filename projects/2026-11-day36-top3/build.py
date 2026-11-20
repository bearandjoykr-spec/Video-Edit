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
# v3 (Joy, 20 Nov): no question hook (this video is the fair's picks); Joy and Mark between the shots in every pick;
# Blue Rabbit Sound Chart info from Joy's photos of the stand.
# v2 (Joy agreed, 20 Nov 2026): open on the most surprising picture (the AI floor ball game) with a question every parent feels,
# then Mark's "TOP 3!"; the ball game becomes No.1 (the climax), the poster No.2 with a comment call-to-action.
SECTIONS = [
    # 1 Mark to camera, "TOP 3!" (his own voice), the fair line over it
    {"kind": "hook", "bite": (B2, 22.95, 24.85), "title": "유아교육전 다 돌고\n딱 3개만 골랐어요", "kicker": "COEX 유아교육전", "big": "TOP 3"},
    # 2 Joy: "교구와 그림책 TOP 3, 함께 소개해드릴게요" (her voice), quick cutaways of the three picks under it
    {"kind": "bite", "bite": (B2, 10.62, 14.62), "who": "Joy", "cap": "교구와 그림책 TOP 3,\n함께 소개해드릴게요",
     "inserts": [(1.4, (D(57), 1.0, None)), (1.9, (B2, 300.5, None)), (2.4, (B2, 206.0, "rot"))]},
    # 3 No.3 reveal — books
    {"kind": "rank", "n": 3, "title": "영어책, 이렇게 고르세요", "shot": (D(57), 2.0)},
    {"kind": "vo", "n": 3, "pieces": [(1.20, 3.85, "사람이 제일 많았던 곳,\n바로 영어책 코너!"),
                                     (4.10, 7.62, "소리책, 팝업북도 좋지만\n고를 땐 꼭 펼쳐 보세요"),
                                     (8.10, 11.18, "바로 말해 줄 문장이 있는 책이\n제일 오래 쓰여요"),
                                     (11.60, 14.68, None, "Mark")],   # Mark reads the 3-second-test lines (they are on the card)
     "shots": [(B1, 56, 2), (B2, 180.3, 2), (D(63), 1.0, 2), (D(64), 0.5, 2), (B2, 4.3, 2), (B1, 124, 2), (D(61), 1.0, 2), (B2, 136.5, 2),
               (D(75), 2.0, 2), (D(62), 1.0, 2), (B2, 7.3, 2), (B1, 148, 2), (D(67), 1.0, 2)],
     "card": {"at": 2, "title": "3초 테스트 ✓", "body": "펼쳤을 때 오늘 바로 말해 줄 문장이 3개 있으면 합격",
              "en": ["Where's the cat?", "Let's go outside!", "Night night!"]}},
    # 5 No.2 reveal — the sound poster
    {"kind": "rank", "n": 2, "title": "소리 나는 벽 포스터", "shot": (B2, 284.0)},
    {"kind": "vo", "n": 2, "pieces": [(15.12, 18.32, "직접 누르면 소리가 나서\n새 단어를 스스로 익혀요"),
                                     (18.42, 20.42, None, "Mark", "play"),   # "Where's the tiger? Press it!" (the play card)
                                     (20.82, 24.22, "집이나 어린이집, 유치원\n환경 구성에도 딱이에요")],
     "shots": [(B2, 282.0, 2), (B2, 286.0, 2), (B2, 165.0, 2), (B2, 289.0, 2), (B2, 293.0, 2), (B2, 58.3, 2), (B2, 297.5, 2), (B2, 301.0, 2),
               (B2, 16.2, 2), (B2, 305.0, 2)],
     "info": {"name": "블루래빗 사운드 차트", "lines": ["누르면 우리말·영어 단어와 소리", "퀴즈 · 동요 5곡 · 피아노·실로폰 연주", "현장가 1장 17,500원 (4장 64,000원)"]},
     "play": ("Where's the tiger? Press it!", "호랑이 어디 있지? 눌러 봐!")},
    # 7 Mark: "Brilliant." (his voice, poster picture) + comment call-to-action
    {"kind": "bite", "bite": (B2, 316.85, 317.65), "who": "Mark", "cap": "Brilliant! 👏", "cta": "더 궁금한 점은\n댓글에 '포스터' 💬"},
    {"kind": "cta", "beats": 3, "shot": (B2, 312.0), "cta": "더 궁금한 점은\n댓글에 '포스터' 💬"},
    # 9 No.1 reveal — the AI floor ball game (the climax)
    {"kind": "rank", "n": 1, "title": "몸으로 하는 공 게임", "shot": (B2, 203.0, "rot")},
    {"kind": "vo", "n": 1, "pieces": [(24.56, 27.94, "아이들은 앉아서 공부할 때보다\n놀 때 훨씬 빨리 배워요"),
                                     (28.20, 29.88, "놀면서 이렇게 말해 주세요")],
     "shots": [(B2, 198.6, 2, "rot"), (B2, 200.6, 2, "rot"), (B2, 181.3, 2), (B2, 203.5, 2, "rot"), (B2, 205.5, 2, "rot"), (B2, 25.0, 1), (B2, 207.5, 2, "rot")],
     "info": {"name": "스포마루 (SPOMARU)", "lines": ["AI 인터랙티브 바닥 놀이", "바닥에 튕기는 공을 발로 '뻥!'", "원하는 활동을 문장으로 쓰면 AI가 게임으로"]}},
    # 11 phrase cards (Joy says them in the VO), Mark kicking on the beat
    {"kind": "phrases", "n": 1, "phrases": [(30.10, 31.28, "Kick the ball!", "공을 차!"), (31.50, 32.82, "Throw it to me!", "나한테 던져!"), (33.60, 34.60, "Your turn!", "네 차례야!")],
     "shots": [(B2, 213.0, 2, "rot"), (B2, 215.6, 2, "rot"), (B2, 207.0, 2, "rot")]},   # "Catch!" was not in the recording
    # 12 Mark on why it works (his voice; picture = the game)
    {"kind": "bite", "bite": (B2, 251.95, 255.75), "who": "Mark", "cap": "They're not just on their fingers,\nthey're actually jumping up and down!",
     "ko": "손가락만 쓰는 게 아니라, 온몸으로 뛰면서 놀아요!", "picture": (B2, 204.5, "rot")},
    # 13 end: save + share + follow (Joy's last VO line)
    {"kind": "end", "pieces": [(34.98, 36.92, "저장해 두고\n아이랑 꼭 해 보세요!"), (37.38, 39.20, "See you tomorrow!", "Mark")], "shot": (B2, 0.8)},
]
END_TAIL = 1.2
VO, GAP = "raw-footage/day36/vo.m4a", 0.12   # Joy + Mark's recording (등촌동 4.m4a, 20 Nov); silences between lines cut to GAP


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
            for pc in S["pieces"]:
                a, b, text = pc[:3]; who = pc[3] if len(pc) > 3 else ""; d = b - a
                bites.append({"src": VO, "ss": a, "t": round(t, 3), "d": round(d, 3), "vo": True})
                if len(pc) > 4 and pc[4] == "play":
                    S["playAt"] = round(t, 3)
                if text:
                    caps.append({"s": round(t, 3), "e": round(t + d + GAP, 3), "text": text, "vo": True, "who": who if who == "Mark" else ""})
                t += d + GAP
            if kind == "end":
                t += END_TAIL
            if kind == "end":
                shot(S["shot"][0], S["shot"][1], t - s0, S["shot"][2] if len(S["shot"]) > 2 else None)
            else:
                # fill the section with the listed shots (each N beats), looping if the VO runs longer
                i, sh = 0, S["shots"]
                while t_shot[0] < t - 1e-6:
                    x = sh[i % len(sh)]; d = min(x[2] * BEAT, t - t_shot[0])
                    shot(x[0], x[1] + (i // len(sh)) * 1.0, d, x[3] if len(x) > 3 else None); i += 1
        elif kind == "phrases":
            for (a, b, en, ko), x in zip(S["phrases"], S["shots"]):
                d = b - a + GAP + .1
                bites.append({"src": VO, "ss": a, "t": round(t, 3), "d": round(b - a, 3), "vo": True})
                caps.append({"s": round(t, 3), "e": round(t + d, 3), "text": en, "ko": ko, "phrase": True})
                sfx.append({"t": round(t, 3), "sound": "pop", "gain": -16})
                shot(x[0], x[1], d, x[3] if len(x) > 3 else None); t += d
        sec = {k2: v for k2, v in S.items() if k2 not in ("shots", "bite", "inserts", "picture", "shot")}
        sec.update({"s": round(s0, 3), "e": round(t, 3)})
        secs.append(sec)
    total = round(t, 3)
    plan = {"fps": FPS, "day": 36, "media": "day36", "duration": total, "frames": int(math.ceil(total * FPS)), "beat": BEAT,
            "shots": shots, "captions": caps, "sections": secs, "bites": bites, "sfx": sfx, "voEstimated": False}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    for p in (f"{HERE}/versions/main/plan.json", f"{HERE}/../../remotion/src/day36.json"):
        json.dump(plan, open(p, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s, {len(shots)} shots, {len(caps)} captions")
    for s in secs:
        print(f"  {s['s']:6.2f}-{s['e']:6.2f} {s['kind']:8s} {s.get('n', '')}")


if __name__ == "__main__":
    main()
