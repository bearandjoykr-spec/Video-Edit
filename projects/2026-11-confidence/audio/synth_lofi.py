"""Original lo-fi hip hop bed + punchy reel SFX for Bear & Joy (all synthesised, owner holds all rights).

Usage: python3 synth_lofi.py OUT_DIR TIMELINE_JSON
The timeline may hold "music": {"dropouts": [[s, e], ...], "drops": [t, ...]} in seconds:
dropouts mute the beat (a comic stop), drops restart it with a crash-style hit.
"""
import sys, json, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(23)  # day 23


def write(path, x, peak_db=-1.0):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    x = x / (np.max(np.abs(x)) or 1) * 10 ** (peak_db / 20)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def band(x, lo=None, hi=None):
    """Brick-wall-ish FFT filter with soft edges."""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); g = np.ones_like(f)
    if lo: g *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: g *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * g, len(x))


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def t_(d):
    return np.arange(int(d * SR)) / SR


# --- instruments -------------------------------------------------------------
def kick():
    t = t_(0.42); f = 45 + 85 * np.exp(-t * 28)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    return np.tanh(x * 2.2) * 0.9 + band(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t * 120) * 0.15


def snare():
    t = t_(0.3)
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 22)
    nz = band(rng.standard_normal(len(t)), 1200, 7000) * np.exp(-t * 16)
    return body * 0.5 + nz * 0.7


def hat(open_=False):
    t = t_(0.22 if open_ else 0.06)
    return band(rng.standard_normal(len(t)), 7000, 14000) * np.exp(-t * (14 if open_ else 70))


def rhodes(midi, dur, vel=1.0):
    t = t_(dur); f = hz(midi)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.6 * t)
    x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3)
         + 0.12 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 6))
    env = np.minimum(1, t / 0.012) * np.exp(-t * 0.9) * np.minimum(1, (dur - t) / 0.08)
    return x * env * trem * vel


def bass(midi, dur):
    t = t_(dur); f = hz(midi)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return np.tanh(1.6 * x * np.minimum(1, t / 0.01) * np.exp(-t * 1.6) * np.minimum(1, (dur - t) / 0.05))


def crackle(n):
    x = np.zeros(n); pops = rng.random(n) < 0.0009
    x[pops] = rng.standard_normal(pops.sum()) * 0.9
    return band(x, 800, 9000) * 0.5 + band(rng.standard_normal(n), 2000, 8000) * 0.012


def place(buf, s, t0, gain=1.0, pan=0.5):
    i = int(t0 * SR)
    if i >= len(buf) or i + len(s) <= 0:
        return
    a, b = max(0, i), min(len(buf), i + len(s))
    seg = s[a - i: b - i] * gain
    buf[a:b, 0] += seg * (1 - pan) * 2 ** .5 * .7; buf[a:b, 1] += seg * pan * 2 ** .5 * .7


