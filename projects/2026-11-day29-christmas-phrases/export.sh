#!/bin/bash
# Day 29 / Christmas Countdown D-43 Instagram package: standard-range H.264 MP4 (house settings, see
# projects/2026-11-welcome-reels/export.sh), cover JPG from the hook, caption.txt and Korean subtitles. Run from repo root.
set -e
P=projects/2026-11-day29-christmas-phrases; X=exports/instagram/day29; B=BearJoy_Day29_ChristmasCountdown_D43
mkdir -p $X
ffmpeg -nostdin -v error -y -i renders/day29-final-silent.mp4 -i $P/versions/main/mix.wav -map 0:v -map 1:a -shortest \
  -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$X/$B.mp4"
ffmpeg -nostdin -v error -y -ss 2.2 -i renders/day29-final-silent.mp4 -frames:v 1 -q:v 2 "$X/${B}_Cover.jpg"
cp $P/caption.txt "$X/caption.txt"
python3 - "$P/versions/main/plan.json" "$X/${B}_ko.srt" <<'PY'
import json, sys
p = json.load(open(sys.argv[1])); f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
caps = [{"s": p["hook"]["s"], "e": p["hook"]["e"], "ko": p["hook"]["ko"]}] + p["captions"]
caps += [{"s": s["lineS"], "e": s["e"], "ko": s["ko"]} for s in p["segments"] if s["kind"] == "film"]
caps.sort(key=lambda c: c["s"]); out = []
for i, c in enumerate(caps):
    e = min(c["e"], caps[i + 1]["s"]) if i + 1 < len(caps) else c["e"]
    out.append(f"{i + 1}\n{f(c['s'])} --> {f(e)}\n{c['ko']}\n")
open(sys.argv[2], "w", encoding="utf8").write("\n".join(out))
PY
ls -la $X
