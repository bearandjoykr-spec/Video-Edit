#!/bin/bash
# DAY 31 Instagram package (Mark's 영유 interview). Run from the repo root after the render and mix.
set -e; export PATH=/opt/homebrew/bin:$PATH
P=projects/2026-11-mark-spicy; D=exports/instagram/day31; B=BearJoy_Day31; mkdir -p $D
ffmpeg -nostdin -v error -y -i renders/spicy/day31-final.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
(cd remotion && npx remotion still src/index.ts MarkSpicy /tmp/day31-cover.png --frame=0 --log=error </dev/null) && ffmpeg -nostdin -v error -y -i /tmp/day31-cover.png -q:v 2 "$D/${B}_Cover.jpg"
.venv/bin/python - "$P/versions/main/timeline_v2.json" "$D/${B}_ko.srt" <<'PY'
import json, sys
p = json.load(open(sys.argv[1])); f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
caps = sorted(p["captions"], key=lambda c: c["s"]); out = []
for i, c in enumerate(caps):
    e = min(c["e"], caps[i + 1]["s"]) if i + 1 < len(caps) else min(c["e"], p["speechEnd"])
    out.append(f"{i + 1}\n{f(max(0, c['s']))} --> {f(e)}\n{c['ko']}\n")
open(sys.argv[2], "w", encoding="utf8").write("\n".join(out))
PY
ls -la $D
