"""Mark spicy interview: cut the source into the edited timeline (hardware H.264 on the Mac), or the subject matte.

Usage: .venv/bin/python cut.py SOURCE video      -> versions/main/cut.mov
       .venv/bin/python cut.py MATTE.webm matte  -> versions/main/matte.webm (one segment at a time, low memory)
"""
import json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
SRC, what = sys.argv[1], sys.argv[2]
name = "main"
segs = json.load(open(f"{HERE}/versions/{name}/timeline_v2.json"))["segments"]
n = len(segs)
if what == "video":
    f = "".join(f"[0:v]trim={g['src_s']}:{g['src_e']},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={g['src_s']}:{g['src_e']},asetpts=PTS-STARTPTS,"
                f"afade=t=in:d=0.02,afade=t=out:st={g['src_e'] - g['src_s'] - 0.03}:d=0.03[a{i}];" for i, g in enumerate(segs))
    f += "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", f, "-map", "[v]", "-map", "[a]",
                    "-c:v", "h264_videotoolbox", "-b:v", "20M", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "pcm_s16le", "-ar", "48000",
                    f"{HERE}/versions/{name}/cut.mov"], check=True)
else:
    tmp = tempfile.mkdtemp(prefix="matte-", dir=f"{HERE}/versions/{name}")
    parts = []
    for i, g in enumerate(segs):
        out = f"{tmp}/p{i:02d}.webm"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-c:v", "libvpx-vp9", "-ss", str(g["src_s"]), "-i", SRC, "-t", str(round(g["src_e"] - g["src_s"], 3)),
                        "-an", "-vf", "format=yuva420p", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "22", "-row-mt", "1",
                        "-deadline", "good", "-cpu-used", "5", "-r", "30", out], check=True)
        parts.append(out)
    lst = f"{tmp}/list.txt"
    open(lst, "w").write("".join(f"file '{x}'\n" for x in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", f"{HERE}/versions/{name}/matte.webm"], check=True)
    for x in parts + [lst]:
        os.remove(x)
    os.rmdir(tmp)
print("cut", what, name)
