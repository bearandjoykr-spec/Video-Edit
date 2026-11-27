#!/bin/bash
# DAY 41 Instagram package: MP4 (DAY 37 settings), cover (hook with the resource), Korean srt, caption. Run from the repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
P=projects/2026-11-day41-home-english; D=exports/instagram/day41; B=BearJoy_Day41; mkdir -p $D
ffmpeg -nostdin -v error -y -i renders/day41/final-41.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
(cd remotion && npx remotion still src/index.ts Day41 /tmp/day41-cover.png --frame=45 --log=error </dev/null) && ffmpeg -nostdin -v error -y -i /tmp/day41-cover.png -q:v 2 "$D/${B}_Cover.jpg"
.venv/bin/python - "$D/${B}_ko.srt" <<'PY'
import json, sys
p = json.load(open("remotion/src/day41.json")); f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
open(sys.argv[1], "w", encoding="utf8").write("\n".join(f"{i + 1}\n{f(c['s'])} --> {f(c['e'])}\n{c['text']}\n" for i, c in enumerate(p["caps"])))
PY
cp $P/caption.txt "$D/caption.txt"; ls -la $D
