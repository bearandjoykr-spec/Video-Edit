"""Build versions/main/voice.wav from the chosen takes of raw-footage/day34/vo.m4a, placed at the times in timeline.json ("vo").
Run (repo root) after build.py: .venv/bin/python projects/2026-11-day34-bookguide/voice.py"""
import json, os, subprocess
P = os.path.dirname(os.path.abspath(__file__)); plan = json.load(open(f"{P}/versions/main/timeline.json"))
ins, fc, lab = [], [], []
for k, v in enumerate(plan["vo"]):
    d = round(v["src_e"] - v["src_s"], 3); ins += ["-ss", str(v["src_s"]), "-t", str(d), "-i", "raw-footage/day34/vo.m4a"]; ms = int(v["at"] * 1000)
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=mono,afade=t=in:d=0.03,afade=t=out:st={d - 0.05:.3f}:d=0.05,adelay={ms}|{ms}[v{k}]"); lab.append(f"[v{k}]")
fc.append("".join(lab) + f"amix=inputs={len(lab)}:normalize=0:duration=longest,highpass=f=80,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=130:makeup=2,"
          f"apad=whole_dur={plan['duration']},atrim=0:{plan['duration']}[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[a]", "-ar", "48000", f"{P}/versions/main/voice.wav"], check=True)
print("voice.wav")
