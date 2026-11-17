#!/usr/bin/env python3
"""Fotogramas de comparación antes/después del color del reel de Neko (sin renderizar el reel completo).
Uso: python3 neko_stills.py --src carpeta_videos --photo foto.jpg --sticks IMG_4716.mov --out salida.png [--w 300]
"""
import argparse, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from neko_grade import GRADES
from PIL import Image, ImageDraw

ap = argparse.ArgumentParser()
ap.add_argument('--src', required=True); ap.add_argument('--photo', required=True); ap.add_argument('--sticks', required=True)
ap.add_argument('--out', required=True); ap.add_argument('--w', type=int, default=300)
a = ap.parse_args()
W, H = a.w, int(a.w * 16 / 9)
up = f'scale=-2:{H}:flags=lanczos,crop={W}:{H}'
v = lambda n: os.path.join(a.src, f'IMG_{n}_720p.mp4')
# (rótulo, archivo, instante, clave de corrección). La foto usa su recorte 9:16.
scenes = [('Máquina · gancho', v('8186'), 1.2, '8186'), ('Máquina · barrido', v('8186'), 5.9, '8186'),
          ('Preparación 8181', v('8181'), 9.8, '8181'), ('Preparación 8182', v('8182'), 3.0, '8182'),
          ('Preparación 8184', v('8184'), 3.6, '8184'), ('Ramen terminado', a.sticks, 2.2, '4716'),
          ('Foto cenital', a.photo, 0, 'photo')]
tmp = tempfile.mkdtemp()
def frame(src, t, vf, name):
    out = os.path.join(tmp, name + '.png')
    if src == a.photo:
        cmd = ['ffmpeg', '-v', 'error', '-y', '-i', src, '-frames:v', '1', '-vf', f'crop=1125:2000:187:0,{up}' + (',' + vf if vf else ''), out]
    else:
        cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', src, '-frames:v', '1', '-vf', up + (',' + vf if vf else ''), out]
    subprocess.check_call(cmd); return Image.open(out).convert('RGB')
pairs = []
for i, (lab, src, t, key) in enumerate(scenes):
    pairs.append((lab, frame(src, t, '', f'b{i}'), frame(src, t, GRADES[key], f'a{i}')))
cols = 4; rows = (len(pairs) + cols - 1) // cols; pw = W * 2 + 6; ph = H + 26
sheet = Image.new('RGB', (cols * (pw + 14) + 14, rows * (ph + 14) + 14), (22, 19, 20))
d = ImageDraw.Draw(sheet)
for i, (lab, b, af) in enumerate(pairs):
    x = 14 + (i % cols) * (pw + 14); y = 14 + (i // cols) * (ph + 14)
    d.text((x, y + 4), f'{lab}   antes | después', fill=(231, 223, 210))
    sheet.paste(b, (x, y + 24)); sheet.paste(af, (x + W + 6, y + 24))
sheet.save(a.out); print(a.out, sheet.size)
