"""Voice track: the cut's audio cleaned of the outdoor background noise (DeepFilterNet, limited to 18 dB so it stays natural),
a light clarity EQ and gentle compression. Also writes the sound effects (synth_lofi.py is used for SFX only, never music).
Usage (repo root): python3 projects/2026-11-accent-question/voice.py   -> versions/main/audio/voice.wav + sfx_*.wav
On the Mac the tool is tools/deepfilter/deep-filter as well.
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/../..")
A = f"{HERE}/versions/main/audio"; os.makedirs(f"{A}/df", exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{ROOT}/remotion/public/accentq/main/cut.mov", "-ac", "1", "-ar", "48000", f"{A}/raw.wav"], check=True)
subprocess.run([f"{ROOT}/tools/deepfilter/deep-filter", "-a", "18", "-o", f"{A}/df", f"{A}/raw.wav"], check=True, capture_output=True)
EQ = "highpass=f=90:poles=2,equalizer=f=3000:t=q:w=0.9:g=2.5,highshelf=f=9000:g=1.5,acompressor=threshold=-22dB:ratio=2.5:attack=6:release=110:makeup=2"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{A}/df/raw.wav", "-af", EQ, "-ar", "48000", f"{A}/voice.wav"], check=True)
# Joy's question (owner, 12 Nov 2026: "too piercing, the mic was too close"): a little quieter (about 1.5 dB under Mark), the harsh 2-6 kHz band and the top end tamed
import json  # noqa: E402
import numpy as np, soundfile as sf  # noqa: E402
SOFT = "equalizer=f=3500:t=q:w=1.0:g=-5,highshelf=f=7000:g=-4,deesser=i=0.5:f=0.4,volume=-2dB"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{A}/voice.wav", "-af", SOFT, "-ar", "48000", f"{A}/voice_soft.wav"], check=True)
v, sr = sf.read(f"{A}/voice.wav"); s2, _ = sf.read(f"{A}/voice_soft.wav"); s2 = np.pad(s2[:len(v)], (0, max(0, len(v) - len(s2))))
w = np.zeros(len(v)); f = int(0.05 * sr)
for a, b in json.load(open(f"{HERE}/versions/main/timeline_v2.json"))["joyRanges"]:
    i, j = int(a * sr), int(b * sr)
    w[i:j] = 1; w[max(0, i - f):i] = np.linspace(0, 1, i - max(0, i - f)); w[j:j + f] = np.linspace(1, 0, len(w[j:j + f]))
sf.write(f"{A}/voice.wav", v * (1 - w) + s2 * w, sr)
sys.path.insert(0, f"{ROOT}/projects/2026-11-confidence/audio")
import synth_lofi as s  # noqa: E402
for name in ("pop", "whoosh", "sparkle", "impact", "boing", "scratch", "chime"):
    s.write(f"{A}/sfx_{name}.wav", getattr(s, name)())
print("voice + sfx ->", A)
