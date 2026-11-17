"""DAY 34 mix: Joy's music track (no voice-over; captions carry the words) + SFX, -14 LUFS. Run from the repo root.
Usage: .venv/bin/python projects/2026-11-day34-bookguide/mix.py PICTURE OUT [MUSIC] [MUSIC_START]"""
import json, re, subprocess, sys, os
P = os.path.dirname(os.path.abspath(__file__)); V = f"{P}/versions/main"
pic, out = sys.argv[1:3]; music = sys.argv[3] if len(sys.argv) > 3 else f"{P}/music/ig-music-1.mp3"; m0 = float(sys.argv[4]) if len(sys.argv) > 4 else 0
plan = json.load(open(f"{V}/timeline.json")); dur = plan["duration"]
ins = ["-ss", str(m0), "-i", music]
fc = [f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{dur},afade=t=in:d=0.2,afade=t=out:st={dur - 2.5}:d=2.5[m]"]; lab = ["[m]"]
for k, c in enumerate(plan["sfx"]):
    ins += ["-i", f"{V}/audio/sfx_{c['sound']}.wav"]; ms = int(c["t"] * 1000)
    fc.append(f"[{k + 1}:a]volume={c['gain'] + 4}dB,adelay={ms}|{ms}[s{k}]"); lab.append(f"[s{k}]")
fc.append("".join(lab) + f"amix=inputs={len(lab)}:normalize=0:duration=first,atrim=0:{dur}[mix]")
g = ";".join(fc)
m = subprocess.run(["ffmpeg", "-hide_banner", *ins, "-filter_complex", g + ";[mix]loudnorm=I=-14:TP=-2:LRA=11:print_format=json[o]", "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", m.stderr)[-1])
ln = f"loudnorm=I=-14:TP=-2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
shift = lambda s: re.sub(r"\[(\d+):a\]", lambda mm: f"[{int(mm.group(1)) + 1}:a]", s)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pic, *ins, "-filter_complex", shift(g) + f";[mix]{ln},aresample=48000[o]", "-map", "0:v", "-map", "[o]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-t", str(dur), out], check=True)
print("mixed ->", out)
