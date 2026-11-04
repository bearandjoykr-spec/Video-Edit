"""Day 24 edit plan: "아이 영어, 무조건 어릴 때?" — snappy, Korean-only captions.

Usage: python3 build.py AUDIO_16K_WAV
Writes versions/main/timeline_v2.json (same schema the BearJoyReelV2 template reads, plus
Korean word-by-word caption timing, pull-back camera moves, kicker lines and slot layout).
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-confidence"))
from build_timeline import load_db, snap  # noqa: E402

FPS, DAY, END = 30, 24, 3.0
MAX_CHUNK = 22  # Korean characters per caption page (shown on two lines; no spaces counted)

# --- script & whisper words -----------------------------------------------------
lines = []
for ln in open(f"{HERE}/script.txt", encoding="utf8"):
    if not ln.strip() or ln.startswith("#"):
        continue
    cut = ln.startswith("-")
    s, e, ko = ln.lstrip("-").rstrip("\n").split("|", 2)
    lines.append({"s": float(s), "e": float(e), "ko": ko.strip(), "cut": cut})


def srt(fn):
    out = []
    for b in open(fn, encoding="utf8").read().strip().split("\n\n"):
        l = b.split("\n")
        if len(l) < 3 or "-->" not in l[1]:
            continue
        t = [int(a) * 3600 + int(b) * 60 + int(c) + int(d) / 1000 for a, b, c, d in re.findall(r"(\d+):(\d+):(\d+),(\d+)", l[1])]
        out.append({"w": " ".join(l[2:]).strip(), "s": t[0], "e": t[1]})
    return out


wwords = srt(f"{HERE}/words-ko.srt")
clean = lambda s: re.sub(r"[^0-9A-Za-z가-힣]", "", s)


def word_times(line):
    """Time each word of a script line by mapping character positions onto whisper's words."""
    ws = [w for w in wwords if line["s"] - 0.25 <= w["s"] < line["e"] - 0.05]
    pts = []  # (fraction of whisper chars, time)
    total = sum(len(clean(w["w"])) for w in ws) or 1
    acc = 0
    for w in ws:
        pts.append((acc / total, w["s"])); acc += len(clean(w["w"]))
    pts.append((1.0, line["e"]))
    if pts[0][0] > 0 or not ws:
        pts.insert(0, (0.0, line["s"]))

    def at(frac):
        for (f0, t0), (f1, t1) in zip(pts, pts[1:]):
            if f0 <= frac <= f1:
                return t0 + (t1 - t0) * ((frac - f0) / (f1 - f0) if f1 > f0 else 0)
        return line["e"]

    toks = line["ko"].split()
    n = sum(len(clean(t)) for t in toks) or 1
    out, acc = [], 0
    for t in toks:
        out.append({"w": t, "t": round(max(line["s"], at(acc / n)), 3)}); acc += len(clean(t))
    return out


# Gold word per line (substring) — the idea that carries the sentence
HI = {0: "무조건 어릴 때", 1: "사실일까요?", 2: "구별", 3: "민감해지는", 4: "'지각적 협소화'", 5: "아니에요.",
      6: "집에서", 7: "소통하는 경험", 8: "손동작", 9: "가리키며", 10: "연결하고,", 11: "경험하느냐예요.", 12: "막막하시죠?",
      13: "베어앤조이가", 14: "7일 홈 잉글리시", 15: "5분에서 10분,", 16: "즐겁게", 17: "팔로우하고", 18: "리틀 스텝스를", 19: "안녕!"}

