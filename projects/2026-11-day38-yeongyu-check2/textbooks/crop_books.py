"""Close-ups of real textbooks from Joy's photos (raw-footage/day39/books/, sent 23 Nov) for the DAY 39 opening flash.
No 영유 brand signs or logos in any crop (Joy: don't name the 영유). Run from repo root with .venv/bin/python."""
import os
from PIL import Image, ImageOps
SRC, OUT = "raw-footage/day39/books", "remotion/public/day38/books"
os.makedirs(OUT, exist_ok=True)
CROPS = [  # (photo, left, top, right, bottom)
    ("joy-21", 530, 605, 1110, 890),    # Wonders units 1–6
    ("joy-21", 520, 330, 1055, 585),    # Let's Go 1–5
    ("joy-22", 0, 60, 1000, 1571),      # bookshelf: Fly Phonics, Bricks Reading…
    ("joy-21", 1065, 335, 1540, 590),   # Grammar Space
    ("joy-23", 445, 440, 652, 850),     # Super Simple Songs (Oxford)
    ("joy-21", 520, 45, 1165, 315),     # phonics & vocabulary row
    ("joy-22", 1080, 60, 2000, 1571),   # bookshelf: Wonders Your Turn, Hand in Hand
    ("joy-21", 530, 895, 1445, 1165),   # reading row
]
for i, (p, *box) in enumerate(CROPS):
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{p}.webp")).convert("RGB").crop(box)
    im.thumbnail((1000, 1000)); im.save(f"{OUT}/b{i}.jpg", quality=90)
print(len(CROPS))
