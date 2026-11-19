"""Plan v5 — "Born in Oxford · Built in Seoul". Bear & Joy brand film, narrated by Mark (script approved by Joy).

v5 (Mark + Joy, 19 Nov 2026, after the v4 preview: "I like it but not love it… the concept is wow"):
- the words change when the scene changes: every subtitle belongs to exactly one shot (approved lines split at
  natural pauses, wording unchanged);
- a tighter edit: every cut lands on a beat of the piano track (~92 BPM, 0.69 s), 2–6 beats per shot;
- cute kids playing and reading (Pexels, no other publishers' books visible);
- a punchier grade and stronger push-ins (look 'vivid').
Real footage and our real printed books only (no AI art, no story cards). Earlier plans are in git history.
When Mark's recording arrives, re-time SEQ beats to his takes.

SEQ row: (beats, clip, in-point s, fx, fy, zoom-from, zoom-to, speed, Korean, English)
  clip: 'cNN'/'jN'/'d34nN' Joy's footage (prep/), 'p:ID' Pexels, 'endcard'. Empty text = no subtitle.
"""
import os

MUSIC = 'piano-inspiring-moment-611638.mp3'   # Pixabay "Inspiring Moment" (solo piano)
FLASHES = []
LETTERBOX = False
LOOK = 'vivid'
SUB_FADE = (0.18, 0.12, 0)                    # fade in, fade out, rise px: crisp, so words change with the cut

SEQ = [
    # 1. Are you sitting comfortably? -------------------------------------------------------------
    (4, 'j6',          5.0, 0.45, 0.80, 1.12, 1.02, 0.6, '편안하게 앉으셨나요?', 'Are you sitting comfortably?'),
    (4, 'p:8498360',   2.0, 0.50, 0.40, 1.00, 1.10, 0.8, '그럼, 시작해 볼까요.', 'Then we’ll begin.'),
    # 2. BORN IN OXFORD ---------------------------------------------------------------------------
    (4, 'c06',         5.0, 0.55, 0.62, 1.00, 1.12, 0.9, '옛날 옛적,', 'Once upon a time,'),
    (4, 'c07',         1.0, 0.50, 0.55, 1.10, 1.00, 0.9, '옥스퍼드라는 아름다운 도시에', 'in a lovely city called Oxford,'),
    (5, 'd34n4',       4.0, 0.50, 0.55, 1.08, 1.00, 0.7, '이름 없는 작은 곰 한 마리가 살았어요.', 'there lived a small bear with no name.'),
    (4, 'c11',         2.0, 0.50, 0.45, 1.00, 1.10, 0.9, '어느 날 아침, 곰은 문을 열고', 'One morning, he opened the door…'),
    (4, 'p:10981043',  6.0, 0.50, 0.55, 1.00, 1.10, 0.9, '밖으로 한 걸음 나섰어요.', '…and stepped outside.'),
    (3, 'c12',         1.0, 0.45, 0.45, 1.00, 1.12, 0.9, '그 작은 한 걸음이,', 'Just one small step.'),
    (4, 'p:15614364',  12.0, 0.50, 0.40, 1.00, 1.08, 0.9, '큰 모험의 시작이었어요.', 'It was the first step of a big adventure.'),
    # 3. BUILT IN SEOUL ---------------------------------------------------------------------------
    (4, 'p:31474610',  1.0, 0.40, 0.50, 1.00, 1.10, 1.0, '그 모험은 세상을 건너…', 'And that adventure carried him across the world…'),
    (4, 'p:40834925',  1.0, 0.50, 0.50, 1.10, 1.00, 1.0, '멀리 서울까지 이어졌어요.', '…all the way to Seoul,'),
    (6, 'p:8342700',   1.0, 0.68, 0.45, 1.00, 1.08, 0.9, '그곳에서, 아이들이 곰을 기다리고 있었어요.', 'where children were waiting to meet him.'),
    (2, 'c20',         30.0, 0.50, 0.55, 1.05, 1.12, 1.0, '', ''),
    (2, 'c22',         3.0, 0.50, 0.55, 1.05, 1.12, 1.0, '', ''),
    (5, 'c13',         8.0, 0.45, 0.40, 1.00, 1.10, 0.8, 'Born in Oxford · Built in Seoul', '§tagline'),
    # 4. THE JOURNEY ------------------------------------------------------------------------------
    (3, 'p:7197893',   4.0, 0.50, 0.55, 1.00, 1.10, 1.0, '스물네 권의 이야기,', 'Twenty-four stories.'),
    (3, 'p:29622798',  3.0, 0.50, 0.55, 1.10, 1.00, 1.0, '세계 열두 도시.', 'Twelve places in the world.'),
    (2, 'p:14908997',  3.0, 0.50, 0.55, 1.00, 1.10, 1.0, '', ''),
    (2, 'p:15785118',  8.0, 0.50, 0.55, 1.10, 1.00, 1.0, '', ''),
    (2, 'c09',         0.5, 0.40, 0.55, 1.00, 1.10, 1.0, '', ''),
    (6, 'd34n1',       0.5, 0.50, 0.55, 1.00, 1.08, 0.9, '자기 이름을 찾아 떠나는, 작은 곰 한 마리.', 'One little bear, looking for his name.'),
    # 5. WHY — kids, and our book -------------------------------------------------------------------
    (4, 'p:27118848',  5.0, 0.50, 0.60, 1.00, 1.08, 0.9, '영어는 외우는 게 아니라,', 'Children should meet English'),
    (4, 'd34n5',       0.3, 0.50, 0.55, 1.00, 1.06, 0.7, '아름다운 이야기와', 'through beautiful stories,'),
    (2, 'p:8426407',   2.0, 0.30, 0.50, 1.00, 1.08, 1.0, '', ''),
    (2, 'p:8384707',   2.0, 0.50, 0.50, 1.08, 1.00, 1.0, '', ''),
    (5, 'p:8441312',   3.0, 0.50, 0.45, 1.00, 1.06, 0.9, '사랑하는 사람을 통해 만나는 거예요.', '…and the people they love.'),
    # 6. THE NAME ---------------------------------------------------------------------------------
    (4, 'j6',          2.0, 0.45, 0.30, 1.00, 1.04, 0.7, '그리고 이야기의 끝에서,', 'And at the very end…'),
    (6, 'j6',          4.5, 0.45, 0.80, 1.00, 1.10, 0.7, '곰에게 이름을 지어주는 건… 바로 우리 아이예요.', 'it’s your child who gives him his name.'),
    (10, 'endcard',    0.0, 0.5, 0.5, 1, 1, 1, '', ''),
]

