"""Repair the subject matte where fast hand moves blur and the AI matte drops the hand (owner: "my hand clips and
glitches on the blimey stretch"). For SRC_FROM..SRC_TO: alpha = max(model alpha, temporal max of model alpha over
±R frames × "not the wall" key), so motion-blurred hands stay solid while the plain wall never shows.
Usage (repo root): python3 projects/2026-11-day29-christmas-phrases/fix_matte.py 30.0 38.5 remotion/public/day29/subject-fix-blimey.webm
"""
import subprocess, sys
import numpy as np, cv2

a, b, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
SRC, MATTE = "raw-footage/day29/day29.mov", "remotion/public/day29/subject.webm"
W, H, R = 1080, 1920, 3
n = int(round((b - a) * 30))

def frames(cmd, ch):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for _ in range(n):
        buf = p.stdout.read(W * H * ch)
        if len(buf) < W * H * ch: break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, ch)
    p.stdout.close(); p.wait()

rgb = list(frames(["ffmpeg", "-v", "error", "-ss", str(a), "-i", SRC, "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], 3))
alp = [f[..., 3] for f in frames(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-ss", str(a), "-i", MATTE, "-frames:v", str(n),
                                   "-f", "rawvideo", "-pix_fmt", "rgba", "-"], 4)]
n = min(len(rgb), len(alp))
# wall colour: median of pixels the model is sure are background
bg = np.median(np.concatenate([rgb[i][alp[i] < 10][::97] for i in range(0, n, 10)]), axis=0)
print("wall colour", bg, "frames", n)

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "12M", "-auto-alt-ref", "0", out], stdin=subprocess.PIPE)
fixed = 0
for i in range(n):
    lo, hi = max(0, i - R), min(n, i + R + 1)
    tmax = np.max(np.stack(alp[lo:hi]), axis=0)
    tmax = cv2.dilate(tmax, np.ones((9, 9), np.uint8))
    lab = cv2.cvtColor(rgb[i], cv2.COLOR_RGB2LAB).astype(np.float32)
    bgl = cv2.cvtColor(bg.reshape(1, 1, 3).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)[0, 0]
    d = np.linalg.norm(lab - bgl, axis=2)
    key = np.clip((d - 12) / 18, 0, 1)          # 0 = wall, 1 = clearly not wall
    key = cv2.GaussianBlur(key, (5, 5), 0)
    new = np.maximum(alp[i].astype(np.float32), tmax.astype(np.float32) * key)
    fixed += int((new - alp[i] > 60).sum() > 500)
    enc.stdin.write(np.dstack([rgb[i], new.clip(0, 255).astype(np.uint8)]).tobytes())
enc.stdin.close(); enc.wait()
print("frames repaired:", fixed)
