#!/bin/bash
# Cuts the owner's montage, lesson clips and animated logo out of their finished edit, as rendered. Run from repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
E=raw-footage/day0-owner-edit/edit.mp4; O=remotion/public/day0/owner; mkdir -p "$O"
enc="-c:v libx264 -preset medium -crf 15 -pix_fmt yuv420p -an"
ffmpeg -nostdin -v error -y -i $E -t 12.3 -vf scale=1920:1080 $enc $O/montage.mp4
ffmpeg -nostdin -v error -y -ss 345 -t 6 -i $E $enc $O/logo-end.mp4
clip(){ ffmpeg -nostdin -v error -y -ss $2 -to $3 -i $E -vf crop=$4 $enc $O/$1.mp4; }
clip pip-a 64.0 73.0 521:293:91:710
clip pip-b1 79.0 84.3 519:290:1361:725
clip pip-b2 86.0 90.4 519:290:1361:725
for k in 1 2 3; do y=$((233 + (k-1)*285)); clip pip-c$k 207.0 215.3 468:264:43:$y; clip pip-d$k 220.0 227.7 468:264:43:$y; done
ffmpeg -nostdin -v error -y -i $E -t 12.3 -vn -ar 48000 -ac 2 -c:a pcm_s16le projects/2026-11-day0-welcome/versions/main/audio/montage.wav
ls -la $O | tail -n +4 | awk '{print $5,$9}'