# ---- beat grid from the music (librosa, cached) -> SHOTS / LINES / OVERLAYS / END -------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_CACHE = f'{_HERE}/music/beats-{MUSIC}.txt'


def _beats():
    if os.path.exists(_CACHE):
        return [float(x) for x in open(_CACHE).read().split()]
    import librosa
    y, sr = librosa.load(f'{_HERE}/music/{MUSIC}', sr=22050)
    _, b = librosa.beat.beat_track(y=y, sr=sr, units='time')
    open(_CACHE, 'w').write(' '.join(f'{t:.3f}' for t in b))
    return list(b)


_B = _beats()
_cuts, _k = [0.0], 0
for row in SEQ:
    _k += row[0]
    _cuts.append(round(_B[_k] if _k < len(_B) else _cuts[-1] + row[0] * 0.69, 3))
END = _cuts[-1]

SHOTS, LINES, OVERLAYS = [], [], []
for i, (beats, clip, tin, fx, fy, z0, z1, sp, ko, en) in enumerate(SEQ):
    s, e = _cuts[i], _cuts[i + 1]
    SHOTS.append((s, clip, tin, LOOK, fx, fy, z0, z1, sp, f'{clip} {ko or en}'.strip()))
    if ko:
        LINES.append((round(s + 0.10, 2), round(e - 0.06, 2), ko, '' if en == '§tagline' else en,
                      'tagline' if en == '§tagline' else 'voice'))
    if i == 0:
        OVERLAYS.append((s + 0.4, e - 0.05, 'bear.png', (0.20, 0.86, 0.26), (0.26, 0.86, 0.13)))
    if en == '§tagline':
        OVERLAYS.append((s + 0.3, e - 0.05, 'butterfly.png', (0.80, 0.48, 0.36), (0.74, 0.50, 0.17)))
    if 'gives him his name' in en:
        OVERLAYS.append((s + 0.6, e - 0.05, 'butterfly.png', (0.62, 0.34, 0.30), (0.46, 0.74, 0.17)))
