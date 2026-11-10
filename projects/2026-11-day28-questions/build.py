"""Day 28 edit plan: "아이가 영어로 대답을 안 해요" — three ways to talk with a child in English.

Usage: .venv/bin/python projects/2026-11-day28-questions/build.py raw-footage/joy-questions/audio16k.wav
Writes versions/main/timeline_v2.json for BearJoyReelV2 (same schema as Day 24, plus "mark" captions:
Mark's recorded English lines in Playfair Display italic, with his avatar, a UK flag and the Korean translation).
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-confidence"))
from build_timeline import load_db, snap  # noqa: E402

FPS, DAY, END = 30, 28, 5.0
MAX_CHUNK = 24  # Korean characters per caption page

lines = []
for ln in open(f"{HERE}/script.txt", encoding="utf8"):
    if not ln.strip() or ln.startswith("#"):
        continue
    cut = ln.startswith("-")
    mark = ln.startswith("M")
    s, e, text = ln.lstrip("-M").rstrip("\n").split("|", 2)
    l = {"s": float(s), "e": float(e), "cut": cut, "mark": mark}
    if mark:
        l["en"], l["ko"] = [x.strip() for x in text.split(" / ", 1)]
    else:
        l["ko"] = text.strip()
    lines.append(l)


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
    """Time each word of a Korean line by mapping character positions onto whisper's words."""
    ws = [w for w in wwords if line["s"] - 0.25 <= w["s"] < line["e"] - 0.05 and clean(w["w"])]
    pts, total, acc = [], sum(len(clean(w["w"])) for w in ws) or 1, 0
    for w in ws:
        pts.append((acc / total, max(line["s"], w["s"]))); acc += len(clean(w["w"]))
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
        out.append({"w": t, "t": round(min(line["e"] - 0.1, max(line["s"], at(acc / n))), 3)}); acc += len(clean(t))
    return out


def en_times(line):
    """Mark's English: spread words over the spoken span by vowel groups (a fair proxy for syllables)."""
    toks = line["en"].split()
    syl = [max(1, len(re.findall(r"[aeiouy]+", w.lower()))) + (0.6 if re.search(r"[?!.,]$", w) else 0) for w in toks]
    span, tot, acc, out = line["e"] - line["s"] - 0.15, sum(syl), 0, []
    for w, n in zip(toks, syl):
        out.append({"w": w, "t": round(line["s"] + span * acc / tot, 3)}); acc += n
    return out


# Yellow highlight word per Korean line (index in script order)
HI = {0: "한 단어로", 1: "방식", 2: "세 가지", 3: "선택지", 5: "바꿔보세요.", 7: "파란색을", 9: "손짓으로", 10: "행동으로", 11: "블록 놀이를",
      15: "찾고", 17: "발견했을", 19: "괜찮아요.", 20: "언어 경험", 21: "확장해", 22: '"Car!"라고', 26: "새로운 표현", 27: "정답을 확인하는",
      28: "자연스럽게", 29: "꼭 한번", 30: "공유해"}

# Big words behind Joy's head, revealed by a camera pull-back (source seconds)
BEHIND = [
    {"kicker": "영어로 대답 안 해도", "ko": "괜찮아요!", "s": 68.55, "e": 70.95, "size": 250, "lift": 60},
]
# Key-point pops (source s, e, kicker, text, slot, sound)
# The hook (Joy, 10 Nov 2026): no blurred pull-back, so the first frame works as the thumbnail.
# A big word in front of the sharp, full-frame picture, between the mic and the captions.
# Joy: no DAY badge over the hook (it covered her face), no emoji, a bigger first line.
HOOK = {"s": 0.03, "e": 6.00, "kicker": "영어로 물어보면", "text": "묵묵부답?", "size": 190, "kickerSize": 108}
POPS = [
    (9.00, 11.30, "질문 더 많이 ❌", "말하는 방식 🔄", "mid", "boing"),
    (14.40, 16.70, "유아 영어 수업에서 쓰는", "대화법 3가지 💬", "mid", "sparkle"),
    (17.24, 20.90, "방법 1", "정답 대신 선택지 🔴🔵", "mid", "pop"),
    (38.40, 41.50, "", "👉 손짓도 대답이에요", "mid", "pop"),
    (42.05, 45.30, "방법 2", "말 대신 행동으로 🧱", "mid", "pop"),
    (71.41, 75.90, "", "👂 듣고 · 🔍 찾고 · 🏃 움직이고", "mid", "pop"),
    (76.50, 79.45, "방법 3", "짧은 대답 확장 ➕", "mid", "pop"),
    (81.20, 83.55, "", "🚗 Car!", "mid", "boing"),
    (99.30, 102.20, "", "질문 공세 ❌", "mid", "boing"),
    (104.80, 108.40, "", "💬 반응을 이어주기", "mid", "pop"),
    (109.01, 112.90, "", "✅ 오늘 놀 때 바로!", "mid", "sparkle"),
]
TAG = {"s": 6.41, "e": 8.90, "name": "Joy Kim", "flags": "🇰🇷", "role": "Bear & Joy 공동 저자"}
MARK = {"img": "brand/mark-avatar.png", "name": "Mark", "flags": "🇬🇧"}
SLOTS = {"mid": {"left": 0, "right": 0, "top": 950, "rot": -2}, "hook": {"left": 0, "right": 0, "top": 820, "rot": -3}}  # below chin and mic, above captions
TAG_POS = {"left": 50, "top": 1480}
CAPTION_TOP = 1250

