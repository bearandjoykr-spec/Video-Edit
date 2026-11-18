"""Shot plan v2 — "한 마디의 문" / One phrase opens a door. Bear & Joy cinematic film.

v2 (Joy, 18 Nov 2026): follow the reference reel's grammar more closely (B/W archival cold open with big
statement type, colour break, place supers, fast world montage, title over the two flags, black end card).
Joy's own shots of herself are out (also the hanbok close-up j5: "too much of my face"); the film ends on our picture book in Oxford (j6). Use only the
footage that earns its place; fill with Pexels/Pixabay stock.

One edit, two frames: 16:9 website film (2.39:1 letterbox) and 9:16 Instagram cut.
Timing follows Pixabay "Epic Hollywood Trailer" (Good_B_Music, id 9489): quiet hits 2 / 9.5 s, silence ~19-21 s,
rising hits 21.5/30/37/45/49/53.5 s, climax 53.5-89 s, drop 89.5 s, slam 94.5 s, hits 99/101 s, outro 108-118 s.

Shot: (start s, clip, in-point s, look, fx, fy, zoom-from, zoom-to, speed, note)
  clip: 'cNN' Joy's first batch (prep/cNN.mov), 'jN' Joy's second batch (prep/jN.mov),
        'p:ID' Pexels (pexels/ID.mp4), 's:name' Pixabay (stock/name.mp4), 'black', 'endcard'
  fx, fy: focus point (0-1) for the crop; speed < 1 = slow motion.
"""
END = 118.0

