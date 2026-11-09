#!/bin/bash
# Clean the owner's voice memo: DeepFilterNet noise/room reduction, then EQ for clarity (less boom, more presence),
# a light de-esser and compression. Run from the repo root. Writes work/vo-clean.wav (used by edl.py).
set -e; export PATH=/opt/homebrew/bin:$PATH
W=projects/2026-11-day25-kyobo/work; mkdir -p $W/df
ffmpeg -v error -y -i raw-footage/2026-11-new/vo-memo.m4a -ac 1 -ar 48000 $W/vo-memo48.wav
tools/deepfilter/deep-filter -a 35 -D -o $W/df $W/vo-memo48.wav
ffmpeg -v error -y -i $W/df/vo-memo48.wav -af "highpass=f=85:poles=2,lowshelf=f=200:g=-4,equalizer=f=350:t=q:w=1.2:g=-1.5,equalizer=f=1300:t=q:w=1:g=2,equalizer=f=2800:t=q:w=0.9:g=4.5,deesser=i=0.35:f=0.45,highshelf=f=10000:g=2.5,acompressor=threshold=-22dB:ratio=2.5:attack=6:release=110:makeup=2,alimiter=limit=0.89" -ar 48000 $W/vo-clean.wav
