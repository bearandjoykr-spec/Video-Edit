"""Background picture for DAY 34 (no sound: Joy records the voice-over later). Each section plays its clip full frame.
Run (repo root): .venv/bin/python projects/2026-11-day34-bookguide/cut.py  -> versions/main/cut.mov
"""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); V = f"{HERE}/versions/main"
secs = json.load(open(f"{V}/sections_src.json"))
ins, fc = [], []
SLOW = {}
for k, x in enumerate(secs):
    d = round(x["e"] - x["s"] + 0.3, 3)
    SLOW[k] = 1.0
    if x["clip"] and not x["clip"].endswith("n5.mov"):
        # sections now follow the voice and can outlast the clip: start earlier, then slow down gently (never freeze)
        L = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", x["clip"]], capture_output=True, text=True).stdout)
        if x["cs"] + d > L - 0.05:
            x["cs"] = max(0.0, round(L - d - 0.05, 2))
        if d > L - 0.05:
            SLOW[k] = round(d / (L - 0.05), 3)
    if x["clip"]:
        ins += ["-ss", str(x["cs"]), "-t", str(d), "-i", x["clip"]]
        if x["clip"].endswith("n5.mov"):  # Joy's workbook clip (2.5 s, portrait): slowed to fill, the question page big on a blurred copy
            sl = max(1.0, d / 2.4)
            fc.append(f"[{k}:v]setpts={sl:.3f}*(PTS-STARTPTS),crop=1750:1750:150:1650,split[wa{k}][wb{k}];[wa{k}]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.12[wbg{k}];"
                      f"[wb{k}]scale=1080:1080[wfg{k}];[wbg{k}][wfg{k}]overlay=0:760,setsar=1,fps=30,format=yuv420p,tpad=stop_mode=clone:stop_duration=60,trim=0:{d},setpts=PTS-STARTPTS[v{k}]")
            continue
        fc.append(f"[{k}:v]setpts={SLOW[k]:.3f}*(PTS-STARTPTS),scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS,"
                  f"tpad=stop_mode=clone:stop_duration=60,trim=0:{d},setpts=PTS-STARTPTS[v{k}]")
    else:
        ins += ["-f", "lavfi", "-t", str(d), "-i", "color=c=0x1E2D4D:s=1080x1920:r=30"]
        fc.append(f"[{k}:v]format=yuv420p,setsar=1[v{k}]")
# Joy (17 Nov): the flow felt choppy. Soft 0.3 s dissolves between every shot; each input runs 0.3 s longer, so the timeline keeps its times.
X = 0.3
prev = "v0"; t = secs[0]["e"] - secs[0]["s"]
for k in range(1, len(secs)):
    fc.append(f"[{prev}][v{k}]xfade=transition=fade:duration={X}:offset={t:.3f}[x{k}]")
    prev = f"x{k}"; t += secs[k]["e"] - secs[k]["s"]
fc.append(f"[{prev}]null[v]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-c:v", "h264_videotoolbox", "-b:v", "20M", f"{V}/cut.mov"], check=True)
print("cut.mov")
