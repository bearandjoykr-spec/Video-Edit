"""Mix Joy's TOP 3: Joy's recorded voice-over (when there is one) + the clips' own sound as low ambience + licensed music + SFX.
Usage (repo root): .venv/bin/python projects/2026-11-joy-top3/mix.py PICTURE OUT_MP4 [VO_WAV|-] [MUSIC] [MUSIC_DB]
VO_WAV is already laid out on program time (align.py). "-" = draft without voice. Music must stay clearly audible (Joy, Day 28).
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
V = f"{HERE}/versions/main"
picture, out = sys.argv[1:3]
vo = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "-" else None
music = sys.argv[4] if len(sys.argv) > 4 else "projects/2026-11-day25-kyobo/music/magic-moments.mp3"
music_db = float(sys.argv[5]) if len(sys.argv) > 5 else -15
plan = json.load(open(f"{V}/timeline.json")); dur = plan["duration"]
inputs = ["-i", f"{V}/cut.mov", "-i", music] + (["-i", vo] if vo else [])
fc = [f"[0:a]apad=whole_dur={dur}[amb]",  # cut.py sets the levels (live lines full, shop sound low)
      f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={music_db}dB,atrim=0:{dur},afade=t=in:d=0.3,afade=t=out:st={dur - 2.5}:d=2.5[mus0]"]
if vo:
    fc.append(f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=80,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=130:makeup=2,"
              f"apad=whole_dur={dur},asplit=2[voice][key]")
    fc.append("[mus0][key]sidechaincompress=threshold=0.05:ratio=2:attack=30:release=450[mus]")
    labels, n0 = ["[voice]", "[amb]", "[mus]"], 3
else:
    fc.append("[mus0]anull[mus]"); labels, n0 = ["[amb]", "[mus]"], 2
for k, cue in enumerate(plan["sfx"]):
    inputs += ["-i", f"{V}/audio/sfx_{cue['sound']}.wav"]
    ms = int(round(cue["t"] * 1000))
    fc.append(f"[{k + n0}:a]volume={cue['gain']}dB,adelay={ms}|{ms}[s{k}]"); labels.append(f"[s{k}]")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,atrim=0:{dur}[mix]")
graph = ";".join(fc)
m = subprocess.run(["ffmpeg", "-hide_banner", *inputs, "-filter_complex", graph + ";[mix]loudnorm=I=-14:TP=-3:LRA=11:print_format=json[o]",
                    "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", m.stderr)[-1])
ln = (f"loudnorm=I=-14:TP=-3:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
shift = lambda g: re.sub(r"\[(\d+):a\]", lambda mm: f"[{int(mm.group(1)) + 1}:a]", g)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", picture, *inputs, "-filter_complex", shift(graph) + f";[mix]{ln},aresample=48000[o]",
                "-map", "0:v", "-map", "[o]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out], check=True)
print("mixed ->", out)
