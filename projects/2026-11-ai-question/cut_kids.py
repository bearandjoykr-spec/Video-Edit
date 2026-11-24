"""Joy's torn-paper children (raw-footage/ai-question/joy-paper-kids.webp, 24 Nov 2026) as layers.
Joy: cutting the arms off looked unnatural, so the picture stays whole (arms up, as she drew it); only the two raised HANDS are
separate pieces that wave a little at the wrist. Under each hand there is only wall, filled with real wall paper.
kids-base.png = the picture from y 250 down (top edge fades into our wall). Run (repo root): tools/fx-venv/bin/python projects/2026-11-ai-question/cut_kids.py"""
import cv2, numpy as np
im = cv2.imread("projects/2026-11-ai-question/faces/kids.png"); h, w = im.shape[:2]; yy, xx = np.mgrid[:h, :w]
lab = cv2.cvtColor(cv2.GaussianBlur(im, (0, 0), 1.2), cv2.COLOR_BGR2LAB).astype(np.float32)
wall = np.median(lab[300:380, 700:900].reshape(-1, 3), axis=0)
notwall = np.sqrt(((lab - wall) ** 2 * np.array([.4, 1.5, 1.5])).sum(-1)) > 10
HANDS = {"a": ((505, 185, 632, 312), (566, 300)), "b": ((1118, 212, 1242, 318), (1186, 312))}
patch = im[262:398, 690:890]; tile = np.tile(patch, (h // patch.shape[0] + 1, w // patch.shape[1] + 1, 1))[:h, :w]
base = im.copy()
for k, ((x0, y0, x1, y1), piv) in HANDS.items():
    m = np.zeros((h, w), np.uint8); m[y0:y1, x0:x1] = 255; m = ((m > 0) & notwall).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lb, st, _ = cv2.connectedComponentsWithStats(m); m = ((lb == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])) * 255).astype(np.uint8)
    layer = np.dstack([im, cv2.GaussianBlur(m, (3, 3), 0)])[y0:y1, x0:x1]; cv2.imwrite(f"remotion/public/paper/kid-hand-{k}.png", layer)
    # behind the hand: wall paper only above the wrist (the forearm stays in the picture)
    fm = cv2.dilate(m, np.ones((7, 7), np.uint8)) > 0; fm &= yy < piv[1] - 6
    mm = cv2.GaussianBlur(fm.astype(np.float32), (0, 0), 2)[..., None]; mm = np.maximum(mm, fm[..., None].astype(np.float32))
    base = (tile * mm + base * (1 - mm)).astype(np.uint8)
    print(k, (x0, y0, x1 - x0, y1 - y0), piv)
TOP = 150; b = base[TOP:]; a = (255 * np.clip(np.arange(b.shape[0]) / 140, 0, 1))[:, None] * np.ones(b.shape[1])[None]
# keep the green cloud out: fade it to wall colour
cloud = (yy[TOP:] < 262)
b[cloud] = tile[TOP:][cloud]
cv2.imwrite("remotion/public/paper/kids-base.png", np.dstack([b, a.astype(np.uint8)])); print("top", TOP, b.shape)
