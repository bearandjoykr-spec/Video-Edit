#!/bin/bash
# Usage: prep.sh <raw dir> <out dir>
# Makes an SDR, upright, 30 fps editing copy of every clip: HLG -> SDR via avconvert (BRAND.md rule), else as is.
RAW="$1"; OUT="$2"; mkdir -p "$OUT"
for d in "$RAW"/dl_*; do
  n=${d##*_}; f=$(ls "$d" | head -1); p="$d/$f"; o="$OUT/c$n.mov"
  [ -f "$o" ] && continue
  case "$f" in *.heic|*.HEIC|*.jpg|*.JPG|*.png|*.PNG) sips -s format png "$p" --out "$OUT/c$n.png" >/dev/null; continue;; esac
  nf=$(ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of csv=p=0 "$p")
  [ "$nf" = "1" ] && { echo "$n: single-frame video, skipped"; continue; }
  tr=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of csv=p=0 "$p")
  if [ "$tr" = "arib-std-b67" ] || [ "$tr" = "smpte2084" ]; then
    avconvert -s "$p" -o "$o" -p Preset1920x1080 --replace
  else
    ffmpeg -v error -y -i "$p" -c:v hevc_videotoolbox -b:v 40M -tag:v hvc1 -c:a aac "$o"
  fi
  echo "$n done ($tr)"
done
