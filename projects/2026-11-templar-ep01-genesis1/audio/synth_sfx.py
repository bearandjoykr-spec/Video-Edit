"""Subtle SFX track placed from the plan: book open/close, page turns, chain-mail rustle at the kneel prompt,
ember whoosh for notes, a deep boom on the title cross. All synthesised here.
usage: synth_sfx.py <plan.json> <out.wav>"""
import sys, json, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
SR = 48000
plan = json.load(open(sys.argv[1]))
N = int((plan['duration'] + 1) * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(5)
def filt(x, kind, f, o=2): return sosfilt(butter(o, f, kind, fs=SR, output='sos'), x)
def place(sig, at, gain=1.0, pan=0.5):
    a = int(at * SR); b = min(N, a + len(sig))
    if a < 0 or a >= N: return
    L[a:b] += sig[:b - a] * gain * (1 - pan) * 2; R[a:b] += sig[:b - a] * gain * pan * 2
def env(n, att, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / att) * np.exp(-np.maximum(0, t - att) / dec)

def page_turn():
    d = 0.75; n = int(d * SR); t = np.arange(n) / SR
    swish = filt(rng.standard_normal(n), 'band', [900, 7000]) * np.sin(np.pi * np.clip(t / 0.55, 0, 1)) ** 1.5
    crinkle = np.zeros(n)
    for _ in range(26):
        a = rng.integers(0, int(0.5 * SR)); l = int(SR * rng.uniform(0.002, 0.008))
        crinkle[a:a + l] += rng.standard_normal(l) * np.exp(-np.linspace(0, 6, l)) * rng.uniform(0.2, 0.7)
    flap = filt(rng.standard_normal(n), 'low', 300) * env(n, 0.01, 0.06) * (t > 0.48)
    return 0.5 * swish + 0.35 * filt(crinkle, 'high', 2000) + 0.6 * flap

def thud(depth=1.0):
    n = int(0.8 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (70 + 40 * np.exp(-t * 30)) * t) * np.exp(-t * 9)
    return depth * (body + 0.4 * filt(rng.standard_normal(n), 'low', 500) * np.exp(-t * 25))

def book_open():
    return np.concatenate([thud(0.6)[: int(0.25 * SR)], page_turn() * 1.2])

def book_close():
    s = np.concatenate([page_turn()[: int(0.4 * SR)] * 0.8, thud(1.0)])
    return s

def chainmail():
    d = 1.4; n = int(d * SR); s = np.zeros(n)
    for _ in range(140):
        a = rng.integers(0, int(1.1 * SR)); l = int(0.05 * SR)
        f = rng.uniform(3500, 9000); tt = np.arange(l) / SR
        s[a:a + l] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * rng.uniform(60, 140)) * rng.uniform(0.1, 0.4)
    shape = np.sin(np.pi * np.clip(np.arange(n) / (1.2 * SR), 0, 1))
    cloth = filt(rng.standard_normal(n), 'band', [200, 1500]) * 0.25 * shape
    return (s * shape + cloth) * 0.7

def ember_whoosh():
    d = 1.3; n = int(d * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    lo = filt(noise, 'band', [150, 900]); hi = filt(noise, 'band', [900, 3000])
    shape = (t / d) ** 2 * np.exp(-((t - 0.9) / 0.25) ** 2 * (t > 0.9))
    return (0.7 * lo + 0.3 * hi) * shape

def boom():
    n = int(4 * SR); t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * (38 + 30 * np.exp(-t * 6)) * t) * np.exp(-t * 1.4)
    rumble = filt(rng.standard_normal(n), 'low', 160) * np.exp(-t * 1.0) * 0.6
    return sub + rumble

for s in plan['scenes']:
    if s['type'] == 'title':
        place(boom(), s['from'] + 0.3, 0.55)
    if s['type'] == 'prayer':
        place(chainmail(), s['kneelFrom'] + 0.1, 0.45, 0.55)
    if s['type'] == 'bible':
        place(book_open(), s['from'] + 0.2, 0.5, 0.45)
        for sp in s['spreads'][1:]:
            place(page_turn(), sp['from'] - 0.1, 0.42, 0.5 + rng.uniform(-0.15, 0.15))
        place(book_close(), s['to'] - 2.0, 0.45, 0.5)
    if s['type'] == 'notes':
        for it in s['items']:
            place(ember_whoosh(), it['at'] - 0.9, 0.35, 0.5)
st = np.stack([L, R], 1)
st = filt(st.T, 'high', 35).T
peak = np.abs(st).max()
st = st / peak * 0.5
sf.write(sys.argv[2], st.astype(np.float32), SR, subtype='PCM_24')
print('sfx events written', sys.argv[2])
