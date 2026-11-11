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
        if s.get("silent"): continue  # picture only (e.g. the barrier run for "Off you go")
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

# ── magic SFX (synthesised; cue list from build_plan.py) ──
rng = np.random.default_rng(29)
def bp_noise(dur, f0, f1, q=3.0):
    n = int(dur * SR); x = rng.standard_normal(n)
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(n, 1 / SR); out = np.zeros(n)
    # sweep by summing short windows with moving band centres
    hop = int(0.02 * SR); win = np.hanning(hop * 2)
    for i in range(0, n - 2 * hop, hop):
        c = f0 * (f1 / f0) ** (i / n); seg = x[i:i + 2 * hop] * win
        S = np.fft.rfft(seg); ff = np.fft.rfftfreq(len(seg), 1 / SR)
        S *= np.exp(-0.5 * ((ff - c) / (c / q)) ** 2)
        out[i:i + 2 * hop] += np.fft.irfft(S, len(seg))
    return out
def env_ad(n, a, d):
    t_ = np.arange(n) / SR; return np.minimum(t_ / a, 1) * np.exp(-np.maximum(t_ - a, 0) / d)
def bell(f, dur=1.4, amp=1.0):
    n = int(dur * SR); t_ = np.arange(n) / SR; y = np.zeros(n)
    for ratio, g, dec in ((1, 1, 0.9), (2.76, 0.45, 0.45), (5.4, 0.25, 0.25), (8.93, 0.12, 0.15)):
        y += g * np.sin(2 * np.pi * f * ratio * t_) * np.exp(-t_ / dec)
    return amp * y * np.minimum(t_ / 0.003, 1)
def place(buf, y, at, gain):
    i = int(at * SR)
    if i < 0: y, i = y[-i:], 0
    j = min(len(buf), i + len(y)); buf[i:j] += (y[: j - i] * gain)[:, None]
def make(kind):
    if kind == "whoosh":
        y = bp_noise(0.5, 400, 4500); n = len(y); y *= np.sin(np.linspace(0, np.pi, n)) ** 2; return y / np.abs(y).max()
    if kind == "whoosh_out":
        y = bp_noise(0.45, 4000, 500); n = len(y); y *= np.sin(np.linspace(0, np.pi, n)) ** 2; return y / np.abs(y).max()
    if kind == "swish":
        y = bp_noise(0.28, 1800, 6000, 2.0); n = len(y); y *= np.sin(np.linspace(0, np.pi, n)) ** 3; return y / np.abs(y).max()
    if kind == "ding":
        y = bell(1568, 1.6) + 0.5 * bell(2349, 1.6); return y / np.abs(y).max()
    if kind == "chime":  # quick rising pentatonic glissando
        y = np.zeros(int(1.8 * SR))
        for k, f in enumerate((1047, 1175, 1397, 1568, 1760, 2093)):
            b = bell(f, 1.3, 0.7 + 0.06 * k); i = int(k * 0.055 * SR); y[i:i + len(b)] += b[: len(y) - i]
        return y / np.abs(y).max()
    if kind == "boom":  # countdown slam: low sweep + noise hit + bell sparkle on top
        n = int(1.2 * SR); t_ = np.arange(n) / SR
        f = 110 * np.exp(-t_ * 3) + 38
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ / 0.35)
        hit = rng.standard_normal(n) * np.exp(-t_ / 0.03) * 0.5
        y = y + hit + 0.25 * np.pad(bell(2093, 1.0), (0, n - int(1.0 * SR)))
        return y / np.abs(y).max()
    if kind == "rise":  # magical upward swirl: whoosh sweeping up + rising bell run
        y = bp_noise(1.9, 300, 7000, 2.5); n = len(y); y *= np.sin(np.linspace(0, np.pi, n)) ** 1.5; y /= np.abs(y).max()
        for k, f in enumerate((784, 988, 1175, 1397, 1568, 1976, 2349, 2794)):
            b = bell(f, 0.9, 0.35); i = int((0.15 + k * 0.17) * SR); y[i:i + len(b)] += b[: n - i]
        return y / np.abs(y).max()
    if kind == "sparkle":
        y = np.zeros(int(1.0 * SR))
        for k in range(16):
            f = rng.uniform(2500, 6500); b = bell(f, 0.35, rng.uniform(0.3, 1)); i = int(rng.uniform(0, 0.6) * SR)
            y[i:i + len(b)] += b[: len(y) - i]
        return y / np.abs(y).max()
    raise ValueError(kind)
GAIN = {"rise": 0.16, "boom": 0.30, "whoosh": 0.16, "whoosh_out": 0.12, "swish": 0.14, "ding": 0.10, "chime": 0.09, "sparkle": 0.08}
sfx = np.zeros_like(voice); cache = {}
for c in plan.get("sfx", []):
    y = cache.setdefault(c["k"], make(c["k"]))
    place(sfx, y, c["t"], GAIN[c["k"]])

mix = (voice + film + m + sfx)[:tail]
mix *= 10 ** ((-14 - meter.integrated_loudness(mix)) / 20)
out = f"{P}/versions/{V}/mix.wav"
sf.write(out + ".pre.wav", mix, SR, subtype="FLOAT")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out + ".pre.wav", "-af", "alimiter=limit=0.89:attack=3:release=60:level=disabled",
                "-c:a", "pcm_s24le", out], check=True); os.remove(out + ".pre.wav")
mix, _ = sf.read(out)
print(f"mix {len(mix)/SR:.2f} s, {meter.integrated_loudness(mix):.1f} LUFS, peak {20*np.log10(np.abs(mix).max()):.1f} dBFS")
