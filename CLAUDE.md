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
Remotion, HyperFrames (npm, in `remotion/`), FFmpeg, yt-dlp, numpy, and Whisper (whisper.cpp) for transcripts.

### Fresh cloud session setup (do this first, about 5 minutes)
1. `npm ci --prefix remotion` (installs Remotion, HyperFrames and the Pretendard font package)
2. `pip install yt-dlp numpy`
3. `sh remotion/fetch-fonts.sh` (TTF fonts are not committed; the Pretendard woff2 files and the emoji font list are)
4. Whisper: `git clone --depth 1 https://github.com/ggml-org/whisper.cpp /opt/tools/whisper.cpp`, then `cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build -j --target whisper-cli` inside it, then `sh ./models/download-ggml-model.sh large-v3-turbo`. Use `-l en` or `-l ko` per section; the owner may supply exact bilingual translations, so use them word for word.
5. Render Remotion with `--browser-executable=/opt/pw-browsers/chromium`.

### Running on the owner's Mac (Marks-MacBook-Pro)
- One-time setup: `bash setup-mac.sh` from this repo. It clones to `~/Video-Edit`, installs the tools, and adds a pointer to `~/.claude/CLAUDE.md`.
- Python: use `.venv/bin/python` (not `python3 -I`). Whisper is at `tools/whisper.cpp/build/bin/whisper-cli`, with its model in `tools/whisper.cpp/models/`.
- Remotion: omit `--browser-executable` (it uses its own Chrome on the Mac). HyperFrames background removal: add `--device coreml`, which is much faster than the cloud CPU.
- Footage can be read straight from `~/Downloads` or `~/Desktop/Footage For Claude`, so no Drive link is needed.

### Keeping sessions in sync
Claude sessions cannot read each other's chats. This repo is the shared memory. Start every session with `git pull` and end it with a commit and push (videos stay out of git). Record new owner feedback in `brand/BRAND.md`.

## Making a new reel (the workflow the owner approved)
1. Get the footage. Large files arrive as a Google Drive "anyone with the link" share. Download with
   `curl -L "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"` into `raw-footage/`.
2. Ask for the **day number** of the daily-posting series ("DAY N · 출간까지 매일 업로드") and whether there are Korean translations.
3. Transcribe, then copy `projects/2026-11-confidence/` as the starting point for `projects/<yyyy-mm>-<topic>/`:
   `script.txt` → `captions.json` → `build_timeline_v2.py` (cuts, pops, behind-head words, SFX) → `cut.py` → `hyperframes remove-background` for the subject matte (about 40 min for 90 s on CPU; start it early) → `audio/synth_lofi.py` → Remotion `BearJoyReelV2` → `mix.py ... timeline_v2.json -8 2.5`.
4. Show a storyboard (stills rendered from the real footage) and wait for approval before the final export.
5. Deliver an Instagram package in `exports/instagram/dayN/`: standard-range H.264 MP4 (see the Day 23 ffmpeg settings in git history), a cover JPG from the hook, and `caption.txt` (Korean, catchy, a "send to a friend" line, a follow line, 5 hashtags).

Notes: YouTube blocks cloud downloads without cookies. Instagram profiles need a login, so ask the owner for screenshots instead. Public reels can be downloaded with yt-dlp.
