"""Original music-box bed and sound effects for Bear & Joy reels.

Everything here is synthesised from scratch, so the owner holds all rights.
Usage: python3 synth.py OUT_DIR DURATION_SECONDS
Writes music.wav (stereo, 48 kHz) and sfx_*.wav.
"""
import sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def write(path, x):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    peak = np.max(np.abs(x)) or 1.0
    x = x / peak * 0.89  # about -1 dBFS
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def music_box_note(f, dur=2.4, vel=1.0):
    t = np.arange(int(dur * SR)) / SR
    # Inharmonic partials of a struck metal tine, each decaying at its own rate.
    parts = [(1.0, 1.0, 2.2), (2.0, 0.28, 3.5), (3.01, 0.12, 5.0), (5.4, 0.06, 8.0)]
    x = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in parts)
    attack = np.minimum(1, t / 0.004)
    return x * attack * vel


def soft_pad(freqs, dur):
    t = np.arange(int(dur * SR)) / SR
    x = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs)
    env = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 0.8)
    return x * env


def reverb(x, mix=0.3):
    y = np.copy(x)
    for d, g in [(0.031, .5), (0.047, .42), (0.071, .36), (0.113, .3), (0.167, .24), (0.229, .18)]:
        n = int(d * SR)
        y[n:] += g * x[:-n]
    return (1 - mix) * x + mix * y / 2.5


def music(duration):
    bpm = 84
    beat = 60 / bpm
    n = int((duration + 3) * SR)
    L = np.zeros(n); R = np.zeros(n)
    # F major, gentle bedtime progression: F - Dm - Bb - C
    chords = [[53, 57, 60], [50, 53, 57], [46, 50, 53], [48, 52, 55]]
    melody_up = [0, 1, 2, 1]  # arpeggio shape (index into chord, +12)
    bar = 4 * beat
    t0 = 0.0
    k = 0
    while t0 < duration + 1:
        ch = chords[k % 4]
        # pad
        p = soft_pad([hz(m - 12) for m in ch], bar + 0.6) * 0.05
        i = int(t0 * SR); j = min(n, i + len(p))
        L[i:j] += p[: j - i]; R[i:j] += p[: j - i]
        # music-box arpeggio in eighth notes
        for e in range(8):
            m = ch[melody_up[e % 4] if e < 4 else (2 - e % 4) % 3] + 12 + (12 if e in (3,) else 0)
            vel = 0.55 if e % 2 else 0.8
            note = music_box_note(hz(m), vel=vel * (0.9 + 0.2 * rng.random()))
            s = int((t0 + e * beat / 2 + rng.normal(0, 0.006)) * SR)
            if s < 0 or s >= n:
                continue
            j = min(n, s + len(note)); pan = 0.35 + 0.3 * rng.random()
            L[s:j] += note[: j - s] * (1 - pan); R[s:j] += note[: j - s] * pan
        t0 += bar; k += 1
    L = reverb(L); R = reverb(R)
    x = np.stack([L, R], axis=1)[: int(duration * SR)]
    t = np.arange(len(x)) / SR
    fade = np.minimum(1, t / 1.5) * np.minimum(1, (duration - t) / 2.5)
    return x * fade[:, None]


def noise(dur):
    return rng.standard_normal(int(dur * SR))


def lowpass(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc) if np.ndim(a) else a * (x[i] - acc)
        y[i] = acc
    return y


def whoosh(dur=0.45):
    t = np.arange(int(dur * SR)) / SR
    a = 0.02 + 0.25 * np.sin(np.pi * t / dur) ** 2  # sweep filter open then closed
    x = lowpass(noise(dur), a)
    return x * np.sin(np.pi * t / dur) ** 1.5


def chime(base=1396.9):  # F6
    t = np.arange(int(1.6 * SR)) / SR
    x = sum(a * np.sin(2 * np.pi * base * r * t) * np.exp(-t * d) for r, a, d in [(1, 1, 3.0), (2.76, .3, 6), (5.4, .12, 10)])
    x += 0.5 * np.sin(2 * np.pi * base * 1.5 * t) * np.exp(-t * 4) * (t > 0.09)  # second strike, a fifth up
    return reverb(x * np.minimum(1, t / 0.002), 0.35)


def page_turn(dur=0.55):
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-((t - 0.18) / 0.09) ** 2) + 0.6 * np.exp(-((t - 0.36) / 0.05) ** 2)
    crackle = (rng.random(len(t)) < 0.03) * rng.standard_normal(len(t)) * 2
    x = lowpass(noise(dur) + crackle, 0.35) * env
    return x


def tick():
    t = np.arange(int(0.25 * SR)) / SR
    return np.sin(2 * np.pi * 2093 * t) * np.exp(-t * 30) + 0.4 * np.sin(2 * np.pi * 3136 * t) * np.exp(-t * 45)


def rise(dur=0.9):
    """Soft upward shimmer for behind-the-head words."""
    t = np.arange(int(dur * SR)) / SR
    f = 700 + 900 * (t / dur) ** 2
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * 0.25 + lowpass(noise(dur), 0.08) * 0.6
    return reverb(x * (t / dur) ** 1.8 * np.exp(-np.maximum(0, t - dur * .85) * 30), 0.4)


if __name__ == "__main__":
    out, dur = sys.argv[1], float(sys.argv[2])
    write(f"{out}/music.wav", music(dur))
    write(f"{out}/sfx_whoosh.wav", whoosh())
    write(f"{out}/sfx_chime.wav", chime())
    write(f"{out}/sfx_page.wav", page_turn())
    write(f"{out}/sfx_tick.wav", tick())
    write(f"{out}/sfx_rise.wav", rise())
    print("wrote music and sfx for", dur, "s")
