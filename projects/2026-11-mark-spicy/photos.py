"""Joy's own class photos as B-roll for DAY 31 (Joy, 15 Nov 2026). Children's faces are always blurred.
Writes raw-footage/new-1113/stock/ph_*.mp4 (1080x1920, 30 fps): each photo sits on a blurred copy of itself and pushes in slowly.
Run (repo root): tools/fx-venv/bin/python projects/2026-11-mark-spicy/photos.py
"""
import os, subprocess
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
P = f"{HERE}/photos"; OUT = "raw-footage/new-1113/stock"; TMP = f"{P}/blurred"; os.makedirs(TMP, exist_ok=True)
# children's heads to blur, (x0, y0, x1, y1) in each photo's own pixels (checked by eye on the contact sheet)
# Joy (15 Nov): don't overdo it, backs of heads need no blur. Only faces turned toward the camera (the stream walk) get a light blur.
KIDS = {
    "p2": [], "p3": [], "p6": [], "p7": [], "p8": [],
    "p4": [(505, 300, 590, 385), (560, 355, 645, 440), (590, 430, 680, 515)],
}
for name, boxes in KIDS.items():
    im = Image.open(f"{P}/{name}.png").convert("RGB")
    blur = im.filter(ImageFilter.GaussianBlur(14))
    mask = Image.new("L", im.size, 0); d = ImageDraw.Draw(mask)
    for b in boxes:
        d.ellipse(b, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(10))
    Image.composite(blur, im, mask).save(f"{TMP}/{name}.png")

def clip(names, dur, out, durs=None):
    """photos one after another (dur seconds each), soft 0.3 s dissolve, slow push-in, blurred fill behind"""
    ins, fc = [], []
    durs = durs or [dur] * len(names)
    for k, n in enumerate(names):
        dur = durs[k]
        ins += ["-loop", "1", "-t", str(dur + 0.3), "-i", f"{TMP}/{n}.png"]
        fc.append(f"[{k}:v]split[a{k}][b{k}];[a{k}]scale=8:8,scale=1080:1920,geq=r='245':g='240':b='230'[bg{k}];"
                  f"[b{k}]scale=1000:-2,zoompan=z='1+0.08*on/{int(dur * 30)}':d=1:s=1000x{{H}}:fps=30[fg{k}];"
                  f"[bg{k}][fg{k}]overlay=(W-w)/2:(H-h)/2-80,fps=30,format=yuv420p,trim=0:{dur + 0.3},setpts=PTS-STARTPTS[c{k}]")
    # zoompan needs the photo's scaled height
    for k, n in enumerate(names):
        w, h = Image.open(f"{TMP}/{n}.png").size
        fc[k] = fc[k].replace("{H}", str(int(round(1000 * h / w / 2) * 2)))
    prev = "c0"; t = durs[0]
    for k in range(1, len(names)):
        fc.append(f"[{prev}][c{k}]xfade=transition=fade:duration=0.3:offset={t - 0.0:.2f}[x{k}]"); prev = f"x{k}"; t += durs[k]
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", f"[{prev}]", "-c:v", "libx264", "-crf", "16", "-r", "30",
                    f"{OUT}/{out}"], check=True)
    print(out)

clip(["p6"], 6.6, "ph_teach.mp4")            # Joy teaching a small group (40-46 s)
clip(["p2", "p3"], 2.6, "ph_look.mp4")       # Mark's high five, the train-track writing game
clip(["p8", "p7"], 0, "ph_fun.mp4", [2.4, 4.3])  # Mark and Joy talking on stage, then laughing (longer). Joy: no stream photo
