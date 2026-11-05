# The Bear & Joy Co. — Reels brand rules (approved 4 Nov 2026)

## v2 reel style (owner request, 4 Nov 2026) — overrides the type, caption, pacing and music rules below for Reels
The owner found v1 "a little boring" and asked for more energy. For every Reel:
- **Fonts (updated by owner, 4 Nov 2026):** Pretendard for everything on screen. Black (900) for big words and pops, ExtraBold (800) for Korean captions, Bold (700) for English and small lines. Noto Color Emoji for flags and emoji. Playfair Display only in the logo wordmark image.
- **Colours (owner reference):** pastel Butter Yellow #F6F0BA and Sky Blue #AECCE6, alternating on key words, with white for small lines. Soft dark shadows, no hard outlines. Layout follows the owner's reference: a small white line above a big pastel line.
- **Captions:** white Pretendard with a soft shadow. Each Korean line has one butter-yellow highlight word. English words light up sky blue as they are spoken.
- **Key-point pops:** big pastel Pretendard Black words with a soft shadow and a bouncy entrance (no boxes), about every 3–5 s, with emoji and 🇬🇧 / 🇰🇷 flags where relevant. Each has a pop or boing sound.
- **Behind the head:** 2–3 big pastel Korean words per reel (Pretendard Black, small white English line above), with an impact and sparkle sound.
- **Camera:** punch zoom on every caption (100% / 108%), shake on key moments, a big punch-in for jokes.
- **Series:** "🔥 DAY N · 출간까지 매일 업로드 📚" badge, big during the hook, then docked top-right. A progress bar along the top with the bear walking along it.
- **Follow CTA (5 s end card):** logo, "DAY N ✅ · 출간까지 매일 업로드 중 📚", a big two-line "팔로우하고 / DAY N+1 같이 봐요!", and a large "＋ 팔로우" button that a 👆 taps and that flips to "팔로잉 ✓", with the Kakao button below.
- **Music:** original lo-fi hip hop, about 82 BPM, about 8 dB under the voice with light ducking. The beat stops for jokes and drops back in with a hit.
- **Look:** a brighter, punchier grade (more contrast and saturation) with light grain.
- **Caption reading speed (owner feedback, Day 23):** in Day 23 the Korean lines around "보셨죠? 정말 엉망이죠." flashed by too fast. Keep every Korean caption to at most ~6 characters per second and on screen for at least 1.2 s. Achieve that by showing it slightly before the speech, holding it into the next pause, or merging very short lines (e.g. "예를 들어볼게요." with the next line). Never speed up the footage. Check the reading-speed table before rendering.
- Template: `remotion/src/BearJoyReelV2.tsx`. Plans: `projects/*/build_timeline_v2.py`. Mix: `mix.py <version> <picture> <out> timeline_v2.json -8 2.5`.

