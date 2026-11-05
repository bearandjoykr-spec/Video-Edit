"""Mix a Day 1 promo: voice clips + lo-fi (Reels style, about 8 dB under the voice with -5 dB on this quiet music file, light ducking) + SFX, then mux.

Usage: .venv/bin/python projects/2026-11-day1-promos/mix.py NAME PICTURE OUT_MP4
Final mix -14 LUFS, peaks at or under -1 dBTP.
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(f"{HERE}/../..")
sys.path.insert(0, f"{ROOT}/projects/2026-11-confidence/audio")
import synth_lofi as syn

name, picture, out = sys.argv[1:4]
plan = json.load(open(f"{HERE}/versions/{name}/timeline.json"))
SRC = f"{ROOT}/raw-footage/day1-hello-bear/source.mov"
A = f"{HERE}/versions/{name}/audio"; os.makedirs(A, exist_ok=True)
for n, fn in [("pop", syn.pop), ("whoosh", syn.whoosh), ("sparkle", syn.sparkle), ("impact", syn.impact)]:
    syn.write(f"{A}/sfx_{n}.wav", fn())
dur = plan["duration"]
syn.write(f"{A}/music.wav", syn.lofi(dur))

inputs = ["-i", SRC, "-i", f"{A}/music.wav"]
fc, parts = [], []
for i, g in enumerate(plan["segments"]):
    d = g["src_e"] - g["src_s"]
    fc.append(f"[0:a]atrim={g['src_s']}:{g['src_e']},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d - 0.03}:d=0.03[a{i}]")
    parts.append(f"[a{i}]")
clean = "highpass=f=80,afftdn=nr=8:nf=-40,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3"
fc.append("".join(parts) + f"concat=n={len(parts)}:v=0:a=1,{clean},apad=whole_dur={dur},asplit=2[voice][key]")
fc.append(f"[1:a]volume=-5dB,atrim=0:{dur}[mus0]")
fc.append("[mus0][key]sidechaincompress=threshold=0.02:ratio=2.5:attack=25:release=450[mus]")
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
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
wav = f"{A}/mix.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph + f";[mix]{ln},aresample=48000[o]", "-map", "[o]", "-c:a", "pcm_s16le", wav], check=True)
os.makedirs(os.path.dirname(out), exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", picture, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out], check=True)
print("mixed", name, out, "| input", j["input_i"], "LUFS")
