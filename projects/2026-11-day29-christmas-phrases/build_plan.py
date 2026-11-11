"""Day 29 — Harry Potter phrases. Builds versions/<v>/plan.json for Remotion Day29Magic (+ SFX cues for mix.py).

History (owner feedback, 11 Nov 2026):
- v2: no clips behind Mark, no freezing; full-screen "magic cut" to the film line at a natural sentence break.
- v3: big opening hook, glasses + scar from frame 0 and at the sign-off, HP-series CTA + follow end card.
- v4: No. 5 now really says "Happy Christmas, Ron"; hand glitch fixed (fix_matte.py patch for 30–38.5 s);
      faster pace (jump cuts remove silences > 0.2 s in Mark's take, alternating 1.0/1.06 zoom to hide them;
      shorter film lines); magic SFX (whooshes, dings, sparkles); Korean-led CTA, "Is your English ready?" kept in English.
Cut points come from ffmpeg silencedetect (-35 dB), not Whisper word times (those ran ~0.35 s early).
Usage (repo root): python3 projects/2026-11-day29-christmas-phrases/build_plan.py [version]
"""
import json, os, re, subprocess, sys

V = sys.argv[1] if len(sys.argv) > 1 else "main"
import datetime
POST_DATE = datetime.date.fromisoformat(os.environ.get("POST_DATE", "2026-11-12"))  # day the reel goes up
DAYS_TO_GO = (datetime.date(POST_DATE.year, 12, 25) - POST_DATE).days
P = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(P))
FPS = 30
PAD = 0.22          # clip picture either side of the film line (covers the magic-cut transition)
KEEP = 0.09         # silence kept either side of a jump cut
MIN_GAP = 0.20      # silences longer than this get cut

# (Mark stops, Mark resumes, clip, line in, line out, extra picture after the line, EN, KO)
FILMS = [
    (7.78, 8.78,  "christmas", 15.30, 16.60, 0.0, "Happy Christmas, Harry!", "해피 크리스마스, 해리!"),
    (24.31, 24.56, "christmas", 16.60, 17.65, 0.0, "Happy Christmas, Ron.", "해피 크리스마스, 론."),
    (29.97, 30.36, "brilliant", 15.00, 16.50, 0.0, "Brilliant!", "최고야!"),
    (37.58, 38.23, "blimey",    20.00, 21.15, 0.0, "Blimey, Hermione.", "세상에, 헤르미온느."),  # v5: Ron + Harry (14.95 was a troll)
    (44.43, 44.93, "platform",  92.30, 94.60, 0.0, "Off you gooooooo!", "자, 출바아아알!"),  # v6: silent barrier run (no one says "off you go" in the film)
    (53.89, 54.09, "map",      117.90, 119.60, 0.0, "Mischief managed.", "장난 완료."),
]
MARK_START, MARK_END = 0.62, 59.30
PATCHES = [(30.0, 38.5, "day29/subject-fix-blimey.webm")]  # repaired matte (fix_matte.py)

LINES = [
    (8.78, 11.60, "Because that's how we say it in Britain.", "영국에서는 그렇게 말하거든요."),
    (11.60, 17.90, "Five Harry Potter phrases to teach your child before Christmas Day.", "크리스마스 전에 아이에게 알려 줄 해리 포터 표현 5가지!"),
    (17.90, 21.34, "Number five, Happy Christmas.", "5번, 해피 크리스마스."),
    (21.34, 24.31, "Same meaning, more British.", "뜻은 같아요, 더 영국식일 뿐!"),
    (24.56, 27.05, "Four, Brilliant.", "4번, 브릴리언트."),
    (27.05, 29.97, "Not “good job” — brilliant.", "“잘했어” 말고, “최고야!”"),
    (30.36, 33.20, "Number three, Blimey.", "3번, 블라이미."),
    (33.20, 37.58, "For when the snow is this deep… Blimey.", "눈이 이만큼 쌓였을 때, “세상에!”"),
    (38.23, 40.65, "Two, Off you go.", "2번, 오프 유 고."),
    (40.65, 44.43, "Shoes on, coat on, off you go.", "신발 신고, 코트 입고, “자, 출발!”"),
    (44.93, 50.34, "And number one, for when the toys are finally tidied away…", "그리고 1번, 장난감을 다 정리했을 때…"),
    (50.34, 53.89, "(whisper) Mischief managed.", "(속삭이며) “장난 완료.”"),
    (54.09, 59.11, "Save this and try one tonight. Happy Christmas from Oxford.", "저장해 두고 오늘 밤 하나 써 보세요. 옥스퍼드에서, 해피 크리스마스!"),
]
PHRASES = [(17.90, 5, "Happy Christmas", "해피 크리스마스"), (24.56, 4, "Brilliant", "최고야!"),
           (30.36, 3, "Blimey", "세상에!"), (38.23, 2, "Off you go", "자, 출발!"), (44.93, 1, "Mischief managed", "장난 완료")]

