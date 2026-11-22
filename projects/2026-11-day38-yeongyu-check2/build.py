"""DAY 38 "영유 상담 전 꼭 확인할 3가지 (2편)" (Joy, 21 Nov 2026).
Joy's 2:32 talk, everything she says in order except a retake near the end and the closing "내일 만나요"; pauses ≥ 0.3 s shrink
to KEEP, then 1.1x speed (pitch kept). Captions are her spoken words (two lines). Different look from DAY 37: light "상담 노트" style —
the stock B-roll sits in a rounded window in the top half, the bottom half is warm paper where Joy's sticker stands.
Run (repo root): .venv/bin/python projects/2026-11-day38-yeongyu-check2/build.py
"""
import json, math, os, subprocess, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, WAV = "raw-footage/day38/main.mov", "raw-footage/day38/main16k.wav"
SPEED, FPS, KEEP = 1.1, 30, 0.14
ST = "raw-footage/day38/stock/"

SEGS = [
    ("hook", 0.25, 4.05, [(0.25, "우리 아이가 다니는 영유에서\n선생님이 자주 바뀐다면?")]),
    ("intro", 4.75, 10.70, [(4.75, "지난 영상에 이어, 오늘도"), (7.00, "영유 상담 때 꼭 확인해야 할\n세 가지 말씀드릴게요")]),
    ("p1", 11.15, 38.40, [(11.15, "첫 번째, 교사의 근속 기간"), (14.00, "아이들에게 선생님은 단순히\n영어를 가르치는 사람이 아니라"),
                         (17.40, "매일 만나고 관계를\n쌓아가는 사람이에요"), (20.80, "그런데 선생님이 자주 바뀐다면\n아이들은 새로운 선생님에게"),
                         (24.50, "적응하는 과정을\n반복해야 할 수도 있어요"), (27.80, "상담하실 때 선생님들이 평균적으로\n얼마나 오래 근무하시는지"),
                         (32.80, "교사가 바뀐다면 아이들의 특성과\n수업 내용은 어떻게 인수인계되는지"), (37.20, "꼭 물어보세요")]),
    ("p2", 39.45, 72.50, [(39.45, "두 번째, 교과서"), (41.30, "상담을 가면 '우리 원은\n미국 교과서를 사용한다'"),
                         (44.00, "혹은 '영국 교과서를 사용한다'는\n이야기를 들으실 수도 있어요"),
                         (49.10, "하지만 유명한 교과서를 쓴다고\n반드시 좋은 수업이 되는 건 아니에요"),
                         (54.50, "교과서 속 영어 문장을 읽고\n문제를 푸는 것과"), (58.50, "그 영어를 이해하고 일상에서\n사용하는 것은 다르거든요"),
                         (62.60, "그래서 어떤 교재를 쓰는지만\n확인하지 마시고"), (65.10, "그 교재로 어떤 활동을 하는지"),
                         (68.10, "배운 영어를 직접 써 볼 기회가\n얼마나 있는지 물어보세요")]),
    ("p3", 73.05, 100.60, [(73.05, "세 번째, 학원 운영진의 소통 방식"), (75.90, "이건 제가 근무하면서 정말\n중요하다고 느낀 부분이에요"),
                          (80.00, "학부모님의 의견이\n여러 사람을 거쳐 전달되면"), (83.30, "정작 수업하는 원어민 강사에게는\n내용이 다르게 전달되거나"),
                          (88.10, "문제가 충분히 해결되지 않는\n경우도 봤어요"), (91.60, "그래서 원장님이나 운영진이\n원어민 강사와 원활하게 소통하는지"),
                          (96.20, "학부모님의 의견이 실제 수업에\n어떻게 반영되는지 꼭 확인해 주세요")]),
    ("last", 101.35, 134.60, [(101.35, "그리고 꼭 말씀드리고 싶은 게 있어요"), (104.00, "영어를 배우기 위해 반드시\n영유를 다녀야 한다고 생각하진 않아요"),
                             (109.20, "하지만 모든 영유가\n같은 교육을 제공하는 것도 아니고"), (112.90, "아이마다 잘 맞는\n교육 환경도 다를 수 있어요"),
                             (116.80, "영유를 선택하신다면,\n혹은 이미 다니고 있다면"), (119.60, "유명한 교재나 화려한 시설보다"),
                             (123.10, "우리 아이가 매일 어떤 선생님과\n어떤 환경에서 시간을 보내는지"), (127.00, "확인해 주셨으면 좋겠어요"),
                             (129.00, "결국 중요한 건 어디에서\n영어를 배우느냐보다"), (132.00, "어떤 경험을 통해\n영어를 배우느냐니까요")]),
    ("end", 135.65, 144.45, [(135.65, "관련해서 더 궁금한 점이 있다면\n댓글로 남겨 주세요"),
                            (139.10, "제가, 혹은 원어민 마크가 경험했던\n이야기를 바탕으로 함께 나눠볼게요")]),
    ("bye", 149.85, 151.80, [(149.85, "그럼 내일 만나요, 안녕! 👋")]),   # Joy (22 Nov): keep her goodbye + a follow card
]
TICKS = {"p1": [27.80, 32.80], "p2": [65.10, 68.10], "p3": [91.60, 96.20]}
# fresh stock for DAY 38 (Pexels + Pixabay, STOCK.md) — each clip once
BG = {}  # filled by stock.json


