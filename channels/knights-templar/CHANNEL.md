# Knights Templar channel (YouTube @weareknightstemplar)

Started 23 Nov 2026. Not a Bear & Joy channel: do not use brand/BRAND.md or its assets.

## What the owner told us (23 Nov 2026)
- Faceless videos: the owner's own audio of him reading the Bible, part by part.
- Visuals: beautiful, Knights Templar style.

## Series
- Reads the whole Bible (KJV) start to finish, 10–15 min episodes (~850 in total). One playlist per book + a master playlist.
- Each episode: Opening + prayer (Non nobis, Domine — Psalm 115), Context, The reading, Analysis, For the brothers, Closing + benediction (Numbers 6:24–26).
- Scripts are written with the owner in Claude docs, then copied to projects/<yyyy-mm>-templar-epNN-<book>/script.md.
- Episode 1: Genesis 1:1–2:3 — projects/2026-11-templar-ep01-genesis1/

## Look (owner, 23 Nov 2026)
- Dark, sanctified, simple.
- Reading: we look at an open Bible page; each word highlights as Mark says it (word-level Whisper timing).
- Teaching (Analysis, For the brothers): notes appear for the brothers to take to heart.
- Opening prayer: the whole prayer shown beautifully, with a prompt for the brothers to take a knee.
- Fonts: Cinzel (titles), EB Garamond (scripture, notes), UnifrakturMaguntia (drop caps) in remotion/public/templar/fonts.

## Sound (owner, 23 Nov 2026)
- Mood: dark, masculine, battle-worn — a camp by the fire before going to war. Gritty, powerful.
- Voice: the fuller chain in projects/2026-11-templar-ep01-genesis1/mix.sh (VOICE_FX) is APPROVED ("2nd version is better").
- Subtle SFX only (page turns, book open/close, fire); never over the voice.
- Owner supplies real fire SFX and music; synthesised fire/music were not good enough.
  Ep 1 uses: bed "Landscape KT" (owner's), chant from the owner's video (owner says cleared to use),
  fire "soundreality fire ambience". Files live in raw-footage/templar-ep01/ (not in git).
- Chant only where Mark is silent: title, a 5 s swell after "The Word of the Lord", end card.
- Mix: projects/2026-11-templar-ep01-genesis1/mix.py (bed -31, chant -20, fire -35 LUFS; voice -16; final -14).

## Waiting on the owner
- The audio file (Google Drive, anyone with the link), which book/chapters, which Bible translation
- Look and feel (reference channels/videos), language(s), rough length
- Logo/brand set-up? Thumbnail prompt? YouTube title/description?

## Rules that apply
- Storyboard (stills from the real footage) + short sample before final export; wait for OK.
- Final export: standard-range BT.709 H.264, AAC 48 kHz, about -14 LUFS.
- Also a ~8 Mbps 1080p copy (chat limit 400 MB).
- Render long videos in parts (background jobs stop after 30 min unless given a longer timeout).
