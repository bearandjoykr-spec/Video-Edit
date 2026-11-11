"""Round glasses + lightning scar tracked to Mark's face for the hook (owner request, 11 Nov 2026).

Usage (repo root): python3 projects/2026-11-day29-christmas-phrases/face_props.py SRC START END OUT_DIR
Writes a transparent PNG per frame (1080x1920) to OUT_DIR, plus track.json.
Encode: ffmpeg -framerate 30 -i OUT_DIR/%04d.png -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 4M props.webm
"""
import json, sys, math
import cv2, numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

src, t0, t1, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
MODEL = "/opt/tools/models/face_landmarker.task"
import os; os.makedirs(out, exist_ok=True)

lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL), running_mode=vision.RunningMode.VIDEO, num_faces=1))

cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_POS_MSEC, t0 * 1000)
W, H = int(cap.get(3)), int(cap.get(4))
track, prev = [], None
n = 0
while True:
    ok, frame = cap.read()
    if not ok or n >= round((t1 - t0) * fps): break
    res = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)), int(n * 1000 / fps))
    if res.face_landmarks:
        p = np.array([[q.x * W, q.y * H] for q in res.face_landmarks[0]])
        cur = dict(
            le=p[[33, 133, 159, 145]].mean(0), re=p[[362, 263, 386, 374]].mean(0),
            lt=p[127], rt=p[356], brow=p[9], top=p[10],
        )
        if prev:  # light smoothing against jitter
            cur = {k: 0.55 * cur[k] + 0.45 * prev[k] for k in cur}
        prev = cur
    track.append({k: v.tolist() for k, v in prev.items()} if prev else None)
    n += 1

def draw(c, i):
    img = np.zeros((H, W, 4), np.uint8)
    if c is None: return img
    le, re, lt, rt, brow, top = (np.array(c[k]) for k in ("le", "re", "lt", "rt", "brow", "top"))
    d = np.linalg.norm(re - le); ang = math.atan2(*(re - le)[::-1])
    r = int(d * 0.37); th = max(3, int(d * 0.045))
    S = 4  # supersample for smooth edges
    big = np.zeros((H * S, W * S, 4), np.uint8)
    col = (25, 22, 20, 255)
    def P(v): return tuple(int(x * S) for x in v)
    up = np.array([math.sin(ang), -math.cos(ang)])  # perpendicular, pointing up the face
    for e in (le, re):
        cv2.circle(big, P(e), r * S, col, th * S, cv2.LINE_AA)
        cv2.circle(big, P(e + up * r * 0.35 - np.array([math.cos(ang), math.sin(ang)]) * r * 0.3), int(r * 0.10 * S), (255, 255, 255, 45), -1, cv2.LINE_AA)  # glint
    ux = (re - le) / d
    a, b = le + ux * r, re - ux * r
    mid = (a + b) / 2 + up * r * 0.25
    cv2.polylines(big, [np.array([P(a), P(mid), P(b)])], False, col, th * S, cv2.LINE_AA)
    cv2.line(big, P(le - ux * r), P(lt), col, th * S, cv2.LINE_AA)
    cv2.line(big, P(re + ux * r), P(rt), col, th * S, cv2.LINE_AA)
    # lightning-bolt scar: forehead, slightly to Mark's right (viewer's left)
    fx = brow + (top - brow) * 0.72 - ux * d * 0.22
    s = d * 0.42
    bolt = np.array([[0.05, -0.5], [-0.12, -0.02], [0.04, -0.02], [-0.06, 0.5], [0.16, -0.12], [0.0, -0.12], [0.12, -0.5]])
    R = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    pts = (bolt * s) @ R.T + fx
    cv2.fillPoly(big, [np.array([P(q) for q in pts])], (70, 60, 150, 165), cv2.LINE_AA)
    img = cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    return img

for i, c in enumerate(track):
    cv2.imwrite(f"{out}/{i:04d}.png", draw(c, i))
json.dump({"fps": fps, "start": t0, "frames": track}, open(f"{out}/track.json", "w"))
print("frames", len(track), "missing", sum(t is None for t in track))
