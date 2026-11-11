"""Little Steps Day 1 ad (Joy, 11 Nov 2026): Mark says a phrase, Joy shows it in the peekaboo-window game, three times.

Ad style (Joy: brand fonts/colours not required, clean like an ad, short, viral). Vertical 1080x1920, the landscape
class footage sits in a 4:5 card with a big headline above it. Source: raw-footage/day1-promo/promo.mov (Day 1 class edit).
Run: .venv/bin/python projects/2026-11-day1-ad/build.py   -> versions/main/timeline.json (+ cut list)
All shot and word times are SOURCE seconds; nothing is sped up. Joy's part of the source is mirrored (the worksheet text
reads backwards), so her shots are flipped back ("mirror"); crop centres stay in source pixels.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-confidence"))
from build_timeline import load_db, snap  # noqa: E402

FPS, END = 30, 3.6
P = {1: ("Look, it's a bear!", "봐, 곰이야!"), 2: ("Where's the bear?", "곰이 어디 있지?"), 3: ("There he is!", "여기 있네!")}
# who, src_s, src_e, crop centre x at start/end (source px), header, english word times (source), card caption (s, e, ko)
SHOTS = [
    dict(who="joy", s=214.95, e=217.30, cx=(900, 900), head="hook", words=[],
         cap=(214.98, 217.30, "There he is! · 여기 있었네!")),
    dict(who="mark", s=29.95, e=32.45, cx=(1050, 1050), head=1, words=[30.06, 30.79, 31.31, 31.44]),
    dict(who="joy", s=191.95, e=195.65, cx=(940, 940), head=1, words=[192.06, 192.78, 192.82, 192.85], cap=(194.10, 195.65, "봐, 여기 곰이 있어.")),
    dict(who="mark", s=98.90, e=100.75, cx=(1000, 1000), head=2, words=[98.96, 99.06, 99.53]),
    dict(who="joy", s=203.50, e=206.15, cx=(900, 900), head=2, words=[203.62, 203.68, 203.80], cap=(205.10, 206.15, "곰이 어디 있지?")),
    dict(who="mark", s=128.00, e=129.95, cx=(1000, 1000), head=3, words=[128.06, 128.12, 128.51]),
    dict(who="joy", s=210.88, e=214.40, cx=(1100, 900), head=3, words=[210.97, 211.80, 212.41], cap=(213.30, 214.40, "여기 있었네!")),
    dict(who="joy", s=218.80, e=222.45, cx=(880, 880), head="done", words=[], cap=(218.86, 222.45, "이렇게만 해도 짧은 놀이 하나가 완성돼요.")),
    dict(who="mark", s=150.75, e=151.62, cx=(1000, 1000), head="lovely", words=[150.82]),
]
HEADS = {
    "hook": {"kicker": "영국 원어민 × 엄마표 놀이", "big": "영어 까꿍 놀이 🐻", "ko": ""},
    "done": {"kicker": "영어 3문장 + 창문 하나", "big": "까꿍 놀이 완성! 🎉", "ko": ""},
    "lovely": {"kicker": "", "big": "Lovely! 💛", "ko": "참 잘했어요!"},
}


def main():
    db = load_db(sys.argv[1] if len(sys.argv) > 1 else "raw-footage/day1-promo/audio16k.wav")
    shots, caps, t = [], [], 0.0
    for k, sh in enumerate(SHOTS):
        s = snap(sh["s"], db, 0.12, 0.05); e = snap(sh["e"], db, 0.05, 0.15)
        off = lambda x: round(t + x - s, 3)
        if isinstance(sh["head"], int):
            en, ko = P[sh["head"]]
            head = {"kicker": f"PHRASE {sh['head']} / 3", "big": en, "ko": ko, "step": sh["head"]}
        else:
            head = dict(HEADS[sh["head"]])
        head["words"] = [off(w) for w in sh["words"]]
        shots.append({"who": sh["who"], "src_s": s, "src_e": e, "out_s": round(t, 3), "out_e": round(t + e - s, 3),
                      "cx0": sh["cx"][0], "cx1": sh["cx"][1], "head": head, "mirror": sh["who"] == "joy", "hook": sh["head"] == "hook"})
        if sh.get("cap"):
            a, b, ko = sh["cap"]
            caps.append({"s": max(off(a) - 0.6, round(t + 0.3, 3)) if k else round(t, 3), "e": min(off(b), round(t + e - s, 3)), "ko": ko})
        t += e - s
    speech = round(t, 3); total = round(speech + END, 3)
    sfx = [{"t": 0.0, "sound": "impact", "gain": -8}, {"t": 0.05, "sound": "sparkle", "gain": -14}]
    for sh in shots[1:]:
        sfx.append({"t": max(0, sh["out_s"] - 0.06), "sound": "whoosh", "gain": -14})
        if sh["head"].get("step") and sh["who"] == "mark":
            sfx.append({"t": sh["out_s"], "sound": "pop", "gain": -10})
    done = next(sh for sh in shots if sh["head"]["big"].startswith("까꿍"))
    sfx += [{"t": done["out_s"] + 0.05, "sound": "sparkle", "gain": -10}, {"t": speech, "sound": "chime", "gain": -9},
            {"t": speech + 1.6, "sound": "pop", "gain": -8}]
    plan = {"fps": FPS, "duration": total, "frames": math.ceil(total * FPS), "speechEnd": speech, "shots": shots, "caps": caps,
            "sfx": sorted(sfx, key=lambda x: x["t"]), "media": "day1ad/main", "theme": "oxford"}  # Mark: not white; Joy chose Oxford blue (11 Nov 2026)
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/main/timeline.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s ({speech:.1f}s speech), {len(shots)} shots")
    for sh in shots:
        print(f"  {sh['out_s']:5.2f}-{sh['out_e']:5.2f} {sh['who']:4} {sh['head']['big']}")
    for c in caps:
        n = len(c["ko"].replace(" ", "")); d = c["e"] - c["s"]
        print(f"  cap {c['s']:5.2f} {d:4.2f}s {n/d:4.1f}/s {c['ko']}")


if __name__ == "__main__":
    main()
