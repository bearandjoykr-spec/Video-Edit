#!/bin/bash
# Subject cut-outs for the "words behind the head" moments. Usage: make_mattes.sh (run from repo root)
set -e
P=projects/2026-11-day1-class; SRC=raw-footage/day1-hello-bear/source.mov
while read name s e; do
  [ -f remotion/public/day1/$name.webm ] && continue
  ffmpeg -nostdin -v error -y -ss $s -to $e -i $SRC -an -c:v libx264 -crf 10 -pix_fmt yuv420p $P/matte/$name.mp4
  (cd remotion && npx hyperframes remove-background ../$P/matte/$name.mp4 -o public/day1/$name.webm --device coreml --quality balanced </dev/null)
  echo done $name
done <<L
ready 25.0 28.8
together 278.0 285.0
discovery 124.0 127.2
adventure 337.4 341.4
L
