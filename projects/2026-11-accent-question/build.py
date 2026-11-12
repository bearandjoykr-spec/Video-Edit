"""DAY 29 edit plan (take 2): "내 영어 발음이 안 좋으면 아이 영어도 문제?" — Mark answers a parent's question on the balcony.

Usage (repo root): python3 projects/2026-11-accent-question/build.py
Writes versions/main/timeline_v2.json for BearJoyReelV2. Source = work/src2.mov (take 2, the full answer; owner, 12 Nov 2026).
Take 1 (build_take1.py) stopped at "What they get from you is different"; take 2 has the payoff, so it carries the whole reel.

Structure:
  cold open  "I promise you, it will not." (title on screen from frame 1)
  question   flash back to the parent's Korean question (title only, no long caption: Joy, Day 28)
  answer     British teacher -> 절대 아니에요! behind his head -> songs / stories / teachers -> "what they get from you is different"
             -> 그게 뭘까요? beat -> safe / fun / mummy too -> the classroom story -> 용기! behind his head
  action     tonight: open a book, say "Look, what can you see?" -> that's enough -> follow card (DAY 30)
All times below are SOURCE seconds in work/src2.mov unless they say "out".
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, DAY, END = 30, 29, 5.0   # owner, 12 Nov 2026: DAY 29, posted 13 Nov

COLD = (10.22, 12.75)                                                  # "I promise you, it will not."
BODY = [(2.33, 28.35), (29.05, 31.12), (31.52, 36.34), (36.84, 48.75)]  # pauses longer than ~0.4 s cut (28.35-29.05, 31.12-31.52, 36.34-36.84)
SHIFT = -0.15                                                          # DTW word times run ~0.15 s late against the waveform

WORDS = []
for ln in open(f"{HERE}/words-en.txt", encoding="utf8"):
    if ln.startswith("#") or not ln.strip():
        continue
    w, t = ln.rstrip("\n").split("\t")
    WORDS.append((w, round(float(t) + SHIFT, 3)))

# (source start, source end, Korean line). The English is every word whose time falls inside [start, end).
# Korean drafted by Claude (the owner has not supplied translations); Mark's British "mummy" kept as 엄마.
LINES = [
    (5.95, 7.30, "전 영국인이에요."),
    (7.30, 9.85, "서울 영어 유아학원에서 가르쳤어요."),  # owner, 12 Nov: in Korea it is called 영어 유아학원
    (9.85, 12.75, "장담하는데, 절대 아니에요."),
    (12.85, 15.90, "아이는 영어를 사방에서 들어요."),
    (15.90, 18.55, "노래, 이야기, 선생님."),
    (18.55, 20.75, "발음은 거기서 만들어져요."),
    (20.75, 23.20, "부모에게서 받는 건 따로 있어요."),
    (23.20, 25.55, "영어는 무섭지 않다는 것,"),
    (25.55, 28.35, "재미있다는 것, 엄마도 한다는 것!"),
    (29.05, 33.60, "제 반에서 말을 제일 많이 한 아이들은"),
    (33.60, 36.34, "완벽한 부모를 둔 아이가 아니었어요."),
    (36.84, 40.85, "틀려도 겁내지 않는 아이들이었어요."),
    (40.85, 44.70, "오늘 밤, 책을 펴고 딱 한마디만 해보세요."),
    (44.70, 47.20, "\"봐, 뭐가 보여?\""),
    (47.20, 48.75, "그거면 충분해요. 안녕!"),
]

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
        body = segs[1:]
        for g in body:
            if g["src_s"] - 1e-6 <= x <= g["src_e"] + 1e-6:
                return round(g["out_s"] + x - g["src_s"], 3)
        nxt = min((g for g in body if g["src_s"] > x), key=lambda g: g["src_s"], default=body[-1])
        return nxt["out_s"]  # inside a cut pause: snap to the next kept frame

    words_in = lambda s, e: [(w, tt) for w, tt in WORDS if s - 0.05 <= tt < e - 0.05]

    C = []
    cw = [(w, max(tt, COLD[0] + 0.05)) for w, tt in words_in(COLD[0] - 0.2, COLD[1]) if w != "and"]  # "I" sits right on the cut
    C.append({"i": 0, "s": 0.0, "e": cold, "ko": LINES[2][2], "en": " ".join(w for w, _ in cw), "hi": "", "demo": False, "mark": True, "onCam": True,
              "words": [{"w": w, "t": round(max(0, tt - COLD[0]), 3)} for w, tt in cw], "kwords": []})
    for k, (s, e, ko) in enumerate(LINES):
        ws = words_in(s, e)
        C.append({"i": k + 1, "s": round(max(o(s), o(ws[0][1]) - 0.1), 3), "e": o(e), "ko": ko, "en": " ".join(w for w, _ in ws), "hi": "", "demo": False,
                  "mark": True, "onCam": True, "words": [{"w": w, "t": o(tt)} for w, tt in ws], "kwords": []})
    for a, b in zip(C[1:], C[2:]):
        a["e"] = b["s"]  # no gaps between Mark's lines

    wt = lambda word, after=0: o(next(tt for w, tt in WORDS if w.strip(",.?!").lower() == word.strip(",.?!").lower() and tt >= after))

    ev, sfx = [], []
    add = lambda tt, s, g: sfx.append({"t": round(max(0, tt), 3), "sound": s, "gain": g})

    def pop(s, e, text, kicker="", slot="mid", snd="pop", k=1, **kw):
        ev.append({"type": "pop", "s": s, "e": e, "text": text, "kicker": kicker, "slot": slot, "k": k, **kw})
        add(s, snd, -9 if snd == "pop" else -11)
        ev.append({"type": "punch", "s": s, "e": s + 0.25, "z": 1.035, "shake": 5})

    def behind(s, e, kicker, ko, size, top, k):
        # Joy (Day 28): a plain Bear & Joy cream background behind the pulled-back picture, deep-blue words
        ev.append({"type": "behind", "ko": ko, "en": kicker, "size": size, "top": top, "s": s, "e": e, "k": k, "cream": True})
        ev.append({"type": "pull", "s": s - 0.12, "e": e, "z": 0.74, "bg": "#F5F0E6"})
        add(s - 0.15, "whoosh", -9); add(s, "impact", -7); add(s + 0.05, "sparkle", -13)

    # --- hook: the title is on screen from frame 1 (thumbnail), over the cold open and the question
    q_end = o(5.95)
    ev.append({"type": "pop", "s": -0.6, "e": q_end, "text": HOOK["text"], "kicker": HOOK["kicker"], "slot": "hook", "k": 0, "size": HOOK["size"], "kickerSize": HOOK["kickerSize"]})
    ev.append({"type": "punch", "s": 0.0, "e": cold - 0.05, "z": 1.10, "shake": 0, "hold": True})
    nt = 12.25 - COLD[0]                                   # "not."
    ev.append({"type": "punch", "s": nt, "e": nt + 0.3, "z": 1.07, "shake": 8}); add(nt, "impact", -7)
    ev.append({"type": "flash", "s": cold, "e": cold + 0.22}); add(cold - 0.3, "scratch", -7); add(cold, "whoosh", -10)
    ev.append({"type": "tag", "s": cold + 0.15, "e": q_end, "name": "오늘의 질문", "flags": "💬", "role": "", "pos": {"left": 60, "top": 1130}})
    ev.append({"type": "punch", "s": o(4.10), "e": q_end - 0.1, "z": 1.12, "shake": 4, "hold": True})   # push in on "우리 아이에게도 영향을 줄까요?"
    add(o(4.10), "pop", -10)

    # --- the answer
    ev.append({"type": "badge", "s": q_end, "e": speech_end - 0.2, "day": DAY, "docked": True})
    add(q_end, "whoosh", -13)
    br = wt("British.")
    ev.append({"type": "tag", "s": o(6.30), "e": o(9.80), "name": "Mark T", "flags": "🇬🇧", "role": "영국인 선생님", "playfair": True, "pos": {"left": 590, "top": 330}})
    ev.append({"type": "burst", "s": br, "e": br + 1.5, "x": 540, "y": 1000, "emoji": ["🇬🇧"], "n": 16, "size": 96})
    add(br, "sparkle", -11); ev.append({"type": "punch", "s": br, "e": br + 0.25, "z": 1.05, "shake": 6})
    pop(wt("kindergarten"), o(9.80), "영어 유아학원 선생님 🏫", "🇰🇷 서울에서", k=1)
    behind(wt("promise", 10), o(12.75), "발음 걱정?", "절대 아니에요!", 170, 215, 0)

    # "hears English from everywhere": emoji pop up around him (clear of his face), then the three sources land as a list
    spots = [("🎵", 640, 330, "hears"), ("📺", 960, 660, "English"), ("🎧", 640, 820, "from"), ("📖", 950, 1010, "everywhere."), ("🧸", 140, 1130, "everywhere."), ("🎬", 800, 440, "everywhere.")]
    sp = [(e, x, y, wt(w, 13) + (0.18 * k if k > 3 else 0)) for k, (e, x, y, w) in enumerate(spots)]
    ev.append({"type": "scatter", "s": sp[0][3], "e": o(15.90), "items": [{"e": e, "x": x, "y": y, "t": tt, "size": 130} for e, x, y, tt in sp]})
    for *_, tt in sp:
        add(tt, "pop", -13)
    src = [("🎵", "노래", wt("Songs,")), ("📖", "이야기", wt("stories,")), ("🧑‍🏫", "선생님", wt("teachers."))]
    ev.append({"type": "list", "s": src[0][2], "e": o(20.70), "top": 800, "items": [{"emoji": e, "text": tx, "t": tt} for e, tx, tt in src]})
    for *_, tt in src:
        add(tt, "pop", -7); ev.append({"type": "punch", "s": tt, "e": tt + 0.22, "z": 1.04, "shake": 5})
    pop(wt("accent"), o(20.70), "👆 아이 발음은 여기서!", slot="low", snd="boing", k=0, size=84)

    # "What they get from you is different." — the beat stops for a second: 그게 뭘까요?
    behind(wt("you", 20.9), o(23.15), "부모가 주는 건", "따로 있어요!", 190, 70, 1)
    q = wt("They", 23)
    pop(q - 0.05, q + 0.95, "그게 뭘까요? 🤔", snd="boing", k=0, size=110)
    add(q - 0.3, "scratch", -8)
    gifts = [("😌", "안 무서워", wt("safe,")), ("🤩", "재미있어", wt("fun,")), ("👩", "엄마도 해!", wt("mummy"))]
    ev.append({"type": "list", "s": gifts[0][2], "e": o(28.35), "top": 800, "size": 80, "gap": 30, "items": [{"emoji": e, "text": tx, "t": tt} for e, tx, tt in gifts]})
    for *_, tt in gifts:
        add(tt, "pop", -7); ev.append({"type": "punch", "s": tt, "e": tt + 0.22, "z": 1.04, "shake": 5})

    # the classroom story
    pop(wt("perfect"), o(36.34), "❌ 완벽한 부모", "말 잘하는 아이의 비결은", k=1, snd="boing")
    behind(wt("afraid"), o(40.85), "틀려도 괜찮아", "겁 없이!", 260, 40, 0)

    # the action for tonight
    pop(wt("tonight,"), o(44.70), "📖 책 펴고 딱 한마디!", "🌙 오늘 밤 미션", k=0, snd="sparkle")
    pop(wt("Look,", 44.5), o(47.20), "Look, what can you see? 👀", "🇬🇧 이렇게 말해보세요", k=1, snd="sparkle", size=78)
    pop(wt("enough."), speech_end - 0.2, "✅ 그거면 충분!", k=0, snd="chime", size=100)
    ev.append({"type": "punch", "s": wt("Bye-bye."), "e": speech_end - 0.25, "z": 1.10, "shake": 2, "hold": True})

    zooms = [{"t": c["s"], "z": 1.07 if k % 2 else 1.0} for k, c in enumerate(C)]
    for g in segs[2:]:
        add(g["out_s"] - 0.05, "whoosh", -15)   # jump cuts
    total = round(speech_end + END, 3)
    es = round(speech_end - 0.2, 3)
    # owner, 12 Nov: a powerful CTA that gets the follow and sends people to the link in the bio.
    # Follow is tapped early (1.2 s / 1.8 s), then the link card bounces in at 2.4 s with a hand pointing up to the profile.
    ev.append({"type": "end", "s": es, "e": total, "l1": "팔로우하고", "l2": "DAY 30도 같이! 🔥", "tap1": 1.2, "tap2": 1.8,
               "link": "🔗 프로필 링크 확인!", "linkSub": "🎁 무료 체험 신청은 프로필 링크에서", "linkAt": 2.4,
               "share": "💌 발음 걱정하는 엄마 아빠에게 보내주세요"})
    add(es, "impact", -8); add(speech_end, "sparkle", -10)
    add(es + 1.2, "pop", -6); add(es + 1.8, "pop", -6); add(es + 1.85, "chime", -9)   # end-card follow taps
    add(es + 2.35, "whoosh", -10); add(es + 2.4, "boing", -8)                         # link card
    # owner, 12 Nov 2026: "use the drop for the big reveal". The beat cuts out on 그게 뭘까요? and the track's drop
    # (lofi-hip-hop-578608.mp3 at 109.10 s, after its breakdown) hits on the first answer, 😌 안 무서워 ("English is safe").
    reveal = gifts[0][2]
    add(reveal, "impact", -6)
    ev.append({"type": "punch", "s": reveal, "e": reveal + 0.35, "z": 1.08, "shake": 10})
    music = {"dropouts": [[q - 0.3, reveal]], "drops": [reveal], "track": "music/lofi-hip-hop-578608.mp3", "trackDrop": 109.10,
             "start": round(109.10 - reveal, 3)}

    plan = {"name": f"accentq-{name}", "media": f"accentq/{name}", "fps": FPS, "duration": total, "frames": int(math.ceil(total * FPS)), "speechEnd": speech_end,
            "day": DAY, "segments": segs, "captions": C, "events": ev, "zooms": zooms, "music": music,
            "slots": SLOTS, "scrim": True, "look": "original",  # the DJI picture is already vivid; the v2 grade turned skin orange
            "captionTop": CAPTION_TOP, "joyRanges": [[segs[1]["out_s"], q_end]],  # Joy's question, softened in voice.py (owner, 12 Nov)
            "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/{name}", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/{name}/timeline_v2.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{name}: {total:.1f}s ({speech_end:.1f}s speech), {len(C)} captions, {sum(e['type'] == 'pop' for e in ev)} pops, {len(sfx)} sfx")
    print("  reading speed (Korean line: at most ~6 characters/s, at least 1.2 s):")
    for c in C:
        n = len(clean(c["ko"])); d = c["e"] - c["s"]
        flag = "  <-- fast" if (n and (n / d > 6.0 or d < 1.2)) else ""
        print(f"  {c['s']:6.2f} {d:4.2f}s {n:2d}자 {n / d:4.1f}/s  {c['en']} / {c['ko']}{flag}")


if __name__ == "__main__":
    build()
