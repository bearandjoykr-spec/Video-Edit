"""Cut Mark and Joy out of Joy's torn-paper portrait (raw-footage/ai-question/joy-paper-portrait.webp, 24 Nov 2026).
The AI matte (hyperframes) loses Mark's cream jacket against the cream paper, so the jacket is keyed by colour and merged in.
Joy's waving hand becomes its own piece so it can wave. Run (repo root): tools/fx-venv/bin/python projects/2026-11-ai-question/cut_portrait.py
(needs faces/portrait.png and faces/portrait-cut.png from: npx hyperframes remove-background faces/portrait.png -o faces/portrait-cut.png --device coreml)"""
import cv2, numpy as np
F = "projects/2026-11-ai-question/faces"; O = "remotion/public/paper"
im = cv2.imread(f"{F}/portrait.png"); cut = cv2.imread(f"{F}/portrait-cut.png", cv2.IMREAD_UNCHANGED)
h, w = im.shape[:2]; yy, xx = np.mgrid[:h, :w]
lab = cv2.cvtColor(cv2.GaussianBlur(im, (0, 0), 2), cv2.COLOR_BGR2LAB).astype(np.float32)
bg = np.median(lab[150:280, 1150:1650].reshape(-1, 3), axis=0)
d = np.sqrt(((lab - bg) ** 2 * np.array([.5, 1.6, 1.6])).sum(-1))
label = (xx < 460) & (yy < 548) & (yy > 290)
key = ((d > 11) & (xx < 900) & (yy > 440) & ~label).astype(np.uint8)
key = cv2.morphologyEx(key, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)); key = cv2.morphologyEx(key, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
n, lb, st, _ = cv2.connectedComponentsWithStats(key); key = (lb == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
a = np.maximum(cut[..., 3], key * 255); a[(xx < 340) & (yy < 240)] = 0
cs, _ = cv2.findContours((a > 128).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
fill = np.zeros_like(a); cv2.drawContours(fill, cs, -1, 255, -1); a = cv2.GaussianBlur(np.maximum(a, fill).astype(np.uint8), (3, 3), 0)
rgba = np.dstack([im, a])
# Joy's waving hand (full-image coords), pivot at the wrist
hand = np.array([(838, 540), (1050, 540), (1060, 700), (1010, 790), (930, 800), (850, 700)], np.int32)
hm = np.zeros((h, w), np.uint8); cv2.fillPoly(hm, [hand], 255)
L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
skin = (L > 150) & (A > 135) & (B > 145)                                  # the peach paper of the hand
hm = ((hm > 0) & skin).astype(np.uint8) * 255
hm = cv2.morphologyEx(hm, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)); hm = cv2.morphologyEx(hm, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
n2, lb2, st2, _ = cv2.connectedComponentsWithStats(hm); hm = ((lb2 == 1 + np.argmax(st2[1:, cv2.CC_STAT_AREA])) * 255).astype(np.uint8)
hm = cv2.GaussianBlur(cv2.dilate(hm, np.ones((5, 5), np.uint8)), (5, 5), 0)
im_inp = cv2.inpaint(im, (hm > 60).astype(np.uint8), 9, cv2.INPAINT_TELEA)   # what shows behind the hand when it moves
for name, x0, x1 in (("mark", 0, 862), ("joy", 838, 1676)):
    c = rgba[:, x0:x1].copy()
    if name == "joy":
        c[:, :45, 3] = np.where(yy[:, x0:x0 + 45] > 600, 0, c[:, :45, 3])            # strip of Mark's jacket
        hand_layer = c.copy(); hand_layer[..., 3] = np.minimum(c[..., 3], hm[:, x0:x1])
        c[..., :3] = im_inp[:, x0:x1]
        c[..., 3] = np.where((hm[:, x0:x1] > 60) & (xx[:, x0:x1] < 958), 0, c[..., 3])   # left of her hair it was paper background
    ys, xs = np.nonzero(c[..., 3] > 20); y0, xa = ys.min(), xs.min()
    if name == "joy": y0 = min(y0, 137)
    c = c[y0:, xa:xs.max() + 1]; cv2.imwrite(f"{O}/{name}-bust.png", c); print(name, c.shape, "origin", x0 + xa, y0)
    if name == "joy":
        hl = hand_layer[y0:, xa:xs.max() + 1]; cv2.imwrite(f"{O}/joy-hand.png", hl)
