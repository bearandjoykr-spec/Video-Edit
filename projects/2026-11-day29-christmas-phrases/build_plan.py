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
    (37.58, 38.23, "blimey",    14.95, 15.85, 0.0, "Blimey.", "세상에."),
    (44.43, 44.93, "platform",  86.80, 89.10, 0.9, "All right, Percy. You first.", "자, 퍼시. 너부터 가렴."),
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
        segs.append({"kind": "film", "clip": clip, "src": f"day29/clips/{clip}.mp4", "clipIn": cs, "clipOut": ce,
                     "s": t, "e": t + d, "lineS": t + PAD, "en": en, "ko": ko}); t += d
        z = 0
END_CARD = 3.6
total = t + END_CARD

def out(x, end=False):
    marks = [s for s in segs if s["kind"] == "mark"]
    for s in marks:
        if s["src"] - 1e-6 <= x <= s["srcEnd"] + 1e-6: return s["s"] + x - s["src"]
    if end:  # inside a removed gap: snap to the end of the piece before it
        return max(s["e"] for s in marks if s["srcEnd"] <= x)
    return min(s["s"] for s in marks if s["src"] >= x)

r = lambda v: round(v, 3)
films = [s for s in segs if s["kind"] == "film"]
phr = [{"s": r(out(a)), "n": n, "en": en, "ko": ko} for a, n, en, ko in PHRASES]
hook = {"s": 0.0, "e": r(out(7.78, True)), "strike": 0.85, "happy": 1.45,
        "top": "Why does Ron say…", "no": "Merry Christmas", "yes": "Happy Christmas?", "ko": "왜 ‘메리’가 아니라 ‘해피’ 크리스마스일까?"}
props = [{"dir": "day29/props-start", "srcFrom": 0.0, "frames": 237, "s": 0.0, "e": hook["e"], "poofIn": False},
         {"dir": "day29/props-end", "srcFrom": 53.9, "frames": 168, "s": r(out(54.6)), "e": r(out(MARK_END, True)) + 0.3, "poofIn": True}]
end_s = r(t)
# SFX cues for mix.py: whoosh into/out of every magic cut, chime on pops, sparkle on poofs, ding on the follow button
sfx = [{"t": 0.0, "k": "sparkle"}, {"t": hook["strike"], "k": "swish"}, {"t": hook["happy"], "k": "chime"}]
for s in films:
    sfx += [{"t": r(s["s"] - 0.18), "k": "whoosh"}, {"t": r(s["s"]), "k": "ding"}, {"t": r(s["e"] - 0.15), "k": "whoosh_out"}]
sfx += [{"t": p["s"], "k": "chime"} for p in phr]
sfx += [{"t": props[1]["s"], "k": "sparkle"}, {"t": r(end_s - 0.5), "k": "whoosh"}, {"t": r(end_s + 0.35), "k": "chime"},
        {"t": r(end_s + 1.6), "k": "ding"}]

plan = {
    "name": f"day29-{V}", "fps": FPS, "duration": r(total), "frames": int(round(total * FPS)), "day": 29,
    "background": "day29/great-hall.jpg", "props": props, "hook": hook,
    "cta": {"ko1": "새 해리 포터 시리즈", "ko2": "12월 25일 공개!", "q": "Is your English ready?", "qKo": "영어 준비됐나요?",
            "follow": "팔로우하고 함께 준비해요", "small": "The new Harry Potter series · 25 December"},
    "title": {"s": r(out(12.0)), "e": r(out(17.7, True)), "en": "5 Harry Potter Phrases",
              "sub": "to teach your child before Christmas", "ko": "크리스마스 전에 알려 줄 해리 포터 표현 5가지"},
    "segments": [{k: (r(v) if isinstance(v, float) else v) for k, v in s.items()} for s in segs],
    "captions": [{"s": r(out(a)), "e": r(out(b, True)), "en": en, "ko": ko} for a, b, en, ko in LINES],
    "phrases": phr, "endCard": {"s": end_s, "e": r(total)}, "sfx": sfx,
}
os.makedirs(f"{P}/versions/{V}", exist_ok=True)
json.dump(plan, open(f"{P}/versions/{V}/plan.json", "w"), ensure_ascii=False, indent=1)
print(f"{V}: {total:.2f} s, {plan['frames']} frames, {len(films)} film cuts, "
      f"{sum(s['kind'] == 'mark' for s in segs)} Mark pieces, {len(sfx)} SFX")
