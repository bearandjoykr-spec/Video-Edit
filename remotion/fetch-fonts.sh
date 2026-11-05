#!/bin/sh
# Download the brand fonts (Gowun Batang, Playfair Display, Noto Sans KR) into public/fonts.
set -e
cd "$(dirname "$0")/public/fonts"
curl -sS "https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400;1,600&family=Noto+Sans+KR:wght@500;700" -A "curl/8" \
  | grep -oE "https://fonts.gstatic.com[^)]+" | while read -r u; do curl -sS -o "$(basename "$u")" "$u"; done
ls *.ttf
# Noto Color Emoji (BearJoyReelV2 loads this exact file name)
curl -sS -o Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf "https://fonts.gstatic.com/s/notocoloremoji/v50/Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf"
