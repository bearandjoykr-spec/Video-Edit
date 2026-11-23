#!/bin/sh
# usage: sh mix.sh <voice wav> <offset s> <total s> <out wav> <plan.json>
# Voice: high-pass, gentle compression, to -16 LUFS. Music bed -34, campfire -33, SFX (page turns etc.) peaks about -20 dBFS.
# Final: two-pass loudnorm to -14 LUFS, true peak -1.5 dB, 48 kHz.
set -e
V=$1; OFF=$2; DUR=$3; OUT=$4; PLAN=$5; D=$(dirname "$0")
mkdir -p "$D/work"
[ -f "$D/work/music.wav" ] || python3 "$D/audio/synth_sanctum.py" "$DUR" "$D/work/music.wav"
[ -f "$D/work/fire.wav" ] || python3 "$D/audio/synth_campfire.py" "$DUR" "$D/work/fire.wav"
python3 "$D/audio/synth_sfx.py" "$PLAN" "$D/work/sfx.wav"
MS=$(python3 -c "print(int($OFF*1000))")
ffmpeg -v error -y -i "$V" -af "highpass=f=70,acompressor=threshold=-24dB:ratio=3:attack=15:release=250:makeup=2,loudnorm=I=-16:TP=-2:LRA=7,adelay=${MS}:all=1,apad,atrim=0:${DUR},aformat=sample_rates=48000:channel_layouts=stereo" -ar 48000 "$D/work/voice.wav"
ffmpeg -v error -y -i "$D/work/music.wav" -af "loudnorm=I=-34:TP=-9:LRA=11" -ar 48000 "$D/work/music_n.wav"
ffmpeg -v error -y -i "$D/work/fire.wav" -af "loudnorm=I=-33:TP=-9:LRA=11" -ar 48000 "$D/work/fire_n.wav"
ffmpeg -v error -y -i "$D/work/voice.wav" -i "$D/work/music_n.wav" -i "$D/work/fire_n.wav" -i "$D/work/sfx.wav" \
  -filter_complex "[3]volume=-14dB[s];[0][1][2][s]amix=inputs=4:normalize=0:duration=first" -ar 48000 "$D/work/premix.wav"
J=$(ffmpeg -hide_banner -i "$D/work/premix.wav" -af loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
g() { echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i "$D/work/premix.wav" -af "loudnorm=I=-14:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" -ar 48000 -c:a pcm_s24le "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
