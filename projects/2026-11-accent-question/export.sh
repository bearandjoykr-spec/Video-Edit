#!/bin/bash
# DAY 29 (accent question) Instagram package: standard-range H.264 MP4, cover JPG from the hook, caption.txt and Korean subtitles.
# Run from the repo root after mix.py has written renders/accentq/day29-final.mp4. Approved by the owner, 12 Nov 2026 (posting 13 Nov).
set -e
P=projects/2026-11-accent-question; D=exports/instagram/day29-accent; B=BearJoy_Day29_AccentQuestion; mkdir -p $D
ffmpeg -nostdin -v error -y -i renders/accentq/day29-final.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
ffmpeg -nostdin -v error -y -ss 1.2 -i renders/accentq/day29-final.mp4 -frames:v 1 -q:v 2 "$D/${B}_Cover.jpg"
cp $P/caption.txt $D/caption.txt
python3 - "$P/versions/main/timeline_v2.json" "$D/${B}_ko.srt" <<'PY'
import json, sys
p = json.load(open(sys.argv[1])); f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
caps = sorted(p["captions"], key=lambda c: c["s"]); out = []
for i, c in enumerate(caps):
    e = min(c["e"], caps[i + 1]["s"]) if i + 1 < len(caps) else min(c["e"], p["speechEnd"])
    out.append(f"{i + 1}\n{f(max(0, c['s']))} --> {f(e)}\n{c['ko']}\n")
open(sys.argv[2], "w", encoding="utf8").write("\n".join(out))
PY
ls -la $D
