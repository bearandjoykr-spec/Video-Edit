"""Paper-doll cutouts of Joy and Mark (Joy, 24 Nov 2026: paper-craft reel made on this Mac).
A frame of an existing transparent matte -> printed-paper look (soft posterize, paper grain, faint halftone) + white cut border.
Usage (repo root): .venv/bin/python projects/2026-11-ai-question/paper_doll.py SRC.webm SECONDS OUT.png"""
import subprocess, sys, numpy as np
from PIL import Image, ImageFilter
src, t, out = sys.argv[1], sys.argv[2], sys.argv[3]
tmp = "/tmp/paperdoll.png"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-c:v", "libvpx-vp9", "-ss", t, "-i", src, "-frames:v", "1", tmp], check=True)
im = Image.open(tmp).convert("RGBA"); bb = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox(); im = im.crop(bb)
pad = 40; c = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad)); c.alpha_composite(im, (pad, pad)); im = c
rgb = np.asarray(im.convert("RGB")).astype(np.float32); a = np.asarray(im.getchannel("A")).astype(np.float32) / 255
rgb = np.round(rgb / 18) * 18                                   # soft posterize: printed look
rng = np.random.default_rng(7); grain = rng.normal(0, 7, rgb.shape[:2])[..., None]
yy, xx = np.mgrid[:rgb.shape[0], :rgb.shape[1]]; dots = (np.sin(xx * .9) * np.sin(yy * .9)) * 5   # faint halftone
rgb = np.clip(rgb * .93 + 14 + grain + dots[..., None], 0, 255)   # a little lighter/matte, like paper
hard = Image.fromarray((a > .5).astype(np.uint8) * 255)
border = hard.filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.GaussianBlur(1.2))
paper = Image.new("RGBA", im.size, (252, 249, 241, 0)); paper.putalpha(border)
fig = Image.fromarray(rgb.astype(np.uint8)).convert("RGBA"); fig.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
paper.alpha_composite(fig); paper.save(out); print(out, paper.size)
