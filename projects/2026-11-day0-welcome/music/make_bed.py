"""Builds the music bed: the owner's ukulele track, looped on the beat with short crossfades, ending on the track's natural ending at the end of the video.
Usage: tools/fx-venv/bin/python projects/2026-11-day0-welcome/music/make_bed.py LENGTH_SECONDS   Writes versions/main/audio/music_bed.wav and music/beats.json (beats counted back from the end)."""
import json, os, sys, numpy as np, librosa, soundfile as sf
H = os.path.dirname(os.path.abspath(__file__)); L = float(sys.argv[1]); SR = 48000
y, _ = librosa.load(f"{H}/ukulele.mp3", sr=SR, mono=False); y = y.T if y.ndim > 1 else np.c_[y, y]
tempo, b = librosa.beat.beat_track(y=y.mean(1), sr=SR, units="time"); tempo = float(np.atleast_1d(tempo)[0]); d = len(y) / SR
print("tempo", round(tempo, 1), "beats", len(b), "track", round(d, 1))
period = 60 / tempo * 4 * 8                     # 8 bars
loop_a = next(t for t in b if t > 4)            # after the intro
ends = [t for t in b if t < d - 12]; n = int((ends[-1] - loop_a) // period); loop_b = loop_a + n * period; idx = np.argmin(np.abs(b - loop_b)); loop_b = float(b[idx])
print("loop", round(loop_a, 2), round(loop_b, 2))
X = int(SR * .08)
A, B = int(loop_a * SR), int(loop_b * SR)
# from the end backwards: track tail, then whole loops, then the intro
parts = [y[A:]]; total = len(y) - A; body = y[A:B]; beat_rel = []
while total < L * SR: parts.insert(0, body); total += len(body) - X
out = parts[0]
for p in parts[1:]:
    f = np.linspace(0, 1, X)[:, None]; out = np.r_[out[:-X], out[-X:] * (1 - f) + p[:X] * f, p[X:]]
out = out[-int(L * SR):]
sf.write(f"{H}/../versions/main/audio/music_bed.wav", out, SR, subtype="PCM_16")
# beats counted back from the end of the bed
tail = d - b; back = list(tail[b >= loop_a])
per = (B - A - X) / SR; m = list(back); k = 1
while m and max(m) < L and k < 12:
    m += [x + per * k + d - loop_b - (d - loop_b) for x in tail[(b >= loop_a) & (b < loop_b)]]; k += 1
json.dump({"tempo": tempo, "from_end": sorted(round(float(x), 3) for x in m if x <= L)}, open(f"{H}/beats.json", "w"))
print("bed", round(len(out) / SR, 1), "beats saved", len(m))
