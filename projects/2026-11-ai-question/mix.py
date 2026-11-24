"""Mix Mark's voice (audio/voice.wav) with light SFX from the DAY 34 kit (paper whoosh on scene changes, pops on the crosses,
a chime on 'the power to think'), -14 LUFS, no music (Joy adds her own). Usage (repo root): .venv/bin/python projects/2026-11-ai-question/mix.py PICTURE OUT"""
import json, os, re, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__)); pic, out = sys.argv[1:3]
plan = json.load(open(f"{H}/../../remotion/src/paperthink.json")); dur = plan["duration"]
ins = ["-i", f"{H}/audio/voice.wav"]; fc = [f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=70,apad=whole_dur={dur},atrim=0:{dur}[v]"]; lab = ["[v]"]
for k, c in enumerate(plan["sfx"]):
    ms = max(0, int(c["t"] * 1000)); ins += ["-i", f"projects/2026-11-day34-bookguide/versions/main/audio/sfx_{c['sound']}.wav"]
    fc.append(f"[{k + 1}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={c['gain']}dB,adelay={ms}|{ms}[s{k}]"); lab.append(f"[s{k}]")
fc.append("".join(lab) + f"amix=inputs={len(lab)}:normalize=0:duration=first,atrim=0:{dur}[mix]"); g = ";".join(fc)
m = subprocess.run(["ffmpeg", "-hide_banner", *ins, "-filter_complex", g + ";[mix]loudnorm=I=-14:TP=-2:LRA=11:print_format=json[o]", "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", m.stderr)[-1])
ln = f"loudnorm=I=-14:TP=-2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
shift = lambda s: re.sub(r"\[(\d+):a\]", lambda mm: f"[{int(mm.group(1)) + 1}:a]", s)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pic, *ins, "-filter_complex", shift(g) + f";[mix]{ln},aresample=48000[o]", "-map", "0:v", "-map", "[o]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-t", str(dur), out], check=True)
print("mixed ->", out)
