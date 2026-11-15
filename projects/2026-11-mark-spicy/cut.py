"""Mark 영유 interview (DAY 31): Mark full frame, or stock B-roll with Mark in a round inset (top left). Mark's voice throughout.
Run (repo root): .venv/bin/python projects/2026-11-mark-spicy/cut.py   -> versions/main/cut.mov
"""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
V = f"{HERE}/versions/main"
RAW = "raw-footage/new-1113"
plan = json.load(open(f"{V}/timeline_v2.json"))
segs = plan["segments"]
PIP, PX, PY = 330, 48, 470  # below the top pops
# B-roll sources with a pre-crop (Joy, 15 Nov 2026: no faces that read as non-Korean; hands-only stock, and our own footage of Joy)
BROLL = {
    "quizhands": (f"{RAW}/stock/quiz.mp4", "crop=1080:1920:300:1920,"),          # pencil on a test sheet, background child cropped out
    "joywindow": ("raw-footage/day1-promo/promo.mov", "hflip,crop=608:1080:716:0,"), # Joy's Day 1 peekaboo window game (source is mirrored)
    "booktop3": ("raw-footage/joy-top3/book2.mov", ""),                            # Joy's thumbs-up with a picture book
    "stroller": ("raw-footage/day32/stock/stroller1.mp4", ""),                    # autumn stroller walk (Pexels, no faces)
    "walk1": ("raw-footage/day32/walk1.mov", ""),                                  # Joy's autumn walk: red trees
    "walk2": ("raw-footage/day32/walk2.mov", ""),                                  # Joy's autumn walk: ginkgo street
}
ins, fc = [], []
def add_in(*a):
    ins.extend(a); return sum(1 for x in ins if x == "-i") - 1
labels = []
T = 0.25  # Mark (15 Nov): soft dissolves instead of hard jump cuts. Each picture runs T longer so the sound stays in sync.
for k, g in enumerate(segs):
    d = round(g["src_e"] - g["src_s"], 3)
    vd = d + (T if k < len(segs) - 1 else 0)
    j = add_in("-ss", str(g["src_s"]), "-t", str(vd), "-i", f"{RAW}/spicy.mov")
    fc.append(f"[{j}:a]atrim=0:{d},aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.03,afade=t=out:st={d - 0.04:.3f}:d=0.04,asetpts=PTS-STARTPTS[a{k}]")
    if not g.get("broll"):
        fc.append(f"[{j}:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=1,trim=0:{vd}[v{k}]")
    else:
        src, pre = BROLL.get(g["broll"], (f"{RAW}/stock/{g['broll']}.mp4", ""))
        if g["broll"] == "paper":  # a plain cream page; the paper graphic is drawn on top in Remotion
            b = add_in("-f", "lavfi", "-t", str(vd), "-i", "color=c=0xF5F0E6:s=1080x1920:r=30")
        else:
            b = add_in("-ss", str(g["b_s"]), "-t", str(vd), "-i", src)
        fc.append(f"[{b}:v]{pre}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS,"
                  f"tpad=stop_mode=clone:stop_duration=1,trim=0:{vd}[bg{k}]")
        fc.append(f"[{j}:v]crop=420:420:350:570,scale={PIP}:{PIP},fps=30,format=rgba,"
                  f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(lte(hypot(X-{PIP / 2},Y-{PIP / 2}),{PIP / 2 - 2}),255,0)',setpts=PTS-STARTPTS[pip{k}]")
        R = PIP + 16
        fc.append(f"color=c=0xF5F0E6:s={R}x{R}:d={vd},format=rgba,geq=r='245':g='240':b='230':a='if(lte(hypot(X-{R / 2},Y-{R / 2}),{R / 2 - 1}),255,0)'[ring{k}]")
        px, py = {"joywindow": (702, 880), "teacherkids": (702, 470), "paper": (48, 60), "ph_teach": (48, 100), "ph_look": (48, 100), "ph_fun": (48, 1500)}.get(g["broll"], (PX, PY))  # Joy's face is top-left in her own footage: keep it clear
        fc.append(f"[bg{k}][ring{k}]overlay={px - 8}:{py - 8}[bgr{k}];[bgr{k}][pip{k}]overlay={px}:{py}:eof_action=repeat,trim=0:{vd},format=yuv420p,setpts=PTS-STARTPTS[v{k}]")
    labels.append(f"[a{k}]")
fc.append("".join(labels) + f"concat=n={len(segs)}:v=0:a=1[a0]")
prev = "v0"
fc.append("[v0]null[x0]"); prev = "x0"
for k in range(1, len(segs)):
    fc.append(f"[{prev}][v{k}]xfade=transition=fade:duration={T}:offset={segs[k]['out_s']:.3f}[x{k}]"); prev = f"x{k}"
fc.append(f"[{prev}]null[v0]")
tail = round(plan["duration"] - plan["speechEnd"], 3)
fc.append(f"[v0]tpad=stop_mode=clone:stop_duration={tail}[v];[a0]apad=whole_dur={plan['duration']}[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-t", str(plan["duration"]),
                "-c:v", "h264_videotoolbox", "-b:v", "20M", "-c:a", "pcm_s16le", f"{V}/cut.mov"], check=True)
print("cut.mov", plan["duration"], "s")
