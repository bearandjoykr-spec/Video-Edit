#!/bin/bash
# Cuts the storyboard highlights out of the full picture + mix. Run from repo root after the full render.
set -e; export PATH=/opt/homebrew/bin:$PATH
F=renders/day0/full-picture.mp4; W=projects/2026-11-day0-welcome/versions/main/audio/mix.wav; R=renders/day0/high; mkdir -p renders/day0/high
rm -f renders/day0/high/*.mp4 renders/day0/high/list.txt; i=0
for r in "4 22" "53 78" "131 137" "163 172" "194 200" "214 224" "247 254" "344 354" "378 391"; do
  set -- $r
  ffmpeg -nostdin -v error -y -ss $1 -to $2 -i $F -ss $1 -to $2 -i $W -map 0:v -map 1:a -vf scale=1280:-2,format=yuv420p -c:v libx264 -preset slow -crf 27 -c:a aac -b:a 128k -shortest $R/p$i.mp4
  echo "file p$i.mp4" >> $R/list.txt; i=$((i+1))
done
ffmpeg -nostdin -v error -y -f concat -safe 0 -i $R/list.txt -c copy -movflags +faststart $R/sample.mp4
ls -la $R/sample.mp4; ffprobe -v error -show_entries format=duration -of csv=p=0 $R/sample.mp4
