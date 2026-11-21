"""DAY 37: steady matte for a seated talker. The AI matte is unsure about Joy's fluffy jacket at the frame edge (half-transparent
patches that the white sticker outline then traces). Joy barely moves, so the 80th-percentile alpha over the clip gives a clean
body shape; below the neck the final alpha is max(frame alpha, that shape). Head, hair and hands keep the per-frame alpha.
Holes inside the silhouette are filled as in day35 fill_matte.py.
Run (repo root): tools/fx-venv/bin/python projects/2026-11-day37-yeongyu-check/steady_matte.py IN.webm OUT.webm"""
import subprocess, sys
import cv2, numpy as np

src, out = sys.argv[1:3]
W, H = 1080, 1920
dec = lambda: subprocess.Popen(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)

# pass 1: body shape from every 3rd frame's alpha
p = dec(); al, i = [], 0
while True:
    buf = p.stdout.read(W * H * 4)
    if len(buf) < W * H * 4: break
    if i % 3 == 0: al.append(np.frombuffer(buf, np.uint8).reshape(H, W, 4)[:, :, 3].copy())
    i += 1
p.wait()
body = np.percentile(np.stack(al), 80, axis=0) > 160
body = cv2.erode(body.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
rows = np.where(body.any(axis=1))[0]
neck = int(rows[0] + 0.33 * (rows[-1] - rows[0]))   # the shape below about a third of the way down = shoulders and torso
body[:neck] = 0
body = cv2.GaussianBlur(body.astype(np.float32) * 255, (0, 0), 3).astype(np.uint8)
del al

# pass 2
p = dec()
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "18", "-b:v", "0", "-row-mt", "1", "-auto-alt-ref", "0", out], stdin=subprocess.PIPE)
n = 0
while True:
    buf = p.stdout.read(W * H * 4)
    if len(buf) < W * H * 4: break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 4).copy()
    a = np.maximum(f[:, :, 3], body)
    solid = cv2.morphologyEx((a > 100).astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    pad = np.pad(solid, 1); flood = pad.copy(); m = np.zeros((H + 4, W + 4), np.uint8)
    cv2.floodFill(flood, m, (0, 0), 1)
    inside = cv2.erode(((pad | (1 - flood))[1:-1, 1:-1]).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    a[inside] = 255
    f[:, :, 3] = a
    enc.stdin.write(f.tobytes()); n += 1
enc.stdin.close(); enc.wait(); p.wait()
print(n, "frames; body shape from row", neck)
