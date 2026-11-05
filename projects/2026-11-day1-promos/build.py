"""Three vertical Instagram promos cut from the Day 1 class footage. They send people to try Day 1 free.

Run: .venv/bin/python projects/2026-11-day1-promos/build.py
Writes versions/<name>/timeline.json for remotion/src/BearJoyPromo.tsx and prints the reading-speed table.
All clip and caption times are SOURCE seconds. Nothing is sped up. Korean follows Joy's script and translation.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, END = 30, 5.0
P1 = "Look! It's a bear!"; P2 = "Where's the bear?"; P3 = "There he is!"

# seg: (src_s, src_e, centre x of the vertical crop in the source frame)
# cap: (s, e, korean, yellow word, english or "")
# pop: (s, e, small, big, tone, y, emoji-free text sizes come from the template)
# behind: (s, e, clip, clip_start_in_source, left word, right word, size)
VERSIONS = {
 "kkakkung": {
  "hook": ("창문 하나로", "영어 까꿍 놀이!"),
  "segs": [(203.5, 206.3, 840), (206.7, 214.5, 1120), (219.0, 222.45, 920), (225.5, 235.2, 920), (278.2, 284.75, 1020)],
  "capTop": {210.95: 880, 232.3: 880, 228.2: 880},
  "caps": [(203.6, 206.3, "곰이 어디 있지?", "어디", P2),
           (206.7, 210.8, "그리고 창문을 열면…", "열면", ""),
           (210.95, 214.5, "여기 있었네!", "여기", P3),
           (219.0, 222.45, "이렇게만 해도 짧은 놀이 하나가 완성돼요.", "완성", ""),
           (225.5, 228.2, "이번에는 작은 목소리로", "작은 목소리", ""),
           (228.2, 231.4, "곰이 어디 있지?", "어디", P2),
           (232.3, 235.2, "여기 있었네!", "여기", P3),
           (278.2, 281.3, "저희 베어앤조이가 중요하게 생각하는 건", "중요하게", ""),
           (281.3, 284.75, "영어를 가르치려고 하기보다는 함께 사용하는 거예요.", "함께", "")],
  "pops": [(210.95, 213.6, "", "까꿍!", "butter", 250), (219.2, 222.2, "", "놀이 완성! 🎉", "sky", 250), (225.7, 228.2, "", "쉿! 🤫", "sky", 250)],
  "behind": [(281.3, 284.75, "together", 278.0, "함", "께", 300)],
  "punch": [210.95],
 },
 "three-phrases": {
  "hook": ("아이와 오늘 바로 쓰는", "영어 세 문장"),
  "segs": [(8.75, 12.7, 985), (30.0, 32.6, 1120), (98.9, 101.0, 1000), (127.95, 130.0, 1040), (137.3, 149.3, 985), (17.75, 25.3, 975)],
  "caps": [(8.75, 12.7, "오늘은 세 가지 짧은 영어 표현을 연습해 볼 거예요.", "세 가지", ""),
           (30.0, 32.6, "봐! 곰이야!", "곰", P1),
           (98.9, 101.0, "곰이 어디 있지?", "어디", P2),
           (127.95, 130.0, "여기 있었네!", "여기", P3),
           (137.3, 141.0, "봐! 곰이야!", "곰", P1),
           (141.9, 144.3, "곰이 어디 있지?", "어디", P2),
           (145.3, 149.3, "여기 있었네!", "여기", P3),
           (17.75, 21.9, "처음부터 모든 걸 기억하려고 하지 않으셔도 돼요.", "모든 걸", ""),
           (21.9, 25.3, "언제든 다시 돌아와 저와 함께 연습하시면 됩니다.", "언제든", "")],
  "pops": [(30.1, 32.5, "첫 번째", "1 🐻", "butter", 870), (98.95, 100.9, "두 번째", "2 🔍", "sky", 870), (128.0, 129.9, "세 번째", "3 🎉", "butter", 870), (137.4, 140.0, "이제 다 함께", "한 번 더!", "sky", 870)],
  "behind": [(9.2, 12.7, "three", 8.7, "3", "!", 240)],
  "punch": [128.0],
 },
 "mistakes-ok": {
  "hook": ("영어로 다시 말해봐?", "안 해도 돼요"),
  "segs": [(272.65, 277.45, 1020), (281.3, 284.75, 1020), (285.15, 294.5, 1020), (297.55, 303.85, 1020), (310.25, 315.4, 1020)],
  "caps": [(272.65, 277.45, "꼭 영어로 다시 한번 말해봐, 영어로 뭐라고 했지? 라고 확인하지 않으셔도 돼요.", "확인", ""),
           (281.3, 284.75, "영어를 가르치려고 하기보다는 함께 사용하는 거예요.", "함께", ""),
           (285.15, 291.1, "우리말로 까꿍 놀이를 할 때 아이에게 정답을 말하게 하려고 놀지는 않잖아요.", "정답", ""),
           (291.2, 294.5, "서로의 반응을 보고 웃으며 함께 하려는 거죠.", "웃으며", ""),
           (297.55, 303.85, "부모님이 편하게 시도해보고 실수해도 웃으며 다시 해보는 모습을 보여주세요.", "실수해도", ""),
           (310.25, 315.4, "그렇게 부모님과 아이 모두 영어를 사용하는 데 조금씩 자신감을 쌓아가는 거예요.", "자신감", "")],
  "pops": [(285.4, 288.4, "", "까꿍! 👀", "sky", 870), (310.5, 314.8, "조금씩", "자신감 💪", "butter", 870)],
  "behind": [(281.3, 284.75, "together", 278.0, "함", "께", 300), (298.3, 303.85, "mistake", 297.5, "실수", "OK", 125)],
  "punch": [298.3],
 },
}

def build(name, v):
    t, segs = 0.0, []
    for s, e, cx in v["segs"]:
        segs.append({"src_s": s, "src_e": e, "out_s": round(t, 3), "cx": cx}); t += e - s
    speech_end = round(t, 3); dur = round(t + END, 3)
    def out(x):
        for g in segs:
            if g["src_s"] - 1e-6 <= x <= g["src_e"] + 1e-6: return round(g["out_s"] + x - g["src_s"], 3)
        raise ValueError(f"{name}: {x} is outside every clip")
    top = v.get("capTop", {})
    caps = [{"s": out(a), "e": out(b), "ko": k, "hi": h, "en": en, **({"top": top[a]} if a in top else {})} for a, b, k, h, en in v["caps"]]
    pops = [{"s": out(a), "e": out(b), "small": sm, "big": bg, "tone": tn, "y": y} for a, b, sm, bg, tn, y in v["pops"]]
    behind = []
    for a, b, clip, clip_src, l, r, size in v["behind"]:
        g = next(g for g in segs if g["src_s"] <= a <= g["src_e"])
        behind.append({"s": out(a), "e": out(b), "clip": clip, "trim": round((g["src_s"] - clip_src) * FPS), "seg_s": g["out_s"], "seg_e": round(g["out_s"] + g["src_e"] - g["src_s"], 3), "cx": g["cx"], "l": l, "r": r, "size": size})
    sfx = [{"t": 0.05, "sound": "whoosh", "gain": -16}, {"t": speech_end, "sound": "whoosh", "gain": -14}, {"t": speech_end + 0.6, "sound": "sparkle", "gain": -14}, {"t": speech_end + 1.6, "sound": "pop", "gain": -14}]
    sfx += [{"t": p["s"], "sound": "pop", "gain": -14} for p in pops]
    sfx += [{"t": b["s"], "sound": "impact", "gain": -18} for b in behind] + [{"t": b["s"] + .05, "sound": "sparkle", "gain": -18} for b in behind]
    punches = [{"s": out(x), "e": out(x) + .35} for x in v["punch"]]
    sfx += [{"t": p["s"], "sound": "sparkle", "gain": -14} for p in punches]
    # 100% / 104% punch on each caption. The source is 1080p, so keep it small.
    zooms = [{"t": c["s"], "z": 1.04 if i % 2 else 1.0} for i, c in enumerate(caps)]
    plan = {"name": name, "fps": FPS, "duration": dur, "frames": round(dur * FPS), "speechEnd": speech_end, "segments": segs, "captions": caps,
            "pops": pops, "behind": behind, "punches": punches, "zooms": zooms, "sfx": sorted(sfx, key=lambda x: x["t"]),
            "hook": {"small": v["hook"][0], "big": v["hook"][1], "e": 2.6}}
    d = f"{HERE}/versions/{name}"; os.makedirs(d, exist_ok=True)
    json.dump(plan, open(f"{d}/timeline.json", "w"), ensure_ascii=False, indent=1)
    bad = 0
    for c in caps:
        n = len(re.sub(r"[^가-힣0-9]", "", c["ko"])); d_ = c["e"] - c["s"]; cps = n / d_
        if cps > 6.5 or d_ < 1.2:
            bad += 1; print(f"  {name} {c['s']:6.2f} {d_:4.1f}s {cps:4.1f}/s {c['ko']}")
    print(f"{name}: {dur:.1f}s, {len(caps)} captions, {bad} over the reading rule")

for name, v in VERSIONS.items():
    build(name, v)
