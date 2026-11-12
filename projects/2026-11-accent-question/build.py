"""Edit plan: "내 영어 발음이 안 좋으면 아이 영어도 문제?" — Mark answers a parent's question on the balcony.

Usage (repo root): python3 projects/2026-11-accent-question/build.py
Writes versions/main/timeline_v2.json for BearJoyReelV2.

Structure (viral pass, same idea Joy approved on Day 28):
  cold open  Mark's answer first: "And I promise you, it will not."  (title on screen from frame 1)
  question   flash + scratch, back to the parent's question (title only, no long caption: Joy, Day 28)
  answer     British teacher -> "it will not" behind his head -> songs / stories / teachers -> the accent comes from there
  cliff      "What they get from you is different." -> "그게 뭘까요?" -> follow card (answer in the next video)
All times below are SOURCE seconds in work/src.mov unless they say "out".
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, DAY, END = 30, 29, 5.0   # owner, 12 Nov 2026: "29", posted 13 Nov

COLD = (13.72, 16.45)                       # "And I promise you, it will not."
BODY = [(1.78, 6.62), (7.55, 29.15)]        # "Mark Teacher! ...문제가 될까요?" | (pause cut) | the answer to the end of the take

# Mark's English, word by word (start times from whisper DTW checked against the loudness map), with a Korean line.
# Korean drafted by Claude: the owner has not supplied translations yet.
W = lambda *a: [{"w": w, "t": t} for w, t in zip(a[0::2], a[1::2])]
LINES = [
    (7.55, 8.80, "좋은 질문이에요.", W("Good", 7.85, "question.", 8.18)),
    (8.80, 10.12, "전 영국인이에요.", W("I'm", 9.10, "British.", 9.40)),
    (10.12, 13.62, "서울 영어유치원에서 오래 가르쳤는데요,",
     W("I", 10.14, "taught", 10.32, "English", 10.70, "kindergarten", 11.10, "in", 12.20, "Seoul", 12.38, "for", 12.60, "many", 12.78, "years,", 13.10)),
    (13.62, 16.60, "장담하는데, 절대 아니에요.", W("and", 13.78, "I", 13.92, "promise", 14.08, "you,", 14.60, "it", 15.33, "will", 15.62, "not.", 16.00)),
    (16.60, 20.55, "아이는 영어를 사방에서 들어요.", W("Your", 16.85, "child", 17.25, "hears", 18.28, "English", 18.75, "from", 19.40, "everywhere.", 19.75)),
    (20.55, 23.05, "", W("Songs,", 20.68, "stories,", 21.55, "teachers,", 22.40)),   # the Korean is in the list above the caption
    (23.05, 25.80, "발음은 거기서 만들어져요.", W("that's", 23.28, "where", 23.58, "the", 23.80, "accent", 24.05, "comes", 25.10, "from.", 25.42)),
    (25.80, 29.15, "부모에게서 받는 건 따로 있어요.", W("What", 25.93, "they", 26.14, "get", 26.33, "from", 26.52, "you", 26.72, "is", 26.95, "different.", 27.20)),
]
COLD_LINE = ("장담하는데, 절대 아니에요.", W("And", 13.78, "I", 13.92, "promise", 14.08, "you,", 14.60, "it", 15.33, "will", 15.62, "not.", 16.00))

HOOK = {"kicker": "내 영어 발음이 안 좋으면", "text": "아이 영어도 문제?", "size": 132, "kickerSize": 80}
SLOTS = {"mid": {"left": 0, "right": 0, "top": 960, "rot": -2}, "hook": {"left": 0, "right": 0, "top": 860, "rot": -3},
         "low": {"left": 0, "right": 0, "top": 1075, "rot": 2}}
CAPTION_TOP = 1250
clean = lambda s: "".join(ch for ch in s if ch.isalnum())


def build(name="main"):
    cold = round(COLD[1] - COLD[0], 3)
    segs, t = [{"src_s": COLD[0], "src_e": COLD[1], "out_s": 0.0, "cold": True}], cold
    for s, e in BODY:
        segs.append({"src_s": s, "src_e": e, "out_s": round(t, 3)}); t += e - s
    speech_end = round(t, 3)

    def o(x):
        for g in segs[1:]:
            if g["src_s"] - 1e-6 <= x <= g["src_e"] + 1e-6:
                return round(g["out_s"] + x - g["src_s"], 3)
        raise ValueError(f"{x} is cut")

    C = [{"i": 0, "s": 0.0, "e": cold, "ko": COLD_LINE[0], "en": " ".join(w["w"] for w in COLD_LINE[1]), "hi": "", "demo": False, "mark": True, "onCam": True,
          "words": [{"w": w["w"], "t": round(w["t"] - COLD[0], 3)} for w in COLD_LINE[1]], "kwords": []}]
    for k, (s, e, ko, words) in enumerate(LINES):
        C.append({"i": k + 1, "s": o(s), "e": o(e), "ko": ko, "en": " ".join(w["w"] for w in words), "hi": "", "demo": False, "mark": True, "onCam": True,
                  "words": [{"w": w["w"], "t": o(w["t"])} for w in words], "kwords": []})

    ev, sfx = [], []
    add = lambda tt, s, g: sfx.append({"t": round(max(0, tt), 3), "sound": s, "gain": g})
    pop = lambda s, e, text, kicker="", slot="mid", snd="pop", k=1, **kw: (
        ev.append({"type": "pop", "s": s, "e": e, "text": text, "kicker": kicker, "slot": slot, "k": k, **kw}),
        add(s, snd, -9 if snd == "pop" else -11), ev.append({"type": "punch", "s": s, "e": s + 0.25, "z": 1.035, "shake": 5}))

    # --- hook: the title is on screen from frame 1 (thumbnail), over the cold open and the question
    q_end = o(6.62)
    ev.append({"type": "pop", "s": -0.6, "e": q_end, "text": HOOK["text"], "kicker": HOOK["kicker"], "slot": "hook", "k": 0, "size": HOOK["size"], "kickerSize": HOOK["kickerSize"]})
    ev.append({"type": "punch", "s": 0.0, "e": cold - 0.05, "z": 1.10, "shake": 0, "hold": True})
    nt = 16.00 - COLD[0]                                   # "not."
    ev.append({"type": "punch", "s": nt, "e": nt + 0.3, "z": 1.07, "shake": 8}); add(nt, "impact", -7)
    ev.append({"type": "flash", "s": cold, "e": cold + 0.22}); add(cold - 0.3, "scratch", -7); add(cold, "whoosh", -10)
    ev.append({"type": "tag", "s": cold + 0.15, "e": q_end, "name": "오늘의 질문", "flags": "💬", "role": "", "pos": {"left": 60, "top": 1130}})
    ev.append({"type": "punch", "s": o(5.25), "e": q_end - 0.1, "z": 1.12, "shake": 4, "hold": True})   # push in on "아이 영어에도 문제가 될까요?"
    add(o(5.25), "pop", -10)

    # --- the answer
    ev.append({"type": "badge", "s": q_end, "e": speech_end - 0.2, "day": DAY, "docked": True})
    add(q_end, "whoosh", -13)
    ev.append({"type": "tag", "s": o(8.85), "e": o(13.55), "name": "Mark T", "flags": "🇬🇧", "role": "영국인 선생님", "playfair": True, "pos": {"left": 590, "top": 330}})
    ev.append({"type": "burst", "s": o(9.40), "e": o(9.40) + 1.5, "x": 540, "y": 1000, "emoji": ["🇬🇧"], "n": 16, "size": 96})
    add(o(9.40), "sparkle", -11); ev.append({"type": "punch", "s": o(9.40), "e": o(9.40) + 0.25, "z": 1.05, "shake": 6})
    pop(o(11.05), o(13.55), "영어유치원 선생님 🏫", "🇰🇷 서울에서 여러 해", k=1)

    def behind(s, e, kicker, ko, size, top, k):
        s, e = o(s), o(e)
        # Joy (Day 28): a plain Bear & Joy cream background behind the pulled-back picture, deep-blue words
        ev.append({"type": "behind", "ko": ko, "en": kicker, "size": size, "top": top, "s": s, "e": e, "k": k, "cream": True})
        ev.append({"type": "pull", "s": s - 0.12, "e": e, "z": 0.74, "bg": "#F5F0E6"})
        add(s - 0.15, "whoosh", -9); add(s, "impact", -7); add(s + 0.05, "sparkle", -13)
    behind(14.55, 16.55, "발음 걱정?", "절대 아니에요!", 170, 215, 0)

    # "hears English from everywhere": emoji pop up all around him, then the three sources land as a list
    spots = [("🎵", 640, 330, 18.28), ("📺", 960, 660, 18.75), ("🎧", 640, 820, 19.40), ("📖", 950, 1010, 19.75), ("🧸", 140, 1130, 19.95), ("🎬", 800, 440, 20.12)]  # clear of his face
    ev.append({"type": "scatter", "s": o(18.28), "e": o(20.62), "items": [{"e": e, "x": x, "y": y, "t": o(tt), "size": 130} for e, x, y, tt in spots]})
    for _, _, _, tt in spots:
        add(o(tt), "pop", -13)
    items = [("🎵", "노래", 20.68), ("📖", "이야기", 21.55), ("🧑‍🏫", "선생님", 22.40)]
    ev.append({"type": "list", "s": o(20.68), "e": o(25.72), "top": 800, "items": [{"emoji": e, "text": tx, "t": o(tt)} for e, tx, tt in items]})
    for _, _, tt in items:
        add(o(tt), "pop", -7); ev.append({"type": "punch", "s": o(tt), "e": o(tt) + 0.22, "z": 1.04, "shake": 5})
    pop(o(24.05), o(25.72), "👆 아이 발음은 여기서!", slot="low", snd="boing", k=0, size=84)

    # --- cliffhanger
    behind(26.20, 27.55, "부모가 주는 건", "따로 있어요!", 190, 70, 1)
    cs = o(27.70)
    ev.append({"type": "pop", "s": cs, "e": speech_end - 0.2, "text": "그게 뭘까요? 🤫", "kicker": "", "slot": "mid", "k": 0, "size": 124})
    ev.append({"type": "punch", "s": cs, "e": speech_end - 0.25, "z": 1.14, "shake": 3, "hold": True})
    add(cs - 0.25, "scratch", -8); add(cs, "chime", -9)

    zooms = [{"t": c["s"], "z": 1.07 if k % 2 else 1.0} for k, c in enumerate(C)]
    total = round(speech_end + END, 3)
    es = round(speech_end - 0.2, 3)
    ev.append({"type": "end", "s": es, "e": total, "l1": "팔로우하고", "l2": "정답 확인해요! 👀", "share": "💬 뭘까요? 댓글로 맞혀보세요"})
    add(es, "impact", -8); add(speech_end, "sparkle", -10)
    add(es + 2.0, "pop", -6); add(es + 2.9, "pop", -6); add(es + 2.95, "chime", -9)   # end-card follow taps
    music = {"dropouts": [[cs - 0.05, es]], "drops": [es]}

    plan = {"name": f"accentq-{name}", "media": f"accentq/{name}", "fps": FPS, "duration": total, "frames": int(math.ceil(total * FPS)), "speechEnd": speech_end,
            "day": DAY, "segments": segs, "captions": C, "events": ev, "zooms": zooms, "music": music,
            "slots": SLOTS, "scrim": True, "look": "original",  # the DJI picture is already vivid; the v2 grade turned skin orange
             "captionTop": CAPTION_TOP, "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/{name}", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/{name}/timeline_v2.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{name}: {total:.1f}s ({speech_end:.1f}s speech), {len(C)} captions, {sum(e['type'] == 'pop' for e in ev)} pops, {len(sfx)} sfx")
    print("  reading speed (Korean line: at most ~6 characters/s, at least 1.2 s):")
    for c in C:
        n = len(clean(c["ko"])); d = c["e"] - c["s"]
        flag = "  <-- fast" if (n and (n / d > 6.2 or d < 1.2)) else ""
        print(f"  {c['s']:6.2f} {d:4.2f}s {n:2d}자 {n / d:4.1f}/s  {c['en']} / {c['ko']}{flag}")


if __name__ == "__main__":
    build()
