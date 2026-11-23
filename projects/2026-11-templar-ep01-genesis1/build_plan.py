"""Build the Remotion plan for a Templar episode from the whisper.cpp word timings.

usage: python3 build_plan.py <whisper.json> <out plan.json> [--offset 7.0]

- Display text comes from the script (sections) and the KJV (the reading), never from Whisper.
- Whisper only gives timing: script words are aligned to the heard words; words Mark did not
  say get times interpolated from their neighbours.
- --offset: seconds of title card before the voice starts (the audio is delayed by this in the mix).
"""
import json, re, sys, difflib, argparse

ap = argparse.ArgumentParser()
ap.add_argument('whisper'); ap.add_argument('out'); ap.add_argument('--offset', type=float, default=11.5)
ap.add_argument('--voice', default=__file__.rsplit('/', 1)[0] + '/../../raw-footage/templar-ep01/ep01_48k.wav')
ap.add_argument('--pre', type=float, default=4.5, help='headphones card before the title')
ap.add_argument('--trim', type=float, default=None, help='seconds cut from the start of the voice (default: just before the first word)')
args = ap.parse_args()
OFF = args.offset; PRE = args.pre

# ---------------- heard words ----------------
def heard_words(path):
    d = json.load(open(path))
    words = []
    for seg in d['transcription']:
        for tk in seg.get('tokens', []):
            txt = tk['text']
            if txt.startswith('[_') or txt.startswith('<|'):
                continue
            s = tk['offsets']['from'] / 1000; e = tk['offsets']['to'] / 1000
            if tk.get('t_dtw', -1) not in (-1, None):
                s = tk['t_dtw'] / 100
            if txt.startswith(' ') or not words:
                words.append({'w': txt.strip(), 's': s, 'e': e})
            else:
                words[-1]['w'] += txt; words[-1]['e'] = max(words[-1]['e'], e)
    words = [w for w in words if norm(w['w'])]
    # DTW gives the onset; make each word end at the next onset (capped)
    for i, w in enumerate(words):
        nxt = words[i + 1]['s'] if i + 1 < len(words) else w['s'] + 0.5
        w['e'] = min(max(w['s'] + 0.12, nxt - 0.02), w['s'] + 1.2)
    return words

def norm(w):
    w = w.lower().replace('’', "'")
    w = re.sub(r"[^a-z0-9']", '', w)
    return {'lord': 'lord'}.get(w, w)

# ---------------- display text ----------------
SCRIPT = open(__file__.rsplit('/', 1)[0] + '/script.md').read()

def section(name):
    m = re.search(r'^## ' + re.escape(name) + r'.*?$(.*?)(?=^## |\Z)', SCRIPT, re.S | re.M)
    return m.group(1)

def clean(text):
    """Script markdown -> spoken text (drop stage directions, markup)."""
    text = re.sub(r'\[[^\]]*\]', ' ', text)
    text = re.sub(r'^\s*>\s?', '', text, flags=re.M)
    text = text.replace('**', '').replace('*', '')
    text = re.sub(r'\(Numbers 6:24–26\)', '', text)
    return re.sub(r'\s+', ' ', text).strip()