VERSIONS = {"main": None}


def build(db, name="main"):
    keep = [l for l in lines if not l["cut"]]
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

    # captions
    C = []
    for idx, l in enumerate(lines):
        if l["cut"]:
            continue
        if l["mark"]:
            C.append({"i": idx, "s": to_out(l["s"]), "e": to_out(l["e"]), "ko": l["ko"], "en": l["en"], "hi": "", "demo": False,
                      "mark": True, "words": [{"w": w["w"], "t": to_out(w["t"])} for w in en_times(l)], "kwords": []})
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
        if " /" in l["ko"]:
            # the page break lands on the quietest moment near its estimated time (a real pause)
            k = next(j for j, w in enumerate(wt) if w["w"].startswith("/"))
            at = wt[k]["w"][2:]  # "/@14.35" pins the break to a source time
            brk = snap(float(at), db, 0.1, 0.1) if at else snap(wt[k]["t"], db, 0.9, 0.9)
            wt[k]["w"] = "/"
            for j, w in enumerate(wt):
                w["t"] = min(w["t"], brk - 0.12) if j < k else max(w["t"], brk)
            for w in wt:
                if w["w"] == "/":
                    flush(brk); chunk = []
                else:
                    chunk.append(w)
            flush(l["e"]); chunk = []
            continue
        total = sum(len(clean(w["w"])) for w in wt)
        pages = 1 if idx == 0 else max(1, math.ceil(total / MAX_CHUNK))  # the hook stays one page
        target, acc, n_pages = total / pages, 0, 0
        for w in wt:
            n = len(clean(w["w"]))
            page_no = min(pages - 1, int((acc + n / 2) // target))
            if chunk and page_no > n_pages:
                flush(w["t"]); chunk = []; n_pages += 1
            chunk.append(w); acc += n
        flush(l["e"]); chunk = []
    C.sort(key=lambda c: c["s"])
    for a, b in zip(C, C[1:]):
        if 0 < b["s"] - a["e"] < 0.6:
            a["e"] = b["s"]
    for c in C:
        c["s"] = max(0, c["s"] - 0.08)
    # Joy (10 Nov): the long first sentence is too much for the hook; only the big title stays on screen
    C = [c for c in C if c["i"] != 0]
    # reading speed (owner, Day 23): a fast Korean page borrows up to 0.45 s from the page before it
    for a, b in zip(C, C[1:]):
        n = len(clean(b["ko"]))
        if n / (b["e"] - b["s"]) > 6.0:
            give = max(0.0, min(0.45, (a["e"] - a["s"]) - max(1.5, len(clean(a["ko"])) / 5.0)))
            b["s"] = round(b["s"] - give, 3); a["e"] = b["s"]

    ev, sfx = [], []
    add = lambda tt, s, g: sfx.append({"t": round(max(0, tt), 3), "sound": s, "gain": g})
    for k, b in enumerate(BEHIND):
        s, e = to_out(b["s"]), to_out(b["e"])
        # Joy: a Bear & Joy cream background behind the pulled-back picture instead of blur
        ev.append({"type": "behind", "ko": b["ko"], "en": b["kicker"], "size": b["size"], "top": 250 - b["size"] - b.get("lift", 0), "s": s, "e": e, "k": k, "cream": True})
        ev.append({"type": "pull", "s": max(0, s - 0.12), "e": e, "z": 0.74, "bg": "#F5F0E6"})
        add(s - 0.15, "whoosh", -9); add(s, "impact", -7); add(s + 0.05, "sparkle", -13)
    ev.append({"type": "pop", "s": -0.3, "e": to_out(HOOK["e"]), "text": HOOK["text"], "kicker": HOOK["kicker"], "slot": "hook", "k": 0, "size": HOOK["size"], "kickerSize": HOOK["kickerSize"]})
    add(0.0, "impact", -7); add(0.05, "sparkle", -13)
    # more energy in the hook (Joy): a punch on "한 단어로", then a held punch-in with a record scratch on "아무 말도 하지 않나요?"
    ev.append({"type": "punch", "s": 2.70, "e": 2.95, "z": 1.06, "shake": 4})
    add(2.70, "pop", -9)
    ev.append({"type": "punch", "s": 4.36, "e": 5.95, "z": 1.16, "shake": 5, "hold": True})
    add(4.28, "scratch", -7)
    # Mark is introduced in the hook (Joy): a small face with a UK flag, so viewers know a British teacher speaks the English
    ev.append({"type": "markpill", "s": 0.5, "e": 6.0, "img": "brand/mark-avatar.png", "name": "마크 선생님 🇬🇧", "line": "영국인 선생님 발음으로 들어보세요", "top": 1240})
    add(0.5, "whoosh", -12)
    for k, (s, e, kick, text, slot, snd) in enumerate(POPS):
        ev.append({"type": "pop", "s": to_out(s), "e": to_out(e), "text": text, "kicker": kick, "slot": slot, "k": k + 1})
        add(to_out(s), snd, -9 if snd == "pop" else -11)
        ev.append({"type": "punch", "s": to_out(s), "e": to_out(s) + 0.25, "z": 1.035, "shake": 5})
    # Mark speaking: small avatar + UK flag rides on the caption; a soft pop when each line starts
    for c in C:
        if c.get("mark"):
            ev.append({"type": "mark", "s": c["s"], "e": c["e"], **MARK})
            add(c["s"], "pop", -12)
    ev.append({"type": "tag", "s": to_out(TAG["s"]), "e": to_out(TAG["e"]), **{k: v for k, v in TAG.items() if k not in ("s", "e")}})
    add(to_out(TAG["s"]), "whoosh", -12)

    zooms = [{"t": c["s"], "z": 1.07 if k % 2 else 1.0} for k, c in enumerate(C)]
    for g in out[1:]:
        add(g["out_s"] - 0.05, "whoosh", -15)
    total = round(speech_end + END, 3)
    ev.append({"type": "end", "s": round(speech_end - 0.2, 3), "e": total,
               "share": "💌 영어교육 고민하는 엄마 아빠에게 공유해 주세요"})
    ev.append({"type": "badge", "s": to_out(HOOK["e"]), "e": speech_end - 0.2, "day": DAY, "docked": True})
    add(speech_end - 0.2, "impact", -8); add(speech_end, "sparkle", -10)
    es = speech_end - 0.2
    add(es + 2.0, "pop", -6); add(es + 2.9, "pop", -6); add(es + 2.95, "chime", -9)  # end-card follow taps
    music = {"dropouts": [[speech_end - 0.3, speech_end - 0.05]], "drops": [speech_end - 0.05]}

    plan = {"name": f"day28-{name}", "media": f"day28/{name}", "fps": FPS, "duration": total, "frames": int(math.ceil(total * FPS)), "speechEnd": speech_end,
            "day": DAY, "segments": out, "captions": C, "events": ev, "zooms": zooms, "music": music,
            "slots": SLOTS, "tagPos": TAG_POS, "scrim": True, "captionTop": CAPTION_TOP, "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/{name}", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/{name}/timeline_v2.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{name}: {total:.1f}s ({speech_end:.1f}s speech, {len(out)} segments), {len(C)} captions, "
          f"{sum(e['type'] == 'pop' for e in ev)} pops, {len(sfx)} sfx")
    for c in C:
        txt = c["en"] if c.get("mark") else c["ko"]
        n = len(clean(c["ko"])); d = c["e"] - c["s"]
        flag = "  <-- fast" if (n / max(d, .01) > 6.5 or d < 1.2) else ""
        print(f"  {c['s']:6.2f} {d:4.2f}s {n:2d}자 {n / max(d, .01):4.1f}/s {'🇬🇧 ' if c.get('mark') else ''}{txt}{flag}")


if __name__ == "__main__":
    db = load_db(sys.argv[1])
    for n in VERSIONS:
        build(db, n)
