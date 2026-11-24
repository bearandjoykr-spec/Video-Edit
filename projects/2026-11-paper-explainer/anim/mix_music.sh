#!/bin/bash
# Sound for the paper explainer: the owner's Korean track (owner, 24 Nov 2026: "use this music") under the paper sound effects.
# usage (in anim/): bash mix_music.sh [track.mp3] [music_db]   -> build/audio.wav (build.mjs embeds it; render.mjs normalises to -16 LUFS)
# Tracks and licences: ../music/SOURCE.md
set -e
TRACK=${1:-../music/korean-music-614543.mp3}; MDB=${2:--5}
./py audio/audio.py build/sfx.wav
ffmpeg -v error -y -i build/sfx.wav -i "$TRACK" -filter_complex \
 "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:64,volume=${MDB}dB,afade=t=in:d=1.2,afade=t=out:st=61.2:d=2.8[m];[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=-3dB[s];[m][s]amix=inputs=2:normalize=0:duration=longest,atrim=0:64[o]" \
 -map "[o]" -ar 48000 build/audio.wav
echo "audio -> build/audio.wav ($TRACK at ${MDB} dB)"
