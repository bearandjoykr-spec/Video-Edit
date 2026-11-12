"""Mix voice + licensed music + SFX and mux with the rendered picture.

Usage (repo root): python3 projects/2026-11-accent-question/mix.py PICTURE OUT_MP4 [MUSIC_FILE|none] [MUSIC_DB] [MUSIC_START_S]
Music is a licensed track chosen by the owner by ear (never generated), about -15 dB with light ducking (Joy, Day 28), silent for the
cliffhanger beat, back in on the follow card. Without a music file the draft is voice + effects only. Final -14 LUFS, peaks <= -1 dBTP.
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
picture, out = sys.argv[1:3]
music = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "none" else None
music_db = float(sys.argv[4]) if len(sys.argv) > 4 else -15
m0 = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
V = f"{HERE}/versions/main"
plan = json.load(open(f"{V}/timeline_v2.json")); dur = plan["duration"]
inputs = ["-i", f"{V}/audio/voice.wav"]
fc = [f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={dur},asplit=2[voice][key]"]
labels, n = ["[voice]"], 1
if music:
    inputs += ["-ss", str(m0), "-i", music]; n = 2
    mute = "".join(f",volume=enable='between(t,{a},{b})':volume=0" for a, b in plan["music"]["dropouts"])
    fc += [f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={music_db}dB,atrim=0:{dur},afade=t=in:d=0.3{mute},afade=t=out:st={dur - 2.5}:d=2.5[mus0]",
           "[mus0][key]sidechaincompress=threshold=0.05:ratio=2:attack=30:release=500[mus]"]
    labels.append("[mus]")
else:
    fc.append("[key]anullsink")
for k, cue in enumerate(plan["sfx"]):
    inputs += ["-i", f"{V}/audio/sfx_{cue['sound']}.wav"]
    ms = int(round(cue["t"] * 1000))
    fc.append(f"[{k + n}:a]volume={cue['gain']}dB,adelay={ms}|{ms}[s{k}]"); labels.append(f"[s{k}]")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,atrim=0:{dur}[mix]")
graph = ";".join(fc)
m = subprocess.run(["ffmpeg", "-hide_banner", *inputs, "-filter_complex", graph + ";[mix]loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[o]",
                    "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", m.stderr)[-1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
shift = lambda g: re.sub(r"\[(\d+):a\]", lambda mm: f"[{int(mm.group(1)) + 1}:a]", g)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", picture, *inputs, "-filter_complex", shift(graph) + f";[mix]{ln},aresample=48000[o]",
                "-map", "0:v", "-map", "[o]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out], check=True)
print("mixed ->", out, "| music:", music or "none", "| measured input", j["input_i"], "LUFS")