# silences in Mark's take
log = subprocess.run(["ffmpeg", "-v", "info", "-i", f"{R}/raw-footage/day29/audio16k.wav", "-af", "silencedetect=noise=-35dB:d=0.15",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]; se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
gaps = [(a + KEEP, b - KEEP) for a, b in zip(ss, se) if b - a > MIN_GAP]

def pieces(a, b):
    """split Mark source range a..b at long silences and at matte-patch borders"""
    cuts = [(a, b)]
    for g0, g1 in gaps:
        nxt = []
        for x0, x1 in cuts:
            if g0 > x0 + 0.05 and g1 < x1 - 0.05: nxt += [(x0, g0), (g1, x1)]
            else: nxt.append((x0, x1))
        cuts = nxt
    out = []
    for x0, x1 in cuts:
        pts = sorted({x0, x1, *[p for pa, pb, _ in PATCHES for p in (pa, pb) if x0 < p < x1]})
        out += list(zip(pts[:-1], pts[1:]))
    return out

def subject_for(x0):
    for pa, pb, f in PATCHES:
        if pa <= x0 < pb: return f, pa
    return "day29/subject.webm", 0.0

segs, t, src, z = [], 0.0, MARK_START, 0
ranges = []
for stop, resume, *_ in FILMS:
    ranges.append((src, stop)); src = resume
ranges.append((src, MARK_END))
for k, (a, b) in enumerate(ranges):
    prev_end = None
    for x0, x1 in pieces(a, b):
        if prev_end is not None and x0 - prev_end > 0.01: z ^= 1   # jump cut → change framing
        f, off = subject_for(x0)
        segs.append({"kind": "mark", "src": x0, "srcEnd": x1, "file": f, "fileFrom": off, "zoom": 1.06 if z else 1.0,
                     "s": t, "e": t + x1 - x0}); t += x1 - x0; prev_end = x1
    if k < len(FILMS):
        _, _, clip, cs, ce, tail, en, ko = FILMS[k]
        d = PAD + (ce - cs) + tail + PAD
        segs.append({"kind": "film", "clip": clip, "src": f"day29/clips/{clip}.mp4", "clipIn": cs, "clipOut": ce, "silent": clip == "platform", "big": clip == "platform",
                     "s": t, "e": t + d, "lineS": t + PAD, "en": en, "ko": ko}); t += d
        z = 0
END_CARD = 4.8   # v6: + "comment your favourite phrase" line
total = t + END_CARD

def out(x, end=False):
    marks = [s for s in segs if s["kind"] == "mark"]
    for s in marks:
        if s["src"] - 1e-6 <= x <= s["srcEnd"] + 1e-6: return s["s"] + x - s["src"]
    if end:  # inside a removed gap: snap to the end of the piece before it
        return max(s["e"] for s in marks if s["srcEnd"] <= x)
    return min(s["s"] for s in marks if s["src"] >= x)

# v5: per-word timing for the golden-snitch captions. Whisper word times drift, so spread each caption's words over
# the voiced audio inside its source range (silencedetect at a finer -35 dB / 0.08 s), weighted by word length.
log2 = subprocess.run(["ffmpeg", "-v", "info", "-i", f"{R}/raw-footage/day29/audio16k.wav", "-af", "silencedetect=noise=-35dB:d=0.08",
                       "-f", "null", "-"], capture_output=True, text=True).stderr
s2 = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log2)]; e2 = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log2)]
voiced = []; last = 0.0
for a_, b_ in zip(s2, e2):
    if a_ > last: voiced.append((last, a_))
    last = b_
voiced.append((last, 60.0))
def word_times(a, b, text):
    words = text.split()
    spoken = [w for w in words if not w.startswith("(")]
    iv = [(max(a, x), min(b, y)) for x, y in voiced if y > a and x < b]
    total = sum(y - x for x, y in iv) or (b - a)
    wts = [max(2, len(w.strip(".,!?…“”—"))) for w in spoken]; W_ = sum(wts)
    res, acc = [], 0.0
    for w, wt in zip(spoken, wts):
        tgt = acc / W_ * total; t0 = iv[0][0] if iv else a
        for x, y in iv:  # walk voiced intervals to the target offset
            if tgt <= y - x: t0 = x + tgt; break
            tgt -= y - x
        res.append(t0); acc += wt
    out_w, k = [], 0
    for w in words:
        if w.startswith("("): out_w.append({"w": w, "t": None})
        else: out_w.append({"w": w, "t": res[k]}); k += 1
    return out_w

r = lambda v: round(v, 3)
films = [s for s in segs if s["kind"] == "film"]
# v6: giant countdown number slams in on the spoken number word
NUM_LINE = {5: 2, 4: 4, 3: 6, 2: 8, 1: 10}
NUM_WORD = {5: "five", 4: "four", 3: "three", 2: "two", 1: "one"}
def num_time(n):
    a, b, en, _ = LINES[NUM_LINE[n]]
    return next(x["t"] for x in word_times(a, b, en) if x["w"].lower().strip(",.") == NUM_WORD[n])
