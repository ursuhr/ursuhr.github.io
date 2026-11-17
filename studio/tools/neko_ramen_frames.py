#!/usr/bin/env python3
"""Fotogramas alternativos del ramen terminado con la corrección actual (fila 1) y la versión suave (fila 2).
Uso: python3 neko_ramen_frames.py --sticks IMG_4716.mov --t 1.8 3.9 4.5 --out hoja.png"""
import argparse, glob, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import neko_lr
from PIL import Image, ImageDraw, ImageFont
ap = argparse.ArgumentParser(); ap.add_argument('--sticks', required=True); ap.add_argument('--t', nargs='+', type=float, required=True)
ap.add_argument('--out', required=True); ap.add_argument('--w', type=int, default=340); a = ap.parse_args()
W, H = a.w, int(a.w * 16 / 9); tmp = tempfile.mkdtemp(); luts = neko_lr.luts(tmp)
f = (glob.glob('/usr/share/fonts/**/DejaVuSans.ttf', recursive=True) or [None])[0]; font = ImageFont.truetype(f, 11) if f else None
pad = 10; sheet = Image.new('RGB', (len(a.t) * (W + pad) + pad, 2 * (H + 20 + pad) + pad), (245, 241, 232)); dr = ImageDraw.Draw(sheet); dr.font = font
for r, (key, nom) in enumerate([('ramen', 'corrección actual'), ('ramen_suave', 'alternativa suave')]):
    for i, t in enumerate(a.t):
        out = os.path.join(tmp, f'{key}{i}.png')
        subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-ss', str(t), '-i', a.sticks, '-frames:v', '1', '-vf',
                               neko_lr.HLG_A_SDR + f',scale=-2:{H}:flags=lanczos,crop={W}:{H},lut3d=file={luts[key]}:interp=tetrahedral', out])
        x = pad + i * (W + pad); y = pad + r * (H + 20 + pad)
        dr.text((x, y), f'fotograma {i+1} · {t:.1f} s · {nom}', fill=(11, 11, 11)); sheet.paste(Image.open(out).convert('RGB'), (x, y + 16))
sheet.save(a.out); print(a.out, sheet.size)
