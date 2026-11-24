"""Cut pieces out of Book One (owner, 24 Nov 2026: no complete pages; cut the bear, butterfly and scenes out).
Pieces painted on cream paper are cut by keying the paper colour; text inside a box is painted out first.
Pieces on painted backgrounds go through hyperframes remove-background (cut_ai below).
Usage (repo root): python3 projects/2026-11-paper-explainer/anim/cutouts.py   -> src/assets/art/cut-*.png
"""
import os, subprocess
import numpy as np, pymupdf as fitz
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/../../..")
OUT = f"{HERE}/src/assets/art"; WORK = f"{HERE}/../work"; os.makedirs(WORK, exist_ok=True)
B1 = fitz.open(f"{HERE}/../source/book1-review.pdf")
def page(n):  # whole spread at 150 dpi, 2481 x 1241
    p = B1[n - 1].get_pixmap(dpi=150); return Image.frombytes("RGB", (p.width, p.height), p.samples)
def key(im, paint=(), lo=14, hi=46, size=900):
    a = np.asarray(im).astype(np.float32)
    for (x0, y0, x1, y1) in paint:  # paint text out with the paper colour
        h, w = a.shape[:2]; a[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = np.nan
    bg = np.nanmedian(np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)]), axis=0)
    a = np.where(np.isnan(a), bg, a)
    d = np.sqrt(((a - bg) ** 2).sum(-1))
    al = np.clip((d - lo) / (hi - lo), 0, 1)
    al = np.asarray(Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)))
    out = Image.fromarray(np.dstack([a.astype(np.uint8), al]), "RGBA")
    # drop stray specks (bits of page text, page numbers): keep blobs at least 3% the size of the biggest
    from scipy import ndimage
    lab, n = ndimage.label(np.asarray(out.getchannel("A")) > 20)
    if n > 1:
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1)); keep = np.isin(lab, 1 + np.flatnonzero(sizes >= 0.03 * sizes.max()))
        al2 = np.asarray(out.getchannel("A")) * keep; out.putalpha(Image.fromarray(al2.astype(np.uint8)))
    out = out.crop(out.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox())
    out.thumbnail((size, size), Image.LANCZOS); return out
def box(im, x0, y0, x1, y1):  # fractions of the spread
    return im.crop((int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height)))
pieces = {
    "cut-window": (8, (0.04, 0.32, 0.215, 0.84), ()),
    "cut-garden": (23, (0.205, 0.20, 0.53, 0.92), ()),
    "cut-sit": (20, (0.835, 0.73, 0.962, 0.95), ()),
    "cut-door": (9, (0.235, 0.13, 0.495, 0.97), ((0, 0.25, 0.11, 0.37),)),
    "cut-cat": (9, (0.71, 0.20, 0.99, 0.86), ()),
    "cut-oxford": (6, (0.60, 0.16, 0.995, 0.99), ()),
    "cut-flowers": (23, (0.51, 0.62, 0.985, 0.93), ()),
}
for name, (n, b, paint) in pieces.items():
    im = key(box(page(n), *b), paint); im.save(f"{OUT}/{name}.png", optimize=True); print(name, im.size)
# painted backgrounds: AI matte (CPU, a few seconds per image)
ai = {"cut-leap": (18, (0.62, 0.17, 0.80, 0.70)), "cut-friend": (13, (0.06, 0.52, 0.33, 0.96))}
for name, (n, b) in ai.items():
    src = f"{WORK}/{name}-src.png"; box(page(n), *b).save(src)
    subprocess.run(["npx", "hyperframes", "remove-background", src, "-o", f"{WORK}/{name}.png"], cwd=f"{ROOT}/remotion", check=True,
                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(f"{WORK}/{name}.png").convert("RGBA"); im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 30 else 0).getbbox())
    im.thumbnail((900, 900), Image.LANCZOS); im.save(f"{OUT}/{name}.png", optimize=True); print(name, im.size)
