"""Joy's torn-paper children (raw-footage/ai-question/joy-paper-kids.webp, 24 Nov 2026) as layers for animation:
kids-base.png (the scene from y 250 down, raised arms painted out where they cross the wall, top edge fading into our wall) and
kid-arm-a.png / kid-arm-b.png (the two raised arms with their sleeves, to rise naturally from the shoulder).
Run (repo root): tools/fx-venv/bin/python projects/2026-11-ai-question/cut_kids.py"""
import cv2, numpy as np
im = cv2.imread("projects/2026-11-ai-question/faces/kids.png"); h, w = im.shape[:2]; yy, xx = np.mgrid[:h, :w]
lab = cv2.cvtColor(cv2.GaussianBlur(im, (0, 0), 1.5), cv2.COLOR_BGR2LAB).astype(np.float32)
wall = np.median(lab[300:380, 700:900].reshape(-1, 3), axis=0); print("wall BGR", np.median(im[300:380, 700:900].reshape(-1, 3), axis=0))
notwall = np.sqrt(((lab - wall) ** 2 * np.array([.4, 1.5, 1.5])).sum(-1)) > 10
ARMS = {"a": ([(505, 188), (632, 188), (626, 330), (606, 420), (612, 470), (604, 560), (500, 560), (494, 470), (514, 410), (508, 300)], 430, (552, 555)),
        "b": ([(1118, 215), (1240, 215), (1236, 330), (1248, 450), (1250, 565), (1160, 565), (1150, 470), (1158, 380), (1140, 320)], 395, (1200, 560))}
inp = np.zeros((h, w), np.uint8); out = {}
for k, (poly, ywall, piv) in ARMS.items():
    m = np.zeros((h, w), np.uint8); cv2.fillPoly(m, [np.array(poly, np.int32)], 255)
    m = ((m > 0) & notwall).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)); m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lb, st, _ = cv2.connectedComponentsWithStats(m); m = ((lb == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])) * 255).astype(np.uint8)
    inp |= cv2.dilate(((m > 0) & (yy < ywall)).astype(np.uint8) * 255, np.ones((9, 9), np.uint8))
    ys, xs = np.nonzero(m); x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    layer = np.dstack([im, cv2.GaussianBlur(m, (3, 3), 0)])[y0:y1, x0:x1]
    cv2.imwrite(f"remotion/public/paper/kid-arm-{k}.png", layer); out[k] = (int(x0), int(y0), int(x1 - x0), int(y1 - y0), piv)
base = cv2.inpaint(im, inp, 11, cv2.INPAINT_TELEA)
TOP = 250; base = base[TOP:]; a = np.full(base.shape[:2], 255, np.uint8)
fade = np.clip((np.arange(base.shape[0]) - 0) / 160, 0, 1); a = (a * fade[:, None]).astype(np.uint8)
cv2.imwrite("remotion/public/paper/kids-base.png", np.dstack([base, a]))
print({k: v for k, v in out.items()}, "base top", TOP, base.shape)
