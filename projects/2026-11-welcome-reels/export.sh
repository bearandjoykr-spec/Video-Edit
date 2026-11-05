#!/bin/bash
# Instagram package per reel: standard-range H.264 MP4, a cover JPG from the hook, caption.txt and Korean subtitles. Run from repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
R=projects/2026-11-welcome-reels; X=exports/instagram/little-steps-reels
for row in "A use Use 0.45" "B perfect PerfectEnglish 1.0" "C bearvoice BearVoice 1.6"; do
  set -- $row; D=$X/$1-$2; mkdir -p "$D"; B=BearJoy_LittleSteps_Reel_$1_$3
  ffmpeg -nostdin -v error -y -i renders/reels/$2.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
    -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
  ffmpeg -nostdin -v error -y -ss $4 -i renders/reels/$2.mp4 -frames:v 1 -q:v 2 "$D/${B}_Cover.jpg"
  cp $R/captions/$2.txt "$D/caption.txt"
  .venv/bin/python - "$R/versions/$2/timeline.json" "$D/captions-ko.srt" <<'P'
import json, sys
p = json.load(open(sys.argv[1])); f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
caps = sorted(p["captions"], key=lambda c: c["s"]); out = []
for i, c in enumerate(caps):
    e = min(c["e"], caps[i + 1]["s"]) if i + 1 < len(caps) else min(c["e"], p["speechEnd"])
    out.append(f"{i + 1}\n{f(c['s'])} --> {f(e)}\n{c['ko']}\n")
open(sys.argv[2], "w", encoding="utf8").write("\n".join(out))
P
done
ls -la $X/*
