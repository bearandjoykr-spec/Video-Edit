"""Cut the background track for DAY 35 from plan.json: hard cuts (Remotion adds the punch-in and flash), 1080x1920 30 fps, no audio.
Run (repo root): .venv/bin/python projects/2026-11-day35-expo/cut.py"""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
plan = json.load(open(f"{HERE}/versions/main/plan.json"))
out = "remotion/public/day35/bg.mp4"
ins, fc = [], []
for k, s in enumerate(plan["shots"]):
    ins += ["-ss", str(s["ss"]), "-t", str(s["d"] + 0.2), "-i", s["src"]]
    fc.append(f"[{k}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,"
              f"tpad=stop_mode=clone:stop_duration=2,trim=0:{s['d']},setpts=PTS-STARTPTS[v{k}]")
fc.append("".join(f"[v{k}]" for k in range(len(plan["shots"]))) + f"concat=n={len(plan['shots'])}:v=1:a=0[v]")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]",
                "-c:v", "h264_videotoolbox", "-b:v", "20M", "-pix_fmt", "yuv420p", out], check=True)
print("wrote", out)
