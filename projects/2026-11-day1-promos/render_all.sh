#!/bin/bash
# Renders the three promos and writes them to renders/day1/ig/final. Run from the repo root.
set -e
export PATH="/opt/homebrew/bin:$PATH"
R=renders/day1/ig/final; mkdir -p $R
cd remotion
node class-stills.mjs ../renders/day1/ig/sb-kkakkung 1 id=PromoKkakkung 1 5 8.5 11.5 18 21.5 27.5 33 </dev/null | tail -1
node class-stills.mjs ../renders/day1/ig/sb-three-phrases 0 id=PromoThreePhrases 1 5 7.5 9.5 14 24 28 33 </dev/null | tail -1
node class-stills.mjs ../renders/day1/ig/sb-mistakes-ok 0 id=PromoMistakesOk 1 6 10 15 22 26 32 </dev/null | tail -1
B=$(cat ../renders/day1/bundle-path.txt)
npx remotion render "$B" PromoKkakkung ../$R/kkakkung-pic.mp4 --crf=16 --color-space=bt709 --log=error </dev/null
npx remotion render "$B" PromoThreePhrases ../$R/three-phrases-pic.mp4 --crf=16 --color-space=bt709 --log=error </dev/null
npx remotion render "$B" PromoMistakesOk ../$R/mistakes-ok-pic.mp4 --crf=16 --color-space=bt709 --log=error </dev/null
cd ..
for n in kkakkung three-phrases mistakes-ok; do
  .venv/bin/python projects/2026-11-day1-promos/mix.py $n $R/$n-pic.mp4 $R/$n.mp4
  ffmpeg -hide_banner -i $R/$n.mp4 -af ebur128=peak=true -vn -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
done