SHOTS = [
    # ACT 1 — PAST, black and white ------------------------------------------------------------
    (0.0,  'black',        0.0,  'past',    0.5, 0.5, 1, 1, 1, 'black, wind'),
    (2.0,  'p:40352276',   2.0,  'past',    0.62, 0.40, 1.10, 1.25, 0.5, 'palace guard, close (B/W)'),
    (5.5,  'p:6752415',    6.0,  'past',    0.45, 0.60, 1.05, 1.15, 0.6, 'letter written by candlelight'),
    (7.5,  'p:2123151',    8.0,  'past',    0.55, 0.50, 1.00, 1.10, 0.7, 'old ship in harbour'),
    (9.5,  'p:2536815',    30.0, 'past',    0.55, 0.45, 1.00, 1.08, 0.7, 'steam train crosses a bridge'),
    (12.5, 'p:34162953',   2.0,  'past',    0.50, 0.55, 1.00, 1.10, 0.6, 'crowded street'),
    (15.0, 'c22',          3.0,  'past',    0.50, 0.55, 1.00, 1.12, 0.5, 'hanbok crowd climbs through the palace gate'),
    (19.0, 'p:31938875',   10.0, 'past',    0.50, 0.50, 1.00, 1.00, 1.0, 'film burn into colour'),
    # ACT 2 — PRESENT, colour on the 21.5 s hit -----------------------------------------------
    (21.5, 'p:29240315',   2.0,  'present', 0.45, 0.55, 1.00, 1.08, 0.8, 'royal guard ceremony, drum (Seoul)'),
    (24.0, 'c04',          0.5,  'present', 0.48, 0.70, 1.15, 1.02, 0.8, 'red Joseon robe under autumn maples'),
    (26.5, 'p:29242638',   3.0,  'present', 0.40, 0.45, 1.00, 1.10, 0.6, 'guard and yellow banners, close'),
    (28.0, 'c13',          8.0,  'night',   0.45, 0.40, 1.00, 1.08, 0.8, 'king in dragon robe, night'),
    (30.0, 'p:15614364',   12.0, 'present', 0.50, 0.40, 1.00, 1.05, 0.8, 'plane lifts off'),
    (32.5, 'p:4396425',    12.0, 'present', 0.50, 0.50, 1.00, 1.05, 1.0, 'wing over English fields'),
    (34.0, 'p:7197886',    4.0,  'present', 0.50, 0.50, 1.00, 1.06, 1.0, 'Tower Bridge'),
    (36.0, 'c16',          2.0,  'present', 0.50, 0.70, 1.00, 1.06, 0.7, 'Household Cavalry on The Mall'),
    (37.0, 'p:3150358',    3.0,  'present', 0.40, 0.45, 1.00, 1.08, 0.7, 'Union Jack'),
    (39.0, 'p:12156230',   20.0, 'present', 0.50, 0.45, 1.00, 1.06, 1.0, 'Big Ben'),
    (41.0, 'c06',          5.0,  'present', 0.55, 0.62, 1.00, 1.08, 1.0, 'Oxford rooftops to the Radcliffe Camera'),
    (43.5, 'c11',          2.0,  'present', 0.50, 0.45, 1.00, 1.05, 0.8, 'under the Bridge of Sighs'),
    (45.0, 'p:35081001',   3.0,  'present', 0.55, 0.50, 1.00, 1.12, 0.6, 'a door opens onto sunlight'),
    (49.0, 'j1',           2.0,  'present', 0.50, 0.42, 1.00, 1.08, 0.7, 'Margam Castle under big clouds, Wales'),
    (51.0, 'p:10981043',   6.0,  'present', 0.50, 0.55, 1.00, 1.06, 0.8, 'a child runs down a path'),
    # ACT 3 — CLIMAX MONTAGE 53.5-89 s -------------------------------------------------------
    (53.5, 'p:18662635',   1.0,  'night',   0.50, 0.50, 1.00, 1.06, 1.0, 'Tokyo crossing at night'),
    (55.0, 'c08',          0.5,  'night',   0.55, 0.30, 1.00, 1.10, 1.0, 'Tokyo Tower'),
    (56.5, 'c09',          0.5,  'present', 0.40, 0.55, 1.00, 1.05, 1.0, 'Sydney Opera House'),
    (58.0, 'c09',          11.0, 'present', 0.55, 0.55, 1.00, 1.05, 1.0, 'Harbour Bridge'),
    (59.5, 'c23',          2.6,  'night',   0.50, 0.50, 1.00, 1.08, 1.0, 'Flinders Street Station, Melbourne'),
    (61.0, 'j3',           3.5,  'present', 0.50, 0.55, 1.00, 1.06, 1.0, 'Welsh clifftop to the sea'),
    (62.5, 'p:5084489',    14.0,  'present', 0.50, 0.50, 1.00, 1.05, 1.0, 'London buses'),
    (64.0, 'p:27118848',   5.0,  'present', 0.50, 0.55, 1.00, 1.05, 0.8, 'children race across a field'),
    (65.5, 'c19',          2.0,  'present', 0.50, 0.65, 1.00, 1.06, 0.8, 'riders in a Cotswold lane'),
    (67.0, 'j4',           8.0,  'present', 0.50, 0.60, 1.00, 1.06, 1.0, 'path down to a Welsh beach'),
    (68.5, 'c20',          30.0, 'night',   0.50, 0.55, 1.00, 1.06, 0.6, 'drum dance at the palace'),
    (70.0, 'p:7565156',    2.0,  'present', 0.50, 0.50, 1.00, 1.08, 0.8, 'pages of a picture book turn'),
    (71.5, 'c21',          1.0,  'present', 0.45, 0.62, 1.00, 1.06, 1.0, 'flags over the Randolph, Oxford'),
    (73.0, 'c28',          1.0,  'present', 0.50, 0.40, 1.00, 1.08, 1.0, 'The Travel Book Co., Notting Hill'),
    (74.5, 'j2',           2.0,  'present', 0.50, 0.50, 1.00, 1.06, 1.0, 'Welsh coast'),
    (76.0, 'p:31801691',   4.0,  'present', 0.55, 0.45, 1.00, 1.08, 0.8, 'the great palace drum'),
    (77.5, 'c29',          30.0, 'night',   0.50, 0.65, 1.00, 1.08, 0.7, 'court dance, blue and white'),
    (79.0, 'p:38035115',   3.0,  'night',   0.50, 0.50, 1.00, 1.08, 1.0, 'Seoul at night from above'),
    (80.5, 'p:30975008',   10.0, 'present', 0.50, 0.40, 1.00, 1.06, 1.0, 'N Seoul Tower on Namsan'),
    (82.0, 'c13',          60.0, 'night',   0.50, 0.65, 1.00, 1.08, 0.7, 'dancers in yellow'),
    (83.5, 'p:7308355',    2.0,  'present', 0.50, 0.50, 1.00, 1.08, 0.8, 'small hands on a picture book'),
    (85.0, 'p:17735952',   6.0,  'night',   0.50, 0.45, 1.00, 1.06, 1.0, 'fireworks'),
    (86.5, 'p:10714335',   2.0,  'present', 0.55, 0.45, 1.00, 1.06, 1.0, 'Taegukgi'),
    (88.0, 'p:9279682',    2.0,  'present', 0.60, 0.40, 1.00, 1.06, 1.0, 'Union Jack'),
    # DROP 89 s: black with one line; TITLE slam over the flags at 94.5 s ---------------------
    (89.0, 'black',        0.0,  'present', 0.5, 0.5, 1, 1, 1, 'black'),
    (94.5, 'p:13301938',   3.0,  'present', 0.50, 0.50, 1.00, 1.08, 0.5, 'field of Taegukgi in the wind'),
    (96.8, 'p:3150358',    8.0,  'present', 0.45, 0.45, 1.00, 1.08, 0.5, 'Union Jack in the wind'),
    (99.0, 'c12',          1.0,  'present', 0.45, 0.45, 1.00, 1.10, 0.8, 'butterfly mural, Oxford'),
    # Joy, 18 Nov 2026: no close-up of her face here; end on our picture book in Oxford instead.
    # 16:9: slow tilt from the Radcliffe Camera (fy 0.30) down to the book (fy 0.80); 9:16 shows both.
    (101.5,'j6',           2.0,  'present', 0.45, 0.30, 1.00, 1.04, 0.7, 'Radcliffe Camera, tilt down to...'),
    (104.5,'j6',           4.5,  'present', 0.45, 0.80, 1.00, 1.08, 0.7, '...our Bear & Joy picture book against Oxford stone'),
    (108.0,'endcard',      0.0,  'present', 0.5, 0.5, 1, 1, 1, 'black end card: logo, then URL'),
]

