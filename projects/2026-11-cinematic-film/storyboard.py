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
    ImageDraw.Draw(sh).text(xy, text, font=font, fill=210, anchor=anchor, stroke_width=3)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.paste((0, 0, 0), (0, 0), sh)
    ImageDraw.Draw(img).text(xy, text, font=font, fill=fill, anchor=anchor)


def draw_line(img, ln, W, H, top, pic_h, vertical):
    _, _, ko, en, style = ln
    s = W / 1920 if not vertical else W / 1080
    if style == 'sub':
        y = top + pic_h - (110 if not vertical else 520) * s
        shadow_text(img, (W / 2, y), ko, ImageFont.truetype(KO, int(54 * s if not vertical else 60 * s)), CREAM, 'ms')
        shadow_text(img, (W / 2, y + 60 * s), en, ImageFont.truetype(ENI, int(40 * s if not vertical else 46 * s)), CREAM, 'ms')
    elif style == 'big':
        x = (150 if not vertical else 90) * s
        y = top + pic_h * (0.52 if not vertical else 0.40)
        shadow_text(img, (x, y), ko, ImageFont.truetype(KO, int((96 if not vertical else 104) * s)), CREAM, 'ls', 12)
        shadow_text(img, (x + 4 * s, y + 64 * s), en, ImageFont.truetype(ENI, int(40 * s)), CREAM, 'ls')
    elif style == 'place':
        x = (150 if not vertical else 80) * s
        y = top + pic_h - (150 if not vertical else 700) * s
        shadow_text(img, (x, y), en, ImageFont.truetype(EN, int(96 * s)), CREAM, 'ls', 10)
        shadow_text(img, (x + 4 * s, y + 52 * s), ko, ImageFont.truetype(KO, int(36 * s)), CREAM, 'ls')
    elif style == 'title':
        shadow_text(img, (W / 2, H / 2 - 10 * s), ko, ImageFont.truetype(KO, int(54 * s)), CREAM, 'ms')
        shadow_text(img, (W / 2, H / 2 + 50 * s), en, ImageFont.truetype(ENI, int(40 * s)), CREAM, 'ms')
    elif style == 'main':
        shadow_text(img, (W / 2, H / 2 - 120 * s), 'THE BEAR & JOY CO.  ·  PRESENTS', ImageFont.truetype(EN, int(24 * s)), GOLD, 'ms')
        fs = 104 if not vertical else 92
        if vertical:
            shadow_text(img, (W / 2, H / 2 - 10 * s), 'Little Steps', ImageFont.truetype(EN, int(fs * s)), CREAM, 'ms', 12)
            shadow_text(img, (W / 2, H / 2 + 100 * s), 'to Big Adventures', ImageFont.truetype(EN, int(fs * s)), CREAM, 'ms', 12)
            shadow_text(img, (W / 2, H / 2 + 190 * s), ko, ImageFont.truetype(KO, int(48 * s)), CREAM, 'ms')
        else:
            shadow_text(img, (W / 2, H / 2 + 20 * s), en, ImageFont.truetype(EN, int(fs * s)), CREAM, 'ms', 12)
            shadow_text(img, (W / 2, H / 2 + 100 * s), ko, ImageFont.truetype(KO, int(46 * s)), CREAM, 'ms')


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
    d.text((W / 2, y0 + logo.height + wm.height + int(80 * s)), '아이의 첫 영어 한 마디, 그림책으로 함께 열어요',
           font=ImageFont.truetype(KO, int(34 * s)), fill=CREAM, anchor='ms')
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