# Big words behind her head, revealed by a camera pull-back (source seconds)
BEHIND = [
    {"kicker": "아이 영어는", "ko": "무조건 어릴 때?", "s": 0.09, "e": 3.99, "size": 150},
    {"kicker": "늦으면 끝?", "ko": "아니에요!", "s": 24.10, "e": 26.02, "size": 190},
    {"kicker": "더 중요한 건", "ko": "경험!", "s": 50.03, "e": 51.83, "size": 230},
]
# Key-point pops (source s, e, kicker, text, slot, sound)
POPS = [
    (4.36, 6.40, "", "🤔 진짜일까?", "mid", "boing"),
    (7.20, 11.38, "생후 초기", "모든 소리 구별 👂", "mid", "pop"),
    (11.63, 18.33, "생후 6~12개월", "익숙한 소리에 집중 🎯", "mid", "pop"),
    (19.31, 22.39, "이걸 부르는 말", "지각적 협소화 🧠", "mid", "sparkle"),
    (25.94, 29.21, "", "🏠 집에서는?", "mid", "pop"),
    (30.84, 34.91, "핵심", "📺 틀어두기 ≠ 💬 소통", "mid", "boing"),
    (35.82, 37.67, "TIP 1", "🎵 노래 + 손동작 👐", "mid", "pop"),
    (37.81, 40.98, "TIP 2", "📖 그림 가리키며 이야기 👉", "mid", "pop"),
    (41.30, 46.00, "", "👂 듣고 · 👀 보고 · 💬 반응", "mid", "pop"),
    (52.67, 54.52, "", "😵 막막하시죠?", "mid", "boing"),
    (55.41, 57.32, "그래서 베어앤조이가", "준비했어요 🎁", "mid", "sparkle"),
    (60.27, 62.39, "", "📚 7일 홈 잉글리시", "mid", "pop"),
    (63.00, 64.45, "하루", "5~10분 ⏱️", "mid", "pop"),
    (64.49, 68.03, "", "📖 그림책 + 놀이 🧸", "mid", "pop"),
    (68.80, 70.66, "", "😊 즐겁게 시작!", "mid", "pop"),
    (73.20, 76.96, "👆 프로필 링크", "Little Steps 🐾", "mid", "sparkle"),
]
AVATAR = {"s": 58.30, "e": 60.20, "img": "brand/mark-avatar.png", "kicker": "영국인 교사", "text": "🇬🇧 마크 선생님"}
FOLLOW = (70.90, 72.64)  # she says "팔로우하고 지켜봐주세요" — show the follow button right then
TWIST = (4.36, 6.94)     # "그런데 이 말 어디까지 사실일까요?" — beat stops, record scratch
TAG = {"s": 7.00, "e": 11.28, "name": "Joy Kim", "flags": "🇰🇷", "role": "Bear & Joy 공동 저자"}
SLOTS = {"mid": {"left": 0, "right": 0, "top": 950, "rot": -2}}  # below chin and mic, above captions
TAG_POS = {"left": 50, "top": 1450}  # under the captions
CAPTION_TOP = 1250


# Versions: which script lines (0-based, in script order) each cut keeps. None = every line not marked "-".
VERSIONS = {
    "main": None,  # follows the owner's script in full
    # tight (~48 s) for reach: hook + twist, one fact, the payoff, key point, both tips, "경험", the pitch, CTA
    "tight": [0, 1, 2, 5, 7, 8, 9, 11, 12, 13, 14, 17, 18, 19],
}


