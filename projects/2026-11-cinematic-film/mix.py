"""Sound for the cinematic film: licensed trailer music + synthesized impact SFX, mastered to -14 LUFS / -1 dBTP.

  tools/fx-venv/bin/python projects/2026-11-cinematic-film/mix.py
Writes renders/cinematic-film/mix.wav (48 kHz stereo). Music is never generated (BRAND.md); the SFX are
synthesized here (booms, whooshes, wind), as synth_lofi.py does for other projects.
"""
import os, subprocess, sys
import numpy as np, soundfile as sf, librosa

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f'{HERE}/../..')
sys.path.insert(0, HERE)
from plan import END  # noqa

SR = 48000
MUSIC = f'{HERE}/music/good_b_music-epic-hollywood-trailer-9489.mp3'
BOOMS = [21.5, 53.5, 94.5, 108.6]                 # biggest hits: colour break, climax, title, end card
WHOOSH_INTO = [21.5, 30.0, 37.0, 45.0, 49.0, 53.5, 94.5]
TICKS = [2.0, 5.5, 7.5, 9.5, 12.5, 15.0]          # soft low thumps on the B/W statement cuts
rng = np.random.default_rng(7)


def db(x):
    return 10 ** (x / 20)


def boom(dur=2.8):
    t = np.arange(int(dur * SR)) / SR
    f = 28 + 34 * np.exp(-t * 6)                                   # pitch drops 62 -> 28 Hz
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    hit = rng.standard_normal(len(t)) * np.exp(-t * 28)
    hit = np.convolve(hit, np.ones(24) / 24, 'same')                # dull the click
    x = sub + 0.5 * hit
    return x / np.abs(x).max()


def whoosh(dur=0.8):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    env = np.sin(np.pi * (t / dur) ** 1.6) ** 2                     # swells into the hit
    # sweeping band-pass via a moving one-pole low-pass minus a slower one
    out = np.zeros(n); lp1 = lp2 = 0.0
    for i in range(n):
        a1 = 0.02 + 0.25 * (t[i] / dur); a2 = 0.004
        lp1 += a1 * (noise[i] - lp1); lp2 += a2 * (lp1 - lp2); out[i] = lp1 - lp2
    x = out * env
    return x / np.abs(x).max()


def thump(dur=0.9):
    t = np.arange(int(dur * SR)) / SR
    x = np.sin(2 * np.pi * (45 + 20 * np.exp(-t * 20)) * t) * np.exp(-t * 5)
    return x / np.abs(x).max()


def wind(dur):
    n = int(dur * SR); x = rng.standard_normal(n)
    for _ in range(3):
        x = np.convolve(x, np.ones(64) / 64, 'same')
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * np.arange(n) / SR)
    x = x * lfo; return x / np.abs(x).max()


def place(bus, sig, t, gain_db, stereo_spread=0.0):
    i = int(t * SR); j = min(len(bus), i + len(sig)); s = sig[:j - i] * db(gain_db)
    bus[i:j, 0] += s * (1 - stereo_spread); bus[i:j, 1] += s * (1 + stereo_spread)


def main():
    n = int(END * SR)
    y, _ = librosa.load(MUSIC, sr=SR, mono=False)
    music = np.zeros((n, 2)); m = y.T[:n]; music[:len(m)] = m
    fade = int(2.0 * SR); music[n - fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
    sfx = np.zeros((n, 2))
    for t in BOOMS:
        place(sfx, boom(), t, -6)
    w = whoosh()
    for k, t in enumerate(WHOOSH_INTO):
        place(sfx, w, t - 0.8, -13, stereo_spread=0.3 * (1 if k % 2 else -1))
    for t in TICKS:
        place(sfx, thump(), t, -14)
    wd = wind(21.5); wd[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))
    place(sfx, wd, 0.0, -30)
    mix = music + sfx
    os.makedirs(f'{ROOT}/renders/cinematic-film', exist_ok=True)
    raw = f'{ROOT}/renders/cinematic-film/mix_raw.wav'; out = f'{ROOT}/renders/cinematic-film/mix.wav'
    sf.write(raw, (mix / max(1.0, np.abs(mix).max())).astype(np.float32), SR, subtype='FLOAT')
    # two-pass loudnorm to -14 LUFS, -1 dBTP
    meas = subprocess.run(['ffmpeg', '-hide_banner', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json',
                           '-f', 'null', '-'], capture_output=True, text=True).stderr
    import json, re
    j = json.loads(re.findall(r'\{[^{}]+\}', meas)[-1])
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', af, '-ar', str(SR), '-c:a', 'pcm_s24le', out], check=True)
    # linear loudnorm can land a little hot; trim the gain so integrated loudness is -14 LUFS
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', out, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])
    if abs(I + 14) > 0.2:
        tmp = out + '.tmp.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out, '-af', f'volume={-14 - I:.2f}dB', '-c:a', 'pcm_s24le', tmp], check=True)
        os.replace(tmp, out)
    chk = subprocess.run(['ffmpeg', '-hide_banner', '-i', out, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr.splitlines()[-12:]
    print('\n'.join(chk))


if __name__ == '__main__':
    main()
