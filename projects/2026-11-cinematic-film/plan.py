"""Plan v4 — "Born in Oxford · Built in Seoul". Bear & Joy brand film, told like our read-aloud (Joy approved v4, 18 Nov 2026).

Mark (M. Foster) narrates in English like a bedtime story, Korean subtitles under him. Real footage only (Joy: no AI-made pictures, no story cards): Joy's Oxford and Seoul footage, real places from
Pexels, and our real printed book on Oxford stone. Solo piano. Small storybook type. Earlier plans (trailer v2, travel v3) are in git history.

Narration timings are placeholders until Mark's recording arrives; then each 'voice' line is snapped to his take.

Shot: (start s, clip, in-point s, look, fx, fy, zoom-from, zoom-to, speed, note)
  clip: 'a:file' project art (art/), 'cNN'/'jN' Joy's footage, 'p:ID' Pexels, 'black', 'endcard'
  look '+fit' = whole artwork on a cream page.
"""
END = 84.0
MUSIC = 'piano-inspiring-moment-611638.mp3'   # gentle solo piano under a voice; Joy chooses by ear
FLASHES = []
LETTERBOX = False

# Small hand-drawn Bear and Joy (Joy's own art, overlay/bear.png & butterfly.png), used sparingly (3 moments).
# (start, end, png, centre-x, bottom-y, height as share of frame: 16:9, 9:16)
OVERLAYS = [
    # (start, end, png, (cx, bottom, height) for 16:9, (cx, bottom, height) for 9:16) — shares of the frame
    (0.6,  5.0,  'bear.png',      (0.20, 0.86, 0.26), (0.26, 0.86, 0.13)),   # the bear sits beside his real book
    (42.4, 46.6, 'butterfly.png', (0.80, 0.48, 0.36), (0.74, 0.50, 0.17)),   # Joy flutters over the title
    (71.8, 75.9, 'butterfly.png', (0.62, 0.34, 0.30), (0.46, 0.74, 0.17)),   # Joy comes to rest by the book
]

SHOTS = [
    # Joy, 18 Nov 2026: no AI-made pictures and no story cards. Real footage and the real printed book only.
    # 1. Are you sitting comfortably? — our real book, on Oxford stone ---------------------------
    (0.0,  'j6',          5.0,  'soft', 0.45, 0.80, 1.10, 1.02, 0.6, 'our printed book on Oxford stone, close'),
    # 2. BORN IN OXFORD -------------------------------------------------------------------------
    (5.0,  'c06',         5.0,  'soft', 0.55, 0.62, 1.00, 1.06, 0.8, 'Oxford rooftops (Joy)'),
    (9.0,  'c07',         1.0,  'soft', 0.50, 0.55, 1.00, 1.05, 0.8, 'Radcliffe Camera, people crossing (Joy)'),
    (13.0, 'c11',         2.0,  'soft', 0.50, 0.45, 1.00, 1.05, 0.8, 'under the Bridge of Sighs (Joy)'),
    (17.0, 'c21',         1.0,  'soft', 0.45, 0.55, 1.00, 1.05, 0.9, 'flags over the Randolph (Joy)'),
    (19.5, 'c12',         1.0,  'soft', 0.45, 0.45, 1.00, 1.08, 0.8, 'butterfly mural (Joy)'),
    (22.5, 'p:15614364',  12.0, 'soft', 0.50, 0.40, 1.00, 1.04, 0.8, 'a plane lifts off'),
    # 3. BUILT IN SEOUL -------------------------------------------------------------------------
    (26.0, 'p:30975008',  10.0, 'soft', 0.50, 0.40, 1.00, 1.06, 1.0, 'N Seoul Tower on Namsan'),
    (29.5, 'p:29354411',  1.0,  'soft', 0.50, 0.50, 1.00, 1.05, 0.8, 'a Seoul street'),
    (33.0, 'c04',         0.5,  'soft', 0.48, 0.70, 1.08, 1.00, 0.8, 'red Joseon robe under autumn maples (Joy)'),
    (36.0, 'c22',         3.0,  'soft', 0.50, 0.55, 1.00, 1.06, 0.7, 'hanbok crowd through the palace gate (Joy)'),
    (39.0, 'c20',         30.0, 'soft', 0.50, 0.55, 1.00, 1.05, 0.8, 'drum dance at the palace (Joy)'),
    (42.0, 'c13',         8.0,  'soft', 0.45, 0.40, 1.00, 1.06, 0.8, 'TITLE over the king at night (Joy)'),
    # 4. THE JOURNEY: 24 stories, 12 places — real places --------------------------------------
    (47.0, 'p:7197893',   4.0,  'soft', 0.50, 0.55, 1.00, 1.05, 1.0, 'Paris'),
    (49.0, 'p:29622798',  3.0,  'soft', 0.50, 0.55, 1.00, 1.05, 1.0, 'Cairo'),
    (51.0, 'p:14908997',  3.0,  'soft', 0.50, 0.55, 1.00, 1.05, 1.0, 'Kenya'),
    (53.0, 'p:15785118',  8.0,  'soft', 0.50, 0.55, 1.00, 1.05, 1.0, 'Hoi An'),
    (55.0, 'c09',         0.5,  'soft', 0.40, 0.55, 1.00, 1.04, 1.0, 'Sydney (Joy)'),
    # 5. WHY — our real book only (Joy: no stock shots that show other publishers' books) -----------
    (57.0, 'd34n1',       1.0,  'soft', 0.50, 0.55, 1.00, 1.05, 0.8, 'our book carried through Oxford (DAY 34 shoot)'),
    (61.0, 'p:8441312',   3.0,  'soft', 0.50, 0.45, 1.00, 1.04, 0.9, 'children from many countries, arm in arm'),
    (64.5, 'd34n3',       0.5,  'soft', 0.50, 0.45, 1.00, 1.06, 0.8, 'our book on an Oxford street post (DAY 34 shoot)'),
    # 6. THE NAME -------------------------------------------------------------------------------
    (68.0, 'j6',          2.0,  'soft', 0.45, 0.30, 1.00, 1.04, 0.7, 'Radcliffe Camera, tilt down to...'),
    (71.5, 'j6',          4.5,  'soft', 0.45, 0.80, 1.00, 1.08, 0.7, '...our book on Oxford stone'),
    (76.0, 'endcard',     0.0,  'soft', 0.5, 0.5, 1, 1, 1, 'end card'),
]

