"""Generate the animated pieces of the v6 brand film (all on this Mac, no AI imagery):
  globe  — our route of 24 stories on a navy globe (Natural Earth outlines, public domain); spins and dives.
  door   — the blue door from our Book One art swings open in 3D perspective onto Oxford and the bear.
  kb     — camera moves (pan + push) over our book illustrations.

  tools/fx-venv/bin/python projects/2026-11-cinematic-film/genclips.py h|v [name ...]
Writes raw-footage/cinematic-film/gen/<name>_<fmt>.mov (git-ignored) at 30 fps, ProRes-quality VideoToolbox.
"""
import json, math, os, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(f'{HERE}/../..')
sys.path.insert(0, HERE)
import plan  # noqa
FPS = 30
GEN = f'{ROOT}/raw-footage/cinematic-film/gen'
GEO = f'{ROOT}/raw-footage/cinematic-film/geo'
ART = f'{HERE}/bookart'
F = f'{ROOT}/remotion/public/fonts'
EN = f'{F}/nuFRD-vYSZviVYUb_rj3ij__anPXDTnCjmHKM4nYO7KN_qiTbtY.ttf'
SIZES = {'h': (1920, 1080), 'v': (1080, 1920)}
GOLD = (201, 168, 76); CREAM = (245, 240, 230); NAVY = (30, 45, 77)


def writer(path, W, H):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                             '-r', str(FPS), '-i', '-', '-c:v', 'h264_videotoolbox', '-b:v', '40M', '-pix_fmt',
                             'yuv420p', path], stdin=subprocess.PIPE)


def ease(t):          # smooth in-out
    t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)


# ---------------------------------------------------------------------------------------------- globe
def load_land(res):
    gj = json.load(open(f'{GEO}/ne_{res}_land.geojson'))
    polys = []
    for ft in gj['features']:
        g = ft['geometry']; rings = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        for poly in rings:
            ring = np.radians(np.array(poly[0], dtype=float))
            lon, lat = ring[:, 0], ring[:, 1]
            xyz = np.stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)], 1)
            c = xyz.mean(0); c /= np.linalg.norm(c) + 1e-9
            rad = np.arccos(np.clip(xyz @ c, -1, 1)).max()
            polys.append((xyz, c, rad))
    return polys


_LAND = {}


def land(res):
    if res not in _LAND:
        _LAND[res] = load_land(res)
    return _LAND[res]


def basis(lon0, lat0):
    lo, la = math.radians(lon0), math.radians(lat0)
    c = np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)])
    e = np.array([-math.sin(lo), math.cos(lo), 0.0])
    n = np.cross(c, e)
    return c, e, n


def project(xyz, c, e, n, R, cx, cy):
    z = xyz @ c; x = xyz @ e; y = xyz @ n
    behind = z < 0
    if behind.any():                      # clamp hidden vertices onto the limb
        r = np.hypot(x, y) + 1e-9
        x = np.where(behind, x / r, x); y = np.where(behind, y / r, y)
    return np.stack([cx + R * x, cy - R * y], 1), z


def unit(lon, lat):
    lo, la = math.radians(lon), math.radians(lat)
    return np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)])


def slerp(a, b, n):
    om = math.acos(min(1, max(-1, float(a @ b))))
    if om < 1e-6:
        return np.repeat(a[None], n, 0)
    t = np.linspace(0, 1, n)[:, None]
    return (np.sin((1 - t) * om) * a + np.sin(t * om) * b) / math.sin(om)


ROUTE_XYZ = [unit(lo, la) for _, lo, la in plan.ROUTE]
ARCS = [slerp(ROUTE_XYZ[i], ROUTE_XYZ[i + 1], 48) for i in range(len(ROUTE_XYZ) - 1)]
rng = np.random.default_rng(3)
STARS = rng.random((260, 3))


