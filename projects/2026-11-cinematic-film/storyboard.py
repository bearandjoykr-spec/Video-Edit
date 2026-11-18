"""Render storyboard stills from the real footage with the planned grade, crop, letterbox and subtitles.
Usage: tools/fx-venv/bin/python projects/2026-11-cinematic-film/storyboard.py <outdir>
"""
import os, subprocess, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, HERE)
from plan import SHOTS, LINES, END  # noqa
from looks import LOOKS  # noqa

PREP = f'{ROOT}/raw-footage/cinematic-film/prep'
STOCK = f'{ROOT}/raw-footage/cinematic-film/stock'
F = f'{ROOT}/remotion/public/fonts'
KO = f'{F}/ijwSs5nhRMIjYsdSgcMa3wRhXA.ttf'          # Gowun Batang 400
KOB = f'{F}/ijwNs5nhRMIjYsdSgcMa3wRZ4J7awg.ttf'     # Gowun Batang 700
EN = f'{F}/nuFRD-vYSZviVYUb_rj3ij__anPXDTnCjmHKM4nYO7KN_qiTbtY.ttf'   # Playfair 400
ENI = f'{F}/nuFvD-vYSZviVYUb_rj3ij__anPXJzDwcbmjWBN2PKebukDQ.ttf'   # Playfair italic
CREAM = (245, 240, 230)
GOLD = (201, 168, 76)


PEXELS = f'{ROOT}/raw-footage/cinematic-film/pexels'


def src(clip):
    if clip.startswith('s:'):
        return f'{STOCK}/{clip[2:]}.mp4'
    if clip.startswith('p:'):
        return f'{PEXELS}/{clip[2:]}.mp4'
    return f'{PREP}/{clip}.mov'


def grab(clip, t, look, fx, fy, zoom, W, H, pic_h):
    """One graded frame, cropped to W x pic_h around (fx, fy)."""
    p = src(clip)
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams',
                                               '-of', 'json', p]))['streams'][0]
    w, h = info['width'], info['height']
    rot = [d.get('rotation', 0) for d in info.get('side_data_list', [])]
    if rot and abs(int(rot[0])) % 180 == 90:
        w, h = h, w
    tgt = W / pic_h
    cw, ch = (w, w / tgt) if w / h < tgt else (h * tgt, h)
    cw, ch = cw / zoom, ch / zoom
    x = min(max(fx * w - cw / 2, 0), w - cw); y = min(max(fy * h - ch / 2, 0), h - ch)
    vf = f'crop={int(cw)}:{int(ch)}:{int(x)}:{int(y)},scale={W}:{pic_h}:flags=lanczos,{LOOKS[look]},format=rgb24'
    out = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', p, '-frames:v', '1', '-vf', vf,
                          '-f', 'rawvideo', '-'], capture_output=True).stdout
    return Image.frombytes('RGB', (W, pic_h), out)


def shadow_text(img, xy, text, font, fill, anchor, blur=6):
    sh = Image.new('L', img.size, 0)
    ImageDraw.Draw(sh).text(xy, text, font=font, fill=210, anchor=anchor, stroke_width=max(1, int(font.size / 16)))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    if img.mode == 'RGBA':   # transparent title layers for the final render
        layer = Image.new('RGBA', img.size, (0, 0, 0, 0)); layer.putalpha(sh)
        img.alpha_composite(layer)
    else:
        img.paste((0, 0, 0), (0, 0), sh)
    ImageDraw.Draw(img).text(xy, text, font=font, fill=fill, anchor=anchor)


RED = (214, 38, 38)


def cond_text(img, xy, text, font, fill, anchor, squeeze=0.78, blur=8):
    """Tall, condensed type like the reference reel: draw normally, then squeeze horizontally about x."""
    W, H = img.size; x, y = xy
    CW = int(W / squeeze) + 2                      # wide canvas so nothing clips before the squeeze
    layer = Image.new('RGBA', (CW, H), (0, 0, 0, 0))
    shadow_text(layer, (x / squeeze, y), text, font, fill, anchor, blur)
    full = layer.resize((W, H), Image.LANCZOS)
    if img.mode == 'RGBA':
        img.alpha_composite(full)
    else:
        img.paste(full, (0, 0), full)


