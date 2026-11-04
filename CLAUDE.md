# Video editing for The Bear & Joy Co.

Claude acts as the video editor for The Bear & Joy Co. (bearandjoy.com), a bilingual Korean–English picture-book brand.

## Always
- Follow `brand/BRAND.md` on every edit. It was approved by the owner on 4 Nov 2026. Change it only when the owner asks, and update `brand/brand-sheet.html` to match.
- Use the logo and artwork in `brand/assets/` as drawn.
- Show a storyboard for approval before every export.

## Folders
- `references/` — downloaded reference reels (video files are git-ignored).
- `remotion/` — Remotion project (titles, animation). `hf/` — HyperFrames projects.
- Put renders in `remotion/out/` or `renders/` (git-ignored).

## Tools
Remotion, HyperFrames (npm, in `remotion/`), FFmpeg, yt-dlp (`pip install yt-dlp`) and Whisper (whisper.cpp) for captions.
In a fresh cloud session, reinstall with `npm ci --prefix remotion` and `pip install yt-dlp`. Render Remotion with `--browser-executable=/opt/pw-browsers/chromium`.
YouTube blocks cloud downloads without cookies. Instagram works for public reels.
