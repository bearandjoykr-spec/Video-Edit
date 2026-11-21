"""DAY 38 mix: Joy's tightened voice (versions/main/voice.wav) + soft music under it + light SFX, -14 LUFS.
Usage (repo root): .venv/bin/python projects/2026-11-day37-yeongyu-check/mix.py PICTURE OUT [MUSIC_DB]"""
import json, os, re, subprocess, sys
P = os.path.dirname(os.path.abspath(__file__)); V = f"{P}/versions/main"
pic, out = sys.argv[1:3]; mdb = float(sys.argv[3]) if len(sys.argv) > 3 else -14
plan = json.load(open(f"{V}/plan.json")); dur = plan["duration"]
music, m0 = "projects/2026-11-day36-top3/music/fashion-lifestyle-628637.mp3", 0.557   # same track as DAY 36 (Pixabay licence)
ins = ["-i", f"{V}/voice.wav", "-ss", str(m0), "-i", music]
fc = [f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=80,apad=whole_dur={dur},atrim=0:{dur},asplit=2[voice][key]",
      f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={mdb}dB,atrim=0:{dur},afade=t=in:d=0.4,afade=t=out:st={dur - 1.5}:d=1.5[m0]",
      "[m0][key]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=350[m]"]
lab = ["[voice]", "[m]"]
for k, c in enumerate(plan["sfx"]):
    ins += ["-i", f"projects/2026-11-day34-bookguide/versions/main/audio/sfx_{c['sound']}.wav"]; ms = int(c["t"] * 1000)
    fc.append(f"[{k + 2}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={c['gain']}dB,adelay={ms}|{ms}[s{k}]"); lab.append(f"[s{k}]")
fc.append("".join(lab) + f"amix=inputs={len(lab)}:normalize=0:duration=first,atrim=0:{dur}[mix]")
g = ";".join(fc)
m = subprocess.run(["ffmpeg", "-hide_banner", *ins, "-filter_complex", g + ";[mix]loudnorm=I=-14:TP=-2:LRA=11:print_format=json[o]", "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", m.stderr)[-1])
ln = f"loudnorm=I=-14:TP=-2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
shift = lambda s: re.sub(r"\[(\d+):a\]", lambda mm: f"[{int(mm.group(1)) + 1}:a]", s)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pic, *ins, "-filter_complex", shift(g) + f";[mix]{ln},aresample=48000[o]", "-map", "0:v", "-map", "[o]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-t", str(dur), out], check=True)
print("mixed ->", out)