def lofi(duration, dropouts=(), drops=()):
    bpm = 82; beat = 60 / bpm; bar = 4 * beat; swing = 0.58
    n = int((duration + 1) * SR)
    drums = np.zeros((n, 2)); keys = np.zeros((n, 2)); low = np.zeros((n, 2))
    # Dm9 - G13 - Cmaj9 - A7(b13): classic warm lo-fi loop
    prog = [(50, [65, 69, 72, 76]), (43, [65, 71, 76, 81]), (48, [64, 67, 71, 74]), (45, [67, 72, 76, 77])]
    K, S, H, HO = kick(), snare(), hat(), hat(True)
    bars = int(duration / bar) + 2
    for b in range(bars):
        t0 = b * bar
        root, ch = prog[b % 4]
        for k, m in enumerate(ch):  # slightly strummed chord, held for the bar
            place(keys, rhodes(m, bar * 0.98, 0.55), t0 + k * 0.012 + rng.normal(0, .003), pan=0.35 + 0.1 * k)
        if b % 2:  # little melodic answer on the "and of 3"
            place(keys, rhodes(ch[-1] + 12 - (2 if b % 4 == 3 else 0), beat * 1.4, 0.32), t0 + 2.5 * beat, pan=0.7)
        place(low, bass(root - 12, beat * 1.7), t0)
        place(low, bass(root - 12 + (7 if b % 2 else 0), beat * 0.9), t0 + 2.5 * beat)
        for kt in (0, 1.5 + (0.0 if b % 2 else 0.25), 2.5):
            place(drums, K, t0 + kt * beat, 0.95)
        for st in (1, 3):
            place(drums, S, t0 + st * beat + 0.012, 0.6, pan=0.48)
        for e in range(8):
            pos = (e // 2) * beat + (swing * beat if e % 2 else 0)
            v = 0.32 if e % 2 else 0.45
            place(drums, HO if e == 7 and b % 4 == 3 else H, t0 + pos, v * (0.85 + .3 * rng.random()), pan=0.62)
    tt = np.arange(n) / SR
    gate = np.ones(n)
    for s, e in dropouts:  # comic stop: everything cuts, quick fade back
        gate *= 1 - np.clip((tt - s) / 0.03, 0, 1) * np.clip((e + 0.08 - tt) / 0.08, 0, 1)
    keys = np.stack([band(keys[:, c], 120, 5200) for c in (0, 1)], axis=1)
    drums = np.stack([band(drums[:, c], 40, 9000) for c in (0, 1)], axis=1)
    mix = (drums * 0.9 + keys * 0.55 + low * 0.55) * gate[:, None]
    for d in drops:  # crash on the restart
        place(mix, band(rng.standard_normal(int(1.4 * SR)), 3000, 12000) * np.exp(-t_(1.4) * 3) * 0.6, d)
        place(mix, kick() * 1.2, d)
    c = crackle(n)
    mix += np.stack([c, np.roll(c, 211)], axis=1)
    mix = np.tanh(mix * 1.3) / 1.3  # tape-ish glue
    fade = np.minimum(1, tt / 0.15) * np.clip((duration - tt) / 1.8, 0, 1)
    return (mix * fade[:, None])[: int(duration * SR)]


# --- SFX ---------------------------------------------------------------------
def pop():
    t = t_(0.12); f = 500 + 1400 * (t / 0.12)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)


def whoosh(d=0.35):
    t = t_(d); x = rng.standard_normal(len(t)); env = np.sin(np.pi * t / d) ** 2
    lo = band(x, 300, 2500) * env; hi = band(x, 2500, 9000) * env ** 3
    return lo * 0.8 + hi * 0.5


def sparkle():
    out = np.zeros(int(1.2 * SR))
    for k in range(9):
        t = t_(0.6); f = hz(84 + [0, 4, 7, 11, 12, 16, 19, 23, 24][k])
        s = np.sin(2 * np.pi * f * t) * np.exp(-t * 9)
        i = int(k * 0.045 * SR); out[i:i + len(s)] += s[: len(out) - i] * 0.5
    return out


def impact():
    t = t_(0.9); f = 38 + 60 * np.exp(-t * 18)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    return np.tanh(boom * 2.5) + band(rng.standard_normal(len(t)), 200, 3000) * np.exp(-t * 9) * 0.35


def boing():
    t = t_(0.5); f = 220 + 160 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)


def scratch():
    t = t_(0.42); rate = np.concatenate([np.linspace(1.6, 0.2, len(t) // 2), np.linspace(0.2, 1.8, len(t) - len(t) // 2)])
    src = band(rng.standard_normal(int(len(t) * 2) + 10), 300, 5000)
    idx = np.cumsum(rate).astype(int) % len(src)
    return src[idx] * np.sin(np.pi * t / 0.42) * 0.9


def chime():
    t = t_(1.0)
    return sum(a * np.sin(2 * np.pi * 1568 * r * t) * np.exp(-t * d) for r, a, d in [(1, 1, 4), (2.76, .3, 7), (1.5, .45, 5)])


if __name__ == "__main__":
    out, tl = sys.argv[1], json.load(open(sys.argv[2]))
    m = tl.get("music", {})
    write(f"{out}/music.wav", lofi(tl["duration"], m.get("dropouts", []), m.get("drops", [])))
    for name, fn in [("pop", pop), ("whoosh", whoosh), ("sparkle", sparkle), ("impact", impact), ("boing", boing),
                     ("scratch", scratch), ("chime", chime)]:
        write(f"{out}/sfx_{name}.wav", fn())
    print("lofi + sfx written for", tl["duration"], "s")