def wrap(text, font, max_w, squeeze):
    if font.getlength(text) * squeeze <= max_w or ' ' not in text:
        return [text]
    words = text.split(' '); best = None
    for i in range(1, len(words)):
        a, b = ' '.join(words[:i]), ' '.join(words[i:])
        w = max(font.getlength(a), font.getlength(b))
        if best is None or w < best[0]:
            best = (w, [a, b])
    return best[1]


def draw_line(img, ln, W, H, top, pic_h, vertical):
    _, _, ko, en, style = ln
    s = W / 1920 if not vertical else W / 1080
    if style == 'sub':
        y = top + pic_h - (110 if not vertical else 520) * s
        shadow_text(img, (W / 2, y), ko, ImageFont.truetype(KO, int(54 * s if not vertical else 60 * s)), CREAM, 'ms')
        shadow_text(img, (W / 2, y + 60 * s), en, ImageFont.truetype(ENI, int(40 * s if not vertical else 46 * s)), CREAM, 'ms')
    elif style == 'tagline':
        cond_text(img, (W / 2, top + pic_h / 2 + 30 * s), ko, ImageFont.truetype(EN, int((120 if not vertical else 92) * s)), CREAM, 'ms', 0.8, 12)
    elif style == 'big':
        # reference: huge statement top-left, a small line underneath
        size = 170 if not vertical else 132
        x = (150 if not vertical else 80) * s
        y = top + pic_h * (0.40 if not vertical else 0.30)
        f = ImageFont.truetype(KO, int(size * s))
        rows = wrap(ko, f, W - 2 * x, 0.78)
        for r, t in enumerate(rows):
            cond_text(img, (x, y + r * size * 1.12 * s), t, f, CREAM, 'ls', 0.78, 12)
        y2 = y + (len(rows) - 1) * size * 1.12 * s + 78 * s
        cond_text(img, (x + 6 * s, y2), en, ImageFont.truetype(EN, int(46 * s)), CREAM, 'ls', 0.85, 6)
    elif style == 'place':
        x = (150 if not vertical else 80) * s
        y = top + pic_h - (120 if not vertical else 560) * s
        cond_text(img, (x, y), en, ImageFont.truetype(EN, int((176 if not vertical else 140) * s)), CREAM, 'ls', 0.72, 14)
        cond_text(img, (x + 8 * s, y + 66 * s), ko, ImageFont.truetype(KO, int(40 * s)), CREAM, 'ls', 0.85, 6)
    elif style == 'row':
        # reference: one red row across a B/W shot
        if vertical:
            y = H * 0.60
            cond_text(img, (W / 2, y), ko, ImageFont.truetype(KO, int(76 * s)), RED, 'ms', 0.85, 10)
            cond_text(img, (W / 2, y + 86 * s), en, ImageFont.truetype(EN, int(64 * s)), RED, 'ms', 0.8, 10)
        else:
            y = top + pic_h * 0.66
            cond_text(img, (W * 0.30, y), ko, ImageFont.truetype(KO, int(66 * s)), RED, 'ms', 0.85, 10)
            cond_text(img, (W * 0.70, y), en, ImageFont.truetype(EN, int(62 * s)), RED, 'ms', 0.8, 10)
    elif style == 'title':
        f = ImageFont.truetype(KO, int((96 if not vertical else 80) * s))
        rows = wrap(ko, f, W * 0.84, 0.82); y = H / 2 - (len(rows) - 1) * 44 * s
        for r, t in enumerate(rows):
            cond_text(img, (W / 2, y + r * 88 * s), t, f, CREAM, 'ms', 0.82, 10)
        cond_text(img, (W / 2, y + (len(rows) - 1) * 88 * s + 70 * s), en, ImageFont.truetype(EN, int(44 * s)), CREAM, 'ms', 0.85, 6)
    elif style == 'main':
        cond_text(img, (W / 2, H / 2 - (130 if not vertical else 150) * s), 'THE BEAR & JOY CO.  PRESENTS', ImageFont.truetype(EN, int(30 * s)), GOLD, 'ms', 0.9, 4)
        fs = 150 if not vertical else 132
        if vertical:
            cond_text(img, (W / 2, H / 2 - 10 * s), 'Little Steps', ImageFont.truetype(EN, int(fs * s)), CREAM, 'ms', 0.78, 14)
            cond_text(img, (W / 2, H / 2 + 120 * s), 'to Big Adventures', ImageFont.truetype(EN, int(fs * s)), CREAM, 'ms', 0.78, 14)
            cond_text(img, (W / 2, H / 2 + 210 * s), ko, ImageFont.truetype(KO, int(50 * s)), CREAM, 'ms', 0.85, 6)
        else:
            cond_text(img, (W / 2, H / 2 + 20 * s), en, ImageFont.truetype(EN, int(fs * s)), CREAM, 'ms', 0.78, 14)
            cond_text(img, (W / 2, H / 2 + 100 * s), ko, ImageFont.truetype(KO, int(48 * s)), CREAM, 'ms', 0.85, 6)