Visual version: `brand/brand-sheet.html` (published at https://claude.ai/artifact/MU7MQRqet5eMyBhUcyqNq1).
Source of the look: bearandjoy.com. Structure adapted from a reference reel and from research on top-performing Reels.

## Logo and art (`brand/assets/`)
- `logo-full.png` — bear + butterfly + wordmark, transparent background.
- `bear-butterfly.png` — artwork only. `wordmark-navy.png` for cream backgrounds, `wordmark-cream.png` for navy backgrounds.
- Wordmark reads "The Bear & Joy Co." exactly. Never gold, never stretched, never recoloured. Art is never redrawn.
- Logo only on the end card. Optional small bear watermark at the top-left, 60% opacity.

## People
- **Mark (마크 선생님, British teacher):** always use `brand/assets/mark-photo.jpg` (owner-supplied, 5 Nov 2026), shown as `mark-avatar.png` (circle with a sky-blue and butter-yellow ring) whenever a video mentions him. Never cut his image from other footage.
- **Joy (조이 선생님):** use `brand/assets/joy-photo.png` (owner-supplied, 5 Nov 2026), shown as `joy-avatar.png`, until the owner supplies a headshot.
- **Mark and Joy together (support from both):** `brand/assets/mark-joy-photo.jpg` (owner-supplied, 5 Nov 2026).

## Colour
| Name | Hex | Use |
|---|---|---|
| Night | #1E2D4D | cards, end screen, caption shadow |
| Deep blue | #173B5C | logo/headings on cream |
| Gold | #C9A84C | one highlight word, English caption line, borders, stars |
| Cream | #F5F0E6 | all text on video |
| Parchment | #FAEEDF | light backgrounds |
| Kakao | #FEE500 | Kakao button only |

## Type
- English titles: Playfair Display (600; italic 400 for English caption lines).
- Korean titles and captions: Gowun Batang Bold.
- Small labels, prices, dates: Noto Sans KR.

## Captions
- Korean first, Gowun Batang Bold, Cream, soft Night shadow. When the line includes an English phrase, it goes below in gold Playfair italic.
- One phrase at a time (~6–10 Korean syllables). At most one gold word per caption.
- Centred, top edge at 63% of frame height, inside the safe zone (top 11.5%, bottom 20%, right 11%, left 4%).

## Hook (first 1.5–2 s)
- Small gold caps line "BEAR & JOY · LITTLE STEPS" + big English Playfair title + Korean title under it.
- Pick ONE hook type: result first, parent's worry, two kinds of parent (gentle), the unexpected, the open question (the bear who needs a name), today's phrase.
- Say it out loud and show it as on-screen text from frame 1, with motion at the same time.
- The hook must match the payoff. No clickbait.

## Cards and motion
- Night cards at 86% with a thin gold border and 24 px corners, in the top third. Book art goes on a cream mat.
- Step pill: gold outline, Playfair caps ("DAY 1 · 1일차"). Progress: a row of stars, gold when done.
- Cards fade and rise 16 px over 400 ms with a gentle ease. Book spreads change with a page turn or a 10-frame dissolve. No hard slides, glitches or bounces.
- Jump cuts alternate between 100% and 105% framing. Slow push-ins on illustrations.

## Pacing
- First useful thing by 5 s. Cut greetings and intros.
- Scene change about every 10 s. Something small moves every 2–4 s.
- Cut pauses longer than 0.4 s and repeated takes. Keep natural breaths.
- Length: 15–35 s for reach reels, 60–90 s for step-by-step guides.
- The last line loops back into the first frame. Answer any open question in the last 3 s.

## Sound
- The creator's own voice first. Soft piano, celesta or acoustic music at 70–90 BPM, about 20 dB under the voice, ducked further under speech. Royalty-free or Instagram's library only.
- Sound effects: a page turn when book art appears and a tiny chime when a star turns gold. Nothing else.
- Final mix at −14 LUFS with peaks no higher than −1 dBTP.

## Ending and caption text
- The last 5 s fade to Night. The bear and butterfly drift in, then the cream wordmark, one warm Korean line, and a Kakao pill reading "카카오톡 채널 추가하기".
- Post caption ends with a reason to share, e.g. "영어 그림책 고민하는 친구에게 보내주세요".

## Children
- Show children's faces only with their parents' consent. Hands, books and the back of a head tell the story just as well.

## Export
- 1080×1920, 30 fps, H.264, about 12 Mbps, AAC 48 kHz. Captions burned in, plus Korean and English .srt files.

## Process
- Always show a storyboard for approval before exporting.

## Class video feedback (owner, 5 Nov 2026)
See "Owner feedback from Day 1" in `docs/class-video-style.md`: a plan card and countdown instead of a cold open, music only on the ending, and no QR code or link on screen.

## Music source (owner, 5 Nov 2026) — overrides "original lo-fi" above and in docs/class-video-style.md
Do not generate music (`synth_lofi.py` is for sound effects only from now on). The owner found the generated music not good enough. Find real licensed tracks, keep each track's source and licence with the project, and let the owner choose by ear, because Claude cannot hear them.

## Little Steps welcome film (owner, 5 Nov 2026)
"Day 0" is an internal name only. On screen and in public it is **Little Steps to Big Adventures**. Keep words well away from the frame edges (at least 64 px at the sides and 40 px at the top of a 1920×1080 frame).
Backgrounds: the owner's watercolour Oxford and Seoul paintings (`brand/assets/art-river.jpg`, `art-both.jpg`, `art-lawn.jpg`), with slow moving clouds kept in the sky over them.
No logo in the top-left of this film (owner, 5 Nov 2026): the version cut from their end card clipped the bear's head. The owner's animated logo closes the video.
