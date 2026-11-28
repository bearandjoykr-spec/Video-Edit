#!/bin/bash
# DAY 42 Instagram package: MP4 (DAY 37 settings), cover (full bookcase), Korean srt, caption, the book-list image. Run from the repo root.
set -e; export PATH=/opt/homebrew/bin:$PATH
P=projects/2026-11-day42-bookshelf; D=exports/instagram/day42; B=BearJoy_Day42; mkdir -p $D
ffmpeg -nostdin -v error -y -i renders/day42/final-42.mp4 -c:v libx264 -preset slow -profile:v high -level 4.1 -b:v 9M -maxrate 12M -bufsize 18M -pix_fmt yuv420p \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$D/$B.mp4"
(cd remotion && npx remotion still src/index.ts Day42 /tmp/day42-cover.png --frame=360 --log=error </dev/null) && ffmpeg -nostdin -v error -y -i /tmp/day42-cover.png -q:v 2 "$D/${B}_Cover.jpg"
cat > "$D/${B}_ko.srt" <<'SRT'
1
00:00:00,000 --> 00:00:06,000
안녕하세요, 서울에 사는 영국 선생님 마크예요.

2
00:00:06,000 --> 00:00:10,150
제가 어릴 때 가장 좋아했던 그림책들이에요.

3
00:00:10,150 --> 00:00:12,400
꼭 저장해 두세요! 📌

4
00:00:12,400 --> 00:00:15,200
책 목록이 필요하면 댓글에 '그림책' 남겨 주세요
SRT
cp $P/caption.txt "$D/caption.txt"; cp raw-footage/day42/books.webp "$D/댓글_책목록.webp"; ls -la $D
