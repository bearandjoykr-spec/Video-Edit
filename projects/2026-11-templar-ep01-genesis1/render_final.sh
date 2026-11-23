#!/bin/sh
# Final render of Templar Ep 1 (run on the owner's Mac, or in the cloud with CLOUD=1).
# usage: sh projects/2026-11-templar-ep01-genesis1/render_final.sh <voice .aifc/.wav> <Landscape KT mp3> <chant video/mp4> <fire mp3>
# On the Mac the files are usually in ~/Downloads:
#   "Episode 1 — In the Beginning (Genesis 1-1–2-3).aifc", "Landsacape KT-copy.MP3",
#   "videoplayback (12).mp4", "soundreality-fire-ambience-528618.mp3"
# Output: exports/youtube/templar-ep01/ (final 1080p H.264 + an ~8 Mbps copy for chat)
set -e
cd "$(dirname "$0")/../.."
P=projects/2026-11-templar-ep01-genesis1
OUT=exports/youtube/templar-ep01; mkdir -p "$OUT" "$P/work" remotion/out/templar
VOICE=$1; BED=$2; CHANT=$3; FIRE=$4
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python

# 1. audio
ffmpeg -v error -y -i "$VOICE" -ar 48000 -ac 1 -c:a pcm_s24le "$P/work/voice48k.wav"
$PY "$P/mix.py" "$P/versions/main/plan.json" "$P/work/voice48k.wav" "$P/work/final_mix.wav" \
  --bed "$BED" --chant "$CHANT" --fire "$FIRE" --fire-lufs -35

# 2. video (Mac M1: 6 workers, Remotion's own Chrome; cloud: Playwright's Chromium, in 4 parts)
if [ -n "$CLOUD" ]; then BX="--browser-executable=/opt/pw-browsers/chromium"; CONC=4; else BX=""; CONC=6; fi   # Apple M1: 8 cores (4 performance)
TOTAL=$(node -e "const p=require('./$P/versions/main/plan.json');console.log(Math.ceil(p.duration*p.fps))")
PARTS=4; STEP=$(( (TOTAL + PARTS - 1) / PARTS )); : > remotion/out/templar/parts.txt
i=0; while [ $i -lt $PARTS ]; do
  A=$((i * STEP)); B=$(( (i + 1) * STEP - 1 )); [ $B -ge $TOTAL ] && B=$((TOTAL - 1))
  F=remotion/out/templar/part$i.mp4
  [ -f "$F" ] || (cd remotion && npx remotion render src/templar/index.ts TemplarEp01 "out/templar/part$i.mp4" \
    --frames=$A-$B --concurrency=$CONC $BX --muted --crf=14 --log=error)
  echo "file 'part$i.mp4'" >> remotion/out/templar/parts.txt; i=$((i + 1))
done
ffmpeg -v error -y -f concat -safe 0 -i remotion/out/templar/parts.txt -c copy remotion/out/templar/video_full.mp4

# 3. export: standard-range BT.709 H.264, AAC 48 kHz (YouTube upload)
COL="-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv"
ffmpeg -v error -y -i remotion/out/templar/video_full.mp4 -i "$P/work/final_mix.wav" -map 0:v -map 1:a \
  -c:v libx264 -preset slow -crf 16 -profile:v high -pix_fmt yuv420p $COL \
  -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest "$OUT/Templar_Ep01_In_the_Beginning_1080p.mp4"
# small copy (~8 Mbps) so it can be sent in chat
ffmpeg -v error -y -i "$OUT/Templar_Ep01_In_the_Beginning_1080p.mp4" -c:v libx264 -preset medium -b:v 7500k -maxrate 8M -bufsize 16M \
  -pix_fmt yuv420p $COL -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT/Templar_Ep01_preview_8Mbps.mp4"
ffmpeg -hide_banner -i "$OUT/Templar_Ep01_In_the_Beginning_1080p.mp4" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
ls -la "$OUT"
