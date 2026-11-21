"""DAY 37 "영유 상담 때 꼭 확인할 3가지" (Joy, 21 Nov 2026).
Joy's 2:36 talking head is cut to its strongest lines (hook story → 3 checks → next-episode tease → comment ask),
pauses inside lines shortened, then sped up 1.1x (pitch kept) so it moves. Joy becomes a white-outlined sticker at the
bottom; the top half carries a checklist panel that fills in as she talks (save-worthy), with fair book footage behind
the textbook parts.
Run (repo root): .venv/bin/python projects/2026-11-day37-yeongyu-check/build.py
→ joy-src.mp4 (video for the matte), versions/main/voice.wav, versions/main/plan.json (+ remotion/src/day37.json)
"""
import json, math, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "raw-footage/day37/main.mov"
SPEED, FPS, KEEP = 1.1, 30, 0.14     # pauses ≥ 0.3 s inside a segment shrink to KEEP (source seconds)
# pauses measured on the audio (level below floor+14 dB), source seconds
PAUSES = [(3.84, 4.22), (6.02, 6.46), (36.22, 36.9), (37.34, 37.6), (41.62, 42.06), (65.2, 65.72), (75.84, 76.12), (79.98, 80.42),
          (98.12, 98.4), (107.1, 107.6), (109.26, 109.7), (139.38, 139.92), (142.3, 142.74), (144.76, 145.06), (147.08, 147.64),
          (122.0, 122.52), (124.46, 124.82), (126.92, 127.32), (130.1, 130.4)]
# Joy (21 Nov): under 30 s each, so the talk becomes TWO reels. Part 1 (DAY 37): the textbook story → check ①;
# Part 2 (DAY 38): checks ② and ③, opening on the native-teacher line. Background scenes are Pexels stock (STOCK.md).
# (section, src start, src end, [(src time, caption)])  — captions are Joy's own words, two lines max
PARTS = {
 1: [
    ("hook", 0.80, 8.80, [(0.80, "영유에 새로 들어온 아이가\n교재비는 다 냈는데"), (4.15, "정작 몇 페이지만 공부하고\n새 책 그대로 집에 가져간다면?")]),
    ("intro", 16.84, 20.56, [(16.84, "영유 상담 때 꼭 확인해야 할\n세 가지를 말씀드릴게요")]),
    ("p1", 21.12, 22.64, [(21.12, "첫 번째, 교재 진도")]),
    ("p1", 37.60, 45.06, [(37.60, "중간 입학이라면 지금 교재가\n어디까지 진행됐는지"), (41.54, "교재비는 어떻게 책정되는지\n꼭 확인해 보세요")]),
    ("end1", 150.54, 154.98, [(150.54, "영유에 대해 궁금한 점은\n댓글로 남겨 주세요"), (153.84, "그럼 안녕! 👋")]),
 ],
 3: None,   # filled below: one video with everything (Joy, 21 Nov: "두 개를 한 개로")
 2: [
    ("hook2", 61.30, 65.20, [(61.30, "영어가 모국어라고 해서\n어린아이를 잘 가르치는 건 아니에요")]),
    ("p2", 74.66, 83.42, [(74.66, "중요한 건 유아교육에 대한\n이해가 있는지"), (79.94, "아이들을 가르친 경험이\n얼마나 있는지예요")]),
    ("p3", 91.62, 93.64, [(91.62, "세 번째, 아이들의 하루 일과")]),
    ("p3", 94.30, 98.12, [(94.30, "'놀이형'이라고 해서\n무조건 뛰어놀기만 하는 건 아니에요")]),
    ("p3", 103.85, 113.50, [(103.85, "실제 우리 아이의\n시간표를 꼭 확인하시고"), (107.04, "얼마나 움직이는지, 자유롭게 노는\n시간은 충분한지 살펴보세요")]),
    ("end2", 150.54, 154.98, [(150.54, "영유에 대해 궁금한 점은\n댓글로 남겨 주세요"), (153.84, "그럼 안녕! 👋")]),
 ],
}
PARTS[3] = PARTS[1][:4] + [
    ("p2", 57.96, 60.72, [(57.96, "두 번째, 원어민 강사의 교육 경험")]),
    ("p2", 61.30, 65.20, [(61.30, "영어가 모국어라고 해서\n어린아이를 잘 가르치는 건 아니에요")]),
] + PARTS[2][1:5] + [
    # Joy (21 Nov): also speak to parents whose child is already in a study-focused 영유
    ("p4", 117.04, 131.70, [(117.04, "만약 아이가 학습 중심의\n영유에 다니고 있다면"), (120.10, "정규 수업 이후까지\n계속 학습을 이어가기보다는"),
                            (124.46, "신체 활동이나 자유로운 놀이,\n다양한 경험을 할 수 있는 시간을"), (129.17, "만들어 주는 것도\n좋은 방법이라고 생각해요")]),
] + [("end2",) + PARTS[2][5][1:]]
DAYS = {1: 37, 2: 38, 3: 37}
ST = "raw-footage/day37/stock/"
# background scenes per section (Pexels clip id, start s), each ~2 s
BG = {
    "hook": [("5897636", 1.0), ("5426854", 2.0), ("5897636", 5.0), ("8363896", 3.0)],
    "intro": [("8088346", 1.0), ("8088307", 2.0)],
    "p1": [("5426861", 3.0), ("5897636", 7.0), ("5426854", 8.0), ("8363896", 8.0)],
    "end1": [("8088346", 4.0), ("8088307", 5.0)],
    "hook2": [("8088320", 1.0), ("8342750", 1.0)],
    "p2": [("8363857", 2.0), ("8088320", 4.0), ("8342750", 4.0), ("8363857", 8.0)],
    "p3": [("7356018", 4.0), ("8088307", 4.0), ("5426854", 11.0), ("7356018", 14.0), ("37477954", 2.0), ("34125223", 4.0)],
    "end2": [("37477954", 5.0), ("34125223", 9.0)],
    "p4": [("34125223", 1.0), ("37477954", 1.0), ("8088320", 6.0), ("34125223", 12.0), ("37477954", 7.0)],
}
# when each checklist tick appears (source time of the words that name it)
TICKS = {"p1": [37.60, 41.54], "p2": [74.66, 79.94], "p3": [103.85, 108.0, 109.7], "p4": [124.46, 125.27, 126.90]}
PART = int(os.environ.get("PART", "1"))
SEGS = PARTS[PART]


