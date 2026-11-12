"""Mix voice + licensed music + SFX for DAY 32 and mux with the rendered picture.

Usage (repo root): .venv/bin/python projects/2026-11-day28-questions/mix.py PICTURE OUT_MP4 MUSIC_FILE [MUSIC_DB] [MUSIC_START_S]
Voice = the cut's audio (Joy on camera + Mark's recorded English). Music is a licensed track chosen by the owner by ear
(never generated); it is ducked under the voice and fades out over the end card. Final -14 LUFS, peaks <= -1 dBTP.
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
picture, out, music = sys.argv[1:4]
music_db = float(sys.argv[4]) if len(sys.argv) > 4 else -12
m0 = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
V = f"{HERE}/versions/main"
plan = json.load(open(f"{V}/timeline_v2.json"))
dur = plan["duration"]

# voice.wav = the cut audio with Mark's lines cleaned (voice.py, Joy 10 Nov 2026); fall back to the raw cut audio
VOICE = "remotion/public/day32/main/cut.mov"
inputs = ["-i", VOICE, "-ss", str(m0), "-i", music]
fc = [
    # Joy's mic voice (and Mark's recorded lines): tidy low end, gentle compression
    f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3,apad=whole_dur={dur},asplit=2[voice][key]",
    f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={music_db}dB,atrim=0:{dur},afade=t=in:d=0.4,"
    f"afade=t=out:st={dur - 2.5}:d=2.5[mus0]",
    "[mus0][key]sidechaincompress=threshold=0.05:ratio=2:attack=30:release=500[mus]",
]
labels = ["[voice]", "[mus]"]
for k, cue in enumerate(plan["sfx"]):
    inputs += ["-i", f"{V}/audio/sfx_{cue['sound']}.wav"]
    ms = int(round(cue["t"] * 1000))
    fc.append(f"[{k + 2}:a]volume={cue['gain']}dB,adelay={ms}|{ms}[s{k}]")
    labels.append(f"[s{k}]")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,atrim=0:{dur}[mix]")
graph = ";".join(fc)
m = subprocess.run(["ffmpeg", "-hide_banner", *inputs, "-filter_complex", graph + ";[mix]loudnorm=I=-14:TP=-3.5:LRA=11:print_format=json[o]",
                    "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", m.stderr)[-1])
ln = (f"loudnorm=I=-14:TP=-3.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
shift = lambda g: re.sub(r"\[(\d+):a\]", lambda mm: f"[{int(mm.group(1)) + 1}:a]", g)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", picture, *inputs, "-filter_complex", shift(graph) + f";[mix]{ln},aresample=48000[o]",
                "-map", "0:v", "-map", "[o]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", out], check=True)
print("mixed ->", out, "| measured input", j["input_i"], "LUFS")
