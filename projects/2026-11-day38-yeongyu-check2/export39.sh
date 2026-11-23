#!/bin/bash
# DAY 39 Instagram package: MP4 (DAY 37 settings), cover (frame 8: Joy's Wonders photo + the question), Korean srt, caption. Run from the repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
P=projects/2026-11-day38-yeongyu-check2; D=exports/instagram/day39; B=BearJoy_Day39; mkdir -p $D
ffmpeg -nostdin -v error -y -i renders/day38/final-39.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
(cd remotion && npx remotion still src/index.ts Day39 /tmp/day39-cover.png --frame=8 --log=error </dev/null) && ffmpeg -nostdin -v error -y -i /tmp/day39-cover.png -q:v 2 "$D/${B}_Cover.jpg"
.venv/bin/python - "$P/versions/day39/plan.json" "$D/${B}_ko.srt" <<'PY'
import json, sys
p = json.load(open(sys.argv[1])); f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
out = [f"{i + 1}\n{f(c['s'])} --> {f(c['e'])}\n{c['text']}\n" for i, c in enumerate(p["captions"])]
open(sys.argv[2], "w", encoding="utf8").write("\n".join(out))
PY
cp $P/caption-39.txt "$D/caption.txt"
cp $P/textbooks/textbook-table.png "$D/DM_교재표.png"
ls -la $D
