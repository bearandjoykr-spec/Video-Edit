#!/bin/bash
# DAY 34 Instagram package: MP4, cover (frame 0), Korean srt, and the clean save card PNG for '그림책' DMs. Run from the repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
P=projects/2026-11-day34-bookguide; D=exports/instagram/day34; B=BearJoy_Day34; mkdir -p $D
ffmpeg -nostdin -v error -y -i renders/day34/day34-final.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
(cd remotion && npx remotion still src/index.ts Day34 /tmp/day34-cover.png --frame=0 --log=error </dev/null) && ffmpeg -nostdin -v error -y -i /tmp/day34-cover.png -q:v 2 "$D/${B}_Cover.jpg"
F=$(.venv/bin/python -c "import json;p=json.load(open('$P/versions/main/timeline.json'));print(int((next(x for x in p['sections'] if x['kind']=='summary')['e']-.5)*30))")
(cd remotion && npx remotion still src/index.ts Day34 ../$D/${B}_그림책카드.png --frame=$F --log=error </dev/null)
.venv/bin/python - "$P/versions/main/timeline.json" "$D/${B}_ko.srt" <<'PY'
import json, sys
p = json.load(open(sys.argv[1])); f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
caps = [x for x in p["sections"] if x["vo"]]; out = []
for i, c in enumerate(caps):
    out.append(f"{i + 1}\n{f(c['s'])} --> {f(c['e'])}\n{c['vo']}\n")
open(sys.argv[2], "w", encoding="utf8").write("\n".join(out))
PY
