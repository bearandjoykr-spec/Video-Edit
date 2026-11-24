"""Paper textures for PaperThink (made here with numpy, no AI): crumpled-paper light map, newsprint, fibre.
Run (repo root): tools/fx-venv/bin/python projects/2026-11-ai-question/textures.py"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OUT = "remotion/public/paper"; R = np.random.default_rng(11)
from scipy.ndimage import gaussian_filter
def blur_noise(n, sigma):
    a = gaussian_filter(R.standard_normal((n, n)), sigma, mode="wrap")
    return (a - a.mean()) / (a.std() + 1e-9)
N = 1024
# crumpled paper: flat facets with sharp folds (Voronoi cells, each tilted a little), lit from the top-left
M = 512; pts = R.random((140, 2)) * M; nrm = R.normal(0, 1, (140, 2)) * .5
yy, xx = np.mgrid[:M, :M].astype(np.float32); best = np.full((M, M), 1e9, np.float32); second = best.copy(); idx = np.zeros((M, M), np.int32)
for i, (px, py) in enumerate(pts):
    for ox in (-M, 0, M):
        for oy in (-M, 0, M):
            d = (xx - px - ox) ** 2 + (yy - py - oy) ** 2
            sec = np.where(d < best, best, np.minimum(second, d)); idx = np.where(d < best, i, idx); best = np.minimum(best, d); second = sec
facet = nrm[idx, 0] * .8 + nrm[idx, 1] * .6
crease = np.exp(-(np.sqrt(second) - np.sqrt(best)) / 2.5)      # dark-light line at each fold
shade = gaussian_filter(facet, 2.5, mode="wrap") * 9 - crease * 9 + gaussian_filter(R.standard_normal((M, M)), 40, mode="wrap") * 120
img = np.clip(128 + shade + R.normal(0, 4, (M, M)), 0, 255).astype(np.uint8)
Image.fromarray(img).save(f"{OUT}/tex-crumple.png")
# light fibre only (flat card)
Image.fromarray(np.clip(128 + blur_noise(N, .7) * 6 + blur_noise(N, 30) * 6, 0, 255).astype(np.uint8)).save(f"{OUT}/tex-fibre.png")
# newsprint: rows of grey "text" on off-white, for clothes and props
W = 800; im = Image.new("L", (W, W), 235); d = ImageDraw.Draw(im)
y = 10
while y < W:
    x = 8
    while x < W:
        w = int(R.integers(8, 46)); d.rectangle((x, y, x + w, y + 5), fill=int(R.integers(70, 140))); x += w + int(R.integers(5, 9))
    y += 13 if R.random() > .08 else 30
im = im.filter(ImageFilter.GaussianBlur(.6)); im.save(f"{OUT}/tex-news.png")
print("ok")
