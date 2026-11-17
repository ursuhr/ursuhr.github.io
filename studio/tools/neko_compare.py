#!/usr/bin/env python3
"""Comparación del color: original | corrección anterior | nueva propuesta, para máquina, preparación y ramen terminado.
Uso: neko_compare.py --src carpeta --sticks IMG_4716.mov --refs 1.webp 2.webp --out salida.png [--w 300]"""
import argparse, os, subprocess, sys, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from neko_grade import GRADES
from neko_look import grade
from neko_params import PARAMS
from PIL import Image, ImageDraw
ap = argparse.ArgumentParser()
ap.add_argument('--src', required=True); ap.add_argument('--sticks', required=True); ap.add_argument('--refs', nargs='*', default=[])
ap.add_argument('--out', required=True); ap.add_argument('--w', type=int, default=300); ap.add_argument('--all', action='store_true')
a = ap.parse_args()
W, H = a.w, int(a.w * 16 / 9)
up = f'scale=-2:{H}:flags=lanczos,crop={W}:{H}'
v = lambda n: os.path.join(a.src, f'IMG_{n}_720p.mp4')
scenes = [('Máquina de fideos', v('8186'), 1.2, '8186'), ('Preparación', v('8181'), 9.8, '8181'), ('Ramen terminado', a.sticks, 2.2, '4716')]
if a.all:
    scenes = [('Máquina · gancho', v('8186'), 1.2, '8186'), ('Máquina · barrido', v('8186'), 5.9, '8186b'), ('Preparación 8181', v('8181'), 9.8, '8181'),
              ('Preparación 8182', v('8182'), 3.0, '8182'), ('Preparación 8184', v('8184'), 3.6, '8184'), ('Ramen terminado', a.sticks, 2.2, '4716')]
tmp = tempfile.mkdtemp()
def fr(src, t, vf, n):
    out = os.path.join(tmp, n + '.png')
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', src, '-frames:v', '1', '-vf', up + (',' + vf if vf else ''), out])
    return Image.open(out).convert('RGB')
cols = []
for i, (lab, src, t, key) in enumerate(scenes):
    o = fr(src, t, '', f'o{i}')
    old = fr(src, t, GRADES[key.rstrip('b')], f'p{i}')
    new = Image.fromarray((grade(np.asarray(o, np.float32) / 255, PARAMS[key]) * 255 + 0.5).astype(np.uint8))
    cols.append((lab, o, old, new))
pad = 8
if a.all:
    sheet = Image.new('RGB', (len(cols) * (W + pad) + pad, 3 * (H + 22) + 3 * pad), (16, 14, 15)); d = ImageDraw.Draw(sheet)
    for ci, (lab, o, old, new) in enumerate(cols):
        for ri, (im, nm) in enumerate([(o, 'original'), (old, 'anterior'), (new, 'nueva')]):
            x = pad + ci * (W + pad); y = pad + ri * (H + 22 + pad)
            d.text((x, y), f'{lab} · {nm}', fill=(231, 223, 210)); sheet.paste(im, (x, y + 16))
else:
    rw = 0
    refs = []
    for r in a.refs:
        im = Image.open(r).convert('RGB'); im.thumbnail((W, H)); refs.append(im)
    nrow = 3 + (1 if refs else 0)
    sheet = Image.new('RGB', (len(cols) * (W + pad) + pad, nrow * (H + 22 + pad) + pad), (16, 14, 15)); d = ImageDraw.Draw(sheet)
    names = ['original', 'corrección anterior', 'nueva propuesta']
    for ci, c in enumerate(cols):
        for ri in range(3):
            x = pad + ci * (W + pad); y = pad + ri * (H + 22 + pad)
            d.text((x, y), f'{c[0]} · {names[ri]}', fill=(231, 223, 210)); sheet.paste(c[ri + 1], (x, y + 16))
    if refs:
        y = pad + 3 * (H + 22 + pad); d.text((pad, y), 'referencias: fotografías reales del local', fill=(231, 223, 210))
        for i, im in enumerate(refs): sheet.paste(im, (pad + i * (W + pad), y + 16))
sheet.save(a.out); print(a.out, sheet.size)