def speech_mask():
    with wave.open(WAV) as f:
        a = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768; sr = f.getframerate()
    w = int(sr * .02); r = np.array([20 * np.log10(np.sqrt(np.mean(a[i:i + w] ** 2)) + 1e-9) for i in range(0, len(a) - w, w)])
    sp = r > np.percentile(r, 10) + 8
    i = 0
    while i < len(sp):           # fill gaps < 0.12 s inside words
        if not sp[i]:
            j = i
            while j < len(sp) and not sp[j]: j += 1
            if 0 < i and j < len(sp) and (j - i) * .02 < .12: sp[i:j] = True
            i = j
        else: i += 1
    return sp


SP = speech_mask()


def runs(min_len):
    """silent runs (start, end) in seconds, at least min_len long"""
    out, i = [], 0
    while i < len(SP):
        if not SP[i]:
            j = i
            while j < len(SP) and not SP[j]: j += 1
            if (j - i) * .02 >= min_len: out.append((i * .02, j * .02))
            i = j
        else: i += 1
    return out


def speech_end(b):
    """first silence of 0.2 s that starts after b - 0.3 → her voice has really stopped"""
    for a0, a1 in runs(.2):
        if a0 >= b - .3: return round(a0 + .1, 3)
    return b


def pauses():
    with wave.open(WAV) as f:
        a = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768; sr = f.getframerate()
    w = int(sr * .02); r = np.array([20 * np.log10(np.sqrt(np.mean(a[i:i + w] ** 2)) + 1e-9) for i in range(0, len(a) - w, w)])
    th = np.percentile(r, 10) + 14; sp = r > th; out, i = [], 0
    while i < len(sp):
        if not sp[i]:
            j = i
            while j < len(sp) and not sp[j]: j += 1
            if (j - i) * .02 >= .3: out.append((i * .02 + .03, j * .02 - .03))
            i = j
        else: i += 1
    return out


