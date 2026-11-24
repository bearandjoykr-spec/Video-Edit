"""Paper heads of Joy and Mark (Joy, 24 Nov 2026: no microphones, only our faces, bodies made of paper like her reference).
Source: brand avatars (remotion/public/brand/*-avatar.png) -> hyperframes remove-background (faces/*-cut.png) -> keep inside the
avatar circle -> printed-paper look (posterize, halftone, grain) + white cut edge. Run (repo root): .venv/bin/python projects/2026-11-ai-question/face_doll.py"""
import numpy as np
from PIL import Image, ImageFilter
D = "projects/2026-11-ai-question/faces"
for n in ("joy", "mark"):
    im = Image.open(f"{D}/{n}-cut.png").convert("RGBA").resize((960, 960), Image.LANCZOS)
    yy, xx = np.mgrid[:960, :960]; circ = ((xx - 480) ** 2 + (yy - 480) ** 2) < (418 ** 2)
    a = np.asarray(im.getchannel("A")).astype(np.float32) / 255 * circ
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    rgb = np.round(rgb / 16) * 16
    lum = rgb.mean(-1, keepdims=True); dots = (np.sin(xx * .7) * np.sin(yy * .7))[..., None]
    rgb = rgb - np.clip(150 - lum, 0, 150) / 150 * (dots > .25) * 26     # halftone dots in the shadows, like newsprint
    rgb = np.clip(rgb * .95 + 10 + np.random.default_rng(3).normal(0, 6, rgb.shape[:2])[..., None], 0, 255)
    hard = Image.fromarray(((a > .5) * 255).astype(np.uint8))
    edge = hard.filter(ImageFilter.MaxFilter(17)); rough = np.asarray(edge).astype(np.float32) * (np.random.default_rng(5).random((960, 960)) > .02)
    border = Image.fromarray(rough.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))
    out = Image.new("RGBA", (960, 960), (250, 247, 238, 0)); out.putalpha(border)
    fig = Image.fromarray(rgb.astype(np.uint8)).convert("RGBA"); fig.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    out.alpha_composite(fig); out = out.crop(out.getchannel("A").getbbox()); out.save(f"remotion/public/paper/{n}-head.png"); print(n, out.size)