KJV = [  # (chapter, verse, text) Genesis 1:1–2:3, King James Version
 (1,1,"In the beginning God created the heaven and the earth."),
 (1,2,"And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters."),
 (1,3,"And God said, Let there be light: and there was light."),
 (1,4,"And God saw the light, that it was good: and God divided the light from the darkness."),
 (1,5,"And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day."),
 (1,6,"And God said, Let there be a firmament in the midst of the waters, and let it divide the waters from the waters."),
 (1,7,"And God made the firmament, and divided the waters which were under the firmament from the waters which were above the firmament: and it was so."),
 (1,8,"And God called the firmament Heaven. And the evening and the morning were the second day."),
 (1,9,"And God said, Let the waters under the heaven be gathered together unto one place, and let the dry land appear: and it was so."),
 (1,10,"And God called the dry land Earth; and the gathering together of the waters called he Seas: and God saw that it was good."),
 (1,11,"And God said, Let the earth bring forth grass, the herb yielding seed, and the fruit tree yielding fruit after his kind, whose seed is in itself, upon the earth: and it was so."),
 (1,12,"And the earth brought forth grass, and herb yielding seed after his kind, and the tree yielding fruit, whose seed was in itself, after his kind: and God saw that it was good."),
 (1,13,"And the evening and the morning were the third day."),
 (1,14,"And God said, Let there be lights in the firmament of the heaven to divide the day from the night; and let them be for signs, and for seasons, and for days, and years:"),
 (1,15,"And let them be for lights in the firmament of the heaven to give light upon the earth: and it was so."),
 (1,16,"And God made two great lights; the greater light to rule the day, and the lesser light to rule the night: he made the stars also."),
 (1,17,"And God set them in the firmament of the heaven to give light upon the earth,"),
 (1,18,"And to rule over the day and over the night, and to divide the light from the darkness: and God saw that it was good."),
 (1,19,"And the evening and the morning were the fourth day."),
 (1,20,"And God said, Let the waters bring forth abundantly the moving creature that hath life, and fowl that may fly above the earth in the open firmament of heaven."),
 (1,21,"And God created great whales, and every living creature that moveth, which the waters brought forth abundantly, after their kind, and every winged fowl after his kind: and God saw that it was good."),
 (1,22,"And God blessed them, saying, Be fruitful, and multiply, and fill the waters in the seas, and let fowl multiply in the earth."),
 (1,23,"And the evening and the morning were the fifth day."),
 (1,24,"And God said, Let the earth bring forth the living creature after his kind, cattle, and creeping thing, and beast of the earth after his kind: and it was so."),
 (1,25,"And God made the beast of the earth after his kind, and cattle after their kind, and every thing that creepeth upon the earth after his kind: and God saw that it was good."),
 (1,26,"And God said, Let us make man in our image, after our likeness: and let them have dominion over the fish of the sea, and over the fowl of the air, and over the cattle, and over all the earth, and over every creeping thing that creepeth upon the earth."),
 (1,27,"So God created man in his own image, in the image of God created he him; male and female created he them."),
 (1,28,"And God blessed them, and God said unto them, Be fruitful, and multiply, and replenish the earth, and subdue it: and have dominion over the fish of the sea, and over the fowl of the air, and over every living thing that moveth upon the earth."),
 (1,29,"And God said, Behold, I have given you every herb bearing seed, which is upon the face of all the earth, and every tree, in the which is the fruit of a tree yielding seed; to you it shall be for meat."),
 (1,30,"And to every beast of the earth, and to every fowl of the air, and to every thing that creepeth upon the earth, wherein there is life, I have given every green herb for meat: and it was so."),
 (1,31,"And God saw every thing that he had made, and, behold, it was very good. And the evening and the morning were the sixth day."),
 (2,1,"Thus the heavens and the earth were finished, and all the host of them."),
 (2,2,"And on the seventh day God ended his work which he had made; and he rested on the seventh day from all his work which he had made."),
 (2,3,"And God blessed the seventh day, and sanctified it: because that in it he had rested from all his work which God created and made."),
]

# Every displayed word in speaking order, tagged with where it goes.
stream = []   # dicts: t (display), key (section tag)
def add(text, key):
    for w in text.split():
        stream.append({'t': w, 'key': key})

opening = clean(section('Opening'))
# words Mark added while recording (shown on screen so the captions match his voice)
opening = opening.replace('Brothers. Welcome.', "Brothers. Welcome. It's been a while.", 1)
pre, rest = opening.split('Non nobis', 1)
latin_rest, after_latin = rest.split('Not unto us', 1)
english, prayer = ('Not unto us' + after_latin).split('Lord, open', 1)
prayer = 'Lord, open' + prayer
add(pre, 'open')
add('Non nobis' + latin_rest, 'p_latin')
add(english, 'p_english')
p1, p2 = prayer.split('In the name', 1)
add(p1, 'p_prayer1'); add('In the name' + p2, 'p_prayer2')
add(clean(section('Context')), 'context')
add('Genesis, chapter one.', 'b_intro')
for ch, v, txt in KJV:
    if ch == 2 and v == 1:
        add('Genesis, chapter two.', 'b_intro2')
    add(txt, f'v{ch}:{v}')
add('The Word of the Lord.', 'b_end')
add(clean(section('Analysis')), 'analysis')
add(clean(section('For the brothers')), 'brothers')
closing = clean(section('Closing'))
c_pre, c_rest = closing.split('The LORD bless', 1)
bless, c_next = ('The LORD bless' + c_rest).split('Next time:', 1)
charge, c_tail = c_pre.split('In the comments:', 1)
add(charge, 'charge'); add('In the comments:' + c_tail, 'comments')
add(bless, 'blessing'); add('Next time:' + c_next, 'next')