def main():
    global SEGS
    SEGS = [(sec, a, min(speech_end(b), b + .6, SEGS[k + 1][1] - .05) if k + 1 < len(SEGS) else min(speech_end(b), b + .6), cl) for k, (sec, a, b, cl) in enumerate(SEGS)]
    P = [(a0 + .1, a1 - .06) for a0, a1 in runs(.35)]; ps = []
    for sec, a, b, _ in SEGS:
        t = a
        for pa, pb in P:
            if a < pa and pb < b:
                ps.append((sec, t, pa + KEEP / 2)); t = pb - KEEP / 2
        ps.append((sec, t, b))
    starts, acc = [], 0.0
    for _, a, b in ps:
        starts.append(acc); acc += (b - a) / SPEED
    voice = acc

    def o(x):
        for (sec, a, b), s in zip(ps, starts):
            if a - 1e-6 <= x <= b + 1e-6:
                return round(s + (x - a) / SPEED, 3)
        best = min(range(len(ps)), key=lambda i: min(abs(x - ps[i][1]), abs(x - ps[i][2])))
        return round(starts[best] if x < ps[best][1] else starts[best] + (ps[best][2] - ps[best][1]) / SPEED, 3)

    # Joy (21 Nov): captions must not move on while she is still talking. Whisper word times run early, so every caption
    # boundary inside a segment snaps to the quietest 80 ms in [t-0.25, t+0.7] (the breath between her phrases).
    with wave.open(WAV) as f:
        au = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768; sr = f.getframerate()
    gaps = runs(.1)
    def snap(x):
        c = [g for g in gaps if x - .2 <= g[0] <= x + .9]
        return round(c[0][0] + min(.1, (c[0][1] - c[0][0]) / 2), 3) if c else round(x + .3, 3)
    caps = []
    for sec, a, b, cl in SEGS:
        cl = [(st if k == 0 else snap(st), text) for k, (st, text) in enumerate(cl)]
        for k, (st, text) in enumerate(cl):
            e = cl[k + 1][0] if k + 1 < len(cl) else b
            caps.append({"s": o(st), "e": round(o(e) - .02, 3), "text": text, "sec": sec})
    for sec, a, b, cl in SEGS:
        pass
    secs = [{"kind": sec, "s": o(a), "e": o(b)} for sec, a, b, _ in SEGS]
    for i in range(len(secs) - 1):
        secs[i]["e"] = secs[i + 1]["s"]
    total = round(voice + 2.6, 3); secs[-1]["e"] = total
    ticks = {k: [o(x) for x in v] for k, v in TICKS.items()}

    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    fc, n = [], len(ps)
    for i, (_, a, b) in enumerate(ps):
        fc.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d=0.012,afade=t=out:st={b - a - 0.015:.3f}:d=0.015[a{i}]")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca]")
    fc.append(f"[cv]setpts=PTS/{SPEED},fps={FPS}[v];[ca]atempo={SPEED},aresample=48000[a]")
    if not os.environ.get("BG_ONLY"):
     subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[v]", "-c:v", "h264_videotoolbox", "-b:v", "30M",
                    "-an", f"{HERE}/joy-src.mp4", "-map", "[a]", "-ac", "2", f"{HERE}/versions/main/voice.wav"], check=True)

    # background: each section's clips in order, each used once, 0.3 s dissolves
    bg = json.load(open(f"{HERE}/stock.json"))
    pub = f"{HERE}/../../remotion/public/day38"; os.makedirs(pub, exist_ok=True)
    shots = []
    for sc in secs:
        lst = bg[sc["kind"]]; per = (sc["e"] - sc["s"]) / len(lst)
        for i, sid in enumerate(lst):
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ST + sid + ".mp4"],
                                       capture_output=True, text=True).stdout)
            ss = max(0.0, min(1.0, dur - per - .8))
            shots.append((ST + sid + ".mp4", round(ss, 2), round(sc["s"] + i * per, 3), round(per, 3)))
    X = .3; ins, f2 = [], []
    for k, (src, ss, t0, d) in enumerate(shots):
        ins += ["-ss", f"{ss:.2f}", "-t", f"{d + X + .3:.2f}", "-i", src]
        f2.append(f"[{k}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={FPS},setsar=1,format=yuv420p,"
                  f"tpad=stop_mode=clone:stop_duration=3,trim=0:{d + X:.3f},setpts=PTS-STARTPTS[b{k}]")
    prev = "b0"
    for k in range(1, len(shots)):
        f2.append(f"[{prev}][b{k}]xfade=transition=fade:duration={X}:offset={shots[k][2]:.3f}[x{k}]"); prev = f"x{k}"
    f2.append(f"[{prev}]trim=0:{total},setpts=PTS-STARTPTS[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(f2), "-map", "[v]", "-c:v", "h264_videotoolbox", "-b:v", "16M", f"{pub}/bg.mp4"], check=True)

    plan = {"fps": FPS, "day": 38, "media": "day38", "duration": total, "frames": int(math.ceil(total * FPS)), "captions": caps, "sections": secs, "ticks": ticks,
            "sfx": [{"t": s["s"], "sound": "whoosh", "gain": -16} for s in secs[1:]] + [{"t": t, "sound": "pop", "gain": -15} for v in ticks.values() for t in v]}
    for p in (f"{HERE}/versions/main/plan.json", f"{HERE}/../../remotion/src/day38.json"):
        json.dump(plan, open(p, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s, {len(ps)} pieces, {len(caps)} captions, {len(shots)} shots")
    for s in secs:
        print(f"  {s['s']:6.2f}-{s['e']:6.2f} {s['kind']}")
    for c in caps:
        d = c["e"] - c["s"]; n2 = sum('가' <= ch <= '힣' for ch in c["text"])
        print(f"  {c['s']:6.2f} {d:4.2f}s {n2 / d:4.1f}/s {c['text']!r}")


if __name__ == "__main__":
    main()
