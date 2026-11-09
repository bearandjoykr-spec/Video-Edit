#!/bin/bash
# Renders the storyboard sample: the listed ranges of the real edit, joined, 720p, voice + SFX (music once chosen). Run from repo root.
set -e
export PATH=/opt/homebrew/bin:$PATH
P=projects/2026-11-day0-welcome; R=renders/day0/sample; mkdir -p renders/day0/sample
rm -f renders/day0/sample/*.mp4 renders/day0/sample/list.txt
cd remotion; [ -d ../renders/day0/bundle ] || npx remotion bundle src/index.ts --out-dir=../renders/day0/bundle >/dev/null; cd ..
i=0
for r in "0 22" "45.5 69" "183 189" "332 341" "366 379"; do
  set -- $r; a=$(python3 -c "print(round($1*30))"); b=$(python3 -c "print(round($2*30)-1)")
  (cd remotion; npx remotion render ../renders/day0/bundle Day0Welcome ../$R/v$i.mp4 --frames=$a-$b --concurrency=6 --crf=16 --muted --log=error)
  ffmpeg -nostdin -v error -y -i $R/v$i.mp4 -ss $1 -to $2 -i $P/versions/main/audio/mix.wav -map 0:v -map 1:a -vf scale=1280:-2,format=yuv420p -c:v libx264 -preset slow -crf 25 -c:a aac -b:a 128k -shortest $R/p$i.mp4
  echo "file p$i.mp4" >> $R/list.txt; i=$((i+1))
done
ffmpeg -nostdin -v error -y -f concat -safe 0 -i $R/list.txt -c copy -movflags +faststart $R/sample.mp4
ls -la $R/sample.mp4; ffprobe -v error -show_entries format=duration -of csv=p=0 $R/sample.mp4
