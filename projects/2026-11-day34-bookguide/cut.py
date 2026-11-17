"""Background picture for DAY 34 (no sound: Joy records the voice-over later). Each section plays its clip full frame.
Run (repo root): .venv/bin/python projects/2026-11-day34-bookguide/cut.py  -> versions/main/cut.mov
"""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); V = f"{HERE}/versions/main"
secs = json.load(open(f"{V}/sections_src.json"))
ins, fc = [], []
for k, x in enumerate(secs):
    d = round(x["e"] - x["s"] + 0.3, 3)
    if x["clip"]:
        ins += ["-ss", str(x["cs"]), "-t", str(d), "-i", x["clip"]]
        fc.append(f"[{k}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS,"
                  f"tpad=stop_mode=clone:stop_duration=2,trim=0:{d}[v{k}]")
    else:
        ins += ["-f", "lavfi", "-t", str(d), "-i", "color=c=0x1E2D4D:s=1080x1920:r=30"]
        fc.append(f"[{k}:v]format=yuv420p,setsar=1[v{k}]")
# Joy (17 Nov): the flow felt choppy. Soft 0.3 s dissolves between shots; a section continuing the same clip runs straight on (no dissolve).
X = 0.3
prev = "v0"; t = secs[0]["e"] - secs[0]["s"]
for k in range(1, len(secs)):
    same = secs[k]["clip"] and secs[k]["clip"] == secs[k - 1]["clip"] and abs(secs[k]["cs"] - (secs[k - 1]["cs"] + secs[k - 1]["e"] - secs[k - 1]["s"])) < 0.05
    hook = secs[k]["kind"] == "hook"
    fc.append(f"[{prev}][v{k}]xfade=transition={'fade' if not (same or hook) else 'fade'}:duration={0.04 if (same or hook) else X}:offset={t - (0.04 if (same or hook) else X) / 2:.3f}[x{k}]")
    prev = f"x{k}"; t += secs[k]["e"] - secs[k]["s"]
fc.append(f"[{prev}]null[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-c:v", "h264_videotoolbox", "-b:v", "20M", f"{V}/cut.mov"], check=True)
print("cut.mov")
