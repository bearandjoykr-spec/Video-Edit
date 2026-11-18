"""Render the cinematic film from plan.py. Everything runs on this Mac (VideoToolbox for intermediates).

  tools/fx-venv/bin/python projects/2026-11-cinematic-film/render.py shots   h|v   # graded shot clips
  tools/fx-venv/bin/python projects/2026-11-cinematic-film/render.py layers  h|v   # title / end-card PNGs
  tools/fx-venv/bin/python projects/2026-11-cinematic-film/render.py compose h|v   # picture + titles + flashes
Outputs go to renders/cinematic-film/<h|v>/ (git-ignored).

h = 16:9 website film: 1920x1080 frame, picture 1920x804 (2.39:1 letterbox).
v = 9:16 Instagram cut: 1080x1920 full frame.
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from plan import SHOTS, LINES, END  # noqa
from looks import LOOKS  # noqa
import storyboard as sb  # noqa

ROOT = sb.ROOT
FPS = 30
HITS_FLASH = [21.5, 53.5, 94.5]            # white flash frames on the biggest hits
FORMATS = {'h': dict(W=1920, H=1080, PW=1920, PH=804), 'v': dict(W=1080, H=1920, PW=1080, PH=1920)}


def out_dir(fmt):
    d = f'{ROOT}/renders/cinematic-film/{fmt}'; os.makedirs(d, exist_ok=True); return d


def probe(p):
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_streams',
                                               '-of', 'json', p]))['streams'][0]
    w, h = info['width'], info['height']
    rot = [d.get('rotation', 0) for d in info.get('side_data_list', [])]
    if rot and abs(int(rot[0])) % 180 == 90:
        w, h = h, w
    num, den = map(int, info['r_frame_rate'].split('/'))
    return w, h, num / den


def frame_index(t):
    return int(round(t * FPS))


def render_shot(fmt, i):
    f = FORMATS[fmt]; PW, PH = f['PW'], f['PH']
    start, clip, tin, look, fx, fy, z0, z1, speed, note = SHOTS[i]
    end = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else END
    n = frame_index(end) - frame_index(start)
    out = f'{out_dir(fmt)}/shot{i:02d}.mov'
    enc = ['-c:v', 'h264_videotoolbox', '-b:v', '24M', '-pix_fmt', 'yuv420p', '-an']
    if clip in ('black', 'endcard'):
        col = '0x1E2D4D' if clip == 'endcard' else 'black'
        cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c={col}:s={PW}x{PH}:r={FPS}',
               '-frames:v', str(n), *enc, out]
        subprocess.run(cmd, check=True); return out
    p = sb.src(clip); w, h, sfps = probe(p)
    if fmt == 'v':
        fy = 0.5 if h > w else fy
    tgt = PW / PH
    cw, ch = (w, w / tgt) if w / h < tgt else (h * tgt, h)
    cw, ch = int(cw) // 2 * 2, int(ch) // 2 * 2
    x = int(min(max(fx * w - cw / 2, 0), w - cw)); y = int(min(max(fy * h - ch / 2, 0), h - ch))
    dur = n / FPS
    src_dur = dur * speed + 0.5
    chain = [f'crop={cw}:{ch}:{x}:{y}', f'scale={PW}:{PH}:flags=lanczos', f'setpts=(PTS-STARTPTS)/{speed}']
    if speed < 0.95 and sfps < 45:
        chain.append(f'minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1')
    else:
        chain.append(f'fps={FPS}')
    zt = f'({z0}+({z1}-{z0})*t/{dur:.3f})'
    chain += [f"scale=w='ceil({PW}*{zt}/2)*2':h='ceil({PH}*{zt}/2)*2':eval=frame:flags=bicubic",
              f'crop={PW}:{PH}:(in_w-{PW})/2:(in_h-{PH})/2', LOOKS[look], 'format=yuv420p']
    cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', f'{tin:.3f}', '-t', f'{src_dur:.3f}', '-i', p,
           '-vf', ','.join(chain), '-frames:v', str(n), '-r', str(FPS), *enc, out]
    subprocess.run(cmd, check=True)
    got = int(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0',
                                       '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', out]).decode().replace(',', ' ').split()[0])
    if got < n:   # source ran short: hold the last frame
        tmp = out + '.pad.mov'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out, '-vf', f'tpad=stop_mode=clone:stop={n - got}',
                        '-frames:v', str(n), *enc, tmp], check=True); os.replace(tmp, out)
    return out


def shots(fmt):
    idx = list(range(len(SHOTS)))
    with ThreadPoolExecutor(4) as ex:
        for o in ex.map(lambda i: render_shot(fmt, i), idx):
            print('ok', os.path.basename(o), flush=True)
    with open(f'{out_dir(fmt)}/concat.txt', 'w') as fh:
        for i in idx:
            fh.write(f"file 'shot{i:02d}.mov'\n")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{out_dir(fmt)}/concat.txt',
                    '-c', 'copy', f'{out_dir(fmt)}/picture.mov'], check=True)
    print('picture.mov')


def layers(fmt):
    """One transparent full-frame PNG per subtitle line, plus three end-card layers. Writes layers.json."""
    f = FORMATS[fmt]; W, H, PH = f['W'], f['H'], f['PH']; top = (H - PH) // 2; v = fmt == 'v'
    d = f'{out_dir(fmt)}/layers'; os.makedirs(d, exist_ok=True); meta = []
    for k, ln in enumerate(LINES):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        sb.draw_line(img, ln, W, H, top, PH, v)
        path = f'{d}/line{k:02d}.png'; img.save(path)
        rise = 0 if ln[4] in ('main', 'title') else 16
        meta.append(dict(png=path, s=ln[0], e=ln[1], fin=0.5 if ln[4] == 'main' else 0.35, fout=0.4, rise=rise))
    # end card: logo + wordmark (108.6 s), tagline (110.5 s), URL (112.2 s); all out by 117.4 s
    s = min(W, H) / 1080
    logo = Image.open(f'{ROOT}/brand/assets/bear-butterfly.png').convert('RGBA')
    wm = Image.open(f'{ROOT}/brand/assets/wordmark-cream.png').convert('RGBA')
    logo = logo.resize((int(300 * s), int(300 * s * logo.height / logo.width)), Image.LANCZOS)
    wm = wm.resize((int(620 * s), int(620 * s * wm.height / wm.width)), Image.LANCZOS)
    y0 = int(H / 2 - (logo.height + wm.height + 120 * s) / 2)
    a = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a.alpha_composite(logo, ((W - logo.width) // 2, y0)); a.alpha_composite(wm, ((W - wm.width) // 2, y0 + logo.height + int(20 * s)))
    b = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(b).text((W / 2, y0 + logo.height + wm.height + int(80 * s)), 'Born in Oxford · Built in Seoul',
                           font=ImageFont.truetype(sb.ENI, int(38 * s)), fill=sb.CREAM, anchor='ms')
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(c).text((W / 2, y0 + logo.height + wm.height + int(130 * s)), 'bearandjoy.com',
                           font=ImageFont.truetype(sb.EN, int(28 * s)), fill=sb.GOLD, anchor='ms')
    for name, img, st in (('end_logo', a, 108.6), ('end_tag', b, 110.5), ('end_url', c, 112.2)):
        path = f'{d}/{name}.png'; img.save(path)
        meta.append(dict(png=path, s=st, e=117.4, fin=0.9, fout=0.9, rise=8))
    json.dump(meta, open(f'{out_dir(fmt)}/layers.json', 'w'), indent=1)
    print(len(meta), 'layers')


def compose(fmt):
    f = FORMATS[fmt]; W, H, PH = f['W'], f['H'], f['PH']; top = (H - PH) // 2
    od = out_dir(fmt); meta = json.load(open(f'{od}/layers.json'))
    args = ['ffmpeg', '-v', 'error', '-y', '-i', f'{od}/picture.mov']
    for m in meta:
        args += ['-loop', '1', '-framerate', str(FPS), '-t', f'{END}', '-i', m['png']]
    g = [f'[0:v]pad={W}:{H}:0:{top}:black,setsar=1[b0]']
    cur = 'b0'
    for k, m in enumerate(meta, start=1):
        s, e, fi, fo = m['s'], m['e'], m['fin'], m['fout']
        g.append(f'[{k}:v]format=rgba,fade=t=in:st={s}:d={fi}:alpha=1,fade=t=out:st={e - fo}:d={fo}:alpha=1[l{k}]')
        y = f"'{m['rise']}*max(0,1-(t-{s})/0.5)'" if m['rise'] else '0'
        g.append(f"[{cur}][l{k}]overlay=x=0:y={y}:eval=frame:enable='between(t,{s},{e})'[b{k}]")
        cur = f'b{k}'
    # white flashes on the big hits (2 frames full, then 0.3 s decay), and a fade-out to black at the end
    for j, t in enumerate(HITS_FLASH):
        g.append(f"color=c=white:s={W}x{PH}:r={FPS}:d={END},format=rgba,"
                 f"fade=t=out:st={t + 0.066}:d=0.28:alpha=1[w{j}]")
        g.append(f"[{cur}][w{j}]overlay=0:{top}:enable='between(t,{t},{t + 0.35})'[f{j}]")
        cur = f'f{j}'
    g.append(f'[{cur}]fade=t=out:st={END - 0.6}:d=0.6,format=yuv420p[out]')
    args += ['-filter_complex', ';'.join(g), '-map', '[out]', '-frames:v', str(frame_index(END)), '-r', str(FPS),
             '-c:v', 'h264_videotoolbox', '-b:v', '30M', '-pix_fmt', 'yuv420p', f'{od}/composed.mov']
    subprocess.run(args, check=True)
    print('composed.mov')



def reshoot(fmt, idx):
    """Re-render only the listed shots, then rebuild picture.mov."""
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda i: render_shot(fmt, i), idx))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{out_dir(fmt)}/concat.txt',
                    '-c', 'copy', f'{out_dir(fmt)}/picture.mov'], check=True)
    print('picture.mov (reshot', idx, ')')


if __name__ == '__main__':
    step, fmt = sys.argv[1], sys.argv[2]
    if step == 'reshoot':
        reshoot(fmt, [int(a) for a in sys.argv[3:]])
    else:
        {'shots': shots, 'layers': layers, 'compose': compose}[step](fmt)

