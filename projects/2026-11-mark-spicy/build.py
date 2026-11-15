"""Mark's 영유 interview as DAY 31 (Joy, 15 Nov 2026).

Joy's brief: a hook that makes people tap ("영유 성적표, 정말 믿어도 될까?"; the message is pressure, not manipulation), the problem framed in 영유 (유아 영어학원), parents' real
curiosity about results and how a business answers it, then the question "who is this for?" and an agree/disagree comment
prompt. Stock B-roll matches what Mark says (STOCK.md; Joy: Korean-looking families, 15 Nov 2026); during B-roll Mark stays in a round inset. Fairness: Mark's own
disclaimer stays, and a "개인 경험담" note sits on the sharp claims.
Run: .venv/bin/python projects/2026-11-mark-spicy/build.py raw-footage/new-1113/audio16k.wav
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-confidence"))
from build_timeline import load_db, snap  # noqa: E402

FPS, DAY, END, MSG = 30, 31, 5.0, 4.2
STOCK_LEN = {"redpen": 21.9, "money": 27.6, "quizhands": 13.3, "joywindow": 358.0, "booktop3": 11.4, "teacherkids": 11.0, "paper": 99.0, "ph_teach": 6.8, "ph_look": 5.5, "ph_fun": 6.7, "holdhands": 7.9, "raisehands": 22.8, "swing": 10.0, "walk1": 16.1, "walk2": 8.5}
# (src_s, src_e, role, b-roll or None, b-roll start)
CUTS = [
    (28.30, 33.40, "cold", None, 0),          # The pressure that we put on the students, the pressure that we put on the families.
    # Joy (15 Nov): the message is pressure, not "manipulation"; the hook asks whether the report card can be trusted
    (5.45, 8.20, "q", None, 0),               # Q (off camera): What's the biggest problem of 영유?
    (16.30, 19.05, "a", None, 0),             # And in my 20 years as a teacher,
    (22.90, 28.20, "a", "quizhands", 0.5),     # ...the biggest problem is pressure.
    (34.05, 40.60, "a", "teacherkids", 0.5),  # Joy: a Western teacher with Asian children         # tests and tests and tests.
    (72.45, 80.60, "a", None, 0),             # As an example, my kindergarten refused to give a child anything below a B
    (80.60, 89.35, "a", "paper", 0.0),       # Joy (15 Nov): a test paper gets A+, then is crumpled into the bin (graphic)       # ...because they were concerned that the parent would pull their child out
    (105.00, 110.60, "a", "ph_teach", 0.0),  # Joy (15 Nov): her own teaching photo, kids blurred
    (110.60, 112.70, "a", "money", 3.0),      # In the end, this is a business.
    (122.15, 126.10, "a", None, 0),           # And who loses? Your child loses. You lose.
    (138.10, 142.30, "a", "raisehands", 4.0), # Joy: children from behind, raising hands to answer      # And this is why we say that it's good to make mistakes.
    (197.17, 204.18, "a", None, 0),           # Again, I must state that this is just my experience. This is not all kindergartens.
    (224.88, 225.62, "a", "ph_look", 0.0),
    (226.45, 229.00, "a", "ph_look", 1.0),   # Joy: Mark's high five + the train game (kids blurred)
    (229.30, 231.90, "a", "ph_fun", 0.0),
    (232.92, 235.10, "a", "ph_fun", 2.6),    # Joy: the stream walk + Mark and Joy laughing on stage
]
# Korean captions in SOURCE time. "유아 영어학원(영유)" at the first mention, then "영유".
LINES = [
    (28.30, 33.40, "아이들에게 주는 압박, / 그리고 가정에 주는 압박이요."),
    (5.45, 8.20, "Q. 유아 영어학원(영유)의 가장 큰 문제는요?"),
    (16.30, 19.05, "20년 동안 교사로 일하면서"),
    (22.90, 28.20, "가장 큰 문제는 / '압박'이라고 생각해요."),
    (34.05, 40.60, "제가 일했던 영유들은 / 시험, 시험, 또 시험이었어요."),
    (72.45, 80.60, "예를 들어, 제가 있던 영유는 / 아이에게 B 아래 점수를 / 절대 주지 않았어요."),
    (80.60, 89.40, "부모님이 아이를 / 다른 곳으로 옮길까 봐서요."),
    (105.00, 110.60, "실제보다 좋은 점수로 / 아이를 계속 다니게 하는 거죠."),
    (110.60, 112.70, "결국 이건 비즈니스예요."),
    (122.15, 126.10, "그럼 누가 손해일까요? / 여러분의 아이, 그리고 여러분이에요."),
    (138.10, 142.30, "그래서 저희는 / 실수해도 괜찮다고 말해요."),
    (197.17, 204.70, "말씀드리지만 이건 제 경험이에요. / 모든 영유가 그렇다는 건 아니에요."),
    (224.88, 229.00, "아이를 잘 보시고"),
    (229.30, 235.10, "솔직하게 결정하세요. / 재미있게, 행복하게요."),
]
HI = ["압박,", "압박이요.", "가장 큰 문제는", "20년", "'압박'", "또 시험", "B 아래", "절대", "옮길까", "실제보다", "비즈니스",
      "누가 손해", "여러분의 아이,", "실수해도", "제 경험", "모든 영유가", "솔직하게", "행복하게요.", "아이를 잘", "계속"]
WHITE = "#FFFFFF"
# pops in SOURCE time: (s, e, small, big, sound, punch, size, colour). White and calm while the problem is named, warm from the turn.
POPS = [
    (24.50, 28.10, "가장 큰 문제", "PRESSURE", "impact", True, None, WHITE),
    (36.00, 40.50, "", "TEST · TEST · TEST", "impact", True, 92, WHITE),
    (72.60, 78.40, "부모님은 결과가 궁금하고", "학원은 '높은 점수'로 답한다", "pop", False, 72, WHITE),
    (110.70, 112.60, "", "BUSINESS", "impact", True, None, WHITE),
    (121.50, 126.00, "누가 손해?", "우리 아이", "impact", True, None, WHITE),
    (138.20, 142.20, "", "실수 = 성장 🌱", "sparkle", True, None, None),
    (197.50, 204.60, "Mark T", "모든 영유가 그런 건 아니에요", "pop", False, 66, WHITE),
    (229.00, 235.00, "", "FUN 🎈 · HAPPY 😊", "sparkle", True, None, None),
]


EXACT = {105.00, 122.15, 197.17, 224.88, 226.45, 229.30, 232.92}
EXACT_END = {89.35, 204.18, 229.00, 231.90}


def main():
    db = load_db(sys.argv[1] if len(sys.argv) > 1 else "raw-footage/new-1113/audio16k.wav")
    segs, t = [], 0.0
    for s, e, role, br, bs in CUTS:
        # starts placed by hand to drop Mark's repeated words ("who, who", "I must, I must", "make, make") are kept exactly
        s2 = s if s in EXACT else snap(s, db, 0.15, 0.1); e2 = e if e in EXACT_END else snap(e, db, 0.1, 0.2)
        if segs and segs[-1]["src_s"] < s2 < segs[-1]["src_e"]:
            s2 = segs[-1]["src_e"]  # never replay audio already used (repeated syllables)
        # brand pacing: cut pauses longer than 0.45 s inside a take, keeping 0.15 s of breath on each side
        pieces, run, a = [], None, s2
        for i in range(int(s2 * 100), int(e2 * 100)):
            quiet = db[i] < -40
            if quiet and run is None:
                run = i
            if not quiet and run is not None:
                if (i - run) / 100 > 0.9:  # Mark (15 Nov): smoother, fewer jump cuts; only long pauses go
                    pieces.append((a, round(run / 100 + 0.25, 2))); a = round(i / 100 - 0.25, 2)
                run = None
        pieces.append((a, e2))
        for ps, pe in pieces:
            if pe - ps > 0.2:
                g = {"src_s": ps, "src_e": pe, "out_s": round(t, 3), "role": role}
                if br:
                    g["broll"] = br
                    g["b_s"] = round(min(bs + (ps - s2), STOCK_LEN[br] - (pe - ps) - 0.05), 2)
                segs.append(g); t += pe - ps
    speech_end = round(t, 3); total = round(speech_end + MSG + END, 3)

    def to_out(x, role=None):
        cands = [g for g in segs if (role == "cold") == (g["role"] == "cold")]
        for g in cands:
            if g["src_s"] <= x <= g["src_e"]:
                return round(g["out_s"] + x - g["src_s"], 3)
        nxt = [g for g in cands if g["src_s"] > x]
        if nxt and nxt[0]["src_s"] - x < 3:
            return nxt[0]["out_s"]
        prv = [g for g in cands if g["src_e"] < x]
        return round(prv[-1]["out_s"] + prv[-1]["src_e"] - prv[-1]["src_s"], 3)

    syl = lambda p: len(re.findall(r"[가-힣0-9A-Z]", p))
    C = []
    for k, (s, e, ko) in enumerate(LINES):
        role = "cold" if k == 0 else None
        ps = [p.strip() for p in ko.split(" / ")]
        n = [max(1, syl(p)) for p in ps]
        a = s
        for p, m in zip(ps, n):
            b = a + (e - s) * m / sum(n)
            C.append({"i": len(C), "s": to_out(a, role), "e": to_out(b, role), "ko": p, "en": "", "hi": next((h for h in HI if h in p), ""),
                      "demo": False, "words": []}); a = b
    C.sort(key=lambda c: c["s"])
    for a, b in zip(C, C[1:]):
        if 0 < b["s"] - a["e"] < 0.7:
            a["e"] = b["s"]
    for c in C:
        c["s"] = max(0, c["s"] - 0.08)
    ev, sfx = [], []
    add = lambda tt, s, g: sfx.append({"t": round(max(0, tt), 3), "sound": s, "gain": g})
    cold = sum(g["src_e"] - g["src_s"] for g in segs if g["role"] == "cold")
    # HOOK / thumbnail (Joy): the sharp question, Mark's face and flag, and the fairness note
    ev.append({"type": "pop", "s": -0.3, "e": round(cold, 3), "kicker": "영유 성적표,", "text": "정말 믿어도 될까?", "slot": "hook", "k": 90,
               "size": 120, "kickerSize": 84, "color": "#F6E27A"})
    # Mark (15 Nov): a visual hook. A perfect A+ report card with a red "정말?" stamp, already on screen at frame 0 (thumbnail).
    ev.append({"type": "hookcard", "s": -1.0, "e": round(cold, 3), "stampAt": -0.5, "x": 24, "y": 560, "w": 360})
    add(0.45, "impact", -9)
    ev.append({"type": "markpill", "s": -0.3, "e": round(cold, 3), "img": "brand/mark-avatar.png", "name": "Mark T", "line": "20년 이상 영어를 가르친 영국인 선생님", "top": 1125})
    ev.append({"type": "note", "s": 0.0, "e": round(cold, 3), "text": "20년 이상 원어민 교사의 경험담 · 모든 영유가 그렇지는 않아요", "top": 1465})
    add(0.0, "impact", -6); add(0.05, "sparkle", -12)
    for k, (s, e, kick, text, snd, punch, size, colour) in enumerate(POPS):
        p = {"type": "pop", "s": to_out(s), "e": to_out(e), "text": text, "kicker": kick, "slot": "top", "k": k}
        if size:
            p["size"] = size
        if colour:
            p["color"] = colour
        ev.append(p); add(to_out(s), snd, {"pop": -9, "impact": -7}.get(snd, -11))
        # Mark (15 Nov): no punch-ins, they made it feel jumpy
    # report card: C turns into a B stamp
    # photo clips sit on the cream page: no dark caption scrim or vignette over them
    for g in segs:
        if str(g.get("broll", "")).startswith("ph_"):
            ev.append({"type": "creampage", "s": g["out_s"], "e": round(g["out_s"] + g["src_e"] - g["src_s"], 3)})
    pg = next(g for g in segs if g.get("broll") == "paper")
    pe = round(pg["out_s"] + pg["src_e"] - pg["src_s"], 3)
    ev.append({"type": "paper", "s": pg["out_s"], "e": pe, "crumpleAt": round((pe - pg["out_s"]) - 2.3, 2)})
    add(pg["out_s"] + 0.6, "whoosh", -14); add(pg["out_s"] + 1.8, "impact", -7); add(pe - 2.3, "boing", -11); add(pe - 1.1, "pop", -9)
    ev.append({"type": "grades", "s": to_out(78.5), "e": to_out(80.55), "stampAt": round(to_out(79.6), 3)})
    add(to_out(78.5), "whoosh", -10); add(to_out(79.6), "impact", -5)
    ev.append({"type": "note", "s": to_out(72.5), "e": to_out(126.0), "text": "※ Mark T의 개인 경험담이에요"})
    ev.append({"type": "tag", "s": to_out(16.4), "e": to_out(18.6), "name": "Mark T", "flags": "🇬🇧", "role": "20년 이상 교육 경력 · 한국·일본 등 여러 나라", "playfair": True})
    q = next(g for g in segs if g["role"] == "q")
    qe = round(q["out_s"] + q["src_e"] - q["src_s"], 3)
    # (the corner Mark chip is gone: with the tag and the round inset it was one label too many)
    # a soft whoosh only where the picture changes between Mark and B-roll
    for p_, g in zip(segs, segs[1:]):
        if p_.get("broll") != g.get("broll"):
            add(g["out_s"] - 0.06, "whoosh", -18)
    # the question to leave with (Joy), then the follow card
    ev.append({"type": "message", "s": round(speech_end - 0.1, 3), "e": round(speech_end + MSG, 3), "line1": "이건 과연", "line2": "누구를 위한 걸까요?",
               "small": "압박 속 성적표보다, 즐겁게 배우는 영어가 오래 가요.", "ask": "💬 동의 👍 / 비동의 👎 댓글로 알려주세요"})
    add(speech_end - 0.1, "chime", -8); add(speech_end + 0.3, "sparkle", -11)
    ev.append({"type": "end", "s": round(speech_end + MSG, 3), "e": total, "short": False, "share": "💬 동의 👍 / 비동의 👎 댓글로 알려주세요"})
    ev.append({"type": "badge", "s": round(cold, 3), "e": speech_end - 0.1, "day": DAY, "docked": True})
    es = speech_end + MSG
    add(es, "impact", -8); add(es + 0.05, "sparkle", -10)
    add(es + 1.9, "pop", -6); add(es + 2.8, "pop", -6); add(es + 2.85, "chime", -9)
    # camera: medium close-up on Mark (the source is a wide shot), full frame on B-roll so the round inset stays put
    def on_broll(x):
        return any(g.get("broll") and g["out_s"] <= x < g["out_s"] + g["src_e"] - g["src_s"] for g in segs)
    # one steady framing per shot (Mark, 15 Nov: the zoom changes on every caption were hard to follow)
    zooms = [{"t": -1.0, "z": 1.5}]
    for g in segs:
        zooms.append({"t": g["out_s"], "z": 1.0 if g.get("broll") else 1.5})
    plan = {"name": "spicy-main", "media": "spicy/main", "fps": FPS, "duration": total, "frames": int(math.ceil(total * FPS)), "speechEnd": speech_end,
            "day": DAY, "segments": segs, "captions": C, "events": ev, "zooms": zooms, "music": {"dropouts": [], "drops": []},
            "slots": {"hook": {"left": 0, "right": 0, "top": 330, "rot": -3}, "top": {"left": 0, "right": 0, "top": 300, "rot": -2}},
            "tagPos": {"left": 50, "top": 1150}, "scrim": True, "look": "original", "captionTop": 1330, "camOrigin": "52% 40%",
            "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/main/timeline_v2.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s ({speech_end:.1f}s speech), {len(segs)} cuts, {len(C)} captions")
    for g in segs:
        print(f"  {g['out_s']:5.1f} {g['role']:4} {g['src_s']:6.2f}-{g['src_e']:6.2f} {g.get('broll', '')} {g.get('b_s', '')}")
    for c in C:
        n = syl(c["ko"]); d = c["e"] - c["s"]
        flag = "  <-- fast" if n / d > 6.5 else ("  <-- short" if d < 1.2 else "")
        print(f"  {c['s']:6.2f} {d:4.2f}s {n:2d}자 {n / d:4.1f}/s [{c['hi']}] {c['ko']}{flag}")


if __name__ == "__main__":
    main()
