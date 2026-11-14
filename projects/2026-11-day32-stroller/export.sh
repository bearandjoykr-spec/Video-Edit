#!/bin/bash
# Instagram package for the stroller-walk reel, posted as DAY 30 (Joy, 14 Nov 2026). Run from the repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
P=projects/2026-11-day32-stroller; D=exports/instagram/day30; B=BearJoy_Day30; mkdir -p $D
ffmpeg -nostdin -v error -y -i renders/day32/day30-final.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
ffmpeg -nostdin -v error -y -ss 0.7 -i renders/day32/day30-final.mp4 -frames:v 1 -q:v 2 "$D/${B}_Cover.jpg"
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
