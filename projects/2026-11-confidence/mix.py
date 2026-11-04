"""Mix voice + music + SFX for a version and mux with the rendered picture.

Usage: python3 mix.py VERSION RENDERED_VIDEO OUT_MP4 [PLAN_FILE] [MUSIC_DB] [DUCK_RATIO]
Defaults (v1 storybook): timeline.json, music -21 dB, duck ratio 5.
v2 high-energy reels: timeline_v2.json, music -8 dB, duck ratio 2.5.
Always: voice first, final mix -14 LUFS, peaks <= -1 dBTP.
"""
import json, subprocess, sys, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
name, picture, out = sys.argv[1:4]
plan_file = sys.argv[4] if len(sys.argv) > 4 else "timeline.json"
music_db = float(sys.argv[5]) if len(sys.argv) > 5 else -21
duck = float(sys.argv[6]) if len(sys.argv) > 6 else 5
V = f"{HERE}/versions/{name}"
plan = json.load(open(f"{V}/{plan_file}"))
dur = plan["duration"]

inputs = ["-i", f"{V}/cut.mov", "-i", f"{V}/audio/music.wav"]
fc = [
    # voice: tidy low end, gentle compression, pad to full length (end card has no speech)
    f"[0:a]highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3,apad=whole_dur={dur},asplit=2[voice][key]",
    f"[1:a]volume={music_db}dB,atrim=0:{dur}[mus0]",
    f"[mus0][key]sidechaincompress=threshold=0.02:ratio={duck}:attack=25:release=450[mus]",
]
labels = ["[voice]", "[mus]"]
for k, cue in enumerate(plan["sfx"]):
    inputs += ["-i", f"{V}/audio/sfx_{cue['sound']}.wav"]
    ms = int(round(cue["t"] * 1000))
    fc.append(f"[{k + 2}:a]volume={cue['gain']}dB,adelay={ms}|{ms}[s{k}]")
    labels.append(f"[s{k}]")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,atrim=0:{dur}[mix]")
graph = ";".join(fc)

# pass 1: measure loudness
m = subprocess.run(["ffmpeg", "-hide_banner", *inputs, "-filter_complex", graph + ";[mix]loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[o]",
                    "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", m.stderr)[-1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
# pass 2: write. The picture is input 0 here, so shift every audio input index by one.
os.makedirs(os.path.dirname(out), exist_ok=True)
shift = lambda g: re.sub(r"\[(\d+):a\]", lambda mm: f"[{int(mm.group(1)) + 1}:a]", g)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", picture, *inputs, "-filter_complex", shift(graph) + f";[mix]{ln},aresample=48000[o]",
                "-map", "0:v", "-map", "[o]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out], check=True)
print("mixed", name, "->", out, "| measured input", j["input_i"], "LUFS")
