"""Three Instagram reels cut from the Little Steps welcome film.

Run: .venv/bin/python projects/2026-11-welcome-reels/build.py   (writes versions/<name>/timeline.json)
Times below are the CapCut clock (see ../2026-11-day0-welcome/capcut-timeline.txt), which is what the owner's captions use.
Captions are the owner's and Joy's, word for word. Reel style: brand/BRAND.md. Ending: the approved "Day 1 is free" card.
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); W = f"{HERE}/../2026-11-day0-welcome"
END_CARD = 4.8
CAP = []; CAPS = []
for line in open(f"{W}/capcut-timeline.txt"):
    g = re.match(r"\s*([\d.]+)\s+([\d.]+) src\s+([\d.]+) VID_", line)
    if g: CAP.append(tuple(map(float, g.groups())))
    g = re.match(r"\s*([\d.]+)\s+([\d.]+) '(.*)'\s*$", line) or re.match(r'\s*([\d.]+)\s+([\d.]+) "(.*)"\s*$', line)
    if g and g.group(3) not in ("", "Mark", "Joy"): CAPS.append((float(g.group(1)), float(g.group(2)), g.group(3).strip()))
FACES = json.load(open(f"{W}/versions/main/faces.json"))
MARK = [(41.8, 44.8), (55, 65), (97, 104.3), (148, 154.4), (155.7, 162.3), (179.1, 183.8)]
KEYS = ["사용하세요", "함께 사용", "함께", "의미", "“Hello”", "“Look!“", "“Your turn”", "유창한", "우리말", "잘 잤어", "배고파", "양말", "대답할", "자연스럽게", "조금씩", "우리 아가", "곰이다", "이미", "더 많은 걸", "새로운 놀이", "곰의 목소리", "이야기를", "게임", "난 곰이야", "아침밥", "배가 고픈", "짧은 표현", "아이의 생각"]
EN = {"“Hello”는": "Hello becomes a greeting", "“Look!“은": "Look! becomes a shared discovery", "“Your turn”은": "Your turn becomes an invitation",
      "안녕, 우리 아가": "Hello, little one", "봐! 곰이다": "Look! A bear!", "아이가 이미 이 표현": "If your child already knows these words", "그 표현들을 활용": "give them somewhere to take them",
      "안녕. 난 곰이야": "Hello, I'm Bear!", "내 아침밥은": "Where's my breakfast?", "가르치려고 하지 말고": "Don't teach: USE"}

def build(name, a, b, bg, bgx, draw):
    """a, b = CapCut clock. draw(k) adds the events, where k(t) = time in the reel."""
    ev, sfx = [], []
    k = lambda t: round(t - a, 3)
    segs = []
    for s, e, src in CAP:
        lo, hi = max(s, a), min(e, b)
        if hi > lo: segs.append({"src_s": round(src + lo - s, 3), "src_e": round(src + hi - s, 3), "out_s": k(lo)})
    speech = round(b - a, 3)
    cue = lambda t, sound, gain=-18: sfx.append({"t": round(t, 3), "sound": sound, "gain": gain})
    def add(type_, s, e, sound=None, gain=-18, **kw):
        ev.append({"type": type_, "s": k(s), "e": k(e), **kw})
        if sound: cue(k(s), sound, gain)
    draw(add, k, cue)
    caps = []
    inside = [c for c in CAPS if c[0] >= a - .05 and c[0] < b]
    for i, (s, e, ko) in enumerate(inside):
        nxt = inside[i + 1][0] if i + 1 < len(inside) else b
        end = min(max(e, s + 1.2) + .2, nxt)
        en = next((v for p, v in EN.items() if p in ko), None)
        caps.append({"s": k(s), "e": k(end), "ko": ko, "hi": next((h for h in KEYS if h in ko), ""), **({"en": en} if en else {})})
    zooms = [{"t": 0, "z": 1.0, "cx": 948}]; big = 0
    for c in caps:
        tc = c["s"] + a; big = 1 - big
        mark = any(x <= tc < y for x, y in MARK)
        zooms.append({"t": c["s"], "z": 1.07 if big else 1.0, "cx": 948 + ((-70 if mark else 70) if big else 0)})   # both always in frame
    dur = round(speech + END_CARD, 3)
    # the end card lands with a hit
    for t, snd, g in [(speech, "whoosh", -15), (speech + .1, "sparkle", -16), (speech + .5, "pop", -16), (speech + .7, "pop", -16), (speech + 1.6, "impact", -15), (speech + 2.0, "chime", -17)]:
        cue(t, snd, g)
    plan = {"name": name, "fps": 30, "duration": dur, "frames": round(dur * 30), "speechEnd": speech, "bg": bg, "bgx": bgx, "segments": segs,
            "captions": caps, "events": ev, "zooms": zooms, "faces": FACES, "sfx": sorted(sfx, key=lambda x: x["t"])}
    os.makedirs(f"{HERE}/versions/{name}", exist_ok=True)
    json.dump(plan, open(f"{HERE}/versions/{name}/timeline.json", "w"), ensure_ascii=False, indent=0)
    cps = [round(len(re.sub(r"\s", "", c["ko"])) / (c["e"] - c["s"]), 1) for c in caps]
    gaps = sorted(e["s"] for e in ev)
    print(f"{name}: {dur:.1f}s, {len(ev)} cues, {len(sfx)} sfx, longest gap {max(y - x for x, y in zip([0] + gaps, gaps + [speech])):.1f}s, fastest caption {max(cps)} chars/s")

# ---------------------------------------------------------------- A: Don't teach, USE
def use(add, k, cue):
    add("word", 41.77, 44.8, "impact", -14, big="영어, 가르치지 말고", small=None, size=112, y=300)
    add("word", 41.9, 44.8, "sparkle", -17, big="USE", small=None, size=330, y=440)
    add("shake", 42.3, 42.4)
    add("burst", 42.3, 44.1, x=540, y=640, emoji=["⭐", "✨", "💛"], n=24)
    add("chip", 44.9, 48.1, "pop", -18, text="가르치기 ✗", emoji=None, x=70, y=420, tone="sky", size=66)
    add("chip", 46.53, 51.3, "pop", -18, text="함께 사용하기 ✓", emoji=None, right=110, y=560, tone="butter", size=66)
    add("word", 48.13, 51.3, None, big="함께하는 순간", size=120, y=300)
    add("word", 51.33, 54.8, "sparkle", -18, big="짧은 표현에도", small=None, size=112, y=320)
    add("word", 51.5, 54.8, None, big="의미가 생겨요", small=None, size=112, y=460, tone="sky")
    add("word", 55.03, 57.4, "sparkle", -17, big="Hello!", small="반가운 인사", size=250, y=330)
    add("stick", 55.2, 57.3, "pop", -18, emoji="👋", who="mark", dx=1.15, dy=.5, size=170)
    add("word", 57.6, 61.1, "sparkle", -17, big="Look!", small="함께 발견하는 말", size=250, y=330, tone="sky")
    add("stick", 57.8, 61.0, "pop", -18, emoji="👀", who="mark", dx=-1.0, dy=.3, size=170)
    add("burst", 58.0, 59.6, x=880, y=760, emoji=["🔎", "✨"], n=12)
    add("word", 61.4, 65.3, "sparkle", -17, big="Your turn", small="함께하자는 초대", size=190, y=350)
    add("stick", 61.7, 65.2, "pop", -18, emoji="💌", who="joy", dx=-1.1, dy=-.1, size=170)
    add("burst", 64.0, 65.4, x=540, y=620, emoji=["🎉", "💛", "✨"], n=22)

# ---------------------------------------------------------------- B: Perfect English isn't needed
def perfect(add, k, cue):
    add("word", 117.0, 118.45, "impact", -15, big="유창한 영어,", size=140, y=340)
    add("word", 117.0, 118.45, None, big="꼭 필요할까요?", size=124, y=520, tone="sky")
    add("strike", 118.5, 122.9, "pop", -17, text="유창한 영어", at=2.6, y=470, size=112)
    cue(k(121.1), "boing", -15)
    add("shake", 121.1, 121.2)
    add("word", 122.97, 128.2, "whoosh", -18, big="우리말로", small="아기에게", size=190, y=360)
    add("bubble", 128.33, 133.0, "pop", -17, text="잘 잤어?", x=70, y=320)
    add("bubble", 129.8, 134.0, "pop", -17, text="배고파?", right=110, y=480)
    add("bubble", 131.43, 136.9, "pop", -17, text="양말 어디 갔지? 🧦", x=170, y=650, w=720)
    add("word", 137.07, 139.6, "whoosh", -18, big="기다리지 않잖아요", size=110, y=400)
    add("chip", 139.67, 143.6, "pop", -18, text="함께 하루를 보내며", emoji="☀️", x=120, y=420, tone="butter", size=64)
    add("chip", 141.63, 143.6, "pop", -18, text="자연스럽게", emoji="💬", right=140, y=570, tone="sky", size=64)
    add("word", 143.73, 147.8, "sparkle", -17, big="영어도 조금씩", size=130, y=400)
    add("word", 148.7, 151.0, "whoosh", -17, big="Hello,", small=None, size=200, y=300)
    add("word", 149.1, 151.0, None, big="little one", size=150, y=510, tone="sky")
    add("stick", 148.9, 150.9, "pop", -18, emoji="👶", who="joy", dx=-1.05, dy=.2, size=170)
    add("word", 151.9, 154.9, "sparkle", -15, big="Look! A bear!", size=150, y=320)
    add("bear", 151.95, 154.9, None, x=240, y=490, h=540)
    add("burst", 152.0, 153.8, x=540, y=740, emoji=["✨", "⭐", "🦋"], n=20)

# ---------------------------------------------------------------- C: The bear voice
def bearvoice(add, k, cue):
    add("word", 155.2, 159.45, "impact", -15, big="이미 영어를", size=140, y=320)
    add("word", 155.2, 159.45, None, big="잘하는 아이라면?", size=112, y=500, tone="sky")
    add("word", 159.57, 162.3, "whoosh", -18, big="더 많은 걸", size=170, y=380)
    add("word", 162.43, 168.5, "sparkle", -17, big="새로운 놀이", size=160, y=390)
    add("stick", 163.0, 168.4, "pop", -18, emoji="🎈", who="joy", dx=-1.1, dy=.1, size=170)
    add("chip", 168.63, 178.9, "pop", -17, text="곰의 목소리", emoji="🐻", x=90, y=320, tone="butter", size=66)
    add("chip", 172.2, 178.9, "pop", -17, text="이야기 짓기", emoji="📖", right=130, y=470, tone="sky", size=66)
    add("chip", 174.97, 178.9, "pop", -17, text="게임 설명하기", emoji="🎲", x=120, y=620, tone="butter", size=66)
    add("bear", 179.47, 184.0, "boing", -14, giant=True, x=-300, y=500, h=800)
    add("shake", 179.5, 179.6)
    add("bubble", 179.47, 181.6, None, text="Hello, I'm Bear!", right=120, y=330, size=80)
    add("bubble", 181.8, 184.0, "pop", -16, text="Where's my breakfast?", right=120, y=330, size=72)
    add("burst", 184.1, 186.0, x=540, y=620, emoji=["🍯", "🥞", "🍓"], n=20)
    add("word", 184.07, 186.6, "sparkle", -18, big="배고픈 곰!", size=170, y=330)
    add("word", 186.67, 191.1, "whoosh", -18, big="짧은 표현 하나로", small=None, size=112, y=320)
    add("word", 188.7, 191.1, None, big="이야기는 계속돼요", size=100, y=470, tone="sky")
    add("word", 191.17, 196.0, "sparkle", -17, big="아이의 생각을", size=130, y=320)
    add("word", 192.0, 196.0, None, big="따라가 보세요", size=130, y=480, tone="sky")
    add("burst", 193.0, 195.0, x=540, y=560, emoji=["🦋", "✨"], n=20)

build("use", 41.77, 65.5, "art-lawn", 500, use)
build("perfect", 117.0, 155.0, "art-both", 1500, perfect)
build("bearvoice", 155.2, 196.05, "art-river", 300, bearvoice)
