"""DAY 35: fill holes inside Joy's matte (Joy, 19 Nov 2026: the scarf flickered). The model's outline is clean, but on some
frames it makes the beige scarf and the black mic half-transparent. Every pixel enclosed by her silhouette becomes opaque;
the soft outer edge is kept. Run (repo root): tools/fx-venv/bin/python projects/2026-11-day35-expo/fill_matte.py IN.webm OUT.webm"""
import subprocess, sys
import cv2, numpy as np

src, out = sys.argv[1:3]
W, H = 1080, 1920
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "18", "-b:v", "0", "-row-mt", "1", "-auto-alt-ref", "0", out], stdin=subprocess.PIPE)
n, filled_px = 0, 0
while True:
    buf = dec.stdout.read(W * H * 4)
    if len(buf) < W * H * 4:
        break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 4).copy()
    a = f[:, :, 3]
    solid = (a > 100).astype(np.uint8)
    solid = cv2.morphologyEx(solid, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    # flood the background from the frame border; whatever it cannot reach is inside her
    pad = np.pad(solid, 1); flood = pad.copy(); m = np.zeros((H + 4, W + 4), np.uint8)
    cv2.floodFill(flood, m, (0, 0), 1)
    inside = (pad | (1 - flood))[1:-1, 1:-1].astype(bool)
    inside = cv2.erode(inside.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)  # keep the soft edge as it was
    filled_px += int(((a < 250) & inside).sum())
    a[inside] = 255
    f[:, :, 3] = a
    enc.stdin.write(f.tobytes()); n += 1
enc.stdin.close(); enc.wait(); dec.wait()
print(f"{n} frames, {filled_px / max(n, 1):.0f} px filled per frame on average")
