# "Once upon a time" — Bear & Joy paper pop-up explainer (owner, 24 Nov 2026)
60 s, vertical 1080×1920, 24 fps. Built with the animation skill (`.claude/skills/animation/`).

Rebuild (repo root, then `anim/`):
1. Put the owner's proofs in `source/` (`walkbook-one-proof.pdf`, `book1-review.pdf`; git-ignored).
2. `python3 projects/2026-11-paper-explainer/extract.py` (pages + site images → `remotion/public/paper/`)
3. `python3 projects/2026-11-paper-explainer/anim/prep_art.py` and `anim/cutouts.py` (covers, site images and cut-outs → `anim/src/assets/art/`)
4. In `anim/`: `cp ../../../remotion/public/fonts/{Gaegu-Bold,PatrickHand,NanumBrushScript,GowunBatang-Bold}.ttf src/assets/` (after `sh remotion/fetch-fonts.sh`), `npm install`, `./py audio/audio.py build/audio.wav`, `node build.mjs`, `node render.mjs` (stills: `--stills 4.5,24,45`).

Timings and all words on screen: `anim/src/beats.json`. Scenes: `anim/src/story.js`. Paper drawing + families: `anim/src/paper.js`.
Sound: `anim/mix_music.sh` (paper effects from `audio/audio.py` + the licensed piano in `music/`, see `music/SOURCE.md`).
