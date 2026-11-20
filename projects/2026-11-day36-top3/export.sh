#!/bin/bash
# DAY 36 Instagram package: MP4 (Day 23/34 settings), cover (Day36Cover: Mark smiling, bg2 20.7 s), Korean srt. Run from the repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
P=projects/2026-11-day36-top3; D=exports/instagram/day36; B=BearJoy_Day36; mkdir -p $D
ffmpeg -nostdin -v error -y -i renders/day36/day36-final.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
(cd remotion && npx remotion still src/index.ts Day36Cover /tmp/day36-cover.png --frame=0 --log=error </dev/null) && ffmpeg -nostdin -v error -y -i /tmp/day36-cover.png -q:v 2 "$D/${B}_Cover.jpg"
.venv/bin/python - "$P/versions/main/plan.json" "$D/${B}_ko.srt" <<'PY'
import json, sys
p = json.load(open(sys.argv[1])); f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
out = [f"{i + 1}\n{f(c['s'])} --> {f(c['e'])}\n{c['text']}\n" for i, c in enumerate(p["captions"])]
open(sys.argv[2], "w", encoding="utf8").write("\n".join(out))
PY
cp $P/caption.txt "$D/caption.txt"
ls -la $D