# ---------------- align ----------------
heard = heard_words(args.whisper)
A = [norm(x['t']) for x in stream]
B = [norm(x['w']) for x in heard]
sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False)
for blk in sm.get_matching_blocks():
    for k in range(blk.size):
        h = heard[blk.b + k]
        stream[blk.a + k]['s'] = h['s']; stream[blk.a + k]['e'] = h['e']
matched = sum(1 for x in stream if 's' in x)
print(f'script words {len(stream)}, heard {len(heard)}, matched {matched} ({100*matched/len(stream):.1f}%)')
# interpolate the rest
idx = [i for i, x in enumerate(stream) if 's' in x]
for i, x in enumerate(stream):
    if 's' in x: continue
    prev = max([j for j in idx if j < i], default=None); nxt = min([j for j in idx if j > i], default=None)
    if prev is None: x['s'] = stream[nxt]['s'] - 0.3 * (nxt - i)
    elif nxt is None: x['s'] = stream[prev]['e'] + 0.3 * (i - prev)
    else:
        a, b = stream[prev]['e'], stream[nxt]['s']
        x['s'] = a + (b - a) * (i - prev) / (nxt - prev)
    x['e'] = x['s'] + 0.25; x['interp'] = True
# Music-only pauses inserted into the voice (audio time -> seconds of silence), e.g. a chant swell
# after "The Word of the Lord" while the book closes. mix.py inserts the same gaps into the voice.
GAP_AFTER = {'b_end': 5.0}
gaps = []
for key, secs in GAP_AFTER.items():
    ws = [x for x in stream if x['key'] == key]
    nxt = [x for x in stream if x['s'] > ws[-1]['e']]
    at = (ws[-1]['e'] + min(x['s'] for x in nxt)) / 2 if nxt else ws[-1]['e'] + 0.5
    gaps.append([round(at, 3), secs])
# cut the noisy lead-in (breaths, mouth clicks) before the first word; the mix cuts the same amount
# first sound in the recording (20 ms windows above -40 dBFS for 100 ms)
import soundfile as _sf, numpy as _np
_y, _sr = _sf.read(args.voice, frames=48000 * 15)
_w = int(0.02 * _sr)
_r = [20 * _np.log10(_np.sqrt((_y[i:i + _w] ** 2).mean()) + 1e-9) for i in range(0, len(_y) - _w, _w)]
ONSET = next(i for i in range(len(_r) - 5) if min(_r[i:i + 5]) > -40) * 0.02
# cut the noisy lead-in (breaths, mouth clicks) before the first word; the mix cuts the same amount
TRIM = args.trim if args.trim is not None else round(max(0, ONSET - 0.25), 2)
# hand-checked timings (raw audio seconds) where Whisper was wrong: stream index -> (start, end)
# Ep 1: energy shows "Brothers." at 3.32–3.90 and "Welcome." at 4.52–5.00
OVERRIDE = {0: (3.32, 3.90), 1: (4.52, 5.00)}
for i_, (s_, e_) in OVERRIDE.items():
    stream[i_]['s'], stream[i_]['e'] = s_, e_
# Snap to the real pauses: Whisper often puts the first word after a pause too early (inside the
# silence), so the highlight ran ahead while Mark was silent. Find silences in the recording and
# move any word that starts inside one to where the sound resumes; end words where the silence begins.
_ya, _ = _sf.read(args.voice)
_ra = _np.array([20 * _np.log10(_np.sqrt((_ya[i:i + _w] ** 2).mean()) + 1e-9) for i in range(0, len(_ya) - _w, _w)])
_q = _ra < -48
SIL = []
_i = 0
while _i < len(_q):
    if _q[_i]:
        _j = _i
        while _j < len(_q) and _q[_j]: _j += 1
        if (_j - _i) * 0.02 >= 0.3: SIL.append((_i * 0.02, _j * 0.02))
        _i = _j
    else: _i += 1
import bisect as _bs
_starts = [a_ for a_, b_ in SIL]
moved = 0
def _sil_at(t):
    j_ = _bs.bisect_right(_starts, t) - 1
    return SIL[j_] if j_ >= 0 and SIL[j_][0] <= t < SIL[j_][1] - 0.04 else None
