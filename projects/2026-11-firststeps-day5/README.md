# First Steps · Day 5 — landscape class video (YouTube)

Status (8 Nov 2026): storyboard + sample approved by the owner; full render exported to `exports/youtube/day5/`.

Owner decisions (8 Nov 2026):
- No script supplied: Claude wrote the plan from the Whisper transcript. Mark's Korean captions (Claude's translation),
  Joy's corrected captions and the four condensed lines were approved as shown. Pronunciations approved.
- The source footage is mirrored (worksheet text reads backwards) with the logo burned in after the flip: leave as is.
- The source already has music under Mark's section; the lo-fi bed plays only under Joy and the end cards.
- Mark's cards sit mid-right (his mouth is low in frame, near the mic), not low in frame.
- Render: `npx remotion render src/index.ts Day5Class out/day5/full.mp4 --crf=16`, then
  `python3 mix_class.py main ../../remotion/out/day5/full.mp4 <out.mp4> -12`.

- Template: `remotion/src/BearJoyClass.tsx` (composition `Day5ClassDemo` = layout preview on a placeholder background).
- `spec-demo.json` → `python3 build_class.py spec-demo.json versions/demo` → `versions/demo/timeline_class.json`.
- Event types: `title`, `phrase` (words with times, `pron`, `ko`, `stress[{word, part, pron, pulses}]`, `flow[[i, i+1]]`,
  `tone{dir, at, why}`, `voice{kind: tiny|big}`, `note`), `yourturn`, `label`, `avatar` (Mark's photo), `voice` (Joy:
  robot | sleepy | sing | tiny | big | joke), `message`, `recap`, `logo`. Captions: `{s, e, ko, hi, en?, speaker}`.
- Pipeline for the real footage: transcribe (whisper.cpp large-v3-turbo, `-l en` for Mark, `-l ko` for Joy, owner text
  used word for word) → cut.py (copy from `projects/2026-11-confidence/`) → `spec.json` → `build_class.py` →
  `audio/synth_lofi.py` with softer drums → render → `mix.py <v> <picture> <out> timeline_class.json -16 3`.
- Before export: storyboard of stills from the real footage + a short sample, wait for the owner's OK.
