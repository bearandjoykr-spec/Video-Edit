"""AI 질문 reel: fit the picture to Mark's English narration (raw-footage/ai-question/mark-ai.m4a, 24 Nov 2026).
Voice: deep-filter cleaned (audio/df/mark48.wav), the leading "okay" cut, pauses over 0.35 s shortened (soft word endings kept:
speech mask = 10th-percentile floor + 8 dB, gaps < 0.12 s filled). Scenes start where Mark starts each line; captions are his words
(English) under a Korean line; animation cues follow his words. Writes audio/voice.wav and remotion/src/paperthink.json.
Run (repo root): .venv/bin/python projects/2026-11-ai-question/build.py"""
import json, os, subprocess, wave
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); A = f"{H}/audio"
WAV = f"{A}/df/mark48.wav"
words = [(w["offsets"]["from"] / 1000, w["offsets"]["to"] / 1000, w["text"].strip().lower().strip(".,?!\"'")) for w in json.load(open(f"{A}/mark.json"))["transcription"] if w["text"].strip()]
with wave.open(WAV) as f:
    sr = f.getframerate(); a = np.frombuffer(f.readframes(f.getnframes()), np.int16).astype(np.float32) / 32768
W = int(sr * .02); r = np.array([20 * np.log10(np.sqrt(np.mean(a[i:i + W] ** 2)) + 1e-9) for i in range(0, len(a) - W, W)])
sp = r > np.percentile(r, 10) + 8
i = 0
while i < len(sp):
    if not sp[i]:
        j = i
        while j < len(sp) and not sp[j]: j += 1
        if 0 < i and j < len(sp) and (j - i) * .02 < .12: sp[i:j] = True
        i = j
    else: i += 1
runs, i = [], 0
while i < len(sp):
    if sp[i]:
        j = i
        while j < len(sp) and sp[j]: j += 1
        runs.append([i * .02, j * .02]); i = j
    else: i += 1
start = next(w[0] for w in words if w[2] == "in") - .12          # skip the "okay" before the first line
runs = [[max(s, start), e] for s, e in runs if e > start]
merged = [runs[0]]
for s, e in runs[1:]:
    if s - merged[-1][1] < .35: merged[-1][1] = e
    else: merged.append([s, e])
segs = [[max(start, s - .1), e + .12] for s, e in merged]          # keep breath-in and soft endings
for k in range(1, len(segs)):
    if segs[k][0] < segs[k - 1][1]: segs[k][0] = segs[k - 1][1]
GAP = .22
SPEED = 1.08                                                       # a touch brisker, pitch kept (atempo)
tl, t = [], 0.0
for s, e in segs:
    tl.append((s, e, t)); t += (e - s) + GAP
voice_len = t - GAP
def m(x):
    for s, e, o in tl:
        if x <= e: return (o + max(0, x - s)) / SPEED
    return voice_len / SPEED
fc = [f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={e - s - .04:.3f}:d=0.04,apad=pad_dur={GAP}[s{k}]" for k, (s, e, _) in enumerate(tl)]
fc.append("".join(f"[s{k}]" for k in range(len(tl))) + f"concat=n={len(tl)}:v=0:a=1,atempo={SPEED}[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", WAV, "-filter_complex", ";".join(fc), "-map", "[o]", "-ar", "48000", f"{A}/voice.wav"], check=True)

# lines: (first words to find, Korean caption, English = Mark's words, scene it starts)
txt = [w[2] for w in words]
def find(seq, after=0):
    seq = seq.split()
    for k in range(after, len(txt)):
        if txt[k:k + len(seq)] == seq: return k
    raise ValueError(seq)
L = [("in a world where ai can", "AI가 다 알려주는 세상,\n우리 아이에게 정말 필요한 건 뭘까요?", "In a world where AI can tell us everything,\nwhat do our children really need?", "hook"),
     ("ask ai anything", "AI에게 무엇이든 물으면\n몇 초 만에 답이 돌아와요", "Ask AI anything,\nand the answer comes back in seconds.", "ai"),
     ("no need to find", "책을 찾지 않아도, 검색하지 않아도,\n누군가에게 묻지 않아도요", "No need to find a book. No need to search.\nNo need to ask anyone.", "cross"),
     ("but what matters", "하지만 가장 중요한 건 답이 아니에요.\n바로 질문이에요", "But what matters most isn't the answer.\nIt's the question.", "turn"),
     ("when we read", "함께 그림책을 읽으며\n'너는 어떻게 생각해?'라고 물으면", "When we read a picture book together\nand ask, \"What do you think?\"", "cls"),
     ("their little minds", "아이들의 작은 머릿속은\n질문과 상상으로 가득 차요", "their little minds fill up\nwith questions and imagination.", None),
     ("and when they meet", "세계 곳곳의 사람들을 만났을 때도\n자기 생각을 자기 말로 말할 수 있어요", "And when they meet people from all over the world,\nthey can say what they think, in their own words.", "world"),
     ("so in a world where ai gives", "AI가 답을 주는 시대,\n우리 아이에게 필요한 건 '생각하는 힘'", "So in a world where AI gives the answers,\nwhat our children need is the power to think.", "msg"),
     ("don't stop exploring", "", "", None),
     ("so in the age", "AI 시대, 우리 아이에게\n어떤 교육이 필요할까요?", "In the age of AI, what kind of education do our children need?\nLet us know in the comments.", "end")]
idx, k0 = [], 0
for q, *_ in L:
    k0 = find(q, k0); idx.append(k0)
st = [round(m(words[k][0]), 2) for k in idx]
st[0] = 0.0
voice_len = voice_len / SPEED; TAIL = 2.0; total = round(voice_len + TAIL, 2)
caps = []
for n, (q, ko, en, sc) in enumerate(L):
    if not ko: continue
    e = st[n + 1] if n + 1 < len(st) else total
    if q.startswith("so in a world"): e = st[n + 2]                  # the card holds through "don't stop…"
    caps.append({"s": st[n], "e": round(e, 2), "text": ko, "en": en})
order = ["hook", "ai", "cross", "turn", "cls", "world", "msg", "end"]
starts = {sc: st[n] for n, (_, _, _, sc) in enumerate(L) if sc}
scenes = {k: [starts[k], starts[order[i + 1]] if i + 1 < len(order) else total] for i, k in enumerate(order)}
w_at = lambda q, after=0: round(m(words[find(q, after)][0]), 2)
cues = {"crossX": [w_at("book"), w_at("search"), w_at("anyone")],
        "kidsHook": [.6, 1.0], "kidsCls": [w_at("think", find("when we read")) + .1, w_at("think", find("when we read")) + .6],
        "think": w_at("their little minds"), "glassesOff": w_at("they can say"), "power": w_at("power"), "explore": w_at("don't stop exploring"),
        "aiAnswers": w_at("and the answer comes")}
sfx = [{"t": scenes[k][0] - .15, "sound": "whoosh", "gain": -16} for k in order[1:]]
sfx += [{"t": c, "sound": "pop", "gain": -14} for c in cues["crossX"]]
sfx += [{"t": cues["power"], "sound": "chime", "gain": -12}]
plan = {"fps": 30, "duration": total, "frames": int(np.ceil(total * 30)), "scenes": scenes, "caps": caps, "cues": cues, "sfx": sfx, "voice": voice_len}
json.dump(plan, open(f"{H}/../../remotion/src/paperthink.json", "w"), ensure_ascii=False, indent=1)
print(f"voice {voice_len:.1f}s total {total}s"); print(scenes); print(cues)
