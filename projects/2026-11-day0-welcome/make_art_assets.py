"""Clouds cut from the owner's own paintings, the Little Steps wordmark keyed from their end card, and the music bed + beat map.
Run: tools/fx-venv/bin/python projects/2026-11-day0-welcome/make_art_assets.py"""
import json, sys, numpy as np
from PIL import Image, ImageFilter
Pub = "remotion/public/day0"
# --- watercolour clouds: real painted clouds from the sky of art-river / art-both
def cloud(src, box, out, cut=.80):
    im = Image.open(src).convert("RGB").crop(box); a = np.asarray(im, float) / 255
    white = a.min(axis=2)
    alpha = np.clip((white - cut) / .10, 0, 1)
    h, w = alpha.shape; yy, xx = np.mgrid[0:h, 0:w]
    fall = np.clip(1.25 - np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2), 0, 1) ** .6
    alpha = np.asarray(Image.fromarray((alpha * fall * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1.5)), float) / 255
    # lift to pure cloud colour so no blue fringe shows when it drifts
    rgb = np.clip(a * 1.05 + .03, 0, 1)
    Image.fromarray(np.dstack([rgb, alpha]).__mul__(255).astype("uint8"), "RGBA").save(out)
    print(out, im.size, round(float(alpha.mean()), 3))
k = 2240 / 1672
b = lambda *v: tuple(int(x * k) for x in v)
cloud(f"{Pub}/art-river.jpg", b(900, 20, 1660, 300), f"{Pub}/cloud0.png")
cloud(f"{Pub}/art-river.jpg", b(170, 270, 700, 530), f"{Pub}/cloud1.png")
cloud(f"{Pub}/art-both.jpg", b(150, 165, 710, 355), f"{Pub}/cloud2.png")
# --- Little Steps wordmark (no bear): dark ink keyed off the cream end card
fr = np.asarray(Image.open(sys.argv[1]).convert("RGB"), float)
paper = np.median(fr.reshape(-1, 3), axis=0); dist = np.abs(fr - paper).sum(axis=2) / 3
ys, xs = np.where(dist > 40); print("logo bbox", xs.min(), xs.max(), ys.min(), ys.max())
rows = np.where((dist > 40).sum(axis=1) > 0)[0]
wide = np.where((dist > 40).sum(axis=1) > 0)[0]
# the script line starts where ink is widest: find the top of the wordmark from column spread
spread = [(np.ptp(np.where(dist[r] > 40)[0]) if (dist[r] > 40).any() else 0) for r in range(fr.shape[0])]
top = next(r for r in range(fr.shape[0]) if spread[r] > (xs.max() - xs.min()) * .32)
crop = fr[top - 4:ys.max() + 6, xs.min() - 6:xs.max() + 6]; d = dist[top - 4:ys.max() + 6, xs.min() - 6:xs.max() + 6]
alpha = np.clip(d / 90, 0, 1)
ink = np.clip((crop - paper * (1 - alpha[..., None])) / np.maximum(alpha[..., None], .02), 0, 255)
Image.fromarray(np.dstack([ink, alpha * 255]).astype("uint8"), "RGBA").save(f"{Pub}/little-steps-wordmark.png"); print("wordmark", crop.shape)
