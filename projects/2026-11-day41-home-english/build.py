"""DAY 41 "엄마가 영어를 못하는데, 엄마표 영어요?" (Joy, 27 Nov 2026). Joy's talking-head (raw-footage/day41/main.mov) with pauses
over 0.4 s shortened (jump cuts, soft endings kept), captions on her lines at chest height, and her screen recording of the free
'7-day roadmap' resource (raw-footage/day41/screen.mov) in a card while she talks about it (her reference: hailey_ourhabit reel).
Word stamps: Whisper per 10 s chunk (words_raw.txt). Run (repo root): .venv/bin/python projects/2026-11-day41-home-english/build.py"""
import json, os, subprocess, wave
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); R = f"{H}/../.."
W = [(float(x.split(":")[0]), x.split(":", 1)[1]) for x in open(f"{H}/words_raw.txt").read().split()]
with wave.open(f"{H}/audio/a16.wav") as f:
    sr = f.getframerate(); a = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
w = int(sr * .02); r = np.array([20 * np.log10(np.sqrt(np.mean(a[i:i + w] ** 2)) + 1e-9) for i in range(0, len(a) - w, w)])
sp = r > np.percentile(r, 10) + 14
runs, i = [], 0
while i < len(sp):
    if sp[i]:
        j = i
        while j < len(sp) and sp[j]: j += 1
        runs.append([i * .02, j * .02]); i = j
    else: i += 1
merged = [runs[0]]
for s, e in runs[1:]:
    if s - merged[-1][1] < .4: merged[-1][1] = e
    else: merged.append([s, e])
END = 36.4                                                          # after "그럼 안녕" and the wave
segs = [[max(0, s - .12), min(END, e + .2)] for s, e in merged if s < END]
for k in range(1, len(segs)):
    if segs[k][0] < segs[k - 1][1]: segs[k][0] = segs[k - 1][1]
segs = [s for s in segs if s[1] - s[0] > .15]
segs[-1][1] = END
tl, t = [], 0.0
for s, e in segs: tl.append((s, e, t)); t += e - s
total = round(t, 3)
def m(x):
    for s, e, o in tl:
        if x <= e: return round(o + max(0, x - s), 3)
    return total
fc, cat = [], ""
for k, (s, e, _) in enumerate(tl):
    fc.append(f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS[v{k}];[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={e - s - .02:.3f}:d=0.02[a{k}]")
    cat += f"[v{k}][a{k}]"
fc.append(cat + f"concat=n={len(tl)}:v=1:a=1[v][a]")
os.makedirs(f"{R}/remotion/public/day41", exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{R}/raw-footage/day41/main.mov", "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
                "-c:v", "h264_videotoolbox", "-b:v", "20M", "-c:a", "aac", "-b:a", "256k", f"{R}/remotion/public/day41/main.mp4"], check=True)
first = lambda word, after=0: next(m(s) for s, x in W if x.startswith(word) and s >= after)
L = [("엄마가", "엄마가 영어를 못하는데,\n엄마표 영어요?"), ("영어에", "영어에 자신이 없어도\n집에서 아이와 영어를 써 볼 수 있어요"),
     ("대신", "대신, 오늘부터\n부모님이 노력하셔야 돼요"), ("학원에서", "학원에서 배운 영어,\n학원 문 앞에 두고 오기엔 아깝잖아요"),
     ("집에서도", "집에서도 한마디씩 주고받으면"), ("아이가", "아이가 영어를 쓸 기회가\n그만큼 늘어요"),
     ("학원에", "학원에 안 다닌다면"), ("오늘", "오늘 딱 한마디부터\n영어로 이야기해 보세요"),
     ("그래서", "\"그래서 집에서 무슨 말을 해요?\"\n싶으신 분들"), ("제가", "제가 집에서 영어를 시작하는 방법을\n자료로 정리했어요"),
     ("댓글에", "댓글에 아무 이모지나 남겨 주세요"), ("무료로", "무료로 보내 드릴게요!"), ("그럼", "그럼 안녕! 👋")]
starts, after = [], 0
for wd, _ in L:
    s = next(x for x in W if x[1].startswith(wd) and x[0] >= after); starts.append(m(s[0])); after = s[0] + .01
caps = [{"s": max(0, starts[k] - .05), "e": (starts[k + 1] - .05) if k + 1 < len(L) else total, "text": L[k][1]} for k in range(len(L))]
res = [first("그래서", 22), first("댓글에", 30)]                    # screen recording runs from "그래서…" to "댓글에"
plan = {"fps": 30, "duration": total, "frames": int(np.ceil(total * 30)), "caps": caps, "hookEnd": first("영어에"), "res": res,
        "emoji": first("댓글에", 30), "free": first("무료로"), "bye": first("그럼"), "day": 41}
json.dump(plan, open(f"{R}/remotion/src/day41.json", "w"), ensure_ascii=False, indent=1)
# screen recording, h264, fit to the resource span
span = res[1] - res[0] + 2.4
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{R}/raw-footage/day41/screen.mov", "-an", "-vf", f"setpts=PTS*{span / 12.72:.4f},fps=30,scale=840:-2",
                "-c:v", "h264_videotoolbox", "-b:v", "12M", f"{R}/remotion/public/day41/screen.mp4"], check=True)
print(f"total {total}s from 38.1s", "res", res, "span", round(span, 2))
