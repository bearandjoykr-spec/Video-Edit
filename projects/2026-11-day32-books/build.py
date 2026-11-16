"""DAY 32 plan for BearJoyReelV2 (Joy, 16 Nov 2026): "영어책은 잔뜩 샀는데, 아이는 왜 안 읽을까요?"
Message: pick what the child likes, not what the parent likes. B-roll with Joy in a round inset while she talks.
Run (repo root): .venv/bin/python projects/2026-11-day32-books/build.py
"""
import json, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "2026-11-confidence"))
from build_timeline import load_db, snap  # noqa: E402

FPS, DAY, END = 30, 32, 5.0
RAW = "raw-footage/day32-books"
LEN = {"bookpile": 5.2, "phonebuy": 14.2, "cartboxes": 8.0, "doorboxes": 7.4, "b1": 4.9, "b2": 6.9, "b3": 7.5, "b4": 8.7, "b5": 8.3, "b6": 5.4}
# (src_s, src_e, b-roll or None, b-roll start). Joy's own words throughout.
CUTS = [
    (0.00, 2.60, "bookpile", 0.0),     # 혹시 비싼 영어 전집도 사고
    (2.60, 5.46, "phonebuy", 3.0),     # 공동구매로 영어책도 잔뜩 샀는데
    (5.46, 8.40, None, 0),             # 정작 우리 아이는 그 책을 잘 읽지 않나요?
    (8.80, 12.50, None, 0),            # 그렇다면 책을 더 사기 전에 꼭 해보셨으면 하는 게 있어요.
    (13.00, 14.80, "b4", 1.0),         # 아이와 함께 서점에 가보세요.
    (15.30, 18.90, "b1", 0.5),         # 아이가 직접 읽고 싶은 책을 고르게 해주세요.
    (19.40, 23.60, None, 0),           # 제가 실제로 유아영어학원에서 일했을 때…
    (24.15, 30.40, "b2", 0.2),         # 두 권 직접 고르고, 한 권은 추천
    (30.90, 36.30, None, 0),           # 아이들이 자기가 고른 책을 계속해서 읽는다는 거예요.
    (36.85, 40.80, "b6", 0.5),         # 같은 책을 거의 닳도록 매일 읽었어요.
    (41.35, 49.30, None, 0),           # 영어 문장을 통째로 기억하고 일상에서도 사용
    (49.75, 57.75, None, 0),           # 그때 다시 느꼈어요. 많이 사주느냐보다 얼마나 좋아하느냐
    (57.75, 65.45, "b3", 0.0),         # 이번 주말에는 서점에 가서 한 권 직접 골라보는 건 어떠세요?
    (66.05, 76.45, None, 0),           # 곧 영국인 마크와 제가…
    (77.00, 81.55, None, 0),           # 베어앤조이를 팔로우하고… 안녕!
]
LINES = [
    (0.00, 5.46, "혹시 비싼 영어 전집도 사고 / 공동구매로 영어책도 잔뜩 샀는데"),
    (5.46, 8.34, "정작 우리 아이는 / 그 책을 잘 읽지 않나요?"),
    (8.84, 12.46, "그렇다면 책을 더 사기 전에 / 꼭 해보셨으면 하는 게 있어요."),
    (13.08, 14.76, "아이와 함께 서점에 가보세요."),
    (15.40, 18.86, "그리고 아이가 직접 / 읽고 싶은 책을 고르게 해주세요."),
    (19.44, 23.56, "제가 실제로 유아 영어학원에서 일했을 때 / 매일 아침 이렇게 시작했어요."),
    (24.22, 30.36, "아이들이 등원하면 / 읽고 싶은 책 두 권을 직접 고르고 / 나머지 한 권은 제가 추천해 줬거든요."),
    (30.94, 36.26, "그런데 정말 재미있는 건 / 아이들이 자기가 고른 책을 / 계속해서 읽는다는 거예요."),
    (36.92, 40.76, "어떤 아이들은 같은 책을 / 거의 닳도록 매일 읽었어요."),
    (41.40, 49.24, "그러다 어느 순간 / 책에 나오는 영어 문장을 통째로 기억하고 / 일상에서도 자연스럽게 사용하는 모습을 / 여러 번 봤어요."),
    (49.82, 50.92, "그때 다시 느꼈어요."),
    (51.32, 57.72, "아이에게 중요한 건 / 얼마나 많은 책을 사주느냐보다 / 그 책을 얼마나 좋아하느냐는 거예요."),
    (57.72, 65.40, "이번 주말에는 아이와 서점에 가서 / 좋아하는 영어 그림책 한 권을 / 직접 골라보는 건 어떠세요?"),
    (66.12, 76.42, "어떤 영어 그림책을 골라야 할지 고민되신다면 / 곧 영국인 마크와 제가 / 아이들과 함께 읽기 좋은 영어 그림책을 / 소개해 드릴게요."),
    (77.08, 81.48, "베어앤조이를 팔로우하고 / 다음 영상도 놓치지 마세요! 안녕~"),
]
HI = ["전집도", "잔뜩", "잘 읽지 않나요?", "더 사기 전에", "서점에", "직접", "매일 아침", "두 권", "추천해", "재미있는", "자기가 고른 책을", "닳도록",
      "통째로", "자연스럽게", "다시 느꼈어요.", "중요한 건", "많은 책을", "얼마나 좋아하느냐는", "이번 주말에는", "한 권을", "직접", "고민되신다면", "마크와", "소개해",
      "팔로우하고", "놓치지"]
