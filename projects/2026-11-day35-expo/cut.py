"""Cut the background track for DAY 35 from plan.json, 1080x1920 30 fps, no audio.
Joy (v2): no flashes — every cut is a short dissolve (X s). Each shot runs d+X so the dissolve eats into its tail and
every cut still starts at the planned time (no drift). Run (repo root): .venv/bin/python projects/2026-11-day35-expo/cut.py"""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
X = 0.3
plan = json.load(open(f"{HERE}/versions/main/plan.json"))
out = "remotion/public/day35/bg.mp4"
ins, fc, sh = [], [], plan["shots"]
for k, s in enumerate(sh):
    ins += ["-ss", str(s["ss"]), "-t", str(s["d"] + X + 0.3), "-i", s["src"]]
    fc.append(f"[{k}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,format=yuv420p,"
              f"tpad=stop_mode=clone:stop_duration=3,trim=0:{s['d'] + X:.3f},setpts=PTS-STARTPTS[v{k}]")
prev = "v0"
for k in range(1, len(sh)):
    fc.append(f"[{prev}][v{k}]xfade=transition=fade:duration={X}:offset={sh[k]['t']:.3f}[x{k}]"); prev = f"x{k}"
fc.append(f"[{prev}]trim=0:{plan['duration']},setpts=PTS-STARTPTS[v]")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]",
                "-c:v", "h264_videotoolbox", "-b:v", "20M", "-pix_fmt", "yuv420p", out], check=True)
print("wrote", out)