def globe_frame(W, H, lon0, lat0, Rf, pins=99, route=1.0, label=None, label_a=0.0):
    m = min(W, H); R = Rf * m * 0.5 * 2.0 / 2.0 * 2.0 * 0.5 * 2  # R as share of the short side
    R = Rf * m
    cx, cy = W / 2, H / 2
    img = np.zeros((H, W, 3), np.uint8); img[:] = (4, 11, 23)
    for sx, sy, sb in STARS:                                         # faint stars
        cv2.circle(img, (int(sx * W), int(sy * H)), 1, tuple(int(40 + 90 * sb) for _ in range(3)), -1, cv2.LINE_AA)
    c, e, n = basis(lon0, lat0)
    if R < 3 * max(W, H):
        glow = np.zeros((H, W), np.float32); cv2.circle(glow, (int(cx), int(cy)), int(R * 1.02), 1.0, -1, cv2.LINE_AA)
        glow = cv2.GaussianBlur(glow, (0, 0), max(4, R * 0.06))
        img = np.clip(img + glow[..., None] * np.array([40, 34, 18]), 0, 255).astype(np.uint8)
        cv2.circle(img, (int(cx), int(cy)), int(R), (14, 27, 52), -1, cv2.LINE_AA)
    else:
        img[:] = (14, 27, 52)
    res = '10m' if R > 2.5 * m else '50m'
    view_rad = math.asin(min(1.0, (math.hypot(W, H) / 2) / R)) if R > 0 else math.pi / 2
    sh = 4
    for xyz, pc, rad in land(res):
        ang = math.acos(min(1, max(-1, float(pc @ c))))
        if ang - rad > min(math.pi / 2, view_rad + 0.02):
            continue
        p, z = project(xyz, c, e, n, R, cx, cy)
        if (z < 0).all():
            continue
        pts = np.round(p * (1 << sh)).astype(np.int64)
        if np.abs(pts).max() > 2 ** 30:
            pts = np.clip(pts, -2 ** 30, 2 ** 30)
        pts = pts.astype(np.int32).reshape(-1, 1, 2)
        cv2.fillPoly(img, [pts], (38, 54, 86), cv2.LINE_AA, shift=sh)
        cv2.polylines(img, [pts], True, (62, 82, 118), 1, cv2.LINE_AA, shift=sh)
    if R < 3 * max(W, H):
        cv2.circle(img, (int(cx), int(cy)), int(R), (150, 128, 70), 1, cv2.LINE_AA)
    # route: dashed gold great circles, drawn up to `route` share
    nseg = len(ARCS); show = route * nseg
    lw = max(1, int(m / 540))
    for i, arc in enumerate(ARCS):
        if i >= show:
            break
        k = arc if i + 1 <= show else arc[:max(2, int(len(arc) * (show - i)))]
        p, z = project(k, c, e, n, R, cx, cy)
        for j in range(0, len(k) - 1, 2):
            if z[j] > 0 and z[j + 1] > 0:
                cv2.line(img, tuple(np.int32(p[j])), tuple(np.int32(p[j + 1])), GOLD, lw, cv2.LINE_AA)
    pil = Image.fromarray(img); d = ImageDraw.Draw(pil)
    pr = max(7, int(m / 75)); fnt = ImageFont.truetype(EN, int(pr * 1.15))
    seen = {}
    for idx, (name, lo, la) in enumerate(plan.ROUTE):
        if idx >= pins:
            break
        v = unit(lo, la); z = float(v @ c)
        if z < 0.05:
            continue
        p, _ = project(v[None], c, e, n, R, cx, cy); x, y = p[0]
        key = (round(x / pr), round(y / pr))
        if key in seen:
            continue
        seen[key] = 1
        d.ellipse([x - pr - 2, y - pr - 2, x + pr + 2, y + pr + 2], fill=(20, 28, 44))
        d.ellipse([x - pr, y - pr, x + pr, y + pr], fill=GOLD)
        d.text((x, y + 1), str(idx + 1), font=fnt, fill=NAVY, anchor='mm')
    if label and label_a > 0:
        v = unit(*[(lo, la) for nm, lo, la in plan.ROUTE if nm.upper() == label.upper()][0])
        p, _ = project(v[None], c, e, n, R, cx, cy); x, y = p[0]
        lay = Image.new('RGBA', pil.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        f2 = ImageFont.truetype(EN, int(m / 22)); txt = '  '.join(label)
        ld.text((x, y - pr * 2.4), txt, font=f2, fill=CREAM + (int(255 * label_a),), anchor='ms')
        pil = Image.alpha_composite(pil.convert('RGBA'), lay).convert('RGB')
    return np.asarray(pil)


def interp_keys(keys, t):
    for (t0, *a), (t1, *b) in zip(keys, keys[1:]):
        if t <= t1:
            u = ease((t - t0) / max(1e-6, t1 - t0))
            lon = a[0] + (b[0] - a[0]) * u; lat = a[1] + (b[1] - a[1]) * u
            r = math.exp(math.log(a[2]) + (math.log(b[2]) - math.log(a[2])) * (u ** 1.6 if b[2] > a[2] * 3 else u))
            return lon, lat, r
    return keys[-1][1], keys[-1][2], keys[-1][3]


def globe(name, fmt, dur, spec):
    W, H = SIZES[fmt]; n = int(round(dur * FPS)) + 2
    pw = writer(f'{GEN}/{name}_{fmt}.mov', W, H)
    for k in range(n):
        t = k / max(1, n - 1)
        lon, lat, r = interp_keys(spec['keys'], t)
        if spec.get('spin'):
            pins = int(1 + t * 23.99); route = t
        else:
            pins, route = 99, 1.0
        la = ease((t - 0.82) / 0.12) if spec.get('label') else 0
        fr = globe_frame(W, H, lon, lat, r, pins, route, spec.get('label'), la)
        pw.stdin.write(fr.tobytes())
    pw.stdin.close(); pw.wait()


# ---------------------------------------------------------------------------------------------- book-art camera
def fit_canvas(img, W, H):
    """Cover-fit when aspect is close; otherwise place on an extended paper canvas (soft, blurred edges)."""
    return img


def kb(name, fmt, dur, spec):
    W, H = SIZES[fmt]; src = Image.open(f"{ART}/{spec['src']}").convert('RGB'); sw, sh = src.size
    asp = W / H
    bw, bh = (sw, sw / asp) if sw / sh < asp else (sh * asp, sh)          # cover box at zoom 1
    n = int(round(dur * FPS)) + 2; pw = writer(f'{GEN}/{name}_{fmt}.mov', W, H)
    for k in range(n):
        t = ease(k / max(1, n - 1))
        cx = spec['a'][0] + (spec['b'][0] - spec['a'][0]) * t
        cy = spec['a'][1] + (spec['b'][1] - spec['a'][1]) * t
        z = math.exp(math.log(spec['a'][2]) + (math.log(spec['b'][2]) - math.log(spec['a'][2])) * t)
        w, h = bw / z, bh / z
        x0 = min(max(cx * sw - w / 2, 0), sw - w); y0 = min(max(cy * sh - h / 2, 0), sh - h)
        fr = src.transform((W, H), Image.Transform.EXTENT, (x0, y0, x0 + w, y0 + h), Image.Resampling.BICUBIC)
        pw.stdin.write(np.asarray(fr).tobytes())
    pw.stdin.close(); pw.wait()


# ---------------------------------------------------------------------------------------------- door
HX, TOP, BOT = 644.0, 205.0, 1152.0          # hinge x, door top/bottom at the wall (source px, 880x1316 art)
DW = 380.0                                    # door width
CX, CY, FOC = 440.0, 737.0, 1563.0            # vanishing point and focal length fitted to the open-door art
THETA_OPEN = math.radians(100.6)


def door_quad(th):
    X = HX - DW * math.cos(th); Zd = -DW * math.sin(th); s = FOC / (FOC + Zd)
    fx = CX + (X - CX) * s
    return np.float32([[HX, TOP], [fx, CY + (TOP - CY) * s], [fx, CY + (BOT - CY) * s], [HX, BOT]])


def door_layers():
    art = cv2.cvtColor(cv2.imread(f'{ART}/blue-door.png'), cv2.COLOR_BGR2RGB)
    clean = art.copy()
    m = np.zeros(art.shape[:2], np.uint8)                                  # page text and page number
    cv2.rectangle(m, (0, 0), (70, 42), 255, -1); cv2.rectangle(m, (0, 330), (185, 455), 255, -1)
    cv2.rectangle(m, (826, 1252), (858, 1290), 255, -1)
    clean = cv2.inpaint(clean, m, 7, cv2.INPAINT_TELEA)
    open_quad = np.float32([[642, 210], [797, 38], [803, 1282], [646, 1150]])
    tw, th = 380, 947
    M = cv2.getPerspectiveTransform(open_quad, np.float32([[0, 0], [tw, 0], [tw, th], [0, th]]))
    tex = cv2.warpPerspective(clean, M, (tw, th), flags=cv2.INTER_CUBIC)
    # a door texture whose hinge side is on the left (x=0) and free edge (knob) on the right
    dm = np.zeros(art.shape[:2], np.uint8)                                 # remove the painted open door
    cv2.fillConvexPoly(dm, np.int32([[636, 24], [880, 24], [880, 1316], [636, 1316]]), 255)
    # right of the hinge: a mirrored copy of the plain left wall and floor (boots and hook removed first)
    left = clean[:, :244].copy()
    lm = np.zeros(left.shape[:2], np.uint8)
    cv2.rectangle(lm, (90, 1060), (215, 1185), 255, -1); cv2.rectangle(lm, (105, 360), (175, 430), 255, -1)
    left = cv2.inpaint(left, lm, 9, cv2.INPAINT_TELEA)
    strip = left[:, ::-1]
    base = clean.copy(); base[:, 636:880] = strip
    seam = np.linspace(0, 1, 24)[None, :, None]
    base[:, 636:660] = (clean[:, 636:660] * (1 - seam) + strip[:, :24] * seam).astype(np.uint8)
    return clean, base, tex


def door(name, fmt, dur, spec):
    W, H = SIZES[fmt]; clean, base, tex = door_layers(); sh, sw = clean.shape[:2]
    tw, th = tex.shape[1], tex.shape[0]
    n = int(round(dur * FPS)) + 2; pw = writer(f'{GEN}/{name}_{fmt}.mov', W, H)
    # placement: scale to frame height; pad wide frames with soft, blurred paper
    s = H / sh; nw = int(sw * s)
    if fmt == 'v':
        s = max(W / sw, H / sh); nw = int(sw * s)
    for k in range(n):
        t = k / max(1, n - 1)
        u = ease((t - 0.18) / 0.55)                                          # closed 18%, swing 55%, hold
        u = u + 0.035 * math.sin(math.pi * min(1, max(0, (t - 0.73) / 0.12)))   # tiny settle
        theta = THETA_OPEN * min(1.0, u)
        if u >= 0.999 and t > 0.8:
            src = clean
        else:
            q = door_quad(theta)
            Mi = cv2.getPerspectiveTransform(np.float32([[0, 0], [tw, 0], [tw, th], [0, th]]), q)
            layer = cv2.warpPerspective(tex, Mi, (sw, sh), flags=cv2.INTER_CUBIC)
            mask = cv2.warpPerspective(np.full((th, tw), 255, np.uint8), Mi, (sw, sh))
            shade = 0.82 + 0.18 * abs(math.cos(theta))                      # darker when edge-on
            layer = np.clip(layer * shade, 0, 255).astype(np.uint8)
            a = (cv2.GaussianBlur(mask, (3, 3), 0) / 255.0)[..., None]
            src = (base * (1 - a) + layer * a).astype(np.uint8)
            if theta < 0.02:                                                  # closed: also cover the doorway shadow line
                src = src
        im = Image.fromarray(src).resize((nw, int(sh * s)), Image.Resampling.LANCZOS)
        push = 1.0 + 0.10 * ease(t)                                          # gentle push towards the bear
        if fmt == 'h':
            yy, xx = np.mgrid[0:H, 0:W]
            r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
            paper = np.array([246, 234, 214], float) * (1 - 0.06 * np.clip(r, 0, 1.4))[..., None]
            canvas = Image.fromarray(paper.astype(np.uint8))       # plain warm paper, like the page's own wall
            x0 = (W - nw) // 2
            mask = Image.new('L', im.size, 255); md = ImageDraw.Draw(mask)
            for i in range(60):
                md.rectangle([i, 0, im.width - 1 - i, im.height - 1], outline=int(255 * i / 60))
            canvas.paste(im, (x0, 0), mask)
            fr = canvas
        else:
            x0 = int(min(max(0, nw * (452 / 880) - W / 2), nw - W))
            fr = im.crop((x0, 0, x0 + W, H))
        Wp, Hp = int(W / push), int(H / push)
        fx, fy = (W * 0.50, H * 0.62)
        l = int(min(max(fx - Wp / 2, 0), W - Wp)); tp = int(min(max(fy - Hp / 2, 0), H - Hp))
        fr = fr.crop((l, tp, l + Wp, tp + Hp)).resize((W, H), Image.Resampling.BICUBIC)
        pw.stdin.write(np.asarray(fr).tobytes())
    pw.stdin.close(); pw.wait()


if __name__ == '__main__':
    fmt = sys.argv[1]; names = sys.argv[2:] or list(plan.GEN)
    os.makedirs(GEN, exist_ok=True)
    need = plan.gen_lengths()
    for nm in names:
        spec = plan.GEN[nm]; dur = need.get(nm, 3.0) + 0.2
        {'globe': globe, 'kb': kb, 'door': door}[spec['kind']](nm, fmt, dur, spec)
        print('ok', nm, fmt, round(dur, 2), flush=True)
