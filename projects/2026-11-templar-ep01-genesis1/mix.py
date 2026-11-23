"""Final mix for a Templar episode (replaces mix.sh).

usage: python3 mix.py <plan.json> <voice wav> <out wav> --bed <music file> --chant <music/video file>
                      [--fire <fire file>] [--bed-start 0] [--chant-start 60]

- Voice: the owner-approved fuller chain (VOICE_FX), to -16 LUFS, delayed by plan.offset, with the
  plan's music-only gaps inserted (so it matches the video timing).
- Bed (e.g. "Landscape KT"): under the whole episode, about 15 LU below the voice; dips during chant.
- Chant: only where Mark is not speaking (plan.chant regions: title, book-closing swell, end card).
- Fire (owner's real fire effect, optional) under everything, low. SFX from audio/synth_sfx.py.
- Final: two-pass loudnorm to -14 LUFS, true peak -1.5 dB, 48 kHz stereo.
"""
import argparse, json, subprocess, os, numpy as np, soundfile as sf

VOICE_FX = ("highpass=f=55,lowshelf=f=140:g=4.5:w=0.7,equalizer=f=250:t=q:w=1.1:g=1.5,equalizer=f=480:t=q:w=1.4:g=-2,"
            "equalizer=f=3200:t=q:w=1.2:g=2,highshelf=f=9000:g=1.5,"
            "acompressor=threshold=-28dB:ratio=2.5:attack=20:release=200:makeup=3,"
            "acompressor=threshold=-18dB:ratio=4:attack=5:release=120:makeup=1,aecho=0.9:0.6:28|47:0.07|0.05")
SR = 48000
ap = argparse.ArgumentParser()
ap.add_argument('plan'); ap.add_argument('voice'); ap.add_argument('out')
ap.add_argument('--bed', required=True); ap.add_argument('--chant', required=True); ap.add_argument('--fire')
ap.add_argument('--bed-start', type=float, default=0); ap.add_argument('--chant-start', type=float, default=60)
ap.add_argument('--bed-lufs', type=float, default=-31); ap.add_argument('--chant-lufs', type=float, default=-20)
ap.add_argument('--fire-lufs', type=float, default=-36)
a = ap.parse_args()
D = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(D, 'work'); os.makedirs(W, exist_ok=True)
plan = json.load(open(a.plan)); DUR = plan['duration']; N = int(DUR * SR)

def ff(*args): subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)
def load(path):
    y, sr = sf.read(path, always_2d=True); assert sr == SR
    return y if y.shape[1] == 2 else np.repeat(y, 2, 1)
def norm_clip(src, start, dur, lufs, out, loop=True):
    pre = ['-stream_loop', '-1'] if loop else []
    ff(*pre, '-ss', str(start), '-i', src, '-t', str(dur), '-vn', '-af', f'loudnorm=I={lufs}:TP=-6:LRA=11,aformat=sample_rates={SR}:channel_layouts=stereo', '-c:a', 'pcm_f32le', out)
    return load(out)
def ramp(n, t_in, t_out):
    e = np.ones(n); i, o = int(t_in * SR), int(t_out * SR)
    if i: e[:i] = np.linspace(0, 1, i)
    if o: e[-o:] = np.minimum(e[-o:], np.linspace(1, 0, o))
    return e

# voice
vp = os.path.join(W, 'voice_proc.wav')
ff('-i', a.voice, '-af', VOICE_FX + ',loudnorm=I=-16:TP=-2:LRA=7', '-ar', str(SR), '-ac', '1', '-c:a', 'pcm_f32le', vp)
v, _ = sf.read(vp)
voice = np.zeros(N); pos_src = 0.0; cur = plan['offset']
for at, secs in sorted(plan.get('gaps', [])) + [[len(v) / SR, 0]]:
    seg = v[int(pos_src * SR):int(at * SR)]
    s = int(cur * SR); voice[s:s + len(seg)] = seg[:max(0, N - s)]
    cur += (at - pos_src) + secs; pos_src = at
voice = np.repeat(voice[:, None], 2, 1)

# bed with dips under the chant
bed = norm_clip(a.bed, a.bed_start, DUR, a.bed_lufs, os.path.join(W, 'bed.wav'))[:N]
bed = np.pad(bed, ((0, N - len(bed)), (0, 0)))
bed_env = np.ones(N)
chant = np.zeros((N, 2))
for k, (c0, c1) in enumerate(plan.get('chant', [])):
    dur = c1 - c0
    seg = norm_clip(a.chant, a.chant_start + 150 * k, dur, a.chant_lufs, os.path.join(W, f'chant{k}.wav'))[: int(dur * SR)]
    fin = 0.05 if c0 == 0 else 1.5
    seg = seg * ramp(len(seg), fin, min(3.0, dur / 2))[:, None]
    s = int(c0 * SR); chant[s:s + len(seg)] += seg[:N - s]
    # bed dips about 8 dB while the chant plays, with 1.5 s crossfades
    e = np.ones(N); i0, i1 = s, min(N, s + len(seg)); f = int(1.5 * SR)
    e[i0:i1] = 0.4
    e[max(0, i0 - f):i0] = np.minimum(e[max(0, i0 - f):i0], np.linspace(1, 0.4, i0 - max(0, i0 - f)))
    e[i1:min(N, i1 + f)] = np.minimum(e[i1:min(N, i1 + f)], np.linspace(0.4, 1, min(N, i1 + f) - i1))
    bed_env = np.minimum(bed_env, e)
bed *= ramp(N, 3, 8)[:, None] * bed_env[:, None]

# fire (optional) and SFX
fire = np.zeros((N, 2))
if a.fire:
    one = norm_clip(a.fire, 0, 10 ** 6, a.fire_lufs, os.path.join(W, 'fire_n.wav'), loop=False)
    X = int(3 * SR); fire = one.copy()
    while len(fire) < N:   # seamless loop: 3 s equal-power crossfade at each join
        w = np.sqrt(np.linspace(0, 1, X))[:, None]
        fire = np.concatenate([fire[:-X], fire[-X:] * w[::-1] + one[:X] * w, one[X:]])
    fire = fire[:N] * ramp(N, 3, 8)[:, None]
sfxp = os.path.join(W, 'sfx.wav')
subprocess.run(['python3', os.path.join(D, 'audio/synth_sfx.py'), a.plan, sfxp], check=True)
sfx = load(sfxp)[:N]; sfx = np.pad(sfx, ((0, N - len(sfx)), (0, 0))) * 10 ** (-14 / 20)

pre = os.path.join(W, 'premix.wav')
sf.write(pre, (voice + bed + chant + fire + sfx).astype(np.float32), SR, subtype='FLOAT')
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
ff('-i', pre, '-af', f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
   f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true", '-ar', str(SR), '-c:a', 'pcm_s24le', a.out)
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', a.out, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
print([l.strip() for l in r.splitlines() if l.strip().startswith(('I:', 'Peak:'))][-2:])