def build(db, name="main"):
    sel = VERSIONS[name]
    use = lambda idx, l: (not l["cut"]) and (sel is None or idx in sel)
    keep = [l for idx, l in enumerate(lines) if use(idx, l)]
    # segments: each kept sentence, padded, snapped to the quietest moment; merge if the gap is tiny
    segs = []
    for l in keep:
        s = snap(max(0, l["s"] - 0.06), db, 0.12, 0.0); e = snap(l["e"] + 0.04, db, 0.0, 0.16)
        if segs and s - segs[-1][1] < 0.12:
            segs[-1] = (segs[-1][0], e)
        else:
            segs.append((s, e))
    out, t = [], 0.0
    for s, e in segs:
        out.append({"src_s": round(s, 3), "src_e": round(e, 3), "out_s": round(t, 3)}); t += e - s
    speech_end = round(t, 3)

    def to_out(x):
        for g in out:
            if g["src_s"] - 1e-6 <= x <= g["src_e"] + 1e-6:
                return round(g["out_s"] + x - g["src_s"], 3)
        best = min(out, key=lambda g: min(abs(x - g["src_s"]), abs(x - g["src_e"])))
        return round(best["out_s"] + (0 if x < best["src_s"] else best["src_e"] - best["src_s"]), 3)

    def inside(s, e, min_len=0.4):
        """True when a source-time event overlaps the kept footage by at least min_len seconds."""
        return any(min(e, g["src_e"]) - max(s, g["src_s"]) >= min_len for g in out)

    # captions: split each line into chunks of <= MAX_CHUNK characters at word boundaries
    C = []
    for idx, l in enumerate(lines):
        if not use(idx, l):
            continue
        wt = word_times(l)
        chunk = []
        def flush(nxt_t):
            if not chunk:
                return
            text = " ".join(w["w"] for w in chunk)
            hi = HI.get(idx, "")
            hi_in = hi if hi and hi in text else next((p for p in hi.split() if p in text and len(clean(p)) > 1), "") if hi else ""
            C.append({"i": idx, "s": to_out(chunk[0]["t"]), "e": to_out(nxt_t), "ko": text, "en": "", "hi": hi_in, "demo": False,
                      "kwords": [{"w": w["w"], "t": to_out(w["t"])} for w in chunk], "words": []})
        # " / " in the script forces a page break at a natural pause
        if " / " in l["ko"]:
            for w in wt:
                if w["w"] == "/":
                    flush(w["t"]); chunk = []
                else:
                    chunk.append(w)
            flush(l["e"]); chunk = []
            continue
        # balanced pages: as few pages as fit MAX_CHUNK, each about the same length (no orphan tails)
        total = sum(len(clean(w["w"])) for w in wt)
        pages = 1 if idx == 0 else max(1, math.ceil(total / MAX_CHUNK))  # the hook stays one page
        target = total / pages
        acc = 0
        for k, w in enumerate(wt):
            n = len(clean(w["w"]))
            page_no = min(pages - 1, int((acc + n / 2) // target))
            if chunk and page_no > len([c for c in C if c["i"] == idx]):
                flush(w["t"]); chunk = []
            chunk.append(w); acc += n
        flush(l["e"]); chunk = []
    # never show a caption for less than 0.9 s if the next one allows a hold; close tiny gaps
    for a, b in zip(C, C[1:]):
        if 0 < b["s"] - a["e"] < 0.5:
            a["e"] = b["s"]
    for c in C:
        c["s"] = max(0, c["s"] - 0.08)  # appear a hair before the words (owner feedback: reading speed)

    ev, sfx = [], []
    add = lambda tt, s, g: sfx.append({"t": round(max(0, tt), 3), "sound": s, "gain": g})
    for k, b in enumerate(BEHIND):
        if not inside(b["s"], b["e"]):
            continue
        s, e = to_out(b["s"]), to_out(b["e"])
        ev.append({"type": "behind", "ko": b["ko"], "en": b["kicker"], "size": b["size"], "top": 330, "s": s, "e": e, "k": k})
        ev.append({"type": "pull", "s": s - 0.12, "e": e, "z": 0.74})
        add(s - 0.15, "whoosh", -9); add(s, "impact", -7); add(s + 0.05, "sparkle", -13)
    for k, (s, e, kick, text, slot, snd) in enumerate(POPS):
        if not inside(s, e):
            continue
        ev.append({"type": "pop", "s": to_out(s), "e": to_out(e), "text": text, "kicker": kick, "slot": slot, "k": k + 1})
        add(to_out(s), snd, -9 if snd == "pop" else -11)
        ev.append({"type": "punch", "s": to_out(s), "e": to_out(s) + 0.25, "z": 1.035, "shake": 5})
    if inside(AVATAR["s"], AVATAR["e"]):
        ev.append({"type": "avatar", **{k: v for k, v in AVATAR.items() if k not in ("s", "e")}, "s": to_out(AVATAR["s"]), "e": to_out(AVATAR["e"]), "slot": "mid"})
        add(to_out(AVATAR["s"]), "pop", -8)
    fs, fe = to_out(FOLLOW[0]), to_out(FOLLOW[1])
    ev.append({"type": "follow", "s": fs, "e": fe + 0.15, "tap1": fs + 0.55, "tap2": fs + 1.15})
    add(fs, "whoosh", -10); add(fs + 0.55, "pop", -6); add(fs + 1.15, "pop", -6); add(fs + 1.2, "chime", -9)
    ts, te = to_out(TWIST[0]), to_out(TWIST[1])
    ev.append({"type": "punch", "s": ts, "e": te - 0.1, "z": 1.14, "shake": 4, "hold": True})
    add(ts - 0.3, "scratch", -6)
    ev.append({"type": "tag", "s": to_out(TAG["s"]), "e": to_out(TAG["e"]), **{k: v for k, v in TAG.items() if k not in ("s", "e")}})
    add(to_out(TAG["s"]), "whoosh", -12)

    zooms = []
    for k, c in enumerate(C):
        zooms.append({"t": c["s"], "z": 1.07 if k % 2 else 1.0})
    for g in out[1:]:
        add(g["out_s"] - 0.05, "whoosh", -15)
    total = round(speech_end + END, 3)
    ev.append({"type": "end", "s": round(speech_end - 0.2, 3), "e": total, "short": True,
               "share": "💌 아이 영어 고민하는 부모님께 공유해 주세요"})
    ev.append({"type": "badge", "s": 0.0, "e": speech_end - 0.2, "day": DAY})
    add(speech_end - 0.2, "impact", -8); add(speech_end, "sparkle", -10)
    music = {"dropouts": [[ts - 0.05, te - 0.05], [speech_end - 0.3, speech_end - 0.05]], "drops": [te - 0.05, speech_end - 0.05]}

    plan = {"name": f"day24-{name}", "media": f"day24/{name}", "fps": FPS, "duration": total, "frames": int(math.ceil(total * FPS)), "speechEnd": speech_end,
            "day": DAY, "segments": out, "captions": C, "events": ev, "zooms": zooms, "music": music,
            "slots": SLOTS, "tagPos": TAG_POS, "scrim": True, "captionTop": CAPTION_TOP, "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/{name}", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/{name}/timeline_v2.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{name}: {total:.1f}s ({speech_end:.1f}s speech, {len(out)} segments), {len(C)} caption chunks, "
          f"{sum(e['type'] == 'pop' for e in ev)} pops, {len(sfx)} sfx")
    for c in C:
        n = len(clean(c["ko"])); d = c["e"] - c["s"]
        flag = "  <-- short" if d < 1.4 else ""
        print(f"  {c['s']:6.2f} {d:4.2f}s {n:2d}자 {n / max(d, .01):4.1f}/s {c['ko']}{flag}")


if __name__ == "__main__":
    db = load_db(sys.argv[1])
    for n in VERSIONS:
        build(db, n)