def endcard(W, H):
    img = Image.new('RGB', (W, H), (30, 45, 77))
    logo = Image.open(f'{ROOT}/brand/assets/bear-butterfly.png').convert('RGBA')
    wm = Image.open(f'{ROOT}/brand/assets/wordmark-cream.png').convert('RGBA')
    s = min(W, H) / 1080
    logo = logo.resize((int(300 * s), int(300 * s * logo.height / logo.width)))
    wm = wm.resize((int(620 * s), int(620 * s * wm.height / wm.width)))
    y0 = int(H / 2 - (logo.height + wm.height + 120 * s) / 2)
    img.paste(logo, ((W - logo.width) // 2, y0), logo)
    img.paste(wm, ((W - wm.width) // 2, y0 + logo.height + int(20 * s)), wm)
    d = ImageDraw.Draw(img)
    d.text((W / 2, y0 + logo.height + wm.height + int(80 * s)), 'Born in Oxford · Built in Seoul',
           font=ImageFont.truetype(ENI, int(38 * s)), fill=CREAM, anchor='ms')
    d.text((W / 2, y0 + logo.height + wm.height + int(130 * s)), 'bearandjoy.com',
           font=ImageFont.truetype(EN, int(28 * s)), fill=GOLD, anchor='ms')
    return img


def frame(i, vertical):
    start, clip, tin, look, fx, fy, z0, z1, speed, note = SHOTS[i]
    nxt = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else END
    mid = start + min(1.2, (nxt - start) / 2)
    W, H = (1080, 1920) if vertical else (1920, 1080)
    pic_h = H if vertical else 804              # 2.39:1 letterbox in the 16:9 film
    top = (H - pic_h) // 2
    if clip == 'endcard':
        return endcard(W, H), mid, note
    img = Image.new('RGB', (W, H), (0, 0, 0))
    if clip != 'black':
        z = z0 + (z1 - z0) * 0.3
        fyv = fy if not vertical else 0.5
        img.paste(grab(clip, tin + (mid - start) * speed, look, fx, fyv, z, W, H, pic_h), (0, top))
    for ln in LINES:
        if ln[0] <= mid + 0.3 and ln[1] > mid:
            draw_line(img, ln, W, H, top, pic_h, vertical)
    return img, mid, note


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    meta = []
    for v in (False, True):
        for i in range(len(SHOTS)):
            img, t, note = frame(i, v)
            name = f"{'v' if v else 'h'}{i:02d}.jpg"
            img.save(f'{out}/{name}', quality=85)
            if not v:
                meta.append({'i': i, 't': round(t, 1), 'start': SHOTS[i][0], 'clip': SHOTS[i][1], 'note': note,
                             'lines': [[l[2], l[3]] for l in LINES if l[0] <= t + 0.3 and l[1] > t]})
    json.dump(meta, open(f'{out}/meta.json', 'w'), ensure_ascii=False, indent=1)
    print('ok', len(meta))
