"""Cut the transparent subject matte one segment at a time (low memory), then join the pieces."""
import json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
for name in sys.argv[2:] or ["main", "tight"]:
    p = json.load(open(f"{HERE}/versions/{name}/timeline_v2.json"))
    tmp = tempfile.mkdtemp(prefix=f"matte-{name}-", dir=f"{HERE}/versions/{name}")
    parts = []
    for i, g in enumerate(p["segments"]):
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
    print("matte cut", name)
