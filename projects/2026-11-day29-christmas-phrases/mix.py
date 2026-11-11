"""Day 29 audio: Mark's voice segments + film lines (Mark frozen) + Pixabay "School of Magic" under everything.
Usage (repo root): python3 projects/2026-11-day29-christmas-phrases/mix.py [version]
Writes versions/<v>/mix.wav at -14 LUFS. Music about -15 dB under voice with light ducking (BRAND.md, Day 28 feedback),
dipped further under film lines so the line is clear.
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf, pyloudnorm as pyln

V = sys.argv[1] if len(sys.argv) > 1 else "test"
P = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(P))
SR = 48000
plan = json.load(open(f"{P}/versions/{V}/plan.json"))

def load(path, s=None, e=None):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", str(s)] if s is not None else []) + ["-i", path] + \
          (["-t", str(e - s)] if e is not None else []) + ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2)
    return a.copy()

def fades(a, ms=12):
    n = min(len(a) // 2, int(SR * ms / 1000)); r = np.linspace(0, 1, n)[:, None]
    a[:n] *= r; a[-n:] *= r[::-1]; return a

meter = pyln.Meter(SR)
N = int(plan["duration"] * SR) + SR
voice = np.zeros((N, 2), np.float32); film = np.zeros((N, 2), np.float32)
src = f"{R}/raw-footage/day29/day29.mov"
for s in plan["segments"]:
    o = int(s["s"] * SR)
    if s["kind"] == "mark":
        a = fades(load(src, s["src"], s["srcEnd"])); voice[o:o + len(a)] += a
    else:
        a = load(f"{R}/raw-footage/day29/clips/{s['clip']}.mp4", s["clipIn"], s["clipOut"])
        a = fades(a, 60)
        a *= 10 ** ((-20 - meter.integrated_loudness(a)) / 20) if len(a) > SR * 0.4 else 10 ** (-1 / 20)  # match the voice
        lo = int(s["lineS"] * SR); film[lo:lo + len(a)] += a
v_l = meter.integrated_loudness(voice[: int(plan["endCard"]["s"] * SR)])
voice *= 10 ** ((-20 - v_l) / 20)

# music: loop if short, light ducking under speech, deeper dip under film lines, fade out over the end card
m = load(f"{P}/music/school-of-magic.mp3")
m = np.tile(m, (int(np.ceil(N / len(m))), 1))[:N]
m *= 10 ** ((-20 - 15 - meter.integrated_loudness(m)) / 20)  # about 15 dB under the voice
def env(x, win=0.25):
    e = np.sqrt(np.convolve((x ** 2).mean(1), np.ones(int(SR * win)) / int(SR * win), "same"))
    return e
ve, fe = env(voice), env(film)
gate_v = np.clip(ve / (ve.max() * 0.08 + 1e-9), 0, 1); gate_f = np.clip(fe / (fe.max() * 0.08 + 1e-9), 0, 1)
duck_db = -3.0 * gate_v - 8.0 * gate_f
k = int(SR * 0.3); duck_db = np.convolve(duck_db, np.ones(k) / k, "same")
m *= (10 ** (duck_db / 20))[:, None]
end = int(plan["endCard"]["s"] * SR)
m[end:] *= 10 ** (6 / 20)  # music up on the end card
tail = int(plan["duration"] * SR); fo = int(SR * 1.8)
m[tail - fo:tail] *= np.linspace(1, 0, fo)[:, None]; m[tail:] = 0

mix = (voice + film + m)[:tail]
mix *= 10 ** ((-14 - meter.integrated_loudness(mix)) / 20)
out = f"{P}/versions/{V}/mix.wav"
sf.write(out + ".pre.wav", mix, SR, subtype="FLOAT")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out + ".pre.wav", "-af", "alimiter=limit=0.89:attack=3:release=60:level=disabled",
                "-c:a", "pcm_s24le", out], check=True); os.remove(out + ".pre.wav")
mix, _ = sf.read(out)
print(f"mix {len(mix)/SR:.2f} s, {meter.integrated_loudness(mix):.1f} LUFS, peak {20*np.log10(np.abs(mix).max()):.1f} dBFS")
