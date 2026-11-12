"""Cut the upright master (work/src2.mov) into the edited timeline, or cut the subject matte to match.

Usage (repo root): python3 projects/2026-11-accent-question/cut.py video   -> remotion/public/accentq/main/cut.mov
                   python3 projects/2026-11-accent-question/cut.py matte   -> remotion/public/accentq/main/matte.webm (one segment at a time, low memory)
On the Mac, swap libx264 for `-c:v h264_videotoolbox -b:v 20M` (CLAUDE.md).
"""
import json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(f"{HERE}/../..")
what = sys.argv[1]
segs = json.load(open(f"{HERE}/versions/main/timeline_v2.json"))["segments"]
OUT = f"{ROOT}/remotion/public/accentq/main"; os.makedirs(OUT, exist_ok=True)
n = len(segs)
if what == "video":
    f = "".join(f"[0:v]trim={g['src_s']}:{g['src_e']},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={g['src_s']}:{g['src_e']},asetpts=PTS-STARTPTS,"
                f"afade=t=in:d=0.02,afade=t=out:st={g['src_e'] - g['src_s'] - 0.03}:d=0.03[a{i}];" for i, g in enumerate(segs))
    f += "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{HERE}/work/src2.mov", "-filter_complex", f, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-g", "15", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "pcm_s16le", "-ar", "48000", f"{OUT}/cut.mov"], check=True)
else:
    tmp = tempfile.mkdtemp(prefix="matte-", dir=f"{HERE}/work")
    parts = []
    for i, g in enumerate(segs):
        out = f"{tmp}/p{i:02d}.webm"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-c:v", "libvpx-vp9", "-ss", str(g["src_s"]), "-i", f"{HERE}/work/matte2_full.webm", "-t", str(round(g["src_e"] - g["src_s"], 3)),
                        "-an", "-vf", "format=yuva420p", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "22", "-row-mt", "1",
                        "-deadline", "good", "-cpu-used", "5", "-r", "30", out], check=True)
        parts.append(out)
    lst = f"{tmp}/list.txt"
    open(lst, "w").write("".join(f"file '{x}'\n" for x in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", f"{OUT}/matte.webm"], check=True)
    for x in parts + [lst]:
        os.remove(x)
    os.rmdir(tmp)
print("cut", what)
