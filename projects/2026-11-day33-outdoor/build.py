"""DAY 33 "바깥놀이 영어 3문장" (Joy, 17 Nov 2026). New concept for saves and shares:
a fast montage hook, a chalkboard (top) + Mark (bottom) layout for each phrase, a slow-motion and a normal replay of each phrase,
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
    (15.45, 18.50, "board", None, 0, 1, 1, ""),
    (18.50, 20.38, "boardb", "b2", 4.0, 1, 1, "car"),
    (20.38, 23.30, "boardb", "b3_sdr", 1.0, 1, 1, "boat"),
    (23.30, 26.75, "boardb", "koi", 6.0, 1, 1, "fish"),
    (18.50, 20.30, "replay", None, 0, SLOW, 1, "slow"),
    (18.50, 20.30, "board", None, 0, 1, 1, "again"),
    (27.30, 30.10, "board", None, 0, 1, 2, ""),
    (30.10, 32.90, "boardb", "grassfeet", 0.3, 1, 2, "grass"),
    (32.90, 34.90, "boardb", "b1_sdr", 12.0, 1, 2, "trees"),
    (34.90, 38.00, "board", None, 0, 1, 2, "whatever"),
    (30.10, 32.70, "replay", None, 0, SLOW, 2, "slow"),
    (30.10, 32.70, "board", None, 0, 1, 2, "again"),
    (38.00, 43.00, "board", None, 0, 1, 3, ""),
    (43.00, 46.85, "boardb", "picnic", 1.0, 1, 3, "hungry"),
    (43.00, 44.80, "replay", None, 0, SLOW, 3, "slow"),
    (43.00, 44.80, "board", None, 0, 1, 3, "again"),
    (47.00, 51.05, "full", None, 0, 1, 0, "joke"),
    (51.05, 54.95, "full", None, 0, 1, 0, "bye"),
]
# Korean captions in SOURCE time (only for first-time speech; replays get the board instead)
CAP = [
    (4.10, 8.10, "아이와 밖에 있을 때는"), (8.10, 12.30, "함께 영어를 써볼 정말 좋은 기회예요."),
    (12.40, 15.45, "아이와 함께 쓸 수 있는 말을 알려드릴게요."),
    (15.45, 18.50, "첫 번째, 보이는 것에 따라 이렇게 말해요."),
    (18.50, 20.38, "봐, 자동차야!"), (20.38, 23.30, "봐, 배야!"), (23.30, 26.75, "봐, 물고기야! (강가에 있다면요)"),
    (27.30, 30.10, "두 번째, 'Do you like ~?'"), (30.10, 32.90, "풀 좋아해?"), (32.90, 34.90, "나무 좋아해?"),
    (34.90, 38.00, "좋아하는 건 뭐든 넣어서 물어보세요!"),
    (38.00, 43.00, "마지막으로, 여기는 한국이니까 이렇게 물어볼래요."), (43.00, 46.85, "배고파? 배고프니?"),
    (47.00, 51.05, "서울에서 저를 보면 물어봐 주세요. 그리고 점심 사주세요! 😂"),
    (51.05, 54.95, "고마워요, 또 만나요! 저는 밥 먹으러 갈게요."),
]
PHRASES = {
    1: {"n": "①", "en": "Look, it's a ___!", "ko": "봐, ___야!", "say": "룩, 잇츠 어 ___!", "fill": "car",
        "chips": [("car", "🚗", 18.50), ("boat", "⛵", 20.38), ("fish", "🐟", 23.30)]},
    2: {"n": "②", "en": "Do you like ___?", "ko": "___ 좋아해?", "say": "두 유 라이크 ___?", "fill": "grass",
        "chips": [("grass", "🌱", 30.10), ("trees", "🌳", 32.90), ("…", "✨", 34.90)]},
    3: {"n": "③", "en": "Are you hungry?", "ko": "배고파?", "say": "아 유 헝그리?", "fill": "",
        "chips": [("hungry", "🍙", 43.00), ("Do you feel hungry?", "😋", 44.95)]},
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

    caps = [{"s": first_out(a), "e": first_out(b), "ko": ko} for a, b, ko in CAP]
    phrases = []
    for k, p in PHRASES.items():
        gs = [g for g in segs if g["phrase"] == k]
        phrases.append({"k": k, "s": gs[0]["out_s"], "e": gs[-1]["out_e"], **{x: p[x] for x in ("n", "en", "ko", "say", "fill")},
                        "chips": [{"w": w, "emoji": em, "t": first_out(tt)} for w, em, tt in p["chips"]],
                        "slow": next(({"s": g["out_s"], "e": g["out_e"]} for g in gs if g["note"] == "slow"), None),
                        "again": next(({"s": g["out_s"], "e": g["out_e"]} for g in gs if g["note"] == "again"), None)})
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
        add(p["slow"]["s"] - 0.05, "boing", -11)
        add(p["again"]["s"] - 0.05, "pop", -10)
    joke = next(g for g in segs if g["note"] == "joke")
    add(joke["out_s"] + 3.0, "boing", -9)
    add(speech_end, "impact", -7); add(speech_end + 0.1, "sparkle", -10)
    add(speech_end + SUMMARY, "whoosh", -10)
    add(speech_end + SUMMARY + 1.9, "pop", -6); add(speech_end + SUMMARY + 2.8, "pop", -6); add(speech_end + SUMMARY + 2.85, "chime", -9)
    plan = {"fps": FPS, "day": DAY, "duration": total, "frames": int(math.ceil(total * FPS)), "speechEnd": speech_end, "summaryEnd": round(speech_end + SUMMARY, 3),
            "media": "day33/main", "segments": segs, "captions": caps, "phrases": phrases,
            "joke": {"s": round(joke["out_s"] + 2.6, 3), "e": joke["out_e"]}, "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/main/timeline.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s (speech {speech_end:.1f}s)")
    for g in segs:
        print(f"  {g['out_s']:5.1f}-{g['out_e']:5.1f} {g['layout']:7} {g['broll'] or '':10} {g['note']}")


if __name__ == "__main__":
    main()
