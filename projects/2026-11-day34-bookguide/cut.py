"""Background picture for DAY 34 (no sound: Joy records the voice-over later). Each section plays its clip full frame.
Run (repo root): .venv/bin/python projects/2026-11-day34-bookguide/cut.py  -> versions/main/cut.mov
"""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); V = f"{HERE}/versions/main"
secs = json.load(open(f"{V}/sections_src.json"))
ins, fc = [], []
for k, x in enumerate(secs):
    d = round(x["e"] - x["s"], 3)
    if x["clip"]:
        ins += ["-ss", str(x["cs"]), "-t", str(d), "-i", x["clip"]]
        fc.append(f"[{k}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS,"
                  f"tpad=stop_mode=clone:stop_duration=2,trim=0:{d}[v{k}]")
    else:
        ins += ["-f", "lavfi", "-t", str(d), "-i", "color=c=0x1E2D4D:s=1080x1920:r=30"]
        fc.append(f"[{k}:v]format=yuv420p,setsar=1[v{k}]")
fc.append("".join(f"[v{k}]" for k in range(len(secs))) + f"concat=n={len(secs)}:v=1:a=0[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-c:v", "h264_videotoolbox", "-b:v", "20M", f"{V}/cut.mov"], check=True)
print("cut.mov")
