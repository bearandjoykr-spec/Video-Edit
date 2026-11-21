#!/bin/bash
# DAY 37 Instagram package: MP4 (Day 23/34 settings), cover (frame 75: Joy + 원어민 ≠ 유아 영어 전문가), Korean srt. Run from the repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
P=projects/2026-11-day37-yeongyu-check; D=exports/instagram/day37; B=BearJoy_Day37; mkdir -p $D
ffmpeg -nostdin -v error -y -i renders/day37/day37-full.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
(cd remotion && npx remotion still src/index.ts Day37 /tmp/day37-cover.png --frame=75 --log=error </dev/null) && ffmpeg -nostdin -v error -y -i /tmp/day37-cover.png -q:v 2 "$D/${B}_Cover.jpg"
.venv/bin/python - "$P/versions/part4/plan.json" "$D/${B}_ko.srt" <<'PY'
import json, sys
p = json.load(open(sys.argv[1])); f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
out = [f"{i + 1}\n{f(c['s'])} --> {f(c['e'])}\n{c['text']}\n" for i, c in enumerate(p["captions"])]
open(sys.argv[2], "w", encoding="utf8").write("\n".join(out))
PY
cp $P/caption.txt "$D/caption.txt"
ls -la $D
