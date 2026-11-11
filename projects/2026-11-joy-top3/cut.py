"""Cut the picture (1080x1920, 30 fps, original colours) with the clips' own sound low as ambience.
Run from the repo root: .venv/bin/python projects/2026-11-joy-top3/cut.py  -> versions/main/cut.mov
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from edl import PIC, RAW, SPEECH_END, END  # noqa: E402
TOTAL = round(SPEECH_END + END, 3)
OUT = f"{HERE}/versions/main"; os.makedirs(OUT, exist_ok=True)
ins, fc = [], []
for k, (clip, s, e) in enumerate(PIC):
    ins += ["-ss", str(s), "-t", str(round(e - s, 3)), "-i", f"{RAW}/{clip}"]
    fc.append(f"[{k}:v]scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v{k}]")
    fc.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.05,afade=t=out:st={e - s - 0.08:.3f}:d=0.08,asetpts=PTS-STARTPTS[a{k}]")
fc.append("".join(f"[v{k}][a{k}]" for k in range(len(PIC))) + f"concat=n={len(PIC)}:v=1:a=1[v0][a0]")
# hold the last frame under the end card
fc.append(f"[v0]tpad=stop_mode=clone:stop_duration={END}[v];[a0]apad=whole_dur={TOTAL}[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-t", str(TOTAL),
                "-c:v", "h264_videotoolbox", "-b:v", "20M", "-c:a", "pcm_s16le", f"{OUT}/cut.mov"], check=True)
print("cut.mov", TOTAL, "s")
