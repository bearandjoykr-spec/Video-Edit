"""DAY 39 opening flash (Joy, 23 Nov): sharp textbook covers, 0.3 s each. Joy's own Wonders photo first, then publisher covers
from the Aladin bookstore pages (raw-footage/day39/covers/, see SOURCE.md). Run from repo root with .venv/bin/python."""
import os
from PIL import Image
OUT = "remotion/public/day38/books"; os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(f"{OUT}/{f}")
C = "raw-footage/day39/covers/"
SRC = ["raw-footage/day39/books/joy-25.webp",   # Wonders Reading/Writing Companion + Practice Book (Joy's photo)
       C + "c0.jpg",            # Let's Go 1 (Oxford)
       C + "ready-action.jpg",  # Ready, Action! Classic — Sleeping Beauty (musical readers; Joy, 23 Nov)
       C + "c2.jpg",            # Bricks Reading 50
       C + "c5.jpg",            # Smart Phonics 1 (e-future)
       C + "spotlight_k.jpg",   # Spotlight on First Phonics (Bricks)
       C + "c7.jpg",            # Hand in Hand Starter (e-future)
       C + "c8.jpg",            # Grammar Space Beginner 1 (NE Build & Grow)
       C + "c13.jpg",           # My First Grammar 1 (e-future)
       C + "c14.jpg"]           # Fly Phonics 3
for i, p in enumerate(SRC):
    im = Image.open(p).convert("RGB"); im.thumbnail((1000, 1000)); im.save(f"{OUT}/b{i}.jpg", quality=92)
print(len(SRC))
