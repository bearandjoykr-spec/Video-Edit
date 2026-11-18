#!/bin/bash
# Usage: catalogue.sh <raw dir> <out dir>  — probe + 12-frame contact sheet per clip
RAW="$1"; OUT="$2"; mkdir -p "$OUT/sheets"
for d in "$RAW"/dl_*; do
  n=${d##*_}; f=$(ls "$d" | head -1); [ -z "$f" ] && continue; p="$d/$f"
  [ -f "$OUT/sheets/$n.jpg" ] && continue
  info=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,color_transfer:stream_side_data=rotation:format=duration -of default=nw=1 "$p" 2>/dev/null | tr '\n' ' ')
  echo "$n | $f | $info" >> "$OUT/probe.txt"
  case "$f" in *.heic|*.HEIC|*.jpg|*.JPG|*.png|*.PNG) sips -s format jpeg -Z 800 "$p" --out "$OUT/sheets/$n.jpg" >/dev/null; continue;; esac
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$p")
  ffmpeg -v error -y -i "$p" -vf "fps=12/$dur,scale=320:-2,tile=6x2,format=yuvj420p" -frames:v 1 "$OUT/sheets/$n.jpg"
done
