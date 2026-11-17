"""DAY 33 "바깥놀이 영어 3문장" (Joy, 17 Nov 2026). New concept for saves and shares:
a fast montage hook, a chalkboard (top) + Mark (bottom) layout for each phrase, (replays removed, Joy 17 Nov)
and a save-worthy summary card at the end. Template: remotion/src/OutdoorEnglish.tsx. cut.py composes the picture layouts.
Run (repo root): .venv/bin/python projects/2026-11-day33-outdoor/build.py
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FPS, DAY = 30, 33
SLOW = 0.7       # replay speed (pitch kept)
SUMMARY, END = 5.5, 4.0
# (src_s, src_e, layout, b-roll, b-roll start, speed, phrase, note)
# layouts: montage (full B-roll, cut fast), full (Mark full frame), board (board top + Mark bottom), boardb (board top + B-roll bottom),
#          replay (board top + Mark bottom, slowed)
S = [
    (0.15, 1.00, "montage", "kidrun", 1.0, 1, 0, "hook"),
    (1.00, 1.85, "montage", "b1_sdr", 6.0, 1, 0, "hook"),
    (1.85, 2.75, "montage", "koi", 2.0, 1, 0, "hook"),
    (2.75, 3.70, "montage", "familywalk", 3.0, 1, 0, "hook"),
    (4.10, 12.30, "full", None, 0, 1, 0, "intro"),
    (12.40, 15.45, "full", None, 0, 1, 0, "intro2"),
    # Joy (17 Nov): pictures and swap-in words change when the word itself is heard (times found by ear-probing the audio),
    # and the slow/again replays are gone (they cut words and sounded messy).
    (15.45, 20.55, "board", None, 0, 1, 1, ""),
    (20.55, 22.85, "boardb", "b2", 4.0, 1, 1, "car"),
    (22.85, 24.85, "boardb", "b3_sdr", 1.5, 1, 1, "boat"),
    (24.85, 27.30, "boardb", "koi", 6.0, 1, 1, "fish"),
    (27.30, 32.50, "board", None, 0, 1, 2, ""),
    (32.50, 34.45, "boardb", "grassfeet", 0.3, 1, 2, "grass"),
    (34.45, 35.40, "boardb", "b1_sdr", 12.0, 1, 2, "trees"),
    (35.40, 38.00, "board", None, 0, 1, 2, "whatever"),
    (38.00, 42.95, "board", None, 0, 1, 3, ""),
    (42.95, 46.85, "boardb", "picnic", 1.0, 1, 3, "hungry"),
    (47.00, 51.05, "full", None, 0, 1, 0, "joke"),
    (51.05, 54.95, "full", None, 0, 1, 0, "bye"),
]
# Korean captions in SOURCE time (only for first-time speech; replays get the board instead)
# "\n" = line break (Joy: clean two-line captions). A 4th item is an English line in the chalk font.
CAP = [
    (4.10, 8.10, "아이와 밖에 있을 때는"), (8.10, 12.30, "함께 영어를 써볼\n정말 좋은 기회예요."),
    (12.40, 15.45, "아이와 함께 쓸 수 있는 말을\n알려드릴게요."),
    (15.45, 20.55, "첫 번째,\n보이는 것에 따라 이렇게 말해요."),
    (20.55, 22.85, "봐, 자동차야!"), (22.85, 24.85, "봐, 배야!"), (24.85, 27.30, "봐, 물고기야!\n(강가에 있다면요)"),
    (27.30, 32.50, "두 번째,\n'Do you like ~?'"), (32.50, 34.45, "풀 좋아해?"), (34.45, 35.40, "나무 좋아해?"),
    (35.40, 38.00, "좋아하는 건 뭐든\n넣어서 물어보세요!"),
    (38.00, 42.95, "마지막으로, 여기는 한국이니까\n이렇게 물어볼래요."), (42.95, 46.85, "배고파?\n배고프니?"),
    (47.00, 51.05, "서울에서 저를 보면\n이렇게 물어봐 주세요.", "Are you hungry?"),
    (51.05, 54.95, "고마워요, 또 만나요!\n저는 밥 먹으러 갈게요."),
]
PHRASES = {
    1: {"n": "①", "en": "Look, it's a ___!", "ko": "봐, ___야!", "say": "룩, 잇츠 어 ___!", "fill": "car",
        "chips": [("car", "🚗", 20.60), ("boat", "⛵", 22.95), ("fish", "🐟", 24.92)]},
    2: {"n": "②", "en": "Do you like ___?", "ko": "___ 좋아해?", "say": "두 유 라이크 ___?", "fill": "grass",
        "chips": [("grass", "🌱", 32.55), ("trees", "🌳", 34.50), ("…", "✨", 35.90)]},
    3: {"n": "③", "en": "Are you hungry?", "ko": "배고파?", "say": "아 유 헝그리?", "fill": "",
        "chips": [("hungry", "🍙", 42.96), ("Do you feel hungry?", "😋", 45.30)]},
}


def main():
    segs, t = [], 0.0
    for s, e, lay, br, bs, sp, ph, note in S:
        d = (e - s) / sp
        segs.append({"src_s": s, "src_e": e, "out_s": round(t, 3), "out_e": round(t + d, 3), "layout": lay, "broll": br, "b_s": bs, "speed": sp,
                     "phrase": ph, "note": note})
        t += d
    speech_end = round(t, 3)
    total = round(speech_end + SUMMARY + END, 3)

    def first_out(x):
        for g in segs:
            if g["note"] not in ("slow", "again") and g["src_s"] - 1e-6 <= x <= g["src_e"] + 1e-6:
                return round(g["out_s"] + (x - g["src_s"]) / g["speed"], 3)
        raise ValueError(x)

    caps = [{"s": first_out(c[0]), "e": first_out(c[1]), "ko": c[2], "en": c[3] if len(c) > 3 else ""} for c in CAP]
    phrases = []
    for k, p in PHRASES.items():
        gs = [g for g in segs if g["phrase"] == k]
        phrases.append({"k": k, "s": gs[0]["out_s"], "e": gs[-1]["out_e"], **{x: p[x] for x in ("n", "en", "ko", "say", "fill")},
                        "chips": [{"w": w, "emoji": em, "t": first_out(tt)} for w, em, tt in p["chips"]],
                        "slow": None, "again": None})
    sfx = []
    add = lambda tt, s_, gn: sfx.append({"t": round(max(0, tt), 3), "sound": s_, "gain": gn})
    for g in segs[:4]:
        add(g["out_s"], "whoosh", -10)
    add(0.0, "impact", -6)
    add(segs[4]["out_s"], "impact", -8)
    for p in phrases:
        add(p["s"], "chime", -8)
        for c in p["chips"]:
            add(c["t"], "pop", -10)
    joke = next(g for g in segs if g["note"] == "joke")
    add(speech_end, "impact", -7); add(speech_end + 0.1, "sparkle", -10)
    add(speech_end + SUMMARY, "whoosh", -10)
    add(speech_end + SUMMARY + 1.9, "pop", -6); add(speech_end + SUMMARY + 2.8, "pop", -6); add(speech_end + SUMMARY + 2.85, "chime", -9)
    plan = {"fps": FPS, "day": DAY, "duration": total, "frames": int(math.ceil(total * FPS)), "speechEnd": speech_end, "summaryEnd": round(speech_end + SUMMARY, 3),
            "media": "day33/main", "segments": segs, "captions": caps, "phrases": phrases,
            "joke": {"s": 0, "e": 0}, "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/main/timeline.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s (speech {speech_end:.1f}s)")
    for g in segs:
        print(f"  {g['out_s']:5.1f}-{g['out_e']:5.1f} {g['layout']:7} {g['broll'] or '':10} {g['note']}")


if __name__ == "__main__":
    main()