def pieces():
    """source pieces to keep, in order: each segment minus the long pauses inside it"""
    out = []
    for sec, a, b, _ in SEGS:
        t = a
        for pa, pb in PAUSES:
            if a < pa and pb < b:
                out.append((sec, t, pa + KEEP / 2)); t = pb - KEEP / 2
        out.append((sec, t, b))
    return out


def main():
    ps = pieces()
    # output time of a source time (after cutting and the 1.1x speed-up)
    starts, acc = [], 0.0
    for _, a, b in ps:
        starts.append(acc); acc += (b - a) / SPEED
    total_voice = acc

    def o(x):
        for (sec, a, b), s in zip(ps, starts):
            if a - 1e-6 <= x <= b + 1e-6:
                return round(s + (x - a) / SPEED, 3)
        best = min(range(len(ps)), key=lambda i: min(abs(x - ps[i][1]), abs(x - ps[i][2])))
        return round(starts[best], 3)

    caps = []
    for sec, a, b, cl in SEGS:
        for k, (st, text) in enumerate(cl):
            e = cl[k + 1][0] if k + 1 < len(cl) else b
            caps.append({"s": o(st), "e": round(o(e) - .02, 3), "text": text, "sec": sec})
    secs = []
    for sec, a, b, _ in SEGS:
        if secs and secs[-1]["kind"] == sec:
            secs[-1]["e"] = o(b)
        else:
            secs.append({"kind": sec, "s": o(a), "e": o(b)})
    for i in range(len(secs) - 1):
        secs[i]["e"] = secs[i + 1]["s"]
    END_TAIL = 1.0
    total = round(total_voice + END_TAIL, 3); secs[-1]["e"] = total
    ticks = {k: [o(x) for x in v] for k, v in TICKS.items() if any(sg[0] == k for sg in SEGS)}

    # edited source: video for the matte, voice for the mix (same cut, same speed)
    os.makedirs(f"{HERE}/versions/part{PART}", exist_ok=True)
    fc, n = [], len(ps)
    for i, (_, a, b) in enumerate(ps):
        fc.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d=0.012,afade=t=out:st={b - a - 0.015:.3f}:d=0.015[a{i}]")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca]")
    fc.append(f"[cv]setpts=PTS/{SPEED},fps={FPS}[v];[ca]atempo={SPEED},aresample=48000[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[v]", "-c:v", "h264_videotoolbox", "-b:v", "30M",
                    "-an", f"{HERE}/joy-src-p{PART}.mp4", "-map", "[a]", "-ac", "2", f"{HERE}/versions/part{PART}/voice.wav"], check=True)

    plan = {"fps": FPS, "day": DAYS[PART], "part": PART, "media": f"day37/p{PART}", "duration": total, "frames": int(math.ceil(total * FPS)), "voice": round(total_voice, 3),
            "captions": caps, "sections": secs, "ticks": ticks,
            "sfx": [{"t": s["s"], "sound": "whoosh", "gain": -16} for s in secs[1:]] + [{"t": t, "sound": "pop", "gain": -15} for v in ticks.values() for t in v]}
    for p in (f"{HERE}/versions/part{PART}/plan.json", f"{HERE}/../../remotion/src/day{DAYS[PART]}.json"):
        json.dump(plan, open(p, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    # background: stock scenes per section, ~2 s each, soft 0.3 s dissolves, dimmed in Remotion
    os.makedirs(f"{HERE}/../../remotion/public/day37/p{PART}", exist_ok=True)
    shots = []
    for sc in secs:
        lst, d0 = BG[sc["kind"]], sc["e"] - sc["s"]; n2 = max(1, round(d0 / 2.0)); per = d0 / n2
        for i in range(n2):
            sid, ss = lst[i % len(lst)]; shots.append((ST + sid + ".mp4", ss + (i // len(lst)) * 2.5, round(sc["s"] + i * per, 3), round(per, 3)))
    X = 0.3; ins2, fc2 = [], []
    for k, (src, ss, t0, d) in enumerate(shots):
        ins2 += ["-ss", f"{ss:.2f}", "-t", f"{d + X + .3:.2f}", "-i", src]
        fc2.append(f"[{k}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={FPS},setsar=1,format=yuv420p,"
                   f"tpad=stop_mode=clone:stop_duration=3,trim=0:{d + X:.3f},setpts=PTS-STARTPTS[b{k}]")
    prev = "b0"
    for k in range(1, len(shots)):
        fc2.append(f"[{prev}][b{k}]xfade=transition=fade:duration={X}:offset={shots[k][2]:.3f}[x{k}]"); prev = f"x{k}"
    fc2.append(f"[{prev}]trim=0:{total},setpts=PTS-STARTPTS,eq=saturation=0.85:contrast=1.04[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins2, "-filter_complex", ";".join(fc2), "-map", "[v]", "-c:v", "h264_videotoolbox", "-b:v", "16M",
                    f"{HERE}/../../remotion/public/day37/p{PART}/bg.mp4"], check=True)
    print(f"{total:.1f}s (voice {total_voice:.1f}s), {len(ps)} pieces, {len(caps)} captions")
    for s in secs:
        print(f"  {s['s']:6.2f}-{s['e']:6.2f} {s['kind']}")
    for c in caps:
        d = c["e"] - c["s"]; n2 = sum(ch >= '가' and ch <= '힣' for ch in c["text"])
        print(f"  {c['s']:6.2f} {d:4.2f}s {n2 / d:4.1f}/s {c['text']!r}")


if __name__ == "__main__":
    main()
