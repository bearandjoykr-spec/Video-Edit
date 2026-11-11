"""Mix the Day 1 ad: Mark and Joy's mic voices + licensed music + SFX, mux with the rendered picture.
Usage (repo root): .venv/bin/python projects/2026-11-day1-ad/mix.py PICTURE OUT_MP4 [MUSIC_FILE] [MUSIC_DB]
Music: the Little Steps ukulele track the owner chose by ear (projects/2026-11-day0-welcome/music/SOURCE.md), clearly audible
under the voices (Joy, Day 28: music must not be buried), ducked lightly, up full over the end card. Final -14 LUFS, peaks <= -1 dBTP.
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
V = f"{HERE}/versions/main"
picture, out = sys.argv[1:3]
music = sys.argv[3] if len(sys.argv) > 3 else "projects/2026-11-day0-welcome/music/ukulele.mp3"
music_db = float(sys.argv[4]) if len(sys.argv) > 4 else -14
plan = json.load(open(f"{V}/timeline.json")); dur = plan["duration"]; se = plan["speechEnd"]
inputs = ["-i", f"{V}/cut.mov", "-i", music]
fc = [
    # two different mics: tidy the low end and even the levels out with a compressor before the mix
    f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=85,equalizer=f=3000:t=q:w=1:g=2,"
    f"acompressor=threshold=-24dB:ratio=3.5:attack=6:release=120:makeup=4,apad=whole_dur={dur},asplit=2[voice][key]",
    f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={music_db}dB,atrim=0:{dur},afade=t=in:d=0.3,afade=t=out:st={dur - 1.2}:d=1.2[mus0]",
    "[mus0][key]sidechaincompress=threshold=0.05:ratio=2:attack=30:release=450[mus1]",
    f"[mus1]volume='if(gte(t,{se}),1.8,1)':eval=frame[mus]",
]
labels = ["[voice]", "[mus]"]
for k, cue in enumerate(plan["sfx"]):
    inputs += ["-i", f"{V}/audio/sfx_{cue['sound']}.wav"]
    ms = int(round(cue["t"] * 1000))
    fc.append(f"[{k + 2}:a]volume={cue['gain']}dB,adelay={ms}|{ms}[s{k}]"); labels.append(f"[s{k}]")
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
