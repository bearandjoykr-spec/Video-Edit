"""Clearer voice track for Day 28 (Joy, 10 Nov 2026: Mark's English sounded muffled).

Mark's recorded lines reached Joy's mic through the room, so they are boomy and smeared. For his lines only:
DeepFilterNet (noise + room reduction), then the Day 25 clarity EQ (less boom, more presence), a de-esser and compression.
Joy's own voice stays as recorded. Writes versions/main/audio/voice.wav (48 kHz mono), which mix.py uses.
Usage (repo root): tools/fx-venv/bin/python projects/2026-11-day28-questions/voice.py
"""
import json, os, subprocess
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
A = f"{HERE}/versions/main/audio"
os.makedirs(f"{A}/df", exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "remotion/public/day28/main/cut.mov", "-ac", "1", "-ar", "48000", f"{A}/raw.wav"], check=True)
subprocess.run(["tools/deepfilter/deep-filter", "-a", "30", "-D", "-o", f"{A}/df", f"{A}/raw.wav"], check=True, capture_output=True)
EQ = ("highpass=f=110:poles=2,lowshelf=f=220:g=-5,equalizer=f=400:t=q:w=1.2:g=-2.5,equalizer=f=1500:t=q:w=1:g=2,"
      "equalizer=f=3000:t=q:w=0.9:g=5,deesser=i=0.35:f=0.45,highshelf=f=9000:g=2,"
      "acompressor=threshold=-24dB:ratio=3:attack=5:release=100:makeup=2")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{A}/df/raw.wav", "-af", EQ, "-ar", "48000", f"{A}/mark_clean.wav"], check=True)
raw, sr = sf.read(f"{A}/raw.wav"); cl, _ = sf.read(f"{A}/mark_clean.wav")
cl = cl[:len(raw)]; cl = np.pad(cl, (0, len(raw) - len(cl)))
w = np.zeros(len(raw)); f = int(0.04 * sr)
for a, b in json.load(open(f"{HERE}/versions/main/mark_ranges.json")):
    i, j = int((a - 0.12) * sr), int((b + 0.15) * sr)
    w[i:j] = 1
    w[i - f:i] = np.linspace(0, 1, f); w[j:j + f] = np.linspace(1, 0, f)
# match Mark's cleaned level to his original loudness (RMS within his lines) so the mix chain stays the same
m = w > 0.99
cl *= np.sqrt(np.mean(raw[m] ** 2) / max(np.mean(cl[m] ** 2), 1e-12))
sf.write(f"{A}/voice.wav", raw * (1 - w) + cl * w, sr)
print("voice ->", f"{A}/voice.wav")
