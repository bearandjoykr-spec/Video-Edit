"""Style-frame plan with fake timing (0.36 s a word) to preview the look before the real transcript."""
import json, sys
W = 0.36
def toks(text, t0):
    out = []
    for i, w in enumerate(text.split()):
        out.append({"t": w, "s": round(t0 + i * W, 2), "e": round(t0 + i * W + W * 0.85, 2)})
    return out, t0 + len(out) * W
scenes = []
scenes.append({"type": "title", "from": 0, "to": 8, "kicker": "THE WHOLE BIBLE · EPISODE 1",
               "title": "IN THE BEGINNING", "sub": "Genesis 1:1 – 2:3"})
c, e = toks("The Templars of old were men of the sword, but they were first men of the Word.", 8.5)
scenes.append({"type": "speech", "from": 8, "to": e + 1, "chunks": [{"from": 8.3, "to": e + 0.8, "tokens": c}]})
t = e + 1.5
blocks = []
pt = t + 2.5
for style, text in [("latin", "Non nobis, Domine, non nobis, sed nomini tuo da gloriam."),
                    ("english", "Not unto us, O Lord, not unto us, but unto thy name give glory."),
                    ("prayer", "Lord, open our eyes to see, our ears to hear, and our hearts to obey. Make us men who do not just read your Word, but live it."),
                    ("prayer", "In the name of the Father, and of the Son, and of the Holy Spirit. Amen.")]:
    tk, pt = toks(text, pt); pt += 0.8
    blocks.append({"style": style, "tokens": tk})
scenes.append({"type": "prayer", "from": t, "to": pt + 2, "heading": "THE PRAYER", "kneelFrom": t + 0.5, "kneelTo": pt + 1.5, "blocks": blocks})
t = pt + 2.5
verses = ["In the beginning God created the heaven and the earth.",
 "And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters.",
 "And God said, Let there be light: and there was light.",
 "And God saw the light, that it was good: and God divided the light from the darkness.",
 "And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day.",
 "And God said, Let there be a firmament in the midst of the waters, and let it divide the waters from the waters.",
 "And God made the firmament, and divided the waters which were under the firmament from the waters which were above the firmament: and it was so.",
 "And God called the firmament Heaven. And the evening and the morning were the second day.",
 "And God said, Let the waters under the heaven be gathered together unto one place, and let the dry land appear: and it was so.",
 "And God called the dry land Earth; and the gathering together of the waters called he Seas: and God saw that it was good."]
paras = []; vt = t + 1.5
for i, v in enumerate(verses):
    tk, vt = toks(v, vt); vt += 0.5
    p = {"verse": i + 1, "tokens": tk}
    if i == 0: p = {"label": "CHAPTER 1", "dropcap": True, "tokens": tk}
    paras.append(p)
scenes.append({"type": "bible", "from": t, "to": vt, "spreads": [{"from": t, "to": vt, "header": "GENESIS", "left": paras[:5], "right": paras[5:]}]})
t = vt + 0.5
items = [{"at": t + 2, "head": "Know whose image you bear", "body": "You didn't earn it, and no one can take it."},
         {"at": t + 6, "head": "Dominion is stewardship", "body": "Strength under control. That's the knight's code."},
         {"at": t + 10, "head": "Work hard, then rest", "body": "Rest isn't weakness. It's trust."}]
c, ce = toks("Work with everything you've got, then lay down your tools and rest in God.", t + 10.5)
scenes.append({"type": "notes", "from": t, "to": ce + 2, "label": "FOR THE BROTHERS", "title": "TAKE THESE TO HEART", "items": items,
               "chunks": [{"from": t + 10.3, "to": ce + 1, "tokens": c}]})
t = ce + 2.5
scenes.append({"type": "end", "from": t, "to": t + 8, "next": "Genesis 2:4 · The Garden", "sign": "Non nobis, Domine."})
plan = {"fps": 30, "duration": t + 8, "audio": None, "scenes": scenes}
json.dump(plan, open(sys.argv[1], "w"), indent=1)
for s in scenes: print(s["type"], s["from"], s["to"])
