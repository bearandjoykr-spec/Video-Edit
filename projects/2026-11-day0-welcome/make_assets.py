"""Backdrops, cloud sprites and worksheet pages for Day 0. Run: tools/fx-venv/bin/python projects/2026-11-day0-welcome/make_assets.py
The backdrops are procedural placeholders until the owner supplies watercolour art; nothing here redraws brand art."""
import glob, os
import numpy as np
from PIL import Image
OUT = "remotion/public/day0"; os.makedirs(f"{OUT}/sheets", exist_ok=True)
rng = np.random.default_rng(7)

def fbm(h, w, base=4, octv=6):
    out = np.zeros((h, w)); amp = 1.0; tot = 0
    for o in range(octv):
        n = base * 2 ** o
        g = rng.random((int(n * h / w) + 2, n + 2))
        im = Image.fromarray((g * 255).astype("uint8")).resize((w, h), Image.BICUBIC)
        out += amp * (np.asarray(im, float) / 255); tot += amp; amp *= .5
    return out / tot

def sky(name, top, mid, bottom, cloud=1.0):
    H, W = 1260, 2240
    y = np.linspace(0, 1, H)[:, None, None]
    c = lambda v: np.array(v, float)[None, None, :]
    img = np.where(y < .55, c(top) + (c(mid) - c(top)) * (y / .55), c(mid) + (c(bottom) - c(mid)) * ((y - .55) / .45))
    img = np.repeat(img, W, axis=1)
    n = fbm(H, W, 3, 7)
    a = np.clip((n - .52) * 5 * cloud, 0, 1)[..., None]
    img = img * (1 - a) + 255 * a
    img += ((fbm(H, W, 40, 3) - .5) * 10)[..., None]          # watercolour bloom
    img += rng.normal(0, 1.6, (H, W, 1))                       # paper grain
    Image.fromarray(np.clip(img, 0, 255).astype("uint8")).save(f"{OUT}/{name}.jpg", quality=92)

sky("bg-sky", (150, 196, 232), (190, 220, 242), (236, 244, 248))
sky("bg-butter", (252, 226, 140), (253, 238, 180), (255, 248, 226), .7)
sky("bg-peach", (250, 190, 170), (252, 214, 192), (255, 240, 222), .7)
sky("bg-lilac", (176, 188, 240), (208, 212, 246), (244, 238, 248), .8)

for i in range(3):
    H, W = 420, 820
    yy, xx = np.mgrid[0:H, 0:W]
    m = np.exp(-(((xx - W / 2) / (W * .36)) ** 2 + ((yy - H * .62) / (H * .28)) ** 2))
    a = np.clip((fbm(H, W, 4, 6) * .9 + m * 1.2 - .75) * 6, 0, 1)
    rgba = np.dstack([np.full((H, W, 3), 255), a * 250]).astype("uint8")
    Image.fromarray(rgba, "RGBA").save(f"{OUT}/cloud{i}.png")

try:
    import fitz
    for k, p in enumerate(sorted(glob.glob(os.path.expanduser("~/Downloads/Little-Steps-seven-day-worksheets/*.pdf")))):
        d = fitz.open(p); d[0].get_pixmap(dpi=110).save(f"{OUT}/sheets/day{k + 1}.jpg")
        print(os.path.basename(p), len(d), "pages", d[0].rect)
except ImportError:
    print("pymupdf missing: no worksheets")
