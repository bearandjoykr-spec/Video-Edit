"""Build the edit plan for each version of the confidence reel.

Reads captions.json (source-time captions) and writes versions/<name>/timeline.json
with segments to cut, captions and graphic events in edited time, and SFX cues.
Usage: python3 build_timeline.py AUDIO_16K_WAV
"""
import json, sys, wave, array, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
END_CARD = 3.6

caps = json.load(open(f"{HERE}/captions.json", encoding="utf8"))

# Gold highlight word per caption (index -> substring of the Korean line)
HI = {0: "영어 발음", 4: "굉장히 중요하게", 5: "억양", 7: "한국 부모님들", 9: "영국인", 13: "첫 번째 단계",
      16: "자신감", 18: "엉망", 19: "배고파요?", 21: "자신 있게", 23: "이해한다는", 25: "자신감",
      27: "실수해도 괜찮다는", 28: "평가받는", 31: "배우고 싶은 마음", 33: "재미있게", 34: "부담 없이,",
      36: "자신감", 37: "첫 번째 작은 걸음"}

VERSIONS = {
    "full": [(0.51, 4.20), (8.50, 18.16), (18.60, 38.48), (38.90, 87.70)],
    "short": [(0.51, 4.20), (42.78, 56.68), (64.30, 68.64), (76.06, 82.28), (86.24, 87.70)],
}

# Source-time graphic events
BEHIND = [  # word behind the head
    {"text": "Pronunciation?", "s": 0.51, "e": 4.20, "style": "italic", "size": 138, "top": 600, "eyebrow": True},
    {"text": "Confidence", "s": 43.6, "e": 46.0, "style": "roman", "size": 165, "top": 485},
    {"text": "It's okay.", "s": 66.6, "e": 69.0, "style": "italic", "size": 210, "top": 500},
]
KOREAN_DEMO = (49.44, 52.44)
CONF_PUSH = (42.78, 45.52)
CARD = {"s": 78.3, "e": 82.6, "rows": [("재미있게", "keep it fun", 79.6), ("즐겁게", "keep it happy", 80.6), ("부담 없이", "keep it light", 81.6)]}
TAG_FULL = (23.5, 30.3)
TAG_SHORT = (46.2, 49.4)


def load_db(path):
    wf = wave.open(path); a = array.array("h", wf.readframes(wf.getnframes()))
    hop = 160  # 10 ms
    return [20 * math.log10(math.sqrt(sum(x * x for x in a[i:i + hop]) / hop) / 32768 + 1e-9) for i in range(0, len(a) - hop, hop)]


def snap(t, db, before=0.15, after=0.0):
    """Move a cut point to the quietest 10 ms between t-before and t+after."""
    i0, i1 = int((t - before) * 100), int((t + after) * 100) + 1
    best = min(range(max(0, i0), min(len(db), i1)), key=lambda i: db[i])
    return round(best / 100, 2)


