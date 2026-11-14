"""DAY 32 plan for BearJoyReelV2: Joy's stroller-walk English, with B-roll, phrase pops, falling leaves and a breeze.
Run (repo root): .venv/bin/python projects/2026-11-day32-stroller/build.py raw-footage/day32/audio16k.wav
Writes versions/main/timeline_v2.json (segments carry the B-roll choice for cut.py) and prints the reading-speed table.
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-confidence"))
from build_timeline import load_db, snap  # noqa: E402
from edl import DAY, END, SEGS, LINES  # noqa: E402

FPS = 30
CAPTION_TOP = 1330
HI = {"아기에게": 0, "막막한": 0, "어렵게": 0, "보고 느끼는": 0, "출발할 때는": 0, "나무를": 0, "살랑살랑": 0, "작은 것들을": 0, "한마디로": 0,
      "괜찮아요.": 0, "반응하면서": 0, "자연스럽게": 0, "더 필요하신가요?": 0, "'산책'": 0, "20가지를": 0, "바로 쓸 수 있는": 0, "유모차를 끌 때": 0}
# pops: (source time, source end, small, big, slot, sound, size) — times in SOURCE seconds of Joy's voice
POPS = [
    (18.50, 22.20, "보고 · 느끼는 것 그대로", "영어 한마디 💬", "mid", "sparkle", None),
    (23.05, 24.75, "출발할 때", "①", "mid", "pop", 200),
    (27.65, 29.85, "나무를 발견하면", "②", "mid", "pop", 200),
    (32.80, 35.15, "바람이 불 때", "③", "mid", "pop", 200),
    (45.70, 48.20, "", "대답 못 해도 OK 👶", "mid", "boing", None),
    (58.90, 61.75, "댓글에", "💬 '산책'", "mid", "impact", 170),
    (61.80, 68.10, "산책 영어 표현", "📩 20가지 보내드려요", "mid", "sparkle", 96),
]
# English phrases, big and bouncy (source times)
PHRASES = [(24.78, 26.95, "Here we go!", "🚼"), (29.88, 32.78, "Look at that tree!", "🌳"), (35.20, 37.75, "Can you feel the breeze?", "🍃")]


def main():
    db = load_db(sys.argv[1] if len(sys.argv) > 1 else "raw-footage/day32/audio16k.wav")
    segs, t = [], 0.0
    for k, (kind, s, e, br, bs) in enumerate(SEGS):
        s2 = s if round(s * 100) % 5 else snap(s, db, 0.12, 0.05)  # a start not on a 0.05 grid is hand-placed: keep it
        e2 = snap(e, db, 0.05, 0.15)
        if segs and kind != "cold" and segs[-1]["kind"] != "cold" and s2 < segs[-1]["src_e"] + 0.02 and s2 > segs[-1]["src_s"]:
            s2 = segs[-1]["src_e"]  # continue exactly where the last take stopped: no repeated syllables
        segs.append({"kind": kind, "src_s": s2, "src_e": e2, "out_s": round(t, 3), "broll": br, "b_s": bs})
        t += e2 - s2
    speech_end = round(t, 3); total = round(speech_end + END, 3)

    def to_out(x):
        body = segs  # v2: the cold open no longer repeats a later line, so it maps like any take
        for g in body:
            if g["src_s"] - 1e-6 <= x <= g["src_e"] + 1e-6:
                return round(g["out_s"] + x - g["src_s"], 3)
        best = min(body, key=lambda g: min(abs(x - g["src_s"]), abs(x - g["src_e"])))
        return round(best["out_s"] + (0 if x < best["src_s"] else best["src_e"] - best["src_s"]), 3)

    syl = lambda p: len(re.findall(r"[가-힣0-9]", p)) + 1.5 * len(re.findall(r"[A-Za-z']+", p))
    raw = open("raw-footage/day32/ko_words.srt", encoding="utf8", errors="replace").read()
    tsec = lambda x: sum(float(q.replace(",", ".")) * m for q, m in zip(x.split(":"), [3600, 60, 1]))
    onsets = [tsec(a_) for a_, b_, w in re.findall(r"(\d+:\d+:[\d,]+) --> (\d+:\d+:[\d,]+)\n(.*)", raw) if w.startswith(" ")]
    def on_word(x, lo, hi):
        near = [o for o in onsets if lo + 0.4 < o < hi - 0.4]
        return min(near, key=lambda o: abs(o - x)) if near else x
    C = []
    for s, e, ko, en in LINES:
        ps = [p.strip() for p in ko.split(" / ")]
        n = [max(1, syl(p)) for p in ps]
        a = s
        for j, (p, k) in enumerate(zip(ps, n)):
            b = a + (e - s) * k / sum(n)
            if j < len(ps) - 1:
                b = on_word(b, s, e)
            cap = {"i": len(C), "s": to_out(a), "e": to_out(b), "ko": p, "en": "", "hi": next((h for h in HI if h in p), ""), "demo": False, "words": []}
            if en and False:  # the English phrase is the big pop above; the caption keeps the Korean meaning only
                ws = en.split()
                cap["en"] = en
                cap["words"] = [{"w": w, "t": round(to_out(s) + (to_out(e) - to_out(s) - 0.3) * i / len(ws), 3)} for i, w in enumerate(ws)]
            C.append(cap); a = b
    C.sort(key=lambda c: c["s"])
    for a, b in zip(C, C[1:]):
        if 0 < b["s"] - a["e"] < 0.6:
            a["e"] = b["s"]
    for c in C:
        c["s"] = max(0, c["s"] - 0.08)
    ev, sfx = [], []
    add = lambda tt, s, g: sfx.append({"t": round(max(0, tt), 3), "sound": s, "gain": g})
    cold = segs[0]["src_e"] - segs[0]["src_s"]
    # cold open: stroller POV, leaves, the title, Joy's question
    ev.append({"type": "pop", "s": -0.3, "e": round(cold, 3), "kicker": "말 못 하는 아기에게도 OK 👶", "text": "유모차 산책 영어 🍂", "slot": "hook", "k": 90, "size": 116, "kickerSize": 60})
    # Joy (DAY 30): the first frame is the thumbnail, so it also says what viewers get
    ev.append({"type": "pop", "s": -0.25, "e": round(cold, 3), "kicker": "", "text": "📩 산책 영어 표현 20가지 공유해요", "slot": "hook2", "k": 92, "size": 56, "color": "#FFFFFF"})
    ev.append({"type": "leaves", "s": 0.0, "e": round(cold, 3), "emoji": ["🍂", "🍁", "🍂"], "n": 18})
    ev.append({"type": "speaker", "s": -0.3, "e": round(cold, 3), "img": "brand/mark-avatar.png", "name": "Mark T", "flags": "🇬🇧",
               "note": "원어민 발음", "right": 40, "top": 400, "scale": 1.45})
    add(0.0, "impact", -7); add(0.05, "sparkle", -12)

    for k, (s, e, kick, text, slot, snd, size) in enumerate(POPS):
        p = {"type": "pop", "s": to_out(s), "e": to_out(e), "text": text, "kicker": kick, "slot": slot, "k": k}
        if size:
            p["size"] = size
        ev.append(p); add(to_out(s), snd, {"pop": -9, "impact": -7}.get(snd, -11))
        ev.append({"type": "punch", "s": to_out(s), "e": to_out(s) + 0.25, "z": 1.05, "shake": 5})
    for k, (s, e, en, emo) in enumerate(PHRASES):
        # Joy: the three English phrases are Mark's voice, so his face and the UK flag sit right above each one
        ev.append({"type": "speaker", "s": to_out(s) - 0.1, "e": to_out(e), "img": "brand/mark-avatar.png", "name": "Mark T", "flags": "🇬🇧",
                   "note": "원어민 발음", "center": True, "top": 760, "scale": 1.2})
        ev.append({"type": "pop", "s": to_out(s), "e": to_out(e), "kicker": "", "text": f"{en} {emo}", "slot": "mid", "k": 40 + k, "size": 104 if len(en) < 20 else 74})
        add(to_out(s), "impact", -8); add(to_out(s) + 0.05, "sparkle", -12)
        ev.append({"type": "punch", "s": to_out(s), "e": to_out(s) + 0.35, "z": 1.1, "shake": 7})
    # effects on the walks
    tree = next(x for x in segs if x["broll"] == "walk1" and x["kind"] == "broll")
    breeze = next(x for x in segs if x["broll"] == "walk2")
    for x, wind in ((tree, 0), (breeze, 140)):
        ev.append({"type": "leaves", "s": x["out_s"], "e": round(x["out_s"] + x["src_e"] - x["src_s"], 3), "emoji": ["🍂", "🍁", "🍃"], "n": 14, "wind": wind})
    ev.append({"type": "wind", "s": breeze["out_s"], "e": round(breeze["out_s"] + breeze["src_e"] - breeze["src_s"], 3)})
    ev.append({"type": "sticker", "s": to_out(58.9), "e": to_out(68.15), "img": "day32/main/walk-20-phrases.png", "x": 755, "y": 470, "w": 300, "rot": 6,
               "label": "📩 20가지 무료!"})
    add(to_out(58.9) + 0.05, "whoosh", -10)
    ev.append({"type": "burst", "s": to_out(58.95), "e": to_out(58.95) + 1.4, "x": 540, "y": 1000, "emoji": ["💬", "🍂", "💛"], "n": 14, "size": 80})
    for x in segs[1:]:
        add(x["out_s"] - 0.06, "whoosh", -14)
    ev.append({"type": "tag", "s": to_out(18.5), "e": to_out(22.2), "name": "Joy T", "flags": "🇰🇷", "role": "Bear & Joy 공동 저자"})
    add(to_out(18.5), "whoosh", -12)
    ev.append({"type": "end", "s": round(speech_end - 0.1, 3), "e": total, "short": False, "share": "💬 댓글에 '산책' 남기고 20가지 표현 받기"})
    ev.append({"type": "badge", "s": round(cold, 3), "e": speech_end - 0.1, "day": DAY, "docked": True})
    add(speech_end - 0.1, "impact", -8); add(speech_end + 0.05, "sparkle", -10)
    add(speech_end + 1.9, "pop", -6); add(speech_end + 2.8, "pop", -6); add(speech_end + 2.85, "chime", -9)
    zooms = [{"t": c["s"], "z": 1.05 if k % 2 else 1.0} for k, c in enumerate(C)]
    plan = {"name": "day32-main", "media": "day32/main", "fps": FPS, "duration": total, "frames": int(math.ceil(total * FPS)), "speechEnd": speech_end,
            "day": DAY, "segments": segs, "captions": C, "events": ev, "zooms": zooms, "music": {"dropouts": [], "drops": []},
            "slots": {"hook": {"left": 0, "right": 0, "top": 700, "rot": -3}, "hook2": {"left": 0, "right": 0, "top": 960, "rot": -2}, "mid": {"left": 0, "right": 0, "top": 900, "rot": -2},
                      "low": {"left": 0, "right": 0, "top": 1150, "rot": 2}},
            "tagPos": {"left": 50, "top": 1140}, "scrim": True, "look": "original", "captionTop": CAPTION_TOP, "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/main/timeline_v2.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s ({speech_end:.1f}s speech), {len(segs)} segments, {len(C)} captions")
    for x in segs:
        print(f"  {x['out_s']:5.1f} {x['kind']:5} {x['broll'] or ''}")
    for c in C:
        n = syl(c["ko"]); d = c["e"] - c["s"]
        flag = "  <-- fast" if n / d > 6.5 else ("  <-- short" if d < 1.2 else "")
        print(f"  {c['s']:6.2f} {d:4.2f}s {n:4.1f}자 {n / d:4.1f}/s [{c['hi']}] {c['en']} {c['ko']}{flag}")


if __name__ == "__main__":
    main()
