"""Cut source footage (and optionally the subject matte) into each version's edited timeline."""
import json, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]; what = sys.argv[2]  # what: video | matte
for name in ("main", "tight"):
    p = json.load(open(f"{HERE}/versions/{name}/timeline_v2.json"))
    segs = p["segments"]; n = len(segs)
    if what == "video":
        f = "".join(f"[0:v]trim={g['src_s']}:{g['src_e']},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={g['src_s']}:{g['src_e']},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={g['src_e']-g['src_s']-0.03}:d=0.03[a{i}];" for i, g in enumerate(segs))
        f += "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", f, "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "pcm_s16le", "-ar", "48000",
               f"{HERE}/versions/{name}/cut.mov"]
    else:
        f = "".join(f"[0:v]trim={g['src_s']}:{g['src_e']},setpts=PTS-STARTPTS[v{i}];" for i, g in enumerate(segs))
        f += "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,format=yuva420p[v]"
        cmd = ["ffmpeg", "-v", "error", "-y", "-c:v", "libvpx-vp9", "-i", SRC, "-filter_complex", f, "-map", "[v]",
               "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "20", "-row-mt", "1", "-deadline", "good", "-cpu-used", "4", "-r", "30",
               f"{HERE}/versions/{name}/matte.webm"]
    subprocess.run(cmd, check=True); print("cut", what, name)
