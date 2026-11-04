"""v2 edit plan: high-energy reel. Same cuts as v1, plus word-level karaoke, key-point pops,
flags, Day-23 badge, punch zooms and a lo-fi beat with a comic stop.

Usage: python3 build_timeline_v2.py AUDIO_16K_WAV
Writes versions/<name>/timeline_v2.json
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_timeline import VERSIONS, HI, END_CARD, FPS, load_db, snap  # noqa: E402
caps = json.load(open(f"{HERE}/captions.json", encoding="utf8"))
words = json.load(open(f"{HERE}/words.json", encoding="utf8"))
DAY = 23
END_V2 = 5.0  # longer end card for the follow CTA

# Words behind the head (Korean punch + small English kicker)
BEHIND = [
    {"ko": "발음 걱정?", "en": "PRONUNCIATION?", "s": 0.51, "e": 4.20, "size": 210, "top": 680, "sfx": "impact"},
    {"ko": "자신감!", "en": "CONFIDENCE", "s": 44.3, "e": 46.2, "size": 250, "top": 470, "sfx": "impact"},
    {"ko": "괜찮아!", "en": "IT'S OKAY", "s": 67.8, "e": 69.4, "size": 250, "top": 490, "sfx": "impact"},
]
# Key-point pops: (start, end, text, slot, sound). Slots keep clear of the face.
POPS = [
    (10.9, 12.7, "겉모습 👀", "tr", "pop"),
    (18.9, 20.5, "🇰🇷 부모님", "tl", "pop"),
    (24.0, 26.4, "🇬🇧 영국인!", "tr", "pop"),
    (34.6, 37.3, "발음 = 1단계 ❌", "center", "boing"),
    (47.4, 49.4, "한국어 억양 = 😅", "tr", "pop"),
    (52.5, 55.3, "엉망 😂", "tr", "boing"),
    (55.5, 56.9, "그래도 자신감 💪", "center", "pop"),
    (58.9, 60.7, "통한다! ✅", "tr", "pop"),
    (62.6, 64.1, "자신감 키우기 🌱", "tl", "pop"),
    (69.0, 70.5, "평가 ❌", "tr", "pop"),
    (74.8, 76.1, "배우기 싫어요 😢", "tr", "pop"),
    (79.93, 82.6, "재미있게 🎉", "stack0", "pop"),
    (81.02, 82.6, "즐겁게 😊", "stack1", "pop"),
    (81.70, 82.6, "부담 없이 🪶", "stack2", "pop"),
    (84.2, 85.8, "자신감 UP! 🚀", "center", "sparkle"),
    (86.4, 87.9, "첫걸음 👣", "center", "sparkle"),
]
DEMO_WORDS = [("오른쪽?", 49.44), ("왼쪽?", 50.6), ("배고파요?", 51.75)]
DEMO = (49.44, 52.44)
TAG = {"full": (23.5, 30.3), "short": (46.2, 49.4)}

norm = lambda w: re.sub(r"[^a-z0-9']", "", w.lower().replace("’", "'"))


def build(name, segs, db):
    segs = [(snap(s, db, 0.15, 0.0) if k else s, snap(e, db, 0.0, 0.2)) for k, (s, e) in enumerate(segs)]
    out = []; t = 0.0
    for s, e in segs:
        out.append({"src_s": s, "src_e": e, "out_s": round(t, 3)}); t += e - s
    speech_end = round(t, 3)

    def to_out(x):
        for g in out:
            if g["src_s"] - 1e-6 <= x <= g["src_e"] + 1e-6:
                return round(g["out_s"] + x - g["src_s"], 3)
        return None

    def span(s, e, min_len=0.05):
        best = None
        for g in out:
            a, b = max(s, g["src_s"]), min(e, g["src_e"])
            if b - a > min_len and (best is None or b - a > best[1] - best[0]):
                best = (a, b)
        return (to_out(best[0]), to_out(best[1])) if best else None

    C = []
    for c in caps:
        sp = span(c["s"], c["e"])
        if not sp:
            continue
        # English words of this line, timed in edited time, for karaoke highlighting
        ws = []
        if c["en"] and c["i"] != 0:  # line 0 is spoken in Korean: no English karaoke
            pool = [w for w in words if c["s"] - 0.3 <= w["s"] <= c["e"] + 0.1 and to_out(w["s"]) is not None]
            pi = 0
            for tok in c["en"].split():
                st = None
                for j in range(pi, len(pool)):
                    if norm(pool[j]["w"]) == norm(tok):
                        st = to_out(pool[j]["s"]); pi = j + 1; break
                ws.append({"w": tok, "t": st})
            # fill unmatched words by interpolation
            for k, w in enumerate(ws):
                if w["t"] is None:
                    prev = next((ws[j]["t"] for j in range(k - 1, -1, -1) if ws[j]["t"] is not None), sp[0])
                    nxt = next((ws[j]["t"] for j in range(k + 1, len(ws)) if ws[j]["t"] is not None), sp[1])
                    w["t"] = round(prev + (nxt - prev) * 0.5, 3)
        C.append({"i": c["i"], "s": sp[0], "e": sp[1], "ko": c["ko"], "en": c["en"], "hi": HI.get(c["i"], ""),
                  "words": ws, "demo": c["i"] == 19})
    for a, b in zip(C, C[1:]):
        if 0 < b["s"] - a["e"] < 0.6:
            a["e"] = b["s"]

    ev, sfx = [], []
    add = lambda t, s, g: sfx.append({"t": round(max(0, t), 3), "sound": s, "gain": g})
    for bw in BEHIND:
        sp = span(bw["s"], bw["e"])
        if sp:
            ev.append({"type": "behind", **{k: v for k, v in bw.items() if k not in ("s", "e", "sfx")}, "s": sp[0], "e": sp[1],
                       "k": sum(e["type"] == "behind" for e in ev)})
            add(sp[0] - 0.05, bw["sfx"], -6); add(sp[0], "sparkle", -14)
            ev.append({"type": "punch", "s": sp[0], "e": sp[0] + 0.35, "z": 1.06, "shake": 10})
    for s, e, text, slot, snd in POPS:
        sp = span(s, e, 0.4)
        if sp:
            ev.append({"type": "pop", "s": sp[0], "e": sp[1], "text": text, "slot": slot, "k": sum(e["type"] == "pop" for e in ev) + 1})
            add(sp[0], snd, -9 if snd == "pop" else -11)
            if slot in ("center",):
                ev.append({"type": "punch", "s": sp[0], "e": sp[0] + 0.3, "z": 1.04, "shake": 6})
    sp = span(*DEMO)
    music = {"dropouts": [], "drops": []}
    if sp:
        ev.append({"type": "demo", "s": sp[0], "e": sp[1], "words": [{"w": w, "t": to_out(tt)} for w, tt in DEMO_WORDS]})
        ev.append({"type": "punch", "s": sp[0], "e": sp[1], "z": 1.16, "shake": 4, "hold": True})
        add(sp[0] - 0.35, "scratch", -6)
        for w, tt in DEMO_WORDS:
            add(to_out(tt), "boing", -12)
        music["dropouts"].append([sp[0] - 0.05, sp[1]])
        music["drops"].append(sp[1])
    ts = span(*TAG[name])
    if ts:
        ev.append({"type": "tag", "s": ts[0], "e": ts[1], "name": "M. Foster", "flags": "🇬🇧 → 🇰🇷",
                   "role": "Bear & Joy 공동 저자 · 영국 출신 선생님"})
        add(ts[0], "whoosh", -10)

    # Punch-zoom rhythm: alternate 100% / 108% on every caption, eased in over 0.12 s.
    zooms = []
    for k, c in enumerate(C):
        zooms.append({"t": c["s"], "z": 1.08 if k % 2 else 1.0})
        if k % 2:
            add(c["s"] - 0.06, "whoosh", -17)
    for g in out[1:]:
        add(g["out_s"] - 0.06, "whoosh", -12)
    ev.append({"type": "push", "s": max(0, speech_end - 2.5), "e": speech_end, "from": 1.0, "to": 1.1})

    total = round(speech_end + END_V2, 3)
    ev.append({"type": "end", "s": round(speech_end - 0.3, 3), "e": total})
    add(speech_end - 0.3, "impact", -8); add(speech_end, "sparkle", -10)
    end_s = speech_end - 0.3
    add(end_s + 0.6, "pop", -10); add(end_s + 0.8, "pop", -10)          # headline lines land
    add(end_s + 2.0, "pop", -6); add(end_s + 2.9, "pop", -6); add(end_s + 2.95, "chime", -9)  # follow taps
    # Beat stops on the end card hit and comes back for the outro.
    music["dropouts"].append([speech_end - 0.35, speech_end - 0.05]); music["drops"].append(speech_end - 0.05)
    ev.append({"type": "badge", "s": 0.0, "e": speech_end - 0.3, "day": DAY})

    plan = {"name": name, "fps": FPS, "duration": total, "frames": int(math.ceil(total * FPS)), "speechEnd": speech_end,
            "day": DAY, "segments": out, "captions": C, "events": ev, "zooms": zooms, "music": music,
            "sfx": sorted(sfx, key=lambda x: x["t"])}
    json.dump(plan, open(f"{HERE}/versions/{name}/timeline_v2.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{name}: {total:.1f}s, {len(C)} captions, {sum(e['type'] == 'pop' for e in ev)} pops, {len(sfx)} sfx")


if __name__ == "__main__":
    db = load_db(sys.argv[1])
    for n, s in VERSIONS.items():
        build(n, s, db)