k_ = 0
while k_ < len(stream):
    sl = _sil_at(stream[k_]['s'])
    if not sl:
        k_ += 1; continue
    # run of consecutive words that start inside this silence
    run = [k_]
    while run[-1] + 1 < len(stream) and _sil_at(stream[run[-1] + 1]['s']) == sl: run.append(run[-1] + 1)
    nxt = run[-1] + 1
    t0 = sl[1] + 0.02
    t1 = stream[nxt]['s'] if nxt < len(stream) else t0 + 0.3 * len(run)
    if t1 < t0 + 0.18 * len(run): t1 = t0 + 0.18 * len(run)   # not enough room: give each word ~0.18 s
    for m_, r_ in enumerate(run):
        stream[r_]['s'] = t0 + (t1 - t0) * m_ / len(run)
        stream[r_]['e'] = t0 + (t1 - t0) * (m_ + 1) / len(run) - 0.02
    if run[0] > 0 and stream[run[0] - 1]['e'] > sl[0] + 0.12: stream[run[0] - 1]['e'] = sl[0] + 0.12
    # if we had to push past the next word, carry the push forward until the timeline catches up
    q_ = nxt
    while q_ < len(stream) and stream[q_]['s'] < stream[q_ - 1]['s'] + 0.15:
        stream[q_]['s'] = stream[q_ - 1]['s'] + 0.18; stream[q_]['e'] = max(stream[q_]['e'], stream[q_]['s'] + 0.15); q_ += 1
    moved += len(run); k_ = nxt
print('silences', len(SIL), 'words snapped to the end of a pause', moved)
for x in stream:   # nothing can be spoken before the first sound
    if x['s'] < ONSET:
        x['s'] = ONSET; x['e'] = max(x['e'], ONSET + 0.3)
print('voice trimmed at', TRIM, 's')
def vt(t):  # audio time -> video time
    return t - TRIM + OFF + sum(g for a, g in gaps if t >= a)
for x in stream:
    x['s'] = round(vt(x['s']), 3); x['e'] = round(vt(x['e']), 3)
# report unmatched runs so they can be checked by ear
run = []
for x in stream + [{'s': 0, 'key': ''}]:
    if x.get('interp'): run.append(x)
    elif run:
        if len(run) >= 2: print(f'  not heard @ {run[0]["s"]-OFF:7.2f}s [{run[0]["key"]}]: {" ".join(r["t"] for r in run)}')
        run = []

def T(x): return {'t': x['t'], 's': x['s'], 'e': x['e']}
def keyed(prefix): return [x for x in stream if x['key'] == prefix or x['key'].startswith(prefix)]
def first(words, phrase):
    """time of the first word of phrase inside words"""
    ws = phrase.split(); n = [norm(w) for w in ws]
    for i in range(len(words)):
        if [norm(w['t']) for w in words[i:i + len(n)]] == n: return words[i]['s']
    raise SystemExit(f'phrase not found: {phrase}')

def chunks(words, maxw=16):
    """sentence-sized caption chunks"""
    out, cur = [], []
    for w in words:
        cur.append(w)
        end = w['t'][-1] in '.?!' or (w['t'][-1] in ',;:' and len(cur) >= maxw - 4)
        if end or len(cur) >= maxw:
            out.append(cur); cur = []
    if cur: out.append(cur)
    res = []
    for i, c in enumerate(out):
        nxt = out[i + 1][0]['s'] if i + 1 < len(out) else c[-1]['e'] + 1.2
        res.append({'from': round(c[0]['s'] - 0.25, 3), 'to': round(min(nxt - 0.05, c[-1]['e'] + 2.5), 3), 'tokens': [T(x) for x in c]})
    return res

def span(words, pad_in=0.6, pad_out=0.8):
    return round(words[0]['s'] - pad_in, 3), round(words[-1]['e'] + pad_out, 3)

scenes = []
fps = 30
scenes.append({'type': 'notice', 'from': 0, 'to': PRE + 0.3, 'text': 'Best experienced with headphones', 'sub': 'in a quiet, dark place'})
scenes.append({'type': 'title', 'from': PRE, 'to': OFF + 0.4, 'kicker': 'THE WHOLE BIBLE · EPISODE 1',
               'title': 'IN THE BEGINNING', 'sub': 'Genesis 1:1 – 2:3'})

