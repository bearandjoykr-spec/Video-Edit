"""Plan v3 — "한 마디의 문" / English connects Korea to the world. Bear & Joy brand film.

v3 (Joy, 18 Nov 2026): the trailer cut said nothing and its type was too big. The film should carry our voice:
English is the language that connects Korea and the world. A child in Seoul learns one English sentence and that
sentence carries them across the world (route = the Bear & Joy series countries, bear-journey-cards.webp). In each
place the child's own English line appears as a small subtitle, so the English itself tells the story. The Bear with
No Name story is for a separate video; our book appears at the end. Piano music, small type, no red, no Wales,
no letterbox, a gentle natural grade.

Previous plans (trailer v2) are in git history.

Shot: (start s, clip, in-point s, look, fx, fy, zoom-from, zoom-to, speed, note)
  clip: 'cNN' / 'jN' Joy's footage (prep/), 'p:ID' Pexels (pexels/ID.mp4), 'black', 'endcard'
"""
END = 113.0
MUSIC = 'piano-travel-627382.mp3'      # Pixabay "Travel Piano" (recommended; Joy chooses by ear)
FLASHES = []                           # no white flashes in this cut
LETTERBOX = False

SHOTS = [
    # SEOUL — one sentence ------------------------------------------------------------------
    (0.0,  'p:29354411',  1.0,  'soft', 0.50, 0.50, 1.00, 1.06, 0.8, 'Seoul street, morning'),
    (4.0,  'p:8471666',   2.0,  'soft', 0.55, 0.50, 1.00, 1.06, 0.8, 'two children read an English book together'),
    (8.5,  'p:15614364',  12.0, 'soft', 0.50, 0.40, 1.00, 1.04, 0.8, 'a plane lifts off'),
    # THE WORLD — the child's English, place by place (route of the Bear & Joy cards) ----------
    (12.5, 'c06',         5.0,  'soft', 0.55, 0.62, 1.00, 1.06, 1.0, 'Oxford rooftops'),
    (16.5, 'p:3206652',   2.0,  'soft', 0.50, 0.55, 1.00, 1.05, 1.0, 'London crossing, red buses'),
    (20.0, 'p:7197893',   4.0,  'soft', 0.50, 0.55, 1.00, 1.05, 1.0, 'Paris, Champ de Mars'),
    (24.0, 'p:4840503',   2.0,  'soft', 0.50, 0.50, 1.00, 1.05, 1.0, 'Rome, a market square'),
    (27.5, 'p:38884169',  5.0,  'soft', 0.50, 0.50, 1.00, 1.05, 1.0, 'Istanbul, the Bosphorus'),
    (30.5, 'p:29622798',  3.0,  'soft', 0.50, 0.55, 1.00, 1.05, 1.0, 'Cairo, camels and the pyramids'),
    (34.5, 'p:14908997',  3.0,  'soft', 0.50, 0.55, 1.00, 1.05, 1.0, 'Kenya, giraffes'),
    (38.0, 'p:9116111',   2.0,  'soft', 0.50, 0.60, 1.00, 1.05, 1.0, 'Cape Town, penguins at sunset'),
    (41.0, 'p:12851353',  1.0,  'soft', 0.50, 0.45, 1.00, 1.04, 0.8, 'Mumbai, schoolchildren wave hello'),
    (45.5, 'p:39292014',  4.0,  'soft', 0.50, 0.45, 1.00, 1.05, 1.0, 'Nepal, prayer flags'),
    (49.0, 'p:39646286',  1.0,  'soft', 0.50, 0.50, 1.00, 1.05, 1.0, 'Chengdu, a panda'),
    (52.5, 'p:15785118',  8.0,  'soft', 0.50, 0.55, 1.00, 1.05, 1.0, 'Hoi An, lanterns on the river'),
    (56.5, 'c09',         0.5,  'soft', 0.40, 0.55, 1.00, 1.04, 1.0, 'Sydney Opera House'),
    (59.5, 'p:3321014',   2.0,  'soft', 0.50, 0.50, 1.00, 1.05, 1.0, 'New Zealand, lake and mountains'),
    (62.5, 'p:11279748',  1.0,  'soft', 0.50, 0.50, 1.00, 1.04, 0.9, 'Moorea, whales'),
    (65.5, 'p:17054489',  4.0,  'soft', 0.50, 0.45, 1.00, 1.04, 0.9, 'Cusco, a festival dance'),
    (69.0, 'p:37595373',  2.0,  'soft', 0.50, 0.50, 1.00, 1.05, 1.0, 'Rio de Janeiro, the beach'),
    (72.0, 'p:34118777',  3.0,  'soft', 0.50, 0.55, 1.00, 1.05, 1.0, 'New York, Central Park'),
    (75.5, 'p:3888935',   2.0,  'soft', 0.50, 0.50, 1.00, 1.05, 1.0, 'Vancouver, the harbour'),
    (78.5, 'p:31385031',  6.0,  'soft', 0.50, 0.45, 1.00, 1.05, 0.9, 'Kyoto, a paper umbrella'),
    # PEOPLE — never alone -------------------------------------------------------------------
    (81.5, 'p:8441312',   3.0,  'soft', 0.50, 0.45, 1.00, 1.04, 0.9, 'children from many countries, arm in arm'),
    (85.5, 'p:5085429',   5.0,  'soft', 0.50, 0.45, 1.00, 1.04, 0.9, 'two friends share a secret and laugh'),
    (88.5, 'p:8342700',   1.0,  'soft', 0.55, 0.45, 1.00, 1.04, 0.9, 'a girl waves hello'),
    # HOME — it begins with a picture book -------------------------------------------------------
    (92.0, 'p:10565881',  2.0,  'soft', 0.50, 0.50, 1.00, 1.05, 0.8, 'reading a picture book at bedtime'),
    (96.0, 'j6',          2.0,  'soft', 0.45, 0.30, 1.00, 1.04, 0.7, 'Radcliffe Camera, tilt down to...'),
    (99.5, 'j6',          4.5,  'soft', 0.45, 0.80, 1.00, 1.08, 0.7, '...our Bear & Joy book on Oxford stone'),
    (104.5,'endcard',     0.0,  'soft', 0.5, 0.5, 1, 1, 1, 'end card: logo, tagline, URL'),
]

