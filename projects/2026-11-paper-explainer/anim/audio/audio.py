# Sound effects for the paper pop-up book. Music is a real licensed piano track mixed in by mix_music.sh (BRAND.md: no generated music). Every cue comes from src/beats.json.
# usage: ./py audio/audio.py build/audio.wav
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audiolib import *

B = beats(); cue = B['cues']; D = B['duration']; TURN = B['turns']
mx = Mix(D)
mx.bed(0, D, room, 0.35, fi=0.6, fo=1.0)                       # a quiet room

def page_turn(t):                                                # paper lifts, swishes over, lands
    mx.sfx(t, rustle(0.5, 0.55), 1, -0.2, 0.15); mx.sfx(t + 0.15, whoosh(0.7, False, 0.35), 1, 0.1, 0.2)
    mx.sfx(t + 0.75, thud(0.18, 90, 0.35), 1, 0, 0.1)
def fold_up(t, g=1.0, pan=0.0):                                  # a pop-up piece unfolds: small paper flick + soft pop
    mx.sfx(t, rustle(0.18, 0.35 * g), 1, pan, 0.1); mx.sfx(t + 0.12, pop(0.45 * g), 1, pan, 0.15)

for a, b in TURN: page_turn(a)
fold_up(TURN[0][1] + 0.15, 1.1)                                  # you and your child
for k in ['friend', 'flowers', 'read-book', 'read-pair', 'read-bear', 'practise-pair', 'practise-card', 'park-tree', 'park', 'park-friends',
          'dinner', 'bed', 'fun-pair', 'fun-tablet', 'mark', 'joy', 'cta-book', 'cta-bear']:
    fold_up(cue[k], 1.0, rng.uniform(-0.4, 0.4))
for i in range(3): fold_up(cue['starters'] + i * 0.4, 1.0, (i - 1) * 0.4)   # conversation-starter cards
mx.sfx(cue['worry'], boing(150, 0.25, 0.4), 1, -0.2, 0.2)        # the worry cloud
for i in range(3): mx.sfx(cue['bear-in'] + i * 0.37, boing(210 + 30 * i, 0.4, 0.35), 1, 0.4, 0.1)   # the bear hops in
for i in range(2): mx.sfx(cue['starters'] + 1.6 + i * 0.45, boing(230 + 30 * i, 0.3, 0.3), 1, 0.4, 0.1)
mx.sfx(cue['bear-in'] + 1.2, shimmer(1.2, 0.3), 1, 0.2, 0.3)
mx.sfx(cue['flowers'] + 0.4, shimmer(1.0, 0.22), 1, 0, 0.3)
for i in range(6): mx.sfx(cue['practise-circle'] + i * 0.15, bp(noise(0.12), 2000, 6000) * np.exp(-tt(0.12) * 20) * 0.25, 1, 0.2)  # pencil circle
mx.sfx(cue['aha'], bell(mf(88), 1.8), 0.35); mx.sfx(cue['aha'] + 0.1, shimmer(1.0, 0.35), 1, 0, 0.3)   # aha!
mx.sfx(47.9, shimmer(1.2, 0.3), 1, 0, 0.3); mx.sfx(cue['cta-comment'] + 0.15, shimmer(1.2, 0.3), 1, 0, 0.3)  # confetti
mx.sfx(cue['fun-joy-screen'], click(0.4), 1, 0)
for r in B['talks']: mx.sfx(r[2], pop(0.35), 1, -0.3 if r[1] == 'adult' else 0.3, 0.2)   # speech bubbles
mx.sfx(cue['cta-comment'], bell(mf(84), 2.5), 0.35); mx.sfx(cue['cta-comment'] + 0.1, bell(mf(91), 2.5), 0.25)
mx.write(sys.argv[1] if len(sys.argv) > 1 else 'build/audio.wav', fade_out=0.8)
