"""Cut the Day 25 picture and voice track. Run from the repo root:
  .venv/bin/python projects/2026-11-day25-kyobo/cut.py
Writes remotion/public/day25/main/cut.mov (1080x1920, 30 fps; audio = hook sound + voice-over)
and projects/2026-11-day25-kyobo/work/voice.wav (for word timing).
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from edl import PIC, VO, VO_SRC, HOOK, SDR, SPEECH_END, END  # noqa: E402

OUT = "remotion/public/day25/main"; W = f"{HERE}/work"
os.makedirs(OUT, exist_ok=True); os.makedirs(W, exist_ok=True)
TOTAL = round(SPEECH_END + END, 3)
# "image filter": warm, punchy, a little filmic (lifted blacks, warm highlights), light sharpening.
LOOK = ("eq=contrast=1.06:saturation=1.16:gamma=0.98,"
        "curves=r='0/0.03 0.5/0.52 1/1':g='0/0.02 0.5/0.5 1/0.98':b='0/0.05 0.5/0.48 1/0.94',"
        "unsharp=5:5:0.5")
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)

parts, t = [], 0.0
for k, (clip, s, e, o) in enumerate(PIC):
    out = f"{W}/p{k:02d}.mov"
    if clip == "ART":
        d = round(TOTAL - t, 3)
        # Oxford-to-Seoul watercolour, scaled to full height and panned slowly left to right
        vf = (f"scale=-2:1920:flags=lanczos,crop=1080:1920:x='(iw-1080)*0.15+(iw-1080)*0.55*t/{d}':y=0,"
              "gblur=sigma=1.2,eq=brightness=0.02:saturation=1.05,format=yuv420p")
        run("-loop", "1", "-framerate", "30", "-i", "brand/assets/art-both.jpg", "-t", str(d), "-vf", vf,
            "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-r", "30", out)
    else:
        f = []
        if "crop" in o:
            cw, ch, cx, cy = o["crop"]; f.append(f"crop={cw}:{ch}:{cx}:{cy}")
        f.append("scale=1080:1920:flags=lanczos")
        if "slow" in o:
            f.append(f"setpts={o['slow']}*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1")
        f += [LOOK, "fps=30", "format=yuv420p"]
        d = round((e - s) * o.get("slow", 1), 3)
        run("-ss", str(s), "-t", str(round(e - s, 3)), "-i", f"{SDR}/{clip}.mov", "-vf", ",".join(f), "-t", str(d), "-an",
            "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-r", "30", out)
    parts.append(out); t += d
    print(f"{k:2d} {clip} {d:6.3f}s  ends {t:6.3f}")

with open(f"{W}/parts.txt", "w") as fh:
    fh.writelines(f"file '{p}'\n" for p in parts)
run("-f", "concat", "-safe", "0", "-i", f"{W}/parts.txt", "-c", "copy", f"{W}/picture.mov")

# voice track: the hook's own sound, then each voice-over piece at its program time
clip, hs, he = HOOK
ins = ["-ss", str(hs), "-t", str(he - hs), "-i", f"{SDR}/{clip}.mov"]
fc = ["[0:a]aresample=48000,aformat=channel_layouts=mono,afade=t=out:st=5.6:d=0.23[h]"]
labels = ["[h]"]
for k, (s, e, p) in enumerate(VO):
    ins += ["-ss", str(s), "-t", str(round(e - s, 3)), "-i", VO_SRC]
    ms = int(round(p * 1000))
    fc.append(f"[{k + 1}:a]aresample=48000,aformat=channel_layouts=mono,afade=t=in:d=0.03,afade=t=out:st={e - s - 0.05:.3f}:d=0.05,"
              f"adelay={ms}:all=1[v{k}]")
    labels.append(f"[v{k}]")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,apad=whole_dur={TOTAL},atrim=0:{TOTAL}[a]")
run(*ins, "-filter_complex", ";".join(fc), "-map", "[a]", "-c:a", "pcm_s16le", "-ar", "48000", f"{W}/voice.wav")
run("-i", f"{W}/picture.mov", "-i", f"{W}/voice.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "pcm_s16le",
    "-t", str(TOTAL), f"{OUT}/cut.mov")
print("cut.mov", TOTAL, "s")
