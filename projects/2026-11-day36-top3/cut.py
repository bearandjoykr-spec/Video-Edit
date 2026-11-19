"""DAY 36 background track from plan.json: straight, frame-accurate cuts on the beat (Joy: fast transitions, no flashes),
1080x1920 30 fps, a quiet premium grade (a little contrast, less saturation, warm). rot 180 = the upside-down ball-game clip.
Run (repo root): .venv/bin/python projects/2026-11-day36-top3/cut.py"""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
plan = json.load(open(f"{HERE}/versions/main/plan.json"))
out = "remotion/public/day36/bg.mp4"; os.makedirs(os.path.dirname(out), exist_ok=True)
FPS = plan["fps"]
ins, fc, sh = [], [], plan["shots"]
for k, s in enumerate(sh):
    f0, f1 = round(s["t"] * FPS), round((s["t"] + s["d"]) * FPS)
    ins += ["-ss", f"{s['ss']:.3f}", "-t", f"{s['d'] + 0.5:.3f}", "-i", s["src"]]
    rot = "hflip,vflip," if s.get("rot") == 180 else ""
    fc.append(f"[{k}:v]{rot}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={FPS},setsar=1,format=yuv420p,"
              f"tpad=stop_mode=clone:stop_duration=2,trim=end_frame={f1 - f0},setpts=PTS-STARTPTS[v{k}]")
fc.append("".join(f"[v{k}]" for k in range(len(sh))) + f"concat=n={len(sh)}:v=1:a=0,"
          "eq=contrast=1.06:saturation=0.88:gamma=0.98,colorbalance=rh=0.03:bh=-0.03:rm=0.02:bm=-0.02[v]")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]",
                "-c:v", "h264_videotoolbox", "-b:v", "24M", "-pix_fmt", "yuv420p", out], check=True)
print("wrote", out)
