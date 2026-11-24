"""Turn Joy's and Mark's faces into cut-paper portraits like Joy's reference (24 Nov 2026): flat paper layers in a few tones,
each layer's edge casting a small shadow on the one below, crumpled-paper light on top. Done here with OpenCV (no AI images).
Input: faces/*-cut.png (avatars with the background removed). Output: remotion/public/paper/*-head.png.
Run (repo root): tools/fx-venv/bin/python projects/2026-11-ai-question/papercut_face.py"""
import cv2, numpy as np
D = "projects/2026-11-ai-question/faces"
tex = cv2.imread("remotion/public/paper/tex-crumple.png", 0).astype(np.float32)
for n, k in (("joy", 11), ("mark", 11)):
    im = cv2.imread(f"{D}/{n}-cut.png", cv2.IMREAD_UNCHANGED); im = cv2.resize(im, (960, 960), interpolation=cv2.INTER_LANCZOS4)
    yy, xx = np.mgrid[:960, :960]; circ = ((xx - 480) ** 2 + (yy - 480) ** 2) < 418 ** 2
    a = (im[..., 3] > 128) & circ; bgr = im[..., :3]
    sm = bgr.copy()
    for _ in range(4): sm = cv2.bilateralFilter(sm, 11, 40, 9)
    lab = cv2.cvtColor(sm, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32); pts = lab[a.reshape(-1)]
    _, lbl, cen = cv2.kmeans(pts, k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, .5), 4, cv2.KMEANS_PP_CENTERS)
    full = np.zeros(960 * 960, np.int32); full[a.reshape(-1)] = lbl[:, 0] + 1; full = full.reshape(960, 960).astype(np.uint8)
    full = cv2.medianBlur(full, 9); full = cv2.medianBlur(full, 7)        # simplify shapes like cut paper
    order = np.argsort(cen[:, 0])                                          # dark layers at the bottom, light ones on top
    out = np.zeros((960, 960, 3), np.float32)
    cols = cv2.cvtColor(cen.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_LAB2BGR).reshape(-1, 3).astype(np.float32)
    for rank, ci in enumerate(order):
        m = (full == ci + 1)
        out[m] = cols[ci]
    # layer edges: each lighter layer casts a soft shadow onto darker ones (light from the top-left)
    L = np.zeros((960, 960), np.float32)
    for rank, ci in enumerate(order): L[full == ci + 1] = rank + 1
    up = cv2.GaussianBlur(L, (0, 0), 3); shift = np.roll(np.roll(up, 4, 0), 4, 1)
    shadow = np.clip(shift - L, 0, 3) * 18; light = np.clip(L - np.roll(np.roll(up, -2, 0), -2, 1), 0, 3) * 10
    out = out - shadow[..., None] + light[..., None]
    # thin drawn lines where the face has real detail (eyes, brows, lips), like the pencil lines on the reference
    g = cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY); ed = cv2.Canny(cv2.GaussianBlur(g, (0, 0), 1.6), 40, 90) * a
    ed = cv2.GaussianBlur(cv2.dilate(ed, np.ones((2, 2), np.uint8)).astype(np.float32), (0, 0), .8) / 255
    out = out * (1 - ed[..., None] * .55)
    t = cv2.resize(tex, (960, 960)); out = out * (0.86 + (t / 255) * .28)[..., None]
    out = np.clip(out + np.random.default_rng(2).normal(0, 3, (960, 960, 1)), 0, 255).astype(np.uint8)
    alpha = (full > 0).astype(np.uint8) * 255
    border = cv2.dilate(alpha, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    res = np.dstack([np.where(alpha[..., None] > 0, out, np.array([238, 244, 248], np.uint8)), border])
    ys, xs = np.nonzero(border); res = res[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    cv2.imwrite(f"remotion/public/paper/{n}-head.png", res); print(n, res.shape)