phr = [{"s": r(out(a)), "num": r(out(num_time(n))), "n": n, "en": en, "ko": ko} for a, n, en, ko in PHRASES]
hook = {"s": 0.0, "e": r(out(7.78, True)), "strike": 0.85, "happy": 1.45,
        "top": "Why does Ron say…", "no": "Merry Christmas", "yes": "Happy Christmas?", "ko": "왜 ‘메리’가 아니라 ‘해피’ 크리스마스일까?"}
props = [{"dir": "day29/props-start", "srcFrom": 0.0, "frames": 237, "s": 0.0, "e": hook["e"], "poofIn": False},
         {"dir": "day29/props-end", "srcFrom": 53.9, "frames": 168, "s": r(out(54.6)), "e": r(out(MARK_END, True)) + 0.3, "poofIn": True}]
end_s = r(t)
britain = next(x["t"] for x in word_times(8.78, 11.60, LINES[0][2]) if x["w"].startswith("Britain"))
# SFX cues for mix.py: whoosh into/out of every magic cut, chime on pops, sparkle on poofs, ding on the follow button
sfx = [{"t": 0.0, "k": "sparkle"}, {"t": hook["strike"], "k": "swish"}, {"t": hook["happy"], "k": "chime"}]
for s in films:
    sfx += [{"t": r(s["s"] - 0.18), "k": "whoosh"}, {"t": r(s["s"]), "k": "ding"}, {"t": r(s["e"] - 0.15), "k": "whoosh_out"}]
sfx += [{"t": r(p["num"] - 0.02), "k": "boom"} for p in phr] + [{"t": r(p["num"] + 0.5), "k": "chime"} for p in phr]
sfx += [{"t": r(out(britain)), "k": "ding"}]
for f_ in films:  # v7: rising magic swirl + sparkle as "Off you gooooooo!" stretches out
    if f_["clip"] == "platform": sfx += [{"t": r(f_["lineS"]), "k": "rise"}, {"t": r(f_["lineS"] + 1.7), "k": "sparkle"}]
sfx += [{"t": props[1]["s"], "k": "sparkle"}, {"t": r(end_s - 0.5), "k": "whoosh"}, {"t": r(end_s + 0.35), "k": "chime"},
        {"t": r(end_s + 1.6), "k": "ding"}, {"t": r(end_s + 2.3), "k": "sparkle"}]

plan = {
    "name": f"day29-{V}", "fps": FPS, "duration": r(total), "frames": int(round(total * FPS)), "day": 29,
    "background": "day29/great-hall.jpg", "props": props, "hook": hook,
    "cta": {"ko1": "새 해리 포터 시리즈", "ko2": "12월 25일 공개!", "q": "Is your English ready?", "qKo": "영어 준비됐나요?",
            "follow": "팔로우하고 함께 준비해요", "small": "The new Harry Potter series · 25 December",
            "comment": "가장 좋아하는 해리 포터 표현은? 댓글로 알려 주세요 👇", "commentEn": "Comment your favourite Harry Potter phrase!"},
    "title": {"s": r(out(12.0)), "e": r(out(17.7, True)), "en": "5 Harry Potter Phrases",
              "sub": "to teach your child before Christmas", "ko": "크리스마스 전에 알려 줄 해리 포터 표현 5가지"},
    "segments": [{k: (r(v) if isinstance(v, float) else v) for k, v in s.items()} for s in segs],
    "captions": [{"s": r(out(a)), "e": r(out(b, True)), "en": en, "ko": ko,
                  "words": [{"w": x["w"], "t": (r(out(x["t"])) if x["t"] is not None else None)} for x in word_times(a, b, en)]}
                 for a, b, en, ko in LINES],
    "flags": [{"s": r(out(britain)), "e": r(out(britain) + 1.9), "emoji": "🇬🇧"}],
    "phrases": phr, "endCard": {"s": end_s, "e": r(total)}, "sfx": sfx,
    # v8 (owner): series is now "Christmas Countdown" with days to go (posting date → D-n), not "DAY 29"
    "series": {"en": "Christmas Countdown", "ko": "크리스마스 카운트다운", "dday": f"D-{DAYS_TO_GO}"},
    "capFont": os.environ.get("CAPFONT", "fell"),
}
os.makedirs(f"{P}/versions/{V}", exist_ok=True)
json.dump(plan, open(f"{P}/versions/{V}/plan.json", "w"), ensure_ascii=False, indent=1)
print(f"{V}: {total:.2f} s, {plan['frames']} frames, {len(films)} film cuts, "
      f"{sum(s['kind'] == 'mark' for s in segs)} Mark pieces, {len(sfx)} SFX")
