"""DAY 37 sticker cut (Joy, 21 Nov: "목이랑 얼굴이 잘라져 보여 … 어렵다면 배경도 조금 포함해서"):
the outline follows Joy's silhouette pushed out by ~22 px and smoothed, so a thin band of the real background sits inside the white
sticker border. Nothing of her face, neck, hair or jacket is ever cut, and the edge does not flicker.
alpha: per-frame AI matte (> 0.5) ∪ steady body shape (80th percentile over the clip) → holes filled → grown 22 px →
smoothed in space (blur) and time (running average) → soft 1.5 px edge. Colour comes from the original clip, not the matte file.
Run (repo root): tools/fx-venv/bin/python projects/2026-11-day37-yeongyu-check/sticker_matte.py MATTE.webm SOURCE.mp4 OUT.webm"""
import subprocess, sys
import cv2, numpy as np

matte, source, out = sys.argv[1:4]
W, H, GROW = 1080, 1920, 22


def frames(cmd, ch):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        buf = p.stdout.read(W * H * ch)
        if len(buf) < W * H * ch: break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, ch)
    p.wait()


alpha_cmd = ["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", matte, "-vf", "alphaextract", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
rgb_cmd = ["ffmpeg", "-v", "error", "-i", source, "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]

al = [a[:, :, 0].copy() for i, a in enumerate(frames(alpha_cmd, 1)) if i % 3 == 0]
body = (np.percentile(np.stack(al), 80, axis=0) > 128).astype(np.uint8)
rows = np.where(body.any(axis=1))[0]; neck = int(rows[0] + 0.33 * (rows[-1] - rows[0])); body[:neck] = 0
del al

kgrow = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * GROW + 1, 2 * GROW + 1))
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "18", "-b:v", "0", "-row-mt", "1", "-auto-alt-ref", "0", out], stdin=subprocess.PIPE)
ema, n = None, 0
for a, rgb in zip(frames(alpha_cmd, 1), frames(rgb_cmd, 3)):
    m = ((a[:, :, 0] > 128) | (body > 0)).astype(np.uint8)
    # fill holes (everything enclosed by her outline)
    pad = np.pad(m, 1); flood = pad.copy(); mm = np.zeros((H + 4, W + 4), np.uint8)
    cv2.floodFill(flood, mm, (0, 0), 1)
    m = (pad | (1 - flood))[1:-1, 1:-1].astype(np.uint8)
    m = cv2.dilate(m, kgrow)
    s = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 7)            # rounder sticker shape
    ema = s if ema is None else .55 * ema + .45 * s                    # steady over time
    edge = np.clip((ema - .5) * 6 + .5, 0, 1)                          # crisp but anti-aliased
    edge = cv2.GaussianBlur(edge, (0, 0), 1.5)
    f = np.dstack([rgb, (edge * 255).astype(np.uint8)])
    enc.stdin.write(f.tobytes()); n += 1
enc.stdin.close(); enc.wait()
print(n, "frames")
