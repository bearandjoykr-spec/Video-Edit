"""Mark's "spicy problems" interview (English kindergartens, 영유), cut for Korean Instagram (Joy left every choice to Claude, 13 Nov 2026).

Source: raw-footage/new-1113/spicy.mov (Mark on a bench by the Han river, 4 min, English). Off-camera question in Korean-English.
Plan: open cold on the strongest line, then question -> answer -> story -> who loses -> the positive turn -> his own disclaimer
-> advice, ~80 s. Korean captions (Claude's translation; Joy/Mark to check), English keyword pops, a report-card graphic,
and a standing "개인 경험담" note on the sharp claims (Mark says it himself; keep it so the video stays fair).
Run: .venv/bin/python projects/2026-11-mark-spicy/build.py raw-footage/new-1113/audio16k.wav
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-confidence"))
from build_timeline import load_db, snap  # noqa: E402

FPS, DAY, END = 30, 33, 5.0  # DAY: confirm with Joy
# (src_s, src_e, role)
CUTS = [
    (115.20, 121.40, "cold"),   # ...kindergartens will falsify the test results in order to keep your business.
    (5.45, 8.20, "q"),          # Q (off camera): What's the biggest problem of 영유?
    (16.30, 18.70, "a"),        # And in my 20 years as a teacher,
    (22.90, 28.20, "a"),        # I would have to say the biggest problem is pressure.
    (34.05, 40.60, "a"),        # In the kindergartens that I've worked in, tests and tests and tests.
    (52.95, 63.10, "a"),        # The top universities in the world do not want a child that has been tested all their child life.
    (72.45, 89.40, "a"),        # My kindergarten refused to give a child anything below a B... pull their child out
    (104.60, 112.70, "a"),      # But the results are faked... In the end, this is a business.
    (121.45, 126.10, "a"),      # And who loses? Your child loses. You lose.
    (138.10, 142.30, "a"),      # And this is why we say that it's good to make mistakes.
    (196.00, 204.70, "a"),      # Again, I must state that this is just my experience. This is not all kindergartens.
    (224.55, 235.10, "a"),      # Please look to yourself, look to your child, make an honest decision, keep it fun, keep it happy.
]
# Korean captions in SOURCE time (s, e, text). " / " = page break.
LINES = [
    (115.20, 121.40, "유치원이 원생을 놓치지 않으려고 / 시험 결과를 조작하기도 한다는 걸 / 아셔야 해요."),
    (5.45, 8.20, "Q. 영유의 가장 큰 문제는 뭔가요?"),
    (16.30, 18.70, "20년 동안 교사로 일하면서"),
    (22.90, 28.20, "가장 큰 문제는 / '압박'이라고 생각해요."),
    (34.05, 40.60, "제가 일했던 유치원들은 / 시험, 시험, 또 시험이었어요."),
    (52.95, 63.10, "세계 최고의 대학들은 / 어릴 때부터 시험만 보며 자란 아이를 / 원하지 않아요."),
    (72.45, 89.40, "예를 들어, 제가 있던 유치원은 / 아이에게 B 아래 점수를 / 절대 주지 않았어요. / 부모님이 아이를 / 다른 곳으로 옮길까 봐서요."),
    (104.60, 112.70, "결과를 꾸며서라도 / 아이를 붙잡아 두는 거죠. / 결국 이건 비즈니스예요."),
    (121.45, 126.10, "그럼 누가 손해일까요? / 여러분의 아이, 그리고 여러분이에요."),
    (138.10, 142.30, "그래서 저희는 / 실수해도 괜찮다고 말해요."),
    (196.00, 204.70, "다시 말씀드리지만 이건 제 경험이에요. / 모든 유치원이 그렇다는 건 아니에요."),
    (224.55, 235.10, "아이를 잘 보시고 / 솔직하게 결정하세요. / 재미있게, 행복하게요."),
]
HI = ["조작하기도", "가장 큰 문제는", "20년", "'압박'", "또 시험", "원하지 않아요.", "B 아래", "절대", "옮길까", "꾸며서라도", "비즈니스",
      "누가 손해", "여러분의 아이,", "실수해도", "제 경험", "모든 유치원이", "솔직하게", "행복하게요.", "영유의", "붙잡아"]
# pops in SOURCE time: (s, e, small, big, slot, sound, punch, size)
POPS = [
    (24.50, 28.10, "가장 큰 문제", "PRESSURE 😰", "top", "impact", True, None),
    (36.00, 40.50, "", "TEST · TEST · TEST 📝", "top", "boing", True, 92),
    (55.00, 62.90, "세계 최고 대학이 원하는 건", "🎓 시험 기계 ❌", "top", "pop", False, None),
    (110.70, 112.60, "", "BUSINESS 💼", "top", "impact", True, None),
    (121.50, 126.00, "누가 손해?", "👉 우리 아이", "top", "boing", True, None),
    (138.20, 142.20, "", "실수 = 성장 🌱", "top", "sparkle", True, None),
    (229.00, 235.00, "", "FUN 🎈 · HAPPY 😊", "top", "sparkle", True, None),
]


def main():
    db = load_db(sys.argv[1] if len(sys.argv) > 1 else "raw-footage/new-1113/audio16k.wav")
    segs, t = [], 0.0
    for s, e, role in CUTS:
        s2 = snap(s, db, 0.15, 0.1); e2 = snap(e, db, 0.1, 0.2)
        # brand pacing: cut pauses longer than 0.45 s inside a take, keeping 0.15 s of breath on each side
        pieces, run, a = [], None, s2
        for i in range(int(s2 * 100), int(e2 * 100)):
            quiet = db[i] < -40
            if quiet and run is None:
                run = i
            if not quiet and run is not None:
                if (i - run) / 100 > 0.45:
                    pieces.append((a, round(run / 100 + 0.15, 2))); a = round(i / 100 - 0.15, 2)
                run = None
        pieces.append((a, e2))
        for ps, pe in pieces:
            if pe - ps > 0.2:
                segs.append({"src_s": ps, "src_e": pe, "out_s": round(t, 3), "role": role}); t += pe - ps
    speech_end = round(t, 3); total = round(speech_end + END, 3)

    def to_out(x, role=None):
        cands = [g for g in segs if (role == "cold") == (g["role"] == "cold")]
        for g in cands:
            if g["src_s"] <= x <= g["src_e"]:
                return round(g["out_s"] + x - g["src_s"], 3)
        # inside a removed pause: snap to the next kept piece (or the end of the previous one)
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
    # the hook: title over the sharpest line, and the fairness note from the first frame
    ev.append({"type": "pop", "s": -0.3, "e": round(cold, 3), "kicker": "20년 차 원어민 교사가 말하는", "text": "영유의 진짜 문제", "slot": "hook", "k": 90, "size": 132, "kickerSize": 62})
    add(0.0, "impact", -6); add(0.05, "sparkle", -12)
    for k, (s, e, kick, text, slot, snd, punch, size) in enumerate(POPS):
        p = {"type": "pop", "s": to_out(s), "e": to_out(e), "text": text, "kicker": kick, "slot": slot, "k": k}
        if size:
            p["size"] = size
        ev.append(p); add(to_out(s), snd, {"pop": -9, "impact": -7}.get(snd, -11))
        if punch:
            ev.append({"type": "punch", "s": to_out(s), "e": to_out(s) + 0.3, "z": 1.08, "shake": 6})
    # report card: C turns into a B stamp while he tells the story
    g_s = to_out(78.6); ev.append({"type": "grades", "s": g_s, "e": to_out(89.3), "stampAt": round(to_out(80.9), 3)})
    add(g_s, "whoosh", -10); add(to_out(80.9), "impact", -5)
    # fairness note on the sharp claims (cold open, the story, faked results, who loses) and his own disclaimer
    for a, b in ((0, cold), (to_out(72.5), to_out(126.0))):
        ev.append({"type": "note", "s": round(a, 3), "e": round(b, 3), "text": "※ Mark T의 개인 경험담이에요"})
    ev.append({"type": "pop", "s": to_out(197.5), "e": to_out(204.6), "kicker": "Mark T", "text": "모든 유치원이 그런 건 아니에요 🙏", "slot": "top", "k": 30, "size": 64})
    ev.append({"type": "tag", "s": to_out(16.4), "e": to_out(27.0), "name": "Mark T", "flags": "🇬🇧", "role": "20년 차 영어 교사 · 한국·일본", "playfair": True})
    add(to_out(16.4), "whoosh", -12)
    for g in segs[1:]:
        add(g["out_s"] - 0.06, "whoosh", -15)
    ev.append({"type": "end", "s": round(speech_end - 0.1, 3), "e": total, "short": False, "share": "💬 여러분 생각은? 영유 꼭 필요하다 vs 아니다"})
    ev.append({"type": "badge", "s": round(cold, 3), "e": speech_end - 0.1, "day": DAY, "docked": True})
    add(speech_end - 0.1, "impact", -8); add(speech_end + 0.05, "sparkle", -10)
    add(speech_end + 1.9, "pop", -6); add(speech_end + 2.8, "pop", -6); add(speech_end + 2.85, "chime", -9)
    # camera: Mark sits small in a wide shot, so the frame lives at a medium close-up and punches closer on every new page
    zooms = [{"t": c["s"], "z": 1.75 if k % 2 else 1.5} for k, c in enumerate(C)]
    plan = {"name": "spicy-main", "media": "spicy/main", "fps": FPS, "duration": total, "frames": int(math.ceil(total * FPS)), "speechEnd": speech_end,
            "day": DAY, "segments": segs, "captions": C, "events": ev, "zooms": zooms, "music": {"dropouts": [], "drops": []},
            "slots": {"hook": {"left": 0, "right": 0, "top": 330, "rot": -3}, "top": {"left": 0, "right": 0, "top": 300, "rot": -2}},
            "tagPos": {"left": 50, "top": 1150}, "scrim": True, "look": "original", "captionTop": 1330, "camOrigin": "52% 40%",
            "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/main/timeline_v2.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s ({speech_end:.1f}s speech), {len(segs)} cuts, {len(C)} captions")
    for c in C:
        n = syl(c["ko"]); d = c["e"] - c["s"]
        flag = "  <-- fast" if n / d > 6.5 else ("  <-- short" if d < 1.2 else "")
        print(f"  {c['s']:6.2f} {d:4.2f}s {n:2d}자 {n / d:4.1f}/s [{c['hi']}] {c['ko']}{flag}")


if __name__ == "__main__":
    main()
