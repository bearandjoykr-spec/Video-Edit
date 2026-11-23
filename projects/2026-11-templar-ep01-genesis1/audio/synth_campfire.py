"""Campfire ambience: low roar + hiss + random crackles and pops. Original synthesis.
usage: synth_campfire.py <seconds> <out.wav>"""
import sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
SR = 48000; dur = float(sys.argv[1]); N = int(dur * SR)
rng = np.random.default_rng(21)
t = np.arange(N) / SR
def filt(x, kind, f, o=2): return sosfilt(butter(o, f, kind, fs=SR, output='sos'), x)
# slow 'breathing' of the fire
breath = 0.75 + 0.25 * filt(rng.standard_normal(N), 'low', 0.4, 1) * 40
breath = np.clip(breath, 0.4, 1.2)
roar = filt(np.cumsum(rng.standard_normal(N)) * 0.002, 'high', 30)
roar = filt(roar, 'low', 220) * 2.2 * breath
hiss = filt(rng.standard_normal(N), 'band', [1800, 6000]) * 0.012 * breath
out = np.zeros(N)
# crackles: clusters of short noise bursts with fast decay
n_crack = int(dur * 9)
for _ in range(n_crack):
    a = rng.integers(0, N - SR // 10)
    L = int(SR * rng.uniform(0.002, 0.018))
    burst = rng.standard_normal(L) * np.exp(-np.linspace(0, rng.uniform(4, 10), L))
    burst *= rng.uniform(0.05, 0.45) ** 1.5
    out[a:a + L] += burst
# occasional bigger pops (wood snapping)
for _ in range(int(dur / 6)):
    a = rng.integers(0, N - SR // 5); L = int(SR * rng.uniform(0.02, 0.06))
    out[a:a + L] += rng.standard_normal(L) * np.exp(-np.linspace(0, 6, L)) * rng.uniform(0.4, 0.8)
crack = filt(out, 'band', [700, 9000])
mono = roar + hiss + crack
st = np.stack([mono + 0.3 * filt(np.roll(crack, 211), 'high', 1000), mono + 0.3 * filt(np.roll(crack, -173), 'high', 1000)], 1)
fade = (np.minimum(1, t / 3) * np.minimum(1, (dur - t) / 6))[:, None]
st = st * fade; st /= np.abs(st).max() / 0.7
sf.write(sys.argv[2], st.astype(np.float32), SR, subtype='PCM_24'); print('wrote', sys.argv[2])