def build(name, segs, db):
    segs = [(snap(s, db, 0.15, 0.0) if k else s, snap(e, db, 0.0, 0.2)) for k, (s, e) in enumerate(segs)]
    out = []; t = 0.0
    for s, e in segs:
        out.append({"src_s": s, "src_e": e, "out_s": round(t, 3)}); t += e - s
    speech_end = t

    def to_out(x):
        for g in out:
            if g["src_s"] - 1e-6 <= x <= g["src_e"] + 1e-6:
                return round(g["out_s"] + x - g["src_s"], 3)
        return None

    def span(s, e):
        """Map a source span into edited time, clipped to the segment that holds most of it."""
        best = None
        for g in out:
            a, b = max(s, g["src_s"]), min(e, g["src_e"])
            if b - a > 0.05 and (best is None or b - a > best[1] - best[0]):
                best = (a, b)
        return (to_out(best[0]), to_out(best[1])) if best else None

    C = []
    for c in caps:
        sp = span(c["s"], c["e"])
        if not sp:
            continue
        C.append({"i": c["i"], "s": sp[0], "e": sp[1], "ko": c["ko"], "en": c["en"], "hi": HI.get(c["i"], ""),
                  "demo": c["i"] == 19})
    # Hold each caption until the next one starts (no flicker in small gaps).
    for a, b in zip(C, C[1:]):
        if 0 < b["s"] - a["e"] < 0.6:
            a["e"] = b["s"]

    events, sfx = [], []
    for bw in BEHIND:
        sp = span(bw["s"], bw["e"])
        if sp:
            events.append({"type": "behind", **{k: v for k, v in bw.items() if k not in ("s", "e")}, "s": sp[0], "e": sp[1]})
            sfx.append({"t": max(0, sp[0] - 0.25), "sound": "rise", "gain": -9})
    sp = span(*KOREAN_DEMO)
    if sp:
        events.append({"type": "zoom", "s": sp[0], "e": sp[1], "from": 1.12, "to": 1.12, "snap": True})
        sfx.append({"t": max(0, sp[0] - 0.12), "sound": "whoosh", "gain": -8})
        sfx.append({"t": sp[1] - 0.1, "sound": "whoosh", "gain": -12})
    sp = span(*CONF_PUSH)
    if sp:
        events.append({"type": "zoom", "s": sp[0], "e": sp[1] + 0.5, "from": 1.05, "to": 1.09, "snap": False})
    sp = span(CARD["s"], CARD["e"])
    if sp:
        rows = [{"ko": k, "en": en, "t": to_out(tt)} for k, en, tt in CARD["rows"]]
        events.append({"type": "card", "s": sp[0], "e": sp[1], "rows": rows})
        sfx.append({"t": sp[0], "sound": "page", "gain": -12})
        for r in rows:
            if r["t"] is not None:
                sfx.append({"t": r["t"], "sound": "chime", "gain": -14})
    tag = TAG_FULL if name == "full" else TAG_SHORT
    sp = span(*tag)
    if sp:
        events.append({"type": "tag", "s": sp[0], "e": sp[1], "name": "M. Foster", "role": "Bear & Joy 공동 저자",
                       "line": "Born in Oxford. Built in Seoul."})
        sfx.append({"t": sp[0], "sound": "page", "gain": -13})

    # Framing: alternate 100% / 105% at every segment start and every second caption,
    # with a soft whoosh when the framing jumps at a cut.
    zooms = []
    level = 1.0
    starts = sorted({g["out_s"] for g in out} | {c["s"] for k, c in enumerate(C) if k % 2 == 0})
    for k, st in enumerate(starts):
        level = 1.05 if k % 2 else 1.0
        zooms.append({"t": st, "z": level})
        if st in {g["out_s"] for g in out} and st > 0:
            sfx.append({"t": max(0, st - 0.08), "sound": "whoosh", "gain": -16})
    # final slow push-in before the end card
    events.append({"type": "zoom", "s": max(0, speech_end - 3), "e": speech_end, "from": 1.0, "to": 1.08, "snap": False})

    total = speech_end + END_CARD
    events.append({"type": "end", "s": speech_end - 0.4, "e": total})
    sfx.append({"t": speech_end - 0.2, "sound": "chime", "gain": -10})
    sfx.append({"t": speech_end + 0.6, "sound": "rise", "gain": -14})

    plan = {"name": name, "fps": FPS, "duration": round(total, 3), "frames": int(math.ceil(total * FPS)),
            "speechEnd": round(speech_end, 3), "segments": out, "captions": C, "events": events,
            "zooms": zooms, "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/{name}", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/{name}/timeline.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{name}: {len(out)} segments, speech {speech_end:.1f}s, total {total:.1f}s, {len(C)} captions, {len(sfx)} sfx")
    for g in out:
        print("   ", g)


if __name__ == "__main__":
    db = load_db(sys.argv[1])
    for n, s in VERSIONS.items():
        build(n, s, db)
