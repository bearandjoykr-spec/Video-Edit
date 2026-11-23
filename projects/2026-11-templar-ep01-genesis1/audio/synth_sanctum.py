"""Solemn ambient bed for the Templar channel: low drone + slow minor-mode string/organ pad + soft choir 'ah'.
Original, synthesised here (no licensing issues). usage: synth_sanctum.py <seconds> <out.wav>"""
import sys, numpy as np, soundfile as sf
from scipy.signal import oaconvolve as fftconvolve, butter, sosfilt

SR = 48000
dur = float(sys.argv[1]); out = sys.argv[2]
N = int(dur * SR)
rng = np.random.default_rng(7)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
# D aeolian/dorian progression, one chord every 12 s: Dm  Bb  Gm  A(sus)  Dm  F  C  Dm
CH = [[50, 57, 62, 65], [46, 58, 62, 65], [43, 55, 62, 67], [45, 57, 62, 64],
      [50, 57, 62, 69], [41, 57, 60, 65], [48, 55, 60, 64], [50, 57, 62, 65]]
SEG = 12.0
L = np.zeros(N); R = np.zeros(N)
t_all = np.arange(N) / SR

def voice(f, t, kind):
    if kind == 'string':      # detuned saws, softened
        s = 0
        for d in (-0.12, 0.0, 0.13):
            ph = 2 * np.pi * f * (1 + d / 100) * t + rng.uniform(0, 6.28)
            s = s + sum(np.sin(k * ph) / k ** 1.6 for k in range(1, 9))
        return s / 3
    if kind == 'organ':
        ph = 2 * np.pi * f * t
        return np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(4 * ph) + 0.12 * np.sin(3 * ph)
    if kind == 'choir':       # 'ah' formants approximated with harmonic weights + vibrato
        vib = 1 + 0.004 * np.sin(2 * np.pi * 5.1 * t)
        ph = 2 * np.pi * f * np.cumsum(vib) / SR
        w = {1: 1, 2: 0.7, 3: 0.9, 4: 0.5, 5: 0.25, 6: 0.15, 7: 0.1}
        return sum(a * np.sin(k * ph) for k, a in w.items()) / 3

nseg = int(np.ceil(dur / SEG))
for i in range(nseg):
    ch = CH[i % len(CH)]
    a = int(i * SEG * SR); b = min(N, int((i + 1) * SEG * SR + 4 * SR))  # 4 s overlap
    if a >= N: break
    t = t_all[a:b] - t_all[a]
    n = b - a
    env = np.minimum(1, t / 4.0) * np.minimum(1, np.maximum(0, (n / SR - t) / 4.0))
    sig = np.zeros(n)
    for j, m in enumerate(ch):
        sig += 0.22 * voice(hz(m), t, 'string')
        sig += 0.10 * voice(hz(m + 12 if j else m), t, 'organ')
    if i % 2 == 1:
        sig += 0.18 * voice(hz(ch[2] + 12), t, 'choir') * np.sin(np.pi * np.clip(t / (n / SR), 0, 1)) ** 2
    sig *= env
    pan = 0.5 + 0.15 * np.sin(i)
    L[a:b] += sig * (1 - pan) * 2; R[a:b] += sig * pan * 2

drone = 0.35 * (np.sin(2 * np.pi * hz(38) * t_all) + 0.4 * np.sin(2 * np.pi * hz(50) * t_all))
drone *= 0.8 + 0.2 * np.sin(2 * np.pi * t_all / 23)
L += drone; R += drone

sos = butter(4, 2400, 'low', fs=SR, output='sos')
L = sosfilt(sos, L); R = sosfilt(sos, R)
# cathedral reverb: 5 s decaying noise IR, separate per side
ir_t = np.arange(int(5 * SR)) / SR
def ir(seed):
    r = np.random.default_rng(seed).standard_normal(len(ir_t)) * np.exp(-ir_t / 1.3)
    return sosfilt(butter(2, 3000, 'low', fs=SR, output='sos'), r) / 60
L = 0.55 * L + fftconvolve(L, ir(1))[:N]
R = 0.55 * R + fftconvolve(R, ir(2))[:N]
st = np.stack([L, R], 1)
fade = np.minimum(1, t_all / 5)[:, None] * np.minimum(1, (dur - t_all) / 8)[:, None]
st *= fade
st /= np.abs(st).max() / 0.8
sf.write(out, st.astype(np.float32), SR, subtype='PCM_24')
print('wrote', out, dur, 's')
