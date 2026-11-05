"""Mix cleaned voices, SFX and (once the owner has chosen a track) licensed music, then mux with the picture.

Usage: .venv/bin/python projects/2026-11-day0-welcome/mix.py PICTURE OUT_MP4 [--music FILE] [--wav-only]
Voice comes from audio/voice_clean.wav (DeepFilterNet on the source). No music is generated (owner, 5 Nov 2026).
Music: full over the intro and the offer, about 16 dB lower under speech. Final mix -14 LUFS, peaks under -1 dBTP.
"""
import argparse, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/../..")
sys.path.insert(0, f"{ROOT}/projects/2026-11-confidence/audio")
import synth_lofi as syn
ap = argparse.ArgumentParser(); ap.add_argument("picture"); ap.add_argument("out"); ap.add_argument("--music"); a = ap.parse_args()
plan = json.load(open(f"{HERE}/versions/main/timeline.json"))
A = f"{HERE}/versions/main/audio"; dur = plan["duration"]
for name, fn in [("pop", syn.pop), ("whoosh", syn.whoosh), ("sparkle", syn.sparkle), ("chime", syn.chime), ("impact", syn.impact), ("boing", syn.boing)]:
    syn.write(f"{A}/sfx_{name}.wav", fn())
inputs = ["-i", f"{A}/voice_clean.wav"]; fc = []; labels = []
SILENCE = ["-f", "lavfi", "-t", str(dur + 15), "-i", "anullsrc=r=48000:cl=stereo"]  # holds the mix open: loudnorm's lookahead must not cut the ending
clean = "highpass=f=80,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=140:makeup=2"
split = "".join(f"[v{i}]" for i in range(len(plan["segments"])))
fc.append(f"[0:a]{clean},asplit={len(plan['segments'])}{split}")
for i, g in enumerate(plan["segments"]):
    ms = int(round(g["out_s"] * 1000))
    fc.append(f"[v{i}]atrim={g['src_s']}:{g['src_e']},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={g['src_e'] - g['src_s'] - .03:.3f}:d=0.03,adelay={ms}|{ms}[vd{i}]")
    labels.append(f"[vd{i}]")
n = 1
# the owner's montage keeps its own sound
inputs += ["-i", f"{A}/montage.wav"]; fc.append(f"[{n}:a]afade=t=out:st=11.8:d=0.5[mt]"); labels.append("[mt]"); n += 1
if a.music:  # bed starts when the montage ends: full on title and offer, about 16 dB lower under speech
    inputs += ["-i", a.music]
    m0 = next(e["e"] for e in plan["events"] if e["type"] == "montage"); s_, e_ = plan["mainStart"] - m0, plan["mainEnd"] - m0; ms = int(m0 * 1000)
    fc.append(f"[{n}:a]volume='if(between(t,{s_ + .4},{e_ - .4}),0.16,1)':eval=frame,volume=-8dB,afade=t=in:d=0.3,adelay={ms}|{ms}[mus]")
    labels.append("[mus]"); n += 1
for k, cue in enumerate(plan["sfx"]):
    inputs += ["-i", f"{A}/sfx_{cue['sound']}.wav"]
    ms = int(round(cue["t"] * 1000))
    fc.append(f"[{n}:a]volume={cue['gain'] + 6}dB,adelay={ms}|{ms}[s{k}]"); labels.append(f"[s{k}]"); n += 1
inputs += SILENCE; fc.append(f"[{n}:a]anull[pad]"); labels.append("[pad]")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest[mix]")
graph = ";".join(fc)
m = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", *inputs, "-filter_complex", graph + ";[mix]loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[o]", "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
if m.returncode: print(m.stderr[-1500:])
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", m.stderr)[-1])
ln = f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
wav = f"{A}/mix.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph + f";[mix]{ln},aresample=48000,atrim=0:{dur},asetpts=PTS-STARTPTS[o]", "-map", "[o]", "-c:a", "pcm_s16le", wav], check=True)
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
if a.picture != "-":
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.picture, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", a.out], check=True)
print("mixed", wav, "| input", j["input_i"], "LUFS, peak", j["input_tp"])
