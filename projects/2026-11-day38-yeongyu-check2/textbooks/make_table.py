"""DAY 39 textbook table (Joy, 23 Nov 2026): common 영유 books by skill. Run: .venv/bin/python projects/2026-11-day38-yeongyu-check2/textbooks/make_table.py"""
import os
from PIL import Image, ImageDraw, ImageFont
H = os.path.dirname(os.path.abspath(__file__))
F = "remotion/node_modules/pretendard/dist/public/static/Pretendard-"
f = lambda w, s: ImageFont.truetype(F + w + ".otf", s)
NAVY, CREAM, YEL, GREY = (31, 45, 84), (250, 245, 234), (255, 214, 80), (110, 110, 120)
W, Hh = 1080, 1350
im = Image.new("RGB", (W, Hh), CREAM); d = ImageDraw.Draw(im)
d.text((W // 2, 92), "영유에서 자주 쓰는 교재", font=f("Black", 62), fill=NAVY, anchor="mm")
d.text((W // 2, 160), "영역별 정리 · ★ = 여러 영유에서 겹치는 교재", font=f("SemiBold", 30), fill=GREY, anchor="mm")
rows = [("파닉스", ["★ Bricks Phonics / Spotlight on First Phonics", "Smart Phonics · Fly Phonics"]),
        ("리딩", ["★ Wonders (McGraw-Hill · 미국 교과서)", "★ Bricks Reading 30 → 150", "Reading Link · Wonderful World"]),
        ("라이팅", ["★ Wonders Your Turn Practice Book", "My First Writing · Writing Monster"]),
        ("리스닝 · 스피킹", ["★ Let's Go (Oxford)", "Hand in Hand · English Bus"]),
        ("문법 · 어휘", ["★ Grammar Space · My First Grammar", "Vocabulary Workshop · Reading for Vocabulary"])]
y, L, R = 220, 60, W - 60
for name, items in rows:
    h = 58 + 52 * len(items)
    d.rounded_rectangle((L, y, R, y + h), 26, fill="white", outline=NAVY, width=3)
    d.rounded_rectangle((L, y, L + 250, y + h), 26, fill=NAVY)
    d.rectangle((L + 220, y, L + 250, y + h), fill=NAVY)
    d.text((L + 125, y + h // 2), name, font=f("ExtraBold", 36), fill="white", anchor="mm")
    for i, t in enumerate(items):
        star = t.startswith("★")
        if star: d.rounded_rectangle((L + 278, y + 30 + 52 * i, L + 278 + d.textlength(t, font=f("Bold", 30)) + 16, y + 74 + 52 * i), 10, fill=YEL)
        d.text((L + 286, y + 52 + 52 * i), t, font=f("Bold" if star else "Medium", 30), fill=NAVY, anchor="lm")
    y += h + 22
d.text((W // 2, y + 40), "교재 이름보다 중요한 것: 어떤 활동·문장을 배우는지 직접 펼쳐 보세요 📖".replace(" 📖", ""), font=f("Bold", 30), fill=NAVY, anchor="mm")
d.text((W // 2, Hh - 50), "@thebearandjoy", font=f("Black", 32), fill=NAVY, anchor="mm")
im.save(f"{H}/textbook-table.png"); print(y)
