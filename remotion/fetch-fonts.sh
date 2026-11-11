#!/bin/sh
# Download the TTF fonts into public/fonts (Pretendard woff2 files are committed).
# v1: Gowun Batang, Playfair Display, Noto Sans KR. v2 / class videos: Noto Color Emoji (flags, emoji)
# plus the fonts listed in fonts-v2.css. Filenames must match the gstatic basenames used in the templates.
set -e
cd "$(dirname "$0")/public/fonts"
for css in \
  "https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400;1,600&family=Noto+Sans+KR:wght@500;700" \
  "https://fonts.googleapis.com/css2?family=Noto+Color+Emoji&family=Black+Han+Sans&family=Jua&family=Lilita+One&family=Poppins:wght@700;800;900"; do
  curl -sS "$css" -A "curl/8" | grep -oE "https://fonts.gstatic.com[^)]+" | while read -r u; do curl -sS -o "$(basename "$u")" "$u"; done
done
ls *.ttf
# Noto Color Emoji (BearJoyReelV2 loads this exact file name)
curl -sS -o Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf "https://fonts.gstatic.com/s/notocoloremoji/v50/Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf"
# Day 29 "Countdown to Christmas" caption options: Cinzel 700/900, IM Fell English, Cormorant Garamond 700 italic
for u in https://fonts.gstatic.com/s/cinzel/v26/8vIU7ww63mVu7gtR-kwKxNvkNOjw-jHgTYo.ttf https://fonts.gstatic.com/s/cinzel/v26/8vIU7ww63mVu7gtR-kwKxNvkNOjw-n_gTYo.ttf \
  https://fonts.gstatic.com/s/imfellenglish/v14/Ktk1ALSLW8zDe0rthJysWrnLsAz3Fw.ttf \
  https://fonts.gstatic.com/s/cormorantgaramond/v21/co3smX5slCNuHLi8bLeY9MK7whWMhyjYrGFEsdtdc62E6zd5FTfOjw.ttf; do curl -sS -o "$(basename "$u")" "$u"; done
