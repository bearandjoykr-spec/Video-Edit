"""Compose the DAY 33 picture: montage / full / board (top cream-board area left for Remotion, Mark below) / boardb / replay (slowed).
Run (repo root): .venv/bin/python projects/2026-11-day33-outdoor/cut.py   -> versions/main/cut.mov (audio = Mark, replays slowed with pitch kept)
"""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
V = f"{HERE}/versions/main"; RAW = "raw-footage/day33"
plan = json.load(open(f"{V}/timeline.json"))
SRC = {"b1_sdr": f"{RAW}/b1_sdr.mov", "b2": f"{RAW}/b2.mp4", "b3_sdr": f"{RAW}/b3_sdr.mov"}
BOARD_H = 860
ins, fc, n = [], [], 0
def add_in(*a):
    global n
    ins.extend(a); n += 1; return n - 1
labels = []
for k, g in enumerate(plan["segments"]):
    d = round(g["src_e"] - g["src_s"], 3); od = round(d / g["speed"], 3)
    j = add_in("-ss", str(g["src_s"]), "-t", str(d), "-i", f"{RAW}/main.mp4")
    sp = g["speed"]
    fc.append(f"[{j}:a]aresample=48000,aformat=channel_layouts=stereo,{'atempo=%s,' % sp if sp != 1 else ''}"
              f"afade=t=in:d=0.02,afade=t=out:st={od - 0.03:.3f}:d=0.03,asetpts=PTS-STARTPTS[a{k}]")
    mark = f"[{j}:v]setpts=(PTS-STARTPTS)/{sp},fps=30,"
    lay = g["layout"]
    if lay in ("montage", "boardb"):
        b = add_in("-ss", str(g["b_s"]), "-t", str(od), "-i", SRC.get(g["broll"], f"{RAW}/stock/{g['broll']}.mp4"))
        h = 1920 if lay == "montage" else 1920 - BOARD_H
        fc.append(f"[{b}:v]scale=1080:{h}:force_original_aspect_ratio=increase,crop=1080:{h},setsar=1,fps=30,setpts=PTS-STARTPTS,trim=0:{od}[br{k}]")
    if lay == "montage":
        fc.append(f"[br{k}]format=yuv420p[v{k}]")
    elif lay == "full":
        fc.append(f"{mark}scale=1080:1920,setsar=1,format=yuv420p,trim=0:{od}[v{k}]")
    else:
        fc.append(f"color=c=0x23402F:s=1080x{BOARD_H}:r=30:d={od}[top{k}]")
        if lay == "boardb":
            bottom = f"[br{k}]"
        else:
            fc.append(f"{mark}crop=1080:{1920 - BOARD_H}:0:250,setsar=1,trim=0:{od}[bot{k}]"); bottom = f"[bot{k}]"
        fc.append(f"[top{k}]{bottom}vstack,format=yuv420p,setsar=1[v{k}]")
    labels.append(f"[v{k}][a{k}]")
fc.append("".join(labels) + f"concat=n={len(plan['segments'])}:v=1:a=1[v0][a0]")
tail = round(plan["duration"] - plan["speechEnd"], 3)
fc.append(f"[v0]tpad=stop_mode=clone:stop_duration={tail}[v];[a0]apad=whole_dur={plan['duration']}[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-t", str(plan["duration"]),
                "-c:v", "h264_videotoolbox", "-b:v", "20M", "-c:a", "pcm_s16le", f"{V}/cut.mov"], check=True)
print("cut.mov", plan["duration"], "s")
