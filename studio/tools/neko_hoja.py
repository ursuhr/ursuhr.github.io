#!/usr/bin/env python3
"""Hoja comparativa: original y corrección (LUT de neko_lr.py) de los cuatro videos de la máquina y del ramen terminado, con los valores efectivos.
Uso: python3 neko_hoja.py --src carpeta_videos --sticks IMG_4716.mov --out hoja.png [--w 300]"""
import argparse, os, subprocess, sys, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import neko_lr
from PIL import Image, ImageDraw, ImageFont
import glob
_f = (glob.glob('/usr/share/fonts/**/DejaVuSans.ttf', recursive=True) or glob.glob('/usr/share/fonts/**/*.ttf', recursive=True))
FONT = ImageFont.truetype(_f[0], 10) if _f else None
ap = argparse.ArgumentParser()
ap.add_argument('--src', required=True); ap.add_argument('--sticks', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--w', type=int, default=300); ap.add_argument('--metrics', action='store_true')
a = ap.parse_args()
W, H = a.w, int(a.w * 16 / 9)
up = f'scale=-2:{H}:flags=lanczos,crop={W}:{H}'
v = lambda n: os.path.join(a.src, f'IMG_{n}_720p.mp4')
cols = [('IMG_8186 · máquina', v('8186'), 1.2, '8186'), ('IMG_8181 · preparación', v('8181'), 9.8, '8181'), ('IMG_8182 · preparación', v('8182'), 3.0, '8182'),
        ('IMG_8184 · preparación', v('8184'), 3.6, '8184'), ('Ramen terminado', a.sticks, 2.2, 'ramen')]
tmp = tempfile.mkdtemp(); luts = neko_lr.luts(tmp); d = neko_lr.cargar()
def fr(src, t, vf, n):
    out = os.path.join(tmp, n + '.png')
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', src, '-frames:v', '1', '-vf', vf, out]); return Image.open(out).convert('RGB')
pad, tl = 10, 12 * 12 + 30
sheet = Image.new('RGB', (len(cols) * (W + pad) + pad, 2 * (H + 22) + tl + 3 * pad + 40), (245, 241, 232)); dr = ImageDraw.Draw(sheet); dr.font = FONT
res = {}
for i, (lab, src, t, key) in enumerate(cols):
    o = fr(src, t, up, f'o{i}'); n = fr(src, t, up + f',lut3d=file={luts[key]}:interp=tetrahedral', f'n{i}'); res[key] = (o, n)
    x = pad + i * (W + pad)
    dr.text((x, pad), f'{lab} · original', fill=(11, 11, 11)); sheet.paste(o, (x, pad + 14))
    y2 = pad + H + 22 + pad
    dr.text((x, y2), f'{lab} · corrección', fill=(11, 11, 11)); sheet.paste(n, (x, y2 + 14))
    y3 = y2 + H + 22 + pad
    for j, line in enumerate(neko_lr.texto_valores(key, d)): dr.text((x, y3 + j * 12), line, fill=(11, 11, 11))
dr.text((pad, sheet.height - 30), 'Sin viñeta · sin máscaras ni luz localizada · sin glow · sin grano · sin presets · sin filtro cálido adicional', fill=(11, 11, 11))
sheet.save(a.out); print(a.out, sheet.size)
if a.metrics:
    L = lambda im: np.asarray(im, np.float32) / 255
    for key, (o, n) in res.items():
        xo, xn = L(o), L(n); yo, yn = xo @ neko_lr.LUMA, xn @ neko_lr.LUMA
        h, w = yo.shape; c = (slice(h // 3, 2 * h // 3), slice(w // 3, 2 * w // 3)); e = np.ones_like(yo, bool); e[c] = False
        print(f'{key:6s} luma media {yo.mean():.3f}→{yn.mean():.3f} | p1 {np.percentile(yo,1):.3f}→{np.percentile(yn,1):.3f} | p99 {np.percentile(yo,99):.3f}→{np.percentile(yn,99):.3f} | '
              f'borde/centro {yo[e].mean()/yo[c].mean():.3f}→{yn[e].mean()/yn[c].mean():.3f}')
