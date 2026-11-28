"""DAY 42 Mark cut-out, done properly (Joy, 28 Nov: "마크 누끼 제대로 따줘"). The AI matte (hyperframes) kept bits of the chairs and
room; MediaPipe's selfie multiclass segmenter knows hair/body/face/clothes only, so alpha = hyperframes matte ∩ (person mask grown 7 px),
largest blob kept, holes filled, edge softened, smoothed over time. Model: tools/models/selfie_multiclass.tflite (Google MediaPipe).
Run (repo root): tools/fx-venv/bin/python projects/2026-11-day42-bookshelf/clean_matte.py"""
import subprocess
import cv2, numpy as np, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
P = "projects/2026-11-day42-bookshelf/work"; OUT = "remotion/public/day42/mark-clean.webm"; W, H, CH = 1080, 1920, 1700
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path="tools/models/selfie_multiclass.tflite"),
                                                                             output_confidence_masks=True))
def frames(cmd, ch):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * ch)
        if len(b) < W * H * ch: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, ch)
src = frames(["ffmpeg", "-v", "error", "-i", f"{P}/src.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], 3)
mat = frames(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", f"{P}/matte.webm", "-f", "rawvideo", "-pix_fmt", "rgba", "-"], 4)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{CH}", "-r", "30", "-i", "-",
                        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "5M", "-auto-alt-ref", "0", OUT], stdin=subprocess.PIPE)
ema = None; k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
for rgb, m in zip(src, mat):
    r = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
    bg = np.squeeze(r.confidence_masks[0].numpy_view())          # class 0 = background
    pc = 1 - bg                                                  # person confidence
    near = cv2.dilate((pc > .35).astype(np.uint8), k)            # where a person can be (kills chairs and room)
    hf = m[..., 3].astype(np.float32)
    # Joy (28 Nov): arms must be solid — a moving (blurred) arm is solid where either model sees it, no ghost trails
    solid = ((hf > 70) | ((pc > .5) & (hf > 20))) & (near > 0)
    solid[1330:, 880:] = False; solid[1380:, :130] = False      # chair backs at his sides, low down
    hard = solid.astype(np.uint8)
    hard = cv2.morphologyEx(hard, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    n, lb, st, _ = cv2.connectedComponentsWithStats(hard)
    if n > 1: hard = (lb == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    cs, _ = cv2.findContours(hard, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); fill = np.zeros_like(hard); cv2.drawContours(fill, cs, -1, 1, -1)
    a = cv2.GaussianBlur(fill.astype(np.float32) * 255, (5, 5), 1.2)
    ema = a if ema is None else np.where(np.abs(a - ema) > 60, a, ema * .3 + a * .7)   # steady edges, but no trails when he moves
    out = np.dstack([rgb, cv2.GaussianBlur(ema, (3, 3), 0).clip(0, 255).astype(np.uint8)])[:CH]
    enc.stdin.write(out.tobytes())
enc.stdin.close(); enc.wait(); print("ok")
