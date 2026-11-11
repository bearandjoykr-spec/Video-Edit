"""Cut the ad's shots from the source (hardware H.264 on the Mac) -> versions/main/cut.mov (full 1920x1080 frames; the card crops).
Run: .venv/bin/python projects/2026-11-day1-ad/cut.py raw-footage/day1-promo/promo.mov"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
shots = json.load(open(f"{HERE}/versions/main/timeline.json"))["shots"]
f = "".join(f"[0:v]trim={g['src_s']}:{g['src_e']},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={g['src_s']}:{g['src_e']},asetpts=PTS-STARTPTS,"
            f"afade=t=in:d=0.02,afade=t=out:st={g['src_e'] - g['src_s'] - 0.03}:d=0.03[a{i}];" for i, g in enumerate(shots))
f += "".join(f"[v{i}][a{i}]" for i in range(len(shots))) + f"concat=n={len(shots)}:v=1:a=1[v][a]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", sys.argv[1], "-filter_complex", f, "-map", "[v]", "-map", "[a]", "-c:v", "h264_videotoolbox",
                "-b:v", "24M", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "pcm_s16le", "-ar", "48000", f"{HERE}/versions/main/cut.mov"], check=True)
print("cut ->", f"{HERE}/versions/main/cut.mov")
