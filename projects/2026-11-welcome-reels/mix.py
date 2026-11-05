"""Mix cleaned voices, SFX and the owner's ukulele for one reel. Usage: .venv/bin/python projects/2026-11-welcome-reels/mix.py NAME PICTURE OUT
Music about 16 dB under speech, full on the end card. Final -14 LUFS, peaks under -1 dBTP."""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f"{HERE}/../.."); W = f"{ROOT}/projects/2026-11-day0-welcome"
sys.path.insert(0, f"{ROOT}/projects/2026-11-confidence/audio")
name, picture, out = sys.argv[1:4]
plan = json.load(open(f"{HERE}/versions/{name}/timeline.json")); dur, sp = plan["duration"], plan["speechEnd"]
A = f"{W}/versions/main/audio"
inputs = ["-i", f"{A}/voice_clean.wav"]; fc = []; labels = []
clean = "highpass=f=80,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=140:makeup=2"
n = len(plan["segments"]); fc.append(f"[0:a]{clean},asplit={n}" + "".join(f"[v{i}]" for i in range(n)))
for i, g in enumerate(plan["segments"]):
    ms = int(round(g["out_s"] * 1000))
    fc.append(f"[v{i}]atrim={g['src_s']}:{g['src_e']},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={g['src_e'] - g['src_s'] - .03:.3f}:d=0.03,adelay={ms}|{ms}[vd{i}]"); labels.append(f"[vd{i}]")
inputs += ["-ss", "4.17", "-i", f"{W}/music/ukulele.mp3"]
fc.append(f"[1:a]atrim=0:{dur},asetpts=PTS-STARTPTS,volume='if(lt(t,{sp - .2}),0.16,1)':eval=frame,volume=-7dB,afade=t=out:st={dur - .9}:d=0.9[mus]"); labels.append("[mus]")
k = 2
for j, c in enumerate(plan["sfx"]):
    inputs += ["-i", f"{A}/sfx_{c['sound']}.wav"]; ms = int(round(c["t"] * 1000))
    fc.append(f"[{k}:a]volume={c['gain'] + 4}dB,adelay={ms}|{ms}[s{j}]"); labels.append(f"[s{j}]"); k += 1
inputs += ["-f", "lavfi", "-t", str(dur + 15), "-i", "anullsrc=r=48000:cl=stereo"]; fc.append(f"[{k}:a]anull[pad]"); labels.append("[pad]")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest[mix]"); g = ";".join(fc)
m = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", *inputs, "-filter_complex", g + ";[mix]loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[o]", "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
if m.returncode: print(m.stderr[-1200:])
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", m.stderr)[-1])
ln = f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
wav = f"{HERE}/versions/{name}/mix.wav"
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *inputs, "-filter_complex", g + f";[mix]{ln},aresample=48000,atrim=0:{dur},asetpts=PTS-STARTPTS[o]", "-map", "[o]", "-c:a", "pcm_s16le", wav], check=True)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", picture, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
print("mixed", name, "input", j["input_i"], "LUFS")
