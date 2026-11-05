# Class video style (landscape, YouTube) — from Day 6 "Silly English"

Reference storyboard (owner's, private): https://claude.ai/artifact/UhSMW422zKPLMoipbXnroP
The Day 6 code lived in a temporary folder on the Mac and was **not** saved here. Rebuild it in this repo
(e.g. `remotion/src/BearJoyClass.tsx` + `projects/<yyyy-mm>-dayN-class/`) and commit it.

## Format
- 16:9 landscape, 4K source (export 3840×2160 or 1920×1080), like Days 1–6. Length follows the lesson (Day 6 was 5:22); do not speed up footage.
- Brand: Pretendard, pastel Butter Yellow #F6F0BA / Sky Blue #AECCE6, Ink #14203A text on light chips. Calmer pacing than Reels, because this is a class.
- Music: original lo-fi (`projects/2026-11-confidence/audio/synth_lofi.py`) with softer drums, about 16 dB under the voice. SFX: soft pop, whoosh, chime, boing for jokes, sparkle.

## Structure (Day 6)
1. **Opening:** Day N title card beside Mark for his first sentence, then it clears. Music fades in with a sparkle.
2. **Mark teaches each phrase**, one card style throughout so viewers learn where to look:
   - **Phrase card**, large and low in frame so his mouth stays visible: English / Korean pronunciation (sky-blue pill) / Korean meaning. Each English word lights up as he says it. Whoosh in.
   - **Your turn:** a yellow chip plus a bar that counts down the pause he leaves. A chime starts the pause.
   - **Stress:** the stressed part bigger and yellow (hel-LO), with the same part marked in the Korean. It pulses each time, with a very soft tap.
   - **Flow:** a curved line joins words that run together (little⌒friend).
   - **Intonation:** an arrow for a rising or falling voice, with the reason in Korean.
   - **Voice play:** text reacts to the voice (shrinks for a tiny voice; for jokes a boing, then the music stops).
   - Mark's English gets Korean captions underneath. Have a fluent speaker check them.
3. **Joy's section:** Korean captions (one yellow word), small labels kept away from worksheets, a playful card per voice (robot words jerk, sleepy words droop with 💤, singing gets a label), and a key-message card (e.g. "Don't correct pronunciation, respond to the child").
4. **Ending:** a recap card with the day's phrases (pronunciation and meaning) and "Day N+1 next", then the logo card (about 10 s), a chime and a music fade-out. Replace any dead or black screen with the recap.

## Captions
Same reading-speed rule as Reels: at most ~6 Korean characters per second and at least 1.2 s on screen. Shorten long captions if needed, and say so.

## Extras the owner wants
- A **YouTube thumbnail prompt** for ChatGPT (watercolour storybook style, Mark as a real photo using `brand/assets/mark-photo.jpg`, the bear with the straw hat, a "Day N / [title]" wooden sign). Claude can't generate the image itself. Skipped for Day 1 at the owner's request; ask each time.
- A **Korean YouTube description.**
- A **vertical Reel cut** from the class if asked (use the Reels style in BRAND.md).

## Code (rebuilt for Day 1, saved here)
- Template: `remotion/src/BearJoyClass.tsx` (composition `Day1Class`, registered in `remotion/src/Root.tsx`).
- Lesson plan: `projects/2026-11-day1-class/build_timeline.py` → `versions/main/timeline.json`. Copy this project for the next class video.
- Words behind heads: `make_mattes.sh` (about 30 s per clip with `--device coreml`). Mix: `mix.py`. Storyboard page: `storyboard/build_page.py`. Stills with one reused browser: `remotion/class-stills.mjs`.
- Renders on the Mac need `/opt/homebrew/bin` on PATH in a Claude session.

## Owner feedback from Day 1 (5 Nov 2026), the free day that sells the course
- **No cold open in the class video.** People have already pressed play, so tell them what's coming: a "오늘의 순서" card with rough times over the intro, then a 3-2-1 countdown that ends as the first phrase starts. Keep the most exciting moment for Instagram hooks.
- **Music only on the goodbye and the ending** (recap, reviews, offer, logo). The lesson itself is voice and sound effects.
- **Viewers are already on the Little Steps page**, so no QR code or link on screen. The offer card uses the page's own wording and button text ("전체 과정 열기 · ₩47,000").
- Joy's Korean translation of Mark's lines is available on request and is used word for word.
- Check the footage first for burned-in items (logo, labels, small previews) and keep cards clear of them.