WHITE = "#FFFFFF"
# pops in SOURCE time: (s, e, small, big, slot, sound, size)
POPS = [
    (2.70, 5.40, "📦 공동구매 · 전집", "일단 샀는데…", "mid", "boing", 96),
    (5.60, 8.30, "", "아이는 안 읽어요 😢", "mid", "pop", 96),
    (13.10, 14.70, "", "👣 서점으로 GO!", "mid", "pop", None),
    (15.50, 18.80, "", "👉 아이가 직접 고르기", "mid", "sparkle", None),
    (24.30, 30.30, "매일 아침 루틴", "📚📚 아이 선택 + 📖 추천 1권", "mid", "pop", 66),
    (36.95, 40.70, "", "닳도록 매일 📖🔁", "mid", "boing", None),
    (41.50, 49.20, "", "💬 문장이 입에서 술술", "mid", "sparkle", 84),
    (51.40, 57.60, "많이 사주기 ❌", "좋아하는 한 권 ⭕", "mid", "impact", 110),
    (57.80, 65.30, "이번 주말 미션", "📚 서점에서 한 권 고르기", "mid", "sparkle", 80),
]


def main():
    db = load_db(f"{RAW}/audio16k.wav")
    segs, t = [], 0.0
    for s, e, br, bs in CUTS:
        s2 = s if s == 0 else snap(s, db, 0.15, 0.1); e2 = snap(e, db, 0.1, 0.2)
        if segs and s2 < segs[-1]["src_e"]:
            s2 = segs[-1]["src_e"]
        segs.append({"kind": "broll" if br else "joy", "src_s": s2, "src_e": e2, "out_s": round(t, 3), "broll": br,
                     "b_s": round(min(bs, LEN.get(br, 99) - (e2 - s2) - 0.05), 2) if br else 0})
        t += e2 - s2
    speech_end = round(t, 3); total = round(speech_end + END, 3)

    def to_out(x):
        for g in segs:
            if g["src_s"] <= x <= g["src_e"]:
                return round(g["out_s"] + x - g["src_s"], 3)
        nxt = [g for g in segs if g["src_s"] > x]
        return nxt[0]["out_s"] if nxt else round(segs[-1]["out_s"] + segs[-1]["src_e"] - segs[-1]["src_s"], 3)

    syl = lambda p: len(re.findall(r"[가-힣0-9A-Za-z]", p))
    C = []
    for s, e, ko in LINES:
        ps = [p.strip() for p in ko.split(" / ")]
        n = [max(1, syl(p)) for p in ps]
        a = s
        for p, m in zip(ps, n):
            b = a + (e - s) * m / sum(n)
            C.append({"i": len(C), "s": to_out(a), "e": to_out(b), "ko": p, "en": "", "hi": next((h for h in HI if h in p), ""), "demo": False, "words": []}); a = b
    C.sort(key=lambda c: c["s"])
    for a, b in zip(C, C[1:]):
        if 0 < b["s"] - a["e"] < 0.7:
            a["e"] = b["s"]
    for c in C:
        c["s"] = max(0, c["s"] - 0.08)
    C = [c for c in C if c["s"] >= 2.0]  # the thumbnail title carries the first line
    ev, sfx = [], []
    add = lambda tt, s, g: sfx.append({"t": round(max(0, tt), 3), "sound": s, "gain": g})
    # HOOK / thumbnail: Joy's title over the piles of books
    ev.append({"type": "pop", "s": -0.3, "e": 2.55, "kicker": "영어책은 잔뜩 샀는데,", "text": "아이는 왜 안 읽을까요?", "slot": "hook", "k": 90,
               "size": 112, "kickerSize": 84, "color": "#F6E27A"})
    add(0.0, "impact", -6); add(0.05, "sparkle", -12)
    for k, (s, e, kick, text, slot, snd, size) in enumerate(POPS):
        p = {"type": "pop", "s": to_out(s), "e": to_out(e), "text": text, "kicker": kick, "slot": slot, "k": k}
        if size:
            p["size"] = size
        ev.append(p); add(to_out(s), snd, {"pop": -9, "impact": -7}.get(snd, -11))
        ev.append({"type": "punch", "s": to_out(s), "e": to_out(s) + 0.25, "z": 1.05, "shake": 4})
    ev.append({"type": "tag", "s": to_out(19.5), "e": to_out(23.5), "name": "Joy T", "flags": "🇰🇷", "role": "Bear & Joy 공동 저자 · 유아 영어 교사"})
    add(to_out(19.5), "whoosh", -12)
    ev.append({"type": "markpill", "s": to_out(69.6), "e": to_out(76.3), "img": "brand/mark-avatar.png", "name": "Mark T", "line": "영국인 선생님과 함께 소개할게요", "top": 1000})
    add(to_out(69.6), "whoosh", -11)
    for p_, g in zip(segs, segs[1:]):
        if p_["broll"] != g["broll"]:
            add(g["out_s"] - 0.06, "whoosh", -16)
    ev.append({"type": "end", "s": round(speech_end - 0.1, 3), "e": total, "short": False, "share": ""})
    ev.append({"type": "badge", "s": 2.55, "e": speech_end - 0.1, "day": DAY, "docked": True})
    add(speech_end - 0.1, "impact", -8); add(speech_end + 0.05, "sparkle", -10)
    add(speech_end + 1.9, "pop", -6); add(speech_end + 2.8, "pop", -6); add(speech_end + 2.85, "chime", -9)
    zooms = [{"t": -1.0, "z": 1.0}] + [{"t": g["out_s"], "z": 1.0 if g["broll"] else (1.06 if k % 2 else 1.0)} for k, g in enumerate(segs)]
    plan = {"name": "day32-books", "media": "day32books/main", "fps": FPS, "duration": total, "frames": int(math.ceil(total * FPS)), "speechEnd": speech_end,
            "day": DAY, "segments": segs, "captions": C, "events": ev, "zooms": zooms, "music": {"dropouts": [], "drops": []},
            "slots": {"hook": {"left": 0, "right": 0, "top": 860, "rot": -3}, "mid": {"left": 0, "right": 0, "top": 900, "rot": -2}},
            "tagPos": {"left": 50, "top": 1120}, "scrim": True, "look": "original", "captionTop": 1330, "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/main", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/main/timeline_v2.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print(f"{total:.1f}s ({speech_end:.1f}s speech), {len(segs)} segments, {len(C)} captions")
    for c in C:
        n = syl(c["ko"]); d = c["e"] - c["s"]
        flag = "  <-- fast" if n / d > 6.5 else ("  <-- short" if d < 1.2 else "")
        print(f"  {c['s']:6.2f} {d:4.2f}s {n:2d}자 {n / d:4.1f}/s [{c['hi']}] {c['ko']}{flag}")


if __name__ == "__main__":
    main()