# Subtitles: (start, end, Korean, English, style)
#   'big'   = large statement (Gowun Batang) left third, small English under it (reference style)
#   'sub'   = two-line subtitle, Korean above English, low centre
#   'place' = location super (Playfair, lower-left, small Korean under)
#   'title' = centred line on black;  'main' = main title over the flags
LINES = [
    (2.3,  5.3,  '아주 오래전,',              'Long ago,',                              'big'),
    (5.7,  9.3,  '한 통의 편지가',             'a single letter',                         'big'),
    (9.7,  12.3, '바다를 건넜고',              'crossed the sea,',                        'big'),
    (12.6, 14.8, '낯선 사람이',                'and a stranger',                          'big'),
    (15.1, 19.0, '친구가 되었습니다.',          'became a friend.',                        'big'),
    (21.7, 24.0, '서울',                      'Seoul, Korea',                            'place'),
    (30.2, 33.8, '그리고 오늘,',               'And today,',                              'sub'),
    (34.1, 36.0, '런던',                      'London, England',                         'place'),
    (37.2, 40.8, '우리 아이의 첫 한 마디가',     "your child's first phrase",               'sub'),
    (41.2, 43.4, '옥스퍼드',                   'Oxford, England',                         'place'),
    (45.3, 48.8, '한 마디의 문',               'One phrase opens a door.',                'big'),
    (49.2, 51.0, '웨일스',                    'Wales',                                   'place'),
    (53.7, 55.0, '도쿄',                      'Tokyo, Japan',                            'place'),
    (56.7, 58.0, '시드니',                     'Sydney, Australia',                       'place'),
    (59.6, 61.0, '멜버른',                     'Melbourne, Australia',                    'place'),
    (62.6, 67.0, '한 마디는 인사가 되고,',       'One phrase becomes a hello,',             'sub'),
    (67.2, 72.0, '인사는 친구가 되고,',          'a hello becomes a friend,',               'sub'),
    (72.4, 77.4, '친구는 세상이 됩니다.',        'and a friend becomes the world.',         'sub'),
    (79.1, 84.8, 'Born in Oxford · Built in Seoul', '', 'tagline'),   # Bear & Joy's own tagline (Joy, 18 Nov 2026)
    (89.8, 94.2, '그 첫 마디는, 그림책에서 시작됩니다.', 'That first phrase begins in a picture book.', 'title'),
    (94.5, 99.0, '작은 걸음. 하나의 큰 모험.',    'Little Steps to Big Adventures',          'main'),
]
