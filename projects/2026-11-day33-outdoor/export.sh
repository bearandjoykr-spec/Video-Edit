#!/bin/bash
# DAY 33 Instagram package: MP4, cover (frame 0), Korean srt, and the clean "바깥놀이 영어 3문장" card for DMs. Run from the repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
P=projects/2026-11-day33-outdoor; D=exports/instagram/day33; B=BearJoy_Day33; mkdir -p $D
ffmpeg -nostdin -v error -y -i renders/day33/day33-final.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
(cd remotion && npx remotion still src/index.ts Day33 /tmp/day33-cover.png --frame=52 --log=error </dev/null) && ffmpeg -nostdin -v error -y -i /tmp/day33-cover.png -q:v 2 "$D/${B}_Cover.jpg"
F=$(.venv/bin/python -c "import json;p=json.load(open('$P/versions/main/timeline.json'));p['cardOnly']=True;json.dump({'plan':p},open('/tmp/day33-card.json','w'));print(int((p['speechEnd']+3.5)*30))")
(cd remotion && npx remotion still src/index.ts Day33 ../$D/${B}_바깥놀이영어3문장.png --frame=$F --props=/tmp/day33-card.json --log=error </dev/null)
.venv/bin/python - "$P/versions/main/timeline.json" "$D/${B}_ko.srt" <<'PY'
import json, sys
p = json.load(open(sys.argv[1])); f = lambda t: f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
caps = sorted(p["captions"], key=lambda c: c["s"]); out = []
for i, c in enumerate(caps):
    e = min(c["e"], caps[i + 1]["s"]) if i + 1 < len(caps) else min(c["e"], p["speechEnd"])
    out.append(f"{i + 1}\n{f(max(0, c['s']))} --> {f(e)}\n{c['ko']}" + (f"\n{c['en']}" if c.get('en') else "") + "\n")
open(sys.argv[2], "w", encoding="utf8").write("\n".join(out))
PY
ls -la $D
