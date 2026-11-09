"""Mix Joy and Mark's voices + SFX, with music on the goodbye and ending only, and mux with the rendered picture.

Usage: .venv/bin/python projects/2026-11-day1-class/mix.py PICTURE OUT_MP4 [FROM_S TO_S]
FROM/TO cut a sample out of the full mix. Final mix -14 LUFS, peaks at or under -1 dBTP.
"""
import json, os, re, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(f"{HERE}/../..")
sys.path.insert(0, f"{ROOT}/projects/2026-11-confidence/audio")
import synth_lofi as syn  # reuse the approved SFX recipes

picture, out = sys.argv[1:3]
frm, to = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (0.0, None)
plan = json.load(open(f"{HERE}/versions/main/timeline.json"))
SRC = f"{ROOT}/raw-footage/day1-hello-bear/source.mov"
A = f"{HERE}/versions/main/audio"; os.makedirs(A, exist_ok=True)
for name, fn in [("pop", syn.pop), ("whoosh", syn.whoosh), ("sparkle", syn.sparkle), ("chime", syn.chime)]:
    syn.write(f"{A}/sfx_{name}.wav", fn())

dur = plan["duration"]; g1 = plan["segments"][0]
# Music: the approved lo-fi recipe with softer drums (class style), low under Joy, then full for recap, reviews and offer.
M = plan["music"]; MUSIC_DB, UNDER_VOICE = -9.0, 0.22
for name in ("kick", "snare", "hat"):
    orig = getattr(syn, name)
    setattr(syn, name, (lambda f: (lambda *a, **k: f(*a, **k) * 0.5))(orig))
mlen = M["end"] - M["start"]
mus = syn.lofi(mlen)
tt = np.arange(len(mus)) / syn.SR
env = np.interp(tt, [0, 1.5, M["full"] - M["start"] - .3, M["full"] - M["start"] + .9, mlen - 2.5, mlen], [0, UNDER_VOICE, UNDER_VOICE, 1, 1, 0])
syn.write(f"{A}/music.wav", mus * env[:, None])
inputs = ["-i", SRC, "-i", f"{A}/music.wav"]
clean = "highpass=f=80,afftdn=nr=8:nf=-40,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=140:makeup=2"
ms0 = int(M["start"] * 1000)
fc = [f"[0:a]atrim={g1['src_s']}:{g1['src_e']},asetpts=PTS-STARTPTS,afade=t=out:st={g1['src_e'] - 0.25}:d=0.25,{clean},apad=whole_dur={dur}[voice]",
      f"[1:a]volume={MUSIC_DB}dB,adelay={ms0}|{ms0}[mus]"]
labels = ["[voice]", "[mus]"]
for k, cue in enumerate(plan["sfx"]):
    inputs += ["-i", f"{A}/sfx_{cue['sound']}.wav"]
    ms = int(round(cue["t"] * 1000))
    fc.append(f"[{k + 2}:a]volume={cue['gain']}dB,adelay={ms}|{ms}[s{k}]")
    labels.append(f"[s{k}]")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,atrim=0:{dur}[mix]")
graph = ";".join(fc)

m = subprocess.run(["ffmpeg", "-hide_banner", *inputs, "-filter_complex", graph + ";[mix]loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[o]", "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", m.stderr)[-1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
wav = f"{A}/mix.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph + f";[mix]{ln},aresample=48000[o]", "-map", "[o]", "-c:a", "pcm_s16le", wav], check=True)
os.makedirs(os.path.dirname(out), exist_ok=True)
seek = ["-ss", str(frm)] + (["-t", str(to - frm)] if to else [])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", picture, *seek, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out], check=True)
print("mixed", out, "| input", j["input_i"], "LUFS")