# opening speech
w = keyed('open'); a, b = span(w)
opening_scene = {'type': 'speech', 'from': a, 'to': None, 'chunks': chunks(w)}
scenes.append(opening_scene)

# prayer
pw = keyed('p_')
pa = first(w, 'Before we open it')
scenes[-1]['to'] = round(pa - 0.1, 3)
blocks = [{'style': 'latin', 'tokens': [T(x) for x in keyed('p_latin')]},
          {'style': 'english', 'tokens': [T(x) for x in keyed('p_english')]},
          {'style': 'prayer', 'tokens': [T(x) for x in keyed('p_prayer1')]},
          {'style': 'prayer', 'tokens': [T(x) for x in keyed('p_prayer2')]}]
# the lead-in line shows as the first block, small
lead = [x for x in w if x['s'] >= pa - 0.01]
blocks.insert(0, {'style': 'say', 'tokens': [T(x) for x in lead]})
pend = pw[-1]['e'] + 1.6
scenes.append({'type': 'prayer', 'from': round(pa - 0.4, 3), 'to': round(pend + 0.4, 3), 'heading': 'THE PRAYER',
               'kneelFrom': round(pa + 0.2, 3), 'kneelTo': round(pend, 3), 'kneelText': 'Brothers, take a knee',
               'kneelSub': 'Bow your head and pray with me', 'blocks': blocks})
# the opening speech chunks must not overlap the prayer
opening_scene['chunks'] = [c for c in opening_scene['chunks'] if c['from'] < pa - 0.2]
for c in opening_scene['chunks']: c['to'] = min(c['to'], pa - 0.15)

# context
w = keyed('context'); a, b = span(w)
scenes.append({'type': 'speech', 'from': round(pend + 0.4, 3), 'to': None, 'chunks': chunks(w)})

# the reading: paginate verses into spreads
bw = keyed('b_') + keyed('v')
bw.sort(key=lambda x: x['s'])
b0 = keyed('b_intro')[0]['s'] - 0.8
scenes[-1]['to'] = round(b0 + 0.6, 3)
for c in scenes[-1]['chunks']: c['to'] = min(c['to'], b0)
paras = []
for ch, v, txt in KJV:
    toks = [T(x) for x in keyed(f'v{ch}:{v}') if x['key'] == f'v{ch}:{v}']
    p = {'verse': v, 'tokens': toks, 'ch': ch}
    if v == 1: p = {'label': f'CHAPTER {ch}', 'dropcap': True, 'tokens': toks, 'ch': ch}
    paras.append(p)
