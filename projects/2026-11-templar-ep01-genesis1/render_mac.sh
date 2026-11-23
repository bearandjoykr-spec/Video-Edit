#!/bin/sh
# Templar Ep 1 — version 2 (paintings) — final render on the owner's Mac (Apple M1).
# Run from the repo root (~/Video-Edit) after `git pull`:
#   sh projects/2026-11-templar-ep01-genesis1/render_mac.sh
# It finds the four source files in ~/Downloads (or pass them: voice bed chant fire).
# Output: exports/youtube/templar-ep01/Templar_Ep01_In_the_Beginning_1080p.mp4 (12 Mbps H.264, BT.709, AAC 48 kHz, -14 LUFS)
# Resumable: finished video parts in remotion/out/templar/ are kept if you run it again.
set -e
cd "$(dirname "$0")/../.."
P=projects/2026-11-templar-ep01-genesis1
DL="$HOME/Downloads"
pick() { [ -n "$1" ] && { echo "$1"; return; }; ls -t "$DL"/$2 2>/dev/null | head -1; }
VOICE=$(pick "$1" "Episode 1*In the Beginning*.aif*")
BED=$(pick "$2" "Lands*KT*.[Mm][Pp]3")
CHANT=$(pick "$3" "videoplayback (12)*.mp4")
FIRE=$(pick "$4" "*fire-ambience*.mp3")
for f in "$VOICE" "$BED" "$CHANT" "$FIRE"; do [ -f "$f" ] || { echo "Missing a source file. Found: voice=$VOICE bed=$BED chant=$CHANT fire=$FIRE"; exit 1; }; done
echo "voice: $VOICE"; echo "bed:   $BED"; echo "chant: $CHANT"; echo "fire:  $FIRE"
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
PLAN=$P/versions/main/plan_v2.json
OUT=exports/youtube/templar-ep01; mkdir -p "$OUT" "$P/work" remotion/out/templar
[ -d remotion/node_modules ] || npm ci --prefix remotion

# 1. audio (fuller voice, Landscape KT, chant in the gaps, fire, page turns) -> -14 LUFS
ffmpeg -v error -y -i "$VOICE" -ar 48000 -ac 1 -c:a pcm_s24le "$P/work/voice48k.wav"
$PY "$P/mix.py" "$PLAN" "$P/work/voice48k.wav" "$P/work/final_mix.wav" --bed "$BED" --chant "$CHANT" --fire "$FIRE" --fire-lufs -35

# 2. video in 6 parts (M1: 6 workers, hardware-encoded intermediates are not used: crf parts keep quality)
TOTAL=$(node -e "const p=require('./$PLAN');console.log(Math.ceil(p.duration*p.fps))")
PARTS=6; STEP=$(( (TOTAL + PARTS - 1) / PARTS )); : > remotion/out/templar/parts.txt
i=0; while [ $i -lt $PARTS ]; do
  A=$((i * STEP)); B=$(( (i + 1) * STEP - 1 )); [ $B -ge $TOTAL ] && B=$((TOTAL - 1))
  [ -f remotion/out/templar/v2part$i.mp4 ] || (cd remotion && npx remotion render src/templar/index.ts TemplarEp01v2 "out/templar/v2part$i.mp4" \
    --frames=$A-$B --concurrency=6 --muted --crf=14 --log=error)
  echo "file 'v2part$i.mp4'" >> remotion/out/templar/parts.txt; echo "part $((i+1))/$PARTS done"; i=$((i + 1))
done
ffmpeg -v error -y -f concat -safe 0 -i remotion/out/templar/parts.txt -c copy remotion/out/templar/v2_full.mp4

# 3. YouTube export: 12 Mbps H.264 High, standard-range BT.709, AAC 320k 48 kHz
F="$OUT/Templar_Ep01_In_the_Beginning_1080p.mp4"
ffmpeg -v error -y -i remotion/out/templar/v2_full.mp4 -i "$P/work/final_mix.wav" -map 0:v -map 1:a \
  -c:v libx264 -preset slow -b:v 12M -maxrate 16M -bufsize 24M -profile:v high -pix_fmt yuv420p -g 60 -bf 2 \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest "$F"
ffmpeg -hide_banner -i "$F" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
ls -la "$F"; open -R "$F" 2>/dev/null || true
