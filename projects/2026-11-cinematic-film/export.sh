#!/bin/bash
# Final exports for "한 마디의 문" (run from repo root after render.py compose h|v and mix.py).
# Standard-range H.264 (libx264, as projects/2026-11-welcome-reels/export.sh), AAC 48 kHz, covers, .srt, caption.
set -e; export PATH=/opt/homebrew/bin:$PATH
P=projects/2026-11-cinematic-film; R=renders/cinematic-film
WEB=exports/website/cinematic-film; IG=exports/instagram/cinematic-film; mkdir -p $WEB $IG
B=BearJoy_OnePhraseOpensADoor
enc() { ffmpeg -nostdin -v error -y -i "$1" -i $R/mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -profile:v high \
  -level "$3" -b:v "$4" -maxrate "$5" -bufsize "$6" -pix_fmt yuv420p -color_range tv -colorspace bt709 -color_trc bt709 \
  -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -shortest -movflags +faststart "$2"; }
enc $R/h/composed.mov $WEB/${B}_16x9.mp4 4.2 14M 18M 28M
enc $R/v/composed.mov $IG/${B}_9x16.mp4 4.1 10M 12M 18M
# covers: the title over the flags (96.2 s)
ffmpeg -nostdin -v error -y -ss 96.2 -i $WEB/${B}_16x9.mp4 -frames:v 1 -pix_fmt yuvj420p -q:v 2 $WEB/${B}_Cover.jpg
ffmpeg -nostdin -v error -y -ss 96.2 -i $IG/${B}_9x16.mp4 -frames:v 1 -pix_fmt yuvj420p -q:v 2 $IG/${B}_Cover.jpg
cp $P/caption.txt $IG/caption.txt
tools/fx-venv/bin/python - $WEB $IG <<'PY'
import sys; sys.path.insert(0, 'projects/2026-11-cinematic-film')
from plan import LINES
f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
for lang, k in (('ko', 2), ('en', 3)):
    rows = []
    for ln in LINES:
        text = ln[k] or ln[2]
        rows.append(f"{len(rows) + 1}\n{f(ln[0])} --> {f(ln[1])}\n{text}\n")
    for d in sys.argv[1:]:
        open(f'{d}/subtitles-{lang}.srt', 'w', encoding='utf8').write('\n'.join(rows))
PY
ls -la $WEB $IG
