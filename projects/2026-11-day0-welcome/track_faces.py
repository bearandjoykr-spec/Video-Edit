"""Face positions through the source, so stickers can follow heads. Writes versions/main/faces.json: {"fps":5,"mark":[[cx,top,w]...],"joy":[...]} in 1920x1080 source pixels.
Run: tools/fx-venv/bin/python projects/2026-11-day0-welcome/track_faces.py"""
import json, cv2, mediapipe as mp
from mediapipe.tasks import python as P
from mediapipe.tasks.python import vision as V
d = V.FaceDetector.create_from_options(V.FaceDetectorOptions(base_options=P.BaseOptions(model_asset_path="tools/models/blaze_face_short_range.tflite"), min_detection_confidence=.3))
cap = cv2.VideoCapture("raw-footage/day0-welcome/source.mp4"); fps = cap.get(5); step = round(fps / 5)
mark, joy = [], []; lm, lj = [620, 150, 300], [1280, 200, 280]; i = 0; miss = 0
while True:
    ok, f = cap.read()
    if not ok: break
    if i % step == 0:
        r = d.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(f, cv2.COLOR_BGR2RGB)))
        bs = sorted([(b.bounding_box.origin_x + b.bounding_box.width / 2, b.bounding_box.origin_y, b.bounding_box.width) for b in r.detections])
        for b in bs:
            if b[0] < 950: lm = list(b)
            else: lj = list(b)
        if len(bs) < 2: miss += 1
        mark.append([round(x) for x in lm]); joy.append([round(x) for x in lj])
    i += 1
json.dump({"fps": 5, "mark": mark, "joy": joy}, open("projects/2026-11-day0-welcome/versions/main/faces.json", "w"))
print("samples", len(mark), "frames with a face missing", miss, "first", mark[10], joy[10])
