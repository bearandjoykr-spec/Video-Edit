"""Mix the class video: source audio (Mark & Joy, plus the music already in Mark's section) + lo-fi bed + SFX.

Usage: python3 mix_class.py VERSION PICTURE OUT_MP4 [MUSIC_DB=-12] [FROM TO]
FROM/TO (seconds) mix only that stretch, for a sample whose PICTURE was rendered with --frames for the same range.
Voice first; final -14 LUFS, peaks <= -1 dBTP. Source audio stops at the end of speech (the source's black gap is silent).
"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
name, picture, out = sys.argv[1:4]
music_db = float(sys.argv[4]) if len(sys.argv) > 4 else -12
V = f"{HERE}/versions/{name}"
plan = json.load(open(f"{V}/timeline_class.json"))
dur = plan["duration"]; speech_end = plan["mediaDuration"]
a, b = (float(sys.argv[5]), float(sys.argv[6])) if len(sys.argv) > 6 else (0, dur)
src = os.path.join(HERE, "../../raw-footage/day5/day5.mov")
inputs = ["-i", src, "-i", f"{V}/audio/music.wav"]
fc = [f"[0:a]aresample=48000,highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=150:makeup=2,atrim=0:{speech_end},apad=whole_dur={dur},asplit=2[voice][key]",
      f"[1:a]volume={music_db}dB,atrim=0:{dur}[mus0]",
      "[mus0][key]sidechaincompress=threshold=0.03:ratio=3:attack=30:release=500[mus]"]
labels = ["[voice]", "[mus]"]
for k, cue in enumerate(plan["sfx"]):
    inputs += ["-i", f"{V}/audio/sfx_{cue['sound']}.wav"]
    ms = int(round(cue["t"] * 1000))
    fc.append(f"[{k + 2}:a]aresample=48000,volume={cue['gain']}dB,adelay={ms}|{ms}[s{k}]"); labels.append(f"[s{k}]")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,atrim={a}:{b},asetpts=PTS-STARTPTS[mix]")
graph = ";".join(fc)
m = subprocess.run(["ffmpeg", "-hide_banner", *inputs, "-filter_complex", graph + ";[mix]loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[o]",
                    "-map", "[o]", "-f", "null", "-"], capture_output=True, text=True)
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", m.stderr)[-1])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
shift = lambda g: re.sub(r"\[(\d+):a\]", lambda mm: f"[{int(mm.group(1)) + 1}:a]", g)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", picture, *inputs, "-filter_complex", shift(graph) + f";[mix]{ln},aresample=48000[o]",
                "-map", "0:v", "-map", "[o]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", out], check=True)
print("mixed ->", out, "| input", j["input_i"], "LUFS")
