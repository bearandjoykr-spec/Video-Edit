"""DAY 35 mix: Joy's intro voice (main.mov) + her voice-over (versions/main/vo.wav, once recorded) + upbeat music + soft SFX, -14 LUFS.
Usage (repo root): .venv/bin/python projects/2026-11-day35-expo/mix.py PICTURE OUT [MUSIC_DB] [MUSIC] [MUSIC_START]"""
import json, os, re, subprocess, sys
P = os.path.dirname(os.path.abspath(__file__)); V = f"{P}/versions/main"
pic, out = sys.argv[1:3]; mdb = float(sys.argv[3]) if len(sys.argv) > 3 else -8
# Joy (v3): Magic Moments was not lively enough → "Pop Energy" (studiokolomna), from its full beat at 9.6 s
music = sys.argv[4] if len(sys.argv) > 4 else f"{P}/music/pop-energy-632664.mp3"; m0 = float(sys.argv[5]) if len(sys.argv) > 5 else 9.6
plan = json.load(open(f"{V}/plan.json")); dur = plan["duration"]; intro = plan["intro"]
ins = ["-i", "remotion/public/day35/intro.wav", "-ss", str(m0), "-i", music]
fc = []
vo = f"{V}/vo.wav"
if os.path.exists(vo):  # Joy's recording starts right after the intro
    ins += ["-i", vo]; ms = int((intro + .15) * 1000)
    fc.append(f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms}[vo]")
    fc.append(f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo[in];[in][vo]amix=inputs=2:normalize=0,apad=whole_dur={dur},asplit=2[voice][key]")
else:
    fc.append(f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={dur},asplit=2[voice][key]")
fc += [f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={mdb}dB,atrim=0:{dur},afade=t=in:d=0.3,afade=t=out:st={dur - 2.5}:d=2.5[m0]",
       "[m0][key]sidechaincompress=threshold=0.08:ratio=1.6:attack=30:release=450[m]"]
lab = ["[voice]", "[m]"]; n0 = ins.count("-i")
for k, c in enumerate(plan["sfx"]):
    ins += ["-i", f"projects/2026-11-day34-bookguide/versions/main/audio/sfx_{c['sound']}.wav"]; ms = int(c["t"] * 1000)
    fc.append(f"[{n0 + k}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={c['gain']}dB,adelay={ms}|{ms}[s{k}]"); lab.append(f"[s{k}]")
fc.append("".join(lab) + f"amix=inputs={len(lab)}:normalize=0:duration=first,atrim=0:{dur}[mix]")
g = ";".join(fc)
m = subprocess.run(["ffmpeg", "-hide_banner", *ins, "-filter_complex", g + ";[mix]loudnorm=I=-14:TP=-2:LRA=11:print_format=json[o]", "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", m.stderr)[-1])
ln = f"loudnorm=I=-14:TP=-2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
shift = lambda s: re.sub(r"\[(\d+):a\]", lambda mm: f"[{int(mm.group(1)) + 1}:a]", s)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pic, *ins, "-filter_complex", shift(g) + f";[mix]{ln},aresample=48000[o]", "-map", "0:v", "-map", "[o]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-t", str(dur), out], check=True)
print("mixed ->", out)
