"""Build a landscape class-video plan (Remotion BearJoyClass) from a hand-edited spec.

Usage: python3 build_class.py SPEC_JSON OUT_DIR
  SPEC_JSON: {name, day, title{en,ko}, media?, cardSide?, duration, captions[], events[], zooms?}
             times in seconds on the CUT timeline (after cut.py). Word timings come from Whisper (-l en / -l ko).
  Writes OUT_DIR/timeline_class.json (captions, events, sfx cues, music dropouts) and prints the reading-speed table.

Rules (docs/class-video-style.md, BRAND.md):
  - Korean captions <= ~6 chars/s and >= 1.2 s on screen. Too-fast lines are extended into the following gap
    (never past the next caption); anything still too fast is flagged so it can be shortened (and the owner told).
  - SFX: sparkle on the title, whoosh per phrase card, chime starts each "Your turn", very soft tap per stress pulse,
    boing for jokes (music drops out, then back in), chime on the logo card.
"""
import json, os, re, sys

FPS = 30
MAX_CPS, MIN_DUR = 6.0, 1.2


def kchars(s):
    return len(re.sub(r"[\s.,!?'\"“”‘’…~·:;()\-]", "", s))


def fix_reading_speed(caps):
    caps.sort(key=lambda c: c["s"])
    rows = []
    for i, c in enumerate(caps):
        need = max(MIN_DUR, kchars(c["ko"]) / MAX_CPS)
        limit = caps[i + 1]["s"] - 0.05 if i + 1 < len(caps) else c["e"] + 2
        if c["e"] - c["s"] < need:
            c["e"] = round(min(limit, c["s"] + need), 3)
        if c["e"] - c["s"] < need:  # still short: show it a little early, if the previous caption has room
            prev_end = caps[i - 1]["e"] + 0.05 if i else 0
            c["s"] = round(max(prev_end, c["e"] - need), 3)
        d = c["e"] - c["s"]
        cps = kchars(c["ko"]) / d
        rows.append((c["s"], d, cps, "OK" if cps <= MAX_CPS + 0.05 and d >= MIN_DUR - 1e-3 else "TOO FAST", c["ko"]))
    return rows


def sfx_for(events):
    cues = []
    add = lambda t, s, g: cues.append({"t": round(max(0, t), 3), "sound": s, "gain": g})
    for ev in events:
        k = ev["type"]
        if k == "title": add(ev["s"], "sparkle", -10)
        if k == "phrase":
            add(ev["s"] - 0.1, "whoosh", -12)
            for st in ev.get("stress", []):
                for p in st.get("pulses", []): add(p, "tap", -22)
        if k == "yourturn": add(ev["s"], "chime", -12)
        if k == "voice": add(ev["s"], "boing" if ev.get("kind") == "joke" else "pop", -10 if ev.get("kind") == "joke" else -14)
        if k == "message": add(ev["s"], "sparkle", -12)
        if k == "recap": add(ev["s"] + 0.3, "whoosh", -12)
        if k == "logo": add(ev["s"] + 0.3, "chime", -10)
    return sorted(cues, key=lambda c: c["t"])


def main(spec_path, out_dir):
    spec = json.load(open(spec_path))
    rows = fix_reading_speed(spec["captions"])
    events = spec["events"]
    jokes = [e for e in events if e["type"] == "voice" and e.get("kind") == "joke"]
    dur = spec["duration"]
    plan = {**spec, "fps": FPS, "frames": int(round(dur * FPS)), "sfx": sfx_for(events),
            "music": {"dropouts": [[j["s"], j["e"]] for j in jokes], "drops": [j["e"] for j in jokes]}}
    os.makedirs(out_dir, exist_ok=True)
    json.dump(plan, open(f"{out_dir}/timeline_class.json", "w"), ensure_ascii=False, indent=1)
    print(f"{'start':>7} {'dur':>5} {'ch/s':>5}  status    caption")
    bad = 0
    for s, d, cps, st, ko in rows:
        bad += st != "OK"
        print(f"{s:7.2f} {d:5.2f} {cps:5.1f}  {st:8}  {ko}")
    print(f"\n{len(rows)} captions, {bad} too fast, {len(plan['sfx'])} SFX cues -> {out_dir}/timeline_class.json")


if __name__ == "__main__":
    main(*sys.argv[1:3])
