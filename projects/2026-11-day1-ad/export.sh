#!/bin/bash
# Day 1 Little Steps ad Instagram package: standard-range H.264 MP4, cover JPG from the hook, caption.txt. Run from repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
D=exports/instagram/day1-ad; B=BearJoy_Day1_LittleSteps_Ad; mkdir -p $D
ffmpeg -nostdin -v error -y -i renders/day1ad/day1ad-final.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
ffmpeg -nostdin -v error -y -ss 1.0 -i renders/day1ad/day1ad-final.mp4 -frames:v 1 -q:v 2 "$D/${B}_Cover.jpg"
ls -la $D
