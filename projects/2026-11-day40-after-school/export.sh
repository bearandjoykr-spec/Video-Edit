#!/bin/bash
# DAY 40 Instagram package: MP4 (DAY 37 settings), cover (hook frame), Korean/English srt, caption, the four comment images. Run from the repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
P=projects/2026-11-day40-after-school; D=exports/instagram/day40; B=BearJoy_Day40; mkdir -p $D
ffmpeg -nostdin -v error -y -i renders/day40/final-40.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
(cd remotion && npx remotion still src/index.ts Day40Phrases /tmp/day40-cover.png --frame=60 --log=error </dev/null) && ffmpeg -nostdin -v error -y -i /tmp/day40-cover.png -q:v 2 "$D/${B}_Cover.jpg"
.venv/bin/python - "$D/${B}.srt" <<'PY'
import json, sys
p = json.load(open("remotion/src/day40.json")); f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
caps = [(0.0, p["hook"][1], "하원 후, 이렇게 말해요!\nWhat can I say in English to my child after school?")]
caps += [(q["s"], q["e"], q["en"].replace("\n", " ") + "\n" + q["ko"]) for q in p["phrases"]]
caps += [(p["outro"], p["duration"], "댓글에서 상황별 대화문 4가지를 확인하세요\nCheck the comments below")]
open(sys.argv[1], "w", encoding="utf8").write("\n".join(f"{i + 1}\n{f(s)} --> {f(e)}\n{t}\n" for i, (s, e, t) in enumerate(caps)))
PY
cp $P/caption.txt "$D/caption.txt"
for n in 48 49 50 51; do i=$((n - 47)); cp remotion/public/day40/card$n.jpg "$D/댓글_대화문_0$i.jpg"; done
ls -la $D