# (start, end, Korean, English, style)
#   'line'   = our voice: Korean above, English below, small, low centre
#   'phrase' = the child's own English (English first, Korean meaning below)
#   'place'  = small letter-spaced place label, top left (English  ·  Korean)
LINES = [
    (0.6,  4.0,  '오늘, 서울의 한 아이가 영어 한 문장을 배웠습니다.', 'Today, a child in Seoul learned one English sentence.', 'line'),
    (4.3,  8.4,  '안녕! 나는 한국에서 왔어. 만나서 반가워!',          '“Hi! I’m from Korea. Nice to meet you!”',               'phrase'),
    (8.8,  12.3, '그 한 문장이, 아이를 세상으로 데려갑니다.',         'And that one sentence carries them into the world.',     'line'),

    (12.7, 16.3, '옥스퍼드 · 영국',      'OXFORD · ENGLAND',        'place'),
    (13.2, 16.3, '실례지만, 도서관이 어디예요?', '“Excuse me, where is the library?”', 'phrase'),
    (16.7, 19.8, '런던 · 영국',          'LONDON · ENGLAND',        'place'),
    (20.2, 23.8, '파리 · 프랑스',        'PARIS · FRANCE',          'place'),
    (20.6, 23.8, '사진 좀 찍어 주시겠어요?',     '“Could you take our picture, please?”', 'phrase'),
    (24.2, 27.3, '로마 · 이탈리아',      'ROME · ITALY',            'place'),
    (24.5, 27.3, '냄새가 정말 좋아요!',          '“This smells delicious!”',             'phrase'),
    (27.7, 30.3, '이스탄불 · 튀르키예',  'ISTANBUL · TÜRKİYE',      'place'),
    (30.7, 34.3, '카이로 · 이집트',      'CAIRO · EGYPT',           'place'),
    (31.0, 34.3, '낙타한테 인사해도 돼요?',      '“Can I say hello to your camel?”',     'phrase'),
    (34.7, 37.8, '나이로비 · 케냐',      'NAIROBI · KENYA',         'place'),
    (35.0, 37.8, '봐! 기린이 정말 커!',          '“Look! They’re so tall!”',             'phrase'),
    (38.2, 40.8, '케이프타운 · 남아프리카공화국', 'CAPE TOWN · SOUTH AFRICA', 'place'),
    (41.2, 45.3, '뭄바이 · 인도',        'MUMBAI · INDIA',          'place'),
    (41.5, 45.3, '안녕! 너는 이름이 뭐야?',      '“Hi! What’s your name?”',              'phrase'),
    (45.7, 48.8, '카트만두 · 네팔',      'KATHMANDU · NEPAL',       'place'),
    (46.0, 48.8, '도와주셔서 고마워요.',          '“Thank you for helping us.”',          'phrase'),
    (49.2, 52.3, '청두 · 중국',          'CHENGDU · CHINA',         'place'),
    (49.5, 52.3, '쉿… 자고 있나 봐.',             '“Shh… I think he’s sleeping.”',        'phrase'),
    (52.7, 56.3, '호이안 · 베트남',      'HOI AN · VIETNAM',        'place'),
    (53.0, 56.3, '우리 같이 소원 빌래?',          '“Shall we make a wish together?”',     'phrase'),
    (56.7, 59.3, '시드니 · 호주',        'SYDNEY · AUSTRALIA',      'place'),
    (59.7, 62.3, '뉴질랜드',             'NEW ZEALAND',             'place'),
    (62.7, 65.3, '모오레아 · 프랑스령 폴리네시아', 'MOOREA · FRENCH POLYNESIA', 'place'),
    (63.0, 65.3, '방금 봤어?!',                   '“Did you see that?!”',                 'phrase'),
    (65.7, 68.8, '쿠스코 · 페루',        'CUSCO · PERU',            'place'),
    (66.0, 68.8, '이 춤 가르쳐 줄래요?',          '“Can you teach me this dance?”',       'phrase'),
    (69.2, 71.8, '리우데자네이루 · 브라질', 'RIO DE JANEIRO · BRAZIL', 'place'),
    (72.2, 75.4, '뉴욕 · 미국',          'NEW YORK · USA',          'place'),
    (72.5, 75.4, '우리랑 같이 놀래?',             '“Do you want to play with us?”',       'phrase'),
    (75.7, 78.3, '밴쿠버 · 캐나다',      'VANCOUVER · CANADA',      'place'),
    (78.7, 81.3, '교토 · 일본',          'KYOTO · JAPAN',           'place'),

    (81.8, 85.6, '어디를 가든, 아이는 혼자가 아닙니다.',     'Wherever they go, they are never alone.',              'line'),
    (86.0, 91.6, '영어는 한국과 세계를 잇는 언어니까요.',    'Because English is the language that connects Korea to the world.', 'line'),
    (92.3, 95.8, '그리고 그 모든 대화는,',                   'And every one of those conversations',                 'line'),
    (96.2, 100.0,'오늘 밤, 그림책 한 권에서 시작됩니다.',   'begins tonight, with one picture book.',               'line'),
    (100.4,104.2,'Born in Oxford · Built in Seoul',          '',                                                     'tagline'),
]
