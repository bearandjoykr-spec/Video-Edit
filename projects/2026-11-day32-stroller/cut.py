"""Cut DAY 32: Joy's voice throughout; Joy full frame, or B-roll with Joy in a round picture-in-picture (top right).
Run (repo root): .venv/bin/python projects/2026-11-day32-stroller/cut.py   -> versions/main/cut.mov
Segment times come from versions/main/timeline_v2.json (build.py snaps them first).
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from edl import RAW, BROLL, END  # noqa: E402
V = f"{HERE}/versions/main"
plan = json.load(open(f"{V}/timeline_v2.json"))
segs = plan["segments"]
MAIN = f"{RAW}/main.mp4"
PIP, PX, PY = 330, 48, 300  # round Joy: diameter, position (top left, clear of the DAY badge)
ins, fc, n = [], [], 0
def add_in(*a):
    global n
    ins.extend(a); n += 1; return n - 1
labels = []
for k, g in enumerate(segs):
    d = round(g["src_e"] - g["src_s"], 3)
    j = add_in("-ss", str(g["src_s"]), "-t", str(d), "-i", MAIN)
    fc.append(f"[{j}:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.02,afade=t=out:st={d - 0.03:.3f}:d=0.03,asetpts=PTS-STARTPTS[a{k}]")
    if g["kind"] == "joy":
        fc.append(f"[{j}:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v{k}]")
    else:
        b = add_in("-ss", str(g["b_s"]), "-t", str(d), "-i", BROLL[g["broll"]])
        fc.append(f"[{b}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS[bg{k}]")
        if g["kind"] == "cold":
            fc.append(f"[bg{k}]null[v{k}]")
        else:
            # Joy's face, round, with a cream ring
            fc.append(f"[{j}:v]crop=640:640:220:230,scale={PIP}:{PIP},fps=30,format=rgba,"
                      f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(lte(hypot(X-{PIP / 2},Y-{PIP / 2}),{PIP / 2 - 2}),255,0)',setpts=PTS-STARTPTS[pip{k}]")
            R = PIP + 16
            fc.append(f"color=c=0xF5F0E6:s={R}x{R}:d={d},format=rgba,geq=r='245':g='240':b='230':a='if(lte(hypot(X-{R / 2},Y-{R / 2}),{R / 2 - 1}),255,0)'[ring{k}]")
            fc.append(f"[bg{k}][ring{k}]overlay={PX - 8}:{PY - 8}[bgr{k}];[bgr{k}][pip{k}]overlay={PX}:{PY}:shortest=1,format=yuv420p[v{k}]")
    labels.append(f"[v{k}][a{k}]")
fc.append("".join(labels) + f"concat=n={len(segs)}:v=1:a=1[v0][a0]")
fc.append(f"[v0]tpad=stop_mode=clone:stop_duration={END}[v];[a0]apad=whole_dur={plan['duration']}[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-t", str(plan["duration"]),
                "-c:v", "h264_videotoolbox", "-b:v", "20M", "-c:a", "pcm_s16le", f"{V}/cut.mov"], check=True)
print("cut.mov", plan["duration"], "s")
