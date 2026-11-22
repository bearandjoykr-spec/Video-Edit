"""Split the full DAY 38 cut into three ~35–40 s reels (Joy, 22 Nov 2026): DAY 38 ① 교사 근속 · DAY 39 ② 교과서 · DAY 40 ③ 운영진 소통.
Uses the full edit's output timeline (versions/main/plan-full.json, voice-full.wav, remotion/public/day38/joy.webm), so Joy's matte is
not re-made: each part lists the ranges of the full timeline it plays (joyMap), the voice is cut from voice-full.wav, the stock
background is rebuilt per part. Each part opens on its own question, has props beside Joy's face, and ends with goodbye + follow +
next-episode teaser. Run (repo root): .venv/bin/python projects/2026-11-day38-yeongyu-check2/split.py
"""
import json, math, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
V = f"{HERE}/versions/main"
full = json.load(open(f"{V}/plan-full.json"))
FPS, TAIL = 30, 2.8
BYE = (128.945, 130.75)
ST = "raw-footage/day38/stock/"
stock = json.load(open(f"{HERE}/stock.json"))

PARTS = {
    38: {"ranges": [(0.0, 3.755), (9.236, 34.555), BYE], "hook": None, "n": 1,
         "hookTitle": ["영유 선생님이", "자주 바뀐다면?"], "props": ["👩‍🏫", "🔄", "👨‍🏫", "📅"], "next": "② 미국·영국 교과서면 다 좋을까?",
         "bg": {"hook": stock["hook"], "p1": stock["p1"], "bye": stock["intro"], "tip": ["5427517"]},
         # Joy (22 Nov): a silent bonus card at the very end, typed out with keyboard sounds
         "tip": ["💡 꿀팁 하나 더!", "상담 전, 영유 이름을 영어로", "구글에 검색해 보세요 🔍", "원어민 선생님들이 남긴", "리뷰를 볼 수 있어요",
                 "구글 지도 · Glassdoor · Reddit", "👉 '선생님이 자주 바뀐다'는 이야기가", "반복되는지 꼭 확인해 보세요!"]},
    39: {"ranges": [(34.555, 64.618), BYE], "hook": 2.6, "n": 2,
         "hookTitle": ["미국·영국 교과서면", "다 좋을까?"], "props": ["📘", "🇺🇸", "📗", "🇬🇧"], "next": "③ 학부모 의견, 원어민 선생님께 잘 전달될까?",
         "bg": {"p2": stock["p2"], "bye": stock["end"]}},
    40: {"ranges": [(64.618, 89.936), (115.055, 120.4), (120.4, 123.462), BYE], "hook": 2.6, "n": 3,
         "hookTitle": ["학부모 의견,", "원어민 선생님께 잘 전달될까?"], "props": ["📞", "💬", "☎️", "📩"], "next": None,
         "bg": {"p3": stock["p3"], "last": stock["last"][:3], "end": stock["last"][3:5], "bye": stock["bye"]}},
}


def run(day, P):
    out = f"{HERE}/versions/day{day}"; os.makedirs(out, exist_ok=True)
    jm, t = [], 0.0
    for a, b in P["ranges"]:
        jm.append({"t": round(t, 3), "src": a, "d": round(b - a, 3)}); t += b - a
    voice = t; TIP = 8.5 if P.get("tip") else 0; total = round(voice + TAIL + TIP, 3)

    def m(x):  # full timeline -> part timeline
        for r in jm:
            if r["src"] - 1e-3 <= x <= r["src"] + r["d"] + 1e-3:
                return round(r["t"] + x - r["src"], 3)
        return None

    caps = []
    for c in full["captions"]:
        s, e = m(c["s"]), m(min(c["e"], c["s"] + 30))
        if s is not None and e is not None and e > s: caps.append({**c, "s": s, "e": e})
    secs = []
    for sc in full["sections"]:
        for r in jm:
            a, b = max(sc["s"], r["src"]), min(sc["e"], r["src"] + r["d"])
            if b - a > .05:
                s0 = round(r["t"] + a - r["src"], 3)
                if secs and secs[-1]["kind"] == sc["kind"]: secs[-1]["e"] = round(s0 + b - a, 3)
                else: secs.append({"kind": sc["kind"], "s": s0, "e": round(s0 + b - a, 3)})
    if P["hook"]:   # parts 2 and 3: the question sits over the first seconds of the point card
        secs.insert(0, {"kind": "hook", "s": 0.0, "e": P["hook"]}); secs[1]["s"] = P["hook"]
    secs[-1]["e"] = round(voice + TAIL, 3)
    if TIP:
        secs.append({"kind": "tip", "s": round(voice + TAIL, 3), "e": total})
    ticks = {k: [m(x) for x in v if m(x) is not None] for k, v in full["ticks"].items()}
    ticks = {k: v for k, v in ticks.items() if v}
    sfx = [{"t": m(x["t"]), "sound": x["sound"], "gain": x["gain"]} for x in full["sfx"] if m(x["t"]) is not None]
    if TIP:   # keyboard typing while the lines type out (Pixabay sound, sfx/SOURCE.md)
        sfx.append({"t": round(voice + TAIL + .3, 3), "file": "projects/2026-11-day38-yeongyu-check2/sfx/typing.mp3", "ss": .25, "d": 5.6, "gain": -4})

    # voice: the same ranges of the full voice track, then silence for the end card
    fc = [f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={b - a - 0.02:.3f}:d=0.02[a{i}]" for i, (a, b) in enumerate(P["ranges"])]
    fc.append("".join(f"[a{i}]" for i in range(len(P["ranges"]))) + f"concat=n={len(P['ranges'])}:v=0:a=1,apad=whole_dur={total}[o]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/voice-full.wav", "-filter_complex", ";".join(fc), "-map", "[o]", "-t", str(total), f"{out}/voice.wav"], check=True)

    # background
    pub = f"{HERE}/../../remotion/public/day38/p{day}"; os.makedirs(pub, exist_ok=True)
    shots = []
    for sc in secs:
        lst = P["bg"].get(sc["kind"]) or P["bg"].get("p%d" % P["n"])
        if sc["kind"] == "hook" and P["hook"]: continue          # the hook shares the point's first clip
        s0 = 0.0 if (P["hook"] and sc is secs[1]) else sc["s"]
        per = (sc["e"] - s0) / len(lst)
        for i, sid in enumerate(lst):
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ST + sid + ".mp4"], capture_output=True, text=True).stdout)
            shots.append((ST + sid + ".mp4", round(max(0.0, min(1.0, dur - per - .8)), 2), round(s0 + i * per, 3), round(per, 3)))
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

    plan = {"fps": FPS, "day": day, "part": P["n"], "media": f"day38/p{day}", "joyMedia": "day38/joy.webm", "joyMap": jm, "duration": total,
            "frames": int(math.ceil(total * FPS)), "captions": caps, "sections": secs, "ticks": ticks, "sfx": sfx,
            "hookTitle": P["hookTitle"], "props": P["props"], "next": P["next"], "tip": P.get("tip"), "tipType": [.35, 5.9]}
    for p in (f"{out}/plan.json", f"{HERE}/../../remotion/src/day{day}.json"):
        json.dump(plan, open(p, "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"DAY {day}: {total:.1f}s", [(s["kind"], s["s"], s["e"]) for s in secs])


for day, P in PARTS.items():
    run(day, P)
