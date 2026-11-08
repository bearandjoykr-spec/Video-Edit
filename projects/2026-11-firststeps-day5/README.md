# First Steps · Day 5 — landscape class video (YouTube)

Status (8 Nov 2026): template ready, waiting for footage and scripts from the owner.

- Template: `remotion/src/BearJoyClass.tsx` (composition `Day5ClassDemo` = layout preview on a placeholder background).
- `spec-demo.json` → `python3 build_class.py spec-demo.json versions/demo` → `versions/demo/timeline_class.json`.
- Event types: `title`, `phrase` (words with times, `pron`, `ko`, `stress[{word, part, pron, pulses}]`, `flow[[i, i+1]]`,
  `tone{dir, at, why}`, `voice{kind: tiny|big}`, `note`), `yourturn`, `label`, `avatar` (Mark's photo), `voice` (Joy:
  robot | sleepy | sing | tiny | big | joke), `message`, `recap`, `logo`. Captions: `{s, e, ko, hi, en?, speaker}`.
- Pipeline for the real footage: transcribe (whisper.cpp large-v3-turbo, `-l en` for Mark, `-l ko` for Joy, owner text
  used word for word) → cut.py (copy from `projects/2026-11-confidence/`) → `spec.json` → `build_class.py` →
  `audio/synth_lofi.py` with softer drums → render → `mix.py <v> <picture> <out> timeline_class.json -16 3`.
- Before export: storyboard of stills from the real footage + a short sample, wait for the owner's OK.
