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
sys.path.insert(0, f"{ROOT}/projects/2026-11-confidence/audio")
import synth_lofi as s  # noqa: E402
for name in ("pop", "whoosh", "sparkle", "impact", "boing", "scratch", "chime"):
    s.write(f"{A}/sfx_{name}.wav", getattr(s, name)())
print("voice + sfx ->", A)
