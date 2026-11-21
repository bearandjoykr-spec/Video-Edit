"""Render storyboard stills from the real footage with the planned grade, crop, letterbox and subtitles.
Usage: tools/fx-venv/bin/python projects/2026-11-cinematic-film/storyboard.py <outdir>
"""
import os, subprocess, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '../..'))
sys.path.insert(0, HERE)
from plan import SHOTS, LINES, END  # noqa
import plan as _plan  # noqa
LETTERBOX = getattr(_plan, 'LETTERBOX', True)
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


ART = f'{ROOT}/projects/2026-11-cinematic-film/art'


def src(clip):
    if clip.startswith('a:'):
        return f'{ART}/{clip[2:]}'
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
    still = p.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
    if look.endswith('+fit'):
        # whole artwork on a cream page (book cover, single pages)
        base = look[:-4]
        sw, sh = (int(W * 0.9 / zoom), int(pic_h * 0.74 / zoom))   # leave the lower band free for subtitles
        vf = (f'scale={sw}:{sh}:force_original_aspect_ratio=decrease:flags=lanczos,'
              f'pad={W}:{pic_h}:(ow-iw)/2:(oh-ih)*0.3:color=0xF5F0E6,{LOOKS[base]},format=rgb24')
    else:
        cw, ch = (w, w / tgt) if w / h < tgt else (h * tgt, h)
        cw, ch = cw / zoom, ch / zoom
        x = min(max(fx * w - cw / 2, 0), w - cw); y = min(max(fy * h - ch / 2, 0), h - ch)
        vf = f'crop={int(cw)}:{int(ch)}:{int(x)}:{int(y)},scale={W}:{pic_h}:flags=lanczos,{LOOKS[look]},format=rgb24'
    seek = [] if still else ['-ss', str(t)]   # -ss on a JPEG input yields no frame
    out = subprocess.run(['ffmpeg', '-v', 'error', *seek, '-i', p, '-frames:v', '1', '-vf', vf,
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


def spaced(img, xy, text, font, fill, tracking, blur=4):
    """Letter-spaced small caps line, left-anchored at xy (baseline)."""
    x, y = xy
    for ch in text:
        shadow_text(img, (x, y), ch, font, fill, 'ls', blur)
        x += font.getlength(ch) + tracking


NIGHT = (30, 45, 77)


def paper_wash(img, y_from):
    """Soft cream (#F5F0E6) fade from y_from to the bottom, like the bottom of a book page."""
    W, H = img.size; y_from = int(max(0, y_from))
    grad = Image.linear_gradient('L').resize((W, H - y_from)).point(lambda v: int(v * 0.86))
    layer = Image.new('RGB', (W, H - y_from), (245, 240, 230))
    if img.mode == 'RGBA':
        l = layer.convert('RGBA'); l.putalpha(grad); img.alpha_composite(l, (0, y_from))
    else:
        img.paste(layer, (0, y_from), grad)


def shot_under(ln):
    return max((sh for sh in SHOTS if sh[0] <= ln[0] + 0.05), key=lambda sh: sh[0])


def on_light_art(ln):
    """True when the shot under this line is our light artwork (pages, watercolours; not the navy card grid)."""
    shot = max((sh for sh in SHOTS if sh[0] <= ln[0] + 0.05), key=lambda sh: sh[0])
    return (shot[1].startswith('a:') and 'cards' not in shot[1]) or \
        shot[1] in ('gen:oxpage', 'gen:house', 'gen:door', 'gen:bearrun', 'gen:map')


def is_bright(img, W, y0, y1):
    """Mean luma of the subtitle band (centre 70%); True when navy text reads better than cream."""
    box = img.convert('RGB').crop((int(W * 0.15), int(max(0, y0)), int(W * 0.85), int(min(img.height, y1))))
    if box.width < 2 or box.height < 2:
        return False
    from PIL import ImageStat
    return ImageStat.Stat(box.convert('L')).mean[0] > 168


def draw_line(img, ln, W, H, top, pic_h, vertical):
    _, _, ko, en, style = ln
    s = W / 1920 if not vertical else W / 1080
    # v3 storybook type: small, quiet, our voice (Joy, 18 Nov 2026)
    base = top + pic_h * (0.86 if not vertical else 0.70)   # vertical: keep text inside y 300–1450 (Joy, DAY 35)
    if shot_under(ln)[1] == 'd34n5':
        base = top + pic_h * (0.12 if not vertical else 0.24)   # the open page fills the lower frame; use the dark bark above
    if vertical and shot_under(ln)[1] == 'j6':
        base = top + pic_h * 0.56            # keep clear of the book at the bottom of the vertical frame
    if style == 'line':
        f_ko = ImageFont.truetype(KOB, int((40 if not vertical else 46) * s))
        f_en = ImageFont.truetype(ENI, int((28 if not vertical else 32) * s))
        rows = wrap(en, f_en, W * 0.86, 1.0)
        shadow_text(img, (W / 2, base), ko, f_ko, CREAM, 'ms', 5)
        for r, t in enumerate(rows):
            shadow_text(img, (W / 2, base + (46 + r * 36) * s), t, f_en, CREAM, 'ms', 4)
        return
    if style == 'phrase':
        f_en = ImageFont.truetype(ENI, int((44 if not vertical else 50) * s))
        f_ko = ImageFont.truetype(KO, int((28 if not vertical else 32) * s))
        shadow_text(img, (W / 2, base), en, f_en, CREAM, 'ms', 5)
        shadow_text(img, (W / 2, base + 46 * s), ko, f_ko, CREAM, 'ms', 4)
        return
    if style == 'voice':
        # Mark's narration: English (what you hear) above, Korean below; small storybook subtitle.
        # On bright art (cream pages, watercolour sky) the text turns Night navy with no shadow.
        f_en = ImageFont.truetype(ENI, int((40 if not vertical else 46) * s))
        f_ko = ImageFont.truetype(KO, int((28 if not vertical else 32) * s))
        rows = wrap(en, f_en, W * 0.84, 1.0)
        y0 = base - (len(rows) - 1) * 46 * s
        bright = on_light_art(ln)
        if bright and '+fit' not in [sh for sh in SHOTS if sh[0] <= ln[0] + 0.05][-1][3]:
            paper_wash(img, y0 - 110 * s)
        put = (lambda xy, t, f: ImageDraw.Draw(img).text(xy, t, font=f, fill=NIGHT, anchor='ms')) if bright else \
              (lambda xy, t, f: shadow_text(img, xy, t, f, CREAM, 'ms', 5))
        for r, t in enumerate(rows):
            put((W / 2, y0 + r * 46 * s), t, f_en)
        put((W / 2, y0 + (len(rows) - 1) * 46 * s + 44 * s), ko, f_ko)
        return
    if style == 'place':
        x = (72 if not vertical else 64) * s
        y = top + (84 if not vertical else 340) * s
        spaced(img, (x, y), en, ImageFont.truetype(EN, int((26 if not vertical else 32) * s)), CREAM, 4 * s)
        d = ImageDraw.Draw(img)
        d.line([(x, y + 16 * s), (x + 44 * s, y + 16 * s)], fill=GOLD, width=max(1, int(2 * s)))
        shadow_text(img, (x, y + 54 * s), ko, ImageFont.truetype(KO, int((24 if not vertical else 30) * s)), CREAM, 'ls', 4)
        return
    if style == 'tagline' and on_light_art(ln):
        paper_wash(img, base - 140 * s)
        ImageDraw.Draw(img).text((W / 2, base), ko, font=ImageFont.truetype(ENI, int((56 if not vertical else 54) * s)),
                                 fill=NIGHT, anchor='ms')
        return
    if style == 'tagline':
        shadow_text(img, (W / 2, base), ko, ImageFont.truetype(ENI, int((56 if not vertical else 54) * s)), CREAM, 'ms', 6)
        return
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


def draw_overlay(img, ov, W, H, vertical, alpha=1.0):
    """Paste the small hand-drawn Bear or Joy art (overlay/*.png) with a soft shadow."""
    _, _, png, ph, pv = ov
    cx, by, hs = pv if vertical else ph
    art = Image.open(f'{HERE}/overlay/{png}').convert('RGBA')
    h = int(H * hs); w = int(art.width * h / art.height)
    art = art.resize((w, h), Image.LANCZOS)
    if alpha < 1:
        art.putalpha(art.getchannel('A').point(lambda v: int(v * alpha)))
    x, y = int(W * cx - w / 2), int(H * by - h)
    sh = Image.new('RGBA', art.size, (0, 0, 0, 0)); sh.putalpha(art.getchannel('A').point(lambda v: int(v * 0.35)))
    sh = sh.filter(ImageFilter.GaussianBlur(max(2, h // 60)))
    base = img if img.mode == 'RGBA' else None
    if base is None:
        img.paste((0, 0, 0), (x + 3, y + 5), sh.getchannel('A')); img.paste(art, (x, y), art)
    else:
        img.alpha_composite(sh, (x + 3, y + 5)); img.alpha_composite(art, (x, y))


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
    pic_h = H if (vertical or not LETTERBOX) else 804   # 2.39:1 letterbox only when the plan asks
    top = (H - pic_h) // 2
    if clip == 'endcard':
        return endcard(W, H), mid, note
    img = Image.new('RGB', (W, H), (0, 0, 0))
    if clip != 'black':
        z = z0 + (z1 - z0) * 0.3
        fyv = fy if not vertical else 0.5
        img.paste(grab(clip, tin + (mid - start) * speed, look, fx, fyv, z, W, H, pic_h), (0, top))
    for ov in getattr(_plan, 'OVERLAYS', []):
        if ov[0] <= mid + 0.3 and ov[1] > mid:
            draw_overlay(img, ov, W, H, vertical)
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