endw = keyed('b_end')
paras.append({'center': True, 'tokens': [T(x) for x in endw], 'ch': 2})
CPL, LPP = 42, 16.2       # characters per line, lines per page (checked against rendered stills)
def lines(p):
    n = sum(len(t['t']) + 1 for t in p['tokens']) + (4 if p.get('verse') else 0)
    l = -(-n // CPL)
    if p.get('label'): l += 1.6 + 1.0
    if p.get('center'): l += 1.0
    return l + 0.15
pages, cur, used = [], [], 0
for p in paras:
    l = lines(p)
    if cur and (used + l > LPP or (p.get('label') and p['ch'] == 2)):
        pages.append(cur); cur, used = [], 0
    cur.append(p); used += l
pages.append(cur)
if len(pages) % 2: pages.append([])
spreads = []
for i in range(0, len(pages), 2):
    allw = [t for pg in pages[i:i + 2] for p in pg for t in p['tokens']]
    spreads.append({'from': allw[0]['s'] - 0.7, 'left': pages[i], 'right': pages[i + 1], 'header': 'GENESIS'})
bend = endw[-1]['e'] + 2.5 + GAP_AFTER['b_end'] - 1.0
for i, s in enumerate(spreads):
    s['from'] = round(b0 if i == 0 else s['from'], 3)
    s['to'] = round(spreads[i + 1]['from'] if i + 1 < len(spreads) else bend, 3)
    for pg in (s['left'], s['right']):
        for p in pg: p.pop('ch', None)
scenes.append({'type': 'bible', 'from': round(b0, 3), 'to': round(bend, 3), 'spreads': spreads})
print('bible spreads:', len(spreads), [round(s['to'] - s['from']) for s in spreads])

# analysis notes
w = keyed('analysis')
items = [{'at': first(w, 'God speaks, and it happens'), 'head': 'God speaks, and it happens', 'body': 'One word, and the universe obeys.'},
         {'at': first(w, 'Order out of chaos'), 'head': 'Order out of chaos', 'body': 'Form, then fullness. God builds with order.'},
         {'at': first(w, 'Man is different'), 'head': 'Man is different', 'body': 'Only man is made in the image of God.'}]
for it in items: it['head'] = it['head']; it['at'] = round(it['at'] - 0.2, 3)
a, b = span(w)
scenes.append({'type': 'notes', 'from': round(bend, 3), 'to': None, 'label': 'WHAT TO NOTICE', 'title': 'THREE THINGS',
               'items': items, 'chunks': chunks([x for x in w if not re.fullmatch(r'\d\.', x['t'])])})
# for the brothers
w = keyed('brothers')
items = [{'at': first(w, 'Know whose image you bear'), 'head': 'Know whose image you bear', 'body': "You didn't earn it, and no one can take it."},
         {'at': first(w, 'Dominion is stewardship'), 'head': 'Dominion is stewardship', 'body': "Strength under control. That's the knight's code."},
         {'at': first(w, 'Work hard, then rest'), 'head': 'Work hard, then rest', 'body': "Rest isn't weakness. It's trust."}]
for it in items: it['at'] = round(it['at'] - 0.2, 3)
a, b = span(w)
scenes[-1]['to'] = round(a - 0.3, 3)
scenes.append({'type': 'notes', 'from': round(a - 0.3, 3), 'to': None, 'label': 'FOR THE BROTHERS', 'title': 'TAKE THESE TO HEART',
               'items': items, 'chunks': chunks(w)})
# the charge
w = keyed('charge'); a, b = span(w)
scenes[-1]['to'] = round(a - 0.3, 3)
scenes.append({'type': 'notes', 'from': round(a - 0.3, 3), 'to': None, 'label': "THIS WEEK'S CHARGE", 'title': 'YOUR CHARGE',
               'items': [{'at': round(first(w, 'pick one thing') - 0.2, 3), 'head': 'Build one thing up on purpose', 'body': 'Your home, your family, your body, or your work.'},
                         {'at': round(first(w, 'And take one day') - 0.2, 3), 'head': 'Take one day to truly rest'}],
               'chunks': chunks(w)})
# comments + subscribe
w = keyed('comments'); a, b = span(w)
scenes[-1]['to'] = round(a - 0.3, 3)
scenes.append({'type': 'speech', 'from': round(a - 0.3, 3), 'to': None, 'chunks': chunks(w)})
# benediction
w = keyed('blessing'); a, b = span(w)
scenes[-1]['to'] = round(a - 1.0, 3)
for c in scenes[-1]['chunks']: c['to'] = min(c['to'], a - 1.1)
scenes.append({'type': 'prayer', 'from': round(a - 1.2, 3), 'to': None, 'heading': 'THE BENEDICTION',
               'kneelFrom': round(a - 1.0, 3), 'kneelTo': round(b, 3), 'kneelText': 'Bow your heads, brothers', 'kneelSub': 'Numbers 6:24–26',
               'blocks': [{'style': 'prayer', 'tokens': [T(x) for x in w]}]})
# next time + sign-off
w = keyed('next'); a, b = span(w)
scenes[-1]['to'] = round(a - 0.2, 3)
end = round(w[-1]['e'] + 10, 3)
scenes.append({'type': 'end', 'from': round(a - 0.2, 3), 'to': end, 'next': 'Genesis 2:4 · The Garden', 'sign': 'Non nobis, Domine.',
               'chunks': chunks(w)})
for i, s in enumerate(scenes):
    if s['to'] is None: s['to'] = scenes[i + 1]['from']

# where the chant plays (video time): title card, the book-closing swell, the end card
chant = [[PRE, OFF + 1.5], [round(endw[-1]['e'] + 0.3, 3), round(bend + 1.0, 3)], [round(w[-1]['e'] + 0.5, 3), end]]
plan = {'fps': fps, 'duration': end, 'audio': None, 'offset': OFF, 'trim': TRIM, 'gaps': [[round(a_ - TRIM, 3), g_] for a_, g_ in gaps], 'chant': chant, 'scenes': scenes}
json.dump(plan, open(args.out, 'w'), indent=1)
for s in scenes: print(f"{s['type']:7s} {s['from']:8.2f} → {s['to']:8.2f}")
