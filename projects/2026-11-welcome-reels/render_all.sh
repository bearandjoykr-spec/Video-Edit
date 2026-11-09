#!/bin/bash
# Renders the three reels and a lighter preview of each. Run from repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
R=projects/2026-11-welcome-reels; O=renders/reels; mkdir -p renders/reels/preview
cd remotion; npx remotion bundle src/index.ts --out-dir=../renders/reels/bundle --log=error >/dev/null; cd ..
for pair in "use ReelUse" "perfect ReelPerfect" "bearvoice ReelBearVoice"; do
  set -- $pair
  (cd remotion; npx remotion render ../renders/reels/bundle $2 ../renders/reels/$1-picture.mp4 --concurrency=7 --crf=17 --color-space=bt709 --muted --log=error)
  .venv/bin/python $R/mix.py $1 $O/$1-picture.mp4 $O/$1.mp4
  ffmpeg -nostdin -v error -y -i $O/$1.mp4 -vf scale=540:-2,format=yuv420p -c:v libx264 -preset slow -crf 27 -c:a aac -b:a 128k -movflags +faststart $O/preview/$1.mp4
  ls -la $O/preview/$1.mp4; ffmpeg -nostdin -hide_banner -i $O/$1.mp4 -af ebur128=peak=true:framelog=quiet -f null - 2>&1 | grep -E " I:|Peak:"
done
