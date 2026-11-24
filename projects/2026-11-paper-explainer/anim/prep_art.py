"""(Owner, 24 Nov 2026: no complete book pages. Only covers, site images and cut-outs; see cutouts.py.)
Copy the art the film uses into src/assets/art/ at embed-friendly sizes (git-ignored: derived from the owner's unpublished proofs).
Run extract.py (one folder up) first. Usage (repo root): python3 projects/2026-11-paper-explainer/anim/prep_art.py
"""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/../../..")
SRC = f"{ROOT}/remotion/public/paper"; OUT = f"{HERE}/src/assets/art"; os.makedirs(OUT, exist_ok=True)
def save(name, im, size, alpha=False):
    im.thumbnail((size, size), Image.LANCZOS)
    if alpha: im.save(f"{OUT}/{name}.png", optimize=True)
    else: im.convert("RGB").save(f"{OUT}/{name}.jpg", quality=86)
    print(name, im.size)
o = lambda f: Image.open(f)
half = lambda im, side: im.crop((0, 0, im.width // 2, im.height) if side == "L" else (im.width // 2, 0, im.width, im.height))
save("b1-cover", o(f"{SRC}/b1-cover.png"), 1024)
wb = o(f"{SRC}/wb-cover.png"); s = wb.height; save("wb-cover", wb.crop((wb.width * 0.25 - 6, 0, wb.width * 0.25 - 6 + s, s)), 768)
for f, n in (("site-day1-mark-v2.webp", "site-mark"), ("site-day1-joy-seoul.webp", "site-joy"), ("site-day1-worksheet-preview.webp", "site-sheet"),
             ("site-five-closed.webp", "site-doors")):
    save(n, o(f"{SRC}/{f}"), 900)
for f in ("overlay/bear.png", "overlay/butterfly.png"):
    save(os.path.basename(f)[:-4], o(f"{ROOT}/projects/2026-11-cinematic-film/{f}").convert("RGBA"), 700, True)
for f in ("mark-avatar", "joy-avatar", "wordmark-navy", "bear-butterfly"):
    save(f, o(f"{ROOT}/brand/assets/{f}.png").convert("RGBA"), 600, True)
