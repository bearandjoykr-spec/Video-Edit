"""Pull the art for the paper explainer out of the owner's book proofs and the website (owner, 24 Nov 2026: "you can pull the illustrations").
Usage (repo root): python3 projects/2026-11-paper-explainer/extract.py  -> remotion/public/paper/*.png|webp (git-ignored: unpublished proofs)
Pages are spreads (1190 x 595 pt); 'L'/'R' = left/right page, 'S' = whole spread.
"""
import os, subprocess
import pymupdf as fitz
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/../..")
OUT = f"{ROOT}/remotion/public/paper"; os.makedirs(OUT, exist_ok=True)
PAGES = {  # name: (pdf, page, side)
    "b1-cover": ("book1-review", 1, "R"), "b1-door": ("book1-review", 9, "R"), "b1-joy": ("book1-review", 13, "S"),
    "b1-friend": ("book1-review", 27, "L"), "b1-hill": ("book1-review", 27, "R"), "b1-house": ("book1-review", 6, "S"),
    "wb-cover": ("walkbook-one-proof", 1, "S"), "wb-howto": ("walkbook-one-proof", 12, "L"), "wb-pron": ("walkbook-one-proof", 16, "L"),
    "wb-quote": ("walkbook-one-proof", 36, "R"), "wb-starters": ("walkbook-one-proof", 37, "L"), "wb-bear": ("walkbook-one-proof", 36, "L"),
}
for name, (pdf, n, side) in PAGES.items():
    pix = fitz.open(f"{HERE}/source/{pdf}.pdf")[n - 1].get_pixmap(dpi=150)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    w, h = im.size
    im = im.crop({"L": (0, 0, w // 2, h), "R": (w // 2, 0, w, h), "S": (0, 0, w, h)}[side])
    im.save(f"{OUT}/{name}.png"); print(name, im.size)
SITE = ["littlesteps/day1/assets/day1-mark-v2.webp", "littlesteps/day1/assets/day1-joy-seoul.webp", "littlesteps/day1/assets/day1-worksheet-preview.webp",
        "littlesteps/paid/assets/oxford/five-closed.webp", "littlesteps/paid/assets/oxford/five-open.webp", "images/s2-pg-01.webp"]
for s in SITE:
    subprocess.run(["curl", "-sSL", "-m", "60", "-o", f"{OUT}/site-{os.path.basename(s)}", f"https://bearandjoy.com/{s}"], check=True)
    print("site", s, os.path.getsize(f"{OUT}/site-{os.path.basename(s)}"))
