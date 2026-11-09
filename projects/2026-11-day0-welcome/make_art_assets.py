"""Clouds cut from the owner's own paintings, for the moving sky.
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
