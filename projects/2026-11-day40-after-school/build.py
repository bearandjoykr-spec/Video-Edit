"""DAY 40 (Joy, 26 Nov 2026): Mark says three after-school phrases; each phrase card pops up as he says it, words light up on his
timing (Whisper word stamps), and when he says 'look at the comments below' Joy's four dialogue cards (raw-footage/day40/cards/) fan in.
Run (repo root): .venv/bin/python projects/2026-11-day40-after-school/build.py -> remotion/src/day40.json"""
import json, os
H = os.path.dirname(os.path.abspath(__file__))
W = [(w["offsets"]["from"] / 1000, w["offsets"]["to"] / 1000, w["text"].strip()) for w in json.load(open(f"{H}/audio/words.json"))["transcription"] if w["text"].strip()]
norm = lambda s: s.lower().strip(".,?!")
def at(word, after=0.0):
    return next(w for w in W if norm(w[2]) == word and w[0] >= after)
def words_of(text, after):
    out, t = [], after
    for tok in text.replace("\n", " \n ").split(" "):
        if not tok: continue
        if tok == "\n": out.append({"w": "\n"}); continue
        try: w = at(norm(tok.replace("’", "'").replace("favourite", "favorite")), t); out.append({"w": tok, "s": w[0]}); t = w[0]
        except StopIteration: out.append({"w": tok, "s": t + .3})
    return out
P = [{"n": "01", "who": "PARENT", "en": "How was your day?", "ko": "오늘 하루 어땠어?", "s": at("how")[0] - .25, "again": [at("again")[0], at("how", 7.5)[0]]},
     {"n": "02", "who": "PARENT", "en": "What was your favourite part?", "ko": "오늘 뭐가 제일 좋았어?", "s": at("what")[0] - .25, "again": [at("again", 13)[0], at("what", 14)[0]]},
     {"n": "03", "who": "PARENT", "en": "Okay, sounds great.\nLet's get ready for dinner!", "ko": "좋아! 이제 저녁 먹을 준비하자!", "s": at("okay", 20)[0] - .25, "again": [at("one", 25)[0], at("okay", 26.5)[0]]}]
for p in P:
    first = words_of(p["en"], p["s"]); second = words_of(p["en"], p["again"][1] - .1)
    p["words"] = first; p["words2"] = second
ends = [at("number", 10)[0] - .1, at("and", 18)[0] - .1, at("and", 32)[0] - .05]
for p, e in zip(P, ends): p["e"] = round(e, 2)
comments = at("comments")[0]
plan = {"fps": 30, "duration": 38.3, "frames": int(38.3 * 30), "hook": [0, P[0]["s"]], "phrases": P, "outro": at("and", 32)[0] - .05, "comments": comments,
        "check": at("check")[0], "day": 40}
json.dump(plan, open(f"{H}/../../remotion/src/day40.json", "w"), ensure_ascii=False, indent=1)
print([(p["n"], round(p["s"], 2), p["e"], [round(a, 2) for a in p["again"]]) for p in P], plan["outro"], comments)
