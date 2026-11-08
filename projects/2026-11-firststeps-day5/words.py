"""Flatten a whisper.cpp -ojf JSON into word timings: python3 words.py IN.json OFFSET_S OUT.json"""
import json, sys
d = json.load(open(sys.argv[1])); off = float(sys.argv[2]); out = []
for s in d["transcription"]:
    for tk in s["tokens"]:
        t = tk["text"]
        if t.startswith("[_") or not t.strip(): continue
        a, b = tk["offsets"]["from"] / 1000 + off, tk["offsets"]["to"] / 1000 + off
        if t.startswith(" ") or not out: out.append({"w": t.strip(), "s": round(a, 2), "e": round(b, 2)})
        else: out[-1]["w"] += t; out[-1]["e"] = round(b, 2)
json.dump(out, open(sys.argv[3], "w"), ensure_ascii=False, indent=0)
print(len(out), "words")
