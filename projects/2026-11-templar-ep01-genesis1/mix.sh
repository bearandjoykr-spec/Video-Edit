#!/bin/sh
# usage: sh mix.sh <voice wav> <offset s> <total s> <out wav> <plan.json>
# Voice: high-pass, gentle compression, to -16 LUFS. Music bed -34, campfire -33, SFX (page turns etc.) peaks about -20 dBFS.
# Final: two-pass loudnorm to -14 LUFS, true peak -1.5 dB, 48 kHz.
set -e
# Fuller voice: warm low end (chest), slight low-mid body, gentle cut of boxiness, a little presence and air,
# then two-stage compression so the voice sits big and steady, plus a very short room so it is not bone-dry.
VOICE_FX="highpass=f=55,lowshelf=f=140:g=4.5:w=0.7,equalizer=f=250:t=q:w=1.1:g=1.5,equalizer=f=480:t=q:w=1.4:g=-2,equalizer=f=3200:t=q:w=1.2:g=2,highshelf=f=9000:g=1.5,acompressor=threshold=-28dB:ratio=2.5:attack=20:release=200:makeup=3,acompressor=threshold=-18dB:ratio=4:attack=5:release=120:makeup=1,aecho=0.9:0.6:28|47:0.07|0.05"
V=$1; OFF=$2; DUR=$3; OUT=$4; PLAN=$5; D=$(dirname "$0")
mkdir -p "$D/work"
# Owner-supplied beds (MUSIC_SRC / FIRE_SRC) are looped to length with a 3 s fade-in, 8 s fade-out; otherwise synthesise.
bed() { # src dur out
  ffmpeg -v error -y -stream_loop -1 -i "$1" -t "$2" -af "afade=in:d=3,afade=out:st=$(python3 -c "print($2-8)"):d=8,aformat=sample_rates=48000:channel_layouts=stereo" -c:a pcm_s24le "$3"; }
if [ -n "$MUSIC_SRC" ]; then bed "$MUSIC_SRC" "$DUR" "$D/work/music.wav"; else [ -f "$D/work/music.wav" ] || python3 "$D/audio/synth_sanctum.py" "$DUR" "$D/work/music.wav"; fi
if [ -n "$FIRE_SRC" ]; then bed "$FIRE_SRC" "$DUR" "$D/work/fire.wav"; else [ -f "$D/work/fire.wav" ] || python3 "$D/audio/synth_campfire.py" "$DUR" "$D/work/fire.wav"; fi
python3 "$D/audio/synth_sfx.py" "$PLAN" "$D/work/sfx.wav"
MS=$(python3 -c "print(int($OFF*1000))")
ffmpeg -v error -y -i "$V" -af "$VOICE_FX,loudnorm=I=-16:TP=-2:LRA=7,adelay=${MS}:all=1,apad,atrim=0:${DUR},aformat=sample_rates=48000:channel_layouts=stereo" -ar 48000 "$D/work/voice.wav"
ffmpeg -v error -y -i "$D/work/music.wav" -af "loudnorm=I=-34:TP=-9:LRA=11" -ar 48000 "$D/work/music_n.wav"
ffmpeg -v error -y -i "$D/work/fire.wav" -af "loudnorm=I=-33:TP=-9:LRA=11" -ar 48000 "$D/work/fire_n.wav"
ffmpeg -v error -y -i "$D/work/voice.wav" -i "$D/work/music_n.wav" -i "$D/work/fire_n.wav" -i "$D/work/sfx.wav" \
  -filter_complex "[3]volume=-14dB[s];[0][1][2][s]amix=inputs=4:normalize=0:duration=first" -ar 48000 "$D/work/premix.wav"
J=$(ffmpeg -hide_banner -i "$D/work/premix.wav" -af loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
g() { echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i "$D/work/premix.wav" -af "loudnorm=I=-14:TP=-1.5:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" -ar 48000 -c:a pcm_s24le "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