# (start, end, Korean, English, style)  'voice' = Mark's narration (EN heard, KO under it)
LINES = [
    (0.8,  4.6,  '편안하게 앉으셨나요? 그럼, 시작해 볼까요.',            'Are you sitting comfortably? Then we’ll begin.',              'voice'),
    (5.4,  9.0,  '옛날 옛적, 옥스퍼드라는 아름다운 도시에',              'Once upon a time, in a lovely city called Oxford,',            'voice'),
    (9.4,  12.8, '이름 없는 작은 곰 한 마리가 살았어요.',                 'there lived a small bear with no name.',                       'voice'),
    (13.4, 18.6, '어느 날 아침, 곰은 문을 열고 밖으로 한 걸음 나섰어요.', 'One morning, he opened the door… and stepped outside.',        'voice'),
    (19.4, 25.6, '그 작은 한 걸음이, 큰 모험의 시작이었어요.',            'Just one small step. It was the first step of a big adventure.', 'voice'),
    (26.4, 32.6, '그 모험은 세상을 건너… 멀리 서울까지 이어졌어요.',      'And that adventure carried him across the world… all the way to Seoul,', 'voice'),
    (33.4, 41.4, '그곳에서, 아이들이 곰을 기다리고 있었어요.',           'where children were waiting to meet him.',                     'voice'),
    (42.6, 46.6, 'Born in Oxford · Built in Seoul',                       '',                                                             'tagline'),
    (47.4, 52.8, '스물네 권의 이야기, 세계 열두 도시.',                   'Twenty-four stories. Twelve places in the world.',             'voice'),
    (53.0, 56.8, '자기 이름을 찾아 떠나는, 작은 곰 한 마리.',             'One little bear, looking for his name.',                       'voice'),
    (57.4, 64.2, '영어는 외우는 게 아니라, 아름다운 이야기와',            'Children should meet English through beautiful stories,',      'voice'),
    (64.4, 67.8, '사랑하는 사람을 통해 만나는 거예요.',                   '…and the people they love.',                                   'voice'),
    (68.4, 75.6, '그리고 이야기의 끝에서, 곰에게 이름을 지어주는 건… 바로 우리 아이예요.', 'And at the very end… it’s your child who gives him his name.', 'voice'),
]
